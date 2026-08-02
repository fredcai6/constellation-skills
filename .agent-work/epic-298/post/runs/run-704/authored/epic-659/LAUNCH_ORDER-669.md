# LAUNCH ORDER — #669 (manifest J), epic #659 Wave 5a

**Commander:** `constellation-commander-delegated` (full commander depth).
**Model tier:** OPUS. RULING: this is an UNATTENDED OVERNIGHT run that gates the season run (#670). Robustness to surprises + clean diagnosis of any stage breakage (rather than thrashing) matters more than raw speed. If a stage breaks, DIAGNOSE + REPORT — do not paper over.
**Worktree:** `C:/Programs/f1brainz-wt/epic659-669` · branch `epic659/669-pilot` · base main `30cf676d` (carries #660–#668: the full landed chain — frozen constants, segment map, grip G, reference laps + observables, pooling, fingerprint store + fit, the join, the instrument panel).
**Interpreter PIN (CRITICAL):** `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`. Verify `import fastf1` before any real run. Bare scripts hit the editable-`.pth` trap → add `_REPO_ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(_REPO_ROOT))`.

## Issue intent
#669 (manifest J): a **3-circuit end-to-end pilot — a TRACER BULLET.** Wire the whole chain (tiling → G → utilization → fingerprint-fit smoke → the join → panel dry-run) into ONE invocable pipeline and run it on **three contrasting 2023 circuits**, to prove the MACHINE RUNS end-to-end before the season-scale bet (#670). This exists because five prior lineages of this idea were each built and never joined/run — the pilot ends that pattern.

## OVERNIGHT-UNATTENDED HARD CONSTRAINTS (owner is AFK; reversibility is the contract)
- **OFFLINE ONLY — no FastF1 online calls.** Read exclusively from the on-disk stores (telemetry Parquet mirror, the archived `fp_slice_2023Q.db` / `reference_utilization_run.db`, `physics_fits.db`, grip substrate). If a stage needs data not on disk, **REPORT THE GAP and stop that stage — do NOT pull from FastF1** (rate-limit exposure + external resource; owner not around to authorize).
- **Circuits = Monaco / Belgium / Great Britain** (all 2023-Q, all confirmed on-disk in fp_slice_2023Q.db). They ARE the required contrast: Monaco=street, Belgium=low-downforce/high-speed straights, Great Britain=high-severity fast corners. Do NOT pick circuits whose data isn't on disk.
- **Reversibility:** everything you produce must be git-revertible (code) or regenerable (run artifacts). Write ALL run artifacts to ISOLATED scratch/own-DB paths — **NEVER the tracked `data/f1_data_*.db`** (#632/#656 — DB-blob guard) and **NEVER touch the 38GB FastF1 cache**. `git checkout -- data/f1_data_*.db` if any shows Modified before commit.
- **Long-run tax (#650/#648):** detached start + STATE-NOTE-FIRST; thread-cap ~2× fit wall-time. If a stage hangs, PARK it with a precise diagnosis in your notes — do NOT thrash or retry in a loop.

## What to build
- **One invocable pipeline** (not five hand-run scripts): tiling → G (fit + held-out score) → utilization observables → fingerprint-fit smoke → the join → panel dry-run, over the 3 circuits, from ONE command.
- **Acceptance:** the one command produces, for ALL THREE circuits: valid maps; a fitted G with its held-out score; populated utilization observables; a smoke-fit fingerprint; a panel dry-run. Every GATING check from issues C/D/E/H passes on the slice. A short written report names anything that broke and what it implies for the season run (#670).

## THE FIVE EPIC OWNER RULINGS (binding, but this issue is a "does-it-RUN" test)
1. **No frame-kill** — a stage that surfaces a limitation is a COMPLETE finding; report it, don't abandon.
2. **Frozen constants (F12)** — consume the LANDED frozen sets (#660 layer2 + #666 fingerprint + the #668 REPLICATION_*). Mint NOTHING new; a needed-but-unfrozen threshold is a FLOAT to the Admiral, not an inline literal. (No new F12 expected here.)
3. **Pre-quali** — preserve strictly-pre cutoffs through the chain; no race-outcome leakage.
4. **Lowest dimensionality** — wire the EXISTING stages; build no new model. The deliverable is the pipeline wiring + the run, not new method.
5. **No baked normality** — the stages already carry Student-t σ; don't regress that.

## Out of scope
INTERPRETING signal sizes (three circuits cannot size anything — that's #670); the season run itself (#670, HITL); any new method/model; backfill; touching the live tiling path's internals.

## Constraints & hygiene
- **DB-BLOB GUARD (hard):** stage deliverables EXPLICITLY (never `git add -A`); final diff = code+tests+report only, zero DB blobs, zero `.agent-work` paths.
- **Map fence:** do NOT touch `docs/architecture/*` (the reconcile is #671). Record map impact as prose + stage `notes-669.md` + `669-cartography/` for #671/closeout.
- Feedback trio under `.agent-work/staged-feedback/669-pilot/` with `FENCE.md`. Working-notes = `notes-669.md`.
- **pyright-0 bar** on any new pipeline module.
- Isolation gate: first-action echo `ISOLATION_OK`; run ONLY in this worktree.

## Reporting
- **Proof-of-life FIRST** (echo ISOLATION_OK + SendMessage `main` one-liner) before any other work — silence-after-dispatch is the failure mode being actively fought; break silence immediately on any block.
- STATE-NOTE-FIRST before any long stage (owner is AFK — a crashed run must be resumable).
- Float `user-decision`s UP TO THE ADMIRAL (SendMessage `main`) — never reach the owner (AFK).
- Report at PR + closeout: the one-command pipeline; per-circuit results (maps/G+heldout/observables/fingerprint/panel-dry-run); every C/D/E/H GATING check pass/fail on the slice; anything that broke + season-run implications; map-impact prose; clean-diff confirmation. NO merge without the Admiral (independent verify + re-run on pinned 3.14).

**Expiry:** at #669 merge or a Wave-5 contract-refresh from the Admiral.
