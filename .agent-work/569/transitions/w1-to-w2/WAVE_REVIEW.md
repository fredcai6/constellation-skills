## Wave review — boundary `w1-to-w2`

Wave 1 delivered both lanes and merged both PRs. `main` is verified green at `3622 passed, 6 skipped`
in a clean worktree. The wave's real value, though, is what it falsified.

**The epic's own work package 1 was aimed at the wrong path.** `generate_spine.py` requires a
`because` per qualitative condition, which the epic read as "half the fix already exists." It is a
live, tested compiler — but no shipped role skill routes through it. Every spine actually driven by a
Commander, Admiral or Crew comes from `init_work_area.py` resolving a hand-written template, and
`COMMANDER_SPINE.template.json` carries **0** `because` fields against **19** `check: null`
postconditions. Had the epic run in its filed order, its central mechanism would have been built on a
path nothing drives, and the built-not-wired sweep that catches it was scheduled last.

**Every measurement of the built-not-wired population understated it, in the same direction, three
times.** #345 filed six instances. The Admiral's pre-census found 7 live of 26. The commander's first
pass found 12. Its second found **17 live, 8 unwired, 1 dead**. Each measured a narrower surface than
enforcement actually uses — a measurement true about a smaller thing than it appeared to describe,
which is this epic's own subject aimed at the people running it.

**A commander's self-report was not sufficient to merge on.** `w1-wiring` ran without any independent
review — a consequence of an Admiral dispatch error — and reported both negative self-tests sound and
the suite green. An Admiral-ordered clean-room review found one negative test never called the real
scan (proved by breaking `_prose_files()` and watching all seven tests still pass) and the suite
actually 1-failed. Both defects were exactly the class a self-review cannot catch.

**A `MERGEABLE`, reviewed, conflict-free PR turned `main` red.** Measured directly: merging #645 into
`main` succeeded cleanly and produced a failing suite. Every automated signal said yes, and CI is
Windows-only and known-red so its verdict is ignored by policy. Only a hand-run suite on the merged
tree caught it.

**The sonnet thesis held.** Both lanes delivered at sonnet. `w1-wiring` caught and documented its own
census error mid-run; `w1-verdict` found and fixed an uncaught `AttributeError` crash beyond its brief
and its crew reproduced every evidence figure independently rather than re-reading the implementer's.
The one quality gap traced to the Admiral's dispatch mechanism, not the model tier.
