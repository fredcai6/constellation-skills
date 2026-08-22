# Implementer Handoff

## Gate
g2 (g2-implement)

## Task
Hand-author a `basis` field onto exactly three conditions in the shipped `skills/commander/templates/COMMANDER_SPINE.template.json`: `plan.c2`, `plan.c4`, `plan.c5` — the mechanism g1 just shipped (`scripts/checklist_engine.py`, report-only `basis` field, `file`/`evidence_ref` locator kinds). Sync the `.agent-work/templates/` overlay mirror. Write a red-proof integration test against the real shipped file, pinned to this gate's shipped git SHA.

## Protected Intent
Do not touch any condition other than `plan.c2`, `plan.c4`, `plan.c5`. Every other condition in this template (including `plan.c1`, `reconcile.c1`, `archive.c2`, `init.c1` — deliberately deferred to triage per `PLAN_ALTERNATIVES.md`) must be byte-identical before and after your edit.

## Test Mode
TDD required for the new integration test (write it against the pre-edit template first — it should fail because the fields don't exist yet — then make it pass by editing the template).

## Close Criteria
- `skills/commander/templates/COMMANDER_SPINE.template.json` gains a `"basis": {...}` sibling key on exactly these three condition objects (their EXACT current text, confirmed live at this gate's dispatch — quote-match before editing, since the file may have shifted since this handoff was authored):
  - Line ~55: `{"id": "c2", "statement": "execute.json authored from the converged candidate plan, one bounded issue, gates carry anchors cut from the frame, and every file and decision-class in the issue's stated file-ownership scope has its own gate", "check": null, "satisfied": false}` (in the `plan` task's postconditions) — add `"basis": {"locator_kind": "file", "locator": {"path": ".agent-work/<work-id>/execute.json"}, "because": "execute.json's own existence is checkable; whether its gates are genuinely cut from the frame and cover the full ownership scope stays a human/reviewer judgment call"}`.
  - Line ~57: `{"id": "c4", "statement": "plan-alternatives run BEFORE execute.json is authored...", "check": null, "satisfied": false}` — add `"basis": {"locator_kind": "file", "locator": {"path": ".agent-work/<work-id>/plan-candidate-*.md", "glob": true, "min_matches": 2}, "because": "at least 2 candidate files must exist for a real design-it-twice panel to have run; PLAN_ALTERNATIVES.md's own convergence and the ordering claim stay a judgment call no file check can make"}`.
  - Line ~58: `{"id": "c5", "statement": "cold plan critic run on the converged candidate plan + mission frame...", "check": null, "satisfied": false}` — add `"basis": {"locator_kind": "file", "locator": {"path": ".agent-work/<work-id>/PLAN_CRITIC.md"}, "because": "the critic's findings file must exist; whether it was genuinely cold-read and triaged stays a judgment call"}`.
  - The exact `basis` JSON shape must match what g1 actually shipped — re-confirm against `docs/CHECKLIST_SCHEMA.md`'s new "Basis" subsection (search for `locator_kind`) before writing these, since the handoff's example shapes above are this Commander's best understanding at plan time, not a guarantee the implemented field names didn't shift slightly during g1.
- Edit surgically: locate each condition's exact existing text in the raw file and insert `, "basis": {...}` immediately before its closing `}` (after `"satisfied": false`). Do **not** run the file through `json.load`/`json.dump` to make this edit — that reflows the whole compact-format file and destroys git blame for every other line. Use a text edit tool that only touches the target substring.
- After editing, re-validate with a **read-only** `json.load` (parse-check only, discard the result) to confirm the file is still valid JSON.
- Sync `.agent-work/templates/COMMANDER_SPINE.template.json` and `.agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json` — apply the identical edit to both (or copy the shipped file's bytes over both, whichever is more surgical) so all three copies stay byte-identical, per `PLAN_CRITIC.md` finding 7.
- New integration test (in `tests/test_checklist_engine.py`, a new test class, e.g. `CommanderSpineBasisFields`) pinned to this gate's shipped git SHA per `ruling-red-proof-pinned-to-shipped-revision` — get the SHA via `git rev-parse HEAD` at implementation time and assert against it (e.g. skip or fail loudly if HEAD has moved, per the corpus's existing convention for revision-pinned tests — check how another test in this file already does this, if one does, and follow that convention rather than inventing a new one). The test must:
  1. Load the real shipped `skills/commander/templates/COMMANDER_SPINE.template.json` (not a fixture).
  2. Confirm `plan.c2`, `plan.c4`, `plan.c5` each carry a well-formed `basis` object matching the shapes above.
  3. Confirm every OTHER condition in the file has no `basis` key (byte-identical protected-intent check — enumerate all conditions, assert only these 3 have the key).
  4. Build a live checklist from this template (however the existing test suite already constructs one from a shipped template — follow that pattern) and confirm `current`/`render_human` shows the `basis:` sub-line at `plan.c2`/`c4`/`c5` when those gates are active and open.
- Full `tests/test_checklist_engine.py` suite passes, including the new test and every pre-existing test (especially `GoldenOutputBriefing` and `TemplateOnlyFieldAllowlist` — confirm they still pass with a real `basis` field now present in a shipped template for the first time; this is the first live exercise of g1's render code against real content, watch for it).
- Also confirm `skills/commander/templates/COMMANDER_SPINE.template.json` is still accepted by whatever validates a shipped template at install time (`scripts/install_constellation.py` or its own test coverage) — a shape g1's engine accepts must also be accepted by anything else that independently parses/validates this template family; check for such a validator and run it if one exists, note if none does.

## Allowed Scope
- `skills/commander/templates/COMMANDER_SPINE.template.json` (exactly 3 conditions edited)
- `.agent-work/templates/COMMANDER_SPINE.template.json` and `.agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json` (sync only, same edit)
- `tests/test_checklist_engine.py` (new integration test class only — do not modify existing tests)

## Specific Exclusions
- `scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md` — g1's scope, already shipped and reviewed; do not touch.
- Any condition in `COMMANDER_SPINE.template.json` other than `plan.c2`/`plan.c4`/`plan.c5` — this includes `plan.c1`, `reconcile.c1`, `archive.c2`, `init.c1`, all preconditions, and everything in every other gate.
- `scripts/generate_spine.py`, `specs/` — whole-epic exclusion.
- `checklist_engine.py`'s `waive()`/forced-claim-release/`consolidate --override-reason`/`trip_ledger` — w2-ledger lane fence (not applicable to this gate's files, stated for completeness).

## Constraints
- Hand-edit the compact-format JSON template surgically — never `json.load`/`json.dump` round-trip it.
- The three `basis` objects' exact field values (`path`, `glob`, `min_matches`, `because`) must match whatever g1 actually implemented — verify against `docs/CHECKLIST_SCHEMA.md`'s Basis subsection and, if genuinely ambiguous, against `scripts/checklist_engine.py`'s `_resolve_basis_locator` source directly, not against this handoff's illustrative JSON alone.
- `<work-id>` in the `locator.path` values is a literal placeholder in the shipped template — this template is instantiated per-run by `init_work_area.py`'s placeholder substitution (same convention every other `<work-id>`-bearing string in this file already uses); do not resolve it to `w2-basis` in the shipped file.

## Map Anchors (inbound)
- **Map entry point:** `skills/commander/templates/COMMANDER_SPINE.template.json` — start by reading the live `plan` task block in full (lines ~40-65) before editing anything.
- **Structural:** `skills/commander/templates/COMMANDER_SPINE.template.json:plan.c2/c4/c5`, `.agent-work/templates/` overlay mirror.
- **Capability:** the basis field mechanism g1 shipped (`scripts/checklist_engine.py`, report-only, `file`/`evidence_ref` locator kinds).
- **Constraints/assumptions:** `ruling-engine-first-backfill-where-it-earns-it` (exactly these 3 conditions, not a rollout) | `ruling-basis-lives-in-hand-written-templates` (this IS a hand-written template, edited surgically) | `ruling-red-proof-pinned-to-shipped-revision` (pin the test to this gate's shipped SHA).
- **Decision anchors:** the three conditions and their exact locator shapes are ratified in `.agent-work/w2-basis/PLAN_ALTERNATIVES.md` (post-critic-revision) — not open for re-derivation.
  `@grade: settled/human`
- **Evidence expectations:** g1's `IMPLEMENTER_RESULT`/`docs/CHECKLIST_SCHEMA.md` Basis subsection is the authoritative shape reference for what field names/defaults actually shipped.

## Deliverable Path Check
- **Committed** — `skills/commander/templates/COMMANDER_SPINE.template.json`; `git check-ignore` exited 1 (not ignored).
- **Committed** — `.agent-work/templates/COMMANDER_SPINE.template.json` and `.agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json`; `git check-ignore` on both exited 1 (not ignored — confirmed together with the shipped path above).
- **Committed** — `tests/test_checklist_engine.py`; already confirmed not ignored at g1.

## Required Evidence
- **Load-bearing**: the new integration test's red-then-green transcript (fails against the pre-edit template, passes after).
- **Load-bearing**: full `tests/test_checklist_engine.py` suite result (exact pass count).
- **Load-bearing**: a diff of the exact JSON inserted at each of the 3 conditions (paste the before/after substrings, not just "I added a basis field").
- **Confirmatory**: `diff` output (or byte-equality check) confirming the shipped file and both overlay copies are identical after your edit.
- **Confirmatory**: the `git rev-parse HEAD` your red-proof test is pinned to.

## Wiring Grep
```bash
grep -c '"basis"' skills/commander/templates/COMMANDER_SPINE.template.json
```
Expect exactly 3 (one per edited condition — this is a direct count of your own edit, not a caller-wiring check; state it as such).

## Verification Commands
```bash
cd /home/tommy/projects/569-w2-basis && python3 -c "import json; json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json')); print('parses ok')"
cd /home/tommy/projects/569-w2-basis && diff skills/commander/templates/COMMANDER_SPINE.template.json .agent-work/templates/COMMANDER_SPINE.template.json && echo "overlay matches"
cd /home/tommy/projects/569-w2-basis && diff skills/commander/templates/COMMANDER_SPINE.template.json .agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json && echo "baseline matches"
cd /home/tommy/projects/569-w2-basis && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q tests/test_checklist_engine.py
```

## Suggested Model Tier
simple bounded — reason: a narrow, precisely-specified template edit plus one integration test; g1 already did the hard design/engine work, this gate applies it.

## Authority
The three target conditions and their basis shapes are ratified in `.agent-work/w2-basis/PLAN_ALTERNATIVES.md`. Do not add basis to any other condition even if it looks like it would "complete the picture" — that was deliberately and explicitly scoped out (see the plan's "leave everything else check: null" item).

## Stop Conditions
Stop and return if: the live template's `plan.c2`/`c4`/`c5` text has diverged from what this handoff quotes in a way that makes the target insertion point ambiguous, g1's actual shipped `basis` shape differs materially from what this handoff assumes (verify against `docs/CHECKLIST_SCHEMA.md` before proceeding, don't guess), or the overlay/baseline files are not currently byte-identical to the shipped file before you start (that would mean pre-existing drift unrelated to this gate — report it, don't silently fix or ignore it).

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/w2-basis/crew-handoffs/g2-implementer-result.md` before ending your turn.
