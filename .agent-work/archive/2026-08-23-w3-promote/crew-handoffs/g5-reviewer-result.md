# REVIEW_RESULT

## Gate
g5-review (execute.json, work-id w3-promote) — reviewing g5-implement's completed slice

## Verdict
**APPROVE**

## Summary
Independently reproduced every claim in `g5-implementer-result.md`. Exactly 1 condition changed
in `skills/charter/templates/CHARTER.template.json` (`project-templates.c1`, `check: null` →
`artifact` kind, `evidence_type: "project-templates"`, enum-match on `status` in `{"seeded",
"skipped-no-need"}`). The two other candidates named in the handoff (`closeout.c1`,
`interrogate.c1`) were fresh-verified and correctly left `check: null`; I independently re-derived
both dispositions from source rather than trusting the implementer's prose, and both hold up.

## Per-check findings

**`project-templates.c1` (promoted)**
- Diff is exactly 1 single-line replacement in `skills/charter/templates/CHARTER.template.json`
  and its overlay (compact-format hand-edit discipline honored; `git diff --stat` = 1/1 in each
  file, index hashes identical between the two files).
- Confirmed via `git show HEAD:...` dump of every condition's `check` field, pre- and post-edit:
  only `project-templates.c1` differs. `closeout.c1`, `interrogate.c1`,
  `orchestrator-context.c1`, `agent-guide.c1`, and every other condition in the file are
  byte-identical to HEAD.
- Shape matches spec: `artifact` kind, enum-match on `status`, `statement` text byte-unchanged,
  no `basis` field (`grep -n "basis" skills/charter/templates/CHARTER.template.json` → no match).
- `artifact`-kind eligibility independently spot-checked against `git show HEAD:...`: 6
  pre-existing `artifact`-kind checks already live in this file (`intent.c1`,
  `orchestrator-context.c1`, `crew-context.c1`, `glossary.c1`, `agent-guide.c1`,
  `engine-config.c1`), so this is not a first-of-kind use — `decision:blocking-where-adjudicated`
  correctly did not require a Commander consult.
- Mirroring claim against COMMANDER_SPINE's `plan.c1` independently verified by reading that
  condition directly: `kind: artifact`, `evidence_type: "mission-frame"`,
  `match: {"status": ["produced", "skipped-as-trivial"]}`, no `basis` field — the same
  artifact+enum-match shape, confirming the claimed precedent is real.
- Overlay byte-identical (`diff .agent-work/templates/CHARTER.template.json
  skills/charter/templates/CHARTER.template.json` empty); `check_template_overlay_freshness.py`
  reports it clean among all 56 overlays.

**`closeout.c1` (left `check: null` — verified sound)**
- `scripts/verify_interrogation.py` is not relevant here (that's `interrogate.c1`); for
  `closeout.c1` the claim is the wall-clock-keyed archive path. Read
  `scripts/spine_lifecycle.py::archive_name_for` directly: `f"{today}-{work_id.replace('/', '-')}"`
  — `today` is a caller-supplied wall-clock string, not derivable from any placeholder.
- Read `scripts/init_work_area.py`'s placeholder-family list directly (`<work-id>`, `<repo-root>`,
  `<role-skill-dir>`, `<role-session-id>`): none of these can express a date. No stable
  archive-path locator exists.
- This is genuinely the same defect g3's reviewer already confirmed for ADMIRAL_SPINE
  `closeout.c4` (cross-checked `AdmiralSpineW3PromotePromotions`'s own docstring in
  `tests/test_checklist_engine.py`, which names the identical function and the identical
  `/`-strip-transform gap) — the pattern-match is genuine, not asserted on faith.

**`interrogate.c1` (left `check: null` — verified sound)**
- `scripts/verify_interrogation.py` confirmed to exist (`ls` on the path).
- Read `scripts/init_work_area.py::_resolve_skill_dir_token` and its caller `resolve_spine`
  directly (lines 80–149): every `<role-skill-dir>` token found in a template's text resolves to
  the SAME single `--skill-dir` value passed for that template's own instantiation — confirmed at
  line 142, `for token in sorted({f"{role}-skill-dir" for role in _ROLE_SKILL_DIR_RE.findall(text)})`
  followed by a single shared `_resolve_skill_dir_token(text, token, skill_dir, root)` call, not a
  per-role lookup. A `<interrogator-skill-dir>` token inside CHARTER's own spine would indeed
  resolve to CHARTER's own skill-dir, not interrogator's.
- Read `scripts/install_constellation.py`'s `SKILL_SCRIPTS` manifest directly: line 234,
  `"interrogator": ("checklist_engine.py", "verify_interrogation.py")`; line 224,
  `"charter": ("checklist_engine.py",)` — confirms `verify_interrogation.py` is genuinely not
  bundled with `"charter"` in an installed repo.
- Independently confirmed CHARTER carries zero `command`-kind checks today (dumped every
  condition's `check.kind`; all 6 pre-existing non-null checks are `artifact`) — a `command`-kind
  use here would be a genuine first-of-kind that `decision:blocking-where-adjudicated` gates, an
  independent second reason the decline holds even setting the wiring problem aside.
- Both reasons are real, source-verified, and either is independently sufficient. Decline is sound.

## Evidence independently reproduced
- `python3 -c "import json; json.load(...)"` → OK.
- `python3 scripts/check_template_overlay_freshness.py` → all 56 overlays clean, CHARTER included.
- `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` →
  **641 passed, 26 skipped, 148 subtests passed** — matches the implementer's claimed result
  exactly.
- `python3 -m pytest tests/test_checklist_engine.py -k Charter -q` → 5 passed.
- `falsifiable-all-null` corpus sweep independently re-run pre/post-edit: 15 (pre, via
  `git stash push/pop` on just the two CHARTER template files) → 14 (post, current tree). The
  drop is real and correctly attributed — `project-templates.c1` was that task's only
  postcondition.
- `grep -n "basis" skills/charter/templates/CHARTER.template.json` → no match.
- Fowler pass: recorded to `.agent-work/w3-promote/g5-review/FOWLER_PASS.json`,
  `scripts/verify_fowler_pass.py` exits 0 (10 smells absent, 2 overridden citing the already-
  landed sibling test classes' identical shape).

## Red-proof genuineness check
Read `CharterW3PromotePromotions` in full. `test_project_templates_c1_status_membership_discriminates`
attacks (1) wrong `evidence_type`, (2) a differently-cased `status` string ("Seeded" vs "seeded" —
a genuine adversarial mutation attacking the case-sensitivity boundary, not a restatement of the
match text), plus (3) a positive control on the *other* enum member (`skipped-no-need`) to prove
genuine list-membership rather than a hardcoded match. I additionally hand-mutated the shipped
JSON (dropped `"skipped-no-need"` from the match list) and re-ran the suite: both
`test_promoted_checks_match_shipped_shape` and
`test_no_condition_outside_pre_existing_and_promoted_carries_a_check` genuinely failed, confirming
real discriminating power, then restored the file by re-applying the implementer's exact
single-line edit and confirmed the restored diff was byte-identical to the original (matching git
blob index hashes) before re-running the full suite green again.

## Blockers
None.

## Out-of-scope observations
- `scripts/install_constellation.py`'s manifest gap for `verify_interrogation.py`/`"charter"`
  (already flagged by the implementer, independently confirmed real here) is a genuine future
  triage candidate — not a blocker for this gate.

## Workflow feedback
- The handoff's Close Criteria were unusually well-specified for source-level re-verification
  (naming the exact files/functions to read for both left-null dispositions) — this made
  independent verification fast and left no ambiguity about what "verify yourself" meant.
- One process note, not a handoff gap: during red-proof genuineness testing I mutated the shipped
  JSON to confirm test discrimination, then used `git checkout --
  skills/charter/templates/CHARTER.template.json` intending to undo my own mutation — this
  reverted the file all the way to pre-g5 HEAD instead, since the implementer's edit is itself
  uncommitted. Caught immediately via `git diff` (wrong direction), corrected by re-applying the
  implementer's exact line, and confirmed restoration was byte-identical to the original diff
  before proceeding. Future reviewers doing this kind of mutation test on an uncommitted diff
  should restore via a saved copy or `git stash`/`git apply`, not a bare `git checkout --`, since
  the latter resets to the last commit, not to "the state before my last edit," when the target
  file already carries uncommitted changes.

## Review survey
Hand-tracked survey (no `mcp__spine__*` access, as instructed) recorded at
`.agent-work/w3-promote/g5-review/review.json`; Fowler pass at
`.agent-work/w3-promote/g5-review/FOWLER_PASS.json`.
