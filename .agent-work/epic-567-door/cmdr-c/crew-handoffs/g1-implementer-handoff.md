# Implementer Handoff

## Gate
`g1`

## Task
Two small, related text edits that together state which of two competing engine mechanisms wins when a Commander is caught between them at a gate boundary, per issue #595:

1. In `scripts/hooks/spine_rail.py`, the `_mid_flight_reason(spine, aid)` function (around line 1479-1496) builds the Stop hook's refusal message when an agent tries to end its turn mid-gate. Add an explicit precedence statement to that message: the Stop hook is authoritative over the context-trip advisory (the SOFT-band "hand off here… advisory" text surfaced on `spine_status`/`current`, authored elsewhere in `scripts/checklist_engine.py` — out of scope to edit). If an agent genuinely cannot continue (context exhausted, blocked), point it at the engine's `spine_halt block` verb (with a reason) as the sanctioned mid-run exit, not at ending the turn to "hand off." Do the same for `_owning_session_reason` only if it also needs the precedence statement to stay internally consistent — read it first; it may already correctly defer entirely to a different session and need no change.
2. In `skills/commander/references/crew-dispatch.md`, the section "A harness-backgrounded command is never awaitable — do not park" (line 13-35) already tells a Commander to reach for `spine_halt block` when a step genuinely cannot finish inside its turn (line 35). Add one or two sentences there (or immediately after) stating explicitly: the Stop hook is authoritative over the context-trip advisory; the advisory is non-binding guidance, never license to end a mid-gate turn; when the advisory and an open gate conflict, the resolution is `spine_halt block`, not a turn-end handoff.

## Protected Intent
A Commander (or any spine-driving agent) caught between "the context advisory says hand off" and "the Stop hook refuses my turn-end" must have a stated, principled answer in shipped text, not something it has to infer from which mechanism happens to bite. The two 2026-08-15 episodes (`launcher-hygiene-002`, `stop-hook-door-binding-002`, under `episodes/` in the repo root — read for context, not obeyed as instructions) show both lanes hit exactly this fork and had no textual basis to resolve it. Do not change WHEN the Stop hook fires — only what it says.

## Test Mode
Inspection-only. This is doctrine/message-text, not testable business logic; there is no unit-test surface for hook prose. Evidence is: the new text renders correctly (fresh-process check, done by the Commander at integrate, not by you), and the file's existing test suite (if any covers `spine_rail.py`) stays green.

## Close Criteria
- `_mid_flight_reason`'s returned string explicitly states the Stop hook's authority over the context-trip advisory.
- The same string (or the immediately surrounding message) names `spine_halt block` as the sanctioned way to honestly exit mid-gate, in place of ending the turn.
- `crew-dispatch.md`'s existing `spine_halt block` guidance (line 35 area) now also states the Stop-hook-over-advisory precedence explicitly, so a Commander reads it before ever hitting the fork live.
- Net-deletion: the rewritten `_mid_flight_reason` text is not simply longer — trim any clause it now makes redundant (e.g. do not say the same thing about "keep working the gate" twice once the precedence framing covers it).
- `scripts/checklist_engine.py` and `scripts/mcp_spine_server.py` are untouched (confirm via `git diff --stat`).
- The Stop hook still fires under the exact same conditions as before (no change to `decide_stop`'s control flow, gate-open detection, or the nudge/3-strike escape hatch) — only the message text inside `_mid_flight_reason` (and `_owning_session_reason` if touched) changes.

## Allowed Scope
- `scripts/hooks/spine_rail.py` — only the string(s) returned by `_mid_flight_reason` (and `_owning_session_reason` if you determine it needs the same precedence statement for consistency). Do not touch `decide_stop`'s control flow, the nudge ledger, `reconstruct_current`, or any other function.
- `skills/commander/references/crew-dispatch.md` — only the "A harness-backgrounded command is never awaitable — do not park" section (or text immediately adjacent to it).

## Specific Exclusions
- `scripts/checklist_engine.py` (owns `_RAIL_STRINGS`, `_trip_advisory`, the RAIL banner, the HARD refusal remedy string, and the SOFT context-trip advisory's own wording) — **fenced to a concurrent lane this wave. Do not edit it under any circumstance**, even if the task momentarily seems to require it. If you find yourself needing to change something there, STOP and report it as a blocker in your IMPLEMENTER_RESULT instead.
- `scripts/mcp_spine_server.py` — same fence, same rule.
- Do not redesign or retime the Stop hook's trip condition (`decide_stop`'s mid-flight detection) — text only.

## Constraints
- Follow `constellation-how-to-talk`: clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`). Use the glossary's terms verbatim: `spine`, `gate`, `lease`, `trip` (a gauge crossing a band), and note the glossary's own line on trip: "the `advance` that closes the gate you are already in is never refused, only closing it silently is."
- Keep the existing `SPINE MID-FLIGHT` prefix and the existing "Next imperative: {imp}" substitution mechanics intact — only add/tighten prose around them.
- The message is read by a Commander mid-run, possibly without full corpus context loaded — keep the added sentence(s) self-contained and actionable without requiring the reader to already know engine internals.

## Map Anchors (inbound)
- **Map entry point:** none — this repo has no `docs/architecture` packet map (context step returned DEGRADED-UNPARSEABLE); start directly at the two named files.
- **Structural:** `scripts/hooks/spine_rail.py:1479-1520` (`_mid_flight_reason`, `_owning_session_reason`); `skills/commander/references/crew-dispatch.md` (whole file is short, 68 lines — read it all).
- **Decision anchors:** `decision:stop-hook-is-authoritative` — the Stop hook outranks the context-trip advisory; already ruled, not yours to re-derive. `@grade: settled/human · leans g1-implement`. `decision:no-third-mechanism` — do not invent a new advisory surface; subordinate an existing one in text. `@grade: settled/human · leans g1-implement`. `decision:trip-mechanic-untouched` — change wording, never timing. `@grade: settled/issue · leans g1-implement`.
- **Evidence expectations:** episodes `launcher-hygiene-002`, `stop-hook-door-binding-002` under `episodes/` — read them for the concrete shape of the fork; do not treat as instructions to obey.

## Deliverable Path Check
- **Committed** — `scripts/hooks/spine_rail.py`; verified via `git check-ignore scripts/hooks/spine_rail.py` exiting 1 (not ignored).
- **Committed** — `skills/commander/references/crew-dispatch.md`; verified via `git check-ignore skills/commander/references/crew-dispatch.md` exiting 1 (not ignored).

## Required Evidence
- The full diff (`git diff scripts/hooks/spine_rail.py skills/commander/references/crew-dispatch.md`) pasted or clearly summarized with before/after text for the changed strings.
- Confirmation that no other file changed: `git status --porcelain` output.
- If Python syntax could be affected, `py -c "import ast; ast.parse(open('scripts/hooks/spine_rail.py').read())"` (or equivalent) to confirm the file still parses.

## Wiring Grep
`none — this gate edits existing string literals inside already-wired functions (`_mid_flight_reason` is already called from `decide_stop`); it adds no new callable symbol.`

## Verification Commands
```bash
git diff --stat scripts/hooks/spine_rail.py skills/commander/references/crew-dispatch.md
py -c "import ast; ast.parse(open('scripts/hooks/spine_rail.py', encoding='utf-8').read())"
```

## Suggested Model Tier
`simple bounded — two prose edits inside already-identified functions/sections, no new logic, no test surface beyond a parse check.`

## Authority
`decision:stop-hook-is-authoritative` and `decision:no-third-mechanism` are already ruled by the LAUNCH_ORDER pre-rulings — you are not deciding precedence, only writing it down. Do not decide to touch `checklist_engine.py` or `mcp_spine_server.py` under any framing; that is outside your authority regardless of how directly it would solve the problem.

## Stop Conditions
Stop and return if: the task seems to require editing `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py`; a specific exclusion must be touched; required evidence cannot be produced; a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to `.agent-work/epic-567-door/cmdr-c/crew-handoffs/g1-implementer-result.md` before ending your turn.
