# LAUNCH ORDER — #671 (manifest L), epic #659 Wave 5b — architecture reconcile + lineage dispositions

**Commander:** `constellation-commander-delegated` (full commander depth).
**Model tier:** OPUS. RULING: this is the epic's CONSOLIDATED architecture reconcile — folding 8 waves of map deltas + disposing five part-forgotten lineages with a live-code landmine (segment_classifier). The judgment (what's safe to call superseded, what must NOT be touched) is the whole point; a wrong disposition either breaks live code or re-buries a stray. Careful reading over speed.
**Worktree:** `C:/Programs/f1brainz-wt/epic659-671` · branch `epic659/671-reconcile` · base main `5f802731` (full landed pipeline #660–#669).
**Interpreter PIN:** `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.
**Runs in PARALLEL with cmdr-670 (season run).** You are the ONLY writer to `docs/architecture/*` this wave — cmdr-670 is map-fenced OFF it, so no conflict. Do NOT touch `src/physics/pilot/*` or any run artifacts (cmdr-670's territory).

## Issue intent
#671 (manifest L): with the pipeline landed, **reconcile it into `docs/architecture/index.md`** (real EDGES, not just nodes) and give each of five prior lineages an **explicit disposition** (wired-in / superseded-and-removed-PROPOSED / kept-with-stated-reason), recorded where a future agent will actually find it. This ends the "five lineages built, unjoined, part-forgotten, rediscovered" loop — the epic's stated raison d'être.

## THE DELETION GUARD (hard — this is why the owner can be AFK for this)
**This issue PROPOSES dispositions and executes ONLY the documentation + map work. NO code is deleted under this issue.** Deciding built code is safe to remove is a judgement no test verifies and is hard to walk back once merged — so **every proposed removal comes back as a LIST for the owner to approve (go/no), it is NOT executed here.** The owner is AFK: you will produce the list; the Admiral parks it. Deleting anything with a live consumer, or anything at all without sign-off, is OUT OF SCOPE.

## The five lineages — disposition each (READ each before disposing)
1. **circuit rollup #625** (`regime_rollup.py` / `property_mixture.py`) — validated but unwired.
2. **#628 utilization pipeline** (`driver_utility_observable.py` / `car_prior.py`) — code-complete, never run at season scale.
3. **ephemeris per-corner pilot** (`src/physics/ideal_lap/`).
4. **apex_obs full-coverage raw material** (`src/physics/apex_extract.py::extract_apex_observations`, persisted as the `apex_obs` column of `session_fits` in `data/physics_fits.db`).
5. **`segment_classifier.py` — READ THIS ONE CAREFULLY BEFORE DISPOSING ANYTHING.** `SegmentClassifier.classify_samples` (the tiling) is **LIVE PRODUCTION code**, imported by `src/physics/apex_extract.py`, `src/physics/parameter_estimator.py`, `src/physics/layer2/session_braking.py`, and `src/physics/__init__.py`. Only the `soft_class_membership` bridge method is genuinely unwired (present + unit-tested, zero non-test callers). Dispose ONLY the bridge question; **DO NOT touch the live tiling path** (verify the callers yourself before writing a word about it).

Each disposition = one line + a pointer, recorded where a future agent finds it (the arch map / a decisions anchor), so nothing stays in the "exists, unwired, unexplained" state that caused the loop.

## Consolidate the whole epic's map deltas (this is the closeout reconcile)
Fold the staged cartography deltas from every wave's archive into the map — they are staged for exactly this:
`.agent-work/archive/*/{661,662,663,664,666,667,668,669}-cartography/` (segment_map, grip node #663, segment-map derivation, reference-laps, fingerprint, the join `struct:physics.instrument_panel`-adjacent, instrument_panel node, `struct:physics.pilot`). Regenerate the #663 grip node; do NOT duplicate the #665 pooling block already on main. Show the JOINED pipeline with real edges C→D→E→G→H→PANEL.
**Also graduate #696** (the Builds 2–3 forward roadmap) into a docs/architecture anchor — #696 stays open as the tracker, the arch anchor is its structural home (anti-orphan; this is the epic's whole point).
Disposition #587/#559/#577 (same class of question on adjacent machinery — be CONSISTENT, don't invent a second convention) and record the disposition of the reserved/deferred structure in #642/#654 here rather than let it be rediscovered.

## Constraints & hygiene
- **CARTOGRAPHER-WRONG-CHECKOUT carry-forward (known trap):** IF you dispatch a cartographer subagent, `git status` in BOTH the worktree AND main afterward and verify its edits committed on YOUR branch (cartographers have committed to the wrong checkout before). Quote YAML evidence containing commas/parens carefully.
- **check_arch_map.py green is BLIND to content drift** — a green check does NOT mean the edges/evidence are right; do a real code-vs-map read (reverse-import-scan for missing edges; verify call-chains vs import edges).
- **DB-BLOB GUARD:** never `git add -A`; final diff = docs + any decisions-anchor files ONLY, zero DB blobs, zero `.agent-work`. `git checkout -- data/f1_data_*.db` if Modified.
- Feedback trio under `.agent-work/staged-feedback/671-reconcile/` + `FENCE.md`. Working-notes = `notes-671.md`.
- Isolation gate: first-action echo `ISOLATION_OK`; run ONLY in this worktree.

## THE FIVE EPIC OWNER RULINGS
Apply as relevant: no frame-kill (a "kept-with-reason" disposition is a valid complete answer — not everything must be wired or removed); lowest dimensionality (reconcile what's there, don't invent structure); the others are largely N/A to doc work. NO new F12.

## Reporting
- **Proof-of-life FIRST** (echo ISOLATION_OK + SendMessage `main`).
- Float `user-decision`s UP TO THE ADMIRAL — never reach the owner (AFK).
- Report at PR + closeout with: the reconciled map (joined pipeline, real edges); the five dispositions (each one-line + pointer; the segment_classifier live-path explicitly confirmed untouched); the #696 graduation anchor; the #587/#559/#577/#642/#654 dispositions; and **the "FOR OWNER — proposed removals" LIST** (what you propose to delete + why + what confirms it's safe) — as a list, NOT executed. Clean-diff confirmation. NO merge without the Admiral.

**Expiry:** at #671 merge or a Wave-5 contract-refresh.
