# Implementer Handoff

## Gate
g7-implement (execute.json, work-id w3-promote)

## Task
Promote real `check: null` conditions in BOTH `skills/cartographer/templates/CARTOGRAPHER.template.json`
AND `skills/scout/templates/SCOUT.template.json` using only the engine's existing check kinds — per
`decision:no-new-check-kinds`. Then red-proof each promotion and sync both overlays.

## Protected Intent
No decorative artifact conditions. **This gate carries an extra risk**: both files measure ZERO
live check kinds today (every existing postcondition in both is `check: null` outside whatever you
promote here) — confirm this yourself by grep before you start. That means ANY promotion here is a
FIRST USE of that check kind in that specific template, by construction. Default every promotion to
REPORT-ONLY WITH A NAMED TRIGGER unless you have a specific, stated reason to ship it blocking — a
pattern reused from a DIFFERENT template (e.g. EXPLORER_SPINE's `verify_spec_confirmed.py` wiring)
is context for your reasoning, never eligibility for blocking here.

## Test Mode
Test-after allowed.

## Close Criteria
Fresh-verify each against the real shipped JSON first:

**CARTOGRAPHER.template.json:**
1. `packets.c1` ("touched packets reflect current code") / `index-overlays.c1` ("index and
   overlays consistent with packets") — these are WEAK candidates: a git-diff-based "something
   under docs/architecture/ changed" proxy verifies motion, not correctness, and the base commit to
   diff against is ambiguous in a general-purpose template. If you cannot construct a genuinely
   unambiguous locator, LEAVE BOTH `check: null` and say so explicitly in your result — do not ship
   a decorative check just to hit a promotion count.
2. `map-compliance.c1` — pure judgment, leave `check: null`.
3. `context.c1` — pure judgment, leave `check: null`.

**SCOUT.template.json:**
1. `report.c1` ("SCOUT_REPORT written; candidates routed") → existence-only promotion for
   `.agent-work/<work-id>/SCOUT_REPORT.md`, REPORT-ONLY (first use of whatever kind you pick in
   this file) with a named trigger (e.g. "N clean report-only runs with zero false-refusals,
   reviewed at the next Scout-owning wave"). "Candidates routed" stays unverified.
2. `context.c1` / `audit.p1` / `audit.c1` — pure judgment / gate-order, leave `check: null`.

For any condition you DO promote: if the honest check kind is `command`, it has a real
report-only shape (a script's own `--report-only` flag if you write one, or a shell wrapper that
always exits 0 while the real verdict still prints to stdout for the evidence payload — model this
on `constellation-commander/scripts/map_orient.py`'s own `--report-only` flag, read it first). If
the honest check kind is `artifact`, IT HAS NO REPORT-ONLY SHAPE (confirmed by a prior wave's own
finding) — if that's the only fit, DEMOTE the condition back to `check: null` with the reason
recorded rather than shipping it forced-blocking.

- Every other `check: null` condition in both files stays untouched.
- Both `.agent-work/templates/CARTOGRAPHER.template.json` and
  `.agent-work/templates/SCOUT.template.json` byte-match their edited sources.
- A red-proof test class in `tests/test_checklist_engine.py` covering whatever you promote (if
  nothing promotes cleanly in one or both files, say so — an honest zero here is a legitimate,
  pre-sanctioned outcome per the launch order's Honest-Null Clause, not a shortfall).
- If you wire either of `check_role_spine_bookends.py` or `check_skill_freshness.py` (currently
  listed `unwired` in `docs/CHECK_SCRIPT_CENSUS.md`) as a real check here, that's a genuine option
  but NOT mandatory — if you do, say so plainly (the Commander will update
  `docs/CHECK_SCRIPT_CENSUS.md`'s corpus-wide tallies downstream); if you don't, no doc update is
  needed.
- Update `tests/test_validate_spine.py`'s floor if an all-null gate clears in either file (both
  currently have EVERY gate all-null — clearing even one condition in a gate clears that gate's
  fault).
- Full `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` green.
- This run's map is DEGRADED-UNPARSEABLE — do not build a promoted check that depends on map state
  this repo cannot currently produce.

## Allowed Scope
- `skills/cartographer/templates/CARTOGRAPHER.template.json`,
  `skills/scout/templates/SCOUT.template.json` (raw text hand-edit only).
- `.agent-work/templates/CARTOGRAPHER.template.json`,
  `.agent-work/templates/SCOUT.template.json` (overlay sync).
- `tests/test_checklist_engine.py` (new test class(es) only).
- `tests/test_validate_spine.py` (floor numbers only, if triggered).

## Specific Exclusions
Do not touch already-landed templates from prior gates. Do not touch `checklist_engine.py`.

## Constraints
- `decision:no-new-check-kinds`.
- Report-only-with-trigger is the DEFAULT for both files given zero live check kinds today;
  blocking requires a stated override reason in your result.
- Compact-format JSON: raw text hand-edit, never `json.load`/`json.dump` round-trip.

## Map Anchors (inbound)
- **Map entry point:** `docs/CHECK_SCRIPT_CENSUS.md`'s unwired-script list
  (`check_role_spine_bookends.py`, `check_skill_freshness.py`), `docs/CHECKLIST_SCHEMA.md`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human · leans g7-implement`;
  `decision:blocking-where-adjudicated` — report-only branch applies by default here
  `@grade: settled/human · leans g7-implement`.
- **Map confidence flags:** repo map is DEGRADED-UNPARSEABLE — do not depend a promoted check on it.

## Deliverable Path Check
- **Committed** — `skills/cartographer/templates/CARTOGRAPHER.template.json`,
  `skills/scout/templates/SCOUT.template.json`; verify `git check-ignore` exits 1 for both.
- **Committed** — both overlay copies; same check.
- **Committed** — `tests/test_checklist_engine.py`, `tests/test_validate_spine.py` (if touched).

## Required Evidence
- `git diff -- skills/cartographer/templates/CARTOGRAPHER.template.json
  skills/scout/templates/SCOUT.template.json`.
- JSON parse-check output for both files.
- `python3 scripts/check_template_overlay_freshness.py` output.
- Full pytest output for the two test files.

## Wiring Grep
`grep -n '"check"' skills/cartographer/templates/CARTOGRAPHER.template.json
skills/scout/templates/SCOUT.template.json` before/after.

## Verification Commands
```bash
python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
python3 scripts/check_template_overlay_freshness.py
python3 -c "import json; json.load(open('skills/cartographer/templates/CARTOGRAPHER.template.json',encoding='utf-8')); json.load(open('skills/scout/templates/SCOUT.template.json',encoding='utf-8')); print('OK')"
```

## Suggested Model Tier
simple bounded.

## Authority
Report-only-by-default is already decided (Commander authority, per PLAN_CRITIC.md finding 3) —
do not ship blocking without a stated override reason. An honest zero in either or both files is
legitimate and pre-sanctioned.

## Stop Conditions
Stop and return if: a promotion candidate's only honest check kind is `artifact` with no
report-only shape and demoting it to null feels wrong (surface as a decision, don't guess); any
edit would require touching `checklist_engine.py`.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape. `Return status` lowercase. Write to
`.agent-work/w3-promote/crew-handoffs/g7-implementer-result.md` before ending your turn.
