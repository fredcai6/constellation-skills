# FENCE — why this export is staged rather than written to the durable root

**Citing:** `.agent-work/cleanup-a-door/LAUNCH_ORDER.md`, "Return Shape" item 5 — *"If you
are fenced from writing `.agent-work/CONSTELLATION_FEEDBACK.md`, stage the export in your
work area and leave a `FENCE.md` citing this order."*

**The fence is mechanical, not a judgement call.** The Commander spine's `archive` gate
carries a `git-change-policy` postcondition (`c4`) whose `deny_globs` names
`.agent-work/CONSTELLATION_FEEDBACK.md` and `.agent-work/CONSTELLATION_FEEDBACK.collected.json`
explicitly. Writing this run's feedback there and committing it would refuse closeout, and
waiving `c4` to force it through would record a human authority that does not exist on this
delegated run.

**So the export sits beside this file, complete**, at
`.agent-work/staged-feedback/cleanup-a-door/CONSTELLATION_FEEDBACK.md`. A `FENCE.md`
citation without the staged export still fails the gate — learning cannot be silently
dropped — so the export is the point and this file is only its explanation.

**Named explicitly for the harvest, because the harvest has failed before.** The launch
order says so in the same breath, so this path is repeated in the return report rather than
left to a sweep:

```
.agent-work/staged-feedback/cleanup-a-door/CONSTELLATION_FEEDBACK.md
```

The run's episodes are unaffected by any of this: `episodes/` is a tracked repo-root path
inside this worktree, and the five episodes for this run were written through
`scripts/apply_episode_delta.py` and committed. The commit is what carries them out.
