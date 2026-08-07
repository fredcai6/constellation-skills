# Excursion handoff: exc-7-simple-english

Full brief: `### EXCURSION_BRIEF exc-7-simple-english` in `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/IDEAS_BOARD.md` — read it first; it is the contract.

- **Task:** answer the brief's one named question — what should a simplified-technical-English standard for this project's reports look like, including a local glossary mechanism and mechanically checkable rules?
- **Why (the human's words, 2026-08-03):** "I think we're seeing issues because we're talking too jargony. we need to starting making discourse simple and direct. we should demand reports in American simplified technical English and build up a local glossary." Jargon is confusing the human AND suspected of confusing agents talking to each other.
- **Scope:**
  1. Research controlled/simplified English with primary sources: ASD-STE100 (the aerospace Simplified Technical English standard — writing rules + controlled dictionary), plain-language standards (e.g. US Plain Writing practice, ISO 24495-1), and anything credible on controlled language for machine/agent communication. Cite everything.
  2. Audit THIS repo's own writing for the jargon shapes that cause confusion: sample 3–5 human-facing artifacts (e.g. `.agent-work/epic-298/EPIC_SUMMARY.md`, a recent issue body, a closeout report) and name concrete offender patterns (coined terms used bare, metaphor-dense phrasing, nested qualifications).
  3. Draft, as a proposal for the human (do NOT ship into doctrine): ~10 writing rules fit for agent reports; the structure of a local glossary (where it lives, how terms get added, how agents are pointed at it — note `docs/agents/GLOSSARY.md` is referenced by doctrine today but does not exist); and 2–3 candidate mechanical checks (rules a linter could enforce, e.g. sentence length caps, term-not-in-glossary flags) — mechanization over prose is a project principle.
- **Exclusions:** no doctrine/skill edits, no issue writes; the ONLY file you write is the result artifact.
- **Success criteria / evidence:** every external claim cited; the repo audit quotes real sentences; the draft rules are concrete enough to apply to the next report verbatim.
- **No test surface:** research excursion.
- **Stop conditions:** report even if partial; scoped nulls — state what standards/sources you did NOT examine.
- **Result artifact (REQUIRED):** `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/evidence/exc-7-simple-english-RESULT.md`. Write fat there.
- **Return format:** thin — one verdict line + the artifact path.
