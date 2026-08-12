# Harvest manifest — epic-226

Written at closeout in response to the lessons auditor's own request: a fresh-context
auditor had to *infer* why a folder was empty, which is exactly the kind of inference
a manifest removes.

**Expected 7 folders, 7 present.**

| Folder | Source | Contents |
|---|---|---|
| `227/` | wt-227 (issue #227) | AGENT_FEEDBACK, LESSONS, CONSTELLATION_FEEDBACK, lessons-delta |
| `228/` | wt-228 (issue #228) | staged trio + FENCE.md (fenced closeout) |
| `229/` | wt-229 (issue #229) | AGENT_FEEDBACK, LESSONS, lessons-delta — **no verdict**: commander-229 went idle with complete artifacts and dropped it; the Admiral verified acceptance itself plus a clean-room reviewer |
| `230/` | wt-230 (issue #230) | AGENT_FEEDBACK, CONSTELLATION_FEEDBACK, lessons-delta |
| `231/` | wt-231 (issue #231) | AGENT_FEEDBACK, LESSONS, lessons-delta |
| `232/` | wt-232 (issue #232, wave 1) | staged trio + FENCE.md |
| `239/` | wt-239 (#239 item 3) | **empty BY DESIGN** — dispatched as bounded implementer-with-plan, not a full Commander, so it had no spine, no lessons inbox, and no durable trio to produce |

All seven source worktrees were swept **after** this harvest, per the harvest-before-sweep
rule. Both constellation-scoped lessons raised here were exported, not silently confirmed.
