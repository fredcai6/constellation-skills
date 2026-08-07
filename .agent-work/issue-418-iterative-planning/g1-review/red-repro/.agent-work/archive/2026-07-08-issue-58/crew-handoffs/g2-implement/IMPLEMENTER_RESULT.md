# Implementer Result — g2 (Explorer engine artifacts + verifier cross-check)

## Rework note (attempt-2 — document correction only)

Reviewer verdict BLOCK on finding **BL-1** (see `crew-handoffs/g2-review/REVIEW_RESULT.md`):
the "Full suite" evidence section of attempt-1 mis-attributed the 31 failures as
"all 31 in tests/test_install_constellation.py". That is wrong. The true
distribution is **26 in tests/test_install_constellation.py + 5 in
tests/test_feedback_tooling.py** — the root-cause conclusion (missing
`skills/explorer/SKILL.md`) was correct but the per-file attribution was
under-inclusive. This attempt corrects the attribution only. **No deliverable,
code, or template changed; commit `a49c8a0` stands unchanged** (no new commits).
The corrected sections below are the "Full suite" evidence block and the
diagnostic paragraph.

## Completed slice

Authored the constellation-explorer engine-facing templates and the
verifier↔template cross-check test. All four NEW files delivered; the targeted
cross-check suite is green. Commit `a49c8a0` on `constellation/issue-58`.

The one open item is NOT a defect in this gate's deliverables: the full suite is
transiently red because `skills/explorer/` now exists with only `templates/` and
no `SKILL.md` (that is g4) — see Stop conditions below. This is a plan-ordering
consequence the g2-integrate override_policy exists for, not a fault in the
templates or the cross-check test.

## Files changed (all NEW, all in Allowed Scope)

- `skills/explorer/templates/EXPLORER_SPINE.template.json`
- `skills/explorer/templates/CYCLE.template.json`
- `skills/explorer/templates/DESIGN_SPEC.template.md`
- `tests/test_explorer_templates.py`

No files outside Allowed Scope were touched. `scripts/*`, `skills/explorer/SKILL.md`,
the other explorer templates, `skills/prototyper/**`, `skills/_shared/**`,
`install_constellation.py`, and the design spec were left untouched.

## Design notes (how the contract was met)

- **Spine steps** exactly `init, context, explore, spec, review, confirm, route`.
  Inline `config.rework_cap: 99` (no `config_ref` — the whole point is a repo with
  no engine-config file). Every bundled-script path uses the generic `<skill-dir>`
  token; no `<commander-skill-dir>` leaks in.
- **explore** closes on an `artifact`/`user-decision` postcondition AND a `command`
  postcondition running `verify_cycles.py <work-id>`.
- **review** runs `verify_spec_confirmed.py <work-id> --phase review`.
- **confirm** has an `artifact`/`user-decision` postcondition AND a `command`
  postcondition running `verify_spec_confirmed.py <work-id>` (default/confirm phase,
  no `--phase`).
- **route** statement covers the three human routes (to-issues/Commander hand-off /
  file a shaped-design issue / shelve with the `UNCONFIRMED — DO NOT CUT` header),
  archive, and lease release.
- **CYCLE** is a `type: survey` with `consolidation: null` as shipped and a
  top-level `flavor` placeholder naming shotgun|compare|refine — exactly what
  `verify_cycles.py` keys on; instantiated files are `cycle-<N>.json`.
- **DESIGN_SPEC** ships a standalone `**UNCONFIRMED — DO NOT CUT**` banner line
  (trips the verifier's marker refusal on BOTH phases), a DRAFT Confirmation block,
  and the fixed columns `| ID | Lens | Severity | Finding | Disposition | Reason |`
  with the sample row's Disposition/Reason cells EMPTY (so a marker-stripped draft
  still fails review on the incomplete table). The marker is the only standalone
  marker line, so removing it + flipping the Status/fields yields a spec the
  verifier passes. Every other mention of the marker (banner-removal note, route
  doctrine) is inline in prose, so it does not trip the standalone-line refusal.

## Test mode

Test-after; the cross-check test file IS a gate deliverable. All mandated red
cases present: DRAFT refused on both phases (marker), incomplete-table review
refusal, each Confirmation field blanked independently, zero-cycles, and
one-unconsolidated-among-consolidated.

## Evidence (pasted)

### Targeted cross-check suite — green

```
$ python -m pytest tests/test_explorer_templates.py -q
......................                                                   [100%]
22 passed in 0.39s
```

### verify_spec_confirmed.py refuses the shipped DRAFT template (both phases)

```
$ python scripts/verify_spec_confirmed.py skills/explorer/templates/DESIGN_SPEC.template.md --phase confirm
REFUSED: shaped-design spec is marked UNCONFIRMED -- DO NOT CUT: '**UNCONFIRMED — DO NOT CUT**'
confirm exit=1
$ python scripts/verify_spec_confirmed.py skills/explorer/templates/DESIGN_SPEC.template.md --phase review
REFUSED: shaped-design spec is marked UNCONFIRMED -- DO NOT CUT: '**UNCONFIRMED — DO NOT CUT**'
review exit=1
```

### Transformation matrix (template edited into CONFIRMED, one field at a time)

```
FAIL raw-draft (confirm): REFUSED ... UNCONFIRMED -- DO NOT CUT
FAIL raw-draft (review): REFUSED ... UNCONFIRMED -- DO NOT CUT
FAIL review-incomplete (review): findings table has empty Disposition cell(s) at data row(s) [1]
PASS review-pass-draft (review)
PASS confirmed (review)
PASS confirmed (confirm)
FAIL blank-confirmed-by (confirm): Confirmed by is missing or empty   [confirmed_by field: '']
FAIL blank-date (confirm): Date is missing or empty                   [date field: '']
FAIL draft-status (confirm): Status is not CONFIRMED (found 'DRAFT')
```

### verify_cycles.py green + red against CYCLE-template-derived fixtures

```
zero cycles:            fail OK ("no cycle-*.json files found ... zero cycles")
unconsolidated (as-is): fail OK ("... unconsolidated (consolidation: null)")
consolidated x2:        PASS OK
```

### Engine claim/start transcript for the instantiated spine

```
$ init_work_area.py --spine EXPLORER_SPINE.template.json --skill-dir <repo>
no <skill-dir> residual: True | has scripts/verify_cycles.py: True | has scripts/verify_spec_confirmed.py: True
$ checklist_engine.py --file spine.json claim --session-id explore-topic --claimed-by explorer --worktree .
claim exit 0: claimed lease explore-topic -> active
$ checklist_engine.py --file spine.json start init --session-id explore-topic
start exit 0: init -> in-progress
```

### Full suite (transiently red — see Stop conditions)

```
$ python -m pytest tests/ -q
31 failed, 389 passed, 1 skipped, 14 subtests passed

$ python -m pytest tests/ -q 2>&1 | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
     5 FAILED tests/test_feedback_tooling.py
     26 FAILED tests/test_install_constellation.py
```

**All 31 failures share one root cause: `skills/explorer/` exists with only
`templates/` and no `SKILL.md`, which `install_constellation.py::discover_skills`
refuses (`InstallError: source skill is missing SKILL.md: skills/explorer`).** The
distribution across two files:

- **26 in `tests/test_install_constellation.py`** — install runs that hit
  `discover_skills` directly.
- **5 in `tests/test_feedback_tooling.py`** — their `setUp` calls
  `install_constellation.main()` to stage a fixture skills tree, so they hit the
  identical refusal at `install_constellation.py:625`. Confirmed by grepping their
  traceback: `raise InstallError(f"source skill is missing SKILL.md: {source_path}")`.

Diagnostic: a stub `skills/explorer/SKILL.md` (added and immediately removed)
collapsed the set **31 → 2**, with **all 5 `test_feedback_tooling.py` failures
clearing** — confirming the shared root cause. Of the 2 that remain with a stub
present, both are in `test_install_constellation.py`: they are the expected-skills
list assertions that still lack `constellation-explorer`/`constellation-prototyper`
(resolved by g5). The 29 that cleared are purely `discover_skills` refusing
`skills/explorer/` for its missing `SKILL.md` (resolved by g4). Zero failures
relate to the g2 templates or the cross-check test.

## Assumptions used

- Instantiate with `--skill-dir <repo-root as POSIX>` so command postconditions
  resolve to the real script files and the substituted path stays valid JSON on
  Windows (backslashes would break `json.loads`). This mirrors the g1
  `test_init_work_area.py` explicit-skill-dir path.
- No `engine_session` key in the shipped spine (matches the commander template);
  the lease is created at runtime by `claim`.
- The engine ignores unknown top-level keys (`flavor`, `cycle`), verified by the
  passing claim/start and by `verify_cycles` reading only `type`/`consolidation`.

## Stop conditions hit

None that block the deliverables. One surfaced conflict, per the "surface conflicts,
don't improvise" instruction:

- **Full-suite-green vs Allowed Scope conflict.** The Close Criteria ask for
  `pytest tests/ -q` green, but creating `skills/explorer/templates/` (a required
  deliverable) makes `skills/explorer/` a skill directory with no `SKILL.md`, which
  `install_constellation.py::discover_skills` refuses — turning red every test that
  invokes the installer: 26 in `tests/test_install_constellation.py` and 5 in
  `tests/test_feedback_tooling.py` (whose setUp stages a fixture tree via
  `install_constellation.main()`), 31 total, all one root cause. Making it green
  requires either `skills/explorer/SKILL.md` (gate g4) or an installer/test change
  (gate g5), both in Specific Exclusions. I did NOT improvise a stub SKILL.md or an
  installer patch. The g2-integrate postcondition c1 carries
  `override_policy {allowed:true, authority:human}` for exactly this transient; the
  Commander should waive it, and the suite returns to green at g5-integrate.

## Out-of-scope observations

- The plan's per-gate "full suite green" postcondition is unsatisfiable in-scope for
  g2/g3/g4 because a skill directory is illegal to the installer until its `SKILL.md`
  exists. Note the blast radius is wider than the install suite alone: any test that
  calls `install_constellation.main()` in setUp (here `test_feedback_tooling.py`, 5
  tests) also goes red, so "install tests are expected-red until g5" understates it —
  the accurate frame is "every installer-invoking test is expected-red until g4 adds
  the SKILL.md, with the residual expected-skills-list assertions clearing at g5." A
  future plan could order the skill's `SKILL.md` (even a minimal frontmatter stub)
  BEFORE its templates so the suite never goes red — worth a triage note on gate
  sequencing for skill-creation epics. (Not actioned; out of my scope.)

## Workflow feedback (run-specific)

- The single hardest part of this handoff was that the load-bearing behavior lives
  in `verify_spec_confirmed.py`'s decoration-stripping marker matcher
  (`_unconfirmed_marker_hit`): whether a given line trips the refusal depends on
  `lstrip('#')` + `^[-*]\s*` + `strip('*` + backtick)` + `fullmatch`. The handoff
  correctly said "the verifier is the senior partner," but I only got the DESIGN_SPEC
  template right by running the real verifier against draft variants BEFORE writing
  the test (e.g. `- **Status: DRAFT — UNCONFIRMED — DO NOT CUT**` does NOT trip the
  refusal because the `Status:` prefix breaks `fullmatch`, whereas a bare
  `**UNCONFIRMED — DO NOT CUT**` banner does). A one-line pointer in the handoff —
  "the marker only trips on a STANDALONE line; verify your banner placement against
  the script, not by eye" — would have saved a round-trip. Recommend g4's
  SKILL.md/shelve-header work heed the same: the shelve header must be a standalone
  line to be enforceable, and any template that merely *mentions* the marker must
  keep it inline in prose.
- The full-suite-green Close Criterion colliding with the gate ordering (above) cost
  a diagnostic detour to prove the 31 failures were not mine. Flagging in the handoff
  that "every installer-invoking test is expected-red until g4/g5; assert only the
  targeted suite + no NEW failures that survive a stub SKILL.md" would have removed
  the ambiguity about whether I was allowed to commit.
- **Rework lesson (attempt-2):** my attempt-1 result said "all 31 failures are in
  `test_install_constellation.py`" — I eyeballed the failure list, saw it dominated
  by that file, and generalized instead of counting. The correct move (which the
  reviewer had to do for me) is one command:
  `pytest -q 2>&1 | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`. When a result
  doc makes a distribution claim ("all N in file X"), the number and the per-file
  split must come from that command's output pasted verbatim, never from a glance at
  the tail. A correct root-cause conclusion does not excuse an inaccurate supporting
  fact — the reviewer reproduces every stated number, so an under-inclusive one costs
  a full rework round-trip even when nothing about the deliverables is wrong.
