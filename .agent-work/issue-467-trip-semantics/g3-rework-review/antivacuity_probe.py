"""g3-rework review, criterion 2 + 3: attack the new test for vacuity.

Reads the SHIPPED engine and the SHIPPED test module's own helpers, rebuilds the new
test's fixture, and runs counterfactuals the test itself cannot run. Touches nothing.
Run from the worktree root: python .agent-work/.../antivacuity_probe.py
"""
import importlib.util
import sys
import types
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "t_ce", ROOT / "tests" / "test_checklist_engine.py")
T = importlib.util.module_from_spec(spec)
sys.modules["t_ce"] = T
spec.loader.exec_module(T)

E = T.E
gated, gate, PASS = T.gated, T.gate, T.PASS_COMMAND
RESERVE, MODEL, FILL = 50_000, "claude-opus-5", 0.12


def gauge(fill):
    return mock.patch.object(E, "_read_gauge", return_value=T._reading(fill, MODEL))


def blk(iid):
    return types.SimpleNamespace(verb="block", id=iid, blocker="upstream authority",
                                 authority="human", next_action="wait", session_id=None)


def fixture(do_block=True):
    cl = gated(g1=gate("g1", "pending", command=PASS, why_exempt=True),
               g2=gate("g2", "pending", command=PASS, why_exempt=True))
    cl["tasks"]["g2"]["context_headroom_tokens"] = RESERVE
    with gauge(0.0):
        E.dispatch(cl, T._start_ns("g1"), base_dir=Path("."))
        E.dispatch(cl, T._advance_ns("g1"), base_dir=Path("."))
        E.dispatch(cl, T._start_ns("g2"), base_dir=Path("."))
        if do_block:
            E.dispatch(cl, blk("g1"), base_dir=Path("."))
    return cl


def try_advance(cl, fill):
    with gauge(fill):
        try:
            return "CLOSED: " + E.dispatch(cl, T._advance_ns("g2", mechanical=True),
                                           base_dir=Path("."))
        except E.EngineError as exc:
            return "REFUSED: " + str(exc)[:90]


print("P1  reachability of the divergent state through PUBLIC verbs only")
cl = fixture()
print("    statuses            :", {k: v["status"] for k, v in cl["tasks"].items()})
print("    active_id(cl)       :", E.active_id(cl), " <- gate being CLOSED is g2")
print("    engine invariant chk:", E.validate(cl) if hasattr(E, "validate") else "n/a")

print()
print("P2  the two readings the mutation chooses between, in that state, at fill=0.12")
with gauge(FILL):
    named = E._trip_hard_band_reading(cl, Path("."), "g2")     # shipped
    active = E._trip_hard_band_reading(cl, Path("."))          # M15 mutant
print("    shipped  (gate='g2'):", "Reading -> require_why" if named else "None")
print("    mutant   (no gate)  :", "Reading -> require_why" if active else "None")

print()
print("P3  counterfactual: SAME fixture WITHOUT the block (active_id == g2, no divergence)")
cl_nb = fixture(do_block=False)
print("    statuses            :", {k: v["status"] for k, v in cl_nb["tasks"].items()})
print("    active_id(cl)       :", E.active_id(cl_nb))
with gauge(FILL):
    n2 = E._trip_hard_band_reading(cl_nb, Path("."), "g2")
    a2 = E._trip_hard_band_reading(cl_nb, Path("."))
print("    shipped  (gate='g2'):", "Reading" if n2 else "None",
      "| mutant (no gate):", "Reading" if a2 else "None",
      "  <- identical, so a no-block fixture kills NOTHING")
print("    advance g2 --mechanical:", try_advance(cl_nb, FILL)[:60])

print()
print("P4  is the gauge reading LIVE in the assertion window?")
print("    fill=0.12 ->", try_advance(fixture(), FILL)[:70])
print("    fill=0.00 ->", try_advance(fixture(), 0.0)[:70])
print("    fill=0.99 ->", try_advance(fixture(), 0.99)[:70])

print()
print("P5  is the refusal the NO-SILENT-CLOSE rule, or some unrelated refusal?")
cl2 = fixture()
with gauge(FILL):
    try:
        E.dispatch(cl2, T._advance_ns("g2", mechanical=True), base_dir=Path("."))
        print("    mechanical close: NOT REFUSED")
    except E.EngineError as exc:
        print("    mechanical close REFUSED:", str(exc)[:120])
cl3 = fixture()
with gauge(FILL):
    ns = T._advance_ns("g2")
    ns.why = "I understand the state of g2 and here is the handoff for the next agent."
    try:
        print("    close WITH --why:", E.dispatch(cl3, ns, base_dir=Path(".")))
    except E.EngineError as exc:
        print("    close WITH --why REFUSED:", str(exc)[:120])

print()
print("P6  no-reserve control: same shape, but g2 carries NO override")
cl4 = gated(g1=gate("g1", "pending", command=PASS, why_exempt=True),
            g2=gate("g2", "pending", command=PASS, why_exempt=True))
with gauge(0.0):
    E.dispatch(cl4, T._start_ns("g1"), base_dir=Path("."))
    E.dispatch(cl4, T._advance_ns("g1"), base_dir=Path("."))
    E.dispatch(cl4, T._start_ns("g2"), base_dir=Path("."))
    E.dispatch(cl4, blk("g1"), base_dir=Path("."))
print("    active_id:", E.active_id(cl4), "| advance g2 --mechanical:",
      try_advance(cl4, FILL)[:60])
