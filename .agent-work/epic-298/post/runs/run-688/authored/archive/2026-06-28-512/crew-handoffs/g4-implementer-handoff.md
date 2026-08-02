# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g4-implement` — Static-latent separability at manageable uncertainty (issue #512, C3)

## Why this gate exists (context — read it)
G1's `frac_team` (two-way car-vs-circuit split) found the raw per-session parameter is
**circuit-dominated**. But that's the *expected* fingerprint of cars set up per-track, and it
under-tests the real thesis: **pool many track-viewpoints to recover a STABLE static car latent**
(e.g. a "pretty stable PU power capability"; a base drag platform that gets modified per track).
The success bar is **manageable uncertainty, NOT full recovery** — we accept we won't recover
everything; we want to know which components pin down a static car estimate well enough to tell
cars apart.

## Task
Extend `src/physics/layer2/regime_readiness.py` with a **static-latent separability** readout:
for each component axis, recover each car's static estimate by pooling its sessions, then measure
car separability **relative to that static estimate's own uncertainty** (NOT vs circuit variance —
that's the existing, distinct `frac_team`).

## Method (compose existing seams)
For each component axis, for each constructor with valid rows:
- **Static estimate:** `pool_random_effects(vals_c, sigs_c)` → `mu_c` (pooled static value),
  `sigma_mu_c` (uncertainty OF the pooled mean), `tau_c`, `n_c`. **Development separation:** also
  `fit_drift(vals_c, clock=round_idx, sigs_c)`; report `tau_c` before vs after detrend so a car
  that's developing isn't counted as noisy. The headline static estimate is `mu_c ± sigma_mu_c`
  from the RE pool (sigma_mu_c shrinks ~`tau_c/sqrt(n_c)` — this is the "manageable uncertainty"
  quantity: huge per-track setup spread (tau) can still pool to a usable mean).
- **Separability vs own uncertainty:** across cars,
  `separation_ratio = stdev({mu_c}) / median({sigma_mu_c})` (how many static-σ apart cars
  typically are) and `sep_F = var({mu_c}) / mean({sigma_mu_c**2})` (ANOVA-style).
- **`manageable` flag:** `separation_ratio >= thresholds.separation_ratio_manageable`
  (add to `DEFAULT_THRESHOLDS`, default **2.0** — cars ~2σ apart on the static estimate).
- **Return per-car `(mu_c, sigma_mu_c, n_c)`** so the ordering is inspectable (e.g. is RBR top on
  static power?).

Contrast to be explicit about in a docstring: `frac_team` compares the car main-effect to
**circuit** variance (setup-per-track swamps it); `static_separability` compares per-car **static
estimates to their own estimation uncertainty** (pooling beats down the per-track spread). They
answer different questions.

## Return shape
- Extend `DEFAULT_THRESHOLDS`/`ReadinessThresholds` with `separation_ratio_manageable=2.0`.
- A `@dataclass StaticSeparability`: axis name, `car_spread` (stdev of mu_c), `med_sigma_mu`,
  `separation_ratio`, `sep_F`, `manageable: bool`, `per_car: dict[str, tuple[float,float,int]]`
  (ctor → mu_c, sigma_mu_c, n_c), `tau_pre`/`tau_post` (median across cars, dev-detrend effect).
- Attach to `AxisReadiness` as a `static: StaticSeparability | None` field (None when n<2 cars),
  OR a parallel `compute_static_separability(df, *, thresholds) -> dict[str, ...]`. Implementer's
  call; keep `compute_readiness` backward-compatible (existing fields unchanged).
- **No GO/NO-GO verdict** (that's the revised G3).

## Physical caveat to encode (do not paper over)
The pooled static mean is physically clean for **power** (you don't retune peak PU power per
track → `mu_c` ≈ static PU capability). For **drag/aero** the pooled mean **conflates per-track
setup** (skinny-wing Monza vs max-downforce Monaco) → `mu_c` is "mean across the season's
setups", not a clean base platform. Carry a per-component boolean/flag `static_mean_setup_conflated`
(True for drag/aero & the lateral-aero axis; False for power; document the reasoning) so the
verdict and dashboard don't over-read a drag separation number.

## Allowed Scope
`src/physics/layer2/regime_readiness.py` (extend), `tests/unit/physics/layer2/test_regime_readiness.py`
(extend), and the dashboard `scripts/regime_capability_dashboard.py` + its test
(`test_regime_capability_dashboard.py`) to RENDER a new "Static-latent separability" section
(per-component separation_ratio + manageable + a per-car `mu_c ± sigma_mu_c` table; optionally a
caterpillar plot to `reports/physics/regime_capability_static_*.png`, gitignored). Render the new
section from the core (single source of truth), and re-run over the real store.

## Specific Exclusions
- Don't modify `pooling.py`/`estimate_store.py`. No evo import. No grip-state (#511)/traction-rebuild (#557).
- No verdict assignment. Keep the existing G1/G2 metrics & flags unchanged (additive — backward compatible).

## Constraints
- `constraint:physics_region_no_evo_import`; honest covariance first-class.
- Tests independent of `data/` (synthetic fixtures); real run reads the absolute main-checkout DB
  `C:/Programs/f1Brainz/data/physics_estimates_g3wired.db` (`status=None`).
- Single canonical path.

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/regime_readiness.py` (extend); `pooling.pool_random_effects`/`fit_drift`; dashboard.
- **Capability:** static-latent recovery test (distinct from additive frac_team) — the pooling-thesis readiness.
- **Constraints:** `constraint:physics_region_no_evo_import`; manageable-uncertainty bar.
- **Decision pressure:** `separation_ratio_manageable` threshold → reconcile candidate.
- **Evidence:** pooling thesis — power expected separable-at-manageable-uncertainty; drag setup-conflated.

## Required Evidence
`py -m pytest tests/unit/physics/layer2/test_regime_readiness.py tests/unit/physics/layer2/test_regime_capability_dashboard.py -q` green; synthetic fixtures recover planted separable vs non-separable static latents; the real-run static-separability section (per-component separation_ratio + per-car static power ordering) pasted into the result.

## Verification Commands
```bash
py -m pytest tests/unit/physics/layer2/test_regime_readiness.py tests/unit/physics/layer2/test_regime_capability_dashboard.py -q
py scripts/regime_capability_dashboard.py --db C:/Programs/f1Brainz/data/physics_estimates_g3wired.db
```

## Suggested Model Tier
`simple bounded` (Sonnet) — precise spec + seams; care on the dev-detrend and the setup-conflation flag.

## Authority
Method (RE-pool static estimate, separation_ratio vs own uncertainty, manageable threshold default
2.0, setup-conflation flag) is DECIDED (commander, user-ratified: manageable-uncertainty bar).
No verdict here. Naming/dataclass layout is the implementer's call.

## Stop Conditions
Stop if: a metric can't be computed from the seams, the real run errors, scope must be exceeded,
or a verdict decision is forced.

## Return Format
IMPLEMENTER_RESULT: completed slice, files changed, test mode, evidence (pytest + real-run static
section incl. per-car static-power ordering + separation_ratio per component), assumptions, stop
conditions, out-of-scope observations, workflow feedback.
