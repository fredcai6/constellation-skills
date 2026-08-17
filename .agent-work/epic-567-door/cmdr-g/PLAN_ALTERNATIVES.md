# Plan alternatives: convergence

## The one thing being designed twice
The gate plan for `finish_work` (working name `spine_done`'s underlying orchestration) in `scripts/spine_lifecycle.py`: how much of #574's verify->close->reap->archive->dispose sequence one call actually drives.

## Count and panel
2 candidates, single pass (not a 3-lens panel): the design space is narrow (one file owned, two fenced files read-only, the mechanism already largely reverse-engineered during interrogation), so a fairly-easy call rather than an architecture-spanning one. Named constraints: SMALLEST-DIFF (candidate A) and MOST-TESTABLE/full-contract-coverage (candidate B). A third "common-caller-first" candidate is named as an untaken road below rather than run, since both A and B already converge on the same caller shape (a single `finish_work(spine_path, ...)` call) and differ only in how much of the sequence it drives -- a third candidate would not surface new structure, only restate the same axis.

## Candidates
Written independently (forked with shared research context, diverged under distinct constraints) to `.agent-work/epic-567-door/cmdr-g/PLAN_CANDIDATE_A.md` and `PLAN_CANDIDATE_B.md`.

- **A (smallest-diff)**: `finish_work` does NOT drive the final `advance` -- only release/reap/archive/dispose. Smaller, but self-scores its own gap: "this is the smallest diff, not the smallest gap" -- it leaves exactly the failure mode #574 was opened to close (a still-manual `advance` call an agent can still skip).
- **B (most-testable / full coverage)**: `finish_work` drives verify -> advance (mechanical) -> release -> reap -> child-plan release -> archive -> dispose, composed from four independently-testable sub-functions (`done_refusal`, `_advance_and_release`, `force_reap`, `_release_child_plans`). Genuinely delivers "the agent says I'm done, the engine does the rest" -- Tommy's actual ruling quoted in the launch order's Mission.

## Recommendation
**Candidate B**, with candidate A's one real contribution folded in as a mitigation, not a separate diff: A correctly flags that the `advance` call is the piece most exposed to lane A's checklist_engine.py rewrite landing first (CLI flag shape could change). B already isolates that call inside one small function, `_advance_and_release` -- so this run adopts B as designed (the isolation A would have bought by omission, B already buys by seam placement) rather than authoring a third hybrid.

Axis-by-axis: A and B tie on locality (both land entirely in spine_lifecycle.py + one new CLI file + tests, zero fenced-file touches) and both score well on testability, but B wins depth and seam placement outright -- A's own risk section admits it does not satisfy the mission's actual point (one call, not one-and-a-half). Rejecting A's premise ("cut the riskiest piece") in favor of containing that risk (isolate it, don't omit it) is the deciding call.

## Untaken-road record
- A third, common-caller-first candidate: not run. Both landed candidates already converge on the same caller shape (`finish_work(spine_path, *, root, session_id, today, ...)`); the only axis in dispute was scope (how much of the sequence is driven), which A and B already bracket. A third candidate on the same axis would not surface new structure.
- Sweeping the 41 pre-existing stale leases: named out of scope in the mission frame, not planned as a gate at all (separate question per the launch order's `decision:new-rot-first-old-rot-maybe`).

## Panel-vs-single record
Single pass, 2 candidates -- surfaced here per design-it-twice doctrine. Rationale: fairly-easy call, not architecture-spanning (one owned file, fenced files touched only via existing library entry points already proven safe by mcp_spine_server.py's own established pattern). If a cold critic below finds this scoping wrong, escalate to a 3-lens panel before finalizing.

## Cold-critic disposition (added after convergence, before plan freeze)

A cold critic (fresh subagent: mission frame + both candidates + source ground
truth only, no authoring context) returned **approve-with-fixes** on Candidate B
with three BLOCKING findings. The Commander **independently verified all three
against source** before accepting them (inherited doctrine: never accept a
claimed side-effect on the strength of the claim). Full report:
`PLAN_CRITIC.md`. Dispositions, all folded into `execute.json` before freeze:

1. **BLOCKING, CONFIRMED, fixed in g1** -- `advance --mechanical` can be flatly
   refused. `advance()`'s `require_why` is computed LIVE at the CLI boundary from
   `_trip_hard_band_reading(...)` (`checklist_engine.py:2519-2534`, wired at
   `_run_verb:3361-3370`), not from any caller flag, and at/over the HARD context
   band it refuses `--mechanical` outright. Plausibly the very scenario #574
   cites ("closeout refused at 23% context"). Fix: `finish_work` takes a `why`;
   `--mechanical` is never assumed; a refused advance returns the engine's own
   text verbatim as the one actionable refusal and never proceeds to release. A
   dedicated HARD-band fixture test is now a g1 close criterion.
2. **BLOCKING, CONFIRMED, fixed in g3** -- ordering inversion. B had
   `force_reap` before `_release_child_plans`, but `_reap_binding_entries`
   (`spine_rail.py:311-366`) only drops entries whose target reads
   `status == "released"`, so children still active at reap time survive it --
   reproducing the exact #552 staleness this run exists to end. Fix: order is now
   children-released -> top-level advance+release -> reap -> archive -> dispose,
   which also keeps the top spine's own release its last journaled action.
3. **BLOCKING, CONFIRMED, fixed in g2** -- child release self-authorized and
   "never touch a live spine" was unenforced. Echoing a child's own
   `engine_session.session_id` back to `release()` makes its ownership check
   (`checklist_engine.py:1133-1147`) tautological, and directory-proximity-only
   child identification could seize a lease another working agent genuinely
   holds. Fix: three shipped runtime guards -- lineage-based identification (a
   child must be DECLARED by some task's `child_checklist`; an unclaimed
   active-leased file is reported, never released), honest non-owner release via
   `--force --reason` so the override is recorded, and realpath containment so a
   symlink cannot reach outside the work area.
4. **SHOULD-FIX, CONFIRMED, fixed in g1** -- in-process `main(argv)` calls were
   unguarded against `SystemExit` (argparse exits 2; `main()` catches only
   `EngineError`). Fix: one `_engine_call` choke point catching both.
5. **SHOULD-FIX, accepted** -- A's rejection was argued on the weaker axis. The
   critic is right that A's real advantage is structural: never calling `advance`
   means it cannot hit finding 1 at all. Recorded honestly here rather than
   quietly re-argued. B is still adopted, but it now adopts A's insight instead
   of ignoring it: because a why-less close is refusable, `finish_work` treats
   the advance as a step that can legitimately refuse and hands the caller one
   actionable message, rather than presuming it always succeeds. B keeps full
   one-call coverage; A's structural safety is bought with the `why` parameter
   and the verbatim-refusal path, not with a narrower verb.
6. **NIT, fixed in g3** -- refusal shape now specified: `finish_work` returns
   `{ok: False, refusal, stage}` and never raises for a normal closeout refusal.

No finding was rejected. No finding was deferred.
