# Implementation Result

## Assigned gate
`f3-can-it-reach`, `f4-tell-the-crew`, `f5-verify` (`f1-bind-parent` and `f2-blocked-is-not-failed` were already complete on entry to this session, per `CONTINUATION_HANDOFF.md`)

## Completed slice
- `f3`: recorded the measured reachability finding — two real probe crews were dispatched (by the Admiral, ahead of this session) with `--parent` bound and `SendMessage` granted. Probe 1 got a genuine tool-level refusal (`"No agent named 'Admiral session 717403d3' is reachable."`) when messaging a parent named by a descriptive string; probe 2, dispatched against the more plausible candidate name `"mcp cs"`, reported done and wrote no artifact — recorded as inconclusive rather than papered over. Wrote `.agent-work/epic-559/e1-fail-up/REACH_FINDING.md` with the `PROBE-EVIDENCE` marker and both results verbatim.
- `f4`: added one short paragraph each to `skills/implementer/SKILL.md` and `skills/reviewer/SKILL.md` — a gate/check a crew cannot satisfy blocks via `spine_halt block`, naming the gate and `SPINE_PARENT`, never waiving its own gate or inventing an authority; and never ending a turn waiting on something the crew itself started, poll inside the turn instead. Fixed the third copy of the stale CLI-fallback instruction in `skills/workbench/references/checklist-engine.md` (~line 34): it told every dispatched Implementer/Reviewer to drive its own plan/survey through the CLI, which is only true for a Task-tool subagent (inherits the dispatcher's MCP scope wholesale); a `run_crew.py`-dispatched crew is a fresh headless process with its own `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` bound before its MCP server starts, so its door is bound to its own plan from the first call — exactly what this session did, gate by gate, through `f3`/`f4`/`f5`.
- `f5`: full suite green, map rebuilt, result written, work committed.

## Scope
**Files changed:**
- `skills/implementer/SKILL.md`
- `skills/reviewer/SKILL.md`
- `skills/workbench/references/checklist-engine.md`
- `map/INDEX.md` (rebuilt)
- `.agent-work/epic-559/e1-fail-up/REACH_FINDING.md` (new)
- `.agent-work/epic-559/e1-fail-up/IMPLEMENTER_RESULT.md` (new, this file)

`scripts/run_crew.py` and `tests/test_crew_launcher.py` carry `f1`/`f2`'s pre-existing, already-complete diff — untouched by this session's `f3`–`f5` work, carried forward and committed here per the handoff ("Commit — gate `f5.c2` refuses on a dirty tree, and the previous instance left everything unstaged").

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `settings.json`, `docs/agents/*`, and `skills/*/templates/` were not touched.

## Behavior changed
Yes: `skills/implementer/SKILL.md` and `skills/reviewer/SKILL.md` now instruct a crew, in the place it already reads its door instructions, to block-and-name-parent rather than self-waive or invent authority, and to poll in-turn rather than yield on a started task. `skills/workbench/references/checklist-engine.md` now correctly routes a `run_crew.py`-dispatched crew to the door for its own spine instead of misdirecting it to the CLI (the CLI-fallback misdirection is what a cold reviewer this week disproved by driving its own bound survey through the door successfully).

## Map Impact
- **Structural anchors touched:** none new — no code symbols changed, only doc/skill text and REACH_FINDING evidence.
- **Capabilities added/changed/affected:** none in code this session (`--parent`/`blocked` capability landed in `f1`/`f2`, carried forward unchanged).
- **Constraints/assumptions touched:** the doc-level assumption that a dispatched crew must always fall back to the CLI for its own spine was wrong for the `run_crew.py` case and is now corrected in `checklist-engine.md`.
- **Trust limitations / drift found:** probe 2's inconclusive result means the "parent named directly, not descriptively" reach case is still unmeasured — flagged as a triage candidate below, not assumed either way.
- **Triage candidates:** re-run a probe with `--parent` set to the Admiral's own exact addressable session name (not a descriptive string, not a guess like `"mcp cs"`) to get a conclusive answer on whether `SendMessage` reaches a correctly-named parent; probe 2 wrote no evidence either way.

## Test mode
**Required:** evidence-only (gate checks are command-based; `f4`/`f5` have no TDD requirement)
**Satisfied:** yes — every gate's command-kind postcondition was satisfied and verified via `spine_advance` before closing.

## Evidence

```bash
grep -q 'PROBE-EVIDENCE' .agent-work/epic-559/e1-fail-up/REACH_FINDING.md && grep -q 'No agent named' .agent-work/epic-559/e1-fail-up/REACH_FINDING.md && test $(python -m pytest -q tests/test_crew_launcher.py -k "Parent" --collect-only 2>/dev/null | grep -c '::') -ge 4
# f3 postcondition — exit 0

for f in skills/implementer/SKILL.md skills/reviewer/SKILL.md; do grep -qi 'parent' "$f" && grep -qiE 'not waive|never waive|cannot waive' "$f" || exit 1; done; ! grep -qiE 'checklist_engine|CLI fallback' skills/implementer/SKILL.md skills/reviewer/SKILL.md
# f4 postcondition — exit 0

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
# f5 c1 — 2605 passed, 1 skipped, 1121 subtests passed
```

**Result:** pass — all three gates' command postconditions verified true, then closed through `spine_advance`.

## Docs/contracts touched
- `skills/implementer/SKILL.md`, `skills/reviewer/SKILL.md`, `skills/workbench/references/checklist-engine.md` — doctrine text only, no schema/contract change.

## Assumptions
- none

## Stop conditions hit
- none

## Out-of-scope observations
- Probe 2's inconclusive result (see Triage candidates above) — a conclusive reach test against the Admiral's real addressable name is still open.

## Workflow Feedback

- **Handoff gaps:** none — the handoff's verbatim evidence block for `REACH_FINDING.md` matched `.agent-work/epic-559/e1-fail-up/probe/REACH.md` on disk exactly, so no field was missing or ambiguous.
- **Context rediscovered:** the third-copy fix in `checklist-engine.md` required checking `tests/test_mcp_adoption.py::TestTier3ChecklistEngineReference::test_states_identity_trade_rule`, which pins the "dispatched subagent → CLI" sentence by regex (`in-session|dispatch\w*` AND `own\b` AND a CLI marker, all in one sentence). My first edit dropped the word "dispatch" while narrowing the sentence to the Task-tool-subagent case specifically, which broke that pinned test; re-adding "dispatched" to the sentence fixed it without weakening the correction. Worth flagging: that regex-pinned test is the reason the wrong instruction survived in three places for as long as it did — the pin was written to lock the OLD (wrong, for `run_crew.py` crews) instruction in place, and nothing in the test distinguishes a Task-tool subagent from a `run_crew.py` headless crew, so a future edit could easily re-break this test's intent without the test catching a similarly wrong distinction.
- **Instructions improvised around:** none.
- **What would have made this easier:** `tests/test_mcp_adoption.py`'s Tier3 pin could name explicitly that its "dispatched subagent" sentence is scoped to Task-tool subagents specifically (not `run_crew.py` crews), so a future editor fixing the `run_crew.py` case doesn't have to rediscover the regex's word-choice sensitivity by running the suite.

## Return status
`complete`
