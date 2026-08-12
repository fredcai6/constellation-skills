# Problem statement — issue #300 (projection generator + manifest)

Reconciled against the frozen `LAUNCH_ORDER-300.md` (delegated mode; no reachable human).
Source of truth for intent: that order's **Mission**, **Pre-Rulings**, **Inherited Latitude**.

## The ask, restated

Build the minimal **deterministic projection substrate** — a versioned script that assembles
agent-facing context from canonical Markdown — and its **manifest**, the record of *what was
loaded and from which canonical revision*, produced as a free byproduct of assembly.

Acceptance (verbatim from the issue): manifest produced on every deterministic assembly;
revision identity present; consumable as the episode record's context field.
Out of scope: access tracing, transcript analysis.

## Baseline verified against code before planning

Per `lesson:verify-launch-order-claims-against-code`, the order's named baseline was checked
against HEAD (`b69e6c8`) rather than assumed.

**What the order calls "the spine's existing gate-note loading" (spec Assumption 5,
"partially grounded") actually is at HEAD:**

- `skills/commander/templates/COMMANDER_SPINE.template.json` is `{work_id, type, config_ref,
  items, tasks, ...}`. `items` is an ordered list of step-id **strings**; `tasks` is a dict of
  step objects whose fields are exactly:
  `id, title, imperative, preconditions, postconditions, constraints, directives,
  child_checklist, status, status_detail, result, finding, evidence, rework_count`.
- The engine's `current` verb is `render_human(state(cl))` — a **pure state projection** port
  (`scripts/checklist_engine.py:1336-1471`, ports-and-adapters, carrying a `contract` version
  int; documented in `docs/CHECKLIST_ENGINE_DESIGN.md` §Answerability). It selects the active
  step deterministically off spine state and prints that step's `imperative`.

**So the half that is real:** *selection* is deterministic, mechanical, and spine-keyed. That
is the whole of Assumption 5's grounding, and it is genuine.

**The half that does not exist:** *assembly*. Every canonical Markdown file an agent is meant
to hold is named **inside the imperative prose** and opened by hand:
`references/global-orchestrator.md`, `references/global-everyone.md`,
`docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`, `.agent-work/LESSONS.md`,
`references/design-it-twice-brief.md`, `templates/MISSION_FRAME.template.md`,
`skills/workbench/templates/STATE_NOTE.template.md` (extracted by regex over the template).
There is **no machine-readable declaration** of that set, **no assembler**, and **no record**
of what was loaded or at which revision.

**Negative greps (mission premise is NOT already satisfied at HEAD):**

- `grep -rniI "projection" scripts/ skills/ docs/ tests/` — every hit is the engine's
  *internal state* projection or unrelated Charter vocabulary. No context/doctrine projection.
- `grep -rniI "manifest" scripts/` — only `TEMPLATES_MANIFEST.json` (installer template
  freshness, `check_skill_freshness.py`) and `file_issue_set.py`'s issue-set manifest.
  Neither is a context manifest.

**Conclusion:** this is a real build, not an honest-null. But it is a **narrower** build than
"a versioned script that assembles agent-facing context" reads at first: the deterministic
selector already exists and must be extended, not re-created (`decision:extend-dont-parallel`).
The genuinely new machinery is (a) a declared, machine-readable per-step context set,
(b) an assembler over it, (c) the manifest.

## Governing constraints inherited (not re-litigated)

| Constraint | Source | Effect on this run |
|---|---|---|
| Design-it-twice on the manifest interface, 3+ candidates under named distinct constraints | `decision:design-it-twice-required` | A required plan-step gate. Not skippable as trivial. |
| Convergence choice is **not mine** — float to the Admiral, who surfaces it to Tommy | `decision:convergence-is-human` | Expected mid-mission return. I recommend; I do not settle. |
| Extend the spine's gate-note loading; no parallel assembly path | `decision:extend-dont-parallel` | The assembler binds to the existing engine selector/projection port. |
| Canonical storage stays Markdown in git; no DB, no query language | `decision:markdown-in-git` | Revision identity must come from git itself. |
| Full cold-panel review (spec B0.4) | `decision:full-cold-panel` | 3-lens panel floor; no light single-reviewer pass. |
| Determinism is exercised, not asserted: clean checkout, second environment, declared exclusion set kept separate from content | `decision:determinism-is-the-acceptance-test` | Line endings, filesystem ordering, locale are the named real risks on this Windows corpus. |
| Must not foreclose the Stratum A assertion truth model | `decision:no-foreclosure` | Manifest entries must stay expressible as assertions with source. |
| Stochastic boundary (spec B0.1) | Launch order §Governing spec principle | No LLM inference at assembly time. Pure function of canon + selector. |

## Protected intent

The manifest is the epic's **honest observability instrument**: it answers *what was made
available to an agent, at which revision* — **delivery, not use**. It must not be built or
described as if it proved use; issue #307 pairs it with transcript ordering for that. Anything
that quietly widens it toward access tracing is out of scope by the issue's own words.

## Interface obligation toward #301 (concurrent, no cross-edit)

The manifest must be **consumable as the episode record's context field**. I define its shape on
its own merits and state the obligations #301 can rely on. Any change to those obligations is a
float to the Admiral, never a cross-edit into #301's worktree.

## Map confidence

This skill-source repo carries no `docs/architecture/` packet map. Substituted structural
record: `docs/CONSTELLATION_OVERVIEW.md`, `docs/CHECKLIST_SCHEMA.md`,
`docs/CHECKLIST_ENGINE_DESIGN.md`. The engine-design doc is current and specific about the
projection port (written for #227), so confidence on the affected seam is **high**; there is no
map area this ask depends on that is stale or disputed. `docs/agents/` overlay is absent by
design in this repo — not a gap to fix.

## Gaps taken to the Admiral

None at `understand`. The one known float is scheduled and expected: the design-it-twice
**convergence choice** at the `plan` step.
