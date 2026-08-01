# Triage recommendations — issue #104 (delegated run)

Authority note: this is a delegated run under an Admiral launch order that grants NO
direct issue-filing authority (Inherited Latitude fences filing). Every candidate lands
`recommend-and-defer`: the recommendation is produced here; the Admiral routes/files at
the epic boundary. None is filed by this run.

## tc1 — Ratify curator's reference bucket (DC1) [recommend-and-defer]
- **What:** confirm `SKILL_REFERENCE_BUNDLES["curator"] = _GLOBAL_EVERYONE` vs the
  `_GLOBAL_ORCHESTRATOR` alternative.
- **Evidence:** MISSION_FRAME DC1 carries the complete comparison. Curator is a solo,
  non-orchestrating, human-invoked role (chose everyone-tier, like interrogator/
  lessons-auditor). Cold-critic counter-evidence: scout+triage are orchestrator-bucket
  despite dispatching no crew; a scout-analogy would put curator there. Chose everyone on
  the epic's per-invoker tailoring intent (curator exercises none of the orchestrator-only
  payload).
- **Acceptance:** human ratifies at epic return. Reversible one-line bucket swap if the
  epic prefers scout-consistency.

## tc2 — SKILL_NAMES fragility (tooling) [recommend-and-defer]
- **What:** `tests/test_install_constellation.py` pins a hardcoded skill-name list that a
  full-set install assertion compares for equality; every new skill must hand-update it
  (this run did). Consider deriving it from `discover_skills()` / a single source so a new
  skill can't silently break/pass the set assertion.
- **Evidence:** the critic BLOCKER for this run traced to exactly this fixture; folded the
  one-line fix into G2.

## tc3 — Residual duplication: engine-invocation restatement (curator first-run) [recommend-and-defer]
- **What:** the engine-invocation absolute-path rule is restated inline across 5 SKILL.md
  files (charter, implementer, interrogator, lessons-auditor, reviewer) rather than
  pointing at its canonical statement.
- **Evidence:** flagged by BOTH curate_corpus.py AND the independent fresh-context sweep
  (ACCEPTANCE_NOTE). Real doctrine prose, not a pointer. A natural first target for the
  curator's first real mend/route run.

## tc4 — Residual duplication: crew Workflow-Feedback paragraph [recommend-and-defer]
- **What:** implementer/reviewer share a near-verbatim "Workflow Feedback" paragraph (one
  word differs) + the "proof-of-life" instruction. Candidate to hoist into a shared
  crew-tier doctrine file (global-crew.md) with a per-role pointer.
- **Evidence:** curate_corpus 35-shingle cluster + independent sweep both flagged it.

## tc5 — SKILL_INDEX.md coverage gap (pre-existing) [recommend-and-defer]
- **What:** SKILL_INDEX.md lacks entries for docent, explorer, prototyper (predates #104).
  Backfill against the discovered-skill set; consider a test asserting the index covers
  every discovered skill.
- **Evidence:** G4 reviewer independently confirmed via `grep '^##' SKILL_INDEX.md`.

## tc6 — curate_corpus.py v2 matching refinements (minor) [recommend-and-defer]
- **What:** description-exclusion matches substring "not " anywhere; person-check
  shortlists on "us". Both mechanical/shortlist-only (never verdicts, by design T7).
  Refine matching if a future run finds the false-positive rate noisy.
- **Evidence:** G3 implementer + reviewer out-of-scope observations.
