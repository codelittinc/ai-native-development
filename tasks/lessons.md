# Lessons

## 2026-07-03 — Billing model is an architecture constraint
The v3.0 workflows guide recommended running /qa-check in CI via `anthropics/claude-code-action@v1`. Rejected: headless/CI invocations bill API credits (June 15, 2026 billing change), and this team runs on subscription. Interactive sessions are the only subscription-covered surface.

**Rule:** Any automation that invokes Claude must run inside an interactive session (skills, hooks) or contain no LLM call at all (deterministic scripts, grep-level CI checks). Check the billing surface BEFORE designing enforcement, not after.

## 2026-09-28 — A hook's repo is where the command runs, not where the session started
The push gate resolved the repo with `git -C "$CLAUDE_PROJECT_DIR"`. That variable stays on the main checkout after a session enters a git worktree, so a worktree push was compared against another branch's HEAD. The skill wrote its marker through `git rev-parse --git-dir` (the per-worktree dir), so the check and the gate never met, and worktree isolation blocks writes under the shared `.git` anyway. In practice every worktree push needed `QA_CHECK_SKIP=1`, and a gate that always needs an override stops protecting anything.

**Rule:** Resolve the target from the hook input's `cwd` plus the command's own `cd` / `git -C`. Derive the writer's and the reader's paths from one expression, and test them together. Keep hook state inside the working tree, not under `.git`.
