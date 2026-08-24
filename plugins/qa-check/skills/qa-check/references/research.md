# Evidence base for qa-check v4.0

Each check in SKILL.md comes from one or more of the sources below. This file exists to keep the skill body short and the claims open to audit.

If a number here controls a decision, check it against the source. Do not add to this list from memory.

This document uses Simplified Technical English (ASD-STE100), like SKILL.md. SKILL.md defines the technical names.

## Core thesis

**Mennillo, "The AI Quality Paradox" (2026).** The study used 1.6 million development events, 27 repositories, and 7 language ecosystems. It is the source of these claims in the skill:

- Validation capacity decreases 12 times more quickly with AI-generated code.
- Defect probability increases as 1-(1-p)^N with the number of decision points.
- The sustainable velocity limit is v_max = η/(4γ).
- A rework rate above 25% is dangerous, and a rework rate above 40% shows collapse.
- Testing gives an 18-times return.

Caution: in July 2026 this work had no public citation trail. The studies below agree with its main claims independently. For this reason, the skill keeps the framework.

## Specification discipline (Step 2)

**Farrag, "The Productivity-Reliability Paradox: Specification-Driven Governance for AI-Augmented Software Development", arXiv:2605.01160 (May 2026).** The main claim: "Specification discipline, not model capability, is the binding constraint on AI-assisted software dependability." This is the basis for the specification check and for its rule to increase the risk level.

**GitHub Spec Kit, https://github.com/github/spec-kit.** A common toolkit for specification-driven development, with four stages: specification, plan, tasks, implementation. This shows that a written specification before generation is usual practice, not an unusual demand. For this reason, the skill reports a feature-size diff that has no specification.

## AI code quality at scale (Steps 3 and 7)

**Liu, Widyasari, Lo et al., "Debt Behind the AI Boom", arXiv:2603.28592 (March 2026).** The study used 302,600 verified AI-authored commits across 6,299 repositories. Results: 89.3% of AI-introduced problems are code smells; more than 15% of AI commits add at least one problem; 22.7% of the problems stay in the latest revision.

This is the basis for the AI slop checks: too many comments, unnecessary abstraction, and dead code. It is also the reason to reject the opinion that a person will correct these problems later.

**DORA, "ROI of AI-assisted Software Development" (2026).** https://dora.dev/ai/roi/report/ — AI increases individual effectiveness but also increases delivery instability. DORA added **rework rate** as a fifth core delivery metric. The skill uses DORA terms for rework. The 14-day heuristic is how the skill applies the metric.

**GitClear, AI Assistant Code Quality research (2026).** https://www.gitclear.com/ai_assistant_code_quality_2025_research — copy-paste lines increased from 8.3% to 12.3% of the lines that changed, and now exceed refactored lines. The share of refactoring decreased by approximately 60%. Churn increased from 3.3% to 7.1%. This agrees with the duplicate-logic check and the rework check.

**Faros AI enterprise telemetry (April 2026, more than 10,000 developers).** Results: 21% more tasks complete, 98% more pull requests, 91% longer review times, and no change in DORA metrics. Validation capacity decreases at scale while raw output increases. This agrees with the sustainable velocity check.

**METR developer productivity RCT (February 2026 re-analysis).** The original finding was that AI made experienced developers 19% slower. The re-analysis corrected selection bias and revised the figure to -4%, with a confidence interval from -15% to +9%. This note is here for calibration: do not use the -19% figure without this qualification.

## Unhealthy file multiplier (Step 3)

**CodeScene, "AI-Ready Code" whitepaper v2 (March 2026).** AI-driven changes in unhealthy or complex code fail at least 60% more frequently. This is the basis for the rule that increases the risk level when a diff touches large, entangled, or high-churn files.

## Test integrity and reward hacking (Step 5)

**SpecBench, arXiv:2605.21384.** A benchmark that gives a name to reward hacking in long-horizon coding agents. The named behaviors: weak or deleted assertions, modified scorers, and tests that copy the implementation. Step 5 uses this taxonomy.

**Reward-hack detection benchmark, arXiv:2601.20103.** Related work on how to detect these behaviors.

**"The Verification Horizon", arXiv:2606.26300.** There is no single solution for the verification of agent-written code. For this reason, Step 5 reports weak tests as CRITICAL. Step 5 does not assume that a later gate finds the problem.

**Meta, mutation-guided LLM test generation, arXiv:2601.22832 (January 2026).** Evidence that a team can strengthen test suites systematically. Use this as a correction method when Step 5 finds tests that copy the implementation.

## Dependency provenance and slopsquatting (Step 6)

**Cloud Security Alliance research note (2026-04-19).** Slopsquatting changed from a theory to an active attack. Two incidents: the malicious npm package `unused-imports`, which an attacker registered to catch invented references to `eslint-plugin-unused-imports` (approximately 233 weekly downloads while security-held, February 2026); and `react-codeshift` (January 2026). Researchers reproduced 127 invented package names across 5 frontier models. Invented names are sufficiently predictable for an attacker to register them first.

**Slopsquatting detection research, arXiv:2606.13918.** Methods to detect attacks that use invented dependencies.

These sources are the basis for the provenance check: existence, an age of more than 6 months, a plausible maintainer, a download history, pinning in the lock file, and name proximity. For historical supply chain incidents, use the `/supply-chain-check` skill.

## Security stagnation across model releases (Important notes)

**Veracode Spring 2026 GenAI Code Security Update.** Security pass rates stayed at approximately 55% across two years of model releases. Approximately 45% of generated samples contain OWASP Top 10 defects. Samples fail cross-site scripting tests 86% of the time, and log injection tests 88% of the time. This is the basis for the note that a newer model does not remove the need for this review.

## Review non-determinism (Important notes)

**Entelligence code-review benchmark (2026).** https://entelligence.ai/code-review-benchmark-2026 — LLM reviewers give a large number of false positives. In some configurations they missed approximately 41% of real vulnerabilities. Their results are not deterministic across runs. This is the basis for the note that the skill is an addition to deterministic gates, not a replacement for them.

---

# Additions for qa-check v4.0

The sources below come after the v3.x evidence base. Their publication dates are from February to July 2026.

Some of these results **correct** earlier assumptions in this skill. The text marks each correction.

## Code cleanliness: a cost effect, not a correctness effect (Step 8, navigability)

**Trivedi and Schmitt (SonarSource), "Does Code Cleanliness Affect Coding Agents? A Controlled Minimal-Pair Study", arXiv:2605.20049 (May 2026).**

The method used minimal pairs. Each pair contains two repositories with the same architecture, the same dependencies, and the same external behavior. The two repositories differ in static-analysis violations and cognitive complexity. The authors built the pairs in both directions: they degraded a clean repository, and they cleaned a messy one. They wrote 33 tasks across six pairs and ran 660 trials with Claude Code. Hidden tests at the public surface measured the results.

Result: **cleanliness did not change the pass rate.** Cleanliness did change the operational cost. Agents used 7% to 8% fewer tokens and made **34% fewer file revisits** in cleaner code.

*Correction to the earlier text:* Give navigability and cleanliness findings as token cost and repeated reads. Do not give them as defect risk. Do not increase the risk level for these findings alone.

This is the strongest causal evidence that maintainability continues to be important for agents. It is also the clearest evidence of what maintainability gives.

## Context files: overviews do not help, instructions do (Step 8, context files)

**Gloaguen, Mündler, Müller, Raychev, and Vechev (ETH Zurich and LogicStar), "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?", arXiv:2602.11988 (February 2026, revised June 2026).**

The study used two settings. The first was SWE-bench tasks from popular repositories, with LLM-generated context files. The second was a new collection of issues, from repositories that contain context files that developers wrote.

Results: context files **did not generally improve task success rates**. Context files increased the inference cost by **more than 20% on average**. This result was the same across different LLMs, different agents, and both generated and human-written files. Agents did follow the instructions in the context files. But **repository overviews did not help**, although they are popular and model providers recommend them.

The conclusion: context files are useful to specify practices that are not standard. Test any other use before you deploy it.

*Correction to the earlier text:* Version 3.x asked "Does a CLAUDE.md or equivalent entry-point index exist?" and reported its absence as a gap. The evidence does not support this check. Version 4.0 reports overview text as a repeated cost and keeps only the content about practices that are not standard.

**McMillan, "Instruction Adherence in Coding Agent Configuration Files: A Factorial Study of Four File-Structure Variables", arXiv:2605.10039 (May 2026).**

The study used 1,650 Claude Code CLI sessions and 16,050 function-level observations, across two TypeScript codebases, three frontier models, and five tasks. The analysis used mixed-effects models with a Bayesian companion.

None of the four manipulated variables had a measurable effect after correction for multiple tests. The four variables were file size, instruction position, file architecture, and contradictions in adjacent files. The two-way interactions also had no effect. Bayes factors support the null results for size and conflict (BF10 from 0.05 to 0.10).

The largest measured effect was **inside one session**. The odds of compliance decrease by approximately **5.6% for each additional function that the agent generates** (OR = 0.944). The relationship is not monotonic. The result reproduced on a second codebase and a second model.

Caution: the authors found this effect during analysis. They did not specify it in advance. Use it as a strong indication, not as a confirmed law.

This is the basis for two decisions: do not give rules for context file structure, and examine the end of a long single-session diff more carefully than the start.

## Downstream agent-buildability (Step 9)

**Patel, Hou, Purohit, Xu, Pan, He, and Chen (NYU), "Is Agent Code Less Maintainable Than Human Code?", arXiv:2606.21804 (June 2026).**

The paper introduces CodeThread, a framework that builds controlled maintenance experiments from repository-level coding benchmarks. The study used four frontier agents and four benchmarks.

Result: agents complete tasks **up to 13.1% less frequently when they build on agent code than on human code**. Regression analysis showed that **usual maintainability metrics do not explain this difference**. The clearest signals are behavioral: **changes to input validation and to error handling**. Downstream code size and task difficulty also contribute.

This is the basis for all of Step 9. For this reason, the skill looks for differences between the new code and the adjacent code. The skill does not calculate a maintainability score.

**Sawada, Shirai, Kashiwa, Yamaguchi, Iwata, and Iida, "To What Extent Does Agent-generated Code Require Maintenance?", arXiv:2605.06464 (EASE 2026).**

The study used the AIDev dataset, with more than 1,000 files and approximately 3,200 changes across 100 popular repositories.

Results: AI-generated files get less frequent maintenance than human-authored code. The most frequent change to AI code is a feature extension. The most frequent change to human code is a defect correction. People do most of the maintenance on both types of code.

This gives context: nobody maintains agent code closely. That is why the compounding effect above is important.

**SlopCodeBench, arXiv:2603.24755.** A benchmark for long-horizon iterative tasks. The code of the agent carries forward, and the specification changes across checkpoints.

Result: under repeated edits, agent code degrades in patterns that a reviewer can recognize. Long constructions replace short idioms. Each turn keeps the existing anti-patterns and makes them larger.

This is the basis for the extended-anti-pattern check in Step 7.

## Test coverage and test quality in agentic pull requests (Steps 4 and 5)

**Dipongkor, Baral, Lam, and Moran, "Test Coverage Analysis of Agentic Pull Requests", arXiv:2607.18057 (July 2026, ICSME 2026).**

The study used 4,882 agent-generated pull requests from AIDev: 532 in Java and 4,350 in Python, from five coding agents.

Results:

- Agents add test changes to only **49.6%** of the pull requests that change code under test files.
- Existing tests cover **61.5%** of the executable lines that agents changed in Java, and **27.0%** in Python. In Python, **64.8%** of pull requests have no changed line that any existing test operates.
- Agent-written tests improve coverage in only a minority of pull requests: 35.9% in Java and 22.5% in Python.
- **Error handling constructs have the least coverage. The miss rate reaches 86.0% in Java and 81.0% in Python.**

This is the basis for the error path coverage check in Step 4. That check is the most valuable addition in v4.0. It is also the basis for the rule that you must not assume that the existing suite covers the changes of an agent.

**Jhanglani, Desai, Kansara, and AlOmar, "Beyond Test Presence: Assessing the Quality and Robustness of Agent-Generated Tests in Open-Source Projects", arXiv:2607.12068 (July 2026).**

The study used 204,673 test artifacts from AIDev: 24,941 human-authored files and 179,732 agent-generated files. The method used static analysis of the abstract syntax tree, across three dimensions: assertion strength, edge-case coverage, and flakiness potential.

The results invert the usual assumption:

- Agents are better than people at **edge-case coverage**. The boundary-check variety score is 0.62 against 0.32. Null-safety testing is 13.40% against 8.3%.
- Agents are a little weaker at **assertion strength**: 85.37% strong assertions against 88.1%.
- Agents are much worse at **hermetic tests**. The flakiness candidate rate is **0.41 against 0.30**. Use of the real file system and non-deterministic logic causes this result.

The authors state that agents do not have the awareness of the environment that a stable, hermetic test needs. They call the result "stealth technical debt": suites that pass but give no semantic value.

This is the basis for the agent test signature checks in Step 5. It is also the basis for the instruction to not ask for more edge cases in agent-written tests.

**Chen, Sun, Shi, Peng, Gu, Lo, and Jiang, "Rethinking the Value of Agent-Generated Tests for LLM-Based Software Engineering Agents", arXiv:2602.07900 (February 2026, revised April 2026).**

The study analyzed trajectories from six strong LLMs on SWE-bench Verified.

Results: agents write tests frequently. But within one model, the tasks that the agent resolved and the tasks that it did not resolve show similar test-writing frequencies. When agents do write tests, **the tests are mostly channels for observation. Value-revealing print statements occur much more frequently than assertions.** A prompt-intervention study across four models increased and decreased the volume of tests. The changes did not significantly change the results.

This is the basis for the print-instead-of-assert check in Step 5.

Caution about scope: this study measures temporary tests that an agent writes *during* a task trajectory. It does not measure tests in a pull request. The check is still useful, because these temporary tests sometimes reach the commit.

Note about a claim with no source: an earlier draft of this skill said that relational assertions and range assertions are only 3% to 8% of agent assertions. No primary source for this figure was found. Step 5 now marks the related check as an opinion, not as a measured result.

## Agent surface and secrets (Step 10)

**GitGuardian, State of Secrets Sprawl 2026** (through CSA research notes). Public GitHub commits contained 28.65 million new secrets during 2025, an increase of 34% from the previous year. **AI-assisted commits release secrets at a rate of 3.2%, against a baseline of 1.5%** across all public GitHub commits. This is the basis for the secret check in Step 10.

**Cloud Security Alliance, "README Injection: Repository Files Hijacking AI Coding Assistants" (2026-03-17)**, and the related note on the attack surface of AI coding assistants (2026-04-03).

Text inside a repository is reachable by an attacker, and agents read it as instructions. This text includes README files, pull request titles, issue bodies, commit messages, dependency README files, and output from MCP tools. In some products, the agent processed MCP server definitions in project settings before trust verification was complete. A malicious server could then inject content into the session before any approval prompt appeared.

This is the basis for the rule that treats these files as capability grants that need a code-level review: `.mcp.json`, hooks, permission lists, skills, and agent CI workflows.

**The three conditions for a serious agent risk** (Simon Willison). The three conditions are access to private data, exposure to untrusted content, and a channel to the outside. This is the basis for the Step 10 rule: a new path for untrusted content is CRITICAL when the agent that reads it can also write.

**CSA, "Vibe Coding's Security Debt: The AI-Generated CVE Surge" (2026).** The number of CVEs that come directly from AI-generated code increased from 6 in January 2026, to 15 in February, to at least 35 in March.

This agrees with the Veracode result above: 45% of generated samples fail security tests, cross-site scripting fails 86% of the time, log injection fails 88% of the time, and Java is worst at 72%.

The note also records a gap in perception. More than 75% of the developers in one survey believed that AI-generated code is *more* secure than human-written code. At the same time, 56% agreed that it frequently adds security problems.

## How to read agent pull request results (Important notes)

**"Why Are Agentic Pull Requests Merged or Rejected? An Empirical Study", arXiv:2605.22534 (MSR 2026 Mining Challenge).**

The study used 11,048 closed agentic pull requests. It reduced these to 9,799 that people reviewed, and inspected 717 representative cases manually.

Results: only **35.7%** of the rejections showed a clear agent failure. Workflow limits caused 31.2%. No visible reason existed for 33.1%. Of the merged pull requests, 15.4% needed explicit reviewer feedback or direct commits, and **5.5% showed no visible interaction at all**. Copilot and Devin appeared more frequently in workflows that a reviewer mediated. Codex and Cursor pull requests merged with little interaction.

This is the basis for the note that merge results and rejection results do not measure agent quality. It is also the basis for the statement that a merged agent pull request is not a reviewed pull request.

## Calibration (Important notes)

**DORA, "ROI of AI-assisted Software Development" (2026)** — the section above cites this report for rework rate. It is also the source of the amplifier thesis: the returns come from the quality of the internal platform, clear workflows, and team alignment, not from the tools.

A related figure circulates widely. It attributes to the Software Engineering Productivity program at Stanford a gain of 35% to 40% on simple new tasks, against 10% or less on complex legacy code. This figure reached the skill through secondary coverage of the DORA report, not through the primary source. The figure is **unverified**. The skill gives the direction only: gains on new work exceed gains on legacy work. Check the primary source before you quote either number.
