# Scout Report

Work file: `.agent-work/scout-graph-support-systems/scout.json`

## Target

**Scope:** Current Constellation graph support architecture: representation, map consumption, maintenance, feedback, and expansion beyond a single code repository.  
**Authority:** User request to step back from detailed assertion behavior and identify the weak architectural seams first.  
**Map inputs:** `skills/cartographer/references/map-model.md`; Cartographer templates; `README.md`; `docs/CONSTELLATION_OVERVIEW.md`; Commander/Implementer/Reviewer workflow templates; existing `.agent-work/AGENT_FEEDBACK.md`. No instantiated `docs/architecture/` map exists in this source repository.  
**Code sample:** `scripts/build_architecture_map.py`, `scripts/checklist_engine.py`, `scripts/grade_lint.py`, and their targeted tests.

## Findings

### Candidate: Establish a real dogfood map before generalizing the model

**Rank:** 1  
**Class:** missing architecture packet / missing structural node  
**Structural anchor:** repository-wide; intended `docs/architecture/`  
**Confidence:** high  
**Disposition:** future work -> Triage; an existing issue `#156` is recorded in `.agent-work/epic-178/crew-handoffs/cartographer-reconcile.md`

**Current pain:** Constellation's central claim is map-first operation, but its own source repository repeatedly takes the map-absent escape hatch. That prevents this project from observing whether the map actually changes planning behavior and makes every reconcile an honest null.  
**Evidence:** `docs/architecture/` is absent; `.agent-work/AGENT_FEEDBACK.md:643-657` records the recurring dogfood gap; `.agent-work/epic-178/crew-handoffs/cartographer-reconcile.md:19-34` records the existing initial-self-map issue and explains why piecemeal packets would be misleading.  
**Improvement direction:** Build one coherent current-only baseline for Constellation itself, then use real work against it before expanding ontology or storage.  
**Locality/leverage impact:** Produces the first representative corpus for every later question: map usefulness, maintenance cost, agent habits, and graph navigation.  
**Test impact:** Run the existing architecture-map builder/checker and use actual Commander runs as behavioral evidence.  
**Risk:** A map created merely to satisfy doctrine could become comprehensive ceremony. Keep it sparse under the Inclusion Rule.

### Candidate: Bind Commander map-first doctrine to a canonical input

**Rank:** 2  
**Class:** scattered interface knowledge / low locality  
**Structural anchor:** `skills/commander/templates/COMMANDER_SPINE.template.json`, `skills/commander/references/commander-core.md`, and Charter's agent-context outputs  
**Confidence:** high  
**Disposition:** future work -> Triage

**Current pain:** The Commander is told to read "the current map (packets, overlays, decision anchors)" and then author `MISSION_FRAME.md`, but its context contract does not name `docs/architecture/index.md` or another resolved map root. The mission-frame template describes the output of map consumption, not the source to consume. The canonical path appears elsewhere in the Charter-generated `AGENT_GUIDE`, which the Commander context step does not explicitly name. A critical input contract is therefore distributed across several dense documents and can be satisfied by inference or backfilled from code.  
**Evidence:** `skills/commander/templates/COMMANDER_SPINE.template.json:22-24` requires a map read without a path; `skills/commander/references/commander-core.md:122` points to `MISSION_FRAME.template.md` as the produced frame; `skills/commander/templates/MISSION_FRAME.template.md:1-5` likewise says "current map" without locating it. The actual entry point appears in `skills/charter/templates/AGENT_GUIDE.template.md:46-48,84`, while `ORCHESTRATOR_CONTEXT.template.md` contains no canonical map reference. Reconcile is more explicit than intake: Commander names the absent `docs/architecture` case at `commander-core.md:142`.  
**Improvement direction:** Give the orchestrator one compact, canonical map-consumption contract: a resolved map root/entrypoint (defaulting deliberately to `docs/architecture/index.md` where appropriate), the relevant generated projection if any, and an explicit absent/not-configured state. The Commander context step should read that contract directly and record which packet/anchor inputs shaped the mission frame. Reduce duplicated prose rather than adding another doctrine layer.  
**Locality/leverage impact:** Makes map-first a discoverable deep interface: one input, one bounded read, one output frame.  
**Test impact:** Template/fixture tests can prove a Commander receives either a resolvable map entrypoint or an explicit absent state; mission-frame evidence can name source paths without requiring full behavioral instrumentation.  
**Risk:** Hard-coding `docs/architecture` would obstruct future backends or project layouts. The contract should resolve a project-owned entrypoint while retaining a clear default.

### Candidate: Make map consumption observable, not merely instructed

**Rank:** 3  
**Class:** map/code pressure / ungrounded claim  
**Structural anchor:** `skills/commander/templates/COMMANDER_SPINE.template.json`, `skills/commander/templates/EXECUTE_PLAN.template.json`, and the crew handoff/result chain  
**Confidence:** high  
**Disposition:** future work -> Triage

**Current pain:** Constellation explicitly tells the Commander/orchestrator to read the map, create a mission frame, carry scoped anchors into crew gates, and reconcile afterward. Implementer and Reviewer are not told to crawl the full map; they consume the bounded anchors in their handoffs and return map-impact evidence. Most orchestrator map-use gates are satisfied by qualitative attestation, so the system cannot currently distinguish a Commander that used the map to find the seam from one that crawled the code first and backfilled plausible anchors.  
**Evidence:** Commander `context` and `plan` require a current-map read, mission frame, and anchored gates, but their relevant postconditions are manual null-check attestations (`skills/commander/templates/COMMANDER_SPINE.template.json:22-47`). The execute template carries structured anchors (`skills/commander/templates/EXECUTE_PLAN.template.json:19-41`), while engine-side anchor checking is absent; `scripts/grade_lint.py:456-472` only inspects decision anchors for grading. Run feedback shows both sides: precise anchors reduced rediscovery (`.agent-work/AGENT_FEEDBACK.md:515`), while a remembered packet count overrode live map truth and propagated into handoffs (`:233-248`).  
**Improvement direction:** Add a light usage/evidence loop around existing habits: record the anchors actually used to orient, validate that plan anchors exist in the current map, and record what context had to be rediscovered outside the map. Do not add a large behavioral policy engine.  
**Locality/leverage impact:** Converts map-first from doctrine into an inspectable interface and shows where the map is too thin.  
**Test impact:** Fixture tests can prove anchor references resolve; a small dogfood evaluation can compare source reads and seam selection before/after map use.  
**Risk:** Instrumentation can become surveillance-shaped ceremony. Measure only what answers whether the map saved context or improved boundary selection.

### Candidate: Add semantic drift and staleness support

**Rank:** 4  
**Class:** stale/low-confidence packet / map-code mismatch  
**Structural anchor:** Cartographer packet lifecycle and `scripts/build_architecture_map.py`  
**Confidence:** high  
**Disposition:** future work -> Triage

**Current pain:** The map can represent `current`, `partial`, `stale`, and `disputed` status plus confidence and evidence, but detecting semantic staleness remains primarily a Cartographer judgment at reconcile time. Structural validation proves shape, not that a packet's claims still match changed code.  
**Evidence:** `skills/cartographer/templates/ARCHITECTURE_PACKET.template.md:10-12` records status, confidence, and last-reconciled date. `scripts/build_architecture_map.py:298-330` validates permitted status/confidence and relationship form. Commander and Admiral schedule Cartographer reconciliation after work, but there is no source-change-to-assertion staleness trigger in the sampled builder or checklist engine.  
**Improvement direction:** Produce a map-health view that identifies assertions or packets whose evidence paths changed since reconciliation. Treat it as a review trigger, never an automatic declaration that the map is false.  
**Locality/leverage impact:** Keeps trust metadata honest without requiring agents to rediscover the entire map during every run.  
**Test impact:** Fixtures can change an evidence-backed file and prove the health view flags the dependent map material.  
**Risk:** File-change signals are noisy and do not prove semantic impact; the mechanism must remain advisory.

### Candidate: Add a federation layer rather than stretching the code spine

**Rank:** 5  
**Class:** structure/constraint mismatch  
**Structural anchor:** `skills/cartographer/references/map-model.md`  
**Confidence:** high  
**Disposition:** future work -> Triage / continued Explorer work

**Current pain:** The current model is deliberately excellent for one codebase: architecture and code form one `struct:` hierarchy, every overlay anchors to it, and artifacts live under one repository. That cannot directly serve an organized cross-project idea commons with overlapping frames and no universal structural spine.  
**Evidence:** The map doctrine says architecture and code are one hierarchy (`map-model.md:3-4`), `struct:` is the spine (`:53-61`), and durable overlays require structural anchors (`:138-182`). Generated paths are repo-local under `docs/architecture/` (`:271-280`).  
**Improvement direction:** Preserve each project map as an authoritative local frame and add stable cross-project identities plus bridge assertions in a separate federating projection. Do not weaken the useful code-map spine to make it globally generic.  
**Locality/leverage impact:** Lets local rigor and global serendipity coexist.  
**Test impact:** Eventually requires resolution tests for cross-repository identities and missing targets; no implementation is justified before the local dogfood map proves useful.  
**Risk:** Federation can introduce duplicate truth, broken references, and premature global ontology.

## Triage Handoff

- Establish a coherent initial Constellation self-map (`#156` already recorded) -> `missing architecture packet`
- Bind Commander map-first intake to one canonical map entrypoint and explicit absent state -> `architecture weakness`
- Make map consumption observable and validate plan anchors -> `architecture weakness`
- Add evidence-change-driven map health reporting -> `stale generated map`
- Explore a cross-project federation layer above local project maps -> `unresolved decision`

## Non-Findings

- **A larger tagging taxonomy is not currently justified.** The existing map already has structural, capability, event, constraint, assumption, decision, and claim kinds plus status, confidence, provenance, and evidence.
- **The orchestrator-to-crew map-use path is not absent.** Commander performs the direct read/frame step; Implementer and Reviewer receive scoped anchors and return impact evidence; Cartographer owns reconciliation. The gap is evidence of effectiveness and selective enforcement, not a need to tell every worker to read the entire map.
- **The Commander's direct-read instruction is not yet a clear input interface.** Its operative text says "current map" and points toward the mission-frame output, while the actual `docs/architecture/index.md` entrypoint is declared in a separate Charter-generated guide.
- **A graph database is not the immediate missing support.** The main pressures appear before storage: representative corpus, actual consumption, drift visibility, and federation.
- **Detailed truth-promotion behavior is downstream.** The architecture can first prove that assertions and connections help agents orient and humans understand.

## Closeout

- Unclear map truth: no instantiated map exists in this repo, so the audit used the documented map model, workflow templates, implementation, tests, and run feedback as the architecture record.
- Suggested Cartographer check: build the coherent initial self-map before using this repo as evidence for or against the broader graph.
- Triage handoff: four candidates above; no issues created or existing issues modified.
