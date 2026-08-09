"""Unit tests for scripts/hooks/spine_rail.py.

Every decision branch is exercised through the pure/handler functions with
constructed spine fixtures. No subprocess of the engine; state-file facts only
-- with ONE deliberate exception (lesson:verify-harness-field-and-drive-real-
writer, #261): test_session_start_real_engine_claim_produces_real_binding_
diff below DOES subprocess the real scripts/checklist_engine.py to produce a
genuinely engine-claimed spine, specifically so the bind-on-resume write path
is proven against production machinery, not a hand-built fixture.
"""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]

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
    sr.handle_post_tool_use(_real_post_tool_use(parent, _claim_cmd("run-parent", "eng-p"), proj), proj)
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("run-sub", "eng-s"), proj), proj)

    binding = sr.load_binding(proj)
    assert len(binding) == 2
    assert list(binding[sid].keys()) == [_abs_spine(proj, "run-parent")]

    out = sr.decide_stop({"session_id": sid, "cwd": str(proj)}, proj)
    assert out["decision"] == "block"
    assert "g9" in out["reason"]
    assert "COMPOSITE-MARKER" in out["reason"]
    # Strikes still accrue under the BARE sid -- the hatch is not fragmented.
    assert list(sr.load_nudges(proj).keys()) == [sid]


def test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key(proj):
    """decide_session_start's read goes through session_view too. The spine
    lives outside proj/.agent-work so the fallback scan cannot find it -- the
    only route to it is the composite key."""
    sub = _real_subagent_payloads()[0]
    sid = sub["session_id"]
    alt = proj / "altwt"
    write_spine(alt, make_spine([("g4", "in-progress")], imperatives={"g4": "COMPOSITE-RESUME keep going"}),
                work="run-sub")
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("run-sub", "eng-s"), alt), proj)

    binding = sr.load_binding(proj)
    assert list(binding.keys()) == [sid + sr.BINDING_KEY_SEP + sub["agent_id"]]
    assert sr._scan_active_spine(proj) == []  # nothing for the fallback to find

    out = sr.decide_session_start({"session_id": sid, "cwd": str(alt), "source": "resume"}, proj)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "RESUMING" in ctx
    assert "COMPOSITE-RESUME" in ctx


def test_session_start_bind_on_resume_still_writes_under_the_bare_key(proj):
    """SessionStart never carries an agent_id, so a resumed session is by
    definition top-level: the bind-on-unambiguous-scan write must land under
    the BARE session_id, never under a composite one. The sid's pre-existing
    composite entry is FOREIGN so the existing-binding read is skipped and the
    scan path is actually reached."""
    sub = _real_subagent_payloads()[0]
    sid = sub["session_id"]
    composite = sid + sr.BINDING_KEY_SEP + sub["agent_id"]
    alt = proj / "altwt"
    write_spine(alt, make_spine([("gx", "in-progress")]), work="run-sub")
    sr.handle_post_tool_use(_real_post_tool_use(sub, _claim_cmd("run-sub", "eng-s"), alt), proj)
    assert list(sr.load_binding(proj).keys()) == [composite]

    sp = write_spine(proj, make_spine([("g1", "in-progress")], session_id="eng-alone",
                                      imperatives={"g1": "ONLY-MARKER keep going"}),
                     work="run-alone")

    out = sr.decide_session_start({"session_id": sid, "cwd": str(proj), "source": "resume"}, proj)
    assert "ONLY-MARKER" in out["hookSpecificOutput"]["additionalContext"]

    binding = sr.load_binding(proj)
    assert set(binding.keys()) == {composite, sid}   # new entry under the BARE key
    assert list(binding[sid].keys()) == [sp]
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


# --- worktree attribution helpers (_same_path / _foreign_worktree) -----------

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
    # spine in ITS OWN worktree; the real PostToolUse path writes a NESTED entry
    # (keyed by abs_spine, #202) pointing at the subagent's worktree/spine. The
    # PARENT then ends its turn (Stop) from the PARENT worktree while that bound
    # spine is mid-flight. The worktree mismatch must let the parent stop
    # (parent is not this driver).
    sub = proj / "subwt"
    subspine = write_spine(sub, make_spine([("g1", "in-progress")]), journal_lines=1)
    cmd = ('py scripts/checklist_engine.py --file .agent-work/run1/spine.json '
           'claim --session-id eng-9 --claimed-by commander')
    sr.handle_post_tool_use(_bash(cmd, session_id="shared", cwd=str(sub)), proj)
    sid_bindings = sr.load_binding(proj)["shared"]
    assert len(sid_bindings) == 1
    entry = next(iter(sid_bindings.values()))
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


def test_stop_does_not_block_when_all_entries_foreign_or_non_mid_flight(proj):
    """One session_id bound to TWO spines: one is genuinely mid-flight but
    FOREIGN (a subagent's own worktree, parent stopping elsewhere), the other
    is not mid-flight at all (released lease). Neither should block -- the
    Stop is allowed."""
    sub = proj / "subwt"
    sp_foreign_mid_flight = write_spine(sub, make_spine([("g1", "in-progress")]), journal_lines=1)
    sp_released = write_spine(proj, make_spine([("g2", "complete")], lease_status="released"), work="run-done")
    bind(proj, "shared", sp_foreign_mid_flight, worktree=str(sub))
    bind(proj, "shared", sp_released)
    assert len(sr.load_binding(proj)["shared"]) == 2

    out = sr.decide_stop({"session_id": "shared", "cwd": str(proj)}, proj)
    assert out == {}
    assert "shared" not in sr.load_nudges(proj)  # no mid-flight entry -> nudges untouched


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
    abs_spine_path entry this sid already holds for a DIFFERENT (foreign-
    worktree) spine (mirrors the real claim writer's leave-siblings-
    untouched behavior, #202). The sibling is made FOREIGN on purpose: a
    non-foreign sibling would already satisfy the existing-binding read
    (g1's territory, unrelated to this scan-bind path) and the scan would
    never run at all -- foreign is the one shape that reaches this branch
    with a pre-existing sibling still in place."""
    sub = proj / "subwt"
    other_sp = write_spine(
        sub, make_spine([("gx", "in-progress")], lease_status="released"), work="other-run"
    )
    bind(proj, "resuming-sid", other_sp, worktree=str(sub))  # foreign relative to cwd=proj

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
    abspath = str(proj / ".agent-work" / "run1" / "spine.json")
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


def test_post_claim_absolute_file_is_rung_zero_and_is_not_validated(proj):
    """Rung 0: an absolute --file is ground truth, taken as-is WITHOUT a
    validity test -- deliberately, so a `release` whose spine has already been
    archived or deleted can still name its own entry."""
    abspath = str(proj / ".agent-work" / "gone" / "spine.json")
    cmd = 'python C:/x/checklist_engine.py --file "%s" claim --session-id eng-2' % abspath
    sr.handle_post_tool_use(_bash(cmd, cwd=str(proj)), proj)
    abs_spine, entry = _only_entry(proj)
    assert abs_spine == abspath
    assert entry["path_source"] == "absolute"


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
