# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`x1-installed-bundle` / `x2-survey-terminal` / `x3-verify` (rework spine `REWORK2_PLAN.json`, implementer) — work id `epic-559/a-spine-is-the-job`

## Completed slice
Both blockers named in `REWORK2_HANDOFF.md`, all three gates driven to `complete`:

1. **`run_crew.py` was dead on every installed bundle.** `2152ded3` added a bare, module-scope `import install_constellation` to `run_crew.py` (for `assert_shell_safe_command`), but no bundle carrying `run_crew.py` (Commander, Explorer) shipped `install_constellation.py` as a sibling — verified two-sidedly with a real install: `python <installed>/scripts/run_crew.py --help` raised `ModuleNotFoundError: No module named 'install_constellation'` before argparse ever ran. Fixed by declaring `"run_crew.py": ("install_constellation.py",)` in `SCRIPT_RUNTIME_COMPANIONS` (`scripts/install_constellation.py`) — `expand_script_bundle` already applies that automatically to every skill bundling `run_crew.py`, so no hand-edit of `SKILL_SCRIPT_BUNDLES` was needed. `checklist_engine.py`'s own import (already a declared companion of both bundles) was untouched, per the handoff's own diagnosis.
2. **The companion guard itself was blind to every script but one.** The guard that pins `SCRIPT_RUNTIME_COMPANIONS` against reality was `test_engine_runtime_siblings_are_declared_as_companions`, keyed to the literal string `"checklist_engine.py"` (plus a second, separately hand-written copy for `gauge_writer_hook.py`) — it watched exactly those two scripts and nothing else, which is why the `run_crew.py` regression landed one file over from where the drift class is documented and the suite stayed green. Generalized: `CompanionGuardCoversEveryScriptTests` derives every script bundled by *any* skill from `SKILL_SCRIPT_BUNDLES` (not a hand-picked name) and asserts each script's actual runtime-reachable closure (via the existing AST-walking `_direct_runtime_siblings`/`engine_runtime_closure` helpers) lands inside that skill's own expanded bundle.
3. **A reviewer that records no verdict was recorded `completed`.** `spine_terminal` judged a spine-only crew's completion with `checklist_engine.active_id(...) is None` alone, which walks item statuses and never reads `consolidation` — a real reviewer-crew survey with every item recorded but `consolidation: None` was recorded `completed`, telling the Commander a review was done when no verdict existed anywhere. Fixed: for `checklist.get("type") == checklist_engine.SURVEY`, `spine_terminal` now also requires `consolidation is not None`. `checklist_engine.py` stayed untouched (out of scope); the type-aware check lives in `run_crew.py` with a comment noting the cleaner long-term shape is a type-aware `is_terminal` owned by the engine.
4. **Same function, smaller: valid-JSON-wrong-shape leaked as terminal.** `active_id` walks `cl.get("items", [])`, so `{}` and `{"items": []}` both find no non-terminal item and return `None` — terminal by vacuity, directly contradicting `spine_terminal`'s own docstring ("a missing/unparseable/malformed spine is never terminal"). Fixed by requiring a non-empty `items` list (and a `dict` shape) before consulting `active_id` at all; the already-correct missing-file/unparseable-JSON paths are untouched.

Also, while generalizing the companion guard, surfaced and fixed a real pre-existing false positive in the shared AST/regex test helper `_direct_runtime_siblings`: its "dynamic path load" regex scanned raw source TEXT, including comments. `install_constellation.py` carries a `#`-comment describing `checklist_engine`'s own dynamic `gauge_reader.py` load (`# checklist_engine._load_gauge_reader() -> Path(__file__).parent/"gauge_reader.py"`), and an unfiltered scan misread that prose as `install_constellation.py` itself performing the load — a false sibling edge that, once this helper was generalized beyond the two scripts whose own source happened to carry no such commentary about itself, dragged `gauge_reader.py` into every script transitively reaching `install_constellation.py` (including `install_constellation.py` bundled directly by `write-a-skill`). Fixed by blanking `#`-comment text (via `tokenize`, not a naive `#`-split — a `#` inside a string literal is not a comment) before the regex runs.

Regenerated `map/INDEX.md`: entity count drifted (`scripts` and `tests` both grew from the new tests/companion entry) — `python -m scripts.code_map build --root .`.

## Scope
**Files changed:**
- `scripts/run_crew.py`
- `scripts/install_constellation.py`
- `tests/test_crew_launcher.py`
- `tests/test_install_constellation.py`
- `map/INDEX.md` (mechanical regeneration)

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `settings.json`, `docs/agents/*`, and `skills/*/templates/` were not modified.

## Behavior changed
Yes.
- An installed Commander or Explorer bundle's `run_crew.py` now imports and runs (`--help` and every real invocation) instead of raising `ModuleNotFoundError` at import.
- `run_crew.py --spine <s>` (no `--result`) now correctly reports `failed`/exit 1 for a `type: survey` spine whose items are all recorded but `consolidation` is still `None` — it previously reported `completed`/exit 0 in that case. It also now correctly reports `failed` for a malformed-shape spine (`{}`, `{"items": []}`) where it previously reported `completed`.
- The runtime-companion guard (test-only, no production behavior change) now covers every script any skill bundles, not just `checklist_engine.py`/`gauge_writer_hook.py`.

## Map Impact
- **Structural anchors touched:** `scripts.run_crew:spine_terminal` (survey-consolidation + malformed-shape checks added), `scripts.install_constellation:SCRIPT_RUNTIME_COMPANIONS` (new `run_crew.py` entry), `tests.test_install_constellation:_direct_runtime_siblings`/`_without_comments` (comment-blind regex fix), `tests.test_install_constellation:CompanionGuardCoversEveryScriptTests` (new, generalized guard).
- **Capabilities added/changed/affected:** a Commander/Explorer bundle installed from this repo can now actually launch a crew via `run_crew.py` (previously silently could not, in every install). A spine-only reviewer/interrogator dispatch is now judged correctly on its recorded verdict, not just its item statuses.
- **Constraints/assumptions touched:** `SCRIPT_RUNTIME_COMPANIONS`'s documented invariant ("a bundled script that loads a sibling at runtime must ship that sibling, or the feature silently no-ops wherever installed") now actually holds for every bundled script, not just the two it was hand-checked against.
- **Decision candidates / resolved decisions:** confirmed the ruling named in the handoff — the type-aware terminal check for a survey belongs in `run_crew.py` for now, with the seam commented for a future engine-owned `is_terminal`.
- **Trust limitations / drift found:** the retext-checked `x2-survey-terminal.c1` command in `REWORK2_PLAN.json` originally had an unquoted `pytest -k SurveyTerminal or MalformedSpine`, which `checklist_engine._run_check_command`'s `[shell, "-c", command]` invocation splits into bogus positional pytest arguments (`file or directory not found: or`) — an authoring bug in the check text itself, unconditionally failing independent of implementation correctness. Corrected via `spine_amend`/`retext-check` (quoted the `-k` expression) after verifying the corrected command collects and passes the intended 4 tests; see the spine's amend log for the full reasoning.
- **Triage candidates:** none beyond what pass 2's result already flagged (`recover_crews.py`'s spine-unaware `classify_entry`, `test_mcp_adoption.py`'s stale `DOOR_TOOL_NAMES`/`CLI_ONLY_VERBS` pin) — both explicitly out of this pass's scope and left untouched.

## Test mode
**Required:** test-first / evidence-only
**Satisfied:** yes — verified genuinely red pre-fix for all three fixes:
- `run_crew.py --help` from a real installed commander/explorer bundle raised `ModuleNotFoundError` before the `install_constellation.py` companion fix (reproduced directly, see Evidence).
- `CompanionGuardCoversEveryScriptTests` fails against the pre-fix `SCRIPT_RUNTIME_COMPANIONS` (no `run_crew.py` entry) — `run_crew.py` (bundled by commander/explorer) reaches `install_constellation.py` at runtime but neither bundle's expanded set ships it.
- `SurveyTerminalTests.test_survey_with_every_item_recorded_but_no_consolidation_is_not_terminal` and both `MalformedSpineTests` fail against the pre-fix `spine_terminal` (returns `True` in all three cases).

## Evidence

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
**Result:** pass — `2563 passed, 1 skipped, 1120 subtests passed`

```bash
test $(python -m pytest -q tests/test_crew_launcher.py -k InstalledBundle --collect-only 2>/dev/null | grep -c '::') -ge 2 && \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m pytest -q tests/test_crew_launcher.py -k InstalledBundle
```
**Result:** pass — 2 tests collected, 2 passed (x1 gate `c1`: real installed commander/explorer bundle, `run_crew.py --help` runs clean).

```bash
test $(python -m pytest -q tests/test_install_constellation.py -k CompanionGuardCoversEveryScript --collect-only 2>/dev/null | grep -c '::') -ge 1 && \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m pytest -q tests/test_install_constellation.py -k CompanionGuardCoversEveryScript
```
**Result:** pass — 1 test collected, 1 passed, 15 subtests passed (x1 gate `c2`).

```bash
test $(python -m pytest -q tests/test_crew_launcher.py -k "SurveyTerminal or MalformedSpine" --collect-only 2>/dev/null | grep -c '::') -ge 4 && \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m pytest -q tests/test_crew_launcher.py -k "SurveyTerminal or MalformedSpine"
```
**Result:** pass — 4 tests collected, 4 passed (x2 gate `c1`, after correcting the check's own shell-quoting via `spine_amend`).

```bash
test -z "$(git status --porcelain -- scripts tests skills map)"
```
**Result:** pass after commit (x3 gate `c2`).

## TDD evidence, if required
- Failing test observed: `run_crew.py --help` `ModuleNotFoundError` from a real install (pre-fix); `CompanionGuardCoversEveryScriptTests` and `SurveyTerminalTests`/`MalformedSpineTests` fail against the pre-fix code — see Test mode above.
- Passing test observed: full suite green at `2563 passed, 1 skipped, 1120 subtests passed` with all fixes applied.
- Refactor while green: no refactor pass beyond the implementation; `map/INDEX.md` regeneration was mechanical.

## Docs/contracts touched
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`), enforced by `tests/test_code_map.py::MapTreeFreshnessTests`.

## Assumptions
- The generalized companion guard (`CompanionGuardCoversEveryScriptTests`) skips scripts whose source lives under a `SCRIPT_SOURCE_SUBDIRS` subdirectory (today just the hook pair, `gauge_writer_hook.py`/`spine_rail.py`): the shared AST/regex helpers resolve source and sibling existence directly under a flat `scripts_root`, so they cannot see a subdir-sourced script's real siblings without a larger refactor. That pair already has its own dedicated, layout-aware check (`HookScriptBundleTests`), so the skip does not leave a gap — treated as in-scope-but-minimal rather than reaching into `_direct_runtime_siblings` to make it subdir-aware for a set of exactly two files.
- `spine_amend`/`retext-check` on `x2-survey-terminal.c1` was a mechanical shell-quoting correction, not a scope or intent change: verified the failure was unconditional (independent of test content) by tracing it to `checklist_engine._run_check_command`'s literal `[shell, "-c", command]` invocation, and verified the corrected command collects and passes exactly the intended 4 tests before advancing.

## Stop conditions hit
- None.

## Out-of-scope observations
- (Carried from pass 2, still true, still untouched) `scripts/recover_crews.py::classify_entry` still classifies a `status: "completed"` spine-only entry as `STATE_NEEDS_ABANDON` whenever `has_result` is false, because it re-derives resolution from `entry.get("result")` rather than trusting the stored `status`. Not touched: `recover_crews.py` is outside this handoff's four in-scope files.
- (Carried from pass 2, still true, still untouched) `tests/test_mcp_adoption.py`'s `DOOR_TOOL_NAMES` (7)/`CLI_ONLY_VERBS` (5) pin a stale fact (N1 already made all 18 verbs door-reachable) — left untouched per the handoff's explicit instruction.

## Workflow Feedback

- **Handoff gaps:** none — the handoff named both blockers precisely (down to the exact `SCRIPT_RUNTIME_COMPANIONS.get('checklist_engine.py', ())` literal and the exact `spine_terminal`/`active_id` mechanism), and both reproduced exactly as described on the first try.
- **Context rediscovered:** `checklist_engine.SURVEY`/`GATED` constant names and `active_id`'s exact walk (`cl.get("items", [])`, hard-subscripted `cl["tasks"][iid]`) — read directly from `checklist_engine.py` rather than assumed, since the handoff correctly warned that file is a hard no-go to *edit* but reading it was necessary to get the `spine_terminal` fix's edge cases (empty dict, empty items list) exactly right.
- **Instructions improvised around:** the two postcondition-check commands for `x2-survey-terminal.c1` (`-k SurveyTerminal or MalformedSpine`, unquoted) and `x1-installed-bundle.c1`/`c2` (both correctly quoted, for contrast) revealed a real authoring inconsistency in how `REWORK2_PLAN.json`'s check commands were composed — one gate's `-k` expression was quoted, the sibling gate's was not, and only the unquoted one breaks under `checklist_engine._run_check_command`'s `[shell, "-c", command]` invocation. Traced the failure to that exact invocation (not a test-content problem) before using `spine_amend`/`retext-check` to fix the check text itself, per the tool's documented purpose ("retext-check a pending/in-progress gate's check text").
- **What would have made this easier:** running every postcondition check command through a real shell once at plan-authoring time (the same `[shell, "-c", command]` the engine itself uses) before handing the spine off would have caught the quoting bug before dispatch instead of mid-run.

## Return status
`complete`
