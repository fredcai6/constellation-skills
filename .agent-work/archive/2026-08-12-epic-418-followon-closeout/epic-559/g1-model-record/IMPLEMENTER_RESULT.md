# Implementation Result

## Assigned gate
`epic-559/g1-model-record` — G1: the registry does not record what model a crew ran at

## Completed slice
`scripts/run_crew.py`'s `CliBackend.dispatch` now passes `model=spec.model` into its
`build_entry(...)` call, matching the `ExternalBackend.dispatch` call site. A registry entry
for a spawned (cli-backend) crew now carries `model` whenever `--model` was given, the same as
an externally-dispatched entry already did.

## Scope
**Files changed:**
- `scripts/run_crew.py` — `CliBackend.dispatch`'s `build_entry(...)` call now passes
  `model=spec.model`; updated `build_entry`'s docstring `model` bullet, which previously
  documented the drop as intentional ("the cli path does not store it") — that sentence was
  itself wrong and needed to change with the fix.
- `tests/test_crew_launcher.py` — added
  `BackendEquivalenceTests.test_cli_dispatch_records_model_when_given`, the red control and its
  permanent green pin.
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`) after the new test
  function changed the repo's entity count; not itself edited by hand.

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `scripts/validate_spine.py`,
`scripts/generate_spine.py`, `settings.json`, `.mcp.json`, and everything under `skills/` are
untouched. No retroactive registry backfill. No merge or push to `main`.
`scripts/install_constellation.py` was not run.

## Behavior changed
Yes. A crew dispatched through the cli backend with `--model <x>` now gets a registry entry
carrying `"model": "<x>"`. Previously that entry had no `model` key at all — indistinguishable
from a crew dispatched with no `--model`. Entries for crews dispatched without `--model` are
unaffected (no `model` key, unchanged — `build_entry` still only stores a truthy value).
Historical entries already written are not touched; the past stays unknowable, as scoped.

## Map Impact
- **Structural anchors touched:** `scripts/run_crew.py:CliBackend.dispatch`,
  `scripts/run_crew.py:build_entry` — one call-site argument added, one docstring bullet
  corrected; no new symbol, no signature change.
- **Capabilities added/changed/affected:** the crew registry (`crew-runs.json`) now records
  `model` for cli-backend entries, closing the gap named in the handoff — a reader of the
  registry can now tell "no `--model` given" apart from "given and dropped" on the cli path,
  the same distinction the external path already supported.
- **Constraints/assumptions touched:** the handoff's premise — "every spawned crew in this
  repo's history has a registry entry with no `model` key" — is confirmed as a defect, not
  a spec; going forward, spawned entries with `--model` are symmetric with recorded entries.
- **Trust limitations / drift found:** none beyond what's reported in the asymmetry
  enumeration below.

## Test mode
**Required:** `test-first` (TDD red → green)
**Satisfied:** yes — red observed against unfixed code, then the fix, then green.

## Evidence

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_crew_launcher.py -k 'model'
```
**Result:** pass — `4 passed, 156 deselected` (post-fix; includes the new red-control test now
green, plus `test_external_dispatch_records_without_spawning_returns_none`,
`test_external_entry_keeps_dispatch_marker_pidless_and_model`, `test_falsy_model_is_not_stored`).

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
**Result:** pass — `2690 passed, 3 skipped, 1121 subtests passed` (baseline was `2689 passed, 3
skipped, 1121 subtests`; the +1 is the new test. Zero regressions.) One transient failure was
observed and resolved mid-run: `MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
went red because the new test function shifted the repo's map entity count (4117 → 4118);
`python -m scripts.code_map build --root .` regenerated `map/INDEX.md` and the suite went green
on the next run.

## TDD evidence, if required

**Failing test observed** (against unfixed code — `CliBackend.dispatch` not yet passing `model=`):

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_crew_launcher.py -k test_cli_dispatch_records_model_when_given

F                                                                        [100%]
=================================== FAILURES ===================================
______ BackendEquivalenceTests.test_cli_dispatch_records_model_when_given ______

self = <test_crew_launcher.BackendEquivalenceTests testMethod=test_cli_dispatch_records_model_when_given>

    def test_cli_dispatch_records_model_when_given(self):
        ...
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result):
                code, entry = RC.CliBackend().dispatch(spec, root=root, entries=entries)
            self.assertEqual(0, code)
>           self.assertEqual("sonnet", entry["model"])
                                       ^^^^^^^^^^^^^^
E           KeyError: 'model'

tests/test_crew_launcher.py:2305: KeyError
=========================== short test summary info ============================
FAILED tests/test_crew_launcher.py::BackendEquivalenceTests::test_cli_dispatch_records_model_when_given
1 failed, 159 deselected in 0.09s
```

This reproduces the Admiral's finding directly: `--model sonnet` reaches `CrewSpec.model` and
`build_crew_argv` correctly forwards it to the child `claude -p` process, but the registry entry
built by `CliBackend.dispatch` carries no `model` key.

**Passing test observed** (after adding `model=spec.model` to the cli `build_entry(...)` call):

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_crew_launcher.py -k 'model'
....                                                                     [100%]
4 passed, 156 deselected in 0.04s
```

**Refactor while green:** yes — updated `build_entry`'s docstring `model` bullet (previously
described the cli path's omission as by-design; now describes the symmetric behavior and names
the historical defect), no behavior change from that edit.

## Asymmetry enumeration (task 4)

Comparing the two `build_entry(...)` call sites in `scripts/run_crew.py` argument by argument
(`CliBackend.dispatch`, now line 1106; `ExternalBackend.dispatch`, line 1232), post-fix:

| argument | cli call | external call | symmetric? |
|---|---|---|---|
| `work_id` | `spec.work_id` | `spec.work_id` | yes |
| `gate` | `spec.gate` | `spec.gate` | yes |
| `role` | `spec.role` | `spec.role` | yes |
| `attempt` | `spec.attempt` | `spec.attempt` | yes |
| `worktree` | `spec.worktree` | `spec.worktree` | yes |
| `handoff` | `spec.handoff` | `spec.handoff` | yes |
| `result` | `spec.result` | `spec.result` | yes |
| `root` | `root` | `root` | yes |
| `started` | `started` (`_now()`, called locally) | `started` (`_now()`, called locally) | yes — same source shape |
| `backend` | `self.name` (`"cli"`) | `self.name` (`"external"`) | yes — correctly differs by design (that's the field's job) |
| `spine` | `spec.spine` | `spec.spine` | yes |
| `parent` | `spec.parent` | `spec.parent` | yes |
| `model` | `spec.model` **(this fix)** | `spec.model` | **yes, now** — was the bug: cli omitted this argument entirely |
| `pid` | `os.getpid()` | `None` | **no — by design.** `build_entry`'s own docstring: "the spawning process (cli) or `None` (external, PID-less)." The external backend spawns nothing, so there is no PID to record. Pinned by `test_cli_entry_carries_backend_cli_and_pid_no_dispatch` and `test_external_dispatch_records_without_spawning_returns_none`. |
| `dispatch` | not passed (defaults to `None`) | `DISPATCH_EXTERNAL` | **no — by design.** `build_entry`'s docstring, Decision 5: "external keeps its legacy `dispatch: "external"` marker … the cli backend passes `None` (no marker, as before)." Pinned by `EntryBackendTests` (`test_explicit_backend_wins`, `test_legacy_external_dispatch_infers_external`, `test_legacy_no_marker_infers_cli`) and `BuildEntryTests.test_cli_entry_carries_backend_cli_and_pid_no_dispatch`. |

**`model` was the only unintentional asymmetry.** `pid` and `dispatch` remain asymmetric, and
both are by design: `pid` because the external backend spawns no process to have one, and
`dispatch` because it is the legacy backend-type marker the external path alone needs. Both are
documented in `build_entry`'s own docstring and each has a dedicated pinning test predating this
change. No other field differs between the two call sites.

## Docs/contracts touched
- `scripts/run_crew.py` — `build_entry`'s docstring `model` bullet corrected to match the fixed
  behavior (see Evidence/TDD sections above).

## Assumptions
- none

## Stop conditions hit
- none — the reproduction confirmed the defect exactly as the handoff described, and the fix
  was the single-argument change the handoff named.

## Out-of-scope observations
- none — the asymmetry enumeration in task 4 found no further asymmetries beyond the two
  by-design ones (`pid`, `dispatch`) already documented and tested.

## Workflow Feedback

- **Handoff gaps:** none. Task, intent, scope, exclusions, evidence, test mode, and stop
  conditions were all present and accurate; the reproduction matched on the first attempt.
- **Context rediscovered:** `build_entry`'s own docstring (scripts/run_crew.py:830-857)
  documented the cli path's `model` omission as the *intended* shape ("matching the prior
  per-path shape; the cli path does not store it") — the handoff didn't mention this, so the
  fix required noticing the docstring would go stale/self-contradictory if left unchanged after
  the code fix, and updating it as part of the same slice rather than leaving stale
  documentation that re-asserts the just-fixed bug as a feature.
- **Instructions improvised around:** the full-suite run (`m4-suite`) hit an unrelated but
  mechanically-caused failure — `MapTreeFreshnessTests` — because the new test function shifted
  `map/`'s tracked entity count. `map/` isn't named in the handoff's `In:`/`Out:` scope lists at
  all. Treated it as the generated-artifact-regeneration case from `global-crew.md`
  ("generated artifact → regenerate/check evidence") rather than a blocker, since regenerating
  it (`python -m scripts.code_map build --root .`) is mechanical, touches no hand-authored
  content, and is required for the stated test-mode command to pass at all.
- **What would have made this easier:** the handoff could note that `map/INDEX.md` is a tracked
  generated artifact that test-mode's full-suite run will flag stale after any change that
  shifts the repo's map-relevant entity count, and that regenerating it via
  `python -m scripts.code_map build --root .` is in scope even though `map/` isn't named in
  `In:`/`Out:`.

## Return status
`complete`
