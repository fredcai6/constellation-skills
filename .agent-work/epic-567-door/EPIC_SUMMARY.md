# Epic #567 — the door is the interface. Summary for acceptance.

Three waves, eleven lanes, seven PRs merged this session. `origin/main` at **`a8f59c69`**.
Every figure below was measured, not recalled.

---

## Did it work

**Yes.** `git grep "CLI fallback"` over `skills/`, `specs/` and the tracked `.agent-work/templates/`
overlay returns **zero**, and a **718-line guard** fails if any of it returns.

The acceptance test that mattered was not a grep. Lane D1 instantiated a fresh spine and read what
a Commander is actually *handed*:

```
init     <engine>: False | CLI fallback: False | checklist_engine.py: False
plan     <engine>: False | CLI fallback: False | checklist_engine.py: False
archive  <engine>: False | CLI fallback: False | checklist_engine.py: False
```

And a cartographer dispatched *after* the sweep, which had never seen the epic, closed its report
with: *"no CLI fallback used or needed at any gate."*

**Suite: 3191 at epic start → 3418 now.** 227 net-new tests, from an epic whose subject was
removing a path.

## The finding that made it possible

`#559`'s text had been deleted twice and grown back twice, and nobody knew why. Lane D1 found it:

> `tests/test_mcp_adoption.py::TestTier1ImperativeFields::test_field_still_carries_cli_fallback`
> **asserted that each of 7 imperative fields still carried its exact CLI command line**, failing
> with *"the CLI door must stay, never be removed or discouraged."*

Every earlier sweep was reverted by a red suite telling the deleter it had broken a rule. **Nine**
assertions mandated it. The regrowth was a mechanism, not drift. It is now inverted, and the guard
generalizes an in-tree precedent that already quoted you — *"the agents should not know about the
CLI. period."*

## What shipped

| Wave | Lanes | Delivered |
|---|---|---|
| 1 | A B C G | `spine_bind`; ExternalBackend refuses a spineless success; Stop hook outranks the context advisory; `finish_work` + lease-release-on-archive |
| 2 | D1 D2 E F H | the complete sweep + the regrowth guard; workbench teaching half 289→124; door refusals captured as episode friction; two evidenced honest nulls |
| 3 | J K L | installer stops rewriting the calling repo; role×harness tier table with allowed sets and recorded reasons; **declared bookends**; a drift lint |

## The thing I would put in front of you first

**A run could delete the steps that make it finish.** Lane K measured it before changing anything:

```
$ amend --delta '{"ops":[{"op":"drop","id":"archive"},{"op":"drop","id":"feedback"},
                         {"op":"drop","id":"review"}]}'
amended: dropped archive, dropped feedback, dropped review
exit: 0
```

One unforced call, from a Commander standing at `execute`, deleting its own independent-review
step. `_floor()` froze only what had already been *started*, so the opening bookend was protected
by accident of status and the closing bookend by nothing at all. That is now refused — proven by
performing the deletion before the change and showing it refused after.

**Your instinct was right and the engine had half of it by accident.**

## Where I was wrong, and what corrected me

Six errors of mine are in the log. The pattern is one thing, not six: **I measured something real
and attached it to a mechanism I had not checked.**

- I said `spine_bind`'s refusal proved the CLI was still load-bearing. A door launched from the
  lane's own worktree binds that lane's spine; the case is solved by launch, not by bind.
- I said a launcher inherited your host model default. It **refuses** a tierless dispatch and has
  since an earlier issue. The escalation came from an unconstrained free-text field.
- I reported a lease lapse "seen on two spines". **There is no lease key** — it lives in
  `engine_session`, my probe read a field that has never existed, and the engine had already told
  me so in a message I quoted as proof of the opposite.
- I reported a lane as "gate 4 of 17" when 13 of 17 were done. You chose to stop it on my number;
  I caught it while executing your choice and put the real numbers back before touching anything.
- Three file fences drawn from the plan instead of measured from the tree. One would have failed
  D1's own guard on D1's own branch.

**Three lanes corrected me by reading code I had reasoned about.** D1 found the mandate, K found
the capability I called missing, J found the refusal I said was absent.

## Still open, deliberately

- **#634** — the crew half of "every planning role" (~one line in `generate_spine.py`), the
  `execute.json` migration (which carries a deadline: an Admiral can only reify its waves *before*
  `execute` starts), and that **the freeze protects a run's completion but not its acceptance** —
  the Commander's `archive` and the Explorer's `route` have no human-acceptance postcondition, so
  for those roles the sign-off gate still sits in the mutable middle.
- **#632** helper environment inheritance · **#636** the registry losing concurrent dispatches.
- **#442** and **#565** — both rest on premises this epic's measurements contradict. Yours to rule.
- **#613** deferred behind #615 · **#575** parked.

## Two things I need from you

**1. A corpus reinstall.** K's bookends and L's lint are **inert until the installed skills are
refreshed**. The lint names the gap precisely today:

```
repo=['closeout','init'] installed=[]   admiral
repo=['archive','init']  installed=[]   commander
repo=['init','route']    installed=[]   explorer
```

It is a deployment action on your machine and this session already reverted one installer-caused
change, so I have not done it. J's #619 fix is now on `main`, so it should be clean.

**2. Acceptance**, which is the last gate on the spine.

## One diagnosis worth carrying forward

Lane L proposed it and I think it is right: the self-waive refusal and the archive-move deadlock
are **one defect, not two**. A door binds one spine, at one path, under one identity, at process
start — and all three assumptions break the moment a run moves its own files or must act on
itself. Two lanes hit the self-action half this wave; L hit the moved-path half as well.
