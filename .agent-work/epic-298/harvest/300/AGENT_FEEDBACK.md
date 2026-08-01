## 2026-08-01 — issue-300 (epic-298, wave 0, delegated Commander)

**Run shape.** Delegated Commander under frozen `LAUNCH_ORDER-300.md`, worktree
`C:/Programs/constellation-skills-wt/298-300`, branch `epic-298/300`, base `b69e6c8`.
Spine driven init → context → understand → plan; **stopped at `execute`** on the launch order's own
named stop condition (the design-it-twice convergence choice is Tommy's, floated to the Admiral).

### What worked

- **Grep-before-plan paid off again, in a new way.** The order and the confirmed spec both call the
  spine's gate-note loading the "partially grounded" thing to extend. Checking first showed the
  grounding covers deterministic *selection* only; *assembly* does not exist at all. Planning an
  "extension" to a mechanism that was never there would have produced a gate with no target.
- **The 3-author interface panel converged independently on five things.** Three Opus authors under
  three different constraints, none seeing the others, each verified the same revision-identity
  answer (git blob OID of LF-normalised bytes) against live bytes including CRLF twins. That
  agreement is worth more than any single candidate's argument, and it let the comparison spend its
  attention on the one thing they genuinely disagreed about.
- **The comparison produced a defect none of the three candidates had alone.** Candidate A recorded a
  real blob OID for an untracked file; candidate C recorded `absent` for the same file. Both honest
  about their own environment, mutually contradictory — and a committed artifact built either way
  would false-FAIL its own drift check on the next machine. That is design-it-twice doing the thing
  it exists to do, and it would not have surfaced from any one candidate.
- **The mandatory cold plan critic caught two postconditions that passed at HEAD with nothing built.**
  Both reproduced by hand before acting. See the lessons delta.

**Friction / unclear**

- **Two harness refusals cost a dispatch round-trip each.** A delegated Commander runs as a teammate,
  and a teammate can spawn neither named subagents nor background ones — but `commander-core.md`
  instructs telling every background subagent to deliver via `SendMessage`, and the delegated skill
  instructs polling a crew's result artifact in a loop while waiting. Both are unfollowable at this
  tier. Filed as issue #316. Workaround: multiple *synchronous* `Agent` calls in one message do run
  concurrently, and the result-artifact file is a perfectly good delivery channel.
- **`py -m pytest` silently has no pytest on this host.** `py` resolves to a shim whose runtime lacks
  it; `python -m pytest` works. Six of the plan's command postconditions were unrunnable as first
  written. The repo's own docs carry both conventions, so there was no house style to lean on. This
  cost nothing only because the critic ran the strings; a frozen plan whose evidence commands were
  never executed once is a wish list, not a plan.
- **The engine does not pass `cwd=` to command postconditions** while `_git` does. Filed as #315.
- **`verify_worktree_isolation.py` printed nothing under PowerShell** and `$LASTEXITCODE` came back
  empty; the same command under the Bash tool printed `worktree OK` and exit 0. The mandatory first
  action of every delegated launch order is therefore silently uninformative in one of the two shells
  the platform offers. Not filed separately — it is a small instance of the general
  use-Bash-for-POSIX rule the launch order already states, but the *isolation check specifically*
  is the one command a Commander runs before it knows anything, and a blank result reads as failure.

### Feedback on the launch order itself

Unusually good. The `notes-300.md`-not-`findings-300.md` warning saved a guaranteed round-trip (the
`Write` guard does refuse "findings" basenames). The pre-rulings were graded, which made it
immediately clear which were mine to revise and which were not. The one thing I would add: the order
says the convergence float is "the expected mid-mission return", but the skill text says never to end
a turn with a spine step pending. Those read as contradictory until you notice the order is the
frozen principal and wins. One clause reconciling them would remove the hesitation.

### Addendum — the bash-negation wrapper is safe only when bound to the right subject

Recorded at the Admiral's request, because the nuance is not in the technique as documented.

`lesson:prove-command-fails-postcondition` introduced `! <command>` as the way to make "the guard
correctly fails" a mechanically re-verified engine check, and #311 is open to document it inline in
the plan template. Both are right. What neither says is that **the wrapper is not safe by itself —
it is safe when bound to the right subject.**

I wrote `! <probe> || <real command>`, intending "probe whether the test exists; if so, run it."
POSIX binds `!` to the pipeline, so it parses as `(! A) || B`: when the probe fails because nothing
is built yet, `! A` is true, `||` short-circuits, and the list exits 0 — which the engine records as
PASS. The condition whose entire purpose was "prove the guard fires on bad input" was satisfied by
never writing the guard. A cold critic caught it; I reproduced it verbatim before believing it.

The same run has a *correct* use for contrast — an invariant that no `.gitattributes` rule exempts a
path from LF normalisation — where the `!` wraps the grep that must find nothing, and where a
`test -f` guard is load-bearing because a missing file makes `grep` exit 2, which `!` flips to 0 and
the invariant goes vacuous the same way.

So the operative rule, which belongs beside the technique wherever it lands: **the `!` must wrap the
invocation that must fail, and nothing else — never a probe or a guard clause joined by `||`/`&&`.**
Where the failing behaviour can be asserted inside a test, prefer a plain positive command naming
that test: a missing file or missing test id exits 4, which correctly fails. Posted to #311 with
both examples, since a doc issue that shows only the success case does not teach the subtlety that
both of my cases turned on.

### Addendum — the rest of the run (3 rework rounds, 2 reviewer BLOCKs, a cold panel)

The entry above was written at the mid-mission return, before any code existed. What followed changed
what I would emphasise.

**The cold panel found what two reviewer rounds structurally could not.** Both reviewers were good —
one returned a correct BLOCK on a test that turned CI red on any clean checkout, which was invisible
locally because this worktree happened to contain the very artifact whose absence triggered it. But
neither could reach the defects the panel found, and the reason is not diligence: **a reviewer given
a handoff checks conformance to that handoff.** Nobody had written "prove this test can fail" into a
handoff, so nobody checked it, and the issue's single acceptance test spent two approved rounds
comparing the parent's re-encoding of two parsed objects rather than the bytes the two environments
actually wrote. The panel's method is what found it: 45 deliberate mutations in a sandbox worktree,
34 killed, **11 survivors** — and the survivors are the map of where the suite is blind. That is the
lesson I would most want to survive this run.

**Three of my own errors, since owning them is the point.** I inverted the lint's direction in the
handoff — propagated from a design-panel candidate's framing, which I had already flagged as an
inheritance hazard and then reproduced anyway. I wrote a `!`-negation postcondition that bound the
negation to a probe rather than the guard, so it passed with nothing built. And I put a gitignored
`.agent-work/` path into a committed docstring, which three critics independently flagged — in the
same run where I had been arguing that gitignored artifacts are fragile.

**What the launch order's structure bought, concretely.** Isolating the one contingent gate meant
Tommy's ruling cost a single `amend` verb rather than a replan. That was the cold plan critic's
finding, not my foresight — my original cut had the acceptance test sitting inside the gate the
ruling deleted.

**Friction worth fixing.** One verification command I wrote (`grep -rn "agent-work" … docs/CHECKLIST_SCHEMA.md`)
could not return nothing, because that file has pre-existing unrelated hits; the crew narrowed it and
flagged the discrepancy instead of deviating silently, which is exactly right and worth naming as
good crew behaviour rather than a defect. And the engine's `reopen` cascade-reset is correct but
expensive at closeout: reopening g1 reset five downstream gates whose work was untouched, costing a
re-drive of each.

**Crew-reported friction**

- **A handoff rule stated backwards costs a full rework round, and the crew cannot tell.** I specified the lint as catching "the declaration narrowing away from the prose". The predicate I also specified catches the opposite. The implementer built exactly what I asked, documented it in my words, and the inversion shipped into a committed design doc before a cold reviewer disproved it in one command. The crew had no way to catch this: it was conforming to the contract, and the contract was wrong.
- **My own verification command was unrunnable as written.** `grep -rn "agent-work" … docs/CHECKLIST_SCHEMA.md` cannot return nothing — that file carries pre-existing unrelated hits. The crew narrowed it to the two files the diff actually touched and flagged the discrepancy rather than deviating silently or widening scope to "fix" unrelated lines. That is the behaviour I want and it deserves naming as such.
- **Two false-greens the g1 crew caught in its own work, unprompted.** A clean checkout at `HEAD` does not contain uncommitted changes, so the determinism test would have compared two copies of *old* code and passed while proving nothing; and in a bare source checkout every declared row resolved to `rev: null`, making byte-identity trivially true. Both were self-reported, not extracted.
- **A crew correctly refused to gold-plate and flagged the remainder.** Told to fix the leading path boundary, the g3 crew fixed exactly that and reported the trailing half as still open rather than silently extending scope. I then scoped the extension in deliberately. The division of labour worked because the crew reported instead of guessing.

**Improvement signals**

- **Mutation testing should be the cold panel's default method for evidence-shaped gates.** 45 deliberate mutations, 34 killed, 11 survivors — and the survivors were a precise map of where the suite was blind, including both blocking defects. This is far more productive than reading the diff, and cheap: a throwaway `git worktree` sandbox and a loop.
- **Contract-bound review and no-contract review catch disjoint classes.** Two good reviewer rounds could not reach a defect in the acceptance test, because no handoff asked "can this test fail?". Worth making explicit in review-class doctrine: for a gate whose deliverable is *evidence*, the panel is not a deeper version of the same check, it is the only pass that interrogates the evidence's own validity.
- **Isolating a contingency to exactly one gate turns a human ruling into a one-verb change.** Tommy's ruling deleted a gate; because the cold plan critic had forced the acceptance test out of that gate first, the whole cost was a single `amend`. Worth doing deliberately whenever a plan carries a floated decision.
- **`reopen`'s cascade-reset is correct but expensive at closeout.** Reopening g1 reset five downstream gates whose work was untouched, each needing a re-drive with re-attested evidence. A "reset only what depends on this" mode, or a cheaper re-affirm path for gates whose artifacts are provably unchanged, would have saved a dozen engine calls.

**Improvement signals (second addendum — the doctrine-version gate)**

- **A gate imperative can blind the very test it names as its settle condition.** I graded the placement of a new field a guess and wrote the settle condition myself — *"if two checkouts at the same commit disagree on the field, it belongs in `/run`"* — then, in the same imperative, wrote *"both children are worktrees at the SAME commit and are equally dirty, so the field is identical across environments."* That second sentence is the assumption that makes the first unfalsifiable. The reviewer built the case I had excluded (dirt confined to a file no declaration names) and the field disagreed immediately. **When you name a settle experiment, check that the harness can actually reach the failing case** — otherwise the grade is theatre and the `@grade: guess` tag is worse than no tag, because it looks like the question was left open when it was quietly closed.
- **Appending a gate beats reopening one.** Tommy's ruling arrived after `execute` had closed. Adding `g5` via `amend` cost one new gate; reopening `g1` would have cascade-reset five reviewed gates. Same engine honesty, an order of magnitude less churn.
- **Three separate defects this run were "a test that cannot see what it was written for."** The `skipTest` that fired only on a clean checkout; the determinism test that re-encoded through the parent; and this one. That is a pattern, not three coincidences, and the thing that caught all three was the same move: **mutate the code and check the test goes red**. It is cheap and it should be the default proof that a new test is load-bearing, not an extra a critic applies afterwards.
