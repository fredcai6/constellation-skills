# Implementer Handoff

## Gate
g4-implement (execute.json, work-id w3-promote)

## Task
Promote real `check: null` conditions in `skills/explorer/templates/EXPLORER_SPINE.template.json`
using only the engine's existing check kinds — per `decision:no-new-check-kinds`. Then red-proof
each promotion and sync the `.agent-work/templates/` overlay.

## Protected Intent
Same as g1/g3: no decorative artifact conditions. A check that cannot fail is worse than the honest
`check: null` it replaces.

## Test Mode
Test-after allowed.

## Close Criteria
Promote exactly these conditions (fresh-verify each against the real shipped JSON first — the
counts/shapes below are this Commander's own hand-assessment, not guaranteed final; if your fresh
read disagrees, say so and adjust, do not force a fit):
1. `init.c2` ("engine session lease claimed for this spine (explorer owns the state)") → `command`,
   same seam as g1's landed `COMMANDER_SPINE.template.json` `init.c1` and g3's landed
   `ADMIRAL_SPINE.template.json` `init.c2`. Confirm independently that `command`-kind is ALSO
   justified against THIS template's own existing checks (grep first, cite the specific sibling
   condition already `command`-kind in this file — do not rely on the other two templates' seam
   alone, per PLAN_CRITIC.md finding 3).
2. `context.c1` ("doctrine + project deltas + map read where they exist; IDEAS_BOARD.md seeded from
   template") → SPLIT, existence-only: promote only the "IDEAS_BOARD.md seeded from template" half
   (a real fixed-path file, e.g. `artifact` or `command` existence+nonempty check — pick whichever
   this template's own existing check-kind mix favors). The "doctrine + project deltas + map read"
   half is judgment/comprehension — do NOT promote it, and do NOT let the `statement` text imply the
   check covers more than it does. This mirrors COMMANDER_SPINE's own `context.c1`, which stayed
   null for the identical reason — do not over-promote here just because a locator exists for part
   of it.
3. `spec.c1` ("DESIGN_SPEC.md crystallized from the board with per-section approval; load-bearing
   interfaces designed-it-twice or skipped with a stated reason") → SPLIT, existence-only: promote
   only "DESIGN_SPEC.md crystallized" (file exists, e.g. `artifact` match `{"exists": true}` or a
   `command` test). "Per-section approval" and "designed-it-twice fidelity" stay judgment/null — do
   not overclaim. Same split shape as COMMANDER_SPINE's `plan.c2`.
4. `route.c1` ("confirmed spec routed (handed off / shaped-design issue filed / shelved with
   UNCONFIRMED header); work area archived; engine lease released") → potential FULL promotion via
   an `artifact` enum-match on the 3 named outcomes, if and only if each of the 3 outcomes
   (handed-off, issue-filed, shelved-UNCONFIRMED) has its own real, independently-checkable
   artifact. Verify this claim yourself against the imperative text and any existing routing
   tooling before committing to the match enum — if any one outcome lacks a real artifact, do not
   force a fit: fall back to existence-only for the outcomes that do have one, or leave the whole
   condition `check: null` and say so.
- Every other `check: null` condition in this file stays untouched.
- `.agent-work/templates/EXPLORER_SPINE.template.json` byte-matches the edited
  `skills/explorer/templates/EXPLORER_SPINE.template.json`.
- A red-proof test class in `tests/test_checklist_engine.py` (adjacent to g1's/g3's own classes,
  same pattern: pinned HEAD, skipTest on drift, adversary-chosen mutations per promoted condition).
- If any all-null gate in this file clears (check whether `init`, `context`, `spec`, `route`, or
  any other gate currently has ALL postconditions null — if promoting one of your conditions clears
  one, update `tests/test_validate_spine.py`'s floor per the same discipline as g1/g3).
- Full `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` green.

## Allowed Scope
- `skills/explorer/templates/EXPLORER_SPINE.template.json` (raw text hand-edit only).
- `.agent-work/templates/EXPLORER_SPINE.template.json` (overlay sync).
- `tests/test_checklist_engine.py` (new test class only).
- `tests/test_validate_spine.py` (floor numbers only, if triggered).

## Specific Exclusions
Do not touch `COMMANDER_SPINE.template.json` or `ADMIRAL_SPINE.template.json` or their overlays (g1
and g3 own them, already landed on this branch). Do not touch `checklist_engine.py`.

## Constraints
- `decision:no-new-check-kinds`.
- `decision:blocking-where-adjudicated` — ship blocking for conditions that reuse a kind already
  live in THIS template; if a candidate would be the FIRST use of that kind in this specific file,
  say so explicitly and consult the Commander before shipping it blocking (name it as a stop
  condition rather than guessing).
- Compact-format JSON: raw text hand-edit, never `json.load`/`json.dump` round-trip.

## Map Anchors (inbound)
- **Map entry point:** `docs/CHECK_SCRIPT_CENSUS.md` (`verify_spec_confirmed.py` and
  `verify_cycles.py`'s existing live wiring in THIS file), `docs/CHECKLIST_SCHEMA.md`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human`;
  `decision:blocking-where-adjudicated` `@grade: settled/human`.

## Deliverable Path Check
- **Committed** — `skills/explorer/templates/EXPLORER_SPINE.template.json`; verify
  `git check-ignore skills/explorer/templates/EXPLORER_SPINE.template.json` exits 1.
- **Committed** — `.agent-work/templates/EXPLORER_SPINE.template.json`; same check.
- **Committed** — `tests/test_checklist_engine.py`, `tests/test_validate_spine.py` (if touched).

## Required Evidence
- `git diff -- skills/explorer/templates/EXPLORER_SPINE.template.json`.
- JSON parse-check command output.
- `python3 scripts/check_template_overlay_freshness.py` output.
- Full pytest output for the two test files.

## Wiring Grep
`grep -n '"check"' skills/explorer/templates/EXPLORER_SPINE.template.json` before/after.

## Verification Commands
```bash
python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
python3 scripts/check_template_overlay_freshness.py
python3 -c "import json; json.load(open('skills/explorer/templates/EXPLORER_SPINE.template.json',encoding='utf-8')); print('OK')"
```

## Suggested Model Tier
simple bounded — mirrors g1's/g3's already-proven pattern.

## Authority
Which conditions to promote is a first-pass judgment call from the Commander (this handoff), not
frozen — if your fresh read of the real JSON disagrees with a specific item above, say so and
adjust rather than forcing it; report the correction plainly in your result.

## Stop Conditions
Stop and return if: a promotion would be the first use of its check kind in this template and you
are unsure whether it should ship blocking or report-only; `route.c1`'s 3-outcome enum cannot be
confirmed to have real per-outcome artifacts; any edit would require touching `checklist_engine.py`.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape. `Return status` lowercase. Write to
`.agent-work/w3-promote/crew-handoffs/g4-implementer-result.md` before ending your turn.
