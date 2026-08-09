# Review Result

## Assigned Gate
`g6` — stale-tag detector (issue #456)

## Result
`BLOCK`

## Handoff compliance
The change does what the handoff asked (span-hash-based staleness detection, surfaced advisory in
`render_report.json`), within allowed scope (exactly `scripts/code_map/extract.py`,
`scripts/code_map/render.py`, `tests/test_code_map.py`). It BLOCKS on the handoff's own
pre-declared sharpest question: whether the shipped negative ("does not flag") tests have teeth.
Ran the exact attack the handoff prescribed — disabled flag emission on one code path in
`extract.run()` (forced `stale = []` after the real computation) and reran the closing selector.
9 of 12 tests stayed green, including **every** dedicated "does not flag" test
(`test_stale_tag_first_extraction_flags_nothing`,
`test_stale_tag_does_not_flag_a_reformat_across_two_extractions`,
`test_stale_tag_does_not_flag_an_unrelated_anchor`,
`test_stale_tag_render_report_does_not_flag_a_reformat`,
`test_stale_tag_render_report_does_not_fail_the_build`). Only 3 went red — the two "flags a real
change" tests, plus one that failed incidentally via its own precondition assertion. Reverted the
mutation immediately after; `git status --porcelain -- scripts/code_map/extract.py` clean, selector
back to 12/12. This is exactly the handoff's own threshold: "if most of the negatives stay green...
that is a BLOCK-worthy finding even though the feature works" — and it is the same defect class as
this run's tc38/tc47. The feature itself genuinely works (independently confirmed under attack —
see Evidence verdict); most of its own regression evidence cannot fail, so a future regression that
silently disables the whole detector would ship green.

The other three named questions: **Q1** (does slug-match beg the question?) is a correctly-deferred
`g7` concern, not a defect now — confirmed zero comment-tag vocabulary exists pre-`g7` and zero
anchors exist in this corpus today. **Q2** (advisory-only + `FAIL` text) — severity ruling
(advisory-only) stands, but the text collision is real and confirmed: the advisory line and
`checks.py`'s real check failures both print the identical `FAIL ` prefix, and a single `build`
invocation's stdout can legally contain both a build-failing and an advisory-only `FAIL` line,
distinguishable only by exit code. **Q3** (novel-mutation reformatting-immunity attack) — 8 novel
mutations the crew did not choose, all predictions matched exactly, no accidental behavior found,
no new defect.

## Scope drift
Clean. `git show --name-only` on `55b95314` shows only workbench bookkeeping plus exactly the three
named files. All specific exclusions (`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`,
`page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers,
`thresholds.py`) independently re-verified untouched by direct diff grep — zero hits. No new
imports.

## Evidence verdict
Reproducible evidence reproduced exactly, independently: full suite **1805 passed, 2 skipped, 683
subtests passed, 0 failed, exit 0** (384.94s, backgrounded to completion) — exact match. Fresh
`build` then `check` into a scratch `--artifacts`/`--out` pair — **7/7 exit 0**, `deterministic-rebuild`
included, `render_report.json` carries `stale_tags: []` and `ids: 0` — matches the claim. Closing
selector `-k 'stale_tag'`: **12 collected, 12 passed, exit 0** — exact match.

The capability the evidence demonstrates is real (confirmed independently under two separate
attacks this review — Q3's 8 novel mutations, and the "flags a real change" tests surviving the
Q4 disablement attack). What does NOT hold up is the evidence's own claim that the negative tests
prove correct discrimination — most do not, per the Q4 finding above; see the full attack and
counts under `r1-handoff`/`r3-evidence` in the survey.

Also confirmed independently rather than accepted: `deterministic-rebuild` structurally cannot
exercise the staleness path (two fresh scratch dirs on every call — read `checks.py`'s
`_build_into`/`deterministic_rebuild` directly). Further: `check` never exercises the staleness
path either, since it never calls `render.py` at all — this mechanism's only routine exerciser
today is a human/agent not wiping `.code-map` between local `build` runs, an unenforced convention.
Read-before-overwrite robustness: reproduced a genuine, previously-unreported crash — a
truncated/malformed leftover `statements.jsonl` (simulating an interrupted prior run, a real
scenario since the writer has no atomic rename) makes every subsequent `extract` fail with an
uncaught `JSONDecodeError` and a bare traceback naming no actionable next step. This is a new
failure mode this gate introduces; before it, a corrupted leftover store was harmless. Filed as
`tc1`. Count discrepancy: IMPLEMENTER_RESULT's Scope section says "16 new tests total"; the
Evidence section and my own independent count (`StaleAnchorExtractionTests` 5 +
`StaleAnchorRenderReportTests` 4 + `SpanHashUnitTests` 3 = 12) both say 12. **12 is right** —
nothing was dropped between writing and shipping, this is a drafting error confined to the RESULT
document. `extract_report.json`'s secondary `stale_tags` field: harmless duplication on the
blessed `build` path (both reports derive from the same `stale` list within one process); a latent,
pre-existing (not `g6`-specific) drift risk only if `extract`/`render` are invoked as
independently-timed CLI stages.

## Code/doc quality
Fowler pass: 12/12 rendered a verdict (`.agent-work/issue-456/g6-review/fowler-pass.json`, rail
exit 0). Two flagged, both non-blocking: **long-method** on `extract.py`'s `run()`, which grew
from ~54 to ~86 lines, bundling a third concern (read-old-hashes, then diff-and-emit) onto its
existing extraction/report-writing responsibilities — still cohesive, worth a future split if a
fourth concern lands. **data-clumps** on the new `anchor_hashes[slug] = (sym, hash, file, line,
col)` bare 5-tuple, documented only in a comment — low realistic risk, but a small `NamedTuple`
would remove the silent-field-reorder risk. Ten smells absent, zero overridden. Comments and
docstrings throughout explain design decisions and their reasoning rather than restating the
obvious.

## Map impact verdict
- **Evidence supports claimed change:** yes for the capability itself (independently verified
  under attack); no for the negative-test evidence specifically (Q4 finding).
- **Constraints not violated:** yes — no-timings constraint independently verified as a dynamic
  key-scan, not a fixed list; full suite green; page headers untouched.
- **Notes match the diff:** yes — structural anchors, capabilities, constraints, and decision
  candidates named in Map Impact all match what the diff actually touches, confirmed by direct
  read.
- **Decision candidates surfaced:** yes, and one is re-opened per the handoff's own invitation:
  the crew's overrule of the Commander's original "a bare rename should not trip the flag" position
  is examined independently (not merely restated as settled) and **affirmed** — Q3's findings show
  "over-flag, never under-flag" is the mechanism's consistent, deliberate posture throughout, not a
  one-off carve-out for renames.
- **Durable context routed:** yes — two triage candidates filed through the engine (`tc1`:
  read-before-overwrite crash; `tc2`: FAIL-text collision), both cheap, should ride the same rework
  pass as the Q4 fix.

## Reconciliation check
No architecture doc outside the generated `map/` tree exists in this repo to reconcile against —
consistent with prior gates' reviewers' same finding. No structural divergence beyond what is
already recorded above.

## Blockers
- **Q4 — most shipped "does not flag" tests are vacuous under a whole-feature-disable attack.**
  Reproduced directly: disabling flag emission on one code path in `extract.run()` leaves 9/12
  tests green, including every dedicated "does not flag" test. Fix shape: give each "does not
  flag" test its own positive control in the same test method (assert a known-should-flag mutation
  DOES flag, in the same method that asserts the target case does not), so a full-disable
  regression cannot leave it green.

## Out-of-scope observations
- `tc1`: read-before-overwrite crash on a malformed/truncated leftover `statements.jsonl` —
  uncaught `JSONDecodeError`, no actionable message, a new failure mode this gate introduces.
- `tc2`: the advisory stale-tag line's literal `FAIL ` prefix collides with `checks.py`'s and
  `render.py`'s own build-failing `FAIL ` convention — a single `build` invocation's stdout can
  contain both, distinguishable only by exit code. One-line fix (e.g. `ADVISORY stale tag [...]`).
- The "gb's ruling" code comment citation is looser than it reads: `gb`'s own gate scope is the
  four ratio-based thresholds, not a literal ruling about build-failing-vs-advisory severity for
  this class of check. The underlying reasoning is sound and consistent with `gb`'s documented
  ratio-over-count philosophy; only the citation's precision is worth tightening.

## Workflow Feedback

- **Handoff gaps:** none of substance. The four named questions were exactly the review's real
  work, as advertised — Q4 in particular was concrete enough to execute verbatim (the "disable one
  code path, rerun the selector" instruction translated directly into a 10-minute, unambiguous
  attack with a clear pass/fail line).
- **Context rediscovered:** the exact call graph proving `check` never reaches `render.py` (so the
  `FAIL` collision is confined to `build`'s own stdout, never literally interleaved with `check`'s
  own `FAIL {name}: {count}` lines in one command) took a `cli.py` read the handoff did not point
  to directly — worth a one-line pointer ("`check` = `checks.run()`, never touches `render.py`") in
  a future handoff for this same subsystem, since the "Also verify" section's `deterministic-rebuild`
  bullet already gestures at the `build`/`check` split without stating it explicitly.
- **Instructions improvised around:** this worktree's compound-Bash restriction (no `$(...)`, no
  heredocs, no long quoted strings) made the engine's plain `--finding "<text>"` CLI argument
  impractical for multi-paragraph findings (this review's findings ran several KB each). Worked
  around it by writing the finding to a scratch file and calling `checklist_engine.main([...])`
  directly from a tiny Python wrapper script (a list of argv strings, no shell quoting involved) —
  functionally identical to the CLI path, same engine, same provenance, just invoked in-process.
  This worked cleanly but is not documented anywhere as the sanctioned route for a long finding
  under this constraint.
- **What would have made this easier:** a `--finding-file <path>` (or `--payload-file`, matching
  the pattern `attach` already offers) option on `record` would remove the need for the
  wrapper-script workaround above and make long survey findings straightforward under worktree
  isolation's compound-Bash restriction — this will recur for any reviewer whose findings are long
  enough to need real evidence, which is most of them.

## Return status
`complete`
