# Gated Plan: `<work item>`

## Source framing

**Framing note:** `<path/title>`  
**Route:** `patch | quick | research/prototype | cautious/framing | custodian-needed`  
**Architecture region:** `<region or unknown>`  
**Reconciliation required:** `yes/no, because <reason>`

## Gates

### Gate 1: `<name>`

**Purpose:** `<why this gate exists>`  
**Work:** `<what must be done>`  
**Owner:** `<conductor | implementer | reviewer | cartographer | triage | etc.>`  

**Inputs:**
- `<input>`

**Completion criteria:**
- [ ] `<observable condition>`
- [ ] `<evidence condition>`

**Required evidence:** `<tests, inspection result, generated output, review approval, etc.>`  
**Stop conditions:** `<when this gate must return to O/user>`  
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
- [ ] required reconciliation complete or explicitly skipped
- [ ] unresolved follow-up work captured as issue-ready recommendations
