"""Probe 2 (reality-check, NOT a deliverable): two questions.

Q1: Is the constant-CV a STRUCTURAL property of binary-outcome BT, robust over the FULL
    event population (not just a sample) and at a representative lambda? Re-confirm that
    lowering lambda only uniformly scales spread (CV invariant).

Q2: Does OBSERVED event dispersion actually vary event-to-event? Two model-free dispersion
    proxies computed from the SAME persisted pairwise data the labels are solved from, plus
    from finishing positions:
      - margin_dispersion: there is none in binary y (that's the point) -> use start_bias as
        the only persisted continuous signal (race/race_start), AND
      - n_entities and n_pairs (field size varies) — a trivial structural varier.
    The real magnitude signal (finishing-time gaps) is NOT in retro artifacts; this probe
    shows what IS and ISN'T available without going to the DB.

This is the evidence that decides option1 (re-solve) vs option2 (external target).
"""
from __future__ import annotations

import json
from pathlib import Path

import torch

from src.latent_power.retro_observation import PhaseObservation
from src.latent_power.retro_solve import solve
from src.latent_power.retro_solution import RetroTruthConfig

ROOT = Path("params/retro_truth")


def load_obs(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    entity_ids = tuple(str(e) for e in raw["entity_ids"])
    diag = raw["pairwise_diagnostics"]
    obs = PhaseObservation(
        event_id=raw["event_id"],
        phase=raw["phase"],
        entity_scope=raw["entity_scope"],
        entity_ids=entity_ids,
        pair_index=torch.tensor(diag["pair_index"], dtype=torch.int64),
        outcome=torch.tensor(diag["observed_y"], dtype=torch.float32),
        start_bias=torch.tensor(diag["start_bias"], dtype=torch.float32),
        weight=torch.tensor(diag["weight"], dtype=torch.float32),
        start_positions={},
        outcome_positions={},
        dropped_drivers=(),
        baseline_fingerprint="probe",
    )
    return obs, raw


def all_paths(phase: str):
    out = []
    for year_dir in sorted(ROOT.glob("[0-9]" * 4)):
        if not year_dir.is_dir():
            continue
        for rd in sorted((d for d in year_dir.iterdir() if d.is_dir()), key=lambda p: int(p.name)):
            p = rd / f"{phase}.json"
            if p.exists():
                out.append(p)
    return out


def cv(values):
    m = sum(values) / len(values)
    sd = (sum((v - m) ** 2 for v in values) / len(values)) ** 0.5
    c = sd / m if m else float("nan")
    return c, m, sd


def main():
    for phase in ("quali", "race", "race_start"):
        paths = all_paths(phase)
        print(f"\n==== phase={phase}  FULL population n_events={len(paths)} ====")
        for lam in (1.0, 0.1, 0.01):
            cfg = RetroTruthConfig(lambda_ridge=lam)
            stds = []
            for p in paths:
                obs, _ = load_obs(p)
                res = solve(obs, cfg)
                stds.append(float(res.field_solution.pi.std(unbiased=False).item()))
            c, m, sd = cv(stds)
            print(f"  lam={lam:<6g} per-event pi std: mean={m:.4f} std_across_events={sd:.5f} CV={c:.5f}")

        # Q2: what continuous, event-varying signal is even present in the artifacts?
        n_ent = []
        startbias_absmean = []
        for p in paths:
            obs, _ = load_obs(p)
            n_ent.append(len(obs.entity_ids))
            sb = obs.start_bias.abs()
            startbias_absmean.append(float(sb.mean().item()) if sb.numel() else 0.0)
        ce, me, sde = cv([float(x) for x in n_ent])
        print(f"  n_entities across events: mean={me:.2f} std={sde:.3f} CV={ce:.4f} (min={min(n_ent)} max={max(n_ent)})")
        if phase != "quali":
            cb, mb, sdb = cv(startbias_absmean)
            print(f"  |start_bias| mean per event: mean={mb:.4f} std={sdb:.4f} CV={cb:.4f}  <- only persisted continuous varier")


if __name__ == "__main__":
    main()
