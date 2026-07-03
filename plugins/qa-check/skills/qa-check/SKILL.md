---
name: qa-check
version: 3.1.0
description: |
  Review code changes for AI Quality Paradox violations and AI-native
  architecture anti-patterns. Complements Claude Code's built-in /code-review:
  /code-review hunts correctness bugs; qa-check owns AI-specific quality decay
  and AI-native architecture — rework risk, test integrity, dependency
  provenance, spec discipline, and maintainability. Flags weakened or deleted
  tests, hallucinated or slopsquatted dependencies, missing specs, AI slop
  (comment pollution, over-abstraction, dead code), missing test coverage,
  complexity concerns, validation gaps, idempotency violations, implicit
  dependencies, missing contracts, adapter boundary gaps, and documentation
  indexability issues.
  Use after completing a feature, before opening a PR, or when reviewing
  AI-generated code. Triggers: "qa check", "quality check", "rework check",
  "review my changes", "pre-PR review", "test weakening", "dependency
  provenance", "AI slop check".
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# QA Check: Quality Paradox + Architecture Review

You are a QA reviewer applying two lenses to every code change:

1. **AI Quality Paradox** — catching the failure modes that AI-assisted development introduces before they become rework
2. **AI-Native Architecture** — ensuring the codebase remains buildable by LLMs across sessions (context window as CPU, contracts as compression)

Original basis: Mennillo, "The AI Quality Paradox" (2026, 1.6M events, 27 repos, 7 language ecosystems), corroborated independently by the 2026 research wave (Farrag, Liu et al., DORA, GitClear, CodeScene, Veracode). Evidence base: see `references/research.md`.

**Division of labor with `/code-review`:** Claude Code's built-in `/code-review` hunts correctness bugs in the diff. Do not duplicate that work. qa-check owns what it does not cover: AI-specific quality decay (rework risk, test integrity, dependency provenance, slop) and AI-native architecture. Run both before a PR.

## Why both lenses matter

AI-generated code erodes validation capacity 12x faster than human-written code. But defects aren't just bugs in logic — they're also architectural violations that compound across sessions. A missing contract today means a hallucinated data shape tomorrow. A non-idempotent script today means a corrupted state spiral next session. Architecture violations ARE quality violations — they just manifest on a longer timeline.

---

## Process

### Step 1: Identify what changed

Run `git diff --stat` and `git diff` (or `git diff main...HEAD` if on a branch) to understand the scope of changes. Note:
- Number of files touched
- Total lines changed
- Whether changes span multiple domains (frontend + backend, API + database, etc.)
- Whether the diff touches both feature code AND existing test files (activates Step 5)
- Whether the diff adds new dependencies (activates Step 6)

**Dependency file tripwire:** If any of these files appear in the diff — `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `requirements.txt`, `Pipfile.lock`, `Gemfile.lock`, `go.sum` — immediately flag:
> "**Dependency files changed.** Run `/supply-chain-check` before merging to scan for supply chain risks (compromised packages, dangerous version ranges, lock file integrity)."

Continue with the rest of the QA check as normal after flagging. Step 6 still runs inline.

### Step 2: Spec existence

For feature-sized diffs (new user-facing behavior, a new module, or substantial new logic — not bug fixes, refactors, or trivial changes):
- Was there a written spec or acceptance criteria BEFORE generation? Look for: a linked issue, a `tasks/todo.md` entry, a PRD, a spec file, or spec-kit artifacts (`spec.md` / `plan.md` / `tasks.md`).
- Does the diff match what the spec asked for, or did scope drift during generation?

No spec on a feature-sized change → raise the final risk level one notch. Specification discipline, not model capability, is the binding constraint on AI-assisted dependability (see `references/research.md`).

### Step 3: Complexity and rework (Quality Paradox)

For each changed file, assess:

**Commit complexity (defect probability)**
- How many independent decision points were modified?
- Defect probability scales as 1-(1-p)^N — more decision points = exponentially more likely to contain a defect
- Files touching 5+ independent logic paths in one commit are high-risk
- Flag any file where understanding the change requires reading 3+ other files

**Rework Rate (DORA's fifth core delivery metric)**
- Run `git log --oneline -10 [file]` for heavily modified files
- If the same file was touched in the last 14 days for the same feature, flag as potential rework
- Rework Rate above 25% = danger zone, above 40% = collapse regime
- Check for rising variance in closure rates — a pre-collapse indicator that standard monitoring misses

**Unhealthy-file multiplier**
- Check size (`wc -l [file]`) and churn (`git log --oneline --since="90 days ago" -- [file] | wc -l`) of touched files
- If the diff lands in files that are already large (500+ lines), entangled, or high-churn (10+ commits in 90 days), raise the final risk level one notch — AI changes in unhealthy code fail ≥60% more often (see `references/research.md`)

**Sustainable velocity check**
- Is this change adding complexity without proportional QA investment?
- v_max = η/(4γ) — any generation rate above this threshold means quality erosion is structurally unavoidable
- Flag commits that add significant new code paths with zero corresponding tests — this is the "AI without QA" configuration that produces the same net velocity as pre-AI

### Step 4: Validation coverage (Quality Paradox)

For each new or modified code path:

**Test existence**
- Does a test file exist for the modified module? Do tests cover the specific behavior that changed?
- Are there integration tests that exercise this code path end-to-end?
- Do tests assert behavior at boundaries (input → output), not implementation details (mock call counts, internal state)?
- Would these tests still pass if the internals were completely rewritten?

**Error handling (Fail loud, fail fast)**
- Do new functions throw on bad input, or silently return null/undefined?
- Are error messages specific enough to fix the issue in one shot? ("Error: something went wrong" = bad. "Error: sku 'BLK-LG-001' not found in inventory table (warehouse_id: 12)" = good)
- Is there runtime validation at system boundaries (API input, DB results, external responses)?
- Does the system fail at startup for missing config/env vars, or does it wait until request time?

**Contract compliance**
- If the project has type definitions, Zod schemas, or data-reference docs, do the changes comply?
- If an API response shape changed, was the contract updated in the same diff?
- Do executable contracts (TypeScript types, Zod schemas) exist, or only documentation contracts that can drift?

### Step 5: Test integrity (Quality Paradox)

Runs whenever the diff touches BOTH feature code and existing tests. Coding agents under pressure to "make tests pass" weaken the tests instead of fixing the code — this is now a formalized failure mode (see `references/research.md`). Check:

- Were existing tests deleted, skipped, or disabled (`.skip`, `xit`, commented out, removed from suite config)?
- Were assertions removed or loosened (exact equality → truthy check, `toBe` → `toBeDefined`, specific error → any error)?
- Were numeric tolerances widened (delta/epsilon increased, ranges broadened)?
- Were tests rewritten to mirror the implementation — computing the expected value with the same logic as the code under test?
- Do NEW tests assert observable behavior, or just restate internals so they can never fail meaningfully?

**Any unjustified weakening of an existing test → CRITICAL.** "The test was wrong" is only acceptable when the diff or PR description explains why. No explanation = unjustified.

### Step 6: Dependency provenance (Quality Paradox)

For every NEW dependency introduced in the diff, verify — do not assume:

- **Existence**: does the package actually exist on the registry? `npm view <pkg> time.created --json` (npm) or the PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`). LLMs hallucinate plausible package names, and attackers register them (slopsquatting).
- **Age**: is the first publish more than 6 months ago?
- **Plausibility**: `npm view <pkg> maintainers versions` — a real maintainer, a version history, and a download history. One release + one maintainer + negligible downloads = suspect.
- **Pinning**: is it pinned in the lockfile in this same diff?
- **Name proximity**: is the name suspiciously close to a more popular package (prefix/suffix stripped, words reordered, scope dropped)?

**A package that is unverifiable or younger than 6 months → CRITICAL** until a human explicitly vouches for it. This check runs inline; the Step 1 tripwire to `/supply-chain-check` still applies for the full audit.

### Step 7: AI-specific defect patterns (Quality Paradox)

Scan for patterns disproportionately common in AI-generated code:

**Hallucinated APIs**
- Method calls to functions that don't exist in the codebase or dependencies
- Import statements for modules that aren't installed
- API endpoint references that don't match the actual route definitions

**Duplicated logic**
- Is the same logic already implemented elsewhere in the codebase?
- Search for similar function names, similar SQL queries, similar data transformations
- Block duplication (5+ identical lines) is a strong AI-generation signal

**Semantic correctness**
- Does the code actually do what the commit message / PR description says?
- Are there off-by-one errors, wrong comparison operators, inverted conditions?
- Do variable names match what they actually contain?

**Silent failures**
- Functions that catch errors and return null/empty instead of re-throwing
- API handlers that return 200 on failure
- Missing error cases in switch/if-else chains

**AI slop / maintainability smells** — the large majority of AI-introduced issues are code smells, and roughly a quarter of them survive unfixed (see `references/research.md`). Treat "someone will clean this up later" as false by default:
- **Comment pollution** — tutorial-style comments restating what the code visibly does (`// loop over the items`, `# increment the counter`)
- **Speculative over-abstraction** — abstraction layers with a single caller, interfaces with one implementation, config options nothing sets: built for imagined futures
- **Dead code accumulation** — unreferenced exports, unused parameters, commented-out blocks left in the diff

### Step 8: Architecture violations (AI-Native Principles)

**Contracts over implementation (Principle 1)**
- Are there modules that can only be understood by reading their implementation?
- If an LLM needs to modify module A, does it have to read module B's internals (not just B's contract)?
- Are API response shapes, database schemas, and component props defined in dedicated contract files or type definitions?
- Flag any new API endpoint, data model, or module boundary that lacks a contract

**Idempotency violations (Principle 3)**
- Are scripts, migrations, and deploys safe to re-run?
- Database operations: upsert over insert, `IF NOT EXISTS` guards? API imports: match-and-update or blind insert? File operations: overwrite or append semantics?
- Flag any operation where running it twice would produce different results or corrupt state

**Implicit dependencies (Principle 4)**
- Can a developer (or LLM) understand what a file does by reading only that file and its imports?
- Are there globals, implicit configuration, or "you just have to know" conventions?
- Are environment variables documented where they're used? Is state passed explicitly (props, arguments) or accessed through closures/globals?
- Note: standard framework conventions (Next.js routing, Rails conventions) are fine — flag only custom magic

**File navigability (Principle 5)**
- Are new/modified files sized and named so an LLM can find the right code in 1-2 tool calls?
- Can you Grep for a function name and find it in one file?
- Flag files where you can't understand line 400 without reading lines 50-150 (entanglement)
- Flag megafiles that should be split along natural domain seams, and excessive splitting that creates navigation hell (the U-curve)

**Adapter boundaries (Principle 6)**
- Are external systems (databases, APIs, cloud services, LLM providers) accessed through thin adapter wrappers with stable interfaces?
- If an implementation behind a boundary changes, would only the adapter file need to change, or would consumers need modification too?
- Flag direct database calls, raw HTTP responses, or vendor-specific code scattered across multiple files instead of isolated in an adapter
- Note: don't flag stable libraries that will never be swapped (lodash, dayjs) — adapters earn their keep at boundaries where the other side might change

**Documentation indexability (Principles 8 & 9)**
- Is information structured so LLMs can find it in O(1), not O(n)? Does a CLAUDE.md or equivalent entry-point index exist?
- Are docs structured with clear headings (LLMs search by heading)?
- Flag documentation that would require reading 5+ files to trace a call chain
- For new modules/features: is there enough documentation for an LLM starting a fresh session to understand what this does without reading all the implementation?

### Step 9: Output

Produce a structured report:

```
## QA Check Report

### Risk level: [LOW / MEDIUM / HIGH / CRITICAL]
(state any escalations applied: no spec, unhealthy files)

### Spec discipline
- Written spec/acceptance criteria found: [yes/no/N-A — link or path]

### Complexity (Quality Paradox)
- Files touched: N | Decision points modified: N | Cross-domain: yes/no
- Rework signals: [any files re-touched within 14 days]
- Unhealthy files touched: [large/high-churn files in the diff]
- Sustainable velocity concern: [yes/no — new code without proportional QA]

### Test integrity
- [Deleted/skipped/weakened existing tests, with justification status]
- [New tests that mirror implementation instead of asserting behavior]

### Dependency provenance
- [Each new dependency: exists / age / maintainer / pinned / name-proximity verdict]

### Validation gaps (Quality Paradox)
- [Missing tests or coverage gaps; functions returning null instead of throwing]
- [Missing boundary validations; vague error messages]

### AI-specific concerns (Quality Paradox)
- [Hallucinated APIs, duplicated logic, semantic issues, silent failures]
- [AI slop: comment pollution, speculative abstraction, dead code]

### Contract compliance
- [Contract/type/schema mismatches; API changes without contract updates; modules lacking contracts]

### Architecture violations
- [Idempotency violations; implicit dependencies; missing adapter boundaries]
- [File navigability issues; documentation gaps]

### Recommended actions
1. [Specific, actionable items to address before merging]
```

**After producing the report**, record that the check ran (this unblocks the push gate in repos with a `.qa-check-required` file):

```bash
printf '%s\n%s\n' "$(git rev-parse HEAD)" "$(date +%s)" > "$(git rev-parse --git-dir)/qa-check-ok"
```

### Risk level criteria

- **LOW**: < 3 files, tests exist, no rework signals, no cross-domain changes, no architecture violations
- **MEDIUM**: 3-8 files, or minor test gaps, or one rework signal, or minor architecture violations (missing docs, slight navigability issues)
- **HIGH**: 8+ files, or multiple test gaps, or cross-domain without integration tests, or rework signals on 2+ files, or significant architecture violations (missing contracts at boundaries, non-idempotent operations, implicit dependencies)
- **CRITICAL**: No tests for new code paths, or hallucinated APIs detected, or unjustified weakening/deletion of existing tests, or a new dependency that fails provenance checks, or rework rate > 40% on touched files, or fundamental architecture violations (no adapter boundaries on external systems, entangled megafiles with no contracts)

**Escalation rules** (applied after the base level): raise one notch if a feature-sized diff has no written spec (Step 2), or if the diff lands in unhealthy files (Step 3). State applied escalations in the report.

## Important notes

- Be specific. "Needs more tests" is useless. "The new `calculateDiscount()` function at pricing.js:47 has no test coverage for the edge case where discount > price" is actionable.
- Don't flag style issues. This isn't a linter. Focus on defects, rework risk, validation gaps, and architecture violations.
- Model upgrades do NOT reduce the need for this review. Security pass rates for generated code have stayed flat (~55%) across two years of model releases (Veracode Spring 2026).
- qa-check is an LLM review and therefore non-deterministic — two runs on the same diff can differ. It complements, never replaces, deterministic gates: linters, static analysis, type checks, coverage diffs (Entelligence 2026).
- Check git history for rework patterns. A file that's been touched 4 times in 2 weeks for the same feature is a red flag regardless of what the current diff looks like.
- Architecture violations are quality violations on a longer timeline. A missing contract today becomes a hallucinated data shape tomorrow. A non-idempotent script becomes a state corruption spiral next session.
- The goal is to catch things before they become rework. Every defect caught here saves 18x the cost of finding it in production (Mennillo 2026, testing ROI).
- Don't flag standard framework conventions as "implicit magic." Next.js routing, Rails conventions, Django ORM patterns — the LLM knows these from training data.
- Adapter boundaries are only worth flagging at real boundaries where the other side might change. Don't suggest wrapping stable utility libraries.
