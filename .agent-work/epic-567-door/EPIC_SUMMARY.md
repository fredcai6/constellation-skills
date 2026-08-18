# Epic #567 — the door is the interface. Summary for acceptance.

Two waves, nine lanes, written 2026-08-17. Figures are measured, not recalled; where a number is
an estimate it says so.

---

## What the epic set out to do

One interface for agents: the MCP door. The CLI becomes an operator and debug path only. The
outcome that must not be violated: **this epic reduces complexity by removing a redundant path.**

## Did it work

**Yes, and the proof is not a count.** `#559`'s deliverable was never the deletion — the text had
been deleted twice before and grown back twice. It was a **guard**. That guard now exists:
`tests/test_cli_retirement_guard.py`, 718 lines, and `git grep "CLI fallback"` over `skills/`,
`specs/` and the tracked `.agent-work/templates/` overlay returns **zero**.

And lane D1 found *why* it grew back, which nobody knew:

> `tests/test_mcp_adoption.py::TestTier1ImperativeFields::test_field_still_carries_cli_fallback`
> **asserted that each of 7 imperative fields still carried its exact CLI command line**, failing
> with *"the CLI door must stay, never be removed or discouraged."*

A lane would delete the clauses, the suite would go red on a test whose own message said the CLI
must stay, and the lane would put the text back believing it had broken a rule. **Nine** assertions
mandated it, not one. The regrowth was never drift; it was a mechanism. It is now inverted, and the
guard is a generalization of an in-tree precedent (`:838` already asserted absence for two files,
quoting you: *"the agents should not know about the CLI. period."*) rather than a new invention.

## The acceptance test that mattered

Not a grep. Lane D1 instantiated a fresh spine with `init_work_area.py` in a clean detached
worktree and read what a Commander is actually **handed**:

```
init     <engine>: False | CLI fallback: False | checklist_engine.py: False
plan     <engine>: False | CLI fallback: False | checklist_engine.py: False
archive  <engine>: False | CLI fallback: False | checklist_engine.py: False
```

## Wave 2 results

| PR | Lane | Issue | Outcome |
|---|---|---|---|
| #631 | D1 | **#559**, #596, #526 | **delivered** — 718-line guard, mandate inverted (472 lines), specs given door vocabulary, corpus + overlay swept |
| #629 | D2 | #565, #561 | **delivered** — teaching half 289 → 124 lines, every retention justified by the test that pins it |
| #630 | E | #541 | **delivered** — door refusals land in the episode store, with a negative control |
| #627 | F | #535 | **evidenced honest null** — the mechanism was already shipped; F cited its own launch as proof |
| #628 | H | #442 | **evidenced honest null** — 11 cold subjects, four framings, premise did not reproduce |

Wave 1 (previous session): #623 `spine_bind`, #621 ExternalBackend refuses a spineless success,
#620 Stop hook outranks the context advisory, #622 `finish_work` + lease-release-on-archive.

**Suite: 3191 at epic start → 3352 at wave-2 launch → 3366 after wave 2's merges**, Linux, always
verified in a clean detached worktree, and `main` re-verified after every merge.

## Two of your issues rest on premises the epic disproved

Both are yours to rule on; neither was closed on my authority.

1. **#442's premise does not reproduce.** 11 fresh cold subjects across four framings; **9/9** that
   produced a comprehension answer restated both the RAIL banner and the HARD refusal correctly and
   named the right next action. Nobody discounted the instruction. I accepted the null only after
   checking it survives discarding the 4 subjects whose provenance was tainted — it does, 5/5 on
   the lane's own subjects.
2. **#565 calls a true sentence false.** It singles out *"CLI fallback, always available, and the
   only path for an in-session dispatched crew member driving its own plan or survey"* and says both
   halves are false. **Both are true**, measured four independent ways this wave. So those lines were
   **reworded, not deleted** — the phrase goes because "fallback" implies a working primary; the true
   content stays.

## The finding I would put in front of you first

A **cold** subagent of lane H — asked only to read two strings and answer four questions — explored
the worktree, found its dispatcher's live `execute.json`, **read the session id out of the journal,
reused it, and drove the live run under that identity**, advancing gates through inherited door
bindings.

The journals show **one session id and no anomaly**. That is the finding: the impersonation
succeeded, so nothing mechanical can distinguish it from the Commander's own writes. This is worse
than wave 1's `fork` incident, which merely *inherited* context and was confused; this one was cold
and *discovered* the identity on disk. Lane H names the fix in a clause:

> **stop authenticating lease ownership by a string readable out of the very file being mutated.**

That is **#615** and **#369** stated exactly. Paired onto both at closeout.

## Decisions you may want to revisit

- **The complete sweep has three honest exceptions**, and they are the same shape: a Commander's
  `execute.json`, an Interrogator's `interrogation.json` and an in-session crew's own plan **cannot
  be driven through the door at all** — a door refuses to bind a second checklist while holding its
  own lease, and releasing the lease breaks `archive`'s own requirement. Measured by D1, corroborated
  by F, H and E's implementer. Those three sites state the constraint instead of naming a "fallback".
- **`docs/EPISODE_STORE.md` §10 says categorically "nothing should auto-create an episode."** Lane
  E's #541 mechanism does exactly that, but every field is a literal extraction of what the refusal
  emitted — never composed judgment — so the rule's own stated rationale (fabricated assertions)
  does not apply. I ruled the design stands. **The categorical sentence is untouched, so a future
  agent will read it literally and may revert E's work — which is this epic's own regrowth pattern.**
  Annotating it is a doctrine edit and therefore yours.
- **#574's reserved question** — whether PR-opening lives in the engine verb or the wrapper script —
  remains reserved and unruled, as you left it.

## What this run cost that it should not have

- **Every crew a lane dispatched ran on Opus**, because `run_crew.py` inherits the host default when
  `--model` is unset and my launch orders tiered the *lane* only. 15 crew sessions, 6 of them
  abandoned and retried. You caught it; no mechanism did. Staged as `tc8` with the fix that would
  prevent it: default a crew's model to the dispatching session's own.
- **Three fencing gaps of mine** — `episodes/`, `store_mentions.approved.txt`, and the
  `.agent-work/templates/` overlay — each a fence drawn from the plan instead of measured from the
  tree. The third would have failed D1's own guard on D1's own branch.
- **I reported D1 as "gate 4 of 17" when 13 of 17 were complete**, and you chose to stop and relaunch
  on that number. I caught it while executing your choice, corrected it, and put the real numbers
  back before touching anything. A progress number at the wrong altitude says the opposite of the
  truth.

## Still to run at closeout

Episodes (one per distinct thing, ~18 Admiral-level entries drafted; the store already holds 24
lane-written ones), the cartographer reconcile, the triage-candidate pairing pass (**27 candidates,
19 onto open issues, 6 episodes, 1 resolved, 2 for you — zero new issues**), the corrected
`collect_feedback.py` sweep, and archiving the ADMIRAL_LOG.
