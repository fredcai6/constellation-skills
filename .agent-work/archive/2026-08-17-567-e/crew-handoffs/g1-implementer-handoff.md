# Implementer Handoff

## Gate
g1 (`.agent-work/567-e/execute.json`)

## Task
In `scripts/mcp_spine_server.py` (this repo's MCP door), make two changes, both already fully
designed — implement, do not redesign:

**A. Capture a door-own rejection into the tracked `episodes/` store.** Today
`_log_rejection()` (line 761) already writes one JSONL line per door-own rejection to a local
sidecar (`mcp_rejections.jsonl`, via `_rejectionlog()`/`_telemetry_path()`), but that sidecar
is not `episodes/`, is not git-tracked, and does not survive worktree teardown. Add a second
side-effect, alongside the existing JSONL append, that — when a spine is bound — writes a
real episode into `episodes/` via `scripts/apply_episode_delta.py --store-root episodes`.

**B. Replace the CLI-recommending refusal tail.** `_THE_CLI_IS_PER_CALL` (line 1247,
`"Name a spine under that work area, or use the CLI, which is per-call by construction."`)
is used at the two `_spine_bind` containment refusal sites (lines 1396, 1437). Replace it with
text naming the path that actually works for a dispatched crew: it is launched with its spine
already bound (`run_crew.py --backend cli --spine`, which assigns `SPINE_FILE` and starts the
child in its own worktree) — the CLI is an operator/debug path, not an instruction aimed at an
agent (issue #559 already ratified this fleet-wide; this module's own docstring cites it).

## Protected Intent
A door refusal must not vanish. It must land somewhere a later reader can find it, without
ever inventing content the store's own doctrine (`docs/EPISODE_STORE.md` §10) forbids: an
auto-created episode's five agent-supplied assertions must never be fabricated narrative.

## Test Mode
Test-after allowed, with a required acceptance shape: trigger a REAL refusal through the door
in a FRESH process, read it back out of `episodes/` with `scripts/query_episodes.py`, and show
a NEGATIVE CONTROL (same trigger, capture call reverted/removed, no trace in `episodes/`).
Per repo doctrine (`docs/agents/ORCHESTRATOR_CONTEXT.md`, "Dogfooding") an in-session
observation after editing this file is not evidence — the trigger must run as a genuinely
separate `python` process, never imported into this same conversation's interpreter state.

## Close Criteria
- A real `_spine_bind` containment refusal (path-escape or cross-checkout — trigger whichever
  is easier to construct with a real spine file outside this checkout's `.agent-work/`),
  triggered via `scripts/mcp_spine_server.py`'s `call_tool()` entry point in a fresh `python`
  subprocess with `SPINE_FILE`/`SPINE_SESSION` set to a real, currently-bound spine (this
  run's own `.agent-work/567-e/spine.json` is a live candidate — check what step is
  in-progress on it first), produces one new episode under `episodes/active/`.
- `scripts/query_episodes.py fetch <the new id>` (or `enumerate`) reads it back and shows all
  five agent-supplied assertions and a complete `## Mechanical` block (no missing required
  field — if `episode_capture.mechanical_fields()` cannot honestly derive all nine
  `MECHANICAL_SCALAR_FIELDS`, capture is skipped for that call, not fabricated; if that is
  what happens on your first real attempt, find or construct a bound spine with an
  `in-progress` gate so the mechanical block is complete, rather than fabricating the missing
  field).
- With the new capture call reverted (`git stash` the diff, or an `if False:` bypass for the
  test only — your choice, just show it), the identical trigger produces NO new file under
  `episodes/` — negative control.
- The two `_spine_bind` refusal sites no longer contain the string `"or use the CLI, which is
  per-call by construction."` — `grep -n "per-call by construction" scripts/mcp_spine_server.py`
  returns nothing.
- Full existing test suite for this module still passes (`tests/test_mcp_spine_server.py`,
  `tests/test_mcp_spine_bind.py`, `tests/test_mcp_identity.py`, `tests/test_mcp_lifecycle.py`)
  plus `tests/test_episode_store.py`.
- New unit-level tests added for the capture path (mock/fixture-based is fine for these; the
  fresh-process trigger above is the separate, additional acceptance proof, not a substitute).

## Allowed Scope
- `scripts/mcp_spine_server.py` (sole writer this wave).
- New test file(s) under `tests/` for the new capture behavior (e.g.
  `tests/test_mcp_rejection_episode_capture.py`) — pre-authorized.
- `episodes/active/*.md` files your own trigger run creates during testing are expected
  byproducts of the acceptance proof, not stray files — keep them, they are the evidence.

## Specific Exclusions
- `scripts/checklist_engine.py` — fenced to lane H this wave. Do not touch, even to fix the
  observation (named below) that the engine's own `refusals` counter never sees a door-own
  rejection. That is a real, separate gap — record it as a triage candidate, do not fix it here.
- `docs/EPISODE_STORE.md`, any other file under `docs/**` except `docs/agents/CREW_CONTEXT.md`
  — fenced to lane D1 this wave.
- `scripts/run_crew.py` — fenced to lane F.
- Do not close the `spine_bind` hardlink hole (standing prohibition, unrelated to this task
  but touches the same function).

## Constraints
- Never hand-edit `episodes/**` — the only write path is `scripts/apply_episode_delta.py
  --store-root episodes`.
- Reuse existing module patterns rather than re-deriving:
  - `_write_amend_delta()` (line 815) for the shape of "write a delta JSON file beside
    `SPINE.parent`, timestamped" — `apply_episode_delta.py --delta` takes a FILE PATH, not
    inline JSON (confirmed via `--help` and source; do not attempt to pass JSON on argv).
  - `_own_checkout_for_binding()` (line 946) resolved once, joined with `"episodes"`, as the
    ABSOLUTE `--store-root` argument. A relative `--store-root` resolves against the
    subprocess's inherited cwd, which is not constant in this module (see `run_engine`'s
    docstring on `_standing_in_the_bound_spines_worktree`) — never pass a relative one.
  - `_derivable_work_id(spine_dict)` (line 1014) for the delta's `mechanical.run` field.
  - `episode_capture.mechanical_fields(checklist, base_dir)` (this repo's
    `scripts/episode_capture.py:407`) for the ENTIRE `## Mechanical` bin — do not
    hand-construct any of its nine fields. Read the bound spine's own JSON once
    (`json.loads(SPINE.read_text())`, the same pattern `_rebind_refusal` already uses at
    line 1144) and pass it straight to `mechanical_fields()`. If the returned dict is missing
    any of `MECHANICAL_SCALAR_FIELDS` (`run, project, role, spine-step, context-manifest-ref,
    refusals, reopens, rework-count, failed-commands`), **skip the capture entirely** — write
    a stderr diagnostic (mirroring `_report_dropped_telemetry`'s shape) naming which field(s)
    were missing, and do not call `apply_episode_delta.py` at all. This is the load-bearing
    rule that keeps this change inside `docs/EPISODE_STORE.md`'s own "refuse rather than
    fabricate" contract (`episode_capture.py`'s own `decision:refuse-never-fabricate`, cited
    in its `reopen_total` docstring) — do not relax it to "fill in a placeholder" under any
    circumstance.
- Every one of the five `agent_supplied` assertion fields must be a LITERAL derivation from
  data the refusal itself produced — never invented narrative (this is how the design resolves
  a real tension with `docs/EPISODE_STORE.md` §10's blanket "nothing should auto-create an
  episode" — see Authority below):
  - `task-intent`: `f"Called \`{tool}\` through the MCP door."` — the literal tool name, no
    argument dump (arguments may be large or carry paths not worth quoting whole).
  - `expected-behavior`: quote the tool's own registered MCP `description` string verbatim
    from the `TOOLS` list (module-level, ~line 1565) — a real, pre-existing string, not
    authored fresh. Look it up by name; if for some reason a tool name has no `TOOLS` entry
    (should not happen for any door-own-rejection-emitting call site), skip capture and say
    why in the stderr diagnostic.
  - `observed-behavior`: the refusal `message` string verbatim, exactly as `_tool_error`
    received it.
  - `impact-cost`: a fixed, always-true-for-this-population sentence, e.g. `f"The call did
    not proceed; {tool!r} returned REFUSED before it reached the engine."` (true by
    construction for every call that reaches `_tool_error` with `tool`/`rejection_class` set,
    since that only happens on the pre-`run_engine` path).
  - `workaround`: extract the LAST sentence of `message` (split on `". "`, take the final
    segment, strip) rather than repeating the whole message — every refusal in this module
    already ends with its own named escape hatch, so this is a literal substring, not
    something authored. Use `"none"` only if extraction yields the whole message unchanged
    (i.e., no sentence boundary found).
  - `strength`: `task-intent` and `observed-behavior` and `impact-cost` = `"strong"` (directly
    witnessed/mechanical facts); `expected-behavior` = `"weak"` (a declared contract, not
    evidence of what should have happened operationally); `workaround` = `"medium"` (extracted,
    not authored, but a heuristic substring rather than a certain fact).
- In-process dedup: capture AT MOST ONCE per `(tool, rejection_class)` pair per door-process
  lifetime (a module-level `set()`, checked/updated right where `_log_rejection` already logs)
  — bounds a retry-loop from mass-creating near-duplicate episodes. This is the filter; do
  not capture every occurrence.
- Skip capture entirely when `SPINE is None` (no bound spine, no work-id to attribute to) —
  say so in a code comment, do not invent a sentinel run id. The existing JSONL sidecar still
  gets that case when `SPINE_REJECTION_LOG` is set.
- The new subprocess call must never crash the door: wrap it in `try/except Exception`,
  fail loud to stderr (mirroring `_report_dropped_telemetry`'s contract), never raise past the
  caller. A capture failure must never turn a successful refusal-return into a server crash.
- The `_tool_error` choke-point itself (docstring cites
  `tests/test_mcp_identity.py::IdentityBindingPinTests.test_call_tool_can_only_produce_content_two_ways`)
  must keep its exact return shape — add the capture as a side effect called from inside
  `_tool_error` (or from `_log_rejection`, which `_tool_error` already calls), never by adding
  a second return path.

## Map Anchors (inbound)
- **Map entry point:** none — map is DEGRADED-UNPARSEABLE this wave
  (`.agent-work/567-e/map-orientation.json`); read `scripts/mcp_spine_server.py` directly.
- **Structural:** `scripts/mcp_spine_server.py:_tool_error:797`,
  `_log_rejection:761`, `_rejectionlog:297`, `_own_checkout_for_binding:946`,
  `_derivable_work_id:1014`, `_write_amend_delta:815`, `_THE_CLI_IS_PER_CALL:1247`,
  `_spine_bind:1252` (refusal sites `:1396`, `:1437`); `scripts/episode_capture.py:mechanical_fields:407`;
  `scripts/apply_episode_delta.py:_validate_create:1043`.
- **Capability:** MCP door rejection capture (issue #541); episode store single write path.
- **Constraints:** episode-store-single-write-path; refuse-never-fabricate; no-inode-containment.
- **Decision anchors:**
  `capture-is-literal-derivation-only` — resolves EPISODE_STORE.md §10's categorical
  no-auto-create stance by making every field a literal quotation/extraction, never invented
  judgment.
  `@grade: guess · leans g1-implement,g1-review · settle: run the acceptance trigger, show the
  five fields against the real captured episode, confirm none reads as invented`
- **Evidence expectations:** the three Close Criteria acceptance items above.
- **Map confidence flags:** none beyond the repo-wide DEGRADED state, already priced in.

## Deliverable Path Check
- **Committed** — `scripts/mcp_spine_server.py`; verify `git check-ignore scripts/mcp_spine_server.py; echo $?` prints `1` before you finish (already tracked, editing an existing file).
- **Committed** — new test file(s) under `tests/`; same check, expect exit `1`.
- **Committed** — `episodes/active/<new-id>.md` created by your own acceptance-trigger run;
  same check, expect exit `1` (episodes/ is tracked, not gitignored).
- **Local-only** — `.agent-work/567-e/mcp_amend_delta_*.json`-style temp delta files your new
  code writes beside the spine as part of normal operation are under `.agent-work/`, which is
  tracked in this repo (see Constraints above) — note in your result whether any such file was
  created during testing and where.

## Required Evidence
- The full captured episode file's content, pasted in your result (all `## Mechanical` and
  `## Agent-supplied` fields visible).
- `scripts/query_episodes.py`'s own output reading that episode back (exact command + output).
- The negative-control run's command + output showing no new file appeared.
- `grep -n "per-call by construction" scripts/mcp_spine_server.py` output (expect empty) and
  the before/after text of both replaced sites, quoted.
- `python -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_spine_bind.py tests/test_mcp_identity.py tests/test_mcp_lifecycle.py tests/test_episode_store.py <your new test file>`
  output, tail included, pass count stated.
- Which evidence is load-bearing: the fresh-process trigger + negative control (prove
  rigorously, these are the mission's own acceptance bar) versus the unit tests (confirmatory,
  a pass/fail count suffices).

## Wiring Grep
```bash
grep -rn "_capture_refusal_episode\|_maybe_capture_rejection" --include=*.py . | grep -v "def _capture_refusal_episode" | grep -v "def _maybe_capture_rejection"
```
(use whatever name you give the new function; state the count of call sites found outside its
own definition — expect exactly 1, the call site inside `_tool_error`/`_log_rejection`).

## Verification Commands
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-e-door-rejection-episodes
python -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_spine_bind.py tests/test_mcp_identity.py tests/test_mcp_lifecycle.py tests/test_episode_store.py
grep -n "per-call by construction" scripts/mcp_spine_server.py
```

## Suggested Model Tier
stronger — reason: real doctrine tension to implement faithfully (refuse-never-fabricate),
several existing module invariants (identity-binding pin, cwd-moves-mid-call) that a shallow
edit could silently violate, and the acceptance proof requires a genuinely fresh subprocess.

## Authority
Design is frozen by the Commander (`.agent-work/567-e/DESIGN_NOTE.md`, corrected against a
cold-critic pass) — do not redesign. One thing is explicitly NOT yours to decide: whether
`docs/EPISODE_STORE.md` §10's "nothing should auto-create an episode" permits this change at
all. The Commander has floated that tension to the Admiral rather than resolving it; you
implement the literal-derivation-only design as specified, and if in the course of building it
you find the tension is worse than described (e.g. `apply_episode_delta.py`'s validator
rejects the literal-derivation delta for a reason not yet identified), stop and report it as a
blocker — do not paper over it with an invented field.

## Stop Conditions
Stop and return if: the allowed scope must be exceeded; a specific exclusion must be touched;
`episode_capture.mechanical_fields()` never returns a complete set for any bound spine you can
construct in this worktree (meaning the acceptance proof is genuinely unobtainable, not just
inconvenient) — report this as a scoped null, not a workaround; a decision outside this
Authority section is needed.

## Return Format
Return IMPLEMENTER_RESULT per the template. Write it to
`.agent-work/567-e/crew-handoffs/g1-implementer-result.md` before ending your turn.
