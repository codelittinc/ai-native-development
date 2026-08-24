---
name: qa-check
version: 4.0.0
description: |
  Examine code changes for AI Quality Paradox problems and for AI-native
  architecture problems. This skill is an addition to the /code-review command
  in Claude Code. The /code-review command finds correctness defects. This
  skill finds AI-specific quality decay and architecture defects: rework risk,
  test integrity, dependency source, specification discipline,
  agent-buildability, and maintainability. It reports weak or deleted tests,
  error paths with no test, tests that use external resources, dependencies
  that do not exist, secrets in the code, agent configuration files, prompt
  injection paths, missing specifications, AI slop, missing test coverage, too
  much complexity, missing data checks, operations that are not safe to do
  again, hidden dependencies, missing contracts, missing adapter boundaries,
  and context files that are too large.
  Use this skill after you complete a feature, before you open a pull request,
  or when you examine AI-generated code. Triggers: "qa check", "quality check",
  "rework check", "review my changes", "pre-PR review", "test weakening",
  "dependency provenance", "AI slop check", "agent-friendly", "LLM-friendly
  codebase".
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# QA Check: Quality Paradox and Architecture Review

You are a QA reviewer. Apply these three lenses to each code change:

1. **AI Quality Paradox** — find the failure modes that AI-assisted development causes, before they become rework
2. **AI-Native Architecture** — keep the codebase easy for an LLM to build in across many sessions
3. **Agent-buildability** — leave the codebase less costly and more safe for the next agent session

The first basis is Mennillo, "The AI Quality Paradox" (2026). That study used 1.6 million development events, 27 repositories, and 7 language ecosystems. Other 2026 studies agree with its main claims: Farrag, Liu et al., DORA, GitClear, CodeScene, and Veracode. The studies from the middle of 2026 add more: the SonarSource minimal-pair study, CodeThread, the AIDev test analyses, and Gloaguen et al. on context files. For the full evidence, read `references/research.md`.

**How this skill divides work with `/code-review`:** The `/code-review` command finds correctness defects in the diff. Do not do that work again. This skill covers what `/code-review` does not: AI-specific quality decay and AI-native architecture. Run both commands before a pull request.

## Technical names in this document

This document uses Simplified Technical English (ASD-STE100). These technical names do not have approved equivalents, so the document keeps them and defines them here:

| Technical name | Meaning |
|---|---|
| AI slop | Low-value code that AI tools add: unnecessary comments, unnecessary abstraction, dead code |
| Idempotent | Safe to do more than one time, with the same result each time |
| Hermetic test | A test that does not use the file system, the network, the clock, or random values |
| Provenance | The source and history of a dependency |
| Rework | Work that changes code again, for the same feature, soon after the first change |
| Slopsquatting | An attack that registers a package name that an LLM invents |
| Context file | A file that an agent reads at session start, such as CLAUDE.md or AGENTS.md |

## Why all three lenses are necessary

AI-generated code decreases validation capacity 12 times more quickly than code that a person writes. But defects are not only logic errors. Defects are also architecture violations that increase across sessions. A missing contract today causes an incorrect data shape tomorrow. A script that is not idempotent today causes corrupt state in the next session. Architecture violations are quality violations on a longer timeline.

---

## Process

### Step 1: Find what changed

Run `git diff --stat` and `git diff` to find the size of the change. On a branch, run `git diff main...HEAD`. Record these items:

- The number of files that changed
- The total number of lines that changed
- If the change covers more than one domain, such as frontend and backend, or API and database
- If the diff touches both feature code and existing test files, which starts Step 5
- If the diff adds new dependencies, which starts Step 6

**Dependency file alarm:** Look for these files in the diff: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `requirements.txt`, `Pipfile.lock`, `Gemfile.lock`, `go.sum`. If the diff contains one of them, report this immediately:

> "**Dependency files changed.** Run `/supply-chain-check` before you merge. That command finds supply chain risks: packages that attackers control, dangerous version ranges, and lock file problems."

Continue with the other steps after you report this. Step 6 also runs.

### Step 2: Specification existence

Do this step for feature-size diffs. A feature-size diff adds new behavior that a user sees, a new module, or a large quantity of new logic. Do not do this step for defect corrections, refactors, or small changes.

- Find out if a written specification or acceptance criteria existed before generation. Look for a linked issue, a `tasks/todo.md` entry, a PRD, a specification file, or spec-kit files (`spec.md`, `plan.md`, `tasks.md`).
- Compare the diff to the specification. Find out if the scope changed during generation.

If a feature-size change has no specification, increase the final risk level by one step. Specification discipline is the limit on AI-assisted dependability, not model capability. For the evidence, read `references/research.md`.

### Step 3: Complexity and rework (Quality Paradox)

Examine each file that changed.

**Commit complexity (defect probability)**

- Count the independent decision points that changed.
- Defect probability increases as 1-(1-p)^N. More decision points cause much more probability of a defect.
- A file with 5 or more independent logic paths in one commit has a high risk.
- Report each file where you must read 3 or more other files to understand the change.

**Rework rate (the fifth core DORA delivery metric)**

- Run `git log --oneline -10 [file]` for each file with many changes.
- If a person changed the same file in the last 14 days for the same feature, report possible rework.
- A rework rate above 25% is dangerous. A rework rate above 40% shows collapse.
- Look for an increase in the variance of closure rates. This shows collapse before usual monitoring finds it.

**Unhealthy file multiplier**

- Find the size with `wc -l [file]`.
- Find the churn with `git log --oneline --since="90 days ago" -- [file] | wc -l`.
- A file is unhealthy if it is large (500 lines or more), entangled, or has high churn (10 or more commits in 90 days).
- If the diff touches an unhealthy file, increase the final risk level by one step. AI changes in unhealthy code fail at least 60% more frequently. For the evidence, read `references/research.md`.

**Sustainable velocity check**

- Find out if this change adds complexity but does not add QA work in proportion.
- The velocity limit is v_max = η/(4γ). Above this limit, quality decay is unavoidable.
- Report each commit that adds many new code paths but adds no tests. This condition gives the same net velocity as development before AI.

### Step 4: Validation coverage (Quality Paradox)

Examine each new or changed code path.

**Test existence**

- Find out if a test file exists for the module that changed.
- Find out if the tests cover the behavior that changed.
- Find out if integration tests operate this code path from end to end.
- Find out if the tests examine behavior at the boundaries, from input to output. Tests must not examine internal details, such as mock call counts or internal state.
- Ask this question: if a person writes the internals again, do these tests continue to pass?

**Error path coverage**

Error handling code is the construct with the least test coverage in agent-written pull requests. The miss rate is 86% in Java and 81% in Python. For the evidence, read `references/research.md`.

Examine each `try`, `catch`, `except`, `rescue`, error branch, or early return on failure that this diff adds:

- Find out if a test enters that branch. A happy-path test that does not operate the branch is not sufficient.
- Use Grep on the test files for the error type or the error message. If only the source contains the error, no test covers the branch.
- Agents add test changes to approximately half of the pull requests that touch code under test. Existing test suites cover as little as 27% of the lines that changed. Do not assume that the existing suite covers this code.

**Report an error branch with no test as HIGH.** Report it as CRITICAL if the branch controls money, authentication, data deletion, or external writes.

**Error handling (fail loudly and quickly)**

- Find out if new functions throw an error for bad input. A function that returns null or undefined without a message is a defect.
- Find out if the error messages are sufficient to correct the problem in one operation. "Error: something went wrong" is bad. "Error: sku 'BLK-LG-001' not found in inventory table (warehouse_id: 12)" is good.
- Find out if the code validates data at the system boundaries: API input, database results, and external responses.
- Find out if the system fails at start for a missing configuration value. A system that fails only at request time is a defect.

**Contract compliance**

- If the project has type definitions, Zod schemas, or data reference documents, find out if the changes obey them.
- If an API response shape changed, find out if the same diff also changed the contract.
- Find out if executable contracts exist, such as TypeScript types or Zod schemas. Documentation contracts alone can become incorrect.

### Step 5: Test integrity (Quality Paradox)

Do this step when the diff touches both feature code and existing tests.

Coding agents that must "make the tests pass" can make the tests weaker instead of correcting the code. Research gives a name to this failure mode. For the evidence, read `references/research.md`. Examine these items:

- Find out if a person deleted, skipped, or disabled existing tests. Look for `.skip`, `xit`, comments, and removal from the suite configuration.
- Find out if a person removed or weakened assertions. Examples: exact equality became a truthy check, `toBe` became `toBeDefined`, a specific error became any error.
- Find out if a person made numeric tolerances larger. Look for a larger delta or epsilon, or a wider range.
- Find out if a person wrote the tests again to copy the implementation. Such a test calculates the expected value with the same logic as the code under test.
- Find out if the new tests examine behavior that a user can observe. A test that only repeats the internals cannot fail in a useful way.

**Report each weak test with no reason as CRITICAL.** "The test was wrong" is acceptable only when the diff or the pull request description gives the reason. If there is no reason, the change has no justification.

**Signatures of agent-written tests**

A comparison of 204,673 test artifacts found a specific profile. For the evidence, read `references/research.md`. Agents are better than people at boundary coverage and null-safety coverage. Agents are a little weaker at assertion strength. Agents are much worse at hermetic tests: the flakiness candidate rate is 0.41 against 0.30. Real file input and output, and non-deterministic logic, cause this result.

Use this profile:

- **Do not** ask for more edge cases in agent-written tests. Agents are already good at this dimension.
- **Do** examine each new test for hermetic behavior. Find out if the test uses the real file system, the network, the system clock, `random`, or an unordered collection. Each of these can cause a flaky test in CI. A flaky suite teaches the next agent to make the tests weaker.
- **Do** find out if the test uses assertions to observe results. Agents write value-revealing print statements much more frequently than assertions. For the evidence, read `references/research.md`. These temporary tests sometimes reach the commit. Look for `print`, `console.log`, and log calls that replace an assertion.
- **Do** look for assertions that use only exact values, where a relational assertion or a range assertion is the correct oracle. Examples: time, floating point values, order, and generated identifiers. This item is an opinion, not a measured result. Apply it when the oracle is clearly wrong. Do not apply it as a quota.

**Report a new test that is not hermetic as MEDIUM.** Report it as HIGH if the test is in a suite that controls CI.

### Step 6: Dependency provenance (Quality Paradox)

Check each NEW dependency in the diff. Do not assume that a dependency is correct.

- **Existence**: Find out if the package exists in the registry. For npm, run `npm view <pkg> time.created --json`. For Python, use the PyPI JSON API at `https://pypi.org/pypi/<pkg>/json`. LLMs invent package names that look correct, and attackers register those names. This attack is slopsquatting.
- **Age**: Find out if the first release is more than 6 months old.
- **Plausibility**: Run `npm view <pkg> maintainers versions`. A safe package has a real maintainer, a version history, and a download history. One release, one maintainer, and very few downloads together show a risk.
- **Pinning**: Find out if the same diff pins the package in the lock file.
- **Name proximity**: Find out if the name is very near to the name of a more popular package. Look for a removed prefix, a removed suffix, words in a different order, or a removed scope.

**Report a package as CRITICAL if you cannot check it, or if it is less than 6 months old.** Keep this level until a person accepts the risk. This step runs in this skill. The Step 1 alarm for `/supply-chain-check` also applies, for the full audit.

### Step 7: AI-specific defect patterns (Quality Paradox)

Look for the patterns that occur much more frequently in AI-generated code.

**Invented APIs**

- Calls to functions that do not exist in the codebase or in the dependencies
- Import statements for modules that are not installed
- API endpoint references that do not agree with the route definitions

**Duplicate logic**

- Find out if the same logic exists in a different location in the codebase.
- Search for function names, SQL queries, and data transformations that are similar.
- A duplicate block of 5 or more identical lines is a strong signal of AI generation.

**Semantic correctness**

- Find out if the code does what the commit message or the pull request description says.
- Look for off-by-one errors, incorrect comparison operators, and inverted conditions.
- Find out if the variable names agree with the values that they hold.

**Silent failures**

- Functions that catch an error and return null or an empty value, but do not throw the error again
- API handlers that return 200 after a failure
- Missing error cases in switch or if-else structures

**AI slop and maintainability problems**

Most AI-introduced problems are code smells, and approximately one quarter of them stay in the code. For the evidence, read `references/research.md`. Do not accept the opinion that a person will correct these problems later.

- **Too many comments** — comments that repeat what the code shows, such as `// loop over the items` or `# increment the counter`
- **Unnecessary abstraction** — an abstraction layer with one caller, an interface with one implementation, or a configuration option that nothing sets
- **Dead code** — exports with no reference, unused parameters, and blocks in comments
- **Extended anti-patterns** — repeated agent edits do not only keep an anti-pattern, they make it larger. Each turn keeps the pattern and adds to it. Long constructions replace short idioms. For the evidence, read `references/research.md`. When the diff makes a block with a known problem larger, report the extension, not only the new lines. Ask this question: is the pattern now more difficult to remove?

### Step 8: Architecture violations (AI-native principles)

**Contracts before implementation (principle 1)**

- Look for modules that a reader can understand only from the implementation.
- Find out if an LLM must read the internals of module B to change module A. The contract of module B must be sufficient.
- Find out if contract files or type definitions hold the API response shapes, the database schemas, and the component properties.
- Report each new API endpoint, data model, or module boundary that has no contract.

**Operations that are not idempotent (principle 3)**

- Find out if scripts, migrations, and deployments are safe to run again.
- For database operations, look for upsert instead of insert, and for `IF NOT EXISTS` guards.
- For API imports, look for match-and-update instead of a blind insert.
- For file operations, find out if the code overwrites or appends.
- Report each operation that gives a different result, or corrupts state, when it runs two times.

**Hidden dependencies (principle 4)**

- Find out if a person or an LLM can understand a file from that file and its imports alone.
- Look for global values, hidden configuration, and conventions that a reader must already know.
- Find out if the code documents the environment variables where it uses them.
- Find out if the code moves state explicitly, through properties or arguments. State from closures or globals is a defect.
- Do not report standard framework conventions, such as Next.js routing or Rails conventions. These are acceptable. Report only custom behavior that a reader cannot see.

**File navigability (principle 5)**

- Examine the size and the name of each new file and each changed file. An LLM must find the correct code in 1 or 2 tool calls.
- Find out if Grep on a function name finds that function in one file.
- Report each file where a reader cannot understand line 400 without lines 50 to 150. This condition is entanglement.
- Report very large files that a person can divide along domain boundaries. Also report too many small files, because they make navigation difficult. Both extremes are bad.
- **Report navigability as a cost defect, not a correctness defect.** A controlled minimal-pair experiment used 660 trials. It compared clean repositories with degraded repositories that had the same architecture and the same behavior. Cleanliness did **not** change the pass rate of the agent. Cleanliness did decrease token use by 7% to 8%, and decreased file revisits by 34%. For the evidence, read `references/research.md`. Therefore, do not increase the risk level for navigability alone. Give the finding in its true units: this costs tokens and repeated reads in each future session. Do not say that it causes a defect. Increase the risk level only when entanglement hides a contract.

**Adapter boundaries (principle 6)**

- Find out if the code reaches external systems through thin adapter wrappers with stable interfaces. External systems include databases, APIs, cloud services, and LLM providers.
- Find out if a change behind a boundary needs a change in the adapter file only. If the consumers also need changes, the boundary is not sufficient.
- Report direct database calls, raw HTTP responses, and vendor-specific code in more than one file. This code belongs in an adapter.
- Do not report stable libraries that nobody will replace, such as lodash or dayjs. An adapter is useful only at a boundary that can change.

**Documentation indexability (principles 8 and 9)**

- Find out if an LLM can find the information in O(1) time, not O(n) time.
- Find out if the documents have clear headings. LLMs search by heading.
- Report documentation that needs 5 or more files to follow a call chain.
- For each new module or feature, find out if the documentation is sufficient. An LLM in a new session must understand the purpose without a read of all the implementation.

**Context files (CLAUDE.md, AGENTS.md, Cursor rules)**

Many people believe that a larger and better organized context file makes an agent better. The evidence does not support this belief.

One study used SWE-bench tasks and also repositories with context files that developers wrote. Context files did **not** generally improve the task success rate. Context files did increase the inference cost by **more than 20%**. Agents followed the instructions well. But *repository overviews did not help*, although most guidance recommends them.

A second study was a factorial experiment over 1,650 Claude Code sessions. It manipulated four variables: file size, instruction position, file architecture, and contradictions between adjacent files. None of the four variables had a measurable effect on adherence. For the evidence, read `references/research.md`.

When the diff touches a context file, do these checks:

- **Report overview prose and architecture tours as unnecessary cost.** Each session pays this cost, and the evidence shows no benefit. Remove this prose, or move it to documents that the agent can Grep when it needs them.
- **Keep the instructions that an agent cannot infer.** Examples: the test command for this repository, the migration procedure, "never edit `generated/`", and a house idiom that is different from the framework default. This content has a measured value.
- **Do not report the file structure, the order, or the size.** These variables had no measurable effect. Report only the total cost and the ratio of overview text to instructions.
- **Do report contradictions with the code.** Adjacent-file conflicts have no measured effect on adherence. But an agent follows an incorrect instruction exactly and with confidence.
- If an LLM generated a context file in this diff, say so, and ask for a review by a person. Auto-generated context files gave *worse* results than no context file in the SWE-bench setting.

**Instruction decay in one session**

The largest measured effect in the factorial study was not structural. Adherence to a repository convention decreases by approximately 5.6% in odds for each additional function that the agent generates in one session. If this diff is one long generation run, expect the conventions to decay near the end. Examine the files that changed last more carefully than the files that changed first. Recommend shorter runs. Do not recommend a new context file.

### Step 9: Downstream agent-buildability

This code is not complete when it ships. It is complete when the next agent session can extend it.

A controlled study used the CodeThread framework, four frontier agents, and four repository-level benchmarks. Agents completed tasks up to **13.1% less frequently when they built on agent-written code than on code that a person wrote**. Usual maintainability metrics did not explain this difference. Two signals did explain it: **differences in input validation and in error handling**. Downstream code size also explained part of it. For the evidence, read `references/research.md`.

Therefore, look for validation differences and error handling differences between the new code and the code near it. A linter cannot find these differences.

- Find out if the new code validates its inputs in the same way as the module around it. Report code that trusts its callers where the adjacent code does not. Also report defensive checks that the conventions put at the boundary instead.
- Find out if the new code handles errors in the style of the codebase. Look for the same error types, the same propagation direction, and the same log contract. Report a second convention next to the first one.
- Ask this question: are there now two answers to "what happens with bad input here?" Two conventions degrade the next session, because the agent must guess which one applies.
- Find out if the change is larger than the task needs. Extra downstream code size is an independent predictor of failure.

**Report two validation conventions or two error handling conventions in one module as HIGH.** Say which convention you think is the correct one.

### Step 10: Agent surface and secrets

AI-assisted development has a threat surface that usual code review does not examine. These artifacts are not source code. They are content that an agent reads and obeys.

This step covers only the agent-specific part. The `/security-review` command covers general security. The `/supply-chain-check` command covers dependencies.

**Secrets in the code**

AI-assisted commits release secrets at a rate of approximately **3.2%, against a baseline of 1.5%** across public GitHub commits. For the evidence, read `references/research.md`.

Examine the diff, not only the source files. Fixtures, test files, `.env.example`, snapshot files, and documents can all contain secrets.

```bash
# Use the SAME diff range that you set in Step 1. On a branch, add main...HEAD.
git diff -U0 | grep -E '^\+[^+]' | grep -Ei '(api[_-]?key|secret|passwd|password|token|bearer|private[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|aws_(access|secret)|sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,})' | head -40
```

Read each result to confirm it. Placeholders and variable names are not secrets.

**Report a real secret in the diff as CRITICAL.** Also say that a later commit does not correct the problem. The value stays in the history. A person must change the secret.

**Agent configuration in the diff**

These files give capability to an agent. Examine them with the same care as source code, not as documentation.

- `.mcp.json`, `.claude/settings.json`, `.claude/settings.local.json` — a new MCP server is a new dependency with the authority of the agent. Ask who publishes it. Ask what it can reach.
- Hook definitions such as `hooks.json`, `PreToolUse` entries, and `PostToolUse` entries — these run shell commands at each applicable tool call.
- New or changed permission lists — find out if the diff makes `allow` wider than necessary. A wider `Bash(*)` permission is a finding.
- `.claude/skills/**`, `.claude/agents/**`, `CLAUDE.md`, `AGENTS.md` — an agent obeys these instructions.
- CI workflows that run an agent, such as `.github/workflows/**` — find out what starts them and what secrets they mount.

**Paths for untrusted content**

Three conditions together cause a serious risk: access to private data, exposure to untrusted content, and a channel to the outside. Find out if this change adds the second condition.

- Find out if the change causes an agent to read text that an attacker can control, and then to act on that text. Examples: issue bodies, pull request titles, commit messages, review comments, dependency README files, web pages, records that users supply, and output from a third-party API.
- Find out if the code puts that content into a prompt, or gives it to an agent runtime. The content must have a boundary and a label that mark it as untrusted data.
- If the agent workflow can also write, name the path for data theft in the report. Write operations include a new pull request, a new comment, and an API call.

**Report a new path for untrusted content into an agent that can also write as CRITICAL.**

### Step 11: Output

Give a report with this structure:

```
## QA Check Report

### Risk level: [LOW / MEDIUM / HIGH / CRITICAL]
(name each increase that you applied: no specification, unhealthy files)

### Specification discipline
- Written specification or acceptance criteria found: [yes / no / not applicable — link or path]

### Complexity (Quality Paradox)
- Files touched: N | Decision points changed: N | More than one domain: yes/no
- Rework signals: [files that changed again in 14 days]
- Unhealthy files touched: [large files or high-churn files in the diff]
- Sustainable velocity problem: [yes/no — new code without QA in proportion]

### Test integrity
- [Deleted, skipped, or weak existing tests, and the reason status]
- [New tests that copy the implementation instead of examining behavior]
- [Error branches with no test that enters them]
- [Tests that are not hermetic: file system, network, clock, random values, unordered collections]

### Dependency provenance
- [For each new dependency: existence, age, maintainer, pinning, name proximity]

### Validation gaps (Quality Paradox)
- [Missing tests and coverage gaps; functions that return null instead of an error]
- [Missing boundary checks; error messages that are not specific]

### AI-specific problems (Quality Paradox)
- [Invented APIs, duplicate logic, semantic errors, silent failures]
- [AI slop: too many comments, unnecessary abstraction, dead code]

### Contract compliance
- [Contract, type, or schema differences; API changes with no contract change; modules with no contract]

### Architecture violations
- [Operations that are not idempotent; hidden dependencies; missing adapter boundaries]
- [File navigability — give this as token cost and repeated reads, not as correctness risk]
- [Context file findings: unnecessary overview text, incorrect instructions, auto-generated content]

### Agent-buildability
- [Validation or error handling that is different from the adjacent code; which convention is correct]
- [Code size larger than the task needs]

### Agent surface and secrets
- [Secrets in the code — say that a person must change them]
- [MCP servers, hooks, wider permissions, and changes to skills, agents, or workflows]
- [New paths for untrusted content, and the write channel that goes with them]

### Recommended actions
1. [Specific actions to complete before the merge]
```

**After you give the report**, record that the check ran. This unblocks the push gate in repositories that have a `.qa-check-required` file:

```bash
printf '%s\n%s\n' "$(git rev-parse HEAD)" "$(date +%s)" > "$(git rev-parse --git-dir)/qa-check-ok"
```

### Risk level criteria

- **LOW**: Fewer than 3 files, tests exist, no rework signals, one domain only, and no architecture violations
- **MEDIUM**: 3 to 8 files, or small test gaps, or one rework signal, or small architecture violations such as missing documents or minor navigability problems
- **HIGH**: any one of these conditions:
  - 8 or more files
  - More than one test gap
  - More than one domain, with no integration tests
  - Rework signals in 2 or more files
  - Error branches with no test
  - Two validation conventions in one module
  - A large architecture violation. These are missing contracts at boundaries, operations that are not idempotent, and hidden dependencies.
- **CRITICAL**: any one of these conditions:
  - No tests for new code paths
  - Invented APIs
  - Weak or deleted existing tests, with no reason
  - A new dependency that fails the provenance check
  - A real secret in the diff
  - A new path for untrusted content into an agent that can also write
  - A rework rate above 40%
  - A basic architecture violation. These are no adapter boundaries on external systems, and entangled very large files with no contracts.

Navigability, context file size, and documentation gaps are cost findings. Report them. Do not increase the risk level for these findings alone.

**Rules to increase the level** (apply after the base level): Increase the level by one step if a feature-size diff has no written specification (Step 2). Increase the level by one step if the diff touches unhealthy files (Step 3). Name each increase in the report.

## Important notes

- Be specific. "Needs more tests" does not help. "The new `calculateDiscount()` function at pricing.js:47 has no test for the case where the discount is more than the price" is a usable finding.
- Do not report style problems. This skill is not a linter. Examine defects, rework risk, validation gaps, and architecture violations.
- A newer model does not remove the need for this review. Security pass rates for generated code stayed at approximately 55% across two years of model releases (Veracode, spring 2026).
- This skill is an LLM review, so it is not deterministic. Two runs on the same diff can give different results. This skill is an addition to deterministic gates. It does not replace linters, static analysis, type checks, or coverage diffs (Entelligence 2026).
- Examine the git history for rework patterns. A file with 4 changes in 2 weeks for the same feature is a risk, whatever the current diff shows.
- Architecture violations are quality violations on a longer timeline. A missing contract today causes an incorrect data shape tomorrow. A script that is not idempotent causes corrupt state in the next session.
- Find problems before they become rework. Each defect that you find here saves 18 times the cost of a defect that reaches production (Mennillo 2026, testing ROI).
- Do not report standard framework conventions as hidden behavior. An LLM knows Next.js routing, Rails conventions, and Django ORM patterns from its training data.
- Report adapter boundaries only at real boundaries that can change. Do not recommend a wrapper for a stable utility library.
- Divide cost findings from correctness findings, and say which is which. Clean code makes agents less costly and more efficient. But clean code did not make agents more correct in controlled trials. If you overstate this result, the review loses its authority.
- Do not give rules for the structure of a context file. Size, position, and internal architecture had no measured effect on adherence. The type of content did have an effect. Instructions that an agent cannot infer are worth their cost. Repository overviews are not.
- Change the depth of the review for the type of task. Reported gains are large for simple new work and much smaller for complex legacy code. A diff in a mature subsystem needs more examination for each line, not less. (The frequently quoted figures of 35% to 40% against 10% come from secondary coverage of DORA 2026. The direction is correct. The numbers are unverified.)
- AI is an amplifier, not a correction (DORA 2026). The largest returns come from the quality of the system below the tools: the platform, clear workflows, and team alignment. Findings about repeated structural problems are more important than any one diff.
- Do not use merge results or rejection results as evidence of agent quality. In a study of 9,799 pull requests that people reviewed, only 35.7% of the rejections showed a clear agent failure. Workflow limits caused 31.2%, and 33.1% had no visible reason. Of the merged pull requests, 15.4% needed reviewer feedback or direct commits, and 5.5% showed no interaction at all. A merged agent pull request is not a reviewed pull request.
