# Implementation Result

## Assigned gate
`g7` remediation (issue #456) — rework pass on a BLOCK. Four fixes: tag staleness independent of anchors, alias instead of retire, widen the AST pin test, correct two overstated claims.

## Completed slice
All four fixes landed. Tags are now watched for staleness on their own (no anchor required); `Assumption:`/`Constraint:` are recognized again and normalize to `Rationale:` at extraction instead of silently vanishing; the AST pin test catches dict-lookup and `match` dispatch, not just an explicit compare; the re-derivation-count and join-framing claims are corrected here (the prior crew's own RESULT doc was left untouched, per the brief).

## Scope
**Files changed:**
- `scripts/code_map/extract.py` — `TAG_START` widened, `TAG_KIND_ALIAS` added, `tag_check()` now hashes an enclosing-node span and normalizes kind, `Extractor.__init__`/`visit_ClassDef`/`_func` carry a new `encl_nodes` stack, `visit_Assign`/`visit_AnnAssign` pass it through, `run()` diffs tag hashes the same way it diffs anchor hashes and emits `stale-tag` rows
- `scripts/code_map/render.py` — `load_stores()` intercepts `p == "stale-tag"` into the existing `stale_tags` list; the ADVISORY line and report-field comment reworded to cover both anchors and tags
- `tests/test_code_map.py` — new fixtures/tests for tag-only staleness (`CommentTagOnlyStaleTagTests`, `CommentTagOnlyStaleTagRenderReportTests`), a corrected `CommentTagStaleAnchorJoinTests` docstring + coexistence assertion, an alias round-trip (extraction + render), a rewritten `CommentTagNegativeTests` case, a shared `_kind_dispatch_nodes` helper used by both pin tests, and `CullVerdictArtifactTests` updated for the widened grammar + alias mapping
- `tests/fixtures/comment_tags_corpus/corpus.py` — `retired_words()` renamed `aliased_words()`, reflecting the new behavior
- `.agent-work/issue-456/cull-verdict.json` — `shipped_keywords` widened to all five words, `kind_normalization` field added, per-kind notes and `consequence` rewritten to describe aliasing

**Specific exclusions touched:** no. `span_hash`'s body, `anchor()`, and the anchored diff block in `extract.py:run()` are byte-identical to what shipped at `0d1af801` — verified by inspection, not just intent (the new tag-staleness code is a parallel block added immediately after the existing one, never edited into it). `is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`, `page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers, and `thresholds.py` were not touched.

## Behavior changed
Yes. (1) A tag's staleness is now detected independent of any anchor — the real corpus (zero anchors) can now actually be watched. (2) A comment authored with `Assumption:`/`Constraint:` extracts and renders again, normalized to `Rationale:` — no longer silently dropped. (3) The render-path pin test now catches two dispatch shapes it previously missed. On this repo today the net effect is still zero rendered pages (this repo carries zero authored tags), matching design intent.

## Map Impact
- **Structural anchors touched:** `scripts/code_map/extract.py`'s `Extractor` (new `encl_nodes` stack, `tag_hashes` dict, widened `TAG_START`, new `TAG_KIND_ALIAS`), `run()` (new tag-hash read/diff/emit, parallel to the anchor path); `scripts/code_map/render.py`'s `load_stores()` (new `stale-tag` interception).
- **Capabilities added/changed:** tag staleness detection no longer depends on an anchor being present. `Assumption:`/`Constraint:` are recognized-and-aliased keywords, not retired ones.
- **Constraints/assumptions touched:** "g6's anchor path is untouched" — honored, verified by inspection (see Scope above). "tag_lines stays branch-free" — honored; the AST-walk pin test itself was widened, `tag_lines` was not touched. "the run report carries no timings" — the review's finding here was itself overruled by the brief (that constraint governs `render_report.json`, the artifact the determinism check diffs, not this document); this document states real wall-clock timings below, deliberately.
- **Decision candidates:** none new. The vocabulary-collapse decision candidate from the original build stands unchanged (still `collapse`, now implemented as alias); still awaiting confirmation beyond this gate.
- **Claims/evidence produced:** the disable-attack (below) is the strongest evidence in this pass — it names the exact tests that catch removal of the new mechanism, not an inference.
- **Triage candidates:** none new beyond the two already filed (tc1: `See:` tags render as literal text; tc2: tag/anchor binding-granularity asymmetry).

## Test mode
**Required:** test-first where a red state is real (fix 1's new mechanism); test-after/inspection for the alias and pin-test fixes, which extend existing, already-tested surfaces.
**Satisfied:** yes for fix 1 — RED observed for real (the mechanism did not exist), not inferred; GREEN observed after. Fix 3 was verified by a live mutation attack against the check logic itself (not the shipped code), since `tag_lines` carries no bug to write a failing test against.

## Evidence

### 1. `-k 'comment_tags'`, before/after
```bash
python -m pytest tests/test_code_map.py -k 'comment_tags' -q --color=no
```
- **Before (this pass's baseline, per brief):** 18 passed.
- **After:** **24 passed, 13 subtests passed, exit 0.** (+6: 3 tag-only staleness extraction tests + 1 tag-only staleness render-report test + 1 alias-extraction test + 1 alias-render test; the retired-keyword test was rewritten in place, not added.)

### 2. `-k 'stale_tag'`, before/after
```bash
python -m pytest tests/test_code_map.py -k 'stale_tag' -q --color=no
```
- **Before:** 15 passed.
- **After:** **19 passed, 13 subtests passed, exit 0.** (+4: the same tag-only staleness tests, which all carry both `comment_tags` and `stale_tag` in their names by convention.)

### 3. The tag-staleness disable attack (fix 1's required evidence)
`stale_real_tags = sorted(...)` in `extract.py:run()` was temporarily replaced with `stale_real_tags = []`, leaving everything else (span-hash persistence, the enclosing-node stack, `render.py`'s interception) intact.

```bash
python -m pytest tests/test_code_map.py -k 'stale_tag' -q --color=no
```
Result: **3 failed, 16 passed, 12 subtests passed** — exactly the tests that name the mechanism:
- `CommentTagStaleAnchorJoinTests::test_comment_tags_stale_tag_flags_a_real_body_change_under_a_live_tag` (the coexistence assertion added this pass)
- `CommentTagOnlyStaleTagTests::test_comment_tags_stale_tag_flags_a_real_body_change_with_zero_anchors_present`
- `CommentTagOnlyStaleTagRenderReportTests::test_comment_tags_stale_tag_lands_in_the_same_render_report_field`

**No survivor.** The change was reverted; a re-run of `-k 'stale_tag'` returned to 19 passed, confirming a clean revert.

### 4. Tag-and-no-anchor proof (fix 1's other required evidence)
`CommentTagOnlyStaleTagTests` uses `_TAG_ONLY_STALE_SOURCE`, a fixture whose one function carries a `Rationale:` tag and **zero** anchors — the test's own first assertion (`{st["o"] for st in before if st["p"] == "anchored"} == set()`) is an input precondition that fails loudly if that ever stops being true. This is the fixture the shipped join test's own docstring claimed to be but was not (its fixture carried both a `[slug]` anchor and a tag, so its flag fired off `p == "stale-anchor"`, g6's own untouched predicate).

### 5. The alias round-trip (fix 2's required evidence)
```bash
python -m pytest tests/test_code_map.py -k 'constraint_keyword' -q --color=no
```
Result: **2 passed** — `test_comment_tags_constraint_keyword_extracts_normalized_to_rationale` (a `# Constraint: ...` comment extracts with `o == "Rationale"`) and `test_comment_tags_constraint_keyword_renders_as_rationale` (the page shows `Rationale: budget stays under 200ms...` and contains no literal `Constraint:`). `tag_lines` itself is unmodified — the AST-walk pin test (widened by fix 3) still passes against it.

### 6. Live mutation attack (fix 3's required verification)
A scratch script (not committed) built two mutant copies of `tag_lines`'s logic: a dict-lookup dispatch (`LABEL[t['kind']]`) and a `match kind:` statement. Result:

| variant | old (Compare-only) check | new (`_kind_dispatch_nodes`) check |
|---|---|---|
| real shipped `tag_lines` | clean | clean |
| dict-lookup dispatch mutant | **clean (missed it)** | **caught** |
| `match` statement mutant | **clean (missed it)** | **caught** |

Confirms the old check's blind spot exactly as the review described, and that the widened check closes it without a false positive on the real code.

```bash
python -m pytest tests/test_code_map.py -k "no_branch_on_kind or collapse_kinds_have_no_render_dependency" -q --color=no
```
Result: **2 passed.**

### 7. Full suite
```bash
python -m pytest tests/ -q --color=no
```
Baseline (this pass's starting point): 1825 passed, 2 skipped, 692 subtests, 0 failed.
**Result: 1831 passed, 2 skipped, 697 subtests passed, 0 failed, 606.05s (0:10:06).** Run by this crew, backgrounded and polled to completion in-context (not left blank). +6 passed matches the net new tests across fixes 1 and 2 exactly; +5 subtests; zero regressions elsewhere.

### 8. Fresh build + check
```bash
python -m scripts.code_map build --root .
python -m scripts.code_map check --root .
```
- `build`: exit 0. `pass1: 113 modules indexed`, `statements: 98109 over 113 files (0 failures)`, 3881 entities, 3995 pages, `ids: 0`.
- `check`: **7/7 checks passed, exit 0** (no-empty-pages, page-accounting, refs-line-self-consistent, entity-symbol-join, page-location-matches-content, inbound-attribution, deterministic-rebuild).

### 9. `cull-verdict.json`
Rewritten: `verdict` is still `"collapse"`; `shipped_keywords` now lists all five words (matching the widened `TAG_START`); a new `kind_normalization` field states the alias mapping; every per-kind `note` and the `consequence` field describe aliasing, not retirement. `CullVerdictArtifactTests::test_comment_tags_cull_verdict_matches_extractors_recognized_keywords` re-derives BOTH the widened pattern and the normalization mapping against the live code (`extract.TAG_START.pattern`, `extract.TAG_KIND_ALIAS`), not the artifact's own prose.

### 10. Git status
Committed as `ffa959c5` ("g7 remediation: tag staleness independent of anchors, alias not retire"), 8 files changed, explicit paths only (no `git add -A`): `scripts/code_map/extract.py`, `scripts/code_map/render.py`, `tests/test_code_map.py`, `tests/fixtures/comment_tags_corpus/corpus.py`, `.agent-work/issue-456/cull-verdict.json`, this crew's own plan (`.agent-work/issue-456/g7-remediate/plan.json` + `.journal`), and this RESULT doc. `.agent-work/issue-456/execute.json.journal` and `.agent-work/issue-456/g7-review/review.json` showed as modified in `git status` but were NOT touched by this crew — a concurrent process was writing them; excluded from this commit.

## TDD evidence, if required
- **Failing test observed (fix 1, real RED):** before any implementation code was written, `python -m pytest tests/test_code_map.py -k "CommentTagOnlyStaleTag" -q --color=no` → `2 failed, 2 passed` (the two flag-firing assertions failed with `0 != 1`; the two negative-control tests passed vacuously, as expected with no mechanism yet).
- **Passing test observed:** after implementation, the same selector → all green; full selectors reported in Evidence #1/#2 above.
- **Refactor while green:** no refactor pass beyond the disable-attack (which reverted cleanly, confirmed by re-running the selector, not by `git status --porcelain` per this run's own operating constraint about `core.autocrlf` false negatives).

## Docs/contracts touched
- `.agent-work/issue-456/cull-verdict.json` — this gate's own close criterion, updated to match the code (see Evidence #9).

## Assumptions
- The "enclosing entity" a statement-level tag's staleness hash covers is the entity/module `self.here()` names — the SAME node `visit_Assign`/`visit_AnnAssign`'s caller already treats as the tag's owner — not the tagged statement itself. This follows the gate's own rule literally ("hash each tag's enclosing entity span"), and it is what makes the real corpus's majority shape (a tag above a function-local assignment) produce a hash that actually varies when the surrounding function changes, not just when that one line does.
- A tag's cross-extraction identity is `(owning symbol, tag text)`. A tag whose text changes is treated as a different tag, not a stale one — this is the gate's own stated rule ("a tag whose text also changed is not stale"), not an inferred convenience; it is also directly tested (`test_comment_tags_stale_tag_does_not_flag_when_tag_text_also_changes`).
- The `id` field on a `stale-tag` report row is `"{kind}: {text}"`, truncated to 80 chars — the same string a human already sees rendered on the page, since a tag has no natural slug-like identifier the way an anchor does.

## Stop conditions hit
None. All plan items advanced to completion through the engine.

## Out-of-scope observations
None new. tc1 (`See:` tags render as literal text) and tc2 (tag/anchor binding-granularity asymmetry) remain filed from the original build, unchanged by this pass.

## Workflow Feedback

- **Handoff gaps:** none material. One ambiguity worth naming for a future remediation brief: "hash each tag's enclosing entity span" (quoted from `g6`'s original task wording) does not by itself say whether "enclosing entity" means the statement the tag sits directly above or the entity/module that statement lives inside — for a whole-function/class tag these are the same node, so the original build's design never had to distinguish them. This pass read it as the latter (matching `self.here()`'s own convention-gap resolution from the original build), stated as an explicit Assumption above rather than left implicit.
- **Context rediscovered:** none — the brief's own code citations (`p == "anchored"` vs `p == "tag"`, the fixture's dual anchor+tag shape) were accurate and let the defect be re-confirmed directly in under the time it would have taken to re-derive it from scratch.
- **Instructions improvised around:** the brief's fix 3 said "verify by writing the evading mutation and watching the test's behavior." Since the real, shipped `tag_lines` has no dispatch bug to attack, there is no failing-test-on-real-code to observe — the verification necessarily runs against a scratch mutant of the CHECK's target shape, not the shipped file. Reported literally as a comparison table (old check vs. new check, against both the real code and two mutants) rather than a single red/green pair, since that is what actually demonstrates the fix.
- **What would have made this easier:** none.

## Return status
`complete`
