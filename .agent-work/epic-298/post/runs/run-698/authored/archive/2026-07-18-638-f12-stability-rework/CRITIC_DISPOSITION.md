# Cold-critic disposition — #638 gate plan (commander-triaged, delegated; cite LAUNCH_ORDER)

Single cold critic (panel scaling recorded in PLAN_ALTERNATIVES.md). All findings triaged
before the plan freezes.

1. **[BLOCKING] Circularity / seed-overfit** — ACCEPTED, strengthen. The fix must be chosen on a
   PRINCIPLED root-cause mechanism (e.g. effective-N-corrected selection), NOT by tuning knobs to
   the specific 5 seeds F12 uses. G3 now confirms the PASS on the canonical seeds (base 42) AND a
   PRE-FROZEN independent second seed batch (base 137), both n_pass=5/5 — declared here, before
   any post-fix real run. Added to G1 c2 (mechanism-driven) and G3 c1 (dual-seed).
2. **[BLOCKING] .pth worktree trap on G3 real run** — ACCEPTED. G3 asserts the imported
   `property_mixture.__file__` is under C:/Programs/f1-638 before trusting the run (the f12 script
   already inserts the worktree root at sys.path[0], but assert it). Added to G3.
3. **[BLOCKING] Model-collapse / minimal-agreement hack (blunt k_range narrowing)** — ACCEPTED.
   G1 must show the chosen fix addresses the ROOT CAUSE and the resulting classes stay physically
   adequate (report component centroids in raw radius_m/lateral_g; the universal corner-type
   classes must remain physically meaningful, not collapsed to uselessly-coarse). Prefer a
   root-cause fix over blunt k_range narrowing. Added to G1 c2.
4. **[SHOULD-FIX] "k support-driven" only eyeballed** — ACCEPTED. G2 adds a mechanical synthetic
   test: k RESPONDS UPWARD to a genuine well-supported added cluster (and down with fewer) —
   mechanizing pre-ruling #1 so a k-pinned-in-all-but-name fix fails CI.
5. **[SHOULD-FIX] G3 c1 grep weaker than criterion** — ACCEPTED. headline PASS ⟺ n_pass==n_splits
   by construction, but strengthen anyway: assert `"n_pass": 5` on both seed batches.
6. **[SHOULD-FIX] Pin foreground timeout** — ACCEPTED. G3 real runs use Bash timeout 600000 ms.
7. **[SHOULD-FIX] cross-repo `git checkout -- data/`** — ACCEPTED. Scripts open the DB READ-ONLY
   (mode=ro URI, cannot write), but cleanup/`no-data-staged` runs against the MAIN repo
   C:/Programs/f1Brainz, not the worktree. Added to G3.
8. **[SHOULD-FIX] cross-ship contention docs/physics/625-*** — NOTED for Admiral. I edit on branch
   feat/638; ShipC-625's work is on its own branch/merged to main base 20ab4a78. This is a
   merge-ordering concern the Admiral owns, not a same-tree write collision. Flagged in verdict;
   I'll sanity-check git state at G3. Launch order explicitly grants me the 625-* evidence refresh.
9. **[NIT] downstream fit sanity** — ACCEPTED-light. G3 rollup re-run reports the Monza<Monaco
   corner-share sanity read (already the 625 writeup's sanity anchor).
10. **[NIT] scripts unscoped in G2** — ACCEPTED-light. G2 scope widened: MAY edit
    scripts/f12_held_out_stability.py / build_regime_rollup.py IF the fix needs a param plumbed
    (default-valued so callers are unaffected). If the fix is a pure change to
    fit_property_mixture's default behavior, scripts need no edit.

## Pre-frozen confirmation seed batch (declared BEFORE any post-fix real-data run)
- Canonical F12 batch: base_seed=42, n_splits=5 (unchanged, the gate's own default).
- Independent confirmation batch: base_seed=137, n_splits=5. Both must be n_pass=5/5 for a
  genuine PASS. These constants are frozen here and NOT to be changed after seeing any result.
