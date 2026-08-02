# Reviewer Handoff

## Gate
g2 — Side-by-side braking frontier + decoupled-estimator adapter (review). This review's verdict
and judgment feed the human's retire/wire decision, so the analysis matters as much as the checks.

## What Was Implemented
A reusable decoupled-estimator braking adapter (`src/physics/layer2/decoupled_braking_input.py`),
an `altitude_at_positions` helper in `terrain.py`, and a 6-circuit × VER+PER side-by-side script
comparing **(A) synthesis F_vehicle frontier** (`F_vehicle/m` + θ=0) vs **(B) incumbent**
(`clean_longitudinal_from_raw` a_long + real θ). Report at
`reports/physics/braking_sidebyside_2023Q.{json,md}` (gitignored). Measurement only — no production
view touched. Result: A wins the braking FLOOR (a_b) on 5/6 + better calibration; B wins the
CEILING@80 (via larger b_b) on 4/6. Crew recommends KEEP-for-now, resolve b_b first.

## How to Inspect the Diff
```bash
cd /c/Programs/f1Brainz
git diff HEAD -- src/physics/terrain.py        # the only modified production file (+altitude_at_positions)
git status --short                              # new: decoupled_braking_input.py, 2 test files, the script
git log --oneline -1                            # G1 already committed (c6119bf6); G2 work is uncommitted
```
Full result: `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g2-implement-result.md`.
Report: `reports/physics/braking_sidebyside_2023Q.{json,md}`.

## Task Statement
Build the per-lap decoupled-estimator adapter (terrain-aware, σ-carrying, aligned to classified
samples) and run a side-by-side braking-frontier comparison to produce the deciding numbers +
a retire/keep recommendation. Measurement only.

## Close Criteria
- **Gravity counted exactly once** in BOTH variants — verify the two guard tests
  (`test_double_count_trap_diverges`, `test_variantA_and_variantB_deconflate_equally`) actually
  encode this, and that Variant A feeds `F_vehicle/m` with `theta=0` and Variant B feeds `a_long`
  with real θ. A silent double-count or omission here invalidates the whole comparison.
- **Anchor-source invariant** (`decision:two_cycle_external_anchor_design`): the estimator's soft
  anchor is the TV-denoised RAW `a_long` (from `clean_longitudinal_from_raw`), never re-read from a
  smoothed trajectory. Confirm in the adapter.
- **Apples-to-apples:** A and B use the SAME classified samples (n identical per circuit — verify),
  same priors (`cold_start_braking_supporting`, `GaussianPrior2.cold()`), same circuits/cars.
- **No production view modified** (prepare_braking_frontier / BrakingView.fit / clean_longitudinal_from_raw
  / session_* / EstimateStore / car_prior). Confirm by diff + grep.
- Tests + simplification reproduce: re-run `py -m pytest tests/unit/physics/layer2/ -q` and
  `py -m src.utils.simplification_limits` on the touched paths inline; report real output.

## THE KEY JUDGMENT (spend your effort here — it drives the human's decision)
The crew recommends KEEP (don't retire the incumbent yet) because A's ceiling@80 is lower on 4/6
circuits (B's b_b is systematically larger). **Independently assess whether that is a sound reason
to keep B, or an artifact that production resolves:**

1. **Is B's larger b_b "more correct" or an artifact?** The crew hypothesizes B's local-gradient θ
   removal pushes high-speed decline into b_b (inflating the ceiling), while A's per-sample z-map
   attributes less to downforce. If B's larger b_b is a *terrain-handling artifact* that A fixes,
   then B's "ceiling win" is B being wrong, not better — which would argue FOR adopting A. Assess
   the evidence (the hilly circuits Belgium/Monaco where A's a_b is most above B; the θ_brake ranges).
2. **Does b_b-pinning dissolve the divergence?** `braking_view.py` documents that b_b is meant to be
   PINNED from DragView/cross-session downforce; the production `EstimateStore` is populated by the
   `session_estimator` outer loop (Plan 7) which pins b_b. The side-by-side used cold-start (unpinned)
   b_b. Assess: is comparing two cold-start (unreliable) b_b extrapolations a sound basis to reject A,
   given production pins b_b? Would a pinned-b_b comparison reduce the decision to a_b (where A wins)?
3. **Bottom line for the human:** state your independent view — should we (a) adopt A and verify the
   pinned-b_b ceiling at G3's store repopulation, (b) do an explicit b_b-pinned re-compare in G2
   before deciding, or (c) keep B. Give your reasoning. (You are NOT making the decision — you are
   giving the human a second expert read alongside the implementer's KEEP.)

## Allowed Scope (what the implementation was permitted to touch)
New adapter module + helper in terrain.py + comparison script + 2 test files + gitignored report.

## Specific Exclusions (flag if touched)
Any production view, BrakingView.fit, clean_longitudinal_from_raw, EstimateStore, car_prior — must be unchanged.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import`; `decision:two_cycle_external_anchor_design`.
- Honest per-sample σ carried (not scalar-broadcast).
- `py` not `python`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `decoupled_braking_input.py`, `braking_view.py`, `terrain.py`.
- **Decision anchors:** `decision:smoother_rounds_braking_knee` (the retire caveat), `decision:decoupled_1d_longitudinal` (the wiring this gates).
- **Decision pressure:** retire/keep — your judgment feeds the human's call.

## Evidence Produced
- layer2 suite 197 passed; simplification exit 0 (only pre-existing build_terrain_profile flagged).
- Side-by-side table (in the result + report): a_b (A wins 5/6), ceiling@80 (B wins 4/6), per-circuit.
- Gravity guard tests pass.

## Suggested Model Tier
Stronger (Opus) — the central judgment (b_b/ceiling artifact vs real; pinning) is a physics call that
shapes the human's retire decision.

## Stop Conditions
BLOCK if: gravity is not counted once; the anchor invariant is violated; the comparison is not
apples-to-apples; a production view was touched; tests/simplification do not reproduce.

## Return Format
Return REVIEW_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g2-review-result.md`
with a clear `verdict: APPROVE` or `verdict: BLOCK` line, per-check findings, **your independent
KEEP-vs-ADOPT judgment with reasoning** (the key deliverable), blockers, out-of-scope observations,
and Workflow Feedback. (APPROVE means the side-by-side is sound + the numbers trustworthy — it does
NOT mean "retire"; that is the human's decision, which your judgment informs.)
