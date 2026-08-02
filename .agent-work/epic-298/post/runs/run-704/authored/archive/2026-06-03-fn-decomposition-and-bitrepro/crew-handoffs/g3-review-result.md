# REVIEW_RESULT — g3 (bit-reproducibility spike)

Verdict: **APPROVE** (methodology sound, numbers reproduced, root cause verified in code)

- Reproduced independently: baseline drift 3.712e-4, det-strict 3.027e-4, det-warn 3.358e-4 (~3e-4, ~300x over 1e-6); baseline-seeded 0.0 and det-strict-seeded 0.0 EXACTLY. Strict mode did NOT raise; zero nondeterminism warnings. Cost ~1x.
- Methodology FAIR: identical seeded jobs across conditions (no seed_override), only the determinism/seed knob varies; in-process so flags in effect; baseline genuinely single-thread; drift = max-abs state_dict diff; wall-time warm.
- Root cause verified in code: training.py:95-97 seeds only inside fork_rng() (restores global state on exit); no .train()/.eval() before the loop (only validation-only pair in _evaluate_module); network.py:37 nn.Dropout reused 3x is the only stochastic train-mode op -> train-loop dropout draws from unseeded global RNG. manual_seed(0) -> 0.0 is the matching proof. Seeding bug, NOT intrinsic FP nondeterminism.
- No production code changed (git diff -- src/ tests/ empty; training.py/network.py/test_utilization_determinism.py byte-unchanged).
- GO/NO-GO sound: NO-GO on the literal det-flags criterion; GO-signal via the G4 seeding fix.

## Out-of-scope (tc1)
- When G4 seeding fix lands: update test_utilization_determinism.py docstring + #356 G6 narrative (which wrongly call the drift 'intrinsic FP nondeterminism'); revisit _WEIGHT_TOL=1e-2 once drift is 0.0.
- Design note: G4 must place manual_seed to govern the training loop without re-perturbing module init (spike preseeds global RNG before the whole run; exact placement is G4's design choice).
