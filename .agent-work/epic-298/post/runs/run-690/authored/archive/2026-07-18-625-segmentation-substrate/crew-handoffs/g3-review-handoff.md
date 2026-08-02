# Reviewer Handoff

## Gate
g3 (execute.json: g3-review) — F12 mandatory falsifiable gate

## Survey State Location
`.agent-work/625-segmentation-substrate/g3-review/review.json`

## What Was Implemented
`src/physics/layer2/mixture_stability.py` (`hungarian_match`, `component_agreement_stat`,
`SplitResult`/`StabilityResult`, `check_holdout_stability`, pre-registered
`RADIUS_SCALE_M=50.0`/`LATERAL_G_SCALE=0.5`/`F12_AGREEMENT_THRESHOLD=1.0`),
`scripts/f12_held_out_stability.py` (real-data runner). **The real-data verdict is FAIL**:
across 5 seeded circuit-splits, `fit_property_mixture` picked a DIFFERENT k on the two halves
of every split (4v6, 6v2, 4v6, 5v3, 3v4) — the mixture never even agreed on class count.

## How to Inspect the Diff
Worktree `C:/Programs/f1-625` — `git status --porcelain` then `Read` the new files directly
(untracked). Gates 1/2's changes are already approved — review only this gate's slice:
`mixture_stability.py` (new), `scripts/f12_held_out_stability.py` (new),
`tests/unit/physics/layer2/test_mixture_stability.py` (new),
`.agent-work/625-segmentation-substrate/artifacts/f12_holdout_stability.json` (generated
evidence). CONFIRM `src/physics/layer2/property_mixture.py` has ZERO diff from this gate
(`git diff --stat` on that specific file must be empty) — this gate must compose Gate 2, not
modify it.

## Task Statement
Build the mandatory held-out-circuit stability check (launch order pre-ruling #4), including a
discriminating test proving it can fail, then run it for real against
`data/damage_integrals.db` and report the honest verdict — per CONVERGED_PLAN.md Gate 3 and
the full handoff at
`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g3-implement-handoff.md`.

## Close Criteria — THIS IS THE MOST IMPORTANT REVIEW OF THE RUN, READ CAREFULLY
This gate's real-data result is FAIL. Your job is NOT to judge whether FAIL is an acceptable
outcome (it explicitly is, per the launch order's Honest-Null Clause) — your job is to verify
the FAIL is REAL and HONESTLY COMPUTED, not a bug that fabricates a false-negative, and not a
result quietly weakened/adjusted to force a different answer:
1. **The discriminating test is genuine.** Independently confirm (read the test bodies, don't
   trust green) that `test_same_generator_all_circuits_gives_pass` and
   `test_shifted_generator_two_circuits_gives_fail` actually construct DIFFERENT scenarios and
   assert DIFFERENT verdicts — if both tests would pass under either scenario, the
   discriminating claim is hollow.
2. **`F12_AGREEMENT_THRESHOLD=1.0` and the two scale constants were genuinely chosen BEFORE the
   real run**, not reverse-engineered from the FAIL result. Check the module docstring's
   rationale reads as principled-before-the-fact reasoning (domain magnitude), not a
   post-hoc justification tuned to a known outcome. You cannot fully prove "before" from a
   single artifact, but you CAN check: does the stated rationale make sense on its own terms,
   independent of the outcome? Is there any sign the threshold was adjusted after a first run
   (e.g. suspiciously round numbers with no reasoning, or reasoning that only makes sense in
   light of the k-mismatch outcome)?
3. **The k-mismatch-as-automatic-FAIL rule is a legitimate, pre-declared rule**, not an ad-hoc
   excuse invented to explain away a bad result — confirm the handoff itself specified this
   rule (`.agent-work/625-segmentation-substrate/crew-handoffs/g3-implement-handoff.md`,
   `hungarian_match` close criterion: "if the two independently fit mixtures select DIFFERENT
   k... treated as float('inf') / automatic FAIL... document this explicitly") — it was, so
   this is NOT an implementer improvisation, it was specified upstream. Confirm the code
   actually implements it as `float("inf")`, not silently swallowed.
4. **Independently re-run the real-data script yourself** against
   `C:/Programs/f1Brainz/data/damage_integrals.db` (absolute path; NOTE this takes several
   minutes — approximately 5-6 minutes on this machine, do not assume a hang, let it run to
   completion) and confirm you get the IDENTICAL verdict, per-split k_a/k_b values, and circuit
   membership as the committed `f12_holdout_stability.json` — determinism is essential evidence
   here (seeded splits should reproduce byte-identically).
5. Confirm `property_mixture.py` (Gate 2's file) was NOT modified by this gate — the mixture
   fit that produced the k-instability is the SAME fitting logic Gate 2 already had reviewed
   and approved; this gate only composes it differently (per-half fitting across splits), it
   does not change how any single fit works.
6. Confirm the DB was opened read-only (`?mode=ro` URI or equivalent) and never written to.

## Allowed Scope
`src/physics/layer2/mixture_stability.py`, `scripts/f12_held_out_stability.py`,
`tests/unit/physics/layer2/test_mixture_stability.py`,
`.agent-work/625-segmentation-substrate/artifacts/f12_holdout_stability.json`.

## Specific Exclusions
`src/physics/layer2/property_mixture.py` must show ZERO diff. No `circuits.yaml`/production
default changes. No writes to `data/damage_integrals.db`. No
`evo_predictor`/`latent_power`/`compound_prior` imports.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import`.
- `constraint:canonical_data_source`.
- The FAIL verdict is reported exactly as computed — no adjustment.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — new `mixture_stability.py`; real read against
  `data/damage_integrals.db`'s `grip_bin_obs` (absolute path, main checkout, read-only).
- **Capability:** F12 falsifiable gate (mandatory, now EXERCISED with a real FAIL result).
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`,
  `constraint:canonical_data_source`.
- **Decision anchors:** pre-ruling #4 (falsifiable gate mandatory; a FAIL is a complete,
  reportable outcome per the Honest-Null Clause — this is NOT grounds for a BLOCK verdict on
  its own).
- **Evidence expectations:** the discriminating test + the reproducible real-data determinism
  are the two things this review must independently confirm are genuine.

## Evidence Produced
See `C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g3-implement-result.md`
(claimed: 8/8 tests pass; real-data FAIL, n_pass=0/5, k mismatches on every split). This
commander independently reproduced the real-data run once already (6 min, identical verdict)
— you should also independently reproduce it to have your own first-hand evidence, not rely on
either the implementer's or commander's transcript alone. Target postcondition:
`g3-integrate.c1` (test command), `g3-integrate.c2` (this verdict), `g3-integrate.c3`
(artifact existence).

## Suggested Model Tier
Stronger — this is the run's single most consequential verdict; get the genuineness check
right.

## Stop Conditions
Stop and return BLOCK only if: the discriminating test is not actually discriminating, the
threshold/rule was demonstrably chosen AFTER seeing the real result, the real-data run doesn't
reproduce, or `property_mixture.py` was modified. Do NOT return BLOCK merely because the
real-data verdict is FAIL — that is an acceptable, expected-possible outcome per the launch
order.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write it to
`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g3-review-result.md`
before ending your turn, and also return it as your final assistant text response.
