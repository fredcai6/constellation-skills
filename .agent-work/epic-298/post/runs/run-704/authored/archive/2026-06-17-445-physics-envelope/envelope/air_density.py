"""Per-session air density (#445) — replaces the fixed sea-level RHO=1.2 used in the CdA/drag fits.

The codebase already MODELS moist-air density (src/utils/environment.estimate_air_density_kg_m3:
altitude + air-temp + humidity -> ISA pressure -> moist-air density). We use that physics but
prefer the MEASURED barometric pressure from FastF1 weather, because:
  - it encodes altitude AND the actual race-day conditions (not an ISA-standard atmosphere), and
  - it needs no circuit-name mapping. The name/country altitude lookup is wrong for exactly the
    tracks that matter: "Mexico City" -> 0 m (misses the whole 2240 m!), and the three US races
    share Country="United States" (Austin 265 m vs Las Vegas 610 m) — only Location disambiguates.
Measured-P and ISA-altitude agree to ~1% where both are valid; measured-P is primary, the
ISA-altitude model is the fallback when Pressure is missing.

Why it matters: fixed RHO=1.2 over-states density everywhere (warm air: rho ~1.11-1.17) and badly
at altitude (Mexico City rho ~0.90). Since CdA = 2·m·K/rho is backed out at the wrong (too-high)
density, every car reads too slippery — ~25% at Mexico, a few % elsewhere — a pure environmental
confound on the per-car drag axis. Using real density removes it.
"""
import json
import logging
import math
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)

from src.utils.environment import (  # noqa: E402
    estimate_air_density_kg_m3,
    SPECIFIC_GAS_CONSTANT_DRY_AIR as RD,
    SPECIFIC_GAS_CONSTANT_WATER_VAPOR as RV,
)
from src.evo_predictor.data_adapter import get_circuit_altitude  # noqa: E402

DEFAULT_RHO = 1.2
CACHE_DIR = "C:/Programs/f1Brainz/outputs/cache"
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CACHE = OUT / "session_density.json"
_MEM: dict = {}


def moist_density(pressure_pa: float, air_temp_c: float, humidity_pct: float) -> float:
    """Moist-air density from a known barometric pressure (the codebase moist-air formula).

    Identical physics to estimate_air_density_kg_m3 but takes pressure directly instead of
    deriving it from altitude via the ISA standard atmosphere.
    """
    temp_k = air_temp_c + 273.15
    p_sat = 610.78 * math.exp(17.27 * air_temp_c / (air_temp_c + 237.3))
    p_vap = (humidity_pct / 100.0) * p_sat
    p_dry = pressure_pa - p_vap
    return p_dry / (RD * temp_k) + p_vap / (RV * temp_k)


def _altitude_for(event) -> float:
    """Resolve circuit altitude from a FastF1 event. Location (city) first — it's the only
    reliable discriminator for tracks that share a country (the three US races)."""
    for fld in ("Location", "Country", "EventName"):
        val = str(event.get(fld, "")).replace(" Grand Prix", "").strip()
        alt = get_circuit_altitude(val)
        if alt:
            return alt
    if "Mexico" in str(event.get("EventName", "")):   # mapping misses "Mexico City"
        return 2240.0
    return 0.0


def air_density(year: int, gp, ses: str = "Q") -> float:
    """Per-session air density (kg/m^3). Measured barometric pressure primary, ISA-altitude
    fallback, fixed DEFAULT_RHO last resort. Cached in-memory and on disk (session_density.json)."""
    key = f"{year}|{gp}|{ses}"
    if key in _MEM:
        return _MEM[key]
    if CACHE.exists():
        disk = json.loads(CACHE.read_text())
        if key in disk:
            _MEM[key] = disk[key]
            return disk[key]

    import fastf1
    fastf1.Cache.enable_cache(CACHE_DIR)
    s = fastf1.get_session(year, gp, ses)
    s.load(telemetry=False, laps=False, weather=True)
    ev = s.event
    wd = s.weather_data

    def med(col):
        if wd is not None and col in wd and len(wd):
            v = float(np.nanmedian(wd[col]))
            return v if v == v else float("nan")
        return float("nan")

    at, hum, pres = med("AirTemp"), med("Humidity"), med("Pressure")
    hum_use = hum if hum == hum else 50.0
    if at != at:                                   # no weather at all
        rho, src = DEFAULT_RHO, "fixed"
    elif pres == pres and pres > 100:              # measured barometric pressure (primary)
        rho, src = moist_density(pres * 100.0, at, hum_use), "measured-P"
    else:                                          # ISA-altitude model (fallback)
        rho, src = estimate_air_density_kg_m3(_altitude_for(ev), at, hum_use), "ISA-altitude"
    rho = float(rho)

    _MEM[key] = rho
    disk = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    disk[key] = rho
    CACHE.write_text(json.dumps(disk, indent=2, sort_keys=True))
    print(f"[air_density] {year} {gp} {ses}: rho={rho:.3f} ({src}; "
          f"AirTemp={at:.1f}C Hum={hum_use:.0f}% Pres={pres:.0f}hPa)", flush=True)
    return rho


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for r in range(1, 23):
        try:
            air_density(2023, r, "Q")
        except Exception as e:
            print(f"round {r}: {e}")
