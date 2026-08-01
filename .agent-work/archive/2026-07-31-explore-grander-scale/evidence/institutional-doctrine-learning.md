# Institutional Learning Without Doctrine Overload

**Excursion question:** How do safety-critical or knowledge-intensive human organizations retain lessons while preventing checklists, procedures, and doctrine from becoming too dense to use?

**Research date:** 2026-07-30

## Thin verdict

The recurring solution is not a better way to append instructions. It is a governed lifecycle that keeps three things distinct:

1. **Observed learning** — the event, evidence, lesson, or postmortem retained as institutional memory.
2. **A proposed intervention** — an owned, testable change intended to address the lesson.
3. **Current operative doctrine** — the small surface a practitioner must actually use.

Mature systems do not promote every lesson into universally visible doctrine. Promotion is selective; an accountable owner consolidates it with what already exists; the changed procedure is tried under realistic conditions; and old material is revised, superseded, or rescinded. Rich history remains available without remaining in the execution path.

The most transferable answer for Constellation is therefore a **doctrine lifecycle and consolidation boundary**, not more tags:

- retain run learning separately from current instructions;
- require each proposed doctrine change to identify the current contract it changes or supersedes;
- prefer changing tools, templates, or checks over adding behavioral prose when possible;
- distinguish a tiny universally loaded contract from role-local and reference material;
- test changed instructions by having an agent use them on representative work;
- periodically review doctrine for duplication, conflict, discoverability, and deletion;
- evaluate the learning system itself when repeated fixes continue to produce the same failure or make execution harder.

This is an inference from the comparison below, not a finding that any one institution implements the full combined pattern.

## Comparison

### 1. FAA flight-deck procedures and checklist human factors

The FAA's active [AC 120-71B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_120-71B.pdf) is unusually direct about instruction density because its procedures must be usable under workload and time pressure.

1. **How a lesson enters durable doctrine.** Procedure changes may be driven by equipment or operating-environment changes, operational problems, incidents, accidents, mergers, and safety data. Procedure developers are told to analyze the need and its wider implications before changing an SOP.
2. **Who owns consolidation and resolves conflicts.** The operator owns its SOPs, working with line flight crews, managers, manufacturers, training organizations, and the FAA where required. This is not free-form contribution: a procedure developer integrates inputs into one operating system.
3. **How detail is separated.** The operative procedure should include only what is necessary to select and execute it. The rationale belongs in a separate training manual or other document. Supplemental information is visually separated from action steps; excessively detailed hierarchies and unnecessary cross-references are discouraged.
4. **Review, rehearsal, and usability testing.** The FAA recommends periodic review involving line crews, trial periods followed by feedback and revision, and evaluation under conditions approximating actual use—including tablets, turbulence, darkness, and time pressure. Training is part of implementation.
5. **Retirement.** SOPs are revised as conditions change. At the publication level, AC 120-71B explicitly cancels its predecessor. The circular does not prescribe one universal operator-level expiry mechanism.
6. **Detecting doctrine-created risk.** Line-user review, operational safety data, observed checklist errors, inability to maintain place, visual clutter, and tests under realistic conditions expose bad procedure design. The document treats the presentation of a correct procedure as a safety variable in its own right.
7. **Transfer / disproportion.** Constellation can borrow the sharp division between executable steps and rationale, plus realistic use testing. OEM and regulator approvals, aviation-specific formatting controls, and exhaustive abnormal-situation coverage would be disproportionate.

**Distinct lesson:** The instruction is a user interface. Correct content that cannot be found, parsed, or executed under actual working conditions is still defective.

### 2. WHO surgical-checklist governance

The WHO's [Surgical Safety Checklist resources](https://www.who.int/teams/integrated-health-services/patient-safety/research/safe-surgery/tool-and-resources) pair a one-page, 19-item execution surface with a separate implementation manual, adaptation guide, training material, and local consultation.

1. **How a lesson enters durable doctrine.** The global checklist was created through evidence review and extensive multidisciplinary consultation. Local additions and modifications are encouraged where they fit the setting.
2. **Who owns consolidation and resolves conflicts.** WHO supplies the baseline. Local leaders, multidisciplinary staff, and clinical champions adapt and implement it. During execution, one designated person leads the checklist even though the whole team participates.
3. **How detail is separated.** The checklist itself remains a single concise artifact. Explanations, implementation practices, education, and adaptation guidance live outside it.
4. **Review, rehearsal, and usability testing.** WHO recommends starting in one operating room or service, testing on cases, observing whether the full team actually pauses and verbally verifies items, coaching, collecting local compliance/outcome data, and then expanding.
5. **Retirement.** WHO warns against casually removing evidence-supported baseline items, but its public material does not define a periodic expiry process for local additions. That is a limit of this lineage for the present question.
6. **Detecting doctrine-created risk.** Failure to complete the checklist consistently, lack of team participation, reliance on memory, and poor local fit reveal implementation failure. WHO explicitly warns that making the checklist too comprehensive makes it harder to implement successfully.
7. **Transfer / disproportion.** Constellation can borrow a tiny invariant core, separate implementation guidance, local adaptation, a single coordinator, and small-scale behavioral trials. Treating all software-agent instructions with clinical checklist rigidity would be disproportionate.

**Distinct lesson:** Universal safety value does not require universal detail. A small common kernel and locally adapted implementations can coexist.

### 3. Google SRE postmortem practice

Google's [SRE postmortem guidance](https://sre.google/workbook/postmortem-culture/) treats incident learning as a reviewed historical artifact with owned corrective work, not as an automatic instruction-appending process.

1. **How a lesson enters durable doctrine.** Predeclared incident thresholds trigger postmortems, and stakeholders may request one. The postmortem records impact, causes, response, and follow-up actions.
2. **Who owns consolidation and resolves conflicts.** A named postmortem owner coordinates the record; senior engineers review completeness; each action item has an owner and tracking issue; high-priority exceptions receive leadership review.
3. **How detail is separated.** The rich incident narrative stays in a searchable postmortem repository. Resulting changes are separately tracked actions. Many examples change automation, system boundaries, alerts, or safeguards rather than adding operator reminders.
4. **Review, rehearsal, and usability testing.** Drafts receive formal review and broad sharing. Reading clubs and the "Wheel of Misfortune" rehearse old incidents. Actions require measurable end states and tracking.
5. **Retirement.** Selective postmortem triggers prevent every minor event from becoming a formal artifact. Action items can close, but postmortems remain historical records. The guidance does not provide a general doctrine-expiry mechanism.
6. **Detecting doctrine-created risk.** Repeated incidents, unclosed actions, vague or equally prioritized action lists, low-quality postmortems, avoidance of the process, and reliance on "make humans less error-prone" signal that the learning mechanism is failing. The text also recognizes hard-to-train, lengthy maintenance manuals as part of system risk.
7. **Transfer / disproportion.** Constellation can keep lessons as history, require owned and measurable interventions, and prefer system changes over added admonitions. Google's company-wide incentives, incident thresholds, and operational reliability machinery would be disproportionate.

**Distinct lesson:** A lesson is not completed by documenting it. It is completed by changing a system, validating the change, and retaining the incident as evidence rather than forcing its narrative into current instructions.

### 4. FEMA continuous-improvement practice

FEMA's [National Continuous Improvement Guidance](https://preptoolkit.fema.gov/documents/36933745/38870988/National_Continuous_Improvement_Guidance_2022.pdf?download=true) provides the clearest explicit separation between an evidence-backed observation, a recommended action, implementation, and evaluation.

1. **How a lesson enters durable doctrine.** Collected data is analyzed into a concise observation. A finalized observation has evidence from multiple sources, a demonstrable operational effect, analysis, and a recommended improvement.
2. **Who owns consolidation and resolves conflicts.** Process owners, relevant stakeholders, subject-matter experts, leadership, and the responsible implementing entity participate. Actions receive accountable owners and can be tracked by an action-plan manager or body.
3. **How detail is separated.** The factual observation remains distinct from the mutable recommended action. A recommendation may change a plan or SOP, but not every observation is itself put into the plan. FEMA also offers different views of the guidance for resource-constrained, new, and mature programs.
4. **Review, rehearsal, and usability testing.** Completed actions are evaluated against steady-state data, later incidents, or exercises. Success criteria can be checked at several time horizons. The continuous-improvement program separately evaluates its own activities and outcomes.
5. **Retirement.** A recommended action may be changed or abandoned if evidence shows it is ineffective, while the original observation remains as a stable record. The guidance does not prescribe one general expiry rule for every operational procedure.
6. **Detecting doctrine-created risk.** FEMA explicitly evaluates the improvement program itself, including its processes, products, data sources, effort, and outcomes. Recurrent symptoms, failure to address root causes, and unintended effects on stakeholders send work back to an earlier phase.
7. **Transfer / disproportion.** Constellation can borrow the distinction between stable evidence and revisable intervention, plus a small periodic meta-evaluation of the learning process. A full emergency-management program office, formal AAR apparatus, and extensive outcome measurement would be disproportionate.

**Distinct lesson:** Recursive learning needs a loop that evaluates the learning process—not merely more iterations through it.

### 5. NASA lessons-learned lifecycle

NASA's current [Lessons Learned Lifecycle](https://www.nasa.gov/learning-resources/for-professionals/appel-lessons-learned/) separates collection, recording, dissemination, and application. Its public [Lessons Learned System](https://www.nasa.gov/nasa-lessons-learned/) contains reviewed lessons from projects and programs.

1. **How a lesson enters durable doctrine.** Individuals and teams collect lessons through pause-and-learn sessions, write-ups, and formal or informal discussions. Lessons can be recorded in the agency database, local repositories, reports, case studies, or recordings.
2. **Who owns consolidation and resolves conflicts.** The agency Lessons Learned Steering Committee manages the system, with a curator handling its operation. The public lifecycle page does not expose a complete contemporary conflict-adjudication procedure.
3. **How detail is separated.** Collection and preservation do not automatically equal application. A lesson may remain searchable knowledge; selected lessons are applied through training, best practices, processes, checklists, handbooks, or policy.
4. **Review, rehearsal, and usability testing.** Public LLIS entries are described as official and reviewed. NASA disseminates through courses, briefings, communities of practice, and other formats. The current public lifecycle description does not specify a universal rehearsal or usability-test gate before policy promotion.
5. **Retirement.** Current guidance shows several locations and application forms but does not specify expiry of lessons or doctrine generated from them. This is a visible gap for the present comparison: a lessons system can retain value while still growing indefinitely.
6. **Detecting doctrine-created risk.** NASA says the lifecycle helps identify where teams need support, but the public description does not name doctrine density as a managed hazard.
7. **Transfer / disproportion.** The separation of captured lesson from applied policy is highly transferable. A central agency database, steering committee, clearance workflow, and records regime are not.

**Distinct lesson:** Institutional memory should be broader than operative doctrine. Preserving a lesson is not a commitment to make every future worker read it.

### 6. U.S. Army doctrine lifecycle

The currently listed [TRADOC Regulation 25-36](https://adminpubs.tradoc.army.mil/regulations/TR25-36.pdf) supplies the strongest explicit currentness and rescission mechanism in this sample. The [TRADOC regulations index](https://adminpubs.tradoc.army.mil/regulations.html) identifies the governing publication, while the Combined Arms Center describes a [lessons-learned system](https://usacac.army.mil/Home/Lessons-Learned) that validates observations and integrates selected corrective action into doctrine, training, education, and operations.

1. **How a lesson enters durable doctrine.** Operational lessons and best practices are collected and validated; doctrine work can also be triggered by currentness assessments, leadership guidance, new policy, and capability change.
2. **Who owns consolidation and resolves conflicts.** Named doctrine proponents develop publications; affected organizations staff drafts and submit comments; comments are adjudicated; designated authorities approve. A 2026 Army description of its [Doctrine Development Tool](https://usacac.army.mil/Article-Library/View-Content?ArtMID=575&ArticleID=2313&PageID=34&PgrID=1586) emphasizes transparent, consistent review and adjudication.
3. **How detail is separated.** Army doctrine uses a publication hierarchy and assigned proponents rather than one cumulative universal manual. Development planning checks alignment with related doctrine and seeks to minimize duplication. The exact boundaries are more formal than Constellation needs.
4. **Review, rehearsal, and usability testing.** Proponents assess publications after 18 months. Planning assumes revision at least every five years, or sooner for volatile information. Draft staffing, comment adjudication, implementation, and evaluation form part of the lifecycle.
5. **Retirement.** Currentness is reported as green, amber, or red. Red publications require revision or rescission; if a publication is no longer required, the proponent rescinds it.
6. **Detecting doctrine-created risk.** The assessment asks whether the publication remains current and relevant. Amber also exposes a different risk: the owner lacked resources to perform the assessment. Feedback from the operating force and conflicts across publications are handled through staffing.
7. **Transfer / disproportion.** Explicit ownership, scheduled currentness checks, consolidation across related doctrine, and rescission are directly useful. Multi-echelon staffing, formal matrices, approval authorities, and fixed five-year planning would overwhelm a personal experimental project.

**Distinct lesson:** Doctrine must have an owner and a deletion path. Without both, "continuous improvement" means continuous accumulation.

## Recurring lifecycle mechanisms

Across the six lineages, the same mechanisms recur:

1. **Selective admission.** Incidents, observations, and field feedback enter a learning store more easily than they enter mandatory doctrine.
2. **Separate artifacts.** Evidence/history, proposed action, rationale/training, and the operative instruction are different products.
3. **Named consolidation ownership.** A proponent, process owner, operator, coordinator, or review group has responsibility for one coherent current surface.
4. **Transformation rather than transcription.** Lessons commonly become redesigned systems, checks, training, automation, or locally adapted procedures—not appended warnings.
5. **Progressive disclosure.** Universal principles and brief execution aids are separated from local procedures, explanation, examples, and history.
6. **Representative-use testing.** Procedures are tried with actual users, in realistic conditions, exercises, or small pilots before broad reliance.
7. **Closed-loop evaluation.** Completion is not enough; organizations examine whether the intervention changed the outcome.
8. **Periodic currentness and rescission.** Strong doctrine programs inspect whether material is still relevant and explicitly revise or remove it.
9. **Meta-evaluation.** Repetition, non-use, workload, conflicts, and poor outcomes can indict the learning process itself.

## What this suggests Constellation is missing

These are high-level design hypotheses, not implementation recommendations yet.

### A. A boundary between learning and doctrine

Run lessons currently have a short path to skills, references, templates, and rules. Constellation needs a durable place where a lesson can be retained, linked, and revisited without being promoted into every agent's operative context.

### B. A promotion and consolidation contract

Adding doctrine should require answering:

- Which current contract does this change?
- Is the intervention better expressed as tooling, validation, a template, role-local guidance, or universal instruction?
- What existing instruction does it replace, combine, narrow, or make unnecessary?
- Who owns the coherence of the resulting surface?

The governing pressure should be **replace or transform before append**. This is an inference from the institutional patterns, not wording taken from a source.

### C. Explicit instruction strata

A likely structure is:

- a very small universal execution contract;
- role- or frame-local operative doctrine;
- optional rationale, examples, and deep references;
- historical lessons and evidence outside the execution path.

The exact number of strata is not yet tested. The important property is that history and rationale remain discoverable without being universally loaded.

### D. Doctrine usability as testable behavior

A doctrine change is not validated merely because its text is accurate. A representative agent should be able to discover the instruction, choose the correct scope, and perform the intended behavior without reconstructing the contract from scattered references.

### E. A recurring subtraction pass

Some owner needs to periodically inspect the operative corpus for duplicated rules, conflicts, material in the wrong layer, stale assumptions, and instructions made obsolete by tooling. The Army's formal cycle is too heavy, but the presence of a deliberate revise/rescind decision is not.

### F. A health check on recursive learning

Useful warning signals include:

- the same lesson recurring despite successive instruction changes;
- agents failing to find a rule that technically exists;
- a local rule leaking into universal context;
- several sources needed to reconstruct one operative contract;
- new wording that does not replace any old wording;
- repeated exceptions, workarounds, or skipped gates;
- instruction growth without corresponding improvement in observed behavior.

FEMA's key transferable idea is to evaluate this learning machinery as its own system.

## Tensions the lifecycle must preserve

- **Memory versus attention:** retain rich learning without forcing all of it through every execution.
- **Consistency versus local fit:** keep a small shared contract while allowing roles and frames to adapt.
- **Stability versus revision:** make current doctrine dependable but cheap to supersede when reality changes.
- **Traceability versus cognitive load:** preserve why and evidence without putting them inside every procedure.
- **Expert ownership versus field judgment:** give someone consolidation responsibility while testing against actual users.
- **Rigor versus experimentation:** require clear promotion, testing, and retirement without importing regulatory ceremony.
- **Automation versus human thought:** mechanize repeatable safeguards while preserving human participation in genuinely directional decisions.

## Tested scope

- Compared six distinct institutional lineages using current regulator, institutional, and primary-practice sources available as of 2026-07-30.
- Checked each lineage against admission, ownership, layering, testing, retirement, self-risk detection, and proportional transfer.
- Looked specifically for mechanisms that prevent a valid local lesson from automatically becoming globally visible instruction.
- Distinguished source-stated practice from cross-source inference.

## Not tested

- Whether the published practices are followed consistently inside any institution.
- Comparative outcome data attributing lower error rates specifically to doctrine-density controls.
- Constellation's actual instruction dependency graph, token load, duplication rate, or agent failure modes.
- A concrete target schema, file layout, role assignment, or migration plan.
- Whether a proposed stratification improves agent behavior; that requires representative task trials.
- Legal, certification, records-retention, or compliance requirements, which are intentionally outside this personal experimental project's needs.

