# Mission Frame

Shrunk per the template's own escape hatch: this repo has no `docs/architecture` map at all
(`map_orient.py orient` returns `DEGRADED-NO-MAP`, discharged at the context step with
`docs/agents/ORCHESTRATOR_CONTEXT.md` + `docs/agents/GLOSSARY.md` as substitutes), and the run is a
bounded wiring conversion touching a small, source-confirmed set of files, not an architecture-shaping
change. A full frame would manufacture map ceremony the repo cannot back. Anchors below cite the two
substitute docs and the source files read directly, not map node ids (none exist).

## Intent

Convert two prose-only invariants (#329 worktree isolation, #328's two `record()`-survey checks) into
real command-check postconditions/preconditions the engine enforces, per LAUNCH_ORDER `D-422.md` Mission
and `DESIGN_SPEC.md` section D. Ship an enumeration check that fails when a worktree-entering template
lacks the isolation precondition, and land deliberate-breakage negative tests for every conversion in the
automated suite (`tests/`) — not manual scratch demonstrations.

## Affected Capabilities

- `checklist_engine.py` — the `record()` survey verb (invariant-check path, this workstream's fence).
  Today it stores whatever the agent types (`t["result"] = result`) and never calls `_check_condition`
  on postconditions — confirmed by direct read, not assumed. `advance()` (gated path) already does.
- `COMMANDER_SPINE.template.json` — the `init` gate, which currently has `"preconditions": []`.
- `INTERROGATION.template.json` — the `zc-consolidate` item, currently `"postconditions": []`.
- `REVIEW_SURVEY.template.json` — the `r6-fowler` item, currently `"postconditions": []`.

## Examples / Events

- A delegated Commander's `init` gate today only *prose*-instructs `verify_worktree_isolation.py --here`
  (`LAUNCH_ORDER.template.md:43`) — this run's own first Bash command was exactly that manual check,
  the thing #329 wants backed by a real gate.
- An interrogator marking `zc-consolidate` `pass` without ever running `verify_interrogation.py`, or a
  reviewer marking `r6-fowler` `pass` without `verify_fowler_pass.py`, both currently succeed — nothing
  stops it.

## Structural Anchors

- `scripts/checklist_engine.py:1731` — `record()` def (survey verb, no postcondition check).
- `scripts/checklist_engine.py:1668` — `advance()` def (gated verb, postcondition check at line 1699 —
  the pattern `record()` needs to mirror for command-kind conditions only).
- `scripts/verify_worktree_isolation.py`, `scripts/verify_interrogation.py`, `scripts/verify_fowler_pass.py`
  — the three existing, working rail scripts this issue wires in, unmodified in behavior.
- `skills/commander/templates/COMMANDER_SPINE.template.json` (`init` gate).
- `skills/interrogator/templates/INTERROGATION.template.json` (`zc-consolidate`).
- `skills/reviewer/templates/REVIEW_SURVEY.template.json` (`r6-fowler`).

## Governing Constraints / Assumptions

- Two-bin rule (doctrine B0.3, `docs/agents/GLOSSARY.md`): every enforced invariant is checked by a
  command or attested by a named human — prose alone enforces nothing. This issue is that rule applied.
- `<repo-root>`/`<work-id>` placeholders are resolved only by `instantiate_spine()` at **gated**-spine
  instantiation (`init_work_area.py --spine ...`); survey templates (`INTERROGATION.template.json`,
  `REVIEW_SURVEY.template.json`) are never run through that resolver today. The existing corpus precedent
  for a survey/child template needing a run-specific literal is `EXECUTE_PLAN.template.json`'s
  `<exact test command>` — a placeholder the driving agent hand-fills when it creates its own working
  copy, not machine-resolved. The two new command checks in this issue follow that same precedent rather
  than inventing new resolver machinery.
- #315 (open, out of scope): `_run_check_command` passes no `cwd=`, so a command postcondition's relative
  paths resolve against the engine's launch cwd, not the checklist's own directory. Every existing
  command-check in the corpus already lives with this fragility (documented in `resolve_spine`'s own
  docstring as "fragile, not broken"). This issue's new checks inherit the same fragility and do not fix
  #315 — consistent with #328's own text ("land #315 first or use a cwd-independent invocation").

## Decision Anchors & Decision Pressure

- decision:worktree-entering-membership — the enumeration check's membership set is an explicit, commented
  list (currently one entry: `COMMANDER_SPINE.template.json`), not a heuristic auto-detector, because
  "which roles get dispatched into an isolated worktree" is an architectural fact (who provisions via a
  LAUNCH_ORDER) not mechanically derivable from spine JSON content alone.
  @grade: guess · leans g1-implement · settle: if a second worktree-entering spine ships later, confirm
  the enumeration check's refusal-on-omission actually fires for it, not just in the deliberate-breakage
  fixture
- decision:survey-record-check-scope — `record()`'s new postcondition check covers `command`-kind
  conditions only; `artifact`/`null`-kind postconditions on a survey item remain unevaluated by `record()`
  (none exist in the corpus today, so untested territory, not a hard requirement of #328).
  @grade: settled/human · leans g2-implement (Tommy's scope ruling: "make the thing that needs to work,
  and no more" — noted at the code site, not chased)
- decision pressure: whether #329's original ask (PreToolUse hook feasibility + fleet-doctrine.md sentence
  correction) gets picked up separately — DESIGN_SPEC.md T13 already resolved the *build* to the cheaper
  spine-precondition design, so this is a triage-candidate, not a decision this run makes.

## Claims / Evidence Surfaces

- claim:record-ignores-postconditions — verified by direct read of `checklist_engine.py:1731-1740`, not
  asserted from the issue text alone.
- claim:no-template-wires-isolation — verified by `grep -rln verify_worktree_isolation skills/*/templates/*.json` returning nothing.
- claim:only-commander-enters-worktree — verified by reading `ADMIRAL_SPINE.template.json`,
  `EXPLORER_SPINE.template.json`, and `LAUNCH_ORDER.template.md`: only the Commander's own spine is the
  target of a worktree-provisioning launch order; Admiral provisions worktrees for others but does not
  itself enter one, and Explorer is human-synchronous, upstream-only, non-delegated.

## Map Confidence / Staleness / Disputes

None — no map exists to be stale or disputed; see the DEGRADED-NO-MAP discharge at the context step.

## Out of Scope

- The rest of cluster K1 (#243, #257, #280, #281, #288, #291, #313, #330, #344, #363, #373) — consolidates
  into workstream E's cluster item, per `D-422.md`'s Boundary.
- #329's PreToolUse-hook feasibility investigation and the `fleet-doctrine.md` "no engine chokepoint"
  sentence correction — DESIGN_SPEC.md T13 resolved the build to the cheaper spine-precondition design
  instead; filed as a triage candidate, not built here (spec-vs-tracker divergence, noted per the launch
  order's own tie-breaker).
- #315 (command-check cwd inheritance) — separate open issue, not fixed by this run.
- Any survey-item postcondition of `artifact`/`null` kind — only `command`-kind is wired into `record()`.
