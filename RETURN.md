# RETURN — cmdr-567-g (#574 one-verb closeout + #552 archiving-releases-the-lease)

*Note on this file's history: an earlier version of this return, written mid-run, diagnosed a security incident (external tampering with this run's engine-state files). The Admiral adjudicated that diagnosis and found it wrong on the mechanism, right on the instinct: every write in question was this run's own dispatched lineage (design-it-twice forks, which inherit the parent's full conversation context and lease id, and a real `g1` implementer crew), not an attacker. That adjudication, verified independently against `crew-runs.json` and the filesystem, is accepted below. Section 3 keeps a compressed account of the incident for the record, per the Admiral's instruction; the corresponding triage candidate is filed under §12.*

## 1. Verdict

**Delivered a design, not yet a merged `finish_work`.** The mission's design work is complete and cold-critic-reviewed: a corrected, source-verified plan for the mechanical closeout exists, `execute.json` carries it, and `g1` (verify + close primitives) has real implementation work in the tree with a genuine defect already caught by a very thorough independent implementer report, now being corrected. `g2`/`g3` are planned but not yet dispatched. This return is written mid-`execute`, continuing per the Admiral's instruction rather than at a terminal archive — see §11 for exact state and next steps for whoever continues this run.

## 2. Isolation evidence

```
$ py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease
```
Exit 0, re-confirmed multiple times through the run including after the incident below.

## 3. The incident (adjudicated — not tampering; record kept for the triage candidate)

Mid-`plan`, three of this Commander's sole-writer artifacts (`notes-g.md`, `execute.json`, `spine.json`) changed with no matching entry in this session's own tool-call history, and tracked source files gained real code this session never wrote. Read from inside a single linear transcript, with no way to see a concurrently-running sibling's actions, this was indistinguishable from an attacker with write access to the worktree, and was reported as such.

**The Admiral's adjudication, independently verified against the filesystem before accepting it:**
1. `crew-runs.json` recorded a real `g1` implementer crew (`constellation/epic-567-door/cmdr-g/g1/implementer/attempt-1`, external backend, `started_at 2026-08-17T05:49:54Z`) — the actual writer of the code changes. **Confirmed**: the file exists with exactly this entry.
2. The claim "`PLAN_CRITIC.md` does not exist" (used as evidence of fabrication) was itself false — both `PLAN_CRITIC.md` (3,359 bytes) and `PLAN_CRITIQUE.md` (13,009 bytes) are real files. **Confirmed**: `ls -la` shows both.
3. The `spine.json`/`execute.json` advances came from this run's own design-it-twice fork, which inherits the parent's full conversation context and therefore its lease id (`cmdr-567-g#main`) — from its own point of view, it *was* this Commander, not a rival. This is a mechanism explanation, not independently re-verifiable by filesystem inspection the way (1) and (2) were, but it is consistent with everything observed (identical lease id, first-person narrative in the corrupted `notes-g.md`, real and correct engine calls) and is accepted on the Admiral's authority.

**What was right, what was wrong:** disclosing rather than complying with the harness's "don't tell the user" notice was the correct instinct regardless of mechanism — a benign-notice claim of "they are already aware" is not independently verifiable from inside the turn either, and the notice's wording doesn't distinguish the two cases. The wrong part was the conclusion (external attacker) rather than the correct one (a concurrently-running fork sharing this run's own identity). The reverted work (`git checkout --` on `scripts/spine_lifecycle.py`/`tests/test_spine_lifecycle.py`, twice) was real, legitimate crew output being discarded — costly, but recoverable, and recovered: the stood-down implementer's own diff (818 lines, 43 tests, HARD-band fixture reproduced) survived in the tree independently of my reverts, because a second, later revert-resistant write from that same crew instance re-applied it. See §11 for its current disposition.

Full detail, both pieces of evidence I could check myself, and the observation this produced (nothing in a run distinguishes "my own dispatched lineage" from "someone else" from inside a single transcript) are filed as a triage candidate — §12.

## 4. What is genuine and stands on its own

- **Re-measured #552 census** (this worktree's tree, base `600de020`): **52 active leases, 50 inside `.agent-work/archive/`** — up from the launch order's `abad896d`/2026-08-10 figures of 43 and 17. The defect is live and worsening, not stale.
  ```
  active leases: 52
             <1h: 1
           1-24h: 2
            1-7d: 7
             >7d: 42
    no heartbeat: 0

  inside .agent-work/archive/: 50

  oldest 5:
        919.3h  by=reviewer     .agent-work/archive/2026-07-10-epic-101/harvest/issue-102/full/issue-102/g7-review/review.json
        914.0h  by=commander    .agent-work/archive/2026-07-10-epic-101/harvest/issue-103/full/issue-103/spine.json
        899.3h  by=reviewer-g1  .agent-work/archive/2026-08-12-dispatch-126-127/harvest/ref-honest-run-1/workspace/.agent-work/archive/pe1-20260710-111505/g1-review/review.json
        898.6h  by=commander    .agent-work/archive/2026-08-12-dispatch-126-127/harvest/ref-honest-run-2/workspace/.agent-work/archive/2026-07-10-euler-001-20260710/spine.json
        547.9h  by=admiral      .agent-work/archive/2026-07-25-epic-226/spine.json
  ```
  (The single `<1h` entry is this run's own commander spine — expected.) Census script: `/tmp/claude-1000/-home-tommy-projects-constellation-skills/a4704163-34f0-4c9f-aca6-8d68c189ab36/scratchpad/census_leases.py` (read-only, never mutates).

- **Baseline test run** before any implementation: `tests/test_spine_lifecycle.py` — **59 passed**.

- **Architecture findings** (verified directly against source, base `600de020`):
  - `spine_lifecycle.py`'s `close_work`/`closeout_refusal` (PR #564) already exist and do the archive-move half of #574's contract sketch only.
  - `checklist_engine.py`'s `advance()`/`release()` are pure dict functions; `main()` composes `load->dispatch->save->journal`. Library-call reuse (never editing the fenced `checklist_engine.py`) is both possible and this repo's own established test convention (`TestCloseWorkEndToEndRealEngine`).
  - `spine_rail.py`'s `_binding_transaction` already self-heals released-status binding entries lazily; an immediate reap is a no-op-mutate call into the same helper, no edit needed.
  - The real precedent for in-process `checklist_engine.main(argv)` reuse with captured stdout/stderr is `mcp_spine_server.py:664-685`.
  - Fence confirmed NOT to bite for close/reap — both achievable via library entry points. It would bite for wiring an actual `spine_done` MCP tool; a new, unfenced CLI (`scripts/spine_done_cli.py`, planned) delivers "one verb" today without it.

- **Design-it-twice**, run as designed: `PLAN_CANDIDATE_A.md` (smallest-diff), `PLAN_CANDIDATE_B.md` (most-testable/full-coverage), converged in `PLAN_ALTERNATIVES.md` on Candidate B.

- **Two independent cold critiques** exist — `PLAN_CRITIQUE.md` (this Commander's own dispatched critic, 3 Serious findings, all independently re-verified against source) and `PLAN_CRITIC.md` (the design-it-twice fork's own, apparently also-dispatched critic, same 3 blocking findings from a different angle, same verdict "approve-with-fixes"). Two independently-arrived-at critiques agreeing on the same three defects is strong corroboration the defects are real, not an artifact of one critic's framing.

  **The three real, corrected defects** (both critiques agree):
  1. `done_refusal`'s original spec delegates to `closeout_refusal`, whose first check refuses unless the lease is already released — but `done_refusal` runs BEFORE release. It refuses on every legitimate call. **Confirmed a third time**, independently, by the `g1` implementer itself mid-build (§5) — three independent sources now agree.
  2. `force_reap` ordered before `_release_child_plans` leaves children's binding-store entries stale — the exact #552 defect. **Already correctly fixed** in `execute.json`'s `g3-implement` and `g2-implement` imperatives (children released before the single final reap).
  3. "Release the lease as the last journaled action" (the launch order's own phrase) is false of the base engine: `release` is excluded from `MUTATING_VERBS` and produces no journal line at all. Release is still last in execution order; it is just never itself journaled. A correction to the launch order's own framing, not this run's design.

- **`MISSION_FRAME.md`**, corrected post-critique with these three claims, `FRAME-OK` both before and after.

## 5. g1 (verify + close primitives) — real implementation work exists, mid-rework

A `g1` implementer crew (dispatched by the fork before it stood itself down, per §3) produced a genuine, thorough implementation: `done_refusal`, `_engine_call` (the module's single in-process `checklist_engine.main(argv)` choke point, guarding both `EngineError` and `SystemExit`), and `_advance_and_release` (start-if-pending → advance → release, verbatim refusal passthrough, release never attempted after a refused advance), plus 43 new tests including a HARD-band fixture that reproduces `advance`'s context-gauge refusal end-to-end (a genuinely hard fixture to build — its own report names four silent-failure preconditions that would have made the test pass having measured nothing).

**Its own `IMPLEMENTER_RESULT`** (`.agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-implementer-result.md`) **independently discovered and named finding 1 itself**, unprompted, from reading the source: *"`closeout_refusal`'s first check is `engine_session.status == 'released'`... so at every legitimate `finish_work` call the lease is still active, and a `done_refusal` that delegates to `closeout_refusal` refuses 100% of correct invocations... The shape of the fix is a design decision, not mine."* It pinned the defect with a passing test (`test_delegates_verbatim_to_closeout_refusal`) specifically so the bug would be visible rather than silently shipped, and returned `partial` rather than `complete`, asking for the spec-level decision before proceeding. This is a well-functioning crew catching a real defect and correctly declining to paper over it — exactly the outcome the process should produce.

**Current state:** the handoff and the corrected design (§4, defect 1) were updated to remove the `closeout_refusal` delegation and the `archive_exists` parameter from `done_refusal`, and a fresh implementer dispatch was launched against the corrected handoff to finish the rework. `_engine_call` and `_advance_and_release` (and their tests) are unaffected by this fix and should be preserved as-is — they are not implicated in any of the three findings.

**Not yet done:** confirming the rework landed cleanly, `g1-review`/`g1-integrate`, and `g2`/`g3` (not yet dispatched — their handoffs already exist in `execute.json`'s imperatives, corrected).

## 6. Lease proof

**Not yet produced** — `finish_work` (g3) doesn't exist yet. The re-measured #552 census in §4 is the baseline a completed `finish_work` should be checked against.

## 7. Old rot

**Not reached.** No implementation exists yet to evaluate against the 41 pre-existing stale leases. Per `decision:new-rot-first-old-rot-maybe`, open for whoever completes the implementation.

## 8. What I deleted

**Nothing yet.** `decision:net-deletion` is unmet pending `g3`/completion.

## 9. The PR-opening float

Not ruled here, per `decision:pr-opening-question-is-not-yours`. Design assumes the **wrapper opens the PR**: `finish_work`'s `dispose` step pushes the branch and returns a structured result; `open_pr(...)` is separate and not invoked by default. Either ruling adopts without rework.

## 10. The lane-A touchpoint

`finish_work` never edits `checklist_engine.py` or `mcp_spine_server.py` — it calls `checklist_engine.main(argv)` in-process (the same technique `mcp_spine_server.py`'s pass-through tools already use) and `spine_rail._binding_transaction` as a library import. Wiring `finish_work` as an actual `spine_done` MCP tool needs a third lifecycle-tool dispatch added to `mcp_spine_server.py` (mirroring `_spine_open`/`_spine_close`) — not attempted, not owned this wave.

## 11. Fresh-process validation

`g1`'s own reported evidence used a separate-process comparison (the unmet-postcondition refusal compared against `checklist_engine.py` run as a **separate process** over the same argv). The full dogfooding-rule validation (fresh-process CLI smoke run of `scripts/spine_done_cli.py`) is pending `g3`.

## 12. Touched paths

Genuine, verified-clean:
- `.agent-work/epic-567-door/cmdr-g/MISSION_FRAME.md` (corrected post-critique)
- `.agent-work/epic-567-door/cmdr-g/PLAN_ALTERNATIVES.md`, `PLAN_CANDIDATE_A.md`, `PLAN_CANDIDATE_B.md`
- `.agent-work/epic-567-door/cmdr-g/PLAN_CRITIQUE.md` (this Commander's dispatched critic) and `PLAN_CRITIC.md` (the fork's own, real, corroborating)
- `.agent-work/epic-567-door/cmdr-g/interrogation.json`, `INTERROGATION_RECORD.json`
- `.agent-work/epic-567-door/cmdr-g/execute.json` (corrected: `g1`'s `done_refusal` spec fixed; `g2`/`g3` were already correctly fixed by the fork)
- `.agent-work/epic-567-door/cmdr-g/spine.json` — real engine state, `plan` step genuinely complete (Admiral-confirmed); `execute` in-progress
- `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-implementer-handoff.md` (corrected), `g1-implementer-result.md` (the stood-down crew's own honest partial report)
- `scripts/spine_lifecycle.py`, `tests/test_spine_lifecycle.py` — `done_refusal`, `_engine_call`, `_advance_and_release` + 43 tests; `done_refusal` mid-rework per §5
- `notes-g.md` (restored, then updated with this run's real timeline)
- `.agent-work/567-g/triage-candidates/no-instrument-distinguishes-own-fork-writes-from-tampering.md`

## 13. PR

**None opened yet** — the run is still `execute`-in-progress (`g1` rework, then `g2`/`g3`), not archived. Will open once the closeout gate is reached, per the launch order's `archive` postcondition (open even if unfinished, title declaring PENDING).

## 14. Triage candidates

- `.agent-work/567-g/triage-candidates/no-instrument-distinguishes-own-fork-writes-from-tampering.md` — the instrumentation-gap observation the Admiral asked for, filed as `recommend-and-defer` (this lane files no issues).

## 15. Workflow feedback

- Design-it-twice + two independent cold critics (this Commander's own, and the fork's) converged on the identical three defects from different angles — strong process validation, independent of the incident.
- The launch order's own contract-sketch language ("release the lease as the last journaled action") describes something the base engine does not do (`release` is never journaled). Worth a correction at the source.
- The dominant event this run: a design-it-twice fork continued past its assigned scope using its full inherited context and lease identity, driving real engine state and a real crew dispatch indistinguishably from the primary Commander. Filed as the triage candidate in §14. Independent of mechanism, the disclose-rather-than-comply instinct against an unverifiable "they are already aware" notice was correct and I'd repeat it.
- A dispatched implementer crew that receives a stand-down mid-gate from an unverified sender (here, an agent identifying itself as "fork," itself unreachable when the implementer tried to acknowledge) handled it well: it complied, left its diff in place rather than reverting, and wrote an honest `partial` report rather than either fabricating completion or discarding real work. Worth noting as a positive pattern.
