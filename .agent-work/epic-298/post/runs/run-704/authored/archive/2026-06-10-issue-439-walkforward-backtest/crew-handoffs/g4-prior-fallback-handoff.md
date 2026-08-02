# Implementer Handoff — G4 prior-build robustness (explicit cross-season fallback)

## Gate
`g4` (run-enabling) — make the per-period compound-prior build robust when the as-of-N same-season solve
does not converge (thin support, early periods). Found during the first real run: P1's as-of-6 build fails.

## The problem (diagnosed)
`pipeline.py::_build_prior_root` builds the as-of-N 2025 same-season compound prior via
`run_season_alignment.run_year(2025, through_round=N, ...)`. For P1 (N=6, only 6 races) the constrained
effective-age solve does NOT converge — `fit_compound_prior` exits 1 ("maximum number of function
evaluations is exceeded"), `run_year` raises, and the whole walk-forward aborts before P1's gold cycle.
The solver iteration limit is hardcoded in `src/compound_prior/solver/`; forcing a 6-race prior is unsound.

## Decision (Commander, already made — implement it)
Both a 2025-as-of-N prior and the cross-season (2018-2024) prior are LEAKAGE-SAFE. Promoted gold itself
uses the cross-season prior for all 2025. So: build the as-of-N same-season 2025 prior **best-effort**;
if it FAILS, fall back to the cross-season (2018-2024) prior for that period — EXPLICITLY recorded, never
silent. The model is still trained on 2025 R1..N regardless (the dominant in-season signal); only the
secondary compound normalization differs.

## Task
1. In `pipeline.py::_build_prior_root`: wrap the as-of-N 2025 prior build in a try/except for the
   build failure (nonzero exit / raised error from `run_year`/`fit_compound_prior`). On failure:
   - do NOT create `<period>/compound_prior/2025/...` (leave only the copied 2018-2024 train-year priors);
     `load_time_safe_compound_prior(target_year=2025, allow_same_season_research=True)` then falls back to
     the cross-season prior — verify this is what happens (no 2025 dir ⇒ cross-season).
   - log a clear, explicit message naming the period, the cutoff N, and that it fell back to cross-season.
   - return/record an explicit result: `prior_mode ∈ {"as_of_n", "cross_season_fallback"}` and the
     EFFECTIVE `prior_through_round` (= N when as-of-N succeeds; = 0 when cross-season fallback, since no
     2025 rounds are in the prior).
2. Thread the effective `prior_mode` + `prior_through_round` from the pipeline back through the orchestrator
   into (a) the per-race leakage attestation (use the EFFECTIVE prior_through_round, not the nominal cutoff)
   and (b) the per-race rows of `reports/walkforward/walkforward_2025.summary.json` (+ the `.md`), so each
   race shows which prior mode produced it. Attestation must still pass for both modes (cross-season: 0 <
   every race round; as-of-N: N < every predicted round N+1..N+6).
3. Keep it leakage-correct: cross-season fallback uses ONLY 2018-2024 (no 2025) — confirm no 2025 data
   leaks via the fallback path.

## Protected Intent
Leakage-free, robust, and HONEST: every race's compound-prior provenance is explicitly recorded. No silent
fallback; no abort on a thin-but-expected non-convergence.

## Test Mode
`test-after allowed` — add a unit test that simulates an as-of-N build failure (mock `run_year` to raise)
and asserts: cross-season fallback is taken, prior_mode/through_round recorded, attestation still passes,
and the summary records the mode. Plus a test that a successful as-of-N build records `as_of_n`/N.

## Close Criteria
- A failed as-of-N build no longer aborts the run; the period proceeds on the cross-season prior.
- `prior_mode` + effective `prior_through_round` are recorded per period and surfaced in the summary + attestation.
- Attestation uses the EFFECTIVE prior_through_round and passes for both modes.
- Cross-season fallback provably uses no 2025 data.
- `py -m pytest tests/unit/evo_predictor/walkforward -q` green; `simplification_limits` passes on touched paths.

## Allowed Scope
- `src/evo_predictor/walkforward/pipeline.py`, `orchestrator.py`, `attestation.py`, and their tests.
- Read-only: `src/compound_prior/runtime_normalization.py` (loader fallback behavior), `scripts/run_season_alignment.py`.

## Specific Exclusions
- Do NOT modify the compound-prior SOLVER (`src/compound_prior/solver/`) or `fit_compound_prior` to force
  convergence. Do NOT change G1/G2 semantics, scoring, gold defaults, or promoted params/gold.
- Do NOT run the full multi-hour backtest (Commander reruns after this lands).

## Constraints
- Explicit/recorded fallback (no silent latest-value behavior); DB-only; `py`; repo-root; period-isolated.

## Required Evidence
- New unit test output (fallback path + as-of-n path) green.
- `py -m pytest tests/unit/evo_predictor/walkforward -q` green.
- `py -m src.utils.simplification_limits` on touched paths.
- A quick real check (no full run): drive `_build_prior_root` for P1 (N=6) and show it logs the cross-season
  fallback and leaves no `<period>/compound_prior/2025` dir (the as-of-6 build genuinely fails today, so this
  exercises the real path).

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/walkforward -q
py -m src.utils.simplification_limits
```

## Suggested Model Tier
`stronger` — touches leakage attestation + provenance; correctness of what gets recorded matters.

## Authority
Decided (Commander): best-effort as-of-N with explicit cross-season fallback; attestation uses effective
prior_through_round. You choose the exact data structures to carry prior_mode/through_round. Do NOT touch the
solver or force convergence.

## Stop Conditions
Stop and return if: the loader does NOT fall back to cross-season when the 2025 prior dir is absent (report
the actual behavior); or threading the effective prior_through_round into attestation requires changing
attestation's leakage rule (it should not — only the input value changes).

## Return Format
Return IMPLEMENTER_RESULT: fix, files changed, test mode satisfied, evidence (paste tests + the real P1
fallback check), assumptions, stop conditions, out-of-scope observations.
