#!/usr/bin/env python
"""Probe: do two binding keys sharing one work directory collide?

WHICH WORLD THIS DESCRIBES — read this before trusting any output.

  This file now describes the world AFTER #600 (commit 3bc87e93), and it
  ASSERTS that world: it exits non-zero if the collision comes back.

  `probe_cross_key.pre-fix.out` is the record of the world BEFORE #600. Do not
  re-run this script and expect that output — it cannot reproduce, because the
  defect it captured is fixed. It is kept because it is the measurement the
  design was cut from, not because it is still reproducible.

  `probe_cross_key.post-fix.out` is this script's output at 3bc87e93 and after.

WHAT IT ORIGINALLY SETTLED (#600's open question). Two candidates were offered
for how a stale / foreign reading survives at the instant of a trip:

  candidate 1 — the write is skipped (ambiguous or unresolvable binding) and the
                stale file survives;
  candidate 2 — another agent's key resolves into the same directory and writes
                its own fill.

The pre-fix run confirmed CANDIDATE 2, and the decisive detail was that the
foreign overwrite is FRESH: `observed_at > claimed_at`, so `_reading_predates_
claim` is False and #477/#601's timestamp guard does not fire. Time cannot see a
concurrent collision. That is the whole argument for keying on identity.

WHAT IT ASSERTS NOW. The same two keys, the same one work directory. Post-fix
each agent's reading lands in its OWN `gauge-<owner>.json`, keyed on its binding
entry's `engine_session`, so neither can overwrite the other and neither can be
read as the other's. The probe fails if the two agents ever share one file, if
either loses its reading, or if the fills get swapped.

A note on reading this script's OLD verdict line. Before this update the probe
watched `gauge.json` only, so post-fix it printed "VERDICT: NEITHER — the
dispatched agent's write was skipped." That was wrong in a way worth recording:
nothing was skipped: both agents wrote, to owner-keyed files the probe was not
looking at. An archived artifact that misdescribes the fixed world is the reason
this update belongs to `g1-integrate`.

This drives the REAL `handle_post_tool_use` in a fresh process against a real
binding store, real transcript files and the real payload shapes the harness
sends (pinned by tests/fixtures/probe_payloads.jsonl: a top-level payload omits
`agent_id` entirely; a dispatched one carries it). Nothing is patched.

Topology is the everyday one: an orchestrator holding the bare `session_id` key,
and an agent it dispatched holding `session_id#agent_id`, with both spine files
under one `.agent-work/<work-id>/`.

Run: py probe_cross_key.py
Exit 0 when the fixed behaviour holds; 1 when it does not.
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
READER = REPO / "scripts" / "gauge_reader.py"


def _load(name: str, path: Path):
    """Load a module by path.

    The `sys.modules` registration is load-bearing, not tidiness: `gauge_reader`
    declares a `@dataclass(frozen=True)`, and dataclass field resolution looks
    the owning module up in `sys.modules`. Without this line the load raises
    `AttributeError: 'NoneType' object has no attribute '__dict__'` -- but only
    when nothing else registered the module first. Post-fix the hook loads
    `gauge_reader` itself, which masked the omission; running this probe against
    the PRE-fix tree, where the hook does not, is what exposed it.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
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
    reader = _load("gauge_reader", READER)

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

    # Say plainly which world we are standing in, rather than dying obscurely.
    # `owner_key`/`gauge_filename` arrive WITH #600, so their absence is the
    # cleanest available signal that this tree predates the fix.
    if not (hasattr(reader, "owner_key") and hasattr(reader, "gauge_filename")):
        print("REFUSING TO RUN: this tree PREDATES #600.")
        print()
        print(f"  {READER} has no owner_key/gauge_filename, so there are no")
        print("  owner-keyed gauge files for this probe to assert against.")
        print()
        print("  This script describes the world AFTER #600 (commit 3bc87e93).")
        print("  The pre-fix world is recorded in probe_cross_key.pre-fix.out --")
        print("  read that artifact rather than re-running this script here.")
        return 1

    # Post-fix, each agent's reading is keyed on its OWN binding entry's
    # engine_session -- 'orch-1' and 'sub-1' -- not on the work directory.
    path_orch = work / reader.gauge_filename(reader.owner_key("orch-1"))
    path_sub = work / reader.gauge_filename(reader.owner_key("sub-1"))

    print(f"work dir            : {work}")
    print(f"key A (dispatched)  : {session_id}#{agent_id} -> {spine_sub.name}"
          f"  (engine_session sub-1)")
    print(f"key B (orchestrator): {session_id} -> {spine_orch.name}"
          f"  (engine_session orch-1)")
    print(f"shared path (pre-fix): {gauge.name}   <- the collision site")
    print(f"owner-keyed (post-fix): {path_sub.name}")
    print(f"                        {path_orch.name}")
    print()

    def _load_json(path: Path):
        return json.loads(path.read_text()) if path.exists() else None

    # --- act 1: the dispatched agent's tool call ---------------------------
    hook.handle_post_tool_use(payload_sub, proj)
    print("after DISPATCHED agent's call :")
    print("    shared     :", json.dumps(_load_json(gauge)))
    print("    sub-1 own  :", json.dumps(_load_json(path_sub)))

    # --- act 2: the orchestrator's own tool call ---------------------------
    hook.handle_post_tool_use(payload_orch, proj)
    print("after ORCHESTRATOR's call     :")
    print("    shared     :", json.dumps(_load_json(gauge)))
    print("    sub-1 own  :", json.dumps(_load_json(path_sub)))
    print("    orch-1 own :", json.dumps(_load_json(path_orch)))

    skip = gauge.with_name("gauge-skip.json")
    print("gauge-skip.json               :",
          json.loads(skip.read_text()) if skip.exists() else "(none)")
    print()

    after_sub = _load_json(path_sub)
    after_orch = _load_json(path_orch)

    # --- verdict: ASSERT the fixed world -----------------------------------
    # Pre-fix this printed 'CANDIDATE 2 CONFIRMED' by watching gauge.json alone.
    # It now asserts that the collision is gone AND that neither reading was
    # lost -- because "no collision" is also what a dark governor looks like.
    failures: list[str] = []

    if _load_json(gauge) is not None:
        failures.append(
            "the shared gauge.json was written -- the collision site is live again")
    if after_sub is None:
        failures.append(
            "the dispatched agent kept NO reading -- silent loss, not separation")
    if after_orch is None:
        failures.append(
            "the orchestrator kept NO reading -- silent loss, not separation")

    if not failures:
        sub_fill = after_sub["fill_fraction"]
        orch_fill = after_orch["fill_fraction"]
        # 20_000/900_000 tokens: the dispatched agent's fill must stay the small
        # one. Swapped fills would mean each agent read the other's transcript.
        if not sub_fill < orch_fill:
            failures.append(
                f"fills are not separated as expected: dispatched={sub_fill} "
                f"orchestrator={orch_fill} (the dispatched agent's must be smaller)")
        if after_sub.get("owner") != reader.owner_key("sub-1"):
            failures.append(
                f"the dispatched agent's record is stamped "
                f"{after_sub.get('owner')!r}, not its own owner")
        if after_orch.get("owner") != reader.owner_key("orch-1"):
            failures.append(
                f"the orchestrator's record is stamped "
                f"{after_orch.get('owner')!r}, not its own owner")

    if failures:
        print("VERDICT: THE COLLISION IS BACK (or a reading was lost).")
        for line in failures:
            print(f"  - {line}")
        print()
        print("  This probe asserts the world AFTER #600. See the module "
              "docstring; the pre-fix record is probe_cross_key.pre-fix.out.")
        return 1

    print(f"VERDICT: EACH AGENT KEPT ITS OWN READING. The orchestrator's fill "
          f"({after_orch['fill_fraction']}) no longer overwrites the dispatched "
          f"agent's ({after_sub['fill_fraction']}): two distinct keys, two "
          f"owner-keyed files, and the shared gauge.json is never written.")
    print()
    print("  Each record NAMES its owner, which is what the timestamp guard "
          "could not do:")
    print(f"    dispatched agent -> {path_sub.name}  owner={after_sub['owner']}")
    print(f"    orchestrator     -> {path_orch.name}  owner={after_orch['owner']}")
    print()
    print("  Why time alone was never enough (the pre-fix finding, retained):")
    sub_claim = datetime.fromisoformat(
        binding[f'{session_id}#{agent_id}'][str(spine_sub)]['claimed_at'])
    obs = datetime.fromisoformat(after_orch["observed_at"].replace("Z", "+00:00"))
    print(f"    dispatched agent claimed_at : {sub_claim.isoformat()}")
    print(f"    orchestrator     observed_at: {obs.isoformat()}")
    print(f"    observed_at > claimed_at    : {obs > sub_claim}  "
          f"-> _reading_predates_claim would be False, so #477/#601's guard "
          f"could NOT have caught this overwrite. Identity can; time could not.")
    print()
    print("  NOTE: #601's timestamp comparison is still present and still fires "
          "on the SEQUENTIAL relaunch case. This probe covers the CONCURRENT "
          "case only, and decision:identity-not-time is NOT complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
