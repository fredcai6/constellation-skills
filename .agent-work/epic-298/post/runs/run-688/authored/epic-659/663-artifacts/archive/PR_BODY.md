## Summary

Builds issue #663 (epic #659, Build 1): grip baseline module G — one canonical module owning per-weekend/per-session track grip state (`src/physics/layer2/{grip_store,grip_baseline,grip_batch}.py`), following the repo's existing estimate-store pattern.

**Verdict: built + measured-null (Honest-Null Clause).** Both GATING acceptance criteria were run with full rigor and both converge on the same real, diagnosed defect:

- **g4 (held-out reconciliation, real 2023 data, 4 contrasting circuits, genuinely disjoint driver split):** subtracting G **worsens** cross-session pace reconciliation RMS by **+155.5%** (0/4 circuits improved). Diagnosed to structurally unidentified per-session curve fits (offset↔asymptote correlation pinned near ±1).
- **g5 (synthetic-recovery, 72 replicates, known ground truth):** separability fails — **31.9% vs the 90% threshold** — and even the estimator's cleanest tested regime (data drawn exactly from the model, high SNR) only reaches median `|corr|=0.939`. This independently confirms g4's real-data finding is intrinsic to the functional form, not a data artifact.

Both results were independently re-derived to full precision by separate reviewers before approval (see `.agent-work/663-grip-g/crew-handoffs/g4-review-result.md` / `g5-review-result.md`, and `.agent-work/epic-659/notes-663.md` in the main checkout for the full writeup with all numbers).

## Follow-on issues filed
- #678 — the identifiability defect itself (dominant, high priority)
- #679 — `run_grip_batch` doesn't wire weekend-sibling sessions for the thin-session fallback
- #680 — `sessions.rainfall` schema/storage mismatch (declared REAL, stored as int64 blob)

## What's in this PR
- `src/physics/layer2/grip_store.py` — `GripEstimateRecord` (session-level PK, field-pooled) + `GripStore` (additive-only migration) + `get_grip_at` query surface.
- `src/physics/layer2/grip_baseline.py` — fit logic: field-wide cumulative-track-laps index (reuses `session_race.compute_cumulative_track_laps`'s exact convention), reuses `tyre_supplant.race_degradation_slopes` unchanged via a local session-type-generalized reader (`tyre_supplant.py` itself untouched), Student-t residuals via `predictive_t`, frozen thin-session + rain-flag wide-sigma fallbacks (both real, tested, distinct constants).
- `src/physics/layer2/grip_batch.py` — `run_grip_batch`, injectable-fn batch driver, per-unit failure isolation.
- 5 new test files, including the two GATING harnesses (`test_grip_heldout.py`, `test_grip_synthetic_recovery.py`).
- `docs/architecture/packets/physics.md` + a new decision anchor + `index.md`/`constraints.yml` — architecture map reconciled to reflect the build and its honest limitation.

## Test plan
- [x] `py -m pytest tests/unit/physics/layer2/test_grip_store.py tests/unit/physics/layer2/test_grip_baseline.py tests/unit/physics/layer2/test_grip_batch.py tests/unit/physics/layer2/test_grip_heldout.py tests/unit/physics/layer2/test_grip_synthetic_recovery.py -q` — all pass (honest-null harnesses exit 0 regardless of the scientific outcome; only harness-validity is asserted, never "G must improve").
- [x] `py -m src.utils.simplification_limits --paths src/physics/layer2/grip_baseline.py src/physics/layer2/grip_store.py src/physics/layer2/grip_batch.py` — PASS.
- [x] `py scripts/check_arch_map.py` — OK, green before and after.
- [x] Every crew claim independently re-verified by the commander before integration (not just re-running tests — re-derived key diagnostic numbers by hand at both GATING gates).

Note on Windows environment: this sandbox's plain `py` on PATH resolves to a shim missing scipy/fastf1 — commands were run via the full Windows Python Launcher path. Not a change introduced by this PR.

🤖 Generated with a Constellation Commander (delegated), epic #659 Build 1.

https://claude.ai/code/session_01AxSxn4GGTrbVwWaR52Hm8R
