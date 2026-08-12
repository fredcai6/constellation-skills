#!/usr/bin/env python
"""Verify the PRE-B TREATMENT landed, per run. This is the arm's reason to exist.

A run with no verified Commander load is a FAILED CAPTURE, not a data point. An
unverified treatment is worse than no arm, because it looks valid.

THE DISCRIMINATOR (found by the #331 probe, and strictly better than a planted sentinel)
    Claude Code prefixes loaded skill content with a literal
        `Base directory for this skill: <absolute path>`
    line, delivered as a `user` text block. It is emitted by the harness rather than
    planted, so it cannot be defeated by content truncation, and it NAMES THE SERVING
    COPY outright — which is the quantity #332 showed cannot otherwise be established.

WHAT COUNTS AS A VERIFIED LOAD
    A `Skill` tool_use naming `constellation-commander` OR `constellation-commander-delegated`,
    AND a matching `Base directory for this skill:` line resolving under a directory of that
    name. Both variants count and WHICH ONE is recorded: the delegated variant ships no
    templates of its own and explicitly drives the SAME `COMMANDER_SPINE.template.json` out
    of `constellation-commander`, so both fire the identical two map-first imperatives. The
    treatment surface is the same; only the human-gating differs, so collapsing them would
    lose information but accepting only one would reject a run that got the treatment.

WHAT THIS ALSO COUNTS, AND WHY
    `write_audit` — every `Write`/`Edit`/`NotebookEdit`/`MultiEdit` call WITH its resolved
    target. Under a Commander treatment "zero write calls" is not achievable by
    construction (the plan step authors a mission frame and `execute.json`), so the
    "nothing landed in f1Brainz" claim rests on a different and strictly stronger check:
    every write resolves INSIDE this run's own disposable pinned worktree, under
    `.agent-work/`. Anything else is a stop condition.

    `map_credit_suppressed` — the frozen extractor's CALL-LEVEL corpus rule credits a call
    that touches `.claude/skills` as `skill-corpus` and NOTHING ELSE. That rule was written
    for a corpus installed INSIDE the worktree; under PRE-B the corpus is at
    `~/.claude/skills` and the Commander invokes its bundled scripts constantly, so a
    combined call could in principle swallow a genuine map read. The extractor is FROZEN
    and is not touched. Instead the exposure is MEASURED: calls bucketed `skill-corpus`
    that also carry a `docs/architecture` token. A count of 0 means the concern is
    hypothetical in this arm; a non-zero count is a declared limitation with a number on it.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

WRITE_TOOLS = ("Write", "Edit", "NotebookEdit", "MultiEdit")
FORBIDDEN = (
    re.compile(r"\bgit\s+push\b"),
    re.compile(r"\bgh\s+pr\s+create\b"),
    re.compile(r"\bgh\s+issue\s+(comment|create|edit|close)\b"),
    re.compile(r"\bgit\s+commit\b"),
    re.compile(r"\bgit\s+merge\b"),
)
BASE_DIR_RE = re.compile(r"Base directory for this skill:\s*(.+)")
COMMANDER_NAMES = ("constellation-commander", "constellation-commander-delegated")
MAP_TOKEN = re.compile(r"docs[\\/]architecture")


def events(path: Path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except ValueError:
            continue


def _skill_name_of(base_dir: str) -> str:
    parts = base_dir.replace("\\", "/").rstrip("/").split("/")
    return parts[-1] if parts else ""


def analyze(run_dir: Path) -> dict:
    stream = run_dir / "stream.ndjson"
    if not stream.is_file():
        return {"captured": False, "verdict": "FAILED-CAPTURE", "reason": "no transcript"}

    raw = stream.read_text(encoding="utf-8", errors="replace")
    # A transcript whose last line is not newline-terminated was cut mid-line — the exact
    # instrument failure the #331 probe hit. Never report such a run as a data point.
    truncated = bool(raw) and not raw.endswith("\n")

    calls: list[dict] = []
    skill_calls: list[dict] = []
    writes: list[dict] = []
    forbidden: list[dict] = []
    loads: list[dict] = []
    init_skills: list[str] = []
    result_text = ""

    for ev in events(stream):
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            init_skills = ev.get("skills") or []
        elif ev.get("type") == "assistant":
            for b in (ev.get("message") or {}).get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                inp = b.get("input") or {}
                rec = {"index": len(calls), "tool": b.get("name"), "input": inp}
                calls.append(rec)
                if rec["tool"] == "Skill":
                    skill_calls.append({"index": rec["index"], "skill": inp.get("skill"),
                                        "input": inp})
                if rec["tool"] in WRITE_TOOLS:
                    writes.append({
                        "index": rec["index"], "tool": rec["tool"],
                        "target": str(inp.get("file_path") or inp.get("notebook_path") or ""),
                    })
                blob = json.dumps(inp)
                if any(p.search(blob) for p in FORBIDDEN):
                    forbidden.append({"index": rec["index"], "tool": rec["tool"],
                                      "target": blob[:300]})
        elif ev.get("type") == "user":
            for b in (ev.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "text":
                    m = BASE_DIR_RE.search(b.get("text") or "")
                    if m:
                        bd = m.group(1).strip()
                        loads.append({"base_dir": bd, "skill": _skill_name_of(bd),
                                      "after_call_index": len(calls) - 1})
        elif ev.get("type") == "result":
            result_text = str(ev.get("result") or "")

    from collections import Counter

    con = [s for s in init_skills if s.startswith("constellation-")]
    dupes = {k: v for k, v in Counter(con).items() if v > 1}

    commander_calls = [c for c in skill_calls if c["skill"] in COMMANDER_NAMES]
    commander_loads = [l for l in loads if l["skill"] in COMMANDER_NAMES]

    # Both witnesses must agree: the tool was invoked AND the harness reported serving it.
    treatment_ok = bool(commander_calls) and bool(commander_loads)

    verdict = (
        "FAILED-CAPTURE-TRUNCATED" if truncated
        else "TREATMENT-VERIFIED" if treatment_ok
        else "FAILED-CAPTURE-NO-COMMANDER-LOAD"
    )

    # Writes outside this run's own worktree are a stop condition, not a note.
    meta_p = run_dir / "meta.json"
    worktree = ""
    if meta_p.is_file():
        worktree = json.loads(meta_p.read_text(encoding="utf-8")).get("worktree", "")
    wt = worktree.replace("\\", "/").rstrip("/").lower()

    def _resolve(target: str) -> str:
        """Relative write targets resolve against the subject's cwd, which IS the worktree.

        Without this a perfectly in-bounds `Write(file_path=".agent-work/x.md")` would be
        reported as escaping the worktree - a FALSE stop condition, which on a
        time-sensitive arm is as costly as a missed one."""
        t = target.replace("\\", "/").lower()
        if not t:
            return ""
        if re.match(r"^[a-z]:/|^//", t):
            return t
        if not wt:
            return t
        # NOT `lstrip("./")` - that is a character SET and eats the leading dot of
        # `.agent-work`, silently relocating every in-bounds Commander write.
        while t.startswith("./"):
            t = t[2:]
        return f"{wt}/{t}"

    def _outside(target: str) -> bool:
        t = _resolve(target)
        if not t or not wt:
            return True                      # an unresolvable target is not evidence of safety
        return not t.startswith(wt + "/")

    escaping = [w for w in writes if _outside(w["target"])]
    non_agent_work = [
        w for w in writes
        if not _outside(w["target"]) and "/.agent-work/" not in _resolve(w["target"])
    ]

    # Frozen-extractor exposure, measured rather than patched.
    order_p = run_dir / "ordering.json"
    suppressed: list[dict] = []
    if order_p.is_file():
        for c in json.loads(order_p.read_text(encoding="utf-8")).get("calls", []):
            if "skill-corpus" in c["buckets"] and MAP_TOKEN.search(c.get("target", "")):
                suppressed.append({"index": c["index"], "tool": c["tool"],
                                   "target": c["target"][:200]})

    return {
        "run": run_dir.name,
        "captured": True,
        "transcript_complete": not truncated,
        "verdict": verdict,
        "treatment_verified": treatment_ok,
        "tool_call_count": len(calls),
        "skill_invocations": len(skill_calls),
        "skill_calls": skill_calls,
        "commander_invocation_indices": [c["index"] for c in commander_calls],
        "commander_served_by": commander_loads,
        "all_skill_loads": loads,
        "init_constellation_entries": len(con),
        "init_duplicated_names": len(dupes),
        "write_audit": {
            "count": len(writes),
            "calls": writes,
            "writes_outside_own_worktree": escaping,
            "writes_inside_worktree_but_outside_agent_work": non_agent_work,
            "clean": not escaping and not non_agent_work,
        },
        "forbidden_operations": forbidden,
        "map_credit_suppressed_by_corpus_rule": suppressed,
        "tool_histogram": dict(Counter(c["tool"] for c in calls).most_common()),
        "final_answer_chars": len(result_text),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dirs", nargs="+")
    args = p.parse_args()
    rc = 0
    for d in args.run_dirs:
        run = Path(d)
        out = analyze(run)
        (run / "treatment.json").write_text(json.dumps(out, indent=2) + "\n",
                                            encoding="utf-8", newline="\n")
        served = ", ".join(sorted({l["base_dir"] for l in out.get("commander_served_by", [])})) or "-"
        wa = out.get("write_audit", {})
        print(f"{run.name}: {out['verdict']}  calls={out.get('tool_call_count')} "
              f"skill_calls={out.get('skill_invocations')} "
              f"cmdr_at={out.get('commander_invocation_indices')} "
              f"served_by={served} "
              f"writes={wa.get('count')} write_clean={wa.get('clean')} "
              f"forbidden={len(out.get('forbidden_operations', []))} "
              f"map_credit_suppressed={len(out.get('map_credit_suppressed_by_corpus_rule', []))}")
        if not out.get("treatment_verified"):
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
