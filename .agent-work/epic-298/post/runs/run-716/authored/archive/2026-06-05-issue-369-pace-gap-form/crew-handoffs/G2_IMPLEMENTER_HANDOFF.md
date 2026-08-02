# Implementer Handoff

## Gate
g2 — adapter pace-gap encoding (issue #369, work area `.agent-work/issue-369-pace-gap-form/`)

## Task
Add the flag-gated `quali_pace_gap` form encoding to the two quali recent-history adapters. G1 (already merged on this branch) provides `src/evo_predictor/quali_pace_gap_history.py`; this gate makes the adapters able to consume its output. NO plumbing (builders/CLI/config files) — that is G3.

**(a) `src/evo_predictor/models/_features.py`** — `DriverFeatures` gains one field:
```python
quali_pace_gap_history_full: list | None = None
```
(typed like its sibling `quali_history_full`; default None = not populated; re-export untouched — it's a dataclass field, not a new symbol.)

**(b) `src/evo_predictor/recent_history_adapter.py`** — `RecentHistoryFeatureConfig` gains:
```python
form_encoding: str = "position_quality"
```
validated (in `__post_init__` or the existing validation seam — follow file convention) to be in `{"position_quality", "quali_pace_gap"}`; invalid → ValueError naming the field and value. The race adapter in this file must NOT change behavior — it ignores the new field (race adapters never receive `quali_pace_gap`; do not add handling there).

**(c) `src/evo_predictor/quali_recent_history_adapter.py`** — the driver quali adapter (entry `build_driver_quali_recent_history_pair_batch`, line 74; `_history_vector(positions, config)` line 136; v1 schema constant line 27). Under `config.form_encoding == "quali_pace_gap"`:

- **Source series**: `DriverFeatures.quali_pace_gap_history_full` (raw gaps, `nan` = missing) instead of `quali_history_full` positions. If the field is `None` for any driver while encoding is `quali_pace_gap`, raise `ValueError` naming `quali_pace_gap_history_full` and the driver — no silent fallback to positions, ever.
- **No quality mapping**: gaps are used raw (no `_position_to_quality`, no dnf clamp anywhere on the gap path). Lower = better (mirrors position polarity).

Orientation table — exact required semantics per machinery piece:

| Machinery | v1 position_quality | v2 quali_pace_gap |
|---|---|---|
| per-event value | `_position_to_quality(pos, dnf)` ∈ [0,1], higher=better | raw gap, lower=better, nan=missing |
| empty-window neutral | `(0.5, 0.5, 0.0)` | `(0.0, 0.0, 0.0)` (0.0 = at field median) |
| forgiveness (drop worst m) | keeps highest qualities | drops HIGHEST gaps (worst = slowest), keeps lowest |
| h2h edge | `lp < rp` over clamped positions | `lg < rg` over raw gaps (faster wins); NO `min(value, dnf_position)` clamp |
| h2h gap magnitude | `rp − lp` position diff | `rg − lg` gap diff, raw |
| h2h overlap eligibility | both positions present | both gaps non-nan |
| availability / recency | over position missingness | same machinery over gap missingness |

- **Feature names**: every value-bearing name changes so v1/v2 vectors are never confusable: window stats `quali_classification_quality_{mean,median,std}_*` → `quali_pace_gap_{mean,median,std}_*`; h2h magnitude `mean/median_quali_classification_gap_*` → a `quali_pace_gap`-bearing name that does NOT collide with the window-stat names (pick a clear token, e.g. `..._h2h_...`, and use it consistently). Pure-presence names stay unchanged: `availability_fraction_n{n}_delta`, `head_to_head_quali_edge_n{n}`, recency features (they measure presence/ordinal edge, not the form value).
- **Schema**: `feature_schema_version` becomes `"driver_quali_power_from_recent_history.v2"` (new constant alongside the v1 constant; v1 constant unchanged).
- **Diagnostics**: record `form_encoding` in the diagnostics dict for BOTH encodings (this is additive to v1 diagnostics — diagnostics are not part of the feature-vector bit-identity guarantee, but if any existing test pins the exact diagnostics dict, extend the expectation rather than weakening the test).

**(d) `src/evo_predictor/constructor_quali_recent_history_adapter.py`** — already imports `_history_vector`/`_pairwise_features` from the driver adapter (line 12), so the v2 vector path is shared. What this file owns: pooling driver series into constructor series. Mirror the existing position-pooling rule for gaps, oriented lower=better (read the current pooling code first; e.g. if v1 pools by best/min position per event, v2 pools by min gap per event; if v1 pools differently, mirror that rule's spirit and document the choice in your result). Missing pooling: a constructor-event is missing only when ALL its drivers' gaps are nan that event. Schema constant `"constructor_quali_power_from_recent_history.v2"` (v1 constant at line 24 unchanged). Same ValueError-on-absent-field, same diagnostics `form_encoding`.

**(e) Tests** — extend `tests/unit/evo_predictor/test_quali_recent_history_adapter.py` and `test_constructor_quali_recent_history_adapter.py`:
- v2 names + schema string emitted under the flag (window, h2h, availability names asserted).
- Neutral `(0.0,0.0,0.0)` for an all-missing window.
- Forgiveness orientation: with known gaps, dropping m=1 removes the HIGHEST gap.
- h2h: edge and gap-diff values over a small hand-computed pair; nan rounds excluded from overlaps; no dnf clamping (use a gap large enough that a clamp would corrupt it if wrongly applied — e.g. gap > dnf would be absurd; instead prove clamp absence by asserting exact arithmetic on raw values).
- Loud failure: encoding on + field None → ValueError naming the field.
- Invalid `form_encoding` value → ValueError.
- **EXPLICIT default-off identity**: same DriverFeatures inputs through (i) default config and (ii) `form_encoding="position_quality"` → identical feature_names, identical vectors (`np.array_equal`), v1 schema string. Plus all existing tests pass UNMODIFIED (do not edit any existing assertion except, if strictly needed, an exact-diagnostics-dict pin per (c)).
- Constructor pooling: gap pooling rule pinned with hand-computed values; all-driver-missing event → missing.

## Protected Intent
- **Default off = bit-identical v1 features.** Existing tests must pass without modification; that is the proof the default path didn't move.
- No silent fallback between encodings: absent field under `quali_pace_gap` fails loudly.
- Adapters stay pure feature consumers — no DB access, no imports from `quali_pace_gap_history.py` (G3 wires the data in via DriverFeatures).

## Test Mode
TDD required — logic on the promoted prediction path.

## Close Criteria
- `py -m pytest tests/unit/evo_predictor/test_quali_recent_history_adapter.py tests/unit/evo_predictor/test_constructor_quali_recent_history_adapter.py tests/unit/evo_predictor/test_recent_history_adapter.py -q` green.
- `py -m pytest tests/unit/evo_predictor -q` green (no collateral damage in the region).
- `py -m src.utils.simplification_limits --paths <every touched file>` PASS.
- Orientation table above implemented exactly; identity test present and meaningful.

## Allowed Scope
- `src/evo_predictor/models/_features.py` (one field)
- `src/evo_predictor/recent_history_adapter.py` (config field + validation only)
- `src/evo_predictor/quali_recent_history_adapter.py`
- `src/evo_predictor/constructor_quali_recent_history_adapter.py`
- `tests/unit/evo_predictor/test_quali_recent_history_adapter.py`
- `tests/unit/evo_predictor/test_constructor_quali_recent_history_adapter.py`
- `tests/unit/evo_predictor/test_recent_history_adapter.py` (only if the config addition requires a new validation test there)

## Specific Exclusions
- `module_adapters/` (builders/closures — G3), `data_adapter/` (G3), `run.py` (G3), `configs/` (G3), docs (G3)
- Race / race-start adapters' behavior (`recent_history_adapter.py` race path, `race_start_recent_history_adapter.py`, `constructor_race_recent_history_adapter.py`)
- `src/latent_power/` entirely
- `quali_pace_gap_history.py` (frozen by G1)

## Constraints
- `py` not `python`; pyright-clean type hints; follow each file's existing style.
- DQI handling: reuse the existing DQI machinery unchanged (availability drives it the same way for both encodings).
- If a needed seam genuinely requires touching an excluded file, STOP and return.

## Required Evidence
- pytest output for the three test files and the full evo unit region.
- simplification_limits output.
- TDD failing-first note.
- One-paragraph note: the constructor gap-pooling rule chosen and why it mirrors the v1 position-pooling rule.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_quali_recent_history_adapter.py tests/unit/evo_predictor/test_constructor_quali_recent_history_adapter.py tests/unit/evo_predictor/test_recent_history_adapter.py -q
py -m pytest tests/unit/evo_predictor -q
py -m src.utils.simplification_limits --paths src/evo_predictor/models/_features.py src/evo_predictor/recent_history_adapter.py src/evo_predictor/quali_recent_history_adapter.py src/evo_predictor/constructor_quali_recent_history_adapter.py tests/unit/evo_predictor/test_quali_recent_history_adapter.py tests/unit/evo_predictor/test_constructor_quali_recent_history_adapter.py
```

## Suggested Model Tier
stronger-leaning bounded — orientation subtleties; mitigated by the exact table above.

## Authority
Human-confirmed problem statement: `.agent-work/issue-369-pace-gap-form/PROBLEM_STATEMENT.md`. The orientation table, neutral, schema strings, ValueError behavior, and identity requirement are frozen. You choose: exact h2h v2 feature-name token, internal helper structure, test naming, and the constructor pooling rule mirror (documented). You must NOT decide alone: any clipping/winsorizing, changing v1 behavior, changing race adapters, silent fallbacks.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required evidence cannot be produced, the existing pooling rule turns out to be ambiguous enough that mirroring it requires a design decision, or any existing test would need a non-diagnostics assertion change to stay green.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (verbatim tails), assumptions used, stop conditions hit, out-of-scope observations.
