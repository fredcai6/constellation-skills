# Implementation Result

## Assigned gate
`w1-completion-contract` / `w2-hook-portable` / `w3-verify` (rework spine `REWORK_PLAN.json`, implementer) — work id `epic-559/a-spine-is-the-job`

## Completed slice
Both blockers named in `REWORK_HANDOFF.md`, all three gates driven to `complete`:

1. **A spine-only crew's completion contract is its spine, not a result file.** `--result` is now optional wherever `--spine` is given (`CrewSpec`, `build_entry`, `finalize_from_exit_code`). When `--result` is omitted, completion is judged by a new `spine_terminal(spine, root)` — the bound spine's `checklist_engine.active_id(...) is None` — instead of a result artifact. Providing both `--result` and `--spine` keeps the prior result-based judgment byte-for-byte unchanged (existing tests that pass both are untouched). `CrewSpec.__post_init__` now also refuses a spec with neither `result` nor `spine`, the same shape as its existing handoff-or-spine refusal.
2. **The waive-deny hook cannot fail open off this machine.** `crew_settings_json` emits `shlex.quote(sys.executable)` instead of the literal `python3`, adds `"shell": "bash"` to the hook entry (matching all four entries in this repo's own `.claude/settings.json`), and calls `install_constellation.assert_shell_safe_command()` on the composed command — the same #539 guard `build_hook_command` applies to its own hooks, cited by comment at the site. The bare `assert "'" not in WAIVE_DENY_REASON` (stripped under `python -O`) now raises `CrewLaunchError` instead.

Also: fixed `REWORK_PLAN.json` itself, which used a `"gates"` key the engine does not read (`checklist_engine.py` hard-requires `"items"` — see Workflow Feedback) and was missing the `gated`-type's `consolidation`/`triage_candidates`/`blockers` fields; without this the engine could not even run `current` against the spine (`KeyError: 'items'`). Regenerated `map/INDEX.md` (entity count drifted: `scripts` 1085→1086, `tests` 3923→3936).

## Scope
**Files changed:**
- `scripts/run_crew.py`
- `tests/test_crew_launcher.py`
- `map/INDEX.md` (mechanical regeneration)
- `.agent-work/epic-559/a-spine-is-the-job/REWORK_PLAN.json` (schema fix so the engine could drive it at all — not a hard-no-go file, not one of the four listed in-scope files, but required to execute this dispatch)

**Specific exclusions touched:** no. `checklist_engine.py`, `mcp_spine_server.py`, `settings.json`, `docs/agents/*`, and `skills/*/templates/` were not modified. `run_crew.py` now imports `checklist_engine` and `install_constellation` (read-only, same same-directory `sys.path.insert` pattern `mcp_spine_server.py`/`verify_installed_bundles.py` already use) — no line inside either file was edited.

## Behavior changed
Yes. `run_crew.py --spine <s>` (no `--result`) now reports `completed`/exit 0 when the bound spine reached a terminal state, where it previously always reported `failed`/exit 1 regardless of spine state. The waive-deny hook's emitted command now names the launching interpreter instead of a hardcoded `python3` and declares `shell: bash`.

## Map Impact
- **Structural anchors touched:** `scripts.run_crew:CrewSpec` (result nullable, new refusal), `scripts.run_crew:build_entry` (result nullable), `scripts.run_crew:finalize_from_exit_code` (new `spine` param, branches on `result is None`), `scripts.run_crew:spine_terminal` (new), `scripts.run_crew:crew_settings_json` (interpreter/shell/guard).
- **Capabilities added/changed/affected:** a crew dispatch can now be spine-only end-to-end — no handoff document (already true, #559 job 1) AND no result artifact (this job) — judged entirely through the spine. The waive-deny hook is portable to any host's Python interpreter name.
- **Constraints/assumptions touched:** `assert_shell_safe_command`'s documented invariant ("a hook command must begin with a bare command word") is now also load-bearing for `run_crew.py`'s own emitted hook, not just the installer's.
- **Decision candidates / resolved decisions:** confirmed the ruling named in the handoff — judge spine-only completion on the spine reaching a terminal state, not by threading a result path into the prompt.
- **Triage candidates:** see Out-of-scope observations below (`recover_crews.py` classification gap).

## Test mode
**Required:** test-first / evidence-only
**Satisfied:** yes — verified genuinely red by checking out the pre-fix `scripts/run_crew.py` (commit `6fc83013`, before either of this run's commits) with the new test file in place: 7 of 8 new tests failed (`AssertionError`/`IndexError`, plus the CLI's own `REFUSED: launch requires ... --result` on stderr for the spine-only cases); the 8th (refusing neither `--result` nor `--spine`) already held under the old code, as expected. Restored and reran green.

## Evidence

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
**Result:** pass — `2556 passed, 1 skipped, 1101 subtests passed`

```bash
test $(python -m pytest -q tests/test_crew_launcher.py -k SpineOnlyCompletion --collect-only 2>/dev/null | grep -c '::') -ge 3 && \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m pytest -q tests/test_crew_launcher.py -k SpineOnlyCompletion
```
**Result:** pass — 5 tests collected, 5 passed (w1 gate `c1`).

```bash
python -c "import re,sys;s=open('tests/test_crew_launcher.py').read();m=re.search(r'def test_spine_only_success_is_not_recorded_failed.*?(?=\n    def |\nclass )',s,re.S);sys.exit(0 if m and 'write_result_at' not in m.group(0) else 1)"
```
**Result:** pass, exit 0 (w1 gate `c2`).

```bash
python -c "import sys,json,shlex;sys.path.insert(0,'scripts');import run_crew;h=json.loads(run_crew.crew_settings_json())['hooks']['PreToolUse'][0]['hooks'][0];sys.exit(0 if shlex.split(h['command'])[0] not in ('python3','python','py') and h.get('shell')=='bash' else 1)"
grep -q assert_shell_safe_command scripts/run_crew.py
grep -q 539 scripts/run_crew.py
test $(python -m pytest -q tests/test_crew_launcher.py -k HookPortab --collect-only 2>/dev/null | grep -c '::') -ge 2 && \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m pytest -q tests/test_crew_launcher.py -k HookPortab
```
**Result:** pass on all four (w2 gate `c1`-`c4`) — interpreter is `sys.executable` (an absolute path, not `python3`/`python`/`py`), `shell: bash` present, both greps hit, 3 `HookPortab` tests collected and passed.

## TDD evidence, if required
- Failing test observed: 7/8 new tests (`SpineOnlyCompletionContractTests` × 4, `HookPortabilityTests` × 3) fail against the pre-fix `scripts/run_crew.py` (commit `6fc83013`) — see Test mode above.
- Passing test observed: full suite green at `2556 passed, 1 skipped, 1101 subtests passed` with the real change restored.
- Refactor while green: no refactor pass beyond the implementation; `map/INDEX.md` regeneration was mechanical.

## Docs/contracts touched
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`), enforced by `tests/test_code_map.py::MapTreeFreshnessTests`.

## Assumptions
- `assert_shell_safe_command`'s leading-character check (not a mid-string apostrophe check) is the right tool for the new risk `sys.executable`-quoting introduces (a path containing spaces would make `shlex.quote` wrap it in single quotes, producing a leading-quote command — exactly the #539 hazard that function exists to catch). The separate, narrower "no apostrophe in `WAIVE_DENY_REASON`" invariant is a distinct property (guards a literal embedded inside the command, not the command's own leading token) and was kept as its own raising check rather than folded into `assert_shell_safe_command`, since that function does not — and by its own docstring, is not meant to — inspect mid-string content.
- `REWORK_PLAN.json`'s `"gates"` → `"items"` rename and the added `consolidation`/`triage_candidates`/`blockers` fields were a mechanical schema-conformance fix (verified no script anywhere reads a `"gates"` key), not a scope or intent change — treated as in-scope because the engine could not execute this dispatch at all without it.

## Stop conditions hit
- None.

## Out-of-scope observations
- `scripts/recover_crews.py::classify_entry` (not touched — out of the four named in-scope files) still classifies a `status: "completed"` entry as `STATE_NEEDS_ABANDON` whenever `has_result` is false, because it re-derives resolution from `entry.get("result")` rather than trusting the stored `status`. A genuinely successful spine-only crew (no `--result`, `status: "completed"`, `result_present: false` by design) would therefore be misclassified by `recover_crews.py` as needing abandonment, even though `run_crew.py` now correctly records it `completed`. `_default_result_present` already guards `if not result: return False` so it does not crash — but `classify_entry`'s `"completed" -> has_result ? COMPLETE : NEEDS_ABANDON` branch has no spine-aware fallback. Flagging as a triage candidate rather than fixing: `recover_crews.py` is not in this handoff's scope, and the fix would need the same `spine_terminal` read this task added to `run_crew.py`.
- `tests/test_mcp_adoption.py`'s `DOOR_TOOL_NAMES` (7)/`CLI_ONLY_VERBS` (5) pin a stale fact (N1 already made all 18 verbs door-reachable) — confirmed still present, left untouched per the handoff's explicit instruction to leave it alone again.

## Workflow Feedback

- **Handoff gaps:** `REWORK_PLAN.json` used a `"gates"` key; `checklist_engine.py` reads `"items"` everywhere (`cl["items"]`, hard-subscripted, no `.get` fallback) and has no schema-validation layer to surface the mismatch as anything friendlier than a raw `KeyError: 'items'` on the very first `current` call. The handoff said "drive the spine gate by gate" but the spine as handed to me could not be driven at all until I renamed that key and added the missing `gated`-type fields (`consolidation`, `triage_candidates`, `blockers`) the template carries. Worth naming explicitly next time a rework spine is authored by hand rather than instantiated from `templates/IMPLEMENTER_PLAN.template.json`: whatever builds a `REWORK_PLAN.json` should either use the template's exact top-level keys or run it through the engine's `current` verb once before handing it off, so a schema typo is caught before dispatch instead of by the crew.
- **Context rediscovered:** the checklist engine's exact top-level schema (`items` not `gates`, and which fields are hard-subscripted vs. `.get`-defaulted) — had to read `checklist_engine.py` directly (`_rail_position`, `active_id`, `claim`/`release`) since `docs/CHECKLIST_SCHEMA.md` states the shape but the handed spine didn't match it and there was no faster way to find *why* than reading the engine's own subscripts.
- **Instructions improvised around:** the handoff named `assert_shell_safe_command()` as the replacement for the bare assert guarding `WAIVE_DENY_REASON`, but that function only checks a command's *leading* character, not embedded apostrophes — the actual property the old assert checked. Rather than mechanically swap one call for the other (which would have silently dropped real protection), I kept a raising check for the apostrophe property and additionally called `assert_shell_safe_command` on the composed hook command, where it's the correct tool for the new leading-quote risk `sys.executable`-quoting introduces. Named explicitly in case the ruling intended something narrower.
- **What would have made this easier:** a spine instantiated (even mechanically) from the `gated` template, or a one-line note in the handoff that the spine's schema had not been round-tripped through `checklist_engine.py current` before dispatch, would have saved the first ~15 minutes of this run.

## Return status
`complete`
