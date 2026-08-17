# Plan Alternatives — 567-d2

Design-it-twice, bias-to-yes. Panel-vs-single is a surfaced choice, not a silent default:
**single-author comparison, not a parallel dispatch panel** — the deciding evidence
(two pre-existing test suites' exact assertions, `discover_skills()`'s source) is empirical and
already gathered at `understand`, not a matter of architectural taste that benefits from
independently-framed candidates. A panel would re-derive facts I already hold, not surface new
ones. Named here as the untaken road.

## Candidate A — full deletion, as the launch order's line counts literally read

Delete `SKILL.md`, `checklist-engine.md`, `status-model.md` outright. Update
`tests/test_mcp_adoption.py` (Tier2/Tier3 constants + assertions), `tests/test_install_constellation.py`
(the post-install read-back), `tests/test_commander_evidence_convention.py` (repoint
`STATUS_MODEL`) to match. Deepest cut, matches the issue's literal framing.

- Depth: high (removes the whole surface at once).
- Locality: **poor** — forces edits into `tests/`, a path with no explicit owner this wave, and
  risks colliding with lane D1, which is independently removing 13 of 15 "CLI fallback" clauses
  from other skills this same wave and may need to touch `test_mcp_adoption.py` itself for the
  same reason.
- Testability: the two adoption-gate suites are deliberately hard to edit correctly (their own
  docstrings warn about two previous rounds of subtly-wrong loosening); rewriting them under this
  lane's own budget ("no design work remains") without independent review is real risk of
  reintroducing the exact defects those suites' history describes.
- Blast radius on `skills/_shared/global-everyone.md`'s pointer sentence to `checklist-engine.md`
  is unresolved either way (fenced to D1), so Candidate A does not even fully avoid it.

## Candidate B — partial, evidenced deletion (chosen)

Keep each of the 3 files present (satisfies `discover_skills()`) but shrink to exactly what
`understand`'s interrogation (q2/q3) measured as load-bearing: `SKILL.md`'s Tier2-pinned
default-path paragraph; `checklist-engine.md`'s `## MCP door` + `## Session lease` sections
(Tier3-pinned) plus its opening CLI-invocation line (needed by
`test_install_constellation.py`); `status-model.md`'s `Crew Return Status` section (needed by
`test_commander_evidence_convention.py` and `IMPLEMENTER_HANDOFF.template.md:106`, a file this
lane does not own). Delete everything else: TOC, Instantiate-from-template, Dispatch
subagent-vs-own-context, One-agent-one-plan, Two types, Verb loop, Refresh, Obey refusals,
Waive, Mechanism-guaranteed, Bubble-up channels, Context-read step, Template set (from
`checklist-engine.md`); Layout, Controller-prose, Closeout (from `SKILL.md`); Gate
Status/Review Verdict/Commander Gate Decision (from `status-model.md`).

- Depth: still a large cut — measured at plan time to remove roughly two-thirds of the original
  289 lines (exact count reported at `execute`).
- Locality: **good** — every edit stays inside `skills/workbench/**`, this lane's sole-write
  fence. Zero `tests/` edits, zero collision risk with D1 or any other lane.
- Testability: the full suite is the review surface; no test authorship risk, only content
  precision risk (get the retained sections byte-correct), which is verifiable directly with
  `grep`/`pytest -k` before commit.
- Matches `decision:establish-the-door-carries-it`'s actual instruction — "name anything the
  door does not carry" — literally: what's retained here **is** that named list.

## Convergence

**Candidate B.** It satisfies the same mission (redundant teaching content gone, door is now the
primary source for everything it actually carries) with materially lower blast radius and no
cross-lane collision risk, at the cost of a smaller line-count reduction than the issue's
original framing suggested — an honest-null on the exact 289-line target, not on the mission
itself. Reported as a deviation, per Stop Conditions / Inherited Latitude, in the run return.
