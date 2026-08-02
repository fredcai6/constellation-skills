# notes-669 — 3-circuit end-to-end pilot (tracer bullet)

Commander: cmdr-669 (delegated, OPUS). Worktree `epic659-669` @ base main `30cf676d`.
Owner AFK overnight — reversibility is the contract. Float user-decisions to the Admiral (`main`), never the owner.

## Problem statement (reconciled against LAUNCH_ORDER-669.md)

Wire the six LANDED epic-659 stages into ONE invocable pipeline and RUN it on **Monaco / Belgium / Great Britain**
(2023-Q, all on-disk) to prove the MACHINE runs end-to-end before the season-scale bet (#670). This is a
"does-it-RUN" tracer bullet, NOT a signal-sizing study (3 circuits can't size anything → that's #670).

Acceptance (one command, all 3 circuits): valid maps + fitted G with held-out score + populated utilization
observables + smoke-fit fingerprint + panel dry-run, with every C/D/E/H GATING check passing on the slice; a
short report naming anything broken + season-run (#670) implications.

## The six stages (source-verified via Explore, file:line cited in stage map below)

| id | stage | entry point | reads | writes | GATING |
|----|-------|-------------|-------|--------|--------|
| C | segment-map derivation (#662) | `derive_segment_map()` / `scripts/derive_segment_maps.py` | telemetry Parquet mirror + grip_bin substrate + FIA sector lines (f1_data_<year>.db) | `segment_maps.db` (`segment_maps`, PK=map_version) | `scripts/validate_segment_map_662.py`: split-half drift < MAP_STABILITY_DRIFT_M(=10) + typing spot-checks |
| D | Grip G baseline (#663) | `run_grip_batch()` module driver (NO CLI) | f1_data_<year>.db (sessions+lap_times) | `grip_estimates` own-DB | `test_grip_heldout.py` (held-out reconciliation) + `test_grip_synthetic_recovery.py` (separability). Ships mu=0 one-sided sigma+ |
| E | reference-laps + class utilization (#664) | `scripts/build_class_utilization_observables.py` | physics_estimates.db + telemetry (derives C **live** in-process) + optional D grip | own reference-utilization DB: `reference_laps` + `driver_class_observables` | `class_utilization_validation.py` via `--validate`: delete-d jackknife + REQUIRED positive control |
| G | DriverFingerprint (#666) | `fit_driver_fingerprints()` / `scripts/fingerprint_bounded_validation.py` | E's `driver_class_observables` (DB, mode=ro, round<=as_of) | `driver_fingerprint_cells` own-DB | bounded-validation tests (cutoff-leakage no-op, idempotence, k-cells-populated) |
| H | the join (#667) | `join_weekend_prior()` PURE / `scripts/join_bounded_validation_667.py` | E's `reference_laps.time_shares_json` x G cells (in-mem) | in-memory `WeekendUtilizationPrior` + JSON summary | `test_join.py` t7_1..t7_4 reduces-to-simple-case invariants |
| PANEL | instrument panel (#668) | `scripts/instrument_panel_668_report.py` | RAW `driver_class_observables` (un-aggregated) + reference_laps + f1_data_2023.db official laps | `docs/physics/*_report.md/.json` | frozen REPLICATION_* + SECTOR_CALIB_* (sizing, not hard gate) |

## On-disk stores (all on MAIN checkout C:/Programs/f1Brainz)
- `.agent-work/archive/2026-07-26-666-driver-fingerprint/artifacts/fp_slice_2023Q.db` — **THE pilot slice**: Belgium/GB/Monaco/Spain x {LEC,PER,SAI,VER} = 96 `driver_class_observables` + 12 `reference_laps`. Guaranteed-offline fallback for E's outputs.
- `.agent-work/archive/2026-07-26-664-reference-laps/artifacts/reference_utilization_run.db` — GB-only #664 run (join CLI default).
- `data/physics_estimates.db` — full 2023-Q coverage (car ceiling / v_ideal for E).
- `data/physics_fits.db`, `data/telemetry_store_parquet/` mirror, grip substrate (`damage_integrals.db`).
- TRACKED (guard, never write): `data/f1_data_*.db`.

## Wiring seams (from Explore)
- C → nothing upstream (telemetry + grip_bin + FIA sectors).
- D → f1_data DB only (independent of C).
- E ← C (derives map live, NOT via segment_maps.db) + E ← D (optional grip, soft-degrades to None).
- G ← E: reads `driver_class_observables` from a DB table (ro).
- H ← E (reference_laps field fingerprint) + H ← G (cells; pure join takes in-mem Sequence[FingerprintCell]).
- PANEL ← E's RAW observables (NOT G's fitted cells).

**Two SegmentMap production paths exist**: persisted `segment_maps.db` (C's CLI) vs live re-derivation inside E.
Downstream trusts the live one. The pilot should run C's derivation+gating as the "valid maps" deliverable AND
let E re-derive live (what actually feeds G/H) — note the duality; do NOT try to unify (that's out of scope).

## KEY DECISION — re-run C/E from telemetry vs consume archived observables
@grade: guess · settle: feasibility-probe ONE circuit (GB) offline, check load_quali_session reads Parquet mirror not FastF1 + wall-time
- The tracer-bullet purpose ("does the MACHINE run") favors RE-RUNNING C+E from telemetry for the 3 circuits.
- Risk (owner AFK): E's telemetry load may fall through to FastF1 (offline-only violation) or hang (#650/#648 long-compute).
- Mitigation (within latitude, park-on-hang doctrine + report-the-gap): feasibility-probe ONE circuit first. If
  E's telemetry compute is offline-safe + tractable → run all three fresh. If any stage hits FastF1 or hangs →
  PARK it, fall back to the archived `fp_slice_2023Q.db` observables for downstream G/H/PANEL, and REPORT the gap
  + #670 implication. This is the lowest-dimensionality, reversible path; NOT an Admiral float unless the probe
  shows the telemetry compute cannot run offline AT ALL (then the re-run-vs-consume scope genuinely needs a ruling).

## Hard constraints (LAUNCH_ORDER-669)
OFFLINE ONLY (no FastF1); artifacts to ISOLATED scratch/own-DB paths, NEVER tracked f1_data_*.db, NEVER the 38GB
FastF1 cache; `git checkout -- data/f1_data_*.db` if any shows Modified; detached + STATE-NOTE-FIRST before long
stages; park-on-hang; interpreter PIN `.../pythoncore-3.14-64/python.exe`; consume LANDED frozen sets, mint
nothing; strictly-pre cutoffs (no leakage); pyright-0 on new modules; map-fence (notes-669.md + 669-cartography/).

## g1-probe DIAGNOSIS (2026-07-26, offline, scratch DB) — decision:pilot-fresh-vs-archived FIXED

**Verdict: FRESH C/E compute is the DEFAULT path.** All three circuits run offline + tractable; the archived
fp_slice_2023Q.db fallback is retained ONLY as the per-stage timeout/park-on-hang safety net, not the default.
@grade: settled/measured (probe evidence below).

- **Offline-safe: YES.** GB E-stage ran fully offline — telemetry sourced via the `telemetry_store.db` shim, no
  FastF1 network; `src/physics` never imports fastf1 (#503). fastf1 3.8.1 present on the pinned 3.14 interp (soft dep).
- **Store coverage (all on MAIN checkout, read-only):** physics_estimates.db — Monaco r6 / GB r10 / Belgium r12,
  10 ok-status constructor rows each, 2023-Q. telemetry_store.db — 1 session each, 2023-Q. Drivers VER/PER (Red Bull),
  LEC/SAI (Ferrari) available. damage_integrals.db (era mixture) + Parquet mirror present.
- **Wall-time:** GB E-stage, 4 drivers, no --validate = **65s** (reproduced #664 VER +5.625s exactly; segment map C
  ran live inside E: 41 segments, k=4, pooled 272 laps). +~60s with --validate jackknife. Per circuit ~1-2 min;
  full 3-circuit chain est. ~10-20 min. TRACTABLE → DETACH + STATE-NOTE for g3 (not a multi-hour hang).
- **Reversibility:** worktree `data/f1_data_2023.db` WAL-churns when opened as `--per-year-db` → restored via
  `git checkout` (clean). MAIN's dirty `f1_data_2023.db` (mtime 06:56) + race_stint wal/shm (08:19) PREDATE my
  22:53 run — NOT mine (Admiral's earlier verify runs); I do not touch main. Worktree `data/telemetry` FastF1
  cache dir is gitignored + empty (harmless).
- **Entry points:** C gating CLI (validate_segment_map_662) OK; PANEL CLI (instrument_panel_668_report) OK; D grip
  modules (run_grip_batch/fit_session_grip_baseline/get_grip_at) import OK; D/G/H gating tests collect (33). G/H
  bounded-validation CLIs have NON-BLOCKING issues: G (fingerprint_bounded_validation) needs an absolute --slice-db
  (default path unresolved from worktree); H (join_bounded_validation_667) --help throws UnicodeEncodeError on a σ
  (U+03C3) char under Windows cp1252 — fixed by PYTHONIOENCODING=utf-8. In-process cores (fit_driver_fingerprints,
  join_weekend_prior, DriverFingerprintStore, ReferenceUtilizationStore, derive_segment_map) ALL import cleanly.

### g2 IMPLEMENTER design implications (binding)
1. Gitignored input stores → absolute MAIN paths (physics_estimates.db, telemetry_store.db, damage_integrals.db).
2. Tracked --per-year-db → COPY the worktree f1_data_2023.db to scratch ONCE and point there (fully avoids dirtying
   any tracked file); else point at the worktree copy and `git checkout` after each run.
3. Set PYTHONIOENCODING=utf-8 on any subprocess (σ chars in stage output break cp1252 stdout).
4. Call G/H via in-process cores (fit_driver_fingerprints / join_weekend_prior), NOT the bounded-validation CLIs.
   Invoke E via its CLI as a SUBPROCESS with a wall-time timeout (~180s, ~2x the 65s+validate) so a hang auto-parks
   → archived fp_slice fallback for downstream G/H/PANEL. D grip via run_grip_batch (subprocess or in-process).
5. FastF1 cache dir defaults to worktree data/telemetry (gitignored) — leave or set to scratch.
