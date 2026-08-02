# Reviewer Handoff

## Gate
g1 (g1-review)

## What Was Implemented
`scripts/characterize_telemetry_instruments.py` — read-only characterization of raw FastF1
`car_data`/`pos_data` streams over 6 cached sessions (3 seasons, incl. a wet session). Emits
per-session + summary JSON to `.agent-work/issue-447/evidence/`. Measured: sampling-interval
distributions, position quantization, Z-channel quality, per-channel noise covariance.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-447
git status
git diff --stat
git diff -- scripts/characterize_telemetry_instruments.py
# evidence (untracked, under .agent-work):
py -c "import glob,json; [print(f) for f in sorted(glob.glob('.agent-work/issue-447/evidence/*char*'))]"
```
Implementer result: `.agent-work/issue-447/crew-handoffs/g1-implement-result.md`.

## Task Statement
Build a read-only script measuring, per raw stream, over >=6 sessions / >=2 seasons (incl. a
messy/wet session): (1) sampling-interval distribution; (2) position quantization step (dm AND
m); (3) Z-channel quality verdict; (4) per-channel noise covariance. Numbers traceable to
script + session. Raw streams only (no `get_telemetry`), offline cache only, pos_data in
DECIMETRES.

## Close Criteria (each becomes a review check)
- Script is read-only, imports the 0a `offline_loader`, runs on the real offline cache.
- NO `get_telemetry`, NO network fetch, NO evo imports, NO DB writes. (AST-verify, not just grep.)
- Decimetre handling correct (pos_data ×0.1 → metres; quantization reported in dm AND m).
- All four measurements computed per stream per session, soundly and reproducibly.
- Session selection meets pre-ruling 6: >=6 sessions, >=2 seasons, >=1 wet/red-flag session.
- Numbers traceable to the on-disk JSON.

## CRITICAL REVIEW MANDATE — verify the 4.2 Hz claim independently
The implementer reports a HEADLINE finding that BOTH `session.car_data` and
`session.pos_data` sit on a single session-unified **~4.2 Hz (240 ms) timeline**, NOT the
commonly cited 240 Hz / 10 Hz, and that both streams share the SAME timestamp grid. This claim
will materially drive the epic's GO/NO-GO (if both raw streams share one clock grid, there is
no differential rate to exploit and arguably no independent inter-stream clock to estimate).
**Do NOT take it on faith.** Independently confirm or refute it with your OWN throwaway script:
- Load one session's raw `session.car_data[drv]` and `session.pos_data[drv]` directly via
  `offline_loader` and inspect the actual `SessionTime` / `Date` diffs for a single driver.
- Check whether car_data and pos_data timestamp grids are truly identical or merely similar in
  median dt (median dt alone does NOT prove a shared grid — check the actual values align).
- Sanity-check against FastF1's own understanding: is `session.car_data` the per-driver raw
  channel, and could the ~4.2 Hz be an artifact of how rows are sampled/decimated, NaN-padding,
  or driver row alignment? State definitively what the raw streams' true cadence is.
This is the single most important thing to get right. If the implementer's characterization of
the cadence is wrong, BLOCK with the corrected measurement.

## Allowed Scope
`scripts/characterize_telemetry_instruments.py`; `.agent-work/issue-447/evidence/*.json`;
read-only reuse of `offline_loader`. Optionally a tested `src/preprocessing/` helper.

## Specific Exclusions (flag if touched)
`get_telemetry`/merged product; network fetch; estimator/filter as a deliverable; evo imports;
DB writes; any GO/NO-GO decision.

## Constraints the Implementation Must Respect
- Raw streams only via `offline_loader`; offline cache `C:/Programs/f1Brainz/outputs/cache`.
- pos_data X/Y/Z in DECIMETRES (×0.1 → m).
- Analysis in `scripts/` (read-only); no evo imports; `py` not `python`.
- Any touched `src/` passes `py -m src.utils.simplification_limits`.

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing` (physics region); `scripts/` non-map analysis.
- **Capability:** instrument characterization upstream of trajectory grading.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; offline-cache +
  raw-streams sanctioned exception (telemetry not in DB).
- **Decision anchors:** 0a — cross-residual is a diagnostic, not a gate.
- **Evidence expectations:** sampling-interval distributions, quantization, Z verdict,
  per-channel covariances — every number traceable to script + session. The 4.2 Hz cadence
  claim is the load-bearing one.

## Evidence Produced
6 per-session `char_*.json` + `char_summary.json`. Script ran in ~8s. Headlines: both streams
median dt 0.240 s; X/Y/Z quant exactly 1.0 dm = 0.1 m; Z PASS all 30 driver-sessions; Speed
noise 1.3–1.6 (km/h)^2; XY noise 19–55 dm^2; Z noise 41–485 dm^2 (elevated at Spa).

## Suggested Model Tier
stronger — reason: the load-bearing cadence claim contradicts common understanding and drives
the GO/NO-GO; needs an independent re-measurement, not a glance.

## Stop Conditions
BLOCK if: diff/evidence inaccessible or unverifiable; the 4.2 Hz cadence claim cannot be
independently confirmed (return your corrected measurement); a constraint was violated.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings (INCLUDING your independent
cadence measurement and whether it confirms/refutes 4.2 Hz), blockers, out-of-scope
observations, workflow feedback. Write it to:
`C:/Programs/f1Brainz-worktrees/cmdr-447/.agent-work/issue-447/crew-handoffs/g1-review-result.md`
