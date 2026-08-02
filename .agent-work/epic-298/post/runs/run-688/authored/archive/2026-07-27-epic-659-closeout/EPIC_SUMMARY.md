# Epic #659 — Build-1 quali-side physics feature pipeline — CLOSEOUT SUMMARY

**Run:** Constellation Admiral, 2026-07-25 → 2026-07-27. **Main HEAD:** `0a751cf0`.
**Status:** all 12 manifest issues landed + independently verified. Two owner decisions await you (below). Epic closeout mechanics (lessons audit, hygiene) in progress.

---

## What this epic built (and why)
A **joined quali-side physics feature pipeline** — the first time five previously-built-but-never-joined lineages of this idea were wired into one runnable chain and actually run at season scale:

**C → D → E → G → H → PANEL**
- **C** segment-map (per-weekend corner geometry, #661/#662)
- **D** grip-baseline G (honest measured-null, #663)
- **E** class-grain utilization + reference laps (#664)
- **G** driver fingerprint (hierarchical Student-t cells, #666)
- **H** the join (fingerprint × circuit composition → weekend prior, #667)
- **PANEL** the instrument panel (variance / replication / channel / scorecard, #668)

Plus: the pooling-validation harness (#665), the 3-circuit pilot/tracer-bullet (#669), the season run + diagnostic (#670), and the architecture reconcile + lineage dispositions (#671).

## The headline finding (the whole point of Build 1 — an honest, complete result)
The pipeline ran the **full 2023 season offline** (20/22 rounds; Bahrain + Saudi honestly parked — no strictly-prior data to predict a season opener from) and measured how much signal the driver-utilization axis actually carries. The answer, on 2023 alone:

- **Driver-utilization variance is at the floor (~0).** The car reference explains **69–82%** of segment-time variance; the driver term carries little *independent* variance beyond it.
- **No severity class clears the replication floor.** Utilization replicates weakly-positive across circuits (r ≈ +0.14–0.29); energy is near-zero. If any channel earns join weight, evidence favors **utilization over energy** — but neither clears the bar on one season.
- **Composition-weighting helps** (|resid| 0.854 < 1.143 driver-overall baseline) — weighting a driver's class cells by the circuit's corner mix beats a flat driver mean.
- **But the whole driver term does NOT beat the golf null** (0.830 ≤ 0.854): adding the driver fingerprint doesn't improve on a driver-agnostic field/composition prediction on this bounded single-season slice.

**This is a thin/near-null driver-term result — and under the no-frame-kill ruling it is a COMPLETE, successful deliverable.** It routes to structural work (multi-season depth, σ-calibration), never abandonment. It is exactly the "size the signal before betting on it" answer the epic was built to produce honestly.

A load-bearing caveat: the probabilistic (log-score) comparison is **vacuous** because the landed #666 fit's grip-term σ (`g_sigma_onesided` ≈ 1e9) inflates the intervals — so the report leads with the σ-robust point metric and routes the σ fix to follow-ons. That σ-calibration is the single lever that would make this diagnostic *probabilistically* informative.

---

## ⇒ TWO DECISIONS WAITING FOR YOU

### 1. #670 allocation decisions (the report's FOR-OWNER block — presented as evidence, NOT decided)
- **Decision 1 — variance shares → Build-2 effort.** Driver-util variance at floor on one season. Less Build-2 effort on the driver axis, or earn the signal back via multi-season depth? Your call.
- **Decision 2 — which axes/channel earn join weight.** Evidence favors utilization over energy, but nothing clears the floor on 2023 alone. Your call.
- **Decision 3 — reference-lap fidelity vs fingerprint work ordering.** The grip-term σ (~1e9) makes the diagnostic's probabilistic score vacuous. Should σ/reference-lap work *precede* further fingerprint work? Your call.
- One caveat to weigh (my D1 adjudication): the held-out composition uses track-geometry that isn't strictly-prior on a 2023-only slice — it's shared across all arms so it doesn't bias the fingerprint-vs-baseline comparison, but the stricter reading is yours to weigh.

### 2. #671 proposed-removal list (nothing deleted — awaits your go/no)
1. `regime_rollup.py` (+ its script/test; repoint one import in `scripts/validate_segment_map_662.py`) — zero prod importers, superseded by #664.
2. `SegmentClassifier.soft_class_membership` bridge method (+ 3 test assertions) — zero non-test callers. **The live tiling `classify_samples` STAYS.** (Nuance I added: also update 4 docstring refs in `corner_attributes.py`.)
3. *(investigate, don't delete)* the unwired ephemeris core in `ideal_lap/` — entangled (pvat_writer live).

---

## Follow-on issues filed (the "structural work" the result routes to)
- **#712 (HIGH)** grip-term σ-calibration (`g_sigma_onesided` ~1e9) — feeds Decision 3.
- **#713 (HIGH)** multi-season held-out re-test of the whole driver term — feeds Decisions 1 & 2.
- #700 correlation-aware σ; #701 fit-cutoff enforcement; #714 rotating-block sensitivity; #715/#704 panel-helper dedup; #698 #666 hardening; #694 axis-specific coverage; #695 calendar-time recency; #696 Builds-2/3 roadmap (graduated to an arch anchor); #703 region-suite test staller; #706/#707/#708 pilot triage; #710 stale-#664-comment repoint; #690/#691/#692/#693 (#664 follow-ons).

## Process notes
- **6 waves, 12 issues**, each dispatched to a delegated Commander in its own worktree, **independently world-verified by the Admiral on the pinned 3.14 interpreter before every merge** (reproduced numbers, re-ran gating, checked diffs for DB-blob/`.agent-work` leakage). Caught and fixed real defects at the gate: 27 pyright errors on the join (#667), 2 broken #660 guard tests (#668), the diagnostic's leakage guards verified non-vacuous (#670).
- **Reversibility contract held** the whole overnight run: the season compute wrote only to isolated scratch DBs; the tracked `data/f1_data_*.db` and the 38GB FastF1 cache were never touched. Everything is git-revertible or regenerable.
- **F12 owner gate:** you signed the panel's REPLICATION_* frozen set; all other frozen constants consumed, none minted inline.
- Two Admiral adjudications on the season diagnostic (D1 composition-as-track-geometry; D2 rotating-block split scheme) — both surfaced in the report for your review.
- Repo clean: all worktrees swept, all branches deleted, main at `0a751cf0`.

Full audit trail: `.agent-work/epic-659/ADMIRAL_LOG.md`.
