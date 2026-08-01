#!/usr/bin/env python
"""Capture ONE measured baseline run for epic #298 (issue #299), pre-change arm.

Launches a headless Commander against a PINNED f1Brainz worktree with the pre-#304
corpus installed, records the full tool-call stream, and stops at plan stage.

Design notes that are load-bearing:

* The launcher is reused from `scripts/run_skill_eval.py` (`launch_agent`) rather than
  reinvented: it already owns the Windows process-tree kill, the pipe-drain grace, and
  the liveness heartbeat that a naive `subprocess.run(timeout=)` gets wrong on this
  platform. It is also the form the epic-138/#145 precedent established as the
  sanctioned way to spawn a subject (a hand-rolled `claude -p` was classifier-refused;
  the Popen-based harness wrapper was not).

* `--output-format stream-json --verbose` is what makes the ordering measure real: it
  emits every `tool_use` block with its input, in order, so the measure is extracted
  mechanically instead of self-reported by the subject.

* THE SUBJECT MUST NOT KNOW IT IS BEING MEASURED. The brief carries the real issue and
  a plan-stage scope boundary and NOTHING about epic #298, maps, architecture, or
  observation. An agent told its map-reading is watched will read the map.

* The environment is SCRUBBED of CLAUDE_* variables. A probe run inherited an unrelated
  additional working directory from the launching session and went looking in it; the
  corpus under measurement must be the corpus that actually ran.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_eval = _load("run_skill_eval", REPO_ROOT / "scripts" / "run_skill_eval.py")

PIN = "3541d2929b19de37107ae13e56776b7162d07255"

# The brief. Deliberately silent on maps, architecture, epic #298, and measurement.
# It names the issue and the deliverable, exactly as an ordinary planning dispatch would.
BRIEF = """You are picking up issue #{n} in this repository ({repo}).

--- ISSUE #{n}: {title} ---
{body}
--- END ISSUE ---

This is a PLANNING engagement only. Implementation is a separate, later engagement and
is out of scope for you: do not modify, commit, push, or open a pull request, and do not
comment on the issue.

Understand the problem, then produce a plan. Your plan must name the specific files you
would change and explain why each one. Finish by stating your file list plainly under a
final heading `FILES I WOULD CHANGE`, one path per line.
"""


FROZEN_ISSUES = Path(__file__).resolve().parent / "issues.frozen.json"


def fetch_issue(repo: str, number: int) -> tuple[str, str]:
    """Read one issue from the FROZEN snapshot, not live.

    The commit is pinned but issue text is not: if any of the five is edited between the
    PRE and POST arms, the arms would receive different briefs — and the brief is where
    every path give-away lives. Snapshotting makes the arms' most load-bearing shared
    input immutable. `freeze_issues.py` writes the snapshot; it is committed alongside
    the rubric, before any run."""
    if not FROZEN_ISSUES.is_file():
        raise SystemExit(f"frozen issue snapshot missing: {FROZEN_ISSUES} — run freeze_issues.py first")
    snap = json.loads(FROZEN_ISSUES.read_text(encoding="utf-8"))
    key = str(number)
    if key not in snap["issues"]:
        raise SystemExit(f"issue #{number} not in frozen snapshot")
    rec = snap["issues"][key]
    return rec["title"], rec["body"]


def scrubbed_env() -> dict:
    """os.environ minus CLAUDE_* — see module docstring."""
    return {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_")}


def install_corpus(source_worktree: Path, temp_root: Path) -> tuple[Path, str]:
    """Install the pre-#304 corpus once and fingerprint it install-path-invariantly, so
    #307 can prove the post arm differs from this one ONLY by #304."""
    skills_dir = _eval.temp_install(str(source_worktree), str(temp_root))
    corpus_id = _eval.write_stable_corpus_marker(skills_dir, _eval._source_commit())
    return Path(skills_dir), corpus_id


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--issue", type=int, required=True)
    p.add_argument("--worktree", required=True, help="PINNED f1Brainz worktree (cwd for the subject)")
    p.add_argument("--out", required=True, help="run directory for artifacts")
    p.add_argument("--skills", required=True, help="already-installed corpus dir")
    p.add_argument("--corpus-id", required=True)
    p.add_argument("--repo", default="fredcai6/f1Brainz")
    p.add_argument("--model", default="claude-opus-5")
    p.add_argument("--timeout", type=int, default=2400)
    args = p.parse_args()

    worktree = Path(args.worktree).resolve()
    run_dir = Path(args.out).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    # Confirm the worktree really is at the pin. A baseline spread across a moving map
    # measures different things run to run; this is the single most load-bearing number.
    head = subprocess.run(["git", "-C", str(worktree), "rev-parse", "HEAD"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
    if head != PIN:
        raise SystemExit(f"worktree {worktree} is at {head}, not the pin {PIN}")

    # ONE WORKTREE PER RUN. A reused worktree lets run N inherit whatever run N-1 wrote,
    # which is data loss, not friction (LAUNCH_ORDER-299 §Workspace). Assert cleanliness
    # rather than trusting it: anything already dirty here means reuse.
    dirty = subprocess.run(["git", "-C", str(worktree), "status", "--porcelain"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
    residue = [ln for ln in dirty.splitlines() if ".claude/skills" not in ln]
    if residue:
        raise SystemExit(
            f"worktree {worktree} is not pristine — refusing to reuse it for a measured "
            f"run:\n" + "\n".join(residue[:20])
        )

    title, body = fetch_issue(args.repo, args.issue)
    prompt = BRIEF.format(n=args.issue, repo=args.repo, title=title, body=body)
    (run_dir / "brief.md").write_text(prompt, encoding="utf-8", newline="\n")

    # Install the corpus into the subject's own workspace.
    run_skills = worktree / ".claude" / "skills"
    if run_skills.exists():
        shutil.rmtree(run_skills)
    shutil.copytree(args.skills, run_skills,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    seen = _eval.stable_corpus_id(run_skills, Path(args.skills))
    if seen != args.corpus_id:
        raise SystemExit(f"corpus mismatch: {seen} != {args.corpus_id}")

    argv = ["claude", "-p", prompt, "--model", args.model,
            "--permission-mode", "acceptEdits",
            "--output-format", "stream-json", "--verbose"]

    # Record git state BEFORE, so "nothing landed in f1Brainz" is verified, not asserted.
    def git_state() -> dict:
        g = lambda *a: subprocess.run(["git", "-C", str(worktree), *a],
                                      capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
        return {"head": g("rev-parse", "HEAD"), "status": g("status", "--porcelain")}

    before = git_state()
    (run_dir / "meta.json").write_text(json.dumps({
        "issue": args.issue, "pin": PIN, "model": args.model,
        "corpus_id": args.corpus_id, "worktree": str(worktree),
        "status": "launched", "launched_at": time.time(),
        "git_before": before,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")

    started = time.time()
    outcome = _eval.launch_agent(
        argv, cwd=str(worktree), env=scrubbed_env(),
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

    # The corpus copy is scaffolding, not evidence — drop it so the archive stays small
    # and the worktree sweep is clean.
    shutil.rmtree(run_skills, ignore_errors=True)

    print(f"run #{args.issue}: exit={outcome.exit_code} timed_out={outcome.timed_out} "
          f"elapsed={elapsed:.0f}s git_unchanged={before == after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
