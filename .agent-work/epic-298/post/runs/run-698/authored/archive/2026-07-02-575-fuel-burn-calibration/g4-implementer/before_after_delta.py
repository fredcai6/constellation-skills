"""Before/after live delta for the g4 wiring (issue #575).

Picks ONE real dry (year, gp, driver) case and shows how the resolved
calibrated burn rate changes race_mass at the first clean race lap versus the
flat DEFAULT_BURN_PER_LAP_KG=1.8 default. This isolates the numeric effect of
the session_race wiring on the real populated season DB, using the SAME
track_statuses / n_race_laps the loader would build.

Read-only; no telemetry-store / smoother path needed for the delta.
"""
from __future__ import annotations

import sqlite3
import sys

from src.physics.fuel_features import resolve_race_burn_rate
from src.physics.mass_model import DEFAULT_BURN_PER_LAP_KG, race_mass

YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2023
GP = sys.argv[2] if len(sys.argv) > 2 else "Bahrain"
DRIVER = sys.argv[3] if len(sys.argv) > 3 else "VER"
DB = f"data/f1_data_{YEAR}.db"


def _ro(db):
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)


con = _ro(DB)
sid = con.execute(
    "SELECT id FROM sessions WHERE year=? AND gp_name=? AND session_type='R'",
    (YEAR, GP),
).fetchone()[0]
n_race_laps = con.execute(
    "SELECT MAX(lap_number) FROM lap_times WHERE session_id=?", (sid,)
).fetchone()[0]

# First clean lap for the driver (valid, no pit, green).
first_clean = con.execute(
    """
    SELECT MIN(lap_number) FROM lap_times
    WHERE session_id=? AND driver_id=? AND valid_lap=1
      AND pit_in_time IS NULL AND pit_out_time IS NULL AND track_status='1'
    """,
    (sid, DRIVER),
).fetchone()[0]

# Full per-lap track_status vector (index 0 = lap 1), filling gaps with '1'.
rows = con.execute(
    "SELECT lap_number, track_status FROM lap_times WHERE session_id=? AND driver_id=?",
    (sid, DRIVER),
).fetchall()
con.close()

status_map = {int(ln): str(ts) for ln, ts in rows if ts is not None and str(ts) != ""}
all_ts = [status_map.get(i, "1") for i in range(1, n_race_laps + 1)]

resolved, source = resolve_race_burn_rate(YEAR, GP, db_path=DB)

before = race_mass(
    YEAR, GP, int(first_clean), n_race_laps,
    track_statuses=all_ts, burn_per_lap_kg=DEFAULT_BURN_PER_LAP_KG,
)
after = race_mass(
    YEAR, GP, int(first_clean), n_race_laps,
    track_statuses=all_ts, burn_per_lap_kg=resolved,
)

print(f"case            : {YEAR} {GP} {DRIVER}")
print(f"n_race_laps     : {n_race_laps}")
print(f"first_clean_lap : {first_clean}")
print(f"resolved rate   : {resolved:.4f} kg/lap  (source={source})")
print(f"default rate    : {DEFAULT_BURN_PER_LAP_KG:.4f} kg/lap")
print(f"mass_kg[0] BEFORE (flat 1.8) : {before:.4f} kg")
print(f"mass_kg[0] AFTER  (resolved) : {after:.4f} kg")
print(f"delta           : {after - before:+.4f} kg")
