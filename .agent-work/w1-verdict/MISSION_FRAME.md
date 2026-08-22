# Mission Frame — #371 (epic 569, wave 1)

Shrunk. `map/INDEX.md` and `map/ids.jsonl` at this repo's tip carry no live packet dirs
(`map/scripts.checklist_engine/`, `map/scripts.validate_spine/` are referenced but absent on
disk) and `docs/architecture/generated/map.json` has zero `nodes[].id`. `map_orient.py` returned
`DEGRADED-UNPARSEABLE`, discharged at the `context` step with substitutes
`docs/CHECKLIST_SCHEMA.md`, `docs/CHECKLIST_ENGINE_DESIGN.md`, `scripts/checklist_engine.py`,
`scripts/validate_spine.py`. This frame's anchors are those substitutes and the launch order's own
pasted code, not `map:` node ids — there are none to cite. The mission is small, local, and fully
specified by the launch order (exact code at both sites pasted verbatim), so this frame is
shrunk accordingly rather than skipped outright: the corpus-wide backward-compatibility question
(does a new `match` shape collide with any real payload in the shipped corpus?) is genuine
map-shaped work worth framing even though no `map:` node backs it.

## Intent
Make `checklist_engine.py`'s two `match`-comparison sites (`_check_condition`'s artifact branch,
`attest`'s artifact branch) accept a set-valued `match` for "any of these acceptable values" without
breaking any existing scalar `match`, and make `validate_spine.py` refuse (report-only, promotion
trigger named) a `match` shaped in a way that would silently produce an unsatisfiable condition.

## Affected Capabilities
- The engine's `artifact` postcondition check (`docs/CHECKLIST_SCHEMA.md` "What 'engine-checked'
  means", `check.kind == "artifact"`): confirms an evidence item's payload matches `check.match`
  by per-key equality. This run widens the per-key comparison from scalar-`==` to
  scalar-`==`-or-membership-in-a-declared-set.
- `validate_spine.py`'s spine-lint family (`_fault_artifact_no_match`, issue #562, is the existing
  sibling fault for a *missing* match; this run adds the *malformed-match-shape* fault next to it).

## Structural Anchors
- `scripts/checklist_engine.py` — `_check_condition`, artifact branch, ~line 1083 (per launch order
  pasted excerpt).
- `scripts/checklist_engine.py` — `attest`, artifact branch, ~line 3438 (per launch order pasted
  excerpt).
- `scripts/validate_spine.py` — `_fault_artifact_no_match`, ~line 456 (existing sibling fault to
  extend the family beside).
- `docs/CHECKLIST_SCHEMA.md` — "What 'engine-checked' means" table, the `artifact` row's `match`
  description; needs a matching sentence for the new shape once chosen.

## Governing Constraints / Assumptions
- `decision:backward-compatibility-is-non-negotiable` (launch order) — every existing scalar
  `match` in the shipped corpus keeps its exact current meaning.
- `decision:widening-ships-live-refusal-ships-report-only` (launch order, guess/admiral, leans g1) —
  the widened comparison ships live (adds no wall to a currently-broken comparison); the new
  `validate_spine` refusal ships report-only with a named promotion trigger.
- Two enforcement strengths named in Inherited Context (#345): a `command`-kind postcondition is
  engine-refusing, `record()` on a survey evaluates only `command`-kind — `null`/`artifact`-kind
  stay unevaluated there (#422). This run's `artifact`-kind matching change is read against that
  scoping: `record()` never calls `_check_condition`'s artifact branch or `attest`'s artifact
  branch on a survey postcondition, so the two functions this run touches are gated-plan-only
  paths; the #422 scoping decision does not interact with this change. (If code reading proves
  this wrong, that is a float, not a silent scope change — see Stop Conditions.)

## Decision Anchors & Decision Pressure
- `decision:371-vocabulary-half-is-already-done` — #371's `APPROVE-WITH-FOLLOWUPS` framing is stale;
  mechanism-only mission.
  `@grade: settled/admiral · leans g1`
- `decision:widening-ships-live-refusal-ships-report-only` — split ship posture, see above.
  `@grade: guess/admiral · leans g1 · settle: Admiral confirms with the human at the wave-2 checkpoint`
- `decision:match-shape-is-yours-to-choose` — bare list vs. richer operator form (`{"any_of": [...]}`)
  is this run's own design content; settled in `PLAN_ALTERNATIVES.md`.
  `@grade: guess · leans g1 · settle: run both shapes against the existing corpus of matches; the
  one that cannot be confused with a legitimate scalar list-valued payload wins`

## Claims / Evidence Surfaces
- Claim: "a list-valued `match` is silently unsatisfiable today" — verified by a red-proof run
  against the base commit before any code change (Return Shape item 4).
- Claim: "every existing scalar `match` in the shipped corpus keeps behaving identically" —
  verified by the corpus inventory below plus the full local `pytest` run.

## Map Confidence / Staleness / Disputes
- `map/INDEX.md` and `map/ids.jsonl` (this repo's own architecture map) are stale/unusable at this
  commit — see Intent. This is an out-of-mission finding surfaced to the Admiral at `reconcile`
  (this repo has no `docs/architecture` packet map either, so `reconcile` falls to the direct-record
  path per `commander-core.md` "Architecture bookend"). Does not alter this plan: the launch order
  already pasted the exact code this run touches, so the map's absence removes navigation
  convenience, not planning input.

## Corpus inventory (backward-compatibility evidence, gathered at plan time)
`grep -rn '"match"' skills/*/templates/*.json` → 2 hits, both scalar:
- `skills/commander/templates/EXECUTE_PLAN.template.json:21` — `{"status": "complete"}`
- `skills/commander/templates/EXECUTE_PLAN.template.json:52` — `{"verdict": "APPROVE"}`

Broader real-usage census (`grep -rhoE '"match": ?\{[^}]*\}' .agent-work --include=*.json`, ~90
driven spines/plans under this worktree's `.agent-work/`, itself a copy of the main checkout's real
history) → every distinct match-value shape found is scalar-per-key:
`{"status": "complete"}`, `{"verdict": "APPROVE"}`, `{"status": "complete", "red_green": ...,
"mutation_control": ..., "mixed_writer": ..., "blast_radius": ...}`, and one similar multi-key
scalar variant. **No list-valued or dict-valued match value exists anywhere in the corpus sampled.**
This is the evidence a chosen shape is checked against for collision risk.

## Out of Scope
- `APPROVE-WITH-FOLLOWUPS` or any verdict-vocabulary change (`decision:371-vocabulary-half-is-already-done`).
- #558 (review-levels doctrine) — pulled from this wave entirely.
- `waive()`'s `produced_by`/`override_policy.authority` gaps (#557, wave 2) — do not touch in passing.
- A new `scripts/verify_*.py`/`check_*.py` script — `w1-wiring`'s territory this wave; float instead.
- Making the new `validate_spine` refusal blocking — floats to the Admiral, not decided here.
