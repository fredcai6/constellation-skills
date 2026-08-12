# PRE-B brief: every byte that differs from the frozen #299 brief

Applied by `str.replace` against `capture_baseline.BRIEF`, each guarded by a presence
assertion. Never retyped. No other byte of the brief differs — the issue text, the
repository line, and the `FILES I WOULD CHANGE` output demand are byte-identical to
PRE-A.

## Substitution 1 of 2 — scope

Needed only because substitution 2 makes it necessary: a Commander driven to `plan`
must author a mission frame and `execute.json`, which the frozen blanket "do not
modify" would forbid. The carve-out is scoped to `.agent-work/` and nothing else;
commit / push / PR / issue-comment prohibitions are untouched.

### BEFORE

```
This is a PLANNING engagement only. Implementation is a separate, later engagement and
is out of scope for you: do not modify, commit, push, or open a pull request, and do not
comment on the issue.
```

### AFTER

```
This is a PLANNING engagement only. Implementation is a separate, later engagement and
is out of scope for you: do not modify this repository's source, tests, or documentation,
do not commit, push, or open a pull request, and do not comment on the issue. Your own
working notes and planning artifacts under `.agent-work/` are the one exception, and are
expected.
```

## Substitution 2 of 2 — the treatment

The whole point of the arm. The `FILES I WOULD CHANGE` demand is carried through
unchanged so the plan-stage output and the seam-grading input stay comparable.

### BEFORE

```
Understand the problem, then produce a plan. Your plan must name the specific files you
would change and explain why each one. Finish by stating your file list plainly under a
final heading `FILES I WOULD CHANGE`, one path per line.
```

### AFTER

```
Run this as a Commander. Load the `constellation-commander` skill and drive its spine
through its steps in order, stopping once the `plan` step is complete: the mission frame
authored and `execute.json` authored. Do not enter `execute`: stop there and return.
No human is reachable for this engagement, so wherever a step calls for a human decision,
record what you would have asked, decide it yourself, and carry on rather than waiting.

Your plan must name the specific files you would change and explain why each one. Finish
by stating your file list plainly under a final heading `FILES I WOULD CHANGE`, one path
per line.
```
