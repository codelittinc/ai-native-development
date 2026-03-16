# The AI quality paradox: why you need more QA, not less

AI coding tools make you faster. They also make defects cheaper to create and more expensive to miss. If you don't adjust your QA practices, the productivity gain is illusory -- and the math proves it.

This guide distills findings from A. Mennillo's "The AI Quality Paradox" (March 2026), a paper that formalizes the relationship between AI-assisted development velocity and code quality. The dataset spans 1.6M events across 27 repositories in seven language ecosystems.

---

## The core problem

AI-assisted developers generate code ~55% faster than unassisted developers (GitHub Copilot study, replicated by Peng et al. 2023). But multiple independent sources show the quality is worse:

| Source | Finding |
|--------|---------|
| CodeRabbit (2025) | 1.7x more issues per PR for AI vs. human code |
| Google DORA (2025) | +9% bug rate with 90% AI usage |
| GitClear (2024) | 4x increase in block duplication (5+ lines) |
| Sonar (2025) | Code quality trend hit an inflection point in 2024 |

The common pattern: velocity is measured and rewarded. The rework it generates is not.

---

## The feedback loop

The mechanism is a five-link chain, and each link makes the next one worse:

**Complexity creates defects.** AI generates bigger, more complex commits. A commit touching N independent decision points, each with error probability p, contains at least one defect with probability 1-(1-p)^N. More code = more places to be wrong. This isn't an empirical claim -- it's combinatorics.

**Defects create rework.** Every defect that reaches production needs to be fixed. Without QA gates, observed rework rates hit 45% in the studied enterprise project. The DORA elite benchmark is ~15%.

**Rework saturates the team.** Rework re-enters the work queue. As the rework fraction grows, available bandwidth for new features, testing, documentation, and migration work shrinks toward zero.

**Saturation kills validation.** When the team is buried in rework, code review and testing are the first things cut. Less validation means more defects escape. This closes the feedback loop -- it's now self-reinforcing.

**Debt accumulates across projects.** Each escaped defect persists as technical debt. The paper models this as a geometric series across projects, with a saturation time of ~11 years in the no-QA scenario. For the first time, technical debt can saturate a client relationship within a typical commercial horizon.

---

## The speed limit

The paper derives a maximum sustainable velocity: v_max = η/(4γ), where η is QA effectiveness and γ is the erosion rate. Any generation rate above this threshold places the system in a regime with no stable equilibrium. Quality erosion becomes structurally unavoidable regardless of how good individual developers are.

AI increases γ by roughly 12x compared to human-written code. If η (your QA investment) doesn't scale up proportionally, you cross the threshold.

---

## The numbers that matter

| Scenario | Gross velocity | Rework | Net velocity |
|----------|---------------|--------|-------------|
| Pre-AI, no QA | 1.00x | 50% | 0.50x |
| AI, no QA | 1.55x | 45% | 0.85x |
| Pre-AI, with QA | 1.00x | 15% | 0.85x |
| AI, with QA | 1.55x | 15% | 1.32x |

Read that again: **AI without QA produces the same net velocity as pre-AI with QA.** You're working 55% faster to end up in exactly the same place you were before AI, because you're spending half your time fixing things.

AI with QA is the only configuration that actually accelerates. The tester doesn't slow things down -- they convert 1.55x gross into 1.32x net by keeping rework at 15% instead of letting it climb to 45%.

---

## The false safety zone

This is the scariest finding. Projects near the collapse threshold slow down gradually -- the "critical slowing down" phenomenon from dynamical systems theory.

A system with QA effectiveness just below the critical threshold can take 4-6 years to visibly deteriorate. It passes any 3-year audit. It looks fine on quarterly reviews. But it's already on an irreversible trajectory, and by the time the deterioration is visible, the system is in the post-bottleneck acceleration phase.

Standard monitoring cannot detect this. The paper proposes three early-warning signals from Git-derived time series: rising variance in closure rates, rising lag-1 autocorrelation, and longer recovery times after perturbation spikes.

---

## The ROI of one tester

The paper's most actionable finding: a single dedicated tester (at ~$30K/year cost) eliminates 70% of client-facing defects. The ROI is 18:1.

Even a part-time tester (η moving from 0 to 0.10) triples validation capacity and halves the rework rate. The jump from zero QA to any QA is the largest marginal gain in the entire model.

| η (QA intensity) | Validation capacity | Rework rate | Regime |
|-------------------|-------------------|-------------|--------|
| 0.00 | 0.19 | 45.3% | Collapse |
| 0.10 | 0.59 | 25.6% | Operational |
| 0.20 | 0.75 | 17.6% | Sustainable |
| 0.30 | 0.83 | 13.5% | Wide margin |
| 0.50 | 0.90 | 9.9% | Optimal |

---

## What to do about it

**If you're shipping AI-generated code without dedicated testing, stop and fix that first.** Everything else is secondary to getting η above zero.

Practically:

1. **Add a tester.** Doesn't have to be full-time. Doesn't have to be expensive. But someone whose job is to find defects in new AI-generated features, not just review legacy code patterns. The existing code review process was probably designed pre-AI and is tuned to catch different things.

2. **Track rework rate.** Measure the fraction of files that are re-touched within 14 days of apparent completion. If it's above 25%, you're in the danger zone. If it's above 40%, you're in the collapse regime and accumulating debt faster than you're building.

3. **Watch for the early-warning signals.** If your monthly closure rate variance is increasing, if recovery from production incidents is taking longer each quarter, or if the same files keep getting re-opened -- these are pre-collapse indicators.

4. **Don't confuse velocity with throughput.** PRs merged per week is not the same as working features delivered. If you're measuring the first and ignoring the second, you're optimizing for the wrong thing.

5. **Align your QA to AI output.** Most QA processes were designed before AI tools. Code reviewers are looking for architectural consistency and legacy pattern compliance, not the kinds of defects AI introduces (subtle semantic errors, hallucinated APIs, duplicated logic). Retune your filters.

6. **Accept the speed limit.** There is a maximum generation rate your team can sustain. Pushing past it doesn't make you faster -- it makes you slower, with a delay that makes the cause invisible.

---

## Source

A. Mennillo, "The AI Quality Paradox: How Code Complexity Drives Rework in AI-Assisted Development," v5.7, March 2026. Evidence from 1,594,764 events across 27 repositories, seven language ecosystems. Theoretical model with empirical validation on enterprise (DMS-E) and open-source (ApacheJIT) datasets.
