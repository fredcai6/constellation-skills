"""Agent-free unit layer for scripts/run_skill_eval.py (#106, gate g2).

This suite launches NO real agent, ever. The one real subprocess seam
(`launch_agent`) is an inert stub until g3; every test here either injects a
fake launcher (`--dry-run`/`--dry-run-fail`) or exercises pure logic. An autouse
guard hard-fails if any test attempts to spawn a real `claude` subprocess, so the
agent-free guarantee is mechanically enforced rather than trusted.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
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
    whose basename starts with `claude` is not. Wraps the module-global
    `subprocess.run` that both `run_check` and the (stubbed) live seam would use."""
    real_run = subprocess.run

    def guarded_run(cmd, *args, **kwargs):
        argv0 = cmd[0] if isinstance(cmd, (list, tuple)) and cmd else cmd
        base = os.path.basename(str(argv0)).lower()
        assert not base.startswith("claude"), f"blocked real agent subprocess: {cmd!r}"
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)
    yield


# --------------------------------------------------------------------------- #
# helpers to fabricate canned run-dirs and scenarios (no agent)
# --------------------------------------------------------------------------- #
PASS_CHECK = (
    "import sys, pathlib\n"
    "run_dir = pathlib.Path(sys.argv[1])\n"
    "art = run_dir / 'workspace' / 'eval-complete.txt'\n"
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
        (ws / "eval-complete.txt").write_text("done\n", encoding="utf-8")
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
def test_build_eval_argv_with_model():
    assert rse.build_eval_argv("claude", prompt="do it", model="sonnet") == [
        "claude", "-p", "do it", "--model", "sonnet",
    ]


def test_build_eval_argv_without_model():
    assert rse.build_eval_argv("claude", prompt="do it", model=None) == ["claude", "-p", "do it"]


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
    assert (s.n, s.m, s.timeout_seconds) == (2, 3, 1800)
    assert s.model == rse.DEFAULT_MODEL
    assert s.fixture_dir is None


def test_load_scenario_toml_overrides(tmp_path):
    scen = make_scenario(
        tmp_path,
        toml='id = "euler-1"\nmodel = "haiku"\nn = 3\nm = 4\ntimeout_seconds = 900\n',
    )
    s = rse.load_scenario(scen)
    assert (s.id, s.model, s.n, s.m, s.timeout_seconds) == ("euler-1", "haiku", 3, 4, 900)


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


# --------------------------------------------------------------------------- #
# the agent-free guard STILL BITES on the live launch_agent (mechanical guarantee)
# --------------------------------------------------------------------------- #
def test_agent_free_guard_still_bites_on_launch_agent(tmp_path):
    # launch_agent is implemented on subprocess.run, which the autouse guard wraps;
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
