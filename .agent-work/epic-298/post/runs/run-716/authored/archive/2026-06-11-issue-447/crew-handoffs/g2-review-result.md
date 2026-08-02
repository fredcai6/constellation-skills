# Review Result

## Assigned Gate
`g2 (g2-review)` — issue #447 Phase 0b: time-tag jitter + inter-stream offset stability (GO/NO-GO core)

## Result
`APPROVE`

## Handoff compliance
Change does exactly what the handoff asked, within allowed scope. Read-only characterization over the SAME 6 G1 sessions; measures (1) per-stream time-tag jitter vs BOTH a cadence fit AND DB sector-crossing truth; (2) error-model class with discriminating statistics; (3) inter-stream offset stability resolving 0a finding F2; (4) the reduced chi-square the 0a covariance gate would see. 0a primitives are imported, never forked. No estimator/filter/smoother deliverable. No GO/NO-GO decision. All 6 sessions ran; all 6 had DB sector truth. Stop conditions: none hit; none should have been.

## Scope drift
Clean. Only `scripts/characterize_timetag_jitter.py` + `.agent-work/issue-447/evidence/jitter_offset_*.json` touched; no `src/` change. Static checks (grep over the script): NO `get_telemetry` (only docstring references), no `requests`/`urllib`/`http`/direct `fastf1.` call (fastf1 reached solely via `offline_loader`), no `evo_predictor` import, no `INSERT`/`UPDATE`/`DELETE`/`.commit(`/`to_sql` (DB read-only via `db_truth_loader`, `file:?mode=ro`). The SG fit is used only as a measurement device, not a product. No specific exclusion touched.

## Evidence verdict
Required evidence present and traceable. 7 JSONs; every headline number in the implement-result matches the JSON (car/pos cadence-jitter IQR 0.128–0.141 s; sector-crossing |median| 0.102–0.158 s; chi-square 78.7–3292; all 6 stable-estimable + white-jitter). Test mode `evidence-only` is appropriate (new evidence script; no project test surface). Reused 0a primitives verified intact (implementer reports 47 trajectory_grading + 129 physics green; primitives unmodified in the diff).

### Independent re-computations (the load-bearing verdicts)

**Verdict 1 — error model = WHITE-JITTER. CONFIRMED.**
I loaded raw `car_data`/`pos_data` for 2023 Belgian Q via `offline_loader`, took `SessionTime` diffs, formed the dt-deviation series `dt - median(dt)`, and computed its lag-1 autocorrelation independently:
- car_data dt-deviation lag-1 autocorr = **-0.00004**; pos_data = **-0.0386** — reproduces the implementer's numbers exactly. White (≈0), NOT a strongly-positive random-walk signature.
- The "SG-residual autocorr ~0.6 is a smoothing ARTIFACT" reasoning is SOUND, and I proved it independently: I shuffled the real dt sequence (destroying all time-ordering → provably white by construction), rebuilt the timestamp series, and SG-smoothed it. The SG-residual lag-1 autocorr stayed at **+0.625** — essentially identical to the real **+0.630** — while the dt-deviation autocorr correctly dropped to ~0. This conclusively shows the SG-residual positivity carries NO temporal-correlation information (SG smoothing correlates neighbouring residuals by construction); the dt-deviation series is the honest discriminator, and it reads white.
- Supporting discriminators trace: per-Source eta²=0 (single Source tag per car stream → not per-batch); |mean|/std ~1e-4 (→ not a constant bias). The classifier's gating logic (random-walk requires BOTH large drift ratio AND positive dt-autocorr ≥ 0.10; the observed ~0 autocorr correctly defeats it despite a large cumulative-drift ratio from sparse gaps) is correct.

**Verdict 2 — offset STABLE-ESTIMABLE all 6 sessions. CONFIRMED.**
Numbers trace to the summary: |session mean offset| ≤ 0.081 s; median per-lap std 0.084–0.129 s; per-lap range 0.32–0.50 s; median |lag-1 autocorr| < 0.5; small drift. The `stable-estimable` verdict follows from the documented thresholds (std ≤ 0.15 s AND |autocorr| < 0.5). Spot-check of 2023 Belgian Q per-lap offsets: VER spans [-0.146, +0.170] s (std 0.091, ac -0.087, total drift -0.043), SAR spans [-0.316, +0.262] s — consistent with 0a's reported per-lap ranges (~[-0.20,+0.41]/[-0.23,+0.03]/[-0.08,+0.36] s). Tight, low-drift → an estimable stable bias, not per-lap wander.

**Verdict 3 — chi-square OFFSET-DOMINATED. CONFIRMED.**
On 2023 Belgian Q / VER (sigma²=0.74 m²): the residual is genuinely the offset-inclusive `speed_arc − position_arc`. Mean |raw residual| = **5.46 m** — several metres, far beyond what ~0.1 m² positional noise explains, so the chi-square inflation is driven by the unremoved inter-stream offset's arc term, not positional noise. Removing the per-lap offset (+ per-lap level) drops chi-square from **95.9 → 63.9** toward the 0a band; the offset is the dominant term as claimed. The "G3 should set the F1 band against an offset-removed residual" routing is the right call.

## Code/doc quality
Physics evidence bar met: units/bounds/invariants explicit (time s, arc m, offset s, chi dimensionless; pos decimetres ×0.1 → m via `XY_TO_METRES`; speed km/h ÷3.6 → m/s). Decimetre handling in `_arc_from_xy_dm` is correct (diff in dm, ×0.1 to metres). Speed-arc integrated on the car grid then interpolated onto the pos grid — preserves the genuine inter-stream timing structure so the offset fit is meaningful. Small composable functions; reuses 0a primitives rather than duplicating. Logging via `logger` + `print` is fine for a `scripts/` file. The 1240-line length is an ADVISORY hit only: `--baseline` (DEFAULT_ROOTS = src, tests) does NOT scan `scripts/`, and `--paths` on the script shows the SOLE violation is `file_lines=1240` with all function-level complexity/length limits passing. Not a `src/` check-in gate violation — the implementer's judgement is correct.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the 7 JSONs back every headline; the three load-bearing verdicts hold under independent re-computation.
- **Constraints not violated:** Yes — `constraint:physics_region_no_evo_import` honored; raw streams only via `offline_loader`; offline cache; pos decimetres; DB read-only; characterization-only.
- **Notes match the diff:** Yes — new `scripts/` consumer of `struct:preprocessing` `trajectory_grading/{cross_residual,sector_anchor,covariance_gate,offline_loader,db_truth_loader,contract}`; no primitive modified.
- **Decision candidates surfaced:** Yes — F2 resolved from evidence (stable estimable bias); the chi-square band/residual-definition question explicitly routed to G3 (flagged, not decided), respecting authority.
- **Durable context routed:** Yes — G3 F1-band input flagged; no committed schema/contract touched (evidence JSON is local agent-work). No new triage candidate.

## Reconciliation check
No docs/contracts/structural-baseline concern. No public interface or committed report-schema change. The 2 pre-existing `--baseline` failures (`_param_dataclasses.py`, `html_reports/__init__.py`) are unrelated src/ files, not introduced here.

## Blockers
- none

## Out-of-scope observations
- For G3 (already surfaced by the implementer, concur): the covariance-gate chi-square (78.7–3292) is dominated by the unremoved inter-stream offset term, not positional noise. G3 should set the F1 band against an offset-removed residual (the `cross_residual` arc-residual, which sits at a few metres) OR widen the per-sample variance to include the offset's arc contribution. Design call for G3, not a defect here.

## Workflow Feedback
- **Handoff gaps:** The review handoff was strong and named the exact load-bearing verdicts and re-computations. One small gap: it did not state where the engine lives (the bundled `checklist_engine.py` is under the installed reviewer skill, and `references/checklist-engine.md` does not exist at the workbench path the skill text implies) — I located it by listing the skill's `scripts/`.
- **Context rediscovered:** The engine's `advance` and `start` subcommands both require an `id` positional; for a flat survey, `record` auto-advances the cursor and `advance` is only for parent-past-consolidated-child — not obvious from the skill text. Minor; recovered quickly.
- **Instructions improvised around:** None of substance. My first SG-artifact toy (synthetic regular grid) was a poor demonstration because it lacked the real stream's hardware quantization; I replaced it with a clean shuffle-of-the-real-dt-sequence test, which is the rigorous proof. Reporting that so the method is on record.
- **What would have made this easier:** none — confirmed after review: the handoff carried the JSON paths, the exact verdicts to re-derive, the 0a primitive list, and the platform invariants; everything needed to verify independently was present.

## Return status
`complete`
