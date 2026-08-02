# Cartographer Reconcile Result — Issue #447 (Phase 0b Telemetry Instrument Characterization)

**Date:** 2026-06-11
**Branch:** issue-447-instrument-characterization
**Commits reconciled:** c56291a, 3b0f87b, c4b659c

---

## Map Artifacts Edited

### 1. `docs/architecture/packets/preprocessing.md`

Added a new **Phase 0b — Telemetry Instrument Characterization (#447)** section (before Key References) covering:
- The two characterization scripts (G1, G2) as packet prose (non-structural; scripts are not map nodes)
- The key measured durable truth: both raw streams are two separate irregular grids at ~4.2 Hz median, NOT the "240/10 Hz" figure, NOT a shared grid. Includes base-tick difference, timestamp overlap %, and consequence for Phase 1 (must register streams to a common time base).
- White-jitter time-tag error model (~0.13 s IQR) and inter-stream offset stability verdict (stable estimable bias, 6/6 sessions).
- Cross-reference to `docs/physics/measurement_model.md` as the durable physics contract.

Added `docs/physics/measurement_model.md` to Key References with its role described.

### 2. `docs/architecture/index.md`

Prepended a new "Reconciled 2026-06-11 for Phase 0b telemetry instrument characterization (#447)" line above the #446 line. Captures:
- New doc `docs/physics/measurement_model.md` as the durable physics contract (measurement model, noise covariances, GO/NO-GO brief, F1 band recommendation, F3 s_finish design decision)
- Key measured truth (two-separate-grids fact, white-jitter, stable offset)
- G1/G2 scripts as non-structural evidence producers
- `offline_loader.py` docstring correction (was "~240 Hz / ~10 Hz"; now correctly states two separate ~4.2 Hz irregular grids)
- No new src/ structural nodes, edges, or overlays

---

## What Was NOT Changed

- No new container/component YAML nodes (no new src/ structural nodes)
- No overlay changes (constraint:physics_region_no_evo_import was already added in #446; it covers #447 work without modification)
- No new edge types
- No decision anchor files authored (see Decision Candidate section below)

---

## Decision Candidates Evaluated

**F1 covariance-gate band recommendation (keep (0.5, 2.0) on offset-removed residual):**
- Disposition: **Rejected** as a map-level durable anchor. The gate default already matches the recommendation; no code change was made. The recommendation is fully captured in `docs/physics/measurement_model.md` §9. Short verifiable assertion, not cross-cutting — does not warrant a separate `decision:` anchor file. Captured as packet prose reference.

**F3 s_finish free-anchor design decision:**
- Disposition: **Rejected** as a current-structure map anchor (no code change was made; this is a documented Phase 1 design input). Fully captured in `docs/physics/measurement_model.md` §10. When Phase 1 implements it, the implementing Cartographer run should evaluate promotion to a `decision:` anchor at that time.

**Two-separate-grids measured truth:**
- Disposition: **Captured as packet prose** in `preprocessing.md` (local to one struct; already backed by `offline_loader.py` docstring and `measurement_model.md`). Does not need a separate `claim:` overlay node — the Inclusion Rule is served by the packet prose for planning (Phase 1 will read this) and rule preservation (prevents wrong grid assumption).

---

## check_arch_map.py Result

```
Parsed 37 catalog nodes, 16 packets, 11 overlay nodes.
OK: architecture map is consistent.
```

Run before and after edits — both clean. No new nodes were added so node count is unchanged.

---

## Open Structural Questions Surfaced

None new. Existing open questions table in index.md is unchanged.

The F3 (s_finish free-anchor) implementation will require a `packets/preprocessing.md` update when Phase 1 lands the code change — not routing to Triage because it's already a known planned Phase 1 item documented in `measurement_model.md` §10 with clear implementation criteria.

---

## Summary

Two map artifacts edited; map passes validation. The key durable fact (two-separate-grids at ~4.2 Hz, white-jitter, stable offset) is now recorded in the preprocessing packet and index. The measurement model document is registered as the Phase 0b/1 physics contract. No new structural nodes, overlays, or decision anchors were needed.
