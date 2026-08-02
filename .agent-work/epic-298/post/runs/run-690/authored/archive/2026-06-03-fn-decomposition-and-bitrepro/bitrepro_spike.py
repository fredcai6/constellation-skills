#!/usr/bin/env python
"""THROWAWAY measurement spike (gate G3, fn-decomposition-and-bitrepro).

NOT production code. NOT a committed test. This script measures whether
latent-power CPU training can be made (near-)bit-reproducible run-to-run, and at
what training-time cost. It changes NOTHING in src/: it only sets torch
determinism flags in THIS process and reuses the bounded #356 determinism
harness (tests/integration/test_utilization_determinism.py) which runs the real
gold-cycle train+backtest jobs through ``run_jobs`` at n_workers=1 (in-process,
so flags set here are in effect during training).

Fair comparison: identical seeds/data/config across every run; we vary ONLY the
determinism knobs between conditions. The training code re-seeds itself each run
(``torch.manual_seed(seed)`` inside ``fork_rng`` + ``random.Random(seed)`` for
batch shuffling), so the two runs of a condition are seed-identical by
construction. Per condition we run training TWICE into separate temp trees and
record (a) max-abs weight drift over the model state_dict and (b) wall-time/run.

Conditions:
  1. baseline             - current behavior (single thread via the plan, same seed).
  2. deterministic-strict - torch.use_deterministic_algorithms(True) + set_num_threads(1).
                            If this RAISES on an op without a deterministic impl,
                            we capture the exact op + error (a key finding).
  3. deterministic-warn   - torch.use_deterministic_algorithms(True, warn_only=True)
                            + set_num_threads(1); logs nondeterministic ops via
                            Python warnings, measures drift anyway.

CUBLAS_WORKSPACE_CONFIG is CUDA-only -> N/A on this CPU build (documented, not set).

Re-run:
  py .agent-work/fn-decomposition-and-bitrepro/bitrepro_spike.py \
     --out .agent-work/fn-decomposition-and-bitrepro/evidence/bitrepro_results.json
Optional: --runs N (default 2) to do more than two runs per condition.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
import time
import warnings
from pathlib import Path
from typing import Any, Callable

# .agent-work/fn-decomposition-and-bitrepro/bitrepro_spike.py -> repo root is parents[2].
_REPO_ROOT = Path(__file__).resolve().parents[2]
_TEST_PATH = _REPO_ROOT / "tests" / "integration" / "test_utilization_determinism.py"


def _load_356_harness():
    """Import the #356 determinism test module by path and reuse its setup.

    We do NOT modify it; we import its private helpers (_run_plan, _load_weights,
    _max_weight_diff) and its bounded module set. Importing by file path avoids any
    dependence on the tests package being importable as a module.
    """
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    spec = importlib.util.spec_from_file_location("_bitrepro_356_harness", _TEST_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load #356 harness from {_TEST_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _one_training_run(
    harness, run_dir: Path, *, preseed: int | None = None
) -> tuple[list[dict], float]:
    """Run the bounded job set once at n_workers=1; return (results, wall_seconds).

    ``preseed`` (diagnostic only) re-seeds the PROCESS-GLOBAL torch RNG immediately
    before the run. The production training loop's ``nn.Dropout`` layers draw from the
    global RNG during the train-mode forward pass; training.py seeds only inside a
    ``fork_rng()`` block (restored on exit), so the loop's dropout is NOT seeded
    per-run. Setting a global seed here tests whether that unseeded-RNG path is the
    drift source. This is a measurement knob in the harness, NOT a src/ change.
    """
    import torch

    if preseed is not None:
        torch.manual_seed(preseed)
    start = time.perf_counter()
    results = harness._run_plan(run_dir, n_workers=1)
    return results, time.perf_counter() - start


def _max_state_dict_drift(harness, results_a: list[dict], results_b: list[dict]) -> float:
    """Max absolute weight diff across every module's state_dict between two runs."""
    drift = 0.0
    for result_a, result_b in zip(results_a, results_b):
        state_a = harness._load_weights(result_a["manifest_path"])
        state_b = harness._load_weights(result_b["manifest_path"])
        drift = max(drift, harness._max_weight_diff(state_a, state_b))
    return drift


def _set_baseline() -> dict[str, Any]:
    import torch

    # Match the plan's intra-worker thread cap so baseline == "current single-thread".
    torch.use_deterministic_algorithms(False)
    torch.set_num_threads(1)
    return {"use_deterministic_algorithms": False, "warn_only": None, "num_threads": 1}


def _set_deterministic_strict() -> dict[str, Any]:
    import torch

    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)  # strict: may RAISE during training
    return {"use_deterministic_algorithms": True, "warn_only": False, "num_threads": 1}


def _set_deterministic_warn() -> dict[str, Any]:
    import torch

    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True, warn_only=True)
    return {"use_deterministic_algorithms": True, "warn_only": True, "num_threads": 1}


def _reset_determinism() -> None:
    import torch

    # Leave global torch state clean between conditions so one condition cannot
    # leak its flag into the next.
    torch.use_deterministic_algorithms(False)


def _measure_condition(
    harness,
    name: str,
    setter: Callable[[], dict[str, Any]],
    *,
    n_runs: int,
    root: Path,
    capture_warnings: bool,
    preseed: int | None = None,
) -> dict[str, Any]:
    """Run one condition n_runs times; return drift + per-run wall-times (+ findings)."""
    print(f"\n=== condition: {name} (runs={n_runs}, preseed={preseed}) ===", flush=True)
    record: dict[str, Any] = {
        "condition": name,
        "n_runs": n_runs,
        "preseed": preseed,
        "wall_seconds": [],
        "max_weight_drift": None,
        "flags": None,
        "raised": None,
        "nondeterministic_ops": [],
        "status": "ok",
    }

    _reset_determinism()
    try:
        flags = setter()
    except Exception as exc:  # a flag setter itself failing is a finding
        record["status"] = "setter-error"
        record["raised"] = {"type": type(exc).__name__, "message": str(exc)}
        print(f"  SETTER RAISED: {type(exc).__name__}: {exc}", flush=True)
        return record
    record["flags"] = flags

    run_results: list[list[dict]] = []
    caught: list[warnings.WarningMessage] = []
    try:
        with warnings.catch_warnings(record=True) as wlist:
            warnings.simplefilter("always")
            for run_index in range(n_runs):
                run_dir = root / f"{name}_run{run_index}"
                results, wall = _one_training_run(harness, run_dir, preseed=preseed)
                run_results.append(results)
                record["wall_seconds"].append(round(wall, 4))
                print(f"  run {run_index}: {wall:.3f}s", flush=True)
            caught = list(wlist) if capture_warnings else []
    except RuntimeError as exc:
        # use_deterministic_algorithms(True) strict path raises a RuntimeError naming
        # the op that lacks a deterministic implementation. Capture it verbatim.
        record["status"] = "raised"
        record["raised"] = {"type": type(exc).__name__, "message": str(exc)}
        print(f"  TRAINING RAISED: {type(exc).__name__}: {exc}", flush=True)
        return record

    # Distill the nondeterministic-op warnings (deduped, message text only).
    seen: set[str] = set()
    for w in caught:
        text = str(w.message)
        if "deterministic" in text.lower() and text not in seen:
            seen.add(text)
            record["nondeterministic_ops"].append(text)
    for text in record["nondeterministic_ops"]:
        print(f"  nondet-op warning: {text}", flush=True)

    drift = _max_state_dict_drift(harness, run_results[0], run_results[1])
    for later in run_results[2:]:
        drift = max(drift, _max_state_dict_drift(harness, run_results[0], later))
    record["max_weight_drift"] = drift
    print(f"  max weight drift (run0 vs others): {drift:.3e}", flush=True)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="path to write the results JSON")
    parser.add_argument("--runs", type=int, default=2, help="runs per condition (>=2)")
    args = parser.parse_args(argv)
    if args.runs < 2:
        parser.error("--runs must be >= 2 (need two runs to measure run-to-run drift)")

    harness = _load_356_harness()
    if not harness._required_dbs_present() or not harness._RETRO_ROOT.is_dir():
        print(f"SKIP: {harness._SKIP_REASON}", flush=True)
        return 2

    import torch

    env_note = {
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        "cublas_workspace_config_note": "CUDA-only knob; N/A on this CPU build (not set).",
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
        "modules": list(harness._MODULES),
        "train_years": list(harness._TRAIN_YEARS),
        "eval_year": harness._EVAL_YEAR,
        "max_rounds_per_year": harness._MAX_ROUNDS_PER_YEAR,
        "epochs": harness._EPOCHS,
        "threads_per_worker": 1,
        "n_workers": 1,
    }
    print("env:", json.dumps(env_note, indent=2), flush=True)

    # (name, setter, capture_warnings, preseed). The two HANDOFF conditions are
    # baseline + deterministic-strict; deterministic-warn surfaces nondeterministic-op
    # warnings; the *-seeded conditions are a ROOT-CAUSE diagnostic showing what a
    # global-RNG preseed (a contained extra knob) would buy beyond the set-flags call.
    conditions = [
        ("baseline", _set_baseline, False, None),
        ("deterministic-strict", _set_deterministic_strict, True, None),
        ("deterministic-warn", _set_deterministic_warn, True, None),
        ("baseline-seeded", _set_baseline, False, 0),
        ("deterministic-strict-seeded", _set_deterministic_strict, True, 0),
    ]

    records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="bitrepro_spike_") as tmp:
        root = Path(tmp)
        # One discarded warmup run so the first MEASURED condition is not penalized by
        # cold-start import/JIT/allocator costs (otherwise wall-time is not a fair knob
        # comparison). Reported wall-times below are therefore all warm.
        _set_baseline()
        print("\n=== warmup (discarded) ===", flush=True)
        _warm_results, _warm_wall = _one_training_run(harness, root / "_warmup")
        print(f"  warmup: {_warm_wall:.3f}s (discarded)", flush=True)
        for name, setter, capture, preseed in conditions:
            records.append(
                _measure_condition(
                    harness,
                    name,
                    setter,
                    n_runs=args.runs,
                    root=root,
                    capture_warnings=capture,
                    preseed=preseed,
                )
            )
    _reset_determinism()

    # Derived comparison vs baseline mean wall-time.
    baseline = next(r for r in records if r["condition"] == "baseline")
    baseline_mean = (
        sum(baseline["wall_seconds"]) / len(baseline["wall_seconds"])
        if baseline["wall_seconds"]
        else None
    )
    for record in records:
        if record["wall_seconds"]:
            record["wall_mean"] = round(sum(record["wall_seconds"]) / len(record["wall_seconds"]), 4)
            record["wall_min"] = round(min(record["wall_seconds"]), 4)
            if baseline_mean:
                record["wall_ratio_vs_baseline"] = round(record["wall_mean"] / baseline_mean, 3)
        else:
            record["wall_mean"] = None
            record["wall_min"] = None
            record["wall_ratio_vs_baseline"] = None

    payload = {"env": env_note, "criterion": {"drift_lt": 1e-6, "wall_ratio_lt": 2.0}, "conditions": records}
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # Console summary table.
    print("\n================ SUMMARY ================", flush=True)
    header = f"{'condition':<22} {'runs':>4} {'drift(max-abs)':>16} {'wall_mean(s)':>13} {'x_baseline':>11}  status"
    print(header, flush=True)
    print("-" * len(header), flush=True)
    for record in records:
        drift = record["max_weight_drift"]
        drift_str = f"{drift:.3e}" if isinstance(drift, (int, float)) else "n/a"
        wall_mean = record.get("wall_mean")
        wall_str = f"{wall_mean:.3f}" if isinstance(wall_mean, (int, float)) else "n/a"
        ratio = record.get("wall_ratio_vs_baseline")
        ratio_str = f"{ratio:.2f}x" if isinstance(ratio, (int, float)) else "n/a"
        print(
            f"{record['condition']:<22} {record['n_runs']:>4} {drift_str:>16} "
            f"{wall_str:>13} {ratio_str:>11}  {record['status']}",
            flush=True,
        )
    print(f"\nwrote {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
