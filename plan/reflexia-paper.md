---
title: "Reflexia: A Text-Based Cognitive Architecture for Self-Reflective Agents"
author: "Frank Bergmann"
date: "2026"
---

# Abstract

This paper describes Reflexia, a cognitive architecture derived from Scene Based Reasoning (SBR) [1] that replaces SBR's 3D scene representation with a text representation, so that the architecture can be implemented directly on top of a large language model (LLM). Where SBR used 3D scene graphs, Description Logic, and STRIPS-style planner states unified under the notion of a "scene", Reflexia unifies the same functional roles — perception, planning, belief, and self-representation — under the notion of a *text-scene*: a structured natural-language description of a world state that includes, as one of its objects, a representation of the agent itself. This "self-object" is what allows Reflexia to reason about its own plans, beliefs, and cognitive history using the same machinery it uses to reason about the external world, without invoking higher-order or modal logic. We describe the Reflexia architecture layer by layer, following the structure of the original SBR paper, and we relate Reflexia's self-object to the Functional Consciousness (FC) framework [8], which supplies a self-model catalog (the FSMA) and a quantitative metric (FCS) for scoring the richness of an agent's self-representation. A reference implementation of Reflexia is underway on Nanobot, an open-source agent runtime.

**Keywords:** cognitive architecture, self-model, meta-reasoning, large language models, self-reflection, introspection, plan reasoning

# 1 Introduction

Scene Based Reasoning (SBR) [1] is a cognitive architecture in the tradition of SOAR [15], ACT-R [2], and ICARUS [16], distinguished by its use of "scenes" — a unification of 3D scene graphs, Description Logic ABoxes, and STRIPS-style planner states — as the single representation on which perception, planning, belief maintenance, and introspection all operate. SBR's central architectural move was not the choice of a 3D representation per se, but the idea that a cognitive architecture should have exactly *one* representation that is expressive enough to serve as the substrate for every subsystem, including the representation of the system's own internal state. SBR called this "gödelization": encoding properties of the reasoning system in the same object-level language used to describe the world, so that a plan, a belief set, or a sequence of cognitive events can be inspected, compared, and reasoned about with the system's ordinary object-recognition and reasoning machinery, rather than requiring a separate meta-language.

Reflexia preserves this architectural move but changes the substrate. Instead of a 3D scene graph, Reflexia represents world states, plans, beliefs, and the agent's own cognitive history as structured text — a *text-scene*. The self-object that SBR located inside a 2D scene diagram is, in Reflexia, located inside the text-scene itself: a natural-language description of the agent, its goals, its beliefs, and its recent cognitive events, situated among the descriptions of the other objects and agents in its environment. This gives Reflexia the same "no modal logic required" property that SBR had: the system does not need a distinct belief operator or a distinct self operator, because beliefs and self-attributes are just further objects and attributes inside the one representation the system already knows how to read and write.

# 2 Why Text: Choosing the Substrate

SBR's authors chose a 3D scene representation because, in 2015, the most tractable path to grounded perception, planning, and object reasoning ran through robotics and computer-vision pipelines: scene graphs, physics engines, and Description Logic ABoxes were the mature tools available for representing an embodied agent's world state. That path required a substantial amount of custom machinery — 3D reconstruction, a description-logic reasoner, a planner operating over sub-scenes — before any reasoning about plans or beliefs could begin.

A decade later, large language models offer a substrate that already performs a large fraction of this work natively. LLMs read and write structured and unstructured text, carry out multi-step symbolic and quasi-logical inference over textual descriptions, track entities and relations across long contexts, and can be prompted to produce and consume the same kind of compact, structured descriptions that SBR built by hand out of scene graphs and DL ABoxes. Rather than converting sensor data into a 3D graph so that an object-recognition and DL-reasoning stack can operate on it, an LLM-based architecture can operate directly on a textual description of the scene, using the model's own capacity for entity tracking, relation extraction, and multi-step inference in place of a bespoke reasoning stack. This is the central design bet behind Reflexia: for a cognitive architecture whose reasoning, planning, and introspection subsystems are meant to be implemented on top of an LLM, a text-scene is a more direct substrate than a 3D scene, because it removes the translation layer between "what the model natively reasons over" and "what the architecture represents world state as." The gödelization move that made SBR's self-model possible carries over unchanged, and in fact becomes simpler: encoding the system's own plans and cognitive events in natural-language text is no harder than encoding them in a 2D scene diagram, and the same LLM that reasons about the external world can reason about the text-scene's self-object without any special-purpose visual or spatial reasoning subsystem.

# 3 Related Work

Reflexia is a direct descendant of SBR [1], from which it inherits the plan/scene duality, the use of "active tasks" with execution statistics, and the gödelization principle for self-representation. It shares SBR's family resemblance to SOAR [15], ACT-R [2], and ICARUS [16], particularly ICARUS's grounding of plans in observable attributes and its roadmap toward social cognition [17].

Where SBR's closest neighbors were robotics and planning systems, Reflexia's closest neighbors are LLM-based agent frameworks and agent runtimes that use natural-language scratchpads, memory stores, and tool-calling loops as their working representation. Reflexia differs from typical agent scaffolding in the same way SBR differed from typical planners: rather than treating the agent's own state (goals, beliefs, recent actions) as a separate bookkeeping structure outside the model's reasoning loop, Reflexia folds that state into the same text-scene representation used for the external world, so that self-reflection and self-reasoning use the identical inference machinery as ordinary world reasoning.

Reflexia's treatment of self-representation is grounded in the Functional Consciousness (FC) framework [8], which independently developed a catalog of self-model domains (the Functional Self-Model Architecture, or FSMA) and a metric (FCS) for scoring how rich and how well-reasoned-over a system's self-model is. We treat FC as providing the self-model *content* and *metric* that Reflexia's self-object needs to be scored against, while Reflexia itself is concerned with the architectural question of how such a self-object is represented and kept in sync with an LLM-based reasoning loop. Section 6 elaborates this relationship.

# 4 Architecture Overview

Reflexia retains SBR's four-layer structure, with each layer's subsystems re-targeted from scenes to text-scenes.

**Interface layer.** Converts raw input (user messages, tool outputs, sensor or API data) into text-scene updates, and converts planner output back into executed actions or tool calls.

**Planner layer.** Creates, recognizes, and executes plans represented as structured text (in place of SBR's HTN task trees over scenes).

**Reasoning layer.** Implements operations over plans and beliefs, including the self-object, using the LLM's native inference capabilities in place of a separate Description Logic reasoner.

**Control layer.** Maintains persistent goals, a portfolio of active plans, and a focus of attention over the text-scene, including the self-object.

## 4.1 Subsystems

**Text-Scene Construction.** Converts interface-layer input into a text-scene: a structured natural-language description of the current world state, analogous to SBR's 3D-reconstruction subsystem but operating directly on text (or on text produced by upstream perception components) rather than on sensor geometry.

**Reflexia Planner.** Takes as input an initial text-scene and a goal (expressed as a target sub-scene, i.e., a partially specified description of a desired end state) and returns candidate plans as structured task decompositions, together with confidence scores, in the same way the SBR planner returned HTN tasks over sub-scenes.

**Prediction Subsystem.** Predicts the likely evolution of objects, agents, and the self-object within a text-scene, providing Reflexia with a textual "what-if" sandbox in place of SBR's physics-based simulation. Because objects and agents are already described in natural language, the LLM itself can be used to simulate plausible continuations of a text-scene, including the likely reactions of other agents described in it.

**Episodic Memory.** Stores past text-scenes, key frames, and plan executions, indexed by the entities and relations they contain, for later retrieval during planning and belief revision — functionally identical to SBR's episodic memory [13], now indexed over text rather than scene-graph content.

**Plan Reasoning.** Implements comparison, abstraction, merging, and optimization of plans, using the self-object's own record of past plan outcomes rather than a separate meta-planning subsystem.

**Belief Reasoning.** Maintains the agent's beliefs about the world and about other agents as attributes within the text-scene, together with confidence scores, replacing SBR's Description Logic subsystem with the LLM's native capacity for tracking and revising natural-language claims. Beliefs about other agents' beliefs are represented the same way SBR represented them: as a further text-scene, "spawned" from the perspective of the other agent, supporting "what-would-they-do" analysis without recourse to modal logic.

**Attention Subsystem.** Maintains persistent goals, a portfolio of plans, and a focus of attention that can be directed either at the external portion of the text-scene or at the self-object, tracking execution and triggering re-planning — unchanged in function from SBR, only in substrate.

## 4.2 Data Structures

**Objects.** Named entities described by a set of natural-language attributes (key–value pairs, where values may be strings, numbers, or references to other objects), corresponding to SBR's untyped attribute objects.

**Agents.** Objects that additionally carry a goal hierarchy and a set of beliefs, used to represent humans, other software agents, and the Reflexia system itself.

**Relations.** Named, directed associations between two objects, expressed as short natural-language predicates rather than as spatial or DL-role edges.

**Text-Scenes.** The core representation. A text-scene can be defined formally as a triple

$$
\mathcal{T} = \langle O,\; R,\; s \rangle
$$

where $O$ is a set of objects (including agents), $R$ is a set of relations over $O$, and $s \in O$ is a distinguished *self-object* describing the Reflexia agent's own goals, beliefs, plans, and recent cognitive events. The self-object is not a separate data structure or a different representation level; it is an ordinary member of $O$, subject to the same reasoning operations as any other object. This is the direct analogue of SBR's use of 2D scene diagrams to gödelize the system's own plans and beliefs: in Reflexia, no diagram-rendering step is required, because natural language is already a representation the system's reasoning subsystems operate over natively.

**Sub-Scenes.** Text-scenes with only partially specified attributes, used as goal descriptions and as the pre- and post-conditions of plan actions, exactly as in SBR.

**Plans.** A root task decomposed into a tree of sub-tasks, each optionally carrying execution statistics drawn from episodic memory, following SBR's "active task" formulation [1].

# 5 Self-Reflection and Self-Reasoning

The purpose of the self-object $s$ is to let Reflexia apply its ordinary reasoning operations — recognition, comparison, abstraction, simulation — to its own plans, beliefs, and history, rather than requiring a dedicated introspection mechanism. Concretely, this means: a completed or failed plan can be inspected and compared against other plans in episodic memory in the same way an external event is compared against remembered scripts; a sequence of recent cognitive events (a shift in attention focus, a belief update, a planning failure) can be described as attributes of $s$ and reasoned over as a small text-scene in its own right; and beliefs the system holds about its own competence or about the likely success of a plan can be revised using the same belief-reasoning subsystem used for beliefs about the external world.

This gives Reflexia a form of self-reasoning that is deliberately narrow in scope: it does not claim to model subjective experience, and the architecture makes no commitments about what, if anything, it is like to run a Reflexia agent. What it does provide is a mechanism by which an agent's model of itself — its goals, its beliefs, its record of past plans and their outcomes — is represented in the same substrate, and manipulated by the same operations, as its model of everything else. Scoring how rich and how well-integrated that self-representation is, and cataloging which domains of self-modeling it covers, is the job of a separate framework, to which we turn next.

# 6 Relation to Functional Consciousness

The Functional Consciousness (FC) framework [8] independently addresses the question of what it means for a system's self-model to be rich, and proposes a metric, FCS, defined as the product of a self-model breadth term $R$ and a reasoning-power term $P$, together with the Functional Self-Model Architecture (FSMA) — a catalog of self-model domains against which a given system's self-object can be checked for coverage. Reflexia and FC are complementary rather than overlapping: Reflexia specifies *how* a self-object is represented and kept available to an LLM-based reasoning loop, while FC specifies *what* such a self-object should ideally contain and *how richly reasoned-over* it is. A Reflexia self-object can, in principle, be scored under FCS by checking its coverage of the FSMA catalog and the depth of reasoning the system applies to it, giving Reflexia a concrete, external target to design toward rather than an informal notion of "good self-representation."

Comparing the two catalogs briefly: Reflexia's self-object, as described in Section 4.2, directly realizes a subset of FSMA domains out of the box — goals and the persistent goal hierarchy, beliefs and their confidence scores, plan history and execution statistics, and attention focus all map onto FSMA domains in a fairly direct way, since they were already first-class attributes of SBR's self-model before FC's catalog existed. Other FSMA domains — for instance those concerned with resource or capability self-models, or with modeling the reliability of the system's own perception and reasoning subsystems — are not automatically populated by the base Reflexia architecture and would need to be added as further attributes of $s$ or as additional subsystems feeding it. In this sense the FSMA catalog functions as a checklist for extending Reflexia's self-object over time, and FCS provides a way of tracking how that extension changes the agent's measured self-model richness as new domains are added.

# 7 Implementation

A reference implementation of Reflexia is underway on Nanobot, an open-source agent runtime in the OpenClaw lineage. Nanobot's existing skill-based execution loop provides a natural home for the Interface and Control layers described in Section 4: skills correspond to Interface-layer actions, while the Planner and Reasoning layers are implemented as a small set of additional skills that read and write the text-scene, including the self-object, as part of each reasoning step. This mirrors the relationship SBR had to its own TinyCog reference implementation [1]: the architecture is defined independently of any one implementation, but a concrete, runnable system is used throughout development to validate that each subsystem's textual interface is sufficient in practice, not only on paper.

# 8 Conclusion

Reflexia carries SBR's central architectural commitment — a single representation expressive enough to encode both the external world and the system's own plans, beliefs, and cognitive history — forward into an LLM-native substrate. By replacing 3D scene graphs and Description Logic with structured text, and by locating the self-object as an ordinary member of the text-scene rather than in a separate representation, Reflexia preserves SBR's "no modal logic required" approach to belief and self-representation while removing the substantial machinery SBR needed to build and maintain its 3D scene representation. The FC framework's FSMA catalog and FCS metric give Reflexia's self-object a concrete external standard to be extended toward and measured against, and an initial implementation on Nanobot provides a testbed for validating the architecture in practice.

# Acknowledgment

This paper builds directly on the original Scene Based Reasoning architecture developed with Brian Fenton [1].

# References

1. Bergmann, F., Fenton, B.: Scene Based Reasoning. In: Proceedings of the 8th Conference on Artificial General Intelligence (AGI-2015) (2015)
2. Anderson, J.R., Lebiere, C.: The Newell test for a theory of cognition. Behavioral and Brain Sciences 26(05), 587–601 (2003)
3. Brachman, R.J.: What's in a concept: structural foundations for semantic networks. International Journal of Man-Machine Studies 9(2), 127–152 (1977)
4. Carberry, S.: Techniques for plan recognition. User Modeling and User-Adapted Interaction 11(1–2), 31–48 (2001)
5. Fikes, R.E., Nilsson, N.J.: STRIPS: A new approach to the application of theorem proving to problem solving. Artificial Intelligence 2(3), 189–208 (1972)
6. Ghallab, M., Nau, D., Traverso, P.: Automated Planning: Theory & Practice. Elsevier (2004)
7. Goertzel, B., Pennachin, C., Geisweiller, N.: Engineering General Intelligence, Part 1. Springer (2014)
8. Bergmann, F.: Functional Consciousness: A Self-Model Catalog and Metric for Reasoning Systems. In: Proceedings of the 19th Conference on Artificial General Intelligence (AGI-2026) (2026, forthcoming)
9. Metzinger, T.: Being No One: The Self-Model Theory of Subjectivity. MIT Press (2003)
10. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Ł., Polosukhin, I.: Attention is all you need. In: Advances in Neural Information Processing Systems 30 (2017)
11. Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q., Zhou, D.: Chain-of-thought prompting elicits reasoning in large language models. In: Advances in Neural Information Processing Systems 35 (2022)
12. Konolige, K., Nilsson, N.J.: Multiple-agent planning systems. In: AAAI, vol. 80, pp. 138–142 (1980)
13. Veloso, M., Carbonell, J., Perez, A., Borrajo, D., Fink, E., Blythe, J.: Integrating planning and learning: the PRODIGY architecture. Journal of Experimental & Theoretical Artificial Intelligence 7(1), 81–120 (1995)
14. Jiménez Celorrio, S.: Planning and learning under uncertainty. Ph.D. thesis, Universidad Carlos III de Madrid (2011)