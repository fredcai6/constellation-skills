# Review Result

## Assigned Gate
`g3-implement` (reviewing)

## Result
`APPROVE`

## Handoff compliance
Satisfied. `CrewSpec.__post_init__` calls `resolve_model(role=self.role, harness=self.launcher, requested=self.model, reason=self.reason)` exactly once — confirmed by independent wiring grep (1 real call site at line 1483; three other grep hits are prose/docstring). The old flat `if not self.model: raise` block is gone, replaced not duplicated (zero hits for "explicit tier"/"no default is invented"/`decision:refuse-a-tierless-dispatch` in the current source). All 4 `CrewSpec(` construction sites (`launch_crew` L2002, `record_external_attempt` L2068, `main()` abandon-relaunch L2363, `main()` fresh-launch L2387) resolve through `__post_init__` by Python's own construction semantics. Both `main()` sites now symmetrically pass `reason=args.reason`. An old-shape `crew-runs.json` entry (a `model` key, no `reason` key) round-trips cleanly through `resume_crew`/`CliBackend.resume` — independently re-ran `test_old_shape_registry_entry_with_model_and_no_reason_key_resumes_cleanly`, PASSED.

## Scope drift
None. `resume_crew()`/`CliBackend.resume()`/`ExternalBackend.resume()` show zero diff — confirmed by comparing all 12 hunk headers' new-file line ranges against the current source's function ranges (`CliBackend.resume` 1687–1763, `ExternalBackend.resume` 1835–1945, `resume_crew` 2010–2035); every hunk falls outside them. g3's diff is confined to `CrewSpec` (field + `__post_init__`), `build_parser` (`--reason`), `build_entry` (`reason` param/write, both call sites inside `CliBackend.dispatch`/`ExternalBackend.dispatch` — necessarily in scope to thread `spec.reason` per the implement handoff even though the reviewer handoff's Allowed Scope line names only `build_entry` itself), and `main()`'s two `CrewSpec(...)` sites. `resolve_model`/`ROLE_MODEL_TIERS` (g2's) shows a single addition-only hunk, not re-touched. Fenced paths untouched. `install_constellation.py`/`test_install_constellation.py` carry unrelated pre-existing g1-lane changes in the same shared uncommitted tree. Test-file changes confined to the named `MandatoryModelTests` rewrites/additions plus one `ExternalDispatchTests` test and one `BackendEquivalenceTests` test, matching both handoffs exactly.

## Evidence verdict
Satisfies required evidence. Independently reproduced: wiring grep (1 real call site), all 4 `CrewSpec(` sites, full suite (`py -m pytest tests/test_crew_launcher.py -q` → 236 passed, 1 failed — the identical pre-existing `ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound` `CREW_SCRATCH_DIR`-leak failure named in the handoff; this reviewer's own re-run traceback confirms the leak comes from this crew's own ambient env var, same defect class). All 36 tests in `MandatoryModelTests`/`ExternalDispatchTests`/`BackendEquivalenceTests` individually PASSED. Test-after mode (sanctioned for the wiring) verified by a mutation test per `CREW_CONTEXT.md`'s verification-discipline rule: mutated `implementer`'s declared default tier from `sonnet` to `haiku`, reran `MandatoryModelTests` → 2 tests went red, confirming real behavior is asserted; restored and reconfirmed 13/13 green.

## Code/doc quality
The three tests the rework handoff authorized rewriting preserve their original testing intent — verified by reading each full body, not just its name:
- `test_crew_spec_with_falsy_model_resolves_the_role_default` asserts `role="reviewer"` → `model="sonnet"`, `reason=None`, exactly as specified.
- `test_cli_parser_persists_model_and_reasoning_effort_to_external_registry` still asserts an explicit `--model`/`--reasoning-effort` pair persists, now using in-table `"haiku"` for `"implementer"` with `--reason`, and additionally asserts the persisted `reason` field.
- `test_external_dispatch_records_without_spawning_returns_none`'s no-spawn/`None`-return assertions (`assertIsNone(code)`, `assertEqual([], calls)`) are byte-for-byte unchanged; only the model value moved from `"opus"` to `"sonnet"` (implementer's default, needs no reason).

The new `test_abandon_relaunch_with_reason_succeeds_and_entry_carries_reason` confirms Ruling 2's symmetry fix. No stray debug code, no unused imports; docstring/comment style matches surrounding house style (dense rationale, decision-anchor citations).

**Fowler pass:** all 12 baseline smells rendered a verdict, recorded to `.agent-work/567-j/g3-review/FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0 (`smells=12, flagged=[long-parameter-list], overridden=[shotgun-surgery]`). 10 absent. `long-parameter-list` flagged non-blocking (`build_entry` now 19 keyword-only params) and raised as a triage candidate. `shotgun-surgery` overridden — the 6-site `--reason` threading matches the exact touch-point set every existing optional dispatch parameter (`model`/`reasoning_effort`/`spine`/`parent`) already uses, per `global-crew.md`'s match-surrounding-conventions standard.

## Map impact verdict
No architecture map exists in this repo (DEGRADED-UNPARSEABLE, waived by the Admiral, `decision:map-index-is-admiral-owned`) — the handoff correctly names this instead of pointing at a map, so this section is largely inapplicable structurally. `decision:refuse-a-tierless-dispatch` (#611) is superseded in scope exactly as declared: an absent `--model` no longer hard-refuses when the role/harness pair has a table entry (confirmed by 3 tests); it still refuses when no table entry exists (`test_unpopulated_harness_is_refused_by_name_even_with_model_given`). No decision candidates required beyond what was already settled by the rework handoff's two rulings.

## Reconciliation check
None. Nothing here requires Commander reconciliation beyond what the handoff already scoped to g3.

## Blockers
- none

## Out-of-scope observations
- `build_entry()` has grown to 19 keyword-only parameters (18 pre-g3, +1 for `reason`). Not a defect in this diff — flagged as a triage candidate (`tc1` in the survey) for a future gate to consider a parameter object rather than a 20th kwarg.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: the handoff's close-criteria list and the two prior handoffs (original + rework) fully specified every check, including the exact assertion each rewritten test needed to preserve.
- **Context rediscovered:** the reviewer skill's own `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` env pointed at the parent Commander's spine (lease held by `commander`, gate `execute`), not this reviewer crew's own work — confirmed via `spine_status` and my own `crew-runs.json` entry (`"spine": null`). Per prior recorded guidance on this exact pattern, authored my own `REVIEW_SURVEY` at `.agent-work/567-j/g3-review/review.json` and drove it through the CLI (`scripts/checklist_engine.py`) rather than the MCP door, to avoid mutating the parent's spine. This is a known, recurring misfit worth fixing durably in the crew-dispatch skills (branch on whether the bound spine's `work_id`/session actually matches this crew's own).
- **Instructions improvised around:** the `r6-fowler` survey item's postcondition command needed the repo's absolute path substituted in (same detour g2-review already needed) — filled it correctly at survey-authoring time this run rather than via a post-hoc `amend`, since I was writing the file from the template myself.
- **What would have made this easier:** none beyond the spine-binding note above — the two implement handoffs were unusually thorough and left no ambiguity to resolve.

## Return status
`complete`
