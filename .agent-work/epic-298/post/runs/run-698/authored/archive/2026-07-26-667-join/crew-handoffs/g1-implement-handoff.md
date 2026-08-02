# Implementer Handoff — g1 (the join module + T7 gating tests)

## Gate
`g1` (issue #667, epic #659 Wave 4a — "the join")

## Task
Build `src/physics/fingerprint/join.py`: a **pure** function that composes a circuit's
per-class corner TIME-share composition with a driver's fingerprint cells into a per-weekend,
quali-side utilization prior with honest Student-t σ. Plus `tests/unit/physics/fingerprint/test_join.py`.

## Protected Intent
This is the core Build-1 product; Fred's fantasy-points decision metric rides on it. The
correctness hazard is subtle-and-silent: a mechanically-broken join (wrong per-class weight,
sign error on a cell subset, wrong σ-widening) can still beat a driver-overall baseline through
compensating errors. The 4 T7 reduces-to-simple-case invariants + the T7-5 general case are the
gate that catches that. σ-propagation correctness through the soft-membership-weighted linear
combination is where this earns its cost.

## Test Mode
TDD strongly preferred (the invariants ARE the spec). Test-after acceptable if every invariant
below is covered exactly.

## Close Criteria
- `join_weekend_prior(composition, cells, vocabulary, *, as_of_round, nu_loss=DEFAULT_NU_LOSS,
  rule=FormulaRule(), map_version=None) -> WeekendUtilizationPrior` implemented, PURE (no store /
  FastF1 / DB import inside it — the caller passes `composition: Mapping[str,float]` and
  `cells: Sequence[FingerprintCell]`).
- **Join arithmetic = NORMALIZED WEIGHTED AVERAGE** over the k severity classes:
  - `comp_i = composition[class_id]` for each `class_id in vocabulary.class_ids` (a missing key
    refuses loudly). Do NOT renormalize the input composition. `corner_share = Σ comp_i` (NOT 1.0).
  - weights `w_i = comp_i / corner_share` (Σ w_i = 1).
  - `prior_mean = Σ w_i m_i` over RESOLVED cells; an UNRESOLVED cell's mean falls back to the
    resolved-weighted mean `μ_res` (so it never silently shifts the mean, and prior_mean == μ_res).
- **σ propagation (QUADRATURE, pinned):**
  `combined_scale = sqrt( Σ_res w_i²·σ_i²  +  (weight_on_thin · σ_unres)² )`.
  - `σ_unres` MUST be able to EXCEED the resolved cells' σ (an UNKNOWN class inflates uncertainty
    beyond known dispersion — it must WIDEN, never CAP, the prior):
    `σ_unres = max( cross-class spread of the resolved cell MEANS (population std; use range/2 if
    <2 resolved), max_resolved_σ )`. DERIVED — never a new frozen literal.
  - `n_eff` MUST fold in the thin weight so the TAIL fattens (not just the scale):
    `n_eff_res = 1 / Σ_res (w_i² / support_i)` (weight-aware effective count — NO arbitrary
    "meaningfully-weighted" threshold), then `n_eff = n_eff_res · (1 − weight_on_thin)`, floored
    to keep `predictive_t` valid (just above where nu would hit NU_FLOOR).
  - Wrap: `predictive_t(mu=prior_mean, sigma=combined_scale, n_eff=n_eff, nu_loss=nu_loss, rule=rule)`.
- **`WeekendUtilizationPrior`** frozen dataclass fields: `driver`, `channel`,
  `prior: PredictiveT | None`, `mean: float | None`, `corner_share`, `class_ids: tuple`,
  `weights: tuple`, `resolved_mask: tuple[bool,...]`, `thin_classes: tuple[str,...]`,
  `weight_on_thin: float`, `as_of_round: int`, `vocabulary_version: str`,
  `map_version: str | None`, `share_provenance: str = "time"`.
- **Loud refusals (no silent substitution):** every `cell.vocabulary_version ==
  vocabulary.vocabulary_id`; all cells share one `channel`; cell `class_id`s equal
  `vocabulary.class_ids` in order; each vocabulary class present in `composition`;
  `corner_share <= 0`. Each raises a `ValueError` naming the mismatch.
- **Zero resolved cells** ⇒ return a fully-thin prior (`prior=None`, `mean=None`,
  `weight_on_thin=1.0`, `thin_classes = all class_ids`) surfaced loudly — NEVER a fabricated value.
- **Independent-cell assumption** (`Var=Σw²σ²` treats classes as uncorrelated, ~1/√k shrink under
  averaging) stated honestly in the module docstring as a Build-1 simplification.
- Tests (`test_join.py`) cover EXACTLY — see Required Evidence.
- `py -m pytest tests/unit/physics/fingerprint/test_join.py -q` green; simplification_limits pass.

## Allowed Scope
- CREATE `src/physics/fingerprint/join.py`, `tests/unit/physics/fingerprint/test_join.py`.
- MAY add exports to `src/physics/fingerprint/__init__.py` IF that matches the package convention
  (check the existing `__init__.py` first).
- Consume `FingerprintCell` from `src.physics.fingerprint.store`; `ClassVocabulary` from
  `.../vocabulary`; `predictive_t`, `PredictiveT`, `FormulaRule`, `TailRule`, `DEFAULT_NU_LOSS`,
  `NU_FLOOR` from `src.common.student_t`; `FINGERPRINT_FROZEN` if any frozen value is needed.

## Specific Exclusions
- Do NOT read the #664/#666 stores inside the join (that is g2's harness). The join is pure.
- Do NOT mint any new frozen literal (F12) — if you believe one is genuinely needed, STOP and
  return it as a blocker (it is a FLOAT to the Admiral), do not inline it.
- Do NOT build sequence/interaction/bespoke forms (that is #670). The linear join IS the prior.
- Do NOT touch the cell store's direct-read API or any #668/#670 surface.

## Constraints
- PURE function — no store/DB/FastF1 import inside `join.py`.
- Student-t output (no baked-in normality).
- Tests use temp DBs only if any DB is touched (#656) — but the join is pure, so tests should
  construct `FingerprintCell` / `ClassVocabulary` objects DIRECTLY (no DB needed).
- `FingerprintCell` fields: driver, era, vocabulary_version, class_id, channel, what_measure,
  mean (Optional), sigma (Optional), support_n (Optional), status ("resolved"/"unresolved"),
  shared_floor_applied, format_version. `ClassVocabulary` fields: vocabulary_id, rules_era, k,
  class_ids (tuple), f12_verdict, f12_provenance.

## Map Anchors (inbound)
- **Structural:** `src/physics/fingerprint/join.py` (NEW pure module); `test_join.py` (NEW).
- **Capability:** weekend-utilization-prior (compose circuit composition × driver fingerprint).
- **Constraints:** normalized-weighted-average forced by T7-1; composition sums to corner share
  (no renormalize); thin exposure surfaced not discounted; vocabulary-version pinned/loud-refusal.
- **Decision anchors:**
  - `decision:join-is-normalized-weighted-average` @grade: settled/inherited (DESIGN_SPEC line 132 + T7) — do not contradict.
  - `decision:sigma-propagation-quadrature-fat-unresolved` @grade: guess · settle: T7-5 + numeric thin-widening test — the σ form above is the settled candidate; implement it as specified.
- **Evidence expectations:** the 4 T7 invariants + T7-5 pass exactly; thin cell fattens σ numerically.

## Deliverable Path Check
- **Committed** — `src/physics/fingerprint/join.py`; `git check-ignore` exit 1 (NOT ignored). New
  file — appears in `git status`, not `git diff` until staged.
- **Committed** — `tests/unit/physics/fingerprint/test_join.py`; `git check-ignore` exit 1. New file.
- **Local-only** — write your IMPLEMENTER_RESULT to
  `.agent-work/667-join/crew-results/g1-implement-result.md` (gitignored; not in the diff).

## Required Evidence
`test_join.py` MUST assert, EXACTLY (load-bearing — prove rigorously):
- **T7-1** uniform composition (all shares equal) ⇒ `prior.mean == unweighted arithmetic mean of
  the k cell means` (the join-level driver-overall mean). Document that comparator in a comment.
- **T7-2** all cells identical (same mean) ⇒ `prior.mean == that constant` for ANY composition.
- **T7-3** single-class circuit (one class's share nonzero, rest 0) ⇒ `combined_scale == that
  cell's σ` AND `prior.mean == that cell's mean`.
- **T7-4** soft memberships flow through unchanged; `corner_share == Σ input shares` and is NOT 1.0.
- **T7-5** (the real broken-join catch) DISTINCT shares AND DISTINCT cell means ⇒ `prior.mean`
  equals the hand-computed `Σ_i (comp_i/Σcomp)·m_i` to full float precision; ALSO assert that a
  wrong normalization (÷k, or renormalizing comp to 1.0) would give a numerically DIFFERENT value
  (i.e. pick numbers where the degenerate cases can't hide the bug).
- **σ thin-widening (numeric):** SAME inputs, one class flipped resolved→unresolved ⇒ prior scale
  STRICTLY WIDER than all-resolved (proves the unresolved path fattens, not caps).
- **σ monotonicity:** a fatter-σ resolved cell ⇒ wider prior.
- **Thin surfacing:** unresolved class ∈ thin_classes with its weight in weight_on_thin;
  all-resolved ⇒ thin_classes empty, weight_on_thin == 0.0.
- **Both channels symmetric:** identical inputs on channel="utilization" and channel="energy"
  produce identical priors.
- **Loud refusals:** vocabulary-version mismatch, channel mismatch, class-order mismatch, missing
  composition key, corner_share<=0 — each raises ValueError. Zero-resolved ⇒ fully-thin prior.
Confirmatory (spot-check): docstring states the independent-cell assumption.

## Verification Commands
```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_join.py -q
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m src.utils.simplification_limits src/physics/fingerprint/join.py tests/unit/physics/fingerprint/test_join.py
```
(Use the pinned interpreter — NEVER bare `py` for real runs. Verify `import fastf1` is NOT needed;
this module is pure. From the worktree the editable `.pth` resolves `src.*` to MAIN's checkout for
BARE scripts — pytest is immune, so run via pytest as above.)

## Suggested Model Tier
`stronger — the σ propagation + the exact invariants are subtle and load-bearing (OPUS-tier issue)`

## Authority
Decided (do not re-litigate): join = normalized weighted average (forced by T7-1); composition
sums to corner share, no renormalize; σ = the quadrature-with-fat-unresolved form specified; both
channels symmetric; pure function. You may choose local naming/structure. You may NOT mint a frozen
literal, change the σ form, or add escalation beyond the linear join — STOP and return if any seems needed.

## Stop Conditions
Stop and return if: a frozen literal seems needed; the σ form as specified can't satisfy an
invariant (report which); allowed scope must be exceeded; a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/667-join/crew-results/g1-implement-result.md`):
completed slice, files changed, test mode satisfied, evidence produced (paste the pytest + 
simplification output), assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback.
