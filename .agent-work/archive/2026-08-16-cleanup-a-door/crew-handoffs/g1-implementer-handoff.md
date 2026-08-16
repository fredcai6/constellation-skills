# Implementer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

## Gate
`g1` — issue #604, telemetry-never-fatal.

## Task

Make the MCP door's telemetry writes incapable of failing a tool call or killing the
server process, and prove it with a committed test that fails before your change.

The mechanism, already diagnosed — do not re-derive it:

- `_log` (`scripts/mcp_spine_server.py:180-184`) opens `CALLLOG` with no guard, and writes
  `START_MARKER` in the same function, also unguarded.
- `run_engine` calls `_log(rec)` at `:461`, **outside** its own `try/except` (`:445-458`).
- `main()` catches only `KeyError` around the dispatch (`:1355`, `:1360`).

So any `OSError` from a telemetry write unwinds the whole process. Reproduced at
`a69bbac4`, pasted in Required Evidence below.

## Protected Intent

A diagnostic side-channel must never be able to take down the thing it is observing.
The door stays usable when its own log is unwritable.

## Test Mode

**Test-first for the regression test.** Write the failing test, watch it fail on the
current tree, then fix. This is the gate's whole point — see Required Evidence.

## Close Criteria

- Every telemetry write in `scripts/mcp_spine_server.py` is guarded. Enumerate them by
  command and **state the count** — do not work from memory. (An independent AST pass
  found four filesystem writes in the module: `:181` and `:184` in `_log`, both unguarded
  and both yours; `:492` in `_log_rejection`, already guarded; `:535` in
  `_write_amend_delta`, guarded at its call site `:1289-1294`. Confirm this yourself.)
- The guard catches `OSError` — which covers `FileNotFoundError`, `PermissionError` and
  `IsADirectoryError` — **not** bare `Exception`. A bare catch would swallow programming
  errors and is the wrong width.
- A dropped record is reported on `stderr`, never silently discarded.
- A committed regression test fails on the pre-fix tree and passes after.
- The five MCP test files still pass.

## Allowed Scope

- `scripts/mcp_spine_server.py` — `_log` and its call site only.
- `tests/test_mcp_spine_server.py`, or a new `tests/test_mcp_door_telemetry.py` if you
  prefer a dedicated file. Your call.

## Specific Exclusions

- `_identity_violation` (`:236-363`) — **fenced** by the launch order (issue #603's lane);
  any change to its semantics floats to the Admiral.
- `scripts/checklist_engine.py`, `scripts/hooks/**`, `scripts/run_crew.py`,
  `scripts/gauge_reader.py` — owned by **lanes B and C, running concurrently**. Do not
  touch them for any reason.
- `.mcp.json` and the module's import-time `SPINE`/`ENGINE` reads (`:145-147`) — those are
  **gate g3's** (#603). Do not make `SPINE` optional here; that is a different change with
  its own review.
- `examples/mcp-interactive-demo/**` — **gate g2's** (#605).
- `scripts/install_constellation.py`, `skills/commander/templates/COMMANDER_SPINE.template.json`.

## Constraints

- **Preserve the environment overrides.** `CALLLOG`, `START_MARKER` and `REJECTIONLOG`
  read `SPINE_CALLLOG` / `SPINE_START_MARKER` / `SPINE_REJECTION_LOG` (`:162`, `:167`,
  `:177`). `tests/test_mcp_lifecycle.py:102-103` relies on them. A "simplification" that
  drops them breaks that test.
- **`stderr` is safe; `stdout` is not.** `main()` writes the JSON-RPC protocol to
  `sys.stdout` only (`:1367`, `:1375`). `_log_rejection` (`:472-499`) already uses
  `sys.stderr` for exactly this purpose — **reuse its shape rather than inventing a second
  one.** Its docstring states the principle: fail loud, every occurrence, no batching, no
  once-per-run flag, no silent drop.
- Validate by launching the server as a **subprocess** with the environment under test.
  Never reason about this session's own door — it is bound to whatever `.mcp.json` said at
  launch, which is the defect the epic is fixing.
- Do not "fix" the start-marker semantics while you are in there. `START_MARKER` is written
  on first successful engine call; keep that behaviour, just make it non-fatal.

## Map Anchors (inbound)

- **Map entry point:** none. `map/ids.jsonl` is tracked but **empty (0 bytes)**, so
  `map_orient.py` resolves no anchors for any area in this repo. The context step oriented
  `DEGRADED-UNPARSEABLE` with substitutes hash-pinned in
  `.agent-work/cleanup-a-door/map-orientation.json`. Start from the source, not a map.
- **Structural:** `scripts/mcp_spine_server.py:180-184` (`_log`), `:441-462`
  (`run_engine`), `:472-499` (`_log_rejection` — the shape to reuse), `:1322-1377`
  (`main()`).
- **Capability:** door telemetry — the call log and the start marker.
- **Constraints/assumptions:** `constraint:stdout-is-the-protocol-channel`;
  `constraint:env-overrides-for-log-paths-must-survive`.
- **Decision anchors:** `decision:telemetry-never-fatal` — the call log is diagnostic; if
  it cannot be written, drop the record and continue; do not fail the call.
  `@grade: settled/measured · leans g1-implement`
- **Evidence expectations:** `claim:604-kills-the-server` — reproduce the crash with its
  exit code, then show it not reproduced, with its exit code.
- **Map confidence flags:** `map/ids.jsonl` empty (triage candidate `tc1`) — verify against
  source, never against a map claim.

## Deliverable Path Check

- **Committed** — `scripts/mcp_spine_server.py`; `git check-ignore` exits 1 (not ignored).
- **Committed** — your test file; if new, it is untracked until staged, so `git diff` shows
  one file and the new test appears in `git status`.
- **Local-only** — anything you write under `.agent-work/`; do not expect it in the diff.

## Required Evidence

**Load-bearing — prove these rigorously:**

1. **The crash, before.** Measured at `a69bbac4`, and reproduced with
   `py .agent-work/cleanup-a-door/door_probe.py <path-under-a-missing-directory>`:

   ```
   File ".../scripts/mcp_spine_server.py", line 461, in run_engine
       _log(rec)
   EXIT 1
   ```

   Full output is at `.agent-work/cleanup-a-door/evidence/pre-fix-probes.txt`.

2. **The same probe, after** — the door answers the call and the process exits **0**.
   Paste both exit codes.

3. **The regression test failing pre-fix.** Stash or `git stash`/`git worktree` your fix,
   run the new test, and paste the failure. **Demonstrate it; do not assert that it would
   fail.** This is the gate's reason for existing: measured on the unfixed tree, this
   gate's own pytest postcondition reports `89 passed` — identical output in the healthy
   and the defective world, which is a check that cannot discriminate.

**Confirmatory — a spot-check suffices:**

4. The five MCP test files pass:
   `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_identity.py tests/test_mcp_lifecycle.py tests/test_mcp_door_engine_cwd.py tests/test_mcp_friction_capture.py`
5. `stdout` stays pure JSON-RPC when a telemetry write fails (the probe shows this).

## Wiring Grep

`none — this slice adds no new callable symbol.` It guards an existing function body and
adds a test. If you *do* factor the guard into a new helper, name it here and show a call
site outside its own definition, with the count.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
py .agent-work/cleanup-a-door/door_probe.py /home/tommy/projects/constellation-skills/.agent-work/epic-418-followon/spine.json
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_mcp_spine_server.py tests/test_mcp_identity.py tests/test_mcp_lifecycle.py \
  tests/test_mcp_door_engine_cwd.py tests/test_mcp_friction_capture.py
```

**Clear `__pycache__` before every measurement.** Stale bytecode from a relocated worktree
fabricates failures that look exactly like defects; it cost epic 568 hours twice (#597).

## Suggested Model Tier

`simple bounded` — the mechanism is fully diagnosed and the fix shape already exists in the
same module. The care is in the test, not the change.

## Authority

Already decided, not yours to revisit: `decision:telemetry-never-fatal` (settled/measured);
`OSError` as the catch width; `stderr` as the report channel; reusing `_log_rejection`'s
shape. Yours to decide: where the guard sits inside `_log`, whether the test lives in the
existing file or a new one, and the exact wording of the stderr message.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be touched;
the regression test cannot be made to fail pre-fix (that would mean the defect is not what
we think, which is a finding, not a failure); or a decision outside the given authority is
needed.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback.

`Return status` must be one of `complete | partial | blocked | out-of-scope | failed`,
written **lowercase** — the Commander copies it verbatim into this gate's evidence and the
postcondition matches on exact case.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to
`.agent-work/cleanup-a-door/crew-handoffs/g1-implementer-result.md` **before ending your
turn** — that write is the delivery.
