# Reviewer Handoff

## Gate
`g6` — stale-tag detector (issue #456)

## Survey State Location
Create your review survey at `.agent-work/issue-456/g6-review/review.json`. Under the issue workbench, never at the worktree root.

Note on the engine: a `survey` has **no `reopen` verb** — it is gated-checklist-only. If you file a verdict and then need to re-verify a fix, the correct path is `append` a recheck item → `record` it → re-`consolidate` with `--override-reason`. The original failing item stays in the record for audit and stops blocking. Do not hand-edit the survey file.

## What Was Implemented
Staleness detection for the authored layer — the first build of a design the human signed **accepted-untested** at confirm.

1. `extract.span_hash(node)` — `ast.dump(node, annotate_fields=False)` over an entity's own AST subtree, with the leading docstring statement stripped before dumping. `include_attributes` defaults False, so the hash encodes no source text, whitespace, or position.
2. `Extractor.anchor()` persists `d.span_hash` on every `anchored` statement at extraction time.
3. `extract.run()` reads the **previous** `statements.jsonl` before overwriting it, diffs old-vs-new span hashes **keyed by slug**, and appends one `stale-anchor` statement per slug whose hash changed.
4. `render.load_stores()` intercepts `stale-anchor`, surfaces it as `report["stale_tags"]` in `render_report.json`, and prints an advisory `FAIL stale tag [...]` line naming the human action. **It does not fail the build.**

Committed by the crew at `55b95314`.

## How to Inspect the Diff
This is a linked worktree. The change is **committed**, so:
```
git show --stat 55b95314
git show 55b95314 -- scripts/code_map/extract.py scripts/code_map/render.py
```
Also run `git status --porcelain` first (not `git diff --name-only`, which hides untracked additions) to confirm the tree is clean and nothing else is loose.

Three files only: `scripts/code_map/extract.py`, `scripts/code_map/render.py`, `tests/test_code_map.py`.

## Task Statement
Hash each tag's enclosing entity span at extraction. On rebuild, flag any tag whose anchor body changed **while its text did not**, in the run report the reviewer already reads. Without this the design ships the predecessor's failure mode in a smaller box (critics IF4/TS8).

## Close Criteria
- The gate's three parts exist and work: span hashed at extraction, previous store read-before-overwrite and diffed, flag surfaced in `render_report.json`.
- The full suite is green at this boundary. This gate carries an explicit full-suite constraint (critic F6).
- Closing selector `python -m pytest tests/test_code_map.py -k 'stale_tag' -q --color=no` collects and passes. **Baseline was 0 by design** (no such tests existed); the Commander measured **12 collected, 12 passed, exit 0** on the shipped tree. Anything that is not caught by that selector is invisible to the command that closes this gate — flag it.
- Fresh `build` then `check` (in that order — `check` reads a stale tree otherwise) returns 7/7, exit 0, `deterministic-rebuild` included.

## The four questions this review exists to answer

These are the review's real work. Grade them, don't just confirm them.

**1. Does slug-match actually constitute the "text did not change" half of the rule, or does it beg the question?**
The crew's reasoning: no comment-tag vocabulary exists yet (that is gate `g7`), so today an anchor carries no text besides the `[slug]` it was minted with; therefore matching old and new by identical slug **is** "the text did not change." Interrogate this. If a future tag's prose can change while its slug stays fixed — which is exactly what `g7` introduces — then slug-match is matching *identity*, not *text*, and the rule as built will miss the case where prose is edited and body is edited together, or flag where prose was updated deliberately. Decide whether that is a defect now, a correctly-deferred `g7` concern, or a hook that needs widening before `g7` can use it. Say which, with reasoning.

**2. Is advisory-only the right severity?**
A flag that cannot fail the build can be ignored forever. The crew states this as an explicit design call, not an inherited ruling, and invites you to overrule it. Note also that the advisory line is printed with the literal word **`FAIL`** while the exit code is unaffected. Check whether that collides with the output convention `check` already uses for real failures, and whether anything (a script, a CI grep, a human skimming) could reasonably read `FAIL` and conclude the build failed. If it can, that is a finding regardless of how you rule on severity.

**3. Attack reformatting immunity with a mutation the crew did not choose.**
Reproducing a falsifier its author designed proves only that the author's probe works. The crew's own probes are: adding a blank line plus a trailing comment (expect no flag), and `return WIDTH` → `return WIDTH * 2` (expect a flag). Pick mutations it did **not** choose and predict the answer before running. Candidates worth trying: converting a string literal's quote style; splitting one statement across lines with a backslash or parentheses; changing a default argument value; reordering two independent statements; adding a type annotation; changing an integer literal to an equivalent expression; converting a `for` loop to a comprehension. For each, state whether the flag fired, whether it *should* have, and whether the answer follows from `ast.dump`'s documented behavior or is accidental.

**4. Do the negative tests have teeth, or do they pass vacuously?**
This is the sharpest one. The crew disclosed honestly that during its red phase **7 of its 10 "does-not-flag" assertions passed vacuously** — nothing was implemented, so nothing flagged, so they were green against an empty feature. Verify whether the **shipped** negative tests are now guarded by a positive control, i.e. whether each "no flag here" test would go red if staleness detection were disabled wholesale. The concrete attack: disable the flag emission on one code path in `extract.run()`, rebuild, and see how many of the 12 go red. If most of the negatives stay green, they are checks that cannot fail — the same defect class as this run's tc38 and tc47 — and that is a BLOCK-worthy finding even though the feature works.

## Also verify

- **The new report field cannot perturb `deterministic-rebuild`.** The crew's argument is structural: that check builds into two *fresh* scratch `--artifacts` directories each time, so `old_hashes` is always empty in both and the staleness path never runs. Confirm that reading of the check rather than accepting it. Note the corollary, and say whether it bothers you: `check` therefore **never exercises the staleness path at all**.
- **Read-before-overwrite robustness.** What happens on the first ever run (no previous `statements.jsonl`), on a truncated or malformed one, and when a slug is newly added or removed between runs rather than changed. A crash or a spurious flag in any of those is a finding.
- **A count discrepancy in the result document.** Its Scope section claims "16 new tests total"; its own Evidence section and the Commander's independent run both say **12**. Establish which is right and whether anything was dropped between writing and shipping.
- **`extract_report.json` also gained a `stale_tags` field** as a secondary surface. The gate asked for one report. Judge whether that is harmless duplication or a second source of truth that can drift.

## Allowed Scope
`scripts/code_map/extract.py`, `scripts/code_map/render.py`, `tests/test_code_map.py`. Nothing else.

## Specific Exclusions — flag if touched
`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`, `page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers, and `scripts/code_map/thresholds.py`. The crew states all are untouched and `git show --stat` shows three files; verify rather than accept.

**Do not `git add -A` in this worktree.** An untracked `map/` tree of ~3,865 generated pages sits here and is staged deliberately at the final gate. Stage explicit paths only, or do not stage at all.

`C:\Programs\f1Brainz` and `C:\Programs\superCoolSpaceSim` are READ-ONLY corpora. f1Brainz's six real authored tags (PR #733) are the natural first real-world validation of this mechanism — you may read them to reason about question 1, but do not write there and do not treat their absence from this gate as a defect.

## Constraints the Implementation Must Respect
- The run report carries **no timings**, so the determinism diff can cover it. `stale_tags` must be a plain list of ids with no timing field. The crew claims a dedicated test scans `render_report.json`'s own keys for this — check that test actually scans rather than asserts a fixed list.
- The **full suite** must be green at this gate boundary (critic F6).
- Page headers carry path and `, N lines` — never `:<line>`. Human ruling, still in force.

## Map Anchors (inbound)
- **Structural:** `scripts/code_map/` extractor — span hashing.
- **Capability:** derive structure from source.
- **Constraint:** the run report carries no timings.
- **Decision:** what constitutes a tag's anchor body. Resolved by the crew as: the entity's own AST subtree, docstring excluded, rename-sensitive. The crew **overruled the Commander's handoff** here — the Commander had reasoned a bare local-variable rename should not trip the flag; the crew argued a tag's prose can name a local variable, so a rename silently invalidates it. The Commander accepted this as the safer direction of error. You may re-open it if you disagree; say so explicitly rather than restating it as settled.
- **Evidence expectation:** authored-layer staleness — a tag whose anchor body changed while its text did not, going unflagged.
- **Map confidence flag:** staleness detection was designed but unbuilt and human-signed **accepted-untested** at confirm. This is its first build. Confirm rather than trust.

## Evidence Produced
`IMPLEMENTER_RESULT` at `.agent-work/issue-456/crew-handoffs/g6-implement-RESULT.md`, return status `complete`, no stop conditions hit. Recorded as engine evidence `e-g6-implement-1` against postcondition `g6-implement.c1`.

Commander-verified independently, not taken from the report:
- Full suite: **1805 passed, 2 skipped, 683 subtests, 0 failed**, exit 0. Baseline entering this gate was 1793 / 2 / 672 / 0.
- Fresh `build` then `check`: **7/7 ok, exit 0**, `deterministic-rebuild` among them.
- Closing selector `-k 'stale_tag'`: **12 passing**, against a designed baseline of 0.
- Working tree clean; crew commit `55b95314` present in `git log`.

**Known and disclosed, not defects to re-report unless you find them worse than stated:**
- The detector reports **nothing stale** against this repo. That is correct, not a null result: `render_report.json` shows `ids: 0` — there are zero authored anchors in this corpus today, so nothing exists that could be stale. It follows that the mechanism has only ever been exercised against a fixture.
- Docstring-only and comment-only edits are invisible to the span hash **by construction**. Deliberate.
- A bare local-variable rename **does** trip the flag. Accepted cost, see the decision anchor above.

## Suggested Model Tier
`sonnet` — bounded scope, three files, but the four questions above need real judgement rather than checklist matching.

## Stop Conditions
Stop and return BLOCK if the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return `REVIEW_RESULT`: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, and workflow feedback — including anything in this handoff that made the review harder than it needed to be. Previous crews on this run have caught eight Commander errors; that is the expected standard here, not an exception. If a number in this handoff is wrong, say so.

Note on the context governor: its HARD band fires around 15–20% context fill and will refuse `advance` until you attach a refresh-request — `attach <item> --type refresh-request --field seam=<item> --field why_ref=<the latest why_trail[-1].id>`. Every `advance` mints a new id, so read the id fresh each time; a cited one goes stale immediately. Expect it to fire early, before you have written anything; comply and continue.
