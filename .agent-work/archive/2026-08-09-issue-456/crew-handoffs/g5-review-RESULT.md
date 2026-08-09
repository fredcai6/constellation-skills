# Review Result

## Assigned Gate
`g5` — unused vs untested must stop looking identical. Issue #456.

## Result
`BLOCK`

## Lead: rulings on Findings A and B

**FINDING A — CONFIRMED, BLOCKING.** `SPLIT_LEGEND`, printed on every one of 3864 built pages,
claims the split is based on "a top-level tests package." Reproduced directly, not from the diff
alone: `is_test_module("scripts.tests.helpers")` and `is_test_module("pkg.sub.tests.foo")` both
return `True` in **both** copies (`render.py`, `checks.py`) even though neither module has
`tests` as its first dotted segment. The page's stated basis is wrong. This sits squarely on the
gate's own close criterion, judged verbatim — "the predicate is derived from a published
convention... and the page says what it was based on" — and is the exact defect class this whole
run exists to close: a stated rule that does not match the applied rule, on the single sentence
explaining the gate's central mechanism, repeated on every page. Confirmed no check pins the
legend text to the real predicate the way `RefsAccountingTests.
test_the_legend_names_the_predicates_the_count_actually_counts` already pins `REFS_LEGEND` to
`load_stores`'s real predicate set — grepped `tests/test_code_map.py` for `SPLIT_LEGEND`/
`top-level`; the only hits are the legend's own definition and an assertion it merely *appears*
on a page. Fix: either narrow the predicate to top-level-only, or reword the legend to drop
"top-level" — either way, add a pinning regression check afterward (filed as `tc1`).

**FINDING B — CONFIRMED as a real conflation; does NOT escape into anything shipped.**
Reproduced `measure_split.py`'s exact headline numbers on a fresh build (unused 2428/64.7%,
test-only 451/12.0%, production 873/23.3% of 3752 entity pages — byte-for-byte match). Wrote an
independent re-measurement adding the one dimension the script omits (whether the entity's own
module is itself a test module) — exact match to the Commander's numbers:

| bucket | prod-defined | test-defined |
|---|---|---|
| unused | **88** | **2340** |
| test-only | **2** | 449 |
| production | 873 | 0 |

2340/2428 (96.4%) of "unused" is test-defined; genuinely unused production code is **88**, a 27x
difference from the headline. Separately verified `TEST_NOTE` appears on exactly 2789
test-defined pages and 0 production-defined pages — the per-page mechanism is right. Checked
whether the conflation escapes into anything shipped: read `top_index`/`module_index` in full and
grepped `scripts/` for `unused`/`test_only` — zero hits outside the split-grammar constants and
`measure_split.py` itself. **The gate's actual shipped capability is sound and independently
verified working under attack; the defect is confined to the evidence layer** — this gate's own
`measure_split.py` script and the `IMPLEMENTER_RESULT` headline claim reproduce the exact
conflation the gate exists to remove. Does not block the shipped behavior by itself (Finding A
already blocks), but the headline must not propagate uncorrected — filed as `tc2`.

## Also verified — all four hold up

- **tc32** attacked with mutations the implementer did not choose (their probe only deletes
  `sorted(...)`): reverse-sort (diff correctly EMPTY — still visit-order-independent),
  call-count-with-tied-counts (diff NON-EMPTY — ties leak visit order through Python's stable
  sort), reversed-insertion (diff NON-EMPTY). All three matched a-priori expectations exactly.
  Also confirmed **both** bucket lines order deterministically, not just production — built a
  second fixture where the TEST bucket is the one with 2 external callers and reran the attack;
  same result. **tc32 genuinely closed.**
- **Independence of the two `is_test_module` copies**, attacked for real: diverged only
  `checks.py`'s copy (confirmed `render.py`'s copy in the same mutated host stayed untouched),
  built a fixture exercising the divergence, and `check` went red on **two** separate checks
  (`inbound_attribution`, `refs_line_self_consistent`). The second copy is load-bearing, not
  decoration — not a tc29/tc38 finding.
- **Retargeted mutation anchors** (`OWN_MODULE_NAMED_MUTATION`, `LEGEND_DROPPED_MUTATION`): ran
  directly, isolated — 3 passed. Each test's own harness independently proves its anchor is
  unique in the source and that the mutation actually flips `check`'s exit code with the exact
  message asserted.
- Confirmed above (test-bucket order fixture).

## Handoff compliance
Change matches the handoff: `is_test_module`, `_bucket_line`, rewritten `refs_line` in
`render.py`; independent second copies + rewritten `refs_line_self_consistent`/
`inbound_attribution` in `checks.py`; new tests + retargeted anchors in `tests/test_code_map.py`;
new `measure_split.py`. Both Commander findings confirmed by independently running them, not
taken on trust — full detail above and in `.agent-work/issue-456/g5-review/review.json`.

## Scope drift
None. `git diff --name-only 5e5e2794..1f5c8a6e` (my own run): exactly
`scripts/code_map/checks.py`, `scripts/code_map/render.py`, `tests/test_code_map.py`, plus
workbench artifacts. All named exclusions re-verified directly: `_make_collision_repo`'s INDEX
collision still fires (4 tests green); `entity_symbol_join` untouched by the diff (grepped —
zero hits); `page_location_matches_content` untouched (only appears as a hunk's preceding-context
marker); page headers zero `:<line>` across all 3864 pages. Additional scan: 386 pages are
non-ASCII, but every one traces to pre-existing docstring prose elsewhere in the repo (an em-dash
in `scripts/agent_work_root.py`'s docstring) — g5's own new strings are all confirmed pure ASCII;
out of scope for this gate, not a blocker.

## Evidence verdict
Full suite (backgrounded to completion, not truncated): **1780 passed, 2 skipped, 672 subtests,
exit 0**, 310.01s — exact match to `IMPLEMENTER_RESULT`. Fresh build: **111/3752/3864** — exact
match. Fresh `check`: **7/7** — exact match. Gate selector `-k 'refs or caller'`: **19 passed** —
exact match. `measure_split.py`'s headline numbers reproduced byte-for-byte. But the headline
number itself does not demonstrate what its own English ("unused") denotes — see Finding B; this
is a required-evidence defect (`r3-evidence` recorded fail) even though the shipped page-level
behavior is sound.

## Code/doc quality
Fowler pass: 12/12 rendered, rail exit 0 (`.agent-work/issue-456/g5-review/fowler-pass.json`).
One **flagged** (non-blocking): `refs_line_self_consistent` grew to bundle 4 concerns (~67 lines
of code) — worth a future split, not blocking. One **overridden** with a logged reason:
duplicated-code on the byte-identical constants/`is_test_module` declared independently in both
files — `checks.py`'s own established convention ("a check that reads its expected text out of
the code under test can only ever agree with it"), earned this review by the independence attack
above (mutating one copy alone made two checks go red). All other 10 smells absent.

## Map impact verdict
- **Evidence supports claimed change:** yes for the per-page capability (independently verified
  under attack); no for the headline aggregate (Finding B).
- **Constraints not violated:** the classification-predicate constraint IS violated in the sense
  Finding A names — the page's own stated basis does not match the code.
- **Notes match the diff:** structural anchors match exactly. The "Claims/evidence produced"
  bullet overstates what the headline number shows (Finding B). The "Trust limitations" bullet
  understates Finding A — the Assumptions section honestly discloses the nested-vs-top-level
  design choice but never connects it to the fact that the page's own printed legend contradicts
  that choice.
- **Decision candidates surfaced:** yes — no absolute-count threshold introduced (re-confirmed
  independently from the diff's added lines).
- **Durable context routed:** yes — `tc1`, `tc2` filed via `flag-candidate --from
  r5-reconciliation`.

BLOCK per this section's own rule: graph-impact claims materially wrong for architecture-
significant work (Finding A misstates the classification basis on every page).

## Reconciliation check
No `docs/architecture/` exists in this repo to reconcile against — consistent with prior gates'
reviewers' same finding. No architecture-level divergence beyond the two findings already ruled
above.

## Blockers
- **Finding A**: `SPLIT_LEGEND` states "a top-level tests package"; `is_test_module` matches
  `tests` anywhere on the dotted path. Fix the legend or the predicate, and add a pinning check.

## Out-of-scope observations
- `tc1`: add a regression check pinning `SPLIT_LEGEND`'s stated basis to `is_test_module`'s real
  predicate once Finding A is fixed (parallel to the existing `REFS_LEGEND` precedent).
- `tc2`: fix `measure_split.py` to add the definer dimension (or caveat the headline) before the
  2428/64.7% number propagates beyond this gate's own closeout. Ready template:
  `.agent-work/issue-456/evidence/g5_reviewer_split_by_definer.py`.
- 386 pre-existing non-ASCII pages (em-dash in `scripts/agent_work_root.py`'s docstring), out of
  this gate's scope — carried forward, not re-litigated by this review.

## Workflow Feedback

- **Handoff gaps:** none material. The handoff's framing (name two findings, direct me to
  confirm/refute by running them, explicitly invite overruling) was unusually well-specified —
  it told me exactly what evidence shape would settle each question rather than leaving me to
  invent the investigation from scratch.
- **Context rediscovered:** none beyond the ordinary read of the diff and prior gates' review
  precedent (the `REFS_LEGEND`-pinning test as the missing-parallel for `SPLIT_LEGEND`; the
  duplicated-code override precedent from g3/g4). Both were findable directly in
  `tests/test_code_map.py` without needing anything the handoff should have carried separately.
- **Instructions improvised around:** the `r6-fowler` postcondition's `<fowler-pass-record-path>`
  placeholder — filled the real path directly into the survey JSON at creation time rather than
  leaving the raw template placeholder for `record` to trip over (same choice g4's reviewer
  reported and recommended promoting into the template itself; still not done).
- **What would have made this easier:** nothing further. The wrapper scripts
  (`run_record.py`/`run_flag_candidate.py`/`run_consolidate.py`) worked exactly as documented for
  every long-finding-text call this review made.

## Return status
`complete`
