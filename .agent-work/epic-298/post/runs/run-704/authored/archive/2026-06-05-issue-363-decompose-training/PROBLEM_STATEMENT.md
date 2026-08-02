# Problem Statement — issue-363-decompose-training

**Issue:** #363 — Decompose `train_latent_power_module` under simplification limits

## Statement

Behavior-preserving decomposition of `train_latent_power_module`
(`src/latent_power/training.py:50`) into private same-module helpers so the
strict simplification limits pass (currently CC=39 / 244 lines; limits CC<20 /
<100 lines). Natural seams: epoch training loop, validation + early-stop
tracking, per-epoch diagnostics row, final diagnostics assembly.

## Protected intent (zero behavior change)

- RNG call order and seeding untouched (`fork_rng` init block, post-init
  `torch.manual_seed(seed)` re-seed, `random.Random(seed)` shuffle order)
- Early-stop / best-checkpoint semantics unchanged
- Diagnostics dict shape and JSONL telemetry unchanged
- Training stays bit-reproducible
- No public API change; helpers module-private per existing convention
  (`_build_optimizer`, `_evaluate_module`)

## Evidence required

1. `py -m src.utils.simplification_limits --paths src/latent_power/training.py` passes
2. latent_power region suite green: `py -m pytest tests/unit/latent_power/`
3. `tests/unit/latent_power/test_training_reproducibility.py` green (bit-repro)
4. New unit tests for the extracted helpers in
   `tests/unit/latent_power/test_training.py` (human-requested)

## Scope

This one function only. No change to training behavior, RNG seeding, or model
architecture (issue non-goals).

Confirmed by human 2026-06-05 (AskUserQuestion: "Confirmed").
