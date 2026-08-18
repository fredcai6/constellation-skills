# Decision anchors for lane D1 — carried here, and into execute.json

`map_orient.py verify-frame` refuses ANY `<prefix>:<id>` anchor token in the mission frame
when orientation is DEGRADED, because with no map read there is nothing for an anchor to be
a member of. Decision-fixedness doctrine (`global-everyone.md`) nonetheless requires graded
`decision:<id>` bullets. The two mechanisms conflict in a repo with no map. Resolution: the
frame cites only hash-pinned substitute PATHS, and the graded decisions live here and in
`execute.json`, where each `leans <gate-id>` actually resolves. Staged as a triage candidate.

## Decision Anchors & Decision Pressure

- decision:complete-sweep — sweep all 13 clauses in my files, not all-but-one.
  `@grade: settled/human · leans g1,g2,g3 · settle: n/a — the human ruled it verbatim`
- decision:guard-is-the-deliverable — a deletion with no failing-guard demonstration does not close #559.
  `@grade: settled/doctrine · leans g4`
- decision:two-engine-sites-are-not-targets — the plan record and the `init_work_area.py` comment survive.
  `@grade: settled/doctrine · leans g3,g4`
- decision:guard-scope-is-the-existing-corpus-walk — express "agent-facing" by reusing `test_mcp_adoption.py`'s `INSTRUCTION_FILES` rglob over `skills/` for `.md`/`.json`, rather than inventing a scope or listing exceptions.
  `@grade: settled/measured · leans g4 · settle: done — measured, all 10 target files IN, both pre-ruled survivors OUT, every historical record OUT, exception list length zero`
- decision:second-checklist-clauses-are-reworded-not-deleted — the 3 clauses naming a path the door provably cannot reach lose the "fallback" framing but keep the path, stating the measured reason.
  `@grade: guess · leans g2 · settle: floated to the Admiral; red-proof shows the guard still catches a genuine reintroduction at these same sites`
- **Decision pressure**: `tests/test_mcp_adoption.py` and `tests/data/store_mentions.approved.txt` are in **no** lane's ownership list. The sweep is impossible without editing the first. Surfaced to the Admiral as an ownership gap; proceeding because no other lane owns them, so there is no collision risk.

