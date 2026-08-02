# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1` (`execute.json` `g1-implement`) — EVIDENCE-ONLY diagnosis for GitHub issue #495 (physics fit robustness).

## Completed slice
Re-measured the current (`main`, post-PR #548) failure population of the per-session physics fit pipeline by re-running all 19 OLD-store failing 2023-Q cases on current code; root-caused each pattern with real reproduced evidence; enumerated the `FitRecord.fit_status` set from source; named exact fix loci. No `src/` changes.

## Diagnosis summary
PR #548 already fixed **18 of 19** cases. Current re-run: **17 → `ok`** (all 3 NoneType + 14/15 interleaved), **1 → `no_laps`** (Japan SAR, correct typed skip), **1 → `error`** (Saudi Arabia DEV — a NEW failure mode, not the old `interleaved n=0`). The live exception population is now exactly **one**.

**Report path:** `.agent-work/issue-495-fit-robustness/g1_diagnosis.md`

### Per-case classification (all 19)
- **already-fixed → `ok` (17):** Japan PIA/NOR/LEC/SAI/MAG, Netherlands SAR, Mexico ZHO, Brazil PIA, Las Vegas BOT, Abu Dhabi VER, Azerbaijan GAS/DEV, Miami BOT, Canada ALB, Bahrain ALO/HAM, Canada HUL.
- **already-clean typed-skip → `no_laps` (1):** Japan SAR (confirmed still clean).
- **still-raises → genuinely-unfittable (1):** Saudi Arabia DEV (`zero-size array to reduction operation minimum which has no identity`).

### NoneType root cause (file:line)
- All 3 NoneType cases now `ok`. Original origin: **`calibration.py:861` (commit `52fe677b^`)** `iso = StintSmoother(hp["ell"], ...)` subscripted `None` when `fit_stint_hp` returned `None`. Real reproduced `TypeError` in `nonetype_output.log`.
- **Why None:** NOT emptiness (full window had 3800-4000 pos / 1300-1400 spd samples). `fit_stint_hp` returned `None` via `if best is None: return None` (calibration.py:359-360) — `_grid_search` found no valid HP because the full out-lap-contaminated span collapsed the held-out chi² (non-finite). Fixed by #548 `windows=` (flying-lap union → well-conditioned, ell 1.92/3.20/3.60) and #543 typed guard at calibration.py:898-902.

### Interleaved recover-vs-skip determinations (overlap numbers)
- **14/15 RECOVER** (already recovered on main): pos+speed overlap 272-1432s, n_spd-in-window 791-2018. Streams co-exist; OLD calibration sampled the wrong sub-window. (Full table §4 of report.)
- **1/15 SKIP-CLEAN — Saudi Arabia DEV:** speed stream empty session-wide (total spd N=0, overlap 0.0s). Genuinely unfittable.
- **OLD `interleaved n=0` mechanism** (confirmed Japan PIA): stint span 1173.6s >> 300s `slice_dur` → `_select_slice` middle-300s `[4207,4507]` had `len(tcs)=0` (pit gap; speed only logs `Vkmh>0`) → pre-548 `interleaved(0)` raised.

### The one remaining bug — Saudi Arabia DEV
- Raw traceback at **`src/preprocessing/trajectory/calibration.py:879`**: `tc_min, tc_max = float(tc.min()), float(tc.max())` on the empty speed array. DEV's `car_data["Speed"]` is all-zero/missing → `driver_streams` (filters `Vkmh>0`, loaders.py:393) yields an empty spd stream → `mc` selects 0 samples.
- **#548 gap:** the `windows=` branch computes `tc.min()/max()` BEFORE `fit_stint_hp`'s `len(tcs)<1` guard (calibration.py:343) can fire.

### Current failure counts by pattern
- NoneType: 3 → **0**; interleaved n=0: 15 → **0**; NEW zero-size-array: 0 → **1** (Saudi DEV); no_laps: 1 → **1** (Japan SAR). Total non-ok of the 19: 19 → **2** (1 error + 1 no_laps).

### From-source `fit_status` set
`{"ok", "no_laps", "no_accel_samples", "error"}` — all emitted in `session_fit.py` (ok:79, no_laps:241/285, no_accel_samples:312, error:314/317). **`fit_store.py:34` comment `"ok"|"error"|"no_laps"` is STALE** (missing `no_accel_samples`, added by #548/#543).

### Recommended fix loci
1. **`calibration.py:877-891`** (`calibrate_session_hp` windows= branch) — guard empty `tp`/`tc` (the `.min()` at line 878/879) and raise the typed `ValueError("no_accel_samples: ...")` it already raises at line 899, so `fit_driver:310-312` maps Saudi DEV to a clean typed skip. THE one live bug.
2. **`session_fit.py:236/247-248`** (optional defense-in-depth) — explicit `if len(spd_d["t"])==0: return _err(...)` right after `driver_streams`, mirroring the `no_laps` short-circuit.
3. **`fit_store.py:34`** — update the stale status comment to the real set.
4. **Decision pressure (report, don't decide):** whether to add a distinct typed reason (e.g. `no_speed_stream`) vs reuse `no_accel_samples`; the recover-vs-skip boundary = recoverable iff both streams overlap in the flying-lap windows, clean-skip iff a required stream is empty session-wide.

## Scope
**Files changed:**
- `.agent-work/issue-495-fit-robustness/g1_diagnosis.md` (report)
- `.agent-work/issue-495-fit-robustness/g1_implementer_result.md` (this result)
- `.agent-work/issue-495-fit-robustness/probe_*.py` + `*_output.log` (throwaway probes/logs)
- `.agent-work/issue-495-fit-robustness/g1_plan.json` (engine state)

**`src/` changed:** NO. `git status --short src/` is empty (verified). All reproduction went through public seams; no temporary instrumentation was needed (the broad except was bypassed by calling the inner chain directly from probe scripts, not by editing `src/`).

**Specific exclusions touched:** no — no src/ edits remain; no fixes made; FastF1 cache and telemetry store untouched (read-only).

## Behavior changed
No — evidence-only gate; zero production code change.

## Map Impact
- **Structural anchors touched:** `struct:physics` — `session_fit.fit_driver` (the per-case repro entry; `fit_session_full` is the single-driver diagnostic path, NOT a batch looper as the handoff stated); `struct:preprocessing` — `calibration.calibrate_session_hp` (windows= branch line 877-891 is the live-bug locus), `calibration.fit_stint_hp` (None-return producer), `loaders.driver_streams` (empty-stream source via `Vkmh>0` filter). Read-only; no edits.
- **Capabilities affected:** per-session physics fit robustness — measured: 18/19 OLD failures already fixed by #548; 1 residual bug (empty-speed-stream in windows= path).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` honored (stayed in physics/preprocessing); `evidence-only` honored.
- **Decision candidates:** typed-skip reason naming for the empty-speed-stream class (no_speed_stream vs no_accel_samples); the recover-vs-skip boundary — both surfaced for the decide-fix human checkpoint, not decided here.
- **Claims/evidence produced:** current 2023-Q failure population of the 19 = 1 error + 1 no_laps; fit_status set = {ok, no_laps, no_accel_samples, error}; fit_store.py:34 comment stale. All backed by reproduced logs.
- **Trust limitations / drift found:** handoff's Map Anchor describing `fit_session_full(...)` as "the per-session batch entry that derives round_idx/constructor and loops drivers" is INCORRECT — that is `fit_batch.run_batch` (which loops the whole calendar); `fit_session_full` is the single-driver P1 diagnostic. `fit_store.py:34` docstring drift confirmed.
- **Triage candidates:** none new beyond the named fix loci (the bug is in-scope for the following fix gate).

## Test mode
**Required:** evidence-only (diagnosis; no production code change).
**Satisfied:** yes — every claim is backed by a reproduced run captured in a log file; no tests authored because no behavior changed.

## Evidence

```bash
py .agent-work/issue-495-fit-robustness/probe_repro.py        # 19-case re-run -> repro_output.log
py .agent-work/issue-495-fit-robustness/probe_nonetype.py     # NoneType root cause + traceback -> nonetype_output.log
py .agent-work/issue-495-fit-robustness/probe_overlap.py      # stream overlap, recover-vs-skip -> overlap_output.log
py .agent-work/issue-495-fit-robustness/probe_saudi_dev.py    # Saudi DEV raw traceback -> saudi_dev_output.log
git status --short src/                                        # empty (no src/ edits)
```

**Result:** pass — all four probes ran to completion; outcomes folded into `g1_diagnosis.md`. Key numbers: 17 ok / 1 no_laps / 1 error; NoneType origin calibration.py:861 (pre-548); Saudi DEV crash calibration.py:879; fit_status = {ok, no_laps, no_accel_samples, error}.

## TDD evidence, if required
Not required (evidence-only, no behavior change).

## Docs/contracts touched
- None in `src/`. (Recommended doc fix `fit_store.py:34` is named as a fix locus, not applied — this gate is diagnose-only.)

## Assumptions
- "Current `main`" = checkout `fix/495-fit-robustness` at HEAD `bac0e96b`, which contains PR #548's hardening (verified in source). The branch sits at the same HEAD as main per gitStatus.
- The telemetry store (`data/telemetry_store.db`) is the faithful source `load_quali_session` reads first; all 11 affected 2023-Q GPs are present, so repro is store-backed (not dependent on the volatile FastF1 cache).
- Reproducing the OLD NoneType subscript by replaying the full-span (`windows=None`) path through current public seams is faithful to the original mechanism (the `fit_stint_hp` None-return is the producer; the subscript site is git-confirmed at the pre-548 line 861).

## Stop conditions hit
- None. No fix was required to produce the evidence; scope was not exceeded; every case reproduced.

## Out-of-scope observations
- `data/physics_fits.db` is the OLD pre-#548 store (2026-06-23). A G3-style re-fit of all 2023-Q on current code would shrink the recorded failure count from 19 to ~2; the store is stale and should be rebuilt after the fix (already anticipated by the problem_statement's G3 lean validation).
- Azerbaijan GAS/DEV and Japan MAG now fit with very few flying laps (n_fly=1-3, n_samp 412-1051). They are `ok` but thin; the fix gate's "no second-class fits" bar may want a minimum-flying-laps / minimum-sample sanity floor — flagged for the decide-fix checkpoint, not decided here.

## Workflow Feedback
- **Handoff gaps:** The Map Anchors (and the parent prompt's "Key seams") state `fit_session_full(...)` is "the per-session batch entry that derives round_idx/constructor and loops drivers — use it for faithful per-case repro." That is wrong: `fit_session_full` is the single-driver P1 diagnostic (returns `SessionFitFull | None`, re-fits one driver). The actual per-session looper is `fit_batch.run_batch`, and it loops the whole calendar, not one case. I used `load_quali_session` + `fit_driver` per case instead (the natural per-case unit and what `run_batch` itself calls). Cost: ~one extra source read to confirm the misfit before trusting the seam.
- **Context rediscovered:** The handoff named two live error patterns but not that PR #548 had ALSO introduced `no_accel_samples` as a typed status and the `windows=` branch's `tc.min()` (the new crash site) — the genuinely-new failure mode (Saudi DEV `zero-size array`) was unanticipated by the handoff's "two patterns are still live" framing. The handoff was right to insist on re-running rather than trusting the OLD list; that instruction directly surfaced the new pattern.
- **Instructions improvised around:** The engine's `record` verb is survey-only ("record is for survey checklists; use advance") — for a gated plan the per-step evidence path is `attest` (postcondition) + `advance`; the IMPLEMENTER_PLAN template's `record`-shaped postcondition with a `command` check did not match an inspection-only gate, so I used `null`-check attest postconditions. The skill's `claim` takes `--session-id` (claims the active gate) with no positional task id, unlike `attest`/`advance` which take a positional id — a one-time argument-shape gotcha.
- **What would have made this easier:** Correct the `fit_session_full`-as-batch-looper claim in the seam description (point repro at `fit_driver` + `load_quali_session`, or at `fit_batch.run_batch` with a single-session filter), and note that #548 added the `windows=` branch as a *new* code path whose own edge cases (empty stream pre-guard) were not all covered — that's exactly where the one residual bug lives.

## Return status
`complete`
