# Mission Frame — w3-promote

Map is DEGRADED-UNPARSEABLE repo-wide (`map/INDEX.md` carries no citable anchor ids, `map/ids.jsonl`
is empty, `docs/architecture/` is empty) — see `.agent-work/w3-promote/map-orientation.json`.
Substitutes declared and hash-pinned: `docs/agents/AGENT_GUIDE.md`, `docs/CHECK_SCRIPT_CENSUS.md`.
This is a shrunk frame: the target artifacts are `skills/*/templates/*.json` data files the code map
does not model at all (confirmed against `docs/CHECK_SCRIPT_CENSUS.md`'s own method, which locates
check-script wiring by direct grep/import-graph inspection, not the code map). Full mission frame
mechanics are followed regardless — this is a shrink, not a skip.

## Intent
Convert bucket-2 `check: null` conditions (locator expressible, no new engine mechanism needed) in
the corpus's shipped spine/survey templates into real, mechanically-checked postconditions/preconditions
using only the three check kinds the engine already implements (`command`, `artifact`,
`git-change-policy`) — per `decision:no-new-check-kinds`. Record the bucket for every condition
assessed, in every template touched, so a small honest result reads as a measurement
(`docs/agents/ORCHESTRATOR_CONTEXT.md`'s "Machine-checkable evidence when practical" plus the
launch order's Honest-Null Clause).

## Affected Capabilities
- `docs/CHECKLIST_SCHEMA.md` "Condition (pre/post)" — the `check` field's three mechanical kinds
  (`command`, `artifact`, `git-change-policy`); this run's promotions are instances of this existing
  contract, not a new one.
- `scripts/checklist_engine.py`'s `attest()` — the artifact-refusal branch already blocking-live on
  5 conditions in `COMMANDER_SPINE.template.json` today (`understand.c1`, `plan.c3`, `triage.c2`,
  `review.c1`, `archive.c5`); this run reuses that exact path for more conditions, per
  `decision:no-new-check-kinds`. Not edited this run — reused, read-only.
- `scripts/validate_spine.py` — the falsifiable-all-null linter that already refuses
  `COMMANDER_SPINE.template.json`'s `init`/`reconcile` gates; wiring it at the shipped templates is
  in scope (`decision:validate-spine-wiring-is-in-scope`).

## Examples / Events
- The already-measured, already-red-proofed-in-design "artifact-conversion" candidate from
  `w2-basis` (`.agent-work/archive/2026-08-22-w2-basis/plan-candidate-artifact-conversion.md`):
  independently converged with two other candidates on `COMMANDER_SPINE.template.json`'s 19-condition
  split, then further narrowed 5 clean conversions (`plan.c1`, `plan.c4`, `plan.c5`, `reconcile.c1`,
  `archive.c2`) after a cold critic pass. w2-basis did NOT ship these (it built the `basis` field
  instead, per its own scope fence) — they are real prior analysis to re-verify fresh, not to
  re-derive from scratch, and not to trust blindly: this run has authority (the ratified
  `decision:blocking-where-adjudicated`) that w2-basis explicitly lacked, so this run's own
  per-condition assessment is authoritative where it disagrees.

## Structural Anchors
- `skills/commander/templates/COMMANDER_SPINE.template.json` — 32 conditions, 19 `check: null`
  (measured fresh this run, matches launch order exactly).
- `skills/admiral/templates/ADMIRAL_SPINE.template.json` — 16 conditions, 10 null.
- `skills/cartographer/templates/CARTOGRAPHER.template.json` — 5 conditions, 5 null.
- `skills/charter/templates/CHARTER.template.json` — 16 conditions, 10 null.
- `skills/commander/templates/EXECUTE_PLAN.template.json` — 8 conditions, 4 null.
- `skills/explorer/templates/EXPLORER_SPINE.template.json` — 18 conditions, 10 null.
- `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` — 4 conditions, 3 null.
- `skills/scout/templates/SCOUT.template.json` — 4 conditions, 4 null.
- Sum of null conditions across these 8 templates: **65** — matches the launch order's "~65
  qualitative conditions in the corpus" exactly (measured fresh, not recalled).
- The remaining templates under `skills/*/templates/*.json` either carry no `tasks` field (data
  payload templates: `FINDING`, `REPLAN_*`, `INITIAL_ISSUE_SET`, `SHAPED_BRIEF`,
  `INTERROGATION_RECORD`, `FOWLER_PASS`, `ENGINE_CONFIG`) or have zero null conditions
  (`CYCLE`, `INTERROGATION`, `REVIEW_SURVEY`) — out of scope by measurement, not by assumption.

## Governing Constraints / Assumptions
- `decision:no-new-check-kinds` — promotion only; a condition needing a new kind is bucket-1/3, left alone.
- `decision:no-basis-backfill` — `basis` field is `w3-basis`'s population; do not roll it out here.
- `decision:record-the-partition-per-condition` — record bucket per condition per template; a
  template partitioning materially differently from 9/19 (~47%) is a material exception, float it.
- `decision:blocking-where-adjudicated` — ship blocking where adjudication is available now (this
  wave has it, per the wave-2-checkpoint ratification cited in Prior-Wave Verdicts); report-only
  with a named promotion trigger where genuinely unmeasured.
- `decision:red-proof-each-promotion` — each promotion red-proved against the shipped revision with
  an attacker-chosen mutation, not a self-designed falsifier.
- `decision:validate-spine-wiring-is-in-scope` — count faults across all shipped templates first,
  decide blocking-vs-not with the Admiral if it reds the suite.
- A check that cannot fail is worse than no check (`global-orchestrator.md` "A check that cannot
  fail") — governs every promotion decision below: an artifact condition an agent can trivially
  self-satisfy with a matching-shaped payload is not a promotion, it is the launch order's own
  named defect reproduced.

## Decision Anchors & Decision Pressure
- decision:promote-only-conditions-with-a-real-locator — do not force a "did-you-understand-X"
  condition into artifact shape merely to raise a conversion count; leave it honestly `check: null`.
  @grade: settled/human · leans g1-commander-spine,g2-other-templates · (cites launch order's Honest-Null Clause + w2-basis's own measured finding that a decorative artifact condition is worse than a bare assertion)
- decision pressure: for COMMANDER_SPINE, whether `init.c1` (engine lease claimed) promotes as
  `artifact` (w2-basis's original framing) or is refused as vacuous/gate-order-guaranteed (w2-basis's
  own later "wrong kind" finding) — this run's own fresh assessment decides, cited in execute.json.
- decision pressure: per-template bucket-2 promotion list for the 7 non-COMMANDER_SPINE templates —
  not yet assessed; execute.json's gates carry this assessment as first-class work, not a foregone
  conclusion.
- decision pressure: whether `validate_spine.py` wiring lands blocking this wave, once the
  full-corpus fault count is in hand.

## Claims / Evidence Surfaces
- claim:validate-spine-refuses-commander-spine — `python3 scripts/validate_spine.py
  skills/commander/templates/COMMANDER_SPINE.template.json` exits 1 with 2
  `falsifiable-all-null` faults (`init`, `reconcile`). Re-verified fresh this run at HEAD
  `135c34eb`, matches launch order exactly.
- claim:65-null-conditions-corpus-wide — measured fresh this run (script pasted above), matches
  the launch order's extrapolated ~65 figure exactly, not merely recalled from the order.
- claim:5-clean-conversions-measured-by-w2-basis — `plan.c1`, `plan.c4`, `plan.c5`, `reconcile.c1`,
  `archive.c2` in `COMMANDER_SPINE.template.json`, each with a real, re-runnable file locator per
  `plan-candidate-artifact-conversion.md` §2's table — re-verified fresh by this run's own gate,
  not taken on faith.

## Map Confidence / Staleness / Disputes
- The repo-wide code map is DEGRADED-UNPARSEABLE (see Intent). This is a pre-existing, repo-wide
  condition independent of this lane's scope — flagged as a triage candidate for the map owner
  (`scripts/code_map`), not blocked on here. It does not alter this plan: the target artifacts are
  data-only JSON the code map does not model.

## Out of Scope
- The `basis` field and any `basis` backfill (`w3-basis`'s population, `decision:no-basis-backfill`).
- Inventing a new check kind or changing `checklist_engine.py` behavior beyond reusing existing
  `attest`/`command`/`git-change-policy` machinery as-is.
- Re-measuring the already-established 19-condition COMMANDER_SPINE partition from scratch (cited,
  not re-derived) — this run's own work is promotion plus per-condition bucket recording, including
  wherever this run's fresh assessment diverges from w2-basis's prior analysis.
- The other 12 template files with no `tasks` field or zero null conditions (measured, not assumed).
- Fixing every `validate_spine.py` fault across the whole corpus this wave if that scope exceeds the
  Mission — float to the Admiral per `decision:validate-spine-wiring-is-in-scope`.
