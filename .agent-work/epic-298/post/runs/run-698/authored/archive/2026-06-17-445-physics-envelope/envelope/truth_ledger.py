"""Staged truth ledger (epic #445) — append-only layered estimates + uncertainty.

Principle (user 2026-06-14): save best truth at EACH stage so we can rebuild,
never overwrite. Stage 0 = roughest (raw smoother accel + honest large sigma);
later stages refine uncertainty where new information is reliable, falling back
to the prior stage elsewhere. Adding a stage NEVER modifies an earlier one.

One ledger per (year, gp, session, driver, lap), stored as an npz of flattened
'<stage>::<field>' arrays plus a JSON '_meta' record of provenance per stage.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

LEDGER_ROOT = Path("C:/Programs/f1Brainz/.agent-work/445/ledger")


def ledger_path(year, gp, ses, driver, lap):
    d = LEDGER_ROOT / f"{year}_{gp}_{ses}" / driver
    d.mkdir(parents=True, exist_ok=True)
    return d / f"lap_{lap}.npz"


def load_ledger(path):
    path = Path(path)
    if not path.exists():
        return {"_meta": {"stages": {}}}, {}
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["_meta"])) if "_meta" in z else {"stages": {}}
    arrays = {k: z[k] for k in z.files if k != "_meta"}
    return meta, arrays


def save_base(path, s, t, v, meta_extra=None):
    """Initialize a ledger with the shared coordinate base (s, t, v)."""
    meta, arrays = load_ledger(path)
    arrays["base::s"] = np.asarray(s, float)
    arrays["base::t"] = np.asarray(t, float)
    arrays["base::v"] = np.asarray(v, float)
    meta.setdefault("stages", {})
    if meta_extra:
        meta.update(meta_extra)
    _write(path, meta, arrays)


def save_stage(path, stage, fields, provenance, overwrite=False):
    """Append a stage. Refuses to overwrite an existing stage unless asked."""
    meta, arrays = load_ledger(path)
    if stage in meta.get("stages", {}) and not overwrite:
        raise ValueError(
            f"stage {stage!r} already in ledger {path.name}; refusing to overwrite "
            f"(append-only). Use a new stage name or overwrite=True."
        )
    for k, arr in fields.items():
        arrays[f"{stage}::{k}"] = np.asarray(arr, float)
    meta.setdefault("stages", {})[stage] = {
        "provenance": provenance,
        "fields": list(fields.keys()),
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _write(path, meta, arrays)


def get_stage(path, stage):
    meta, arrays = load_ledger(path)
    fields = meta["stages"][stage]["fields"]
    return {f: arrays[f"{stage}::{f}"] for f in fields}


def best_field(path, field, stage_order):
    """Best available <field> across stages: take each node from the latest stage
    that provides a finite value (with its sigma). stage_order earliest->latest."""
    meta, arrays = load_ledger(path)
    out = None
    out_sig = None
    for stage in stage_order:
        key = f"{stage}::{field}"
        sigkey = f"{stage}::{field}_sigma"
        if key not in arrays:
            continue
        vals = arrays[key]
        sig = arrays.get(sigkey)
        if out is None:
            out = vals.copy()
            out_sig = sig.copy() if sig is not None else np.full_like(vals, np.nan)
        else:
            take = np.isfinite(vals)
            out[take] = vals[take]
            if sig is not None:
                out_sig[take] = sig[take]
    return out, out_sig


def _write(path, meta, arrays):
    np.savez(path, _meta=json.dumps(meta), **arrays)
