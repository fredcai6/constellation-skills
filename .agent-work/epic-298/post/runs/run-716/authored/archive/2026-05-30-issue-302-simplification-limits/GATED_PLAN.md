# Issue #302 — Gate plan (draft)

## Gates

| Gate | Deliverable | Close evidence |
|------|-------------|----------------|
| **g1** | `verify_simplification_limits` + tests + `config/simplification_baseline.json` | pytest unit; `py -m src.utils.simplification_limits --baseline` |
| **g2** | Agent wiring + `run_tests.py` delegation + fix compliance crash | `py run_tests.py --compliance` exits 0 with baseline |
| **g3** | Split `race_report.py` → `src/reporting/` package | `test_race_report.py`; strict limits on `src/reporting` |
| **g4** | Split `database.py` → `src/data/database/` package | `test_database.py` + classifications; strict limits on `src/data` |
| **g5** | Triage docs for remaining 10 mega targets | `triage-candidates/*.md` for Commander/user issue filing |

## Split strategy (g3/g4)

**race_report** — single class today; split by concern:

- `race_report_data.py` — DB fetch / actual results assembly
- `race_report_markdown.py`, `race_report_html.py`, `race_report_json.py` — format writers
- `race_report.py` — thin `RaceReportGenerator` orchestrator

**database** — `DatabaseManager` method groups (from line map):

- `_core` — init, schema upgrades, query_builder wiring
- `_sessions` — insert session/lap/telemetry/weather, collection flags
- `_results` — race/quali/practice/sprint result getters
- `_telemetry` — processed telemetry, speed profiles
- `_metadata` — circuits, entry lists, classifications, points, environment

Facade keeps `from src.data.database import DatabaseManager` unchanged.

## Triage (post-g5, user approves issues)

Evo: `models.py`, `data_adapter.py`, `fusion_training.py`, `practice_preprocessor.py`, `module_adapters.py`, `gold_cycle/runner.py`

Compound prior: `diagnostics.py`, `solver.py`

Physics: `windowed_solver.py`

Tests: `test_fusion_training.py`, `test_session_dropout.py`, `test_data_adapter.py`
