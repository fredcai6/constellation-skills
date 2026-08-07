# Research Excursion: Software Policy Architecture That Resists Accretion

Date: 2026-07-30  
Question: Which software architecture patterns keep recursively edited policy, configuration, documentation, or rules understandable as exceptions and lessons accumulate?

## Verdict

Constellation's current `global baseline + tier doctrine + role procedure + project delta` model is directionally sound, but it does not yet separate **retaining what has been learned** from **delivering what an agent must understand now**.

The external systems that cope best with recurring additions use several mechanisms together:

1. Every policy concern has one canonical owner and stable identity.
2. Readers receive a resolved projection, decision, or retrieved subset rather than the whole corpus.
3. Composition semantics are mechanically explicit: merge, constrain, supersede, or fail. "Read all layers and reconcile them mentally" is not a composition rule.
4. History and rationale remain available but stay off the operational path.
5. Temporary rules carry their deletion conditions when introduced.
6. Tests, usage evidence, and corpus checks create a retirement queue; adding a lesson is not the terminal action.

The immediate architectural opportunity is therefore **not another tagging vocabulary** and not simply shorter prose. It is a small policy-resolution support system:

- canonical, concern-owned policy modules;
- a generated manifest and role/step-specific effective-policy projection;
- fail-fast detection of conflicts, duplicate ownership, dangling references, and illegal override shapes;
- an evidence-driven retirement loop for unused, expired, redundant, and superseded material.

This would preserve the full learned corpus in Git while reducing what any one agent must reconstruct.

## Scope and current Constellation pressure

This excursion compared eight architectural mechanisms across mature specifications, official project designs, and primary research. It did not install, prototype, or benchmark any candidate.

Constellation already contains important defenses:

- inherited global doctrine with project departures rather than project restatement;
- canonical shared sources copied into installed skill bundles;
- a transitory lessons inbox whose entries must graduate-and-retire or be deleted;
- a Curator that measures body size, duplicate signatures, and reference navigation;
- templates, engine gates, lint, and reproduction drills;
- explicit supersession and revision history through Git.

The pressure is nevertheless visible in the repository itself. The shared doctrine files describe themselves as "dense by design"; `global-everyone.md` is 245 lines and `global-orchestrator.md` is 138 lines as inspected on 2026-07-30. Some high-exposure rules are deliberately transcribed into multiple skill surfaces while other skills use compressed pointers. The installer materializes shared references into every applicable installed skill. The Curator detects source size and duplicated signatures, but no current mechanism resolves and reports the exact effective policy an agent needs for one role, one workflow step, and one project.

**Inference:** Constellation has a source-maintenance model, but not yet a first-class policy-delivery model. Density is being controlled mainly by authoring discipline and periodic cleanup, while each reader still pays for a broad inherited superset and must discover which sections matter.

## Comparison at a glance

| Mechanism | Canonical truth | Reader-facing form | Conflict / precedence | Removal | Main lesson |
|---|---|---|---|---|---|
| Typed modules and generated options | Option declarations plus definitions | Generated option/manual projection and evaluated configuration | Typed merges; explicit priorities; conflicts cite origins | Mostly manual | Normalize once, generate views, bound escape hatches |
| Constraint unification | Distributed compatible constraints | Concrete exported value | Order-independent intersection; contradiction fails | Weak redundancy detection | Prefer conjunction and visible conflict over implicit override |
| Policy compilation and partial evaluation | Policy modules and scoped data bundles | Decision or residual policy for known context | Named ownership roots and language semantics; tests/lint | Coverage and logs inform manual retirement | Compile the relevant operational surface |
| Deep modules / information hiding | Concern-owned module | Small interface hiding implementation knowledge | Avoids cross-layer precedence by ownership | Delete one module rather than scattered clauses | Organize by change-owning concern, not reader role |
| Decision-record lifecycle | Current decision record plus explicit history | Current index/status; history on demand | `superseded by` / deprecated status | Historical record retained, removed from current view | Keep why and old truth off the traversal path |
| Retrieval and reflection | Memory stream or validated skill library | Dynamically retrieved memories/skills | Relevance ranking, not strong conflict semantics | Commonly weak; libraries grow | Learning need not mean appending every lesson to the prompt |
| Staged feature lifecycle | Feature registry with stage, default, since/until | Component-relevant enabled gates | Lifecycle state and default are explicit | Graduation, withdrawal, and removed tables | Temporary policy needs a designed death |
| Usage-driven cleanup | Flag registry, source uses, runtime/test evidence | Cleanup candidate and reviewable diff | Intended final outcome settles branch | Automated proposal, human review, CI | Make deletion a routine product of evidence |

## 1. Typed modules, generated projections, and bounded overrides

### Source

The [NixOS module system](https://nixos.org/manual/nixos/stable/) co-locates an option's type, default, example, and documentation in its declaration. Descriptions are included in the generated NixOS manual. Multiple modules can define an option, with option types determining how definitions merge. Non-mergeable conflicts report the originating files. Override priority is explicit: ordinary definitions, defaults, and deliberate operations such as `mkForce` occupy known priority levels; ordering priority is distinct from override priority.

### Architecture

1. **Canonical truth:** option declarations define the interface; module definitions supply values.
2. **Relevant delivery:** users inspect a generated options manual or evaluated configuration rather than reading every module.
3. **Precedence:** merge semantics belong to the option type. Explicit override priorities are available and provenance is preserved for error reporting.
4. **Global validation:** module evaluation, types, assertions, and the system build test the resolved whole.
5. **Removal:** no automatic dead-option removal is inherent. Deprecation and source cleanup remain governance work.
6. **Complexity movement:** generated docs and evaluation reduce reader burden, but liberal use of `mkForce`, ordering operations, and conditional modules can create a new precedence puzzle.

### Transfer to Constellation

Constellation could define a policy module once with a stable ID, owning concern, applicability, concise operative text, source/rationale links, and validation expectation. Role-facing instructions would be generated projections of those modules plus role-local procedure.

The useful part is not Nix's numeric priority scheme itself. It is that:

- source declarations generate documentation;
- composition is typed;
- error messages preserve origins;
- exceptions are syntactically visible;
- the final resolved configuration can be inspected.

A Constellation delta should state what it narrows or replaces and name its canonical target. A project should not be able to introduce an anonymous paragraph that implicitly outranks a global invariant.

### Trap

Do not copy Nix's full generality. If Constellation grows multiple priority numbers, arbitrary ordering operators, and force-like escape hatches, it will replace prose density with precedence density. A small fixed set is preferable: inherited invariant, role selection, project narrowing, and explicit human exception.

## 2. Constraint unification instead of override stacks

### Source

[CUE](https://cuelang.org/docs/concept/how-cue-enables-configuration/) treats data, schemas, and constraints as values that unify. Unification is order-independent, associative, commutative, and idempotent. CUE deliberately disallows ordinary overrides; compatible constraints intersect, while incompatible constraints produce an error with their locations. Defaults provide preference only when a concrete value has not otherwise been supplied. The [language specification](https://cuelang.org/docs/reference/spec/) formalizes these operations.

### Architecture

1. **Canonical truth:** constraints may be distributed, but none secretly erases another.
2. **Relevant delivery:** a concrete exported value is the reader-facing projection.
3. **Precedence:** most composition is intersection, not precedence. Defaults are a limited preference layer.
4. **Global validation:** the whole configuration must unify; contradictions fail before use.
5. **Removal:** contradictions are detected, but redundant or never-materialized constraints are not automatically garbage-collected.
6. **Complexity movement:** override reasoning is genuinely reduced. Constraint provenance and domain modeling can still become difficult when many distant constraints meet.

### Transfer to Constellation

Many Constellation rules are invariants rather than preferences: a crew cannot exceed its handed-off scope; current architecture cannot include future intent; a result claim needs evidence. Project context should normally **add constraints** or narrow latitude, not replace those invariants.

This suggests separating:

- **constraints**, which intersect and fail on contradiction;
- **selection**, which chooses relevant modules;
- **defaults**, which apply only when no more specific direction exists;
- **exceptions**, which require explicit authority and provenance.

That is much more legible than treating every document layer as an override.

### Trap

Human judgment cannot always be encoded as a lattice. Forcing creative or contextual guidance into mechanical constraints would either make it brittle or produce an informal escape hatch larger than the system. Use unification for decidable invariants and leave judgment in a bounded, clearly owned interface.

## 3. Policy compilation and partial evaluation

### Source

[Open Policy Agent](https://www.openpolicyagent.org/docs) stores policy in Rego modules and data bundles, then answers named queries rather than requiring callers to interpret the policy corpus. Bundle manifests declare ownership roots. OPA recommends central aggregation where possible and warns that multiple sources have no load-order guarantee; overlapping or conflicting roots can place the system in an error state. Bundle validation checks that policy and data fall under declared roots. [Partial evaluation](https://www.openpolicyagent.org/docs/policy-performance) precomputes rules using known data and leaves a residual policy for unknown inputs. [Policy testing](https://www.openpolicyagent.org/docs/policy-testing) includes coverage reporting, while [decision logs](https://www.openpolicyagent.org/docs/management-decision-logs) record the query, input, result, and policy-bundle revision.

### Architecture

1. **Canonical truth:** versioned Rego modules and data bundles.
2. **Relevant delivery:** callers receive a decision; deployment can receive a compiled or partially evaluated policy specialized for known context.
3. **Precedence:** named package paths and bundle ownership roots replace a loose file-order cascade. Language semantics handle rule composition.
4. **Global validation:** parsing, strict checking, lint, policy tests, coverage, bundle validation, signature verification, and activation health.
5. **Removal:** coverage and decision logs expose unused surfaces but do not prove a rule is unnecessary. Retirement remains a reviewed decision.
6. **Complexity movement:** runtime callers become simple, but authors must understand a policy language, build system, data contracts, and evaluation semantics.

### Transfer to Constellation

The key pattern is **partial evaluation of doctrine against known context**:

```text
canonical policy corpus
  + role
  + workflow step
  + project context
  + delegation mode
  -> effective policy packet + provenance manifest
```

An agent should receive the result, not mentally perform that evaluation across global, tier, role, template, and project files. The manifest should make every included rule traceable to its source and explain which selector included it.

Policy behavior can be regression-tested as scenario decisions: given role X, step Y, and project delta Z, a required constraint must appear exactly once; a forbidden override must fail; a superseded rule must not enter the packet.

### Trap

Do not immediately build a general policy language or opaque runtime. Constellation's semantics are not stable enough to justify OPA-like infrastructure. A deterministic source resolver and human-readable compiled Markdown/JSON projection would test the architectural boundary first. The compiled output must remain inspectable; otherwise density is only hidden behind machinery.

## 4. Deep modules and information hiding

### Source

David Parnas's 1972 paper, [On the Criteria To Be Used in Decomposing Systems into Modules](https://sunnyday.mit.edu/16.355/parnas-criteria.html), argues that modules should be divided around design decisions likely to change, with those decisions hidden behind stable interfaces. The goal is not merely separate files; it is to make a system comprehensible one module at a time and prevent a change from propagating through unrelated modules.

### Architecture

1. **Canonical truth:** the module owning a concern owns its rules and hidden decisions.
2. **Relevant delivery:** callers learn the interface, not the internal history or every implementation clause.
3. **Precedence:** good ownership removes much of the need for precedence. Two modules should not independently own the same semantic decision.
4. **Global validation:** contract and integration tests exercise interfaces where modules meet.
5. **Removal:** if a module is truly deep, its concern and complexity can be removed locally. Scattered clauses make deletion fan out.
6. **Complexity movement:** genuine information hiding reduces complexity. Merely moving paragraphs into more files creates pointer chasing and shallow modules.

### Transfer to Constellation

This is the most important structural lesson. Constellation currently organizes much doctrine by **reader tier and role**, because those are convenient delivery locations. Learning, however, often concerns a cross-cutting concept: evidence, delegation, completion, architecture-map use, context refresh, or lesson promotion.

Each such concept needs one semantic owner with a small interface. Role documents should say how the role invokes that interface, not restate its mechanism. For example, "map-first intake" should have one compact contract that resolves the map entrypoint, absent state, required output, and evidence. Commander should consume it directly; Cartographer and Charter should implement or populate their side of the contract.

### Trap

Moving each doctrine section to its own reference file is not modularization. If an agent must open eight references to reconstruct one behavior, locality has worsened. The test is whether the caller-facing contract got smaller and the hidden material can change without requiring caller edits.

## 5. Decision records, explicit supersession, and history off the hot path

### Source

[MADR](https://adr.github.io/madr/) provides Markdown architecture-decision templates with lifecycle statuses such as proposed, accepted, rejected, deprecated, and superseded by another decision. The [MADR 4.0 templates](https://github.com/adr/madr/tree/4.0.0/template) retain context, considered options, outcome, and consequences as durable history.

### Architecture

1. **Canonical truth:** an accepted decision record owns the historical decision; a separate current architecture/policy projection should describe what operates now.
2. **Relevant delivery:** current indexes can select accepted active records; historical context is opened when needed.
3. **Precedence:** explicit status and `superseded by` links state which decision governs.
4. **Global validation:** link/status checks verify documentary integrity; behavioral tests must separately verify that implementation still matches the accepted decision.
5. **Removal:** records are normally retained as history, but deprecated and superseded records leave the current view.
6. **Complexity movement:** this reduces operational density only when readers are not required to traverse decision history to perform ordinary work.

### Transfer to Constellation

When a lesson changes a rule, the operative policy should be edited in place or superseded cleanly. The incident, rejected variants, and reason belong in a decision/lesson-history record linked from the current rule. Appending a corrective paragraph beneath the original paragraph keeps history in the runtime interface and forces every future reader to replay the evolution.

Git already supplies revision history, so a separate ADR is warranted only when the rationale and alternatives remain useful as named knowledge. The current instruction should remain concise.

### Trap

An ADR corpus easily becomes a graveyard. If "current" requires reading every accepted and superseded record, this pattern has preserved information but failed to improve use. The current projection and history must be distinct interfaces.

## 6. Retrieval and reflection in recursively learning agents

### Source

[Generative Agents](https://arxiv.org/abs/2304.03442) stores a complete natural-language memory stream, synthesizes higher-level reflections, and retrieves memories dynamically for planning. Its ablation found observation, planning, and reflection each contributed to the evaluated behavior.

[Voyager](https://arxiv.org/abs/2305.16291) accumulates an ever-growing library of executable skills. Skills are indexed by descriptions and retrieved from current task plans and environment feedback. New skills enter the library only after iterative execution feedback and self-verification.

### Architecture

1. **Canonical truth:** raw experience remains in a memory stream; reusable capability lives in reflections or validated skill artifacts.
2. **Relevant delivery:** retrieval selects a small context based on the present task rather than appending all experience to every prompt.
3. **Precedence:** semantic relevance and recency rank material, but neither system provides strong general conflict or authority semantics.
4. **Global validation:** Generative Agents validates system behavior experimentally; Voyager validates candidate programs against environment feedback and self-verification before committing them.
5. **Removal:** both examples are much stronger at accumulation and retrieval than forgetting. Voyager explicitly describes an ever-growing library.
6. **Complexity movement:** prompt density falls, but the memory corpus, retriever, synthesized reflections, and conflict risk grow.

### Transfer to Constellation

Recursive learning need not produce recursive instruction layering. A run artifact can remain historical evidence; a lesson candidate can remain staged; only a recurring, generalized, behaviorally tested constraint should enter canonical operational doctrine. At execution time, context assembly should retrieve the relevant current rule or proven procedure, not all incidents that taught it.

Constellation's current lesson audit already resembles a promotion pipeline. What is missing is a retrieval/projection boundary after promotion: graduating a lesson into a global document currently increases the inherited material every matching role may read.

### Trap

Retrieval is not governance. An embedding can find similar material but cannot reliably settle precedence, truth, or human authority. Generated reflections must not silently become canonical doctrine. Also, an ever-growing library with no consolidation or deletion policy merely hides accretion until retrieval quality degrades.

## 7. Staged lifecycle and expiry

### Source

[Kubernetes feature gates](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/) expose each gate's default, lifecycle stage, `Since`, and `Until` release. Each component supports only its relevant gates. Graduated, deprecated, withdrawn, and removed features remain inspectable through lifecycle tables, while a stable feature eventually no longer needs an active gate.

### Architecture

1. **Canonical truth:** a feature registry plus implementation owns gate state.
2. **Relevant delivery:** each component exposes only gates relevant to it.
3. **Precedence:** stage and default are explicit; this is not a general override mechanism.
4. **Global validation:** compatibility policy, conformance tests, release processes, and component behavior test transitions.
5. **Removal:** the lifecycle anticipates graduation, withdrawal, deprecation, and eventual gate removal.
6. **Complexity movement:** lifecycle metadata reduces ambiguity but creates process overhead; stale gates still accumulate if transitions are not enforced.

### Transfer to Constellation

Every temporary exception, compatibility clause, experimental workflow, or mitigation should be born with:

- owner;
- scope;
- reason;
- entry condition;
- review or expiry trigger;
- successful end state;
- removal evidence.

Permanent safety invariants do not need arbitrary dates. Temporary scaffolding does. The Curator can surface reached triggers and missing owners as review candidates.

### Trap

Date-driven expiry is unsafe for rarely exercised, high-impact protections. Expiry should trigger review or a validated cleanup proposal, not blindly delete semantic doctrine.

## 8. Usage-driven cleanup and regression handling

### Source

Uber's [Piranha research report](https://lazaroclapp.com/preprints/ICSE20-SEIP-Piranha.pdf) describes an automated pipeline that consumes a stale feature flag's name, owner, and intended final behavior, rewrites code, and sends the generated diff to developers for review. The reported production pipeline removed large numbers of stale flags; the paper recommends assigning an expiry date when a flag is created. Generated cleanup still passes through developer review and ordinary tests. Uber's [project introduction](https://www.uber.com/en-IN/blog/piranha/) frames stale flags as source complexity and reliability debt.

OPA supplies the complementary observability mechanism: decision logs identify which policy path and bundle revision produced a decision, while test coverage identifies rules and expressions not exercised by a suite.

### Architecture

1. **Canonical truth:** registry metadata states the flag and intended final outcome; source code contains its uses.
2. **Relevant delivery:** cleanup tooling presents a concrete candidate diff rather than a general "this may be stale" warning.
3. **Precedence:** the declared final outcome settles which branch remains.
4. **Global validation:** tests and human review protect against incorrect transformation.
5. **Removal:** deletion is a routine automated proposal, not optional future hygiene.
6. **Complexity movement:** validated automation genuinely deletes complexity. The analysis rules and metadata discipline add maintenance cost.

### Transfer to Constellation

Record which policy modules were included in an effective packet, which were cited in mission frames or rulings, and which caused a validation decision. Combine that with source change, expiry, supersession, and duplicate-signature evidence to produce **retirement candidates**.

The output should be a reviewable patch or precise report:

- remove unreachable duplicate;
- replace two clauses with one canonical module;
- retire expired exception;
- supersede stale procedure;
- move rationale to history;
- investigate a never-selected but high-impact invariant.

Usage is evidence, not authority. A rule unused for six months may be dead, or it may protect a rare catastrophic path.

### Trap

Hard token or line budgets can reward compressed opacity, pointer mazes, or moving text outside measured paths. Complexity budgets should remain diagnostic and should measure the **effective reader interface**—packet size, number of policy modules, number of exceptions, and precedence depth—not merely total repository lines.

## What is actually weak in Constellation

The survey points to four architectural weaknesses.

### 1. Delivery is inheritance-shaped rather than task-shaped

Global and tier references give agents broad baselines. This is safer than omission, but each role reads a superset independent of the active workflow step. There is no explicit compilation boundary between the learned corpus and the active context.

### 2. Semantic ownership and delivery ownership are conflated

A role document is a convenient place to tell a role something, but it is not necessarily the correct owner of the underlying policy. Cross-cutting concepts are consequently repeated, transcribed, or distributed through pointers. The Commander map-first defect is an example: the behavior touches Charter, Commander, Cartographer, the project guide, and a mission-frame template, but there is no one small map-intake interface.

### 3. Addition is more mature than deletion

Lessons have strong evidence, promotion, and retirement-from-inbox behavior. After graduation, however, the permanent corpus has only periodic size and duplication review. There is no equally strong lifecycle for proving a rule redundant, superseded, unused, or absorbed into machinery.

### 4. Validation checks artifacts more often than resolved behavior

Templates and scripts can validate individual files and workflow gates, but there is no inspectable "effective instruction set for Commander at plan step under project X" to test. This allows conflict and density to remain properties of a reader's mental merge.

## Opinionated support-system direction

### First: expose the current effective-policy graph before redesigning it

Create a generated manifest over existing doctrine without changing authoring format. For each operative section or policy module, record:

- stable identity;
- canonical source path and owner;
- applicable roles and workflow steps;
- project-overridable, project-narrowable, or invariant;
- references and supersession;
- whether it is copied, pointed to, generated, or enforced mechanically.

Generate, for each role and step, a report showing all selected sources, their order, duplicate signatures, unresolved targets, and total effective size. This makes today's hidden composition visible and provides a baseline.

### Second: refactor one high-value seam into a compiled projection

Use the Commander map-intake contract as the tracer bullet. It already demonstrates scattered interface knowledge and has observable outputs.

One canonical module should define:

- resolved architecture-map entrypoint or explicit absence;
- relevant-packet selection behavior;
- mission-frame output;
- evidence/anchor recording;
- failure behavior.

Commander receives the compact operational contract. Charter and Cartographer supply its inputs. History and explanation are linked, not embedded. A fixture should compile the effective Commander packet and fail if the contract is absent, duplicated, or contradicted by a project delta.

### Third: close the deletion loop

Extend corpus health from source shape to lifecycle evidence:

- expired/review-due exceptions;
- superseded modules still entering projections;
- identical or semantically overlapping ownership;
- modules never selected by any role/step;
- selected modules never referenced in sampled runs;
- prose rules whose behavior is now completely enforced by an engine gate;
- effective packets exceeding a soft size or exception-depth budget.

Each is a review candidate, never automatic semantic deletion. Mechanical duplicates and expired generated artifacts can be removed automatically when tests prove the transformation.

## Opinionated pattern language

The following patterns should guide future design. They are intentionally high-level and do not prescribe a graph database, policy language, or new tag taxonomy.

### One Concern, One Home

Every operative policy concern has one canonical semantic owner. Roles reference or project it; they do not restate it. If no single owner can be named, the interface is not yet understood.

### Compile, Do Not Layer

Treat global, tier, role, step, project, and delegation context as compiler inputs. Produce one inspectable effective packet. Never make the acting agent infer precedence by reading a stack of documents.

### Constraints Intersect; Exceptions Declare

Safety and correctness invariants compose conjunctively and fail on conflict. Defaults apply only in unspecified space. A true override is rare, authority-bearing, source-linked, and visible in the compiled output.

### Narrow at the Edge

Project deltas may narrow or specialize a canonical interface near the project boundary. They must not fork global doctrine by copying it.

### History Is Adjacent, Not Inline

Current instructions say what is true and what to do now. Rationale, prior forms, and incidents remain one link away in Git or decision records. Supersession removes old material from the current projection without erasing history.

### Learning Has a Promotion Funnel

Run evidence becomes a candidate lesson; repeated or decisive evidence becomes a generalized proposal; a named owner and behavioral test are required before it becomes operative doctrine. Promotion must replace or deepen an existing module where possible, not append a sibling warning.

### Temporary by Construction

Every exception and mitigation enters with an owner, scope, review trigger, and exit condition. Reaching the trigger produces a cleanup decision, not a silent extension.

### Runtime Is a Product

Measure the effective packet an agent receives: size, module count, exceptions, precedence depth, source diversity, and unresolved references. Total corpus size matters less than the size and coherence of the active interface.

### Usage Nominates; Evidence Decides

Selection logs, citations, and coverage identify likely dead or missing rules. They do not independently authorize removal or prove value. Rare safety constraints require scenario evidence, not popularity.

### Deletion Completes Learning

A lesson is not fully integrated when new prose is added. It is integrated when the system has also removed the obsolete instruction, redundant workaround, expired exception, or repeated explanation that the lesson replaces.

### Fail the Projection

The resolver should fail visibly on duplicate canonical ownership, cycles in supersession, dangling references, contradictory invariants, illegal project overrides, and ambiguous precedence. A plausible packet assembled from conflicting sources is worse than no packet.

## Recommended near-term experiment

The smallest experiment that answers the architectural question is not a new ontology:

1. Generate an effective-source manifest for Commander `context` and `plan`.
2. Measure the present packet and enumerate every source needed to reconstruct map-first intake.
3. Refactor only map-first intake into one canonical concern-owned module.
4. Generate the Commander projection from it and preserve a provenance manifest.
5. Run several real Commander tasks and record whether the map seam is selected before code exploration.
6. Compare effective context size, source count, ambiguity, and behavioral success.
7. Attempt to delete the superseded prose and pointers. If deletion cannot be local and safe, the proposed module is not deep enough.

This directly tests whether compilation and ownership reduce density rather than relocating it.

## Tested and NOT-tested scope

### Tested in this excursion

- Current official documentation for NixOS modules, CUE configuration, OPA policy management, Kubernetes feature gates, and MADR as available on 2026-07-30.
- Primary research/design sources for Parnas modularity, Generative Agents, Voyager, and Piranha.
- Direct inspection of Constellation's shared doctrine, installer bundling, Curator, lessons-auditor, and Scout report.
- Conceptual comparison against the handoff's seven required questions.

### NOT tested

- No candidate system was installed or run.
- No Constellation policy manifest or compiler was implemented.
- No agent task was benchmarked with projected versus inherited doctrine.
- No semantic duplicate detector was evaluated.
- No claim is made that Nix, CUE, OPA, or another external implementation should be adopted.
- Retrieval quality, rule-usage instrumentation, and safe automated deletion remain untested.
- The recommendation does not establish the final canonical policy schema; it identifies the support-system boundary that should be tested first.

The scoped verdict is therefore: **mature systems consistently separate canonical accumulation from relevant delivery and make lifecycle/removal explicit; a Constellation-specific projection experiment is justified, while a general policy engine or larger tagging taxonomy is not yet justified.**
