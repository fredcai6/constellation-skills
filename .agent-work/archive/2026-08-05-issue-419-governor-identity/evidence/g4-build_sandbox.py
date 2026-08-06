#!/usr/bin/env python3
"""Build the g4 acceptance sandbox for issue #419.

Two sibling sandboxes (treatment / control), each with its OWN .agent-work/ so the
main checkout's live binding store is never touched. Real gated spines, a chunked
plain-text corpus large enough that an agent reading many chunks genuinely consumes
context, and both arms' settings files. Nothing here supplies an agent identity.
"""
import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

ACC = Path(__file__).resolve().parent
WT = "C:/Programs/constellation-skills-wt/epic418-a-419"
MAIN = "C:/Programs/constellation-skills"
PY = "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe"
ENGINE = WT + "/scripts/checklist_engine.py"

CHUNKS = 20
CHUNK_BYTES = 96_000
LINE_CHARS = 96

WORDS = """orbit lattice cadence turbine harbor mantle cipher glacier pylon meridian
ledger tundra quartz beacon furrow anvil cistern plateau vellum runnel spindle
thicket cobalt ravine fathom bramble kestrel granite marsh conduit lantern
trellis sediment aperture cornice bulwark estuary parapet alcove filament
current gauge spine rail binding transcript agent session harness identity
consume window fraction threshold advisory refusal journal evidence artifact
measure attribute derive resolve compose observe record narrow widen anchor
copper willow ember tide furnace saddle prism ladder canyon meadow bridge
""".split()


def gen_corpus(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    rng = random.Random(419)
    for i in range(CHUNKS):
        out = []
        size = 0
        while size < CHUNK_BYTES:
            line = []
            n = 0
            while n < LINE_CHARS:
                w = rng.choice(WORDS)
                line.append(w)
                n += len(w) + 1
            s = " ".join(line)
            out.append(s)
            size += len(s) + 1
        text = "\n".join(out) + "\n"
        (dest / ("chunk-%02d.txt" % i)).write_text(text, encoding="utf-8", newline="\n")


def gate(gid: str, title: str) -> dict:
    return {
        "id": gid,
        "title": title,
        "imperative": "Work the sandbox reading task for %s, then move the gate through the engine." % gid,
        "preconditions": [],
        "postconditions": [{
            "id": "c1",
            "statement": "the reading pass for this gate is done",
            "check": {"kind": "command", "command": "exit 0"},
            "satisfied": False,
        }],
        "constraints": [],
        "directives": None,
        "child_checklist": None,
        "why_exempt": True,
        "status": "pending",
        "status_detail": {},
        "result": None,
        "finding": None,
        "evidence": [],
        "rework_count": 0,
    }


def spine(work_id: str) -> dict:
    return {
        "work_id": work_id,
        "type": "gated",
        "items": ["g1", "g2"],
        "tasks": {"g1": gate("g1", "First reading pass"), "g2": gate("g2", "Second reading pass")},
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
    }


WORK_IDS = ["wk-parent", "wk-alpha", "wk-bravo", "wk-echo"]


def build_sandbox(name: str) -> Path:
    sb = ACC / name
    if sb.exists():
        shutil.rmtree(sb)
    (sb / ".agent-work").mkdir(parents=True)
    for wid in WORK_IDS:
        d = sb / ".agent-work" / wid
        d.mkdir(parents=True)
        (d / "spine.json").write_text(
            json.dumps(spine(wid), indent=2), encoding="utf-8", newline="\n")
    shutil.copytree(ACC / "corpus", sb / "corpus")
    return sb


def settings(hook_dir: str) -> dict:
    return {
        "defaultShell": "powershell",
        "hooks": {
            "PostToolUse": [{
                "matcher": "*",
                "hooks": [
                    {"type": "command",
                     "command": '"%s" "%s/spine_rail.py" PostToolUse' % (PY, hook_dir),
                     "timeout": 30},
                    {"type": "command",
                     "command": '"%s" "%s/gauge_writer_hook.py"' % (PY, hook_dir),
                     "timeout": 30},
                ],
            }],
        },
    }


def slug_for(path: Path) -> str:
    s = str(path).replace("\\", "/")
    s = s.replace(":", "-")
    return s.replace("/", "-")


def main() -> int:
    gen_corpus(ACC / "corpus")
    sizes = sorted((ACC / "corpus").glob("chunk-*.txt"))
    total = sum(p.stat().st_size for p in sizes)
    print("corpus: %d chunks, %d bytes total, chunk-00 = %d bytes"
          % (len(sizes), total, sizes[0].stat().st_size))

    for name in ("sb-treatment", "sb-control"):
        sb = build_sandbox(name)
        print("built %s" % sb)

    (ACC / "settings-treatment.json").write_text(
        json.dumps(settings(WT + "/scripts/hooks"), indent=2), encoding="utf-8", newline="\n")
    (ACC / "settings-control.json").write_text(
        json.dumps(settings(MAIN + "/scripts/hooks"), indent=2), encoding="utf-8", newline="\n")
    print("settings written (one variable: the hook directory)")

    # Validate every spine through THIS worktree's engine.
    bad = 0
    for name in ("sb-treatment", "sb-control"):
        for wid in WORK_IDS:
            f = ACC / name / ".agent-work" / wid / "spine.json"
            r = subprocess.run([sys.executable, ENGINE, "--file", str(f), "current"],
                               capture_output=True, text=True)
            ok = r.returncode == 0 and "ACTIVE g1" in r.stdout
            print("validate %s/%s -> exit %d %s" % (name, wid, r.returncode, "OK" if ok else "FAIL"))
            if not ok:
                bad += 1
                print(r.stdout[-500:], r.stderr[-500:])
    if bad:
        return 1

    # Pre-run emptiness proof (handoff constraint 2).
    lines = []
    for name in ("sb-treatment", "sb-control"):
        sb = ACC / name
        b = sb / ".agent-work" / ".spine-rail-binding.json"
        lines.append("binding store %s exists=%s" % (b, b.exists()))
        proj = Path("C:/Users/fredc/.claude/projects") / slug_for(sb)
        lines.append("harness project dir %s exists=%s" % (proj, proj.exists()))
        sessions = sorted(p.name for p in proj.iterdir() if p.is_dir()) if proj.exists() else []
        lines.append("  session dirs present BEFORE this run: %d %s" % (len(sessions), sessions))
        subs = list(proj.glob("*/subagents")) if proj.exists() else []
        lines.append("  subagents dirs under it: %d %s" % (len(subs), [str(s) for s in subs]))
        gauges = list(sb.glob(".agent-work/*/gauge.json"))
        lines.append("  gauge.json files present: %d" % len(gauges))
    txt = "\n".join(lines) + "\n"
    (ACC / "prerun-empty.txt").write_text(txt, encoding="utf-8", newline="\n")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
