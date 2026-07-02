# Claude Code workflows

Setup decisions and habits that have made a real difference in how much I get out of Claude Code. Some are obvious in retrospect. Most I learned by wasting time doing it the other way first.

---

## Plan before you build

For any non-trivial feature (3+ steps, or anything involving architectural decisions), enter plan mode before writing code (start the session with `--permission-mode plan`, or switch modes in the UI). Add "do deep research on best practices and known issues, using web search" to your prompt. Claude will come back with a structured plan.

Read the plan. Adjust it. Then let it execute.

This matters more than it sounds like it should. Plans survive context compaction much better than vibe-prompted features do. When you're 40 messages into a session and the context window starts compressing earlier messages, a plan at the top of the conversation keeps the LLM anchored. Without one, bigger features tend to drift or lose coherence as the session goes on.

If something goes sideways mid-build, stop and re-plan. Don't let the LLM keep pushing through a broken approach. It will dig itself deeper.

---

## Expand your context window

Install the context-mode plugin:

```
/plugin marketplace add mksglu/context-mode
```

This uses an MCP server to load files into context via reference instead of parking the full file contents in the conversation. The practical effect is a significantly larger effective context window. For any project with more than a handful of files, it's worth the 30 seconds to install.

---

## Build a /documents/ folder

Create a `/documents/` directory with these files. None of them should be loaded by default -- they're on-demand references that the LLM reads when a task requires them (see the [architecture guide's documentation stack](ai-native-architecture.md#principle-9-structured-documentation-as-system-memory) for the token budget reasoning).

**platform-docs.md** -- Describes every feature of your product in detail. Not marketing copy. Actual descriptions of what each screen does, what each component shows, how the business logic works. You can generate an initial version by having Claude Code go through each file and screen and summarize functionality. Then edit it into something accurate.

**ICPs.md** -- Ideal Customer Profiles. A dossier for each type of user: who they are, what they need, what they can and can't do, what frustrates them. Think private detective report, not marketing persona. This keeps Claude from making UX decisions in a vacuum.

**styleguide.md** -- The visual language of your application. Colors, typography, component hierarchy, spacing, responsive breakpoints. You can generate an initial version from an existing codebase using the `--chrome` flag to let Claude see the running app. Then refine it.

**roadmap.md or vision.md** -- Where the product is going. This gives exploratory runs some guardrails. Without it, Claude will build speculative features that don't fit your direction. With it, suggestions tend to align with what you actually want.

**data-reference.md** -- The connections between your domain data that aren't obvious from the models and their relationships. Implicit business rules, edge cases, the stuff a new developer would get wrong on their first PR. If an LLM has to guess at domain logic, it will guess wrong.

---

## Wire it together with CLAUDE.md

Your CLAUDE.md is the entry point for every session. It should index your `/documents/*.md` files with conditional triggers -- telling the LLM *when* to load each one, not dumping them all up front. This follows the Search over Scan principle: the LLM loads what's relevant to the current task, not everything that exists.

```markdown
## Product documentation

All product documentation lives in `/documents/`.

| Document | When to read |
|----------|-------------|
| platform-docs.md | Before adding or modifying any feature. |
| ICPs.md | When making UX decisions or designing user-facing flows. |
| styleguide.md | When creating or modifying UI components. |
| roadmap.md | Before building speculative features or suggesting new scope. |
| data-reference.md | Before any data model, API, or schema changes. |

### Compliance rules
- Use colors, fonts, and patterns from styleguide.md. No new colors without updating the guide.
- New features must be documented in platform-docs.md after implementation.
- Schema or API changes must be reflected in data-reference.md.
```

The compliance rules belong in CLAUDE.md because they're short and always relevant. The docs themselves stay on disk until needed. This way your CLAUDE.md costs ~200 tokens for the index instead of 10K+ tokens loading everything every session.

---

## Workflow orchestration rules worth stealing

These go in your CLAUDE.md and tell the LLM how to work, not just what to work on. They've cut the amount of back-and-forth correction in my sessions significantly.

### Use subagents aggressively

Tell Claude to offload research, exploration, and parallel analysis to subagents. One task per subagent keeps execution focused and keeps the main context window clean. For complex problems, more compute via subagents beats trying to do everything in a single thread.

```markdown
## Subagent strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- One task per subagent for focused execution
```

### Make it learn from corrections

After any correction, have Claude update a `tasks/lessons.md` file with the pattern. The rules should be specific enough to prevent the same mistake next time. Over a few sessions, this file becomes a project-specific style guide for the LLM.

```markdown
## Self-improvement loop
- After ANY correction from the user: update tasks/lessons.md with the pattern
- Write rules for yourself that prevent the same mistake
- Review lessons at session start
```

### Verify before declaring done

Never let the LLM mark a task complete without proving it works. Run the tests. Check the actual output. Diff against main if relevant. "Would a staff engineer approve this?" is a useful gut check to put in the CLAUDE.md.

```markdown
## Verification
- Never mark a task complete without proving it works
- Run tests, check logs, demonstrate correctness
- Diff behavior between main and your changes when relevant
```

### Autonomous bug fixing

When you hand Claude a bug report, it should just fix it. No asking you to look up error messages or check logs. It has the tools. Point at the problem and let it resolve everything -- including failing CI -- without requiring you to context-switch.

```markdown
## Bug fixing
- When given a bug report: just fix it. Don't ask for hand-holding.
- Point at logs, errors, failing tests, then resolve them
- Zero context switching required from the user
```

---

## Task tracking inside the session

For anything that takes more than a few steps, have Claude write a plan to `tasks/todo.md` with checkable items. Mark items complete as they're done. Add a review section when finished. This gives you a paper trail and gives the LLM something concrete to reference when the context window gets long.

```markdown
## Task management
1. Write plan to tasks/todo.md with checkable items
2. Check in before starting implementation
3. Mark items complete as you go
4. Document results and add a review section
5. Capture lessons after corrections
```

---

## Core principles for the CLAUDE.md

These three go at the top. They're short and they prevent the most common failure modes.

**Simplicity first.** Make every change as simple as possible. Touch minimal code. The LLM's instinct is to over-engineer. Push back on that.

**Find root causes.** No temporary fixes, no bandaids, no "this should work for now." Senior developer standards. If something is broken, find out why and fix the actual problem.

**Minimal impact.** Changes should only touch what's necessary. If the task is to fix a button color, don't also refactor the component's state management.

---

## Automated QA in CI

Review habits only work when someone remembers to run them. To make QA structural instead of voluntary, run `/qa-check` headless on every PR with GitHub Actions and `anthropics/claude-code-action@v1`. (v0.x is deprecated; its `mode`/`direct_prompt`/`max_turns` inputs were replaced by `prompt` and `claude_args` in v1.)

Minimal working example -- `.github/workflows/qa-check.yml`:

```yaml
name: qa-check
on:
  pull_request:

jobs:
  qa-check:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: read
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # full history so the base..head diff is available

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Run /qa-check against this pull request. Diff the PR branch
            against origin/${{ github.base_ref }} and review only the
            changed files. Report findings in the skill's standard format.
          claude_args: "--allowedTools Read,Grep,Glob,Bash(git:*),Bash(npm view:*)"
```

Add `ANTHROPIC_API_KEY` as a repository secret. The runner also needs the qa-check skill available: either commit it into the repository (`.claude/skills/qa-check/`) or install the plugin from its marketplace as a setup step before the action runs.

Two operational notes:

- As of June 15, 2026, headless Claude Code (which includes CI runs like this) bills to API credits, not your subscription. Budget for it before turning this on across many repositories.
- Pilot on one repository first. Tune the prompt and allowed tools until the reports are useful, then roll out org-wide.

---

## The meta-point

The context window resets every session. If the knowledge is in your head but not in the files, the LLM is working with incomplete information and you'll spend your time correcting it instead of building.

Put the knowledge in files. Index those files from CLAUDE.md with conditional triggers so the LLM loads what it needs, when it needs it.
