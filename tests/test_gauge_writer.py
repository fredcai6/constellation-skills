"""Unit tests for scripts/hooks/gauge_writer_hook.py.

Fixture-based against tests/fixtures/golden_transcript.jsonl (a hand-built
transcript modeled on a real Claude Code session transcript captured and
inspected live during implementation -- see docs/GAUGE_WRITER_HOOK.md for the
exact schema this depends on). No real filesystem paths outside tmp_path; no
network; no dependency on a live harness.
"""

import importlib.util
import json
import os
import threading
from pathlib import Path

import pytest

_HOOKS_DIR = Path(__file__).resolve().parents[1] / "scripts" / "hooks"
_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "golden_transcript.jsonl"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sr = _load("spine_rail", _HOOKS_DIR / "spine_rail.py")
gw = _load("gauge_writer_hook", _HOOKS_DIR / "gauge_writer_hook.py")

# Hand-computed expectation for tests/fixtures/golden_transcript.jsonl's
# latest MAIN-CHAIN (non-sidechain) assistant usage record (line 4):
# 3 + 1200 + 158000 = 159203 tokens, against claude-opus-4-8's 1_000_000
# window (the real default window — see gauge_writer_hook.MODEL_WINDOWS). Lines 5-6 are
# TWO trailing sidechain (subagent) turns -- LATER in the file AND in time,
# with BIGGER usage totals than line 4 -- that the reverse tail-scan
# encounters first and must skip past to reach this answer. That ordering
# (not the earlier draft's, where the true answer was already the last line)
# is what actually forces gauge_writer_hook.find_latest_usage's
# isSidechain-continue branch to run; see
# test_golden_fixture_picks_latest_main_chain_usage_not_sidechain below.
EXPECTED_MODEL = "claude-opus-4-8"
EXPECTED_FILL = (3 + 1200 + 158000) / 1_000_000


@pytest.fixture
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    return tmp_path


def _bind(proj, session_id, spine_path):
    """Write a NEW-shape (#202 nested) binding entry for `session_id`, keyed
    by `spine_path` -- merges onto any existing entries for this session_id
    rather than clobbering them, so two calls under the same session_id bind
    two distinct spines (needed for the fan-out tests below)."""
    binding = sr.load_binding(proj)
    sid_bindings = dict(binding.get(session_id) or {})
    sid_bindings[str(spine_path)] = {
        "spine": str(spine_path),
        "engine_session": "eng-1",
        "worktree": str(proj),
        "claimed_at": "2026-07-27T00:00:00+00:00",
    }
    binding[session_id] = sid_bindings
    sr.save_binding(proj, binding)


def _hook_data(session_id="s1", transcript_path=None):
    return {"session_id": session_id, "transcript_path": str(transcript_path) if transcript_path else None}


# --- well-formed write --------------------------------------------------------

def test_golden_fixture_produces_well_formed_record(proj):
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    out = gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert out == {}

    gauge_path = work / "gauge.json"
    assert gauge_path.exists()
    record = json.loads(gauge_path.read_text(encoding="utf-8"))
    assert set(record.keys()) == {"schema_version", "fill_fraction", "model", "observed_at"}
    assert record["schema_version"] == 1
    assert isinstance(record["fill_fraction"], float)
    assert 0.0 <= record["fill_fraction"] <= 1.0
    assert isinstance(record["model"], str)
    assert isinstance(record["observed_at"], str)


def test_golden_fixture_picks_latest_main_chain_usage_not_sidechain(proj):
    """The fixture's trailing lines 5-6 (a subagent's own context, isSidechain:
    true) are LATER in the file AND in time than the real main-chain answer
    on line 4, and carry BIGGER usage totals. Because
    _iter_tail_lines_reverse scans from the end of the file, it hits both
    sidechain lines FIRST and must skip both (find_latest_usage's
    isSidechain-continue branch) before it reaches line 4's answer -- so a
    correct result here is only possible if that skip actually ran, not an
    artifact of the true answer already being the last line."""
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)

    record = json.loads((work / "gauge.json").read_text(encoding="utf-8"))
    assert record["model"] == EXPECTED_MODEL
    assert record["fill_fraction"] == pytest.approx(EXPECTED_FILL)
    assert record["observed_at"] == "2026-07-18T12:00:00.000Z"
    # Sanity-check the premise itself: if the skip branch were a no-op (bug),
    # the sidechain turns' bigger totals would produce a fill above this
    # bound instead of matching EXPECTED_FILL above.
    sidechain_fill = (5 + 2000 + 190000) / 1_000_000
    assert record["fill_fraction"] < sidechain_fill


# --- skip-on-uncertainty: parse failure leaves prior file untouched ----------

def test_parse_failure_leaves_prior_gauge_file_untouched(proj, tmp_path):
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    gauge_path = work / "gauge.json"
    prior = {"schema_version": 1, "fill_fraction": 0.42, "model": "claude-opus-4-8", "observed_at": "2026-07-18T09:00:00.000Z"}
    gauge_path.write_text(json.dumps(prior), encoding="utf-8")

    bad_transcript = tmp_path / "corrupt.jsonl"
    bad_transcript.write_text("{ not json\nalso not json\n", encoding="utf-8")

    out = gw.handle_post_tool_use(_hook_data("s1", bad_transcript), proj)
    assert out == {}
    assert json.loads(gauge_path.read_text(encoding="utf-8")) == prior


def test_transcript_with_no_usable_usage_leaves_prior_file_untouched(proj, tmp_path):
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    gauge_path = work / "gauge.json"
    prior = {"schema_version": 1, "fill_fraction": 0.1, "model": "claude-opus-4-8", "observed_at": "2026-07-18T09:00:00.000Z"}
    gauge_path.write_text(json.dumps(prior), encoding="utf-8")

    # well-formed JSON, but no assistant/usage records at all (e.g. a brand
    # new session with only a user turn so far)
    empty_transcript = tmp_path / "no_usage.jsonl"
    empty_transcript.write_text(json.dumps({"type": "user", "message": {"role": "user", "content": []}}) + "\n", encoding="utf-8")

    gw.handle_post_tool_use(_hook_data("s1", empty_transcript), proj)
    assert json.loads(gauge_path.read_text(encoding="utf-8")) == prior


def test_missing_transcript_path_skips_no_write(proj):
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    out = gw.handle_post_tool_use({"session_id": "s1"}, proj)
    assert out == {}
    assert not (work / "gauge.json").exists()


def test_nonexistent_transcript_file_skips_no_write(proj, tmp_path):
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    out = gw.handle_post_tool_use(_hook_data("s1", tmp_path / "gone.jsonl"), proj)
    assert out == {}
    assert not (work / "gauge.json").exists()


def test_no_binding_skips_no_write(proj):
    """No session->spine binding (e.g. no engine claim has run yet this
    session) -- work_id is unresolvable, so the hook must skip entirely."""
    out = gw.handle_post_tool_use(_hook_data("unbound-session", _FIXTURE), proj)
    assert out == {}
    assert not (proj / ".agent-work").exists() or list((proj / ".agent-work").rglob("gauge.json")) == []


# --- containment: never write outside .agent-work/<work_id>/ -----------------


def test_spine_outside_agent_work_skips_no_write(proj):
    """A binding whose spine path resolved to a CHECKOUT ROOT rather than a
    work dir (observed live: an untracked gauge.json in the repo root) must
    produce NO write at all. Only `.agent-work/` is gitignored, so a gauge
    record dropped beside it is untracked debris in the user's tree.

    Drives the real handler against a real transcript with a real binding --
    the only thing wrong is the spine location -- so a regression that removes
    the containment check fails here rather than passing on a mocked path."""
    spine_path = proj / "spine.json"       # root-level: NOT under .agent-work/
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    out = gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert out == {}
    assert not (proj / "gauge.json").exists()
    # and it did not silently redirect somewhere else either
    assert list(proj.rglob("gauge.json")) == []


def test_spine_directly_in_agent_work_root_skips_no_write(proj):
    """`.agent-work/spine.json` (no <work_id> dir) is also outside the
    contract -- writing there would collide across every run that made the
    same mistake, so it skips rather than guessing a work_id."""
    work = proj / ".agent-work"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert not (work / "gauge.json").exists()


def test_worktree_local_agent_work_outside_project_dir_still_writes(proj, tmp_path):
    """Containment checks the `.agent-work/<work_id>/` SHAPE, not containment
    within project_dir. Under an active Admiral epic lease `durable_root()`
    resolves to the worktree root, so a legitimate spine can sit in a
    different checkout entirely -- that must still be written, or the governor
    goes blind for exactly the epic runs it matters most in."""
    worktree = tmp_path / "wt-epic-1"
    work = worktree / ".agent-work" / "epic-1"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)

    record = json.loads((work / "gauge.json").read_text(encoding="utf-8"))
    assert record["model"] == EXPECTED_MODEL
    assert record["fill_fraction"] == pytest.approx(EXPECTED_FILL)


# --- #261: gauge-write skips on 2+ bound spines (supersedes #202 fan-out) ---

# A REAL captured subagent transcript (isSidechain: true on every line,
# carrying the PARENT's own sessionId -- copied read-only from
# C:/Users/fredc/.claude/projects/C--Programs-constellation-skills/ce777c3b-505c-4b76-b09b-db2c11082b83/
# subagents/agent-af45cec63b2835a40.jsonl; the original is untouched). It has
# exactly one assistant/usage line, so this is adversarial: a bug that failed
# to skip isSidechain entries would find a usable reading here, not silence.
_REAL_SUBAGENT_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "real_subagent_transcript.jsonl"


def test_resolve_gauge_path_returns_list_of_every_bound_spine(proj):
    work_a = proj / ".agent-work" / "run-a"
    work_b = proj / ".agent-work" / "run-b"
    work_a.mkdir(parents=True)
    work_b.mkdir(parents=True)
    _bind(proj, "s1", work_a / "spine.json")
    _bind(proj, "s1", work_b / "spine.json")

    paths = gw.resolve_gauge_path(proj, "s1")
    assert isinstance(paths, list)
    assert set(paths) == {work_a / "gauge.json", work_b / "gauge.json"}


def test_resolve_gauge_path_empty_list_when_unbound(proj):
    assert gw.resolve_gauge_path(proj, "no-such-session") == []


def test_multiple_bindings_skips_writes_neither_spine(proj):
    """One session_id bound to TWO spines, ONE PostToolUse event with a
    realistic main-chain transcript -- (decision:gauge-write-skips-on-
    multiple-bindings, supersedes decision:gauge-write-fans-out-on-ambiguity).

    Live production evidence (epic-226 / #261) proved fan-out wrong: when two
    genuinely different top-level agents share one session_id, find_latest_usage
    cannot tell whose activity produced the latest usage record, and fanning the
    same wrong-source record out to every bound spine SPREADS the
    misattribution instead of fixing it. So 2+ candidates must now be treated
    as uncertainty -- write NOTHING to either spine, exactly like the existing
    zero-candidate (unbound) case. Before/after comparison: neither
    gauge.json existed before the call, and neither exists after -- the
    strongest form of "unchanged" for a file that was never there."""
    work_a = proj / ".agent-work" / "run-a"
    work_b = proj / ".agent-work" / "run-b"
    work_a.mkdir(parents=True)
    work_b.mkdir(parents=True)
    (work_a / "spine.json").write_text("{}", encoding="utf-8")
    (work_b / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work_a / "spine.json")
    _bind(proj, "s1", work_b / "spine.json")

    gauge_a = work_a / "gauge.json"
    gauge_b = work_b / "gauge.json"
    assert not gauge_a.exists() and not gauge_b.exists()  # before

    out = gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert out == {}

    assert not gauge_a.exists() and not gauge_b.exists()  # after: both still absent


def test_multiple_bindings_skips_and_leaves_existing_gauge_files_untouched(proj):
    """Same 2-binding ambiguity, but each spine already carries a prior
    reading -- proves 'skip' means the prior content survives byte-identical,
    not merely 'no crash'."""
    work_a = proj / ".agent-work" / "run-a"
    work_b = proj / ".agent-work" / "run-b"
    work_a.mkdir(parents=True)
    work_b.mkdir(parents=True)
    (work_a / "spine.json").write_text("{}", encoding="utf-8")
    (work_b / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work_a / "spine.json")
    _bind(proj, "s1", work_b / "spine.json")

    prior_a = json.dumps({"schema_version": 1, "fill_fraction": 0.1, "model": "claude-opus-4-8", "observed_at": "2026-07-18T09:00:00.000Z"})
    prior_b = json.dumps({"schema_version": 1, "fill_fraction": 0.2, "model": "claude-sonnet-5", "observed_at": "2026-07-18T09:05:00.000Z"})
    (work_a / "gauge.json").write_text(prior_a, encoding="utf-8")
    (work_b / "gauge.json").write_text(prior_b, encoding="utf-8")

    out = gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert out == {}

    assert (work_a / "gauge.json").read_text(encoding="utf-8") == prior_a  # byte-identical
    assert (work_b / "gauge.json").read_text(encoding="utf-8") == prior_b  # byte-identical


def test_single_binding_still_writes_normally(proj):
    """No-regression check: exactly ONE bound spine must still write the real
    record -- skip-on-multiple must not become skip-on-any."""
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    (work / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work / "spine.json")

    out = gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert out == {}

    record = json.loads((work / "gauge.json").read_text(encoding="utf-8"))
    assert record["model"] == EXPECTED_MODEL
    assert record["fill_fraction"] == pytest.approx(EXPECTED_FILL)


def test_multiple_bindings_uncalibrated_flag_path_also_skips(proj, tmp_path):
    """The uncalibrated-flag path is a second write path inside the same
    handler -- it must skip on 2+ bindings too, not just the calibrated-record
    path. Neither spine gets a gauge-uncalibrated.json flag."""
    work_a = proj / ".agent-work" / "run-a"
    work_b = proj / ".agent-work" / "run-b"
    work_a.mkdir(parents=True)
    work_b.mkdir(parents=True)
    (work_a / "spine.json").write_text("{}", encoding="utf-8")
    (work_b / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work_a / "spine.json")
    _bind(proj, "s1", work_b / "spine.json")

    unknown_model_transcript = tmp_path / "unknown_model.jsonl"
    line = {
        "type": "assistant",
        "isSidechain": False,
        "timestamp": "2026-07-18T12:00:00.000Z",
        "message": {
            "model": "claude-future-9",
            "usage": {"input_tokens": 1, "cache_creation_input_tokens": 1, "cache_read_input_tokens": 99998},
        },
    }
    unknown_model_transcript.write_text(json.dumps(line) + "\n", encoding="utf-8")

    out = gw.handle_post_tool_use(_hook_data("s1", unknown_model_transcript), proj)
    assert out == {}

    assert not (work_a / gw.UNCALIBRATED_FILENAME).exists()
    assert not (work_b / gw.UNCALIBRATED_FILENAME).exists()
    assert not (work_a / "gauge.json").exists()
    assert not (work_b / "gauge.json").exists()


def test_containment_drops_one_bad_path_writes_the_remaining_single_candidate(proj):
    """One session_id bound to two spines -- one whose resolved spine path is
    OUTSIDE the `.agent-work/<work_id>/` shape (fails `_is_contained`), one
    legitimate. `_is_contained` is exercised PER PATH inside
    `resolve_gauge_path` itself (unchanged by this rework -- see its own
    docstring/#202), so the bad candidate is dropped BEFORE the handler ever
    sees the list -- `resolve_gauge_path` returns exactly ONE candidate here,
    not two. That means this scenario was never actually a multi-binding case
    from `handle_post_tool_use`'s point of view: it collapses to the ordinary
    single-candidate path (decision:gauge-write-skips-on-multiple-bindings
    only changes behavior when 2+ candidates reach the handler). Retained
    rather than retired -- it still proves per-path containment filtering,
    just no longer frames it as 'both attempted' since nothing in this design
    ever attempted both."""
    bad_spine = proj / "spine.json"  # root-level: NOT under .agent-work/
    work_good = proj / ".agent-work" / "run-good"
    work_good.mkdir(parents=True)
    bad_spine.write_text("{}", encoding="utf-8")
    (work_good / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", bad_spine)
    _bind(proj, "s1", work_good / "spine.json")

    paths = gw.resolve_gauge_path(proj, "s1")
    assert paths == [work_good / "gauge.json"]  # bad_spine's candidate fenced out

    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert (work_good / "gauge.json").exists()
    assert not (proj / "gauge.json").exists()


def test_real_subagent_transcript_finds_no_usage_and_writes_nothing(proj):
    """Adversarial confirmation of decision:gauge-write-fans-out-on-ambiguity's
    residual open question: a REAL captured subagent transcript (every line
    isSidechain: true, carrying the PARENT's own sessionId) must make
    find_latest_usage skip every line and return None, so the PostToolUse
    handler writes nothing -- even though the transcript DOES contain a
    parseable assistant/usage record, just a sidechain one."""
    assert gw.find_latest_usage(_REAL_SUBAGENT_FIXTURE) is None

    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    (work / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work / "spine.json")

    out = gw.handle_post_tool_use(_hook_data("s1", _REAL_SUBAGENT_FIXTURE), proj)
    assert out == {}
    assert not (work / "gauge.json").exists()


# --- uncalibrated model: no reading, but a visible flag ---------------------


def _unknown_model_transcript(tmp_path, model="claude-future-9"):
    transcript = tmp_path / "unknown_model.jsonl"
    line = {
        "type": "assistant",
        "isSidechain": False,
        "timestamp": "2026-07-18T12:00:00.000Z",
        "message": {
            "model": model,
            "usage": {"input_tokens": 1, "cache_creation_input_tokens": 1, "cache_read_input_tokens": 99998},
        },
    }
    transcript.write_text(json.dumps(line) + "\n", encoding="utf-8")
    return transcript


def _bound_work(proj):
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True, exist_ok=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)
    return work


def test_uncalibrated_model_writes_no_reading(proj, tmp_path):
    """The #252 regression. An unknown model previously divided its token count
    by a 200k default and wrote that as a genuine fill — which read ~5x high
    for the 1M-window models that are now the whole lineup, and tripped the
    governor at ~14% of real capacity. There must be NO reading at all."""
    work = _bound_work(proj)
    gw.handle_post_tool_use(_hook_data("s1", _unknown_model_transcript(tmp_path)), proj)
    assert not (work / "gauge.json").exists()


def test_uncalibrated_model_raises_a_visible_flag(proj, tmp_path):
    """Silence alone would be a regression of a different kind — a blind
    governor that says nothing is how this survived a whole epic unnoticed."""
    work = _bound_work(proj)
    gw.handle_post_tool_use(_hook_data("s1", _unknown_model_transcript(tmp_path)), proj)

    flag = json.loads((work / gw.UNCALIBRATED_FILENAME).read_text(encoding="utf-8"))
    assert flag["model"] == "claude-future-9"
    # the SAMPLED moment, carried from the transcript — not write time
    assert flag["observed_at"] == "2026-07-18T12:00:00.000Z"


def test_uncalibrated_flag_does_not_clobber_an_existing_reading(proj, tmp_path):
    """A good reading already on disk must survive; it ages into staleness on
    its own, which the reader already collapses to no-reading."""
    work = _bound_work(proj)
    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    before = (work / "gauge.json").read_text(encoding="utf-8")

    gw.handle_post_tool_use(_hook_data("s1", _unknown_model_transcript(tmp_path)), proj)
    assert (work / "gauge.json").read_text(encoding="utf-8") == before


def test_flag_is_cleared_once_the_model_resolves(proj, tmp_path):
    """Adding the missing row must actually silence the warning — otherwise the
    fix leaves a permanent nag and people learn to ignore it."""
    work = _bound_work(proj)
    gw.handle_post_tool_use(_hook_data("s1", _unknown_model_transcript(tmp_path)), proj)
    assert (work / gw.UNCALIBRATED_FILENAME).exists()

    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert not (work / gw.UNCALIBRATED_FILENAME).exists()
    assert (work / "gauge.json").exists()


# --- #271: gauge-skip.json -- positively-localized silence causes ------------
#
# Every test below drives the REAL handler (gw.handle_post_tool_use, loaded by
# file path via importlib.util.spec_from_file_location at module scope above)
# against real tmp_path fixtures -- the same real-file-I/O boundary the rest
# of this file already uses, and the technique the handoff names as the
# required fresh-process-equivalent evidence for these new branches: nothing
# here hand-injects sidecar content, every sidecar on disk was produced by the
# hook's own handler.


def test_ambiguous_binding_writes_skip_flag_to_every_candidate(proj):
    """Two genuinely different top-level agents sharing one session_id (#202/
    #261) still write NOTHING to gauge.json (unchanged), but now BOTH
    candidate spines get a gauge-skip.json: each one genuinely has no reading
    because of this exact ambiguity, so each deserves the signal
    (decision:skip-sidecar-fanout-and-clear -- unlike a gauge.json reading,
    a diagnostic fact about why nothing was written can never cross-write a
    misattributed value)."""
    work_a = proj / ".agent-work" / "run-a"
    work_b = proj / ".agent-work" / "run-b"
    work_a.mkdir(parents=True)
    work_b.mkdir(parents=True)
    (work_a / "spine.json").write_text("{}", encoding="utf-8")
    (work_b / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work_a / "spine.json")
    _bind(proj, "s1", work_b / "spine.json")

    out = gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert out == {}

    assert not (work_a / "gauge.json").exists()
    assert not (work_b / "gauge.json").exists()

    flag_a = json.loads((work_a / gw.SKIP_FILENAME).read_text(encoding="utf-8"))
    flag_b = json.loads((work_b / gw.SKIP_FILENAME).read_text(encoding="utf-8"))
    for flag in (flag_a, flag_b):
        assert flag["reason"] == "ambiguous-binding"
        assert flag["candidate_count"] == 2
        assert isinstance(flag["observed_at"], str) and flag["observed_at"]
    # one shared event -> one shared observed_at across every candidate
    assert flag_a["observed_at"] == flag_b["observed_at"]


def test_ambiguous_binding_with_three_candidates_fans_out_to_all_three(proj):
    """N candidates, not just two -- the fan-out is unbounded in N."""
    works = []
    for name in ("run-a", "run-b", "run-c"):
        w = proj / ".agent-work" / name
        w.mkdir(parents=True)
        (w / "spine.json").write_text("{}", encoding="utf-8")
        _bind(proj, "s1", w / "spine.json")
        works.append(w)

    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)

    for w in works:
        flag = json.loads((w / gw.SKIP_FILENAME).read_text(encoding="utf-8"))
        assert flag["reason"] == "ambiguous-binding"
        assert flag["candidate_count"] == 3


def test_no_usable_record_single_candidate_writes_skip_flag_no_candidate_count(proj, tmp_path):
    """Single resolved candidate, transcript exists and is readable, but
    compute_record finds nothing usable -- the second positively-localized
    cause. No candidate_count key (this is a single-path outcome, unlike
    ambiguous-binding)."""
    work = _bound_work(proj)
    empty_transcript = tmp_path / "no_usage.jsonl"
    empty_transcript.write_text(
        json.dumps({"type": "user", "message": {"role": "user", "content": []}}) + "\n",
        encoding="utf-8")

    out = gw.handle_post_tool_use(_hook_data("s1", empty_transcript), proj)
    assert out == {}
    assert not (work / "gauge.json").exists()

    flag = json.loads((work / gw.SKIP_FILENAME).read_text(encoding="utf-8"))
    assert flag["reason"] == "no-usable-record"
    assert "candidate_count" not in flag


def test_corrupt_transcript_single_candidate_also_writes_no_usable_record_flag(proj, tmp_path):
    """Unparseable transcript lines are also a compute_record (None, None)
    outcome -- same 'no-usable-record' treatment as an empty transcript."""
    work = _bound_work(proj)
    bad_transcript = tmp_path / "corrupt.jsonl"
    bad_transcript.write_text("{ not json\nalso not json\n", encoding="utf-8")

    gw.handle_post_tool_use(_hook_data("s1", bad_transcript), proj)

    flag = json.loads((work / gw.SKIP_FILENAME).read_text(encoding="utf-8"))
    assert flag["reason"] == "no-usable-record"


def test_zero_candidates_never_writes_a_skip_flag_anywhere(proj):
    """No binding at all -- genuinely unlocatable, no known path to write a
    sidecar TO. Must stay silent by design, unlike the two cases above."""
    gw.handle_post_tool_use(_hook_data("unbound-session", _FIXTURE), proj)
    assert list(proj.rglob(gw.SKIP_FILENAME)) == []


def test_missing_transcript_path_never_writes_a_skip_flag(proj):
    """Missing/unreadable transcript_path is checked BEFORE gauge_paths is
    even resolved -- there is no known gauge path yet, so this stays silent
    even though a real (single) binding exists."""
    work = _bound_work(proj)
    gw.handle_post_tool_use({"session_id": "s1"}, proj)
    assert not (work / gw.SKIP_FILENAME).exists()


def test_clean_write_clears_a_prior_skip_flag_at_that_path(proj, tmp_path):
    """A path that was flagged no-usable-record on one call and then resolves
    to a clean reading on the next call must have its skip flag cleared --
    mirrors _clear_uncalibrated_flag exactly."""
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    empty_transcript = tmp_path / "no_usage.jsonl"
    empty_transcript.write_text(
        json.dumps({"type": "user", "message": {"role": "user", "content": []}}) + "\n",
        encoding="utf-8")
    gw.handle_post_tool_use(_hook_data("s1", empty_transcript), proj)
    assert (work / gw.SKIP_FILENAME).exists()

    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert not (work / gw.SKIP_FILENAME).exists()
    assert (work / "gauge.json").exists()


def test_uncalibrated_outcome_clears_a_prior_skip_flag_at_that_path(proj, tmp_path):
    """The uncalibrated-flag write is also a 'resolved' outcome for this
    path (a real, if unwindowed, usage record was found) -- it must clear a
    stale skip flag too, not just a clean gauge.json write."""
    work = _bound_work(proj)
    empty_transcript = tmp_path / "no_usage.jsonl"
    empty_transcript.write_text(
        json.dumps({"type": "user", "message": {"role": "user", "content": []}}) + "\n",
        encoding="utf-8")
    gw.handle_post_tool_use(_hook_data("s1", empty_transcript), proj)
    assert (work / gw.SKIP_FILENAME).exists()

    gw.handle_post_tool_use(_hook_data("s1", _unknown_model_transcript(tmp_path)), proj)
    assert not (work / gw.SKIP_FILENAME).exists()
    assert (work / gw.UNCALIBRATED_FILENAME).exists()


def test_ambiguous_binding_skip_flags_do_not_clobber_existing_gauge_files(proj):
    """Same 'byte-identical survival' proof the existing multi-binding tests
    make for gauge.json, extended to confirm the NEW skip-flag write doesn't
    disturb a prior reading at either candidate path."""
    work_a = proj / ".agent-work" / "run-a"
    work_b = proj / ".agent-work" / "run-b"
    work_a.mkdir(parents=True)
    work_b.mkdir(parents=True)
    (work_a / "spine.json").write_text("{}", encoding="utf-8")
    (work_b / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work_a / "spine.json")
    _bind(proj, "s1", work_b / "spine.json")

    prior_a = json.dumps({"schema_version": 1, "fill_fraction": 0.1, "model": "claude-opus-4-8", "observed_at": "2026-07-18T09:00:00.000Z"})
    (work_a / "gauge.json").write_text(prior_a, encoding="utf-8")

    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)

    assert (work_a / "gauge.json").read_text(encoding="utf-8") == prior_a  # byte-identical
    assert json.loads((work_a / gw.SKIP_FILENAME).read_text(encoding="utf-8"))["reason"] == "ambiguous-binding"
    assert json.loads((work_b / gw.SKIP_FILENAME).read_text(encoding="utf-8"))["reason"] == "ambiguous-binding"


# --- #419: the reading belongs to the agent that produced it -----------------
#
# Agent-tool subagents SHARE their parent's session_id (measured live on
# harness 2.1.222 -- see .agent-work/issue-419-governor-identity/
# PROBLEM_STATEMENT.md), so a session-keyed lookup piled every crew claim under
# one key and the writer, seeing 2+ candidates, went silent. g1 landed
# spine_rail.binding_key (session_id#agent_id for a dispatched agent, the bare
# session_id for a top-level one, None when the identity is unusable); these
# tests pin the WRITER half.
#
# The failure that must never ship is a CONFIDENT WRONG NUMBER. Silence is an
# acceptable outcome here; misattribution is not.

_PARENT_AGENT_ID = "af45cec63b2835a40"  # the real id inside the captured fixture


def _agent_hook_data(session_id="s1", agent_id="a1", transcript_path=None):
    """A payload as the harness delivers it for a DISPATCHED agent: the
    parent's transcript_path plus the acting agent's own agent_id.

    Constructing this by hand is legitimate at this level -- the ban on
    supplying agent_id binds the LIVE acceptance run (gate g4), whose whole
    point is proving the harness delivers it. Here we test rejection and
    attribution, not delivery."""
    data = _hook_data(session_id, transcript_path)
    data["agent_id"] = agent_id
    return data


def test_binding_key_helper_returns_none_when_spine_rail_failed_to_load(proj, monkeypatch):
    """The `_spine_rail is None` guard lives at the binding-key call site, NOT
    only inside resolve_gauge_path. `_load_spine_rail` returns None on any
    import failure; an unguarded `_spine_rail.binding_key(...)` would raise
    into handle_post_tool_use's outer swallow, leaving the governor silent
    with zero diagnostic -- wearing the same symptom as every other silence.

    This asserts the guard where it is OBSERVABLE: `_binding_key` carries no
    swallow of its own, so a missing guard surfaces as a raised AttributeError
    here instead of being absorbed one frame up."""
    monkeypatch.setattr(gw, "_spine_rail", None)
    assert gw._binding_key({"session_id": "s1"}) is None
    assert gw._binding_key({"session_id": "s1", "agent_id": "a1"}) is None


def test_binding_key_helper_delegates_to_spine_rail(proj):
    """It is spine_rail's binding_key that composes the key -- this module
    calls it, it does not reimplement it (g1 shipped and reviewed that half)."""
    assert gw._binding_key({"session_id": "s1"}) == "s1"
    assert gw._binding_key({"session_id": "s1", "agent_id": "a1"}) == "s1#a1"
    assert gw._binding_key({"session_id": "s1", "agent_id": "bad#id"}) is None
    assert gw._binding_key({}) is None


def test_resolve_gauge_path_keys_on_the_composite_key_not_the_session(proj):
    """A parent and its dispatched agent share a session_id but hold DISTINCT
    bindings. Each key must see exactly its own -- one candidate each, so
    neither is ambiguous and neither goes silent."""
    work_parent = proj / ".agent-work" / "run-parent"
    work_sub = proj / ".agent-work" / "run-sub"
    work_parent.mkdir(parents=True)
    work_sub.mkdir(parents=True)
    _bind(proj, "s1", work_parent / "spine.json")
    _bind(proj, "s1#a1", work_sub / "spine.json")

    assert gw.resolve_gauge_path(proj, "s1") == [work_parent / "gauge.json"]
    assert gw.resolve_gauge_path(proj, "s1#a1") == [work_sub / "gauge.json"]


def test_subagent_payload_never_writes_to_the_parents_gauge(proj):
    """THE misattribution this gate exists to prevent. The parent holds the
    bare-session binding; a dispatched agent's tool call carries the parent's
    transcript_path. Resolving by session_id alone would write the PARENT's
    reading -- from the PARENT's transcript -- as if it were this agent's.

    The subagent's own key is unbound here, so the correct outcome is zero
    candidates: write nothing, anywhere."""
    work_parent = proj / ".agent-work" / "run-parent"
    work_parent.mkdir(parents=True)
    (work_parent / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work_parent / "spine.json")

    out = gw.handle_post_tool_use(_agent_hook_data("s1", "a1", _FIXTURE), proj)
    assert out == {}
    assert list(proj.rglob("gauge.json")) == []
    assert list(proj.rglob(gw.UNCALIBRATED_FILENAME)) == []
    assert list(proj.rglob(gw.SKIP_FILENAME)) == []


def test_unresolvable_identity_writes_nothing(proj):
    """The issue's own named negative control. An agent_id the key composer
    cannot use (empty, non-string, or carrying the separator) must NOT fall
    back to the bare session_id -- that files the SUBAGENT's reading under the
    PARENT's key, which is the same misattribution wearing a different hat."""
    work_parent = proj / ".agent-work" / "run-parent"
    work_parent.mkdir(parents=True)
    (work_parent / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work_parent / "spine.json")

    for bad in ("", None, "sess#agent", "..", "a/b", "a\\b", 17):
        out = gw.handle_post_tool_use(_agent_hook_data("s1", bad, _FIXTURE), proj)
        assert out == {}
        assert list(proj.rglob("gauge.json")) == [], bad
        assert list(proj.rglob(gw.UNCALIBRATED_FILENAME)) == [], bad
        assert list(proj.rglob(gw.SKIP_FILENAME)) == [], bad


def test_spine_rail_missing_writes_nothing_and_does_not_raise(proj, monkeypatch):
    """End-to-end companion to the guard unit test above: with the sibling
    module unloadable, the handler skips deliberately rather than by way of an
    exception, and still returns the neutral payload."""
    work = _bound_work(proj)
    monkeypatch.setattr(gw, "_spine_rail", None)

    assert gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj) == {}
    assert gw.handle_post_tool_use(_agent_hook_data("s1", "a1", _FIXTURE), proj) == {}
    assert not (work / "gauge.json").exists()
    assert not (work / gw.SKIP_FILENAME).exists()


# --- #419: agent_id is interpolated into a PATH, so validate it here ---------


def test_local_allowlist_is_stricter_than_spine_rails_denylist(proj):
    """g1's rejection is a hand-maintained DENYLIST (`#`, `/`, `\\`, `..`) and
    it still admits `:`, `*` and `?` -- every one of which reaches this
    module's `agent-{agent_id}.jsonl` interpolation on a Windows filesystem.
    So this module validates at its OWN boundary, with an ALLOWLIST (the real
    ids observed are hex-ish tokens plus `-` and `_`) rather than by extending
    someone else's denylist.

    Each id below is one spine_rail ADMITS and this module must not."""
    for admitted in ("a:b", "a*b", "a?b", "a<b", "a>b", 'a"b', "a|b", "a b", "a.b", "a" * 65):
        assert sr.binding_key({"session_id": "s1", "agent_id": admitted}) is not None, admitted
        assert gw._binding_key({"session_id": "s1", "agent_id": admitted}) is None, admitted


def test_local_allowlist_admits_the_real_observed_id_shape(proj):
    """The guard must not be so tight it rejects the ids the harness actually
    sends -- the probe captured `a8f0a946eaaa2fe6c`, `adb52b4ec6c7dbd40` and
    the fixture's `af45cec63b2835a40`; `-` and `_` are admitted too."""
    for good in ("a8f0a946eaaa2fe6c", "adb52b4ec6c7dbd40", _PARENT_AGENT_ID, "a-b_C9"):
        assert gw._binding_key({"session_id": "s1", "agent_id": good}) == "s1#" + good


def test_rejected_agent_id_writes_nothing_even_when_its_key_is_bound(proj):
    """A rejected value means WRITE NOTHING -- never a repaired or sanitized
    path. Adversarial setup: the offending composite key IS bound, so an
    implementation that admitted the character would have somewhere to write
    and would write there."""
    for bad in ("a:b", "a*b", "a?b"):
        work = proj / ".agent-work" / "run-sub"
        work.mkdir(parents=True, exist_ok=True)
        (work / "spine.json").write_text("{}", encoding="utf-8")
        _bind(proj, "s1#" + bad, work / "spine.json")

        out = gw.handle_post_tool_use(_agent_hook_data("s1", bad, _FIXTURE), proj)
        assert out == {}
        assert list(proj.rglob("gauge.json")) == [], bad
        assert list(proj.rglob(gw.UNCALIBRATED_FILENAME)) == [], bad
        assert list(proj.rglob(gw.SKIP_FILENAME)) == [], bad


def test_derived_subagent_transcript_shape(proj, tmp_path):
    """The acting agent's transcript is DERIVED from payload fields, never
    searched for -- which is why the identical-command race a search would
    have to worry about cannot arise here at all. Shape confirmed on disk for
    both agents of a live two-subagent probe."""
    parent = tmp_path / "proj-slug" / "ce777c3b-505c-4b76-b09b-db2c11082b83.jsonl"
    derived = gw.derive_subagent_transcript(parent, _PARENT_AGENT_ID)
    assert derived == (
        tmp_path / "proj-slug" / "ce777c3b-505c-4b76-b09b-db2c11082b83"
        / "subagents" / ("agent-" + _PARENT_AGENT_ID + ".jsonl")
    )


def test_derive_subagent_transcript_refuses_an_unusable_id(proj, tmp_path):
    """The derivation re-validates at its own boundary too: a rejected value
    yields None, never a repaired path and never an exception that the outer
    swallow would turn into indistinguishable silence."""
    parent = tmp_path / "sess.jsonl"
    for bad in ("a:b", "a*b", "a?b", "../escape", "a/b", "a\\b", "", None, 17, "a" * 65):
        assert gw.derive_subagent_transcript(parent, bad) is None, bad
    assert gw.derive_subagent_transcript(None, "a1") is None


# --- #419: fail closed -- a subagent reads its OWN transcript or nothing -----


def _bound_subagent_work(proj, agent_id="a1", session_id="s1", name="run-sub"):
    """Bind the composite key `session_id#agent_id` to its own work dir."""
    work = proj / ".agent-work" / name
    work.mkdir(parents=True, exist_ok=True)
    (work / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, session_id + "#" + agent_id, work / "spine.json")
    return work


def _parent_transcript(proj, source=None, name="sess-1"):
    """A copy of a fixture transcript at a path INSIDE tmp_path, so the
    derivation's `<parent>/subagents/agent-<id>.jsonl` sibling can be planted
    without ever writing into the repo's own fixtures directory."""
    directory = proj / "transcripts" / "proj-slug"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (name + ".jsonl")
    path.write_text((source or _FIXTURE).read_text(encoding="utf-8"),
                    encoding="utf-8", newline="\n")
    return path


def _plant_derived_transcript(parent_transcript, agent_id, source=None):
    """Materialize the acting agent's own transcript where the derivation
    says it lives, from real captured harness output."""
    derived = gw.derive_subagent_transcript(parent_transcript, agent_id)
    derived.parent.mkdir(parents=True, exist_ok=True)
    derived.write_text(
        (source or _REAL_SUBAGENT_FIXTURE).read_text(encoding="utf-8"),
        encoding="utf-8", newline="\n")
    return derived


def test_subagent_with_missing_derived_transcript_leaves_gauge_untouched(proj):
    """THE fail-closed case. agent_id present, its own transcript absent: the
    parent's transcript is RIGHT THERE and readable, and falling back to it is
    exactly the misattribution #202/#261 already tried and reverted -- fan-out
    did not fix ambiguity, it spread one agent's reading into an unrelated
    agent's work area.

    'Unchanged' is proved in BYTES and MTIME: the prior mtime is stamped to a
    distinct past value first, so the assertion cannot pass by filesystem
    timestamp granularity."""
    work = _bound_subagent_work(proj)
    gauge_path = work / "gauge.json"
    prior = json.dumps({"schema_version": 1, "fill_fraction": 0.42,
                        "model": "claude-opus-4-8", "observed_at": "2026-07-18T09:00:00.000Z"})
    gauge_path.write_text(prior, encoding="utf-8")
    stamp = 1_500_000_000_000_000_000  # 2017-07-14, unmistakably not "now"
    os.utime(gauge_path, ns=(stamp, stamp))
    before_mtime = gauge_path.stat().st_mtime_ns

    parent = _parent_transcript(proj)
    derived = gw.derive_subagent_transcript(parent, "a1")
    assert not derived.exists()  # premise: the acting agent's transcript is absent

    out = gw.handle_post_tool_use(_agent_hook_data("s1", "a1", parent), proj)
    assert out == {}

    assert gauge_path.read_text(encoding="utf-8") == prior          # bytes
    assert gauge_path.stat().st_mtime_ns == before_mtime            # mtime
    assert not (work / gw.UNCALIBRATED_FILENAME).exists()

    flag = json.loads((work / gw.SKIP_FILENAME).read_text(encoding="utf-8"))
    assert flag["reason"] == "subagent-transcript-missing"
    assert "candidate_count" not in flag
    assert isinstance(flag["observed_at"], str) and flag["observed_at"]


def test_subagent_with_missing_derived_transcript_writes_no_gauge_at_all(proj):
    """Same branch with no prior reading on disk -- the strongest form of
    'unchanged' for a file that was never there. Only the sidecar appears."""
    work = _bound_subagent_work(proj)

    gw.handle_post_tool_use(_agent_hook_data("s1", "a1", _parent_transcript(proj)), proj)

    assert list(proj.rglob("gauge.json")) == []
    assert list(proj.rglob(gw.UNCALIBRATED_FILENAME)) == []
    assert json.loads((work / gw.SKIP_FILENAME).read_text(encoding="utf-8"))["reason"] == \
        "subagent-transcript-missing"


def test_subagent_reading_is_computed_from_its_own_transcript_only(proj, monkeypatch):
    """There must be NO code path that hands the parent's transcript to
    compute_record while agent_id is present. Asserted by intercepting
    compute_record and recording exactly which path it was given."""
    work = _bound_subagent_work(proj)
    parent = _parent_transcript(proj)
    derived = _plant_derived_transcript(parent, "a1")

    seen = []
    real = gw.compute_record
    monkeypatch.setattr(gw, "compute_record",
                        lambda path, *a, **kw: (seen.append(str(path)), real(path, *a, **kw))[1])

    gw.handle_post_tool_use(_agent_hook_data("s1", "a1", parent), proj)

    assert seen == [str(derived)]
    assert str(parent) not in seen
    assert work.exists()


def test_missing_derived_transcript_never_calls_compute_record(proj, monkeypatch):
    """The fail-closed branch returns BEFORE any reading is computed -- it
    does not compute one and then decline to write it."""
    _bound_subagent_work(proj)
    seen = []
    monkeypatch.setattr(gw, "compute_record", lambda path, *a, **kw: seen.append(str(path)) or (None, None))

    gw.handle_post_tool_use(_agent_hook_data("s1", "a1", _parent_transcript(proj)), proj)
    assert seen == []


def test_top_level_payload_still_reads_the_session_transcript(proj, monkeypatch):
    """The other half of the same invariant: with no agent_id, nothing is
    derived and the session transcript is read exactly as today."""
    _bound_work(proj)
    seen = []
    real = gw.compute_record
    monkeypatch.setattr(gw, "compute_record",
                        lambda path, *a, **kw: (seen.append(str(path)), real(path, *a, **kw))[1])

    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    assert seen == [str(_FIXTURE)]


# --- #419: the sidechain filter INVERTS for a subagent -----------------------
#
# EVERY line of a subagent's own transcript is `isSidechain: true` (measured;
# docs/GAUGE_WRITER_HOOK.md's field table states both polarities), so the
# filter that is correct for a top-level agent is exactly backwards for a
# dispatched one.
#
# The three obvious assertions against _REAL_SUBAGENT_FIXTURE (4 lines, ALL
# isSidechain truthy, ALL agentId af45cec63b2835a40) are ALL satisfied by an
# implementation that checks agentId equality alone and silently drops the
# sidechain half -- the conjunct is unfalsifiable against that fixture. Hence
# _MAINCHAIN_TAIL_FIXTURE: the same 4 real lines plus ONE derived line
# carrying the MATCHING agentId with isSidechain FALSY. Only the conjunct
# skips it.
_MAINCHAIN_TAIL_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "subagent_transcript_with_mainchain_tail.jsonl")

# line 4 of the real capture: 4823 + 1088 + 15111
_REAL_SUBAGENT_TOKENS = 4823 + 1088 + 15111
_REAL_SUBAGENT_OBSERVED_AT = "2026-07-07T05:30:40.581Z"
# the derived tail line: 7 + 3000 + 300000, on a DIFFERENT model, so picking
# the wrong line is unmistakable in both the fill and the model name
_TAIL_TOKENS = 7 + 3000 + 300000


def _reaching(monkeypatch, path, agent_id=None):
    """Run find_latest_usage and report how many transcript lines the reverse
    scan actually reached -- 'any guard that loops must assert what it looped
    over'. A conjunct that was never exercised shows up here as a reach count
    that never gets past the first line."""
    real_iter = gw._iter_tail_lines_reverse
    seen = []

    def counting(p, *a, **kw):
        for line in real_iter(p, *a, **kw):
            seen.append(line)
            yield line

    monkeypatch.setattr(gw, "_iter_tail_lines_reverse", counting)
    return gw.find_latest_usage(path, agent_id), len(seen)


def test_fixture_premises_hold(proj):
    """Pin the premises the assertions below rest on, so a fixture edit
    breaks here rather than silently hollowing out the conjunct test."""
    real_lines = [l for l in _REAL_SUBAGENT_FIXTURE.read_text(encoding="utf-8").split("\n") if l.strip()]
    assert len(real_lines) == 4
    for raw in real_lines:
        line = json.loads(raw)
        assert line["isSidechain"] is True
        assert line["agentId"] == _PARENT_AGENT_ID

    tail_lines = [l for l in _MAINCHAIN_TAIL_FIXTURE.read_text(encoding="utf-8").split("\n") if l.strip()]
    assert len(tail_lines) == 5
    assert tail_lines[:4] == real_lines           # the real capture, unmodified
    tail = json.loads(tail_lines[4])
    assert tail["type"] == "assistant"
    assert tail["agentId"] == _PARENT_AGENT_ID    # MATCHING id ...
    assert not tail["isSidechain"]                # ... but main-chain


def test_find_latest_usage_takes_one_agent_id_parameter(proj):
    """One parameter, not two. 'This is agent X's own transcript' is a single
    fact; an expect_sidechain + expect_agent_id pair would let a caller set an
    incoherent combination, and the agentId equality is what makes a wrong
    derived path fail closed instead of producing a confidently misattributed
    number."""
    import inspect
    assert list(inspect.signature(gw.find_latest_usage).parameters) == ["transcript_path", "agent_id"]
    assert list(inspect.signature(gw.compute_record).parameters) == ["transcript_path", "agent_id"]


def test_real_subagent_transcript_yields_its_usage_for_its_own_agent_id(proj, monkeypatch):
    """Given the fixture's OWN agentId the inverted filter returns the real
    usage sum. Reach: 1 of 4 lines -- the answer is the last line, so the
    scan hits it immediately."""
    (found, reach) = _reaching(monkeypatch, _REAL_SUBAGENT_FIXTURE, _PARENT_AGENT_ID)
    assert found == ("claude-opus-4-8", _REAL_SUBAGENT_TOKENS, _REAL_SUBAGENT_OBSERVED_AT)
    assert reach == 1


def test_real_subagent_transcript_returns_none_for_a_different_agent_id(proj, monkeypatch):
    """A wrong derived path must fail CLOSED, not produce a confident wrong
    number. Reach: all 4 lines examined and all 4 rejected."""
    (found, reach) = _reaching(monkeypatch, _REAL_SUBAGENT_FIXTURE, "a8f0a946eaaa2fe6c")
    assert found is None
    assert reach == 4


def test_default_polarity_reaches_every_line_and_still_returns_none(proj, monkeypatch):
    """The existing assertion (test_real_subagent_transcript_finds_no_usage_
    and_writes_nothing, unedited) restated with its reach measured: at default
    polarity all 4 sidechain lines are examined and rejected."""
    (found, reach) = _reaching(monkeypatch, _REAL_SUBAGENT_FIXTURE, None)
    assert found is None
    assert reach == 4


def test_matching_agent_id_on_a_main_chain_line_is_skipped(proj, monkeypatch):
    """THE falsifier. The tail line carries the matching agentId, sits LAST so
    the reverse scan meets it FIRST, and has a much bigger usage total on a
    different model -- so an implementation checking agentId equality alone
    returns it. The conjunct must skip it and keep going to the real sidechain
    line. Reach: 2 of 5 lines (tail rejected, line 4 accepted)."""
    (found, reach) = _reaching(monkeypatch, _MAINCHAIN_TAIL_FIXTURE, _PARENT_AGENT_ID)
    assert found == ("claude-opus-4-8", _REAL_SUBAGENT_TOKENS, _REAL_SUBAGENT_OBSERVED_AT)
    assert found[1] != _TAIL_TOKENS
    assert reach == 2


def test_the_skipped_tail_line_is_itself_perfectly_usable(proj, monkeypatch):
    """Control for the test above: the tail line is skipped because of the
    sidechain conjunct, NOT because it is unparseable or missing a field. At
    DEFAULT polarity it is the answer, on the first line the scan reaches."""
    (found, reach) = _reaching(monkeypatch, _MAINCHAIN_TAIL_FIXTURE, None)
    assert found == ("claude-sonnet-5", _TAIL_TOKENS, "2026-07-07T05:31:00.000Z")
    assert reach == 1


def test_compute_record_carries_the_agent_id_through(proj):
    """compute_record takes the same single parameter and forwards it."""
    record, uncal = gw.compute_record(_REAL_SUBAGENT_FIXTURE, _PARENT_AGENT_ID)
    assert uncal is None
    assert record["model"] == "claude-opus-4-8"
    assert record["fill_fraction"] == pytest.approx(_REAL_SUBAGENT_TOKENS / 1_000_000)
    assert record["observed_at"] == _REAL_SUBAGENT_OBSERVED_AT

    assert gw.compute_record(_REAL_SUBAGENT_FIXTURE) == (None, None)


def test_dispatched_agent_writes_its_own_reading_to_its_own_binding(proj):
    """End to end, the whole point of the gate: a dispatched agent and its
    parent share one session_id but hold distinct bindings; the agent's
    reading is computed from ITS OWN transcript and lands in ITS OWN work
    dir, and the parent's gauge is not touched at all."""
    work_parent = proj / ".agent-work" / "run-parent"
    work_parent.mkdir(parents=True)
    (work_parent / "spine.json").write_text("{}", encoding="utf-8")
    _bind(proj, "s1", work_parent / "spine.json")
    work_sub = _bound_subagent_work(proj, agent_id=_PARENT_AGENT_ID)

    parent = _parent_transcript(proj)
    _plant_derived_transcript(parent, _PARENT_AGENT_ID)

    out = gw.handle_post_tool_use(_agent_hook_data("s1", _PARENT_AGENT_ID, parent), proj)
    assert out == {}

    record = json.loads((work_sub / "gauge.json").read_text(encoding="utf-8"))
    assert record["model"] == "claude-opus-4-8"
    assert record["fill_fraction"] == pytest.approx(_REAL_SUBAGENT_TOKENS / 1_000_000)
    assert record["observed_at"] == _REAL_SUBAGENT_OBSERVED_AT
    # the parent's own reading, from the parent's own transcript, is untouched
    assert not (work_parent / "gauge.json").exists()
    assert not (work_sub / gw.SKIP_FILENAME).exists()


def test_a_wrong_derived_transcript_fails_closed_rather_than_misattributing(proj):
    """If the derived path existed but belonged to a DIFFERENT agent, the
    agentId equality is the thing standing between the governor and a
    confidently misattributed number. Plant another agent's real transcript at
    this agent's derived path and require silence."""
    other = "a8f0a946eaaa2fe6c"
    work_sub = _bound_subagent_work(proj, agent_id=other)
    parent = _parent_transcript(proj)
    _plant_derived_transcript(parent, other)  # content carries agentId af45...

    gw.handle_post_tool_use(_agent_hook_data("s1", other, parent), proj)

    assert not (work_sub / "gauge.json").exists()
    assert json.loads((work_sub / gw.SKIP_FILENAME).read_text(encoding="utf-8"))["reason"] == \
        "no-usable-record"


# --- #419: the identity-resolution duration, against the 100ms budget --------

_IDENTITY_BUDGET_MS = 100.0  # the issue's stated placeholder budget


class _SlowRail:
    """spine_rail with a deliberate delay on binding_key -- the lever that
    makes 'is this a real measurement or a constant?' answerable."""

    def __init__(self, real, delay_s):
        self.real = real
        self.delay_s = delay_s

    def binding_key(self, data):
        import time
        time.sleep(self.delay_s)
        return self.real.binding_key(data)

    def __getattr__(self, name):
        return getattr(self.real, name)


def _write_a_subagent_reading(proj, agent_id=_PARENT_AGENT_ID):
    work_sub = _bound_subagent_work(proj, agent_id=agent_id)
    parent = _parent_transcript(proj)
    _plant_derived_transcript(parent, agent_id)
    gw.handle_post_tool_use(_agent_hook_data("s1", agent_id, parent), proj)
    return json.loads((work_sub / "gauge.json").read_text(encoding="utf-8"))


def test_identity_resolution_duration_is_recorded_within_budget(proj):
    """Identity is an O(1) payload lookup plus a derived path, so the 100ms
    placeholder budget should never be in danger -- but 'should' is not
    evidence, so the writer records what it actually cost."""
    record = _write_a_subagent_reading(proj)
    assert set(record.keys()) == {
        "schema_version", "fill_fraction", "model", "observed_at", "identity_resolution_ms"}
    value = record["identity_resolution_ms"]
    assert isinstance(value, float)
    assert 0.0 <= value < _IDENTITY_BUDGET_MS


def test_identity_resolution_duration_tracks_a_deliberately_slowed_step(proj, monkeypatch):
    """A constant would satisfy the assertion above. Slow the identity step by
    a known amount and require the recorded value to follow it -- if the field
    were hardcoded, or timed something else, this fails."""
    fast = _write_a_subagent_reading(proj)["identity_resolution_ms"]

    # Same agent, same binding, same derived transcript -- the ONLY thing that
    # differs on the second pass is the deliberate delay, so the second
    # record's value minus the first is the delay and nothing else.
    monkeypatch.setattr(gw, "_spine_rail", _SlowRail(gw._spine_rail, 0.030))
    slow = _write_a_subagent_reading(proj)["identity_resolution_ms"]

    assert slow >= 25.0            # the 30ms delay is in there
    assert slow > fast + 20.0      # and it is the DELTA that moved, not a floor
    assert slow < _IDENTITY_BUDGET_MS


def test_top_level_record_keeps_exactly_the_frozen_four_fields(proj):
    """The fifth field is additive and OPTIONAL, and it appears only on the
    dispatched-agent path: a payload with no agent_id must stay byte-identical
    to today's behavior, and the frozen 4-field record is what the reader and
    the pre-existing tests pin. There is no identity to resolve for a
    top-level agent, so there is nothing to report."""
    work = _bound_work(proj)
    gw.handle_post_tool_use(_hook_data("s1", _FIXTURE), proj)
    record = json.loads((work / "gauge.json").read_text(encoding="utf-8"))
    assert set(record.keys()) == {"schema_version", "fill_fraction", "model", "observed_at"}


def test_the_four_required_fields_keep_their_meaning_alongside_the_fifth(proj):
    """gauge_reader validates the presence of its four required fields and
    does not reject extras, so the fifth costs zero reader change. Pin that
    the four are still exactly what they were."""
    record = _write_a_subagent_reading(proj)
    assert record["schema_version"] == 1
    assert record["model"] == "claude-opus-4-8"
    assert record["fill_fraction"] == pytest.approx(_REAL_SUBAGENT_TOKENS / 1_000_000)
    assert record["observed_at"] == _REAL_SUBAGENT_OBSERVED_AT  # SAMPLED, not write time


def test_no_default_window_constant_remains(proj):
    """The 200k default IS the bug — guard against a well-meaning reintroduction
    of a fallback on the reading path."""
    assert not hasattr(gw, "DEFAULT_WINDOW")


def test_claude_opus_5_is_calibrated(proj):
    """Verified against platform.claude.com Models overview, 2026-07-25:
    claude-opus-5 has a 1M context window (default and maximum)."""
    assert gw.MODEL_WINDOWS["claude-opus-5"] == 1_000_000


# --- atomic write / torn-read (TF9) ------------------------------------------

def test_concurrent_reads_never_observe_a_torn_record(proj):
    """Hammer writes and reads of the same gauge.json concurrently. Every
    read that returns content must be complete, valid JSON with exactly the
    frozen 4 keys -- never a JSONDecodeError, never a partial/truncated
    record. This is the atomic tmp+rename guarantee (TF9), exercised under
    real thread scheduling rather than asserted only by code inspection."""
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    gauge_path = work / "gauge.json"

    record_a = {"schema_version": 1, "fill_fraction": 0.11, "model": "claude-opus-4-8", "observed_at": "2026-07-18T10:00:00.000Z"}
    record_b = {"schema_version": 1, "fill_fraction": 0.99, "model": "claude-sonnet-5", "observed_at": "2026-07-18T10:00:01.000Z"}

    stop = threading.Event()
    failures = []

    def writer():
        # stop MUST be set even if an individual write hits a transient
        # Windows sharing violation -- otherwise the reader thread (below)
        # spins forever and, being non-daemon, blocks the whole process
        # from exiting even after this test function returns.
        try:
            for i in range(200):
                try:
                    gw._atomic_write_json(gauge_path, record_a if i % 2 == 0 else record_b)
                except OSError:
                    continue
        finally:
            stop.set()

    def reader():
        while not stop.is_set():
            if not gauge_path.exists():
                continue
            try:
                text = gauge_path.read_text(encoding="utf-8")
            except OSError:
                continue
            if not text:
                continue
            try:
                record = json.loads(text)
            except json.JSONDecodeError:
                failures.append(text)
                continue
            if set(record.keys()) != {"schema_version", "fill_fraction", "model", "observed_at"}:
                failures.append(record)

    t_writer = threading.Thread(target=writer, daemon=True)
    t_reader = threading.Thread(target=reader, daemon=True)
    t_writer.start()
    t_reader.start()
    t_writer.join(timeout=30)
    stop.set()  # safety net: make sure the reader is told to stop regardless
    t_reader.join(timeout=30)

    assert failures == []


def test_atomic_write_uses_tmp_then_replace(proj):
    """Direct check of the write primitive: the target is only ever touched
    by os.replace from a distinct tmp file, never opened for direct writing."""
    gauge_path = proj / ".agent-work" / "run1" / "gauge.json"
    record = {"schema_version": 1, "fill_fraction": 0.5, "model": "claude-opus-4-8", "observed_at": "2026-07-18T10:00:00.000Z"}
    gw._atomic_write_json(gauge_path, record)
    assert json.loads(gauge_path.read_text(encoding="utf-8")) == record
    assert not gauge_path.with_name(gauge_path.name + ".tmp").exists()


# --- wiring sanity: this hook never returns a decision payload --------------

def test_main_never_prints_and_always_exits_zero(proj, capsys):
    rc = gw.main(["gauge_writer_hook.py"], json.dumps({"session_id": "s1", "transcript_path": str(_FIXTURE)}))
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_malformed_stdin_fails_open(proj, capsys):
    rc = gw.main(["gauge_writer_hook.py"], "{ not json")
    assert rc == 0
    assert capsys.readouterr().out == ""
