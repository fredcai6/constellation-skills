"""Season prior on the DRAG/POWER channel — validate the architecture (epic #445).

The human's idea: chase a prior through the season (update, don't re-solve). Test
it on the channel we TRUST (drag/power re-fits sensibly; cross_circuit showed CdA
tracks wing config, RBR low / Merc high drag = known character). Decisive ground
truth the grip channel can't offer:
  - ENGINE POWER is a season-constant PU property (doesn't change per track; DRS
    doesn't touch it). 2023 PUs: RBR=Honda RBPT, FER=Ferrari, MERC & WIL=Mercedes
    (WIL a customer). Filter RELATIVE power (car - field mean per race, removing the
    per-track ERS-deploy common-mode) through the season. If WIL CONVERGES to MERC
    (same engine), distinct from RBR/FER, the prior-chasing architecture WORKS on
    known truth.
  - Thin-power tracks (twisty, short straights) give wild per-race P; filter tames.
  - CdA relative-to-field (drag character) should persist season-stable (RBR low).

Light compute: full-throttle uses raw car_data (no Kalman smoothing); whole 22-race
season is cheap. Quali only (low fuel, max push/deploy = cleanest power).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from joint_long import collect, MASS, RHO  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CACHE = OUT / "drag_prior_fits.json"
CAL = list(range(1, 23))
TEAMS = {"RBR": ["VER", "PER"], "MERC": ["HAM", "RUS"], "FER": ["LEC", "SAI"], "WIL": ["ALB", "SAR"]}
ENGINE = {"RBR": "Honda-RBPT", "FER": "Ferrari", "MERC": "Mercedes", "WIL": "Mercedes"}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def robust_joint_fit(d):
    """a = P/(m v) - 0.5 rho CdA v^2/m. Joint (P, CdA_c, CdA_o) when both DRS states
    present; else single-CdA. SEs via pseudo-inverse (rank-safe)."""
    v, a, drs = d[:, 0], d[:, 1], d[:, 2]
    op = drs >= 10
    x1 = 1.0 / (MASS * v)
    x2 = 0.5 * RHO * v**2 / MASS
    if op.sum() >= 8 and (~op).sum() >= 8:
        X = np.column_stack([x1, -x2 * (~op), -x2 * op]); two = True
    else:
        X = np.column_stack([x1, -x2]); two = False
    coef, *_ = np.linalg.lstsq(X, a, rcond=None)
    resid = a - X @ coef
    dof = max(len(a) - X.shape[1], 1)
    cov = np.sum(resid**2) / dof * np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    if two:
        return dict(P=float(coef[0]), sP=float(se[0]), CdA_c=float(coef[1]),
                    sCc=float(se[1]), CdA_o=float(coef[2]), n=len(a))
    return dict(P=float(coef[0]), sP=float(se[0]), CdA_c=float(coef[1]),
                sCc=float(se[1]), CdA_o=float(coef[1]), n=len(a))


def collect_team(session, drvs):
    rows = []
    for car in drvs:
        try:
            r = collect(session, car)
            if len(r):
                rows.append(r)
        except Exception:
            pass
    return np.vstack(rows) if rows else np.empty((0, 3))


def per_race_fits():
    if CACHE.exists():
        log(f"loading cached fits {CACHE.name}")
        return {int(k): v for k, v in json.loads(CACHE.read_text()).items()}
    out = {}
    for rd in CAL:
        try:
            q = H.load_session(2023, rd, "Q")
        except Exception as e:
            log(f"  round {rd}: load failed ({e})"); continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]) if ev is not None else str(rd)
        row = {}
        for team, drvs in TEAMS.items():
            d = collect_team(q, drvs)
            if len(d) < 40:
                continue
            try:
                f = robust_joint_fit(d)
            except Exception as e:
                log(f"    {nm[:18]}/{team}: fit failed ({e})"); continue
            row[team] = {k: f[k] for k in ("P", "sP", "CdA_c", "sCc", "CdA_o", "n")}
        if row:
            out[rd] = dict(name=nm, fits=row)
            log(f"  round {rd:>2} {nm[:22]:22}: " +
                " ".join(f"{t}={row[t]['P']/1e3:.0f}" for t in row))
    CACHE.write_text(json.dumps(out, indent=1))
    log(f"cached -> {CACHE.name}")
    return out


def kalman_1d(series, q_proc, r_floor):
    """Forward Bayesian filter (causal prior-chasing). series=[(rd, obs, sd)]."""
    x = pv = None
    traj = []
    for rd, obs, sd in series:
        R = max(sd, r_floor) ** 2
        if x is None:
            x, pv = obs, R
        else:
            pv += q_proc ** 2
            k = pv / (pv + R)
            x = x + k * (obs - x)
            pv = (1 - k) * pv
        traj.append((rd, x, np.sqrt(pv)))
    return traj


def rel_series(data, rounds, field_key, val):
    """per-team series of (round, car_minus_fieldmean, sd) for the chosen quantity."""
    out = {t: [] for t in TEAMS}
    for rd in rounds:
        fits = data[rd]["fits"]
        present = list(fits)
        if len(present) < 2:
            continue
        fld = np.mean([fits[t][val] for t in present])
        for t in present:
            out[t].append((rd, fits[t][val] - fld, fits[t][field_key]))
    return out


def main():
    data = per_race_fits()
    rounds = sorted(data)
    log(f"{len(rounds)} races with fits")

    # ---- RELATIVE POWER filtered through the season (engine ground truth) ----
    print("\n" + "=" * 74)
    print("SEASON RELATIVE-POWER FILTER (kW vs field) — WIL should converge to MERC")
    print("(same Mercedes PU); FER strongest. removes per-track ERS-deploy common-mode")
    print("=" * 74)
    relP = rel_series(data, rounds, "sP", "P")
    finalRel = {}
    for team in TEAMS:
        s = relP[team]
        if len(s) < 4:
            continue
        traj = kalman_1d([(rd, o / 1e3, sd / 1e3) for rd, o, sd in s], q_proc=3.0, r_floor=4.0)
        finalRel[team] = (traj[-1][1], traj[-1][2])
        raw = np.array([o for _, o, _ in s]) / 1e3
        print(f"  {team:>5} [{ENGINE[team]:>9}]: filtered relative P = {traj[-1][1]:+5.1f} "
              f"± {traj[-1][2]:.1f} kW   (raw per-race {raw.min():+.0f}..{raw.max():+.0f})")
    print("\n  pairwise |Δ relative-P_filtered| (kW) — same-engine pair should be SMALLEST:")
    teams = list(finalRel)
    pairs = []
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            a, b = teams[i], teams[j]
            same = ENGINE[a] == ENGINE[b]
            pairs.append((abs(finalRel[a][0] - finalRel[b][0]), a, b, same))
    for gap, a, b, same in sorted(pairs):
        print(f"    {a:>5}-{b:<5}: {gap:4.1f} kW {'  <- SAME ENGINE (MERC/WIL)' if same else ''}")

    # ---- thin-power-track taming (absolute P, widest obs) ----
    print("\n" + "=" * 74)
    print("THIN-POWER-TRACK TAMING (twisty -> wild raw P; filter steadies from prior)")
    print("=" * 74)
    for team in TEAMS:
        series = [(rd, data[rd]["fits"][team]["P"], data[rd]["fits"][team]["sP"])
                  for rd in rounds if team in data[rd]["fits"]]
        if len(series) < 4:
            continue
        traj = {t[0]: t for t in kalman_1d(series, 6e3, 4e3)}
        worst = sorted(series, key=lambda s: -s[2])[:3]
        print(f"  {team:>5}: " + "  |  ".join(
            f"{data[rd]['name'][:14]}: raw {o/1e3:.0f}±{sd/1e3:.0f}->filt {traj[rd][1]/1e3:.0f}±{traj[rd][2]/1e3:.0f}"
            for rd, o, sd in worst))

    # ---- CdA relative-to-field (drag CHARACTER) filtered ----
    print("\n" + "=" * 74)
    print("DRAG CHARACTER: CdA relative-to-field, filtered (RBR low? Merc high?)")
    print("=" * 74)
    relC = rel_series(data, rounds, "sCc", "CdA_c")
    for team in TEAMS:
        s = relC[team]
        if len(s) < 4:
            continue
        traj = kalman_1d(s, q_proc=0.03, r_floor=0.05)
        print(f"  {team:>5}: filtered relative CdA = {traj[-1][1]:+.3f} ± {traj[-1][2]:.3f} m²  "
              f"({'LOW drag' if traj[-1][1] < 0 else 'HIGH drag'})")
    print("\n(known: RBR efficient/low-drag, Merc draggy. does the season filter recover it?)")


if __name__ == "__main__":
    main()
