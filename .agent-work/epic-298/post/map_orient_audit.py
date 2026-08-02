#!/usr/bin/env python
"""The SECOND WITNESS: did the #304 contract actually fire, and did it fire before source?

WHY THIS EXISTS, AND WHY IT IS NOT A RESCORING
    The frozen extractor's call-level corpus rule credits any call touching `.claude/skills`
    as `skill-corpus` AND NOTHING ELSE. The #304 contract is discharged by invoking
    `~/.claude/skills/constellation-commander/scripts/map_orient.py` — so **the mandated act
    is invisible to the frozen extractor by construction.** That is a property of the
    treatment, not a bug in the extractor, and the extractor is NOT modified.

    So the primary outcome stays exactly what PRE-B measured: `map_before_src`, the boolean
    over genuine `docs/architecture/*` reads, computed by the frozen extractor and reported
    by `discriminate.py`. This script only ADDS a column the primary measure cannot see.

WHY IT RUNS OVER BOTH ARMS
    A column computed only for POST is not comparable to anything. The same code is run over
    PRE-B's archived transcripts, where it should report zero invocations by construction
    (that corpus predates `map_orient.py` entirely). PRE-B is therefore this script's own
    negative control: a non-zero PRE-B count would mean the script is matching noise, and the
    POST column would have to be thrown out with it.

WHAT IT DECIDES
    The pre-registered three-way needs to separate *insufficient* (contract loaded, order did
    not move) from *irrelevant* (contract never reached the agent). `verify_treatment.py`
    proves the Commander LOADED. This proves the contract's own instrument RAN, and whether
    it ran before the first source read — the anchor #304 is built on.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MAP_ORIENT_RE = re.compile(r"map_orient(?:\.py)?\b")

# Anchored to the SAME argv as the `map_orient` match. The earlier form used `[^\n]*?`,
# which is a no-op against `json.dumps` output — that output contains no literal newlines,
# only two-character `\n` escapes — so on a large payload the non-greedy scan could bind a
# subcommand token from an entirely different part of the file.
SUBCOMMAND_RE = re.compile(
    r"map_orient(?:\.py)?[\"'\\ ]+(?:[-\w:/.\\]+[\"'\\ ]+)*?(orient|verify-orientation|verify-frame)\b"
)
VERDICT_RE = re.compile(r"\b(RESOLVED|DEGRADED-NO-MAP|DEGRADED-EMPTY-MAP|DEGRADED-UNPARSEABLE|"
                        r"UNRESOLVABLE-ROOT|FRAME-OK|FRAME-MISSING|FRAME-REFUSED)\b")

# ONLY these tools can RUN anything. Everything else that mentions `map_orient` is talking
# ABOUT the tool, not using it.
EXECUTOR_TOOLS = ("Bash", "PowerShell")
# The one input key that is actually executed. Matching against `json.dumps(input)` counted
# `Read(file_path=".../scripts/map_orient.py")` — a Commander inspecting its own tooling —
# as an orientation invocation, which alone flips *irrelevant* into *insufficient*. Same for
# `Grep(pattern="map_orient")` and for any Write whose CONTENT quotes the spine's gate command.
COMMAND_KEYS = ("command", "cmd")

NO_MAP_ORIENT = "NO-MAP-ORIENT-CALL"
NO_SRC_READ = "NO-SRC-READ"


def events(path: Path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except ValueError:
            continue


def audit(run_dir: Path) -> dict:
    stream = run_dir / "stream.ndjson"
    if not stream.is_file():
        return {"run": run_dir.name, "status": "NOT-CAPTURED", "reason": "no transcript"}

    calls: list[dict] = []
    invocations: list[dict] = []
    mentions: list[dict] = []
    verdicts: list[str] = []
    confirmed: set[int] = set()
    pending: dict[str, int] = {}

    for ev in events(stream):
        if ev.get("type") == "assistant":
            for b in (ev.get("message") or {}).get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                idx = len(calls)
                tool = b.get("name")
                inp = b.get("input") or {}
                calls.append({"index": idx, "tool": tool})

                # An INVOCATION is an executor tool whose executed key names the script.
                command = ""
                if tool in EXECUTOR_TOOLS and isinstance(inp, dict):
                    for key in COMMAND_KEYS:
                        value = inp.get(key)
                        if isinstance(value, str):
                            command = value
                            break
                if command and MAP_ORIENT_RE.search(command):
                    sub = SUBCOMMAND_RE.search(command)
                    invocations.append({
                        "index": idx,
                        "tool": tool,
                        "subcommand": sub.group(1) if sub else "unknown",
                        "command": command[:400],
                    })
                    if b.get("id"):
                        pending[b["id"]] = idx
                elif MAP_ORIENT_RE.search(json.dumps(inp)):
                    # Talking ABOUT the tool: a Read of the script, a Grep for the token, a
                    # Write quoting the gate command. Kept VISIBLE in its own column rather
                    # than fused into the measure — fusing them is what made the first
                    # version of this script able to manufacture a false *insufficient*.
                    mentions.append({"index": idx, "tool": tool,
                                     "excerpt": json.dumps(inp)[:200]})
        elif ev.get("type") == "user":
            for b in (ev.get("message") or {}).get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_result":
                    continue
                if b.get("tool_use_id") not in pending:
                    continue
                text = json.dumps(b.get("content"))
                for m in VERDICT_RE.finditer(text):
                    verdicts.append(f"call{pending[b['tool_use_id']]}:{m.group(1)}")
                    confirmed.add(pending[b["tool_use_id"]])

    # `first_src_read_index` comes from the FROZEN extractor, never recomputed here — the
    # whole point is that this column sits alongside the frozen measure on the same axis.
    order_p = run_dir / "ordering.json"
    first_src = None
    first_map = None
    captured = False
    if order_p.is_file():
        order = json.loads(order_p.read_text(encoding="utf-8"))
        captured = bool(order.get("captured"))
        fs = order.get("first_src_read_index")
        fm = order.get("first_map_read_index")
        first_src = fs if isinstance(fs, int) else None
        first_map = fm if isinstance(fm, int) else None

    # `unknown` is NOT folded into the orient set: a `--help` or `--self-test` call would
    # otherwise set first_map_orient_index and be read as the contract firing.
    orient_calls = [i for i in invocations if i["subcommand"] == "orient"]
    first_orient = orient_calls[0]["index"] if orient_calls else None

    if first_orient is None:
        before_src = NO_MAP_ORIENT
    elif first_src is None:
        before_src = NO_SRC_READ
    else:
        before_src = first_orient < first_src

    return {
        "run": run_dir.name,
        "run_dir": str(run_dir.resolve()),
        "arm": _arm_of(run_dir),
        "status": "ok" if captured else "NOT-CAPTURED",
        "tool_call_count": len(calls),
        "map_orient_invocation_count": len(invocations),
        "map_orient_indices": [i["index"] for i in invocations],
        "map_orient_subcommands": [i["subcommand"] for i in invocations],
        "map_orient_orient_indices": [i["index"] for i in orient_calls],
        # An invocation whose RESULT carried a verdict token actually ran and returned.
        "map_orient_confirmed_by_result": sorted(confirmed),
        "map_orient_verdicts": verdicts,
        # Talking ABOUT the tool. Reported, never counted as use.
        "map_orient_mention_count": len(mentions),
        "map_orient_mentions": mentions,
        "first_map_orient_index": first_orient if first_orient is not None else NO_MAP_ORIENT,
        "first_src_read_index": first_src if first_src is not None else NO_SRC_READ,
        "first_map_read_index": first_map if first_map is not None else "NO-MAP-READ",
        "map_orient_before_src": before_src,
        "invocations": invocations,
    }


def _arm_of(run_dir: Path) -> str:
    """The arm label from the run's own meta.json — so a row cannot be mistaken for the
    other arm's. Both arms name their dirs `run-690` ... `run-704`; without this a POST
    scoring file and a PRE-B one are indistinguishable by content."""
    meta = run_dir / "meta.json"
    if not meta.is_file():
        return "UNKNOWN"
    try:
        return json.loads(meta.read_text(encoding="utf-8")).get("arm", "UNKNOWN")
    except ValueError:
        return "UNKNOWN"


def _ev_assistant(tool: str, inp: dict, call_id: str = "") -> str:
    block = {"type": "tool_use", "name": tool, "input": inp}
    if call_id:
        block["id"] = call_id
    return json.dumps({"type": "assistant", "message": {"content": [block]}})


def _ev_result(call_id: str, text: str) -> str:
    return json.dumps({"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": call_id, "content": text}]}})


ORIENT_CMD = ('py C:/Users/fredc/.claude/skills/constellation-commander/scripts/map_orient.py '
              'orient --root C:/Programs/f1bwt/post690 --work-id issue-690')


def self_test() -> int:
    """POSITIVE control plus the mutants that must NOT count.

    The PRE-B negative control proves only that the token does not appear spontaneously in a
    pre-#304 arm — which is true BY CONSTRUCTION and therefore proves almost nothing about
    this code. It cannot show that a real invocation is matched, nor that a mere mention is
    rejected. That is what these mutants are for. New code beside a frozen instrument needs a
    falsification floor at least as strong as the instrument's.
    """
    import tempfile

    cases: list[tuple[str, list[str], int, int]] = [
        # (name, ndjson lines, expected invocations, expected mentions)
        ("POSITIVE: real Bash orient invocation",
         [_ev_assistant("Bash", {"command": ORIENT_CMD}, "c1"),
          _ev_result("c1", "DEGRADED-NO-MAP\nroot: C:/Programs/f1bwt/post690")], 1, 0),
        ("POSITIVE: PowerShell executor counts too",
         [_ev_assistant("PowerShell", {"command": ORIENT_CMD})], 1, 0),
        ("MUTANT: Read of the script is a MENTION, not a call",
         [_ev_assistant("Read", {"file_path": "C:/Users/fredc/.claude/skills/"
                                 "constellation-commander/scripts/map_orient.py"})], 0, 1),
        ("MUTANT: Grep for the token is a MENTION",
         [_ev_assistant("Grep", {"pattern": "map_orient", "path": "."})], 0, 1),
        ("MUTANT: Write quoting the gate command is a MENTION",
         [_ev_assistant("Write", {"file_path": "x.md",
                                  "content": f"the gate runs `{ORIENT_CMD}`"})], 0, 1),
        ("MUTANT: --help is an invocation but NOT an orient call",
         [_ev_assistant("Bash", {"command": "py .../map_orient.py --help"})], 1, 0),
        ("CONTROL: unrelated call is neither",
         [_ev_assistant("Bash", {"command": "git status --porcelain"})], 0, 0),
    ]

    failures = 0
    print(f"self-test: {len(cases)} case(s)")
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, lines, want_inv, want_men) in enumerate(cases):
            d = Path(tmp) / f"run-{i}"
            d.mkdir()
            (d / "stream.ndjson").write_text("\n".join(lines) + "\n", encoding="utf-8")
            (d / "ordering.json").write_text(json.dumps(
                {"captured": True, "first_src_read_index": 50,
                 "first_map_read_index": 60}), encoding="utf-8")
            r = audit(d)
            got_inv = r["map_orient_invocation_count"]
            got_men = r["map_orient_mention_count"]
            ok = got_inv == want_inv and got_men == want_men
            # The --help case must produce an invocation with NO orient credit.
            if name.startswith("MUTANT: --help"):
                ok = ok and r["first_map_orient_index"] == NO_MAP_ORIENT
            if name.startswith("POSITIVE: real Bash"):
                ok = ok and r["map_orient_before_src"] is True and r["map_orient_verdicts"]
            print(f"  [{'ok ' if ok else 'FAIL'}] {name}: inv={got_inv} (want {want_inv}) "
                  f"mentions={got_men} (want {want_men})")
            if not ok:
                failures += 1
    print(f"self-test: {len(cases) - failures}/{len(cases)} passed")
    return 1 if failures else 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dirs", nargs="*")
    p.add_argument("--self-test", action="store_true",
                   help="positive control + mutants; takes no run dirs")
    p.add_argument("--out", default=None)
    p.add_argument("--expect-zero", action="store_true",
                   help="negative-control mode: exit 1 if ANY run shows a map_orient call")
    args = p.parse_args()

    if args.self_test:
        return self_test()
    if not args.run_dirs:
        print("REFUSED: no run dirs given (and --self-test not requested)")
        return 1

    rows = [audit(Path(d)) for d in args.run_dirs]

    # RULE: a guard that loops must assert WHAT IT LOOPED OVER. Without this line a typo in
    # a glob that expands to nothing prints a clean table and reports success over zero runs.
    print(f"enumerated {len(rows)} run dir(s): {', '.join(r['run'] for r in rows)}")
    if not rows:
        print("REFUSED: zero run dirs enumerated — there is nothing to audit")
        return 1

    hdr = (f"{'run':<12} {'calls':>5} {'mo_calls':>8} {'first_mo':>18} "
           f"{'first_src':>11} {'mo<src':>18} {'verdicts':<40}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if r["status"] == "NOT-CAPTURED":
            print(f"{r['run']:<12} NOT-CAPTURED")
            continue
        print(f"{r['run']:<12} {r['tool_call_count']:>5} "
              f"{r['map_orient_invocation_count']:>8} "
              f"{str(r['first_map_orient_index']):>18} "
              f"{str(r['first_src_read_index']):>11} "
              f"{str(r['map_orient_before_src']):>18} "
              f"{','.join(r['map_orient_verdicts'])[:40]:<40}")

    total = sum(r.get("map_orient_invocation_count", 0) for r in rows)
    print(f"\ntotal map_orient invocations across {len(rows)} run(s): {total}")

    if args.out:
        Path(args.out).write_text(json.dumps(rows, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")
        print(f"written: {args.out}")

    if args.expect_zero and total:
        print(f"NEGATIVE CONTROL FAILED: expected 0 map_orient invocations, found {total} — "
              "this script is matching noise and its POST column cannot be trusted")
        return 1
    if args.expect_zero:
        print(f"negative control PASSED: 0 invocations across {len(rows)} pre-#304 run(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
