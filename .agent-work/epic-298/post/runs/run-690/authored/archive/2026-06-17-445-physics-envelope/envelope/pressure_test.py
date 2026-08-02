"""Pressure-test the v5 measured-capability lap reconstruction (#445). SAME stack (p95 frontiers,
DRS from telemetry, measured grip/accel/braking) applied unchanged to cases it wasn't built on:
slow cars at Monza, and RBR/others at Hungary (regime shift). Does it reconstruct each real lap, or
does the RBR/Monza tuning make everyone fast / break on a different track?"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import (load_session, fit_grip_clean, get_apex_nodes, load_cal_nodes,
                           G_CONST, OUT)  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from long_constraints import long_accel  # noqa: E402
from lap_trace import profile_to_t  # noqa: E402
from lap_trace_v5 import fit_curve, fit_brake, vg_minenv, sim, GSAT, BRAKE_SAT  # noqa: E402

TEAMS = {"RBR": ["VER", "PER"], "WIL": ["ALB", "SAR"], "HAA": ["MAG", "HUL"],
         "MERC": ["HAM", "RUS"], "FER": ["LEC", "SAI"]}
TRACKS = {"Monza": dict(gp="Italy", rib="monza", length=5793),
          "Hungary": dict(gp="Hungary", rib="hungary", length=4381)}
GRID = np.linspace(0, 100, 600)


def reconstruct(track, team, cal, q):
    cfg = TRACKS[track]; cars = TEAMS[team]
    d = np.load(OUT / f"ribbon_clean_{cfg['rib']}.npz"); s, kappa = d["s"], d["kappa"]
    pct_rib = s / s[-1] * 100; length = cfg["length"]
    vk, gg = get_apex_nodes(cal, cfg["gp"], cars)
    if vk is None or len(vk) < 25:
        return None
    A, B, _ = fit_grip_clean(vk, gg)
    if A is None:
        return None
    Gs = lambda v: min(A + B * v * v, GSAT)
    v, a, op = throttle_av(q, cars)
    a_open = fit_curve(v[op], a[op]); a_closed = fit_curve(v[~op], a[~op])
    if a_open is None or a_closed is None:
        return None
    va, aa, th, bk = long_accel(q, cars); brk = (bk > 0.5) & (aa < 0)
    if brk.sum() < 30:
        return None
    Ab, Bb, _, _ = fit_brake(va[brk], -aa[brk] / G_CONST)
    abrake = lambda vv: min(Ab + Bb * vv * vv, BRAKE_SAT)
    # DRS zones from the team's fastest lap
    drv0 = max(cars, key=lambda c: len(q.laps.pick_drivers(c)))
    lap = q.laps.pick_drivers(drv0).pick_fastest(); tel = lap.get_car_data().add_distance()
    drs = tel["DRS"].to_numpy(float); dist = tel["Distance"].to_numpy(float)
    o = np.argsort(dist); dist, drs = dist[o], drs[o]
    drs_open = np.interp(pct_rib, dist / dist[-1] * 100, (drs >= 10).astype(float)) > 0.5
    vmax_node = np.where(drs_open, a_open["vmax"], a_closed["vmax"])
    a_node = lambda vv, i: max((a_open if drs_open[i] else a_closed)["K"] *
                               ((a_open if drs_open[i] else a_closed)["vmax"] ** 3 / max(vv, 1.0) - vv * vv), 0.0)
    vg = vg_minenv(kappa, A, B, vmax_node)
    vrec = sim(s, kappa, vg, a_node, vmax_node, Gs, abrake)
    t_rec = profile_to_t(pct_rib, vrec, length, GRID)[0][-1]
    # real fastest team lap (actual + same-method computed)
    best_actual = np.inf; t_real = np.nan
    for drv in cars:
        try:
            lp = q.laps.pick_drivers(drv).pick_fastest(); lt = lp["LapTime"].total_seconds()
            if lt < best_actual:
                best_actual = lt; t2 = lp.get_car_data().add_distance()
                dd = t2["Distance"].to_numpy(float); vv = t2["Speed"].to_numpy(float) / 3.6
                t_real = profile_to_t(dd / dd[-1] * 100, vv, cfg["length"], GRID)[0][-1]
        except Exception:
            pass
    return dict(rec=t_rec, real_actual=best_actual, real_comp=t_real,
                vmin=vrec.min() * 3.6, vtop=vrec.max() * 3.6, A=A, Ab=Ab,
                vmaxo=a_open["vmax"] * 3.6)


def main():
    cal = load_cal_nodes()
    cases = [("Monza", "RBR"), ("Monza", "WIL"), ("Monza", "HAA"),
             ("Hungary", "RBR"), ("Hungary", "WIL"), ("Hungary", "FER")]
    print(f"{'track':>8} {'team':>5} | {'recon':>6} {'real':>6} {'Δ(rec-real)':>11} | "
          f"{'vmin':>5} {'vtop':>5} {'gripA':>6} {'brakeA':>6}")
    sess = {}
    for track, team in cases:
        if track not in sess:
            sess[track] = load_session(2023, TRACKS[track]["gp"], "Q")
        try:
            r = reconstruct(track, team, cal, sess[track])
        except Exception as e:
            print(f"{track:>8} {team:>5} | FAILED {e}"); continue
        if r is None:
            print(f"{track:>8} {team:>5} | thin/failed"); continue
        dvc = r["rec"] - r["real_comp"]
        print(f"{track:>8} {team:>5} | {r['rec']:>6.2f} {r['real_actual']:>6.2f} "
              f"{dvc:>+11.2f} | {r['vmin']:>5.0f} {r['vtop']:>5.0f} {r['A']:>6.2f} {r['Ab']:>6.2f}")
    print("\n  Δ = recon − real(same-method). Generalises if Δ small & consistent across cars/tracks;")
    print("  overfit-to-RBR if slow cars come out too fast (Δ very negative for WIL/HAA).")


if __name__ == "__main__":
    main()
