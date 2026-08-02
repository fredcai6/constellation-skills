# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`tc1 — track_status explicit missingness (Admiral cleanup ruling)`

## Completed slice
`FpLapLatent.track_status` is now typed `Optional[str]`; `extract_fp_lap_latent` sets `None` (not `""`) when
`lap_times.track_status` is NULL, mirroring the existing `tyre_life: Optional[int]` convention in the same
module (same `pd.notna(...)` idiom).

## Scope
**Files changed:**
- `src/physics/layer2/fp_lap_latent.py`
- `tests/unit/physics/test_fp_lap_latent.py`

**Specific exclusions touched:** no — no other file touched, no downstream numeric/string use of
`track_status` exists in this module beyond straight carry-through (confirmed by read), so no policy point
needed changing.

## Behavior changed
`yes` — `FpLapLatent.track_status` for a row with NULL `lap_times.track_status` now surfaces as `None`
instead of the empty string `""`. Rows with a real `track_status` value are unaffected (still the same
string). No change to `run_purpose`, `fuel_kg_est`, `mass_kg`, or any other field.

## Map Impact
Trivial local edit (one field's missingness sentinel, mirroring an established in-module convention) — no
structural, capability, constraint, or decision impact. Skipping the rest of this section per the skill's
own conditional-skip instruction.

## Test mode
**Required:** `test-first (TDD RED-first)`
**Satisfied:** `yes` — RED observed before the fix, GREEN after.

## Evidence

```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/test_fp_lap_latent.py -q
```
**Result:** `pass` — 52 passed (was 51 passed, 1 failed pre-fix; the 1 new test added).

```bash
cd /c/Programs/f1-513 && py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/fp_lap_latent.py
```
**Result:** `pass` — `PASS (1 files checked)`

```bash
cd /c/Programs/f1-513 && git status --short data/
```
**Result:** `pass` — empty output, `data/` tree clean throughout (synthetic `tmp_path` sqlite fixture only,
no `data/*.db` touched).

## TDD evidence, if required

- Failing test observed: extended `_build_fixture_db_null_tyre_life` so lap 2 also carries a NULL
  `track_status`, then added `test_null_track_status_yields_none_not_empty_string`. Pre-fix run:
  `51 passed, 1 failed` — `AssertionError: assert '' is None` (`track_status=''` from the old `else ""`
  sentinel at the pre-edit `fp_lap_latent.py:368`).
- Passing test observed: post-fix run: `52 passed` (full `tests/unit/physics/test_fp_lap_latent.py`).
- Refactor while green: `no` — change was already minimal (type annotation + docstring line + one
  conditional-expression swap); no further refactor needed.

## Docs/contracts touched
- `src/physics/layer2/fp_lap_latent.py` docstring for `FpLapLatent.track_status` updated in place to state
  the `None`-on-NULL convention (mirrors the existing `tyre_life` docstring language). No external
  doc/contract file references this field.

## Assumptions
- None — the handoff's authority section marked the fix DECIDED (Admiral cleanup ruling), so no design
  choice was made beyond the exact mirror-tyre_life mechanics named in the handoff.

## Stop conditions hit
- None.

## Out-of-scope observations
- None found — grepped for other `track_status` consumers of this module's `FpLapLatent` output; none exist
  yet (module is still #513 g2 in isolation), so there is no downstream call site that could be affected by
  the `""` -> `None` change.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: task, intent, scope, exclusions, evidence, test mode,
  stop conditions, verification commands, and authority were all present and unambiguous; the handoff's own
  worked example (mirror `tyre_life`) was directly copy-able as the extraction-line pattern
  (`pd.notna(row["tyre_life"]) else None` -> `pd.notna(row["track_status"]) else None`).
- **Context rediscovered:** none — the tyre_life mirror target (dataclass field, docstring, extraction line)
  was exactly where the handoff said it would be.
- **Instructions improvised around:** none.
- **What would have made this easier:** none — this handoff was already minimal and precise; nothing to
  improve.

## Return status
`complete`
