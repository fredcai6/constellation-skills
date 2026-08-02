# Implementer Handoff

## Gate
g2 (g2-implement)

## Task
Build a read-only script `scripts/characterize_timetag_jitter.py` that, over the SAME 6
sessions G1 used, quantifies the TIME-TAG error model and the INTER-STREAM offset stability
that the GO/NO-GO turns on. Reuse the 0a `cross_residual` primitive, `offline_loader`, and
`db_truth_loader`. Emit per-session JSON (filenames containing `jitter` and/or `offset`) to
`.agent-work/issue-447/evidence/`.

## Protected Intent
This is the CORE of epic #445's GO/NO-GO. The spec's question: is the data correlatable
enough to support trajectory estimation — i.e. are inter-stream OFFSETS ESTIMABLE and are
CROSS-RESIDUALS BOUNDED? Your measured jitter model and offset-stability numbers are the
evidence the human's decision rests on. Be honest: a measured negative (NO-GO) is as valuable
as a positive. Characterization ONLY — no estimator/filter/smoother as a deliverable.

## Inherited G1 facts (already measured + reviewer-confirmed — build on these, do not relitigate)
- Raw `session.car_data` and `session.pos_data` are TWO SEPARATE IRREGULAR grids, ~4.2 Hz
  MEDIAN each (NOT 240/10 Hz, NOT a shared grid). car base tick ~40 ms; pos ~10-20 ms;
  ~0.4% exact timestamp overlap; median nearest-neighbour distance ~0.065 s. This means there
  IS genuine inter-stream timing structure — an inter-stream offset is a meaningful quantity
  to estimate (this is the G2 question).
- pos_data X/Y/Z in DECIMETRES (×0.1 → m); quantization exactly 0.1 m.
- Per-channel G1 noise: Speed ~1.3-1.6 (km/h)^2; XY ~0.04-0.55 m^2; Z 0.4-4.85 m^2 (Spa high).
- G1 evidence JSON: `.agent-work/issue-447/evidence/char_*.json` (read these for the per-session
  noise + grid numbers you'll build on).
- Session set: 2023 Belgian Q+R, 2022 Spanish R, 2024 British Q+R, 2023 São Paulo R (wet).

## Close Criteria — measure and store, per session, with distributions
1. **Time-tag JITTER magnitude per stream**: residuals of the SessionTime timestamps against
   (a) a smooth/expected-cadence fit (the deviation of actual sample instants from a locally
   regular cadence) AND (b) sector-crossing constraints — use `db_truth_loader` to get the
   official sector split times from the season DB and measure how far the telemetry-derived
   sector-crossing instants deviate from DB truth. Report a DISTRIBUTION (median, IQR, tails),
   in seconds, per stream.
2. **Time-tag ERROR-MODEL CLASS**: classify the jitter as one of {pure bias, random-walk,
   per-batch (per-Source/per-transmission-block) offset} with the EVIDENCE for the choice:
   test for per-batch structure (does jitter cluster by Source/transmission block?),
   autocorrelation of the residual (random-walk signature = slow-decaying autocorr / drift),
   and constant offset (bias). State the chosen class and show the discriminating statistic.
3. **INTER-STREAM clock-offset STABILITY (resolves 0a finding F2)**: using the 0a
   `diagnose_cross_residual` primitive (fits a per-lap inter-stream time offset), measure
   per-lap AND per-session offsets across all laps in each session. Characterize whether the
   inter-stream offset is an ESTIMABLE STABLE bias (tight per-lap distribution, low
   autocorrelation of the per-lap deviations around a session mean) or per-lap WANDER (wide
   spread, drift). Report: per-session mean offset, per-lap spread (std / IQR / range),
   autocorrelation/drift of the per-lap series, and the per-lap arc-residual after offset fit
   (the "bounded cross-residual" half of the gate). 0a saw per-lap offset ranges like
   [-0.20,+0.41], [-0.23,+0.03], [-0.08,+0.36] s on its 3 sessions — quantify the same across
   yours and say: stable-estimable or wander.
4. **Reduced chi-square the 0a covariance gate would see**: given your measured per-channel
   noise model (from G1 + refined here), compute the reduced chi-square values the 0a
   covariance gate computes, so G3 can recommend a tightened acceptance band (resolves F1).
   The 0a strawman saw 0.60-11.14 with the loose [0.01,100] band.

## Allowed Scope
- `scripts/characterize_timetag_jitter.py` (new).
- `.agent-work/issue-447/evidence/*.json` (outputs).
- Read-only reuse of `src/preprocessing/trajectory_grading/{cross_residual,offline_loader,db_truth_loader,contract}.py`.
- OPTIONAL tested `src/preprocessing/` helper only if genuinely reusable — else keep in scripts/.

## Specific Exclusions
- NO `get_telemetry`; NO network; offline cache only.
- NO estimator/filter/smoother as a deliverable (a smooth fit purely to MEASURE jitter is fine).
- NO evo imports; NO DB writes (sector truth via `file:?mode=ro`, which db_truth_loader does).
- Do NOT decide GO/NO-GO. Do NOT fork the 0a primitives — import them.

## Constraints
- Raw streams only via offline_loader; offline cache `C:/Programs/f1Brainz/outputs/cache`.
- Sector truth: `db_truth_loader` reads `C:/Programs/f1Brainz/data/f1_data_<year>.db` via
  `file:?mode=ro`. DB GP naming "Belgium" vs FastF1 "Belgian Grand Prix" — db_truth_loader maps
  it for the 0a sessions; CHECK new sessions (2024 British, 2023 São Paulo) resolve, and report
  if a session's sector truth is missing (degrade gracefully — jitter-vs-cadence still works).
- pos_data DECIMETRES; `py` not `python`; PYTHONUTF8=1 in captured subprocess env.
- Long compute FOREGROUND. Any touched src/ → `py -m src.utils.simplification_limits`.

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing` — `trajectory_grading/{cross_residual,db_truth_loader}.py`; `scripts/`.
- **Capability:** inter-stream correlatability characterization — the GO/NO-GO core.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; characterization-only.
- **Decision anchors:** F2 (offsets wander vs stable bias — resolve from evidence); error-model
  class choice; 0a's cross-residual-is-a-diagnostic split (respect it — you REPORT, don't gate).
- **Evidence expectations:** jitter distribution, evidence-backed error-model class, per-lap/
  per-session offset stability, chi-square the gate would see. Every number traceable to script
  + session.

## Required Evidence
- Per-session jitter/offset JSON + an aggregate summary.
- Captured stdout of a full run on the real cache.
- For each session: the per-lap offset series stats + the error-model classification statistic.

## Verification Commands
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-447
py scripts/characterize_timetag_jitter.py   # or its documented invocation
py -c "import glob; print(glob.glob('.agent-work/issue-447/evidence/*jitter*')+glob.glob('.agent-work/issue-447/evidence/*offset*'))"
```

## Suggested Model Tier
stronger — reason: this is the GO/NO-GO core; statistical care on the error-model
classification and the stable-vs-wander call matters, and it must NOT slide into estimator work.

## Authority
Statistical method, error-model discriminators, JSON shape are YOURS — document them. You must
NOT: decide GO/NO-GO, build an estimator, cross into evo/data, use get_telemetry, fork 0a code.

## Stop Conditions
Stop and return if: sector truth is unavailable for ALL sessions (report what jitter-vs-cadence
still yields); a required quantity is impossible; scope must be exceeded; a decision outside
authority is needed; the work starts to require estimator construction (it must not — flag it).

## Return Format
Return IMPLEMENTER_RESULT to
`C:/Programs/f1Brainz-worktrees/cmdr-447/.agent-work/issue-447/crew-handoffs/g2-implement-result.md`:
completed slice, files changed, evidence JSON paths + headline numbers (jitter magnitude +
distribution per stream; chosen error-model class + its discriminating statistic; per-session
inter-stream offset mean + per-lap spread + stable/wander verdict; chi-square range), session
set, assumptions, stop conditions, out-of-scope observations, workflow feedback. Then a concise
final message leading with the stable-vs-wander verdict and the error-model class.
