# Design-it-twice Brief: ExternalBackend spine-verification fix

## The one thing being designed twice
How `run_crew.py`'s ExternalBackend verification path proves a dispatched crew actually
drove an engine-gated checklist, instead of accepting a fresh result-artifact mtime alone.

## Count and panel -- a surfaced choice
**1 authored candidate + 1 named untaken road**, not a 2-agent parallel fan-out. This is a
fairly-easy call (single file, well-understood existing precedent in `finalize_from_exit_code`
for the CLI backend's spine-aware verdict), scaled per "a fairly-easy call may run two
candidates or a single with the alternatives named as untaken roads." No parallel dispatch
spent on a second full candidate; the real second option (mandatory `--spine`) is compared
below and rejected for a stated, load-bearing reason rather than silently dropped.

## Candidate A (adopted): optional `--spine`, AND semantics, loud report when absent
`ExternalBackend.dispatch()` stops refusing `--spine` -- accepts it as a *verification-only*
target (still never bound; nothing spawns to bind it into). `verify()` requires, when a
spine was named, BOTH the result fresh AND `spine_terminal(spine)` before `completed`
(AND, never rescue/OR -- the opposite of the CLI backend's semantics, because here a fresh
result must never excuse an undriven spine). When no spine was named, mtime-only survives
for back-compat but a WARNING prints and `spine_verified: null` is recorded on the entry,
so a silent clean pass is deleted even where a hard refusal is not yet possible.

- **Depth**: hides the terminal-state check behind the existing `spine_terminal` primitive;
  callers pass one new optional flag, nothing else changes.
- **Locality**: contained entirely to `run_crew.py` (dispatch + verify + CLI parser text);
  no other skill's calling convention is required to change to keep working.
- **Seam placement**: reuses the seam `finalize_from_exit_code` already proved for the CLI
  backend (`spine_terminal`), rather than inventing a second completion primitive.
- **Testability**: both halves (refuse-when-non-terminal, warn-when-unnamed) are independently
  exercisable against `RC.main` with no mocks beyond the existing `fake_launch` seam.

## Candidate B (untaken road): make `--spine` mandatory for every external dispatch
Refuse `dispatch()` itself unless `--spine` is given, forcing every future external caller
through the refusal path -- no silent-report fallback would ever be reachable.

**Why untaken**: the crew's own plan/spine path is chosen by the CREW when it starts (per
`constellation-implementer`: "Instantiate your gated plan..."), not by the dispatching
Commander at dispatch time -- the dispatcher genuinely does not know the path yet in the
common case. Making the flag mandatory without also changing the handoff contract (telling
the crew in advance where to put its plan) would either invent a naming convention this lane
does not own the authority to impose across every role skill, or make every dispatch refuse
unconditionally (a check that cannot pass is as broken as one that cannot fail). That is an
architecture/interface change spanning skills this lane does not own this wave --
recorded as decision pressure in MISSION_FRAME.md and floated to the Admiral, not decided here.

## Output -- recommendation
**Candidate A.** It closes the #432 gap with a real, exercisable refusal wherever a caller
already knows its target (e.g. a spine-open'd sub-dispatch), deletes the *silent* clean-pass
for every other case, stays inside this lane's sole file ownership, and requires zero
coordinated change to skills this wave does not own.

## Revision after cold critic
A cold plan critic (fresh agent, no authoring context, reading only MISSION_FRAME.md,
this file, and execute.json) found Candidate A **not sound enough to execute as-is**,
2 CRITICAL findings:

1. **Plan-introduced crash.** Accepting `--spine` on `dispatch()` newly legalizes
   `result=None` + `spine=<path>` on the external path (already legal at the `CrewSpec`
   level, previously unreachable because spine was always refused). The first draft's
   `verify()` sketch unconditionally called `result_exists(entry["result"], root)` -- a
   `TypeError` on `Path(None)`. **Disposition: fixed-now**, in scope, no float needed --
   `result_exists`/`result_fresh` are now guarded, never called with `result=None`; a
   spine-only external dispatch is judged solely on `spine_terminal`. Recorded as
   `decision:result-none-spine-only-guarded` in MISSION_FRAME.md.
2. **Intent-fit loophole in the dominant case.** The mission's own bar is "impossible ...
   to return a clean success." Candidate A left the common case (dispatcher does not know
   the spine path -- Candidate B's own untaken-road rationale says this IS the common
   case) as mtime-only-plus-warning: still a clean `completed`, exit 0, with only a
   stderr line as the trace. That does not meet the mission's bar for the dominant path.
   **Disposition: fixed-now**, in scope -- this is exactly what the mission asks this lane
   to build, not a separate architecture decision. Redesigned: `--verify-result` gains
   `--verify-spine <path>` (checked independently of dispatch-time `--spine`, since the
   dispatcher usually only learns the real path after the crew returns) and defaults to
   **refusing** when neither a spine target nor an explicit
   `--accept-mtime-only-risk "<reason>"` override is given -- printed to BOTH stdout and
   stderr, recorded on the entry, never silent. Recorded as
   `decision:verify-time-spine-not-just-dispatch-time` and
   `decision:default-refuse-not-default-warn` in MISSION_FRAME.md.

Both dispositions are within this lane's Inherited Latitude ("where the check sits on the
ExternalBackend path; its evidence shape") and do not touch the fenced files. Neither is
floated to the Admiral as a blocking question; both are noted for wave-checkpoint
visibility per the critic's own recommendation. MAJOR/MINOR findings (legacy entries
missing the `spine` key outright, ambiguous verify()-vs-finalize_from_exit_code backend
scope, stale docstring prose) are folded into the revised `g1-implement` handoff's
Constraints and Close Criteria directly -- use `.get("spine")` never `entry["spine"]";
`verify()` is `ExternalBackend`-only (an override, not a shared-base change) so the
CliBackend/`finalize_from_exit_code` OR/rescue path is untouched and the backend-uniform
tests that do not involve spine keep passing; `ExternalBackend`'s docstring is rewritten
to match, not left contradicting the new behavior.

## Untaken-road record
- Candidate B (mandatory `--spine`) -- architecture-scope, floated to the Admiral as decision
  pressure rather than built.
- A 2-agent parallel dispatch for this comparison -- skipped as disproportionate to a
  single-file, well-precedented fix; the comparison above is real, not rubber-stamped.

## Panel-vs-single record
Single author (this Commander), not a panel: no architecture or multi-epic surface is
touched, and the fix's shape was already fixed by an existing in-repo precedent
(`finalize_from_exit_code`'s spine-terminal reuse) rather than being a novel interface
choice with several live shapes.
