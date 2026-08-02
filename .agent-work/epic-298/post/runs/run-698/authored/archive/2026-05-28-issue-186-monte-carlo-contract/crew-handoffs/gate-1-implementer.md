# Crew Handoff

## Role
`implementer`

## Assigned Gate
`Gate 1: Strategy ClassificationFutureSet v2`

## Suggested Model Tier
`simple bounded, because scope is localized but touches fixtures and report call sites`

## Test Mode
`TDD required`

## Task
Implement the strategy-facing `ClassificationFutureSet` v2 contract. Move futures from ordered driver-ID string rows to integer driver-index permutation rows over `driver_ids`, remove `max_futures` truncation semantics, and update strategy tests/fixtures/report paths in this gate scope.

## Intent Protected
Strategy/fantasy consumes a narrow strategy contract and does not import evo runtime internals. Sampled evo runtime production semantics stay outside strategy.

## Close Criteria
- `ClassificationFutureSet` supports only schema v2 with integer driver-index futures.
- Validator fails fast for non-integer futures, duplicate indices, out-of-range indices, wrong row length, and values not representable as `uint8`.
- Adapter converts `final_order_samples` to full index permutations with no truncation argument.
- Strategy scoring/report paths consume v2 futures correctly and do not expose `max_futures` or truncation metadata.
- Strategy fixtures/tests are migrated to v2.

## Authority
User answered: implement everything now. Issue comments define v2 index-future contract and no truncation feature. Backwards compatibility is not a major concern.

## Allowed Scope
`src/strategy/classification_futures.py`, `src/strategy/sample_futures.py`, `src/strategy/sampled_runtime_bridge.py`, `src/strategy/beam_report.py`, `scripts/generate_strategy_report_from_sampled_runtime.py`, related tests under `tests/unit/strategy`, strategy fixtures under `tests/fixtures/strategy`.

## Specific Exclusions
Do not import `src.evo_predictor` from strategy. Do not keep `max_futures` compatibility. Do not change evo runtime contracts in this gate. Do not manually edit generated reports under `reports/`.

## Relevant Project Rules For This Gate
- TDD for logic changes.
- Strict input validation at public boundaries; fail fast with clear field names and expectations.
- One canonical representation per concept at each boundary.
- Touch only what the gate requires.
- Use `py`, not `python`.

## Required Context
- `.agent-work/issue-186-monte-carlo-contract/GATED_PLAN.md`
- `.agent-work/issue-186-monte-carlo-contract/PROBLEM_INTERROGATION_RESULT.md`
- `docs/agents/CREW_CONTEXT.md`
- `src/strategy/classification_futures.py`
- `src/strategy/sample_futures.py`
- `src/strategy/sampled_runtime_bridge.py`
- `src/strategy/beam_report.py`

## Project Mechanics For This Gate
Do not commit, push, PR, or close the issue. Edit directly in the current workspace. You are not alone in the codebase; do not revert edits made by others, and accommodate any existing changes.

## Required Evidence
Diff summary, tests added/updated before implementation, verification command output summary, blockers if any, and explicit statement whether the strategy layer imports evo runtime internals.

## Required Verification Commands

```bash
py -m pytest tests/unit/strategy/test_classification_futures.py tests/unit/strategy/test_sample_futures.py tests/unit/strategy/test_sampled_runtime_bridge.py tests/unit/strategy/test_strategy_report_from_sampled_runtime.py tests/unit/strategy/test_fantasy_future_scoring.py tests/unit/strategy/test_fantasy_beam_search.py -v
```

## No-Test-Surface Rationale
Not applicable.

## Stop Conditions
Stop and return if allowed scope is exceeded, a specific exclusion must be touched, evidence cannot be produced, hidden intent would need inference, or an authority/dependency/failure policy decision is needed.

## Return Format
Diff summary, files changed, tests run with pass/fail result, blockers, scope concerns, assumptions used.
