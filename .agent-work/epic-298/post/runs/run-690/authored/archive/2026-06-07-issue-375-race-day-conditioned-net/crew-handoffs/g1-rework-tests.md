# Implementer Handoff — G1 REWORK: add unit tests (issue #375)

You are a constellation-implementer. Repo root and worktree:
`C:\Programs\f1Brainz\.claude\worktrees\agent-a2d028d13259581aa`. Windows; `py` not `python`;
set `PYTHONIOENCODING=utf-8` in every shell that captures subprocess output. Branch
`constellation/issue-375-race-day-conditioned-net`. Untracked files are real.

## Gate
g1 REWORK. A previous crew built `scripts/fusion_replay/g1_ordering_reconcile.py` and the G1 findings
section. The independent reviewer issued a BLOCK with exactly ONE blocker: the required unit tests were
not written. Everything else passed review. Your ENTIRE job is to add those tests. Do NOT change the
analysis script's behavior, do NOT touch the findings doc, do NOT regenerate records, do NOT add
production code.

## Task
Create `tests/unit/evo_predictor/test_g1_ordering_reconcile.py` with fast, self-contained unit tests
(no DB, no record files, no network — build tiny synthetic arrays inline) covering the NEW load-bearing
logic in `scripts/fusion_replay/g1_ordering_reconcile.py`:

1. **`_sign_acc_pooled` correctness.** Hand-built logits + y where you know the answer. E.g.
   logits=[+1,-1,+1,-1], y=[1,0,0,1] → 2/4 correct = 0.5. Include a case at 1.0 and a case at 0.0.
   Confirm the convention: prediction is `logits > 0`, compared to `y.astype(bool)`.

2. **`_sign_acc_per_event` correctness incl. `valid_mask`.** Two synthetic events with known per-event
   accuracies; assert the returned per-event array and unique_events. Add a case where `valid_mask`
   drops some pairs (the persistence path) and an event whose pairs are ALL masked out → that event's
   value must be NaN (assert with `np.isnan`).

3. **Persistence-logit derivation + missingness drop counting.** This is the core G1 logic. Rather than
   call `build_g1_dataset` (which needs records+DB), test the persistence logic directly by replicating
   the documented rule on a tiny example OR by extracting it if cheaply testable. The rule (from the
   script docstring, lines ~14-19 and ~181-192):
     - `persist_logit = prior_pos_j - prior_pos_i` for pair (i,j), i<j.
     - `persist_valid = ~(isnan(prior_i) | isnan(prior_j)) & (prior_i != prior_j)`.
     - dropped count = number of invalid pairs.
   Build a small `prior_pos` dict (e.g. {"A":1,"B":3,"C":2}) and a driver list including an ABSENT
   driver "D" and a TIE (two drivers same position). Assert: the logit signs are correct (lower prior
   position → predicts ahead → positive logit when that driver is i), absent-driver pairs are invalid,
   tie pairs are invalid, and the dropped count matches. If you can call the vectorized snippet via a
   tiny helper, prefer that; otherwise re-implement the exact 3-line rule in the test and assert it
   matches the script's documented contract (cite the line). DO NOT change the script to make it
   testable unless a SMALL, behavior-preserving refactor (extracting the 3-line persistence rule into a
   named pure function `_persistence_logits(prior_pos, driver_ids, i_idx, j_idx)` in the script) is the
   cleanest path — if you do that refactor, it must be behavior-identical and you must re-run the full
   analysis to confirm identical numbers (see Verification). Prefer NO refactor if a direct test works.

4. **`_get_prior_stage_order` task dispatch (no real DB).** Pass a fake `db_cache` pre-populated with a
   stub DatabaseManager exposing `get_session_classification` and `get_race_start_order` (mirror the
   stubs already in `tests/unit/evo_predictor/test_sampled_runtime_data_adapter.py` lines ~91-99 for the
   method signatures). Assert race_start calls `get_session_classification(..., 'Q')` and race calls
   `get_race_start_order(..., expected_target_lap=3)`, and that an exception inside returns `{}`.

5. **`_bootstrap_delta_ci` sanity.** Two identical per-event arrays → CI brackets 0 (lo<=0<=hi).
   A constant positive shift → CI strictly positive. NaN events excluded. Determinism: same seed →
   identical CI across two calls.

## Allowed Scope
- NEW FILE ONLY: `tests/unit/evo_predictor/test_g1_ordering_reconcile.py`.
- OPTIONAL, only if needed for testability: a SMALL behavior-preserving extraction in
  `scripts/fusion_replay/g1_ordering_reconcile.py` (named pure function for the persistence rule). If
  you touch the script, you MUST re-run the full analysis and confirm byte-identical headline numbers.

## Specific Exclusions
- Do NOT edit `docs/evo/fusion_rework_findings.md`.
- Do NOT edit the analysis logic/output of `g1_ordering_reconcile.py` (extraction-only refactor allowed).
- Do NOT touch `src/evo_predictor/`, `sampled_runtime.py`, `quali_pace_anchor.py`, the ceiling doc.
- Do NOT regenerate records. Do NOT add quali.

## Constraints
- Tests must be FAST (<5s total) and hermetic: no DB files, no record files, no network. Build tiny
  numpy arrays / dicts inline.
- `py -m src.utils.simplification_limits` on your new test file AND (if you refactored) on the script
  must pass. Check TESTING.md for whether scripts/ is exempt.
- Tunable values in named constants, not inline magic.

## Required Evidence (paste into your IMPLEMENTER_RESULT)
- Full output of: `PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/test_g1_ordering_reconcile.py -q` (GREEN).
- Full output of: `PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/ -k "fusion or replay or metalearner or record or sampled_runtime" -q` (GREEN, no regressions).
- `PYTHONIOENCODING=utf-8 py -m src.utils.simplification_limits <touched paths>` output.
- If you refactored the script: the reproduce command output showing race_start Model1 LL ~0.33582 and
  race ~0.47736 UNCHANGED, plus the gaps unchanged.

## Suggested Model Tier
standard — focused test authoring against a verified, frozen implementation.

## Authority
You decide test structure and whether the small extraction refactor is warranted (default: no refactor).
You do NOT change any reported number or the verdict.

## Stop Conditions
Stop and report if: a test reveals an actual BUG in the script logic (do not silently fix — report it,
it changes the gate verdict); you would need to touch an excluded file; simplification_limits cannot
pass without altering script behavior.

## Return Format
IMPLEMENTER_RESULT: files changed, test list with what each asserts, all required evidence outputs,
whether you refactored (and the unchanged-numbers proof if so), assumptions, stop conditions hit,
out-of-scope observations.
