# Triage recommendations — #664 (all recommend-and-defer)

Delegated run: the launch order grants no explicit issue-filing authority (it directs floating
to the Admiral). All candidates are therefore **recommend-and-defer** — issue-ready below; the
Admiral/human files/routes. None clear the fix-now ladder (each is a cold-start follow-on:
research hardening, a threshold ruling, a data-prep run, or a cross-issue rename).

---
## T1 — Re-point the stale "#664 = Build 3 seeded/supersede" forward-references
- **Labels:** cleanup, stale doc.
- **What:** `segment_map/store.py:24,148-163`, `identity.py:33-34,84-100`,
  `derivation/derive.py:234` name **#664** as "Build 3, the SegmentMap seeded/supersede write
  path" — a different deliverable than #664's actual (reference laps + utilization). Re-point
  these comments to whatever issue now owns Build 3 (seeded/supersede).
- **Importance:** low, but a live mis-reference misleads the next reader of the segment-map
  store; the `write(prior_map=...)` branch correctly remains `NotImplementedError`.
- **Evidence:** floated to the Admiral at #664 understand; confirmed OUT of #664 scope.
- **Acceptance:** the three comment sites cite the correct owning issue (or a note that Build 3
  is deferred); no code change to the write path.
- **Out of scope:** implementing the seeded/supersede write path itself.

## T2 — Reconcile the G σ⁺ band's pace-second scale with the per-class deficit units
- **Labels:** research hardening, unresolved decision.
- **What:** `class_utilization_observable` sets the one-sided σ⁺ = `hypot(mu, sigma)` from
  `get_grip_at`, whose `(mu, sigma)` are grip PACE-seconds; it attaches (correctly, coherently)
  ONLY to the per-class TIME-deficit (seconds). The band is a whole-lap-pace-scale σ combined
  into a per-class transit-time band → a conservatively WIDE envelope. Refine the mapping so the
  band scales to the per-CLASS grip contribution rather than the whole-lap pace swing.
- **Importance:** low while the grip store is empty (σ⁺=0); matters once G is populated (T4).
- **Evidence:** g3 reviewer + implementer both flagged; judged coherent-but-generous, non-blocking.
- **Acceptance:** a per-class G σ⁺ scaling with a documented rationale; unit test the width shape.
- **Out of scope:** moving G's μ off zero (#678); re-fitting G.

## T3 — Frozen-threshold ruling for the dormant `derate_flag` energy-escalation column
- **Labels:** unresolved decision, missing config.
- **What:** `driver_class_observables` carries dormant escalation columns
  (`derate_flag`/`escalation_tier`/`escalation_note`, present-but-NULL per the launch order's
  "escalation layers dormant from day one"). Activating a REAL `derate_flag` needs a frozen
  (F12) energy/derate threshold — which must be a NEW named constant set + re-run, never an
  inline literal.
- **Importance:** low until the energy channel is promoted from descriptive to gated.
- **Evidence:** g3 implementer + reviewer triage note.
- **Acceptance:** a pre-registered F12 derate threshold (owner-signed) before any derate_flag
  is populated from data.
- **Out of scope:** populating derate_flag this run (it stays dormant).

## T4 — Populate the #663 grip-baseline store so the G one-sided band goes live
- **Labels:** dependency cleanup, data prep.
- **What:** the #663 `grip_estimates` store is UNPOPULATED on disk, so #664's G σ⁺ band
  soft-degrades to 0 (point deficits byte-identical — the honest, expected "G barely moves
  utilization" outcome). Running the #663 `grip_batch` to populate `grip_estimates` (season or
  bounded) would make the G band live wherever #664 consumes it.
- **Importance:** medium — the G-band feature is built and tested but dormant until the store
  exists; this is the data-prep that activates it.
- **Evidence:** g4 feasibility probe (no `grip_estimates` table in any data DB; only the #625
  `grip_bin_obs` substrate).
- **Acceptance:** `grip_estimates` populated for the target slice; #664 G σ⁺ non-zero and
  point-unchanged (re-confirm the byte-identical-point invariant on real G).
- **Out of scope:** re-fitting/altering G's methodology (#687/#688 own grip-fit quality);
  #664 consumes G, never re-fits it.

## T5 — Stability of the field-median fingerprint under dropping a constructor
- **Labels:** missing test, research hardening (the `settle:` experiment for
  `decision:field-reference-fingerprint`, graded `guess`).
- **What:** the circuit fingerprint = field-MEDIAN across constructors of per-constructor
  simulated-lap class shares. The g4 jackknife perturbs DRIVER blocks (boundary jitter); it does
  not directly test fingerprint stability under dropping a whole CONSTRUCTOR. Add a
  drop-a-constructor stability check to settle the `guess`-graded decision (→ `settled/measured`
  if stable).
- **Importance:** low-medium; confirms the fingerprint is robust to field composition, as its
  field-conditioned framing assumes.
- **Evidence:** `decision:field-reference-fingerprint` `@grade: guess · settle: g4
  drop-a-constructor stability`.
- **Acceptance:** a reported constructor-drop stability number on a bounded slice; regrade the
  decision accordingly.
- **Out of scope:** ANY fingerprint FITTING (#666, Wave 3).
