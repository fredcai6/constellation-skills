"""Read-only probe: is session_surface_features.wet_lap_fraction populated for non-race sessions?"""
import sqlite3

Q = """SELECT s.session_type st, COUNT(*) n,
 SUM(CASE WHEN ssf.wet_lap_fraction IS NOT NULL THEN 1 ELSE 0 END) have_frac,
 SUM(CASE WHEN ssf.session_rain_flag IS NOT NULL THEN 1 ELSE 0 END) have_flag
 FROM sessions s LEFT JOIN session_surface_features ssf ON ssf.session_id=s.id
 GROUP BY s.session_type ORDER BY s.session_type"""

for year in (2022, 2023, 2024, 2025):
    print(f"=== {year} ===")
    con = sqlite3.connect(f"file:data/f1_data_{year}.db?mode=ro", uri=True)
    try:
        for st, n, hf, hg in con.execute(Q):
            print(f"  {st:<4} sessions={n:>3}  wet_lap_fraction={hf:>3}  session_rain_flag={hg:>3}")
    except sqlite3.OperationalError as exc:
        print("  ", exc)
    con.close()
