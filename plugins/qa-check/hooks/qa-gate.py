#!/usr/bin/env python3
"""qa-check push gate (PreToolUse hook on Bash). Deterministic: no LLM calls.

Blocks `git push` until /qa-check has run against the current HEAD (or within
the last 30 minutes) in the checkout the push runs in. Worktree-aware: the
checkout is the hook's `cwd`, a leading `cd <dir>`, or `git -C <dir>`.

Opt-in per repo: a `.qa-check-required` file at the repo root.
Escape hatch:    QA_CHECK_SKIP=1 git push
Marker file:     <checkout root>/.qa-check/ok (written by /qa-check: sha + epoch)
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time

REQUIRED_FILE = ".qa-check-required"
MARKER = os.path.join(".qa-check", "ok")
FRESH_SECONDS = 1800
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
OPERATORS = "();<>|&"


def git(cwd, *args):
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def tokenize(text):
    lex = shlex.shlex(text, posix=True, punctuation_chars=OPERATORS)
    lex.whitespace_split = True
    return list(lex)


def segments(command):
    """Split a shell command into simple commands (lists of words)."""
    try:
        tokens = tokenize(command.replace("\n", ";"))
    except ValueError:
        # Unbalanced quotes, e.g. a heredoc body. Parse line by line instead.
        tokens = []
        for line in command.splitlines():
            try:
                tokens += tokenize(line) + [";"]
            except ValueError:
                tokens.append(";")
    current = []
    for tok in tokens:
        if tok and all(c in OPERATORS for c in tok):
            if current:
                yield current
            current = []
        else:
            current.append(tok)
    if current:
        yield current


def push_directories(command, cwd):
    """Yield the directory of each `git push` in `command`, following `cd` and `git -C`."""
    for words in segments(command):
        while words and ASSIGNMENT.match(words[0]):
            words.pop(0)
        if not words:
            continue
        prog, args = words[0], words[1:]
        if prog == "cd":
            cwd = os.path.normpath(os.path.join(cwd, os.path.expanduser(args[0] if args else "~")))
        elif prog == "git":
            target = cwd
            while len(args) >= 2 and args[0] == "-C":
                target = os.path.normpath(os.path.join(target, os.path.expanduser(args[1])))
                args = args[2:]
            if args and args[0] == "push":
                yield target


def check(directory):
    """Return a block message, or None when the push may proceed."""
    root = git(directory, "rev-parse", "--show-toplevel")
    if not root or not os.path.isfile(os.path.join(root, REQUIRED_FILE)):
        return None

    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD") or "?"
    where = f"{root} ({branch})"
    try:
        with open(os.path.join(root, MARKER), encoding="utf-8") as fh:
            marker_sha = fh.readline().strip()
            marker_time = fh.readline().strip()
    except OSError:
        return (
            f"qa-check gate: this repo requires a QA check before push (.qa-check-required), and none "
            f"has run in {where}. Run /qa-check there, then push. "
            f"Override for this push only: QA_CHECK_SKIP=1 git push"
        )

    head_sha = git(root, "rev-parse", "HEAD")
    age = int(time.time()) - (int(marker_time) if marker_time.isdigit() else 0)
    # Fresh if the check ran against this exact HEAD, or ran recently
    # (covers the normal flow: qa-check -> fix -> commit -> push).
    if (marker_sha and marker_sha == head_sha) or age < FRESH_SECONDS:
        return None
    return (
        f"qa-check gate: last QA check in {where} is stale (ran against {marker_sha[:8] or '?'}, "
        f"{age // 60} minutes ago; HEAD is {head_sha[:8] or '?'}). Run /qa-check again, then push. "
        f"Override: QA_CHECK_SKIP=1 git push"
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    if "git" not in command or "QA_CHECK_SKIP=1" in command:
        return 0
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    for directory in push_directories(command, cwd):
        message = check(directory)
        if message:
            print(message, file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
