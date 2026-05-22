# Orchestrator Context

Standalone context for high-level agents: Conductor, Cartographer, and planning agents.

## Project purpose

`<What this project exists to do. Include what it explicitly is not trying to do.>`

## Users and operating context

**Primary users:** `<who directly uses outputs>`  
**Secondary users:** `<maintainers, reviewers, auditors, integrators>`  
**Primary decisions/actions supported:** `<what outputs influence>`  
**Output authority:** `<suggestion | diagnostic | canonical record | automated action | user-facing claim | other>`  
**Failure costs:** `<what happens if wrong, stale, unavailable, slow, or misleading>`  
**Project maturity/risk posture:** `<prototype | research | internal tool | production | safety/security/privacy-sensitive | mixed>`

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
- `custodian-needed`: current truth is unclear; establish baseline before choosing route

## Grilling posture

Challenge ideas without being antagonistic. Ask what problem is being solved, why it matters, who uses the result, what architecture region owns it, what packet supports it, what simpler path exists, what could make it unsafe/misleading/too broad, what done means, and what evidence proves done.

When options are clear, provide A/B/C options, lightweight pros/cons, and a recommendation. The recommendation is not authority.

## Baseline confidence rules

Classify gaps as: no gap, code missing, abstraction missing, both missing, mismatch, or unknown. If the gap affects the work, ask whether code or abstraction should be treated as truth, or route to Cartographer.

## Artifact triggers

- Framing note: workflow-local what/why/done.
- Decision note: workflow-local decision shaping gates.
- Gated plan: ordered execution structure.
- Handoff: bounded subagent task packet.
- Architecture packet: durable current truth after reconciliation.
- Glossary: durable shared meanings.
- Issue-ready recommendation: future work outside current workflow.

## High-level forbidden failure modes

Do not silently choose project values, treat recommendations as authority, hide contradictions, expand a low-confidence baseline without noting risk, or create ceremony that does not improve future work.
