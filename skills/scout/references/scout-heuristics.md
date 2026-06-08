# Scout Heuristics

Map-first architecture audit. Read Cartographer artifacts first. Use code as pressure test.

## Loop

1. Load target packets/index/overlays/generated map.
2. Pick suspicious structural anchors.
3. Sample code/tests/config around each anchor.
4. Compare map claim, code shape, dependency direction, constraint anchors.
5. Rank candidates. Route future work to Triage.

## Modes

- **After-work reconcile**: audit the scopes a run just touched.
- **Map-quality audit** (periodic): sweep the whole map on a human/Commander cadence, asking the planning-authority lens below. Same candidates-only output; broader scope and a periodic trigger.

## Structural signals

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

## Map-quality signals — does the map still deserve planning authority?

The map earns planning authority only while it stays current, grounded, and sparse. Audit the multidimensional graph for:

- Stale / low-confidence packet: `status: stale | disputed` or `confidence: low` node never reconciled; map claim no longer matches current code.
- Map/code mismatch: a node's purpose, dependency, or constraint contradicts the current code it anchors.
- Missing capability anchor: an important structural node does behavior Commander would plan against, but no `capability:` names it (only `Purpose` prose).
- Ungrounded capability/claim/decision: a `capability:`/`claim:`/`decision:` with no supporting `struct:` via `supports` or no evidence-backed `verified-by`/`explained-by` — nothing grounds it in current structure.
- Constraint without evidence/explanation: a `constraint:` with no `verified-by` claim/evidence and no `explained-by` decision — unenforceable, unfalsifiable rule.
- Wrong dependency direction: a `depends-on` edge points consumer<-provider, circular, or policy-leaking.
- High-maintenance edge: an edge (especially `generated` or fine-grained) costs upkeep but serves no Inclusion-Rule purpose (planning / boundary correctness / rule preservation / trust) — propose retiring it.

When in doubt, apply the Inclusion Rule: if a node/edge serves none of planning, boundary correctness, rule preservation, or trust, flag it as failing to earn its place.

## Disposition

Split every finding:

- **Current-truth fix -> Cartographer**: the map disagrees with current code/structure (stale status, wrong dependency, missing/ungrounded anchor that current truth supports). Cartographer fixes it in place.
- **Future work -> Triage**: redesign, new structure, an unresolved decision, or remediation that is not current truth. Route as a Triage candidate.

Scout records the disposition on each finding and never applies it.

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
