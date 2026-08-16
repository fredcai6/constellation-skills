#!/usr/bin/env python
"""Probe: does a SECOND binding key write into the SAME gauge.json?

Settles the #600 open question. Two candidates were offered for how a stale /
foreign reading survives at the instant of a trip:

  candidate 1 — the write is skipped (ambiguous or unresolvable binding) and the
                stale file survives;
  candidate 2 — another agent's key resolves into the same directory and writes
                its own fill.

This drives the REAL `handle_post_tool_use` in a fresh process against a real
binding store, real transcript files and the real payload shapes the harness
sends (pinned by tests/fixtures/probe_payloads.jsonl: a top-level payload omits
`agent_id` entirely; a dispatched one carries it). Nothing is patched.

Topology is the everyday one: an orchestrator holding the bare `session_id` key,
and an agent it dispatched holding `session_id#agent_id`, with both spine files
under one `.agent-work/<work-id>/`.

Run: py probe_cross_key.py
Exit 0 always; the verdict is on stdout.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "scripts" / "hooks" / "gauge_writer_hook.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _transcript(path: Path, *, total: int, model: str, when: datetime,
                sidechain: bool, agent_id: str | None) -> None:
    """One assistant line whose three usage fields sum to `total`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "type": "assistant",
        "isSidechain": sidechain,
        "timestamp": when.isoformat().replace("+00:00", "Z"),
        "message": {
            "model": model,
            "usage": {
                "input_tokens": 1,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": total - 1,
            },
        },
    }
    if agent_id is not None:
        line["agentId"] = agent_id
    path.write_text(json.dumps(line) + "\n", encoding="utf-8")


def _checklist(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "work_id": "W", "type": "gated", "items": ["g1"],
        "tasks": {"g1": {"id": "g1", "title": "t", "imperative": "i",
                         "preconditions": [], "postconditions": [],
                         "status": "pending", "evidence": []}},
    }), encoding="utf-8")


def main() -> int:
    hook = _load("gauge_writer_hook", HOOK)

    tmp = Path(tempfile.mkdtemp(prefix="probe-cross-key-"))
    proj = tmp / "proj"
    work = proj / ".agent-work" / "W"
    gauge = work / "gauge.json"

    spine_orch = work / "spine.json"        # the orchestrator's own spine
    spine_sub = work / "execute.json"       # the dispatched agent's own plan
    _checklist(spine_orch)
    _checklist(spine_sub)

    now = datetime.now(timezone.utc)
    session_id = "SESS-ORCH"
    agent_id = "agentsub"

    # The orchestrator's transcript: main chain, isSidechain falsy, a BIG fill.
    parent_tx = tmp / "transcripts" / f"{session_id}.jsonl"
    _transcript(parent_tx, total=900_000, model="claude-opus-5",
                when=now - timedelta(seconds=5), sidechain=False, agent_id=None)

    # The dispatched agent's OWN transcript, at the derived path, a SMALL fill.
    sub_tx = parent_tx.with_suffix("") / "subagents" / f"agent-{agent_id}.jsonl"
    _transcript(sub_tx, total=20_000, model="claude-opus-5",
                when=now, sidechain=True, agent_id=agent_id)

    # Two DIFFERENT keys, each bound to ONE spine, both in the SAME work dir.
    binding = {
        session_id: {
            str(spine_orch): {"spine": str(spine_orch),
                              "engine_session": "orch-1",
                              "worktree": str(proj),
                              "claimed_at": (now - timedelta(minutes=10)).isoformat()},
        },
        f"{session_id}#{agent_id}": {
            str(spine_sub): {"spine": str(spine_sub),
                             "engine_session": "sub-1",
                             "worktree": str(proj),
                             "claimed_at": (now - timedelta(minutes=1)).isoformat()},
        },
    }
    store = proj / ".agent-work" / ".spine-rail-binding.json"
    store.write_text(json.dumps(binding), encoding="utf-8")

    payload_sub = {"session_id": session_id, "agent_id": agent_id,
                   "transcript_path": str(parent_tx), "cwd": str(proj)}
    payload_orch = {"session_id": session_id,
                    "transcript_path": str(parent_tx), "cwd": str(proj)}

    print(f"work dir            : {work}")
    print(f"key A (dispatched)  : {session_id}#{agent_id} -> {spine_sub.name}")
    print(f"key B (orchestrator): {session_id} -> {spine_orch.name}")
    print(f"both resolve to     : {gauge}")
    print()

    # --- act 1: the dispatched agent's tool call ---------------------------
    hook.handle_post_tool_use(payload_sub, proj)
    after_sub = json.loads(gauge.read_text()) if gauge.exists() else None
    print("after DISPATCHED agent's call :", json.dumps(after_sub))

    # --- act 2: the orchestrator's own tool call ---------------------------
    hook.handle_post_tool_use(payload_orch, proj)
    after_orch = json.loads(gauge.read_text()) if gauge.exists() else None
    print("after ORCHESTRATOR's call     :", json.dumps(after_orch))

    skip = gauge.with_name("gauge-skip.json")
    print("gauge-skip.json               :",
          json.loads(skip.read_text()) if skip.exists() else "(none)")
    print()

    # --- verdict -----------------------------------------------------------
    if after_sub is None:
        print("VERDICT: NEITHER — the dispatched agent's write was skipped.")
        return 0
    if after_orch is None:
        print("VERDICT: unexpected — gauge.json disappeared.")
        return 0
    sub_fill = after_sub["fill_fraction"]
    orch_fill = after_orch["fill_fraction"]
    if orch_fill != sub_fill:
        print(f"VERDICT: CANDIDATE 2 CONFIRMED. The orchestrator's own fill "
              f"({orch_fill}) OVERWROTE the dispatched agent's ({sub_fill}) at "
              f"the same path. Two distinct keys, one gauge file, no guard.")
        print()
        print("  The overwrite is FRESH, which is the decisive part:")
        sub_claim = datetime.fromisoformat(binding[f'{session_id}#{agent_id}'][str(spine_sub)]['claimed_at'])
        obs = datetime.fromisoformat(after_orch["observed_at"].replace("Z", "+00:00"))
        print(f"    dispatched agent claimed_at : {sub_claim.isoformat()}")
        print(f"    foreign reading observed_at : {obs.isoformat()}")
        print(f"    observed_at > claimed_at    : {obs > sub_claim}  "
              f"-> _reading_predates_claim is False -> #477/#601 guard does NOT fire")
    else:
        print(f"VERDICT: CANDIDATE 2 NOT REPRODUCED — both calls wrote the same "
              f"fill ({orch_fill}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
