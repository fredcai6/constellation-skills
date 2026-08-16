# Triage Recommendation: `Two test files outside cleanup-g-crew-tier's ownership break under the new tierless-dispatch refusal`

## Classification
`bug`, `cleanup`

## Source checklist/artifact
- `execute.json` triage_candidates `tc1`, flagged from `g1-integrate`, independently confirmed by both the `g1-implement` implementer and the `g1-review` reviewer via full-suite runs.

## Structural anchor
`tests/test_crew_worktree_cwd.py`, `tests/test_work_id_nesting.py`

## Cartographer mismatch class
`none`

## Observations

### Observation 1
- **What's wrong:** `tests/test_crew_worktree_cwd.py::CrewSpawnCwdTests` calls `RC.launch_crew(...)` with `model=None` at 4 call sites (`test_cli_default_dot_dispatch_passes_an_absolute_repo_cwd`, `test_dispatch_passes_an_absolute_worktree_as_the_child_cwd`, `test_relative_worktree_resolves_against_root_not_the_dispatchers_cwd`, `test_the_registry_records_the_same_worktree_the_spawn_received`), so all 4 now raise `CrewLaunchError("a crew needs an explicit tier: refusing a dispatch with no --model given...")` instead of exercising the cwd-resolution behavior they were written to test.
- **Expected:** These tests should exercise worktree-cwd resolution, unaffected by tier selection — they need an explicit `model="sonnet"` (or equivalent) kwarg added, the same mechanical reconciliation already applied at ~27 call sites in `tests/test_crew_launcher.py` by this mission's own `g1-implement` gate.
- **Conditions:** Any full-suite run on `cleanup-g-crew-tier`'s branch (or after it merges to `main`) after `scripts/run_crew.py`'s `CrewSpec.__post_init__` refusal lands. Environment-independent — fires every time, not intermittent.
- **Type:** `measured` — `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q`, both by the Commander directly and independently reproduced by the `g1-review` reviewer; exact `CrewLaunchError` traceback confirmed in the reviewer's own run output.
- **Rev:** cleanup-g-crew-tier branch head, this run (base `e0539903`).

### Observation 2
- **What's wrong:** `tests/test_work_id_nesting.py::CrewRegistryAddressingTests`'s `_record_external` helper calls `RC.record_external_attempt(..., model=None, ...)`, breaking `test_flat_work_id_finalizes_identically` and `test_nested_work_id_finalizes_its_own_registry` the same way.
- **Expected:** Same fix shape as Observation 1 — an explicit `model=` kwarg at the helper's call site, unrelated to what the tests actually verify (work-id nesting/registry addressing).
- **Conditions:** Same as Observation 1.
- **Type:** `measured` — same full-suite runs as Observation 1.
- **Rev:** cleanup-g-crew-tier branch head, this run (base `e0539903`).

## Possible fix

Add an explicit `model="sonnet"` (or any valid tier string) kwarg at each of the 6 call sites named above — mechanically identical to the reconciliation already performed across `tests/test_crew_launcher.py` in this mission's `g1-implement` gate. No design question: the tests exercise unrelated behavior (worktree cwd resolution, registry work-id addressing) and simply need a tier named to keep constructing successfully.

## Recommended priority
`high`

**Reason:** Without this fix, `local Linux green` — this repo's stated merge-gate bar — is not met by a straight full-suite run on `cleanup-g-crew-tier`'s branch; every future branch based on it inherits the same 6 known-red tests. The fix itself is trivial (six one-line edits) and fully specified.

## Related artifacts
- `.agent-work/cleanup-g-crew-tier/crew-handoffs/g1-implement-implementer-result.md` (original enumeration)
- `.agent-work/cleanup-g-crew-tier/crew-handoffs/g1-review-reviewer-result.md` (independent re-derivation + confirmation)
- `.agent-work/cleanup-g-crew-tier/REPLAN_INPUT.json` discrepancy `D1`

## Disposition
`recommend-and-defer`

**Detail:** Clears all four Fix-Now Eligibility Ladder rungs (bounded diff — 6 one-line edits; adjacent to current scope — same repo, same mechanism, same run; verifiable now — the existing tests themselves prove it once fixed; no architecture/production-default impact — pure test-fixture change). **Not fixed now** despite clearing the ladder: `tests/test_crew_worktree_cwd.py` and `tests/test_work_id_nesting.py` are explicitly outside this mission's File Ownership (LAUNCH_ORDER: "Files you own: `scripts/run_crew.py`, `tests/test_crew_launcher.py`... plus any new test file" — these two are neither), and the launch order's own pre-ruling on `decision:refuse-a-tierless-dispatch` reserves this exact question to the Admiral by name: "if refusing breaks callers that legitimately have no tier to name (tests, tooling, a legacy path), REPORT them rather than adding a silent default — the list is the deliverable, and I will rule on it." Filing authority is therefore not unclear — it is explicitly retained by the Admiral for this specific finding, which is why this is `recommend-and-defer` rather than `filed`.

## Issue creation authority
`ask user` — the Admiral said "I will rule on it"; this recommendation is issue-ready for whatever disposition (fix directly, file, fold into a follow-up lane) the Admiral chooses.
