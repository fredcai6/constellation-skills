"""Tests for scripts/spine_lifecycle.py -- open Constellation work in one call.

Frozen contract: .agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md, sections 2
and 3. This gate ships `open_work` and the pure helpers only -- `close_work` tests
belong to g2.

House style (tests/test_mcp_adoption.py::_cli_only_verb_violations): every guard
gets a VIOLATING fixture that trips it and an INNOCENT fixture that does not, so a
green suite measures the boundary, not just the happy path. Every test that touches
git builds its own throwaway repo under `tmp_path` -- this worktree's own real git
state is read only by `TestWorktreePathForRealWorktree`, and never written.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import checklist_engine  # noqa: E402
import run_crew  # noqa: E402
import spine_lifecycle as sl  # noqa: E402
import validate_spine  # noqa: E402
import verify_worktree_isolation as vwi  # noqa: E402

HAS_GIT = shutil.which("git") is not None
requires_git = pytest.mark.skipif(not HAS_GIT, reason="git not available")


# --------------------------------------------------------------------------- #
# fixture builders
# --------------------------------------------------------------------------- #

def _artifact_cond(id_="c1", evidence_type="user-decision"):
    return {"id": id_, "statement": "human decided", "kind": "artifact", "evidence_type": evidence_type}


def _qual_cond(id_="c1"):
    return {"id": id_, "statement": "reviewer read the diff", "kind": "qualitative",
            "because": "no automatable signal exists"}


def _spec(work_id, *, gate_id="m1", postconditions=None):
    """A minimal spec that compiles clean: not all-qualitative, zero probes
    needed (artifact/qualitative carry no probe), no config_ref to chase."""
    return {
        "work_id": work_id,
        "type": "gated",
        "gate": [{
            "id": gate_id,
            "title": "do it",
            "imperative": "do the thing",
            "postconditions": postconditions if postconditions is not None else [_artifact_cond()],
        }],
    }


def _all_qualitative_spec(work_id, *, gate_id="m1"):
    """Deliberately invalid past spec-shape: this is the fixture used to force
    a LATE failure (step 6, inside _compile_spine) without monkeypatching --
    `git worktree add` and work-area scaffolding both succeed first."""
    return {
        "work_id": work_id,
        "type": "gated",
        "gate": [{
            "id": gate_id, "title": "do it", "imperative": "do the thing",
            "postconditions": [_qual_cond("c1"), _qual_cond("c2")],
        }],
    }


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.email=t@t", "-c", "user.name=t",
         "commit", "-q", "--allow-empty", "-m", "init"],
        check=True, capture_output=True,
    )


def _porcelain(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "worktree", "list", "--porcelain"],
        check=True, capture_output=True, text=True,
    ).stdout


def _branches(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "branch", "--list"],
        check=True, capture_output=True, text=True,
    ).stdout


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _init_repo(r)
    return r


@pytest.fixture
def wt_root(tmp_path):
    return str(tmp_path / "wt")


# --------------------------------------------------------------------------- #
# pure helpers -- tested directly, today/wt_root passed in
# --------------------------------------------------------------------------- #

class TestWorktreePathFor:
    def test_nested_work_id_uses_last_segment(self):
        assert sl.worktree_path_for("epic-559/c3-lifecycle", wt_root="/x/wt") == "/x/wt/c3-lifecycle"

    def test_single_segment_work_id(self):
        assert sl.worktree_path_for("issue-310", wt_root="/x/wt") == "/x/wt/issue-310"

    def test_pure_no_filesystem_symbols(self):
        import inspect
        src = inspect.getsource(sl.worktree_path_for)
        for banned in ("open(", "subprocess.", "Path("):
            assert banned not in src


@requires_git
class TestWorktreePathForRealWorktree:
    def test_reproduces_this_runs_real_worktree(self):
        # The ONE test allowed to read this worktree's own real git state --
        # confirms the default wt_root convention against the live tree
        # rather than a hardcoded path, so it stays true on any host.
        primary = Path(vwi.primary_checkout())
        default_wt_root = sl._default_wt_root(primary)
        got = sl.worktree_path_for("epic-559/c3-lifecycle", wt_root=default_wt_root)
        assert Path(got).resolve() == ROOT.resolve()


class TestBranchNameFor:
    def test_verbatim(self):
        assert sl.branch_name_for("epic-559/c3-lifecycle") == "epic-559/c3-lifecycle"


class TestArchiveNameFor:
    def test_format(self):
        assert sl.archive_name_for("epic-559/c3-lifecycle", today="2026-08-12") == "2026-08-12-epic-559-c3-lifecycle"

    def test_today_is_never_read_inside(self):
        import inspect
        src = inspect.getsource(sl.archive_name_for)
        assert "date.today" not in src and "datetime.now" not in src


class TestBuildOrigin:
    def test_shape(self):
        origin = sl.build_origin(
            "w1", branch="w1", worktree="/x/w1", base="deadbeef",
            opened_at="2026-01-01T00:00:00+00:00", parent="unknown",
        )
        assert origin == {
            "work_id": "w1",
            "branch": "w1",
            "worktree": "/x/w1",
            "base": "deadbeef",
            "opened_at": "2026-01-01T00:00:00+00:00",
            "opened_by": "spine_open",
            "parent": "unknown",
        }


# --------------------------------------------------------------------------- #
# _active_engine_session_spine -- the step-3 guard, tested directly and
# defensively (agent_work_root._active_epic_lease's own style)
# --------------------------------------------------------------------------- #

class TestActiveEngineSessionScan:
    def test_violating_active_status_is_found(self, tmp_path):
        spine_dir = tmp_path / ".agent-work" / "w1"
        spine_dir.mkdir(parents=True)
        (spine_dir / "spine.json").write_text(json.dumps({"engine_session": {"status": "active"}}))
        found = sl._active_engine_session_spine(tmp_path, "w1")
        assert found == spine_dir / "spine.json"

    def test_innocent_released_status_is_not_found(self, tmp_path):
        spine_dir = tmp_path / ".agent-work" / "w1"
        spine_dir.mkdir(parents=True)
        (spine_dir / "spine.json").write_text(json.dumps({"engine_session": {"status": "released"}}))
        assert sl._active_engine_session_spine(tmp_path, "w1") is None

    def test_violating_finds_a_differently_named_spine(self, tmp_path):
        # This epic's own driving spine is execute.json, not spine.json --
        # the scan is structural (looks for the field), never filename-based.
        spine_dir = tmp_path / ".agent-work" / "w1"
        spine_dir.mkdir(parents=True)
        (spine_dir / "execute.json").write_text(json.dumps({"engine_session": {"status": "active"}}))
        assert sl._active_engine_session_spine(tmp_path, "w1") is not None

    def test_missing_work_dir_is_none_not_raise(self, tmp_path):
        assert sl._active_engine_session_spine(tmp_path, "does-not-exist") is None

    def test_garbage_json_is_skipped_not_raised(self, tmp_path):
        spine_dir = tmp_path / ".agent-work" / "w1"
        spine_dir.mkdir(parents=True)
        (spine_dir / "spine.json").write_text("{not valid json")
        assert sl._active_engine_session_spine(tmp_path, "w1") is None

    def test_list_shaped_file_is_skipped_not_raised(self, tmp_path):
        # crew-runs.json is a JSON LIST, not a dict -- must not crash the scan.
        spine_dir = tmp_path / ".agent-work" / "w1"
        spine_dir.mkdir(parents=True)
        (spine_dir / "crew-runs.json").write_text(json.dumps([{"status": "running"}]))
        assert sl._active_engine_session_spine(tmp_path, "w1") is None

    def test_non_dict_engine_session_is_skipped(self, tmp_path):
        spine_dir = tmp_path / ".agent-work" / "w1"
        spine_dir.mkdir(parents=True)
        (spine_dir / "spine.json").write_text(json.dumps({"engine_session": "active"}))
        assert sl._active_engine_session_spine(tmp_path, "w1") is None


# --------------------------------------------------------------------------- #
# open_work -- work-id validation (reuses run_crew.validate_work_id)
# --------------------------------------------------------------------------- #

@requires_git
class TestOpenWorkValidatesWorkId:
    def test_violating_unsafe_work_id_refused_by_name(self, repo, wt_root):
        with pytest.raises(sl.SpineLifecycleError) as excinfo:
            sl.open_work("../escape", _spec("../escape"), root=repo, base="HEAD",
                          parent="unknown", wt_root=wt_root)
        assert "unsafe segment" in str(excinfo.value)
        # Nothing was touched -- refused before git ever ran.
        assert _porcelain(repo).count("worktree ") == 1


# --------------------------------------------------------------------------- #
# open_work -- occupied worktree path refusal (step 2)
# --------------------------------------------------------------------------- #

@requires_git
class TestOpenWorkOccupiedRefusal:
    def test_violating_refuses_when_worktree_path_exists(self, repo, wt_root):
        occupied = Path(wt_root) / "w1"
        occupied.mkdir(parents=True)
        with pytest.raises(sl.SpineLifecycleError) as excinfo:
            sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="unknown", wt_root=wt_root)
        assert str(occupied) in str(excinfo.value)
        assert _porcelain(repo).count("worktree ") == 1  # no worktree was registered

    def test_innocent_free_path_succeeds(self, repo, wt_root):
        result = sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="unknown", wt_root=wt_root)
        assert Path(result["worktree"]).is_dir()


# --------------------------------------------------------------------------- #
# open_work -- active engine-session refusal (step 3)
# --------------------------------------------------------------------------- #

@requires_git
class TestOpenWorkActiveSessionRefusal:
    def test_violating_refuses_when_engine_session_active(self, repo, wt_root):
        spine_dir = repo / ".agent-work" / "w1"
        spine_dir.mkdir(parents=True)
        (spine_dir / "spine.json").write_text(json.dumps({"engine_session": {"status": "active"}}))

        with pytest.raises(sl.SpineLifecycleError) as excinfo:
            sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="unknown", wt_root=wt_root)
        assert "w1" in str(excinfo.value)
        assert _porcelain(repo).count("worktree ") == 1  # never even attempted worktree add

    def test_innocent_only_spine_is_released_succeeds(self, repo, wt_root):
        spine_dir = repo / ".agent-work" / "w1"
        spine_dir.mkdir(parents=True)
        (spine_dir / "spine.json").write_text(json.dumps({"engine_session": {"status": "released"}}))

        result = sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="unknown", wt_root=wt_root)
        assert Path(result["worktree"]).is_dir()


# --------------------------------------------------------------------------- #
# open_work -- rollback: a late failure leaves NO worktree and NO branch
# --------------------------------------------------------------------------- #

@requires_git
class TestOpenWorkRollback:
    def test_violating_late_failure_at_compile_leaves_no_worktree_or_branch(self, repo, wt_root):
        before = _porcelain(repo)
        before_branches = _branches(repo)

        with pytest.raises(sl.SpineLifecycleError):
            sl.open_work("w1", _all_qualitative_spec("w1"), root=repo, base="HEAD",
                         parent="unknown", wt_root=wt_root)

        after = _porcelain(repo)
        after_branches = _branches(repo)
        assert after == before, f"a worktree survived a late failure:\nbefore:\n{before}\nafter:\n{after}"
        assert after_branches == before_branches, (
            f"a branch survived a late failure:\nbefore:\n{before_branches}\nafter:\n{after_branches}"
        )
        assert not Path(wt_root, "w1").exists()

    def test_violating_late_failure_after_origin_injection_leaves_no_worktree_or_branch(
        self, repo, wt_root, monkeypatch
    ):
        # Forces the failure specifically at step 7 (the RE-validate after
        # origin injection), not step 6: real validate() runs clean the first
        # time (inside _compile_spine) and only fails on the second call.
        before = _porcelain(repo)
        before_branches = _branches(repo)

        real_validate = validate_spine.validate
        calls = {"n": 0}

        def flaky_validate(spine, *, repo_root=None):
            calls["n"] += 1
            if calls["n"] >= 2:
                raise RuntimeError("forced failure on the post-origin re-validate")
            return real_validate(spine, repo_root=repo_root)

        monkeypatch.setattr(sl.validate_spine, "validate", flaky_validate)

        with pytest.raises(RuntimeError):
            sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="unknown", wt_root=wt_root)

        assert calls["n"] >= 2
        after = _porcelain(repo)
        after_branches = _branches(repo)
        assert after == before, f"a worktree survived a late failure:\nbefore:\n{before}\nafter:\n{after}"
        assert after_branches == before_branches
        assert not Path(wt_root, "w1").exists()

    def test_innocent_rollback_is_scoped_to_this_calls_own_worktree(self, repo, wt_root):
        # A pre-existing UNRELATED worktree survives a failed open of a
        # DIFFERENT work id.
        survivor = sl.open_work("survivor", _spec("survivor"), root=repo, base="HEAD",
                                 parent="unknown", wt_root=wt_root)
        assert Path(survivor["worktree"]).is_dir()

        with pytest.raises(sl.SpineLifecycleError):
            sl.open_work("w1", _all_qualitative_spec("w1"), root=repo, base="HEAD",
                         parent="unknown", wt_root=wt_root)

        # The survivor is untouched: still on disk, still registered, its
        # branch still present.
        assert Path(survivor["worktree"]).is_dir()
        porcelain = _porcelain(repo)
        assert survivor["worktree"] in porcelain
        assert "survivor" in _branches(repo)
        assert not Path(wt_root, "w1").exists()


# --------------------------------------------------------------------------- #
# open_work -- check_distinct_real says no despite `git worktree add` exit 0
# (required evidence #2, load-bearing)
# --------------------------------------------------------------------------- #

@requires_git
class TestOpenWorkSelfVerifyForcesRollback:
    def test_violating_check_distinct_real_says_no_forces_rollback(self, repo, wt_root, monkeypatch):
        before = _porcelain(repo)
        before_branches = _branches(repo)

        # `git worktree add` runs for real and exits 0 -- only the in-process
        # self-verify is faked to say no, proving the code does not trust
        # git's own exit code as evidence.
        monkeypatch.setattr(
            sl.verify_worktree_isolation, "check_distinct_real",
            lambda *a, **kw: (False, "faked: git exit 0 is not evidence"),
        )

        with pytest.raises(sl.SpineLifecycleError) as excinfo:
            sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="unknown", wt_root=wt_root)
        assert "not evidence" in str(excinfo.value) or "self-verify" in str(excinfo.value)

        after = _porcelain(repo)
        after_branches = _branches(repo)
        assert after == before, f"a worktree survived a failed self-verify:\nbefore:\n{before}\nafter:\n{after}"
        assert after_branches == before_branches
        assert not Path(wt_root, "w1").exists()


# --------------------------------------------------------------------------- #
# open_work -- happy path shape, and the origin block itself
# --------------------------------------------------------------------------- #

@requires_git
class TestOpenWorkHappyPath:
    def test_returns_crew_binding_values(self, repo, wt_root):
        result = sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="constellation/parent/g0/commander/attempt-1",
                              wt_root=wt_root)
        assert set(result) == {"SPINE_FILE", "SPINE_SESSION", "SPINE_PARENT", "branch", "worktree"}
        assert result["branch"] == "w1"
        assert Path(result["worktree"]) == Path(wt_root) / "w1"
        assert Path(result["SPINE_FILE"]).is_file()
        assert result["SPINE_PARENT"] == "constellation/parent/g0/commander/attempt-1"

    def test_origin_block_is_written_and_valid(self, repo, wt_root):
        result = sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="unknown", wt_root=wt_root)
        compiled = json.loads(Path(result["SPINE_FILE"]).read_text())
        origin = compiled["origin"]
        assert origin["work_id"] == "w1"
        assert origin["branch"] == "w1"
        assert origin["worktree"] == result["worktree"]
        assert origin["opened_by"] == "spine_open"
        assert origin["parent"] == "unknown"
        # base was resolved to a real commit sha, not left as the "HEAD" ref string.
        assert origin["base"] != "HEAD"
        assert len(origin["base"]) == 40

        # And the written spine is genuinely valid -- validate_spine has no complaints.
        result_validation = validate_spine.validate(compiled, repo_root=Path(result["worktree"]))
        assert not result_validation
        assert not result_validation.undecidable


# --------------------------------------------------------------------------- #
# origin round-trip through a REAL engine drive (required evidence #3,
# load-bearing): claim -> start -> attest -> advance, byte-identical origin.
# --------------------------------------------------------------------------- #

@requires_git
class TestOriginRoundTrip:
    def test_origin_survives_claim_start_attest_advance(self, repo, wt_root):
        spec = _spec("w1", postconditions=[_qual_cond("c1"), _artifact_cond("c2")])
        result = sl.open_work("w1", spec, root=repo, base="HEAD", parent="unknown", wt_root=wt_root)

        spine_path = Path(result["SPINE_FILE"])
        cl = json.loads(spine_path.read_text())
        origin_before = json.loads(json.dumps(cl["origin"]))  # deep copy

        config = checklist_engine.load_config(cl, None)
        checklist_engine.claim(cl, "test-session", "test", result["worktree"], config)
        checklist_engine.start(cl, "m1")
        checklist_engine.attest(cl, "m1", "c1", "postconditions", "verified by hand")
        checklist_engine.attach(cl, "m1", "user-decision", {"decision": "go"})
        evidence_id = cl["tasks"]["m1"]["evidence"][0]["id"]
        checklist_engine.attest(cl, "m1", "c2", "postconditions", "human decided", evidence_id=evidence_id)
        checklist_engine.advance(cl, "m1", mechanical=True)

        assert cl["tasks"]["m1"]["status"] == "complete"
        assert cl["origin"] == origin_before, (
            f"origin mutated by the engine drive:\nbefore: {origin_before}\nafter: {cl['origin']}"
        )


# --------------------------------------------------------------------------- #
# work-id validator reuse -- never a second implementation
# --------------------------------------------------------------------------- #

class TestReusesRunCrewValidator:
    def test_open_work_uses_run_crew_validate_work_id(self):
        import inspect
        src = inspect.getsource(sl.open_work)
        assert "run_crew.validate_work_id" in src
