# Ruling: worktree identity is derived from git, compared by equality

**Issued:** 2026-08-15 · **By:** Admiral (post-epic-568) · **Authority:** the human, directly, on
2026-08-15 ("c is cool").

**Resolves:** the `authority_needed: admiral` blocker on `commander-315`'s `plan` gate, open since
2026-08-13. **Closes:** tc1 (containment predicate), recorded at epic 568 closeout.

---

## The question that was asked

`commander-315` blocked its own `plan` gate rather than ship, and escalated:

> Forcing a command check's cwd disarms the shipped worktree-isolation gate:
> `verify_worktree_isolation.py --here` reads the ambient cwd as the SUBJECT of the check, so with cwd
> set to the spine's enclosing repo root the comparison becomes tautological. Proven through the real
> engine path — unmodified engine REFUSES a wrong-worktree launcher, naive-fix engine ADVANCES it.

It offered the Admiral two options: **(a)** the engine exports the launcher cwd into the check
environment and `verify_worktree_isolation.py` gains an explicit `--from`; or **(b)** a schema flag
marks environment-observing checks exempt.

That escalation was never adjudicated. PR #577 shipped a **third** answer without ruling against the
question: it moved the check out of the spine entirely and into the engine as
`checklist_engine.origin_worktree_refusal`, comparing an `origin.worktree` stamped at creation.

## What #577 actually settled, and what it left open

#577 settled the half #315 was really complaining about — **who is the subject, and who can turn the
check off**. A check wired into a spine's own text can be edited by the spine's author; an engine-native
guard cannot. Its docstring is careful to claim only that:

> It does NOT make the comparison unforgeable. The engine reads its ambient cwd, so a check command
> authored as `cd <origin.worktree> && ...` still satisfies it. That claim was withdrawn deliberately;
> do not restate it.

So after #577 the guard has coverage and unbypassability, but the comparison itself is still
`here.is_relative_to(root)` — **containment, not identity**.

## Why containment stopped being safe

Containment was a correct choice when it was made, for a real reason: you must be able to drive the
engine from a subdirectory of your own worktree.

PR #585 then made worktrees nest at `<root>/.worktrees/<slug>`. That was also correct — it is why
worktrees are now tidy and ignorable.

Together they void the guarantee. **Every worktree is now literally inside the primary checkout path**,
so a spine stamped with the primary checkout passes from inside any worktree. Measured on the live tree:

| spine stamped with the primary checkout, driven from | result |
|---|---|
| inside a nested worktree — **the default layout since #585** | **ALLOWED** ← should refuse |
| the old sibling layout (`<root>-wt/<slug>`) | REFUSED |
| the stamped worktree itself (control) | ALLOWED |

Under the sibling layout this applied to no worktree. It now applies to all of them. Neither decision
was wrong; the interaction is what is wrong, and the interaction was introduced by this Admiral in #585.

## The ruling

**Worktree identity is what git says it is, and the comparison is equality.**

(a) and (b) are both **rejected**. Both keep the check outside the engine, which is the property #577
correctly took away. This ruling completes #577 rather than reopening it.

Three parts, all binding:

### 1. Resolve the cwd to a git worktree toplevel, at the single impure call site

`checklist_engine.py` has exactly one call site — line ~3413:

```python
origin_refusal = origin_worktree_refusal(cl, cwd=engine_cwd, verb=args.verb)
```

That site resolves `engine_cwd` to its **git worktree toplevel** before handing it to the predicate.
Git already answers this correctly for linked worktrees; measured on the live tree:

```
$ git rev-parse --show-toplevel   # run from .worktrees/epic-568-441/.agent-work/epic-568-441
/home/tommy/projects/constellation-skills/.worktrees/epic-568-441
```

It reports the **linked worktree**, not the primary checkout. That is the whole fix.

### 2. The predicate stays pure, and compares by equality

`tests/test_spine_origin_isolation.py::test_it_is_pure` is a deliberate, shipped invariant:

> No filesystem, no clock, no subprocess, no ambient cwd read: the impure half lives at the one call
> site in `main()`.

**That invariant is upheld, not traded away.** The predicate keeps its pure refusal-or-`None` shape and
its normcase folding; only its comparison changes from `is_relative_to` to equality. All impurity —
the git call — lives at the call site, which is already the impure half.

This is why subdirectory work keeps working **for free**: toplevel resolved from `<worktree>/scripts` is
`<worktree>`, so equality holds without any containment logic. Containment existed to buy that
property; git gives it away.

### 3. Fail closed

If a spine carries an `origin.worktree` stamp and no git toplevel can be resolved for the cwd, the verb
is **refused**. Today an unresolvable cwd fails closed only by accident (it fails the containment test);
under equality it must fail closed by intent. Origin-less and malformed-origin spines keep their
existing fallback and must still never raise.

## What this ruling does NOT fix, stated plainly

**The forgery hole stays open, and is now accepted rather than quietly withdrawn.**

Anything that can `chdir` into the stamped worktree still passes, exactly as #577's docstring warned.
This is not an oversight, and it is not closable at this layer, because **the MCP door depends on it**.
`mcp_spine_server._standing_in_the_bound_spines_worktree` physically stands in the bound spine's
worktree for the length of one engine call, and its docstring explains why that is structural:

> The structural case is `spine_open`, which creates a NEW worktree and stamps `origin.worktree` to it;
> the next verb on that spine is `claim`, and a process cannot already be standing inside a directory
> that did not exist a moment earlier.

The same docstring rejects the obvious alternative — letting the door pass its identity by argument —
because "the guard deliberately has no off switch outside the spine."

So: this ruling closes **tc1 completely** and **#315 partially**. The residual is a named, understood
architectural tension, not an unknown. Closing it would require an authenticated caller identity rather
than an observed cwd, which is a separate design change and is **out of scope**.

## Blast radius, measured

Narrow. Only **four** spines in this repo carry an `origin` stamp at all:

| spine | `origin.worktree` | git toplevel agrees |
|---|---|---|
| `.worktrees/epic-568-441` (live) | `…/.worktrees/epic-568-441` | **yes** |
| `archive/2026-08-14-epic-568-530` | `…/.worktrees/epic-568-530` | worktree gone; terminal |
| `archive/2026-08-15-epic-568-510` | `…/.worktrees/epic-568-510` | worktree gone; terminal |
| `archive/2026-08-15-epic-568-codex-tier-local` | `…/.worktrees/epic-568-codex-tier-routing` | worktree gone; terminal |

Every other spine — including `commander-315`, the epic-568 Admiral spine, and every pre-#577 archived
spine — has `origin: None` and takes the untouched fallback branch. The three stamped archived spines
are terminal and need no further verbs. **The one live stamped spine already satisfies equality**, so
this change cannot strand work in flight.

`origin.worktree` values are immutable engine identity. **No rewriting, no backfill, no migration.**

## The other half of tc3: lexical vs git ownership

Two derivations disagree today and neither knows the other exists:

- `scripts/hooks/spine_rail.py::_worktree_from_spine` derives ownership **lexically** from the spine path.
- `scripts/mcp_spine_server.py::_worktree_root_for_lifecycle` asks **git**.

**Ruled: both stay. Neither is a bug. The defect is that the split is accidental, so it gets written
down.**

The hook keeps lexical derivation for a real reason its docstring already gives — an absolute claim path
stays meaningful after a checklist is archived and its worktree is gone, which git cannot answer for a
directory that no longer exists. The hook also runs on every tool call, where a subprocess per call is a
cost the engine's once-per-verb call site does not pay.

**This is a documentation deliverable, not a code change.** `scripts/hooks/spine_rail.py` is **not to be
edited** under this ruling — it is also the primary target of live work on #441, and a docstring edit
there would collide for no gain.

## Authorized deviation from normal stop conditions

Migrating existing test **intent** is normally a stop condition. Here it is **explicitly authorized and
expected**, in one specific way:

`tests/test_spine_origin_isolation.py` asserts containment against synthetic paths (`/w/repo`,
`/w/repo-2`, `C:\W\REPO\scripts`) that are not real directories and not git repos. Under equality, the
subdirectory cases (`cwd="/w/repo/scripts"` → `None`) become wrong *at the predicate level* — the
resolution that makes them right now happens above the predicate.

Those assertions **move up a level**: the property "a subdirectory of my own worktree is allowed" must be
re-asserted through `main()` against a **real temporary git repo**, not deleted. The predicate's own
tests stay pure and synthetic, and switch from containment semantics to equality semantics.

Losing that property from the suite is a failure of this ruling. Moving it is the point.
