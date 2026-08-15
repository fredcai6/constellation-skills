# Implementer Handoff: stop work-area manifests escaping their own tree

**Issued:** 2026-08-15 · **Requested by:** the human, directly. This handoff is the whole scope.

## The model you are protecting — read this first

A work area is **transportable work in progress**, not scratch. It lives at

```
<root>/.worktrees/<slug>/.agent-work/<work-id>/
```

inside the worktree, **tracked on that worktree's branch**. Pushing a worktree in progress is how a
fresh agent picks the work up and resumes it. It is deliberately *not* gitignored and *not*
disposable. `.worktrees/` appears in `.gitignore` only so the primary checkout does not list nested
checkouts as untracked noise; from inside a linked worktree its own `.agent-work/` is not ignored,
which is what makes it committable. Verified: the retained `epic-568-441` worktree currently carries
8,345 tracked `.agent-work` files on its branch.

Nothing about that layout changes in this task. You are fixing a bug that violates it.

## Task 1 — the escape (the real defect)

`scripts/episode_capture.py::manifest_root` ends with `return base.parent`. That fallback fires
whenever the checklist directory does not end in the work-id, and it climbs **out** of the tree,
writing a sibling of whatever directory it was handed. Nothing raises, so it happens in silence.

Reproduced exactly against the real functions, no mocking:

```python
import sys; sys.path.insert(0, "scripts")
import episode_capture as ec, context_manifest as cm
base = ".../constellation-skills/.worktrees/epic-568-510"   # a worktree root, not a work area
cm.manifest_path(ec.manifest_root(base, "probe"), "probe", "g1")
# -> .../constellation-skills/.worktrees/probe/context/g1.json
```

That predicted path **is** a real stray on disk. The same call shape reproduces the older pair under
the previous sibling layout, so one mechanism explains every stray found:

| `base_dir` handed in | work-id | lands at | on disk |
|---|---|---|---|
| `.worktrees/epic-568-510` | `probe` | `.worktrees/probe/context/g1.json` | yes |
| `.worktrees/epic-568-510` | `s`, `t` | `.worktrees/s`, `.worktrees/t` | yes |
| `constellation-skills-wt/epic-568-315` | `s`, `t` | `constellation-skills-wt/s`, `/t` | yes |

Each stray's own manifest records `roots.skill`, `roots.repo`, `roots.durable` and `host.cwd` **all**
pointing at the worktree it was generated from — while the file itself landed one level above that
worktree. **The record and the write disagree**, which is the sharpest statement of the bug.

**Fix the escape.** A work-area write must not land outside the work-area root it belongs to. Where
the root cannot be resolved with confidence, refuse loudly rather than silently guessing a parent —
this run's own evidence is that the silent guess produced four stray directories over six days and
nobody noticed until an unrelated audit.

Read `manifest_root`'s existing docstring before changing it. It is careful, it already anticipates
the non-conforming case, and it explains a real prior bug (a doubled `epic-418-followon/` path) that
the current shape exists to prevent. **Do not reintroduce that.** Your change must keep the nested
work-id strip working exactly as it does today.

## Task 2 — the docstring that caused a real error

`scripts/agent_work_root.py:7` describes each worktree's `.agent-work/` as
**"(gitignored, disposable)"**. Both halves are false: it is not gitignored (verify with
`git check-ignore`), and it is transportable work in progress, not disposable.

This is not cosmetic. That sentence is the reason a design was proposed that would have moved work
areas out of their worktree and gitignored them, destroying resumability. Correct it to describe what
the directory actually is. Keep the rest of the docstring's substance — the durable-root redirect and
the active-epic-lease exception are accurate and load-bearing.

## Scope — what is OUT

- The layout. `<root>/.worktrees/<slug>/.agent-work/<work-id>/` is correct and stays.
- `<root>/.agent-work/` at the primary checkout: tracked history and archives. The human has said the
  archives will likely be gitignored later; **do not act on that now** and do not build anything that
  depends on them being tracked.
- `durable_root`'s redirect semantics and its active-epic-lease exception.
- The lexical-vs-git spine ownership question, and `origin_worktree_refusal`'s containment predicate.
- The four existing stray directories (`.worktrees/s`, `/t`, `/probe`, and the pair under
  `constellation-skills-wt/`). **Leave them.** They are preserved evidence and the human has not asked
  for a cleanup. Removing them would also destroy your own regression's real-world reference.
- `.worktrees/epic-568-441` — a retained worktree with a live lease and blocked work. Do not touch.

## Evidence required

- **Red before, green after**, driven by the reproduction above: a test that a work-area write cannot
  land outside its work-area root. Use the real functions — the bug is in how two real functions
  compose, and a mocked test would not have caught it.
- A test that the existing nested work-id strip still resolves correctly
  (`epic-418-followon/commander-424` must not double).
- Full Linux suite, cache-clean. Clear caches first:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  Baseline on `main` at `bbbf41f6` is **3000 passed, 6 skipped, 0 failed**.
- Regenerate `map/INDEX.md` with `python -m scripts.code_map build --root .` and commit it if it moves.

## Anything interesting

Record what you are **not** fixing in `.agent-work/fix-work-area-escape/FINDINGS.md` rather than
widening the diff. One open lead: nothing yet explains *what* invoked the manifest tooling with
placeholder work-ids `s`, `t` and `probe` from inside the `epic-568-510` worktree. `probe` is stamped
`2026-08-15T00:30:32Z`, while an agent was live in that worktree. If you can identify the caller
cheaply, say so; if not, say that plainly rather than guessing.

## Workspace

Worktree `.worktrees/fix-work-area-escape`, branch `fix/work-area-escape`, based on `main` at
`bbbf41f6`. Yours alone. Work area `.agent-work/fix-work-area-escape/` **inside your worktree** — note
that the result path below is worktree-relative for exactly the reason this task exists.

No spine, no engine gates.

## Stop conditions

- A refusal cannot be added without breaking a legitimate existing caller.
- Green would require touching anything in the OUT list.
- The nested work-id strip cannot be preserved.

## Return shape

Report: what you changed; the red/green proof using the real functions; cache-clean suite counts
before and after; whether the map moved; and anything in `FINDINGS.md`.

**You are fenced from push, PR, and merge.** Commit locally and say so.
