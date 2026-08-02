"""Method-artifact check (#445): is the DRS-CLOSED set (what the CdA fit uses) thin at high speed
at the flagged tracks? Overall top speed can be high (Mexico) while the DRS-CLOSED points top out
low because cars open DRS on the straight — that's a short drag lever arm in the set that matters,
even though vmax looks fine. Compare flagged tracks (Mexico, Singapore) to long-straight controls
(Italian/Monza, Las Vegas).
"""
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import load_session  # noqa: E402
from long_throttle_probe import throttle_av  # noqa: E402
from season_cda_collect import TEAMS  # noqa: E402

# (round, name, flagged?, key teams to spotlight)
PROBES = [(19, "Mexico City", True, ["RBR", "ALF", "WIL"]),
          (15, "Singapore", True, ["RBR"]),
          (14, "Italian", False, ["RBR"]),
          (21, "Las Vegas", False, ["RBR"])]


def stats(v_closed, v_open):
    """High-speed reach of the DRS-closed fit set vs the DRS-open reach."""
    if len(v_closed) == 0:
        return None
    vc = v_closed * 3.6
    vo = v_open * 3.6 if len(v_open) else np.array([np.nan])
    return dict(n=len(vc),
                v95_closed=np.percentile(vc, 95), vmax_closed=vc.max(),
                vmax_open=np.nanmax(vo),
                frac_over280=float(np.mean(vc > 280)),
                frac_over300=float(np.mean(vc > 300)))


def main():
    for rnd, name, flagged, spot in PROBES:
        q = load_session(2023, rnd, "Q")
        tag = "FLAGGED" if flagged else "control"
        print(f"\n=== {name}  ({tag}) ===")
        # field aggregate
        Vc, Vo = [], []
        for team, cars in TEAMS.items():
            v, a, op = throttle_av(q, cars)
            mclosed = (~op) & (a > -2)
            Vc.append(v[mclosed]); Vo.append(v[op])
        Vc = np.concatenate(Vc); Vo = np.concatenate(Vo)
        s = stats(Vc, Vo)
        print(f"  FIELD: n_closed={s['n']:5d}  closed v95={s['v95_closed']:.0f}  "
              f"closed vmax={s['vmax_closed']:.0f}  OPEN vmax={s['vmax_open']:.0f}  "
              f"(closed reaches {s['vmax_closed']-s['vmax_open']:+.0f} vs open)")
        print(f"         frac closed >280={s['frac_over280']*100:.0f}%  >300={s['frac_over300']*100:.0f}%")
        for team in spot:
            v, a, op = throttle_av(q, TEAMS_GET(team, q))
            mclosed = (~op) & (a > -2)
            st = stats(v[mclosed], v[op])
            if st:
                print(f"   {team:>4}: n_closed={st['n']:4d}  closed v95={st['v95_closed']:.0f}  "
                      f"closed vmax={st['vmax_closed']:.0f}  OPEN vmax={st['vmax_open']:.0f}  "
                      f">280={st['frac_over280']*100:.0f}% >300={st['frac_over300']*100:.0f}%")


def TEAMS_GET(team, q):
    return TEAMS[team]


if __name__ == "__main__":
    main()
