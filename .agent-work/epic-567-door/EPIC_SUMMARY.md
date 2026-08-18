# Epic #567 — the door is the interface. Summary for acceptance.

Four waves, twelve lanes, eight PRs. `origin/main` at **`519226cc`**; the last gated tree is
**`c30ef5ae`**. Every figure below was measured, not recalled.

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

**Suite: 3191 at epic start → 3431 now.** 240 net-new tests, from an epic whose subject was
removing a path. Zero failures, in a clean detached worktree, map index included.

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
| 4 | N (M closed unsent) | the tier table's missing role declared and its provenance guarded, 313 lines |

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
- **#442** rests on a premise this epic's measurements contradict. Yours to rule.
- **#639** — the installer ships only skills, so the engine bundle rides inside a vestigial one.
- **#638** — the door binds one spine, at one path, under one identity, at process start. Three
  instances this epic: the self-waive refusal, the archive-move deadlock, and — sharpest — an
  **implementer has no spine at all**, so my own dispatch shape forced a CLI use inside the epic
  whose subject is removing the CLI.
- **#613** deferred behind #615 · **#575** parked.

## The cleanup wave, and what your reinstall caught

**The epic's own wave-3 deliverable blocked its closing dispatch.** The tier table refused
`commander-delegated` — the role every delegated Commander in this epic ran under. The refusal was
correct: it failed closed rather than guessing. What was wrong was the key set's provenance. Live
doctrine names **7** role terms; the table declared **6**, and the one it omitted was the one 10
registry entries used. I did not patch it myself, and I refused the other shortcut — relabeling the
blocked dispatch `implementer` to slip past the check would have written a false role onto a 10-gate
commander spine and fed the same wave's drift lint a lie. Lane N declared the key at your ruled tier
and wrote a guard that scans doctrine for **the property that matters** — a role doctrine hands a
model-tier-bearing dispatch artifact to — asserting `scanned ⊆ declared`, and proved it red on the
real bug rather than a fixture.

**Your reinstall order is the reason lane M did not ship a deletion that would have unwired your
Stop hook.** I wrote M's launch order from a census of the repo tree. The installed package is a
different object:

```
install_constellation.py:229   "workbench": ("checklist_engine.py", "gauge_writer_hook.py")
                        :848   HOOK_OWNER_SKILL = "workbench"
                        :929   hooks load from <target>/constellation-workbench/scripts/
~/.claude/settings.json        5 hook entries + 1 permission at that path
```

`skills/workbench` is the installer's **shipping unit for the checklist engine, the spine rail and
the gauge hook**. The skill is vestigial; the wrapper is load-bearing, because the installer can
only ship *skills* — a script bundle must wear a `SKILL.md` to be installable at all. **#565 closed**
on its real subject (the teaching, 289 → 124 → 20 lines). **#639 filed** for the package coupling,
to be done deliberately with its own `settings.json` migration path.

The reinstall also made two wave-3 deliverables real. The lint flipped from `repo=[...] installed=[]`
on all three roles to **`all 3 role spine template(s) declare bookends and match the installed
corpus`** — K's freeze and L's lint were **inert until deployed**, and the suite could not see it.

**I was wrong three times about the same six files.** I told you `DEFAULT.template.json` had zero
live referrers. It has two. My exclusion filter dropped `.agent-work/` to cut archive noise and took
the tracked overlay manifest out with it — the one referrer that decides the question. All six files
have live referrers. There was no deletion available at the cheap tier **at all**, which is what
closed lane M.

## What I need from you

**Acceptance** — the last gate on the spine. The reinstall is done and verified (20 skills,
`CORPUS.json sha256:106de882…`).

## One diagnosis worth carrying forward

Lane L proposed it and I think it is right: the self-waive refusal and the archive-move deadlock
are **one defect, not two**. A door binds one spine, at one path, under one identity, at process
start — and all three assumptions break the moment a run moves its own files or must act on
itself. Two lanes hit the self-action half this wave; L hit the moved-path half as well.
