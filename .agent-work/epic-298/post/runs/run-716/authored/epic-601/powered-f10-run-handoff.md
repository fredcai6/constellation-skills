# Handoff — Powered F10 held-out run (the deferred #513 measured answer)

**Type:** delegated implementer-with-plan (bounded). **Model:** Sonnet.
**Worktree:** `C:/Programs/f1-fp-powered` (provisioned, base main `72577cef`) · **Branch:** `feat/fp-powered-run`.
**DO NOT let this worktree be swept — the detached run executes from it for hours.**
**Report → `C:/Programs/f1Brainz/.agent-work/epic-601/powered-f10-run-report.md` + SendMessage "main".**

## Mission
Get the **powered F10 held-out verdict** cooking as a DETACHED background job, optimize-first (~5–10 h, NOT the naive 37 h). This is the ONE measured answer Phase 4 deferred: **does the learned observation-representativeness weighting BEAT a "weight-by-clock-distance-to-Q" baseline on held-out weekends** (paired-bootstrap significance) + does a known sandbagging weekend visibly discount. Honest-null (learned does NOT beat clock) is a COMPLETE, first-class result — report it straight.

## Context (read these first)
- `.agent-work/archive/2026-07-19-513-fp-fits/REAL_RUN_HANDBACK.md` — the deferral spec + compute-reduction levers.
- `.agent-work/513-fp-followup/minimal_real_pass.py` — the PROVEN invocation pattern (Hungary FP2, completed, 7 FP + 6 Q real observations). Mirror it at scale.
- Harness: `src/physics/layer2/fp_gate.py` (FROZEN — do NOT modify; freeze hashes `f1725bd81cd3eefa` / re-stamp `349216857e6c09d9`). Extractor: `src/physics/layer2/fp_gate_real_extractor.py` (`make_extractor(year, weekends, db_path, sessions, max_drivers, max_laps_per_driver)`). CLI: `scripts/fp_representativeness_gate.py` (`--extractor module:factory` wants a ZERO-ARG factory; `--weekends`, `--bootstrap-resamples`, `--seed`).

## Build (small)
1. A **zero-arg GateExtractor factory wrapper** (e.g. `scripts/_fp_powered_factory.py`) that returns `make_extractor(year=2023, weekends=<16 frozen>, db_path="data/f1_data_2023.db", sessions=("FP1","FP2","FP3"), max_drivers=None (full field — apex_pace needs it), max_laps_per_driver=3)`. **`max_laps_per_driver=3` IS the fastest-K optimization lever** (handback-sanctioned: fewer laps, still enough on-limit apexes) — this is what turns ~37 h into ~5–10 h. Confirm the CLI accepts the dotted ref + runs LOWO + paired bootstrap end-to-end.
2. Ensure the run writes: the gate verdict JSON (redirect stdout or an `--out`-equivalent to `reports/physics/fp_representativeness_gate_2023_powered.json`) + a **completion sentinel** file (e.g. `.agent-work/epic-601/POWERED_F10_DONE.txt`, written with the final PASS/HONEST_NULL + key numbers) so the Admiral can poll with bounded waiters.

## Pre-flight BEFORE committing hours (mandatory gate)
Run a **1-weekend slice** (e.g. `--weekends Hungary`, same fastest-K=3, full field, FP1-3) to completion FIRST. Confirm: (a) the CLI produces a shape-valid gate verdict (not a crash), (b) it completes in a sane time, (c) extrapolated 16-weekend wall is ~5–10 h (measure the slice, multiply). **If the extrapolation is >~15 h or the slice hits a real headless/error issue → STOP and FLOAT to main. Do NOT fire a doomed 37 h+ job.**

## Launch (only after pre-flight passes)
- DETACHED: `Start-Process -WindowStyle Hidden` (NOT bare `py`+DETACHED — #648 launcher-stub hangs), from `C:/Programs/f1-fp-powered`, env `OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 PYTHONPATH=C:/Programs/f1-fp-powered`.
- **State-note BEFORE detach** (`.agent-work/epic-601/POWERED_F10_STATE.md`: PID, command, sentinel path, expected wall, resume command).
- **Verify liveness the RIGHT way** (learned false-stall lesson): confirm the python.exe **CHILD** PID accumulates CPU over the first ~1–2 min (not the 0-CPU `py` launcher stub). Single-thread fallback only if a genuine hang.
- **Do NOT wait for the 5–10 h run.** Once it's confirmed alive + the sentinel path is wired, HAND BACK: the PID, the command, the sentinel path, the measured slice→full extrapolation. The Admiral polls the sentinel; you're done once it's provably cooking.

## Guardrails
- The FROZEN harness (`fp_gate.py`, the protocol, the split) is UNTOUCHABLE — you only supply the extractor + a thin factory + launch plumbing. If fastest-K=3 visibly shifts grip observations vs full-laps on the slice, NOTE it (it's a sanctioned approximation, acceptable — just be honest).
- **DB hygiene:** the run READS `data/f1_data_2023.db` read-only; NEVER commit `data/*.db`; outputs go to `reports/`. Check `git status data/`.
- Explicit-unknown: the verdict's SECONDARY power channel will likely report CONFOUNDED (flat fp_mass σ, #652) — that's the correct honest outcome, report it, don't strain.

## Decision routing
Delegated; Admiral is your tier (no human). Float the pre-flight STOP decision, any error, or a scope question → SendMessage "main". No merge (the wrapper can be a follow-on PR or discarded — the RESULT is the deliverable, not the code).
