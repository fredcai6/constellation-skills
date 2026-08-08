"""g4 REVIEWER adversarial probes: hunt for a compliance signal green in BOTH worlds.

Each probe states what a GREEN result would mean before it runs.
"""
import copy, json, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import importlib.util

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467")
ENGINE = ROOT / "scripts" / "checklist_engine.py"
spec = importlib.util.spec_from_file_location("eng", ENGINE)
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)

MODEL = "claude-opus-4-8"
SOFT, HARD = E._gauge_reader.thresholds_for(MODEL)
OVER = min(HARD + 0.05, 1.0)
PASS_CMD = f'"{sys.executable}" -c "import sys; sys.exit(0)"'


def gate(iid, status="pending", why_exempt=False):
    return {"id": iid, "title": iid, "imperative": f"do {iid}", "preconditions": [],
            "postconditions": [{"id": "c1", "statement": "ok",
                                "check": {"kind": "command", "command": PASS_CMD},
                                "satisfied": False}],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": status, "status_detail": {}, "result": None, "finding": None,
            "evidence": [], "rework_count": 0, "why_exempt": why_exempt}


def spine(n=4):
    ts = {f"g{i}": gate(f"g{i}", "in-progress" if i == 1 else "pending") for i in range(1, n + 1)}
    return {"work_id": "adv", "type": "gated", "config": {"rework_cap": 3},
            "items": list(ts), "tasks": ts, "consolidation": None,
            "triage_candidates": [], "blockers": []}


def write_gauge(d, fill, offset_seconds=0):
    ts = (datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)).isoformat()
    (Path(d) / "gauge.json").write_text(json.dumps(
        {"schema_version": 1, "fill_fraction": fill, "model": MODEL, "observed_at": ts}),
        encoding="utf-8")


def cli(f, *a):
    p = subprocess.run([sys.executable, str(ENGINE), "--file", str(f), *a],
                       capture_output=True, text=True, cwd=str(ROOT))
    return p.returncode, p.stdout, p.stderr


def load(f):
    return json.loads(Path(f).read_text(encoding="utf-8"))


def setup(n=4, fill=OVER, offset=0):
    d = tempfile.mkdtemp(); f = Path(d) / "spine.json"
    E.save(f, spine(n)); write_gauge(d, fill, offset)
    return d, f


print(f"hard={HARD} over={OVER}\n")

# --- P1: can a non-compliant agent walk the whole spine using ONLY `advance`? ---
print("P1  Can an agent over the line close gate after gate WITHOUT ever running a begin verb?")
d, f = setup(4)
seq = []
for g in ("g1", "g2", "g3", "g4"):
    rc, out, err = cli(f, "advance", g, "--why", f"still going at {g}")
    cl = load(f)
    seq.append((g, rc, cl["tasks"][g]["status"], len(cl.get("trip_ledger") or []),
                len(E.begin_over_line_records(cl))))
assert len(seq) == 4, seq
for row in seq:
    print(f"    advance {row[0]}: rc={row[1]} status={row[2]} ledger_len={row[3]} signal_len={row[4]}")
final = load(f)
print(f"    -> whole spine closed over the line, ledger key present: "
      f"{'trip_ledger' in final}; compliance signal: {len(E.begin_over_line_records(final))}")
print("    MEANING: `advance` is deliberately NOT a write site (handoff exclusion), so a"
      "\n             runaway that only CLOSES gates leaves no mark. Documented as 'records"
      "\n             BEGINS, not WORK'? -- checked separately against the doc.\n")

# --- P2: does the OFFENDING agent's own next `advance --why` silence the signal? ---
print("P2  After a recorded over-the-line begin, does the SAME agent's next `advance --why`")
print("    silence the rendered compliance signal?")
d, f = setup(4)
cli(f, "advance", "g1", "--why", "u1")
rc, _, _ = cli(f, "start", "g2")                       # refused -> tl-1 (why_ref w-1)
cl = load(f)
sig_before = len(E.begin_over_line_records(cl))
adv_before = E._trip_advisory(cl, Path(d))
cli(f, "attach", "g2", "--type", "refresh-request", "--field", "seam=g2", "--field", "why_ref=w-1")
cli(f, "start", "g2")                                  # released -> tl-2 (why_ref w-1)
cl = load(f); sig_mid = len(E.begin_over_line_records(cl))
cli(f, "advance", "g2", "--why", "u2 -- same agent, carried on anyway")
cl = load(f)
sig_after = len(E.begin_over_line_records(cl))
adv_after = E._trip_advisory(cl, Path(d))
print(f"    ledger entries on disk: {len(cl.get('trip_ledger') or [])}  "
      f"why_trail ids: {[w['id'] for w in cl.get('why_trail', [])]}")
print(f"    signal length: after refusal={sig_before}  after release={sig_mid}  "
      f"after the agent's own next advance={sig_after}")
print(f"    'TRIP LEDGER' rendered before={'TRIP LEDGER' in adv_before}  "
      f"after={'TRIP LEDGER' in adv_after}")
print(f"    durable record still on disk: "
      f"{[(e['id'], e['outcome'], e['why_ref']) for e in cl.get('trip_ledger') or []]}\n")

# --- P3: append-only under reopen's cascade ---
print("P3  Does `reopen`'s cascade (which supersedes EVIDENCE) mutate or drop a ledger entry?")
d, f = setup(4)
cli(f, "advance", "g1", "--why", "u1")
cli(f, "start", "g2")
before = copy.deepcopy(load(f)["trip_ledger"])
cli(f, "attach", "g1", "--type", "refresh-request", "--field", "seam=g1", "--field", "why_ref=w-1")
rc, out, err = cli(f, "reopen", "g1", "--reason", "rework")
after = load(f).get("trip_ledger")
print(f"    reopen rc={rc}; entries before={len(before)} after={len(after)}")
print(f"    prior entry byte-identical: {after[0] == before[0]}  (entries only ever grow: "
      f"{len(after) >= len(before)})\n")

# --- P4: --dry-run must not persist an entry ---
print("P4  Does `start --dry-run` over the line persist an entry?")
d, f = setup(4)
cli(f, "advance", "g1", "--why", "u1")
rc, out, err = cli(f, "start", "g2", "--dry-run")
print(f"    rc={rc}  'trip_ledger' on disk after dry-run: {'trip_ledger' in load(f)}\n")

# --- P5: clock-skewed / future gauge (handoff trap 3) ---
print("P5  A FUTURE observed_at (clock skew) collapses to no reading. Entry? Claim?")
d, f = setup(4, offset=+3600)
cli(f, "advance", "g1", "--why", "u1")
rc, out, err = cli(f, "start", "g2")
cl = load(f)
print(f"    start rc={rc} (0 = not refused, reading discarded)  "
      f"'trip_ledger' present: {'trip_ledger' in cl}")
print(f"    advisory: {E._trip_advisory(cl, Path(d))!r}\n")

# --- P6: a spine with NO why_trail at all (live id is None) ---
print("P6  A spine with NO why_trail: entries carry why_ref=None and live is None.")
d = tempfile.mkdtemp(); f = Path(d) / "spine.json"
s = spine(3)
for t in s["tasks"].values():
    t["why_exempt"] = True          # exempt gates never write a why_trail
E.save(f, s); write_gauge(d, OVER)
cli(f, "advance", "g1", "--mechanical")
rc, _, _ = cli(f, "start", "g2")
cl = load(f)
print(f"    why_trail: {[w.get('id') for w in cl.get('why_trail', [])]}  "
      f"entries: {[(e['id'], e['why_ref']) for e in cl.get('trip_ledger') or []]}")
print(f"    signal length: {len(E.begin_over_line_records(cl))}  "
      f"'TRIP LEDGER' rendered: {'TRIP LEDGER' in E._trip_advisory(cl, Path(d))}\n")

# --- P7: does a NON-dict / garbage ledger crash the read-only path? ---
print("P7  Robustness of the selector against a malformed ledger (it is read on `current`).")
for bad in ([], None, "nope", [None, 3, {"outcome": "begin-refused"}], {"a": 1}):
    cl = spine(2); cl["trip_ledger"] = bad
    try:
        n = len(E.begin_over_line_records(cl))
        print(f"    trip_ledger={bad!r:<45} -> {n}")
    except Exception as exc:
        print(f"    trip_ledger={bad!r:<45} -> RAISED {type(exc).__name__}: {exc}")
print()

# --- P8: is the entry visible to a reader who is NOT over the line? ---
print("P8  Where can a reader see the record when the gauge is back below hard?")
d, f = setup(4)
cli(f, "advance", "g1", "--why", "u1")
cli(f, "start", "g2")
write_gauge(d, max(SOFT - 0.02, 0.0))
rc, out, err = cli(f, "current")
cl = load(f)
print(f"    `current` mentions TRIP LEDGER below hard: {'TRIP LEDGER' in out}")
print(f"    raw trip_ledger still readable in the spine file: "
      f"{[(e['id'], e['outcome']) for e in cl.get('trip_ledger') or []]}")
print("    MEANING: the RECORD is durable in the file; the RENDERED signal is HARD-only "
      "by design (shape 6e).")
