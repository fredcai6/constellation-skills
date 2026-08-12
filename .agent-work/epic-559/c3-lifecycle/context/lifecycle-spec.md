# The work lifecycle is one thing, and it is currently three

**Author:** Admiral · **Date:** 2026-08-11 · **Authority:** the human's directive of 2026-08-11,
verbatim: *"we should mechanise worktree management at the start and end. worktrees and spines should
be completely connected, there's no reason why those should be spawned separately. also the archiving
step usually requires a little bit of a shell game, especially since the last step involves closing
out the spine. I think that spine close out is where we can automate moving everything to archive and
the last step will say 'we're good to PR!' effectively"*

## The measurement

Nothing in this corpus provisions a worktree. `grep -rl "worktree add" scripts/ skills/` returns:

| file | what it is |
|---|---|
| `scripts/verify_worktree_isolation.py` | verifier — checks after the fact |
| `scripts/verify_worktree_precondition_coverage.py` | verifier — checks after the fact |
| `skills/admiral/templates/LAUNCH_ORDER.template.md` | prose |
| `skills/admiral/references/fleet-doctrine.md` | prose |
| `skills/_shared/windows.md` | prose |

Two checks and three paragraphs. **The act itself is unautomated**, so it is typed by hand every
time, and the spine is then created by a second, unrelated command (`init_work_area.py --root .`).
Seven worktrees were provisioned that way in this epic's wave 5 alone.

This is the epic's own thesis pointed at the Admiral's hands: an act that only exists as prose gets
performed by whoever reads the prose, at whatever fidelity they manage that day.

## Why the archive step is a shell game

It is not incidental fiddliness. It follows from the split.

Because creation is manual, close has to **rediscover** what creation did: which worktree, which
branch, and where `.agent-work` actually landed. That last one is genuinely hard — `durable_root()`
(`scripts/agent_work_root.py:110`) returns the **main** checkout root for a linked worktree, except
that while an Admiral epic lease is held it deliberately returns the **worktree** root instead,
because the main checkout is fenced read-only. So the same path resolves to two different places
depending on run state, and the close step has to know which.

Bind creation to the spine and none of that needs discovering: the spine records where it was opened,
and close reads it.

## The hazard any implementation must sequence around

**Closeout moves the work area that contains the spine driving the closeout.** The spine file, its
`.journal`, and the lease all live under `.agent-work/<work-id>/`. Move that directory naively and the
engine loses the file it is mid-operation on.

Required order:

1. satisfy the closeout gate's postconditions
2. **final `advance`** on the closeout gate — this is what marks the spine done
3. **`release`** the lease — must come after the closing advance, never before, or the journal
   carries entries after the lease release and the terminal provenance check fails
4. **then** move the work area to `.agent-work/archive/<work-id>/`, spine file **last**
5. commit the move
6. report readiness

Steps 2 and 3 are already doctrine and already get fumbled. Steps 4–6 are what this proposal
mechanizes.

## The two mechanisms

### Open — one operation creates the spine and its worktree

One call takes a work id and a spec, and produces: the branch, the worktree, the scaffolded work
area, the spine instantiated into it, and the environment binding a crew needs (`SPINE_FILE`,
`SPINE_SESSION`, `SPINE_PARENT`). It **verifies its own result** with the isolation verifier that
already exists rather than trusting that it worked.

Properties:

- **Refuses rather than half-succeeds.** A partial open — worktree without spine, or spine without
  worktree — is the state that produces the mismatches. Roll back on failure.
- **Records where it opened.** The spine carries its own worktree path and branch, so close needs no
  archaeology and `durable_root`'s two-answer behaviour stops being the close step's problem.
- **Idempotent on an existing work id**, or refuses with a legible reason. Never silently reuses a
  worktree another crew is in — *"never two crews in one worktree"* is currently prose in five
  places and enforced nowhere.
- **Reachable through the door** (the human's standing ruling: anything wanted for the spine is
  reachable via MCP). This is C3's territory and lands with it.

**Owner: C2.** It is building the thing that spawns spines. Adding the worktree now is cheap; adding
it after the spec format ships means changing the format.

### Close — the terminal advance archives, and says it is ready

When the closeout gate advances and the lease releases, the same operation:

- moves `.agent-work/<work-id>/` to `.agent-work/archive/<work-id>/`, spine last;
- stages **by name** — `.agent-work/` is tracked in this repo and `git add -A` is forbidden;
- commits the move;
- prints a readiness verdict naming the branch, the commit, and what remains: **"ready to PR."**

**What close does NOT do**, deliberately:

- **It does not open the PR.** Outward-facing acts stay explicit.
- **It does not remove the worktree.** Deleting a directory is not something a terminal advance
  should do as a side effect. `git worktree remove` stays a separate, named step.
- **It does not decide the work was good.** Terminal means driven to the end, not approved.

**Owner: a new issue, next wave.** It touches terminal engine behaviour and git. Folding it into C2
would blow C2's appetite, and it wants its own control: a spine driven to terminal in a scratch repo,
archived, with the engine still able to read the archived spine afterward.

## What this subsumes

The closeout **harvest** step exists to rescue a worktree-local `CONSTELLATION_FEEDBACK.md` before
`git worktree remove` destroys it. Measured on 2026-08-11 across all 20 worktrees: **not one carries
an untracked export.** Every crew in this epic wrote its feedback into a result artifact, which is
committed and survives. The step guards a path nobody uses, and it is the reason worktrees are still
standing.

A mechanized close does not need to guess: it created the work area, so it knows what is in it. The
harvest becomes "archive everything under the work area", which is correct whether or not a crew
exported anything.
