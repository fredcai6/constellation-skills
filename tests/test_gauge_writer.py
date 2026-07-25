"""Unit tests for scripts/hooks/gauge_writer_hook.py.

Fixture-based against tests/fixtures/golden_transcript.jsonl (a hand-built
transcript modeled on a real Claude Code session transcript captured and
inspected live during implementation -- see docs/GAUGE_WRITER_HOOK.md for the
exact schema this depends on). No real filesystem paths outside tmp_path; no
network; no dependency on a live harness.
"""

import importlib.util
import json
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
    sr.save_binding(proj, {session_id: {"spine": str(spine_path), "engine_session": "eng-1", "worktree": str(proj)}})


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
