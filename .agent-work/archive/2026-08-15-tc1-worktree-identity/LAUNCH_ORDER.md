# Launch Order: `tc1-worktree-identity` — worktree identity by git, compared by equality

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**
Three Commanders last epic refused instead of forcing, and every one of those refusals was worth more
than an advance would have been.

## Mission

Implement the Admiral ruling at

`/home/tommy/projects/constellation-skills/.agent-work/rulings/2026-08-15-worktree-identity.md`

**Read that document first and in full.** It is the authority for this lane, it is untracked and lives
in the **primary checkout** (your worktree does not contain it), and it already resolves the design
questions — you are implementing a decision, not making one.

In one line: `checklist_engine.origin_worktree_refusal` currently compares by **containment**
(`here.is_relative_to(root)`). Since worktrees began nesting at `<root>/.worktrees/<slug>`, every
worktree is inside the primary checkout, so a primary-stamped spine is drivable from inside **any**
worktree. Replace containment with **git worktree identity, compared by equality**.

## The three binding parts of the ruling

1. **Resolve at the single impure call site.** `scripts/checklist_engine.py:~3413` —
   `origin_refusal = origin_worktree_refusal(cl, cwd=engine_cwd, verb=args.verb)`. That site resolves
   `engine_cwd` to its **git worktree toplevel** before calling the predicate. It is the only call site
   in the engine; verified.
2. **The predicate stays pure and compares by equality.**
   `tests/test_spine_origin_isolation.py::test_it_is_pure` reads the function's compiled `co_names` and
   forbids `subprocess`, `run`, `getcwd`, `resolve`, `open`, `exists`, and more. **That test must stay
   green as written.** Do not weaken it, do not add your name to its forbidden list's exceptions. Keep
   the existing `os.path.normcase` folding — it exists because the two producers normalize differently
   (`spine_lifecycle` stores native separators, `init_work_area` stores `as_posix()`).
3. **Fail closed.** A spine that carries `origin.worktree` where no git toplevel resolves for the cwd is
   **refused**. Origin-less and malformed-origin spines keep the existing fallback and must still never
   raise — `tests/test_spine_origin_isolation.py::OriginRefusalFallback` enumerates those shapes.

## Why this works, so you can check my reasoning rather than trust it

Git already reports the **linked worktree** as toplevel, not the primary checkout. Measured on the live
tree before this order was written:

```
$ git rev-parse --show-toplevel      # from .worktrees/epic-568-441/.agent-work/epic-568-441
/home/tommy/projects/constellation-skills/.worktrees/epic-568-441
```

That is the entire fix. It also means **subdirectory work keeps working for free** — toplevel resolved
from `<worktree>/scripts` is `<worktree>`, so equality holds with no containment logic. Containment
existed only to buy that property.

If that measurement does not reproduce for you, **stop and report** — the ruling rests on it.

## The test migration — authorized, and the interesting part of this lane

Normally "an existing test's intent must change" is a stop condition. **Here it is explicitly
authorized**, in exactly one way, and the ruling says so.

`tests/test_spine_origin_isolation.py` asserts containment against **synthetic paths that are not real
directories and not git repos** — `/w/repo`, `/w/other`, `/w/repo-2`, `C:\W\REPO\scripts`. Under
equality, its subdirectory cases (`cwd="/w/repo/scripts"` → `None`) become wrong *at the predicate
level*, because the resolution that makes them right now happens above the predicate.

Those assertions **move up a level. They do not get deleted.** The property *"a subdirectory of my own
worktree is allowed"* must be re-asserted through `main()` against a **real temporary git repo**.
Predicate-level tests stay pure and synthetic and switch from containment to equality semantics.

**Losing that property from the suite is a failure of this lane. Moving it is the point.**
If you find yourself deleting a case rather than relocating it, stop and say so.

## Pre-Rulings — settled, do not relitigate

1. **`decision:git-not-lexical` — settled/human.** Options (a) engine-exports-cwd + `--from` and (b) a
   schema exemption flag are **rejected**. Both keep the check outside the engine, which is the property
   #577 correctly took away.
2. **`decision:forgery-stays-open` — settled/measured.** Anything that can `chdir` into the stamped
   worktree still passes. This is **accepted, not overlooked**, because
   `mcp_spine_server._standing_in_the_bound_spines_worktree` structurally depends on it: `spine_open`
   creates a new worktree and the next verb is `claim`, and no process can already stand in a directory
   that did not exist a moment ago. **Do not try to close this.** Do not remove or "improve" that
   contextmanager. Closing it needs an authenticated caller identity instead of an observed cwd — a
   separate design change, out of scope.
3. **`decision:no-migration` — settled.** `origin.worktree` values are immutable engine identity. **No
   rewriting, no backfill, no migration**, including the archived spine stamped
   `.worktrees/epic-568-codex-tier-routing`, a worktree that no longer exists. It is terminal; leave it.
4. **`decision:spine-rail-untouched` — settled.** See File Ownership.
5. **`decision:clear-caches-before-measuring` — settled.** A stale `.pyc` carrying a dead path
   fabricated a convincing phantom failure last epic and cost four falsifications to attribute.

## File Ownership

**Yours:** `scripts/checklist_engine.py` (the predicate and its one call site),
`tests/test_spine_origin_isolation.py`, your work area, plus any new test file you add.

**NOT yours — do not edit, for a reason:**
- `scripts/hooks/spine_rail.py` — **two** reasons. The ruling keeps its lexical derivation deliberately
  (an absolute claim path survives archival; git cannot answer for a deleted directory; and the hook runs
  on every tool call where a subprocess is a cost the engine's once-per-verb site does not pay). It is
  **also** the live target of in-flight work on #441 in a sibling worktree. A docstring edit here would
  collide for no gain.
- `scripts/mcp_spine_server.py` — specifically `_standing_in_the_bound_spines_worktree`. See pre-ruling 2.
- `.mcp.json`, and anything under `.worktrees/epic-568-441/`.

If the lexical/git split needs writing down somewhere, put it in **your findings**, not in code.

## The MCP door — verify before you mutate anything

This dispatch launches through the `cli` backend with `--spine`, which binds `SPINE_FILE` and an
assignment-keyed `SPINE_SESSION` into your process before your MCP servers start.

**`spine_status` must describe `tc1-worktree-identity`. If it resolves to any other spine — especially a
`f-424` demo spine — stop and report. Do not proceed and do not fall back.** A claim through a
demo-bound door mutates the wrong spine while looking like success. This bit a Commander last epic.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/tc1-worktree-identity`,
branch `tc1/worktree-identity`, based on `main` at `453f8492`. Yours alone.
Work area `.agent-work/tc1-worktree-identity/` **inside your worktree**.

Note the recursion: you are changing the guard that governs which worktree may drive a spine, **from
inside a nested worktree, driving a spine stamped to that worktree**. Your own spine's origin is
`/home/tommy/projects/constellation-skills/.worktrees/tc1-worktree-identity` and git agrees, so you
satisfy the new rule as well as the old one. **Confirm that before you change the engine** — if your own
spine would become undrivable by your own change, you have found something and must stop.

## Evidence required

- **Red before, green after**, over behavior: the nested-worktree case (primary-stamped spine, cwd inside
  a nested worktree) must **refuse** after your change and be shown to **pass** before it.
- The subdirectory property, re-asserted through `main()` against a real temporary git repo.
- `test_it_is_pure` green, **unmodified**.
- `OriginRefusalFallback` green — no origin shape raises.
- Full Linux suite, cache-clean. Clear first:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  **Baseline at `453f8492` is 3002 passed, 7 skipped, 0 failed, 1130 subtests passed** — measured
  cache-clean immediately before this dispatch.
- Regenerate the map: `python -m scripts.code_map build --root .` and commit if it moves
  (`tests/test_code_map.py` fails the suite when it is stale).

## Budget

One implementation. If it grows a second subsystem, that is a signal to stop and report, not to continue.

## Stop Conditions

- `spine_status` does not resolve to `tc1-worktree-identity`.
- The `git rev-parse --show-toplevel` measurement above does not reproduce.
- Green would require editing anything in the not-yours list, or weakening `test_it_is_pure`.
- A test case must be **deleted** rather than relocated.
- Your own spine would become undrivable by your own change.

## Return Shape

Report: what `spine_status` resolved to, **named explicitly**; what you changed; the red/green proof for
the nested-worktree case; where the subdirectory property now lives and how it is asserted; cache-clean
suite counts before and after; whether the map moved; and anything floated or recorded in findings.

**You may push your branch and open a PR** — your `archive` gate's postconditions require it.
**You are fenced from merging.** The Admiral merges, because the merge gate requires an independent
approval and a lane cannot approve itself. Say plainly in your report that the PR is open and unmerged.
