# Reviewer Handoff

## Gate
g3 — Wire braking + terrain scoreboard handle + repopulate store (review). Production wiring gate;
the C1 re-eval (G4) builds on the repopulated store, so the wiring + store correctness matter.

## What Was Implemented
`prepare_braking_frontier` rewired to the decoupled adapter (`a_long = F_vehicle/m`, `theta=0`,
`sigma_kin = per-sample sigma_a`); `clean_longitudinal_from_raw` retired as the DIRECT braking input
(NOT deleted — still the adapter's raw anchor + #498 refine + throttle/coast); `scoreboard.CaseInputs`
got an optional `theta`/`z` terrain handle (additive). A NEW store `data/physics_estimates_g3wired.db`
was repopulated (RBR r1-15 wired, seeded from a copy of OLD so full causal history is preserved; OLD
`data/physics_estimates.db` untouched). Pinned-ceiling verified sensible. Other 4 C1 constructors =
flagged continuation. Return status: `partial` (wiring complete + RBR store verified; other-4 continuation).

## How to Inspect the Diff
```bash
cd /c/Programs/f1Brainz
git status --short
git diff HEAD -- src/physics/layer2/session_braking.py src/physics/layer2/scoreboard.py
git diff HEAD --stat
# new: scripts/repopulate_g3wired_store.py, scripts/compare_g3wired_braking.py,
#      tests/unit/physics/layer2/test_session_braking_wired.py
# G1+G2 already committed; G3 work uncommitted.
```
Full result: `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g3-implement-result.md`.

## Task Statement
Wire the adapter as the one canonical braking input (gravity once, per-sample σ), retire the raw-speed
direct braking read, add the scoreboard terrain handle, repopulate the store (apples-to-apples with
#510), and verify the downforce-pinned ceiling is sensible.

## Close Criteria (each a review check)
- **One canonical braking input:** `prepare_braking_frontier` uses ONLY the adapter for the frontier
  `a_long`; no dual/flagged path; `clean_longitudinal_from_raw` no longer the direct braking-frontier
  read (but PRESENT for the adapter anchor + #498 refine + throttle/coast — confirm it is not deleted
  and those uses remain).
- **Gravity counted exactly once:** Variant A — `a_long = F_vehicle/m` fed with `theta = zeros`, so
  BrakingView's `-g sin(theta)` is identically zero. Confirm no double-subtraction and no omission.
- **Per-sample σ propagated:** `sigma_kin` is the adapter's per-sample `sigma_a`, not a broadcast scalar.
- **Scoreboard terrain handle additive:** `CaseInputs` terrain is optional; FLAT cases byte-identical
  when no terrain supplied (verify the 4 new terrain tests + that existing scoreboard tests unchanged).
- **Store correctness:** NEW store seeded from a COPY of OLD; OLD preserved (verify byte-identical /
  RBR r16-22 == OLD); RBR r1-15 carry the wired braking with FULL causal history (n_sessions_causal
  matches #510: 6/10/14/15 at Monaco/GB/Italy/Singapore). The schema migration is in the repop script
  only (estimate_store.py untouched).
- **Pinned-ceiling verification sound:** inspect `scripts/compare_g3wired_braking.py` output — `b_b>=0`
  all rounds, `a_brake(80)>0`, cold→pinned gap does NOT inflate (mean −0.59), and the a_b↔b_b trade-off
  on Miami/Spain is a high-speed-ceiling RISE not an under-call. Confirm the claim is supported.
- **No excluded code touched:** `session_traction.py`, `session_coast.py`, `car_prior`, the dashboard,
  `docs/architecture/**` UNMODIFIED. `clean_longitudinal_from_raw` NOT deleted. Confirm by diff + grep.
- **Tests reproduce:** re-run `py -m pytest tests/unit/physics/layer2/ tests/unit/physics/ -q` and
  `py -m src.utils.simplification_limits` on the touched paths inline; report real output.
- **Partial-close acceptability:** confirm the RBR-only store + the bounded, reproducible other-4
  continuation (`py scripts/repopulate_g3wired_store.py`) is an acceptable gate close (wiring intent
  fully delivered; continuation captured as triage). Flag if you disagree.

## Allowed Scope (what the implementation was permitted to touch)
session_braking.py, scoreboard.py (additive), decoupled_braking_input.py, estimate_batch/store/session_estimator
as needed, new repop+compare scripts, layer2 tests, gitignored reports + the new store.

## Specific Exclusions (flag if touched)
session_traction/session_coast, car_prior, dashboard, utilization layer, docs/architecture/**;
clean_longitudinal_from_raw must not be deleted.

## Constraints
- One canonical braking path; gravity once; honest per-sample σ.
- `constraint:physics_region_no_evo_import`; `decision:two_cycle_external_anchor_design` (anchor = TV-denoised RAW a_long).
- `py` not `python`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `session_braking.py`, `decoupled_braking_input.py`, `scoreboard.py`, `estimate_store.py`.
- **Capability:** per-car braking capability ceiling — recalibrated via the repopulated store.
- **Decision anchors:** `decision:decoupled_1d_longitudinal` (→ wired, 1 importer now), `decision:smoother_rounds_braking_knee` (retire caveat resolved). NOTE: the implementer correctly FLAGGED these MEASURED→wired updates for reconcile rather than editing docs/architecture — verify it did not edit the map.
- **Evidence:** wired knee deep (matches G2 synthesis); pinned ceiling sensible; store reproducible.

## Evidence Produced
- Full suite 592 passed / 6 skips; touched-path simplification PASS.
- Wired-knee spot check Monaco RBR a_b=26.61 (vs OLD 26.11, G2 synth 26.74).
- Store: RBR r1-15 wired (15 fitted, 0 errors), OLD preserved, deterministic (Monaco reproduced 3×).
- Pinned-ceiling: sensible, not under-calling (b_b≥0, cold→pin gap −0.59, Miami/Spain high-speed ceiling rises).

## Suggested Model Tier
Bounded (Sonnet) — the wiring checks are mechanical (diff/grep/test re-run) and the pinned-ceiling
soundness is checkable against the compare-script output; escalate only if the gravity-once or
store-correctness check is ambiguous.

## Stop Conditions
BLOCK if: gravity is not counted once; a dual braking input remains; per-sample σ is dropped; an
excluded file was touched; `clean_longitudinal_from_raw` was deleted; the OLD store was mutated; the
store is not apples-to-apples (causal history); tests/simplification do not reproduce; the pinned-ceiling
claim is not supported by the compare-script numbers.

## Return Format
Return REVIEW_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g3-review-result.md`
with a clear `verdict: APPROVE` or `verdict: BLOCK`, per-check findings, an explicit note on whether
the partial (RBR + continuation) close is acceptable, blockers, out-of-scope observations, and Workflow Feedback.
