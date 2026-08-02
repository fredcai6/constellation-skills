# D2 — DriverFingerprint interface, common-caller-first

Design excursion, interface only (no implementation beyond signatures). Scope per the
handoff: the module's job is owner-ruled and fixed (per-(driver, rules-era) class-level
utilization cells, hierarchical Student-t shrinkage, circuit-composition join, slow-loop
mutation only). This document designs the shapes and signatures around the two callers
that dominate ergonomics/performance: the practice-update caller and the race simulator.

## What was read before designing

`src/physics/utilization/{driver_utility.py,driver_utility_observable.py,car_prior.py,
regime_utilization.py,driver_utility_gate.py}`, `src/physics/layer2/{pooling.py,
estimate_store.py,property_mixture.py,regime_rollup.py}`, `src/common/student_t.py`,
`src/evo_predictor/{physics_feature_injection.py,runtime_contracts.py}`,
`src/physics/weekend_state/model.py`, `src/physics/regulation_era.py` (existence check),
`docs/agents/ORCHESTRATOR_CONTEXT.md`, and three prior excursions in this same batch:
`x1-RESULT.md` (circuit-fingerprint machinery inventory), `x3-RESULT.md` (driver-observable
inventory), `P2-RESULT.md` (k=4 severity-class noise check), `P6-RESULT.md` (push/managed
context-classifier probe). Findings from those excursions are load-bearing design inputs,
cited inline below.

---

## 0. Ground truth this design stands on (not re-derived, cited)

- **The class taxonomy already exists and is validated, but unwired.**
  `src/physics/layer2/property_mixture.py::fit_property_mixture` fits a BIC-selected,
  support-floored Gaussian mixture over `(log10 radius_m, lateral_g)`, `k_range=(2,4)`,
  producing **soft/fractional** membership (`posterior_membership`, shape `(N, k)`, rows
  sum to 1 — never a hard per-corner tag). `regime_rollup.py::circuit_distance_share`
  already computes the circuit-side vector this design's JOIN needs
  (`corner_class_{i}_distance_share`), validated by a real held-out-circuit stability gate
  (5/5 pass, `docs/physics/625-regime-time-share.csv`). Per `x1-RESULT.md`, this whole
  lineage is tagged **MEASURED-not-wired** — zero `src/` importers today. This design is
  the first production consumer.
- **k=4 severity-class granularity is usable signal, not mush**, per `P2-RESULT.md`: noise
  ratio (within-driver scatter ÷ between-driver separation) across the 4 severity classes
  (1.93–2.40) is indistinguishable from the existing macro `slow_corner`/`fast_corner`
  regimes (2.32–2.39) already shipped in `regime_utilization.py`. Point support per class
  (~309/driver-weekend) is *better* than the thinnest existing macro regime (`fast_corner`
  ~163, min 70). This licenses fitting fingerprint cells at the finer k-class grain instead
  of the current 4 hard tiling regimes.
- **`straight`/power is excluded from this taxonomy.** `driver_utility_gate.py` already
  rules `STRAIGHT_AXIS` a `confounded_negative_control` (the causal ceiling under-predicts
  straight speed via DRS/slipstream — not a driver-skill axis). The fingerprint's class
  vocabulary is **corner-severity only** (`property_mixture`'s k classes), matching that
  established ruling. `circuit_distance_share`'s `straight_distance_share` is never joined
  against a fingerprint cell.
- **Push/managed is a declared simulator abstraction, not an observed data mode.**
  `P6-RESULT.md` ran a context-signal soft classifier on 5,380 real 2023 race laps and
  found the push/managed split is **not bimodal** in observed data (r=-0.227 against
  fuel-corrected pace, ~69% of laps in an ambiguous middle, 2 of 3 "known-push" sanity
  contexts failed to separate). The owner's brief already frames push/managed as something
  Build 2 *constructs* (a config-driven transform of one fingerprint cell into two
  distributions), not something Build 1 discovers. This design keeps that boundary sharp:
  `DriverFingerprint` never claims two modes; `push_managed_split` (race-table build config)
  is the ONLY place two-mode structure is manufactured, and it is swappable without
  touching any other type in this document.
- **Reusable pooling primitives already exist and fit this problem shape exactly:**
  `src/physics/layer2/pooling.py::fit_two_way(values, teams, circuits) -> TwoWayPool`
  decomposes a parameter into `grand_mean + team_effect + circuit_effect`, each
  empirical-Bayes shrunk, with `.predict(team, circuit)`. Applied with `teams=driver,
  circuits=class_id` this is **exactly** "field mean → driver-overall → class cell +
  class-across-drivers parent" from the brief, with zero new statistical machinery.
  `pool_random_effects` (DerSimonian-Laird) and `src/common/student_t.py::predictive_t`
  (the project-wide `(mu, sigma, n_eff) -> Student-t(nu, loc, scale)` seam, already used
  for exactly this "thin support → fat tail" job elsewhere) complete the fit.
- **`RegulationEra.for_season(year)`** (`src/physics/regulation_era.py`) is the existing
  rules-era seam — reused as the `rules_era` key, not invented fresh.

---

## 1. Types

```python
# src/physics/utilization/driver_fingerprint/types.py

SegmentSeverityClassId = int          # 0..k-1, ordinal by severity (0=tightest)
RulesEra = str                        # RegulationEra.for_season(year).name — see regulation_era.py

@dataclass(frozen=True)
class ClassTaxonomyRef:
    """Which severity-class vocabulary a cell / composition vector is expressed in.
    A class_id is meaningless without this pin — every cross-boundary call carries it,
    and every consumer must assert equality before indexing by class_id."""
    taxonomy_version: str             # content/date-stamped tag of the MixtureFit that produced these ids
                                       # e.g. "property_mixture_638_2026-07-18_k4"
    k: int                            # 2..4 (property_mixture.py's k_range ceiling)
    class_labels: tuple[str, ...]     # len == k, e.g. ("tight","medium","fast","very_fast")

@dataclass(frozen=True)
class FingerprintCell:
    """One (driver, rules_era, class_id) utilization cell — the STORE's atom."""
    driver: str
    rules_era: RulesEra
    taxonomy: ClassTaxonomyRef
    class_id: SegmentSeverityClassId
    mean_deficit_ms: float            # g = v_ideal - v_real (m/s), NEVER a ratio — matches
                                       # driver_utility_observable.py's absolute-deficit convention
    sigma_ms: float                   # dispersion of the SHRUNK estimate (already reflects
                                       # thin-cell inflation — see FIT)
    nu: float                         # Student-t df for this cell's predictive distribution, > student_t.NU_FLOOR
    n_eff: float                      # effective support behind mean/sigma (> 0; a pooling-weight
                                       # sum, NEVER a raw row count — see FIT)
    n_raw_points: int                 # raw track-point count contributing (diagnostic ONLY)
    consistency: Optional[float]      # 1 - CV of the per-point deficit within the cell, in [-1,1];
                                       # None if fewer than MIN_REGIME_POINTS points (mirrors
                                       # regime_utilization.py's existing consistency metric, reused)
    status: Literal["resolved", "thin", "unresolved"]
    fit_run_id: str                   # provenance: which offline fit run produced this row
    updated_at: str                   # ISO8601

@dataclass(frozen=True)
class DriverFingerprint:
    """All persisted cells for one (driver, rules_era) — unit of the fit/store round-trip."""
    driver: str
    rules_era: RulesEra
    taxonomy: ClassTaxonomyRef
    cells: tuple[FingerprintCell, ...]  # len == taxonomy.k EXACTLY, one per class_id, in class_id
                                        # order — ALWAYS fully populated (status="unresolved" rather
                                        # than a missing row; mirrors driver_utility.py's
                                        # "nothing dropped silently" contract)

@dataclass(frozen=True)
class WeekendPrior:
    """Circuit-conditioned utilization prior for one driver at one weekend — the JOIN's
    output and the entirety of what the practice-update caller needs."""
    driver: str
    event_id: str
    taxonomy: ClassTaxonomyRef
    per_class_weight: np.ndarray       # (k,) circuit_distance_share's corner_class_i shares;
                                        # sums to <= corner_distance_share, NOT 1.0 (straight excluded — see §0)
    expected_deficit_ms: float         # per_class_weight . per_class_deficit_ms — the scalar prior
    expected_deficit_sigma_ms: float   # honest propagated sigma — see join.py below
    per_class_deficit_ms: np.ndarray   # (k,) cell means, class_id order
    per_class_sigma_ms: np.ndarray     # (k,)
    per_class_nu: np.ndarray           # (k,)
    per_class_status: tuple[str, ...]  # (k,)
    missing_classes: tuple[int, ...]   # class_ids with status != "resolved"
    missing_driver: bool               # True iff FingerprintStore had no row at all for this driver
    composition_is_distance_share: bool = True  # regime_rollup's documented LOWER BOUND on true
                                        # corner time-share (x1 finding) — carried as an explicit
                                        # caveat flag, never silently treated as time-weighted
```

---

## 2. STORE

```python
# src/physics/utilization/driver_fingerprint/store.py

class FingerprintStore:
    def __init__(self, db_path: str): ...

    def write_fingerprints(self, fingerprints: Sequence[DriverFingerprint]) -> None:
        """Replace-on-rerun for the EXACT (driver, rules_era, taxonomy_version) slices
        touched (mirrors driver_utility.py::write_driver_utility_db's replace contract —
        a plain rerun reproduces the same rows, never accumulates duplicates). SLOW-LOOP
        ONLY: the only caller is fit.py's build_driver_fingerprints; never called from a
        weekend-local or race-sim path."""

    def read_fingerprint(
        self, driver: str, rules_era: RulesEra, taxonomy_version: str,
    ) -> Optional[DriverFingerprint]:
        """Single-driver point read (indexed PK lookup). Returns None — NOT a fabricated
        neutral fingerprint — when the driver has zero cells for this (era, taxonomy);
        the caller (runtime.py) owns the missing-driver fallback contract."""

    def read_fingerprints_bulk(
        self, drivers: Sequence[str], rules_era: RulesEra, taxonomy_version: str,
    ) -> dict[str, DriverFingerprint]:
        """Bulk read, ONE query (`WHERE driver IN (...)`), not N round-trips. The race-sim
        preload path and sizing studies both use this. Drivers absent from the returned
        dict are the caller's missing-driver cases (same contract as the single-read path)."""
```

### Persistence shape

SQLite table `driver_fingerprint_cells`, PK `(driver, rules_era, taxonomy_version, class_id)`
— one flat row per cell (mirrors `estimate_store.py`'s flatten-to-scalars-plus-provenance
convention, not a nested blob):

```
driver TEXT, rules_era TEXT, taxonomy_version TEXT, taxonomy_k INTEGER,
class_id INTEGER, class_label TEXT,
mean_deficit_ms REAL, sigma_ms REAL, nu REAL, n_eff REAL, n_raw_points INTEGER,
consistency REAL NULL,
status TEXT,                 -- 'resolved' | 'thin' | 'unresolved'
fit_run_id TEXT, updated_at TEXT
PRIMARY KEY (driver, rules_era, taxonomy_version, class_id)
```

---

## 3. FIT (offline, slow-loop only)

```python
# src/physics/utilization/driver_fingerprint/fit.py

def build_driver_fingerprints(
    observable_rows: pd.DataFrame,
    *,
    taxonomy: ClassTaxonomyRef,
    min_resolved_n_eff: float,          # generalizes driver_utility.py's MIN_RESOLVED_SESSIONS=3
                                         # to a continuous n_eff floor (soft membership means
                                         # "3 sessions" isn't a countable integer anymore)
    nu_loss: float = student_t.DEFAULT_NU_LOSS,
    tail_rule: student_t.TailRule = student_t.FormulaRule(),
    fit_run_id: str,
) -> list[DriverFingerprint]:
    """Hierarchical shrinkage: field mean -> driver-overall -> class cell +
    class-across-drivers parent, via TWO REUSED stages — no new statistical machinery.

    Stage A — point estimate (fit_two_way, REUSED as-is, axes reinterpreted):
        pool = src.physics.layer2.pooling.fit_two_way(
            values=observable_rows['g_class'], teams=observable_rows['driver'],
            circuits=observable_rows['class_id'])
        pool.grand_mean       == "field mean"
        pool.team_effects[d]  == "driver-overall" for driver d
        pool.circuit_effects[c] == "class-across-drivers parent" for class c
        pool.predict(driver, class_id) == the shrunk point estimate for that cell —
        literally "field mean -> driver-overall -> class cell" collapsed to one call.
        (fit_two_way's "team"/"circuit" naming is a REUSE of the existing team x circuit
        decomposition machinery with driver/class substituted for team/circuit — same
        method-of-moments variance components and BLUP shrinkage, no new code path.)

    Stage B — dispersion + tail (pool_random_effects + predictive_t, REUSED):
        for each (driver, class_id) cell, pool_random_effects over that cell's raw
        (g_class, sigma_lapsampling) rows gives sigma_mu and per-row weights; n_eff is
        the sum of normalized weights (an effective, not raw, count — same idea as
        every other n_eff in this codebase, see student_t.py's own contract). Then
        student_t.predictive_t(mu=pool.predict(driver, class_id), sigma=sigma_mu,
        n_eff=n_eff, nu_loss=nu_loss, rule=tail_rule) supplies (nu, scale) — "thin
        cells -> fat sigma" IS predictive_t's sqrt(1 + 1/n_eff) inflation, already
        built, tested, and used elsewhere in this codebase for the identical job.

    consistency: computed the same way regime_utilization.py already computes it
    (1 - CV of the per-point deficit within the cell's soft-membership-weighted point
    set) — reused metric, new axis (class instead of macro regime).

    status: "resolved" (n_eff >= min_resolved_n_eff), "thin" (0 < n_eff < floor — cell
    emitted with real, if wide, values), "unresolved" (zero raw rows for this
    (driver, class_id) — cell STILL emitted, mean falls back to
    pool.circuit_effects[class_id]-only i.e. class-parent-conditioned field prediction
    with driver_effect=0, sigma widened per the SAME effective_axis_sigma convention
    estimate_store_fields.py already establishes). Every (driver, class_id) pair in
    taxonomy.k x the observable rows' driver set gets EXACTLY one row.

    Input contract (observable_rows) — THE GENERALIZATION THIS FIT REQUIRES UPSTREAM:
    one row per (driver, rules_era, class_id, session/round key), with a SOFT-membership-
    weighted deficit already collapsed per class:
        g_class_i = sum_points(membership[pt, i] * deficit[pt]) / sum_points(membership[pt, i])
        n_points_i = sum_points(membership[pt, i])     # fractional support, not integer
    This is driver_utility_observable.py's G1 computation GENERALIZED from 4 hard tiling
    masks to property_mixture.posterior_membership's k soft memberships. Building that
    generalized observable producer is OUT OF SCOPE for this interface (a sibling build
    item — the current driver_utility_observables.db does not exist on disk per x3, so
    there is no live producer to point at yet); build_driver_fingerprints only specifies
    the schema it needs to consume.

    Mutates the STORE (via FingerprintStore.write_fingerprints), never a weekend-local
    object. Run per rules_era SEPARATELY (a regulation change invalidates cross-era
    pooling — physical evidence from a ground-effect car says nothing about a
    high-rake car). Scheduled/manual re-fit job only; never on a live weekend path.
    """
```

---

## 4. JOIN

```python
# src/physics/utilization/driver_fingerprint/join.py

def join_circuit_composition(
    fingerprint: DriverFingerprint,
    circuit_class_share: np.ndarray,   # (k,) from regime_rollup.circuit_distance_share's
                                        # corner_class_{i}_distance_share, SAME taxonomy_version
    *,
    event_id: str,
) -> WeekendPrior:
    """THE JOIN. Pure function, no I/O — both inputs are already resolved by the caller
    (FingerprintStore.read_fingerprint; circuit_class_share cached per event, read once
    per weekend from regime_rollup's artifact or a future live equivalent).

    Point estimate — soft-membership-weighted expectation:
        expected_deficit_ms = sum_i circuit_class_share[i] * cell[i].mean_deficit_ms

    Honest sigma — variance-of-a-weighted-sum, cells treated as INDEPENDENT across
    class (v1; no cross-class covariance modeled for one driver — same posture
    physics_feature_injection.py already takes for cross-entity covariance: diagonal
    only, documented as v1, not a silent omission):
        expected_deficit_sigma_ms = sqrt(sum_i (circuit_class_share[i] * cell[i].sigma_ms)^2)

    This is the mechanism that makes a thin/unresolved cell ACCEPTABLE on the hot path:
    a class with circuit_class_share[i] ~ 0 contributes ~0 to both the mean and the
    sigma regardless of how wide that cell's own uncertainty is — a circuit with no
    tight hairpins does not care that the driver's tight-hairpin cell is unresolved.

    Raises ValueError if circuit_class_share.shape != (fingerprint.taxonomy.k,), or if
    the composition vector's own taxonomy pin (carried by the caller alongside it,
    checked by the caller before this call — join_circuit_composition itself only has
    fingerprint.taxonomy to check shape against) doesn't match fingerprint.taxonomy.
    taxonomy_version — never silently reinterpret one taxonomy's class_id 2 as another's.
    """
```

---

## 5. Hot path (a) — practice update

```python
# src/physics/utilization/driver_fingerprint/runtime.py

def fetch_weekend_open_prior(
    store: FingerprintStore,
    circuit_composition: np.ndarray,   # (k,) pre-resolved by the caller (cached per event —
                                        # see "Other consumers" for who resolves this)
    *,
    driver: str,
    rules_era: RulesEra,
    taxonomy_version: str,
    event_id: str,
) -> WeekendPrior:
    """The weekend-open call: ONE fingerprint read + ONE join, called ONCE per
    (driver, weekend) — at FP1, or whenever the caller's weekend-local Bayesian state is
    first initialized. NOT called again as later FP sessions land: the FP1/FP2/FP3
    Bayesian updates happen entirely inside the CALLER's OWN weekend-local state object
    (outside this module), using this WeekendPrior as the t=0 prior. FingerprintStore is
    NEVER touched again for the rest of the weekend — fingerprints are frozen
    (owner-ruled invariant, restated not redesigned).

    Missing driver (FingerprintStore.read_fingerprint returns None): returns a
    WeekendPrior with expected_deficit_ms=0.0 (field-neutral — exactly fit_two_way's
    grand_mean semantics, the least-informative honest default), expected_deficit_sigma_ms
    = NEUTRAL_DRIVER_SIGMA_MS (a named config constant, not inline), every per_class_status
    = "unresolved", missing_driver=True — mirrors physics_feature_injection.py's
    missing-constructor fallback EXACTLY (never silently imputed, never dropped, flagged
    in the output for the caller to see).

    Performance envelope: single-driver, single-event. NOT a hot loop — called at most a
    handful of times per weekend (once per driver at FP1). Budget: <5ms including the
    store read (indexed SQLite point lookup on the 4-column PK) + the join's O(k)
    arithmetic (k <= 4). No batching need; this call's ergonomics (simplicity, one driver
    in, one prior out) dominate over throughput, unlike (b).
    """
```

---

## 6. Hot path (b) — race simulator (the FAST path)

```python
@dataclass(frozen=True)
class RaceDistributionTable:
    """Precomputed, race-local, ARRAY-DENSE table — the ONLY thing the race simulator's
    inner sampling loop touches. Built ONCE per race (or once per Monte-Carlo batch) by
    build_race_distribution_table; never re-fit, re-joined, or dict-looked-up per draw.

    Every array is shape (D, k, 2) — driver-major, class-second, mode-last (push=0,
    managed=1), C-contiguous — so table.nu[driver_idx, class_id, mode_idx] for a whole
    (n_draws,) index array stays a single vectorized numpy gather, and downstream
    rng.standard_t(nu_array, size=n_draws) draws the whole batch in one call with no
    per-draw Python-level branching or object construction.
    """
    driver_ids: tuple[str, ...]        # index -> driver, len D
    taxonomy: ClassTaxonomyRef
    nu: np.ndarray                     # (D, k, 2) float64, Student-t df, > student_t.NU_FLOOR
    loc: np.ndarray                    # (D, k, 2) float64, location (m/s deficit)
    scale: np.ndarray                  # (D, k, 2) float64, > 0
    consistency: np.ndarray            # (D, k) float64 in [-1, 1] — ONE channel per
                                        # (driver, class), MODE-INDEPENDENT (see note below)
    resolved_mask: np.ndarray          # (D, k) bool — False for an unresolved/missing cell;
                                        # numeric arrays stay finite and usable regardless,
                                        # this is a diagnostic the caller MAY ignore
    driver_index: dict[str, int]       # driver -> row index, for the caller assembling
                                        # per-race driver order


def build_race_distribution_table(
    fingerprints: dict[str, DriverFingerprint],  # from FingerprintStore.read_fingerprints_bulk,
                                                  # ALL drivers in the race, resolved ONCE
                                                  # before the sim starts
    *,
    push_managed_split: PushManagedSplitConfig,  # OWNER-RULED, config-driven, NOT data-derived
                                                  # (see §0 — P6 found no clean bimodal split in
                                                  # observed race pace; this config MANUFACTURES
                                                  # the two-point abstraction Build 2 needs)
    nu_loss: float = student_t.DEFAULT_NU_LOSS,
    tail_rule: student_t.TailRule = student_t.FormulaRule(),
) -> RaceDistributionTable:
    """Builds the dense table ONCE per race. For each (driver, class_id): reads the
    resolved FingerprintCell and applies push_managed_split to produce TWO
    (nu, loc, scale) triples via student_t.predictive_t (REUSED) — push and managed
    differ in how push_managed_split transforms the cell's (mean_deficit_ms, sigma_ms)
    before the predictive_t call (e.g. push tightens toward the cell's demonstrated
    ceiling, managed relaxes toward a wider execution margin) — the EXACT transform is
    push_managed_split's business, config-owned, deliberately NOT hardcoded here so it
    can be recalibrated (or eventually replaced by a data-derived split, if P6's honest
    null is ever overturned by better data) without touching this function's signature.

    Missing/unresolved cells: same neutral-fallback numbers as fetch_weekend_open_prior
    (field mean, NEUTRAL_DRIVER_SIGMA_MS-derived scale), resolved_mask=False at that
    (driver, class) — the numeric arrays are ALWAYS finite, so a caller that ignores
    resolved_mask still gets a usable (if uninformative) draw rather than a NaN
    propagating through a million-draw simulation.

    Performance envelope: O(D * k) predictive_t calls (D <= ~24 drivers, k <= 4 ->
    <= 96 calls total across both modes = 192), each O(1) — built ONCE per race/batch,
    amortized over millions of downstream draws. This is NOT the hot loop; it is the
    hot loop's setup cost. Flag for the implementer: benchmark actual predictive_t
    per-call cost against a <50ms race-table-build budget before committing to it as a
    hard number.
    """


def sample_segment_times(
    table: RaceDistributionTable,
    driver_idx: np.ndarray,    # (n_draws,) int, which driver each draw is for
    class_idx: np.ndarray,     # (n_draws,) int, which severity class
    mode_idx: np.ndarray,      # (n_draws,) int in {0, 1}: push=0 / managed=1
    *,
    rng: np.random.Generator,
) -> np.ndarray:
    """THE hot-path call — fires millions of times per race simulation batch, one call
    per BATCH of draws (not one call per draw). Pure array indexing + one vectorized
    rng.standard_t call:

        nu    = table.nu[driver_idx, class_idx, mode_idx]      # (n_draws,)
        loc   = table.loc[driver_idx, class_idx, mode_idx]     # (n_draws,)
        scale = table.scale[driver_idx, class_idx, mode_idx]   # (n_draws,)
        return loc + scale * rng.standard_t(nu, size=n_draws)  # Generator.standard_t
                                                                 # accepts an array df

    No Python-level per-draw branching, no dict/dataclass construction inside the call.

    Deliberately does NOT model cross-class or cross-mode CORRELATION for one driver
    within a lap (e.g. "this driver chose to push this lap" should correlate mode_idx
    across all of that lap's segments, not be drawn independently per class). That
    composition is the CALLER's (Build 2's) job, built on table.consistency — exposed
    for exactly this purpose (a per-(driver,class) consistency scalar the sim can feed
    into its own mode-persistence or copula model). This module computes and hands the
    consistency channel over; it never consumes it. Baking a fixed correlation
    structure into this function would freeze a race-simulator design decision that
    does not belong to the fingerprint module.

    Raises ValueError if any of driver_idx/class_idx/mode_idx is out of range — checked
    ONCE via a vectorized np.any(...) bounds check at the top of the call, never
    per-element (would defeat the point of vectorizing).
    """
```

---

## 7. Other consumers (adapt around the hot two)

- **Instrument panel (cell access + support counts).** Reads `FingerprintStore.
  read_fingerprint(driver, era, taxonomy)` directly and iterates `.cells` for a debug
  table (mean/sigma/n_eff/status/consistency per class). No new API — pays the STORE's
  per-cell dataclass granularity directly, which is fine at human-driven, low-QPS access.
  Never touches `RaceDistributionTable` (see §8).
- **Fusion feature family ((μ,σ) summaries).** Needs the SAME `ModuleFieldResult` shape
  `physics_feature_injection.py` already produces (entity-space `pi`/`sigma_pi` vectors,
  `entity_scope="driver"`). This is a NEW thin adapter module living in `src/evo_predictor/`
  (mirroring `physics_feature_injection.py` exactly), calling `join_circuit_composition`
  per driver and packing `expected_deficit_ms`/`expected_deficit_sigma_ms` into `pi`/
  `sigma_pi` — NOT part of `DriverFingerprint` itself, since evo must not import
  `src.physics.utilization` directly (`ORCHESTRATOR_CONTEXT.md`'s data/physics/evo boundary
  — physics/preprocessing do not couple directly to evo). This is the same boundary
  `physics_feature_injection.py` already crosses via `read_feature_view_at`; the
  fingerprint module would need an equivalent read-only seam function exposed from
  physics for evo to call, not a redesign of `WeekendPrior`/`RaceDistributionTable`.
- **Sizing studies (bulk reads).** `FingerprintStore.read_fingerprints_bulk` across many
  drivers/eras — already the bulk-read path both the race-sim preload and this consumer
  share; no separate API needed.

---

## 8. Invariants

- Fingerprints **never move during a weekend** — the only writer is `fit.py`'s
  `build_driver_fingerprints`, called from an offline/scheduled job, never from
  `runtime.py` or any weekend-local/race-sim path.
- A `class_id` is meaningless without its `ClassTaxonomyRef.taxonomy_version` pin —
  every function that receives both a fingerprint/table and a composition vector
  asserts the versions match before indexing.
- No cross-`rules_era` pooling, ever — `fit.py` runs per era, `store.py`'s PK includes
  `rules_era`, `runtime.py` requires it as an explicit argument (no silent "latest era"
  fallback, per `ORCHESTRATOR_CONTEXT.md`'s "no silent latest fallback" planning
  invariant).
- Every `(driver, class_id)` combination present in the fit's input population gets
  exactly one persisted cell — `status` is explicit (`resolved`/`thin`/`unresolved`),
  nothing is dropped silently (generalizes `driver_utility.py`'s existing contract).
- `straight`/power is never a class in this taxonomy (§0) — the corner-severity classes
  only.
- `RaceDistributionTable`'s numeric arrays (`nu`, `loc`, `scale`) are always finite for
  every `(driver, class, mode)` cell, even when `resolved_mask` is `False` — a caller
  that ignores the mask never gets a NaN mid-simulation.

## 9. Ordering

1. **Offline (slow loop):** observable producer (sibling build item, out of scope here,
   §3) → `build_driver_fingerprints` → `FingerprintStore.write_fingerprints`. Run per
   `rules_era`, on a schedule/manual trigger, never mid-weekend.
2. **Weekend open (FP1):** `fetch_weekend_open_prior` (one call per driver) →
   caller's own weekend-local Bayesian state object seeded with the returned
   `WeekendPrior` → that state object updates itself as FP2/FP3/sprint data lands,
   entirely outside this module.
3. **Race sim setup (once per race/batch):** `FingerprintStore.read_fingerprints_bulk`
   → `build_race_distribution_table` → hand the resulting `RaceDistributionTable` into
   the simulator's inner loop.
4. **Race sim inner loop (millions of times):** `sample_segment_times`, batched, driven
   by whatever driver/class/mode index arrays the simulator's own timestep loop
   assembles.

## 10. Error modes

- **Missing driver** (no store row): `WeekendPrior.missing_driver=True` /
  `RaceDistributionTable.resolved_mask` all-`False` for that driver — never an
  exception, never a silent zero-information object indistinguishable from a resolved
  one (the flag is load-bearing).
- **Taxonomy version mismatch** between a fingerprint/table and a composition vector or
  index array: `ValueError`, fail fast — never a silent reinterpretation of `class_id`.
- **Shape mismatch** (`circuit_class_share.shape != (k,)`, index arrays not matching
  `driver_ids`/`taxonomy.k`/mode range): `ValueError` at the top of the call, checked
  once via a vectorized predicate, not per-element.
- **Cross-era read**: `rules_era` is a required, non-defaulted argument everywhere —
  there is no "current era" global to fall back to.
- **Unresolved cell used downstream**: never an error — `status="unresolved"` /
  `resolved_mask=False` cells still carry finite, honestly-wide numbers (field-mean
  fallback + widened sigma), by design (§0, §8).

## 11. Config

- `ClassTaxonomyRef` itself is config (which `MixtureFit` run is authoritative) —
  pinned per era, not a code constant.
- `min_resolved_n_eff` (fit.py) — generalizes `driver_utility.py`'s
  `MIN_RESOLVED_SESSIONS=3` to a continuous floor.
- `nu_loss`, `tail_rule` — reused directly from `student_t.py`'s existing project-wide
  defaults (`DEFAULT_NU_LOSS=4.0`, `FormulaRule(nu_prior=2.5, k=1.0)`); overridable per
  fit run / per race-table build, not hardcoded inline.
- `NEUTRAL_DRIVER_SIGMA_MS` — named constant, the missing-driver fallback scale (mirrors
  `physics_feature_injection.py`'s `neutral_sigma` config field, not an inline literal).
- `PushManagedSplitConfig` — owner-ruled, race-table-build-only config; the ONE place
  the two-mode abstraction is manufactured (§0, §6).

## 12. Performance envelope (summary)

| Call | Frequency | Budget | Shape |
|---|---|---|---|
| `fetch_weekend_open_prior` | ~1×/driver/weekend | <5ms | scalar in/out, O(k) |
| `build_race_distribution_table` | ~1×/race or MC batch | <50ms (flag: unbenchmarked) | O(D·k), D≤~24, k≤4 |
| `sample_segment_times` | millions of draws/race, batched | vectorized, O(n_draws), zero Python-level per-draw work | dense array gather + one `standard_t` call |

## 13. What the hot-path bias cost the other consumers, and why it's acceptable

- **Instrument panel loses nothing** — it never touches `RaceDistributionTable` at all;
  it reads `FingerprintCell` dataclasses directly through `store.py`, which stayed
  human-readable (named fields, not array indices) specifically because that consumer's
  ergonomics don't compete with the race sim's.
- **`WeekendPrior` collapsing the join to one scalar** (`expected_deficit_ms`) costs
  nothing to a consumer wanting per-class detail instead — the per-class vectors
  (`per_class_deficit_ms`, `per_class_sigma_ms`, etc.) are carried alongside the scalar,
  not discarded. The bias is in ordering (scalar first, for the common case), not
  information loss.
- **`push_managed_split` being config-manufactured rather than data-derived is a real,
  named cost to statistical honesty** — Build 2 gets a fast, discrete two-mode sampler at
  the price of an unvalidated bimodality assumption P6 already found absent in observed
  race data. This is accepted because the race simulator's hot-path requirement (fast,
  vectorizable, discrete mode selection) structurally dominates; the cost is contained by
  keeping the split fully swappable (a config object, not baked into `RaceDistributionTable`'s
  shape) so a future better-supported split — or an honest single-mode fallback — can
  replace it without touching `sample_segment_times`'s signature.
- **Fixing the class taxonomy at `k <= 4`, fit once per era offline**, costs an
  instrument-panel user (or any future consumer) wanting finer-grained classes a full
  re-fit-and-restore round trip rather than a live parameter — accepted because
  fingerprints are explicitly slow-loop-only by owner ruling, and P2's noise check
  found k=4 is already at the edge of usable support (~309 pts/driver-weekend per class,
  not comfortably above it) — going finer would need new data volume, not just a config
  change, so freezing k in the offline fit is not leaving performance on the table for a
  caller who can't use it yet anyway.
- **The array-dense `RaceDistributionTable` is opaque for ad-hoc debugging** (a human
  wants "VER, class 2, push" not `table.nu[7, 2, 0]`) — acceptable because
  `driver_index`/`taxonomy.class_labels` are carried on the table specifically so a
  debug wrapper can translate names to indices without the hot path itself paying that
  cost.

---

**Deliverable file:** `C:\Programs\f1Brainz\.agent-work\explore-ref-utilization\excursions\D2-fp-caller-RESULT.md`
