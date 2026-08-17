# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` (work-id `567-d2`)

## Result
`BLOCK`

## Handoff compliance
The change applies `.agent-work/567-d2/g1-target-content.md` byte-for-byte to the three
workbench files and makes exactly the one-paragraph `CREW_CONTEXT.md` edit — independently
re-verified by programmatic string-equality of each extracted target block against the real
file, and by `git diff docs/agents/CREW_CONTEXT.md` showing a single hunk matching the
specified swap exactly.

All 5 mechanical Close Criteria pass, independently reproduced:
- 3 full-replacement files byte-exact against `g1-target-content.md` — confirmed.
- `CREW_CONTEXT.md` diff is exactly the one named paragraph — confirmed.
- `py -m pytest tests/test_mcp_adoption.py tests/test_commander_evidence_convention.py tests/test_install_constellation.py -q`
  is green: `388 passed, 2 skipped, 506 subtests passed` — reproduced myself in-context (not
  copied from the implementer's or Commander's report).
- `git diff --name-only` shows exactly the 4 allowed files — confirmed.
- `grep -c "Nothing here removes or discourages the CLI." skills/workbench/references/checklist-engine.md`
  is exactly 1 — confirmed.

**But a Stop Condition is tripped.** The handoff's Constraints section names `## MCP door` and
`## Session lease` (checklist-engine.md) "especially" as sections that "must be byte-identical
to the pre-change file," and its Stop Conditions section says BLOCK if "any retained section is
not byte-identical to the original." I diffed both sections mechanically (`git show
HEAD:skills/workbench/references/checklist-engine.md` vs. the working-tree file, exact string
comparison):

- `## MCP door` — byte-identical. Confirmed, matches the Stop Conditions' explicit named check.
- `## Session lease` — **not** byte-identical. Pre-change: 5 bullets, 2255 chars. Post-change: 2
  bullets, 1336 chars. The `heartbeat` bullet and the "every mutating verb needs `--session-id`"
  bullet were deleted outright; the surviving "lease goes stale" bullet was itself shortened
  (dropped the self-heal clause and the "engine refuses it and tells it to claim" clause).

This is a **plan-level inconsistency, not an implementer defect**: `g1-target-content.md` itself
— the file both the implementer and I were told is the authoritative byte-for-byte spec —
already contains this shortened Session-lease text. The implementer applied it correctly.
`tests/test_mcp_adoption.py::test_lease_section_carries_door_equivalent` only asserts substring
presence of `claim`/`heartbeat`/`release`/`spine_lease`, not exact wording, so the suite stays
green despite the rewording — the test cannot catch what the handoff's prose constraint asks
for.

## Scope drift
None. `git status --porcelain` and `git diff --name-only` show exactly the 4 allowed files
changed; the only other status entry is the untracked `.agent-work/567-d2/` workflow-scratch
directory (this dispatch's own crew-work area). `git diff --stat -- skills/workbench/templates/`
is empty — no template moved, renamed, or edited.

## Evidence verdict
Required evidence is present and I reproduced all of it independently rather than trusting the
report: reran the 3-file pytest suite post-change myself (matches); `git stash`ed the 4-file
diff, reran the same suite pre-change (also `388 passed, 2 skipped, 506 subtests`, matching the
implementer's claimed baseline), then `git stash pop`ped and confirmed `git diff --stat` returned
to its pre-stash state; recomputed the byte-exact comparison of the 3 full-replacement files
against `g1-target-content.md` programmatically; recounted the sentinel grep. Test mode is
test-after/inspection (no new test surface), which is the correct mode for a docs/prose shrink.

## Code/doc quality
Docs-only diff (3 skill/reference markdown files, 1 doc paragraph). Ran the required Fowler
baseline pass over all 12 smells (`.agent-work/567-d2/FOWLER_PASS.json`,
`verify_fowler_pass.py` exits 0: `smells=12, flagged=[], overridden=['duplicated-code']`).
11 are absent (no code in a markdown-only diff). One is `overridden`: SKILL.md's new
"Checklist engine" pointer paragraph and checklist-engine.md's opening paragraph both describe
the MCP-door-vs-CLI-fallback choice — this is this repo's own documented
index/detail convention (SKILL.md as thin entry pointer, `references/` as the elaborated
version), not accidental duplication; logged with standard + reason in the record.

Otherwise the retained prose reads cleanly and the retirement preambles are transparent about
what was cut and why (issue #565) — except for the Session-lease gap named above, which is a
content-fidelity defect, not a style one.

## Map impact verdict
- **Evidence supports claimed change:** Yes, for the byte-exact/scope/test claims — independently
  reproduced above.
- **Constraints not violated:** Partially. "Templates untouched" holds. "Retained sections
  byte-identical (MCP door, Session lease)" does **not** hold for Session lease — see Handoff
  compliance above.
- **Notes match the diff:** The implementer's Map Impact notes describe the shrink accurately for
  what changed, but do not surface the Session-lease-not-byte-identical gap (their own
  verification checked "does output match target-content.md," which target-content.md itself
  satisfies — the gap only shows up when you diff against the *pre-change file*, which is the
  handoff's stated bar, not the target-content spec's).
- **Decision candidates surfaced:** No — this gap needs a decision (restore the bullets verbatim,
  or relax the constraint) that neither the implementer nor the plan surfaced.
- **Durable context routed:** N/A — no separate architecture map exists in this repo
  (`docs/architecture/` not present) to route this into beyond this review result.

## Reconciliation check
Both named decision anchors from the handoff's Map Anchors are honored: "workbench stays a
template package" (templates/ untouched) and "partial not full deletion, settle: full suite
green post-change" (settled — full suite reproduced green both pre- and post-change,
independently).

The Session-lease gap above is a reconciliation item Commander must resolve: either (a) amend
`g1-target-content.md` to restore the 5 original Session-lease bullets verbatim and re-run
g1-implement, or (b) explicitly correct the handoff's "byte-identical ... especially Session
lease" constraint, since only that section's *substance* (claim/heartbeat/release/spine_lease)
is test-pinned, not its exact wording — unlike `## MCP door`, which genuinely is pinned verbatim
by `tests/test_mcp_adoption.py`.

## Blockers
- `g1-target-content.md`'s `checklist-engine.md` block does not preserve the `## Session lease`
  section byte-identical to the pre-change file (5 bullets/2255 chars → 2 bullets/1336 chars,
  with rewording even in the surviving bullets), contradicting the handoff's own explicit
  Constraints clause and its Stop Conditions clause ("BLOCK if any retained section is not
  byte-identical to the original"). This is a plan-level spec defect, not an implementer
  deviation — the implementer applied the spec correctly. Commander must reconcile the spec
  (restore verbatim text) or the constraint (state explicitly that Session lease's wording is not
  pinned, only its substance) before this gate can close as APPROVE.

## Out-of-scope observations
- None found beyond the blocker above, which is in-scope for this gate.

## Workflow Feedback

- **Handoff gaps:** The handoff's Constraints section states "`## MCP door` and `## Session
  lease` sections ... especially ... must be byte-identical to the pre-change file," but the
  target-content spec it points the implementer at does not actually preserve Session lease
  byte-identical. A reviewer who only checks "does the diff match target-content.md" (as the
  implementer's own verification did) will miss this — the check has to be "does target-content
  itself honor the constraint," which requires diffing against the *pre-change* file, not just
  the spec. Worth tightening: either the target-content file's preamble should say plainly which
  named sections are wording-pinned vs. substance-pinned, or the Constraints clause should drop
  "Session lease" if it was never meant to survive verbatim.
- **Context rediscovered:** None beyond the above — the handoff's Map Anchors and the target-content
  file were otherwise sufficient on their own.
- **Instructions improvised around:** No spine was bound for this reviewer role (the
  `SPINE_FILE`/`SPINE_SESSION` in this environment resolve to the parent Commander's own
  `constellation/567-d2/lane-d2/commander-delegated` execute spine, per this session's standing
  ruling that a crew's inherited `SPINE_*` env is the parent's, never the crew's own to drive) —
  so I built and drove my own `REVIEW_SURVEY` at `.agent-work/567-d2/g1-review/review.json` via
  the CLI fallback (`checklist_engine.py`) exactly as the task's fallback note anticipated. Two
  small CLI-surface mismatches versus the skill's prose examples, resolved by reading `--help`:
  `claim` takes `--claimed-by`, not `--role`; `record` takes the item id as a positional
  argument and `--result`/`--finding`, not `--task-id`; and survey checklists use `record`, not
  `advance` (which is gated-only and was refused with a clear message).
- **What would have made this easier:** Naming, in the target-content file's own header, which
  specific sub-sections of each "full replacement" file are wording-pinned by a named test vs.
  which are only presence/substance-pinned — this would have let both the implementer and
  Commander catch the Session-lease gap before dispatch instead of at review.

## Return status
`complete`
