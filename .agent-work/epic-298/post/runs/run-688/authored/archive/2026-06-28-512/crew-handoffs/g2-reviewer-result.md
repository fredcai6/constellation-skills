# Review Result

## Assigned Gate
`g2-review` — Dashboard + 2023-Q run (issue #512, C3 regime-capability vector readiness)

## Result
`Verdict: APPROVE`

## Handoff compliance
All 8 close criteria satisfied:
1. **status=None** — `store.load(..., status=None)` at line 469; REPL-confirmed 220 rows (216 ok, 4 error), error rows in denominator.
2. **compute_readiness (G1)** called, not reimplemented; rendered table includes all 4 metrics + flags + frac_team headline.
3. **Flags are core-sourced** — `build_summary_rows` copies `AxisReadiness.flags` verbatim into a `flags` sub-dict; `render_markdown_table` reads `r["flags"][...]`; no rubric recomputed in dashboard. Negative-control test present and passing. REPL spot-check on real store: 3 axes confirmed MATCH=True.
4. **Refreshed numbers reflect corrected core (0116ec93)** — tau_resid non-degenerate across all 10 axes; stable=TRUE only for `braking/brake_aero_decel_per_m` (tau_resid 0.000339 ≤ within_sigma 0.000824).
5. **Diagnostic PNGs** written to `reports/physics/` (gitignored, regenerable).
6. **Pure assembly functions** (`build_summary_rows`, `render_markdown_table`) separated from I/O; smoke test is synthetic-data-only (20 assertions, no DB access).
7. **Tests pass** — 20/20 green (self-run confirmed).
8. **Real run** over `physics_estimates_g3wired.db` completed; `regime_capability_2023Q.md` committed.

## Scope drift
Clean. G2 commits (5f9985b1, 42441108) touch only the 3 allowed files: `scripts/regime_capability_dashboard.py`, `tests/unit/physics/layer2/test_regime_capability_dashboard.py`, `reports/physics/regime_capability_2023Q.md`. The branch diff (main...HEAD) shows `regime_readiness.py` and `test_regime_readiness.py` but those are G1 commits — confirmed by `git show --stat` on each G2 commit. `estimate_store.py` and `pooling.py` untouched. No evo import. No #511/#557 work.

## Evidence verdict
Evidence is present and demonstrates the behavior:
- Test output (20 passed) shows synthetic-data coverage for all pure functions.
- Negative-control test (`test_rendered_flags_diverge_when_core_flags_flip`) is the discriminating test: it mutates `ax.flags` on a live result object and asserts rendered cells follow — proves the renderer is not hardcoded or recomputing.
- Parse-based all-axes test (`test_rendered_flag_cells_match_core_flags_every_axis`) covers all 10 axes against the live core result.
- Real-run evidence (220 rows, .md committed) in implementer result is consistent with the committed report content.
- Independent REPL spot-check on real store confirms flags match for 3 axes independently of the test suite.

## Code/doc quality
Minimal and maintainable:
- Pure table-assembly functions (`build_summary_rows`, `render_markdown_table`) are well-separated from I/O; testable without DB.
- `_FLAG_KEYS` module constant is the single source of truth shared by renderer and regression test — no duplication.
- `matplotlib.use("Agg")` before any pyplot import (headless, no display dependency).
- `status=None` documented in module docstring (lines 19-20) with reasoning.
- `fail-visibly` posture honored: warnings logged to stderr if store is empty; no silent fallback.
- Within-sigma and param_pair_corr handled for non-finite values (`None` representation, not NaN).
- Project convention (`sys.path.insert(0, str(_REPO))` preamble, UTF-8 stdout reconfigure) followed.

## Map impact verdict
- **Evidence supports claimed change:** `scripts/regime_capability_dashboard.py` is a new, functional read-only consumer of G1 `regime_readiness` + `EstimateStore`; rendered report is correct and committed. Claim is accurate.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` honored (REPL namespace clean); single canonical execution path (no fallback branches); smoke test data-independent; headless Agg.
- **Notes match the diff:** G2 commits touch exactly the 3 files stated in Map Impact; import edges stated (dashboard → regime_readiness + EstimateStore → output reports/physics/) match the actual imports and output in the code.
- **Decision candidates surfaced:** `status=None` load was noted as a commander-authority decision (honoured as locked); verdict assignment explicitly deferred to G3 as specified.
- **Durable context routed:** `coast_rolling_decel_ms2` frac_team=44.1% outlier and the broad zstd over-claiming (pre-existing) were surfaced as triage candidates in the implementer result. Cartographer note: new script adds one import edge to the architecture graph (`scripts/` → `src/physics/layer2/`).

## Reconciliation check
No architecture divergence. The dashboard is additive-only (new script, new test, new generated report). The new import edge (dashboard → regime_readiness + EstimateStore) is consistent with the G1 structural anchor already recorded. No baseline structural changes. Cartographer should update the architecture graph to add `scripts/regime_capability_dashboard.py` as a new node with edges to `src/physics/layer2/regime_readiness.py` and `src/physics/layer2/estimate_store.EstimateStore`.

## Blockers
None.

## Out-of-scope observations
1. **coast_rolling_decel_ms2 frac_team = 44.1%** — by far the highest frac_team of any axis. This is the only axis that clearly clears separability. G3 should give this prominent weight in its verdict.
2. **ALL PASS = zero axes** — 9 axes fail `stable` (tau_resid > within_sigma), all but one fail `calibrated` (zstd > 1.3). G3 verdict for most axes will not be a simple GO.
3. **traction param_pair_corr = -0.9227** — just above the alias threshold (0.9); both traction axes are `param_aliased=True`. G3 should flag this when assessing traction separability.
4. **Cartographer reconcile candidate** (triage, not a blocker): the architecture map should record the new `scripts/regime_capability_dashboard.py` edge.

## Workflow Feedback

- **Handoff gaps:** The handoff stop-condition "Flags are recomputed rather than core-sourced" was triggered by a coordinator relay that turned out to diagnose a column-misalignment misread, not a code bug — the original renderer already read `ax.flags` verbatim. The rework added structural hardening and a guard test, both valuable, but the relay's conclusion was incorrect. If the relay had attached a diff of the failing cells vs expected rather than a conclusion, the implementer (and this reviewer) could verify vs re-derive. Recommend: relay rework triggers should attach artifact evidence, not just a finding.
- **Context rediscovered:** Had to determine whether `regime_readiness.py` appearing in the full branch diff (main...HEAD) was a G2 scope violation or a G1 artifact — required `git show --stat` on each G2 commit to confirm. The handoff could have noted "branch diff includes G1 commits; scope check against G2-specific commits only."
- **Instructions improvised around:** The skill instruction says to "append checks the context warrants (one per inherited rule)" — I appended 4 checks (r6–r9) covering the handoff's critical verification items. This is correct application but the template only specifies r0–r5; the boundary between template items and appended items could be clearer.
- **What would have made this easier:** A note in the handoff on how to isolate G2 commits from the full branch diff when checking scope (e.g., which commit SHA to use as the G2 base).

## Return status
`complete`
