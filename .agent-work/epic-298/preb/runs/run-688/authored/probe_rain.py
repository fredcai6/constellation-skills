"""Read-only probe: how aggressive is the 'any wet sample' rain rule really?

Planning evidence for issue #688. Touches nothing; opens each season DB read-only.
"""
import sqlite3
import sys

YEARS = [2022, 2023, 2024]
TIMED = ("Q", "R", "SQ", "S")


def rain_count(raw):
    if raw is None:
        return 0
    if isinstance(raw, (bytes, bytearray)):
        if not raw:
            return 0
        try:
            return int.from_bytes(raw, "little", signed=True)
        except (ValueError, OverflowError):
            return 0
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


rows_out = []
for year in YEARS:
    path = f"data/f1_data_{year}.db"
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    sessions = con.execute(
        "SELECT id, year, gp_name, session_type, rainfall FROM sessions ORDER BY round_num, id"
    ).fetchall()
    for s in sessions:
        sid = s["id"]
        n_wet_flag = rain_count(s["rainfall"])
        w = con.execute(
            "SELECT COUNT(*) n, SUM(CASE WHEN rainfall IS NOT NULL AND rainfall > 0 THEN 1 ELSE 0 END) wet "
            "FROM weather WHERE session_id=?",
            (sid,),
        ).fetchone()
        n_w, n_wet = int(w["n"] or 0), int(w["wet"] or 0)
        lp = con.execute(
            "SELECT COUNT(*) n, "
            "SUM(CASE WHEN UPPER(COALESCE(compound,'')) IN ('WET','INTERMEDIATE') THEN 1 ELSE 0 END) wet "
            "FROM lap_times WHERE session_id=?",
            (sid,),
        ).fetchone()
        n_l, n_lwet = int(lp["n"] or 0), int(lp["wet"] or 0)
        rows_out.append(
            dict(year=year, gp=s["gp_name"], st=s["session_type"], flag=n_wet_flag,
                 n_w=n_w, n_wet=n_wet, n_l=n_l, n_lwet=n_lwet)
        )
    con.close()

print(f"{'yr':>5} {'session':<34} {'flagN':>6} {'wsamp':>6} {'wet':>5} {'wfrac':>7} {'laps':>6} {'wetlap':>7} {'lfrac':>7}")
n_flagged = n_total = 0
for r in rows_out:
    if r["st"] not in TIMED:
        continue
    n_total += 1
    if r["flag"] > 0:
        n_flagged += 1
    wfrac = (r["n_wet"] / r["n_w"]) if r["n_w"] else float("nan")
    lfrac = (r["n_lwet"] / r["n_l"]) if r["n_l"] else float("nan")
    if r["flag"] > 0:
        print(f"{r['year']:>5} {r['gp'][:26]+'/'+r['st']:<34} {r['flag']:>6} {r['n_w']:>6} "
              f"{r['n_wet']:>5} {wfrac:>7.3f} {r['n_l']:>6} {r['n_lwet']:>7} {lfrac:>7.3f}")

print()
print(f"timed sessions (Q/R/SQ/S) across {YEARS}: {n_total}; any-wet-flagged: {n_flagged} "
      f"({100.0*n_flagged/max(n_total,1):.1f}%)")

# Weekend-level: a weekend is 'dropped' if ANY of its timed sessions is flagged
from collections import defaultdict
wk_any = defaultdict(bool)
wk_frac = defaultdict(float)
for r in rows_out:
    if r["st"] not in TIMED:
        continue
    key = (r["year"], r["gp"])
    if r["flag"] > 0:
        wk_any[key] = True
    else:
        wk_any[key] = wk_any[key]
print(f"weekends with >=1 timed session: {len(wk_any)}; weekends with >=1 any-wet timed session: "
      f"{sum(1 for v in wk_any.values() if v)}")

# What survives at graded thresholds, per timed session
for thr in (0.0, 0.05, 0.10, 0.20, 0.30, 0.50):
    kept = 0
    for r in rows_out:
        if r["st"] not in TIMED:
            continue
        wfrac = (r["n_wet"] / r["n_w"]) if r["n_w"] else 0.0
        if wfrac <= thr:
            kept += 1
    print(f"  weather-sample wet-fraction <= {thr:>4.2f}: {kept:>4}/{n_total} timed sessions kept")
for thr in (0.0, 0.05, 0.10, 0.20, 0.30, 0.50):
    kept = 0
    for r in rows_out:
        if r["st"] not in TIMED:
            continue
        lfrac = (r["n_lwet"] / r["n_l"]) if r["n_l"] else 0.0
        if lfrac <= thr:
            kept += 1
    print(f"  WET/INTER lap-fraction    <= {thr:>4.2f}: {kept:>4}/{n_total} timed sessions kept")
