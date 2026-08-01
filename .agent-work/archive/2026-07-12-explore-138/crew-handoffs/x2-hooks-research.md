# x2 research excursion — do hooks fire for subagents and headless runs?

## The one named question

On this harness (Claude Code, Windows), do project-local hooks (`.claude/settings.json`) fire for
(a) Agent-tool dispatched subagents, (b) headless `claude -p` runs, and (c) which hook events exist
and can block/inject — specifically `SessionStart` (does it distinguish source `compact`?), `Stop`
(can it refuse a stop and return a reason the agent must act on?), and `PreCompact`?

## Type

Research. Primary sources REQUIRED: official Claude Code docs (docs.anthropic.com / code.claude.com
hooks reference), changelogs. A live empirical probe is worth more than a doc claim where cheap: you
MAY create a scratch dir OUTSIDE the repo (use the OS temp dir), write a minimal hook that appends to
a log file, and run a tiny `claude -p` there to observe firing. Do NOT touch
`C:/Programs/constellation-skills` working tree or its `.claude/` settings.

## What "answered" looks like

A findings doc with one row per (hook event × invocation mode): fires? can block? payload fields
available (e.g. session source, transcript path)? — each claim cited to a doc section or a pasted
probe log. Contradictions surfaced, not smoothed. Explicitly state what was NOT tested.

## Budget / stop conditions

- ≤25 minutes; report partial findings rather than overrun.
- No changes to the constellation repo. Scratch probes only in temp dirs.
- Scoped nulls: "probe X didn't fire in mode Y" kills that combination as tested, not the channel.

## Result path (write the findings doc here)

`C:/Programs/constellation-skills/.agent-work/explore-138/evidence/x2-hooks-research.md`
