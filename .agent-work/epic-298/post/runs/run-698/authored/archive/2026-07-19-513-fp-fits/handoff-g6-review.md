# Reviewer Handoff — G6 (held-out gate harness)

## What was implemented
`src/physics/layer2/fp_gate.py` (core encoding GATE_PROTOCOL.md: `GateExtractor` Protocol seam,
`build_gate_observations`, `run_lowo`, learned/clock arms, paired bootstrap, divergent-case read,
emergence audit, sandbagging demo) + `scripts/fp_representativeness_gate.py` (CLI) + 36 synthetic tests.
Result: `.agent-work/513-fp-fits/result-g6-implement.md`. FROZEN CONTRACT:
`.agent-work/513-fp-fits/GATE_PROTOCOL.md` (verify the harness encodes it).

## How to inspect
`git diff` the three new files; read `GATE_PROTOCOL.md` and confirm the harness matches it.

## Close criteria to verify (reproduce)
- THE ANTI-RIG CHECK (most important): the NULL fixture (`test_harness_reports_honest_null_not_rigged_to_always_pass`)
  genuinely returns HONEST_NULL — confirm the harness is NOT constructed to always PASS. Read the null fixture
  and confirm learned CANNOT beat clock there by construction. If the null fixture is weak/trivially rigged, BLOCK.
- POSITIVE fixture returns PASS where representativeness genuinely diverges from clock.
- LEAKAGE (F6): `test_shuffling_held_out_q_targets_does_not_change_train_fit` +
  `test_run_lowo_fold_params_unaffected_by_held_out_shuffle` — held-out Q cannot reach the learned fit.
  Confirm the LOWO fit signature structurally cannot see held-out data.
- DIVERGENT-CASE read (F4): the primary verdict is read on |w_learned − w_clock| top-tercile observations.
  NOTE: the implementer normalizes both arms (min-max) before differencing to fix a scale mismatch
  (clock=unbounded exp decay vs learned=bounded logistic) — verify this normalization is sound and does NOT
  smuggle in an unfair advantage for either arm (it's a decision-candidate in the result).
- Protocol faithfulness: LOWO over weekends, paired bootstrap significance, both channels reported
  (PRIMARY grip + SECONDARY longitudinal at matched-σ or confounded-labeled), emergence audit present.
- NO session-type hardcoding; weighting comes ONLY from `fp_representativeness`.
- NO real telemetry/DB/compute (synthetic fixtures only); `git status --short data/` clean;
  `py -m src.utils.simplification_limits --baseline --paths <touched>` PASS.

## Verification commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_representativeness_gate.py -q && py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/fp_gate.py scripts/fp_representativeness_gate.py; git status --short data/
```

## Return format
REVIEW_RESULT: verdict APPROVE or BLOCK + findings. BLOCK on: a null fixture that cannot actually fail
(rigged-to-pass), any leakage path (held-out Q reaching learned fit), a divergent-case normalization that
unfairly advantages one arm, session-type hardcoding, or protocol deviation. Write to
`.agent-work/513-fp-fits/result-g6-review.md` AND SendMessage to "ShipI-513".
