# Fence — why lane K's feedback export is staged rather than exported

**Citation:** `LAUNCH_ORDER.md` (lane K, `cmdr-567-k`, epic #567 wave 3) — "File Ownership" and
"Workspace". This run is a delegated Commander in an isolated worktree with no reachable human.

The durable-root export target, `.agent-work/CONSTELLATION_FEEDBACK.md`, is named in the
**deny_globs** of the Commander spine's `archive` gate `c4` git-change-policy check
(`skills/commander/templates/COMMANDER_SPINE.template.json:130`), alongside the retired
`.agent-work/LESSONS.md` and `.agent-work/AGENT_FEEDBACK.md`. Committing it from this branch would
either be refused at closeout or require a human waiver that no one is present to give.

Per `constellation-commander-delegated` SKILL.md, "Fenced feedback/archive closeout": the gate is
**not waived**. The export is staged beside this note, for the Admiral to harvest before sweeping
this worktree.

**The episodes are unaffected and were not staged** — `episodes/` is a tracked path inside this
worktree, so lane K's seven episodes were written through
`scripts/apply_episode_delta.py --store-root episodes`, proved by
`verify_episode_captured.py 567-k --store-root episodes --phase feedback` (exit 0, 7 recorded), and
**committed on the branch**. The commit is what carries them out. Two assertions were afterwards
restated through the same writer because the observation guard read their leading words as
imperatives; the store was never hand-edited.

**Harvest target:** `.agent-work/staged-feedback/567-k/CONSTELLATION_FEEDBACK.md`.
