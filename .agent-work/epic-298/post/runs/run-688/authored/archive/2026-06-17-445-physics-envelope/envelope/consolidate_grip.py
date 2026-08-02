"""Consolidate the grip channel: one saturating G(v), bounds power-to-ground (#445).

Unify lateral + longitudinal into ONE grip ceiling G(v) (the friction-circle
radius), measured cleanly from lateral apexes (rising ~1.7g -> ~5g plateau;
sustained grip saturates ~5g per driver/tyre). Same G bounds cornering, braking
(~G; direct braking under-reads at 4.2Hz so G is the truer value), and traction.
Power into the ground: P_ground = min(G*g*m*v, P_engine) -- grip caps it at low
speed (excess spins the tyres), engine caps it at high speed.

Saves the consolidated grip channel (G(v) + sigma + provenance) as an artifact.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
G0 = 9.81
MASS = 810.0          # kg (quali); racing ~798+fuel
P_ENGINE = 700e3      # W, 2023 F1 PU usable (~1000 hp gross)
G_SAT = 5.2           # g, sustained-grip saturation

# Pooled VER lateral grip ceiling (90th pct apex), from pool_lateral.py
SPD = np.array([46, 58, 70, 82, 94, 106, 118, 130, 142, 154, 166, 178])       # km/h
CEIL = np.array([1.83, 2.56, 2.50, 2.84, 2.93, 3.38, 4.13, 4.29, 5.01, 4.85, 4.93, 5.51])
LO = np.array([1.82, 2.45, 2.39, 2.76, 2.90, 3.26, 3.95, 4.17, 4.75, 4.73, 4.78, 5.41])
HI = np.array([2.02, 2.62, 2.58, 2.87, 2.96, 3.50, 4.30, 4.38, 5.15, 4.98, 4.99, 5.64])


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def grip_model(v_ms, A, B):
    """G(v) = min(A + B v^2, G_SAT) — mechanical + downforce, saturating."""
    return np.minimum(A + B * v_ms**2, G_SAT)


def main():
    v_ms = SPD / 3.6
    sig = (HI - LO) / 2
    # fit mechanical + downforce on the unsaturated part, weighted by 1/sigma
    popt, pcov = curve_fit(grip_model, v_ms, CEIL, p0=[1.7, 0.002],
                           sigma=sig, absolute_sigma=True, maxfev=10000)
    A, B = popt
    sA, sB = np.sqrt(np.diag(pcov))
    log(f"consolidated grip: mechanical A = {A:.2f}±{sA:.2f} g, "
        f"downforce B = {B:.5f}±{sB:.5f} (g per (m/s)^2), saturation {G_SAT} g")
    v_sat = np.sqrt(max((G_SAT - A) / B, 0)) * 3.6
    log(f"  grip saturates (~{G_SAT}g) at {v_sat:.0f} km/h")

    # save consolidated grip-channel artifact
    artifact = {
        "channel": "grip_ceiling_Gv",
        "form": "G(v) = min(A + B*v^2, G_sat)  [g]; v in m/s",
        "A_mechanical_g": float(A), "A_sigma": float(sA),
        "B_downforce": float(B), "B_sigma": float(sB),
        "G_sat_g": G_SAT,
        "valid_range_kmh": [46, 185],
        "above_range": "physically capped at G_sat (unmeasurable, v^2/R too noisy)",
        "provenance": "pooled VER corner apexes Suzuka+Monaco quali+race (2210), "
                      "90th-pct ceiling; bounds lateral, braking, traction",
        "source_points": {"speed_kmh": SPD.tolist(), "ceiling_g": CEIL.tolist(),
                          "sigma_g": sig.tolist()},
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (OUT / "grip_channel.json").write_text(json.dumps(artifact, indent=2))
    log("saved grip_channel.json")

    # power into the ground
    vv = np.linspace(8, 95, 200)            # m/s (~30-340 km/h)
    Gv = grip_model(vv, A, B)
    P_grip = Gv * G0 * MASS * vv            # W, grip-limited traction power
    P_ground = np.minimum(P_grip, P_ENGINE)
    cross = vv[np.argmin(np.abs(P_grip - P_ENGINE))]
    log(f"\n--- power into the ground ---")
    log(f"  grip-limited below {cross*3.6:.0f} km/h (tyres can't take more than "
        f"grip force); engine-limited ({P_ENGINE/1e3:.0f} kW) above")
    log(f"  e.g. at 80 km/h grip caps traction power at "
        f"{grip_model(80/3.6,A,B)*G0*MASS*(80/3.6)/1e3:.0f} kW "
        f"(< engine {P_ENGINE/1e3:.0f} kW)")
    _plot(v_ms, A, B, vv, Gv, P_grip, P_ground, cross)


def _plot(v_ms, A, B, vv, Gv, P_grip, P_ground, cross):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    # grip ceiling
    ax1.errorbar(SPD, CEIL, yerr=(HI - LO) / 2, fmt="o", color="navy",
                 label="measured lateral ceiling")
    ax1.plot(vv * 3.6, Gv, "r-", lw=2, label=f"G(v)=min({A:.1f}+{B:.4f}v², {G_SAT}g)")
    ax1.axhline(G_SAT, color="gray", ls="--", lw=0.8, label="sustained saturation ~5g")
    ax1.axvline(185, color="k", ls=":", lw=0.8, label="measured limit")
    ax1.set_xlabel("speed (km/h)"); ax1.set_ylabel("grip ceiling G (g)")
    ax1.set_title("Consolidated grip ceiling (bounds cornering, braking, traction)")
    ax1.legend(fontsize=8); ax1.grid(alpha=0.3); ax1.set_ylim(0, 6.5)
    # power to the ground
    ax2.plot(vv * 3.6, P_grip / 1e3, "b-", label="grip-limited traction power G·g·m·v")
    ax2.axhline(P_ENGINE / 1e3, color="firebrick", ls="-", label=f"engine limit {P_ENGINE/1e3:.0f} kW")
    ax2.plot(vv * 3.6, P_ground / 1e3, "k-", lw=2.5, alpha=0.7, label="power into the ground = min")
    ax2.axvline(cross * 3.6, color="gray", ls="--", label=f"crossover {cross*3.6:.0f} km/h")
    ax2.set_xlabel("speed (km/h)"); ax2.set_ylabel("power to ground (kW)")
    ax2.set_title("Grip bounds power put into the ground (low speed) → engine caps (high speed)")
    ax2.legend(fontsize=8); ax2.grid(alpha=0.3)
    fig.tight_layout()
    png = OUT / "consolidate_grip.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
