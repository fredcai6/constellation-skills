# LAUNCH ORDER — #668 (manifest I), epic #659 Wave 4b

**Commander:** `constellation-commander-delegated` (full commander depth — understand/plan/execute/reconcile).
**Model tier:** OPUS. RULING: #668 is Build-1's **exit instrument** and its correctness hazard is subtle-and-silent — the **golf-correction** (item 2). Raw split-half replication flatters by smuggling *overall skill* back into a per-class residual; the mature analog found residual shape-fit had **zero out-of-sample power once overall skill was controlled**. A mechanically-plausible-but-wrong replication (skill not fully removed, wrong support-scaling, coverage computed on the raw not the residual) can report a healthy signal size that is an artifact. This is exactly where a strong model earns its cost.
**Worktree:** `C:/Programs/f1brainz-wt/epic659-668` · branch `epic659/668-instrument-panel` · base main `ef97d799` (carries #660–#667: frozen constants, segment map, grip G, reference laps + class-grain observables, pooling verdict, DriverFingerprint store + fit, **the join #667**).
**Interpreter PIN (CRITICAL):** `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` (Python 3.14.3 / fastf1 3.8.1). NEVER bare `py`. Verify `import fastf1` before any real run. Bare scripts hit the editable-`.pth` trap (`src.*` resolves to MAIN's checkout, which lacks unmerged modules) — pytest is immune; for any bare script add `_REPO_ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(_REPO_ROOT))`.

## Issue intent
#668 (manifest I): **the instrument panel — Build-1's exit instrument. SIZING, never go/no-go.** Emit a written, versioned report with four instruments + the constants used. By owner ruling NO output halts the program (Build 2/3 never gated on a signal size). Outputs carry named *allocation* decisions (where Build-2 effort goes), not gates.

## THE FIVE EPIC OWNER RULINGS (binding)
1. **No frame-kill.** A small/zero signal size is a COMPLETE, successful deliverable — the panel SIZES, it never abandons. The driver-utilization share reads as a **floor**; "residual replicates at zero OOS power once skill removed" is an honest, acceptable finding, not a failure. Say the size plainly.
2. **Frozen constants (F12) — HARD OWNER GATE this wave.** The `REPLICATION_*` thresholds, the **support-count-scaling formula**, and the **channel-comparison registration** must be pre-registered as a NEW named frozen set BEFORE any real-data run (a needed-but-unfrozen threshold is a FLOAT: new named set + re-run, never inline). Consume #660 `layer2/frozen_constants.py` + #666 `fingerprint/frozen_constants.py`; mint NO inline literals. **You MUST float the proposed frozen set UP TO THE ADMIRAL and BLOCK the real-data run until the Admiral returns the owner's sign-off** (see GATE below). All non-real-data work (build the four instruments, synthetic tests) proceeds in parallel meanwhile.
3. **Pre-quali constraint.** The fingerprint cells you read are strictly-pre — preserve that provenance (pass `as_of_round` through; never read a cell past the cutoff). The scorecard validates predictions that were themselves pre-quali against official sector times *already on disk* (a post-hoc SIZING diagnostic is fine; do not let real sector outcomes leak back into the cells/predictions being scored).
4. **Lowest dimensionality.** Build EXACTLY the four instruments as specified — a variance share-split, a split-half replication, a per-class channel comparison, a sector-sum scorecard. NO bespoke model, no interaction terms, no extra instruments.
5. **No baked-in normality.** The scorecard's distribution-calibration coverage and the replication σ-honesty check use the repo's Student-t / heavy-tailed seam (`predictive_t` / `student_t`); the cells carry heavy-tailed σ — propagate honestly. Coverage is DISTRIBUTION calibration, not Gaussian ±.

## What to build (the four instruments)
1. **Variance decomposition** — split segment-time variance into **car-reference / driver-utilization / residual** shares. This is THE "set the size" instrument; its output directs where Build-2 effort goes. The driver-utilization share reads as a **floor**. Car-reference ← #664 `reference_laps`; driver-utilization ← #666 fingerprint cells.
2. **Residual split-half replication (golf-corrected — LOAD-BEARING)** — per-class fingerprint replication computed **AFTER removing overall skill** (the golf-corrected form). Raw replication smuggles overall skill back in and flatters; the correction is load-bearing, not cosmetic. Doubles as a **σ-honesty check**: do cells replicate WITHIN their stated uncertainty? Thresholds + support-count-scaling formula = the frozen set (GATE below).
3. **Pre-registered channel comparison (owner-initiated)** — run the replication per class in BOTH channels (time-deficit AND energy = kinetic-energy deficit from the same speed observables). **Whichever channel replicates better in a class earns join weight there.** The comparison protocol is REGISTERED (frozen) before any real-data run; which channel wins is decided empirically AFTER. Rationale: time weights by lap-time cost (driver-aligned); energy expresses momentum-carry + deployment (car/2026-aligned) — decide empirically, not on priors.
4. **Composed-sector scorecard** — segment predictions sum into FIA sectors, validated against **official sector times already on disk**, every pipeline weekend. Per review T11 the two claims are SEPARATED: (a) position-sum exactness = a construction check (segments sum to sectors); (b) the genuine external anchor = predicted sector-time **distribution calibration** (central values AND coverage). DIAGNOSTIC for signal size; **GATING only on the frozen gross-miscalibration sanity bound** (part of the frozen set).

## Consumer boundary (ruled at #667)
The panel reads **UN-AGGREGATED fingerprint cells directly** (#666 store read API) — do NOT route the replication through the #667 join aggregation. The join is for practice-update + fusion summaries; the panel and race sim read cells directly. The variance decomposition consumes the car-reference (#664) and driver-utilization (#666 cells) inputs directly.

## THE F12 GATE (hard — do not cross without Admiral sign-off)
Sequence: (1) understand + plan; (2) DESIGN the four instruments and PRE-REGISTER the frozen set — `REPLICATION_*` thresholds, the support-count-scaling formula, the channel-comparison registration, and the gross-miscalibration sanity bound — as a NEW named constant set (with a one-line rationale each); (3) **FLOAT the proposed frozen set to the Admiral (SendMessage `main`) and STOP the real-data run** — the Admiral routes it to the owner for sign-off (standing clearance stops at any F12 pre-registration). (4) Build the instruments + synthetic/deterministic tests MEANWHILE (scope-independent — do not idle). (5) Only after the Admiral returns owner sign-off, run the real-data pass + emit the versioned report. Pre-registration values are a starting point the owner may adjust; do not treat your proposal as self-approved.

## Scope boundary — build season-CAPABLE, validate BOUNDED
Build the panel season-capable; validate on the on-disk slice. As with #667, only **Great Britain 2023-Q** is on disk (Monaco/Spain/Belgium reference_laps+observables were never built / swept). Official FIA sector times for the validation weekend: LOCATE them in the DB / telemetry store (they are "already on disk" per spec — find where; do NOT pull FastF1 online). Run the four instruments on the GB slice; document the 1-circuit bounded scope + route multi-circuit breadth to **#670** (the season run), explicit not silent. Do NOT run the full season (#670, HITL).

## Out of scope
Any gate that halts Build 2 or 3 on a signal size (owner ruling — the panel never halts); the full season run (#670); the correlation-aware σ upgrade (#700); the fit-cutoff enforcement (#701); moving G's μ off zero (#678); the 3-circuit regeneration (Admiral-owned, → #670).

## Debt to heed
#632 (write any new store/report artifact to its OWN db/path, NEVER the f1_data DBs); #656 (tests use temp/scratch DBs, never dirty real DBs); #650/#648 (thread-cap + launcher-hang on long runs — bounded slice is short; detach + state-note-first if anything runs long).

## Constraints & hygiene
- **DB-BLOB GUARD (hard):** `data/f1_data_*.db` are TRACKED and WAL-churn on read — NEVER commit them. Stage deliverables EXPLICITLY (never `git add -A`); `git checkout -- data/f1_data_2023.db` if it shows Modified before commit. Final diff = code+tests+schema+report only, zero DB blobs, zero `.agent-work` paths.
- **Map fence:** do NOT touch `docs/architecture/*`. Record map impact as prose in your return + stage `notes-668.md` and `668-cartography/` for the epic CLOSEOUT cartographer reconcile.
- **Cartographer carry-forward:** IF you dispatch a cartographer subagent, `git status` in BOTH the worktree AND main afterward and verify its edits committed on the branch.
- Stage the feedback trio (AGENT_FEEDBACK + lessons-delta.json + CONSTELLATION_FEEDBACK) under `.agent-work/staged-feedback/668-instrument-panel/` with a `FENCE.md` citing this launch order; satisfy your feedback/archive gate against that staging dir. Do NOT commit any `.agent-work/` path on the branch.
- Working-notes file = `notes-668.md` (never `findings-*.md`).
- **pyright:** the join #667 shipped pyright-0; hold that bar — keep new modules pyright-clean on the pinned interpreter (type-only strictness, no forced casts). A dirty new module is a triage smell.
- Isolation gate: run ONLY in the provisioned worktree (first-action echo `ISOLATION_OK`). Do NOT re-provision.

## Reporting
- **Proof-of-life FIRST** (echo ISOLATION_OK + SendMessage `main` one-liner) before any other work — silence-after-dispatch is the failure mode we are actively fighting; if anything blocks you in the first steps, say so immediately.
- Float `user-decision`s (incl. the F12 set) UP TO THE ADMIRAL (SendMessage `main`) — never reach the owner directly (owner is popping in/out).
- Report at the F12 gate (proposed frozen set), at PR, and at closeout with: the four instruments + their results on the GB slice (variance shares incl. the driver floor; golf-corrected replication per class per channel + the σ-honesty verdict; the channel-comparison winners; the sector scorecard central + coverage vs official sector times); the frozen constants used; the versioned report artifact; the 1-circuit bounded-scope note (→#670); map-impact prose; clean-diff confirmation. NO merge without the Admiral (independent world-verify + re-run on pinned 3.14).

## Pre-rulings recap (binding)
- The panel SIZES, never gates — no output halts Build 2/3.
- The golf-correction (remove overall skill BEFORE replication) is load-bearing — a raw-replication signal is an artifact.
- F12 frozen set pre-registered + Admiral/owner sign-off BEFORE the real-data run — hard gate.
- Panel reads UN-AGGREGATED cells directly, NOT through the #667 join.
- Sector scorecard: position-sum = construction check; distribution calibration = the real anchor; GATING only on the frozen gross-miscalibration sanity bound.
- Lowest dimensionality: exactly the four instruments; Student-t coverage, no baked normality.
- Bounded to GB 2023-Q; multi-circuit breadth → #670.

**Expiry:** this order expires at #668 merge or on a Wave-4 contract-refresh from the Admiral.
