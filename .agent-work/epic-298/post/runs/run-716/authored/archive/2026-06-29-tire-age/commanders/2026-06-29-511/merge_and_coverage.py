"""G2 merge + coverage diagnosis (commander-run, work-area tool — not committed).

Merges the 7 per-worker part DBs into the canonical race_stint_estimates.db
(raw row INSERT OR REPLACE; schema identical), then computes the coverage
diagnosis the G2 reasoning gate requires and writes G2_COVERAGE.md.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import numpy as np

_REPO = Path(r"C:/Programs/f1Brainz-511")
sys.path.insert(0, str(_REPO))

from src.physics.layer2.race_stint_store import RaceStintStore  # noqa: E402

CANON = r"C:/Programs/f1Brainz/data/race_stint_estimates.db"
PARTS_DIR = Path(
    r"C:/Users/fredc/AppData/Local/Temp/claude/C--Programs-f1Brainz/"
    r"ead34712-6309-4c4d-a6e6-8dba62630517/scratchpad/race_stint_parts"
)
OUT = _REPO / ".agent-work/511/evidence/G2_COVERAGE.md"


def _columns(con, table):
    return [r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()]


def merge_parts() -> dict:
    """Raw-row INSERT OR REPLACE from each part DB into canonical. Returns per-part counts."""
    RaceStintStore(CANON)  # ensure canonical table exists
    counts = {}
    with sqlite3.connect(CANON) as cdst:
        cols = _columns(cdst, "race_stint_estimates")
        col_sql = ", ".join(f'"{c}"' for c in cols)
        ph = ", ".join("?" for _ in cols)
        for part in sorted(PARTS_DIR.glob("race_stint_part*.db")):
            try:
                with sqlite3.connect(f"file:///{part.as_posix()}?mode=ro", uri=True) as csrc:
                    rows = csrc.execute(
                        f"SELECT {col_sql} FROM race_stint_estimates"
                    ).fetchall()
            except sqlite3.OperationalError as exc:
                counts[part.name] = f"ERR {exc}"
                continue
            cdst.executemany(
                f"INSERT OR REPLACE INTO race_stint_estimates ({col_sql}) VALUES ({ph})",
                rows,
            )
            counts[part.name] = len(rows)
        cdst.commit()
    return counts


def _psd_finite(cov) -> tuple[bool, bool]:
    if cov is None:
        return (False, False)
    a = np.asarray(cov, dtype=float)
    finite = bool(np.all(np.isfinite(a)))
    psd = False
    if finite and a.ndim == 2 and a.shape[0] == a.shape[1]:
        try:
            psd = bool(np.all(np.linalg.eigvalsh(a) >= -1e-9))
        except Exception:
            psd = False
    return (finite, psd)


def coverage() -> str:
    store = RaceStintStore(CANON)
    df = store.load(year=2023, session_type="R", status=None)
    ok = df[df["fit_status"] == "ok"].copy()
    L = []
    L.append("# G2 Coverage Diagnosis — race_stint_estimates 2023 (R)")
    L.append("")
    L.append(f"- Total rows: {len(df)}  | ok: {len(ok)}  | error: {int((df['fit_status']=='error').sum())}")
    L.append(f"- Distinct circuits (gp_name): {df['gp_name'].nunique()}  | drivers: {df['driver'].nunique()}")
    L.append("")
    # per-circuit
    L.append("## Per-circuit (ok rows / lateral fits)")
    for gp, g in ok.groupby("gp_name"):
        lat = int(g["lateral_g0"].notna().sum())
        L.append(f"- {gp}: rows={len(g)} lateral_fit={lat}")
    L.append("")
    # per-compound
    L.append("## Per-compound (ok rows)")
    for comp, g in ok.groupby("compound"):
        lat = int(g["lateral_g0"].notna().sum())
        trac = int(g["traction_a0"].notna().sum())
        L.append(f"- {comp}: rows={len(g)} lateral_fit={lat} traction_fit={trac}")
    L.append("")
    # per-axis yield
    L.append("## Per-axis fit yield (of ok rows)")
    for axis, col in [
        ("lateral (g0)", "lateral_g0"),
        ("traction (a0)", "traction_a0"),
        ("braking", "brake_decel_ms2"),
        ("power_drag", "max_power_w"),
        ("coast", "coast_rolling_decel_ms2"),
    ]:
        n = int(ok[col].notna().sum()) if col in ok.columns else 0
        L.append(f"- {axis}: {n}/{len(ok)}")
    L.append("")
    # (g0,k) distribution
    lat = ok[ok["lateral_g0"].notna()]
    if len(lat):
        g0 = lat["lateral_g0"].to_numpy(float)
        k = lat["lateral_k"].to_numpy(float)
        L.append("## Lateral (g0,k) distribution")
        L.append(f"- g0: min={g0.min():.3f} median={np.median(g0):.3f} max={g0.max():.3f}")
        L.append(f"- k : min={k.min():.5f} median={np.median(k):.5f} max={k.max():.5f}  | k>=0: {int((k>=0).sum())}/{len(k)}")
        # covariance sanity
        fin = psd = 0
        for cov in lat["lateral_covariance"]:
            f, p = _psd_finite(cov)
            fin += int(f); psd += int(p)
        L.append(f"- lateral covariance finite={fin}/{len(lat)} PSD={psd}/{len(lat)}")
    L.append("")
    # pit-staggered age spread
    if "tyre_life_start" in ok.columns and "tyre_life_end" in ok.columns:
        span = (ok["tyre_life_end"] - ok["tyre_life_start"]).to_numpy(float)
        span = span[np.isfinite(span)]
        if len(span):
            L.append("## Pit-staggered tyre-age spread")
            L.append(f"- per-stint age span: min={span.min():.0f} mean={span.mean():.1f} max={span.max():.0f}")
        # multi-compound races
        mc = ok.groupby("gp_name")["compound"].nunique()
        L.append(f"- races with >=2 compounds (ok): {int((mc>=2).sum())}/{ok['gp_name'].nunique()}")
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    if "--coverage-only" not in sys.argv:
        print("Merging part DBs into canonical...")
        print(merge_parts())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = coverage()
    OUT.write_text(text, encoding="utf-8")
    print(text)
    print(f"\nWrote {OUT}")
