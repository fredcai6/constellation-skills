# Lessons Apply-or-Defer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make "apply-or-defer" a forced outcome at the Commander feedback step for every threshold-ripe lesson, so validated, fixable lessons stop being silently re-banked.

**Architecture:** Extend the existing deterministic `apply_lessons_delta.py` (the LLM proposes ops, the script applies) with a `target` field, apply-thresholds in the playbook-state marker, and three disposition ops (`apply`/`export`/`defer`). A new sibling verifier `verify_lessons_applied.py` reuses the ripeness model and is wired as an engine `command` postcondition on the Commander `feedback` step (and Admiral `closeout`), turning the previously-advisory disposition into a hard gate.

**Tech Stack:** Python 3 stdlib only (argparse, json, re, dataclasses). Tests are `unittest` run via `pytest`. JSON checklist templates. The constellation checklist engine.

## Global Constraints

- Python stdlib only — no new dependencies.
- Run tests with `python -m pytest tests/<file>.py -v` from the repo root (`C:\Programs\constellation-skills`).
- `apply_lessons_delta.py` is **all-or-nothing**: any invalid op rejects the whole delta and writes nothing. Preserve this.
- `LESSONS.md` is never edited by hand or by an LLM — only via applied deltas. Preserve this.
- Scopes are exactly `handoff | commander | admiral | project | constellation`. Only `constellation` accrues `recurrences` (debt); all others accrue `confirmed` (trust).
- Default thresholds: constellation `apply-recurrences = 1`, non-constellation `apply-confirmed = 3`. Stored in the `playbook-state` marker; parsing must default them when absent (back-compat with existing files).
- Engine `command` postconditions reference bundled scripts via the `<commander-skill-dir>` / `<admiral-skill-dir>` token (rewritten to an absolute path at install) and must be POSIX-shell safe.
- End every commit message with:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` and
  `Claude-Session: https://claude.ai/code/session_0128jJKVmWX5RmeA19KWwg6b`

---

## File Structure

- `scripts/apply_lessons_delta.py` — data model + ops + `ripe_lessons()` (Tasks 1–5)
- `scripts/verify_lessons_applied.py` — **new** feedback-step gate (Task 6)
- `scripts/install_constellation.py` — bundle the new verifier (Task 7)
- `skills/commander/templates/COMMANDER_SPINE.template.json` — feedback postcondition + imperative (Task 7)
- `skills/admiral/templates/ADMIRAL_SPINE.template.json` — closeout postcondition (Task 7)
- `skills/admiral/templates/LATITUDE_CONTRACT.template.md` — apply-lessons decision class (Task 7)
- `skills/workbench/templates/LESSONS.template.md` — document field/ops/statuses/thresholds (Task 8)
- `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` — retire the Template Update Candidates table (Task 8)
- `tests/test_apply_lessons_delta.py` — extend (Tasks 1–5)
- `tests/test_verify_lessons_applied.py` — **new** (Task 6)
- `tests/test_install_constellation.py` — extend (Task 7)

---

### Task 1: `target` field + apply-thresholds in the data model

**Files:**
- Modify: `scripts/apply_lessons_delta.py`
- Test: `tests/test_apply_lessons_delta.py`

**Interfaces:**
- Produces: `Lesson.target: str`, `Lesson.deferred_at: int`; `Playbook.apply_recurrences: int`, `Playbook.apply_confirmed: int`; module constants `DEFAULT_APPLY_RECURRENCES = 1`, `DEFAULT_APPLY_CONFIRMED = 3`. `add`/`amend` ops accept an optional `target`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_apply_lessons_delta.py`:

```python
    def test_add_accepts_target_and_round_trips(self):
        self.run_delta({"work_id": "issue-1", "ops": [
            add_op(target="docs/agents/CREW_CONTEXT.md")]})
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active[0].target, "docs/agents/CREW_CONTEXT.md")
        self.assertIn("- target: docs/agents/CREW_CONTEXT.md", self.file.read_text(encoding="utf-8"))

    def test_thresholds_default_when_absent_and_render_explicit(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.apply_recurrences, 1)
        self.assertEqual(book.apply_confirmed, 3)
        self.assertIn("apply-recurrences=1 apply-confirmed=3", self.file.read_text(encoding="utf-8"))

    def test_thresholds_round_trip_custom_values(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        text = self.file.read_text(encoding="utf-8").replace(
            "apply-recurrences=1 apply-confirmed=3", "apply-recurrences=2 apply-confirmed=5")
        self.file.write_text(text, encoding="utf-8")
        book = self.m.load_playbook(self.file)
        self.assertEqual((book.apply_recurrences, book.apply_confirmed), (2, 5))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_apply_lessons_delta.py -k "target or threshold" -v`
Expected: FAIL (`Lesson` has no `target`; `Playbook` has no `apply_recurrences`).

- [ ] **Step 3: Implement the data-model changes**

In `scripts/apply_lessons_delta.py`:

Add constants beside `DEFAULT_DORMANCY_RUNS`:
```python
DEFAULT_APPLY_RECURRENCES = 1
DEFAULT_APPLY_CONFIRMED = 3
```

Widen `STATE_RE` to optionally capture the two thresholds:
```python
STATE_RE = re.compile(
    r"<!--\s*playbook-state:\s*run-tick=(\d+)\s+cap=(\d+)\s+dormancy-runs=(\d+)"
    r"(?:\s+apply-recurrences=(\d+))?(?:\s+apply-confirmed=(\d+))?\s*-->"
)
```

Add fields to `Lesson` (after `runs_since_confirmed`):
```python
    target: str = ""
    deferred_at: int = -1
```

In `Lesson.render()`, add a `target` line after the `grounding` line:
```python
            f"- grounding: {self.grounding}",
        ]
        if self.target:
            lines.append(f"- target: {self.target}")
        lines += [
            f"- mentions: {self.mentions}",
```
and a `deferred-at` line after `runs-since-confirmed`:
```python
            f"- runs-since-confirmed: {self.runs_since_confirmed}",
        ]
        if self.deferred_at >= 0:
            lines.append(f"- deferred-at: {self.deferred_at}")
        if self.retired:
```

In `parse_lessons.flush()`, pass the two new fields into `Lesson(...)`:
```python
                target=current.get("target", ""),
                deferred_at=int(current.get("deferred-at", "-1")),
```

Add fields to `Playbook` (after `dormancy_runs`):
```python
    apply_recurrences: int
    apply_confirmed: int
```

In `load_playbook`, after `run_tick, cap, dormancy = ...`:
```python
    apply_recurrences = int(state.group(4)) if state.group(4) else DEFAULT_APPLY_RECURRENCES
    apply_confirmed = int(state.group(5)) if state.group(5) else DEFAULT_APPLY_CONFIRMED
```
and pass them into the `Playbook(...)` constructor.

In `render_playbook`, extend the `STATE_RE.sub` replacement string:
```python
    preamble = STATE_RE.sub(
        f"<!-- playbook-state: run-tick={book.run_tick} cap={book.cap} "
        f"dormancy-runs={book.dormancy_runs} apply-recurrences={book.apply_recurrences} "
        f"apply-confirmed={book.apply_confirmed} -->",
        book.preamble,
    )
```

In `_default_preamble`, update the marker line to:
```python
        "<!-- playbook-state: run-tick=0 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 -->\n\n"
```

In `apply_delta`'s `add` branch, set the target from the op:
```python
                    grounding=str(op["grounding"]).strip(),
                    target=str(op.get("target", "")).strip(),
                    added=stamp,
```

In `apply_delta`'s `amend` branch, allow updating target (after the task_class update):
```python
            if str(op.get("target", "")).strip():
                lesson.target = str(op["target"]).strip()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_apply_lessons_delta.py -v`
Expected: PASS (all existing + 3 new).

- [ ] **Step 5: Commit**

```bash
git add scripts/apply_lessons_delta.py tests/test_apply_lessons_delta.py
git commit -m "feat(lessons): add target field and apply-thresholds to the playbook"
```

---

### Task 2: `defer` op

**Files:**
- Modify: `scripts/apply_lessons_delta.py`
- Test: `tests/test_apply_lessons_delta.py`

**Interfaces:**
- Produces: op `{"op": "defer", "id": <id>, "reason": <str>}` → sets `status="deferred"`, records `deferred_at` = current disposition count (recurrences for constellation, else confirmed).

- [ ] **Step 1: Write the failing tests**

```python
    def test_defer_requires_reason(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "defer", "id": "handoff-diff-command"}]},
                       expect_rc=1)

    def test_defer_sets_status_and_records_count(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})
        self.run_delta({"work_id": "i2", "ops": [
            {"op": "confirm", "id": "handoff-diff-command", "grounding": "g"},
            {"op": "confirm", "id": "handoff-diff-command", "grounding": "g"}]})
        self.run_delta({"work_id": "i3", "ops": [
            {"op": "defer", "id": "handoff-diff-command", "reason": "needs human"}]})
        lesson = self.m.load_playbook(self.file).active[0]
        self.assertEqual(lesson.status, "deferred")
        self.assertEqual(lesson.deferred_at, 2)
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_apply_lessons_delta.py -k defer -v`
Expected: FAIL (`unknown op 'defer'`).

- [ ] **Step 3: Implement**

In `validate_delta`, add `defer` to the allowed-op tuple and a reason check:
```python
        if kind not in ("add", "amend", "confirm", "disconfirm", "mention", "retire",
                        "apply", "export", "defer"):
            raise LessonsDeltaError(f"unknown op {kind!r}")
```
```python
        if kind == "defer" and not str(op.get("reason", "")).strip():
            raise LessonsDeltaError(f"defer {lesson_id}: reason is required")
```

In `apply_delta`, after the `retire` branch, add:
```python
        elif kind == "defer":
            count = lesson.recurrences if lesson.scope == "constellation" else lesson.confirmed
            lesson.status = "deferred"
            lesson.deferred_at = count
            lesson.history.append(f"deferred {stamp} at {count} — {op['reason']}")
            log.append(f"deferred lesson:{lesson_id} at {count} — {op['reason']}")
```

(`apply` and `export` are added in Tasks 3–4; adding them to the validate tuple now is harmless — they are validated and applied in those tasks.)

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_apply_lessons_delta.py -k defer -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/apply_lessons_delta.py tests/test_apply_lessons_delta.py
git commit -m "feat(lessons): defer op records status and deferral count"
```

---

### Task 3: `apply` op (non-constellation deletes; constellation refused)

**Files:**
- Modify: `scripts/apply_lessons_delta.py`
- Test: `tests/test_apply_lessons_delta.py`

**Interfaces:**
- Produces: op `{"op": "apply", "id": <id>, "applied_evidence": <str>, "target"?: <str>}`. Requires `applied_evidence`; resolves target from op or lesson. Non-constellation → deletes the lesson. Constellation → error.

- [ ] **Step 1: Write the failing tests**

```python
    def test_apply_requires_applied_evidence(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "apply", "id": "handoff-diff-command"}]},
                       expect_rc=1)

    def test_apply_deletes_non_constellation_lesson(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "apply", "id": "handoff-diff-command",
            "applied_evidence": "docs/agents/CREW_CONTEXT.md §Implementation Rules"}]})
        self.assertEqual(self.m.load_playbook(self.file).active, [])

    def test_apply_requires_a_target(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})  # no target
        self.run_delta({"work_id": "i2", "ops": [{"op": "apply", "id": "handoff-diff-command",
            "applied_evidence": "e"}]}, expect_rc=1)

    def test_apply_refuses_constellation(self):
        self.run_delta({"work_id": "i1", "ops": [add_op("engine-attest", "constellation",
            target="skills/_shared/global-everyone.md")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "apply", "id": "engine-attest",
            "applied_evidence": "e"}]}, expect_rc=1)
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_apply_lessons_delta.py -k apply -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

In `validate_delta`, add an applied_evidence check:
```python
        if kind == "apply" and not str(op.get("applied_evidence", "")).strip():
            raise LessonsDeltaError(f"apply {lesson_id}: applied_evidence citation is required")
```

In `apply_delta`, include `apply` in the retire-first ordering:
```python
    ordered = sorted(ops, key=lambda op: 0 if op["op"] in ("retire", "apply") else 1)
```

Add the `apply` branch (place before `defer`):
```python
        elif kind == "apply":
            if lesson.scope == "constellation":
                raise LessonsDeltaError(
                    f"apply {lesson_id}: constellation lessons cannot be applied in-project; "
                    "use export to queue the fix upstream"
                )
            effective_target = str(op.get("target", "")).strip() or lesson.target
            if not effective_target:
                raise LessonsDeltaError(
                    f"apply {lesson_id}: target required (set on the lesson or in the op)"
                )
            book.active.remove(lesson)
            log.append(
                f"applied lesson:{lesson_id} -> {effective_target} (paid; deleted) "
                f"— {op['applied_evidence']}"
            )
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_apply_lessons_delta.py -k apply -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/apply_lessons_delta.py tests/test_apply_lessons_delta.py
git commit -m "feat(lessons): apply op encodes-and-retires non-constellation lessons"
```

---

### Task 4: `export` op (constellation → exported + pinned)

**Files:**
- Modify: `scripts/apply_lessons_delta.py`
- Test: `tests/test_apply_lessons_delta.py`

**Interfaces:**
- Produces: op `{"op": "export", "id": <id>, "grounding": <CONSTELLATION_FEEDBACK citation>}`. Constellation only. Sets `status="exported"`, keeps the lesson.

- [ ] **Step 1: Write the failing tests**

```python
    def test_export_requires_grounding(self):
        self.run_delta({"work_id": "i1", "ops": [add_op("engine-attest", "constellation")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "export", "id": "engine-attest"}]},
                       expect_rc=1)

    def test_export_sets_exported_and_pins(self):
        self.run_delta({"work_id": "i1", "ops": [add_op("engine-attest", "constellation")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "export", "id": "engine-attest",
            "grounding": "CONSTELLATION_FEEDBACK.md 2026-06-27 engine-attest"}]})
        lesson = self.m.load_playbook(self.file).active[0]
        self.assertEqual(lesson.status, "exported")

    def test_export_refuses_non_constellation(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})  # handoff scope
        self.run_delta({"work_id": "i2", "ops": [{"op": "export", "id": "handoff-diff-command",
            "grounding": "g"}]}, expect_rc=1)
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_apply_lessons_delta.py -k export -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

In `validate_delta`, add a grounding check for export:
```python
        if kind == "export" and not str(op.get("grounding", "")).strip():
            raise LessonsDeltaError(f"export {lesson_id}: grounding (CONSTELLATION_FEEDBACK citation) required")
```

In `apply_delta`, add the `export` branch (before `defer`):
```python
        elif kind == "export":
            if lesson.scope != "constellation":
                raise LessonsDeltaError(
                    f"export {lesson_id}: only constellation-scoped lessons export upstream"
                )
            lesson.status = "exported"
            lesson.history.append(f"exported {stamp} — {op['grounding']}")
            log.append(
                f"exported lesson:{lesson_id} to CONSTELLATION_FEEDBACK "
                f"(pinned until upstream ships) — {op['grounding']}"
            )
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_apply_lessons_delta.py -v`
Expected: PASS (full file).

- [ ] **Step 5: Commit**

```bash
git add scripts/apply_lessons_delta.py tests/test_apply_lessons_delta.py
git commit -m "feat(lessons): export op queues constellation debt upstream and pins it"
```

---

### Task 5: `ripe_lessons()` + `--ripe` CLI

**Files:**
- Modify: `scripts/apply_lessons_delta.py`
- Test: `tests/test_apply_lessons_delta.py`

**Interfaces:**
- Produces: `ripe_lessons(book: Playbook) -> list[Lesson]` — threshold-crossed lessons lacking a terminal disposition. Used by the verifier (Task 6).

- [ ] **Step 1: Write the failing tests**

```python
    def _confirm(self, n, lid="handoff-diff-command"):
        for _ in range(n):
            self.run_delta({"work_id": "x", "ops": [{"op": "confirm", "id": lid, "grounding": "g"}]})

    def test_ripe_selects_confirmed_threshold_with_target(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self._confirm(3)
        ripe = self.m.ripe_lessons(self.m.load_playbook(self.file))
        self.assertEqual([l.lesson_id for l in ripe], ["handoff-diff-command"])

    def test_ripe_excludes_targetless_non_constellation(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})  # no target
        self._confirm(3)
        self.assertEqual(self.m.ripe_lessons(self.m.load_playbook(self.file)), [])

    def test_ripe_selects_constellation_recurrence(self):
        self.run_delta({"work_id": "i1", "ops": [add_op("engine-attest", "constellation")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "confirm", "id": "engine-attest", "grounding": "g"}]})
        ripe = self.m.ripe_lessons(self.m.load_playbook(self.file))
        self.assertEqual([l.lesson_id for l in ripe], ["engine-attest"])

    def test_ripe_suppresses_exported_and_fresh_defer(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self._confirm(3)
        self.run_delta({"work_id": "i2", "ops": [
            {"op": "defer", "id": "handoff-diff-command", "reason": "later"}]})
        self.assertEqual(self.m.ripe_lessons(self.m.load_playbook(self.file)), [])

    def test_ripe_refires_when_count_climbs_past_defer(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self._confirm(3)
        self.run_delta({"work_id": "i2", "ops": [
            {"op": "defer", "id": "handoff-diff-command", "reason": "later"}]})
        self._confirm(1)  # confirmed now 4 > deferred_at 3
        self.assertEqual([l.lesson_id for l in self.m.ripe_lessons(self.m.load_playbook(self.file))],
                         ["handoff-diff-command"])
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_apply_lessons_delta.py -k ripe -v`
Expected: FAIL (`module has no attribute 'ripe_lessons'`).

- [ ] **Step 3: Implement**

Add the function after `render_playbook`:
```python
def ripe_lessons(book: Playbook) -> list[Lesson]:
    """Threshold-ripe lessons still awaiting an apply/export/defer disposition."""
    ripe: list[Lesson] = []
    for lesson in book.active:
        if lesson.status == "charter-review":
            continue
        if lesson.scope == "constellation":
            if lesson.recurrences < book.apply_recurrences:
                continue
            if lesson.status == "exported":
                continue
            count = lesson.recurrences
        else:
            if lesson.confirmed < book.apply_confirmed:
                continue
            if not lesson.target:
                continue
            count = lesson.confirmed
        if lesson.status == "deferred" and lesson.deferred_at >= count:
            continue
        ripe.append(lesson)
    return ripe
```

Make `delta` optional and add `--ripe` in `main`:
```python
    parser.add_argument("delta", type=Path, nargs="?", help="JSON delta file with work_id, tick, ops")
    parser.add_argument("--ripe", action="store_true", help="list ripe-unpaid lessons and exit")
```
Right after `args = parser.parse_args(argv)`:
```python
    if args.ripe:
        book = load_playbook(args.file)
        for lesson in ripe_lessons(book):
            print(f"{lesson.lesson_id}\t{lesson.scope}\ttarget={lesson.target or 'CONSTELLATION_FEEDBACK.md'}")
        return 0
    if args.delta is None:
        parser.error("delta file is required unless --ripe is given")
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_apply_lessons_delta.py -v`
Expected: PASS (full file).

- [ ] **Step 5: Commit**

```bash
git add scripts/apply_lessons_delta.py tests/test_apply_lessons_delta.py
git commit -m "feat(lessons): ripe_lessons selector and --ripe emit"
```

---

### Task 6: `verify_lessons_applied.py` (the gate)

**Files:**
- Create: `scripts/verify_lessons_applied.py`
- Test: `tests/test_verify_lessons_applied.py`

**Interfaces:**
- Consumes: `apply_lessons_delta.load_playbook`, `apply_lessons_delta.ripe_lessons` (co-bundled in the same `scripts/` dir).
- Produces: `main(argv) -> int`; exit `0` = clear, `1` = unpaid ripe lessons.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_verify_lessons_applied.py`:
```python
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerifyLessonsAppliedTests(unittest.TestCase):
    def setUp(self):
        self.apply = _load("apply_lessons_delta")
        self.verify = _load("verify_lessons_applied")
        self.tmp = tempfile.TemporaryDirectory()
        self.file = Path(self.tmp.name) / "LESSONS.md"

    def tearDown(self):
        self.tmp.cleanup()

    def _apply(self, delta):
        p = Path(self.tmp.name) / "d.json"
        p.write_text(json.dumps(delta), encoding="utf-8")
        self.assertEqual(0, self.apply.main([str(p), "--file", str(self.file)]))

    def _add(self, **ov):
        op = {"op": "add", "id": "handoff-diff-command", "scope": "handoff",
              "task_class": "general-workflow", "statement": "s",
              "grounding": "AGENT_FEEDBACK.md i1"}
        op.update(ov)
        return op

    def test_clear_when_no_playbook(self):
        self.assertEqual(0, self.verify.main(["--file", str(self.file)]))

    def test_clear_when_no_ripe_lessons(self):
        self._apply({"work_id": "i1", "ops": [self._add()]})
        self.assertEqual(0, self.verify.main(["--file", str(self.file)]))

    def test_blocks_on_unpaid_ripe_lesson(self):
        self._apply({"work_id": "i1", "ops": [self._add(target="docs/agents/CREW_CONTEXT.md")]})
        for _ in range(3):
            self._apply({"work_id": "x", "ops": [
                {"op": "confirm", "id": "handoff-diff-command", "grounding": "g"}]})
        self.assertEqual(1, self.verify.main(["--file", str(self.file)]))

    def test_clear_after_apply(self):
        self._apply({"work_id": "i1", "ops": [self._add(target="docs/agents/CREW_CONTEXT.md")]})
        for _ in range(3):
            self._apply({"work_id": "x", "ops": [
                {"op": "confirm", "id": "handoff-diff-command", "grounding": "g"}]})
        self._apply({"work_id": "x2", "ops": [
            {"op": "apply", "id": "handoff-diff-command", "applied_evidence": "edited CREW_CONTEXT"}]})
        self.assertEqual(0, self.verify.main(["--file", str(self.file)]))
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_verify_lessons_applied.py -v`
Expected: FAIL (module file does not exist).

- [ ] **Step 3: Implement**

Create `scripts/verify_lessons_applied.py`:
```python
#!/usr/bin/env python
"""Feedback-step gate: refuse advance while any threshold-ripe lesson is unpaid.

A lesson is unpaid when its scope threshold is crossed and it has no terminal
disposition this cycle (neither applied/exported nor deferred at/above its current
count). Reuses the ripeness model from apply_lessons_delta. Exit 0 = clear, 1 = blocked.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_lessons_delta import LessonsDeltaError, load_playbook, ripe_lessons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path(".agent-work/LESSONS.md"))
    args = parser.parse_args(argv)

    if not args.file.exists():
        print("lessons gate: no playbook — clear")
        return 0
    try:
        book = load_playbook(args.file)
    except LessonsDeltaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    ripe = ripe_lessons(book)
    if not ripe:
        print("lessons gate: clear — no ripe lesson awaiting apply-or-defer")
        return 0

    print("lessons gate: BLOCKED — ripe lesson(s) need apply / export / defer:", file=sys.stderr)
    for lesson in ripe:
        target = lesson.target or "CONSTELLATION_FEEDBACK.md"
        print(f"  - {lesson.lesson_id} ({lesson.scope}) -> {target}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_verify_lessons_applied.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/verify_lessons_applied.py tests/test_verify_lessons_applied.py
git commit -m "feat(lessons): verify_lessons_applied gate over ripe lessons"
```

---

### Task 7: Wire the gate live (bundle + postconditions + latitude class)

**Files:**
- Modify: `scripts/install_constellation.py:74-84` (`SKILL_SCRIPT_BUNDLES`)
- Modify: `skills/commander/templates/COMMANDER_SPINE.template.json` (feedback task)
- Modify: `skills/admiral/templates/ADMIRAL_SPINE.template.json` (closeout task)
- Modify: `skills/admiral/templates/LATITUDE_CONTRACT.template.md`
- Test: `tests/test_install_constellation.py`

**Interfaces:**
- Consumes: `scripts/verify_lessons_applied.py` (Task 6).

- [ ] **Step 1: Write the failing test**

Append to `tests/test_install_constellation.py` (inside `InstallConstellationTests`):
```python
    def test_lessons_gate_verifier_bundled_into_commander_and_admiral(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                            "--skills", "commander", "admiral"], env={}, out=lambda _: None)
            for skill in ("constellation-commander", "constellation-admiral"):
                self.assertTrue(
                    (target_root / skill / "scripts" / "verify_lessons_applied.py").exists())
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_install_constellation.py -k lessons_gate -v`
Expected: FAIL (script not bundled).

- [ ] **Step 3: Bundle the verifier**

In `scripts/install_constellation.py`, add `"verify_lessons_applied.py"` to the `commander` and `admiral` tuples in `SKILL_SCRIPT_BUNDLES`:
```python
    "admiral": ("checklist_engine.py", "init_work_area.py", "verify_agent_feedback.py", "verify_state_note.py", "apply_lessons_delta.py", "verify_lessons_applied.py"),
    ...
    "commander": ("checklist_engine.py", "init_work_area.py", "verify_agent_feedback.py", "verify_state_note.py", "run_crew.py", "recover_crews.py", "apply_lessons_delta.py", "verify_lessons_applied.py"),
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_install_constellation.py -k lessons_gate -v`
Expected: PASS.

- [ ] **Step 5: Add the feedback-step postcondition + imperative**

In `skills/commander/templates/COMMANDER_SPINE.template.json`, in the `feedback` task: append a second postcondition to its `postconditions` array (after `c1`):
```json
        {"id": "c2", "statement": "no threshold-ripe lesson left unpaid — each applied to its target, exported upstream, or explicitly deferred with a reason", "check": {"kind": "command", "command": "python <commander-skill-dir>/scripts/verify_lessons_applied.py --file .agent-work/LESSONS.md"}, "satisfied": false}
```
In the same task's `imperative`, replace this exact sentence (the whole sentence, through the closing `slug).`):
`Route concrete interface fixes to the closeout Template Update Candidates table; lessons flagged charter-review go to a Charter refresh; constellation-scoped lessons also append to .agent-work/CONSTELLATION_FEEDBACK.md — carry the originating lesson id in that entry's Lesson field so the upstream sweep groups recurrences on stable identity (reword a recurring finding via amend, never a new slug).`
with:
`Then settle every threshold-ripe lesson (python <commander-skill-dir>/scripts/apply_lessons_delta.py --ripe --file .agent-work/LESSONS.md): for each, APPLY it (make the bounded edit to its target — a thin docs/agents/* delta or a project template working copy — confirmed by the human, then an apply op deletes it as paid), or for a constellation lesson EXPORT it (append to .agent-work/CONSTELLATION_FEEDBACK.md — carry the originating lesson id in that entry's Lesson field so the upstream sweep groups recurrences on stable identity, rewording a recurring finding via amend not a new slug — then an export op marks it exported and pinned), or DEFER it with a reason (a broad or contradictory doctrine shift routes to a Charter refresh; an autonomous run without that latitude defers 'needs human'). Lessons flagged charter-review go to a Charter refresh.`

- [ ] **Step 6: Add the Admiral closeout postcondition**

In `skills/admiral/templates/ADMIRAL_SPINE.template.json`, in the `closeout` task, append a postcondition:
```json
        {"id": "cL", "statement": "no threshold-ripe lesson left unpaid across the epic (applied, exported, or deferred)", "check": {"kind": "command", "command": "python <admiral-skill-dir>/scripts/verify_lessons_applied.py --file .agent-work/LESSONS.md"}, "satisfied": false}
```
(Read the closeout task first; reuse its existing postcondition-id style — if ids are `c1..cN`, use the next `cN+1` instead of `cL`.)

- [ ] **Step 7: Add the latitude decision class**

In `skills/admiral/templates/LATITUDE_CONTRACT.template.md`, in the decision-classes section, add a row/bullet:
```markdown
- **Apply a lesson / fold doctrine** — may the fleet apply a ripe lesson to a project doc/template (and export constellation debt) without surfacing, or must each apply be surfaced? Default: surface. When delegated, applies are logged as rulings in ADMIRAL_LOG; constellation lessons are always exported, never silently confirmed.
```

- [ ] **Step 8: Validate JSON and run installer tests**

Run: `python -c "import json,glob; [json.load(open(f,encoding='utf-8')) for f in glob.glob('skills/**/*.json',recursive=True)]; print('ok')"`
Expected: `ok`
Run: `python -m pytest tests/test_install_constellation.py -v`
Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add scripts/install_constellation.py skills/commander/templates/COMMANDER_SPINE.template.json skills/admiral/templates/ADMIRAL_SPINE.template.json skills/admiral/templates/LATITUDE_CONTRACT.template.md tests/test_install_constellation.py
git commit -m "feat(lessons): wire the apply-or-defer gate into feedback and admiral closeout"
```

---

### Task 8: Documentation — LESSONS template + retire the closeout table

**Files:**
- Modify: `skills/workbench/templates/LESSONS.template.md`
- Modify: `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md`

**Interfaces:** none (docs only).

- [ ] **Step 1: Document the new mechanism in `LESSONS.template.md`**

Update the marker line at the top to include the thresholds:
`<!-- playbook-state: run-tick=0 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 -->`

Add to the "Rules the apply script enforces" list:
```markdown
- **Apply-or-defer is forced at feedback.** A lesson is *ripe* when its scope threshold is
  crossed — non-constellation `confirmed ≥ apply-confirmed` (default 3) with a `target`, or
  constellation `recurrences ≥ apply-recurrences` (default 1). The `feedback` step refuses to
  advance (via `verify_lessons_applied.py`) until every ripe lesson is settled: **apply** it
  (`apply` op — edit the `target`, then the lesson is deleted as paid), **export** it
  (`export` op — constellation only; status `exported`, pinned until shipped upstream), or
  **defer** it (`defer` op — records `deferred-at`; re-fires only when the count climbs).
```
Add to the lesson-shape block:
```markdown
- target: <editable artifact this applies to: docs/agents/*, a template, skills/_shared/global-*, or CONSTELLATION_FEEDBACK.md> (optional)
- status: active | charter-review | recurrence-debt | deferred | exported
```

- [ ] **Step 2: Retire the Template Update Candidates table in `WORKFLOW_CLOSEOUT.template.md`**

Delete the `## Template Update Candidates` heading and its table/paragraph (lines 24–32), and replace with:
```markdown
## Lesson dispositions

Template/interface and doctrine fixes are now lessons carrying a `target`, settled at the
Commander `feedback` step by the forced apply-or-defer gate (`verify_lessons_applied.py`) — not
a separate advisory table. Confirm here only that the gate passed: every ripe lesson was
applied, exported, or deferred with a reason.
```

- [ ] **Step 3: Validate and commit**

Run: `python -m pytest tests/ -q`
Expected: PASS (full suite).
```bash
git add skills/workbench/templates/LESSONS.template.md skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md
git commit -m "docs(lessons): document apply-or-defer; retire the advisory closeout table"
```

---

## Final verification

- [ ] Run the full suite: `python -m pytest tests/ -q` — expect all green.
- [ ] Validate all template JSON parses (Task 7, Step 8 command).
- [ ] Reinstall user-scope and confirm the verifier is bundled and the feedback postcondition path rewrote:
  `python scripts/install_constellation.py --agent claude --scope user --force` then check
  `~/.claude/skills/constellation-commander/scripts/verify_lessons_applied.py` exists and the installed
  `COMMANDER_SPINE.template.json` feedback `c2` command contains an absolute path (no `<commander-skill-dir>`).
