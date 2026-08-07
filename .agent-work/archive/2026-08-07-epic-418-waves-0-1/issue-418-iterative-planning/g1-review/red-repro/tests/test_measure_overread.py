"""Unit tests for scripts/measure_overread.py.

Fixture-based against the small SYNTHETIC corpus at
tests/fixtures/overread_corpus/ (see that directory's README.md for why it
is synthetic and what schema it is modeled on). No real filesystem paths
outside the repo/tmp_path; no network; deterministic.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = Path(__file__).resolve().parent / "fixtures" / "overread_corpus"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mo = load("measure_overread")


# --- classify_path -----------------------------------------------------------

def test_classify_spine_json_is_state():
    assert mo.classify_path("C:/Programs/x/.agent-work/issue-227/spine.json") == "state"


def test_classify_cycle_json_is_state():
    assert mo.classify_path("/repo/.agent-work/explore/cycle-2.json") == "state"


def test_classify_generic_checklist_json_is_state():
    assert mo.classify_path("/repo/.agent-work/foo/my_checklist.json") == "state"


def test_classify_execute_json_is_state():
    assert mo.classify_path("C:\\repo\\.agent-work\\issue-227\\execute.json") == "state"


def test_classify_checklist_engine_py_is_engine_source():
    assert mo.classify_path("C:/Programs/x/scripts/checklist_engine.py") == "engine-source"


def test_classify_journal_file_does_not_count():
    # A .journal audit log is a different artifact from the live-state read
    # the definition targets -- explicitly excluded (see module docstring).
    assert mo.classify_path("/repo/.agent-work/issue-227/execute.json.journal") is None
    assert mo.classify_path("/repo/.agent-work/issue-227/spine.json.journal") is None


def test_classify_references_and_templates_do_not_count():
    assert mo.classify_path("/repo/skills/implementer/references/global-everyone.md") is None
    assert mo.classify_path("/repo/skills/implementer/templates/PLAN.template.json") is None


def test_classify_schema_doc_does_not_count():
    assert mo.classify_path("/repo/docs/CHECKLIST_SCHEMA.md") is None


def test_classify_unrelated_source_does_not_count():
    assert mo.classify_path("/repo/scripts/gauge_reader.py") is None


# --- scan_transcript -----------------------------------------------------------

def test_scan_transcript_zero_structural_reads():
    result = mo.scan_transcript(CORPUS_DIR / "run-clean-explorer.jsonl")
    assert result.structural_reads == 0
    assert result.skipped_lines == 0


def test_scan_transcript_several_structural_reads():
    result = mo.scan_transcript(CORPUS_DIR / "run-heavy-scaffolding.jsonl")
    assert result.structural_reads == 3
    assert result.state_reads == 2  # spine.json + cycle-2.json
    assert result.engine_source_reads == 1  # checklist_engine.py
    assert result.skipped_lines == 0


def test_scan_transcript_discriminates_journal_and_references():
    result = mo.scan_transcript(CORPUS_DIR / "run-mixed-with-journal.jsonl")
    assert result.structural_reads == 1
    assert result.state_reads == 1
    assert result.engine_source_reads == 0


def test_scan_transcript_skips_malformed_lines_without_crashing():
    result = mo.scan_transcript(CORPUS_DIR / "run-malformed-line.jsonl")
    assert result.structural_reads == 2
    assert result.engine_source_reads == 2
    assert result.skipped_lines == 1


def test_scan_transcript_counter_actually_discriminates():
    # The zero-read and several-read runs must differ -- proves the counter
    # is not a constant.
    zero = mo.scan_transcript(CORPUS_DIR / "run-clean-explorer.jsonl")
    several = mo.scan_transcript(CORPUS_DIR / "run-heavy-scaffolding.jsonl")
    assert zero.structural_reads != several.structural_reads
    assert zero.structural_reads == 0
    assert several.structural_reads > 0


# --- scan_corpus / aggregate ---------------------------------------------------

def test_scan_corpus_is_sorted_by_filename():
    results = mo.scan_corpus(CORPUS_DIR)
    names = [r.transcript.name for r in results]
    assert names == sorted(names)


def test_scan_corpus_covers_all_four_fixtures():
    results = mo.scan_corpus(CORPUS_DIR)
    assert len(results) == 4


def test_aggregate_sums_across_committed_corpus():
    results = mo.scan_corpus(CORPUS_DIR)
    # 0 (clean) + 3 (heavy) + 1 (mixed) + 2 (malformed) == 6, per the
    # committed corpus's README table.
    assert mo.aggregate(results) == 6


def test_scan_corpus_deterministic_across_repeated_calls():
    first = mo.aggregate(mo.scan_corpus(CORPUS_DIR))
    second = mo.aggregate(mo.scan_corpus(CORPUS_DIR))
    assert first == second


# --- format_report --------------------------------------------------------------

def test_format_report_has_per_run_and_aggregate_line():
    results = mo.scan_corpus(CORPUS_DIR)
    report = mo.format_report(results)
    for r in results:
        assert r.transcript.name in report
    assert "AGGREGATE_STRUCTURAL_READS: 6" in report


# --- CLI ---------------------------------------------------------------------

def _child_env():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def test_cli_default_corpus_prints_aggregate_line():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "measure_overread.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_child_env(),
    )
    assert proc.returncode == 0
    assert "AGGREGATE_STRUCTURAL_READS: 6" in proc.stdout


def test_cli_missing_corpus_dir_fails_visibly():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "measure_overread.py"), "--corpus", "tests/fixtures/does-not-exist"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_child_env(),
    )
    assert proc.returncode != 0
