"""G4 smoke: sigma calibration path with synthetic retro_delta training."""
from __future__ import annotations

import json
import math
import random
import sys
from dataclasses import replace
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.latent_power.config import LatentPowerConfig
from src.latent_power.modules import DriverRacePowerFromRaceWeekendModule
from src.latent_power.training import train_latent_power_module
from tests.fixtures.latent_power.synthetic_event import generate_event

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
DIAGNOSTICS_PATH = EVIDENCE_DIR / "g4-diagnostics.jsonl"


def _data_availability() -> dict[str, bool]:
    data_dir = REPO_ROOT / "data"
    retro_root = REPO_ROOT / "params" / "retro_truth"
    db_files = list(data_dir.glob("*.db")) if data_dir.is_dir() else []
    retro_files = list(retro_root.rglob("*")) if retro_root.is_dir() else []
    retro_file_count = sum(1 for p in retro_files if p.is_file())
    return {
        "data_dir_exists": data_dir.is_dir(),
        "db_count": len(db_files),
        "retro_root_exists": retro_root.is_dir(),
        "retro_file_count": retro_file_count,
    }


def _build_batches(seed: int = 42) -> list:
    torch.manual_seed(seed)
    raw_batches = [generate_event(n_entities=6, seed=i, feature_dim=8) for i in range(4, 7)]
    return [
        replace(
            batch,
            outcome=None,
            target_mu=torch.randn(batch.pair_index.shape[0], dtype=torch.float32) * 0.5,
        )
        for batch in raw_batches
    ]


def collect_sigma_stats(module: DriverRacePowerFromRaceWeekendModule, batches) -> dict:
    floor = float(module.config.solve_sigma_floor)
    was_training = module.network.training
    module.network.eval()
    sigma_chunks: list[torch.Tensor] = []
    try:
        with torch.no_grad():
            for batch in batches:
                pairwise = module.predict_pairwise(batch)
                sigma_chunks.append(pairwise.sigma.detach().cpu())
    finally:
        module.network.train(was_training)

    sigma = torch.cat(sigma_chunks)
    clamped = torch.clamp(sigma, min=floor)
    effective_w = 1.0 / (clamped * clamped)
    tol = 1e-5
    at_floor = (sigma <= floor + tol).to(torch.float32)

    return {
        "count": int(sigma.numel()),
        "min": float(sigma.min().item()),
        "median": float(sigma.median().item()),
        "max": float(sigma.max().item()),
        "mean": float(sigma.mean().item()),
        "std": float(sigma.std(unbiased=False).item()),
        "frac_at_solve_sigma_floor": float(at_floor.mean().item()),
        "max_effective_W": float(effective_w.max().item()),
        "solve_sigma_floor_W_cap": float(1.0 / (floor * floor)),
        "has_nan": bool(torch.isnan(sigma).any()),
        "has_inf": bool(torch.isinf(sigma).any()),
    }


def per_epoch_sigma_snapshots(
    batches,
    config: LatentPowerConfig,
    *,
    epochs: int,
    seed: int,
) -> list[dict]:
    """Lightweight epoch loop mirroring training to capture sigma evolution."""
    with torch.random.fork_rng():
        torch.manual_seed(seed)
        module = DriverRacePowerFromRaceWeekendModule(config)
    rng_shuffle = random.Random(seed)
    optimizer = torch.optim.Adam(module.network.parameters(), lr=float(config.learning_rate))
    total_steps = epochs * len(batches)
    warmup_steps = min(int(config.warmup_steps), total_steps)

    def lr_lambda(step: int) -> float:
        if step < warmup_steps:
            return float(step + 1) / float(warmup_steps + 1)
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * progress))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lr_lambda)
    snapshots: list[dict] = []

    for epoch in range(epochs):
        shuffled = list(batches)
        rng_shuffle.shuffle(shuffled)
        running_loss = 0.0
        last_sigma_nll = 0.0
        for batch in shuffled:
            optimizer.zero_grad(set_to_none=True)
            pairwise = module.predict_pairwise(batch)
            losses = module.loss_from_pairwise(pairwise, batch)
            if torch.isnan(losses.total):
                raise RuntimeError(f"NaN total loss at epoch {epoch + 1}")
            losses.total.backward()
            optimizer.step()
            scheduler.step()
            running_loss += float(losses.total.detach().item())
            last_sigma_nll = float(losses.sigma_nll.detach().item())

        sigma_stats = collect_sigma_stats(module, batches)
        snapshots.append(
            {
                "epoch": epoch + 1,
                "train_loss": running_loss / len(batches),
                "sigma_nll": last_sigma_nll,
                **sigma_stats,
            }
        )
    return snapshots


def main() -> dict:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    availability = _data_availability()
    batches = _build_batches()
    config = LatentPowerConfig(
        feature_dim=8,
        val_season_cutoff=2025,
        nn_hidden_dim=16,
        learning_rate=1e-2,
        lambda_sigma_nll=1.0,
        solve_sigma_floor=0.05,
        warmup_steps=0,
    )

    with torch.random.fork_rng():
        torch.manual_seed(0)
        untrained = DriverRacePowerFromRaceWeekendModule(config)
    initial_sigma = collect_sigma_stats(untrained, batches)

    result = train_latent_power_module(
        batches,
        config=config,
        epochs=10,
        seed=0,
        diagnostics_path=str(DIAGNOSTICS_PATH),
    )
    final_sigma = collect_sigma_stats(result.module, batches)
    epoch_snapshots = per_epoch_sigma_snapshots(batches, config, epochs=10, seed=0)

    epoch_losses = list(result.epoch_losses)
    loss_decreased = epoch_losses[-1] < epoch_losses[0]
    sigma_varies = (
        abs(final_sigma["max"] - final_sigma["min"]) > 0.01
        and final_sigma["std"] > 0.01
    )
    not_stuck_at_prior = final_sigma["median"] < 9.0 or final_sigma["std"] > 0.05

    diagnostics_rows = []
    if DIAGNOSTICS_PATH.is_file():
        diagnostics_rows = [
            json.loads(line) for line in DIAGNOSTICS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()
        ]

    summary = {
        "data_availability": availability,
        "training_mode": "synthetic_target_mu",
        "config": {
            "lambda_sigma_nll": config.lambda_sigma_nll,
            "solve_sigma_floor": config.solve_sigma_floor,
            "student_t_nu": config.student_t_nu,
            "sigma_prior_max": config.sigma_prior_max,
        },
        "initial_sigma": initial_sigma,
        "final_sigma": final_sigma,
        "epoch_losses": epoch_losses,
        "loss_decreased": loss_decreased,
        "sigma_varies": sigma_varies,
        "not_stuck_at_prior_max": not_stuck_at_prior,
        "epoch_snapshots": epoch_snapshots,
        "diagnostics_rows": diagnostics_rows,
        "pairwise_metrics_final_step": result.diagnostics.get("pairwise_metrics", {}),
    }
    return summary


if __name__ == "__main__":
    payload = main()
    out_path = EVIDENCE_DIR / "g4-smoke-summary.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
