# Mission Frame

Map is DEGRADED-UNPARSEABLE (see `.agent-work/w3-basis/map-orientation.json`); no map anchor ids
exist to cite. This frame is built instead from the three substitutes hash-pinned into that
receipt at `context`: `tests/test_checklist_engine.py`, `skills/commander/templates/COMMANDER_SPINE.template.json`,
and `docs/CHECKLIST_SCHEMA.md`.

## Intent
Make `CommanderSpineBasisFields` (in `tests/test_checklist_engine.py`) pin to the BLOB OID of
`skills/commander/templates/COMMANDER_SPINE.template.json` (the file it actually depends on)
instead of whole-repo `HEAD`, and FAIL — not skip — on drift, with a cheap documented re-verify
path for whoever next legitimately edits the template.

## Affected Capabilities
- The red-proof class `tests/test_checklist_engine.py::CommanderSpineBasisFields` and its three
  test methods (`test_plan_c2_c4_c5_each_carry_the_ratified_basis_shape`,
  `test_no_condition_outside_plan_c2_c4_c5_carries_a_basis_key`,
  `test_live_checklist_from_the_template_renders_basis_lines_at_plan`), all of which share the
  `_skip_if_head_moved` gate this run replaces.

## Structural Anchors (substitute-pinned)
- `tests/test_checklist_engine.py` — `CommanderSpineBasisFields` class, `PINNED_HEAD`,
  `_skip_if_head_moved`.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — the file the pin must key off;
  read-mostly this wave, owned by `w3-promote`.
- `docs/CHECKLIST_SCHEMA.md` — the `basis` field's documented shape, for consistency of any new
  doc note on the re-verify path.

## Governing Constraints / Assumptions
- File ownership — `tests/test_checklist_engine.py` is mine alone; the template is read-mostly.
- No skip on drift — a check that can only skip is not evidence (human ruling `c5ac6662`).
- Blob-OID granularity — pin `git rev-parse HEAD:<path>`, not repo HEAD.
- Cheap re-verify — re-establishing the pin after a legitimate template edit must be cheap and
  documented.
- No qualitative rollout — this lane binds evidence only; no rollout to qualitative conditions.
- Prove both directions — must demonstrate a planted template edit going RED and an unrelated
  repo commit staying GREEN.

## Decision Anchors & Decision Pressure
Pre-rulings from the launch order, cited rather than re-derived (all `settled`, not revisable
locally — float to the Admiral if reality contradicts one):
- Pin the blob OID of the template file, not repo HEAD (`decision blob-oid-not-head`).
  Grade — settled/human, leans plan + execute.
- Divergence FAILs with a message naming the stale proof and re-run path
  (`decision drift-fails`). Grade — settled/human, leans plan + execute.
- Ship a cheap, documented re-verify path alongside the guard (`decision
  ship-the-re-verify-path`). Grade — settled/human, leans plan + execute.
- Do not roll the `basis` field out further, this lane binds evidence only (`decision
  do-not-generalise-to-qualitative-conditions`). Grade — settled/human, leans plan.
- Prove both directions of the granularity fix (`decision prove-both-directions`).
  Grade — settled/admiral, leans plan + execute.

Decision pressure (not yet settled, this run's to resolve): where exactly the re-verify path
lives (a documented one-liner command vs. an extracted reusable helper) and whether the pin lives
in the test class or a shared helper — delegated latitude per the launch order; resolved at the
plan-alternatives step below.

## Claims / Evidence Surfaces
- The pin tracks the file's content, not the repo's HEAD — verified by a mutation test: touch an
  unrelated file, commit, re-run the suite, assert still GREEN.
- Drift FAILs, never skips — verified by a mutation test: edit the pinned template, re-run, assert
  FAIL (not SKIP) with a message naming the stale proof and the re-run path.
- The re-verify path is genuinely cheap — verified by actually running the documented re-verify
  path after a planted edit and confirming the pin updates and tests go green again.

## Map Confidence / Staleness / Disputes
- Repo map (`map/INDEX.md`, `docs/architecture/`) is DEGRADED-UNPARSEABLE repo-wide — not specific
  to this run's scope. Altered plan: no map-derived anchors used; frame is cut from direct reads of
  the three substitute files instead. Escalated as a triage candidate (not blocking this lane).

## Out of Scope
- Any edit to `skills/commander/templates/COMMANDER_SPINE.template.json` itself (owned by
  `w3-promote`).
- Any qualitative-condition population, the `basis` field's rollout beyond `plan.c2/c4/c5`, and any
  change to `scripts/checklist_engine.py`.
