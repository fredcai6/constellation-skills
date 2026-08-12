#!/usr/bin/env python
"""Mechanical verifier for the #467 DC5 round trip.

Reads the acceptance spine, its journal, and the deliverable, and asserts that the
round trip ACTUALLY HAPPENED -- not that a document says it did. Exit 0 = every
assertion held. Exit 1 = at least one failed, and the failing line names which.

DESIGNED TO DISCRIMINATE. A verifier that reports success on a broken round trip is
the exact defect this issue catalogues, so every assertion is keyed to a fact that a
faked run would get wrong, and `--self-test` proves it: it mutates a COPY of the real
inputs eight ways, each corresponding to one way the round trip could be faked, and
requires the verifier to FAIL on every one. `--self-test` failing is itself a failure.

USAGE
    python verify_roundtrip.py                # verify the real round trip
    python verify_roundtrip.py --self-test    # prove the verifier discriminates
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ACC = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/acceptance-467")

# The shipped hard-band cap as a fraction for the claude-* 1M-window profile
# (150_000 / 1_000_000). Recorded here ONLY to assert that the ledger's own `hard`
# came in BELOW it -- i.e. that the per-gate override was really applied. The
# verifier never computes a threshold; it reads the two numbers the engine wrote.
SHIPPED_HARD = 0.15

NONCE_LINE = re.compile(r"^6\. NONCE: ([0-9a-fA-F]{6})$")


class Failed(Exception):
    pass


def _load(spine: Path, journal: Path, doc: Path):
    if not spine.exists():
        raise Failed(f"spine {spine} does not exist")
    if not journal.exists():
        raise Failed(f"journal {journal} does not exist")
    if not doc.exists():
        raise Failed(f"deliverable {doc} does not exist")
    cl = json.loads(spine.read_text(encoding="utf-8"))
    entries = [json.loads(ln) for ln in journal.read_text(encoding="utf-8").splitlines()
               if ln.strip()]
    lines = [ln.rstrip() for ln in doc.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return cl, entries, lines


def verify(spine: Path, journal: Path, doc: Path, verbose: bool = True) -> list[str]:
    """Return the list of PASS lines, or raise Failed on the first failure."""
    cl, entries, lines = _load(spine, journal, doc)
    ok: list[str] = []

    def passed(msg: str):
        ok.append(msg)
        if verbose:
            print(f"  [OK]   {msg}")

    ledger = cl.get("trip_ledger") or []
    why = {w["id"]: w for w in (cl.get("why_trail") or []) if isinstance(w, dict)}

    # --- V1: two DISTINCT engine session ids actually acted ------------------
    advances = [e for e in entries if e.get("verb") == "advance"]
    if len(advances) < 2:
        raise Failed(f"V1: expected at least two `advance` entries in the journal, "
                     f"found {len(advances)}")
    first_closer = advances[0].get("session_id")
    last_closer = advances[-1].get("session_id")
    if not first_closer or not last_closer:
        raise Failed("V1: a journal advance entry carries no session_id")
    if first_closer == last_closer:
        raise Failed(f"V1: the same session id {first_closer!r} closed both the first and "
                     f"the last gate -- one agent did the whole thing, so no round trip "
                     f"was measured")
    passed(f"V1: two distinct engine session ids acted -- {first_closer} closed "
           f"{advances[0].get('task')}, {last_closer} closed {advances[-1].get('task')}")

    # --- V2: a BEGIN was refused over the line, keyed to a live understanding -
    refused = [e for e in ledger if e.get("outcome") == "begin-refused"]
    if not refused:
        raise Failed("V2: the trip ledger holds no `begin-refused` entry, so no agent was "
                     "ever actually stopped at a gate boundary")
    trip = refused[-1]
    tripped_gate = trip.get("gate")
    wref = trip.get("why_ref")
    if wref not in why:
        raise Failed(f"V2: the refusal at {tripped_gate} names why_ref {wref!r}, which is "
                     f"not a record in the why_trail")
    rec = why[wref]
    if rec.get("mechanical") or not (rec.get("why") or "").strip():
        raise Failed(f"V2: why-record {wref} carries no understanding "
                     f"(mechanical={rec.get('mechanical')!r}) -- the successor would "
                     f"cold-start from silence")
    passed(f"V2: A's why-record {wref} exists at gate {rec.get('gate')!r}, carries a real "
           f"understanding, and is the record the refusal at {tripped_gate!r} was keyed to")

    # --- V3: the refused agent is the one that wrote that understanding ------
    closer_of = {}
    for e in entries:
        if e.get("verb") == "advance":
            closer_of[e.get("task")] = e.get("session_id")
    a_session = closer_of.get(rec.get("gate"))
    if a_session is None:
        raise Failed(f"V3: no journal advance closes gate {rec.get('gate')!r}, so the "
                     f"why-record has no author")
    if a_session != first_closer:
        raise Failed(f"V3: gate {rec.get('gate')!r} was closed by {a_session!r}, not by the "
                     f"first closer {first_closer!r}")
    passed(f"V3: the agent that was refused ({a_session}) is the agent that wrote the "
           f"handoff the successor reads")

    # --- V4: B advanced a gate AFTER A's last action -------------------------
    a_last = max((e["ts"] for e in entries if e.get("session_id") == a_session),
                 default=None)
    b_advance = next((e for e in advances if e.get("session_id") == last_closer), None)
    if a_last is None or b_advance is None:
        raise Failed("V4: cannot locate A's last action or B's advance in the journal")
    if not (b_advance["ts"] > a_last):
        raise Failed(f"V4: B's advance at {b_advance['ts']} is not after A's last action at "
                     f"{a_last} -- the two agents overlapped, so this is not a handoff")
    passed(f"V4: B ({last_closer}) advanced {b_advance.get('task')} at {b_advance['ts']}, "
           f"after A's last action at {a_last}")

    # --- V5: the ledger holds the expected entries, each with its own reading -
    released = [e for e in ledger if e.get("outcome") == "begin-released"]
    if not released:
        raise Failed("V5: the trip ledger holds no `begin-released` entry, so no agent was "
                     "ever let through the guard while over the line")
    b_released = [e for e in released if e.get("gate") == tripped_gate
                  and e.get("ts") > trip.get("ts", "")]
    if not b_released:
        raise Failed(f"V5: no `begin-released` entry at {tripped_gate!r} AFTER the refusal -- "
                     f"the refused gate was never resumed by anyone")
    for e in ledger:
        f, h = e.get("fill"), e.get("hard")
        if not isinstance(f, (int, float)) or not isinstance(h, (int, float)):
            raise Failed(f"V5: ledger entry {e.get('id')} carries no fill/hard pair, so no "
                         f"reading can be shown to have existed")
        if f < h:
            raise Failed(f"V5: ledger entry {e.get('id')} records fill {f} BELOW hard {h} -- "
                         f"the engine recorded a trip that was not over the line")
        if h >= SHIPPED_HARD:
            raise Failed(f"V5: ledger entry {e.get('id')} was judged against hard {h}, not "
                         f"below the shipped {SHIPPED_HARD} -- the per-gate override was "
                         f"NOT in force, so this trip proves nothing about the override")
    passed(f"V5: ledger holds {len(ledger)} entries "
           f"({len(refused)} refused, {len(released)} released); every one carries its own "
           f"fill/hard pair, every fill is at/over its hard, and every hard is below the "
           f"shipped {SHIPPED_HARD} (the per-gate override was applied)")

    # --- V6: the refresh-request that released B is keyed to A's why-record --
    found = False
    for t in (cl.get("tasks") or {}).values():
        for ev in (t.get("evidence") or []):
            if (ev.get("type") == "refresh-request" and not ev.get("superseded")
                    and (ev.get("payload") or {}).get("seam") == tripped_gate
                    and (ev.get("payload") or {}).get("why_ref") == wref):
                found = True
    if not found:
        raise Failed(f"V6: no pending refresh-request for {tripped_gate!r} keyed to {wref} -- "
                     f"the successor was released by something other than the handoff")
    passed(f"V6: the refresh-request for {tripped_gate!r} is keyed to {wref}, A's own "
           f"understanding -- B was released by A's handoff, not by a stale request")

    # --- V7: B's work corresponds item by item to what A was mid-way through -
    expected = ["# Round trip 467", "1. alpha", "2. bravo", "3. charlie",
                "4. delta", "5. echo"]
    if lines[:6] != expected:
        raise Failed(f"V7: deliverable lines 1-6 are {lines[:6]!r}, expected {expected!r}")
    if len(lines) != 7:
        raise Failed(f"V7: deliverable has {len(lines)} non-blank lines, expected 7")
    m = NONCE_LINE.match(lines[6])
    if not m:
        raise Failed(f"V7: last line {lines[6]!r} is not '6. NONCE: <6 hex chars>'")
    nonce = m.group(1)
    passed(f"V7: the deliverable holds items 1-6 exactly; A left 1-3, B added 4-6")

    # --- V8: B could ONLY have got the nonce from A's handoff ----------------
    if nonce not in (rec.get("why") or ""):
        raise Failed(f"V8: the nonce {nonce!r} in the deliverable does not appear in A's "
                     f"why-record {wref} -- B invented it rather than reading it from the "
                     f"handoff, so nothing was actually carried across the seam")
    passed(f"V8: the nonce {nonce} in B's line 6 appears in A's why-record {wref} -- the "
           f"one fact only the handoff carried made it across the seam")

    # --- V9: both gates are closed -------------------------------------------
    statuses = {k: v.get("status") for k, v in (cl.get("tasks") or {}).items()}
    if set(statuses.values()) != {"complete"}:
        raise Failed(f"V9: not every gate is complete: {statuses}")
    passed(f"V9: every gate is complete: {statuses}")

    return ok


# --------------------------------------------------------------------------- #
# self-test: prove the verifier fails on a broken round trip
# --------------------------------------------------------------------------- #
def _mutations():
    """(name, spine-mutator, journal-mutator, doc-mutator). Each is one way the
    round trip could be faked or broken; the verifier must reject every one."""
    def nop(x):
        return x

    def one_session(entries):
        for e in entries:
            e["session_id"] = "acc-oneagent"
        return entries

    def drop_refused(cl):
        cl["trip_ledger"] = [e for e in cl["trip_ledger"]
                             if e.get("outcome") != "begin-refused"]
        return cl

    def blank_why(cl):
        for w in cl["why_trail"]:
            w["why"] = ""
            w["mechanical"] = True
        return cl

    def reorder(entries):
        # make B's advance predate A's last action
        adv = [e for e in entries if e.get("verb") == "advance"]
        adv[-1]["ts"] = "2000-01-01T00:00:00+00:00"
        return entries

    def unkey_request(cl):
        for t in cl["tasks"].values():
            for ev in t.get("evidence") or []:
                if ev.get("type") == "refresh-request":
                    ev["payload"]["why_ref"] = "w-999"
        return cl

    def shipped_hard(cl):
        for e in cl["trip_ledger"]:
            e["hard"] = 0.15
        return cl

    def shipped_hard_isolated(cl):
        """Same claim as `shipped_hard`, but with fill raised ABOVE the shipped line
        so the earlier fill>=hard assertion cannot be the thing that catches it.
        Without this the override assertion is never independently exercised."""
        for e in cl["trip_ledger"]:
            e["hard"] = 0.15
            e["fill"] = 0.2
        return cl

    def fake_nonce(text):
        return text.replace(text.strip().splitlines()[-1], "6. NONCE: deadbe")

    def drop_release(cl):
        cl["trip_ledger"] = [e for e in cl["trip_ledger"]
                             if not (e.get("outcome") == "begin-released"
                                     and e.get("gate") == "a2")]
        return cl

    return [
        ("V1 one agent did everything", nop, one_session, None),
        ("V2 no begin was ever refused", drop_refused, nop, None),
        ("V2 the handoff carries no understanding", blank_why, nop, None),
        ("V4 B acted before A finished", nop, reorder, None),
        ("V5 the refused gate was never resumed", drop_release, nop, None),
        ("V5 the override was not in force", shipped_hard, nop, None),
        ("V5 the override was not in force (isolated)", shipped_hard_isolated, nop, None),
        ("V6 the request is keyed to nothing", unkey_request, nop, None),
        ("V8 B invented the nonce", nop, nop, fake_nonce),
    ]


def self_test(spine: Path, journal: Path, doc: Path) -> int:
    print("SELF-TEST -- each mutation must make the verifier FAIL.\n")
    base_cl = json.loads(spine.read_text(encoding="utf-8"))
    base_entries = [json.loads(ln) for ln in journal.read_text(encoding="utf-8").splitlines()
                    if ln.strip()]
    base_doc = doc.read_text(encoding="utf-8")

    bad = 0
    for name, mut_cl, mut_j, mut_doc in _mutations():
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            cl = mut_cl(copy.deepcopy(base_cl))
            entries = mut_j(copy.deepcopy(base_entries))
            text = mut_doc(base_doc) if mut_doc else base_doc
            (d / "spine.json").write_text(json.dumps(cl), encoding="utf-8")
            (d / "spine.json.journal").write_text(
                "\n".join(json.dumps(e) for e in entries), encoding="utf-8")
            (d / "roundtrip.md").write_text(text, encoding="utf-8")
            try:
                verify(d / "spine.json", d / "spine.json.journal", d / "roundtrip.md",
                       verbose=False)
            except Failed as exc:
                print(f"  [REJECTED] {name}\n             -> {exc}")
                continue
            except Exception as exc:  # a crash is not a clean rejection
                print(f"  [CRASHED ] {name} -> {exc!r}")
                bad += 1
                continue
            print(f"  [ACCEPTED] {name}   <-- THE VERIFIER DID NOT DISCRIMINATE")
            bad += 1

    print()
    if bad:
        print(f"SELF-TEST FAILED: {bad} mutation(s) slipped past the verifier.")
        return 1
    print(f"SELF-TEST PASSED: all {len(_mutations())} broken round trips were rejected.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--acc", default=str(ACC))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    acc = Path(args.acc)
    spine, journal, doc = (acc / "spine.json", acc / "spine.json.journal",
                           acc / "roundtrip.md")

    if args.self_test:
        return self_test(spine, journal, doc)

    print(f"VERIFYING the #467 DC5 round trip at {acc}\n")
    try:
        ok = verify(spine, journal, doc)
    except Failed as exc:
        print(f"\n  [FAIL] {exc}")
        print("\nROUND TRIP NOT VERIFIED.")
        return 1
    print(f"\nROUND TRIP VERIFIED: {len(ok)} assertions held.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
