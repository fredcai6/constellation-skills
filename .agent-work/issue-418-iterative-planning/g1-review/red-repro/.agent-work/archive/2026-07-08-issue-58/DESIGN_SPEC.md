# Design Spec — constellation-explorer + constellation-prototyper

## Confirmation

- **Status: CONFIRMED**
- Confirmed by: fredcai6 (human)
- Date: 2026-07-07
- Critic findings dispositioned: YES (3-lens panel 2026-07-07; see Critic findings section — every finding carries a disposition)
- Assumptions exercised: the shaping loop itself (cycles, excursions, cold critic panel, findings triage, delta re-confirmation) was dogfooded live in the shaping session that produced this spec; engine mechanics claims were verified against checklist_engine.py / init_work_area.py / install_constellation.py source by the critic panel.
- Assumptions accepted untested (human-signed): human-only convergence end-to-end and downstream UNCONFIRMED-refusal behavior are doctrine + verifier backstops exercised by the post-merge dogfood drill, not by this run's test suite.

## Intent

Constellation has no upstream creative phase. The Interrogator resolves ambiguity in an *already-cut* ask; nothing serves the stage before: a human with a raw idea who needs to explore what the point is, generate and test alternatives, and harden a chosen design into a spec **before** any issue or epic exists. The absence has a named cost: work gets cut from unexamined first ideas, agents overgeneralize early negative results into "impossible," and premature convergence goes unchallenged.

This design adds two skills and one piece of shared doctrine:

1. **constellation-explorer** — the shaping loop: repeatable exploration cycles with explicit divergence/convergence control held by the human, excursion off/on-ramps to research/prototype/parallel-design agents, and a hard confirmation gate feeding issue-cutting.
2. **constellation-prototyper** — throwaway artifact answering one named design question; only the answer survives.
3. **Deep-module vocabulary** in shared global doctrine, so every role describes interfaces the same way.

The end goal, stated plainly: **deep, testable, and tested pathways**, reached without rushing to conclusions.

## Exploration record (digest)

Shaped over one interrogation (20 recorded findings, `interrogation.json`) plus live dogfooding of the flow itself in the shaping session. Key verdicts:

**Rejected approaches, with reasons:**
- *Durable-docs spec home* (`docs/designs/`): rejected — the spec is used immediately or transcribed; a docs home invites stale design docs. The issue tracker is the durable home.
- *Linear brainstorm pipeline* (superpowers-style explore→approaches→design once through): rejected — exploration is inherently cyclic; re-interrogation is normal, not exceptional.
- *Global 2–3 approaches cap* (superpowers doctrine): rejected as a global rule; recast as the Compare flavor. Divergence sometimes needs ~20 ideas, not 3.
- *Forking the Interrogator's question loop into explorer*: rejected — reuse the one-question engine; explorer adds creative framing around it.
- *Reusing constellation-reviewer as the spec critic*: rejected — a reviewer verifies a change against close criteria; the critic attacks a design cold. Different posture, different brief.
- *Explorer-bundled-only deep-module vocabulary*: rejected — goes straight into `global-everyone.md` so all roles speak it now.
- *Admiral doctrine touch* (confirmed spec as named pre-ruling material): deferred out of scope this run.

**Run-discovered gaps folded in** (from dogfooding the flow while designing it): living ideas board; first-cycle seed questions; excursions initiated by either side; slow-excursion rule; mid-exploration shelve; delta re-confirmation; scoped nulls.

## Chosen design

### 1. constellation-explorer

**Role and tier.** Orchestrator-tier skill (dispatches subagents, talks to the human). Upstream only: the human invokes it directly with a raw idea, before any issue exists. It requires a reachable human by construction — convergence decisions belong to the human alone — so it has **no delegated/autonomous mode**. Work id convention: `explore-<topic>`.

**Headline doctrine (in SKILL.md, in this order):**
1. **Premature convergence is THE failure mode this skill exists to prevent.** The agent never initiates convergence. It presents each cycle's consolidated ideas and open threads; only the human says "converge to spec." The agent may flag ripeness only as a **standalone message containing nothing else** — never alongside findings, options, or any other content.
2. **Scoped nulls, optimistic persistence.** A failed excursion kills *that specific test under those conditions*, never the idea class. Every negative verdict states what was and was NOT tested. Impossibility requires evidence spanning the class; the default next move after a null is another variant, not a closed branch.
3. **Hard gate.** No work is cut from an unconfirmed design. **Mechanism, not just prose**: (a) explorer bundles `verify_spec_confirmed.py`, which refuses unless the Confirmation block is filled (status CONFIRMED, by, date) and no critic-finding disposition cell is empty; the confirm gate's postcondition runs it as a command check. (b) A shelved (unconfirmed) shaped-design issue carries a loud `UNCONFIRMED — DO NOT CUT` header. (c) Commander's understand-step doctrine gains one line: an ask citing a shaped-design spec/issue is verified confirmed (marker visible / verifier passes) before work is cut; an UNCONFIRMED shaped-design issue is never cut. **Trust model stated honestly**: the engine records a `user-decision` rather than cryptographically proving a human made it; explorer has no delegated mode, so fabricating one violates doctrine an agent has no sanctioned path around — the verifier and downstream refusal are the mechanical backstops.

**Spine** (gated, `EXPLORER_SPINE.template.json`, driven through the engine):

| Step | What happens |
|---|---|
| init | work area `explore-<topic>`, engine lease claimed |
| context | global doctrine + project deltas + map read where it exists; seed `IDEAS_BOARD.md` from template |
| explore | repeatable cycles (below); stays in-progress across cycles; closes only on a human converge/shelve decision (`user-decision` evidence) AND a command check: `verify_cycles.py` confirms ≥1 `cycle-N.json` exists and every one carries a non-null consolidation — `explore` cannot close having run zero cycles or with an unconsolidated cycle |
| spec | crystallize `DESIGN_SPEC.md` from the ideas board; per-section approval, delta-based after the first pass; design-it-twice on every load-bearing interface (skip only with a stated reason) |
| review | cold adversarial critique (below); findings live as a **structured table** in the spec with fixed columns `ID | Lens | Severity | Finding | Disposition | Reason` (Disposition ∈ EDIT / RE-EXPLORE / REJECT) — the exact format `verify_spec_confirmed.py` parses; closes only when every Disposition cell is filled — `verify_spec_confirmed.py --phase review` checks this mechanically |
| confirm | hard gate: `user-decision` evidence artifact AND command check `verify_spec_confirmed.py` (Confirmation block filled, no empty disposition cells). The Confirmation block also records **assumptions exercised vs accepted untested** — accepting an untested load-bearing assumption is a visible, human-signed choice, never a silent skip |
| route | human routes the confirmed spec: hand off to to-issues/a Commander (explorer does NOT cut issues itself — to-issues owns cutting) / file one "shaped design" issue holding the full body / shelve unconfirmed (issue carries the `UNCONFIRMED — DO NOT CUT` header); archive work area; release lease |

**Exploration cycles.** Each cycle is its own survey checklist (`cycle-N.json`, from `CYCLE.template.json`), driven with Interrogator doctrine loaded (one question at a time, recommended answers, append/skip, code-answers-over-questions). A cycle has a **flavor**, picked by the human at cycle start (agent may recommend):

- **Shotgun** — pure divergence when direction is unknown. A deliberately challenging idea count (default ~20, human-set) as cheap one-liners; wild entries sanctioned; light excursions only. Consolidation clusters and culls; culled ideas stay on the board with reasons (a cull is a scoped verdict — it can come back).
- **Compare** — 2–5 candidates developed seriously: trade-offs, recommendation-led presentation, excursions per candidate where earned (prototype, measurement, design-it-twice on a contested interface). Consolidation is an opinionated comparison; hybrids allowed. (Home of the superpowers 2–3-approaches pattern.)
- **Refine** — harden one direction: chase open threads, test load-bearing assumptions, tighten interfaces in deep-module terms. Consolidation output is spec-shaped.

Natural arc: shotgun → compare → refine → spec; flavors re-orderable and repeatable. A refine that kills its candidate drops back to compare or shotgun — the loop working, not failing. Seed questions (`EXPLORER_STARTING_QUESTIONS.template.md`: the itch, for whom, what does done feel like, what already exists, what would make this pointless) apply to the **first** cycle; later cycles seed from the board's open threads.

**Excursion ramps.** An excursion is a dispatched investigation answering **one named question**. Off-ramp: an `EXCURSION_BRIEF` (question, type, what "answered" looks like, budget/stop conditions) recorded on the ideas board before dispatch; excursions run as **background** subagents. On-ramp: the result lands in the cycle's record and the board before consolidation. Rules:
- Three types: **research** (web/academia/codebase; primary sources; cited findings), **prototype** (dispatches constellation-prototyper), **design-it-twice** (3+ parallel agents design the same module's interface under distinct constraints — minimal-interface / max-flexibility / common-caller-first / ports-and-adapters — compared on depth, locality, seam placement, testability; opinionated recommendation or hybrid).
- Either side initiates: human ("go look up X") or agent proposal — same brief, same on-ramp.
- **Durability**: excursion dispatches run through the bundled `run_crew.py` (durable registry, result-artifact verification), and `recover_crews.py` is run before each dispatch and before consolidation — the same crash-recovery contract the Commander uses for crews. An in-flight excursion is never lost to a session crash: the registry, not chat history, knows what was running.
- **One brief, no double entry**: `EXCURSION_BRIEF.template.md` is the single dispatch template for all three types; for a prototype excursion its prototype-section fields are **identical to `PROTOTYPE_HANDOFF`'s** (which remains for standalone prototyper use), so nothing is typed twice. Build order enforces this: the prototyper (and its handoff template) ships **before** the explorer's templates, and the explorer review verifies the field alignment against the real file.
- Slow excursion at consolidation time: the human decides — wait, or consolidate with the excursion logged as an open thread carried into the next cycle. Never silently dropped.
- Every excursion verdict obeys scoped-nulls doctrine.

**The ideas board** (`IDEAS_BOARD.md`, from template). The living record of shared understanding: the point; current candidates; verdicts (with scope of what was tested); open threads; rejected ideas with reasons; cycle log. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history; a mid-exploration shelve files *it* as the shaped-design issue, marked unconfirmed.

**Critical review.** Cold, full adversary: the critic reads the spec with **no exploration record**, nothing sacred, and may attack deliberate decisions; the human filters relitigation noise. Panel scaled by weight: default one critic; a spec that would spawn epics or touch architecture gets a 3-lens panel (**intent-fit** — does the design serve the stated point; **testability** — can each pathway be exercised and falsified; **simplicity/YAGNI** — what can be deleted). When in doubt, panel — the trigger biases up, and the human can dial either way. Findings routing: findings land in the spec's structured findings table; the human triages every one — spec edit / re-open exploration (a new cycle, possibly with a targeted excursion) / reject-with-reason. The confirm gate opens only when every disposition cell is filled (mechanically checked, see spine). A critic-driven return to exploration is an engine `reopen` of the explore step. **The spine template carries an inline engine `config` with an effectively-unbounded rework cap** (e.g. 99) — the default cap of 3 would hard-block the loop in any repo without an engine-config file, including this one; a cap defends against runaway autonomous loops and explorer is human-synchronous, so it defends nothing here. Documented cost: `reopen` cascades — spec/review/confirm reset and their evidence is superseded on each return. This is survivable by design: the **ideas board is the source of truth** and the spec re-crystallizes from it; the superseded copies remain in the work area for reference.

**Templates shipped:** `EXPLORER_SPINE.template.json` (with inline engine config), `CYCLE.template.json`, `EXPLORER_STARTING_QUESTIONS.template.md`, `IDEAS_BOARD.template.md`, `DESIGN_SPEC.template.md` (with structured findings table and Confirmation block incl. assumptions-exercised lines), `EXCURSION_BRIEF.template.md`, `CRITIC_HANDOFF.template.md`.

**Scripts bundled (new):** `verify_cycles.py` (explore postcondition: ≥1 cycle, all consolidated), `verify_spec_confirmed.py` (review/confirm postconditions and downstream intake check: Confirmation block filled, no empty disposition cells; loud UNCONFIRMED detection). Both small, single-purpose, fail-visibly, unit-tested. Plus reused: `checklist_engine.py`, `init_work_area.py`, `run_crew.py`, `recover_crews.py`.

**Commander seam (one line, in scope):** Commander's understand-step doctrine gains: an ask citing a shaped-design spec/issue is verified confirmed (`verify_spec_confirmed.py` passes / CONFIRMED marker visible) before any work is cut; an `UNCONFIRMED — DO NOT CUT` shaped-design issue is never cut into work. External consumers (e.g. a user-level to-issues skill) rely on the loud marker.

**Interrogator seam.** Explorer loads constellation-interrogator for its question phases exactly as the Commander's understand step does; the cycle survey is the interrogation survey with flavor framing. No Interrogator changes.

### 2. constellation-prototyper

**Role and tier.** Crew-tier, handoff-driven, no engine checklist of its own (like Triage: doctrine + templates, work the handoff directly). Dispatchable as an explorer excursion, by a Commander, or standalone by the human.

**Core doctrine (after Pocock's prototype skill, adapted):** a prototype is **throwaway code that answers one named question — the question decides the shape**. Question stated in writing before any code. One command to run. No tests, no persistence, no polish. Surface full state after every action. Delete or absorb when done: the answer is the only thing worth keeping.

**Three branches** (reference files: `references/logic.md`, `references/ui.md`, `references/measurement.md`):
- **Logic** — interactive terminal app over a **pure, portable logic module** (reducer / state machine / pure functions; no I/O in the module). The TUI shell is throwaway; the validated module is liftable into real code. For "does this state model / data shape feel right?"
- **UI** — 3–5 **structurally different** variants on one route, `?variant=` switcher, floating cycle bar; strongly prefer mounting inside a real existing page ("an empty route hides design problems a populated one exposes"). For "what should this look like?"
- **Measurement** — a scoreboard defines the metric first; each spike implements **one mechanism**; the output is a number on the board. For "is X actually faster/better?" — aligns with existing global spike doctrine (scoreboard → parallel one-mechanism spikes → synthesis).

**Location split by driver:** human-driven prototypes (logic TUI, UI variants) live in-repo next to the real code, clearly marked, one command to run. Agent-driven spikes (measurement, parallel wild ideas) live in throwaway worktrees. The handoff states which.

**Interface (templates):**
- `PROTOTYPE_HANDOFF.template.md` — the one named question; branch; host-project conventions (runtime, task runner, routing); location (in-repo vs worktree); stop conditions; return format.
- `PROTOTYPE_RESULT.template.md` — the answer; **what was tested and what was NOT tested** (scoped-nulls enforcement lives here); what it taught beyond the question; surviving pure module (if any) and where it lives; disposition recommendation.

**Closeout rule:** a recorded disposition is mandatory — **deleted** / **absorbed** (with commit ref) / **parked-with-owner**. No silent rot.

### 3. Shared doctrine: deep-module vocabulary

Add a concise "Deep-module vocabulary" section to `skills/_shared/global-everyone.md` (the single-source shared file, bundled into every skill's `references/` at install): **module** (interface + implementation, scale-agnostic), **interface** (*everything* a caller must know — invariants, ordering, error modes, config, performance — not just the type surface), **seam** (where an interface lives; its placement is its own decision), **adapter** (a thing satisfying an interface at a seam; one adapter = hypothetical seam, two = real), **depth/leverage** (behavior per unit of interface a caller must learn), **locality** (change and verification concentrate in one place). Plus two working rules: *the interface is the test surface* (wanting to test past it means the module is the wrong shape) and *the deletion test* (delete the module in imagination: if complexity vanishes it was a pass-through; if it reappears across N callers it was earning its keep).

### 4. Install and test integration

- `scripts/install_constellation.py` auto-discovers `skills/*/SKILL.md`; installed names come from frontmatter (`constellation-explorer`, `constellation-prototyper`).
- `SKILL_SCRIPT_BUNDLES`: `"explorer": ("checklist_engine.py", "init_work_area.py", "run_crew.py", "recover_crews.py", "verify_cycles.py", "verify_spec_confirmed.py")`; prototyper needs no scripts.
- `SKILL_REFERENCE_BUNDLES`: `"explorer": _GLOBAL_ORCHESTRATOR`; `"prototyper": _GLOBAL_CREW`.
- `tests/test_install_constellation.py`: both names added to the expected-skills list; bundle assertions for explorer's scripts.
- The vocabulary addition to `global-everyone.md` ships to every skill automatically via the existing reference-bundle mechanism — no installer change needed for it.
- Spine instantiation: `init_work_area.py --spine`'s `resolve_spine` is **extended this run** to a generic `<skill-dir>` token (back-compat: `<commander-skill-dir>` keeps working), so the explorer spine resolves at runtime through the same tested path — not just at install time. Unit-tested; this is a named deliverable, not a gate-time choice.

## Interfaces, in the vocabulary this spec adopts

- **Explorer's interface** to the human: raw idea in → one of three outcomes out: confirmed spec routed (handed to to-issues or a Commander / shaped-design issue filed), or shelved board (unconfirmed issue, loudly marked), or abandoned. Everything else — cycles, flavors, excursions, critics — is implementation behind that seam.
- **Prototyper's interface**: `PROTOTYPE_HANDOFF` in → `PROTOTYPE_RESULT` out. The prototype artifact itself is *not* part of the interface — it is implementation, disposed at closeout. Deep by construction: one question in, one scoped answer out.
- **Explorer→prototyper seam**: the excursion brief/result pair. Prototyper is one adapter at that seam; research agents and design-it-twice panels are others satisfying the same brief-in/finding-out shape. Two-plus adapters: the seam is real.

## Testing pathways

1. **Behavioral tests on the enforcement scripts** (the load-bearing layer): `verify_cycles.py` — passes with consolidated cycles, fails with zero cycles or an unconsolidated one; `verify_spec_confirmed.py` — fails on DRAFT status, empty Disposition cells, or missing Confirmation fields, passes on a filled block; detects the `UNCONFIRMED — DO NOT CUT` marker. These are the mechanical teeth of the hard gate and the review contract — they get real unit tests, not grep checks.
1b. **Verifier↔template cross-check** (`tests/test_explorer_templates.py`): instantiates the explorer spine via `init_work_area.py --spine`, fills a sample DESIGN_SPEC from the shipped template, and runs both verifiers against the artifacts the templates actually produce — the two halves of the hard gate are cross-checked in-suite, not deferred to the dogfood run. (Guards against the verifier parsing a format the template doesn't emit.)
2. **Runtime spine resolution**: `resolve_spine` with the generic `<skill-dir>` token instantiates the explorer spine; the engine can claim/start it and its command-check postconditions reference real script paths (extends `test_init_work_area.py`).
3. **Install tests** (exists, extended): both skills discovered, correct installed names, explorer script bundle present, `global-everyone.md` carries the vocabulary section into every installed skill.
4. **Template validity + doctrine invariants** (cheap extras, not the main coverage): templates parse; SKILL.md files carry the hard-gate, scoped-nulls, and anti-rush text; PROTOTYPE_RESULT carries the "NOT tested" and disposition fields.
5. **Dogfood drill** (post-merge, not this run's gate): first real explorer run records friction to AGENT_FEEDBACK per normal lesson flow. Honest limit, stated: human-only convergence and downstream refusal are doctrine + verifier backstops; their end-to-end behavior is exercised by the dogfood run, not this suite.

## Out of scope

- Admiral doctrine changes (confirmed-spec-as-pre-ruling seam) — deferred; candidate for triage.
- Interrogator changes. (Commander gets exactly one understand-step doctrine line — the shaped-design intake check; no other Commander changes.)
- to-issues/to-prd skill changes (external user-level skills; they rely on the loud UNCONFIRMED marker and the transcribed Confirmation block).
- Making the critical-review pattern standard for other spec-producing flows (e.g. Charter) — candidate for triage.
- A durable docs/ home for specs.

## Critic findings and dispositions

3-lens cold panel (intent-fit / testability / simplicity), 2026-07-07. 25 raw findings deduplicated to 10; every disposition human-approved.

| ID | Lens(es) | Sev | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit, testability | BLOCKING | Hard gate was prose: shelve path files unconfirmed issues nothing downstream checks; user-decision agent-forgeable | EDIT | `verify_spec_confirmed.py` + `UNCONFIRMED — DO NOT CUT` marker + Commander intake line + honest trust-model text (headline doctrine 3) |
| F2 | testability, intent-fit | BLOCKING | Critic-driven reopens hard-block at default rework cap 3; cascade destroys spec/review evidence undisclosed | EDIT | Inline engine config on spine (cap ~99); cascade cost documented — ideas board is source of truth, spec re-crystallizes |
| F3 | testability, simplicity | MAJOR | Cycles had no engine footprint — explore could close with zero cycles (simplicity: drop the surveys instead) | EDIT | `verify_cycles.py` command check on explore close; surveys and flavors kept (deliberate rigor choice) |
| F4 | testability, intent-fit | MAJOR | "Every finding dispositioned" unenforceable; "tested" goal ungated; panel trigger biases down | EDIT | Structured findings table + verifier refuses empty cells; Confirmation block records assumptions exercised vs accepted untested; "when in doubt, panel" |
| F5 | testability | MAJOR | Background excursions had no crash durability (the exact gap run_crew.py exists for) | EDIT | Excursions dispatch via bundled run_crew.py/recover_crews.py |
| F6 | testability | MAJOR | Test suite green over a design that enforces nothing; spine placeholder resolution unbuilt | EDIT | Testing pathways rewritten around behavioral tests of the verifier scripts; `resolve_spine` `<skill-dir>` extension a named deliverable |
| F7 | simplicity | MAJOR | Cut design-it-twice, flavors, global vocabulary, panel scaling; drop explorer's own issue-cutting | PARTIAL | Route simplification ACCEPTED (to-issues owns cutting). DIT/flavors/vocabulary/panel REJECTED: deliberate decisions made with alternatives on the table (exploration record) |
| F8 | intent-fit | MINOR | Vocabulary target path wrong (`_shared/references/` vs `_shared/`) | EDIT | Path corrected |
| F9 | intent-fit | MINOR | Ripeness flag leaks the human-only convergence wall | EDIT | Flag allowed only as a standalone message containing nothing else |
| F10 | intent-fit | MINOR | In-repo throwaway prototypes carry the rot risk rejected for docs-homes | REJECT | Recorded-disposition rule + clear prototype naming is the mitigation; human-driven runnability was the deliberate trade |
