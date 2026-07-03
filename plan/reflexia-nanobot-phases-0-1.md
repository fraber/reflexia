# Reflexia / Reflexia on Nanobot — Phase 0 & Phase 1 ToDos

This supersedes the generic Phase 0/1 sketch in the original MVP plan. The
Reflexia world-simulation spec (`aria-world-simulation.md`) is now the source of
truth for file names, schemas, and world logic — the earlier `self/self_model.json`
sketch is replaced by Reflexia's actual file set: `SOUL.md`, `MEMORY.md`,
`RELATIONS.md`, `HYPOTHESES.md`, `PLAN.md`, `WORLD.md`, `messages_inbox.md`.

Scope note: Phase 1 targets **TC-001** and **TC-002** only (alice + bob, at
Market/Fields/Workshop). Carlos, the Archive, the dry-season mechanic, and the
archive-closing rumor are intentionally deferred to Phase 2, which is where
the "informant / hypothesis-tracking" behavior (TC-003 onward) lives — this
keeps Phase 1 to a provably-working two-agent trade loop before the
information-asymmetry mechanics are layered on.

---

## Phase 0 — Scaffolding

### 0.1 Docker + repo setup
- [ ] Fork `HKUDS/nanobot` into your own GitHub repo.
- [ ] Write a `Dockerfile` that installs the forked Nanobot (`pip install -e .`) plus Python deps needed for the world engine (no extra deps beyond stdlib + `pydantic` or similar for JSON-schema validation should be needed at this stage).
- [ ] Write a `docker-compose.yml` that:
  - Mounts the forked Nanobot repo **and** a separate `reflexia-sim/` project directory (world engine + agent workspaces) as bind mounts, so edits from Antigravity on the host are reflected live in the container.
  - Exposes whatever port Nanobot's WebUI/gateway needs, even if unused in Phase 0/1 (useful later for watching agents interact).
  - Passes through the LLM provider API key(s) as environment variables (don't bake into the image).
- [ ] Confirm `nanobot onboard` runs cleanly inside the container and produces a default workspace, as a smoke test that the container + forked package are wired correctly.
- [ ] Confirm you can run a single Nanobot agent turn from inside the container via the Python SDK (not just the CLI/chat loop), since Phase 1's `agent_tick.py` needs to drive agents programmatically rather than interactively.

### 0.2 Repo layout
- [ ] Create the top-level `reflexia-sim/` project structure:
  ```
  reflexia-sim/
    world/
      world_tick.py         # stub, no logic yet
      world_state.py        # in-memory World object (food pool, tick, archive flags)
      WORLD.md               # generated, not hand-authored
    agents/
      alice/
        SOUL.md               # from spec §2.3
        AGENTS.md              # Nanobot instructions, references Reflexia framing
        MEMORY.md               # empty, Nanobot-managed
        RELATIONS.md             # stub, populated in 0.3
        HYPOTHESES.md             # stub (used from Phase 2 on, but scaffold now)
        PLAN.md                    # stub
        messages_inbox.md           # empty
        inventory.json                # {food, tools, knowledge, energy}
      bob/  (same structure)
      carlos/  (same structure, unused until Phase 2 — scaffold only)
    orchestrator/
      tick_loop.py           # drives world_tick → agent_tick(alice) → agent_tick(bob) → agent_tick(carlos)
      agent_tick.py            # stub, no context assembly yet
      schema.py                 # JSON schemas for move/trade/message/work/farm/rest/teach + validator
    tests/
      test_world_tick.py
      test_schema_validation.py
  ```
- [ ] Write `SOUL.md` for alice and bob directly from spec §2.3 (personality, aptitude, starting goal) — carlos's SOUL.md can be scaffolded but isn't exercised until Phase 2.
- [ ] Populate each agent's `inventory.json` with the starting inventories from spec §2.3 (alice: food=40/tools=0/knowledge=1; bob: food=50/tools=2/knowledge=0).
- [ ] Populate each agent's `RELATIONS.md` with the default trust vector from spec §2.3 (`{competence: 0.5, values: 0.5, communication: 0.5}` for every other known agent).

### 0.3 Action schema + validation
- [ ] Implement `schema.py` with JSON-schema (or `pydantic`) models for all seven action types in spec §3: `move`, `trade`, `message`, `work`, `farm`, `rest`, `teach`, plus the `trade`-response schemas (`accept`/`counter`/`decline`).
- [ ] Write a validator function `validate_action(raw_json) -> Action | ValidationError` that Phase 1's `agent_tick.py` will call on every LLM output — this is the boundary that keeps malformed agent output from ever reaching `world_tick.py`.
- [ ] Unit test the validator against every example action JSON already given in the spec (§3 and the Example 1/2 transcripts) — these are free test fixtures, use them.

### 0.4 Logging
- [ ] Decide the log format for `WORLD.md`'s "Recent Events" section (spec keeps only the last 5 — §4 point 6) and implement a `world_events.py` append/prune helper now, since almost everything downstream writes to it.
- [ ] Add a separate full-history JSONL log (`run_log.jsonl`) outside of `WORLD.md`, so that ground-truth test-case checks (which need more than the last 5 events) don't depend on parsing a pruned markdown file.

**Phase 0 exit criteria:** container builds and runs; a hand-crafted fake tick (calling `agent_tick.py` with a hardcoded action) can be validated by `schema.py`, written to the JSONL log, and reflected in a regenerated `WORLD.md` — with **no LLM calls and no real world logic yet**. This proves the plumbing before any agent intelligence enters the picture.

---

## Phase 1 — Minimal World Engine (TC-001, TC-002)

### 1.1 `world_tick.py` — deterministic core
- [ ] Implement the pseudocode from spec §4 exactly, scoped down: resource consumption (`food -= 3/agent/tick`), world food pool update, tick counter increment, `WORLD.md` regeneration. **Skip** the dry-season branch, archive-visitor-capacity reset, and archive-rumor injection for now (Phase 2) — but leave clearly marked hook points (`# PHASE 2: dry season`, `# PHASE 2: archive rumor`) so they're easy to slot in later without restructuring.
- [ ] Implement Fields production (5 food/tick, 6/tick for bob) and Workshop production (0.3 tools/tick, 0.36 for alice) as pure functions, triggered by the `farm`/`work` actions from Phase 1.3.
- [ ] Implement energy: `rest` restores 10 energy over 3 ticks; `work`/`farm` cost 3 energy each — enough energy bookkeeping to make the `rest` action meaningful, without building out a full "soft limit on simultaneous actions" mechanic yet (spec only calls this a soft limit, not a hard gate — treat energy as informational/logged for Phase 1, not action-blocking).
- [ ] Unit test `world_tick.py` in isolation against the exact numbers in Example 1's "Ground truth checks" (alice.food = 37 − 10 − 3 = 24, etc.) and Example 2's (alice.food = 29 − 3 = 26 on a declined trade) — these two blocks are effectively pre-written test oracles for TC-001/TC-002.

### 1.2 Locations and movement
- [ ] Implement Fields, Market, Workshop, Commons as valid `move` targets (Archive excluded until Phase 2).
- [ ] Enforce "movement costs 0 resources, takes 1 tick" and "agents can only observe events at their current location" — this location-filtering is explicitly called out in spec §8's failure-mode table ("All agents have identical MEMORY.md → Location filter not working"), so build the filter as its own testable function (`filter_visible_events(location, all_events) -> list`) rather than inline logic, and unit test it directly against that failure mode.

### 1.3 `agent_tick.py` — context assembly + Nanobot invocation
- [ ] Implement context-bundle assembly per agent per tick: `SOUL.md` + `AGENTS.md` (static) + location-filtered `WORLD.md` excerpt + own `inventory.json` + own `RELATIONS.md` + unread `messages_inbox.md` entries + recent `MEMORY.md` entries.
- [ ] Wire this bundle into a single Nanobot agent turn via the Python SDK (built in Phase 0.1), parse the raw output through `schema.py`'s validator, and re-prompt once on validation failure before hard-failing the tick (matches Nanobot's existing tool-call retry conventions).
- [ ] Implement the fixed tick order from spec §2.4: `world_tick.py` runs, then `agent_tick(alice)`, then `agent_tick(bob)` — carlos excluded from the loop until Phase 2.

### 1.4 `trade_handler.py` — the only cross-agent action needed for TC-001/TC-002
- [ ] Implement `trade` proposal → next-tick `accept`/`counter`/`decline` response cycle, including `expiry`.
- [ ] On `accept`: apply the resource exchange, update both agents' `inventory.json`, and apply the trust-vector deltas from spec §2.3 ("competence ±0.1 on delivery/failure, values ±0.05/±0.2 on fair/unfair action") to both agents' `RELATIONS.md`.
- [ ] On `decline`: apply **no** resource change, but still allow the trust-vector update path to fire later if a `message` action follows (this is exactly TC-002's mechanic — bob declines, then sends a message, and *that's* what triggers alice's `values +0.1` update, on the next tick after she reads it).
- [ ] Implement `messages_inbox.md` delivery: a `message` action writes into the target's inbox file, available to that agent starting next tick — this is required for TC-002's bob→alice message and its delayed trust effect.

### 1.5 Minimal reflection (required for TC-002)
- [ ] TC-002 explicitly depends on "bob's MEMORY.md contains reflection from tick 10." Implement the simplest version of spec §2.4's "every 10 ticks" reflection: after tick 10's agent turns complete, trigger one additional Nanobot turn per agent whose only job is to summarize the last 10 ticks of that agent's own `MEMORY.md`/event log into 1–3 sentences, appended back into `MEMORY.md` as a labeled reflection entry.
- [ ] Don't build the full reflection pipeline (goal revision, `PLAN.md` updates, strategy pivots — those belong to TC-005/Phase 3+). Phase 1's reflection only needs to produce the kind of note the spec shows ("alice's food is frequently low; accepting food-for-tools when she is below 30 may harm her") so that TC-002's bob decision can actually reference it.

### 1.6 End-to-end validation
- [ ] Run TC-001 end to end (ticks 5–6, alice ↔ bob first trade) and check against spec §5 Example 1's exact pass criterion: inventory arithmetic exact, both trust vectors updated, event logged to `WORLD.md` and both `MEMORY.md` files.
- [ ] Run TC-002 end to end (ticks 15–16, declined trade + message + delayed trust update) and check against Example 2's pass criterion.
- [ ] Run both as automated tests with a fixed seed / fixed scripted scenario (per the earlier MVP plan's "same seed across conditions" principle) so they can be re-run in CI as the world engine grows in Phase 2+.

**Phase 1 exit criteria:** TC-001 and TC-002 pass automatically, with real Nanobot agent turns (not scripted/mocked actions) driving alice and bob, and `world_tick.py` remaining 100% LLM-free per spec §4's "critical rule."

---

## Deferred to Phase 2 (do not build yet)
- Carlos, the Archive, archive capacity/closing, the tick-20 rumor injection, dry season (ticks 30–50) — these are exactly the mechanics that TC-003 onward (and the earlier MVP plan's "informant/trust-calibration" Test Case B) depend on, so Phase 2 should pick up directly with carlos + Archive once Phase 1's two-agent loop is solid.
- `HYPOTHESES.md` population/update logic (`inf-hypo` domain) — file is scaffolded in Phase 0 but stays empty until carlos and the rumor mechanic exist.
- `teach` action — not exercised by TC-001/TC-002, deferred with carlos.
