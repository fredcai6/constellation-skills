"""Provenance hardening for the eval `spine_completed` process check (issue #127).

The check must demand ENGINE-WRITTEN provenance, not just agent-written JSON state:
a spine passes only when it is the gated `tasks` form with every task complete AND
it carries a plausible `engine_session` lease (monotonic claim -> heartbeat ->
release) AND its evidence matches engine grammar. These tests pin the boundary the
issue names -- fabrication cost above doing-the-work cost -- by proving the genuine
engine shape passes while the cheap fabrication shapes (template copy, stripped
lease, non-monotonic lease, hand-written evidence, bare `{"status": "done"}`) fail.

The check ships identically in every eval scenario; we exercise the euler-1 copy.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK_PATH = ROOT / "evals" / "euler-1-multiples" / "checks" / "spine_completed.py"
TEMPLATE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


chk = load_module("spine_completed_check", CHECK_PATH)


# --------------------------------------------------------------------------- #
# a minimal GENUINE engine-shaped spine (the shape checklist_engine leaves)
# --------------------------------------------------------------------------- #
def genuine_spine() -> dict:
    t0 = datetime(2026, 7, 10, 18, 15, 17, tzinfo=timezone.utc)
    return {
        "work_id": "pe1",
        "type": "gated",
        "items": ["init", "execute"],
        "tasks": {
            "init": {
                "id": "init",
                "status": "complete",
                "preconditions": [],
                "postconditions": [{
                    "id": "c1",
                    "check": {"kind": "command", "command": "py init.py"},
                    "satisfied": True,
                    "satisfied_by": "e-init-1",
                }],
                "status_detail": {},
                "evidence": [{
                    "id": "e-init-1",
                    "type": "command-output",
                    "payload": {"cmd": "py init.py", "exit": 0, "shell": "posix"},
                    "produced_by": "engine",
                    "ts": "",
                }],
                "rework_count": 0,
            },
            "execute": {
                "id": "execute",
                "status": "complete",
                "preconditions": [],
                "postconditions": [{
                    "id": "c1",
                    "check": None,
                    "satisfied": True,
                    "satisfied_by": "attested",
                }],
                "status_detail": {},
                "evidence": [],
                "rework_count": 0,
            },
        },
        "engine_session": {
            "session_id": "cmd-pe1",
            "status": "released",
            "claimed_at": t0.isoformat(),
            "last_heartbeat": (t0 + timedelta(minutes=13)).isoformat(),
            "claimed_by": "commander",
            "worktree": ".",
            "previous_session_id": None,
            "takeover_reason": None,
            "released_at": (t0 + timedelta(minutes=13, seconds=3)).isoformat(),
        },
    }


def write_run_dir(tmp_path: Path, spine: dict, name: str = "run-0") -> Path:
    run_dir = tmp_path / name
    (run_dir / "workspace" / ".agent-work").mkdir(parents=True)
    (run_dir / "workspace" / ".agent-work" / "spine.json").write_text(
        json.dumps(spine), encoding="utf-8"
    )
    return run_dir


# --------------------------------------------------------------------------- #
# genuine engine spine PASSES (positive control)
# --------------------------------------------------------------------------- #
def test_genuine_engine_spine_passes():
    ok, why = chk.spine_has_engine_provenance(genuine_spine())
    assert ok, why


def test_genuine_engine_spine_passes_end_to_end(tmp_path):
    run_dir = write_run_dir(tmp_path, genuine_spine())
    assert chk.main(str(run_dir)) == 0


# --------------------------------------------------------------------------- #
# an ACTIVE (never released) lease still passes -- an honest run fenced by the
# per-run timeout finishes the work but never releases the lease (issue #126).
# --------------------------------------------------------------------------- #
def test_active_unreleased_lease_passes():
    spine = genuine_spine()
    spine["engine_session"]["status"] = "active"
    spine["engine_session"].pop("released_at", None)
    ok, why = chk.spine_has_engine_provenance(spine)
    assert ok, why


# --------------------------------------------------------------------------- #
# fabrication vectors FAIL, each on its intended gate
# --------------------------------------------------------------------------- #
def test_template_copy_all_pending_fails():
    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    ok, why = chk.spine_has_engine_provenance(data)
    assert not ok and "not all tasks" in why


def test_hand_marked_complete_without_lease_fails():
    # The attempt-6 vector: template copy, every step flipped to complete, fake
    # evidence, but no engine_session (the engine never ran `claim`).
    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    for t in data["tasks"].values():
        t["status"] = "complete"
        for c in t.get("postconditions", []) + t.get("preconditions", []):
            c["satisfied"] = True
        t["evidence"] = [{
            "id": "note", "type": "command-output", "payload": {},
            "produced_by": "agent", "ts": "now",
        }]
    ok, why = chk.spine_has_engine_provenance(data)
    assert not ok and "engine_session" in why


def test_stripped_lease_fails():
    spine = genuine_spine()
    spine["engine_session"] = None
    ok, why = chk.spine_has_engine_provenance(spine)
    assert not ok and "engine_session" in why


def test_missing_lease_field_fails():
    spine = genuine_spine()
    del spine["engine_session"]["claimed_by"]
    ok, why = chk.spine_has_engine_provenance(spine)
    assert not ok and "missing" in why


def test_nonmonotonic_lease_fails():
    spine = genuine_spine()
    spine["engine_session"]["last_heartbeat"] = "2026-07-10T00:00:00+00:00"
    ok, why = chk.spine_has_engine_provenance(spine)
    assert not ok and "monotonic" in why


def test_released_before_heartbeat_fails():
    spine = genuine_spine()
    spine["engine_session"]["released_at"] = "2026-07-10T00:00:00+00:00"
    ok, why = chk.spine_has_engine_provenance(spine)
    assert not ok and "monotonic" in why


def test_unparseable_timestamp_fails():
    spine = genuine_spine()
    spine["engine_session"]["claimed_at"] = "yesterday afternoon"
    ok, why = chk.spine_has_engine_provenance(spine)
    assert not ok and "ISO-8601" in why


def test_hand_written_evidence_id_fails():
    spine = genuine_spine()
    spine["tasks"]["init"]["evidence"][0]["id"] = "my-note"
    ok, why = chk.spine_has_engine_provenance(spine)
    assert not ok and "grammar" in why


def test_non_engine_produced_evidence_fails():
    spine = genuine_spine()
    spine["tasks"]["init"]["evidence"][0]["produced_by"] = "agent"
    ok, why = chk.spine_has_engine_provenance(spine)
    assert not ok and "produced_by" in why


def test_command_condition_without_backing_evidence_fails():
    # A satisfied command postcondition whose satisfied_by names no engine record.
    spine = genuine_spine()
    spine["tasks"]["init"]["evidence"] = [{
        "id": "e-init-1", "type": "review-result", "payload": {},
        "produced_by": "engine", "ts": "",
    }]
    ok, why = chk.spine_has_engine_provenance(spine)
    # no engine command-output remains -> caught by that gate.
    assert not ok


def test_bare_status_done_form_fails():
    ok, why = chk.spine_has_engine_provenance({"status": "done"})
    assert not ok


# --------------------------------------------------------------------------- #
# waived engine check (git-change-policy) is honored when a human waiver backs it
# --------------------------------------------------------------------------- #
def test_waived_engine_check_with_human_waiver_passes():
    spine = genuine_spine()
    spine["tasks"]["execute"]["postconditions"] = [{
        "id": "c1",
        "check": {"kind": "git-change-policy", "mode": "staged"},
        "satisfied": True,
        "satisfied_by": "e-execute-1",
        "waived": {"authority": "human", "reason": "no repo"},
    }]
    spine["tasks"]["execute"]["evidence"] = [{
        "id": "e-execute-1", "type": "waiver",
        "payload": {"cond": "c1", "authority": "human"},
        "produced_by": "human", "ts": "",
    }]
    ok, why = chk.spine_has_engine_provenance(spine)
    assert ok, why


def test_waived_engine_check_without_waiver_record_fails():
    spine = genuine_spine()
    spine["tasks"]["execute"]["postconditions"] = [{
        "id": "c1",
        "check": {"kind": "git-change-policy", "mode": "staged"},
        "satisfied": True,
        "satisfied_by": "e-init-1",  # points at a command-output, not a waiver
        "waived": {"authority": "human", "reason": "forged"},
    }]
    ok, why = chk.spine_has_engine_provenance(spine)
    assert not ok and "waiver" in why


# --------------------------------------------------------------------------- #
# journal cross-verification (issue #131) — the journal STRENGTHENS provenance
# where present and is GRANDFATHERED where absent (backward compatible).
# --------------------------------------------------------------------------- #
_T0 = datetime(2026, 7, 10, 18, 15, 17, tzinfo=timezone.utc)


def _jhash(entry: dict) -> str:
    """Re-derive an entry hash exactly as the engine + check do."""
    payload = {k: entry.get(k) for k in
               ("seq", "ts", "session_id", "verb", "task", "evidence_ids", "prev_hash")}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def chain_journal(rows, session_id="cmd-pe1") -> str:
    """Build a valid hash-chained journal from (ts, verb, task, evidence_ids) rows."""
    out, prev = [], ""
    for i, (ts, verb, task, ev) in enumerate(rows):
        e = {"seq": i + 1, "ts": ts, "session_id": session_id, "verb": verb,
             "task": task, "evidence_ids": ev, "prev_hash": prev}
        e["hash"] = _jhash(e)
        prev = e["hash"]
        out.append(json.dumps(e))
    return "\n".join(out) + "\n"


def genuine_rows():
    iso = lambda m: (_T0 + timedelta(minutes=m)).isoformat()
    return [
        (iso(1), "start", "init", []),
        (iso(2), "advance", "init", ["e-init-1"]),   # backs init's command condition
        (iso(3), "start", "execute", []),
        (iso(4), "advance", "execute", []),          # execute is complete too
    ]


def write_spine_and_journal(tmp_path: Path, spine: dict, journal_text: str | None):
    sp = tmp_path / "spine.json"
    sp.write_text(json.dumps(spine), encoding="utf-8")
    if journal_text is not None:
        (tmp_path / "spine.json.journal").write_text(journal_text, encoding="utf-8")
    return sp


def test_journal_absent_is_grandfathered(tmp_path):
    sp = write_spine_and_journal(tmp_path, genuine_spine(), None)
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert ok and "grandfather" in why.lower()


def test_genuine_journal_passes(tmp_path):
    sp = write_spine_and_journal(tmp_path, genuine_spine(), chain_journal(genuine_rows()))
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert ok, why


def test_genuine_journal_passes_end_to_end(tmp_path):
    run_dir = write_run_dir(tmp_path, genuine_spine())
    sp = run_dir / "workspace" / ".agent-work" / "spine.json"
    (run_dir / "workspace" / ".agent-work" / "spine.json.journal").write_text(
        chain_journal(genuine_rows()), encoding="utf-8")
    assert chk.main(str(run_dir)) == 0


def test_journal_present_but_empty_fails(tmp_path):
    sp = write_spine_and_journal(tmp_path, genuine_spine(), "")
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert not ok and "empty" in why


def test_journal_tampered_hash_fails(tmp_path):
    text = chain_journal(genuine_rows())
    lines = text.strip().splitlines()
    e = json.loads(lines[1]); e["verb"] = "record"  # change a field, leave stale hash
    lines[1] = json.dumps(e)
    sp = write_spine_and_journal(tmp_path, genuine_spine(), "\n".join(lines) + "\n")
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert not ok and "re-derive" in why


def test_journal_broken_chain_fails(tmp_path):
    text = chain_journal(genuine_rows())
    lines = text.strip().splitlines()
    e = json.loads(lines[1]); e["prev_hash"] = "0" * 64; e["hash"] = _jhash(e)
    lines[1] = json.dumps(e)
    sp = write_spine_and_journal(tmp_path, genuine_spine(), "\n".join(lines) + "\n")
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert not ok and "hash-chain" in why


def test_journal_seq_out_of_order_fails(tmp_path):
    text = chain_journal(genuine_rows())
    lines = text.strip().splitlines()
    e = json.loads(lines[1]); e["seq"] = 5; e["hash"] = _jhash(e)
    lines[1] = json.dumps(e)
    sp = write_spine_and_journal(tmp_path, genuine_spine(), "\n".join(lines) + "\n")
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert not ok and "seq" in why


def test_journal_non_monotonic_ts_fails(tmp_path):
    rows = genuine_rows()
    rows[3] = (_T0.isoformat(), "advance", "execute", [])  # earlier than prior rows
    sp = write_spine_and_journal(tmp_path, genuine_spine(), chain_journal(rows))
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert not ok and "monotonic" in why


def test_journal_ts_outside_lease_fails(tmp_path):
    rows = genuine_rows()
    # push the last advance PAST the lease release (t0 + 13m3s)
    rows[3] = ((_T0 + timedelta(minutes=30)).isoformat(), "advance", "execute", [])
    sp = write_spine_and_journal(tmp_path, genuine_spine(), chain_journal(rows))
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert not ok and "release" in why


def test_journal_missing_advance_for_complete_task_fails(tmp_path):
    rows = [r for r in genuine_rows() if not (r[1] == "advance" and r[2] == "execute")]
    sp = write_spine_and_journal(tmp_path, genuine_spine(), chain_journal(rows))
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert not ok and "no advance/record" in why


def test_journal_unreferenced_engine_evidence_fails(tmp_path):
    rows = genuine_rows()
    rows[1] = (rows[1][0], "advance", "init", [])  # drop e-init-1 reference
    sp = write_spine_and_journal(tmp_path, genuine_spine(), chain_journal(rows))
    ok, why = chk.journal_consistent(sp, genuine_spine())
    assert not ok and "not referenced by any journal entry" in why
