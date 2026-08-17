# Review Result

## Assigned Gate
`g1` — `epic-567-door/cmdr-c`

## Result
`APPROVE`

## Handoff compliance
Full compliance. All 8 close criteria independently verified against the diff, not just the implementer's pasted evidence:

1. `_mid_flight_reason`'s returned string states the Stop hook is authoritative over the SOFT-band context-trip advisory — confirmed present in the diff.
2. The same string names `spine_halt block` as the sanctioned mid-run exit, replacing the vaguer "use the engine's block verb" phrasing — confirmed.
3. `crew-dispatch.md`'s existing `spine_halt block` guidance now also states the precedence explicitly — confirmed, new paragraph sits immediately after the existing guidance.
4. Net-deletion honored — the redundant "Keep working the gate -- do not end your turn to wait." and "do not just stop." were trimmed, not merely appended around; the result reads as one precedence statement plus one closing clause rather than three repetitions of "don't stop."
5. `scripts/checklist_engine.py` and `scripts/mcp_spine_server.py` untouched — confirmed by independently re-running `git diff --name-only` and `git status --porcelain`.
6. The Stop hook's trigger condition is unchanged — confirmed structurally: `git diff -U0 scripts/hooks/spine_rail.py` shows exactly one hunk, spanning lines 1491-1499, entirely inside `_mid_flight_reason`'s return string. `decide_stop` (line 1679), `load_nudges`/`save_nudges` (593/597), and the `count >= 3` branch (1736) fall outside that hunk, so they are byte-identical by construction, not merely by eyeballing.
7. `scripts/hooks/spine_rail.py` still parses — reproduced independently: `python3 -c "import ast; ast.parse(...)"` → `PARSE_OK`.
8. The new prose reads clearly to its actual cold-reader audience (an agent that already saw the SOFT-band advisory via `spine_status`/`current` before triggering this refusal) — no unintroduced jargon in that context.

## Scope drift
None. Only the two allowed files changed. Within `spine_rail.py`, the sole hunk is confined to `_mid_flight_reason`'s string literals; `_owning_session_reason` (line 1502) is untouched, consistent with the implementer's stated reason (it addresses a structurally different foreign-owned-gate scenario). Within `crew-dispatch.md`, the new paragraph sits inside the named section ("A harness-backgrounded command is never awaitable — do not park"), immediately adjacent to the existing `spine_halt block` guidance. No specific exclusion touched — `scripts/checklist_engine.py` and `scripts/mcp_spine_server.py` do not appear anywhere in the diff or status output.

## Evidence verdict
Satisfies the handoff's `evidence-only` test mode (prose/doctrine-only change, no test surface). All three evidence items reproduced independently and matched the implementer's pasted output exactly: `git diff --stat` (2 files, 9 insertions/4 deletions), `ast.parse` (PARSE_OK), `git status --porcelain` (only the two allowed files plus the expected untracked `.agent-work/` work area).

## Code/doc quality
Minimal, targeted change; matches surrounding style and existing message-formatting conventions (`.format(aid=aid, imp=imperative)` unchanged). Fowler refactoring pass run in full (`r6-fowler`, all 12 baseline smells visited, `verify_fowler_pass.py` exits 0): 11 absent, 1 flagged non-blocking — duplicated-code. The precedence sentence is now written out independently in both `_mid_flight_reason` (runtime refusal text) and `crew-dispatch.md` (read-ahead doc). Judged non-blocking: the two locations serve genuinely different audiences/moments and the task explicitly scoped both edits; flagged rather than overridden because no documented repo standard specifically sanctions duplicate precedence prose. Logged as a light triage candidate (`tc1`) rather than fixed silently.

## Map impact verdict
- **Evidence supports claimed change:** yes — diff, parse check, and status all confirm a string-literal/prose-only change.
- **Constraints not violated:** yes — `decision:trip-mechanic-untouched` and `decision:no-third-mechanism` both hold, verified structurally (no code path, flag, or state field added; the only diff hunk in `spine_rail.py` is inside `_mid_flight_reason`'s strings).
- **Notes match the diff:** yes — the implementer's Map Impact notes (structural anchors, no new capability, no new decision surfaced) match what the diff actually touched.
- **Decision candidates surfaced:** none needed — both relevant decisions were already settled/human before this gate; the task only shipped them into text.
- **Durable context routed:** yes — the one out-of-scope observation (duplicated precedence prose) is routed as triage candidate `tc1`, not fixed silently or dropped.

## Reconciliation check
None. No packet map exists for this repo (context step returned DEGRADED-UNPARSEABLE, matching the handoff's own Map Confidence Flags note). The change adds no new callable symbol or code path, so nothing here needs Commander reconciliation against a structural baseline.

## Blockers
- none

## Out-of-scope observations
- Triage candidate `tc1` (recorded in the survey's `triage_candidates`): the Stop-hook-authoritative-over-advisory precedence statement is now duplicated in full across `spine_rail.py` and `crew-dispatch.md`. Non-blocking today; worth considering a single source of truth if a third location ever needs the same sentence.

## Workflow Feedback

- **Handoff gaps:** none — the handoff named exact line ranges, exact functions, exact close criteria, and exact exclusions; every close criterion was independently checkable from the information given.
- **Context rediscovered:** none — the handoff's diff-inspection commands and Map Anchors were sufficient; no additional digging was needed beyond reading `decide_stop`'s full body to confirm the trigger-condition close criterion structurally (via hunk-boundary analysis) rather than by trusting the implementer's claim.
- **Instructions improvised around:** no `SPINE_FILE`/`SPINE_SESSION` was bound in this environment (dispatch note confirmed no such env vars were set), so per the constellation-reviewer skill's "nothing bound" path I authored my own `REVIEW_SURVEY.json` at the handoff's named `Survey State Location` rather than driving a pre-bound spine. The Fowler-pass template's postcondition command embeds a literal `<work-id>` placeholder inside its own imperative text; since the handoff's survey location (`g1-review/review.json`) does not match the template's default `.agent-work/<work-id>/…` convention exactly, I set the survey's `work_id` field to `epic-567-door/cmdr-c/g1-review` (matching the survey's own directory) and substituted that consistently everywhere `<work-id>` appeared, per the template's own instruction that this is "the same substitution you already make everywhere else in this survey" — not a deviation, just resolving an underspecified placeholder at authoring time.
- **What would have made this easier:** nothing concrete — this was a well-scoped, self-contained handoff with a small, mechanically-verifiable diff.

## Return status
`complete`
