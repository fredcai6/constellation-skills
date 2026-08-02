# Review Result

## Assigned Gate
`g1 (g1-review) — Phase 0b telemetry instrument characterization (issue #447) — RE-REVIEW attempt 2`

## Result
`APPROVE`

## Handoff compliance
The rework satisfies the task statement and resolves blocker B1 in full. Change is
read-only/additive: a new `compute_grid_relationship()` measurement, corrected narrative in
three locations, and a docstring-only edit to `offline_loader.py`. Script still imports only
the 0a `offline_loader`, runs on the real offline cache, and computes all four original
measurement categories plus the new grid-relationship metric over 6 sessions / 3 seasons
(incl. wet São Paulo R). Re-ran end-to-end in ~9 s offline; per-session + summary JSON on disk.

## B1 resolution — per-part findings (independently re-measured)

**B1(a) NARRATIVE — RESOLVED.** Neither the script nor the result doc still *asserts*
"session-unified" / "shared grid" / "no differential rate." Verified by reading:
- Script docstring (lines 7–13) and the dropout comment (lines 110–117) now state: two
  separate irregular grids, ~4.2 Hz MEDIAN, distinct base ticks (car ~40 ms, pos ~20 ms),
  ~0.4 % overlap. The only "SHARED"/"session-unified" strings remaining are (i) line 431, the
  `compute_grid_relationship` docstring posing the question the code then *measures*, and (ii)
  result-doc lines 8–13, the rework note quoting the old claim to mark it corrected. Both are
  legitimate context, not live false assertions.

**B1(b) MEASURED GRID-RELATIONSHIP METRIC — RESOLVED.** `compute_grid_relationship()`
(script lines 425–521) genuinely computes per-stream row counts, GCD base tick (round-to-10 ms
then `functools.reduce(math.gcd, ...)`), exact-overlap count + fraction (searchsorted nearest-
neighbour within 0.1 ms), and median NN distance. Nothing hardcoded. Per-driver + per-session
`grid_relationship` keys with real numbers present in all 6 session JSONs and the summary.
   - **Independent re-measurement (Belgian Q, driver VER), loaded via offline_loader only:**
     car rows **21051**, pos rows **21764**, exact overlaps **87**, overlap_fraction **0.003997
     (~0.4 %)**, car base tick **0.04 s**, pos base tick **0.01 s**, median NN **0.067 s**, both
     median dt **0.24 s**. These reproduce the stored JSON exactly.
   - Note: I previously cited pos base tick **20 ms**; the script (and my GCD re-measurement)
     yield **10 ms** for Belgian Q. This is a *finer/more correct* GCD, not a discrepancy — pos
     tick legitimately varies 10–20 ms by session (implementer's table reflects this). Either
     way the streams are distinct-base-tick separate grids; the conclusion is unchanged.

**B1(c) CONCLUSION REVISED — RESOLVED.** The "no inter-stream clock to estimate / no
differential rate to exploit" claim is gone and explicitly **retracted** (result doc "Trust
limitations"). Replaced with: distinct, ~0.4 %-overlapping grids constitute genuine
inter-stream timing structure; characterizing how to exploit it is a G2 task. No GO/NO-GO call
is made.

## Scope drift
None. `git status`: one tracked change (`offline_loader.py`, docstring only) plus untracked
`scripts/characterize_telemetry_instruments.py` and `.agent-work/issue-447/**`. `git diff` on
`offline_loader.py` is +8/-2 docstring lines — the `(sampled ~240 Hz)` / `(sampled ~10 Hz)`
parentheticals removed and replaced with the two-separate-grids picture; no behavioral code
touched. Forbidden-pattern scan: NO `get_telemetry` call (only docstring mentions of what is
*not* used), no network/requests/urllib, no evo imports, no sqlite/DB writes, no
estimator/Kalman/filter/fusion deliverable, no GO/NO-GO. `savgol_filter` appears only as the
noise-measurement smoother (allowed; not a shipped estimator). Imports limited to
json/logging/math/os/sys/pathlib/typing + numpy/pandas/scipy + offline_loader.

## Evidence verdict
Present and reproducible offline. Four original measurements re-run and **unchanged & correct**:
car/pos ~4.2 Hz median (median_dt 0.2400 / 0.2402 s); X/Y/Z quant 1.0 dm = 0.1 m; Z verdict
PASS 30/30; noise covariances as reported. New grid-relationship numbers verified against my
independent measurement. simplification_limits on offline_loader: `PASS (1 files checked)`.
Test mode "evidence-only" is appropriate for a `scripts/` analysis tool.

## Code/doc quality
Clean, units labelled throughout (`unit_note` fields), decimetre handling correct. GCD base-tick
logic is sound (round to 10 ms to collapse FP jitter, then integer GCD). Narrative now matches
what the code measures — the over-reach that caused the attempt-1 BLOCK is gone.

## Map impact verdict
- **Evidence supports claimed change:** Yes — 4.2 Hz median, 0.1 m quant, Z PASS, noise
  variances, AND the now-measured separate-grids claim are all backed by reproducible numbers.
- **Constraints not violated:** Yes — `constraint:physics_region_no_evo_import` honored;
  offline-cache + raw-stream sanctioned exception honored (offline_loader only).
- **Notes match the diff:** Yes — Map Impact accurately describes a docstring-only `src/` edit
  plus an additive measurement; no overstatement remains.
- **Decision candidates surfaced:** No unauthorized GO/NO-GO; inter-stream timing structure
  correctly routed as a G2/triage candidate.
- **Durable context routed:** Yes — corrected empirical numbers and the timing-structure triage
  candidate are surfaced for Commander/Cartographer.

## Reconciliation check
The recorded empirical claim is now correct: both raw streams ~4.2 Hz *median* but two separate
irregular grids (car ~40 ms / pos ~10–20 ms base ticks, ~0.4 % overlap). Safe to propagate.

## Blockers
- None. B1 (a)(b)(c) all resolved; no new defect introduced.

## Out-of-scope observations
- **tc1 (triage, carried):** The distinct base ticks and ~0.4 %-overlapping irregular grids are
  real inter-stream timing structure — a phase-offset + rate-difference relationship worth
  characterizing for trajectory fusion in G2. The implementer has folded this into the result;
  Commander to route into the 0b GO/NO-GO brief.

## Workflow Feedback
- **Handoff gaps:** The original `offline_loader` docstring "~240 Hz / ~10 Hz" parenthetical
  (inherited into the handoff) seeded the attempt-1 error on both sides; it is now corrected.
  Confirmed fixed in this pass.
- **Context rediscovered:** None new this pass — the two-separate-grids structure is now
  documented in code/JSON, so a future reader will not have to rediscover it.
- **Instructions improvised around:** The reviewer survey template still has no dedicated
  "independent re-measurement" slot; I carried it inside r3-evidence as in attempt 1, per skill
  guidance to do the closest compliant thing and report the misfit. No material friction.
- **What would have made this easier:** Adopt the standing physics-region close-criterion the
  implementer and I both proposed: any "shared/identical/unified grid" claim must be backed by a
  measured timestamp-overlap fraction + per-stream base tick (GCD of unique dt quanta, not modal
  or minimum) + nearest-neighbour distance. One handoff-template line converts this error class
  into a mechanical required check.

## Return status
`complete`
