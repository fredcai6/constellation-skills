# Run Summary — issue #447 (Phase 0b instrument characterization + GO/NO-GO)

## Verdict
Characterization COMPLETE. **RECOMMENDATION: GO** (a recommendation, not a decision — the
human ratifies the epic fork). The FastF1 telemetry IS correlatable enough to support
trajectory estimation: both gate halves pass on 6/6 sessions including the wet one.

## Gates closed (all APPROVE; one rework on G1)
- **G1** per-stream instrument characterization — APPROVE (after 1 rework: reviewer's
  independent re-measurement BLOCKED an over-claim that the two raw streams share one grid;
  implementer corrected it and added a measured grid-relationship metric).
- **G2** time-tag jitter model + inter-stream offset stability — APPROVE (all three
  load-bearing verdicts independently re-computed by the reviewer, incl. a shuffled-white
  control proving the SG-residual autocorr is a smoothing artifact).
- **G3** measurement-model doc + GO/NO-GO evidence pack — APPROVE (15 spot-checked numbers
  matched the JSON; provenance honesty confirmed).

## Changes implemented
- `scripts/characterize_telemetry_instruments.py` (G1, read-only).
- `scripts/characterize_timetag_jitter.py` (G2, read-only; reuses 0a primitives).
- `docs/physics/measurement_model.md` (G3 — THE deliverable: measurement model + GO/NO-GO brief).
- `src/preprocessing/trajectory_grading/offline_loader.py` docstring corrected (240/10 Hz → two
  separate ~4.2 Hz irregular grids). No behavior change.
- `docs/architecture/index.md` + `packets/preprocessing.md` reconciled (#447 line + Phase 0b
  section; check_arch_map.py OK, 37 nodes).
- 13 evidence JSON under `.agent-work/issue-447/evidence/` (untracked; not committed).

## Headline measured numbers
- Sampling: car & pos both ~4.2 Hz MEDIAN, two SEPARATE irregular grids (car base tick ~40 ms,
  pos ~10-20 ms, ~0.4% timestamp overlap, median nearest-neighbour ~0.065 s). NOT 240/10 Hz.
- Quantization: X/Y/Z exactly 0.1 m. Z-channel PASS 30/30 (noise circuit-dependent; highest at
  São Paulo 8.12 m²).
- Per-channel noise: Speed 1.3-1.6 (km/h)²; X 0.04-0.19 m²; Y 0.06-0.55 m²; Z 0.02-8.12 m².
- Time-tag jitter: cadence-residual IQR ~0.13 s; sector-crossing |median| 0.10-0.16 s.
- Error model: WHITE-JITTER (no bias/random-walk/per-batch) — consensus 6/6.
- Inter-stream offset: STABLE ESTIMABLE bias 6/6 (|session mean| ≤ 0.081 s; per-lap std
  0.084-0.129 s; low drift). Resolves 0a finding F2 favorably.
- Covariance chi-square the 0a gate would see: 78.7-3292, offset-dominated (not noise); removing
  the offset collapses it toward the 0a range.

## GO/NO-GO evidence pack (operationalized)
- Half A "offsets estimable": per-lap offset std ≤ 0.15 s, |session mean| ≤ 0.13 s, |lag-1
  autocorr| < 0.5 → PASS 6/6.
- Half B "cross-residuals bounded": post-offset arc-residual at the few-metre §4 noise scale and
  chi-square moves toward the band on offset removal → PASS 6/6.
- F1: keep covariance-gate band (0.5, 2.0), applied to an OFFSET-REMOVED residual (gate already
  defaults to that band; no code change). F3: promote s_finish to a free co-estimated anchor
  (evidence: s3 pins to track length when s_finish is fixed).

## Map impact
No new structural nodes/edges/overlays. New durable physics contract doc
`docs/physics/measurement_model.md`; offline_loader docstring corrected; two non-node scripts as
packet prose. check_arch_map.py OK.

## Triage candidates (issue-ready; NONE filed — all gated on GO ratification)
TR-1 Phase 1 estimator (GO fork); TR-2 F1 gate contract; TR-3 F3 s_finish; TR-4 fusion timing
structure. See triage-candidates/RECOMMENDATIONS.md. tc1 docstring half already fixed in-run.

## Open user-decisions floated
- The GO/NO-GO ratification itself (recommendation: GO) — human's call.
- Whether/when to file TR-1 and open Phase 1 — gated on the ratification.

## Still to do (archive step)
Push branch; open PR (no merge); post verdict comment on issue #447; record AGENT_FEEDBACK +
lessons delta; archive work area.
