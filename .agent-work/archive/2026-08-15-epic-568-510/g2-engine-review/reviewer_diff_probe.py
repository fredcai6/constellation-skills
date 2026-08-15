"""Differential sweep: OLD engine (23ed6b70) vs NEW engine (working tree).

The strongest narrowness statement available. Over every reachable state, run the
identical verb against both engines and compare:

  * did the verb RAISE?                    -> must be identical
  * how many ledger entries were appended? -> must be identical
  * the gate's resulting status             -> must be identical
  * the outcome labels                      -> may differ ONLY as
                                              begin-released -> begin-instructed

If any state changes whether a begin is RELEASED (rather than merely how it is
LABELLED), the change is not confined to labelling and the claim is refuted.
"""
import importlib.util
import itertools
import subprocess
import sys
import tempfile
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tmp = Path(tempfile.mkdtemp())
old_src = subprocess.run(["git", "show", "23ed6b70:scripts/checklist_engine.py"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
(tmp / "old_engine.py").write_text(old_src, encoding="utf-8")
# the engine resolves gauge_reader.py as its own file-system sibling, so the
# old copy needs one too, or it silently loads with _gauge_reader = None.
(tmp / "gauge_reader.py").write_text(
    (ROOT / "scripts" / "gauge_reader.py").read_text(encoding="utf-8"), encoding="utf-8")
sys.path.insert(0, str(ROOT / "scripts"))
OLD = load("old_engine", tmp / "old_engine.py")
NEW = load("new_engine", ROOT / "scripts" / "checklist_engine.py")

MODEL = "claude-opus-4-8"
PASS_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(0)"'


def build(E, statuses, why_exempt, kind):
    def task(iid, status):
        t = {"id": iid, "title": iid, "imperative": f"do {iid}",
             "preconditions": [],
             "postconditions": [{"id": "c1", "statement": "tests pass",
                                 "check": {"kind": "command", "command": PASS_COMMAND},
                                 "satisfied": False}],
             "constraints": [], "directives": None, "child_checklist": None,
             "status": status, "status_detail": {}, "result": None, "finding": None,
             "evidence": [], "rework_count": 0, "why_exempt": why_exempt}
        return t
    return {"work_id": "probe", "type": kind, "config": {"rework_cap": 3},
            "items": [i for i, _ in statuses],
            "tasks": {i: task(i, s) for i, s in statuses},
            "consolidation": None, "triage_candidates": [], "blockers": []}


def ns(verb, iid):
    if verb == "start":
        return types.SimpleNamespace(verb="start", id=iid, session_id=None)
    return types.SimpleNamespace(verb="reopen", id=iid, reason="rework", session_id=None)


def one(E, verb, target, astatus, req, wx, band, kind):
    _, hard = E._gauge_reader.thresholds_for(MODEL)
    over, under = min(hard + 0.05, 1.0), max(hard - 0.10, 0.0)
    cl = build(E, [("g1", "complete"), ("g2", astatus), ("g3", "pending")], wx, kind)
    if not wx:
        E._append_why(cl, "g1", "u1 — the understanding in force", False)
    rec = E._latest_why_record(cl)
    wid = rec["id"] if rec else None
    if req == "keyed-at-target":
        E.attach(cl, target, "refresh-request", {"seam": target, "why_ref": wid})
    elif req == "stale-key-at-target":
        E.attach(cl, target, "refresh-request", {"seam": target, "why_ref": "w-stale-999"})
    elif req == "keyed-elsewhere":
        other = "g3" if target != "g3" else "g1"
        E.attach(cl, other, "refresh-request", {"seam": other, "why_ref": wid})

    def reading(fill, observed_at=None):
        return E._gauge_reader.Reading(schema_version=1, fill_fraction=fill, model=MODEL,
                                       observed_at=observed_at or datetime.now(timezone.utc))

    if band == "predates-claim":
        E.claim(cl, "s-probe", "reviewer", ".", {})
        r = reading(over, datetime.now(timezone.utc) - timedelta(hours=2))
    elif band == "over":
        r = reading(over)
    elif band == "under":
        r = reading(under)
    else:
        r = None

    raised = None
    with mock.patch.object(E, "_read_gauge", return_value=r):
        try:
            E.dispatch(cl, ns(verb, target), base_dir=Path("."))
        except E.EngineError as exc:
            raised = type(exc).__name__
    return {
        "raised": raised,
        "n_entries": len(cl.get("trip_ledger", [])),
        "outcomes": tuple(e["outcome"] for e in cl.get("trip_ledger", [])),
        "gates": tuple(cl["tasks"][g]["status"] for g in ("g1", "g2", "g3")),
        "live": len(E.begin_over_line_records(cl)),
        "hist": len(E.begin_over_line_records_historical(cl)),
    }


GRID = list(itertools.product(
    ["start", "reopen"], ["g1", "g2", "g3"], ["pending", "in-progress", "blocked"],
    ["none", "keyed-at-target", "stale-key-at-target", "keyed-elsewhere"],
    [False, True], ["over", "under", "absent", "predates-claim"], ["gated", "survey"]))

structural, relabel, unbranded = [], [], []
for key in GRID:
    o, n = one(OLD, *key), one(NEW, *key)
    if (o["raised"], o["n_entries"], o["gates"]) != (n["raised"], n["n_entries"], n["gates"]):
        structural.append((key, o, n))
    if o["outcomes"] != n["outcomes"]:
        relabel.append((key, o["outcomes"], n["outcomes"]))
        if not all(a == b or (a == "begin-released" and b == "begin-instructed")
                   for a, b in zip(o["outcomes"], n["outcomes"])):
            structural.append((key, o, n))
    if (o["live"], o["hist"]) != (n["live"], n["hist"]):
        unbranded.append((key, (o["live"], o["hist"]), (n["live"], n["hist"])))

print(f"states compared: {len(GRID)}")
print(f"states where RAISE / entry-count / gate-status differ: {len(structural)}")
for s in structural[:5]:
    print("   STRUCTURAL DIFF:", s)
print(f"states where only the OUTCOME LABEL changed: {len(relabel)}")
for r in relabel:
    print("   relabel:", r[0], r[1], "->", r[2])
print(f"states where the compliance selectors changed: {len(unbranded)}")
for u in unbranded:
    print("   de-branded:", u[0], u[1], "->", u[2])

ok = not structural
print("\nVERDICT:", "CONFINED TO LABELLING" if ok else "NOT CONFINED — REFUTED")
sys.exit(0 if ok else 1)
