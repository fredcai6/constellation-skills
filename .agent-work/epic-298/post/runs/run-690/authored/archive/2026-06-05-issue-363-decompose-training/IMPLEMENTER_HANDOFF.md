# Implementer Handoff

## Gate
`g1` (work area: `C:\Programs\f1Brainz\.agent-work\issue-363-decompose-training\`, checklist `execute.json`)

Repo: `C:\Programs\f1Brainz`, branch `constellation/issue-363-decompose-training` (already checked out). GitHub issue #363.

## Task
Behavior-preserving decomposition of `train_latent_power_module` (`src/latent_power/training.py:50`, currently CC=39 / 244 lines) into private same-module helpers so every function in the file passes strict simplification limits (CC<20, <100 lines). Suggested seams (adapt as the code dictates):
- input/batch validation + module-class resolution (lines ~61-93)
- the per-epoch training loop body (lines ~138-159)
- the per-epoch diagnostics JSONL row write (lines ~164-181)
- validation eval + early-stop/best-checkpoint tracking (lines ~183-236)
- final diagnostics dict assembly (lines ~247-288)

Plus: unit tests for the extracted helpers added to `tests/unit/latent_power/test_training.py` (human-requested; test the helper contracts, not torch internals).

## Protected Intent
Zero behavior change. Specifically:
- RNG call order and seeding exactly as now: `fork_rng` + `manual_seed(seed)` for module init, then the post-init `torch.manual_seed(seed)` re-seed (the comment block at lines 98-103 explains why — preserve comment and semantics), then `random.Random(seed)` for shuffling. Do not add/remove/reorder any RNG-consuming call.
- Training must stay bit-reproducible (`test_training_reproducibility_same_seed_is_bit_identical` proves it).
- Early-stop / best-checkpoint semantics, min_delta comparison, patience counting unchanged.
- Diagnostics dict keys/values and JSONL telemetry rows unchanged.
- Public API unchanged: `train_latent_power_module` signature, `LatentPowerTrainingResult`, `train_race_power_module`, `__all__`.

## Test Mode
Test-after allowed. This is a behavior-preserving refactor pinned by an existing end-to-end suite (`tests/unit/latent_power/test_training.py`, `test_training_reproducibility.py`); run it before and after. New helper unit tests are written after extraction against the extracted signatures.

## Close Criteria
- `py -m src.utils.simplification_limits --paths src/latent_power/training.py tests/unit/latent_power/test_training.py` → PASS
- `py -m pytest tests/unit/latent_power/ -q` → all green (run from repo root; use `py`, never `python`)
- New unit tests exist in `tests/unit/latent_power/test_training.py` covering each extracted helper
- `git diff` shows changes only in the two allowed files

## Allowed Scope
- `src/latent_power/training.py`
- `tests/unit/latent_power/test_training.py`

## Specific Exclusions
- Any other file (no conftest, no config, no other latent_power module)
- No change to training behavior, RNG seeding, or model architecture (issue non-goals)
- No new public names: helpers are module-private (`_underscore`) in `training.py`; `__all__` unchanged

## Constraints
- `src/latent_power` must not import `src/evo_predictor` (constraint:latent_power_no_evo_import)
- No mutable module-level runtime state (project review blocker)
- Match existing module idiom (`_build_optimizer`, `_evaluate_module` are the local helper style); a small frozen/private dataclass for early-stop state is acceptable if it reads cleaner than threading many locals
- Keep the lines 98-103 re-seed comment with the code it explains

## Required Evidence
- Before/after output of the simplification limits command
- Full pytest output (final summary line) for `tests/unit/latent_power/`
- List of extracted helpers with one-line responsibility each

## Verification Commands

```bash
cd C:/Programs/f1Brainz
py -m src.utils.simplification_limits --paths src/latent_power/training.py tests/unit/latent_power/test_training.py
py -m pytest tests/unit/latent_power/ -q
```

## Suggested Model Tier
simple bounded — mechanical code motion with strong engine-checked criteria; the bit-repro test is the drift tripwire.

## Authority
Decided (do not re-decide): one gate; helpers private in same module; helper unit tests required; scope limited to the two files. You may decide: exact helper boundaries/names/signatures, whether to use a private state dataclass. Stop rather than decide: anything touching behavior, public API, or files outside scope.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required evidence cannot be produced (e.g., a test fails for a pre-existing reason), or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (command outputs), assumptions used, stop conditions hit, out-of-scope observations.
