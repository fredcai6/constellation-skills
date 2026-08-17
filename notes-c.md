# Working notes — cmdr-567-c (epic-567-door lane C)

## Bootstrap
- Worktree isolation verified: `worktree OK: in .../567-c-rail-readability`.
- Read `LANE_C_LAUNCH_ORDER.md` in full before touching source.
- Loaded `constellation-commander-delegated`, drove `spine.json` (work-id `epic-567-door/cmdr-c`)
  through the installed engine at `/home/tommy/.claude/skills/constellation-commander/scripts/checklist_engine.py`
  via CLI fallback (the MCP `spine_*` door tools reported "no spine is bound to this door" for a
  freshly-minted spine in this session — used the documented CLI fallback for every verb instead).

## The load-bearing discovery (understand step)
Before writing the mission frame, grepped the actual source for the mission's two named strings:
- `RAIL:` banner text and the HARD refusal's `attach ... refresh-request` remedy string (#442's two
  problem instances).
- The context-trip SOFT advisory's own wording (#595, "hand off here… advisory — decline with a
  reason if you're nearly done").

All three live in `scripts/checklist_engine.py`:
- `_RAIL_STRINGS` (the RAIL banner table), lines 310-326, explicitly commented
  "the five strings are FROZEN and verbatim (measurement precondition for #145) — do not paraphrase".
- `_refresh_attach_hint` (the HARD refusal's exact remedy command), lines 1532-1543.
- `_trip_advisory`'s SOFT branch (the context-trip advisory's own wording), lines 1858-1861.

`scripts/hooks/spine_rail.py` — this lane's sole-owned file — contains none of these. It has only the
Stop hook's own `SPINE MID-FLIGHT` refusal text (`_mid_flight_reason`, `_owning_session_reason`,
~1479-1520).

The launch order's Fence section says: "you do NOT own `scripts/checklist_engine.py` ... Lane A owns
[it] this wave. If the rail or advisory text you must change is authored inside either file, stop and
float to the Admiral rather than editing it. This is a genuine possibility for your mission; expect
it and ask early rather than late." That is exactly what happened — not a hypothetical, a confirmed
fact of the current source tree at base commit `600de020`.

Cross-checked `LANE_A_LAUNCH_ORDER.md`: Lane A's own mission (#559, per-dispatch spine identity) does
not plan to touch these specific strings either — the fence is a wave-sequencing artifact (concurrent
hook-file edits break every live session), not a competing intent. So this is purely a sequencing
question for the Admiral, not a design disagreement between lanes.

## Scope decision
Recorded this as a `user-decision` at `understand` citing `LAUNCH_ORDER:Mission`, and again at `plan`.
Scoped the plan to the ONE deliverable actually reachable this wave:
1. `scripts/hooks/spine_rail.py`'s `_mid_flight_reason` states the Stop hook is authoritative over the
   context-trip advisory and points at `spine_halt block`.
2. `skills/commander/references/crew-dispatch.md` states the same precedence next to its existing
   `spine_halt block` guidance (line ~35) — this file is explicitly named in-scope shipped doctrine by
   the pre-ruling `decision:no-doctrine-promotion` ("#595's resolution names crew-dispatch.md, which
   is shipped skill doctrine ... that one is in scope").

#442 (RAIL banner + HARD refusal readability) could not be attempted at all — no editable surface
existed in the sole-owned file. Floated as a triage candidate (`tc2`) and a `blocks_current_wave_exit`
discrepancy in `REPLAN_INPUT.json`, not guessed past.

## Execution
- One crew gate (`g1`): implementer dispatched via `run_crew.py --backend external` + Agent tool
  (general-purpose subagent loading `constellation-implementer`), then a reviewer the same way loading
  `constellation-reviewer`. Both delivered clean, complete results; independently re-verified the diff
  against the world both times (not just trusting the pasted evidence).
- Reviewer ran a full Fowler pass and flagged one non-blocking finding (duplicated precedence prose
  across the two files) — logged as triage candidate `tc1`, not fixed silently.
- Fresh-process validation (per `decision:in-session-observation-is-not-evidence`, #269): built a
  synthetic binding-store + spine fixture under `.agent-work/`, ran
  `CLAUDE_PROJECT_DIR=<worktree> py scripts/hooks/spine_rail.py Stop < fixture` as a genuinely new OS
  process, confirmed the new wording rendered in the JSON `reason` field, then deleted the scratch
  fixtures.

## Cold-agent measurement (#442's stated acceptance)
Not run. #442's target text lives entirely outside this lane's editable surface (see above) — there
was no rewrite to measure. This is reported as the honest scope limit it is, not substituted with a
measurement of something else.

## Workflow observation (for feedback step, not obeyed as a rule)
The launch order's File Ownership grant ("sole writer of ... the rail/refusal/advisory strings
wherever they are authored") and its Fence section (naming two specific files off-limits) describe
overlapping, narrowing scope for the SAME mission — a first read of File Ownership alone would
overclaim what was actually reachable. Only grepping the real source at context/understand time
surfaced how much the fence actually removed. Recorded as episode `epic-567-door_cmdr-c-001`.
