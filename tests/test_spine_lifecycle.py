"""Tests for scripts/spine_lifecycle.py -- open and close Constellation work in one
call each.

Frozen contract: .agent-work/archive/2026-08-12-epic-559-c3-lifecycle/LIFECYCLE_CONTRACT.md,
sections 2-4 (archived alongside the rest of that work area at closeout). `open_work`
and its pure helpers are g1's; `closeout_refusal` and `close_work` are g2's.

House style (tests/test_mcp_adoption.py::_cli_only_verb_violations): every guard
gets a VIOLATING fixture that trips it and an INNOCENT fixture that does not, so a
green suite measures the boundary, not just the happy path. Every test that touches
git builds its own throwaway repo under `tmp_path` -- this worktree's own real git
state is read only by `TestWorktreePathForRealWorktree`, and never written.
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
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
    """A throwaway git repo, self-sufficient for every commit it will ever be
    asked to make -- not just the one this function makes itself.

    `user.name`/`user.email` are set REPO-LOCAL (`git config`, persisted in
    `.git/config`), not just passed via `-c` on this function's own init
    commit: a fixture that only configures identity for its OWN commit still
    fails the moment code under test (e.g. `close_work`'s internal `git
    commit`) makes a SECOND commit with no `-c` override of its own, because
    nothing here follows it. This surfaced on Windows CI, where the runner
    carries no ambient git identity at all (`Author identity unknown`) --
    Linux runs never caught it because SOME ambient identity happened to be
    configured there. A test that only passes where someone happened to
    configure git is a test that cannot fail for the right reason; this repo
    is self-sufficient regardless of the runner's own git config."""
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "t@t"], check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "t"], check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "commit", "-q", "--allow-empty", "-m", "init"],
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
        assert sl.worktree_path_for("epic-100/sample-slug", wt_root="/x/wt") == "/x/wt/sample-slug"

    def test_single_segment_work_id(self):
        assert sl.worktree_path_for("issue-310", wt_root="/x/wt") == "/x/wt/issue-310"

    def test_pure_no_filesystem_symbols(self):
        import inspect
        src = inspect.getsource(sl.worktree_path_for)
        for banned in ("open(", "subprocess.", "Path("):
            assert banned not in src


class TestDefaultWtRoot:
    def test_resolves_to_dot_worktrees_under_root(self):
        root = Path("/x")
        assert sl._default_wt_root(root) == str(root / ".worktrees")


@requires_git
class TestWorktreePathForRealWorktree:
    def test_reproduces_this_runs_real_worktree(self):
        # The ONE test allowed to read this worktree's own real git state --
        # confirms the default wt_root convention against the live tree.
        # The work id's last segment is DERIVED from this checkout's own
        # directory name rather than naming one (`worktree_path_for` only
        # ever looks at that last segment), so this holds from any worktree
        # created under the convention, not just one specific archived
        # worktree -- a hardcoded work id passes only from that one checkout
        # and starts failing everywhere else the moment it is archived away.
        #
        # Applies only inside a worktree directly under <primary>-wt/: skips,
        # and says why, from the primary checkout or a scratch worktree
        # created elsewhere (e.g. a detached review checkout). It runs and
        # passes from a worktree following the convention -- this repo's own
        # <primary>-wt/<slug> checkout is one such worktree.
        primary = Path(vwi.primary_checkout())
        default_wt_root = sl._default_wt_root(primary)
        if ROOT.parent.resolve() != Path(default_wt_root).resolve():
            pytest.skip(
                f"this checkout ({ROOT}) is not directly inside {default_wt_root}; "
                "only applies to a worktree following the <wt_root>/<work-slug> convention"
            )
        got = sl.worktree_path_for(ROOT.name, wt_root=default_wt_root)
        assert Path(got).resolve() == ROOT.resolve()


@requires_git
class TestDefaultLayoutAgainstAConstructedTopology:
    """#598 (closeout reconcile tc5) — the SAME composition as the class above,
    against a topology this test builds, so it runs where anyone actually
    measures.

    `TestWorktreePathForRealWorktree` reads the ambient checkout, and its skip is
    correct in itself: a hardcoded work id passes only from one checkout. The
    consequence was not. The suite normally runs from the PRIMARY checkout, so
    that test skipped in every routine run and `_default_wt_root` composed with
    `worktree_path_for` was exercised by nothing — while worktree location became
    load-bearing engine identity (`origin.worktree` is immutable once stamped,
    #577), was given a single owner (#585), and then had to be repaired when the
    nesting it introduced weakened `origin_worktree_refusal` (#588). The one test
    that would catch a regression in how that path is computed did not run where
    anyone was looking.

    Building the topology instead of finding it removes the skip: this is the
    pattern `tests/test_worktree_precondition_wiring.py::IsolationGateSurvivesThroughTheCLI`
    established for the same reason.
    """

    def _worktree_at(self, primary: Path, slug: str) -> Path:
        """Create the worktree at the LITERAL documented layout,
        `<primary>/.worktrees/<slug>`.

        Deliberately not `sl._default_wt_root(primary) / slug`: computing the
        expected path with the function under test moves both sides of the
        assertion together and passes for any implementation whatsoever. That is
        the tautology #315 was blocked on and PR #576 landed a guard against, and
        the first draft of this class reproduced it -- a regression to the old
        sibling layout was caught by only one of the two tests here until this
        helper stopped asking the code where it thought the worktree went.
        """
        target = primary / ".worktrees" / slug
        subprocess.run(
            ["git", "-C", str(primary), "worktree", "add", "-q",
             str(target), "-b", slug],
            check=True, capture_output=True,
        )
        return target

    def test_the_default_layout_names_where_git_actually_puts_a_worktree(self, tmp_path):
        """The composition under test is `_default_wt_root` -> `worktree_path_for`.
        Its answer must be the path a real `git worktree add` produced, not a
        string that merely looks right."""
        primary = tmp_path / "proj"
        _init_repo(primary)
        created = self._worktree_at(primary, "issue-999")

        got = sl.worktree_path_for("issue-999", wt_root=sl._default_wt_root(primary))

        assert Path(got).resolve() == created.resolve()
        # And git agrees it is a real linked worktree, not just a directory.
        assert str(created.resolve()) in _porcelain(primary).replace("\\", "/") or \
            str(created) in _porcelain(primary)

    def test_a_nested_work_id_lands_beside_its_siblings(self, tmp_path):
        """`worktree_path_for` takes only the last segment, so an epic-scoped
        work id must not nest a directory per segment under `.worktrees/`. That
        is the shape that produced the stray `constellation-skills-wt/s` and `/t`
        directories a path-construction bug left on disk (#586)."""
        primary = tmp_path / "proj"
        _init_repo(primary)
        created = self._worktree_at(primary, "issue-1000")

        got = sl.worktree_path_for("epic-568/issue-1000",
                                   wt_root=sl._default_wt_root(primary))

        assert Path(got).resolve() == created.resolve()
        assert Path(got).parent.name == ".worktrees"


class TestBranchNameFor:
    def test_verbatim(self):
        assert sl.branch_name_for("epic-100/sample-slug") == "epic-100/sample-slug"


class TestArchiveNameFor:
    def test_format(self):
        assert sl.archive_name_for("epic-100/sample-slug", today="2026-08-12") == "2026-08-12-epic-100-sample-slug"

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
# spine.json is written with newline="\n" -- CREW_CONTEXT.md's "every write"
# rule. Byte-level (Path.read_bytes()) because a text-mode read translates
# CRLF back to LF on read, which would pass on Windows regardless.
# --------------------------------------------------------------------------- #

@requires_git
class TestSpineFileHasNoCRLF:
    def test_written_spine_bytes_contain_no_crlf(self, repo, wt_root):
        result = sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="unknown", wt_root=wt_root)
        raw = Path(result["SPINE_FILE"]).read_bytes()
        assert b"\r\n" not in raw


# --------------------------------------------------------------------------- #
# Every write_text call in the module pins newline="\n" explicitly. AST-based
# (house style: tests/test_mcp_adoption.py::_cli_only_verb_violations) because
# TestSpineFileHasNoCRLF above cannot go red on Linux: os.linesep here is "\n",
# so write_text() with no newline= argument produces identical bytes to
# write_text() with newline="\n" -- the CRLF-producing bug is real only on
# Windows and invisible to any byte comparison run on this host. This check
# instead reads the source and can fail on any host, including this one.
# --------------------------------------------------------------------------- #

def _missing_newline_write_text_calls(source: str, where: str) -> list[str]:
    """Every `.write_text(...)` call in `source` lacking an explicit
    `newline=` keyword argument, as `where:lineno` strings."""
    tree = ast.parse(source, filename=where)
    violations = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "write_text"
            and not any(kw.arg == "newline" for kw in node.keywords)
        ):
            violations.append(f"{where}:{node.lineno}")
    return violations


class TestEveryWriteTextPinsNewline:
    SOURCE = (ROOT / "scripts" / "spine_lifecycle.py").read_text(encoding="utf-8")

    def test_the_shipped_module_has_no_violations(self):
        assert _missing_newline_write_text_calls(self.SOURCE, "scripts/spine_lifecycle.py") == []

    def test_violating_a_mutated_copy_missing_newline_is_caught(self):
        # Positive control: proves the predicate can fail, per the mutated-copy
        # convention `_cli_only_verb_violations` establishes. Strips exactly the
        # keyword this check exists to require -- not a stand-in for a different
        # mutation.
        mutated = self.SOURCE.replace(', newline="\\n")', ")")
        assert mutated != self.SOURCE, "the mutation did not change the source -- fixture is stale"
        violations = _missing_newline_write_text_calls(mutated, "<mutated>")
        assert violations, "the predicate did not catch a write_text call with newline= stripped"

    def test_innocent_a_write_text_call_with_newline_present_is_not_flagged(self):
        innocent = "p.write_text(data, encoding='utf-8', newline='\\n')"
        assert _missing_newline_write_text_calls(innocent, "<innocent>") == []


# --------------------------------------------------------------------------- #
# work-id validator reuse -- never a second implementation
# --------------------------------------------------------------------------- #

class TestReusesRunCrewValidator:
    def test_open_work_uses_run_crew_validate_work_id(self):
        import inspect
        src = inspect.getsource(sl.open_work)
        assert "run_crew.validate_work_id" in src


# =============================================================================
# g2 -- closeout_refusal (pure) and close_work (impure)
# LIFECYCLE_CONTRACT.md section 4.
# =============================================================================

def _terminal_spine(**overrides):
    """A minimal genuinely-terminal, released, gated spine dict -- the
    baseline every closeout_refusal/close_work fixture below starts from and
    overrides one field of at a time."""
    spine = {
        "type": "gated",
        "items": ["m1"],
        "tasks": {"m1": {"status": "complete"}},
        "engine_session": {"status": "released", "session_id": "s1"},
    }
    spine.update(overrides)
    return spine


def _make_work_area(
    repo: Path, work_id: str, spine_name: str, spine: dict, *, ignored_file: str | None = None,
) -> dict:
    """Scaffold `.agent-work/<work_id>/` under `repo` with a spine file named
    `spine_name` plus the usual init_work_area.py subdirectories -- one
    (`crew-handoffs/`) holding a real file, the other two (`evidence/`,
    `triage-candidates/`) left genuinely empty, so every close_work test
    exercises BOTH the tracked/untracked-file path and the empty-directory
    path through `_stage_and_move` at once. Nothing here is `git add`ed or
    committed -- a freshly scaffolded work area routinely isn't either.

    `ignored_file`, when given, adds a top-level entry gitignored via a
    `.gitignore` COMMITTED at the repo root (never left dangling, so it does
    not itself show up as an untracked file in a later `git status`) --
    reproducing the MCP door's `mcp_calls.jsonl` / `mcp_server_started`,
    which a real work area always carries beside the spine."""
    work_dir = repo / ".agent-work" / work_id
    for sub in ("crew-handoffs", "evidence", "triage-candidates"):
        (work_dir / sub).mkdir(parents=True, exist_ok=True)
    (work_dir / "crew-handoffs" / "note.md").write_text("hello\n", encoding="utf-8", newline="\n")
    spine_path = work_dir / spine_name
    spine_path.write_text(json.dumps(spine), encoding="utf-8", newline="\n")
    if ignored_file is not None:
        (repo / ".gitignore").write_text(f"{ignored_file}\n", encoding="utf-8", newline="\n")
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t",
             "add", ".gitignore"], check=True, capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "-q", "-m", "add .gitignore"], check=True, capture_output=True,
        )
        (work_dir / ignored_file).write_text("ignored content\n", encoding="utf-8", newline="\n")
    return {"work_dir": work_dir, "spine_path": spine_path}


def _snapshot(root: Path) -> dict:
    """relpath -> bytes for every FILE under `root`, for a byte-for-byte
    before/after comparison. Silently empty (not raising) when `root` does
    not exist -- the natural "nothing there" reading for a refusal that
    never created anything."""
    if not root.exists():
        return {}
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


# --------------------------------------------------------------------------- #
# closeout_refusal -- pure. Every guard gets a VIOLATING and an INNOCENT case
# (house style, tests/test_mcp_adoption.py::_cli_only_verb_violations).
# --------------------------------------------------------------------------- #

class TestCloseoutRefusal:
    def test_violating_lease_still_active_names_it(self):
        spine = _terminal_spine(engine_session={"status": "active", "session_id": "s1"})
        msg = sl.closeout_refusal(spine, archive_exists=False)
        assert msg is not None
        assert "the lease is still active" in msg

    def test_violating_non_terminal_gate_names_the_offending_gate(self):
        spine = _terminal_spine(
            items=["m1", "m2"],
            tasks={"m1": {"status": "complete"}, "m2": {"status": "in-progress"}},
        )
        msg = sl.closeout_refusal(spine, archive_exists=False)
        assert msg is not None
        assert "m2" in msg
        assert "m1" not in msg  # only the OFFENDING gate is named, not the terminal one

    def test_violating_archive_already_exists(self):
        msg = sl.closeout_refusal(_terminal_spine(), archive_exists=True)
        assert msg is not None
        assert "archive" in msg

    def test_innocent_terminal_and_released_proceeds(self):
        assert sl.closeout_refusal(_terminal_spine(), archive_exists=False) is None

    def test_innocent_skipped_status_is_terminal_too(self):
        spine = _terminal_spine(tasks={"m1": {"status": "skipped"}})
        assert sl.closeout_refusal(spine, archive_exists=False) is None

    def test_checks_run_in_order_lease_before_terminality(self):
        # An active lease is named even when a gate is ALSO non-terminal --
        # proves the lease check runs first, per the contract's stated order.
        spine = _terminal_spine(
            engine_session={"status": "active", "session_id": "s1"},
            tasks={"m1": {"status": "in-progress"}},
        )
        msg = sl.closeout_refusal(spine, archive_exists=False)
        assert "the lease is still active" in msg

    def test_pure_no_filesystem_symbols(self):
        import inspect
        src = inspect.getsource(sl.closeout_refusal)
        for banned in ("open(", "subprocess.", "Path("):
            assert banned not in src


# --------------------------------------------------------------------------- #
# closeout_refusal agrees with run_crew.spine_terminal -- differential test
# (required evidence: criterion 9). `spine_terminal` takes a PATH and reads
# the file; closeout_refusal takes the already-parsed dict. Both are run
# against the SAME spine content, held terminal-or-not constant while lease
# and archive are held fixed, so the comparison isolates the terminality
# verdict alone.
# --------------------------------------------------------------------------- #

class TestCloseoutRefusalAgreesWithSpineTerminal:
    def _write(self, tmp_path, spine):
        path = tmp_path / "spine.json"
        path.write_text(json.dumps(spine), encoding="utf-8", newline="\n")
        return path

    def test_agrees_on_a_terminal_case(self, tmp_path):
        spine = _terminal_spine()
        path = self._write(tmp_path, spine)
        pure_says_terminal = sl.closeout_refusal(spine, archive_exists=False) is None
        real_says_terminal = run_crew.spine_terminal(path, tmp_path)
        assert pure_says_terminal is True
        assert real_says_terminal is True

    def test_agrees_on_a_non_terminal_case(self, tmp_path):
        spine = _terminal_spine(tasks={"m1": {"status": "in-progress"}})
        path = self._write(tmp_path, spine)
        pure_says_terminal = sl.closeout_refusal(spine, archive_exists=False) is None
        real_says_terminal = run_crew.spine_terminal(path, tmp_path)
        assert pure_says_terminal is False
        assert real_says_terminal is False


# --------------------------------------------------------------------------- #
# spine_terminal resolves THROUGH a real close_work relocation
# (launcher-hygiene Task 2): `close_work` moves the entire work area, spine
# included, into `.agent-work/archive/<date>-<work_id>/`. A dispatcher that
# recorded the spine's ORIGINAL path (every crew-runs.json entry does) reads
# a plain file-not-found at that path afterward, and `run_crew.spine_terminal`
# used to read that as "never terminal" -- inverting a genuinely successful
# spine-only dispatch into `failed`. These tests compose the REAL close_work
# move with the REAL spine_terminal read (no mock of either), because the bug
# lives in how the two behaviors compose.
# --------------------------------------------------------------------------- #

@requires_git
class TestSpineTerminalThroughArchiveRelocation:
    def test_terminal_spine_relocated_by_a_real_close_work_still_reads_terminal(self, repo):
        spine = _terminal_spine()
        area = _make_work_area(repo, "w1", "spine.json", spine)
        original_rel = area["spine_path"].relative_to(repo)

        sl.close_work(area["spine_path"], root=repo, today="2026-08-12")

        assert not (repo / original_rel).exists()  # genuinely gone from where it was dispatched
        assert run_crew.spine_terminal(original_rel, repo) is True

    def test_non_terminal_spine_never_archived_still_reads_not_terminal(self, repo):
        # Nothing to relocate through: a genuinely incomplete run's spine
        # simply is not there, at the original path or in any archive dir --
        # this must NOT become a rubber stamp for a crew that is not done.
        spine = _terminal_spine(tasks={"m1": {"status": "in-progress"}})
        area = _make_work_area(repo, "w1", "spine.json", spine)
        original_rel = area["spine_path"].relative_to(repo)

        assert run_crew.spine_terminal(original_rel, repo) is False

    def test_archive_dir_for_a_prefix_colliding_work_id_is_never_matched(self, repo):
        # An archive dir exists for "w10" -- a work id that CONTAINS "w1" as
        # a prefix. The relocation lookup must match the work id exactly,
        # never as a substring/prefix, or archiving w10 would let w1's own
        # (never-archived, never-created) spine read back as terminal.
        spine_w10 = _terminal_spine()
        area_w10 = _make_work_area(repo, "w10", "spine.json", spine_w10)
        sl.close_work(area_w10["spine_path"], root=repo, today="2026-08-12")

        missing_w1_path = (repo / ".agent-work" / "w1" / "spine.json").relative_to(repo)
        assert run_crew.spine_terminal(missing_w1_path, repo) is False


# --------------------------------------------------------------------------- #
# close_work -- refusal leaves the work area byte-for-byte untouched
# (required evidence: criterion 1).
# --------------------------------------------------------------------------- #

@requires_git
class TestCloseWorkLeaseActiveRefusalLeavesWorkUntouched:
    def test_violating_lease_active_refuses_byte_for_byte_untouched(self, repo):
        spine = _terminal_spine(engine_session={"status": "active", "session_id": "s1"})
        area = _make_work_area(repo, "w1", "spine.json", spine)
        before = _snapshot(repo / ".agent-work")

        with pytest.raises(sl.SpineLifecycleError) as excinfo:
            sl.close_work(area["spine_path"], root=repo, today="2026-08-12")
        assert "the lease is still active" in str(excinfo.value)

        after = _snapshot(repo / ".agent-work")
        assert after == before, "the work area was touched by a refused close"
        assert not (repo / ".agent-work" / "archive").exists()


@requires_git
class TestCloseWorkNonTerminalGateRefusal:
    def test_violating_non_terminal_gate_refuses_and_names_it(self, repo):
        spine = _terminal_spine(
            items=["m1", "m2"],
            tasks={"m1": {"status": "complete"}, "m2": {"status": "in-progress"}},
        )
        area = _make_work_area(repo, "w1", "spine.json", spine)
        before = _snapshot(repo / ".agent-work")

        with pytest.raises(sl.SpineLifecycleError) as excinfo:
            sl.close_work(area["spine_path"], root=repo, today="2026-08-12")
        assert "m2" in str(excinfo.value)

        assert _snapshot(repo / ".agent-work") == before


@requires_git
class TestCloseWorkArchiveExistsRefusal:
    def test_violating_archive_already_exists_refuses_never_overwrites(self, repo):
        spine = _terminal_spine()
        area = _make_work_area(repo, "w1", "spine.json", spine)
        archive_dir = repo / ".agent-work" / "archive" / sl.archive_name_for("w1", today="2026-08-12")
        archive_dir.mkdir(parents=True)
        (archive_dir / "prior.txt").write_text("prior\n", encoding="utf-8", newline="\n")
        before = _snapshot(repo / ".agent-work")

        with pytest.raises(sl.SpineLifecycleError) as excinfo:
            sl.close_work(area["spine_path"], root=repo, today="2026-08-12")
        assert "archive" in str(excinfo.value)

        assert _snapshot(repo / ".agent-work") == before  # the prior archive is untouched too


@requires_git
class TestCloseWorkInnocentProceeds:
    def test_innocent_terminal_and_released_moves_work_area_to_archive(self, repo):
        spine = _terminal_spine()
        area = _make_work_area(repo, "w1", "spine.json", spine)

        result = sl.close_work(area["spine_path"], root=repo, today="2026-08-12")

        archive_dir = repo / ".agent-work" / "archive" / "2026-08-12-w1"
        assert archive_dir.is_dir()
        assert json.loads((archive_dir / "spine.json").read_text()) == spine
        assert (archive_dir / "crew-handoffs" / "note.md").read_text() == "hello\n"
        assert (archive_dir / "evidence").is_dir()  # the empty-directory path moved too
        assert (archive_dir / "triage-candidates").is_dir()
        assert not area["spine_path"].exists()

        assert result["work_id"] == "w1"
        assert result["branch"] is not None
        assert result["head"] is not None
        assert result["message"].endswith("ready to PR.")

        status = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"], check=True, capture_output=True, text=True,
        ).stdout
        assert status.strip() == "", f"the move was not fully committed:\n{status}"


# --------------------------------------------------------------------------- #
# close_work -- a real work area always carries a gitignored top-level entry
# beside the spine (the MCP door's `mcp_calls.jsonl`, `mcp_server_started`).
# `git add` refuses an untracked path that matches a gitignore rule outright
# -- this reproduces the closeout defect C3 found by running close_work on
# its own work area (22 entries moved, then refused, no rollback).
# --------------------------------------------------------------------------- #

@requires_git
class TestCloseWorkGitignoredEntry:
    def test_innocent_gitignored_top_level_file_moves_without_git_add_refusing(self, repo):
        spine = _terminal_spine()
        area = _make_work_area(repo, "w1", "spine.json", spine, ignored_file="mcp_calls.jsonl")

        result = sl.close_work(area["spine_path"], root=repo, today="2026-08-12")

        archive_dir = repo / ".agent-work" / "archive" / "2026-08-12-w1"
        assert (archive_dir / "mcp_calls.jsonl").read_text() == "ignored content\n"
        assert not (area["work_dir"] / "mcp_calls.jsonl").exists()
        assert result["message"].endswith("ready to PR.")

        status = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"], check=True, capture_output=True, text=True,
        ).stdout
        assert status.strip() == "", f"the move was not fully committed:\n{status}"


# --------------------------------------------------------------------------- #
# close_work -- a failure partway through the "everything else" batch rolls
# the whole batch back rather than leaving the work area split (required
# evidence: criterion matching C3's own incident -- 22 entries moved, then a
# refusal, no rollback). Forces the failure on the LAST batch entry so the
# fixture proves entries already moved (including the gitignored one, moved
# on the filesystem, not through git) are genuinely restored, not merely
# never touched.
# --------------------------------------------------------------------------- #

@requires_git
class TestCloseWorkBatchFailureRollsBack:
    def test_violating_mid_batch_failure_restores_every_already_moved_entry(self, repo, monkeypatch):
        spine = _terminal_spine()
        area = _make_work_area(repo, "w1", "spine.json", spine, ignored_file="mcp_calls.jsonl")
        before = _snapshot(repo / ".agent-work")

        real_git = sl._git
        def watching_git(args, *, cwd):
            # "triage-candidates" sorts last among the batch entries
            # (crew-handoffs, evidence, mcp_calls.jsonl, triage-candidates)
            # -- everything else in the batch has already moved by the time
            # this fires, including the gitignored file (moved on the
            # filesystem, never reaching `_git` at all).
            if any("triage-candidates" in str(a) for a in args):
                raise RuntimeError("simulated failure on the last batch entry")
            return real_git(args, cwd=cwd)
        monkeypatch.setattr(sl, "_git", watching_git)

        with pytest.raises(RuntimeError):
            sl.close_work(area["spine_path"], root=repo, today="2026-08-12")

        # Nothing left in the archive -- the whole batch was undone.
        archive_root = repo / ".agent-work" / "archive"
        assert not archive_root.exists() or not any(archive_root.rglob("*"))

        # Every entry, including the gitignored one, is back at its original
        # path -- byte-for-byte identical to before close_work ran.
        assert area["spine_path"].is_file()
        assert (area["work_dir"] / "mcp_calls.jsonl").read_text() == "ignored content\n"
        assert (area["work_dir"] / "crew-handoffs" / "note.md").is_file()
        assert (area["work_dir"] / "evidence").is_dir()
        assert (area["work_dir"] / "triage-candidates").is_dir()
        assert _snapshot(repo / ".agent-work") == before

        # And nothing was left staged either.
        status = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"], check=True, capture_output=True, text=True,
        ).stdout
        # Only the untouched work-area entries remain, all untracked -- no
        # staged renames or adds left dangling from the rolled-back batch.
        for line in status.splitlines():
            assert not line.startswith(("A ", "R ", "M ")), f"leftover staged change:\n{status}"


# --------------------------------------------------------------------------- #
# close_work -- the differing-basename fixture (required evidence: criterion
# 5, MANDATORY). open_work always writes `spine.json`; this Commander's OWN
# driving spine is `execute.json`. A literal hardcode of the excluded names
# would sweep it into the "everything else" batch before the spine-last step
# -- untestable by any spine.json-named fixture, because open_work never
# writes anything else. See the result artifact for the mutation experiment
# (hardcode the literal strings, watch this go red, restore, watch it go
# green again).
# --------------------------------------------------------------------------- #

@requires_git
class TestCloseWorkDifferingBasenameMandatory:
    def test_execute_json_spine_moves_last_not_swept_into_the_early_batch(self, repo, monkeypatch):
        spine = _terminal_spine()
        area = _make_work_area(repo, "w1", "execute.json", spine)

        real_git = sl._git
        def watching_git(args, *, cwd):
            if any("execute.json" in str(a) for a in args):
                raise RuntimeError("simulated interruption at the spine-last step")
            return real_git(args, cwd=cwd)
        monkeypatch.setattr(sl, "_git", watching_git)

        with pytest.raises(RuntimeError):
            sl.close_work(area["spine_path"], root=repo, today="2026-08-12")

        # The spine is STILL at its original path -- the "everything else"
        # batch never reached it.
        assert area["spine_path"].is_file()

        # But every OTHER top-level entry already moved -- proving the spine
        # move really is attempted LAST, not merely absent from this batch.
        archive_dir = repo / ".agent-work" / "archive" / "2026-08-12-w1"
        assert (archive_dir / "crew-handoffs" / "note.md").is_file()
        assert (archive_dir / "evidence").is_dir()
        assert (archive_dir / "triage-candidates").is_dir()


# --------------------------------------------------------------------------- #
# close_work -- spine-last under a SIMULATED interruption (required evidence:
# criterion 6). Monkeypatches the git call itself to raise once the "spine
# last" step is reached; a real process kill between two git operations is
# out of scope -- this fixture proves ordering, not crash-atomicity.
# --------------------------------------------------------------------------- #

@requires_git
class TestCloseWorkSpineLastUnderInterruption:
    def test_simulated_interruption_leaves_spine_and_journal_at_original_path(self, repo, monkeypatch):
        spine = _terminal_spine()
        area = _make_work_area(repo, "w1", "spine.json", spine)
        journal_path = area["work_dir"] / "spine.json.journal"
        journal_path.write_text('{"seq": 1}\n', encoding="utf-8", newline="\n")

        real_git = sl._git
        def watching_git(args, *, cwd):
            if any("spine.json" in str(a) for a in args):
                raise RuntimeError("simulated interruption before the spine-last step")
            return real_git(args, cwd=cwd)
        monkeypatch.setattr(sl, "_git", watching_git)

        with pytest.raises(RuntimeError):
            sl.close_work(area["spine_path"], root=repo, today="2026-08-12")

        # Both the spine and its journal are still at their ORIGINAL path --
        # a retry can find them.
        assert area["spine_path"].is_file()
        assert journal_path.is_file()

        # The other entries already moved -- the interruption really did
        # land at the spine-last step, not before.
        archive_dir = repo / ".agent-work" / "archive" / "2026-08-12-w1"
        assert (archive_dir / "crew-handoffs" / "note.md").is_file()
        assert (archive_dir / "evidence").is_dir()
        assert (archive_dir / "triage-candidates").is_dir()


# --------------------------------------------------------------------------- #
# close_work -- stage-by-name source guard (required evidence: criterion 7).
# No `git add -A`, no bare `.` reaches a staging call. AST-based (house
# style, tests/test_mcp_adoption.py::_cli_only_verb_violations /
# TestEveryWriteTextPinsNewline above): a byte-comparison cannot go red here
# because the shipped code has no violation to compare against, so this reads
# the source directly and carries its own mutated-copy positive control.
# --------------------------------------------------------------------------- #

def _bare_dot_or_add_all_violations(source: str, where: str) -> list[str]:
    """Every git-call argument LIST literal in `source` containing the bare
    string "." or "-A" -- either reads the whole worktree/cwd instead of
    naming a precise path, defeating "each call names its own paths"."""
    tree = ast.parse(source, filename=where)
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.List):
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and elt.value in ("-A", "."):
                    violations.append(f"{where}:{node.lineno}")
                    break
    return violations


class TestCloseWorkNeverGitAddAllOrBareDot:
    # `close_work`'s own source, INCLUDING the nested `_stage_and_move`
    # closure that actually issues every staging call -- `inspect.getsource`
    # of an outer function returns its full text, nested defs included, so
    # this is genuinely "close_work's own source", not a different function's.
    SOURCE = None

    def setup_method(self):
        import inspect
        self.SOURCE = inspect.getsource(sl.close_work)

    def test_the_shipped_close_work_has_no_violations(self):
        assert _bare_dot_or_add_all_violations(self.SOURCE, "close_work") == []

    def test_violating_a_mutated_copy_with_add_dash_a_is_caught(self):
        # Positive control: proves the predicate can fail. Injects the exact
        # call this guard exists to forbid.
        mutated = self.SOURCE.replace(
            '_git(["commit", "-m"',
            '_git(["add", "-A"], cwd=root)\n    _git(["commit", "-m"',
        )
        assert mutated != self.SOURCE, "the mutation did not change the source -- fixture is stale"
        violations = _bare_dot_or_add_all_violations(mutated, "<mutated>")
        assert violations, "the predicate did not catch an injected `git add -A` call"

    def test_innocent_a_named_path_argument_is_not_flagged(self):
        innocent = '_git(["add", str(work_dir / name)], cwd=root)'
        assert _bare_dot_or_add_all_violations(innocent, "<innocent>") == []


# --------------------------------------------------------------------------- #
# close_work -- end to end through the REAL engine: claim -> start -> attest
# -> advance on every gate, release, THEN close_work (required evidence:
# criterion 8, load-bearing). Origin and every gate's evidence[] must survive
# intact under the archive.
# --------------------------------------------------------------------------- #

def _two_gate_spec(work_id):
    return {
        "work_id": work_id,
        "type": "gated",
        "gate": [
            {"id": "m1", "title": "first", "imperative": "do first",
             "postconditions": [_qual_cond("c1"), _artifact_cond("c2")]},
            {"id": "m2", "title": "second", "imperative": "do second",
             "postconditions": [_qual_cond("c1"), _artifact_cond("c2")]},
        ],
    }


def _drive_gate_to_complete(cl: dict, gate_id: str) -> None:
    checklist_engine.start(cl, gate_id)
    checklist_engine.attest(cl, gate_id, "c1", "postconditions", "verified by hand")
    checklist_engine.attach(cl, gate_id, "user-decision", {"decision": "go"})
    evidence_id = cl["tasks"][gate_id]["evidence"][-1]["id"]
    checklist_engine.attest(cl, gate_id, "c2", "postconditions", "human decided", evidence_id=evidence_id)
    checklist_engine.advance(cl, gate_id, mechanical=True)


@requires_git
class TestCloseWorkEndToEndRealEngine:
    def test_real_generated_spine_driven_to_terminal_then_closed(self, repo, wt_root):
        opened = sl.open_work(
            "w1", _two_gate_spec("w1"), root=repo, base="HEAD",
            parent="constellation/parent/g0/commander/attempt-1", wt_root=wt_root,
        )
        spine_path = Path(opened["SPINE_FILE"])
        worktree = Path(opened["worktree"])

        cl = json.loads(spine_path.read_text())
        origin_before = json.loads(json.dumps(cl["origin"]))

        config = checklist_engine.load_config(cl, None)
        checklist_engine.claim(cl, "test-session", "test", opened["worktree"], config)
        _drive_gate_to_complete(cl, "m1")
        _drive_gate_to_complete(cl, "m2")
        assert checklist_engine.active_id(cl) is None
        checklist_engine.release(cl, "test-session")
        checklist_engine.save(spine_path, cl)

        before_entries = sorted(p.name for p in (worktree / ".agent-work" / "w1").iterdir())

        result = sl.close_work(spine_path, root=worktree, today="2026-08-12")

        archive_dir = worktree / ".agent-work" / "archive" / "2026-08-12-w1"
        assert archive_dir.is_dir()
        after_entries = sorted(p.name for p in archive_dir.iterdir())
        assert after_entries == before_entries, "the archive is missing an entry the work area had"

        archived = json.loads((archive_dir / "spine.json").read_text())
        assert archived["origin"] == origin_before
        for gate_id in ("m1", "m2"):
            assert archived["tasks"][gate_id]["status"] == "complete"
            assert archived["tasks"][gate_id]["evidence"], f"gate {gate_id} lost its evidence[]"
        assert archived["engine_session"]["status"] == "released"

        assert result["work_id"] == "w1"
        assert "ready to PR" in result["message"]


# =============================================================================
# g1 (#574) -- verify + close primitives: done_refusal (pure), _engine_call (the
# single in-process engine choke point) and _advance_and_release.
#
# House style as above: every guard gets a VIOLATING fixture that trips it and an
# INNOCENT fixture that does not. EVERY fixture spine lives under `tmp_path` --
# never a live spine, and never a live lease.
# =============================================================================

import gauge_reader  # noqa: E402

G1_SESSION = "constellation/g1-fixture/implementer"


def inspect_source(fn) -> str:
    """A function's source text, for the source-level assertions below (the one
    choke point, no subprocess, no second call path)."""
    import inspect
    return inspect.getsource(fn)


def _g1_spine(*, gate_status="in-progress", satisfied=True, lease_status="active",
              claimed_ago=300, items=None, tasks=None):
    """A minimal single-gate gated spine the REAL engine will drive: an active
    lease owned by `G1_SESSION`, one gate, one `check: null` postcondition whose
    `satisfied` flag is the knob every refusal fixture below turns."""
    now = datetime.now(timezone.utc)
    claimed_at = (now - timedelta(seconds=claimed_ago)).isoformat()
    default_tasks = {
        "m1": {
            "id": "m1", "title": "the gate", "imperative": "do the thing",
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "the thing is done", "check": None,
                 "satisfied": satisfied},
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": gate_status, "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        },
    }
    return {
        "work_id": "g1-fixture",
        "type": "gated",
        "items": ["m1"] if items is None else items,
        "tasks": default_tasks if tasks is None else tasks,
        "engine_session": {
            "session_id": G1_SESSION, "claimed_by": "implementer", "worktree": ".",
            "status": lease_status, "claimed_at": claimed_at,
            "last_heartbeat": now.isoformat(),
        },
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }


def _write_g1_spine(tmp_path: Path, spine: dict, name: str = "spine.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(spine, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def _read_g1_spine(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _engine_main_call_lines() -> list[int]:
    """The line of every AST call to `checklist_engine.main(...)` in
    scripts/spine_lifecycle.py. AST, not text search: the module and
    `_engine_call` both DISCUSS that call in prose, and prose is not a call
    site."""
    tree = ast.parse((ROOT / "scripts" / "spine_lifecycle.py").read_text(encoding="utf-8"))
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "main"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "checklist_engine"
    ]


def _function_line_span(name: str) -> tuple[int, int]:
    """`(first, last)` source lines of a top-level function in
    scripts/spine_lifecycle.py."""
    tree = ast.parse((ROOT / "scripts" / "spine_lifecycle.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node.lineno, node.end_lineno
    raise AssertionError(f"{name} not found in scripts/spine_lifecycle.py")


def _raw_engine_cli(argv: list[str]) -> str:
    """The same argv run through the REAL engine CLI in a SEPARATE PROCESS, and
    its combined output. The independent path the byte-identity assertions below
    compare against, so "verbatim" is measured against the engine itself rather
    than against another call into the same in-process helper.

    Newline-normalized (\\r\\n -> \\n) before returning: on Windows, output
    piped through a real subprocess picks up CRLF at the OS/CRT layer that the
    in-process `_engine_call` capture (an `io.StringIO`, never touching a
    platform pipe) never introduces. The assertion this feeds is a genuine
    "same text" check, not a "same line-ending convention" check -- comparing
    raw strings made it fail on Windows CI for a reason unrelated to what it
    exists to test (issue #495's family: a newline-sensitive comparison that
    only a non-Linux runner exposes)."""
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "checklist_engine.py"), *argv],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    return (proc.stdout + proc.stderr).strip().replace("\r\n", "\n")


# --------------------------------------------------------------------------- #
# done_refusal -- pure. Exactly the two new checks (tree clean, episode
# captured). It must NOT call or fold in closeout_refusal: done_refusal runs
# on the CURRENT state, before _advance_and_release runs, while the lease is
# by definition still active -- closeout_refusal's own first check refuses
# unless the lease has already been released, so folding it in here would
# refuse every legitimate call. closeout_refusal's lease/terminality/archive
# logic stays exclusively in close_work, downstream, after release.
# --------------------------------------------------------------------------- #

class TestDoneRefusal:
    def test_innocent_all_clear_proceeds(self):
        assert sl.done_refusal(
            _terminal_spine(), tree_clean=True, episodes_captured=True,
        ) is None

    def test_innocent_all_clear_proceeds_even_with_an_active_lease(self):
        # The real calling context: done_refusal runs BEFORE
        # _advance_and_release, so the lease is still active by definition.
        # That must not refuse -- done_refusal does not look at the lease.
        spine = _terminal_spine(engine_session={"status": "active", "session_id": "s1"})
        assert sl.done_refusal(spine, tree_clean=True, episodes_captured=True) is None

    def test_violating_dirty_tree_refuses_with_the_exact_string(self):
        msg = sl.done_refusal(
            _terminal_spine(), tree_clean=False, episodes_captured=True,
        )
        assert msg == "close refused: the working tree has uncommitted changes"

    def test_violating_no_episode_refuses_with_the_exact_string(self):
        msg = sl.done_refusal(
            _terminal_spine(), tree_clean=True, episodes_captured=False,
        )
        assert msg == "close refused: this run captured no episode"

    def test_checks_run_in_order_tree_before_episode(self):
        # Both new checks fail; the TREE is named, proving check 1 runs first.
        msg = sl.done_refusal(
            _terminal_spine(), tree_clean=False, episodes_captured=False,
        )
        assert msg == "close refused: the working tree has uncommitted changes"

    def test_only_one_refusal_ever_comes_back(self):
        # Every check failing at once still yields ONE message, not a list --
        # "one actionable refusal, never a ritual to re-derive".
        msg = sl.done_refusal(
            _terminal_spine(engine_session={"status": "active", "session_id": "s1"},
                            tasks={"m1": {"status": "in-progress"}}),
            tree_clean=False, episodes_captured=False,
        )
        assert isinstance(msg, str)
        assert msg.count("close refused:") == 1

    def test_does_not_call_closeout_refusal(self):
        # Source-text check, not merely eyeballed: done_refusal never
        # references closeout_refusal at all.
        import inspect
        assert "closeout_refusal" not in inspect.getsource(sl.done_refusal)

    def test_does_not_take_archive_exists(self):
        with pytest.raises(TypeError):
            sl.done_refusal(
                _terminal_spine(), tree_clean=True, episodes_captured=True,
                archive_exists=False,
            )

    def test_pure_no_filesystem_symbols(self):
        import inspect
        src = inspect.getsource(sl.done_refusal)
        for banned in ("open(", "subprocess.", "Path("):
            assert banned not in src


# --------------------------------------------------------------------------- #
# _engine_call -- the SINGLE in-process choke point. Never raises: an argv
# argparse rejects exits 2 through SystemExit, which main()'s own try/except
# (EngineError only) does not catch.
# --------------------------------------------------------------------------- #

class TestEngineCall:
    def test_innocent_valid_argv_returns_output_and_zero(self, tmp_path):
        path = _write_g1_spine(tmp_path, _g1_spine())
        output, code = sl._engine_call(["--file", str(path), "current"])
        assert code == 0
        assert "m1" in output

    def test_violating_malformed_argv_returns_nonzero_and_does_not_raise(self, tmp_path):
        # `advance` with no gate id: argparse calls sys.exit(2), and main()'s own
        # try/except catches EngineError ONLY -- so without the SystemExit clause
        # this escapes the helper entirely instead of coming back as (output, code).
        path = _write_g1_spine(tmp_path, _g1_spine())
        output, code = sl._engine_call(["--file", str(path), "advance"])
        assert code == 2
        assert output  # argparse's usage text was captured, not printed past us
        assert "usage" in output.lower()

    def test_violating_unknown_flag_returns_nonzero_and_does_not_raise(self, tmp_path):
        # The lane-A shape the handoff names: a flag that is not (or is no longer)
        # in `parse_args`.
        path = _write_g1_spine(tmp_path, _g1_spine())
        output, code = sl._engine_call(
            ["--file", str(path), "advance", "m1", "--no-such-flag"]
        )
        assert code == 2
        assert output

    def test_violating_unknown_verb_returns_nonzero_and_does_not_raise(self, tmp_path):
        path = _write_g1_spine(tmp_path, _g1_spine())
        output, code = sl._engine_call(["--file", str(path), "not-a-verb"])
        assert code == 2

    def test_violating_missing_spine_file_returns_nonzero_and_does_not_raise(self, tmp_path):
        # `load()` runs BEFORE main()'s try/except, so a missing file raises an
        # OSError from outside every engine-side handler.
        output, code = sl._engine_call(["--file", str(tmp_path / "nope.json"), "current"])
        assert code == 1
        assert output

    def test_violating_engine_refusal_returns_nonzero_with_the_refusal_text(self, tmp_path):
        # An EngineError the engine handles itself: main() prints REFUSED and
        # returns 1, so the text must come back as output, not as an exception.
        path = _write_g1_spine(tmp_path, _g1_spine(satisfied=False))
        output, code = sl._engine_call(
            ["--file", str(path), "advance", "m1", "--mechanical",
             "--session-id", G1_SESSION]
        )
        assert code == 1
        assert "REFUSED:" in output
        assert "postconditions unmet" in output

    def test_captured_output_never_reaches_the_real_streams(self, tmp_path, capsys):
        # The redirect is the point: a closeout primitive must not spray engine
        # output onto its caller's stdout/stderr.
        path = _write_g1_spine(tmp_path, _g1_spine())
        sl._engine_call(["--file", str(path), "current"])
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    def test_is_the_only_place_this_module_calls_checklist_engine_main(self):
        # Close criterion: ONE choke point. Measured over the AST, not the text,
        # so prose in a docstring cannot pass for a call site and a second real
        # call path added later cannot hide behind one.
        sites = _engine_main_call_lines()
        assert len(sites) == 1, f"checklist_engine.main called at lines {sites}"
        start, end = _function_line_span("_engine_call")
        assert start <= sites[0] <= end, "the one call site is not inside _engine_call"

    def test_advance_and_release_goes_through_the_choke_point_only(self):
        body = inspect_source(sl._advance_and_release)
        assert "_engine_call(" in body
        # Never a second call path: no subprocess, no direct engine.main, no
        # shelling out to the engine script.
        assert "subprocess" not in body
        assert "checklist_engine.main(" not in body
        assert "checklist_engine.py" not in body


# --------------------------------------------------------------------------- #
# _advance_and_release -- advance the gate the run is inside, then release. A
# refused advance comes back VERBATIM and the release is never attempted.
# --------------------------------------------------------------------------- #

class TestAdvanceAndRelease:
    def test_innocent_terminal_gate_not_yet_advanced_ends_released(self, tmp_path):
        # Close criterion 1: the gate is at its last postcondition, satisfied but
        # not yet advanced. One call closes it and releases the lease.
        path = _write_g1_spine(tmp_path, _g1_spine(gate_status="in-progress", satisfied=True))
        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)
        assert result["ok"] is True, result
        after = _read_g1_spine(path)
        assert after["engine_session"]["status"] == "released"
        assert after["tasks"]["m1"]["status"] == "complete"

    def test_innocent_pending_gate_is_started_first(self, tmp_path):
        # Step 2 of the sequence: a gate still `pending` cannot be advanced, so
        # it is started first.
        path = _write_g1_spine(tmp_path, _g1_spine(gate_status="pending", satisfied=True))
        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)
        assert result["ok"] is True, result
        after = _read_g1_spine(path)
        assert after["tasks"]["m1"]["status"] == "complete"
        assert after["engine_session"]["status"] == "released"

    def test_innocent_already_terminal_spine_only_releases(self, tmp_path):
        # active_id() is None: every gate is terminal, so the advance half has
        # nothing to do and only the release is left.
        path = _write_g1_spine(tmp_path, _g1_spine(gate_status="complete", satisfied=True))
        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)
        assert result["ok"] is True, result
        after = _read_g1_spine(path)
        assert after["engine_session"]["status"] == "released"
        assert "released lease" in result["output"]

    def test_innocent_relative_spine_path_resolves_against_root(self, tmp_path):
        _write_g1_spine(tmp_path, _g1_spine())
        result = sl._advance_and_release("spine.json", G1_SESSION, root=tmp_path)
        assert result["ok"] is True, result
        assert _read_g1_spine(tmp_path / "spine.json")["engine_session"]["status"] == "released"

    def test_why_is_recorded_on_the_why_trail_when_given(self, tmp_path):
        path = _write_g1_spine(tmp_path, _g1_spine())
        result = sl._advance_and_release(
            path, G1_SESSION, root=tmp_path, why="the gate's evidence is attached and green",
        )
        assert result["ok"] is True, result
        trail = _read_g1_spine(path).get("why_trail") or []
        assert any(
            r.get("why") == "the gate's evidence is attached and green" for r in trail
        ), trail

    def test_blank_why_falls_back_to_mechanical(self, tmp_path):
        # Not a why: whitespace records no understanding, so it must take the
        # --mechanical branch rather than being passed as a why the engine would
        # refuse as empty.
        path = _write_g1_spine(tmp_path, _g1_spine())
        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path, why="   ")
        assert result["ok"] is True, result
        trail = _read_g1_spine(path).get("why_trail") or []
        assert trail and trail[-1].get("mechanical") is True, trail

    def test_violating_unmet_postcondition_passes_the_refusal_through_unchanged(self, tmp_path):
        # Close criterion 2, load-bearing. The refusal text must be BYTE-IDENTICAL
        # to the engine's own, and the release must never be attempted.
        spine = _g1_spine(satisfied=False)
        path = _write_g1_spine(tmp_path, spine)
        pristine = _write_g1_spine(tmp_path, spine, name="pristine.json")

        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)

        assert result["ok"] is False
        assert result["stage"] == "advance"

        # The engine's own words, produced by a SEPARATE PROCESS running the real
        # CLI over the same argv against an identical spine.
        expected = _raw_engine_cli([
            "--file", str(pristine), "advance", "m1", "--mechanical",
            "--session-id", G1_SESSION,
        ])
        assert result["refusal"] == expected
        assert "postconditions unmet" in result["refusal"]

        # The release was NEVER attempted: the lease is still active and the gate
        # is still open.
        after = _read_g1_spine(path)
        assert after["engine_session"]["status"] == "active"
        assert after["tasks"]["m1"]["status"] == "in-progress"

    def test_violating_refusal_carries_no_wording_of_our_own(self, tmp_path):
        # A re-worded refusal is the defect: the returned text must be exactly what
        # the engine emitted, with nothing prepended, appended, or paraphrased.
        path = _write_g1_spine(tmp_path, _g1_spine(satisfied=False))
        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)
        assert result["refusal"].startswith("RAIL:") or result["refusal"].startswith("REFUSED:")
        for invented in ("close refused", "spine_lifecycle", "SpineLifecycleError"):
            assert invented not in result["refusal"]

    def test_violating_refused_start_reports_stage_start_and_never_advances(self, tmp_path):
        # A pending gate with an unmet PREcondition: `start` refuses, so neither
        # the advance nor the release may happen.
        spine = _g1_spine(gate_status="pending", satisfied=True)
        spine["tasks"]["m1"]["preconditions"] = [
            {"id": "p1", "statement": "upstream work is done", "check": None, "satisfied": False},
        ]
        path = _write_g1_spine(tmp_path, spine)

        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)

        assert result["ok"] is False
        assert result["stage"] == "start"
        assert "preconditions unmet" in result["refusal"]
        after = _read_g1_spine(path)
        assert after["tasks"]["m1"]["status"] == "pending"
        assert after["engine_session"]["status"] == "active"

    def test_violating_refused_release_reports_stage_release(self, tmp_path):
        # Every gate is already terminal, so the advance half is skipped and the
        # release is reached -- and refused, because this session does not own the
        # lease. `stage` names which half failed and the engine's text says why.
        path = _write_g1_spine(tmp_path, _g1_spine(gate_status="complete"))
        result = sl._advance_and_release(path, "not-the-owner", root=tmp_path)
        assert result["ok"] is False
        assert result["stage"] == "release"
        assert "does not own the lease" in result["refusal"]
        after = _read_g1_spine(path)
        assert after["engine_session"]["status"] == "active"

    def test_violating_non_owner_is_refused_at_the_advance_before_any_release(self, tmp_path):
        # The engine's actor-authority gate fires first for a non-owner, so the
        # refusal is the ADVANCE's and the release is never attempted.
        path = _write_g1_spine(tmp_path, _g1_spine())
        result = sl._advance_and_release(path, "not-the-owner", root=tmp_path)
        assert result["ok"] is False
        assert result["stage"] == "advance"
        assert "owned by active session" in result["refusal"]
        after = _read_g1_spine(path)
        assert after["engine_session"]["status"] == "active"
        assert after["tasks"]["m1"]["status"] == "in-progress"

    def test_no_second_advance_after_a_refused_one(self, tmp_path):
        # The refusal returns; it never retries with a different flag. A run that
        # quietly re-advanced with --why on refusal would defeat the whole point.
        path = _write_g1_spine(tmp_path, _g1_spine(satisfied=False))
        calls = []
        real = sl._engine_call

        def spy(argv):
            calls.append(list(argv))
            return real(argv)

        sl._engine_call = spy
        try:
            result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)
        finally:
            sl._engine_call = real
        assert result["ok"] is False
        verbs = [argv[2] for argv in calls]
        assert verbs == ["advance"], verbs


# --------------------------------------------------------------------------- #
# HARD band -- close criterion 3, the finding this gate exists to cover.
#
# `advance`'s `require_why` is computed LIVE at the engine's CLI boundary from
# `_trip_hard_band_reading` (checklist_engine._run_verb, ~:3369); it is not
# derived from anything a caller passes. At/over the hard band the engine
# REFUSES `--mechanical` outright, so `_advance_and_release` must never assume
# the mechanical close succeeds. This is plausibly the exact scenario #574
# cites: "an Admiral's closeout was refused at 23% context."
#
# What the fixture has to satisfy for the gauge to be read at all -- all four,
# or the reading collapses to None and the band is silently inactive:
#   * an ACTIVE lease, because `_checklist_owner` keys the gauge FILENAME off it
#     (`gauge_reader.gauge_filename(owner_key(session_id))`);
#   * `observed_at` NOT before the lease's `claimed_at`, or
#     `_reading_predates_claim` reads the sample as a predecessor's;
#   * a model in `gauge_reader._PROFILES`, or `read()` declines it as
#     uncalibrated;
#   * freshness inside `DEFAULT_MAX_AGE` (30 minutes).
#
# And the gate must already be IN-PROGRESS: `start` (not `advance`) is
# TRIP_HARD_GUARDED (checklist_engine:83), so a hard-band fixture whose gate is
# still `pending` is refused at the BEGIN with the begin-refused message and
# never reaches the why-required refusal this test is about.
# --------------------------------------------------------------------------- #

HARD_BAND_MODEL = "claude-opus-5"  # hard threshold 150_000/1_000_000 = 0.15
HARD_BAND_FILL = 0.92


def _write_hard_band_gauge(spine_path: Path, *, fill=HARD_BAND_FILL,
                           model=HARD_BAND_MODEL, session_id=G1_SESSION) -> Path:
    """A gauge record at/over the hard band, beside `spine_path`, named for the
    lease that owns the fixture spine -- `gauge_reader.gauge_filename` /
    `owner_key`, never a hand-spelled filename, so this side and the engine's
    read side cannot drift."""
    gauge_path = spine_path.parent / gauge_reader.gauge_filename(
        gauge_reader.owner_key(session_id)
    )
    gauge_path.write_text(
        json.dumps({
            "schema_version": 1,
            "fill_fraction": fill,
            "model": model,
            "observed_at": datetime.now(timezone.utc).isoformat(),
        }),
        encoding="utf-8", newline="\n",
    )
    return gauge_path


class TestAdvanceAndReleaseHardBand:
    def test_the_fixture_really_is_in_the_hard_band(self, tmp_path):
        # The negative control for this whole class: if the gauge were declined
        # for any of the four reasons above, the tests below would pass by
        # accident on a band that was never active.
        spine = _g1_spine()
        path = _write_g1_spine(tmp_path, spine)
        gauge_path = _write_hard_band_gauge(path)
        assert gauge_path.exists()

        reading = gauge_reader.read(gauge_path)
        assert reading is not None, "the gauge record itself was declined"
        _, hard = gauge_reader.thresholds_for(reading.model)
        assert reading.fill_fraction >= hard

        # And the ENGINE, on this exact spine, agrees it is over the line.
        assert checklist_engine._trip_hard_band_reading(spine, tmp_path, "m1") is not None

    def test_violating_why_less_close_is_refused_instead_of_closing_silently(self, tmp_path):
        path = _write_g1_spine(tmp_path, _g1_spine())
        _write_hard_band_gauge(path)

        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)  # no why

        assert result["ok"] is False
        assert result["stage"] == "advance"
        # The engine's own why-required wording, verbatim -- not a paraphrase.
        assert "cannot be closed silently" in result["refusal"]
        assert "Closing the gate is NOT refused; only the silence is." in result["refusal"]
        assert 'advance m1 --why "<understanding>"' in result["refusal"]

        # It did NOT close silently, and the release never happened.
        after = _read_g1_spine(path)
        assert after["tasks"]["m1"]["status"] == "in-progress"
        assert after["engine_session"]["status"] == "active"
        # No mechanical marker was recorded either: a mechanical close over the
        # line is exactly what leaves the next agent cold-starting from a
        # pre-trip digest.
        assert not (after.get("why_trail") or [])

    def test_the_refusal_is_byte_identical_to_the_engines_own(self, tmp_path):
        spine = _g1_spine()
        path = _write_g1_spine(tmp_path, spine)
        _write_hard_band_gauge(path)

        pristine_dir = tmp_path / "pristine"
        pristine_dir.mkdir()
        pristine = _write_g1_spine(pristine_dir, spine)
        _write_hard_band_gauge(pristine)

        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)
        expected = _raw_engine_cli([
            "--file", str(pristine), "advance", "m1", "--mechanical",
            "--session-id", G1_SESSION,
        ])
        assert result["refusal"] == expected

    def test_innocent_the_same_fixture_closes_cleanly_once_a_why_is_supplied(self, tmp_path):
        # THE SAME fixture, over the same line, after the same refusal: closing the
        # gate was never what the engine refused -- only closing it in silence.
        path = _write_g1_spine(tmp_path, _g1_spine())
        _write_hard_band_gauge(path)

        refused = sl._advance_and_release(path, G1_SESSION, root=tmp_path)
        assert refused["ok"] is False

        why = "postconditions attested and green; g2 picks up reap and child-plan release"
        closed = sl._advance_and_release(path, G1_SESSION, root=tmp_path, why=why)

        assert closed["ok"] is True, closed
        after = _read_g1_spine(path)
        assert after["tasks"]["m1"]["status"] == "complete"
        assert after["engine_session"]["status"] == "released"
        # The understanding actually landed on the append-only why_trail, which is
        # the whole point of the refusal.
        assert any(r.get("why") == why for r in (after.get("why_trail") or []))

    def test_innocent_below_the_hard_band_a_mechanical_close_still_succeeds(self, tmp_path):
        # The INNOCENT counterpart: identical fixture, identical call, a gauge
        # BELOW the line. The mechanical close goes through -- so the refusal above
        # is caused by the band and by nothing else in the fixture.
        path = _write_g1_spine(tmp_path, _g1_spine())
        _write_hard_band_gauge(path, fill=0.05)

        result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)

        assert result["ok"] is True, result
        after = _read_g1_spine(path)
        assert after["tasks"]["m1"]["status"] == "complete"
        assert after["engine_session"]["status"] == "released"
        assert (after.get("why_trail") or [])[-1].get("mechanical") is True

    def test_mechanical_is_never_assumed_to_have_succeeded(self, tmp_path):
        # The regression this gate exists to prevent: a helper that fires
        # `--mechanical` and then releases regardless would leave the lease closed
        # on a gate that never closed.
        path = _write_g1_spine(tmp_path, _g1_spine())
        _write_hard_band_gauge(path)

        calls = []
        real = sl._engine_call

        def spy(argv):
            calls.append(list(argv))
            return real(argv)

        sl._engine_call = spy
        try:
            result = sl._advance_and_release(path, G1_SESSION, root=tmp_path)
        finally:
            sl._engine_call = real

        assert result["ok"] is False
        assert [argv[2] for argv in calls] == ["advance"], calls
        assert "--mechanical" in calls[0]
        assert "release" not in [argv[2] for argv in calls]


# --------------------------------------------------------------------------- #
# force_reap -- g2. A LIBRARY call into spine_rail._binding_transaction with
# an identity mutate; spine_rail.py itself is never edited.
# --------------------------------------------------------------------------- #

sys.path.insert(0, str(ROOT / "scripts" / "hooks"))
import spine_rail  # noqa: E402


def _binding_entry(*, spine: Path, claimed_at=None) -> dict:
    return {
        "spine": str(spine),
        "engine_session": {"session_id": "irrelevant-to-the-reaper"},
        "worktree": str(spine.parent),
        "claimed_at": claimed_at or datetime.now(timezone.utc).isoformat(),
    }


def _write_binding_target(path: Path, *, status: str) -> Path:
    """A standalone spine JSON -- only `engine_session.status` matters to
    `_reap_binding_entries`, which reads the TARGET file, not the binding
    entry's own denormalized copy."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"engine_session": {"session_id": "s1", "status": status}}),
        encoding="utf-8", newline="\n",
    )
    return path


class TestForceReap:
    def test_innocent_a_released_targets_entry_is_gone_immediately(self, tmp_path):
        # Close criterion: a binding-store entry whose target spine is already
        # `released` is gone IMMEDIATELY after the call -- read via
        # spine_rail.load_binding, not by waiting for another transaction.
        target = _write_binding_target(
            tmp_path / ".agent-work" / "some-work" / "spine.json", status="released"
        )
        # Precondition sanity: the fixture's target really does read
        # "released" before force_reap ever runs -- the reap is conditional on
        # this, not unconditional.
        assert spine_rail.load_spine(target)["engine_session"]["status"] == "released"

        spine_rail.save_binding(tmp_path, {"s1": {str(target): _binding_entry(spine=target)}})
        before = spine_rail.load_binding(tmp_path)
        assert str(target) in before.get("s1", {}), before

        result = sl.force_reap(tmp_path)

        assert result is not None, "fail-open path taken unexpectedly"
        after = spine_rail.load_binding(tmp_path)
        assert str(target) not in after.get("s1", {}), after

    def test_violating_an_active_targets_entry_is_retained(self, tmp_path):
        # Paired contrast: `_reap_binding_entries` only drops a "released"
        # target -- an ACTIVE one must survive an identity-mutate force_reap
        # unchanged, proving the reap is conditional, not a blanket wipe.
        target = _write_binding_target(
            tmp_path / ".agent-work" / "some-work" / "spine.json", status="active"
        )
        spine_rail.save_binding(tmp_path, {"s1": {str(target): _binding_entry(spine=target)}})

        result = sl.force_reap(tmp_path)

        assert result is not None
        after = spine_rail.load_binding(tmp_path)
        assert str(target) in after.get("s1", {}), after


# --------------------------------------------------------------------------- #
# _release_child_plans -- g2, #552's mechanism half: reap alone only clears
# entries whose target already reads "released"; a child plan's own
# still-active lease is invisible to that reap and must be released
# explicitly. Three safety properties, each exercised by a NEGATIVE test
# below: lineage not proximity, honest non-owner release, escape refusal.
# --------------------------------------------------------------------------- #

PARENT_SESSION = "constellation/cmdr-parent/commander"


def _leased_plan(session_id: str, *, status: str = "active") -> dict:
    """A minimal standalone plan/spine JSON carrying just enough shape to be
    driven by the real engine's `release` verb -- what _release_child_plans
    keys off (items/tasks content itself is irrelevant to it)."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "work_id": "child-fixture",
        "type": "gated",
        "items": ["c1"],
        "tasks": {
            "c1": {
                "id": "c1", "title": "x", "imperative": "x",
                "preconditions": [], "postconditions": [], "constraints": [],
                "directives": None, "child_checklist": None,
                "status": "complete", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            },
        },
        "engine_session": {
            "session_id": session_id, "claimed_by": "implementer", "worktree": ".",
            "status": status, "claimed_at": now, "last_heartbeat": now,
        },
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }


def _parent_spine_with_children(child_refs: list[str], *, session_id=PARENT_SESSION) -> dict:
    """A parent spine whose tasks declare `child_refs` (each resolved
    relative to work_dir) as their `child_checklist`. An empty list yields
    one ordinary gate with no child_checklist at all -- the 0-children case."""
    tasks: dict = {}
    items: list[str] = []
    for i, ref in enumerate(child_refs, start=1):
        tid = f"g{i}"
        items.append(tid)
        tasks[tid] = {
            "id": tid, "title": f"gate {i}", "imperative": "x",
            "preconditions": [], "postconditions": [], "constraints": [],
            "directives": None, "child_checklist": ref,
            "status": "complete", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        }
    if not items:
        items = ["m1"]
        tasks["m1"] = {
            "id": "m1", "title": "gate", "imperative": "x",
            "preconditions": [], "postconditions": [], "constraints": [],
            "directives": None, "child_checklist": None,
            "status": "complete", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        }
    now = datetime.now(timezone.utc).isoformat()
    return {
        "work_id": "cmdr-parent",
        "type": "gated",
        "items": items,
        "tasks": tasks,
        "engine_session": {
            "session_id": session_id, "claimed_by": "commander", "worktree": ".",
            "status": "active", "claimed_at": now, "last_heartbeat": now,
        },
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }


def _write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


class TestReleaseChildPlans:
    def test_innocent_zero_children_releases_nothing(self, tmp_path):
        work_dir = tmp_path / "cmdr"
        spine_path = _write_json(work_dir / "spine.json", _parent_spine_with_children([]))

        result = sl._release_child_plans(spine_path, work_dir, root=tmp_path, reason="cmdr-parent closeout")

        assert result == {"released": [], "unclaimed_active": []}
        # The parent's own active lease must not have been touched either.
        assert json.loads(spine_path.read_text())["engine_session"]["status"] == "active"

    def test_innocent_one_declared_child_ends_released(self, tmp_path):
        work_dir = tmp_path / "cmdr"
        child_path = _write_json(work_dir / "g1-implementer-plan.json", _leased_plan("child-session-1"))
        spine_path = _write_json(
            work_dir / "spine.json",
            _parent_spine_with_children(["g1-implementer-plan.json"]),
        )

        result = sl._release_child_plans(
            spine_path, work_dir, root=tmp_path, reason="cmdr-parent closeout: parent cmdr-parent"
        )

        assert result["released"] == [str(child_path)]
        assert result["unclaimed_active"] == []
        after = json.loads(child_path.read_text())
        assert after["engine_session"]["status"] == "released"

    def test_innocent_two_declared_children_both_end_released(self, tmp_path):
        work_dir = tmp_path / "cmdr"
        c1 = _write_json(work_dir / "interrogation.json", _leased_plan("child-session-1"))
        c2 = _write_json(work_dir / "execute.json", _leased_plan("child-session-2"))
        spine_path = _write_json(
            work_dir / "spine.json",
            _parent_spine_with_children(["interrogation.json", "execute.json"]),
        )

        result = sl._release_child_plans(spine_path, work_dir, root=tmp_path, reason="cmdr-parent closeout")

        assert sorted(result["released"]) == sorted([str(c1), str(c2)])
        assert result["unclaimed_active"] == []
        assert json.loads(c1.read_text())["engine_session"]["status"] == "released"
        assert json.loads(c2.read_text())["engine_session"]["status"] == "released"

    def test_release_never_echoes_the_childs_own_session_id(self, tmp_path):
        # Property 2, positive half: the caller id passed to `release` is the
        # PARENT's own session, never the child's -- `release` itself records
        # no session_id anywhere in the persisted spine or journal (it is not
        # a MUTATING_VERBS member -- checklist_engine.py:70-74 -- so no
        # journal line is written for it at all), so the only way to observe
        # WHICH id crossed the choke point is to watch the choke point.
        work_dir = tmp_path / "cmdr"
        _write_json(work_dir / "g1-implementer-plan.json", _leased_plan("child-session-1"))
        spine_path = _write_json(work_dir / "spine.json", _parent_spine_with_children(["g1-implementer-plan.json"]))

        calls = []
        real = sl._engine_call

        def spy(argv):
            calls.append(list(argv))
            return real(argv)

        sl._engine_call = spy
        try:
            result = sl._release_child_plans(spine_path, work_dir, root=tmp_path, reason="cmdr-parent closeout")
        finally:
            sl._engine_call = real

        assert result["released"], result
        release_calls = [argv for argv in calls if "release" in argv]
        assert len(release_calls) == 1, release_calls
        argv = release_calls[0]
        session_id = argv[argv.index("--session-id") + 1]
        assert session_id != "child-session-1"
        assert session_id == PARENT_SESSION
        assert "--force" in argv
        assert argv[argv.index("--reason") + 1] == "cmdr-parent closeout"

    # ----------------------------------------------------------------- #
    # NEGATIVE tests -- load-bearing. Each proves one safety property by
    # reproducing the boundary, not by arguing for it.
    # ----------------------------------------------------------------- #

    def test_violating_a_spine_outside_work_dir_sharing_a_prefix_is_never_touched(self, tmp_path):
        # Property 1 (directory proximity is the WRONG predicate), the sharp
        # form: a sibling directory whose NAME merely shares a string prefix
        # with work_dir ("cmdr-g" vs "cmdr-g2") is not "inside" it by any
        # path-containment test, and must never be scanned at all.
        work_dir = tmp_path / "cmdr-g"
        sibling_dir = tmp_path / "cmdr-g2"
        outside_spine = _write_json(sibling_dir / "spine.json", _leased_plan("sibling-session"))
        spine_path = _write_json(work_dir / "spine.json", _parent_spine_with_children([]))

        result = sl._release_child_plans(spine_path, work_dir, root=tmp_path, reason="x")

        assert str(outside_spine) not in result["released"]
        assert str(outside_spine) not in result["unclaimed_active"]
        assert json.loads(outside_spine.read_text())["engine_session"]["status"] == "active"

    def test_violating_unclaimed_active_json_is_left_alone_and_reported(self, tmp_path):
        # Property 1, the ordinary form: an active-leased JSON genuinely
        # UNDER work_dir that no task declares as its child_checklist must be
        # left alone -- releasing it would seize a lease a different,
        # still-working agent genuinely holds.
        work_dir = tmp_path / "cmdr"
        orphan_path = _write_json(work_dir / "some-other-agents-plan.json", _leased_plan("orphan-session"))
        spine_path = _write_json(work_dir / "spine.json", _parent_spine_with_children([]))

        result = sl._release_child_plans(spine_path, work_dir, root=tmp_path, reason="x")

        assert result["released"] == []
        assert result["unclaimed_active"] == [str(orphan_path)]
        assert json.loads(orphan_path.read_text())["engine_session"]["status"] == "active"

    def test_violating_a_symlink_inside_work_dir_escaping_outside_is_refused(self, tmp_path):
        # Property 3: a symlink that lexically sits inside work_dir (and is
        # even DECLARED as a child_checklist) but whose realpath walks
        # outside it must be refused -- the real target's lease survives.
        work_dir = tmp_path / "cmdr"
        outside_dir = tmp_path / "outside"
        real_target = _write_json(outside_dir / "real-spine.json", _leased_plan("outside-session"))

        symlink_path = work_dir / "escape.json"
        work_dir.mkdir(parents=True, exist_ok=True)
        try:
            symlink_path.symlink_to(real_target)
        except OSError:
            pytest.skip("symlinks not supported on this platform/permission level")

        spine_path = _write_json(work_dir / "spine.json", _parent_spine_with_children(["escape.json"]))

        result = sl._release_child_plans(spine_path, work_dir, root=tmp_path, reason="x")

        assert str(symlink_path) not in result["released"]
        assert str(real_target) not in result["released"]
        assert json.loads(real_target.read_text())["engine_session"]["status"] == "active"


# =============================================================================
# finish_work + open_pr (#574 g3) -- "I'm done" as one call, composing g1's
# verify/close primitives and g2's reap + child-plan release with close_work
# (unmodified). Every fixture spine lives under tmp_path -- never a live
# spine, and never a live lease.
# =============================================================================

def _census_active_leases(root: Path) -> int:
    """Structural active-lease census -- mirrors `_active_engine_session_spine`'s
    scan predicate (any `*.json` under `root`, any depth, whose
    `engine_session.status == 'active'`), generalized to COUNT every match
    instead of returning the first. Read-only and defensive on the same
    terms: a missing directory, an unreadable/non-JSON file, a non-dict
    payload, or a missing/non-dict `engine_session` is skipped rather than
    raised."""
    if not root.exists():
        return 0
    count = 0
    for candidate in sorted(root.rglob("*.json")):
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        session = data.get("engine_session")
        if isinstance(session, dict) and str(session.get("status", "")).strip().lower() == "active":
            count += 1
    return count


class TestFinishWorkRefusals:
    def test_violating_dirty_tree_refuses_stage_verify_with_no_mutation(self, tmp_path):
        spine_path = _write_json(
            tmp_path / ".agent-work" / "g3-verify" / "spine.json",
            _g1_spine(gate_status="in-progress", satisfied=True),
        )
        before = spine_path.read_bytes()
        archive_root = tmp_path / ".agent-work" / "archive"

        result = sl.finish_work(
            spine_path, root=tmp_path, session_id=G1_SESSION, today="2026-08-16",
            tree_clean=False, episodes_captured=True, push=False,
        )

        assert result == {
            "ok": False,
            "refusal": "close refused: the working tree has uncommitted changes",
            "stage": "verify",
        }
        assert spine_path.read_bytes() == before, "step 2 refusal must not mutate the spine file"
        assert not archive_root.exists(), "step 2 refusal must not create an archive"

    def test_violating_no_episode_refuses_stage_verify(self, tmp_path):
        spine_path = _write_json(
            tmp_path / ".agent-work" / "g3-verify2" / "spine.json",
            _g1_spine(gate_status="in-progress", satisfied=True),
        )
        result = sl.finish_work(
            spine_path, root=tmp_path, session_id=G1_SESSION, today="2026-08-16",
            tree_clean=True, episodes_captured=False, push=False,
        )
        assert result == {
            "ok": False,
            "refusal": "close refused: this run captured no episode",
            "stage": "verify",
        }

    def test_violating_unmet_postcondition_refuses_stage_advance_release_advance(self, tmp_path):
        # done_refusal passes (tree_clean/episodes_captured both True); the
        # top-level gate itself is not ready -- _advance_and_release refuses
        # at its own "advance" substage, and finish_work must not raise.
        spine_path = _write_json(
            tmp_path / ".agent-work" / "g3-advance" / "spine.json",
            _g1_spine(satisfied=False),
        )
        result = sl.finish_work(
            spine_path, root=tmp_path, session_id=G1_SESSION, today="2026-08-16",
            tree_clean=True, episodes_captured=True, push=False,
        )
        assert result["ok"] is False
        assert result["stage"] == "advance-release:advance"
        assert "postconditions unmet" in result["refusal"]
        after = json.loads(spine_path.read_text())
        assert after["engine_session"]["status"] == "active", "a refused advance must not release the lease"

    def test_violating_archive_already_exists_refuses_stage_archive_without_raising(self, tmp_path):
        # done_refusal passes and _advance_and_release succeeds (releasing the
        # lease); close_work itself then refuses because the archive
        # directory already exists -- finish_work must catch
        # SpineLifecycleError and return the structured refusal, never raise.
        work_id = "g3-archive"
        spine_path = _write_json(
            tmp_path / ".agent-work" / work_id / "spine.json",
            _g1_spine(gate_status="in-progress", satisfied=True),
        )
        today = "2026-08-16"
        archive_dir = tmp_path / ".agent-work" / "archive" / f"{today}-{work_id}"
        archive_dir.mkdir(parents=True)

        result = sl.finish_work(
            spine_path, root=tmp_path, session_id=G1_SESSION, today=today,
            tree_clean=True, episodes_captured=True, push=False,
        )

        assert result["ok"] is False
        assert result["stage"] == "archive"
        assert "archive" in result["refusal"]
        # The advance-and-release half already ran (it is not this step's job
        # to unwind it): the gate closed and the lease released.
        after = json.loads(spine_path.read_text())
        assert after["tasks"]["m1"]["status"] == "complete"
        assert after["engine_session"]["status"] == "released"

    def test_pure_no_hidden_wording_on_refusal(self, tmp_path):
        # The verify-stage refusal text is exactly done_refusal's own words --
        # finish_work does not prepend/append anything of its own.
        spine_path = _write_json(
            tmp_path / ".agent-work" / "g3-wording" / "spine.json",
            _g1_spine(gate_status="in-progress", satisfied=True),
        )
        result = sl.finish_work(
            spine_path, root=tmp_path, session_id=G1_SESSION, today="2026-08-16",
            tree_clean=False, episodes_captured=True, push=False,
        )
        assert result["refusal"] == sl.done_refusal(
            _g1_spine(), tree_clean=False, episodes_captured=True,
        )


class TestFinishWorkCompositionOrder:
    def test_children_released_then_top_level_release_then_reap_then_archive(self, tmp_path):
        # Close criterion, load-bearing: the ORDER finish_work calls its four
        # composed steps in, not merely that all four eventually happen. Every
        # composed function is monkeypatched with a spy that records its own
        # name into a shared list, restored in a finally.
        spine_path = _write_json(tmp_path / ".agent-work" / "g3-order" / "spine.json", {})
        calls: list[str] = []

        def fake_release_children(*args, **kwargs):
            calls.append("release_child_plans")
            return {"released": [], "unclaimed_active": []}

        def fake_advance_and_release(*args, **kwargs):
            calls.append("advance_and_release")
            return {"ok": True, "output": "ok"}

        def fake_force_reap(*args, **kwargs):
            calls.append("force_reap")
            return {"reaped": True}

        def fake_close_work(*args, **kwargs):
            calls.append("close_work")
            return {"work_id": "g3-order", "branch": "b", "head": "h", "archive": "a"}

        real = (sl._release_child_plans, sl._advance_and_release, sl.force_reap, sl.close_work)
        sl._release_child_plans = fake_release_children
        sl._advance_and_release = fake_advance_and_release
        sl.force_reap = fake_force_reap
        sl.close_work = fake_close_work
        try:
            result = sl.finish_work(
                spine_path, root=tmp_path, session_id="s1", today="2026-08-16",
                tree_clean=True, episodes_captured=True, push=False,
            )
        finally:
            sl._release_child_plans, sl._advance_and_release, sl.force_reap, sl.close_work = real

        assert result["ok"] is True, result
        assert calls == [
            "release_child_plans", "advance_and_release", "force_reap", "close_work",
        ], calls


class TestFinishWorkLeaseProofEndToEnd:
    """THE #552 lease-proof end-to-end test -- this gate's actual reason to
    exist (launch order Return Shape item 5)."""

    def test_two_active_leases_become_zero_and_child_lands_in_archive(self, repo):
        work_id = "g3-e2e"
        work_dir = repo / ".agent-work" / work_id
        child_rel = "child-plan.json"
        parent_session = "constellation/g3-e2e/implementer"

        # Child: a real single-gate plan, already terminal (complete), with
        # its OWN lease still ACTIVE -- finish_work is what releases it.
        _write_json(work_dir / child_rel, _leased_plan("child-session-1"))

        # Parent: a real single-gate spine whose gate's postcondition is
        # satisfiable (in-progress, satisfied=True) but not yet advanced,
        # declaring the child via child_checklist, with its OWN lease active.
        parent_spine = _g1_spine(gate_status="in-progress", satisfied=True)
        parent_spine["work_id"] = work_id
        parent_spine["tasks"]["m1"]["child_checklist"] = child_rel
        parent_spine["engine_session"]["session_id"] = parent_session
        spine_path = _write_json(work_dir / "spine.json", parent_spine)

        # A real work area shape beside the spine (a tracked file, an empty
        # dir) -- close_work's own convention, exercised end to end here too.
        (work_dir / "crew-handoffs").mkdir(parents=True, exist_ok=True)
        (work_dir / "crew-handoffs" / "note.md").write_text("hi\n", encoding="utf-8", newline="\n")
        (work_dir / "evidence").mkdir(parents=True, exist_ok=True)

        agent_work_root = repo / ".agent-work"
        active_before = _census_active_leases(agent_work_root)
        assert active_before == 2, "fixture precondition: parent + child both active"

        today = "2026-08-16"
        result = sl.finish_work(
            spine_path, root=repo, session_id=parent_session, today=today,
            tree_clean=True, episodes_captured=True, push=False,
        )
        assert result["ok"] is True, result
        assert result["child_plans_released"], result

        active_after = _census_active_leases(agent_work_root)
        assert active_after == 0, "every lease must be released before finish_work returns"

        archive_dir = repo / ".agent-work" / "archive" / f"{today}-{work_id}"
        assert archive_dir.is_dir()
        archived_child = archive_dir / child_rel
        assert archived_child.is_file(), sorted(p.name for p in archive_dir.rglob("*"))
        assert json.loads(archived_child.read_text())["engine_session"]["status"] == "released"


class TestOpenPr:
    def test_finish_work_never_calls_open_pr_unless_flagged(self, repo):
        spine_path = _write_json(
            repo / ".agent-work" / "g3-pr" / "spine.json",
            _g1_spine(gate_status="in-progress", satisfied=True),
        )
        calls = []
        real_open_pr = sl.open_pr

        def spy(*args, **kwargs):
            calls.append((args, kwargs))
            return "https://example.invalid/pr/1"

        sl.open_pr = spy
        try:
            result = sl.finish_work(
                spine_path, root=repo, session_id=G1_SESSION, today="2026-08-16",
                tree_clean=True, episodes_captured=True, push=False,
            )
        finally:
            sl.open_pr = real_open_pr

        assert result["ok"] is True, result
        assert calls == [], "open_pr must never be called when open_pr=False (the default)"
        assert result["pr"] is None

    def test_finish_work_calls_open_pr_only_when_flagged(self, repo):
        spine_path = _write_json(
            repo / ".agent-work" / "g3-pr2" / "spine.json",
            _g1_spine(gate_status="in-progress", satisfied=True),
        )
        calls = []
        real_open_pr = sl.open_pr

        def spy(work_id, branch, *, root):
            calls.append((work_id, branch, root))
            return "https://example.invalid/pr/2"

        sl.open_pr = spy
        try:
            result = sl.finish_work(
                spine_path, root=repo, session_id=G1_SESSION, today="2026-08-16",
                tree_clean=True, episodes_captured=True, push=False, open_pr=True,
            )
        finally:
            sl.open_pr = real_open_pr

        assert result["ok"] is True, result
        assert len(calls) == 1, calls
        assert result["pr"] == "https://example.invalid/pr/2"

    def test_open_pr_uses_body_file_never_a_body_flag(self, tmp_path, monkeypatch):
        calls = []
        captured_body = {}

        def fake_run(argv, **kwargs):
            calls.append(argv)
            body_file = argv[argv.index("--body-file") + 1]
            captured_body["text"] = Path(body_file).read_text(encoding="utf-8")

            class _Result:
                returncode = 0
                stdout = "https://example.invalid/pr/3\n"
                stderr = ""

            return _Result()

        monkeypatch.setattr(sl.subprocess, "run", fake_run)
        url = sl.open_pr("w1", "feat/w1", root=tmp_path, body="hello\nworld")

        assert url == "https://example.invalid/pr/3"
        assert len(calls) == 1
        argv = calls[0]
        assert "--body-file" in argv
        assert "--body" not in argv
        assert captured_body["text"] == "hello\nworld"

    def test_open_pr_cleans_up_its_temp_body_file(self, tmp_path, monkeypatch):
        captured = {}

        def fake_run(argv, **kwargs):
            captured["path"] = Path(argv[argv.index("--body-file") + 1])

            class _Result:
                returncode = 0
                stdout = "https://example.invalid/pr/4\n"
                stderr = ""

            return _Result()

        monkeypatch.setattr(sl.subprocess, "run", fake_run)
        sl.open_pr("w1", "feat/w1", root=tmp_path)
        assert not captured["path"].exists()

    def test_open_pr_returns_none_on_gh_failure_without_raising(self, tmp_path, monkeypatch):
        def fake_run(argv, **kwargs):
            class _Result:
                returncode = 1
                stdout = ""
                stderr = "gh: not authenticated"

            return _Result()

        monkeypatch.setattr(sl.subprocess, "run", fake_run)
        assert sl.open_pr("w1", "feat/w1", root=tmp_path) is None


@requires_git
class TestSpineDoneCli:
    """scripts/spine_done_cli.py -- the reachable-today "one door verb". Every
    invocation is a FRESH PROCESS (subprocess.run against `python3`), never an
    in-process import -- the only trustworthy validation for engine/hook-
    adjacent code (docs/agents/ORCHESTRATOR_CONTEXT.md)."""

    CLI_PATH = str(ROOT / "scripts" / "spine_done_cli.py")

    def _run_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            ["python3", self.CLI_PATH, *args],
            cwd=str(ROOT), capture_output=True, text=True, env=env,
        )

    def test_fresh_process_ok_path_exits_zero_and_prints_ok_json(self, repo):
        work_id = "g3-cli-ok"
        spine_path = _write_json(
            repo / ".agent-work" / work_id / "spine.json",
            _g1_spine(gate_status="in-progress", satisfied=True),
        )
        proc = self._run_cli([
            "--file", str(spine_path), "--root", str(repo),
            "--session-id", G1_SESSION, "--today", "2026-08-16",
            "--tree-clean", "--episodes-captured", "--no-push",
        ])
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["ok"] is True, payload
        archive_dir = repo / ".agent-work" / "archive" / f"2026-08-16-{work_id}"
        assert archive_dir.is_dir()

    def test_fresh_process_refusal_path_exits_one(self, repo):
        work_id = "g3-cli-refuse"
        spine_path = _write_json(
            repo / ".agent-work" / work_id / "spine.json",
            _g1_spine(gate_status="in-progress", satisfied=True),
        )
        proc = self._run_cli([
            "--file", str(spine_path), "--root", str(repo),
            "--session-id", G1_SESSION, "--today", "2026-08-16",
            "--tree-clean", "--no-push",
        ])
        assert proc.returncode == 1, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["ok"] is False
        assert payload["stage"] == "verify"

    def test_fresh_process_never_touches_a_live_spine_path(self):
        # Constraint check, not a functional one: this suite's own CLI
        # invocations above only ever pass tmp_path-rooted --file/--root
        # arguments -- grep the test source proves no argument literal
        # points at this worktree's own .agent-work/epic-567-door spines.
        source = inspect_source(TestSpineDoneCli._run_cli) + "".join(
            inspect_source(getattr(TestSpineDoneCli, name))
            for name in dir(TestSpineDoneCli)
            if name.startswith("test_fresh_process") and name != "test_fresh_process_never_touches_a_live_spine_path"
        )
        assert ".agent-work/epic-567-door" not in source
