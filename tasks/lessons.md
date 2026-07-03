# Lessons

## 2026-07-03 — Billing model is an architecture constraint
The v3.0 workflows guide recommended running /qa-check in CI via `anthropics/claude-code-action@v1`. Rejected: headless/CI invocations bill API credits (June 15, 2026 billing change), and this team runs on subscription. Interactive sessions are the only subscription-covered surface.

**Rule:** Any automation that invokes Claude must run inside an interactive session (skills, hooks) or contain no LLM call at all (deterministic scripts, grep-level CI checks). Check the billing surface BEFORE designing enforcement, not after.
