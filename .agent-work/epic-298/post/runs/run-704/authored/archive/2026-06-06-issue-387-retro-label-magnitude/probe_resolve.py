"""Quick reality-check probe (NOT a deliverable): re-solve existing retro artifacts at a
lambda sweep and report per-event spread CV + ordering stability vs lambda=1.0.

Reconstructs PhaseObservation from the persisted pairwise diagnostics in each retro JSON
(pair_index, observed_y/outcome, start_bias, weight) and re-runs the SAME solver.
Pure CPU; no DB pull, no NN. Driver scope only, a sample of events per phase.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import torch

from src.latent_power.retro_observation import PhaseObservation
from src.latent_power.retro_solve import solve
from src.latent_power.retro_solution import RetroTruthConfig

ROOT = Path("params/retro_truth")
PHASES = ("quali", "race", "race_start")
LAMBDAS = (1.0, 0.3, 0.1, 0.03, 0.01, 0.003, 1e-3, 1e-4)


def load_observation_and_oldpi(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    entity_ids = tuple(str(e) for e in raw["entity_ids"])
    diag = raw["pairwise_diagnostics"]
    pair_index = torch.tensor(diag["pair_index"], dtype=torch.int64)
    outcome = torch.tensor(diag["observed_y"], dtype=torch.float32)
    start_bias = torch.tensor(diag["start_bias"], dtype=torch.float32)
    weight = torch.tensor(diag["weight"], dtype=torch.float32)
    old_pi = torch.tensor(raw["field"]["pi"], dtype=torch.float32)
    obs = PhaseObservation(
        event_id=raw["event_id"],
        phase=raw["phase"],
        entity_scope=raw["entity_scope"],
        entity_ids=entity_ids,
        pair_index=pair_index,
        outcome=outcome,
        start_bias=start_bias,
        weight=weight,
        start_positions={},
        outcome_positions={},
        dropped_drivers=(),
        baseline_fingerprint=str(raw.get("config_fingerprint", "probe")),
    )
    return obs, old_pi


def spearman(a: torch.Tensor, b: torch.Tensor) -> float:
    # rank correlation; a,b 1D same length
    ra = a.argsort().argsort().to(torch.float64)
    rb = b.argsort().argsort().to(torch.float64)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = (ra.norm() * rb.norm()).item()
    if denom == 0:
        return float("nan")
    return float((ra @ rb).item() / denom)


def sign_flips(old_pi: torch.Tensor, new_pi: torch.Tensor) -> int:
    n = old_pi.shape[0]
    flips = 0
    for i in range(n):
        for j in range(i + 1, n):
            so = old_pi[i] - old_pi[j]
            sn = new_pi[i] - new_pi[j]
            if (so > 0) != (sn > 0) and so != 0 and sn != 0:
                flips += 1
    return flips


def sample_paths(phase: str, n_per_year: int = 2):
    paths = []
    for year_dir in sorted(ROOT.glob("[0-9]" * 4)):
        if not year_dir.is_dir():
            continue
        rounds = sorted(
            (d for d in year_dir.iterdir() if d.is_dir()), key=lambda p: int(p.name)
        )
        for rd in rounds[:n_per_year]:
            p = rd / f"{phase}.json"
            if p.exists():
                paths.append(p)
    return paths


def main():
    for phase in PHASES:
        paths = sample_paths(phase, n_per_year=2)
        print(f"\n==== phase={phase}  (n_events sampled={len(paths)}) ====")
        # per-lambda: collect per-event std, spearman-vs-old, sign-flips
        for lam in LAMBDAS:
            cfg = RetroTruthConfig(lambda_ridge=lam)
            stds = []
            spearmans = []
            total_flips = 0
            total_pairs = 0
            for p in paths:
                obs, old_pi = load_observation_and_oldpi(p)
                res = solve(obs, cfg)
                new_pi = res.field_solution.pi
                stds.append(float(new_pi.std(unbiased=False).item()))
                spearmans.append(spearman(old_pi, new_pi))
                n = new_pi.shape[0]
                total_flips += sign_flips(old_pi, new_pi)
                total_pairs += n * (n - 1) // 2
            mean_std = sum(stds) / len(stds)
            std_of_std = (
                sum((s - mean_std) ** 2 for s in stds) / len(stds)
            ) ** 0.5
            cv = std_of_std / mean_std if mean_std else float("nan")
            mean_sp = sum(spearmans) / len(spearmans)
            min_sp = min(spearmans)
            flip_rate = total_flips / total_pairs if total_pairs else float("nan")
            print(
                f"  lam={lam:<7g} mean_std={mean_std:.4f} CV={cv:.4f} "
                f"spearman(old,new) mean={mean_sp:.5f} min={min_sp:.5f} "
                f"sign_flips={total_flips}/{total_pairs} ({flip_rate:.5f})"
            )


if __name__ == "__main__":
    main()
