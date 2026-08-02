"""Probe (#445): what does FastF1 give us to compute air density, and does the codebase
moist-air model resolve the Mexico altitude artifact?

Checks, for a few representative 2023 rounds:
  - event fields (EventName / Country / Location) for altitude-key resolution
  - weather_data: AirTemp, Humidity, Pressure availability + values
  - density three ways: fixed 1.2 (current), measured-pressure moist-air, ISA-altitude moist-air
"""
import logging
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.preprocessing.trajectory.loaders import enable_cache  # noqa: E402
import fastf1  # noqa: E402


def load_session(year, gp, ses):
    enable_cache("C:/Programs/f1Brainz/outputs/cache")
    s = fastf1.get_session(year, gp, ses)
    s.load(telemetry=False, laps=False, weather=True)
    return s
from src.utils.environment import (  # noqa: E402
    estimate_air_density_kg_m3,
    SPECIFIC_GAS_CONSTANT_DRY_AIR as RD,
    SPECIFIC_GAS_CONSTANT_WATER_VAPOR as RV,
)
from src.evo_predictor.data_adapter import get_circuit_altitude  # noqa: E402

import math


def density_from_measured(pressure_hpa, air_temp_c, humidity_pct):
    """Moist-air density from MEASURED barometric pressure (codebase formula back-half)."""
    p_pa = pressure_hpa * 100.0
    temp_k = air_temp_c + 273.15
    p_sat = 610.78 * math.exp(17.27 * air_temp_c / (air_temp_c + 237.3))
    p_vap = (humidity_pct / 100.0) * p_sat
    p_dry = p_pa - p_vap
    return p_dry / (RD * temp_k) + p_vap / (RV * temp_k)


# round -> (EventName-stripped) for reference; probe a sea-level race, an altitude race, a US race
PROBE = {14: "Italy?", 18: "Qatar?", 20: "Mexico?", 17: "USA-Austin?", 21: "Brazil?"}


def main():
    for r in [14, 16, 17, 18, 19, 20, 21]:
        try:
            q = load_session(2023, r, "Q")
        except Exception as e:
            print(f"round {r}: load fail {e}")
            continue
        ev = q.event
        name = str(ev.get("EventName", "?"))
        country = str(ev.get("Country", "?"))
        location = str(ev.get("Location", "?"))
        gp_key = name.replace(" Grand Prix", "")
        alt_by_name = get_circuit_altitude(gp_key)
        alt_by_country = get_circuit_altitude(country)
        wd = q.weather_data
        at = float(np.nanmedian(wd["AirTemp"])) if wd is not None and "AirTemp" in wd else float("nan")
        hum = float(np.nanmedian(wd["Humidity"])) if wd is not None and "Humidity" in wd else float("nan")
        pres = float(np.nanmedian(wd["Pressure"])) if wd is not None and "Pressure" in wd else float("nan")
        d_fixed = 1.2
        d_meas = density_from_measured(pres, at, hum) if pres == pres and pres > 100 else float("nan")
        alt_use = alt_by_name if alt_by_name else alt_by_country
        d_isa = estimate_air_density_kg_m3(alt_use, at, hum) if at == at else float("nan")
        print(f"\nround {r:>2}: EventName={name!r}")
        print(f"   Country={country!r}  Location={location!r}")
        print(f"   altitude: by_name({gp_key!r})={alt_by_name:.0f}m  by_country({country!r})={alt_by_country:.0f}m")
        print(f"   weather: AirTemp={at:.1f}C  Humidity={hum:.0f}%  Pressure={pres:.1f}hPa")
        print(f"   density: fixed={d_fixed:.3f}  measured-P={d_meas:.3f}  ISA-altitude={d_isa:.3f}  "
              f"(meas/fixed={d_meas/d_fixed:.3f})")


if __name__ == "__main__":
    main()
