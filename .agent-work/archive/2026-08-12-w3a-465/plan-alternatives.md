# Plan alternatives — w3a-465

Three candidate designs for the same defect, each generated under a distinct constraint, then one
recommendation. Run before the plan froze.

## Candidate A — constraint: "add no machinery"

Delete `r6-fowler`'s `c1` postcondition and keep the Fowler rail as prose plus
`scripts/verify_fowler_pass.py` run by hand.

**Rejected on evidence, not taste.** `record(result="pass")` executes `command`-kind postconditions
(`scripts/checklist_engine.py:1887-1911`), so `c1` is the only thing that makes the Fowler rail
enforced rather than requested. Deleting it moves the invariant into the prose bin, which
`docs/agents/GLOSSARY.md`'s two-bin rule says enforces nothing. This is the "remove the placeholder"
exit the launch order offers, and the load-bearing question closes it.

## Candidate B — constraint: "change no engine code"

Keep the placeholder but reclassify it as an *instantiation-time* placeholder, like `<work-id>` on
line 2 of the same template. Rewrite the imperative to say: resolve the real record path when you
instantiate the survey, before you `claim` — never mid-run.

**Genuinely attractive and nearly taken.** It is entirely inside the reviewer skill, it keeps the
command check, and it matches how every other placeholder in the corpus is resolved.

**Rejected on the residual.** It has no answer for the reviewer who instantiates the survey with the
path wrong, or who has to move the record. At that point `record pass` fails on a check that is
wrong rather than on work that is undone, and the only exits are hand-editing the survey or throwing
away the run's state and re-instantiating. That is the same trap one step later. The engine already
has a name for "this check's text is wrong" — `retext-check` — and it is withheld from surveys for
no reason connected to surveys.

## Candidate C — constraint: "the imperative must name a verb that works" — RECOMMENDED

Lift `amend`'s existing `retext-check` op to survey checklists; keep `add`/`drop`/`rescope`
gated-only. That last part is a conservative CHOICE, not a type-level impossibility: `drop` on a
survey item is a coherent thing to want. It stays refused because nothing in this issue needs it. Name the verb in
`r6-fowler`'s imperative.

**Recommended.** It is not a new verb and not a new concept — it is one existing op's type guard,
which is currently a blanket `type != GATED` refusal at the top of `amend()` rather than a
considered per-op rule. It gives the imperative something true to say, it keeps the check enforced,
and it removes the incentive to hand-edit engine state. It also makes the interrogator's identical
`zc-consolidate` fix AVAILABLE without reaching across that fence -- available, not applied: that
defect persists until its own imperative changes.

## Untaken road, named

Adding a `{checklist_dir}` substitution to command-check text, so the shipped command could name the
record relative to the survey and carry no placeholder at all. It would kill this defect class
corpus-wide. Not taken -- and the cold critic corrected the reason. Substitution is ADDITIVE (no shipped check
text contains braces, so nothing existing changes meaning), whereas widening `amend`'s type guard is
a semantic widening of a shared verb. On blast radius the untaken road actually scores better. It
loses on a different axis: it does not fix the residual case where a path was right at instantiation
and became wrong mid-run, which is the case that drives an agent to hand-edit. Raised as a triage
candidate.
