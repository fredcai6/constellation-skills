# Reviewer Handoff — g6-finalize-review

## Gate
g6-finalize-review (#668 instrument panel). Worktree `C:/Programs/f1brainz-wt/epic659-668`,
branch `epic659/668-instrument-panel`. PINNED interpreter
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Survey State Location
`.agent-work/668-instrument-panel/g6-finalize-review/review.json`.

## What Was Implemented
Finalized the OWNER-SIGNED `REPLICATION_*` frozen set in `src/physics/layer2/frozen_constants.py`,
wired `replication.py` to consume it via `frozen_replication_thresholds()`, and added refinement 2
(main-effect estimation uncertainty into the σ-honesty margin + thin-class surfacing). Result:
`.agent-work/668-instrument-panel/crew-results/g6-finalize-implement-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree. `git status --porcelain` then `git diff`. NOTE: `data/f1_data_2023.db`
must NOT appear modified (a prior test WAL-touched it and was restored — confirm it is clean).

## Close Criteria (each a check — reproduce)
- **Signed values are EXACT** (an owner signature): `REPLICATION_MIN_SUPPORT_N=15.0`,
  `REPLICATION_THRESHOLD=0.5`, `REPLICATION_R_FLOOR_CAP=0.7`, `REPLICATION_R_FLOOR_SUPPORT_REF=100.0`,
  `REPLICATION_CHANNEL_TIE_MARGIN=0.1`. Any deviation = BLOCK.
- **Consume-not-remint**: `replication.py`'s `frozen_replication_thresholds()` IMPORTS the frozen
  constants (no re-minted literals). Confirm the r_floor formula matches
  `threshold + (cap−threshold)*clip((ref−n)/ref,0,1)`.
- **Refinement 2 correct**: the σ-honesty margin quadrature-adds the SE of the removed driver+class
  main effects to the cell σ BEFORE `predictive_t` (stays OUT-OF-SAMPLE + Student-t); a thin class
  (below MIN_SUPPORT_N to center) is SURFACED/flagged, not silently dropped. Confirm the widening
  raises coverage (not spuriously over-claims) and that `margin=None` is a clean no-op.
- **No fitted interaction term** introduced (double-centering stays a data transform).
- **frozen_constants append is clean**: `git diff src/physics/layer2/frozen_constants.py` = the
  DEFERRED-note replacement + the append only; no unrelated edits; discipline note present.
- pyright-0 on both edited modules; the FULL `tests/unit/physics/instrument_panel/` suite green
  (49 tests) on the pinned interpreter — reproduce. `data/` clean in `git status`.

## Allowed Scope
`src/physics/layer2/frozen_constants.py`, `src/physics/instrument_panel/replication.py`,
`tests/unit/physics/instrument_panel/test_replication_frozen_constants.py`, `test_replication_channel.py`.

## Specific Exclusions
No signed-value change; no re-minted SECTOR_CALIB_*/FINGERPRINT_* constants; no producer edits
beyond the frozen_constants append; no fitted interaction term; no `data/` commit.

## Constraints the Implementation Must Respect
Exact signed values; consume-not-remint; OOS Student-t σ-honesty; no-frame-kill thin-class surfacing.

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/frozen_constants.py`; `src/physics/instrument_panel/replication.py`.
- **Decision anchors:** decision:replication-deferred — finalized with owner-signed values.
  `@grade: settled/human · leans g6`

## Evidence Produced
49/49 tests + pyright-0. Reproduce:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/ -q`.
Your APPROVE feeds `g6-finalize-integrate.c1` (test_replication_frozen_constants.py) + `.c2` (verdict).

## Suggested Model Tier
stronger — owner-signature exactness + the σ-honesty margin math.

## Stop Conditions
BLOCK if: any signed value deviates; a literal is re-minted; the margin widening is in-sample or
Gaussian; a thin class is silently dropped; a fitted interaction term appears; `data/` is dirty;
or tests don't reproduce.

## Return Format
Return REVIEW_RESULT (APPROVE/BLOCK + findings + workflow feedback). WRITE it to
`.agent-work/668-instrument-panel/crew-results/g6-finalize-review-result.md` before ending your turn.
