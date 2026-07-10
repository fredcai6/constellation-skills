#!/usr/bin/env python
"""Corpus skill-eval runner — the PURE, agent-free core (#106, gate g2).

Gates a candidate constellation corpus by running each scenario N-of-M times and
scoring the result with PROCESS checks. The verdict is carried by process checks
alone; answer-correctness checks are advisory and can NEVER move it (structural
T3). Environment flake can never FAIL a good corpus — timed-out / usage-limited /
errored runs are FENCED and excluded from the N-of-M tally (infra-fence).

This module is built test-first and is fully agent-free except the single
`launch_agent` seam (the ONLY place a real agent subprocess would be spawned).
`launch_agent` and `temp_install` are inert stubs here (raising NotImplementedError
with a "wired at g3" message); the live wiring lands at g3. `--dry-run` and
`--dry-run-fail` work end-to-end NOW by injecting a fake launcher + a dry installer
through the same seams the unit layer uses, so no path here ever reaches a real
`claude`.

Seam pattern mirrors run_crew.py: the module-level default launcher/installer are
resolved INSIDE the orchestration function at CALL time, so a monkeypatched (or
CLI-selected) seam takes effect.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------- #
# import (never edit) install_constellation for the corpus-hash primitive
# --------------------------------------------------------------------------- #
_HERE = Path(__file__).resolve().parent


def _load_install_constellation():
    if "install_constellation" in sys.modules:
        return sys.modules["install_constellation"]
    spec = importlib.util.spec_from_file_location(
        "install_constellation", _HERE / "install_constellation.py"
    )
    module = importlib.util.module_from_spec(spec)
    # Register BEFORE exec so the module's own dataclasses resolve their
    # __module__ against a live sys.modules entry (Python 3.12+ dataclass
    # KW_ONLY probe dereferences sys.modules[cls.__module__]).
    sys.modules["install_constellation"] = module
    spec.loader.exec_module(module)
    return module


_install = _load_install_constellation()
_hash_file = _install._hash_file
_source_commit = _install._source_commit

# Pilot tier — one model tier below prod, per the frozen contract (§(e)); pilots
# run cheaper because a wave commander died to a usage limit this epic.
DEFAULT_MODEL = "sonnet"
DEFAULT_N = 2
DEFAULT_M = 3
DEFAULT_TIMEOUT_SECONDS = 1800
DEFAULT_LAUNCHER = "claude"

# The completion stub a finished run leaves in its workspace. A canned test run
# and the dry-run launcher fabricate the same shape the live run will (run-dir
# contract): workspace/<COMPLETION_ARTIFACT> + a spine.json terminal.
COMPLETION_ARTIFACT = "eval-complete.txt"
CORPUS_MARKER = "CORPUS.json"

# Infra markers sniffed in a run's stderr — any hit FENCES the run (inconclusive),
# so environment flake can only ever yield INCONCLUSIVE, never FAIL a good corpus.
INFRA_MARKERS = ("usage limit", "rate limit", "quota", "overloaded", "429")


class EvalConfigError(Exception):
    """A scenario that violates the directory-is-schema contract (missing task.md,
    zero process checks, unreadable scenario.toml). Surfaces as CLI exit 3."""


# --------------------------------------------------------------------------- #
# dataclasses (exact named fields per the frozen contract)
# --------------------------------------------------------------------------- #
@dataclass
class Scenario:
    id: str
    task_prompt: str
    process_checks: list[Path]
    answer_checks: list[Path]
    fixture_dir: Path | None
    n: int
    m: int
    model: str | None
    timeout_seconds: int


@dataclass
class CheckResult:
    id: str
    passed: bool
    evidence: str
    is_answer: bool


@dataclass
class LaunchOutcome:
    """The observable result of one launch attempt. `launch_agent` (and the fake
    launchers) return this; `classify_run` consumes it. Fenceable conditions are
    flags so classification stays a pure function of the outcome."""
    exit_code: int | None
    stderr_text: str = ""
    timed_out: bool = False
    launch_error: bool = False
    corpus_mismatch: bool = False


@dataclass
class RunResult:
    status: str  # completed-pass | completed-fail | inconclusive | errored
    reason: str | None
    check_results: list


@dataclass
class Verdict:
    status: str  # PASS | FAIL | INCONCLUSIVE
    exit_code: int
    completed_count: int
    passed_count: int
    fenced_count: int
    corpus_id: str | None
    source_commit: str | None
    per_run: list = field(default_factory=list)


# --------------------------------------------------------------------------- #
# load_scenario — PURE, total; directory-is-schema with structural T3
# --------------------------------------------------------------------------- #
def load_scenario(scenario_dir) -> Scenario:
    """Parse a scenario directory into a Scenario. PURE and total: it reads only
    the directory, never launches anything, and raises EvalConfigError (never a
    bare error) on any schema violation.

    Structural T3: `checks/*.py` are PROCESS checks and carry the verdict;
    `checks/answer/*.py` are advisory and never gate. A scenario with ZERO process
    checks is a hard config error — you cannot pass on answer checks alone, and
    you cannot pass with no process check."""
    scenario_dir = Path(scenario_dir)
    if not scenario_dir.is_dir():
        raise EvalConfigError(f"scenario directory does not exist: {scenario_dir}")

    task = scenario_dir / "task.md"
    if not task.is_file():
        raise EvalConfigError(f"scenario is missing required task.md: {scenario_dir}")
    task_prompt = task.read_text(encoding="utf-8")

    checks_dir = scenario_dir / "checks"
    # checks/*.py is non-recursive, so checks/answer/*.py is NOT swept into the gate.
    process_checks = sorted(checks_dir.glob("*.py")) if checks_dir.is_dir() else []
    if not process_checks:
        raise EvalConfigError(
            f"scenario has ZERO process checks (checks/*.py) — cannot pass on answer "
            f"checks alone (structural T3): {scenario_dir}"
        )
    answer_dir = checks_dir / "answer"
    answer_checks = sorted(answer_dir.glob("*.py")) if answer_dir.is_dir() else []

    fixture = scenario_dir / "fixture"
    fixture_dir = fixture if fixture.is_dir() else None

    overrides: dict = {}
    toml_path = scenario_dir / "scenario.toml"
    if toml_path.is_file():
        import tomllib

        try:
            overrides = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            raise EvalConfigError(f"scenario.toml is not valid TOML: {toml_path}: {exc}") from exc

    return Scenario(
        id=str(overrides.get("id", scenario_dir.name)),
        task_prompt=task_prompt,
        process_checks=process_checks,
        answer_checks=answer_checks,
        fixture_dir=fixture_dir,
        n=int(overrides.get("n", DEFAULT_N)),
        m=int(overrides.get("m", DEFAULT_M)),
        model=overrides.get("model", DEFAULT_MODEL),
        timeout_seconds=int(overrides.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)),
    )


# --------------------------------------------------------------------------- #
# build_eval_argv — PURE; mirrors run_crew.build_crew_argv
# --------------------------------------------------------------------------- #
def build_eval_argv(launcher: str, *, prompt: str, model: str | None) -> list[str]:
    """PURE construction of the headless agent command line. Exactly
    `[launcher, "-p", prompt]`, plus `--model <model>` when a model is set. Kept
    separate so tests assert on the argv without spawning anything."""
    argv = [launcher, "-p", prompt]
    if model:
        argv += ["--model", model]
    return argv


def wrap_prompt(task_prompt: str) -> str:
    """The verbatim task wrapped with the completion clause (contract §(d))."""
    return (
        task_prompt.rstrip()
        + "\n\n"
        + "The constellation skills are installed in this project. Run the workflow "
        + "to completion. The run is complete only when "
        + f"`{COMPLETION_ARTIFACT}` exists in the workspace."
    )


# --------------------------------------------------------------------------- #
# run_check — run ONE check script against a run-dir (a CHECK subprocess, not an
# agent). Allowed in tests against a canned run-dir.
# --------------------------------------------------------------------------- #
def run_check(script_path, run_dir, *, is_answer: bool = False) -> CheckResult:
    """Execute `python <script> <run-dir>` as a subprocess. Exit 0 => passed;
    stdout's first line is the evidence printed verbatim into the verdict. This is
    a CHECK subprocess (its only input is a directory, its only output an exit
    code) — never an agent launch."""
    script_path = Path(script_path)
    proc = subprocess.run(
        [sys.executable, str(script_path), str(run_dir)],
        capture_output=True,
        text=True,
    )
    stdout = (proc.stdout or "").strip()
    evidence = stdout.splitlines()[0] if stdout else ""
    return CheckResult(
        id=script_path.stem,
        passed=proc.returncode == 0,
        evidence=evidence,
        is_answer=is_answer,
    )


# --------------------------------------------------------------------------- #
# is_infra_marker / classify_run — PURE infra-fence + pass/fail classification
# --------------------------------------------------------------------------- #
def is_infra_marker(text) -> bool:
    """Whether `text` carries a transient-environment marker (usage/rate limit,
    quota, overloaded, 429). PURE. A hit fences the run as inconclusive."""
    low = (text or "").lower()
    return any(marker in low for marker in INFRA_MARKERS)


def classify_run(outcome: LaunchOutcome, *, completion_present: bool,
                 completion_fresh: bool, process_results: list) -> RunResult:
    """Resolve one launch attempt to exactly one class (contract §(i) infra-fence
    table). PURE.

      inconclusive (fenced): timeout, or a usage/rate-limit/overloaded/429 marker
                             sniffed in stderr;
      errored (fenced):      launch failure, corpus mismatch, or a non-zero exit
                             with NO marker AND no completion;
      completed-pass:        completed and every process check passed;
      completed-fail:        completed (incl. exit 0 with no spine terminal) but a
                             process check failed.

    A run "completed" when its completion artifact is present+fresh OR the agent
    exited 0 — so an exit-0 run with no spine terminal is still tallied (as a
    fail if a process check failed), never silently fenced."""
    if outcome.timed_out:
        return RunResult(status="inconclusive", reason="timeout", check_results=list(process_results))
    if is_infra_marker(outcome.stderr_text):
        return RunResult(status="inconclusive", reason="infra-marker", check_results=list(process_results))
    if outcome.launch_error:
        return RunResult(status="errored", reason="launch-error", check_results=list(process_results))
    if outcome.corpus_mismatch:
        return RunResult(status="errored", reason="corpus-mismatch", check_results=list(process_results))

    completed = (completion_present and completion_fresh) or (outcome.exit_code == 0)
    if not completed:
        # non-zero exit, no marker, no completion -> environment/launch failure.
        return RunResult(status="errored", reason="nonzero-exit-no-completion",
                         check_results=list(process_results))

    all_pass = all(c.passed for c in process_results)
    if all_pass:
        return RunResult(status="completed-pass", reason=None, check_results=list(process_results))
    return RunResult(status="completed-fail", reason="process-check-failed",
                     check_results=list(process_results))


# --------------------------------------------------------------------------- #
# verdict — PURE N-of-M math over COMPLETED runs only
# --------------------------------------------------------------------------- #
def verdict(run_results: list, *, n: int, m: int,
            corpus_id: str | None = None, source_commit: str | None = None) -> Verdict:
    """The corpus verdict from the per-run classifications. PURE.

    Tally is over COMPLETED runs only (completed-pass/-fail); fenced runs
    (inconclusive/errored) are excluded. `completed < n => INCONCLUSIVE (exit 2)`;
    `passed >= n => PASS (exit 0)`; else `FAIL (exit 1)`. Environment flake can
    only ever yield INCONCLUSIVE, never FAIL a good corpus.

    2-of-3 is a regression-vs-variance smoke, NOT a statistical guarantee: it
    separates a corpus that reliably fails from one that reliably works and stops
    a single lucky/unlucky run from being the verdict."""
    completed = [r for r in run_results if r.status in ("completed-pass", "completed-fail")]
    passed = [r for r in completed if r.status == "completed-pass"]
    fenced = [r for r in run_results if r.status in ("inconclusive", "errored")]

    if len(completed) < n:
        status, exit_code = "INCONCLUSIVE", 2
    elif len(passed) >= n:
        status, exit_code = "PASS", 0
    else:
        status, exit_code = "FAIL", 1

    return Verdict(
        status=status,
        exit_code=exit_code,
        completed_count=len(completed),
        passed_count=len(passed),
        fenced_count=len(fenced),
        corpus_id=corpus_id,
        source_commit=source_commit,
        per_run=list(run_results),
    )


# --------------------------------------------------------------------------- #
# corpus provenance — sha256 id, marker, assert (PURE over a tree)
# --------------------------------------------------------------------------- #
def compute_corpus_id(skills_dir) -> str:
    """Content id of an installed skill tree: `"sha256:" + sha256(sorted
    (rel_posix_path, _hash_file(p)) over files)`. PURE. Reuses
    install_constellation._hash_file. The corpus marker (CORPUS.json) is excluded
    so writing the marker cannot perturb the id it records."""
    skills_dir = Path(skills_dir)
    pairs: list[tuple[str, str]] = []
    for path in sorted(skills_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name == CORPUS_MARKER:
            continue
        rel = path.relative_to(skills_dir).as_posix()
        pairs.append((rel, _hash_file(path)))
    digest = hashlib.sha256()
    for rel, file_hash in sorted(pairs):
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("utf-8"))
        digest.update(b"\n")
    return "sha256:" + digest.hexdigest()


def write_corpus_marker(skills_dir, source_commit: str) -> str:
    """Compute the corpus id and write `<skills_dir>/CORPUS.json`. Returns the id.
    A silent install bug cannot green a corpus that was never loaded: each run
    re-hashes its copy and asserts equality against this id (assert_corpus)."""
    skills_dir = Path(skills_dir)
    corpus_id = compute_corpus_id(skills_dir)
    marker = {"corpus_id": corpus_id, "source_commit": source_commit}
    (skills_dir / CORPUS_MARKER).write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    return corpus_id


def assert_corpus(run_skills_dir, expected_id: str) -> bool:
    """Whether a run's copied skill tree hashes to `expected_id`. A mismatch
    fences the run (corpus_mismatch), never silently counts."""
    return compute_corpus_id(run_skills_dir) == expected_id


# --------------------------------------------------------------------------- #
# the ONE real seam (inert until g3) + fake launchers for --dry-run
# --------------------------------------------------------------------------- #
def launch_agent(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome:
    """The ONLY place a real agent subprocess would be spawned. Inert stub at g2 —
    the live wiring lands at g3. Being inert, no unit path can ever reach a real
    `claude` through the default seam."""
    raise NotImplementedError("launch_agent is wired at g3 (#106)")


def temp_install(worktree, temp_root) -> Path:
    """Install the candidate corpus once under a system-temp dir and return its
    skills path. Inert stub at g2 — the live wiring (reusing
    install_constellation.install_skills) lands at g3."""
    raise NotImplementedError("temp_install is wired at g3 (#106)")


def _write_transcript(stdout_path, stderr_path, note: str) -> None:
    if stdout_path:
        Path(stdout_path).parent.mkdir(parents=True, exist_ok=True)
        Path(stdout_path).write_text(note + "\n", encoding="utf-8")
    if stderr_path:
        Path(stderr_path).parent.mkdir(parents=True, exist_ok=True)
        Path(stderr_path).write_text("", encoding="utf-8")


def dry_run_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome:
    """Fake launcher that synthesizes a PASSING workspace (completion artifact +
    spine.json terminal) so process checks pass. Spawns NOTHING — the CI smoke for
    the runner itself and caller #2's live target."""
    workspace = Path(cwd)
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / COMPLETION_ARTIFACT).write_text("dry-run complete\n", encoding="utf-8")
    (workspace.parent / "spine.json").write_text(
        json.dumps({"status": "done"}) + "\n", encoding="utf-8"
    )
    _write_transcript(stdout_path, stderr_path, "dry-run: synthesized passing workspace")
    return LaunchOutcome(exit_code=0)


def dry_run_fail_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome:
    """Fake launcher that synthesizes a BROKEN workspace (no completion artifact)
    so the process checks catch it — the agent-free FALSIFICATION FLOOR. Exits 0
    so the run is a COMPLETED-fail (tallied, exit 1), never fenced. Spawns
    NOTHING."""
    workspace = Path(cwd)
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "BROKEN.txt").write_text("dry-run-fail: no completion artifact\n", encoding="utf-8")
    (workspace.parent / "spine.json").write_text(
        json.dumps({"status": "in-progress"}) + "\n", encoding="utf-8"
    )
    _write_transcript(stdout_path, stderr_path, "dry-run-fail: synthesized broken workspace")
    return LaunchOutcome(exit_code=0)


def _dry_installer(worktree, temp_root) -> Path:
    """Fake installer for --dry-run/--dry-run-fail: materializes a minimal, valid
    skill tree under temp_root so corpus provenance (id + marker + assert) runs
    end-to-end with zero agent cost. This is dry-run scaffolding, NOT temp_install
    (which stays an inert stub until g3)."""
    skills = Path(temp_root) / "skills"
    stub = skills / "constellation-dry-run"
    stub.mkdir(parents=True, exist_ok=True)
    (stub / "SKILL.md").write_text("dry-run stub corpus\n", encoding="utf-8")
    return skills


# --------------------------------------------------------------------------- #
# orchestration — run_scenario(…, launch=…, installer=…)
# --------------------------------------------------------------------------- #
def _probe_completion(run_dir: Path, since: float) -> tuple[bool, bool]:
    """Whether the run's completion artifact is present and FRESH (mtime at/after
    `since`, floored to whole seconds so coarse fs mtime cannot falsely flag a
    same-second write — the run_crew freshness convention)."""
    artifact = run_dir / "workspace" / COMPLETION_ARTIFACT
    if not artifact.is_file():
        return False, False
    floor = float(int(since))
    return True, artifact.stat().st_mtime >= floor


def _run_once(scenario: Scenario, index: int, temp_root: Path, skills_dir: Path,
              corpus_id: str, launch) -> RunResult:
    """Execute (and score) ONE attempt into `run-<index>/`. Fabricates the run-dir
    shape, copies the corpus into an isolated `workspace/.claude/skills` and
    asserts its id, launches via the injected seam, probes completion, then runs
    the process (gating) and answer (advisory, recorded-not-gating) checks."""
    run_dir = temp_root / f"run-{index}"
    workspace = run_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    if scenario.fixture_dir is not None:
        shutil.copytree(scenario.fixture_dir, workspace, dirs_exist_ok=True)

    run_skills = workspace / ".claude" / "skills"
    shutil.copytree(skills_dir, run_skills)

    started = time.time()
    if not assert_corpus(run_skills, corpus_id):
        outcome = LaunchOutcome(exit_code=None, corpus_mismatch=True)
        present = fresh = False
        process_results: list = []
        answer_results: list = []
    else:
        prompt = wrap_prompt(scenario.task_prompt)
        argv = build_eval_argv(DEFAULT_LAUNCHER, prompt=prompt, model=scenario.model)
        outcome = launch(
            argv,
            cwd=str(workspace),
            env=dict(os.environ),
            stdout_path=str(run_dir / "transcript.txt"),
            stderr_path=str(run_dir / "stderr.txt"),
            timeout=scenario.timeout_seconds,
        )
        present, fresh = _probe_completion(run_dir, started)
        process_results = [run_check(c, run_dir) for c in scenario.process_checks]
        answer_results = [run_check(c, run_dir, is_answer=True) for c in scenario.answer_checks]

    rr = classify_run(outcome, completion_present=present, completion_fresh=fresh,
                      process_results=process_results)
    # Answer checks are executed and RECORDED on the per-run record but never gate.
    rr.check_results = list(rr.check_results) + answer_results

    (run_dir / "meta.json").write_text(
        json.dumps(
            {
                "corpus_id": corpus_id,
                "scenario_id": scenario.id,
                "exit_code": outcome.exit_code,
                "status": rr.status,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return rr


def run_scenario(scenario: Scenario, *, temp_root, worktree=None, launch=None,
                 installer=None, max_attempts: int | None = None) -> Verdict:
    """Install the corpus once, then run the completion-seeking M-run loop and
    return the Verdict. The `launch`/`installer` seams default to the module-level
    `launch_agent`/`temp_install` resolved at CALL time (run_crew's pattern), so a
    monkeypatched or CLI-selected seam takes effect.

    Loop is completion-seeking: launch until `completed == m` or
    `attempts == max_attempts` (default m+2). Fenced attempts (inconclusive/
    errored) do not advance the completed count, so environment flake extends the
    loop rather than failing the corpus."""
    launch = launch if launch is not None else launch_agent
    installer = installer if installer is not None else temp_install
    temp_root = Path(temp_root)
    temp_root.mkdir(parents=True, exist_ok=True)

    skills_dir = installer(worktree, temp_root)
    source_commit = _source_commit()
    corpus_id = write_corpus_marker(skills_dir, source_commit)

    m = scenario.m
    n = scenario.n
    if max_attempts is None:
        max_attempts = m + 2

    run_results: list = []
    completed = 0
    attempt = 0
    while completed < m and attempt < max_attempts:
        rr = _run_once(scenario, attempt, temp_root, skills_dir, corpus_id, launch)
        run_results.append(rr)
        if rr.status in ("completed-pass", "completed-fail"):
            completed += 1
        attempt += 1

    return verdict(run_results, n=n, m=m, corpus_id=corpus_id, source_commit=source_commit)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run a corpus skill-eval scenario N-of-M and print the verdict."
    )
    p.add_argument("scenario_dir", help="path to evals/<name>/")
    p.add_argument("--worktree", default=None, help="source worktree to install the corpus from (g3)")
    p.add_argument("--n", type=int, default=None, help="passes required (default from scenario / 2)")
    p.add_argument("--m", type=int, default=None, help="completion target (default from scenario / 3)")
    p.add_argument("--model", default=None, help="override the scenario model")
    p.add_argument("--timeout", type=int, default=None, help="per-run timeout seconds")
    p.add_argument("--command", default=DEFAULT_LAUNCHER, help="agent launcher binary")
    p.add_argument("--dry-run", action="store_true",
                   help="run the whole pipeline with a fake PASSING launcher (no agent)")
    p.add_argument("--dry-run-fail", action="store_true",
                   help="run the whole pipeline with a fake BROKEN launcher (falsification floor)")
    p.add_argument("--keep-temp", action="store_true", help="preserve + print the temp dir")
    p.add_argument("--json", action="store_true", help="emit the verdict as JSON")
    return p


def _apply_overrides(scenario: Scenario, args: argparse.Namespace) -> None:
    if args.n is not None:
        scenario.n = args.n
    if args.m is not None:
        scenario.m = args.m
    if args.model is not None:
        scenario.model = args.model
    if args.timeout is not None:
        scenario.timeout_seconds = args.timeout


def _print_verdict(v: Verdict, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(
            {
                "status": v.status,
                "exit_code": v.exit_code,
                "completed": v.completed_count,
                "passed": v.passed_count,
                "fenced": v.fenced_count,
                "corpus_id": v.corpus_id,
                "source_commit": v.source_commit,
                "n_of_m": "regression-vs-variance smoke, not a statistical guarantee",
            },
            indent=2,
        ))
        return
    print(f"VERDICT: {v.status} (exit {v.exit_code})")
    print(f"  completed={v.completed_count} passed={v.passed_count} fenced={v.fenced_count}")
    print(f"  corpus_id={v.corpus_id}")
    print(f"  source_commit={v.source_commit}")
    print("  N-of-M is a regression-vs-variance smoke, not a statistical guarantee.")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.dry_run and args.dry_run_fail:
        print("error: --dry-run and --dry-run-fail are mutually exclusive", file=sys.stderr)
        return 3

    try:
        scenario = load_scenario(Path(args.scenario_dir))
    except EvalConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    _apply_overrides(scenario, args)

    # Seam selection. Only --dry-run/--dry-run-fail run at g2; the real
    # launch_agent + temp_install are inert stubs until g3.
    if args.dry_run:
        launch, installer = dry_run_launch, _dry_installer
    elif args.dry_run_fail:
        launch, installer = dry_run_fail_launch, _dry_installer
    else:
        launch, installer = launch_agent, temp_install

    if args.keep_temp:
        temp_root = Path(tempfile.mkdtemp(prefix="constellation-eval-"))
        try:
            v = run_scenario(scenario, temp_root=temp_root, worktree=args.worktree,
                             launch=launch, installer=installer)
        finally:
            print(f"kept temp dir: {temp_root}", file=sys.stderr)
    else:
        with tempfile.TemporaryDirectory(prefix="constellation-eval-") as td:
            v = run_scenario(scenario, temp_root=Path(td), worktree=args.worktree,
                             launch=launch, installer=installer)

    _print_verdict(v, as_json=args.json)
    return v.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
