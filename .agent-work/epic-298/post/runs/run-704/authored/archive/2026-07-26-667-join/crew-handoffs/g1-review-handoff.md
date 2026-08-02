# Reviewer Handoff — g1 (the join module + T7 gating tests)

## Gate
`g1` (issue #667, epic #659 — "the join")

## What was implemented
- NEW `src/physics/fingerprint/join.py` — pure `join_weekend_prior(...)` + `WeekendUtilizationPrior`.
- NEW `tests/unit/physics/fingerprint/test_join.py` — 18 tests (claimed 18/18 green).
- IMPLEMENTER_RESULT: `.agent-work/667-join/crew-results/g1-implement-result.md`.

## How to inspect
Read `src/physics/fingerprint/join.py` and `tests/unit/physics/fingerprint/test_join.py` in the
worktree `C:/Programs/f1brainz-wt/epic659-667`. Both are untracked (new files) — `git status`, not
`git diff`. Re-run the tests yourself with the PINNED interpreter:
```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_join.py -q
```

## Task statement (what the join must be)
A PURE normalized-weighted-average join of a circuit's per-class corner TIME-share composition ×
a driver's fingerprint cells → a per-weekend quali-side utilization prior with honest Student-t σ.
The 4 T7 reduces-to-simple-case invariants + the T7-5 general case are the correctness gate: a
mechanically-broken join can beat a driver-overall baseline through compensating errors, so these
unit invariants — NOT an outcome win — are what proves correctness.

## Close Criteria (verify each independently — do not trust the implementer's claim)
- **Join arithmetic:** normalized weighted average `w_i = comp_i / Σcomp`; `prior_mean = Σ_res w_i m_i / Σ_res w_i` (== μ_res); composition NOT renormalized to 1.0 (`corner_share = Σcomp`).
- **T7-1** uniform composition ⇒ `prior.mean == UNWEIGHTED arithmetic mean of the k cell means`.
  CONFIRM the test asserts EQUALITY to the unweighted cell mean (not an approximation that would
  mask a normalization bug), and that the comparator is documented.
- **T7-2** identical cells ⇒ that constant for any composition. **T7-3** single-class ⇒
  `combined_scale == that cell's σ` and mean == that cell's mean.
- **T7-4** soft memberships unchanged; `corner_share == Σ input shares` and NOT 1.0.
- **T7-5** (the real broken-join catch) DISTINCT shares × DISTINCT means ⇒ `prior.mean` ==
  hand-computed `Σ (comp_i/Σcomp)·m_i` to full precision, AND the test is pinned to numbers where a
  ÷k or renormalize-to-1.0 bug would give a DIFFERENT value (verify the numbers actually
  distinguish those bugs — this is the load-bearing check).
- **σ propagation:** `combined_scale = sqrt(Σ_res w²σ² + (weight_on_thin·σ_unres)²)`; `σ_unres` CAN
  EXCEED resolved σ (derived from cross-class mean spread vs max resolved σ); `n_eff =
  n_eff_res·(1−weight_on_thin)`, `n_eff_res = 1/Σ(w²/support)`. CONFIRM the **numeric thin-widening**
  test: same inputs, one class flipped resolved→unresolved ⇒ STRICTLY WIDER prior scale (proves the
  unresolved path fattens, not caps — this guards the cold-critic BLOCKER).
- **Thin surfacing:** unresolved class ∈ thin_classes with weight in weight_on_thin; all-resolved ⇒
  empty/0.0. **Both channels symmetric.** **Loud refusals:** vocab-version / channel / class-order
  mismatch, missing composition key, corner_share<=0 each raise ValueError. Zero-resolved ⇒
  fully-thin prior (prior=None), never fabricated.
- **Purity:** no store-DB / FastF1 / sqlite import inside join.py (type-only imports of
  FingerprintCell/ClassVocabulary/predictive_t are fine). **No new frozen literal minted.**
- `simplification_limits` passes on both files.

## Specific scrutiny (FLAGGED by the implementer — adjudicate these)
1. `_N_EFF_FLOOR = NU_FLOOR - 2.0` (== 1e-6): the implementer flags this as a possible frozen
   literal. JUDGE: is it a DERIVED numeric guard (keeps n_eff>0 for predictive_t) or a tuned
   threshold? If you judge it a frozen literal (a tuned value), that is an F12 concern → BLOCK and
   it floats to the Admiral. If derived/structural, APPROVE it. State your reasoning.
2. The independent-cell σ assumption (Var=Σw²σ²) — confirm it is stated honestly in the docstring
   and NOT over-claimed as full correlation-honesty.

## Constraints
- The linear join IS the prior — no sequence/interaction/bespoke forms (that is #670).
- Student-t output (no baked-in normality). Pure function. No committed data/*.db. Map fence.

## Map Anchors (inbound)
- `decision:join-is-normalized-weighted-average` @grade: settled/inherited — must hold.
- `decision:sigma-propagation-quadrature-fat-unresolved` @grade: guess — the settled candidate;
  verify it is implemented as specified and the invariants + thin-widening prove it.

## Required Evidence
Reproduce the pytest run yourself (paste output). Reproduce simplification_limits. For T7-5 and the
thin-widening test, independently confirm the asserted numbers are correct and actually discriminate
the bug they claim to catch (recompute by hand for at least T7-5).

## Verification Commands
```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_join.py -q
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" src/utils/simplification_limits.py src/physics/fingerprint/join.py tests/unit/physics/fingerprint/test_join.py
```
(Note: the implementer reported the `-m src.utils.simplification_limits` module-invocation hit the
editable-.pth worktree trap; use the file-path invocation above, or `-m` from the MAIN checkout.
Verify whichever you run actually exercised THIS worktree's files.)

## Suggested Model Tier
`stronger — the σ propagation + exact invariants are subtle and load-bearing`

## Authority
Verdict is yours (APPROVE / BLOCK). The σ form + join arithmetic are DECIDED (do not relitigate the
design — verify the implementation matches it). Do adjudicate the `_N_EFF_FLOOR` frozen-literal
question and the honesty of the independent-cell caveat.

## Stop Conditions
Return BLOCK with specifics if any invariant is mis-stated/missing, the σ path caps instead of
fattening, a frozen literal was minted, purity is violated, or refusals are silent.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/667-join/crew-results/g1-review-result.md`): verdict
(APPROVE/BLOCK), what you verified + reproduced (paste command output), each close-criterion
pass/fail, the two flagged adjudications with reasoning, any out-of-scope observations, workflow
feedback.
