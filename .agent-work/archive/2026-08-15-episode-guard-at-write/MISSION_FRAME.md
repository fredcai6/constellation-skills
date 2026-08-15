# Mission Frame

Map for this repo is DEGRADED-UNPARSEABLE (`map/INDEX.md` unfilled, `map/ids.jsonl` empty) —
recorded via `map_orient.py` with substitutes `docs/EPISODE_STORE.md` and
`docs/agents/ORCHESTRATOR_CONTEXT.md`. No `capability:`/`struct:`/`decision:`/`claim:` node ids
exist to cite, so this frame names the substitute docs and real file paths directly rather than
inventing anchor ids the map inventory cannot back.

## Intent

Reject an instruction-shaped episode statement at write time — in `scripts/apply_episode_delta.py`,
the store's single write path — using the read-time guard (`scripts/verify_episode_observations.py`'s
`triggers_for`/`EXCEPTIONS`) rather than a second implementation of its rules, so a lane's own
write can no longer pass cleanly and red `tests/test_episode_observations.py::RealStoreTests` later,
once the episode it had not yet written at integrate-time exists for that suite to scan.

## Affected Capabilities

- The episode store's write path (`docs/EPISODE_STORE.md`) — `validate_delta`/`apply_delta` in
  `scripts/apply_episode_delta.py`, specifically the `create` and `restate-assertion` ops (the two
  that write a `statement` field).
- The read-time guard (`scripts/verify_episode_observations.py`) — consumed, not modified: its
  `triggers_for(kind, statement)` and `EXCEPTIONS` are imported, its rules are not restated.
- The installer's runtime-companion bundling (`scripts/install_constellation.py`,
  `SCRIPT_RUNTIME_COMPANIONS`) — the guard has to ship alongside the writer in installed skill
  copies or the check silently no-ops there.

## Structural Anchors

- `scripts/apply_episode_delta.py` — `validate_delta` (pure, no disk I/O), `_apply_create`,
  `_apply_restate_assertion`, `_Transaction`, `store_root()`.
- `scripts/verify_episode_observations.py` (read-only; not mine to modify) — `triggers_for`,
  `EXCEPTIONS`.
- `tests/test_episode_observations.py` (read-only; not mine to modify) — `RedProofTests`,
  `RealStoreTests`; builds adversarial fixtures THROUGH the writer.
- `tests/test_episode_store.py` — the writer's own test suite; every fixture targets a throwaway
  `--store-root`, never the tracked `episodes/`.

## Governing Constraints / Assumptions

- `docs/EPISODE_STORE.md` — validate-then-apply, all-or-nothing; the writer is the sole write path.
- `validate_delta`'s own docstring — pure, no disk I/O, rejects before any file is touched
  regardless of store contents.
- LAUNCH_ORDER.md's file ownership: `tests/test_episode_observations.py`,
  `scripts/verify_episode_observations.py` and others are explicitly NOT mine to modify.
- `docs/agents/ORCHESTRATOR_CONTEXT.md`, "The Retired Learning Playbook" — an episode is a record,
  never read back as a rule; this change enforces WRITE-time shape, not a read-and-apply loop.

## Decision Anchors & Decision Pressure

- decision:guard-import-lazy-by-file-location — `apply_episode_delta.py` resolves
  `verify_episode_observations.py` lazily via `importlib.util.spec_from_file_location`, mirroring
  the guard's own resolution of `query_episodes.py`, so it works both in-repo and installed.
  @grade: settled/measured · leans execute-1 · settle: ran under both direct-repo and a companion-guard install test

- decision:check-placement-apply-phase-not-validate-delta — the guard call sits in `_apply_create`
  and `_apply_restate_assertion`, not inside `validate_delta`, so `validate_delta` stays exactly as
  pure as before (no new parameter, no disk touch) and every existing direct caller of
  `validate_delta` (test_episode_fields.py, test_episode_negative_control.py, test_episode_store.py)
  is unaffected.
  @grade: settled/measured · leans execute-1 · settle: full-suite run confirmed those callers unaffected

- decision:scope-to-real-store-only — the guard fires only when the write targets the store
  `store_root()` itself resolves to (`_is_real_store`), never an explicit `--store-root` temp
  directory. Forced by a genuine conflict: `tests/test_episode_observations.py::RedProofTests`
  builds a store the guard must refuse by writing THROUGH this exact writer into a temp root: an
  unconditional guard makes that fixture-building impossible without touching a file this lane may
  not modify.
  @grade: settled/measured · leans execute-1 · settle: full-suite run green with this scoping; a dedicated new test (test_episode_observation_guard_at_write.py) proves the guard still fires against a simulated real store

- decision:grandfathered-restate-bypass — `restate-assertion` against an assertion on the guard's
  own `EXCEPTIONS` list is exempt from the check entirely (any statement), so a grandfathered
  assertion stays editable.
  @grade: settled/human · leans execute-1 (LAUNCH_ORDER.md hazard: "must not reject an amendment to one of those")

- decision:install-companion-manifest-update — `scripts/install_constellation.py`'s
  `SCRIPT_RUNTIME_COMPANIONS["apply_episode_delta.py"]` now names `verify_episode_observations.py`
  and (transitively required by the companion-guard's own static reachability scan)
  `query_episodes.py`. Outside the narrow "yours" file named in LAUNCH_ORDER.md, but required or the
  feature silently no-ops in every installed skill copy; the write-side bundle comment in that file
  already anticipated this exact route.
  @grade: settled/human · leans execute-1 (floated in this run's report per LAUNCH_ORDER.md "say so and float")

## Claims / Evidence Surfaces

- claim:red-green — a `create` op with a bare-verb-opening `workaround` statement was accepted
  pre-change and is rejected post-change, driving the real script (not a reimplementation).
  Verified by `tests/test_episode_observation_guard_at_write.py::RedBeforeGreenAfterTests`.
- claim:control — a well-formed create still writes. Verified by `ControlTests`.
- claim:message-names-offender — the rejection names the offending word and kind. Verified by
  `test_the_rejection_names_the_offending_word_and_kind`.
- claim:grandfathered-editable — a restate against an EXCEPTIONS-listed assertion still writes even
  with a tripping statement; the same statement against a non-excepted assertion is refused.
  Verified by `GrandfatheredExceptionTests`.
- claim:no-regression — full clean-env suite, 0 failed. Verified by the closeout suite run.

## Map Confidence / Staleness / Disputes

- The repo's own architecture map (`docs/architecture/`, `map/`) is absent/unbuilt for this run —
  `map_orient.py` returned DEGRADED-UNPARSEABLE. LAUNCH_ORDER.md already names the fix
  (`python -m scripts.code_map build --root .` at closeout), so this is not a new gap to surface —
  it is scheduled work this run's own closeout performs.

## Out of Scope

- The guard's rules or its exception list (`scripts/verify_episode_observations.py`,
  `tests/test_episode_observations.py`) — not mine to change.
- Gate ordering (closeout vs. integrate) — larger blast radius, not recommended by the triage doc.
- Retro-fixing existing `episodes/` records — all pass today; left alone.
