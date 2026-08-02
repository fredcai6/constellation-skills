# Gated Plan: Lane A — Tire-Wear / Compound-Prior Production Hardening

## Problem Statement

Make the tire-wear compound-prior solver pristine enough to be trusted as an evo regularizer:
(A1) retire stale issues; (A2) create a real-race validation harness; (A3) make the production bridge from unified solver → compact runtime artifact explicit and clean — removing the post-hoc patch hack and making `fit_tire_wear_model` the canonical producer.

## Intent Protected

- `load_time_safe_compound_prior` always receives a validating `compound_prior_summary.json`
- No same-season leakage in production (unless `allow_same_season_research=True`)
- `fit_tire_wear_model` is the sole canonical path; `fit_compound_prior` becomes exploratory
- All 158 unit tests stay green throughout

## Scope

**Allowed regions/files:**
- `scripts/fit_compound_prior.py` (fix `_summary_payload`)
- `scripts/promote_runtime_artifact.py` (new)
- `scripts/validate_tire_wear_fit.py` (new)
- `scripts/build_rolling_compound_priors.py` (update to unified solver path)
- `tests/unit/compound_prior/` (add tests for promote script)
- `docs/architecture/packets/compound_prior.md` (add promote step, mark fit_compound_prior exploratory)

**Not scope:**
- Core solver logic in `src/compound_prior/solver.py`, `baseline.py`, `runtime_normalization.py`
- Evo integration changes beyond what already exists
- Gold artifact regen (2018–2026) — Triage candidate
- CI integration of validation harness

**Specific exclusions:**
- `src/compound_prior/diagnostics.py` — `write_tire_wear_run_bundle()` stays as-is; do not extend it
- `params/gold/` — do not modify existing gold files in this lane
- `tests/integration/` — do not add new integration tests

## Structural Baseline

**Need:** no  
**Status:** skipped — architecture packet (`docs/architecture/packets/compound_prior.md`) is current and accurate; no Cartographer pass needed  
**Evidence:** packet read during interrogation; canonical path already listed as `fit_tire_wear_model`

## Authority / Assumptions

- Close #49 and #50: user confirmed both are fully implemented; tests green; nothing dropped
- Unified solver (Option B): user decision
- Separate promote step (Option E2): user decision
- DB as source of truth for harness (H1 script-only): user decision
- `build_rolling_compound_priors.py` update in scope: user decision
- Gold regen (2018–2026) deferred: user decision
- `fit_compound_prior.py` marked exploratory, not deleted: low-risk reversible assumption (safe to keep for debug use)
- Assumption: `CompoundPriorFitConfig` has `accepted_compounds` and `reference_compound` attributes (verified)

## Test Mode

**Plan default:** TDD for all behavior changes (new scripts, `_summary_payload` fix, `build_rolling_compound_priors.py` swap)  
**Inspection-only gates:** Gate 1 (GitHub close only — no code surface)

## Project Mechanics Hooks

| Moment | Hook | Owner | Evidence |
|---|---|---|---|
| Before Gate 1 | none | Pilot | — |
| Gate 1 close | Close #49 and #50 on GitHub | Pilot | issue URLs |
| Before Gate 2 | branch `claude/lane-a-validation-harness` | Pilot | branch name |
| Gate 2 evidence accepted | commit + PR | Crew/Pilot | PR URL |
| Before Gate 3 | branch `claude/lane-a-promote-bridge` | Pilot | branch name |
| Gate 3 evidence accepted | commit + PR | Crew/Pilot | PR URL |
| Before Gate 4 | branch `claude/lane-a-pipeline-cleanup` | Pilot | branch name |
| Gate 4 evidence accepted | commit + PR | Crew/Pilot | PR URL |
| Before closeout | archive `.agent-work/20260525-lane-a-tire-hardening/` | Pilot | archive path |

## Gates

---

### Gate 1: Close #49 and #50

**Purpose:** Retire stale issues with evidence; no code change required.  
**Crew cycle:** Pilot-only action — no Crew handoff needed  
**Implementer handoff:** not applicable — Pilot closes directly  
**Reviewer handoff:** skipped — closing issues against confirmed green tests is not ambiguous  
**Suggested model tier:** n/a  
**Test mode:** inspection-only — no code surface  
**Allowed scope:** GitHub issue comments/close only  
**Specific exclusions:** no code changes  

**Close criteria:**
- [ ] #49 closed with comment referencing green test evidence and "windowed baseline" doc fix
- [ ] #50 closed with comment referencing green test evidence and `fit_tire_wear_model` / `write_tire_wear_run_bundle` / `load_tire_wear_run_bundle` all present
- [ ] No code changes committed

**Required evidence:**
- `py -m pytest tests/unit/compound_prior/ -q --tb=no` output (158 passed)
- GitHub issue URLs showing CLOSED state

**Stop conditions:** none expected  
**Next gate:** Gate 2

---

### Gate 2: A2 — Real-Race Validation Harness

**Purpose:** `scripts/validate_tire_wear_fit.py` — DB-backed script that runs `fit_tire_wear_model` over configurable seasons, saves compact validation report, exits non-zero on required-diagnostic failures.  
**Crew cycle:** implementer Crew → integrate evidence → reviewer Crew → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required  
**Suggested model tier:** simple bounded — scope is one new script with clear acceptance criteria  
**Test mode:** TDD — write unit tests first for report assertion logic; script itself tested via `--dry-run` smoke if feasible  
**Allowed scope:** `scripts/validate_tire_wear_fit.py` (new), `tests/unit/compound_prior/test_validate_harness.py` (new)  
**Specific exclusions:** no changes to `src/compound_prior/`, no changes to existing test files  

**Required behavior:**
- CLI: `py -m scripts.validate_tire_wear_fit --db <path> --seasons 2023 2024 [--output-dir outputs/validation]`
- For each season: extract all races via `RaceSegmentExtractor`, run `fit_tire_wear_model`, save compact JSON report
- Report fields: `season`, `converged`, `passes_run`, `support_by_compound` (obs count + weighted count per C#), `dropped_compounds`, `warnings`, `slope_sensitivity_summary` (min/max gamma by compound)
- Fail (non-zero exit) if: any required report field missing, any season has `dropped_compounds` that were in `accepted_compounds` without a warning, solver did not converge after max passes
- No leakage assertion: solver must not use target-year data for prior selection (validation is fitting, not prior loading — note in report header)

**Close criteria:**
- [ ] Script runs to completion against real DB (or returns clear error if DB unavailable)
- [ ] Report written to `outputs/validation/validate_<season>.json` per season
- [ ] Exit code non-zero when required diagnostic missing in unit test
- [ ] `py -m pytest tests/unit/compound_prior/test_validate_harness.py -q` passes
- [ ] Full suite still green: `py -m pytest tests/unit/compound_prior/ -q --tb=no`

**Required evidence:**
- pytest output for new test file
- Full suite output (158+ passed)
- Reviewer sign-off on report schema and exit-code logic

**Stop conditions:** DB not available → report to Pilot; ambiguous accepted_compounds for a season → ask Pilot  
**Next gate:** Gate 3

---

### Gate 3: A3a — Promote Bridge

**Purpose:** Make the run bundle → runtime artifact bridge explicit and self-verifying. Two parts: (1) fix `_summary_payload()` to emit runtime fields natively; (2) write `scripts/promote_runtime_artifact.py`.  
**Crew cycle:** implementer Crew → integrate evidence → reviewer Crew → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required  
**Suggested model tier:** simple bounded — well-defined JSON field additions and a new script  
**Test mode:** TDD  
**Allowed scope:**
- `scripts/fit_compound_prior.py` — fix `_summary_payload()` only
- `scripts/promote_runtime_artifact.py` (new)
- `tests/unit/compound_prior/test_fit_compound_prior_cli.py` — extend for new fields
- `tests/unit/compound_prior/test_promote_artifact.py` (new)  
**Specific exclusions:** `src/compound_prior/runtime_normalization.py` — do not touch; `src/compound_prior/diagnostics.py` — do not touch  

**Part 1 — fix `_summary_payload()`:**
- Add to output: `artifact_id` (caller-supplied or auto-generated slug), `source_season` (int), `accepted_compounds` (list), `reference_compound` (str), `effect_space="normalized_fractional"`, `normalize_residuals=True`
- These fields make the output of `fit_compound_prior_artifacts()` directly loadable by `load_compound_prior_artifact()` without patching
- `artifact_id` default: `f"compound-prior-{source_season}"` when not supplied by caller

**Part 2 — `scripts/promote_runtime_artifact.py`:**
- CLI: `py -m scripts.promote_runtime_artifact --bundle-dir <path> --season <year> --dest <root> [--artifact-id <id>]`
- Reads `compound_parameters.json` from run bundle (written by `write_tire_wear_run_bundle`)
- Constructs `compound_prior_summary.json` payload with all required runtime fields
- Validates payload by calling `load_compound_prior_artifact()` on a temp path before writing
- Writes to `<dest>/<season>/compound_prior_summary.json` (creates dir)
- Prints field summary on success; exits non-zero on validation failure

**Close criteria:**
- [ ] `load_compound_prior_artifact(path)` succeeds on artifact written by fixed `fit_compound_prior_artifacts()`
- [ ] `load_compound_prior_artifact(path)` succeeds on artifact written by `promote_runtime_artifact.py`
- [ ] `py -m pytest tests/unit/compound_prior/test_promote_artifact.py -q` passes
- [ ] `py -m pytest tests/unit/compound_prior/test_fit_compound_prior_cli.py -q` passes
- [ ] Full suite still green

**Required evidence:**
- pytest output for both test files
- Full suite output
- Reviewer sign-off confirming round-trip: run bundle → promote → `load_compound_prior_artifact` passes

**Stop conditions:** `compound_parameters.json` lacks a field needed by the runtime artifact schema → check `write_tire_wear_run_bundle` output, report to Pilot  
**Next gate:** Gate 4

---

### Gate 4: A3b — Pipeline Cleanup

**Purpose:** Update `build_rolling_compound_priors.py` to use `fit_tire_wear_model` + promote step; remove `_patch_summary_json` hack; mark `fit_compound_prior.py` as exploratory; update architecture doc.  
**Crew cycle:** implementer Crew → integrate evidence → reviewer Crew → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required  
**Suggested model tier:** stronger broad/ambiguous — `build_rolling_compound_priors.py` is a complex orchestration script; the solver swap has more surface than it looks  
**Test mode:** TDD where surface exists; inspection-only for doc changes  
**Allowed scope:**
- `scripts/build_rolling_compound_priors.py` (swap solver, remove `_patch_summary_json`)
- `scripts/fit_compound_prior.py` (add deprecation/exploratory marker to module docstring)
- `docs/architecture/packets/compound_prior.md` (add promote step to canonical path, note fit_compound_prior exploratory)
- `tests/unit/compound_prior/test_fit_race_baseline_cli.py` or new test file if needed  
**Specific exclusions:** `params/gold/` — do not touch existing gold files; `src/compound_prior/` — no src changes in this gate  

**Required changes to `build_rolling_compound_priors.py`:**
- Replace `fit_compound_prior_artifacts()` call with `fit_tire_wear_model()` + `write_tire_wear_run_bundle()` per round
- Replace `_patch_summary_json()` with call to promote logic (import from `promote_runtime_artifact` or inline equivalent)
- Remove `_patch_summary_json` function entirely
- Artifact ID convention: `f"rolling-{target_year}-before-r{round_num}"` (preserve existing naming)
- Source season: `target_year` (preserve existing logic)

**Required changes to docs:**
- Canonical Execution Path: add step 4.5 `promote_runtime_artifact → compact runtime prior artifact`
- Scripts section: note `fit_compound_prior.py` is exploratory/debug only, not canonical
- Known Limits: note gold artifacts (2018–2025) were produced via old path; regen planned

**Close criteria:**
- [ ] `_patch_summary_json` function gone from `build_rolling_compound_priors.py`
- [ ] `fit_compound_prior.py` docstring says "exploratory/debug — not the canonical production path"
- [ ] Architecture packet updated with promote step and exploratory note
- [ ] Full suite still green: `py -m pytest tests/unit/compound_prior/ -q --tb=no`
- [ ] Reviewer confirms `build_rolling_compound_priors.py` logic is equivalent (same artifact naming, same season logic)

**Required evidence:**
- Full suite output
- Diff of `build_rolling_compound_priors.py` showing `_patch_summary_json` removed
- Reviewer sign-off

**Stop conditions:** `build_rolling_compound_priors.py` uses DB-backed observations that don't exist in current run — note as assumption, do not block; `fit_tire_wear_model` API mismatch with current rolling prior inputs → report to Pilot  
**Next gate:** closeout

---

## Triage Candidate Log

| Candidate | Reason | Anchor | Evidence | Status |
|---|---|---|---|---|
| Gold regen 2018–2026 from unified solver | Current golds (2022–2025) produced via old `fit_compound_prior` path; unified solver should be canonical source | Gate 4 / `params/gold/` | `params/gold/compound_prior/2024/compound_prior_summary.json` keys inspection | noted |

---

## Plan-Level Stop Conditions

- `compound_parameters.json` from run bundle lacks fields needed by runtime artifact schema
- `fit_tire_wear_model` API is incompatible with `build_rolling_compound_priors.py` observation inputs
- Any gate's implementation causes unit test regressions

## Final Completion Criteria

- [ ] Gate 1: #49 and #50 closed on GitHub with evidence
- [ ] Gate 2: validation harness script + tests merged
- [ ] Gate 3: promote bridge + `_summary_payload` fix + tests merged
- [ ] Gate 4: pipeline cleanup + docs merged
- [ ] Full suite green after all gates
- [ ] Triage candidate (gold regen) routed as issue
- [ ] Architecture reconciliation: compound_prior packet updated (done in Gate 4)
