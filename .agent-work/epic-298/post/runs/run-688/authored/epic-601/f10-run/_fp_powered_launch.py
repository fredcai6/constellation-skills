# scripts/_fp_powered_launch.py
"""Thin launch wrapper for the powered F10 held-out run (#513 Phase 4 G7, epic #601).

Reuses ``scripts.fp_representativeness_gate``'s own orchestration (``build_gate_observations``
/ ``run_lowo`` / ``evaluate_gate`` / ``secondary_power_gate`` / ``emergence_audit`` /
``sandbagging_demo`` -- all from the FROZEN ``src.physics.layer2.fp_gate``) and its own
``format_report`` for the human-readable text -- encodes NO extraction or weighting logic of
its own. The CLI (``fp_representativeness_gate.py``) has no ``--out``/JSON/sentinel output;
this wrapper adds exactly that (the handoff's "redirect stdout or an --out-equivalent" +
completion-sentinel ask) as launch plumbing, nothing else.

Writes, always (success or failure -- the Admiral polls the sentinel with a bounded waiter,
so it must appear either way):
  * reports/physics/fp_representativeness_gate_2023_powered.txt  -- the human-readable report
  * reports/physics/fp_representativeness_gate_2023_powered.json -- the full typed verdict
  * .agent-work/epic-601/POWERED_F10_DONE.txt (main repo)        -- PASS/HONEST_NULL/FAILED + numbers
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

MAIN_REPO_AGENT_WORK = Path("C:/Programs/f1Brainz/.agent-work/epic-601")


def _write_sentinel(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument("--weekends", nargs="+", default=None,
                         help="Weekend ids to run LOWO over (default: the FROZEN 16-weekend split).")
    parser.add_argument("--bootstrap-resamples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--sentinel-name", default="POWERED_F10_DONE.txt",
                         help="Filename written under the main repo's .agent-work/epic-601/.")
    parser.add_argument("--report-prefix", default="fp_representativeness_gate_2023_powered",
                         help="Basename (no extension) for reports/physics/<prefix>.{txt,json}.")
    args = parser.parse_args(argv)

    sentinel = MAIN_REPO_AGENT_WORK / args.sentinel_name
    report_txt = REPO / "reports" / "physics" / f"{args.report_prefix}.txt"
    report_json = REPO / "reports" / "physics" / f"{args.report_prefix}.json"

    t0 = time.time()
    try:
        from src.physics.layer2.fp_gate import (
            FROZEN_2023_WEEKENDS,
            build_gate_observations,
            emergence_audit,
            evaluate_gate,
            run_lowo,
            sandbagging_demo,
            secondary_power_gate,
        )
        from scripts._fp_powered_factory import make_powered_extractor
        from scripts.fp_representativeness_gate import format_report

        extractor = make_powered_extractor()
        weekends = list(args.weekends) if args.weekends else list(FROZEN_2023_WEEKENDS)

        weekend_data = build_gate_observations(weekends, extractor, quali_fuel_kg=15.0)
        lowo = run_lowo(weekend_data)
        primary = evaluate_gate(
            weekend_data, lowo, n_resamples=args.bootstrap_resamples, seed=args.seed,
        )
        secondary = secondary_power_gate(
            weekend_data, n_resamples=args.bootstrap_resamples, seed=args.seed + 1000,
        )
        emergence = emergence_audit()
        try:
            sandbag = sandbagging_demo(weekend_data)
        except ValueError:
            sandbag = None

        wall_s = time.time() - t0
        text = format_report(primary, secondary, emergence, sandbag)
        text += f"\n\nwall_seconds={wall_s:.0f} n_weekends={len(weekend_data)}\n"

        report_txt.parent.mkdir(parents=True, exist_ok=True)
        report_txt.write_text(text, encoding="utf-8")

        payload = {
            "primary": dataclasses.asdict(primary),
            "secondary": dataclasses.asdict(secondary),
            "emergence": dataclasses.asdict(emergence),
            "sandbag": dataclasses.asdict(sandbag) if sandbag is not None else None,
            "wall_seconds": wall_s,
            "n_weekends": len(weekend_data),
            "weekends": weekends,
        }
        report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        _write_sentinel(
            sentinel,
            f"POWERED F10 DONE\n"
            f"primary_verdict={primary.verdict}\n"
            f"secondary_verdict={secondary.verdict} (status={secondary.status})\n"
            f"emergence_passes={emergence.passes}\n"
            f"sandbag_passes={sandbag.passes if sandbag is not None else 'N/A'}\n"
            f"wall_seconds={wall_s:.0f}\n"
            f"n_weekends={len(weekend_data)}\n"
            f"report_txt={report_txt}\n"
            f"report_json={report_json}\n",
        )
        print(text)
        return 0
    except Exception as exc:  # noqa: BLE001 -- must still signal completion (FAILED)
        wall_s = time.time() - t0
        tb = traceback.format_exc()
        _write_sentinel(
            sentinel,
            f"POWERED F10 FAILED\n"
            f"error={type(exc).__name__}: {exc}\n"
            f"wall_seconds={wall_s:.0f}\n\n{tb}\n",
        )
        print(tb, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
