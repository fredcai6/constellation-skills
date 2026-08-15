# Implementation Result

## Assigned gate
`g1-implement — worktree identity is derived from git, compared by equality (2026-08-15 Admiral ruling)`

## Completed slice
`origin_worktree_refusal` now compares by equality instead of containment and fails closed on `cwd=None`; the single `main()` call site resolves the engine's cwd to its git worktree toplevel via the existing `_git` helper before the predicate sees it. The nested-worktree regression (`<primary>/.worktrees/<slug>` driving a primary-stamped spine) is captured red→green through `main()` with real git repos and kept as a permanent test. The authorized test migration landed: the synthetic subdirectory-passes case flipped to refusal at the predicate, and the subdirectory-is-allowed property moved up to a `main()`-level assertion against a real git repo.

## Scope
**Files changed:**
- `scripts/checklist_engine.py` — the predicate (~L102-180) and its one call site in `main()` (~L3427-3441) only
- `tests/test_spine_origin_isolation.py` — migration + new tests (7 new test methods, 1 corrected, fixtures git-inited)
- `tests/test_explorer_templates.py` — **out of Allowed Scope, flagged**: 1-line fixture repair (+comment), see Stop conditions / Workflow Feedback
- `map/INDEX.md` — regenerated via `python -m scripts.code_map build --root .` (3 insertions, 3 deletions; `map/ids.jsonl` did not move)

**Specific exclusions touched:** no — `spine_rail.py`, `mcp_spine_server.py`, `.mcp.json`, `.worktrees/epic-568-441/`, `test_it_is_pure` all untouched (purity proven byte-identical below).

## Behavior changed
Yes. (1) A primary-stamped spine driven from inside a nested worktree is now REFUSED (was ALLOWED — the regression). (2) A stamped spine driven from a cwd with no resolvable git toplevel is now refused by intent (fail closed), including `cwd=None` at the predicate level. (3) Origin-less/malformed-origin spines are unchanged: drivable from anywhere, never raise. (4) Subdirectory-of-own-worktree stays drivable — git toplevel resolution buys the property containment used to provide. (5) Every engine verb now costs one `git rev-parse --show-toplevel` subprocess at load — the once-per-verb cost the ruling explicitly accepts.

## Map Impact
- **Structural anchors touched:** `scripts/checklist_engine.py::origin_worktree_refusal` (comparison semantics + `cwd: str | None`); `scripts/checklist_engine.py::main` call site (git-toplevel resolution added); `tests/test_spine_origin_isolation.py` (all three sections).
- **Capabilities affected:** engine-native worktree isolation (#315/#568) — the guard's comparison is now git-identity equality; coverage extends to the nested-worktree layout #585 introduced.
- **Constraints/assumptions honored:** `test_it_is_pure` byte-identical and green; `OriginRefusalFallback` green and intent-unchanged; no `origin.worktree` migration (`decision:no-migration`).
- **Decision anchors executed:** `decision:git-not-lexical` (implemented at the call site), `decision:forgery-stays-open` (untouched — `_standing_in_the_bound_spines_worktree` still passes by chdir, by design), `decision:test-migration-authorized` (executed exactly as scoped, plus the ruling-listed Windows synthetic path `C:\W\REPO\scripts` → cwd is now the root itself so the test pins folding, not containment).
- **Claims/evidence produced:** nested-worktree refused after / allowed before (red/green pair below); fail-closed at predicate and `main()` levels; suite ≥ baseline.
- **Trust limitations / drift found:** none in the map (repo-wide `map/ids.jsonl` is empty — no decision anchors exist to update).
- **Triage candidates:** (a) the lexical-vs-git derivation split (`spine_rail.py::_worktree_from_spine` lexical, `mcp_spine_server.py::_worktree_root_for_lifecycle` git) is ruled deliberate but still written down nowhere durable — the ruling names it a documentation deliverable; it should land as a docstring/doc change once #441 is off `spine_rail.py`. (b) `test_mcp_identity.py::DC3InheritanceMechanismTests` asserts a clean caller environment and therefore fails inside any `run_crew.py`-dispatched crew (ambient `SPINE_FILE/SPINE_SESSION/SPINE_PARENT`); consider an explicit skip-or-scrub for crew-run suites so a crew's full-suite gate doesn't trip on its own dispatch envelope.

## Test mode
**Required:** test-first for the nested-worktree regression; test-after for the rest.
**Satisfied:** yes — red captured on the unmodified engine before any engine edit (engine diff was empty at capture; verified `git diff --stat scripts/checklist_engine.py` clean), green after the fix; the remaining changes were transcription with tests added after.

## Evidence

Red (unmodified engine, verbatim in `.agent-work/tc1-worktree-identity/evidence/g1-red.txt`):
```
tests/test_spine_origin_isolation.py::NestedWorktreeRegression::test_a_guarded_verb_from_inside_a_nested_worktree_is_refused FAILED
tests/test_spine_origin_isolation.py::NestedWorktreeRegression::test_a_subdirectory_of_the_nested_worktree_is_also_refused FAILED
E       AssertionError: 0 != 1        <- guarded verb ALLOWED, spine mutated (g1 -> in-progress)
============================== 2 failed in 0.06s ===============================
```

Green (fixed engine, verbatim in `.agent-work/tc1-worktree-identity/evidence/g1-green.txt`):
```
tests/test_spine_origin_isolation.py::NestedWorktreeRegression::test_a_guarded_verb_from_inside_a_nested_worktree_is_refused PASSED
tests/test_spine_origin_isolation.py::NestedWorktreeRegression::test_a_subdirectory_of_the_nested_worktree_is_also_refused PASSED
============================== 2 passed in 0.03s ===============================
```

Full origin-isolation file: `python -m pytest tests/test_spine_origin_isolation.py -v` → **37 passed, 1 skipped (Windows-only folding), 16 subtests passed**. Also re-run by the engine as m3's command check.

`test_it_is_pure` unmodified: `git diff -- tests/test_spine_origin_isolation.py | grep -A3 -B3 "def test_it_is_pure"` → zero lines (grep exit 1). Independently, m3's engine check compared the method's exact source segment between HEAD and working tree via `ast` → byte-identical.

Cache-clean full suite (`find . -name __pycache__ … -exec rm -rf {} + && python -m pytest tests/ -q`, summary in `evidence/g1-fullsuite.txt`):
```
3010 passed, 6 skipped, 1135 subtests passed in 126.43s
```
Baseline at `453f8492`: 3002 passed, 7 skipped, 0 failed, 1130 subtests. Passed +8 (7 new tests + 1), failed 0, subtests +5. The differing skip count was derived mechanically, not eyeballed: stashing the diff and re-running every skip-capable file yields the **identical 6-skip list** (2 Windows-only, 2 `REVISED_SPEC.md`-absent, 2 `CLI_ONLY_VERBS`-empty), so no skip converts under this diff — the 7th baseline skip is a property of the baseline measurement's workspace state, not of this change. The suite run was executed with `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT` (see Assumptions).

Wiring grep:
```
$ grep -n "_git(\[\"rev-parse\", \"--show-toplevel\"\]" scripts/checklist_engine.py
3439:    toplevel = _git(["rev-parse", "--show-toplevel"], base_dir=Path.cwd())
```
Exactly one match, inside `main()`, none in the predicate (the predicate's purity is separately pinned by `test_it_is_pure`, green).

Map: `python -m scripts.code_map build --root .` → `map/INDEX.md` moved (6 lines), `map/ids.jsonl` unchanged; INDEX will be committed with the change.

Engine-driven plan: every gate of `.agent-work/tc1-worktree-identity/crew-handoffs/g1-implement-implementer-plan.json` was driven via `scripts/checklist_engine.py` CLI under lease `constellation/tc1-worktree-identity/g1-implement/implementer/attempt-1`; m2/m3/m4 command checks were run by the engine at `advance`, not hand-asserted.

## TDD evidence, if required
- Failing test observed: yes — see red block above, captured before any engine edit.
- Passing test observed: yes — same scenario, same test, after the fix.
- Refactor while green: yes (call-site comment/expression tidied while the regression stayed green).

## Docs/contracts touched
- `origin_worktree_refusal` docstring rewritten for equality + fail-closed semantics (the "Containment, not equality" paragraph replaced; the deliberately-withdrawn unforgeability claim kept verbatim). Call-site comment extended with the resolution rationale. No external docs touched.

## Assumptions
- The full-suite baseline comparison is only meaningful in a non-crew environment: `test_mcp_identity.py::DC3InheritanceMechanismTests::test_launching_the_parent_never_touches_the_calling_processs_own_environ` asserts `SPINE_FILE/SPINE_SESSION/SPINE_PARENT` are absent from the calling process's environment, and a `run_crew.py`-dispatched crew carries all three by design. Verified both ways: fails in my crew env at HEAD-equivalent conditions, passes fully (`31 passed, 10 subtests`) with those three variables unset, with zero dependence on this diff (the test never touches origin logic). The suite gate was therefore run with the three variables scrubbed.
- Fixture tempdirs (`/tmp`) are outside any git repository — the same assumption the pre-existing fixtures already made implicitly.

## Stop conditions hit
- None fired: the git-toplevel measurement reproduces (a nested worktree resolves to itself — measured on the live tree and inside the regression fixture); green required no Specific-Exclusion edit and no test deletion; no decision outside the handoff's Authority was taken. One judgment call adjacent to a stop condition is recorded honestly: `tests/test_explorer_templates.py` (not in Allowed Scope, not in Specific Exclusions) began failing because its fixture instantiates an origin-stamped spine into a bare non-git tempdir and drives it from there — exactly the case the ruling's part 3 now refuses. I applied the minimal repair (git-init the fixture tempdir; test intent untouched — the same fixture-repair class as the `_SpineOnDisk` git-init this handoff itself ordered) rather than blocking the run, because the close criterion "full suite ≥ baseline" cannot be met any other way and the ruling itself dictates the semantics. If the Commander prefers a block-and-rescope, reverting is one hunk.

## Out-of-scope observations
- Per the ruling's "other half of tc3": the lexical (`spine_rail.py::_worktree_from_spine`) vs git (`mcp_spine_server.py::_worktree_root_for_lifecycle`) ownership-derivation split is deliberate — lexical stays because an archived checklist's worktree no longer exists for git to answer, and the hook runs per tool call where a subprocess is too costly. This is a documentation deliverable that could not land here (`spine_rail.py` is excluded and live under #441); it needs a home once #441 merges.
- The forgery hole is structurally load-bearing: `mcp_spine_server._standing_in_the_bound_spines_worktree` chdirs into the stamped worktree per engine call, so the door passes the new equality check the same way it passed containment. Confirmed no door test broke (`test_mcp_door_engine_cwd.py`, `test_mcp_lifecycle.py`, `test_mcp_adoption.py` all green in the full suite).
- Crew dispatch env observation for the Commander: my process was dispatched with the **commander's** `SPINE_FILE`/`SPINE_SESSION` pair ambient (no `--spine` binding for the crew), so the MCP door in my session was bound to the commander's spine — I drove my own plan via the CLI per workbench doctrine. Worth knowing that a crew calling door tools in this configuration would operate on the parent's spine.

## Workflow Feedback
- **Handoff gaps:** the full-suite close criterion collides with the Allowed Scope whitelist: the ruling's fail-closed rule breaks any test fixture that drives an origin-stamped spine from a non-git directory, and one such fixture lives outside the whitelist (`tests/test_explorer_templates.py`). The handoff enumerated this exact fixture class for `_SpineOnDisk` but the whitelist didn't cover the repo-wide blast radius of the semantics change. A one-line "plus any test fixture the fail-closed rule breaks, flagged in the result" clause would have removed the judgment call.
- **Context rediscovered:** that the baseline suite numbers are environment-sensitive (crew `SPINE_*` env fails `test_mcp_identity`; workspace state moves one skip). Stating the baseline's measurement environment (env + workspace) next to the numbers would make ≥-baseline mechanically checkable.
- **Instructions improvised around:** the implementer skill's "a dispatched crew's spine is bound for you; spine_status is your first call" did not fit — the bound pair was the commander's own (dispatch without `--spine`), so I fell back to the CLI-and-own-plan path the workbench reference prescribes. Reporting, not complaining: the skill text could name this configuration explicitly.
- **What would have made this easier:** the handoff was otherwise exceptional — the close criteria anticipated the two subtle fixture traps (`self.foreign` as a real repo, predicate-level `cwd=None` pin) exactly where I would have been most likely to silently narrow coverage.

## Return status
`complete`
