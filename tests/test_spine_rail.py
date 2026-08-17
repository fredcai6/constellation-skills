"""Unit tests for scripts/hooks/spine_rail.py.

Every decision branch is exercised through the pure/handler functions with
constructed spine fixtures. No subprocess of the engine; state-file facts only
-- with ONE deliberate exception (lesson:verify-harness-field-and-drive-real-
writer, #261): test_session_start_real_engine_claim_produces_real_binding_
diff below DOES subprocess the real scripts/checklist_engine.py to produce a
genuinely engine-claimed spine, specifically so the bind-on-resume write path
is proven against production machinery, not a hand-built fixture.
"""

import errno
import hashlib
import importlib.util
import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]

# Import the hook module directly from its file path (it is not on a package).
_MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "hooks" / "spine_rail.py"
_spec = importlib.util.spec_from_file_location("spine_rail", _MODULE_PATH)
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)


def _spawn_claim_writer(project_dir, spine_path, writer_index, barrier):
    """Picklable production-topology worker for #441's lost-update proof."""
    barrier.wait(timeout=30)
    command = (
        'python scripts/checklist_engine.py --file "%s" claim '
        '--session-id engine-%d --claimed-by implementer'
        % (spine_path, writer_index)
    )
    sr.handle_post_tool_use(
        {
            "session_id": "spawn-shared",
            "agent_id": "writer-%d" % writer_index,
            "cwd": str(project_dir),
            "tool_input": {"command": command},
        },
        Path(project_dir),
    )


def _spawn_session_start_writer(project_dir, session_id, barrier):
    """Picklable production-topology worker for #441 m3's SessionStart-versus-
    claim mixed-writer race proof."""
    barrier.wait(timeout=30)
    sr.decide_session_start({"session_id": session_id, "cwd": str(project_dir)}, Path(project_dir))


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


def bind(project_dir, sid, spine_path, engine_session="eng-1", worktree=None):
    """Write a NEW-shape binding: one nested entry, keyed by spine_path, for
    `sid`. Merges onto any existing bindings for `sid` (mirrors the real
    claim writer's leave-siblings-untouched behavior) rather than clobbering."""
    binding = sr.load_binding(project_dir)
    sid_bindings = dict(binding.get(sid) or {})
    sid_bindings[str(spine_path)] = {
        "spine": str(spine_path),
        "engine_session": engine_session,
        "worktree": worktree if worktree is not None else str(project_dir),
        "claimed_at": "2026-07-27T00:00:00+00:00",
    }
    binding[sid] = sid_bindings
    sr.save_binding(project_dir, binding)


@pytest.fixture
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    return tmp_path


# --- the real captured hook payloads (#419) ----------------------------------
#
# Six payloads captured from a REAL headless `claude -p` run on harness 2.1.222
# (a parent Bash call, two concurrent subagents each running a Bash call, a
# second parent Bash call, and the parent's own Agent-tool dispatch calls).
# They are pinned here so a later hand-edit fails the suite instead of silently
# weakening every test built on them -- the whole unit layer below is a check
# over real harness output, not over a dict someone typed.

_PROBE_FIXTURE = _REPO_ROOT / "tests" / "fixtures" / "probe_payloads.jsonl"

# sha256 of the fixture's NEWLINE-NORMALIZED bytes, and that normalized length.
# Normalized, never raw: `.gitattributes` sets `* text=auto`, so the working
# tree legitimately holds CRLF while the blob holds LF, and a raw working-tree
# byte hash is silently wrong on Windows (docs/agents/CREW_CONTEXT.md).
_PROBE_FIXTURE_SHA256 = "b03536865c8c0215939346447ebd196c579cf051228aa5a9bb75898c10a37402"
_PROBE_FIXTURE_NORMALIZED_BYTES = 13155


def _probe_wrappers():
    """Every line of the pinned capture as the probe's CAPTURE WRAPPER dict
    ({captured_at, cwd, env, env_claude_keys, pid, raw, raw_len, payload})."""
    text = _PROBE_FIXTURE.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def probe_payloads():
    """The real hook payloads, UNWRAPPED out of the capture wrapper's `payload`
    key. Every test built on the capture goes through here: the wrapper is the
    probe's own envelope and carries no `agent_id` at its top level, so reading
    a wrapper as if it were a payload would test nothing that ships."""
    return [w["payload"] for w in _probe_wrappers()]


def test_probe_fixture_sha256_pin():
    """Pin the fixture's content. If someone hand-edits the capture -- adding a
    convenient agent_id, say -- this fails first and loudly, instead of every
    downstream test quietly proving something about invented input."""
    assert _PROBE_FIXTURE.exists(), "pinned capture missing: %s" % _PROBE_FIXTURE
    norm = _PROBE_FIXTURE.read_bytes().replace(b"\r\n", b"\n")
    digest = hashlib.sha256(norm).hexdigest()
    print("\nprobe_payloads.jsonl normalized bytes = %d, sha256 = %s" % (len(norm), digest))
    assert len(norm) == _PROBE_FIXTURE_NORMALIZED_BYTES
    assert digest == _PROBE_FIXTURE_SHA256, (
        "pinned capture changed: expected %s, got %s" % (_PROBE_FIXTURE_SHA256, digest)
    )


def test_probe_fixture_decomposition():
    """State what the capture actually holds, measured here rather than
    inherited from prose. Printed so the counts land in the evidence."""
    wrappers = _probe_wrappers()
    payloads = probe_payloads()
    assert len(wrappers) == 6
    assert len(payloads) == 6
    # wrapper != payload: `agent_id` exists only INSIDE `payload`.
    assert all("payload" in w for w in wrappers)
    assert not any("agent_id" in w for w in wrappers)

    sids = {p.get("session_id") for p in payloads}
    assert len(sids) == 1, "the whole capture is ONE harness session_id: %r" % sids

    subagent = [p for p in payloads if "agent_id" in p]
    parent_bash = [p for p in payloads
                   if "agent_id" not in p and p.get("tool_name") == "Bash"]
    parent_dispatch = [p for p in payloads
                       if "agent_id" not in p and p.get("tool_name") == "Agent"]

    print("probe decomposition: %d parent Bash / %d subagent-scope / %d parent Agent-dispatch"
          % (len(parent_bash), len(subagent), len(parent_dispatch)))
    print("subagent agent_ids: %s" % sorted(p["agent_id"] for p in subagent))

    # Measured, and it is NOT the 3/2/1 the handoff offered provisionally.
    assert (len(parent_bash), len(subagent), len(parent_dispatch)) == (2, 2, 2)
    assert len(parent_bash) + len(subagent) + len(parent_dispatch) == len(payloads)
    assert len({p["agent_id"] for p in subagent}) == 2  # distinct ids, one per agent
    assert all(p.get("agent_type") == "general-purpose" for p in subagent)
    assert all(p.get("agent_id") and isinstance(p["agent_id"], str) for p in subagent)


# --- binding_key: the per-agent outer key (#419) -----------------------------

_ABSENT = object()


def _derive(payload, **overrides):
    """Derive an adversarial row by MUTATING a real captured payload.

    This is not the forbidden hand-injection: these rows prove REJECTION, never
    delivery. They are necessary because the real capture holds zero malformed
    agent_ids and zero falsy session_ids, so the reject branch is unreachable
    from unmutated capture alone.
    """
    row = dict(payload)
    for key, value in overrides.items():
        if value is _ABSENT:
            row.pop(key, None)
        else:
            row[key] = value
    return row


def test_binding_key_composition_table_over_the_six_real_payloads():
    payloads = probe_payloads()
    assert len(payloads) == 6
    bare, composite = [], []
    for p in payloads:
        key = sr.binding_key(p)
        sid = p["session_id"]
        if "agent_id" in p:
            assert key == sid + sr.BINDING_KEY_SEP + p["agent_id"]
            composite.append(key)
        else:
            assert key == sid  # top-level agent: bare key, behavior unchanged
            bare.append(key)
        print("  %-6s agent_id=%-18r -> %r"
              % (p.get("tool_name"), p.get("agent_id"), key))
    print("composition table: %d bare / %d composite over %d real payloads"
          % (len(bare), len(composite), len(payloads)))
    assert len(bare) == 4
    assert len(composite) == 2
    assert len(set(bare)) == 1          # one parent session
    assert len(set(composite)) == 2     # two agents -> two independent keys
    assert set(bare).isdisjoint(set(composite))
    assert all(k.startswith(bare[0] + sr.BINDING_KEY_SEP) for k in composite)


def test_binding_key_rejects_unusable_agent_ids_derived_from_real_payloads():
    """Fail closed. Every row below is a real captured payload with ONE field
    mutated; each must bind NOTHING rather than fall back to the bare key."""
    real_sub = [p for p in probe_payloads() if "agent_id" in p][0]
    real_parent = [p for p in probe_payloads() if "agent_id" not in p][0]
    # Positive controls: the unmutated bases are usable, so a None below is
    # caused by the mutation and not by the base payload.
    assert sr.binding_key(real_sub) == real_sub["session_id"] + "#" + real_sub["agent_id"]
    assert sr.binding_key(real_parent) == real_parent["session_id"]

    rows = [
        ("empty agent_id", _derive(real_sub, agent_id="")),
        ("null agent_id", _derive(real_sub, agent_id=None)),
        ("int agent_id", _derive(real_sub, agent_id=12345)),
        ("dict agent_id", _derive(real_sub, agent_id={"id": "a8f0a946eaaa2fe6c"})),
        ("separator in agent_id", _derive(real_sub, agent_id="a8f0a946eaaa2fe6c#b")),
        ("forward slash in agent_id", _derive(real_sub, agent_id="a8f0a946/eaaa2fe6c")),
        ("backslash in agent_id", _derive(real_sub, agent_id="a8f0a946\\eaaa2fe6c")),
        ("parent traversal in agent_id", _derive(real_sub, agent_id="../../a8f0a946")),
        ("empty session_id, subagent", _derive(real_sub, session_id="")),
        ("missing session_id, subagent", _derive(real_sub, session_id=_ABSENT)),
        ("empty session_id, parent", _derive(real_parent, session_id="")),
        ("missing session_id, parent", _derive(real_parent, session_id=_ABSENT)),
    ]
    for label, row in rows:
        assert sr.binding_key(row) is None, "%s should bind nothing" % label
        print("  rejected: %s" % label)
    print("adversarial rows derived from real payloads and rejected: %d" % len(rows))
    assert len(rows) >= 6


def test_binding_key_never_raises_on_junk():
    # The hook must never raise; a key it cannot compose is None, not an error.
    assert sr.binding_key({}) is None
    assert sr.binding_key(None) is None
    assert sr.binding_key({"session_id": None}) is None


# --- write routing: claim / release / cleanup key off binding_key (#419) -----

def _real_post_tool_use(payload, command, cwd):
    """A PostToolUse payload built from a REAL captured payload: its own
    session_id, and its own agent_id or the genuine ABSENCE of one, preserved
    verbatim from the capture. Only `tool_input` and `cwd` are swapped, for the
    engine command whose effect is under test. No agent_id is ever invented
    here -- the point is that the harness delivers it."""
    data = dict(payload)
    data["tool_input"] = {"command": command}
    data["cwd"] = str(cwd)
    return data


def _claim_cmd(work, engine_session):
    return ('py scripts/checklist_engine.py --file .agent-work/%s/spine.json '
            'claim --session-id %s --claimed-by commander' % (work, engine_session))


def _release_cmd(work, engine_session):
    return ('py scripts/checklist_engine.py --file .agent-work/%s/spine.json '
            'release --session-id %s' % (work, engine_session))


def _abs_spine(proj, work):
    return str((proj / ".agent-work" / work / "spine.json").resolve())


def _real_parent_payloads():
    return [p for p in probe_payloads() if "agent_id" not in p]


def _real_subagent_payloads():
    return [p for p in probe_payloads() if "agent_id" in p]


def test_post_claim_subagent_writes_composite_key_bare_set_byte_identical(proj):
    """A claim carrying agent_id files under sid#agent_id and leaves the bare
    sid entry set byte-identical -- the parent's gauge candidate count is
    unchanged, which is the whole point of the re-key."""
    parent = _real_parent_payloads()[0]
    sub = _real_subagent_payloads()[0]
    sid = parent["session_id"]
    assert sub["session_id"] == sid  # the shared session_id that caused the pile-up

    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-parent")
    put_checklist(proj, "run-sub")
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("run-parent", "eng-parent"), proj), proj)
    bare_before = json.dumps(sr.load_binding(proj)[sid], sort_keys=True)

    out = sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("run-sub", "eng-sub"), proj), proj)
    assert out == {}  # PostToolUse never blocks

    binding = sr.load_binding(proj)
    composite = sid + sr.BINDING_KEY_SEP + sub["agent_id"]
    assert set(binding.keys()) == {sid, composite}
    assert json.dumps(binding[sid], sort_keys=True) == bare_before  # untouched
    assert list(binding[sid].keys()) == [_abs_spine(proj, "run-parent")]
    assert list(binding[composite].keys()) == [_abs_spine(proj, "run-sub")]
    assert binding[composite][_abs_spine(proj, "run-sub")]["engine_session"] == "eng-sub"


def test_post_claim_two_agent_ids_give_two_independent_key_sets(proj):
    """Two distinct agent_ids on ONE session_id produce two independent key
    sets -- exactly the case that used to collapse into one ambiguous key."""
    sub_a, sub_b = _real_subagent_payloads()
    sid = sub_a["session_id"]
    assert sub_a["agent_id"] != sub_b["agent_id"]

    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-a")
    put_checklist(proj, "run-b")
    sr.handle_post_tool_use(_real_post_tool_use(sub_a, _claim_cmd("run-a", "eng-a"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(sub_b, _claim_cmd("run-b", "eng-b"), proj), proj)

    binding = sr.load_binding(proj)
    key_a = sid + sr.BINDING_KEY_SEP + sub_a["agent_id"]
    key_b = sid + sr.BINDING_KEY_SEP + sub_b["agent_id"]
    assert set(binding.keys()) == {key_a, key_b}
    assert sid not in binding  # nothing piled under the bare parent key
    assert list(binding[key_a].keys()) == [_abs_spine(proj, "run-a")]
    assert list(binding[key_b].keys()) == [_abs_spine(proj, "run-b")]
    # Each key holds exactly ONE candidate -- the gauge writer's ambiguity test.
    assert [len(v) for v in binding.values()] == [1, 1]


def test_post_release_composite_removes_only_that_agents_entry(proj):
    """A release carrying agent_id removes only that agent's entry: the other
    agent's key set and the parent's bare key set both survive."""
    sub_a, sub_b = _real_subagent_payloads()
    parent = _real_parent_payloads()[0]
    sid = parent["session_id"]
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-parent")
    put_checklist(proj, "run-a")
    put_checklist(proj, "run-b")
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("run-parent", "eng-parent"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(sub_a, _claim_cmd("run-a", "eng-a"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(sub_b, _claim_cmd("run-b", "eng-b"), proj), proj)
    assert len(sr.load_binding(proj)) == 3

    out = sr.handle_post_tool_use(_real_post_tool_use(sub_a, _release_cmd("run-a", "eng-a"), proj), proj)
    assert out == {}

    binding = sr.load_binding(proj)
    key_a = sid + sr.BINDING_KEY_SEP + sub_a["agent_id"]
    key_b = sid + sr.BINDING_KEY_SEP + sub_b["agent_id"]
    assert set(binding.keys()) == {sid, key_b}
    assert key_a not in binding
    assert list(binding[sid].keys()) == [_abs_spine(proj, "run-parent")]
    assert list(binding[key_b].keys()) == [_abs_spine(proj, "run-b")]


def test_post_release_composite_leaves_bare_nudge_ledger_untouched(proj):
    """The nudge / three-strike escape-hatch ledger stays keyed by the BARE
    session_id, so a subagent's release must not clear the parent's strikes."""
    sub = _real_subagent_payloads()[0]
    sid = sub["session_id"]
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-sub")
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("run-sub", "eng-sub"), proj), proj)
    sr.save_nudges(proj, {sid: {"count": 2, "journal_seq": 7, "active_id": ["g1"]}})

    sr.handle_post_tool_use(_real_post_tool_use(sub, _release_cmd("run-sub", "eng-sub"), proj), proj)

    nudges = sr.load_nudges(proj)
    assert nudges[sid] == {"count": 2, "journal_seq": 7, "active_id": ["g1"]}


def test_post_release_parent_still_clears_its_own_bare_nudge_ledger(proj):
    """The other half of the same rule: a top-level release still clears the
    bare-keyed ledger, so the pre-#419 behavior is intact."""
    parent = _real_parent_payloads()[0]
    sid = parent["session_id"]
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-parent")
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("run-parent", "eng-p"), proj), proj)
    sr.save_nudges(proj, {sid: {"count": 2, "journal_seq": 7, "active_id": ["g1"]}})

    sr.handle_post_tool_use(_real_post_tool_use(parent, _release_cmd("run-parent", "eng-p"), proj), proj)
    assert sid not in sr.load_nudges(proj)


def test_post_claim_unusable_agent_id_writes_no_binding_anywhere(proj):
    """An unresolved identity binds NOTHING -- not under a composite key, and
    above all not under the parent's bare key, which is where a two-way
    fallback would have silenced the parent's gauge."""
    sub = _real_subagent_payloads()[0]
    parent = _real_parent_payloads()[0]
    sid = parent["session_id"]
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-parent")
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("run-parent", "eng-p"), proj), proj)
    before = json.dumps(sr.load_binding(proj), sort_keys=True)

    for bad in ("", None, 12345, "a8f0#b", "a8f0/b", "a8f0\\b", "../a8f0"):
        payload = _real_post_tool_use(
            _derive(sub, agent_id=bad), _claim_cmd("run-bad", "eng-bad"), proj)
        assert sr.handle_post_tool_use(payload, proj) == {}

    after = sr.load_binding(proj)
    assert json.dumps(after, sort_keys=True) == before  # nothing written at all
    assert set(after.keys()) == {sid}
    assert list(after[sid].keys()) == [_abs_spine(proj, "run-parent")]
    assert _abs_spine(proj, "run-bad") not in after[sid]


def test_post_release_empty_set_cleanup_deletes_composite_key_not_bare(proj):
    """The single line where a wrong substitution deletes a live parent's whole
    binding. Parent and subagent both hold an entry for the SAME spine path
    under different keys; the subagent's release empties ITS key set, and the
    cleanup must delete that composite key while the bare key's entries stay."""
    parent = _real_parent_payloads()[0]
    sub = _real_subagent_payloads()[0]
    sid = parent["session_id"]
    composite = sid + sr.BINDING_KEY_SEP + sub["agent_id"]

    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "shared-run")
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("shared-run", "eng-p"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("shared-run", "eng-s"), proj), proj)
    binding = sr.load_binding(proj)
    assert set(binding.keys()) == {sid, composite}
    assert list(binding[sid].keys()) == list(binding[composite].keys()) == [_abs_spine(proj, "shared-run")]
    parent_entry_before = json.dumps(binding[sid], sort_keys=True)

    sr.handle_post_tool_use(_real_post_tool_use(sub, _release_cmd("shared-run", "eng-s"), proj), proj)

    after = sr.load_binding(proj)
    assert composite not in after            # emptied key set removed
    assert set(after.keys()) == {sid}        # bare key survives
    assert json.dumps(after[sid], sort_keys=True) == parent_entry_before


# --- read routing: session_view merges bare + composite keys (#419) ----------

def test_session_view_merges_one_bare_and_two_composite_keys(proj):
    """The settle a cold critic flagged as otherwise vacuous: on a store with
    ONLY bare keys the merge is the identity function, so it would pass in
    exactly the world where session_view ignores composite keys. This store
    holds one bare key and TWO composite keys, written by the real claim
    writer from real payloads, plus two decoy keys that must NOT be merged."""
    parent = _real_parent_payloads()[0]
    sub_a, sub_b = _real_subagent_payloads()
    sid = parent["session_id"]
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-parent")
    put_checklist(proj, "run-a")
    put_checklist(proj, "run-b")
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("run-parent", "eng-p"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(sub_a, _claim_cmd("run-a", "eng-a"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(sub_b, _claim_cmd("run-b", "eng-b"), proj), proj)

    # Decoys: a different session's composite key, and a key that merely starts
    # with the sid but is not a child of it (no separator) -- the prefix test
    # must be sid + BINDING_KEY_SEP, not a bare startswith.
    binding = sr.load_binding(proj)
    decoy_entry = {
        "C:/decoy/spine.json": {
            "spine": "C:/decoy/spine.json", "engine_session": "eng-decoy",
            "worktree": "C:/decoy", "claimed_at": "2026-08-05T00:00:00+00:00",
        }
    }
    binding["other-session#a8f0a946eaaa2fe6c"] = dict(decoy_entry)
    binding[sid + "-lookalike"] = dict(decoy_entry)
    sr.save_binding(proj, binding)

    binding = sr.load_binding(proj)
    key_a = sid + sr.BINDING_KEY_SEP + sub_a["agent_id"]
    key_b = sid + sr.BINDING_KEY_SEP + sub_b["agent_id"]
    assert set(binding.keys()) == {sid, key_a, key_b,
                                   "other-session#a8f0a946eaaa2fe6c", sid + "-lookalike"}

    view = sr.session_view(binding, sid)
    print("\nstore keys = %d (1 bare + 2 composite + 2 decoy); merged view entries = %d"
          % (len(binding), len(view)))
    assert len(view) == 3
    assert set(view.keys()) == {
        _abs_spine(proj, "run-parent"), _abs_spine(proj, "run-a"), _abs_spine(proj, "run-b")
    }
    assert "C:/decoy/spine.json" not in view
    # An unknown / falsy sid sees nothing, and the call never raises.
    assert sr.session_view(binding, "no-such-session") == {}
    assert sr.session_view(binding, None) == {}
    assert sr.session_view({}, sid) == {}


# --- _session_keys: the shared seam session_view and session_view_provenance
# --- both fold over (#549) --------------------------------------------------

def test_session_keys_bare_only():
    binding = {"sid-1": {"path/a": {}}, "other": {"path/b": {}}}
    assert sr._session_keys(binding, "sid-1") == ["sid-1"]


def test_session_keys_composite_only():
    binding = {"sid-1#agent-a": {"path/a": {}}, "sid-1#agent-b": {"path/b": {}}}
    assert sr._session_keys(binding, "sid-1") == ["sid-1#agent-a", "sid-1#agent-b"]


def test_session_keys_mixed_preserves_binding_iteration_order():
    """Bare + composite + decoys (a different session's composite key, and a
    key that merely starts with sid but lacks the separator) -- order matches
    the dict's own insertion order, decoys excluded."""
    binding = {
        "sid-1#agent-b": {"x": {}},
        "sid-1": {"y": {}},
        "other#agent-a": {"z": {}},
        "sid-1-lookalike": {"w": {}},
        "sid-1#agent-a": {"v": {}},
    }
    assert sr._session_keys(binding, "sid-1") == ["sid-1#agent-b", "sid-1", "sid-1#agent-a"]


def test_session_keys_empty_or_none_sid_never_raises():
    binding = {"sid-1": {"path/a": {}}}
    assert sr._session_keys(binding, "") == []
    assert sr._session_keys(binding, None) == []
    assert sr._session_keys({}, "sid-1") == []
    assert sr._session_keys(None, "sid-1") == []


# --- session_view_provenance: which key sourced each visible path (#549) ----

def test_session_view_provenance_bare_only():
    binding = {"sid-1": {"path/a": {"spine": "path/a"}}}
    assert sr.session_view_provenance(binding, "sid-1") == {"path/a": "sid-1"}


def test_session_view_provenance_composite_only():
    binding = {
        "sid-1#agent-a": {"path/a": {"spine": "path/a"}},
        "sid-1#agent-b": {"path/b": {"spine": "path/b"}},
    }
    owners = sr.session_view_provenance(binding, "sid-1")
    assert owners == {"path/a": "sid-1#agent-a", "path/b": "sid-1#agent-b"}


def test_session_view_provenance_mixed_matches_session_view_keys(proj):
    """Reuses the same real-claim-writer fixture shape as
    test_session_view_merges_one_bare_and_two_composite_keys: the provenance
    map's key set must equal session_view's, and never disagree about what's
    visible to sid -- both fold over the same _session_keys list."""
    parent = _real_parent_payloads()[0]
    sub_a, sub_b = _real_subagent_payloads()
    sid = parent["session_id"]
    put_checklist(proj, "run-parent")
    put_checklist(proj, "run-a")
    put_checklist(proj, "run-b")
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("run-parent", "eng-p"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(sub_a, _claim_cmd("run-a", "eng-a"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(sub_b, _claim_cmd("run-b", "eng-b"), proj), proj)

    binding = sr.load_binding(proj)
    key_a = sid + sr.BINDING_KEY_SEP + sub_a["agent_id"]
    key_b = sid + sr.BINDING_KEY_SEP + sub_b["agent_id"]

    view = sr.session_view(binding, sid)
    owners = sr.session_view_provenance(binding, sid)
    assert set(owners.keys()) == set(view.keys())
    assert owners[_abs_spine(proj, "run-parent")] == sid
    assert owners[_abs_spine(proj, "run-a")] == key_a
    assert owners[_abs_spine(proj, "run-b")] == key_b


def test_session_view_provenance_last_key_wins_on_path_collision():
    """Matches session_view's own dict.update overwrite semantics: when two
    keys in _session_keys order both carry the same path, the later key's
    owner wins."""
    binding = {
        "sid-1": {"shared/path": {"spine": "shared/path"}},
        "sid-1#agent-a": {"shared/path": {"spine": "shared/path"}},
    }
    owners = sr.session_view_provenance(binding, "sid-1")
    assert owners["shared/path"] == "sid-1#agent-a"


def test_session_view_provenance_empty_or_falsy_never_raises():
    binding = {"sid-1": {"path/a": {"spine": "path/a"}}}
    assert sr.session_view_provenance(binding, "") == {}
    assert sr.session_view_provenance(binding, None) == {}
    assert sr.session_view_provenance({}, "sid-1") == {}
    assert sr.session_view_provenance(None, "sid-1") == {}


def test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key(proj):
    """The parent's bare key holds nothing mid-flight; the only mid-flight
    spine is bound under a SUBAGENT's composite key. Before the read routing
    this Stop was allowed (the bare key looked idle), which is exactly the
    silence being fixed."""
    parent = _real_parent_payloads()[0]
    sub = _real_subagent_payloads()[0]
    sid = parent["session_id"]

    write_spine(proj, make_spine([("g1", "complete")], lease_status="released"), work="run-parent")
    write_spine(proj, make_spine([("g9", "in-progress")], imperatives={"g9": "COMPOSITE-MARKER keep going"}),
                work="run-sub", journal_lines=1)
    # Sub claims FIRST (#441): each writer transaction safe-reaps released
    # entries already on disk BEFORE its own mutation, so claiming the
    # released run-parent binding second (fresh, past that reap) is what
    # keeps it present for this test's own read below.
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("run-sub", "eng-s"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("run-parent", "eng-p"), proj), proj)

    binding = sr.load_binding(proj)
    assert len(binding) == 2
    assert list(binding[sid].keys()) == [_abs_spine(proj, "run-parent")]

    out = sr.decide_stop({"session_id": sid, "cwd": str(proj)}, proj)
    assert out["decision"] == "block"
    owner_key = sid + sr.BINDING_KEY_SEP + sub["agent_id"]
    # #549: the reason/context must NOT render the sub's own next imperative
    # into the PARENT's Stop-block -- that reads as an instruction for the
    # parent to go execute a gate that is not its own to drive. Still blocked
    # (the #419 fix stays intact), but the owning composite key/agent id
    # appears instead of the imperative text.
    assert "COMPOSITE-MARKER" not in out["reason"]
    assert "COMPOSITE-MARKER" not in out["hookSpecificOutput"]["additionalContext"]
    assert owner_key in out["reason"]
    # Strikes still accrue under the BARE sid -- the hatch is not fragmented.
    assert list(sr.load_nudges(proj).keys()) == [sid]


def test_stop_bare_sid_owned_mid_flight_still_renders_original_imperative_text(proj):
    """Control: an ordinary same-session mid-flight entry -- reachable through
    the BARE sid key, no subordinate involved -- must keep rendering the
    original imperative-bearing _mid_flight_reason text unchanged. Proves
    #549's fix is scoped to per-agent-key-only entries, never a blanket
    reword of every Stop-block."""
    parent = _real_parent_payloads()[0]
    sid = parent["session_id"]

    write_spine(proj, make_spine([("g1", "in-progress")], imperatives={"g1": "BARE-MARKER keep going"}),
                work="run-parent", journal_lines=1)
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("run-parent", "eng-p"), proj), proj)

    binding = sr.load_binding(proj)
    assert list(binding.keys()) == [sid]

    out = sr.decide_stop({"session_id": sid, "cwd": str(proj)}, proj)
    assert out["decision"] == "block"
    assert "g1" in out["reason"]
    assert "BARE-MARKER" in out["reason"]
    assert "BARE-MARKER" in out["hookSpecificOutput"]["additionalContext"]
    assert list(sr.load_nudges(proj).keys()) == [sid]


def test_session_start_reads_through_to_a_composite_key_but_answers_only_its_owner(proj):
    """decide_session_start's read goes through session_view too -- #419's
    read-through, which this asserts directly: the entry IS visible to the
    session and provenance attributes it to the composite key.

    What CHANGED (#609 lane F g3): being visible is not being yours. A bare
    SessionStart is the top-level agent restarting, and handing it a spine its
    SUBAGENT claimed is #549/#419's own failure -- "pick the run back up at this
    gate", about someone else's gate. It used to depend on where the payload
    was standing: same tree as the recorded worktree and the entry was resumed,
    different tree and it was skipped. Selection is the binding key now, so the
    answer is the same from anywhere, and the agent that DID claim it is still
    answered with it. The spine lives outside proj/.agent-work so the fallback
    scan cannot find it -- the only route to it is the composite key.

    This test asserted the opposite until #609 lane F g3. It is not weakened:
    it makes the same read-through claim, plus the ownership claim, plus the
    round trip that shows nothing became unreachable."""
    sub = _real_subagent_payloads()[0]
    sid = sub["session_id"]
    composite = sid + sr.BINDING_KEY_SEP + sub["agent_id"]
    alt = proj / "altwt"
    sp = write_spine(alt, make_spine([("g4", "in-progress")], imperatives={"g4": "COMPOSITE-RESUME keep going"}),
                     work="run-sub")
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("run-sub", "eng-s"), alt), proj)

    binding = sr.load_binding(proj)
    assert list(binding.keys()) == [composite]
    assert list(sr.session_view(binding, sid)) == [sp]              # read-through intact
    assert sr.session_view_provenance(binding, sid)[sp] == composite  # and attributed
    assert sr._scan_active_spine(proj) == []  # nothing for the fallback to find

    # The top-level agent restarting: visible, not its own, so not its gate.
    bare = sr.decide_session_start({"session_id": sid, "cwd": str(alt), "source": "resume"}, proj)
    assert bare == {}

    # The agent that claimed it is still answered with it, from the same tree
    # and by the same route -- the entry did not become unreachable.
    own = sr.decide_session_start(
        {"session_id": sid, "agent_id": sub["agent_id"], "cwd": str(alt), "source": "resume"}, proj)
    ctx = own["hookSpecificOutput"]["additionalContext"]
    assert "RESUMING" in ctx
    assert "COMPOSITE-RESUME" in ctx


def test_session_start_withholds_a_composite_key_imperative_from_the_bare_session(proj):
    """#549's concern -- one agent being handed another's next imperative --
    reaching decide_session_start (#609 lane F g3). decide_stop answers a
    foreign-owned gate with the foreign-owner wording, because the stop blocks
    whatever it renders; this site has no such obligation, so it says nothing
    at all and the imperative appears in NEITHER field.

    Until #609 lane F g3 this asserted that the imperative rendered in full,
    guarding #549's fence around a site that was then out of scope. The fence
    is gone; the concern it was fencing now applies here too."""
    sub = _real_subagent_payloads()[0]
    sid = sub["session_id"]
    alt = proj / "altwt2"
    write_spine(alt, make_spine([("g7", "in-progress")], imperatives={"g7": "REGRESSION-MARKER keep going"}),
                work="run-sub2")
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("run-sub2", "eng-s2"), alt), proj)

    binding = sr.load_binding(proj)
    assert list(binding.keys()) == [sid + sr.BINDING_KEY_SEP + sub["agent_id"]]

    out = sr.decide_session_start({"session_id": sid, "cwd": str(alt), "source": "resume"}, proj)
    assert out == {}
    assert "REGRESSION-MARKER" not in json.dumps(out)  # neither field, nowhere
    assert "g7" not in json.dumps(out)


def test_session_start_bind_on_resume_still_writes_under_the_bare_key(proj):
    """SessionStart never carries an agent_id, so a resumed session is by
    definition top-level: the bind-on-unambiguous-scan write must land under
    the BARE session_id, never under a composite one, and it must leave a
    sibling composite key alone. Both entries are claimed by the real writer,
    so their `claimed_at` is fresh and the reaper retains them once their
    targets vanish.

    Both bound targets are made UNREADABLE so the existing-binding read finds
    nothing to resume from and the scan path is actually reached. The session's
    OWN entry is what has to be unreadable for that: an arrangement where the
    only visible entry is the SUBAGENT's -- which is what this test used to
    build -- no longer reaches the scan at all, because a session that owns
    none of what it can see is now withheld from rather than bound to whatever
    the glob turns up (#609 lane F g3; that arrangement is pinned in
    `OwnershipIsBindingKeyNotWorktree` as the behaviour it now gets). Owning an
    entry whose spine has been deleted or archived out from under it is the
    shape that still belongs here, and it is the realistic one."""
    parent = _real_parent_payloads()[0]
    sub = _real_subagent_payloads()[0]
    sid = sub["session_id"]
    assert parent["session_id"] == sid  # one harness session
    composite = sid + sr.BINDING_KEY_SEP + sub["agent_id"]
    alt, own = proj / "altwt", proj / "ownwt"
    sub_spine = write_spine(alt, make_spine([("gx", "in-progress")]), work="run-sub")
    own_spine = write_spine(own, make_spine([("gy", "in-progress")]), work="run-own")
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("run-sub", "eng-s"), alt), proj)
    sr.handle_post_tool_use(
        _real_post_tool_use(parent, _claim_cmd("run-own", "eng-own"), own), proj)
    assert list(sr.load_binding(proj).keys()) == [composite, sid]
    os.remove(sub_spine)  # both bound, then both targets vanish
    os.remove(own_spine)

    sp = write_spine(proj, make_spine([("g1", "in-progress")], session_id="eng-alone",
                                      imperatives={"g1": "ONLY-MARKER keep going"}),
                     work="run-alone")

    out = sr.decide_session_start({"session_id": sid, "cwd": str(proj), "source": "resume"}, proj)
    assert "ONLY-MARKER" in out["hookSpecificOutput"]["additionalContext"]

    binding = sr.load_binding(proj)
    assert set(binding.keys()) == {composite, sid}   # new entry under the BARE key
    assert set(binding[sid].keys()) == {own_spine, sp}  # merged, sibling survives
    assert binding[sid][sp]["engine_session"] == "eng-alone"
    assert list(binding[composite].keys()) == [_abs_spine(alt, "run-sub")]  # untouched


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


# --- path comparison helper (_same_path) -------------------------------------
#
# `_foreign_worktree` used to live here and answered "is this bound spine mine?"
# by comparing the stopping payload's cwd against the binding's recorded
# worktree. #609 lane F g3 deleted it with both its call sites: ownership is the
# binding key, never the tree (see OwnershipIsBindingKeyNotWorktree below).
# `_same_path` survives because its other callers -- git_worktree_roots and
# resolve_spine_candidate -- ask it about PATHS, which is all it ever knew.

def test_same_path_fail_safe_returns_true_on_bad_input():
    # (d) a comparison error must NEVER relax the rail: default True.
    assert sr._same_path(None, "x") is True
    assert sr._same_path("x", 123) is True


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="ntpath's normcase (lowercase + backslash/forward-slash folding) only applies on Windows",
)
def test_same_path_windows_normcase_sep_equivalence():
    # (f) case + separator normalize to equal -> no spurious relaxation.
    assert sr._same_path("C:\\Foo", "c:/foo") is True


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="posixpath's normcase is identity and backslash is not a separator -- "
    "covered by the Windows-only case above instead",
)
def test_same_path_posix_case_and_backslash_are_significant():
    # (f-posix) On POSIX, os.path.normcase does not fold case and os.path.normpath
    # does not treat backslash as a separator (it is a plain, case-significant
    # filename character) -- so these really are two DIFFERENT path strings, and
    # _same_path is right to say so. Collapsing them here would be exactly the
    # spurious relaxation the fail-safe design (see _same_path's docstring)
    # exists to prevent: it would treat a POSIX file literally named "C:\Foo" as
    # the same path as directory "foo" under "c:", which they are not.
    assert sr._same_path("C:\\Foo", "c:/foo") is False


def test_same_path_distinct_paths_differ():
    assert sr._same_path("C:/a/wtParent", "C:/a/wtChild") is False


def test_foreign_worktree_is_gone_and_stays_gone():
    """The tree-as-ownership test was deleted, not softened (#609 lane F g3).
    A reintroduced `_foreign_worktree` would read as a harmless helper right up
    until something asked it who owns a spine, so its absence is pinned here
    rather than left to be noticed."""
    assert not hasattr(sr, "_foreign_worktree")


class OwnershipIsBindingKeyNotWorktree(unittest.TestCase):
    """#609 lane F g3. Ownership -- "is this spine MINE to drive?" -- is decided
    by the BINDING KEY that claimed it, never by the tree it sits in.

    Spines are 1:1 with work AREAS, not worktrees. A Commander gets a worktree;
    an in-tree crew works in its Commander's tree, in its own area. So one
    worktree holds several spines, and `same worktree, therefore mine` is wrong
    the moment a crew shares its Commander's tree: the tree answers WHERE, and
    only the binding key answers WHOSE.

    Which tree the cases use is chosen per SITE, and the two sites want
    opposite shapes:

    - For the Stop site, one worktree shared by parent and crew is the shape
      that matters. Giving them different trees proves nothing there -- that is
      the case the deleted worktree test already got right, and it is preserved
      as an explicit control below.
    - For the SessionStart site it is the other way round. The differing-tree
      case is exactly where the deleted test was doing real work: the skip it
      performed was the only thing keeping a restarting Commander on its own
      binding, so that is the shape that REGRESSED when the skip went and
      nothing replaced it. The single-call cases below put parent and crew in
      different trees for that reason, and place both spines outside the
      fallback scan's reach so only the binding can explain the answer.

    Scoping the spines out of the scan's reach answers one question and hides
    another, so the last cases in this class deliberately do the opposite.
    `decide_session_start`'s binding read and its scan-bind write are the same
    `if spine is None:` branch, so withholding at the read routes traffic into
    the write -- and that write files under the bare `sid`, which is the key the
    NEXT call reads as OWN. No single call can see that, and no fixture the scan
    cannot reach can see it either, so those cases are SEQUENCES with the spine
    genuinely in-tree.

    Two different states of that read reach the one write, so there are two
    such fixtures and not one: `_in_tree_crew_only`, where the acting agent owns
    nothing visible, and `_in_tree_crew_and_the_parents_archived_spine`, where
    it owns an entry whose spine no longer loads. The second is the one no
    reader-side rule can see, and it is guarded at the writer.

    `unittest.TestCase` rather than this module's function style so pytest
    collects the class under its required name: this repo ships no pytest
    config, so the default `python_classes = Test*` would skip a plain class,
    while a `TestCase` subclass is collected whatever it is called.
    """

    def setUp(self):
        self.proj = Path(tempfile.mkdtemp(prefix="ownership-binding-key-")).resolve()
        self.addCleanup(shutil.rmtree, str(self.proj), True)
        prior = os.environ.get("CLAUDE_PROJECT_DIR")
        os.environ["CLAUDE_PROJECT_DIR"] = str(self.proj)
        self.addCleanup(self._restore_project_dir, prior)

    @staticmethod
    def _restore_project_dir(prior):
        if prior is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = prior

    # -- the shape: one worktree, a parent and its crew ----------------------

    def _parent_and_in_tree_crew(self):
        """A Commander and an in-tree crew sharing ONE worktree, bound by the
        REAL claim writer from the REAL captured payloads (#419's probe): the
        parent carries no `agent_id`, so it binds under the bare session_id;
        the crew carries one, so it binds under `sid#agent_id`. Both spines
        live under the same project dir and both claims are issued from it, so
        every recorded `worktree` is the same string and the tree can decide
        nothing.

        The crew claims FIRST so its composite key leads the binding map and
        its entry leads the merged session view. That ordering is the point,
        not incidental: with the worktree skip gone, whichever entry leads is
        what `decide_stop` would render, so a parent that is answered with its
        own gate here is answered with it by ownership, not by luck.
        """
        parent = _real_parent_payloads()[0]
        crew = _real_subagent_payloads()[0]
        self.assertEqual(crew["session_id"], parent["session_id"])  # one harness session
        write_spine(
            self.proj,
            make_spine([("g3", "in-progress")],
                       imperatives={"g3": "CREW-MARKER implement the crew gate"}),
            work="run-crew", journal_lines=1,
        )
        write_spine(
            self.proj,
            make_spine([("execute", "in-progress")],
                       imperatives={"execute": "PARENT-MARKER drive execute.json"}),
            work="run-parent", journal_lines=1,
        )
        sr.handle_post_tool_use(
            _real_post_tool_use(crew, _claim_cmd("run-crew", "eng-crew"), self.proj), self.proj)
        sr.handle_post_tool_use(
            _real_post_tool_use(parent, _claim_cmd("run-parent", "eng-parent"), self.proj), self.proj)

        sid = parent["session_id"]
        crew_key = sid + sr.BINDING_KEY_SEP + crew["agent_id"]
        binding = sr.load_binding(self.proj)
        self.assertEqual(list(binding), [crew_key, sid])  # crew's key leads
        entries = sr.session_view(binding, sid)
        self.assertEqual(
            list(entries),
            [_abs_spine(self.proj, "run-crew"), _abs_spine(self.proj, "run-parent")],
        )
        # ONE worktree: whatever spelling the claim writer recorded, both
        # entries carry the SAME one, so no comparison against it can tell
        # these two spines apart.
        self.assertEqual(len({e["worktree"] for e in entries.values()}), 1)
        return sid, crew, crew_key

    def test_a_parents_stop_is_answered_with_its_own_gate_not_its_in_tree_crews(self):
        """THE #549 shape. The parent's Stop must be answered with the PARENT's
        gate. Before this change the crew's in-tree entry was not "foreign", so
        it led the mid-flight list and the parent's Stop was answered with the
        crew's gate -- the parent's own open gate never rendered at all."""
        sid, _crew, crew_key = self._parent_and_in_tree_crew()

        out = sr.decide_stop({"session_id": sid, "cwd": str(self.proj)}, self.proj)

        self.assertEqual(out["decision"], "block")  # both gates are open; still blocked
        reason = out["reason"]
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("PARENT-MARKER", reason)      # answered with its OWN gate
        self.assertIn("PARENT-MARKER", ctx)
        self.assertNotIn("CREW-MARKER", reason)     # never with the crew's
        self.assertNotIn("CREW-MARKER", ctx)
        self.assertNotIn(crew_key, reason)
        # The 3-strike hatch stays keyed by session id ALONE, never fragmented
        # per entry -- two mid-flight entries, one nudge record.
        self.assertEqual(list(sr.load_nudges(self.proj)), [sid])

    def test_the_same_answer_when_the_crew_has_its_own_tree_control(self):
        """CONTROL, green before and after: the differing-tree case the deleted
        worktree test already got right. Kept so the change is visibly a
        generalization -- the parent gets its own gate whether or not the crew
        shares its tree -- rather than a swap of one skip for another."""
        parent = _real_parent_payloads()[0]
        crew = _real_subagent_payloads()[0]
        sid = parent["session_id"]
        crew_tree = self.proj / "crewwt"
        write_spine(crew_tree, make_spine([("g3", "in-progress")],
                                          imperatives={"g3": "CREW-MARKER implement the crew gate"}),
                    work="run-crew", journal_lines=1)
        write_spine(self.proj, make_spine([("execute", "in-progress")],
                                          imperatives={"execute": "PARENT-MARKER drive execute.json"}),
                    work="run-parent", journal_lines=1)
        sr.handle_post_tool_use(
            _real_post_tool_use(crew, _claim_cmd("run-crew", "eng-crew"), crew_tree), self.proj)
        sr.handle_post_tool_use(
            _real_post_tool_use(parent, _claim_cmd("run-parent", "eng-parent"), self.proj), self.proj)
        entries = sr.session_view(sr.load_binding(self.proj), sid)
        self.assertEqual(len({e["worktree"] for e in entries.values()}), 2)  # two trees here

        out = sr.decide_stop({"session_id": sid, "cwd": str(self.proj)}, self.proj)

        self.assertEqual(out["decision"], "block")
        self.assertIn("PARENT-MARKER", out["reason"])
        self.assertNotIn("CREW-MARKER", out["reason"])
        self.assertNotIn("CREW-MARKER", out["hookSpecificOutput"]["additionalContext"])

    def test_a_crew_that_stops_is_not_handed_its_parents_gate(self):
        """The inverse, and the failure five crews on this issue actually hit:
        a crew told by the Stop hook to go drive its PARENT's `execute` gate.

        The acting agent's own key is `binding_key(payload)` -- the one function
        that composes a key anywhere in this codebase -- so when the harness
        delivers an `agent_id` (measured for PostToolUse in the pinned probe
        capture), the crew is answered with the gate it actually claimed, and
        its parent's imperative is withheld from it exactly as the crew's is
        withheld from the parent. If a Stop payload carries no `agent_id`, this
        collapses to the bare-key case above rather than to a different rule."""
        sid, crew, _crew_key = self._parent_and_in_tree_crew()

        out = sr.decide_stop(
            {"session_id": sid, "agent_id": crew["agent_id"], "cwd": str(self.proj)}, self.proj)

        self.assertEqual(out["decision"], "block")
        reason = out["reason"]
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("CREW-MARKER", reason)        # its own gate
        self.assertNotIn("PARENT-MARKER", reason)   # never its parent's
        self.assertNotIn("PARENT-MARKER", ctx)

    # -- site 1: mid-flight Stop blocking ------------------------------------

    def test_stop_blocks_on_an_own_entry_recorded_in_another_worktree(self):
        """What NEWLY blocks. This session claimed the spine -- the binding key
        says so -- so its Stop is refused wherever it happens to be standing.
        Before this change the recorded worktree differed from the payload cwd,
        the entry was skipped as "foreign", and the session walked away from
        its own mid-flight run."""
        other = self.proj / "otherwt"
        sp = write_spine(other, make_spine([("g1", "in-progress")],
                                           imperatives={"g1": "OWN-MARKER finish it"}),
                         journal_lines=1)
        bind(self.proj, "s1", sp, worktree=str(other))

        out = sr.decide_stop({"session_id": "s1", "cwd": str(self.proj)}, self.proj)

        self.assertEqual(out["decision"], "block")
        self.assertIn("OWN-MARKER", out["reason"])

    # -- site 2: which binding entry a resumed session picks up --------------

    def test_session_start_resumes_from_its_own_binding_in_another_worktree(self):
        """The two call sites are NOT symmetric. Here the skip did not decide
        blocking -- it decided whether a resumed session reads its OWN binding
        or falls through to `_scan_active_spine`, the blind glob that can hand a
        session a spine it never claimed. Dropping the tree test keeps the
        session on its own binding, which is the safer of the two paths."""
        alt = self.proj / "altwt"
        sp = write_spine(alt, make_spine([("g2", "in-progress")],
                                         imperatives={"g2": "RESUME-MARKER keep going"}))
        bind(self.proj, "s1", sp, worktree=str(alt))
        self.assertEqual(sr._scan_active_spine(self.proj), [])  # nothing for the fallback

        out = sr.decide_session_start({"session_id": "s1", "cwd": str(self.proj)}, self.proj)

        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("RESUMING", ctx)
        self.assertIn("RESUME-MARKER", ctx)

    # -- fail-safe: uncertainty blocks, it never relaxes ---------------------

    def test_garbage_location_data_never_relaxes_the_rail(self):
        """Location data is now inert, and inert must mean BLOCKED, not
        allowed. Every row is a mid-flight entry this session claimed, with the
        location fields ranging over absent, wrong-typed and structurally
        nonsense values."""
        sp = write_spine(self.proj, make_spine([("g1", "in-progress")],
                                               imperatives={"g1": "FAILSAFE-MARKER finish it"}),
                         journal_lines=1)
        rows = [
            ("no cwd at all", {"session_id": "s1"}, str(self.proj)),
            ("int cwd", {"session_id": "s1", "cwd": 12345}, str(self.proj)),
            ("dict cwd", {"session_id": "s1", "cwd": {"not": "a path"}}, str(self.proj)),
            ("null worktree", {"session_id": "s1", "cwd": str(self.proj)}, None),
            ("int worktree", {"session_id": "s1", "cwd": str(self.proj)}, 12345),
            ("empty worktree", {"session_id": "s1", "cwd": str(self.proj)}, ""),
        ]
        for label, payload, worktree in rows:
            with self.subTest(row=label):
                sr.save_binding(self.proj, {})
                sr.save_nudges(self.proj, {})
                bind(self.proj, "s1", sp, worktree=worktree)
                out = sr.decide_stop(payload, self.proj)
                self.assertEqual(out.get("decision"), "block", label)
                self.assertIn("FAILSAFE-MARKER", out["reason"], label)
        self.assertEqual(len(rows), 6)  # a loop that asserts what it looped over

    def test_an_unidentifiable_agent_blocks_and_is_told_nothing_to_drive(self):
        """The other fail-safe direction. `binding_key` refuses to compose a key
        for a malformed `agent_id` (#441's allowlist), so the hook cannot say
        who is stopping. Uncertainty must block -- and it must withhold, since
        handing an imperative to an agent whose identity is unestablished is the
        very confusion this gate exists to end."""
        sp = write_spine(self.proj, make_spine([("g1", "in-progress")],
                                               imperatives={"g1": "WITHHELD-MARKER finish it"}),
                         journal_lines=1)
        bind(self.proj, "s1", sp)
        for label, agent_id in [("path separator", "a/b"), ("empty", ""), ("wrong type", 12345)]:
            with self.subTest(agent_id=label):
                # Reset the strike counter per row: the journal is frozen, so
                # three no-progress rows in a row would otherwise trip the
                # 3-strike hatch and the third row would measure THAT.
                sr.save_nudges(self.proj, {})
                self.assertIsNone(sr.binding_key({"session_id": "s1", "agent_id": agent_id}))
                out = sr.decide_stop(
                    {"session_id": "s1", "agent_id": agent_id, "cwd": str(self.proj)}, self.proj)
                self.assertEqual(out.get("decision"), "block", label)
                self.assertNotIn("WITHHELD-MARKER", out["reason"], label)
                self.assertNotIn(
                    "WITHHELD-MARKER", out["hookSpecificOutput"]["additionalContext"], label)

    # -- Windows -------------------------------------------------------------

    def test_ownership_no_longer_folds_case_or_separators(self):
        """Windows, CONSTRUCTED rather than inherited. `os.path.normcase` is the
        identity function on POSIX, so a case expectation read off this host
        proves nothing -- the platform split is stated explicitly below.

        The old test compared a recorded worktree against the payload cwd
        through `normcase`, which made this Stop decision PLATFORM-DEPENDENT:
        `C:\\Foo\\wt` and `c:/foo/wt` are the same path on Windows and two
        different paths on POSIX, so the same binding allowed the stop on one
        platform and refused it on the other. Ownership is now an exact
        binding-key comparison over harness-issued session and agent ids --
        which are opaque tokens, never paths, and cannot contain a separator
        (`_AGENT_ID_ALLOWED`) -- so nothing here folds case or separators and
        the answer is the same on both platforms."""
        recorded, standing_in = "C:\\Foo\\wt", "c:/foo/wt"
        folds = os.path.normcase(recorded) == os.path.normcase(standing_in)
        self.assertEqual(folds, sys.platform == "win32")  # the split, stated not observed
        self.assertEqual(sr._same_path(recorded, standing_in), folds)  # still true of paths

        sp = write_spine(self.proj, make_spine([("g1", "in-progress")],
                                               imperatives={"g1": "PLATFORM-MARKER finish it"}),
                         journal_lines=1)
        bind(self.proj, "s1", sp, worktree=recorded)

        out = sr.decide_stop({"session_id": "s1", "cwd": standing_in}, self.proj)

        self.assertEqual(out["decision"], "block")  # on BOTH platforms
        self.assertIn("PLATFORM-MARKER", out["reason"])

    # -- site 2, continued: SELECTION is a binding-key question here too -----
    #
    # Nothing measured says a SessionStart payload carries an `agent_id` -- the
    # pinned capture is PostToolUse only -- and it is tempting to read that
    # absence as "so every entry in the merged view is this session's own". It
    # is not. `session_view` merges the bare `sid` PLUS
    # every `sid#<agent_id>` key, and Agent-tool subagents SHARE their parent's
    # session_id -- that sharing is the whole premise of #419 and of the
    # per-agent key -- so another AGENT's entry is in the view by construction.
    # Taking the first entry in dict order therefore hands a restarting
    # Commander whichever spine happened to be claimed first, routinely its
    # crew's, together with "Pick the run back up at this gate and drive it
    # through the engine". That is the #549/#419 failure itself.

    def _parent_and_out_of_tree_crew(self, parent_first=False):
        """A Commander and a crew in DIFFERENT worktrees, bound by the REAL
        claim writer from the REAL captured payloads (the parent carries no
        `agent_id` and binds under the bare session_id; the crew carries one
        and binds under `sid#agent_id`), with `parent_first` choosing which key
        is written first.

        BOTH spines are placed outside `_scan_active_spine`'s glob, which only
        reaches `<project>/.agent-work/*/spine.json`, and that emptiness is
        asserted rather than assumed: with nothing for the fallback to find,
        only the BINDING can explain what a restarted session is told to
        resume, so a passing assertion here is about selection and cannot be
        the blind scan answering by luck.

        Differing trees are the point at THIS site, not a control. The deleted
        worktree test skipped the crew's entry because its tree differed, and
        that skip was the only thing keeping the parent on its own binding --
        so this is exactly the shape that regressed when the skip went and
        nothing replaced it.
        """
        parent = _real_parent_payloads()[0]
        crew = _real_subagent_payloads()[0]
        self.assertEqual(crew["session_id"], parent["session_id"])  # one harness session
        parent_tree, crew_tree = self.proj / "parentwt", self.proj / "crewwt"
        write_spine(parent_tree,
                    make_spine([("execute", "in-progress")],
                               imperatives={"execute": "PARENT-MARKER drive execute.json"}),
                    work="run-parent", journal_lines=1)
        write_spine(crew_tree,
                    make_spine([("g3", "in-progress")],
                               imperatives={"g3": "CREW-MARKER implement the crew gate"}),
                    work="run-crew", journal_lines=1)
        claims = [(crew, _claim_cmd("run-crew", "eng-crew"), crew_tree),
                  (parent, _claim_cmd("run-parent", "eng-parent"), parent_tree)]
        if parent_first:
            claims.reverse()
        for payload, command, tree in claims:
            sr.handle_post_tool_use(_real_post_tool_use(payload, command, tree), self.proj)

        sid = parent["session_id"]
        crew_key = sid + sr.BINDING_KEY_SEP + crew["agent_id"]
        binding = sr.load_binding(self.proj)
        self.assertEqual(list(binding), [sid, crew_key] if parent_first else [crew_key, sid])
        entries = sr.session_view(binding, sid)
        self.assertEqual(len(entries), 2)  # the crew's entry IS in the parent's view
        self.assertEqual(len({e["worktree"] for e in entries.values()}), 2)  # two trees
        self.assertEqual(sr._scan_active_spine(self.proj), [])  # nothing for the fallback
        return sid, crew, crew_key

    def test_session_start_resumes_from_its_own_entry_not_its_crews(self):
        """A restarting Commander must be handed its OWN gate. Before this
        change `decide_session_start` took the first entry in dict order, and
        the crew claimed first, so the parent was told to drive the crew's
        gate."""
        sid, _crew, _crew_key = self._parent_and_out_of_tree_crew()

        out = sr.decide_session_start({"session_id": sid, "cwd": str(self.proj)}, self.proj)

        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("RESUMING", ctx)
        self.assertIn("PARENT-MARKER", ctx)   # its own gate
        self.assertNotIn("CREW-MARKER", ctx)  # never its crew's

    def test_session_start_selection_is_ownership_not_write_order(self):
        """The proof that selection is a decision and not an accident: the SAME
        binding, differing only in which key was written first, must give the
        same answer. Before this change the answer flipped with the order."""
        for label, parent_first in (("crew's key written first", False),
                                    ("parent's key written first", True)):
            with self.subTest(order=label):
                sr.save_binding(self.proj, {})  # each order builds its own binding
                sid, _crew, _crew_key = self._parent_and_out_of_tree_crew(parent_first)

                out = sr.decide_session_start({"session_id": sid, "cwd": str(self.proj)},
                                              self.proj)

                ctx = out["hookSpecificOutput"]["additionalContext"]
                self.assertIn("PARENT-MARKER", ctx, label)
                self.assertNotIn("CREW-MARKER", ctx, label)

    def test_session_start_does_not_resume_from_a_crews_binding_it_never_claimed(self):
        """A session that claimed nothing must not be handed a gate from the
        BINDING. Here only the crew's per-agent key exists -- visible to the
        parent's session because they share a session_id, asserted below -- and
        the parent has no binding of its own. Before this change it was told to
        drive the crew's gate; the answer must be no context at all.

        Scoped to the binding on purpose: both spines sit outside
        `_scan_active_spine`'s glob, so this says nothing about the fallback.
        The in-tree twin of this arrangement, where the scan CAN reach a spine
        and used to bind the parent to it, is
        `test_a_restarting_parent_is_never_bound_to_its_in_tree_crews_spine`."""
        parent = _real_parent_payloads()[0]
        crew = _real_subagent_payloads()[0]
        sid = parent["session_id"]
        crew_tree = self.proj / "crewwt"
        write_spine(crew_tree,
                    make_spine([("g3", "in-progress")],
                               imperatives={"g3": "CREW-MARKER implement the crew gate"}),
                    work="run-crew", journal_lines=1)
        sr.handle_post_tool_use(
            _real_post_tool_use(crew, _claim_cmd("run-crew", "eng-crew"), crew_tree), self.proj)

        binding = sr.load_binding(self.proj)
        self.assertEqual(list(binding), [sid + sr.BINDING_KEY_SEP + crew["agent_id"]])
        self.assertEqual(len(sr.session_view(binding, sid)), 1)  # visible to the parent
        self.assertEqual(sr._scan_active_spine(self.proj), [])   # and nothing to scan

        out = sr.decide_session_start({"session_id": sid, "cwd": str(self.proj)}, self.proj)

        self.assertEqual(out, {})  # no gate of its own -> no context, not the crew's

    def test_session_start_answers_the_agent_the_payload_names(self):
        """Two DIFFERENT crew agents under one harness session. The site reads
        `binding_key(payload)`, the one function that composes a key anywhere in
        this codebase, so if a payload ever does carry an `agent_id` the answer
        follows THAT agent's claim rather than whichever key leads the view.
        Both ids here are real, from the pinned capture. No test claims the
        harness sends `agent_id` at SessionStart; the point is that the site no
        longer ignores it when it is there."""
        agent_a, agent_b = _real_subagent_payloads()[0], _real_subagent_payloads()[1]
        self.assertNotEqual(agent_a["agent_id"], agent_b["agent_id"])
        sid = agent_a["session_id"]
        for agent, work, marker in ((agent_a, "run-a", "AGENT-A-MARKER"),
                                    (agent_b, "run-b", "AGENT-B-MARKER")):
            tree = self.proj / work
            write_spine(tree, make_spine([("g1", "in-progress")],
                                         imperatives={"g1": marker + " gate"}),
                        work=work, journal_lines=1)
            sr.handle_post_tool_use(
                _real_post_tool_use(agent, _claim_cmd(work, "eng-" + work), tree), self.proj)
        self.assertEqual(sr._scan_active_spine(self.proj), [])

        out = sr.decide_session_start(
            {"session_id": sid, "agent_id": agent_b["agent_id"], "cwd": str(self.proj)},
            self.proj)

        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("AGENT-B-MARKER", ctx)     # agent B's own gate
        self.assertNotIn("AGENT-A-MARKER", ctx)  # not agent A's, which leads the view

    def test_session_start_withholds_when_it_cannot_say_who_is_starting(self):
        """The fail-safe direction at THIS site. Withholding is not blocking
        here -- SessionStart never blocks -- it is declining to hand out a gate.
        `binding_key` refuses to compose a key for a malformed `agent_id`
        (#441's allowlist), so the hook cannot say who is starting, nothing is
        attributable to it, and it is told nothing to drive rather than being
        pointed at the only entry lying around.

        Scoped honestly: this asserts what the BINDING can hand out, and the
        spine is placed outside `_scan_active_spine`'s glob so only the binding
        can answer. A session that owns none of a NON-EMPTY view no longer
        falls through to that scan at all -- the scan's branch writes a binding
        under the bare `sid`, so falling through would have handed exactly the
        agent this test cannot identify an ownership record to be answered with
        on its next call. That is pinned by its own in-tree case in
        `test_bind_on_resume_is_withheld_only_when_the_session_owns_nothing_visible`;
        here the glob is empty, so this test measures the binding decision
        alone."""
        alt = self.proj / "altwt"
        sp = write_spine(alt, make_spine([("g2", "in-progress")],
                                         imperatives={"g2": "WITHHELD-MARKER keep going"}))
        bind(self.proj, "s1", sp, worktree=str(alt))
        self.assertEqual(sr._scan_active_spine(self.proj), [])  # only the binding can answer
        self.assertEqual(len(sr.session_view(sr.load_binding(self.proj), "s1")), 1)
        for label, agent_id in (("path separator", "a/b"), ("empty", ""),
                                ("wrong type", 12345), ("explicit null", None)):
            with self.subTest(agent_id=label):
                payload = {"session_id": "s1", "agent_id": agent_id, "cwd": str(self.proj)}
                self.assertIsNone(sr.binding_key(payload))
                out = sr.decide_session_start(payload, self.proj)
                ctx = (out.get("hookSpecificOutput") or {}).get("additionalContext", "")
                self.assertNotIn("WITHHELD-MARKER", ctx, label)

    def test_session_start_location_data_is_inert_not_load_bearing(self):
        """The other half of the fail-safe direction: garbage in the LOCATION
        fields must not cost a session its own resume. `cwd` absent, wrong-typed
        or structurally nonsense, and a recorded `worktree` that is null, wrong-
        typed or empty -- the session still picks its own binding back up,
        because location no longer participates in the decision at all."""
        alt = self.proj / "altwt"
        sp = write_spine(alt, make_spine([("g2", "in-progress")],
                                         imperatives={"g2": "RESUME-MARKER keep going"}))
        rows = [
            ("no cwd at all", {"session_id": "s1"}, str(alt)),
            ("int cwd", {"session_id": "s1", "cwd": 12345}, str(alt)),
            ("dict cwd", {"session_id": "s1", "cwd": {"not": "a path"}}, str(alt)),
            ("null worktree", {"session_id": "s1", "cwd": str(self.proj)}, None),
            ("int worktree", {"session_id": "s1", "cwd": str(self.proj)}, 12345),
            ("empty worktree", {"session_id": "s1", "cwd": str(self.proj)}, ""),
        ]
        for label, payload, worktree in rows:
            with self.subTest(row=label):
                sr.save_binding(self.proj, {})
                bind(self.proj, "s1", sp, worktree=worktree)
                self.assertEqual(sr._scan_active_spine(self.proj), [])  # only the binding
                out = sr.decide_session_start(payload, self.proj)
                ctx = out["hookSpecificOutput"]["additionalContext"]
                self.assertIn("RESUME-MARKER", ctx, label)
        self.assertEqual(len(rows), 6)  # a loop that asserts what it looped over

    # -- the two sites share ONE MUTABLE STORE, so the properties above are
    # -- not enough: they are properties of a single call, and the binding a
    # -- SessionStart writes is what the next Stop reads as ownership. The
    # -- cases below are SEQUENCES, and they put the spine INSIDE the
    # -- fallback scan's glob, which every case above deliberately avoids.

    def _in_tree_crew_only(self):
        """The topology this lane actually runs in, and the one no case above
        constructs: a crew claims the IN-TREE spine under `sid#agent_id`, the
        parent holds no claim of its own, and the crew's spine sits exactly
        where `_scan_active_spine`'s `<project>/.agent-work/*/spine.json` glob
        looks.

        Every other SessionStart case in this class places its spines OUTSIDE
        that glob so only the binding can explain the answer. That scoping is
        honest but it means none of them can reach the fallback at all -- and
        the fallback is not a read, it WRITES a binding under the bare `sid`,
        which is the key the next call reads as OWN. The three asserted facts
        below are exactly the three the fallback's bind-on-resume branch keys
        on: a non-empty view, no entry in it the parent owns, and a scan count
        of exactly one.
        """
        parent = _real_parent_payloads()[0]
        crew = _real_subagent_payloads()[0]
        self.assertEqual(crew["session_id"], parent["session_id"])  # one harness session
        write_spine(
            self.proj,
            make_spine([("g3", "in-progress")],
                       imperatives={"g3": "CREW-MARKER implement the crew gate"}),
            work="run-crew", journal_lines=1,
        )
        sr.handle_post_tool_use(
            _real_post_tool_use(crew, _claim_cmd("run-crew", "eng-crew"), self.proj), self.proj)

        sid = parent["session_id"]
        crew_key = sid + sr.BINDING_KEY_SEP + crew["agent_id"]
        binding = sr.load_binding(self.proj)
        self.assertEqual(list(binding), [crew_key])              # the parent owns nothing
        self.assertEqual(list(sr.session_view(binding, sid)),
                         [_abs_spine(self.proj, "run-crew")])    # and still sees the crew's
        self.assertEqual(len(sr._scan_active_spine(self.proj)), 1)  # in-tree and scannable
        return sid, crew_key

    def test_a_restarting_parent_that_owns_nothing_visible_writes_no_binding(self):
        """A SessionStart that owns none of the visible entries must write NO
        binding. Withholding at the selection above is undone one branch later
        if the fallback then manufactures the very ownership that was withheld:
        the bind-on-resume write files under the bare `sid`, which is precisely
        the key the next Stop reads as OWN, so the parent is answered with its
        crew's gate AS ITS OWN.

        Asserted on both halves of the sequence, because either alone passes
        while the defect stands: what the FIRST call wrote to the binding
        store, and what the SECOND call rendered.

        The name states the fixture and not a universal. It read "a restarting
        parent is NEVER bound to its in-tree crew's spine" until a production
        sequence falsified exactly that universal one door over (see the B5 case
        below), and a false test name is the worst place for this defect --
        the name is what the next reader greps."""
        sid, crew_key = self._in_tree_crew_only()

        start = sr.decide_session_start({"session_id": sid, "cwd": str(self.proj)}, self.proj)

        # What the FIRST call WROTE. No bare-`sid` key is manufactured, and the
        # crew's own entry is left exactly as its claim wrote it.
        binding = sr.load_binding(self.proj)
        self.assertEqual(list(binding), [crew_key])
        self.assertEqual(sr.session_view_provenance(binding, sid),
                         {_abs_spine(self.proj, "run-crew"): crew_key})  # still the crew's
        # ...and what it RENDERED: a resume context naming the crew's gate is
        # the same leak in the other direction, since it ends "Pick the run
        # back up at this gate and drive it through the engine."
        self.assertNotIn("CREW-MARKER",
                         json.dumps((start.get("hookSpecificOutput") or {})))

        # What the SECOND call renders, through the store the first one left.
        out = sr.decide_stop({"session_id": sid, "cwd": str(self.proj)}, self.proj)

        self.assertEqual(out["decision"], "block")  # an open gate still blocks
        reason = out["reason"]
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("foreign-owned", reason)   # named as someone else's
        self.assertIn(crew_key, reason)          # and whose
        self.assertNotIn("CREW-MARKER", reason)  # imperative withheld from BOTH
        self.assertNotIn("CREW-MARKER", ctx)     # rendered fields (#549)

    def test_a_restart_does_not_change_what_the_next_stop_is_told(self):
        """The same fixture with the SessionStart as the ONLY variable. A
        restart after a compaction is routine on this lane, and it must not be
        able to turn a foreign-owner answer into an own-gate one -- so the two
        arms are asserted to render the SAME wording, rather than each being
        checked against its own expectation."""
        answers = {}
        arms = (("no restart", False), ("restart first", True))
        for label, restart in arms:
            with self.subTest(arm=label):
                sr.save_binding(self.proj, {})
                sr.save_nudges(self.proj, {})  # each arm gets its own strike count
                sid, crew_key = self._in_tree_crew_only()
                if restart:
                    sr.decide_session_start({"session_id": sid, "cwd": str(self.proj)},
                                            self.proj)

                out = sr.decide_stop({"session_id": sid, "cwd": str(self.proj)}, self.proj)

                self.assertEqual(out["decision"], "block", label)
                self.assertNotIn("CREW-MARKER", json.dumps(out), label)
                self.assertIn(crew_key, out["reason"], label)
                answers[label] = out
        self.assertEqual(len(answers), len(arms))  # assert what the loop looped over
        self.assertEqual(answers["no restart"], answers["restart first"])

    def test_bind_on_resume_still_binds_a_session_that_has_no_binding_at_all(self):
        """The regression risk the fix above carries, pinned so it cannot be
        traded away. #261's path is a resumed/compacted session that never
        itself ran `claim`: its view is EMPTY, so there is no ownership to
        withhold, and exactly one active-leased in-tree spine is the
        unambiguous answer the scan exists to give. It must still bind, and the
        binding must still be readable by the next call."""
        write_spine(
            self.proj,
            make_spine([("g1", "in-progress")], imperatives={"g1": "RESUME-MARKER keep going"}),
            work="run-solo", journal_lines=1,
        )
        sid = "s-resumed"
        self.assertEqual(sr.load_binding(self.proj), {})            # never ran claim
        self.assertEqual(len(sr._scan_active_spine(self.proj)), 1)  # one unambiguous spine

        out = sr.decide_session_start({"session_id": sid, "cwd": str(self.proj)}, self.proj)

        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("RESUMING", ctx)
        self.assertIn("RESUME-MARKER", ctx)
        binding = sr.load_binding(self.proj)
        self.assertEqual(list(binding), [sid])  # bound under the bare sid, as #261 asks
        self.assertEqual(list(binding[sid]), [_abs_spine(self.proj, "run-solo")])
        # and the next call reads it as this session's OWN, which is the point
        # of writing it: the gauge and the Stop path both go through this key.
        stop = sr.decide_stop({"session_id": sid, "cwd": str(self.proj)}, self.proj)
        self.assertEqual(stop["decision"], "block")
        self.assertIn("RESUME-MARKER", stop["reason"])

    def test_bind_on_resume_binds_an_empty_view_and_withholds_a_wholly_foreign_one(self):
        """Two of the three states of the read, at the READER's guard: the
        fallback binds on an EMPTY view (#261) and withholds on a non-empty view
        the session owns none of (B4). Both are asserted so this guard cannot
        drift into "never bind", which breaks #261.

        The third state is NOT here and this test does not speak for it: a view
        the session DOES own, whose spine no longer loads, reaches the same
        fallback with nothing withheld. It is asserted two cases down, and it is
        guarded at the writer rather than here -- which is why the drift this
        test pins cannot be stated as "back into always bind". "Always bind" was
        never the whole of B4's class, and reading these two rows as the whole
        discriminator is precisely what left B5 open."""
        rows = [("empty view -> bind (#261)", False, True),
                ("sees a crew's entry, owns none -> withhold (B4)", True, False)]
        for label, crew_claims, expect_bound in rows:
            with self.subTest(row=label):
                sr.save_binding(self.proj, {})
                shutil.rmtree(str(self.proj / ".agent-work"), True)
                if crew_claims:
                    sid, _crew_key = self._in_tree_crew_only()
                else:
                    write_spine(
                        self.proj,
                        make_spine([("g1", "in-progress")],
                                   imperatives={"g1": "SCAN-MARKER keep going"}),
                        work="run-solo", journal_lines=1,
                    )
                    sid = "s-resumed"
                self.assertEqual(len(sr._scan_active_spine(self.proj)), 1, label)

                sr.decide_session_start({"session_id": sid, "cwd": str(self.proj)}, self.proj)

                bound = sid in sr.load_binding(self.proj)
                self.assertEqual(bound, expect_bound, label)
        self.assertEqual(len(rows), 2)  # a loop that asserts what it looped over

    # -- the SECOND door into the same writer --------------------------------

    def _in_tree_crew_and_the_parents_archived_spine(self):
        """`_in_tree_crew_only` plus ONE ordinary further event: the parent
        claims a spine of its OWN, and that spine is later archived at closeout.

        This is the topology `_in_tree_crew_only` cannot reach. There the parent
        owns nothing, so the selection's withholding fires and the fallback is
        never entered. Here the parent DOES own a visible entry -- it just no
        longer loads -- so the selection withholds nothing, `spine` is left None
        for the other reason, and the SAME bind-on-resume write is reached. Both
        facts are asserted below rather than described, because which door this
        fixture uses is the whole point of it.

        Every binding entry is written by the real claim writer from the real
        captured payloads, so the store shape is production's, not one invented
        here.
        """
        parent = _real_parent_payloads()[0]
        crew = _real_subagent_payloads()[0]
        self.assertEqual(crew["session_id"], parent["session_id"])  # one harness session
        write_spine(
            self.proj,
            make_spine([("g3", "in-progress")],
                       imperatives={"g3": "CREW-MARKER implement the crew gate"}),
            work="run-crew", journal_lines=1,
        )
        write_spine(
            self.proj,
            make_spine([("execute", "in-progress")],
                       imperatives={"execute": "OWN-MARKER drive your own gate"}),
            work="run-own", journal_lines=1,
        )
        sr.handle_post_tool_use(
            _real_post_tool_use(crew, _claim_cmd("run-crew", "eng-crew"), self.proj), self.proj)
        sr.handle_post_tool_use(
            _real_post_tool_use(parent, _claim_cmd("run-own", "eng-own"), self.proj), self.proj)

        sid = parent["session_id"]
        crew_key = sid + sr.BINDING_KEY_SEP + crew["agent_id"]
        crew_spine = _abs_spine(self.proj, "run-crew")
        own_spine = _abs_spine(self.proj, "run-own")
        self.assertEqual(list(sr.load_binding(self.proj)), [crew_key, sid])

        shutil.rmtree(str(self.proj / ".agent-work" / "run-own"))  # archived at closeout

        binding = sr.load_binding(self.proj)
        owners = sr.session_view_provenance(binding, sid)
        # The store still attributes the crew's spine to the CREW, and the
        # parent still owns its own (now unloadable) entry.
        self.assertEqual(owners, {crew_spine: crew_key, own_spine: sid})
        self.assertTrue(sr._own_entries(list(sr.session_view(binding, sid).items()),
                                        owners, sid))          # B5's door, not B4's
        self.assertEqual(len(sr._scan_active_spine(self.proj)), 1)  # and the scan fires
        return sid, crew, crew_key, crew_spine

    def test_a_restarting_parent_is_not_bound_to_a_spine_its_crew_visibly_claims(self):
        """The bind-on-resume must not file a spine path the store already
        attributes to a DIFFERENT binding key, and must not overwrite that
        attribution.

        A session reaches that writer whenever `spine` is left None, and owning
        nothing visible is only one of the two ways that happens: a session that
        owns an entry whose spine no longer loads -- archived, deleted, moved --
        arrives there too, with the withholding above it silent because there is
        nothing there to withhold. The spine the glob then turns up is whatever
        single active-leased spine is in the tree, and on this lane that is
        routinely a crew's.

        The damage runs BOTH ways, so both are asserted: the parent is handed
        the crew's imperative as its own, AND the manufactured binding takes the
        crew's gate away from the crew, because provenance is last-key-wins and
        the parent's bare key is written last."""
        sid, crew, crew_key, crew_spine = self._in_tree_crew_and_the_parents_archived_spine()

        start = sr.decide_session_start({"session_id": sid, "cwd": str(self.proj)}, self.proj)

        # What the FIRST call WROTE: no ownership of the crew's spine is
        # manufactured under the parent's bare key, and the attribution the
        # store already held is left standing.
        binding = sr.load_binding(self.proj)
        self.assertNotIn(crew_spine, binding.get(sid) or {})
        self.assertEqual(sr.session_view_provenance(binding, sid)[crew_spine], crew_key)
        # ...and what it RENDERED: the resume context ends "Pick the run back up
        # at this gate and drive it through the engine", so naming the crew's
        # gate there is the same leak in the other field.
        self.assertNotIn("CREW-MARKER", json.dumps(start.get("hookSpecificOutput") or {}))

        # DIRECTION 1 -- what the parent's own next Stop is told.
        out = sr.decide_stop({"session_id": sid, "cwd": str(self.proj)}, self.proj)
        self.assertEqual(out["decision"], "block")  # an open gate still blocks
        self.assertIn("foreign-owned", out["reason"])
        self.assertIn(crew_key, out["reason"])
        self.assertNotIn("CREW-MARKER", json.dumps(out))  # imperative withheld (#549)

        # DIRECTION 2 -- and the crew still recognises its OWN gate afterwards.
        crew_stop = sr.decide_stop(
            {"session_id": sid, "agent_id": crew["agent_id"], "cwd": str(self.proj)}, self.proj)
        self.assertEqual(crew_stop["decision"], "block")
        self.assertIn("CREW-MARKER", crew_stop["reason"])
        self.assertNotIn("foreign-owned", crew_stop["reason"])

    def test_a_parents_restart_does_not_take_the_crews_gate_away_from_the_crew(self):
        """The same fixture with the parent's SessionStart as the ONLY variable,
        the two arms asserted EQUAL to each other rather than each against its
        own expectation. A restart is routine on this lane; it must not be able
        to move an answer that belongs to another agent entirely."""
        answers = {}
        arms = (("no restart", False), ("parent restarts first", True))
        for label, restart in arms:
            with self.subTest(arm=label):
                sr.save_binding(self.proj, {})
                sr.save_nudges(self.proj, {})  # each arm gets its own strike count
                shutil.rmtree(str(self.proj / ".agent-work"), True)
                sid, crew, _crew_key, _crew_spine = \
                    self._in_tree_crew_and_the_parents_archived_spine()
                if restart:
                    sr.decide_session_start({"session_id": sid, "cwd": str(self.proj)},
                                            self.proj)

                out = sr.decide_stop(
                    {"session_id": sid, "agent_id": crew["agent_id"], "cwd": str(self.proj)},
                    self.proj)

                self.assertEqual(out["decision"], "block", label)
                self.assertIn("CREW-MARKER", out["reason"], label)  # still its own gate
                answers[label] = out
        self.assertEqual(len(answers), len(arms))  # assert what the loop looped over
        self.assertEqual(answers["no restart"], answers["parent restarts first"])

    def test_the_writer_rule_refuses_only_a_contradicting_attribution(self):
        """The rule the bind-on-resume applies, asked directly, including the
        two answers that keep it from being broader than it is: a path the store
        attributes to NOBODY is not a contradiction (that is #202's sibling
        merge, and #261's resumed session), and neither is one already
        attributed to the very key the write would file it under.

        Unusable input answers REFUSE, not permit: this guard sits in front of a
        writer, and the fail-safe direction at a writer is to withhold."""
        conflict = "/p/.agent-work/run-crew/spine.json"
        cases = [
            ("attributed to a sibling's composite key -> refuse",
             {conflict: "sid#agent"}, conflict, "sid", True),
            ("attributed to nobody -> allow (#202/#261)",
             {"/p/.agent-work/other/spine.json": "sid"}, conflict, "sid", False),
            ("already attributed to the writing key itself -> allow",
             {conflict: "sid"}, conflict, "sid", False),
            ("no attributions at all -> allow (#261's empty view)",
             {}, conflict, "sid", False),
            ("unusable attributions -> refuse (fail-safe at a writer)",
             "not-a-mapping", conflict, "sid", True),
            # A spelling difference must not buy a write past the guard. This
            # one is `normpath`'s, so it holds on every platform; `normcase`'s
            # case folding is real only on Windows and is asserted where the
            # rest of this file asserts it, against the derivation rule itself.
            ("the same file spelled differently -> refuse",
             {"/p/.agent-work/./run-crew/spine.json": "sid#agent"}, conflict, "sid", True),
        ]
        for label, owners, path, bind_key, expected in cases:
            with self.subTest(case=label):
                self.assertEqual(
                    sr._attributed_to_another_key(owners, path, bind_key), expected, label)
        self.assertEqual(len(cases), 6)  # a loop that asserts what it looped over


def _derived_form(path):
    """A directory in the normalized form `_worktree_from_spine` returns it in.

    Spelled from the predicate the implementation applies -- `normcase` +
    `normpath` -- never inherited from the platform. `str(tmp_path / ...)`
    preserves case, while the derivation folds it; on Windows `normcase`
    lowercases and rewrites separators, so comparing against the raw `str` would
    fail for EVERY `tmp_path` there, starting at the drive letter. On POSIX
    `normcase` is the identity, which is exactly why that failure is invisible
    on this host and has to be constructed rather than observed.

    Same construction as `tests/test_worktree_derivation.py`'s `_expected()`,
    which is what pins these two files' expectations to one rule.
    """
    return os.path.normcase(os.path.normpath(str(path)))


def test_worktree_from_spine_walks_to_the_nearest_agent_work_ancestor(tmp_path):
    """NEW CONTRACT (#609 lane F g1). `_worktree_from_spine` answers LOCATION for
    any absolute path: nearest `.agent-work` ancestor, take its parent, arbitrary
    depth; no such ancestor means unowned.

    It used to require the exact one-level `.agent-work/<id>/<name>.json` shape,
    and the four `.json`-suffix / work-id-segment / depth cases below are the
    scenario that test forbade -- they are now precisely what this change
    permits. The narrow shape did not disappear: it moved to `_is_claim_layout`,
    which is what the ownership gate now uses (see the two tests below).

    The rule's SPECIFICATION is the exhaustive case table in
    `tests/test_worktree_derivation.py`, which drives this function -- now the
    one implementation of the rule in the repo, since #609 g2 deleted the
    engine-side twin under `ADMIRAL_RULING-2` N2 (it re-lands in #610's wave
    with #315, its consumer, and re-derives against that same table). This test
    covers only what the hook itself must guarantee.
    """
    worktree = tmp_path / "worktree"

    # Unchanged: the one-level shape still derives the same answer as before.
    spine = worktree / ".agent-work" / "run1" / "checklist.json"
    assert sr._worktree_from_spine(str(spine)) == _derived_form(worktree)

    # NEWLY ACCEPTED -- each returned None before this change.
    now_owned = (
        # deeper than one level: a crew's own plan under a Commander's area
        worktree / ".agent-work" / "run1" / "crew-handoffs" / "g1" / "PLAN.json",
        # an archived spine, arbitrarily deep
        worktree / ".agent-work" / "archive" / "ep" / "harvest" / "i" / "spine.json",
        # depth zero: no work-id segment at all
        worktree / ".agent-work" / "checklist.json",
        # not a .json leaf -- suffix is a checklist-shape question, not location
        worktree / ".agent-work" / "run1" / "checklist.txt",
    )
    for path in now_owned:
        assert sr._worktree_from_spine(str(path)) == _derived_form(worktree), path

    # NEAREST, never outermost: the inner `.agent-work` roots a nested sandbox.
    sandbox = worktree / ".agent-work" / "archive" / "ep" / "workspace"
    nested = sandbox / ".agent-work" / "run1" / "spine.json"
    assert sr._worktree_from_spine(str(nested)) == _derived_form(sandbox)

    # Still unowned -- these did not change.
    unowned = (
        None,
        "",
        os.path.join(".agent-work", "run1", "checklist.json"),  # relative
        str(worktree / "other" / "run1" / "checklist.json"),    # no ancestor
        str(worktree / "not-.agent-work-really" / "checklist.json"),  # substring
    )
    for path in unowned:
        assert sr._worktree_from_spine(path) is None, path


def test_is_claim_layout_holds_the_narrow_shape_the_derivation_gave_up(tmp_path):
    """The shape preconditions moved OUT of `_worktree_from_spine` and landed
    here, so widening the derivation does not widen the ownership gate."""
    worktree = tmp_path / "worktree"
    assert sr._is_claim_layout(str(worktree / ".agent-work" / "run1" / "c.json"))

    # Every path the widened derivation newly OWNS, this still refuses.
    refused = (
        None,
        "",
        os.path.join(".agent-work", "run1", "c.json"),               # relative
        str(worktree / ".agent-work" / "run1" / "crew" / "g1" / "PLAN.json"),  # deep
        str(worktree / ".agent-work" / "archive" / "ep" / "spine.json"),       # deep
        str(worktree / ".agent-work" / "c.json"),                    # depth zero
        str(worktree / ".agent-work" / "run1" / "c.txt"),            # not .json
        str(worktree / ".agent-work" / "run1" / ".json"),            # bare suffix
        str(worktree / "other" / "run1" / "c.json"),                 # no .agent-work
    )
    for path in refused:
        assert sr._is_claim_layout(path) is False, path


def test_is_valid_claim_target_still_rejects_a_symlinked_spine(tmp_path):
    """The symlink-escape guard must remain able to FAIL.

    `_is_valid_claim_target` checks the given path lexically, then re-checks the
    RESOLVED path. That second check is only meaningful while the derivation
    stays lexical -- if it resolved symlinks itself, both checks would see the
    same path and the guard could never fire. This test is what makes that
    falsifiable rather than asserted.
    """
    worktree = tmp_path / "worktree"
    (worktree / ".agent-work" / "run1").mkdir(parents=True)

    # A real, valid claim target inside the work area: accepted.
    good = worktree / ".agent-work" / "run1" / "checklist.json"
    good.write_text(json.dumps({"items": []}), encoding="utf-8")
    assert sr._is_valid_claim_target(str(good)) is True

    # The same checklist content living OUTSIDE any `.agent-work`, reached
    # through a symlink that sits at a valid-looking claim path. The lexical
    # check passes; the resolved re-check must reject it.
    outside = tmp_path / "elsewhere" / "checklist.json"
    outside.parent.mkdir(parents=True)
    outside.write_text(json.dumps({"items": []}), encoding="utf-8")
    escaped = worktree / ".agent-work" / "run1" / "escaped.json"
    try:
        escaped.symlink_to(outside)
    except (OSError, NotImplementedError):  # pragma: no cover -- Windows w/o privilege
        pytest.skip("symlinks unavailable on this host")

    assert sr._is_claim_layout(str(escaped)) is True       # lexically fine...
    assert sr.looks_like_checklist(str(escaped)) is True   # ...and readable...
    assert sr._is_valid_claim_target(str(escaped)) is False  # ...but it escapes.

    # An ancestor DIRECTORY symlink escapes the same way.
    linked_work_area = worktree / ".agent-work" / "run2"
    try:
        linked_work_area.symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    except (OSError, NotImplementedError):  # pragma: no cover
        pytest.skip("directory symlinks unavailable on this host")
    assert sr._is_valid_claim_target(str(linked_work_area / "checklist.json")) is False


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


def test_stop_own_claim_from_another_worktree_now_blocks(proj):
    # (a) Production-shaped, and FLIPPED by #609 lane F g3. This payload carries
    # no agent_id, so the real PostToolUse path files the entry under the BARE
    # session_id: the claim is this agent's own, made while standing in another
    # worktree. It then ends its turn from elsewhere. The recorded worktree used
    # to differ from the payload cwd and the entry was skipped as "foreign",
    # which let a session walk away from its OWN mid-flight run; ownership is
    # the binding key now, so it is refused wherever it is standing.
    sub = proj / "subwt"
    subspine = write_spine(sub, make_spine([("g1", "in-progress")],
                                           imperatives={"g1": "OWN-CLAIM-MARKER keep going"}),
                           journal_lines=1)
    cmd = ('py scripts/checklist_engine.py --file .agent-work/run1/spine.json '
           'claim --session-id eng-9 --claimed-by commander')
    sr.handle_post_tool_use(_bash(cmd, session_id="shared", cwd=str(sub)), proj)
    sid_bindings = sr.load_binding(proj)["shared"]
    assert len(sid_bindings) == 1
    entry = next(iter(sid_bindings.values()))
    assert entry["worktree"] == str(sub)            # binding wrote the other wt
    assert sr._same_path(entry["spine"], subspine)  # via the real code path
    out = sr.decide_stop({"session_id": "shared", "cwd": str(proj)}, proj)
    assert out["decision"] == "block"
    assert "OWN-CLAIM-MARKER" in out["reason"]      # its own gate, imperative and all
    # And the nudge IS recorded now -- this is a real refusal, so it accrues a
    # strike toward the escape hatch like any other.
    assert list(sr.load_nudges(proj).keys()) == ["shared"]


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


# --- decide_stop: #202 multi-entry (one session_id, N bound spines) ---------

def test_stop_blocks_when_any_of_two_entries_is_mid_flight(proj):
    """One session_id bound to TWO spines: one already complete+released
    (not mid-flight), the other genuinely in-progress with an active lease.
    ANY non-foreign mid-flight entry must block the Stop."""
    sp_done = write_spine(proj, make_spine([("g1", "complete")], lease_status="released"), work="run-done")
    sp_open = write_spine(proj, make_spine([("g2", "in-progress")], imperatives={"g2": "keep going"}), work="run-open", journal_lines=1)
    bind(proj, "s1", sp_done)
    bind(proj, "s1", sp_open)  # merges onto sp_done's entry (bind() merges, doesn't clobber)
    assert len(sr.load_binding(proj)["s1"]) == 2

    out = sr.decide_stop({"session_id": "s1"}, proj)
    assert out["decision"] == "block"
    assert "g2" in out["reason"]
    assert "keep going" in out["reason"]


def test_stop_does_not_block_when_no_entry_is_mid_flight(proj):
    """One session_id bound to TWO spines, neither a genuine mid-flight
    blocker: one is unreadable, the other has a released lease. Neither should
    block -- the Stop is allowed.

    A FOREIGN WORKTREE used to be the first of these shapes and is no longer
    one of them (#609 lane F g3): a differing tree says nothing about who owns
    a spine, so it no longer excuses anything. The surviving non-blocking
    shapes are exactly unreadable, released, and honestly blocked."""
    sub = proj / "subwt"
    sp_unreadable = write_spine(sub, make_spine([("g1", "in-progress")]), journal_lines=1)
    sp_released = write_spine(proj, make_spine([("g2", "complete")], lease_status="released"), work="run-done")
    bind(proj, "shared", sp_unreadable, worktree=str(sub))
    bind(proj, "shared", sp_released)
    assert len(sr.load_binding(proj)["shared"]) == 2
    Path(sp_unreadable).write_text("{ not json", encoding="utf-8")  # bound, then corrupted

    out = sr.decide_stop({"session_id": "shared", "cwd": str(proj)}, proj)
    assert out == {}
    assert "shared" not in sr.load_nudges(proj)  # no mid-flight entry -> nudges untouched


def test_stop_old_active_binding_blocks_only_its_own_identity(proj):
    """#441: age alone never makes an active binding stop blocking Stop --
    reap only ever drops entries for a RELEASED or long-missing target, never
    a readable ACTIVE one, regardless of how old `claimed_at` is (see
    test_reap_binding_entries_matrix's `active_sp` case). The block also
    stays scoped to the OWNING identity: a foreign session holding no binding
    into this spine is never blocked by someone else's mid-flight run."""
    sp = write_spine(proj, make_spine([("g1", "in-progress")]), work="old-active-run")
    binding = {
        "owner-sid": {
            sp: {
                "spine": sp, "engine_session": "eng-1", "worktree": str(proj),
                "claimed_at": "2020-01-01T00:00:00+00:00",
            }
        }
    }
    sr.save_binding(proj, binding)

    out = sr.decide_stop({"session_id": "owner-sid", "cwd": str(proj)}, proj)
    assert out["decision"] == "block"

    out_foreign = sr.decide_stop({"session_id": "someone-else", "cwd": str(proj)}, proj)
    assert out_foreign == {}


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


def test_session_start_unreadable_skip_bound_reinject_fallback_reinject(proj):
    # (c) three-way: an UNREADABLE binding is skipped (no re-inject), a readable
    # binding re-injects from the BINDING, and with no binding at all the
    # _scan_active_spine fallback still re-injects.
    #
    # The first leg used to be a FOREIGN-WORKTREE binding, until #609 lane F g3
    # stopped decide_session_start from reading the tree. Both legs also used to
    # be written in the pre-#202 FLAT shape, which `load_binding` drops on sight
    # -- so each was silently answered by the fallback scan rather than by the
    # binding it named. They go through `bind()`'s real nested shape here, and
    # the readable leg is deliberately placed OUTSIDE proj/.agent-work so the
    # scan cannot reach it and only the binding can explain the marker.
    sub = proj / "subwt"
    subspine = write_spine(sub, make_spine([("g2", "in-progress")]), work="run-sub")
    bind(proj, "shared", subspine, worktree=str(sub))
    os.remove(subspine)  # bound, then the target vanishes
    binding = sr.load_binding(proj)
    binding["shared"][subspine]["claimed_at"] = sr._now_iso()  # inside the reap grace window
    sr.save_binding(proj, binding)
    out_unreadable = sr.decide_session_start({"session_id": "shared", "cwd": str(proj)}, proj)
    assert out_unreadable == {}  # unreadable -> skipped, and the scan finds none
    # -- readable binding, out of the scan's reach: re-injects from the binding
    alt = proj / "altwt"
    sp = write_spine(alt, make_spine([("g3", "in-progress")],
                                     imperatives={"g3": "BOUND-MARKER keep going"}), work="run-alt")
    bind(proj, "s1", sp, worktree=str(alt))
    assert sr._scan_active_spine(proj) == []  # nothing for the fallback to answer with
    out_bound = sr.decide_session_start({"session_id": "s1", "cwd": str(proj)}, proj)
    assert "RESUMING" in out_bound["hookSpecificOutput"]["additionalContext"]
    assert "BOUND-MARKER" in out_bound["hookSpecificOutput"]["additionalContext"]
    # -- no binding: fallback scan under proj/.agent-work still re-injects
    write_spine(proj, make_spine([("g4", "in-progress")]), work="run-scan")
    out_fallback = sr.decide_session_start({"session_id": "unbound", "cwd": str(proj)}, proj)
    assert "RESUMING" in out_fallback["hookSpecificOutput"]["additionalContext"]


def test_session_start_no_active_spine_returns_empty(proj):
    write_spine(proj, make_spine([("g2", "complete")]))  # all terminal
    assert sr.decide_session_start({"session_id": "s1"}, proj) == {}


def test_session_start_released_lease_returns_empty(proj):
    sp = write_spine(proj, make_spine([("g2", "in-progress")], lease_status="released"))
    bind(proj, "s1", sp)
    assert sr.decide_session_start({"session_id": "s1"}, proj) == {}


def test_session_start_prefers_own_binding_over_scan_with_multiple_active_spines(proj, monkeypatch):
    # Reviewer's live-reproduced BLOCK regression (#261 rework): decide_session_start's
    # existing-binding read used the OLD flat b.get("spine") shape, which is ALWAYS
    # None under the new nested {abs_spine_path: entry} shape (#202) -- b itself IS
    # that nested dict, and there is no literal "spine" key at that level. Every
    # SessionStart silently fell through to the ambiguous _scan_active_spine
    # fallback, which could return a COMPLETELY DIFFERENT session's spine. Two real,
    # on-disk, active-leased spines here; session bound to ONE via the REAL
    # handle_post_tool_use claim writer (not a hand-built fixture).
    own_spine_path = write_spine(
        proj,
        make_spine([("g1", "in-progress")], imperatives={"g1": "OWN-SPINE-MARKER keep going"}),
        work="own-run",
    )
    other_spine_path = write_spine(
        proj,
        make_spine([("g1", "in-progress")], imperatives={"g1": "OTHER-SPINE-MARKER wrong answer"}),
        work="other-run",
    )

    claim_cmd = (
        'py scripts/checklist_engine.py --file "%s" claim --session-id eng-9 '
        '--claimed-by commander --worktree .' % own_spine_path
    )
    claim_out = sr.handle_post_tool_use(
        {"session_id": "s1", "cwd": str(proj), "tool_input": {"command": claim_cmd}},
        proj,
    )
    assert claim_out == {}
    # Sanity: the real claim writer wrote a nested binding entry keyed by the
    # resolved absolute own-spine path (not the flat pre-#202 shape).
    assert sr.load_binding(proj)["s1"][own_spine_path]["spine"] == own_spine_path

    # Force the fallback scan to return the OTHER (wrong) spine deterministically
    # -- both spines are real and on-disk; this only removes dependence on real
    # filesystem glob ordering so the assertion below isolates exactly one
    # question: did decide_session_start use its OWN binding, or silently fall
    # through to the ambiguous scan?
    other_spine = sr.load_spine(other_spine_path)
    monkeypatch.setattr(sr, "_scan_active_spine", lambda project_dir: other_spine)

    out = sr.decide_session_start({"session_id": "s1", "cwd": str(proj)}, proj)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "OWN-SPINE-MARKER" in ctx
    assert "OTHER-SPINE-MARKER" not in ctx


# --- decide_session_start: #261 bind-on-resume (unambiguous-scan write) ----

def test_session_start_zero_matches_writes_no_binding(proj):
    """No .agent-work/*/spine.json at all -> the existing zero-match
    behavior (empty {} response) is unchanged, AND no binding file is
    created/written as a side effect of the scan finding nothing."""
    assert sr.decide_session_start({"session_id": "unbound", "cwd": str(proj)}, proj) == {}
    assert sr.load_binding(proj) == {}
    assert not sr.binding_path(proj).exists()


def test_session_start_ambiguous_scan_injects_context_but_writes_no_binding(proj):
    """Two real, on-disk, active-leased spines and NO prior binding for the
    calling sid -- decide_session_start still injects the advisory context
    (first match, same tone as before #261) but decision:no-bind-on-
    ambiguous-scan means it must NOT write a binding: the scan is
    ambiguous, so guessing which of the two spines this session actually
    owns would be exactly the wrong-binding failure class the launch order
    is protecting against."""
    write_spine(
        proj,
        make_spine([("g1", "in-progress")], imperatives={"g1": "FIRST-MARKER keep going"}),
        work="run-first",
    )
    write_spine(
        proj,
        make_spine([("g1", "in-progress")], imperatives={"g1": "SECOND-MARKER keep going"}),
        work="run-second",
    )
    out = sr.decide_session_start({"session_id": "ambiguous-sid", "cwd": str(proj)}, proj)
    assert "RESUMING" in out["hookSpecificOutput"]["additionalContext"]
    # No binding written for the ambiguous case, at all.
    assert sr.load_binding(proj) == {}


def test_session_start_unambiguous_scan_writes_binding(proj):
    """Exactly ONE real, on-disk, active-leased spine and no prior binding
    for the calling sid -- decide_session_start injects the advisory
    context AND writes a real binding entry (g1's per-spine-path writer
    shape) so a resumed/compacted session that never itself ran `claim`
    still resolves through gauge_writer_hook for the rest of its life."""
    sp = write_spine(
        proj,
        make_spine(
            [("g1", "in-progress")],
            session_id="eng-alone",
            imperatives={"g1": "ONLY-MARKER keep going"},
        ),
        work="run-alone",
    )
    assert sr.load_binding(proj) == {}  # nothing bound yet

    out = sr.decide_session_start({"session_id": "resuming-sid", "cwd": str(proj)}, proj)
    assert "ONLY-MARKER" in out["hookSpecificOutput"]["additionalContext"]

    binding = sr.load_binding(proj)
    assert "resuming-sid" in binding
    entry = binding["resuming-sid"][sp]
    assert entry["spine"] == sp
    assert entry["engine_session"] == "eng-alone"  # the SPINE's own lease session id
    assert entry["worktree"] == str(proj)
    assert entry["claimed_at"]


def test_session_start_no_bind_when_sid_missing(proj):
    """An unambiguous scan (exactly one active-leased spine) but no
    session_id on the payload at all -- there is nothing to key a binding
    by, so no write happens (fail-open: still injects context)."""
    write_spine(
        proj,
        make_spine([("g1", "in-progress")], imperatives={"g1": "keep going"}),
        work="run-alone",
    )
    out = sr.decide_session_start({"cwd": str(proj)}, proj)
    assert "RESUMING" in out["hookSpecificOutput"]["additionalContext"]
    assert sr.load_binding(proj) == {}


def test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding(proj):
    """The bind-on-unambiguous-scan write must not clobber a sibling
    abs_spine_path entry this sid already holds for a DIFFERENT spine (mirrors
    the real claim writer's leave-siblings-untouched behavior, #202). The
    sibling is made UNREADABLE on purpose: a readable one would satisfy the
    existing-binding read and the scan would never run at all, so an unreadable
    sibling is the shape that reaches this branch with a pre-existing entry
    still in place. It used to be a foreign-worktree sibling, until #609 lane F
    g3 stopped decide_session_start from reading the tree at all.

    Its `claimed_at` is refreshed to now because the reaper drops an
    unreadable target only once it is a day old (REAP_MISSING_TARGET_GRACE_
    SECONDS) -- a recently-claimed one is retained, which is the shape this
    test needs and also the realistic one: a spine deleted or archived out from
    under a live session."""
    sub = proj / "subwt"
    other_sp = write_spine(
        sub, make_spine([("gx", "in-progress")]), work="other-run"
    )
    bind(proj, "resuming-sid", other_sp, worktree=str(sub))
    os.remove(other_sp)  # bound, then the target vanishes
    binding = sr.load_binding(proj)
    binding["resuming-sid"][other_sp]["claimed_at"] = sr._now_iso()
    sr.save_binding(proj, binding)

    sp = write_spine(
        proj,
        make_spine([("g1", "in-progress")], session_id="eng-alone"),
        work="run-alone",
    )
    sr.decide_session_start({"session_id": "resuming-sid", "cwd": str(proj)}, proj)

    sid_bindings = sr.load_binding(proj)["resuming-sid"]
    assert set(sid_bindings.keys()) == {other_sp, sp}  # sibling survives, new one added


def test_session_start_real_engine_claim_produces_real_binding_diff(proj):
    """The single most important proof on this gate
    (lesson:verify-harness-field-and-drive-real-writer, #261): a hand-set
    cwd/session_id fixture would pass green even if production never
    delivers the field, hiding a silent no-op fix -- so every layer here is
    driven by the real production code, not a stub.

    (1) A REAL checklist_engine.py subprocess claims a REAL spine file
        (copied from the repo's own vendored IMPLEMENTER_PLAN template, not
        sr.make_spine()'s hand-built dict) -- the active lease on disk is
        genuinely engine-produced.
    (2) That exact claim command's text is fed through the REAL
        handle_post_tool_use, exactly as the harness's PostToolUse hook
        would deliver it after really running that command, writing a real
        binding entry via the real save_binding writer for an OWNER
        session (simulating "this spine was already claimed by someone
        else").
    (3) A SECOND, different, never-before-bound session_id then fires a
        SessionStart payload shaped like the real documented contract
        (session_id, cwd, transcript_path, hook_event_name, source --
        code.claude.com/docs/en/hooks, confirmed live in notes-261.md)
        straight at decide_session_start (the real function, no stub).

    The real `.spine-rail-binding.json` file on disk is shown, by content
    diff, to gain a fresh entry for that new session_id it did not have
    before the call. Run with `-s` so the printed before/after text lands
    in the evidence output verbatim.
    """
    work_dir = proj / ".agent-work" / "owner-run"
    work_dir.mkdir(parents=True)
    spine_path = work_dir / "spine.json"
    template_path = (
        _REPO_ROOT / "skills" / "implementer" / "templates" / "IMPLEMENTER_PLAN.template.json"
    )
    spine_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    spine_abs = str(spine_path.resolve())

    # (1) REAL engine subprocess claims the REAL spine file.
    claim_argv = [
        sys.executable, str(_REPO_ROOT / "scripts" / "checklist_engine.py"),
        "--file", spine_abs, "claim",
        "--session-id", "eng-owner", "--claimed-by", "commander", "--worktree", ".",
    ]
    result = subprocess.run(claim_argv, cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert result.returncode == 0, "real engine claim subprocess failed: " + result.stdout + result.stderr
    claimed_spine = sr.load_spine(spine_abs)
    assert claimed_spine["engine_session"]["status"] == "active"
    assert claimed_spine["engine_session"]["session_id"] == "eng-owner"

    # (2) REAL PostToolUse handler parses that exact claim command and
    # writes a real binding entry via the real save_binding writer.
    claim_cmd = (
        'py scripts/checklist_engine.py --file "%s" claim --session-id eng-owner '
        '--claimed-by commander --worktree .' % spine_abs
    )
    post_out = sr.handle_post_tool_use(
        {"session_id": "owner-harness-sid", "cwd": str(proj), "tool_input": {"command": claim_cmd}},
        proj,
    )
    assert post_out == {}

    binding_file = sr.binding_path(proj)
    before_text = binding_file.read_text(encoding="utf-8")
    before = json.loads(before_text)
    assert "new-resuming-sid" not in before
    print("\n--- .spine-rail-binding.json BEFORE decide_session_start (real SessionStart write) ---")
    print(before_text)

    # (3) A DIFFERENT, never-before-seen session resumes/compacts: a
    # SessionStart payload shaped like the real documented contract.
    session_start_payload = {
        "session_id": "new-resuming-sid",
        "transcript_path": str(proj / "transcript.jsonl"),
        "cwd": str(proj),
        "hook_event_name": "SessionStart",
        "source": "resume",
    }
    out = sr.decide_session_start(session_start_payload, proj)
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "ACTIVE m0-context" in out["hookSpecificOutput"]["additionalContext"]

    after_text = binding_file.read_text(encoding="utf-8")
    print("--- .spine-rail-binding.json AFTER decide_session_start ---")
    print(after_text)

    assert before_text != after_text
    after = json.loads(after_text)
    assert "new-resuming-sid" in after
    new_sid_bindings = after["new-resuming-sid"]
    assert len(new_sid_bindings) == 1
    new_key, new_entry = next(iter(new_sid_bindings.items()))
    assert sr._same_path(new_key, spine_abs)  # resolved path, may differ in exact
                                               # string form from glob vs .resolve()
    assert new_entry["spine"] == new_key
    assert new_entry["engine_session"] == "eng-owner"  # the SPINE's own lease session id
    assert new_entry["worktree"] == str(proj)
    assert new_entry["claimed_at"]
    # The owner's own binding entry (from step 2) survives untouched.
    assert after["owner-harness-sid"][spine_abs]["engine_session"] == "eng-owner"


# --- handle_post_tool_use ----------------------------------------------------

def _bash(command, session_id="s1", cwd=None):
    data = {"session_id": session_id, "tool_input": {"command": command}}
    if cwd:
        data["cwd"] = cwd
    return data


def test_post_claim_writes_binding(proj):
    # Reconciled for #202's nested shape: a claim now writes
    # binding[sid][abs_spine] = {...} (nested by resolved spine path), not a
    # single flat binding[sid] = {...} -- the old single-entry-per-session_id
    # scenario is impossible once one session_id can hold multiple bindings.
    cmd = 'py scripts/checklist_engine.py --file .agent-work/run1/spine.json claim --session-id eng-9 --claimed-by commander --worktree .'
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run1")
    out = sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    assert out == {}
    binding = sr.load_binding(proj)
    assert "s1" in binding
    sid_bindings = binding["s1"]
    assert len(sid_bindings) == 1
    abs_spine, entry = next(iter(sid_bindings.items()))
    assert entry["spine"] == abs_spine
    assert entry["engine_session"] == "eng-9"
    assert entry["spine"].endswith("spine.json")
    assert Path(entry["spine"]).is_absolute()
    assert entry["claimed_at"]  # new field: recorded, non-empty


def test_post_claim_absolute_file_preserved(proj):
    # Reconciled for #202's nested shape: keyed by the resolved abs_spine
    # path itself, so the entry now lives under binding["s1"][abspath].
    # #441: an absolute --file claim target is now validated (rung 0 is
    # ground truth about WHERE, never about whether it is a real checklist),
    # so the target must actually exist.
    abspath = put_checklist(proj, "run1")
    cmd = 'py C:/x/checklist_engine.py --file "%s" claim --session-id eng-2' % abspath
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    assert sr.load_binding(proj)["s1"][abspath]["spine"] == abspath


def test_post_release_deletes_binding_and_nudge(proj):
    # Reconciled for #202's nested shape: bind() now writes a nested single
    # entry; release must remove that one abs_spine entry, which also empties
    # sid's binding entirely (no other spines bound), so "s1" is fully absent.
    sp = str(proj / ".agent-work" / "run1" / "spine.json")
    bind(proj, "s1", sp)
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run1")
    sr.save_nudges(proj, {"s1": {"count": 2, "journal_seq": 1, "active_id": "g1"}})
    cmd = 'py scripts/checklist_engine.py --file .agent-work/run1/spine.json release --session-id eng-9'
    out = sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    assert out == {}
    assert "s1" not in sr.load_binding(proj)
    assert "s1" not in sr.load_nudges(proj)


# --- #202: multi-entry binding (two distinct spines, one session_id) -------

def test_post_claim_two_different_spines_same_worktree_no_clobber(proj):
    """Two claims under the SAME session_id, for two DIFFERENT spines, both
    resolved from the SAME worktree (cwd) -- both must persist as distinct
    entries; neither clobbers the other (decision:key-binding-by-spine-path-
    not-worktree-or-cwd -- keying by worktree alone would have collided these
    two)."""
    cmd_a = 'py scripts/checklist_engine.py --file .agent-work/run-a/spine.json claim --session-id eng-a --claimed-by commander'
    cmd_b = 'py scripts/checklist_engine.py --file .agent-work/run-b/spine.json claim --session-id eng-b --claimed-by commander'
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-a")
    put_checklist(proj, "run-b")
    sr.handle_post_tool_use(_bash(cmd_a, session_id="shared", cwd=str(proj)), proj)
    sr.handle_post_tool_use(_bash(cmd_b, session_id="shared", cwd=str(proj)), proj)

    sid_bindings = sr.load_binding(proj)["shared"]
    assert len(sid_bindings) == 2
    abs_a = str((proj / ".agent-work" / "run-a" / "spine.json").resolve())
    abs_b = str((proj / ".agent-work" / "run-b" / "spine.json").resolve())
    assert set(sid_bindings.keys()) == {abs_a, abs_b}
    assert sid_bindings[abs_a]["engine_session"] == "eng-a"
    assert sid_bindings[abs_b]["engine_session"] == "eng-b"


def test_spawn_binding_transaction_red_green(proj):
    """Real spawned PostToolUse claim writers retain every serial update.

    The start barrier releases distinct processes into the production claim
    handler together.  Before #441 every process independently loaded the
    registry and replaced it after changing only its own snapshot, so the
    final valid JSON reliably contained only a subset of these entries.
    """
    ctx = multiprocessing.get_context("spawn")
    writer_count = 16
    barrier = ctx.Barrier(writer_count + 1)
    spines = [put_checklist(proj, "spawn-%02d" % i) for i in range(writer_count)]
    processes = [
        ctx.Process(
            target=_spawn_claim_writer,
            args=(str(proj), spines[i], i, barrier),
        )
        for i in range(writer_count)
    ]
    for process in processes:
        process.start()
    barrier.wait(timeout=30)
    for process in processes:
        process.join(timeout=30)
    assert [process.exitcode for process in processes] == [0] * writer_count

    binding_text = sr.binding_path(proj).read_text(encoding="utf-8")
    binding = json.loads(binding_text)
    expected = {"spawn-shared#writer-%d" % i for i in range(writer_count)}
    actual = set(binding)
    print("\nspawned binding final JSON keys (%d/%d): %s" %
          (len(actual), len(expected), sorted(actual)))
    assert actual == expected, "lost-update: missing %s" % sorted(expected - actual)


def test_spawn_binding_sessionstart_claim_mixed_writer_race(proj):
    """#441 m3: real spawned PostToolUse claim writers AND real spawned
    SessionStart bind-on-resume writers, contending on the SAME registry file
    at the same instant, retain every serial update from BOTH writer kinds --
    proving the transaction seam serializes across the mixed-writer topology,
    not just within one writer's own code path.

    Claim targets have every item already `complete` so `active_id` is None
    and `_scan_active_spine` skips them -- keeping the scan unambiguous onto
    the single genuinely-active `resume_spine` every SessionStart worker
    races to bind.
    """
    ctx = multiprocessing.get_context("spawn")
    claim_count = 8
    resume_count = 8
    barrier = ctx.Barrier(claim_count + resume_count + 1)

    resume_spine = write_spine(
        proj, make_spine([("g1", "in-progress")], session_id="orig-eng"), work="resume-target"
    )
    claim_spines = [
        write_spine(proj, make_spine([("g1", "complete")]), work="mixed-claim-%02d" % i)
        for i in range(claim_count)
    ]

    processes = [
        ctx.Process(target=_spawn_claim_writer, args=(str(proj), claim_spines[i], i, barrier))
        for i in range(claim_count)
    ] + [
        ctx.Process(target=_spawn_session_start_writer,
                    args=(str(proj), "resume-%02d" % i, barrier))
        for i in range(resume_count)
    ]
    for process in processes:
        process.start()
    barrier.wait(timeout=30)
    for process in processes:
        process.join(timeout=30)
    assert [process.exitcode for process in processes] == [0] * len(processes)

    binding = json.loads(sr.binding_path(proj).read_text(encoding="utf-8"))
    expected_claim_keys = {"spawn-shared#writer-%d" % i for i in range(claim_count)}
    expected_resume_keys = {"resume-%02d" % i for i in range(resume_count)}
    actual = set(binding)
    print("\nmixed-writer race final keys (%d/%d): %s"
          % (len(actual), claim_count + resume_count, sorted(actual)))
    assert actual == expected_claim_keys | expected_resume_keys, (
        "lost-update: missing %s" % sorted((expected_claim_keys | expected_resume_keys) - actual)
    )
    for i, spine in enumerate(claim_spines):
        assert set(binding["spawn-shared#writer-%d" % i]) == {spine}
    for i in range(resume_count):
        assert set(binding["resume-%02d" % i]) == {resume_spine}


# --- #441 m1: named lock/replace/Windows-adapter failure contracts -----------
#
# All four fail-open tests below monkeypatch the module's lock/replace SEAMS
# (`_try_lock`, `LOCK_RETRY_ATTEMPTS`, `LOCK_ACQUIRE_TIMEOUT_SECONDS`,
# `os.replace`) rather than racing real processes or sleeping on wall-clock
# time -- deterministic, and each one isolates exactly ONE named bound.

def test_binding_lock_contention_fails_open(proj, monkeypatch):
    """Sustained contention (every attempt fails, plenty of time left) exhausts
    the ATTEMPTS bound, not the timeout bound: the handler still fails open,
    the registry is never created, and the retry loop tried exactly
    LOCK_RETRY_ATTEMPTS times."""
    put_checklist(proj, "run1")
    calls = []

    def _always_busy(fileobj):
        calls.append(1)
        return False

    monkeypatch.setattr(sr, "_try_lock", _always_busy)
    monkeypatch.setattr(sr, "LOCK_RETRY_ATTEMPTS", 5)
    monkeypatch.setattr(sr, "LOCK_RETRY_INTERVAL_SECONDS", 0.0)
    monkeypatch.setattr(sr, "LOCK_ACQUIRE_TIMEOUT_SECONDS", 1000.0)

    out = sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(proj)), proj)
    assert out == {}
    assert not sr.binding_path(proj).exists()
    assert len(calls) == 5


def test_binding_lock_timeout_fails_open(proj, monkeypatch):
    """A zero-second deadline fails open on the very first contended attempt,
    long before LOCK_RETRY_ATTEMPTS could ever be exhausted -- proving the
    TIMEOUT bound independently of the attempts bound."""
    put_checklist(proj, "run1")
    calls = []

    def _always_busy(fileobj):
        calls.append(1)
        return False

    monkeypatch.setattr(sr, "_try_lock", _always_busy)
    monkeypatch.setattr(sr, "LOCK_RETRY_ATTEMPTS", 1_000_000)
    monkeypatch.setattr(sr, "LOCK_RETRY_INTERVAL_SECONDS", 0.0)
    monkeypatch.setattr(sr, "LOCK_ACQUIRE_TIMEOUT_SECONDS", 0.0)

    out = sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(proj)), proj)
    assert out == {}
    assert not sr.binding_path(proj).exists()
    assert len(calls) < 1_000_000  # the deadline stopped it, not the attempt budget


def test_binding_lock_api_failure_fails_open(proj, monkeypatch):
    """A genuine lock-API failure (not mere contention) is caught, not
    propagated, and the loop does not retry past it -- one failing call is
    enough to fail the transaction open."""
    put_checklist(proj, "run1")
    calls = []

    def _raises(fileobj):
        calls.append(1)
        raise OSError(errno.ENOLCK, "no locks available")

    monkeypatch.setattr(sr, "_try_lock", _raises)

    out = sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(proj)), proj)
    assert out == {}
    assert not sr.binding_path(proj).exists()
    assert len(calls) == 1  # fails open immediately, no retry after an API error


def test_binding_replace_failure_fails_open(proj, monkeypatch):
    """A replace failure (disk full, permission error, ...) is caught after a
    REAL lock was actually acquired: the handler still fails open, the
    registry is left exactly as it was, and the unique temp file is cleaned
    up rather than left behind."""
    put_checklist(proj, "run1")

    real_replace = os.replace

    def _boom(src, dst):
        raise OSError(errno.ENOSPC, "no space left on device")

    monkeypatch.setattr(sr.os, "replace", _boom)
    try:
        out = sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(proj)), proj)
    finally:
        monkeypatch.setattr(sr.os, "replace", real_replace)
    assert out == {}
    assert not sr.binding_path(proj).exists()
    leftover_tmp = list((proj / ".agent-work").glob("*.tmp"))
    assert leftover_tmp == [], "temp file not cleaned up: %s" % leftover_tmp


class _FakeMsvcrt:
    """A minimal stand-in for the `msvcrt` module's locking surface, so the
    Windows byte-range adapter's contract is unit-tested on every platform
    (#441), not only a real Windows host."""

    LK_NBLCK = 1
    LK_UNLCK = 2

    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail

    def locking(self, fd, mode, nbytes):
        self.calls.append((fd, mode, nbytes))
        if self.fail:
            raise OSError(errno.EACCES, "locking violation")


def test_windows_lock_adapter_contract(tmp_path):
    """The Windows adapter's full contract: `_open_lock_file` initializes one
    byte so there is always something to lock; `_windows_try_lock` seeks to
    the start of the file and locks exactly its first byte via
    `LK_NBLCK`, returning True on success; `_windows_unlock` seeks back and
    unlocks the same byte via `LK_UNLCK`; and a lock failure (contention or
    any other locking-API error) returns False rather than raising."""
    lock_file = sr._open_lock_file(tmp_path)
    try:
        assert sr._lock_path(tmp_path).exists()
        assert sr._lock_path(tmp_path).stat().st_size >= 1

        lock_file.seek(5)  # move off zero -- the adapter must seek back itself
        fake = _FakeMsvcrt()
        assert sr._windows_try_lock(lock_file, fake) is True
        assert fake.calls == [(lock_file.fileno(), _FakeMsvcrt.LK_NBLCK, 1)]

        lock_file.seek(5)
        sr._windows_unlock(lock_file, fake)
        assert fake.calls[-1] == (lock_file.fileno(), _FakeMsvcrt.LK_UNLCK, 1)
    finally:
        lock_file.close()

    lock_file2 = sr._open_lock_file(tmp_path)
    try:
        failing = _FakeMsvcrt(fail=True)
        assert sr._windows_try_lock(lock_file2, failing) is False  # fails open, no raise
        sr._windows_unlock(lock_file2, failing)  # never raises even after a failed lock
    finally:
        lock_file2.close()


# --- #441 m2: the transaction-internal safe reaper's full matrix ------------

def test_reap_binding_entries_matrix(proj):
    """`_reap_binding_entries` driven directly with an injected `now` -- no
    wall-clock sleeps -- over every named branch: malformed entry, malformed
    per-key value, readable released (goes immediately), readable non-released
    (stays regardless of age), missing target just past the 24h grace (goes),
    missing target just inside it (stays), missing target with untrustworthy
    age -- naive or absent `claimed_at` (stays either way), an empty per-key
    map after reaping (the key itself goes), and an old-shape per-key value
    (passed through untouched, never migrated)."""
    now = "2026-08-15T12:00:00+00:00"

    active_sp = write_spine(
        proj, make_spine([("g1", "in-progress")], lease_status="active"), work="active-run"
    )
    released_sp = write_spine(
        proj, make_spine([("g1", "complete")], lease_status="released"), work="released-run"
    )
    missing_old = str(proj / ".agent-work" / "gone-old" / "spine.json")
    missing_fresh = str(proj / ".agent-work" / "gone-fresh" / "spine.json")
    missing_naive_ts = str(proj / ".agent-work" / "gone-naive" / "spine.json")
    missing_no_ts = str(proj / ".agent-work" / "gone-no-ts" / "spine.json")

    def _entry(spine_path, claimed_at):
        e = {"spine": spine_path, "engine_session": "eng-x", "worktree": str(proj)}
        if claimed_at is not None:
            e["claimed_at"] = claimed_at
        return e

    binding = {
        "s1": {
            active_sp: _entry(active_sp, "2020-01-01T00:00:00+00:00"),  # old, active -> stays
            released_sp: _entry(released_sp, now),  # readable + released -> goes
            missing_old: _entry(missing_old, "2026-08-14T11:59:59+00:00"),  # 24h+1s -> goes
            missing_fresh: _entry(missing_fresh, "2026-08-14T12:00:01+00:00"),  # 24h-1s -> stays
            missing_naive_ts: _entry(missing_naive_ts, "2026-08-14T00:00:00"),  # naive -> stays
            missing_no_ts: _entry(missing_no_ts, None),  # absent -> stays
            "malformed-entry": "not-a-dict",  # malformed entry -> goes
        },
        "empty-after-reap": {
            "gone": _entry(str(proj / ".agent-work" / "reaps-to-empty" / "spine.json"),
                            "2020-01-01T00:00:00+00:00"),  # the only entry reaps away
        },
        "malformed-outer-value": "not-a-dict-either",  # goes
        "old-shape-key": {"spine": "somewhere", "engine_session": "eng-y", "worktree": "elsewhere"},
    }

    reaped = sr._reap_binding_entries(binding, now)

    assert set(reaped.get("s1", {})) == {active_sp, missing_fresh, missing_naive_ts, missing_no_ts}
    assert "empty-after-reap" not in reaped  # emptied entirely -> key dropped
    assert "malformed-outer-value" not in reaped
    assert reaped["old-shape-key"] == binding["old-shape-key"]  # untouched, not migrated


def test_reap_binding_entries_never_raises_and_keeps_data_on_error(proj, monkeypatch):
    """A defect inside the reaper must fail TOWARD keeping data, not toward
    silently discarding the registry."""
    monkeypatch.setattr(sr, "load_spine", lambda *_: (_ for _ in ()).throw(RuntimeError("boom")))
    binding = {"s1": {"/x/spine.json": {"spine": "/x/spine.json", "claimed_at": "2020-01-01T00:00:00+00:00"}}}
    assert sr._reap_binding_entries(binding, "2026-08-15T12:00:00+00:00") == binding


def test_post_claim_symlink_escape_target_binds_nothing(proj):
    """#441: a symlink AT the exact lexical `.agent-work/<work>/spine.json`
    shape, pointing to a real checklist OUTSIDE that containment, must not
    validate -- the lexical shape check alone would be fooled, so the
    validator re-checks the fully resolved path."""
    outside = proj.parent / "outside-checklist"
    outside.mkdir(exist_ok=True)
    real_target = outside / "spine.json"
    real_target.write_text(_checklist_json(), encoding="utf-8")

    link_dir = proj / ".agent-work" / "escape-run"
    link_dir.mkdir(parents=True, exist_ok=True)
    link_path = link_dir / "spine.json"
    link_path.symlink_to(real_target)

    cmd = 'python scripts/checklist_engine.py --file "%s" claim --session-id eng-2' % str(link_path)
    out = sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_claim_two_different_spines_different_worktrees_no_clobber(proj):
    """Same session_id, two DIFFERENT spines resolved from two DIFFERENT
    worktrees -- both persist as distinct entries. This is the case a
    'worktree' key (even a correctly-derived one) would ALSO collide if both
    spines happened to share a worktree; here they don't even share one, so
    it is doubly clear the key must be the spine path itself, not the
    worktree."""
    wt_a = proj / "wt-a"
    wt_b = proj / "wt-b"
    # #440: each worktree really holds its own spine, so the payload cwd (rung
    # 3) validates for each claim in turn -- which is exactly what this test
    # already meant by "resolved from two DIFFERENT worktrees".
    put_checklist(wt_a, "run-a")
    put_checklist(wt_b, "run-b")
    cmd_a = 'py scripts/checklist_engine.py --file .agent-work/run-a/spine.json claim --session-id eng-a --claimed-by commander'
    cmd_b = 'py scripts/checklist_engine.py --file .agent-work/run-b/spine.json claim --session-id eng-b --claimed-by commander'
    sr.handle_post_tool_use(_bash(cmd_a, session_id="shared", cwd=str(wt_a)), proj)
    sr.handle_post_tool_use(_bash(cmd_b, session_id="shared", cwd=str(wt_b)), proj)

    sid_bindings = sr.load_binding(proj)["shared"]
    assert len(sid_bindings) == 2
    abs_a = str((wt_a / ".agent-work" / "run-a" / "spine.json").resolve())
    abs_b = str((wt_b / ".agent-work" / "run-b" / "spine.json").resolve())
    assert set(sid_bindings.keys()) == {abs_a, abs_b}
    assert sid_bindings[abs_a]["worktree"] == str(wt_a)
    assert sid_bindings[abs_b]["worktree"] == str(wt_b)


def test_post_claim_same_spine_reclaim_overwrites_only_itself(proj):
    """A THIRD claim for the SAME spine (same session_id, same abs_spine)
    overwrites only that one entry -- the sibling entry for the other spine
    survives untouched."""
    cmd_a = 'py scripts/checklist_engine.py --file .agent-work/run-a/spine.json claim --session-id eng-a --claimed-by commander'
    cmd_b = 'py scripts/checklist_engine.py --file .agent-work/run-b/spine.json claim --session-id eng-b --claimed-by commander'
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-a")
    put_checklist(proj, "run-b")
    sr.handle_post_tool_use(_bash(cmd_a, session_id="shared", cwd=str(proj)), proj)
    sr.handle_post_tool_use(_bash(cmd_b, session_id="shared", cwd=str(proj)), proj)
    before = sr.load_binding(proj)["shared"]
    abs_a = str((proj / ".agent-work" / "run-a" / "spine.json").resolve())
    abs_b = str((proj / ".agent-work" / "run-b" / "spine.json").resolve())
    claimed_at_b_before = before[abs_b]["claimed_at"]

    # re-claim spine A under a NEW engine_session (simulates a genuine re-claim)
    cmd_a_reclaim = 'py scripts/checklist_engine.py --file .agent-work/run-a/spine.json claim --session-id eng-a-2 --claimed-by commander'
    sr.handle_post_tool_use(_bash(cmd_a_reclaim, session_id="shared", cwd=str(proj)), proj)

    after = sr.load_binding(proj)["shared"]
    assert len(after) == 2  # still exactly two entries -- no new key, no lost sibling
    assert after[abs_a]["engine_session"] == "eng-a-2"  # overwritten
    assert after[abs_b]["engine_session"] == "eng-b"  # untouched
    assert after[abs_b]["claimed_at"] == claimed_at_b_before  # untouched, not re-stamped


def test_post_release_removes_only_matching_entry_sibling_intact(proj):
    """release removes ONLY the entry for the released spine, leaving a
    sibling entry for a different spine under the same session_id intact."""
    cmd_a = 'py scripts/checklist_engine.py --file .agent-work/run-a/spine.json claim --session-id eng-a --claimed-by commander'
    cmd_b = 'py scripts/checklist_engine.py --file .agent-work/run-b/spine.json claim --session-id eng-b --claimed-by commander'
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-a")
    put_checklist(proj, "run-b")
    sr.handle_post_tool_use(_bash(cmd_a, session_id="shared", cwd=str(proj)), proj)
    sr.handle_post_tool_use(_bash(cmd_b, session_id="shared", cwd=str(proj)), proj)

    cmd_release_a = 'py scripts/checklist_engine.py --file .agent-work/run-a/spine.json release --session-id eng-a'
    out = sr.handle_post_tool_use(_bash(cmd_release_a, session_id="shared", cwd=str(proj)), proj)
    assert out == {}

    sid_bindings = sr.load_binding(proj)["shared"]
    abs_b = str((proj / ".agent-work" / "run-b" / "spine.json").resolve())
    assert set(sid_bindings.keys()) == {abs_b}  # only the released one is gone


def test_post_release_last_entry_removes_sid_key_entirely(proj):
    """Releasing the only bound spine for a session_id removes the sid key
    entirely (tidy, cosmetic -- not load-bearing)."""
    cmd = 'py scripts/checklist_engine.py --file .agent-work/run-a/spine.json claim --session-id eng-a --claimed-by commander'
    # #440: the claimed spine must REALLY EXIST -- a relative --file now
    # resolves only to a candidate root that validates as a checklist.
    put_checklist(proj, "run-a")
    sr.handle_post_tool_use(_bash(cmd, session_id="shared", cwd=str(proj)), proj)
    assert "shared" in sr.load_binding(proj)

    cmd_release = 'py scripts/checklist_engine.py --file .agent-work/run-a/spine.json release --session-id eng-a'
    sr.handle_post_tool_use(_bash(cmd_release, session_id="shared", cwd=str(proj)), proj)
    assert "shared" not in sr.load_binding(proj)


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


# --- nested binding shape (#202) ---------------------------------------------

def test_binding_round_trips_new_nested_shape(proj):
    nested = {
        "s1": {
            "C:/wt/a/spine.json": {
                "spine": "C:/wt/a/spine.json",
                "engine_session": "eng-1",
                "worktree": "C:/wt/a",
                "claimed_at": "2026-07-27T00:00:00+00:00",
            },
            "C:/wt/b/spine.json": {
                "spine": "C:/wt/b/spine.json",
                "engine_session": "eng-2",
                "worktree": "C:/wt/b",
                "claimed_at": "2026-07-27T00:00:01+00:00",
            },
        }
    }
    sr.save_binding(proj, nested)
    assert sr.load_binding(proj) == nested


def test_old_shape_entry_loads_as_absent_real_fixture(proj):
    # Real on-disk shape of C:/Programs/constellation-skills/.agent-work/.spine-rail-binding.json
    # as of this run (5 flat, single-entry-per-session_id entries -- read, not
    # guessed): {session_id: {spine, engine_session, worktree}}.
    old_shape_fixture = {
        "5d549ce6-490f-4654-a751-085085ccd9ec": {
            "spine": "C:\\Programs\\constellation-skills\\.agent-work\\explore-shared-understanding\\spine.json",
            "engine_session": "explore-shared-understanding",
            "worktree": "C:\\Programs\\constellation-skills",
        },
        "90ab6530-cb8d-44c5-b8ca-e35949797062": {
            "spine": "C:\\Programs\\constellation-skills\\.agent-work\\explore-context-governor\\spine.json",
            "engine_session": "explore-context-governor",
            "worktree": "C:\\Programs\\constellation-skills",
        },
        "3c5f5837-b120-46a4-915f-1d10f3d7f6db": {
            "spine": "C:\\Programs\\constellation-skills\\.agent-work\\explore-design-thrust\\spine.json",
            "engine_session": "explore-design-thrust",
            "worktree": "C:\\Programs\\constellation-skills",
        },
        "7a69e7fd-1c86-43c0-8847-1428f02eb616": {
            "spine": "C:\\Programs\\constellation-skills\\.agent-work\\epic-226\\spine.json",
            "engine_session": "admiral-epic-226",
            "worktree": "C:\\Programs\\constellation-skills",
        },
        "05c5ec39-68b1-45f0-a55f-d78261009133": {
            "spine": "C:\\Programs\\constellation-skills-wt\\governor-261\\.agent-work\\governor-261\\spine.json",
            "engine_session": "commander-261",
            "worktree": "C:\\Programs\\constellation-skills",
        },
    }
    p = sr.binding_path(proj)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(old_shape_fixture), encoding="utf-8")

    loaded = sr.load_binding(proj)
    # every old-shape session_id loads as absent -- no crash, no silent
    # misinterpretation of "spine" as an abs_spine_path key
    assert loaded == {}
    for sid in old_shape_fixture:
        assert sid not in loaded


def test_load_binding_mixed_old_and_new_shape_sessions(proj):
    # one session still old-shape (untouched by any new-shape writer yet), one
    # already re-claimed under the new writer -- old one drops, new one loads.
    mixed = {
        "old-sid": {"spine": "C:/x/spine.json", "engine_session": "e1", "worktree": "C:/x"},
        "new-sid": {
            "C:/y/spine.json": {
                "spine": "C:/y/spine.json",
                "engine_session": "e2",
                "worktree": "C:/y",
                "claimed_at": "2026-07-27T00:00:00+00:00",
            }
        },
    }
    p = sr.binding_path(proj)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(mixed), encoding="utf-8")

    loaded = sr.load_binding(proj)
    assert "old-sid" not in loaded
    assert loaded["new-sid"] == mixed["new-sid"]


# --- #440: validated candidate-root resolution of a relative --file ----------
#
# The defect these cover returns a PLAUSIBLE-LOOKING WRONG ANSWER (a binding
# naming a same-named path inside the main checkout), so every test below is
# written to fail against the pre-#440 hook, not merely to describe the new one.


def _checklist_json(work_id="run1"):
    """The weakest thing that positively identifies a checklist: a JSON object
    with a top-level `items` LIST. Matches what load_spine/active_id actually
    require."""
    return json.dumps({
        "work_id": work_id,
        "type": "gated",
        "items": ["g1"],
        "tasks": {"g1": {"id": "g1", "status": "pending", "imperative": "do g1"}},
    })


def put_checklist(root, work="run1"):
    """Write a REAL checklist at <root>/.agent-work/<work>/spine.json and return
    its resolved absolute path."""
    d = Path(root) / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    p = d / "spine.json"
    p.write_text(_checklist_json(work), encoding="utf-8")
    return str(p.resolve())


def _claim(work="run1", engine_session="eng-9", prefix="python scripts/checklist_engine.py"):
    return ('%s --file .agent-work/%s/spine.json claim --session-id %s '
            '--claimed-by commander' % (prefix, work, engine_session))


def _only_entry(proj, sid="s1"):
    sid_bindings = sr.load_binding(proj)[sid]
    assert len(sid_bindings) == 1, sid_bindings
    return next(iter(sid_bindings.items()))


def test_looks_like_checklist_accepts_a_real_checklist(tmp_path):
    p = tmp_path / "spine.json"
    p.write_text(_checklist_json(), encoding="utf-8")
    assert sr.looks_like_checklist(str(p)) is True


def test_looks_like_checklist_rejects_phantom_leftovers(tmp_path):
    """A bare exists() test would be DECOYED by the very bug being fixed: the
    old defect creates phantom .agent-work/<work_id>/ trees in the main
    checkout. Each row below EXISTS and must still be rejected."""
    rows = {
        "gauge.json": json.dumps({"work_id": "run1", "band": "SOFT", "tokens": 120000}),
        "not-json.json": "{ not json",
        "list.json": json.dumps(["g1", "g2"]),
        "items-not-a-list.json": json.dumps({"items": {"g1": {}}}),
        "no-items.json": json.dumps({"work_id": "run1", "tasks": {}}),
        "empty.json": "",
    }
    for name, text in rows.items():
        p = tmp_path / name
        p.write_text(text, encoding="utf-8")
        assert p.exists()
        assert sr.looks_like_checklist(str(p)) is False, name
    assert sr.looks_like_checklist(str(tmp_path / "absent.json")) is False
    assert sr.looks_like_checklist(None) is False
    assert sr.looks_like_checklist(str(tmp_path)) is False  # a DIRECTORY


def test_post_claim_no_candidate_validates_writes_nothing_store_byte_unchanged(proj):
    """The fail-closed core: nothing on disk answers the relative --file, so
    NO entry is written and the store is byte-unchanged.

    Pre-#440 this wrote a confident wrong entry naming a path that does not
    exist -- 60 of 64 live entries measured 2026-08-05."""
    store = sr.binding_path(proj)
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps({"other-sid": {}}), encoding="utf-8")
    before = store.read_bytes()

    out = sr.handle_post_tool_use(_bash(_claim("ghost"), cwd=str(proj)), proj)
    assert out == {}
    assert store.read_bytes() == before
    assert "s1" not in sr.load_binding(proj)


def test_post_claim_payload_cwd_wins_when_it_validates(proj):
    """Rung 3 keeps today's behaviour and now SAYS SO in path_source."""
    spine = put_checklist(proj, "run1")
    sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == spine
    assert entry["path_source"] == "payload_cwd"
    assert entry["spine"] == spine
    assert entry["engine_session"] == "eng-9"
    assert entry["worktree"] == str(proj)
    assert entry["claimed_at"]


def test_post_claim_falls_through_to_project_dir_when_cwd_does_not_validate(proj):
    """Rung 5. The payload cwd is a sibling directory holding NO checklist; the
    project dir does. Pre-#440 the cwd was trusted blindly and the binding named
    a path under `elsewhere/` that does not exist."""
    elsewhere = proj.parent / "elsewhere"
    elsewhere.mkdir(exist_ok=True)
    spine = put_checklist(proj, "run1")
    sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(elsewhere)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == spine
    assert entry["path_source"] == "project_dir"


def test_post_claim_absolute_file_is_rung_zero_and_skips_the_ladder(proj):
    """Rung 0: an absolute --file is ground truth about WHERE the caller
    means, so resolution returns it directly without walking the guessed
    candidate ladder -- but (#441) the resolved target must still be a real,
    contained checklist before a CLAIM records it; only the ladder-walk is
    skipped, not claim-target validation."""
    abspath = put_checklist(proj, "gone")
    cmd = 'python C:/x/checklist_engine.py --file "%s" claim --session-id eng-2' % abspath
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == abspath
    assert entry["path_source"] == "absolute"


def test_post_claim_absolute_file_naming_a_nonexistent_target_binds_nothing(proj):
    """#441: claim-target validation applies even at rung 0. An absolute
    --file naming a target that is not (or no longer) a real checklist binds
    nothing -- a confident wrong record is worse than silence, the same
    posture `resolve_spine_candidate`'s guessed rungs already take."""
    abspath = str(proj / ".agent-work" / "gone" / "spine.json")
    cmd = 'python C:/x/checklist_engine.py --file "%s" claim --session-id eng-2' % abspath
    out = sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_claim_path_source_is_additive_and_key_shape_untouched(proj):
    """path_source is an ADDITIVE VALUE field: the binding KEY shape (#419) and
    every pre-existing value field are unchanged."""
    put_checklist(proj, "run1")
    sub = _real_subagent_payloads()[0]
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim("run1"), proj), proj)
    binding = sr.load_binding(proj)
    key = sub["session_id"] + "#" + sub["agent_id"]
    assert list(binding.keys()) == [key]  # composite key shape untouched
    entry = next(iter(binding[key].values()))
    assert set(entry) == {"spine", "engine_session", "worktree", "claimed_at", "path_source"}


# --- #440 rungs 1-2: the observed command's own text --------------------------


def _msys(path):
    r"""C:\a\b -> /c/a/b. The form git-bash really writes, DERIVED from the
    path under test -- never a hand-typed literal."""
    s = str(path).replace("\\", "/")
    if len(s) > 1 and s[1] == ":":
        s = "/" + s[0].lower() + s[2:]
    return s


def _sibling(proj, suffix):
    """A directory BESIDE the project dir -- where a git worktree actually
    lives. Never inside it."""
    d = proj.parent / (proj.name + suffix)
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_normalize_shell_path_forms():
    assert sr.normalize_shell_path("/c/Programs/foo") == "C:/Programs/foo"
    assert sr.normalize_shell_path("/d/a/b") == "D:/a/b"
    assert sr.normalize_shell_path('"C:/Program Files/x"') == "C:/Program Files/x"
    assert sr.normalize_shell_path("'/d/a b/c'") == "D:/a b/c"
    assert sr.normalize_shell_path("C:\\x\\y") == "C:\\x\\y"  # native form untouched
    assert sr.normalize_shell_path("sub/dir") == "sub/dir"    # relative untouched
    assert sr.normalize_shell_path("") is None
    assert sr.normalize_shell_path("   ") is None
    assert sr.normalize_shell_path(None) is None
    assert sr.normalize_shell_path(12345) is None


def test_last_cd_target_parses_and_refuses():
    assert sr.last_cd_target("cd /c/a && python x") == "/c/a"
    assert sr.last_cd_target("cd /c/a && cd /c/b && python x") == "/c/b"  # LAST wins
    assert sr.last_cd_target("Set-Location C:/a; python x") == "C:/a"
    assert sr.last_cd_target("pushd C:/a && python x") == "C:/a"
    assert sr.last_cd_target('cd "C:/a b/c" && python x') == '"C:/a b/c"'
    assert sr.last_cd_target("echo abcd && python x") is None   # not in command position
    assert sr.last_cd_target("python x --cd /c/a") is None      # not in command position
    assert sr.last_cd_target("python x") is None
    assert sr.last_cd_target("") is None
    assert sr.last_cd_target(None) is None


def test_post_claim_cd_into_worktree_beats_payload_cwd_msys_form(proj):
    """THE HEADLINE CASE (#440). A worktree-dispatched agent's payload `cwd` is
    the MAIN CHECKOUT -- fixed at session launch (#269) and measured identical
    across a parent and its subagents -- while its command cd's into its own
    worktree and claims a relative --file there.

    The main checkout deliberately holds a SAME-NAMED spine, so a hook that
    ignores the cd does not merely fail to resolve: it returns a plausible-
    looking WRONG answer, which is the whole defect. Asserting `!= decoy` is
    what makes this test able to FAIL rather than able to pass for the wrong
    reason."""
    worktree = _sibling(proj, "-worktree")
    decoy = put_checklist(proj, "run1")       # main checkout, same relative path
    real = put_checklist(worktree, "run1")    # the agent's ACTUAL spine
    assert decoy != real
    cmd = ('cd %s && python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-wt '
           '--claimed-by commander --worktree .' % _msys(worktree))
    out = sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    assert out == {}
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == real, "bound the main checkout's decoy, not the worktree"
    assert abs_spine != decoy
    assert entry["path_source"] == "cd_target"
    assert entry["spine"] == real


def test_post_claim_absolute_worktree_option_beats_cd_target(proj):
    """Rung 1 outranks rung 2: both roots validate, and --worktree wins."""
    wt_opt = _sibling(proj, "-optdir")
    cd_dir = _sibling(proj, "-cddir")
    opt_spine = put_checklist(wt_opt, "run1")
    put_checklist(cd_dir, "run1")
    put_checklist(proj, "run1")
    cmd = ('cd %s && python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-1 --worktree "%s"'
           % (_msys(cd_dir), wt_opt))
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == opt_spine
    assert entry["path_source"] == "worktree_opt"


def test_post_claim_relative_worktree_option_is_skipped_not_joined(proj):
    """`--worktree .` is the engine's own convention and resolves against the
    very cwd this ladder exists to stop trusting -- so rung 1 skips it and the
    ladder moves on rather than manufacturing a wrong answer with a right
    label."""
    cd_dir = _sibling(proj, "-cdonly")
    cd_spine = put_checklist(cd_dir, "run1")
    put_checklist(proj, "run1")
    cmd = ('cd %s && python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-1 --worktree .'
           % _msys(cd_dir))
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == cd_spine
    assert entry["path_source"] == "cd_target"


def test_post_claim_last_cd_target_wins_over_an_earlier_one(proj):
    first = _sibling(proj, "-first")
    second = _sibling(proj, "-second")
    put_checklist(first, "run1")
    second_spine = put_checklist(second, "run1")
    cmd = ('cd %s && cd %s && python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-1'
           % (_msys(first), _msys(second)))
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == second_spine
    assert entry["path_source"] == "cd_target"


def test_post_claim_quoted_cd_target_containing_spaces(proj):
    spaced = _sibling(proj, " space wt")
    spine = put_checklist(spaced, "run1")
    cmd = ('cd "%s" && python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-1' % spaced)
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == spine
    assert entry["path_source"] == "cd_target"


def test_post_claim_powershell_semicolon_chain_set_location(proj):
    """PowerShell 5.1 has no `&&`, so a real PowerShell command chains with `;`
    and moves with Set-Location."""
    wt = _sibling(proj, "-psh")
    spine = put_checklist(wt, "run1")
    cmd = ('Set-Location "%s"; python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-1' % wt)
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == spine
    assert entry["path_source"] == "cd_target"


def test_post_claim_pushd_target(proj):
    wt = _sibling(proj, "-pushd")
    spine = put_checklist(wt, "run1")
    cmd = ('pushd %s && python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-1' % _msys(wt))
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == spine
    assert entry["path_source"] == "cd_target"


def test_post_claim_relative_cd_target_resolves_against_payload_cwd(proj):
    sub = proj / "sub"
    spine = put_checklist(sub, "run1")
    cmd = ('cd sub && python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-1')
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == spine
    assert entry["path_source"] == "cd_target"


def test_post_claim_cd_target_that_does_not_validate_falls_through(proj):
    """A cd target is a candidate, never an override: when nothing validates
    under it the ladder moves on rather than guessing."""
    spine = put_checklist(proj, "run1")
    cmd = ('cd /c/no/such/place && python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-1')
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == spine
    assert entry["path_source"] == "payload_cwd"


# --- #440 rung 4: a REAL git worktree, discovered, not injected ---------------


def _git(args, cwd):
    proc = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True,
                          text=True, timeout=120)
    assert proc.returncode == 0, "git %s failed: %s%s" % (args, proc.stdout, proc.stderr)
    return proc


def _make_repo_with_worktree(tmp_path):
    """A REAL git repo with a REAL second worktree beside it, on disk. Returns
    `(main_tree, worktree)`. No fixture, no stub -- `git worktree list` has to
    have something true to report."""
    main_tree = tmp_path / "main"
    main_tree.mkdir()
    _git(["init"], main_tree)
    _git(["config", "user.email", "t@example.invalid"], main_tree)
    _git(["config", "user.name", "t"], main_tree)
    (main_tree / "README.md").write_text("seed\n", encoding="utf-8")
    _git(["add", "-A"], main_tree)
    _git(["commit", "-m", "seed"], main_tree)
    wt = tmp_path / "wt-epic418"
    _git(["worktree", "add", str(wt), "-b", "feature"], main_tree)
    assert wt.is_dir()
    return main_tree, wt


def test_git_worktree_roots_lists_a_real_worktree_and_excludes_the_main_tree(tmp_path):
    main_tree, wt = _make_repo_with_worktree(tmp_path)
    roots = sr.git_worktree_roots(main_tree)
    print("git_worktree_roots(%s) -> %r" % (main_tree, roots))
    assert len(roots) == 1, roots
    assert sr._same_path(roots[0], str(wt))
    # the main tree is filtered out: rung 5 owns that answer, so a
    # `git_worktree` path_source unambiguously means ANOTHER tree.
    assert not any(sr._same_path(r, str(main_tree)) for r in roots)


def test_binding_worktree_comes_from_resolved_spine_in_real_linked_worktree(tmp_path):
    """A stale launch cwd cannot attribute a child to the main checkout.

    The claim and SessionStart writers both receive the deliberately wrong main
    cwd. Their only trustworthy ownership source is the resolved absolute spine
    path. The parent and child share a harness session but have distinct agent
    identities, as real dispatched children do.
    """
    main_tree, child_tree = _make_repo_with_worktree(tmp_path)
    parent_spine = write_spine(
        main_tree, make_spine([("parent", "in-progress")]), work="parent-run"
    )
    child_spine = write_spine(
        child_tree, make_spine([("child", "in-progress")]), work="child-run"
    )
    shared_sid = "shared-harness-session"

    parent_claim = (
        'python scripts/checklist_engine.py --file "%s" claim '
        '--session-id parent-engine' % parent_spine
    )
    child_claim = (
        'python scripts/checklist_engine.py --file .agent-work/child-run/spine.json '
        'claim --session-id child-engine'
    )
    sr.handle_post_tool_use(
        {
            "session_id": shared_sid,
            "agent_id": "parent-agent",
            "cwd": str(main_tree),
            "tool_input": {"command": parent_claim},
        },
        main_tree,
    )
    # The only way the child claim can find its spine is the real `git worktree
    # list` rung. The child path is absent from the command and hook payload.
    assert str(child_tree) not in child_claim
    assert "cd " not in child_claim and "--worktree" not in child_claim
    sr.handle_post_tool_use(
        {
            "session_id": shared_sid,
            "agent_id": "child-agent",
            "cwd": str(main_tree),  # deliberately stale launch checkout
            "tool_input": {"command": child_claim},
        },
        main_tree,
    )

    child_entry = sr.load_binding(main_tree)[shared_sid + "#child-agent"][child_spine]
    assert child_entry["worktree"] == str(child_tree)
    assert sr.decide_stop({"session_id": shared_sid, "cwd": str(main_tree)}, main_tree)["decision"] == "block"

    parent_release = (
        'python scripts/checklist_engine.py --file "%s" release '
        '--session-id parent-engine' % parent_spine
    )
    sr.handle_post_tool_use(
        {
            "session_id": shared_sid,
            "agent_id": "parent-agent",
            "cwd": str(main_tree),
            "tool_input": {"command": parent_release},
        },
        main_tree,
    )
    # The parent's own run is closed, but the CHILD's is still open -- and the
    # parent is still refused (#419), now that a differing tree no longer excuses
    # it (#609 lane F g3). It is told whose gate it is and NOT what that gate's
    # next step is (#549).
    after_release = sr.decide_stop({"session_id": shared_sid, "cwd": str(main_tree)}, main_tree)
    assert after_release["decision"] == "block"
    assert shared_sid + "#child-agent" in after_release["reason"]
    assert "do child" not in after_release["reason"]  # the child's imperative, withheld
    assert "do child" not in after_release["hookSpecificOutput"]["additionalContext"]

    # A child SessionStart is also handed the stale main cwd; its unambiguous
    # scan still records the child worktree from the discovered absolute spine.
    session_start = sr.decide_session_start(
        {"session_id": shared_sid, "cwd": str(main_tree), "source": "resume"}, child_tree
    )
    assert session_start["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    resumed_entry = sr.load_binding(child_tree)[shared_sid][child_spine]
    assert resumed_entry["worktree"] == str(child_tree)


def test_git_worktree_roots_never_raises_and_is_bounded(tmp_path, monkeypatch):
    # not a git repo at all -> empty, no raise
    assert sr.git_worktree_roots(tmp_path) == []
    # absent / locked / slow git -> empty, no raise, no hang
    def _timeout(*a, **kw):
        raise subprocess.TimeoutExpired(cmd="git", timeout=sr.GIT_PROBE_TIMEOUT_SECONDS)
    monkeypatch.setattr(sr.subprocess, "run", _timeout)
    assert sr.git_worktree_roots(tmp_path) == []
    monkeypatch.setattr(sr.subprocess, "run", lambda *a, **kw: (_ for _ in ()).throw(OSError("no git")))
    assert sr.git_worktree_roots(tmp_path) == []
    assert 0 < sr.GIT_PROBE_TIMEOUT_SECONDS <= 5  # a PostToolUse hook cannot wait long


def test_git_probe_does_not_run_when_an_earlier_rung_answers(proj, monkeypatch):
    """The probe is off the turn's hot path: handle_post_tool_use returns before
    the ladder is even built unless the observed command is an engine
    claim/release, so `git` is never spawned for an ordinary tool call.

    Within a claim, a TOLD-TRUTH rung still short-circuits and never probes (the
    absolute-`--file` half below, and the `_under_ambiguity` tests further down).
    A GUESSED rung is different since g1b (#440): rung 3 answering is not the end
    of the scan, because rungs 4-5 have to be consulted before that guess can be
    trusted -- so the probe runs there, exactly ONCE."""
    calls = []
    monkeypatch.setattr(sr, "git_worktree_roots",
                        lambda pd: calls.append(str(pd)) or [])
    spine = put_checklist(proj, "run1")
    sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(proj)), proj)
    assert _only_entry(proj)[0] == spine
    assert calls == [str(proj)], "the guessed-rung scan must probe exactly once"

    # ... and an absolute --file (rung 0) short-circuits before the ladder runs
    abspath = str(proj / ".agent-work" / "run1" / "spine.json")
    sr.handle_post_tool_use(
        _bash('python e/checklist_engine.py --file "%s" claim --session-id e2' % abspath,
              session_id="s2", cwd=str(proj)), proj)
    assert calls == [str(proj)]  # unchanged -- rung 0 added no probe of its own


def test_post_claim_rung4_real_git_worktree_resolved_in_a_fresh_subprocess(tmp_path):
    """THE RUNG-4 PROOF. A real `git worktree add` tree on disk, and the hook
    run as a FRESH SUBPROCESS -- not an in-process call against a monkeypatched
    helper.

    The worktree path is set into NO env var, NO payload field and NO fixture
    field the hook reads back; the command carries NO `cd` and NO `--worktree`.
    Both are ASSERTED below, because a test that hands the hook the very root it
    claims the hook derives is a test that cannot fail (#432, #446).

    The only way to the answer is `git worktree list --porcelain` run against
    the main tree.
    """
    main_tree, wt = _make_repo_with_worktree(tmp_path)

    # The agent's REAL spine exists ONLY in the worktree.
    spine = put_checklist(wt, "run-wt")
    assert not (main_tree / ".agent-work" / "run-wt" / "spine.json").exists()

    payload = {
        "session_id": "wt-sid",
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "cwd": str(main_tree),  # session launch dir = the MAIN tree (#269)
        "tool_input": {"command": (
            "python scripts/checklist_engine.py --file .agent-work/run-wt/spine.json "
            "claim --session-id eng-wt --claimed-by commander"
        )},
    }
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(main_tree)

    # No hand-injection, asserted rather than asserted-in-prose.
    assert str(wt) not in json.dumps(payload)
    assert "cd " not in payload["tool_input"]["command"]
    assert "--worktree" not in payload["tool_input"]["command"]
    leaks = [k for k, v in env.items() if isinstance(v, str) and str(wt) in v]
    assert leaks == [], "worktree path leaked into env: %r" % leaks

    proc = subprocess.run(
        [sys.executable, str(_MODULE_PATH), "PostToolUse"],
        input=json.dumps(payload), capture_output=True, text=True,
        cwd=str(main_tree), env=env, timeout=180,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""  # PostToolUse never blocks

    store_path = main_tree / ".agent-work" / ".spine-rail-binding.json"
    store = json.loads(store_path.read_text(encoding="utf-8"))
    print("\n--- .spine-rail-binding.json written by the FRESH SUBPROCESS ---")
    print(json.dumps(store, indent=2))
    entries = store["wt-sid"]
    assert len(entries) == 1
    abs_spine, entry = next(iter(entries.items()))
    assert sr._same_path(abs_spine, spine), (
        "bound %r, not the worktree spine %r" % (abs_spine, spine))
    assert entry["path_source"] == "git_worktree"
    assert entry["engine_session"] == "eng-wt"


# --- #440 g1b: the guessed rungs refuse to guess when they disagree -----------
#
# Rungs 0-2 are TOLD TRUTH (the caller stated where it is); rungs 3-5 are
# GUESSES the hook makes for it. Two guesses naming DIFFERENT files is the one
# case where the ladder previously returned a confident wrong path.


def _two_tree_ambiguity(tmp_path, work="run1"):
    """A main checkout and a REAL `git worktree` tree beside it, BOTH holding a
    valid checklist at the same relative path -- the g1b residual's setup.

    Returns `(main_tree, worktree, main_spine, worktree_spine)`. `.agent-work/`
    is tracked in this repo, so committed checklists really do sit at identical
    relative paths in every tree; this is the shape that produces, not a
    contrivance.
    """
    main_tree, wt = _make_repo_with_worktree(tmp_path)
    here = put_checklist(main_tree, work)
    there = put_checklist(wt, work)
    assert here != there
    return main_tree, wt, here, there


def test_post_claim_ambiguous_guessed_rungs_bind_nothing_store_byte_unchanged(tmp_path):
    """THE g1b RESIDUAL. Rung 3 (payload cwd -> the main checkout) and rung 4 (a
    real git worktree) both validate, and they name DIFFERENT files, with NO
    told-truth signal in the command to break the tie.

    Pre-g1b rung 3 simply won and the store recorded the MAIN CHECKOUT's copy --
    a confident wrong path, which is the exact failure class #440 exists to end.
    Skip on uncertainty instead: a missing binding is recoverable, a wrong one
    silently misattributes one agent's context reading to another agent's work
    area."""
    main_tree, wt, here, there = _two_tree_ambiguity(tmp_path)

    store = sr.binding_path(main_tree)
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps({"other-sid": {}}), encoding="utf-8")
    before = store.read_bytes()

    cmd = _claim("run1")
    # asserted, not asserted-in-prose: nothing in the command is told truth
    assert "cd " not in cmd and "--worktree" not in cmd

    out = sr.handle_post_tool_use(_bash(cmd, cwd=str(main_tree)), main_tree)

    assert out == {}                              # PostToolUse never blocks
    assert store.read_bytes() == before           # not one byte written
    assert "s1" not in sr.load_binding(main_tree)
    assert Path(here).exists() and Path(there).exists()  # nothing on disk touched


def test_post_claim_cd_target_still_wins_outright_under_ambiguity(tmp_path):
    """Rung 2 is TOLD TRUTH and must short-circuit before the ambiguity check
    sees rungs 3-5 at all. This is the case the residual was masked by: a
    dispatched agent's shell cwd resets between calls, so its `cd` is always
    in-command -- and the guard must not cost it the binding it gets today."""
    main_tree, wt, here, there = _two_tree_ambiguity(tmp_path)
    cmd = ('cd %s && python scripts/checklist_engine.py --file '
           '.agent-work/run1/spine.json claim --session-id eng-wt' % _msys(wt))
    sr.handle_post_tool_use(_bash(cmd, cwd=str(main_tree)), main_tree)
    abs_spine, entry = _only_entry(main_tree)
    assert abs_spine == there
    assert abs_spine != here
    assert entry["path_source"] == "cd_target"


def test_post_claim_absolute_worktree_opt_still_wins_outright_under_ambiguity(tmp_path):
    """Rung 1 is TOLD TRUTH: an absolute --worktree names the tree outright, so
    the guessed rungs never get a vote."""
    main_tree, wt, here, there = _two_tree_ambiguity(tmp_path)
    cmd = ('python scripts/checklist_engine.py --file .agent-work/run1/spine.json '
           'claim --session-id eng-wt --worktree "%s"' % wt)
    sr.handle_post_tool_use(_bash(cmd, cwd=str(main_tree)), main_tree)
    abs_spine, entry = _only_entry(main_tree)
    assert abs_spine == there
    assert abs_spine != here
    assert entry["path_source"] == "worktree_opt"


def test_post_claim_absolute_file_wins_and_never_probes_git_under_ambiguity(tmp_path, monkeypatch):
    """Rung 0 must never start probing git. An absolute --file returns before the
    candidate ladder is built at all, so the ambiguity scan -- and its one
    subprocess -- is not on that path even when two trees really do disagree."""
    main_tree, wt, here, there = _two_tree_ambiguity(tmp_path)
    calls = []
    monkeypatch.setattr(sr, "git_worktree_roots",
                        lambda pd: calls.append(str(pd)) or [])
    cmd = ('python e/checklist_engine.py --file "%s" claim --session-id eng-abs'
           % there)
    sr.handle_post_tool_use(_bash(cmd, cwd=str(main_tree)), main_tree)
    abs_spine, entry = _only_entry(main_tree)
    assert abs_spine == there
    assert entry["path_source"] == "absolute"
    assert calls == [], "rung 0 probed git"


def test_post_claim_guessed_rungs_naming_the_same_file_is_agreement_not_ambiguity(proj, monkeypatch):
    """Agreement is not ambiguity. Here the payload cwd (rung 3), a rung-4 root
    and the project dir (rung 5) all resolve to the SAME file -- the ordinary
    top-level case, where cwd IS the project dir -- so the guard must still bind,
    and must keep the EARLIEST rung's path_source rather than the last one to
    agree."""
    spine = put_checklist(proj, "run1")
    seen = []
    monkeypatch.setattr(sr, "git_worktree_roots",
                        lambda pd: seen.append(str(pd)) or [str(pd)])
    sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == spine
    assert entry["path_source"] == "payload_cwd"  # earliest rung, not project_dir
    assert seen == [str(proj)], "the ambiguity scan never consulted rung 4"


def test_post_claim_two_worktree_roots_disagreeing_bind_nothing(proj, monkeypatch):
    """Ambiguity needs no second RUNG: two roots from rung 4 alone are enough.
    The payload cwd and the project dir hold nothing here, so the two worktrees
    compete directly."""
    elsewhere = proj.parent / "nowhere"
    elsewhere.mkdir(exist_ok=True)
    wt_a = _sibling(proj, "-wtA")
    wt_b = _sibling(proj, "-wtB")
    put_checklist(wt_a, "run1")
    put_checklist(wt_b, "run1")
    monkeypatch.setattr(sr, "git_worktree_roots", lambda pd: [str(wt_a), str(wt_b)])
    out = sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(elsewhere)), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_claim_one_worktree_root_still_binds_under_the_guard(proj, monkeypatch):
    """The guard refuses only a DISAGREEMENT. A single validating candidate is
    not ambiguous, so rung 4's answer survives the check unchanged -- the
    behaviour the real-`git worktree` subprocess proof above depends on."""
    elsewhere = proj.parent / "nowhere-solo"
    elsewhere.mkdir(exist_ok=True)
    wt_a = _sibling(proj, "-wtSolo")
    spine = put_checklist(wt_a, "run1")
    monkeypatch.setattr(sr, "git_worktree_roots", lambda pd: [str(wt_a)])
    sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(elsewhere)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == spine
    assert entry["path_source"] == "git_worktree"


# --- #440: release resolves against its OWN recorded binding first ------------


def _release(work="run1", engine_session="eng-9"):
    return ('python scripts/checklist_engine.py --file .agent-work/%s/spine.json '
            'release --session-id %s' % (work, engine_session))


def test_post_release_removes_its_own_entry_after_the_spine_file_is_deleted(proj):
    """`release` is not `claim`. By release time the spine may already be
    archived, moved or deleted, so NO filesystem candidate validates -- and a
    ladder-only release would leak the entry forever, with no reaper to collect
    it. A release must remove what its own claim put there."""
    spine = put_checklist(proj, "run1")
    sr.handle_post_tool_use(_bash(_claim("run1"), cwd=str(proj)), proj)
    assert _only_entry(proj)[0] == spine

    os.remove(spine)  # the run closed and the work area was archived
    assert not Path(spine).exists()

    out = sr.handle_post_tool_use(_bash(_release("run1"), cwd=str(proj)), proj)
    assert out == {}
    assert "s1" not in sr.load_binding(proj)


def test_post_release_recorded_lookup_beats_a_validating_decoy(proj):
    """The recorded binding is consulted FIRST, so a same-named spine sitting in
    the main checkout cannot redirect a release away from the entry its own
    claim wrote."""
    worktree = _sibling(proj, "-relwt")
    real = put_checklist(worktree, "run1")
    decoy = put_checklist(proj, "run1")
    claim = ('cd %s && python scripts/checklist_engine.py --file '
             '.agent-work/run1/spine.json claim --session-id eng-1' % _msys(worktree))
    sr.handle_post_tool_use(_bash(claim, cwd=str(proj)), proj)
    assert _only_entry(proj)[0] == real

    # the release command carries NO cd -- only the recorded binding knows
    sr.handle_post_tool_use(_bash(_release("run1", "eng-1"), cwd=str(proj)), proj)
    assert "s1" not in sr.load_binding(proj), "released the decoy, not its own entry"
    assert Path(decoy).exists()  # nothing on disk was touched


def test_post_release_ambiguous_recorded_suffix_falls_through_to_the_ladder(proj):
    """Two recorded entries end with the SAME relative suffix, so the recorded
    lookup is ambiguous and must not guess -- the filesystem ladder decides."""
    worktree = _sibling(proj, "-ambwt")
    here = put_checklist(proj, "run1")
    there = put_checklist(worktree, "run1")
    sr.handle_post_tool_use(_bash(_claim("run1", "eng-here"), cwd=str(proj)), proj)
    cd_claim = ('cd %s && python scripts/checklist_engine.py --file '
                '.agent-work/run1/spine.json claim --session-id eng-there'
                % _msys(worktree))
    sr.handle_post_tool_use(_bash(cd_claim, cwd=str(proj)), proj)
    assert set(sr.load_binding(proj)["s1"]) == {here, there}

    # ambiguous -> ladder -> rung 3 (payload cwd) -> the `here` entry
    sr.handle_post_tool_use(_bash(_release("run1", "eng-here"), cwd=str(proj)), proj)
    assert set(sr.load_binding(proj)["s1"]) == {there}


def test_post_release_recorded_lookup_ignores_a_different_relative_suffix(proj):
    """The suffix match is a real match, not a substring coincidence: releasing
    `run1` must not remove the `run11` entry."""
    put_checklist(proj, "run1")
    put_checklist(proj, "run11")
    sr.handle_post_tool_use(_bash(_claim("run11", "eng-11"), cwd=str(proj)), proj)
    only = _only_entry(proj)[0]
    sr.handle_post_tool_use(_bash(_release("run1", "eng-1"), cwd=str(proj)), proj)
    assert _only_entry(proj)[0] == only


def test_post_release_that_resolves_nothing_still_clears_the_nudge_ledger(proj):
    """The three-strike escape hatch is keyed by the bare session_id and is
    independent of whether any binding entry matched -- an unresolvable release
    must not strand a strike count."""
    sr.save_nudges(proj, {"s1": {"count": 2, "journal_seq": 4, "active_id": ["g1"]}})
    out = sr.handle_post_tool_use(_bash(_release("never-claimed"), cwd=str(proj)), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}
    assert "s1" not in sr.load_nudges(proj)


def test_post_tool_use_never_raises_on_junk(proj):
    """Fuzz over the shapes a real payload can degrade into. PostToolUse returns
    {} on every path and never raises -- including every new #440 failure mode."""
    rows = [
        {},
        {"session_id": "s1"},
        {"session_id": "s1", "tool_input": None},
        {"session_id": "s1", "tool_input": {"command": None}},
        {"session_id": "s1", "tool_input": {"command": ""}},
        {"session_id": "s1", "tool_input": {"command": "checklist_engine.py"}},
        {"session_id": "s1", "tool_input": {"command": "checklist_engine.py claim"}},
        {"session_id": "s1", "tool_input": {"command": "checklist_engine.py --file"}},
        {"session_id": "s1", "tool_input": {"command": 'checklist_engine.py --file " claim'}},
        {"session_id": "s1", "tool_input": {"command": "cd && checklist_engine.py --file x claim"}},
        {"session_id": "s1", "tool_input": {"command": "cd \x00 && checklist_engine.py --file x claim"}},
        {"session_id": "s1", "cwd": 12345,
         "tool_input": {"command": "checklist_engine.py --file x claim"}},
        {"session_id": "s1", "cwd": None,
         "tool_input": {"command": "checklist_engine.py --file .a/b.json release"}},
        {"session_id": "s1", "tool_input": {"command": "checklist_engine.py --file=" + "x" * 500 + " claim"}},
        {"session_id": "s1", "tool_input": {"command": "cd /z/nope && checklist_engine.py --file a/b.json claim"}},
        {"session_id": "s1", "tool_input": {"command": "Set-Location '' ; checklist_engine.py --file a/b.json claim"}},
    ]
    for row in rows:
        assert sr.handle_post_tool_use(row, proj) == {}, row
    print("fuzz rows returning {} without raising: %d" % len(rows))
    assert len(rows) >= 12


# --- door path: mcp__spine__spine_lease claim/release (#door-binding) -------
#
# The MCP door carries no --file: it reads SPINE_FILE/SPINE_SESSION from its
# OWN environment (scripts/mcp_spine_server.py: SPINE = Path(os.environ
# ["SPINE_FILE"]).resolve()), and this hook process shares that environment.
# So the door path resolves the claimed spine from THIS process's own
# SPINE_FILE, never from tool_input or a candidate-root ladder.

DOOR_TOOL = "mcp__spine__spine_lease"


def _door(action, session_id="s1", cwd=None, tool_input="__default__"):
    data = {"session_id": session_id, "tool_name": DOOR_TOOL}
    data["tool_input"] = {"action": action} if tool_input == "__default__" else tool_input
    if cwd:
        data["cwd"] = cwd
    return data


def test_stop_door_claimed_mid_flight_blocks(proj, monkeypatch):
    """RED/GREEN: a door-issued claim (mcp__spine__spine_lease, action=claim)
    must record a binding just like the Bash checklist_engine.py claim path,
    so a mid-flight spine claimed through the door is refused at Stop -- same
    assertion shape as test_stop_mid_flight_blocks_with_substrings."""
    spine = make_spine([("g1", "in-progress")], imperatives={"g1": "finish the door work"})
    sp = write_spine(proj, spine, journal_lines=2)
    monkeypatch.setenv("SPINE_FILE", sp)
    monkeypatch.setenv("SPINE_SESSION", "eng-9")
    out = sr.handle_post_tool_use(_door("claim", cwd=str(proj)), proj)
    assert out == {}
    result = sr.decide_stop({"session_id": "s1"}, proj)
    assert result.get("decision") == "block"
    reason = result.get("reason", "")
    assert "SPINE MID-FLIGHT" in reason
    assert "g1" in reason


def test_post_door_claim_writes_binding(proj, monkeypatch):
    """GREEN: the door claim writes a binding entry equivalent in shape to the
    Bash-path entry (spine, engine_session, worktree, claimed_at, path_source)."""
    abs_spine = put_checklist(proj, "run1")
    monkeypatch.setenv("SPINE_FILE", abs_spine)
    monkeypatch.setenv("SPINE_SESSION", "eng-42")
    out = sr.handle_post_tool_use(_door("claim", cwd=str(proj)), proj)
    assert out == {}
    got_path, entry = _only_entry(proj)
    assert got_path == abs_spine
    assert entry["spine"] == abs_spine
    assert entry["engine_session"] == "eng-42"
    assert entry["worktree"] == str(proj)
    assert entry["claimed_at"]
    assert entry["path_source"] == sr.PATH_SOURCE_DOOR_ENV


def test_post_door_claim_records_absent_spine_session_as_is(proj, monkeypatch):
    """SPINE_SESSION may be empty/absent -- record whatever is actually
    present, never fabricate a value."""
    abs_spine = put_checklist(proj, "run1")
    monkeypatch.setenv("SPINE_FILE", abs_spine)
    monkeypatch.delenv("SPINE_SESSION", raising=False)
    sr.handle_post_tool_use(_door("claim", cwd=str(proj)), proj)
    _, entry = _only_entry(proj)
    assert entry["engine_session"] is None


def test_post_door_release_removes_binding_and_nudge(proj, monkeypatch):
    """GREEN: a door release removes the exact abs_spine entry it claimed,
    mirroring test_post_release_deletes_binding_and_nudge."""
    abs_spine = put_checklist(proj, "run1")
    monkeypatch.setenv("SPINE_FILE", abs_spine)
    monkeypatch.setenv("SPINE_SESSION", "eng-9")
    sr.save_nudges(proj, {"s1": {"count": 2, "journal_seq": 1, "active_id": "g1"}})
    sr.handle_post_tool_use(_door("claim", cwd=str(proj)), proj)
    out = sr.handle_post_tool_use(_door("release", cwd=str(proj)), proj)
    assert out == {}
    assert "s1" not in sr.load_binding(proj)
    assert "s1" not in sr.load_nudges(proj)


# --- CONTROL: legitimate door-claimed turn-ends must NOT be refused ---------

def test_stop_door_claimed_terminal_released_lease_allows(proj, monkeypatch):
    spine = make_spine([("g1", "complete")], lease_status="released")
    sp = write_spine(proj, spine)
    monkeypatch.setenv("SPINE_FILE", sp)
    monkeypatch.setenv("SPINE_SESSION", "eng-9")
    sr.handle_post_tool_use(_door("claim", cwd=str(proj)), proj)
    assert _only_entry(proj)[0] == sp
    assert sr.decide_stop({"session_id": "s1"}, proj) == {}


def test_stop_door_claimed_own_spine_in_another_worktree_now_blocks(proj, monkeypatch):
    # The door twin of test_stop_own_claim_from_another_worktree_now_blocks, and
    # flipped for the same reason (#609 lane F g3): the door claim carries no
    # agent_id either, so this is the same agent's own binding and its Stop is
    # refused wherever it stands.
    sub = proj / "subwt"
    subspine = write_spine(sub, make_spine([("g1", "in-progress")],
                                           imperatives={"g1": "DOOR-CLAIM-MARKER keep going"}),
                           journal_lines=1)
    monkeypatch.setenv("SPINE_FILE", subspine)
    monkeypatch.setenv("SPINE_SESSION", "eng-9")
    sr.handle_post_tool_use(_door("claim", session_id="shared", cwd=str(sub)), proj)
    sid_bindings = sr.load_binding(proj)["shared"]
    assert len(sid_bindings) == 1
    entry = next(iter(sid_bindings.values()))
    assert entry["worktree"] == str(sub)
    out = sr.decide_stop({"session_id": "shared", "cwd": str(proj)}, proj)
    assert out["decision"] == "block"
    assert "DOOR-CLAIM-MARKER" in out["reason"]


def test_stop_door_claimed_unreadable_spine_allows(proj, monkeypatch):
    spine = make_spine([("g1", "in-progress")])
    sp = write_spine(proj, spine, journal_lines=1)
    monkeypatch.setenv("SPINE_FILE", sp)
    monkeypatch.setenv("SPINE_SESSION", "eng-9")
    sr.handle_post_tool_use(_door("claim", cwd=str(proj)), proj)
    assert _only_entry(proj)[0] == sp  # bound while readable
    os.remove(sp)  # then the spine vanishes
    assert sr.decide_stop({"session_id": "s1"}, proj) == {}


def test_stop_door_claimed_blocked_status_honest_stop_allows(proj, monkeypatch):
    spine = make_spine([("g1", "blocked")])
    sp = write_spine(proj, spine)
    monkeypatch.setenv("SPINE_FILE", sp)
    monkeypatch.setenv("SPINE_SESSION", "eng-9")
    sr.handle_post_tool_use(_door("claim", cwd=str(proj)), proj)
    assert _only_entry(proj)[0] == sp
    assert sr.decide_stop({"session_id": "s1"}, proj) == {}


# --- fail-open: a malformed door payload records nothing and never raises ---

def test_post_door_claim_missing_tool_input_records_nothing(proj, monkeypatch):
    abs_spine = put_checklist(proj, "run1")
    monkeypatch.setenv("SPINE_FILE", abs_spine)
    data = {"session_id": "s1", "tool_name": DOOR_TOOL}
    out = sr.handle_post_tool_use(data, proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_door_claim_non_dict_tool_input_records_nothing(proj, monkeypatch):
    abs_spine = put_checklist(proj, "run1")
    monkeypatch.setenv("SPINE_FILE", abs_spine)
    out = sr.handle_post_tool_use(_door("claim", tool_input="not-a-dict"), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_door_claim_missing_action_records_nothing(proj, monkeypatch):
    abs_spine = put_checklist(proj, "run1")
    monkeypatch.setenv("SPINE_FILE", abs_spine)
    out = sr.handle_post_tool_use(_door("claim", tool_input={}), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_door_claim_unrecognized_action_records_nothing(proj, monkeypatch):
    abs_spine = put_checklist(proj, "run1")
    monkeypatch.setenv("SPINE_FILE", abs_spine)
    out = sr.handle_post_tool_use(_door("heartbeat"), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_door_claim_missing_spine_file_records_nothing(proj, monkeypatch):
    monkeypatch.delenv("SPINE_FILE", raising=False)
    out = sr.handle_post_tool_use(_door("claim"), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_door_claim_non_checklist_spine_file_records_nothing(proj, monkeypatch):
    junk = proj / ".agent-work" / "run1" / "gauge.json"
    junk.parent.mkdir(parents=True, exist_ok=True)
    junk.write_text(json.dumps({"not": "a checklist"}), encoding="utf-8")
    monkeypatch.setenv("SPINE_FILE", str(junk))
    out = sr.handle_post_tool_use(_door("claim"), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_door_claim_spine_file_outside_agent_work_records_nothing(proj, monkeypatch):
    outside = proj / "elsewhere.json"
    outside.write_text(_checklist_json(), encoding="utf-8")
    monkeypatch.setenv("SPINE_FILE", str(outside))
    out = sr.handle_post_tool_use(_door("claim"), proj)
    assert out == {}
    assert sr.load_binding(proj) == {}


def test_post_door_never_raises_on_junk(proj, monkeypatch):
    """Fuzz sibling to test_post_tool_use_never_raises_on_junk for the door
    shape specifically."""
    abs_spine = put_checklist(proj, "run1")
    rows = [
        {"session_id": "s1", "tool_name": DOOR_TOOL},
        {"session_id": "s1", "tool_name": DOOR_TOOL, "tool_input": None},
        {"session_id": "s1", "tool_name": DOOR_TOOL, "tool_input": []},
        {"session_id": "s1", "tool_name": DOOR_TOOL, "tool_input": {"action": None}},
        {"session_id": "s1", "tool_name": DOOR_TOOL, "tool_input": {"action": "claim"}},
        {"tool_name": DOOR_TOOL, "tool_input": {"action": "claim"}},
        {"session_id": None, "tool_name": DOOR_TOOL, "tool_input": {"action": "claim"}},
    ]
    assert len(rows) >= 7
    for row in rows:
        monkeypatch.delenv("SPINE_FILE", raising=False)
        assert sr.handle_post_tool_use(row, proj) == {}, row
    monkeypatch.setenv("SPINE_FILE", abs_spine)
    for row in rows:
        assert sr.handle_post_tool_use(row, proj) == {}, row
