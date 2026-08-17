# Implementer Handoff — g2: bind the door to an existing spine

## Gate
`g2-implement` (epic-567-door/cmdr-a, lane A of epic #567)

Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`
Branch: `feat/567-a-spine-identity`. Use absolute paths — **the shell's working
directory does not persist between tool calls in this harness.**

## Task

Add one MCP door tool, `spine_bind`, that binds this door process to a spine file
that **already exists**, so an agent whose door was launched with no `SPINE_FILE`
can drive its own spine through the door instead of falling back to the CLI.

The full design is in
`.agent-work/epic-567-door/cmdr-a/DESIGN_CONVERGENCE.md` (read it first) and its
source candidate is `crew-handoffs/CANDIDATE_A_minimal-interface.md` (read it
second — it carries the refusal texts and line numbers). **Where the two disagree,
`DESIGN_CONVERGENCE.md` wins**: it corrects the candidate's session derivation, and
that correction is the point of the gate.

### The one correction, and why it is load-bearing

Candidate A derives the session from the spine's stamped `origin.work_id`. Measured
over the live population (52 spine-shaped files under `.agent-work/` and
`.worktrees/*/.agent-work/`, excluding `archive/` and `templates/`):

| | count |
|---|---|
| carrying `origin.work_id` | **4** |
| no origin, but top-level `work_id` | **48** |
| neither | **0** |

Deriving from `origin.work_id` alone refuses 92% of real spines, including
`.agent-work/epic-567-door/spine.json` (the Admiral's own live spine) and
`.agent-work/implementer-315-native-g1/IMPLEMENTER_PLAN.json` — the two cases the
mission exists for.

**So: derive the work id as `origin.work_id` when present, else the spine's
top-level `work_id`.** Refuse only when neither is present.

Re-derive the census yourself before you start; do not take the numbers on trust.

## AMENDMENT after the cold plan critic — read this before the sections below

A cold critic reviewed the design and found five blocking defects. Three change your
task. Where this amendment and any later section disagree, **this amendment wins.**

### A1 — The containment root is NARROWER than the design document says

`DESIGN_CONVERGENCE.md` names `_primary_checkout_for_lifecycle()` (`:797`) as the
root. **Do not use it.** That function resolves `git rev-parse --git-common-dir`,
which jumps to the **primary** checkout from any worktree — and `.worktrees/` nests
*inside* the primary checkout, so that root admits every other lane's checkout.
Measured in this tree:

| root | spine-shaped files with a `work_id` | with an active lease |
|---|---|---|
| `_primary_checkout_for_lifecycle()` (as designed) | **4205** | 307 |
| of those, inside other lanes' `.worktrees/` | **3505** | — |
| `<the door's own checkout>/.agent-work/` (**use this**) | **683** | 51 |

The design killed candidate C for a 683-file root and then crowned a 4205-file one
without printing the number. **Use the narrow root:**

- Derive the door's own checkout with `git rev-parse --show-toplevel` from the door
  script's own directory (`Path(__file__).resolve().parent`) when nothing is bound,
  and from `SPINE.parent` when something is. **`--show-toplevel`, not
  `--git-common-dir`** — that one flag is the whole difference between "my checkout"
  and "the primary checkout and every worktree under it".
- Confine the candidate to `<that toplevel>/.agent-work/`.
- **Additionally refuse any candidate whose own `git rev-parse --show-toplevel`
  differs from the door's own.** This is what makes the isolation claim true rather
  than aspirational, and the module already has a `_git_rev_parse` helper.

The resulting property, which you should put in the tool description: **one
checkout's work-area tree per process.**

### A2 — One design claim was false and the narrow root is what makes it true

`DESIGN_CONVERGENCE.md` says, 18 lines apart, both "including a sibling worktree's
live spine may become the spine this process drives" **and** "what an agent still
cannot do: drive a spine in another checkout." A linked worktree *is* another
checkout, so the second was false. A1's root and its cross-checkout refusal make the
second sentence true. That is the point of A1 — not tidiness.

### A3 — Two obligations were stated only in prose; they are now yours explicitly

The critic found `grep -c "IDENTITY_TRADE" execute.json` → **0**. An obligation
stated only in a document you are not required to satisfy is not an obligation. So,
required deliverables, each of which must appear in your diff:

1. **The `IDENTITY_TRADE.md` amendment.** The pin's own failure message
   (`tests/test_mcp_identity.py:832-836`) says: "If the identity trade was
   deliberately re-opened, update ... IDENTITY_TRADE.md in the same change — this
   test exists so that cannot happen silently." Find that file under
   `.agent-work/archive/` and add a section recording what changed and the new
   measured reach from A1.
2. **The pin exemption must be keyed on `(tool, property)`, not on the tool alone.**
   Add a test asserting that a hypothetical `spine_bind.session_id` property would
   **still** be an offender. A tool-wide skip would let a future identity argument
   through unseen.
3. **`tests/test_mcp_identity.py`'s positive control currently reimplements the
   detector loop inline** (`:845-853`) instead of calling it, so the moment the real
   pin gains an exemption the control silently stops controlling for it. **Extract
   the detector into one module-level function called by both the pin and its
   control.** Without this, the exemption you add is unguarded by construction.

### A4 — Do not rename the argument to dodge the pin

Stated in Authority already, restated here because it is the cheap wrong answer:
the argument is `spine_file`. Renaming it to `work_file`/`plan_path` passes the pin
and is the spelling game `_identity_violation`'s docstring records losing six times.

## Protected Intent

Violating any of these fails the gate regardless of test results.

- **One spine per process.** `decision:one-spine-per-process-stands`. You may change
  *when* the binding is decided. You may not let a process drive two spines.
- **`_bind_process_to` stays the only identity mutator.** Your new dispatch function
  must assign neither `SPINE` nor `SESSION`; it calls `_bind_process_to` and lets
  that function do it. A module-wide AST pin
  (`tests/test_mcp_lifecycle.py:563`) asserts the assigning scopes are exactly
  `{<module>, _bind_process_to}` and will catch you.
- **`_identity_violation` is not to be re-specified.** It compares argv against
  `SPINE` at call time, so it follows a binding change for free. Leave its
  semantics alone.
- **Fail closed.** A spine that cannot be identified refuses. Never resolve a
  binding from the process cwd or any ambient state — `_spine_from_env`'s docstring
  (`scripts/mcp_spine_server.py:156`) records that `Path("").resolve()` once
  "silently bound the door to whatever directory it was standing in", and removing
  that was a deliberate act.
- **Both identity roots move together or not at all.** Binding a spine without a
  session yields a door that cannot `claim`, which is not a bound door.

## Test Mode

**TDD required.** Every refusal is a pure function of `(args, SPINE, filesystem)`
and independently reachable, so there is no excuse for writing them untested. Write
the failing test, then the code.

## Close Criteria

Prove each.

- `spine_bind` exists in the tool surface, and a door launched with **no**
  `SPINE_FILE` can call it and afterwards successfully run a read-only verb
  (`spine_status`) against the bound spine.
- **The two-door round trip**: door 1 mints work with `spine_open`; door 2, launched
  unbound, binds the same spine with `spine_bind` and drives it. Assert that door
  2's resulting `SPINE`/`SESSION` are byte-identical to what door 1 was bound to.
  This is the load-bearing test — it is the only one that measures "bound by
  binding" and "bound at launch" being the same thing.
- **The reach-delta negative test**: a spine file outside the containment root is
  **refused**, and the refusal names the boundary. Required by
  `decision:isolation-not-fencing`; a green suite is not a substitute.
- Binding the already-bound spine twice is an idempotent success, not a refusal.
  Order the check **before** `_rebind_refusal`, or an agent that binds, claims, then
  re-binds the same path gets refused for rebinding to where it already is.
- A spine carrying **neither** `origin.work_id` nor a top-level `work_id` refuses,
  and the refusal explains that a door bound with no session cannot `claim`.
- The three AST pins in `tests/test_mcp_lifecycle.py` and the identity-arg pin in
  `tests/test_mcp_identity.py` all pass, **and their positive controls still fail on
  planted regressions.** State that you checked the controls, not just the pins.

## Allowed Scope

- `scripts/mcp_spine_server.py`
- `scripts/spine_lifecycle.py` — only to extract `session_id_for(work_id)` and have
  `open_work` (`:357`) call it.
- `tests/test_mcp_lifecycle.py`, `tests/test_mcp_identity.py`,
  `tests/test_mcp_door_unbound.py`, and a new test module if you want one.
- `.agent-work/archive/2026-08-12-epic-418-followon-closeout/.../IDENTITY_TRADE.md`
  — the amendment described below.

Pre-authorized: the two pin edits named under "Authority". Reconciling those two
test files is expected work, not an out-of-scope breach.

## Specific Exclusions

- **`scripts/checklist_engine.py` — owned by gate `g3` this same wave (#613's
  atomicity half). Do not touch it.** Another crew is editing it in parallel.
- **`scripts/hooks/*` — out of scope for the whole lane (#567 lane A).** Hooks
  execute from the main checkout for every live session; editing them can break
  other running agents. Read them for patterns if useful; write nothing.
- `scripts/run_crew.py`'s launch-time `--spine` env-pair binding. It stays. It is
  better than this path when it is available.
- Do not delete or rename `SPINE_FILE` / `SPINE_SESSION` support.

## Constraints

- New refusals follow the module's established voice: **name the problem, then name
  the remedy.** Read `_unbound_refusal` (`:393`), `_identity_violation` (`:443`) and
  `_rebind_refusal` (`:920`) and match them. Each refusal returns through
  `_tool_error` with a `rejection_class` so it lands in the rejection log.
- Reuse, do not reinvent: `_resolve_confined` for containment (it already takes a
  `bound_dir` parameter and `_spine_open` already passes a different root),
  `_primary_checkout_for_lifecycle()` for the root, `checklist_engine._active_lease`
  and `_is_stale` for "is this identity live". Do not define a second notion of any
  of these — that is the exact failure `_identity_violation`'s docstring records six
  times over.
- Extract `_unbound_refusal`'s five-input usability ladder into a helper both it and
  `spine_bind` call, rather than writing a second ladder with drifting wording.
- **`spine_bind` must be added to `BINDS_WITHOUT_A_BOUND_SPINE` (`:1425`)** or
  `main()`'s uniform unbound gate (`:1723`) refuses it before your dispatch is ever
  reached — a bind tool that only works on an already-bound door.
- The argument is named **`spine_file`**. Do **not** rename it to `work_file` or
  `plan_path` to slip past the identity-arg pin. See Authority.

## Map Anchors (inbound)

- **Map entry point:** none — map orientation is `DEGRADED-UNPARSEABLE` repo-wide
  (`map/ids.jsonl` is tracked and 0 bytes). Start from
  `.agent-work/epic-567-door/cmdr-a/MISSION_FRAME.md` and this handoff; do not go
  looking for a map packet, there is none.
- **Structural:** `scripts/mcp_spine_server.py` — `_bind_process_to`(:878),
  `_unbound_refusal`(:393), `_rebind_refusal`(:920), `_identity_violation`(:443),
  `_resolve_confined`(:~330-380), `_primary_checkout_for_lifecycle`(:~797-861),
  `BINDS_WITHOUT_A_BOUND_SPINE`(:1425), `LIFECYCLE_TOOLS`(:1368),
  `call_lifecycle_tool`(:1067), `main()`'s unbound gate(:1723).
- **Capability:** door-binding — how the door decides which spine it drives.
- **Constraints/assumptions:** `constraint:ast-pin-on-identity-assignment`;
  `constraint:lifecycle-return-pin`; `constraint:fail-closed-binding`.
- **Decision anchors:**
  - `decision:one-spine-per-process-stands` — one process, one spine.
    `@grade: settled/inherited · leans g2-implement`
  - `decision:isolation-not-fencing` — name the replacement isolation property and the reach delta.
    `@grade: guess/admiral · leans g2-implement,g2-review · settle: name the property in the design doc and have the reviewer attack it`
  - `decision:bind-on-open-over-new-verb` — binding may be decided after launch; this gate extends the same idea.
    `@grade: settled/measured · leans g2-implement`
- **Evidence expectations:** the two-door round trip; the reach-delta negative test.
- **Map confidence flags:** the whole map is degraded. Trust code and tests, not
  any map claim.

## Deliverable Path Check

- **Committed** — `scripts/mcp_spine_server.py`, `scripts/spine_lifecycle.py`,
  `tests/test_mcp_*.py`. `git check-ignore` on each exits 1 (not ignored); the
  commander verified before dispatch.
- **Committed** — your `IMPLEMENTER_RESULT` under
  `.agent-work/epic-567-door/cmdr-a/crew-handoffs/`. Note: **`.agent-work/` is NOT
  gitignored in this repo** — `git check-ignore .agent-work/x` exits 1. Measured, not
  assumed; the Commander's first draft of this handoff asserted it was ignored and
  that was wrong. Your result file will appear in the diff, so write it as something
  a reviewer is meant to read.
- Any **new** test module is untracked until staged: `git diff` will show one fewer
  file than you changed, and the new one appears in `git status`.

## Required Evidence

**Load-bearing — prove rigorously:**

1. The two-door round trip, with pasted output.
2. The reach-delta negative test: the refusal text, quoted, naming the boundary.
3. The AST pins pass **and** their positive controls still fail. Paste both.
4. Your own re-derivation of the `work_id` census.

**Confirmatory — a spot-check suffices:** the remaining refusals, the idempotency
case, and the full door suite green.

## Wiring Grep

Required. For each symbol you add, show a call site outside its own definition:

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
grep -rn "_spine_bind\|session_id_for\|_unusable_spine_reason" --include=*.py . \
  | grep -v "^\./\.agent-work" | grep -v "def _spine_bind" \
  | grep -v "def session_id_for" | grep -v "def _unusable_spine_reason"
```

**State the count of call sites found for each symbol. Zero external call sites for
any of them is a stop condition, not a note** — a `spine_bind` that is never routed
from `call_lifecycle_tool`, or a `session_id_for` that `open_work` does not call, is
shipped-inert: it passes review, passes tests, and nothing reaches it.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
  py -m pytest tests/test_mcp_lifecycle.py tests/test_mcp_identity.py \
                tests/test_mcp_door_unbound.py tests/test_mcp_spine_server.py -q
```

Then the full suite, to catch fan-out:

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
  py -m pytest tests/ -q 2>&1 | tail -25
```

If anything outside the door/identity suites goes red, that is a **stop condition** —
report it, do not fix it. `scripts/checklist_engine.py` is being edited in parallel
by another crew, so an engine-suite failure is probably not yours.

## Suggested Model Tier

**Stronger.** This is a security boundary with seven previously-defeated guards
around it and three AST pins constraining the shape.

## Authority

Already decided; do not re-litigate:

- The design is the named hybrid in `DESIGN_CONVERGENCE.md`. The Commander converged
  it from a three-candidate panel. **The human has not yet ratified it**
  (`decision:convergence-is-human-only`), so keep the change cleanly revertible: put
  the `spine_bind` addition in its own commit, separate from the
  `session_id_for` extraction.
- **`tests/test_mcp_lifecycle.py:135`** — `ALLOWED` grows from
  `{"_spine_open", "_spine_close"}` to include your new dispatch function's name.
  This is **widening an allow-list, not loosening a ban**: the pin forbids
  `call_lifecycle_tool` from producing content any way other than delegating to a
  named dispatch function, and a third named function preserves that exactly. Its
  own failure message tells you to do this. **The positive control at `:156` must
  stay untouched and must still fail** — if it goes green you weakened something.
- **`tests/test_mcp_identity.py:817`** will fail on `spine_bind.spine_file`, by
  design; that property is literally the pin's own positive control. Fix it with a
  **tool-scoped** exemption (so `spine_advance.spine_file` would still be an
  offender) **plus** an `IDENTITY_TRADE.md` amendment in the same change. The pin's
  failure message demands exactly this pairing "so that cannot happen silently."
  **Renaming the argument to dodge the pin is forbidden** — that is the spelling
  game `_identity_violation` records losing six times.

**You must not decide alone:** any widening of the containment root beyond "this
door's own checkout"; making the session a caller-supplied argument
(`IDENTITY_TRADE.md` §3 Option B settled that it buys nothing); anything that
touches `_identity_violation`'s comparison semantics. Stop and report instead.

## Stop Conditions

Stop and return with what you have if: the containment root cannot be resolved for
a real case you need; the identity-arg pin cannot be satisfied tool-scoped without
weakening it globally; a test outside the door/identity suites goes red; you find
that binding an existing spine cannot be made safe without adding more mechanism
than the design allows. **A measured negative on the stated question is a complete,
successful deliverable** — report it with the same rigor as a win.

## Return Format

Write `IMPLEMENTER_RESULT` to
`.agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-implement-implementer-result.md`
**before ending your turn** — that write is the delivery. Include a
`Return status:` line whose value is exactly `complete` (lowercase) when the gate's
close criteria are met, and a `Workflow Feedback` section on how the run went.
