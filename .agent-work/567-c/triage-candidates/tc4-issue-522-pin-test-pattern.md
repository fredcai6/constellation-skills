# Triage candidate: #522's pin-test pattern reproduced live

**Source:** Admiral diagnosis on PR #620, `cmdr-567-c` (epic-567-door lane C).

**Statement:** `tests/test_spine_rail.py::test_stop_mid_flight_blocks_with_substrings` pinned one
literal phrase (`"do not end your turn to wait"`) instead of the class of guarantee the Stop hook's
mid-flight refusal must carry. The #595 net-deletion rewrite of `_mid_flight_reason` (this lane's own
change) was correct and an improvement, but broke the test purely because the wording changed — this
is #522's exact complaint ("pin tests guard the literal wording of the bug, not the class of defect")
reproducing inside this epic. Notably the test's own name (`_with_substrings`) already signals intent
to check content properties rather than exact wording, yet it still pinned one literal phrase inside
that shape — the naming convention did not prevent the anti-pattern it was presumably meant to guard
against.

**Fix applied this run:** rewrote the test to assert three named properties (mid-flight identification
with gate id; stated precedence over the context-trip advisory; `spine_halt block` named as the
sanctioned exit) instead of one substring.

**Disposition:** recommend-and-defer. Not filed as an issue this run (`decision:no-issue-filing`).
Recommend a corpus-wide sweep for the same anti-pattern in other hook/engine-refusal-text tests
(anywhere a `_with_substrings`/`_blocks`-shaped test pins one literal phrase rather than the properties
a rewrite must preserve) — likely useful evidence for #522 itself, which this instance reproduces.
