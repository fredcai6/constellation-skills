# #634 — design-it-twice comparison: how a plan declares its frozen bookends

**Convergence is the human's, not mine.** This is a comparison and one recommendation, per
`decision:design-it-twice`. Everything is pinned to `9b38b9d9`.

Three candidates were authored by **cold, independent Sonnet agents**, each given the same brief
and facts and **one distinct named constraint**, each told to attack itself. None saw the others.
Full texts: `.agent-work/567-k/crew-handoffs/design-{A,B,C}-result.md`.

| | **A — Positional** | **B — Per-gate flag** | **C — Mutable region** |
|---|---|---|---|
| Constraint | no new state | declare per gate | declare the window once |
| Declaration | none — `items[0]` and `items[-1]` are the bookends | `"bookend": true` on a task | `"mutable_region": {"after","before"}` top-level |
| Backward compatible | **No — by its own admission** | Yes | Yes |
| Protects spines already running | **Yes, immediately** | No — until retrofitted | No — and no retrofit path |
| Retrofit path through the engine | n/a | **Yes** — `rescope {bookend:true}` | **None** — would need hand-editing |
| Crew (`m0-context, m1`) | **Breaks it** — freezes `m1`, the real work | Opening bookend only | `before: null` — open finish |
| Failure mode when misdeclared | n/a | **silent-permissive** | loud (crash at first `amend`) |

> **Correction, found during implementation and confirmed independently at review.** Candidate B's
> written `_bookend_ceiling()` formula — `max(marked_indices) + 1` — is **off by one**. A bookend at
> the final index `n-1` yields `ceiling = n`, and an append computes `insert_at = n`, so
> `insert_at > ceiling` is `n > n`, false — the append is *allowed*, which is precisely the case
> B's own prose says must be refused. The shipped code uses `ceiling = max(bookends)` (the
> bookend's own index). **Do not copy the formula out of `design-B-result.md`.** The implementer
> caught it; the reviewer re-derived it without being told the answer.

## Where all three agree — treat this as settled

Independently, all three put the guard in the **same four places** in `amend()`: a ceiling on
`add`, and an identity/bounds check on `drop`, `rescope` and `retext-check`. All three leave
`_floor()` (`:3036`) doing its existing status job. All three need **no MCP door schema change** —
`spine_amend` already forwards the delta and returns `EngineError` through the existing channel,
so **`spine_amend` is confirmed as the seam.** All three leave `from_child` untouched.

**This is why the declaration form is a cheap, late decision.** The guard placement is common; the
candidates differ only in one helper that answers "is this gate frozen?". Swapping A for B for C
is roughly one function, not a rewrite. I state that as the reason the human can decide this
without holding up the mechanism.

Three findings were also reached independently by all three, which is what makes them worth
believing:

1. **`retext-check` is an escape hatch on check *text*.** A frozen gate's `command` check can be
   retexted to something trivially true and then passed, without any `drop`/`rescope`. (A#4, B#3,
   C#2.) A deliberately left it open, arguing a bookend whose typo'd check can never be corrected
   is worse. This is a real open question, not a bug any candidate closes.
2. **Hand-editing `spine.json` defeats every candidate.** `load()` is a bare `json.loads` and
   nothing cross-checks the file against the hash-chained journal. The refusal is scoped to the
   engine's verbs, never to the file. (B#2.)
3. **The `execute.json` migration is not funded by any candidate**, because it reaches into
   `run_crew.py` and `recover_crews.py`, which are **lane J's** and fenced from me.

## The one real disagreement, and the measurement that settles it

A and B contradicted each other on whether an Admiral's single `execute` gate can grow one gate
per wave. **I measured it rather than adjudicating between them**, on a copy of the live Admiral
spine:

```
REFUSED: drop execute: only a pending gate can be dropped (is 'in-progress')
Recovery: amend's drop only applies to a pending gate; execute is 'in-progress'
and no verb reaches a pending status from here
```

Neither was right. **The window to reify waves closes the moment `execute` starts.** An Admiral
that re-plans at `latitude` can decompose `execute` into `wave-1..wave-N` (B's path works there);
once it has started `execute`, no verb reaches back (A is right from that point on). The live
epic-567-door spine has `execute` in-progress, so **it can never be reified** — this epic's own
Admiral has already passed the door.

That answers the order's Local Unknown #3 with a measurement: waves *can* be spine gates, but only
if declared before `execute` starts. It is a doctrine choice with a deadline, not a free option.

## The trilemma the human actually has to resolve

The candidates do not differ mainly in elegance. They differ in **who gets protected and when**:

- **A protects every spine the instant it ships** — including the two live under this epic —
  because it needs no declaration. The price is that it **cannot be backward compatible**, and A
  says so plainly rather than pretending: with no declaration bit, there is no way to tell an
  opted-in plan from a legacy one, so `drop archive` starts refusing everywhere at once. A also
  **breaks the crew case**, freezing `m1` — the crew's only real work gate — which directly
  contradicts the human's "I wouldn't be mad at a crew updating its plan along the way."
- **B and C are both perfectly backward compatible and both protect nothing that already
  exists.** Their own self-attacks say this in almost identical words. The freeze arrives only
  when templates are updated *and* new spines are instantiated from them.

So it reads as: **immediate protection, or backward compatibility. Not both.**

### The cold critic dissolved that binary, and it was right

I put this comparison and the gate plan to a cold critic with no authoring context. Its strongest
finding is that the trilemma above is **false as I stated it**, and I am correcting it rather than
defending it. Two independent escapes, neither of which any of the three candidates or I saw:

1. **Backward-compatible is not the same as un-retrofitted.** B's engine-reachable retrofit
   (`rescope {bookend: true}`) can simply be *run once against every live spine as part of shipping
   the change*. "Backward compatible" describes the mechanism's **default reading of an undeclared
   plan**; it says nothing about whether you also choose to exercise the retrofit in the same
   release. That yields B's compatibility **and** A's immediate protection.
2. **The two bookends need not use the same strategy.** Every candidate's crew analysis shows the
   *opening* bookend is uncontested — nobody argues a crew should be free to reopen `m0-context`,
   and A's positional rule for `items[0]` breaks nothing there. All the per-role variance is about
   the *closing* bookend. So: **positional for the opening, declared for the closing.** Call it
   **candidate D**, credited to the critic. It is strictly more protection than B alone, with none
   of A's crew breakage.

**D is a real fourth option and the human should see it.** I am not converging on it — it arrived
after the panel and has had no self-attack pass of its own, which is exactly the scrutiny the other
three got and it has not. Its obvious untested risk is that two freeze rules in one engine is more
surface than one, and that the positional half re-imports A's backward-compatibility break for the
opening bookend specifically (small, since opening gates are non-pending by the time anyone amends —
but "small" is an assumption I did not measure).

**My recommendation stands at B, now with escape 1 attached**: ship B and run the retrofit over
live spines in the same change. That keeps one freeze rule, one declaration form, and still
protects what is already running.

## My recommendation: **B**, the per-gate `bookend` flag

Not because it is the prettiest — C's single `mutable_region` key matches the human's own
"bookends and a squishy middle" framing more directly, and I want that on the record as the
runner-up. B wins on one operational fact:

**B is the only candidate with a retrofit path that goes through the engine.** Adding `"bookend"`
to `rescope`'s `overwritable` tuple lets a live spine be frozen by one ordinary `amend` call —
and, because the guard sits *before* the overwrite, the flag becomes a **one-way latch**: once
set, every future `rescope` of that gate is refused, including one trying to unset it. C has no
verb that can write a top-level key, so retrofitting a running spine would mean hand-editing
`spine.json`, which this repo's doctrine forbids outright and which its own operational memory
records as having caused a lease deadlock. With two spines live under this epic right now, a
mechanism that cannot reach them is a mechanism that does not yet do its job.

B's real cost, which I am not hiding: **forgetting to declare fails silently in the permissive
direction**, and surfaces late, at some other gate, on some other day. C fails loudly instead.
The mitigation is a template lint rather than an engine change, and I have **not** built it — it
is staged as a triage candidate.

**What I would graft from the others:** C's insistence that an unresolvable declaration raise a
proper `EngineError` at first use rather than a bare `ValueError` — C found that defect in its own
design, and the same discipline applies to B's flag.

## What this comparison does not claim

- It does not settle the `retext-check` hatch. All three found it; none closes it. That is a
  genuine open decision, not an oversight I am papering over.
- It does not fund the `execute.json` → spine migration. That reaches `run_crew.py` and
  `recover_crews.py`, both **lane J's**, and the Commander/Admiral prose that names `execute.json`
  sits in **neither** my ownership list nor lane J's fence. **Floated to the Admiral as a scope
  question.**
- **It does not deliver the crew half, and that is a fence, not a choice.**
  `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` is not a `*SPINE*` template, so it
  is outside my ownership — and more decisively, it is **compiled** from
  `specs/implementer.spine.toml` by `scripts/generate_spine.py`, whose `_compile_gate`
  (`:669-684`) returns a **fixed field list with no `bookend` key**. A hand-added declaration would
  survive until the next regeneration and then vanish silently. **This repo has already had that
  exact incident** — `tests/test_generate_spine.py:1694-1700`, "the artifact diverged from its
  source", where an `amend` fix applied to a generated spine left the source spec stale and
  regenerating reproduced the break. `generate_spine.py` is in neither my ownership nor lane J's
  fence. So `decision:every-planning-role` is **satisfied for Admiral, Commander and Explorer and
  not for crew**, and the gap is one field in one unowned file. **Floated.**
- It does not deliver the "capture the plan changed, here's how" half. `amend`'s
  `cl["amendments"]` trail already records it and this run adds nothing to it; no role is newly
  told that `spine_amend` is how it re-plans its own middle (`grep -rn "amend" skills/implementer/`
  returns nothing). The critic caught me asserting that half solved by citation. It is not.
- It does not claim anyone has actually dropped a closing bookend in a real run. The probe proves
  the capability, not an incident. I did not search the journals.
- The three candidates are Sonnet-authored. I verified their central factual claims at source and
  measured the one place they disagreed; I did not re-verify every line citation in all three.
