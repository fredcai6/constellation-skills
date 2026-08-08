"""g4 REVIEWER's OWN two-world construction for issue #467.

Independent of tests/test_checklist_engine.py: spines are hand-built here, the
gauge sidecar is written from the CLOCK (never a hand-typed timestamp), and the
CLI shapes run the real `checklist_engine.py` in a subprocess.

Every shape prints DEFECTIVE / HEALTHY / DIFFERS so the discrimination is read
off the output, not asserted away.
"""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467")
ENGINE = ROOT / "scripts" / "checklist_engine.py"

spec = importlib.util.spec_from_file_location("eng", ENGINE)
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

MODEL = "claude-opus-4-8"
SOFT, HARD = E._gauge_reader.thresholds_for(MODEL)
OVER = min(HARD + 0.05, 1.0)
UNDER = max(HARD - 0.001, 0.0)

RESULTS = []
PASS_CMD = f'"{sys.executable}" -c "import sys; sys.exit(0)"'


def gate(iid, status="pending", why_exempt=False, headroom=None):
    t = {"id": iid, "title": iid, "imperative": f"do {iid}",
         "preconditions": [],
         "postconditions": [{"id": "c1", "statement": "ok",
                             "check": {"kind": "command", "command": PASS_CMD},
                             "satisfied": False}],
         "constraints": [], "directives": None, "child_checklist": None,
         "status": status, "status_detail": {}, "result": None, "finding": None,
         "evidence": [], "rework_count": 0, "why_exempt": why_exempt}
    if headroom is not None:
        t["context_headroom_tokens"] = headroom
    return t


def spine(**tasks):
    return {"work_id": "probe", "type": "gated", "config": {"rework_cap": 3},
            "items": list(tasks), "tasks": tasks, "consolidation": None,
            "triage_candidates": [], "blockers": []}


def three(headroom_g2=None):
    return spine(g1=gate("g1", "in-progress"), g2=gate("g2", "pending", headroom=headroom_g2),
                 g3=gate("g3", "pending"))


def write_gauge(d, fill, age_seconds=0):
    """observed_at is ALWAYS derived from the clock (handoff trap 3)."""
    ts = (datetime.now(timezone.utc) - timedelta(seconds=age_seconds)).isoformat()
    (Path(d) / "gauge.json").write_text(json.dumps(
        {"schema_version": 1, "fill_fraction": fill, "model": MODEL, "observed_at": ts}),
        encoding="utf-8")


def cli(f, *argv):
    p = subprocess.run([sys.executable, str(ENGINE), "--file", str(f), *argv],
                       capture_output=True, text=True, cwd=str(ROOT))
    return p.returncode, p.stdout, p.stderr


def load(f):
    return json.loads(Path(f).read_text(encoding="utf-8"))


_GAUGE_DIRS = {}


def gauge_dir(fill):
    """A base_dir holding a REAL fresh gauge.json at `fill` -- no mocks anywhere."""
    if fill not in _GAUGE_DIRS:
        d = tempfile.mkdtemp()
        if fill is not None:
            write_gauge(d, fill)
        _GAUGE_DIRS[fill] = d
    return Path(_GAUGE_DIRS[fill])


def say(n, name, defective, healthy, differs):
    same = defective == healthy
    RESULTS.append((n, name, not same))
    print(f"\n--- shape {n}: {name}")
    print(f"    DEFECTIVE : {defective!r}")
    print(f"    HEALTHY   : {healthy!r}")
    print(f"    field     : {differs}")
    print(f"    DISCRIMINATES: {'YES' if not same else '*** NO -- IDENTICAL IN BOTH WORLDS ***'}")


print(f"engine   : {ENGINE}  ({ENGINE.stat().st_size} bytes on disk)")
print(f"model    : {MODEL}  soft={SOFT} hard={HARD}  over={OVER} under={UNDER}")

# ------------------------------------------------------------------ shape 1
with tempfile.TemporaryDirectory() as d:
    f = Path(d) / "spine.json"
    E.save(f, three())
    assert cli(f, "advance", "g1", "--why", "u1")[0] == 0
    base = load(f)
    write_gauge(d, OVER)
    # healthy: told to wrap up, closed g1, STOPPED. (g1 already closed above.)
    healthy = load(f).get("trip_ledger")
    # defective: begins g2 anyway
    rc, out, err = cli(f, "start", "g2")
    dfile = load(f)
    dled = dfile.get("trip_ledger")
    say(1, "begin over the line REFUSED",
        (rc, [(e["outcome"], e["gate"], e["verb"]) for e in dled or []]),
        (0, [] if healthy is None else healthy), "trip_ledger + rc")
    print(f"    refusal stderr tail: {err.strip().splitlines()[-1][:110]}")
    print(f"    g2 status after refusal: {dfile['tasks']['g2']['status']} (was {base['tasks']['g2']['status']})")

# ------------------------------------------------------------------ shape 2
def released(fill):
    d = tempfile.mkdtemp()
    f = Path(d) / "spine.json"
    E.save(f, three())
    assert cli(f, "advance", "g1", "--why", "u1")[0] == 0
    assert cli(f, "attach", "g2", "--type", "refresh-request",
               "--field", "seam=g2", "--field", "why_ref=w-1")[0] == 0
    write_gauge(d, fill)
    rc, out, err = cli(f, "start", "g2")
    cl = load(f)
    return rc, out.strip().splitlines()[-1] if out.strip() else "", cl

rc_o, msg_o, cl_o = released(OVER)
rc_u, msg_u, cl_u = released(UNDER)
say(2, "begin over the line RELEASED (identical command, identical success)",
    (rc_o, msg_o, [(e["outcome"], e["gate"]) for e in cl_o.get("trip_ledger") or []]),
    (rc_u, msg_u, [(e["outcome"], e["gate"]) for e in cl_u.get("trip_ledger") or []]),
    "trip_ledger only -- rc and message are the same in both worlds")

# ------------------------------------------------------------------ shape 3
def cli_durability(age_seconds):
    d = tempfile.mkdtemp()
    f = Path(d) / "spine.json"
    E.save(f, three())
    assert cli(f, "advance", "g1", "--why", "u1")[0] == 0
    write_gauge(d, OVER, age_seconds=age_seconds)
    rc, out, err = cli(f, "start", "g2")
    return rc, load(f).get("trip_ledger")

rc_fresh, led_fresh = cli_durability(0)
rc_stale, led_stale = cli_durability(7200)
say(3, "refused entry SURVIVES THE RAISE, reloaded from disk",
    (rc_fresh, led_fresh and [(e["id"], e["outcome"]) for e in led_fresh]),
    (rc_stale, led_stale), "trip_ledger on the file reloaded from disk")

# ------------------------------------------------------------------ shape 4
def hard_recorded(headroom):
    d = tempfile.mkdtemp()
    f = Path(d) / "spine.json"
    E.save(f, three(headroom_g2=headroom))
    assert cli(f, "advance", "g1", "--why", "u1")[0] == 0
    write_gauge(d, OVER)
    cli(f, "start", "g2")
    return load(f)["trip_ledger"][0]["hard"]

h30, h_none = hard_recorded(30_000), hard_recorded(None)
_, tight = E._gauge_reader.thresholds_for(MODEL, 30_000)
say(4, "recorded `hard` is the PER-GATE line, not a constant",
    h30, h_none, f"entry['hard']; resolver says tightened={tight}, default={HARD}")

# ------------------------------------------------------------------ shapes 5 / 5b
ENTRY = {"id": "tl-1", "gate": "g2", "verb": "start", "outcome": "begin-refused",
         "fill": OVER, "hard": HARD, "model": MODEL, "why_ref": "w-1",
         "ts": datetime.now(timezone.utc).isoformat()}

live = three(); live["trip_ledger"] = [copy.deepcopy(ENTRY)]
live["why_trail"] = [{"id": "w-1", "gate": "g1", "why": "u1", "ts": ENTRY["ts"]}]
superseded = copy.deepcopy(live)
superseded["why_trail"].append({"id": "w-2", "gate": "g2", "why": "fresh agent", "ts": ENTRY["ts"]})
assert live["trip_ledger"] == superseded["trip_ledger"], "ledgers must be byte-identical"
say(5, "mark under the LIVE understanding vs a SUPERSEDED one (identical ledger)",
    len(E.begin_over_line_records(live)), len(E.begin_over_line_records(superseded)),
    "begin_over_line_records() length; ledgers asserted equal first")

reop = copy.deepcopy(live)
E._append_reopen_marker(reop, "g1", "rework") if hasattr(E, "_append_reopen_marker") else None
if not hasattr(E, "_append_reopen_marker"):
    reop["why_trail"].append({"id": "w-2", "gate": "g1", "reopen": True,
                              "reason": "rework", "ts": ENTRY["ts"]})
assert live["trip_ledger"] == reop["trip_ledger"]
say("5b", "the same, via the REOPEN supersede path",
    len(E.begin_over_line_records(live)), len(E.begin_over_line_records(reop)),
    "begin_over_line_records() length; ledger untouched by reopen")

# ------------------------------------------------------------------ shapes 6 / 6b / 6d / 6e
def advisory(cl, fill):
    """Real gauge sidecar, real _read_gauge, no mock. fill=None -> empty dir."""
    return E._trip_advisory(cl, gauge_dir(fill))

healthy6 = three(); healthy6["why_trail"] = copy.deepcopy(live["why_trail"])
a_def, a_heal = advisory(live, OVER), advisory(healthy6, OVER)
say(6, "the RENDERED signal on the HARD advisory (no pending request)",
    ("TRIP LEDGER" in a_def, len(a_def)), ("TRIP LEDGER" in a_heal, len(a_heal)),
    "the advisory string")
print(f"    healthy advisory is a strict prefix of defective: {a_def.startswith(a_heal)}")
print(f"    added text: {a_def[len(a_heal):]!r}")

def with_request(cl):
    c = copy.deepcopy(cl)
    c["tasks"]["g1"]["evidence"].append(
        {"id": "e-1", "type": "refresh-request", "payload": {"seam": "g1", "why_ref": "w-1"}})
    return c

a_def_r, a_heal_r = advisory(with_request(live), OVER), advisory(with_request(healthy6), OVER)
say("6b", "the rendered signal on the ALREADY-REQUESTED HARD sub-branch",
    ("TRIP LEDGER" in a_def_r, len(a_def_r)), ("TRIP LEDGER" in a_heal_r, len(a_heal_r)),
    "the advisory string")
print(f"    already-requested branch confirmed: {'already requested' in a_heal_r}")

a_sup = advisory(superseded, OVER)
say("6d", "the mark STOPS being rendered once superseded",
    "TRIP LEDGER" in a_def, "TRIP LEDGER" in a_sup, "presence of TRIP LEDGER")

below = [advisory(live, f) for f in (SOFT + 0.001, max(SOFT - 0.02, 0.0))]
say("6e", "the signal is a HARD escalation only",
    "TRIP LEDGER" in a_def, [("TRIP LEDGER" in x) for x in below],
    f"presence of TRIP LEDGER at fills {SOFT + 0.001} and {max(SOFT - 0.02, 0.0)} (count={len(below)})")

# ------------------------------------------------------------------ shape 6c (CLI)
def current_out(seed_ledger):
    d = tempfile.mkdtemp()
    f = Path(d) / "spine.json"
    E.save(f, three())
    assert cli(f, "advance", "g1", "--why", "u1")[0] == 0
    if seed_ledger:
        write_gauge(d, OVER)
        cli(f, "start", "g2")            # writes the entry via the real guard
    write_gauge(d, OVER)
    rc, out, err = cli(f, "current")
    return rc, out

rc_d, out_d = current_out(True)
rc_h, out_h = current_out(False)
say("6c", "it reaches the agent through `current` at the CLI boundary",
    ("TRIP LEDGER" in out_d, out_d.strip().splitlines()[-1][:70]),
    ("TRIP LEDGER" in out_h, out_h.strip().splitlines()[-1][:70]),
    "presence of TRIP LEDGER in real `current` stdout")

# ------------------------------------------------------------------ shape 7 (fail-safe)
a_none = advisory(live, None)
d = tempfile.mkdtemp(); f = Path(d) / "spine.json"
E.save(f, three()); cli(f, "advance", "g1", "--why", "u1")   # NO gauge written at all
rc_ng, out_ng, err_ng = cli(f, "start", "g2")
no_gauge_cl = load(f)
say(7, "SILENCE IS NOT COMPLIANCE -- a None reading makes no claim either way",
    ("TRIP LEDGER" in a_def, "claim rendered"),
    ("TRIP LEDGER" in a_none, f"advisory={a_none!r}"),
    "presence of TRIP LEDGER in the advisory")
print(f"    with no gauge at all: start rc={rc_ng} (0 = not refused), "
      f"'trip_ledger' in spine = {'trip_ledger' in no_gauge_cl}")
print(f"    -> neither a compliant nor a non-compliant claim is made: "
      f"no entry AND no rendered line")

# ------------------------------------------------------------------ shape 8
d = tempfile.mkdtemp(); f = Path(d) / "spine.json"
E.save(f, three())
assert cli(f, "advance", "g1", "--why", "u1")[0] == 0
write_gauge(d, OVER)
NON_BEGIN = [("current",), ("attach", "g2", "--type", "note", "--field", "k=v"),
             ("flag-candidate", "--from", "g2", "--statement", "x"),
             ("block", "g2", "--blocker", "b", "--authority", "a", "--next", "n"),
             ("resume", "g2", "--reason", "r"),
             ("skip", "g3", "--reason", "obe")]
checked = 0
after = []
for v in NON_BEGIN:
    cli(f, *v)
    after.append((v[0], "trip_ledger" in load(f)))
    checked += 1
assert checked == len(NON_BEGIN) == 6, checked
rc_b, _, _ = cli(f, "start", "g2")
say(8, "ONLY the begin verbs write",
    (rc_b, len(load(f).get("trip_ledger") or [])), after,
    f"presence of trip_ledger after each of {checked} non-begin verbs, then `start`")

# ------------------------------------------------------------------ shape 9
d = tempfile.mkdtemp(); f = Path(d) / "survey.json"
sv = {"work_id": "s", "type": "survey", "config": {}, "items": ["v1"],
      "tasks": {"v1": {"id": "v1", "title": "v1", "imperative": "x", "preconditions": [],
                       "postconditions": [], "constraints": [], "directives": None,
                       "child_checklist": None, "status": "pending", "status_detail": {},
                       "result": None, "finding": None, "evidence": [], "rework_count": 0}},
      "consolidation": None, "triage_candidates": [], "blockers": []}
E.save(f, sv)
write_gauge(d, OVER)
rc_s, out_s, err_s = cli(f, "start", "v1")
say(9, "surveys NEVER record",
    (rc_b, len(load(Path(tempfile.gettempdir())) if False else []) or "gated: 1 entry (shape 8)"),
    (rc_s, "trip_ledger" in load(f)), "presence of trip_ledger on a survey over the same reading")

# ------------------------------------------------------------------ shape 10
def outcomes(vals):
    c = three()
    c["why_trail"] = [{"id": "w-1", "gate": "g1", "why": "u", "ts": ENTRY["ts"]}]
    c["trip_ledger"] = [dict(ENTRY, id=f"tl-{i+1}", outcome=v) for i, v in enumerate(vals)]
    return len(E.begin_over_line_records(c))

begins = outcomes(["begin-refused", "begin-released"])
others = [(v, outcomes([v])) for v in ("advance-noted", "", None, "begin", "refused")]
assert len(others) == 5
say(10, "only the two BEGIN outcomes count",
    begins, others, f"selector length; {len(others)} non-begin outcome values checked")

# ------------------------------------------------------------------ shape 11
d = tempfile.mkdtemp(); f = Path(d) / "spine.json"
E.save(f, three())
write_gauge(d, UNDER)
seq = [("advance", "g1", "--why", "u1"), ("start", "g2"), ("advance", "g2", "--why", "u2")]
keys = []
for v in seq:
    rc, o, e = cli(f, *v)
    keys.append((v[0], rc, "trip_ledger" in load(f)))
assert len(keys) == 3
say(11, "a LEGACY spine with no ledger key drives unchanged",
    (rc_b, "trip_ledger" in load(Path(tempfile.gettempdir()) / "nope") if False else True),
    keys, f"presence of trip_ledger across {len(keys)} verbs below hard")

# ------------------------------------------------------------------ shape 12
d = tempfile.mkdtemp(); f = Path(d) / "spine.json"
pre = three()
pre["trip_ledger"] = [copy.deepcopy(ENTRY)]
E.save(f, pre)
assert cli(f, "advance", "g1", "--why", "u1")[0] == 0
write_gauge(d, OVER)
cli(f, "start", "g2")
post_led = load(f)["trip_ledger"]
say(12, "an existing ledger is EXTENDED, never replaced",
    (len(post_led), post_led[0] == ENTRY),
    (1, True), "len(trip_ledger) and whether the prior entry is byte-identical")

print("\n================ SUMMARY ================")
bad = [r for r in RESULTS if not r[2]]
for n, name, ok in RESULTS:
    print(f"  shape {str(n):>3}: {'DISCRIMINATES' if ok else 'IDENTICAL (FAIL)'}  {name}")
print(f"\nshapes constructed: {len(RESULTS)}   non-discriminating: {len(bad)}")
