# Implementer Handoff

## Gate
g5-implement (execute.json, work-id w3-promote)

## Task
Promote real `check: null` conditions in `skills/charter/templates/CHARTER.template.json` using
only the engine's existing check kinds — per `decision:no-new-check-kinds`. Then red-proof each
promotion and sync the `.agent-work/templates/` overlay.

## Protected Intent
Same as g1/g3/g4: no decorative artifact conditions. A check that cannot fail is worse than the
honest `check: null` it replaces. Note: CHARTER runs once per repo (bootstrap), not per-issue like
COMMANDER_SPINE — a false-negative here is cheaper to hit but also cheaper to notice/fix by hand, so
do not let that lower the bar for what counts as a genuine promotion.

## Test Mode
Test-after allowed.

## Close Criteria
Promote exactly these conditions (fresh-verify each against the real shipped JSON first — the
counts/shapes below are this Commander's own hand-assessment, not guaranteed final; if your fresh
read disagrees, say so and adjust, do not force a fit):
1. `project-templates.c1` ("project-specific templates seeded") → `artifact`, enum-match on
   `status` in `{"seeded", "skipped-no-need"}` — same shape as COMMANDER_SPINE's already-landed
   `plan.c1` (g1, committed). Cite that shape, verify it independently fits this condition's own
   statement text before copying it.
2. `closeout.c1` ("durable outputs complete; work area archived") → SPLIT, existence-only: promote
   only the "work area archived" half (a real, checkable fact — confirm the actual archive
   mechanism/path convention this skill uses, e.g. via `scripts/spine_lifecycle.py` or CHARTER's own
   closeout tooling, the same way g3's ADMIRAL_SPINE assessment checked before committing to a
   path). "Durable outputs complete; no open questions; contradiction pass done" stays judgment/null
   — do not overclaim. If no stable archive-path convention can be confirmed, leave the whole
   condition `check: null` and say so (do not invent a path — same fallback g3 used for
   `closeout.c4`).
3. `interrogate.c1` ("doctrine resolved to role-operable decisions") → WEAK candidate, ONLY if a
   real, reusable verifier for `interrogation.json`'s terminal state already exists in this repo.
   Check first (grep for an `interrogation.json`-reading script or a `--phase interrogate`-style
   verifier). If none exists, leave `check: null` — do not invent a new verifier
   (`decision:no-new-check-kinds` bars new mechanism, and a bespoke script written just for this
   promotion would be exactly that).
- Do NOT touch `orchestrator-context.c1` or `agent-guide.c1` — both already carry real checks
  (confirmed: only their PRECONDITIONS are null, which are gate-order-guaranteed and stay null, same
  pattern as COMMANDER_SPINE's own preconditions).
- Every other `check: null` condition in this file stays untouched.
- `.agent-work/templates/CHARTER.template.json` byte-matches the edited
  `skills/charter/templates/CHARTER.template.json`.
- A red-proof test class in `tests/test_checklist_engine.py` (adjacent to g1's/g3's/g4's own
  classes, same pattern: pinned HEAD, skipTest on drift, adversary-chosen mutations per promoted
  condition).
- If any all-null gate in this file clears, update `tests/test_validate_spine.py`'s floor per the
  same discipline as g1/g3/g4 (message text AND numeric floor if the count actually drops below the
  current threshold — check what the current floor number is before editing).
- Full `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` green.

## Allowed Scope
- `skills/charter/templates/CHARTER.template.json` (raw text hand-edit only).
- `.agent-work/templates/CHARTER.template.json` (overlay sync).
- `tests/test_checklist_engine.py` (new test class only).
- `tests/test_validate_spine.py` (floor numbers/message only, if triggered).

## Specific Exclusions
Do not touch `COMMANDER_SPINE.template.json`, `ADMIRAL_SPINE.template.json`, or
`EXPLORER_SPINE.template.json` or their overlays (g1/g3/g4 own them, already landed/landing on this
branch). Do not touch `checklist_engine.py`.

## Constraints
- `decision:no-new-check-kinds`.
- `decision:no-basis-backfill` — do NOT add a `basis` field to any condition, even a SPLIT
  promotion. A prior gate this wave (g4) made exactly this mistake by citing an out-of-wave
  precedent (COMMANDER_SPINE's own `plan.c2/c4/c5`, which predates this wave's own pre-rulings) —
  do not repeat it. Split promotions in this wave leave the `statement` text unchanged and add NO
  `basis` object; the uncovered judgment half is documented in your IMPLEMENTER_RESULT and the
  red-proof test's docstring, not in the shipped JSON.
- `decision:blocking-where-adjudicated` — ship blocking for conditions that reuse a kind already
  live in THIS template; if a candidate would be the FIRST use of that kind in this specific file,
  say so explicitly and consult the Commander before shipping it blocking.
- Compact-format JSON: raw text hand-edit, never `json.load`/`json.dump` round-trip.

## Map Anchors (inbound)
- **Map entry point:** `docs/CHECK_SCRIPT_CENSUS.md`, `docs/CHECKLIST_SCHEMA.md`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human`;
  `decision:no-basis-backfill` `@grade: settled/human`;
  `decision:blocking-where-adjudicated` `@grade: settled/human`.

## Deliverable Path Check
- **Committed** — `skills/charter/templates/CHARTER.template.json`; verify
  `git check-ignore skills/charter/templates/CHARTER.template.json` exits 1.
- **Committed** — `.agent-work/templates/CHARTER.template.json`; same check.
- **Committed** — `tests/test_checklist_engine.py`, `tests/test_validate_spine.py` (if touched).

## Required Evidence
- `git diff -- skills/charter/templates/CHARTER.template.json`.
- JSON parse-check command output.
- `python3 scripts/check_template_overlay_freshness.py` output.
- Full pytest output for the two test files.

## Wiring Grep
`grep -n '"check"' skills/charter/templates/CHARTER.template.json` before/after.

## Verification Commands
```bash
python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
python3 scripts/check_template_overlay_freshness.py
python3 -c "import json; json.load(open('skills/charter/templates/CHARTER.template.json',encoding='utf-8')); print('OK')"
```

## Suggested Model Tier
simple bounded — mirrors g1's/g3's/g4's already-proven pattern.

## Authority
Which conditions to promote is a first-pass judgment call from the Commander (this handoff), not
frozen — if your fresh read of the real JSON disagrees with a specific item above, say so and
adjust rather than forcing it; report the correction plainly in your result.

## Stop Conditions
Stop and return if: a promotion would be the first use of its check kind in this template and you
are unsure whether it should ship blocking or report-only; `closeout.c1`'s archive-path convention
cannot be confirmed; `interrogate.c1`'s reusable verifier cannot be confirmed to exist; any edit
would require touching `checklist_engine.py`.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape. `Return status` lowercase. Write to
`.agent-work/w3-promote/crew-handoffs/g5-implementer-result.md` before ending your turn.
