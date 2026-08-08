# Problem statement — issue #433 (delegated, reconciled against LO-433)

No reachable human. The frozen launch order `.agent-work/epic-418-redux/launch-orders/LO-433.md` is the
ratified intent. This statement records where the order's assumed baseline and the actual code differ,
per the delegated `understand` obligation.

## The ask

A populated `directives` block must reach the agent through the engine's `current` projection, and the
class of unrendered-field defects must be closed by a completeness property rather than one more golden.

## Reconciliation — three departures from the order's assumed baseline

**1. The completeness property already exists. The order reads as if it does not.**
`tests/test_checklist_engine.py:3958` already carries `class TaskFieldCompleteness`, shipped by #420, and
`docs/CHECKLIST_SCHEMA.md:138` already documents it. What #420 did *not* do is include `directives`: the
field sits in `_EXCLUDED_FIELDS` (line 4004) under an explicit `KNOWN GAP` comment scoping #420 to
anchors + constraints. So the deliverable is not "write a property from scratch" — it is render the field
and pull it out of the exclusion set.

**2. Pulling `directives` out of the exclusion set alone would produce a check that cannot fail.**
This is the load-bearing finding. The property's `_flatten` helper handles `str`, `[str]`, and
`{category: [str] | str}` — the shapes *anchors* carries. It returns `[]` for anything else. Every
populated `directives` block in the corpus is a **dict whose values are nested dicts**
(`{"replan_input": {"template": ..., "evidence_fields": [...], ...}}`), so `_flatten` yields no strings
for it, the inner loop body never runs, and the property asserts **nothing** about `directives` while
reporting green. The test's own `checked_any` guard does not catch this: it is one flag for the whole
loop, so any other field yielding text satisfies it on behalf of a field yielding none.

Closing the *class* therefore means three things, not one:
- render `directives`;
- make the flattener reach the shapes the corpus really carries (nested containers, scalars);
- make the "did this actually check anything" guard **per-field**, so a field that flattens to nothing is
  a loud failure rather than a silent skip.

**3. The schema's type for `directives` is drifted.** `docs/CHECKLIST_SCHEMA.md`'s Task table declares
`[string] | null`. All 8 populated instances in the tree are dicts. The renderer must serve the corpus,
not the table; the table gets corrected at reconcile.

## Inventory verdict: render, do not delete

The order puts deletion on the table for a vestigial field. It is not vestigial — 3 shipped spine
templates (commander, admiral, explorer) carry it, every run instantiated from them carries it, and
`tests/test_iterative_planning_doctrine.py` asserts its parsed contract. Full evidence and the derived
counts are in `.agent-work/epic-418-redux/notes-433.md`.

## Protected intent

- `current`'s first line stays exactly `ACTIVE {id} [{status}] — {imperative}` (pinned by
  `GoldenOutputBriefing`).
- An absent/empty `directives` adds no output, exactly as `anchors`/`constraints` behave.
- `state()` stays pure — passthrough only, no check re-runs (INV-2).
- Assert against the projection's behaviour, never against prose describing it (LO pre-ruling
  `decision:assert-behaviour-not-text`).

## Out of scope

The seven other unrendered fields named in #420's revised spec stay excluded **with stated reasons** —
they are identity, bookkeeping, survey-only, or pointer fields, not narrative content. Their exclusion
is documented in the property's own docstring, which is the honest form: an exclusion set with a reason
per entry, not an unstated omission.
