# Reviewer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
`g1` — issue #604, telemetry-never-fatal.

## Task statement (what was asked)

Make the MCP door's telemetry writes incapable of failing a tool call or killing the
server process, and prove it with a committed test that fails before the change.

Mechanism, as diagnosed at dispatch: `_log` (`scripts/mcp_spine_server.py:180-184`) wrote
`CALLLOG` and `START_MARKER` unguarded; `run_engine` calls `_log(rec)` at `:461` outside
its own `try/except`; `main()` catches only `KeyError`. So any `OSError` from a telemetry
write unwound the whole process, and the client saw only `Connection closed`.

## What was implemented

Commit `8b1d3208`, two files:

- `scripts/mcp_spine_server.py` — both writes in `_log` guarded against `OSError`
  separately (not one `try` around the body), plus a new module-private helper
  `_report_dropped_telemetry` that reports each drop on `stderr`.
- `tests/test_mcp_door_telemetry.py` — new, 247 lines, drives the real server as a
  subprocess.

The full `IMPLEMENTER_RESULT` is at
`.agent-work/cleanup-a-door/crew-handoffs/g1-implementer-result.md`.

## How to inspect the diff

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
git show 8b1d3208 --stat
git show 8b1d3208
git diff a69bbac4..HEAD -- scripts/mcp_spine_server.py
```

## Close criteria — verify each independently

1. **The crash reproduces pre-fix and does not post-fix**, both with real subprocess exit
   codes. Do not accept the pasted table; run it.
2. **The guard catches `OSError`, not bare `Exception`.** A bare catch is the wrong width —
   it would swallow programming errors.
3. **The loss is reported on `stderr`**, not silently dropped.
4. **No telemetry write anywhere in the module remains unguarded.** Enumerate every
   filesystem write in the module yourself and **state the count** — a guard that loops
   must assert what it looped over. Two independent passes have said four (`:181`, `:184`,
   `:492`, `:535`); confirm or refute with your own.
5. **`stdout` stays pure JSON-RPC** while telemetry is failing.
6. **The new regression test genuinely FAILS on the pre-fix tree.** Check it out and run
   it — do not accept the claim. Recipe: `git checkout a69bbac4 -- scripts/mcp_spine_server.py`,
   confirm the new helper is absent, clear `__pycache__`, run the test file, then
   `git checkout HEAD -- scripts/mcp_spine_server.py`.
7. **The `SPINE_CALLLOG` / `SPINE_START_MARKER` / `SPINE_REJECTION_LOG` env overrides still
   work** — `tests/test_mcp_lifecycle.py:102-103` depends on them.

## Allowed scope

Review only. Report findings; do not fix. If you find something small and obviously
correct to change, still report it — the Commander decides.

## Specific exclusions

- Fail-closed refusal **wording** for a missing or unbound spine is **gate g3's** (#603).
  The post-fix probe answering `isError: true` with a raw `FileNotFoundError` is the
  correct outcome *for this gate* — the door is alive and telling the truth. Do not block
  g1 for it.
- `_identity_violation` — fenced by the launch order.
- `checklist_engine.py`, `scripts/hooks/**`, `run_crew.py`, `gauge_reader.py` — lanes B
  and C, running concurrently.
- `.mcp.json`, `examples/mcp-interactive-demo/**` — gates g3 and g2.

## Constraints

- **Clear `__pycache__` before every measurement**
  (`find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +`). Stale
  bytecode from a relocated worktree fabricates failures that look exactly like defects;
  it cost epic 568 hours twice (#597).
- Validate against a **subprocess** you launch, never against this session's own door.
- The suite command excludes the spine env vars:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q ...`

## Map anchors (inbound)

Inherited from `g1-implement`. **Map entry point: none** — `map/ids.jsonl` is tracked but
empty (0 bytes), so no map anchor resolves anywhere in this repo (triage candidate `tc1`).
Verify against source, never against a map claim.

- **Structural:** `scripts/mcp_spine_server.py:180-219` (`_log` + new helper), `:441-462`
  (`run_engine`), `:472-499` (`_log_rejection`, the shape reused), `:1322-1377` (`main()`).
- **Capability:** door telemetry — call log and start marker, both now best-effort.
- **Constraints:** `constraint:stdout-is-the-protocol-channel`;
  `constraint:env-overrides-for-log-paths-must-survive`.
- **Decision:** `decision:telemetry-never-fatal` — drop the record and continue; never fail
  the call. `@grade: settled/measured · leans g1-implement`
- **Evidence:** `claim:604-kills-the-server`.

## Evidence already produced (reproduce, do not trust)

- Pre-fix baseline: `.agent-work/cleanup-a-door/evidence/pre-fix-probes.txt`
- Post-fix: `.agent-work/cleanup-a-door/evidence/post-fix-probes.txt`
- Implementer's suite run: `95 passed, 10 subtests passed`
- Commander's own re-verification: probe `EXIT 1 → EXIT 0`; pre-fix test run
  `5 failed, 2 passed`.

**Note the two that pass pre-fix.** The implementer disclosed, unprompted, that its
stdout-purity assertion passes on the unfixed tree too, because a dead door's stdout is
empty and therefore trivially pure. Judge whether that disclosure is complete — is the
*second* pre-fix pass equally benign, or is it a check that cannot fail?

## Verification commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
py .agent-work/cleanup-a-door/door_probe.py \
  /home/tommy/projects/constellation-skills/.agent-work/epic-418-followon/spine.json
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_mcp_door_telemetry.py tests/test_mcp_spine_server.py tests/test_mcp_identity.py \
  tests/test_mcp_lifecycle.py tests/test_mcp_door_engine_cwd.py tests/test_mcp_friction_capture.py
```

## Suggested model tier

`simple bounded` — small diff, fully specified criteria. The judgment is in criterion 4
(the count) and criterion 6 (proving the test discriminates).

## Stop conditions

Stop and return if: the diff exceeds the two files named; a fenced file was touched;
required evidence cannot be produced; or a decision outside review authority is needed.

## Return format

Return `REVIEW_RESULT` with a verdict of **`APPROVE`** or **`BLOCK`**, findings (each with
evidence you reproduced yourself), what you checked and found sound, and what you did NOT
check stated plainly as a scoped null. Include a `Workflow Feedback` section.

**Delivery.** Write the full `REVIEW_RESULT` to
`.agent-work/cleanup-a-door/crew-handoffs/g1-reviewer-result.md` **before ending your
turn** — that write is the delivery.
