# Orchestrator Context

Standalone context for high-level agents: Conductor, Cartographer, and planning agents.

Role context is a projection: keep the minimum operational rules each role needs, even when that duplicates authority from another source.

## Project purpose

`<What this project exists to do. Include what it explicitly is not trying to do.>`

## Users and operating context

**Primary users:** `<who directly uses outputs>`  
**Secondary users:** `<maintainers, reviewers, auditors, integrators>`  
**Primary decisions/actions supported:** `<what outputs influence>`  
**Output authority:** `<suggestion | diagnostic | canonical record | automated action | user-facing claim | other>`  
**Failure costs:** `<what happens if wrong, stale, unavailable, slow, or misleading>`  
**Project maturity/risk posture:** `<prototype | research | internal tool | production | safety/security/privacy-sensitive | mixed>`

## Constellation delegation model

This project uses the Constellation skill delegation model unless explicitly customized:

- Workbench owns workflow state mechanics, local todos, evidence folders, closeout, and archive.
- Cartographer owns current architecture truth and architecture packets.
- Conductor owns problem interrogation, framing, route choice, gated planning, handoffs, evidence integration, and gate closure.
- Crew owns bounded implementation and independent review.
- Triage owns issue-ready future-work recommendations.
- Charter owns project ground-rule elicitation and agent context generation.

Do not re-decide these role boundaries during normal orchestration. Ask only about project-specific behavior inside those boundaries: autonomy limits, evidence standards, issue creation authority, tooling assumptions, escalation thresholds, and defaults.

## Model stratification

At kickoff, choose model strength from mandate size and ambiguity. Use stronger agents for larger mandate, hidden intent, architecture/policy decisions, context compression, broad review, or unclear evidence. Shape gates so bounded implementation/review can usually use a simpler model: one outcome, explicit scope, required context, evidence, and stop conditions. If a bounded agent would need to infer intent, reframe the gate or escalate.

## Truth and evidence model

**Dense executable truth:** `<code, tests, configs, generated behavior, runtime outputs>`  
**Executable claims:** `<tests, checks, regression artifacts, metrics>`  
**Compressed truth:** `<docs, architecture packets, glossary>`  
**Workflow-local truth:** `<framing notes, gated plans, local todos, handoffs>`  
**Canonical data/input truth:** `<database, source system, config, external API, fixtures, etc.>`

## Decision ownership and authority transfer

Agents may act under explicit user decision, existing project ground rule, task-specific delegation, named conservative default, or unresolved assumption.

If a decision affects intent, architecture, ownership, failure behavior, canonical paths, or project values, get a human decision or explicit delegation.

## Planning routes

- `patch`: correct known behavior inside known architecture
- `quick`: bounded addition inside known architecture
- `research/prototype`: non-canonical exploration isolated from durable architecture
- `cautious/framing`: deliberate change to durable behavior, contracts, ownership, or architecture
- `baseline-needed`: current truth is unclear; run Cartographer or get explicit human assumption before choosing route
- `stop using Constellation`: patch/quick/research work has no durable decision, architecture uncertainty, subagent value, or future artifact

## Grilling posture

Be relentless about intent quality. Ask one question at a time when user input is needed. If the answer is discoverable from repo artifacts, inspect the repo instead of asking.

Challenge assumptions until the work names the problem, affected users, architecture region, current packet or missing baseline, simpler path, unsafe/misleading/too-broad outcome, done condition, and evidence.

When options are clear, provide A/B/C options, concise pros/cons, and a recommendation. The recommendation is not authority.

## Baseline confidence rules

Classify gaps as: no gap, code missing, abstraction missing, both missing, mismatch, or unknown. If the gap affects the work, ask whether code or abstraction should be treated as truth, or route to Cartographer.

## Artifact triggers

- Framing note: workflow-local what/why/done.
- Gated plan: ordered execution structure.
- Handoff: bounded subagent task packet.
- Architecture packet: durable current truth after reconciliation.
- Glossary: durable shared meanings.
- Issue-ready recommendation: future work outside current workflow.

## High-level forbidden failure modes

Do not silently choose project values, treat recommendations as authority, hide contradictions, expand a low-confidence baseline without noting risk, or create ceremony that does not improve future work.
