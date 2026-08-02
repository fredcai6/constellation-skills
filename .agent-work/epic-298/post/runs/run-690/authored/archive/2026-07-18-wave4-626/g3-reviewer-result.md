# Review Result

## Assigned Gate
`g3` — Layer 2: structured within-session evolution (smooth grip latent for track rubbering-in), with honest σ + out-of-sample identifiability test.

## Result
`APPROVE`

## Handoff compliance
All five close criteria independently reproduced (not taken on the implementer's word):
1. **12/12 tests pass**, freshly re-run: `py -m pytest tests/unit/physics/weekend_state/test_layer2_evolution.py -q` → `12 passed in 2.70s`, none skipped (DB present).
2. **LOO harness is genuinely out-of-sample.** Read `loo_earns_keep` (layer2_evolution.py:338-383): per held-out weekend, `b_ctl`/`b_tl` are refit on `train = ident[gp_name != wk]` only, then scored on `test = ident[gp_name == wk]`. `test_loo_folds_are_disjoint_not_self_inclusive` asserts the held-out weekend is never in its own training set, for all 9 folds. I independently re-ran `loo_earns_keep(frame)` live outside the test suite: `n_folds=9, rmse_without_l2=0.82482, rmse_with_l2=0.80368, pct_reduction=2.5634%` — matches the implementer's result doc exactly. This is a genuine disjoint LOO, not self-inclusive (lesson:loo-residual-diagnostic honored).
3. **Orthogonality-vs-season check is real and reported.** Independently re-ran `orthogonality_vs_season(frame)` live: `corr=-1.64e-17, r_squared=2.69e-34` — machine-zero. I traced why: `ctl` is demeaned within `(gp_name, bin)` groups (so it is exactly zero-mean per weekend) while `round_idx` is constant within a weekend — the near-zero correlation is *structurally guaranteed by the demeaning construction*, not a coincidental empirical finding. The module is honest about this ("orthogonal to season-time by construction", docstring line 37) rather than presenting it as a surprising discovery — this is, if anything, a *stronger* guarantee against the F5 season-time-double-count trap than a merely-empirical correlation would be.
4. **The honest-null/FLOAT is reported with real numbers, not hidden or faked.** `EARNS_KEEP_VERDICT` states FLOAT-TO-ADMIRAL with the LOO/orthogonality numbers inline; pinned by `test_verdict_states_float_and_coverage_caveat`. The wide-σ fallback is genuinely mean-0/wide-σ: `apply_track_evolution` (lines 322-335) has exactly two branches — in-coverage (`fit.latent_at` + `fit.sigma[key]`) or the literal `(0.0, fit.wide_sigma)` — no third path, no fabrication. Verified live for both `(2026, "Bahrain")` and `(2023, "Monaco")` (in-2023-year but out-of-store GP): both return `(0.0, 1.2042)`.
5. **The float reasoning is a real architectural limit, not a cop-out.** I independently read `frame.py`'s `KEY_COLUMNS = [year, gp_name, constructor, round_idx]` and queried `physics_estimates.db:session_estimates`'s live schema (`PRAGMA table_info`, 60 columns) myself — confirmed there is genuinely **no** per-car lap-clock / `cumulative_track_laps` column anywhere in that table. The "no bridge" claim is a verified fact, not an assertion taken on faith. And the layer genuinely IS built and fits a real signal: `b_ctl = +0.0019595 g/lap, se=6.90e-5, t=28.4`, reproduced live, positive in all 9 weekends.

One deviation from the handoff's literal ask, judged acceptable: the handoff asked whether removing L2 changes *held-out car-signal noise on g1's frozen split* (via `floor.py`'s metric). The implementer could not run that exact evaluation and instead ran LOO on the grip-fit itself (weekend-level, not car-signal-level). This substitution is explicitly pre-sanctioned by the handoff's own Stop Conditions ("Stop and return a FLOAT ... if ... the 2023-24-only coverage makes held-out evaluation impossible on the frozen split. Report the held-out evidence that led you there.") — the implementer ran the identifiability-level LOO that *is* reachable, reported it, and gave the (independently verified) architectural reason the car-signal-level LOO is *not* reachable.

## Scope drift
None. `git diff --stat` against HEAD is empty (zero tracked files modified) — g1/g2/estimator/evo/config are byte-for-byte untouched. `git status --porcelain --untracked-files=all` shows only the two allowed new files plus `.agent-work/` (review scratch). No Layer 3/4 files exist. The module never imports g1/g2 helpers despite being permitted to — it duplicates a 3-line `_connect_readonly` helper instead (see Code/doc quality); defensible (different DB) and not a scope violation.

## Evidence verdict
All required evidence present and independently reproduced: pytest pass, LOO numbers, orthogonality number, and the explicit earns-keep/float statement with coverage caveat. See Handoff compliance above for the reproduction detail. Test mode was test-after (handoff-sanctioned); implementer reports whole-file RED (ImportError) observed before the module existed, consistent with test-after discipline.

## Code/doc quality
All 6 named handoff constraints independently verified pass (LOO out-of-sample discipline; no fabrication outside coverage; no evo import — grep confirms zero `evo_predictor` references and an import list limited to sqlite3/dataclasses/pathlib/typing/numpy/pandas/scipy; σ explicit everywhere — every `apply_track_evolution` call returns a `(delta, sigma)` tuple, never a bare point; absolute DB path — `DB_PATH = Path("C:/Programs/f1Brainz/data/damage_integrals.db")`, matching g1's established pattern; no `data/*.db` staged or modified).

Fowler refactoring pass run per SKILL.md and recorded to `.agent-work/wave4-626/g3-review/fowler_pass.json`, verified clean by `verify_fowler_pass.py` (exit 0, all 12 baseline smells visited). Findings:
- **long-method** (flagged, non-blocking): `fit_track_evolution` is ~95 lines but stays a single cohesive fitting responsibility.
- **duplicated-code** (flagged, non-blocking, triage candidate): `_connect_readonly` (3-line sqlite `mode=ro` URI helper) is copy-pasted verbatim from g1's `frame.py` rather than shared. Not overridden — no documented repo standard mandates the duplication, only one prior precedent.
- **comments-as-deodorant** (overridden, logged): the long module docstring / `EARNS_KEEP_VERDICT` prose is the handoff's own mandated deliverable ("state coverage limit loudly", "report with held-out numbers"; implementer result: "the numbers are the deliverable as much as the code") — not compensating for unclear code (names/constants are independently clear).
- All other 9 baseline smells: absent.

One minor test-quality nit (non-blocking): `test_apply_2023_but_unseen_gp_falls_back` line 106 asserts `("2023", "Monaco") not in fit.coverage` — a string year compared against `fit.coverage`'s `(int, str)` keys, so it is vacuously true regardless of whether Monaco is actually absent. The functional assertions two lines below (using the correct `int` 2023) still correctly exercise the real fallback behavior, so this doesn't undermine the test's actual coverage — just a dead sanity-check line.

## Map impact verdict
- **Evidence supports claimed change:** Yes — every numeric claim in the Map Impact section was independently reproduced (see Handoff compliance).
- **Constraints not violated:** Yes — all 6 named constraints independently verified.
- **Notes match the diff:** Yes — `layer2_evolution.py` (NEW) is the only structural anchor touched; grep for `layer2_evolution` outside the module+test confirms zero downstream consumers, matching the "not wired" claim (fact, not aspiration).
- **Decision candidates surfaced:** Yes — DC1 correctly surfaces to Admiral as FLOAT rather than being silently resolved either way. This matches Pre-Ruling 2's pre-authorization (build+test+report is frozen authority; concluding "unidentifiable → float" is explicitly sanctioned, not an overreach).
- **Durable context routed:** Yes — three genuine out-of-scope observations correctly routed as triage candidates (below), independently verified as real gaps.

## Reconciliation check
This is a greenfield architecture area — `docs/architecture` has no packet for `physics/weekend_state` yet (MISSION_FRAME.md notes this). The implementer correctly names this gap rather than silently absorbing it; nothing here diverges from recorded architecture in a way needing separate reconciliation beyond what's already flagged as triage.

## Blockers
- none

## Out-of-scope observations
- **Per-car session-time bridge:** `physics_estimates.db:session_estimates` genuinely has no per-car lap-clock/`cumulative_track_laps` field (verified via live `PRAGMA table_info`, 60 columns). Adding one would let L2's field latent become a real per-car Layer-2 correction. Estimator-layer work, out of g1/g2/g3 scope (g1/g2 frozen).
- **`grip_bin_obs` Q coverage is 2023-only** (verified: `SELECT DISTINCT year FROM grip_bin_obs WHERE session_type='Q'` → `{2023}`), narrower than the g3 handoff's stated "2023 and 2024". Future handoffs should spot-check Key-Data-Facts against the live store before asserting them. Backfilling 2022/2024 Q grip bins would widen L2 identifiability toward the 2019-2026 frozen split.
- **Grip-to-axis unit map:** L2's latent is lateral-grip `g` (`mu_lat_p90`), not one of the 11 physics axes. A measured map from grip-evolution to axis-estimate bias would let L2 touch `lateral_mech_grip_g`/`lateral_aero_grip_g` directly. Unmeasured, out of this gate's scope.
- Minor cleanup candidates (non-blocking): duplicated `_connect_readonly` helper vs g1's `frame.py`; the dead string/int comparison line in `test_apply_2023_but_unseen_gp_falls_back`.

## Workflow Feedback
- **Handoff gaps:** the g3 handoff's Key-Data-Fact "grip_bin_obs only covers 2023 and 2024" was wrong (store is 2023-only) — the implementer caught and corrected this before I did, and I independently re-verified it. Worth a standing practice: handoffs that state a store coverage fact should include the verification query used, so both implementer and reviewer can re-run the exact same check instead of re-deriving it.
- **Context rediscovered:** the reasoning for why a FIELD-level (shared-across-cars) latent can only move the car-signal held-out metric via a per-car session-time attachment — not directly — is the entire crux of the FLOAT verdict, and it had to be re-derived from reading `frame.py`'s schema rather than being stated explicitly anywhere in the handoff or MISSION_FRAME. This is the same gap the implementer flagged in their own Workflow Feedback; I confirm it from the reviewer side too.
- **Instructions improvised around:** none — the reviewer skill's engine-drive process (survey + Fowler pass + `verify_fowler_pass.py` rail) applied cleanly to this gate.
- **What would have made this easier:** none beyond the handoff-gap point above — the packet (implementer result + module docstring) was unusually complete and self-verifying, which made independent reproduction fast.

## Return status
`complete`
