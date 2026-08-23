# Implementer Handoff

## Gate
g7-implement (execute.json, work-id w3-promote)

## Task
Promote bucket-2 `check: null` conditions in BOTH `skills/cartographer/templates/CARTOGRAPHER.template.json`
AND `skills/scout/templates/SCOUT.template.json` — grouped in one gate for priority-ordering only,
keep per-file records separate in `notes-1.md`. Use only the engine's existing check kinds
(`decision:no-new-check-kinds`).

## Protected Intent
Same as g1/g3/g4/g5: no decorative artifact conditions. A check that cannot fail is worse than the
honest `check: null` it replaces.

## CRITICAL — different default from every prior gate this wave
`notes-1.md`'s fresh assessment found **BOTH files have ZERO live check kinds today** — every
existing postcondition in both files is `check: null` outside whatever this gate promotes. That
means ANY promotion here is, by construction, the FIRST use of that check kind in that specific
template. Per this wave's own constraint (`decision:blocking-where-adjudicated`), **default every
promotion in this gate to REPORT-ONLY with a named promotion trigger** (e.g. "N clean report-only
runs through this gate with zero false-refusals, reviewed at the next Cartographer/Scout-owning
wave") — do NOT ship blocking here, unless you find a specific, stated per-condition reason that
overrides the default. A pattern cited from a DIFFERENT template (e.g. EXPLORER_SPINE's
`verify_spec_confirmed.py` wiring) is context for your reasoning, never eligibility for shipping
blocking in THIS file.

Command-kind checks have a real report-only shape (a script's own `--report-only` flag, or a shell
wrapper that always exits 0 while still printing the real verdict to stdout for the evidence
payload — see `/home/tommy/.claude/skills/constellation-commander/scripts/map_orient.py`'s own
`--report-only` flag as the model). Artifact-kind checks have NO report-only shape (w2-basis's own
finding, reconfirmed by g1-g5) — if the honest check kind for a candidate here is `artifact`, it
demotes back to `check: null` with the reason recorded; it does NOT ship forced-blocking to dodge
this constraint.

This run's own map is DEGRADED-UNPARSEABLE (see `MISSION_FRAME.md`) — do not let any promoted check
depend on map state this repo cannot currently produce.

## Test Mode
Test-after allowed.

## Close Criteria
Promote exactly these conditions (fresh-verify each against the real shipped JSON first — the
counts/shapes below are this Commander's own hand-assessment, not guaranteed final; if your fresh
read disagrees, say so and adjust, do not force a fit):

### CARTOGRAPHER.template.json
1. `packets.c1` ("touched packets reflect current code") and `index-overlays.c1` ("index and
   overlays consistent with packets") — WEAK candidates, locator-ambiguous: a git-diff-based
   "something under `docs/architecture/` changed" proxy verifies motion, not correctness. If you
   cannot make the locator genuinely unambiguous (i.e. it would falsely pass when the map is stale
   but something *else* under that path happened to change), leave `check: null` and say so rather
   than shipping a decorative check. If you find a genuinely discriminating locator, ship it
   report-only (first use of any kind in this file) with a named promotion trigger.
2. `context.c1` and `map-compliance.c1` — pure judgment (no locator). Leave `check: null`.

### SCOUT.template.json
1. `report.c1` ("SCOUT_REPORT written; candidates routed") — SPLIT candidate: the "SCOUT_REPORT.md
   written" half has a real fixed-path locator (existence-only), report-only since this is the
   first use of any kind in this file. "Candidates routed" (judgment) stays `check: null`. No
   `basis` field (`decision:no-basis-backfill` — see the note below).
2. `context.c1` and `audit.c1` — pure judgment (no locator). Leave `check: null`.

- Every other `check: null` condition in both files stays untouched.
- Both `.agent-work/templates/CARTOGRAPHER.template.json` and
  `.agent-work/templates/SCOUT.template.json` byte-match their edited `skills/` sources (only sync
  the ones you actually edit — if one file gets zero promotions, do not touch its overlay).
- A red-proof test class (or two, one per file, your call) in `tests/test_checklist_engine.py`
  (adjacent to g1's/g3's/g4's/g5's own classes, same pattern: pinned HEAD, skipTest on drift,
  adversary-chosen mutations per promoted condition — for a report-only command check, the
  discrimination test asserts the command still exits 0 AND still prints the real verdict to stdout
  even under the defect fixture, since report-only never blocks `advance`).
- If any all-null gate in either file clears, update `tests/test_validate_spine.py`'s floor per the
  same discipline as g1/g3/g4/g5.
- `docs/CHECK_SCRIPT_CENSUS.md`'s unwired-script list names `check_role_spine_bookends.py` and
  `check_skill_freshness.py` as options — wiring either live here is a genuine option but NOT
  mandatory. If you use one, note it plainly: it flips that doc's own live/unwired tallies, which
  g8 (the next gate) must then update — do not update `docs/CHECK_SCRIPT_CENSUS.md` yourself, just
  flag it in your result so g8 knows.
- Full `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` green.

## Allowed Scope
- `skills/cartographer/templates/CARTOGRAPHER.template.json` (raw text hand-edit only).
- `skills/scout/templates/SCOUT.template.json` (raw text hand-edit only).
- `.agent-work/templates/CARTOGRAPHER.template.json`, `.agent-work/templates/SCOUT.template.json`
  (overlay sync, only for files actually edited).
- `tests/test_checklist_engine.py` (new test class/classes only).
- `tests/test_validate_spine.py` (floor numbers/message only, if triggered).

## Specific Exclusions
Do not touch `COMMANDER_SPINE.template.json`, `ADMIRAL_SPINE.template.json`,
`EXPLORER_SPINE.template.json`, `CHARTER.template.json`, or `IMPLEMENTER_PLAN.template.json` or
their overlays (owned by prior gates, already landed/landing on this branch). Do not touch
`checklist_engine.py`. Do not edit `docs/CHECK_SCRIPT_CENSUS.md` (g8's job).

## Constraints
- `decision:no-new-check-kinds`.
- `decision:no-basis-backfill` — do NOT add a `basis` field to any condition (g4's implementer made
  this exact mistake once already this wave — caught and fixed by the Commander; do not repeat it).
- **Default report-only with a named trigger, per the CRITICAL section above** — this REVERSES
  g1/g3/g4/g5's default (which shipped blocking because those templates already had live checks to
  cite). State explicitly, per promoted condition, which of THIS SAME template's existing checks
  (if any) already use that kind before shipping ANYTHING blocking — if none do (which notes-1.md
  says is the case for both files), it ships report-only.
- Compact-format JSON: raw text hand-edit, never `json.load`/`json.dump` round-trip.

## Map Anchors (inbound)
- **Map entry point:** `docs/CHECK_SCRIPT_CENSUS.md` (unwired-script list), `docs/CHECKLIST_SCHEMA.md`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human`;
  `decision:no-basis-backfill` `@grade: settled/human`;
  `decision:blocking-where-adjudicated` `@grade: settled/human`.

## Deliverable Path Check
- **Committed** — both template files touched; verify `git check-ignore <path>` exits 1 for each.
- **Committed** — corresponding overlay files touched; same check.
- **Committed** — `tests/test_checklist_engine.py`, `tests/test_validate_spine.py` (if touched).

## Required Evidence
- `git diff` for each template file touched.
- JSON parse-check command output for each.
- `python3 scripts/check_template_overlay_freshness.py` output.
- Full pytest output for the two test files.

## Wiring Grep
`grep -n '"check"' skills/cartographer/templates/CARTOGRAPHER.template.json` and
`grep -n '"check"' skills/scout/templates/SCOUT.template.json`, before/after each.

## Verification Commands
```bash
python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
python3 scripts/check_template_overlay_freshness.py
python3 -c "import json; json.load(open('skills/cartographer/templates/CARTOGRAPHER.template.json',encoding='utf-8')); print('OK')"
python3 -c "import json; json.load(open('skills/scout/templates/SCOUT.template.json',encoding='utf-8')); print('OK')"
```

## Suggested Model Tier
simple bounded — mirrors g1's/g3's/g4's/g5's already-proven pattern, but with the report-only
default reversal — read the CRITICAL section carefully before promoting anything.

## Authority
Which conditions to promote (and whether report-only vs. null) is a first-pass judgment call from
the Commander (this handoff), not frozen — if your fresh read of the real JSON disagrees with a
specific item above, say so and adjust rather than forcing it; report the correction plainly in
your result.

## Stop Conditions
Stop and return if: you find a genuinely unambiguous locator for CARTOGRAPHER's `packets.c1`/
`index-overlays.c1` but are unsure whether it should ship report-only or you believe blocking is
actually justified despite the default; any edit would require touching `checklist_engine.py`; you
are unsure whether wiring `check_role_spine_bookends.py`/`check_skill_freshness.py` here is in
scope.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape. `Return status` lowercase. Write to
`.agent-work/w3-promote/crew-handoffs/g7-implementer-result.md` before ending your turn.
