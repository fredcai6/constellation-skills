# Handoff — design candidate C

**Your result path (write here, nothing else):** `.agent-work/567-k/crew-handoffs/design-C-result.md`

**Suggested Model Tier:** sonnet — bounded design authoring against a brief that already carries the facts; breadth over reasoning depth.

---

# Design brief — #634: one spine per agent, frozen bookends, mutable middle

You are a **cold design-candidate author**. You have no authoring context and you are not
expected to acquire any beyond this brief and the source it points at. Read the source. Do not
guess. **Write no code and change no file** except your own result file.

Repo: `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`
Everything below is pinned to commit `9b38b9d9`. Verify each line number yourself; report any
that has moved.

## The human's direction, verbatim

> "I regret freezing gates, if anything I want to make the gates a little looser so we can step
> back more frequently and update them. there should likely be frozen required gates at the start
> and finish, but what we do in the middle is squishy and is totally reasonable to change as
> we're executing and understanding the problem better"

> "this isn't only a commander thing, admirals also should be able to mutate the middle of their
> plan… let's not over design this for commanders. heck, I wouldn't be mad at a crew updating its
> plan along the way too. it'd probably be good for us to be able to capture 'the plan changed,
> here's how' though"

## Established facts — do not re-derive, do not contradict without evidence

These were read at source this run. If your reading disagrees, **say so and show the line**.

1. `amend()` (`scripts/checklist_engine.py:2971`) already re-plans a GATED checklist:
   `add` (`:3047`), `drop` (`:3076`), `rescope` (`:3089`), `retext-check` (`:3115`).
   All-or-nothing — built on copies, committed only at `:3177`. Requires non-empty `--reason`
   and `--authority`. Appends `{ts, reason, authority, ops}` to `cl["amendments"]` (`:3180`).
   The MCP door already exposes it as `spine_amend`.
2. `_floor()` (`:3036`) is the **only** freeze in the engine: `1 + index of the last non-pending
   gate`. An `add` may not insert below it (`:3068`). `drop` and `rescope` gate on
   `status == "pending"` and nothing else.
3. **Therefore the opening bookend is already frozen (by having been started) and the closing
   bookend is not frozen at all.** A Commander standing at `execute` can `drop` its own
   `archive`. An Admiral can `drop` its own `closeout`. Confirm this yourself before building on it.
4. `advance(--from_child)` (`:2617`) attaches a child **survey**'s `consolidation` as
   `review-result` evidence before postconditions run. `consolidate()` is survey-only (`:2734`).
   It is a **cross-agent verdict seam** — evidence flows up, a parent never drives a child.
   **It is out of scope and must survive untouched.** Any candidate that reshapes it is wrong.
5. The three role spines are all `type: gated`:
   - `skills/commander/templates/COMMANDER_SPINE.template.json` —
     `init·context·understand·plan·execute·reconcile·triage·review·feedback·archive`
   - `skills/admiral/templates/ADMIRAL_SPINE.template.json` — `init·latitude·execute·closeout`
   - `skills/explorer/templates/EXPLORER_SPINE.template.json` —
     `init·context·explore·spec·review·confirm·route`
   Crew plans use `skills/implementer/templates/IMPLEMENTER_PLAN.template.json`.
6. The second-file middles — a Commander's `execute.json`, an Admiral's `ADMIRAL_LOG.md` +
   `transitions/` — exist because **doctrine says so**, not because `amend` refused them.
   `scripts/verify_iterative_role_artifacts.py` does not reference `execute.json`.

## The question you are answering

**How should a role's plan declare which gates are frozen bookends, so the engine refuses to
amend them, while the middle stays freely mutable — for Admiral, Commander and crew alike?**

## Your named constraint

**DECLARE THE MUTABLE WINDOW ONCE, AT PLAN LEVEL. One new top-level key on the checklist names the mutable REGION of the plan (however you choose to express a region). Everything outside that region is frozen; everything inside is freely amendable. One declaration per plan, not one per gate. Make the region expression as simple as it can be while still handling all three role spines.**

This is *your* constraint and yours alone. Design the best possible candidate **under it**. Do
not hedge toward the other candidates; do not propose a menu. A candidate that abandons its own
constraint is a failed candidate.

## Hard requirements every candidate must satisfy

- **Backward compatible.** Every spine in flight today carries no bookend declaration — including
  the Admiral's live epic spine and the one this run is driving. An undeclared plan must behave
  **exactly** as it does at `9b38b9d9`.
- **The rail refuses, it does not remind.** `README.md`: a rail is "a script exit code or a
  required field that *refuses* rather than reminds." A bookend enforced only in prose is not a
  bookend.
- **Legible plan change.** "The plan changed, here's how" must be reconstructable after the fact.
  Prefer `cl["amendments"]` and the append-only `why_trail` over inventing a third record.
- **All three roles, one mechanism.** Not a Commander feature generalised later.
- **No new file.** `docs/agents/ORCHESTRATOR_CONTEXT.md` retires accumulating-advice files;
  the whole point of #634 is *fewer* files, not more.

## Required shape of your result

Write **only** to your result path. Use these headings exactly.

### 1. Candidate name and one-sentence summary
### 2. The mechanism
Concretely: what changes in `checklist_engine.py` (name the functions and roughly where), what
changes in the plan/template JSON shape, what changes at the MCP door, and what a role *does*
differently. Include the literal JSON fragment a spine template would carry.
### 3. Worked example
Show the Commander spine: which gates are frozen, which are the middle, and the exact `amend`
delta a Commander at `plan` would send to author `g1-implement`/`g1-review`/`g1-integrate` into
its own middle instead of into `execute.json`. Then show what the engine does when that same
Commander tries to `drop archive`.
### 4. How it lands for Admiral and for crew
Admiral: does the single `execute` gate grow one gate per wave, or are waves a different shape?
Answer, do not defer. Crew: same question for `IMPLEMENTER_PLAN.json`.
### 5. Attack your own candidate
**This section is scored hardest.** At least four genuine weaknesses. For each: the failure, how
it would show up in a real run, and whether it is fixable within your constraint or is a real
cost the human must accept. A candidate whose self-attack is soft is a worse deliverable than one
with fewer features. Include at minimum:
- what happens on an existing in-flight spine with no declaration;
- how someone could defeat your freeze without `--force`;
- what your mechanism costs an author who just wants a small plan;
- the migration cost of moving `execute.json` into the spine under your design.
### 6. Test surface
The specific tests that would prove it, named as `tests/<file>.py::<Class>::<test>`, including
the negative tests (what must be REFUSED) and the backward-compat test.
### 7. What you are NOT claiming
Scope limits of your own answer — what you did not check, what you assumed.

## Rules

- Read source before asserting. Cite `file:line`. Pin claims to `9b38b9d9`.
- Do **not** run the full test suite. Do not modify tracked files.
- Do **not** touch, and do not propose touching: `scripts/run_crew.py`,
  `scripts/install_constellation.py`, either `LAUNCH_ORDER.template.md`, or `map/INDEX.md`.
- **Never run a mutating engine verb against a live spine.** If you want to try `amend`, copy a
  spine to a temp directory first and drive the copy. `.agent-work/567-k/spine.json` and
  `.agent-work/epic-567-door/spine.json` are LIVE — read-only, always.
- An honest negative is a complete answer. If your constraint cannot satisfy a hard requirement,
  say so plainly with evidence rather than inventing a mechanism that does not work.
- Write your result file **before** ending your turn. That write is the delivery.
