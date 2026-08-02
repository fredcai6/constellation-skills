# D2-fp-flex — DriverFingerprint interface, designed for maximum flexibility

**Brief:** design the store+fit+join interface for the driver-fingerprint module (owner-ruled
job: class-level utilization cells per (driver, rules-era), fit via hierarchical Student-t
shrinkage from the class-grain observable store, joined against a circuit's per-class
time-share vector into an expected-weekend-utilization prior) so that every named escalation
layer — sub-phase cells, transition/compound-class cells, segment-discriminativeness
weighting, management-efficiency, energy-channel cells, era-changing class vocabulary, and
far-future low-rank factorization — activates without breaking a consumer that ignores it.
Organizing idea: a **versioned cell-address space**.

Grounded in: `src/physics/utilization/driver_utility.py` (explicit resolved/unresolved status
+ `effective_axis_sigma` reserved-widening convention), `driver_utility_observable.py`
(anti-circularity, absolute-deficit-not-ratio contract), `car_prior.py` (`strictly_pre`
causal-ceiling convention), `src/physics/layer2/pooling.py` (`pool_random_effects`
DerSimonian–Laird, `fit_drift`), `src/physics/layer2/estimate_store.py` (wide-column axis
schema — read as a **cautionary** precedent, see Complexity costs), `property_mixture.py` /
`segment_classifier.soft_class_membership` (the mixture-membership machinery this reuses), and
the `explore-ref-utilization` `IDEAS_BOARD.md` owner rulings (cycle-3 q1–q7 vocabulary
lifecycle, cluster B fingerprint mechanism, x1's Lineage A/B circuit-share gap).

---

## 1. The core idea: CellAddress is the one thing that grows

Every escalation the brief lists is, structurally, either **a new dimension of *where* a
utilization value lives** (sub-phase, transition, energy channel, era/vocabulary) or **a new
dimension of *what* is being measured at a fixed address** (push vs managed vs
management-efficiency vs consistency — "slot"), or **a weighting applied at fit time that
never touches the address at all** (segment-discriminativeness). Keeping those three
categories distinct is what lets most escalations cost zero schema change.

```python
@dataclass(frozen=True)
class CellAddress:
    """A versioned address into the driver-fingerprint cell space.

    era:
        Rules-era key (e.g. "2022_ground_effect", "2026_active_aero"). The unit at which
        class vocabulary is independently fit and pooled — owner ruling: "era pooling =
        cross-circuit class identity." A cell in one era is NEVER compared numerically to
        a cell in another era without going through `era` explicitly.
    class_vocabulary_version:
        Which fitted severity-class ladder (`ClassVocabulary`, §2) `class_id` is meaningful
        against, for this `era`. Mandatory, not optional — see Invariant I2.
    class_id:
        Severity-class id (int), meaningful ONLY as (era, class_vocabulary_version, class_id).
        k varies by era/vocabulary (today's mixture ceiling is k<=4; nothing here assumes 4).
    subphase:
        None (whole-class cell — the grain every cell has TODAY) | "entry" | "apex" | "exit".
        Escalation dimension #1. Open string, not a closed enum (a future taxonomy addition
        costs nothing at this layer).
    channel:
        "utilization" (default, everything live today) | "energy" | future channel names.
        Escalation dimension #2 (energy-channel cells) — WHICH PHYSICAL QUANTITY the deficit
        is measured in. Open string; validated against a `KNOWN_CHANNELS` registry (warn, not
        hard-fail, on an unregistered value — see §6 config).
    transition_from:
        None (steady-state cell, the default) | class_id of the PRECEDING class, for a
        transition/compound-class cell. Escalation dimension #3. `transition_from == class_id`
        (self-transition) is invalid — enforced at construction.

    Deliberately ABSENT from this address: corner identity (arc-length / per-corner id).
    Owner ruling (cycle-3 q2): "NO cross-year corner-history... class-membership-only for the
    join; corner identity... only for the dormant discriminativeness layer." Corner identity
    lives in the OBSERVABLE row (§4), never in the join-facing cell address — this is why
    segment-discriminativeness weighting is the cheapest escalation in this design (§5.3).
    """
    era: str
    class_vocabulary_version: int
    class_id: int
    subphase: Optional[str] = None
    channel: str = "utilization"
    transition_from: Optional[int] = None

    def __post_init__(self):
        if self.transition_from is not None and self.transition_from == self.class_id:
            raise ValueError(f"CellAddress: transition_from == class_id ({self.class_id}); "
                              f"a class cannot transition into itself")

    def grain(self) -> "CellGrain": ...   # derived: CLASS if subphase/transition both unset, else finer

    def collapsed_to(self, grain: "CellGrain") -> "CellAddress":
        """Return the coarser address this cell rolls up to at `grain` (drops subphase
        and/or transition_from; NEVER changes era/class_vocabulary_version/class_id/channel).
        Identity when self is already at `grain` or coarser. See §3 collapse semantics."""
```

`CellAddress` is hashable/orderable (canonical field-tuple order matches declaration order) so
it can key a `dict` or a DataFrame MultiIndex without a second encoding — but persistence uses
a canonical string key (`cell_key`, §6) rather than relying on tuple/NULL ordering in SQL, for
reasons in §6.

**Explicitly not an address dimension:** push/managed/management-efficiency/consistency. Those
are answers to "what distribution", not "where" — they live in `slot` (§2, a string on the
*cell record*, not the address) so adding one is a new row, never a new address field.

---

## 2. Class vocabulary — versioned separately from the cells that use it

```python
@dataclass(frozen=True)
class ClassVocabulary:
    """One era's fitted severity-class ladder. Wraps property_mixture.MixtureFit (reused,
    not reinvented) with the versioning + stability-gate provenance the fingerprint needs.

    era: rules-era key (matches CellAddress.era).
    version: monotonic per-era counter. Bumped whenever the mixture is REFIT for this era
        (new data, new k, new component params) — a routine DATA event, no store migration.
    k: component count actually selected (support-driven, per property_mixture's own gate).
    mixture: the underlying MixtureFit (log-radius/lateral-g components + scaler).
    stability_verdict: "pass" | "fail" — the F12 held-out-circuit stability gate, evaluated
        PER ERA (owner ruling: "F12 stability gate = per-era acceptance"). A "fail" vocabulary
        can still be persisted (transparency) but `fit_driver_fingerprint` (§4) refuses to fit
        against it by default (`allow_unstable_vocabulary=False`) — an explicit override, never
        a silent downgrade.
    fitted_at: ISO timestamp.
    """
    era: str
    version: int
    k: int
    mixture: "MixtureFit"
    stability_verdict: str
    fitted_at: str

def soft_membership(vocab: ClassVocabulary, radius_m: np.ndarray, lateral_g: np.ndarray) -> np.ndarray:
    """(N, k) fractional class membership — thin wrapper over the existing
    segment_classifier.SegmentClassifier.soft_class_membership / property_mixture.posterior_membership
    seam, NOT reimplemented. Reused for BOTH the observable-row class assignment (§4) and the
    circuit time-share vector's own soft weighting (§3) — one membership function, two callers,
    guaranteeing the driver-side and circuit-side classes are assigned identically."""
```

**Why version vocabulary separately from `CellAddress.class_id` instead of folding k/boundaries
into the address itself:** a vocabulary is a big fitted object (mixture components, scaler,
stability gate) that changes rarely and is shared across every driver and every circuit for an
era; a cell address is a small hashable key that changes per driver/class/dimension. Coupling
them in one struct would mean every cell carries a copy of the mixture fit. Keeping them apart
means `class_vocabulary_version` in `CellAddress` is a *reference*, and vocabulary compatibility
is a single equality check at join time (Invariant I2), not a per-cell cost.

---

## 3. The join — circuit time-share × driver cells, address-reconciled

```python
@dataclass(frozen=True)
class Distribution:
    """A (location, scale, shape) summary — NOT assumed Gaussian (owner principle #2: no
    baked-in normality). `kind` is an open string so a new shape costs nothing at this type.
    """
    kind: str            # "gaussian" | "student_t" (open; unknown kind => consumer treats as
                          # gaussian with a logged warning, never a silent drop)
    mu: float
    sigma: float
    df: Optional[float]  # student_t only
    n_support: int
    status: str           # "resolved" | "unresolved" | "reserved" — reused verbatim from
                           # driver_utility.py's explicit-unknown convention

@dataclass(frozen=True)
class CircuitClassShare:
    """One circuit-layout's per-cell time-share vector for one (era, vocabulary).

    era, class_vocabulary_version: must match the fingerprint being joined against
        (Invariant I2) — this is what makes CircuitClassShare a first-class citizen of the
        SAME versioned address space as DriverFingerprint, not a parallel ad hoc schema.
    layout_version: circuit-map version (cycle-3 q2's "map version cited per observable row"
        ruling, extended to the share vector itself).
    shares: dict[CellAddress, float]. Keys populated ONLY at whatever grain the circuit-side
        producer currently computes (today: CLASS grain, channel="utilization",
        transition_from=None, subphase=None — Lineage A's regime_rollup once it's cross-walked
        from distance-share to time-share, per x1's named open gap). Sums to 1.0 over the
        populated key set. NOT required to populate every dimension CellAddress supports —
        see the reconciliation rule below.
    n_laps: int
    fitted_at: str
    """
    era: str
    class_vocabulary_version: int
    circuit: str
    layout_version: str
    shares: dict         # dict[CellAddress, float]
    n_laps: int
    fitted_at: str


def join_fingerprint_to_circuit(
    fingerprint: "DriverFingerprint",
    circuit_shares: CircuitClassShare,
    *,
    slot: str = "utilization",
) -> Distribution:
    """The linear join (owner: "exactly the thing"): expected weekend utilization =
    sum_c share_c * cell_c.mu, honest sigma = sqrt(sum_c share_c^2 * cell_c.sigma^2)
    (v1 treats cells as independent across class_id — see Complexity costs #2 for the
    correlated-cells caveat this glosses over).

    ADDRESS RECONCILIATION (the mechanism every escalation example in §7 relies on):
    `circuit_shares.shares` keys define the join's OWN grain — call it G. Before multiplying,
    every cell in `fingerprint` is collapsed (§3.1) to grain G. This means a finer-grained
    fingerprint (e.g. subphase-decomposed) joins CORRECTLY against a coarser circuit-share
    vector with NO caller-visible change — the collapse happens inside the join, always.

    Raises
    ------
    VocabularyMismatchError: fingerprint.era/class_vocabulary_version != circuit_shares'
        (Invariant I2 — no silent cross-vocabulary join).
    ShareCoverageError: a circuit_shares key's collapsed-fingerprint cell is "unresolved" with
        no reserved effective_sigma fallback available (should not happen in practice — every
        DriverFingerprint cell is TOTAL, see Invariant I1 — kept as a defensive error, not
        a silent skip).
    """
```

### 3.1 Collapse: the mechanism, stated once

```python
def collapse_cells(cells: list["DriverFingerprintCell"], target: CellAddress) -> "DriverFingerprintCell":
    """Fold every cell in `cells` (all of which must collapse to `target` under
    CellAddress.collapsed_to) into ONE cell at `target`, via `pool_random_effects`
    (REUSED, not reinvented — same DerSimonian-Laird machinery every other cross-session
    pool in this codebase uses). A single flat pool over all matching finer cells in one
    call — never a sequential pairwise reduction across dimensions — so the result is
    ORDER-INDEPENDENT regardless of which dimensions are being collapsed or in what order
    a caller enumerates them (Invariant I3).
    """
```

`load_fingerprint` (§4) and `join_fingerprint_to_circuit` both route through `collapse_cells`;
it is the only place collapse logic lives.

---

## 4. Fit + store

```python
@dataclass(frozen=True)
class ClassObservableRow:
    """One driver's per-cell deficit observation from one session — the class-grain analog
    of driver_utility_observable.RegimeDeficits, generalized to the versioned address.
    A finer observable row (subphase/channel/transition populated) maps DIRECTLY to a finer
    fingerprint cell with no translation layer, because both use CellAddress.

    corner_id: OPTIONAL, dormant. Arc-length-within-layout-version corner identity — carried
        on the OBSERVABLE ROW ONLY (never promoted into CellAddress, per the owner's no-
        cross-year-corner-history ruling). Consumed exclusively by discrim_weight derivation
        (§5.3) and the dormant per-corner discriminativeness diagnostic; the fit and the join
        never group or key by it.
    """
    driver: str
    session_key: tuple            # (year, gp_name, session_type) — recency anchor
    cell: CellAddress
    slot: str                     # "utilization" | "push" | "managed" | ... (open, §2)
    value: float                  # deficit, in cell.channel's native unit
    sigma_lapsampling: float
    n_points: int
    corner_id: Optional[str] = None
    discrim_weight: float = 1.0   # §5.3 — fit-time-only, never an address dimension


@dataclass(frozen=True)
class FingerprintFitConfig:
    era: str
    vocabulary: ClassVocabulary
    recency_half_life_sessions: float    # exponential recency weight; NO trajectory/drift
                                          # model (owner: culled as "science-projecty")
    min_resolved_n: int                  # MIN_RESOLVED_SESSIONS-style threshold, same convention
    shared_systematic_floor: float       # -> pool_random_effects(shared_floor=...)
    allow_unstable_vocabulary: bool = False   # refuses a "fail"-verdict ClassVocabulary unless set


def fit_driver_fingerprint(
    rows: Iterable[ClassObservableRow],
    *,
    config: FingerprintFitConfig,
) -> "DriverFingerprint":
    """Hierarchical Student-t shrinkage: field mean -> driver-overall -> class cell,
    + class-across-drivers parent (two crossed partial-pooling levels, each level reusing
    pool_random_effects — the SAME reuse discipline driver_utility.py already established,
    not a new pooling implementation). Recency weighting via config.recency_half_life_sessions.
    Groups rows by (driver, cell, slot). A (driver, cell, slot) combination with ZERO rows still
    emits a reserved cell (status="unresolved", widened effective_sigma via effective_axis_sigma
    — REUSED verbatim) so a consumer never silently reads a missing cell as zero (Invariant I1).
    """


class DriverFingerprintStore:
    """SQLite-backed, long/tidy schema (§6). One row per
    (driver, era, class_vocabulary_version, cell_key, slot)."""

    def __init__(self, db_path: str, *, must_exist: bool = False): ...

    def upsert_cells(self, driver: str, cells: list["DriverFingerprintCell"]) -> None:
        """SLOW-LOOP-ONLY write path (two-speed update ruling). Lives in a module the
        weekend-local practice-update loop does not import — enforced by import topology,
        same trust level the rest of this codebase uses for producer/consumer splits."""

    def load_fingerprint(
        self, driver: str, era: str, *,
        class_vocabulary_version: Optional[int] = None,   # None = latest for era
        grain: "CellGrain" = CellGrain.CLASS,
        slot: str = "utilization",
    ) -> "DriverFingerprint":
        """The read path every consumer uses. Prefers a cell DIRECTLY STORED at `grain`
        over a collapsed one when both exist (Invariant I4 — this is what makes "identical
        results until someone opts in" a byte-identical guarantee, not just an approximate
        one — see §7.1). Falls back to collapse_cells over finer stored cells when no direct
        row exists at `grain`. Raises CellNotAvailableError if `grain` is FINER than
        anything stored for this driver/era/slot (collapse only ever goes fine -> coarse,
        never the reverse — Invariant I5)."""

    def load_bulk(self, drivers: list[str], era: str, **kw) -> dict:
        """Sizing-study consumer: one query, same grain/collapse semantics as load_fingerprint."""

    def cell_support(self, driver: str, era: str, cell: CellAddress, slot: str) -> "CellSupport":
        """Instrument-panel consumer: n_support, tau, status, fitted_at — WITHOUT the mu/sigma
        payload, so a variance-decomposition/replication check can't accidentally trust an
        unresolved cell's point value."""
```

`DriverFingerprintStore` is one implementation of a read-only `FingerprintReader` Protocol
(`load_fingerprint`/`load_bulk`/`cell_support`, same signatures). This is the seam the
far-future low-rank factorization escapes through (§7.7) — a factorized producer is a *second*
implementation of the same Protocol, not a new consumer contract.

---

## 5. Per-consumer usage sketches

1. **Practice update** (weekend-local, read-only, two-speed boundary):
   ```python
   prior = store.load_fingerprint(driver, era, slot="utilization")
   expected = join_fingerprint_to_circuit(prior, circuit_shares)
   # weekend-local state updates from `expected` (F10 fp_representativeness-weighted);
   # never calls upsert_cells.
   ```
2. **Race simulator** (Build 2 — per-class push/managed distributions):
   ```python
   push    = store.load_fingerprint(driver, era, slot="push")
   managed = store.load_fingerprint(driver, era, slot="managed")
   consistency = store.load_fingerprint(driver, era, slot="consistency")
   # per-lap draw source chosen by race state; consistency widens/narrows the draw.
   ```
3. **Instrument panel** (cell-level access, support counts, σ-honesty):
   ```python
   support = store.cell_support(driver, era, cell, slot="utilization")
   # variance decomposition / split-half replication read n_support/tau/status directly,
   # at whatever grain is actually stored — no join required.
   ```
4. **Fusion feature family** ((μ,σ) summaries):
   ```python
   dist = store.load_fingerprint(driver, era, slot="utilization").cells[addr]
   feature = (dist.mu, dist.sigma)
   ```
5. **Sizing studies** (bulk reads):
   ```python
   fps = store.load_bulk(all_drivers, era, slot="utilization")
   # same collapse/grain semantics per driver, one query
   ```

### 5.3 Segment-discriminativeness weighting — the zero-schema escalation

`ClassObservableRow.discrim_weight` (default `1.0`, uniform) is fed into `pool_random_effects`
as a per-observation precision multiplier inside `fit_driver_fingerprint`. Turning this on
changes **only the weights**, computed from `corner_id` (dormant, observable-row-only field,
never promoted to `CellAddress` per the owner ruling in §1). `CellAddress`, `DriverFingerprint`,
`DriverFingerprintStore`, and every consumer signature are untouched. This is the cheapest
escalation in the whole design, by construction — the reason the address explicitly excludes
corner identity is exactly to keep this one free.

---

## 6. Persistence / versioning shape

Table `driver_fingerprint_cells`, one row per (driver, era, class_vocabulary_version, `cell_key`,
slot):

| column | notes |
|---|---|
| `driver`, `era`, `class_vocabulary_version` | as above |
| `cell_key` | **canonical non-NULL string encoding of CellAddress** — `f"{class_id}\|{subphase or ''}\|{channel}\|{transition_from if transition_from is not None else ''}"`. See gotcha below. |
| `class_id`, `subphase`, `channel`, `transition_from` | denormalized copies of the address fields, kept queryable (WHERE subphase IS NULL) without parsing `cell_key` |
| `slot` | open string, validated against `KNOWN_SLOTS` (warn-only) |
| `mu`, `sigma`, `effective_sigma`, `status`, `tau`, `n_support` | same shape as `driver_utility.py`'s output columns |
| `fitted_at` | ISO timestamp |

**PRIMARY KEY = (driver, era, class_vocabulary_version, cell_key, slot).** `cell_key` exists
specifically because **SQLite treats NULL as distinct from every other NULL in a
UNIQUE/PRIMARY KEY**, so a naive PK over `(..., class_id, subphase, channel, transition_from,
slot)` would silently fail to dedupe two rows that both have `subphase=NULL` — an
`INSERT OR REPLACE` would happily insert duplicates instead of upserting. Coalescing every
optional dimension into one non-NULL canonical string sidesteps that trap entirely; this is a
concrete instance of "flexibility costs complexity" worth flagging up front rather than
discovering at integration time.

**Column additivity:** the four denormalized address columns above are the FULL set this
design ever expects to need for the named escalations (class_id/subphase/channel/
transition_from). Adding a genuinely new address dimension beyond what's listed here is a real
schema migration (ALTER TABLE, additive, mirroring `estimate_store._migrate_missing_columns`).
Adding a new **vocabulary_version** or a new **slot** is a pure data event — no migration.

**Regeneration discipline (required policy, not optional):** whenever subphase/transition/
channel cells for a `(driver, era, class_id)` are refit, the corresponding whole-class,
steady-state, `channel="utilization"` cell for that same `(driver, era, class_id)` MUST be
regenerated in the SAME write (derived via `collapse_cells` over the new finer cells, then
upserted) — never left as a stale row from before the finer fit existed. This is what makes
Invariant I4 (prefer-direct-row) safe: without this rule, a direct class-level row and a
live-collapsed one could silently diverge (see Complexity costs #3).

---

## 7. Worked examples — each escalation, in full

### 7.1 Sub-phase cells turn on (the brief's named example, in depth)

**Before:** `class_vocabulary_version=3`, every stored row has `subphase=NULL`
(`cell_key` encodes it as `""`). `load_fingerprint(driver, era, slot="utilization")` (default
`grain=CLASS`) finds a **direct** row per class_id and returns it as-is.
`join_fingerprint_to_circuit` collapses (trivially, no-op — already at grain G) and sums.

**Activation:** a new fitter pass runs with `subphase` populated, producing THREE new rows per
`(driver, class_id)` — `subphase="entry"|"apex"|"exit"` — via `fit_driver_fingerprint` against
observable rows that now carry populated `cell.subphase`. Per the regeneration discipline
(§6), the SAME write also re-derives the whole-class row from those three via `collapse_cells`
and upserts it, replacing (not duplicating) the prior direct row.

**After, for an unmodified caller:** `load_fingerprint(..., grain=CLASS)` (default, unchanged
call site) still finds a **direct** row per class_id — now freshly regenerated, but at the same
key, same shape, same semantics. `join_fingerprint_to_circuit` against an unmodified
`circuit_shares` (still CLASS-grain keys) is byte-for-byte the same call path. The practice
update, fusion feature family, and sizing-study consumers above never pass `grain=`, so none of
them change behavior or code.

**For a consumer that opts in:** the race simulator (or instrument panel) calls
`load_fingerprint(..., grain=SUBPHASE)` and receives the three-way decomposition — new code,
additive, doesn't touch anyone else.

### 7.2 Transition/compound-class cells

Default `transition_from=None` cells are unaffected when transition cells are added — they're
additional rows at NEW addresses (`class_id=X, transition_from=Y`), not replacements. The
asymmetry worth naming: **the circuit side must also escalate** for this axis to have any
effect on the join — a `CircuitClassShare` that never reassigns time-share mass from
steady-state to transition cells means `join_fingerprint_to_circuit`'s reconciliation collapses
the driver's transition cells right back into their steady-state parent before multiplying
(there's no share-key to multiply the finer cell against). This is the one escalation with a
real cross-side coordination cost — flagged in Complexity costs #4.

### 7.3 Energy-channel cells

Default `channel="utilization"` everywhere. Energy work adds rows with `channel="energy"` at
the same `(class_id, subphase)` grain. `load_fingerprint(..., channel="utilization")` (the
default) is unaffected. A consumer wanting the energy channel passes `channel="energy"`
explicitly — new parameter, old call sites untouched.

### 7.4 Management-efficiency as a new axis

Not a `CellAddress` change at all — it is a new **slot**. `derive_management_efficiency(push_cell,
managed_cell) -> Distribution` computes a derived quantity from the existing `slot="push"` /
`slot="managed"` cells and writes it back as `slot="management_efficiency"` at the same address.
Any consumer that never asks for that slot never sees it.

### 7.5 Class vocabulary changing between rules eras

A new `era` key (e.g. `"2026_active_aero"`) appears with its own `ClassVocabulary`
(`version=1`) and, initially, mostly-`"unresolved"`/`"reserved"` cells (few 2026 sessions yet)
— the SAME resolved/unresolved status machinery `driver_utility.py` already has, reused
verbatim, not reinvented. No existing era's rows change. A join against the new era naturally
returns wide, honest `effective_sigma` until data accumulates — a real, visible cold-start cost
(flagged in Complexity costs #5), not a silent gap.

### 7.6 Segment-discriminativeness weighting

Covered in §5.3 — zero schema cost, fit-time-only.

### 7.7 Far-future low-rank factorization

A `FactorizedFingerprintReader` implementing the same `FingerprintReader` Protocol
(`load_fingerprint`/`load_bulk`/`cell_support`) could serve cells synthesized from a low-rank
driver×class factor model instead of the tidy SQLite table — reconstructing a `CellAddress`
query on demand. Every consumer above depends only on the Protocol's method signatures, never
on `DriverFingerprintStore` being SQLite-backed, so this swap is invisible to them. This is
deliberately the ONLY escalation this design does not give a concrete data shape for — the
brief's own framing ("a little cute", deferred far) makes speccing its internals premature; the
design's job here is just to confirm the read contract doesn't block it, which it doesn't.

---

## 8. Invariants (numbered, for citation)

- **I1 — Totality.** Every `(driver, era, class_id)` combination in scope for a fit run emits
  exactly one cell per `(subphase×channel×transition_from×slot)` combination that was actually
  requested — reserved/unresolved, never silently absent. Reused from `driver_utility.py`.
- **I2 — Vocabulary compatibility.** A join or a bulk read across two vocabulary-tagged objects
  (`DriverFingerprint`, `CircuitClassShare`) requires equal `(era, class_vocabulary_version)`.
  Mismatch raises; there is no implicit crosswalk in v1.
- **I3 — Collapse order-independence.** `collapse_cells` is always a single flat
  `pool_random_effects` call over every matching finer cell, never a sequential pairwise
  reduction — so which dimension is "collapsed first" is not a meaningful question.
- **I4 — Direct-row preference.** `load_fingerprint` prefers a cell stored directly at the
  requested grain over one derived by collapse, when both exist — paired with the §6
  regeneration discipline, this is what makes "no consumer breaks when an escalation activates"
  a byte-identical guarantee for anyone not opting in.
- **I5 — Collapse is one-directional.** Fine → coarse only. Requesting a grain finer than
  anything stored raises `CellNotAvailableError`; it never fabricates a decomposition.

## 9. Error modes

`VocabularyMismatchError` (I2), `CellNotAvailableError` (I5), `ValueError` on
`transition_from == class_id` (CellAddress construction), `ShareCoverageError` (defensive, join
input contract violated — should be unreachable given I1).

## 10. Where flexibility costs complexity, and whether it's worth it

1. **Long/tidy schema vs wide columns.** Every read pays a pivot/group cost `driver_utility.py`'s
   wide DataFrame doesn't. Worth it: `estimate_store.py`'s `AXIS_STATUS_NAMES` /
   `*_shared_sigma`-per-axis pattern is the visible cost of the *wide* alternative — every new
   axis there touches a tuple constant, N dataclass fields, and N SQL columns. This design has
   ~7 known escalations coming; tidy avoids that multiplication entirely.
2. **Cells treated as independent in the join.** `join_fingerprint_to_circuit`'s v1 sigma
   formula ignores cross-class covariance (a driver strong in tight corners plausibly correlates
   with fast corners too). Deferred, not free — flagged as a known simplification, not hidden.
3. **Direct-row-preference + regeneration discipline (I4 + §6).** Without the regeneration rule,
   a stale class-level row and freshly-refit subphase children can silently diverge. The
   discipline is a real operational obligation on every fitter run, not just documentation —
   worth it because the alternative (always-collapse-never-store-direct) would break
   byte-identical backward compatibility, which is the brief's explicit ask.
4. **Transition cells need both sides to move.** No payoff until the circuit-share producer
   also escalates — the most expensive-to-realize axis in the list, cheapest to leave dormant.
5. **Era cold-start.** A new era starts mostly "unresolved" by design (I1's honesty, not a bug)
   — real UX cost during a rules transition, worth surfacing to whoever owns the practice-update
   consumer rather than silently degrading its prior.
6. **Open string namespaces (`slot`, `channel`).** No typo-safety. Mitigated with
   `KNOWN_SLOTS`/`KNOWN_CHANNELS` registry constants + warn-not-fail validation, consistent
   with the project's own "tunable weights/thresholds/heuristics belong in named constants"
   convention — cheaper than a closed enum that would need editing for every future escalation.

## 11. Explicitly out of scope for this interface pass

Circuit-side producer internals (Lineage A / `regime_rollup.py`'s distance-share → time-share
correction, per x1's named gap) — this design only specifies the `CircuitClassShare` contract
that producer must satisfy, not how to build it. Cross-era vocabulary crosswalks. The actual
hierarchical Student-t math inside `fit_driver_fingerprint` beyond "reuses `pool_random_effects`
per level." The low-rank factorization's internal representation (§7.7).
