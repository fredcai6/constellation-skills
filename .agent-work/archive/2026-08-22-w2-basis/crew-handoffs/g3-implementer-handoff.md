# Implementer Handoff

## Gate
g3 (g3-implement)

## Task
Update `docs/CHECK_SCRIPT_CENSUS.md`'s condition counts to reflect this wave's change (3 of `COMMANDER_SPINE.template.json`'s 19 `check: null` conditions now carry a `basis` field), and run `python -m scripts.code_map build --root .` so `map/INDEX.md` doesn't go stale.

## Protected Intent
Don't touch the substance of `docs/CHECK_SCRIPT_CENSUS.md`'s prior findings (the `generate_spine.py` disposition, the #368/#444 re-measurement) — only the specific counts this wave's change affects, and only by adding accurate, dated new information, not by rewriting prior committed prose.

## Test Mode
Inspection-only — this is a doc + generated-artifact gate, no code changes, no test surface beyond the pre-existing map freshness test.

## Close Criteria
- `docs/CHECK_SCRIPT_CENSUS.md` around lines 126-152 (the `generate_spine.py` disposition section, which cites `grep -c '"because"' skills/commander/templates/COMMANDER_SPINE.template.json` → 0 against 19 `check: null` conditions) gets a short, dated addendum: 3 of those 19 (`plan.c2`, `plan.c4`, `plan.c5`) now carry a `basis` field (epic-569 w2-basis) — state plainly that `basis` is a distinct mechanism from `because` (report-only locator + always-attached `basis-check` evidence, vs. `generate_spine.py`'s prose-folded-into-statement convention) and is unaffected by anything this census section says about the compiler. Re-run `grep -c '"because"' skills/commander/templates/COMMANDER_SPINE.template.json` (expect 0, unchanged) and `grep -c '"basis"' skills/commander/templates/COMMANDER_SPINE.template.json` (expect 3) fresh, and paste both outputs alongside the doc edit as your evidence — do not just assert the numbers.
- Run `python -m scripts.code_map build --root .` and confirm it completes (expect ~2.9s, deterministic) and `map/INDEX.md`/`map/ids.jsonl` are refreshed if the build changed anything (this wave added no new Python symbols, only edited existing files and JSON/doc content, so the map build may be a no-op — confirm with `git status --porcelain map/` and report whichever is true, don't assume).
- The map-freshness test (whatever `tests/test_code_map.py` or similar runs) still passes after the build.
- Full local `pytest -q` (the whole suite, not just `test_checklist_engine.py`) passes — this is the last gate before `reconcile`, so it's the first point this wave runs the FULL suite rather than the targeted file.

## Allowed Scope
`docs/CHECK_SCRIPT_CENSUS.md`, `map/INDEX.md`, `map/ids.jsonl` (only if the build actually changes them).

## Specific Exclusions
Everything g1/g2 already touched (`scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, `skills/commander/templates/COMMANDER_SPINE.template.json`, the overlay copies, `tests/test_checklist_engine.py`) — do not re-touch any of them in this gate.

## Constraints
- Date-stamp the addendum you add to `docs/CHECK_SCRIPT_CENSUS.md` (per global-everyone.md's "pin a claim to the revision you read it at") — cite the git SHA the grep counts were measured against.

## Map Anchors (inbound)
- **Map entry point:** `docs/CHECK_SCRIPT_CENSUS.md:108-152` (the `generate_spine.py` disposition section this addendum extends).
- **Structural:** `map/INDEX.md` (repo-wide code map, rebuilt by `scripts/code_map build`).
- **Evidence expectations:** the re-run grep commands from `docs/CHECK_SCRIPT_CENSUS.md:126-127`, re-measured at this gate's HEAD.

## Deliverable Path Check
- **Committed** — `docs/CHECK_SCRIPT_CENSUS.md`; not gitignored (doc under `docs/`).
- **Committed** — `map/INDEX.md`, `map/ids.jsonl`; not gitignored (tracked generated artifacts per Inherited Context).

## Required Evidence
- **Load-bearing**: the two fresh grep outputs (because count, basis count) pasted verbatim.
- **Load-bearing**: full `pytest -q` (whole suite) result — exact pass/fail/skip counts.
- **Confirmatory**: `git status --porcelain map/` output showing whether the map build changed anything.

## Wiring Grep
none — this gate adds no new callable symbol, only doc text and a regenerated map artifact.

## Verification Commands
```bash
cd /home/tommy/projects/569-w2-basis && grep -c '"because"' skills/commander/templates/COMMANDER_SPINE.template.json
cd /home/tommy/projects/569-w2-basis && grep -c '"basis"' skills/commander/templates/COMMANDER_SPINE.template.json
cd /home/tommy/projects/569-w2-basis && python -m scripts.code_map build --root .
cd /home/tommy/projects/569-w2-basis && git status --porcelain map/
cd /home/tommy/projects/569-w2-basis && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q
```

## Suggested Model Tier
simple bounded — reason: a scoped doc addendum plus running an existing, deterministic map-build script.

## Authority
The counts to report are mechanically derived (grep), not a judgment call.

## Stop Conditions
Stop and return if: the full suite reveals failures unrelated to this wave's changes (report them, don't attempt to fix unrelated red — that's a triage candidate, not this gate's job), or `docs/CHECK_SCRIPT_CENSUS.md`'s cited line numbers have moved enough that the addendum's insertion point is ambiguous.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/w2-basis/crew-handoffs/g3-implementer-result.md` before ending your turn.
