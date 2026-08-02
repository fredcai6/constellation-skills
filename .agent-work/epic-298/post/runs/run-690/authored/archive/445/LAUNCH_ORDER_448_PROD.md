# Launch Order: `cmdr-448-prod — issue #448 (REWRITTEN), windowless joint-fusion trajectory estimator + removal of old pathways`

Commanders start cold. Everything you need is pasted here.

## Mission

Productionize the ONE validated trajectory-estimation pathway from epic #445's lab investigation into a tested `src/preprocessing/trajectory/` module, AND remove the dead pathways so no parallel estimation paths remain. This is an explicit REPLACEMENT, per the user. Run the `constellation-commander` skill end to end on the rewritten issue #448 in your assigned worktree.

Read the rewritten issue #448 in full first (`gh issue view 448`) — it is the binding spec. Also read `C:/Programs/f1Brainz/.agent-work/445/PHYSICS_LADDER_FINDINGS.md` (the full E1–E12 ladder + design) before planning.

## Prior-work verdict (pasted — the lab result you are productionizing)

A single **windowless full-stint Matérn-5/2 SDE Kalman-RTS smoother**, fusing raw position + raw speed with one constant inter-stream time offset, is per-sample honest (χ²≈1), speed-honest, geometrically honest, and O(N). Scored at co-estimated REAL sector loops vs official sector times, held-out: ~20 ms median on clean race data (2022 Spain R — under the 50 ms ambition), ~47–50 ms on thin quali data (small-n, not trajectory error). vs rounds 1–2's 550–960 ms. Corner loops are NOT worse. The estimator nests the dense-GP reference (`JointFusion`) to ~mm and self-tests to 1e-10. The chord-cut that plagued rounds 1–3 was a windowing/stitching artifact, gone with the seams. The acceleration state is recovered as a byproduct (Phase 2 input).

## The validated lab code to LIFT (read-only reference — do NOT modify these worktrees)

All on branch `expt/448-e12`, readable in the sibling worktree `C:/Programs/f1Brainz-worktrees/expt-e12/scripts/experiments/`:
- `e10_lib.py` — `StintSmoother` (the windowless Kalman-RTS core: `matern52_sde`, `discretize`, `_block6`, forward/backward, iterated-EKF speed coupling, detrend, sub-sample query nodes; accessors `pos_at/vel_at/acc_at/speed_at`, `pos_predvar/speed_predvar/pos_cov2x2`, `nis_series`, `banded_gap`). **This is the production core.**
- `e11_lib.py` — `NSStintSmoother(StintSmoother)` + `build_roughness` + `driver_series` (state-dependent roughness extension; clean subclass).
- `e12_lib.py` — `fit_line`, `time_residuals`, `line_distance`, `crossing_from_smoother`, `local_kappa_v2`, `resid_stats` (loop geometry co-estimation + crossing scoring; the E5 method is folded in here — loops calibration-free, b=0).
- `e4_lib.py` — `JointFusion` (dense-GP reference, O(N³)): KEEP ONLY as the nesting-equivalence oracle in tests. `enable_cache`, `load_session`, `driver_streams` are the offline loaders.
- `e6_lib.py` — `db_path`, `session_id`, `db_lap_times`, `stint_span`, `driver_num` (DB truth + stint plumbing). NOTE: `tile_windows`/`fit_chain`/`stitched_traj` are the OLD cosine-stitch path — DO NOT port (superseded by the windowless smoother).
- Lab constants you must carry as named config: σ_spd ≈ 0.49 m/s, inter-stream offset ≈ +0.09 s, Matérn-5/2 position / Matérn-3/2 speed substrate, position σ as an ESTIMATED hyperparameter, 0.1 m quantization negligible.

To lift code: `git show expt/448-e12:scripts/experiments/e10_lib.py` or read the sibling worktree path. Port + clean (remove hardcoded `EVID` worktree paths, experiment-only logging), do not copy verbatim with lab cruft.

## Build target (issue #448 §Build) — `src/preprocessing/trajectory/`

`dynamics.py` (SDE + constants), `smoother.py` (`StintSmoother` + `NSStintSmoother`), `calibration.py` (chi²-target hyperparameter fit + cross-driver loop co-estimation), `loaders.py` (offline cache + DB truth, preprocessing side only), `grading.py` (the trust profile: per-class held-out χ², NIS, sector-crossing residual at calibrated loops — REPLACES pass/fail gates), and an on-disk trajectory-product artifact + `docs/report_schemas/` schema. Phase 2/analysis reads the artifact, never the cache.

## Removal target (issue #448 §REMOVE — do this, don't leave parallel paths)

- Delete the old windowed-estimator lineage: `src/preprocessing/windowed_estimator.py`, `windowed_config.py`, `windowed_solver/*`, `trajectory_models.py`, `consensus_stitcher.py`, `docs/physics/windowed_estimator.md`. **Verify no live imports first** (grep src/ and tests/); remove now-orphaned ribbon-only shared utils that nothing else imports.
- Retire `src/preprocessing/trajectory_grading/`: salvage only ribbon-free reused primitives (DB truth loader, offline loader) into the new module; delete the ribbon `sector_anchor`, `strawman_candidate`, pass/fail `cross_residual`, `runner`, `covariance_gate` as superseded by the trust profile.
- Update `docs/architecture/` + any references; `py -m src.utils.simplification_limits` clean on touched paths; confirm no dual estimator paths remain in `src/preprocessing/`.
- PR #468 is already closed by the Admiral — no action needed there.

## The known soft spot (first-class deliverable, not an afterthought)

Hyperparameter calibration (ell, sf, sig_pos) was chosen per-stint by the chi²-target in the lab. Production needs EITHER a robust automatic calibration routine OR a demonstrated fixed/lightly-parameterized set that generalizes across sessions. Build and test this explicitly; document which path you took and the evidence it generalizes.

## Honest-Null / scope clause

This is a build+removal, not an open-ended research task. If lifting reveals the lab code doesn't generalize cleanly (e.g., calibration won't stabilize), STOP and return with the evidence rather than inventing new estimation theory — that would be a scope change to float. Validation breadth (wets, more circuits, pit/in-out-lap filtering) is explicitly OUT of scope here (tracked as a follow-up); ship the validated estimator + clean removal + the clean-race reproduction.

## Inherited Latitude

Yours: module structure within `src/preprocessing/trajectory/`, test design, which orphaned utils to remove (with import-verification), artifact schema details, the calibration approach, branch commits, opening the PR. Float to Admiral (`user-decision`): removing anything OUTSIDE the named dead-pathway list, any change crossing into `src/evo_predictor`/`src/latent_power`/`src/physics` (physics/#449 is a separate issue — do not touch `src/physics/*`), scope changes, merging (Admiral merges), and any discovery that the lab result doesn't reproduce.

## File Ownership / Workspace

- Worktree: `C:/Programs/f1Brainz-worktrees/cmdr-448-prod` (created), branch `issue-448-trajectory-estimator`, base `bd4033a` (current main).
- Findings: `.agent-work/issue-448-prod/` in your worktree. Sole writer. Do not touch `.agent-work/445/` (Admiral's).
- Lab worktrees `C:/Programs/f1Brainz-worktrees/expt-*` are READ-ONLY reference — never modify them.

## Inherited Context (platform invariants)

- Python `py` never `python`; tests `py -m pytest tests/...`; cd worktree root before git/gh.
- Crews via the Agent tool (run_crew.py's CLI launcher is absent); record in crew-runs.json via its registry functions; `recover_crews` before each dispatch; headless `claude -p` crews need piped empty stdin; crews never background long tasks — long compute foreground in you.
- utf-8 child env for captured python subprocesses; engine attach-then-advance for artifact checks; `record` takes `--result`; engine from worktree root; lease re-claim `--force` if stale; heartbeat before long steps.
- Checkpoint AGENT_FEEDBACK entry + lessons-delta at `review`, not `feedback` (a tail-end death stranded them once this epic).
- Physics-region evidence bar: truth-anchored L1–L4, units/bounds/invariants explicit; report-schema changes need producer + committed consumers + schema doc together.
- TURN-ENDING RULE (hard, violated twice this epic): end your final turn ONLY when DONE or BLOCKED; poll long compute in FOREGROUND calls ≤10 min each; NEVER background a long step and end your turn — it strands the run.

## Data Locations (absolute, into the main checkout — not in your worktree)

- FastF1 cache: `C:/Programs/f1Brainz/outputs/cache`
- Season DBs: `C:/Programs/f1Brainz/data/f1_data_<year>.db` (`lap_times`)
- Lab libs to lift: `C:/Programs/f1Brainz-worktrees/expt-e12/scripts/experiments/{e4,e6,e10,e11,e12}_lib.py`
- Lab evidence (for the reproduction target numbers): `C:/Programs/f1Brainz-worktrees/expt-e12/.agent-work/expt-e12/evidence/`

## Budget

Opus commander, Sonnet crews. Heavy build; commit + PUSH after every gate; if a compute/repro step is long, checkpoint resumable.

## Stop Conditions

Stop and return when: a decision outside inherited latitude is needed; the lab result fails to reproduce in the lifted module; removal would touch something outside the named dead-pathway list with live dependents; or scope balloons toward validation-breadth / new estimation theory.

## Return Shape

1. Verdict: module built + old pathways removed + lab gate reproduced / blocked — one paragraph.
2. Evidence: test results (nesting oracle, synthetic gate, honesty checks), the clean-race reproduction number vs ≤50 ms, simplification_limits, the removal diff summary (files deleted, imports verified clean).
3. The calibration-hardening approach + its generalization evidence.
4. PR opened to main (push allowed; do NOT merge); PR number + check status; verdict on issue #448.
5. Map impact; triage candidates (incl. the validation-breadth follow-up); workflow feedback; floated `user-decision`s.
