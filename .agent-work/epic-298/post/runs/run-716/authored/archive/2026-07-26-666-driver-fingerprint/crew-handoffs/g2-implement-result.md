# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2-implement` (epic659/666-driver-fingerprint; issue #666, epic #659 Wave 3)

## Completed slice
Built the structural spine of the DriverFingerprint: `address.py` (`CellAddress` +
always-non-NULL `cell_key`), `vocabulary.py` (`ClassVocabulary` carrying the F12 stability
verdict + refuse-on-non-PASS), and `store.py` (`DriverFingerprintStore`, its own DB) — with
k-cells-always-populated (unresolved-not-missing), replace-on-rerun via the non-NULL
`cell_key`, loud refusal on era/vocabulary mismatch, and structurally NO fit-on-read. NO fit
logic (that is G3). All four plan items driven through the checklist engine to completion
(`m0-context` → `m1-address` → `m2-vocabulary` → `m3-store` → `m4-verify-and-close`); plan
file: `.agent-work/666-driver-fingerprint/crew-handoffs/g2-implement-plan.json`.

## Scope
**Files changed (all NEW):**
- `src/physics/fingerprint/address.py`
- `src/physics/fingerprint/vocabulary.py`
- `src/physics/fingerprint/store.py`
- `tests/unit/physics/fingerprint/test_address.py`
- `tests/unit/physics/fingerprint/test_vocabulary.py`
- `tests/unit/physics/fingerprint/test_store.py`

**Specific exclusions touched:** no — `reference_utilization_store.py`, `grip_store.py`,
`segment_map/identity.py`, `regulation_era.py`, and `fingerprint/frozen_constants.py` were
read-only consumed (imports/reference only), never edited. No `driver_class_observables`
read. No fit logic added.

## Behavior changed
Yes (additive only, new package modules) — no existing production code path is touched;
`address.py`/`vocabulary.py`/`store.py` are new, standalone modules.

## Map Impact
- **Structural anchors touched:** NEW `struct:physics.fingerprint address` (`CellAddress`,
  non-NULL `cell_key`), NEW `struct:physics.fingerprint vocabulary` (`ClassVocabulary`,
  `era_key`, `require_fittable`), NEW `struct:physics.fingerprint store`
  (`DriverFingerprintStore`, `driver_fingerprint_cells` table). Consumed (read-only)
  `struct:physics.segment_map identity.VocabularyRef` (minted-once/resolved-by-name
  precedent), `struct:physics.regulation_era RegulationEra.for_season` (era_key's flag
  signature source), and the house pattern from
  `struct:physics.utilization reference_utilization_store`/`struct:physics.layer2 grip_store`.
- **Capability:** per-(driver, rules-era) k-cell fingerprint store now exists — write/read
  round-trips exactly `k` cells for a `(driver, era, vocabulary, channel, what_measure)`
  key, with unresolved cells for absent/thin-support classes.
- **Constraints/assumptions touched:** DB-BLOB guard (#632/#656) honored — own DB, no
  `data/` blob committed, tests use `tmp_path` only. Dormant-slot ruling 4 honored —
  `RESERVED_WHAT_MEASURES` are constructible on `CellAddress` but refused at the store
  write path (`ReservedWhatMeasureError`).
- **Decision anchors resolved:** `decision:fingerprint-era-key` (was graded `guess · leans
  g2-implement · settle: confirm against exactly-k-cells + observables class set`) —
  SETTLED this run as: `era_key(season)` derives a string from `RegulationEra.for_season`'s
  `(drs_enabled, mguk_regen, mguh_present)` flag signature (NOT `str(season)`), so seasons
  sharing a regulation package share one era key (e.g. 2024==2025), matching how
  `VocabularyRef.rules_era` is documented elsewhere in this codebase (a regulatory ERA
  range, not a single season). Regrade to `settled/measured` if a future gate contradicts
  it with real observables-class-set evidence — this run only confirms it against the
  exactly-k-cells invariant, not yet against a real observables class set (that is G3/G4's
  job).
- **Claims/evidence produced:** `claim: loud-refusal` — two distinct structural refusals
  verified (era-vs-vocabulary argument mismatch; vocabulary-version drift on write), plus
  non-PASS-vocabulary refusal and reserved-what_measure refusal — see Evidence below.
  `claim: k-cells-populated` — `write_fingerprint`/`get_fingerprint` round-trip exactly `k`
  rows/cells in every tested case, including an empty store (synthesized unresolved cells,
  never a missing row) — see Evidence below.
- **Trust limitations / drift found:** none discovered in existing code; `ClassVocabulary`
  is net-new (building, not trusting a map node) — its `f12_verdict`/`f12_provenance`
  sourcing from the REAL F12 machinery (vs. this gate's synthetic test fixtures) is G3/G4's
  job to wire, not verified here.
- **Triage candidates:** whether the vocabulary-drift refusal (stale `vocabulary_version`
  rows under the same driver/era/channel/what_measure) should eventually gain an explicit
  migration/purge API (currently it just refuses — a caller who genuinely wants to move a
  driver's fingerprint onto a re-fit vocabulary has no sanctioned path yet, only the
  refusal). Out of scope for G2 (no such caller exists yet); flagged for G3/G4 if a re-fit
  workflow needs it.

## Test mode
**Required:** TDD (test-first), per the handoff's Test Mode section — the invariants
(non-NULL cell_key idempotency, k-cells+unresolved, loud-refusal, replace-on-rerun) are the
acceptance surface.
**Satisfied:** yes — RED→GREEN observed for all three modules (`test_address.py`,
`test_vocabulary.py`, `test_store.py`), each written and run to a `ModuleNotFoundError`
failure before its implementation file existed, then implemented until green.

## Evidence

```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_address.py tests/unit/physics/fingerprint/test_vocabulary.py tests/unit/physics/fingerprint/test_store.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-666
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 65 items

tests\unit\physics\fingerprint\test_address.py ......................... [ 38%]
...                                                                      [ 43%]
tests\unit\physics\fingerprint\test_vocabulary.py ....................   [ 73%]
tests\unit\physics\fingerprint\test_store.py .................           [100%]

============================= 65 passed in 0.49s ==============================
```

```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m src.utils.simplification_limits --paths src/physics/fingerprint/address.py src/physics/fingerprint/vocabulary.py src/physics/fingerprint/store.py
```
```
PASS (3 files checked)
```
(Note: the handoff's pinned command omitted the required `--paths` flag —
`-m src.utils.simplification_limits src/physics/... ...` alone errors
`unrecognized arguments`. Ran the corrected CLI form above; see Workflow Feedback.)

```bash
git status --porcelain
```
```
?? .agent-work/666-driver-fingerprint/
?? scripts/fingerprint_class_coverage_675.py
?? src/physics/fingerprint/
?? tests/unit/physics/fingerprint/
```
Nothing staged; all new paths untracked (`??`). `git check-ignore` on the 6 new committed
files all exit 1 (not ignored — correctly trackable):
`src/physics/fingerprint/{address,vocabulary,store}.py`,
`tests/unit/physics/fingerprint/test_{address,vocabulary,store}.py`.

**Result:** pass — both verification commands and the git-status/check-ignore audit run
foreground, reproducibly (re-run immediately before writing this result, same output).

## TDD evidence, if required
- **address.py:** RED — `ModuleNotFoundError: No module named 'src.physics.fingerprint.address'`.
  GREEN — `28 passed` after implementing `CellAddress`.
- **vocabulary.py:** RED — `ModuleNotFoundError: No module named 'src.physics.fingerprint.vocabulary'`.
  GREEN — `20 passed` after implementing `ClassVocabulary`/`era_key`/`require_fittable`.
- **store.py:** RED — `ModuleNotFoundError: No module named 'src.physics.fingerprint.store'`.
  GREEN — `17 passed` after implementing `DriverFingerprintStore` (one intermediate
  refactor: the first draft of the no-fit-on-read test did a raw substring search over the
  WHOLE file, which false-positived on the module's own protective docstring naming
  `driver_class_observables` as a forbidden dependency — not present in any import — so I
  rewrote that one test to `ast`-parse only the import statements, which is also the more
  correct scoping of "no import of the fit module in the read path").
- Refactor while green: yes, the one test-mechanism fix above; no production-code refactor
  was needed after green.

## Docs/contracts touched
- none — no doc file edited; this gate is code + test only.

## Assumptions
- **`cell_key` delimiter:** `"|"` (pipe), validated absent from every one of the six
  identity fields in `CellAddress.__post_init__` — chosen because none of driver code, era
  key, vocabulary id, class id, channel, or what_measure is expected to ever contain it, and
  the validation makes a collision structurally impossible rather than merely unlikely.
- **`era_key` derivation:** a string built from `RegulationEra.for_season(season)`'s
  `(drs_enabled, mguk_regen, mguh_present)` flag signature (e.g. `"drs1-mguk1-mguh1"` for
  2014-2025), NOT `str(season)`. Chosen over the literal-season alternative because it keys
  off the existing `RegulationEra` seam (per Allowed Scope: "do NOT invent a new taxonomy")
  and because it matches `VocabularyRef.rules_era`'s own documented convention elsewhere in
  this codebase (a regulatory ERA range like `"2022-2025"`, not a single season) — two
  seasons under the same regulation package legitimately share one fingerprint era. This
  resolves `decision:fingerprint-era-key` (previously graded `guess`) to `settled/measured`
  against the exactly-k-cells invariant; it has not yet been checked against a real
  observables class set (G3/G4's job).
- **Loud-refusal design for "era/vocab mismatch"** (the handoff named the invariant but left
  the exact trigger to my judgment, per Authority): implemented as TWO checks under one
  `EraVocabularyMismatchError`: (1) an argument-level check — `era` must equal
  `vocabulary.rules_era` on every read and write, since both arguments assert an era and
  disagreement is unresolvable without picking one silently; (2) a write-time
  vocabulary-drift check — refuses if the store already has cells for this
  `(driver, era, channel, what_measure)` under a DIFFERENT `vocabulary_version` than the one
  being written, so a re-fit taxonomy can never silently accumulate alongside a stale one
  under the same logical fingerprint slot.
- **`require_fittable(override=...)` naming:** the handoff's example name was
  `allow_unverified=True`, but the test-mode line explicitly requires "override bypasses"
  with no UNVERIFIED-only restriction, so I named the parameter `override` (bypasses BOTH
  `FAIL` and `UNVERIFIED`) rather than `allow_unverified` (which would misleadingly imply
  FAIL is still blocked). `DriverFingerprintStore.write_fingerprint` exposes this through as
  its own `allow_unverified: bool = False` kwarg (closer to the handoff's own wording at the
  store's public boundary), passed straight through as `vocabulary.require_fittable(override=allow_unverified)`.
- **Resolved/unresolved boundary:** a class's `support_n` must be `>=` (not `>`)
  `FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR` (1.0) to count as resolved, consumed read-only from
  `frozen_constants.FINGERPRINT_FROZEN` exactly as the Allowed Scope specifies.

## Stop conditions hit
- None. Every invariant was made structural within this gate's authority; the house store
  pattern (`reference_utilization_store.py`/`grip_store.py`) fit cleanly; no reserved slot's
  semantics were unclear beyond the one naming choice documented above (which the handoff's
  own Authority section explicitly delegated); no existing module needed editing; the
  observables DB was never read.

## Out-of-scope observations
- **Handoff's `simplification_limits` verification command needs `--paths`.** The pinned
  command `python.exe -m src.utils.simplification_limits src/physics/fingerprint/address.py
  ...` (positional file args, no flag) errors `unrecognized arguments` against the actual
  CLI (`src/utils/simplification_limits.py`'s `argparse` only accepts file/dir paths under
  `--paths`). Ran the corrected form (`--paths <files>`) instead; flagged here rather than
  silently fixed in the handoff (out of my edit scope), and reported below as a template
  fix for future gates.
- **Vocabulary-drift refusal has no migration path yet** (see Map Impact / Triage
  candidates above) — a caller wanting to move a driver's stored fingerprint onto a
  re-fit `ClassVocabulary` has no sanctioned "replace the old vocabulary's rows" API, only
  the refusal. Not needed by anything in G2's scope; worth a note for whichever gate first
  needs a real vocabulary re-fit against already-populated cells.

## Workflow Feedback
- **Handoff gaps:** the `simplification_limits` verification command (see Out-of-scope
  observations) was missing the `--paths` flag the real CLI requires — a small but exact
  wording gap worth fixing in future handoffs/templates that reuse this command form.
- **Context rediscovered:** none beyond the ordinary read of the three named reference
  seams (`reference_utilization_store.py`, `grip_store.py`, `segment_map/identity.py`,
  `regulation_era.py`) the handoff already pointed at directly.
- **Instructions improvised around:** the `require_fittable` override naming (see
  Assumptions above) — the handoff offered two candidate names
  (`allow_unverified=True`/`override`) for one behavior, and the test-mode line's "override
  bypasses" (unqualified) settled which of the two the implementation should actually be
  named and how broadly it should bypass; I picked `override` at the `ClassVocabulary`
  boundary and `allow_unverified` at the store's public boundary (closer to the handoff's
  own wording where a caller actually reads it), documented in both docstrings.
- **What would have made this easier:** fixing the `simplification_limits` command snippet
  in the handoff template to include `--paths` would save the next implementer the same
  five-second stumble.

## Return status
`complete`
