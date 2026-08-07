---
name: constellation-cartographer
description: Verify the current-only structural map. Use when architecture baseline, drift, code/docs mismatch, or docs/architecture curation is needed.
---

# Constellation Cartographer

Cartographer owns current-only structural map verification and curation. It does not change code, invent future architecture, store history/future plans, or own future work. Read `references/map-model.md`; drive `templates/CARTOGRAPHER.template.json` through the engine as your controller.

Drive every step through the checklist engine and finish its sequence — final `advance`, then `release`, as journaled actions. Work the engine never saw did not happen. Full completion doctrine: `_shared/global-everyone.md`.

Own: `index.md`, `packets/`, `overlays/`, map, `MAP_BUILD.md`.

Track edits/durable judgments in your checklist. Packet-first: reconcile touched node packets before index/overlay ceremony. A reconcile that changes the map may leave a published `constellation-docent` explainer site stale — you own the map, not the site, so simply note that it can be regenerated with the docent skill (a soft pointer, never a dependency you must satisfy or edit).

May update wording, status/confidence, dependencies, capability/event/constraint/assumption/claim overlays, decision anchors, and map compliance with clear evidence; decide and record rationale as `claim:` overlays or `decision:` anchors. Ask only when durable ownership, parent, dependency direction, boundary, failure semantics, disputed truth, or ambiguous intent would change. Future work routes to Triage.

## Consuming Scout audit findings

Scout reports map-quality audit candidates only; it never edits the map. For each finding, read its **Disposition** and act:

- **Current-truth fix -> Cartographer**: the map disagrees with current code/structure (stale status, map/code mismatch, wrong dependency, ungrounded or missing anchor that current truth supports, constraint lacking evidence/explanation, high-maintenance edge that fails the Inclusion Rule). Reconcile it in place — update status/confidence, add the missing capability anchor or supporting/`verified-by`/`explained-by` edge, fix the dependency direction, or retire the edge. Decision candidates follow the map-model "Promote, Reject, or Route" step; do not duplicate it.
- **Future work -> Triage**: redesign, new structure, or remediation that is not current truth. Leave the map as-is and let it route to Triage.

Promote only accepted current truth; reject what fails the Inclusion Rule; route the rest.

Templates: `templates/CARTOGRAPHER.template.json`, `templates/ARCHITECTURE_PACKET.template.md`, `templates/ARCHITECTURE_INDEX.template.md`, `templates/ARCHITECTURE_DECISION.template.md`, `templates/MAP_BUILD.template.md`. References: `references/map-model.md`, workbench `references/checklist-engine.md`.
