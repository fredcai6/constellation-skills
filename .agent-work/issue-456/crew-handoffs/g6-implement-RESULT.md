# Implementation Result

## Assigned gate
`g6` — Stale-tag detector (issue #456)

## Completed slice
Span-hash-based staleness detection for the authored layer, built end to end
against a fixture (the anchor mechanism), landing in the run report:

1. `extract.span_hash(node)` — a normalised AST hash of an entity's own
   subtree, immune to reformatting/comments/docstring-only edits by
   construction.
2. `Extractor.anchor()` persists `d.span_hash` on every `anchored` statement
   at extraction time.
3. `extract.run()` reads the PREVIOUS `statements.jsonl` (if present) before
   overwriting it, diffs old-vs-new span hashes by slug, and appends one
   `stale-anchor` statement per slug whose hash changed.
4. `render.py` intercepts `stale-anchor` explicitly in `load_stores()`,
   surfaces it as `report["stale_tags"]` in `render_report.json` (the run
   report the reviewer already reads — same artifact the duplicate-id check
   already uses), and prints an advisory `FAIL stale tag [...]` line naming
   the human action. It does **not** fail the build.

## Scope
**Files changed:**
- `scripts/code_map/extract.py` — `span_hash`, `Extractor.anchor_hashes`,
  `Extractor.anchor()` wiring, `run()`'s old-vs-new diff and `stale-anchor`
  emission, `extract_report.json`'s new `stale_tags` field.
- `scripts/code_map/render.py` — `stale_tags` module list, `load_stores()`
  interception, `run()`'s report field + printed FAIL lines + human-action
  comment.
- `tests/test_code_map.py` — `SpanHashUnitTests`, `StaleAnchorExtractionTests`,
  `StaleAnchorRenderReportTests` (16 new tests total, all containing
  `stale_tag` in their method name).

**Specific exclusions touched:** no. `is_test_module`, `SPLIT_LEGEND`,
`entity_symbol_join`, `page_location_matches_content`, the collision fixture,
the named MUTATION fixtures, page headers, and `thresholds.py` are all
untouched — confirmed by `git diff --stat` (three files only) and by the full
suite staying green (no other gate's tests moved).

## Behavior changed
Yes. `extract`/`build` now persist a span hash on every authored anchor and,
on a second run into the same `--artifacts` directory, flag any anchor whose
enclosing entity body changed while its slug did not. The flag is additive
and advisory: `render_report.json` gains one new key (`stale_tags`), stdout
gains one new printed-line shape when a flag fires, and the build's exit
code is unaffected by a stale tag alone (duplicate id remains the only
build-failing authored-layer defect).

## Decision resolved before designing (per the handoff's explicit requirement)

**What is a "tag" today?** There is no comment-tag vocabulary yet —
`Assumption:`/`Constraint:`/`Rationale:`/`Rejected:`/`See:` are gate `g7`'s
build (`gate-spec.json`: g7 depends on g2 **and g6**; g6 depends only on g3).
Verified directly: `grep -i "comment.tag\|Assumption:" scripts/code_map/`
returns nothing, and the real repo's own `render_report.json` shows `"ids":
0` — zero anchors exist anywhere in this corpus today (confirmed by
DESIGN_SPEC.md's own "Assumptions accepted untested" line: "zero anchor ids
exist"). The only authored-identity surface that exists pre-g7 is the
`[kebab-slug]` **anchor** (`extract.ANCHOR` / the `anchored` predicate). Per
DESIGN_SPEC §3, a real comment tag will be minted with the **same** `[slug]`
allocator ("a comment line holding nothing but the bracket, directly above
the def/class/assignment it names") — so hashing and diffing keyed on slug is
the correct hook point for g7 to wire real tag text into later: g7 needs only
to emit its own `Assumption:`/etc. statement anchored to the same slug: the
comparison, storage, and report-surfacing machinery built here does not
change.

**Consequence for "text did not change":** today an anchor carries no text
of its own besides the slug it was minted with. Matching old and new by
identical slug **is** the "tag text did not change" half of the gate's rule
— it's what makes two entries "the same tag" in the first place. Any hash
delta on a matched slug is exactly the flag this gate defines. This was
built and tested against a **fixture** (`_make_anchor_repo`/`_ANCHOR_SOURCE`,
extended from `IdsJsonlTests`'s own fixture), per the handoff's explicit
permission to do so, stated rather than silently worked around.

## What constitutes the "anchor body" (the gate's other named decision)

The entity's own AST subtree (the node `g3`'s `contains`/`d.end` already
spans), hashed via `ast.dump(node, annotate_fields=False)` with the leading
docstring statement excluded before dumping. `ast.dump` never encodes source
text, whitespace, or position (`include_attributes` defaults to `False`), so
the hash is immune to reindentation, line-wrapping, and blank-line changes
**by construction** — demonstrated in `SpanHashUnitTests` and, end to end, in
`StaleAnchorExtractionTests`/`StaleAnchorRenderReportTests`. The docstring is
excluded on the same reasoning the handoff itself suggests for comments:
prose describing behavior is not the behavior.

**Named blind spot (the honest cost, not hidden):**
- **Invisible by design:** anything confined to the docstring body, or to a
  comment anywhere inside the span. This is deliberate, not an oversight.
- **NOT immune to a bare local-variable rename inside the span** — a rename
  changes `Name.id` in the AST and trips the flag. This is stated as an
  accepted cost rather than a regression: a Constraint/Rationale's prose can
  name a specific variable, so treating a rename as a staleness candidate
  is defensible, at the cost of occasionally flagging a rename that has no
  bearing on the tag's actual claim. Narrowing this further (e.g.
  canonicalising local identifiers before hashing) is future work, not built
  here — flagged rather than silently promised.

## What a human does when this fires
One line, shipped in the printed message itself: open the tag named by the
flagged slug (`t['s']`), re-read its prose against the current code, and
update or remove it if it no longer holds. The flag is advisory, not a build
gate — printed alongside `render_report.json["stale_tags"]`, exit code
unaffected.

## Map Impact
- **Structural anchors touched:** `scripts/code_map/extract.py` —
  `span_hash`, `Extractor.anchor_hashes`, `Extractor.anchor()`, `run()`'s
  old-vs-new diff. `scripts/code_map/render.py` — `stale_tags`,
  `load_stores()`, `run()`'s report/print wiring.
- **Capabilities added:** authored-layer staleness detection (critics
  IF4/TS8) — first build of a design that was human-signed accepted-untested
  at confirm. Built against the anchor fixture; g7 wires the real tag-text
  surface into the same slug-keyed mechanism without rework.
- **Constraints touched:** "run report carries no timings" — honored
  (`stale_tags` is a plain list of ids, no timing field added; confirmed by
  a dedicated test scanning `render_report.json`'s own keys, and by
  `deterministic-rebuild` staying green — that check builds into two FRESH
  scratch `--artifacts` dirs each time, so `old_hashes` is always empty in
  both and this feature cannot perturb it).
- **Decision candidates / resolved decisions:** "what constitutes a tag's
  anchor body" — resolved as above (AST subtree, docstring excluded,
  rename-sensitive). "what is a tag today" — resolved as the `[slug]` anchor,
  not the (unbuilt) comment-tag vocabulary.
- **Trust limitations / drift found:** none beyond the named blind spot
  above. The real repo has zero anchors today (`ids: 0` in a fresh build's
  `render_report.json`), so this mechanism is fully untested against real
  authored tags until `g7` lands and f1Brainz's six real tags (PR #733) can
  exercise it — named as future validation, not claimed as done.
- **Triage candidates:** none raised beyond what the handoff already names
  (g7's dependency on this gate).

## Test mode
**Required:** test-first (TDD red→green, per the handoff and engine plan)
**Satisfied:** yes. Each of the three plan items (`m1-span-hash`,
`m2-persist-and-diff`, `m3-render-report`) was driven red→green through the
engine, attesting the red postcondition before implementing.

## Evidence

### Closing selector, before and after
```bash
python -m pytest tests/test_code_map.py -k 'stale_tag' -q --color=no
```
- **Before** (commit `5d8e9804` / current HEAD `3083a6e7`, verified directly:
  `git show HEAD:tests/test_code_map.py | grep -c stale_tag` → `0`): **0
  collected**, pytest exits **5** (no tests match `-k`), matching the
  handoff's stated baseline exactly.
- **After** this gate's changes: **12 collected, 12 passed, 11 subtests
  passed, exit 0.**

### Full suite
```bash
python -m pytest tests/ -q --color=no
```
Run in the background per doctrine; log at
`.agent-work/issue-456/g6-full-suite.log`.
**Result:** pass — **1805 passed, 2 skipped, 683 subtests passed, 0 failed,
exit 0** (463.57s). Baseline entering this gate was 1793 passed / 2 skipped /
672 subtests / 0 failed (commit `5d8e9804`); the delta is exactly the 12 new
`stale_tag` tests plus 11 new subtests (2 from the persisted-span-hash
`subTest(id=...)` loop, 9 from the no-timing-field key scan) — no other
gate's tests moved.

### Fresh build + check, real repo
```bash
python -m scripts.code_map build --root .
python -m scripts.code_map check --root .
```
**Result:** pass. `check` → **7/7 exit 0** (no-empty-pages, page-accounting,
refs-line-self-consistent, entity-symbol-join, page-location-matches-content,
inbound-attribution, deterministic-rebuild all `ok`). `render_report.json`
on the fresh build carries `"stale_tags": []` and `"ids": 0` (the real repo
has zero authored anchors today, so nothing is or could be flagged yet —
expected, not a gap).

### Reformatting-immunity demonstration
`StaleAnchorExtractionTests.test_stale_tag_does_not_flag_a_reformat_across_two_extractions`
and `StaleAnchorRenderReportTests.test_stale_tag_render_report_does_not_flag_a_reformat`:
add a blank line + a trailing comment to the anchored function's body between
two builds into the same `--artifacts` dir — no `stale-anchor` statement, no
`FAIL stale tag` line, empty `report["stale_tags"]`.

`StaleAnchorExtractionTests.test_stale_tag_flags_a_real_body_change_across_two_extractions`
and `StaleAnchorRenderReportTests.test_stale_tag_render_report_flags_a_real_body_change`:
change `return WIDTH` to `return WIDTH * 2` between the same two builds —
`widget-spin` appears in the `stale-anchor` statements, in
`report["stale_tags"]`, and in stdout; the OTHER anchor in the same file
(`holder-hold`) is confirmed silent
(`test_stale_tag_does_not_flag_an_unrelated_anchor`).

## TDD evidence
- Failing test observed (Grade B — red by absence of the feature, not a
  pre-existing bug): `m1-span-hash` — 3/3 `AttributeError: module
  'scripts.code_map.extract' has no attribute 'span_hash'`. `m2-persist-and-diff`
  — 3/10 failing (span_hash not persisted, staleness not flagged);
  the 7 "does-not-flag" assertions passed vacuously (nothing implemented
  yet), which is the correct/expected shape for a not-yet-wired absence.
  `m3-render-report` — 3/3 failing (`report.get("stale_tags")` was `None`).
- Passing test observed: all three green after implementation (`stale_tag`
  selector: 8/8 after m2, 12/12 after m3).
- Refactor while green: no separate refactor pass was needed; each slice
  landed at its final shape on the first green.

## Docs/contracts touched
- None outside the code + tests listed above. `DESIGN_SPEC.md` and
  `gate-spec.json` are reference material, not owned by this gate — not
  edited.

## Assumptions
- The run report the reviewer reads is `render_report.json`, not
  `extract_report.json` — resolved from the existing duplicate-id
  precedent already living in `render.py`, not assumed from scratch (see
  "Decision resolved" above).
- A stale tag is advisory, not build-failing — an explicit design call
  (see "Behavior changed"), not asserted by any prior ruling; stated plainly
  so it can be overruled if the reviewer disagrees.

## Stop conditions hit
None.

## Out-of-scope observations
- The real repo has zero authored `[slug]` anchors, so this mechanism has
  never been exercised against real staleness — only against the fixture.
  f1Brainz's six real tags (PR #733, currently READ-ONLY for this run) are
  the natural first real-world validation once `g7` lands; flagged as future
  work, not built here.
- `extract_report.json` also gained a `stale_tags` field (list of slugs) as
  a secondary/debug surface, in addition to `render_report.json`. Not the
  primary "run report" channel per the resolved decision above, but free to
  keep since it comes from the same computation.

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff's own instruction to
  resolve "what is a tag" before designing was exactly the right call —
  gate-spec.json's g7-depends-on-g6 line made the answer unambiguous once
  looked for, but a first read of the g6 task text alone ("hash each tag's
  enclosing entity span") could mislead an implementer into assuming a tag
  surface that isn't built yet.
- **Context rediscovered:** which JSON file is "the run report the reviewer
  already reads" is not stated anywhere explicitly — I resolved it by
  finding the existing duplicate-id precedent in `render.py` and matching
  it. A one-line pointer in a future handoff ("the run report = X") would
  save this lookup.
- **Instructions improvised around:** none — the plan's TDD shape (red via
  manual attest, green via command check) fit cleanly across all three
  code-producing items.
- **What would have made this easier:** the context governor's HARD band
  fired at `m0-context` before any real work had happened (~19-22% fill from
  upfront reading alone). Attaching a `refresh-request` at every single
  `advance` call (not just when genuinely stuck) added five extra engine
  round-trips across this run's five gates. If the intent is genuinely "flag
  once per seam," a HARD trip that fires on the very first gate before any
  code exists suggests the threshold or the upfront-reading cost is worth
  revisiting — flagged as observation, not a blocker (I complied at every
  occurrence).

## Return status
`complete`
