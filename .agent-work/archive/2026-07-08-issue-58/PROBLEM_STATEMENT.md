# Problem Statement — issue-58 (rev 7)

## Ask

Constellation has no brainstorm-equivalent: nothing serves the upstream creative phase where a raw idea is explored, alternatives are generated wide, excursions (research, prototypes, parallel designs) test them, and a chosen design is hardened into a critically-reviewed spec BEFORE work is cut into issues/epics. Build **two skills** this run, plus one global-doctrine addition:

1. **constellation-explorer** — the upstream shaping loop (superpowers brainstorming is the process reference; Pocock research/prototype/design-it-twice inform the excursion contract).
2. **constellation-prototyper** — throwaway artifact answering one named design question (Pocock prototype is the reference).
3. **Deep-module vocabulary** added to shared global doctrine.

## Resolved design decisions (interrogation 2026-07-07, rev 5)

### Explorer

1. **Lifecycle**: upstream only. The human invokes explorer directly with a raw idea, before any issue/epic exists. Commander's understand step keeps the Interrogator unchanged.
2. **Interrogator seam**: reuse. Explorer's questioning loads constellation-interrogator doctrine and drives engine surveys; explorer adds the creative framing around the shared one-question engine.
3. **Anti-rush doctrine (headline)**: premature convergence is THE failure mode explorer exists to prevent — stated explicitly in the skill. Mechanically: the agent never initiates convergence; it presents each cycle's consolidated ideas and open threads, and only the human says "converge to spec". The agent may flag "this looks ripe" but never in the same message as new findings.
4. **Skill shape — cyclic, not linear**: spine gates entry/exit only: **context → explore (repeatable) → spec → critical review → confirm**. Each exploration cycle is its own survey (`cycle-N.json`): *questions → excursion dispatches → consolidation of ideas*. At each consolidation the human decides: another cycle (any flavor), converge to spec, or shelve.
   - **Cycle flavors** (human-picked at cycle start; agent may recommend): **Shotgun** — pure divergence, a deliberately challenging idea count (default ~20, human-set), cheap one-liners, wild entries sanctioned, light excursions; consolidation clusters + culls, rejects kept on the board with reasons. **DIT/Compare** — 2–5 candidates developed seriously with trade-offs, recommendation-led, excursions per candidate where earned; opinionated comparison, hybrid allowed (home of the superpowers 2–3-approaches pattern). **Refine** — harden one direction: chase open threads, test load-bearing assumptions, tighten interfaces in deep-module terms; consolidation is spec-shaped.
   - Natural arc: shotgun → compare → refine → spec, but flavors are re-orderable and repeatable; a refine that kills its candidate (scoped null) drops back to compare or shotgun — the loop working, not failing.
   - Seed questions belong to the **first** cycle; later cycles inherit the point from the ideas board and seed from its open threads.
5. **Excursion ramps**: explicit off/on ramps. Off-ramp dispatches excursions as background agents, each answering one named question; on-ramp returns findings into the cycle's exploration record before consolidation. **Three excursion types**: *research* (web/academia/codebase, primary sources, cited findings), *prototype* (via constellation-prototyper), *design-it-twice* (see 7).
6. **Approach generation — diverge wide**: no 2–3 cap. As large a list of approaches as the idea warrants, wild ones sanctioned, agents spun off to try them. Convergence deliberate and human-decided. Per-section approval still governs the hardened design at spec time. "Too simple to explore alternatives" stays the named anti-pattern.
7. **Design-it-twice (Ousterhout via Pocock) — both placements**: available as a cycle excursion when interface shape IS the open question, AND standard at spec time for every load-bearing interface: 3+ parallel agents each design the same module's interface under a distinct constraint (minimal interface / max flexibility / common-caller-first / ports-and-adapters), compared on depth, locality, seam placement, testability, with an opinionated recommendation or hybrid. Trivial interfaces skip with a stated reason.
8. **Critical spec review — standard step**: before confirm, a **cold, full adversary** review: the critic reads the spec with NO exploration record, nothing sacred, may attack deliberate decisions; the human filters relitigation noise. **Panel scaled by weight**: default one critic; specs that spawn epics or touch architecture get a 3-lens panel (intent-fit / testability / simplicity-YAGNI); human can dial either way. **Findings routing**: human triages every finding — spec edit / re-open exploration (new cycle, possibly targeted excursion) / reject-with-reason; the confirm gate opens only when every finding has a disposition.
9. **Output contract**: the spec is ephemeral workflow state in `.agent-work/<work-id>/` — NOT durable docs — but it is a **shipped template** (`DESIGN_SPEC.template.md`): the bridge between the ideas board and plan building, written so to-issues/Commander/Admiral consume it directly. Sections: intent; exploration-record digest (cycles, excursion answers incl. scoped nulls, rejected approaches with reasons); chosen design (interfaces in deep-module terms, per-section approval marks); testing pathways; out-of-scope; critic findings + dispositions; Confirmation block (status/date/by).
10. **Hard gate**: engine gate + status marker. The confirm step requires a `user-decision` evidence artifact; the spec carries a Confirmation block; consumer doctrine: only consume a spec whose Confirmation block is filled.
11. **Naming / Admiral**: `constellation-explorer`. No Admiral doctrine touch this run — a confirmed spec may feed to-issues, go directly to a Commander, or be saved for later.
12. **Transcription contract**: the issue tracker is the durable home. At closeout the human routes: (a) cut issues now — spec body incl. Confirmation block transcribed into the issue(s); (b) save for later — spec filed as a single "shaped design" GitHub issue holding the full body. The `.agent-work` copy archives per normal rules.
13. **Living ideas board**: a named `IDEAS_BOARD.md` in the work area is the evolving record of shared understanding — ideas, verdicts, open threads, rejected approaches with reasons. Every cycle's consolidation updates it; the spec crystallizes from it at convergence; a resumed session reads it instead of chat history.
14. **Cycle seed questions**: explorer ships its own starting-questions template (what's the itch, for whom, what does done feel like, what already exists, what would make this pointless), which the Interrogator may aggressively rework per its normal doctrine.
15. **Excursions from either side**: human-initiated ("go look up X") and agent-proposed excursions are equal citizens — same off-ramp record, same on-ramp return into the cycle.
16. **Slow excursions at consolidation**: human's call each time — wait, or consolidate with the excursion logged as an open thread that lands in the next cycle. Never silently dropped.
17. **Mid-exploration shelve**: shelving before any spec exists files the ideas board itself as the shaped-design issue, clearly marked unconfirmed/not-ready-to-cut.
18. **Delta re-confirmation**: after the first full pass, consolidations present *what changed* since the last confirmation, not the whole statement again.
19. **Scoped nulls + optimistic persistence (headline doctrine, both skills)**: a failed excursion/prototype verdict is scoped to the *specific test that ran* — "this spike of X under conditions Y failed" — never generalized to the approach class without evidence spanning it. `PROTOTYPE_RESULT` states what was and was *not* tested. The explorer's posture is optimistic and persistent: keep trying variants rather than declaring something impossible; premature impossibility verdicts are a named anti-pattern.

### Prototyper

13. **Core doctrine (Pocock)**: a prototype is throwaway code that answers one named question — the question decides the shape; question stated in writing before any code; one command to run; no tests/persistence/polish; surface full state after every action; delete-or-absorb when done — the answer is the only thing worth keeping.
14. **Three branches**: *Logic* (interactive TUI over a pure, portable logic module — module liftable, shell throwaway), *UI* (3–5 radically different variants on one route, `?variant=` switcher, prefer mounting inside a real page), *Measurement* (scoreboard defines the metric; each spike implements one mechanism; output is a number on the board — matches existing global spike doctrine).
15. **Location split by driver**: human-driven prototypes (logic TUI, UI variants) in-repo next to real code, clearly marked; agent-driven excursion spikes (measurement, parallel wild ideas) in throwaway worktrees. The handoff states which.
16. **Interface**: `PROTOTYPE_HANDOFF` (one named question, branch, host conventions, stop conditions) / `PROTOTYPE_RESULT` (answer, what it taught, surviving pure module if any, dispose/absorb recommendation) templates. The result is the evidence artifact explorer consumes on its on-ramp.
17. **Closeout rule**: recorded disposition required — deleted, absorbed (with commit), or parked-with-owner. No silent rot. Dispatchable from explorer excursions; also invocable standalone.

### Global doctrine

18. **Deep-module vocabulary** (module / interface / seam / adapter / depth / leverage / locality; interface = everything a caller must know, incl. invariants, error modes, performance) goes **straight into shared global doctrine this run** (`skills/_shared/references/global-everyone.md`) so every role speaks it immediately.

## Protected intent

- The upstream creative phase gets first-class, engine-rigorous support without duplicating the Interrogator — and without forcing linearity onto an inherently cyclic activity.
- **Don't rush to the conclusion**: divergence is cheap and sanctioned; convergence is deliberate and belongs to the human alone.
- The end goal is **deep, testable, and tested pathways**: interfaces described in deep-module terms, design-it-twice guards against first-idea lock-in, and no spec reaches confirm without a cold adversarial review with every finding dispositioned.
- No work is ever cut from an unconfirmed design (mechanical gate, not just prose).
- The spec is used or transcribed, never left as a stale durable doc.
- Prototypes are throwaway by construction; only their answers persist.
- Nulls are scoped, never generic: a failed test kills that test, not the idea class. The explorer keeps trying — impossibility requires evidence, not fatigue.

## Acceptance criteria (from issue #58, as resolved)

- Design decision recorded (seams with interrogator/triage/admiral, output contract, excursion contract) — this document + spine evidence.
- New skill directories `skills/explorer/` and `skills/prototyper/` with SKILL.md + templates as designed, installable via install_constellation.py as `constellation-explorer` / `constellation-prototyper`.
- Deep-module vocabulary added to `global-everyone.md`.
- Hard gate doctrine: no work cut from an unconfirmed design.
- Test suite green (install tests cover both new skills).
