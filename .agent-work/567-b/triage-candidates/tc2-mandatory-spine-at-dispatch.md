# Triage candidate: consider mandatory `--spine` at dispatch time for ExternalBackend

**Not filed — a recommendation only, per launch order `decision:no-issue-filing`.**

## What
This lane closed #432 by making `ExternalBackend`'s `--verify-result` default-refuse
without spine evidence (a fresh result artifact alone is no longer enough), with an
explicit, reasoned `--accept-mtime-only-risk "<reason>"` escape hatch. It did NOT make
`--spine` mandatory at dispatch time — that was considered and explicitly rejected as an
untaken road (see `PLAN_ALTERNATIVES.md` Candidate B) because the dispatcher (a
Commander) usually does not know the crew's own plan/spine path until AFTER the crew
returns, so a dispatch-time requirement would either force every dispatch to refuse
unconditionally or require a coordinated doctrine/handoff change across
`constellation-implementer`/`constellation-commander`'s crew-dispatch contract — outside
this lane's file ownership this wave.

## Why it matters
The verify-time default-refuse mechanism is real and load-bearing, but it still leaves a
caller free to reach for `--accept-mtime-only-risk` routinely rather than ever supplying
`--verify-spine`. Over time that could become the path of least resistance, quietly
reintroducing something close to the old mtime-only behavior, just with an extra flag and
a reason string. Whether this happens in practice is an open question (see
`REPLAN_INPUT.json` uncertainty_register).

## Suggested disposition
Not urgent. After this lands, a later wave could: (a) observe real `crew-runs.json`
entries for `mtime_only_risk_accepted` frequency, and (b) if it is common, revisit
whether the crew-dispatch contract (handoff templates, `constellation-implementer`
doctrine) should be extended so a dispatcher DOES learn the crew's spine/plan path
early enough to name it, closing the remaining gap structurally rather than by
convention.

## Source
Surfaced by the Commander at plan (MISSION_FRAME.md decision pressure), confirmed still
open at execute/integrate — this lane's own scope boundary, not a defect.
