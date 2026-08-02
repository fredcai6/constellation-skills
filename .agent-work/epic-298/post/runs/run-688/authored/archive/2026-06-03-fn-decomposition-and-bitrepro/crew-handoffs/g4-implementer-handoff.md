# Implementer Handoff

## Gate
g4 — Fix the unseeded training-loop dropout RNG (always-on; makes training reproducible)

## Task
Make latent-power training run-to-run REPRODUCIBLE (0.0 weight drift) by seeding the RNG that drives the
training-loop dropout. Always-on (one canonical path — a real bug fix). Add a reproducibility test + a light quality
sanity check. Correct the #356 determinism narrative.

## The bug (G3-verified, independently reviewed)
`src/latent_power/training.py` (~lines 95-98) seeds torch only inside `with torch.random.fork_rng():
torch.manual_seed(seed); module = module_cls(config)`. `fork_rng()` RESTORES global RNG state on exit → module
INIT is seeded, but the training loop runs in the module's default train mode and the `nn.Dropout(p=...)` layers
(`src/latent_power/network.py:37`, reused 3×) draw from the UNSEEDED process-global torch RNG. (`random.Random(seed)`
at ~line 98 governs only batch shuffle.) Result: ~3e-4 run-to-run weight drift. Seeding the global RNG before the
loop collapses drift to EXACTLY 0.0 (G3 proved this).

## The fix (you own exact placement; reviewer will check init is not re-perturbed)
Seed the torch RNG governing the training-loop dropout WITHOUT re-perturbing module init. Module init must keep
using its existing `fork_rng()`+`manual_seed(seed)` path unchanged. The natural fix: after the module is constructed
(outside/after the fork_rng block) and BEFORE the training loop, seed the global torch RNG (e.g.
`torch.manual_seed(seed)` or a documented derived seed) so dropout is deterministic. Document WHY in a comment.
Note: `nn.Dropout` has no per-call generator argument, so seeding the (process-global) torch RNG is the
established/standard pattern (the file already uses `torch.manual_seed` and `random.Random(seed)`); making the
currently-UNSEEDED global draw SEEDED is the fix — that resolves, not introduces, the "unseeded global state" concern.

## Close Criteria
- Training is run-to-run reproducible: two trainings with the same config/seed produce byte-identical weights
  (0.0 max-abs state_dict drift). Add a test named with `training_reproducibility` (so `pytest -k
  training_reproducibility` selects it). Keep it bounded (small config; you may reuse the #356 harness scale).
- Module init is NOT re-perturbed by the fix (the `fork_rng` init path is unchanged; only the training-loop RNG is seeded).
- LIGHT quality sanity check: dropout is still ACTIVE/stochastic across DIFFERENT seeds (two different seeds →
  different weights — proves regularization wasn't disabled), and the smoke-scale eval is not degraded vs pre-fix.
- The existing latent_power training tests stay green.
- Correct the #356 narrative: update `tests/integration/test_utilization_determinism.py` docstring/comments that call
  the drift "intrinsic FP nondeterminism" — it is a now-fixed seeding bug. OPTIONAL (recommended): tighten that
  test's `_WEIGHT_TOL` toward ~0 now that fixed-threads training is bit-stable, keeping it green.
- `py -m src.utils.simplification_limits --paths` clean on touched files.

## Allowed Scope
- `src/latent_power/training.py` (the fix)
- A new reproducibility/sanity test (tests/unit/latent_power/ or tests/integration/)
- `tests/integration/test_utilization_determinism.py` (docstring correction + optional tolerance tighten)

## Specific Exclusions
- Do NOT run/re-promote the full gold cycle or do the full Brier re-validation here — that is a SEPARATE filed
  follow-up (tc1). This gate ships the code fix + test + LIGHT sanity check only.
- Do NOT change `network.py` dropout rates or model architecture. Do NOT touch the decomposition work (G1/G2).
- Do NOT add an opt-in flag — the fix is always-on (one canonical path).

## Constraints
- Use `py`, not `python`.
- This is an evo/probability change (training output shifts to a seeded realization). Full Brier-vs-baseline is the
  deferred follow-up; in-gate evidence is the reproducibility test + the LIGHT non-degradation sanity check.
- Seeding fix must be deterministic + documented; no new mutable module-level state.
- Run `py -m src.utils.simplification_limits --paths` on touched files.

## Required Evidence
- The reproducibility test: RED before the fix (or demonstrate the pre-fix drift), GREEN after (0.0 drift).
- `py -m pytest -q -k training_reproducibility` → pass.
- The latent_power training test suite green (name the command you ran).
- The sanity check (different seeds → different weights; smoke-eval not degraded).
- `py -m src.utils.simplification_limits --paths <touched>` → clean.

## Verification Commands
```bash
py -m pytest -q -k training_reproducibility
py -m pytest tests/unit/latent_power/ -q
py -m src.utils.simplification_limits --paths src/latent_power/training.py
```

## Suggested Model Tier
stronger — reason: core training-loop RNG semantics; the init-vs-loop seeding boundary is subtle and a mistake either
fails to fix the drift or breaks module-init reproducibility / regularization.

## Authority
Decided (human-approved): always-on seeding fix (no opt-in flag); full gold re-validation deferred to a filed
follow-up; correct the #356 narrative. You own the exact seeding placement + test design.

## Stop Conditions
Stop and return if: the fix cannot achieve 0.0 drift without changing module-init reproducibility or disabling
dropout; the change degrades smoke-eval meaningfully (report it — don't hide it); scope must be exceeded.

## Return Format
Return IMPLEMENTER_RESULT: the fix (with exact placement + why init isn't re-perturbed), the reproducibility test
(0.0 drift), the sanity-check result, latent_power suite + --paths evidence, #356 docstring update, assumptions,
stop conditions hit, out-of-scope observations.
