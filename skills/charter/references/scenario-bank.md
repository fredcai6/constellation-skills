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
