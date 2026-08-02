# LAUNCH ORDER — #670 (manifest K), epic #659 Wave 6 — SEASON-SCALE RUN

**Commander:** `constellation-commander-delegated` (full commander depth).
**Model tier:** OPUS. RULING: this is Build-1's culmination — the full-season sizing + the held-out DIAGNOSTIC whose correctness (strictly-pre, correct golf-null baseline) is subtle-and-silent. And it is a LONG UNATTENDED overnight run (owner AFK). Robust diagnosis + honest reporting over speed.
**Worktree:** `C:/Programs/f1brainz-wt/epic659-670` · branch `epic659/670-season-run` · base main `5f802731` (carries #660–#669: the full landed chain + the #669 PilotPipeline).
**Interpreter PIN (CRITICAL):** `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`. `.pth` guard on bare scripts.

## OWNER AUTHORIZATION (genuine, on file)
The owner explicitly cleared kicking off this season-scale compute tonight: *"you're definitely allowed to kick off the long run… as long as things look fine… flag anything of interest and we can kill it."* The #669 pilot passed clean (all 3 circuits fresh, all C/D/E/H PASS, Admiral independent-verified) → the BEFORE-checkpoint go/no-go is SATISFIED. **You are cleared to run the season compute.** The owner is AFK; the run must be killable and must flag anything of interest via the Admiral.

## Issue intent
#670 (manifest K): run the **full 2023 season** through the pipeline — vocabulary tilings → G → season-scale class-grain utilization (incl. scalar reference-lap recovery) → fingerprint fit + join → instrument panel. 2023 because every store is deepest there. **Deliverable = the panel report + a DIAGNOSTIC held-out-weekend comparison** (fingerprint×composition prior vs a driver-overall-only prior — the golf null is the benchmark to beat). The join's CORRECTNESS is already established by #667's unit invariants — this comparison SIZES value, it does not re-establish correctness.

## THIS IS EXPLICITLY NOT A GATE — the deepest owner ruling
By owner ruling there is **no frame-kill**: a small or fat-σ driver term routes to structural work (different observables, different conditioning), NEVER to abandonment. **A measured negative here is a COMPLETE, SUCCESSFUL deliverable and must be reported as one.** Do not editorialize a small signal as failure.

## YOU DO NOT MAKE THE OWNER'S DECISIONS — you produce the report + present them
The report feeds THREE ALLOCATION DECISIONS that are the OWNER'S alone (the AFTER-checkpoint, NOT delegated):
1. variance shares → where Build-2 effort goes;
2. per-class, per-channel replication → which fingerprint axes (and which channel) earn join weight;
3. sector calibration → whether reference-lap fidelity work precedes fingerprint work.
Present these as a clear **"FOR OWNER — allocation decisions"** block in the report with the evidence for each — **do NOT decide them.** Float the finished report UP TO THE ADMIRAL; the Admiral parks the decisions for the owner.

## Execution plan (sizing + safety from the #669 pilot — heed exactly)
- **OFFLINE ONLY — no FastF1 online calls.** The pilot proved all 6 stages run offline (E reads telemetry_store shim; src/physics never imports fastf1, #503; C/D/G/H/PANEL read on-disk SQLite/Parquet). Run the season OFFLINE.
- **Confirm per-round coverage FIRST.** physics_estimates.db has all 22 rounds of 2023 and telemetry_store is the full-season mirror — but VERIFY per-round coverage before the full run. Any round/driver missing from the durable stores → **PARK it (no FastF1 pull) and report the gap.** A season on the covered rounds + a stated gap is a complete deliverable.
- **Sizing:** E is dominant, ~14s/DRIVER. The full ~20-driver grid × 22 rounds is ≈ ~2-4h single-threaded (apply the #650 ~2× optimistic-timings margin). Parallelize across circuits/rounds if your infra supports it safely (per-circuit is independent); otherwise single-threaded is acceptable — it's overnight.
- **RAISE the E per-stage timeout to ~6-8 min/circuit** for the full 20-driver grid (the pilot's 180s was tuned for 4 drivers and WILL be exceeded). Keep the per-stage auto-park (do not rely on a human poll).
- **DETACHED + STATE-NOTE-FIRST** (long unattended; a crash must be resumable). Auto-park on hang with a precise diagnosis — do NOT thrash/retry-loop.
- **The held-out diagnostic:** fingerprint×composition prior vs driver-overall-only prior, per held-out weekend, **strictly-pre** (predict a held-out weekend using ONLY strictly-prior data — no leakage). **Fix ONE documented driver-overall baseline** (the join's T7-1 unweighted-cell-mean form OR the fit-hierarchy support-weighted form — pick, state which, and justify; per #667 triage TC-1 the two forms differ and an undocumented mismatch mis-sizes the join's value). The golf null is the benchmark to beat.

## Reversibility (owner AFK — the contract)
- **NEVER write to tracked `data/f1_data_*.db`.** The pilot's E read a SCRATCH COPY — do the SAME. Season-scale writes `processed_telemetry` which bloats f1_data (#632) — those writes MUST go to isolated/scratch DBs, NEVER the tracked ones. `git checkout -- data/f1_data_*.db` if any shows Modified. NEVER touch the 38GB FastF1 cache. All run artifacts to isolated paths; the committed deliverable is the REPORT (+ any small code needed), regenerable.

## THE FIVE EPIC OWNER RULINGS (binding)
1. **No frame-kill** — see above; a measured negative is complete.
2. **Frozen constants (F12)** — consume the LANDED frozen sets; mint NOTHING (a needed threshold is a FLOAT to the Admiral). Raising the E TIMEOUT is a run-parameter, not a frozen constant — set it in the run invocation, not by editing a frozen set.
3. **Pre-quali** — strictly-pre throughout; the held-out diagnostic must have zero leakage.
4. **Lowest dimensionality** — run the LANDED pipeline; build no new model. The season run is execution + the diagnostic, not new method.
5. **No baked normality** — Student-t σ preserved end-to-end.

## Out of scope
Backfill of 2019–2026 (chased only AFTER the panel proves the machine); any Build-2/Build-3 work; MAKING the 3 allocation decisions (owner's); the #671 map reconcile; deleting anything.

## Constraints & hygiene
- **DB-BLOB GUARD (hard):** stage deliverables EXPLICITLY (never `git add -A`); final diff = report (+ minimal code/tests) only, zero DB blobs, zero `.agent-work`.
- **Map fence:** do NOT touch `docs/architecture/*` (reconcile is #671). Stage `notes-670.md` + `670-cartography/`.
- Feedback trio under `.agent-work/staged-feedback/670-season-run/` + `FENCE.md`. Working-notes = `notes-670.md`. pyright-0 on any new code.
- Isolation gate: first-action echo `ISOLATION_OK`; run ONLY in this worktree.

## Reporting
- **Proof-of-life FIRST** (echo ISOLATION_OK + SendMessage `main`) before any other work.
- STATE-NOTE-FIRST before launching the long run; SendMessage `main` a one-line progress ping when the run STARTS (so the Admiral can flag "compute started" to the owner) and again when it COMPLETES or PARKS.
- Float `user-decision`s UP TO THE ADMIRAL — never reach the owner (AFK).
- Report at PR + closeout: the season panel report (all 4 instruments over the full corpus — cross-circuit replication now meaningful); the held-out diagnostic (fingerprint×composition vs driver-overall-only, the documented baseline, strictly-pre); the "FOR OWNER — allocation decisions" block (evidence, NOT decisions); any parked rounds/gaps; the real wall-time; map-impact prose; clean-diff confirmation. NO merge without the Admiral (independent verify on pinned 3.14).

**Expiry:** at #670 report-to-Admiral or a Wave-6 contract-refresh.
