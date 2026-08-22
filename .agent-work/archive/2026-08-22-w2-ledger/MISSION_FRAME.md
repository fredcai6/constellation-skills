# Mission Frame — w2-ledger (#557 wave 2)

Map is DEGRADED-UNPARSEABLE (`.agent-work/w2-ledger/map-orientation.json`):
`docs/architecture/generated/map.json` carries no `nodes[].id` and `map/INDEX.md`
has no citable anchor. Per `verify-frame`'s degraded contract, no `decision:`/
`struct:` anchor ids can resolve (there is no map for them to be members of) —
this frame instead cites the hash-pinned substitutes declared at `context`
verbatim: `docs/CHECKLIST_SCHEMA.md` and `docs/agents/ORCHESTRATOR_CONTEXT.md`,
confirmed against source per the "Reconcile the assumed baseline" clause, never
the other way around. Decision-shaped items below are recorded as plain rulings
(no `decision:` id token) since a degraded run has nothing to weld the id to.

## Intent

Give the three genuine engine-authority-bypass paths — `waive`, forced
claim/release, and the trip ledger — one engine-written, append-only home, and
make closeout render it. Fix the two named defects in `waive()`'s authority
handling. Resolve #259 on the evidence the census actually shows, not the
issue's stated premise.

## Affected Capabilities

- Engine session leasing and gate advancement (`docs/CHECKLIST_SCHEMA.md`
  §"Engine session — actor authority over the state") — this run adds a write
  path, never changes lease semantics.
- The trip ledger (`docs/CHECKLIST_SCHEMA.md` §"The trip ledger") — the proven
  engine-written-only model this run extends.
- Closeout (`scripts/spine_lifecycle.py` `finish_work`/`close_work`/`open_pr`) —
  currently blind to `trip_ledger`; this run wires a read.

## Structural Anchors

- `scripts/checklist_engine.py:2167` `_append_trip_entry` — engine-written-only,
  sole caller `_trip_hard_gate`.
- `scripts/checklist_engine.py:2263` `_trip_hard_gate` — called from `dispatch()`
  BEFORE `_run_verb`, for `TRIP_HARD_GUARDED_VERBS` only (start/reopen). This is
  the chokepoint property to reuse, not just imitate.
- `scripts/checklist_engine.py:3663` `dispatch()` — the one chokepoint no CLI
  verb bypasses; `claim`/`release` force-handling already lives here (:3670-3684).
- `scripts/checklist_engine.py:3475` `waive()` — hardcodes `produced_by: "human"`
  (:3511); never reads `policy.get("authority")`.
- `scripts/spine_lifecycle.py:1005` `finish_work` — the closeout call sequence;
  no step reads `trip_ledger`.

## Governing Constraints / Assumptions

- `docs/CHECKLIST_SCHEMA.md:224` — `override_policy` is optional, a sibling of
  `check`; absence means not-waivable. Any authority comparison this run adds
  must not require `override_policy` to exist to keep working the way it does
  today for conditions that lack it.
- Hard constraint (LAUNCH_ORDER Pre-Ruling "engine-written-only"): the unified
  ledger must be reachable only from the dispatch chokepoint, before any verb
  runs — provable, not asserted.
- Epic standing ruling "no-spec-migration" — do not touch `generate_spine.py`,
  `specs/`, or the spec-to-template migration.

## Decision Anchors & Decision Pressure

- Ruling "ledger scope is three paths, not four" — `waive`, forced claim/release,
  and `trip_ledger` unify; `consolidate --override-reason` does not.
  @grade: settled/measured · leans plan,g1-implement · settle: archive census
  already run (117 files, extensive sanctioned use) — done, see notes-w2b.md.
- Ruling "#259 closes on evidence" — #259's "no sanctioned use case" premise is
  refuted by the census; the fix is documentation/closure, not code deletion or
  ledger fold-in.
  @grade: settled/measured · leans triage · settle: done, see notes-w2b.md.
- Pressure: where does the unified ledger physically live — extend
  `trip_ledger`'s entry-vocabulary in place, or introduce a new top-level key
  that both trip entries and waive/force-claim/force-release entries feed? Plan
  alternatives decide this under distinct constraints.
- Pressure: the #503 authority-comparison fix is a new refusal (LAUNCH_ORDER
  Pre-Ruling "widening-live-refusal-report-only") — report-only shape and its
  promotion trigger are named at plan, not guessed at execute.

## Claims / Evidence Surfaces

- claim: `trip_ledger` is engine-written-only — verified by grep (no non-engine,
  non-test, non-archive writer in the repo) and by `_trip_hard_gate`'s call site
  inside `dispatch()` preceding `_run_verb`.
- claim: `consolidate --override-reason` has real sanctioned use — verified by
  117-file archive grep (see notes-w2b.md), not asserted.
- Re-confirm at each execute gate: red-proof pinned to the shipped SHA per
  LAUNCH_ORDER Pre-Ruling "red-proof-pinned-to-shipped-revision".

## Map Confidence / Staleness / Disputes

- `docs/architecture/generated/map.json` / `map/INDEX.md` — DEGRADED, discharged
  per context-step receipt. Out of this issue's override-surface scope; flagged
  as a triage candidate, not fixed here.

## Out of Scope

- The attest/condition surface of `checklist_engine.py` and the shipped spine
  templates (fenced to the `w2-basis` lane).
- `generate_spine.py`, `specs/`, the spec-to-template migration (epic standing
  ruling).
- `consolidate --override-reason` itself — census shows it works as intended;
  untouched except for documentation closing #259.
