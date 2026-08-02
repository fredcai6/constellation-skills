# Wave 6 — Lab experiments E1/E2/E3 (user-approved 2026-06-12)

Context: post step-back redefinition discussion. Lab mode — no GitHub issues/PRs; results return
to the conversation. Common rules for all three: plane frame ONLY (no ribbon in any analysis —
ribbon is demoted to post-estimation analysis; the loaders on this branch are fine, the
projection machinery is off-limits); raw streams `session.car_data`/`session.pos_data` via
`fastf1.Cache.enable_cache('C:/Programs/f1Brainz/outputs/cache')`, never `get_telemetry()`;
pos X/Y are DECIMETRES (×0.1 → m); Speed is km/h (÷3.6 → m/s); sector/lap truth
`C:/Programs/f1Brainz/data/f1_data_<year>.db` `lap_times`; `py` never `python`; honest null =
complete deliverable; checkpoint intermediate results to disk as JSON; commit + push per
milestone; no estimator construction beyond the experiment's explicit scope.

Suggested sessions (deep cache, familiar from prior waves): 2023 Belgian GP Q and R,
2022 Spanish GP R, 2024 British GP Q; ≥3 drivers each where feasible.

## E1 — Structure of the cross-instrument divergence (worktree expt-e1, branch expt/448-e1)

Question: the per-lap integrated-speed vs position-path disagreement (~36 m/lap std) — what is
its STRUCTURE? Method: per driver/session, build cumulative path functions P_pos(t) (chord sums
over raw XY) and P_spd(t) (integrated speed) on native timestamps; compare via interpolation of
the CUMULATIVE functions (monotone, smooth — never interpolate derivatives). Compute the
structure function D(τ) = stats of [ΔP_pos − ΔP_spd] over interval length τ ∈ [1 s … minutes],
log-log slope per regime; plus spatial attribution: disagreement accumulation binned by local
curvature (from raw XY finite differences, smoothed) — corners vs straights. Signatures: white
noise → τ^0.5; clock offset → τ^1; scale error → linear in distance; batch effects → jumps;
quantization/jitter at corners → curvature-correlated. Deliverable: evidence JSON + plots +
one-page verdict: the empirical error budget shape and whether the wall looks reducible.

## E2 — Time-alignment horizon (worktree expt-e2, branch expt/448-e2)

Question: how much of the disagreement does a single per-window time shift remove, vs window
length — and over what horizon is the offset stable? Method: window lengths L ∈ {1, 2, 5, 10,
20, 30, 60, 120 s, full stint}; per window fit one inter-stream time shift (e.g. minimize
post-shift cumulative-path residual); report post-alignment residual RMS vs L (the reliability
horizon = where improvement saturates), and the offset time series offset(t): drift,
autocorrelation, stability per session. Deliverable: evidence JSON + plots + one-page verdict:
is time misalignment the dominant corrupter (and to what fraction), and the measured "window of
reliable information".

## E4 — Minimal joint fusion test (worktree expt-e4, branch expt/448-e4) [wave 7, user-approved 2026-06-12]

Question: can the two instruments be unified in ONE local joint solve with honest uncertainty —
and what does the fused path's honest accuracy project to at sector distance? Built on measured
ground: E1 (fusion mandatory; divergence = position-jitter random walk + reducible chord-arc
geometry), E2 (inter-stream offset = ONE global constant ≈ +0.09 s + white jitter; best windows
10-30 s; NO per-lap/drifting clock states), E3 (substrates: position Matérn 5/2-class, speed
Matérn 3/2; speed sensor noise genuinely white σ≈0.49 m/s speed-independent; position apparent
σ 1.2-2.0 m is mostly UNPREDICTED MOTION between ~4 Hz samples — true sensor σ unknown and
finally identifiable inside a joint solve; 0.1 m quantization negligible).

Method: windows of 10-30 s, plane frame. Latent 2D trajectory with Matérn-5/2-class smoothness;
speed profile Matérn-3/2-class. Observations at native timestamps: position samples with sensor
σ as an ESTIMATED hyperparameter (deliverable in itself); speed samples |v| with σ = 0.49 m/s;
one constant inter-stream time offset (init +0.09 s) — estimated once per session at most, NEVER
per window/lap. Implementation freedom: GP regression / batch MAP over spline states /
state-space Matérn equivalent — pick what is robust with numpy/scipy only; no new deps.

Honesty checks, ALL on withheld data: (a) per-observation-class held-out chi^2 ≈ 1
simultaneously for both classes; (b) overlap consistency between adjacent windows (window N vs
N−1 and N+1 on their shared support) within reported covariance; (c) the decisive readout —
fused along-track path vs each single-instrument path (predictive error on withheld samples),
and the fused path's HONEST uncertainty integrated over a sector's distance (~2.3 km): the
projected sector-crossing time uncertainty at race speed. Report that number prominently — it
answers the 50 ms question from below.

Kill criteria (report, do not patch around): joint solve cannot whiten both classes
simultaneously; or overlap disagreement exceeds reported covariance. Either → the noise model is
wrong; return with the evidence, do not add machinery.

Sessions: 2-3 from {2023 Belgian Q, 2022 Spanish R, 2024 British Q}, ≥2 drivers, ≥20 windows
total incl. corners and straights. Prior evidence (absolute paths): E1
`C:/Programs/f1Brainz-worktrees/expt-e1/.agent-work/expt-e1/evidence/`, E2
`C:/Programs/f1Brainz-worktrees/expt-e2/.agent-work/expt-e2/evidence/`, E3
`C:/Programs/f1Brainz-worktrees/expt-e3/.agent-work/expt-e3/evidence/` (e3_verdict.json,
e3_noise_floor.json are the operative inputs).

## E5 — Sector-loop line calibration observability (worktree expt-e5, branch expt/448-e5) [wave 8, user-approved 2026-06-12]

Question: are the sector timing-loop LINES identifiable in our coordinates from the data — and
once calibrated, what sector-time residual floor remains? Built on E4 (branch parent): honest
fused windows, local crossing-time σ ≈ 16-41 ms. Sector times enter as line-crossing
observations: official sector boundary time = the instant the car crosses a fixed (unknown)
line on the ground. Method: reuse `scripts/experiments/e4_lib.py` (fused window solver). For
each sector boundary (s1/s2, s2/s3, s3/s1=start-finish) on 1-2 circuits: from DB sector times
(`lap_times` sector1/2/3 — note they are durations; convert to crossing timestamps via lap
start), take many (driver, lap) fused local solutions around the nominal crossing; co-estimate
the line (point + orientation in XY) that best explains all crossings; readouts: (a)
cross-driver/cross-subset CONVERGENCE of the line estimate (split-half agreement, an
observability test — speed diversity at the loop should separate geometry from any time bias);
(b) post-calibration crossing-time residual scatter per loop (the empirical sector floor, to
compare against E4's 16-41 ms local projection); (c) any residual per-loop constant time bias
(estimable jointly? degenerate?). Held-out validation: calibrate on a subset of drivers, score
crossing residuals on the others. Kill/branch: lines don't converge → sector times stay coarse
consistency checks (report why: observability vs data). Honest null welcome.

## E6 — Continuous stint chaining + calibration-free lap-time scoring (worktree expt-e6, branch expt/448-e6) [wave 8, user-approved 2026-06-12]

Question: does the integrated solution stay honest at stint scale, and does it reproduce
OFFICIAL lap times withheld from the solve? Built on E4 (branch parent). Method: chain E4
windows continuously over full stints (overlap-stitched, NO lap structure anywhere in the
solve); per-class held-out chi² and overlap-z across the whole chain (does honesty degrade with
chain length?). Lap-time scoring WITHOUT loop calibration (keeps E6 independent of E5): a lap
time equals the interval between successive crossings of ANY fixed line on the circuit — pick
arbitrary reference lines from the data (several, spread around the track), measure successive
fused-trajectory crossing intervals, compare to official lap times from the DB (`lap_times`),
which are NEVER given to the solve. Readouts: (a) lap-interval residual distribution vs
official lap times (median/p90, per reference-line and pooled — the integrated 50 ms question);
(b) consistency of residuals ACROSS reference lines (a trajectory-shape error shows as
line-dependent residuals; a pure timing error is line-invariant); (c) chain-length honesty
profile. Kill/branch: residuals ≫ E4's local projection → the chaining accumulates error the
local covariance doesn't admit; report the accumulation structure. Honest null welcome.

## E7 — Corner-aware (state-dependent) roughness (worktree expt-e7, branch expt/448-e7) [wave 9, user-approved 2026-06-13]

Question: does state-dependent process roughness eliminate the corner chord-cutting bias —
collapsing corner lap-residuals toward the straights' −16 ms — while keeping every honesty
check at chi² ≈ 1? Built on E6 (branch parent: contains E4 solver `e4_lib.py` AND E6 chain +
scoring harness `e6_*.py`).

Diagnosis being treated (E6): fused path cuts corner arcs — stationary per-corner bias −200..
−270 ms, line-dependent, repeated every lap, invisible to honest covariance. Mechanism
hypothesis: single stationary σ_a over mixed windows underfits corner dynamics; smoothness
prior shaves apexes within the ~1 m position budget.

Method: make the process roughness STATE-DEPENDENT and CONTINUOUS (the user's categorical-
acceleration formulation — explicitly NO discrete turn/straight/braking buckets): σ_a modulated
by local curvature and/or speed, e.g. σ_a(t) = σ0 · f(|κ(t)|·v(t)² ...) with f a smooth
low-parameter form whose parameters are selected by the SAME chi²-target honesty criterion as
E4 (never plain likelihood). κ comes from the current path estimate → mild circularity: iterate
(fit → curvature → refit), report convergence behavior, guard divergence (cap iterations,
report if oscillating). Implementation freedom within numpy/scipy; keep E4's observation models
(speed σ=0.49 m/s; position σ estimated; one constant offset) unchanged.

Scoring: E6's harness UNCHANGED — same stints (2022 Spain R VER/HAM, 2023 Belgium Q VER), same
reference lines, same withheld official lap times. Readouts: (a) corner-band lap residuals
before/after (target: collapse toward straights' −16 ms); (b) per-line residual spread
(line-invariance restored?); (c) ALL honesty checks unchanged and passing (per-class held-out
chi², overlap-z, profiled over the chain); (d) straights must NOT regress; (e) the fitted
roughness law itself (parameters, curvature dependence) — it is a deliverable (physical
plausibility: friction-ellipse-like?). Kill/branch: if state-dependent σ_a cannot remove the
bias without breaking honesty, the chord-cutting lives elsewhere (e.g. interpolation of the
latent mean between knots, window stitching in corners) — report the discriminating evidence.
Honest null welcome.

## E8 — Mean-compensated acceleration (worktree expt-e8, branch expt/448-e8) [wave 10, user-approved 2026-06-13]

Question: is the corner chord-cut (E6: −200..−270 ms/lap corner bias; E7: mean-path arc ~1 m/km
short of speed-implied, corner-concentrated) explained by ZERO-MEAN-PRIOR SHRINKAGE of sustained
centripetal acceleration — and does an estimated slowly-varying acceleration mean remove it?

Hypothesis under test (user-provided alternative, not yet established): Matérn-5/2 in Cartesian
asserts zero-mean acceleration; a sustained corner is a long non-zero-mean interval; the
posterior shrinks it → under-curved path → coherent arc shortfall. (User's deeper conjecture —
uncertainty better captured in a non-orthogonal inertial frame, equinoctial-style — is PARKED;
this wave tests the simpler bias/mean form first.)

Method, strictly ordered:
1. MECHANISM CHECK FIRST (cheap, analytic): compute the predicted posterior shrinkage of a
   sustained centripetal acceleration under the E4 kernel + observed sampling/noise (synthetic
   circular-arc truth through the actual solver is acceptable as the "analytic" check). Compare
   predicted arc shortfall vs the measured ~0.9-1.1 m/km corner shortfall (E7 locus evidence).
   IF the predicted magnitude is far off (≫ or ≪), STOP and report — misdiagnosis, do not
   proceed to step 2.
2. Layered dynamics: a(t) = m_a(t) + rough(t); m_a = slowly-varying estimated mean (coarse
   spline or long-length-scale latent, per-axis), rough = Matérn-3/2-class residual;
   zero-mean asserted only about the residual. Observation models UNCHANGED (speed σ=0.49,
   position σ estimated, one constant offset); hyperparameters by the E4 chi²-target criterion.
3. Re-score with the E6 harness UNCHANGED (same stints, lines, withheld official lap times).
4. Integral arc-length-vs-speed comparison as a VALIDATION DIAGNOSTIC only (no constraint in
   the solve): if the prior is fixed, integrals should reconcile on their own. Report before/after.

Readouts: mechanism-check verdict (predicted vs measured shortfall); corner-band residuals
before/after (target: toward straights' −16 ms); per-line spread (line-invariance); full
honesty table (per-class held-out chi², overlap-z, chain profile) — must hold; straights must
not regress; integral reconciliation diagnostic; and the recovered m_a(t) profiles on 2-3
corners (plot magnitude + direction vs curvature demand |κ|v² — first look at the force layer,
Phase-2 preview). Kill/branch: mechanism check fails → report; layered mean removes shortfall
but breaks honesty → report the tradeoff, do not tune past it. Honest null welcome.

## E9 — State-space stitching (worktree expt-e9, branch expt/448-e9) [wave 11, user-approved 2026-06-13]

Question: does replacing the cosine-taper curve blend with proper state-space estimate fusion
on window overlaps remove the corner chord-cut — collapsing corner lap residuals toward the
straights' −16 ms with honesty intact?

Established facts driving this wave (E7+E8): per-window solves are unbiased (S_geo−S_spd ≈
−0.01 m/km on real corners); the −2.1..−4.2 m/km corner deficit appears ONLY after the
cosine-taper overlap blend; pointwise averaging of two laterally-disagreeing curves cuts
corners (curve-averaging bias). The estimator is honest; the post-hoc blend lives outside the
probability model.

Method: replace the blend with estimate-level combination. Two acceptable routes (pick one
primary on numerical-robustness grounds, note the other): (a) precision-weighted posterior
fusion on the overlap region — combine the two windows' Gaussian posteriors over shared
support using their covariances (information filter form), so the merge lives INSIDE the
probability model; (b) reformulate the chain as one fixed-lag smoother / single sequential
solve over the stint so no merge ever occurs. Either way: observation models and E4
hyperparameter selection UNCHANGED; no lap structure; guard the overlap-fusion against
double-counting shared observations (windows sharing raw samples are NOT independent
estimates — handle by splitting observations between windows on the overlap, or by
conditioning properly; state your treatment explicitly and verify on synthetic truth first:
a synthetic circular-arc chain test must show the stitched arc unbiased to well under
0.5 m/km BEFORE running real data).

Scoring: E6 harness UNCHANGED (same stints: 2022 Spain R VER st4 + HAM st3, 2023 Belgium Q
VER st1; same reference lines; same withheld official lap times). Readouts: (a) synthetic
chain-stitch bias check (gate); (b) corner-band lap residuals before/after (target: toward
−16 ms); (c) per-line residual spread — line-invariance restored?; (d) full honesty table
(per-class held-out chi², overlap-z replaced by the new merge's internal consistency metric —
define it; chain-length profile) — must hold; (e) straights must not regress; (f) S_geo−S_spd
on the stitched trajectory, corner bands, before/after (the E8 localization metric — should go
to ≈0). Kill/branch: synthetic gate fails → the fusion treatment is wrong, report; corner bands
don't collapse despite stitched S_geo−S_spd ≈ 0 → arc was not the whole story, report the
residual structure. Honest null welcome.

## E10 — Windowless full-stint SDE smoother (worktree expt-e10, branch expt/448-e10) [wave 12, user-AFK-authorized 2026-06-13]

Question: does a single windowless full-stint solve — Matérn-5/2 latent X,Y as a linear-Gaussian
SDE run as a Kalman-RTS smoother, speed coupled, one constant offset — eliminate the corner
chord-cut (corner lap residuals → straights' −16 ms) while preserving every honesty check, at
O(N)?

Established (E1-E9): per-window solves unbiased (S_geo−S_spd ≈ 0); the −2..−5 m/km corner deficit
is a SEAM-IN-CORNER windowing/stitching artifact (E8/E9); no merge math fixes it (E9 gate); a
single full-span solve is exactly unbiased (E9 T1: −0.002 m/km). E4's fused model IS a Matérn
GP = linear SDE with integrator states → exact O(N) Kalman-RTS equivalent exists.

Method: implement the E4 fused observation model (position samples σ estimated; speed |v| as the
nonlinear derivative-magnitude constraint coupling Ẋ,Ẏ — linearize/EKF-RTS or iterated/sigma-point
as needed; speed σ=0.49; one constant inter-stream offset) as a STATE-SPACE smoother over the WHOLE
stint with NO windows and NO stitching. Matérn-5/2 per axis = 3 integrator states/axis (pos,vel,acc)
driven by white jerk; standard state-space form. Hyperparameters (process σ, length-scale, position
σ) by E4's chi²-target criterion on withheld samples — same objective, fit at stint scale (a few
global params; this is NOT per-window tuning and NOT lap structure). Verify the smoother nests E4 on
a single short window (≡ within numerical tol) before scaling.

Gate then score: (1) synthetic circular-arc chain (corner-realistic) stitched bias must be <0.5
m/km — expected ≈0 since there are no seams; (2) E6 harness UNCHANGED (2022 Spain R VER st4 + HAM
st3, 2023 Belgium Q VER st1; same reference lines; withheld official lap times). Readouts: corner-band
lap residuals before(E6 cosine)/after; per-line spread (line-invariance restored?); full honesty
table — per-class held-out chi², plus a smoother-internal consistency check (innovation whiteness /
NIS over the chain), profiled vs stint length; straights must not regress; stitched S_geo−S_spd corner
band (→≈0 expected). Deliverables also: the recovered per-axis acceleration state (force-layer preview,
Phase 2) and timing/scaling numbers (confirm O(N)). Kill/branch: corner bands fail to collapse despite
S_geo−S_spd ≈ 0 → arc deficit wasn't the whole story, report residual structure; EKF linearization of
the speed constraint degrades honesty → report and propose iterated/UKF remedy. Honest null welcome.

## E11 — Non-stationary roughness inside the windowless smoother (worktree expt-e11, branch expt/448-e11) [wave 13, user-AFK-authorized 2026-06-13]

Question: does state-dependent process roughness — INSIDE the E10 windowless honest smoother, where
the geometric chord-cut artifact is gone — remove the corner SPEED-PROFILE underfit, collapsing
corner lap residuals toward straights' ~−16 ms while keeping χ²_pos≈1 AND driving χ²_spd from
1.33-1.49 down to ≈1?

Why now (vs E7's null): E7 tested state-dependent roughness on the WINDOWED/STITCHED solve, where
the −2..−5 m/km chord-cut artifact dominated and CONFOUNDED it, and χ²_spd was already ≈1 so the
honesty criterion saw no benefit (drove λ→0). E10 removed the windowing artifact (corner locus →
≈0) and EXPOSED a real, corner-localized speed-honesty deficit: corner speed-fit RMS 2.25×/1.25×
sensor noise, held-out χ²_spd inflated to 1.33-1.49. There is now a genuine honesty signal to chase.

Established substrate: E10's windowless Matérn-5/2 SDE Kalman-RTS smoother (`e10_lib.py`), nests E4,
O(N), honest, geometric chord-cut eliminated. The binding error is the stationary length-scale /
jerk process-noise: one global value fits straights below the sensor floor but cannot follow the
~2-4 s brake→apex→accelerate longitudinal transient → corner crossing times biased.

Method: make the jerk process-noise spectral density (equivalently the Matérn length-scale / acc
correlation time) STATE-DEPENDENT and CONTINUOUS inside the windowless smoother — low-parameter,
no discrete buckets. Candidate drivers for the roughness: lateral demand |κ|v², longitudinal-accel
demand |dv/dt|, or total |a| — the binding underfit is the SPEED (longitudinal) transient, so a
longitudinal or total-accel driver is a priori more apt than E7's pure-lateral |κ|v²; let the data
choose among 2-3 forms by the chi²-target criterion. κ/accel come from the current path estimate →
iterate (fit→roughness→refit), report convergence, guard divergence. Observation models UNCHANGED
(position σ estimated, speed σ=0.49, one constant offset). Honor the E10 pitfall: σ_f pinned to the
detrended-residual scale; cap acc-prior growth so no >1000 km/h spikes.

Gate then score: (1) verify nesting/limit — roughness-modulation OFF must reproduce E10 exactly; (2)
synthetic corner-arc chain still unbiased (<0.5 m/km — must not reintroduce a geometric artifact);
(3) E6 harness UNCHANGED (2022 Spain R VER st4 + HAM st3, 2023 Belgium Q VER st1; same reference
lines; withheld official lap times). Readouts (numbers): corner-band lap residuals E10→E11 (target
toward −16 ms); per-line spread (line-invariance restored?); χ²_pos AND χ²_spd held-out before/after
(target both →1, esp. χ²_spd 1.4→~1); NIS profile over the stint; straights must NOT regress;
corner S_geo−S_spd stays ≈0 (don't trade the geometric win back); the fitted roughness law +
physical-plausibility (friction/accel-demand shape?); recovered acc state (force preview). Kill/branch:
χ²_spd won't reach ≈1 without breaking χ²_pos or the geometry → the corner speed transient is at the
data's information limit (honest floor found — a legitimate end-of-ladder result); roughness helps
but residuals stay line-dependent → a non-roughness corner mechanism remains, report it. Honest null
welcome — if this is the data's floor, that is the answer the epic needs.

## E12 — Capstone: windowless smoother scored at calibrated real sector loops vs official times (worktree expt-e12, branch expt/448-e12) [wave 14, user-AFK-authorized 2026-06-13]

Question: does the validated windowless honest smoother (E10/E11), scored at E5-CO-ESTIMATED REAL
sector-loop geometry against OFFICIAL sector times on held-out drivers, PASS the original gate
(rounds 1-2 failed at 550-960 ms; original ambition ≤50 ms)? And does loop LOCATION explain the
gap between E5's 21-46 ms (real loops) and E6/E10/E11's −400 ms (arbitrary corner reference lines)?

Why this is the capstone: the whole ladder converged on a windowless Matérn-5/2 SDE Kalman-RTS
smoother that is per-sample honest (χ²_pos≈1), speed-honest (χ²_spd→1 where recoverable, E11),
and geometrically honest (S_geo−S_spd≈0, E10). E5 separately showed real co-estimated sector
loops give 21-46 ms held-out crossing residuals — but E5 used the E4 WINDOWED solver. E6/E10/E11
lap-scoring used ARBITRARY reference lines (calibration-free) and saw a −400 ms line-dependent
corner bias. This experiment scores the BEST trajectory at the REAL loops against REAL sector
times — the actual epic deliverable — and disambiguates trajectory-defect vs scoring-proxy.

Method: reuse E5's loop co-estimation (`expt-e5` `e5_lib.py` — sibling worktree
`C:/Programs/f1Brainz-worktrees/expt-e5/.agent-work/expt-e5/evidence/`) and E10/E11's windowless
smoother (`e10_lib.py`/`e11_lib.py` on this branch). Pipeline: full-stint windowless trajectories
(E10 stationary baseline AND E11 non-stationary, both) → at each official sector boundary, get the
trajectory's crossing time of the co-estimated loop line → residual vs official sector time.
Held-out: calibrate loop geometry on one driver subset, score the others. Sessions: 2022 Spain R
(VER+HAM), 2023 Belgium Q (VER) + add ≥1 more session if cheap. Readouts:
1. Held-out crossing-time residual per loop: median/p90 ms, E10 vs E11 trajectory, vs E5's E4-windowed
   numbers (does the windowless honest trajectory match or beat 21-46 ms?).
2. Residual vs loop LOCATION — classify each sector loop by local curvature/speed at its position;
   plot residual vs |κ|v². The disambiguator: straight-located loops ≈16-50 ms with corner-located
   worse → real corner trajectory error remains; ALL calibrated loops ≈20-50 ms → the −400 ms
   arbitrary-line bias was a scoring-proxy artifact and the trajectory layer PASSES.
3. Direct comparison on the SAME trajectory: crossing residual at a co-estimated real loop vs at a
   nearby arbitrary reference line — quantify how much of the −400 ms is line-registration, not
   trajectory.
4. The bottom-line gate number: pooled held-out sector-crossing residual median/p90 for the best
   (E11) trajectory at calibrated loops — the honest answer to "does the physics layer clear the
   sector gate," to compare against 50 ms and against rounds 1-2's 550-960 ms.

Kill/branch: if calibrated-loop residuals are ALSO hundreds of ms at corners → the corner error is a
real trajectory defect, not a proxy artifact; characterize it (shape vs timing) as the genuine
end-of-ladder floor. If they are tens of ms everywhere → the trajectory layer is validated end to
end and the lab is DONE. Either is a complete, decisive deliverable. Honest null welcome.

## E3 — Local dynamics substrate identification (worktree expt-e3, branch expt/448-e3)

Question: what process model does the data itself imply, per stream, in the plane frame —
identified, not assumed? Method: per-stream separate fits on windows (use ~10-30 s, refine per
E2 if available — don't block on it): candidate classes = polynomial splines (orders 3-5,
varying knot density), GP kernels (Matérn 3/2, 5/2, RBF), jerk-bounded polynomial; position
likelihood must be quantization-aware (exact 0.1 m grid). Selection by predictive likelihood on
WITHHELD samples + residual whiteness as an OUTCOME (autocorrelation/Ljung-Box on held-out
residuals), never an assumption. Deliverable: evidence JSON + plots + one-page verdict: chosen
substrate class + per-channel noise structure (the empirical process model for the future joint
solve).
