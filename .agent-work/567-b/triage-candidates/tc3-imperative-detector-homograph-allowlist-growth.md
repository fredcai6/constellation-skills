# Triage candidate: episode imperative-detector cannot tell a homograph from an instruction

**Not filed — a recommendation only, per launch order `decision:no-issue-filing`.**

## What

The episode store's strict guard (`tests/test_episode_observations.py`, the imperative
detector behind `guard.scan_store`) flags a record whose statement text reads as an
instruction to a future agent — correct in general, since an episode is a record of what
happened, never a rule to follow. But English spells the past tense and the imperative of
many verbs identically ("read", "run", "write", "check", ...), and the detector cannot
tell them apart: a genuinely past-tense observation like "read its exact error text" trips
the same trigger as an actual imperative like "Read its exact error text [before you
proceed]."

This wave's own episode `epic-567-door_cmdr-b-003` assertion `a5` tripped exactly this way
(caught by the Admiral's post-return diagnosis, fixed by rephrasing "read" -> "reading" via
`restate-assertion`, not by adding to the exception list).

## Why it matters

The guard's remedy channel for a false positive is `guard.EXCEPTIONS`, a hand-maintained
allowlist. It is already 11 entries long across four prior episodes/runs
(`issue-304-g3-005`, `issue-308-014/015/017/019`) before this wave. Each of those was, in
all likelihood, the same homograph pattern repeating — four separate false positives
absorbed by allowlisting rather than the detector being taught to distinguish tense. This
is the repo's own "a check that cannot fail" family, wearing the opposite face: not a
check that passes on everything, but a check whose *failures* are systematically absorbed
into a growing exception list rather than diagnosed at the root, so the check keeps
"finding" the same non-bug indefinitely.

## Suggested disposition

Not urgent, not this lane's fix (the detector lives in episode-store tooling this lane
does not own). Worth a future pass: either (a) make the detector tense-aware — e.g. bias
against verbs that follow "read/run/write/checked/adjusted... its/the/a ..." as an object
of a completed action rather than a bare directive, or (b) accept that some ambiguity is
unavoidable in a heuristic and instead measure whether the allowlist's growth rate is
itself informative (11 entries across 4 runs, now heading toward 5, all early evidence of
the same failure mode) — a growing allowlist is itself a signal the check should surface,
not just silently accommodate.

## Source

Surfaced by the Admiral's post-return diagnosis of PR #621's regression set; fixed
locally by rephrasing (not allowlisting) per the Admiral's explicit instruction.
