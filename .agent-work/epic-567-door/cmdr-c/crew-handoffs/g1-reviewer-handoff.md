# Reviewer Handoff

## Gate
`g1`

## Survey State Location
Create your review survey checklist at `.agent-work/epic-567-door/cmdr-c/g1-review/review.json`.

## What Was Implemented
Two prose-only edits stating that the Stop hook (a mid-spine turn-end guard) is authoritative over the context-trip advisory (a SOFT-band, non-binding "hand off here" suggestion authored elsewhere), and naming the engine's `spine_halt block` verb as the sanctioned way to honestly exit mid-gate:
1. `scripts/hooks/spine_rail.py`, function `_mid_flight_reason` (~line 1479-1499): the Stop hook's refusal message now states the precedence and points at `spine_halt block`.
2. `skills/commander/references/crew-dispatch.md`, in the "A harness-backgrounded command is never awaitable — do not park" section (~line 34-36): two new sentences state the same precedence for a Commander reading the doc before hitting the fork live.

## How to Inspect the Diff
This worktree is `/home/tommy/projects/constellation-skills/.worktrees/567-c-rail-readability`. The change is an UNCOMMITTED working-tree diff. Run:
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-c-rail-readability
git status --porcelain
git diff scripts/hooks/spine_rail.py skills/commander/references/crew-dispatch.md
```
The lone untracked entry `.agent-work/epic-567-door/` is this Commander/crew run's own work area (handoffs, results, spine) — not a source-file scope violation.

## Task Statement
Per issue #595: two engine mechanisms (the Stop hook's mid-spine turn-end refusal, and a context-trip SOFT advisory recommending hand-off) tell an agent opposite things at a gate boundary, and nothing states which wins. The launch order's settled pre-ruling (`decision:stop-hook-is-authoritative`) already answers "the Stop hook wins" — the task was to make that stated and actionable in shipped text, and to point the honest mid-run exit at `spine_halt block` rather than at a turn-end handoff the Stop hook refuses. `scripts/checklist_engine.py` (which authors the advisory's own wording and the RAIL banner/HARD refusal text from a separate issue, #442) is fenced to a concurrent lane this wave and explicitly out of scope for this gate.

## Close Criteria
- `_mid_flight_reason`'s returned string explicitly states the Stop hook is authoritative over the context-trip advisory.
- The same string names `spine_halt block` as the sanctioned mid-run exit, replacing/superseding the vaguer prior "use the engine's block verb" phrasing.
- `crew-dispatch.md`'s existing `spine_halt block` guidance now also states the precedence explicitly.
- Net-deletion honored: the new `_mid_flight_reason` text does not just grow — check that redundant "don't stop" phrasing was trimmed, not merely appended around.
- `scripts/checklist_engine.py` and `scripts/mcp_spine_server.py` are untouched — verify by `git diff --name-only` (or `git status --porcelain`) showing only the two allowed files.
- The Stop hook's trigger condition is unchanged: `decide_stop`'s control flow, gate-open detection, and the nudge/3-strike escape hatch (`load_nudges`/`save_nudges`, the `count >= 3` branch) must be byte-identical to before — only the string(s) inside `_mid_flight_reason` changed. Diff the function boundaries carefully; a control-flow change here would violate `decision:trip-mechanic-untouched` even though the task is nominally "text only."
- `scripts/hooks/spine_rail.py` still parses as valid Python.
- The new prose reads clearly to a cold reader per `constellation-how-to-talk` (no jargon assumed without the corpus loaded, since this same hook module also feeds #442's cold-agent-readability concern even though #442's own target strings are out of reach this gate).

## Allowed Scope
`scripts/hooks/spine_rail.py` (string literals inside `_mid_flight_reason` only — and, if touched, `_owning_session_reason`, with a stated reason why) and `skills/commander/references/crew-dispatch.md` (the named section or immediately adjacent text).

## Specific Exclusions
`scripts/checklist_engine.py` and `scripts/mcp_spine_server.py` — fenced to a concurrent lane (Lane A) this wave. Flag as BLOCK if either appears in the diff at all, no exceptions.

## Constraints the Implementation Must Respect
- No change to WHEN the Stop hook fires (`decision:trip-mechanic-untouched`).
- No new advisory/precedence mechanism invented (`decision:no-third-mechanism`) — this gate subordinates one existing mechanism in text, it does not add a third.
- Glossary terms used correctly (`docs/agents/GLOSSARY.md`): `spine`, `gate`, `lease`, `trip`.

## Map Anchors (inbound)
- **Structural:** `scripts/hooks/spine_rail.py:1479-1499` (`_mid_flight_reason`); `skills/commander/references/crew-dispatch.md`.
- **Decision anchors:** `decision:stop-hook-is-authoritative @grade: settled/human · leans g1-implement`; `decision:no-third-mechanism @grade: settled/human · leans g1-implement`; `decision:trip-mechanic-untouched @grade: settled/issue · leans g1-implement`.
- **Map confidence flags:** none — no packet map exists for this repo (context step returned DEGRADED-UNPARSEABLE).

## Evidence Produced
See `.agent-work/epic-567-door/cmdr-c/crew-handoffs/g1-implementer-result.md` for the full IMPLEMENTER_RESULT: `git diff --stat` (2 files, 9 insertions/4 deletions), the full diff text, `git status --porcelain`, and a Python `ast.parse` confirming the file still parses. Target postcondition: `g1-integrate.c1` (fresh-process validation, done separately by the Commander) and `g1-integrate.c2` (your APPROVE verdict, matched via evidence_type `review-result`).

## Suggested Model Tier
`simple bounded — a small, fully-specified diff (11 changed lines total) against explicit close criteria; independent verification is mechanical (diff read + grep for excluded files + a parse check).`

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py` appear touched, the Stop hook's trigger/control-flow changed, or evidence is absent/unverifiable.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.

**Delivery.** Write the full `REVIEW_RESULT` to `.agent-work/epic-567-door/cmdr-c/crew-handoffs/g1-reviewer-result.md` before ending your turn.
