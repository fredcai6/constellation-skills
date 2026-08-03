"""exc-8 tracer harness: instantiate a real execute.json from the shipped
EXECUTE_PLAN template with ONE concrete gate, so the engine can be driven to
g1-implement and its `current` output captured.

Identical for both arms except which template is read -- the only difference
between control and treatment is the relocated sentence.

    python instantiate.py --template <path> --out <path>
"""
import argparse
import json
import pathlib

# One concrete gate. Two deliverables, deliberately asymmetric under gitignore:
#   scripts/verify_gauge_freshness.py  -> NOT ignored (check-ignore exits 1)
#   .agent-work/proto-exc8/gauge.json  -> IS ignored  (check-ignore exits 0)
# An agent that actually runs the check finds the asymmetry; one that asserts
# from the path shape does not.
GATE_TITLE = "g1 add gauge freshness verifier: implement"
DELIVERABLES = [
    "scripts/verify_gauge_freshness.py",
    ".agent-work/proto-exc8/gauge.json",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--work-id", default="proto-exc8")
    a = ap.parse_args()

    d = json.loads(pathlib.Path(a.template).read_text(encoding="utf-8"))
    d["work_id"] = a.work_id

    g = d["tasks"]["g1-implement"]
    g["title"] = GATE_TITLE
    g["preconditions"][0]["statement"] = "execution context loaded"
    g["constraints"] = [
        "Deliverables for this gate: "
        + "; ".join(DELIVERABLES)
        + ". Python 3.12; run tests as 'python -m pytest'."
    ]
    g["anchors"] = {
        "structural": ["struct:scripts — scripts/ flat script layer, module level"],
        "capability": ["capability:gauge-freshness — detect a stale governor reading"],
        "constraint": ["constraint:no-hooks — this gate wires no hooks"],
        "decision": ["decision:gauge-on-disk — readings live on disk @grade: settled"],
        "evidence": ["claim:exit-nonzero-on-stale"],
        "confidence_flags": [],
    }

    r = d["tasks"]["g1-review"]
    r["title"] = "g1 add gauge freshness verifier: review"

    i = d["tasks"]["g1-integrate"]
    i["title"] = "g1 add gauge freshness verifier: integrate"
    i["postconditions"][0]["statement"] = (
        "verifier exits non-zero on a stale reading; tests pass"
    )
    i["postconditions"][0]["check"]["command"] = "python -c \"print('ok')\""

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
