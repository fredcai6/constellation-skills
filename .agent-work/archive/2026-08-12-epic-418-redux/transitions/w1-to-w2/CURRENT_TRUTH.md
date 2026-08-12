## Current planning truth - epic #418

**Wave 2 (current): B extended.** Make the engine projection show the agent the whole gate, and
stop the playbook retirement from growing back inside the episode store.

| Issue | What it settles |
|---|---|
| #433 | `directives` renders, and a completeness property closes the class rather than the instance |
| #460 | Episode records read as observations, not instructions |
| #461 | The episode-store negative control stops failing on correct behaviour |
| #464 | The `Lesson:` field is renamed to match what it now carries |
| #465 | The reviewer placeholder becomes fillable without rewriting every line ending |
| #436 | The worktree enumeration check is observed actually refusing |

Exit criteria are on the wave, not the issues: every populated gate field renders under a
completeness property; episode records pass an authoring-end check that can fail; each issue
declares its subsumption candidate set before starting and reports how many it closed; the suite
is green against the 1721-passed baseline at `ca0e36a`.

**Forecast, nonbinding:** A2 trip semantics (still needs cutting, deliberately deferred so it is
cut against what B extended leaves behind), then F, then C, then E. Off-chain and runnable at any
point: #458 ship the gauge writer, #452 multi-spine attribution.

**Two of five done-conditions remain unmet:** the projection does not render every populated gate
block, and no agent has driven a real role spine through the MCP door. Done-condition 4 was
retired and replaced by the standing obligation that each workstream retires the findings it
subsumes, against a candidate set declared before it starts.
