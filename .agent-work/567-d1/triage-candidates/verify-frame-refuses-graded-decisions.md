# verify-frame and decision-grading cannot both be satisfied in a repo with no map

**Observed, 567-d1 plan gate.** `map_orient.py verify-frame` refuses every `<prefix>:<id>` anchor
token in MISSION_FRAME.md when orientation is DEGRADED ("no map was read, so there is nothing for
a map anchor to be a member of"). Decision-fixedness doctrine requires graded `decision:<id>`
bullets in the frame's own "Decision Anchors" section. In this repo, which has no map at all,
satisfying one refuses the other: 14 problems reported, all of them legitimate decision/claim/
constraint anchors.

**Workaround used:** moved graded decisions to `.agent-work/567-d1/decision-anchors.md` and into
`execute.json`'s per-gate anchor blocks, leaving the frame citing only hash-pinned substitute
paths. FRAME-OK, 0 problems.

**Candidate fix:** under DEGRADED, accept anchor tokens that the frame *defines inline* rather
than refusing all of them; or give verify-frame a degraded-mode that checks substitute-path
citations and ignores anchor-shaped tokens instead of failing on them.
