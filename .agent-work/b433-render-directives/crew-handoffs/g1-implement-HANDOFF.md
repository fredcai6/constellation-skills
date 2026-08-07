# Implementer Handoff — g1-implement

## Gate
`g1-implement` (execute.json, work-id `b433-render-directives`, issue #433)

Worktree: `C:/Programs/constellation-skills-wt/r418-433`, branch `epic-418/b-433-render-directives`.
Work only there. Use absolute paths.

## Task

Make a populated `directives` block reach the agent through the engine's `current` projection.

Two edits in `scripts/checklist_engine.py`:

1. `state()` (~line 1588) — add `"directives": t.get("directives")` to the `active` dict, beside the
   existing `constraints` / `anchors` passthroughs. Pure passthrough, no side effect, no check re-run.
2. `render_human()` (~line 1667) — emit a `directives:` block after the `anchors:` block and before
   the `next:` line, formatted by a new `_render_directive_lines()` placed beside
   `_render_anchor_lines()` (~line 1650).

## The shape the renderer must serve — measured, not assumed

A tree-wide inventory of this worktree (2955 gates scanned) found **8 populated `directives` blocks,
every one a dict whose values are nested dicts**:

```json
"directives": {
  "replan_input": {
    "template": "../constellation-replan/templates/REPLAN_INPUT.template.json",
    "output": ".agent-work/<work-id>/REPLAN_INPUT.json",
    "evidence_fields": ["completed_outcomes", "wave_evidence", "discrepancies"],
    "auto_file_discrepancies": false
  }
}
```

The renderer MUST handle **both** shapes, exactly as `_anchor_category_items` already handles
anchors' three shapes:

- **(a) key -> nested contract dict** — the shape all 8 populated corpus gates carry. Emit the key,
  then one indented line per contract field. A list leaf joins with `", "`. Scalars take **JSON
  spelling**, so a Python `False` prints as `false`.
- **(b) a flat list of strings** — the shape `docs/CHECKLIST_SCHEMA.md` declares and the `add` amend
  op accepts unvalidated. Emit one indented line per string.

**A dict-only renderer is REFUSED at review.** `tests/test_checklist_engine.py:4038` already carries
the flat-list shape (`t["directives"] = ["DIRECTIVE_UNIQUE_TEXT"]`); narrowing to dicts would
silently reinstate for that shape the very defect this issue closes.

Target format, for the shipped commander-spine `execute` gate:

```
directives:
  replan_input:
    template: ../constellation-replan/templates/REPLAN_INPUT.template.json
    output: .agent-work/<work-id>/REPLAN_INPUT.json
    evidence_fields: completed_outcomes, wave_evidence, discrepancies
    auto_file_discrepancies: false
```

An unrecognized shape renders nothing rather than guessing — same rule `_render_anchor_lines` states.

## Protected Intent

- `current`'s **first line stays byte-identical**: `ACTIVE {id} [{status}] — {imperative}`. Pinned by
  `GoldenOutputBriefing` (~line 3779) across every shipped template.
- An **absent or empty** `directives` emits **nothing** — exactly as `constraints` and `anchors`
  behave today.
- `state()` stays **pure**: passthrough only, no check re-runs (INV-2, stated in the code above it).

## Test Mode

**TDD required, and the RED capture is a close criterion, not a courtesy.** The frozen pre-ruling
`decision:goldens-written-before-the-change` governs: a golden written after the change certifies
whatever the code now emits.

Order of work, non-negotiable:

1. Author the new golden **first**, over the **ACTUAL shipped**
   `skills/commander/templates/COMMANDER_SPINE.template.json` `execute` gate (that gate carries the
   `replan_input` directives block). Put it in `tests/test_checklist_engine.py`.
2. Run it and **capture the REAL failure output verbatim** — that is your RED capture.
3. Only then change `checklist_engine.py`.
4. Re-run: green.

## Close Criteria

- A populated `directives` block appears in `current` for the shipped commander-spine `execute` gate,
  proved by the new golden.
- The RED capture from step 2 is pasted verbatim into the result, with the exact command that produced it.
- Both shapes render: the nested-dict shape and the flat-list-of-strings shape, each with its own test.
- An absent `directives` and an empty `directives` each add zero output — asserted by test.
- The `ACTIVE` first line is unchanged — the existing `GoldenOutputBriefing` class stays green.
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py` exits **0**.

## Allowed Scope

- `scripts/checklist_engine.py` — `state()`, the new `_render_directive_lines()`, and the
  `render_human()` emission site. Docstrings at those sites may be updated to match.
- `tests/test_checklist_engine.py` — new tests, and minimal reconciliation of any existing test whose
  expected output legitimately changes because a gate it uses now renders `directives`. If an
  existing test's expected string must change, **name it in your result and show the before/after**.

## Specific Exclusions

- `tests/test_checklist_engine.py`'s `class TaskFieldCompleteness` (~3958) — **do not touch it.**
  It is gate `g2-implement`'s deliverable in this same run. In particular do not remove `directives`
  from its `_EXCLUDED_FIELDS`, and do not change its `_flatten`.
- `docs/CHECKLIST_SCHEMA.md` — gate `g3-schema` owns it.
- Fenced to concurrent sibling issues this wave, do not touch: `scripts/collect_feedback.py` (#464),
  `episodes/` (#460), `scripts/verify_worktree_precondition_coverage.py` (#436).
- The gate schema itself (what fields a Task may carry) — a load-bearing interface shape, not yours.
- The Trip `CONTEXT` advisory and the doctrine rail — both `dispatch()`-level, outside `current()`.

## Constraints

- Follow the surrounding code's idiom: `_render_directive_lines` mirrors `_render_anchor_lines`'s
  shape, docstring density, and "unrecognized shape renders nothing" discipline.
- Its docstring must say **which corpus shapes it was verified against**, the way
  `_render_anchor_lines`'s does.
- No new dependency. `json.dumps` for scalar spelling is already available.
- Do not share a leaf-extraction helper with anything under `TaskFieldCompleteness` — g2 requires the
  test's extractor to stay independent of the renderer's, so a shared bug cannot render nothing and
  assert nothing in agreement.

## Map Anchors (inbound)

- **Structural:** `scripts/checklist_engine.py` — `state()` ~1588, `_render_anchor_lines()` ~1650,
  `render_human()` ~1667; `tests/test_checklist_engine.py` — `GoldenOutputBriefing` ~3779.
- **Capability:** the projection is the complete state channel — `docs/agents/GLOSSARY.md`: agents
  drive from what `current` prints, never from the JSON file.
- **Constraints/assumptions:** `assumption:schema-type-is-drifted` — `docs/CHECKLIST_SCHEMA.md`
  declares `directives` as `[string] | null`; all 8 populated corpus instances are dicts. Serve the
  corpus. The document is corrected at g3, not by you.
- **Decision anchors:**
  - `decision:render-not-delete` — `directives` is rendered, not deleted.
    `@grade: settled/measured · leans g1 · settle: re-run the tree-wide inventory; a count of 0 populated gates would reopen this`
  - `decision:own-helper-not-anchors-helper` — `directives` gets its own formatter rather than being
    pushed through the anchors normalizer; the two shapes genuinely differ.
    `@grade: settled/human · leans g1`
  - `decision:goldens-written-before-the-change` — golden first, RED captured.
    `@grade: settled/inherited · leans g1`
- **Evidence expectations:** `claim:a-populated-directives-block-appears-in-current`, proved over the
  real shipped template rather than a fixture shaped like it.
- **Map confidence flags:** this repo carries no `docs/architecture` packet map; orientation is
  DEGRADED by standing condition. `docs/CHECKLIST_SCHEMA.md` is a hash-pinned substitute and is known
  stale on exactly the `directives` type — do not trust that row.

## Deliverable Path Check

- **Committed** — `scripts/checklist_engine.py`; `git check-ignore -v` exited **1** (not ignored).
- **Committed** — `tests/test_checklist_engine.py`; same, exit **1**.
- **Committed** — `.agent-work/b433-render-directives/crew-handoffs/g1-implement-IMPLEMENTER_RESULT.md`;
  `git check-ignore -v` on that directory exited **1** (not ignored). It is a **new** file: `git diff`
  shows the two source files; the new result file appears in `git status` until staged.

## Required Evidence

**Load-bearing — prove rigorously:**

1. The **RED capture**: the exact command, and the real failure output of the new golden run *before*
   the renderer change. Paste it verbatim. This is the gate's whole point.
2. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py` after the change —
   the summary line **and** the real exit code (`echo "EXIT=$?"`). Do not infer green from the summary.
3. The **before/after `current` output** for a real populated block. Produce it with:
   `python scripts/checklist_engine.py --file .agent-work/b433-render-directives/spine.json current`
   — this run's own `execute` gate carries `directives.replan_input`. It is `pending`, so make it
   active by pointing at a copy if needed, or use the shipped template directly; state which you did.

**Confirmatory — a spot-check suffices:**

4. `GoldenOutputBriefing` still green (covered by evidence 2, name it).
5. Absent/empty `directives` adds no output (covered by your new test, name it).

## Wiring Grep

```bash
grep -rn "_render_directive_lines" --include=*.py C:/Programs/constellation-skills-wt/r418-433 | grep -v "def _render_directive_lines"
```

State the **count of call sites found outside the definition**. Zero is a stop condition: a renderer
`render_human()` never calls is shipped-inert, which is the exact defect class this issue closes.

## Verification Commands

```bash
cd C:/Programs/constellation-skills-wt/r418-433
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"
```

Never use `py` for pytest (#454). `FORCE_COLOR=3` produces false reds.

## Suggested Model Tier

**Stronger.** The engine's core projection, a frozen first line, and a RED-before-GREEN discipline the
review will independently reproduce.

## Authority

Already decided, not yours to reopen: render rather than delete; a dedicated formatter rather than the
anchors normalizer; both shapes supported; golden-before-change. The nested indentation and the exact
separator for list leaves are yours, provided the format is stable and the tests pin it.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be touched; the RED
capture cannot be produced; the first `ACTIVE` line cannot be kept byte-identical; or a decision
outside the authority above is needed.

## Return Format

Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced
(with the RED capture verbatim), assumptions used, stop conditions hit, out-of-scope observations,
workflow feedback.
