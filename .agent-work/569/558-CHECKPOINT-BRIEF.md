# #558 — brief for the human conversation before wave 3

Prepared by the Admiral during wave 1, per `decision:558-is-a-design-question`. This is not a
proposal to approve. It is the material needed to have the conversation efficiently at the wave-2
checkpoint, with the ground already measured.

## Why this was pulled out of commander dispatch

#558 asks *what question does each review level actually check*. It offers a table, not a decision.
Handing an open design question to a commander produces doctrine written by whoever drew the card —
and this epic's whole subject is doctrine that nobody adjudicated. It is also the only member issue
that would change how **every other** review in the corpus is judged, so getting it wrong is
expensive in a way the rest of the epic is not.

## The issue's own framing, verbatim

> A condition is met when its evidence is linked **and its required reviewers sign**. An
> implementation needs two: the cold review agent and the invoking agent. A review needs one: the
> invoking agent. The open design question is what each level actually checks — because if both read
> the same diff and say "looks right," that is one review counted twice, not two reviews. (Same
> defect family this epic has been killing: an enumeration mistaken for a property.)

| level | what it holds | the question only it can answer |
|---|---|---|
| **executor** | the code it just wrote | — produces the locator, never signs its own condition |
| **reviewer** (cold) | the diff + the condition text, no epic context | **Is the claim true?** |
| **invoker** (dispatcher) | the launch order + the epic intent | **Does the true claim mean we are done?** |

That cut — *is it true* vs *does it mean we're done* — is the strongest idea in the issue, and it is
worth preserving whatever else gets decided.

## What the corpus actually does today — measured

The gate that carries a reviewer verdict is `EXECUTE_PLAN.template.json`:

```json
{"id": "c1", "statement": "REVIEW_RESULT returned",
 "check": {"kind": "artifact", "evidence_type": "review-result"}}
{"id": "c2", "statement": "reviewer verdict is APPROVE",
 "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}}}
```

So today there is **one** signature — the cold reviewer's — expressed as a literal string match. The
invoking agent's sign-off does not exist as a condition anywhere. The "two reviewers for an
implementation" that #558 describes is **not** the current state; it is the proposal.

Note also that `c2` is the exact scalar match `w1-verdict` is changing this wave. The two issues touch
the same line, which is why they were originally paired — and why the pairing was a trap: one is a
type fix, the other is a doctrine decision.

## The two things #558 says must be settled

**1. The chain terminates at a human.** Verbatim:

> Admiral reviews Commander, Commander reviews Implementer — nobody reviews the Admiral's own
> conditions. In this run the human did, catching the wave-2 advance. Make that explicit in doctrine
> rather than leaving it implicit at the top of the tree.

Worth knowing: **this epic has already reproduced that pattern twice, in your favour.** Your commit
`244665ee` corrected an ordering defect in the commander plan step that no agent had caught, and it
also ruled against the `--report-only` reflex that I had just written into this epic's contract. The
top of the tree is being reviewed by you, in practice, right now. The question is whether that stays
informal.

**2. `n` is not a free integer.** Verbatim:

> A human-settable reviewer count gets set to 1 under budget pressure — which is precisely the
> force-through risk. Derive `n` from the condition's kind (implementation → 2, review → 1), declare
> it in the template at authoring time, and make lowering it an override that lands in the ledger.

**This one has a live tension with a decision you already made this epic.** You ruled sonnet for
every commander and crew slot, explicitly as a budget-shaped choice. #558's argument is that budget
pressure is exactly what corrupts reviewer counts. These are not in conflict yet — tier and count are
different dials — but if the wave-1 returns show sonnet reviewers are weaker, the pressure to
compensate by *adding* reviewers, or the temptation to cut them, is the same force #558 names.

## The questions I would actually put to you

1. **Does the invoker-signs level get built at all?** It does not exist today. Adding it is a real
   cost on every gate in the corpus, and this epic's stated goal is taking work *off* the agent's
   plate. The honest case against: one good cold review may beat two mediocre ones, and the
   "does this mean we're done" question is arguably the *dispatcher's job anyway*, not a new gate.
2. **If yes, is it a condition or a doctrine line?** A condition is enforceable and costs a gate. A
   doctrine line is free and enforces nothing — which is the defect this epic exists to kill, so
   choosing it here should be deliberate rather than default.
3. **Is `n` derived, and where does the override land?** #557's append-only ledger is wave 2's work
   and is the natural home. If #558 lands after #557, it gets the ledger for free.
4. **Does the human-at-the-top get written down?** This is the cheapest of the four and the one with
   live evidence behind it from this very epic.

## My recommendation, stated as a recommendation

Settle question 4 (write down that the chain terminates at a human) and question 3 (derive `n`, route
overrides to #557's ledger) — both are cheap and both have evidence. **Defer question 1** until the
declared-basis work from wave 2 has actually run, because if #556 makes conditions carry a resolvable
locator, the cold reviewer's job gets sharper and the marginal value of a second signature changes.
Deciding the reviewer-count question *before* measuring that is deciding it blind.

That would make #558 partially answered, cheaply, without dispatching a commander to invent doctrine.
