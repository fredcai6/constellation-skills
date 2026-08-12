# Charter Scenario Bank

Use these as seeds. Adapt them to the user's project; do not read them verbatim.

## Pattern

```text
Situation:
Rigorous default:
Cost:
Relaxation:
Options:
Evidence:
What this decides:
```

## Operating context

### Output authority

**Situation:** An output may be advisory, diagnostic, a canonical record, a user-facing claim, or an automated action.  
**Rigorous default:** Treat outputs as advisory unless the project explicitly designates higher authority.  
**Cost:** Agents may ask more questions before automating or publishing.  
**Relaxation:** Allow best-effort outputs without explicit authority labels.  
**Options:** A. advisory, B. diagnostic, C. canonical record, D. user-facing claim, E. automated action, F. mixed by artifact.  
**Evidence:** The generated context names the authority and failure consequence for important outputs.  
**What this decides:** Evidence strictness, wording, failure behavior, and stop/ask thresholds.

### Runtime versus analysis

**Situation:** The same repo contains operational runtime code and analysis/reporting tools.  
**Rigorous default:** Execution context controls failure behavior.  
**Cost:** Subsystem rules must be named instead of applying one blanket failure rule.  
**Relaxation:** Use one project-wide failure policy.  
**Options:** A. runtime/operational, B. analysis, C. test infrastructure, D. reporting, E. exploratory, F. generated artifact pipeline, G. mixed.  
**Evidence:** Subsystem table distinguishes rigor profile from execution context.  
**What this decides:** Exceptions versus status returns, degraded output, event/reporting requirements.

## Correctness

### Plausible wrong output

**Situation:** A change produces clean-looking output but may be wrong for edge cases.  
**Rigorous default:** Prefer visible failure over plausible wrong output.  
**Cost:** More validation and tests; fewer silent fallbacks.  
**Relaxation:** Allow best-effort output for low-risk private exploration.  
**Options:** A. fail visibly, B. labeled degraded output, C. allow best effort, D. mixed by output authority.  
**Evidence:** Tests, validation, or review evidence show the wrong-plausible case is caught or labeled.  
**What this decides:** Review blockers and fallback rules.

## Canonical inputs and data sources

### Source bypass

**Situation:** Fastest implementation bypasses the project's named input path.  
**Rigorous default:** Promoted behavior uses canonical inputs and does not bypass them silently.  
**Cost:** Slower implementation when the canonical path is awkward.  
**Relaxation:** Allow direct source access for exploratory or one-off work.  
**Options:** A. never bypass, B. bypass only in labeled exploration, C. allow with evidence, D. mixed by subsystem.  
**Evidence:** Context names canonical inputs and allowed bypass conditions.  
**What this decides:** Data access policy and review blockers.

## Evidence and verification

### Small behavior change

**Situation:** A behavior change looks obvious.  
**Rigorous default:** Use test-led evidence where a test surface exists.  
**Cost:** Slower changes and more up-front test design.  
**Relaxation:** Review-only for no-test-surface artifacts or low-risk text changes.  
**Options:** A. test-led evidence, B. focused regression evidence, C. review evidence only because no relevant test surface, D. mixed by artifact.  
**Evidence:** Failing/passing test evidence or explicit no-test-surface review evidence.  
**What this decides:** Crew evidence requirements.

## Simplicity and unit shape

### Local complexity

**Situation:** One large function is fastest but hides multiple concepts.  
**Rigorous default:** Split when complexity obscures intent or evidence.  
**Cost:** More names and boundaries.  
**Relaxation:** Allow larger local functions when still readable.  
**Options:** A. local readability enough, B. split by reviewer judgment, C. small composable units expected, D. hard complexity limits.  
**Evidence:** Review can point to clear units and focused tests.  
**What this decides:** Implementation convention and review criteria.

## Interface contracts

### Flexible input

**Situation:** Accepting many shapes makes callers easier but hides invalid states.  
**Rigorous default:** Meaningful boundaries have explicit contracts and validation.  
**Cost:** More validation code and stricter callers.  
**Relaxation:** Flexible internals with strict public boundaries only.  
**Options:** A. flexible, B. public strict only, C. meaningful internals strict too, D. fixed-shape contracts.  
**Evidence:** Contract tests, validation tests, or caller evidence.  
**What this decides:** Interface and config rules.

## Architecture boundaries

### Boundary shortcut

**Situation:** Easiest fix imports across intended ownership.  
**Rigorous default:** Do not cross ownership/dependency boundaries without explicit approval.  
**Cost:** More design work or a smaller fix.  
**Relaxation:** Allow temporary shortcut with exit condition.  
**Options:** A. block, B. allow with approval, C. allow with exit condition, D. mixed by subsystem.  
**Evidence:** Context states approval/exit requirements.  
**What this decides:** Stop/ask behavior and review blockers.

## Failure behavior

### Operational invalid state

**Situation:** Runtime code detects invalid state after partial work.  
**Rigorous default:** Fail visibly using the mechanism appropriate to execution context.  
**Cost:** Status/reporting paths and tests may be needed.  
**Relaxation:** Raise immediately or return partial output in lower-risk contexts.  
**Options:** A. exception/stop, B. status result, C. status plus safe default, D. event/status code, E. mixed by execution context.  
**Evidence:** Tests or review evidence for the failure path.  
**What this decides:** Error/status return conventions.

## State and side effects

### Hidden mutable state

**Situation:** Caching or mutation simplifies code but can affect later outputs.  
**Rigorous default:** Hidden state must be explicit, testable, and bounded.  
**Cost:** More plumbing and tests.  
**Relaxation:** Allow local state in private helpers.  
**Options:** A. local state acceptable, B. obvious state only, C. explicit state boundaries, D. deterministic/idempotent constraints.  
**Evidence:** Tests or design notes show state effects are controlled.  
**What this decides:** Implementation and review rules.

## Performance and resources

### Expensive correctness

**Situation:** The safest validation is slower.  
**Rigorous default:** Correctness wins unless resource constraints are material.  
**Cost:** Slower workflows or more compute.  
**Relaxation:** Use sampling, caching, or lighter checks.  
**Options:** A. performance not material, B. avoid obvious waste, C. known scale constraints, D. enforced budgets.  
**Evidence:** Benchmarks, resource notes, or explicit non-material decision.  
**What this decides:** Performance review expectations.

## Documentation

### Ownership change

**Situation:** Code changes responsibility or data flow but public behavior is unchanged.  
**Rigorous default:** Update relevant context/docs when meaning changes.  
**Cost:** More maintenance per change.  
**Relaxation:** Defer docs until public behavior changes.  
**Options:** A. code/tests only, B. public behavior only, C. ownership/interface/data flow docs, D. docs freshness blocks review.  
**Evidence:** Updated context/docs or explicit no-docs reason.  
**What this decides:** Documentation touch rules.

## Dependencies

### New library

**Situation:** A dependency simplifies implementation.  
**Rigorous default:** Prefer existing tools; add mature dependencies only with clear value.  
**Cost:** Some local code may be longer.  
**Relaxation:** Add common dependencies freely.  
**Options:** A. add when useful, B. mature dependency with clear value, C. explicit justification, D. user approval required.  
**Evidence:** Justification and verification.  
**What this decides:** Dependency policy.

## Security, privacy, and publicness

### Public claim

**Situation:** Generated output may be read as a public or user-facing claim.  
**Rigorous default:** Public claims need stronger evidence and careful wording.  
**Cost:** Slower publishing and more provenance checks.  
**Relaxation:** Treat outputs as informal/private unless marked otherwise.  
**Options:** A. private/local, B. teammate-facing, C. public/user-facing, D. sensitive/private data, E. mixed by output.  
**Evidence:** Context names audience, evidence, and labeling rules.  
**What this decides:** Claim confidence and privacy handling.

## Generated artifacts

### Direct edit

**Situation:** It is easiest to edit a generated artifact directly.  
**Rigorous default:** Derived artifacts are regenerated from source unless explicitly canonical.  
**Cost:** Need regeneration path and checks.  
**Relaxation:** Direct edits allowed for one-off or non-canonical artifacts.  
**Options:** A. direct edit allowed, B. convenience output, C. derived only, D. reproducible with stale checks.  
**Evidence:** Regeneration command/check or explicit direct-edit rule.  
**What this decides:** Generated artifact policy for both shaping and review.

## Compromises

### Known violation

**Situation:** A useful change violates a selected rule.  
**Rigorous default:** Accepted compromises need reason, owner, and exit condition when they affect future work.  
**Cost:** More follow-up discipline.  
**Relaxation:** Comment-only or silent compromises in exploratory work.  
**Options:** A. silent in exploration, B. comment note, C. tracked with exit condition, D. block unless approved.  
**Evidence:** Context, checklist, or issue-ready follow-up text records the correct target.  
**What this decides:** Whether compromise becomes context, Charter open question, or future-work text.
