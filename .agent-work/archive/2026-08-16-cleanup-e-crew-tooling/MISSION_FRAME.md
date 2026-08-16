# Mission Frame

Map orientation for this run came back `DEGRADED-UNPARSEABLE` (see
`.agent-work/cleanup-e-crew-tooling/map-orientation.json`): `map/ids.jsonl` is
empty at HEAD even after a fresh `py -m scripts.code_map build`, and
`map/INDEX.md` uses module/entity-count prose rather than the
`struct:`/`capability:`/`decision:` anchor syntax `map_orient.py` expects, so
no anchor id in this repo's own generated map is ever citable by that tool.
Discharged with declared substitutes `README.md`, `map/INDEX.md`,
`docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`,
`docs/agents/CREW_CONTEXT.md`. This frame is built from those substitutes plus
the frozen `LAUNCH_ORDER.md`, which stands in as the map for a bounded,
already-triaged issue (Triage is done; #607 carries the measurement and three
fix directions, #525 its own repro).

## Intent

Ship two independently-verifiable fixes inside `scripts/run_crew.py`'s crew-launch subsystem, owned files only (`scripts/run_crew.py`, `scripts/recover_crews.py`, `tests/test_crew_launcher.py`):

1. **#607** — stop a blocking-by-design, healthy parent Commander from reading lease-stale while its child crew runs, without touching lease semantics in the fenced `scripts/checklist_engine.py`.
2. **#525** — namespace concurrent crews' evidence/scratch paths by the registry's own `(work_id, gate, role[, attempt])` tuple so two crews' evidence can no longer silently collide, and turn a genuine collision into a raised error.

## Affected Capabilities

- Crew dispatch and liveness bookkeeping in `map/INDEX.md`'s `scripts.run_crew` entry ("Safe crew launcher with a durable session-recovery registry", 62 entities) — `entry_liveness`/`active_duplicate` (#599, merged), the blocking `launch_process` call, `build_entry`/`save_registry`.
- Recovery classification in `map/INDEX.md`'s `scripts.recover_crews` entry ("Recovery classifier over the durable crew-run registry", 8 entities).
- The engine's own lease staleness (`checklist_engine.py`'s `_is_stale`/`require_session`) is a **dependency this run reads but does not modify** — it is fenced.

## Examples / Events

- The run that found #607, in its own words (pasted into `LAUNCH_ORDER.md`): "Measured: 53 minutes blocked on a live crew, and the engine already called that lease stale."
- #525's repro during issue #456: a `g8` reviewer found `r0` through `r6` finding-files already sitting in shared scratch from an earlier gate's reviewer, using the same generic names it was about to use; it noticed and prefixed its own. The next crew would not have noticed.

## Structural Anchors

- `scripts/run_crew.py` — `entry_liveness` (~:264), `active_duplicate` (~:330), `load_registry`/`save_registry` (~:237-249), `build_entry` (~:1028-1126), `launch_process` (~:846-887, the single blocking `subprocess.run` with no interim heartbeat/poll loop), `run_log_paths` (~:230-234, already namespaced by the full identity tuple).
- `scripts/recover_crews.py` — `classify_entry`/`classify_registry`.
- `tests/test_crew_launcher.py` — flat `unittest.TestCase` per concern (e.g. `EntryLivenessTests` ~:762), fixture dicts shaped to mirror real archived `crew-runs.json` entries, `RC`/`REC` module aliases loaded via `importlib.util.spec_from_file_location`.

## Governing Constraints / Assumptions

- `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`, `scripts/install_constellation.py`, `skills/commander/templates/**` are fenced — do not touch.
- CI is one `windows-latest` job, red at baseline; local Linux is the only real signal. `os.kill(pid, 0)` is POSIX-only; `process_alive` already carries the cross-platform seam and must not break.
- `__pycache__` must be cleared before every measurement (a cache built in another tree fails `tests/test_bytecode_cache_provenance.py` by name instead of surfacing where it actually bites).

## Decision Anchors & Decision Pressure

Pre-ruled by the Admiral in `LAUNCH_ORDER.md` (cited by name, not by the map's own anchor syntax — none of these are map nodes):

- Decision `registry-before-staleness` — a liveness reader should consult the crew registry before calling a lease stale.
  `@grade: guess · leans execute-607 · settle: tried first (see below); the registry lookup cannot be made available where staleness is judged (that logic lives entirely inside fenced checklist_engine.py, confirmed no owned file reads lease staleness today) — floating the alternative per the settle clause rather than escalating, since the alternative needs no change to checklist_engine.py's lease semantics.`
- Decision `no-reaping` — nothing in this lane marks an entry/lease abandoned, expires it, or force-claims anything.
  `@grade: settled/human · leans execute-607`
- Decision `fail-toward-alive` — every ambiguity resolves toward "this thing is running."
  `@grade: settled/human · leans execute-607`
- Decision `namespace-by-assignment` — #525's scratch path is namespaced by the same `(work_id, gate, role[, attempt])` tuple the registry already keys on.
  `@grade: guess · leans execute-525 · settle: confirmed the registry's exact key tuple in build_entry/active_duplicate before authoring the gate`
- Decision `no-silent-truncation` — an evidence collision under the new scheme is a raised error, never a quiet overwrite.
  `@grade: settled/measured · leans execute-525`

Decision pressure surfaced by this run (not yet settled, a candidate for the Admiral, not chosen unilaterally):

- Whether `run_crew.py` should heartbeat the parent's own lease periodically while `launch_process` blocks on the child (the alternative to the registry-consultation direction) is the concrete mechanism this run proposes for #607; it is inside inherited latitude (no `checklist_engine.py` change, only a call to its existing public `heartbeat` verb) so it is decided here, not floated — but the choice itself, and the rejected registry-consultation direction, is reported back at Review for the Admiral's record.

## Claims / Evidence Surfaces

- Claim: a blocked parent that used to read stale now does not, driven through the real registry and the real staleness path (`checklist_engine.py claim`/`current` against a genuinely aged `last_heartbeat`), in a fresh process — not reasoned about from inside this session.
- Claim: two crews whose evidence used to collide (same generic filename, same shared directory) now write to disjoint, tuple-namespaced paths; a forced collision (two dispatches sharing every element of the tuple) raises rather than overwrites.
- Full clean-env, cache-cleared suite at the published head, plus a `main` baseline re-measured at gate time (`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`).

## Map Confidence / Staleness / Disputes

- The map itself is degraded for reasons unrelated to this run's correctness (an anchor-syntax mismatch between `map_orient.py`'s contract and this repo's own generated `map/`, plus an empty `map/ids.jsonl`) — flagged as an escalation/triage candidate in `map-orientation.json`, not blocking this run's plan.
- `map/INDEX.md`'s entity counts for `scripts.run_crew` (62 entities, 11 holes) and `scripts.recover_crews` (8 entities, 3 holes) are read as coarse structural confirmation only, not as authoritative content — confirmed against source at plan/execute time.

## Out of Scope

- Reaping, expiry, or force-claim of any lease or registry entry (explicitly #552's, out of latitude here).
- Any change to `checklist_engine.py`'s lease semantics (fenced; the #607 fix stays inside owned files by construction).
- `#525`'s other half (no liveness signal for a dead crew) — already closed by #599.
- Anything under `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`, `scripts/install_constellation.py`, `skills/commander/templates/**` (lane A live there), `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py` (not owned, should not need changing).
