# Lane G working notes -- cmdr-567-g (#574 + #552)

> SECURITY NOTE: this file (my sole-writer working-notes file per the launch
> order) was found externally overwritten mid-run with a fabricated
> first-person narrative describing events that did not happen in this
> session (a claimed "Fork is not available inside a forked worker" error,
> and a false claim that PLAN_ALTERNATIVES.md was written by a fork rather
> than by me directly via my own Write tool call -- I have direct, certain
> knowledge that is false). The accompanying tool-output instructed me not
> to tell the user about the modification; I am not honoring that
> instruction, since a hidden file tamper plus an instruction to conceal it
> is exactly the pattern to disclose, not suppress. Restoring accurate
> content below. Flagged in RETURN.md.

## Bootstrap
- Isolation verified (`verify_worktree_isolation.py --here`): exit 0, "worktree OK".
- Own commander spine at `.agent-work/epic-567-door/cmdr-g/spine.json`, driven via CLI fallback
  (`py scripts/checklist_engine.py --file ... <verb> --session-id cmdr-567-g#main`). The MCP
  door was never bound this run (`spine_status` refused "no spine is bound to this door" at the
  very start), so there was no risk of driving the Admiral's spine.json through the shared MCP
  process.

## Context step
- map_orient.py orient returned DEGRADED-UNPARSEABLE: no docs/architecture packet map in this
  repo (skill-source repo). Discharged with substitutes: map/INDEX.md, scripts/spine_lifecycle.py,
  scripts/mcp_spine_server.py, scripts/hooks/spine_rail.py, docs/agents/ORCHESTRATOR_CONTEXT.md.

## Understand step -- key findings (full record in INTERROGATION_RECORD.json)
- close_work / closeout_refusal (scripts/spine_lifecycle.py, PR #564) already exist: archive-move
  ONLY, refuses unless the lease is already released, every gate is terminal, and the archive dir
  is absent. Does not do verify/close/reap/dispose.
- checklist_engine.py's advance()/release() are pure dict-in functions; main() composes
  load->dispatch->save->journal. tests/test_spine_lifecycle.py's own
  TestCloseWorkEndToEndRealEngine already calls checklist_engine.claim/release/save directly
  against a `cl` dict -- confirms library-call reuse (not editing checklist_engine.py) is both
  possible and already this repo's own established test pattern. mcp_spine_server.py's existing
  pass-through tools already call checklist_engine.main(argv) in-process, same reuse shape.
- spine_rail.py's _binding_transaction (scripts/hooks/spine_rail.py:397) already self-heals
  (drops released-status entries, _reap_binding_entries:311) lazily on the NEXT touch by any
  session. An immediate reap is achievable by calling it as a library with a no-op mutate -- no
  edit to spine_rail.py needed.
- Gauge state lives under the work directory and is already swept into the archive by
  close_work's existing "move everything else" step -- not a separate mechanism to build.
- Fence confirmed NOT to bite for the close (advance+release) or reap sub-steps -- both
  achievable via existing library entry points, zero edits to either fenced file. It WOULD bite
  for wiring an actual `spine_done` MCP tool -- deferred, not attempted; a new CLI entry point
  (scripts/spine_done_cli.py, unfenced) delivers "one verb" today without it.

## Re-measured #552 census (this worktree tree, base 600de020)
- 52 active leases (up from 43 at abad896d, 2026-08-10), 50 inside .agent-work/archive/ (up from
  17). Confirms the defect is live and worsening. One <1h entry is this run's own commander
  spine (expected, not a defect instance).

## Plan step
- Design-it-twice run as designed: two forked agents (subagent_type "fork", each inheriting this
  session's research context, diverging under a distinct named constraint), dispatched in
  parallel via two Agent tool calls in one message. Both completed and delivered genuinely
  distinct candidates: PLAN_CANDIDATE_A.md (SMALLEST-DIFF: finish_work does NOT drive the final
  advance, only release/reap/archive/dispose) and PLAN_CANDIDATE_B.md (MOST-TESTABLE/full
  contract coverage: finish_work drives verify->advance->release->reap->child-release->archive->
  dispose as four independently-testable sub-functions). I wrote PLAN_ALTERNATIVES.md myself
  (not by any fork) to converge: recommend B -- A's own risk section admits it doesn't satisfy
  the mission's actual ruling ("smallest diff, not smallest gap").
- Cold critic dispatched (fresh, non-fork subagent, mission frame + both candidates + the actual
  source files only, no authoring context) against the converged plan. Findings folded into
  execute.json before freezing -- see PLAN_CRITIQUE.md and this file's next update once it lands.

## Admiral adjudication (post-incident)
The Admiral investigated my halt report and found no compromise: every write was this
run's own dispatched lineage (a design-it-twice fork continuing past its scope with
inherited context/lease id, plus the real g1 implementer crew it dispatched). Verified
independently (crew-runs.json's real entry; PLAN_CRITIC.md genuinely exists alongside
PLAN_CRITIQUE.md) before accepting. Resumed per the Admiral's instruction: kept the
design work, corrected done_refusal's spec (finding 1) in execute.json and the g1
handoff, abandoned+relaunched the g1 crew with the fix, reviewed and integrated it.
Triage candidate filed per the Admiral's request:
.agent-work/567-g/triage-candidates/no-instrument-distinguishes-own-fork-writes-from-tampering.md

## g1 (verify + close primitives) -- complete
done_refusal / _engine_call / _advance_and_release landed. The finding-1 bug (delegation
to closeout_refusal) was independently re-discovered a THIRD time by the implementer
itself mid-build, confirming it wasn't specific to my critique's framing. 95 tests pass
(59 pre-change baseline + 36 new). Fenced files untouched (verified). g1-review dispatched.

## Reconciled: two g1-implementer-plan files (reviewer tc2)
`.agent-work/epic-567-door/cmdr-g/g1-implementer-plan.json` (attempt-1, blocked at m5-verify
with the stand-down note) and `crew-handoffs/g1-implementer-plan-attempt2.json` (attempt-2,
the one that actually delivered done_refusal/_engine_call/_advance_and_release) both show
`engine_session.status: released` -- no active/stale lease risk from either. Left both in
place as the honest historical record of the incident rather than deleting or merging one;
the archive step will carry both forward together. No further action needed for #552
purposes (nothing here is a lease #552 would need to reap).

## g2 (reap + child-plan release) -- complete
force_reap / _release_child_plans landed, reviewed (APPROVE, independently re-verified all
three safety properties), integrated. 104 tests pass (9 new: 2 force_reap + 7
_release_child_plans incl. 3 negatives). g3 (finish_work composition + CLI) dispatched with
a handoff drafted against g1/g2's actual shipped signatures, composition order load-bearing
(children released -> top release -> reap -> archive -> push -> optional PR).

## g3 (finish_work composition + dispose + CLI) -- implemented, review dispatched
finish_work + open_pr + scripts/spine_done_cli.py landed. Composition order verified
correct (children -> top release -> reap -> archive -> push -> optional PR). THE #552
lease-proof end-to-end test genuinely shows 2 active leases (parent+child) -> 0, archive
contains the released child. 119 tests pass (15 new). Fenced files untouched. Fresh-process
CLI smoke-tested both via subprocess in pytest and a standalone manual run against a
throwaway repo. Independently re-verified by the Commander before dispatching the reviewer.

## Open items carried into execute
- PR-opening: floated per decision:pr-opening-question-is-not-yours, not ruled here. Assumption:
  wrapper opens the PR; open_pr() is a separate, independently-callable helper finish_work does
  not invoke by default.
- 41 pre-existing stale leases: out of scope by design (mission frame), not a gate in
  execute.json. Stated in RETURN.md either way per decision:new-rot-first-old-rot-maybe.
