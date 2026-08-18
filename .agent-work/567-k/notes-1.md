# Lane K working notes — #634 one spine per agent, frozen bookends, mutable middle

Read at `9b38b9d9`. Every line number below is pinned to that revision.

## understand — consolidated problem statement

### The order's assumed baseline, reconciled against the code

The launch order says gated plans can already be re-planned and the roles simply put their
middle elsewhere. **That is correct at source, and it is more correct than the order claims.**
Reconciling before planning (commander-core §delegated `understand`) changed the shape of the
gap twice.

`amend()` (`scripts/checklist_engine.py:2971`) on a GATED checklist already supports:

- `add` — insert a new pending gate, `after` an existing one (`:3047`)
- `drop` — remove a pending gate (`:3076`)
- `rescope` — overwrite title/imperative/pre+postconditions/constraints/directives (`:3089`)
- `retext-check` — correct a pending **or in-progress** gate's check text (`:3115`)

It is all-or-nothing (validated on copies, committed at `:3177`), requires a non-empty
`--reason` and `--authority`, and appends an audit entry to `cl["amendments"]` (`:3180`).
The MCP door already exposes it as `spine_amend`. So the *mutable middle* is built.

`_floor()` (`:3036`) is the freeze that exists today: **1 + the index of the last non-pending
gate**. A new gate may not be inserted below it (`:3068`).

### What is actually missing — and it is not what the title suggests

**Gap 1 (engine, real): the closing bookend is not frozen.** `_floor()` freezes only what has
*already been started*. A gate that is still `pending` is droppable and rescopeable, and every
role's closing bookend is pending for essentially the whole run. Concretely, at `9b38b9d9`
nothing stops a Commander standing at `execute` from amending away its own `archive`, or an
Admiral from dropping `closeout`. The engine's only notion of "frozen" is "already touched"
(`:2983`, `:3037`, `:3069`) — there is **no declared bookend** anywhere in the engine or in any
of the three spine templates. The human asked for "frozen required gates at the start and
finish"; the start half falls out of `_floor()` for free, and **the finish half does not exist.**

That asymmetry is the one genuine engine-level gap #634 names, and it is small.

**Gap 2 (doctrine, not capability): the middle lives in a second file.** A Commander authors
`execute.json`; an Admiral keeps waves in `ADMIRAL_LOG.md` + `transitions/`. Neither is there
because `amend` refused them. `amend` would have taken both. They are there because the
templates and the prose say so. `scripts/verify_iterative_role_artifacts.py` does **not**
reference `execute.json`, so nothing mechanical couples to the second file either.

This split matters for scope: gap 1 is mine to build; gap 2 is a doctrine migration whose
convergence the order reserves to the human (`decision:design-it-twice`).

### Local unknown #1, answered: what `spine_advance --from_child` is for

Read at `checklist_engine.py:2617-2645` and `tests/test_checklist_engine.py:429-471`.

`--from-child` reads a child checklist file's `consolidation` key and attaches it to the parent
gate as `review-result` evidence *before* the postcondition check runs. `consolidate()`
(`:2733`) refuses anything that is not a **survey** (`:2734`), and a survey is the reviewer's
work file. The test fixture (`_review_gate`, `:430`) is a parent gate carrying
`child_checklist` and an artifact postcondition matching `{"verdict": "APPROVE"}`.

So: **`from_child` is a cross-agent verdict seam.** It exists so a *different* agent's finished
survey — a reviewer's — can satisfy a parent gate's `review-result` postcondition without the
parent re-typing the verdict. `test_advance_from_child_block_refuses` (`:456`) proves the
intent: on BLOCK the advance is refused **but the evidence is still attached**, so the parent
cannot launder a rejection into a pass.

**It is not a workaround for gated-can't-grow.** It carries evidence *up*; it never lets a
parent drive a child's gates. It therefore **survives this change untouched**, and it
constrains the design: "one spine per agent" must mean *one agent drives one spine*, not *no
spine may reference another*. The sanctioned cross-spine reference is evidence flowing upward,
and `from_child` is it. My scope does not include removing or reshaping it.

### Constraints carried into planning

- Bookends stay fixed; only the middle moves (`decision:frozen-means-frozen`).
- Build for Admiral, Commander **and** crew (`decision:every-planning-role`).
- Prefer `amend`'s authority + the append-only `why_trail` over a third record
  (`decision:plan-change-is-legible`).
- N>=2 candidates, **do not converge** (`decision:design-it-twice`).
- Self-hosting: read-only on the live spine, mutating verbs only against a **copy**.
- Engine-under-edit is not engine-in-play: validate in a fresh process with explicit paths.
- `map/INDEX.md` is Admiral-owned; `run_crew.py` / installer / LAUNCH_ORDER templates are lane J.

### Map confidence

**Degraded, declared.** This repo has no architecture map: no `docs/architecture/` packets, a
0-byte `map/ids.jsonl`, and a `map/INDEX.md` whose per-module links do not resolve. Receipt at
`.agent-work/567-k/map-orientation.json` with three hash-pinned substitutes. The structural
frame above is built from source and tests and is declared as such. `map/INDEX.md` is fenced to
the Admiral, so I do not repair it.

### Out of scope

Removing `from_child`; `run_crew.py`, the installer and the LAUNCH_ORDER templates (lane J);
`map/INDEX.md`; filing any issue; promoting anything into `docs/agents/*`.

### Open scope question for the Admiral (carried to `plan`)

`skills/commander/templates/EXECUTE_PLAN.template.json` and the Commander/Admiral prose that
tells a role to keep its middle in a second file fall in **neither** my ownership list nor lane
J's fence. Under gap 2 they are exactly what a full migration would rewrite. Flagged here;
disposition decided at `plan`.
