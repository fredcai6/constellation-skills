#!/usr/bin/env python
"""Extract the ORDERING MEASURE from a measured run's stream-json transcript (#299).

Per the frozen rubric §4, and per the cold-critic pass that hardened it before capture.

FOUR reserved literals, never a blank and never a zero. Collapsing any pair would let an
instrument failure masquerade as a result:
  * `NO-MAP-READ`  — transcript captured, no map access. A FINDING.
  * `NO-SRC-READ`  — transcript captured, no source access. A FINDING.
  * `NO-CORPUS-READ` — transcript captured, the subject never touched its installed corpus.
  * `NOT-CAPTURED` — no usable transcript. A MISSING DATUM.

Classification is CALL-LEVEL, not token-level. If any path-bearing argument of a call
resolves under `.claude/skills`, the whole call is `skill-corpus` and nothing else is
credited — otherwise `Grep(pattern="docs/architecture", path=".claude/skills")` would be
scored as reading the map while it was in fact reading the instrument.

`prompt`/`query` arguments are bucketed `mention`, never `map`/`src`. A subagent dispatch
whose prompt names a map path is not a map read, and crediting it would fabricate reads.
The converse — a subagent that really does read the map, invisibly to the parent stream —
is NOT recoverable here, so `subagent_dispatch_count` is reported so a low map count can be
flagged as possibly-hidden rather than read as a finding.

FALSIFICATION FLOOR: `--self-test` runs the extractor against synthetic transcripts built
to make it return a WRONG answer, AND against a REAL `claude -p --output-format stream-json`
excerpt checked in at `fixtures/real-stream-excerpt.ndjson`. The real fixture is the one
that matters: without it the floor only validates the extractor against the author's own
guess at the format, which is self-referential. (It caught exactly that — the first version
of this file was tested only against `input.command` and would have silently missed every
`Read(file_path=...)` in a live run.)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NO_MAP_READ = "NO-MAP-READ"
NO_SRC_READ = "NO-SRC-READ"
NO_CORPUS_READ = "NO-CORPUS-READ"
NOT_CAPTURED = "NOT-CAPTURED"

HERE = Path(__file__).resolve().parent

# Arguments that carry a real filesystem target (a genuine access).
PATH_KEYS = ("file_path", "path", "pattern", "glob", "command", "notebook_path")
# Arguments that are prose, not access. Bucketed `mention`; never credited as a read.
MENTION_KEYS = ("prompt", "query", "description")
SUBAGENT_TOOLS = ("Agent", "Task")

# Operations a measured run must never perform against f1Brainz. A hit is a stop
# condition: kill the run and log it (LAUNCH_ORDER-299 §Stop Conditions).
FORBIDDEN = (
    re.compile(r"\bgit\s+push\b"),
    re.compile(r"\bgh\s+pr\s+create\b"),
    re.compile(r"\bgh\s+issue\s+comment\b"),
    re.compile(r"\bgit\s+commit\b"),
)

CORPUS_RE = re.compile(r"\.claude/skills")
# `docs/architecture` ONLY. A near-miss under docs/ (docs/AGENT_GUIDE.md,
# docs/DOCUMENTATION.md) is NOT the map and must not be credited as one.
MAP_RE = re.compile(r"docs/architecture(/|\b)")
MAP_PATH_RE = re.compile(r"docs/architecture(?:/[\w.*-]+)*")
# `src` with or without a trailing slash: Grep(path="src") is the ordinary form, and
# missing it would push first_src later and bias `map_before_src` toward True.
SRC_RE = re.compile(r"(^|[\s\"'/(=])src(/|[\s\"']|$)")


def _norm(v) -> str:
    return str(v).replace("\\", "/")


def classify_call(tool: str, inp: dict) -> tuple[set[str], list[str], str]:
    """Buckets for one call, the map paths it genuinely touched, and the matched evidence.

    CALL-LEVEL corpus rule: any path-bearing argument under `.claude/skills` makes the
    entire call `skill-corpus` and credits nothing else."""
    path_text = " ".join(_norm(inp.get(k, "")) for k in PATH_KEYS if inp.get(k)).strip()
    mention_text = " ".join(_norm(inp.get(k, "")) for k in MENTION_KEYS if inp.get(k)).strip()

    buckets: set[str] = set()
    if tool in SUBAGENT_TOOLS:
        buckets.add("subagent")
    if mention_text:
        buckets.add("mention")

    if path_text and CORPUS_RE.search(path_text):
        buckets.add("skill-corpus")
        return buckets, [], path_text[:200]

    matched: list[str] = []
    if path_text and MAP_RE.search(path_text):
        buckets.add("map")
        matched.append(MAP_RE.search(path_text).group(0))
    if path_text and SRC_RE.search(path_text):
        buckets.add("src")
    if not buckets:
        buckets.add("other")

    map_hits = MAP_PATH_RE.findall(path_text) if path_text else []
    # A directory-only touch (`ls docs/architecture`) is still an access; record it
    # explicitly rather than letting map_files_read contradict first_map_read_index.
    paths = [m if m != "docs/architecture" else "docs/architecture/" for m in map_hits]
    return buckets, paths, (matched[0] if matched else path_text[:200])


def tool_calls(stream_path: Path) -> list[dict]:
    """Ordered tool calls from a stream-json transcript.

    `index` is position in emitted order; `turn` is the assistant event the call came
    from. Calls sharing a turn were issued together (parallel tool use), so a reader can
    tell a genuine before/after from a coincidence of block order."""
    calls: list[dict] = []
    if not stream_path.is_file():
        return calls
    turn = -1
    for line in stream_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") != "assistant":
            continue
        turn += 1
        content = (ev.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            tool = block.get("name", "?")
            inp = block.get("input") or {}
            buckets, paths, evidence = classify_call(tool, inp)
            raw = " ".join(_norm(inp.get(k, "")) for k in PATH_KEYS + MENTION_KEYS if inp.get(k))
            calls.append({
                "index": len(calls),
                "turn": turn,
                "tool": tool,
                "buckets": sorted(buckets),
                "map_paths": paths,
                "evidence": evidence,
                "target": raw[:400],
            })
    return calls


def extract(stream_path: Path) -> dict:
    calls = tool_calls(stream_path)
    if not calls:
        return {
            "captured": False,
            "tool_call_count": 0,
            "first_map_read_index": NOT_CAPTURED,
            "first_src_read_index": NOT_CAPTURED,
            "first_corpus_read_index": NOT_CAPTURED,
            "map_files_read": NOT_CAPTURED,
            "map_before_src": NOT_CAPTURED,
            "subagent_dispatch_count": NOT_CAPTURED,
            "forbidden_operations": [],
            "calls": [],
        }

    def first(bucket: str):
        return next((c["index"] for c in calls if bucket in c["buckets"]), None)

    first_map, first_src, first_corpus = first("map"), first("src"), first("skill-corpus")

    seen: list[str] = []
    for c in calls:
        for mp in c["map_paths"]:
            if mp not in seen:
                seen.append(mp)

    forbidden = [
        {"index": c["index"], "tool": c["tool"], "target": c["target"]}
        for c in calls if any(p.search(c["target"]) for p in FORBIDDEN)
    ]

    return {
        "captured": True,
        "tool_call_count": len(calls),
        "first_map_read_index": NO_MAP_READ if first_map is None else first_map,
        "first_src_read_index": NO_SRC_READ if first_src is None else first_src,
        "first_corpus_read_index": NO_CORPUS_READ if first_corpus is None else first_corpus,
        # Derived from the INDEX, not from `seen`, so the two can never contradict.
        "map_files_read": NO_MAP_READ if first_map is None else (seen or ["docs/architecture/"]),
        "map_before_src": (
            NO_MAP_READ if first_map is None
            else NO_SRC_READ if first_src is None
            else first_map < first_src
        ),
        "subagent_dispatch_count": sum(1 for c in calls if "subagent" in c["buckets"]),
        "forbidden_operations": forbidden,
        "calls": calls,
    }


# --------------------------------------------------------------------------- #
# falsification floor
# --------------------------------------------------------------------------- #
def _synth(tmp: Path, turns: list[list[tuple[str, str, str]]]) -> Path:
    """Synthetic transcript from [[(tool, input_key, value), ...], ...]. The input KEY is
    a parameter precisely because pinning it to `command` is the mutant that hid every
    real `Read(file_path=...)`."""
    lines = [json.dumps({"type": "system", "subtype": "init"})]
    for turn in turns:
        lines.append(json.dumps({
            "type": "assistant",
            "message": {"content": [
                {"type": "tool_use", "name": t, "input": {k: v}} for t, k, v in turn
            ]},
        }))
    lines.append(json.dumps({"type": "result"}))
    p = tmp / "synth.ndjson"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return p


def self_test() -> int:
    import tempfile
    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{(' - ' + detail) if detail else ''}")
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # M0 — REAL transcript. The only mutation-check that is not self-referential.
        real = HERE / "fixtures" / "real-stream-excerpt.ndjson"
        check("M0 real fixture exists", real.is_file(), str(real))
        if real.is_file():
            r = extract(real)
            check("M0 real transcript yields tool calls", r["tool_call_count"] >= 6,
                  f"got {r['tool_call_count']}")
            tools = {c["tool"] for c in r["calls"]}
            check("M0 real Read calls seen (file_path path)", "Read" in tools, str(sorted(tools)))
            check("M0 real Glob calls seen (pattern path)", "Glob" in tools, str(sorted(tools)))
            check("M0 real Read target non-empty",
                  all(c["target"] for c in r["calls"] if c["tool"] == "Read"))

        # M1 — a map read is detected at the right index, via file_path.
        s = _synth(tmp, [[("Bash", "command", "ls")],
                         [("Read", "file_path", "docs/architecture/index.md")],
                         [("Read", "file_path", "src/physics/x.py")]])
        r = extract(s)
        check("M1 map index correct", r["first_map_read_index"] == 1, f"got {r['first_map_read_index']}")
        check("M1 src index correct", r["first_src_read_index"] == 2, f"got {r['first_src_read_index']}")
        check("M1 map_before_src true", r["map_before_src"] is True)

        # M2 — MUTATION: no map read. NO-MAP-READ, never 0/blank.
        s = _synth(tmp, [[("Bash", "command", "ls")], [("Read", "file_path", "src/x.py")]])
        r = extract(s)
        check("M2 absent map -> NO-MAP-READ", r["first_map_read_index"] == NO_MAP_READ)
        check("M2 NO-MAP-READ not falsy-zero", r["first_map_read_index"] != 0)
        check("M2 src still found", r["first_src_read_index"] == 1)

        # M3 — MUTATION: no transcript. NOT-CAPTURED, distinct from every NO-*-READ.
        r = extract(tmp / "nope.ndjson")
        check("M3 missing -> NOT-CAPTURED", r["first_map_read_index"] == NOT_CAPTURED)
        check("M3 four literals mutually distinct",
              len({NO_MAP_READ, NO_SRC_READ, NO_CORPUS_READ, NOT_CAPTURED}) == 4)
        check("M3 captured false", r["captured"] is False)

        # M4 — MUTATION: absent SRC read gets its OWN literal, not the map's.
        s = _synth(tmp, [[("Read", "file_path", "docs/architecture/index.md")]])
        r = extract(s)
        check("M4 absent src -> NO-SRC-READ", r["first_src_read_index"] == NO_SRC_READ,
              f"got {r['first_src_read_index']!r}")
        check("M4 absent src is NOT NO-MAP-READ", r["first_src_read_index"] != NO_MAP_READ)

        # M5 — MUTATION: corpus reads credited as neither map nor src, call-level.
        s = _synth(tmp, [[("Read", "file_path", ".claude/skills/x/references/src/foo.md")],
                         [("Grep", "pattern", "docs/architecture")]])
        # 2nd call has no path arg under corpus, so it IS a map hit; 1st must not be.
        r = extract(s)
        check("M5 corpus read not a map read", r["calls"][0]["buckets"] == ["skill-corpus"],
              str(r["calls"][0]["buckets"]))
        check("M5 corpus read recorded as corpus", r["first_corpus_read_index"] == 0)

        # M5b — the call-level rule: searching the CORPUS for the map path is not a map read.
        s = _synth(tmp, [[("Grep", "path", ".claude/skills")]])
        r = extract(s)
        check("M5b corpus-scoped grep is not a map read",
              r["first_map_read_index"] == NO_MAP_READ, str(r["calls"][0]["buckets"]))

        # M6 — near-miss under docs/ is NOT the map.
        s = _synth(tmp, [[("Read", "file_path", "docs/AGENT_GUIDE.md")],
                         [("Read", "file_path", "docs/DOCUMENTATION.md")]])
        r = extract(s)
        check("M6 docs/ near-miss is not a map read", r["first_map_read_index"] == NO_MAP_READ)
        s = _synth(tmp, [[("Read", "file_path", "docs/architecture/packets/physics.md")]])
        r = extract(s)
        check("M6 real map path IS a map read", r["first_map_read_index"] == 0)

        # M7 — Grep(path="src") with no trailing slash still counts.
        s = _synth(tmp, [[("Grep", "path", "src")]])
        r = extract(s)
        check("M7 bare src path counts as src", r["first_src_read_index"] == 0,
              str(r["calls"][0]["buckets"]))

        # M8 — a subagent prompt NAMING the map is a mention, not a read.
        s = _synth(tmp, [[("Agent", "prompt", "read docs/architecture/index.md and report")]])
        r = extract(s)
        check("M8 prompt mention is not a map read", r["first_map_read_index"] == NO_MAP_READ)
        check("M8 subagent dispatch counted", r["subagent_dispatch_count"] == 1)

        # M9 — one call spanning both trees credits both at the same index.
        s = _synth(tmp, [[("Grep", "command", "rain -r docs/architecture/ src/")]])
        r = extract(s)
        check("M9 spanning credits map", r["first_map_read_index"] == 0)
        check("M9 spanning credits src", r["first_src_read_index"] == 0)
        check("M9 spanning not map_before_src", r["map_before_src"] is False)

        # M10 — parallel calls share a turn; indices stay distinct.
        s = _synth(tmp, [[("Read", "file_path", "src/a.py"),
                          ("Read", "file_path", "docs/architecture/index.md")]])
        r = extract(s)
        check("M10 parallel share turn", r["calls"][0]["turn"] == r["calls"][1]["turn"])
        check("M10 parallel indices distinct", r["calls"][0]["index"] != r["calls"][1]["index"])

        # M11 — map_files_read can NEVER contradict first_map_read_index.
        s = _synth(tmp, [[("Bash", "command", "ls docs/architecture")]])
        r = extract(s)
        check("M11 dir-only touch has an index", isinstance(r["first_map_read_index"], int))
        check("M11 dir-only touch not NO-MAP-READ in files", r["map_files_read"] != NO_MAP_READ,
              str(r["map_files_read"]))

        # M12 — forbidden operations.
        s = _synth(tmp, [[("Bash", "command", "git push origin HEAD")]])
        check("M12 push flagged", len(extract(s)["forbidden_operations"]) == 1)
        s = _synth(tmp, [[("Bash", "command", "git status")]])
        check("M12 benign git not flagged", len(extract(s)["forbidden_operations"]) == 0)

    print()
    if failures:
        print(f"SELF-TEST FAILED: {len(failures)} mutation(s) survived: {failures}")
        return 1
    print("SELF-TEST PASSED: every mutation was killed.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dir", nargs="?")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()

    if args.self_test:
        return self_test()
    if not args.run_dir:
        p.error("run_dir required unless --self-test")

    run_dir = Path(args.run_dir)
    result = extract(run_dir / "stream.ndjson")
    (run_dir / "ordering.json").write_text(json.dumps(result, indent=2) + "\n",
                                           encoding="utf-8", newline="\n")
    print(f"{run_dir.name}: calls={result['tool_call_count']} "
          f"first_map={result['first_map_read_index']} "
          f"first_src={result['first_src_read_index']} "
          f"corpus={result['first_corpus_read_index']} "
          f"subagents={result['subagent_dispatch_count']} "
          f"forbidden={len(result['forbidden_operations'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
