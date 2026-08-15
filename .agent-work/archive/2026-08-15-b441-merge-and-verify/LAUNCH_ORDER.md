# Launch Order: `b441-merge-and-verify` — bring the new engine guard into #589 and find out what breaks

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

## Mission

PR #589 (`epic-568/441-binding-store`) is finished and was green **in isolation** — 3015 passed, 6
skipped, 0 failed. But it was measured against a `main` that no longer exists. Two PRs have landed since:

- **#587** `6947b15e` — `run_crew.py`: archive-verdict rescue, `verdict_source`, `door_bound`.
- **#588** `84ecee99` — `checklist_engine.py`: **the worktree-identity ruling.**

Merge `origin/main` into your branch and re-verify. **A green measured against a superseded baseline is
not evidence.**

## The interaction this lane exists to test — read this carefully

**#588 changed the engine to fail closed.** `origin_worktree_refusal` no longer compares by containment;
the call site resolves the cwd to its **git worktree toplevel** and compares by equality, and when **no
toplevel resolves at all**, a verb against an origin-carrying spine is **refused**.

Your headline test spawns 16 production claim writers out of a pytest tempdir:

```
proj = PosixPath('/tmp/pytest-of-tommy/pytest-668/test_spawn_binding_transaction0')
```

**A pytest tempdir is not a git repository, so no toplevel resolves there.** That is precisely the shape
the new guard refuses. Another lane already hit this exact interaction from the other side: #588's own
Commander found `tests/test_explorer_templates.py` building its fixture as a bare tempdir, and fixed the
**fixture** by adding `git init` so it was an honest repo — it did **not** weaken the guard.

So there are three possible outcomes, and I want you to distinguish them explicitly:

1. **Nothing breaks.** Your tests never drive an origin-carrying spine through the engine, so the guard
   never engages. Fine — say so, and say how you established it rather than just reporting green.
2. **A fixture is dishonest.** A test builds a bare tempdir where a real run would have a git worktree.
   **Fix the fixture** (`git init`), exactly as #588's lane did. This is in scope.
3. **The guard genuinely conflicts with what #441 must do.** If the binding store legitimately needs to
   operate where no git worktree exists, that is a **real design collision between two merged changes**,
   and it is **not yours to resolve**. **Stop and report** with the specific failing case.

**Under no circumstance weaken, bypass, or special-case the guard in `scripts/checklist_engine.py`.**
It is merged, it is not yours, and it is the answer to an Admiral ruling. Outcome 3 is a finding worth
far more than a green.

## The map conflict

Measured before this order was written — exactly one file conflicts:

```
$ git merge-tree --write-tree --name-only origin/main <your HEAD>
map/INDEX.md
CONFLICT (content): Merge conflict in map/INDEX.md
```

`map/INDEX.md` is **generated**. Do not hand-merge it, do not pick hunks. Resolve by regenerating:

```
git merge origin/main            # expect map/INDEX.md as the only conflict
python -m scripts.code_map build --root .
git add map/INDEX.md && git commit
```

`tests/test_code_map.py` reds on a stale map, so a correct regeneration is verifiable.
**If any file other than `map/INDEX.md` conflicts, stop and report.**

## Do not park — use this exact shape

Five Commanders today ended a turn saying they would "wait for" a backgrounded command. **Nothing will
wake you: your process exits when your turn ends.** The full suite takes ~2 minutes and the harness
auto-backgrounds anything that long. A launch-order warning alone has already been tried and failed, so
here is the mechanism instead — the `until` loop is one foreground command that does not return until the
result exists:

```bash
rm -f /tmp/b441-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/b441-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/b441-suite.log; do sleep 15; done
tail -20 /tmp/b441-suite.log
```

The `env -u` is not optional: your own spine lease exports those three vars and
`tests/test_mcp_identity.py:600` asserts they are absent, which manufactures a false failure. That has
cost two lanes today.

**Do not dispatch a crew.** Everything here is yours, in this turn.

## Pre-Rulings — settled

1. **`decision:guard-is-untouchable` — settled.** `scripts/checklist_engine.py` is merged and not yours.
   Fix fixtures, never the guard.
2. **`decision:regenerate-dont-handmerge` — settled.**
3. **`decision:content-is-final` — settled.** #589's binding-store implementation is complete and
   reviewed. Do not revisit the transaction design, the lock, the reap policy, or the identity rules.
4. **`decision:outcome-3-is-a-finding` — settled.** A genuine collision is reported, not resolved.

## File Ownership

**Yours:** `map/INDEX.md` (by regeneration), the merge commit, and — **only if outcome 2** — the specific
test fixtures in `tests/test_spine_rail.py` / `tests/test_gauge_writer.py` that need to be honest git
repos. Plus your work area.

**NOT yours:** `scripts/checklist_engine.py`, `scripts/run_crew.py`, `tests/test_spine_origin_isolation.py`,
`tests/test_explorer_templates.py`, `tests/test_mcp_identity.py`, `.mcp.json`, and every `episodes/` file
you did not author in this lane.

## Your own closeout episodes

They face the episode-observation guard, which reds the suite. Write them as **observations of what this
run did** — past tense, describing the run, not addressing a reader. In the `workaround` and
`proposed-remedy` kinds, **do not open a clause with a bare verb**; that is what flagged `Read`, `keep`
and `pass` in another lane today and cost a full dispatch. **Do not add anything to the exception list.**

## Evidence required

- The merge, with **only** `map/INDEX.md` conflicted, and the map regenerated rather than hand-edited.
- **An explicit statement of which outcome (1, 2, or 3) you observed, and the evidence for it.** This is
  the deliverable — more than the green.
- Clean-env cache-clean full suite: **0 failed.** The passed count will rise well above 3015 as #587's
  and #588's tests arrive; that rise is expected. Only failures matter.
- `tests/test_code_map.py` green.
- Push to `epic-568/441-binding-store`; confirm `gh pr view 589 --json mergeable` no longer reports
  `CONFLICTING`.

## Stop Conditions

- Any file other than `map/INDEX.md` conflicts.
- **Outcome 3** — a real collision between the guard and what the binding store must do.
- Green would require editing `scripts/checklist_engine.py` or anything else in the not-yours list.
- You find yourself about to dispatch, or to end your turn with something pending.

## Return Shape

What `spine_status` resolved to, named explicitly; the merge result and conflicted files; **the outcome
number and its evidence**; the clean-env suite summary line; whether the map moved; the commit SHA; and
#589's `mergeable` status after pushing.

**You are fenced from merging the PR.** The Admiral merges.
