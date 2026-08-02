"""Shared helpers for G4 bounded sigma-calibration research."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.compound_prior.runtime_normalization import CompoundNormalizer
from src.data.database import DatabaseManager
from src.evo_predictor.module_training_orchestration import (
    get_training_adapter,
    prepare_module_training_data,
    requires_compound_normalizer,
)
from src.evo_predictor.run import _compound_prior_artifacts, _resolve_db_args
from src.latent_power.config import LatentPowerConfig
from src.latent_power.losses import student_t_nll
from src.latent_power.modules import get_module
from src.latent_power.retro_delta_join import attach_target_mu_or_drop_entities
from src.latent_power.retro_loader import load_target_mu_for_event
from src.latent_power.training import _evaluate_module, train_latent_power_module

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
WORK_DIR = Path(__file__).resolve().parent

TRAIN_YEARS = [2023]
EVAL_YEAR = 2024
EPOCHS = 5
SEED = 0
DB_ROOT = str(REPO_ROOT / "data")
COMPOUND_PRIOR_ROOT = str(REPO_ROOT / "params" / "gold" / "compound_prior")
RETRO_ROOT = REPO_ROOT / "params" / "retro_truth"
RACE_START_TARGET_LAP = 3
PROMOTED_BUNDLE_ROOT = (
    REPO_ROOT
    / "params"
    / "gold"
    / "runtime_bundles"
    / "gold_cycle_260530_042533_2018thru2024"
    / "modules"
)

SMOKE_HIDDEN = 32
SMOKE_LR = 1e-4
SMOKE_DROPOUT = 0.2


def pearson_corr(x: np.ndarray, y: np.ndarray) -> float | None:
    if x.size < 3 or y.size < 3:
        return None
    if float(np.std(x)) < 1e-12 or float(np.std(y)) < 1e-12:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def spearman_corr(x: np.ndarray, y: np.ndarray) -> float | None:
    if x.size < 3:
        return None
    rx = np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(np.float64)
    ry = np.argsort(np.argsort(y, kind="stable"), kind="stable").astype(np.float64)
    return pearson_corr(rx, ry)


def loo_correlations(
    event_ids: list[str],
    x: np.ndarray,
    y: np.ndarray,
) -> dict[str, float | None]:
    full_pearson = pearson_corr(x, y)
    full_spearman = spearman_corr(x, y)
    loo_pearson: list[float] = []
    loo_spearman: list[float] = []
    for idx in range(len(event_ids)):
        mask = np.ones(len(event_ids), dtype=bool)
        mask[idx] = False
        p = pearson_corr(x[mask], y[mask])
        s = spearman_corr(x[mask], y[mask])
        if p is not None:
            loo_pearson.append(p)
        if s is not None:
            loo_spearman.append(s)
    return {
        "pearson": full_pearson,
        "spearman": full_spearman,
        "loo_pearson_mean": float(np.mean(loo_pearson)) if loo_pearson else None,
        "loo_pearson_std": float(np.std(loo_pearson)) if loo_pearson else None,
        "loo_spearman_mean": float(np.mean(loo_spearman)) if loo_spearman else None,
        "loo_spearman_std": float(np.std(loo_spearman)) if loo_spearman else None,
    }


def _load_bundle_compat(manifest_path: Path):
    import torch as _torch

    from src.evo_predictor.latent_power_bundle import MANIFEST_FILENAME, _resolve_artifact

    manifest_path = Path(manifest_path)
    if manifest_path.is_dir():
        manifest_path = manifest_path / MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    module_name = str(manifest["module_name"])
    allowed = {field.name for field in fields(LatentPowerConfig)}
    config_payload = {
        key: value for key, value in dict(manifest["config"]).items() if key in allowed
    }
    artifacts = manifest["artifacts"]
    checkpoint_path = _resolve_artifact(
        manifest_path.parent, artifacts.get("model_checkpoint_file")
    )
    module = get_module(module_name).module_cls(LatentPowerConfig(**config_payload))
    checkpoint = _torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    module.network.load_state_dict(checkpoint["state_dict"])
    return module


def try_load_promoted_module(module_name: str):
    manifest_path = PROMOTED_BUNDLE_ROOT / module_name / "latent_power_manifest.json"
    if not manifest_path.is_file():
        return None, str(manifest_path)
    return _load_bundle_compat(manifest_path), str(manifest_path)


def _join_retro(batches, *, phase: str, entity_scope: str):
    out = []
    for batch in batches:
        match = re.match(r"(\d{4})[_:](\d+)", batch.event_id)
        if match is None:
            continue
        labels = load_target_mu_for_event(
            year=int(match.group(1)),
            round_num=int(match.group(2)),
            phase=phase,
            entity_scope=entity_scope,
            root=RETRO_ROOT,
        )
        if labels is None:
            continue
        joined = attach_target_mu_or_drop_entities(batch, labels)
        if joined is not None:
            out.append(joined)
    return tuple(out)


def prepare_smoke_batches(module_name: str):
    db_args = SimpleNamespace(db_path=None, db_root=str(REPO_ROOT / "data"))
    db, db_by_year = _resolve_db_args(db_args, [*TRAIN_YEARS, EVAL_YEAR])
    adapter = get_training_adapter(module_name)
    compound_normalizers = None
    if requires_compound_normalizer(adapter):
        compound_selected = _compound_prior_artifacts(
            COMPOUND_PRIOR_ROOT,
            target_years=[*TRAIN_YEARS, EVAL_YEAR],
            allow_same_season=False,
        )
        compound_normalizers = {
            year: CompoundNormalizer(artifact) for year, artifact in compound_selected.items()
        }
    prepared = prepare_module_training_data(
        module_name=module_name,
        train_years=TRAIN_YEARS,
        eval_year=EVAL_YEAR,
        db=db,
        db_by_year=db_by_year,
        compound_normalizers_by_year=compound_normalizers,
        race_start_target_lap=RACE_START_TARGET_LAP,
        seed=SEED,
    )
    train_batches = _join_retro(
        prepared.train_batches,
        phase=prepared.adapter.task,
        entity_scope=prepared.adapter.entity_scope,
    )
    eval_batches = _join_retro(
        prepared.eval_batches,
        phase=prepared.adapter.task,
        entity_scope=prepared.adapter.entity_scope,
    )
    return prepared, train_batches, eval_batches


def build_latent_config(
    prepared,
    *,
    student_t_nu: float = 4.0,
    student_t_nu_sigma: float | None = None,
    lambda_sigma_nll: float = 1.0,
) -> LatentPowerConfig:
    return LatentPowerConfig(
        feature_dim=prepared.feature_dim,
        val_season_cutoff=EVAL_YEAR,
        nn_hidden_dim=SMOKE_HIDDEN,
        dropout=SMOKE_DROPOUT,
        learning_rate=SMOKE_LR,
        early_stop_patience=2,
        warmup_steps=0,
        entity_type=prepared.adapter.entity_scope,
        target="quali_order" if prepared.adapter.task == "quali" else "race_order",
        student_t_nu=float(student_t_nu),
        student_t_nu_sigma=student_t_nu_sigma,
        lambda_sigma_nll=float(lambda_sigma_nll),
        solve_sigma_floor=0.05,
    )


def train_smoke_module(
    prepared,
    train_batches,
    eval_batches,
    *,
    student_t_nu: float = 4.0,
    student_t_nu_sigma: float | None = None,
    lambda_sigma_nll: float = 1.0,
):
    config = build_latent_config(
        prepared,
        student_t_nu=student_t_nu,
        student_t_nu_sigma=student_t_nu_sigma,
        lambda_sigma_nll=lambda_sigma_nll,
    )
    result = train_latent_power_module(
        train_batches,
        validation_batches=eval_batches,
        config=config,
        epochs=EPOCHS,
        seed=SEED,
        module_name=prepared.module_name,
    )
    metrics = _evaluate_module(result.module, list(eval_batches), seed=SEED)
    pairwise = collect_pairwise_eval(result.module, eval_batches, nu=student_t_nu)
    event_rows = collect_event_level_eval(result.module, eval_batches)
    return {
        "config": {
            "student_t_nu": student_t_nu,
            "student_t_nu_sigma": student_t_nu_sigma,
            "lambda_sigma_nll": lambda_sigma_nll,
            "epochs": EPOCHS,
        },
        "training": {
            "final_train_loss": result.diagnostics.get("final_train_loss"),
            "best_eval_total": result.diagnostics.get("best_eval_total"),
            "epochs_run": result.diagnostics.get("epochs_run"),
        },
        "uncertainty_diagnostics": metrics["uncertainty_diagnostics"],
        "pairwise_metrics": metrics["pairwise_metrics"],
        "pairwise_arrays": pairwise,
        "event_level": event_rows,
    }


def collect_pairwise_eval(module, eval_batches, *, nu: float) -> dict[str, object]:
    sigma_all: list[float] = []
    abs_r_all: list[float] = []
    r_over_sigma_all: list[float] = []
    per_pair_nll: list[float] = []
    was_training = module.network.training
    module.network.eval()
    try:
        with torch.no_grad():
            for batch in eval_batches:
                pairwise = module.predict_pairwise(batch)
                if batch.target_mu is None:
                    continue
                residual = (batch.target_mu - pairwise.mu).detach()
                sigma = pairwise.sigma.detach()
                abs_r = residual.abs()
                r_over_sigma = abs_r / sigma
                # Elementwise NLL for per-pair correlation (scalar student_t_nll is mean-reduced).
                mu_pred = pairwise.mu
                r = batch.target_mu - mu_pred
                log_sigma = torch.log(sigma)
                quad = (r * r) / (nu * sigma * sigma)
                nll_vec = log_sigma + 0.5 * (nu + 1.0) * torch.log1p(quad)
                sigma_all.extend(sigma.cpu().tolist())
                abs_r_all.extend(abs_r.cpu().tolist())
                r_over_sigma_all.extend(r_over_sigma.cpu().tolist())
                per_pair_nll.extend(nll_vec.cpu().tolist())
    finally:
        module.network.train(was_training)

    sigma_np = np.asarray(sigma_all, dtype=np.float64)
    nll_np = np.asarray(per_pair_nll, dtype=np.float64)
    return {
        "pair_count": int(sigma_np.size),
        "sigma_std": float(np.std(sigma_np)) if sigma_np.size else None,
        "sigma_min": float(np.min(sigma_np)) if sigma_np.size else None,
        "sigma_median": float(np.median(sigma_np)) if sigma_np.size else None,
        "sigma_max": float(np.max(sigma_np)) if sigma_np.size else None,
        "abs_r_median": float(np.median(abs_r_all)) if abs_r_all else None,
        "r_over_sigma_p50": float(np.quantile(r_over_sigma_all, 0.50)) if r_over_sigma_all else None,
        "r_over_sigma_p95": float(np.quantile(r_over_sigma_all, 0.95)) if r_over_sigma_all else None,
        "corr_sigma_per_pair_nll_pearson": pearson_corr(sigma_np, nll_np),
        "corr_sigma_per_pair_nll_spearman": spearman_corr(sigma_np, nll_np),
    }


def collect_event_level_eval(module, eval_batches) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    was_training = module.network.training
    module.network.eval()
    try:
        with torch.no_grad():
            for batch in eval_batches:
                if batch.target_mu is None:
                    continue
                try:
                    pairwise = module.predict_pairwise(batch)
                    pred = module.predict_from_pairwise(pairwise, batch)
                    losses = module.loss_from_pairwise(pairwise, batch)
                except (torch.linalg.LinAlgError, RuntimeError):
                    continue
                sigma = pairwise.sigma.detach().cpu().numpy()
                residual = (batch.target_mu - pairwise.mu).detach().cpu().numpy()
                rows.append(
                    {
                        "event_id": batch.event_id,
                        "pair_count": int(sigma.size),
                        "pairwise_log_loss": float(losses.supervised_nll.detach().item()),
                        "sigma_pi_trace": float(pred.diagnostics["sigma_pi_trace"]),
                        "sigma_pair_std": float(np.std(sigma)),
                        "sigma_pair_mean": float(np.mean(sigma)),
                        "abs_r_median": float(np.median(np.abs(residual))),
                        "r_over_sigma_p95": float(
                            np.quantile(np.abs(residual) / np.maximum(sigma, 1e-9), 0.95)
                        ),
                    }
                )
    finally:
        module.network.train(was_training)

    if not rows:
        return {"event_count": 0, "events": [], "correlations": {}}

    sigma_trace = np.array([float(r["sigma_pi_trace"]) for r in rows], dtype=np.float64)
    log_loss = np.array([float(r["pairwise_log_loss"]) for r in rows], dtype=np.float64)
    event_ids = [str(r["event_id"]) for r in rows]
    corrs = loo_correlations(event_ids, sigma_trace, log_loss)
    ranked_by_sigma = sorted(rows, key=lambda r: float(r["sigma_pi_trace"]), reverse=True)
    ranked_by_loss = sorted(rows, key=lambda r: float(r["pairwise_log_loss"]), reverse=True)
    return {
        "event_count": len(rows),
        "events": rows,
        "correlations": corrs,
        "top3_sigma_pi_trace": ranked_by_sigma[:3],
        "top3_log_loss": ranked_by_loss[:3],
    }


def eval_frozen_module(module, eval_batches, *, label: str, nu: float = 4.0) -> dict[str, object]:
    metrics = _evaluate_module(module, list(eval_batches), seed=SEED)
    return {
        "label": label,
        "uncertainty_diagnostics": metrics["uncertainty_diagnostics"],
        "pairwise_metrics": metrics["pairwise_metrics"],
        "pairwise_arrays": collect_pairwise_eval(module, eval_batches, nu=nu),
        "event_level": collect_event_level_eval(module, eval_batches),
    }


def write_evidence(stem: str, payload: dict[str, object], markdown_body: str) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    json_path = EVIDENCE_DIR / f"{stem}.json"
    md_path = EVIDENCE_DIR / f"{stem}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(markdown_body, encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
