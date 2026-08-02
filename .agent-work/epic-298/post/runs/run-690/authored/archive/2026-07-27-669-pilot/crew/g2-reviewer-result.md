# Review Result — g2 (669 pilot pipeline orchestrator)

## Assigned Gate
`g2` (issue #669, epic-659 Wave 5a — 3-circuit end-to-end pilot / tracer bullet)

## Result
`APPROVE`

Independent verification: every load-bearing claim reproduced against the world, not accepted on the implementer's paste. Survey driven through the engine to a consolidated APPROVE (7/7 checks pass, 0 open fails).

## Handoff compliance
PASS. A thin offline orchestrator wires the six landed epic-659 stages (C segment-map → D grip-G → E reference-laps+observables → G fingerprint → H join → PANEL) into ONE per-circuit command. Pure consumer: `src/physics/pilot/pipeline.py` imports+calls landed modules (lazy imports from `src.physics.{segment_map.derivation,layer2,fingerprint,utilization}` + `scripts.*`), reimplements nothing, mints no constant. Deliverables all present and tracked-able: `src/physics/pilot/{__init__,pipeline}.py`, `scripts/run_pilot_669.py`, `scripts/verify_pilot_results_669.py`, `tests/unit/physics/pilot/*`.

## Scope drift
PASS. `git status --porcelain` shows ONLY new untracked files (pilot package, 2 scripts, tests, `.agent-work/`) — ZERO ` M` on any landed stage module (segment_map/layer2/utilization/fingerprint/instrument_panel). The two segment-map paths are tripwired (`two_map_segment_tripwire`), NOT unified. `docs/architecture/*` untouched. PANEL runs in-process `run_panel` (writes nothing); the committed #668 report is untouched.

## Evidence verdict
PASS — all four load-bearing items REPRODUCED by me (pinned interpreter, offline):

1. **GB full-chain offline run** (`run_pilot_669.py --circuits "Great Britain"`): exit 0, ~90s, **provenance=fresh**, all C/D/E/H **PASS**, all 6 slots ran. Verified numbers from `pilot_results.json`:
   - C `n_segments`=41 **==** E live-rederived `e_segment_count`=41 → two-map tripwire **silent** (`flags=[]`)
   - C `median_drift_m`=0.5656 **< 10** (frozen `MAP_STABILITY_DRIFT_M`)
   - E `within_anchor`=True, `positive_control_fired`=True, `n_rows`=24, `map_version`=`2023-Great Britain-Q:v1`
   - D: grip **worsens** (before_rms=0.44 → after_rms=3.20) — the known **#663 null**, correctly a **PASS** (fit ran + score produced), not a false-block.
2. **pytest** `tests/unit/physics/pilot/ -q`: **29 passed, 0 skipped** on Python 3.14.3.
3. **pyright** on the new module + both scripts: **0 errors, 0 warnings, 0 informations**.
4. **verifier** `verify_pilot_results_669.py <results>`: exit **0**.

The four critic-hardening items are REAL + non-vacuous, and (verified via `-rs`, 0 skipped) they actually execute — the fallback DB (53KB) and probe fixture (20KB) are present so no guard silently skips them:
- **(a) fallback/timeout:** `test_timeout_parks_and_stamps_fell_back` raises `TimeoutExpired` in the injected runner → asserts `provenance="fell-back"`, `timed_out=True`, `observables_db==ARCHIVED_FALLBACK`, `n_rows>0`, `"budget"` in reason. Plus non-zero-exit and precise-marker fallthrough parks. Genuinely exercises the auto-park→archived-fallback branch.
- **(b) two-map tripwire:** `test_two_map_tripwire_fires_on_divergence` — `(41,38)` → flag containing "divergence"; `(41,41)` → None. Fails loud on divergence, does NOT unify.
- **(c) non-empty/finite gating:** `gate_observables(0)`→fail; `gate_fingerprint` fails on empty / non-finite mean / all-unresolved / wrong-k; `gate_join_prior([])` and all-thin → fail. All genuinely FAIL on the degenerate fixtures.
- **(d) schema distinctness:** `test_required_slots_and_gates_named_distinctly` — `grip_g` is a distinct slot key from `fingerprint`.

Provenance-inversion fix confirmed: the fresh GB E run stamps `provenance="fresh"` (the benign FastF1 library mention no longer false-matches; `detect_fastf1_fallthrough` keyed to precise store-miss markers, unit-tested both ways).

## Code/doc quality
PASS. Constraints honored, each verified against the run:
- **Offline-only:** gitignored input stores read from absolute MAIN paths (all exist: physics_estimates.db, damage_integrals.db, telemetry_store.db, fp_slice_2023Q.db). E's `--per-year-db` is a **scratch COPY** (`f1_data_2023_scratch.db` under out-dir). **No tracked `data/*.db` dirtied** — `git status data/` empty after the run; the pipeline did NOT cause any ` M data/f1_data_2023.db`. No FastF1 cache touch (provenance=fresh proves the store path resolved offline).
- **Strictly-pre cutoffs:** `as_of_round=round_idx`=circuit round; the pipeline threads it into the fingerprint fit; no race-outcome leakage in the orchestrator.
- **Frozen sets consumed not minted:** `MAP_STABILITY_DRIFT_M` imported from `frozen_constants.py`.
- **grip-G mu=0 one-sided sigma+:** the pipeline does **NOT** point-subtract G; `gate_grip_fit` only reads the harness's held-out reconciliation score (the "subtracting G worsens" verdict is the #663 harness metric, not a pipeline subtraction).
- **Fallback HONESTY:** `_fell_back` stamps `PROV_FELL_BACK` + reason, no silent substitution; a C/D/E/H gating FAIL surfaces machine-broken, not masked.

**Fowler refactoring pass:** 12/12 baseline smells verdicted (rail `verify_fowler_pass.py` exit 0). 0 flagged, 3 overridden — `long-method` (run_circuit ~105-line linear single-level stage sequencing; thin-orchestrator/one-canonical-path standard), `data-clumps` + `long-parameter-list` (year/session_type/round + scratch-path bundle threaded via long keyword-only lists; WIRING-ONLY tracer-bullet defers a context object, each param maps 1:1 to a real landed-stage input). All overrides carry a logged standard + reason. No smell rises to a defect for a tracer bullet.

## Map impact verdict
- **Evidence supports claimed change:** yes — GB run + tests back `capability:pilot-orchestration` and `struct:physics.pilot`.
- **Constraints not violated:** confirmed (offline / reversibility-isolated-db / frozen-consume / strictly-pre) against the actual run.
- **Notes match the diff:** yes — new pilot package + 2 scripts, read-only consumption of landed stages; nothing overstated.
- **Decision candidates surfaced:** the three settled/measured decision anchors (fresh-vs-archived, two-segmap-tripwire, pass-vs-limitation) are exercised exactly as recorded; no new authority needed.
- **Durable context routed:** durable arch map stale-by-design for epic-659 (#671) — no map edit expected; implementer's 3 triage candidates are legit out-of-scope follow-ons.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconcile. The change is purely additive wiring over a map that is stale-by-design for these stages (#671).

## Blockers
- None.

## Out-of-scope observations
- **Report default-path (tc1):** `run_pilot_669.py`'s default `--report-path` writes into `docs/physics/` (a tracked source dir), not under `--out-dir`, so even a scratch run leaves an untracked `docs/physics/pilot_669_report.md`. `pilot_results.json` correctly lands under `--out-dir`. Non-blocking (g3 intentionally writes the committed report there); consider defaulting the report under `--out-dir` for non-g3 runs. (I removed the copy my re-run created so the worktree matches the g2 diff.)
- **g3-hardening (from Fowler overrides):** if the pilot is later hardened into a production orchestrator, a small `PilotContext`/paths dataclass would collapse the `(year, session_type, round)` + scratch-path clump now threaded through the stage functions and shorten the ~16-param `run_stage_e`. Deferred deliberately for the tracer bullet, not a defect.
- **Implementer's 3 triage candidates** (pre-existing dirty DB restore hygiene; `split_half_boundary_drift` latent default-telemetry-store coupling; PANEL instruments 2/3/4 needing cross-circuit official laps → #668/#670) are all valid and correctly out-of-scope here.

Note on the pre-existing dirty DB: the handoff warned of ` M data/f1_data_2023.db` — it is **not present** in `git status` now (Commander appears to have already restored it), and I independently confirmed the pipeline does not write it (scratch-copy approach; `git status data/` empty after my run).

## Workflow Feedback
- **Handoff gaps:** none material — the handoff was unusually complete and its RE-RUN-YOURSELF mandate earned its keep (the provenance-inversion trap is exactly the kind of silent-correctness bug a paste would hide).
- **Context rediscovered:** the critic-#3 negative gating tests live in `test_downstream.py` under a **module-level** `pytest.mark.skipif(not probe_gb.db.exists())`. Those pure-function gating tests don't need the fixture, yet inherit the skip — so on a clean checkout lacking the scratchpad probe fixture they would silently skip and the critic-#3 hardening would go vacuous. Here the fixture is present (they ran, 0 skipped), so it's not a blocker, but the skip-coupling is a latent vacuity risk worth a follow-on (move the pure-decider negatives out from under the fixture skipif).
- **Instructions improvised around:** none — the reviewer skill + engine survey covered the flow cleanly.
- **What would have made this easier:** nothing concrete beyond the skip-coupling note above.

## Return status
`complete`
