---
name: constellation-explorer
description: Shape a raw idea into a confirmed, issue-ready design through repeatable exploration cycles, excursion off/on-ramps, a cold critic panel, and a hard confirmation gate. Use upstream, before any issue exists, when a human needs to explore what the point is and harden a chosen design without rushing to conclusions.
---

# Constellation Explorer

Shape a raw idea into a confirmed design, ready to cut into issues — without rushing to conclusions. Explorer is the upstream creative phase Constellation otherwise lacks: the Interrogator resolves ambiguity in an *already-cut* ask; explorer serves the stage before, when a human has an idea and needs to explore what the point is, generate and test alternatives, and harden one direction into a spec **before** any issue or epic exists.

## Role and tier

Orchestrator-tier: you dispatch subagents and talk to the human. **Upstream only** — the human invokes you directly with a raw idea, before any issue exists. Convergence decisions belong to the human alone, so explorer **requires a reachable human by construction** and has **no delegated/autonomous mode**: there is no launch order to reconcile against and no `user-decision` you may satisfy by citation. If no human is reachable, you cannot run this skill. Work id convention: `explore-<topic>`.

## Headline doctrine

These three come first because they are why this skill exists. Hold them above convenience at every step.

**1. Premature convergence is THE failure mode this skill exists to prevent.** The agent **never initiates convergence**. Present each cycle's consolidated ideas and open threads; only the human says "converge to spec." You may flag ripeness only as a **standalone message containing nothing else** — never alongside findings, options, a recommendation, or any other content. A ripeness flag carrying anything else is a convergence nudge, and nudging is initiating.

**2. Scoped nulls, optimistic persistence.** Inherited doctrine — see `references/global-everyone.md` §"Scoped nulls". Explorer-specific: a failed *excursion* scopes its null, and the default next move is **another excursion variant** — a different angle, tool, or framing, carried into the next cycle — not a closed branch. Optimistic persistence is the posture: keep testing variants; every negative excursion verdict states what was and what was **NOT tested**.

**3. Hard gate — mechanism, not just prose.** No work is cut from an unconfirmed design, and the gate has teeth, not only exhortation:
- Explorer bundles `verify_spec_confirmed.py`, which refuses unless the Confirmation block is filled (Status CONFIRMED, confirmer, date) and no critic-finding Disposition cell is empty. The `confirm` and `review` gate postconditions run it as a command check.
- A shelved (unconfirmed) shaped-design issue carries a loud marker — see Route; that marker is what downstream refuses to cut.
- Trust model, stated honestly: the engine records a `user-decision`, it does not cryptographically prove a human made it. Because explorer has **no delegated** mode, an agent fabricating one is violating doctrine with no sanctioned path around it — there is no legitimate mode in which an agent converges. The verifier and the downstream refusal are the mechanical backstops; the honesty is the point.

Whenever you name the marker in your own writing, keep it inline in a sentence, as this file does — a bare `UNCONFIRMED — DO NOT CUT` line by itself is the enforceable header and will trip the verifier's refusal. Place it standalone only where you *intend* enforcement (a shelved issue), never in passing prose.

## The spine

Drive the gated spine (`templates/EXPLORER_SPINE.template.json`) through the engine one step at a time. Instantiate it at `init` via `py C:/Users/fredc/AppData/Local/Temp/constellation-eval-zecv2779/skills/constellation-explorer/scripts/init_work_area.py <work-id> --spine C:/Users/fredc/AppData/Local/Temp/constellation-eval-zecv2779/skills/constellation-explorer/templates/EXPLORER_SPINE.template.json --skill-dir C:/Users/fredc/AppData/Local/Temp/constellation-eval-zecv2779/skills/constellation-explorer` (let the script resolve placeholders — do not hand-substitute), then `claim` the session lease and pass `--session-id <work-id>` on every mutating call.

| Step | What happens |
|---|---|
| init | scaffold work area `explore-<topic>`; materialize `spine.json`; claim the engine lease |
| context | read global doctrine (incl. deep-module vocabulary) + project deltas + the map where it exists; seed `IDEAS_BOARD.md` from template |
| explore | repeatable cycles (below); stays in-progress across cycles; closes only on a human converge/shelve `user-decision` **and** `verify_cycles.py` (≥1 `cycle-*.json`, every one consolidated) |
| spec | crystallize `DESIGN_SPEC.md` from the board; per-section approval, delta-based after the first pass; design-it-twice on every load-bearing interface |
| review | cold adversarial critique; findings land in the spec's structured table; closes only when every Disposition cell is filled (`verify_spec_confirmed.py --phase review`) |
| confirm | hard gate: `user-decision` artifact **and** `verify_spec_confirmed.py`; the Confirmation block records assumptions exercised vs. accepted untested |
| route | human routes the confirmed spec; archive work area; release lease |

The engine and the templates hold the exact per-step instructions; this table is the map, not the authority.

## Exploration cycles

Each cycle is its own survey checklist (`cycle-<N>.json`, from `templates/CYCLE.template.json`), driven with **constellation-interrogator** doctrine loaded — one question at a time, recommended answers, append/skip follow-ups, code-answers-over-questions. The cycle survey *is* the interrogation survey with flavor framing; the Interrogator is unchanged. Load it exactly as the Commander's understand step does.

At cycle start the human picks a **flavor** (you may recommend):

- **Shotgun** — pure divergence when direction is unknown. A deliberately challenging idea count (default ~20, human-set) as cheap one-liners; wild entries are sanctioned; light excursions only. Consolidation clusters and culls — but culled ideas stay on the board with reasons: a cull is a scoped verdict, and it can come back.
- **Compare** — 2–5 candidates developed seriously: trade-offs, recommendation-led presentation, excursions per candidate where earned. Consolidation is an opinionated comparison; hybrids allowed.
- **Refine** — harden one direction: chase open threads, test load-bearing assumptions, tighten interfaces in deep-module terms. Consolidation output is spec-shaped.

Natural arc: shotgun → compare → refine → spec. Flavors are re-orderable and repeatable. **A refine that kills its candidate drops back to compare or shotgun — that is the loop working, not failing.** First-cycle seeds come from `templates/EXPLORER_STARTING_QUESTIONS.template.md`; later cycles seed from the board's open threads.

## Excursion ramps

An excursion is a dispatched investigation answering **one named question**.

- **Off-ramp**: record an `EXCURSION_BRIEF` (from `templates/EXCURSION_BRIEF.template.md`) on the ideas board *before* dispatch. Either side may initiate — the human ("go look up X") or an agent proposal — same brief, same on-ramp.
- **Three types**: **research** (web/academia/codebase; primary sources; cited findings), **prototype** (dispatches constellation-prototyper), **design-it-twice** (3+ parallel agents design the same module's interface under distinct constraints, compared on depth/locality/seam/testability; opinionated recommendation or hybrid).
- Design-it-twice is a tier-wide standard (see `references/global-orchestrator.md` "Design-it-twice (standard, not optional)" and the shared `references/design-it-twice-brief.md` contract); this excursion type is its design-phase form.
- **Dispatch durably**: excursions run as **background** subagents through the bundled `py C:/Users/fredc/AppData/Local/Temp/constellation-eval-zecv2779/skills/constellation-explorer/scripts/run_crew.py` (durable registry, result-artifact verification). Run `py C:/Users/fredc/AppData/Local/Temp/constellation-eval-zecv2779/skills/constellation-explorer/scripts/recover_crews.py <work-id>` **before each dispatch and before consolidation** — the registry, not chat history, knows what was in flight, so a crash never loses an excursion.
- **On-ramp**: the result lands in the cycle record and on the board before consolidation.
- **Slow excursion at consolidation time**: the human decides — wait, or consolidate with the excursion logged as an open thread carried into the next cycle. Never silently dropped.
- **One brief, no double entry**: for a prototype excursion, the brief's prototype-section fields are identical to `PROTOTYPE_HANDOFF`'s, so nothing is typed twice.
- Every excursion verdict obeys scoped-nulls doctrine (`references/global-everyone.md`).

## The ideas board — source of truth

`IDEAS_BOARD.md` is the living record of shared understanding: the point; current candidates; verdicts (with the scope of what was tested); open threads; rejected ideas with reasons; cycle log. **Every consolidation updates it.** The spec crystallizes from it. A resumed session reads *it*, not chat history. A mid-exploration shelve files *it* as the shaped-design issue, loudly marked unconfirmed. Keep it current; it is the thing that survives a reopen cascade.

## Spec phase

Crystallize `DESIGN_SPEC.md` from the board using `templates/DESIGN_SPEC.template.md` (ships with the loud marker and a DRAFT Confirmation block — deliberate; the verifier refuses it until confirm is genuinely met). Present for **per-section approval**; after the first pass go **delta-based** — present what changed since the last confirmation, not the whole statement again. Run **design-it-twice** on every load-bearing interface (skip a trivial one only with a stated reason). Describe interfaces in deep-module terms.

## Critical review

Cold, **full adversary**: the critic reads the spec with **no exploration record**, holds nothing sacred, and may attack deliberate decisions; the human filters relitigation noise (see `templates/CRITIC_HANDOFF.template.md`). Panel scaled by weight: default one critic; a spec that would spawn epics or touch architecture gets the **3-lens panel** — intent-fit (does the design serve the stated point), testability (can each pathway be exercised and falsified), simplicity/YAGNI (what can be deleted). **When in doubt, panel.**

Findings land in the spec's structured table with fixed columns `| ID | Lens | Severity | Finding | Disposition | Reason |`. The human triages **every** finding to one Disposition — **EDIT** (fix the spec), **RE-EXPLORE** (reopen a cycle, possibly with a targeted excursion), or **REJECT** (with reason). The critic never self-triages. Confirm opens only when every Disposition cell is filled.

A RE-EXPLORE is an engine `reopen` of the `explore` step. The spine's inline rework cap is 99 so the critic→re-explore loop never hard-blocks (the default cap of 3 would). Documented cost: the reopen cascade resets spec/review/confirm and supersedes their evidence (retained, not deleted). This is survivable **because the ideas board is the source of truth** — the spec re-crystallizes from it.

## Route

The human routes the confirmed spec. **Explorer never cuts issues itself** — to-issues owns cutting:
- Hand off to constellation-to-issues or directly to a Commander; or
- File one "shaped design" issue holding the full spec body; or
- **Shelve unconfirmed**: file the ideas board as the shaped-design issue and place `UNCONFIRMED — DO NOT CUT` as a **standalone header line** on it, so `verify_spec_confirmed.py` and Commander intake refuse to cut it. This is the one place the marker is written standalone on purpose.

Then archive the work area (`.agent-work/<work-id>/` → `.agent-work/archive/<date>-<work-id>/`) and `release` the engine lease.

## Templates and scripts

Templates: `EXPLORER_SPINE.template.json`, `CYCLE.template.json`, `EXPLORER_STARTING_QUESTIONS.template.md`, `IDEAS_BOARD.template.md`, `DESIGN_SPEC.template.md`, `EXCURSION_BRIEF.template.md`, `CRITIC_HANDOFF.template.md`. Scripts: `checklist_engine.py`, `init_work_area.py`, `run_crew.py`, `recover_crews.py`, `verify_cycles.py`, `verify_spec_confirmed.py`. Engine reference: workbench `references/checklist-engine.md`.
