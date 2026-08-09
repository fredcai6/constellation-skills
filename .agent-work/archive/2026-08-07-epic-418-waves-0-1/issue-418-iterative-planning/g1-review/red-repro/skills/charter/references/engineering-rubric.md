# Engineering Rubric

Touch every axis. A material choice needs cost, scenario, decision, evidence, and output implication. Mark `not-material` only with user agreement.

Use fixed rigor profiles:

- exploratory/research
- pragmatic internal tool
- rigorous durable system
- operational/runtime
- safety/security/privacy-sensitive
- mixed

Use execution contexts separately:

- runtime/operational
- analysis
- test infrastructure
- reporting
- exploratory
- generated artifact pipeline

## Contents
- [1. Correctness posture](#1-correctness-posture)
- [2. Canonical inputs and data sources](#2-canonical-inputs-and-data-sources)
- [3. Evidence and verification](#3-evidence-and-verification)
- [4. Simplicity, abstraction, and unit shape](#4-simplicity-abstraction-and-unit-shape)
- [5. Interface and contract strictness](#5-interface-and-contract-strictness)
- [6. Data semantics and identity](#6-data-semantics-and-identity)
- [7. Architecture boundaries](#7-architecture-boundaries)
- [8. Failure behavior](#8-failure-behavior)
- [9. State and side effects](#9-state-and-side-effects)
- [10. Performance and resource posture](#10-performance-and-resource-posture)
- [11. Documentation posture](#11-documentation-posture)
- [12. Dependency and tooling posture](#12-dependency-and-tooling-posture)
- [13. Security, privacy, and publicness](#13-security-privacy-and-publicness)
- [14. Generated artifacts and derived outputs](#14-generated-artifacts-and-derived-outputs)
- [15. Compromise and debt policy](#15-compromise-and-debt-policy)

## 1. Correctness posture

A. Best effort acceptable for exploratory work.  
B. Correct for normal paths; edge cases handled as discovered.  
C. Correctness before speed for promoted behavior.  
D. High assurance: explicit invariants, negative cases, and regression evidence.  
E. Mixed by subsystem.

## 2. Canonical inputs and data sources

A. User-selected ad hoc inputs are acceptable.  
B. Existing project data paths are preferred.  
C. Promoted behavior must use named canonical inputs.  
D. Canonical inputs require validation, provenance, and conflict handling.  
E. Mixed by subsystem.

## 3. Evidence and verification

A. Human inspection is enough.  
B. Focused tests/checks for behavior changes.  
C. Reusable automated evidence plus review evidence.  
D. Regression suites, reproducible artifacts, metrics, or audit evidence required.  
E. Mixed by change type or subsystem.

## 4. Simplicity, abstraction, and unit shape

A. Local readability is enough.  
B. Prefer simple functions/modules; split when intent blurs.  
C. Small composable units and explicit seams are expected.  
D. Complexity limits or review-blocking structure rules apply.  
E. Mixed by subsystem.

## 5. Interface and contract strictness

A. Flexible interfaces are acceptable.  
B. Public interfaces strict; internals flexible.  
C. Meaningful internal boundaries also validate shape and meaning.  
D. Fixed-shape contracts are required at critical boundaries.  
E. Mixed by subsystem.

## 6. Data semantics and identity

A. Local interpretation is acceptable.  
B. Common project naming is enough.  
C. Identities, units, frames, and semantics must be explicit where used.  
D. Ambiguous units/identity/frame handling blocks changes.  
E. Mixed by domain area.

## 7. Architecture boundaries

A. Boundary shortcuts are acceptable in local work.  
B. Boundary shortcuts need review judgment.  
C. Ownership and dependency boundaries are respected unless explicitly approved.  
D. Boundary changes require deliberate approval and documentation updates.  
E. Mixed by subsystem.

## 8. Failure behavior

A. Raise/stop clearly.  
B. Return status at important boundaries.  
C. Return status plus explicit degraded output where safe.  
D. Status/event/reporting codes are required for meaningful branches or failures.  
E. Mixed by execution context.

## 9. State and side effects

A. Local mutable state and side effects are acceptable.  
B. Side effects should be obvious and contained.  
C. Stateful boundaries must be explicit, testable, and reviewable.  
D. Determinism, idempotency, or side-effect isolation is required.  
E. Mixed by subsystem.

## 10. Performance and resource posture

A. Performance is not material unless visibly bad.  
B. Avoid obviously wasteful behavior.  
C. Known scale/resource constraints guide design and tests.  
D. Performance budgets, allocation limits, or latency constraints are enforced.  
E. Mixed by execution context.

## 11. Documentation posture

A. No extra docs beyond code/tests.  
B. Update docs only for user-visible behavior.  
C. Update docs/contracts/context when ownership, interfaces, data flow, or failure meaning changes.  
D. Documentation freshness is review-blocking for relevant changes.  
E. Mixed by artifact type.

Constellation-maintained context and architecture artifacts must stay current when their meaning changes; this axis asks for project-specific rules beyond that baseline.

## 12. Dependency and tooling posture

A. Add dependencies when useful.  
B. Prefer existing tools; add mature dependencies when value is clear.  
C. New dependencies need explicit justification and review evidence.  
D. New dependencies require user approval or policy exception.  
E. Mixed by subsystem.

## 13. Security, privacy, and publicness

A. Local/private assumptions acceptable.  
B. Protect secrets and private data by default.  
C. Output audience and claim exposure determine evidence and wording strictness.  
D. Security/privacy/public claims require explicit review and provenance.  
E. Mixed by output or subsystem.

## 14. Generated artifacts and derived outputs

A. Generated artifacts may be edited directly.  
B. Generated artifacts are convenience outputs unless marked canonical.  
C. Generated artifacts are derived; edit sources or regenerate.  
D. Generated artifacts need reproducibility, labels, and stale-output checks.  
E. Mixed by artifact type.

## 15. Compromise and debt policy

A. Silent compromises acceptable in exploratory work.  
B. Code/comment notes are enough.  
C. Track accepted compromises with reason and exit condition.  
D. Block compromises unless the user explicitly approves.  
E. Mixed by subsystem.

Route outcomes carefully:

- unresolved Charter context question: `.agent-work/CHARTER_OPEN_QUESTIONS.md`
- accepted current rule or exception: generated context
- implementation follow-up: issue-ready text outside Charter context
