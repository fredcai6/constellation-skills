# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g5 (issue #662)` — Assembly + persistence + derivation entrypoint: compose G1-G4 into `derive_segment_map`, build + persist the `SegmentMap`, plus a thin batch CLI.

## Completed slice
Full G5 scope delivered in three new files: `derive.py` (pure `assemble_segment_map` composer + data-plumbing `derive_segment_map` sourcer + `write_segment_map` cold-path persister), `scripts/derive_segment_maps.py` (thin per-season batch CLI), `test_derive.py` (7 tests, all real — no stubs).

## Scope
**Files changed:**
- `src/physics/segment_map/derivation/derive.py` (new)
- `scripts/derive_segment_maps.py` (new)
- `tests/unit/physics/segment_map/derivation/test_derive.py` (new)

**Specific exclusions touched:** no — did not compute gating checks/verdict (g6), did not populate sub-phase marks, did not persist adjacency, did not edit `docs/architecture/*` or any existing `segment_map` runtime/store/identity file or `frozen_constants.py`, did not use the seeded/supersede write path (`prior_map` always `None`).

## Behavior changed
Yes — new capability. `derive_segment_map(year, gp_name, session_type="Q", ...)` is the first end-to-end entry point that turns a weekend's raw telemetry+DB data into a persisted `SegmentMap`. `assemble_segment_map` is the pure (I/O-free) composer, factored out so the round-trip/hash/invariant tests need no store/session dependency. `scripts/derive_segment_maps.py` batches a season.

## Map Impact
- **Structural anchors touched:** `src/physics/segment_map/derivation/derive.py` (NEW — `weekend_key`, `assemble_segment_map`, `derive_segment_map`, `write_segment_map`); `scripts/derive_segment_maps.py` (NEW CLI). Calls (read-only) `runtime.SegmentMap.build`, `store.SegmentMapStore.write`, `identity.{MapVersion, VocabularyRef, layout_content_hash, config_fingerprint}`, and all of G1-G4's public entry points.
- **Capabilities added:** end-to-end per-weekend SegmentMap derivation + COLD persistence; a batch CLI for a season.
- **Constraints/assumptions touched:** `decision:derivation-subpackage-placement` (honored: `derive.py` lives beside G1-G4 in `derivation/`); `decision:dormant-subphase` (honored: no sub-phase store touched, adjacency never persisted — `SegmentMap.next_ordinal`/`prev_ordinal`'s mod-arithmetic is untouched and is the only adjacency mechanism). New constraint surfaced: `constraint:map-version-must-be-weekend-qualified` — the store's `segment_maps` table primary-keys on `map_version` ALONE across every weekend (not composite with gp_name/year/weekend); a bare literal `"v1"` would collide across weekends via `INSERT OR REPLACE`. See "layout_id/weekend-key choices" below.
- **Claims/evidence produced:** `claim:geometry-only-hash` — proven by `TestGeometryOnlyHash` (two tests, see Evidence). `claim:store-round-trip` — proven by `TestStoreRoundTrip` (two tests, see Evidence).
- **Trust limitations / drift found:** the handoff states `data/segment_maps.db` is gitignored; it is **not** — `.gitignore` has no `/data/segment_maps.db` (or generic `/data/*.db`) entry, only specific named `.db` files (e.g. `/data/damage_integrals.db`). I did not edit `.gitignore` (out of Allowed Scope) and avoided the issue by running my own CLI smoke test against a scratchpad path outside the repo, so nothing landed in `git status`. Flagged as a triage candidate below.
- **Triage candidates:** add `/data/segment_maps.db` to `.gitignore` (matching the existing named-`.db`-file precedent) before anyone runs `scripts/derive_segment_maps.py` against the default path in a tracked checkout.

## Test mode
**Required:** `TDD-lean (round-trip + hash tests first against synthetic fixtures, real-weekend smoke guarded)`
**Satisfied:** yes — RED observed for all 6 tests needing `derive.py` (1 of 7 passed immediately: the literal boundary-stripping test only needs G3's already-implemented `nest_sectors`), then GREEN on first implementation attempt (no fixup iteration needed for the synthetic tests).

## Evidence

### RED (before derive.py existed)
```
$ pytest tests/unit/physics/segment_map/derivation/test_derive.py -q
collected 7 items
tests\unit\physics\segment_map\derivation\test_derive.py F.FFFFF         [100%]
6 failed (ModuleNotFoundError: No module named 'src.physics.segment_map.derivation.derive'), 1 passed in 0.52s
```

### GREEN — synthetic-fixture tests only (excludes real-weekend smoke)
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_derive.py -k "not RealWeekend" -q
```
```
collected 7 items / 1 deselected / 6 selected
......                                                                   [100%]
6 passed, 1 deselected in 0.55s
```

### Full suite — including the real-2023-Bahrain-weekend smoke (LOAD-BEARING evidence, genuinely ran, not skipped)
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_derive.py -v
```
```
tests/unit/physics/segment_map/derivation/test_derive.py::TestGeometryOnlyHash::test_same_geometry_different_sector_draws_same_layout_id PASSED [ 14%]
tests/unit/physics/segment_map/derivation/test_derive.py::TestGeometryOnlyHash::test_sector_forced_splits_are_the_only_difference_from_base PASSED [ 28%]
tests/unit/physics/segment_map/derivation/test_derive.py::TestStoreRoundTrip::test_build_write_get_by_version_reproduces_map PASSED [ 42%]
tests/unit/physics/segment_map/derivation/test_derive.py::TestStoreRoundTrip::test_get_current_resolves_to_the_same_version PASSED [ 57%]
tests/unit/physics/segment_map/derivation/test_derive.py::TestBuildInvariants::test_noncorner_membership_zero_corner_radius_positive_boundaries_monotone PASSED [ 71%]
tests/unit/physics/segment_map/derivation/test_derive.py::TestIdentityFields::test_identity_fields_match_contract PASSED [ 85%]
tests/unit/physics/segment_map/derivation/test_derive.py::TestRealWeekendSmoke::test_derive_and_persist_2023_bahrain_q PASSED [100%]
7 passed in 5.15s
```

**The two LOAD-BEARING tests, what they prove:**
- `test_same_geometry_different_sector_draws_same_layout_id` — builds ONE synthetic `ReferenceLap` + G2 base tiling (`[0, 545, 695, 795, 1000]`, straight/braking/corner/straight), then calls `assemble_segment_map` TWICE with the SAME base geometry but two DIFFERENT sector-line draws (`[200, 900]` vs `[100, 950]`). Asserts the two persisted maps' `boundaries_m` genuinely differ (proving the sector draws did something), yet `layout_id` is IDENTICAL, and equals `layout_content_hash(base_tiling.boundaries_m)` directly.
- `test_sector_forced_splits_are_the_only_difference_from_base` — literal proof of `identity.py`'s own docstring wording: strips the 2 sector-line distances out of the FINAL nested boundaries and asserts the remainder equals the G2 base tiling's boundaries exactly.
- `test_build_write_get_by_version_reproduces_map` / `test_get_current_resolves_to_the_same_version` — `assemble_segment_map` → `write_segment_map` → `store.get_by_version`/`get_current` reproduce `boundaries_m`, `seg_type_code`, `sector`, `turn_direction`, `corner_descriptor` byte-identical (`np.testing.assert_array_equal`), `severity_membership` numerically identical, and `class_ids` preserved.

### simplification_limits (verification command #2 from the handoff)
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/derive.py scripts/derive_segment_maps.py
```
```
PASS (2 files checked)
```

### CLI manual smoke (not part of the pytest suite — a live run against a scratchpad DB, never the repo's `data/`)
```
$ python scripts/derive_segment_maps.py --year 2023 --gp-name Bahrain Monaco --db-path <scratchpad>/segment_maps_smoke.db
fitted era severity mixture: vocabulary_id=severity:2023:v1 k=4 (reused for every weekend below)
wrote 2023 Bahrain Q -> map_version=2023-Bahrain-Q:v1 n_segments=36 n_corner=13
wrote 2023 Monaco Q -> map_version=2023-Monaco-Q:v1 n_segments=43 n_corner=19
done: 2/2 weekend(s) written
```
Idempotency check: re-ran `--gp-name Bahrain` alone against the SAME db; row count stayed at exactly 2 total afterward (Bahrain's row replaced in place via `INSERT OR REPLACE` on its weekend-qualified `map_version`; Monaco's untouched).

### Deliverable path check (git check-ignore exits 1 -- not ignored; all three new/untracked)
```bash
$ git check-ignore -v src/physics/segment_map/derivation/derive.py scripts/derive_segment_maps.py tests/unit/physics/segment_map/derivation/test_derive.py
(no output; exit code 1)

$ git status --short
 M data/f1_data_2023.db          # pre-existing, unrelated to this gate
?? scripts/derive_segment_maps.py
?? src/physics/segment_map/derivation/derive.py
?? tests/unit/physics/segment_map/derivation/test_derive.py
```
`data/segment_maps.db` (the segment-map store's default output path) does NOT appear here because the manual CLI smoke run above was deliberately pointed at a scratchpad path, not the repo's `data/`. See "Trust limitations" above: this path is **not actually gitignored** in this repo's `.gitignore` (flagged as a triage candidate), so running the CLI against its own default inside a tracked checkout would leave an untracked `data/segment_maps.db`.

**Result:** pass — all required evidence commands green.

## TDD evidence, if required

- Failing test observed: full `test_derive.py` run before `derive.py` existed — 6 failed with `ModuleNotFoundError: No module named 'src.physics.segment_map.derivation.derive'`, 1 passed (the pure G3-only strip test).
- Passing test observed: 6/6 synthetic-fixture tests green on the FIRST implementation attempt (see Evidence); full 7/7 including the real-weekend smoke.
- Refactor while green: no separate refactor pass needed — `derive.py` went green as written.

## Docs/contracts touched
- none (module docstrings only, per Allowed Scope — no `docs/architecture/*` edits, per Specific Exclusions).

## layout_id / weekend-key choices

- **`layout_id`** = the geometry-only `layout_content_hash` value directly (sha256 hex over the G2 BASE tiling's `boundaries_m`, computed BEFORE `nest_sectors` ever runs). This is one of the two options the handoff explicitly offered ("use the geometry-only layout_content_hash as the layout_id, or a documented gp-derived id"); chosen because it requires no separate track-layout registry and is deterministic from data already in hand.
- **The subtle implementation choice for the hash strip:** rather than computing the FINAL (nested) boundaries and then subtracting the 2 known sector-line distances from that list, `_layout_geometry_hash` is fed the G2 base tiling's `boundaries_m` DIRECTLY, captured before `nest_sectors` is ever called. This is provably equivalent for the common case (no sliver-merge interaction near a sector cut) and is STRICTLY SAFER in general: `nest_sectors`'s sliver-merge can, in principle, absorb a genuine (non-sector) geometry boundary into a neighbor if it becomes too short after a sector split — subtracting only the 2 known sector distances from the final list would then NOT reproduce the base boundaries exactly, silently corrupting the "geometry-only" invariant. Computing the hash from the base tiling directly sidesteps this edge case entirely by construction. `test_sector_forced_splits_are_the_only_difference_from_base` additionally proves the literal "subtract 2 distances" reading holds in the non-merge-interaction case, satisfying the handoff's exact wording too.
- **`weekend` key** = `weekend_key(year, gp_name, session_type) = f"{year}-{gp_name}-{session_type}"` (e.g. `"2023-Bahrain-Q"`) — human-readable, used both as `MapVersion.weekend` (the `segment_map_current` lookup key alongside `gp_name`/`year`) and as the prefix of the persisted `map_version` string.
- **`map_version`** = `f"{weekend_key}:v1"` (e.g. `"2023-Bahrain-Q:v1"`), NOT the bare literal `"v1"` the handoff's Close Criterion 4 text names. Reason (flagged, not a silent deviation): `store.py`'s `segment_maps` table primary-keys on `map_version` ALONE across EVERY weekend (not composite with gp_name/year/weekend) — `test_store.py`'s own fixtures already establish the real convention with qualified strings like `"map:testonia:v2"`, `"map:t:2023"`. A literal bare `"v1"` for every weekend would collide via `INSERT OR REPLACE` the moment a second weekend was written (proven live: the CLI smoke run above writes `"2023-Bahrain-Q:v1"` and `"2023-Monaco-Q:v1"` as two DISTINCT rows). The trailing `":v1"` still honors the spirit of the literal instruction (Build-1's monotonic version label), while the weekend-qualified prefix satisfies the store's actual schema contract. This is exactly the kind of tension the Authority section's "you MAY decide ... the weekend key ... state them" latitude covers.

## Real 2023-weekend derive result (store present — genuinely ran, not skipped)
Bahrain 2023 Q (via the guarded smoke test + the manual CLI run, both real):
- `n_segments` = 36 (base G2 tiling: 35 segments; +1 net after 2 FIA sector-line cuts and sliver-merge)
- sector counts: S1=12, S2=18, S3=6 segments
- corner count = 13
- `lap_length_m` ≈ 5314.51 m
- sector lines derived: [1748.90 m, 3920.09 m]
- `mixture.k` = 4, `vocabulary_id` = `severity:2023:v1`

Monaco 2023 Q (manual CLI run only, not asserted in the pytest suite): `n_segments`=43, `n_corner`=19.

## Assumptions
- `mixture`/`vocabulary` are optional params on `derive_segment_map`: passing neither fits fresh via `fit_era_severity_mixture(year=year)`; passing only one raises `ValueError`. The CLI always fits ONCE per batch and passes both explicitly, per G4's own stability contract (`vocabulary_version` must stay constant across every weekend of an era).
- `derive_segment_map`'s `store`/`cache`/`offline` params are shared between the G1 reference-lap load and the G3 sector-line derivation (same weekend's telemetry session) — a single `telemetry_store` param threads to both, rather than two independent overrides, since both G1 and G3 need the SAME session for the SAME weekend.
- `build_config` (the `config_fingerprint` input) captures the assembly-relevant knobs (`ref_n_grid`, `ref_smooth_window`, `ref_min_laps`, `sector_min_laps`, `grip_db_path`, `vocabulary_id`, `version_label`) — an audit-replay fingerprint of the DERIVATION parameters, not a copy of the output arrays.
- `built_at` uses `datetime.now(timezone.utc).isoformat()` when not explicitly supplied (tests pass nothing and assert the result round-trips through `datetime.fromisoformat` with `tzinfo` set).
- The CLI treats `SectorLineUnavailableError`, `ValueError`, `LookupError`, and `FileNotFoundError` from `derive_segment_map` as per-weekend-skippable (logged, batch continues); any other exception type would still propagate and halt the batch (not observed in testing — every real failure mode encountered maps to one of these four).

## Stop conditions hit
- none. The compose needed no edits to any G1-G4 module or runtime/store/identity file; the round-trip reproduced the map exactly; the geometry-only hash was made sector-independent by construction (computed before `nest_sectors` runs at all, not merely by post-hoc stripping).

## Out-of-scope observations
- `data/segment_maps.db` is NOT actually covered by `.gitignore` in this repo (see "Trust limitations" above) — a real batch run against the default path in a tracked checkout would leave an untracked file. Triage candidate: add `/data/segment_maps.db` to `.gitignore`.
- g6 (gating checks / verdict) is explicitly out of scope here and untouched, per the handoff's Specific Exclusions.

## Workflow Feedback
- **Handoff gaps:** the Close Criterion 4 wording `map_version="v1"` reads as a literal value, but the store's real schema (global `map_version` primary key across all weekends) and its own test-suite precedent (`"map:testonia:v2"`-style qualified strings) require a weekend-qualified string instead — a literal `"v1"` would silently corrupt the store the moment a second weekend was written. This tension is resolved (see "layout_id/weekend-key choices" above) but a one-line handoff note pointing at `test_store.py`'s own `map_version` convention would have made the "trivially v1" wording's actual scope (the trailing version tag, not the whole string) unambiguous from the start.
- **Context rediscovered:** confirming that `reference_lap_from_store`'s/`fit_era_severity_mixture`'s own `None` defaults ALREADY resolve to absolute main-checkout paths (`src.data.telemetry_store.DEFAULT_STORE_PATH` = `"C:/Programs/f1Brainz/data/telemetry_store.db"`; G4's `DEFAULT_GRIP_BIN_DB_PATH` likewise) took a manual dry-run to discover — the worktree's own `data/telemetry` FastF1-cache directory is EMPTY (0 bytes), so the store path is the only real source. Once confirmed, `derive_segment_map`'s defaults could stay a thin pass-through with no NEW hardcoded absolute path of its own. A one-line pointer in the handoff ("G1/G4's None defaults already resolve to the main-checkout absolute paths; you don't need a new constant") would have saved the dry-run.
- **Instructions improvised around:** none — the handoff's own worked example ("feed the base-tiling geometry boundaries, i.e. the FINAL boundaries with the derived sector-line distances removed") described a test-fixture methodology; I implemented the STRONGER, sliver-merge-safe version (hash the base tiling directly, before nesting) and additionally wrote a literal strip-and-compare test to cover the handoff's exact wording too — reported as a design choice above, not a deviation.
- **What would have made this easier:** a one-line handoff note on the `map_version` global-primary-key subtlety (see Handoff gaps) and the G1/G4 default-path resolution (see Context rediscovered) would have removed the two genuine discovery detours in this run.

## Return status
`complete`
