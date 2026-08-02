# Plan-alternatives (design-it-twice) — #638 gate plan

The load-bearing structural choice is the gate decomposition (the FIX mechanism itself is
deferred to G1's diagnosis by pre-ruling #3, so it is not what the alternatives compare).

## Candidate A — Diagnose-first 3-gate (CHOSEN)
Constraint: rigor / de-risk the load-bearing fix choice.
- G1 evidence-only diagnosis + decide-fix (reasoning gate, commander-driven).
- G2 implement the G1-selected fix + tests (crew gate).
- G3 real-data F12 rerun + rollup + docs (reasoning gate, commander foreground).
Strengths: matches pre-ruling #3 (characterize WHY before fixing); lesson
`diagnose-first-decide-fix` (confirmed 6x) — an inherited premise (here: "circuit-conditional
is the fix") can be wrong; the three plausible root causes (BIC-noise / support-floor churn /
genuine per-circuit structure) each imply a DIFFERENT fix, so committing before evidence risks
a wasted crew cycle. Green at every gate boundary. Real-data runs stay in commander foreground
(reap-safe, launch-order mandate).

## Candidate B — Fix-forward 2-gate (UNTAKEN ROAD)
Constraint: velocity / fewest gates. Skip a separate diagnosis; dispatch a crew straight to the
leading-hypothesis fix (circuit-conditional or subsample), then rerun.
Rejected: violates pre-ruling #3; the fix choice is load-bearing (cheap regularized selection
vs expensive circuit-conditional redesign) and picking wrong burns a crew cycle + a ~6-min
real-data run. The diagnosis is cheap (commander-run, subsampled) and removes exactly that risk.

## Candidate C — Diagnosis-as-crew (UNTAKEN ROAD)
Constraint: offload compute from commander context. Dispatch the diagnosis to an implementer crew.
Rejected: the decide-fix is a decision the commander must own and reconcile against the launch
order (no human); the diagnosis numbers must land in the deciding context; and a crew running
the slow real-data fits risks harness reaping. Reasoning gate driven by commander is cleaner.

## Convergence
Candidate A. Untaken roads B and C recorded above (bias-to-yes: alternatives genuinely run,
skip surfaced). No human to converge — reconciled against launch-order pre-ruling #3, which
independently mandates diagnose-first.

## Panel-vs-single (cold critic)
Single cold critic (not a 3-lens panel): the plan is a bounded single-issue fix within a frozen
launch order, not an epic-spawning or architecture-touching artifact. Surfaced here as the
scaling choice.
