# Fence citation — 625-segmentation-substrate

This Commander run operates under Admiral launch order `ShipC-625` (epic #601, issue #625
Phase 1 segmentation substrate). Per the launch order's **File Ownership** section: "Sole
writer this wave: verdict `C:/Programs/f1Brainz/.agent-work/epic-601/wave2-625-verdict.md`;
workbench under your worktree `.agent-work/`" — this run is not granted write authority over
the shared, cross-commander durable logs at `C:/Programs/f1Brainz/.agent-work/AGENT_FEEDBACK.md`,
`LESSONS.md`, or `CONSTELLATION_FEEDBACK.md` (the standing `lesson:shared-files-not-on-mission-branch`).

Accordingly, this run's durable-log write is staged here
(`.agent-work/staged-feedback/625-segmentation-substrate/`: `AGENT_FEEDBACK.md`,
`lessons-delta.json`, `CONSTELLATION_FEEDBACK.md`) rather than written directly to the shared
main-checkout files, per `constellation-commander-delegated`'s fencing doctrine. The Admiral
harvests this trio into the shared durable root at epic closeout.

This staged trio's `lessons-delta.json` is validated: well-formed JSON, passes
`apply_lessons_delta.py`'s schema/field validation, confirmed via `--dry-run` against a
disposable scratch copy of `LESSONS.md`. The only rejection was the active-lesson CAP (20/20
already active in the current playbook) on the single `add` op
(`scope-self-authored-regression-to-import-graph`) — a business-rule the Admiral resolves at
real-apply time by retiring or deferring, not a malformed op. The 4 `confirm` ops (grounded in
this run's own artifacts) apply cleanly with no cap interaction.
