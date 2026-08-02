# FENCE — 669-pilot feedback staging citation

This run is a DELEGATED commander run under **LAUNCH_ORDER-669.md** (epic #659 Wave 5a), executed in the linked
worktree `C:/Programs/f1brainz-wt/epic659-669` with the owner AFK and no reachable human.

**Fence basis (from the launch order):**
- "Feedback trio under `.agent-work/staged-feedback/669-pilot/` + `FENCE.md`."
- "DB-BLOB GUARD (hard): final diff = code+tests+report only, zero DB blobs, **zero `.agent-work` paths**."
- "NO merge without the Admiral (independent verify + re-run on pinned 3.14)."

Because the mission-branch diff must carry zero `.agent-work` paths and the run does not write the shared main
checkout, the durable `.agent-work/AGENT_FEEDBACK.md` / `LESSONS.md` / `CONSTELLATION_FEEDBACK.md` writes are staged
here instead of applied. This directory holds the complete trio — `AGENT_FEEDBACK.md`, `lessons-delta.json`
(tick=true; 4 confirms + 1 add with bank_reason), `CONSTELLATION_FEEDBACK.md` — for the Admiral to harvest into the
shared durable root at epic closeout (lessons-delta application + sibling-dedup are the Admiral's, per the epic-659
established pattern).
