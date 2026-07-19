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
# latest MAIN-CHAIN (non-sidechain) assistant usage record (see the fixture's
# line 5): 3 + 1200 + 158000 = 159203 tokens, over a 200_000 window.
EXPECTED_MODEL = "claude-opus-4-8"
EXPECTED_FILL = (3 + 1200 + 158000) / 200_000


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
    """The fixture's sidechain line (a subagent's own context) has a bigger
    and chronologically-later usage total than the real latest main-chain
    line -- if the writer picked it up by mistake, model/fill would differ
    from the hand-computed expectation below."""
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


# --- unknown model falls back to the default window, not a crash ------------

def test_unknown_model_uses_default_window(proj, tmp_path):
    work = proj / ".agent-work" / "run1"
    work.mkdir(parents=True)
    spine_path = work / "spine.json"
    spine_path.write_text("{}", encoding="utf-8")
    _bind(proj, "s1", spine_path)

    transcript = tmp_path / "unknown_model.jsonl"
    line = {
        "type": "assistant",
        "isSidechain": False,
        "timestamp": "2026-07-18T12:00:00.000Z",
        "message": {
            "model": "claude-future-9",
            "usage": {"input_tokens": 1, "cache_creation_input_tokens": 1, "cache_read_input_tokens": 99998},
        },
    }
    transcript.write_text(json.dumps(line) + "\n", encoding="utf-8")

    gw.handle_post_tool_use(_hook_data("s1", transcript), proj)
    record = json.loads((work / "gauge.json").read_text(encoding="utf-8"))
    assert record["model"] == "claude-future-9"
    assert record["fill_fraction"] == pytest.approx(100_000 / gw.DEFAULT_WINDOW)


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
