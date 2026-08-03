# The two-bin routing question — cluster A

**This is Tommy's call.** Both bins are argued below at equal weight. I have a lean and I
state it at the bottom, clearly labelled, after both cases — not woven through them.

## The cluster, restated in one sentence

Three episodes across two runs and two roles: **a written, secondhand claim about current
repo state was taken as a premise, was wrong, and only re-deriving it by command caught
it.**

- `issue-304-g3-001` — a handoff enumerated *the suites that pin this file*; the enumeration
  was under-inclusive, and two out-of-scope test files broke. The suite list stood in for
  "what actually references this string."
- `issue-304-g3-003` — a handoff asserted a prior gate had already made a textual change. It
  had not. Reading the current file would have *confirmed the false claim*; only
  `git log` + `git show` over the 8 commits that touched the file disproved it.
- `issue-309-002` — `docs/EPISODE_STORE.md` §1 carries a worked `git check-ignore`
  transcript claiming `.agent-work/` is ignored. True when written at #301; invalidated by
  #326. The plan's first draft inherited the false premise.

## The governing ruling

#302, verbatim: *"Machinize the mechanizable. We don't need stochastic reasoning for
predictable logic… these are aspirations."* The third-bin candidates were ruled **not
catastrophic**, not *un-mechanizable* — a distinction that matters here, because this
cluster is **partly** mechanizable and the split does not fall on a clean line.

---

## BIN 1 — MECHANIZE

**The change:** a checker that extracts fenced shell transcripts embedded in tracked docs —
blocks of the form `$ <command>` followed by an asserted result — re-runs each command, and
fails when the observed result diverges from the asserted one. Wire it into the suite.

**What it would actually have caught.** Exactly one of the three: `issue-309-002`.
`docs/EPISODE_STORE.md` §1 lines 27-29 are a literal machine-checkable transcript:

```
$ git check-ignore .agent-work/episodes/ ; echo $?     # 0  -> IGNORED
$ git ls-files .agent-work/ | wc -l                    # 0  -> nothing under it is in git
```

Both assertions are false at `4cec87a` (`git check-ignore .agent-work/` exits **1**;
`git ls-files .agent-work/` returns **1958**). A checker would have gone red the moment
#326 merged, months before a commander inherited the stale premise. This is #348, still
open and still stale in the tree today.

**The case for.** It is predictable logic and needs no stochastic reasoning — precisely
#302's trigger. It cannot be forgotten, cannot decay, and does not depend on any agent
reading any doctrine. It converts a class of doc staleness from "discovered by the next
agent it misleads" into "discovered by CI at merge time." It is small and its failure mode
is loud. And it removes a live defect that is *currently in the tree*.

**The case against, stated honestly.** It covers **1 of 3** cluster members. 001 and 003 are
not transcripts — an under-inclusive prose enumeration and a false "already done" assertion
have no machine-checkable form, because nothing marks which prose sentences are repo-state
claims. So bin 1 fixes the member that is cheapest to fix and leaves the two that cost real
rework. There is a genuine risk of the #327 shape here: the action is right, and declaring
the *class* closed on it would be wrong. It also creates a maintenance surface — a
transcript checker that must tolerate machine-specific output, or it becomes a flake.

---

## BIN 2 — INSTRUCT

**The change:** a doctrine line in `docs/agents/`, with a tripwire and a pre-registered
expected-improvement record. Substance: *a repo-state claim you did not derive this run is a
lead, not evidence. Before it becomes a premise, re-derive it with a command — and when the
question is about history ("was this already done?", "what references this?"), the command
must range over history or the corpus, not over the current file.*

**What it would have caught.** All three, in principle. Each episode's own
`proposed-remedy` is a variant of this sentence — 001 d2, 003 d2, 309-002 d2 independently
converged on it, which is real evidence that the instruction is the natural fix as judged by
the agents who were actually burned.

**The case for.** It matches the cluster's true shape. It also has the strongest empirical
track record of anything in this repo's learning loop:
`lesson:verify-launch-order-claims-against-code` states a narrower version of it for one
role and stands at **mentions 9, confirmed 6, last-confirmed 1 run ago** — the most-confirmed
entry in the bank, and never once disconfirmed. Graduating it to `docs/agents/` is not a new
aspiration; it is promoting a rule that has already earned its keep six times over, and
widening it from "verify your launch order" to "verify any inherited repo-state claim,"
which is what the three episodes actually show.

**The case against, stated honestly.** It is an instruction, and #302 is explicitly sceptical
of these: *"these are aspirations."* Nothing enforces it. An agent under context pressure
skips it and nothing goes red. Its own predecessor lesson has been confirmed 6 times, which
proves it keeps *holding* — but also proves the underlying failure keeps *recurring*, which
is not obviously a success story for instruction as a mechanism. And this repo has direct
measured evidence that prose anchoring is weak: `issue-304-g3-005` found that re-anchoring an
imperative to "before you open any source file" produced measured sensitivity **0/4** against
map-lateness. Doctrine text moved nothing that was measured.

---

## Where the bins are not actually exclusive

Bin 1 and bin 2 address different members. Landing both is coherent and neither blocks the
other. **But `decision:one-consolidation-not-many` binds this run to exactly one** — this
issue proves the loop, it does not clear the backlog. So the question is genuinely *which
one*, and the other becomes a filed follow-up rather than a silent drop.

## My lean, labelled as a lean

**Bin 2**, on the grounds that a consolidation should match the cluster it consolidates —
1-of-3 coverage is a different change that happens to be adjacent. I hold it weakly, and the
0/4 measured sensitivity finding is a real argument against my own lean that I have not
answered.

**The strongest argument against me**, stated so it is not buried: bin 1 is the only option
that produces something that *cannot be skipped*, and this epic's own evidence is that
unenforced prose does not move measured behaviour. A reasonable reading of #302 is that
"machinize the mechanizable" means take the mechanizable slice **whenever there is one**,
precisely because the aspirational half will otherwise absorb it and nothing will be
enforced.

## Tier, if bin 2 is chosen (sub-question)

`decision:tier-must-be-justified` — broader-than-audience is a defect. The cluster hit an
**implementer** (001, 003) and a **commander** (309-002). So:

- **not** the repo's auto-loaded `CLAUDE.md` — that tier is *every* agent touching the repo,
  and this is a rule for agents executing planned work, not for every reader;
- **not** a single role's skill — it demonstrably crosses two roles;
- **therefore** `docs/agents/`, at **both** `ORCHESTRATOR_CONTEXT.md` and `CREW_CONTEXT.md`.

Which means bin 2 requires **creating `docs/agents/CREW_CONTEXT.md`**, which this repo lacks
and f1Brainz has had for months. That is the "catching up to established practice" the
launch order describes, and it is a real (small) scope consequence of choosing bin 2.
