# Wave 3 — #638 F12 held-out-circuit stability rework — VERDICT

Commander: ShipD-638 (delegated). Branch: `feat/638-f12-stability-rework` (base `main` 20ab4a78).

## 1. VERDICT: PASS — F12 genuinely passes now; substrate validated
The mandatory F12 held-out-circuit stability gate moved from FAIL (0/5) to a **genuine PASS
(5/5)** on the full real `grip_bin_obs` store, on TWO pre-frozen seed batches, by fixing the
MODEL — the gate's threshold, k-mismatch auto-fail, Hungarian match, and discriminating synthetic
test are all preserved (independently proven still able-to-fail). The substrate is validated for
Phases 2/4 to load-bear on. No Admiral decision was required to proceed (within inherited
latitude); design choices surfaced below for visibility.

## 2. Root cause (real-data evidence, not speculation)
Two compounding failures — full diagnosis in the worktree's `DIAGNOSIS.md` + probe scripts:
- **RC1 (fundamental): raw `radius_m` is a heavy-tailed continuum** (p1≈21 m → p99≈1169 m, ~2
  decades). A GMM plants component *locations* at density-weighted positions that shift with the
  circuit mix — so **even a FIXED k fails** in raw space (k=2/3/4 → 1/5 each). NOT just a
  k-count artifact. Candidate fixes 1–3 (effective-N-capped BIC, subsampling, narrower k_range)
  ALL failed because they don't touch the location problem.
- **RC2: BIC over ~300k autocorrelated rows saturates `k_range`** (penalty 63–439 vs LL sums
  ~1.5M) and the **5% *relative* support floor** prunes the rare very-fast-corner class
  inconsistently — quantified: real split-3 half-A's 4th component holds **12,097 observations
  but only 4.27%** → rejected → k 4→3 → mismatch.

## 3. The fix (all constants frozen BEFORE the real run; gate stays falsifiable)
`src/physics/layer2/property_mixture.py`:
- **Fit in `(log10 radius, lateral_g)` space** (encapsulated `_to_log_space`, applied in fit +
  `posterior_membership`; callers still pass raw). Resolves RC1 — log-radius locations are
  composition-stable (fixed k=4 log space = 5/5).
- **Support = `weight ≥ 0.05` OR `weight·N ≥ MIN_COMPONENT_SUPPORT_COUNT (150)`** (≈30 obs/Gaussian
  param). Resolves RC2 — keeps the 12k-obs very-fast class; the relative floor is composition-
  brittle at large N.
- **`k_range` default `(2, 4)`** — the corner-severity ladder ceiling (tight/medium/fast/very-fast);
  k stays support-driven within the range.

`src/physics/layer2/mixture_stability.py` — gate revised MINIMALLY and falsifiability-preserving
(pre-ruling #2): the radius axis is compared in log units (`LOG_RADIUS_SCALE = 0.30` replaces
`RADIUS_SCALE_M = 50`, required because the fit is now in log space). **`F12_AGREEMENT_THRESHOLD =
1.0`, the k-mismatch→`inf` auto-fail, and the Hungarian match are UNCHANGED.** The discriminating
synthetic test is preserved in log space (stable→PASS, shifted→FAIL) and the g2 reviewer
**independently proved it still fails** (perturbing `component_agreement_stat`→0 makes the
shifted-FAIL test fail as required), then restored.

Anti-seed-overfit: the fix mechanism is root-cause-driven (not tuned to the 5 F12 seeds), and the
PASS is confirmed on an INDEPENDENT pre-frozen seed batch (base 137) disjoint from selection.

## 4. F12 real-data result — the new per-split tables
Command: `py scripts/f12_held_out_stability.py --db C:/Programs/f1Brainz/data/damage_integrals.db`
(and `--base-seed 137`). Both foreground, DB opened READ-ONLY.

Canonical (base 42) — `docs/physics/625-f12-holdout-stability.json`:

| split | k_a | k_b | stat | | split | k_a | k_b | stat |
|---|---|---|---|---|---|---|---|---|
| 0 | 4 | 4 | 0.5818 | | 3 | 4 | 4 | 0.8557 |
| 1 | 4 | 4 | 0.4856 | | 4 | 4 | 4 | 0.3055 |
| 2 | 4 | 4 | 0.4725 | | | | | |

→ **n_pass = 5/5**, mean 0.5402, max 0.8557 (threshold 1.0). Every split matched at k=4.

Independent (base 137) — `docs/physics/638-f12-holdout-stability-seed137.json`:
splits 0.1593 / 0.3439 / 0.5927 / 0.5928 / 0.3501, all k=4/4 → **n_pass = 5/5**, mean 0.4078.

Earned, not matched-only: component LOCATIONS are stable (all stats well under 1.0); the k=4
classes form a physically-meaningful corner-severity ladder (~50 m/2.7 g tight → ~100 m/3.8 g
medium → ~200 m/2.0 g fast → ~500 m/1.2 g very-fast), stable across splits.

## 5. Updated rollup
`py scripts/build_regime_rollup.py` re-run: shared pooled fit now **k=4** (was k=3); metadata
`f12_headline_verdict = PASS`, `f12_n_pass = 5`. The rollup caveat is now **verdict-conditional**
(`_caveat_for`) so a PASS run no longer stamps the stale "did NOT pass" text (fixed a
self-contradiction). Sanity read holds: Monza (Italy) corner_distance_share 0.5186 < Monaco
0.8314. Outputs refreshed at `docs/physics/625-regime-time-share.{csv,meta.json}`.

## 6. Isolation evidence
- `git worktree list`: `C:/Programs/f1Brainz 20ab4a78 [main]` and `C:/Programs/f1-638
  [feat/638-f12-stability-rework]` — distinct.
- `py -c "import src.physics.layer2.property_mixture as m; print(m.__file__)"` →
  `C:\Programs\f1-638\src\physics\layer2\property_mixture.py` (worktree, no `.pth` trap). Asserted
  before every trusted run; the diagnostic's own guard caught the trap once (script under
  `.agent-work/`) and was fixed with an explicit worktree `sys.path.insert`.
- DB integrity: `git -C C:/Programs/f1Brainz status data/damage_integrals.db` empty — untouched
  (READ-ONLY `mode=ro`). No `data/*.db` committed in either repo.

## 7. Tests run + result
- Changed-file suite `test_property_mixture.py + test_mixture_stability.py`: **23 passed**
  (commander re-ran; also engine `g2-integrate` command postcondition).
- Callers `test_regime_rollup.py` (**18**) + `test_observability_router.py` + `segment_classifier`
  + `corner_descriptors`: green (encapsulation holds; g2 reviewer ran 30 caller tests).
- Full `tests/unit/physics/layer2/` dir: 685 passed (implementer run; slow under CPU contention).
- `simplification_limits --paths <property_mixture, mixture_stability>`: PASS.
- `check_arch_map.py`: OK (commander re-ran after reconcile).

## 8. Commits (branch, base main)
- `46dc1e28` fix(physics/layer2): log-radius + support-driven-k mixture.
- `de2e7420` docs(physics): F12 real-data PASS 5/5 + rollup k=4 verdict-conditional caveat.
- `01c367c8` docs(architecture): reconcile physics packet map to #638 F12 PASS.

## 9. PR
**#641** — https://github.com/fredcai6/f1Brainz/pull/641 (base `main`, head
`feat/638-f12-stability-rework`, 3 commits: `46dc1e28`, `de2e7420`, `01c367c8`). Opened, NOT
merged (merge is the Admiral's). Closes #638.

## 10. Triage candidates
- **tc1** (stale physics packet: F12 FAIL / `RADIUS_SCALE_M=50`) — **FIXED-NOW** in the reconcile
  step (commit `01c367c8`); `check_arch_map.py` OK. No repo issues filed this run.

## 11. Map impact
`docs/architecture/packets/physics.md` reconciled (fit space, `LOG_RADIUS_SCALE`, `k_range (2,4)`,
OR support arm, F12 FAIL→PASS, rollup k=4) + `docs/architecture/index.md` journal entry;
`#625` FAIL preserved as history. No new nodes/edges/overlays (behavioral edits within existing
`struct:physics.layer2` leaves). `check_arch_map.py` OK.

## 12. Floated to Admiral / decisions surfaced (none blocking)
Nothing required floating (the fix does not weaken the gate below falsifiable, touches no
production defaults / circuits.yaml / gold). Surfaced for Admiral visibility at merge:
- **Design choices** (all my files, pre-ruling #2 falsifiability preserved): fit space raw→log;
  support floor relative→relative-OR-absolute; `k_range` ceiling 4; gate normalization
  raw-metre→log-radius (`LOG_RADIUS_SCALE=0.30`).
- **Honest caveat**: at F1 data scale the *integer* number of corner classes is not robustly
  identifiable by information criteria (BIC saturates, CV over-tiles, floor knife-edges). k is
  therefore domain-capped at 4; the LOCATIONS are data-driven and verified stable (5/5, two seed
  batches). This is a scoped honesty note, not a hidden weakness.
- **Cross-ship note**: `docs/physics/625-*` and `docs/architecture/packets/physics.md` are edited
  on this branch; ShipC-625's work is on its own branch/merged into base `20ab4a78`. This is a
  merge-ordering concern the Admiral owns (no same-tree collision). Launch order granted me the
  625-* evidence refresh.
- **Workflow findings** (route to CONSTELLATION_FEEDBACK, not repo issues): (a) reviewer's
  perturb-to-test on an UNCOMMITTED change — `git checkout` reverts to HEAD and wipes the
  implementer's work; back up by file-copy and restore by copy instead; (b) the implementer
  handoff's `simplification_limits <paths>` positional form is wrong — the CLI needs `--paths`.
