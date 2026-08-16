#!/usr/bin/env python
"""#600 fresh-process demonstration: does each agent keep its own reading?

A NEW artifact, deliberately not an edit of `probe_cross_key.py`. That probe is
a truthful record of the PRE-FIX world and stays that way until the Commander
retires it at `g1-integrate`; after this change it takes its `after_sub is None`
branch and prints `VERDICT: NEITHER`, which would misdescribe the fixed world.

This script is DIRECTION-AGNOSTIC on purpose: it reports what it observes rather
than asserting what it hopes, so the SAME script run against the merge base and
against the head is the before/after evidence, with no edit in between to argue
about.

Why a fresh process at all: hook code is not fenced by git isolation, and
`CLAUDE_PROJECT_DIR` is resolved once at session launch and inherited unchanged,
so a hook change cannot be validated from inside the session that contains it.

It drives the REAL `handle_post_tool_use` over a REAL binding store and REAL
files on disk, in a scratch project dir, with two DISTINCT binding keys bound
into ONE work directory under two DIFFERENT engine_session names -- two agents
sharing a work area, which is the measured collision.

Usage:  py .agent-work/<work-id>/measurement/demo_owner_keyed_gauge.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def _load(name, path, register=False):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    if register:
        # gauge_reader's frozen dataclass resolves its own module through
        # sys.modules during class creation.
        sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


sr = _load("spine_rail", REPO / "scripts" / "hooks" / "spine_rail.py")
gw = _load("gauge_writer_hook", REPO / "scripts" / "hooks" / "gauge_writer_hook.py")
try:
    gr = _load("gauge_reader", REPO / "scripts" / "gauge_reader.py", register=True)
except Exception:  # pragma: no cover - only reachable on a broken checkout
    gr = None

ORCHESTRATOR = "owner-orchestrator"
DISPATCHED = "owner-dispatched"


def _bind(proj, key, spine_path, engine_session):
    binding = sr.load_binding(proj)
    entries = dict(binding.get(key) or {})
    entries[str(spine_path)] = {
        "spine": str(spine_path),
        "engine_session": engine_session,
        "worktree": str(proj),
        "claimed_at": "2026-08-16T12:00:00+00:00",
    }
    binding[key] = entries
    sr.save_binding(proj, binding)


def _transcript(path, total_tokens):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "type": "assistant",
        "isSidechain": False,
        "timestamp": "2026-08-16T12:00:00.000Z",
        "message": {
            "model": "claude-opus-4-8",
            "role": "assistant",
            "usage": {
                "input_tokens": total_tokens,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
        },
    }) + "\n", encoding="utf-8", newline="\n")
    return path


def _expected_name(engine_session):
    """The file this owner should end up with, through the ONE definition -- or
    the pre-fix shared name when that definition does not exist yet."""
    if gr is None or not hasattr(gr, "gauge_filename"):
        return "gauge.json"
    return gr.gauge_filename(gr.owner_key(engine_session))


def _fill(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp)
        os.environ["CLAUDE_PROJECT_DIR"] = str(proj)
        work = proj / ".agent-work" / "epic-600"
        work.mkdir(parents=True)
        orc_spine = work / "spine.json"
        disp_spine = work / "execute.json"
        orc_spine.write_text("{}", encoding="utf-8")
        disp_spine.write_text("{}", encoding="utf-8")

        _bind(proj, "s-disp", disp_spine, DISPATCHED)
        _bind(proj, "s-orc", orc_spine, ORCHESTRATOR)

        disp_t = _transcript(proj / "t-disp.jsonl", 20_000)     # 0.02 of 1M
        orc_t = _transcript(proj / "t-orc.jsonl", 900_000)      # 0.90 of 1M

        # Dispatched agent first, orchestrator second: the exact order in which
        # probe_cross_key.py watched the dispatched agent's reading disappear.
        gw.handle_post_tool_use(
            {"session_id": "s-disp", "transcript_path": str(disp_t)}, proj)
        gw.handle_post_tool_use(
            {"session_id": "s-orc", "transcript_path": str(orc_t)}, proj)

        disp_path = work / _expected_name(DISPATCHED)
        orc_path = work / _expected_name(ORCHESTRATOR)
        shared = work / "gauge.json"

        print("files written in the one work directory:")
        for p in sorted(work.iterdir()):
            print(f"  {p.name}")
        print()
        print(f"DISPATCHED agent's file  : {disp_path.name}")
        print(f"  -> {_fill(disp_path)}")
        print(f"ORCHESTRATOR's file      : {orc_path.name}")
        print(f"  -> {_fill(orc_path)}")
        print(f"shared gauge.json        : {_fill(shared)}")
        print(f"gauge-skip.json          : {_fill(work / 'gauge-skip.json')}")
        print()

        disp = _fill(disp_path)
        orc = _fill(orc_path)
        both_kept = (
            disp_path != orc_path
            and disp is not None and orc is not None
            and abs(disp.get("fill_fraction", -1) - 0.02) < 1e-9
            and abs(orc.get("fill_fraction", -1) - 0.90) < 1e-9
            and disp.get("owner") == (gr.owner_key(DISPATCHED) if gr and hasattr(gr, "owner_key") else None)
            and orc.get("owner") == (gr.owner_key(ORCHESTRATOR) if gr and hasattr(gr, "owner_key") else None)
        )
        if both_kept:
            print("VERDICT: EACH AGENT KEPT ITS OWN READING.")
            print("  Two distinct files, each carrying its own fill and an "
                  "`owner` field that matches its own filename.")
            return 0
        if disp_path == orc_path:
            print("VERDICT: COLLISION -- both agents resolve to ONE file, "
                  f"{disp_path.name}.")
            print(f"  The surviving fill is {disp.get('fill_fraction') if disp else None}; "
                  "the other agent's reading was destroyed with no skip sidecar "
                  "and no guard.")
            return 1
        print("VERDICT: NEITHER -- the two paths differ but the readings are "
              "not both intact. Inspect the dump above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
