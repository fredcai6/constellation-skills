# Interrogator Questions: Issue 186 Monte Carlo Contract

Required by `constellation-pilot` Step 1. Question statuses: `open`, `answered`, `answered-by-repo`, `deferred`, `blocked`.

## Context Inspected

- User request: `[$constellation-pilot] issue 186`
- GitHub issue #186 and its two design-decision comments.
- `docs/AGENT_GUIDE.md`
- `docs/agents/ORCHESTRATOR_CONTEXT.md`
- `docs/agents/CREW_CONTEXT.md`
- `docs/agents/GLOSSARY.md`
- `README.md`
- `TESTING.md`
- `docs/architecture/index.md`
- `docs/DOCUMENTATION.md`
- `docs/evo/sampled_runtime_strategy_contract.md`
- Current contract/code hits in `src/evo_predictor/runtime_contracts.py`, `src/evo_predictor/sample_state_adapter.py`, `src/evo_predictor/sampled_runtime_serialization.py`, `src/strategy/classification_futures.py`, `src/strategy/sample_futures.py`, `src/strategy/sampled_runtime_bridge.py`, and related tests.

## Problem Statement Draft

Issue #186 asks for the long-term Monte Carlo sampled-race result contract between sampled evo runtime and downstream strategy/fantasy layers. Existing docs and code still reflect a v1 strategy adapter that converts final-order samples to string ordered classifications, can truncate emitted futures via `max_futures`, and treats `FinalOrderSampleSet` as unversioned. Issue comments record newer decisions: strategy should consume only `ClassificationFutureSet`; strategy should not import evo runtime internals; futures should become index-keyed v2 arrays over `driver_ids`; no truncation feature; `FinalOrderSampleSet` should gain `schema_version`; traceability should live in typed `stage_snapshots`.

## Question List

### Q1: Implementation depth for issue #186

**Status:** `answered`  
**Question:** Should this issue implement the recorded contract decisions now, or should it stop at a durable spec plus migration issues?  
**Why it matters:** The acceptance criteria can be satisfied by documentation and a migration plan, but issue comments contain enough concrete decisions to justify code changes across `src/evo_predictor` and `src/strategy`. Those paths have different verification cost and blast radius.  
**Possible answers:**
- `Implement now`: update contracts, adapter, serializer, fixtures/tests, and docs in this issue.
- `Spec only`: update durable docs/report schemas and create issue-ready follow-up gates for implementation.
- `Hybrid`: implement the low-risk strategy v2 adapter now, defer sampled-runtime `StageSnapshot` diagnostics if too broad.
**Recommendation:** `Implement now`, but gate it into independently reviewed slices because the comments appear to be final decisions and backwards compatibility is not a major concern in this repo.
**Answer:** `Implement everything now.`
**Follow-ups:** Build a gated implementation plan covering strategy v2 futures, sampled-runtime versioning/stage snapshots, docs/report schemas, fixtures/tests, and migration cleanup.

### Q2: Strategy boundary

**Status:** `answered-by-repo`  
**Question:** Should strategy consume raw `FinalOrderSampleSet`, normalized `ClassificationFutureSet`, or both?  
**Answer:** Strategy consumes `ClassificationFutureSet` only; `FinalOrderSampleSet` and evo internals remain on the evo side of the adapter.  
**Authority:** Issue comment `4551453397`; current docs already say strategy should use a decoupled adapter output.
**Follow-ups:** Ensure code/docs do not require direct evo imports from strategy.

### Q3: Futures representation

**Status:** `answered-by-repo`  
**Question:** Should sampled futures be represented as per-driver sampled positions or ordered classification lists?  
**Answer:** `ClassificationFutureSet` v2 should use a numpy `uint8` array of shape `(N_futures, N_drivers)` where each entry is a zero-based index into `driver_ids`; JSON wire format emits int lists.  
**Authority:** Issue comment `4551453397`.
**Follow-ups:** Migration requires validator/serializer/scoring path updates if implementation proceeds.

### Q4: Probability metadata crossing boundary

**Status:** `answered-by-repo`  
**Question:** How should position distributions and pairwise matrices be preserved?  
**Answer:** They stay in sampled-runtime production artifacts, not strategy futures. Add typed `stage_snapshots: dict[str, StageSnapshot]` on `FinalOrderSampleSet`; keep `stage_diagnostics` as opaque provenance.  
**Authority:** Issue comments `4551453397` and `4551518263`.
**Follow-ups:** Define `StageSnapshot` fields and serialization if implementation proceeds.

### Q5: Variable entrant count, DNFs, DNS, and non-classified entrants

**Status:** `answered-by-repo`  
**Question:** How should downstream strategy handle variable fields, reserve drivers, DNFs, and non-classified entrants?  
**Answer:** Variable field size is handled by the permutation model over entered drivers. DNFs receive official classified positions and need no contract sentinel. DNS is out of scope and not predicted.  
**Authority:** Issue comments `4551453397` and `4551518263`.
**Follow-ups:** Remove/update stale docs that still describe `DNF_POSITION = 30` as a contract concept if implementation proceeds.

### Q6: Traceability canonical source

**Status:** `answered-by-repo`  
**Question:** What is canonical for traceability: raw samples, summary distributions, or both?  
**Answer:** Both raw samples and summary distributions are canonical in sampled runtime; strategy receives only the narrow adapter output.  
**Authority:** Existing `docs/evo/sampled_runtime_strategy_contract.md` plus issue comments.
**Follow-ups:** Update docs to reflect `schema_version` and stage snapshots.

### Q7: Artifact sizing

**Status:** `answered-by-repo`  
**Question:** Should artifacts use full 1000+ futures, compact representative fixtures, or truncation config?  
**Answer:** No truncation feature. Full sample set crosses the boundary; downstream consumers decide what to use. Compact committed fixtures remain fixtures, not production evidence.  
**Authority:** Issue comment `4551518263`.
**Follow-ups:** Remove `max_futures` API/metadata if implementation proceeds.

## Question Loop State

**Highest-value remaining question:** `none`  
**Next action:** Write `PROBLEM_INTERROGATION_RESULT.md`, then build the gated plan and consistency check.
