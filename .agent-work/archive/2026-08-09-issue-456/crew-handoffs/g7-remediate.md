# Implementer Handoff — g7 remediation

## Gate
`g7` — comment-tag pass (issue #456). **Rework pass on a BLOCK.**

## Plan state
`.agent-work/issue-456/g7-remediate/plan.json` — under the issue workbench, never at the worktree root.

## Read first
1. This brief, in full.
2. `.agent-work/issue-456/crew-handoffs/g7-review-RESULT.md` — the review that blocked.
3. `.agent-work/issue-456/crew-handoffs/g7-implement-RESULT.md` — what you (or your predecessor) shipped.

The build at `0d1af801` is good work. The cull verdict is sound and stays. Three things need fixing, and the first one is bigger than the review scored it.

---

## FIX 1 — THE BIG ONE: the staleness mechanism does not watch tags at all

**The gate's stated evidence expectation is unmet, and the test that claims otherwise passes for the wrong reason.**

Here is what the Commander verified directly in the code, not inferred:

- `extract.run()`'s staleness diff reads only statements where `st["p"] == "anchored"` (around line 1145). Tags are emitted as `p == "tag"`. **The diff never sees a tag.**
- `span_hash` is persisted only in `Extractor.anchor()` — the anchor path. Tag emission persists no hash.
- The join test's fixture, `_STALE_TAG_SOURCE`, gives its one function **both** a `[rate-double]` anchor **and** a `Rationale:` tag. The flag fires because of the **anchor**. Delete the anchor line and the tag goes completely unwatched.

So the test proves *coexistence*, not a join — the reviewer's phrase, and it is exactly right. And this is not academic: **the only real corpus in existence has zero anchors.** f1Brainz PR #733 is six tags and `0 authored slugs`. Under what shipped, **not one real tag would ever be watched for staleness.**

That is critic IF4/TS8's original problem, untouched, in the precise corpus it was raised to protect. `g6`'s gate task was worded *"hash each tag's enclosing entity span; flag any tag whose anchor body changed while its text did not"* — `g6` built it against anchors because no tags existed yet. Tags exist now. Wiring them in was always this gate's job.

### What to build

Extend the staleness mechanism to cover tags as first-class subjects:

- Persist a `span_hash` of the enclosing entity on **tag** statements, the same way `anchor()` already does for anchors. Reuse `span_hash` unchanged — do not write a second hasher.
- Extend `run()`'s old-vs-new diff to compare tags too. A tag's identity is **its own text plus its position/owner**, not a slug — tags have no slug. Work out a stable key and state your reasoning; the rule to implement is the gate's own words: *flag when the enclosing body changed while the tag text did not*. A tag whose text also changed is not stale — the author already revisited it.
- Surface flagged tags in the same run report and with the same `ADVISORY` prefix convention `g6` established. Do not invent a second reporting channel and do not make it build-failing — `g6`'s advisory-only severity ruling was examined and affirmed, and it governs here.

**Do not modify `g6`'s anchor path.** Extend alongside it. If you genuinely cannot avoid touching `span_hash`, `anchor()`, or the anchored diff, say so and explain — do not quietly reach in.

### The test that proves it, and the trap to avoid

The required test: **an entity carrying a tag and NO anchor at all.** Mutate its body, leave the tag text alone, rebuild, assert the flag fires. If your fixture has an anchor anywhere on that entity, the test is worthless — that is precisely how the shipped one passed while proving nothing.

Then attack your own work: **delete the tag-staleness emission and confirm that test goes red.** Report the result. This run has blocked twice on checks that could not fail; this is the third variation of the same disease and I would rather you find it than the reviewer.

Also fix the existing join test's fixture and docstring so it stops claiming more than it demonstrates, or split it: one test for a tag-only entity (the real case), one for an anchored entity (the existing case). Its current docstring says it is "the first test that mutates a tagged entity's body and checks the flag" — that will be true only after this fix.

---

## FIX 2 — alias the retired keywords instead of retiring them

**The cull verdict stands. `collapse` was right. What is wrong is what "collapse" was taken to mean.**

The spec text supports two readings and the crew took one without noticing the other. The reviewer recommends **alias**, the Commander accepts that recommendation, and here is why it wins:

Retire's effect on the only real corpus is that **four of six real tags stop being tags** — silently. No error, no warning, and invisible to the staleness detector that exists to catch tags going wrong. The spec's own survival law is *"a tag survives when a tool visibly consumes it"*; retiring silently is that law's failure condition landing on real text. The `4 of 6 already use one word` fact was read as "the cull costs little"; it reads at least as well as "retire breaks the majority of the corpus." And the sharpest evidence is self-inflicted: the cull broke this gate's **own worked example**, forcing a mid-gate substitution in the join test's docstring.

`g6`, one gate earlier on this same run, blocked on the identical shape in the other direction — a silent skip converts a fault into permanently-dead detection with no signal.

### What to build

- Widen `TAG_START`'s alternation to recognize `Assumption` and `Constraint` again.
- Normalize their `kind` to `Rationale` at the emission site — one lookup, not a branch in the renderer.
- `tag_lines` must stay exactly as branch-free as it is now. **The cull test's own evidence must be untouched** — that is the point of doing it this way. Re-run the AST-walk pin test and confirm it still passes for the same reason.
- Update `.agent-work/issue-456/cull-verdict.json`: the verdict is still `collapse`, but `shipped_keywords`, the per-kind notes, and the `consequence` field must now describe aliasing rather than retirement. Its `consequence` currently says a retired word "will not extract or render" — that must become false and be rewritten. The artifact is a close criterion; leaving it describing behavior that no longer exists would be worse than the original defect.
- Keep the pinning tests honest against the new reality.

---

## FIX 3 — the pin test is narrower than it claims

`test_comment_tags_render_path_carries_no_branch_on_kind` walks `tag_lines`'s AST and fails on any `Compare` node mentioning `kind`. The reviewer proved it catches an explicit `if kind ==` but **does not** catch a dict-lookup dispatch or a `match` statement — neither produces an `ast.Compare` node.

Either widen the check to cover dispatch-by-lookup and `match`, or correct the docstring to say what it actually verifies ("no explicit comparison on kind"). Widening is better if it is cheap; an honest narrow claim beats a broad false one either way. Whatever you choose, verify by writing the evading mutation and watching the test's behavior — do not reason about it.

---

## FIX 4 — two overstated claims

- The commit message and result document say the cull verdict is "pinned by 5 tests that re-derive the claim from the code." The reviewer checked: **2 of 5 re-derive; 3 check the artifact's own internal consistency.** A test that reads its expectation out of the artifact it is checking can only ever agree with it. Correct the wording, and consider whether the 3 should be strengthened to genuinely re-derive.
- The staleness test's "join" framing — fix 1 makes this true; make sure the prose matches once it is.

---

## NOT in this pass

- **The timings finding is overruled, and here is the reasoning so you can rely on it.** The reviewer flagged wall-clock figures in `g7-implement-RESULT.md` as violating "the run report carries no timings." That constraint's own stated rationale is *"so the determinism diff can cover it"* — it governs `render_report.json`, the machine-read artifact the determinism check diffs. A human-facing markdown result document is not in that diff, and stripping timings from prose buys nothing. My handoff quoted the constraint without scoping it, which is what invited the reading. Leave the timings; they are useful evidence.
- Do **not** revisit the cull verdict itself. `collapse` stands.
- Do **not** change the advisory-only severity.
- `tc1` (`See:` tags render as literal text, not links) and `tc2` (tag/anchor binding-granularity asymmetry) are filed for triage. Out of scope.
- The Fowler duplication findings are non-blocking. Skip.

## Allowed scope
`scripts/code_map/extract.py`, `scripts/code_map/render.py`, `tests/test_code_map.py`, `tests/fixtures/comment_tags_corpus/`, `.agent-work/issue-456/cull-verdict.json`.

## Specific exclusions — flag if you must touch them
`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`, `page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers, `thresholds.py`, and **`g6`'s anchor-path staleness code** (`span_hash`'s body, `anchor()`, the anchored diff). Extend alongside; do not rewrite.

## Constraints
- Full suite green at this boundary (critic F6). Baseline **1825 passed, 2 skipped, 692 subtests, 0 failed**.
- `render_report.json` carries no timings.
- Page headers carry path and `, N lines` — never `:<line>`.
- One name for one thing.
- Stdlib only.
- f1Brainz is READ-ONLY.

## Required evidence
1. `-k 'comment_tags'` before/after. Current **18 passed**.
2. `-k 'stale_tag'` before/after. Current **15 passed**.
3. **The tag-staleness disable attack**: delete the tag-flag emission, report how many tests go red, name any survivor. This is the evidence fix 1 exists to produce.
4. A test proving the flag fires on an entity with a tag and **no anchor**.
5. The alias round-trip: `# Constraint: x` extracts, renders as `Rationale: x`, and `tag_lines` still carries no branch on kind.
6. Full suite.
7. Fresh `build` then `check`, in that order. Current 7/7 exit 0.
8. `cull-verdict.json` updated and matching the code.
9. Clean tree, **committed** with explicit paths.

## Operating constraints
- Worktree isolation REFUSES compound Bash: no loops, no heredocs, no `$(...)`, no `env -u`, no variable-assignment chaining, no long quoted strings. Plain separate commands or a script file. `git commit -F <file>`. For long engine `--why`/`--note`, write to a file and call `checklist_engine.main([...])` from a small Python wrapper with an argv list.
- **Do NOT `git add -A`.** The untracked `map/` tree is staged deliberately at the final gate. Explicit paths only.
- Do not push, merge, or force-push. Commit your own work.
- Checking a file reverted cleanly: `git diff --quiet -- <path>` or blob OIDs. **Never** `git status --porcelain` — it false-negatives here under `core.autocrlf`.
- The full suite takes ~7 minutes. Background it and poll. **Report the number yourself** — the previous crew left that field blank and stalled 20 minutes waiting on buffered output.
- Engine CLI: `--file` BEFORE the verb, `--session-id` AFTER. `start <id>` before `advance`. `amend --delta` uses `"op"`, not `"kind"`.
- The governor's HARD band fires early, before you write anything. Attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`, read fresh each time.

## Authority
Commit here: yes. Push, PR, merge: no. Escalating upward is always legitimate. Crews on this run have caught eight Commander errors — if this brief is wrong, say so.

## Return format
`IMPLEMENTER_RESULT` at `.agent-work/issue-456/crew-handoffs/g7-remediate-RESULT.md`. State plainly anything that did not fully land; a partial fix reported honestly beats a clean-looking claim.

## Suggested model tier
`sonnet`.
