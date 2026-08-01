# Mission Frame — issue-99

No packet map exists in this skill-source repo (no docs/architecture); this frame is authored from the skills tree itself, which IS the product structure. Not skipped as trivial: this run changes doctrine that governs every future Commander run.

## Intent
Generalize the design-it-twice standard into shared orchestrator doctrine (symmetric with the #92 critical-spec-review standard) and make Commander's plan step consume it: plan-alternatives + cold plan critic, bias-to-yes, skips surfaced as named untaken roads, panel-vs-single a surfaced complexity call. Fold in the two lifted ideas (human-framing-while-agents-run; competitive-critic opt-in mode).

## Affected Capabilities
- capability: shared orchestrator doctrine baseline (`skills/_shared/global-orchestrator.md`) — gains a design-it-twice standard section; its critical-review section gains the competitive-critic option and (via contract wording) the human-framing pattern.
- capability: Commander per-issue planning (`skills/commander/SKILL.md` Mission frame section; `skills/commander/templates/COMMANDER_SPINE.template.json` plan imperative) — plan step consumes the standard.
- capability: explorer design shaping (`skills/explorer/SKILL.md`, `templates/EXCURSION_BRIEF.template.md`, `templates/CRITIC_HANDOFF.template.md`) — referenced as the reusable contracts; minimal cross-reference edits only.

## Structural Anchors
- `skills/_shared/global-orchestrator.md` — "Critical spec review (standard, not optional)" section is the symmetry model; new sibling section lands adjacent.
- `skills/commander/SKILL.md` — "Mission frame" section carries the existing epic-weight critic sentence to be superseded/extended.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — `plan` task imperative + postconditions.
- `skills/explorer/templates/EXCURSION_BRIEF.template.md` — design-it-twice parallel-agents contract (reusable pattern the doctrine names).
- Sync hazard: `_shared/global-*.md` is mirrored per-skill at install; check how `_shared` propagates (install script bundles references) — the source edit is `skills/_shared/`, per-skill `references/` copies are install-time artifacts. VERIFY during g1 (see Confidence).

## Governing Constraints / Assumptions
- constraint: doctrine files are agent-facing, dense by design — additions must match register and stay departures-only.
- constraint: humans own convergence/triage; agents never self-triage critic findings — competitive-critic option must not erode this.
- constraint: `execute.json` freeze/amend semantics unchanged — plan-alternatives happen BEFORE authoring, not as a new engine verb.
- constraint (non-goal): explorer machinery unchanged beyond references; no new standalone skill; no engine/schema changes.
- assumption: installed-skill copies diverge from source until reinstall (lesson: commander-template-source-vs-installed-divergence) — this run edits source only; user reinstall is out of scope but should be noted at review.

## Decision Anchors & Decision Pressure
- decision (human, this run): bias-to-yes; untaken-road surfacing; panel-vs-single as surfaced complexity call — already ruled, encode faithfully.
- decision pressure: whether a thin shared template (e.g. PLAN_ALTERNATIVES contract) is warranted — implementer's design call, reviewed at gate review; surfaces to human only if it becomes a durable artifact family.

## Claims / Evidence Surfaces
- claim: doctrine section is symmetric with critical-review standard — verified by reviewer reading both sections side by side.
- claim: spine template plan imperative encodes alternatives + critic + loud-skip rules — verified by grep-able wording + reviewer inspection (doc-only gates: expect inspection-attestation proxies per lesson doc-only-gate-inspection-postcondition).
- claim: issue #99 acceptance criteria all satisfied — reviewer checks each criterion.

## Map Confidence / Staleness / Disputes
- How `_shared/` doctrine reaches installed skills (install_constellation.py bundling) — medium confidence; g1 implementer must verify the propagation path and edit the true source, not a mirror.

## Out of Scope
- Explorer's own spine/critic machinery; the checklist engine; installer behavior; superpowers-style execution machinery; reinstalling the user's installed skills.
