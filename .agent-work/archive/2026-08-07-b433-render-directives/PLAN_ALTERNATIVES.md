# Design-it-twice — issue #433

Two candidate gate plans authored in parallel by cold agents, each under one named distinct constraint,
neither shown the other. Both read only the engine, the test class, the schema, and the live template
value. Panel-vs-single: **two candidates, not a panel.** The change lands in one function pair and one
test class; the load-bearing question is narrow (what shape must the completeness property take to be
falsifiable). That call is surfaced here rather than made silently.

## Candidate A — constraint: "minimal seam"

Push `directives` through the existing anchors normalizer; extend that normalizer to handle a dict
category value; keep the existing test class and edit it in place. Rendering comes out flat, with the
top key repeated per line:

```
directives:
  replan_input: template=../constellation-replan/templates/REPLAN_INPUT.template.json
  replan_input: evidence_fields=completed_outcomes, wave_evidence, discrepancies
```

Its strongest contribution is the red-proof set: four separate breaks (R1 renderer suppressed, R2 the
known trap restored, R3 a new unrendered field, R4 a field whose value flattens to nothing), each with a
predicted message. R4 is the one that matters — it is the case the current one-flag guard passes green.

## Candidate B — constraint: "falsifiable by construction"

A dedicated line formatter beside the anchors one; nested indentation; JSON spelling for scalars
(`false`, not `False`). The property is restructured around a per-field ledger and a total leaf
extractor, with a negative self-test in the suite and an optional arm driving the property over the live
shipped templates:

```
directives:
  replan_input:
    template: ../constellation-replan/templates/REPLAN_INPUT.template.json
    evidence_fields: completed_outcomes, wave_evidence, discrepancies
```

Its strongest contribution is naming why the extractor must **not** be shared between renderer and test:
a shared bug would render nothing and assert nothing, in agreement, and both sides would report green.

## Comparison

| axis | A (minimal seam) | B (falsifiable) |
|---|---|---|
| depth | one key buys the field; format borrowed | one key buys the field; format fits the shape |
| locality | highest — no new named surface | one new formatter, one new helper |
| seam placement | forces two different shapes through one normalizer | one adapter per shape |
| testability | equal on the red-proofs; weaker on vacuity detection | per-field ledger makes vacuity a typed failure |

## Convergence — one recommendation, not a menu

**Take B's rendering shape and B's property mechanism; take A's discipline about surface area and A's
red-proof set; decline B's full corpus-parametrized arm.**

- **Rendering: B.** Forcing a nested contract dict through the anchors normalizer would change that
  helper's contract for both callers and produce a line format that repeats the key. Anchors carries
  category-to-list-of-string; directives carries key-to-nested-dict. Two shapes, two adapters.
- **Property: B's per-field ledger, in A's existing class.** Both candidates independently concluded the
  ledger — not the flattener — is what closes the class. That agreement between two agents with no
  contact is the strongest evidence in this pass. No class restructure: the exclusion set and its stated
  per-entry reasons already exist and are the honest form.
- **Extractor: B's independence rule.** The test's leaf extractor stays separate from the renderer's.
- **Red-proofs: A's set, run for real.** R1/R2/R4 are the three that discriminate. Recorded with actual
  output, not predicted output.
- **Declined: B's parametrization over every shipped template.** Instead, one focused test renders the
  *actual* shipped commander spine `execute` gate and asserts its directive leaves appear. That buys the
  "the corpus's real shape is covered" property at a fraction of the coupling.

## Untaken roads

- **Deleting `directives` instead of rendering it.** The launch order sanctions this for a vestigial
  field. Declined on the measured inventory: three shipped templates carry it and a test asserts its
  parsed contract.
- **A full corpus-parametrized property arm.** Named above; declined for coupling, replaced by one
  focused real-template test.
- **A schema-to-renderer generator** (derive the rendered field set from the schema table). Not taken:
  it would make the schema document executable, a far larger interface change than this issue owns.
