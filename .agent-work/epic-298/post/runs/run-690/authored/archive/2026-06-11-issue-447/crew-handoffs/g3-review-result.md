# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3 (g3-review)` — issue #447 Phase 0b: independently verify `docs/physics/measurement_model.md` and its GO/NO-GO evidence pack.

## Result
`APPROVE`

## Handoff compliance
The doc delivers exactly what the handoff asked: a measurement model for the two
raw FastF1 streams (`session.car_data`, `session.pos_data`) plus an
operationalized GO/NO-GO brief with a clearly-labeled GO recommendation, the F1
chi-square band recommendation, the F3 `s_finish` decision, a `Last verified:
2026-06-11` line, and a §11 number→source traceability table. It recommends and
does not decide. All stop conditions clear (no number contradicts the JSON, no
reviewer-only number passed off as on-disk evidence, recommendation not presented
as decision, gate operationalized before application, F1/F3 supported, references
and commands valid).

## Scope drift
Clean. `git status --short` shows only `docs/physics/measurement_model.md` and the
`.agent-work/` directories as new/untracked. No `src/` changed. No estimator,
filter, or smoother. No GO/NO-GO decision (recommendation only). No merge/close.
No evo import. No 0a primitive behaviour change (F1/F3 are documented
recommendations, not code edits).

## Evidence verdict — independent number traceability (the load-bearing check)
I loaded all 14 evidence JSON files myself (`py -c json.load`) and compared 12
numbers across §1–§7, §10 against on-disk values. **Every one MATCHES.**

| # | Doc claim (section) | Doc value | On-disk JSON value | Match |
|---|---|---|---|---|
| 1 | Both streams ~4.2 Hz (§1) | ~4.2 Hz | `char_summary.aggregate.{car,pos}_data.approx_sample_rate_hz` = 4.2 / 4.2 | ✅ |
| 2 | Median dt 0.240 s; pos range to 0.241 (§1) | 0.2400 / 0.2400–0.2410 | car median_dt 0.2400–0.2400; pos 0.2400–0.2410 | ✅ |
| 3 | Belgian Q overlap 0.40 % (87/21764) (§1) | 0.40 %, 87 | `grid_relationship.VER.overlap_fraction`=0.003997, `n_exact_overlaps`=87 | ✅ |
| 4 | Belgian Q rows 21051/21764/713; ticks 0.04/0.01; nn 0.067 (§1) | as stated | car_row=21051, pos_row=21764, diff=713, car_base_tick=0.04, pos_base_tick=0.01, median_nn=0.067 | ✅ |
| 5 | São Paulo rows 41390/42180/790 (§1) | as stated | car=41390, pos=42180, diff=790 | ✅ |
| 6 | 0.1 m quantization all axes (§2) | 0.1 m | `aggregate.pos_data.{X,Y,Z}_min_step_m_range`=[0.1,0.1] | ✅ |
| 7 | Z PASS 30/30 (§2) | 30 PASS, 0 MARGINAL, 0 UNUSABLE | `z_verdict_distribution`={PASS:30,MARGINAL:0,UNUSABLE:0} | ✅ |
| 8 | Belgian Q Z range 467.9 m; São Paulo 782.0 m (§2) | 467.9 / 782.0 | `z_channel_verdict.range_m`=467.9 / 782.0 | ✅ |
| 9 | Per-session offsets §5 (all 6 rows) | e.g. BelQ −0.004/0.129/0.435; SãoP −0.019/0.089/0.416 | `per_session[*]` mean/std/range match all 6 to 3 dp | ✅ |
| 10 | Noise variances §4 (Belgian Q + São Paulo) | Z 0.018–4.851, X 0.069–0.286, Y 0.181–0.550, Speed 0.37–1.49; SãoP Z 0.457–8.121 | `noise_covariance.*` per driver reproduce exactly | ✅ |
| 11 | Chi-square range 78.7–3292 (§7) | 78.7–3292 | `aggregate.covariance_reduced_chi_sq_range_across_sessions`=[78.661, 3291.986] | ✅ |
| 12 | Cadence IQR car 0.128–0.141 / pos 0.128–0.138; sector \|median\| 0.102–0.158 (§3) | as stated | `cadence_jitter_{car,pos}_data_iqr_s_range`, `sector_crossing_jitter_abs_median_s_range` match | ✅ |
| + | Belgian Q arc_abs_median VER 4.92 / GAS 7.62 (§6) | 4.92 / 7.62 | `offset_stability.arc_residual_distribution.arc_abs_median`=4.924 / 7.623 | ✅ |
| + | Error-model discriminators (§3) | car −4e-5, pos −0.039, SG 0.630 ref-only, \|mean\|/std ~1e-4 | dt-dev autocorr car −4.0e-5, pos −0.0386; SG 0.6304 (`reference_only`); \|mean\|/std 9.8e-5 | ✅ |
| + | F3 s3 pins to track length (§10) | VER/NOR/GAS s3≈7004.0; SAR 6998.3, RIC 6990.5; GAS 0.31 s | `fitted_anchors_m.s3`=7003.99996/7004.0/7004.0; 6998.26/6990.51; GAS abs_median 0.3105 | ✅ |

The evidence backs the claimed measurement-model contract. Test mode docs-primary
is correct (deliverable is a doc; no `src/` reader added — the implementer's
justification against adding a redundant JSON wrapper is sound and respects the
one-canonical-path tenet).

## Per-check findings (survey, all 13 PASS → consolidated APPROVE)

- **r4 Traceability:** 12 numbers traced; all match (table above). No fabrication.
- **r5 Corrected picture:** §1 explicitly states NOT a single shared timeline and
  NOT 240/10 Hz (correctly attributes 240/10 Hz to the merged `get_telemetry()`
  product), says two separate irregular grids ~4.2 Hz, `separate_grids` tag on all
  30 driver-sessions. Honored.
- **r6 Operationalization:** §6 states Criterion A (std ≤ 0.15 s AND \|mean\| ≤
  0.13 s AND \|ac\| < 0.5) and Criterion B (post-offset arc residual ≲ ~8 m AND
  χ² moves toward band) in blockquotes **before** the per-session Application
  table. Pass/fail genuinely follows from the verified numbers: all 6 sessions
  std ≤ 0.128, \|mean\| ≤ 0.081, ac < 0.5 → Half A PASS; arc 4.9–7.6 m < 8 m →
  Half B PASS. Half B honestly flags that only Belgian Q carries an explicit
  re-computed χ²; the other five are marked "offset-dominated / direction
  confirmed," not given fabricated numbers.
- **r7 Recommendation:** §8 GO is inside a blockquote reading "This is a
  recommendation, not a decision. The human ratifies." (header line 5 echoes it).
  Honest caveat present: raw χ² large (78.7–3292) until offset modelled, dominated
  by the offset arc term not positional noise; §8 also lists what would have made
  it NO-GO. Labeled, honest.
- **r8 F1 band:** §9 recommends keeping band (0.5, 2.0) with a noise-model
  justification (factor-of-two tolerance on the ~0.1–0.5 m² XY variance once the
  offset is removed). I confirmed `covariance_gate.py` **already** defaults to
  `band: tuple[float, float] = (0.5, 2.0)` (line 46) and the report schema
  `cov_band`. The doc correctly attributes the loose `[0.01, 100]` to the strawman
  runner (matches the JSON `covariance_chi_square.band` field) and correctly
  requires the band apply to an offset-removed residual. No code change.
- **r9 F3 s_finish:** §10 makes a clear decision to promote `s_finish` to a free
  co-estimated anchor (with lap-length scale fixed). Backed by verified evidence:
  Belgian Q VER/NOR/GAS fit s3 = 7003.9999…≈ track length (pinned to bound) while
  SAR/RIC land unpinned at 6998.3/6990.5 m; GAS sector residual 0.31 s. The
  current-behaviour claim (`s_finish` fixed at 0.0) is accurate — verified in
  `sector_anchor.py` (lines 20, 216, 243).
- **r10 Provenance (critical):** PASS. The raw **95.9** IS in the JSON
  (`jitter_offset_2023_Belgian_Q.json` → VER `covariance_chi_square.reduced_chi_sq`
  = 95.9085) and the doc cites it as on-disk. The **63.9** offset-removed value is
  NOT in any of the 14 JSON files (I grepped) and the doc explicitly flags it in
  §6, §7, and §11 as "the G2 reviewer's independent re-computation
  (`g2-review-result.md`, Verdict 3), not the on-disk evidence JSON." Verdict 3
  confirms 95.9 → 63.9. The SG-residual 0.630 is cited "reference-only," matching
  the JSON's `..._reference_only` key. No fabricated number found.
- **r11 Docs bar:** both reproduce scripts exist; all five referenced files exist
  (overview.md, windowed_estimator.md, trajectory_grading_report.md,
  covariance_gate.py, sector_anchor.py); units/bounds explicit throughout;
  `Last verified: 2026-06-11` present in header and footer.

## Map impact verdict
- **Evidence supports claimed change:** Yes — every headline traces and matches;
  the three G2 load-bearing verdicts (white-jitter, stable-estimable offset,
  offset-dominated χ²) are carried faithfully.
- **Constraints not violated:** Yes — `constraint:physics_region_no_evo_import`
  honored (doc-only); recommendation-only authority honored.
- **Notes match the diff:** Yes — new durable physics contract under
  `struct:physics`; no committed schema/contract changed; the only file diff is
  the doc.
- **Decision candidates surfaced:** Yes — F2 resolved; F1 band and F3 `s_finish`
  surfaced as Phase 1 implementation candidates routed to Commander/#445, not
  applied to code.
- **Durable context routed:** Yes — the doc becomes a Cartographer-reconciled
  physics contract; triage candidates flagged.

## Reconciliation check
No docs/contracts/structural-baseline concern. No public interface or committed
report-schema change. Doc-only addition consistent with current physics-region
workflow.

## Blockers
- none

## Out-of-scope observations
- **(Handoff/evidence summarization gap — already flagged by the implementer; I
  concur.)** The handoff's per-channel noise headline ranges (Speed 1.3–1.6;
  X 0.039–0.19; Y 0.056–0.55; Z 0.41–4.85) are a single-session subset; the full
  across-all-sessions JSON ranges are wider (Speed 0.078–3.656; X 0.033–1.190;
  Y 0.022–0.837; Z 0.018–8.121). The doc correctly uses the JSON-traceable wider
  ranges and documents the divergence in a Note block. "Z elevated at Spa" is
  superseded by São Paulo's larger Z noise (8.121 m²) in the evidence — the doc's
  honest correction is right. This is a handoff-summary gap, not a doc defect.
- F1 (offset-removed gate residual) and F3 (free `s_finish` with a bound-unpinning
  test) are ready-to-implement Phase 1 design items for the #445 fork.

## Workflow Feedback
Mandatory section.

- **Handoff gaps:** none of substance — the review handoff was precise: it named
  the exact spot-checks, the §-by-§ criteria, the critical provenance trap (the
  95.9→63.9 reviewer-only number), and the platform invariants. The one carryover
  is the same noise-range subset issue the implementer already flagged; the review
  handoff inherited it but explicitly told me to flag-or-match, which I could act
  on without ambiguity.
- **Context rediscovered:** the JSON aggregate key names differ slightly from the
  doc's §11 prose (`cadence_jitter_car_data_iqr_s_range`, not `..._car_...`), so I
  had to enumerate keys before reading them. Minor; a doc that quoted the exact
  aggregate key strings would have removed the lookup.
- **Instructions improvised around:** the engine `consolidate` verb takes
  `--verdict`/`--summary`, not the `--result`/`--finding` used by `record` (one
  argparse rejection before I corrected it). Worth noting in the engine reference
  alongside the existing constellation-engine-quirks memory.
- **What would have made this easier:** a one-line provenance map in the handoff
  pointing the 63.9 figure to `g2-review-result.md` Verdict 3 (the implementer
  asked for the same) — I confirmed it by grep, but a pointer would save the
  discovery step. Otherwise nothing.

## Return status
`complete`
