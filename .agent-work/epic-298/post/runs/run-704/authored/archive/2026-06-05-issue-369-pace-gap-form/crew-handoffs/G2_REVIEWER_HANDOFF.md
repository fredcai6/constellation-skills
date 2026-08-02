# Reviewer Handoff

## Gate
g2 — adapter pace-gap encoding (issue #369, work area `.agent-work/issue-369-pace-gap-form/`)

## What Was Implemented
Flag-gated `quali_pace_gap` form encoding in the quali recent-history adapters: `DriverFeatures.quali_pace_gap_history_full` field; `RecentHistoryFeatureConfig.form_encoding` (default `position_quality`, validated set); v2 encoding path in `quali_recent_history_adapter.py` (encoding-strategy dispatch `_resolve_encoding_fns` + shared helpers `_build_pairs`/`_make_pair_batch`/`_h2h_support_summary`); constructor mirror with `min(gap)` pooling in `constructor_quali_recent_history_adapter.py`; new v2 schema constants (v1 untouched); `form_encoding` recorded in diagnostics; 17 new tests. The driver quali adapter was substantially restructured (refactor-while-green) to keep CC within limits.

## How to Inspect the Diff
Uncommitted working tree on branch `constellation/issue-369-pace-gap-form` (G1 is the committed HEAD 4b71cd2):
```bash
git -C C:\Programs\f1Brainz status
git -C C:\Programs\f1Brainz diff
```
Touched: `src/evo_predictor/models/_features.py`, `src/evo_predictor/recent_history_adapter.py`, `src/evo_predictor/quali_recent_history_adapter.py`, `src/evo_predictor/constructor_quali_recent_history_adapter.py`, `tests/unit/evo_predictor/test_quali_recent_history_adapter.py`, `tests/unit/evo_predictor/test_constructor_quali_recent_history_adapter.py`.

## Task Statement
Full implementer handoff (frozen orientation table, naming rules, identity requirement): `.agent-work/issue-369-pace-gap-form/crew-handoffs/G2_IMPLEMENTER_HANDOFF.md`.

## Close Criteria
**Primary — default-off bit-identity (the protected intent):**
- v1 path produces identical feature names, vectors, and schema string as before the diff. The strongest proof: every pre-existing test passes UNMODIFIED. Inspect the test-file diffs specifically for any edited existing assertion (only an exact-diagnostics-dict pin was permitted to be extended, nothing else). If any existing assertion was weakened or changed → BLOCK.
- The restructure of `quali_recent_history_adapter.py` is the riskiest part: verify by reading the diff that the v1 computation path (quality mapping, neutral (0.5,0.5,0.0), forgiveness keeping highest qualities, h2h clamped positions) survived the refactor exactly.

**Orientation correctness (v2):**
- Raw gaps, lower=better; NO `_position_to_quality`, NO dnf clamp anywhere on the gap path.
- Empty-window neutral `(0.0, 0.0, 0.0)`.
- Forgiveness drops HIGHEST gaps.
- h2h: edge `lg < rg`, magnitude `rg − lg` raw, overlap only where both non-nan.
- Availability/recency machinery unchanged, driven by gap missingness.

**Schema/naming consistency:**
- `driver_quali_power_from_recent_history.v2` / `constructor_quali_power_from_recent_history.v2`; v1 constants untouched.
- Window stats renamed `quali_pace_gap_{mean,median,std}_*`; h2h magnitudes carry a non-colliding `quali_pace_gap`+`h2h` token; availability/`head_to_head_quali_edge`/recency names unchanged.
- No name collisions within v2; v1 names completely unchanged.

**Loud failure:** encoding on + `quali_pace_gap_history_full is None` → ValueError naming the field (both adapters); invalid `form_encoding` → ValueError naming field+value. No silent fallback path exists.

**Constructor pooling mirror:** v1 pools positions per event by min; v2 pools gaps by min — verify the v1 rule actually IS min(position) in the pre-diff code, and that all-drivers-nan → missing event.

**Test quality:** the 17 new tests pin the above with hand-computed values, not self-referential assertions.

## Allowed Scope
The six files listed above. `tests/unit/evo_predictor/test_recent_history_adapter.py` was allowed but reported untouched — confirm.

## Specific Exclusions
`module_adapters/`, `data_adapter/`, `run.py`, `configs/`, docs, race/race-start adapters' behavior, `src/latent_power/`, `quali_pace_gap_history.py`. Flag if touched. (`recent_history_adapter.py` was allowed ONLY for the config field + validation — verify the race-path functions in that file are behavior-identical.)

## Constraints the Implementation Must Respect
- Adapters stay pure feature consumers: no DB access, no import of `quali_pace_gap_history` into adapters.
- `py` not `python`; pyright-clean on changed files.
- Simplification limits: PASS required on touched files EXCEPT the known pre-existing violations in `recent_history_adapter.py:build_driver_recent_history_pair_batch` (cc=30, lines=143) — commander verified these baseline-identical via stash round-trip; they are NOT a block for this gate (triaged as tc2). Any NEW violation introduced by the diff → BLOCK.

## Evidence Produced
From IMPLEMENTER_RESULT (status complete, TDD failing-first observed — ImportError on v2 constants):
- targeted 3-file pytest: 35 passed in 0.24s
- `py -m pytest tests/unit/evo_predictor -q`: 1237 passed
- limits: PASS (5 files) excluding the pre-existing race-fn violations (commander re-verified)

Re-run the pytest commands yourself; do not take the transcript on faith.

## Suggested Model Tier
stronger-leaning bounded — bit-identity through a structural refactor is subtle; read the diff line by line for the v1 path.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
