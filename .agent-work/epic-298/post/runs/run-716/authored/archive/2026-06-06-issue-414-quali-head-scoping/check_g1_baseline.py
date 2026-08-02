#!/usr/bin/env python3
"""G1 baseline-reproduction guard for issue-414.

Asserts the regenerated 414 records reproduce the published §7.6.2 same-pairs
numbers within tolerance, via the EXISTING diagnostic (no forked math). This is
the apples-to-apples 'before' guard the scoping study builds on. DB-only,
deterministic, run-package artifact (not production).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RECORDS = _REPO_ROOT / ".agent-work" / "issue-414-quali-head-scoping" / "records"
os.environ.setdefault("QUALI_SAME_PAIRS_RECORDS_DIR", str(_RECORDS))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import scripts.diagnose_quali_same_pairs as sp  # noqa: E402

# (label, actual_getter, lo, hi) tolerance windows around the §7.6.2 figures.
_EXPECT = [
    ("headline race_weekend model", lambda n: n["regimes"]["headline_2018_2024"]["race_weekend"]["model"]["acc"], 0.610, 0.620),
    ("headline recent_history model", lambda n: n["regimes"]["headline_2018_2024"]["recent_history"]["model"]["acc"], 0.775, 0.785),
    ("headline best_across_fp ceiling", lambda n: n["regimes"]["headline_2018_2024"]["race_weekend"]["best_across_fp"]["acc"], 0.804, 0.808),
    ("headline blend_rank ceiling", lambda n: n["regimes"]["headline_2018_2024"]["race_weekend"]["blend_rank"]["acc"], 0.806, 0.810),
    ("EASY(gap>=9) race_weekend model", lambda n: n["regimes"]["headline_2018_2024"]["race_weekend"]["strata_model"]["far (gap>=9)"]["acc"], 0.680, 0.695),
    ("EASY(gap>=9) best_across_fp ceiling", lambda n: n["regimes"]["headline_2018_2024"]["race_weekend"]["strata_best_across_fp"]["far (gap>=9)"]["acc"], 0.934, 0.939),
    ("headline pairs (model)", lambda n: float(n["regimes"]["headline_2018_2024"]["race_weekend"]["model"]["pairs"]), 23862, 23862),
    ("OOS pairs (model)", lambda n: float(n["regimes"]["oos_2025"]["race_weekend"]["model"]["pairs"]), 3352, 3352),
]


def main() -> int:
    numbers = sp.build_numbers()
    ok = True
    print("G1 baseline reproduction check (414 records vs §7.6.2):")
    for label, getter, lo, hi in _EXPECT:
        val = float(getter(numbers))
        passed = lo <= val <= hi
        ok = ok and passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {label} = {val:.4f}  (expect [{lo}, {hi}])")
    if not ok:
        print("BASELINE REPRODUCTION FAILED")
        return 1
    print("BASELINE REPRODUCTION OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
