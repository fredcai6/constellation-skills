# scripts.grade_lint
scripts/grade_lint.py, 792 lines, 24 holes

Lint `@grade:` decision tags — a plan decision's fixedness as an inline,

greppable property of the decision itself, so no second hand-maintained ledger
ever has to exist.

Grammar (frozen by a prior 3-agent design panel; do NOT redesign here):

    @grade: <tier>[/provenance][ · leans <ids>][ · settle: <experiment>]

`·` is U+00B7 MIDDLE DOT, the field separator. `tier` is exactly one of
`settled`, `guess`, `placeholder` and is always required; `provenance`
(`human`, `measured`, `inherited`) is written suffixed to the tier as
`settled/human` and is required when tier is `settled` (absent -> WARN, never
FAIL); `leans` is a comma-separated list of gate/item ids in this plan and is
optional; `settle:` is one line naming the cheapest experiment and is required
when tier is `guess`. `@grade:` is the sole greppable anchor; only the tier is
hard-required, every other field degrades gracefully and never raises.

The tag welds to its decision either on the decision's own Markdown list-item
line, or on the next non-blank line as a child of that bullet (bare or wrapped
in single backticks — both accepted), or as a suffix appended to the decision
string itself in JSON (`"decision:foo — text @grade: guess · ..."`).

Three binding rulings from a cold-critic review (see g1-implement handoff,
issue #230, epic-226):

  1. `decision:md-decision-is-a-list-item` — in Markdown, a candidate decision
     is a LIST-ITEM LINE ONLY (matches ``^\s*[-*+]\s``) inside a recognized
     block. Prose sentences are never decisions.
  2. `decision:gl012-scoped-per-file` — contradictory-grade detection (GL012)
     is scoped per input file, never across files. Decision identity comes
     only from an explicit `decision:<id>` token; a decision with no such
     token is excluded from GL008/GL012 cross-occurrence comparison.
  3. `decision:placeholder-is-not-a-decision` — a decision payload that is
     ENTIRELY an angle-bracket placeholder (``^<.*>$`` after stripping the
     list marker and any wrapping backticks) is template scaffolding, not a
     decision, and is skipped everywhere — no ``--include-templates`` flag,
     no filename-based skipping.
  4. `decision:wrapped-bullets-are-invalid` (human ruling, issue #239 item 3)
     — the weld rule above stays exactly same-line-or-next-non-blank; it is
     NOT extended to scan past a decision bullet's own wrapped continuation
     lines. A bullet that wraps before its tag is INVALID and reports GL013
     WRAPPED_DECISION_GRADE (one FAIL naming the real cause) instead of the
     GL001+GL010 pair a naive same-shape check would otherwise emit.

THE FORK — `--mode preflight` (default) treats an ungraded decision in a
recognized block as GL001 UNGRADED_DECISION, a FAIL. `--mode execute` reads an
ungraded decision as implicitly `settled` and suppresses GL001 entirely. This
is a DIAGNOSTIC PREVIEW of the lenient execution-time reading, NOT enforcement:
nothing here is wired to `checklist_engine.py`, which does not parse `@grade:`
tags at all — "lint loud, execute safe."

Locality (invariant 7): this script NEVER creates, writes, reads, or caches a
ledger file. Every run recomputes its view from the inline tags alone.

Exit codes: 0 = pass, 1 = FAIL-severity violations present (or a WARN present
under --strict-warnings), 2 = tooling/usage error (missing file, invalid JSON,
bad flags) — matching argparse's own convention and the sibling
`scripts/verify_*.py` rails.

imports stdlib: __future__.annotations, argparse, dataclasses.dataclass, dataclasses.field, json, pathlib.Path, re, sys
imported by: none found

```python
MIDDOT = '·'
TIERS = {'settled', 'guess', 'placeholder'}
FAIL = 'FAIL'
WARN = 'WARN'
CODE_INFO = {'GL001': ('UNGRADED_DECISION', FAIL), 'GL002': ('INVALID_TIER', FAIL), 'GL003': ('MISS...
FENCE_RE = re.compile('^\\s*(`{3,}|~{3,})')
HEADING_RE = re.compile('^(#{1,6})\\s+(.*\\S)\\s*$')
RECOGNIZED_RE = re.compile('pre-rulings|decision anchors', re.IGNORECASE)
LIST_ITEM_RE = re.compile('^\\s*[-*+]\\s+')
PLACEHOLDER_RE = re.compile('^<[^<>]*>$', re.DOTALL)
DECISION_ID_RE = re.compile('\\bdecision:([A-Za-z0-9_.\\-]+)')
TBD_RE = re.compile('\\b(TBD|TODO|CONTRADICTION)\\b', re.IGNORECASE)
GRADE_MARKER = '@grade:'
```

- [_utf8_stdio](_utf8_stdio.md) function: HOLE: no docstring
- [GradeTag](GradeTag.md) class: HOLE: no docstring
- [DecisionRecord](DecisionRecord.md) class: HOLE: no docstring
- [Violation](Violation.md) class: HOLE: no docstring
- [make_violation](make_violation.md) function: HOLE: no docstring
- [find_grade_occurrences](find_grade_occurrences.md) function: Every literal '@grade:' occurrence's body in `text`, each bounded by the
- [parse_grade_body](parse_grade_body.md) function: HOLE: no docstring
- [strip_wrapping_backticks](strip_wrapping_backticks.md) function: HOLE: no docstring
- [is_placeholder](is_placeholder.md) function: HOLE: no docstring
- [extract_decision_id](extract_decision_id.md) function: HOLE: no docstring
- [scan_block](scan_block.md) function: HOLE: no docstring
  - [scan_block.indent_of](scan_block.indent_of.md) method: HOLE: no docstring
  - [scan_block.child_grade_bodies](scan_block.child_grade_bodies.md) method: Grade bodies on the decision's child line, if any, marking that line
  - [scan_block.detect_wrapped_grade](scan_block.detect_wrapped_grade.md) method: The wrapped-bullet shape: this decision failed to weld (no same-line
  - [scan_block.consume_nested_bullets](scan_block.consume_nested_bullets.md) method: A bullet indented deeper than this decision's own bullet is
- [scan_markdown](scan_markdown.md) function: HOLE: no docstring
  - [scan_markdown.flush_block](scan_markdown.flush_block.md) method: HOLE: no docstring
- [extract_plan_ids](extract_plan_ids.md) function: The known gate/item id universe a JSON plan self-sources: its top-level
- [scan_json](scan_json.md) function: HOLE: no docstring
  - [scan_json.handle_anchor_list](scan_json.handle_anchor_list.md) method: HOLE: no docstring
- [validate_decision](validate_decision.md) function: HOLE: no docstring
- [cross_occurrence_violations](cross_occurrence_violations.md) function: GL008 (same decision id repeated with the same tier) and GL012 (same
- [build_ledger](build_ledger.md) function: HOLE: no docstring
- [ledger_summary_line](ledger_summary_line.md) function: HOLE: no docstring
- [load_id_universe](load_id_universe.md) function: HOLE: no docstring
- [build_arg_parser](build_arg_parser.md) function: HOLE: no docstring
- [compute_exit_code](compute_exit_code.md) function: HOLE: no docstring
- [violation_to_dict](violation_to_dict.md) function: HOLE: no docstring
- [render_text](render_text.md) function: HOLE: no docstring
- [LintToolingError](LintToolingError.md) class: A tooling/usage failure (unreadable file, invalid JSON) -- exit code 2.
- [lint_one_file](lint_one_file.md) function: Scan and validate one plan file, Markdown or JSON.
- [main](main.md) function: HOLE: no docstring
