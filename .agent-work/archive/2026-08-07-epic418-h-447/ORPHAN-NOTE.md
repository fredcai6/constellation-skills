# One orphan the closeout produced, folded rather than left

The `archive` step instructs the Commander to move `.agent-work/<work-id>/` into
`.agent-work/archive/<date>-<work-id>/` and then keep driving the engine from the moved spine.
The engine writes its per-step context and mechanical stamps to a path derived from the WORK ID,
not from the spine file it was handed, so once the move lands the remaining stamps go to
`.agent-work/archive/<work-id>/` -- a sibling of the real package that matches nothing.

Observed here: two files, `context/archive.json` and `mechanical/archive.json`, in
`.agent-work/archive/epic418-h-447/`. Both have been moved into this package alongside the
stamps for every other step, and the orphan directory removed. Nothing is lost.

Not filed as an issue: it is cosmetic, it produces exactly two files, and it is visible as
untracked scratch at the moment it happens. Recorded here and in RETURN.md so the next Commander
that follows the same instruction knows to look for it rather than rediscovering it.
