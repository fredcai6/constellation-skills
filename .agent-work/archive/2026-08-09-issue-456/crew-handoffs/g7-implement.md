# Implementer Handoff — g7

## Gate
`g7` — the authored comment-tag pass (issue #456). Eight of eleven gates are closed; this is the ninth and the last one with a real design call in it.

## Plan state
Create your plan at `.agent-work/issue-456/g7-implement/plan.json` — under the issue workbench, never at the worktree root.

## Task

Extract **authored comment tags** — bare `Word:` paragraph prefixes — and render them on the entity pages. Prior art for the shape is Go's `Deprecated:` convention: a bare capitalized word, a colon, and prose, at the start of a comment paragraph.

Grammar v0, already ruled and not yours to redesign:

- `Assumption:` `Constraint:` `Rationale:` `Rejected:` — four tags
- `See: <target>` — the reference form
- `[stable-id]` — the existing bracket anchor, already built and in use

**Then apply the cull test, in this gate, on first render.** Do not defer it.

## The cull test — the actual work of this gate

Critic SY5 argued four tags exceed what the evidence supports: no consumer distinguishes `Assumption:` from `Constraint:` from `Rationale:`, and the whole real corpus is six tags, four of them the same kind. The human **partially accepted** this and ruled the four-plus-one as **trial vocabulary with an explicit right to cull after contact**. The spec therefore states a test rather than a preemptive cut:

> If the extractor's consumer treats `Assumption:`/`Constraint:`/`Rationale:` identically at first render, collapse them to `Rationale:`/`Rejected:`/`See:`.

**Apply it honestly.** The question is not "can I invent a difference?" — it is "does the consumer *need* to tell these apart?" A distinction that exists only because you added it in order to pass the test is not a distinction; it is the test being gamed. If your renderer gives all three the same treatment — same section, same ordering, same formatting, no branch anywhere in the code that reads the kind — then they are identical to the consumer and the vocabulary collapses to three. That is a legitimate, expected, and probably correct outcome. Do not treat collapsing as failure.

Equally: if you find a real reason the consumer must branch on kind, keep four and **show the branch**. Either verdict is acceptable. A verdict you cannot point at code for is not.

### The verdict must be an ARTIFACT, not a claim

This gate's close criterion says so explicitly (critic F5): *process alone is not a close criterion*. Write the verdict to:

**`.agent-work/issue-456/cull-verdict.json`**

It must be checkable by a reviewer against the code, not merely readable. At minimum record: each tag kind; every place the consumer's behavior actually depends on that kind, cited as file and symbol (empty list if none); the resulting verdict (`collapse` or `keep`); and the reasoning. A reviewer must be able to read your renderer and confirm the "depends on kind" lists are complete and true. Make it easy for them to catch you if they are not.

Pin the artifact with a test: the file exists, parses, and its verdict field matches what the code actually does. That test is what makes the verdict a fact rather than a promise.

## The join to `g6` — this gate closes a limit that gate shipped with

`g6` built staleness detection: it hashes an entity's AST span and flags any tag whose anchor body changed while its text did not. It shipped with a named limit — **zero authored tags exist in this corpus**, so the detector has only ever been exercised against a bare `[slug]` anchor, never against real tag text.

Your tags mint through the **same `[slug]` allocator**, so the join is free: emit your tag statements anchored to the same slug and `g6`'s comparison, storage, and report machinery works unchanged. The `g6` crew verified this dependency direction rather than assuming it; you should not need to modify `extract.py`'s staleness code at all. If you find you do, that is a finding — say so rather than quietly reaching into it.

**Required, and this is a close criterion:** a test proving the staleness flag fires on a **real comment tag** — mutate the body of an entity carrying a `Constraint:` tag, leave the tag text alone, rebuild, and assert the flag. That is the first time this mechanism meets the thing it was built for.

Give that test a name containing **both** `comment_tags` and `stale_tag`, so it is visible to both gates' closing selectors.

## Evidence discipline this run has earned the hard way

Two gates in a row have been blocked or nearly closed on checks that could not fail. `g5` had a selector matching zero tests. `g6` shipped negative tests that stayed green when the whole feature was disabled. Do not make it three.

For every "does not extract this" or "is not a tag" test you write, run the check yourself: **break the extractor and confirm the test goes red.** A test asserting that `# Note: something` is not a tag will pass just as happily if tag extraction is entirely broken. Give it a positive control in the same method — assert a known-good tag *is* extracted alongside.

Report the result of that self-check in your result document with real numbers. If you skip it, the reviewer will run it and it will come back as a block.

## Corpus and fixtures

`C:\Programs\f1Brainz` is **READ-ONLY**. It holds the first real corpus — six authored tags in PR #733: four `Constraint:`, one `Rejected:`, one `Rationale:`, and zero anchor ids. You may **read** them to shape your grammar and to sanity-check the cull test against real usage. Do not write there, do not add it to this build, and do not treat its absence from your test suite as a gap — record it as future validation.

Build against a fixture in this repo. `tests/fixtures/overread_corpus/` is the precedent for a fixture corpus directory here.

Note the real corpus's shape when you weigh the cull test: four of six tags are the same kind. That is evidence, not noise.

## One convention gap to resolve

The spec names it and does not settle it: **where does a tag go when its rationale covers a whole function rather than a single line?** Resolve it from the existing anchor convention — a comment line directly above the `def`/`class`/assignment it names — and state your resolution plainly in the result document. If you cannot resolve it without inventing new policy, say so and flag it as a decision candidate rather than deciding it silently.

## Close criteria
- Tags extract and render.
- The cull test is applied **in this gate** and its verdict is recorded as an artifact at `.agent-work/issue-456/cull-verdict.json`, checkable against the code.
- The staleness flag is proven to fire on a real comment tag.
- Closing selector `python -m pytest tests/test_code_map.py -k 'comment_tags' -q --color=no` — **the current baseline is 0 collected, by design** (no such tests exist). It must collect and pass afterwards. A test the selector cannot see does not exist for this gate.
- Full suite green.

## Allowed scope
`scripts/code_map/` (the extractor's comment pass, and the renderer), `tests/test_code_map.py`, a new fixture directory under `tests/fixtures/`, and `.agent-work/issue-456/cull-verdict.json`.

## Specific exclusions — flag if you need to touch them
`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`, `page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers, `scripts/code_map/thresholds.py`, and **`g6`'s staleness machinery** (`span_hash`, the previous-store read, the slug diff). You should be joining to that machinery, not editing it.

## Constraints
- **f1Brainz is READ-ONLY.** Do not write to it.
- **The cull verdict must be a checkable artifact, not a claim.**
- The **full suite** must be green at this gate boundary (critic F6). It takes ~8 minutes — background it and poll.
- The run report carries **no timings**.
- Page headers carry path and `, N lines` — **never** `:<line>`. Standing human ruling; do not reintroduce line numbers anywhere on a page header.
- One name for one thing. If your tag kind has a name in the grammar, use that name everywhere — code, tests, artifact, prose.
- Stdlib only.

## Required evidence
1. Closing selector `-k 'comment_tags'`, before and after. Before: **0 collected, pytest exits 5**. Report the after count.
2. Selector `-k 'stale_tag'`, still green and grown by your join test. Current: **14 passed**.
3. The break-the-extractor self-check on your negative tests: how many went red, and name any that survived.
4. Full suite. Baseline **1807 passed, 2 skipped, 684 subtests, 0 failed**.
5. Fresh `python -m scripts.code_map build --root .` then `python -m scripts.code_map check --root .`, in that order — `check` reads a stale tree otherwise. Current: 7/7, exit 0.
6. `.agent-work/issue-456/cull-verdict.json` exists and its verdict matches the code.
7. `git status --porcelain` clean, work **committed** with explicit paths.

## Operating constraints, all real
- Worktree isolation REFUSES compound Bash: no loops, no heredocs, no `$(...)`, no `env -u`, no variable-assignment chaining, no long quoted strings. Use plain separate commands or a small script file. `git commit -F <file>` for long messages. For long engine `--why`/`--note` values, write to a file and call the engine from a tiny Python wrapper passing an argv list — two crews on this run found this route and it works.
- **Do NOT `git add -A`.** An untracked `map/` tree of ~3,930 generated pages lives here and is staged deliberately at the final gate. Explicit paths only. Other crews' bookkeeping may also be loose in the tree — stage only your own paths.
- **Do not push, merge, or force-push.** Commit your own work; that is expected.
- When an evidence script checks whether a file reverted cleanly, use `git diff --quiet -- <path>` or compare blob OIDs. **Do not use `git status --porcelain`** — it false-negatives here under `core.autocrlf`, and two independent scripts were fooled by it in the previous gate.
- The full suite takes ~8 minutes. Background it and poll; do not block.
- Engine CLI: `--file` BEFORE the verb, `--session-id` AFTER. `advance` needs a positional id AND `--why`, and the item must be `in-progress` — `start <id>` first. `amend --delta`'s op key is `"op"`, not `"kind"`.
- The context governor's HARD band fires early, often before you have written anything — it trips on orientation cost. It refuses `advance` until you attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`. Read that id fresh every time. Comply and keep moving.

## Map anchors (inbound)
- **Structural:** `scripts/code_map/` extractor — comment pass.
- **Capability:** derive structure from source.
- **Constraint:** one name for one thing.
- **Decision:** the tag vocabulary and the cull test. Its reach extends beyond this run — **surface it as a decision candidate if the vocabulary collapses**, because collapsing changes what every future author writes, not just what this build parses.
- **Evidence:** authored-layer staleness — your join test is what finally exercises it against real tag text.
- **Survival law, from the spec:** a tag survives when a tool visibly consumes it. That law is the cull test's reasoning in one line; keep it in view.

## Authority
Commit in this worktree: yes. Push, PR, merge: no — the Commander owns those. Escalating upward is always legitimate. Crews on this run have caught eight Commander errors; if this handoff is wrong, say so plainly rather than working around it.

## Return format
Return `IMPLEMENTER_RESULT` at `.agent-work/issue-456/crew-handoffs/g7-implement-RESULT.md`: what shipped, the cull verdict and the reasoning behind it, scope touched, the evidence above with real numbers, the convention-gap resolution, assumptions, stop conditions, out-of-scope observations, and workflow feedback. State plainly anything that did not fully land.

## Suggested model tier
`sonnet`.
