# Implementation Result

## Assigned gate
g2-implement: declare the bookends in the role spine templates

## Completed slice
Declared `"bookend": true` on exactly six gates across the three role spine templates (Commander
`init`/`archive`, Admiral `init`/`closeout`, Explorer `init`/`route`), and pinned the exact set
with a new test class. All six choices from the handoff's reasoning table were accepted as-is —
none looked wrong on inspection of `_is_bookend` and its call sites in `scripts/checklist_engine.py`.

## Scope
**Files changed:**
- `skills/commander/templates/COMMANDER_SPINE.template.json` — added `"bookend": true` to `tasks.init` and `tasks.archive` only; nothing else touched.
- `skills/admiral/templates/ADMIRAL_SPINE.template.json` — added `"bookend": true` to `tasks.init` and `tasks.closeout` only.
- `skills/explorer/templates/EXPLORER_SPINE.template.json` — added `"bookend": true` to `tasks.init` and `tasks.route` only.
- `tests/test_checklist_engine.py` — added `ShippedTemplateBookendDeclarations` (the pinning test), and added `"bookend"` to `TemplateOnlyFieldAllowlist.ALLOWLIST` with a stated reason (see Evidence below — this was discovered as a real gap by the full suite, not anticipated).

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `skills/implementer/templates/IMPLEMENTER_PLAN.template.json`, `specs/*.spine.toml`, `scripts/generate_spine.py`, `scripts/run_crew.py`, `scripts/install_constellation.py`, `LAUNCH_ORDER.template.md`, `map/INDEX.md` were all left untouched. No mutating engine verb was ever run against a live spine — every `amend`/`start`/`advance` in this run targeted either my own `IMPLEMENTER_PLAN.json` (driven per the constellation-implementer skill, no bound spine was found — `SPINE_PARENT` only, `SPINE_FILE`/`SPINE_SESSION` unset) or throwaway copies in `/tmp`.

## Behavior changed
Yes. `init`/`archive` (Commander), `init`/`closeout` (Admiral), and `init`/`route` (Explorer) are
now frozen against `drop`, `rescope`, and `retext-check` via `amend`, and no gate can land after
the closing bookend. Before this change the flag existed in the engine (#634) but nothing declared
it, so the guard protected nothing — this is the change that makes it live.

## Map Impact
Skipped — mechanical template edit adding a single declared field per the handoff's exact
six-gate table; no structural, capability, constraint, or decision impact beyond what #634 already
recorded when it built the mechanism.

## Test mode
**Required:** test-first (TDD, test-led for the pinning test)
**Satisfied:** yes — red observed before the declarations landed, green observed after.

## Evidence

### 1. RED — pinning test against the undeclared templates
```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py -k Bookend
```
**Result:** 3 subtests failed (one per template), each reporting `got=[]` against the expected
two bookend gates, e.g.:
```
AssertionError: Items in the second set but not the first:
'init'
'archive' : COMMANDER_SPINE.template.json: expected bookend gates ['archive', 'init'], got []
```
`3 failed, 11 passed, 456 deselected` (the 11 passing are #634's pre-existing engine-mechanism
tests, unaffected by this change).

### 2. Declarations landed; templates still parse and instantiate
Confirmed by `python3 -c "json.load(...)"` on all three edited files (all parsed), and by
instantiating each through the real path:
```
python scripts/init_work_area.py test-commander --root <tmp> --spine skills/commander/templates/COMMANDER_SPINE.template.json
python scripts/init_work_area.py test-admiral   --root <tmp> --spine skills/admiral/templates/ADMIRAL_SPINE.template.json
python scripts/init_work_area.py test-explorer  --root <tmp> --spine skills/explorer/templates/EXPLORER_SPINE.template.json
```
(`--skill-dir` omitted — auto-detected, since this is a source repo with top-level bundled
`scripts/`, not an installed skill directory.) Each produced a `spine.json` whose `tasks` dict
carries the expected `bookend: true` pair, confirming the flag survives instantiation unchanged.

### 3. GREEN — pinning test after the declarations
```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py -k Bookend
```
**Result:** `11 passed, 456 deselected, 3 subtests passed` — all three templates now have exactly
the intended two bookend gates.

### 4. Full required suites (handoff's required verification commands)
```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py
```
First run **failed** unexpectedly: `TemplateOnlyFieldAllowlist.test_shipped_templates_carry_no_unaccounted_task_fields`
refused the new `bookend` field on shipped templates because it wasn't yet on that test's own
stated allowlist (`466 passed`, 1 failed). This is a real, previously-undeclared corpus-wide guard
(#475) that I hadn't anticipated in the plan — not a bug in the guard. Fix: added `"bookend"` to
`TemplateOnlyFieldAllowlist.ALLOWLIST` with a one-line stated reason. Re-run:
**Result:** `467 passed, 143 subtests passed` — full green.

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_generate_spine.py tests/test_init_work_area.py
```
**Result:** `202 passed` — green, confirming `generate_spine.py`'s fixed-field-list compile path
(deliberately untouched) still behaves, and template instantiation is unaffected.

### 5. End-to-end proof: live refusal, on a copy, fresh process
Built a synthetic fixture from `skills/commander/templates/COMMANDER_SPINE.template.json` (the
same shape `probe-closing-bookend.md` used): `init`/`context`/`understand`/`plan` complete,
`execute` in-progress, rest pending — saved to a temp-dir copy, never a live spine. Then, in a
fresh `python scripts/checklist_engine.py` process:
```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
    python scripts/checklist_engine.py --file <tmp>/copy.json amend \
    --delta <tmp>/delta.json --reason "e2e proof: is the declared closing bookend now frozen?" \
    --authority "g2-implementer"
REFUSED: drop archive: a declared bookend gate cannot be dropped, regardless of status
Recovery: amend's drop only applies to a pending gate; archive is 'pending' and no verb reaches a
pending status from here -- escalate to a human if the plan genuinely needs to change. Do not edit
the JSON — use the engine.
exit: 1
```
delta was `{"ops":[{"op":"drop","id":"archive"}]}` — the exact delta `probe-closing-bookend.md`
measured succeeding silently (`exit 0`) at `9b38b9d9`, before #634's guard and before this
declaration. Confirmed the copy was left unmutated (`archive` still present, `items` unchanged).
No live spine (`.agent-work/567-k/spine.json`, `.agent-work/567-k/execute.json`,
`.agent-work/epic-567-door/spine.json`) was ever the target of a mutating verb.

## TDD evidence, if required
- Failing test observed: see Evidence §1 above.
- Passing test observed: see Evidence §3 above.
- Refactor while green: no refactor needed.

## Docs/contracts touched
- none. `docs/CHECKLIST_SCHEMA.md`'s Task field table was left as-is: `SchemaDocFieldReconciliation`
  (existing test) only fails if the doc *documents* a field absent from
  `_builder_task_keys() | ALLOWLIST`; a field the allowlist carries but the doc omits is
  explicitly stated as not itself a failure there, and that test stayed green untouched.

## Assumptions
- The handoff's "on those gates and no others" is read as a top-level task-object key
  (`task["bookend"] = true`), matching `_is_bookend`'s `new_tasks[tid].get("bookend")` read in
  `scripts/checklist_engine.py:3054` and the existing `AmendBookendGuard` test fixtures
  (`tests/test_checklist_engine.py:1697` etc.) — not a nested field under `postconditions` or
  elsewhere.

## Stop conditions hit
- none. All six gate choices matched what `_is_bookend`'s call sites actually enforce; none looked
  wrong. Every template still instantiates. The pinning test failed first as required.

## Out-of-scope observations
- none beyond what's already floated in the handoff (`IMPLEMENTER_PLAN.template.json` /
  `generate_spine.py` compile-path durability hole) — left untouched as instructed.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: task, intent, exact six-gate table, exclusions,
  required verification commands, test mode, and stop conditions were all present and unambiguous.
- **Context rediscovered:** `TemplateOnlyFieldAllowlist` (#475) — a corpus-wide test that any new
  template-only task field must be added to a stated allowlist or the full suite refuses it. The
  handoff's required verification commands (`pytest tests/test_checklist_engine.py`) would have
  surfaced this regardless, so nothing was lost, but a handoff for "add a new template-only field"
  work could save a step by naming this guard up front (mirrors the durability-hole note it already
  gives for `generate_spine.py`).
- **Instructions improvised around:** none. The skill's "no spine bound" path (`SPINE_PARENT` set,
  `SPINE_FILE`/`SPINE_SESSION` unset) matched a documented shape exactly, so I authored my own
  `IMPLEMENTER_PLAN.json` from `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` and
  drove it via the bundled `scripts/checklist_engine.py` CLI rather than the MCP door, per the
  constellation-implementer skill's own branch for that case.
- **What would have made this easier:** none — the handoff's exact-key table and stop conditions
  made the actual edits close to mechanical; the only friction was the allowlist test, noted above.

## Return status
`complete`
