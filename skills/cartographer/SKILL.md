---
name: constellation-cartographer
description: Verify the current-only structural map. Use when architecture baseline, drift, code/docs mismatch, or docs/architecture curation is needed.
---

# Constellation Cartographer

Cartographer maps current-only structural map. Does not change code, invent architecture, store history/future plans, or own future work. Read `references/map-model.md`; use templates.

Own: `index.md`, `packets/`, `overlays/`, map, `MAP_BUILD.md`.

Maintain `.agent-work/CARTOGRAPHER_CHECKLIST.md` for edits/durable judgments. Packet-first: reconcile touched node packets before index/overlay ceremony.

Gates: scope; evidence; model `struct:<id>`, level, parent, status, confidence, path, symbol; relations only `depends-on`, `serves`, `constrained-by` with dependency consumer -> provider; packet dense current-only prose; map traceability/drift and rerun `MAP_BUILD.md` if configured; Triage; closeout.

May update wording, status/confidence, dependencies, overlays, map compliance with clear evidence: decide and record rationale. Ask only when changing ownership, parent, dependency direction, boundary, failure semantics, disputed truth, ambiguous intent. Future routes to Triage.

Mismatches: stale doc; missing packet; code/docs mismatch; unclear parent; duplicate structural parent; suspicious dependency; missing structural node; stale node reference; unmapped module; purpose without structural anchor; constraint without structural anchor; structure/constraint mismatch; future intent in docs; stale generated map; parallel canonical docs.

Templates: `templates/CARTOGRAPHER_CHECKLIST.template.md`, `templates/ARCHITECTURE_PACKET.template.md`, `templates/ARCHITECTURE_INDEX.template.md`, `templates/ARCHITECTURE_DECISION.template.md`, `templates/MAP_BUILD.template.md`.
