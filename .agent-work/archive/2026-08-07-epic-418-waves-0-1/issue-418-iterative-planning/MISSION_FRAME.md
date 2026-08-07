# Mission Frame

## Intent

Replace exhaustive pre-execution epic decomposition with one canonical iterative-planning workflow: compact current truth, current-wave-only runnable issues, nonbinding forecasts, evidence-led wave exits, and revisable unlaunched work. The repository has no architecture map; this frame is grounded in the context gate's hash-pinned substitutes: `README.md`, `SKILL_INDEX.md`, and `docs/agents/ORCHESTRATOR_CONTEXT.md`.

## Affected Capabilities

- Planning intake: Explorer hands off a compact shaped brief with fixed intent, done, good-enough/appetite, constraints, uncertainty, and evidence.
- Initial cutting: the renamed initial-cut skill renders a compact epic and files only current-wave issues.
- Replanning: Admiral classifies wave evidence, selects advance/repair/replan/stop, revises forecast and uncertainty, and preserves fixed boundaries or escalates.
- Installation/discovery: canonical skill names install and register once.

## Examples / Events

- Epic #418 counterfactual: five original runnable issues and three dependency edges become one coherent execution-and-validation wave plus nonbinding later outcomes.
- Blocking discrepancy: current wave is held and a repair pass is rendered.
- Evidence-only discrepancy: it appears in the wave-review record and creates no issue.

## Structural Anchors

- `README.md` — corpus purpose, canonical skill list, installation behavior, and workflow artifact conventions.
- `SKILL_INDEX.md` — public skill discovery and responsibility boundaries.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — local orchestration authority and planning constraints.

## Governing Constraints / Assumptions

- Human-confirmed intent, done, good-enough/appetite, hard constraints, and fixed decisions cannot be silently changed.
- Existing tracker ports, idempotency keys, receipt recovery, dry-run Markdown adapter, independent review, and engine-drive guarantees remain in force.
- Forecast entries are hypotheses, never runnable tracker issues.
- Historical `.agent-work/archive/` records remain untouched; the #418 inputs are read-only evidence.
- No GitHub mutation, push, or PR is authorized.

## Decision Anchors & Decision Pressure

- Human decision: canonical rename to `constellation-to-initial-issues` and separate `constellation-replan` capability.
- Human decision: only current-wave work is runnable; unlaunched work is revisable.
- Human decision: evidence history stays GitHub-native in structured epic comments; no load-bearing rationale may exist only locally.
- Decision pressure: compatibility should remain a thin, explicit migration only if installer/tests prove it necessary; the repository's backwards-compatibility posture favors one canonical path.

## Claims / Evidence Surfaces

- Initial-cut verifier and filer tests prove zero-edge validity, required compact sections, forecast non-filing, offline writes, and idempotency.
- Replan tests prove all four exit decisions, repair behavior, evidence-only non-creation, and fixed-boundary escalation.
- Installer/corpus tests prove canonical registration and absence of unintended live references to the old name.
- Demonstration comparison reports exact before/after metrics and a preservation audit.

## Map Confidence / Staleness / Disputes

- No current architecture map exists. This alters the plan by requiring direct interface tests and an end-of-run structural-document reconciliation; no inferred map boundary is treated as authoritative.
- Epic #418 evidence is historical and intentionally read-only. The counterfactual uses the information available at initial cut, not present child status.

## Out of Scope

- General checklist-engine redesign, arbitrary portfolio planning, generalized confidence languages, numeric scoring, every tracker, historical epic migration, automatic discrepancy filing, or live publication.
