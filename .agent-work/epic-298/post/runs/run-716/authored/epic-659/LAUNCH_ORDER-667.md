# LAUNCH ORDER — #667 (manifest H), epic #659 Wave 4a

**Commander:** `constellation-commander-delegated` (full commander depth — understand/plan/execute/reconcile).
**Model tier:** OPUS. RULING: this is **THE core product of Build 1** and Fred's fantasy-points decision metric rides on it. The correctness hazard is subtle-and-silent (spec T7 / xR3 golf-analog): a mechanically-broken join — a wrong per-class weight, a sign error on a cell subset, wrong σ-widening — can still BEAT a driver-overall baseline on average through compensating errors, because overall skill dominates the signal. σ-propagation correctness through a soft-membership-weighted linear combination is exactly where a strong model earns its cost.
**Worktree:** `C:/Programs/f1brainz-wt/epic659-667` · branch `epic659/667-join` · base main `469d371e` (carries #660–#666: frozen constants, SegmentMap runtime + derivation, grip G, reference laps + class-grain utilization observables, pooling verdict, DriverFingerprint store + fit).
**Interpreter PIN (CRITICAL):** `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` (Python 3.14.3 / fastf1 3.8.1). NEVER bare `py`. Verify `import fastf1` before any real run. NOTE: bare analysis scripts in a worktree hit the editable-`.pth` trap (`src.*` resolves to MAIN's checkout, which lacks unmerged modules) — pytest is immune; for any bare script add `_REPO_ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(_REPO_ROOT))`.

## Issue intent
#667 (manifest H): **The join — circuit per-class time-share vector × DriverFingerprint cells, soft-membership-weighted → an expected weekend utilization prior with honest σ (thin cells → fat σ).** This is the core Build-1 product: it composes the car-reference circuit fingerprint (#664) with the driver-utilization fingerprint (#666) into the per-weekend, quali-side prediction prior.

## THE FIVE EPIC OWNER RULINGS (binding)
1. **No frame-kill.** Weak signal → structural work / honest-null, never abandonment.
2. **Frozen constants (F12).** Consume #660 `layer2/frozen_constants.py` + #666 `fingerprint/frozen_constants.py`; mint NO new literals. A needed-but-unfrozen threshold is a FLOAT (new named set + re-run), never inline.
3. **Pre-quali constraint.** Quali-side prior; predictions BEFORE quali; NO race-outcome leakage. The fingerprint cells you consume are already strictly-pre — preserve that (pass the `as_of_round` cutoff through; never read a cell fit past the cutoff).
4. **Lowest dimensionality that solves the problem.** **THE LINEAR JOIN *IS* THE PRIOR.** Escalation to sequence / bespoke formulations happens ONLY if simple arithmetic under-explains — and that determination is #670's diagnostic, NOT this issue. Do NOT build sequence models, interaction terms, or bespoke formulations here.
5. **No baked-in normality.** Student-t / heavy-tailed σ propagation (use the repo's `predictive_t` / student_t seam; the fingerprint cells already carry heavy-tailed σ — propagate honestly).

## What to build
- **The join:** for each (driver, channel), `prior = Σ_class composition[class] × cell_mean[driver, class]`, soft-membership-weighted, with **honest σ propagated** through the weighted linear combination (thin cells → fat σ dominates). Do this for **BOTH channels** (time-deficit AND energy) — symmetric — so #668's per-channel replication has both.
- **Inputs (consume as-is, do NOT re-derive):**
  - **Circuit per-class TIME-share composition vector** ← #664 `reference_laps` table: `time_shares_json` + `class_ids_json` (field-reference car's per-class time-shares). **Composition sums to the CORNER share, NOT 1.0** — straights are excluded (the confounded-negative-control ruling); do not renormalize to 1.0.
  - **Fingerprint cells** ← #666 `DriverFingerprintStore` read API (address by `CellAddress`: era, vocab-version, class id, channel). Each cell carries (mean, σ, support, resolved/unresolved status). The one-sided G σ⁺ is already folded into the cell σ (soft-degrades to 0 while the grip store is empty) — it rides through cell σ; NO separate G handling at the join.
  - **Soft memberships** flow through UNCHANGED (fractional class weights); the class-vocabulary version is PINNED on every cross-boundary call (read it off the cells / the #662 `map_version`; refuse a vocab-version mismatch loudly, per #666's precedent).
- **Thin exposure surfaced EXPLICITLY** — `thin_classes` / `weight_on_thin` fields on the output, never silently discounted. If a driver's weekend prior leans on an `unresolved`/thin cell, the output must say so.
- **Consumer boundary (ruled):** the join is reserved for the **practice-update + fusion summaries**. The **race simulator and the instrument panel (#668) read UN-AGGREGATED cells directly** — do NOT route them through the join. Build the join as the aggregation product; leave the cell store's direct-read API untouched for those consumers.

## GATING acceptance — the 4 reduces-to-simple-case invariants (spec T7; these ARE the correctness gate)
These exist precisely because an outcome-level win can hide a mechanically broken join. Unit-test all four, exactly:
1. **Uniform composition across classes ⇒ the join returns exactly the driver-overall mean.**
2. **All cells identical ⇒ the join returns that constant, regardless of the composition vector.**
3. **Single-class circuit ⇒ σ propagation collapses to that cell's σ.**
4. **Soft memberships flow through unchanged; composition sums to the corner share, not 1.0.**
A measured result here is the invariants passing + honest σ behavior on a bounded slice — NOT whether the join beats a driver-overall baseline (that is #670's diagnostic sizing, explicitly OUT of scope).

## Scope boundary — build season-CAPABLE, validate BOUNDED
Build the join + the 4 invariants + honest σ + thin-exposure surfacing, season-capable. Validate on the SAME bounded slice the wave has been using (2023-Q, 4 circuits Monaco/Spain/GB/Belgium, VER/PER/LEC/SAI) reading #666's fingerprint store + #664's reference-lap time-shares — offline, no FastF1 online calls. Do NOT run the full season (#670, HITL). If you need the fingerprint slice or the reference-lap time-shares and they are not on disk, regenerate the bounded slice offline via the #664/#666 scripts (state your finding); do not expand scope.

## Out of scope
Whether the join BEATS the driver-overall prior (#670 diagnostic); any sequence/bespoke/interaction escalation (#670 gates that); the instrument panel (#668, Wave 4b); race-side observables (Build 2); moving G's μ off zero (#678); populating the grip store (#692); the full season run (#670).

## Debt to heed
#632 (write any new store/artifact to its OWN db, off the f1_data DBs); #656 (tests use temp/scratch DBs, never dirty real DBs); #650/#648 (thread-cap + launcher-hang on long runs — bounded slice is short, but detach + state-note-first if anything runs long).

## Constraints & hygiene
- **DB-BLOB GUARD (hard):** `data/f1_data_*.db` are TRACKED and WAL-churn on read — NEVER commit them. Stage deliverables EXPLICITLY (never `git add -A`); `git checkout -- data/f1_data_2023.db` if it shows Modified before commit. Final diff = code+tests+schema only, zero DB blobs, zero `.agent-work` paths.
- **Map fence:** do NOT touch `docs/architecture/*`. Record map impact as prose in your return + stage `notes-667.md` and `667-cartography/` for the epic's single CLOSEOUT cartographer reconcile.
- **Cartographer-wrong-checkout carry-forward:** IF you dispatch a cartographer subagent, `git status` in BOTH the worktree AND main afterward and verify its edits committed on the branch.
- Stage the feedback trio (AGENT_FEEDBACK + lessons-delta.json + CONSTELLATION_FEEDBACK) under `.agent-work/staged-feedback/667-join/` with a `FENCE.md` citing this launch order; satisfy your feedback/archive gate against that staging dir. Do NOT commit any `.agent-work/` path on the branch.
- Working-notes file = `notes-667.md` (never `findings-*.md`).
- Isolation gate PASSED (worktree provisioned off `469d371e`, first-action echo ISOLATION_OK). Do NOT re-provision; run ONLY in this worktree.

## Reporting
Report at PR + closeout with: the join implementation + the 4 gating invariant test results (each pass/fail) + honest σ-propagation behavior on the bounded slice (esp. thin-cell fat-σ + `thin_classes`/`weight_on_thin` surfacing) + confirmation both channels join symmetrically + the map-impact prose + a clean-diff confirmation (code+tests+schema, zero DB blobs). NO merge without the Admiral (independent world-verify + gating re-run on the pinned 3.14 precede any squash). Float any `user-decision` UP TO THE ADMIRAL — do NOT reach the owner directly (owner is popping in/out; route through the Admiral).

## Pre-rulings recap
- The linear join IS the prior; NO escalation to sequence/bespoke here (that's #670's call) — **binding**.
- Composition sums to the corner share, NOT 1.0 (straights excluded); do not renormalize — **binding**.
- G rides through the cell σ (already folded, soft-degrades to 0); no separate G handling — **binding**.
- Join BOTH channels symmetrically (time + energy) for #668's per-channel comparison — **binding**.
- Panel + race sim read un-aggregated cells; the join is for practice-update + fusion summaries — **binding**.
- The 4 reduces-to-simple-case invariants are the correctness gate; beating the baseline is #670 diagnostic, out of scope — **binding**.

**Expiry:** this order expires at #667 merge or on a Wave-4 contract-refresh from the Admiral.
