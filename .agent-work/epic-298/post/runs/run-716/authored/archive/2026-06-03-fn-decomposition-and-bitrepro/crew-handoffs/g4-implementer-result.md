# IMPLEMENTER_RESULT — g4 (fix unseeded training-loop dropout RNG)

Status: complete. Always-on fix; training now run-to-run reproducible (0.0 drift).

## The fix
- src/latent_power/training.py: after the UNCHANGED `with torch.random.fork_rng(): manual_seed(seed); module=...`
  init block and BEFORE the training loop, added `torch.manual_seed(seed)` (+ documenting comment). fork_rng restores
  global RNG on exit, so the training-loop nn.Dropout (no per-call generator) was drawing from unseeded global RNG;
  re-seeding after init (init already done inside fork_rng, unaffected) makes dropout deterministic. One canonical
  path, no opt-in flag. +0 cyclomatic complexity; the established torch.manual_seed pattern (resolves, not introduces,
  unseeded-global-state).

## Tests (RED->GREEN)
- NEW tests/unit/latent_power/test_training_reproducibility.py (4 tests, bounded, no DB):
  - same-seed -> byte-identical weights (drift 3.941e-3 RED before fix -> 0.0 GREEN after).
  - different-seeds -> different weights (dropout still active; regularization intact).
  - init not re-perturbed by the fix (fork_rng isolation holds).
  - smoke-eval not degraded (finite/sane losses + eval total).
- Existing latent_power suite: 201 passed.

## #356 narrative correction (+ guarantee strengthened)
- tests/integration/test_utilization_determinism.py: rewrote docstring/comments/assert-msg that called the drift
  "intrinsic FP nondeterminism" (now a fixed seeding bug). Measured post-fix 1-vs-2-worker diff = 0.0 -> tightened
  _WEIGHT_TOL 1e-2 -> 1e-6. Both #356 tests stay green; divergence-catch still non-vacuous (wrong-seed drifts O(0.1-1.0)).

## Evidence
- `py -m pytest -q -k training_reproducibility` -> 4 passed.
- `py -m pytest tests/unit/latent_power/ -q` -> 201 passed.
- `py -m pytest -q -k utilization_determinism` (real gold cycle) -> 2 passed.
- `--paths src/latent_power/training.py + 2 test files` -> FAIL only on PRE-EXISTING train_latent_power_module
  (cc=39, 244 lines; HEAD was cc=39/238 -> G4 added +6 comment lines, 0 CC). Test files PASS. Repo --baseline does
  not flag training.py (file_lines only). -> tc2 (decompose train_latent_power_module) flagged, out of G4 scope.

## Scope
- Only training.py (1-line fix + comment), new test file, test_utilization_determinism.py (docstring + tol). No gold
  re-promote / Brier re-validation (deferred follow-up tc1); no network.py change; no G1/G2 touch; no opt-in flag.

## Out-of-scope observations
- tc2: train_latent_power_module pre-existing over strict limits (cc=39, 244) — NOT one of Rec A's 5 surfaced
  functions; recommend a dedicated decomposition follow-up.
- tc1 (already flagged): full gold re-promote + Brier re-validation after this seeding fix (training output shifts to
  a seeded realization).
