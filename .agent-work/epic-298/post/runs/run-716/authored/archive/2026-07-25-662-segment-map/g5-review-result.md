# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g5 (issue #662)` — Assembly + persistence + derivation entrypoint

## Result
`APPROVE`

## Handoff compliance
All 6 handoff steps implemented and reproduced: `reference_lap_from_store` (G1) → `tile_reference_lap`
(G2, base tiling) → `derive_sector_lines` + `nest_sectors` (G3) → `derive_corner_attributes` (G4) →
`SegmentMap.build` → `write_segment_map` (cold path, `prior_map=None`). `derive_segment_map` returns
`(SegmentMap, VocabularyRef, MapVersion)` as specified. CLI batches a season's quali weekends via
`get_calendar`, skips unavailable weekends with a logged reason, never crashes the batch — reproduced
live (see Evidence). Independently re-ran both handoff verification commands:

```
pytest tests/unit/physics/segment_map/derivation/test_derive.py -v
7 passed in 5.10s   (incl. TestRealWeekendSmoke — genuinely executed, not skipped)

python -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/derive.py scripts/derive_segment_maps.py
PASS (2 files checked)
```

## Scope drift
None. `git status --short` shows only the 3 allowed new files
(`src/physics/segment_map/derivation/derive.py`, `scripts/derive_segment_maps.py`,
`tests/unit/physics/segment_map/derivation/test_derive.py`) plus `.agent-work/` workflow artifacts.
`git status --short docs/architecture/ src/physics/segment_map/runtime.py src/physics/segment_map/store.py
src/physics/segment_map/identity.py src/physics/layer2/frozen_constants.py` produced **no output** —
zero edits to any excluded file. `data/f1_data_2023.db` shows as git-modified but this is a pre-existing,
already-documented artifact from G1/G3's `DatabaseManager` read path (flagged and accepted at the g3
gate; not introduced or worsened by g5). `write_segment_map` always calls `store.write(..., prior_map=None)`
— no parameter anywhere in the new public surface exposes `prior_map`, so cold-path-only is structurally
enforced, not merely a default. No sub-phase or adjacency code added (grep-confirmed; `next_ordinal`/
`prev_ordinal` mod-arithmetic in `runtime.py` is untouched).

## Evidence verdict
Required evidence present and independently reproduced, not merely trusted:

- **Both verification commands re-run** with the pinned interpreter (see above) — both green, matching
  the implementer's report exactly.
- **Load-bearing hash test read + reproduced**: `test_same_geometry_different_sector_draws_same_layout_id`
  builds one synthetic base tiling, calls `assemble_segment_map` twice with two different sector-line
  draws (`[200,900]` vs `[100,950]`), asserts the two persisted `boundaries_m` genuinely differ (proving
  the sector draw did something) yet `layout_id` is identical and equals
  `layout_content_hash(base_tiling.boundaries_m)` directly. `_layout_geometry_hash` in `derive.py` is fed
  `base_tiling.boundaries_m` — the G2 base tiling captured **before** `nest_sectors` ever runs — so the
  sector-forced splits structurally cannot reach the hash input. This is stronger than the handoff's
  literal "strip 2 distances from the final boundaries" wording (immune to a sliver-merge edge case); a
  second test (`test_sector_forced_splits_are_the_only_difference_from_base`) additionally proves the
  literal reading holds too, in the non-merge-interaction case.
- **Store round-trip read + reproduced**: `test_build_write_get_by_version_reproduces_map` /
  `test_get_current_resolves_to_the_same_version` build → write (cold, `status="historical"`) →
  `get_by_version`/`get_current`, asserting `boundaries_m`/`seg_type_code`/`sector`/`turn_direction`/
  `corner_descriptor` byte-identical (`np.testing.assert_array_equal`), `severity_membership` numerically
  identical, `class_ids` preserved. Read `store.py`'s `_write_cold`/`_load_map`/`_materialize_membership`
  to confirm the round-trip is real (labeled→positional conversion keyed on the stored vocabulary's
  `class_ids`, not a live mixture's order) — matches.
- **Independently reproduced the real-weekend CLI path** (not just re-read the report): ran
  `scripts/derive_segment_maps.py --year 2023 --gp-name Bahrain --db-path <scratch>` myself — output
  `wrote 2023 Bahrain Q -> map_version=2023-Bahrain-Q:v1 n_segments=36 n_corner=13`, exactly matching the
  claimed evidence. Re-ran it a second time against the same DB: `segment_maps` row count stayed at
  exactly 1 (`INSERT OR REPLACE` on the weekend-qualified `map_version`) — idempotency confirmed live, not
  just asserted.
- **Build invariants**: `SegmentMap.build`'s own `__post_init__` → `_validate()` mechanically enforces
  non-corner membership == 0.0, corner `radius_m` > 0, and monotone boundaries on every construction — so
  assembly cannot silently corrupt these without raising `ValueError`. `TestBuildInvariants` is a
  confirming test on top of an invariant that is already structurally impossible to violate silently.
- **Identity fields**: `vocabulary_version == VocabularyRef.vocabulary_id` (both `SegmentMap.build` and
  `MapVersion` are constructed from the same `vocabulary.vocabulary_id` — test asserts equality directly);
  `status="historical"` hardcoded in `assemble_segment_map`; `config_fingerprint` set to a non-trivial
  fingerprint of the real build config (`ref_n_grid`, `sector_min_laps`, `grip_db_path`, `vocabulary_id`,
  `version_label`); `layout_id` documented as the geometry-only hash value directly, sourced from the
  handoff's own offered options.

## Code/doc quality
Meets project rules per `docs/agents/CREW_CONTEXT.md`: DB-only access preserved (no FastF1/Jolpica import
in `derive.py`; all data access goes through G1/G3's own store-first seams + `SegmentMapStore`); no
module-level mutable state or DB singleton (`derive.py` carries only the frozen `DEFAULT_VERSION_LABEL`
constant); CLI logs via `logging.getLogger`, no stray `print()`; explicit `year`/`gp_name`/`session_type`
on every call, no silent latest-value fallback; config knobs are named keyword args with sane defaults.
Minor non-blocking observation: the `mixture`/`vocabulary` XOR-precondition `ValueError` names the
constraint but not a strict field+expectation+actual triple — acceptable for a paired-argument
precondition, not the data-validation case the project rule targets.

**Fowler refactoring pass** (`r6-fowler`, record at
`.agent-work/662-segment-map/g5-review/fowler_pass.json`, `scripts/verify_fowler_pass.py` exit 0):
12/12 baseline smells visited. `long-method`, `large-class`, `feature-envy`, `shotgun-surgery`,
`divergent-change`, `message-chains`, `speculative-generality`, `comments-as-deodorant` — **absent**.
`duplicated-code`, `data-clumps`, `primitive-obsession`, `long-parameter-list` — **overridden**: each
present-but-accepted smell is `derive.py`/`derive_segment_map` matching an established convention already
set by G1-G4's own signatures or test fixtures (e.g. `derive_segment_map`'s ~17 parameters is the direct
sum of three already-reviewed upstream config surfaces `reference_lap_from_store`/`derive_sector_lines`/
`fit_era_severity_mixture`; introducing a parameter object or shared conftest.py would require touching
G1-G4 modules or other gates' test files, which is outside g5's Allowed Scope). No smell rose to a
blocking defect.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in the impl result's "Map Impact" and "Real
  2023-weekend derive result" sections was independently reproduced (see Evidence verdict above), not
  just re-read.
- **Constraints not violated:** yes — `decision:derivation-subpackage-placement` and
  `decision:dormant-subphase` both honored (verified: no sub-phase/adjacency code; `derive.py` sits beside
  G1-G4 in `derivation/`).
- **Notes match the diff:** yes — the claimed new capability (`derive_segment_map` end-to-end entry point
  + CLI) matches exactly what the 3 new files contain; no missing or overstated structural claim.
- **Decision candidates surfaced:** yes — the `map_version` weekend-qualification tension (bare `"v1"`
  handoff wording vs. the store's actual global-PK schema) was explicitly surfaced with reasoning, not
  silently resolved. Reviewer independently confirmed the resolution is correct (see Reconciliation check).
- **Durable context routed:** yes — the `.gitignore` gap for `data/segment_maps.db` was flagged as a
  triage candidate by the implementer and re-flagged into this survey's `triage_candidates`
  (`tc1`) for Commander to drain, rather than dropped.

## Reconciliation check
One non-blocking reconciliation note: `map_version` is built as
`f"{year}-{gp_name}-{session_type}:{version_label}"` (e.g. `"2023-Bahrain-Q:v1"`), not the handoff's
literal Close-Criterion-4 wording `map_version="v1"`. Verified this is **required correctness, not a
deviation that breaks anything** — `store.py`'s `segment_maps` table primary-keys on `map_version` ALONE
(global across every weekend, confirmed by reading the `CREATE TABLE` statement), and `test_store.py`'s
own fixtures already use weekend-qualified strings (`"map:testonia:v2"`, `"map:t:2023"`, `"map:t:2024"`)
whenever more than one weekend is exercised in the same test. A bare literal `"v1"` for every weekend
would silently collide via `INSERT OR REPLACE` the moment a second weekend was written — confirmed live in
this review's own reproduction (a scratch-DB write of a second weekend would land at a distinct
`map_version` row, not overwrite Bahrain's). This is within the handoff's own Authority grant ("you MAY
decide ... the weekend key ... state them") and should be regraded by Commander as the settled convention
(currently only documented in the impl result's prose, not yet a recorded decision line) rather than
reopened.

## Blockers
- none

## Out-of-scope observations
- Triage candidate `tc1` (routed via the survey's `flag-candidate`): add `/data/segment_maps.db` to
  `.gitignore` (matching the existing named-`.db`-file precedent, e.g. `/data/damage_integrals.db`) before
  `scripts/derive_segment_maps.py` is run against its default output path in a tracked checkout — confirmed
  via `.gitignore` grep: no `/data/segment_maps.db` or generic `/data/*.db` entry exists today. This is a
  real gap the implementer already surfaced; not caused by g5, but not yet closed either.
- The Bahrain 2023 Q real-weekend result (36 segments, 13 corners) is plausible but not itself
  independently truth-checked against an authoritative Bahrain corner count in this review — per the
  handoff's own instruction, that rigor belongs to g6's gating/verdict pass, not this gate.

## Workflow Feedback
- **Handoff gaps:** none of substance. The reviewer handoff's point 4 ("verify this is correct, not a spec
  deviation that breaks anything") for the `map_version` format was exactly the right amount of steer —
  it named the open question without pre-answering it, which is what let this review independently
  re-derive the same conclusion from `store.py`'s schema rather than just trusting the impl result's prose.
- **Context rediscovered:** none — the g3-review-result.md's prior note on `data/f1_data_2023.db` being a
  pre-existing, already-accepted artifact saved a false-positive scope-drift finding here; that
  cross-gate memory worked as intended.
- **Instructions improvised around:** none.
- **What would have made this easier:** none — the two given verification commands plus the six numbered
  FOCUS items in the handoff were sufficient to drive a full independent reproduction with no additional
  digging required beyond reading the four named source files (`derive.py`, `runtime.py`, `store.py`,
  `identity.py`) and the test file, plus one live CLI re-run for idempotency (which the handoff did not
  explicitly ask for but which the "reproduce claimed side-effects" doctrine required).

## Return status
`complete`
