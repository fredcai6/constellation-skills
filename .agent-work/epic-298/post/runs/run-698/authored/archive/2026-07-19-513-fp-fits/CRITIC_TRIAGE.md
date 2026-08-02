# Cold plan-critic triage (Ship I as delegated principal) — ALL 12 accepted

| # | Sev | Disposition |
|---|-----|-------------|
| F1 | BLOCKING | ACCEPT. Secondary longitudinal is circular via run_purpose↔lap-time↔p/w (up-weighting low-fuel push laps preferentially selects low-fp_mass-error laps → fakes a beat). FIX: secondary verdict reported at MATCHED fuel-uncertainty stratum; learned must beat clock at matched σ, else labeled "confounded, not evidential." → G1 protocol + G7 audit. |
| F2 | BLOCKING | ACCEPT + strengthens explicit-unknown (OWNER HARD REQ). FP per-run STARTING fuel (intercept) is unobservable; burn model gives slope only. FIX: `fp_mass` returns a DISTRIBUTION (value + explicit per-run intercept σ, dominant), NOT a scalar; propagate intercept σ into longitudinal p/w σ. Longitudinal gate meaningful only if that σ is bounded, else structurally null. → G2 + G1. |
| F3 | BLOCKING | ACCEPT. Track-evolution ≈ monotone bijection with session identity → a weighting collapsing to a monotone fn of track-evolution smuggles "later session=better" while passing. FIX: emergence test requires WITHIN-SESSION-orthogonal response — residualize track-evolution vs session identity AND/OR verify within-session reweighting (lap-3 push vs lap-18 long-run) in the predicted direction. → G1 + G4 close. |
| F4 | BLOCKING | ACCEPT — the key methodological fix. On GRIP, clock∥rubber-in genuinely→Q, so clock is a STRONG baseline and the primary is biased toward honest-null for STRUCTURAL reasons; the only channel where representativeness truly diverges from clock (longitudinal) is the circular one (F1). Risk: "clean null + caveated beat" that certifies nothing. FIX: pre-register (G1) that the PRIMARY verdict is read on the DIVERGENT cases — early-session soft low-fuel push laps (FP1 quali-sims) where clock says low-weight but learned says high — NOT pooled where clock and learned coincide. This is the discriminating test. |
| F5 | SHOULD-FIX | ACCEPT. Reorder: cumulative_track_laps unlock BEFORE representativeness (representativeness consumes track-evolution). New order below. (Note: representativeness computes the rubber PROXY directly via `compute_cumulative_track_laps`; it does not require #626's latent WIRED — but the reorder shares the compute + de-risks.) |
| F6 | SHOULD-FIX | ACCEPT. FIX: G6 close asserts ALL normalizers (compound-softness scaling, burn/fuel calibration, any z-scoring) fit WITHIN-TRAIN-FOLD only; G4 audits weekend_state track-evolution consumes NO Q-session input. |
| F7 | SHOULD-FIX | ACCEPT. FIX: G1 pre-registers a PAIRED significance test (paired bootstrap on per-weekend metric deltas) with N (held-out weekend count) + pass threshold stated BEFORE numbers. |
| F8 | SHOULD-FIX | ACCEPT. FIX: sandbagging gate redefined as `learned_weight < clock_weight` on the pre-named weekend (clock is BLIND to sandbagging → weights it high; learned should weight low), direction frozen in G1, flagged single-weekend illustration not evidence. |
| F9 | SHOULD-FIX | ACCEPT (critical for reap discipline). FIX (a): G1/G7 state demo weekend-N + a PRE-MEASURED single-fit ETA before G7 opens. FIX (b): G3 unlock column population scoped to DEMO weekends only (self-heal NULL elsewhere; full backfill deferred to #646). |
| F10 | SHOULD-FIX | ACCEPT (verify). PowerDragView CdA consumes mass_kg (throttle-on descent) — so grip-pinning lateral does NOT remove fp_mass from the longitudinal CdA/p-w chain; fp_mass enters BOTH. FIX: G7 non-circularity audit documents the fp_mass dependence explicitly and propagates its σ; reinforces longitudinal=SECONDARY/caveated. |
| F11 | CONSIDER | ACCEPT w/ framing. Gate tests car-capability (grip/p-w), but FP's load-bearing product feeds #628 driver-utility. FIX: G1 states car-capability representativeness is the TRACTABLE FALSIFIABLE PROXY for "does observation-property weighting work at all"; the transfer argument (same properties — low-fuel/push/soft/rubbered — that make a lap Q-representative for capability also make it the cleanest driver-utility demonstrator) is made explicit; a driver-utility-side held-out check is a named follow-on if primary passes. Surfaced to Admiral. |
| F12 | CONSIDER | ACCEPT. FIX: G1 states the honest-null #628 SHIP CONTRACT — FP fits still land (unbiased mass), but under learned≤clock the FP product ships the BEST-PERFORMING arm (clock-distance weighting), not the learned one; the representativeness-weighting CLAIM is null while the FP-fit capability still ships. |

## Revised gate order (F5)
G1 (reasoning) freeze enriched protocol → G2 (crew) fp_mass distribution + fp_lap_latent → G3 (crew)
cumulative_track_laps unlock (+ shared compute helper, demo-scoped populate) → G4 (crew) representativeness
weighting → G5 (crew) estimate_session FP wiring + explicit-unknown + #560 → G6 (crew) held-out gate harness
(both channels, divergent-case reading, paired significance) → G7 (reasoning) execute bounded compute + verdict
+ non-circularity/leakage audits + #646/parc-fermé dispositions.

## Net methodological shift
The falsifiable test's DISCRIMINATING POWER lives in the observations where learned and clock DISAGREE
(early-session soft low-fuel push laps vs late-session hard high-fuel long-runs). Primary verdict is read there.
Longitudinal is honestly caveated (fp_mass intercept σ propagated; matched-σ or confounded-label). fp_mass is a
distribution, not a scalar. This is a materially stronger, more honest gate than the pre-critic plan.
