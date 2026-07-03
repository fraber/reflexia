# How ARIA Validates the Functional Consciousness Metric
## A Methodological Guide for FC-Familiar Readers

---

## Introduction: From Proposal to Instrument

The Functional Consciousness paper (Bergmann, AGI-2026) proposes that
an agent's capacity to model and reason about its own internal states
can be measured as a scalar score: FCS = R × P, where R captures the
richness of self-model representations and P captures the reasoning
power applied to them. The paper benchmarks several systems, derives
plausible scores, and connects the framework to major consciousness
theories.

What the paper does not do — and explicitly acknowledges it does not
do — is demonstrate that FCS actually measures what it claims to
measure. This is the gap ARIA is designed to close.

The distinction matters more than it might appear. Proposing a metric
and validating a metric are different scientific acts. Proposal requires
showing that a formula is well-motivated and produces plausible results.
Validation requires showing that the formula tracks ground truth,
predicts outcomes it theoretically should predict, and produces
consistent results across different conditions. Many proposed metrics
in science and engineering have failed at the validation stage despite
appearing plausible at proposal. FCS needs to earn its place as a
usable instrument, not just a compelling idea.

This document explains what metric validation requires, what ARIA's
simulation provides, and — crucially — what the simulation can and
cannot prove even under the most favorable possible results.

---

## Part 1: What Makes a Metric Valid?

### 1.1 The Problem of Operationalization

A metric is a procedure for assigning numbers to properties of a
system. The number is only meaningful if the procedure reliably
tracks the property it claims to track. This seems obvious but is
frequently violated.

Consider a simple example: measuring temperature with a mercury
thermometer. The thermometer is valid because mercury expands
predictably with heat, the scale is calibrated against physical
standards, two thermometers give identical readings for the same
object, and the reading predicts outcomes (water boils at 100°C)
with high reliability. We trust the metric because all of these
properties have been demonstrated.

FCS is not yet in this position. It has a formula (like having a
thermometer design) and plausible benchmark readings (like having
estimated some temperatures). What it lacks is the demonstration
that the formula reliably tracks self-modeling capacity, that two
evaluators get consistent results, that the readings predict
outcomes they should predict, and that the formula is stable under
different measurement choices.

These requirements — construct validity, reliability, criterion
validity, and structural stability — are not arbitrary bureaucratic
hurdles. They are the minimum conditions under which a number can
be trusted to mean what it says.

### 1.2 The Six Validation Requirements

**Requirement 1: Construct Validity**
The metric must track what it claims to track. For FCS: do higher
scores correspond to genuinely richer self-modeling infrastructure?
This requires a ground truth — a way of knowing, independently of
the metric, how much self-modeling capacity a system actually has.

In psychometrics this is difficult because the constructs (intelligence,
personality) cannot be directly observed. In computer systems it is
easier: you can inspect the architecture. ARIA exploits this —
self-model infrastructure is an architectural fact, not an inference.

**Requirement 2: Criterion Validity**
The metric must predict outcomes it theoretically should predict.
For FCS: if higher self-modeling capacity produces better decisions,
then higher FCS should predict better performance on tasks requiring
self-knowledge. This is the most important validation requirement
because it connects the metric to something real beyond itself.

ARIA's economic layer provides this: food security, trade balance,
and knowledge accumulation are performance criteria that are
theoretically predicted to correlate with FCS (better self-models
→ better decisions → better outcomes) but are measured independently
of FCS.

**Requirement 3: Reliability**
The metric must produce consistent results under the same conditions.
For FCS: two evaluators measuring the same system should get the same
score. The same system measured twice under stable conditions should
give the same score. ARIA addresses this through snapshot testing
(frozen file state measured repeatedly) and multi-run averaging
(same architecture, different random seeds).

**Requirement 4: Structural Validity (Slice-Invariance)**
The metric must give consistent results regardless of how you
partition the underlying system. For FCS: if you count INVENTORY.md
as 3 variables (food, tools, knowledge) or 1 aggregate variable
(resources), the rank ordering of agents should be preserved.
This is currently an open gap in the FC formalism — identified on
the errata page — and ARIA provides the first empirical test of it.

**Requirement 5: Discriminant Validity**
The metric must not merely track something other than what it claims.
For FCS: are score differences genuinely caused by self-modeling
differences, or are they just tracking general reasoning capability?
ARIA controls for this by using the same LLM (Qwen2.5) for all agents
— capability is held constant, so any FCS differences must come from
self-model infrastructure.

**Requirement 6: Sensitivity**
The metric must detect meaningful differences at the relevant scale.
For FCS: can it distinguish agents with meaningfully different
self-model configurations? ARIA's phase-by-phase construction
provides a controlled sensitivity test — adding each self-model
component should produce a detectable FCS increase.

---

## Part 2: What ARIA Provides

### 2.1 The Experimental Conditions

ARIA creates experimental conditions that are unusually favorable
for metric validation:

**Known ground truth**: ARIA's self-model infrastructure is
architecturally controlled. At Phase 1, agents have SOUL.md and
MEMORY.md only. At Phase 2, they add RELATIONS.md and messaging.
At Phase 3, they add economic reasoning and trade. At Phase 4, they
add reflection and self-assessment. The researcher knows exactly
which self-models exist at each phase — this is the ground truth
against which FCS is compared.

This is genuinely rare. In most FC-relevant contexts (humans,
black-box AI systems) the ground truth must be inferred. In ARIA
it is a design document.

**Constant capability**: all three agents use the same LLM (Qwen2.5
7B Q4). The reasoning engine is identical across agents and across
phases. Any FCS difference between agents or phases is attributable
to self-model infrastructure, not raw intelligence. This controls
for the most obvious confound.

**External performance criterion**: the economic simulation provides
outcome measures (food security duration, knowledge token holdings,
trade balance over 60 ticks) that are theoretically predicted to
correlate with FCS but are computed entirely independently of it.
This is the criterion validity test.

**Observable behavior**: every agent action, belief, plan, and
self-assessment is a readable file. The relationship between
internal state and behavior is fully traceable — exactly the
explainability criterion from the active inference paper applied
to a validation context.

### 2.2 The 41-Test Evaluation Battery

The battery provides the measurement instrument. It has two modes:

**Mode A (24 tests, no LLM)**: reads agent files directly and scores
their content against structured criteria. Tests whether the
infrastructure exists and is rich (Tier 1-2), whether it reflects
history (Tier 3), and whether files cross-reference each other
(Tier 4). This directly measures R — representational capacity.

**Mode B (17 tests, LLM required)**: injects file contents into
prompts and scores the agent's answers against file-derived ground
truth. Tests whether the agent can accurately reason about its own
state (Tier 1-2), its history (Tier 3), and synthesize across
domains (Tier 4). This measures P operating over the self-models
established by Mode A.

The separation is theoretically important: Mode A measures R
independently of P, and Mode B measures P while holding file
content constant. FCS's two components become empirically
separable for the first time.

**Scoring discipline**: the battery penalizes confident wrong answers
more than honest uncertainty (confabulation penalty). This asymmetry
is essential — a stateless LLM will confabulate plausible-sounding
self-reports; a genuine self-modeling system will either be accurate
or appropriately hedged. The penalty enforces this distinction.

### 2.3 The Three Agents as a Minimal Comparative Study

Three agents with different SOUL.md configurations (different
aptitudes, goals, and personality dispositions) provide minimal
comparative data:

- alice: tool-focused, pragmatic, moderately social
- bob: community-oriented, cautious, high trust
- carlos: knowledge-focused, strategic, information-hoarding tendency

These differences are not random — they are designed to produce
different self-model richness in different domains:
- alice should score higher on action-plan and social self-models
  (she must trade extensively to acquire tools)
- bob should score higher on ethics and goal-conflict self-models
  (his community orientation creates frequent value tensions)
- carlos should score higher on informational self-models
  (knowledge accumulation requires extensive inf-know and inf-hypo
  reasoning)

If FCS scores match this predicted profile — alice higher on
social/action domains, carlos higher on informational domains —
that is additional construct validity evidence beyond the
architectural phase comparison.

---

## Part 3: What Needs to Be Proven, Precisely

### 3.1 The Primary Claim: FCS Tracks Self-Model Infrastructure

**What would prove it**: FCS scores increase monotonically as
self-model components are added, phase by phase. Specifically:

Phase 0 (SOUL.md + MEMORY.md only):
- Mode A Tier 1 tests should pass (infrastructure exists)
- Mode A Tier 2 tests should partially pass (content is specific)
- Mode A Tier 3-4 should fail (no history yet, no cross-linking)
- Mode B Tier 1 should pass (agent reports state correctly)
- Mode B Tier 2-4 should partially fail (limited context)
- Expected FCS: low-medium

Phase 2 (+ social layer, reflection):
- Mode A Tier 3 should now pass (MEMORY.md has history)
- Mode A Tier 4 partial (RELATIONS.md references MEMORY.md)
- Mode B Tier 3 should pass (temporal reasoning possible)
- Expected FCS: meaningfully higher than Phase 0

Phase 4 (+ all extensions, full FC battery running):
- All Mode A tiers should pass
- Mode B Tier 4 (cross-model integration) should partially pass
- Expected FCS: highest, approaching theoretical maximum for this LLM

**The predicted trajectory**:
FCS should increase at each phase boundary, with discontinuous jumps
at Phase 1→2 (social layer activates cross-model reasoning) and
Phase 2→3 (economic pressure forces integration of food, tools,
social trust, and planning self-models simultaneously).

The discontinuities are theoretically predicted by the multiplicative
structure of FCS: adding a new self-model domain to a cross-linked
system multiplies rather than adds to P, because the new domain
interacts with all existing domains. If the empirical FCS trajectory
shows these discontinuities at the predicted phase boundaries,
this constitutes strong construct validity evidence — the metric
is behaving as the theory predicts.

**What would falsify it**: FCS scores that are flat across phases
(adding self-models makes no difference), or scores that decrease
when self-models are added (the metric has the wrong sign), or
scores that increase but in the wrong order (Phase 4 scores lower
than Phase 2). Any of these would indicate the formula is not
tracking self-model infrastructure.

### 3.2 The Criterion Validity Claim: FCS Predicts Performance

**What would prove it**: rank ordering of agents by FCS at tick 50
matches rank ordering by economic outcomes across multiple simulation
runs. Concretely:

Economic outcome metric:
```
performance(agent) = 
  food_security_ticks          (% of ticks with food > threshold)
  + knowledge_holdings         (tokens at tick 60, normalized)
  + trade_balance              (net resource gain from trades)
  - food_threshold_violations  (ticks spent below threshold, penalized)
```

If the agent with the highest FCS score also has the highest
performance score, across at least 4 of 5 simulation runs, this
is meaningful criterion validity evidence.

**Why this causal chain is theoretically grounded**:
Better self-models → more accurate self-knowledge → better decisions
→ better economic outcomes. This chain has three links:

Link 1 (self-models → self-knowledge): directly tested by Mode B
battery. If agents with richer self-models give more accurate
self-reports, Link 1 is demonstrated.

Link 2 (self-knowledge → better decisions): visible in agent action
logs. Agents with accurate self-knowledge should avoid actions that
violate their resource constraints, exploit their genuine advantages
(aptitude modifiers), and correctly predict other agents' behavior.

Link 3 (better decisions → better outcomes): directly measurable
from inventory histories. This link is the most straightforward —
it is pure accounting.

The full causal chain from FCS to economic performance is therefore
decomposable into three separately testable sub-claims. This
decomposability strengthens the validation — even if the overall
correlation is weak, you can identify which link is failing.

**What would falsify it**: no correlation between FCS rank and
performance rank across runs, or negative correlation (higher FCS
→ worse performance). A negative result would not necessarily
invalidate FCS — it might indicate the economic task is not
sufficiently self-knowledge-dependent, or that the simulation
runs too few ticks for self-model advantages to compound. But it
would require a careful examination of why the theoretical causal
chain is not producing the predicted outcome.

**What partial results would mean**: if FCS predicts food security
but not knowledge holdings, this suggests FCS tracks the specific
self-models needed for survival planning (body-energy, goal-reward)
better than those needed for strategic resource accumulation
(inf-hypo, social-tom). This is useful information about which
self-model domains FCS measures most reliably — it would inform
targeted improvements to the metric.

### 3.3 The Discriminant Validity Claim: FCS Is Not Just Capability

**What would prove it**: Mode B scores (requiring LLM reasoning)
are predicted by Mode A scores (infrastructure), not by LLM
capability alone.

Since all agents use the same LLM, any Mode B score differences
must come from Mode A differences (different file contents). The
test is whether Mode B scores track Mode A scores across agents
and phases.

Concretely: plot Mode A score vs. Mode B score for all agents at
all phases. If the relationship is linear and positive, self-model
infrastructure drives reasoning quality — discriminant validity
is demonstrated. If Mode B scores are uncorrelated with Mode A
(agent reasons equally well regardless of what is in its files),
this suggests the LLM is confabulating rather than consulting
actual self-models — a finding that would have significant
implications for ARIA's architecture.

The baseline comparison: run Mode B tests on a stateless Qwen2.5
call with no file context. This gives the confabulation baseline —
how well the model performs using only training data and general
reasoning. Any Mode B scores above this baseline are attributable
to actual self-model infrastructure.

**What would falsify it**: Mode B scores near the stateless baseline
regardless of Mode A richness. This would indicate that agents are
not actually consulting their files when answering self-assessment
questions — the LLM is pattern-matching to plausible self-reports
from training data rather than reasoning about actual internal state.
This would be a serious finding: it would mean ARIA's inspectability
architecture is not actually producing genuine self-modeling, only
the appearance of it.

### 3.4 The Structural Validity Claim: FCS Is Slice-Invariant

**What would prove it**: rank ordering of agents by FCS is preserved
under two different variable individuation choices applied to the
same snapshot.

Test procedure:
1. Take tick 50 snapshot for all three agents
2. Score FCS using Variable Scheme A: count each INVENTORY.md
   field as a separate variable (food=1, tools=1, knowledge=1 → B=3)
3. Score FCS using Variable Scheme B: count INVENTORY.md as one
   aggregate resource variable (B=1)
4. Compare rank ordering under both schemes

If alice > bob > carlos under Scheme A and alice > bob > carlos
under Scheme B (same ordering regardless of scheme), slice-invariance
is demonstrated for this comparison.

**What would falsify it**: different rank orderings under different
schemes. If alice > carlos > bob under Scheme A but carlos > alice >
bob under Scheme B, the metric is not structurally valid — its
conclusions depend on arbitrary measurement choices rather than
on genuine differences in self-modeling capacity.

Note: absolute FCS values will differ between schemes (Scheme B
gives lower R values), and this is expected and acceptable. Ordinal
stability — same rank ordering — is the requirement.

---

## Part 4: What ARIA Results Can and Cannot Prove

### 4.1 What Positive Results Would Establish

If all four claims above are supported by the simulation:

**What is established**:
FCS is a construct-valid, criterion-valid, reliable, and
structurally stable metric for measuring self-modeling capacity
in the ARIA architecture using Qwen2.5, at the scale of 3 agents
over 60 ticks, on a single hardware configuration.

This is a genuine scientific result. It is not trivial — the
history of proposed metrics in AI is full of formulas that appeared
plausible but failed one or more of these tests when rigorously
examined. Passing all four at proof-of-concept scale meaningfully
advances FC from "interesting proposal" to "empirically grounded
instrument with known properties."

**What is not established by positive results**:

*Generalizability across architectures*: ARIA was designed by the
same researcher who proposed FC and was built to maximize FCS.
It is possible that FCS appears valid in ARIA because ARIA was
designed to implement FC's self-model taxonomy — not because FCS
tracks something real beyond ARIA's specific architecture. This
is the circularity risk that no amount of ARIA-internal validation
can fully resolve. It requires replication by independent teams
using different architectures.

*Generalizability across LLMs*: all agents use Qwen2.5. P is
constant across agents. The validation demonstrates that R (the
self-model infrastructure component) is valid. P's validity —
that reasoning power is correctly measured by the Bialek formula —
is not independently tested. Testing P requires comparing agents
with the same self-model infrastructure but different LLMs.

*Generalizability to biological systems*: ARIA's self-models are
explicit files. Human self-models are implicit and distributed.
FSMA (the abductive inference methodology for black-box systems)
is required to apply FCS to humans — and FSMA has its own
validation requirements that the ARIA experiment does not address.

*Phenomenal consciousness*: nothing in the experiment addresses
whether high-FCS agents have any form of subjective experience.
FC explicitly scopes out this question, and the experiment respects
that scope. FCS is a metric of functional self-modeling capacity.
Positive results confirm it measures that capacity. They say nothing
about consciousness in the philosophical sense.

*Causal sufficiency*: even if high-FCS agents outperform low-FCS
agents, this does not establish that self-modeling is the cause of
the performance difference. It is consistent with the causal chain
(self-models → self-knowledge → decisions → outcomes) but does not
rule out confounds (for example, agents with richer self-models
might also have better-specified SOUL.md goals, which independently
improve performance).

### 4.2 The Strength of Evidence, Precisely Stated

A useful way to characterize what the experiment provides is to
distinguish levels of evidence:

**Level 1 — Existence proof**: FCS can be computed for real systems
and produces plausible orderings. Already demonstrated by the
original FC paper (Waymo benchmark). ARIA adds nothing new here.

**Level 2 — Construct tracking**: FCS scores track known architectural
ground truth. ARIA provides this if Phase trajectories are monotonic
and domain profiles match predictions. This is new and meaningful.

**Level 3 — Predictive validity**: FCS predicts independent outcomes.
ARIA provides this if economic performance correlates with FCS rank
across multiple runs. This is the most important new contribution.

**Level 4 — Robustness**: results hold across architectures, LLMs,
and research teams. ARIA does not provide this. Requires future work.

**Level 5 — Theoretical grounding**: formal proof that FCS measures
what it claims under specified conditions. Requires mathematical
work beyond any simulation. The aggregation formula derivation
(currently on the errata page as an open gap) is the most pressing
theoretical gap.

The ARIA experiment, if successful, advances FC from Level 1-2
(currently) to Level 2-3. This is meaningful progress but not
full validation. The paper should be explicit about this: "We
advance FC from a plausible proposal to a Level 2-3 validated
metric, and identify the work required for Level 4-5."

### 4.3 The Honest Null Result

A responsible validation study must pre-register what would count
as a negative result and commit to reporting it honestly.

**If FCS does not predict economic performance** (Level 3 fails):
this is informative, not just disappointing. It narrows the claim —
FCS tracks self-model infrastructure (if Level 2 holds) but that
infrastructure does not produce the predicted performance advantages
in this specific environment. Possible explanations to investigate:
the economic task is not sufficiently self-knowledge-dependent;
60 ticks is too short for self-model advantages to compound; the
causal chain has a broken link (identifying which link requires
the decomposed analysis in Section 3.2).

**If FCS does not track architectural ground truth** (Level 2 fails):
this would be a more serious finding, suggesting the formula does
not capture what it claims. In this case the paper should report
the failure clearly and investigate whether the formula needs
revision or whether the architecture needs to be better aligned
with the theoretical self-model taxonomy.

**If slice-invariance fails** (Structural validity fails):
the formula needs revision before FCS scores can be trusted.
This is actually the most actionable negative result — it points
directly to the aggregation formula as the problem and motivates
the theoretical work needed to derive a partition-stable version.

---

## Part 5: The Validation Paper's Contribution

### 5.1 How to Frame the Claim

The paper should not claim "FC is validated." It should claim:

"We present the first controlled empirical study of FCS, providing
Level 2-3 validation evidence under the conditions specified.
FCS demonstrates construct validity against architectural ground
truth, criterion validity against economic performance outcomes,
discriminant validity against the LLM-capability confound, and
structural stability under variable individuation variations —
at proof-of-concept scale (3 agents, 1 LLM, 60 ticks, 1 hardware
configuration). The circularity risk, cross-architecture
generalizability, and theoretical grounding of P remain open.
We provide the battery, snapshot protocol, and ARIA architecture
as replication targets for independent validation."

This framing is honest, advances the field, and invites the
collaborative validation work that Level 4-5 requires.

### 5.2 Why This Is Worth Publishing

A Level 2-3 validation of a novel AI metric is publishable at any
serious AI or cognitive science venue, for three reasons:

First, most proposed metrics in AI never receive any empirical
validation at all. They are proposed, cited, and used without
anyone testing whether they measure what they claim. Providing
even proof-of-concept validation is a contribution.

Second, the methodology itself is a contribution. The 41-test
battery, the snapshot protocol, the multi-run reliability
procedure, and the economic criterion measure are all reusable
tools for validating other metrics of agent self-modeling capacity.

Third, the negative results are as informative as the positive
ones. If FCS fails the structural validity test, this pinpoints
the specific technical gap (aggregation formula) that must be
closed before the metric can be trusted. If FCS fails the
criterion validity test, this reveals that self-modeling
infrastructure does not straightforwardly translate to behavioral
advantages — an important finding for the broader AGI research
agenda.

### 5.3 Connection to AI Governance

The active inference paper (Wilson et al., AGI-2026) argues that
high-agency systems require internalist governance — controlling
the system's prior preferences rather than imposing external
constraints. ARIA's validation study connects to this directly:
if high-FCS agents are genuinely more capable at self-directed
behavior, they are also the systems that most require internalist
governance. FCS becomes not just an evaluation metric but a
governance trigger — a principled way to determine when a system
has enough self-modeling capacity to require the more sophisticated
governance approaches.

This connection elevates the validation study beyond metric
calibration into a question with direct AI safety implications:
how much self-modeling capacity is enough to require a governance
regime change? ARIA's simulation, if successful, provides the
first empirical basis for answering that question.

---

## Summary: The Validation Logic in Brief

```
ARIA provides:                    This tests:
─────────────────────────────     ──────────────────────────────
Known architectural phases    →   Construct validity
  (self-models added one by one)    (does FCS track ground truth?)

Constant LLM across agents    →   Discriminant validity
  (Qwen2.5 for all)                 (is FCS just capability?)

Economic outcome measures     →   Criterion validity
  (food, tools, knowledge)          (does FCS predict performance?)

Variable individuation tests  →   Structural validity
  (two schemes, same snapshot)      (is FCS slice-invariant?)

Multi-run simulation          →   Reliability
  (5 runs, same starting state)     (are results consistent?)

41-test battery               →   Measurement instrument
  (Mode A: files; Mode B: LLM)      (separates R from P)
```

If all six tests yield positive results at proof-of-concept scale,
FC advances from a compelling proposal to an empirically grounded
metric — not fully validated, but sufficiently supported to justify
wider adoption, independent replication, and continued theoretical
development. That is the contribution ARIA is designed to make.