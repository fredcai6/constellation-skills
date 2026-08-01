# Fresh-context selection check (g3) — F's binding acceptance

**Setup:** a cold subagent (model haiku — one tier down, per launch-order budget) was given ONLY the 15 constellation skill frontmatter descriptions (read from THIS worktree, including the new `constellation-commander-delegated` and the updated `constellation-admiral` description) plus three invocation contexts, with no other context. It had to name the single best skill for each.

**Contexts:**
- (a) human at the keyboard, runs one issue end to end, checks decisions as it goes
- (b) frozen Admiral LAUNCH_ORDER to run ONE issue autonomously, no reachable human
- (c) human hands over an epic spanning multiple issues

**Transcript (final message, verbatim):**
```
(a) -> constellation-commander — Runs one bounded issue end to end for a live human, understanding, planning, and executing while surfacing decisions to check with them.
(b) -> constellation-commander-delegated — Runs one bounded issue autonomously under a frozen LAUNCH_ORDER with no reachable human, citing the order and proceeding with genuine gaps escalated to the Admiral.
(c) -> constellation-admiral — Runs an epic spanning multiple issues as the human's delegate, dispatching and adjudicating work across bounded issue commanders.
```

**Verdict: PASS.** All three named correctly, including the newly-introduced confusable pair (commander-delegated vs admiral: one-issue-under-launch-order vs epic) and the human-vs-delegated commander split. Selection works one tier down. No description iteration needed; the honest-null clause was not triggered.
