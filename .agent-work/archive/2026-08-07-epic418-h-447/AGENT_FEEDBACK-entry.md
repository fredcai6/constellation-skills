# This run's AGENT_FEEDBACK entry, extracted for Admiral harvest

The root .agent-work/AGENT_FEEDBACK.md is UNTRACKED as of 77e428d and dies with this
worktree by design (decision:untrack-do-not-delete). This is the entry it received, kept
here so the harvest does not depend on a file that is meant to disappear.

---

## 2026-08-07 - `epic418-h-447` (issue #447, epic-418 workstream H) - delegated Commander

**This is the last entry this file will receive from a Commander run.** #447 retires it. It is
appended here because this run's OWN spine predates its own rewiring, and its `feedback`/`archive`
gate reads THIS WORKTREE's copy - untracked at `77e428d`, alive on disk, dying with the worktree.
That is `decision:untrack-do-not-delete` working exactly as designed. This run's real record is
sixteen episodes under `episodes/active/issue-447-*.md`.

**What I refused, and why.** This step's imperative also instructed me to distill lessons into the
retired playbook via its delta writer. I did not. That writer is deleted from `scripts/`, and
writing to the playbook would have reproduced the exact defect this run exists to fix - two
Commanders wrote to the "retired" playbook three commits after #308's retirement landed. The
obligation was met through the machinery this run shipped instead:
`apply_episode_delta.py --store-root episodes`, gated by `verify_episode_captured.py`. I checked the
other half rather than assuming: the ripeness gate exits 0, "no ripe lesson awaiting apply-or-defer",
so nothing was left unpaid by the refusal.

**Followed closely:** the engine, gate by gate, with an implementer and an INDEPENDENT reviewer on
every one of six gates. Four reviews, all APPROVE, zero blockers. Every reviewer re-ran the evidence
rather than reading the transcript, and in three cases that is what found something.

**Improvised around:**
- The spine step above. Recorded as a refusal with a reason rather than silently skipped.
- Two engine `amend --op rescope` calls, both with authority and reason, rather than attesting
  statements I knew to be false: the live-lesson count 6 to 8 after `main` advanced while this run
  was down, and the `retired-name` approval census added to g5 without which the guard could never
  have gone green.
- `run_crew.py --backend external` for every dispatch, since there is no headless CLI at this tier.

**Ambiguous, missing, or contradictory:**
- **My own g4 handoff asked for a proof that cannot work.** I told the reviewer to verify
  writer-provenance by comparing blob OIDs against `HEAD`. New files have no `HEAD` blob, so the
  check is vacuous exactly where it is needed. The reviewer replaced it with a delta replay into a
  scratch store. -> disposition: `recorded as episode issue-447-014`
- **My line-ending guidance nearly caused a false BLOCK.** I warned that the grep-based check is
  unreliable here (it is), but the obvious Python alternative - worktree bytes against the git blob
  at the base revision - is also wrong: `.gitattributes` sets `text=auto`, so blobs are LF by design
  and all 23 changed files report as corrupted. -> disposition: `recorded as episode issue-447-015`
- **`docs/agents/engine-config.json` does not exist** though every checklist names it as `config_ref`,
  and the engine accepts the dangling reference silently, so every run is on defaults nobody chose.
  Raised independently by two crews from separate work areas. Fourth report. -> disposition:
  `filed as #462`
- **A survey has no verdict for "confirmed a real defect that is out of this gate's scope."** The g4
  reviewer had to record its largest finding as `pass`, because `fail` would have forced a BLOCK on
  something the gate neither introduced nor was permitted to fix. -> disposition: `filed as #465`
- **Reviewer `r6-fowler` ships a placeholder its own imperative orders you to fill, and no engine
  verb fills it.** Filling it in text mode silently rewrote all 371 CRLF endings in the engine's
  state file. -> disposition: `filed as #465`
- **Two crews reported the same proof-of-life gap:** the team roster listed the crew's own name as
  the Commander's, so there was no distinct parent to message without guessing. Both skipped it
  rather than message an unrelated agent. -> disposition: `recorded`

**What helped, and is worth keeping:**
- **The launch order's "Expected and NOT defects" block.** The g3 reviewer said so unprompted: being
  told the red guard was expected let it spend its effort on the intent question instead of
  re-litigating a known red. I put one in every reviewer handoff after that. -> disposition:
  `recorded`
- **Naming the gate's ONE load-bearing property at the top of each handoff**, and saying plainly that
  a mechanical check would not catch it. Every real find this run came from a reviewer reading for
  intent, not from a command.

**Improvement signals:**
- **A leak proof only proves the stream it leaked to.** The g2 implementer's red proof leaked to
  stdout only, so the stderr half of the assertion had never been shown able to fire until the
  reviewer leaked from a different call site. -> disposition: `recorded as episode issue-447-011`
- **A forced-colour environment silently converts killed mutants into HARNESS ERRORs.** Two agents,
  including the pre-crash session, reasoned from a failure count that was an artifact of their own
  terminal. Fail-loud not fail-green, but while red it masks real regressions in that file. ->
  disposition: `filed as #459, recorded as episode issue-447-012`
- **An approval census passes trivially by approving too much.** The property worth measuring is
  exact coverage in both directions - 53 approvals against 53 residual sites, zero dead, zero
  uncovered - which the g5 reviewer measured rather than assuming from a green exit. -> disposition:
  `recorded`
- **The guard caught its own author twice**: on itself at g1 review, and on my own one-column doc
  edit at g5 integrate. -> disposition: `recorded as episode issue-447-016`

**Crew Workflow Feedback harvested at each `gN-integrate`:** eighteen candidates collected in
`.agent-work/epic418-h-447/episode-candidates.md`, eight of them promoted to episodes
`issue-447-009` through `016` and the rest either filed as issues or routed to a home that is not
this log.

---
