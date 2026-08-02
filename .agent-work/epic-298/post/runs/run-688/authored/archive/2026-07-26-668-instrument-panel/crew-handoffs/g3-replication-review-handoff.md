# Reviewer Handoff — g3-replication-review (LOAD-BEARING)

## Gate
g3-replication-review (#668 instrument panel). Worktree `C:/Programs/f1brainz-wt/epic659-668`,
branch `epic659/668-instrument-panel`. PINNED interpreter
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Survey State Location
`.agent-work/668-instrument-panel/g3-replication-review/review.json`.

## What Was Implemented
Instruments 2+3 — `src/physics/instrument_panel/replication.py` + 18 tests in
`tests/unit/physics/instrument_panel/test_replication_channel.py`. The golf-corrected split-half
replication (double-centering), out-of-sample σ-honesty, and the per-class channel comparison.
Implementer result (READ IT — esp. its Workflow Feedback):
`.agent-work/668-instrument-panel/crew-results/g3-replication-implement-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree (linked worktree). `git status --porcelain` then `git diff`. New files
show in `git status`, not `git diff` until staged. Do NOT use `git diff main...HEAD`.

## THE ONE THING THIS REVIEW MUST GET RIGHT (load-bearing correctness)
The implementer surfaced and resolved a genuine mathematical subtlety. **Independently verify
the resolution is correct**, because the whole instrument's validity rests on it:
- Claim: within a SINGLE class, across drivers, double-centering ≡ per-driver-demean, because
  the class mean is a constant across drivers and Pearson correlation is invariant to an
  additive constant. Therefore the **interaction-replication r (the primary statistic + the
  negative control) must span CLASSES** (correlate the flattened driver×class residual matrix
  between halves) — only there does the shared class main effect inflate a demean-only
  correlation, letting the negative control discriminate. The per-class channel-comparison r
  stays within-class-across-drivers (a separate quantity).
- **Verify this yourself** (a scratch derivation or a tiny standalone script, outside the repo,
  read-only): confirm (a) that a within-class across-drivers correlation is identical under
  double-centering and per-driver-demean, and (b) that the module's primary interaction r spans
  classes so the negative control genuinely discriminates. If the module's primary r were
  within-class only, the negative control would be vacuous — that must NOT be the case.

## Close Criteria (each a review check — reproduce every number)
- **Golf-correction is DOUBLE-CENTERING** (`v − driver_mean − class_mean + grand_mean`), a pure
  data transform, NOT a fitted interaction term / model.
- **3-arm falsifier** reproduces: arm(a) overall-skill r≈0; arm(b) pure-shared-class r≈0 AFTER
  correction; arm(c) injected interaction recovers monotonically. The generator carries a TRUE
  driver×class interaction term (confirm it does — an additive-only generator would make arm (c)
  meaningless).
- **NEGATIVE CONTROL passes**: per-driver-demean-ONLY reports HIGH r on arm(b) while
  double-centering reports ~0 — proving the falsifier discriminates and double-centering is
  necessary. Reproduce the reported r_double≈0.0006 vs r_demean≈0.685 gap.
- **σ-honesty is OUT-OF-SAMPLE** (held-out half / LOO), Student-t via `predictive_t` (heavy-tail
  path exercised, NOT ±1.96σ). Understated σ is DETECTED (coverage materially below nominal).
  Reproduce: correct-σ ≈ nominal; understated-σ well below.
- **Thresholds INJECTED** (`ReplicationThresholds` + `r_floor`); NO frozen `REPLICATION_*` import
  (not minted yet). r_floor(n) matches `threshold + (cap−threshold)*clip((ref−n)/ref,0,1)`.
- **Channel comparison**: winner iff r≥r_floor AND beats other by tie_margin; neither clears →
  unresolved; tie → default utilization; insufficient support → unmeasurable (no-frame-kill).
- No #667 join usage; no real DB read; no `f1_data_*.db` touch; pooling.py/student_t.py
  unmodified. pyright-0 on the new module (reproduce). Tests green on the pinned interpreter.

## Allowed Scope
`src/physics/instrument_panel/replication.py`, `tests/unit/physics/instrument_panel/`. No producer
edits, no real DB, no `data/` change.

## Specific Exclusions
No frozen-module import; no fitted interaction term; no #667 join; no `f1_data_*.db` write.

## Constraints the Implementation Must Respect
Double-centering (not demean); out-of-sample σ-honesty; Student-t (no Gaussian); injected
thresholds; no-frame-kill unmeasurable branch.

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/pooling.py`; `src/common/student_t.py`; `scripts/pooling_imbalance_validation_665.py`; `src/physics/instrument_panel/`.
- **Decision anchors:** decision:golf-correction-is-DOUBLE-CENTERING (interaction r spans classes).
  `@grade: settled/measured · leans g3`
- **Evidence:** claim:golf-correction-removes-skill (3-arm + negative control); claim:coverage-is-distribution-not-gaussian; σ-honesty out-of-sample.

## Evidence Produced
Implementer: 18 tests green, pyright-0, the arm/negative-control/σ numbers above. Reproduce:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_replication_channel.py -q`.
Your APPROVE feeds `g3-replication-integrate.c1` (tests) + `.c2` (verdict).

## Suggested Model Tier
stronger — this is the panel's load-bearing correctness; the cross-class-vs-within-class
resolution and the negative control must be independently confirmed sound, not taken on trust.

## Stop Conditions
BLOCK if: the primary interaction r does NOT span classes (negative control vacuous); the
correction is per-driver-demean rather than double-centering; σ-honesty is self-referential;
Gaussian coverage; thresholds baked; or any number fails to reproduce.

## Return Format
Return REVIEW_RESULT (APPROVE/BLOCK + per-check findings + your independent verification of the
cross-class resolution + workflow feedback). WRITE it to
`.agent-work/668-instrument-panel/crew-results/g3-replication-review-result.md` before ending your turn.
