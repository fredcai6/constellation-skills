## Wave review — w1-f424-advance

**F is complete.** All six done-conditions carry a verdict backed by evidence and none is UNMEASURED — the repair's exit criterion, met. PR #533 is green and mergeable, suite 2178 passed / 0 failed, source diff a clean 15 files. Four reviewer BLOCKs were raised across the run; all four resolved on evidence, none overridden, none waived.

**The repair's reordering is what made it work.** Running g3 before g1 put the evidence ahead of the claim that depended on it. DC3 came back YES — an in-session subagent does inherit its parent's MCP scope — and that YES, which everyone expected would justify `gen_mcp_config.py`, is what removed it: a generated config binds at server launch per process exactly as `${VAR}` does, so it names a case **neither** mechanism reaches. Tombstoned with a do-not-reintroduce note, because that YES is precisely what a later reader would use to rebuild it.

**DC5 passed and undercut its own hypothesis.** CLI 22.0 against MCP 18.0 invocation attempts, non-overlapping in both orders — but malformed calls were **zero in both arms**. The door removed the need to read a manual; it did not absorb fumbles. The verdict also moved twice, and neither correction came from the Commander: a reviewer found a shell `for` loop scoring six engine invocations as one, and then called a post-hoc decomposition what it was. `MEASUREMENT.md` records all three versions rather than presenting the final verdict as if it had been the first.

**DC4 earned its cost after the spine closed.** Windows CI exposed that the door's JSON-RPC stdio was never pinned to UTF-8 — it corrupted its own protocol on Windows for most gates while the CLI door was fine. Exactly the CLI/MCP divergence DC4 exists to catch, on a platform no local work ran on.

**What the wave found that the plan did not have:** nothing drives through the door. Zero skills reference its tools, zero MCP references in the installer, and `.mcp.json` serves only an agent launched with the right variables in the right directory. A built door is not a used door.

**Decision: advance.** F2 takes the current wave — adoption and friction capture together, because adoption without capture converts diagnosable defects into silent corrections. C is held behind F2 on a stated entry condition. E leaves the epic at the owner's direction.
