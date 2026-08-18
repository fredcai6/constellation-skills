# Implementation Result

## Assigned gate
`g2-implement`

## Completed slice
Added a pure, zero-I/O role x harness model-tier resolver to `scripts/run_crew.py`:
`ROLE_MODEL_TIERS` (module-level table), `ResolvedModel` (frozen dataclass), and
`resolve_model(role, harness, requested, reason)` — living beside `build_crew_argv`,
implementing all five branches from the handoff in exact order. Additive-only:
nothing in the module calls `resolve_model` yet (that wiring is g3).

## Scope
**Files changed:**
- `scripts/run_crew.py` — new `ROLE_MODEL_TIERS`, `ResolvedModel`, `resolve_model`, added beside `build_crew_argv`. No other edits.
- `tests/test_crew_launcher.py` — new `ResolveModelTests` class (13 tests). No other edits.

**Specific exclusions touched:** no — `CrewLaunchSpec`, `build_parser`, `build_entry`, `main`, `resume_crew` untouched; confirmed by the wiring grep below.

## Behavior changed
No — nothing existing calls the new code, so no observable dispatch behavior changed. The new functions are reachable only from the new test class and are otherwise dead code by design (this gate's contract).

## Map Impact
No architecture map exists in this repo (DEGRADED-UNPARSEABLE, waived by the Admiral this wave per the handoff's Map Anchors). Recording candidates in the handoff's own anchor vocabulary for whenever a map is reconstituted:

- **Structural anchors touched:** `scripts/run_crew.py` — new module-level `ROLE_MODEL_TIERS` table and `resolve_model`/`ResolvedModel` pair, placed beside `build_crew_argv`.
- **Capabilities added/changed/affected:** none observable yet — the resolver exists but is unwired (g3 wires it into `CrewLaunchSpec.__post_init__`, per Protected Intent).
- **Decision candidates / resolved decisions:** `decision:ship-todays-tiers`, `decision:fail-closed-cheaper`, `decision:refuse-by-name`, `decision:reason-on-deviation`, `decision:harness-dimension-is-required` — all consumed as given by the handoff, none revisited.
- **Trust limitations / drift found:** none found this gate.
- **Triage candidates:** none beyond what the handoff already scopes to g3 (wiring `resolve_model` into `CrewLaunchSpec.__post_init__`).

## Test mode
**Required:** `test-first (TDD)`
**Satisfied:** yes — `ResolveModelTests` written and observed failing (RED) before `resolve_model` existed, then implementation added to reach GREEN.

## Evidence

```bash
py -m pytest tests/test_crew_launcher.py -q
```

**Result:** pass (with one pre-existing, unrelated failure noted below).

Full output tail:
```
229 passed, 1 failed in 0.86s
FAILED tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound
```

That one failure is **pre-existing and unrelated**: `assertNotIn("CREW_SCRATCH_DIR", calls[0]["env"])` fails because *this crew's own dispatched-process environment* already carries `CREW_SCRATCH_DIR` (I am myself a `run_crew.py`-dispatched crew), which leaks into `os.environ.copy()`-based env construction the test inspects. Confirmed pre-existing (not introduced by this change): measured against a clean `git diff` of `scripts/run_crew.py`/`tests/test_crew_launcher.py` *before* any edit in this session — the baseline run (216 passed, 1 failed, 217 total) showed the identical single failure with the identical assertion, before `resolve_model` or `ResolveModelTests` existed.

**Delta, stated explicitly:** 216 pre-existing passed + 13 new = 229 passed; 217 pre-existing total + 13 new = 230 total; 0 pre-existing tests changed (the same 1 pre-existing failure, same test, same assertion, present both before and after).

```bash
py -m pytest tests/test_crew_launcher.py -k ResolveModelTests -q
```
**Result:** pass — `13 passed, 217 deselected`. Individual test names (13):
`test_every_populated_claude_role_resolves_to_its_own_default`,
`test_blank_string_requested_also_resolves_to_default`,
`test_out_of_set_model_is_refused_by_name`,
`test_codex_harness_refuses_by_name_branch_one`,
`test_local_harness_refuses_by_name_branch_one`,
`test_unknown_role_under_known_harness_refuses_by_name_branch_one`,
`test_non_default_in_set_choice_with_no_reason_is_refused`,
`test_non_default_in_set_choice_with_reason_succeeds_and_carries_reason`,
`test_default_tier_explicit_choice_never_requires_a_reason`,
`test_default_tier_explicit_choice_passes_reason_through_if_given`,
`test_resolved_model_is_a_frozen_dataclass`,
`test_role_model_tiers_allowed_values_are_frozenset`,
`test_codex_and_local_harnesses_are_declared_empty`.

```bash
grep -n "resolve_model\|ROLE_MODEL_TIERS" scripts/run_crew.py
```
**Result:** 6 matches, all inside the new table/dataclass/function's own definition and docstrings (lines 842, 847, 863, 869, 885, 896) — zero call sites elsewhere in the file. Additive-only confirmed by reading the file, not just running tests.

```bash
grep -rn "resolve_model" --include=*.py . | grep -v "def resolve_model"
```
**Result:** 12 matches — 2 in `scripts/run_crew.py` (a comment and a docstring reference, not a call), 10 in `tests/test_crew_launcher.py` (the new test file's own call sites). Zero call sites outside the new test file.

## TDD evidence, if required

- Failing test observed: `py -m pytest tests/test_crew_launcher.py -k ResolveModelTests -q` → `13 failed, 217 deselected` (`AttributeError: module 'run_crew' has no attribute 'resolve_model'`), before `ROLE_MODEL_TIERS`/`ResolvedModel`/`resolve_model` were added.
- Passing test observed: same command after implementation → `13 passed, 217 deselected`.
- Refactor while green: no refactor needed after first green implementation.

## Docs/contracts touched
- none — this gate is additive-only, no wiring or contract surface changed.

## Assumptions
- none beyond the handoff's own stated values (table contents, branch order, error-message content requirements).

## Stop conditions hit
- none — all five branches expressed as pure standalone logic with no need to touch `CrewLaunchSpec`; no existing test broke.

## Out-of-scope observations
- none found.

## Workflow Feedback

- **Handoff gaps:** none — task, intent, allowed scope, specific exclusions, required evidence, test mode, and stop conditions were all present and sufficient to execute without guessing.
- **Context rediscovered:** this crew's `SPINE_FILE`/`SPINE_SESSION` environment (inherited unchanged, not freshly minted — my own `crew-runs.json` entry records `"spine": null`) pointed at the **Commander's own live `spine.json`** (session `constellation/567-j/lane-j/commander-delegated`), not an implementer-scoped spine. `spine_status` returned the Commander's `execute` gate content rather than a refusal. Attempting `spine_bind` to my own authored `IMPLEMENTER_PLAN.json` was correctly **refused** by the door ("this door still holds an active lease... as 'constellation/567-j/lane-j/commander-delegated'"), because releasing that lease to rebind would have released the Commander's real, live lease out from under it — a destructive side effect on shared state, not something to do to satisfy my own bootstrap. I drove my own `IMPLEMENTER_PLAN.json` (written to my crew scratch dir) through `scripts/checklist_engine.py`'s CLI directly instead, touching the Commander's spine not at all. This matches a previously-recorded pattern (this same class of `run_crew.py` dispatch env-inheritance quirk) and is worth fixing durably in `run_crew.py`/the dispatch env-setup so a handoff-only (non-`--spine`) crew does not inherit a live parent session identity it must not touch.
- **Instructions improvised around:** the constellation-implementer skill's opening instruction assumes "a dispatched crew's spine is bound for you before you start" is always true and always safe to drive; it is not, when `run_crew.py` dispatches with `--handoff`/`--result` (no `--spine`) and the env still carries the parent's `SPINE_FILE`/`SPINE_SESSION` unchanged. I fell back to the skill's own documented alternate path (author `IMPLEMENTER_PLAN.json` from the template, drive it via the bundled `checklist_engine.py`) rather than the door.
- **What would have made this easier:** `run_crew.py` could unset/clear `SPINE_FILE`/`SPINE_SESSION` in a dispatched child's environment when the dispatch is handoff-only (no `--spine` given), rather than leaving the parent's identity ambiently reachable — that would make `spine_status`'s "no spine is bound to this door" refusal fire immediately and correctly, instead of a crew discovering the mismatch only after reading spine content that clearly belongs to a different role/gate.

## Return status
`complete`
