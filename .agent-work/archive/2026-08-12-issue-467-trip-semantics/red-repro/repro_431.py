#!/usr/bin/env python
"""Disposable RED reproduction for issue #431 -- the Trip HARD deadlock, end to end.

WHAT THIS PROVES (and what it deliberately does NOT)

  #431 is NOT "advance raises". The shipped HARD refusal *releases* as soon as a
  keyed `refresh-request` exists, so a repro whose only evidence is an exception has
  reproduced the wrong thing.

  #431 IS: `advance` is the sole writer of the `why_trail`, and the newest live
  record of that trail IS the `DIGEST:` line a cold successor reads from `current`.
  So the event that forces the handoff (the HARD refusal on `advance`) is the same
  event that prevents the handoff's brief from being written. The successor inherits
  a DIGEST that is stale by exactly one gate: it names the PRE-TRIP understanding,
  not the understanding the tripped agent actually held when it stopped.

  Face A asserts that staleness as an equality, in code, against a counterfactual
  run of the identical spine with no gauge planted -- so the difference is
  attributable to the refusal and to nothing else about the spine's shape.

  Face B shows the second half of the same defect: the HARD guard runs BEFORE the
  postcondition check, so an agent whose gate was not finishable anyway is told only
  "request a refresh" and never learns its real problem.

NO SOURCE CHANGE. This script only runs the unmodified engine at
  <worktree>/scripts/checklist_engine.py
as a subprocess, against throwaway spines under this directory's `scratch/`.
Nothing under scripts/ or tests/ is touched, and this is NOT a pytest case:
#467 rules the repro disposable -- the deadlock is a property of the refusal path
that issue deletes, so it is unreproducible by construction after the fix and must
never be promoted to a regression test.

USAGE (single command rebuilds everything and reproduces both faces):

    python .agent-work/issue-467-trip-semantics/red-repro/repro_431.py --all

Other modes: `--face a`, `--face b`, `--assert-gauge-read`.
Every mode rebuilds its own scratch spine from nothing. Exit 0 = the defect
reproduced and every assertion held. Exit 1 = an assertion failed (read the
transcript; a scoped null, not a broken approach). Transcripts are written next to
this file as `transcript-<mode>.txt`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]                      # .../epic418-a2-467
ENGINE = WORKTREE / "scripts" / "checklist_engine.py"
SCRATCH = HERE / "scratch"

# claude-opus-5 -> gauge_reader._PROFILES (1_000_000, 80_000, 150_000)
# -> soft = 0.08, hard = 0.15. 0.30 is comfortably over HARD; 0.02 is under both.
MODEL = "claude-opus-5"
HARD_FILL = 0.30
BELOW_HARD_FILL = 0.02

# The two understandings the run holds, in order. The whole defect is that a cold
# successor is handed the first one when the agent actually held the second.
PRE_TRIP_WHY = (
    "PRE-TRIP UNDERSTANDING: g1 established the seam contract; the writer is the "
    "only producer and the reader must fail safe to None."
)
CURRENT_WHY = (
    "CURRENT UNDERSTANDING: g2 found the reader's None path is reached from three "
    "distinct failure modes, so the retry belongs in the caller, not the reader."
)

_transcript: list[str] = []


# --------------------------------------------------------------------------- #
# transcript + assertions
# --------------------------------------------------------------------------- #
def say(line: str = "") -> None:
    print(line)
    _transcript.append(line)


def banner(text: str) -> None:
    say()
    say("=" * 78)
    say(text)
    say("=" * 78)


class ReproFailed(AssertionError):
    """An assertion in the repro did not hold. Scoped to this check."""


def check(label: str, condition: bool, detail: str = "") -> None:
    """Assert and say so out loud. A silent pass proves nothing (#467)."""
    mark = "ASSERT OK  " if condition else "ASSERT FAIL"
    say(f"  [{mark}] {label}")
    if detail:
        say(f"              {detail}")
    if not condition:
        raise ReproFailed(f"{label} -- {detail}")


# --------------------------------------------------------------------------- #
# engine driver -- the unmodified HEAD engine, as a subprocess
# --------------------------------------------------------------------------- #
def engine(spine: Path, *args: str, expect_refusal: bool = False) -> tuple[int, str]:
    """Run one engine verb against `spine`. Returns (returncode, combined output).

    Output is captured, echoed into the transcript verbatim, and returned so the
    assertions run against the engine's OWN text -- never a paraphrase of it.
    """
    env = dict(os.environ, NO_COLOR="1", FORCE_COLOR="", PYTHONIOENCODING="utf-8")
    cmd = [sys.executable, str(ENGINE), "--file", str(spine), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, cwd=str(WORKTREE))
    out = (proc.stdout or "") + (proc.stderr or "")
    say(f"$ checklist_engine.py --file {spine.name} {' '.join(args)}")
    for line in out.rstrip("\n").splitlines():
        say(f"| {line}")
    say(f"| (exit {proc.returncode})")
    say()
    if expect_refusal and proc.returncode == 0:
        raise ReproFailed(f"expected a refusal from `{' '.join(args)}`, got exit 0")
    if not expect_refusal and proc.returncode != 0:
        raise ReproFailed(f"unexpected refusal from `{' '.join(args)}`:\n{out}")
    return proc.returncode, out


# --------------------------------------------------------------------------- #
# scratch spine + planted gauge
# --------------------------------------------------------------------------- #
def gate(gid: str, title: str, conds: list[tuple[str, str]]) -> dict:
    return {
        "id": gid, "title": title,
        "imperative": f"Do the {gid} work, then satisfy its postconditions.",
        "preconditions": [],
        "postconditions": [
            {"id": cid, "statement": stmt, "check": None, "satisfied": False}
            for cid, stmt in conds
        ],
        "constraints": [], "directives": None, "child_checklist": None,
        "status": "pending", "status_detail": {}, "result": None,
        "finding": None, "evidence": [], "rework_count": 0,
    }


def build_spine(name: str, g2_conds: list[tuple[str, str]]) -> Path:
    """Create a fresh scratch dir holding ONLY a pending gated spine.

    No gauge yet -- the gauge is planted later, mid-run, exactly like a real
    session whose context fills up while it is part-way through a gate.
    """
    root = SCRATCH / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    spine = root / "spine.json"
    spine.write_text(json.dumps({
        "work_id": f"red-repro-431-{name}",
        "type": "gated",
        "items": ["g1", "g2"],
        "tasks": {
            "g1": gate("g1", "Establish the seam contract",
                       [("c1", "seam contract written")]),
            "g2": gate("g2", "Work the reader's failure modes", g2_conds),
        },
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
    }, indent=2), encoding="utf-8")
    say(f"built scratch spine: {spine}")
    say(f"  (gauge sibling path the engine will resolve: {spine.parent / 'gauge.json'})")
    say()
    return spine


def plant_gauge(spine: Path, fill: float) -> Path:
    """Plant a valid, FRESH gauge record as a SIBLING of `spine`.

    `_gauge_path` resolves the gauge as `Path(spine).parent / "gauge.json"`, so the
    location is not negotiable: anywhere else and `read()` returns None, the
    governor goes silent, and the whole run degrades into the indistinguishable
    silence #467 warns about. Exactly the four required fields, `observed_at` in the
    freshness window (<= 30 min old, <= 2 min in the future).
    """
    path = spine.parent / "gauge.json"
    record = {
        "schema_version": 1,
        "fill_fraction": fill,
        "model": MODEL,
        "observed_at": (datetime.now(timezone.utc) - timedelta(seconds=5))
                       .isoformat().replace("+00:00", "Z"),
    }
    path.write_text(json.dumps(record), encoding="utf-8")
    say(f"planted gauge: {path}")
    say(f"  {json.dumps(record)}")
    say()
    return path


# --------------------------------------------------------------------------- #
# output readers -- parse the engine's OWN text, never our memory of it
# --------------------------------------------------------------------------- #
DIGEST_RE = re.compile(r"^DIGEST: (.*)$", re.MULTILINE)
CONTEXT_HARD_RE = re.compile(r"^CONTEXT (\d+)% \(>= hard\)", re.MULTILINE)
REFRESH_RE = re.compile(r"^REFRESH REQUESTED: (\S+)", re.MULTILINE)


def digest_of(out: str) -> str | None:
    m = DIGEST_RE.search(out)
    return m.group(1).strip() if m else None


def context_hard_line(out: str) -> str | None:
    for line in out.splitlines():
        if CONTEXT_HARD_RE.match(line):
            return line.strip()
    return None


def why_ref_from_current(out: str) -> str | None:
    """The why-record id the live DIGEST came from, as the agent would read it."""
    m = re.search(r"REFRESH REQUESTED: \S+ \(why_ref (w-\d+)\)", out)
    return m.group(1) if m else None


# --------------------------------------------------------------------------- #
# shared prelude: drive g1 to done, then get PART-WAY through g2
# --------------------------------------------------------------------------- #
def drive_to_mid_g2(spine: Path, session: str, satisfy_g2_c1: bool) -> None:
    """Real engine verbs only -- no hand-written end state.

    After this the run is: g1 complete (its `advance` wrote the PRE-TRIP why-record,
    which is now the live DIGEST), g2 in-progress and part-way worked. The agent's
    real understanding has moved on into g2; the trail has not.
    """
    engine(spine, "claim", "--session-id", session,
           "--claimed-by", "repro-431", "--worktree", str(WORKTREE))
    engine(spine, "start", "g1", "--session-id", session)
    engine(spine, "attest", "g1", "--cond", "c1", "--which", "postconditions",
           "--note", "seam contract written", "--session-id", session)
    engine(spine, "advance", "g1", "--why", PRE_TRIP_WHY, "--session-id", session)
    engine(spine, "start", "g2", "--session-id", session)
    if satisfy_g2_c1:
        engine(spine, "attest", "g2", "--cond", "c1", "--which", "postconditions",
               "--note", "reader failure modes enumerated", "--session-id", session)


# --------------------------------------------------------------------------- #
# Face A -- the stale DIGEST at the seam
# --------------------------------------------------------------------------- #
def face_a() -> None:
    banner("FACE A -- the DIGEST a cold successor reads is stale by one gate")
    session = "repro-431-a"
    spine = build_spine("face-a", [("c1", "reader failure modes enumerated")])
    drive_to_mid_g2(spine, session, satisfy_g2_c1=True)

    say("--- context fills up here: plant a fresh at-or-over-HARD reading ---")
    plant_gauge(spine, HARD_FILL)

    say("--- step 1: `current` -- prove the planted reading was actually READ ---")
    _, out_before = engine(spine, "current")
    ctx = context_hard_line(out_before)
    check("the engine printed its own CONTEXT (>= hard) advisory, so the planted "
          "reading was read (no-absence-is-evidence discharged)",
          ctx is not None, f"engine said: {ctx!r}")
    check("the advisory reports the planted fill, not some other number",
          ctx is not None and f"{round(HARD_FILL * 100)}%" in ctx,
          f"planted fill_fraction={HARD_FILL} -> expected '{round(HARD_FILL*100)}%' in {ctx!r}")
    met = re.search(r"^(\d+)/(\d+) met$", out_before, re.MULTILINE)
    check("g2's postconditions are ALL satisfied, so nothing but the gauge can "
          "block this advance",
          met is not None and met.group(1) == met.group(2),
          f"engine's own postcondition tally: {met.group(0)!r}" if met else
          "no 'n/m met' line in `current`")

    say("--- step 2: the agent tries to advance g2 carrying its CURRENT understanding ---")
    _, refusal = engine(spine, "advance", "g2", "--why", CURRENT_WHY,
                        "--session-id", session, expect_refusal=True)
    check("advance g2 is REFUSED by the HARD band",
          "hard limit" in refusal and "request a refresh" in refusal)
    check("the refusal prints the exact remedy command",
          "attach g2 --type refresh-request --field seam=g2 --field why_ref=" in refusal)
    check("the CURRENT understanding the agent tried to record was NOT written",
          CURRENT_WHY not in _read_trail_text(spine),
          "advance is the sole why_trail writer; a refused advance writes nothing")

    say("--- step 3: the agent does EXACTLY what the engine told it to, then stops ---")
    why_id = _live_why_id(spine, session)
    engine(spine, "attach", "g2", "--type", "refresh-request",
           "--field", "seam=g2", "--field", f"why_ref={why_id}",
           "--session-id", session)
    say(f"(the agent filled the engine's `<why-id>` placeholder from the live DIGEST: {why_id})")
    say("(and now it STOPS -- 'hand off now; do not keep working')")
    say()

    say("--- step 4: a COLD SUCCESSOR cold-starts from `current` alone ---")
    _, cold = engine(spine, "current")
    successor_digest = digest_of(cold)
    check("the successor's `current` carries a DIGEST line at all",
          successor_digest is not None)
    check("the successor's `current` shows the refresh request, so it knows a "
          "handoff happened",
          REFRESH_RE.search(cold) is not None,
          f"REFRESH REQUESTED -> {REFRESH_RE.search(cold).group(1) if REFRESH_RE.search(cold) else None}")
    check("the successor is pointed at g2 -- the gate the predecessor was working",
          re.search(r"\bACTIVE\b.*\bg2\b", cold) is not None
          or re.search(r"^g2\b", cold, re.MULTILINE) is not None)

    say()
    say(">>> THE DEFECT (#431), asserted as an equality:")
    say(f"    DIGEST the successor reads : {successor_digest!r}")
    say(f"    PRE-TRIP understanding     : {PRE_TRIP_WHY!r}")
    say(f"    what the agent ACTUALLY held: {CURRENT_WHY!r}")
    say()
    check("the DIGEST a cold successor reads STILL names the PRE-TRIP "
          "understanding -- it is stale by exactly one gate",
          successor_digest == PRE_TRIP_WHY)
    check("the successor is told NOTHING of the understanding the predecessor "
          "actually held when it tripped",
          CURRENT_WHY not in cold)

    say("--- step 5: counterfactual -- the identical spine with NO gauge planted ---")
    say("    (proves the staleness is caused by the refusal, not by the spine shape)")
    cf_spine = build_spine("face-a-counterfactual",
                           [("c1", "reader failure modes enumerated")])
    cf_session = "repro-431-a-cf"
    drive_to_mid_g2(cf_spine, cf_session, satisfy_g2_c1=True)
    engine(cf_spine, "advance", "g2", "--why", CURRENT_WHY, "--session-id", cf_session)
    _, cf_cold = engine(cf_spine, "current")
    cf_digest = digest_of(cf_cold)
    check("with no HARD refusal, the SAME advance writes the CURRENT understanding "
          "and the DIGEST is fresh",
          cf_digest == CURRENT_WHY, f"counterfactual DIGEST: {cf_digest!r}")
    check("so the only difference between fresh and stale is the HARD refusal itself",
          cf_digest != successor_digest,
          f"{cf_digest!r} != {successor_digest!r}")

    say()
    say("FACE A REPRODUCED: the event that forces the handoff is the event that "
        "prevents the handoff's brief from being written.")


def _read_trail_text(spine: Path) -> str:
    """Raw spine text -- used ONLY to assert a NEGATIVE (that a why was never
    written). The engine has no verb that shows an absent record."""
    return spine.read_text(encoding="utf-8")


def _live_why_id(spine: Path, session: str) -> str:
    """The why-record id backing the live DIGEST, as the agent fills the engine's
    `<why-id>` placeholder. Read from the spine's own trail so the repro cannot
    hand the engine an id the engine would not agree with."""
    data = json.loads(spine.read_text(encoding="utf-8"))
    trail = data.get("why_trail") or []
    for entry in reversed(trail):
        if not entry.get("reopen") and not entry.get("mechanical") and entry.get("why"):
            return entry["id"]
    raise ReproFailed("no live why-record in the trail")


# --------------------------------------------------------------------------- #
# Face B -- the HARD refusal masks the agent's real problem
# --------------------------------------------------------------------------- #
def face_b() -> None:
    banner("FACE B -- the HARD refusal hides an unmet postcondition")
    session = "repro-431-b"
    spine = build_spine("face-b", [
        ("c1", "reader failure modes enumerated"),
        ("c2", "retry relocated to the caller and shown green"),
    ])
    # c1 satisfied, c2 deliberately left UNMET: this gate is not finishable.
    drive_to_mid_g2(spine, session, satisfy_g2_c1=True)

    say("--- g2 is in-progress with c2 UNMET. Context fills up. ---")
    plant_gauge(spine, HARD_FILL)

    _, out = engine(spine, "current")
    ctx = context_hard_line(out)
    check("the planted reading was read (engine's own CONTEXT advisory)",
          ctx is not None, f"engine said: {ctx!r}")

    say("--- what the agent IS told ---")
    _, hard_refusal = engine(spine, "advance", "g2", "--why", CURRENT_WHY,
                             "--session-id", session, expect_refusal=True)
    check("the refusal it gets is the HARD-band one",
          "hard limit" in hard_refusal and "request a refresh" in hard_refusal)
    check("the HARD refusal never mentions the unmet postcondition",
          "c2" not in hard_refusal and "retry relocated" not in hard_refusal,
          "the agent is told to hand off, not that its gate was unfinishable")

    say("--- what the agent WOULD have been told, with the gauge below HARD ---")
    plant_gauge(spine, BELOW_HARD_FILL)
    _, out_low = engine(spine, "current")
    check("below HARD, the engine prints no HARD advisory (the governor is quiet, "
          "not absent -- the same file is still there and still read)",
          context_hard_line(out_low) is None)
    _, cond_refusal = engine(spine, "advance", "g2", "--why", CURRENT_WHY,
                             "--session-id", session, expect_refusal=True)
    check("the hidden refusal is the postcondition one",
          "c2" in cond_refusal or "postcondition" in cond_refusal.lower(),
          "this is the agent's REAL problem")
    check("the two refusals are different instructions",
          hard_refusal.strip() != cond_refusal.strip())
    check("and the masking is one-way: the postcondition refusal was reachable "
          "only once the HARD band stopped firing",
          "hard limit" not in cond_refusal)

    say()
    say("HONEST SCOPE of Face B -- what is masked and what is not:")
    check("`current` DOES still list the unmet postcondition even at HARD, so the "
          "masking is scoped to the `advance` REFUSAL path, not to the whole engine",
          "c2 [unmet]" in out,
          "an agent that reads `current` can still see c2; an agent that follows the "
          "refusal's own instruction ('request a refresh, then hand off') acts on the "
          "refusal text and hands off believing context was its only blocker")

    say()
    say("FACE B REPRODUCED: the HARD guard runs before the postcondition check, so "
        "one instruction masks the other.")


# --------------------------------------------------------------------------- #
# gauge-read-only mode (m1 harness check)
# --------------------------------------------------------------------------- #
def assert_gauge_read() -> None:
    banner("HARNESS -- the planted gauge is proved to have been READ")
    session = "repro-431-gauge"
    spine = build_spine("gauge-read", [("c1", "reader failure modes enumerated")])
    drive_to_mid_g2(spine, session, satisfy_g2_c1=True)

    say("--- with NO gauge planted, the engine says nothing about context ---")
    _, silent = engine(spine, "current")
    check("no CONTEXT advisory before the gauge exists",
          context_hard_line(silent) is None)

    say("--- plant it as a SIBLING of the spine and ask again ---")
    plant_gauge(spine, HARD_FILL)
    _, loud = engine(spine, "current")
    ctx = context_hard_line(loud)
    check("the engine now prints its OWN 'CONTEXT <n>% (>= hard)' advisory",
          ctx is not None, f"engine said: {ctx!r}")
    check("the number is the one we planted",
          ctx is not None and f"{round(HARD_FILL * 100)}%" in ctx)
    say()
    say("The reading was read. Silence before / advisory after, same spine, same "
        "session -- so a later 'nothing happened' can never be confused with a "
        "silent governor.")


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--face", choices=["a", "b"])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--assert-gauge-read", action="store_true")
    args = ap.parse_args()

    if args.all:
        mode, steps = "all", [assert_gauge_read, face_a, face_b]
    elif args.assert_gauge_read:
        mode, steps = "gauge-read", [assert_gauge_read]
    elif args.face == "a":
        mode, steps = "face-a", [face_a]
    elif args.face == "b":
        mode, steps = "face-b", [face_b]
    else:
        ap.error("pass --all, --face a, --face b, or --assert-gauge-read")
        return 2

    # Wipe the WHOLE scratch root, not just the per-face dirs: the engine also
    # drops context/mechanical manifest sidecars under `scratch/<work_id>/`, and
    # leaving those behind would make "rebuilt from nothing" untrue.
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)

    say(f"repro_431.py  mode={mode}")
    say(f"engine under test (UNMODIFIED HEAD): {ENGINE}")
    say(f"scratch root (wiped and rebuilt from nothing): {SCRATCH}")

    status = 0
    try:
        for step in steps:
            step()
        banner(f"RESULT: reproduced -- every assertion held (mode={mode})")
    except ReproFailed as exc:
        say()
        say(f"REPRO FAILED (scoped to this check): {exc}")
        banner(f"RESULT: NOT reproduced under these conditions (mode={mode})")
        status = 1
    finally:
        out = HERE / f"transcript-{mode}.txt"
        out.write_text("\n".join(_transcript) + "\n", encoding="utf-8")
        print(f"\ntranscript written: {out}")
    return status


if __name__ == "__main__":
    sys.exit(main())
