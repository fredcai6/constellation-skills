# Review Result — g8, attempt-2 (re-verification of remediation-2)

## Assigned Gate
`g8` — verify the fix for the r1-handoff/r3-evidence regression (commit `c385f467`). Not a full re-review; the BOM fix, the paragraph-join mechanism, scope, and the Fowler pass are carried from attempt-1 and not re-litigated here.

## Result
`BLOCK`

## What I verified

**The demonstrated regression is genuinely fixed.** Both named pages restored in full:

- `map/scripts.agent_work_root/_git_rev_parse.md` — tail back: `"...and lets OSError (git absent / bad cwd) propagate — both caught by the caller."` now appears in a body section.
- `map/scripts.checklist_engine/_glob_to_regex.md` — same, full continuation restored.

Sampled 4 more of the 132 no-blank-line entities at random (seed 42) — `_condition_open`, `_stamp_date`, `_read_events`, `_supersede_evidence` — all four now show the previously-lost tail in a body section. The no-blank-line class this pass targeted is fixed across every sample I checked.

**The new boundary test has real teeth.** Reverted only the new overflow branch in `_first_paragraph` (the `elif paragraph and len(paragraph) > 160` block); re-ran the closing selector: exactly 1 test fails (`test_dense_paragraph_over_160_chars_no_blank_line`, `221 != 160`), the other 8 stay green. Restored via `git checkout --`, confirmed clean via `git diff --quiet`.

**The original short-wrapped-summary+blank-line+Args shape still works** when the summary itself is under 160 chars — re-verified directly.

Mechanical: closing selector `-k 'bom or docstring'` = 9 (matches claim). `python -m scripts.code_map check --root .` = 7/7. Diff scope is exactly `scripts/code_map/extract.py` + `tests/test_code_map.py`, both in the allowed scope stated in `g8-remediate-2.md`.

## Why this is still a BLOCK

**The fix patches only one of two symmetric branches, and the invariant it claims to establish — "no docstring content is ever dropped without appearing somewhere" — is not held everywhere.** I probed it directly and found a live counter-example in the sibling branch:

The blank-line case — the *original* D3 shape this whole gate started from, a wrapped summary followed by a blank line and a body — still has no overflow-preservation when the paragraph *before* the blank line itself exceeds 160 characters. `doc_summary_of` correctly returns the full joined paragraph (the paragraph-join fix from remediation-1 is right), but the emit-site `summary[:160]` truncation drops everything past 160 chars, and `doc_body_of`'s body only carries the text after the blank line — the dropped summary tail is nowhere.

This is not hypothetical. I scanned `scripts/**/*.py` for docstrings with a blank line whose first paragraph alone exceeds 160 characters: **54 real instances** (e.g. `scripts/checklist_engine.py:_rail_position`, `:_rail`, `:repo_revision`; `scripts/apply_episode_delta.py:commit`, `:apply_retirement`, `:write_plan`). I checked the already-regenerated real page for one of them:

- `map/scripts.checklist_engine/_rail_position.md` — summary cuts off mid-word (`"...its "`); body starts directly with the bullet list (`"- \`\`n == 0\`\`..."`); the connecting clause from the source docstring (`"head (\`\`remaining[0]\`\`) is the active gate."`) is gone from the page entirely — not relocated, just gone.

Same defect class as the finding this pass was built to close, in the sibling branch of the exact function meant to close it. Multi-byte/boundary probes (exact-160, exact-161, em-dash straddling positions 157–162) all reconstruct byte-for-byte correctly for the *fixed* branch — the string-slicing mechanics are sound; the gap is purely that the fix wasn't applied to both branches.

## Evidence verdict
Confirmed genuine and reproducible for the scoped claim (no-blank-line overflow). Not sufficient for the broader invariant claimed in the commit message ("no docstring content is ever dropped without appearing somewhere") — that claim is currently false for the blank-line branch.

## Blockers
- `_first_paragraph`'s blank-line branch has no overflow-preservation: when the paragraph before the blank line exceeds 160 chars, the excess is silently dropped at the emit sites, with no corresponding body content — the same defect class as the original finding, live today on 54 real docstrings in `scripts/` alone (confirmed on `map/scripts.checklist_engine/_rail_position.md`).

## Recommended fix (small, same function, same shape as the fix already shipped)
Apply the identical overflow-preservation logic already written for the no-blank-line branch to the blank-line branch: when the paragraph before the blank line itself exceeds 160 chars, route its overflow into `body` too (e.g. `body = overflow + "\n\n" + existing_body`), instead of letting the emit-site `summary[:160]` silently drop it. This does not touch the no-blank-line fix, the BOM fix, or the paragraph-join mechanism — all three are correct and need no rework.

## Out-of-scope observations
None new. Carried from attempt-1: the duplicated BOM-strip line (non-blocking Fowler flag) and the repo-wide summary-truncation design question (filed to triage as this survey's `tc1`) are both unaffected by this pass.

## Workflow Feedback
- **Handoff gaps:** none. The brief's own framing ("if you find yourself unable to hold that invariant without a bigger change, stop and say so") gave exactly the right permission to keep probing past the two named pages instead of stopping at "the named cases pass."
- **Context rediscovered:** none — this pass reused the same 132-docstring scan methodology from attempt-1 directly; extending it to the blank-line class (54 more instances) was a five-minute variant, not a rediscovery.
- **Instructions improvised around:** re-consolidating a survey a second time after `consolidate` had already run. The engine allowed `append` → `record` → `consolidate` again with no `--override-reason` needed this time, because the new verdict was BLOCK, not APPROVE (the guard only gates APPROVE-while-fail). Worth confirming this is the intended, documented path — `checklist-engine.md`'s example only shows the BLOCK→APPROVE direction.
- **What would have made this easier:** nothing — the scan-then-spot-check-a-real-page method from attempt-1 generalized cleanly to the second branch.

## Return status
`complete`
