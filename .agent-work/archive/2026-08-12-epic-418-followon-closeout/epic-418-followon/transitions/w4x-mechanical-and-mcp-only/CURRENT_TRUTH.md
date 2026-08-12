## Current planning truth - after boundary w4x-mechanical-and-mcp-only

**The goal, ruled by the human:** constellation agents do not know about the engine CLI. They drive their spines through the MCP door, and the CLI runs only behind it. The reason is insulation - friction from the engine tool must not surface as friction in ordinary dev work.

**Landed:** M1 (`27a5adf5`). A dispatched crew gets `SPINE_FILE` for its own spine and `SPINE_SESSION` as `constellation/<work-id>/<gate>/<role>` - the assignment identity, no attempt tail - so a respawn resumes rather than force-claims. Suite 2494 passed, 1 skipped.

**Measured, and it reshapes the plan:** binding the door does not make agents use it. Two of four correctly-bound crews still went to the CLI, and the two that used the door were the two whose handoffs told them to. This is the evidence behind removing the choice rather than improving the encouragement.

**Current wave:** M2 makes the launcher self-sufficient - it grants a spawned crew its tools and permission mode, so nobody writes a settings file first - and keeps every entry definition configurable, with no literal interpreter in any shipped path. M3 fixes `docs/agents/CREW_CONTEXT.md`'s Python section, which is wrong on this host and which three handoffs today had to correct inline.

**Next:** #559. Its entry condition is explicit - the door must cover every verb an agent needs on the drive loop, or the uncovered ones must be shown not to be load-bearing. Five verbs are CLI-only today, and two others were judged rare at build time and turned out load-bearing.

**Carried, not worked:** #555 stays in the wave verbatim because it is a launched identity; Windows is parked at the human's direction and portability rides instead as a standing constraint on entry definitions.
