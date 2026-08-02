#!/usr/bin/env python
"""Capture ONE measured PRE-B run — the Commander-loaded pre-#304 arm (epic #298).

PRE-B IS A SECOND ARM, NOT A REPAIR OF PRE-A. It pairs with the POST arm and NOT with
PRE-A. See `PREB_RECORD.md` §"Three arms, two series".

Everything is held from `../baselines/capture_baseline.py` except the treatment: the
subject is told to load `constellation-commander` and drive its spine to the plan step.

WHY THE BRIEF IS DERIVED, NOT RETYPED
    The diff is applied by `str.replace` against `capture_baseline.BRIEF` itself, each
    substitution guarded by a presence assertion. A retyped brief could drift in
    whitespace or wording and silently smuggle an extra variable into the arm; a derived
    one cannot. `brief_diff.md` is written per run with every changed byte, verbatim.

WHY THERE IS NO CORPUS INSTALL — and why that is the honest configuration
    Issue #332, resolved during the #331 probe: `~/.claude/skills` SHADOWS any
    `<worktree>/.claude/skills` install. Both copies register in `system/init` (every
    constellation name appears twice) but the global copy is what SERVES. Installing a
    pinned corpus into the worktree therefore does not deliver it — it produces a
    treatment that looks controlled and is not.

    So PRE-B installs nothing and measures the corpus AS ACTUALLY INSTALLED, and instead
    ASSERTS the absence of a worktree copy. With no second copy, `system/init` lists each
    constellation name ONCE, which is itself a check that nothing shadowed anything. The
    global corpus is witnessed by fingerprint before the first run and after the last
    (`fingerprint_global_corpus.py`) rather than pinned.

WHY THE TREATMENT IS VERIFIED PER RUN AND NOT ASSUMED
    A run with no verified Commander load is a FAILED CAPTURE, not a data point — an
    unverified treatment is worse than no arm, because it looks valid. The discriminator
    is the harness-emitted `Base directory for this skill: <absolute path>` line, which
    names the serving copy outright and cannot be defeated by content truncation.
    `verify_treatment.py` reads it; this script only records the transcript.

THE SUBJECT MUST NOT KNOW IT IS BEING MEASURED, beyond what invoking the Commander
    itself requires. Nothing about epic #298, maps, architecture, or observation appears
    in the brief. An agent told its map-reading is watched will read the map.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINES = HERE.parent / "baselines"
REPO_ROOT = HERE.parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_cb = _load("capture_baseline", BASELINES / "capture_baseline.py")
_eval = sys.modules["run_skill_eval"]

PIN = _cb.PIN

# --------------------------------------------------------------------------- #
# THE TREATMENT — verbatim before/after, applied to the frozen brief.
#
# Two substitutions, not one, and the second exists only because the first makes it
# necessary: a Commander driven to `plan` MUST author a mission frame and `execute.json`,
# so the frozen brief's blanket "do not modify" would forbid the very treatment under
# test. The carve-out is scoped as narrowly as it can be — working notes under
# `.agent-work/` only — and every other prohibition is left byte-identical.
# --------------------------------------------------------------------------- #
SCOPE_BEFORE = (
    "This is a PLANNING engagement only. Implementation is a separate, later engagement and\n"
    "is out of scope for you: do not modify, commit, push, or open a pull request, and do not\n"
    "comment on the issue.\n"
)
SCOPE_AFTER = (
    "This is a PLANNING engagement only. Implementation is a separate, later engagement and\n"
    "is out of scope for you: do not modify this repository's source, tests, or documentation,\n"
    "do not commit, push, or open a pull request, and do not comment on the issue. Your own\n"
    "working notes and planning artifacts under `.agent-work/` are the one exception, and are\n"
    "expected.\n"
)

TASK_BEFORE = (
    "Understand the problem, then produce a plan. Your plan must name the specific files you\n"
    "would change and explain why each one. Finish by stating your file list plainly under a\n"
    "final heading `FILES I WOULD CHANGE`, one path per line.\n"
)
TASK_AFTER = (
    "Run this as a Commander. Load the `constellation-commander` skill and drive its spine\n"
    # ASCII only past this point: the brief is passed as an argv element to `claude -p` on
    # Windows, and a non-ASCII character there is a mojibake risk in the one string whose
    # bytes must be identical across every run of the arm.
    "through its steps in order, stopping once the `plan` step is complete: the mission frame\n"
    "authored and `execute.json` authored. Do not enter `execute`: stop there and return.\n"
    "No human is reachable for this engagement, so wherever a step calls for a human decision,\n"
    "record what you would have asked, decide it yourself, and carry on rather than waiting.\n"
    "\n"
    "Your plan must name the specific files you would change and explain why each one. Finish\n"
    "by stating your file list plainly under a final heading `FILES I WOULD CHANGE`, one path\n"
    "per line.\n"
)

for _clause, _label in ((SCOPE_BEFORE, "scope"), (TASK_BEFORE, "task")):
    if _clause not in _cb.BRIEF:
        raise SystemExit(
            f"capture_baseline.BRIEF no longer contains the frozen {_label} clause verbatim — "
            "refusing to run: PRE-B's held-constant claim against PRE-A would be unfounded."
        )

BRIEF = _cb.BRIEF.replace(SCOPE_BEFORE, SCOPE_AFTER).replace(TASK_BEFORE, TASK_AFTER)
if SCOPE_AFTER not in BRIEF or TASK_AFTER not in BRIEF:
    raise SystemExit("brief substitution did not apply")

BRIEF_DIFF = (
    "# PRE-B brief: every byte that differs from the frozen #299 brief\n\n"
    "Applied by `str.replace` against `capture_baseline.BRIEF`, each guarded by a presence\n"
    "assertion. Never retyped. No other byte of the brief differs — the issue text, the\n"
    "repository line, and the `FILES I WOULD CHANGE` output demand are byte-identical to\n"
    "PRE-A.\n\n"
    "## Substitution 1 of 2 — scope\n\n"
    "Needed only because substitution 2 makes it necessary: a Commander driven to `plan`\n"
    "must author a mission frame and `execute.json`, which the frozen blanket \"do not\n"
    "modify\" would forbid. The carve-out is scoped to `.agent-work/` and nothing else;\n"
    "commit / push / PR / issue-comment prohibitions are untouched.\n\n"
    "### BEFORE\n\n```\n" + SCOPE_BEFORE + "```\n\n"
    "### AFTER\n\n```\n" + SCOPE_AFTER + "```\n\n"
    "## Substitution 2 of 2 — the treatment\n\n"
    "The whole point of the arm. The `FILES I WOULD CHANGE` demand is carried through\n"
    "unchanged so the plan-stage output and the seam-grading input stay comparable.\n\n"
    "### BEFORE\n\n```\n" + TASK_BEFORE + "```\n\n"
    "### AFTER\n\n```\n" + TASK_AFTER + "```\n"
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--issue", type=int, required=True)
    p.add_argument("--worktree", required=True, help="PINNED f1Brainz worktree (cwd for the subject)")
    p.add_argument("--out", required=True)
    p.add_argument("--repo", default="fredcai6/f1Brainz")
    p.add_argument("--model", default="claude-opus-5")
    p.add_argument("--timeout", type=int, default=3600)
    p.add_argument("--attempt", type=int, default=1,
                   help="recorded verbatim; every attempt is archived, none is overwritten")
    # THE ONLY CHANGE THIS SCRIPT TOOK FOR THE POST ARM (#307), and it is a LABEL.
    #
    # POST pairs with PRE-B, so POST must be measured BY THIS INSTRUMENT: rebuilding a
    # runner would give any PRE-B/POST difference two candidate causes -- the treatment or
    # the new code -- and the arm could not separate them. The one thing POST genuinely
    # needs is to not claim in its own meta.json that it is PRE-B.
    #
    # Additive and default-preserving on purpose: the brief bytes, argv, env scrub, pin
    # assertion, pristine-worktree assertion, no-worktree-corpus assertion, launch path and
    # every recorded measure are untouched, and omitting the flag reproduces PRE-B exactly.
    p.add_argument("--arm", default="PRE-B",
                   help="arm label recorded in meta.json; the measured path does not read it")
    args = p.parse_args()

    worktree = Path(args.worktree).resolve()
    run_dir = Path(args.out).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    head = subprocess.run(["git", "-C", str(worktree), "rev-parse", "HEAD"],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout.strip()
    if head != PIN:
        raise SystemExit(f"worktree {worktree} is at {head}, not the pin {PIN}")

    # ONE WORKTREE PER RUN. A reused worktree lets run N inherit run N-1's `.agent-work/`,
    # which under the Commander treatment is not cosmetic: an existing spine.json would
    # let the subject skip the very steps under measurement.
    dirty = subprocess.run(["git", "-C", str(worktree), "status", "--porcelain"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace").stdout.strip()
    if dirty:
        raise SystemExit(
            f"worktree {worktree} is not pristine — refusing to reuse it for a measured "
            f"run:\n" + "\n".join(dirty.splitlines()[:20])
        )

    # PRE-B installs NO corpus (issue #332). Assert the absence, so `system/init` listing
    # each constellation name exactly once is a positive check rather than a hope.
    if (worktree / ".claude" / "skills").exists():
        raise SystemExit(
            f"{worktree}/.claude/skills exists — PRE-B measures the corpus AS INSTALLED "
            "and a worktree copy would make it ambiguous which copy registered. Remove it."
        )

    title, body = _cb.fetch_issue(args.repo, args.issue)
    prompt = BRIEF.format(n=args.issue, repo=args.repo, title=title, body=body)
    (run_dir / "brief.md").write_text(prompt, encoding="utf-8", newline="\n")
    (run_dir / "brief_diff.md").write_text(BRIEF_DIFF, encoding="utf-8", newline="\n")

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
        "arm": args.arm,
        "pairs_with": "PRE-B" if args.arm == "POST" else "POST",
        "does_not_pair_with": "PRE-A (#299) — different treatment, see PREB_RECORD.md",
        "issue": args.issue, "pin": PIN, "model": args.model,
        "attempt": args.attempt,
        "corpus": "global-as-installed (no pinned install; see #332)",
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

    print(f"run #{args.issue}: exit={outcome.exit_code} timed_out={outcome.timed_out} "
          f"elapsed={elapsed:.0f}s git_unchanged={before == after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
