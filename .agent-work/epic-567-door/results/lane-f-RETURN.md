# RETURN — `cmdr-567-f` (#535 spec-through-spine, epic-567-door wave 2)

Worktree `/home/tommy/projects/constellation-skills/.worktrees/567-f-spec-through-spine`,
branch `feat/567-f-spec-through-spine`, base `f05a3d78`. **Not merged.**

## 1. Verdict

**Evidenced honest null.** The concrete mechanism #535 names — "dispatch should start with
'start the spine with this identifier,' not the launch order" — is already fully shipped in
`scripts/run_crew.py` (wave 1, PR #623), and this Commander session is itself live proof: it
was launched via `run_crew.py --backend cli --spine <this spine>`, its door resolved to its
own spine at startup, and `spine_lease claim` succeeded with no session-id argument. No
`scripts/run_crew.py` diff is warranted. Two real, adjacent gaps were found and are floated
below rather than built, because closing either sits outside this lane's file ownership and
latitude this wave.

## 2. The measurement

Full detail with source citations and command output: `.agent-work/archive/2026-08-17-567-f/notes-1.md`.

**(a) CLI-backend spine-only dispatch — shipped.** `CrewSpec.__post_init__`
(`scripts/run_crew.py:1369-1383`) requires only one of `--handoff`/`--spine`, only one of
`--result`/`--spine`. `build_crew_argv`'s spine-only branch (`:813-820`) emits exactly the
shape #535 asks for — no pasted document:

```python
elif spine is not None:
    prompt = (
        f"You are the constellation {role} crew for session {session}. "
        f"{parent_clause} "
        "Call mcp__spine__spine_status first: your spine is already bound. "
        "Drive it gate by gate through the door -- do not author a plan of "
        "your own -- until it reports done."
    )
```

Session identity is derived, never caller-supplied: `_crew_door_env` (`:1010-1048`) sets
`SPINE_SESSION = assignment_session_name(work_id, gate, role)`, so `IDENTITY_TRADE.md` §3
stands untouched (not reopened this run, per the launch order).

Command:
```
python -m pytest tests/test_crew_launcher.py -k "spine_only or refuses_spine or spine_status" -q
-> 14 passed, 203 deselected
```

**(b) ExternalBackend (the Agent-tool-harness crew dispatch path) — refuses spine-only, by
design.** `ExternalBackend.dispatch` (`:1685-1702`) raises whenever `spec.handoff is None`,
even with `spec.spine` given. This is the backend a Commander running inside the Constellation
Agent-tool harness actually uses to dispatch Implementer/Reviewer crews
(`skills/commander/references/crew-dispatch.md`). Deliberate and tested
(`test_external_backend_refuses_spine_only_with_no_handoff`), not an oversight.

**(c) `spine_open`'s spec compilation — covers gate plans, not Commander-level mission
content.** Only `specs/implementer.spine.toml` and `specs/reviewer.spine.toml` exist,
confirming the launch order's named Local Unknown. A Commander's own `spine.json` is stamped
from the fixed `templates/COMMANDER_SPINE.template.json`, never spec-compiled from a launch
order — the mission-specific content (everything beyond the fixed step names) travels only as
a pasted `--handoff` document, exactly as it did for this dispatch (both `--handoff` and
`--spine` were given to launch this session).

## 3. The remaining gap

Two distinct claims:

1. **The CLI-backend, Admiral→Commander path** — the concrete mechanism #535 names — is
   **fully delivered**. Nothing to build.
2. **The ExternalBackend, Commander→crew (Agent-tool) path** cannot go spine-only, and the
   blocker is a **harness constraint**: `ExternalBackend` spawns no process and builds no
   environment (the subagent is spawned by the Commander's own `Agent` tool call, which takes
   no environment-variable parameter — only `description`, `prompt`, `model`, `subagent_type`,
   `isolation`, `run_in_background`). No change inside `scripts/run_crew.py` can bind
   `SPINE_FILE`/`SPINE_SESSION` into an Agent-tool subagent's MCP door. Architecture-level,
   floated below.
3. Making the Commander-level launch-order content itself spine-carried would need a spec
   schema and Commander spine template that do not exist, in `skills/**` paths fenced to lane
   D1 this wave. Floated below, not built.

## 4. What I built

**Nothing in `scripts/run_crew.py`.** Zero diff. The measurement itself is the deliverable.

## 5. Floated edits

Neither is inside lane D1's tree literally (I did not draft an edit there), but both name work
that would land there or in `scripts/mcp_spine_server.py` / `scripts/generate_spine.py`
(lane E), out of this lane's ownership:

1. **ExternalBackend spine-only, if the human wants it pursued**: needs a harness capability
   that does not exist today (an env-passing parameter on the `Agent` tool), or a different
   mechanism for the Agent-tool path to resolve spine identity — e.g. the subagent itself
   calling a door verb at startup that names its own `(work_id, gate, role)` and resolves
   server-side against the dispatching Commander's registry, rather than relying on inherited
   environment. This is a genuine open design question, not a small patch.
2. **Commander-level spec-through-spine, if the human wants the fuller reading pursued**: a
   Commander-level (or launch-order-level) spec schema carrying Mission/Pre-Rulings/Latitude/
   File-Ownership fields, a compiler extending `generate_spine.py`'s pattern to it, and a
   `stand-up-work-area.md` change to mint the Commander's spine from that spec instead of the
   fixed template. Multi-lane, architecture-level.

Both are staged as triage candidates (see §9), not filed as issues.

## 6. Suite result

Full suite, Linux, clean detached worktree of this branch (`git worktree add --detach`), commit
`5c65c00ff5829297b95d0834ada5a115863c2463`:

```
3352 passed, 6 skipped, 1219 subtests passed in 140.60s (0:02:20)
```

`grep '^FAILED' /tmp/567f_suite2.log` → no matches (exit 1). `MapTreeFreshnessTests` did not
fail (nothing touched the map). Command environment excluded `SPINE_FILE`/`SPINE_SESSION`/
`SPINE_PARENT`/`CREW_SCRATCH_DIR` (this session's own ambient values, which otherwise leak
into `test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
via `fake_launch`'s `os.environ` base — confirmed by reproducing the failure with only the
first three unset, and clearing it with `CREW_SCRATCH_DIR` also unset; a genuine test-harness
environment-leak hazard for any dispatched crew running the suite from inside its own
dispatch, not a defect in the suite or in `scripts/run_crew.py`).

## 7. Touched paths

- `.agent-work/archive/2026-08-17-567-f/**` — this lane's full work area (spine, execute.json,
  notes-1.md, MISSION_FRAME.md, REPLAN_INPUT.json, map-orientation.json, triage-candidates/,
  episode-delta*.json), moved from `.agent-work/567-f/` at archive.
- `.agent-work/staged-feedback/567-f/CONSTELLATION_FEEDBACK.md`, `FENCE.md` — durable-root
  feedback export, staged (main checkout fenced, per Data Locations).
- `episodes/active/567-f-001.md`, `567-f-002.md`, `567-f-003.md` — 3 episodes.
- `.agent-work/epic-567-door/results/lane-f-RETURN.md` — this file.

**No file inside `scripts/run_crew.py` was touched** — the one file this lane owns. No file
in `skills/**`, `specs/**`, or `scripts/mcp_spine_server.py` was touched (fenced to other
lanes; nothing in this lane's mission needed them).

## 8. Map impact

None. No `docs/architecture` map exists for this repo (skill-source repo); `map/INDEX.md`
and `map/ids.jsonl` were not touched (`decision:map-index-is-admiral-owned`). No source file
changed, so there is nothing to reconcile into any record even if one existed.

## 9. Triage candidates

Staged as files, not filed as issues (`decision:no-issue-filing-mid-run`), under
`.agent-work/archive/2026-08-17-567-f/triage-candidates/`:

- `external-backend-spine-only.md` — §5 item 1 above, in full.
- `commander-level-spec-compilation.md` — §5 item 2 above, in full.

## 10. Workflow feedback

Staged (durable root fenced) at `.agent-work/staged-feedback/567-f/CONSTELLATION_FEEDBACK.md`,
with `FENCE.md` citing the Data Locations rule. Two mistakes worth naming here directly:

1. I initially wrote the mission frame's own explanatory prose using a decision's shorthand
   name (`decision:map-index-is-admiral-owned`), which tripped `verify-frame`'s anchor scanner
   even though it was never meant as a map citation — every matched anchor is an automatic
   refusal in DEGRADED mode. Fixed by rewording in plain language and citing the DEGRADED
   substitutes literally instead.
2. I then wrote an episode assertion containing the ruling name
   `measure-before-you-build`, which the episode-observation guard's word-boundary scan read
   as second-person `you` (hyphens count as boundaries) — caught only by running the full
   suite, not by any earlier gate. Fixed with a `restate-assertion` op rather than a hand-edit.
   Both mistakes are the same shape: a decision's hyphenated shorthand name colliding with an
   unrelated text scanner. Worth a passing mention in the relevant guard's own doctrine.

## 11. PR

Opened against `main` from `feat/567-f-spec-through-spine`: **PR #627**,
<https://github.com/fredcai6/constellation-skills/pull/627>, head sha
`3bb00674010134dc0ff3c2d017d1e3f8a9f0a25a`.
