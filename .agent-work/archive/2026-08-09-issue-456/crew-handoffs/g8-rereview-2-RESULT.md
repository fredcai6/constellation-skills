# Review Result — g8, attempt-3 (re-verification of remediation-3)

## Assigned Gate
`g8` — verify commit `1f2b57ab`, which unifies overflow-preservation across both branches of `_first_paragraph` after attempt-2's finding (blank-line branch still dropped its own overflow).

## Result
`BLOCK` — but with a different shape than the first two rounds: **the production code is correct; the tests written to prove it are not.**

## What I verified

**The invariant genuinely holds in the shipped code.** I probed it with an adversarial battery deliberately built to include shapes the crew's own four hand-picked cases would miss: no docstring at all, whitespace-only, all-blank-lines, a leading blank line before any text, multiple consecutive blank lines, exact 159/160/161-char boundaries both with and without a blank line, a multi-byte character (em-dash) straddling the cut at every position 158–161, Windows CRLF line endings on a long first paragraph, and a huge (3800+ char) post-blank-line body. Every case checked with **character-exact reconstruction** (not word-splitting — my first pass at this used a word-split check and produced false positives on strings with no internal whitespace, corrected). Zero content loss anywhere in this battery.

**The invariant survives to real rendered pages.** `map/scripts.checklist_engine/_rail_position.md` — the page that showed the loss last round — now reads correctly end to end. Sampled 3 more real entities from the 54-item blank-line/long-first-paragraph list (`raw_record.md`, `repo_revision.md`, `_adjudicate_orphan.md`): all read as continuous, complete text. Re-checked the original no-blank-line page (`_git_rev_parse.md`): still correct. `map/` is fresh (rebuilt 62s after the commit, confirmed by mtime).

**The branch collapse is right.** Confirmed by reading the diff: the two previously-separate code paths are now one unconditional overflow check, removing the exact drift risk that produced two consecutive prior findings (a case fixed in one branch, forgotten in its sibling).

## Why this is still a BLOCK

**Two independent mutations, each reproducing a state of the code that was already BLOCKED in an earlier round, leave the shipped test suite entirely green.**

- Mutation 1: revert the whole fix to the remediation-2 shape (blank-line branch doesn't preserve its own overflow — attempt-2's exact finding). All 11 selector tests, including both tests written this pass, stayed green.
- Mutation 2 (surgical): keep the 160-char truncation but drop only the overflow text from `body` (`body = post_blank_body`, discarding the prepended overflow). Only the *older* remediation-2 test caught it, by accident. Both tests written specifically for the blank-line-overflow case stayed green.

Root cause, read directly in the test source: both `test_long_first_paragraph_with_blank_line_and_body` and `test_all_shapes_preserve_complete_content`'s Shape-4 subtest gate their real assertions behind `if summary and len(summary) == 160:`. Under mutation 1, `doc_summary_of` never truncates the blank-line branch at all in the reverted code (245 chars in the test's own fixture, measured directly), so the guard is `False` and the meaningful assertions (`assertIsNotNone(body)`, `assertIn("Args:", body)`) never run — the only assertion that does run (`assertGreater(len(reconstructed), 160)`) passes trivially because the untruncated summary alone already exceeds 160. Under mutation 2 the guard does fire, but neither assertion checks for the overflow text itself, only that `body` is non-`None` and contains `"Args:"` — both true whether or not the overflow was actually prepended.

This is precisely the failure mode this pass's own brief named as the central risk ("an invariant test that cannot fail is the worst of both worlds, since it reads as the strongest possible evidence"), and precisely what this repo's `CREW_CONTEXT.md` names as the rule that most often separates an accepted change from a reworked one: *"A check that cannot fail is indistinguishable from one that passed."*

## Blockers
- `test_long_first_paragraph_with_blank_line_and_body` and `test_all_shapes_preserve_complete_content`'s Shape-4 subtest do not actually exercise the invariant they claim to guard — confirmed by two independent mutations that reproduce a previously-BLOCKED state of the code while leaving the suite fully green.

## Recommended fix — test-only, small, no production code change
1. Remove the `if summary and len(summary) == 160:` gate in `test_long_first_paragraph_with_blank_line_and_body`; assert `len(summary) == 160` unconditionally so a regression that stops truncating fails loudly rather than silently skipping the block.
2. In both that test and Shape 4 of `test_all_shapes_preserve_complete_content`, assert the overflow text itself is present in `body` (e.g. the last words of the constructed first paragraph before the blank line), not just that `body` is non-`None` or contains `"Args:"`.
3. The production fix in `1f2b57ab` needs no changes — it is correct, verified independently by direct execution against the code, not by trusting these tests.

## Evidence verdict
The code-behavior evidence is solid (my own independent probing, not the crew's). The test evidence specifically required by this pass's brief ("do the tests have teeth... revert and confirm what goes red") fails on exactly that ask for the two new tests.

## Out-of-scope observations
None new. Carried unchanged from attempts 1–2: the duplicated BOM-strip line (non-blocking Fowler flag) and the repo-wide summary-truncation design question (filed to triage as this survey's `tc1`).

## Workflow Feedback
- **Handoff gaps:** none. The brief's explicit warning about invariant tests that cannot fail is exactly what led me to mutate rather than trust the new tests, and it paid off.
- **Context rediscovered:** none.
- **Instructions improvised around:** distinguishing "the code is wrong" from "the code is right but its test is a check that cannot fail" needed a different verdict shape than attempts 1–2 (both of which were "the code is wrong"). The reviewer skill's BLOCK/APPROVE framing handles this fine (BLOCK is still correct — required evidence is deficient — but it's worth Commander knowing the two BLOCKs are not the same *kind* of finding when deciding what a 4th pass needs to touch: tests only, not the fix).
- **What would have made this easier:** nothing — the same scan-real-corpus-then-mutate-the-tests method generalized cleanly a third time.

## Return status
`complete`
