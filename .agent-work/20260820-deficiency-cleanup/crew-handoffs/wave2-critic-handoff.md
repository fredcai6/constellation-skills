# Cold critic handoff — architecture candidate comparison

You are a **cold critic**. You did not write any of these candidates and you owe
none of them anything. Your job is to help a human choose, and the most useful
thing you can do is find the flaw each author could not see in their own work.

## The success criterion — read this before anything else

The human who will act on your comparison has ruled:

> **There are no bad actors.** Nothing here defends against malice or
> impersonation. The only adversary is an honest agent about to make a mistake.
>
> **Ease of use for agents is the success criterion.** If a design makes the
> tools harder to use, it failed — whatever else it closes.
>
> **Added machinery is a COST, not a feature.** A new module, verb set,
> permission concept, or file to keep in sync is a debit the design must earn
> back in mistakes prevented.

All three candidates were written **before** this ruling and all three share an
authority/permission frame — grants, capability splits, supervise surfaces,
lineage edges. Score them against the corrected criterion, not the one they were
written for. Be fair about this: they were not told. Judge the design, not the
author's compliance with a rule that did not exist yet.

The central question for each entry is: **does an agent make fewer mistakes, and
are the tools easier to use?** A design that closes every issue while adding a
concept every future agent must learn may well lose to one that changes four
strings.

## The ballot — five entries, all scored

1. **Candidate A** — `architecture/candidate-A-duplicated-plan-state.md`
2. **Candidate B** — `architecture/candidate-B-missing-parent-authority.md`
3. **Candidate C** — `architecture/candidate-C-interaction-seam.md`
4. **Status quo** — change nothing. A real option. Say what it costs.
5. **Minimal intervention** — you construct this one.

### Constructing entry 5

Build the best design you can that uses **only** messages, defaults, and what the
system displays. No new module, no new verb set, no new permission concept, no
new file. Seeds from the evidence, which you should verify and extend:

- `require_session`'s refusal text (`scripts/checklist_engine.py:1148-1152`)
  recommends two remedies that are themselves filed defects (#632, #369).
- A stale lease presents as `status: active` to any reader. The reclaim
  mechanism already works and already records `previous_session_id` and
  `takeover_reason` automatically.
- The five-step waive handshake could plausibly collapse without new concepts.
- Ambient spine inheritance could fail closed by default with a message naming
  the correct action.

Score it honestly against the other four. If it loses, say why. If it wins, say
what it leaves unfixed and whether that matters.

## Required reading

- `evidence/LIVED-CLUSTER-EVIDENCE.md` — **read all of it, including the two
  Corrections and the threat-model section at the end.** The Admiral wrote two
  errors into E1 and E3 that the candidate lanes caught; the corrections are
  load-bearing and one of them inverts the finding.
- All three candidate files.
- `crew-handoffs/wave2-cartographer-result.md` for orientation.
- The six issues: `gh issue view 634 638 632 357 369 615` (read-only).

## Known biases in the evidence — account for these

- **Sampling bias.** All of this epic's Wave 2 dispatches went through the
  in-session Agent tool, not `run_crew --backend cli`. The two channels behave
  differently and only one was exercised. E1 and E2 are affected.
- **Privileged observer.** The reproductions come from an Admiral-driven run.
  An Admiral is the most privileged actor in the system and therefore the one
  most likely to notice missing authority. Frequency in the dossier is not
  importance.
- **Unresolved count discrepancy.** Lane B reported 39 active leases and "52 of
  56"; the Admiral independently measured 58 active, 54 archived. Same shape,
  different scan scope, unexplained. Note it; do not silently pick one.

## What each lane already conceded

Use these; do not rediscover them.

- **A** rejected its own seed after a falsification test, and volunteered that a
  design at roughly a tenth of its cost would probably beat it. Take that
  seriously — it is evidence for entry 5.
- **B** reported its seed survived only half, and that its design "buys nothing"
  on the dispatch path this epic actually used.
- **C** renamed half its seed and disputed E1's framing from source, correctly.

## Deliver

For each of the five entries: what it fixes, what it costs in machinery and in
learning burden, what it leaves open, where it is most likely wrong, and how it
scores on mistakes-prevented-per-unit-added-complexity.

Then: a ranked comparison, the single strongest argument **against** your own
top pick, and — most valuable — **what all five have in common that none of them
questions.** Three independent lanes converged on identity/naming as the
underlying defect; say whether that convergence is real insight or shared blind
spot.

A second design round follows you. Name the two or three questions that round
should be seeded with.

## Constraints

Artifact only. Do not choose for the human — rank and argue, but the decision is
theirs. No source, test, `map/`, or GitHub changes; `gh issue view` reads only.
Do not call any `mcp__spine__*` tool. Do not commit.

Write to `architecture/CRITIC_COMPARISON.md` in the main checkout.
