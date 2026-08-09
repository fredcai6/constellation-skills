# Review Result

## Assigned Gate
`g8` — two code defects (issue #456): BOM-prefixed files rejected by `ast.parse`, and the wrapped-docstring render split (D3).

## Result
`BLOCK`

## Handoff compliance
Defect 1 (BOM) is fully compliant: fixed at all three real `ast.parse` call sites in the module, fixture carries genuine BOM bytes, test goes red without the fix. Defect 2 (D3) implements the Commander's own empirical reading of an undefined term correctly for the literal symptom demonstrated, but the reading itself has a confirmed regression against real docstrings in this repo — see Evidence verdict below. Full reasoning is in the survey's `r1-handoff` finding.

## Scope drift
None. Diff across both commits touches exactly 4 files, all inside the allowed scope (`scripts/code_map/extract.py`, `scripts/code_map/checks.py`, `tests/test_code_map.py`, `tests/fixtures/bom_corpus/bom_sample.py`). No specific exclusion touched (`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`, `page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers, `thresholds.py`, g6/g7 machinery — none referenced). `map/` stays untracked; no `git add -A` used.

## Evidence verdict
Mixed. I independently mutation-tested the shipped tests: reverting `_first_paragraph` to a naive line split makes 2 of 8 selector tests go RED (`test_wrapped_summary_is_first_paragraph`, `test_wrapped_summary_no_body`) — the tests have real teeth, confirmed by an attack I designed myself, not the crew's own break-test. I also reverted the BOM strip and watched `test_bom_file_can_be_extracted` go red, and confirmed the fixture carries genuine `\xef\xbb\xbf` bytes on disk.

But: of the four boundary cases this gate's own remediation handoff named, only three are tested. The fourth — a first paragraph over 160 chars, where truncation must apply after joining, not before — has no test in `tests/test_code_map.py` at all. I confirmed by direct execution that the underlying behavior is correct (truncation genuinely happens after the join), so this is a coverage gap, not a second independent bug — but it is exactly the gap that would have surfaced the regression below had it been tested against a real-shaped (no-blank-line) docstring instead of a short synthetic one.

**The central finding:** per this review's own charge to check the D3 reading against real docstrings, I found the shipped rule — "summary = first paragraph, ends at the first blank line" — creates a new, larger regression than the one it fixes. This codebase's dominant docstring shape is a single dense multi-line paragraph with **no blank line** (132 such docstrings over 160 joined characters found in `scripts/**/*.py` alone). For that shape, the entire docstring now becomes "the summary," gets hard-truncated to 160 characters at the three emit sites, and `doc_body_of` returns `None` — everything past 160 characters is silently gone, with no ellipsis or other signal. Under the old (pre-g8) code, only the first physical line became the summary and the **rest was preserved untruncated in the body**. I confirmed this directly against two already-regenerated real pages in this worktree's `map/` tree:

- `map/scripts.agent_work_root/_git_rev_parse.md` — summary now ends mid-word: `"...and lets OSError (g"`; no body rendered. The source docstring's own tail (`"git absent / bad cwd) propagate — both caught by the caller."`) is gone.
- `map/scripts.checklist_engine/_glob_to_regex.md` — same pattern: `"...no single \`*\` matches within one segment (no \`/\`?"`, cut mid-clause, no body.

This contradicts `DESIGN_SPEC.md`'s own stated intent for the summary field (line 129, the redundancy rule): "DO carry the structural summary that saves opening the file at all." A summary that silently drops the back half of the only real content on the majority of this repo's pages does not save the reader from opening the file.

**Recommended fix (small, scoped):** when `_first_paragraph` finds no blank line, route the 160+-char overflow into `body` instead of discarding it (symmetrical with the blank-line case), or explicitly mark the truncation. Either requires a change only inside `_first_paragraph`/the emit sites' truncation logic — the paragraph-join mechanism and the BOM fix are both otherwise correct and need no rework. Add the missing >160-char boundary-case test against a real-shaped (no-blank-line) docstring while at it.

## Code/doc quality
Fowler pass complete (`.agent-work/issue-456/g8-review/fowler-pass.json`, `verify_fowler_pass.py` exits 0). One non-blocking flag: the one-line BOM-strip (`src.lstrip('\ufeff')  # Strip UTF-8 BOM if present`) is byte-identical across three call sites (`extract.py` x2, `checks.py` x1) — small, worth extracting into a shared helper the next time a fourth `ast.parse` site appears. The other eleven baseline smells are absent; notably shotgun-surgery is explicitly absent because this fix *removes* a latent instance of it (the pre-fix inlined-at-three-sites summary logic was the shape that produced the original D3 defect). No new imports; stdlib only. Page headers and `render_report.json` both correct (no `:<line>`, no timing fields, fresh post-fix build confirmed by mtime).

## Map impact verdict
Neither `g8-implement-RESULT.md` nor `g8-remediate-RESULT.md` carries a "Map Impact" section. Given the Evidence verdict above — this fix measurably changes rendered summary/body content across a large fraction of the corpus this tool indexes, not just the fixture — that omission should have been a flagged capability-impact note. Not filing this as a separate blocker since the BLOCK above already covers the substance; Commander should treat "the docstring-summary rendering rule changed" as durable context worth recording once the rework lands.

## Reconciliation check
No architecture/interface divergence: statement schema, module boundaries, and the store's documented shape are unchanged. `_first_paragraph`/`doc_summary_of`/`doc_body_of` are additions fully contained in `extract.py`; the `checks.py` BOM line mirrors an existing pattern, not a new one. One triage candidate filed (survey `tc1`): whether a docstring summary should ever silently drop content past a truncation limit is a repo-wide (DESIGN_SPEC-level) design question that will recur on every future re-index, including of `f1Brainz`.

## Blockers
- The D3 fix truncates the majority-shape docstring in this repo (no blank line, >160 joined chars) down to 160 characters with total, unsignaled loss of the remainder and no body — a regression against the pre-fix behavior, which preserved that content untruncated in the body. Confirmed against two real, already-regenerated pages. Fix: route the no-blank-line overflow into `body` (or mark the truncation explicitly), and add a test for the missing >160-char boundary case against a real-shaped docstring.

## Out-of-scope observations
- Fowler: the BOM-strip line is duplicated verbatim across 3 call sites — small, non-blocking, extract into a shared helper next time a 4th `ast.parse` site appears.
- Filed to triage (survey `tc1`): the summary-truncation-drops-content design question is bigger than this gate — decide it once in `DESIGN_SPEC.md` so it does not resurface at the next re-index.

## Workflow Feedback
- **Handoff gaps:** none — the handoff's six questions mapped cleanly onto the survey's checks, and naming the D3-definition risk up front (Commander's own words: "attack it") is exactly the framing that made the regression findable. No field was missing or wrong.
- **Context rediscovered:** the fact that `map/` in this worktree was already rebuilt post-fix (mtime 2026-08-08 17:57:04, 4 minutes after the `06fbc138` commit) was not stated in the handoff but was essential — it let me check real, current pages instead of having to rebuild myself. Worth stating explicitly in future handoffs when the reviewer can use an already-fresh `map/` as evidence rather than re-running `build`.
- **Instructions improvised around:** the shared job tmp dir (`C:\Users\fredc\.claude\jobs\9cbc67f4\tmp`) already held `r0-finding.txt` through `r6-finding.txt` from an earlier gate's reviewer reusing the same generic names — my first `Write` to `r1-finding.txt` was refused ("must Read existing file first"). I worked around it by prefixing all my scratch files with `g8-` (e.g. `g8-r1-finding.txt`). Worth naming in the skill: scratch-file names under the shared job tmp dir should be gate-prefixed, since the directory persists across every gate in a run, not just the reviewer's own.
- **What would have made this easier:** nothing structural — this gate's evidence bar (real pages, real docstrings, mutation-test the shipped tests) was exactly right and is what surfaced the finding. Suggest, for future D3-shaped gates (a spec term used but never defined), that Commander's resolution note explicitly ask "does this rule handle the corpus's DOMINANT docstring/code shape, not just the shape in the bug report" — that one framing would have been the fastest route to this finding.

## Return status
`complete`
