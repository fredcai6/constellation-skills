# Scout Report

Work file: `.agent-work/SCOUT_REPORT.md`

## Target

**Scope:** `<struct:<id> | repo region | whole map>`  
**Authority:** `<user request | existing rule | assumption>`  
**Map inputs:** `<packets/index/overlays/generated map paths>`  
**Code sample:** `<paths>`

## Findings

### Candidate: `<title>`

**Rank:** `1..n`  
**Class:** `shallow structural node | pass-through | low locality | low leverage | duplicate responsibility | dependency pressure | constraint pressure | scattered test surface | map/code pressure | stale/low-confidence packet | map/code mismatch | missing capability anchor | ungrounded capability/claim/decision | constraint without evidence/explanation | high-maintenance edge`  
**Structural anchor:** `struct:<id> | path`  
**Confidence:** `high | medium | low`  
**Disposition:** `current-truth fix -> Cartographer | future work -> Triage`  

**Current pain:** `<what hurts now>`  
**Evidence:** `<map/code/test/config paths and observations>`  
**Improvement direction:** `<plain direction; no full design>`  
**Locality/leverage impact:** `<why better>`  
**Test impact:** `<how tests improve or what test risk exists>`  
**Risk:** `<migration/coupling/behavior risk>`  

## Triage Handoff

Only future-work findings route here; current-truth fixes go to Cartographer instead.

- `<candidate title>` -> classification `architecture weakness | structure/constraint mismatch | cleanup | missing test | performance/resource | stale generated map | missing architecture packet | missing structural node | missing capability anchor | ungrounded claim/decision | bad map edge | unresolved decision`

## Non-Findings

- `<checked but not worth reporting; optional>`

## Closeout

- Unclear map truth: `<anchors or none>`
- Suggested Cartographer check: `<scope or none>`
- Triage handoff: `<candidates or none>`
