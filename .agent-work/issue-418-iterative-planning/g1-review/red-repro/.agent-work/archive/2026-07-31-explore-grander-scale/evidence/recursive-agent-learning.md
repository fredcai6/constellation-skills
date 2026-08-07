# Recursive Agent Learning Without Instruction Accretion

**Research question:** How do active agent-learning and self-improvement systems convert experience into reusable capability without appending every lesson to the runtime instruction context?

**Research date:** 2026-07-30

**Boundary:** This is a conceptual excursion, not an adoption recommendation. It compares current primary papers, official repositories, and official documentation. Reported benchmark results are the authors' scoped claims, not independent validation.

## Verdict

Instruction density is not an incidental documentation problem. It is what happens when a learning system has a capture path but no compilation, replacement, retrieval, or retirement lifecycle.

The surveyed systems divide learning into several different durable forms:

- short-lived reflections;
- distilled insights;
- executable skills;
- tiered memories;
- progressively disclosed capability packages;
- optimized prompt/program candidates;
- bounded, regression-gated skill libraries;
- versioned archives of whole agent implementations.

The transferable pattern is not any one representation. It is the separation of:

```text
experience
  -> candidate lesson
  -> validated durable artifact
  -> task-specific runtime projection
  -> observed outcome
  -> revision, replacement, or retirement
```

Constellation currently captures experience well, but too often collapses the middle of this lifecycle into “add another instruction.” It needs support for **replacement and compilation**, **bounded runtime projections**, and **corpus-level regression evidence** more than it needs a richer tagging vocabulary.

The strongest directly relevant result is GRASP: it treats improvement as add/modify/remove edits to a bounded skill library and gates each candidate on a balanced held-out probe containing previously passing and failing cases. In its tested structured environments, the authors' ablation found that skill writing without validation was no better than using no skills. [GRASP paper](https://arxiv.org/abs/2605.29668)

That finding aligns with the broader SkillLearnBench result: automatically learned skills can help, but gains are inconsistent across tasks and models, and self-feedback alone can produce recursive drift. External feedback and repeated evaluation mattered more than model scale. [SkillLearnBench paper](https://arxiv.org/abs/2604.20087), [official repository](https://github.com/cxcscmu/SkillLearnBench)

## A useful lifecycle vocabulary

The comparison is easiest to understand by distinguishing five artifacts that are often conflated:

1. **Experience:** a trajectory, failure, review, human correction, test result, or environmental observation.
2. **Candidate lesson:** an interpretation of experience that might generalize.
3. **Durable capability:** a retained insight, skill, memory, prompt program, tool, or implementation.
4. **Runtime projection:** the subset or compiled form actually placed in an agent's context or tool surface for one task.
5. **Evaluation record:** evidence that the capability helped, harmed, conflicted, or became stale.

A recursive learning system becomes dense when every candidate lesson is promoted directly into an always-loaded runtime projection.

## 1. Capture is useful, but append-only reflection does not scale

### Reflexion: append recent verbal lessons for another attempt

**Sourced mechanism.** Reflexion converts feedback on a trajectory into natural-language self-reflection and stores that reflection in an episodic memory buffer. The buffer then conditions later attempts without changing model weights. The paper evaluates variants across sequential decision-making, coding, and language-reasoning tasks. [Reflexion paper](https://arxiv.org/abs/2303.11366)

- **Durable experience:** verbal reflections derived from a task trajectory and feedback.
- **Lifecycle operation:** primarily append within a retry loop.
- **Runtime context:** stored reflections are supplied to the actor on later trials.
- **Conflict/staleness handling:** no general cross-task reconciliation or corpus maintenance mechanism is established.
- **Regression/global quality:** the paper evaluates task performance and feedback variants, not the health of a long-lived reflection corpus.
- **Promotion authority:** the agent's reflection module promotes its own interpretation of feedback.

**Transfer inference for Constellation.** Reflection is well suited to a local run ledger: it can improve the next attempt while evidence is fresh. It is a poor default route into durable doctrine. A run reflection should remain evidence until a separate process shows that it generalizes.

**Trap.** A plausible explanation of failure can be wrong and then bias later attempts. More recent work explicitly identifies confident, incorrect stored reflections as “memory confabulation,” which reinforces the need to keep reflection and promotion separate. [Honest Lying paper](https://arxiv.org/abs/2605.29463)

**Tested / not tested.** Tested: bounded retry loops on several task families. Not tested: years of accumulated lessons, multi-agent doctrine, human-governed promotion, or whole-corpus regression.

### ExpeL: distill across experiences, then edit and vote

**Sourced mechanism.** ExpeL retains an experience pool, retrieves successful trajectories similar to a new task, and extracts cross-task natural-language insights. Its insight extractor can `ADD`, `EDIT`, `UPVOTE`, and `DOWNVOTE`; an insight is removed when its importance count falls to zero. At inference, the tested implementation concatenates the full insight list and retrieves top-k similar successful trajectories. The authors explicitly note retrieval as a possible response if the insight list grows. [ExpeL paper](https://arxiv.org/pdf/2308.10144.pdf), [official repository](https://github.com/LeapLabTHU/ExpeL)

- **Durable experience:** raw success/failure trajectories plus abstracted insights.
- **Lifecycle operation:** append raw experience; distill, edit, reinforce, weaken, or delete insights; retrieve examples.
- **Runtime context:** all extracted insights in the tested implementation, plus selected similar successes.
- **Conflict/staleness handling:** later experiences can edit, downvote, and eventually remove an insight.
- **Regression/global quality:** task evaluation and ablations compare insight-only and retrieval-only modes, but promotion is not gated against a broad regression set.
- **Promotion authority:** an LLM insight extractor performs the operations; users can inspect, alter, add, or remove the natural-language artifacts.

**Transfer inference for Constellation.** This is the clearest early demonstration that learning should update an existing body of guidance rather than only append to it. The useful primitive is an explicit edit operation with an identity: “this evidence modifies or challenges that lesson.”

**Trap.** ExpeL's tested runtime still loads the whole distilled insight set. Distillation delays density but does not eliminate it. Its scoring also measures recurrence among sampled experiences, not whether an insight preserves behavior elsewhere.

**Tested / not tested.** Tested on HotpotQA, ALFWorld, and WebShop, with a transfer experiment to FEVER. Not tested at organization-scale corpus size, across changing project architectures, or with a durable human approval boundary.

## 2. Compile experience into capabilities rather than prose

### Voyager: retain executable skills and retrieve them when relevant

**Sourced mechanism.** Voyager learns in Minecraft through an automatic curriculum, iterative code generation informed by environment feedback and self-verification, and an ever-growing library of executable skills. Relevant skills are retrieved for new tasks; the library transfers to a fresh world. The paper reports its improvements only in this embodied Minecraft setting. [Voyager paper](https://arxiv.org/abs/2305.16291), [project site](https://voyager.minedojo.org/)

- **Durable experience:** code programs that successfully implement reusable behavior, with descriptions used for retrieval.
- **Lifecycle operation:** compile successful behavior into an executable skill and retrieve it later.
- **Runtime context:** task-relevant library entries, rather than every prior trajectory.
- **Conflict/staleness handling:** environment execution and self-verification filter candidate programs; the design is described as ever-growing and does not establish general pruning or incompatible-version handling.
- **Regression/global quality:** ablations test major components and transfer, but not long-term library health under environmental change.
- **Promotion authority:** the autonomous loop promotes a skill after successful task completion/self-verification.

**Transfer inference for Constellation.** When a lesson is truly procedural and stable, it should often compile into a script, validator, template, or narrow workflow instead of remaining explanatory prose. The runtime instruction then names the capability and its trigger; the mechanics live outside context.

**Trap.** “It worked once” is not a sufficient universal promotion criterion. Executable skills can conceal domain assumptions, and an ever-growing library merely moves density from prose to routing and compatibility.

**Tested / not tested.** Tested: skill acquisition, composition, ablation, and transfer in Minecraft. Not tested: evolving software repositories, contradictory human doctrine, multi-project governance, or skill retirement.

### Agent Skills: progressive disclosure of packaged expertise

**Sourced mechanism.** Anthropic's Agent Skills package instructions, scripts, and references in files. Only name/description metadata is initially visible; the full `SKILL.md` and deeper references are loaded when relevant. Scripts can keep repeatable mechanics out of the context window. The official material explicitly describes skills as packaging expertise because agents do not automatically learn from repeated tasks. [Anthropic Agent Skills explanation](https://claude.com/blog/building-agents-with-skills-equipping-agents-for-specialized-work)

- **Durable experience:** human- or agent-authored instruction/resource packages, versionable as files.
- **Lifecycle operation:** package and progressively retrieve; code can replace repeated prose procedures.
- **Runtime context:** metadata first, skill instructions when selected, references only on demand.
- **Conflict/staleness handling:** not inherently supplied by progressive disclosure; maintainers must curate overlapping or obsolete skills.
- **Regression/global quality:** the mechanism describes context loading, not automatic continual-learning evaluation.
- **Promotion authority:** whoever authors and installs/commits the package; it is not an autonomous learning protocol.

**Transfer inference for Constellation.** Constellation already has this basic shape, but it should apply progressive disclosure inside its orchestration skills more aggressively: a small executable contract at the entrypoint, then narrow references selected by explicit conditions.

**Trap.** Progressive disclosure makes a large corpus cheaper to load; it does not make the corpus coherent. Hundreds of discoverable modules can still produce routing ambiguity, duplicated contracts, and scattered interface knowledge.

**Tested / not tested.** Official operational guidance and product mechanism are available, but the cited material does not present a longitudinal self-learning benchmark or a conflict-resolution evaluation.

## 3. Treat context as a projection over durable storage

### MemGPT / Letta: tier memory and compile the active context

**Sourced mechanism.** MemGPT introduced virtual context management: a limited main context, recall storage containing event history, and archival storage used through explicit retrieval and editing operations. The model can manage movement between tiers. Current Letta memory blocks are labeled, persisted units with explicit size limits; they may be agent-editable or developer-only/read-only, and the request context is compiled from persisted state. Blocks can also be shared across agents. [MemGPT paper](https://arxiv.org/abs/2310.08560), [Letta memory blocks](https://www.letta.com/blog/memory-blocks/)

- **Durable experience:** full event history, archival records, and compact core-memory blocks.
- **Lifecycle operation:** append to recall/archive; retrieve; replace or edit active memory; compile context.
- **Runtime context:** selected core blocks plus retrieved material, within explicit budgets.
- **Conflict/staleness handling:** blocks can be rewritten and protected as read-only, but the base memory architecture does not itself guarantee correct contradiction or freshness adjudication.
- **Regression/global quality:** the original paper evaluates long-document analysis and multi-session chat, not global semantic consistency of a growing memory.
- **Promotion authority:** the agent can edit when given tools; developers can make blocks read-only and edit them directly.

**Transfer inference for Constellation.** The important separation is not “hot versus cold files”; it is **canonical durable material versus a compiled working set**. Runtime instructions should be a budgeted projection assembled for the role, frame, and task, while the complete learning history remains queryable and versioned.

**Trap.** Delegating memory management to the same agent that consumes the memory creates a circular authority problem. Recent STALE evaluation found a broad gap between retrieving updated evidence and actually rejecting or adapting away from stale state, with its best evaluated system reaching only 55.2% overall on that benchmark. [STALE paper](https://arxiv.org/abs/2605.06527)

**Tested / not tested.** MemGPT tested document analysis and multi-session conversation. The cited work does not validate long-lived engineering doctrine, graph-backed provenance, or safe autonomous promotion across agents.

## 4. Replace the active program under evaluation

### GEPA / DSPy: evolve candidate instructions, then return a selected program

**Sourced mechanism.** GEPA reflects on execution traces and textual feedback to propose mutations to selected prompt/program components. It maintains a Pareto frontier of candidates that excel on at least one validation instance, can merge components from different lineages, and ultimately returns the candidate with the best aggregate validation performance. [DSPy GEPA documentation](https://github.com/stanfordnlp/dspy/blob/main/docs/docs/api/optimizers/GEPA/overview.md), [GEPA paper](https://arxiv.org/abs/2507.19457)

- **Durable experience:** traces, textual feedback, scores, candidate prompt/program variants, and optional run metadata.
- **Lifecycle operation:** mutate and replace program components; retain a candidate population during optimization.
- **Runtime context:** the selected compiled program, not the whole optimization history.
- **Conflict/staleness handling:** competing instructions are resolved through candidate comparison and validation; the history may remain outside runtime.
- **Regression/global quality:** validation controls selection, and Pareto retention preserves complementary candidates; quality is bounded by the supplied metric and datasets.
- **Promotion authority:** the optimizer proposes, but the developer defines metrics, feedback, train/validation sets, and chooses whether to deploy the returned program.

**Transfer inference for Constellation.** A doctrine change can be modeled as a candidate replacement of a bounded interface, not a paragraph appended beneath the old one. Run history can explain the replacement without remaining inside the active instruction.

**Trap.** An optimizer makes the evaluation suite constitutional. If the suite does not represent human intent, maintainability, unusual work, or interaction among roles, it will produce locally optimized doctrine with hidden regressions.

**Tested / not tested.** Tested on the paper's selected prompt/program optimization tasks. Not tested as governance for a recursively delegated human-agent organization or as maintenance of a heterogeneous documentation corpus.

### GRASP: bounded, reversible edits with a hard regression gate

**Sourced mechanism.** GRASP groups failed trajectories by mechanism, proposes several candidate edits, and evaluates each on a balanced held-out probe of previously failing and previously passing cases. An edit may add, modify, or remove a skill. The library is deliberately bounded, versioned, and reversible; a candidate is admitted only when it produces net improvement within a hard regression budget. [GRASP paper](https://arxiv.org/abs/2605.29668), [official repository](https://github.com/jomoll/GRASP)

- **Durable experience:** a small library of structured behavioral skills plus evaluation traces and prior versions.
- **Lifecycle operation:** add, modify, remove, reject, or revert; it does not require monotonic growth.
- **Runtime context:** the bounded skill library is injected at inference.
- **Conflict/staleness handling:** comparative proposals can alter or remove prior guidance; candidate changes face a regression-aware gate.
- **Regression/global quality:** directly tested against prior passing and failing examples, with a hard limit on newly introduced regressions.
- **Promotion authority:** an automated proposer creates candidates, while the benchmark/probe and acceptance rule authorize promotion.

**Transfer inference for Constellation.** This is the most direct architectural answer to instruction accretion:

1. lessons enter as proposed edits to a named contract;
2. proposals must say whether they add, replace, merge, or remove;
3. representative old scenarios are rerun;
4. promotion is reversible;
5. the active surface has a size budget.

Human direction can sit above the mechanical gate: changes to values, scope, or decision authority still require human ratification, while mechanically testable workflow improvements can pass an evidence gate.

**Trap.** GRASP is strongest where tasks recur and outcomes are verifiable. Its reported non-clinical evaluation remained flat in an open-ended action space. Constellation must not pretend that hard-thinking quality has the same oracle as a structured environment.

**Tested / not tested.** Tested across five base models on two FHIR clinical-agent benchmarks, supporting clinical and four non-clinical environments, with ablations and frozen-library transfer. Not tested on a dense recursive delegation doctrine, long-term human collaboration, or broad architectural judgment.

## 5. Keep alternative lineages without loading them all

### Darwin Gödel Machine: branch whole implementations and retain an archive

**Sourced mechanism.** DGM samples a coding agent from an archive, asks it to modify its own implementation using benchmark evidence, evaluates the child, and retains a branching archive of agents. The archive preserves lower-performing stepping stones because later descendants can become strong. The outer archive-maintenance and parent-selection process was fixed in the reported work. The paper reports improvement on SWE-bench and Polyglot under sandboxing and human oversight. [DGM paper](https://arxiv.org/abs/2505.22954)

- **Durable experience:** versioned whole-agent implementations, lineage, benchmark results, and evaluation logs.
- **Lifecycle operation:** branch and archive implementations; select a runtime candidate rather than merge every discovery into one prompt.
- **Runtime context:** only the selected agent implementation and task context execute; the full archive stays outside the prompt.
- **Conflict/staleness handling:** alternatives coexist as branches instead of being textually reconciled; poorly performing branches need not become active.
- **Regression/global quality:** coding benchmarks evaluate candidate implementations, but the score is only as broad as the sampled benchmark.
- **Promotion authority:** empirical benchmark selection inside a fixed outer evolutionary process, with the experiments run under human oversight.

**Transfer inference for Constellation.** Git already provides the valuable part: alternatives and history do not need to coexist in current doctrine. A replaced instruction can remain discoverable in lineage without remaining active. Some ideas that fail now can remain evidence or branches rather than becoming runtime burden.

**Trap.** Benchmark-driven self-rewriting grants enormous authority to the evaluation function and is much more autonomous than the desired human relationship. It also changes entire implementations, which makes cause attribution harder than bounded contract edits.

**Tested / not tested.** Tested on coding-agent performance in SWE-bench and Polyglot, including some cross-model and cross-language transfer. Not tested on epistemic governance, project-map accuracy, user-specific values, or broad open-ended collaboration.

## Comparative lifecycle matrix

| System / line | Durable artifact | Primary operation | Runtime loading | Stale/conflict response | Regression / quality boundary |
|---|---|---|---|---|---|
| Reflexion | Recent verbal reflections | Append | Reflection buffer on retry | Little beyond later reflection | Per-task outcomes |
| ExpeL | Trajectories + abstract insights | Distill, edit, vote, delete, retrieve | Full insight list + similar successes | Downvote/edit/remove | Task evaluation; no promotion gate |
| Voyager | Executable code skills | Compile and retrieve | Relevant skills | Execution/self-verification; little pruning | Minecraft task performance and ablation |
| Agent Skills | Versioned instruction/resource packages | Package and progressively disclose | Metadata, then skill, then references | External curation | No intrinsic continual-learning evaluation |
| MemGPT / Letta | Recall/archive + bounded memory blocks | Page, retrieve, replace, compile | Core blocks + retrieved records | Editable/read-only blocks; no guaranteed adjudication | Memory/task tests, not corpus coherence |
| GEPA | Candidate prompt/program variants | Mutate, compare, replace | Selected compiled program | Candidate competition | Developer-defined validation and metric |
| GRASP | Bounded skill library | Add/modify/remove with gate | Bounded active library | Reject/revert/replace under probe | Balanced held-out probe + regression budget |
| DGM | Archive of agent implementations | Branch, evaluate, select | One chosen implementation | Retain alternatives outside runtime | Coding benchmarks over sampled tasks |

## What the survey says Constellation is missing

These are support-system gaps, not a proposed detailed policy for every agent.

### 1. A learning ledger distinct from active doctrine

Run feedback, lessons, review findings, and failed candidates should remain durable evidence without automatically entering runtime instructions. The ledger can be dense because it is queried, not loaded wholesale.

### 2. A doctrine compiler

The active instruction surface should be produced from current accepted contracts. Promotion should be expressed as a transformation:

- add a genuinely new contract;
- replace an obsolete rule;
- merge redundant rules;
- move procedural detail into a script/template/check;
- split context-specific behavior into a retrieved module;
- remove guidance whose responsibility is now enforced elsewhere.

“Append lesson” should not be the default operation.

### 3. Explicit runtime budgets and progressive disclosure

Each orchestrator or crew role should have a small, legible entry contract. Project- and task-specific material should be retrieved through named entrypoints. Deep explanation, examples, history, and evidence should remain reachable without being always loaded.

This is a routing problem as much as a token problem: the entry contract must clearly identify where canonical architecture, role doctrine, and task evidence live.

### 4. Regression probes for instruction changes

A learned improvement should be tested against representative previously successful behaviors, not only the failure that inspired it. Constellation does not need a universal numerical reward. It needs a small, version-controlled scenario corpus that asks whether agents:

- locate the right interface;
- respect authority boundaries;
- produce the required handoff;
- avoid previously observed failure modes;
- preserve successful behavior in other issue shapes.

For open-ended design judgment, the probe supplies evidence rather than automatic authorization.

### 5. Corpus observability

The system should be able to answer:

- Which instructions were loaded for this run?
- Which contract led to this decision?
- Which instructions are never selected?
- Which rules repeatedly conflict or require clarification?
- Which lessons duplicate an existing contract?
- Which accepted change caused regression elsewhere?

Without this, density remains a subjective discomfort and agents can satisfy doctrine by reconstructing it after the fact.

### 6. Deliberate retirement

Git is already the archive. Removing a rule from current doctrine does not destroy the learning that produced it. Current instructions should be allowed to become smaller even while historical knowledge grows.

## Authority boundary

The survey does not support a single promotion authority for every kind of learning.

- **Mechanical rails** can be promoted by grounded tests and reversible review.
- **Procedural skills** can be proposed by agents and gated by representative execution evidence.
- **Architecture descriptions** can track authoritative project artifacts when the derivation is clear.
- **Doctrine, values, and delegation authority** require human ratification because an outcome metric cannot substitute for the intended relationship.
- **Open-ended lessons** should usually remain attributed candidates until repeated use or human judgment demonstrates generality.

This preserves human participation in the hard thinking without forcing humans to manually approve every mechanically grounded correction.

## High-level architecture direction

The smallest coherent direction is:

```text
run artifacts / feedback / evidence
            |
            v
      learning ledger
            |
       candidate edit
            |
   human and/or evidence gate
            |
            v
   canonical current contracts
       /       |        \
 short core  retrieved  compiled rails
 doctrine    modules     and templates
       \       |        /
        task runtime projection
            |
         run evidence
```

The graph can connect every layer, but the layers must not all have equal runtime status. History and candidate lessons remain available; accepted current contracts form the active basis; the task projection is the small portion an instantiated agent actually needs.

## What not to conclude

- Do not conclude that adding confidence tags will solve instruction density.
- Do not conclude that retrieval alone produces coherence.
- Do not conclude that a successful local fix is a reusable lesson.
- Do not conclude that every learned behavior should remain active.
- Do not conclude that automated benchmarks can authorize value or architecture decisions.
- Do not conclude that long instructions are necessarily bad; a long, cohesive interface may be clearer than many short scattered ones.
- Do not conclude that self-improvement results from structured benchmarks transfer automatically to open-ended human-agent collaboration.

## Recommended next experiment

Before redesigning the graph or the entire skill corpus, choose one dense orchestrator seam—Commander map consumption is a good candidate—and run a bounded lifecycle experiment:

1. preserve the current behavior as regression scenarios;
2. extract the current contract from scattered instructions;
3. produce one short entry contract with progressively disclosed references;
4. treat the change as replacement, not additive clarification;
5. run old and newly targeted scenarios;
6. record exactly what context was loaded and what source guided the plan;
7. retire superseded text while retaining Git history and the learning evidence.

This would test the central architectural move: whether Constellation can become more learned while its active instructions become smaller.

## Bottom line

Other recursive-learning systems do encounter the same pressure, but the more mature responses do not merely improve memory retrieval. They change the lifecycle of learning:

- Reflexion captures;
- ExpeL distills and weakly prunes;
- Voyager compiles;
- Agent Skills progressively disclose;
- MemGPT projects bounded context;
- GEPA replaces under validation;
- GRASP bounds, edits, and regression-gates;
- DGM archives alternative lineages outside runtime.

Constellation's missing support system is the combination of those lifecycle ideas at a human-governed level: **capture everything worth learning, promote only through explicit transformations, keep the active surface bounded, test the whole contract rather than the triggering failure, and let Git carry what is no longer current.**
