# Issue #302 — Resolved understanding

## Problem

Introduce machine-checkable simplification limits and agent wiring; consolidate stale `run_tests.py --compliance`; split a sizable chunk of mega-files now; baseline + triage the rest.

## Protected intent

- **One canonical path** for limits (`verify_simplification_limits`); no silent dual limit sets.
- **Structural splits only** for `race_report` and `database` — same public APIs, no query/report semantics change.
- **DB canonical** constraint unchanged.

## In scope (this run)

1. `src/utils/simplification_limits.py` + tests + CLI (`py -m src.utils.simplification_limits`)
2. Agent wiring: REVIEW_SURVEY, ORCHESTRATOR, CREW, engine-config, TESTING.md
3. `run_tests.py --compliance` delegates to canonical verifier; fix complexity-check crash when radon absent/nonzero
4. **Split** `src/reporting/race_report.py` (format/render modules, thin facade)
5. **Split** `src/data/database.py` (core/schema/insert vs results vs telemetry vs classifications mixins or submodules; `DatabaseManager` facade)
6. Committed **baseline allowlist** for remaining ≥1000-line files
7. Triage issues for remaining mega-file burn-down (by region)

## Out of scope (#302)

- `models.py`, `compound_prior/diagnostics.py`, `solver.py`, `data_adapter.py`, `fusion_training.py`, large test megas — separate issues

## Compliance archaeology

Legacy `--compliance` uses **500 SLOC / 50 function / radon grade C+**, **src/ only**, non-blank non-comment line count. Today: **25 src files fail SLOC**; **radon not installed** → complexity leg returns `None` → **TypeError** (latent bug). Not aligned with issue #302 limits (1000 file / 100 function / CC<20 / src+tests).
