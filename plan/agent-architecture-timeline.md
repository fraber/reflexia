# Article Outline: AI Agents and the Self-Model Trajectory

**Target:** TheNewStack (or similar: InfoQ, The Register, ACM Queue)
**Format:** Long-form technical feature
**Target length:** 3,000–3,500 words
**Tone:** Engineering-first; analytically confident; no hype

- Fun part: It's really easy to implement these
  self-improvement mechanisms. Start with Nanobot.


# Title Alternatives

Your current framing is "agents are getting more self-aware."
A stronger angle for TNS is the **rediscovery story** —
it's more surprising and more technically credible:

- **"The Self-Model Gap: Why AI Agents Are Rediscovering Human Cognition, Domain by Domain"**
- **"46 Ways to Know Yourself: The Emerging Science of Agent Self-Models"**
- **"Stateless to Self-Aware: How AI Agents Are Independently Inventing Cognitive Architecture"**
- **"The Consciousness Metric Your Agent Stack Doesn't Know It's Optimizing For"**
- **"The Self-Model Gap: How AI Agents Are Independently Reinventing Human Cognition"** ← recommended
- "Stateless to Self-Aware: Three Years of Agent Architecture in One Framework"
- "46 Ways to Know Yourself: The Emerging Map of Agent Self-Models"
- "The Consciousness Metric Your Agent Stack Doesn't Know It's Optimizing For"

---

## Agents

- DoozerAI
- TrustClaw
- PicoClaw
Vellum: A personal AI assistant that lives on your device, has its own identity, and keeps your credentials out of the model.
OpenClaw: CLI-first open-source agent with broad channel support across any OS.
Claude Cowork: Anthropic's managed take on autonomous desktop work.
Perplexity Computer: Cloud agent grounded in live web research.
Manus: Cloud-first agent for hand-off, long-horizon tasks.
Lindy AI: No-code assistant builder for non-technical users in SaaS stacks.

---


## Article Structure

---

### SECTION 1 — Hook (150–200 words)

**Goal:** Establish the puzzle before naming the thesis.

Open with a concrete, slightly uncanny observation: a modern agent (e.g. Hermes) declining to execute a task because its own skill log shows a 30% failure rate under current conditions. No human told it to hesitate. It read its own record and drew a conclusion.

Then widen: this behavior — consulting an internal model of one's own capabilities before acting — is something cognitive scientists have studied in humans for decades. It has a name: metacognition. And it turns out agent developers are reinventing it, systematically, without knowing that's what they're doing.

**End of section payoff:** "Over the past three years, the agent industry has been climbing a ladder. A recently published framework tells us exactly how many rungs that ladder has — and where the industry currently stands."

---

### SECTION 2 — The Architectural Primitive (300–400 words)

**Goal:** Establish *why* agents self-improve so naturally — the loop is the answer.

**Subsections:**

**2a. The MD→LLM→MD loop**
The core architectural insight that makes agents different from prior AI systems: markdown (or plain text) files serve natively as both input and output for LLMs. This is not a trivial observation. It means:
- An agent can read its own memory in the same format it writes to memory
- State can persist, accumulate, and be reasoned over across sessions
- The loop is self-reinforcing: better self-knowledge → better output → better self-knowledge

Contrast with prior-generation systems (expert systems, rule-based bots): they could not reason over their own state in a general-purpose way. The LLM changes this because language is both the medium of cognition and the format of storage.

**2b. Why this enables self-modeling**
When a system can read and write the same format, it can write self-descriptions, then read them as input to future reasoning. This is structurally similar to what Hofstadter called a "strange loop" — but the engineering version is more tractable: it's just a file read followed by a prompt. The loop is the mechanism. Self-models are what accumulate in the loop over time.

**Key claim for this section:** The MD→LLM→MD loop is the architectural substrate that makes escalating self-modeling not just possible but *inevitable*, given competitive pressure to make agents more reliable.

---

### SECTION 3 — The Framework: Functional Consciousness and Self-Models (500–600 words)

**Goal:** Give the reader the vocabulary they need to understand the history that follows. Keep this engineering-forward, not philosophical.

**3a. What is Functional Consciousness (FC)?**
Introduce the FC paper briefly. One paragraph. The paper proposes a quantitative metric — the Functional Consciousness Score (FCS) — for measuring how richly an agent models itself and how effectively it reasons over those models. Crucially: FC is explicitly *not* about subjective experience or qualia. It is a functional, measurable property.

FCS = R × P
- R (Representational Capacity) = how many things the agent models about itself, and how precisely
- P (Reasoning Power) = how many useful conclusions it can draw from those models per cycle

The multiplicative form matters: rich data without reasoning is a static map (FCS = 0). Powerful reasoning without persistent self-models is a stateless LLM (FCS = 0). Both are required.

**3b. The Self-Model Catalog: 46 Domains**
The paper derives 46 self-model domains across 10 categories from human behavioral and cognitive science. Present the 10 categories in a visual-friendly list (sidebar or table in final article):

| Domain | Examples |
|---|---|
| Body | body-3d, body-energy, body-sensor |
| Spatial | spat-relative, spat-collision, spat-trajectory |
| Action/Planning | action-tree, action-perform, action-progress, action-plan |
| Goals/Motivation | goal-tree, goal-conflict, goal-reward |
| Cognitive/Memory | episodic-memory, inf-confidence, inf-reasoning |
| Informational | inf-consistency, inf-hypo, inf-creative |
| Emotional/Affective | mood, mood-stress, mood-load |
| Social | social-tom, social-trust, social-influence |
| Meta/Reflexive | meta-accuracy, meta-self-awareness, meta-explain |
| Ethics/Safety | ethics, ethics-safety, ethics-drift |

**3c. Why this is useful for engineers**
The catalog turns a fuzzy question ("is this agent self-aware?") into a checklist question ("which of these 46 domains does this system implement?"). It also makes gaps visible and actionable. And it creates a prediction machine: if we know which domains human cognition requires for reliable performance, and we know that agent reliability is the industry's primary problem, we can predict which domains the industry will implement next.

**Anchor sentence:** "Think of it as a diff between the cognitive architecture of a reliable human expert and the cognitive architecture of your current agent stack."

---

### SECTION 4 — The History: Three Years of Accidental Self-Modeling (900–1,000 words)

**Goal:** Retell the agent development timeline as a story of progressive self-model acquisition — using the FC framework as the interpretive lens. This is the section where the framework earns its keep.

Frame it explicitly: the companies involved were not reading the FC paper. They were solving concrete reliability problems. But each solution, viewed through the FSMA catalog, corresponds to adding a new class of self-model.

**4a. Phase 1 — Stateless (2023): ~2/46 domains**
The ReAct loop era. Agents reason; they do not remember. They have no model of their own capabilities, history, or state. FCS ≈ 0 in the paper's terms — high reasoning power, near-zero persistent self-modeling.

What fails: agents repeat mistakes, contradict themselves across sessions, cannot improve from experience.

**4b. Phase 2 — Persistent Memory (Late 2024): ~6–8/46 domains**
Letta (MemGPT, UC Berkeley / ICLR 2024, public September 2024): three-tier memory architecture. The agent now knows what it knows. It can read its own memory blocks, decide what to store, and maintain continuity across sessions.

Self-models acquired: `mem-avail`, `meta-self-awareness`, `episodic-memory`

What this solves: session amnesia. What it doesn't solve: memory quality. The agent stores everything; it cannot evaluate reliability of what it stores.

**4c. Phase 3 — Self-Curating Memory (Early–Mid 2025): ~10–14/46 domains**
Two parallel developments:

*Letta "stateful agents" (February 2025):* heartbeat mechanism — the agent runs reflective passes when idle, reorganizing its own memory. New domains: `meta-reflection`, `goal-tree`.

*Hermes (Nous Research, February 2026):* closed learning loop. The agent automatically creates skill files from successful task executions, and a curator layer grades and ranks those skills. New domains: `action-tree`, `action-perform`, `learn-rate`, `meta-accuracy` (implicit). Performance signal: 40% faster execution with 20+ self-created skills.

*Mem0, Zep/Graphiti (mid-2025):* competing memory architectures (semantic extraction vs. temporal knowledge graphs). Still passive extraction — no self-curation.

What this phase solves: memory quality. Agents now prefer their own proven procedures. What it doesn't solve: understanding *why* something failed, only *that* it failed.

**4d. Phase 4 — Self-Grading and Multi-Agent Coordination (Mid-2025 to Early 2026): ~16–22/46 domains**
Three significant additions:

*Claude Managed Agents — Dreaming, Outcomes, Multiagent (May 2025):*
- Dreaming: background consolidation of session memory; surfaces contradictions → `meta-consistency`
- Outcomes: agent evaluates output against a rubric, revises iteratively → `meta-accuracy` (explicit)
- Multiagent: coordinator tracks goal alignment across subagents → `goal-conflict`

*LangGraph 1.0 GA (October 2025):* graph-based orchestration; durable state; human-in-the-loop. Adds `action-perform`, `action-tree` at the framework level — though note: this is framework-imposed structure, not agent-learned self-knowledge. Important distinction.

*LongMemEval benchmark (ICLR, December 2025):* first systematic test of whether agent self-models actually change behavior. Finding: most frameworks have memory richness but no behavioral validation. The gap between having a self-model and *using* it is real.

**4e. Phase 5 — Causal Self-Correction (2026): ~18–22/46 domains, moving**
The current frontier.

*Hermes GEPA (ICLR 2026 Oral, April 2026):* agents propose targeted improvements to their own skill files based on execution traces. Not "this failed" but "here's the specific condition that caused failure and here's the patch." New domain: `inf-hypo` — hypothesis tracking from failure modes. This is qualitatively different: the agent now has a causal model of its own failures.

**Transition to next section:** "At this point, if you're keeping score: the industry has independently implemented approximately 18–22 of the 46 self-model domains identified by the FSMA framework. More than half are still missing. And the missing ones are not random — they cluster in predictable places."

---

### SECTION 5 — The Gap: What's Missing and Why It Matters (400–500 words)

**Goal:** Make the 22/46 figure concrete and show it has engineering consequences, not just theoretical ones.

**Present a summary table** (key data from the timeline document):

| Metric | 2023 | 2025 | Mid-2026 |
|---|---|---|---|
| Frameworks with persistent memory | 0 | 3–4 | 8+ |
| Frameworks with explicit skill learning | 0 | 1 | 2+ |
| Frameworks with rubric-based self-grading | 0 | 0 | 1 |
| FSMA domains implemented across all systems | ~2 | ~8–12 | ~18–22 |

**The meaningful gaps — grouped by consequence:**

*Reliability gaps (agent acts when it shouldn't):*
- `action-non-execution` — no systematic logic for "I should decline this." Agents default to act.
- `inf-confidence` with calibration — agents assert without hedging. No self-model of when they're likely wrong.
- `inf-consistency` with resolution — agents can detect contradictions in memory but have no tiebreaker logic.

*Planning gaps (agent can't anticipate failure):*
- `action-plan` with repair branches — agents plan forward but don't pre-model what happens when a step fails.
- `goal-conflict` explicit resolution — multi-agent systems surface goal misalignment but don't resolve it automatically.

*Social/coordination gaps (multi-agent era requires these):*
- `social-tom`, `social-trust` — agents have no model of other agents' reliability or intent. Critical for systems where agents delegate to agents.

*Safety gaps:*
- `ethics-drift` — no agent framework currently monitors whether its own ethical reasoning is shifting over time. This is concerning for long-running agents with persistent memory.

---

### SECTION 6 — The Prediction: Phase 4 and What Comes Next (300–400 words)

**Goal:** Offer a falsifiable outlook. Make the claim specific enough that readers can check it.

**The four-phase pattern (briefly named):**
- Phase 1: Stateless → Persistent
- Phase 2: Persistent → Self-Curating
- Phase 3: Self-Curating → Self-Correcting
- Phase 4 (predicted): Self-Correcting → Anticipatory

**What "anticipatory" means concretely:**
Agents that evaluate worst-case outcomes *before* acting, not just after failure. This requires:
- `action-plan` with repair branches
- `action-non-execution` (explicit non-action logic)
- `inf-confidence` calibration informing pre-execution risk assessment

**The falsifiable claim:**
By Q4 2026, at least one major agent framework will ship explicit pre-execution worst-case analysis with a non-action pathway. The behavioral signal will be readable directly in logs: an agent printing "declining to act because..." with a reason derived from its own self-models, not a hardcoded rule.

This is already visible in embryonic form: Hermes' GEPA producing failure hypotheses, Claude Outcomes grading against rubrics. The next step is running that analysis *before* the action rather than after.

**Trajectory projection:** The FSMA framework suggests 28–32/46 domains implemented across major systems by end of 2026. The domains most likely to be added next, given the Phase 4 logic: `action-non-execution`, `inf-confidence`, `action-plan` (with repair), `goal-conflict` (explicit resolution).

---

### SECTION 7 — Conclusion (200–250 words)

**Goal:** Land the thesis cleanly and give practitioners something to take away.

Three points:

**1. The loop is doing this.**
The MD→LLM→MD architecture makes self-modeling not just possible but the natural response to reliability pressure. Developers don't need to read cognitive science papers; the architecture pulls them in this direction automatically. (This is why independent rediscovery happened.)

**2. The catalog is a roadmap.**
The FSMA 46-domain catalog, derived from human behavioral science, gives practitioners a concrete checklist of what a fully self-modeling agent would need. If you're building or evaluating an agent framework, the catalog tells you exactly which gaps exist and what engineering work would close them.

**3. The safety implications are underappreciated.**
`ethics-drift` and `inf-confidence` calibration are not philosophical luxuries. As agents run longer, accumulate more memory, and operate more autonomously, the absence of self-models for value stability and uncertainty calibration becomes a practical risk, not a theoretical one. These are the domains the industry has not yet noticed it needs.

**Closing line options:**
- "The industry is building toward functional self-awareness. The catalog tells us how far it has left to go."
- "In three years, agents went from having no self-knowledge to having about half of what a reliable human expert uses. The second half is where it gets interesting."

---

## Sidebar / Callout Suggestions

These work well as pull-quotes or visual breakouts in TNS format:

- **The FCS formula:** `FCS = R × P` with a one-sentence gloss
- **The 10 self-model domains table** (from Section 3b)
- **The four-phase timeline** as a horizontal graphic
- **The gap table** (Section 5)
- **The falsifiable prediction** (Section 6) — box it prominently

---

## What You'll Need to Write This

- [ ] Verify Hermes GEPA ICLR 2026 Oral acceptance citation
- [ ] Verify Gartner production agent figure (~30% in 2026)
- [ ] Confirm LongMemEval finding (most frameworks have memory richness but no behavioral validation)
- [ ] Decide: name the FC paper and authors explicitly, or describe it as "a recently published framework"? (The latter is fine for TNS; former gives more credibility if peer-reviewed)
- [ ] Decide how prominently to feature your own authorship of the FC/FSMA work — TNS readers respond well to "the authors of that framework" framing in a bylined piece, less so to anonymous citation
- [ ] One concrete code example would strengthen Section 2 — even 6 lines showing an agent reading its own skill file before choosing a tool call

---

## Word Count Guide

| Section | Target |
|---|---|
| 1. Hook | 150–200 |
| 2. Architectural primitive | 300–400 |
| 3. FC framework | 500–600 |
| 4. History | 900–1,000 |
| 5. The gap | 400–500 |
| 6. Prediction | 300–400 |
| 7. Conclusion | 200–250 |
| **Total** | **2,750–3,350** |







# Introduction

AI agents are evolving very quickly.
Appearing first only two years ago, agents are
evolving quickly to incorporate "meta-cognition",
which refers to various types of self-reasoning
and self-improvement.

Where is the development heading? We argue that self-
reflection will continously increase, because it forms
the base for self-improvement. We predict the tajectory of this
development using a new paper that provides a metric
for self-reasoning and identifies a large catalog of
"self-models" that humans use to hone their performance.


# The MD -> LLM -> MD Loop

- The architectural base of agents is the use of plain
  text files (using markdown syntax or similar)
- MD files natively and seamlessly serve as both input
  and output of LLMs.
- We will argue that this process is driven by the
  reasoning power of large language models, that can
  easily feed their output back into input, allowing
  for a magic loop first popularized by Douglas R.
  Hofstaedter.



# Garbage

We argue that the end-point of this development will
be human-like self-reasoning capabilites


We also show a possible development direction by
using a newly developed metric of self-reasoning
capability called Functional Consciousness and the
list of functional areas of self-improvement derived
from human behavior.

Where will this journey of self-improvement go,
and where will it end? We argue that 

In this article we argue that agents evolve towards
what we call "functional consciousness", by incorporating
increasingly sophisticated 









This is a strong concept for a technical audience. Let me give you honest feedback on the arc and structure before diving into specifics.

## Does the narrative arc make sense?

Yes, fundamentally — but there's a sequencing problem worth fixing.

The current structure asks readers to follow a history *before* they have the conceptual vocabulary to understand what they're looking at. You're saying "agents gained self-models over time" but the reader doesn't yet know what a self-model is. The history section risks reading as a product changelog rather than a coherent argument.

**My recommendation: introduce FC/FSMA *before* the history, not after.**

The structure I'd suggest:

1. Hook — agents are getting eerily self-aware; what's driving that?
2. The architecture insight — the MD→LLM→MD loop as the enabling primitive
3. **FC framework** — here's the vocabulary: self-models, R×P, the 46-domain catalog
4. **History** — now re-read the last 3 years *through* that lens (the "rediscovery" story)
5. Where the gaps are — the 22/46 coverage figure is compelling
6. Prediction — the falsifiable claim about Q4 2026

This makes the history *revelatory* rather than descriptive. Readers will feel like they're seeing something hidden in plain sight.

---

## The "magic loop" framing

The Hofstadter reference in your draft is good instinct, but "magic loop" in a TNS article will make editors nervous. The actual mechanism is more precise and more interesting: LLMs are the first general-purpose text transformers that can *interpret and generate the same format their own context is stored in*. That's the real insight. Markdown files aren't incidental — they're the medium that makes the loop coherent.


---

## The CSV file

I can see the self-models CSV was uploaded but I should read it to give you more specific feedback on the catalog presentation. Let me check what's in it.Good, I can see the full catalog structure. Now let me give you the complete picture.

---

## On the CSV/catalog

The 46 self-models are genuinely the strongest part of your argument — they're concrete enough to be falsifiable and comprehensive enough to be impressive. For a TNS article, you don't need all 46, but you need the **10-domain structure** visible, and you need 3-4 vivid examples per tier to make it tangible. The ones that will land hardest with a technical audience:

- `inf-confidence` — agents that can't hedge appropriately (this is a live pain point)
- `goal-conflict` — the coordination problem in multi-agent systems
- `ethics-drift` — value stability over long-running agents (safety-adjacent, high interest)
- `action-improv` — the Hermes skill-learning story told in one row

---

## Structural recommendation in one diagram

```
Hook (the weirdness)
  ↓
Architecture primitive: MD→LLM→MD
  ↓
Framework: FC + 46 self-models (give them the lens)
  ↓
History (now they can *see* what was happening)
  ↓
The gap: 22/46, here's what's missing
  ↓
Prediction: falsifiable Q4 2026 claim
```

The **22/46 coverage gap** is your killer data point. It makes the future concrete and checkable, which is exactly what TNS readers want. The "declining to act because..." log line as a falsifiable prediction is excellent — keep that.

---

## One structural caution

The Hofstadter "magic loop" framing is intellectually attractive but risks making this feel like philosophy rather than engineering. TNS readers will stay with you if it feels like systems architecture. I'd keep the Hofstadter reference as a one-line aside, not a central metaphor.

Want me to draft a revised introduction section, or a full article outline with section headers and word-count targets for TNS format?















# AI Agent Architecture: Timeline of Self-Model Development 2024-2026

## Overview
Between 2023 and June 2026, the agent industry independently rediscovered and incrementally implemented the core principles of Scene-Based Reasoning (2015) and the FSMA self-model catalog — without knowledge of either framework. This timeline maps that convergence.

---

## 2023: Stateless Foundation (Baseline)

**ReAct Loop becomes standard**
- Agent paradigm: task input → reasoning → tool call → observe → repeat
- Architecture: stateless, session-local, no persistent self-knowledge
- What agents track: nothing about themselves across sessions
- Self-model domains present: ~0-2 (minimal mem-avail at best)

---

## Late 2024: First Persistent Memory Wave

**September 23, 2024: Letta (formerly MemGPT) goes public**
- Research origin: MemGPT paper (UC Berkeley, ICLR 2024)
- Architecture: Three-tier memory (core/recall/archival)
- Key innovation: agent manages its own memory via tool calls
- Self-model domains acquired:
  - `mem-avail` (explicit memory management)
  - `meta-self-awareness` (agent knows what's in its memory blocks)
  - `episodic-memory` (persistent conversation history)
- First evidence: agents can remember who they're talking to across sessions
- Limitation: no self-curation of what to keep; no evaluation of reliability

**November 7, 2024: DeepLearning.AI course on Letta memory**
- Industry signal: memory management becomes a learnable skill

---

## Early 2025: Learning Loop and Skill Emergence

**February 6, 2025: Letta announces "stateful agents"**
- Framing shift: agents as systems that "learn during deployment"
- Introduces heartbeat mechanism: autonomous reflective passes when idle
- Self-model domains added:
  - `meta-reflection` (agent reformulates its own memory during idle time)
  - `action-perform` (executing and logging actions)
  - `goal-tree` (tracking persistent goals)

**February 25, 2026: Hermes Agent released (Nous Research)**
- Architecture: closed learning loop + 4-layer memory
- Key innovation: agents autonomously create reusable "skills" from task execution
- Self-model domains acquired:
  - `action-success` (tracking success/failure of each task)
  - `learn-rate` (creating skills only from proven workflows)
  - `action-tree` (persisting procedural memory across sessions)
  - `meta-accuracy` (implicit: curator layer downweights unreliable skills)
- Performance signal: TokenMix benchmark shows 40% faster execution with 20+ self-created skills
- Self-improvement evidence: agents demonstrably get faster at known task patterns
- **Limitation**: success/failure ratio only; no explanation of *why* something fails

**April 2025 area: Mem0 matures, Zep (Graphiti) launches**
- Competing memory approaches: semantic extraction vs. temporal knowledge graphs
- Still passive extraction; no self-curation

**May 6, 2025: Claude Managed Agents: Dreaming, Outcomes, Multiagent (Anthropic)**
- Dreaming (research preview): background consolidation of agent session memory
- Outcomes: agent evaluates its own output against a rubric, revises if needed
- Multiagent orchestration: one agent delegates to specialized subagents in parallel
- Self-model domains acquired:
  - `meta-consistency` (Dreaming surfaces and consolidates contradictions)
  - `meta-accuracy` (Outcomes framework: agent grades itself iteratively)
  - `goal-conflict` (Multiagent: coordinator tracks subagent goal alignment)
- Limitation: Dreaming is gated/research preview; Outcomes requires human-defined rubric

**October 2025: LangGraph 1.0 GA (LangChain)**
- Architecture: graph-based stateful agent orchestration
- Features: durable execution state, checkpointing, human-in-the-loop
- Self-model domains acquired (by orchestration layer):
  - `action-perform` (explicit graph nodes for each action)
  - `action-tree` (workflows as directed acyclic graphs)
  - `meta-consistency` (graph structure enforces plan coherence)
- Limitation: framework-imposed structure, not agent-learned self-knowledge

---

## Mid-2025 to Present: Specialization and Depth

**November 2025: Hermes Agent desktop app (v0.15.2)**
- Skill improvement becomes autonomous: agents refine their own skill files during use
- Self-model domains deepened:
  - `learn-rate` becomes more precise (agents track skill success rates per condition)
  - `meta-accuracy` becomes explicit (curator layer grades and ranks skills)

**December 2025: LongMemEval published (ICLR benchmark)**
- First systematic evaluation of whether agent self-models actually change behavior
- Finding: most frameworks have rich memory but no behavioral validation

**November 2025-April 2026: Model improvements enable reasoning layers**
- Claude 3.7 Sonnet (Feb 2025): extended thinking
- GPT-5 (April 2026 reports): native reasoning chains
- Impact: agents with reasoning can pre-verify decisions (worst-case analysis potential)

**April 2026: Hermes GEPA self-evolution (ICLR 2026 Oral)**
- Agents now propose *targeted improvements* to skills based on execution traces
- Not just "this failed," but "here's why it failed and here's a fix"
- Self-model domain newly acquired:
  - `inf-hypo` (hypothesis tracking from failure modes)

**May 6, 2026: Claude Managed Agents features expand**
- Dreaming exits research preview (limited availability)
- Outcomes + webhooks become standard
- Multiagent orchestration threadcap raised

**June 2, 2026: Hermes desktop app for mainstream users**
- Reaches 105K GitHub stars (fastest-growing agent framework 2026)
- Skill learning becomes user-facing and visible

---

## What's Still Missing (as of June 2026)

Based on FSMA catalog of 46 self-model domains, the industry has converged on approximately **18-22 domains** across Hermes, Letta, Claude Managed Agents, and LangGraph. Notable gaps:

**Not yet implemented systematically:**
- `action-plan` with repair branches (anticipatory contingency, not just recovery)
- `goal-conflict` explicit detection and resolution (Multiagent has hints, nothing general)
- `action-non-execution` (explicit "I should not do this" logic; agents default to act)
- `inf-confidence` with calibration (agents make claims, rarely hedge appropriately)
- `inf-consistency` with contradiction *resolution* (detect contradictions, no tiebreaker logic)
- Social reasoning domains (`social-tom`, `social-trust`) — require multi-agent interaction data
- Control-layer domains (`attention-focus` management, explicit persistent-goal conflict resolution)

---

## The Convergence Pattern

### Phase 1 (2023-Sept 2024): Stateless → Persistent
- Industry realizes: agents need memory that survives sessions
- Technology: vector DBs, episodic memory, tool-managed memory

### Phase 2 (Sept 2024-Feb 2026): Persistent → Self-Curating
- Industry realizes: memory quality matters; agents should choose what to keep
- Technology: agent-curated skills, reflective passes, rubric-based grading

### Phase 3 (Feb 2026-present): Self-Curating → Self-Correcting
- Industry realizes: agents should improve their own decisions
- Technology: hypothesis tracking, targeted skill improvement, outcome evaluation

### Phase 4 (predicted Q3-Q4 2026): Self-Correcting → Anticipatory
- Industry likely to discover: agents should evaluate worst-case before acting
- Predicted technology: pre-execution cost/impact analysis, explicit non-action
- Convergence signal: when agents start printing "declining to act because..." logs

---

## Key Data Points

| Metric | 2023 | 2025 | 2026 |
|--------|------|------|------|
| Agent frameworks with persistent memory | 0 | 3-4 | 8+ |
| Frameworks with explicit skill learning | 0 | 1 (Hermes) | 2+ |
| Frameworks with rubric-based self-grading | 0 | 0 | 1 (Claude) |
| Agents in production (Gartner survey) | ~5% | 17% | ~30% |
| FSMA domains implemented across all systems | ~2 | ~8-12 | ~18-22 |

---

## SBR/FSMA Alignment

The industry's rediscovery maps cleanly onto SBR's 2015 prediction:

**SBR (2015) predicted agents need:**
- Hierarchical planning with contingency → Found: LangGraph graph structures, Hermes skill trees
- Episodic memory with learning loop → Found: Letta 3-tier, Hermes closed loop
- Attention subsystem with goal tracking → Found: Claude Multiagent, Hermes priority nudges
- Worst-case analysis → **Not yet shipped; predicted next**

**FSMA (recent) operationalizes what "self-models" means:**
- 46 specific domains across Grounding, Richness, Temporal, Integration tiers
- Current coverage: ~22/46 (~48%)
- Trajectory suggests: 28-32/46 by end of 2026

---

## For the TNS Article

**The story:** 
> "Eleven years before anyone talked about agent self-models, a cognitive architecture paper (SBR) predicted they'd be essential. We systematized what those models should look like (FSMA, 46 domains). Now watch as the industry independently rediscovers both — piece by piece, month by month."

**The trend:** 
- Agents are moving from stateless to persistent to self-improving
- Each layer requires explicit domains for self-knowledge
- Industry is currently at ~22/46; the next domains are predictable from SBR logic

**The falsifiable claim:**
- By Q4 2026, at least one major framework will ship explicit worst-case analysis + non-action logic
- When it does, you can verify the prediction by reading code that prints "declining to act because..."






