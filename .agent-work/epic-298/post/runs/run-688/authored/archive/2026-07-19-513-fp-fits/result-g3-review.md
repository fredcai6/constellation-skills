# Review Result

## Assigned Gate
`g3` (513-fp-fits — cumulative_track_laps unlock, execute.json gate g3-review)

## Result
`APPROVE`

**Rework note (this supersedes the initial BLOCK below, kept for audit trail):** the sole
blocker from the first pass — `tests/unit/physics/layer2/test_estimate_store.py` crossing the
`simplification_limits` 1000-line threshold — was resolved by splitting the new `#513` tests into
`tests/unit/physics/layer2/test_estimate_store_cumulative.py` (194 lines). Independently
re-verified (survey item `r7-rework-verify`, not taken on the implementer's word):
- `py -m src.utils.simplification_limits --baseline --paths tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_estimate_store_cumulative.py`
  → **PASS (2 files checked)**, reproduced verbatim — no new violation.
- A strict non-baseline run over all 4 touched files does surface
  `cyclomatic_complexity=26` in `test_fit_quality_metadata_populated_and_round_trips`
  (`test_estimate_store.py`). Independently confirmed **pre-existing, not introduced by this
  gate**: `git show 27b6eac9:tests/unit/physics/layer2/test_estimate_store.py | grep -c "def
  test_fit_quality_metadata_populated_and_round_trips"` → `1` (the test already exists at that
  ancestor commit, confirmed via `git merge-base --is-ancestor 27b6eac9 HEAD` → true), **and**
  `git diff -- tests/unit/physics/layer2/test_estimate_store.py` touches zero lines inside that
  function. Same principle as `session_race.py`'s pre-existing violations from the first pass —
  correctly not re-blocked.
- Full target suite reproduced: `py -m pytest tests/unit/physics/layer2/test_estimate_store.py
  tests/unit/physics/layer2/test_estimate_store_cumulative.py
  tests/unit/physics/layer2/test_session_race.py -q` → **125 passed**, matching the claim exactly.
  Read `test_estimate_store.py`'s diff directly: the 5 moved tests are gone from that file
  (replaced by a 7-line pointer comment) and exist **only** in the new companion file — no
  duplication.
- Re-confirmed unchanged: `test_estimate_batch.py` 6/6 green, `compute_cumulative_track_laps`
  still byte-unchanged, `git status --short data/` still empty.
- Read the full companion file: pure `tmp_path` sqlite, no real DB, self-contained (no
  cross-test-file import) — matches the project's own stated precedent.

No new defect surfaced during rework verification. All other checks from the first pass (handoff
compliance, scope, evidence, reconciliation, Fowler pass) already passed and are unaffected by
this change.

## Handoff compliance
All 3 close criteria met and independently reproduced:
1. `EstimateRecord.cumulative_track_laps: Optional[int] = None` added next to `mass_kg_assumed`,
   self-heals via the existing generic `_migrate_missing_columns` (dynamically ALTERs any
   dataclass field absent from the table — the same mechanism `mass_kg_assumed` uses, no
   special-casing added). `test_cumulative_track_laps_self_heals_on_legacy_db` reproduced green
   in isolation.
2. `session_race.session_cumulative_track_laps(year, gp, session_type, constructor, db_path, *,
   session_id=None) -> Optional[int]` matches the handoff's spec exactly: resolves the
   constructor's drivers via `session_classifications.team` (`_constructor_drivers`), finds the
   fastest clean (`valid_lap=1`) lap among them (`_fastest_clean_lap_number`, `ORDER BY lap_time
   ASC LIMIT 1`), and returns `compute_cumulative_track_laps(session_id, anchor_lap, db_path)`
   verbatim. Returns `None` on missing session / constructor / clean lap (4 dedicated tests, all
   green, plus 1 happy-path anchor-selection test asserting the correct field-lap count).
3. `record_from_estimate` gained the optional `cumulative_track_laps: Optional[int] = None` kwarg
   (byte-identical default path — `test_record_from_estimate_cumulative_track_laps_defaults_none`
   and the full unmodified `test_estimate_batch.py` suite, 6/6, both reproduced green).
   `populate_cumulative_track_laps_for_demo` is confirmed UPDATE-only over rows already present
   for the named weekends — no `INSERT`, no `estimate_batch` call (read the function body; a
   dedicated test confirms a second, un-named weekend's row stays untouched/NULL).

Stop conditions were not triggered; TDD evidence (red→green per slice) is present and consistent
with what I reproduced.

## Scope drift
None. Exactly 4 files touched, all within allowed scope: `src/physics/layer2/estimate_store.py`,
`src/physics/layer2/session_race.py` (both explicitly named), plus their test files (the
handoff's named test path `tests/unit/physics/test_estimate_store.py` does not exist — the real,
only path is `tests/unit/physics/layer2/test_estimate_store.py`, a stale-path issue the
implementer correctly self-corrected and documented). Exclusions honored: `session_estimator.py`
and the views untouched; `git status --short data/` is empty; `compute_cumulative_track_laps` is
**byte-unchanged** (`git diff -- src/physics/layer2/session_race.py | grep -A3
compute_cumulative_track_laps` shows only trailing context and the new functions appended after
it — zero lines inside the function body are touched); no real backfill (`populate_..._for_demo`
never calls `estimate_batch`); physics-region import boundary is clean (grepped both changed src
files' imports — no `evo`/`latent_power`/`compound_prior`/`fastf1`).

## Evidence verdict
Required evidence present and independently reproduced, matching the implementer's claims exactly:
- `PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_estimate_store.py
  tests/unit/physics/layer2/test_session_race.py -q` → **125 passed** (reproduced verbatim).
- `git status --short data/` → empty (reproduced).
- Self-heal-on-legacy-store test isolated and green (reproduced).
- Additionally reproduced the two TDD-milestone selectors named in the implementer's Workflow
  Feedback (`-k cumulative_track_laps` → 5 passed; `-k SessionCumulativeTrackLaps` → 5 passed),
  confirming the plan's under-selecting `-k` filter was genuinely worked around, not gamed.
- `test_estimate_batch.py` (6/6) reproduced green, confirming zero regression for existing
  `record_from_estimate` callers.

TDD evidence (red before green, per-slice) is present in `result-g3-implement.md` and is
consistent with the diff shape.

## Code/doc quality
**(First-pass finding, RESOLVED by rework — see Result section above.)** One genuine **new**
project-standard violation, independently reproduced at the time:
`py -m src.utils.simplification_limits --paths src/physics/layer2/estimate_store.py
src/physics/layer2/session_race.py` → **FAIL, 2 violations**. Of the two,
`session_race.py`'s `file_lines=1366` and `load_race_stints=170` are both **pre-existing**
(confirmed via `git stash` + rerun against HEAD: already 1268 lines / already over the limit
before this diff touched it; `load_race_stints` itself is untouched by the diff). But
`tests/unit/physics/layer2/test_estimate_store.py` **crossed the threshold because of this
diff**: 888 lines at HEAD (under the `<1000` limit) → 1005 lines after the +117-line #513
addition. `docs/agents/CREW_CONTEXT.md`'s Verification-By-Region section requires this check for
every source change and states plainly: "Review blocker when skipped or failing on in-scope
Python." The implementer's evidence never ran or reported this required check. Severity is
low/should-fix — a pure line-count lint threshold on a test file, 5 lines over, no functional or
correctness risk — and the fix is trivial and low-risk: split the new `#513 G3` test block into a
companion file (e.g. `test_estimate_store_track_laps.py`), mirroring the project's own precedent
of splitting `estimate_store.py` itself into `estimate_store_fields.py` at #627 for the identical
reason.

All other project rules checked and pass: no module-level mutable state or DB singleton
introduced; missingness handled intentionally (`None` returned + explicit `no_lap` counter, never
zero-filled or guessed); no `print()` added to `src/`; docstrings match the file's existing
documentation conventions (the "APPROXIMATION" paragraph in `session_cumulative_track_laps`
explicitly names the pooling caveat, matching the handoff's explicit requirement).

**Fowler refactoring pass** (`.agent-work/513-fp-fits/g3-review/fowler_pass.json`, rail script
`verify_fowler_pass.py` PASSED): 12/12 baseline smells visited. 8 absent (long-method,
large-class, feature-envy, primitive-obsession, shotgun-surgery, message-chains,
speculative-generality, comments-as-deodorant). 4 present-but-overridden with logged
repo-standard reasons — duplicated-code (the ro-uri/fallback connect idiom repeats an
already-6x-pre-existing pattern in this file), data-clumps (the `year, gp, session_type` triple
is the codebase's established flat session-identity representation, not a new clump),
long-parameter-list (`record_from_estimate`'s growth follows the file's established per-issue
optional-kwarg-bolt-on pattern), divergent-change (`EstimateRecord`'s repeated per-issue growth is
the store's documented, intentional wide-schema self-heal evolution model, with a demonstrated
file-split mechanism at #627 for when it grows too large). Zero smells flagged as blocking; two
non-blocking triage candidates raised (see Out-of-scope observations).

## Map impact verdict
- **Evidence supports claimed change:** yes — every structural anchor named in the implementer's
  Map Impact notes (`EstimateRecord.cumulative_track_laps`, `record_from_estimate`'s new kwarg,
  `populate_cumulative_track_laps_for_demo`, `session_cumulative_track_laps` + 2 private helpers,
  `compute_cumulative_track_laps` reused unchanged) matches the diff line-for-line.
- **Constraints not violated:** yes — DB hygiene (#632) honored (`git status --short data/`
  clean), the `cumulative_track_laps` definition matches what was DECIDED in the handoff exactly
  (rubber-at-representative-lap, FIELD laps, `lap_number < anchor` convention), no deviation.
- **Notes match the diff:** yes, verified above.
- **Decision candidates surfaced:** yes — the constructor→driver resolution seam
  (`session_classifications.team` vs. `estimate_batch`'s live-FastF1 `_group_by_team`) is
  surfaced and **already logged** in `execute.json`'s `triage_candidates` as **tc2** (confirmed
  present verbatim). Per the dispatcher's explicit instruction, this is **not** re-blocked here.
- **Durable context routed:** yes — tc2 is correctly routed for #646 (the real backfill) to
  reconcile before relying on this seam at scale.

No architecture-map update is required at this gate: this is an additive capability within an
already-mapped `struct:physics.layer2` anchor (no new component/container boundary), appropriately
left for Cartographer/Commander to fold in at cleanup.

## Reconciliation check
None beyond what's captured above. No divergence from the recorded architecture baseline.

## Blockers
- None open. The sole first-pass blocker (`test_estimate_store.py` crossing the
  `simplification_limits` 1000-line threshold) was resolved by the rework (split into
  `test_estimate_store_cumulative.py`) and independently re-verified — see Result section above.

## Out-of-scope observations
- (tc2, already logged in `execute.json`) constructor-resolution seam mismatch between
  `session_cumulative_track_laps` (`session_classifications.team`) and `estimate_batch.py`
  (`_group_by_team` via live FastF1) — noted, not re-blocked per dispatcher instruction.
- (new, logged in this review's survey `triage_candidates`) consolidate the repeated
  `try:_ro_uri-connect/except-OperationalError-fallback-connect` block (now 8+ occurrences in
  `session_race.py`, including this gate's 2 new helpers) into a shared `_ro_query(db_path, query,
  params)` helper — future cleanup issue, not a defect of this gate.
- (resolved) the `test_estimate_store.py` line-count fix — was flagged as a triage candidate in
  the first pass, now resolved by the rework; kept in the survey's `triage_candidates` for audit
  trail only, no action needed.

## Workflow Feedback
- **Handoff gaps:** none beyond what the implementer already caught (the handoff's stale test
  path `tests/unit/physics/test_estimate_store.py` — real path has a `layer2/` segment). My own
  handoff (`handoff-g3-review.md`) was internally consistent and its reproduce commands worked
  exactly as given.
- **Context rediscovered:** had to git-stash the diff and rerun `simplification_limits --baseline`
  against HEAD to separate pre-existing violations (session_race.py, already over the limit before
  this diff) from a genuinely new one (test_estimate_store.py, newly crossed by this diff) — the
  tool's `--paths` output alone doesn't distinguish "was already failing" from "newly failing,"
  and neither the handoff nor the implementer's evidence mentioned this check at all.
- **Instructions improvised around:** none — the four explicit BLOCK triggers named in the
  dispatch were unambiguous and none fired; the `simplification_limits` finding sits outside that
  named list, so I applied the reviewer skill's own "quality vs inherited rules" check (r4-quality)
  and CREW_CONTEXT.md's explicit, unqualified "review blocker when... failing" language rather than
  treating it as automatically out of scope for this review.
- **What would have made this easier:** a future g3-adjacent handoff could name
  `simplification_limits` explicitly in its Required Evidence list (as CREW_CONTEXT.md already
  mandates it for every source change) so the implementer runs and reports it proactively rather
  than the reviewer having to discover the newly-crossed threshold independently.

## Return status
`complete`
