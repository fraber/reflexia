# The ARIA Project Summary

---

## Pitch

- It's OpenClaw "with a conscious mind"
- Based on Functional Consciousness metric
- Designed to maximize FC
- LLM-architecture first cognitive architecture.
  LLMs read and write text. You need to embrace this
  if you want to leverage their reasoning power.

---

## Origin and Purpose

**ARIA** (Adaptive Reasoning with Inspectable Architecture) is an
AI agent / cognitive architecture based on LLMs, designed to maximize
**Functional Consciousness (FC)** — a measurable metric for an agent's
capacity to reason about its own internal states (Bergmann, AGI-2026).

ARIA re-implements **Scene-Based Reasoning (SBR)** (Bergmann & Fenton,
AGI-2015) using LLMs. SBR had 9 subsystems; ARIA maps each to an LLM 
call or Python rule. The core design principle:

> **Every internal state that matters for behavior must exist as a
> readable, reasoned-over artifact — never only as a latent vector.**

ARIA is built on top of **Nanobot** (~4k LoC, file-based, git-backed
agent framework).

ARIA is not a chatbot wrapper. It is a multi-agent simulation platform
where agents have persistent memory, explicit self-models, social
relationships, and economic incentives — and where every internal state
is a readable file.

---

## Functional Consciousness (FC) — Essential Background

**Functional Consciousness Score FCS = R × P** where:
- **R = B × D**: representational capacity (breadth × depth)
  - B = number of self-model variables tracked above noise threshold
  - D = average mutual information per variable (Bialek et al.)
- **P**: reasoning power — information amplification ratio, treated
  as a **system-level constant per LLM** (not per-agent, not
  per-tick). For controlled experiments using one LLM, P cancels
  out of inter-agent comparisons; R drives all FCS differences.
- Multiplicative zero-floor: R=0 OR P=0 → FCS=0
  (stateless LLM: R=0 → FCS=0; static map: P=0 → FCS=0)

**10 FC self-model domains**: Body, Spatial, Action/Planning,
Goal/Motivation, Cognitive, Informational, Emotional/Affective,
Social/Interaction, Meta/Reflexive, Ethics/Safety.

**FCS metric status**: formally specified computational metric with
operationalization gaps requiring empirical validation. Psychometric
criteria (construct validity, criterion validity, reliability,
structural validity) apply because operationalization requires human
judgment. See: functional-consciousness.com/updates

---

## Architecture

### Module Map

| Module | Role | LLM? | Primary Output |
|---|---|---|---|
| Perception | Sensor → structured scene | Optional | WORLD.md slice |
| Action | Planner → tool/actuator calls | No | Side effects |
| Planning | Goal + state → ranked plans | Yes | PLAN.md (JSON) |
| Simulation | Forward-simulate other agents | Yes (per agent) | Predicted states |
| Memory | Store + reflect on episodes | Yes (reflect only) | MEMORY.md |
| Plan Reflection | Meta-ops on plans | Yes | Critique JSON |
| Belief | Maintain + update belief store | Yes | MEMORY.md beliefs |
| Executive | Orchestrate, log attention | Yes | Goal doc + log |
| Self-Model Aggregator | Aggregate all 10 FC domains | No | SELF_MODEL.md |
| Self-Assessment | Run FC battery | Yes | FCS scores |
| world_tick.py | Rule-based world update | **NEVER** | WORLD.md |


### Proposed File Structure (per agent)
```
agents/{name}/
  SOUL.md        # Personality, persistent goals, values + violation conditions
  MEMORY.md      # Episodic memory + belief store (confidence, source, verified)
  RELATIONS.md   # Social graph: trust scores, debt, interaction history
  INVENTORY.md   # Private resource holdings (food, tools, knowledge tokens)
  PLAN.md        # Current active plan with step status
  SELF_MODEL.md  # FC self-assessment output (written by self_assess skill)

SOUL.md          # Global SOUL.md from Nanobot, not sure what to do with this.
WORLD.md         # Shared world state: locations, global resources, events
SELF_MODEL.md    # Global FC aggregator (all 10 domain self-models)
sim.log          # Tick log
messages/
  {name}_inbox.md  # Per-agent message queue
```

## Possible implementation plan

Layer 1 — Memory:
- 1.1 Episode Compressor: compress.py, triggers at 50 episodes
- 1.2 Belief Propagation: belief_check.py, conflict detection
- 1.3 Source Reliability Ledger: sources.md, Python-maintained
- 1.4 Hypothesis Ledger: HYPOTHESES.md + 5-tick LLM update

Layer 2 — Planning:
- 2.1 Hierarchical Plan Structure: JSON tree in PLAN.md
- 2.2 Plan Evaluator: 2-alternative Monte Carlo comparison
- 2.3 Skill Library: SKILLS.md, successful plan templates

Layer 3 — Social:
- 3.1 Multi-Dimensional Trust: {competence, values, communication}
- 3.2 Recursive ToM depth 2: "my model of X's model of me"
- 3.3 Social Network Topology: NETWORK.md, influence tracking

Layer 4 — Meta/Reflexive:
- 4.1 Attention Log: derived from agent_tick inner field, no LLM
- 4.2 Calibration Ledger: prediction accuracy over time, Python
- 4.3 Bounded Self-Modification: PROPOSALS.md + human approval

Layer 5 — Ethics:
- 5.1 Pre-Action Ethics Check: LLM call before high-stakes actions
- 5.2 Ethical Uncertainty Field: confidence on ethical judgments

---

## Comparison with Other Cognitive Architectures

| Capability | ACT-R | LIDA | OpenCog | ARIA |
|---|---|---|---|---|
| Natural language self-explanation | X | X | Partial | Ok |
| Native audit trail | X | X | X | Ok |
| Multi-agent social modeling | X | X | Partial | Ok |
| Persistent long-term memory | Partial | X | Partial | Ok |
| Ethical drift detection | X | X | X | Ok |
| Cross-domain transfer | X | X | Partial | Ok |
| Real-time performance | OkOk | OkOk | Ok | X |
| Formal provability | Ok | Partial | Partial | X |
| FC self-modeling | X | X | X | Ok |

ARIA occupies a previously inaccessible design space: inspectability
and auditability at the cost of speed and formal provability.
Governance implication: high-agency systems require internalist
control; ARIA is the first architecture where internalist governance
is architecturally native.

**OpenClaw** (openclaw.ai): predecessor of Nanobot. Nanobot
is a reimplementation in ~4k LoC. ARIA provides FC-maximizing 
cognitive architecture.

---

## Related Papers

**FC paper**: Bergmann (AGI-2026). Proposes FCS = R×P metric.
Benchmarks: Map=0, Stateless LLM=0, Waymo=74.5k, Gen.Agents=6.5M,
Human=14M. FSMA as black-box inference method. 46 self-models across
10 domains. Website: functional-consciousness.com

**SBR paper**: Bergmann & Fenton (AGI-2015).
URL: agi-conf.org/2015/wp-content/uploads/2015/07/agi15_bergmann.pdf
3D-Scenes instead of LLM text descriptions.
Nine subsystems, gödelization (plans as inspectable scenes).
ARIA re-implements each subsystem with LLM or Python rule.

**Nanobot**: lightweight agent framework, ~4k LoC, file-based,
universal LLM support. ARIA extends with world simulation, 
multi-agent coordination, and FC measurement layer.
