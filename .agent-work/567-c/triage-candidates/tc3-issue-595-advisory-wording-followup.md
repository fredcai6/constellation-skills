# Triage candidate: #595's context-trip advisory wording is still unedited

**Source:** `cmdr-567-c` (epic-567-door lane C).

**Statement:** #595's suggested resolution point 2 ("have the context advisory point at
`spine_halt block` as the sanctioned mid-run exit, rather than at a turn-end handoff the Stop hook
will not permit") targets the SOFT-band advisory's own wording (`_trip_advisory`,
`scripts/checklist_engine.py:1858-1861`: "hand off here… advisory — decline with a reason if you're
nearly done"). That string lives in `scripts/checklist_engine.py`, fenced to a concurrent lane this
wave, so this lane could not edit it directly.

**Disposition:** recommend-and-defer. Not filed as an issue this run (`decision:no-issue-filing`).
This lane judges #595's core ask (a stated, actionable precedence) already satisfied by editing the
two files it does own (`scripts/hooks/spine_rail.py`'s Stop-hook refusal and
`skills/commander/references/crew-dispatch.md`) — see `RETURN.md` for the reasoning. Recommend the
Admiral confirm whether that is sufficient closure for `#595`, or schedule a follow-up gate (once the
fence lifts) to also rewrite the advisory's own wording so both mechanisms carry the same statement
independently, not just the Stop hook.
