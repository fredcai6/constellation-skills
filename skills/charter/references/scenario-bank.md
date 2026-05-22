# Charter Scenario Bank

Use this as a seed bank. Adapt scenarios or create new ones based on the user's statements.

## Pattern

```text
Situation:
Boring default:
Options:
Follow-up if needed:
What this decides:
```

## Project-reality scenarios

### Primary use case

**Situation:** The project has several possible purposes: experiment, dashboard, model pipeline, production tool, personal assistant, reporting system, etc.  
**Boring default:** Treat the most concrete current user-facing workflow as the primary use case; treat speculative future workflows as secondary.  
**Options:** A. current manual workflow is primary, B. automated pipeline is primary, C. research exploration is primary, D. external/user-facing output is primary, E. mixed by subsystem, F. I don't care → current concrete workflow is primary.  
**Follow-up if needed:** Name one real task a user performs with this repo today. What output do they trust? What would make that output unusable?  
**What this decides:** Planning route defaults, evidence standards, and how aggressive agents can be.

### Output consumer

**Situation:** A repo output may be consumed by the author, another agent, a script, a report reader, a teammate, or an external user.  
**Boring default:** Treat machine-consumed outputs and teammate-facing outputs as higher rigor than private exploratory outputs.  
**Options:** A. personal exploration, B. internal automation, C. teammate-facing artifact, D. public/user-facing claim, E. downstream machine input, F. mixed by artifact.  
**Follow-up if needed:** Pick the most important output. Who sees it, what do they do with it, and how would they notice it was wrong?  
**What this decides:** Validation, docs, compatibility, and failure-reporting expectations.

### Canonical input/source of truth

**Situation:** Agents can often fetch raw external data, reuse cached data, inspect generated outputs, or read a database.  
**Boring default:** Promoted behavior should use the project-designated canonical source path. Research may bypass only when labeled non-canonical.  
**Options:** A. database/cache is canonical, B. external API/raw source is canonical, C. checked-in fixtures are canonical for tests only, D. generated artifacts are canonical, E. mixed by subsystem, F. I don't care → promoted code uses existing canonical project path.  
**Follow-up if needed:** When raw source and stored project data disagree, which should an agent trust for promoted code?  
**What this decides:** Data access policy and Cartographer truth model.

### Evidence of success

**Situation:** The project can look correct by inspection but fail by calibration, regression, reproducibility, runtime behavior, or user interpretation.  
**Boring default:** Require reusable evidence for promoted behavior; allow manual/visual evidence only for research/prototype work.  
**Options:** A. automated tests, B. backtest/metric threshold, C. reproducible report artifact, D. human visual review, E. reviewer judgment, F. mixed by subsystem.  
**Follow-up if needed:** What is one change that would look good but should still be rejected? What evidence catches it?  
**What this decides:** Crew evidence expectations and Conductor gate criteria.

### Failure cost

**Situation:** The project can fail by being wrong, stale, slow, unavailable, misleading, overconfident, unreproducible, or hard to maintain.  
**Boring default:** Prefer visible failure over valid-looking wrong output when outputs guide decisions.  
**Options:** A. wrong output is worst, B. stale output is worst, C. missing output is worst, D. slow output is worst, E. misleading confidence is worst, F. maintainability loss is worst, G. mixed by output.  
**Follow-up if needed:** Pick one output. If it is wrong but plausible, what bad decision could someone make?  
**What this decides:** Error handling, fallback, degraded mode, and review strictness.

## Seed scenarios

### Output authority

**Situation:** The project produces an output that someone may act on.  
**Boring default:** Treat outputs as advisory unless explicitly designated as canonical or automated authority.  
**Options:** A. advisory, B. diagnostic, C. canonical record, D. automated action, E. mixed, F. I don't care → advisory unless a specific path says otherwise.

### Project maturity

**Situation:** The project could be prototype, research, internal tool, production, or high-assurance.  
**Boring default:** Tune rigor to use case; isolate shortcuts from canonical paths.  
**Options:** A. prototype freely, B. research with labeled non-canonical outputs, C. internal-tool discipline, D. production-like discipline, E. safety/security/privacy discipline, F. mixed, G. I don't care → internal-tool defaults unless risk suggests stricter.

### Ambiguous requirement

**Situation:** Two reasonable implementations would differ.  
**Boring default:** Challenge ambiguity before implementation if it affects behavior, architecture, or evidence.  
**Options:** A. ask, B. make smallest reversible assumption, C. implement likely interpretation, D. create framing first, E. I don't care → ask if consequential.

### Boundary shortcut

**Situation:** Easiest fix imports against intended ownership.  
**Boring default:** Do not violate ownership; find the right seam or ask.  
**Options:** A. block, B. allow if local/tested, C. allow only with temporary-debt issue, D. I don't care → block unless prototype/research.

### Hidden fallback

**Situation:** A fallback can produce output but may hide missing data.  
**Boring default:** Fail clearly rather than produce valid-looking questionable output.  
**Options:** A. fail clearly, B. explicit degraded output, C. fallback only with reporting/tests, D. best effort, E. I don't care → fail clearly.

### Fail-safe pathway

**Situation:** A correctness-relevant operation detects invalid state after partial work.  
**Boring default:** Stop, report clearly, and avoid valid-looking partial output.  
**Options:** A. fail fast, B. fail-safe with required event mechanism, C. rollback then fail, D. degraded mode, E. I don't care → fail clearly.

### Small behavior change

**Situation:** A behavior change is small and obvious.  
**Boring default:** Add/update a focused test.  
**Options:** A. always require test, B. test unless mechanical, C. reviewer judgment, D. no test for obvious changes, E. I don't care → focused test.

### Source bypass

**Situation:** Fastest implementation bypasses canonical data path.  
**Boring default:** Do not bypass canonical paths except explicit research/prototype.  
**Options:** A. never bypass, B. research-only, C. allow if tested, D. I don't care → canonical path for promoted code.

### Architecture doc update

**Situation:** Code changes module responsibility but public behavior is unchanged.  
**Boring default:** Update architecture/context docs if ownership or data flow changed.  
**Options:** A. docs only for public behavior, B. docs for architecture/ownership changes, C. follow-up work, D. I don't care → update if abstract model changed.

### New dependency

**Situation:** A library simplifies implementation but can be written locally.  
**Boring default:** Avoid dependency unless it provides mature, nontrivial value.  
**Options:** A. avoid, B. allow common mature dependencies, C. ask every time, D. prefer dependencies, E. I don't care → avoid unless strong reason.

### Agent finds stale baseline

**Situation:** Conductor shapes a task but code/docs disagree about ownership.  
**Boring default:** Ask whether code or abstraction is truth; route to Cartographer if needed.  
**Options:** A. stop and ask, B. assume code wins, C. assume docs define intent, D. proceed with risk note, E. I don't care → ask if mismatch affects task.
