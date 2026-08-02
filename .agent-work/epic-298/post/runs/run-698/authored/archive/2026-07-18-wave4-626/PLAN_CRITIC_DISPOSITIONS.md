# Cold plan-critic dispositions — #626 gate plan

Cold critic (no authoring context) returned 6 findings on execute.json g1..g5. All ACCEPTED and folded
into the plan BEFORE freeze (plan not yet approved, so editing execute.json is authoring, not a mid-run
hand-edit). Sequencing was judged clean.

| ID | Lens | Sev | Finding (terse) | Disposition |
|---|---|---|---|---|
| F1 | testability | CRITICAL | Convergence metric rewards dispersion reduction — a degenerate over-shrinker (constant per car-season) wins even held-out by killing real development. LOO doesn't close it. | ACCEPT. g1 freezes a **signal-preservation guard**: the model's held-out car-signal is scored by **out-of-sample residual around the train-fit trajectory** (over-shrinking a developing car raises held-out residual), not by its own self-dispersion; PASS requires faster convergence AND preserved held-out accuracy. |
| F2 | testability | CRITICAL | Held-out model vs FULL-SAMPLE frozen floor is apples-to-oranges (sample-size confound). | ACCEPT. g5 **recomputes the raw x4 floor on the IDENTICAL held-out weekends**, paired per car-season. The 624 full-sample table is the g1 reproduction/sanity target, NOT the g5 comparison denominator. |
| F3 | testability | MAJOR | Gating statistic + noise margin under-specified until g5 (forking paths); "median ratio" vs "≥7/11" ambiguous; likely underpowered. | ACCEPT. g1 freezes: PASS rule = **≥7/11 axes where model beats the paired held-out raw floor by a margin outside noise** (median convergence ratio = reported summary, per launch order both are named); **bootstrap over car-seasons** as resampling unit; tie = not-a-beat; plus an **MDE/power sanity check** on the split. |
| F4 | intent-fit | MAJOR | No per-layer ablation → a dead layer rides on the others; "four-layer model beats floor" overclaims. | ACCEPT. g5 adds **held-out leave-one-layer-out ablation** (Δ convergence with/without each layer) so each layer's marginal contribution is reported and the honest-null of any single layer is visible. |
| F5 | rigor | MAJOR | Layer 2 non-identifiable + confounded with L3; the "season-time latent" fallback IS L3's axis (double-counts); grip_bin_obs is RACE-weighted vs Q model. | ACCEPT — sharpens DC1. g3: L2 must come from a genuinely **within-session** signal (grip_bin_obs grip-vs-track-laps, race/Q domain gap acknowledged); identifiability test includes an **orthogonality check vs the L3 trajectory**; if the only reachable signal is season-time, **declare L2 unidentifiable-at-granularity and FLOAT** — do NOT fill with a season-time latent. |
| F6 | intent-fit | MINOR/MAJOR | Mexico-vs-Monaco density check is confirmatory-by-construction (dividing ρ out guarantees "explained"); ignores aero/setup confound. | ACCEPT. g2: make it a **residual-consistency test with numeric tolerance** — after density removal the SAME car's drag/power residual at Mexico vs Monaco agrees within propagated σ — and acknowledge the setup/aero confound. |

Net: F1+F2+F3 change what the g1 frozen harness must contain (folded in before freeze); F4 adds a g5
deliverable; F5 strengthens g3's honest-null/float discipline; F6 hardens g2's density check.
