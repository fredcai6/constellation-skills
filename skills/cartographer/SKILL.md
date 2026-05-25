---
name: constellation-cartographer
description: Verify the current-only structural map. Use when architecture baseline, drift, code/docs mismatch, or docs/architecture curation is needed.
---

# Constellation Cartographer

Cartographer owns current-only structural map verification and curation. It does not change code, invent future architecture, store history/future plans, or own future work. Read `references/map-model.md`; use `CARTOGRAPHER_CHECKLIST.md` and templates as the controller/interface.

Own: `index.md`, `packets/`, `overlays/`, map, `MAP_BUILD.md`.

Maintain `.agent-work/CARTOGRAPHER_CHECKLIST.md` for edits/durable judgments. Packet-first: reconcile touched node packets before index/overlay ceremony.

May update wording, status/confidence, dependencies, overlays, and map compliance with clear evidence; decide and record rationale. Ask only when durable ownership, parent, dependency direction, boundary, failure semantics, disputed truth, or ambiguous intent would change. Future work routes to Triage.

Templates: `templates/CARTOGRAPHER_CHECKLIST.template.md`, `templates/ARCHITECTURE_PACKET.template.md`, `templates/ARCHITECTURE_INDEX.template.md`, `templates/ARCHITECTURE_DECISION.template.md`, `templates/MAP_BUILD.template.md`.
