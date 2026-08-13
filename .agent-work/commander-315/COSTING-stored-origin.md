# Costing — direction D: a spine records its own repo reference at creation

Requested by the Admiral after the human rejected options A/B/C. **This is a
costing, not an implementation.** Nothing in this document was built.

Every count below is **measured** unless explicitly marked *(estimate)*.

## 0. Two corrections carried in

**Mine, withdrawn.** My "394 checks already carry `cd <abs> &&`, so the fix is
inert for the generated majority" counted corpses. Re-bucketed:

| bucket | command checks | carry `cd … &&` |
|---|---|---|
| `.agent-work/archive/` (dead runs) | 1649 | 355 |
| **live template corpus** (`skills/*/templates/` + `.agent-work/templates/`) | **64** | **0** |
| other live (examples, work areas) | 26 | 3 |
| tests/docs fixtures | 8 | 0 |
| **total tracked** | **1747** | **358** |

The Admiral's correction reproduces exactly: **the live template corpus has 64
command checks and zero carry a `cd` prefix.** The immunity is real and almost
entirely in dead scrap. Withdrawn from my evidence; do not carry it forward.

(My 1747 total vs the Admiral's 1733 is my own run's spine and fixtures, added
after that measurement. The load-bearing figures — 1649 archived, 355 archived
`cd`, 64 live, 0 live `cd` — agree cell for cell.)

**The Admiral's, refined.** "107 spines with no `origin`" is now **108**, and the
distribution matters more than the total:

```
tracked spine.json files : 108
  WITH an origin block   : 0
  WITHOUT                : 108
```

**106 of the 108 are under `.agent-work/archive/`** — finished runs that will
never execute again. Only **2** are live: `.agent-work/commander-315/spine.json`
(mine) and `examples/mcp-interactive-demo/spine.json`. The backfill population is
2, not 108.

## 1. What changes, in what module

### Write side

**`scripts/spine_lifecycle.py` — zero change.** `build_origin()` (line 83)
already returns `{work_id, branch, worktree, base, opened_at, opened_by, parent}`
and `open_work()` already injects it. The write side is built and correct.

**`scripts/init_work_area.py` — the whole leverage, and it is small.**
`instantiate_spine()` (line 152) already:

- line 148 (via `resolve_spine`) computes `Path(root).resolve().as_posix()` for
  `<repo-root>` substitution — **and discards the value**;
- line 170 calls `json.loads(resolved)` purely as a validity guard — **and
  discards the dict**.

Both the value and the parsed container are already in hand and thrown away. The
change is to parse once, inject `origin`, and serialize: **~8 lines** *(estimate)*.

This is the load-bearing insight of the costing: **the direction does not need
`open_work`.** `init_work_area.py` already holds the repo reference at exactly
the moment the spine is written, for **all 12** instantiable role templates.

*Optional, separable:* a CLI entry on `spine_lifecycle.py` — **~30 lines**
*(estimate)*, see §3.

### Read side

**`scripts/checklist_engine.py` — currently reads no spine-level `origin` at
all.** Its only `origin` is the git ref `origin/main` (line 692). Three pieces:

| piece | what | size *(estimate)* |
|---|---|---|
| a | read `cl["origin"]["worktree"]`, resolve to a root or `None` | ~8 lines |
| b | thread that root to `_run_check_command` as `cwd=` | ~12 lines |
| c | engine-native isolation refusal (§4) | ~12 lines |

**One real friction on (b), worth naming now.** `_check_condition(cond, t,
base_dir)` receives the *task*, not the checklist, so it cannot reach `origin`
itself. Its callers (`start`, `advance`, `record`) all have `cl`. The clean shape
is to resolve the root once in `dispatch()` and pass it as a **parameter distinct
from `base_dir`** — `base_dir` is also the gauge-file location (`_gauge_path`,
line 1252) and the `--from-child` resolution base (line 2250), so overloading it
would couple three unrelated things. That is why the estimate is ~12 lines rather
than one.

**Total engine-core change: ~32 lines across 3 sites** *(estimate)*, in one
module, with no new argument on any public verb.

## 2. What happens to the 108 spines with no `origin`

**Backfill is not the problem — 106 are dead.** The live population is 2.

The real question is not the existing 108 but **every spine created after the
change**, since `init_work_area.py` is the path 12 role templates use.

Three policies:

| policy | consequence |
|---|---|
| **refuse** a spine without `origin` | breaks all 12 role templates the day it lands, plus the demo. Not viable as a first move. |
| **fall back to deriving a root** from `base_dir` | **reintroduces the defect I was blocked on.** A derived root is exactly what makes `verify_worktree_isolation --here` tautological. Do not do this. |
| **fall back to inherited cwd** | today's behaviour precisely. Nothing regresses; the fix is simply **inert** until a spine carries `origin`. |

**Recommend: fall back to inherited cwd, and treat that as a stated, temporary
tolerance rather than the end state.** It is the only non-breaking option, and it
does not reintroduce the defect.

The consequence must be stated plainly, because it is the direction's main risk:
**a fallback means the fix delivers nothing until spines actually carry
`origin`.** So the write side (`init_work_area.py`, ~8 lines) is not an optional
convenience — it is the change that makes the read side worth landing. Land them
together or the engine work is dead code.

A later `refuse` mode, once the corpus carries `origin`, would close it properly.
That sequencing is a decision for you, not for me.

## 3. Does the dead `spine_open` door block adoption?

**No — and the reason is stronger than "there is a workaround."**

Measured:

- `scripts/spine_lifecycle.py` has **no CLI entry**: zero `__main__` blocks, no
  `argparse`, no `main()`.
- Its **only production caller** is `scripts/mcp_spine_server.py:567`, the dead
  `spine_open` door.
- It is a plain importable module — `tests/test_spine_lifecycle.py:31` imports it
  and calls `open_work()` directly. So `open_work()` **is** reachable without the
  door, today, from Python.

But the door is not the real barrier. **`open_work(work_id, spec, ...)` requires
a compiled `spec`**, which `_compile_spine()` (line 238) puts through
`generate_spine`'s spec-shape → compile → probe → validate chain. And:

```
spec files tracked (specs/*.spine.toml) : 2   (implementer, reviewer)
role spine templates instantiated by init_work_area : 12
```

**Routing the roles through `open_work` would require authoring ~10 new spine
specs** — a migration far larger than this whole issue, and one that would
rewrite every role's spine into generated form. That is a real programme, not a
side effect.

**So: the door does not block the direction, because the direction should not go
through `open_work` at all.** Stamping `origin` in `init_work_area.py` reaches
all 12 templates without a door, without a spec, and without touching
`spine_lifecycle.py`. Fixing the door is worth doing on its own merits — it is
why the disciplined path is unused, including for this epic's own spine — but it
is **not a prerequisite**, and making it one would gate a ~40-line change behind a
10-spec migration.

## 4. What the isolation gate needs

**It shrinks — further than you expected — but stored `origin` does not do it
alone, and that distinction is load-bearing.**

**Stored `origin` by itself does not save the gate.** This is demonstrated, not
argued — `.agent-work/commander-315/d_trap_demo.sh`, a spine carrying a real
`origin` block and the shipped `init.c0` check:

```
  origin.worktree stored in the spine : /tmp/…/wt
  EXPECTED inside the check text      : /tmp/…/wt
  IDENTICAL? True

  launcher standing in the WRONG worktree (the main checkout):
  cwd = launcher's own (today)        : REFUSED (gate works)
  cwd = origin.worktree (direction D) : PASS (gate disarmed)
```

The two values are byte-identical because both derive from the same root at
creation time — `origin.worktree` is written by the process that made the
worktree, and EXPECTED is `<repo-root>` substituted from that same root at
`init_work_area.py:148`. So an engine that sets `cwd = origin.worktree` runs the
check **from the very path the check asserts it is standing in**. It is `X == X`
again — the identical tautology I was blocked on, arrived at by a different
route. Any version of this direction that only stores a root and forwards it as
`cwd` **re-breaks the gate**, and the guard I landed on PR #576 will catch it.

**What does save it:** with `origin.worktree` stored, the isolation gate no
longer needs to be a command check at all. The engine can make the comparison
**natively**, at verb entry:

```
engine's own Path.cwd()   vs   cl["origin"]["worktree"]      -> refuse on mismatch
```

The engine process's own cwd is untouched by any of this — only the *child*
subprocess gets a `cwd=`. So the engine still holds the one fact the check needs,
at the one moment it is still true.

This is **strictly stronger** than today's shell-out and **smaller** than
anything in options A or B:

- no schema flag (option B) — nothing is declared per-check;
- no `SPINE_LAUNCH_CWD` env var and no `--from` flag (option A) — no new
  engine-to-check contract at all;
- it cannot be disarmed by child-process cwd manipulation, because it never
  leaves the engine;
- it runs on **every** verb, not only at `init.c0`;
- **`init.c0`'s command check gets deleted** from `COMMANDER_SPINE.template.json`
  rather than repaired — one template edit, one check removed.

So the answer to "confirm that shrinks as I expect": **it shrinks more than
expected — from a schema feature, to one named check, to zero checks.** The
subject-is-cwd problem does not need to be *handled*; it dissolves, because the
engine stops delegating a question it can answer itself.

The one thing that does not shrink: something must still refuse. The ~12 lines in
(c) above are that. This is not free, it is just cheap.

## 5. What it does to the 17

**Nothing. They need no editing.**

All 17 cwd-dependent checks in the shipped source corpus are authored
**repo-root-relative** — measured in my earlier enumeration and reproduced by the
Admiral cell for cell (22 checks, 6 literal-relative, 11 cwd-defaulting-script,
17 cwd-dependent, 5 clean). Zero are spine-dir-relative.

`origin.worktree` **is** the repo root — it is the worktree path recorded at
creation, which is precisely the root `<repo-root>` already resolves to at
`init_work_area.py:148`. So a check that resolves correctly relative to the repo
root resolves correctly relative to `origin.worktree`, unchanged.

This holds for both classes:

- the **6 literal-relative** (`scripts/x.py`, `.agent-work/<id>/y.json`) resolve
  against the stored root;
- the **11 cwd-defaulting-script** cases (`--root` defaulting to `.`) inherit the
  stored root as their cwd, so their `.` becomes the right `.`.

**Zero template edits for the 17.** The only template edit in the whole direction
is deleting `init.c0`'s now-redundant command check (§4).

## 6. Summary of the costing

| item | measured size |
|---|---|
| `spine_lifecycle.py` write side | **0 lines** — already built |
| `init_work_area.py` stamp `origin` | ~8 lines *(estimate)* |
| `checklist_engine.py` read + thread + native refusal | ~32 lines across 3 sites *(estimate)* |
| template edits | **1** — delete `init.c0`'s command check |
| edits to the 17 cwd-dependent checks | **0** |
| spines needing backfill | **2 live** (106 archived are dead) |
| new spine specs required | **0** — the direction bypasses `open_work` |
| door fixes required first | **0** — worth doing, not a prerequisite |

**Judgment you asked for.** This is small — roughly 40 lines in two modules plus
one template deletion, with no public-verb signature change and no schema change.
It is smaller than option A and much smaller than option B, and it is the only
one of the four that makes the isolation gate *stronger* instead of negotiating
with its weakness.

Two things keep it from being a trivial re-cut, and both are sequencing rather
than size:

1. **The write side and read side must land together.** With a cwd fallback, the
   engine change is inert until spines carry `origin`; without the fallback, it
   breaks 12 templates on day one.
2. **The naive reading of this direction re-breaks the isolation gate** (§4). If
   it is cut as "store the root and pass it as `cwd`", it is the falsified fix
   wearing a new hat. The gate must become engine-native in the same change.

Per your instruction I have not implemented it. If it is re-cut, it is one issue,
not a wave — and the guard on PR #576 is what will catch it if someone builds
only half.

## 7. Adjacent, noted not chased

The `repair`-exit split you flagged (`constellation-admiral/SKILL.md:63` accepts a
`repair` exit and renders `CURRENT_TRUTH.md`/`WAVE_REVIEW.md`, while
`verify_iterative_role_artifacts.py:237-259` refuses `repair` and the render sits
after the refusal) did not cross my path. Not chased, per your instruction.

It does rhyme with my triage candidate 6 — two contract documents asserting a
behaviour no test pins, so code and doctrine drift apart silently. Same failure
shape, different pair of files.
