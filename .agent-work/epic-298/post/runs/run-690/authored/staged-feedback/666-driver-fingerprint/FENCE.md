# Fence citation — 666-driver-fingerprint

This Commander run operates under the Constellation Admiral's frozen launch order `LAUNCH_ORDER-666.md`
(epic #659 Wave 3, issue #666 DriverFingerprint). Per that order's **Constraints & hygiene** section:
"Stage the feedback trio (AGENT_FEEDBACK + lessons-delta.json + CONSTELLATION_FEEDBACK) under
`.agent-work/staged-feedback/666-driver-fingerprint/` with a `FENCE.md` citing this launch order; satisfy your
feedback/archive gate against that staging dir." and "Do NOT commit any `.agent-work/` path on the mission
branch." This is the standing `lesson:shared-files-not-on-mission-branch` (confirmed across every prior
delegated-commander run this repo has logged): the shared durable logs at
`C:/Programs/f1Brainz/.agent-work/{AGENT_FEEDBACK,LESSONS,CONSTELLATION_FEEDBACK}.md` are cross-commander
canonical state this run is not granted write authority over.

Accordingly, this run's durable-log write is STAGED here (`.agent-work/staged-feedback/666-driver-fingerprint/`:
`AGENT_FEEDBACK.md`, `lessons-delta.json`, `CONSTELLATION_FEEDBACK.md`) rather than written to the shared
main-checkout files, per `constellation-commander-delegated`'s fencing doctrine. `verify_agent_feedback.py`
accepts this staged trio in lieu of the durable-root write. The Admiral harvests this trio into the shared
durable root at epic closeout (heeding `lesson:harvest-collected-not-verified-merged` — collected ≠ merged).

`lessons-delta.json` is well-formed JSON (6 ops: 4 confirm + 1 mention on tracked lessons, tick=true) and is
validated below via `apply_lessons_delta.py --dry-run` against a disposable scratch copy of LESSONS.md. The
worktree `verify_lessons_applied.py` gate is already clear (no ripe lesson awaiting apply-or-defer).
