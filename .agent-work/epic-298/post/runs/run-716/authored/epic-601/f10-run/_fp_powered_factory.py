# scripts/_fp_powered_factory.py
"""Zero-arg GateExtractor factory for the powered F10 held-out run (#513 Phase 4 G7,
epic #601 handoff `.agent-work/epic-601/powered-f10-run-handoff.md`).

Bakes the run's fixed configuration into a zero-arg callable so
``scripts/fp_representativeness_gate.py --extractor scripts._fp_powered_factory:make_powered_extractor``
can dynamic-import it (the CLI's ``_load_extractor`` calls the factory with no args).

Configuration (handoff-mandated):
  * year=2023, the FROZEN 16-weekend split (``fp_gate.FROZEN_2023_WEEKENDS``).
  * db_path=data/f1_data_2023.db (read-only; NEVER written).
  * sessions=(FP1, FP2, FP3) -- the full FP set, not just FP2/FP3.
  * max_drivers=None -- apex_pace needs the FULL FIELD for a valid cross-car regression.
  * max_laps_per_driver=3 -- the fastest-K compute-reduction lever (handback-sanctioned:
    fewer laps, still enough on-limit apexes) that turns ~37h into the targeted ~5-10h.

Does NOT modify fp_gate.py / fp_gate_real_extractor.py -- both are frozen/reused verbatim.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.physics.layer2.fp_gate import FROZEN_2023_WEEKENDS  # noqa: E402
from src.physics.layer2.fp_gate_real_extractor import make_extractor  # noqa: E402


def make_powered_extractor():
    """Zero-arg factory -- the ONE real extractor config for the powered F10 run."""
    return make_extractor(
        year=2023,
        weekends=FROZEN_2023_WEEKENDS,
        db_path=str(REPO / "data" / "f1_data_2023.db"),
        sessions=("FP1", "FP2", "FP3"),
        max_drivers=None,
        max_laps_per_driver=3,
    )
