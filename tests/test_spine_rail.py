"""Unit tests for scripts/hooks/spine_rail.py.

Every decision branch is exercised through the pure/handler functions with
constructed spine fixtures. No subprocess of the engine; state-file facts only.
"""

import importlib.util
import json
from pathlib import Path

import pytest

# Import the hook module directly from its file path (it is not on a package).
_MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "hooks" / "spine_rail.py"
_spec = importlib.util.spec_from_file_location("spine_rail", _MODULE_PATH)
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)


# --- fixtures ----------------------------------------------------------------

def make_spine(items_status, lease_status="active", session_id="eng-1",
               claimed_by="commander", imperatives=None):
    """Build a minimal spine dict.

    items_status: list of (id, status) in item order.
    """
    imperatives = imperatives or {}
    items = [iid for iid, _ in items_status]
    tasks = {}
    for iid, status in items_status:
        tasks[iid] = {
            "id": iid,
            "status": status,
            "imperative": imperatives.get(iid, "do %s" % iid),
        }
    spine = {
        "items": items,
        "tasks": tasks,
        "engine_session": {
            "session_id": session_id,
            "status": lease_status,
            "claimed_by": claimed_by,
            "last_heartbeat": "2026-07-12T00:00:00+00:00",
        },
    }
    return spine


def write_spine(project_dir, spine, work="run1", journal_lines=0):
    d = project_dir / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    spine_path = d / "spine.json"
    spine_path.write_text(json.dumps(spine), encoding="utf-8")
    if journal_lines:
        (d / "spine.json.journal").write_text(
            "".join("{}\n".format(json.dumps({"seq": i})) for i in range(journal_lines)),
            encoding="utf-8",
        )
    return str(spine_path)


def bind(project_dir, sid, spine_path, engine_session="eng-1"):
    sr.save_binding(project_dir, {
        sid: {"spine": spine_path, "engine_session": engine_session, "worktree": str(project_dir)}
    })


@pytest.fixture
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    return tmp_path


# --- pure functions ----------------------------------------------------------

def test_active_id_first_non_terminal():
    spine = make_spine([("a", "complete"), ("b", "skipped"), ("c", "in-progress"), ("d", "pending")])
    assert sr.active_id(spine) == "c"


def test_active_id_all_terminal_returns_none():
    spine = make_spine([("a", "complete"), ("b", "skipped")])
    assert sr.active_id(spine) is None


def test_active_id_bad_input():
    assert sr.active_id({}) is None
    assert sr.active_id({"items": None, "tasks": None}) is None


def test_journal_seq_counts_nonblank(tmp_path):
    sp = write_spine(tmp_path, make_spine([("a", "pending")]), journal_lines=4)
    assert sr.journal_seq(sp) == 4


def test_journal_seq_missing_is_zero(tmp_path):
    sp = write_spine(tmp_path, make_spine([("a", "pending")]), journal_lines=0)
    assert sr.journal_seq(sp) == 0
    assert sr.journal_seq(str(tmp_path / "nope.json")) == 0


def test_reconstruct_current_active():
    spine = make_spine([("g1", "in-progress")], imperatives={"g1": "do the thing"})
    out = sr.reconstruct_current(spine)
    assert "LEASE active: eng-1 (by commander" in out
    assert "ACTIVE g1 [in-progress] -- do the thing" in out


def test_reconstruct_current_done():
    spine = make_spine([("g1", "complete")])
    out = sr.reconstruct_current(spine)
    assert "DONE: no open items." in out


def test_reconstruct_current_no_lease_line_when_released():
    spine = make_spine([("g1", "in-progress")], lease_status="released")
    out = sr.reconstruct_current(spine)
    assert "LEASE active" not in out
    assert "ACTIVE g1" in out


# --- worktree attribution helpers (_same_path / _foreign_worktree) -----------

def test_same_path_fail_safe_returns_true_on_bad_input():
    # (d) a comparison error must NEVER relax the rail: default True.
    assert sr._same_path(None, "x") is True
    assert sr._same_path("x", 123) is True


def test_same_path_windows_normcase_sep_equivalence():
    # (f) case + separator normalize to equal -> no spurious relaxation.
    assert sr._same_path("C:\\Foo", "c:/foo") is True


def test_same_path_distinct_paths_differ():
    assert sr._same_path("C:/a/wtParent", "C:/a/wtChild") is False


def test_foreign_worktree_requires_both_present():
    # (e) only one of cwd / worktree present -> no positive mismatch -> False.
    assert sr._foreign_worktree({"cwd": "X"}, {}) is False
    assert sr._foreign_worktree({}, {"worktree": "Y"}) is False
    assert sr._foreign_worktree({}, {}) is False


def test_foreign_worktree_true_only_on_positive_mismatch():
    assert sr._foreign_worktree({"cwd": "C:/a/parent"}, {"worktree": "C:/a/child"}) is True
    assert sr._foreign_worktree({"cwd": "C:/a/same"}, {"worktree": "C:/a/same"}) is False


# --- decide_stop -------------------------------------------------------------

def test_stop_no_binding_allows(proj):
    assert sr.decide_stop({"session_id": "s1"}, proj) == {}


def test_stop_unreadable_spine_allows(proj):
    bind(proj, "s1", str(proj / ".agent-work" / "gone" / "spine.json"))
    assert sr.decide_stop({"session_id": "s1"}, proj) == {}


def test_stop_released_lease_allows(proj):
    sp = write_spine(proj, make_spine([("g1", "in-progress")], lease_status="released"))
    bind(proj, "s1", sp)
    assert sr.decide_stop({"session_id": "s1"}, proj) == {}


def test_stop_blocked_status_honest_stop_allows(proj):
    sp = write_spine(proj, make_spine([("g1", "blocked")]))
    bind(proj, "s1", sp)
    assert sr.decide_stop({"session_id": "s1"}, proj) == {}


def test_stop_mid_flight_blocks_with_substrings(proj):
    spine = make_spine([("g1", "in-progress")], imperatives={"g1": "finish the feature"})
    sp = write_spine(proj, spine, journal_lines=2)
    bind(proj, "s1", sp)
    out = sr.decide_stop({"session_id": "s1"}, proj)
    assert out["decision"] == "block"
    reason = out["reason"]
    assert "SPINE MID-FLIGHT" in reason
    assert "g1" in reason
    assert "the MIDDLE" in reason
    assert "do not end your turn to wait" in reason
    assert "finish the feature" in reason  # next imperative surfaced
    assert "block" in reason and "waive" in reason  # honest-stop hatches
    hso = out["hookSpecificOutput"]
    assert hso["hookEventName"] == "Stop"
    assert hso["additionalContext"].startswith("ENGINE current ->")
    assert "ACTIVE g1" in hso["additionalContext"]


def test_stop_foreign_worktree_parent_not_blocked(proj):
    # (a) Production-shaped: a subagent SHARING the parent's session_id claims a
    # spine in ITS OWN worktree; the real PostToolUse path writes the single-slot
    # binding pointing at the subagent's worktree/spine. The PARENT then ends its
    # turn (Stop) from the PARENT worktree while that bound spine is mid-flight.
    # The worktree mismatch must let the parent stop (parent is not this driver).
    sub = proj / "subwt"
    subspine = write_spine(sub, make_spine([("g1", "in-progress")]), journal_lines=1)
    cmd = ('py scripts/checklist_engine.py --file .agent-work/run1/spine.json '
           'claim --session-id eng-9 --claimed-by commander')
    sr.handle_post_tool_use(_bash(cmd, session_id="shared", cwd=str(sub)), proj)
    entry = sr.load_binding(proj)["shared"]
    assert entry["worktree"] == str(sub)            # binding wrote subagent wt
    assert sr._same_path(entry["spine"], subspine)  # via the real code path
    # PARENT stops from the PARENT worktree -> foreign -> NOT blocked.
    out = sr.decide_stop({"session_id": "shared", "cwd": str(proj)}, proj)
    assert out == {}
    # And no nudge was recorded for the parent (guard fired before nudge logic).
    assert "shared" not in sr.load_nudges(proj)


def test_stop_same_worktree_and_no_cwd_still_block(proj):
    # (b) The single-agent case must NOT be weakened. Same-worktree mid-flight
    # Stop still blocks; and a Stop with NO cwd (foreign guard cannot fire) still
    # blocks -- proving the guard only relaxes on positive mismatch evidence.
    spine = make_spine([("g1", "in-progress")], imperatives={"g1": "finish it"})
    sp = write_spine(proj, spine, journal_lines=1)
    bind(proj, "s1", sp)  # bind() records worktree == str(proj)
    out_same = sr.decide_stop({"session_id": "s1", "cwd": str(proj)}, proj)
    assert out_same["decision"] == "block"
    out_nocwd = sr.decide_stop({"session_id": "s1"}, proj)
    assert out_nocwd["decision"] == "block"


def test_stop_aid_none_lease_active_release_nudge(proj):
    spine = make_spine([("g1", "complete")], lease_status="active")
    sp = write_spine(proj, spine)
    bind(proj, "s1", sp)
    out = sr.decide_stop({"session_id": "s1"}, proj)
    assert out["decision"] == "block"
    assert "lease is still ACTIVE" in out["reason"]
    assert "release" in out["reason"]


def test_stop_three_strike_block_block_continue(proj):
    spine = make_spine([("g1", "in-progress")])
    sp = write_spine(proj, spine, journal_lines=1)  # frozen journal -> no progress
    bind(proj, "s1", sp)
    o1 = sr.decide_stop({"session_id": "s1"}, proj)
    o2 = sr.decide_stop({"session_id": "s1"}, proj)
    o3 = sr.decide_stop({"session_id": "s1"}, proj)
    assert o1.get("decision") == "block"
    assert o2.get("decision") == "block"
    assert o3.get("continue") is True
    assert "SPINE-RAIL: released turn-end after 3 no-progress nudges" in o3["systemMessage"]
    assert "block" in o3["systemMessage"]


def test_stop_progress_resets_counter(proj):
    work = "run1"
    spine = make_spine([("g1", "in-progress")])
    d = proj / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    sp = str(d / "spine.json")
    (d / "spine.json").write_text(json.dumps(spine), encoding="utf-8")
    journal = d / "spine.json.journal"
    journal.write_text('{"seq":0}\n', encoding="utf-8")
    bind(proj, "s1", sp)

    o1 = sr.decide_stop({"session_id": "s1"}, proj)  # count 1
    o2 = sr.decide_stop({"session_id": "s1"}, proj)  # count 2
    assert o1["decision"] == "block" and o2["decision"] == "block"
    # progress: journal grows -> counter resets, stays a block (not continue)
    journal.write_text('{"seq":0}\n{"seq":1}\n', encoding="utf-8")
    o3 = sr.decide_stop({"session_id": "s1"}, proj)
    assert o3["decision"] == "block"
    assert "continue" not in o3
    nud = sr.load_nudges(proj)["s1"]
    assert nud["count"] == 1  # reset then +1


# --- decide_session_start ----------------------------------------------------

def test_session_start_active_binding_injects_resume(proj):
    spine = make_spine([("g2", "in-progress")], imperatives={"g2": "keep going"})
    sp = write_spine(proj, spine)
    bind(proj, "s1", sp)
    out = sr.decide_session_start({"session_id": "s1", "source": "compact"}, proj)
    hso = out["hookSpecificOutput"]
    assert hso["hookEventName"] == "SessionStart"
    ctx = hso["additionalContext"]
    assert "RESUMING" in ctx
    assert "ENGINE current ->" in ctx
    assert "ACTIVE g2 [in-progress] -- keep going" in ctx
    assert "release" in ctx


def test_session_start_fallback_scan_finds_active(proj):
    spine = make_spine([("g2", "in-progress")])
    write_spine(proj, spine, work="wtX")  # no binding at all
    out = sr.decide_session_start({"session_id": "unbound"}, proj)
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "RESUMING" in out["hookSpecificOutput"]["additionalContext"]


def test_session_start_foreign_skip_same_reinject_fallback_reinject(proj):
    # (c) three-way: a FOREIGN-worktree binding is skipped (no re-inject), a
    # SAME-worktree binding re-injects, and with no binding the _scan_active_spine
    # fallback still re-injects.
    # -- foreign: bound spine lives in the subagent worktree (outside proj/.agent-work)
    sub = proj / "subwt"
    subspine = write_spine(sub, make_spine([("g2", "in-progress")]))
    sr.save_binding(proj, {
        "shared": {"spine": subspine, "engine_session": "eng-1", "worktree": str(sub)}
    })
    out_foreign = sr.decide_session_start({"session_id": "shared", "cwd": str(proj)}, proj)
    assert out_foreign == {}  # foreign -> bound spine skipped, fallback finds none
    # -- same worktree: re-injects
    sp = write_spine(proj, make_spine([("g3", "in-progress")], imperatives={"g3": "keep going"}))
    sr.save_binding(proj, {
        "s1": {"spine": sp, "engine_session": "eng-1", "worktree": str(proj)}
    })
    out_same = sr.decide_session_start({"session_id": "s1", "cwd": str(proj)}, proj)
    assert "RESUMING" in out_same["hookSpecificOutput"]["additionalContext"]
    # -- no binding: fallback scan under proj/.agent-work still re-injects
    out_fallback = sr.decide_session_start({"session_id": "unbound", "cwd": str(proj)}, proj)
    assert "RESUMING" in out_fallback["hookSpecificOutput"]["additionalContext"]


def test_session_start_no_active_spine_returns_empty(proj):
    write_spine(proj, make_spine([("g2", "complete")]))  # all terminal
    assert sr.decide_session_start({"session_id": "s1"}, proj) == {}


def test_session_start_released_lease_returns_empty(proj):
    sp = write_spine(proj, make_spine([("g2", "in-progress")], lease_status="released"))
    bind(proj, "s1", sp)
    assert sr.decide_session_start({"session_id": "s1"}, proj) == {}


# --- handle_post_tool_use ----------------------------------------------------

def _bash(command, session_id="s1", cwd=None):
    data = {"session_id": session_id, "tool_input": {"command": command}}
    if cwd:
        data["cwd"] = cwd
    return data


def test_post_claim_writes_binding(proj):
    cmd = 'py scripts/checklist_engine.py --file .agent-work/run1/spine.json claim --session-id eng-9 --claimed-by commander --worktree .'
    out = sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    assert out == {}
    binding = sr.load_binding(proj)
    assert "s1" in binding
    entry = binding["s1"]
    assert entry["engine_session"] == "eng-9"
    assert entry["spine"].endswith("spine.json")
    assert Path(entry["spine"]).is_absolute()


def test_post_claim_absolute_file_preserved(proj):
    abspath = str(proj / ".agent-work" / "run1" / "spine.json")
    cmd = 'py C:/x/checklist_engine.py --file "%s" claim --session-id eng-2' % abspath
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    assert sr.load_binding(proj)["s1"]["spine"] == abspath


def test_post_release_deletes_binding_and_nudge(proj):
    bind(proj, "s1", str(proj / ".agent-work" / "run1" / "spine.json"))
    sr.save_nudges(proj, {"s1": {"count": 2, "journal_seq": 1, "active_id": "g1"}})
    cmd = 'py scripts/checklist_engine.py --file .agent-work/run1/spine.json release --session-id eng-9'
    out = sr.handle_post_tool_use(_bash(cmd), proj)
    assert out == {}
    assert "s1" not in sr.load_binding(proj)
    assert "s1" not in sr.load_nudges(proj)


def test_post_non_engine_command_ignored(proj):
    out = sr.handle_post_tool_use(_bash("ls -la && git status"), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_engine_non_claim_verb_ignored(proj):
    cmd = 'py scripts/checklist_engine.py --file .agent-work/run1/spine.json advance g1 --session-id eng-9'
    out = sr.handle_post_tool_use(_bash(cmd), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


# --- fail-open / main dispatch ----------------------------------------------

def test_main_malformed_stdin_prints_nothing(proj, capsys):
    rc = sr.main(["spine_rail.py", "Stop"], "{ not json")
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_empty_stdin_prints_nothing(proj, capsys):
    rc = sr.main(["spine_rail.py", "Stop"], "")
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_unknown_event_prints_nothing(proj, capsys):
    rc = sr.main(["spine_rail.py", "Bogus"], '{"session_id":"s1"}')
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_no_argv_event_fail_open(proj, capsys):
    rc = sr.main(["spine_rail.py"], '{"session_id":"s1"}')
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_stop_missing_spine_allows_no_output(proj, capsys):
    bind(proj, "s1", str(proj / ".agent-work" / "gone" / "spine.json"))
    rc = sr.main(["spine_rail.py", "Stop"], '{"session_id":"s1"}')
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_stop_block_emits_json(proj, capsys):
    sp = write_spine(proj, make_spine([("g1", "in-progress")]), journal_lines=1)
    bind(proj, "s1", sp)
    rc = sr.main(["spine_rail.py", "Stop"], '{"session_id":"s1"}')
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["decision"] == "block"


def test_main_post_tool_use_never_errors(proj, capsys):
    rc = sr.main(["spine_rail.py", "PostToolUse"], '{"session_id":"s1","tool_input":{"command":"echo hi"}}')
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_load_binding_corrupt_returns_empty(proj):
    p = sr.binding_path(proj)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{ corrupt", encoding="utf-8")
    assert sr.load_binding(proj) == {}
