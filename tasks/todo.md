# qa-check v3.0 — Improvement Plan (proposed 2026-07-02, implemented same day)

Based on: repo audit + research sweep of Feb–Jul 2026 AI code-quality literature + Claude Code platform changes since the March 31 marketplace restructure.

**Verdict on current skill:** The core thesis (validation capacity is the binding constraint) held up — Farrag (arXiv:2605.01160), DORA 2026, and Faros telemetry all independently corroborate it. The SKILL.md format has no breaking changes. But two new first-class risks emerged since Feb, several citations need recalibration, and the repo has distribution bugs.

---

## Phase 1 — Repo hygiene (small, do first)

- [x] Fix README install command: two-step flow (`claude plugin marketplace add codelittinc/ai-native-development`, then `claude plugin install qa-check@ai-native-development`).
- [x] Kill the hand-duplicated skill copies — top-level `skills/` deleted; `plugins/<name>/skills/<name>/` is the single source; README copy-path updated.
- [x] supply-chain-check: fabricated IOC table removed (axios 1.14.1 / plain-crypto-js). Replaced with live-advisory queries (npm audit, OSV.dev, GitHub Advisory DB) + a historical-incidents table (real incidents only) in `references/incidents.md`, explicitly labeled not-current-IOCs, with a rule to never report compromises from memory.
- [x] guides/claude-code-workflows.md: context-mode slug corrected to `mksglu/context-mode` (verified against the installed marketplace's git remote); UI-dependent references reworded.
- [x] Per-plugin `.claude-plugin/plugin.json` added for both plugins.

## Phase 2 — qa-check v3.0 content

- [x] **Test integrity / weakened tests check** (Step 5): deleted/skipped/loosened assertions, widened tolerances, tests mirroring implementation. Unjustified weakening → CRITICAL. (SpecBench arXiv:2605.21384; Verification Horizon arXiv:2606.26300.)
- [x] **Dependency provenance / slopsquatting check** (Step 6): existence, age >6 months, maintainer plausibility, lockfile pinning, name proximity — with concrete `npm view` / PyPI API commands. Fails provenance → CRITICAL. (CSA note 2026-04-19.)
- [x] **Spec-existence check** (Step 2): feature-sized diff with no written spec → escalate one level. (Farrag arXiv:2605.01160; GitHub Spec Kit.)
- [x] **Smell weighting** (Step 7): comment pollution, speculative over-abstraction, dead code accumulation as named checks. (Liu et al. arXiv:2603.28592 — 89.3% smells, 22.7% survive.)
- [x] **Unhealthy-file risk multiplier** (Step 3): large/high-churn files escalate one level. (CodeScene AI-Ready Code v2.)
- [x] Rework terminology aligned with DORA's fifth metric.
- [x] Corroborating citations added; full evidence base in `references/research.md`.
- [x] "Model upgrades don't reduce the need" note (Veracode flat ~55%).
- [x] LLM-review non-determinism note — pair with deterministic gates (Entelligence 2026).
- [x] METR -19% not cited; references carry the Feb 2026 revision (-4%, CI -15%..+9%).
- [x] SKILL.md restructured: 243-line body + `references/research.md`.
- [x] Description repositioned as complement to built-in `/code-review`.
- [x] qa-check bumped to 3.0.0 (marketplace.json + plugin.json + frontmatter, verified matching).

## Phase 3 — Enforcement

- [x] CI recipe documented in guides/claude-code-workflows.md: `anthropics/claude-code-action@v1` (prompt + claude_args), fetch-depth 0, API-credit billing note, pilot-one-repo recommendation.
- [ ] Actually enable the GitHub Action on one active repo as pilot (pick repo — Cody's call).
- [ ] Optional: Stop-hook or pre-push hook reminding to run qa-check before PR.

## Review (2026-07-02)

Implemented via an orchestrated workflow: 5 work items, each a builder→checker loop (adversarial checker, max 3 iterations). All 5 passed — 4 on the first iteration, supply-chain-check on the second. 12 agents total, zero errors.

Independent verification (by the orchestrating session, on top of the checkers):
- Mechanical: version triples match (marketplace = plugin.json = frontmatter: qa-check 3.0.0, supply-chain-check 1.1.0, marketplace metadata 1.1.0); both SKILL.md bodies ≤250 lines (243 each); no stale references to deleted `skills/` paths; all required new content present.
- Anti-fabrication audit: every package in `references/incidents.md` and every arXiv ID in `references/research.md` verified against the approved source list in the implementation spec. Clean.
- Manual review of the full qa-check v3.0 SKILL.md — signed off.
- Diffstat: 7 files changed, 245 insertions, 602 deletions, plus 4 new files (2 plugin.json, 2 references docs).
