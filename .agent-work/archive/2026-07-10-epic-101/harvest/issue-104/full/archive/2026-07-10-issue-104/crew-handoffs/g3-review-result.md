# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3-review` (issue #104, constellation-curator)

verdict: APPROVE

## Result
`APPROVE`

## Handoff compliance
`tests/test_curate_corpus.py` (new, untracked) delivers exactly what the g3 gate asked for: an 18-test golden-fixture suite over `scripts/curate_corpus.py`, one class per detector, plus a dedicated flags-never-gates falsification. All required close criteria reproduced independently (see per-criterion findings below). Stop conditions satisfied — no biting test would pass with its detector disabled (confirmed by spot-check).

## Scope drift
None. `git status --short` shows only `?? tests/test_curate_corpus.py`. `curate_corpus.py` and every real skill are untouched.

## Evidence verdict
Reproduced:
- `py -m pytest tests/test_curate_corpus.py -v` → 18 passed.
- `py -m pytest tests/ -q` → 464 passed, 2 skipped, 150 subtests passed.
Matches the implementer's report exactly. Test mode is `test-after` inspection over an existing G1 tool (appropriate — no new product code was written), and assertions read exact status/check strings from the tool's own constants (`SHINGLE_SIZE`, `SKILL_WORD_TARGET`, `REFERENCE_TOC_LINE_THRESHOLD`, `CONFUSABLE_SKILLS`) rather than guessed literals, so a future drift in tool vocabulary fails loudly.

## Code/doc quality
Stdlib + unittest only, no new dependencies. Minimal, well-scoped fixtures (`write_skill`/`write_raw_skill`/`clean_frontmatter` helpers keep each test focused on the one flaw it plants). Test-only change; no doc updates required.

## Per-criterion findings (reproduced evidence)

**1. Fixtures provably authentic (T6) — PASS.**
Reproduced independently (not just re-run from the implementer's report):
```
$ git show 2696769:skills/implementer/SKILL.md | grep -n "misfit is compliance"
10:**Mandatory, no exceptions: once loaded, drive the checklist to completion through the engine and dispatch each step it names. Within a step, judgment is yours — when an instruction does not fit the work, do the closest compliant thing and report the misfit in your workflow feedback; reporting misfit is compliance, not deviation.**

$ git show 2696769:skills/commander/SKILL.md | grep -n "FOLLOW THIS SKILL STRICTLY"
8:**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**

$ git show 2696769:skills/workbench/SKILL.md | grep -n "checklist_engine.py"
39:Drive a controller one step at a time with the absolute path to this installed skill's bundled `scripts/checklist_engine.py` ...
```
All three match `COMPLIANCE_BOILERPLATE`, `EMPHATIC_BANNER`, `ENGINE_INVOCATION` in the test verbatim (character-for-character diff against the source lines showed no discrepancy). Authentic, not invented.

**2. Every detector has a BITING assertion — PASS.**
Confirmed each detector's test asserts the exact status/check strings:
- `duplication`: `test_duplication_bites_two_authentic_signatures` (2 clusters, `flagged`, exact sharing-skill sets), `test_duplication_ignores_a_single_planting` (needs ≥2 skills), `test_emphatic_banner_clusters_as_exact_shingle` (8-token boundary case).
- `size`: `test_oversized_body_flagged` / `test_within_budget_body_ok`.
- `invoker` (both directions): `test_missing_invoker_flagged` / `test_present_invoker_ok`.
- `description-*`: `test_first_person_shortlists_not_a_verdict` (shortlist), `test_missing_when_to_use_marker_flagged` (flagged), `test_confusable_skill_without_exclusion_flagged` / `test_confusable_skill_with_exclusion_info` (using real `CONFUSABLE_SKILLS` members `scout`/`cartographer`) / `test_nonconfusable_skill_gets_no_exclusion_finding`.
- `reference-toc`: `test_long_reference_without_toc_flagged` / `test_short_reference_and_toc_reference_not_flagged`.
- `parse`: `test_malformed_and_missing_skill_md_become_parse_rows_no_crash` / `test_main_exits_zero_even_with_unparseable_skill`.

**3. Flags-never-gates falsification is REAL and meaningful — PASS.**
In `test_maximally_flagged_fixture_still_exits_zero`, the fixture's flagged checks are collected into a set and asserted (via `assertIn`, one per expected check: size, invoker, description-length, description-when-to-use, description-exclusion, reference-toc, duplication, parse) to actually be present, plus an assertion that some finding is `shortlist` — all BEFORE the `assertEqual(cc.main(...), 0)` calls. This ordering means the invariant assertion cannot pass vacuously.

**4. Falsification spot-check (reviewer-performed) — PASS.**
Copied `tests/test_curate_corpus.py` to a throwaway `tests/_spotcheck_test_curate_corpus.py` and flipped the expected status in `test_missing_invoker_flagged` from `["flagged"]` to `["ok"]`. Ran:
```
$ py -m pytest tests/_spotcheck_test_curate_corpus.py -v -k test_missing_invoker_flagged
FAILED tests/_spotcheck_test_curate_corpus.py::InvokerDetectorTests::test_missing_invoker_flagged
AssertionError: Lists differ: ['flagged'] != ['ok']
```
The real tool still reports `flagged` (unchanged), so the golden assertion reds as expected — proving the test depends on the tool's actual behavior, not a tautology. Deleted the throwaway file immediately after (`rm tests/_spotcheck_test_curate_corpus.py`). Verified clean state after: `git status --short` → only `?? tests/test_curate_corpus.py`; re-ran `py -m pytest tests/test_curate_corpus.py -q` → `18 passed`. Neither `curate_corpus.py` nor the real test file was modified at any point.

**5. Green — PASS.**
`py -m pytest tests/test_curate_corpus.py -v` → 18 passed. `py -m pytest tests/ -q` → 464 passed, 2 skipped, 150 subtests passed.

**6. Scope — PASS.**
`git status --short` → only `?? tests/test_curate_corpus.py`. No other file touched.

## Map impact verdict
- **Evidence supports claimed change:** yes — "every detector bites" and "flags-never-gates holds" are both backed by passing, non-vacuous assertions (verified above), not just asserted in the report.
- **Constraints not violated:** yes — T6 (authentic fixtures) honored; no edit to `curate_corpus.py` or any real skill.
- **Notes match the diff:** yes — implementer's Map Impact notes (structural anchor = the new test file; capability = detector falsification) match the actual diff, which is a single new test file.
- **Decision candidates surfaced:** n/a — no authority-requiring decision arose.
- **Durable context routed:** yes — the two out-of-scope observations (exclusion-marker substring sensitivity, `PERSON_PRONOUNS` "us" sensitivity) are logged in the implementer's report for Commander; not dropped.

## Reconciliation check
None. Test-only addition over an existing G1 tool; no structural/contract divergence to reconcile.

## Blockers
- none

## Out-of-scope observations
- (carried from implementer report, re-verified as accurate, not re-litigated here) `description-exclusion`'s substring match on `"not "` could produce a false `info` from incidental prose (e.g. a stray "not" unrelated to an actual exclusion clause) in a confusable-pair skill's real description. Not a defect in this test suite — flag for Commander/curator-author awareness only.
- `PERSON_PRONOUNS` includes `"us"`, which is common enough that real descriptions may shortlist on incidental matches; by design (shortlist, human judges), just a sensitivity note.

## Workflow Feedback

- **Handoff gaps:** None — the handoff's six close criteria mapped cleanly onto reproducible commands; no ambiguity encountered.
- **Context rediscovered:** The `append` verb's `<id>` argument names the NEW leaf, not an anchor to nest under (documented in `references/checklist-engine.md`, but worth restating in the handoff template for reviewers building a criteria-specific survey, since a first `append` attempt with an anchor-style id would refuse as "already exists").
- **Instructions improvised around:** The reviewer skill's base survey items (`r0`-`r5`) are generic; I appended five handoff-specific items (`r6`-`r10`) mapping 1:1 to the six numbered close criteria (criteria 1 and 2/3/4/5/6 folded to five checks since criterion 2's "every detector" and criterion 5's "green" each got one check). This is exactly what the skill instructs ("append checks the context warrants, one per inherited rule") — no real improvisation, just noting the mapping for future reviewers on similar handoffs.
- **What would have made this easier:** Nothing structural — the handoff was unusually well-specified (each criterion already came with its own verification command). This is a good handoff pattern to replicate for other gates.

## Return status
`complete`
