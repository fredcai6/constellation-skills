# Candidate: template-sequential

**Constraint (assigned):** one gate per template, in file-ownership/priority order. Each gate
bundles that template's full lifecycle — assess every `check: null` condition's bucket, promote
the bucket-2 ones with real check kinds, red-prove each promotion against a mutation, update any
doc that cites stale counts for that template — before moving to the next template.
`COMMANDER_SPINE.template.json` goes first (the launch order's concrete starting point:
`scripts/validate_spine.py skills/commander/templates/COMMANDER_SPINE.template.json` exits 1 today
on 2 `falsifiable-all-null` faults, `init` and `reconcile`). The `validate_spine.py` wiring-scope
decision is its own gate.

## 0. Ordering rationale (file-ownership/priority)

All 8 templates are `skills/*/templates/*.json`, owned solely by this lane. Priority order:
COMMANDER_SPINE first (mandated); then EXECUTE_PLAN, same directory
(`skills/commander/templates/`) and the child checklist COMMANDER_SPINE's own `plan.c2` authors —
context and any seam decision from g1 carries over directly; then ADMIRAL_SPINE, the other
orchestrator "_SPINE" bookend template and the largest remaining null count (10); then
EXPLORER_SPINE (10, same `_SPINE` bookend family, upstream of Commander); then CHARTER (10,
bootstrap role, lower run-frequency than the three spines); then IMPLEMENTER_PLAN (3, crew-tier
child, mirrors EXECUTE_PLAN's "child plan artifact" shape); then CARTOGRAPHER (5) and SCOUT (4),
both single-purpose audit templates with no orchestrator bookends, least central to the corpus.
`validate_spine.py` wiring is a corpus-wide decision — it needs the *post-promotion* fault count
from every template gate, so it lands last (g9), not interleaved.

## Gate sequence

```
g1-commander-spine
  imperative: |
    skills/commander/templates/COMMANDER_SPINE.template.json, 19 check:null conditions
    (init.c1, context.c1, understand.p1, plan.p1, plan.c1, plan.c2, plan.c4, plan.c5, execute.p1,
    execute.c1, reconcile.p1, reconcile.c1, triage.p1, triage.c1, review.p1, feedback.p1,
    archive.p1, archive.c2, archive.c3). Re-verify fresh w2-basis's 5 clean conversions (plan.c1,
    plan.c4, plan.c5, reconcile.c1, archive.c2 — plan-candidate-artifact-conversion.md §2) against
    this run's own decision:blocking-where-adjudicated authority, which w2-basis explicitly lacked.
    Re-open init.c1: w2-basis called it "wrong kind" for an artifact check but conceded the honest
    check is command-kind (read spine.json's own engine_session.status, which `claim` already
    writes) — that IS a real check kind under decision:no-new-check-kinds, so this run's fresh
    assessment promotes init.c1 as bucket-2/command where w2-basis left it unconverted. Re-open
    archive.c3 similarly (user-decision-evidence pattern already used 3x in this file by
    archive.c5/review.c1/triage.c2). Record bucket (1/2/3) for all 19, not just the promoted ones.
  close criteria:
    - all 19 conditions have a recorded bucket in .agent-work/w3-promote/notes-1.md
    - promoted conditions (at least the 6: plan.c1, plan.c4, plan.c5, reconcile.c1, archive.c2,
      init.c1) carry check.kind in {artifact, command, git-change-policy}, no other condition
      changed, file remains valid JSON (parse-check only, never round-tripped)
    - partition compared against the 9/19 baseline; if this template (the source of that baseline)
      still measures 9/19 that's confirmatory, not a finding — the material-exception check bites
      starting at g2
    - .agent-work/templates/ overlay mirror in sync
  required evidence: file-diff (hand-edit + overlay), command-output (JSON parse-validate)
  constraints: decision:no-new-check-kinds; decision:no-basis-backfill; hand-edit raw text only

g2-red-proof-commander-spine
  imperative: |
    For each condition promoted in g1, add/extend a pytest test in tests/test_checklist_engine.py
    pinned to this gate's shipped commit, mutating the shipped revision the way an attacker would
    (not the author's own designed falsifier) — e.g. for init.c1's new command check, mutate
    spine.json's engine_session.status to a value claim never writes and assert attest()/advance()
    refuses with the specific message, not a bare non-zero exit. Update GoldenOutputBriefing
    fixtures for every line whose kind changed (was null, now artifact/command). Every later
    per-template gate (g3, g4, g5, g6, g8) repeats this red-proof step inline rather than as a
    separate numbered gate — g2 exists standalone only because COMMANDER_SPINE is the largest,
    highest-traffic template and its promotions deserve a dedicated close before the rest proceed.
  close criteria: one red-proof per promoted condition, each demonstrably red pre-g1 and green
    post-g1; full tests/test_checklist_engine.py green
  required evidence: command-output (pytest, full file, before/after)
  constraints: decision:red-proof-each-promotion — mutation not self-designed; no engine code edit

g3-execute-plan
  imperative: |
    skills/commander/templates/EXECUTE_PLAN.template.json, 4 null conditions (e0-context.c1,
    g1-implement.p1, g1-review.p1, g1-integrate.p1). g1-implement.p1's statement is itself a
    template placeholder ("<qualitative dependency on a prior gate, or none>") — record that
    verbatim rather than forcing a promotion on templated text. g1-review.p1 ("IMPLEMENTER_RESULT
    received") and g1-integrate.p1 ("REVIEW_RESULT received") are real-locator candidates:
    docs/CHECK_SCRIPT_CENSUS.md already lists verify_iterative_role_artifacts.py wired live at
    EXECUTE_PLAN's own execute step — assess whether the same script/command-kind check applies to
    these receipt conditions, or whether "received" is redundant with gate order (same reasoning
    as w2-basis's precondition finding for COMMANDER_SPINE, re-derived fresh here since EXECUTE_PLAN
    is a different template).
  close criteria: all 4 bucketed and recorded; promoted conditions carry a real check kind;
    partition compared to 9/19 — flag as material exception if it diverges materially (note: n=4 is
    a small sample, so record the raw count alongside the percentage, per the Honest-Null Clause)
  required evidence: file-diff, command-output (parse-validate), red-proof test per promotion
  constraints: same as g1; child-checklist shape (EXECUTE_PLAN is itself instantiated per-run) —
    confirm the promoted check survives generate_spine.py's compile step, not just the raw template

g4-admiral-spine
  imperative: |
    skills/admiral/templates/ADMIRAL_SPINE.template.json, 10 null (init.c2, latitude.p1,
    latitude.c1, execute.p1, execute.c1, execute.c2, closeout.p1, closeout.c1, closeout.c3,
    closeout.c4). init.c2 ("engine session lease claimed") is the same fact as COMMANDER_SPINE's
    init.c1 — reuse g1's command-kind seam decision directly rather than re-deriving it. execute.c2
    ("ADMIRAL_LOG current through the last wave") has a real file locator (ADMIRAL_LOG) and mirrors
    COMMANDER_SPINE's reconcile.c1 file-diff pattern already converted in g1 — likely bucket 2.
    closeout.c4 ("branches dispositioned, worktrees swept, ADMIRAL_LOG archived") is a candidate
    partial: "worktrees swept" is command-checkable (`git worktree list`), "branches dispositioned"
    is judgment — assess as a split condition the way w2-basis split COMMANDER_SPINE's context.c1.
  close criteria: all 10 bucketed; promotions ship with real check kind; partition vs 9/19 compared
    — this is the first template where a material-exception float genuinely becomes possible per
    decision:record-the-partition-per-condition
  required evidence: file-diff, command-output, red-proof test per promotion
  constraints: same as g1; if init.c2's promotion literally duplicates g1's init.c1 check shape,
    cite g1 rather than re-justifying from scratch (locality payoff of doing COMMANDER_SPINE first)

g5-explorer-spine
  imperative: |
    skills/explorer/templates/EXPLORER_SPINE.template.json, 10 null (init.c2, context.p1,
    context.c1, explore.p1, spec.p1, spec.c1, review.p1, confirm.p1, route.p1, route.c1).
    context.c1's "IDEAS_BOARD.md seeded from template" half has a real file locator (bucket 2);
    spec.c1's "DESIGN_SPEC.md crystallized... with per-section approval; load-bearing interfaces
    designed" splits like COMMANDER_SPINE's plan.c2 — the file-exists half converts, the
    approval/interface-fidelity half resists as a judgment claim. docs/CHECK_SCRIPT_CENSUS.md
    already lists verify_spec_confirmed.py wired live at this template's spec/review steps and
    verify_cycles.py at :37 — check whether either script's command-kind pattern extends to
    route.c1 ("confirmed spec routed... worked example present") before inventing a new locator.
  close criteria: all 10 bucketed; promotions carry real check kind; partition vs 9/19 recorded
  required evidence: file-diff, command-output, red-proof test per promotion
  constraints: same as g1; do not touch the `basis` field even though DESIGN_SPEC.md's
    per-section-approval claim is exactly the kind of thing basis was built for — decision:no-
    basis-backfill applies here as much as everywhere else in this corpus

g6-charter
  imperative: |
    skills/charter/templates/CHARTER.template.json, 10 null (context.c1, explore.c1,
    interrogate.p1, interrogate.c1, rigor.p1, rigor.c1, orchestrator-context.p1, agent-guide.p1,
    project-templates.c1, closeout.c1). project-templates.c1 ("project-specific templates seeded")
    has a real locator — the seeded files under skills/*/templates/ or docs/agents/ themselves,
    checkable via git-change-policy (files changed this run) or artifact (file exists) — bucket 2.
    closeout.c1 ("durable outputs complete; work area archived") partially mirrors COMMANDER_SPINE's
    archive gate pattern (g1) for the archive-move half; "durable outputs complete" is judgment.
  close criteria: all 10 bucketed; promotions carry real check kind; partition vs 9/19 recorded —
    CHARTER runs once per repo rather than per-issue, note that frequency difference in the record
    since it affects how much a false-negative here costs relative to COMMANDER_SPINE
  required evidence: file-diff, command-output, red-proof test per promotion
  constraints: same as g1

g7-implementer-plan
  imperative: |
    skills/implementer/templates/IMPLEMENTER_PLAN.template.json, 3 null (m0-context.c1, m1.p1,
    m1.c1). m1.c1's own statement text already flags itself — "TDD red... manual attest; che[cked
    by...]" — record that as a self-declared bucket-1/3 case rather than forcing a fit to hit a
    conversion count, per decision:promote-only-conditions-with-a-real-locator (cited in
    MISSION_FRAME.md's Decision Anchors). This is the smallest population (n=3) in the corpus —
    honest-null here is a legitimate outcome the launch order explicitly wants surfaced, not a
    shortfall.
  close criteria: all 3 bucketed and recorded with reasoning; if 0 promote, that is a valid close
    (Honest-Null Clause) — record assessed-vs-promoted counts explicitly, not just the promoted list
  required evidence: file-diff (if any promotion), command-output (parse-validate regardless)
  constraints: same as g1; do not manufacture a locator to avoid an honest zero

g8-cartographer-and-scout
  imperative: |
    CARTOGRAPHER.template.json (5 null: context.c1, packets.p1, packets.c1, index-overlays.c1,
    map-compliance.c1) and SCOUT.template.json (4 null: context.c1, audit.p1, audit.c1,
    report.c1) — both single-purpose audit templates, grouped as the last, lowest-priority gate.
    packets.c1 ("touched packets reflect current code") and index-overlays.c1 ("index and overlays
    consistent with packets") are command-kind candidates if a live consistency checker exists for
    map/INDEX.md (check docs/CHECK_SCRIPT_CENSUS.md's unwired list — check_role_spine_bookends.py
    and check_skill_freshness.py are both unwired but real, tested scripts; wiring one via an
    existing command-kind check is promotion, not new machinery, per decision:no-new-check-kinds).
    SCOUT's report.c1 ("SCOUT_REPORT written; candidates routed") splits the same way as
    EXPLORER_SPINE's spec.c1 — file-exists half converts, routing-judgment half resists.
  close criteria: all 9 (5+4) bucketed across both files; promotions carry real check kind;
    partition vs 9/19 recorded per template (not pooled) per decision:record-the-partition-per-
    condition — CARTOGRAPHER and SCOUT are grouped in one gate for priority-ordering only, the
    per-condition record stays per-file
  required evidence: file-diff x2, command-output x2, red-proof test per promotion
  constraints: same as g1; this run's map is DEGRADED-UNPARSEABLE (MISSION_FRAME.md) — do not let
    CARTOGRAPHER's own promoted checks depend on map state this repo currently cannot produce

g9-validate-spine-wiring
  imperative: |
    Corpus-wide decision, deliberately last: it needs the post-promotion fault count from g1-g8.
    tests/test_validate_spine.py already runs two corpus sweeps — TestShapeAcceptsEveryShippedTemplate
    (zero-tolerance, blocking, on shape faults) and TestCorpusSweepFindings::test_measured_finding_
    totals (a FLOOR, `by_code.get("falsifiable-all-null", 0) >= 15`, "measured 21 at authoring
    time"). Re-run `python3 -m pytest tests/test_validate_spine.py -q` after g1-g8 land. If
    COMMANDER_SPINE's init/reconcile gates (this wave's named starting point) and any other
    all-null gates promoted along the way cleared their falsifiable-all-null faults, the true count
    has dropped below 21. Decide with the Admiral: (a) ratchet the `>= 15` floor down to the freshly
    measured number (report-only, stays a regression floor), or (b) tighten to a blocking `== 0`
    zero-tolerance assertion for the 8 templates this wave touched specifically (mirroring the
    shape-fault test's already-blocking pattern) — per decision:validate-spine-wiring-is-in-scope's
    settle clause: "count the faults across all shipped templates first, then decide with the
    Admiral." If any of the 4 templates this lane does not own (or faults this wave didn't fix)
    would go red under (b), float that scope question rather than fixing or suppressing it.
  close criteria: fresh corpus fault count measured and pasted; a recorded Admiral decision on
    floor-ratchet vs blocking-tightening; whichever is chosen is implemented in
    tests/test_validate_spine.py with the pin comment updated to this run's measurement, not left
    citing the stale "measured 21/23"
  required evidence: command-output (pytest re-run), user-decision (Admiral)
  constraints: decision:validate-spine-wiring-is-in-scope — do not fix faults outside this lane's
    8 templates to make (b) pass; float instead
```

## Tradeoffs

- **Depth:** full per template, by construction — g1 does not close until COMMANDER_SPINE's
  promote/red-proof/doc-sync cycle is complete, so any single gate is independently auditable and
  droppable without leaving a template half-promoted. The cost is that depth is bought serially:
  whether ADMIRAL_SPINE or CHARTER partitions like COMMANDER_SPINE's 9/19 is unknown until that
  template's own gate (g4, g6), not at the start.
- **Locality:** highest available under this mission. Each gate's blast radius is exactly one
  template file plus its `.agent-work/templates/` overlay (g8 is the one exception, two files, kept
  together only for priority-ordering, with per-file records preserved) — a regression bisects to
  one gate/commit, matching the file-ownership boundary the launch order already grants this lane.
- **Seam placement:** the same seam question repeats per template rather than being settled once.
  "Is engine-session-lease-claimed a command-kind read of spine.json's own state, or a wrong-kind
  artifact ceremony" is literally the same question at COMMANDER_SPINE's `init.c1` (g1) and
  ADMIRAL_SPINE's `init.c2` (g4), three gates apart. g4 is written to cite g1 rather than
  re-litigate, which is the discipline this shape requires to avoid drift — nothing in the
  constraint itself prevents g4 answering it differently than g1 if the assessor's judgment shifts.
- **Testability:** strong within a gate — each promotion gets its own red-proof, scoped to that
  template's own fixtures (GoldenOutputBriefing per template). The one testability surface that
  cannot be gate-local is `tests/test_validate_spine.py`'s corpus-wide floor, which sums faults
  across all 8 templates — that is exactly why g9 is a dedicated last gate instead of touched
  piecemeal in g1-g8: tightening it early would either be premature (before g8's faults are known)
  or require re-touching the same assertion 8 times.

## Verdict

TEMPLATE-SEQUENTIAL is good at producing bounded, independently auditable, revertible units of
work: every gate ships a complete story (assessed, promoted, red-proved, docs synced) for one file,
so a reviewer — or the Admiral, mid-wave — can accept g1-g5 and defer g6-g8 without anything left
half-done. It is weak at surfacing the launch order's own named risk early: the entire ~65-condition
extrapolation rests on one template's 9/19 measurement, and
`decision:record-the-partition-per-condition` calls a materially different partition on any other
template a stop-and-float event. A "measure everything first, then promote everything" alternative
would run a single corpus-wide bucket-assessment pass before writing a single promotion, and would
therefore see a divergent template (say, CARTOGRAPHER partitioning at 1/5 instead of ~47%) at its
own gate 1 — cheaply, before any red-proofs or doc edits exist to unwind. TEMPLATE-SEQUENTIAL
instead discovers that same divergence only when it arrives at that template's gate, which could be
g7 or g8, several templates' worth of committed work later. The seam-repetition cost (re-deriving
the same command-vs-artifact judgment per template) is the other real price of this shape; a
measure-first pass amortizes that judgment once. What TEMPLATE-SEQUENTIAL buys in exchange is a
wave that can be safely interrupted or partially merged at any gate boundary — which matters more
here than early divergence-detection does, given this is explicitly the epic's final wave and every
prior wave in this epic has had at least one relaunch-from-refresh-request.
