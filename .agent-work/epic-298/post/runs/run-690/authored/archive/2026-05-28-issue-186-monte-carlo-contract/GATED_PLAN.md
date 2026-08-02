# Gated Plan: Issue 186 Monte Carlo Contract

## Problem Statement

Implement the issue #186 Monte Carlo result contract decisions across the sampled evo runtime and strategy/fantasy layers. Current code still exposes `ClassificationFutureSet` v1 string futures, supports `max_futures` truncation, and emits unversioned `FinalOrderSampleSet` objects without typed stage snapshots.

## Intent Protected

Sampled evo runtime owns production Monte Carlo race-result semantics. Strategy/fantasy consumes a narrow, validated adapter output and does not import evo runtime internals.

## Scope

**Allowed regions/files:** `src/strategy/**` contract/report/scoring call sites, `src/evo_predictor/runtime_contracts.py`, `src/evo_predictor/sample_state_adapter.py`, `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/sampled_runtime_serialization.py`, directly related tests/fixtures, `docs/evo/sampled_runtime_strategy_contract.md`, `docs/report_schemas/strategy_reports.md`, `docs/report_schemas/README.md` if needed.  
**Not scope:** model/training quality changes, data ingestion, real-data artifact generation, gold artifact promotion, push/PR/merge/issue close.  
**Specific exclusions:** no strategy direct dependency on evo runtime internals; no `max_futures` replacement config; no manual edits to bulky generated outputs.

## Structural Baseline

**Need:** `no`  
**Status:** `established`  
**Evidence:** `docs/architecture/index.md` verified 2026-05-26. Boundary is known: `src/evo_predictor/` owns sampled runtime, `src/strategy/` owns fantasy adapter/reporting.

## Authority / Assumptions

- User explicitly answered: implement everything now.
- Issue comments define contract decisions.
- Orchestrator permits branch, local code/docs edits, tests, and local commits; ask before push, PR, merge, or issue close.
- Backwards compatibility is not a major concern per repo instructions.

## Test Mode

**Plan default:** TDD for behavior changes. Focused tests first, then region suites because this crosses evo and strategy/data-layer regions.  
**Inspection-only rationale:** Documentation-only checks in Gate 3 may use inspection plus doc-specific tests where no runtime surface exists.

## Project Mechanics Hooks

| Moment | Hook | Owner | Evidence |
|---|---|---|---|
| Before gate | branch | Pilot | `codex/issue-186-mc-contract` |
| After gate evidence accepted | local commit allowed | Pilot unless user redirects | commit SHA if created |
| Before closeout | archive workflow artifacts | Pilot | `.agent-work/archive/<date>-issue-186-monte-carlo-contract/` |
| After archive | push/PR/merge/close issue require ask | Pilot | user approval required |

## Gates

### Gate 1: Strategy `ClassificationFutureSet` v2

**Purpose:** Move strategy-facing futures to the decided v2 index-permutation contract and remove truncation semantics from the adapter/report path.  
**Crew cycle:** `implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close`  
**Implementer handoff:** `required`  
**Reviewer handoff:** `required`  
**Suggested model tier:** `simple bounded, because scope is localized but touches fixtures and report call sites`  
**Test mode:** `TDD required`  
**Allowed scope:** `src/strategy/classification_futures.py`, `src/strategy/sample_futures.py`, `src/strategy/sampled_runtime_bridge.py`, `src/strategy/beam_report.py`, `scripts/generate_strategy_report_from_sampled_runtime.py`, related tests under tests/unit/strategy, strategy fixtures under tests/fixtures/strategy`  
**Specific exclusions:** Do not import `src.evo_predictor` from strategy; do not keep `max_futures` compatibility; do not change scoring semantics beyond adapting index futures to driver IDs at the boundary.

**Close criteria:**
- [ ] `ClassificationFutureSet` supports only schema v2 with integer driver-index futures.
- [ ] Validator fails fast for non-integer futures, duplicate indices, out-of-range indices, wrong row length, non-`uint8` representability where applicable.
- [ ] Adapter converts `final_order_samples` to full index permutations with no truncation argument.
- [ ] Strategy scoring/report paths consume v2 futures correctly and do not expose `max_futures` or truncation metadata.
- [ ] Strategy fixtures/tests are migrated to v2.
- [ ] Implementation and review evidence integrated.

**Required evidence:**
- TDD tests showing v1 rejection and v2 acceptance/round-trip.
- Focused strategy tests pass.
- Reviewer verifies no strategy direct evo runtime imports and no truncation compatibility path.

**Required verification commands:**

```bash
py -m pytest tests/unit/strategy/test_classification_futures.py tests/unit/strategy/test_sample_futures.py tests/unit/strategy/test_sampled_runtime_bridge.py tests/unit/strategy/test_strategy_report_from_sampled_runtime.py tests/unit/strategy/test_fantasy_future_scoring.py tests/unit/strategy/test_fantasy_beam_search.py -v
```

**Stop conditions:** hidden compatibility requirement appears; report generation requires generated artifact edits; strategy would need to import evo internals.  
**Next gate:** Gate 2.

### Gate 2: Sampled Runtime `FinalOrderSampleSet` v2 And Stage Snapshots

**Purpose:** Add production runtime versioning and typed per-stage traceability snapshots while keeping probability metadata on the evo side.  
**Crew cycle:** `implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close`  
**Implementer handoff:** `required`  
**Reviewer handoff:** `required`  
**Suggested model tier:** `stronger broad/ambiguous, because runtime contracts and diagnostics touch multiple evo tests`  
**Test mode:** `TDD required`  
**Allowed scope:** `src/evo_predictor/runtime_contracts.py`, `src/evo_predictor/sample_state_adapter.py`, `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/sampled_runtime_serialization.py`, direct `FinalOrderSampleSet` callers in `src/evo_predictor/sampled_backtest.py` and `src/evo_predictor/run.py` if required by tests, related tests under `tests/unit/evo_predictor`  
**Specific exclusions:** Do not change sampling math or module training behavior; do not add DNF/DNS sampled status fields; do not emit bulky new committed artifacts.

**Close criteria:**
- [ ] `FinalOrderSampleSet` has required `schema_version` with current value `2`.
- [ ] `StageSnapshot` is typed and validates position distribution, pairwise matrix, ESS, position-distribution stability, and pairwise flip rate.
- [ ] `stage_snapshots: dict[str, StageSnapshot]` exists on `FinalOrderSampleSet`; top-level and stage snapshot invariants are tested.
- [ ] `stage_diagnostics` remains an opaque provenance dict.
- [ ] Serialization emits `schema_version` and `stage_snapshots` as JSON-native values.
- [ ] Sampled runtime populates snapshots for `quali`, `race_start`, and `race` from available ordering samples.
- [ ] Implementation and review evidence integrated.

**Required evidence:**
- TDD tests for `StageSnapshot` validation and serialization.
- Focused evo tests pass.
- Reviewer verifies no sampling/model semantic drift.

**Required verification commands:**

```bash
py -m pytest tests/unit/evo_predictor/test_runtime_contracts.py tests/unit/evo_predictor/test_sample_state_adapter.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/evo_predictor/test_sampled_runtime_serialization.py -v
py -m pytest tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_predict_cli.py -v
```

**Stop conditions:** diagnostics formulas require a modeling decision beyond issue comments; runtime snapshots require changing sample generation semantics; verification cannot distinguish traceability-only changes from model output changes.  
**Next gate:** Gate 3.

### Gate 3: Durable Docs, Report Schemas, And Region Verification

**Purpose:** Promote the new contract into docs/report schema truth and run final cross-region verification.  
**Crew cycle:** `implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close`  
**Implementer handoff:** `required`  
**Reviewer handoff:** `required`  
**Suggested model tier:** `simple bounded, because this is docs/schema cleanup plus verification`  
**Test mode:** `test-after allowed; docs inspection plus region suites`  
**Allowed scope:** `docs/evo/sampled_runtime_strategy_contract.md`, `docs/report_schemas/strategy_reports.md`, `docs/report_schemas/README.md`, any docs directly contradicted by Gates 1-2, final test evidence files under `.agent-work/issue-186-monte-carlo-contract/evidence/`  
**Specific exclusions:** Do not create new future-looking docs outside the issue scope; do not update architecture map unless implementation changed structural relationships.

**Close criteria:**
- [ ] Docs describe `ClassificationFutureSet` v2, `FinalOrderSampleSet` v2, stage snapshots, no truncation, fixture vs production artifact distinction, and strategy/evo boundary.
- [ ] Stale `DNF_POSITION = 30` contract language and `max_futures` schema language are removed or reframed.
- [ ] Full affected region suites are run or failures documented.
- [ ] Architecture reconciliation decision recorded.
- [ ] Implementation and review evidence integrated.

**Required evidence:**
- Focused docs inspection notes.
- Region verification commands.
- Reviewer verifies docs do not contradict code/tests.

**Required verification commands:**

```bash
py -m pytest tests/unit/evo_predictor/ -v
py -m pytest tests/unit/ -v
```

**Stop conditions:** region suite reveals unrelated existing failures; docs require a new architecture decision; generated reports must be regenerated rather than docs updated.  
**Next gate:** closeout.

## Triage Candidate Log

| Candidate | Reason | Anchor | Evidence | Status |
|---|---|---|---|---|
| none | none | none | none | noted |

## Plan-Level Stop Conditions

- unresolved human decision affects scope, authority, or evidence
- required evidence cannot be produced
- scope expands beyond allowed regions/files
- a specific exclusion must be touched
- structural uncertainty affects ownership, dependency, scope, or evidence

## Final Completion Criteria

- [ ] all gates closed or remaining blockers listed
- [ ] each implementation gate completed its Crew cycle; do not batch review at final closeout
- [ ] evidence satisfies close criteria; reviewer approval alone is insufficient
- [ ] assumptions still hold
- [ ] architecture reconciliation checked
- [ ] Triage candidates routed, dropped because `none`, or none
