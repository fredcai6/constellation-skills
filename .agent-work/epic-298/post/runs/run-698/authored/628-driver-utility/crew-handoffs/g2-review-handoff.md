# Reviewer Handoff — G2 (driver-utility latent + explicit-unknown status + artifact)

## Gate
`g2-review`. Worktree **C:/Programs/f1-628** only.

## What was implemented
- `src/physics/utilization/driver_utility.py` — `estimate_driver_utility(rows_df) -> DataFrame` (one row per
  (year,driver,constructor,axis) via reused `pool_random_effects`; explicit resolved/unresolved status;
  `effective_sigma` via reused `effective_axis_sigma`) + `write_driver_utility_db(df, path)` (untracked SQLite).
- `tests/unit/physics/test_driver_utility.py` — 8 tests.
- Result: `.agent-work/628-driver-utility/crew-results/g2-implement-result.md`.

## Task statement being verified
A partial-pooling driver-utility latent per (driver,axis) with the OWNER-HARD explicit-unknown contract:
every (driver,axis) emits a row WITH a status; thin support → `unresolved` + genuinely WIDE reserved σ;
nothing dropped silently. δ is teammate-relative.

## Close criteria (verify each, re-running the numbers)
- Re-run `py -m pytest tests/unit/physics/test_driver_utility.py -q` → all pass.
- `pool_random_effects` is REUSED (not reimplemented) for δ; `effective_axis_sigma`/`normalize_axis_status`
  REUSED for the reserved-σ contract.
- **Reserved-σ correctness (the load-bearing check):** for an `unresolved` (driver,axis) whose `delta ≈ 0`,
  confirm `effective_sigma` is actually WIDE (reserved scale), NOT ≈0. The implementer reports fixing this by
  passing `value=None` (not `value=delta`) for unresolved rows so the reference_value fallback fires — CONFIRM
  that in the code and that a test exercises the delta≈0 unresolved case.
- **Nothing dropped:** every (driver,axis) in the input emits exactly one row with a status, including a
  zero-valid-observation group.
- **Resolved path:** well-supported driver → status="resolved", δ ≈ DL-pooled mean, σ passes through.
- Artifact `write_driver_utility_db` writes an UNTRACKED `data/driver_utility.db`; `git status data/` shows no
  staged/tracked data file.
- `py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility.py` → PASS.

## Allowed scope / exclusions
Review only the two new files + result. Do not review G1/G3. Out-of-scope finds → triage candidates.

## Map anchors (inbound)
Inherits g2-implement anchors — the explicit-unknown contract (reserved wide σ, nothing dropped) is the
load-bearing review check.

## Required evidence
Paste the pytest re-run, the simplification-limits result, and cite the code lines proving the reserved-σ
`value=None` handling for unresolved + delta≈0.

## Verification commands
```bash
cd /c/Programs/f1-628 && py -m pytest tests/unit/physics/test_driver_utility.py -q
cd /c/Programs/f1-628 && py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility.py
cd /c/Programs/f1-628 && git status --porcelain data/
```

## Return format
REVIEW_RESULT with explicit `verdict: APPROVE` or `verdict: BLOCK`, re-run evidence, severity-ranked findings,
workflow feedback. BLOCK if the reserved-σ contract is defeated (unresolved δ≈0 yields a narrow σ) or any
(driver,axis) is dropped.
