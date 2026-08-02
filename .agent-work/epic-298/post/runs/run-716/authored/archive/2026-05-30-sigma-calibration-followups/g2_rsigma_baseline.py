"""No-train |r/sigma| baseline recompute for promoted gold_cycle_260530 bundle (G2 evidence)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from dataclasses import fields
from types import SimpleNamespace

from src.compound_prior.runtime_normalization import CompoundNormalizer
from src.data.database import DatabaseManager
from src.evo_predictor.module_training_orchestration import (
    get_training_adapter,
    prepare_module_training_data,
    requires_compound_normalizer,
)
from src.evo_predictor.run import _compound_prior_artifacts, _resolve_db_args
from src.latent_power.config import LatentPowerConfig
from src.latent_power.retro_delta_join import attach_target_mu_or_drop_entities
from src.latent_power.retro_loader import load_target_mu_for_event
from src.latent_power.training import _evaluate_module

BUNDLE_ROOT = Path(
    "params/gold/runtime_bundles/gold_cycle_260530_042533_2018thru2024/modules"
)
TRAIN_YEARS = list(range(2018, 2024))
EVAL_YEAR = 2024
RETRO_ROOT = Path("params/retro_truth")
COMPOUND_PRIOR_ROOT = "params/gold/compound_prior"
RACE_START_TARGET_LAP = 3


def _load_bundle_compat(manifest_path: Path):
    """Load promoted bundle checkpoints while ignoring removed config keys (e.g. target_mode)."""
    import json
    import torch

    from src.evo_predictor.latent_power_bundle import MANIFEST_FILENAME, _resolve_artifact
    from src.latent_power.modules import get_module

    manifest_path = Path(manifest_path)
    if manifest_path.is_dir():
        manifest_path = manifest_path / MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    module_name = str(manifest["module_name"])
    allowed = {field.name for field in fields(LatentPowerConfig)}
    config_payload = {
        key: value
        for key, value in dict(manifest["config"]).items()
        if key in allowed
    }
    artifacts = manifest["artifacts"]
    checkpoint_path = _resolve_artifact(
        manifest_path.parent, artifacts.get("model_checkpoint_file")
    )
    diagnostics_path = _resolve_artifact(
        manifest_path.parent, artifacts.get("module_diagnostics_file")
    )
    module = get_module(module_name).module_cls(LatentPowerConfig(**config_payload))
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    module.network.load_state_dict(checkpoint["state_dict"])
    diagnostics = json.loads(diagnostics_path.read_text(encoding="utf-8"))
    return SimpleNamespace(module=module, diagnostics=diagnostics)


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


def main() -> None:
    db_args = SimpleNamespace(db_path=None, db_root="data")
    db, db_by_year = _resolve_db_args(db_args, [*TRAIN_YEARS, EVAL_YEAR])
    compound_selected = _compound_prior_artifacts(
        COMPOUND_PRIOR_ROOT,
        target_years=[*TRAIN_YEARS, EVAL_YEAR],
        allow_same_season=False,
    )
    compound_normalizers = {
        year: CompoundNormalizer(artifact) for year, artifact in compound_selected.items()
    }
    rows: list[dict[str, object]] = []
    for module_dir in sorted(path for path in BUNDLE_ROOT.iterdir() if path.is_dir()):
        module_name = module_dir.name
        manifest_path = module_dir / "latent_power_manifest.json"
        if not manifest_path.exists():
            continue
        bundle = _load_bundle_compat(manifest_path)
        adapter = get_training_adapter(module_name)
        normalizers_arg = compound_normalizers if requires_compound_normalizer(adapter) else None
        prepared = prepare_module_training_data(
            module_name=module_name,
            train_years=TRAIN_YEARS,
            eval_year=EVAL_YEAR,
            db=db,
            db_by_year=db_by_year,
            compound_normalizers_by_year=normalizers_arg,
            race_start_target_lap=RACE_START_TARGET_LAP,
        )
        eval_batches = _join_retro(
            prepared.eval_batches,
            phase=prepared.adapter.task,
            entity_scope=prepared.adapter.entity_scope,
        )
        metrics = _evaluate_module(bundle.module, list(eval_batches), seed=0)
        diag = metrics["uncertainty_diagnostics"]
        rows.append(
            {
                "module_name": module_name,
                "eval_event_count": len(eval_batches),
                **diag,
            }
        )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
