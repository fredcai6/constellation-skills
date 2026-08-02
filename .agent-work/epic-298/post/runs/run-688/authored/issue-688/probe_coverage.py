"""Read-only sizing probe for issue #688 planning (no repo mutation).

Question: how much of the grip fit's rain-flagged session set is actually
"materially wet during the timed running", and would a graded wetness signal
recover coverage on the session types that matter (Q/SQ/S/FP)?
"""
import collections
import sqlite3

for year in (2022, 2023):
    p = f"data/f1_data_{year}.db"
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    print(f"=== {year} ===")
    rows = con.execute(
        """
      SELECT s.session_type,
             COUNT(*) AS n,
             SUM(CASE WHEN f.session_rain_flag=1 THEN 1 ELSE 0 END) AS flagged,
             SUM(CASE WHEN f.wet_lap_fraction IS NOT NULL THEN 1 ELSE 0 END) AS has_frac
      FROM sessions s LEFT JOIN session_surface_features f ON f.session_id=s.id
      GROUP BY s.session_type ORDER BY s.session_type
    """
    ).fetchall()
    for st, n, fl, hf in rows:
        print(
            f"  {st:4s} n={n:4d} rain_flagged={fl or 0:4d} "
            f"wet_lap_fraction_present={hf or 0:4d}"
        )
    rows = con.execute(
        """
      SELECT s.session_type, f.session_rain_flag,
             SUM(CASE WHEN l.compound IN ('INTERMEDIATE','WET') THEN 1 ELSE 0 END)*1.0/COUNT(*),
             COUNT(*)
      FROM sessions s JOIN lap_times l ON l.session_id=s.id
      LEFT JOIN session_surface_features f ON f.session_id=s.id
      GROUP BY s.id
    """
    ).fetchall()
    buckets = collections.Counter()
    for st, flag, wf, laps in rows:
        if flag != 1:
            continue
        if wf is None:
            b = "no-laps"
        elif wf == 0.0:
            b = "0pct-wet-laps"
        elif wf < 0.05:
            b = "lt-5pct"
        elif wf < 0.20:
            b = "5-20pct"
        else:
            b = "ge-20pct"
        buckets[(st, b)] += 1
    print("  rain-flagged sessions bucketed by compound-proxy wet-lap fraction:")
    for (st, b), c in sorted(buckets.items()):
        print(f"    {st:4s} {b:14s} {c}")
    con.close()
