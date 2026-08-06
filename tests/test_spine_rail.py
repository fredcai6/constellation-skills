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
