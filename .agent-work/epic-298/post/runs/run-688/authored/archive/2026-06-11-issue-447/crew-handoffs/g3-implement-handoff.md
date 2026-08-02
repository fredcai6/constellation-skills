# Implementer Handoff

## Gate
g3 (g3-implement)

## Task
Author the DELIVERABLE `docs/physics/measurement_model.md` from the G1+G2 evidence, and within
it assemble the operationalized GO/NO-GO evidence pack with a clearly-labeled RECOMMENDATION.
This is the single most important artifact of issue #447 — it is the human's decision brief for
epic #445's estimator fork. Write it so a careful NON-SPECIALIST can follow it.

## Protected Intent
The document IS the deliverable (not code). Every number must be traceable to its G1/G2 script +
session and match the on-disk evidence JSON. You RECOMMEND GO/NO-GO; you do NOT decide it (the
human ratifies). A rigorous NO-GO would be as valuable as a GO — but the measured evidence here
leans GO; present it honestly, neither overselling nor underselling. Mark every recommendation
explicitly as a recommendation.

## Test Mode
Docs-primary (the deliverable is a doc). If you add any durable noise-model reader in
`src/preprocessing/`, it needs a unit test (test-after allowed) and `simplification_limits`.
PREFER doc-only: the measured artifact is the script JSON already on disk; a thin reader is only
warranted if you judge it genuinely reusable by Phase 1 — if not, document WHY the script-only
artifact suffices (one paragraph) and ship doc-only.

## The measured evidence to write up (all from .agent-work/issue-447/evidence/, traceable)
Read `char_summary.json`, `jitter_offset_summary.json`, and the per-session files. Headlines:

SAMPLING / QUANTIZATION / Z (G1, scripts/characterize_telemetry_instruments.py):
- car_data & pos_data: ~4.2 Hz MEDIAN cadence each; TWO SEPARATE IRREGULAR grids (car base tick
  ~40 ms, pos ~10-20 ms, ~0.4% timestamp overlap, median nearest-neighbour ~0.065 s). NOT 240/10
  Hz (that's the merged get_telemetry product), NOT a shared grid.
- Position quantization: X/Y/Z exactly 1.0 dm = 0.1 m, uniform across all sessions.
- Z-channel: PASS on all 30 driver-sessions (range 467.9 m at Spa; ~15 m Silverstone).
- Per-channel noise (residual var vs local smooth fit): Speed 1.3-1.6 (km/h)^2; X 0.039-0.19 m^2;
  Y 0.056-0.55 m^2; Z 0.41-4.85 m^2 (Z elevated at hilly Spa).

JITTER / ERROR MODEL / OFFSET (G2, scripts/characterize_timetag_jitter.py):
- Time-tag jitter: car/pos cadence-residual IQR ~0.128-0.141 s; sector-crossing |median| vs DB
  truth 0.10-0.16 s.
- Error-model class: WHITE-JITTER (no bias/random-walk/per-batch) — consensus all 6 sessions.
  Discriminators: dt-deviation lag-1 autocorr ~0; per-Source eta^2=0; |mean|/std ~1e-4. (The
  SG-residual autocorr ~0.6 is a smoothing artifact — reviewer proved this via a shuffled-white
  control; the honest discriminator is the dt-deviation series, which is white.)
- Inter-stream offset stability (resolves 0a F2): STABLE-ESTIMABLE on all 6 sessions.
  |session-mean offset| <= 0.081 s; median per-lap offset std 0.084-0.129 s; per-lap range
  0.32-0.50 s; low per-lap autocorr/drift. Per-session means: Belgian Q -0.004, Belgian R -0.081,
  Spanish R +0.040, British Q -0.009, British R -0.069, São Paulo R -0.019 s.
- Covariance-gate reduced chi-square the 0a gate WOULD see: 78.7-3292 — reviewer-confirmed to be
  DOMINATED by the unremoved inter-stream offset's arc term (mean |residual| ~5.5 m), NOT by
  positional noise. Removing the per-lap offset collapses chi-square toward the 0a range (one
  session: 95.9 -> 63.9 after offset removal).

## Close Criteria — the document MUST contain
1. Per-stream sampling-interval distributions (the two-separate-grids picture, with the
   overlap-fraction/base-tick numbers — do NOT say "shared grid" or "240/10 Hz").
2. Position quantization steps (0.1 m); Z-channel verdict (PASS, with the elevated-Z-at-Spa note).
3. Time-tag jitter magnitude + an EXPLICIT error-model: state WHITE-JITTER, with the
   discriminating statistics and the SG-artifact caveat. This is "the thing the old estimator had
   to assume" — frame it that way.
4. Per-channel noise covariances (with units).
5. Inter-stream offset stability: estimable stable bias (the F2 resolution), with the per-session
   numbers.
6. **OPERATIONALIZED GO/NO-GO gate**: state the measured criteria for BOTH halves —
   "offsets estimable" AND "cross-residuals bounded" — BEFORE applying them (show the
   operationalization, then apply). Suggested operationalization (refine with the data, justify
   any change): offsets-estimable = per-session offset is a tight, low-drift bias (e.g. per-lap
   offset std below the ~0.13 s jitter scale, |session-mean| small, low autocorr) — MET on 6/6;
   cross-residuals-bounded = after free per-lap offset removal the arc-residual is at the
   metre-scale consistent with the measured positional noise and the chi-square approaches the
   tightened band — assess from the per-driver arc-residuals in the G2 JSON. Apply both, show the
   pass/fail per session.
7. **Clearly-labeled RECOMMENDATION**: GO / NO-GO / marginal-with-analysis, written as a
   RECOMMENDATION for the human. Given the measured evidence (stable estimable offsets 6/6, white
   jitter, bounded post-offset residuals), this points to GO — but state the caveats honestly
   (the raw chi-square is large until the offset is modeled; the offset IS the thing a Phase 1
   estimator must include; messy/wet session behaves like the dry ones, which is reassuring).
8. **F1 — covariance-gate chi-square band recommendation** with the noise-model justification.
   IMPORTANT CONTEXT: the gate FUNCTION `src/preprocessing/trajectory_grading/covariance_gate.py`
   ALREADY defaults to band (0.5, 2.0); the loose [0.01, 100] in 0a's finding F1 is what the
   STRAWMAN RUNNER applied. So F1 is: recommend the band the runner/contract should use, justified
   by your measured noise model, AND explicitly note that the gate must be applied to an
   OFFSET-REMOVED residual (or with per-sample variance inflated to include the offset arc term) —
   otherwise the offset dominates and any band is meaningless. Recommend a concrete band (e.g.
   keep ~(0.5, 2.0) on the offset-removed residual) with the reasoning. Do NOT change code unless
   trivially warranted; this is a documented recommendation for Phase 1.
9. **F3 — s_finish free-anchor design DECISION** with evidence. Decide: should `s_finish` be a
   free anchor for circuits with ambiguous start/finish-line positions? Ground it in the measured
   lap-closure / sector-anchor behavior (the 0a sector-anchor co-estimates s1/s2/s3; consider
   whether the finish-line arc-length needs to float too). State the decision and its rationale.
10. A `Last verified: 2026-06-11` line and a methods/traceability section pointing each number to
    its script + evidence JSON.

## Allowed Scope
- `docs/physics/measurement_model.md` (new — THE deliverable).
- OPTIONAL: a tested read-only noise-model reader in `src/preprocessing/` IF genuinely reusable.
- You may read all `.agent-work/issue-447/evidence/*.json` and the G1/G2 scripts and result files.

## Specific Exclusions
- NO estimator/filter/smoother (Phase 1, gated behind this GO).
- NO deciding GO/NO-GO (recommend only); NO merging; NO closing the issue/epic.
- NO evo imports; NO changing the 0a primitives' behavior (a band recommendation is a DOC, not a
  code edit, unless you judge a trivial default change warranted AND it gets a test — prefer doc).
- Do NOT invent numbers — every figure traces to the evidence JSON.

## Constraints
- The document is the deliverable; numbers traceable to script + session.
- Operationalize BOTH gate halves before applying.
- `py` not `python`; any touched src/ → `py -m src.utils.simplification_limits`.
- Docs reviewer bar: valid commands, existing references, current workflow, units/bounds explicit,
  `Last verified` line.

## Map Anchors (inbound)
- **Structural:** `docs/physics/measurement_model.md` (deliverable, alongside docs/physics/overview.md,
  windowed_estimator.md); `src/preprocessing/` (any reader);
  `docs/report_schemas/trajectory_grading_report.md` (the chi-square band informs its covariance gate).
- **Capability:** measurement-model contract for Phase 1 estimators.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; recommendation-only.
- **Decision anchors:** F1 (chi-square band), F3 (s_finish), error-model class (white-jitter from
  G2). The measurement-model doc becomes a durable physics contract (Cartographer will reconcile).
- **Evidence expectations:** operationalized gate criteria applied to measured values; labeled
  GO/NO-GO recommendation a non-specialist can follow.

## Required Evidence
- The committed `docs/physics/measurement_model.md`.
- If a reader is added: its passing unit test + simplification_limits output.

## Verification Commands
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-447
py -c "import os; assert os.path.exists('docs/physics/measurement_model.md'); print('doc present')"
# if a src/preprocessing reader added:
py -m pytest tests/unit/preprocessing/<new_test>.py -q
py -m src.utils.simplification_limits src/preprocessing/<file>
```

## Suggested Model Tier
stronger — reason: this synthesizes the whole run into the human's GO/NO-GO brief; the
operationalization, F1 band, and F3 decision require judgment and must be honest and precise.

## Authority
The measurement-model document structure, the operationalization of both gate halves, the F1 band
recommendation, and the F3 s_finish decision are YOURS to make from evidence — document them. You
must NOT: decide GO/NO-GO (recommend only), build an estimator, cross into evo, merge, or close
issues.

## Stop Conditions
Stop and return if: a required number is not in the evidence JSON (do not invent it); the
operationalization reveals the evidence cannot support either gate half (then write the honest
NO-GO/marginal with that finding); scope must be exceeded; a decision outside this authority is
needed.

## Return Format
Return IMPLEMENTER_RESULT to
`C:/Programs/f1Brainz-worktrees/cmdr-447/.agent-work/issue-447/crew-handoffs/g3-implement-result.md`:
completed slice, files changed, the operationalized gate criteria + per-session pass/fail, the
labeled recommendation (GO/NO-GO/marginal), the F1 band + F3 decision as stated in the doc,
assumptions, stop conditions, out-of-scope observations, workflow feedback. Then a concise final
message leading with the recommendation and the F1/F3 calls.
