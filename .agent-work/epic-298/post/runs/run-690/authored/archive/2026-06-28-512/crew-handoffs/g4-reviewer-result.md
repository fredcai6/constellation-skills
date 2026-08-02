# Review Result — g4-review (COMMANDER review in lieu of crew)

**Verdict: APPROVE**

## Context / misfit (for feedback)
The dispatched reviewer crew (`constellation/512/g4-review/reviewer/attempt-1`) returned an
**account session-limit** message (resets 12:10pm PT) and produced no review artifact. Subagents
are rate-limited; per user direction ("keep going") the commander performed this review in-context
(read the diff, ran the tests, verified the metric). Logged as a deviation to surface at the
feedback step — a crew review should re-run if/when capacity returns and this gate is reopened.

## Checks
- **Metric is vs the static estimate's OWN uncertainty (not circuit):** CONFIRMED.
  `_static_separability` (regime_readiness.py:485) computes per car `pool_random_effects(vals, sigs)`
  → `mu_c, sigma_mu_c`; across cars `separation_ratio = stdev({mu_c}) / median({sigma_mu_c})` and
  `sep_F = var(mu_c)/mean(sigma_mu_c²)`. This is the pooling-thesis test, distinct from `frac_team`.
- **Fixtures discriminate (not tautological):** 68 tests green; planted separable ≈31 vs
  non-separable (same-mu ≈0.40, huge-σ ≈0.78); developing-car detrends (tau_pre 0.60→tau_post 0.38).
- **Degenerate `braking/brake_aero_decel` 9.24σ:** NOT a real separation — it's an artifact of an
  **under-estimated per-session σ** (tiny `med_sigma_mu` denominator), coherent with that axis's
  zstd 1.93 over-claim. The code has no explicit degenerate-ratio guard; the interpretation is
  handled in the G3 verdict (discounted). Minor enhancement → triage (flag implausibly-small
  `med_sigma_mu` relative to value scale).
- **setup_conflated per-axis** (power False; drag/aero/lateral-aero/power-drag True): CONFIRMED
  (`_axis_setup_conflated`), correctly per-axis (straight_line mixes a clean power axis + conflated drag).
- **Backward compatible:** existing G1/G2 metrics, flags, tests unchanged (additive `static` field).
- **No evo import; tests data/-independent; no GO/NO-GO verdict in the core/dashboard.** CONFIRMED.
- `py -m pytest tests/unit/physics/layer2/test_regime_readiness.py tests/unit/physics/layer2/test_regime_capability_dashboard.py -q` → **68 passed**.

## Out-of-scope / triage
- Add an explicit degenerate-ratio guard (flag when `med_sigma_mu` is implausibly small vs the
  value scale) so the dashboard never surfaces a spurious high `separation_ratio` (the brake_aero case).
- The `separation_ratio_manageable=2.0` threshold is a reference, NOT a pass/fail gate — F1 margins
  are sub-2σ by nature (user direction). The verdict treats `separation_ratio` as a continuous
  "how much recoverable signal" measure. → rubric decision-anchor must say this.

## Workflow Feedback
Crew review was blocked by an account session limit; commander self-reviewed. The verification was
tractable in-context (metric is a few lines; tests are deterministic). If capacity is constrained,
small reasoning-heavy review gates can be commander-performed without much rigor loss — but it should
be an explicit, logged fallback, not the default.
