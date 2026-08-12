# Addendum to C2's launch order — hand this at the `plan.c3` float

Two things arrived after C2 was dispatched. Both change what the plan should contain, so they go to
the Commander at the plan-approval float rather than mid-gate.

## 1. A human directive: bind the worktree to the spine

Verbatim, 2026-08-11:

> *"we should mechanise worktree management at the start and end. worktrees and spines should be
> completely connected, there's no reason why those should be spawned separately."*

**The open half is now in C2's scope.** The generator does not just emit a spine file — one operation
creates the branch, the worktree, the scaffolded work area, the spine instantiated into it, and the
environment a crew needs (`SPINE_FILE`, `SPINE_SESSION`, `SPINE_PARENT`).

Grounding, so this is not taken on faith: `grep -rl "worktree add" scripts/ skills/` returns **two
verifiers** (`verify_worktree_isolation.py`, `verify_worktree_precondition_coverage.py`) and **three
prose mentions** (`LAUNCH_ORDER.template.md`, `fleet-doctrine.md`, `_shared/windows.md`). Nothing
provisions a worktree. It is hand-typed every time, and the spine is then created by a second,
unrelated command. Seven were provisioned that way in wave 5, and one dispatch landed in a worktree
cut before the `--parent` flag existed.

Required properties:

- **Refuse rather than half-succeed.** A worktree without a spine, or a spine without a worktree, is
  the state that produces mismatches. Roll back on failure.
- **The spine records where it was opened** — its worktree path and branch. This is what makes the
  close half possible without archaeology.
- **Never silently reuse a worktree another crew is in.** *"Never two crews in one worktree"* is
  currently prose in five places and enforced nowhere.
- **Verify your own result** with `verify_worktree_isolation.py` rather than trusting the `git`
  call returned 0.

**The close half is NOT yours** — terminal advance archiving the work area and reporting "ready to
PR" is a separate issue next wave. Do not build it. Do make the open half record what close will
need. Full spec: `.agent-work/epic-418-followon/context/lifecycle-spec.md` in the main checkout.

## 2. A correction: the CLI is still in the corpus, and two clauses assert a falsehood

The launch order told you the CLI was gone from agent-facing instruction. **That was wrong**, and the
Admiral carried the error forward without measuring. On your own base commit `0ab7ecab`:

- **15 explicit `CLI fallback` clauses across 11 files**
- **8 `<engine>` tokens across 4 orchestrator templates** — `ADMIRAL_SPINE` (2), `COMMANDER_SPINE`
  (3), `EXPLORER_SPINE` (2), `commander-core.md` (1)

Wave 5's N3 cleaned the crew-facing skills and left the orchestrator tier untouched.

Two of those clauses assert something wave 5 disproved. `skills/workbench/SKILL.md:37` and
`skills/workbench/references/checklist-engine.md:5` both call the CLI *"the only path for an
in-session dispatched crew member driving its own plan or survey."* A's cold reviewer dispatched a
real crew that drove its spine through the door with no handoff document, and N1 closed the verb gap
— the sentence is false in both halves.

**This is context, not an assignment.** The cleanup is held out of the wave precisely because those
four templates are the surface you were given latitude over, and a second crew would collide with
you. Your call, and either answer is fine:

- **take it** — say so, and it becomes yours exclusively; or
- **decline it** — say so, and it runs as its own issue after C2 merges.

What is *not* optional: **your generator must never emit a `<engine>` token or a CLI-fallback
clause.** A spine that tells its own driver to use the CLI is the defect your generator exists to
prevent.

## 3. A grade I got wrong — `notes-ride-in-existing-substrate` is not `settled/human`

Your problem statement carries `decision:notes-ride-in-existing-substrate` as `settled/human`. **I
graded that wrong, and the mistake could force you into a worse design.**

What the human actually said, verbatim:

> *"there should be plenty of room into a template for beliefs, highlighting concerns, posing open
> questions. it's just a matter of choosing the relevant gate to make those notes. hand off content
> should still be possible."*

That fixes the **requirement**, not the mechanism. Naming `constraints` and `directives` specifically
was **my inference**, not the human's instruction. Regraded:

- **`settled/human`** — every gate has room for beliefs, concerns and open questions; they render on
  the **active gate** where a crew will actually see them; and it is never a field the engine ignores.
  A crew must be able to hand content back at the relevant gate.
- **`guess/admiral`** — that `constraints` and `directives` are the right carriers.
  `settle:` your own reading of the two fields.

Your reading is already better than my inference was. You measured that all three populated
`constraints` instances mean *"rules this gate must respect"*, and that beliefs and open questions are
not rules — so overloading a field 970 tasks use for something else would be wrong. That is exactly
the argument I would want, and my grading forbade you from making it.

So: **if `directives` also turns out to be the wrong shape, you may propose a third answer.** The
constraint that stands is that the engine must *render* it on the active gate — a field
`checklist_engine.py` does not read is worse than no field, because it looks like it works. If your
answer needs a rendering change, that is a float to me, not a patch.

## 4. One factual correction to your map verdict

Your DEGRADED verdict is **right**, and for the right reason: there is no packet map. `map/ids.jsonl`
is genuinely empty (0 lines) and `docs/architecture/` does not exist.

But the supporting claim that `map/INDEX.md` is *"an unfilled template"* is wrong. On your base it is
**180 lines of populated code map** — packages, module counts, entity counts, one section per package
— regenerated at the C1 merge with `python -m scripts.code_map build`, and it already indexes
`scripts.validate_spine` and `tests.test_validate_spine`. It is not the packet map `map_orient` wants,
which is why the verdict stands, but it is a real artifact and a better substitute than several you
hash-pinned. Add it to your substitute set and correct the claim, so nothing downstream is built on
"there is no map at all" when what is true is "there is no *packet* map."

If you add modules, regenerate it: `python -m scripts.code_map build`.

## 5. Your sub-crews name me as their parent, not you

All six plan-stage crews are recorded with `parent: admiral-epic-418-followon`. That is wrong, and it
matters before the execute crews launch.

Traced: `parent` reaches the registry only from `args.parent` (`run_crew.py:1629` → `874`), with **no
environment fallback**. `_crew_door_env`'s docstring states the rule directly — a dispatching process
that is itself a crew already has its own `SPINE_PARENT` in `os.environ`, and *"that must never leak
to a child as the child's parent — it names the grandparent, not the dispatcher."* The guard works.
You passed your own parent down explicitly instead of naming yourself.

The human's ruling is *"crew should fail up ... I'd prefer it go one rung at a time."* As dispatched,
a sub-crew that blocked would have asked up two rungs, past the only tier that had briefed it and
straight to me — who does not have its handoff in context.

**Pass `--parent` naming your own session** on every crew from here:
`constellation/epic-559/c2-generate-the-spine/execute/commander`.

## 6. You never passed `--model`, so none of the six ran on Sonnet

`run_crew.py` records `model` only when set (`884`), and it is **absent on all six entries**, so
`--model` never reached the `claude` invocation (`603`). They ran at the inherited default tier.

`decision:sonnet-crews` is `settled/human` and verbatim: *"prefer sonnet crews."* Pass `--model
sonnet` on every implementer and reviewer. Escalate one to Opus only after a Sonnet crew has failed
the same task once, and say why.

The cost so far is bounded — the six were advisory alternatives and critics and are complete. The
execute crews are the expensive ones and have not launched. Fix it before they do.

### What both of these actually tell us — put it in your plan

Neither is a code defect. Both mechanisms exist, work, and are documented; you had the instruction in
your launch order and it did not get wired through. **That is this epic's thesis landing on a
Commander instead of an Admiral.** "Pass `--parent`" and "dispatch on Sonnet" are prose, and prose is
what keeps failing here.

The durable fix is not that the next Commander reads more carefully. It is that a dispatch which does
not name its parent and its model should be **refused**, the same way your generator refuses a spine
with a check that cannot fail. If your spec format covers how a spine's crews get dispatched, this
belongs in it. If it does not, say so and route it to me as a triage candidate — do not silently
widen your scope to fix `run_crew.py`.

## What I want to see in the plan you float

Beyond the gates themselves:

1. **Where the refusal lives.** `validate_spine.validate(spine: dict)` takes a dict and returns a
   `ValidationResult`, so the generator can validate in memory before anything touches disk. That is
   the shape I expect — refuse before writing, not lint after.
2. **Your answer on the open half** — is it one operation with the generator, or a separate call the
   generator invokes?
3. **Your answer on the `<engine>` cleanup** — take it or decline it.
4. **What your role spec asks its author to type.** If it is still a raw pytest invocation, say so
   now rather than at the return. The defect moving is a real outcome and I would rather plan around
   it than be surprised.
