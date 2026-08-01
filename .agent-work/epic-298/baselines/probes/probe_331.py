#!/usr/bin/env python
"""PROBE for issue #331 — NOT part of the frozen five-run PRE arm (#299).

One question, one variable. The #299 arm recorded ZERO `Skill` invocations across five
runs (BASELINE_RECORD.md Finding 2). Its declared limitation 4 names a live alternative
explanation: the brief's required `FILES I WOULD CHANGE` output pushes subjects toward
path-hunting and away from conceptual orientation, and that — not the corpus — may be
what suppressed invocation.

This re-runs ONE task (#698) with that output demand removed and NOTHING else changed.

WHY THE BRIEF IS DERIVED, NOT RETYPED
    The one-clause diff is applied by `str.replace` against `capture_baseline.BRIEF`
    itself, guarded by an assertion that the clause is present verbatim. A retyped brief
    could drift in whitespace or wording and silently smuggle a second variable into a
    single-variable experiment; a derived one cannot.

WHY THE CORPUS CARRIES A PROVENANCE SENTINEL (issue #332)
    The subject's `.claude/skills` copy is not the only corpus on this box: ~19 identically
    named constellation skills also sit in the GLOBAL `~/.claude/skills`, and `system/init`
    shows one merged list (each name twice). So "a skill was invoked" would not by itself
    establish WHICH copy served it — and that is the quantity under measurement.

    Every SKILL.md in the probe corpus carries an HTML-comment sentinel after its
    frontmatter. Frontmatter is untouched, so the trigger surface (name + description) is
    byte-identical to the #299 corpus and the treatment is unchanged for a probe about
    *whether* invocation happens.

    A stronger discriminator was found while validating the sentinel and is used as the
    primary readout: Claude Code prefixes loaded skill content with a literal
    `Base directory for this skill: <absolute path>` line, which names the serving copy
    outright. The sentinel is retained as an independent second witness on content bytes.

THIS RUN'S CORPUS ID DELIBERATELY DIFFERS FROM THE FROZEN ONE
    Pre-sentinel the probe corpus reproduces `sha256:3a30a64b...` exactly (verified). The
    sentinel changes it to `sha256:7dd678d8...`. That divergence is a feature: it makes the
    probe mechanically impossible to mistake for a #299 run.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_cb = _load("capture_baseline", HERE.parent / "capture_baseline.py")
_eval = sys.modules["run_skill_eval"]

PIN = _cb.PIN

# ---------------------------------------------------------------------------
# THE ONE VARIABLE — verbatim before/after.
# ---------------------------------------------------------------------------
BEFORE_CLAUSE = (
    "Understand the problem, then produce a plan. Your plan must name the specific files you\n"
    "would change and explain why each one. Finish by stating your file list plainly under a\n"
    "final heading `FILES I WOULD CHANGE`, one path per line.\n"
)
AFTER_CLAUSE = "Understand the problem, then produce a plan.\n"

if BEFORE_CLAUSE not in _cb.BRIEF:
    raise SystemExit(
        "capture_baseline.BRIEF no longer contains the frozen output-demand clause — "
        "refusing to run: the probe's single-variable claim would be unfounded."
    )
BRIEF = _cb.BRIEF.replace(BEFORE_CLAUSE, AFTER_CLAUSE)
if BRIEF == _cb.BRIEF or AFTER_CLAUSE not in BRIEF:
    raise SystemExit("brief substitution did not apply")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--issue", type=int, default=698)
    p.add_argument("--worktree", required=True, help="PINNED f1Brainz worktree (cwd for the subject)")
    p.add_argument("--out", required=True)
    p.add_argument("--skills", required=True, help="sentinel-bearing probe corpus dir")
    p.add_argument("--corpus-id", required=True)
    p.add_argument("--sentinel", required=True)
    p.add_argument("--repo", default="fredcai6/f1Brainz")
    p.add_argument("--model", default="claude-opus-5")
    p.add_argument("--timeout", type=int, default=2400)
    args = p.parse_args()

    worktree = Path(args.worktree).resolve()
    run_dir = Path(args.out).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    head = subprocess.run(["git", "-C", str(worktree), "rev-parse", "HEAD"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
    if head != PIN:
        raise SystemExit(f"worktree {worktree} is at {head}, not the pin {PIN}")

    dirty = subprocess.run(["git", "-C", str(worktree), "status", "--porcelain"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
    residue = [ln for ln in dirty.splitlines() if ".claude/skills" not in ln]
    if residue:
        raise SystemExit(f"worktree {worktree} is not pristine — refusing to reuse it:\n"
                         + "\n".join(residue[:20]))

    title, body = _cb.fetch_issue(args.repo, args.issue)
    prompt = BRIEF.format(n=args.issue, repo=args.repo, title=title, body=body)
    (run_dir / "brief.md").write_text(prompt, encoding="utf-8", newline="\n")
    (run_dir / "brief_diff.md").write_text(
        "# The one clause changed (probe #331 vs frozen #299 brief)\n\n"
        "## BEFORE (frozen, `capture_baseline.BRIEF`)\n\n```\n" + BEFORE_CLAUSE + "```\n\n"
        "## AFTER (this probe)\n\n```\n" + AFTER_CLAUSE + "```\n\n"
        "Applied by `str.replace` against the frozen brief, guarded by a presence assertion.\n"
        "No other byte of the brief differs.\n",
        encoding="utf-8", newline="\n")

    run_skills = worktree / ".claude" / "skills"
    if run_skills.exists():
        shutil.rmtree(run_skills)
    shutil.copytree(args.skills, run_skills,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    seen = _eval.stable_corpus_id(run_skills, Path(args.skills))
    if seen != args.corpus_id:
        raise SystemExit(f"corpus mismatch: {seen} != {args.corpus_id}")

    # The sentinel must actually be in the installed copy, or its absence downstream
    # would be unreadable rather than informative.
    stamped = sum(1 for f in run_skills.rglob("SKILL.md")
                  if args.sentinel in f.read_text(encoding="utf-8", errors="replace"))
    if stamped == 0:
        raise SystemExit("sentinel absent from the installed corpus — refusing to run")

    argv = ["claude", "-p", prompt, "--model", args.model,
            "--permission-mode", "acceptEdits",
            "--output-format", "stream-json", "--verbose"]

    def git_state() -> dict:
        g = lambda *a: subprocess.run(["git", "-C", str(worktree), *a],
                                      capture_output=True, text=True, encoding="utf-8",
                                      errors="replace").stdout.strip()
        return {"head": g("rev-parse", "HEAD"), "status": g("status", "--porcelain")}

    before = git_state()
    (run_dir / "meta.json").write_text(json.dumps({
        "kind": "PROBE-331",
        "not_baseline_data": True,
        "issue": args.issue, "pin": PIN, "model": args.model,
        "corpus_id": args.corpus_id,
        "corpus_id_pre_sentinel": "sha256:3a30a64b02df4dfad896e68aba2c1e46d3f080caaaf6ab98d1fab284d91f0c2d",
        "sentinel": args.sentinel,
        "skills_stamped": stamped,
        "worktree": str(worktree),
        "status": "launched", "launched_at": time.time(),
        "git_before": before,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")

    started = time.time()
    outcome = _eval.launch_agent(
        argv, cwd=str(worktree), env=_cb.scrubbed_env(),
        stdout_path=str(run_dir / "stream.ndjson"),
        stderr_path=str(run_dir / "stderr.txt"),
        timeout=args.timeout,
    )
    elapsed = time.time() - started
    after = git_state()

    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    meta.update({
        "status": "timed-out" if outcome.timed_out else "finished",
        "exit_code": outcome.exit_code,
        "elapsed_seconds": round(elapsed, 1),
        "finished_at": time.time(),
        "git_after": after,
        "git_unchanged": before == after,
    })
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n",
                                       encoding="utf-8", newline="\n")

    shutil.rmtree(run_skills, ignore_errors=True)

    print(f"probe #{args.issue}: exit={outcome.exit_code} timed_out={outcome.timed_out} "
          f"elapsed={elapsed:.0f}s git_unchanged={before == after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
