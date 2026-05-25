# Scout Heuristics

Map-first architecture audit. Read Cartographer artifacts first. Use code as pressure test.

## Loop

1. Load target packets/index/overlays/generated map.
2. Pick suspicious structural anchors.
3. Sample code/tests/config around each anchor.
4. Compare map claim, code shape, dependency direction, constraint anchors.
5. Rank candidates. Route future work to Triage.

## Signals

- Shallow structural node: interface nearly as complex as implementation.
- Pass-through: deleting node removes ceremony, not complexity.
- Deletion test: if deleted complexity reappears across callers, node earns keep; if vanishes, suspect.
- Low locality: one concept requires many edits/files to understand or change.
- Low leverage: callers learn too much order, config, invariants, errors.
- Scattered test surface: tests pin internals below true interface.
- Duplicate responsibility: packets/code claim same ownership in multiple anchors.
- Dependency pressure: consumer -> provider direction feels inverted, circular, or policy-leaking.
- Constraint pressure: current structure fights declared constraint.
- Map pressure: packet says clean boundary; code requires cross-boundary knowledge.

## Candidate Bar

Report only if evidence names current pain. No taste-only refactors.

Good candidate has:

- structural anchor
- code/doc evidence
- failure or maintenance cost
- improvement direction, not full design
- expected locality/leverage/test impact
- Triage-ready scope

## Language

Use structural node, anchor, boundary, dependency, locality, leverage, deletion test. Avoid component/service/API unless repo map uses it.
