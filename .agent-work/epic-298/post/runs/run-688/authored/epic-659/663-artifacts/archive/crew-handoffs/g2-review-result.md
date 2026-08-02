# Review Result

## Assigned Gate
`g2-implement` (reviewing for g2-review) — module G grip-baseline FIT logic, issue #663.

## Result
`APPROVE`

## Handoff compliance
All task requirements met and **independently verified** (not trusted from the pasted evidence):

- **(a) Cumulative-track-laps helper** — `session_cumulative_track_laps_by_lap` replicates `session_race.compute_cumulative_track_laps` exactly. Source uses `COUNT(*) FROM lap_times WHERE session_id=? AND lap_number < X`; the helper is an exclusive prefix-sum over `GROUP BY lap_number` (filtering `lap_number IS NOT NULL`, which a `< X` predicate already excludes) — equivalent. The regression test genuinely calls the real source on 3 real 2023 R sessions and asserts exact equality (not a synthetic tautology). Re-ran the full file: **12 passed in 0.42s**.
- **(b) Generalized clean-lap reader** — `_read_clean_session_laps` is a byte-for-byte mirror of `tyre_supplant._read_clean_race_laps` (identical column set + clean-lap filter `valid_lap=1 AND pit_in/out IS NULL AND track_status='1'`, dry compounds, non-null guards), differing only by parameterizing `session_type` (source hardcodes `'R'`) and pinning `gp_name`. `race_degradation_slopes` is **imported and called unchanged** (`from src.physics.layer2.tyre_supplant import ... race_degradation_slopes`; call site in `_wear_corrected_pace`) — the OLS body is never reimplemented.
- **(c) predictive_t** — genuinely used for every stored sigma via `_pt_scale → predictive_t(...).scale`. Confirmed at source it is a real Student-t: `PredictiveT` wraps `scipy.stats.t(df=nu, loc, scale)` and samples via `rng.standard_t`; `FormulaRule` gives `nu = min(nu_loss, nu_prior + k·n_eff)` with `sqrt(1 + 1/n_eff)` epistemic inflation. **Not a Gaussian dressed up** — no `scipy.stats.norm` anywhere.
- **(d) Thin-session fallback** — `fit_grip_baseline_from_laps` never returns `None`: below `MIN_STINTS_FOR_FIT=2` it returns a `thin_fallback` record with `session_offset_sigma` inflated by the named `THIN_SESSION_SIGMA_INFLATION=3.0`, via neighbour extrapolation or (degenerate all-thin weekend) an own-mean field prior. A record always exists.
- **(e) Rain-flag fallback** — independently reproduced: dry `session_offset_sigma=0.029608`, rain `=0.118433`, **ratio exactly 4.000000**, with `session_offset`/`curve_asymptote` unchanged. `RAIN_SIGMA_INFLATION=4.0` is a genuinely distinct named constant from `THIN_SESSION_SIGMA_INFLATION=3.0`.

Stop conditions: none fired.

## Scope drift
Clean. `git status --porcelain` shows only untracked (`??`) files: `grip_baseline.py` + `test_grip_baseline.py` (the two allowed new files), plus g1's `grip_store.py`/test and `.agent-work/`.

- **CRITICAL scope check — `tyre_supplant.py` has no status marker at all** (not even `M`): untouched, confirming the implementer's local-reader choice. This is the single most important scope-integrity check for the gate and it passes.
- `grip_store.py` NOT modified (`grip_baseline.py` only imports `GripEstimateRecord` + `error_record` from it).
- No `run_grip_batch` / `GripStore` write-orchestration (g3's job) leaked in — `grip_baseline.py` is pure fit logic + a read-only DB wrapper.

## Evidence verdict
Required evidence present and reproduced. Test mode was test-after (as required); 12/12 green re-run locally. Load-bearing proofs (cumulative real-data regression, rain sigma ratio) reproduced independently. `simplification_limits` re-run: **PASS (2 files)**.

## Code/doc quality
Minimal, well-decomposed, project-rule compliant. DB-only honored (all reads `file:...?mode=ro`, no FastF1/Jolpica imports). Fail-visibly honored (`error_record` on exception in the DB wrapper — a failure is recorded, never lost; no silent record drop). Docstrings carry substantive statistical rationale (constant choices, frozen decisions, the surfaced fuel limitation). Fowler refactoring pass (all 12 baseline smells, rail `verify_fowler_pass.py` exit 0): 2 non-blocking observations flagged (data-clumps + long-parameter-list — the recurring session-identity tuple / `_thin_fallback_record`'s ~11 kw-only args; both subordinate to g1's frozen record), 2 logged overrides (duplicated-code — local SQL mirror forced by the no-touch-tyre_supplant constraint, regression logic itself reused unchanged; primitive-obsession — bare-string `session_type`/`compound` is the layer2-wide convention), 8 absent.

## Map impact verdict
- **Evidence supports claimed change:** Yes — `claim:cumulative-track-laps-reuse` backed by the real-data regression; `claim:tyre-supplant-correction-reused` backed by the import+call site (no reimplementation).
- **Constraints not violated:** Yes — `assumption:student-t-residuals` honored (predictive_t verified); frozen `decision:thin-session-explicit` and `decision:session-scope-uniform` implemented, not redesigned.
- **Notes match the diff:** Yes — `struct:physics.layer2` gains `grip_baseline.py` as claimed; no overstated/missing structural or capability impact.
- **Decision candidates surfaced:** N/A — no decision requiring authority the implementer lacked; frozen decisions were implemented, not authored.
- **Durable context routed:** Yes — the two out-of-scope items routed to Triage (below), not dropped.

## Reconciliation check
No architecture divergence requiring Commander reconciliation beyond the two triage candidates. The new module sits cleanly as a sibling to `grip_store.py` (g1) and `tyre_supplant.py`.

## Blockers
- None.

## Out-of-scope observations
Both implementer-flagged findings **confirmed genuine, honestly-scoped, and triage-worthy** (not silently-swallowed defects):

1. **Fuel confound in the grip curve.** `race_degradation_slopes` fits a global fuel term internally but returns only `compound`/`deg_slope_raw`/`n_laps` (confirmed at source) — no fuel coefficient to subtract. So the wear-corrected pace still carries fuel burn-off, absorbed by curve+offset and surfaced by `curve_offset_correlation`. De-fuelling would require reimplementing the forbidden OLS body. A real, honestly-scoped limitation, not a bug. **Triage candidate**: expose the fuel coefficient as an additive return field to tighten separability.
2. **`sessions.rainfall` schema/storage mismatch.** Schema declares `REAL`, but the collector writes an 8-byte little-endian int64 blob (wet-sample count). Spot-checked on real 2023 data: Bahrain=0 and Australia=0 (dry → flag False), Netherlands=48 and Monaco=26 (known-wet → flag True); stored dtype is `bytes`. The decode is genuinely correct on real known-wet sessions. **Triage candidate**: consider `session_surface_features.session_rain_flag` (INTEGER, already populated) as the canonical repo-wide rain source, or fix the schema type.

(A third, minor implementer note — the any-wet-sample rain threshold — is a reasonable conservative default; fold into triage candidate 2 if pursued.)

## Workflow Feedback
- **Handoff gaps:** The handoff was unusually complete and testable. One field could be sharper: the rain-flag close criterion said to confirm the 4.0x ratio "on real data" but the frozen numeric proof (`test_rain_flag_widens_...`) runs on the synthetic fixture (correctly — it needs a controlled dry-vs-rain A/B on identical laps). I reproduced the ratio on that fixture and separately spot-checked the rain *decode* on real 2023 sessions; naming those as two distinct sub-checks in the handoff would remove the momentary ambiguity about which artifact proves which claim.
- **Context rediscovered:** Had to open `student_t.py` to confirm `predictive_t` is a genuine Student-t (the handoff asked for this but didn't point at the seam file); a one-line pointer to `src/common/student_t.py` would have saved the grep.
- **Instructions improvised around:** None material. The reviewer skill/engine/templates covered the flow cleanly; the Fowler rail worked first try.
- **What would have made this easier:** Splitting the rain close-criterion into "ratio reproduces on the controlled fixture" + "decode is correct on a real known-wet session" (both of which I did) would make the two verifications explicit in the handoff.

## Return status
`complete`
