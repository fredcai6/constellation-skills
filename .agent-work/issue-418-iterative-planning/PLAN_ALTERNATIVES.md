# Plan Alternatives — Iterative Planning

## One plan designed three ways

Implement the confirmed iterative-planning handoff as one bounded Commander run.

## Panel

Three independent candidates because the change alters public skill taxonomy, the planning artifact seam, and Admiral execution policy.

| Constraint | Recommendation | Depth | Locality | Seam | Testability |
|---|---|---:|---:|---:|---:|
| Smallest diff | Extend the issue-set seam, add one lean pure replan seam, wire doctrine, prove #418 | 4/5 | 5/5 | 4/5 | 5/5 |
| Most testable | Strict structured boundaries and pure validators/renderers across five isolated review steps | 4.5/5 | 4.5/5 | 5/5 | 5/5 |
| Best seam placement | One versioned planning manifest separating fixed boundaries from mutable plan state | 9/10 | 9/10 | 10/10 | 10/10 |

## Converged recommendation

Use one strict planning-manifest seam shared by Explorer's shaped brief, the initial cutter, the replanner, and Admiral. Keep fixed fields (intent, done, good-enough/appetite, constraints, fixed decisions) separate from mutable fields (current wave, forecast, uncertainty, parked). Forecast entries have no issue shape. Existing tracker adapters and receipts remain transport; agent/Admiral judgment authors packets; pure code validates and renders them.

Execute in four crew-reviewed gates:

1. Hard rename plus the current-wave-only initial-cut contract and filing behavior.
2. Lean replanning skill plus strict transition validation/rendering.
3. Explorer, Commander, and Admiral contract wiring.
4. Frozen-input #418 counterfactual and integrated verification.

This combines best-seam's artifact boundary with smallest-diff's four-gate delivery. The most-testable candidate's separate contract gate is folded into each owning behavior gate so tests still lead code without introducing a fifth cross-cutting step.

## Untaken roads

- General planning state machine: outside scope and duplicates Admiral judgment.
- Checklist-engine redesign: no affected interface requires it.
- Second tracker/update framework: existing adapters and receipts already own transport and idempotency.
- Compatibility alias: conflicts with the repository's single-method posture; no evidence yet requires one.
- Mechanical rewrite of archives/external `to-issues` provenance: historical evidence is intentionally preserved.

## Panel record

Panel of three retained. The change is architecture-touching; a two-agent or single-candidate plan would under-sample seam and migration risk.
