# Implementer Handoff (relaunch attempt-3 — pure re-verification, map now fresh)

## Gate
g3 (g3-implement) — end-to-end red/green proof + regression backstop

## What happened
Attempt-2 completed all real work correctly (`tests/test_code_map_precommit_e2e.py`, all 8 cases,
verified against the original handoff and passing) but returned `blocked`: the full local suite had
`1 failed` — `MapTreeFreshnessTests` — because this repo's own `map/INDEX.md` had gone stale from
gate 2's own tracked-file edits (`scripts/install_constellation.py`,
`tests/test_install_constellation.py`), never rebuilt since. Root-caused correctly by attempt-2; not
a defect in gates 1-3's code. The Commander has now run `python -m scripts.code_map build --root .`
directly (a mechanical, explicitly-authorized step per this repo's own `docs/agents/AGENT_GUIDE.md`
and the launch order's Inherited Context) — `map/INDEX.md` is now fresh (6 lines changed,
`map/ids.jsonl` unchanged), and `MapTreeFreshnessTests` passes in isolation.

## Your actual job
Confirm the full local suite is now genuinely green. Nothing else — no new test-writing, no
production code changes. This is pure re-verification.

Run the full suite in the **foreground, polling** — never background it and end your turn (this is
exactly the failure that killed attempt-1):
```bash
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q > /tmp/suite.log 2>&1 &
until grep -qE '^[0-9]+ (passed|failed|error)' /tmp/suite.log; do sleep 15; done
tail -5 /tmp/suite.log
```

## Close Criteria
- Full local suite: `0 failed`, pass count at or above `3622 passed, 6 skipped, 0 failed` plus this
  plan's added tests (gate 1's `test_code_map_precommit.py`, gate 2's `GitPreCommitHookWiringTests`,
  gate 3's `test_code_map_precommit_e2e.py`).
- `git diff -- tests/test_code_map.py` still empty.
- `git diff --stat -- map/INDEX.md map/ids.jsonl` shows the Commander's rebuild (6 lines on
  `map/INDEX.md`, nothing on `map/ids.jsonl`) — confirm this is the ONLY outstanding change to those
  two files, i.e. nothing else drifted since.

## Allowed Scope
None — verification only. Do not edit any file. If the suite is not actually green, STOP and return
`blocked` with the concrete failure evidence rather than attempting a fix here.

## Required Evidence
The full-suite command output (pass/skip/fail line), `git diff -- tests/test_code_map.py` (empty),
and `git diff --stat -- map/INDEX.md map/ids.jsonl`.

## Suggested Model Tier
simple bounded — pure re-run and report.

## Stop Conditions
Stop and return blocked if the suite is not green for any reason.

## Return Format
Return IMPLEMENTER_RESULT to
`.agent-work/w2-reindex/crew-handoffs/g3-implement-implementer-result.md` before ending your turn.
