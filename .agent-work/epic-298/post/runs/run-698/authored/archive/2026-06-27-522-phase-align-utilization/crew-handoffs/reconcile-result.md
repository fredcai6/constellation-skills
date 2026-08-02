# Reconcile Result — #522 Cartographer Pass

**Date:** 2026-06-26
**Branch:** `feat/522-phase-align-utilization`
**Cartographer pass scope:** G2 lateral units fix (33c56214) + G3 CONTEXTUAL verdict (8970a04f)

---

## What Map Artifacts Were Touched

### `docs/architecture/packets/physics.md`

**What the G3 crew did (8970a04f, already committed):**
- Updated the characterization-finding paragraph in the utilization section to reflect the CONTEXTUAL verdict and credit the lateral units fix.
- Updated the `decision:ideal_lap_sim_two_sided_evaluator` anchor reference to remove the stale "binding constraint is phase misalignment" language.

**What this Cartographer pass added:**
1. Extended the `car_prior.py` module entry with an inline **G2 lateral units fix** paragraph, mirroring the G5 p_max paragraph format:
   - Documents `_assemble_lateral`'s g-unit→m/s² conversion (A0·G, A2·G/air_density, Jacobian `diag(G, G/air_density)`).
   - Documents the default-fallback unconverted path (already convention-A m/s²).
   - Records the **two-producer convention split** as current structural fact: convention A (legacy `LateralEnvelopeFit`/`fit_session_full`, m/s², used by `sim_evaluator`/`fit_batch`) vs convention B (five-view `lateral_view` store, g-units, converted at `car_prior`). Unification to #525.
2. Updated the `decision:ideal_lap_sim_two_sided_evaluator` reference in the Decision Anchors section to note that the anchor also explains the two `car_prior` boundary unit conversions (G5 + G2).

### `docs/architecture/index.md`

1. **Added reconcile header** for 2026-06-26: summary of G2 fix, CONTEXTUAL verdict, two-producer split, open-structural-questions change.
2. **Retired stale triage item** — "Utilization phase-alignment fix (C1 unblock)": the item's current-truth description was wrong post-#522 (`u_braking`/`u_fast_corner` are no longer pinned at 2.0; the lateral units bug was the actual binding constraint, not the phase-alignment confound).
3. **Replaced** with "C1 point-aligned phase confound (secondary)": accurately describes the remaining secondary concern (post-fix values ~0.9–1.0; confound much smaller than the bug; no longer a C1 blocker; future-work, low priority).

### `docs/architecture/overlays/constraints.yml`

1. **Added `claim:lateral_car_prior_boundary_conversion`** — a durable verifiable claim recording:
   - `car_prior._assemble_lateral` is the ONE boundary where five-view store g-unit A0/A2 are converted to m/s².
   - Default fallbacks are already convention-A m/s² and pass through unconverted.
   - Two-producer split is the current structural state.
   - Evidence: commit 33c56214, `test_tunnel_corner_cap_is_realistic` (63.19 m/s).
2. **Added `struct:physics.utilization explained-by decision:ideal_lap_sim_two_sided_evaluator`** — the utilization layer's design is directly explained by that decision (which already fired the C1 review trigger and both boundary-conversion triggers).
3. **Added `struct:physics.utilization verified-by claim:lateral_car_prior_boundary_conversion`** — the claim backs the boundary convention that `struct:physics.utilization` relies on.

### `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md`

Not touched by this Cartographer pass — the G3 crew (8970a04f) correctly updated it with:
- G2 lateral units fix fired trigger (superseding the #518 G6 phase-misalignment finding).
- Updated characterization finding (CONTEXTUAL; numbers grounded in VERDICT.md).

Verified accurate: no stale "NO-GO / phase misalignment binding constraint / clipped at 2.0" claim remains as current truth. The document correctly records phase-alignment confound as a **secondary concern**, not a blocker.

---

## Decision on the Lateral Boundary Conversion Anchor

**Question posed:** Does the lateral g-unit→m/s² boundary conversion at `car_prior` warrant its own `decision:` anchor, or does it extend `decision:ideal_lap_sim_two_sided_evaluator`?

**Ruling: REJECT standalone anchor. EXTEND via claim + fired trigger in existing anchor.**

Rationale:
- The rationale is NOT costly to rediscover from the code: `car_prior.py` module docstring table and `_assemble_lateral` docstring are authoritative and explicit (G5-style documentation already present per G2 reviewer's confirmation).
- The structural consequence (five-view store g-units, `LateralEnvelopeFit` m/s², conversion at `car_prior`) is verifiable from the code in one file.
- The fired-trigger in `decision:ideal_lap_sim_two_sided_evaluator` (G2 #522 section) already names the conversion, the old failure mode (Monaco tunnel 17 m/s), and the fix.
- The G5 (p_max watts→W/kg) precedent is already in the same anchor — both boundary conversions belong there, not scattered into separate anchors.
- A separate anchor would duplicate rather than add authority or planning value.

The `claim:lateral_car_prior_boundary_conversion` (added to `constraints.yml`) is the right level of durability: a short, verifiable assertion that names the boundary and both conventions, surfaceable to a future contributor through the `verified-by` edge on `struct:physics.utilization`.

---

## Verification

- `py scripts/check_arch_map.py` → **39 catalog nodes, 18 packets, 12 overlay nodes. OK: architecture map is consistent.**

---

## Decisions Rejected (not new anchors)

- Total-energy/vehicle-force frame as lateral anchor: NOT applicable (lateral is unchanged).
- "Phase misalignment is the binding constraint": SUPERSEDED — retired from triage items, correct current truth is in VERDICT.md and the decision anchor.

---

## Triage Candidates (future work, not map changes)

| Candidate | Reason | Route |
|-----------|--------|-------|
| Lateral producer-convention unification (#525) | Two-producer split is current truth; unification is a future redesign. The claim records the split; fix is out of scope for Cartographer. | Triage (#525 already filed) |
| Straight under-call (Italy 0.987, Singapore 0.958) | Persists post-fix; power-drag path untouched; not a new defect. | Triage (#525-adjacent audit, per VERDICT.md) |
| `air_density` exactness invariant | Same `ρ` must flow from `build_car_ceiling` to `_assemble_lateral` and to the consumer for A2 exactness. Load-bearing assumption; currently honored. | Triage (#525 should make it explicit in tests or eliminate the dependency) |

---

## What Was NOT Changed

- `decision:c1_driver_utilization_design` — not touched; its four C1 design choices are unaffected by #522.
- `overlays/purposes.yml` — not touched; the old-ontology migration remains a pre-existing triage item.
- `src/` code — Cartographer does not change code.
- `.agent-work/LESSONS.md`, `AGENT_FEEDBACK.md`, `CONSTELLATION_FEEDBACK.md` — correctly excluded per Commander instructions.

---

## Return Status

`complete`
