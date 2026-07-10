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

# Model tier — PINNED LOW and EXPLICIT, never silently inherited from the session
# (issue #115 human amendment). A low tier struggles sooner, which is the point: it
# surfaces corpus regressions a frontier model would muscle through, so an eval
# verdict should come from the cheapest model that can plausibly drive the workflow.
# haiku (`claude-haiku-4-5-20251001`) is the preferred, even-cheaper choice wherever
# it can complete the workflow; sonnet is the default because it can drive more of it.
DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_N = 2
DEFAULT_M = 3
DEFAULT_TIMEOUT_SECONDS = 1800
DEFAULT_LAUNCHER = "claude"

# Headless agents (`claude -p`) have no interactive approver, so without an explicit
# permission mode every tool action needing approval is DENIED and the agent can
# write nothing (issue #115 tc2 — the epic's honest-null). acceptEdits is the
# least-powerful documented mode that clears the file-write wall: it auto-accepts
# file edits/writes in the agent's own temp workspace without also auto-approving
# arbitrary shell — operator-overridable via --permission-mode for a workflow that
# provably needs a broader mode.
DEFAULT_PERMISSION_MODE = "acceptEdits"

# The completion stub a finished run leaves in its workspace. A canned test run
# and the dry-run launcher fabricate the same shape the live run will (run-dir
# contract): workspace/<COMPLETION_ARTIFACT> + a spine.json terminal.
COMPLETION_ARTIFACT = "eval-complete.txt"
CORPUS_MARKER = _install.CORPUS_MARKER

# Infra markers sniffed in a run's stderr — any hit FENCES the run (inconclusive),
# so environment flake can only ever yield INCONCLUSIVE, never FAIL a good corpus.
INFRA_MARKERS = ("usage limit", "rate limit", "quota", "overloaded", "429")

# Permission-denial markers (issue #115 tc3). A headless agent that is permission-
# sandboxed prints these as it is refused each tool action. Sniffed in BOTH the
# transcript and stderr; a hit is only load-bearing when ALSO byte-unchanged (see
# classify_run) so a corpus that legitimately did work is never mis-fenced. Phrases
# are drawn from the real g5-live transcript ("Claude requested permissions to
# write", "requires manual approval", "Output redirection ... was blocked").
PERMISSION_MARKERS = (
    "requested permissions",
    "requires manual approval",
    "requires approval",
    "requires permission",
    "permission denied",
    "permission denial",
    "not permitted",
)


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
def build_eval_argv(launcher: str, *, prompt: str, model: str | None,
                    permission_mode: str | None = None) -> list[str]:
    """PURE construction of the headless agent command line. Exactly
    `[launcher, "-p", prompt]`, plus `--model <model>` when a model is set and
    `--permission-mode <mode>` when a mode is set. Kept separate so tests assert on
    the argv without spawning anything. The permission mode is what lets a headless
    agent write files in its own workspace (issue #115 tc2)."""
    argv = [launcher, "-p", prompt]
    if model:
        argv += ["--model", model]
    if permission_mode:
        argv += ["--permission-mode", permission_mode]
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


def is_permission_denial(text) -> bool:
    """Whether `text` carries a permission-sandbox refusal marker (issue #115 tc3).
    PURE. A hit is only load-bearing when the workspace was ALSO left byte-unchanged
    (see classify_run), so it can never mis-fence a run that legitimately did work."""
    low = (text or "").lower()
    return any(marker in low for marker in PERMISSION_MARKERS)


def classify_run(outcome: LaunchOutcome, *, completion_present: bool,
                 completion_fresh: bool, process_results: list,
                 workspace_unchanged: bool = False,
                 permission_denied: bool = False) -> RunResult:
    """Resolve one launch attempt to exactly one class (contract §(i) infra-fence
    table). PURE.

      inconclusive (fenced): timeout, or a usage/rate-limit/overloaded/429 marker
                             sniffed in stderr;
      errored (fenced):      launch failure, corpus mismatch, a permission-sandbox
                             block (exited but left the workspace byte-unchanged AND
                             a permission-denial marker), or a non-zero exit with NO
                             marker AND no completion;
      completed-pass:        completed and every process check passed;
      completed-fail:        completed (incl. exit 0 with no spine terminal) but a
                             process check failed.

    A run "completed" when its completion artifact is present+fresh OR the agent
    exited 0 — so an exit-0 run with no spine terminal is still tallied (as a
    fail if a process check failed), never silently fenced. The permission-block
    fence (issue #115 tc3) is the ONE deliberate carve-out of that rule: an agent
    that exits 0 but was permission-denied every write leaves the workspace
    byte-unchanged, which is the ENVIRONMENT blocking a good corpus, not the corpus
    failing — so it is FENCED, not tallied. It is gated on BOTH signals (unchanged
    workspace AND a denial marker) so an exit-0 run that genuinely produced the
    wrong output — which mutates the workspace — still lands completed-fail per the
    g2-ratified exit-0-no-terminal rule."""
    if outcome.timed_out:
        return RunResult(status="inconclusive", reason="timeout", check_results=list(process_results))
    if is_infra_marker(outcome.stderr_text):
        return RunResult(status="inconclusive", reason="infra-marker", check_results=list(process_results))
    if outcome.launch_error:
        return RunResult(status="errored", reason="launch-error", check_results=list(process_results))
    if outcome.corpus_mismatch:
        return RunResult(status="errored", reason="corpus-mismatch", check_results=list(process_results))
    if workspace_unchanged and permission_denied:
        return RunResult(status="errored", reason="permission-blocked",
                         check_results=list(process_results))

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
# corpus provenance — sha256 id, marker, assert (owned by install_constellation)
# --------------------------------------------------------------------------- #
# These primitives now live in install_constellation (the installer stamps the
# same CORPUS.json into every real install, #122). The eval harness reuses them
# unchanged so an eval fingerprints a corpus exactly as a live install does.
compute_corpus_id = _install.compute_corpus_id
write_corpus_marker = _install.write_corpus_marker
assert_corpus = _install.assert_corpus


# --------------------------------------------------------------------------- #
# the ONE real seam (inert until g3) + fake launchers for --dry-run
# --------------------------------------------------------------------------- #
# Bytes of stderr tail kept for infra-marker sniffing — enough to catch a
# usage/rate-limit banner without slurping a giant transcript into memory.
_STDERR_TAIL_BYTES = 8192


def _read_text_tail(text_path) -> str:
    """Best-effort tail of a run's stderr OR transcript file, for `is_infra_marker`
    and `is_permission_denial` sniffing. Never raises: a missing/unreadable file
    yields an empty string (which fences nothing), so a read hiccup cannot mis-fence
    a run."""
    try:
        path = Path(text_path)
        if not path.is_file():
            return ""
        data = path.read_bytes()
    except OSError:
        return ""
    return data[-_STDERR_TAIL_BYTES:].decode("utf-8", errors="replace")


def launch_agent(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome:
    """The ONE real seam — spawn `claude -p ...` (argv built by build_eval_argv)
    with `cwd=<run>/workspace`, capturing stdout/stderr to the given paths and
    honoring `timeout`. Implemented on `subprocess.run` (mirroring
    run_crew.launch_process) so the tests' autouse agent-free guard — which wraps
    `subprocess.run` — still intercepts every launch.

    Populates LaunchOutcome fully so the pure classify_run infra-fence fires:
      - normal return -> exit_code + stderr tail (for usage/rate-limit sniffing);
      - subprocess.TimeoutExpired -> timed_out=True (fenced inconclusive);
      - spawn failure (FileNotFoundError / OSError, e.g. no `claude` on PATH)
        -> launch_error=True (fenced errored).
    Corpus-mismatch is asserted upstream in _run_once, never here."""
    stdout_path = Path(stdout_path)
    stderr_path = Path(stderr_path)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
            proc = subprocess.run(
                argv,
                cwd=str(cwd),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=err,
                timeout=timeout,
            )
    except subprocess.TimeoutExpired:
        # The child is killed; whatever it wrote to the stderr file is still there.
        return LaunchOutcome(exit_code=None, timed_out=True,
                             stderr_text=_read_text_tail(stderr_path))
    except (FileNotFoundError, OSError) as exc:
        # Launcher not found / could not spawn — a launch failure, not a corpus
        # verdict. Fenced as errored.
        return LaunchOutcome(exit_code=None, launch_error=True, stderr_text=str(exc))
    return LaunchOutcome(exit_code=proc.returncode,
                         stderr_text=_read_text_tail(stderr_path))


def temp_install(worktree, temp_root) -> Path:
    """Install the candidate corpus ONCE into `<temp_root>/skills` and return that
    dir. Reuses install_constellation.discover_skills + install_skills (token
    rewrite + bundle copy), never reinventing install. `worktree` selects the
    source skill root: `<worktree>/skills` when given, else this worktree's
    `skills/` (install_constellation.SOURCE_ROOT). Full-set, non-dry, non-force
    into a fresh temp target; never edits install_constellation or the source
    skills."""
    source_root = (Path(worktree) / "skills") if worktree is not None else _install.SOURCE_ROOT
    skills = _install.discover_skills(source_root=source_root)
    target_root = Path(temp_root) / "skills"
    _install.install_skills(
        skills,
        target_root,
        dry_run=False,
        force=False,
        full_set=True,
        restart_message="",
        out=lambda _msg: None,
    )
    return target_root


def _write_transcript(stdout_path, stderr_path, note: str) -> None:
    if stdout_path:
        Path(stdout_path).parent.mkdir(parents=True, exist_ok=True)
        Path(stdout_path).write_text(note + "\n", encoding="utf-8")
    if stderr_path:
        Path(stderr_path).parent.mkdir(parents=True, exist_ok=True)
        Path(stderr_path).write_text("", encoding="utf-8")


def dry_run_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome:
    """Fake launcher that synthesizes a REAL passing workspace — a non-empty
    `solution.py`, a green `test_solution.py`, the completion artifact, and a
    terminal `spine.json` — so the gating process checks (`artifact_present`,
    `tests_green`, `spine_completed`) each bite STRICTLY on a real deliverable, with
    no sentinel stand-in (issue #115 tc1). Spawns NOTHING — the CI smoke for the
    runner itself and caller #2's live target. The test is self-contained (imports
    nothing from the workspace) so it stays green under any pytest import mode."""
    workspace = Path(cwd)
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "solution.py").write_text(
        "def solve():\n"
        "    return 42\n"
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    print(solve())\n",
        encoding="utf-8",
    )
    (workspace / "test_solution.py").write_text(
        "def test_dry_run_solution():\n"
        "    assert 42 == 42\n",
        encoding="utf-8",
    )
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
    (the real installer) — it deliberately avoids installing the full corpus so a
    dry run stays instant and agent-free."""
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
              corpus_id: str, launch, permission_mode: str | None = None) -> RunResult:
    """Execute (and score) ONE attempt into `run-<index>/`. Fabricates the run-dir
    shape, copies the corpus into an isolated `workspace/.claude/skills` and
    asserts its id, launches via the injected seam, probes completion, then runs
    the process (gating) and answer (advisory, recorded-not-gating) checks.

    Also computes the two signals the permission-block fence (issue #115 tc3)
    consumes: a content fingerprint of the seeded workspace taken BEFORE the launch
    vs. AFTER (byte-unchanged?), and whether a permission-denial marker appears in
    the transcript or stderr. Both true ⇒ the environment blocked the agent, fenced
    rather than tallied."""
    run_dir = temp_root / f"run-{index}"
    workspace = run_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    if scenario.fixture_dir is not None:
        shutil.copytree(scenario.fixture_dir, workspace, dirs_exist_ok=True)

    run_skills = workspace / ".claude" / "skills"
    shutil.copytree(skills_dir, run_skills)

    started = time.time()
    workspace_unchanged = False
    permission_denied = False
    if not assert_corpus(run_skills, corpus_id):
        outcome = LaunchOutcome(exit_code=None, corpus_mismatch=True)
        present = fresh = False
        process_results: list = []
        answer_results: list = []
    else:
        # Fingerprint the seeded workspace (corpus + fixture) BEFORE the launch, so a
        # run that writes nothing can be recognised as byte-unchanged afterwards.
        pre_fingerprint = compute_corpus_id(workspace)
        prompt = wrap_prompt(scenario.task_prompt)
        argv = build_eval_argv(DEFAULT_LAUNCHER, prompt=prompt, model=scenario.model,
                               permission_mode=permission_mode)
        outcome = launch(
            argv,
            cwd=str(workspace),
            env=dict(os.environ),
            stdout_path=str(run_dir / "transcript.txt"),
            stderr_path=str(run_dir / "stderr.txt"),
            timeout=scenario.timeout_seconds,
        )
        workspace_unchanged = compute_corpus_id(workspace) == pre_fingerprint
        transcript_text = _read_text_tail(run_dir / "transcript.txt")
        permission_denied = (is_permission_denial(outcome.stderr_text)
                             or is_permission_denial(transcript_text))
        present, fresh = _probe_completion(run_dir, started)
        process_results = [run_check(c, run_dir) for c in scenario.process_checks]
        answer_results = [run_check(c, run_dir, is_answer=True) for c in scenario.answer_checks]

    rr = classify_run(outcome, completion_present=present, completion_fresh=fresh,
                      process_results=process_results,
                      workspace_unchanged=workspace_unchanged,
                      permission_denied=permission_denied)
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
                 installer=None, max_attempts: int | None = None,
                 permission_mode: str | None = DEFAULT_PERMISSION_MODE) -> Verdict:
    """Install the corpus once, then run the completion-seeking M-run loop and
    return the Verdict. The `launch`/`installer` seams default to the module-level
    `launch_agent`/`temp_install` resolved at CALL time (run_crew's pattern), so a
    monkeypatched or CLI-selected seam takes effect. `permission_mode` is passed to
    the launcher so a live headless agent can write files (issue #115 tc2); it
    defaults to the pinned, operator-visible DEFAULT_PERMISSION_MODE.

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
        rr = _run_once(scenario, attempt, temp_root, skills_dir, corpus_id, launch,
                       permission_mode=permission_mode)
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
    p.add_argument("--model", default=None,
                   help=f"override the scenario model (pinned default: {DEFAULT_MODEL})")
    p.add_argument("--timeout", type=int, default=None, help="per-run timeout seconds")
    p.add_argument("--command", default=DEFAULT_LAUNCHER, help="agent launcher binary")
    p.add_argument("--permission-mode", default=DEFAULT_PERMISSION_MODE,
                   help=f"headless agent permission mode passed to `claude -p` "
                        f"(default: {DEFAULT_PERMISSION_MODE}; a live run needs one "
                        f"or the agent is denied all file writes)")
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
                             launch=launch, installer=installer,
                             permission_mode=args.permission_mode)
        finally:
            print(f"kept temp dir: {temp_root}", file=sys.stderr)
    else:
        with tempfile.TemporaryDirectory(prefix="constellation-eval-") as td:
            v = run_scenario(scenario, temp_root=Path(td), worktree=args.worktree,
                             launch=launch, installer=installer,
                             permission_mode=args.permission_mode)

    _print_verdict(v, as_json=args.json)
    return v.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
