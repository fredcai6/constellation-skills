"""Re-extract node clouds through a PER-SESSION CALIBRATED smoother (#445 wide redo).

All prior envelope extractions used grip_iter's hardcoded StintSmoother(2.0,100,0.3,0.06)
-> chi2_pos=33, chi2_spd=25 (over-trusting meter-noisy position 6x, wrong time offset).
This calibrates each session properly:
  - session_offset()  -> one global inter-stream delta
  - fit_stint_hp()    -> (ell, sf, sig_pos) at the per-channel chi2~=1 target
then re-extracts cornering (v,alat,along,w) + braking (v,alat,decel,w) nodes on the
clean kinematics, reusing the SAME vetted emit logic (aniso/braking emitters).

Outputs: calibrated_aniso_nodes.npz, calibrated_braking_nodes.npz, calibrated_hp.json.
Run:  py calibrated_extract.py sanity   (round 1, 2 drivers, HPs + counts)
      py calibrated_extract.py          (full 22 rounds)
"""
from __future__ import annotations

import json
import logging
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)

import grip_iter as GI  # noqa: E402
from aniso_collect import emit_nodes_aniso  # noqa: E402  (cornering: v,alat,along,w)
from braking_collect import emit_braking  # noqa: E402     (braking:  v,alat,decel,w)
from src.preprocessing.trajectory.smoother import StintSmoother  # noqa: E402
from src.preprocessing.trajectory.calibration import session_offset, fit_stint_hp  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
ANISO = OUT / "calibrated_aniso_nodes.npz"
BRK = OUT / "calibrated_braking_nodes.npz"
HPJSON = OUT / "calibrated_hp.json"
ROUNDS = list(range(1, 23))
CARS = ["VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA", "ALO", "STR",
        "GAS", "OCO", "ALB", "SAR", "TSU", "DEV", "RIC", "LAW", "BOT", "ZHO",
        "MAG", "HUL"]
CAL_CARS = ["VER", "HAM", "LEC", "NOR", "RUS"]
MIN_CORNER, MIN_BRAKE = 25, 25


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def _stream(run):
    return (np.asarray(run["tp"], float), np.asarray(run["X"], float), np.asarray(run["Y"], float),
            np.asarray(run["tc"], float), np.asarray(run["V"], float))


def calibrate(q):
    streams = []
    for c in CAL_CARS:
        runs = GI.H.driver_runs(q, c)
        if runs:
            streams.append(_stream(max(runs, key=lambda r: len(r["X"]))))
    if not streams:
        return None
    delta, _ = session_offset(streams)
    s = max(streams, key=lambda S: len(S[0]))
    hp = fit_stint_hp(s[0], s[1], s[2], s[3], s[4], delta=delta, iters=3)
    if hp is None:
        return None
    hp["delta"] = float(delta)
    return hp


def collect(session, car, ell, sf, sp, delta):
    runs = GI.H.driver_runs(session, car)
    fits, corner, brake = {}, [], []
    for ls, le in GI.flying_windows(session, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = StintSmoother(ell, sf, sp, delta, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"]); fits[key] = ss
        mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
        t = ss.ts[mask]; o = np.argsort(t); t = t[o]
        keep = np.concatenate([[True], np.diff(t) > 1e-9]); t = t[keep]
        X, Y = ss.pos_at(t); v = np.interp(t, run["tc"], run["V"])
        corner += emit_nodes_aniso(t, X, Y, v)
        brake += emit_braking(t, X, Y, v)
    return corner, brake


def sanity():
    q = GI.H.load_session(2023, 1, "Q")
    hp = calibrate(q)
    print(f"Bahrain calibrated HP: ell={hp['ell']:.2f} sf={hp['sf']:.0f} "
          f"sig_pos={hp['sig_pos']:.2f}m delta={hp['delta']:.3f} "
          f"chi2_pos={hp['chi2_pos']:.2f} chi2_spd={hp['chi2_spd']:.2f}")
    for c in ["VER", "HAM"]:
        corner, brake = collect(q, c, hp["ell"], hp["sf"], hp["sig_pos"], hp["delta"])
        cp = np.array(corner); bp = np.array(brake)
        print(f"  {c}: {len(corner)} corner (alat med {np.median(cp[:,1]):.2f}g), "
              f"{len(brake)} brake (decel med {np.median(bp[:,2]):.2f}g)")


def full():
    OUT.mkdir(parents=True, exist_ok=True)
    store_c, store_b, hps, rnames = {}, {}, {}, []
    t_start = time.time()
    for r in ROUNDS:
        t0 = time.time()
        try:
            q = GI.H.load_session(2023, r, "Q")
        except Exception as e:
            log(f"round {r}: LOAD FAILED {e}"); continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        rnames.append(nm)
        hp = calibrate(q)
        if hp is None:
            log(f"round {r:>2} {nm}: CAL FAILED, skip"); continue
        hps[nm] = {k: float(hp[k]) for k in ("ell", "sf", "sig_pos", "delta", "chi2_pos", "chi2_spd")}
        nc = 0
        for c in CARS:
            try:
                corner, brake = collect(q, c, hp["ell"], hp["sf"], hp["sig_pos"], hp["delta"])
            except Exception:
                continue
            if len(corner) >= MIN_CORNER:
                p = np.array(corner)
                store_c[f"v__{nm}__{c}"] = p[:, 0].astype(np.float32)
                store_c[f"alat__{nm}__{c}"] = p[:, 1].astype(np.float32)
                store_c[f"along__{nm}__{c}"] = p[:, 2].astype(np.float32)
                store_c[f"w__{nm}__{c}"] = p[:, 3].astype(np.float32)
                nc += 1
            if len(brake) >= MIN_BRAKE:
                p = np.array(brake)
                store_b[f"v__{nm}__{c}"] = p[:, 0].astype(np.float32)
                store_b[f"alat__{nm}__{c}"] = p[:, 1].astype(np.float32)
                store_b[f"d__{nm}__{c}"] = p[:, 2].astype(np.float32)
                store_b[f"w__{nm}__{c}"] = p[:, 3].astype(np.float32)
        log(f"round {r:>2} {nm:16s} {time.time()-t0:5.0f}s  {nc} cars  "
            f"ell={hp['ell']:.1f} sp={hp['sig_pos']:.1f} d={hp['delta']:.2f} "
            f"X2p={hp['chi2_pos']:.1f} X2s={hp['chi2_spd']:.1f}")
    store_c["rounds"] = np.array(rnames); store_c["cars"] = np.array(CARS)
    store_b["rounds"] = np.array(rnames); store_b["cars"] = np.array(CARS)
    np.savez_compressed(ANISO, **store_c)
    np.savez_compressed(BRK, **store_b)
    HPJSON.write_text(json.dumps(hps, indent=2))
    log(f"wrote {ANISO.name} ({(len(store_c)-2)//4} clouds), {BRK.name} "
        f"({(len(store_b)-2)//4}), {HPJSON.name}  elapsed {time.time()-t_start:.0f}s")


if __name__ == "__main__":
    (sanity if len(sys.argv) > 1 and sys.argv[1] == "sanity" else full)()
