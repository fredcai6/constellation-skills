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
