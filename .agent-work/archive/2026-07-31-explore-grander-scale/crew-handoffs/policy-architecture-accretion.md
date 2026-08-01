# Research Handoff: Software Policy Architecture That Resists Accretion

## One named question

Which software architecture patterns keep recursively edited policy, configuration, documentation, or rules understandable as exceptions and lessons accumulate?

## Context to preserve

- Constellation already uses inherited global doctrine plus project deltas, role templates, generated installs, validators, feedback, and lesson lifecycles.
- The current failure pressure is density and scattered interface knowledge: a critical behavior may be reconstructable only by reading several layers.
- The user wants high-level support systems first, not a detailed taxonomy of every agent action.
- Backward compatibility is not a major concern; one clear execution path and fail-fast interfaces are preferred.

## Required comparison

Compare 5-8 distinct architectural mechanisms, grounded in mature specifications, official project design, or primary research. Candidate mechanisms include:

- canonical normalized source with generated role-specific projections;
- defaults plus explicit deltas and bounded override precedence;
- policy-as-code compilation and partial evaluation;
- modular ownership and deep interfaces;
- decision-record lifecycle and supersession;
- usage telemetry and dead-rule removal;
- expiry/review triggers;
- corpus linting, conflict detection, and complexity budgets.

For each distinguish:

1. Where canonical truth lives.
2. How readers receive only relevant policy.
3. How precedence and conflict are made legible.
4. How changes are validated against global behavior.
5. How dead, redundant, or superseded rules are removed.
6. Whether complexity is reduced or merely displaced.
7. What mechanism transfers to Constellation and what trap should be avoided.

## Constraints

- Use primary specifications, official architecture/design documentation, and strong research sources current as of 2026-07-30.
- Compare mechanisms rather than vendors.
- Include deletion/removability and regression handling.
- Do not install or prototype anything.
- Clearly mark inference and tested/NOT-tested scope.

## Result

Write the self-contained report to:

`C:\Programs\constellation-skills\.agent-work\explore-grander-scale\evidence\policy-architecture-accretion.md`

End with an opinionated pattern language for reducing instruction density without losing learned constraints.
