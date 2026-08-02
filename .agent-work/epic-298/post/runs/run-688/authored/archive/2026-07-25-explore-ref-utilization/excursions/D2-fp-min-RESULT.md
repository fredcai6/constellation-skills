# D2 — DriverFingerprint minimal interface

Design-it-twice excursion. Interface only (types + signatures + invariants + error modes +
config + persistence shape + per-consumer usage). No implementation. Module home:
`src/physics/utilization/driver_fingerprint.py` (physics region — `struct:physics.utilization`,
sibling of `driver_utility.py`/`car_prior.py`; per `constraint:physics_region_no_evo_import`
physics never imports evo, so the fusion consumer reaches this module the same way
`physics_feature_injection.py` already reaches other physics artifacts — config-gated,
one-directional, evo → physics).

Two things this module explicitly does NOT own, cited so nothing here re-litigates them:

- **The SegmentMap and the per-class time-share vector it emits** (parallel excursions
  `d2-segmap-*`, `xP2-class-noise`, `x1`'s Lineage A). This module receives a *finished*
  `class_time_share` mapping and never touches distance-share→time-share conversion, the
  reference-lap speed profile, or the mixture-fit itself.
- **The class-grain utilization observable store** (upstream of `fit`). This module receives
  observation *rows* and never extracts them from telemetry. Its input contract with that
  store is the one thing it does own (§2).

---

## 1. Core types

```python
Driver = str                    # driver code, e.g. "VER" — same vocabulary as elsewhere in src/physics
RulesEra = str                  # caller-defined era tag (e.g. "2022-2025"); this module does NOT
                                 # define era boundaries — that is owned by config/caller (§7 exclusions)
SegmentClass = int              # opaque class id. NOT hardcoded to k=4 here — whatever vocabulary
                                 # the SegmentMap producer emits (property_mixture.py's soft
                                 # corner-severity classes plus however it represents "straight",
                                 # if at all) flows through unvalidated for semantics, ID-matched only
ClassVocabId = str              # fingerprints a specific fitted class vocabulary/mixture version
                                 # (see Invariant I3 — vocabulary-version scoping)
```

```python
@dataclass(frozen=True)
class FingerprintCell:
    """One (driver, era, segment_class) shrinkage-estimate cell.

    ``utilization`` is the SAME car-normalized ratio convention as
    ``regime_utilization.RegimeUtilization.U_r`` (mean(v_real/v_ideal), ~1.0 = riding the
    ceiling) — generalized from the 4 hard track-position regimes to soft severity classes.
    Car-normalization happens UPSTREAM, in the observable store; this module never sees a raw
    car-conflated speed. Constructor is therefore deliberately NOT part of the grouping key
    (§4) — a driver's cells pool across team changes within an era, on the (already
    car-normalized) ratio.
    """
    driver: Driver
    era: RulesEra
    segment_class: SegmentClass
    vocab_id: ClassVocabId
    mu: float                       # car-normalized utilization ratio, shrunk
    sigma: float                    # effective sigma AFTER shrinkage widening (never raw SEM alone)
    n_support: int                  # count of real (non-imputed) contributing observations
    status: Literal["resolved", "unresolved"]   # explicit-unknown convention, mirrors driver_utility.py
    parent_driver_overall: float    # diagnostic: this driver's across-class shrinkage target
    parent_class_across_drivers: float  # diagnostic: this class's across-driver shrinkage target
    tau_class: float                # between-driver spread within this class (0 = static/universal)

@dataclass(frozen=True)
class FingerprintTable:
    """One era's fitted fingerprint cells. The unit of persistence and of a `join` call."""
    era: RulesEra
    vocab_id: ClassVocabId
    as_of_round: int                 # the causal cutoff this table was fit under (Invariant I1)
    cells: tuple[FingerprintCell, ...]

    def rows_for(self, driver: Driver) -> tuple[FingerprintCell, ...]: ...
    def get(self, driver: Driver, segment_class: SegmentClass) -> FingerprintCell: ...
    def to_frame(self) -> "pd.DataFrame": ...   # bulk export, consumer 5

@dataclass(frozen=True)
class WeekendUtilizationPrior:
    """The JOIN's output — the core product."""
    driver: Driver
    era: RulesEra
    mu: float                        # class_time_share-weighted utilization ratio
    sigma: float                     # honest propagated sigma (Invariant I4)
    classes_used: tuple[SegmentClass, ...]
    thin_classes: tuple[SegmentClass, ...]   # subset of classes_used with status="unresolved"
    weight_on_thin: float            # sum of class_time_share weight riding on thin_classes —
                                      # lets a consumer see how much of the prior is reserved-wide
```

---

## 2. Fit — the slow offline loop

```python
def fit_driver_fingerprint(
    observable_rows: "pd.DataFrame",
    *,
    era: RulesEra,
    as_of_round: int,
    config: FingerprintFitConfig | None = None,
) -> FingerprintTable:
    """Pool class-grain observable rows into one era's shrinkage-estimate FingerprintTable.

    ``observable_rows`` required columns: ``driver, era, segment_class, vocab_id, class_weight,
    utilization, sigma_obs, round_idx, clock``. ``class_weight`` is the SOFT membership
    (0..1, ``property_mixture.posterior_membership``'s convention) the source observable
    attaches to each class — a single realized observation may contribute fractionally to
    more than one class row; this function does not require ``class_weight`` to sum to 1 per
    observation-group (the observable store owns that).

    ``as_of_round`` is REQUIRED, not optional (no silent latest-fallback, per the project's
    as-of planning invariant). Rows are filtered internally to ``round_idx < as_of_round``
    (strictly-pre — same discipline and same rationale as ``car_prior.build_car_ceiling(...,
    strictly_pre=True)``: the #628 leakage-materiality diagnostic found a non-causal ceiling
    running 14.6x the pre-committed materiality bar at one real leverage point; a fingerprint
    used to prime a future weekend's prior has the identical leakage shape if it is allowed to
    see that weekend's own rounds). Fitting a full-era retrospective table (not intended to
    prime any single future weekend) is done by passing ``as_of_round`` one past the era's last
    round — there is no separate "no cutoff" mode.

    Hierarchical Student-t shrinkage: field mean -> driver-overall -> class cell, WITH an
    additional class-across-drivers parent (i.e. each cell has two shrinkage parents, not one
    linear chain) — genuinely new pooling machinery, not a reuse of ``pool_random_effects``
    (single-level, Gaussian DerSimonian-Laird) or ``fit_two_way`` (two crossed axes, no
    hierarchy, Gaussian). Recency weighting uses ``clock`` (a development-clock-shaped
    quantity — round-index convention, not wall time, matching ``car_prior``'s established
    "clock = round_idx" choice over an ``upgrades.yaml`` dependency) with a half-life from
    config. Student-t (not Gaussian) shrinkage at every level is the deliberate heavy-tail
    choice — an outlier session (safety car, one banzai qualifying lap) should not swing a
    cell's mu as hard as a Gaussian pool would let it.

    Every (driver, era, segment_class) triple PRESENT IN observable_rows after the causal
    filter emits exactly one cell (nothing silently dropped, mirrors driver_utility.py's
    explicit-unknown convention): status="resolved" iff n_support >= config.min_resolved_n,
    else "unresolved" with mu/sigma shrunk hard toward the class-across-drivers parent and
    sigma widened to a reserved-wide floor (mirrors estimate_store_fields.effective_axis_sigma's
    contract — reused BY CONVENTION, not by import, since the widening basis here is a
    utilization ratio, not this module's own reference-value population).

    Raises
    ------
    ValueError
        ``observable_rows`` missing required columns; no rows survive the ``as_of_round``
        causal filter; more than one ``vocab_id`` present in the input (a fit call is scoped
        to exactly one class vocabulary — see Invariant I3).
    """
```

```python
@dataclass(frozen=True)
class FingerprintFitConfig:
    student_t_nu: float = DEFAULT_NU_LOSS   # reuse src.common.student_t's project-wide default (4.0),
                                             # not a new invented tail constant
    min_resolved_n: int                     # analogous to driver_utility.MIN_RESOLVED_SESSIONS
    recency_half_life_rounds: float
    reference_value_floor: float            # analogous to REFERENCE_VALUE_FLOOR_MS, in utilization-ratio units
```

---

## 3. Persist / load

```python
def write_fingerprint_table(table: FingerprintTable, path: str) -> None:
    """Replace-on-rerun for (era, vocab_id) — mirrors write_driver_utility_db exactly:
    a plain rerun against the same input reproduces the same rows, never accumulates
    duplicates. UNTRACKED SQLite DB (data/driver_fingerprint.db), table `driver_fingerprint`."""

def load_fingerprint_table(path: str, *, era: RulesEra, vocab_id: ClassVocabId) -> FingerprintTable:
    """Raises ValueError if (era, vocab_id) is absent — no silent cross-era or
    cross-vocabulary substitution (Invariants I2, I3)."""
```

**Persistence shape** (SQLite, table `driver_fingerprint`, PK `(era, vocab_id, driver,
segment_class)`): `era, vocab_id, driver, segment_class, as_of_round, mu, sigma, n_support,
status, parent_driver_overall, parent_class_across_drivers, tau_class, fit_generated_at`. One
row per `FingerprintCell`; `FingerprintTable`'s own `as_of_round`/`era`/`vocab_id` are
redundant on every row by construction (query convenience, same pattern `EstimateStore` uses
for its PK columns already being present in every `EstimateRecord`).

---

## 4. The join — the core product

```python
def circuit_weekend_prior(
    table: FingerprintTable,
    driver: Driver,
    class_time_share: Mapping[SegmentClass, float],
) -> WeekendUtilizationPrior:
    """The deep entry point. Given a circuit's per-class time-share vector (already built by
    the SegmentMap + field-reference-lap machinery — this function does not know or care how),
    return the driver's expected weekend utilization PRIOR: a class_time_share-weighted mean
    and an honestly-propagated sigma.

    sigma composition rule (Invariant I4): Var = sum(w_i^2 * cell_i.sigma^2) over classes with
    w_i > 0 in class_time_share — independent-classes assumption (Exclusion E1), NO extra
    down-weighting or dropping of thin (status="unresolved") cells at join time. A thin cell's
    already-widened sigma from `fit` is what carries its "thin-ness" into the sum; the join's
    job is to propagate that honestly, not to re-decide trust. `weight_on_thin` on the returned
    object is how a caller SEES how much of the answer rode on reserved-wide cells, without the
    join silently discounting them.

    Raises
    ------
    ValueError
        `driver` has zero cells in `table` (never observed this era — Error mode M1, distinct
        from a driver WITH cells that are merely thin/unresolved, which is not an error).
        Any key in `class_time_share` is absent from `table`'s vocabulary, or `table.vocab_id`
        does not match what the caller's SegmentMap was built against (Error mode M2 — the
        caller is expected to have already confirmed vocab compatibility; this is a final
        cross-check, not primary validation owned here).
    """
```

---

## 5. Race side (Build 2) — designed for, not built

```python
@dataclass(frozen=True)
class RaceModeCell:
    """Per (driver, era, segment_class): heavy-tailed push/managed distributions + a
    consistency channel. Reuses src.common.student_t.PredictiveT/predictive_t — the ALREADY
    canonical heavy-tail seam in this repo (project-wide DEFAULT_NU_LOSS + sample-adaptive
    n_eff widening) — not a new Student-t mechanism invented for this module."""
    driver: Driver
    era: RulesEra
    segment_class: SegmentClass
    push: "PredictiveT"          # from src.common.student_t
    managed: "PredictiveT"
    consistency: float           # variance/CV-based, same concept as regime_utilization's "1 - CV"

def race_mode_priors(
    table: "RaceFingerprintTable",
    driver: Driver,
    class_time_share: Mapping[SegmentClass, float],
) -> "WeekendRaceModePrior":
    """Sketch only — signature fixed now so Build 1's shapes don't have to change under it,
    body NOT built. Mirrors circuit_weekend_prior's shape (table, driver, class_time_share) ->
    per-class-weighted aggregate, but returns push/managed PredictiveT + consistency instead of
    a single (mu, sigma). The race simulator consumer (§6.2) does NOT wait for this aggregate
    function — it reads RaceModeCell directly, per class, for correlated draws."""
```

Excluded from this excursion: the fit mechanism for push vs. managed classification (what
observable distinguishes "pushing" from "managing" in the class-grain store), and how
`consistency` composes across classes in the aggregate. Both are Build 2 scope.

---

## 6. Per-consumer usage sketches

**6.1 Practice update** (weekend start, reads the prior, updates weekend-local state only):
```python
table = load_fingerprint_table(FP_DB_PATH, era=era_for(year), vocab_id=segmap.vocab_id)
prior = circuit_weekend_prior(table, driver, segmap.class_time_share(circuit))
weekend_state.driver_utilization_prior[driver] = prior   # weekend-local, never written back to table
```
Read-only against `table`; nothing here ever calls `fit_driver_fingerprint` or
`write_fingerprint_table` (Invariant I1 — slow-loop-only mutation).

**6.2 Race simulator** (per-driver per-class distributions for correlated draws): calls
`table.get(driver, segment_class)` (or `RaceFingerprintTable`'s equivalent) directly per class
the lap's SegmentMap exposes that step to, NOT the aggregate `circuit_weekend_prior`/
`race_mode_priors` join — it needs the un-aggregated per-class cells to draw correlated
class-by-class, not a single collapsed prior.

**6.3 Instrument panel** (variance decomposition + split-half residual replication + σ-honesty,
needs cell-level access with support counts): `table.rows_for(driver)` or `table.to_frame()`
filtered to one driver — reads `n_support`, `tau_class`, both parent diagnostics, and `status`
directly off `FingerprintCell`; cannot use the join (it destroys exactly the per-cell structure
the panel needs to decompose).

**6.4 Fusion feature family** (evo, `(mu, sigma)` summaries per driver): calls
`circuit_weekend_prior` once per driver per weekend — same `(mu, sigma)` shape every other
module feeds `fuse_module_fields_ordered`. Reached via the config-gated
`physics_feature_injection.py` channel (physics never imports evo — `constraint:physics_region_no_evo_import`),
not a direct runtime import of this module from `src/evo_predictor/`.

**6.5 Sizing studies** (bulk read across drivers/eras): `table.to_frame()` per era, or a raw
`pd.read_sql("SELECT * FROM driver_fingerprint WHERE ...")` against the persisted table for
cross-era bulk queries — mirrors the `EstimateStore.load`-style bulk-read convention already
used for sizing/dashboard scripts elsewhere in `src/physics/layer2/`.

---

## 7. Invariants (I1–I4)

- **I1 — slow-loop-only mutation.** `fit_driver_fingerprint`/`write_fingerprint_table` are
  called ONLY by the offline batch job. No consumer path (§6.1–6.5) ever calls them. Weekend
  practice updates are local state, never a table write.
- **I2 — era scoping, no silent fallback.** `load_fingerprint_table` and `circuit_weekend_prior`
  both require an exact `era` match; a table fit for one era is never substituted for another.
- **I3 — vocabulary-version scoping.** `SegmentClass` ids are only meaningful relative to the
  mixture fit that produced them (property_mixture's component ordering is not guaranteed
  stable across refits — x1's stability gate exists precisely because of this). Every
  `FingerprintTable`/cell carries `vocab_id`; `fit` refuses mixed-vocab input; `join` refuses a
  `class_time_share` whose ids don't resolve against the table's `vocab_id`.
- **I4 — σ composition is additive-in-quadrature over independent classes, honestly
  propagated, never re-filtered at join time** (§4). Thinness is priced once, at fit time, via
  the sigma-widening step; the join sums what it's given.
- **Fit before join** — enforced structurally (there is no fit-on-read path in `join`; it takes
  an already-`FingerprintTable`, never `observable_rows`).
- **Causal cutoff is mandatory, not optional** (`as_of_round` has no default) — closes the same
  leakage class the c1 decision's `strictly_pre` extension closed for the car ceiling, applied
  here to the driver side.

## 8. Error modes

| Condition | Behavior |
|---|---|
| M1 — driver has zero cells for the era (never observed) | `circuit_weekend_prior` raises `ValueError` |
| M2 — `class_time_share` key(s) absent from table vocab, or vocab_id mismatch | `circuit_weekend_prior` raises `ValueError` |
| Thin/unresolved cell(s) with nonzero join weight | NOT an error — included, reported via `thin_classes`/`weight_on_thin` |
| Era absent from the persisted DB | `load_fingerprint_table` raises `ValueError` |
| `observable_rows` missing required columns, mixed `vocab_id`, or zero rows survive the causal filter | `fit_driver_fingerprint` raises `ValueError` |

## 9. Exclusions (and why)

- **E1 — no cross-class covariance model.** Classes are pooled as independent in I4's sigma
  rule. A driver's tendency in one severity class plausibly correlates with another (skill
  transfers), but modeling that covariance is a genuinely separate, larger design question
  (would need a full covariance matrix per driver-era, not a diagonal). Flagged, not solved —
  same posture as the c1 decision's `split_is_impure` acknowledgment (carried forward
  unsolved rather than pretending it's fixed).
- **E2 — constructor is not a grouping key.** Deliberate (§1): the observable is already
  car-normalized upstream. Residual impurity (ceiling-estimation error correlating with which
  car a driver was in for a given observation) is inherited from `regime_utilization`'s own
  `split_is_impure=True`, not newly introduced or newly solved here.
- **E3 — era-boundary definition is not this module's job.** `RulesEra` is an opaque
  caller-supplied tag; regulation-era boundaries (e.g. where 2026's rules reset a driver's
  effective sample) are a config/owner decision outside this excursion's scope.
- **E4 — SegmentMap / reference-lap / distance-to-time-share conversion is not this module's
  job.** `class_time_share` arrives finished; this module only validates vocabulary-id
  compatibility, never recomputes or sanity-checks the share values themselves.
- **E5 — Build 2's push/managed classification mechanism is not designed here**, only its
  output type shape and entry-point signature (§5), to avoid a breaking change to Build 1's
  types when Build 2 lands.
- **E6 — no semantic validation of the class vocabulary itself** (e.g. whether it includes a
  "coast" bucket the way the existing 4-hard-regime system explicitly excludes coast as a
  utilization axis). IDs are matched, not interpreted.
