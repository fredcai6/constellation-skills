# Review Result

## Assigned Gate
`g1-review` (execute.json, work-id `b433-render-directives`, issue #433)

## Result
`APPROVE`

Survey driven end to end through the engine: `.agent-work/b433-render-directives/g1-review/review.json`,
17 items, all `pass`, consolidated `verdict=APPROVE findings=0`. Nothing committed. Working tree left
exactly as found.

I drove the survey through the **installed** engine copy
(`C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/checklist_engine.py`), not the repo's
vendored one, because the repo's vendored engine is the file under review and this gate required me to
revert it mid-run. See Workflow Feedback.

---

## Close criteria — one finding each, with how I verified it

### 1. The golden was captured RED before the change — PASS (reproduced, not accepted)

This is the criterion the gate exists for, so I reproduced it rather than reading the capture.

I copied `scripts/checklist_engine.py` to a backup **outside the repo** (so no stray untracked file
appeared in the worktree), then reverted only that file:

```
$ git checkout -- scripts/checklist_engine.py
$ git diff --quiet scripts/checklist_engine.py && echo "ASSERT-OK: ... is UNCHANGED vs HEAD"
ASSERT-OK: scripts/checklist_engine.py is UNCHANGED vs HEAD
$ grep -c "_render_directive_lines" scripts/checklist_engine.py
0
ASSERT-OK: 0 occurrences of _render_directive_lines (mutation really applied)
$ grep -c "class RenderDirectives" tests/test_checklist_engine.py
1
```

Two independent assertions that the revert applied, because a mutation that silently does not apply
leaves a green run reading exactly like a passing guard (`CREW_CONTEXT.md`, Verification Discipline).
The test file stayed modified.

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k RenderDirectives; echo "EXIT=$?"
.FFFFF.                                                              [100%]
...
E       KeyError: 'directives'
tests\test_checklist_engine.py:4108: KeyError
=========================== short test summary info ===========================
FAILED tests/test_checklist_engine.py::RenderDirectives::test_directives_render_after_anchors_and_before_next
FAILED tests/test_checklist_engine.py::RenderDirectives::test_flat_list_of_strings_shape_renders_one_line_each
FAILED tests/test_checklist_engine.py::RenderDirectives::test_nested_contract_dict_shape_renders_indented_leaves
FAILED tests/test_checklist_engine.py::RenderDirectives::test_shipped_commander_spine_execute_gate_renders_its_directives
FAILED tests/test_checklist_engine.py::RenderDirectives::test_state_passes_directives_through_without_re_running_checks
5 failed, 2 passed, 339 deselected, 4 subtests passed in 1.15s
EXIT=1
```

Identical counts to the implementer's claim. The failures are substantive, not collection errors:
`state()` raised `KeyError: 'directives'`, and the shipped-spine `assertIn` failure printed the real
pre-change `current` for the shipped `COMMANDER_SPINE` `execute` gate, showing the `replan_input`
contract genuinely absent from what the agent reads.

Restored from the backup and asserted the restoration:

```
$ md5sum scripts/checklist_engine.py
a4d1a78d110bd531daf08811f1a69e78 *scripts/checklist_engine.py   # == pre-revert
$ diff "$BK" scripts/checklist_engine.py && echo "ASSERT-OK: byte-identical"
ASSERT-OK: restored file is byte-identical to the pre-revert working tree
```

### 2. First line of `current` is byte-identical — PASS

Verified empirically, not by reading the diff. I loaded `git show HEAD:scripts/checklist_engine.py`
as a second module alongside the changed one and rendered `current()` under both on the shipped
`COMMANDER_SPINE` `execute` gate:

```
FIRST LINE byte-identical: True
removed-from-old lines: []

=== unified diff of the WHOLE `current` output: HEAD engine -> CHANGED engine ===
@@ -8,2 +8,10 @@
 0/4 met
+directives:
+  replan_input:
+    template: ../constellation-replan/templates/REPLAN_INPUT.template.json
+    output: .agent-work/<work-id>/REPLAN_INPUT.json
+    evidence_fields: completed_outcomes, wave_evidence, discrepancies
+    classifications: blocks_current_wave_exit, invalidates_forecast_or_decomposition, later_only, evidence_only, drop
+    auto_file_discrepancies: false
+    check: verify_iterative_role_artifacts.py commander
 next: attest execute --cond p1 --which preconditions
```

Purely additive: 8 lines added, zero changed, zero removed. I then extended this corpus-wide:

```
checklist FILES scanned: 370
GATES rendered under both engines: 2981
gates with a POPULATED `directives` field: 8
gates whose `current` output CHANGED: 8
gates whose FIRST LINE changed: 0  <-- must be 0
```

The 8 changed gates are exactly the 8 populated ones (`COMMANDER_SPINE`/`ADMIRAL_SPINE` `execute`,
`EXPLORER_SPINE` `confirm`, this run's own `spine.json`, `epic-418-redux`, and three archived
installed-layout copies). No collateral change anywhere else.

`GoldenOutputBriefing`, `ShippedTemplates` and `TaskFieldCompleteness` are each **byte-identical to
HEAD** — I extracted both versions of each class and compared the strings. Green:
`10 passed, 336 deselected, 20 subtests passed`.

### 3. Absent and empty `directives` add zero output — PASS (guard-proven)

The tests exist: `test_absent_or_empty_directives_add_no_output` covers `None`, `{}`, `[]`, `""` via
`subTest` plus `del t["directives"]` for a key absent entirely, and
`test_unrecognized_directives_shape_renders_nothing` covers a scalar.

Existence alone proves nothing here — both tests pass **pre-change too** (they were the 2 passed in
the RED run). So I removed the guard. Byte-level mutation, because the working tree is CRLF and a
naive LF match silently found nothing on my first attempt (exactly the `CREW_CONTEXT.md` hazard):

```
if directive_lines:   ->   if True:  # MUTANT guard removed
$ grep -n "MUTANT guard removed" scripts/checklist_engine.py
1772:    if True:  # MUTANT guard removed

FAILED ...::RenderDirectives::test_absent_or_empty_directives_add_no_output
FAILED ...::RenderDirectives::test_unrecognized_directives_shape_renders_nothing
2 failed, 5 passed, 339 deselected in 0.74s
EXIT=1
```

Exactly those two tests go red, each diffing a spurious bare `directives:` header. Restored
byte-identical; `RenderDirectives` back to `7 passed`.

### 4. `state()` gained no side effect — PASS

One executable line added, at 1617:

```python
"directives": t.get("directives"),
```

A bare dict `.get` inside the same dict literal as `constraints`/`anchors`. No call, no mutation, no
check evaluation. It deliberately does **not** coerce with `or []` (unlike `constraints`), matching
`anchors` so `None` passes through as `None` and `render_human()` owns all shape handling. The rest
of the `state()` hunk is comment.

Behaviourally pinned by `test_state_passes_directives_through_without_re_running_checks`, which
patches `E.subprocess.run` with `side_effect=AssertionError` over a gate carrying `FAIL_COMMAND`, so
any process spawn during `state()` raises. That test was one of the 5 RED failures I reproduced, so
it is a proven-failing guard, not decoration.

### 5. Both shapes render — PASS

Renderer carries an `isinstance(directives, dict)` branch (1709-1718) and an
`isinstance(directives, list)` branch (1719-1720). Tests:
`test_nested_contract_dict_shape_renders_indented_leaves` and
`test_flat_list_of_strings_shape_renders_one_line_each` — **both** among the 5 reproduced RED
failures, so both are proven-failing guards.

The flat-list branch is not hypothetical. I confirmed `tests/test_checklist_engine.py:4192` sets
`t["directives"] = ["DIRECTIVE_UNIQUE_TEXT"]` in the `TaskFieldCompleteness` fixture, and
`directives` is still in that class's `_EXCLUDED_FIELDS` at 4158 pending g2. When g2 un-excludes it,
a dict-only renderer would fail there. It will not.

Also verified the handoff's anti-collusion constraint: the tests share **no** leaf-extraction helper
with the renderer. Every expected value is a hard-coded literal string, so a bug in `_directive_leaf`
cannot cancel out against the assertion. Both mutation runs confirm the assertions move when the
renderer moves.

### 6. The renderer is wired — PASS

```
$ grep -n "_render_directive_lines" scripts/checklist_engine.py
1616:            # live shapes via _render_directive_lines().
1689:def _render_directive_lines(directives) -> list[str]:
1771:    directive_lines = _render_directive_lines(active.get("directives"))
```

One genuine call site outside the definition (1771, inside `render_human()`); 1616 is a comment.
Matches the implementer's claim. Not shipped-inert — the end-to-end proof is the corpus scan in
criterion 2, plus a live reproduction against this run's own `spine.json` through the repo's engine,
which really does print the `replan_input` contract now. A renderer nothing called could not have
changed that output.

### 7. Test suite — PASS

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"
346 passed, 30 subtests passed in 12.16s
EXIT=0      # baseline, before I mutated anything

346 passed, 30 subtests passed in 15.01s
EXIT=0      # final, after both mutations reverted and byte-identity confirmed
```

Real exit code from `echo "EXIT=$?"`, not read off the summary line. `python`, never `py` (#454).
Matches the implementer's claimed 346.

---

## Handoff compliance
Satisfied. Every task-statement clause holds and each was checked independently, not read off the
result. The implementer also caught that the handoff's abbreviated example showed **four** contract
fields where the shipped gate carries **six**, and wrote the golden over the real six — I confirmed
all six render.

## Scope drift
None, and no excluded file touched. `git status --porcelain` shows exactly two tracked source files
modified; everything else is `.agent-work/` engine state and crew artifacts, explicitly out of scope.
Each named exclusion checked individually: `docs/CHECKLIST_SCHEMA.md`, `scripts/collect_feedback.py`,
`episodes/`, `scripts/verify_worktree_precondition_coverage.py` — all unmodified.
`class TaskFieldCompleteness` is byte-identical to HEAD (6635 chars both sides), `_EXCLUDED_FIELDS`
still contains `directives` at 4158, `_flatten` unchanged. g2-implement's territory is intact. The
single test-file hunk is a pure 154-line insertion between two existing classes; no existing expected
string needed reconciliation.

## Evidence verdict
Present, fresh, and reproducible — and I reproduced all of it. RED reproduced with identical counts;
post-change 346/EXIT=0 reproduced twice; the 17-passed/329-deselected four-class selection reproduced
exactly; the 8-line purely-additive `current` delta re-derived two independent ways. Test mode
`test-first` is genuinely satisfied: the goldens fail without the renderer, and the two that pass in
both states are negative-space assertions whose bite I proved separately by mutation.

The implementer's honesty markers hold up: it flagged the em-dash codepage transcription and pointed
at the raw on-disk capture, and it correctly explained why 2 of 7 tests pass in RED by construction.

## Code/doc quality
Minimal, tested, and convention-matching. The formatter/leaf-speller pair mirrors
`_render_anchor_lines`/`_anchor_category_items` exactly. The docstring names both corpus shapes it was
verified against, cites the shipped gate, states the unrecognized-shape rule in the sibling's own
words, and cites `decision:own-helper-not-anchors-helper`. No new dependency: zero added `import`
lines; `json` was already imported at line 16.

Fowler pass: 12 smells visited, record at `.agent-work/b433-render-directives/g1-review/fowler-pass.json`,
rail exits 0. One **flagged** (`speculative-generality`, non-blocking, below); four **overridden**
with logged standard + reason (`duplicated-code` under `decision:own-helper-not-anchors-helper` at
`settled/human`; `primitive-obsession` under the engine's raw-JSON contract; `shotgun-surgery` because
the three edit sites *are* INV-1/INV-2's shape; `comments-as-deodorant` because the docstrings carry
required verification provenance); seven absent. I also confirmed the rail is not a check that cannot
fail — blanking one `override.reason` on a temp copy produced
`REFUSED: OVERRIDE-LOG ... no override.reason`, `EXIT=1`.

## Map impact verdict
- **Evidence supports claimed change:** yes. The capability claim (`current` is the complete state
  channel) is real — `directives` was the third and last of the three populated-but-dropped Task
  fields, `anchors`/`constraints` having closed under #420. Proved over the real shipped template.
- **Constraints not violated:** yes. `assumption:schema-type-is-drifted` confirmed live at
  `docs/CHECKLIST_SCHEMA.md:123` (`[string] | null` against 8/8 dict instances). INV-2 honored and now
  pinned by a test. All three decision anchors honored; none needed unsettling.
- **Notes match the diff:** yes. The structural anchors named are the ones actually touched, and the
  line numbers in the result are accurate at this working tree.
- **Decision candidates surfaced:** n/a — no authority beyond the granted latitude was required.
- **Durable context routed:** yes, three triage candidates recorded in the survey (below).

## Reconciliation check
No divergence Commander must reconcile. One note for g3's scope, beyond the type row it already owns:
`docs/CHECKLIST_SCHEMA.md:138` also asserts **"Known gap, not yet closed: `directives`, when
populated, is not rendered"** — which this change falsifies. g3 must correct both the type row and
that sentence, not just the type. Per the handoff I do not block on the document disagreeing.

## Blockers
- None.

## Out-of-scope observations
1. **The flat-list branch silently drops non-string items.**
   `[f"  {item}" for item in directives if isinstance(item, str)]` — a mixed list renders partially,
   so a standing instruction disappears with no signal: the exact defect class #433 closes, inside the
   fix for it. Latent, not live (all 8 populated corpus gates are dicts; the schema declares
   `[string]`). But it departs from the docstring's own stated rule that an unrecognized shape renders
   *nothing* rather than guessing, and from fail-visibly posture. Note `_render_anchor_lines`'s list
   branch does **not** filter, so the two siblings now disagree. Decide whether to render every item
   via `_directive_leaf` or refuse the whole block.
2. **An untested defensive branch** (the Fowler `speculative-generality` flag). The
   dict-value-that-is-not-a-dict `else` at 1716-1717 handles a shape the implementer states is not in
   the corpus, and no test reaches it. I proved it dead against the suite by mutation: replacing that
   line with an unconditional `raise` still gives `346 passed, EXIT=0`. Not asking for removal at this
   gate — it is two lines, honestly documented, and without it a `{name: scalar}` value would emit a
   bare `  name:` header, which is worse. Either cover it or drop it; a defensive branch nothing can
   reach is indistinguishable from one that works.
3. **The engine mints a work-area directory keyed on the plan's own `work_id`, beside the plan rather
   than under it.** Driving this survey created
   `.agent-work/b433-render-directives/b433-render-directives-g1-review/` holding `context/` and
   `mechanical/` step manifests. The implementer hit the identical surprise from its own plan. Two crew
   roles tripping the same thing in one gate makes it a real convention gap: the handoff dictates where
   the survey file goes, the engine independently derives where its manifests go, and the two disagree.
   Engine-written provenance, so neither of us deleted it — Commander should decide.
4. **A measured number carried without a revision pin.** `_render_directive_lines`'s docstring says
   "2955 gates scanned". My scan of the same worktree counted 2981 across 370 files — the delta is
   files created since, not a wrong claim. Per inherited doctrine, a measured number in durable prose
   should name the revision it was measured at. The load-bearing half, **8 populated blocks**, I
   reproduced exactly.
5. **Near-duplicate sibling formatters, rule of three now reached.** Already flagged by the
   implementer; I concur and recorded it. `decision:own-helper-not-anchors-helper` correctly governs
   this gate, but `render_human` now holds a third copy of "compute lines; if lines: append header;
   extend". Worth naming as a pattern above this gate — not this gate's call.

## Workflow Feedback
- **Handoff gaps:** none material — this was an unusually good handoff, and I am saying so with a
  reason: it named the exact defect class the golden could hide (a golden written after the fact),
  told me to reproduce rather than accept, and pre-identified that criterion 3's tests pass in both
  states so existence alone would not settle them. That last line is what sent me to mutation testing
  instead of a green checkmark. One small thing: the criterion-5 pointer
  `tests/test_checklist_engine.py:~4038` was stale by the time I read it — the new 154-line class
  shifted `TaskFieldCompleteness`'s fixture to 4192. Line pointers into the file the diff edits should
  be given as symbol names, not line numbers.
- **Context rediscovered:** the corpus shape distribution. The handoff says all 8 populated instances
  are dicts and the flat list is schema-declared, but to judge whether "both shapes" was the right
  scope I had to run my own tree-wide inventory. That inventory is cheap and both crew roles have now
  run it separately; the packet could carry it once.
- **Instructions improvised around:** two.
  (a) **Which engine copy drives a review of the engine.** The skill says drive through the installed
  skill's bundled engine; `references/checklist-engine.md` §dogfooding says on this repo drive the
  repo's own vendored `scripts/`. Here that conflict is sharp — the vendored engine is the file I was
  required to *revert mid-run*. I drove the survey through the installed copy so reverting the repo's
  engine could not perturb my own survey state, and verified the change with the repo's copy. The
  implementer hit the same fork and resolved it the same way. This case should be named explicitly in
  the dogfooding paragraph.
  (b) **The `r6-fowler` postcondition ships with a placeholder command** (`python
  scripts/verify_fowler_pass.py <fowler-pass-record-path>`) whose relative `scripts/` path resolves
  against the target repo, not the installed skill. I filled it with absolute paths to the installed
  rail and my record before claiming the lease. The template should carry a
  `<reviewer-skill-dir>` token like the other templates do.
- **What would have made this easier:** the handoff's "Evidence Produced (reproduce it, do not accept
  it)" section gave me the exact counts to match against, which made the reproduction a binary
  comparison rather than a judgment call. Keep that section. The one addition I would want: a line
  stating **which engine copy the reviewer should drive**, since this gate's target and the reviewer's
  own tooling are the same file.

## Return status
`complete`
