# G2 Spike — Shared Context (read with your mechanism file g2-mX.md)

You are an EXPLORATORY spike for the #496/#507 physics-aware filter rebuild. You prototype
ONE mechanism that recovers the real sharp braking knee / longitudinal transients the blind
Matérn position-smoothness prior currently rounds away, and you MEASURE it on the common G1
scoreboard. This is a throwaway prototype — code quality is secondary to an honest, reproducible
measurement and a clear finding.

## The defect you are attacking
The trajectory smoother under-reads real heavy braking and rings on short straights:
- **Bahrain 2023 Q VER (heavy stop):** raw sensor knee ≈ −52 m/s² (~5.3 g), Gaussian smoother
  ≈ −39.5 (~4 g), kind3 ≈ −39.4 — the smoother loses ~1.3 g of REAL decel.
- **Monaco 2023 Q VER (short straight):** Gaussian non-throttle ringing ≈ +13 m/s² vs a raw
  ceiling ≈ +5.6 — spurious positive accel where the car is NOT on throttle.
- **Belgium/Spa 2023 Q VER (control):** the existing kind3 anchor already works here
  (knee −37.4 vs raw −38.8) — you must NOT regress this.

## Your worktree
You are in your OWN git worktree off branch `feat/physics-aware-estimator-496`. The G1
scoreboard `src/physics/layer2/scoreboard.py` IS committed and present — import from it. You may
edit `src/` freely to prototype (add a module, subclass the smoother, etc.). Do NOT commit and do
NOT touch the main checkout's `src/` — your worktree is isolated. Python launcher is `py` (3.14).

## The scoreboard seam you measure against (verified, exact)
`from src.physics.layer2.scoreboard import CaseInputs, VariantScore, score_variant, run_case, run_scoreboard, BUILTIN_VARIANTS`

A **variant** is `VariantFn = Callable[[CaseInputs], np.ndarray]` returning `a_long` (signed
m/s², decel negative) aligned to `inp.t`. `CaseInputs` gives you (all numpy, same length, sorted by time):
- `inp.t` (s), `inp.x`, `inp.y` (m), `inp.v` (m/s speed), `inp.regime` (str array:
  `"straight_brake"`, `"straight_coast"`, `"straight_throttle"`, `"corner"`),
- `inp.a_long_raw` — the RAW-sensor longitudinal accel reference (the un-biased ground truth),
- `inp.make_smoother(nu_proc=None) -> StintSmoother` — a calibrated factory (HPs already fit),
- `inp.brake_mask`, `inp.non_throttle_mask` — derived, fixed (the scoreboard owns metrics/masks).

To get `a_long` from a fitted `StintSmoother sm`: `ax,ay = sm.acc_at(t); vx,vy = sm.vel_at(t);
a_long = (ax*vx+ay*vy)/max(hypot(vx,vy),1e-6)` (see `scoreboard._long_accel` — reuse it).

`StintSmoother.fit(t, x, y, tc, v, accel_obs=None)`; `.acc_at(t)->(ax,ay)`; `.vel_at(t)->(vx,vy)`.

## How to run your measurement
```python
from src.physics.layer2.scoreboard import run_scoreboard, BUILTIN_VARIANTS
CACHE = "C:/Programs/f1Brainz/data/telemetry"
CASES = [(2023, "Bahrain", "VER"), (2023, "Monaco", "VER"), (2023, "Belgium", "VER")]
variants = dict(BUILTIN_VARIANTS)        # gaussian + kind3 baselines for context
variants["mX"] = my_variant_fn           # YOUR mechanism
table = run_scoreboard(CASES, variants, cache=CACHE)
print(table.markdown_table())
import json; print(json.dumps(table.to_json(), indent=2))
```
Each `VariantScore` carries: `knee, ringing, raw_knee, raw_ring, knee_gap_vs_raw (=knee-raw_knee;
NEGATIVE-toward-zero is better, i.e. deeper knee), ringing_over_ceiling (=ringing-raw_ring; want
≤0), ringing_ok`.

## What "good" looks like (report against these — do NOT cherry-pick)
- **Bahrain:** deepen the braking knee toward the raw −52 (shrink `knee_gap_vs_raw`).
- **Monaco:** bring non-throttle ringing under the raw ceiling (`ringing_over_ceiling ≤ 0`).
- **Belgium:** do NOT regress the knee vs the kind3 baseline.
Report ALL three for your variant AND the two baselines. Report failure modes honestly — a
mechanism that helps Bahrain but wrecks Monaco is a finding, not a failure to hide.

## The binding invariant (decision:two_cycle_external_anchor_design)
The existing kind=3 anchor obeys: anchor is EXTERNAL & UN-BIASED (raw `a_long`, NEVER re-read
from a smoothed trajectory), plateau-only placement, two cycles only, Student-t jerk foundation.
If your mechanism changes the anchor SOURCE or PLACEMENT (e.g. anchors the onset transient, or
uses a model/denoised value instead of the raw sample), you are EXTENDING this invariant — say so
EXPLICITLY in your findings (what you changed, and why it stays external/un-biased or why the
extension is justified). Do not silently violate it.

## Smoother internals you may use (src/preprocessing/trajectory/smoother.py — read it)
- `StintSmoother` order=4 (Matérn-7/2): per-axis state [pos, vel, acc, jerk]; jerk is the top
  white-noise state. `nu_proc` = Student-t jerk PROCESS prior (heavy-tailed smoothness): a large
  jerk increment (brake slam) inflates the predict-step Q so the knee un-rounds (`_proc_weights`,
  `_predict_step`).
- `AccelObs(t, ex, ey, a, sigma)` (kind=3): a soft 1-row Kalman update pulling `a_long` toward
  value `a` (unit dir `(ex,ey)`) with noise `sigma`, at times `t`. Empty/None → no kind=3
  (byte-identical Gaussian). `_update_accel`, `_build_timeline`.
- `from src.physics.layer2.accel_obs import emit_accel_obs, FrontierSamples` —
  `emit_accel_obs(FrontierSamples(t,v,vx,vy,a_long,regime), anchor_regimes=(...), plateau_margin=3,
  sigma_floor=0.5) -> AccelObs`. The current plateau-only emitter.
- `NSStintSmoother(... nu_proc=...)` — subclass with STATE-DEPENDENT per-step jerk process variance
  via a roughness schedule `_r_at(t)` (built by `build_roughness(...)`). The seam for "let the
  prior breathe" approaches.

## Output (write to ABSOLUTE main-checkout paths — your worktree's .agent-work is not the main one)
1. **Result file:** `C:/Programs/f1Brainz/.agent-work/496-physics-aware-estimator/crew-handoffs/g2-mX-result.md`
   (replace mX with your mechanism id). Include: the mechanism in 2–3 sentences; the scoreboard
   table (your variant + gaussian + kind3, all 3 circuits, knee/ringing/gaps); honest failure
   modes; whether/how you extended the two-cycle invariant; a soundness self-assessment
   (is the gain real or an artifact?); reproducibility (exact command to re-run); and a one-line
   recommendation (PROMISING / MIXED / WEAK + why).
2. **Prototype code:** copy your key new/changed file(s) into
   `C:/Programs/f1Brainz/.agent-work/496-physics-aware-estimator/spikes/mX/` so the approach
   survives worktree cleanup (the winner gets productionized in G3).

## Stop conditions
Stop and write your result (even if partial) if: the scoreboard can't load the cache (report the
error), your mechanism needs a seam that doesn't exist, or you'd have to exceed the spike scope
(no need to productionize — a credible prototype + honest numbers is the deliverable).
