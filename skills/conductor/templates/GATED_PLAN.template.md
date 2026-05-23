# Gated Plan: `<work item>`

## Source framing

**Framing note:** `<path/title>`  
**Route:** `patch | quick | research/prototype | cautious/framing | baseline-needed | stop using Constellation`  
**Architecture region:** `<region or unknown>`  
**Durable artifact impact:** `none expected | glossary | architecture packet | tests/contracts | issue recommendation | mixed`  
**Reconciliation required:** `yes/no, because <reason>`
**Suggested model tier:** `<simple bounded | stronger broad/ambiguous, because <reason>>`

## Gates

Each gate should be the smallest chunk that can be assigned, reviewed, proven with evidence, and stopped independently.

### Gate 1: `<name>`

**Purpose:** `<why this gate exists>`  
**Work:** `<what must be done>`  
**Owner:** `<conductor | implementer | reviewer | cartographer | triage | etc.>`  
**Suggested model tier:** `<simple bounded | stronger broad/ambiguous>`
**Test mode:** `<TDD required | test-after allowed | no test required, because <reason>>`

**Inputs:**
- `<input>`

**Completion criteria:**
- [ ] `<observable condition>`
- [ ] `<evidence condition>`

**Required evidence:** `<tests, inspection result, generated output, review approval, etc.>`  
**Stop conditions:** `<when this gate must return to Conductor/user>`  
**Next gate:** `<gate number/name>`

## Plan-level stop conditions

- unresolved human decision
- baseline confidence too low
- required evidence cannot be produced
- scope expands beyond route
- implementation requires architecture decision not in framing note

## Final completion criteria

- [ ] all gates closed or remaining blockers listed
- [ ] required review complete
- [ ] durable artifact impact handled or confirmed as none expected
- [ ] required reconciliation complete or explicitly skipped
- [ ] unresolved follow-up work captured as issue-ready recommendations
