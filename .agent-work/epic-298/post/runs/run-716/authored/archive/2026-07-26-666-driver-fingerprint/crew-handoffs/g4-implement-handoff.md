# Implementer Handoff — G4 (bounded validation fit + acceptance demonstration on real data)

## Gate
g4-implement (issue #666, epic #659)

## Task
Demonstrate ALL acceptance invariants on REAL data: run the G3 fit on the commander-provided real bounded slice,
populate a temp fingerprint store, assert the invariants, and emit an honest support+shrinkage summary. This is
the "run bounded" half of build-season-capable/run-bounded.

## Protected Intent
This is the proof the whole machine works on real observations — and the honest record of how thin the signal is.
A measured-null (cells collapsing to the parent under thin support) is a COMPLETE, successful deliverable — report
it as such with the numbers, never dress it up.

## Test Mode
Test-after acceptable for the validation harness (it exercises already-tested code on real data); the invariant
ASSERTIONS are the point. `tests/unit/physics/fingerprint/test_bounded_validation.py`; the real slice DB is
READ-ONLY input, the fingerprint store is a TEMP DB (#656).

## Inputs
- Real slice (READ-ONLY): `.agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db` — 2023 Q, 4 circuits
  (Monaco R6 street, Spain R7, Great Britain R10, Belgium R12), drivers VER/PER/LEC/SAI, k=4 severity classes.
  Severity-cell support (real imbalance): c0 avg n_points≈340, **c1≈1.3 (THIN, near the 1.0 unresolved floor)**,
  c2≈191, c3≈22.6.
- The G3 fit `src/physics/fingerprint/fit.py`, the G2 store/address/vocabulary, `FINGERPRINT_FROZEN`.

## Close Criteria (each asserted on REAL data)
- **Cutoff-leakage on real rounds:** `fit(as_of_round=7)` on the full slice == `fit(as_of_round=7)` on a slice
  truncated to `round_idx<=7` (byte-identical cells) — proves the cutoff excludes the REAL future rounds 10 & 12.
  Also `fit(as_of_round=12)` differs from `fit(as_of_round=7)` (more rounds visible) — the cutoff is load-bearing.
- **Exactly k cells + unresolved-not-missing:** each (driver, era, channel) fingerprint returns EXACTLY k=4 cells;
  the thin c1 cell (support ≈1.3, and BELOW the 1.0 floor in some driver/cutoff combinations) is either resolved
  (heavily shrunk/widened) or `unresolved` — report which per cell; NEVER a missing row.
- **Thin-cell σ-widening priced once** on the real thin cells (the c1 cell shows a widened σ; re-running the fit is
  idempotent — the store replace-on-rerun does not double-widen).
- **Class-axis shared_floor applied per #675:** `shared_floor_applied = sqrt(var_circuit)` per channel is recorded
  on the resolved cells (non-zero); driver-overall NOT floored.
- **Both channels fit:** time + energy cells both present.
- **ClassVocabulary F12 verdict sourced with PROVENANCE (not silent PASS):** construct the production k=4 severity
  vocabulary and source its `f12_verdict` from the existing f12 machinery (`src/physics/layer2/mixture_stability.py`
  threshold / `scripts/f12_held_out_stability.py`) if derivable for this slice; if not readily derivable within
  scope, carry `f12_verdict="UNVERIFIED"` with an explicit `f12_provenance` string and fit via the documented
  `require_fittable(override=True)` path — NEVER a silent hardcoded PASS. State clearly which path you took.
- Emit `.agent-work/666-driver-fingerprint/artifacts/bounded_fit_summary.json`: per-cell (driver, class, channel)
  support_n, sigma before vs after the shared_floor widening, the shrinkage-toward-parent magnitude
  (|cell_point − class_parent| and |cell_point − driver_overall|), status, and a list of measured-null cells
  (those collapsed to the parent / unresolved). Plus a short prose `honest_statement`.

## Allowed Scope
CREATE `tests/unit/physics/fingerprint/test_bounded_validation.py` and (optional) a small helper
`scripts/fingerprint_bounded_validation.py` if you prefer a runnable harness (output-only; committed is fine).
READ-ONLY: the fit/store/vocabulary modules, the slice DB, mixture_stability/f12 machinery.

## Specific Exclusions
Do NOT run the full-season pipeline or any online call. Do NOT regenerate the slice. Do NOT edit the G2/G3 modules
(if a real gap surfaces, STOP and surface it). Do NOT commit any data/.agent-work blob (the slice DB + summary
JSON are gitignored).

## Constraints
- Interpreter PIN + `PYTHONPATH=.`; `from src...` imports. Temp store; slice read-only.
- measured-null = COMPLETE deliverable (no frame-kill).
- No silent PASS for the vocab verdict.
- No data/.agent-work blob staged.

## Map Anchors (inbound)
- **Structural:** `struct:physics.fingerprint` fit/store; `struct:physics.utilization` driver_class_observables (real slice).
- **Decision anchors:** `decision:c1_driver_utilization_design` — strictly_pre. `@grade: settled/measured · leans g4-implement`
- **Evidence expectations:** `claim: cutoff-leakage`, `claim: k-cells-populated`, `claim: sigma-priced-once`, `claim: #675-coverage recorded`.

## Deliverable Path Check
- Committed: `tests/unit/physics/fingerprint/test_bounded_validation.py` (+ optional
  `scripts/fingerprint_bounded_validation.py`) — check-ignore exits 1; new files appear in `git status`.
- Local-only: `.agent-work/666-driver-fingerprint/artifacts/bounded_fit_summary.json`, the slice DB, temp store.

## Required Evidence
- LOAD-BEARING: the real-data cutoff-leakage assertion; the k-cells+unresolved on the thin c1 cell; the
  shared_floor_applied non-zero; paste `bounded_fit_summary.json`; the honest support/shrinkage statement.
- Confirmatory: full `tests/unit/physics/fingerprint/` green; simplification_limits on new files; clean git status.

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/ -q
```

## Suggested Model Tier
Simple-to-moderate — exercises already-tested code on real data; the care is in honest reporting + the vocab
verdict provenance.

## Authority
The invariant set + the "measured-null is complete" framing are commander-decided. You MAY choose the vocab
verdict sourcing path (derive-from-f12 vs UNVERIFIED+override) — document it honestly.

## Stop Conditions
Stop and return if: the fit reveals a real defect in G2/G3 on real data (do not patch across gates — surface it);
the slice DB is unusable; the vocab verdict cannot be sourced without a silent PASS.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test-mode, evidence (paste bounded_fit_summary.json +
the real-data invariant assertions + full suite green), the HONEST support-size + shrinkage-behavior statement
(name any measured-null cells), assumptions (vocab verdict path), stop conditions, out-of-scope, workflow feedback.
Write to `.agent-work/666-driver-fingerprint/crew-handoffs/g4-implement-result.md` AND SendMessage a concise
summary to `cmdr-666` before ending your turn.
