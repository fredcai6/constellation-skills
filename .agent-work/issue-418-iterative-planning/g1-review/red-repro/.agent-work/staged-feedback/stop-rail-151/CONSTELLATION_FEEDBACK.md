# Constellation Feedback (staged exports) — stop-rail-151

Cross-repo / shared-machinery exports from this run, for the upstream Constellation sweep.

## Exports this run

None — confirmed after review. This run fixed a project-local safety-rail bug
(`scripts/hooks/spine_rail.py`, vendored in this repo). No recurring
shared-machinery (checklist_engine / skills-corpus / cross-repo) defect was hit:
the engine, run_crew, verifier, and spine templates all behaved as designed. The
one banked lesson (`verify-harness-field-and-drive-real-writer`) is project-scoped
testing discipline, not a constellation-scoped machinery defect, so it is banked
in lessons-delta.json rather than exported here.

The spine_rail hook itself IS shared machinery (it guards every Constellation
fleet run under a hooked project dir), and this fix removes a false-positive that
broke every background-wave dispatch — but that is delivered as the PR under
review, not as an upstream feedback export.
