"""Longitudinal (braking) grip channel via friction-ellipse projection (#445).

Pure straight-line braking ~doesn't exist (diagnostic), so recover the longitudinal
arm from the abundant COMBINED trail-braking cloud:

  ellipse:  (alat/G_lat(v))^2 + (along/G_long(v))^2 = 1
  =>        along_eq = decel / sqrt(1 - (alat/G_lat)^2)      (project onto the long axis)

G_lat(v) is FIXED from the well-determined lateral channel (aniso_fit, near-apex alat).
Then fit G_long(v)=A_long + B_long v^2 (shared A_long, per-car B_long) on along_eq.

Physics: B_long ~ DOWNFORCE + DRAG (both add v^2 to braking), B_lat ~ DOWNFORCE only.
Two payoff checks:
  (1) corr(B_long, B_lat) across constructors -> do two INDEPENDENT downforce views agree?
  (2) B_long - B_lat (the drag-laden residual) -> recover the known drag order vs the
      independent drag channel (drag_fingerprint10_fits.json)?
Also: is B_long teammate-consistent (a car property)? And the sensor cap biases decel low.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from season_prior_filter import fit_weekend, VREF, GSAT  # noqa: E402
from aniso_fit import load as load_aniso, clouds_lat, DRV2TEAM  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
BRK = OUT / "braking_nodes_full.npz"
DRAG = OUT / "drag_fingerprint10_fits.json"


def load_braking():
    d = np.load(BRK, allow_pickle=True)
    rounds = [str(x) for x in d["rounds"]]; cars = [str(x) for x in d["cars"]]
    out = {}
    for r in rounds:
        cl = {}
        for c in cars:
            k = f"v__{r}__{c}"
            if k in d.files:
                cl[c] = (d[f"v__{r}__{c}"].astype(float),
                         d[f"alat__{r}__{c}"].astype(float),
                         d[f"d__{r}__{c}"].astype(float),
                         d[f"w__{r}__{c}"].astype(float))
        if cl:
            out[r] = cl
    return out


def spear(a, b):
    if len(a) < 3:
        return np.nan
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def teammate_gaps(B):
    bt = {}
    for k, val in B.items():
        t = DRV2TEAM.get(k)
        if t:
            bt.setdefault(t, []).append(val)
    return [abs(v[0] - v[1]) for v in bt.values() if len(v) == 2]


def main():
    if not BRK.exists():
        print("braking cache not ready:", BRK); return
    aniso = dict(load_aniso())
    brk = load_braking()

    seasonLong, seasonLat = {}, {}
    gapsLong = []
    for rname, latcl_all in aniso.items():
        if rname not in brk:
            continue
        clat = clouds_lat(latcl_all)
        clat = {c: v for c, v in clat.items() if len(v[0]) >= 18}
        if len(clat) < 4:
            continue
        Al, Bl = fit_weekend(clat)
        # project braking nodes -> longitudinal-equivalent decel
        clong = {}
        for c, (v, alat, decel, w) in brk[rname].items():
            if c not in Bl or len(v) < 25:
                continue
            glat = np.minimum(Al + Bl[c] * v * v, GSAT)
            ratio = np.clip(alat / glat, 0.0, 0.97)
            along_eq = decel / np.sqrt(1.0 - ratio * ratio)
            m = np.isfinite(along_eq) & (along_eq < 8.0)
            if m.sum() >= 25:
                clong[c] = (v[m], along_eq[m], w[m])
        if len(clong) < 4:
            continue
        Ag, Bg = fit_weekend(clong)
        gapsLong += teammate_gaps(Bg)
        for c in clong:
            seasonLong.setdefault(c, []).append(Bg[c] * VREF * VREF)
            if c in Bl:
                seasonLat.setdefault(c, []).append(Bl[c] * VREF * VREF)

    # aggregate to constructor
    cars = [c for c in seasonLong if len(seasonLong[c]) >= 6 and c in seasonLat]
    teams = sorted({DRV2TEAM[c] for c in cars if c in DRV2TEAM})
    longT = {t: np.mean([np.mean(seasonLong[c]) for c in cars if DRV2TEAM.get(c) == t]) for t in teams}
    latT = {t: np.mean([np.mean(seasonLat[c]) for c in cars if DRV2TEAM.get(c) == t]) for t in teams}

    print("=" * 78)
    print("LONGITUDINAL (braking) channel via ellipse projection")
    print("=" * 78)
    print(f"  teammate B_long gap (1e-3): {np.mean(gapsLong)*1e3:.3f}  "
          f"(car property if small; cf lateral ~0.15)")
    print(f"\n  {'team':>5} {'B_long·vref²':>12} {'B_lat·vref²':>12} {'long-lat(drag?)':>16}")
    fl = np.mean(list(longT.values())); fa = np.mean(list(latT.values()))
    resid = {}
    for t in sorted(teams, key=lambda k: -longT[k]):
        resid[t] = (longT[t] - fl) - (latT[t] - fa)
        print(f"  {t:>5} {longT[t]:12.3f} {latT[t]:12.3f} {resid[t]:+16.3f}")
    xl = np.array([longT[t] - fl for t in teams]); xa = np.array([latT[t] - fa for t in teams])
    print(f"\n  (1) corr(B_long, B_lat) across {len(teams)} constructors = "
          f"{np.corrcoef(xl, xa)[0,1]:+.3f}  Spearman {spear(xl, xa):+.3f}")
    print("      (two INDEPENDENT downforce views; high+ => they agree => downforce is real)")

    # (2) drag cross-check
    if DRAG.exists():
        dfits = {int(k): v for k, v in json.loads(DRAG.read_text()).items()}
        dr = sorted(dfits)
        fieldCdA = {i: np.mean([dfits[rd][t]["CdA_c"] for t in dfits[rd]]) for i, rd in enumerate(dr)}
        dragoff = {}
        for t in teams:
            vals = [dfits[rd][t]["CdA_c"] - fieldCdA[i] for i, rd in enumerate(dr) if t in dfits[rd]]
            if len(vals) >= 6:
                dragoff[t] = float(np.mean(vals))
        common = [t for t in teams if t in dragoff]
        if len(common) >= 4:
            rr = np.array([resid[t] for t in common]); dd = np.array([dragoff[t] for t in common])
            print(f"\n  (2) drag cross-check on {len(common)} teams:")
            print(f"      corr(long-lat residual, independent drag CdA offset) = "
                  f"{np.corrcoef(rr, dd)[0,1]:+.3f}  Spearman {spear(rr, dd):+.3f}")
            print("      (+ => the braking residual recovers drag; known: RBR/WIL low, MERC/FER/AMR high)")
            for t in sorted(common, key=lambda k: -dragoff[k]):
                print(f"        {t:>5}: drag CdA off {dragoff[t]:+.4f}   long-lat resid {resid[t]:+.3f}")
    else:
        print("\n  (drag fingerprint cache absent; skip drag cross-check)")


if __name__ == "__main__":
    main()
