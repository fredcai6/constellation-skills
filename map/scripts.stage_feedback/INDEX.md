# scripts.stage_feedback
scripts/stage_feedback.py, 211 lines, 6 holes

Mechanize the fenced staged-feedback trio for a delegated Commander/Admiral run.

A delegated run fenced off the main checkout's durable `.agent-work/` cannot
write the durable `AGENT_FEEDBACK.md` (see "Fenced feedback/archive closeout
- stage, do not waive" in the commander doctrine). It instead stages a
worktree-local trio -- AGENT_FEEDBACK.md, lessons-delta.json,
CONSTELLATION_FEEDBACK.md, plus a FENCE.md citing the launch order -- at
`.agent-work/staged-feedback/<work-id>/`, in the shapes
`verify_agent_feedback.py --phase feedback` and `--phase archive` accept
(see `_staged_feedback_errors` there). Several commanders this epic hand-rolled
this exact four-file layout (#140, #143, #145); this script mechanizes it so a
fenced commander does not have to hand-roll it again (#154, issue-143 follow-on).

This script writes the FOUR FILES; it does not itself distill the retrospective
content or the lesson candidates -- those still require the calling agent's own
reflection (see `AGENT_FEEDBACK.template.md`). Pass the already-authored body
text/files for the parts that need genuine content (--feedback-body); the two
parts that are frequently a confirmed negative (lessons-delta, constellation
export) get a sane tick-only / no-export default when omitted, and can be
overridden with real content via --lessons-delta / --constellation-feedback.

imports stdlib: __future__.annotations, argparse, datetime.date, json, pathlib.Path, sys
imported by: none found

```python
TRIO_FILES = ('AGENT_FEEDBACK.md', 'lessons-delta.json', 'CONSTELLATION_FEEDBACK.md', 'FENCE.md')
```

- [_utf8_stdio](_utf8_stdio.md) function: HOLE: no docstring
- [_default_lessons_delta](_default_lessons_delta.md) function: HOLE: no docstring
- [_default_constellation_feedback](_default_constellation_feedback.md) function: HOLE: no docstring
- [_agent_feedback_text](_agent_feedback_text.md) function: HOLE: no docstring
- [_fence_text](_fence_text.md) function: HOLE: no docstring
- [stage_feedback](stage_feedback.md) function: Write the four staged-feedback files at
- [main](main.md) function: HOLE: no docstring
