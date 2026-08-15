## Current planning truth — after wave 1

**Landed:** the regression guard at `9bb8c1b6`, engine-native worktree isolation at `0dd6a6eb`, and the post-promotion map refresh at `0448275e`. Merged Linux main is green at 2,980 passed / 7 skipped / 1,130 subtests.

**Harness result:** Codex successfully drove the exact Admiral and Commander spines through the stdio MCP server. The current host did not hot-load the newly configured door into this already-running session, but direct MCP transport worked; no checklist-engine CLI interaction was used. Claude review was limited by account quota rather than the harness.

**Not done:** lease lifecycle, binding-store durability, #530, #510, and the parked consumer work remain.

**Authority boundary:** the latitude contract expired at the wave-1 merge. No next wave is authorized until the human selects a tranche and refreshes scope, concurrency, and latitude.
