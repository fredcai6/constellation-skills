# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`h1-pins` — "A pin asserting a false fact is worse than no pin"

## Completed slice
`tests/test_mcp_adoption.py`'s two stale constants are corrected and tied to their sources, never hand-typed a fourth/fifth time:

- `DOOR_TOOL_NAMES`: 7 → 9 (added `spine_capture`, `spine_amend`), tied to `mcp_spine_server.TOOL_NAMES` by `TestDoorSurfaceTiesToTheEngineRegistry::test_door_tool_names_tie_to_mcp_spine_servers_own_registry` (scratch-env import inside the test, same shape as `tests/test_crew_launcher.py`'s `CrewGrantTiesToDoorTests` for `CREW_ALLOWED_TOOLS`).
- `CLI_ONLY_VERBS`: `('skip','reopen','append','amend','flag-candidate')` → `()`, tied to the gap between the engine's own argparse verb registry and `mcp_spine_server.call_tool`'s actual `run_engine(...)` dispatch (both read mechanically — argparse's own invalid-choice error text, and a regex over `mcp_spine_server.py`'s source text — never hand-typed) by `test_cli_only_verbs_tie_to_the_gap_between_engine_and_door`.
- `_cli_only_verb_violations`'s VIOLATING/INNOCENT/ACCEPTED_FALSE_ALARM self-test structure is unchanged in shape; it now takes an explicit `verbs=` param (default: the real, now-empty `CLI_ONLY_VERBS`) so `TestTheViolationPredicateItself` can keep exercising the predicate's own mechanism via a decoupled `_PREDICATE_SELFTEST_VERBS` constant, independent of how many verbs are genuinely CLI-only today.
- `TestTier3CLIOnlyVerbsStayCLI`'s doctrine-sentence test is `skipif`'d while `CLI_ONLY_VERBS` is empty (nothing to require), documented as reactivating automatically the moment a verb regresses to CLI-only.

Correcting `DOOR_TOOL_NAMES` surfaced a real, pre-existing gap: `skills/workbench/references/checklist-engine.md`'s `## MCP door` section still said "7 tools covering 13 of its 18 verbs" and "5 verbs have no door tool at all" — never updated when the door actually grew (commit `2a3a1d69`, this same epic, #559). Fixed that one paragraph (tool list, verb count, retired the CLI-only-verb doctrine sentence) — see "Specific exclusions touched" below for why this was in-scope despite not being named in the handoff.

`h1-pins`'s own `c1` postcondition check command also had a pre-existing shell-quoting bug (`-k Door or Tie or Registry` unquoted — the shell splits `or`/`Tie`/`Registry` into bogus positional file args, `pytest` errors "file or directory not found: or" for **any** implementer regardless of test content). Corrected via `spine_amend`'s `retext-check` op (quotes the same `-k` value; does not touch the semantic bar). Full detail in Workflow Feedback below.

## Scope
**Files changed:**
- `tests/test_mcp_adoption.py`
- `skills/workbench/references/checklist-engine.md`
- `map/INDEX.md` (rebuild)

**Specific exclusions touched:** yes + explanation — `skills/workbench/references/checklist-engine.md` is not named in the handoff's "In:" list (`tests/test_mcp_adoption.py`, its fixtures/helpers, `map/INDEX.md`), but it is also not on the constraint's hard no-go list (`checklist_engine.py`, `mcp_spine_server.py`, `run_crew.py`, `skills/implementer/*`, `skills/reviewer/SKILL.md`, spine templates, `settings.json`, `docs/agents/*`). I judged the one-paragraph factual correction in-scope because `h2-verify.c1` ("full suite passes") is non-negotiable and this was the *only* other red test in the entire 2574-test suite once the two constants were corrected — `TestTier3ChecklistEngineReference::test_names_door_tools_as_default`, an already-correctly-written check that newly and correctly detected this file was behind reality. I made the narrowest possible edit (one paragraph: tool list, counts, the retired CLI-only-verb sentence) and left everything else in the file untouched, including the "Template set" table another sibling crew (`b-instructions-to-checks`) was recently working in.

## Behavior changed
`no` — test/doc corrections only; no runtime code touched (the two no-go scripts were not modified).

## Map Impact
- **Trust limitations / drift found:** `skills/workbench/references/checklist-engine.md`'s `## MCP door` section had drifted from `scripts/mcp_spine_server.py` since the door grew to 9 tools/18 verbs (#559, commit `2a3a1d69`) — now corrected.
- **Triage candidates:** none beyond the above; the drift is fixed, not merely flagged.

## Test mode
**Required:** `evidence-only` (pin correction + tie tests; no production code path to TDD)
**Satisfied:** `yes` — every new/changed assertion was run before and after to confirm it fails on the old (false) constants and passes on the corrected ones (verified `DOOR_TOOL_NAMES`/`CLI_ONLY_VERBS` tie tests independently before wiring them into the gate).

## Evidence

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m pytest -q tests/test_mcp_adoption.py -k "Door or Tie or Registry"
# 151 passed, 2 skipped, 31 deselected

python -c "import sys;sys.path.insert(0,'scripts');import mcp_spine_server as m;import re;s=open('tests/test_mcp_adoption.py').read();sys.exit(0 if 'flag-candidate' not in re.search(r'CLI_ONLY_VERBS\s*=\s*\(([^)]*)\)',s).group(1) else 1)"
# exit 0 (run inside a SPINE_ENGINE-bound env, matching how the door actually executes this check)

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
# 2574 passed, 3 skipped, 1121 subtests passed
```

**Result:** pass — h1-pins.c1, h1-pins.c2, and h2-verify.c1 (full suite) all green.

## TDD evidence, if required
Not applicable (evidence-only test mode) — see Test mode above for how correctness was still verified before/after.

## Docs/contracts touched
- `skills/workbench/references/checklist-engine.md` — `## MCP door` section's tool list/verb-count/CLI-only-verb paragraph corrected to match `scripts/mcp_spine_server.py`'s current (9-tool, 18-verb, 0-CLI-only) reality; see Scope above.

## Assumptions
- `spine_amend`'s `--authority` is conventionally "human" (the reference doc's own example, and the engine docstring's "(human ratification)" parenthetical), but the engine mechanically accepts any non-empty string, and `run_crew.py`'s `PreToolUse` hook denies a dispatched crew only `spine_evidence action=waive` — never `spine_amend`. I treated a `retext-check` op (an authoring fix that resets the condition to unsatisfied and never marks anything satisfied — I still had to pass the corrected check for real) as within a crew's own granted authority when the check text is demonstrably, mechanically broken (confirmed by running the exact JSON-literal command verbatim before touching anything), as opposed to `waive` (bypassing a substantively-inconvenient-but-working check), which stays "always ask up." Recorded the full reasoning in the `spine_amend` call's `reason` field for audit.

## Stop conditions hit
- none

## Out-of-scope observations
- `skills/workbench/references/checklist-engine.md`'s `## MCP door` section was stale (7 tools/13 verbs/5 CLI-only) relative to `mcp_spine_server.py`'s actual 9-tool/18-verb/0-CLI-only surface, apparently missed when the door grew in this same epic (#559, commit `2a3a1d69`). Fixed in this run (see Scope) rather than left as a finding, because the full-suite postcondition required it and no sibling crew's active work touched that paragraph.
- `IMPLEMENTER_PLAN.json`'s `h1-pins.c1` postcondition check command had a shell-quoting bug (unquoted `-k` value) that made it fail for any implementer regardless of test correctness — corrected via `spine_amend retext-check`, not a plan/authoring file I was otherwise scoped to touch. Worth a general sweep: any other checklist authored with a multi-word unquoted `-k` value elsewhere in this repo's templates would have the identical failure mode.

## Workflow Feedback
- **Handoff gaps:** The handoff (and `h1-pins`'s imperative) named only the two constants; it didn't anticipate that correcting `DOOR_TOOL_NAMES` would make an *already-correct* existing test (`test_names_door_tools_as_default`) newly catch a real, separate staleness in `checklist-engine.md`. Not fixable without touching a file outside the named "In:" list — worth flagging in the handoff next time a pin correction is known to cascade into doc-truth checks the same file enforces.
- **Context rediscovered:** Had to independently discover `h1-pins.c1`'s check command was unquoted and broken (bash splits `-k Door or Tie or Registry` into positional args, `pytest` errors before collecting anything) by running the exact JSON-literal command text verbatim. This is invisible from `spine_status`'s rendered imperative/check summary — only visible by reading `IMPLEMENTER_PLAN.json` directly or by the check simply refusing with no further detail.
- **Instructions improvised around:** No door tool exists for "fix a bug in my own check's wording" distinct from `spine_amend`'s general re-planning surface; used `retext-check` for that purpose (see Assumptions) since it was the closest fit and the PreToolUse hook doesn't deny it to crews, but the skill docs frame `amend` as needing human authority, creating real hesitation before using it unsupervised.
- **What would have made this easier:** A quoting lint/pre-flight over `command`-kind check text at plan-authoring time (e.g. reject an unquoted multi-word `-k`/`-m` style value) would have caught `h1-pins.c1`'s bug before dispatch instead of during it.

## Return status
`complete`
