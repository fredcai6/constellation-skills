# Physics P1 — Ideal-lap sim as a trustworthy two-sided evaluator (#492)

Date: 2026-06-18
Status: approved in session (user-reviewed); pending written-spec ratification
Parent: `2026-06-17-physics-cross-session-pooling-design.md` (Epic 2 P1) · builds on P0 (#492, merged-locally branch `feat/p0-session-fit-store-492`)

## Decision

Make the ideal-lap sim a **trustworthy two-sided evaluator** of car capability:
it must neither **underestimate** acceleration in any direction nor produce
**aphysical runaways**. The ideal lap is a CEILING (a perfect-driver, max-grip
lap), not a regression-to-quali target. Exploration mode; this is the yardstick
the rest of Epic 2 is judged against, pointed at the P0 421-fit store.

## Plausibility philosophy (user-calibrated)

- The ideal lap should be **meaningfully faster than the human best — gut ~10%.**
  A **small gap (a couple of percent) is the SUSPICIOUS signal**: it means the
  sim is *underestimating* capability (not really a ceiling). Large gaps are
  expected and healthy.
- **Per-point Δv-vs-position is the primary signal**, not the single lap-time
  number: *where* on the track the sim is faster/slower than the real lap, and by
  how much, is what we read. (The aggregate lap-time gap is a summary; the
  Δv-vs-position trace is the diagnosis.)
- **Runaway is a separate, physics-implausibility check** (impossible speeds,
  uncapped corners, a braking/accel integral that blows up) — NOT inferred from a
  large gap.

## Sequencing

**B (runaway guard) → D (diagnostic) → A (DRS) + C (braking)**, A and C each
validated through D. The guard is first because the sim currently returns `inf` on
the ~29% of P0 fits that have no tyre ceiling, so the diagnostic can't run across
the store until corners are guaranteed finite.

## B — Per-car Gsat runaway guard

`PhysicsSimulator._compute_speed_caps` caps corner speed at `sqrt(ceiling/κ)` only
when a tyre ceiling exists; when `lateral.ceiling is None` **and** the aero term
makes `denom = κ − A2·ρ ≤ 0`, the cap is `inf` → unbounded corner speed. P0
evidence: **29% of fits have no ceiling**, so this is the live runaway mechanism.

Fix: a **finite fallback ceiling, per-car, with a hook.**
- Default per-car Gsat = the car's own measured peak lateral grip (from its `A0`
  / apex envelope) × a small headroom factor, **clamped by a per-era population
  max** lateral-g. (Confirmed: car-max with era clamp.)
- A hook lets a caller inject a per-car ceiling, so P2 can later feed the pooled
  per-car posterior. Generalized era clamp now, pooled per-car later.

## A — DRS-zone mask producer (all-seasons)

The sim already consumes a per-segment `drs_open` mask and applies the fitted
`theta_D_open`; nothing populates it, so DRS-open drag is dead weight and top
speed is understated. Build the producer:
- **Telemetry-pooled, not a curated zone file** — must be valid across ALL seasons
  with no per-season upkeep. For a session, pool the FastF1 `DRS` channel across
  flying laps and mark a track segment a DRS zone where DRS is open across many
  cars/laps → emit `drs_open(s)` aligned to the ribbon/track-profile distance.
- Self-adapts to each season's zones and to DRS-disabled (wet) sessions (no open
  samples → no zones). Threads onto the track profile the sim already reads.

## C — Braking-peak correction (time kernel; kernel choice is an experiment)

The braking frontier is binned from the **smoothed** `a_long` series, which
flattens the decel spike → biased-low peak (~3.9 g vs ~5 g real) and even a
wrong-sign slope. Fix:
- Model braking deceleration as a **time kernel**: decel as a function of
  time-since-brake-application, **peaking early then decaying**, applied **per
  braking event**, and **NOT curvature-dependent**.
- **The kernel shape is unknown — trying several candidate kernels is an explicit
  step** (e.g. exponential decay, gamma/log-normal-shaped, triangular,
  raised-cosine). The harness must make the kernel **pluggable** so we can try a
  few and compare.
- **Fit/evaluate by Δv at points along the braking event** (the observed
  point-wise speed evolution), choosing the kernel + amplitude that best
  reproduce it. **The total-Δv integral is a runaway guardrail only**, not the
  fitting objective.
- **Generalized kernel + amplitude this pass; per-driver amplitude tuning hooked
  but deferred** (drivers differ in brake-application style).
- The recovered braking model feeds the sim's `braking_grip_limit` / frontier so
  the evaluator stops under-calling decel. Per-car refinement still comes via P2.

## D — Two-sided diagnostic harness

Runs the ideal lap over the P0 fit store and reports, per car-session:
- **Δv-vs-position trace** (sim − real best lap, along the track) — the primary
  read; surfaces *where* the sim under/over-shoots (post-apex under-call,
  straight-line top-speed gap, corner over-speed).
- **Ideal-vs-best lap-time gap** as a summary, flagging **small gaps (≲ a few %)
  as under-call suspects** (against the ~10% expectation).
- **Top-speed vs telemetry max** (the DRS effect lever).
- **Runaway indicators:** fallback-ceiling-hit / corner-cap-hit rate, any
  impossible speeds, integral blow-ups.
- Reusable across the store (aggregate distributions) and per single car-session
  (the existing `plot_capability_diagnostics.py` lap-gap plot is the per-session
  visual; this generalises it to a batch readout).

## Hooks / seams (for P2 and later)

- Per-car Gsat ceiling injection (P2 pooled posterior).
- Per-driver braking-amplitude tuning (deferred).
- Both default to the generalized/era value when not supplied.

## Evidence inputs

The P0 store (`data/physics_fits.db`, 421 ok 2023 Q fits). The diagnostic's first
run over it establishes the baseline under/over distribution that ranks the
remaining fixes.

## Risks

- **Braking kernel may not be cleanly identifiable** from smoothed point-wise Δv
  (the smoother that flattened the peak also flattens the points). The experiment
  must check whether candidate kernels are distinguishable at all; if not, fall
  back to a single generalized kernel + amplitude and flag it. The integral
  runaway-guard still protects the sim regardless.
- **The ~10% plausible-gap heuristic is a prior, not a law** — the diagnostic
  reports the actual distribution; the threshold for "suspicious under-call" is
  tunable once we see real numbers.
- **DRS pooling threshold** (how many cars/laps make a segment a zone) needs a
  sane default; too low → spurious zones, too high → misses zones in sparse
  sessions. Validate against a couple of known circuits (Monza, Spa).
