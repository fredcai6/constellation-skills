# Epic #567 — the door is the interface. Summary for acceptance.

**Superseded in part on 2026-08-17: a third wave is running.** After wave 2 closed, the human
overturned this document's central concession and added scope. What that changed is in
"Wave 3" below; everything above it still holds as the record of waves 1 and 2.

Three waves, eleven lanes. Figures are measured, not recalled; where a number is an estimate it
says so.

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

**Suite: 3191 at epic start → 3352 at wave-2 launch → 3374 after all five merges**, Linux, always
verified in a clean detached worktree, and `main` re-verified after every merge. 183 net-new tests,
from an epic whose subject was *removing* a path.

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

- ~~**The complete sweep has three honest exceptions**~~ — **WITHDRAWN.** I recorded those three
  sites as a documented limit. The human rejected that reading: *"we're trying to move down to a
  single access point for the door so any exception to that is a failure."* They are unfinished
  work, not a limit, and they are now **#634** and lane K. The measurement stands; the conclusion
  drawn from it did not.
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
  abandoned and retried. You caught it; no mechanism did. My first proposed fix — inherit the
  dispatcher's tier — **you rejected**, correctly: it would make Opus commanders dispatch Opus crews,
  laundering the escalation rather than removing it. `tc8` now records your design instead: a
  per-role default, an allowed set per role, and a recorded reason for any deviation.
- **Three fencing gaps of mine** — `episodes/`, `store_mentions.approved.txt`, and the
  `.agent-work/templates/` overlay — each a fence drawn from the plan instead of measured from the
  tree. The third would have failed D1's own guard on D1's own branch.
- **I reported D1 as "gate 4 of 17" when 13 of 17 were complete**, and you chose to stop and relaunch
  on that number. I caught it while executing your choice, corrected it, and put the real numbers
  back before touching anything. A progress number at the wrong altitude says the opposite of the
  truth.

## Closeout status

| Item | State |
|---|---|
| Episodes | **done** — 18 Admiral-level records applied through the sanctioned writer; all cleared the observation guard first time. The store already held 24 lane-written ones, and the two of mine that duplicated them were dropped and referenced instead |
| Repo hygiene | **done** — all 9 epic branches merged and **kept** (#412), all lane worktrees swept after a verified harvest, stray worktrees pruned, the peer session's untouched |
| Cartographer reconcile | running at Sonnet, bounded brief |
| Triage pairing | **indexed, not yet posted — see the ask below** |
| `collect_feedback.py` sweep | run, read-only, **10 uncollected findings surfaced**; not marked, deliberately |
| ADMIRAL_LOG archive | last action before the lease release |

## The one thing I need from you before posting

The candidate count grew **24 → 60** (lane D1 alone staged 19). Every one is a committed markdown
file on `main` with a full write-up, so **nothing is at risk** — the only question is how much gets
surfaced onto GitHub.

Posting one comment per candidate means **60 comments across ~12 issues**, which is the ballooning
your ruling exists to prevent wearing a different shape. So I grouped them: **one comment per target
issue**, each carrying every candidate paired to it with its path. That is **~14 comments**, and the
index is at `.agent-work/epic-567-door/CLOSEOUT_PAIRING_INDEX.md`.

**31 pair onto 14 open issues** — #559 ×6, #535 ×4, #544 ×4, #369 ×3, then #432, #561, #595, #613
×2 each, and #495, #522, #541, #565, #575, #615 ×1. **26 have no open issue that fits** and are
covered by episodes — mine plus the lanes' own. **2 need your decision**, **1 is resolved**.

Say the word and I post the 14. Or name a subset — several are individually worth more than the
rest (a real `install_constellation.py` run mutating the **calling** repo; skill prose naming
bundled scripts by repo-relative path across **91 sites in 27 files**; a headless `claude -p`
inheriting the launching lane's spine and Stop hook).

## The two that need your ruling, restated

1. **#442** — close as an evidenced honest null, or keep it open? Its premise did not reproduce on
   11 cold subjects across four framings.
2. **#565** — it calls a sentence false that this epic measured to be true. Close it as delivered
   with a correcting comment, or would you rather rule on the sentence first?

Plus **`wire finish_work as a spine_done MCP tool`**, whose parent #574 is closed, and which is
adjacent to the PR-opening question you reserved and no lane may settle.


---

# Wave 3 — added after wave 2 closed

The human added scope rather than accept the epic's concession: *"let's file it now and do it now."*

## What changed his mind, and mine

I had written the three unsweepable sites up as a documented limit of the door's isolation
property. His answer reframed it: an exception to the single access point is a **failure**, and two
doors would be an acceptable answer where a surviving CLI path for agents is not.

Then he asked the question that dismantled my framing of the problem: **"is the commander really
driving its crew's spine or is it just populating it?"** It populates. Every crew plan in this epic
was driven under the crew's **own** identity — 26 and 27 journal entries, never the Commander's. So
the gap was never about reaching another agent's work.

What is actually left is one file. A Commander's `execute.json` is the Commander's **own** work,
kept in a second file because a gated spine cannot grow, and driven off-door under an id each lane
invents (`commander-567-d1-execute` and `constellation/567-e/execute` — two lanes, two formats).

And both roles already have the shape he wants. Commander: frozen bookends around **one** middle
step. Admiral: `init · latitude · execute · closeout` — an entire nine-lane epic inside one gate.
**The structure is already right; the file boundary is wrong.**

## The three issues

| | |
|---|---|
| **#632** | A helper inherits its launcher's spine and Stop hook, so every dispatcher strips four variables by hand. Three lanes paid for this in two days. Filed, not in wave-3 scope. |
| **#633** | Crew model tier from a per-role, **per-harness** table with an allowed set and a recorded reason. **Lane J.** |
| **#619** | The installer writes a machine-probed interpreter into a tracked file, and a real install rewrites the *calling* repo's `.mcp.json` regardless of `--dest`. Pulled into scope so the tier item settles before the epic closes. **Lane J.** |
| **#634** | One spine per agent: frozen bookends, mutable middle, for every planning role. **Lane K.** |

## The filing bar, which is his and which I had wrong

Asked which of five findings to file, he gave the test instead of the answer: **file what costs
agents work repeatedly, not what is severe.** Re-scored against it, four of my five "criticals"
failed — the door dying on a non-`KeyError`, the fixed-temp-name atomic write, and the silent lease
lapse are risks with one debugging session between them. They became episodes. Only the inherited
environment passed, because three lanes had already paid for it.

## Wave 3 lanes

- **J** — Sonnet — #619 + #633. One idea in two files: a launcher must take declared defaults, not
  machine-local ones. Merges first.
- **K** — Opus — #634, design-it-twice, convergence human-only. Merges last, and carries a sharper
  self-hosting proof than wave 1 did, because it changes the rule the Admiral's own live spine runs
  under.

## One correction to my own record

I reopened `execute` rather than leave it complete, cascading closeout's four attestations back to
pending. The episodes and the cartographer reconcile stand; hygiene must genuinely re-run over new
branches and worktrees.

That reopen is also the clearest evidence for #634. **This run's own plan changed mid-flight, and
the only way the engine could express it was to unfreeze a frozen middle.**
