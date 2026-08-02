# Implementation Result

## Assigned gate
`g2 (g2-implement)` — issue #447 Phase 0b: time-tag jitter model + inter-stream offset stability (GO/NO-GO core).

## Completed slice
Built a read-only characterization script that, over the SAME 6 G1 sessions, measures (per session, with distributions) the time-tag jitter per stream, classifies the time-tag error model, characterizes inter-stream clock-offset stability (resolving 0a finding F2), and computes the reduced chi-square the 0a covariance gate would see under the measured noise (input for F1). It reuses the 0a primitives (imported, not forked). Full foreground run over all 6 sessions succeeded; all 6 had DB sector truth.

## Scope
**Files changed:**
- `scripts/characterize_timetag_jitter.py` (new, the only source/script change)
- `.agent-work/issue-447/evidence/jitter_offset_2023_Belgian_Q.json`
- `.agent-work/issue-447/evidence/jitter_offset_2023_Belgian_R.json`
- `.agent-work/issue-447/evidence/jitter_offset_2022_Spanish_R.json`
- `.agent-work/issue-447/evidence/jitter_offset_2024_British_Q.json`
- `.agent-work/issue-447/evidence/jitter_offset_2024_British_R.json`
- `.agent-work/issue-447/evidence/jitter_offset_2023_SaoPaulo_R.json`
- `.agent-work/issue-447/evidence/jitter_offset_summary.json`
- `.agent-work/issue-447/crew-handoffs/g2-plan.json` (engine state)

**Specific exclusions touched:** `no` — no `get_telemetry`, no network (offline cache only via offline_loader), no evo imports, no DB writes (read-only `file:?mode=ro` via db_truth_loader), no estimator/filter/smoother deliverable (SG fit used solely to MEASURE jitter), no fork of 0a primitives (all imported), no GO/NO-GO decision. No `src/` files touched.

## Behavior changed
`no` — new analysis script + evidence artifacts only; no library/runtime behavior changed.

## Evidence JSON paths + headline numbers

Session set (all 6 had DB sector truth): 2023 Belgian Q+R (Spa), 2022 Spanish R (Barcelona), 2024 British Q+R (Silverstone), 2023 São Paulo R (Interlagos, wet). DB GP names map cleanly: Belgium / Spain / Great Britain / Brazil.

**(1) Time-tag jitter per stream (distribution, seconds):**
- car_data cadence-residual jitter IQR range across sessions: **[0.128, 0.141] s**; |median| ~0.07 s; p95 |jitter| ~0.24 s.
- pos_data cadence-residual jitter IQR range: **[0.128, 0.138] s**; |median| ~0.068 s.
- Sector-crossing jitter (telemetry-derived sector DURATION minus DB official duration, via `score_sector_anchor`): |median| range **[0.102, 0.158] s** across sessions.

**(2) Time-tag error-model class:** **white-jitter (no systematic bias/walk/batch)** — consensus across all 6 sessions. Discriminating statistics (per driver): dt-deviation lag-1 autocorr ~0 (e.g. car −4e-5, pos −0.039) → uncorrelated increments (NOT random-walk); per-Source eta² = 0.0 (single Source tag per car stream → NOT per-batch); |mean|/std ~1e-4 (→ NOT a constant bias). NB: the SG-residual lag-1 autocorr (~0.6) is a smoothing artifact and is reported as reference-only; the honest discriminator is the dt-deviation series, which is white.

**(3) Inter-stream offset stability (resolves F2) — verdict: STABLE-ESTIMABLE on all 6 sessions:**
| Session | mean offset (s) | median per-lap std (s) | median per-lap range (s) |
|---|---|---|---|
| 2023_Belgian_Q | −0.0036 | 0.129 | 0.435 |
| 2023_Belgian_R | −0.081 | 0.084 | 0.325 |
| 2022_Spanish_R | +0.040 | 0.097 | 0.497 |
| 2024_British_Q | −0.009 | 0.114 | 0.451 |
| 2024_British_R | −0.069 | 0.128 | 0.502 |
| 2023_SaoPaulo_R | −0.019 | 0.089 | 0.416 |

Per-lap offset series have low lag-1 autocorrelation (median |ac| < 0.5) and small drift → tight, low-drift → estimable stable bias. Magnitudes are consistent with 0a's per-lap ranges (~[−0.20,+0.41] etc.); offsets are small (|session mean| ≤ 0.08 s) and per-lap std ≤ 0.13 s. Per-lap arc-residual after offset fit is carried per driver in each session JSON (the "bounded cross-residual" gate half).

**(4) Reduced chi-square the 0a covariance gate would see** (residual = speed_arc − position_arc in m; per-sample variance = 2× measured pos XY noise ~0.1 m²; loose 0a band [0.01,100]): per-session ranges from **78.7 to 3292** across sessions (0a strawman saw 0.60–11.14). The gate is wildly deflated because the inter-stream offset (~0.1 s × track speed) injects a several-metre arc discrepancy not covered by ~0.1 m² positional noise — direct input for G3's F1 band recommendation.

## Map Impact
- **Structural anchors touched:** `struct:preprocessing` — new `scripts/characterize_timetag_jitter.py` consuming `trajectory_grading/{cross_residual,sector_anchor,covariance_gate,offline_loader,db_truth_loader,contract}.py` read-only. No primitive modified.
- **Capabilities added/changed/affected:** inter-stream correlatability characterization (the GO/NO-GO core) now has measured evidence: jitter distribution, error-model class, offset stability verdict, and the gate's chi-square.
- **Constraints/assumptions touched:** honored `constraint:physics_region_no_evo_import` and characterization-only; relied on FastF1 `LapStartTime`/`Time`/`LapNumber` for lap windows and DB `lap_times` sector durations.
- **Decision candidates / resolved decisions:** F2 resolved from evidence → offsets are a **stable estimable bias** (not per-lap wander), all 6 sessions. Error-model class chosen: **white-jitter**. The 0a cross-residual-is-a-diagnostic split is respected (REPORTED, never gated).
- **Claims/evidence produced:** the 7 evidence JSONs back every headline number; each number is traceable to script + session + driver.
- **Trust limitations / drift found:** chi-square is large because the residual includes the inter-stream offset; this is the honest "naive per-sample positional covariance" the gate would use — G3 should recommend a band (and/or residual definition) that accounts for the offset term.
- **Triage candidates:** none new; the chi-square magnitude is an input to G3's F1 work, not a defect.

## Test mode
**Required:** `evidence-only` (characterization; no project test surface for a new evidence script).
**Satisfied:** `yes` — engine `command` postconditions ran and exited 0 (smoke + full run + glob of jitter/offset artifacts). Reused primitives verified intact: `tests/unit/preprocessing/test_trajectory_grading.py` 47 passed; `tests/unit/physics/` 129 passed.

## Evidence

```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-447
set "PYTHONUTF8=1"
py scripts/characterize_timetag_jitter.py --smoke    # m1 gate (engine, exit 0)
py scripts/characterize_timetag_jitter.py            # m2 full run (engine, exit 0)
py -c "import glob;print(glob.glob('.agent-work/issue-447/evidence/*jitter*')+glob.glob('.agent-work/issue-447/evidence/*offset*'))"
py -m pytest tests/unit/preprocessing/test_trajectory_grading.py tests/unit/physics/ -q
py -m src.utils.simplification_limits --baseline      # src/-only repo gate (unaffected by this script)
```

**Result:** `pass` — full run wrote all 7 JSONs; primitive tests green; repo simplification baseline (src/-only) shows only 2 pre-existing, unrelated src/ failures (not introduced here).

## Docs/contracts touched
- `none` — no public interface or committed-schema change; evidence JSON is a local agent-work artifact, not a committed report schema.

## Assumptions
- Track lengths (lap-closure constraint): Spa 7004 m, Barcelona 4675 m, Silverstone 5891 m, Interlagos 4309 m (official circuit lengths).
- Candidate base time grid = pos_data SessionTime; speed-arc integrated on the car grid then interpolated onto the pos grid — this preserves the genuine inter-stream timing structure G1 confirmed, so the offset fit is meaningful.
- "Jitter vs local cadence" uses an SG fit of t(i) vs sample index as the locally-regular-cadence reference; the residual is the per-sample time-tag jitter (measurement smooth only).
- Per-driver SessionTime grid is shared across drivers in a session (FastF1 session clock), so cadence-jitter IQR is identical across drivers within a session — expected, not a bug.
- Single-lap (early-DNF) candidates are excluded from offset and chi-square aggregates (degenerate; e.g. 2024 British R GAS, 1 lap).

## Stop conditions hit
- `none` — sector truth available for all 6 sessions; no quantity impossible; no estimator construction required; no decision outside authority needed.

## Out-of-scope observations
- The covariance-gate chi-square (78–3292) is dominated by the unremoved inter-stream offset term, not by positional noise. For G3: recommend the F1 band be set against a residual that has the per-lap offset removed (the cross_residual arc-residual), OR widen the per-sample variance to include the offset's arc contribution. This is a G3 design call, flagged not decided.
- `scripts/characterize_timetag_jitter.py` is 1240 lines (over the <1000 simplification advisory) due to exhaustive units/bounds/invariants docstrings the evidence bar requires; function-level complexity/length limits are all satisfied. The repo baseline gate scans `src/` only, so this does not break check-in.

## Workflow Feedback
- **Handoff gaps:** The handoff did not say which GP-name namespace db_truth_loader expects (DB short names "Belgium"/"Spain"/"Great Britain"/"Brazil") vs the FastF1 long names G1 used ("Belgian Grand Prix" etc.). I had to derive the FastF1→DB mapping by querying the DBs. A one-line map in the handoff would have saved a discovery step.
- **Context rediscovered:** Official track lengths per circuit (needed for the lap-closure constraint in cross_residual / sector_anchor) were not provided; I sourced them. Also that FastF1 `LapStartTime`/`Time` give clean per-lap session-time windows for slicing raw streams — discovered by inspecting the laps DataFrame.
- **Instructions improvised around:** The engine runs `command` postconditions via `cmd.exe` (`shell=True`), where the handoff/skill's bash-style `PYTHONUTF8=1 py ...` env prefix is a syntax error and fails the check. I rewrote the plan's check commands to `cd /d ... && set "PYTHONUTF8=1" && py ...`. The platform-invariant note ("PYTHONUTF8=1 in any captured subprocess env") implies a bash idiom that the Windows engine shell rejects — worth calling out for future Windows crews driving the engine.
- **What would have made this easier:** Add the DB GP-name map and circuit track-lengths to the handoff (or a shared session-config the 0a/G1/G2 scripts all import), and note the engine's cmd.exe shell for `command` checks on Windows.

## Return status
`complete`
