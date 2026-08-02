# Cartographer Reconcile Result — #518 braking-ceiling re-eval

**Date:** 2026-06-25
**Branch:** `feat/518-braking-ceiling-reeval`
**Commit:** `ba2d7733`
**check_arch_map.py:** green (39 nodes, 18 packets, 12 overlays)

---

## Packets / Anchors / Overlays Updated

### `docs/architecture/packets/physics.md`

1. **New module `layer2/decoupled_braking_input.py`** — inserted before the `decoupled_longitudinal.py` entry; documents `build_decoupled_braking_input` as the Variant-A adapter (gravity-free `F_vehicle/m`, `theta=0`, honest per-sample `sigma_a`); records 1 `src/` importer (`session_braking`), WIRED #518 G3.

2. **`decoupled_longitudinal.py` block** — updated from MEASURED-not-wired to WIRED (via `decoupled_braking_input` adapter; 1 src importer chain `session_braking → decoupled_braking_input → decoupled_longitudinal`); HP calibration basis recorded (season-confirmed defaults 2023-Q VER G1 multi-driver).

3. **`scoreboard.CaseInputs` terrain handle** — documented optional `theta`/`z` pool and `has_terrain` property (additive, #518 G3; FLAT byte-identical).

4. **`terrain.py` module entry** — added `altitude_at_positions` (companion to `gradient_at_positions`).

5. **`car_prior.py` block (utilization)** — added G5 units fix note: `_build_longitudinal` converts store `p_max` (watts) to specific power (W/kg) for `theta_P_values`; ideal lap now physical (~333 km/h); store column stays in watts; conversion at param-assembly boundary.

6. **`regime_utilization.py` block** — added three sigma fields: `sigma_u_lapsampling_*` (SEM of regime ratio, lap-sampling noise), `sigma_u_total_*` (quadrature of envelope + lap-sampling), noting the "future lap-sampling hook TODO" is resolved (#518 G4).

7. **Characterization finding** — replaced #510 C1 finding with updated #518 G6 finding on the FIXED physical sim: braking/fast-corner still clip at 2.0 (raw ratios ~3.3×/~3.8×, KNOWN METHOD FLAW = longitudinal phase misalignment); G3 braking recalibration irrelevant (OLD ≈ WIRED, Δ ≤ 0.04); straight crossed `<1 → >1`; overall NO-GO. Phase-alignment fix routed to Triage as C1 unblock.

8. **`decision:decoupled_1d_longitudinal` packet reference** — updated MEASURED→WIRED with HP calibration basis.

9. **`decision:ideal_lap_sim_two_sided_evaluator` packet reference** — updated with G5 fix note and updated characterization finding pointer.

10. **Known Limits** — replaced four stale lines (MEASURED-not-wired, scoreboard retire, terrain metric, gravity-correction) with current-truth entries; added phase-alignment known flaw.

### `docs/architecture/decisions/decoupled-1d-longitudinal.md`

- Status block: updated MEASURED-not-wired → WIRED; HP calibration basis recorded.
- `clean_longitudinal_from_raw` note: updated from "remains the live production path" to "retired as DIRECT braking-frontier input; not deleted (adapter anchor, #498 refinement anchor, throttle/coast input)".
- Review Trigger: struck the fired `#518 wiring` trigger; added `altitude_assumed_flat` threading as new review trigger.

### `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md`

- Current Structural Consequence: added G5 units fix (watts→W/kg conversion, ideal lap now physical ~333 km/h; store column stays watts).
- Updated characterization finding: new full #518 G6 paragraph recording the KNOWN METHOD FLAW (phase misalignment, NOT ceiling depth), updated regime verdicts, and reference to VERDICT.md.
- Review Trigger: struck the fired G5 trigger; replaced "ceiling recalibration" trigger with the phase-alignment fix trigger (the actual C1 unblock).

### `docs/architecture/index.md`

- `struct:physics.layer2` component purpose: updated from MEASURED-not-wired to WIRED via `decoupled_braking_input` adapter.
- Reconcile header: added full #518 reconcile entry.
- Open Structural Questions: retired 4 stale #518-scoped Triage items (wiring, `clean_longitudinal_from_raw` retire, gravity-corrected metric, terrain handle — all resolved in G3). Added 2 new items: (a) utilization phase-alignment fix (C1 unblock, future work); (b) `altitude_assumed_flat` threading through `SessionEstimate` (low priority, triage).

### `docs/architecture/overlays/constraints.yml`

- `explained-by` edge for `struct:physics.layer2 → decision:decoupled_1d_longitudinal`: evidence updated to include `session_braking.py` and `decoupled_braking_input.py` (the wired production modules).

---

## Decision Adjudications

| Candidate | Disposition | Rationale |
|---|---|---|
| `decoupled_1d_longitudinal` status update (MEASURED→WIRED) | UPDATED anchor | Wiring is current structural truth; HP calibration basis must be on record |
| `ideal_lap_sim_two_sided_evaluator` G5 units fix + updated characterization | UPDATED anchor (two additions) | G5 fix fired a Review Trigger; characterization finding materially changed on the physical sim |
| `smoother_rounds_braking_knee` caveat resolved for braking | NOTED in Known Limits / reconcile prose | Short verifiable fact, not a multi-faceted rationale; no new anchor warranted |
| Phase-alignment as standalone decision anchor | REJECTED as anchor; ROUTED to Triage | The fix is future work; the current method flaw is documented in the existing anchors and Known Limits; a new anchor would be for when the fix is adopted |
| Gravity-counted-exactly-once as standalone constraint | REJECTED | Covered by `decision:decoupled_1d_longitudinal` rationale + module docstring; promotion to durable constraint would be high-maintenance with low planning payoff |

---

## Triage Candidates (not added to map — future work)

1. **Utilization phase-alignment fix** — replacing the point-aligned `v_real/v_ideal` comparison with a phase-aligned or per-regime capability-frontier comparison. Proven C1 unblock on the physical (#518 G6); binding structural blocker for trustworthy `u_braking`/`u_fast_corner`. Route: new issue.
2. **`altitude_assumed_flat` threading through `SessionEstimate`** — currently hardcoded `False`; the wired braking path uses terrain, so honest threading is possible. Low-priority correctness item.
3. **Four other non-RBR constructors in `physics_estimates_g3wired.db`** — Ferrari/McLaren/Williams/Mercedes remain OLD-seeded (only RBR r1–15 wired); continuation via `scripts/repopulate_g3wired_store.py --resume`.

---

## Map-Check Result

```
Parsed 39 catalog nodes, 18 packets, 12 overlay nodes.
OK: architecture map is consistent.
```

---

## Commit

`ba2d7733` — `docs(arch): reconcile #518 braking-ceiling re-eval into map`

Changes committed. No src/ or tests/ touched.

---

## Workflow Feedback

- The Commander's brief covered all 7 items clearly. The most substantive judgment call was item 5 — the updated characterization finding: the #518 G6 verdict directly superseded the #510 characterization on the fixed sim; I updated the packet prose and the decision anchor rather than keeping the old finding alongside. This is correct (current-truth only; old finding was confounded by the G5 bug).
- The `purposes.yml` old-ontology Triage item (uses deprecated `purpose:`/`serves` overlay kinds) was pre-existing and deliberately not touched — map-model says to migrate, but that is a separate curated pass and would risk a map-check regression if done partially. Left as-is in Triage.
- Items 1 (MEASURED→WIRED) and 2 (smoother_rounds_braking_knee retire caveat) are the most structurally significant map changes; the rest are additive documentation of confirmed new structure.
