# Launch Order: `cmdr-R — #495 fit-robustness cluster (#542 + #543 + #544 + #538)`

Commanders start cold. Paste, don't point. **Run the FULL `constellation-commander` gated spine** for this mission (understand → plan → implement → review → integrate). You are a multi-step commander, not a one-shot implementer (explicit user preference).

## Mission
Harden the single-session trajectory-fit pipeline so the ~4%-of-fits-fail class
(found in #475 validation breadth) is closed. This is the **runway** for C-phase
race-state fits (#511) — which will hammer exactly these failure modes (red-flag
restarts, cold-wet, multi-stint). Deliver **ONE coherent calibration-hardening PR**
covering all four issues — they share the same `stint_span → calibrate_session_hp /
fit_stint_hp → interleaved` call chain; fixing them separately would collide.

The four issues (full text pasted below):

- **#542 — chi2 metric always nan.** `session_fit.py` populates `FitRecord.chi2` via
  `getattr(hp, "chi2_pos", float("nan"))` but `SmootherHP` has no `chi2_pos` attr, so
  the default fires every time. Expose the real `chi2_pos` from `fit_stint_hp` through
  `SmootherHP` so the calibration-quality diagnostic is functional. (Diagnostic-only;
  no fit corruption — but it silently misleads.)
- **#543 — red-flag phantom stint NoneType crash** (`calibration.py:861`). Red-flagged/
  restarted sessions get laps spanning the stoppage assigned to one stint → `stint_span`
  returns a ~1253 s window including the parked-car period → `fit_stint_hp` returns
  `None` → `StintSmoother(hp["ell"], …)` with `hp=None` → `TypeError`. Must produce a
  clean `_err(...)` or a correctly-bounded window, never a crash.
- **#544 — cold-wet `interleaved n=0`.** Cold+wet+low-grip → 0 samples pass the
  accelerating-segment filter → scipy `interleaved`/spline raises an opaque
  `"interleaved requires n >= 1; got n=0"`. Pre-check the minimum accelerating-sample
  count and return a clear `_err("no_accel_samples"/"no_laps")` with context.
- **#538 — filter in/out-lap windows before HP calibration** (the structural root that
  also subsumes #543). `stint_span` returns the FULL stint window (out-lap → flying →
  in-lap); the slow pit-lane sections inflate the calibrated length-scale `ell`
  (measured 3.2–7.0 within one session across drivers), over-smoothing the braking knee.
  Fix: build the calibration window as the **union of flying-lap windows** `[t0-overhang,
  t1+overhang]` clipped to stint bounds — NOT the raw stint span. This naturally excludes
  the red-flag phantom out-lap (no flying lap spans it), so it is the shared remedy for
  #543's window AND #538's `ell` inflation.

**Architectural through-line:** #538's flying-lap-window fix is the spine; #543's guard
(`fit_stint_hp` None → clean error, not crash) and #544's pre-check are defensive
companions; #542 is the diagnostic plumbing. Do them as one design.

## Prior-Wave Verdicts (pasted)

**#495 (umbrella):** "Physics fit robustness: ~4% of single-session fits fail
(interleaved n=0 / NoneType)." #543 and #544 are its two named, root-caused instances.

**#475 validation-breadth findings (the grounding, `docs/physics/475-validation-breadth.md` §E1/§E4/§E5):**
- 42 fits / 14 sessions. Fits succeed warm + ≥3 flying laps; **cold-wet fails**.
- `ell` varies **3.6–7.0 WITHIN a session across drivers** — NOT a clean circuit-level
  contamination index; it tracks stint structure (out-lap duration, red-flag pauses).
- #543 confirmed root-cause (targeted debug): 2022 Japan Q VER, stint 3 phantom out-lap
  `LapStartTime≈2779s` but flying lap starts `≈3830s`; `stint_span` → `t0=2776.9, t1=4030.0`
  (1253 s); `fit_stint_hp` → `None` → crash at `calibration.py:861`.
- #544 confirmed: Emilia-Romagna 2022 Q (rain=1.0, track 14.4°C/air 12.5°C), VER:
  `n_valid_laps=11` but **0 samples pass the accelerating-segment filter** → scipy raises.
- #542 confirmed: every session across all 9+ runs returned `chi2=nan`.

**Verified code seams (cite exact signatures — confirmed at filing):**
- `src/physics/session_fit.py` `fit_driver`: `st0, st1, _ = stint_span(session, driver, int(fast["Stint"]), pad=2.0)`; `hp = calibrate_session_hp(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp], spd_d["t"][mc], spd_d["V"][mc], order=4)`; chi2 read at `session_fit.py:~292` via `float(getattr(hp, "chi2_pos", float("nan")))`.
- `src/preprocessing/trajectory/calibration.py`: `interleaved(n, k, phase=…)` raises at `n<1` (line ~133); `fit_stint_hp(...)` returns `dict(..., chi2_pos=best["c_pos"], ...)` or `None` (line ~304/369); `calibrate_session_hp(...)` crash site `calibration.py:861` (`StintSmoother(hp["ell"], …)` with `hp=None`); in-lap masking `in_lap = (tp >= lap_t0) & (tp <= lap_t1)` at ~902; `return dict(n=0)` at ~1144.
- **Verify each signature from source before relying on it** — these line numbers are from the filing snapshot and may drift.

## Pre-Rulings
Ruled in advance, each overridable if evidence contradicts it — say so when overriding.
- **One PR, one design.** Do not split into four PRs. The four issues are one pass.
- **`calibrate_session_hp` may take a new `windows` parameter** (flying-lap union) — that
  is an in-fence signature change, allowed. Keep backward-compat: a `None`/absent
  `windows` falls back to current full-span behaviour so other callers don't break.
- **Honest-null is a win:** a cold-wet session that legitimately has no accelerating
  samples must fail *informatively* (clear `_err`), not crash and not be forced to fit.
- **Diagnose-first for #543:** the inherited red-flag root-cause is well-evidenced, but
  reproduce it (2022 Japan Q VER) before and after your fix to PROVE the crash is gone —
  don't assume the inherited diagnosis without a reproduction.
- **Tests:** update `tests/unit/physics/test_475_validation_breadth.py::TestEllContamination`
  per #538 — after the fix, `ell` should DROP at long-pit-lane circuits; replace any
  now-inverted ordering assertions with positive ones (e.g. `ell < 5.0` for clean quali).
  Add regression tests: #543 (red-flag session → clean error or bounded window, no crash),
  #544 (cold-wet → `_err("no_accel_samples")`), #542 (`chi2` finite on a normal fit).

## Honest-Null Clause
A measured negative on the stated question is a complete, successful deliverable. If a
failure mode legitimately should fail, make it fail *informatively* and say so.

## Inherited Latitude
You MAY (delegated): in-fence refactors, the `windows` param, filing follow-on issues,
choosing the error-taxonomy strings. You MUST float to the Admiral: any need to edit a
file OUTSIDE your fence (see File Ownership) BEFORE editing it (benign is not a reason to
skip the float); any change that alters a *measured number's meaning* beyond bug-fix
intent (units/convention territory — the #525 family); any scope addition beyond these
four issues. Asking up is always sanctioned.

## File Ownership
**Sole writer this wave for:**
- `src/preprocessing/trajectory/calibration.py`
- `src/physics/session_fit.py`
- `stint_span` (and only that) in `src/preprocessing/trajectory/loaders.py`
- `tests/unit/physics/test_475_validation_breadth.py` and any NEW test files you add under `tests/unit/physics/`

**Do NOT touch** `src/physics/layer2/**` or `src/physics/layer2/decoupled_longitudinal.py`
— those are cmdr-V's fence (Lane 2, #523). If your fix needs them, STOP and float.
Findings file: `.agent-work/509-w3/crew-handoffs/cmdr-R-findings.md` (you are sole writer).

## Workspace
Worktree **already provisioned for you**: `C:\Programs\f1Brainz-509w3-robustness`
- Branch: `feat/509w3-fit-robustness`  ·  Base commit: `accf07a2` (fresh main, verified)
- Created with: `git worktree add -b feat/509w3-fit-robustness ../f1Brainz-509w3-robustness accf07a2`

First step, before any git operation: `verify_worktree_isolation.py` does **NOT exist** in
this repo — use the native gate instead: run `git -C "C:\Programs\f1Brainz-509w3-robustness"
rev-parse --show-toplevel` and confirm it returns your worktree path (NOT the shared
`C:\Programs\f1Brainz`). Paste that output into your return report as isolation evidence.
Worktrees lack untracked inputs — see Data Locations.

## Inherited Context
Active playbook lessons (condition planning on these):
- **py-launcher:** Python is `py`, never `python`. Tests: `py -m pytest tests/...`.
- **worktree-untracked-data:** SQLite DBs / FastF1 cache / generated records are untracked
  and ABSENT from your worktree — use absolute paths into the main checkout (Data Locations).
- **shared-files-not-on-mission-branch:** NEVER commit `.agent-work/LESSONS.md`,
  `AGENT_FEEDBACK.md`, or `CONSTELLATION_FEEDBACK.md` on your branch. Return lessons-delta
  + feedback in your closeout report; the Admiral applies them centrally.
- **state-note-before-detach:** rewrite your crash-resume state note before any detached/
  multi-hour process (PID changes each detach).
- **crew-idle-strands-deliverable:** if you background your own long sub-task (a sweep/
  suite), it tends to go idle with the result UNWRITTEN — poll it to completion; the result
  file is the deliverable, you are not done until it exists.
- **run-crew-cli-launcher-misfit:** dispatch implementer/reviewer crews via the **Agent
  tool** (no `claude` CLI binary here); record attempts via `run_crew.py` pure registry
  functions; run `recover_crews` before each dispatch.
- **handoff-cite-exact-seam-signature:** when you hand a crew a seam, cite its EXACT
  verified signature/return type from source, not from memory.
- **diagnose-first-decide-fix:** for #543, gate-1 reproduce-the-bug BEFORE coding the fix.

Technical invariants: strict <1000 lines/file (`py -m src.utils.simplification_limits`);
pyright baseline is red (~83 errors) and **non-required** — gate on **no NEW per-file
errors** (CI log grep), not zero; PR body via temp file + `gh pr create -F <file>` (NEVER
heredoc / PowerShell here-string for PR bodies — here-strings are OK for `git commit -m` only).

## Data Locations
The 38 GB FastF1 telemetry cache + the per-year SQLite DBs + the physics SQLite store live
in the MAIN checkout (absent from your worktree):
- FastF1 cache: `C:\Programs\f1Brainz\data\telemetry` (loaders default to this absolute
  path; confirm via `src/preprocessing/trajectory/loaders.py` `_DEFAULT_CACHE` / `config.py`).
- Per-year DBs + physics store: under `C:\Programs\f1Brainz\data\`.
Read-only is fine from the shared path; do NOT write into the main checkout's data dir.
The sessions you need for reproduction: 2022 Japan Q (VER, #543), 2022 Emilia-Romagna Q
(VER, #544), plus any clean warm quali (e.g. 2023 Spain/Spa Q) for the `ell`/`chi2` tests.

## Budget
Model: **Sonnet** (commander + crews). Escalate to the Admiral only if a step stalls on
reasoning. This is a multi-hour pass; keep the state note current and crews polled.

## Stop Conditions
Stop and return when: a fix requires editing outside your fence (float first); a decision
outside inherited latitude is needed; the inherited root-cause turns out wrong on
reproduction (return with the new evidence); or you need context this order doesn't cover.
Return-and-query the Admiral — it answers and continues you. Asking up is always sanctioned.

## Return Shape
Final report: **verdict per issue** (#542/#543/#544/#538: fixed + evidence, or honest-null)
+ the reproduction proof for #543/#544 (before/after) + the `ell`-drop evidence for #538 +
map impact + triage candidates + workflow feedback (for the lessons audit) + your
`git rev-parse --show-toplevel` isolation output. Open ONE PR (`gh pr create -F <tempfile>`,
title referencing #542/#543/#544/#538 and "Refs #495 #509"), checks green, post the verdict
in the PR body. Do NOT merge — the Admiral merges. Commit trailers required:
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` and
`Claude-Session: https://claude.ai/code/session_01Pg84miea8Tmz2egJrGg2S4`; PR body footer
`🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
