# The one clause changed (probe #331 vs frozen #299 brief)

## BEFORE (frozen, `capture_baseline.BRIEF`)

```
Understand the problem, then produce a plan. Your plan must name the specific files you
would change and explain why each one. Finish by stating your file list plainly under a
final heading `FILES I WOULD CHANGE`, one path per line.
```

## AFTER (this probe)

```
Understand the problem, then produce a plan.
```

Applied by `str.replace` against the frozen brief, guarded by a presence assertion.
No other byte of the brief differs.
