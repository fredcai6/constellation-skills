# Reviewer Handoff

## Gate
g4 — Fix the unseeded training-loop dropout RNG (always-on; training reproducibility)

## What Was Implemented
A single `torch.manual_seed(seed)` added in `src/latent_power/training.py` after the unchanged `fork_rng()` init
block and before the training loop, making training run-to-run reproducible (drift 3.9e-3 → 0.0). New
`tests/unit/latent_power/test_training_reproducibility.py` (4 tests). Corrected the #356 determinism narrative and
tightened its `_WEIGHT_TOL` 1e-2 → 1e-6.

## How to Inspect the Diff
- `git status --porcelain` (expect: training.py, NEW test_training_reproducibility.py, test_utilization_determinism.py).
- `git diff -- src/latent_power/training.py tests/integration/test_utilization_determinism.py`
- Read the new test file; compare the training.py fix against `git show HEAD:src/latent_power/training.py`.
Implementer result: `.agent-work/fn-decomposition-and-bitrepro/crew-handoffs/g4-implementer-result.md`.

## Close Criteria (each a review check)
- **The fix is correct:** `torch.manual_seed(seed)` is placed AFTER the `fork_rng()` module-init block and BEFORE the
  training loop. The fork_rng init path is byte-unchanged. Confirm module INIT is NOT re-perturbed (init reproducibility
  unchanged) and the training-loop dropout is now seeded → 0.0 drift.
- **Reproducibility test is NON-VACUOUS:** confirm it actually trains and compares full model state_dict; same-seed →
  0.0 drift; and the "different seeds differ" test genuinely proves dropout is still active (regularization not disabled —
  a real concern: a fix that accidentally disabled dropout would also give 0.0 drift but be WRONG). Verify the diff
  would FAIL if the manual_seed were removed (it did: RED 3.941e-3).
- **#356 changes sound:** the docstring/comments no longer claim "intrinsic FP nondeterminism"; `_WEIGHT_TOL=1e-6` is
  justified (measured 1-vs-2-worker diff now 0.0) and the #356 tests stay green and NON-FLAKY; the divergence-catch is
  still non-vacuous.
- **No NEW simplification violation:** `--paths` failure on training.py is PRE-EXISTING `train_latent_power_module`
  (cc=39, 244 lines). Confirm via `git show HEAD` that cc was already 39 and G4 added only comment lines (0 CC). The
  new test files PASS `--paths`. (Don't block on the pre-existing debt — it's tc2.)
- Existing latent_power suite (201) + #356 tests green (re-run).

## Allowed Scope (actual)
src/latent_power/training.py, tests/unit/latent_power/test_training_reproducibility.py, tests/integration/test_utilization_determinism.py.

## Specific Exclusions (flag if touched)
No gold re-promote / Brier re-validation (deferred tc1). No network.py dropout/architecture change. No G1/G2 touch.
No opt-in flag (must be always-on / one canonical path).

## Constraints (each a review check)
- The seeding fix is deterministic + documented; no new mutable module-level state (a `manual_seed` call is not state).
- Evo/probability change: in-gate evidence is the reproducibility test + LIGHT non-degradation sanity check; the full
  Brier-vs-baseline is the deferred follow-up (tc1) — do NOT demand a full gold Brier here.

## Evidence Produced
- `py -m pytest -q -k training_reproducibility` → 4 passed.
- `py -m pytest tests/unit/latent_power/ -q` → 201 passed.
- `py -m pytest -q -k utilization_determinism` → 2 passed.
- Re-run all of the above yourself.

## Suggested Model Tier
stronger — reason: core training-loop RNG semantics + a strengthened cross-cutting #356 guarantee; the "did the fix
disable dropout vs seed it" distinction and the init-not-reperturbed property are subtle.

## Stop Conditions
Return BLOCK if: the fix disabled/altered dropout instead of seeding it, module init reproducibility changed, the
reproducibility test is vacuous, the #356 tolerance change makes that test flaky or the narrative inaccurate, a NEW
simplification violation was introduced, scope was exceeded, or an opt-in flag was added.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers (file:line + issue), out-of-scope observations.
