# w3-basis working notes

## Understand (reconciled against LAUNCH_ORDER, no reachable human)

**Problem statement.** `CommanderSpineBasisFields` in `tests/test_checklist_engine.py:8543`
pins `PINNED_HEAD` to a whole-repo `git rev-parse HEAD` (`9d5aac6d...`), which is already stale
one wave later (measured: 3 skipped). Two defects, one remedy (family B: evidence true when
taken, false when relied on):

1. Wrong granularity — pin should be the BLOB OID of the one file the test actually depends on,
   `skills/commander/templates/COMMANDER_SPINE.template.json` (`git rev-parse HEAD:<path>`), not
   repo HEAD. An edit anywhere else in the repo must leave the tests GREEN; an edit to the pinned
   file must turn them RED.
2. Drift currently calls `skipTest`. Per the human's `c5ac6662` ruling (cited verbatim in the
   launch order) and `decision:drift-fails`, drift must FAIL with a message naming the stale proof
   and the re-run path (`decision:ship-the-re-verify-path`).

**Scope (file ownership).** `tests/test_checklist_engine.py` only, mine alone this wave.
`skills/commander/templates/COMMANDER_SPINE.template.json` is read-mostly — reads only, no edits;
float any need to touch it.

**Pre-rulings binding this run** (cited, not re-derived): `decision:blob-oid-not-head`,
`decision:drift-fails`, `decision:ship-the-re-verify-path`, `decision:do-not-generalise-to-qualitative-conditions`,
`decision:prove-both-directions`.

**Map.** DEGRADED-UNPARSEABLE (map/INDEX.md references per-package packets absent on disk;
map/ids.jsonl empty) — discharged at `context` via `map_orient.py orient` with substitutes
`tests/test_checklist_engine.py`, `skills/commander/templates/COMMANDER_SPINE.template.json`,
`docs/CHECKLIST_SCHEMA.md`. Escalated the stale-map defect itself as a triage candidate rather
than blocking this single-file lane on it.

This is a small, bounded, mechanical-shape fix fully specified by the launch order. No genuine
gap surfaced during understand; proceeding under the frozen order.
