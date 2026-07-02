# Evidence base for qa-check v3.0

Every check in SKILL.md traces back to one or more of the sources below. This file exists so the skill body stays short and the claims stay auditable. If a number here matters to a decision, verify it against the linked source — do not extend this list from memory.

## Core thesis

**Mennillo, "The AI Quality Paradox" (2026).** 1.6M development events across 27 repositories and 7 language ecosystems. Origin of the skill's core claims: validation capacity erodes 12x faster with AI-generated code, defect probability scales as 1-(1-p)^N with decision points, sustainable velocity ceiling v_max = η/(4γ), rework rate thresholds (25% danger zone, 40% collapse regime), and the 18x testing ROI figure. Caveat: as of July 2026 this work has no public citation trail; the studies below corroborate its central claims independently, which is why the skill keeps the framework.

## Specification discipline (Step 2)

**Farrag, "The Productivity-Reliability Paradox: Specification-Driven Governance for AI-Augmented Software Development", arXiv:2605.01160 (May 2026).** Key claim: "Specification discipline, not model capability, is the binding constraint on AI-assisted software dependability." Basis for the spec-existence check and its escalation rule.

**GitHub Spec Kit, https://github.com/github/spec-kit.** Mainstream spec-driven development toolkit (Spec → Plan → Tasks → Implement). Evidence that written-spec-before-generation is standard practice, not an exotic demand — which is why its absence on a feature-sized diff is flaggable.

## AI code quality at scale (Steps 3 and 7)

**Liu, Widyasari, Lo et al., "Debt Behind the AI Boom", arXiv:2603.28592 (Mar 2026).** 302.6k verified AI-authored commits across 6,299 repositories. 89.3% of AI-introduced issues are code smells; more than 15% of AI commits introduce at least one issue; 22.7% of introduced issues survive to the latest revision. Basis for the AI slop checks (comment pollution, speculative over-abstraction, dead code) and for treating "someone will clean this up later" as false by default.

**DORA, "ROI of AI-assisted Software Development" (2026).** https://dora.dev/ai/roi/report/ — AI raises individual effectiveness but increases delivery instability. DORA added **Rework Rate** as a fifth core delivery metric. Basis for aligning the skill's rework terminology with DORA; the 14-day re-touch heuristic is the skill's operationalization of it.

**GitClear, AI Assistant Code Quality research (2026).** https://www.gitclear.com/ai_assistant_code_quality_2025_research — copy-paste lines rose from 8.3% to 12.3% of changed lines, now exceeding refactored lines; refactoring share down roughly 60%; churn up from 3.3% to 7.1%. Corroborates the duplicated-logic and rework checks.

**Faros AI enterprise telemetry (Apr 2026, 10k+ developers).** 21% more tasks completed, 98% more PRs, 91% longer review times, flat DORA metrics — validation capacity erodes at scale even as raw output climbs. Corroborates the sustainable-velocity check.

**METR developer-productivity RCT (Feb 2026 re-analysis).** The widely quoted original finding that AI slowed experienced developers by 19% was revised to -4% (CI -15% to +9%) after correcting selection bias. Cited here as a calibration note: do not use the -19% figure unqualified.

## Unhealthy-file multiplier (Step 3)

**CodeScene, "AI-Ready Code" whitepaper v2 (Mar 2026).** AI-driven changes landing in unhealthy or complex code fail at least 60% more often. Basis for the rule that a diff touching large, entangled, or high-churn files raises the risk level one notch.

## Test integrity and reward hacking (Step 5)

**SpecBench, arXiv:2605.21384.** Benchmark formalizing reward hacking in long-horizon coding agents: weakening or deleting assertions, monkey-patching scorers, writing tests that mirror the implementation. The named behaviors in Step 5 come directly from this taxonomy.

**Reward-hack detection benchmark, arXiv:2601.20103.** Companion work on detecting these behaviors.

**"The Verification Horizon", arXiv:2606.26300.** No silver bullet for verification of agent-written code — which is why Step 5 treats unjustified test weakening as CRITICAL rather than assuming downstream gates will catch it.

**Meta, mutation-guided LLM test generation, arXiv:2601.22832 (Jan 2026).** Evidence that test suites can be strengthened systematically; useful as a remediation pointer when Step 5 finds tests that mirror the implementation.

## Dependency provenance and slopsquatting (Step 6)

**Cloud Security Alliance research note (2026-04-19).** Slopsquatting moved from theoretical to actively exploited. Live incidents: malicious npm package `unused-imports` (registered to catch hallucinations of `eslint-plugin-unused-imports`; roughly 233 weekly downloads while security-held, Feb 2026) and `react-codeshift` (Jan 2026). 127 hallucinated package names were reproduced across 5 frontier models — hallucinated names are predictable enough for attackers to pre-register.

**Slopsquatting detection research, arXiv:2606.13918.** Detection approaches for hallucinated-dependency attacks.

These are the basis for the inline provenance check: existence, age >6 months, maintainer plausibility, download history, lockfile pinning, and name proximity. For historical supply-chain incident patterns, see the `/supply-chain-check` skill.

## Security stagnation across model releases (Important notes)

**Veracode Spring 2026 GenAI Code Security Update.** Security pass rates flat (~55%) across two years of model releases; roughly 45% of generated samples introduce OWASP Top 10 flaws; XSS fails 86% of the time, log injection 88%. Basis for the note that model upgrades do not reduce the need for this review.

## Review non-determinism (Important notes)

**Entelligence code-review benchmark (2026).** https://entelligence.ai/code-review-benchmark-2026 — LLM reviewers show meaningful false-positive rates, missed roughly 41% of real vulnerabilities in some setups, and are non-deterministic across runs. Basis for the note that qa-check complements, never replaces, deterministic gates (linters, static analysis, type checks, coverage diffs).
