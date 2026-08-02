"""ell-sensitivity sweep for the cornering ceiling (epic #445 envelope probe).

fit_stint_hp optimizes held-out POSITION prediction and over-smooths (rails to
ell~5.6, sig_pos~2.1). ell is the ACCELERATION correlation time; the position
likelihood does not pin it. This sweep shows how the cornering ceiling moves
with ell (at two sig_pos), to (a) find the ell giving physical ~4-5g peaks that
rise with speed, (b) quantify how ell-sensitive the whole pointwise approach is.

Validated reference (nesting-oracle test): ell=3.0, sf=100, sig_pos=0.3.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def run_one(runs, ell, sf, sig_pos, delta):
    chunks = []
    for r in runs:
        try:
            ss = H.StintSmoother(ell, sf, sig_pos, delta, iters=2)
            ss.fit(r["tp"], r["X"], r["Y"], r["tc"], r["V"])
        except Exception:
            continue
        chunks.append(H._propagate_nodes(ss))
    if not chunks:
        return None
    out = {k: np.concatenate([c[k] for c in chunks]) for k in chunks[0]}
    env = H.build_envelope(out["v"], out["latm"], out["latm_sd"])
    if not env:
        return None
    peak = max(e["ceil"] for e in env)
    return dict(
        c25=H._interp_ceil(env, 25),
        c45=H._interp_ceil(env, 45),
        c70=H._interp_ceil(env, 70),
        peak=peak,
        sig=float(np.median(out["latm_sd"])),
    )


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    runs = H.driver_runs(session, "VER")
    log(f"VER: {len(runs)} runs")
    delta, sf = 0.06, 100.0
    ells = [0.3, 0.5, 0.8, 1.2, 2.0, 3.0, 5.0]
    print(f"\n{'sig_pos':>7} {'ell':>5} | {'25m/s':>7} {'45m/s':>7} {'70m/s':>7} "
          f"{'PEAK':>7} {'med_sig':>8}   (m/s^2; /9.81 = g)")
    print("-" * 70)
    for sig_pos in [0.3, 2.1]:
        for ell in ells:
            r = run_one(runs, ell, sf, sig_pos, delta)
            if r is None:
                print(f"{sig_pos:7.1f} {ell:5.2f} | (no envelope)")
                continue
            def g(x):
                return f"{x:7.1f}" if x is not None else f"{'--':>7}"
            print(f"{sig_pos:7.1f} {ell:5.2f} | {g(r['c25'])} {g(r['c45'])} "
                  f"{g(r['c70'])} {g(r['peak'])} {r['sig']:8.2f}")
        print()


if __name__ == "__main__":
    main()
