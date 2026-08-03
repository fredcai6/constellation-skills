#!/usr/bin/env python3
"""Score the two tracer arms from their engine call logs and agent transcripts."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARMS = [("arm1-mcp","MCP r1"),("arm1-mcp-r2","MCP r2"),("arm2-cli","CLI r1"),("arm2-cli-r2","CLI r2")]


VERBS = {"current", "claim", "heartbeat", "release", "start", "advance", "record",
         "consolidate", "skip", "block", "resume", "reopen", "append", "amend",
         "attest", "waive", "attach", "flag-candidate"}


def load(p: Path):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def verb_of(call: dict) -> str:
    """First argv token that is an actual engine verb (the CLI log's argv starts
    with `--file <path>`, so 'first non-dash token' would return the path)."""
    return next((a for a in call["argv"] if a in VERBS), "?")


rows = {}
for name, label in ARMS:
    d = ROOT / "runs" / name
    calls = load(d / "engine_calls.jsonl")
    tx = load(d / "transcript.jsonl")

    malformed = [c for c in calls if c["code"] == 2]
    refused = [c for c in calls if c["code"] == 1]
    helps = [c for c in calls if "--help" in c["argv"]]
    reads = [c for c in calls if verb_of(c) == "current"]

    tool_calls, errored_results, texts = 0, 0, []
    by_tool: dict[str, int] = {}
    for m in tx:
        msg = m.get("message") or {}
        for blk in msg.get("content") or []:
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "tool_use":
                tool_calls += 1
                by_tool[blk.get("name", "?")] = by_tool.get(blk.get("name", "?"), 0) + 1
            if blk.get("type") == "tool_result" and blk.get("is_error"):
                errored_results += 1
            if blk.get("type") == "text":
                texts.append(blk["text"])

    result = next((m for m in tx if m.get("type") == "result"), {})
    final_state = (d / "spine.json")
    spine = json.loads(final_state.read_text(encoding="utf-8"))
    done = all(spine["tasks"][i]["status"] in ("complete", "skipped") for i in spine["items"])

    rows[name] = {
        "label": label,
        "prompt_words": len((d / "prompt.txt").read_text(encoding="utf-8").split()),
        "engine_calls": len(calls),
        "malformed": len(malformed),
        "refusals": len(refused),
        "help_discovery": len(helps),
        "status_polls": len(reads),
        "agent_tool_calls": tool_calls,
        "errored_tool_results": errored_results,
        "turns": result.get("num_turns"),
        "duration_ms": result.get("duration_ms"),
        "cost_usd": round(result.get("total_cost_usd", 0), 4),
        "reached_done": done,
        "spine_refusal_counter": spine.get("refusals"),
        "malformed_detail": [" ".join(c["argv"]) for c in malformed],
        "refusal_detail": [" ".join(c["argv"]) for c in refused],
        "tool_breakdown": dict(sorted(by_tool.items(), key=lambda kv: -kv[1])),
    }

keys = ["prompt_words", "engine_calls", "malformed", "refusals", "help_discovery",
        "status_polls", "agent_tool_calls", "errored_tool_results", "turns",
        "duration_ms", "cost_usd", "reached_done", "spine_refusal_counter"]
w = max(len(k) for k in keys) + 2
print(f"{'metric':<{w}}" + ''.join(f'{n:>13}' for n,_ in ARMS))
print("-" * (w + 13*len(ARMS)))
for k in keys:
    print(f"{k:<{w}}" + "".join(f"{str(rows[n][k]):>13}" for n, _ in ARMS))

for n, _ in ARMS:
    print(f"\n== {n} malformed ==")
    for x in rows[n]["malformed_detail"]:
        print("  ", x)
    print(f"== {n} refusals ==")
    for x in rows[n]["refusal_detail"]:
        print("  ", x)
    print(f"== {n} agent tool breakdown ==")
    for k, v in rows[n]["tool_breakdown"].items():
        print(f"   {v:>3}  {k}")

(ROOT / "runs" / "scores.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
