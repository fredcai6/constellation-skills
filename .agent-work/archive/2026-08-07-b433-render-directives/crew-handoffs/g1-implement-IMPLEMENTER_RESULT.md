# Implementation Result

## Assigned gate
`g1-implement` (execute.json, work-id `b433-render-directives`, issue #433)

## Completed slice
A populated `directives` block now reaches the agent through the engine's `current` projection.
`state()` passes `directives` through beside `constraints`/`anchors`; `render_human()` emits a
`directives:` block between `anchors:` and `next:`, formatted by a new `_render_directive_lines()`
(with a `_directive_leaf()` scalar speller) that serves both live corpus shapes — the
name -> contract-dict shape all 8 populated corpus gates carry, and the flat list-of-strings shape
`docs/CHECKLIST_SCHEMA.md` declares. Absent, empty, and unrecognized shapes add zero output.

## Scope

**Files changed:**
- `scripts/checklist_engine.py` (+63/-1)
  - `state()` — line **1617** added (`"directives": t.get("directives")`), comment 1611–1616.
  - `_directive_leaf()` — new, lines **1674–1687**.
  - `_render_directive_lines()` — new, lines **1689–1725**.
  - `render_human()` docstring — line **1748** amended to name the new block.
  - `render_human()` emission site — lines **1771–1774**.
- `tests/test_checklist_engine.py` (+154)
  - `class RenderDirectives` — new, lines **3958–4110**, inserted between `RenderAnchorsAndConstraints`
    and `TaskFieldCompleteness`.

**Specific exclusions touched:** **no.** `git status --porcelain` shows no change to
`scripts/collect_feedback.py`, `episodes/`, `scripts/verify_worktree_precondition_coverage.py`, or
`docs/CHECKLIST_SCHEMA.md`. `class TaskFieldCompleteness` appears in `git diff -U0` only as an
unchanged **context** line — no `+`/`-` line touches it, its `_EXCLUDED_FIELDS`, or its `_flatten`.
No existing test's expected string changed; nothing needed reconciliation.

**Not committed** — all changes left in the working tree, as instructed.

## Behavior changed
**Yes.** A gate carrying `directives` now shows them in `current`. Before this change the field was
never read by `state()`, so a standing per-gate instruction was silently invisible to the agent it
binds. No other line of `current` moves: the `ACTIVE {id} [{status}] — {imperative}` first line is
byte-identical, and an absent/empty `directives` renders exactly the pre-change output.

## Map Impact
- **Structural anchors touched:** `scripts/checklist_engine.py` — `state()` (~1588, projection built),
  a new sibling formatter beside `_render_anchor_lines()` (~1650), and `render_human()`'s emission
  sequence (~1667). The anchors-formatter neighbourhood now holds two peer formatters, not one.
- **Capabilities affected:** `capability:current-is-the-complete-state-channel` — the projection now
  carries the third of the three populated-but-dropped Task fields. `anchors` and `constraints` were
  closed by #420; `directives` closes with this change.
- **Constraints/assumptions touched:** `assumption:schema-type-is-drifted` **relied on and confirmed
  live** — `docs/CHECKLIST_SCHEMA.md` declares `directives` as `[string] | null` while every populated
  corpus instance is a dict. The renderer serves both; the document is g3's to correct. INV-2 (state()
  purity) honored and now pinned by a test that patches `subprocess.run` to raise.
- **Decisions honored:** `decision:render-not-delete`, `decision:own-helper-not-anchors-helper`
  (the formatter is its own, not routed through `_anchor_category_items`),
  `decision:goldens-written-before-the-change` (RED captured below).
- **Claims/evidence produced:** `claim:a-populated-directives-block-appears-in-current` — proved over
  the real shipped `skills/commander/templates/COMMANDER_SPINE.template.json` `execute` gate, and
  reproduced live against this run's own `spine.json`.
- **Triage candidates:** two, listed under Out-of-scope observations.

## Test mode
**Required:** `test-first` (TDD, RED capture a close criterion).
**Satisfied:** **yes.** The goldens were authored first; `git diff --quiet scripts/checklist_engine.py`
was run immediately before the RED run and confirmed the engine unchanged; the failure output below is
the real output of that run.

## Evidence

### 1. RED capture — the goldens failing with the engine provably unchanged

Command, run from `C:/Programs/constellation-skills-wt/r418-433`:

```bash
git diff --quiet scripts/checklist_engine.py && echo "scripts/checklist_engine.py: UNCHANGED"
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k RenderDirectives; echo "EXIT=$?"
```

Verbatim output (`—` renders as `?` in the console's codepage; the file bytes are UTF-8):

```
scripts/checklist_engine.py: UNCHANGED
.FFFFF.                                                              [100%]
================================== FAILURES ===================================
____ RenderDirectives.test_directives_render_after_anchors_and_before_next ____

self = <test_checklist_engine.RenderDirectives testMethod=test_directives_render_after_anchors_and_before_next>

    def test_directives_render_after_anchors_and_before_next(self):
        t = gate("g1", "pending")
        t["constraints"] = ["CONSTRAINT_TEXT"]
        t["anchors"] = {"structural": ["ANCHOR_TEXT"]}
        t["directives"] = ["DIRECTIVE_TEXT"]
        cl = gated(g1=t)
>       self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] ? do g1\n"
            "constraints:\n"
            "  CONSTRAINT_TEXT\n"
            "anchors:\n"
            "  structural: ANCHOR_TEXT\n"
            "directives:\n"
            "  DIRECTIVE_TEXT\n"
            "next: start g1"
        ))
E       AssertionError: 'ACTI[78 chars]al: ANCHOR_TEXT\nnext: start g1' != 'ACTI[78 chars]al: ANCHOR_TEXT\ndirectives:\n  DIRECTIVE_TEXT\nnext: start g1'
E         ACTIVE g1 [pending] ? do g1
E         constraints:
E           CONSTRAINT_TEXT
E         anchors:
E           structural: ANCHOR_TEXT
E       + directives:
E       +   DIRECTIVE_TEXT
E         next: start g1

tests\test_checklist_engine.py:4087: AssertionError
___ RenderDirectives.test_flat_list_of_strings_shape_renders_one_line_each ____

self = <test_checklist_engine.RenderDirectives testMethod=test_flat_list_of_strings_shape_renders_one_line_each>

    def test_flat_list_of_strings_shape_renders_one_line_each(self):
        # Shape (b), the one docs/CHECKLIST_SCHEMA.md declares and the `add`
        # amend op accepts unvalidated. Narrowing the renderer to dicts would
        # silently reinstate the #433 defect for this shape.
        t = gate("g1", "pending")
        t["directives"] = ["file REPLAN_INPUT.json before advancing",
                            "discrepancies are evidence, never auto-filed issues"]
        cl = gated(g1=t)
>       self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] ? do g1\n"
            "directives:\n"
            "  file REPLAN_INPUT.json before advancing\n"
            "  discrepancies are evidence, never auto-filed issues\n"
            "next: start g1"
        ))
E       AssertionError: 'ACTI[20 chars] g1\nnext: start g1' != 'ACTI[20 chars] g1\ndirectives:\n  file REPLAN_INPUT.json bef[80 chars]t g1'
E         ACTIVE g1 [pending] ? do g1
E       + directives:
E       +   file REPLAN_INPUT.json before advancing
E       +   discrepancies are evidence, never auto-filed issues
E         next: start g1

tests\test_checklist_engine.py:4049: AssertionError
__ RenderDirectives.test_nested_contract_dict_shape_renders_indented_leaves ___

self = <test_checklist_engine.RenderDirectives testMethod=test_nested_contract_dict_shape_renders_indented_leaves>

    def test_nested_contract_dict_shape_renders_indented_leaves(self):
        # Shape (a), the one all 8 populated corpus gates carry, isolated
        # from the shipped template so the format itself is pinned: a list
        # leaf joins with ", " and a non-string scalar takes JSON spelling
        # (Python False -> `false`), so what prints reads back as the JSON
        # the gate actually carries.
        t = gate("g1", "pending")
        t["directives"] = {"replan_input": {
            "template": "../constellation-replan/templates/REPLAN_INPUT.template.json",
            "evidence_fields": ["completed_outcomes", "wave_evidence"],
            "auto_file_discrepancies": False,
        }}
        cl = gated(g1=t)
>       self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] ? do g1\n"
            "directives:\n"
            "  replan_input:\n"
            "    template: ../constellation-replan/templates/REPLAN_INPUT.template.json\n"
            "    evidence_fields: completed_outcomes, wave_evidence\n"
            "    auto_file_discrepancies: false\n"
            "next: start g1"
        ))
E       AssertionError: 'ACTI[20 chars] g1\nnext: start g1' != 'ACTI[20 chars] g1\ndirectives:\n  replan_input:\n    templat[167 chars]t g1'
E         ACTIVE g1 [pending] ? do g1
E       + directives:
E       +   replan_input:
E       +     template: ../constellation-replan/templates/REPLAN_INPUT.template.json
E       +     evidence_fields: completed_outcomes, wave_evidence
E       +     auto_file_discrepancies: false
E         next: start g1

tests\test_checklist_engine.py:4031: AssertionError
_ RenderDirectives.test_shipped_commander_spine_execute_gate_renders_its_directives _

self = <test_checklist_engine.RenderDirectives testMethod=test_shipped_commander_spine_execute_gate_renders_its_directives>

    def test_shipped_commander_spine_execute_gate_renders_its_directives(self):
        cl = self._shipped_spine_with_execute_active()
        t = cl["tasks"]["execute"]
        self.assertTrue(
            t.get("directives"),
            "fixture drift: the shipped COMMANDER_SPINE `execute` gate no "
            "longer carries a populated `directives` block, so this golden "
            "is no longer proving anything -- re-run the corpus inventory",
        )
        out = E.current(cl)
    
        # INV-1's frozen first line: byte-identical to `ACTIVE {id} [{status}]
        # ? {imperative}`, unchanged by this issue (GoldenOutputBriefing pins
        # the same format across every shipped template).
        self.assertEqual(out.splitlines()[0],
                          f"ACTIVE execute [pending] ? {t['imperative']}")
    
>       self.assertIn(
            "\ndirectives:\n"
            "  replan_input:\n"
            "    template: ../constellation-replan/templates/REPLAN_INPUT.template.json\n"
            "    output: .agent-work/<work-id>/REPLAN_INPUT.json\n"
            "    evidence_fields: completed_outcomes, wave_evidence, discrepancies\n"
            "    classifications: blocks_current_wave_exit, invalidates_forecast_or_decomposition, later_only, evidence_only, drop\n"
            "    auto_file_discrepancies: false\n"
            "    check: verify_iterative_role_artifacts.py commander\n",
            out,
        )
E       AssertionError: '\ndirectives:\n  replan_input:\n    template: ../constellation-replan/templates/REPLAN_INPUT.template.json\n    output: .agent-work/<work-id>/REPLAN_INPUT.json\n    evidence_fields: completed_outcomes, wave_evidence, discrepancies\n    classifications: blocks_current_wave_exit, invalidates_forecast_or_decomposition, later_only, evidence_only, drop\n    auto_file_discrepancies: false\n    check: verify_iterative_role_artifacts.py commander\n' not found in "ACTIVE execute [pending] ? Before entering this step: ensure context headroom (run a harness compaction command if one is exposed, else rely on harness auto-compaction ? either is fine) and reload the constellation-commander skill into this context, confirming it is active; this satisfies p1. Then, before this step and before EACH detached dispatch, (re)write the crash-resume state note at .agent-work/<work-id>/STATE_NOTE.md (step ? slug ? next command ? PID ? expected artifact) from .agent-work/templates/STATE_NOTE.template.md, or the bundled skills/workbench/templates/STATE_NOTE.template.md when the project has no .agent-work/templates/ overlay ? the PID changes per detach, and the engine refuses to start execute until it is filled (precondition p2). Then drive execute.json gate by gate in this conversation using this skill's gate execution instructions. Dispatch subagents only for the implementer and reviewer tasks within each gate, and NEVER hand-launch a crew: run every implementer/reviewer dispatch through python <commander-skill-dir>/scripts/run_crew.py (foreground/blocking, durable registry, result-artifact verification). Before this step and before EACH crew dispatch, run python <commander-skill-dir>/scripts/recover_crews.py <work-id> and only launch when it reports no unresolved running/resumable/conflicting crew for that work-id/gate/role/worktree; recover (resume) or explicitly abandon/relaunch any it flags. Record completed outcomes, observed-vs-expected wave evidence, and classified discrepancies in the exact ../constellation-replan/templates/REPLAN_INPUT.template.json fields at .agent-work/<work-id>/REPLAN_INPUT.json as execution proceeds; discrepancies remain evidence and MUST NOT be auto-filed as issues. Run python <commander-skill-dir>/scripts/verify_iterative_role_artifacts.py commander --work-id <work-id>; missing, malformed, or non-G2 run packets refuse execute completion. If a gate proves the plan wrong, surface the decision to the user before continuing. In delegated mode, surface a plan-invalidating discovery to the Admiral (float it) per the commander skill's Delegated/autonomous mode, rather than blocking on the human.\npreconditions:\n  p1 [unmet] null ? plan approved; context headroom ensured and commander skill reloaded into this context\n  p2 [unmet] command ? crash-resume state note written before any detached dispatch (step, slug, next command, pid, expected artifact)\npostconditions:\n  c1 [unmet] null ? every gate closed with integrated evidence\n  c2 [unmet] command ? the run's REPLAN_INPUT.json returns observed execution discrepancies/evidence through the exact verified G2 input without automatic issue filing\n0/4 met\nnext: attest execute --cond p1 --which preconditions"

tests\test_checklist_engine.py:4002: AssertionError
_ RenderDirectives.test_state_passes_directives_through_without_re_running_checks _

self = <test_checklist_engine.RenderDirectives testMethod=test_state_passes_directives_through_without_re_running_checks>

    def test_state_passes_directives_through_without_re_running_checks(self):
        # INV-2: state() is a pure projection. The passthrough must not
        # touch a `command` check -- if it did, this gate's deliberately
        # process-spawning postcondition would run on a read-only `current`.
        t = gate("g1", "in-progress", command=FAIL_COMMAND, why_exempt=False)
        t["directives"] = {"replan_input": {"output": "x.json"}}
        cl = gated(g1=t)
        with mock.patch.object(E.subprocess, "run",
                                side_effect=AssertionError("state() ran a command check")):
            view = E.state(cl)
>       self.assertEqual(view["active"]["directives"],
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                          {"replan_input": {"output": "x.json"}})
E       KeyError: 'directives'

tests\test_checklist_engine.py:4108: KeyError
=========================== short test summary info ===========================
FAILED tests/test_checklist_engine.py::RenderDirectives::test_directives_render_after_anchors_and_before_next
FAILED tests/test_checklist_engine.py::RenderDirectives::test_flat_list_of_strings_shape_renders_one_line_each
FAILED tests/test_checklist_engine.py::RenderDirectives::test_nested_contract_dict_shape_renders_indented_leaves
FAILED tests/test_checklist_engine.py::RenderDirectives::test_shipped_commander_spine_execute_gate_renders_its_directives
FAILED tests/test_checklist_engine.py::RenderDirectives::test_state_passes_directives_through_without_re_running_checks
5 failed, 2 passed, 339 deselected, 4 subtests passed in 0.93s
EXIT=1
```

> One transcription note, flagged rather than hidden: the block above is byte-for-byte as captured
> **except** that the console rendered every em-dash as the replacement character `�` (its codepage
> cannot show U+2014); those appear here as `?`. The source files themselves are UTF-8 and hold real
> em-dashes. The raw capture is on disk at
> `.agent-work/b433-render-directives/evidence/g1-RED-capture.txt`.

**The two passers are load-bearing, not noise:** `test_absent_or_empty_directives_add_no_output` and
`test_unrecognized_directives_shape_renders_nothing` assert **zero** added output, so they pass in
both the RED and GREEN states by construction. Their passing in RED is what proves those two are
negative-space assertions rather than accidental pass-throughs.

### 2. Post-change full suite

```bash
cd C:/Programs/constellation-skills-wt/r418-433
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"
```

```
346 passed, 30 subtests passed in 14.34s
EXIT=0
```

The exit code is the shell's real `$?`, not read off the summary line. Run twice, identical both times.

### 3. Before/after `current` for a real populated block

Produced against **this run's own live `spine.json`** — no copy was needed, because its `execute`
gate is already `in-progress` and therefore active:

```bash
python scripts/checklist_engine.py --file .agent-work/b433-render-directives/spine.json current
```

`diff` of before vs after (the long `ACTIVE execute` imperative line is elided from both sides so the
delta is legible; nothing else is filtered). Captures on disk:
`.agent-work/b433-render-directives/evidence/g1-current-BEFORE.txt` and `…-AFTER.txt`.

```
7a8,15
> directives:
>   replan_input:
>     template: ../constellation-replan/templates/REPLAN_INPUT.template.json
>     output: .agent-work/b433-render-directives/REPLAN_INPUT.json
>     evidence_fields: completed_outcomes, wave_evidence, discrepancies
>     classifications: blocks_current_wave_exit, invalidates_forecast_or_decomposition, later_only, evidence_only, drop
>     auto_file_discrepancies: false
>     check: verify_iterative_role_artifacts.py commander
```

The diff is purely additive: eight added lines, zero changed or removed. The `ACTIVE` line, the
conditions block, the `n/m met` summary, `next:`, `DIGEST:` and the `CONTEXT` advisory are all
untouched.

### 4. `GoldenOutputBriefing` still green (confirmatory)

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py \
  -k "GoldenOutputBriefing or RenderDirectives or TaskFieldCompleteness or ShippedTemplates"
```

```
17 passed, 329 deselected, 24 subtests passed in 0.42s
```

`ShippedTemplates::test_every_template_is_valid_json_and_checklists_walk` is included: it asserts
`E.current(data).startswith("ACTIVE")` for **every** shipped template, so the frozen first line is
covered corpus-wide, not just on the spine.

### 5. Absent/empty adds no output (confirmatory)

`RenderDirectives::test_absent_or_empty_directives_add_no_output` — asserts byte-equality with the
pre-change baseline for `None`, `{}`, `[]`, `""`, and for the `directives` key deleted entirely.
`RenderDirectives::test_unrecognized_directives_shape_renders_nothing` covers a non-dict, non-list value.

## Wiring grep

```bash
grep -rn "_render_directive_lines" --include=*.py C:/Programs/constellation-skills-wt/r418-433 | grep -v "def _render_directive_lines"
```

```
scripts/checklist_engine.py:1616:            # live shapes via _render_directive_lines().
scripts/checklist_engine.py:1771:    directive_lines = _render_directive_lines(active.get("directives"))
```

**2 lines outside the definition; 1 of them is a real call site** (line 1771, inside `render_human()`).
Line 1616 is a prose comment in `state()`, not a call. **Call-site count = 1, not zero** — the stop
condition does not fire, and evidence 3 confirms the renderer is live end-to-end, not shipped-inert.

## TDD evidence, if required
- **Failing test observed:** yes — Evidence 1 above, engine confirmed unchanged by `git diff --quiet`
  in the same shell invocation immediately prior.
- **Passing test observed:** yes — Evidence 2, `EXIT=0`.
- **Refactor while green:** no. The implementation is the minimal shape the goldens pin.

## Docs/contracts touched
- **None.** `docs/CHECKLIST_SCHEMA.md` is g3's deliverable and was not opened for edit. The two
  docstrings changed (`state()`'s inline comment, `render_human()`'s docstring) are at the changed
  sites, which the handoff's Allowed Scope permits.

## Assumptions
- **The handoff's target-format example is abbreviated; the shipped gate is the authority.** The
  handoff shows the `execute` gate's `directives` with four fields. The actual shipped
  `COMMANDER_SPINE.template.json` `execute` gate carries **six**: `classifications` (a 5-element list)
  and `check` (a string) are also present. The golden was written over the real six, per the handoff's
  own binding rule that the golden go over the ACTUAL shipped gate.
- **String leaves render bare; other scalars take JSON spelling.** The handoff fixes
  `auto_file_discrepancies: false` (so `json.dumps` for non-strings) and
  `template: ../constellation-replan/…` unquoted (so strings bare). Both are within the "nested
  indentation and separator are yours" grant and are pinned by the goldens.
- **A dict value that is not itself a dict renders as one leaf line beside its name.** Not a corpus
  shape — a defensive branch so such a value cannot produce an empty header. Documented as such in
  the docstring, which otherwise names only the two verified corpus shapes.
- **Making the shipped spine's `execute` gate active in the golden** is done by marking the four
  preceding items complete on an in-memory copy. The gate itself is untouched, read straight from disk
  with `encoding="utf-8"`.

## Stop conditions hit
- **None.** Scope was not exceeded, no excluded file was touched, the RED capture was produced, the
  `ACTIVE` first line is byte-identical, and no decision outside the granted authority was needed.

## Out-of-scope observations
1. **`_render_anchor_lines` and `_render_directive_lines` are now near-duplicate siblings.**
   `decision:own-helper-not-anchors-helper` correctly keeps them separate for now, but a third such
   field would make the pattern (project a Task field, format it, emit a labelled block only when
   populated) worth naming. Triage candidate, not this gate's call.
2. **The engine's step-manifest writer creates a directory keyed on the plan's `work_id`.** Driving my
   own plan (`work_id: b433-render-directives-g1-implement`) produced a new untracked
   `.agent-work/b433-render-directives-g1-implement/` beside the run's own work area, holding
   `context/` and `mechanical/` step manifests. It is engine-written provenance, so I did not hand-delete
   it, but Commander should decide whether crew plans belong under the parent work-id directory instead
   of minting a sibling. Triage candidate.
3. **The `CONTEXT` gauge advisory is read from the checklist file's own directory**, so my plan — which
   lives in the Commander's work-area directory — inherited the **Commander's** `gauge.json` reading and
   greeted my very first `claim` with "CONTEXT 11% (>= soft): you've used most of your context." That is
   a misattributed reading, not a real one, at the start of a fresh agent's run. Declined with reason
   (I was at the start of my run); flagging because a crew agent that obeyed it would hand off on turn one.

## Workflow Feedback
- **Handoff gaps:** the **"Target format"** block under *The shape the renderer must serve* is
  incomplete — it shows four contract fields for the shipped `execute` gate's `replan_input`, but the
  shipped gate carries six (`classifications`, `check` are missing from the example). Because the same
  handoff makes "the golden must be over the ACTUAL shipped gate" a refusal condition, an implementer
  who trusted the example would have written a golden that fails for the wrong reason. Show the full
  block, or label the example as abbreviated.
- **Context rediscovered:** nothing structural. The Map Anchors' line numbers (`state()` ~1588,
  `_render_anchor_lines()` ~1650, `render_human()` ~1667, `GoldenOutputBriefing` ~3779) were all
  accurate, which saved real time. The one thing I had to derive myself was **how to make the shipped
  spine's `execute` gate active in a test** — the handoff names the requirement but not the mechanism,
  and the test file had no prior example of driving a shipped template to a chosen gate
  (`ShippedTemplates` only ever asserts the first gate).
- **Instructions improvised around:** the implementer skill says to drive the plan through *the
  installed skill's* bundled engine, while `references/checklist-engine.md` §dogfooding says that on
  the constellation-skills source repo you should drive the repo's own vendored `scripts/`. Those
  conflict, and here the conflict is sharp: the repo's vendored engine is **the file under test**.
  I drove my plan through the installed copy at
  `C:/Users/fredc/.claude/skills/constellation-implementer/scripts/checklist_engine.py` so that editing
  the engine could not perturb my own plan-driving mid-run, and verified the change with the repo's copy.
  Naming this case explicitly in the dogfooding paragraph would remove the judgement call.
- **What would have made this easier:** one line in the handoff stating that the shipped gate carries
  six contract fields and that the example is abbreviated — or, better, pasting the exact expected
  block. That is the single thing that could have sent a careful implementer to a wrong golden.

## Return status
`complete`
