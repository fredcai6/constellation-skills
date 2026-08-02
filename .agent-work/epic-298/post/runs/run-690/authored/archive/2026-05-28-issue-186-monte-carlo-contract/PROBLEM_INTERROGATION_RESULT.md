# Problem Interrogation Result

## User Request

Use `constellation-pilot` on GitHub issue #186 and implement the Monte Carlo result contract decisions now.

## Interpreted Intent

Turn the issue #186 design decisions into current repo truth: code contracts, serialization, strategy adapter/scoring behavior, fixtures/tests, and durable documentation.

## Intent Protected

Sampled evo runtime remains the owner of production Monte Carlo race-result semantics. Strategy/fantasy consumes a narrow, validated `ClassificationFutureSet` contract and does not import or depend on evo runtime internals.

## Resolved Ambiguities

- Implementation depth: implement everything now. Authority: user answer.
- Strategy boundary: strategy consumes `ClassificationFutureSet` only, not raw `FinalOrderSampleSet`. Authority: issue comments.
- Futures representation: `ClassificationFutureSet` v2 uses integer driver-index permutations over `driver_ids`; JSON wire format emits int lists. Authority: issue comments.
- Traceability: sampled runtime keeps probability metadata; `FinalOrderSampleSet` gains `schema_version` and typed `stage_snapshots`. Authority: issue comments.
- Artifact sizing: no truncation feature; full sample set crosses the boundary; compact fixtures remain explicitly fixture-only. Authority: issue comments.
- Entrants/DNF/DNS: variable field size handled by permutations; DNF is classified position, DNS out of scope. Authority: issue comments.

## Remaining Ambiguity

`none`

## Scope

Allowed implementation scope:

- `src/strategy/classification_futures.py`
- `src/strategy/sample_futures.py`
- `src/strategy/sampled_runtime_bridge.py`
- strategy scoring/report generation call sites that consume `ClassificationFutureSet`
- `src/evo_predictor/runtime_contracts.py`
- `src/evo_predictor/sample_state_adapter.py`
- `src/evo_predictor/sampled_runtime.py`
- `src/evo_predictor/sampled_runtime_serialization.py`
- directly related tests/fixtures under `tests/unit/strategy`, `tests/unit/evo_predictor`, and `tests/fixtures/strategy`
- durable docs under `docs/evo/` and `docs/report_schemas/`

## Not Scope

- Training, model quality, or prediction-calibration changes.
- Gold-cycle artifact promotion or real-data reruns.
- FastF1/data-ingestion changes.
- Push, PR, merge, or issue close without explicit user approval.

## Specific Exclusions

- Do not manually edit generated gold outputs or bulky runtime artifacts.
- Do not preserve v1 backwards compatibility unless needed by a committed fixture migration gate.
- Do not add direct strategy imports of evo runtime contracts.

## Success Evidence

- Focused strategy tests pass for `ClassificationFutureSet`, sampled-runtime bridge, sample futures, fantasy scoring/report paths.
- Focused evo tests pass for runtime contracts, sample state adapter, sampled runtime, and serialization.
- Broader region evidence is run before closeout because this crosses evo and strategy/data-layer regions.
- Docs/report schemas describe v2 futures, `FinalOrderSampleSet` versioning, stage snapshots, no truncation, and fixture-vs-production distinction.

## Assumptions

| Assumption | Authority | Risk |
|---|---|---|
| Existing branch `codex/issue-186-mc-contract` is the task branch. | Pilot-created branch and user continued work. | low reversible |
| Current architecture map is sufficient baseline; no Cartographer baseline needed unless implementation changes structural boundaries. | `docs/architecture/index.md` verified 2026-05-26. | low reversible |

## Structural Baseline Need

`no`

## Constellation Value Decision

`use Constellation`

**Reason:** The change spans a contract boundary between evo and strategy, needs TDD, documentation updates, and independent implementer/reviewer gates.

## Recommended Next Action

`create gated plan`

## Rejected Alternatives

- `Spec only`: rejected by explicit user answer to implement everything now.
- Direct strategy consumption of `FinalOrderSampleSet`: rejected by issue decision and boundary intent.
- Truncation config or `max_futures`: rejected by issue decision.

## Stop Conditions Before Planning

`none`
