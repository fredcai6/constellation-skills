# Triage candidate: #442's target text is fenced to a concurrent lane

**Source:** `cmdr-567-c` (epic-567-door lane C), floated to the Admiral at `understand`/`plan`; see
`RETURN.md` and `notes-c.md` for the full evidence trail.

**Statement:** #442's two problem instances — the `RAIL:` banner text (`_RAIL_STRINGS`,
`scripts/checklist_engine.py:310-326`) and the HARD refusal's `attach ... refresh-request` remedy
string (`_refresh_attach_hint`, `scripts/checklist_engine.py:1532-1543`) — are both authored inside
`scripts/checklist_engine.py`, which the launch order fences to Lane A this wave (`#559`) and which
the file itself marks FROZEN/verbatim ("do not paraphrase" — a measurement precondition for `#145`).
This lane's sole-owned file, `scripts/hooks/spine_rail.py`, does not contain either string. #442
cannot be closed by this lane; its acceptance criterion (a cold agent acting correctly on the actual
banner/refusal text) requires editing text this lane cannot legally touch.

**Disposition:** recommend-and-defer. Not filed as an issue this run (`decision:no-issue-filing`).
Recommend: once Lane A's `checklist_engine.py` edits this wave are merged (or the fence is explicitly
lifted for this file), a follow-up wave rewrites `_RAIL_STRINGS` and `_refresh_attach_hint`'s output
for cold-agent readability, then measures the rewrite on real cold agents per
`decision:measure-on-real-agents` — the same acceptance bar this lane could not spend budget on
without text to measure.
