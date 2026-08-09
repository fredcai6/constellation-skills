# Reviewer Handoff — g7

## Gate
`g7` — the authored comment-tag pass and the cull test (issue #456). Ninth of eleven gates.

## Survey State Location
`.agent-work/issue-456/g7-review/review.json` — under the issue workbench, never at the worktree root.

A survey has **no `reopen` verb**. To re-verify after consolidating: `append` a recheck item → `record` it → re-`consolidate` with `--override-reason`. The original failing item stays in the record for audit and stops blocking.

## What Was Implemented

Bare `Word:` paragraph comment tags now extract into `tag` statements and render on entity and module pages. The cull test was applied on first render and returned **collapse**: the shipped grammar recognizes `Rationale:` / `Rejected:` / `See:` only. `Assumption:` and `Constraint:` are **retired** — a comment using either is now ordinary prose and will not extract.

The staleness join to `g6` is proven against a real tag for the first time.

Committed at `0d1af801`. Inspect with `git show 0d1af801`. Files: `scripts/code_map/extract.py`, `scripts/code_map/render.py`, `tests/test_code_map.py`, `tests/fixtures/comment_tags_corpus/`, `.agent-work/issue-456/cull-verdict.json`.

## Task Statement

Extract authored comment tags (bare `Word:` prefixes, prior art Go's `Deprecated:`). On first render **apply the cull test** (critic SY5): if the consumer treats `Assumption:`/`Constraint:`/`Rationale:` identically, collapse them to `Rationale:`/`Rejected:`/`See:`. The human ruled the vocabulary **trial vocabulary with an explicit right to cull after contact**, so the test is applied in this gate, not deferred. f1Brainz holds six real tags as the first corpus but is READ-ONLY: build against a fixture and record the external corpus as future validation.

## THE question this review exists to answer

**Collapse was the right verdict. But "collapse" has two readings, and the crew picked one without noticing the other.**

The spec says collapse `Assumption:`/`Constraint:`/`Rationale:` *to* `Rationale:`/`Rejected:`/`See:`. That can mean:

- **Retire** — stop recognizing the two words. What the crew shipped. `TAG_START` is `^[ \t]*#[ \t]*(Rationale|Rejected|See):[ \t]*(.*)$`. A `# Constraint: ...` comment is now prose.
- **Alias** — keep recognizing them, normalize them to `Rationale` at extraction. The vocabulary still collapses to one rendered kind; existing text keeps working.

Both satisfy "the consumer no longer distinguishes them." They differ enormously in cost, and here is why it matters: **the only real corpus that exists is four `Constraint:` tags out of six** (f1Brainz PR #733 — 4 `Constraint`, 1 `Rejected`, 1 `Rationale`, 0 `Assumption`, 0 `See`). Under the shipped grammar, **four of the six real tags in existence silently stop being tags.** They do not error. They do not warn. They render as ordinary comments and vanish from the map — and `g6`'s staleness detector, which exists precisely to catch a tag going quietly wrong, will never see them either, because they are no longer tags.

The crew cites that corpus shape as evidence the cull "costs little," reasoning that most authors already converged on one word. Test that reasoning hard. The word they converged on is the one being deleted. Read the same fact the other way — 67% of real authored tags break — and say which reading holds.

Your job is not to overturn the collapse. It is to answer: **does the ruling's "right to cull" authorize retiring the words, or only unifying their treatment?** And separately, **is silent** the right failure mode for a retired keyword, or should a `# Constraint:` comment produce a one-line advisory pointing the author at `Rationale:`? Note that `g6` just fixed a near-identical problem in the opposite direction — a silent skip was rejected there because it converts a fault into permanently-dead detection with no signal.

Give a clear recommendation. If you think the shipped behavior is right, say so and say why the f1Brainz breakage is acceptable.

## Also verify

**1. Is the cull test itself sound, or self-fulfilling?** The crew built `tag_lines` with no dispatch on kind, *then* asked whether the consumer distinguishes kinds. That ordering is either exactly right (the honest way — don't invent a distinction to dodge the test) or subtly circular (a renderer written flat will always report flatness). Decide which, and say what would have had to be true for the test to return "keep." If no realistic renderer could have returned "keep," the test could not fail — the tc38/tc47 defect class this run has hit twice. That is the sharpest version of this question and I want your answer to it.

**2. Does the AST-walk pinning test have teeth?** `CommentTagRenderTests::test_comment_tags_render_path_carries_no_branch_on_kind` walks `tag_lines`'s own AST and fails if any `Compare` node mentions `kind`. Add a branch on kind to `tag_lines` and confirm it goes red. Then check what it does **not** catch: a `dict` lookup keyed on kind, a `getattr`, an f-string conditional, a `match` statement, `kind in (...)`. If a branch can be written that the test misses, the pin is narrower than it reads.

**3. Do the five cull-verdict pinning tests re-derive, or restate?** The crew claims each re-derives its assertion from `extract.TAG_START.pattern` or an independent AST walk, "not from the file's own prose." Verify. A test that reads its expectation out of the artifact it is checking can only ever agree with it — this run already proved that principle load-bearing at `g2`, where two hand-independent declarations of the same grammar caught a real divergence.

**4. The staleness join.** `CommentTagStaleAnchorJoinTests::test_comment_tags_stale_tag_flags_a_real_body_change_under_a_live_tag` is the first time `g6`'s detector meets real tag text. Confirm it genuinely exercises the path rather than re-testing the anchor mechanism under a new name, and confirm `g6`'s machinery (`span_hash`, the previous-store read, the slug diff) was not modified — it was excluded from this gate's scope.

**5. TDD discipline, disclosed by the crew itself.** For `m1`–`m4` it wrote test and implementation together and inferred red from baseline absence rather than observing it; `m5` got the full literal treatment with three real breakages, observed and reverted. The disclosure is honest and `m5` is the item where it mattered most. Judge whether the inferred-red items carry real risk — specifically whether any `m1`–`m4` test could pass against an empty implementation.

**6. The negative-test self-check.** The crew ran three breakages and reports zero negative tests survived. It also disclosed that its first attempt at one fixture **passed vacuously** — a `# Note:` comment above a bare `return`, which is not a tag call site — and that it corrected the fixture to use an `Assign` before re-running. Good catch by them; verify the corrected fixture is genuinely the real attack surface, and look for the same vacuity in the fixtures they did *not* revise.

**7. The convention gap.** The crew resolved "where does a tag go when its rationale covers a whole function?" as: the tag binds to the nearest enclosing entity or module, since pages exist per-entity and never per-statement. It flags this as a real design choice not pre-ruled. Judge whether the resolution follows from the existing anchor convention or invents new policy.

## Close criteria
- Tags extract and render.
- The cull test is applied in this gate and its verdict is an artifact at `.agent-work/issue-456/cull-verdict.json`, **checkable against the code** — process alone is not a close criterion (critic F5).
- The staleness flag is proven to fire on a real comment tag.
- Closing selector `python -m pytest tests/test_code_map.py -k 'comment_tags' -q --color=no` — baseline was **0 collected, exit 5**, by design.
- Full suite green.

## Allowed scope
`scripts/code_map/`, `tests/test_code_map.py`, `tests/fixtures/comment_tags_corpus/`, `.agent-work/issue-456/cull-verdict.json`.

## Specific exclusions — flag if touched
`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`, `page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers, `scripts/code_map/thresholds.py`, and **`g6`'s staleness machinery**.

**Do not `git add -A`.** An untracked `map/` tree of ~3,975 pages lives here and is staged deliberately at the final gate. Explicit paths only.

`C:\Programs\f1Brainz` and `C:\Programs\superCoolSpaceSim` are READ-ONLY. Read f1Brainz's six tags — you will need them for the main question — and write nothing.

## Constraints
- **f1Brainz is READ-ONLY.**
- **The cull verdict must be a checkable artifact, not a claim.**
- Full suite green at this boundary (critic F6).
- The run report carries no timings.
- Page headers carry path and `, N lines` — never `:<line>`.
- One name for one thing.
- Stdlib only.

## Map Anchors (inbound)
- **Structural:** `scripts/code_map/` extractor — comment pass.
- **Capability:** derive structure from source.
- **Constraint:** one name for one thing.
- **Decision:** the tag vocabulary and the cull test — **reach extends beyond this run**. The crew correctly flagged the collapse as a decision candidate. The Commander's position: the human pre-authorized exactly this outcome ("trial vocabulary with an explicit right to cull after contact", and the spec names the collapse target), so the crew executed a standing ruling rather than making a new one. Whether *retirement* is inside that authorization is the open question above.
- **Evidence:** authored-layer staleness — this gate's join test is what finally exercises it against real tag text.
- **Survival law, from the spec:** a tag survives when a tool visibly consumes it.

## Evidence Produced

`IMPLEMENTER_RESULT` at `.agent-work/issue-456/crew-handoffs/g7-implement-RESULT.md`, return status complete, no stop conditions.

Commander-verified independently, not taken from the report:
- Full suite **1825 passed, 2 skipped, 692 subtests, 0 failed** (378s). Baseline 1807 / 2 / 684 / 0 — delta matches the new tests exactly, no regressions. **Note: the crew never filled this number in itself** — it backgrounded the run, left section 4 reading "see final numbers below", and stalled ~20 minutes in final verification until I ran the suite and handed it the figures. Treat any evidence in that document as Commander-supplied unless it says otherwise.
- `-k 'comment_tags'`: **18 passed, 8 subtests, exit 0** (baseline 0).
- `-k 'stale_tag'`: **15 passed, 12 subtests, exit 0** (baseline 14 — grown by exactly the one join test).
- Fresh `build` then `check`: **7/7, exit 0**, `deterministic-rebuild` included. Build reports 112 modules, 3862 entities, 3975 pages, `ids: 0`, `stale_tags: []`.
- `TAG_START` and `tag_lines` read directly and match the artifact's claims.
- Tree clean at `0d1af801`.

## Suggested Model Tier
`sonnet`.

## Stop Conditions
Stop and return BLOCK if the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
`REVIEW_RESULT` at `.agent-work/issue-456/crew-handoffs/g7-review-RESULT.md`: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback. Answer the main question with a recommendation, not a survey of options.

Crews on this run have caught eight Commander errors. If a number or a claim in this handoff is wrong, say so.

## Operating notes
- Worktree isolation REFUSES compound Bash: no loops, no heredocs, no `$(...)`, no `env -u`, no long quoted strings. Use plain separate commands or a script file. For long engine findings, write to a file and call `checklist_engine.main([...])` from a small Python wrapper with an argv list — two reviewers on this run found this route.
- When checking whether a file reverted cleanly after an attack, use `git diff --quiet -- <path>` or blob OIDs. **Not** `git status --porcelain` — it false-negatives here under `core.autocrlf` and fooled two scripts at `g6`.
- The full suite takes ~7 minutes. I have already run it; spend your effort on the questions above rather than re-running it.
- The context governor's HARD band fires early, before you write anything. Attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`, reading the id fresh each time.
