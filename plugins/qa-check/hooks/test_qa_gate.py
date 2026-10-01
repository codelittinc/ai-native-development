"""Tests for qa-gate.py. Run: python3 -m unittest discover plugins/qa-check/hooks"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "qa-gate.py")
SKILL = os.path.join(HERE, "..", "skills", "qa-check", "SKILL.md")
PUSH = "git " + "push"


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def commit(repo, name, content):
    with open(os.path.join(repo, name), "w", encoding="utf-8") as fh:
        fh.write(content)
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-q", "-m", "change")


def stamp(repo, age_seconds=0):
    """Write the marker exactly as the SKILL.md command does, optionally backdated."""
    with open(SKILL, encoding="utf-8") as fh:
        text = fh.read()
    start = text.index("```bash\ntop=") + len("```bash\n")
    subprocess.run(["bash", "-c", text[start:text.index("```", start)]], cwd=repo, check=True)
    if age_seconds:
        path = os.path.join(repo, ".qa-check", "ok")
        with open(path, encoding="utf-8") as fh:
            sha, epoch = fh.read().split()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"{sha}\n{int(epoch) - age_seconds}\n")


class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.realpath(os.path.join(self.tmp.name, "repo"))
        os.makedirs(self.repo)
        sh(self.repo, "git", "init", "-q", "-b", "main")
        sh(self.repo, "git", "config", "user.email", "t@example.com")
        sh(self.repo, "git", "config", "user.name", "t")
        commit(self.repo, ".qa-check-required", "")

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, command, cwd=None, raw=None):
        payload = raw if raw is not None else json.dumps(
            {"cwd": cwd or self.repo, "tool_input": {"command": command}}
        )
        r = subprocess.run([sys.executable, HOOK], input=payload, capture_output=True, text=True,
                           env={**os.environ, "CLAUDE_PROJECT_DIR": self.repo})
        return r.returncode, r.stderr

    def assertBlocked(self, command, **kw):
        code, err = self.run_hook(command, **kw)
        self.assertEqual(code, 2, f"expected block for {command!r}")
        return err

    def assertAllowed(self, command, **kw):
        code, err = self.run_hook(command, **kw)
        self.assertEqual(code, 0, f"expected allow for {command!r}: {err}")

    def add_worktree(self):
        path = os.path.join(self.tmp.name, "wt")
        sh(self.repo, "git", "worktree", "add", "-q", "-b", "feature", path)
        return os.path.realpath(path)

    def test_non_push_commands_pass(self):
        for cmd in ["ls", "git status", "gh pr ready", f"echo '{PUSH}'"]:
            self.assertAllowed(cmd)

    def test_repo_not_opted_in_passes(self):
        sh(self.repo, "git", "rm", "-q", ".qa-check-required")
        sh(self.repo, "git", "commit", "-q", "-m", "opt out")
        self.assertAllowed(PUSH)

    def test_push_needs_a_check(self):
        self.assertIn("none has run", self.assertBlocked(f"{PUSH} -u origin HEAD"))

    def test_check_on_head_passes_even_when_old(self):
        stamp(self.repo, age_seconds=7200)
        self.assertAllowed(PUSH)
        self.assertEqual(sh(self.repo, "git", "status", "--porcelain"), "", "marker must be self-ignored")

    def test_recent_check_covers_a_follow_up_commit(self):
        stamp(self.repo)
        commit(self.repo, "a.txt", "fix")
        self.assertAllowed(PUSH)

    def test_old_check_on_another_commit_is_stale(self):
        stamp(self.repo, age_seconds=7200)
        commit(self.repo, "a.txt", "fix")
        self.assertIn("is stale", self.assertBlocked(PUSH))

    def test_skip_override(self):
        self.assertAllowed(f"QA_CHECK_SKIP=1 {PUSH}")

    def test_uses_hook_cwd_not_project_dir(self):
        stamp(self.repo)  # the main checkout is checked; the worktree is not
        wt = self.add_worktree()
        self.assertBlocked(PUSH, cwd=wt)
        stamp(wt)
        self.assertAllowed(PUSH, cwd=wt)

    def test_follows_cd_into_a_worktree(self):
        stamp(self.repo)
        wt = self.add_worktree()
        self.assertIn(wt, self.assertBlocked(f"cd {wt} && {PUSH}"))
        stamp(wt)
        self.assertAllowed(f"cd {wt} && {PUSH}")
        self.assertAllowed(f"(cd {wt}; {PUSH})")

    def test_follows_git_dash_c(self):
        stamp(self.repo)
        wt = self.add_worktree()
        self.assertBlocked(f"git -C {wt} push")
        stamp(wt)
        self.assertAllowed(f"git -C {wt} push")

    def test_worktree_marker_does_not_unlock_main(self):
        wt = self.add_worktree()
        stamp(wt)
        self.assertBlocked(PUSH, cwd=self.repo)

    def test_unbalanced_quotes_still_gate(self):
        self.assertBlocked(f"cat <<EOF\nit's done\nEOF\n{PUSH}")

    def test_bad_input_passes(self):
        code, _ = self.run_hook(None, raw="not json")
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
