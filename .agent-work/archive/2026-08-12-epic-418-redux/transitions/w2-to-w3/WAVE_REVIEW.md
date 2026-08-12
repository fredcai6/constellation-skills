## Wave 2 review — B extended

All four issues merged and closed; main green at `476e044d` (1782 passed, 2 skipped, 683 subtests, exit 0).

| Issue | PR | What landed |
|---|---|---|
| #433 | #485 | `directives` render |
| #436 | #472 | the enumeration check observed refusing a real new entry |
| #460 | #487 | episode records restated as observations; the guard caught 4 real offenders on its first live run |
| #464 | #473 | `Lesson:` renamed to `Episode:`, legacy fallback preserved |
| — | #470 | the Admiral's own fixture-path breakage |

### What the wave found that it was not looking for

Four findings, four subsystems, four different discoverers, **one defect family**: a signal whose value is identical in the healthy and the defective world.

- #433's naive fix would have been one — 2955 gates scanned, 8 populated, so a guard asserting "directives render when present" passes either way.
- The `engine_session` lease field is one in both directions: 18 of 147 tracked spines read `active`, exactly 1 is a live run; and a `null` reading is equally produced by a crew releasing between gates. See #457.
- `matches[0]` cannot signal that a second match existed. Now #489.
- The gauge writer cannot tell "two agents" from "one agent counted twice", so it wrote nothing all wave. Now #488.

The last one is the sharpest, because it fires on *correct* behaviour: an Admiral that drives its latitude bookend properly ends up bound to two checklists that resolve to one gauge path, and blinds its own governor for the rest of the run.

### Two corrections the Admiral owns

- It reported releasing an orphaned lease it had not released — the release exited 0 on the worktree copy, while the copy in `main` arrived via a merge and was never touched. Root cause: verifying that the action succeeded instead of re-running the observation that prompted it.
- It reported that PR #470 merged without review. True when written; two independent reviewers returned APPROVE afterwards, neither posting to the forge.

### Cost

6 of 10 dispatches were governor relaunches at the plan seam. That measurement is confounded — the Admiral's own gauge was dark for the entire wave.

### Wave 3

#461, #465, #488, #489. The last two were filed as findings and then folded in on an explicit amendment: a fix that is genuinely cheap gets done now, not filed and deferred.
