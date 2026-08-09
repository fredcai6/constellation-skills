"""Agent-free unit layer for scripts/run_skill_eval.py (#106, gate g2).

This suite launches NO real agent, ever. The one real subprocess seam
(`launch_agent`) is an inert stub until g3; every test here either injects a
fake launcher (`--dry-run`/`--dry-run-fail`) or exercises pure logic. An autouse
guard hard-fails if any test attempts to spawn a real `claude` subprocess, so the
agent-free guarantee is mechanically enforced rather than trusted.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUN_SKILL_EVAL = ROOT / "scripts" / "run_skill_eval.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rse = load_module("run_skill_eval", RUN_SKILL_EVAL)


# --------------------------------------------------------------------------- #
# mechanical no-agent guard (autouse) — enforces the agent-free guarantee
# --------------------------------------------------------------------------- #
@pytest.fixture(autouse=True)
def _no_real_agent(monkeypatch):
    """Fail LOUDLY if any test spawns a real `claude` agent subprocess. Check
    subprocesses (`sys.executable <script> <run-dir>`) are allowed; a launcher
    whose basename starts with `claude` is not. Wraps BOTH `subprocess.run` (used by
    `run_check` and the taskkill tree-kill) and `subprocess.Popen` (used by the live
    `launch_agent` seam) so every spawn path is intercepted."""
    real_run = subprocess.run
    real_popen = subprocess.Popen

    def _assert_not_claude(cmd):
        argv0 = cmd[0] if isinstance(cmd, (list, tuple)) and cmd else cmd
        base = os.path.basename(str(argv0)).lower()
        assert not base.startswith("claude"), f"blocked real agent subprocess: {cmd!r}"

    def guarded_run(cmd, *args, **kwargs):
        _assert_not_claude(cmd)
        return real_run(cmd, *args, **kwargs)

    def guarded_popen(cmd, *args, **kwargs):
        _assert_not_claude(cmd)
        return real_popen(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)
    monkeypatch.setattr(subprocess, "Popen", guarded_popen)
    yield


# --------------------------------------------------------------------------- #
# helpers to fabricate canned run-dirs and scenarios (no agent)
# --------------------------------------------------------------------------- #
PASS_CHECK = (
    "import sys, pathlib\n"
    "run_dir = pathlib.Path(sys.argv[1])\n"
    "art = run_dir / 'workspace' / 'work-complete.txt'\n"
    "if art.is_file():\n"
    "    print('artifact present')\n"
    "    sys.exit(0)\n"
    "print('artifact MISSING')\n"
    "sys.exit(1)\n"
)
FAIL_CHECK = (
    "import sys\n"
    "print('this check always fails')\n"
    "sys.exit(1)\n"
)
ANSWER_CHECK = (
    "import sys\n"
    "print('advisory answer check (never gates)')\n"
    "sys.exit(1)\n"
)


def make_scenario(tmp_path: Path, *, process=(PASS_CHECK,), answer=(), toml=None, task="Solve it."):
    scen = tmp_path / "scenario"
    (scen / "checks").mkdir(parents=True)
    (scen / "task.md").write_text(task, encoding="utf-8")
    for i, body in enumerate(process):
        (scen / "checks" / f"proc_{i}.py").write_text(body, encoding="utf-8")
    if answer:
        (scen / "checks" / "answer").mkdir()
        for i, body in enumerate(answer):
            (scen / "checks" / "answer" / f"ans_{i}.py").write_text(body, encoding="utf-8")
    if toml is not None:
        (scen / "scenario.toml").write_text(toml, encoding="utf-8")
    return scen


def canned_run_dir(tmp_path: Path, *, artifact: bool) -> Path:
    """A run-dir whose workspace does (or does not) contain the completion stub."""
    run_dir = tmp_path / "run-0"
    ws = run_dir / "workspace"
    ws.mkdir(parents=True)
    if artifact:
        (ws / "work-complete.txt").write_text("done\n", encoding="utf-8")
    return run_dir


def cr(passed: bool, is_answer: bool = False) -> "rse.CheckResult":
    return rse.CheckResult(id="c", passed=passed, evidence="", is_answer=is_answer)


def completed_pass():
    return rse.RunResult(status="completed-pass", reason=None, check_results=[cr(True)])


def completed_fail():
    return rse.RunResult(status="completed-fail", reason="check", check_results=[cr(False)])


def fenced(status="inconclusive"):
    return rse.RunResult(status=status, reason="fenced", check_results=[])


# --------------------------------------------------------------------------- #
# build_eval_argv — PURE, mirrors run_crew.build_crew_argv
# --------------------------------------------------------------------------- #
EXEC_TAIL = ["--allowedTools", *rse.EXEC_ALLOWED_TOOLS]


def test_build_eval_argv_with_model():
    assert rse.build_eval_argv("claude", prompt="do it", model="sonnet") == [
        "claude", "-p", "do it", "--model", "sonnet", *EXEC_TAIL,
    ]


def test_build_eval_argv_without_model():
    assert rse.build_eval_argv("claude", prompt="do it", model=None) == [
        "claude", "-p", "do it", *EXEC_TAIL,
    ]


def test_build_eval_argv_with_permission_mode():
    # issue #115 tc2: the permission mode is plumbed onto the headless command line.
    assert rse.build_eval_argv(
        "claude", prompt="do it", model="sonnet", permission_mode="acceptEdits"
    ) == ["claude", "-p", "do it", "--model", "sonnet", "--permission-mode", "acceptEdits",
          *EXEC_TAIL]


def test_build_eval_argv_omits_permission_mode_when_none():
    assert rse.build_eval_argv("claude", prompt="p", model=None, permission_mode=None) == [
        "claude", "-p", "p", *EXEC_TAIL,
    ]


def test_exec_allowlist_always_present():
    # issue #126: a workspace settings.json allowlist is ignored in untrusted dirs,
    # so execution rights ride the command line — python-family only, nothing broader.
    argv = rse.build_eval_argv("claude", prompt="p", model=None)
    assert "--allowedTools" in argv
    tools = argv[argv.index("--allowedTools") + 1:]
    assert set(tools) == set(rse.EXEC_ALLOWED_TOOLS)
    assert all(t.startswith("Bash(py") or t.startswith("Bash(python") for t in tools)


def test_default_model_is_pinned_low_and_explicit():
    # issue #115 item 4: the default model is PINNED and explicit, never inherited
    # from the session — a low tier surfaces regressions a frontier model muscles through.
    assert rse.DEFAULT_MODEL == "claude-sonnet-4-5"


def test_default_permission_mode_is_least_powerful_write_mode():
    # issue #115 tc2: acceptEdits is the pinned, operator-visible default.
    assert rse.DEFAULT_PERMISSION_MODE == "acceptEdits"


def test_cli_permission_mode_defaults_to_pinned(tmp_path):
    args = rse.build_parser().parse_args([str(tmp_path)])
    assert args.permission_mode == rse.DEFAULT_PERMISSION_MODE


def test_cli_permission_mode_overridable(tmp_path):
    args = rse.build_parser().parse_args(["--permission-mode", "bypassPermissions", str(tmp_path)])
    assert args.permission_mode == "bypassPermissions"


# --------------------------------------------------------------------------- #
# load_scenario — directory-is-schema, structural T3
# --------------------------------------------------------------------------- #
def test_load_scenario_defaults(tmp_path):
    scen = make_scenario(tmp_path, process=(PASS_CHECK, FAIL_CHECK), answer=(ANSWER_CHECK,))
    s = rse.load_scenario(scen)
    assert s.id == "scenario"
    assert s.task_prompt.strip() == "Solve it."
    assert [p.name for p in s.process_checks] == ["proc_0.py", "proc_1.py"]
    assert [p.name for p in s.answer_checks] == ["ans_0.py"]
    assert (s.n, s.m, s.timeout_seconds) == (2, 3, 2400)
    assert s.model == rse.DEFAULT_MODEL
    assert s.fixture_dir is None


def test_load_scenario_toml_overrides(tmp_path):
    # an above-floor toml timeout is respected verbatim.
    scen = make_scenario(
        tmp_path,
        toml='id = "euler-1"\nmodel = "haiku"\nn = 3\nm = 4\ntimeout_seconds = 3000\n',
    )
    s = rse.load_scenario(scen)
    assert (s.id, s.model, s.n, s.m, s.timeout_seconds) == ("euler-1", "haiku", 3, 4, 3000)


def test_load_scenario_timeout_floor_clamps_below_minimum(tmp_path):
    # a scenario.toml can never starve an honest run below the floor (issue #126).
    scen = make_scenario(tmp_path, toml="timeout_seconds = 900\n")
    s = rse.load_scenario(scen)
    assert s.timeout_seconds == rse.SCENARIO_TIMEOUT_FLOOR_SECONDS == 2400


def test_load_scenario_missing_task_is_config_error(tmp_path):
    scen = make_scenario(tmp_path)
    (scen / "task.md").unlink()
    with pytest.raises(rse.EvalConfigError):
        rse.load_scenario(scen)


def test_load_scenario_zero_process_checks_is_config_error(tmp_path):
    # answer-only scenario: structural T3 — cannot pass on answer checks alone.
    scen = make_scenario(tmp_path, process=(), answer=(ANSWER_CHECK,))
    with pytest.raises(rse.EvalConfigError):
        rse.load_scenario(scen)


def test_load_scenario_answer_checks_excluded_from_process_glob(tmp_path):
    scen = make_scenario(tmp_path, process=(PASS_CHECK,), answer=(ANSWER_CHECK,))
    s = rse.load_scenario(scen)
    # checks/*.py must NOT sweep checks/answer/*.py into the process gate.
    assert all("answer" not in p.parts for p in s.process_checks)
    assert len(s.process_checks) == 1


def test_load_scenario_fixture_detected(tmp_path):
    scen = make_scenario(tmp_path)
    (scen / "fixture").mkdir()
    (scen / "fixture" / "seed.txt").write_text("x", encoding="utf-8")
    s = rse.load_scenario(scen)
    assert s.fixture_dir is not None and s.fixture_dir.name == "fixture"


# --------------------------------------------------------------------------- #
# run_check — subprocess of a CHECK against a canned run-dir (no agent)
# --------------------------------------------------------------------------- #
def test_run_check_known_good_passes(tmp_path):
    run_dir = canned_run_dir(tmp_path, artifact=True)
    check = tmp_path / "present.py"
    check.write_text(PASS_CHECK, encoding="utf-8")
    result = rse.run_check(check, run_dir)
    assert result.passed is True
    assert result.evidence == "artifact present"
    assert result.is_answer is False


def test_run_check_known_bad_fails(tmp_path):
    run_dir = canned_run_dir(tmp_path, artifact=False)
    check = tmp_path / "present.py"
    check.write_text(PASS_CHECK, encoding="utf-8")
    result = rse.run_check(check, run_dir)
    assert result.passed is False
    assert result.evidence == "artifact MISSING"


def test_run_check_marks_answer(tmp_path):
    run_dir = canned_run_dir(tmp_path, artifact=True)
    check = tmp_path / "ans.py"
    check.write_text(ANSWER_CHECK, encoding="utf-8")
    result = rse.run_check(check, run_dir, is_answer=True)
    assert result.is_answer is True
    assert result.passed is False


# --------------------------------------------------------------------------- #
# is_infra_marker — pure sniff
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text",
    ["hit the USAGE LIMIT", "rate limit exceeded", "quota reached", "Overloaded", "HTTP 429"],
)
def test_is_infra_marker_true(text):
    assert rse.is_infra_marker(text) is True


@pytest.mark.parametrize("text", ["", "AssertionError in test", "exit code 1", None])
def test_is_infra_marker_false(text):
    assert rse.is_infra_marker(text) is False


# --------------------------------------------------------------------------- #
# is_permission_denial — pure sniff (issue #115 tc3)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text",
    [
        "Claude requested permissions to write",  # verbatim g5-live marker
        "this action requires manual approval",
        "requires approval before running",
        "Permission denied",
        "operation not permitted",
    ],
)
def test_is_permission_denial_true(text):
    assert rse.is_permission_denial(text) is True


@pytest.mark.parametrize("text", ["", None, "wrote solution.py", "all tests passed"])
def test_is_permission_denial_false(text):
    assert rse.is_permission_denial(text) is False


# --------------------------------------------------------------------------- #
# ISSUE #454 — forced colour must not blind the sniffs
#
# The harness exports FORCE_COLOR=3, so a colour-capable child CLI emits ANSI even
# into a captured pipe. Every marker these two predicates match is a MULTI-WORD
# phrase, so a single escape between the words makes the substring miss. That
# failure is silent and points the wrong way: the infra fence would not fire and a
# merely rate-limited run would be recorded as a real FAIL against a good corpus.
# Each case below is a real marker with an escape placed exactly where a colourizer
# highlighting one keyword would put it.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text",
    [
        "\x1b[31musage\x1b[0m limit reached",
        "\x1b[1;33mrate\x1b[0m limit exceeded",
        "\x1b[31mError\x1b[0m: \x1b[1mquota\x1b[0m",
        "server \x1b[31moverloaded\x1b[0m",
        "HTTP \x1b[31m429\x1b[0m",
    ],
)
def test_is_infra_marker_sees_through_ansi_colour(text):
    assert rse.is_infra_marker(text) is True, (
        "#454 REGRESSION: a colourized infra banner did not fence the run, so "
        "environment flake would be recorded as a corpus FAIL."
    )


@pytest.mark.parametrize(
    "text",
    [
        "Claude \x1b[31mrequested\x1b[0m permissions to write",
        "this action \x1b[1mrequires\x1b[0m manual approval",
        "\x1b[31mPermission\x1b[0m denied",
        "operation \x1b[33mnot\x1b[0m permitted",
    ],
)
def test_is_permission_denial_sees_through_ansi_colour(text):
    assert rse.is_permission_denial(text) is True, (
        "#454 REGRESSION: a colourized permission refusal was not recognised."
    )


def test_ansi_stripping_does_not_invent_markers():
    """The guard must not have been bought by making the sniffs trigger-happy."""
    assert rse.strip_ansi("\x1b[32mall tests passed\x1b[0m") == "all tests passed"
    assert rse.is_infra_marker("\x1b[32mall tests passed\x1b[0m") is False
    assert rse.is_permission_denial("\x1b[32mwrote solution.py\x1b[0m") is False
    assert rse.strip_ansi(None) == ""


# --------------------------------------------------------------------------- #
# classify_run — the infra-fence + pass/fail table (pure)
# --------------------------------------------------------------------------- #
def test_classify_completed_pass():
    out = rse.LaunchOutcome(exit_code=0)
    rr = rse.classify_run(out, completion_present=True, completion_fresh=True, process_results=[cr(True), cr(True)])
    assert rr.status == "completed-pass"


def test_classify_completed_fail_when_process_check_fails():
    out = rse.LaunchOutcome(exit_code=0)
    rr = rse.classify_run(out, completion_present=True, completion_fresh=True, process_results=[cr(True), cr(False)])
    assert rr.status == "completed-fail"


def test_classify_exit_zero_no_spine_terminal_is_completed():
    # exit 0 with no completion artifact still counts as completed (tallied).
    out = rse.LaunchOutcome(exit_code=0)
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False, process_results=[cr(False)])
    assert rr.status == "completed-fail"


def test_classify_timeout_is_inconclusive_fenced():
    out = rse.LaunchOutcome(exit_code=None, timed_out=True)
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False, process_results=[])
    assert rr.status == "inconclusive"


def test_classify_timeout_with_all_checks_green_is_pass(tmp_path):
    # issue #126 verdict refinement: an honest run that finished the deliverable but
    # was tree-killed before its own process exit passes ALL (monotone) process
    # checks -> PASS, not fenced. Would have made attempts 9/10 read 1-of-3 each.
    out = rse.LaunchOutcome(exit_code=None, timed_out=True)
    rr = rse.classify_run(out, completion_present=True, completion_fresh=True,
                          process_results=[cr(True), cr(True)])
    assert rr.status == "completed-pass"
    assert rr.reason == "timeout-checks-green"


def test_classify_timeout_with_a_failing_check_stays_fenced():
    # a timeout whose workspace does NOT pass every check stays fenced (infra, not
    # a corpus FAIL) — monotonicity only carries a run that is ALREADY green.
    out = rse.LaunchOutcome(exit_code=None, timed_out=True)
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False,
                          process_results=[cr(True), cr(False)])
    assert rr.status == "inconclusive"
    assert rr.reason == "timeout"


def test_classify_usage_limit_marker_is_inconclusive_fenced():
    out = rse.LaunchOutcome(exit_code=1, stderr_text="Claude hit the usage limit, try later")
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False, process_results=[cr(False)])
    assert rr.status == "inconclusive"


def test_classify_launch_error_is_errored_fenced():
    out = rse.LaunchOutcome(exit_code=None, launch_error=True)
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False, process_results=[])
    assert rr.status == "errored"


def test_classify_corpus_mismatch_is_errored_fenced():
    out = rse.LaunchOutcome(exit_code=None, corpus_mismatch=True)
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False, process_results=[])
    assert rr.status == "errored"


def test_classify_nonzero_exit_no_marker_no_completion_is_errored():
    out = rse.LaunchOutcome(exit_code=7, stderr_text="segfault")
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False, process_results=[])
    assert rr.status == "errored"


def test_classify_permission_blocked_is_errored_fenced():
    # issue #115 tc3: exit 0 but the workspace is byte-unchanged AND a permission-
    # denial marker fired -> the ENVIRONMENT blocked a good corpus, so FENCED (errored),
    # never tallied as a corpus FAIL.
    out = rse.LaunchOutcome(exit_code=0, stderr_text="Claude requested permissions to write")
    rr = rse.classify_run(
        out, completion_present=False, completion_fresh=False, process_results=[cr(False)],
        workspace_unchanged=True, permission_denied=True,
    )
    assert rr.status == "errored"
    assert rr.reason == "permission-blocked"


def test_classify_exit_zero_unchanged_without_denial_marker_stays_completed_fail():
    # The permission fence needs BOTH signals: with no denial marker the g2-ratified
    # exit-0-no-terminal rule still holds — completed-fail, NOT fenced.
    out = rse.LaunchOutcome(exit_code=0)
    rr = rse.classify_run(
        out, completion_present=False, completion_fresh=False, process_results=[cr(False)],
        workspace_unchanged=True, permission_denied=False,
    )
    assert rr.status == "completed-fail"


def test_classify_denial_marker_but_workspace_changed_stays_completed_fail():
    # The agent DID mutate the workspace (it did work) but its output mentions a
    # permission — a stray marker must not fence a run that produced output: tallied.
    out = rse.LaunchOutcome(exit_code=0)
    rr = rse.classify_run(
        out, completion_present=False, completion_fresh=False, process_results=[cr(False)],
        workspace_unchanged=False, permission_denied=True,
    )
    assert rr.status == "completed-fail"


# --------------------------------------------------------------------------- #
# verdict — N-of-M math over COMPLETED runs only (infra-fence)
# --------------------------------------------------------------------------- #
def test_verdict_two_of_three_passes():
    v = rse.verdict([completed_pass(), completed_pass(), completed_fail()], n=2, m=3)
    assert (v.status, v.exit_code) == ("PASS", 0)
    assert (v.completed_count, v.passed_count) == (3, 2)


def test_verdict_one_of_three_fails():
    v = rse.verdict([completed_pass(), completed_fail(), completed_fail()], n=2, m=3)
    assert (v.status, v.exit_code) == ("FAIL", 1)
    assert v.passed_count == 1


def test_verdict_one_completed_two_fenced_is_inconclusive_not_fail():
    # 1 completed-pass + 2 fenced (env flake) must NEVER be a FAIL of a good corpus.
    v = rse.verdict([completed_pass(), fenced("inconclusive"), fenced("errored")], n=2, m=3)
    assert (v.status, v.exit_code) == ("INCONCLUSIVE", 2)
    assert v.completed_count == 1
    assert v.fenced_count == 2


def test_verdict_all_fenced_is_inconclusive():
    v = rse.verdict([fenced("inconclusive"), fenced("errored"), fenced("inconclusive")], n=2, m=3)
    assert v.exit_code == 2


# --------------------------------------------------------------------------- #
# corpus provenance — sha256 id, marker, assert
# --------------------------------------------------------------------------- #
def make_corpus(tmp_path: Path) -> Path:
    sk = tmp_path / "skills"
    (sk / "constellation-x").mkdir(parents=True)
    (sk / "constellation-x" / "SKILL.md").write_text("skill body\n", encoding="utf-8")
    return sk


def test_compute_corpus_id_is_stable_and_sensitive(tmp_path):
    sk = make_corpus(tmp_path)
    id1 = rse.compute_corpus_id(sk)
    assert id1.startswith("sha256:")
    assert rse.compute_corpus_id(sk) == id1  # stable
    (sk / "constellation-x" / "SKILL.md").write_text("skill body CHANGED\n", encoding="utf-8")
    assert rse.compute_corpus_id(sk) != id1  # sensitive to content


def test_write_marker_and_assert_corpus(tmp_path):
    sk = make_corpus(tmp_path)
    corpus_id = rse.write_corpus_marker(sk, "abc123")
    assert (sk / "CORPUS.json").is_file()
    # marker itself must not perturb the id (excluded from the hash).
    assert rse.compute_corpus_id(sk) == corpus_id
    assert rse.assert_corpus(sk, corpus_id) is True
    assert rse.assert_corpus(sk, "sha256:deadbeef") is False


# --------------------------------------------------------------------------- #
# answer checks never move the verdict (integration through run_scenario)
# --------------------------------------------------------------------------- #
def test_answer_only_failure_still_passes(tmp_path):
    # process check passes, answer check fails -> PASS (answers never gate).
    scen = make_scenario(tmp_path, process=(PASS_CHECK,), answer=(ANSWER_CHECK,))
    s = rse.load_scenario(scen)
    v = rse.run_scenario(s, temp_root=tmp_path / "t", launch=rse.dry_run_launch, installer=rse._dry_installer)
    assert v.status == "PASS"
    # the failing answer check IS recorded on each per-run record, just non-gating.
    answer_records = [c for rr in v.per_run for c in rr.check_results if c.is_answer]
    assert answer_records and all(not c.passed for c in answer_records)


# --------------------------------------------------------------------------- #
# g3 live layer — launch_agent + temp_install, still agent-free
# --------------------------------------------------------------------------- #
# A throwaway source skill tree so the REAL temp_install (discover_skills +
# install_skills) runs end-to-end without depending on (or mutating) the real
# skills/ corpus. constellation-foo is not in any script/reference bundle, so
# install copies exactly this dir — fast and hermetic.
FOO_SKILL_MD = (
    "---\n"
    "name: constellation-foo\n"
    "description: throwaway eval-runner fixture skill\n"
    "---\n"
    "# foo\n"
    "A minimal skill body for the g3 e2e tests.\n"
)


def throwaway_worktree(tmp_path: Path) -> Path:
    """A worktree whose `skills/` holds one valid throwaway skill — the source
    the REAL temp_install installs from."""
    wt = tmp_path / "wt"
    skill = wt / "skills" / "constellation-foo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(FOO_SKILL_MD, encoding="utf-8")
    return wt


def fake_pass_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout):
    """Agent-free fake: writes the completion artifact a finished run leaves, so
    the process check bites and the run classifies completed-pass. Spawns nothing."""
    ws = Path(cwd)
    ws.mkdir(parents=True, exist_ok=True)
    (ws / rse.COMPLETION_ARTIFACT).write_text("fake agent: complete\n", encoding="utf-8")
    Path(stdout_path).write_text("fake agent transcript\n", encoding="utf-8")
    Path(stderr_path).write_text("", encoding="utf-8")
    return rse.LaunchOutcome(exit_code=0)


def fake_fail_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout):
    """Agent-free fake: exits 0 (so the run COMPLETED) but leaves a broken
    workspace with no completion artifact, so the process check fails -> completed
    -fail (tallied, never fenced). Spawns nothing."""
    ws = Path(cwd)
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "BROKEN.txt").write_text("fake agent: no completion\n", encoding="utf-8")
    Path(stdout_path).write_text("fake agent transcript (broken)\n", encoding="utf-8")
    Path(stderr_path).write_text("", encoding="utf-8")
    return rse.LaunchOutcome(exit_code=0)


def test_temp_install_real_installs_corpus(tmp_path):
    # REAL temp_install (install_constellation.install_skills) into system-style temp.
    wt = throwaway_worktree(tmp_path)
    skills_dir = rse.temp_install(str(wt), tmp_path / "temp")
    assert skills_dir == tmp_path / "temp" / "skills"
    assert (skills_dir / "constellation-foo" / "SKILL.md").is_file()
    # the source tree is never mutated by the install.
    assert (wt / "skills" / "constellation-foo" / "SKILL.md").is_file()


def test_end_to_end_pass_with_real_temp_install_and_fake_launch(tmp_path):
    # WHOLE pipeline: real temp-install -> corpus id+marker+per-run assert ->
    # launch seam (fake) -> transcript -> checks -> classify -> N-of-M -> PASS.
    wt = throwaway_worktree(tmp_path)
    scen = make_scenario(tmp_path, process=(PASS_CHECK,), answer=(ANSWER_CHECK,))
    s = rse.load_scenario(scen)
    v = rse.run_scenario(s, temp_root=tmp_path / "t", worktree=str(wt), launch=fake_pass_launch)
    assert (v.status, v.exit_code) == ("PASS", 0)
    assert v.completed_count == 3 and v.passed_count >= 2 and v.fenced_count == 0
    assert v.corpus_id and v.corpus_id.startswith("sha256:")
    # every run asserted its copy against the installed corpus id (no mismatch).
    assert all(rr.status == "completed-pass" for rr in v.per_run)
    # answer check ran and is recorded but never moved the verdict.
    answer_records = [c for rr in v.per_run for c in rr.check_results if c.is_answer]
    assert answer_records and all(not c.passed for c in answer_records)


def _tokened_worktree(tmp_path: Path) -> Path:
    """Like `throwaway_worktree` but the skill body carries a `<skill-dir>` token, so
    the installer's `rewrite_installed_skill_paths` bakes the ABSOLUTE install path
    (`target.as_posix()`) into the installed SKILL.md. That reproduces the #153
    pollution the stable corpus id must normalize out; without a rewritable token the
    two installs are byte-identical and the RAW-differs canary below is a false green."""
    wt = tmp_path / "wt"
    skill = wt / "skills" / "constellation-foo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        FOO_SKILL_MD + "Run `python <skill-dir>/scripts/foo.py` from <skill-dir>.\n",
        encoding="utf-8",
    )
    return wt


def test_corpus_id_install_path_invariant(tmp_path):
    """#153: two byte-identical corpora installed at DIFFERENT absolute temp roots must
    hash to the SAME corpus_id. Driven through the REAL copy path — `run_scenario` ->
    `_run_once` copies the installed tree into `workspace/.claude/skills` and asserts it
    against the recorded id — so a naive "strip the dir I am hashing" fix (which no-ops
    on the copy) would false-fence and be caught here, not pass. The RAW `compute_corpus_id`
    of the two installed trees DIFFERS (the installer baked the absolute install path in);
    that canary proves the equality below is the fix normalizing real pollution out, not
    two trivially-identical trees."""
    wt = _tokened_worktree(tmp_path)
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    s = rse.load_scenario(scen)

    root1 = tmp_path / "install-A"
    root2 = tmp_path / "install-B"
    v1 = rse.run_scenario(s, temp_root=root1, worktree=str(wt), launch=fake_pass_launch)
    v2 = rse.run_scenario(s, temp_root=root2, worktree=str(wt), launch=fake_pass_launch)

    # Install-path invariance: same content, different absolute install path, same id.
    assert v1.corpus_id == v2.corpus_id
    assert v1.corpus_id.startswith("sha256:")
    # No run false-fenced as corpus_mismatch through the assert site (~861): every copy
    # normalized back to the recorded stable id.
    assert v1.fenced_count == 0 and v2.fenced_count == 0
    assert all(rr.status == "completed-pass" for rr in v1.per_run)
    assert all(rr.status == "completed-pass" for rr in v2.per_run)

    # Canary: the RAW (path-dependent) ids of the two installed trees DIFFER, proving the
    # baked absolute path really is present and the equality above is the fix at work.
    raw1 = rse.compute_corpus_id(root1 / "skills")
    raw2 = rse.compute_corpus_id(root2 / "skills")
    assert raw1 != raw2


def test_end_to_end_fail_with_real_temp_install_and_fake_launch(tmp_path):
    # Same real pipeline, broken transcript -> completed-fail -> FAIL (never fenced).
    wt = throwaway_worktree(tmp_path)
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    s = rse.load_scenario(scen)
    v = rse.run_scenario(s, temp_root=tmp_path / "t", worktree=str(wt), launch=fake_fail_launch)
    assert (v.status, v.exit_code) == ("FAIL", 1)
    assert all(rr.status == "completed-fail" for rr in v.per_run)
    assert v.fenced_count == 0


# --------------------------------------------------------------------------- #
# launch_agent's real mapping feeds the infra-fence (agent-free: python/no binary)
# --------------------------------------------------------------------------- #
def test_launch_agent_timeout_maps_to_fenced_inconclusive(tmp_path):
    # A real subprocess (python, not claude) that outlives the timeout -> timed_out
    # -> classify_run fences it as inconclusive. Proves the mapping feeds the fence.
    argv = [sys.executable, "-c", "import time; time.sleep(30)"]
    out = rse.launch_agent(
        argv, cwd=str(tmp_path), env=dict(os.environ),
        stdout_path=str(tmp_path / "o.txt"), stderr_path=str(tmp_path / "e.txt"),
        timeout=0.5,
    )
    assert out.timed_out is True and out.exit_code is None
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False, process_results=[])
    assert rr.status == "inconclusive"


def test_launch_agent_spawn_failure_maps_to_fenced_errored(tmp_path):
    # A binary that does not exist -> FileNotFoundError -> launch_error -> classify
    # fences as errored. Not a claude binary, so the guard permits the real spawn
    # attempt; it fails to spawn, which is exactly the mapping under test.
    argv = ["this-binary-does-not-exist-xyz-106", "-p", "hi"]
    out = rse.launch_agent(
        argv, cwd=str(tmp_path), env=dict(os.environ),
        stdout_path=str(tmp_path / "o.txt"), stderr_path=str(tmp_path / "e.txt"),
        timeout=10,
    )
    assert out.launch_error is True and out.exit_code is None
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False, process_results=[])
    assert rr.status == "errored"


# --------------------------------------------------------------------------- #
# launch_agent deadline enforcement — a hanging child (never-EOF pipes) is
# tree-killed on the deadline and fenced as timeout. NO real agent, NO real sleep
# past the sub-second deadline: a fake Popen double stands in for a wedged child.
# --------------------------------------------------------------------------- #
class _BlockingPipe:
    """A pipe double whose read() blocks until the child is 'killed', then EOF.
    Models a grandchild holding the write-handle so read() never naturally returns —
    the exact wedge that hung the old subprocess.run(timeout=) wait."""

    def __init__(self, done: threading.Event):
        self._done = done

    def read(self, _n):
        self._done.wait()
        return b""


class _HangingPopen:
    """A subprocess.Popen double that NEVER exits on its own: poll() stays None and
    its pipes never hit EOF until something kills it. Spawns nothing."""

    def __init__(self):
        self.pid = 987654
        self.returncode = None
        self._done = threading.Event()
        self.stdout = _BlockingPipe(self._done)
        self.stderr = _BlockingPipe(self._done)

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        self._done.wait(timeout)
        return self.returncode

    def _die(self, code=-9):
        self.returncode = code
        self._done.set()


def test_launch_agent_deadline_tree_kills_hanging_child_and_fences_timeout(tmp_path, monkeypatch):
    hanging = _HangingPopen()
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: hanging)

    killed: list[int] = []

    def spy_tree_kill(proc):
        killed.append(proc.pid)
        proc._die()  # the tree-kill is what lets poll()/read() finally return

    monkeypatch.setattr(rse, "_tree_kill", spy_tree_kill)

    out = rse.launch_agent(
        ["dummy-launcher", "-p", "hi"], cwd=str(tmp_path), env=dict(os.environ),
        stdout_path=str(tmp_path / "o.txt"), stderr_path=str(tmp_path / "e.txt"),
        timeout=0.3,
    )
    # deadline fired -> tree-kill invoked on the hung child -> fenced timeout.
    assert killed == [hanging.pid]
    assert out.timed_out is True and out.exit_code is None
    rr = rse.classify_run(out, completion_present=False, completion_fresh=False, process_results=[])
    assert rr.status == "inconclusive" and rr.reason == "timeout"


def test_meta_json_written_incrementally_launch_then_final(tmp_path):
    # meta.json is written TWICE: a launch record (status "launched", exit_code null)
    # visible the moment the launcher is invoked, then the final classification.
    wt = throwaway_worktree(tmp_path)
    temp_root = tmp_path / "t"
    temp_root.mkdir()
    skills_dir = rse.temp_install(str(wt), temp_root)
    # Seed the STABLE id the way run_scenario now does (#153): _run_once's assert
    # site normalizes the copy against skills_dir, so it must receive the stable id.
    corpus_id = rse.write_stable_corpus_marker(skills_dir, "abc123")
    s = rse.load_scenario(make_scenario(tmp_path, process=(PASS_CHECK,)))

    seen: dict = {}

    def checking_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout):
        meta = Path(cwd).parent / "meta.json"
        seen["present_at_launch"] = meta.is_file()
        if meta.is_file():
            seen["launch_record"] = json.loads(meta.read_text(encoding="utf-8"))
        return fake_pass_launch(argv, cwd=cwd, env=env, stdout_path=stdout_path,
                                stderr_path=stderr_path, timeout=timeout)

    rr = rse._run_once(s, 0, temp_root, skills_dir, corpus_id, checking_launch)

    # the launch record existed BEFORE the launcher returned (incremental write).
    assert seen["present_at_launch"] is True
    assert seen["launch_record"]["status"] == "launched"
    assert seen["launch_record"]["exit_code"] is None
    # the final record overwrote it with the resolved classification.
    final = json.loads((temp_root / "run-0" / "meta.json").read_text(encoding="utf-8"))
    assert final["status"] == "completed-pass" == rr.status
    assert final["exit_code"] == 0
    assert "finished_at" in final


def test_all_fenced_run_scenario_is_inconclusive_not_fail(tmp_path):
    # timeouts across the whole loop -> INCONCLUSIVE, never FAIL a corpus that never ran.
    wt = throwaway_worktree(tmp_path)
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    s = rse.load_scenario(scen)

    def fake_timeout_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout):
        return rse.LaunchOutcome(exit_code=None, timed_out=True)

    v = rse.run_scenario(s, temp_root=tmp_path / "t", worktree=str(wt), launch=fake_timeout_launch)
    assert (v.status, v.exit_code) == ("INCONCLUSIVE", 2)
    assert v.completed_count == 0 and v.fenced_count >= 1


def test_permission_blocked_run_scenario_is_inconclusive_not_fail(tmp_path):
    # issue #115 tc3, end-to-end: a launcher that writes NOTHING into the workspace
    # and emits a permission-denial marker leaves the workspace byte-unchanged -> the
    # permission-block fence fires -> INCONCLUSIVE, never a FAIL of a good corpus.
    wt = throwaway_worktree(tmp_path)
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    s = rse.load_scenario(scen)

    def fake_permission_denied_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout):
        # Write ONLY the transcript (outside the workspace); touch nothing under cwd,
        # so the seeded workspace is byte-unchanged. Exit 0 (the false-red shape).
        Path(stdout_path).write_text("Claude requested permissions to write\n", encoding="utf-8")
        Path(stderr_path).write_text("", encoding="utf-8")
        return rse.LaunchOutcome(exit_code=0)

    v = rse.run_scenario(s, temp_root=tmp_path / "t", worktree=str(wt),
                         launch=fake_permission_denied_launch)
    assert (v.status, v.exit_code) == ("INCONCLUSIVE", 2)
    assert v.completed_count == 0 and v.fenced_count >= 1
    assert all(rr.status == "errored" and rr.reason == "permission-blocked" for rr in v.per_run)


# --------------------------------------------------------------------------- #
# strict process checks post-sentinel-removal (issue #115 tc1) — against the REAL
# shipped scenario checks, so the sentinel-hole is proven closed on what ships.
# --------------------------------------------------------------------------- #
REAL_CHECKS_DIR = ROOT / "evals" / "euler-1-multiples" / "checks"


def _canned_workspace_run_dir(tmp_path: Path, files: dict) -> Path:
    run_dir = tmp_path / "run-0"
    ws = run_dir / "workspace"
    ws.mkdir(parents=True)
    for name, body in files.items():
        (ws / name).write_text(body, encoding="utf-8")
    return run_dir


def test_sentinel_only_workspace_now_fails_strict_checks(tmp_path):
    # The old sentinel-hole: a workspace with ONLY the completion sentinel (no real
    # solution, no test). Post-removal, the REAL shipped checks FAIL it.
    run_dir = _canned_workspace_run_dir(tmp_path, {"work-complete.txt": "done\n"})
    ap = rse.run_check(REAL_CHECKS_DIR / "artifact_present.py", run_dir)
    tg = rse.run_check(REAL_CHECKS_DIR / "tests_green.py", run_dir)
    assert ap.passed is False, ap.evidence
    assert tg.passed is False, tg.evidence


def test_real_solution_and_green_test_pass_strict_checks(tmp_path):
    # The positive: a real solution.py + a green test_solution.py PASS the shipped checks.
    run_dir = _canned_workspace_run_dir(tmp_path, {
        "solution.py": "def solve():\n    return 42\n",
        "test_solution.py": "def test_ok():\n    assert 42 == 42\n",
    })
    ap = rse.run_check(REAL_CHECKS_DIR / "artifact_present.py", run_dir)
    tg = rse.run_check(REAL_CHECKS_DIR / "tests_green.py", run_dir)
    assert ap.passed is True, ap.evidence
    assert tg.passed is True, tg.evidence


def test_dry_run_passes_real_scenario_checks_strictly(tmp_path):
    # The runner's --dry-run now synthesizes real deliverables, so it PASSes the REAL
    # euler-1 scenario (strict checks, no sentinel fallback) end-to-end.
    scenario_dir = ROOT / "evals" / "euler-1-multiples"
    assert rse.main(["--dry-run", str(scenario_dir)]) == 0


def test_dry_run_fail_fails_real_scenario_checks_strictly(tmp_path):
    scenario_dir = ROOT / "evals" / "euler-1-multiples"
    assert rse.main(["--dry-run-fail", str(scenario_dir)]) == 1


def test_permission_mode_reaches_launcher_argv(tmp_path):
    # issue #115 tc2, full plumbing: run_scenario -> _run_once -> build_eval_argv puts
    # the requested --permission-mode on the argv the launcher actually receives.
    wt = throwaway_worktree(tmp_path)
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    s = rse.load_scenario(scen)
    seen: list[list[str]] = []

    def recording_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout):
        seen.append(list(argv))
        return fake_pass_launch(argv, cwd=cwd, env=env, stdout_path=stdout_path,
                                stderr_path=stderr_path, timeout=timeout)

    rse.run_scenario(s, temp_root=tmp_path / "t", worktree=str(wt),
                     launch=recording_launch, permission_mode="acceptEdits")
    assert seen, "launcher was never invoked"
    for argv in seen:
        assert "--permission-mode" in argv
        assert argv[argv.index("--permission-mode") + 1] == "acceptEdits"


# --------------------------------------------------------------------------- #
# the agent-free guard STILL BITES on the live launch_agent (mechanical guarantee)
# --------------------------------------------------------------------------- #
def test_agent_free_guard_still_bites_on_launch_agent(tmp_path):
    # launch_agent is implemented on subprocess.Popen, which the autouse guard wraps;
    # a real `claude` argv is blocked before any process is spawned. The guard's
    # AssertionError is neither TimeoutExpired nor OSError, so it propagates out.
    argv = rse.build_eval_argv("claude", prompt="do it", model="sonnet")
    with pytest.raises(AssertionError, match="blocked real agent subprocess"):
        rse.launch_agent(
            argv, cwd=str(tmp_path), env=dict(os.environ),
            stdout_path=str(tmp_path / "o.txt"), stderr_path=str(tmp_path / "e.txt"),
            timeout=10,
        )


# --------------------------------------------------------------------------- #
# --dry-run / --dry-run-fail end-to-end through main() (agent-free floor)
# --------------------------------------------------------------------------- #
def test_dry_run_exits_zero(tmp_path):
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    assert rse.main(["--dry-run", str(scen)]) == 0


def test_dry_run_fail_exits_one(tmp_path):
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    assert rse.main(["--dry-run-fail", str(scen)]) == 1


def test_dry_run_fail_is_completed_fail_not_fenced(tmp_path):
    # the falsification floor must FAIL (exit 1), never fence to INCONCLUSIVE (exit 2).
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    s = rse.load_scenario(scen)
    v = rse.run_scenario(s, temp_root=tmp_path / "t", launch=rse.dry_run_fail_launch, installer=rse._dry_installer)
    assert v.status == "FAIL"
    assert all(rr.status == "completed-fail" for rr in v.per_run)
    assert v.fenced_count == 0


def test_zero_process_checks_via_cli_is_schema_error(tmp_path):
    scen = make_scenario(tmp_path, process=(), answer=(ANSWER_CHECK,))
    assert rse.main(["--dry-run", str(scen)]) == 3


# --------------------------------------------------------------------------- #
# issue #130 — runner durability: heartbeats, orphan watchdog, resume, isolation
# --------------------------------------------------------------------------- #
def _seed_run_dir(temp_root: Path, index: int, *, meta: dict, artifact: bool) -> Path:
    """Seed a run-<index>/ with a meta.json and (optionally) a passing workspace,
    modelling the on-disk state a prior invocation left behind."""
    run_dir = temp_root / f"run-{index}"
    ws = run_dir / "workspace"
    ws.mkdir(parents=True)
    if artifact:
        (ws / rse.COMPLETION_ARTIFACT).write_text("done\n", encoding="utf-8")
    (run_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return run_dir


def test_stamp_meta_heartbeat_updates_only_launched_meta(tmp_path):
    run_dir = tmp_path / "run-0"
    run_dir.mkdir()
    (run_dir / "meta.json").write_text(
        json.dumps({"status": "launched", "launched_at": 1000.0}), encoding="utf-8")
    rse._stamp_meta_heartbeat(run_dir)
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    assert "heartbeat_at" in meta and "elapsed_seconds" in meta
    # a terminal meta is never re-stamped (a heartbeat cannot un-finalize a run).
    (run_dir / "meta.json").write_text(
        json.dumps({"status": "completed-pass"}), encoding="utf-8")
    rse._stamp_meta_heartbeat(run_dir)
    assert "heartbeat_at" not in json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))


class _BrieflyAlivePopen:
    """A Popen double that reports alive for a few polls then exits 0, with pipes
    already at EOF so drain threads finish immediately. Spawns nothing. Lets the
    heartbeat stamp fire inside launch_agent's poll loop without a real subject."""

    def __init__(self, alive_polls: int = 3):
        import io
        self.pid = 555
        self.returncode = None
        self._polls = 0
        self._alive = alive_polls
        self.stdout = io.BytesIO(b"")
        self.stderr = io.BytesIO(b"")

    def poll(self):
        self._polls += 1
        if self._polls > self._alive:
            self.returncode = 0
        return self.returncode

    def wait(self, timeout=None):
        self.returncode = 0
        return 0


def test_launch_agent_stamps_heartbeat_into_launch_meta(tmp_path, monkeypatch):
    # A live-but-slow subject: launch_agent must stamp a liveness heartbeat into the
    # run's launch meta while it polls, so a watcher can see the runner is alive.
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: _BrieflyAlivePopen())
    monkeypatch.setattr(rse, "_HEARTBEAT_INTERVAL_SECONDS", 0.0)  # stamp every poll
    run_dir = tmp_path / "run-0"
    run_dir.mkdir()
    (run_dir / "meta.json").write_text(
        json.dumps({"status": "launched", "launched_at": 1.0}), encoding="utf-8")
    out = rse.launch_agent(
        ["dummy-launcher", "-p", "hi"], cwd=str(run_dir / "workspace"),
        env=dict(os.environ), stdout_path=str(run_dir / "transcript.txt"),
        stderr_path=str(run_dir / "stderr.txt"), timeout=10,
    )
    assert out.exit_code == 0
    assert "heartbeat_at" in json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))


def test_adjudicate_orphan_green_workspace_is_completed_pass(tmp_path):
    # A run the runner died mid-flight on, but whose workspace ALREADY passes every
    # process check: the deliverable is real (checks are monotone) -> completed-pass.
    s = rse.load_scenario(make_scenario(tmp_path, process=(PASS_CHECK,)))
    temp_root = tmp_path / "t"; temp_root.mkdir()
    run_dir = _seed_run_dir(temp_root, 0, artifact=True,
                            meta={"status": "launched", "corpus_id": "sha256:x",
                                  "launched_at": 1.0, "scenario_id": s.id})
    rr = rse._adjudicate_orphan(s, run_dir)
    assert rr.status == "completed-pass" and rr.reason == "orphan-checks-green"
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    # rewritten to a terminal, adjudicable record that preserves the launch fields.
    assert meta["status"] == "completed-pass" and meta["adjudicated_orphan"] is True
    assert meta["corpus_id"] == "sha256:x" and "finished_at" in meta


def test_adjudicate_orphan_broken_workspace_is_fenced_inconclusive(tmp_path):
    # A run the runner died on before the work finished: fenced (never a corpus FAIL).
    s = rse.load_scenario(make_scenario(tmp_path, process=(PASS_CHECK,)))
    temp_root = tmp_path / "t"; temp_root.mkdir()
    run_dir = _seed_run_dir(temp_root, 0, artifact=False,
                            meta={"status": "launched", "launched_at": 1.0, "scenario_id": s.id})
    rr = rse._adjudicate_orphan(s, run_dir)
    assert rr.status == "inconclusive" and rr.reason == "orphaned-runner-died"


def test_adopt_existing_runs_counts_terminal_and_adjudicates_orphan(tmp_path):
    s = rse.load_scenario(make_scenario(tmp_path, process=(PASS_CHECK,)))
    temp_root = tmp_path / "t"; temp_root.mkdir()
    _seed_run_dir(temp_root, 0, artifact=False,
                  meta={"status": "completed-fail", "reason": "process-check-failed"})
    _seed_run_dir(temp_root, 1, artifact=True,   # a green orphan -> completed-pass
                  meta={"status": "launched", "launched_at": 1.0, "scenario_id": s.id})
    run_results, completed, next_index = rse._adopt_existing_runs(s, temp_root)
    assert next_index == 2  # resume launches from run-2
    assert completed == 2   # one adopted completed-fail + one adjudicated completed-pass
    assert [r.status for r in run_results] == ["completed-fail", "completed-pass"]


def test_adopt_existing_runs_routes_corrupt_meta_through_adjudicate_orphan_and_continues(tmp_path):
    # issue #205: a corrupt/truncated meta.json (a kill mid-write) must be routed
    # through _adjudicate_orphan -- exactly like the sibling "launched" branch --
    # and the scan must CONTINUE past it, not `break` and silently strand every
    # slot after it as unaccounted-for.
    s = rse.load_scenario(make_scenario(tmp_path, process=(PASS_CHECK,)))
    temp_root = tmp_path / "t"; temp_root.mkdir()

    # run-0: corrupt the REAL bytes the real _write_meta produced (not a
    # hand-authored json.dumps fixture) -- write a valid meta.json via the real
    # writer, then truncate it mid-object to simulate a process killed mid-flush.
    run_dir_0 = temp_root / "run-0"
    (run_dir_0 / "workspace").mkdir(parents=True)
    (run_dir_0 / "workspace" / rse.COMPLETION_ARTIFACT).write_text("done\n", encoding="utf-8")
    rse._write_meta(run_dir_0, {"status": "launched", "launched_at": 1.0,
                                "scenario_id": s.id, "corpus_id": "sha256:x"})
    real_bytes = (run_dir_0 / "meta.json").read_bytes()
    (run_dir_0 / "meta.json").write_bytes(real_bytes[: len(real_bytes) // 2])  # truncate mid-write

    # run-1: a normal terminal record AFTER the corrupt slot -- proves the scan
    # continued past run-0 rather than stopping there.
    _seed_run_dir(temp_root, 1, artifact=False,
                  meta={"status": "completed-fail", "reason": "process-check-failed"})

    run_results, completed, next_index = rse._adopt_existing_runs(s, temp_root)

    # run-0's workspace already carries the completion artifact -> _adjudicate_orphan
    # (checks monotone) resolves it completed-pass, exactly like a green "launched" orphan.
    assert [r.status for r in run_results] == ["completed-pass", "completed-fail"]
    assert completed == 2
    assert next_index == 2  # scan continued past the corrupt slot to run-1's free index
    # _adjudicate_orphan rewrote the corrupt record to an adjudicable terminal one.
    meta0 = json.loads((run_dir_0 / "meta.json").read_text(encoding="utf-8"))
    assert meta0["status"] == "completed-pass" and meta0["adjudicated_orphan"] is True


def test_resume_recovers_killed_runner_mid_measurement(tmp_path):
    # THE regression bar (issue #130): a kill-9 of the runner mid-measurement leaves
    # run-0 finalized + run-1 stuck "launched". Re-invoking with resume=True must
    # adjudicate the orphan, launch ONLY the remaining run, and reach a verdict —
    # WITHOUT reinstalling the corpus (proven by an installer that refuses to run).
    wt = throwaway_worktree(tmp_path)
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    s = rse.load_scenario(scen)
    temp_root = tmp_path / "t"; temp_root.mkdir()
    skills_dir = rse.temp_install(str(wt), temp_root)
    # Stable marker (#153): resume reads this id back and _run_once asserts the copy
    # against it, so it must be the same install-path-invariant id run_scenario writes.
    rse.write_stable_corpus_marker(skills_dir, "abc123")
    # kill-simulation: run-0 finalized completed-pass; run-1 orphaned "launched"
    # (its workspace already carries the deliverable -> adjudicates completed-pass).
    _seed_run_dir(temp_root, 0, artifact=False, meta={"status": "completed-pass"})
    _seed_run_dir(temp_root, 1, artifact=True,
                  meta={"status": "launched", "launched_at": 1.0, "scenario_id": s.id})

    def _refuse_installer(worktree, tr):
        raise AssertionError("resume must NOT reinstall the corpus")

    v = rse.run_scenario(s, temp_root=temp_root, launch=fake_pass_launch,
                         installer=_refuse_installer, resume=True)
    assert (v.status, v.exit_code) == ("PASS", 0)
    assert v.completed_count == 3 and v.passed_count >= 2
    # run-2 is the only newly-launched run; run-0/1 were resumed from disk.
    assert (temp_root / "run-2" / "meta.json").is_file()
    assert not (temp_root / "run-3").exists()


def test_max_new_runs_caps_new_launches_this_invocation(tmp_path):
    # issue #130 reap mitigation: a single invocation launches at most N new subjects,
    # so the commander drives one short-lived run per --resume rather than a long loop.
    wt = throwaway_worktree(tmp_path)
    s = rse.load_scenario(make_scenario(tmp_path, process=(PASS_CHECK,)))  # m=3
    v = rse.run_scenario(s, temp_root=tmp_path / "t", worktree=str(wt),
                         launch=fake_pass_launch, max_new_runs=1)
    assert len(v.per_run) == 1  # exactly ONE new run this invocation
    assert (tmp_path / "t" / "run-0").exists() and not (tmp_path / "t" / "run-1").exists()
    assert v.status == "INCONCLUSIVE"  # 1 completed < m=3 -> commander re-invokes


def test_sequential_one_run_resumes_accumulate_to_pass(tmp_path):
    # The reap-safe drive pattern: one run per invocation, resumed, accumulates to a
    # PASS across invocations — each invocation short-lived (issue #130).
    wt = throwaway_worktree(tmp_path)
    s = rse.load_scenario(make_scenario(tmp_path, process=(PASS_CHECK,)))
    tr = tmp_path / "t"
    rse.run_scenario(s, temp_root=tr, worktree=str(wt), launch=fake_pass_launch, max_new_runs=1)
    rse.run_scenario(s, temp_root=tr, launch=fake_pass_launch, resume=True, max_new_runs=1)
    v = rse.run_scenario(s, temp_root=tr, launch=fake_pass_launch, resume=True, max_new_runs=1)
    assert v.status == "PASS" and v.completed_count == 3
    assert (tr / "run-2").exists() and not (tr / "run-3").exists()


def test_final_meta_preserves_launch_liveness_fields(tmp_path):
    # issue #130: the finalized meta must RETAIN the liveness history the launcher
    # stamped (heartbeat_at, subject_pid, timeout_seconds) instead of dropping it —
    # a finalized run with no heartbeat looked (falsely) like the path never fired.
    wt = throwaway_worktree(tmp_path)
    tr = tmp_path / "t"; tr.mkdir()
    skills = rse.temp_install(str(wt), tr)
    cid = rse.write_stable_corpus_marker(skills, "abc")  # stable id (#153); see _run_once assert
    s = rse.load_scenario(make_scenario(tmp_path, process=(PASS_CHECK,)))

    def hb_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout):
        rd = Path(stdout_path).parent
        rse._stamp_meta_field(rd, subject_pid=4242)
        rse._stamp_meta_heartbeat(rd)
        return fake_pass_launch(argv, cwd=cwd, env=env, stdout_path=stdout_path,
                                stderr_path=stderr_path, timeout=timeout)

    rse._run_once(s, 0, tr, skills, cid, hb_launch)
    final = json.loads((tr / "run-0" / "meta.json").read_text(encoding="utf-8"))
    assert final["status"] == "completed-pass"
    assert "heartbeat_at" in final and final["subject_pid"] == 4242
    assert final["timeout_seconds"] == s.timeout_seconds


def test_launch_agent_records_subject_pid(tmp_path, monkeypatch):
    # The subject PID is recorded at spawn so an external reaper can tree-kill an
    # orphaned subject after a runner death (issue #130).
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: _BrieflyAlivePopen())
    monkeypatch.setattr(rse, "_HEARTBEAT_INTERVAL_SECONDS", 0.0)
    run_dir = tmp_path / "run-0"; run_dir.mkdir()
    (run_dir / "meta.json").write_text(
        json.dumps({"status": "launched", "launched_at": 1.0}), encoding="utf-8")
    rse.launch_agent(["dummy", "-p", "hi"], cwd=str(run_dir / "workspace"),
                     env=dict(os.environ), stdout_path=str(run_dir / "transcript.txt"),
                     stderr_path=str(run_dir / "stderr.txt"), timeout=10)
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["subject_pid"] == 555


def test_per_run_isolation_one_run_exception_does_not_sink_the_loop(tmp_path):
    # An unexpected fault in ONE run is fenced (errored) and the loop continues to
    # siblings, instead of the whole measurement dying (issue #130).
    wt = throwaway_worktree(tmp_path)
    s = rse.load_scenario(make_scenario(tmp_path, process=(PASS_CHECK,)))
    calls = {"n": 0}

    def flaky_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("simulated mid-run fault")
        return fake_pass_launch(argv, cwd=cwd, env=env, stdout_path=stdout_path,
                                stderr_path=stderr_path, timeout=timeout)

    v = rse.run_scenario(s, temp_root=tmp_path / "t", worktree=str(wt), launch=flaky_launch)
    assert (v.status, v.exit_code) == ("PASS", 0)
    statuses = [r.status for r in v.per_run]
    assert "errored" in statuses and statuses.count("completed-pass") >= 2
    # the errored run left a diagnosable terminal meta, not a bare "launched".
    errored_metas = [
        json.loads((tmp_path / "t" / f"run-{i}" / "meta.json").read_text(encoding="utf-8"))
        for i in range(len(statuses))
    ]
    assert any(m["status"] == "errored" for m in errored_metas)


# --------------------------------------------------------------------------- #
# issue #130 — REAL runner-process death (not hand-seeded): kill a live runner
# subprocess mid-measurement and prove the death left resumable/adjudicable state.
# --------------------------------------------------------------------------- #
def _write_hang_cmd(dir_path: Path) -> Path:
    """A `.cmd` shim whose subject sleeps 600s, so a runner that spawns it as its
    `--command` launcher blocks in launch_agent's poll loop (poll() stays None) until
    something kills it — the empirically-verified hang primitive for this Windows box.
    Popen(shell=False) spawns it; taskkill /T reaps the cmd.exe + `py` grandchild."""
    hang = dir_path / "hang.cmd"
    hang.write_text("@echo off\r\npy -c \"import time; time.sleep(600)\"\r\n", encoding="utf-8")
    return hang


def _confirm_hang_primitive(hang_cmd: Path) -> None:
    """Handoff stop-condition guard: independently re-confirm the `.cmd` subject
    spawns AND hangs under `Popen(shell=False)` here before relying on it. If it does
    not, fail loudly — do NOT silently switch to a POSIX mechanism. Self-contained
    try/finally so this probe can never leak its own process."""
    p = subprocess.Popen([str(hang_cmd)], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(0.5)
        assert p.poll() is None, (
            ".cmd hang subject did not stay alive under Popen(shell=False) — STOP "
            "(do not switch to a POSIX kill mechanism)")
    finally:
        rse._tree_kill(p)
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass


def _await_launched_runner(child_tmp: Path, proc: "subprocess.Popen", *, deadline_s: float):
    """Bounded poll: discover the runner's `--keep-temp` temp dir (created under the
    child-scoped TMP/TEMP as `constellation-eval-*`) and wait until its `run-0/meta.json`
    reaches `status=="launched"` with `subject_pid` stamped. The `kept temp dir:` stderr
    line is unusable for discovery here — the runner prints it only in a `finally` AFTER
    run_scenario returns, which never happens while the subject hangs (and not at all
    under a hard tree-kill) — so the temp dir is located via the redirected temp root.
    Raises a clear assertion (never hangs) if the subject fails to hang or the runner
    dies before reaching `launched`."""
    deadline = time.monotonic() + deadline_s
    temp_root = None
    while time.monotonic() < deadline:
        if temp_root is None:
            cands = sorted(child_tmp.glob("constellation-eval-*"))
            if cands:
                temp_root = cands[0]
        if temp_root is not None:
            meta_path = temp_root / "run-0" / "meta.json"
            if meta_path.is_file():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    meta = None  # half-written; retry
                if meta is not None:
                    status = meta.get("status")
                    if status == "launched" and "subject_pid" in meta:
                        return temp_root, meta
                    if status is not None and status != "launched":
                        raise AssertionError(
                            f".cmd subject did not hang: run-0 finalized to {status!r} "
                            f"(reason={meta.get('reason')!r}) — STOP per handoff")
        if proc.poll() is not None:
            raise AssertionError(
                f"runner exited early (rc={proc.returncode}) before run-0 reached 'launched'")
        time.sleep(0.2)
    raise AssertionError(
        "runner did not reach 'launched' with subject_pid within the bounded poll window")


def test_real_runner_process_death_leaves_resumable_state(tmp_path):
    # THE real-death regression bar (issue #130): launch an ACTUAL run_skill_eval.py
    # runner subprocess whose `--command` subject HANGS, tree-KILL the live runner
    # mid-measurement via the module's own Windows `_tree_kill` (taskkill /T /F), and
    # prove the real death left the resumable contract on disk — then that an
    # in-process `--resume` re-adopts the orphan to a verdict WITHOUT reinstalling.
    # Unlike test_resume_recovers_killed_runner_mid_measurement (which hand-seeds the
    # post-death disk state), this test actually kills a real runner process.
    wt = throwaway_worktree(tmp_path)                 # tiny corpus to install (fast)
    scen = make_scenario(tmp_path, process=(PASS_CHECK,))
    hang_cmd = _write_hang_cmd(tmp_path)

    # Re-confirm the hang primitive on this box before depending on it (handoff).
    _confirm_hang_primitive(hang_cmd)

    # Redirect the child's temp root to a known dir so `--keep-temp`'s mkdtemp lands
    # somewhere we can discover without the (unreachable-while-hung) stderr line.
    child_tmp = tmp_path / "child-tmp"
    child_tmp.mkdir()
    env = dict(os.environ)
    env["TMP"] = str(child_tmp)
    env["TEMP"] = str(child_tmp)

    argv = [sys.executable, str(RUN_SKILL_EVAL), str(scen),
            "--keep-temp", "--worktree", str(wt),
            "--command", str(hang_cmd), "--max-new-runs", "1"]
    out_f = (tmp_path / "runner.out.txt").open("wb")
    err_f = (tmp_path / "runner.err.txt").open("wb")
    # File-redirected stdio (no pipe reader threads, so nothing can hang on a
    # grandchild still holding a pipe write-handle).
    proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                            stdout=out_f, stderr=err_f, env=env)
    try:
        temp_root, meta = _await_launched_runner(child_tmp, proc, deadline_s=45)
        # Pre-kill sanity: the real runner really did spawn a live subject.
        assert meta["status"] == "launched"
        assert isinstance(meta.get("subject_pid"), int)
        # KILL the real runner tree via the module's OWN Windows tree-kill — the
        # production reaper (taskkill /PID <pid> /T /F), NOT a POSIX kill -9.
        rse._tree_kill(proc)
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass
    finally:
        # test-harness-concurrency-failsafe: ALWAYS reap the runner tree, so a failed
        # assertion or timeout above can never leave an orphaned runner/subject hanging
        # pytest. Idempotent — a second tree-kill of a dead pid is a harmless no-op.
        rse._tree_kill(proc)
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            pass
        out_f.close()
        err_f.close()

    # The REAL death left the resumable contract, unfinalized (never a silent hang):
    run0_meta = json.loads((temp_root / "run-0" / "meta.json").read_text(encoding="utf-8"))
    assert run0_meta["status"] == "launched"          # runner died BEFORE finalizing
    assert "subject_pid" in run0_meta                 # reaper target was recorded
    assert (temp_root / "skills" / rse.CORPUS_MARKER).is_file()   # corpus install survived

    # Seed the completion deliverable so the monotone process checks pass -> the orphan
    # adjudicates completed-pass on resume (run-0's workspace already exists from _run_once).
    (temp_root / "run-0" / "workspace").mkdir(parents=True, exist_ok=True)
    (temp_root / "run-0" / "workspace" / rse.COMPLETION_ARTIFACT).write_text(
        "seeded deliverable\n", encoding="utf-8")

    def _refuse_installer(worktree, tr):
        raise AssertionError("resume must NOT reinstall the corpus")

    s = rse.load_scenario(scen)
    v = rse.run_scenario(s, temp_root=temp_root, resume=True,
                         launch=fake_pass_launch, installer=_refuse_installer)
    # Resume re-adopted the real orphan and reached a verdict without reinstalling.
    assert v.status in ("PASS", "INCONCLUSIVE")
    adjudicated = json.loads((temp_root / "run-0" / "meta.json").read_text(encoding="utf-8"))
    assert adjudicated["status"] == "completed-pass"          # orphan finalized (no longer launched)
    assert adjudicated.get("adjudicated_orphan") is True
    assert v.completed_count >= 1
