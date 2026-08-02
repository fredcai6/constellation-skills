VERDICT: APPROVE

# Review Result

## Assigned Gate
g2 — test suite + committed 2022 Spain R sector-gate reproduction (issue-448-trajectory-estimator)

## Result
APPROVE

## Handoff compliance
All six close criteria satisfied. Unit tests are real assertions. Reproduction uses automatic `fit_stint_hp` for all drivers with no hardcoded HP dictionary. Gate assertion is ≤50 ms and not weakened. Evidence is consistent with claimed 22.77 ms result. Integration test skips cleanly when data absent. `JointFusion` imported only from `tests/oracles/`. g2 commit touched only `tests/` and `.agent-work/` (no `src/` changes).

## Scope drift
None. `git show --stat HEAD` confirms 16 files changed, all under `tests/` or `.agent-work/issue-448-prod/`. Zero src/ touches.

## Evidence verdict
Evidence is present, consistent, and substantive:
- `spain_reproduction.json` records `pooled_heldout.median_ms = 22.77 ms` (gate ≤ 50 ms, confirmed by script read of JSON).
- All 3 loops reached `status: heldout` (not degenerate).
- Per-driver HP spread confirmed: ell 0.80–7.03, sf 84.8–176.3, sig_pos 1.60–2.48; chi2_pos ∈ [0.86–1.11], chi2_spd ∈ [0.94–1.26] — all ≈1, generalization evidence clear.
- Lab reference (20.21 ms) and reproduction result (22.77 ms) are plausible and consistent (reproduction uses more drivers / full-automatic path; slightly higher median is expected).
- n=1273 (broader than lab n=509).

## Code/doc quality

### Close-criteria checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Unit tests are REAL assertions, 17 pass | PASS — `py -m pytest tests/unit/preprocessing/trajectory -q` → 17 passed (44.4s) |
| 2 | Nesting-oracle asserts StintSmoother vs JointFusion with tight tolerance | PASS — median ≤0.5 mm at-sample, max ≤5 mm (test_nesting_oracle.py:49-50) |
| 3 | Synthetic-honesty asserts held-out chi²≈1 | PASS — asserts 0.7 ≤ chi2_pos ≤ 1.4 and 0.7 ≤ chi2_spd ≤ 1.4 (test_synthetic_honesty.py:64-65) |
| 4 | r==1 selftest asserts ~1e-10 | PASS — `np.allclose(base.m_s, ns.m_s, atol=1e-10, rtol=0.0)` (test_nesting_oracle.py:83) |
| 5 | Artifact round-trip asserts field preservation | PASS — all 8 fields checked by name + value to atol=1e-9 (test_artifact_roundtrip.py:58-65) |
| 6 | Trust profile asserts structured profile shape, not pass/fail | PASS — asserts dict with keys {held_out, nis, loop_resid} and per-class fields; `not isinstance(prof, bool)` check present (test_trust_profile.py:28-29) |
| 7 | Reproduction uses AUTOMATIC fit_stint_hp for ALL drivers — NO hardcoded HP dict | PASS — grep for KNOWN/ell=/sf= in _spain_repro.py shows only float extractions from the returned hp dict and one docstring mention; no KNOWN dict, no per-driver literals |
| 8 | Gate assertion ≥50 ms present and not weakened | PASS — `assert median_ms <= GATE_MS` with explicit message forbidding HP fallback (test_trajectory_spain_reproduction.py:127-131) |
| 9 | Evidence records pooled median ≤50 ms (22.77 ms) + per-driver HP spread | PASS — JSON verified, MD table matches |
| 10 | Integration test skips cleanly when data absent | PASS — `_data_available()` check at test start; `pytest.skip(...)` on false; DB + cache + fastf1 import all gated |
| 11 | Absolute paths into main checkout for DB + cache | PASS — `_DB = Path("C:/Programs/f1Brainz/data/f1_data_2022.db")` and `_CACHE = Path("C:/Programs/f1Brainz/outputs/cache")` are hard absolute paths |
| 12 | JointFusion imported only from tests/ (not src/) | PASS — grep over tests/ and src/ confirms import only in `tests/oracles/joint_fusion_oracle.py` and `tests/unit/preprocessing/trajectory/test_nesting_oracle.py`; src/ reference is a docstring comment only |
| 13 | g2 commit touched only tests/ + evidence (no src/ change) | PASS — git show --stat HEAD lists 16 files, all `.agent-work/` or `tests/` |

## Map impact verdict

- **Evidence supports claimed change:** Yes. pooled_heldout.median_ms=22.77 ms in the JSON directly backs the claimed ≤50 ms gate. Per-driver chi² all ≈1 directly backs the automatic-calibration generalization claim (D3).
- **Constraints not violated:** DB-only boundary intact (no FastF1 direct calls from src/). The test uses FastF1 only as an integration dependency gated behind skip; source module not touched.
- **Notes match the diff:** Implementer result says "None required" for source fixes; confirmed by git stat — zero src/ lines in the diff.
- **Decision candidates surfaced:** D3 (automatic calibration generalization) was the load-bearing Admiral ruling; the reproduction demonstrates it holds. No new decisions required.
- **Durable context routed:** Out-of-scope observation (quali thin-n sessions 47–63 ms) flagged as triage candidate in the implementer result. Workflow anti-pattern (backgrounding a 13-min task) flagged in implementer feedback.

## Reconciliation check
No architecture changes. New capability (trajectory unit tests + reproduction) is additive under `tests/`. The `tests/oracles/joint_fusion_oracle.py` oracle was pre-existing. No structural changes to `src/preprocessing/trajectory/` or any other module. No reconciliation needed.

## Blockers
None.

## Out-of-scope observations
- Quali thin-n sessions (47–63 ms lab values) are out of scope; flagged as triage candidate by implementer. No action needed here.
- `src/preprocessing/trajectory/dynamics.py` line 132 contains a docstring comment referencing JointFusion by name (not an import). This is cosmetic — no action needed.

## Workflow Feedback

- **Handoff gaps:** The handoff said "confirm the >=50ms assertion is present and not weakened" but the gate is `<= 50 ms` (less-than-or-equal). The wording ">=50ms assertion" is ambiguous — likely meant "assert result ≤ 50 ms". No confusion on actual checking, but the phrasing is inverted and could mislead a future reviewer. Suggest rephrasing to "confirm the gate assertion (median ≤ 50 ms) is present and not weakened."
- **Context rediscovered:** Had to grep src/ for JointFusion to confirm the dynamics.py comment was not an import — the handoff only said "JointFusion is imported only from tests/oracles/ (not from src/)"; the comment in src/ was a potential false positive requiring a grep to resolve.
- **Instructions improvised around:** The engine template (REVIEW_SURVEY.template.json) provides 6 survey checks but the handoff has 7+ specific close criteria. I mapped the close criteria into r4-quality as sub-checks (one per inherited rule) as instructed, and ran them inline rather than via a live engine call, because the engine CLI path was not initialized for this workbench (no survey JSON file pre-created). The review logic is complete and all checks are documented.
- **What would have made this easier:** Pre-initialize the survey JSON with the close-criteria items expanded from the handoff, so the reviewer can `engine advance` through a concrete per-criterion checklist rather than re-deriving from the handoff text.

## Return status
complete
