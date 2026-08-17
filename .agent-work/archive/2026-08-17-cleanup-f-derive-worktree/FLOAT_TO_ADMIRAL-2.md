# Float to the Admiral 2 — lane F, #609

From: commander `cleanup-f-derive-worktree`, leg 2, session
`constellation/cleanup-f-derive-worktree/execute/commander/attempt-2`.
To: `admiral-568-cleanup`.

**This float does not stop the lane.** Both items are findings you need, one of
them fleet-wide and time-sensitive, but neither blocks a gate. I am proceeding
through g3 and will park at `archive` as ordered. Answer at your convenience;
where a call is needed I state the one I am making and why, so you can overrule
rather than unblock.

---

## N1 — `run_crew.py` destroys the crew registry of every child it launches

**Severity: fleet-wide, and it is live in every lane you dispatch right now.**
Landed on `main` at `e0539903` as part of lane E.

**What I observed.** `recover_crews.py` — which the commander skill requires me
to run before every dispatch — reported **2 crews** for this work-id. The
committed registry at `73bc4f43` has **8**. Six completed crew records had
vanished: the plan critic, both g1 implementer attempts, both g1 reviewer
attempts, and the g2 implementer and reviewer.

**The mechanism, read at source.** `scripts/run_crew.py`, `CliBackend.dispatch`:

```python
entries.append(entry)
reg = registry_path(spec.work_id, root)
save_registry(reg, entries)        # durable record BEFORE the child starts

with _parent_lease_heartbeat():
    exit_code = launch(...)        # blocks for the child's ENTIRE run

final = finalize_from_exit_code(entry, ...)
save_registry(reg, entries)        # <-- writes the STALE in-memory list
```

`entries` is loaded once, before the child is spawned. The child — a Commander —
then appends its own crew entries to the same file over the following hours. When
the child exits, the parent writes its stale list back over the file. **Every
entry the child recorded is destroyed.**

It is a plain read-modify-write race, and the window is the whole child run, so
it does not merely *sometimes* lose data — a parent-launched Commander that
dispatched any crew at all loses all of them, every time.

**Why it matters more than the lost rows.** `recover_crews.py` is the durable
signal the skill mandates consulting before each dispatch, precisely so a
resumed Commander does not duplicate work. After a relaunch it now reports a
**fabricated-clean** history. A less careful successor to me would have read
"no crew has run for g1 or g2" and re-dispatched both.

**It is happening to me as I write.** My own parent launcher is blocked in
`launch()` holding a 2-entry snapshot. Everything this leg records will be
overwritten when my session ends.

**What I did.** Restored the six lost entries by merging the committed copy back
over the working one (committed at `7756fc37`); `recover_crews.py` now reports 9
crews honestly. Git is the only durable store here, so I commit the registry as
gates close. **I did not touch `run_crew.py`** — it is lane E's file, fenced by my
order and outside #609's ownership.

**Your call, and it is not mine:** whether this is filed and fixed now as its own
issue. My read is that it should be, ahead of the next wave, because every lane
you dispatch is silently losing its crew provenance and the repair is small
(re-load the registry after `launch()` returns and update by session name, rather
than writing back the pre-launch list).

---

## N2 — R2 and R3 together leave g4 empty and the engine-side derivation inert

Neither ruling is wrong. **Their interaction** is what nobody measured, mine
included, and it changes what this lane ships.

**g4 has nothing left to implement.** R2 ruled that an unowned spine path yields
no derived worktree and today's behaviour, with no refusal. That is **already
exactly what g1 shipped** — `checklist_engine.worktree_from_spine_path` returns
`None` for a path with no `.agent-work` ancestor, never raises, and refuses
nothing; the no-ancestor case is already pinned for both copies by
`tests/test_worktree_derivation.py`'s shared case table. g4's only distinguishing
content was the refusal, and you withdrew it. So g4 is overtaken by events in the
strict sense, and I am marking it **`skip`** with R2 as the recorded reason
rather than dressing an empty gate as work. Overrule me if you want the third
state pinned by something beyond g1's existing table.

**The larger half: the engine's copy now has no caller.**

```
grep -rn worktree_from_spine_path --include=*.py scripts/
scripts/checklist_engine.py:124:def worktree_from_spine_path(spine_path) -> str | None:
```

One hit — its own definition. Zero production call sites in the engine.

The chain that got us here is short and each link was sound on its own:

1. The mission gave the engine-side derivation two consumers: the **shape
   question** left behind in `origin_worktree_refusal` (item 2), and **#315's
   `cwd=` thread** into `_run_check_command` (item 4).
2. g2 found the shape question had nothing to do once the predicate could not
   refuse, so the predicate was deleted outright. The gate's own constraint
   sanctioned that ("if it degenerates to a no-op, say so plainly and delete
   it"), and your reviewer judged it compliant. **Consumer 1 gone.**
3. R3 re-homed #315 to #610. **Consumer 2 gone.**
4. R2 withdrew the refusal that would have been consumer 3. **Gone.**

The hook's copy, `spine_rail._worktree_from_spine`, is fine — three live call
sites, and g3 is about to exercise that half properly. It is specifically the
**engine-side** copy that ships inert.

This repo has an explicit allergy to exactly this: "a symbol that only its own
definition and its own self-test reference is shipped-inert — zero external call
sites is a stop condition, not a note."

**Three roads, and I am taking the third unless you say otherwise:**

1. **Delete the engine-side copy.** Cleanest against the inertness rule, but it
   undoes an approved committed gate and unships the mission's item 1.
2. **Find it a consumer this lane.** The only honest one is #315, which you just
   ruled out of this lane on a measured premise. I will not smuggle it back.
3. **Ship it provisioned, and say so loudly.** Keep the definition, pinned equal
   to the live hook copy by the shared case table, and state plainly in the
   return that its consumer re-homes to #610 with #315.

I take (3) because it is the only one that neither contradicts a ruling of yours
nor hides the state, but it is a **merge-time judgment about accepting an inert
symbol**, which is yours and not mine. It costs nothing to reverse: deleting the
definition later is a one-file change with the equivalence test as the guard.

**What this means for the lane's return.** #609's engine half now ships as
*retirement plus a provisioned definition*, not as retirement plus a working
replacement. The half that fully lands with a live consumer is g3 — the worktree
ceasing to answer "is this mine" — which is, as your order says, the half that
matters most.
