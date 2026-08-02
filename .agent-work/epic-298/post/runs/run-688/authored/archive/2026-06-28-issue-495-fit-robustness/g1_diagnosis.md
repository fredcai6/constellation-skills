# G1 Diagnosis — #495 Physics Fit Robustness (evidence-only)

**Gate:** g1 (`execute.json` `g1-implement`) — EVIDENCE-ONLY, no `src/` changes.
**Checkout:** `C:/Programs/f1Brainz`, branch `fix/495-fit-robustness`, HEAD `bac0e96b` (post-PR #548; #548 = commit `1c501ccf`/`52fe677b`).
**Data:** telemetry store `data/telemetry_store.db` (store-first source; all 11 affected 2023-Q GPs present), OLD fit store `data/physics_fits.db` (built 2026-06-23, pre-#548).
**Repro method:** `load_quali_session(year, gp, "Q")` + `fit_driver(...)` per case (the natural per-case unit). `fit_session_full` is NOT a batch looper — see Workflow Feedback. Probes + raw logs under `.agent-work/issue-495-fit-robustness/`.

---

## 1. Headline

PR #548 already fixed **18 of the 19** OLD-store failing cases. Re-run on current code:

| outcome | count | cases |
|---|---|---|
| **already-fixed → `ok`** | 17 | all 3 NoneType (Bahrain ALO/HAM, Canada HUL) + 14 of 15 interleaved |
| **already-clean typed-skip → `no_laps`** | 1 | Japan SAR (still a clean typed skip, confirmed) |
| **still raises (recorded as `error`)** | 1 | **Saudi Arabia DEV** — NEW failure mode (not the old `interleaved n=0`) |

**Current failure counts (2023-Q, the 19 cases): 1 `error` + 1 `no_laps`.** Only **one** genuine bug remains: Saudi Arabia DEV, which must become a clean typed-skip (genuinely unfittable — no speed stream).

---

## 2. Per-case classification table

Raw transcript: `repro_output.log`. (`n_fly` = flying laps used, `n_samp` = samples used.)

| GP | DRV | OLD status / pattern | CURRENT status | n_fly | n_samp | CURRENT error | classification |
|---|---|---|---|---|---|---|---|
| Japan | PIA | error / interleaved | **ok** | 4 | 1393 | — | already-fixed-ok |
| Japan | NOR | error / interleaved | **ok** | 4 | 1391 | — | already-fixed-ok |
| Japan | LEC | error / interleaved | **ok** | 4 | 1390 | — | already-fixed-ok |
| Japan | SAI | error / interleaved | **ok** | 4 | 1395 | — | already-fixed-ok |
| Japan | MAG | error / interleaved | **ok** | 3 | 1051 | — | already-fixed-ok |
| Netherlands | SAR | error / interleaved | **ok** | 8 | 2492 | — | already-fixed-ok |
| Mexico | ZHO | error / interleaved | **ok** | 5 | 1498 | — | already-fixed-ok |
| Brazil | PIA | error / interleaved | **ok** | 3 | 827 | — | already-fixed-ok |
| Las Vegas | BOT | error / interleaved | **ok** | 6 | 2200 | — | already-fixed-ok |
| Abu Dhabi | VER | error / interleaved | **ok** | 5 | 1645 | — | already-fixed-ok |
| Saudi Arabia | DEV | error / interleaved | **error** | 0 | 0 | `zero-size array to reduction operation minimum which has no identity` | **still-raises-exception → genuinely-unfittable (no speed stream)** |
| Azerbaijan | GAS | error / interleaved | **ok** | 1 | 412 | — | already-fixed-ok |
| Azerbaijan | DEV | error / interleaved | **ok** | 1 | 450 | — | already-fixed-ok |
| Miami | BOT | error / interleaved | **ok** | 5 | 1749 | — | already-fixed-ok |
| Canada | ALB | error / interleaved | **ok** | 8 | 2558 | — | already-fixed-ok |
| Bahrain | ALO | error / NoneType | **ok** | 5 | 1796 | — | already-fixed-ok |
| Bahrain | HAM | error / NoneType | **ok** | 5 | 1789 | — | already-fixed-ok |
| Canada | HUL | error / NoneType | **ok** | 8 | 2591 | — | already-fixed-ok |
| Japan | SAR | no_laps / — | **no_laps** | 0 | 0 | — | already-clean-typed-skip |

---

## 3. NoneType cases — root cause with real traceback

Probe: `probe_nonetype.py`; raw log: `nonetype_output.log`. **All 3 NoneType cases now return `ok` on `main`** — the bug is fixed. But the original root cause, traced faithfully:

### Exact pre-#548 None-origin line
`src/preprocessing/trajectory/calibration.py:861` (in commit `52fe677b^`, the pre-#548 tree):
```python
hp = fit_stint_hp(tp, yX, yY, tc, yV, delta=delta, iters=3, order=order)
iso = StintSmoother(hp["ell"], hp["sf"], hp["sig_pos"], delta, ...)   # line 861 — subscripts None
```
When `fit_stint_hp` returned `None`, `hp["ell"]` raised `TypeError: 'NoneType' object is not subscriptable`. Reproduced traceback (replaying the OLD full-span path via current public seams):
```
File ".../probe_nonetype.py", line 76, in main
    _ = hp_dict["ell"]   # reproduces pre-548 calibration.py:861 subscript
TypeError: 'NoneType' object is not subscriptable
```

### Why `fit_stint_hp` returned None (the upstream producer)
NOT emptiness. For all 3 cases the full stint window holds ample data:

| case | stint span | n_pos in window | n_spd in window |
|---|---|---|---|
| Bahrain ALO | 987.9s | 3819 | 1367 |
| Bahrain HAM | 991.0s | 3828 | 1337 |
| Canada HUL | 1045.8s | 4043 | 1428 |

`fit_stint_hp` returns `None` via its `if best is None: return None` path (calibration.py:359–360): `_grid_search` finds **no valid HP** because every grid point's held-out chi² is non-finite/non-positive (`_eval_hp` returns None for all). The "Mean of empty slice / invalid value in scalar divide" RuntimeWarnings in the log confirm the held-out chi² collapsed on the full, out-lap-contaminated span.

### Why it's `ok` now
`#548` added `windows=` to `calibrate_session_hp`: calibration runs only on the union of `[flying_lap_start-8s, flying_lap_end+8s]`, excluding the slow out/in-lap dynamics that corrupted the chi² surface. With windows, the surface is well-conditioned and `fit_stint_hp` succeeds:
- Bahrain ALO → ell=1.92, chi2_pos=0.861
- Bahrain HAM → ell=3.20, chi2_pos=0.810
- Canada HUL → ell=3.60, chi2_pos=1.295

Additionally `#543` added the None-guard (calibration.py:898–902): even the OLD full-span path now raises a **typed** `ValueError("no_accel_samples: ...")` at the same call site instead of the raw NoneType — confirmed in the log ("current calibrate_session_hp (no windows): ValueError ... no_accel_samples").

---

## 4. `interleaved n=0` cases — per-case stream overlap + recover-vs-skip

Probe: `probe_overlap.py`; raw log: `overlap_output.log`.

### Per-case overlap (stint window of the fast lap)

| GP | DRV | total pos N | total spd N | spd empty? | win span | pos in win | spd in win | overlap (s) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| Japan | PIA | 16708 | 7443 | no | 1173.6 | 4478 | 1566 | 1173.1 | **RECOVER** |
| Japan | NOR | 16773 | 5928 | no | 1204.8 | 4593 | 1511 | 1204.2 | **RECOVER** |
| Japan | LEC | 16417 | 8153 | no | 1216.2 | 4628 | 1358 | 1215.8 | **RECOVER** |
| Japan | SAI | 16384 | 6592 | no | 1217.2 | 4629 | 1373 | 1216.6 | **RECOVER** |
| Japan | MAG | 16819 | 4142 | no | 1361.9 | 5165 | 1371 | 1361.5 | **RECOVER** |
| Netherlands | SAR | 20196 | 10427 | no | 1505.9 | 5712 | 791 | 526.3 | **RECOVER** |
| Mexico | ZHO | 13108 | 6497 | no | 952.6 | 3645 | 1183 | 952.2 | **RECOVER** |
| Brazil | PIA | 13708 | 5953 | no | 1182.5 | 4593 | 1332 | 1182.0 | **RECOVER** |
| Las Vegas | BOT | 14663 | 8442 | no | 1240.3 | 4804 | 1819 | 1240.0 | **RECOVER** |
| Abu Dhabi | VER | 13666 | 6956 | no | 1260.5 | 4800 | 1225 | 1259.9 | **RECOVER** |
| **Saudi Arabia** | **DEV** | **5006** | **0** | **YES** | **685.4** | **2607** | **0** | **0.0** | **SKIP-CLEAN** |
| Azerbaijan | GAS | 21486 | 2745 | no | 1432.1 | 5510 | 2018 | 1431.9 | **RECOVER** |
| Azerbaijan | DEV | 20430 | 1141 | no | 1081.3 | 4144 | 1020 | 271.8 | **RECOVER** |
| Miami | BOT | 15088 | 6992 | no | 1232.1 | 4820 | 1748 | 1231.7 | **RECOVER** |
| Canada | ALB | 17733 | 9225 | no | 1347.4 | 5214 | 1758 | 1346.7 | **RECOVER** |

### Determination
- **14 of 15 → RECOVER (already recovered on `main`).** pos and speed streams overlap massively in the stint window (272–1432s of overlap; 791–2018 speed samples). These were never genuinely non-overlapping — the streams co-exist; the OLD calibration simply *sampled the wrong sub-window*. PR #548's `windows=` path recovers them all (they return `ok`, with healthy `n_samp`). No second-class fits: chi² is in normal range (spot-checked Bahrain/Canada chi2_pos 0.8–1.3).
- **1 of 15 → SKIP-CLEAN (Saudi Arabia DEV).** The speed (`car_data["Speed"]`) stream is **empty for the entire session** for this driver (total spd N = 0). `driver_streams` filters `Vkmh > 0` (loaders.py:393), and DEV's Speed column is all zero/missing in the store. No speed channel → genuinely unfittable. Must skip-clean with a typed reason.

### Root cause of the OLD `interleaved n=0` (mechanism, confirmed on Japan PIA)
Stint window span 1173.6s >> `slice_dur`=300s, so the OLD full-span `fit_stint_hp` called `_select_slice` (calibration.py:379–395) which trimmed to the **middle 300s** `[4207.1, 4507.1]`. Position had 1141 samples there, but the **speed stream had 0 samples in that middle slice** (a pit-lane gap between flying laps — speed only logs `Vkmh>0`). Pre-#548 `fit_stint_hp` then called `interleaved(len(tcs), 4)` with `len(tcs)=0` → raised `interleaved requires n>=1; got n=0`. The full-window speed samples (1566) exist outside that arbitrary middle slice, which is exactly why the `windows=` flying-lap-union calibration recovers it.

---

## 5. The one remaining bug — Saudi Arabia DEV (full root cause + traceback)

Probe: `probe_saudi_dev.py`; raw log: `saudi_dev_output.log`.

**Symptom (current `main`):** `fit_driver` returns `fit_status="error"`, `error="zero-size array to reduction operation minimum which has no identity"`, in ~0.3s, `n_fly=0`.

**Raw traceback (inner chain, broad-except bypassed via direct public-seam calls):**
```
File ".../src/preprocessing/trajectory/calibration.py", line 879, in calibrate_session_hp
    tc_min, tc_max = float(tc.min()), float(tc.max())
ValueError: zero-size array to reduction operation minimum which has no identity
```

**Root cause:** DEV's speed stream is empty session-wide (`spd stream EMPTY`, n=0; `driver_num(DEV)=21`). So `mc = (spd_d["t"] >= st0) & (spd_d["t"] <= st1)` selects 0 speed samples (`n_spd_in_window=0`). `fit_driver` then calls `calibrate_session_hp(..., windows=flying_windows)`. The new `windows=` branch (calibration.py:877–889) computes, **before** `fit_stint_hp` is ever reached:
```python
tc_min, tc_max = float(tc.min()), float(tc.max())   # line 879 — tc is empty → ValueError
```

**Why #548's guard misses it:** #548 added `if len(tps)<1 or len(tcs)<1: return None` *inside* `fit_stint_hp` (calibration.py:343). But the empty-`tc` `min()` in the `windows=` branch happens earlier, so that guard never runs. This is a residual gap in #548's hardening: the empty-speed-stream early-exit is in the wrong place for the windows= code path.

**Recover-vs-skip:** SKIP-CLEAN — there is no speed channel at all, so a fit is physically impossible. This is *not* a non-overlapping-window problem (the whole session has no speed), so widening the window cannot help.

---

## 6. `FitRecord.fit_status` valid set — from source

Every `FitRecord.fit_status` is emitted in `src/physics/session_fit.py` (the only `FitRecord` producer). `_err(status, msg)` (line 212) accepts any string; the statuses actually emitted today:

| status | source line(s) | meaning |
|---|---|---|
| `"ok"` | `session_fit.py:79` (`record_from_params`) | successful fit |
| `"no_laps"` | `session_fit.py:241, 285` | no valid flying lap (≤50s filter, or all flying laps skipped → no processed data) |
| `"no_accel_samples"` | `session_fit.py:312` | typed clean-null; raised as `ValueError("no_accel_samples: ...")` at `calibration.py:899`, caught and mapped |
| `"error"` | `session_fit.py:314, 317` | catch-all for any other `ValueError` / `Exception` |

**Valid set today = `{"ok", "no_laps", "no_accel_samples", "error"}`.**

**`fit_store.py:34` comment is STALE** — confirmed. It reads `# "ok" | "error" | "no_laps"` and omits `"no_accel_samples"` (added by #548/#543). Other `fit_status` occurrences in the tree (`physics/layer2/estimate_store.py`, `evo_predictor/gold_cycle/*`, `evo_predictor/fusion_training/*`) belong to **different** stores (Layer-2 estimate store; evo calibration entries), not `FitRecord`, and are out of scope.

---

## 7. Current failure counts by pattern (the re-run)

| pattern | OLD-store count | CURRENT count | notes |
|---|---|---|---|
| `'NoneType' object is not subscriptable` | 3 | **0** | fixed by #548 (`windows=`) + #543 (typed guard) |
| `interleaved requires n>=1; got n=0` | 15 | **0** | fixed by #548 (`windows=`) + #544 (len-guard) |
| `zero-size array ... minimum ...` (NEW) | 0 | **1** | Saudi Arabia DEV — empty speed stream; #548 gap |
| `no_laps` (clean typed skip) | 1 | **1** | Japan SAR (unchanged, correct) |
| **total non-ok (of the 19)** | **19** | **2** (1 error + 1 no_laps) | |

Net: the live exception population is now exactly **one** (`error`, Saudi Arabia DEV). One typed skip (`no_laps`, Japan SAR) is correct as-is.

---

## 8. Recommended fix loci (exact file:line) — for the decide-fix checkpoint

The human ratifies the fix; this is evidence/recommendation only.

1. **Empty-speed-stream guard for the `windows=` branch — the one live bug.**
   - **`src/preprocessing/trajectory/calibration.py:877–891`** (`calibrate_session_hp`, the `if windows:` block). The `tc.min()/tc.max()` at **line 879** (and `tp.min()/tp.max()` at line 878) run on possibly-empty arrays before any guard. Add an early guard `if len(tp) < 1 or len(tc) < 1:` (or after masking, `if not pos_mask.any() or not spd_mask.any():`) that raises the same typed `ValueError("no_accel_samples: ...")` the None-path already raises at line 899 — so `fit_driver`'s existing `except ValueError ... msg.startswith("no_accel_samples")` (session_fit.py:310–312) maps it to the typed `no_accel_samples` skip. This converts Saudi Arabia DEV from raw `error` to a clean typed skip with **no new status needed**.
   - Alternative (decision for the human): introduce a distinct typed reason such as `no_speed_stream` to disambiguate "no speed channel at all" from "HP search failed". Either way the emit site is `fit_driver` (session_fit.py:308–312) and the raise site is `calibrate_session_hp`.

2. **Pre-emptive empty-stream check earlier (defense in depth, optional).**
   - **`src/physics/session_fit.py:236` / `:247–248`** — right after `pos_d, spd_d = driver_streams(...)`, an explicit `if len(spd_d["t"]) == 0: return _err("no_accel_samples"/"no_speed_stream")` would short-circuit before any calibration work and make the skip reason unambiguous at the fit_driver level (mirrors the existing `if valid.empty: return _err("no_laps")`).

3. **Stale comment.**
   - **`src/physics/fit_store.py:34`** — update `# "ok" | "error" | "no_laps"` to include `"no_accel_samples"` (and whatever typed reason fix #1 lands on). Pure doc fix; keep the enumerated set and the code emitters in sync.

4. **Enumerated typed-skip reason set (decision pressure — report, don't decide).**
   - Current emitted set: `{ok, no_laps, no_accel_samples, error}`. Recommendation for the decide-fix checkpoint: keep `error` strictly for *unexpected* faults, and route every *expected* unfittable condition to a typed reason. The Saudi-DEV class ("no usable speed channel") is the concrete new member to name. The recover-vs-skip boundary established here: a case is **recoverable** iff both streams have samples that overlap in time within the flying-lap windows (14/15 cases); it is a **clean skip** iff a required stream is empty over the whole session (Saudi DEV).

---

## 9. Evidence index (all under `.agent-work/issue-495-fit-robustness/`)

- `probe_repro.py` / `repro_output.log` — 19-case re-run, current status+error per case (§2).
- `probe_nonetype.py` / `nonetype_output.log` — NoneType root cause, reproduced TypeError, with/without `windows=` (§3).
- `probe_overlap.py` / `overlap_output.log` — per-case stream-overlap numbers, recover-vs-skip (§4).
- `probe_saudi_dev.py` / `saudi_dev_output.log` — Saudi DEV raw traceback at calibration.py:879, empty speed stream (§5).
- OLD `interleaved n=0` mechanism confirmation (Japan PIA, inline in §4) — `_select_slice` middle-300s → `len(tcs)=0`.
