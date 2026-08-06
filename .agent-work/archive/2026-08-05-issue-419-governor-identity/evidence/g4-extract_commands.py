#!/usr/bin/env python3
"""Dump every engine command and its RAW result, verbatim, straight out of each
agent's own transcript -- not out of any agent's authored report. Used for both
arms; pass the sandbox directory name."""
import json
import re
import sys
from pathlib import Path

ACC = Path(__file__).resolve().parent
PROJECTS = Path("C:/Users/fredc/.claude/projects")
UUID_RE = re.compile(r"\A[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")


def slug_for(path: Path) -> str:
    return str(path).replace("\\", "/").replace(":", "-").replace("/", "-")


def load(p: Path):
    out = []
    for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue
        if isinstance(d, dict):
            out.append(d)
    return out


def results_by_id(lines):
    m = {}
    for d in lines:
        content = (d.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                c = b.get("content")
                if isinstance(c, list):
                    c = "".join(x.get("text", "") for x in c if isinstance(x, dict))
                m[b.get("tool_use_id")] = c
    return m


def dump(label, path: Path, out):
    lines = load(path)
    res = results_by_id(lines)
    out.append("\n" + "=" * 78)
    out.append("%s -- %s (%d lines)" % (label, path.name, len(lines)))
    out.append("=" * 78)
    for d in lines:
        if d.get("type") != "assistant":
            continue
        for b in (d.get("message") or {}).get("content") or []:
            if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                continue
            inp = b.get("input") or {}
            cmd = inp.get("command")
            if not cmd or "checklist_engine.py" not in str(cmd):
                continue
            out.append("\n$ %s" % cmd)
            out.append("[ts %s]" % d.get("timestamp"))
            out.append(str(res.get(b.get("id"), "<no result captured>")).rstrip())
    return out


def main() -> int:
    sbname = sys.argv[1] if len(sys.argv) > 1 else "sb-treatment"
    sb = ACC / sbname
    proj = PROJECTS / slug_for(sb)
    binding_file = sb / ".agent-work" / ".spine-rail-binding.json"
    binding = json.loads(binding_file.read_text(encoding="utf-8")) if binding_file.exists() else {}
    bare = [k for k in binding if "#" not in k]
    if bare:
        session = bare[0]
    else:
        cands = sorted((p for p in proj.iterdir() if p.is_dir() and UUID_RE.match(p.name)),
                       key=lambda p: p.stat().st_mtime)
        session = cands[-1].name
    out = ["RAW engine commands and results, read out of each agent's OWN transcript",
           "sandbox: %s" % sb, "harness session: %s" % session]
    dump("PARENT (top-level)", proj / ("%s.jsonl" % session), out)
    subdir = proj / session / "subagents"
    for t in sorted(subdir.glob("agent-*.jsonl")):
        dump("SUBAGENT %s" % t.stem[len("agent-"):], t, out)
    text = "\n".join(out) + "\n"
    dest = ACC / ("commands-%s.txt" % sbname.replace("sb-", ""))
    dest.write_text(text, encoding="utf-8", newline="\n")
    print("wrote %s (%d bytes)" % (dest, len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
