# Implementation Result

## Assigned gate
`g1` (implementer) — `epic-567-door/cmdr-c`

## Completed slice
Two related prose edits stating that the Stop hook is authoritative over the SOFT-band context-trip advisory, and naming `spine_halt block` as the sanctioned mid-run exit when an agent genuinely cannot continue, so a Commander caught between the two mechanisms has a stated answer rather than one it has to infer.

1. `scripts/hooks/spine_rail.py` — `_mid_flight_reason(spine, aid)`'s returned string (the Stop hook's refusal message when an agent tries to end its turn mid-gate) now states explicitly that the hook is authoritative over the context-trip advisory, and points to the engine's block verb (`spine_halt block`) as the sanctioned exit in place of ending the turn to "hand off." `_owning_session_reason` was read and left unchanged — it addresses a different scenario (a gate owned by a *different* session/agent, where the stopping session cannot act on it at all), not this agent's own advisory-vs-Stop-hook fork, so it stays as-is per the handoff's own allowance.
2. `skills/commander/references/crew-dispatch.md` — added two sentences immediately after the existing `spine_halt block` guidance in "A harness-backgrounded command is never awaitable — do not park," stating the same precedence explicitly for a Commander reading the doc before ever hitting the fork live.

## Scope
**Files changed:**
- `scripts/hooks/spine_rail.py`
- `skills/commander/references/crew-dispatch.md`

**Specific exclusions touched:** no — `scripts/checklist_engine.py` and `scripts/mcp_spine_server.py` are untouched, confirmed by `git diff --name-only` (only the two files above appear) and `git status --porcelain` (see Evidence).

## Behavior changed
No. This is message-text/doctrine-prose only. `decide_stop`'s control flow, gate-open detection, and the nudge/3-strike escape hatch were not touched — only the string(s) `_mid_flight_reason` returns, and prose in `crew-dispatch.md`. The Stop hook fires under the exact same conditions as before.

## Map Impact
- **Structural anchors touched:** `scripts/hooks/spine_rail.py:1479-1499` (`_mid_flight_reason`) — message text only, no signature/behavior change. `_owning_session_reason` (`~1501-1520`) inspected, not modified.
- **Capabilities added/changed/affected:** none — no new callable symbol (per the handoff's Wiring Grep, this gate edits existing string literals inside already-wired functions).
- **Decision candidates / resolved decisions:** `decision:stop-hook-is-authoritative` and `decision:no-third-mechanism` (already ruled per Authority) are now reflected in shipped text at both the mechanism's own refusal message and the doc a Commander reads before hitting the fork — no new decision surfaced.
- **Trust limitations / drift found:** none found; `_mid_flight_reason` was the single place this message is generated (grep confirmed no other literal duplicates the old "Keep working the gate" phrasing elsewhere in the file).
- **Triage candidates:** none.

## Test mode
**Required:** `evidence-only` (inspection-only per handoff — doctrine/message-text, no unit-test surface for hook prose).
**Satisfied:** yes — the file parses as valid Python after the edit, and the diff is scoped exactly to the two allowed files.

## Evidence

```bash
$ git diff --stat scripts/hooks/spine_rail.py skills/commander/references/crew-dispatch.md
 scripts/hooks/spine_rail.py                  | 11 +++++++----
 skills/commander/references/crew-dispatch.md |  2 ++
 2 files changed, 9 insertions(+), 4 deletions(-)

$ python3 -c "import ast; ast.parse(open('scripts/hooks/spine_rail.py', encoding='utf-8').read())" && echo PARSE_OK
PARSE_OK

$ git status --porcelain
 M scripts/hooks/spine_rail.py
 M skills/commander/references/crew-dispatch.md
?? .agent-work/epic-567-door/
```

(The lone untracked entry, `.agent-work/epic-567-door/`, is this crew's own plan/handoff/result work area, created for this dispatch — not a source-file scope violation. No file under `scripts/` or `skills/` other than the two listed is touched.)

**Full diff:**

```diff
diff --git a/scripts/hooks/spine_rail.py b/scripts/hooks/spine_rail.py
index a2a4324b..dc56e3e3 100755
--- a/scripts/hooks/spine_rail.py
+++ b/scripts/hooks/spine_rail.py
@@ -1488,11 +1488,14 @@ def _mid_flight_reason(spine: dict, aid) -> str:
     return (
         "SPINE MID-FLIGHT: gate {aid} is still open -- you are in the MIDDLE of "
         "the spine, not at its end, so ending your turn now abandons an active "
-        "run. Keep working the gate -- do not end your turn to wait. "
+        "run. This Stop hook is authoritative over any SOFT-band context-trip "
+        "advisory you saw on spine_status/current -- that advisory is "
+        "non-binding guidance, never license to end this turn. "
         "Next imperative: {imp} "
-        "If this is an honest stop (genuinely blocked or out of scope), use the "
-        "engine's block verb to bubble the blocker to the parent, or waive the "
-        "check with human authority -- do not just stop."
+        "If you genuinely cannot continue (context exhausted, truly blocked), "
+        "the sanctioned exit is the engine's block verb -- spine_halt block -- "
+        "with a reason, or waive the check with human authority; do not end "
+        "your turn to \"hand off.\""
     ).format(aid=aid, imp=imperative)


diff --git a/skills/commander/references/crew-dispatch.md b/skills/commander/references/crew-dispatch.md
index 87220e5d..e7a1b223 100644
--- a/skills/commander/references/crew-dispatch.md
+++ b/skills/commander/references/crew-dispatch.md
@@ -34,6 +34,8 @@ The `until` loop itself is the one foreground command your turn is waiting on
 
 When a step genuinely cannot finish inside your turn, do not park on it either: run `spine_halt block` (the `spine_halt` MCP tool with `action=block`, or the CLI `<engine> block`), recording the crew id and what you were waiting on, so a parent resumes deliberately (the E1 fail-up path). A prohibition alone ("do not park") does not prevent this — it has been stated explicitly in a launch order and still failed, because at the moment a turn ends, waiting looks like the correct and careful thing to do. Reach for the idiom above by name; do not improvise a new wait.
 
+This Stop hook is authoritative over the context-trip advisory shown on `spine_status`/`current`: the advisory is non-binding guidance, never license to end a mid-gate turn. When the advisory says hand off and an open gate says otherwise, the gate wins — the resolution is `spine_halt block`, not a turn-end handoff.
+
 ## Backend: CLI vs Agent-tool harness
 
 The wrapper is backend-pluggable behind one result contract (see `docs/superpowers/specs/2026-07-07-crew-backend-design.md`). Two backends:
```

**Result:** pass — parse OK, scope confirmed to the two allowed files, close criteria satisfied (Stop-hook authority stated in `_mid_flight_reason`, `spine_halt block` named as sanctioned exit, `crew-dispatch.md`'s existing guidance now states the precedence, net-deletion: "Keep working the gate -- do not end your turn to wait." and "do not just stop." collapsed into the single precedence + single closing "do not end your turn to \"hand off\"" clause rather than repeating "don't stop" three ways).

## TDD evidence, if required
Not applicable — inspection-only test mode, no test surface for hook prose (per handoff).

## Docs/contracts touched
- `skills/commander/references/crew-dispatch.md` — doctrine addition, in scope per handoff.

## Assumptions
- `_owning_session_reason` does not need the precedence statement: it is the Stop-block reason for a gate owned by a *different* session/agent (foreign-owned, reachable only via a shared harness `session_id`), where the stopping session is told explicitly not to act on it at all — a structurally different scenario from the acting agent's own advisory-vs-Stop-hook choice that `_mid_flight_reason` addresses. Read in full before deciding; left unchanged.
- Kept the existing "or waive the check with human authority" clause in `_mid_flight_reason` alongside the new `spine_halt block` naming — it is a distinct, still-valid escape (overriding a failing postcondition) that the precedence framing does not make redundant.

## Stop conditions hit
None. No specific exclusion needed touching; no decision outside the given authority was needed; all required evidence was producible.

## Out-of-scope observations
None found beyond scope.

## Workflow Feedback

- **Handoff gaps:** none — the handoff named exact line ranges, the exact functions, the exact close criteria, and the exact exclusions; nothing was missing or ambiguous.
- **Context rediscovered:** none beyond what the handoff's Map Anchors and Evidence Expectations already pointed at (the two episodes, read as directed, gave the concrete shape of the fork without needing further digging).
- **Instructions improvised around:** the constellation-implementer skill's default template assumes `docs/agents/engine-config.json` exists (`config_ref` in `IMPLEMENTER_PLAN.template.json`); this repo checkout has no such file (matches the handoff's own note that the context step returned DEGRADED-UNPARSEABLE). Not a blocker — `checklist_engine.py`'s `load_config` falls back to engine defaults gracefully when `config_ref` does not resolve, so the plan drove to completion with default rework-cap/config behavior. Worth a workflow note in case a future gate expects Charter-tuned config values (e.g. a non-default rework cap) that silently do not apply here.
- **What would have made this easier:** nothing concrete — this was a well-scoped, self-contained handoff. One minor: the handoff's Verification Commands used `py -c ...`; this host's `py` on PATH did not resolve for this shell session in the way `python3` did, so I used `python3` per `docs/agents/CREW_CONTEXT.md`'s own guidance to check interpreter availability before relying on a name — consistent with, not a deviation from, project doctrine.

## Return status
`complete`
