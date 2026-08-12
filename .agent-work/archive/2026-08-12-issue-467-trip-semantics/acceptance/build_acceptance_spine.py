#!/usr/bin/env python3
"""Build the SEPARATE acceptance spine for issue #467 DC5 (round trip).

Authored ONCE, before agent A is dispatched, and never edited afterwards --
the gate imperatives are the job file both A and B read, and editing them
between A and B would smuggle a briefing to B. Re-running this refuses if
the spine already exists.

Both gates declare `context_headroom_tokens: 149000`. With the shipped
claude-* profile (window 1_000_000, hard cap 150_000) that puts the per-gate
hard line at 1_000/1_000_000 = 0.001, so ANY real reading is at/over hard.
That is deliberate: it makes the trip fire on the dispatched agent's OWN
LIVE harness-produced reading instead of on a number I planted, and it is
the shipped per-gate override (#467 DC4) doing exactly what it exists for.
"""
import json
import sys
from pathlib import Path

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467")
ACC = ROOT / ".agent-work" / "acceptance-467"
SPINE = ACC / "spine.json"

ENGINE_BLOCK = """HOW TO DRIVE THIS SPINE. Working directory is
C:/Programs/constellation-skills-wt/epic418-a2-467 -- cd there first. Every engine
command has exactly this shape:

  python scripts/checklist_engine.py --file C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/acceptance-467/spine.json <VERB> [ARGS] --session-id <YOUR-SESSION-ID>

YOUR-SESSION-ID is an id you invent RIGHT NOW and reuse for every command you run:
the letters `acc-` followed by six random hexadecimal characters. Do not reuse an id
you find written anywhere, and do not use the harness session id. Your first command
is `claim --session-id <YOUR-SESSION-ID>`; add `--force` only if claim reports the
lease is held by a different id.

LOG EVERYTHING. Append to
C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/acceptance-467/log-<YOUR-SESSION-ID>.txt
the exact command line and the COMPLETE output of EVERY engine command you run,
including the ones the engine refuses. A refusal is data, not a failure: record it
in full and then do what it tells you to do. Never work around a refusal."""

A1 = """ACCEPTANCE ROUND TRIP (issue #467) -- gate a1 of 2.

""" + ENGINE_BLOCK + """

THE WORK FOR a1. Run `start a1`, then create the file
C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/acceptance-467/roundtrip.md
containing exactly these four lines and nothing else:

  # Round trip 467
  1. alpha
  2. bravo
  3. charlie

THE NONCE. Invent a nonce now: six random hexadecimal characters. Write it NOWHERE
on disk -- not in roundtrip.md, not in your log file, not in any other file. It must
exist in exactly one place when you are done: the closing understanding you hand to
the engine in the next step.

CLOSING a1. When the four lines are on disk, close the gate with:

  advance a1 --why "<your understanding>"

Your understanding must state what you completed, that the nonce is <your nonce>,
and what still remains. Write it for an agent that has never seen this run and will
be handed nothing but the engine's `current` output -- that agent is real and it is
next.

THEN STOP. After a1 closes, run `start a2`. If the engine refuses it, run the exact
command its refusal prints, then run `release --session-id <YOUR-SESSION-ID>` and
STOP. Do NOT do gate a2's work, even if you have room. Then report what you did."""

A2 = """ACCEPTANCE ROUND TRIP (issue #467) -- gate a2 of 2, the last gate.

The agent that worked gate a1 is gone. Everything you need is in this output.

""" + ENGINE_BLOCK + """

THE WORK FOR a2. Run `start a2`, then APPEND to the existing file
C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/acceptance-467/roundtrip.md
exactly these three lines, in this order, after the lines already there:

  4. delta
  5. echo
  6. NONCE: <nonce>

<nonce> is the six-hexadecimal-character nonce the previous agent carried in its
closing understanding. It is written in NO file anywhere on disk. Read it out of the
DIGEST line in this output. If you cannot find it there, do not invent one and do
not guess -- stop and report that the digest did not carry it.

Do not alter the heading or lines 1-3.

CLOSING a2. Close with `advance a2 --why "<your understanding>"`, then run
`release --session-id <YOUR-SESSION-ID>`, then report what you did."""


def main() -> int:
    if SPINE.exists():
        print(f"REFUSED: {SPINE} already exists -- the acceptance spine is authored "
              f"once and never re-authored.")
        return 1
    ACC.mkdir(parents=True, exist_ok=True)

    def gate(gid, title, imperative, check_cmd, statement):
        return {
            "id": gid,
            "title": title,
            "imperative": imperative,
            "context_headroom_tokens": 149000,
            "preconditions": [],
            "postconditions": [{
                "id": "c1",
                "statement": statement,
                "check": {"kind": "command", "command": check_cmd},
                "override_policy": {"allowed": False},
                "satisfied": False,
            }],
            "constraints": [],
            "anchors": {},
            "directives": None,
            "child_checklist": None,
            "status": "pending",
            "status_detail": {},
            "result": None,
            "finding": None,
            "evidence": [],
            "rework_count": 0,
        }

    py = ("python C:/Programs/constellation-skills-wt/epic418-a2-467/"
          ".agent-work/acceptance-467/check_gate.py")
    cl = {
        "work_id": "acceptance-467",
        "type": "gated",
        "items": ["a1", "a2"],
        "tasks": {
            "a1": gate("a1", "round trip: first half",
                       A1, py + " a1",
                       "roundtrip.md holds the heading and items 1-3, and nothing more"),
            "a2": gate("a2", "round trip: second half",
                       A2, py + " a2",
                       "roundtrip.md holds items 1-6 with item 6 carrying a 6-hex nonce"),
        },
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
        "why_trail": [],
        "refusals": [],
        "engine_session": None,
        "amendments": [],
    }
    SPINE.write_text(json.dumps(cl, indent=1), encoding="utf-8")
    print(f"wrote {SPINE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
