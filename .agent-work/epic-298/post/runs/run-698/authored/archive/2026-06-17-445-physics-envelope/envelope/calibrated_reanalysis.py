"""Re-run the four grip-axis tests on CALIBRATED node clouds and compare to the
contaminated-HP runs (#445 wide redo).

Reads calibrated_aniso_nodes.npz / calibrated_braking_nodes.npz (per-session chi2~=1
smoother). Builds a magnitude file for the v-term/intercept tests, then drives each
existing (vetted) analysis pointed at the calibrated data. OLD numbers (contaminated
HPs: chi2_pos~33) printed alongside so we see whether any finding moved.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CAL_ANISO = OUT / "calibrated_aniso_nodes.npz"
CAL_BRK = OUT / "calibrated_braking_nodes.npz"
CAL_MAG = OUT / "calibrated_mag_nodes.npz"


def build_mag():
    """g_tot = hypot(alat, along) magnitude file (v,g,w) for v-term / intercept tests."""
    d = np.load(CAL_ANISO, allow_pickle=True)
    store = {}
    for k in d.files:
        if k.startswith("v__"):
            suf = k[3:]
            store[f"v__{suf}"] = d[k].astype(np.float32)
            store[f"g__{suf}"] = np.hypot(d[f"alat__{suf}"], d[f"along__{suf}"]).astype(np.float32)
            store[f"w__{suf}"] = d[f"w__{suf}"].astype(np.float32)
    store["rounds"] = d["rounds"]; store["cars"] = d["cars"]
    np.savez_compressed(CAL_MAG, **store)


def banner(t):
    print("\n\n" + "#" * 80 + f"\n# {t}\n" + "#" * 80)


def main():
    for f in (CAL_ANISO, CAL_BRK):
        if not f.exists():
            print("calibrated cache not ready:", f.name); return
    build_mag()

    banner("1. LATERAL vs MAGNITUDE  (OLD contaminated: teammate gap M.237/L.148, "
           "btwn/within M.74/L.83, R M.53/L.40)")
    import aniso_fit  # noqa: E402
    aniso_fit.CACHE = CAL_ANISO
    aniso_fit.main()

    banner("2. v-TERM  (OLD: shared-C heldout pinball +535%, gap −48% = washout; C sign 50% = DEAD)")
    import vterm_experiment as VT  # noqa: E402
    VT.NODES = CAL_MAG
    VT.main()

    banner("3. PER-CAR INTERCEPT  (OLD: pinball +2.6%, B-gap +174%, A_c teammate gap 0.59g = DEAD)")
    import shape_intercept_experiment as SI  # noqa: E402
    SI.NODES = CAL_MAG
    SI.main()

    banner("4. LONGITUDINAL ellipse  (OLD: B_long noise>signal, corr(B_long,B_lat) +0.18, "
           "drag resid −0.40 = DUD)")
    import aniso_long_fit as AL  # noqa: E402
    AL.BRK = CAL_BRK
    AL.main()


if __name__ == "__main__":
    main()
