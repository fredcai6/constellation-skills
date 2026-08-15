# Mission Frame

Map-first frame for `crew-verdict-and-door`. Written under a DEGRADED-UNPARSEABLE map orientation
(see `.agent-work/crew-verdict-and-door/map-orientation.json`): this repo carries no `docs/architecture/`
packet overlay, and its derived code map (`map/ids.jsonl`) is structurally empty repo-wide (a fresh
`python -m scripts.code_map build --root .` still reports `ids: 0`), so there are no `capability:`/`struct:`/
`decision:` anchor ids anywhere in this repo to cite. Substitutes hash-pinned at context/orient time:
`README.md`, `docs/CHECKLIST_ENGINE_DESIGN.md`, `docs/agents/CREW_CONTEXT.md`. This frame is cut from those
plus a direct read of the two named functions in `scripts/run_crew.py` — source reads here CONFIRM the shape
the launch order and the substitute docs already gave, not build the frame from scratch.

## Intent
Stop `scripts/run_crew.py` from reporting `failed` for a crew whose dispatch bound both `--spine` and
`--result`, where the result artifact is absent/stale purely because the `archive` gate relocated the whole
work area (result document included), but the bound spine is genuinely terminal. Secondarily (bounded,
Task 2): make the `external`-backend door-binding hazard impossible to miss in the crew prompt/registry,
without attempting to bind it out-of-band.

## Affected Capabilities
No `capability:` anchors exist in this repo's map (empty `ids.jsonl`). In map-absence terms, the affected
behavior is: **crew-verdict judging** — `scripts/run_crew.py:finalize_from_exit_code` (and its two helpers
`result_exists`/`result_fresh`/`spine_terminal`, read directly at `scripts/run_crew.py:286-361`), which
decides whether a dispatched crew's registry entry reads `completed`/`blocked`/`failed`.

## Examples / Events
- The triage doc's observed incident: `constellation/epic-568-530/archive/commander/attempt-1`, dispatched
  with both `--spine` and `--result`, archived successfully (spine `archive: complete`, lease released), yet
  reported `failed` because the archive gate moved the result document out from under the watched path.
- This very dispatch is a live second instance: my own `archive` gate will relocate this run's own result
  document, so the primary checkout's unfixed `run_crew.py` will likely report this run `failed` too (noted
  in the launch order's closing section) — expected, not a signal to react to.

## Structural Anchors
No `struct:` anchors exist in this repo's map. Direct-read anchors instead (file:line, confirmed by reading
the source, not asserted from the launch order alone):
- `scripts/run_crew.py:954-1022` — `finalize_from_exit_code`: the verdict-computation function this run
  changes. `blocked_gate` (line 1005) is already checked ahead of both the result-artifact and
  spine-terminal paths whenever a spine is bound — the precedent Task 1's fix follows.
- `scripts/run_crew.py:286-292` — `result_exists`.
- `scripts/run_crew.py:295-314` — `result_fresh`.
- `scripts/run_crew.py:317-361` — `spine_terminal` (already handles missing/unparseable/malformed/empty-items
  spines as non-terminal — the fix must not weaken this).
- `scripts/run_crew.py:364-` — `spine_blocked_id`, the function backing the existing `blocked`-first
  precedent.
- `scripts/checklist_engine.py` — NOT touched (file-ownership fence); its `archive` gate's relocation
  behavior is confirmed correct and out of scope by direct instruction.

## Governing Constraints / Assumptions
- Constraint (file ownership) — only `scripts/run_crew.py` and its tests are mine to change; explicitly
  fenced off: `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`, `.mcp.json`, and the two named
  sibling worktrees.
- Constraint (no rubber stamp) — the fix must not make a genuinely failed crew (spine not terminal, no
  result) read as `completed`.
- Constraint (blocked wins) — `blocked_gate` must continue to be decided first, ahead of both the
  result-artifact and spine-terminal paths, unchanged.
- Assumption (archive relocation is correct) — the `archive` gate relocating the whole work area (result
  included) is working as designed; the fix lives entirely on the launcher's judging side.

## Decision Anchors & Decision Pressure
No map-carried decision anchors exist in this repo to cite. Decisions are pre-ruled instead, directly by the
launch order (frozen, not mine to relitigate):
- Ruling task-1-is-the-lane — ship Task 1 even if Task 2 is deferred.
  `@grade: settled/human · leans plan,execute`
- Ruling no-admiral-side-workarounds — the fix lives in the launcher, never in doctrine
  handed to every future Admiral (rules out "tell Admirals to pass survivable `--result` paths").
  `@grade: settled/human · leans plan,execute`
- Ruling clear-caches-before-measuring — cache-clean suite runs only, `.pyc` sweep first.
  `@grade: settled/human · leans execute`
- Decision pressure: exact wording/field name for "which check decided" in the registry entry (e.g. a new
  `verdict_reason` field vs. reusing an existing field) — resolved during execute as an implementation
  choice within Task 1's stated shape ("say which check decided"), not floated, since the launch order
  already names the requirement without prescribing the field name.

## Claims / Evidence Surfaces
- Claim (inversion is structural) — "every successful archive is reported failed, not sometimes." Verified
  by reading `finalize_from_exit_code` directly: when `result is not None`, `done = fresh` unconditionally;
  `spine_terminal` is only reached in the `else` branch. Confirmed true by source read, not just by trusting
  the launch order.
- Claim (red before green) — the launch order's required evidence: a dispatch given both `--spine` and
  `--result`, result artifact absent, spine terminal → `failed` before the fix, `completed` after. Driven
  through the real `finalize_from_exit_code`, not a mock.
- Claim (genuine failure still fails) — spine not terminal, no result → `failed`, both before and after.
- Claim (blocked still wins) — `blocked_gate` set → `blocked`, regardless of result/spine-terminal state,
  unchanged before and after.
- Claim (full suite green) — cache-clean baseline at `453f8492` is 3002 passed, 7 skipped, 0 failed, 1130
  subtests passed; re-measure cache-clean after the fix.

## Map Confidence / Staleness / Disputes
- The repo's derived code map is DEGRADED-UNPARSEABLE for this whole run (`map/ids.jsonl` empty repo-wide,
  even after a fresh `code_map build`). This is not specific to the `run_crew.py` area — it affects every
  orientation in this repo right now. Flagged as an escalation in the context-step receipt and as a triage
  candidate at the triage step; not blocking this dispatch (Task-1-is-the-lane latitude covers proceeding on
  substitutes).

## Out of Scope
- `scripts/checklist_engine.py`'s `archive` gate relocation behavior — confirmed correct, not touched.
- `scripts/hooks/spine_rail.py` — live target of in-flight work on #441, not touched.
- `.mcp.json` — shared config, not touched.
- Binding the `external` backend's MCP door out-of-band — impossible by construction per the launch order;
  Task 2's deliverable is a hardening (explicit unbound-door statement in prompt/registry), not a binding
  mechanism.
- Any gate other than `archive` relocating watched artifacts — investigated as an open question, answered or
  explicitly marked not-established, not implemented against speculatively.
