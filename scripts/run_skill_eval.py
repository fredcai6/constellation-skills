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

Arm construction (load-bearing, #153): an installed skill is TWO trees welded
together. The skill SOURCE tree is `<worktree>/skills` — `--worktree` only selects
that source. The bundled engine (the `scripts/` + `references/` copied into each
installed skill) does NOT come from `--worktree`; it comes from `REPO_ROOT/scripts`
of the checkout that INVOKES `run_skill_eval.py` (the invoking checkout). So the
corpus a run fingerprints is source-tree bytes plus invoking-checkout engine bytes;
hashing the source tree alone would omit the bundled engine, which is why the
corpus id is taken over the INSTALLED tree (and normalized for install path — below).
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
import threading
import time
from dataclasses import dataclass, field
from datetime import date
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
# An honest engine-driven run at the pinned low tier takes 13.5–30+ min of real
# wall-clock (issue #126, attempts 9/10 measured both honest passes fenced by the
# old 900s/1800s deadlines). The default and the per-scenario floor are set so a
# scenario cannot silently starve an honest run below the observed ceiling; a
# diagnostic --timeout CLI override still applies freely after the floor.
DEFAULT_TIMEOUT_SECONDS = 2400
SCENARIO_TIMEOUT_FLOOR_SECONDS = 2400
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
COMPLETION_ARTIFACT = "work-complete.txt"
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
        # Clamp the scenario-configured timeout UP to the floor so a scenario.toml
        # can never starve an honest run below the observed ceiling; a diagnostic
        # --timeout CLI override (applied later in _apply_overrides) is free to go
        # lower.
        timeout_seconds=max(
            SCENARIO_TIMEOUT_FLOOR_SECONDS,
            int(overrides.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)),
        ),
    )


# --------------------------------------------------------------------------- #
# build_eval_argv — PURE; mirrors run_crew.build_crew_argv
# --------------------------------------------------------------------------- #
# Execution rights every eval workspace needs: the checklist engine, pytest, and
# the agent's own solution are all `python`-family invocations. Passed as
# --allowedTools because a workspace-local settings.json allowlist is IGNORED in
# an untrusted (never interactively opened) directory — the trust dialog cannot
# be answered headlessly (issue #126 diagnosis). CLI-scoped, host state untouched.
EXEC_ALLOWED_TOOLS = ("Bash(python:*)", "Bash(python3:*)", "Bash(py:*)", "Bash(pytest:*)")


def build_eval_argv(launcher: str, *, prompt: str, model: str | None,
                    permission_mode: str | None = None) -> list[str]:
    """PURE construction of the headless agent command line. Exactly
    `[launcher, "-p", prompt]`, plus `--model <model>` when a model is set,
    `--permission-mode <mode>` when a mode is set, and the EXEC_ALLOWED_TOOLS
    allowlist. Kept separate so tests assert on the argv without spawning
    anything. The permission mode covers file writes (issue #115 tc2); the
    allowed-tools list covers non-interactive python/pytest execution (#126)."""
    argv = [launcher, "-p", prompt]
    if model:
        argv += ["--model", model]
    if permission_mode:
        argv += ["--permission-mode", permission_mode]
    argv += ["--allowedTools", *EXEC_ALLOWED_TOOLS]
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

      completed-pass (timeout carve-out): a timed-out run whose workspace ALREADY
                             passes every process check — the checks are monotone,
                             so a finished deliverable is a PASS even though the
                             process was killed before its own exit (issue #126);
      inconclusive (fenced): a timeout with any failing/absent process check, or a
                             usage/rate-limit/overloaded/429 marker sniffed in stderr;
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
        # A timeout is normally fenced (inconclusive) — the process outlived its
        # deadline, inconclusive about the corpus. But if the workspace ALREADY
        # passes every process check, the run is a PASS, not a fence: the process
        # checks are MONOTONE (a spine already terminal, a solution already written,
        # tests already green cannot be un-passed by more wall-clock), so all the
        # timeout cost was the agent's own process exit, not the deliverable. This
        # is exactly the honest run that finished the work but not the exit and got
        # fenced by the old 900s/1800s deadlines (issue #126, attempts 9/10). A
        # timeout with any failing/absent check stays fenced (infra, never a FAIL).
        if process_results and all(c.passed for c in process_results):
            return RunResult(status="completed-pass", reason="timeout-checks-green",
                             check_results=list(process_results))
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
# install-path-invariant corpus id (#153)
# --------------------------------------------------------------------------- #
# `install_constellation.rewrite_installed_skill_paths` bakes the ABSOLUTE install
# path (`target.as_posix()`, where target = <skills_dir>/<skill>) into every
# installed skill file — it replaces the `<skill-dir>` / `<name>-skill-dir>` tokens.
# Raw `compute_corpus_id` then hashes those bytes, so the id depends on WHERE the
# corpus was installed. The eval harness installs into a fresh `tempfile.mkdtemp`
# per invocation, so a byte-identical corpus gets a different id every run — that is
# #153, and it breaks same-corpus-hash grouping for rolling certification.
#
# The fix hashes a path-NORMALIZED copy of each file's text: the original install
# root's posix string is replaced with a fixed sentinel before hashing, so two
# byte-identical corpora at different install paths hash identically. Only the EVAL
# harness's hashing changes; real-install path rewriting/hashing is untouched.
#
# ANCHOR RULE (load-bearing — getting it wrong false-fences every run): the baked
# pollution is ALWAYS the ORIGINAL install root's posix string, and it survives
# verbatim when the installed tree is COPIED elsewhere (`_run_once` copies
# `skills_dir` -> `workspace/.claude/skills` and then asserts the copy). So the
# install root to strip is passed as an EXPLICIT anchor, SEPARATE from the tree being
# hashed — at the assert site the tree is the copy but the anchor is the ORIGINAL
# `skills_dir`. Stripping "the directory I am hashing" would no-op on the copy (whose
# own path is not what its bytes contain) and false-fence every run as corpus_mismatch.
CORPUS_ROOT_SENTINEL = "<CORPUS_ROOT>"


def _hash_normalized_file(path: Path, needle: str) -> str:
    """sha256 hexdigest of a file's TEXT with `needle` (the install root's posix
    string) replaced by a fixed sentinel, so the baked absolute install path does not
    perturb the digest. Undecodable/binary files (which carry no baked text path) fall
    back to the raw-bytes `_hash_file`, keeping them stable and format-identical."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return _hash_file(path)
    normalized = text.replace(needle, CORPUS_ROOT_SENTINEL)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def stable_corpus_id(skills_dir, install_root, names=None) -> str:
    """Install-path-invariant corpus id. Mirrors `_install.compute_corpus_id`'s file
    selection (sorted `rglob`, skip `CORPUS_MARKER` / `.pyc` / `__pycache__`) and its
    `"sha256:" + sha256` over sorted `(rel_posix, file_hash)` pairs EXACTLY — only the
    per-file bytes are normalized, so the id FORMAT is unchanged.

    `skills_dir` is the tree to hash; `install_root` is the ORIGINAL install root whose
    posix string was baked into the files (the ANCHOR). The two DIFFER at the assert
    site, where the tree is a COPY of an `install_root`-rooted corpus — see the ANCHOR
    RULE above. The needle is built from `install_root.as_posix()` (forward slashes,
    matching how the installer baked it via `target.as_posix()`); `str(install_root)`
    would use backslashes on Windows and silently no-op.
    """
    skills_dir = Path(skills_dir)
    needle = Path(install_root).as_posix()
    roots = (
        [skills_dir / n for n in names]
        if names is not None
        else [skills_dir]
    )
    pairs: list[tuple[str, str]] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.name == CORPUS_MARKER:
                continue
            if path.suffix == ".pyc" or "__pycache__" in path.parts:
                continue
            rel = path.relative_to(skills_dir).as_posix()
            pairs.append((rel, _hash_normalized_file(path, needle)))
    digest = hashlib.sha256()
    for rel, file_hash in sorted(pairs):
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("utf-8"))
        digest.update(b"\n")
    return "sha256:" + digest.hexdigest()


def write_stable_corpus_marker(skills_dir, source_commit, *, build_date=None) -> str:
    """Compute the STABLE (install-path-invariant) corpus id for `skills_dir` and write
    `<skills_dir>/CORPUS.json` with it. Mirrors `_install.write_corpus_marker`'s marker
    shape (`{corpus_id, source_commit, date}`) — it differs ONLY in recording the stable
    id instead of the raw path-dependent one, so the id the resume path reads back equals
    the id the assert site checks the per-run copy against. `write_corpus_marker` itself
    recomputes via raw `compute_corpus_id`, so it cannot be reused for the eval id here."""
    skills_dir = Path(skills_dir)
    corpus_id = stable_corpus_id(skills_dir, skills_dir)
    marker = {
        "corpus_id": corpus_id,
        "source_commit": source_commit,
        "date": build_date if build_date is not None else date.today().isoformat(),
    }
    (skills_dir / CORPUS_MARKER).write_text(
        json.dumps(marker, indent=2) + "\n", encoding="utf-8"
    )
    return corpus_id


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


# Deadline machinery. `subprocess.run(timeout=...)` is NOT enough on Windows: it
# waits by joining reader threads that block until the stdout/stderr pipes hit EOF,
# and a grandchild (e.g. a nested `claude -p`) that inherited the pipe write-handle
# keeps EOF from ever arriving — so the runner hangs for hours AFTER the child
# already exited (epic-101 live-acceptance, 2026-07-10). We therefore own the wait:
# poll for exit against a monotonic deadline, HARD-kill the whole process tree on
# expiry (taskkill /T /F), and drain the pipes on daemon threads we join only for a
# bounded grace so a lingering grandchild handle can never block the wait.
_POLL_INTERVAL_SECONDS = 0.1
_DRAIN_GRACE_SECONDS = 5.0
_PIPE_CHUNK_BYTES = 65536
# How often the live launcher stamps a liveness heartbeat into the run's launch
# meta.json while a subject is in flight. A watcher (the Phase-3 poller, or a
# resuming re-invocation) reads it to tell a live runner from a dead one WITHOUT
# waiting the full per-run deadline — the gap that let a dead runner idle a
# watching session for hours on an EXITCODE that never came (issue #130).
_HEARTBEAT_INTERVAL_SECONDS = 30.0


def _tree_kill(proc: "subprocess.Popen") -> None:
    """Hard-kill an entire process tree, best-effort, never raising — a kill failure
    must not mask the timeout it is servicing. On Windows uses
    `taskkill /PID <pid> /T /F` (the /T flag is what reaches grandchildren the plain
    Popen.kill() TerminateProcess would leave orphaned); elsewhere falls back to
    Popen.kill()."""
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):
            pass
    else:  # pragma: no cover - repo is Windows; kept so the module is portable.
        try:
            proc.kill()
        except OSError:
            pass


def _drain_pipe(pipe, file_obj) -> None:
    """Copy a child pipe to its capture file until EOF. Swallows OSError/ValueError
    so an abandoned daemon drainer (grandchild still holding the write-handle, file
    already closed) dies quietly instead of surfacing a spurious error."""
    try:
        for chunk in iter(lambda: pipe.read(_PIPE_CHUNK_BYTES), b""):
            file_obj.write(chunk)
            file_obj.flush()
    except (OSError, ValueError):
        pass


def _stamp_meta_field(run_dir, **fields) -> None:
    """Best-effort merge of `fields` into a run's launch meta.json (only while it is
    still `launched`). Used to record the subject PID at spawn so an external reaper
    can tree-kill an orphaned subject after a runner death. Never raises."""
    try:
        meta_path = Path(run_dir) / "meta.json"
        if not meta_path.is_file():
            return
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("status") != "launched":
            return
        meta.update(fields)
        meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError):
        pass


def _stamp_meta_heartbeat(run_dir) -> None:
    """Best-effort liveness stamp into a run's launch meta.json while its subject
    is in flight. Records `heartbeat_at` (wall-clock now) and `elapsed_seconds`
    (now minus the recorded `launched_at`) so an independent watcher — or a
    resuming re-invocation — can distinguish a live runner from a dead one without
    waiting the full deadline (issue #130). Never raises: a missing/unreadable/
    non-`launched` meta is silently skipped, so a stat hiccup cannot perturb a run.
    Only a still-`launched` meta is stamped, so a heartbeat can never overwrite a
    meta the finalizer already resolved to a terminal status."""
    try:
        meta_path = Path(run_dir) / "meta.json"
        if not meta_path.is_file():
            return
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("status") != "launched":
            return
        now = time.time()
        meta["heartbeat_at"] = now
        launched_at = meta.get("launched_at")
        if isinstance(launched_at, (int, float)):
            meta["elapsed_seconds"] = round(now - launched_at, 1)
        meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError):
        pass


def launch_agent(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome:
    """The ONE real seam — spawn `claude -p ...` (argv built by build_eval_argv)
    with `cwd=<run>/workspace`, capturing stdout/stderr to the given paths and
    ENFORCING `timeout` with a hard process-tree kill. Uses `subprocess.Popen` (which
    the tests' autouse agent-free guard also wraps) so no `claude` is ever spawned
    under test.

    Populates LaunchOutcome fully so the pure classify_run infra-fence fires:
      - normal exit  -> exit_code + stderr tail (for usage/rate-limit sniffing);
      - deadline hit -> tree-killed, timed_out=True (fenced inconclusive);
      - spawn failure (FileNotFoundError / OSError, e.g. no `claude` on PATH)
        -> launch_error=True (fenced errored).
    Corpus-mismatch is asserted upstream in _run_once, never here.

    The wait can never hang on a lingering grandchild pipe handle: we poll for exit
    against a monotonic deadline, tree-kill on expiry, and join the daemon drain
    threads only for `_DRAIN_GRACE_SECONDS` before abandoning them."""
    stdout_path = Path(stdout_path)
    stderr_path = Path(stderr_path)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        out = stdout_path.open("wb")
        err = stderr_path.open("wb")
    except OSError as exc:
        return LaunchOutcome(exit_code=None, launch_error=True, stderr_text=str(exc))

    try:
        try:
            proc = subprocess.Popen(
                argv,
                cwd=str(cwd),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (FileNotFoundError, OSError) as exc:
            # Launcher not found / could not spawn — a launch failure, not a corpus
            # verdict. Fenced as errored.
            return LaunchOutcome(exit_code=None, launch_error=True, stderr_text=str(exc))

        run_dir = Path(stdout_path).parent
        # Record the subject PID into the launch meta the moment it spawns, so an
        # external reaper (a resuming re-invocation) can tree-kill an orphaned
        # subject after a runner death, and a post-hoc inspector can see it (#130).
        _stamp_meta_field(run_dir, subject_pid=proc.pid)

        drainers = [
            threading.Thread(target=_drain_pipe, args=(proc.stdout, out), daemon=True),
            threading.Thread(target=_drain_pipe, args=(proc.stderr, err), daemon=True),
        ]
        for t in drainers:
            t.start()

        deadline = None if timeout is None else time.monotonic() + timeout
        next_heartbeat = time.monotonic() + _HEARTBEAT_INTERVAL_SECONDS
        timed_out = False
        while proc.poll() is None:
            if deadline is not None and time.monotonic() >= deadline:
                timed_out = True
                _tree_kill(proc)
                # Give the tree a moment to fall over, then stop waiting regardless —
                # never an unbounded wait.
                try:
                    proc.wait(timeout=_DRAIN_GRACE_SECONDS)
                except subprocess.TimeoutExpired:
                    pass
                break
            if time.monotonic() >= next_heartbeat:
                _stamp_meta_heartbeat(run_dir)
                next_heartbeat = time.monotonic() + _HEARTBEAT_INTERVAL_SECONDS
            time.sleep(_POLL_INTERVAL_SECONDS)

        # Join drainers for a bounded grace only. A grandchild still holding the pipe
        # write-handle keeps read() from hitting EOF, so an unbounded join is the very
        # hang we are fixing — abandon the daemon threads after the grace.
        for t in drainers:
            t.join(_DRAIN_GRACE_SECONDS)
    finally:
        out.close()
        err.close()

    if timed_out:
        return LaunchOutcome(exit_code=None, timed_out=True,
                             stderr_text=_read_text_tail(stderr_path))
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


def _dry_run_engine_spine() -> dict:
    """A minimal ENGINE-SHAPED terminal spine for the dry-run smoke: the gated
    `tasks` form with every task complete, a plausible `engine_session` lease
    (monotonic claim -> heartbeat -> release), and one engine-produced
    `command-output` evidence item backing its command postcondition. Since #127
    hardened `spine_completed` to demand engine provenance (a bare
    `{"status": "done"}` no longer passes), the runner's own falsification-floor
    smoke must synthesize the same engine fingerprints a real driven spine leaves —
    otherwise the dry-run would fail the very check it exists to exercise."""
    from datetime import datetime, timedelta, timezone

    t0 = datetime.now(timezone.utc)
    iso = lambda dt: dt.isoformat()
    return {
        "work_id": "dry-run",
        "type": "gated",
        "items": ["init"],
        "tasks": {
            "init": {
                "id": "init",
                "title": "dry-run",
                "imperative": "dry-run synthesized gate",
                "preconditions": [],
                "postconditions": [{
                    "id": "c1",
                    "statement": "dry-run engine command check",
                    "check": {"kind": "command", "command": "true"},
                    "satisfied": True,
                    "satisfied_by": "e-init-1",
                }],
                "constraints": [],
                "directives": None,
                "child_checklist": None,
                "status": "complete",
                "status_detail": {},
                "result": None,
                "finding": None,
                "evidence": [{
                    "id": "e-init-1",
                    "type": "command-output",
                    "payload": {"cmd": "true", "exit": 0, "shell": "posix"},
                    "produced_by": "engine",
                    "ts": "",
                }],
                "rework_count": 0,
            }
        },
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
        "engine_session": {
            "session_id": "dry-run-smoke",
            "status": "released",
            "claimed_at": iso(t0),
            "last_heartbeat": iso(t0 + timedelta(seconds=1)),
            "claimed_by": "commander",
            "worktree": ".",
            "previous_session_id": None,
            "takeover_reason": None,
            "released_at": iso(t0 + timedelta(seconds=2)),
        },
    }


def dry_run_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome:
    """Fake launcher that synthesizes a REAL passing workspace — a non-empty
    `solution.py`, a green `test_solution.py`, the completion artifact, and an
    engine-shaped terminal `spine.json` — so the gating process checks
    (`artifact_present`, `tests_green`, `spine_completed`) each bite STRICTLY on a
    real deliverable, with no sentinel stand-in (issue #115 tc1) and with the engine
    provenance `spine_completed` now demands (issue #127). Spawns NOTHING — the CI
    smoke for the runner itself and caller #2's live target. The test is
    self-contained (imports nothing from the workspace) so it stays green under any
    pytest import mode."""
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
        json.dumps(_dry_run_engine_spine(), indent=2) + "\n", encoding="utf-8"
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


def _write_meta(run_dir: Path, payload: dict) -> None:
    """Write `<run-dir>/meta.json`. Called twice per run (a launch record at spawn,
    the final classification at end) so a run that is tree-killed mid-flight still
    leaves a diagnosable meta.json instead of nothing."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "meta.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _run_once(scenario: Scenario, index: int, temp_root: Path, skills_dir: Path,
              corpus_id: str, launch, permission_mode: str | None = None,
              launcher: str = DEFAULT_LAUNCHER) -> RunResult:
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
    shutil.copytree(skills_dir, run_skills,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


    started = time.time()
    workspace_unchanged = False
    permission_denied = False
    # Install-path-invariant check (#153): hash the COPY (`run_skills`) but normalize
    # using the ORIGINAL `skills_dir` as the anchor — the copy's bytes still carry the
    # original install path, so anchoring on the copy's own path would false-fence.
    if stable_corpus_id(run_skills, skills_dir) != corpus_id:
        outcome = LaunchOutcome(exit_code=None, corpus_mismatch=True)
        present = fresh = False
        process_results: list = []
        answer_results: list = []
    else:
        # Fingerprint the seeded workspace (corpus + fixture) BEFORE the launch, so a
        # run that writes nothing can be recognised as byte-unchanged afterwards.
        pre_fingerprint = compute_corpus_id(workspace)
        prompt = wrap_prompt(scenario.task_prompt)
        argv = build_eval_argv(launcher, prompt=prompt, model=scenario.model,
                               permission_mode=permission_mode)
        # Incremental meta.json: a launch record written BEFORE the (possibly
        # hang-then-tree-killed) launch, so a killed run is still diagnosable.
        _write_meta(run_dir, {
            "corpus_id": corpus_id,
            "scenario_id": scenario.id,
            "status": "launched",
            "exit_code": None,
            "launched_at": started,
            "timeout_seconds": scenario.timeout_seconds,
        })
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

    # Final meta.json: MERGE the resolved classification ONTO the launch record so
    # the liveness history the launcher stamped (heartbeat_at, elapsed_seconds,
    # subject_pid, timeout_seconds) survives into the finalized record. Overwriting
    # with a fresh dict silently dropped that history, which made a finalized run
    # look like it never had a heartbeat (issue #130 round-1 diagnosis confusion).
    try:
        final_meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        final_meta = {"corpus_id": corpus_id, "scenario_id": scenario.id,
                      "launched_at": started}
    final_meta.update({
        "status": rr.status,
        "reason": rr.reason,
        "exit_code": outcome.exit_code,
        "finished_at": time.time(),
    })
    _write_meta(run_dir, final_meta)
    return rr


def _adjudicate_orphan(scenario: Scenario, run_dir: Path) -> RunResult:
    """Adjudicate a run whose launch meta is still `launched` — a run the runner
    process died mid-flight without finalizing (issue #130). This is the
    independent wall-clock watchdog: it runs OUTSIDE the dead process (a resuming
    re-invocation), so a runner death can no longer strand a run in `launched`
    forever.

    The verdict is re-derived from the workspace exactly like the timeout
    carve-out: the process checks are MONOTONE, so if the orphan's workspace
    ALREADY passes every process check the deliverable is real and the run is a
    `completed-pass` (the runner died AFTER the work finished but before it could
    finalize). Otherwise the run is FENCED (`inconclusive`) — a runner death is an
    environment failure, never a corpus FAIL — and the completion-seeking loop will
    launch a replacement. Rewrites the run's meta.json to the resolved terminal
    status so the record is adjudicable and never re-adopted as an orphan."""
    process_results = [run_check(c, run_dir) for c in scenario.process_checks]
    if process_results and all(c.passed for c in process_results):
        rr = RunResult(status="completed-pass", reason="orphan-checks-green",
                       check_results=process_results)
    else:
        rr = RunResult(status="inconclusive", reason="orphaned-runner-died",
                       check_results=process_results)
    # Merge the terminal verdict ONTO the preserved launch record so corpus_id /
    # launched_at / timeout survive the adjudication and the record stays diagnosable.
    try:
        meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        meta = {"scenario_id": scenario.id}
    meta.update({
        "status": rr.status,
        "reason": rr.reason,
        "adjudicated_orphan": True,
        "finished_at": time.time(),
    })
    _write_meta(run_dir, meta)
    return rr


def _adopt_existing_runs(scenario: Scenario, temp_root: Path) -> tuple[list, int, int]:
    """Re-adopt the run-<n>/ dirs an earlier (possibly killed) invocation left in
    `temp_root`, so a re-run RESUMES instead of restarting (issue #130). Walks
    run-0, run-1, … in order until the first index with no meta.json (the next
    free slot). For each existing meta: a terminal status is reconstructed as-is
    and counted; a still-`launched` orphan is adjudicated by the watchdog above.
    Returns (run_results, completed_count, next_index)."""
    run_results: list = []
    completed = 0
    idx = 0
    while True:
        run_dir = temp_root / f"run-{idx}"
        meta_path = run_dir / "meta.json"
        if not meta_path.is_file():
            break  # first slot with no launch record: resume launches from here
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            break
        if meta.get("status") == "launched":
            rr = _adjudicate_orphan(scenario, run_dir)
        else:
            rr = RunResult(status=meta.get("status"), reason=meta.get("reason"),
                           check_results=[])
        run_results.append(rr)
        if rr.status in ("completed-pass", "completed-fail"):
            completed += 1
        idx += 1
    return run_results, completed, idx


def _read_corpus_marker(skills_dir: Path) -> tuple[str, str | None]:
    """Read (corpus_id, source_commit) from an already-installed corpus's
    CORPUS.json, for the resume path (the skills tree is not reinstalled). Falls
    back to recomputing the id (the marker is excluded from the hash, so the
    recomputed id matches the recorded one) when the marker is missing/unreadable."""
    marker = Path(skills_dir) / CORPUS_MARKER
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        return data["corpus_id"], data.get("source_commit")
    except (OSError, ValueError, KeyError):
        # Fallback recompute uses the STABLE id (#153) with skills_dir as its own anchor,
        # so a recomputed id matches the stable id written into CORPUS.json at install.
        return stable_corpus_id(skills_dir, skills_dir), _source_commit()


def run_scenario(scenario: Scenario, *, temp_root, worktree=None, launch=None,
                 installer=None, max_attempts: int | None = None,
                 permission_mode: str | None = DEFAULT_PERMISSION_MODE,
                 resume: bool = False, launcher: str = DEFAULT_LAUNCHER,
                 max_new_runs: int | None = None) -> Verdict:
    """Install the corpus once, then run the completion-seeking M-run loop and
    return the Verdict. The `launch`/`installer` seams default to the module-level
    `launch_agent`/`temp_install` resolved at CALL time (run_crew's pattern), so a
    monkeypatched or CLI-selected seam takes effect. `permission_mode` is passed to
    the launcher so a live headless agent can write files (issue #115 tc2); it
    defaults to the pinned, operator-visible DEFAULT_PERMISSION_MODE.

    Loop is completion-seeking: launch until `completed == m` or
    `attempts == max_attempts` (default m+2). Fenced attempts (inconclusive/
    errored) do not advance the completed count, so environment flake extends the
    loop rather than failing the corpus.

    `resume=True` RE-ADOPTS the run-<n>/ dirs already in `temp_root` (issue #130):
    the corpus is NOT reinstalled (its id/commit are read back from CORPUS.json),
    finalized runs are counted as-is, a run the previous (killed) invocation left
    stuck `launched` is adjudicated by the orphan watchdog, and only the remaining
    runs are launched. So a kill-9 of the runner mid-measurement is recovered by
    re-invoking with the same temp dir."""
    launch = launch if launch is not None else launch_agent
    installer = installer if installer is not None else temp_install
    temp_root = Path(temp_root)
    temp_root.mkdir(parents=True, exist_ok=True)

    if resume and (temp_root / "skills").is_dir():
        skills_dir = temp_root / "skills"
        corpus_id, source_commit = _read_corpus_marker(skills_dir)
    else:
        skills_dir = installer(worktree, temp_root)
        source_commit = _source_commit()
        # Record the STABLE, install-path-invariant id in CORPUS.json (#153) so a
        # byte-identical corpus installed at a different temp root fingerprints the same.
        corpus_id = write_stable_corpus_marker(skills_dir, source_commit)

    m = scenario.m
    n = scenario.n
    if max_attempts is None:
        max_attempts = m + 2

    if resume:
        run_results, completed, attempt = _adopt_existing_runs(scenario, temp_root)
    else:
        run_results, completed, attempt = [], 0, 0
    # `max_new_runs` caps how many NEW subjects this single invocation launches
    # (issue #130): the round-1 runner was reaped by the environment at ~60 min of
    # total lifetime, mid-run. Driving ONE run per short-lived invocation (the
    # commander re-invoking `--resume` between them) keeps each invocation well
    # under that window, so the runner lives long enough to enforce its own deadline.
    launch_ceiling = max_attempts if max_new_runs is None else min(max_attempts, attempt + max_new_runs)
    while completed < m and attempt < launch_ceiling:
        try:
            rr = _run_once(scenario, attempt, temp_root, skills_dir, corpus_id, launch,
                           permission_mode=permission_mode, launcher=launcher)
        except Exception as exc:  # noqa: BLE001 — one run's crash must not sink siblings
            # Per-run isolation: an unexpected fault in one run is fenced (errored,
            # never a corpus FAIL) and the loop continues, instead of one bad run
            # taking the whole measurement down (issue #130). Leave a diagnosable
            # terminal meta so the fenced run is adjudicable, not a bare `launched`.
            rr = RunResult(status="errored", reason=f"run-exception: {exc}",
                           check_results=[])
            _write_meta(temp_root / f"run-{attempt}", {
                "corpus_id": corpus_id, "scenario_id": scenario.id,
                "status": rr.status, "reason": rr.reason, "exit_code": None,
                "finished_at": time.time(),
            })
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
    p.add_argument("--resume", metavar="DIR", default=None,
                   help="RESUME an earlier (possibly killed) run: re-adopt the run-<n>/ "
                        "dirs in DIR, adjudicate any orphaned by a dead runner, and launch "
                        "only the remaining runs (issue #130). Implies --keep-temp.")
    p.add_argument("--max-new-runs", type=int, default=None,
                   help="launch at most N NEW subjects this invocation, then return (issue "
                        "#130). Drive ONE run per short-lived --resume invocation so the "
                        "runner never outlives the environment's background-task reap window.")
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

    common = dict(worktree=args.worktree, launch=launch, installer=installer,
                  permission_mode=args.permission_mode, launcher=args.command,
                  max_new_runs=args.max_new_runs)
    if args.resume:
        temp_root = Path(args.resume)
        if not temp_root.is_dir():
            print(f"error: --resume dir does not exist: {temp_root}", file=sys.stderr)
            return 3
        try:
            v = run_scenario(scenario, temp_root=temp_root, resume=True, **common)
        finally:
            print(f"resumed temp dir: {temp_root}", file=sys.stderr)
    elif args.keep_temp:
        temp_root = Path(tempfile.mkdtemp(prefix="constellation-eval-"))
        try:
            v = run_scenario(scenario, temp_root=temp_root, **common)
        finally:
            print(f"kept temp dir: {temp_root}", file=sys.stderr)
    else:
        with tempfile.TemporaryDirectory(prefix="constellation-eval-") as td:
            v = run_scenario(scenario, temp_root=Path(td), **common)

    _print_verdict(v, as_json=args.json)
    return v.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
