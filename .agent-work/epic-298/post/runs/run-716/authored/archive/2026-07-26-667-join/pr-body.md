## #667 — the join (epic #659 Wave 4a)

Composes the car-reference circuit fingerprint (#664) with the driver-utilization fingerprint (#666) into a per-weekend, **quali-side** utilization prior with honest Student-t σ, for **both channels** (utilization/time-deficit + energy), symmetric. **The linear join IS the prior** — no sequence/interaction escalation (that is #670).

### What's here
- **`src/physics/fingerprint/join.py`** — pure `join_weekend_prior(...)` + `WeekendUtilizationPrior`.
  - **Normalized weighted average** over the k severity classes: `w_i = comp_i / Σcomp`; `prior_mean = Σ w_i m_i` (unresolved cells fall back to the resolved-weighted mean μ_res). Composition is **not renormalized** — `corner_share = Σcomp` (≈0.42, NOT 1.0; straights + braking_zone excluded).
  - **Honest quadrature σ**: `sqrt(Σ_res w²σ² + (weight_on_thin·σ_unres)²)` where `σ_unres` can **exceed** resolved σ (an unknown class widens, never caps, the tail) and `n_eff` folds in the thin weight so the tail fattens; wrapped via the repo's `predictive_t` seam (Student-t, no baked-in normality).
  - **Thin exposure surfaced** via `thin_classes` / `weight_on_thin`; **fully-thin** (no resolved cell) returns `prior=None` loudly, never a fabricated value. Loud refusals on vocabulary-version / channel / class-order mismatch, missing composition key, corner_share≤0.
- **`scripts/join_bounded_validation_667.py`** + tests — a **season-capable** offline validation harness.
- **`tests/unit/physics/fingerprint/test_join.py`** (18 tests) + `test_join_bounded_validation.py`.

### The 4 T7 gating invariants (the correctness gate) — each PASS
A mechanically-broken join can beat a driver-overall baseline through compensating errors, so these reduces-to-simple-case invariants — not an outcome win — prove correctness:
1. Uniform composition ⇒ exactly the driver-overall (unweighted k-cell) mean. **PASS**
2. Identical cells ⇒ that constant for any composition. **PASS**
3. Single-class circuit ⇒ σ collapses to that cell's σ. **PASS**
4. Soft memberships unchanged; corner_share = Σ shares ≠ 1.0. **PASS**

Plus **T7-5** (non-degenerate general case: distinct shares × distinct means, hand-computed Σw·m, discriminates ÷k and renormalize-to-1.0 bugs), numeric σ thin-widening, σ monotonicity, both-channels symmetry, and 6 loud-refusal cases. **18/18** on the pinned 3.14 interpreter.

### Honest σ on the real bounded slice (Great Britain 2023-Q) — validation gate is **Admiral-ruled option A** (GB-real + synthetic)
Validated offline on the only #664/#666 slice on disk (Great Britain). Three strictly-pre cutoffs span the honest range (fit reads only `round_idx <= as_of_round`; GB's sole observation is round 10 — no cell past the cutoff read):

- **as_of_round=12** (all-resolved): 8 priors, `corner_share=0.4217` (the corner share, not 1.0), utilization means 2.69–2.92 / scale 1.368, energy ~0.20 / scale 0.090, nu=4.0; the thin **c1** cell (support ~3.56 vs c0 ~212) is thin-but-resolved.
- **as_of_round=22** (c1 UNRESOLVED — the strongest honest-σ demonstration): as GB's round-10 observation ages past the recency half-life, c1's weighted support decays below the 1.0 floor while c0 stays resolved. All 8 priors surface **c1 in `thin_classes`, `weight_on_thin=0.0079`, on BOTH channels identically (symmetric)**, and the **fat σ_unres widens the prior**: utilization scale 1.368 → **1.524** (+11.4%), energy 0.090 → **0.097** (+7.8%). The unresolved class widens, never caps, the prior.
- **as_of_round=9** (fully-thin, before GB's round 10): all 8 priors `prior=None`, `weight_on_thin=1.0` — the loud honest absence.

### Scope boundary → #670 (explicit, not silent)
Per **Admiral ruling A**, path B (regenerating Monaco/Spain/Belgium) is declined — it is Admiral-owned long-compute, **duplicates #670's season-scale regen, and exercises no new code path**. The **3-circuit (Monaco/Spain/Belgium) breadth — including the multi-circuit early-cutoff case where c1 is unresolved because a different circuit supplies c0/c2/c3 support — is routed to #670** (season-scale diagnostic, out of #667 scope). The join + harness are season-ready for those circuits the moment their rows exist.

### Notes
- **NO merge without the Admiral** (independent world-verify + gating re-run on pinned 3.14 precede any squash).
- 3 triage candidates deferred to the Admiral (#670 join-vs-driver-overall baseline consistency; correlation-aware σ upgrade; fingerprint fit-cutoff stamp). Map fence respected (impact recorded as prose + staged `667-cartography/` for the epic closeout reconcile).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AxSxn4GGTrbVwWaR52Hm8R
