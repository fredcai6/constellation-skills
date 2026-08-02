# PROBLEM STATEMENT — issue #690

**Reconcile the #664 one-sided grip σ⁺ band scale (whole-lap pace σ) with per-class deficit units.**

Commander run `issue-690`, planning-only engagement (execute and beyond are a separate
engagement). No human reachable: every `user-decision` checkpoint below records the question that
would have been asked, the ruling taken in the human's stead, and the evidence it rests on.

---

## 1. The ask, restated against verified code (not against the issue's framing)

The issue was written at #664 triage time. Since then **#721 landed on `main`**
(`54c7860f`, merging `a5b24249` + `9fae4c9d`) and fixed **two of the three** things the issue text
implies:

| #690's framing | State on `main` today | Residue |
|---|---|---|
| `σ⁺ = hypot(mu, sigma)` folds the ~90 s pace **level** into the band | **FIXED** — `onesided_sigma_from_grip(sigma)` returns `abs(sigma)`; `mu` never enters the scale | none |
| curve evaluated at hardcoded `x=0` | **FIXED** — builder passes `laps=None` → `round(0.5 · cumulative_track_laps_max)` | none |
| whole-lap pace **σ** attached identically to every per-CLASS transit-time deficit | **UNFIXED** | **this issue** |

So #690's real, remaining content is exactly one thing: **the σ⁺ scale is a whole-lap quantity
being written into a per-class row.** Everything else in the issue text is already discharged.

**Confirmed live in real production data** (read-only, archived #670 season run,
`.agent-work/archive/2026-07-27-670-season-run/artifacts/scratch/refutil_season_2023.db`,
2 325 rows):

```
class                  n     avg(g_sigma_onesided)   avg(time_deficit_s)
straight              381   1146998610.5707          1.5332
braking_zone          381   1146998610.5707          0.8848
severity:2023:v1:c0   381   1146998610.5707          3.7457
severity:2023:v1:c1   381   1146998610.5707          0.0036
severity:2023:v1:c2   381   1146998610.5707         -0.0015
severity:2023:v1:c3   381   1146998610.5707          0.1591
```

The σ column is **byte-identical across all six classes** while the deficits it wraps span
0.00–3.75 s. (The 1.1e9 magnitude is the *pre*-#721 store; #721 fixes that magnitude, not this
uniformity. Rebuilding the store does not make the column class-aware.)

And the weights this issue needs **already exist and are already persisted** — `reference_laps`
carries `time_shares_json` per constructor lap and for the field, e.g. Australia-Q:
`straight 0.531 / braking_zone 0.154 / c0 0.162 / c1 0.001 / c2 0.137 / c3 0.015`. The same
quantity is computable in the pure numeric core from `class_ledger.class_time_ledger`
(`time_share_by_class`, structurally summing to 1).

## 2. Success (user-visible outcome) — IQ-001

The `driver_class_observables.g_sigma_onesided` column carries a **per-class** one-sided σ⁺ whose
magnitude is commensurate with that class's own transit-time deficit, such that:

1. the consumer `src/physics/fingerprint/fit.py:_compose_sigma` (which quadrature-adds
   `g_sigma_onesided` per `(driver, class)` cell) stops inflating every cell by the whole-lap
   pace σ;
2. the widths compose back to the lap-level σ under a stated, tested invariant — the direct
   sibling of the map's existing `claim:deficits-sum-to-lap`;
3. the **band-distribution report** W2's acceptance rests on (median / p90 / vacuous count /
   plausible-|D| count) is computed in units that make its numbers comparable at all.

## 3. Protected intent — what must NOT change (IQ-003)

- **The point deficit is untouched.** `speed_deficit_by_class` / `time_deficit_by_class` /
  `lap_time_deficit_s` are byte-identical with and without the G wrap, before and after this
  change. This is the anti-circularity contract (#628) and the module's own binding pre-ruling.
- **μ stays at zero.** Moving the band's centre is #678, explicitly out of scope.
- **G is consumed, never re-fit.** No touch to `grip_baseline.py`, no change to `get_grip_at`'s
  caller-chosen-x contract (its own negative-evidence tests must need zero edits — the same proof
  #721 used).
- **One-sidedness stays.** `decision:g-one-sided-directed-uncertainty` is
  `@grade: settled/inherited` — this issue changes the band's **scale**, not its posture, so no
  decision is being unsettled.
- **No new physical threshold.** A grip-sensitivity model (down-weighting straights because
  rubbering-in doesn't help a power-limited straight) is a modelling claim, not a unit
  reconciliation — recorded as an untaken road, not built.
- **No re-fit, no store schema migration.** Rows are already per `(…, driver, class)`; the column
  already exists. This is a *value* change plus a provenance marker.

## 4. Ambiguities that could make an implementer build the wrong thing (IQ-002) — and the rulings

Each is a decision that would have gone to the human. Ruled here, with the reasoning, per the
engagement's no-human standing instruction.

**D1 — What is the per-class weight?**
*Ruling:* the class's **transit-time share of the lap**, `w_c = t_c / t_lap`, `Σ w_c = 1`
(`class_ledger.class_time_ledger().time_share_by_class`).
*Why:* the issue's own words — "whole-lap pace σ into a per-class **transit-time** band". The σ is
an uncertainty on a lap-**time** level; the deficit it wraps is a class transit **time**; the
unit-coherent bridge between the two is the class's share of lap time. It needs no new physics and
reuses a shipped, invariant-guarded quantity.
`@grade: guess · settle: the band-distribution report's per-class median under time-share vs. the
grip-sensitive variant on the same substrate`

**D2 — Linear share (`w_c·σ`) or quadrature (`√w_c·σ`)?**
*Ruling:* **linear**, `σ⁺_c = w_c · σ_lap`.
*Why:* `get_grip_at` returns **one session-level scalar**. A single common-mode uncertainty
allocated deterministically across the lap contributes `w_c·G` to each class and is *perfectly
correlated* across classes, so the per-class widths **sum** to the lap width. Quadrature encodes an
independence claim (per-class grip errors uncorrelated) that is flatly false for a session-level
grip level, and it would inflate every class (√0.16 = 0.40 ≫ 0.16). Linear is also the only choice
that yields a clean testable invariant. Quadrature recorded as rejected-with-reason.

**D3 — Whose lap supplies the shares: the driver's real lap, the constructor ideal, or the field
reference?**
*Ruling:* the **driver's real lap**, computed in the pure numeric core from `v_real` on the shared
grid.
*Why:* the pure core must stay I/O-free (its stated contract), and the real lap is the one whose
flattery the band is about. The choice is measured **not** load-bearing: the persisted ideal and
field shares differ from each other by <1 % (Australia-Q field `straight` 0.5310 vs Alfa Romeo
0.5319). Document that, don't agonise.

**D4 — Does the store column change meaning, and how does a reader tell?**
*Ruling:* the column keeps its name and gains per-class semantics; `FORMAT_VERSION` bumps
`"1" → "2"` and the column comment states the change.
*Why:* project doctrine is **one canonical path** — a second `g_sigma_onesided_class` column would
create exactly the dual-reader situation `ORCHESTRATOR_CONTEXT.md` forbids without a tracked exit.
Nothing reads `format_version` today (verified: written at three sites, gated nowhere), so the
bump is a free, honest provenance marker and not a compatibility fork.

**D5 — Does #690 build the W2 band-distribution report, or inherit it?**
*Ruling:* **build it here, defensively.** #690's routing comment makes the report the stream's
scored artifact "recomputed at each chain step", and says this issue is the unit reconciliation the
report depends on. No such reporter exists anywhere in `src/`, `scripts/` or `tests/` (verified by
search). Every other W2 chain issue (#679, #678, #687, #686, #688) is still OPEN, so nothing will
supply it first. The gate is authored with an explicit precondition: **if a band-distribution
reporter exists at execution time, extend it — do not mint a second one.**

**D6 — Which substrate does the measurement run on?**
*Ruling:* the **archived real #670 season-run stores** (`refutil_season_2023.db` +
`grip_estimates.db` + `segment_maps.db`, 2023-Q, 21 grip sessions / 2 325 class rows), read-only,
copied to scratch. The "W0-stamped substrate" the spec prefers does not exist yet (W0's store
rebuild is unrun). The report **states its substrate and its retained-session fraction** and is
re-runnable against the stamped store the moment it lands. Per T7, the harness **hard-fails** on an
absent store — it must never `pytest.skip` its own evidence away.

**D7 — Does the deficit scale (0.1–0.2 s) gate this issue?**
*Ruling:* **no.** Owner ruling recorded in #724/the spec: the deficit scale is an **aspiration**,
not an acceptance bar; harness *validity* failures are stop-the-line. #690 is accepted on the
scaling being correct, invariant-tested and measured — not on the number it lands at.

## 5. Local evidence that answered instead of asking (IQ-004)

- `main` @ `54c7860f`, `a5b24249` — what #721 actually changed (read as a diff, not assumed).
- `.agent-work/archive/2026-08-01-r3-721-consumer-units/RESULT.md` — the verified consumer topology
  table for `g_sigma_onesided`, and the measured before/after band distribution.
- `.agent-work/archive/2026-08-01-explore-physics-go-forward/DESIGN_SPEC.md` §W2 + the T7/IF15/T19/
  T20/S12/IF6 amendments — the stream's acceptance shape.
- `docs/architecture/packets/physics.md` — stage D→E→G pipeline, `decision:g-one-sided-directed-
  uncertainty`, `claim:deficits-sum-to-lap`.
- The archived season-run DBs — the defect and the weights, both observed directly.

## 6. First independent gate's closing evidence (IQ-005)

`tests/unit/physics/test_class_utilization_observable.py` green **including** the new width-shape
tests, and `tests/unit/physics/test_class_ledger.py` + `tests/unit/physics/fingerprint/test_fit.py`
green unchanged (the consumed-frozen-module guard, `lesson:consumed-frozen-module-run-guard-tests`),
plus a byte-identity assertion that the point deficits did not move.

## 7. Cartographer baseline before planning? (IQ-006)

**No.** `map_orient` RESOLVED against `docs/architecture/index.md` (76 anchors) and the
`struct:physics.utilization` / `struct:physics.layer2` / `struct:physics.fingerprint` packet nodes
are current — #721's own Cartographer pass (`9fae4c9d`) verified this exact area a day ago and
logged a no-op. Reconcile at the end as normal.

## 8. Workflow fit (IQ-007)

Yes for the code gates (small, sharp, independently verifiable, with a real regression surface in a
consumed module). The measurement gate is where the value is: without it this is a plausible-looking
formula change with no evidence behind it.

## 9. Stated non-goals

Re-fitting G (#678/#687); moving μ (#678); the flying-lap gate (#679); condition regressors
(#686/#688); the final consumer contract (#712, owner's decision at W2's close); the
`compose_and_persist_weekend` complexity debt (#722).

---

## Confirmation

**No human reachable.** Sections 2–4 are the confirmation surface; the seven rulings D1–D7 are taken
by the Commander in the human's stead and are re-openable at the plan-approved checkpoint. The
questions as they would have been put to the human are stated verbatim in the D-headings.
