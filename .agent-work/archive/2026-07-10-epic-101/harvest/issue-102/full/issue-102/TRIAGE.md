# Triage — issue #102 (delegated; recommend-and-defer only)

Candidates harvested from crew out-of-scope observations. Filing authority was not sought/granted this
run and sibling issue #105 already owns hygiene, so every candidate routes to **recommend-and-defer**
(the triage user-decision cites the deferral itself, per delegated-mode doctrine). None fixed-now
(each is outside cluster A's 10 moves + net), none filed.

| # | Candidate | Source | Route | Reason |
|---|---|---|---|---|
| 1 | `skills/workbench/SKILL.md:3` typo "managemetn" → "management" | g1 impl | recommend-and-defer → #105 | Hygiene; #105 owns corpus hygiene this wave. Fenced from my ownership. |
| 2 | `_shared` → per-skill `references/` bundle-sync is not directly asserted anywhere; a role cites `references/global-everyone.md` while canonical is `skills/_shared/…` | g2 impl, reviewer | recommend-and-defer | The g7 content-pins now install + grep the bundled copies, so sync is implicitly exercised; a dedicated sync-integrity test is worthwhile future work, outside this cluster. |
| 3 | "clean-room reviewer subagent" method stated in both `admiral/SKILL.md` and `admiral/references/fleet-doctrine.md` | g5 impl+reviewer | recommend-and-defer | Mild residual redundancy; a candidate for a future consolidation pass (epic #101 spirit), not one of cluster A's 10 named moves — would be scope creep to fold in now. |
| 4 | Move-5 carrier pointers echo the section title "claimed side-effect"; standardizing on slug-style pointers would zero the echo | g4 reviewer | recommend-and-defer | Cosmetic; the moved principle prose is already gone from both carriers (residual test green). Future pointer-style convention. |

## Non-candidates (recorded, not triaged)
- The globally-INSTALLED `~/.claude/skills/constellation-*` copies are stale vs source (still carry
  banners etc.) — EXPECTED and correct: the launch order rules the source repo (`skills/`) is authority;
  installed copies refresh on the next `install_constellation.py` run. Not a defect, no candidate.

## Decision
All four candidates recommend-and-defer; no issues filed (no filing authority this run; #105 owns
hygiene). Surfaced to the Admiral in the return report for epic-level disposition.
