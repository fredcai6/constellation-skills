# IMPLEMENTER_RESULT — g3 (bit-reproducibility spike)

Status: complete. Measurement-only; NO production code change (git diff -- src/ tests/ empty).

## Measurements (torch 2.10.0+cpu; CUDA N/A; 2 runs each, warm wall-time)
| condition | knobs | drift (max-abs state_dict) | x baseline time | raised? | nondet warnings |
|---|---|---|---|---|---|
| baseline | use_det(False), threads=1 | 3.78e-4 | 1.00x | no | - |
| deterministic-strict | use_det(True), threads=1 | 3.59e-4 | 1.03x | NO | NONE |
| deterministic-warn | use_det(True, warn_only), threads=1 | 3.46e-4 | 1.03x | no | NONE |
| baseline-seeded (diag) | baseline + manual_seed(0) pre-run | 0.0 | 1.07x | no | - |
| det-strict-seeded (diag) | strict + manual_seed(0) pre-run | 0.0 | 1.06x | no | none |

## Findings
- NO op lacks a deterministic CPU impl (strict mode did not raise; zero warnings). Determinism FLAGS are not the cause.
- ROOT CAUSE = seeding placement bug: train-mode nn.Dropout(0.2) layers in src/latent_power/network.py draw from
  UNSEEDED process-global torch RNG. src/latent_power/training.py seeds only inside `with torch.random.fork_rng():
  torch.manual_seed(seed)`, and fork_rng() RESTORES global state on exit -> module init seeded, training-loop dropout NOT.
  A single torch.manual_seed(0) before the run -> EXACTLY 0.0 drift, even with flags off. Not kernel nondeterminism.

## GO/NO-GO
- NO-GO on the literal criterion (det-flags "mode" leaves drift 3.59e-4 >> 1e-6; flags are the wrong tool).
- STRONG GO signal for G4 via a DIFFERENT, better fix: a ~one-line RNG-seeding fix in training.py (seed the global RNG
  for the training loop, not only inside the restored fork_rng block) -> EXACT 0.0 drift at ~1x cost; use_det optional
  defensive guard. Caveat: 0.0 shown at the bounded #356 scale; re-confirm at production scale (multi-thread BLAS
  reduction-order FP nondeterminism could reappear, and the flag would then be the right guard).

## Artifacts (all under .agent-work; no production change)
- harness: .agent-work/fn-decomposition-and-bitrepro/bitrepro_spike.py
- report: .agent-work/fn-decomposition-and-bitrepro/bitrepro-report.md
- raw: .agent-work/fn-decomposition-and-bitrepro/evidence/bitrepro_results.json
- re-run: `py .agent-work/fn-decomposition-and-bitrepro/bitrepro_spike.py --out <json>` (skips exit 2 if data absent)

## REVIEWER focus (load-bearing root-cause claim)
- Re-run the harness; confirm baseline ~3.6e-4 vs seeded 0.0.
- Verify the root cause by reading training.py (fork_rng block) + network.py (Dropout layers): training-loop dropout
  draws from unseeded global RNG.
- Confirm no production code changed; GO/NO-GO reasoning sound.

## Implication beyond this run
- #356 G6 attributed the drift to "intrinsic FP nondeterminism" -> that was a MISDIAGNOSIS; it's a fixable seeding bug.
