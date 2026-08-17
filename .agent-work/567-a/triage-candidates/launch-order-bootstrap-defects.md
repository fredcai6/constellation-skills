# Triage candidate: three bootstrap defects in the launch-order template

- **Disposition:** `recommend-and-defer`. Not filed (`decision:no-issue-filing`).
- **Raised by:** `cmdr-567-a` at `600de020`. All three cost real time at bootstrap,
  before any mission work started.
- **Audience:** the Admiral, since these are order-template defects rather than
  code defects.

## 1. The engine path in the launch order does not exist

`LANE_A_LAUNCH_ORDER.md` §Inherited Context says:

> Engine CLI: `py /home/tommy/.claude/skills/constellation-commander-delegated/scripts/checklist_engine.py --file <plan> <verb>`

and the dispatch instructions repeat it. **That file does not exist.** The installed
`constellation-commander-delegated` skill ships only `SKILL.md`,
`interpreter.json` and `references/` — no `scripts/`, no `templates/`.

This is not an install fault. The skill's own `SKILL.md` says so explicitly: the
doctrine and templates live in the `constellation-commander` skill and "this skill
therefore depends on `constellation-commander` being installed alongside it." The
real engine is:

```
/home/tommy/.claude/skills/constellation-commander/scripts/checklist_engine.py
```

Any delegated launch order citing the delegated path hard-fails at the "claim your
lease" step, which orders instruct agents to run as their **first command**. A
commander that takes the path literally cannot start.

**Recommendation:** the order template should cite the `constellation-commander`
path for both the engine and `init_work_area.py`, or cite no absolute path and tell
the commander to resolve it from the delegated skill's stated dependency.

## 2. The assigned working-notes filename was already a tracked file

The order says: "Your working-notes file: `notes-a.md`, in your worktree root. **You
are its sole writer.**"

`notes-a.md` is tracked at `600de020`, 197 lines, written by lane `cleanup/a-door`
and committed at `33dc3086`. The first write to it destroyed all of it. Recovered
via `git show HEAD:notes-a.md`; the file now carries the prior content verbatim
followed by this lane's record, verified by `git diff --numstat` = `178 0` (178
added, **zero removed**).

`notes-1.md` and `notes-b.md` are also tracked at `600de020`, so lane B this wave
has the same trap set and does not know it.

The order even anticipates a *different* problem with this filename — it explains at
length that the file must not be called `findings-a.md` because the `Write` tool
refuses that basename. It checked the tool's guard and not the tree.

**Recommendation:** a launch order that assigns a working-notes filename should
assign one `git ls-files` reports as absent. Per-epic scoping would do it —
`notes-567-a.md` rather than `notes-a.md`.

## 3. `verify_worktree_isolation.py --here` cannot be run as instructed

The order gives a strict ordering warning: run `verify_worktree_isolation.py --here
<path>` only **after** `cd`-ing into the worktree, because `--here` asserts about the
ambient cwd; and it explicitly forbids the `git -C <path>` workaround as
self-disarming. All correct.

But in this harness **the shell's working directory does not persist between tool
calls.** A bare `cd` in one call, followed by the verify in the next, verifies the
*session's* starting directory. Measured: it reported "wrong worktree: you are in
/home/tommy/projects/constellation-skills", exit 1 — which reads as a failed
isolation gate when isolation was in fact fine.

The working form is a single call that does both:

```
cd <worktree> && py .../verify_worktree_isolation.py --here <worktree>
```

which returns `worktree OK`, exit 0. The check itself is sound; only the
two-call sequencing the order prescribes is unusable here.

**Recommendation:** the order should prescribe the compound single-call form. This
matters more than it looks: the *previous* agent on this lane died after 47 minutes
having written zero bytes, and its last words were "the bash cwd resets between
calls." An order that prescribes a two-call bootstrap sequence in a harness with no
cwd persistence is a documented cause of a lost lane.

## Common shape

All three are the same authoring failure: the order asserts a fact about the
environment (a path exists, a filename is free, a cwd persists) that was never
checked against the environment. Each is cheap to check and each one blocks step
one, where the commander has the least context to diagnose it.
