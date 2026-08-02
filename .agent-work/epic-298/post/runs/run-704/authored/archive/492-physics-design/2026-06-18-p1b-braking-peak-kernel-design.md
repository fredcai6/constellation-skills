# Physics P1b — Braking-peak recovery via a time kernel (#492)

> **SUPERSEDED (2026-06-18).** The kernel approach was implemented and validated
> on synthetic data, then superseded: the smoother rounds the *speed knee* too
> (not just `a_long`), so the kernel can't recover the peak from the smoothed
> trace. Braking capability is instead read from the **raw car-speed sensor**
> (high-quantile frontier ~5 g) as an exploration workaround, and the real fix
> is the **physics-aware filter rebuild (#496)**. The kernel code
> (`braking_kernel*.py` + tests) was removed; this doc is retained as history.

Date: 2026-06-18
Status: SUPERSEDED (see header) — was: approved direction (P1b design forks settled in session)
Parent: `2026-06-18-p1-sim-evaluator-design.md` (Epic 2 P1) · evaluated through P1a's diagnostic

## Decision

The braking frontier `a_brake(v) = a_b + b_b·v²` is fit from the **smoothed**
`a_long` series, which flattens the decel spike → measured peak ~3.9 g vs ~5 g
real, and single-session `b_b` even came out the wrong sign. P1a's sweep
confirmed the consequence: the ideal lap cannot out-brake the human. P1b
**recovers the true braking peak** by modelling braking deceleration as a
**time kernel** and fitting it to the signal the smoother *does* preserve.

## The key lever

The smoother flattens **acceleration** (the derivative) but preserves **speed**
(the integral). So fit the kernel to the **per-event speed trace**, not to
`a_long`: the speed drops between points constrain the kernel, and the kernel's
*derivative* recovers the sharp peak the direct `a_long` measurement lost. This
is why the objective is "Δv at points," and why the total-Δv integral is only a
guardrail (it equals v_start − v_end, which a runaway kernel would exceed).

## Design (settled with user)

- **Braking decel = a TIME kernel** `a(τ) = A · g(τ; θ)`, τ = time since brake
  application, **peak-early-then-decay**, applied **per braking event**, and
  **NOT curvature-dependent**.
- **The kernel shape is unknown → trying several candidates is an explicit
  experiment.** A pluggable kernel interface + a candidate set, e.g.:
  exponential decay, gamma / log-normal, triangular, raised-cosine, half-cosine.
  Each candidate exposes a normalised `g(τ)` (peaks early, ∫ over [0,1] = 1) and
  a small parameter set.
- **Fit objective = point-wise Δv** along each event: choose `A` (and θ) so the
  kernel-implied speed trace `v(τ) = v0 − ∫₀^τ A·g` best matches the OBSERVED
  speeds at the event's sample points (least squares on speed). The
  **total-Δv integral is a runaway guardrail only** (the fitted event Δv must
  not exceed the observed v0−v1 by more than a small tolerance).
- **Kernel selection:** the candidate with the best held-out point-wise speed
  fit, pooled across many braking events, wins as the generalized kernel.
- **Generalized kernel + amplitude this pass; per-driver amplitude hooked but
  deferred** (drivers differ in brake-application style).

## Braking events

A braking event = a contiguous run of `straight_brake`-regime
`KinematicSample`s within a lap (from `segment_classifier`), each carrying
`timestamp_ms` and `speed`. The reliable per-event anchors are `v0` (entry),
`v1` (exit), and duration `T`; the interior smoothed speeds constrain the shape.

## Feeding the sim (interface unchanged)

The sim consumes `a_brake(v)` via `envelope.braking_grip_limit(speed, curvature)`.
P1b maps the kernel-recovered decel back to **speed**: for each event, the kernel
gives `a(τ)` and the event gives `v(τ)`, yielding recovered (un-flattened)
`(v, a_brake)` points across the event's speed range. Pool these across events and
**refit the frontier `a_brake(v) = a_b + b_b·v²` on the recovered peaks** (a_b ≥ 0,
b_b free) — so the sim interface and `BrakingParameters` are unchanged; only the
input peaks are de-biased. (b_b should now come out ≥ 0: more decel at high speed
from downforce — the "peak early" shape.)

## Evaluation (through P1a's diagnostic)

Re-run the sim evaluator with the corrected braking model and read the
**braking-zone Δv** (now progress-registered, P1a fix e55ebd0): does the sim stop
under-calling decel into the corners (Δv ≥ 0 through braking zones), and does the
recovered peak land near ~5 g? Compare candidate kernels on this. The lap-time
gap is secondary (the median-ribbon line is not a true ceiling — accepted, (ii)
skipped).

## Scope / non-goals

- Generalized kernel only; per-driver tuning deferred (hook).
- Does NOT fix the ribbon-optimal-line ceiling question (out of scope, accepted).
- Per-car braking still ultimately comes from P2's pool; P1b de-biases the
  measurement so both the sim and the pool see a realistic peak.

## Risks

- **Kernel identifiability:** if candidate kernels are indistinguishable on the
  smoothed speed traces, fall back to the single best-fitting generalized kernel
  and flag low discriminability — the de-biasing (recovered peak) still helps
  even if the exact shape is uncertain.
- **#495 fit fragility** (~4% of sessions error on stream overlap) shrinks the
  event pool; pool across many sessions to compensate.
- **Event boundary noise:** brake on/off detection at event edges affects `T`;
  use the reliable v0/v1 anchors and the interior fit, not the noisy edges.
