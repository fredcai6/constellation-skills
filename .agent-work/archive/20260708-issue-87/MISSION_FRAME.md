# Mission Frame — issue-87

## Intent
Post-epic reconcile: sync two design docs to shipped reality, rekey the lessons-playbook dormancy clock to distinct work-ids with a same-epoch guard, and disposition two hardening items (honest-null). **Frame shrunk:** this repo carries no Cartographer map (`docs/architecture/` absent — the issue itself records instantiating one as a future trigger). Anchors below are cut directly from code/doc truth verified at understand.

## Affected Capabilities
- capability:lessons-playbook-dormancy — `apply_lessons_delta.py` tick branch ages `runs_since_confirmed` per invocation and auto-deletes past `dormancy-runs`; this run rekeys aging to distinct work-ids and blocks same-epoch expiry.
- capability:design-doc-truth — `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` and `docs/CONSTELLATION_OVERVIEW.md` describe the recursive-improvement loop and role roster; this run syncs five verified stale spots.

## Structural Anchors
- struct:scripts/apply_lessons_delta.py — tick branch (~493-508), playbook-state header line (run-tick/cap/dormancy-runs counters), drill gate (~453-471).
- struct:tests/test_apply_lessons_delta.py — existing test surface for the delta applier (375-test suite, pytest).
- struct:docs/RECURSIVE_IMPROVEMENT_DESIGN.md:18,33-34,134 (retired Template Update Candidates), §5.2 (~391-399), §5.5 (~416-423).
- struct:docs/CONSTELLATION_OVERVIEW.md:4-13 (role roster), :36 (Cartographer consumer row).
- struct:scripts/agent_work_root.py — shipped durable-root that supersedes §5.5's sidecar proposal.

## Governing Constraints / Assumptions
- constraint:no-hand-edit-of-LESSONS — playbook mutated only via apply_lessons_delta.py; the dormancy change must keep cap/grounding/counter enforcement intact.
- constraint:constellation-lessons-pinned — constellation-scoped lessons never auto-delete; must survive the rekey untouched.
- constraint:mechanism-not-quality — the applier enforces mechanism only (same doctrine as the engine); the work-id dedupe must be mechanical (field presence/identity), not judgment.
- constraint:backward-compatible-playbook-state — existing LESSONS.md header (`run-tick=20 cap=20 dormancy-runs=10`) and per-lesson `runs-since-confirmed` fields must parse and migrate without hand edits.
- assumption:pC-cond-disjointness — p*/c* cond ids are disjoint in every template (verified); documented as the invariant instead of a refuse-on-ambiguity change (human decision, understand q2).

## Decision Anchors & Decision Pressure
- decision:dormancy-key=distinct-work-ids+same-epoch-guard (human, understand q1) — a lesson must not expire inside the epic/day that added it; repeat invocations from one run must not double-age.
- decision:item7-honest-null (q2), decision:item8-honest-null+doc-note (q3), decision:s5.5-rewrite-to-shipped (q4).

## Claims / Evidence Surfaces
- claim:test-suite-green — `python -m pytest tests/ -q` (375 tests) passes before close.
- claim:dormancy-behavior — new tests prove: same work-id ticks age a lesson once; a same-epoch burst cannot expire a lesson added in that epoch; constellation lessons still pinned.
- claim:doc-sync — each of the five doc spots verifiably reflects shipped state (grep-able markers per fix).

## Map Confidence / Staleness / Disputes
No map exists; code/doc truth was read directly at understand — no unverified area the plan depends on.

## Out of Scope
- Instantiating this repo's Cartographer map (recorded trigger only).
- verify_agent_feedback.py ordering enforcement (item 8 fix path — declined).
- attest refuse-on-ambiguity code change (item 7 — declined).
- Any LESSONS.md content edits.
