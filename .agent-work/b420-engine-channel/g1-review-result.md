# Review Result

## Assigned Gate
`g1-review` (issue #420, epic #418 workstream B)

## Result
`APPROVE`

## Handoff compliance
All three deliverables verified independently, not trusted from the pasted evidence:

1. **RAIL echo de-dup, `current` verb only.** Built my own mid-flight fixture (g1 complete, g2
   in-progress, g3 pending) and ran the real CLI (`python scripts/checklist_engine.py ... current`,
   `--dry-run`): `do g2` appears exactly once (on the `ACTIVE` line; the RAIL substitutes "the
   ACTIVE line above"). Verified directly via `E._rail(verb, cl)` for `start`, `advance`, `attest`,
   `claim`, `attach` on the same fixture — all five keep the full, unabridged `do g2` imperative,
   unchanged, exactly once each.
2. **`anchors`/`constraints` rendering.** Built a fixture with `anchors: {"inherits": "<verbatim
   text>"}` — the exact shape and verbatim text of `skills/commander/templates/
   EXECUTE_PLAN.template.json` line 41 (confirmed by reading that file directly) — and drove it
   through `current()`: it rendered as **one** readable line (`  inherits: g1-implement anchors —
   …`), not one line per character. Also confirmed absent/empty `anchors`/`constraints` produce
   byte-identical `current()` output between the pre- and post-change engine modules (ran both on
   an identical fixture, diffed: `IDENTICAL: True`).
3. **`TaskFieldCompleteness` property test.** Read the 13-entry `_EXCLUDED_FIELDS` set
   (`tests/test_checklist_engine.py:4001`) — every entry carries a specific, individual reason
   (identity/control-flow, structured-fields-checked-elsewhere, bookkeeping, survey-only field, or
   `directives` explicitly named as an out-of-scope known gap). The enumeration is real: it also
   asserts `imperative` content through the same flatten path, so it is not hardcoded to
   `anchors`/`constraints` by name, and it carries a `checked_any` anti-vacuity assertion.

Stop conditions: none hit. No decision outside my authority was required.

## Scope drift
Only `scripts/checklist_engine.py` and `tests/test_checklist_engine.py` changed
(`git status --porcelain`, confirmed independently). Full diff read line-by-line: touches only
`_rail()`/the mid-flight token substitution, `state()`'s per-task dict (+`constraints`/+`anchors`
pure passthrough), `render_human()` (+2 new small helpers, +constraints/anchors rendering, +a
docstring fix), plus the corresponding new tests. `git diff scripts/checklist_engine.py | grep -c
_check_condition` = 0 (D's #422 fence intact). `tests/test_spine_rail.py` has zero diff lines and
its 10 pre-existing `_rail`/`RAIL_STRINGS` references are a distinct Stop-hook nudge-state concept,
unrelated to `checklist_engine.py`'s `_rail_position`/`_RAIL_STRINGS` — confirmed by inspection.
No mention of DIGEST-staleness, workstream C's relocation, or RAIL-echo compliance-neutrality
anywhere in the diff (grep, 0 hits) — all four specific exclusions genuinely untouched.

## Evidence verdict
Required evidence present and independently reproduced, not copy-pasted:

- **Test counts.** Pre-change baseline (via `git stash` of the two changed files, my own run):
  `388 passed, 24 subtests passed`. Post-change (my own run): `397 passed, 24 subtests passed`.
  Net +9, 0 regressions — matches the claimed count exactly.
- **RED genuinely preceded GREEN.** Swapped `scripts/checklist_engine.py` back to
  `git show HEAD` while keeping the post-change test file, ran the relevant test classes: 7 failed
  / 12 passed, same failing test names/reasons the implementer's pasted RED evidence cites
  (`DoctrineRail` x2, `RenderAnchorsAndConstraints` x4 including the plain-string-dict regression
  test, `TaskFieldCompleteness` x1). Restored the post-change file afterward; `git diff --stat`
  confirmed unchanged (76/244 insertions).
- **`_RAIL_STRINGS` byte-identity.** Extracted the dict literal via `ast.literal_eval` from both
  the pre-change (`git show HEAD`) and post-change source and compared in Python:
  `EQUAL: True` — not eyeballed.
- **TDD evidence** shows red-green-refactor for both slices plus the disclosed rework 1/3, each
  driven through the implementer's own engine plan with attested RED runs before fix code.

Test mode (TDD) satisfied.

## Code/doc quality
Minimal, maintainable change matching the file's existing conventions (naming, docstring density,
issue-number citations). `state()`'s new reads are literal `dict.get()` passthroughs — no side
effect, no check re-run, honoring INV-2 (purity) from `docs/CHECKLIST_ENGINE_DESIGN.md`. Docstring
citation fix verified on both ends: `grep -n "class GoldenOutputBriefing"` → line 3779, matching
the new docstring's "~3779 on"; `git show HEAD:tests/test_checklist_engine.py` lines 815–820
confirm the old citation (line 818) was indeed an unrelated `E.require_session(...)` lease-test
line, exactly as claimed.

A Fowler refactoring pass was run per `r6-fowler` (see `.agent-work/b420-engine-channel/g1-review/
fowler-pass.json`, `scripts/verify_fowler_pass.py` exits 0). 11 of 12 baseline smells are absent.
One non-blocking **duplicated-code** observation: `render_human()` already generalized the
pre/postconditions rendering into a single loop specifically to avoid repeating the "if populated:
append label; extend indented lines" shape (its own inline comment: "rework 1, non-blocking Fowler
note"). The new `constraints` block and the new `anchors` block each re-introduce that exact shape
as two more separate `if` statements immediately below the already-generalized loop, instead of
folding into the same iteration. Five lines, correctness unaffected — worth folding in on the next
touch to this function, not worth blocking on now.

## Map impact verdict
- **Evidence supports claimed change:** yes — verified above, independently.
- **Constraints not violated:** yes — `_RAIL_STRINGS` byte-identity and `state()` purity (INV-2)
  both independently confirmed.
- **Notes match the diff:** yes — the claimed structural anchors (`_rail()`, `state()`,
  `render_human()`) are exactly what the diff touches; no missing or overstated impact.
- **Decision candidates surfaced:** n/a — none needed; the handoff's given decisions
  (vestigial-fields, verb-aware-dedup shape) were followed as given, not reopened.
- **Durable context routed:** yes — flagged the implementer's two out-of-scope observations as
  triage candidates (`tc1`, `tc2`) in the review survey rather than letting them sit only in prose:
  (1) `directives` is in the same unrendered-defect class as anchors/constraints, out of #420's
  authorized scope; (2) `anchors` is still absent from `docs/CHECKLIST_SCHEMA.md`'s Task field
  table (confirmed independently: `grep anchors docs/CHECKLIST_SCHEMA.md` — 0 hits).

## Reconciliation check
No divergence from recorded architecture that Commander must reconcile beyond routing the two
triage candidates above at cleanup.

## Blockers
- none

## Out-of-scope observations
- (Fowler, non-blocking) `render_human()`'s new `constraints`/`anchors` blocks could fold into the
  already-generalized pre/postconditions loop instead of repeating the label+lines shape as two
  more `if` statements — see Code/doc quality above.
- (carried from implementer, independently re-flagged as triage candidates `tc1`/`tc2` in the
  survey) `directives` rendering follow-up; `anchors` missing from `docs/CHECKLIST_SCHEMA.md`'s
  Task field table.

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff was unusually thorough — it named the exact
  load-bearing shape to reproduce (`EXECUTE_PLAN.template.json` line 41) and gave a byte-identity
  check for `_RAIL_STRINGS` rather than leaving "verify unchanged" vague.
- **Context rediscovered:** none beyond what the handoff and implementer's result already named —
  the anchors corpus shapes were fully documented in the implementer's Assumptions section, so I
  didn't need to re-derive them from scratch, only reproduce them.
- **Instructions improvised around:** the skill's `r4-quality` imperative says "append a check per
  rule"; the handoff's Constraints section held exactly three checkable rules (RED-preceded-fix,
  `_check_condition` untouched, docstring citation), so I appended three siblings (`r4a`/`r4b`/`r4c`)
  under `r4-quality` and recorded an umbrella pass — matches the `checklist-engine.md` pattern for
  grouping per-criterion checks, worked cleanly.
- **What would have made this easier:** none — the handoff's Verification Commands section and the
  implementer's Load-bearing samples section together made every independent-reproduction step
  a direct, mechanical translation rather than a search.

## Return status
`complete`
