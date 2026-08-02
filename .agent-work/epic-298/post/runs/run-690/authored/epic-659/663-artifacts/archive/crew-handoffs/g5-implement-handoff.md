# Implementer Handoff

## Gate
g5-implement (GATING acceptance evidence — issue #663's second of two falsifiable gates)

## IMPORTANT CONTEXT FROM g4 (read this before starting)
g4 (the held-out reconciliation gate, already complete/APPROVED) found a MEASURED NEGATIVE: subtracting G's fitted curve worsens cross-session reconciliation on real 2023 FP data, diagnosed to structurally UNIDENTIFIED per-session curve fits — several sessions showed `offset<->asymptote correlation` at ±0.999+ (the aliasing wall) with physically absurd asymptote magnitudes (e.g. -107640s). This gate (g5) tests the SAME identifiability question synthetically — with known ground truth — so it is very plausible this gate will ALSO find a measured negative (the fit's separability criterion failing), which would independently CONFIRM g4's diagnosis rather than contradict it. Build this gate with the same honesty as g4: report exactly what you find, whether it's a pass or a null. Do NOT let g4's finding bias you toward manufacturing a pass, and do NOT let it bias you toward manufacturing a more dramatic failure than what you actually measure — run the real synthetic experiment and report the real numbers.

## Task
Build a synthetic-recovery/identifiability evaluation harness at `tests/unit/physics/layer2/test_grip_synthetic_recovery.py` implementing the frozen decision (interrogation q5):

1. Inject a KNOWN saturating curve (asymptote, rate) + KNOWN per-session offsets into SIMULATED field-pooled pace data. Match real 2023 session shapes: driver counts (~20), stint structure (use the same session-shape distributions g4 already characterized — or your own reasonable synthetic analog), realistic noise levels (base this on the residual scale you observe from a real fit, or a reasonable literature-typical lap-time noise sigma, state your choice).
2. Run G's ACTUAL fit pipeline — import and call `src/physics/layer2/grip_baseline.py`'s `fit_grip_baseline_from_laps` (the SAME function g2 built and g4 called) on the synthetic data. Do NOT reimplement a separate fit routine — if you do, this test proves nothing about the real module.
3. Across >=50 replicates (vary noise seed, and optionally vary session count/driver count/injected-parameter values to cover a reasonable range — state what you varied):
   - **(a) Parameter recovery:** for each replicate, check whether the recovered curve params (asymptote, rate) AND each session's recovered offset land within the fit's OWN reported 2-sigma predictive interval (build this via `src/common/student_t.py`'s `predictive_t(mu, sigma, n_eff, ...)` — cite the exact call) of the INJECTED ground truth. Compute the fraction of replicates where this holds; report it. Criterion synthetic-criterion (frozen at `understand`, q5): pass if >=90% of replicates land within interval.
   - **(b) Separability:** for each replicate, read the fit's own estimated/reported correlation between the curve's initial value (or asymptote — use whichever `curve_offset_correlation` field g1/g2 already expose) and the session offset. Compute the fraction of replicates where `|correlation| < 0.8`. Report this fraction. Pass if >=90%.
4. Report BOTH rates explicitly, plus enough diagnostic detail (e.g. a histogram-style summary of the correlation distribution across replicates) that a reader can see WHY it passed or failed — especially given g4's finding, a failure here would not be surprising and should be explained with the same rigor g4's implementer used (e.g. is it a specific session-shape regime that fails, or uniform across all replicates?).

## HONEST-NULL OPERATIONALIZATION (same discipline as g4 — read g4's implementer result and test file at `tests/unit/physics/layer2/test_grip_heldout.py` and `.agent-work/663-grip-g/crew-handoffs/g4-implement-result.md` for the pattern that was reviewed and APPROVED)
The pytest command must exit 0 whenever the harness runs the full replicate count and computes+reports both rates — whether they clear 90% or not. Do NOT write `assert recovery_rate >= 0.90` or `assert separability_rate >= 0.90` as a pytest assertion. Assert only harness validity: the replicate count actually ran (`>=50`), every replicate produced finite numbers, the fit pipeline was genuinely called (not stubbed), and both rates were computed and logged. Print/log/return the actual rates as real output — write a results artifact (e.g. `.agent-work/663-grip-g/g5-synthetic-results.json`) mirroring g4's pattern.

## Protected Intent
This is the SECOND of two GATING acceptance criteria for the whole issue #663. A failure here is a complete, valid, reportable deliverable per the Honest-Null Clause — especially since g4 already found a related problem. Do not manufacture a pass; do not manufacture drama either — measure and report.

## Test Mode
Real synthetic-data evaluation harness (not TDD).

## Close Criteria
- Harness at `tests/unit/physics/layer2/test_grip_synthetic_recovery.py` (exact path — g5-integrate's postcondition hardcodes it).
- >=50 replicates, genuinely calling `fit_grip_baseline_from_laps` (imported, not reimplemented).
- Both rates (parameter recovery, separability) computed and reported with the 90% threshold applied as a REPORTED verdict, not a pytest assertion.
- Uses `predictive_t` for the 2-sigma interval check (cite the exact call).
- Pytest exits 0 regardless of pass/fail on the scientific criteria.
- `simplification_limits` clean.

## Allowed Scope
- New file: `tests/unit/physics/layer2/test_grip_synthetic_recovery.py`.
- Optional local-only results artifact under `.agent-work/663-grip-g/` (not committed).
- Read-only: `grip_baseline.py`, `grip_store.py`, `student_t.py`.

## Specific Exclusions
Do not modify `grip_baseline.py`, `grip_store.py`, `grip_batch.py`, or the g4 test file. Do not attempt to FIX the identifiability problem g4 found — that is a separate decision for g6/the commander, not this gate's job.

## Constraints
- Must call G's ACTUAL fit pipeline (import `fit_grip_baseline_from_laps`), not a reimplementation.
- A null result must be reported with full rigor, not papered over.
- Test assertions must not fail merely because the scientific result is a null.

## Map Anchors (inbound)
- **Decision anchors:**
  - `decision:synthetic-identifiability` @grade: settled/human · leans g5-implement,g5-review
  - `decision:synthetic-criterion` @grade: guess · leans g5-implement · settle: run the harness, adjust the 0.8 threshold with recorded reasoning if it proves miscalibrated

## Deliverable Path Check
- **Committed** — `tests/unit/physics/layer2/test_grip_synthetic_recovery.py`; verify `git check-ignore` exit 1.
- **Local-only** — any results JSON under `.agent-work/663-grip-g/`.

## Required Evidence
- Both rates (parameter recovery %, separability %) — load-bearing.
- Diagnostic detail explaining the result (load-bearing given g4's context).
- `pytest -q -s` full output, exit 0 regardless of outcome.
- `simplification_limits` clean.
- Confirmation the harness calls g2's real function (grep/cite the import).

## Verification Commands
```bash
cd /c/Programs/f1brainz-wt/epic659-663
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m pytest tests/unit/physics/layer2/test_grip_synthetic_recovery.py -q -s
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_grip_synthetic_recovery.py
```
Use this exact launcher path — plain `py` resolves to a broken shim.

## Suggested Model Tier
Stronger — reason: same class of load-bearing scientific evidence as g4; needs a careful, honest synthetic experiment design.

## Authority
The mechanics (replicate count, both rates, thresholds) are frozen; exact synthetic-data generation parameters (noise level, session-shape choices) are yours within the stated constraints.

## Stop Conditions
Stop and return if: `fit_grip_baseline_from_laps` cannot be called on synthetic data without a structural change to its signature (describe what's blocking), or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/663-grip-g/crew-handoffs/g5-implement-result.md`, and return as final message text): completed slice, files changed, the real recovery/separability rates + diagnostic detail, evidence produced (paste outputs), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
