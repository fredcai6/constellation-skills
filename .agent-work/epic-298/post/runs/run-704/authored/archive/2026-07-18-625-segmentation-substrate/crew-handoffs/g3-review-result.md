# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3 (execute.json: g3-review)` — F12 mandatory falsifiable gate: held-out-circuit
class-membership stability

## Result
`APPROVE`

## Handoff compliance
All close criteria from `g3-implement-handoff.md` independently verified against the actual
diff/new files and against a fresh, independent re-run — not the transcript alone:
- `src/physics/layer2/mixture_stability.py` implements `hungarian_match` (scipy
  `linear_sum_assignment` over pairwise Euclidean distance), `component_agreement_stat`
  (resolution (b): inverse-transforms each fit's standardized `gmm.means_` back to raw
  `(radius_m, lateral_g)` via that fit's own `scaler`, normalizes by `RADIUS_SCALE_M`/
  `LATERAL_G_SCALE`, Hungarian-matches, returns mean matched distance; `float("inf")` on
  `k`-mismatch), `SplitResult`/`StabilityResult` dataclasses, `check_holdout_stability` (5
  seeded 50/50 circuit-NAME splits, `base_seed+i`, deterministic `np.random.default_rng`
  shuffle, pools rows, fits Gate 2's `fit_property_mixture` independently on each half).
- `scripts/f12_held_out_stability.py`: read-only URI connection to the real DB, loads
  `grip_bin_obs`, groups by `gp_name`, applies Gate 1's `descriptors_from_frame`, runs
  `check_holdout_stability`, writes the full JSON artifact + one-line stdout summary. **Run for
  real**, twice by the implementer and once more independently by this review — all three runs
  produced the byte-identical FAIL verdict.
- The real-data verdict is reported exactly as computed: **FAIL**, `n_pass=0/5` — every one of
  the 5 seeded splits hit a `k`-mismatch (4v6, 6v2, 4v6, 5v3, 3v4), so `component_agreement_stat`
  never even reached the distance-threshold comparison. No adjustment, no re-run to flip it.

## Scope drift
None. `git status --porcelain` shows exactly this gate's 3 new files
(`mixture_stability.py`, `scripts/f12_held_out_stability.py`,
`tests/unit/physics/layer2/test_mixture_stability.py`) plus the untracked
`.agent-work/625-segmentation-substrate/` tree (including the generated JSON artifact) —
nothing outside allowed scope. `property_mixture.py`'s content was read in full and matches
`g2-review-result.md`'s already-approved description exactly; file-mtime evidence places it
strictly inside Gate 2's work window (21:49:59 -07:00) and strictly before Gate 3's (earliest
g3 file: 22:12:58) — it was not touched during this gate's work. `evo_predictor`/
`latent_power`/`compound_prior` grep across all 3 new files: zero matches. No
`circuits.yaml`/production-default touched. No writes to `data/damage_integrals.db` (verified
independently — see Evidence verdict).

## Evidence verdict
Required evidence present and independently reproduced, not merely trusted from the transcript:
- Confirmed worktree resolution first (`py -c "import
  src.physics.layer2.mixture_stability as m; print(m.__file__)"` → prints the path under
  `C:\Programs\f1-625`, not the main checkout — the editable-install `.pth` trap does not
  apply here).
- `py -m pytest tests/unit/physics/layer2/test_mixture_stability.py -v` → 8/8 passed, identical
  test IDs/order to `g3-implement-result.md`'s transcript, including both discriminating-test
  scenarios by name.
- `py scripts/f12_held_out_stability.py --db C:/Programs/f1Brainz/data/damage_integrals.db`
  run independently by this review (backgrounded by the harness past its 120s foreground
  limit, polled to completion — actual runtime ≈5m26s, matching the handoff's stated 5-6min
  expectation). The freshly produced `f12_holdout_stability.json` was diffed field-by-field
  against the already-committed artifact (excluding only `timestamp_utc`) — **byte-for-byte
  IDENTICAL**: same `headline_verdict` FAIL, same `n_pass=0/5`, same per-split `k_a`/`k_b`
  (4v6, 6v2, 4v6, 5v3, 3v4), same circuit membership per half of every split, same row counts.
  This is strong determinism evidence — the seeded splits reproduce exactly.
- Read-only DB claim independently re-verified: a fresh `CREATE TABLE` attempt against
  `file:...?mode=ro` correctly raises `sqlite3.OperationalError: attempt to write a readonly
  database`.
- `py -m src.utils.simplification_limits --paths` on all 3 new files → `PASS (3 files
  checked)`, matching the implementer's claim.

## Code/doc quality
Minimal, maintainable, tested, project-rule compliant. No `print()` in the library module
(grep-clean); `print()` confined to the CLI script as CREW_CONTEXT.md permits. Module-level
state is 3 immutable float constants only, no mutable state, no DB singleton. Units explicit
throughout (`radius_m`, `lateral_g` documented at every boundary). Not a new physics model —
a statistical validation gate composing Gate 2's already-approved fit — so CREW_CONTEXT's
L1-L4 truth-anchored-test requirement for physics model changes does not apply; the
discriminating test is the correct analogous rigor for a validation gate, and it is genuinely
discriminating (see Genuineness Verification below).

Fowler code-smell pass (`r6-fowler`, recorded to `.agent-work/625-segmentation-substrate/
g3-review/g3-fowler-pass.json`, `scripts/verify_fowler_pass.py` exit 0): 12/12 baseline smells
absent, no overrides needed. Notable judgment call: `feature-envy` on
`component_agreement_stat`'s deep reach into `fit_a.scaler`/`fit_a.gmm.means_`/`fit_a.k` was
judged absent (not flagged) — it is a legitimate two-object comparator function over a
deliberately data-only `MixtureFit` DTO (Gate 2's own documented design), consistent with this
codebase's pure-function-over-data-record style used throughout `layer2/`.

## Genuineness Verification (the core of this review — handoff's 6-point close criteria)
This is the run's single most consequential verdict, so each point was independently checked
against source and against a fresh re-run, not accepted from the transcript:

1. **Discriminating test is genuine.** `test_same_generator_all_circuits_gives_pass` uses 12
   synthetic circuits ALL drawing from the identical 2-blob generator (different random draws
   only) → asserts `headline_verdict == "PASS"`, `n_pass == n_splits == 5`.
   `test_shifted_generator_two_circuits_gives_fail` uses exactly 2 circuit names from
   generators shifted by 20× each scale constant (1000m radius / 10g lateral-g) — with only 2
   names, the 50/50 split ALWAYS puts exactly one full circuit per half on every seed,
   deterministically guaranteeing separation regardless of shuffle order → asserts
   `headline_verdict == "FAIL"`, `n_pass == 0`, `max_statistic > threshold`. These are
   genuinely different constructions with different assertions; neither would pass under the
   other's scenario — the discriminating claim is not hollow.
2. **Threshold/scales chosen before the real run.** The module docstring's rationale is pure
   domain-magnitude reasoning (a tight hairpin ~15-25m vs a medium corner ~60-90m for
   `RADIUS_SCALE_M`; ~1.0g vs ~2.0g+ for `LATERAL_G_SCALE`), with no reference to
   `grip_bin_obs` data anywhere in the text. Corroborated independently via file-mtime
   evidence: `mixture_stability.py` was last modified 2026-07-17 22:14:12 -07:00 and has NOT
   been touched since (confirmed its mtime is unchanged after this review's own re-runs); BOTH
   real-data runs happened strictly after that write (the implementer's first transcript run
   at 22:29:59 -07:00, the committed artifact's run at 23:16:39 -07:00) — the constants could
   not have been reverse-engineered from a result that did not exist yet when the file was
   last written, and stayed frozen and unchanged across both of those runs (which
   independently reproduced the identical verdict).
3. **k-mismatch-as-automatic-FAIL is a legitimate, pre-declared rule.**
   `g3-implement-handoff.md`'s `hungarian_match` close criterion states this verbatim before
   any implementation existed — upstream Commander authority, not implementer improvisation.
   The code implements it exactly as `float("inf")` on the first line of
   `component_agreement_stat`, never swallowed — it propagates cleanly through
   `SplitResult.statistic`, `StabilityResult.mean_statistic`/`max_statistic` (`np.mean`/
   `np.max` correctly propagate `inf`), and `passed = statistic < threshold` correctly
   evaluates `False`.
4. **Real-data run independently reproduced.** See Evidence verdict above — byte-for-byte
   identical verdict, per-split `k_a`/`k_b`, and circuit membership across three independent
   runs (implementer ×2, this review ×1).
5. **`property_mixture.py` zero diff confirmed.** Content read in full and matches
   `g2-review-result.md`'s already-approved description exactly; mtime evidence places it
   strictly inside Gate 2's window and before Gate 3's earliest file.
6. **DB opened read-only, never written.** Independently re-verified — a write attempt against
   the `mode=ro` URI is rejected at the SQLite driver level.

All 6 points hold. No evidence of fabrication, post-hoc threshold/rule tuning, or rule-swallowing
was found anywhere in this diff.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in `g3-implement-result.md`'s Map
  Impact section was independently checked against source/re-run and holds.
- **Constraints not violated:** yes — `constraint:physics_region_no_evo_import` (grep-clean)
  and `constraint:canonical_data_source` (read-only absolute-path DB access, no FastF1 call)
  both independently confirmed.
- **Notes match the diff:** yes — structural (`struct:physics.layer2`) and capability (F12
  gate, now exercised) anchors match exactly what changed; no overstated or missing impact.
- **Decision candidates surfaced:** yes — the cross-fit-standardization resolution ((a) vs (b))
  and the exact threshold/scale values were genuinely within the handoff's own delegated
  latitude, both documented; no undisclosed decision requiring authority beyond what was
  already delegated.
- **Durable context routed:** two triage candidates flagged this review (not dropped): `tc1`
  (CONVERGED_PLAN.md's terser Gate-3 wording vs the handoff's more detailed (a)/(b) resolution
  — a one-line reconciliation edit candidate) and `tc2` (the FAIL verdict itself needs
  Commander/Cartographer disposition before Gate 2's mixture is trusted by any downstream
  caller, e.g. Gate 4's rollup).

## Reconciliation check
No divergence from `CONVERGED_PLAN.md` Gate 3 requiring a BLOCK. The mandatory F12 gate was
built and run exactly per plan (5 seeded splits per cold-critic disposition #3, new module in
`layer2/`, genuine discriminating test). The FAIL verdict is an accepted, complete outcome per
the launch order's Honest-Null Clause and pre-ruling #4 — not grounds for BLOCK on its own, and
this review's job was to verify the FAIL is honestly computed (confirmed), not to judge whether
FAIL is acceptable (it explicitly is).

## Blockers
- none

## Out-of-scope observations
- (`tc1`) `CONVERGED_PLAN.md`'s Gate-3 summary line ("mean Euclidean distance between matched
  STANDARDIZED component means") is terser than, and could be misread against, the resolution
  actually chosen ((b), raw-unit inverse-transform) — a one-line CONVERGED_PLAN reconciliation
  edit would prevent a future reader from assuming resolution (a).
- (`tc2`) The real-data FAIL (k-instability across all 5 splits, never even reaching the
  distance-threshold comparison) needs disposition before Gate 2's soft-membership property
  mixture is treated as reliable for Gate 4's rollup or any other downstream caller — candidate
  follow-up: root-cause whether `k_range=(2,6)`'s BIC selection is oversensitive to
  circuit-composition at ~300k-row half-pool scale, or whether the support-floor/selection rule
  itself needs revision. Diagnosing/fixing this was explicitly out of this gate's scope (its job
  was to build and honestly run the check).

## Workflow Feedback
- **Handoff gaps:** none material. The handoff's 6-point genuineness checklist was unusually
  precise and made independent verification straightforward — each point named exactly what
  evidence would settle it (test-body construction, docstring rationale sanity, upstream
  handoff citation, reproducibility, diff-emptiness, read-only connection).
- **Context rediscovered:** the file-mtime cross-check (module frozen at 22:14:12, both real
  runs strictly after) was not suggested anywhere in the handoff but turned out to be strong,
  cheap corroborating evidence for "chosen before the real run" beyond just reading the
  docstring's self-declaration — worth naming explicitly as a technique in a future version of
  this close-criterion wording ("check file mtimes place the module's last edit before every
  real-data run timestamp") since it upgrades a self-report into an independently-checkable
  fact.
- **Instructions improvised around:** none. The reviewer skill's engine-drive workflow and the
  Fowler-pass rail both applied cleanly; the appended `r7-genuineness` item was a natural fit
  for the handoff's numbered close-criteria list (survey `append` is exactly the right verb for
  a gate-specific check beyond the generic r0-r6 template).
- **What would have made this easier:** none — the handoff, `g3-implement-handoff.md`, and
  `g3-implement-result.md` together gave a complete, self-consistent evidence trail; nothing had
  to be rediscovered from scratch beyond the mtime cross-check noted above.

## Return status
`complete`
