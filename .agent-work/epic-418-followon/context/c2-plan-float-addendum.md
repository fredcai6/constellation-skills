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
