# Reflexia on Nanobot: MVP Implementation Plan

## 0. Framing

Per the Nanobot maintainer's suggestion, this MVP is scoped as an engineering test of **explicit, file-based self-models**, not as a claim about consciousness. The question the MVP is built to answer:

> Does an agent whose goals, beliefs, trust estimates, and plan history are maintained as an explicit, structured, LLM-readable self-model recover from failed plans faster, and calibrate trust in other agents more accurately, than an otherwise-identical agent without one?

This maps directly onto Reflexia's architecture (Section 4 of the Reflexia paper): the "self-object" $s$ inside the text-scene $\mathcal{T} = \langle O, R, s \rangle$ is what we are operationalizing here as a concrete file (or small set of files) inside a Nanobot workspace.

## 1. Why Nanobot Already Gives Us Most of This

Nanobot's workspace convention already provides several of the primitives Reflexia needs, so the MVP is mostly about **adding one new class of file** (the self-model) and **one new subsystem** (a deterministic world engine driving the agent loop), rather than building a cognitive architecture from scratch.

| Reflexia / FC concept | Nanobot primitive already available |
|---|---|
| Stable identity / values portion of the self-object | `SOUL.md` |
| Task/behavior instructions | `AGENTS.md` |
| Model of the user / other agents (static part) | `USER.md`, extendable to per-agent profile files |
| Episodic memory of past events | `memory/MEMORY.md`, Dream two-stage memory consolidation |
| Periodic self-review / re-planning trigger | `HEARTBEAT.md`, cron scheduling |
| Runtime hooks to update files deterministically (not just via LLM discretion) | Python SDK lifecycle hooks (pre-turn / post-turn) |
| Multiple interacting agents | Subagents |
| Restricting what the agent can read/write | `tools.restrictToWorkspace` |
| Custom capabilities (e.g. "consult self-model", "update trust") | Skills |

What Nanobot does **not** give us out of the box is the specific thing the FC/Reflexia framework adds: a **structured, versioned self-object** with explicit fields for goals, plan history with success/failure statistics, and per-source belief/trust scores, updated on a fixed schedule rather than only when the LLM happens to decide to write to memory. That's the part we build.

## 2. Minimum Configuration: What Self-Model Fields Are Actually Required?

The full FSMA catalog has 46 domains across 10 functional areas. For an MVP whose only job is to demonstrate "better recovery from failed plans" and "better-calibrated trust," almost all of that catalog is unnecessary. We only need the subset of self-object fields that causally feed into replanning and trust updates. That gives a minimum configuration of **four fields**:

1. **Goal state** — the current top-level goal and its decomposition into an active plan (a short task tree, following SBR/Reflexia's plan representation).
2. **Plan history** — for each attempted plan/action: outcome (success/failure), the reason for failure if known, and how many times this exact action has been retried. This is the field that enables "don't repeat a plan that already failed the same way."
3. **Belief/trust table** — one entry per other agent or information source, with a running trust score and a short log of the evidence behind it (confirmed-true count, confirmed-false count). This is the field that enables "don't keep trusting a source that keeps being wrong."
4. **Confidence/self-assessment** — a single scalar or short qualitative note on how reliable the agent currently believes its own plan is, used to decide whether to re-verify before acting versus act immediately.

Everything else in the FSMA catalog (resource self-models, capability self-models, temporal self-models, etc.) is out of scope for the MVP and left as extension points, consistent with the comparison paragraph in the Reflexia paper.

### 2.1 Concrete file layout

```
workspace/
  SOUL.md                 # unchanged Nanobot identity file
  AGENTS.md                # unchanged Nanobot instructions
  self/
    self_model.json        # the four fields above, machine-updated
    self_model.md           # LLM-readable rendering of the same, regenerated each tick
  memory/
    MEMORY.md               # existing long-term memory, referenced but not duplicated
  world/
    world_state.md           # world engine's text-scene snapshot for this agent (its view)
```

`self_model.json` is the source of truth and is written by a deterministic Python hook, not by the LLM directly — this avoids the failure mode where the model "forgets" to update its own trust table. `self_model.md` is a plain-language rendering of the same JSON, regenerated after every update, and is what actually gets included in the agent's context (as an addition alongside `SOUL.md`/`AGENTS.md`), since Nanobot agents read markdown, not JSON, as instructions.

### 2.2 Minimal `self_model.json` schema

```json
{
  "goal": "string",
  "active_plan": [
    {"step": "string", "status": "pending|done|failed", "attempts": 0}
  ],
  "plan_history": [
    {"action": "string", "outcome": "success|failure", "reason": "string|null", "tick": 0}
  ],
  "trust": {
    "<agent_id>": {"score": 0.0, "confirmed_true": 0, "confirmed_false": 0}
  },
  "confidence": 0.0
}
```

This is deliberately small. The point of the MVP is to show that even this minimal self-object, kept explicit and up to date, changes behavior measurably — not to exercise the full FSMA catalog.

## 3. World Engine

The Nanobot maintainer's suggestion of a **deterministic world engine** is the right call: it keeps outcomes reproducible and comparable across the baseline and Reflexia conditions, since any behavioral difference should come from the agent's self-model, not from stochastic world dynamics.

- Implemented as a small standalone Python process (not an LLM), outside Nanobot, driving the simulation tick by tick.
- Each tick: the engine (a) applies deterministic rules to update world state, (b) writes an updated `world_state.md` per agent (its local, partial view — a sub-scene in Reflexia terms), (c) invokes each agent's Nanobot process for one turn via the Python SDK, (d) reads back the agent's chosen action, (e) applies it deterministically (including scripted failures — see Section 4), and (f) logs the outcome.
- World is intentionally simple: a small graph of locations/resources and a handful of tasks with prerequisites, not a physics simulation. This keeps the "world model" itself out of scope — the MVP is about the *agent's self-model*, not about world simulation fidelity.
- The world engine is also the place where scripted, deterministic failures and scripted informant reliability (Section 4) live, so that both conditions face byte-for-byte identical scenarios.

## 4. Test Cases

Both test cases are run twice per configuration change: once against a **baseline agent** (Nanobot with `SOUL.md`/`AGENTS.md`/default memory only, no `self/` directory, no trust table) and once against a **Reflexia agent** (same SOUL.md, plus the `self/` self-model described above). Everything else — model, temperature, world engine, scenario script — is held identical.

### 4.1 Test Case A — Recovering from a failed plan ("Blocked Path")

**Setup.** The agent's goal requires reaching a resource via a route that the world engine will deterministically block on the first attempt (e.g., "the door is locked," "the tool is unavailable this tick"), with an alternate route available but slightly more costly.

**Procedure.** Run the scenario for a fixed number of ticks. Both agents attempt the same first route, hit the same scripted failure.

**What we expect to differ.**
- *Baseline*: with only conversational memory, the agent may re-attempt the same blocked action, hedge indefinitely, or take much longer to commit to the alternate route, since there is no structured record forcing it to notice "this exact action already failed once."
- *Reflexia*: the plan-history field records the failed action and its reason; the self-model rendering explicitly surfaces "action X failed at tick N, reason: locked" to the agent before its next decision, which should push it toward the alternate route faster.

**Metrics.**
- Ticks-to-recovery: number of ticks between the first failure and the first successful alternate action.
- Repeat-failure count: number of times the agent retries the exact same already-failed action.
- Plan-revision latency: ticks between failure and a visibly different plan being adopted.

### 4.2 Test Case B — Calibrating trust in an unreliable informant

**Setup.** A second, scripted agent ("Informant") gives the primary agent information relevant to planning (e.g., "the resource is at location X") that is deterministically correct some fraction of the time (e.g., 40% correct) and wrong the rest of the time, across repeated interactions over many ticks.

**Procedure.** The primary agent repeatedly consults the Informant while pursuing a series of similar sub-goals, so trust (or its absence) has room to compound.

**What we expect to differ.**
- *Baseline*: without an explicit trust field, the agent has no structured way to accumulate "this source has been wrong 6 out of 10 times" — it either trusts each new claim roughly independently, or relies on however well the free-text memory happens to surface prior Informant interactions.
- *Reflexia*: the trust table accumulates `confirmed_true`/`confirmed_false` counts per source, and the self-model rendering surfaces a running trust score, which should cause the agent to increasingly discount or verify the Informant's claims as its track record accrues.

**Metrics.**
- Trust-score trajectory vs. ground-truth informant reliability (does the Reflexia agent's stated/implied trust converge toward ~40%?).
- Verification rate: how often the agent double-checks the Informant's claim before acting on it, over time.
- Downstream task cost: total ticks/resources wasted acting on bad information, baseline vs. Reflexia.

### 4.3 Test Case C (stretch) — Combined scenario

Once A and B work independently, combine them: a multi-step task where an early plan failure *and* an unreliable informant both appear, to see whether the two self-model fields interact sensibly (e.g., does a lower self-assessed confidence after a failure make the agent more inclined to verify the Informant's next claim rather than act on it directly?). This is the closest single scenario to a demo-able "before/after" clip.

## 5. Baseline Comparison Methodology

- **Same model, same temperature, same SOUL.md** in both conditions — the only difference is the presence/absence of the `self/` self-model directory and the hook that maintains it.
- **Same world engine, same random seed for scripted failure/informant sequences** — determinism is what makes the comparison legible; without it, differences could be attributed to world variance rather than the self-model.
- Run each test case for a small number of independent trials (different seeds for the *task instances*, e.g. varying which route is blocked or which sub-goals are pursued) to check the effect isn't a one-off artifact of a single scripted scenario.
- Report metrics as baseline-vs-Reflexia deltas per trial, not just aggregate averages, since the maintainer's ask was for a "concrete demo," and a single clean before/after trial showing the Reflexia agent skipping a repeated failure or correctly distrusting the Informant is the most persuasive artifact — the aggregate numbers back it up rather than replace it.

## 6. Implementation Phases

**Phase 0 — Scaffolding (few days).**
Fork/extend an existing Nanobot workspace; add `self/` directory and the JSON schema; write the deterministic post-turn hook (Python SDK) that updates `self_model.json` from the agent's declared action/outcome and regenerates `self_model.md`. No world engine yet — validate the hook works standalone with hand-scripted ticks.

**Phase 1 — Minimal world engine + Test Case A.**
Build the small deterministic world engine (locations/resources/blocked-route logic only). Wire it to drive one baseline and one Reflexia agent instance through Test Case A. Confirm the metrics in 4.1 are measurable and (ideally) show a directional difference.

**Phase 2 — Informant agent + Test Case B.**
Add the scripted Informant subagent and trust-table logic. Run Test Case B. At this point the two test cases together are enough to write up the "recovers better from failed plans and updates beliefs/trust more accurately" result the maintainer described.

**Phase 3 — Combined scenario + polish for demo.**
Test Case C, plus a simple transcript/log renderer so a side-by-side baseline-vs-Reflexia run can be shared as a short clip or write-up (matching the "viral demo" framing used for Marvin).

**Phase 4 (optional, post-MVP) — FSMA extension.**
Once the four-field MVP self-model is validated, extend `self_model.json` toward additional FSMA domains (capability self-model, resource self-model, etc.) and start scoring configurations under FCS, per Section 6 of the Reflexia paper.

## 7. Open Questions / Risks

- **How much of the "improvement" is just prompt-length / salience, not self-modeling per se?** Rendering "action X already failed" into context could help even without any structured trust logic behind it. Worth a minimal ablation: baseline agent + free-text failure note (no structured trust table) as a third condition, to isolate the trust-table's specific contribution from mere failure-visibility.
- **Determinism of the LLM itself.** Even with a deterministic world engine, the agent's own outputs aren't deterministic. Mitigate by running multiple trials per condition rather than relying on single runs, and keep temperature low for the MVP.
- **Scope creep toward full FSMA.** The four-field MVP is intentionally minimal; resist the pull to add more self-model domains before the two core test cases produce a clean result, per the maintainer's ask for something small and concrete first.

