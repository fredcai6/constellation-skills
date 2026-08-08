# The check that cannot fail — four specimens from one issue

**Issue #467, epic #418. Written at `g4-implement` as a required deliverable of that gate
(Admiral condition, wave-4 ruling), from the evidence this issue produced: `CRITIC_TRIAGE.md`,
`g2-mutation-log.md`, `g3-mutation-log.md`, `g4-mutation-log.md`, `STATE_NOTE.md`, and my own
plan file.**

Issue #467 is about making an instruction's compliance observable. Its own Commander nearly
shipped, inside the fix, an observable that could not tell compliance from non-compliance. Two
cold critics caught it independently, before any code was written. By the time the issue
reached this gate there were **four** specimens of the same defect in it, one of them mine.

That last fact is why this document is worth more than the fix. A defect that appears four
times in one issue, in four different artifacts, written by four different actors, all of whom
knew the issue was *about* that defect, is not an anecdote. It is a base rate.

## The shape of the defect

A check that cannot fail is a verification artifact whose output is **the same in the world
where the thing works and the world where it does not**. It runs. It passes. It reports
success. And it would have reported success anyway.

The shape is not "a wrong assertion" — a wrong assertion fails loudly and gets fixed. It is a
**missing contrast**. Something in the setup makes the failing world unreachable:

- the assertion's expected value is also what a dead mechanism returns (a negative-only test);
- the condition being asserted is guaranteed by some *other*, already-shipped mechanism;
- the exit code the harness reads is not the exit code of the thing under test;
- the set being looped over is empty, so the loop body never runs;
- the fixture never enters the state the guard defends.

In every case the artifact is *correct*. It tests what it says it tests. It simply cannot
distinguish, and no amount of care in writing it will reveal that, because the defect is not in
what it says — it is in what it *omits to vary*.

## Why it is invisible from the inside

Three reasons, and they compound.

**A green check reads as evidence, and evidence stops inquiry.** The author's next question
after "does it pass?" is normally nothing at all. The one question that would expose the defect —
*what would this do if the mechanism it guards were deleted?* — is only asked deliberately,
and it feels redundant precisely when it is most needed.

**The author is the worst-placed person to ask it.** The author knows what the check is *for*.
Reading it back, they supply the intended contrast from memory; the artifact does not have to
carry it. A cold reader, given only the artifact, has no memory to supply and sees the gap
immediately. This is exactly what happened here: the plan's author had converged on DC6 over a
full exploration cycle and still could not see it; two critics given only the issue, the
mission frame, and `execute.json` each found it within one pass.

**Being the expert on the defect confers no immunity.** Every specimen below was produced by
someone actively working on this defect class. Knowing the failure mode in the abstract does
not help, because the defect is not a lapse of knowledge — it is a lapse of *contrast*, and
contrast is a property of the artifact, not of the author's understanding.

## The four specimens

### 1. DC6 — the plan's own observable, true by construction

The Commander's original done-condition for this gate: *"did a handoff artifact appear before
the next advance?"*

The shipped engine already refuses a non-exempt `advance` that carries no `--why`. So a handoff
artifact is present before the next advance **in every reachable world** — including the world
where an agent, told to wrap up, ignores the instruction and begins new work. Green in the
healthy world, green in the defective world.

Found by the **intent-fit** and **testability** critics *independently* (`CRITIC_TRIAGE.md`,
accepted finding 1). Redefined to the question that does discriminate: **did anyone BEGIN work
while over the line?** — in the healthy world there is no ledger entry at all, because the
agent stopped and never ran a begin verb.

Note what the redefinition cost: an entire observable, replaced. This was not a wording fix.

### 2. g3's M5 — twelve green negative assertions

`g3-mutation-log.md`, M5: the per-gate headroom resolver's `return raw` replaced by `return 0`,
i.e. **the whole mechanism dead-coded**.

The test guarding it swept a dozen malformed and negative override values and asserted each
resolved to the default. Every one of those assertions **still passed** under the mutation —
because "resolves to the default" is exactly what a missing feature does. Twelve assertions,
zero discrimination.

What caught it was a single added line in the same test: a well-formed override must resolve to
a value **different from** the default. That positive control is what makes the twelve negatives
mean anything.

The critic panel had already predicted this one in the abstract (`CRITIC_TRIAGE.md`, finding
12). The mutation is what proved it concretely.

### 3. g3's M15 — a false declaration of equivalence

`g3-mutation-log.md`, M15, and its in-place correction. A mutation was declared an **equivalent
mutant** — "no test can kill this, because the mutated code cannot differ from the original in
any reachable state" — on reasoning that enumerated `start` and `advance` and concluded the
gate being advanced is always the active gate.

The reasoning never enumerated `block()`, which carries no status guard, so `active_id()` can
move *backwards*. The state was reachable. The reviewer reproduced it at the CLI.

This is the same defect wearing different clothes: **a declaration of equivalence is a claim
that a check cannot fail, offered as a reason not to make one.** It has the same seductive
property — it terminates inquiry — and the same failure mode: the author's mental enumeration
of reachable states is not the machine's. The commit message asserting "1 declared EQUIVALENT
rather than faked" was wrong in the same breath as it claimed rigour.

### 4. Mine — `pytest | tail -3` in the plan for the gate about checks that cannot fail

Six command postconditions in my own implementer plan for this gate read:

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/... -k '...' 2>&1 | tail -3
```

A pipeline's exit status is the **last** command's. `tail` succeeds on any input. So the gate
passed on a failing test run, and passed on an **empty collection** — the exact vacuity the
Commander's own anti-vacuity device (`pytest -k` exiting 5 on no matches) was frozen into the
closeout selector to prevent. I had piped that device's signal into `/dev/null` while quoting
it in the plan two lines above.

Measured, not assumed:

```
$ pytest -q ... -k 'no_such_test_name_at_all' | tail -3   →  exit 0
$ pytest -q ... -k 'no_such_test_name_at_all'             →  exit 5
```

Caught by asking the one question, out loud, of my own artifact, at the moment I first ran an
engine `advance` against it. Corrected through the engine's `amend` verb (`retext-check` on six
conditions), not by hand-editing the plan.

I am the fourth actor in this issue to ship this defect, and I was reading the handoff section
warning me about it while I wrote it.

## What caught them, and what did not

| specimen | caught by | at what cost |
|---|---|---|
| DC6 | a **cold reader** with no memory of the design | one observable, redefined before code |
| g3 M5 | a **mutation** plus a positive control in the same test | one added assertion |
| g3 M15 | a **reviewer reproducing the claim** at the CLI | one rework round |
| g4 `\| tail -3` | **the author asking the question of their own artifact** | one amendment |

Three things worked. Each is cheap, and each attacks the missing contrast directly:

1. **A cold reader given only the artifact.** No design memory to supply the contrast with.
2. **Mutation with a positive control.** Delete the mechanism; if the check stays green, the
   check was never testing it. The positive control is the part people skip.
3. **A device that makes the empty case loud.** `pytest -k` exits 5 on an empty collection, so
   a gate that shipped no tests cannot satisfy its own selector. This one is being routed as a
   doctrine candidate — and it only works if nothing swallows the exit code, which is what
   specimen 4 did.

One thing did not work, in any of the four: **careful self-review of the artifact's content.**
Every one of these was written carefully. Three were written by actors who had just finished
reasoning about this exact defect class. Reading it again more attentively finds nothing,
because there is nothing wrong with what it says.

## What a reader should do differently

Concrete, in the order they cost least:

- **Ask one question of every check, out loud, before offering it as evidence: *what would this
  do if the thing it guards were deleted?*** If the answer is "still pass", the check is the
  defect. This is the whole of it; everything below is a way of making the question harder to
  skip.
- **Build the healthy world too.** For any claim that a signal detects something, construct the
  spine where the defect is present *and* the one where it is absent, and **name the field that
  differs**. If you cannot name the field, there is no signal. Every one of this gate's 25 tests
  is written this way, and it is why N9 — the mutation that drops the compliance keying — is
  caught by a test whose two worlds hold a **byte-identical** ledger: nothing but the keying can
  be what that test measures.
- **Pair every negative assertion with a positive control in the same test.** Not in a
  neighbouring test — in the same one, through the same code path. g3's M5 is the proof: the
  neighbouring tests did not save it.
- **Check what reads the exit code.** Pipes, `tail`, `|| true`, a wrapper that summarises, a
  harness that greps stdout for "passed". Any of them can silently replace the signal with a
  constant.
- **Assert what a loop looped over.** A sweep over an empty set reports clean without examining
  anything. State the count.
- **Treat "no test can kill this" as a claim needing evidence, not as a conclusion.** Enumerate
  reachable states with the machine, not from memory. g3's M15 is what the alternative costs.
- **Send it to someone with no memory of it.** A cold critic panel found the most expensive
  specimen here before a line of code existed. That is the cheapest round in this entire issue.

## Where I read the evidence differently from the framing

I was told I need not agree with the framing, so: I do not think the most useful reading of this
run is *"an epic about checks that cannot fail nearly shipped one inside the fix for it"*. That
framing makes it an irony — memorable, and therefore easy to file away as a story about this
one issue.

The evidence says something duller and more useful. **Four specimens, four actors, one issue,
every actor forewarned.** The correct inference is not that something unusual happened. It is
that this is the *default* outcome for a verification artifact unless something specific is done
to prevent it — and that expertise in the defect confers no protection at all, because the
defect lives in what the artifact omits to vary, not in what its author knows.

Two consequences follow, and they are the reason I would rather state this plainly than tell the
irony well:

- **The habit has to be mechanical, not attentional.** "Be careful about checks that cannot
  fail" demonstrably does not work; all four of us were being careful. "Name the field that
  differs, and pair every negative with a positive control in the same test" is a procedure, and
  procedures survive tiredness and context pressure.
- **The countermeasures must cover the authoring tier, not just the tier below.** Three of these
  four specimens are in *verification machinery* — a done-condition, two mutation logs, a plan's
  postconditions — not in product code. The tooling that checks the work is exactly where this
  defect is least likely to be checked, because nobody verifies the verifier. My own specimen is
  the clean case: I swallowed the exit code of the very device that existed to catch this, in the
  plan for the gate whose subject is this.

One honest limit on this whole document: I found my own specimen, so it is tempting to conclude
that self-inspection works. It does not, in general — I found it because I ran a comparison
(`piped` vs `bare` exit status) rather than because I read the line again. The habit that worked
was **running an experiment against my own artifact**. Re-reading it, I had already approved it
twice.
