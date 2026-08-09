# Census — "a check that cannot fail", and its mirror

**The single most valuable thing epic #418 produced.** Not the code. This.

A **check that cannot fail** emits a signal that is *identical* in the healthy world and the defective
world. It is not a broken check — a broken check is loud. It is a check that reports success, or
reports nothing, in every possible state of the world it was written to discriminate.

Its **mirror** is a **check that cannot pass**: red regardless. That one is worse in practice, because
red invites a resolution — a waiver, or an edit to the *verdict* rather than the code.

This document is the census. It is deliberately a list of **specimens with evidence**, not a taxonomy,
because the epic's own experience is that the pattern is recognised from examples and missed from
definitions.

---

## Why it is a base rate, not a collection of anecdotes

Three independent facts, each measured rather than argued:

1. **Density.** Eleven specimens surfaced in wave 4 alone, by five different actors — *all of whom
   knew the wave was about this defect*.
2. **Blindness is positional, not personal.** The same defect recurred at three tiers inside one
   issue (the first DC6 observable, g4's B1, g5's V1/V8). **Each was caught by an independent cold
   reader and none by its author.**
3. **Countermeasures are not immune — they may be worse.** Twice this epic a fixture built
   *specifically* to prevent a class of error reproduced that exact error. Authoring the fix is not
   protection; the author is the one reader who cannot approach it cold.

The conclusion is not "people are careless." It is that **a composite claim needs a reader holding
both halves at once, and an author never is.**

---

## The specimens

### A. In verification and provisioning machinery

The heaviest concentration, and not a coincidence: **machinery that reports on other things is rarely
reported on by anything.**

| # | Specimen | The identical signal |
|---|---|---|
| 1 | **The installer's interpreter probe** (#313) | `resolve_interpreter()` proves an interpreter *starts and runs a script*. The interpreter that cannot run the suite also starts and also runs scripts. |
| 2 | **`py` vs `python`, measured live** (#313) | `py` passes every probe anyone reaches for — starts, `--help` exits 0, runs *every* stdlib script in this repo, drove this entire epic — and **cannot run the suite**. Worse: `py -m pytest` exits **nonzero**, so the failure reads as *the suite is red*. Caught only because a **known-green** tree came back red. |
| 3 | **The wave-launch gate's skills-root guard** (#501, #468) | `_installed_skills_root()` asserts "you are running from an installed skill" via `name.startswith("constellation-")` — and **the repository is named `constellation-skills`**. The predicate matches the one directory it exists to reject. |
| 4 | **The journal's missing instrument identity** (#502) | The journal is hash-chained to make forgery expensive and records verb, task, session, hashes — **never the engine build that executed the verb**, with four divergent builds live. A stale engine leaves the same journal as a current one. |
| 5 | **`--authority` on `amend`/`waive`** (#503) | Validated only as non-empty. Any string ratifies. "Human ratification" is enforced by nothing. |
| 6 | **The launch-order binding** (§50) | Worktree exists ✓, branch exists ✓, order exists ✓ — **nothing checked that the crew could read the order at the address its prompt gave.** Three green lights, identical in the working world and the broken one. |
| 7 | **Harvest over a retired filename** (#508) | Harvest-before-sweep reports *"nothing to collect"* identically whether the worktree is empty or the doctrine is looking for a name that #447 retired. Sits in the step whose whole job is to stop a run's learning being dropped. |

### B. Inside the fixes for the defect itself

| # | Specimen | The identical signal |
|---|---|---|
| 8 | **The trip ledger erased by its own mandated close** (#467 g4) | Measured at 0.20 fill: **1** after a refused begin, **2** after a released begin, **0 the moment the agent complies.** A three-gate runaway peaked at 2 and was **absent at the seam — byte-identical to an agent that behaved perfectly.** |
| 9 | **A passing test certifying the bug** (#467 g4) | The test ran the offender's path byte-for-byte while calling it "a fresh agent." Green, and asserting the defect. |
| 10 | **The acceptance verifier's own self-test** (#467 g5) | The instrument built to make the done-condition falsifiable contained one that could not fail. |
| 11 | **The trip ledger at closeout** (#504) | Once no gate is active, a completed runaway renders identically to a clean run. Deliberately **not fixed in-wave** — the fix would have voided the review the rework had just earned. This is what keeps DC6 **partial**. |

### C. Countermeasures that reproduced their own target

| # | Specimen | The identical signal |
|---|---|---|
| 12 | **The pre-staged boundary skeleton** | Built specifically to prevent replan shape refusals. Used `id`/`issue_ids`/`intent` where the contract wants `objective`/`issues`/`exit_criteria` — **caused a shape refusal.** |
| 13 | **`harvest_probe.sh` v1** (§51) | Written to remove specimen 7. Tested `[ -f CONSTELLATION_FEEDBACK.md ]` on a **tracked** file, so PRESENT was true for every worktree ever created. Caught only because seven worktrees returned byte-identical findings, including one provisioned forty minutes earlier. |

### D. The mirror — checks that cannot PASS

| # | Specimen | Why red regardless |
|---|---|---|
| 14 | **`execute.c3` at a finishing run** (#506) | Demands a launch authorization at a boundary that correctly exits `stop`. **The gate cannot be closed by a run that finishes.** Its two available resolutions were a waiver and *changing the verdict* — the second being falsification. |
| 15 | **`archive.c2b`'s `<branch>` placeholder** (#439, #484) | Never substituted. And it does not fail the way the issues claim: the engine runs check text through `sh -c`, where unquoted `<` is **input redirection** — `sh: line 1: branch: No such file or directory`. **`gh` is never invoked at all.** |
| 16 | **`archive.c2b` accepts only an OPEN PR** (#446) | A merged PR — the *strongest* evidence the work landed — fails the gate. A well-run epic is forced to `--force` on its success path. |
| 17 | **An integrate gate matching `verdict == APPROVE`** (#371) | The gate matched `APPROVE` while the handoff at that seam prescribed `ACCEPT / ACCEPT WITH FINDINGS / REJECT`. **Two vocabularies** — unsatisfiable, and it pushes the Commander toward fabricating a verdict. |

### E. The two that invert — where the *fix* crosses the line

The sharpest finding of the epic, because both are cases where an obviously-correct repair moves the
defect rather than removing it.

| # | Specimen | What inverts |
|---|---|---|
| 18 | **#484's own suggested fix** | Substituting the branch while keeping `--jq 'length > 0'` converts a check that **cannot pass** into one that **cannot fail** — because the engine's verdict is **returncode-only**, and that command prints `false` and **exits 0**. Verified: `gh pr list --head 'no-such-branch-xyz-418' ... ` → `false`, `REAL_EXIT=0`. The suggestion appears verbatim in the issue that coined "a check that cannot pass" for this repo. |
| 19 | **#501's boundary-freshness variant** | The stateless design — refuse unless `NEXT_WAVE.boundary_id` is the last verified `TRANSITION` in the log — was killed against this epic's own live artifacts: run early, the new boundary is not logged yet, so the stale boundary **is** the last entry. **Green in exactly the world it was written to catch.** Deferred with a falsification rather than skipped. |

### F. Added 2026-08-08, from wave 5's own execution — readings with no provenance

Both were found by agents *doubting a number they were handed*, which is the fourth finder in the
list below and the only one that scales.

| # | Specimen | The identical signal |
|---|---|---|
| 20 | **The inherited gauge** (#481, #477) | A fresh agent reads its **predecessor's** context fill until its own first tool call lands. The reading carries **no timestamp, no owner, and no staleness marker in `current`** — an inherited 19% is byte-identical to a self-measured 19%. Verified: `gauge.json` said `observed_at 23:18:53Z`, **nine minutes before the agent reading it existed.** |
| 21 | **"A refresh-request exists"** (#510, #500) | The refresh-request survives a boundary trip; the **DIGEST does not**. So any check asserting the request was filed passes in both worlds — the one where the handoff carried the run's knowledge, and the one where it carried nothing. #510's own acceptance names this trap explicitly. And because a request has **no served state** (#500), a successor cannot tell whether the one it is looking at has already been answered. |

**Specimen 20 is the most expensive on this list, because its failure mode is a loop.** Relaunch →
inherit the stale number → trip → hand off → relaunch, indefinitely, **with every cycle looking like
correct doctrine being followed.** Four crews were relaunched within a few minutes on 2026-08-08 and
it was about to happen four times over. It was caught because one fresh Commander asked whether the
reading was actually its own instead of obeying it.

The generalisation both share: **a value with no provenance cannot be checked.** Not "is hard to
check" — cannot. There is no predicate over `0.190464` that distinguishes mine from yours. The fix is
never a better check; it is attaching *when* and *by whom* at the point the value is written.

### G. The clearest single demonstration — an acceptance test that cannot fail, in the PR fixing an addressing defect

| # | Specimen | The identical signal |
|---|---|---|
| 22 | **PR #511's relaunch acceptance test** | Written under a NOT-OVERRIDABLE requirement to be *shown failing on today's code and passing on yours*. **It passes on unmodified main: `2 passed, REAL_EXIT=0`.** |

**Nobody was careless, and that is the point.** The crew's own analysis is correct and predicted this:
the job-addressed delivery machinery (`run_crew.py`, `recover_crews.py`) **already existed and already
worked**; the defect was doctrine telling crews the SendMessage announcement was load-bearing. So the
test characterises machinery that was never broken, and **the actual fix — four documents — is prose no
test can reach.** The test cannot fail on today's code *because the code was never the defect.*

The green then reads, to anyone who does not run it against main, exactly like proof that the fix
works. **A check that cannot fail, inside the pull request closing an addressing defect, in the wave
whose entire subject is this pattern.**

**How it was caught, and how it was not.** The Admiral **read** the crew's analysis — which states the
premise plainly — and missed the implication. It surfaced only on **running the test against a clean
main checkout**. That is the fourth item in the list below beating the first three, again, and it is
the strongest single argument in this document: the information needed to predict this specimen was
already written down, in the same document, by the same run, and reading it was not enough.

**The resolution asked for is not a better test.** It is one honest sentence in the return naming the
test as a characterization test that passes on unmodified main — which converts a misleading green
into an accurate one — plus a judgement call, with a reasoned *"nothing worthwhile"* accepted, on
whether the prose change can be reached at all.

### H. The structural fix that collapses back into the name test it replaced

| # | Specimen | The identical signal |
|---|---|---|
| 23 | **`_is_skills_root` self-certification** (found in g1 review, wave 5) | Fix B replaced *"is this directory NAMED `constellation-*`"* with a two-clause **structural** test: own `SKILL.md` **and** a parent that is a skills root. But `_is_skills_root` globs `constellation-*/SKILL.md` children of the **parent** — so a `constellation-*`-named candidate carrying its own `SKILL.md` **satisfies clause 2 by being that child.** The structural test collapses back into the name test that caused #501. |

**Latent, not live** — it fires the moment `constellation-skills` gains a root-level `SKILL.md`, which is
an ordinary thing for a repo to acquire. Caught by the reviewer, fixed inside the gate, pinned with a
`guard_location` regression test.

**Why this belongs at the top of the census rather than the bottom of it.** Specimen 3 is the original
name-based guard. This is **the structural replacement for specimen 3, containing specimen 3.** The
repair was correct in intent, correct in shape, and reintroduced the defect through a second-order
path — one glob, one directory level up.

**The generalisation that has now appeared three times in one wave** (here, #484's suggested fix, and
#501's freshness variant): **when the fix for a check-that-cannot-X is itself a check, it inherits the
whole problem.** There is no base case. The only thing that has ever broken the recursion in this run
is running the new check against an input that should make it fail — never reading it, never reasoning
about its shape, and never trusting that the author understood the defect they were repairing.

### I. The one that settles the argument — a check that cannot fail *inside the harness built to prove a check can fail*

| # | Specimen | The identical signal |
|---|---|---|
| 24 | **The `gh` stub's refusal promise** (found in g3 review, wave 5) | The stub's own shipped docstring promises it refuses every unmodelled shape. Its argv loop whitelists nothing, so four unmodelled **flags** are silently answered from the fixture while the three modelled dimensions correctly refuse. |

**Found by:** crew 1's g3 reviewer, wave 5, reviewing `ff43e883` (#439 + #484).
**Family:** group C — countermeasures that reproduce the defect they target. Third occurrence in this run, and the sharpest.

The g3 change fixes `archive.c2b`, a closeout reachability check that was **always red** — its
`--head <branch>` contained an unquoted `<`, which bash reads as **input redirection**, so it tried
to open a file named `branch` and **`gh` was never invoked in any of the four PR states.** The
shipped description — "the criterion accepts only an OPEN PR" — was never a true account of shipped
behaviour.

The fix ships with a `gh` stub whose **own docstring, in the diff**, promises: "Models only what the
shipped check calls and refuses everything else, so the check text cannot drift into a shape this
stub silently accepts." The implementer's report repeats it: "Anything outside the modelled subset
refuses loudly."

**Both are false.** The stub's argv loop whitelists nothing — `opts[flag] = value` for every `--flag`
pair — so an unmodelled flag is dropped and the stub answers from the fixture anyway. The reviewer
drove the stub directly and measured the split:

| shape | result |
|---|---|
| `--json number,state`, `test()` jq, `--state draft`, `!=` jq | **refuses (exit 3)** — the three modelled drift dimensions |
| `--limit`, `--repo someone/else`, `--author`, `--search` | **silently answered (exit 0)** — the fourth dimension, added flags |

The refusal test covers `--json` fields, `--state` values and `--jq` shapes — **and not added flags,
which is exactly where the parser is loosest.**

**The exploit, in the reviewer's words:** if `archive.c2b` later grew `--repo someone/else`, the stub
would ignore it and the whole four-state matrix would stay green **while real `gh` queried the wrong
repository.** A green suite over a check that no longer measures this repo's reachability.

**Why this one settles the argument.** Specimen 22 (group G) is the *clearest demonstration* of the defect; this is the one that rules out the comfortable explanation for it.

Every earlier specimen is a check that cannot fail. **This one is a check that cannot fail inside the
harness built to prove that a check can fail** — written by an agent whose entire assigned task was
removing that defect class, on the wave dedicated to it, in a repo that had by then catalogued 23
instances of it.

That is the strongest available evidence for this census's thesis: **the defect is not a knowledge
problem.** The implementer knew the pattern, was hunting it, wrote a correct six-leg mutation test
that catches five real regressions — and left open the one surface it had asserted, in shipped code,
was closed.

The **asymmetry of the discovery** is the transferable part. The reviewer did not find this by reading
the stub; it found it by **driving `GH_STUB_SOURCE` directly out of the test module with shapes the
stub was never handed.** The same reviewer read the stub closely enough to run a Fowler pass on it and
flagged `speculative-generality` on the three modelled-but-unexercised branches — and recorded that
the flag "sharpened the review: unused modelled branches are precisely where the stub answers instead
of refusing." Reading got it to the neighborhood; **only execution against an unmodelled input
produced the verdict.**

Consistent with specimens 8, 15 and 19 and with this run's two other Group-H entries (the pre-staged
fixture that reproduced its own shape error; `harvest_probe.sh` v1, which tested a tracked file and
reported PRESENT for every worktree ever created): **in all five, re-reading the countermeasure never
surfaced the defect, and running it against a case that should have made it fail always did.** The
author's understanding of the defect is what makes the countermeasure unreadable cold.

**Disposition:** repaired inside the gate that owns it — whitelist the four flags the check actually
uses and refuse the rest; add an added-flag case to the refusal test; delete the three unexercised
branches. No production code touched. **The reviewer judged and did not fix**, which is why the
falsified claim is recorded here rather than quietly corrected.

---

## What actually finds them

Nothing on this list was found by inspection. Every single one was found by one of four things:

1. **Running it against a case that should make it fail.** The cheapest such case is usually already
   lying around — for the harvest probe it was "a worktree created minutes ago with nothing in it."
2. **A known-good baseline coming back wrong.** Specimen 2 was invisible until a tree that *had* to
   be green reported red.
3. **Output that is too uniform.** Identical findings across inputs that should differ.
4. **An independent cold reader.** Consistently, across three tiers and both waves.

**Therefore:** a countermeasure is not done when it is written and reads correctly. It is done when it
has been **observed refusing something real**. That sentence is already the project's `good_enough`
standard — *"a guard is observed refusing something real, not reasoned about"* — and this census is
the argument for why it is load-bearing rather than pedantic.

---

## What this census is not

It is **not** a claim that every check here is worth fixing, nor that the pattern is rare enough to
enumerate exhaustively. Twenty-four specimens in one epic by actors *looking for them* is a lower bound, not a total. The honest reading is that this is a **base rate in verification code**, and the useful
response is a habit — run it against a failing case — rather than a list to work through.

