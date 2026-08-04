# Excursion handoff: exc-5-issue-reality

Full brief: `### EXCURSION_BRIEF exc-5-issue-reality` in `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/IDEAS_BOARD.md`.

- **Task:** one cold sonnet agent per open issue (127 at dispatch time), each judging: is this issue real *today*, given the tree at HEAD, the work phase 1 already landed, and the project direction (mechanization over prose, spine-carried instructions, governor working, backlog consolidation, vision later)?
- **Mechanism:** orchestrated as a workflow fan-out from the main session (this registry entry tracks the excursion as a whole). Per-issue agents are NOT shown exc-4's classifications — this is a cold second read.
- **Per-agent contract:** read the issue (`gh issue view N --json title,body,comments`); verify its central claim against the tree by command where cheap; return a structured verdict (real-now / real-later / superseded / obsolete / unclear) + evidence + recommended disposition. Read-only; no tracker writes.
- **Result artifact:** aggregate at `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/evidence/exc-5-issue-reality-RESULT.md`, including the census count vs. classified count (must match) and agreement/disagreement vs. exc-4's earlier classification (computed at aggregation, not shown to agents).
- **Scoped nulls:** an agent that cannot decide returns unclear with what it checked; a failed agent's issue is listed as NOT COVERED, never silently dropped.
