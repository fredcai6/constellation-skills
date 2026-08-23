# Implementer Handoff

## Gate
g3-implement (execute.json, work-id w3-promote)

## Task
Promote real `check: null` conditions in `skills/admiral/templates/ADMIRAL_SPINE.template.json`
using only the engine's existing check kinds — per `decision:no-new-check-kinds`. Then red-proof
each promotion and sync the `.agent-work/templates/` overlay.

## Protected Intent
Same as g1: no decorative artifact conditions. A check that cannot fail is worse than the honest
`check: null` it replaces.

## Test Mode
Test-after allowed.

## Close Criteria
Promote exactly these conditions (fresh-verify each against the real shipped JSON first — the
counts/shapes below are this Commander's own hand-assessment, not guaranteed final; if your fresh
read disagrees, say so and adjust, do not force a fit):
1. `init.c2` ("engine session lease claimed for this spine (admiral owns the state)") → `command`,
   same seam as `g1`'s already-landed `COMMANDER_SPINE.template.json` `init.c1` promotion. The
   exact shipped shape (mirror it verbatim, substituting only the `<work-id>` placeholder context
   if your template uses a different one — check first):
   `{"kind": "command", "command": "python3 -c \"import json,sys; d=json.load(open('<repo-root>/.agent-work/<work-id>/spine.json', encoding='utf-8')); sys.exit(0 if d.get('engine_session',{}).get('status')=='active' else 1)\""}`.
   Per PLAN_CRITIC.md finding 3, confirm independently that `command`-kind is ALSO justified
   against THIS template's own existing checks (ADMIRAL_SPINE already has live `command`-kind
   checks elsewhere in the file — confirm by grep, cite the specific sibling condition).
2. `latitude.c1` ("latitude contract written with decision classes, float-up routing, and
   expiry") → existence-only promotion for the fixed-path file
   `.agent-work/<work-id>/LATITUDE_CONTRACT.md`. Use `artifact` (evidence_type of your choosing,
   e.g. `"latitude-contract"`, match `{"exists": true}`) OR `command` (a shell check for file
   existence + nonempty) — pick whichever this template's own existing check-kind mix favors
   (grep the file first). The judgment half ("decision classes, float-up routing, expiry" are
   *good*) is NOT this check's job — sibling `latitude.c2` already covers human confirmation.
3. `execute.c2` ("ADMIRAL_LOG current through the last wave...") → `command`, existence+pattern
   ONLY: verify `.agent-work/<work-id>/ADMIRAL_LOG.md` is non-empty AND contains at least one line
   matching the imperative's own documented grammar (`^- TRANSITION`). "Current through the last
   wave" (freshness) is NOT checkable and stays unpromoted — do not overclaim.
4. `closeout.c4` ("branches dispositioned, worktrees swept, ADMIRAL_LOG archived") → ONLY IF a
   real, stable path convention for "ADMIRAL_LOG archived" can be confirmed (check
   `scripts/spine_lifecycle.py`'s archive-move logic for the actual destination path pattern) —
   promote a `command` check for THAT existence fact only. If no stable path convention exists,
   leave this condition `check: null` and say so explicitly in your result; do not invent a path.
- Every other `check: null` condition in this file stays untouched.
- `.agent-work/templates/ADMIRAL_SPINE.template.json` byte-matches the edited
  `skills/admiral/templates/ADMIRAL_SPINE.template.json`.
- A red-proof test class in `tests/test_checklist_engine.py` (adjacent to g1's own new class,
  same pattern: pinned HEAD, skipTest on drift, adversary-chosen mutations per condition).
- If any all-null gate in this file clears (check whether `init`, `latitude`, `execute`, or
  `closeout` currently have ALL postconditions null — if promoting one of your conditions clears
  one, update `tests/test_validate_spine.py`'s floor per the same discipline as g1).
- Full `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` green.

## Allowed Scope
- `skills/admiral/templates/ADMIRAL_SPINE.template.json` (raw text hand-edit only).
- `.agent-work/templates/ADMIRAL_SPINE.template.json` (overlay sync).
- `tests/test_checklist_engine.py` (new test class only).
- `tests/test_validate_spine.py` (floor numbers only, if triggered).

## Specific Exclusions
Do not touch `skills/commander/templates/COMMANDER_SPINE.template.json` or its overlay (g1 owns
it, already landed on this branch by the time you run). Do not touch `checklist_engine.py`.

## Constraints
- `decision:no-new-check-kinds`.
- `decision:blocking-where-adjudicated` — ship blocking for conditions that reuse a kind already
  live in THIS template; if a candidate would be the FIRST use of that kind in this specific file,
  say so explicitly and consult the Commander before shipping it blocking (name it as a stop
  condition rather than guessing).
- Compact-format JSON: raw text hand-edit, never `json.load`/`json.dump` round-trip.

## Map Anchors (inbound)
- **Map entry point:** `docs/CHECK_SCRIPT_CENSUS.md`, `docs/CHECKLIST_SCHEMA.md`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human · leans g3-implement`;
  `decision:blocking-where-adjudicated` `@grade: settled/human · leans g3-implement`.

## Deliverable Path Check
- **Committed** — `skills/admiral/templates/ADMIRAL_SPINE.template.json`; verify
  `git check-ignore skills/admiral/templates/ADMIRAL_SPINE.template.json` exits 1.
- **Committed** — `.agent-work/templates/ADMIRAL_SPINE.template.json`; same check.
- **Committed** — `tests/test_checklist_engine.py`, `tests/test_validate_spine.py` (if touched).

## Required Evidence
- `git diff -- skills/admiral/templates/ADMIRAL_SPINE.template.json`.
- JSON parse-check command output.
- `python3 scripts/check_template_overlay_freshness.py` output.
- Full pytest output for the two test files.

## Wiring Grep
`grep -n '"check"' skills/admiral/templates/ADMIRAL_SPINE.template.json` before/after.

## Verification Commands
```bash
python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
python3 scripts/check_template_overlay_freshness.py
python3 -c "import json; json.load(open('skills/admiral/templates/ADMIRAL_SPINE.template.json',encoding='utf-8')); print('OK')"
```

## Suggested Model Tier
simple bounded — mirrors g1's already-proven pattern.

## Authority
Which conditions to promote is a first-pass judgment call from the Commander (this handoff), not
frozen — if your fresh read of the real JSON disagrees with a specific item above, say so and
adjust rather than forcing it; report the correction plainly in your result.

## Stop Conditions
Stop and return if: a promotion would be the first use of its check kind in this template and you
are unsure whether it should ship blocking or report-only; `closeout.c4`'s archive path convention
cannot be confirmed; any edit would require touching `checklist_engine.py`.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape. `Return status` lowercase. Write to
`.agent-work/w3-promote/crew-handoffs/g3-implementer-result.md` before ending your turn.
