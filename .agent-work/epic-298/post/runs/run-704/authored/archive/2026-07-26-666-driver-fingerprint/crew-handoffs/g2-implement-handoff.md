# Implementer Handoff — G2 (address space + ClassVocabulary + versioned cell store)

## Gate
g2-implement (issue #666, epic #659)

## Task
Build the structural spine of the DriverFingerprint: the versioned address space (`CellAddress` + a canonical
always-non-NULL `cell_key`), the `ClassVocabulary` value object (carrying the F12 stability verdict, refusing a
failed-gate vocabulary), and the versioned cell store in its OWN db — with the k-cells-always-populated,
loud-refusal, replace-on-rerun, and NO-fit-on-read invariants. NO fit logic here (that is G3).

## Protected Intent
This store is a keystone state store: every downstream fingerprint consumer trusts its invariants. A NULL PK
component silently breaking idempotency, a missing cell instead of an `unresolved` row, a silent era/vocab
substitution, or a fit-on-read path are all silent-miscalibration hazards. Make the invariants STRUCTURAL.

## Test Mode
TDD required — the invariants (non-NULL cell_key idempotency, k-cells+unresolved, loud-refusal, replace-on-rerun)
are exactly the acceptance surface; write the tests first, using TEMP/scratch DBs only (#656).

## Close Criteria (each proven by a test)
- `src/physics/fingerprint/address.py` — `CellAddress` (frozen dataclass) with fields:
  `driver: str, era: str, vocabulary_version: str, class_id: str, channel: str, what_measure: str`.
  A property/field `cell_key: str` = a delimited join of ALL SIX fields (choose a delimiter that cannot appear
  in the values, e.g. `|`), VALIDATED in `__post_init__` to be always non-NULL / non-empty for every component
  (raise a loud ValueError naming the offending field if any is None/empty). This is the SQLite-NULL-PK fix.
  - `channel`: Build-1 active values are `"utilization"` and `"energy"` (both are fit — see G3). Provide a module
    constant listing them; the dim is present-from-day-one (structural). A `FingerprintChannel` set/enum is fine.
  - `what_measure`: Build-1 default = `"deficit"`. Provide RESERVED-present-but-unused slot constants
    `RESERVED_WHAT_MEASURES = ("push","managed","consistency","management_efficiency")` (Build-2 race-side,
    documented as reserved). A `CellAddress` whose `what_measure` is a reserved slot is CONSTRUCTIBLE (the slot is
    present) but the STORE/FIT path refuses to populate it in Build 1 (loud refusal) — the dormant-dimension
    requirement (ruling 4).
- `src/physics/fingerprint/vocabulary.py` — `ClassVocabulary` (frozen dataclass) with fields:
  `vocabulary_id: str, rules_era: str, k: int, class_ids: tuple[str,...], f12_verdict: str, f12_provenance: str`.
  - `f12_verdict` ∈ {`"PASS"`,`"FAIL"`,`"UNVERIFIED"`}; validate `len(class_ids)==k` and uniqueness.
  - A method/helper that the fit path calls: `require_fittable()` (or similar) that RAISES loudly unless
    `f12_verdict=="PASS"`, UNLESS an explicit `allow_unverified=True`/override is passed. Default = refuse.
  - Era key derived from `RegulationEra.for_season(season)` — provide a small helper
    `era_key(season:int)->str` (e.g. a canonical string from the RegulationEra flag signature or `str(season)` —
    your choice; document it). Do NOT invent a new taxonomy; key off the existing seam.
- `src/physics/fingerprint/store.py` — `DriverFingerprintStore` in its OWN db (house pattern, copy from
  `src/physics/utilization/reference_utilization_store.py` / `grip_store.py`):
  - `__init__(self, db_path: str, *, must_exist: bool=False)`, create-on-construct, `_connect`,
    `_init_schema` with `_migrate_missing_columns` (additive ALTER-ADD, never drop/rename), `format_version` stamp.
  - Table `driver_fingerprint_cells`, PK = **`cell_key` declared `NOT NULL`** (belt-and-suspenders with the
    CellAddress validation). Columns: cell_key(PK), driver, era, vocabulary_version, class_id, channel,
    what_measure, mean, sigma, support_n, status, shared_floor_applied, format_version. Persist via
    `INSERT OR REPLACE` (replace-on-rerun).
  - `status` ∈ {`"resolved"`,`"unresolved"`}. A write API that, GIVEN a (driver, era, vocabulary, channel,
    what_measure), writes EXACTLY k rows (one per `class_id` in the vocabulary) — a class with no/thin support
    gets a `status="unresolved"` row (NULL mean/sigma ok), NEVER a missing row. A read API
    `get_fingerprint(driver, era, vocabulary, channel, what_measure) -> list[cell]` returns EXACTLY k cells.
  - **LOUD refusal** (raise, no silent substitution): reading/writing with an `era` or `vocabulary_version` that
    mismatches what a stored fingerprint carries; and writing a fingerprint whose `ClassVocabulary.f12_verdict`
    is not `"PASS"` (unless override).
  - **NO fit-on-read** — the store NEVER computes/fits on a read; it only persists and returns stored rows. Make
    this structural (no import of the fit module in the read path; a read never triggers a compute).
- Tests `tests/unit/physics/fingerprint/{test_address.py,test_vocabulary.py,test_store.py}` (temp DBs):
  - address: cell_key always non-NULL; a None/empty component raises loudly; cell_key round-trips.
  - vocabulary: `require_fittable()` raises on FAIL/UNVERIFIED, passes on PASS, override bypasses; k/class_ids
    validation.
  - store: k-cells-always-populated + unresolved-not-missing; non-NULL cell_key `INSERT OR REPLACE` idempotency
    (writing the same fingerprint twice yields k rows, not 2k); replace-on-rerun updates in place; loud refusal on
    era/vocab mismatch AND on a non-PASS vocabulary; NO-fit-on-read (a read on an empty store returns unresolved
    cells or refuses, never fits).

## Allowed Scope
CREATE the three `src/physics/fingerprint/*.py` + the three test files. READ-ONLY:
`src/physics/utilization/reference_utilization_store.py`, `src/physics/layer2/grip_store.py`,
`src/physics/segment_map/identity.py` (VocabularyRef), `src/physics/regulation_era.py`,
`src/physics/fingerprint/frozen_constants.py` (consume `FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR` for the thin/unresolved boundary).

## Specific Exclusions
NO fit logic (G3). NO reading `driver_class_observables` here (that is the G3 fit's job). Do NOT edit any
existing module. Do NOT populate a reserved what_measure slot. Do NOT commit any data/.agent-work blob.

## Constraints
- Interpreter PIN + `PYTHONPATH=.` from worktree root; `from src...` imports.
- OWN db (#632) — never the f1_data DBs or #664's observables db. Tests use temp DBs (#656).
- Non-NULL cell_key is STRUCTURAL (CellAddress validation + `NOT NULL` PK).
- Dormant channel/what_measure slots present-but-unused (ruling 4).

## Map Anchors (inbound)
- **Structural:** NEW `struct:physics.fingerprint` address/vocabulary/store; `struct:physics.segment_map`
  VocabularyRef/`RegulationEra.for_season`; house pattern from `reference_utilization_store`/`grip_store`.
- **Capability:** per-(driver,rules-era) k-cell fingerprint store.
- **Constraints/assumptions:** DB-BLOB guard (#632/#656); lowest dimensionality (dormant slots present-unused).
- **Decision anchors:** `decision:fingerprint-era-key` — era from RegulationEra.for_season; k=4 severity cells.
  `@grade: guess · leans g2-implement · settle: confirm against exactly-k-cells + observables class set`
  Design-it-twice CALLER/FLEX/MINIMAL hybrid SETTLED. `@grade: settled/inherited`
- **Evidence expectations:** `claim: loud-refusal`, `claim: k-cells-populated`.
- **Map confidence flags:** ClassVocabulary net-new — building, not trusting a map node.

## Deliverable Path Check
- Committed: the 3 `src/physics/fingerprint/*.py` + 3 `tests/unit/physics/fingerprint/test_*.py`
  (each `git check-ignore` exits 1). New files — appear in `git status`, not `git diff` until staged.
- Local-only: temp test DBs (created under a pytest tmp_path, never committed).

## Required Evidence
- LOAD-BEARING: the full `tests/unit/physics/fingerprint/` run (test_address + test_vocabulary + test_store) green;
  the specific idempotency + k-cells + loud-refusal + no-fit-on-read assertions.
- Confirmatory: `git status --porcelain` (nothing under data/ or .agent-work/ staged); `py -m src.utils.simplification_limits` clean on the new files.

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_address.py tests/unit/physics/fingerprint/test_vocabulary.py tests/unit/physics/fingerprint/test_store.py -q
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m src.utils.simplification_limits src/physics/fingerprint/address.py src/physics/fingerprint/vocabulary.py src/physics/fingerprint/store.py
```

## Suggested Model Tier
Stronger — a keystone store with several structural invariants; correctness over speed.

## Authority
Schema shape above is commander-decided. You MAY choose the exact `era_key` derivation + cell_key delimiter +
internal helper names — document them. You must NOT drop any invariant or add fit logic.

## Stop Conditions
Stop and return if: an invariant cannot be made structural; the house store pattern doesn't fit; a reserved
slot's semantics are unclear; you'd need to edit an existing module or read the observables DB.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test-mode satisfied, evidence (paste the full
fingerprint test run + simplification_limits output), assumptions (era_key derivation, delimiter), stop
conditions, out-of-scope observations, workflow feedback. Write it to
`.agent-work/666-driver-fingerprint/crew-handoffs/g2-implement-result.md` AND SendMessage a concise summary to
`cmdr-666` before ending your turn.
