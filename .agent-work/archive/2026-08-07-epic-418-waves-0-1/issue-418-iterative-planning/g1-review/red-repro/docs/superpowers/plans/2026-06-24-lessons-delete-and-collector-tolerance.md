# Lessons delete-not-mark + collector format tolerance — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the lessons playbook's unread Dormant graveyard with hard deletion, and make the feedback collector see prose-format exports it currently drops — while removing the never-fired `resolved`/auto-close bookkeeping and keeping the human-gated inbox.

**Architecture:** Two Python scripts change (`apply_lessons_delta.py`, `collect_feedback.py`) plus three doc/template files. The engine's `retire` op becomes a delete and the `## Dormant` section disappears (loads of legacy files garbage-collect it on first write); the collector gains a second parser for the legacy prose export shape; the collector loses its `resolved` sidecar + issue auto-close. Skills/templates are reworded to teach "delete handled lessons." A final operational task seeds field-format template tracking into the three prose-format repos.

**Tech Stack:** Python 3 (stdlib only — `re`, `json`, `dataclasses`, `pathlib`), `unittest`. Tests run with `py -m pytest`. Windows host; the Bash tool is Git Bash.

## Global Constraints

- Python: stdlib only, no new dependencies. Match existing style in each script.
- Run tests with `py -m pytest tests/<file> -q` from the repo root `C:\Programs\constellation-skills`.
- The op name stays `retire` (now meaning hard delete) — do NOT rename it to `delete`. (Spec Decision D5.)
- The playbook state marker keeps the name `dormancy-runs` and the lesson field `runs-since-confirmed` — they now drive deletion timing, not demotion. Do not rename them (would break existing playbooks' state markers).
- `constellation`-scoped lessons are PINNED from tick auto-aging (never auto-deleted); they are removed only by an explicit `retire`.
- Commit after each task with the task's own commit. Frequent commits.
- Branch is `constellation/lessons-delete-and-collector-tolerance` (already created).

---

## File Structure

- `scripts/apply_lessons_delta.py` — engine. `retire`→delete; drop Dormant; tick deletes (pins constellation). (Task 1)
- `tests/test_apply_lessons_delta.py` — engine tests, reworked for delete semantics. (Task 1)
- `scripts/collect_feedback.py` — add prose parser (Task 2); remove `resolved`/auto-close (Task 3).
- `tests/test_feedback_tooling.py` — add prose tests (Task 2); remove resolved/close tests (Task 3).
- `skills/workbench/templates/LESSONS.template.md` — delete-semantics preamble, no Dormant section. (Task 4)
- `skills/lessons-auditor/templates/LESSON_CANDIDATES.template.md` — "Active" not "Active and Dormant". (Task 4)
- `skills/lessons-auditor/templates/LESSONS_AUDIT.template.json` — "(Active)" not "(Active and Dormant)". (Task 4)
- (Operational, post-merge) the three prose repos get template tracking seeded. (Task 5)

---

## Task 1: Engine — `retire` deletes, Dormant removed, tick deletes (pins constellation)

**Files:**
- Modify: `scripts/apply_lessons_delta.py` (`Playbook`, `load_playbook`, `render_playbook`, `apply_delta`, `main`)
- Test: `tests/test_apply_lessons_delta.py`

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `Playbook` dataclass has fields `run_tick, cap, dormancy_runs, preamble, active` (NO `dormant`).
  - `Playbook.find(lesson_id) -> Lesson | None` (returns the Lesson directly, NOT a `(lesson, section)` tuple).
  - `retire` op removes a lesson from `active` entirely; requires `reason`.
  - tick deletes any non-constellation active lesson with `runs_since_confirmed > dormancy_runs`; constellation lessons are skipped (pinned).
  - `load_playbook` tolerates a legacy `## Dormant` section by parsing and discarding it.

- [ ] **Step 1: Rewrite the Dormant-dependent tests for delete semantics**

In `tests/test_apply_lessons_delta.py`, replace the three Dormant-era tests below with delete-era versions. Replace `test_cap_enforced_and_retire_before_add`:

```python
    def test_cap_enforced_and_retire_before_add(self):
        ops = [add_op(f"lesson-{i}") for i in range(20)]
        self.run_delta({"work_id": "seed", "ops": ops})
        self.run_delta({"work_id": "over", "ops": [add_op("lesson-21")]}, expect_rc=1)
        # retire-before-add in one delta succeeds; the retired lesson is GONE (deleted)
        self.run_delta(
            {
                "work_id": "swap",
                "ops": [
                    add_op("lesson-21"),
                    {"op": "retire", "id": "lesson-0", "reason": "superseded"},
                ],
            }
        )
        book = self.m.load_playbook(self.file)
        ids = [l.lesson_id for l in book.active]
        self.assertEqual(len(book.active), 20)
        self.assertNotIn("lesson-0", ids)        # deleted, not parked
        self.assertIn("lesson-21", ids)
        self.assertFalse(hasattr(book, "dormant"))
```

Replace `test_tick_auto_demotes_unconfirmed` with:

```python
    def test_tick_auto_deletes_unconfirmed(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        for i in range(11):
            self.run_delta({"work_id": f"run-{i}", "tick": True})
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active, [])        # deleted after dormancy window
        self.assertNotIn("## Dormant", self.file.read_text(encoding="utf-8"))
```

Replace `test_confirm_revives_dormant` with a re-add-after-delete test:

```python
    def test_retire_deletes_and_id_is_reusable(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta(
            {"work_id": "issue-2",
             "ops": [{"op": "retire", "id": "handoff-diff-command", "reason": "internalized"}]}
        )
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active, [])
        # the id is free again — re-adding (relearning) just works, no collision
        self.run_delta({"work_id": "issue-3", "ops": [add_op()]})
        book = self.m.load_playbook(self.file)
        self.assertEqual([l.lesson_id for l in book.active], ["handoff-diff-command"])
```

Replace `test_constellation_confirm_revives_dormant_as_debt` with a pin test:

```python
    def test_constellation_pinned_from_auto_delete(self):
        self.run_delta(
            {"work_id": "issue-1", "ops": [add_op("worktree-isolation", scope="constellation")]}
        )
        for i in range(12):
            self.run_delta({"work_id": f"run-{i}", "tick": True})
        book = self.m.load_playbook(self.file)
        # constellation debt is pinned: unpaid upstream defect is never auto-deleted
        self.assertEqual([l.lesson_id for l in book.active], ["worktree-isolation"])
```

Replace `test_constellation_debt_paid_by_retire` body assertions (retire now deletes):

```python
    def test_constellation_debt_paid_by_retire(self):
        self.run_delta(
            {"work_id": "issue-1", "ops": [add_op("fixed-upstream", scope="constellation")]}
        )
        self._confirm("fixed-upstream", "issue-2")
        self.run_delta(
            {"work_id": "issue-3",
             "ops": [{"op": "retire", "id": "fixed-upstream", "reason": "fixed upstream in PR #99"}]}
        )
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active, [])        # deleted once paid
        self.assertNotIn("fixed-upstream", self.file.read_text(encoding="utf-8"))
```

Add a legacy-migration test at the end of the class (before `if __name__`):

```python
    def test_legacy_dormant_section_discarded_on_load(self):
        # An existing playbook with a populated ## Dormant section must load (active
        # preserved) and render WITHOUT the graveyard — GC'd on first write.
        self.file.write_text(
            "# Lessons Playbook\n\n"
            "<!-- playbook-state: run-tick=3 cap=20 dormancy-runs=10 -->\n\n"
            "## Active\n\n"
            "### lesson:live-one\n"
            "- scope: project\n- task-class: general-workflow\n"
            "- statement: still active\n- grounding: g\n"
            "- mentions: 1\n- confirmed: 0\n- disconfirmed: 0\n"
            "- status: active\n- added: 2026-06-01 (x)\n"
            "- last-confirmed: none\n- runs-since-confirmed: 0\n\n"
            "## Dormant\n\n"
            "### lesson:old-ghost\n"
            "- scope: project\n- task-class: general-workflow\n"
            "- statement: parked long ago\n- grounding: g\n"
            "- mentions: 1\n- confirmed: 0\n- disconfirmed: 0\n"
            "- status: active\n- added: 2026-05-01 (y)\n"
            "- last-confirmed: none\n- runs-since-confirmed: 99\n"
            "- retired: 2026-05-02 (y) — auto-dormant\n",
            encoding="utf-8",
        )
        book = self.m.load_playbook(self.file)
        self.assertEqual([l.lesson_id for l in book.active], ["live-one"])
        rendered = self.m.render_playbook(book)
        self.assertNotIn("## Dormant", rendered)
        self.assertNotIn("old-ghost", rendered)
```

- [ ] **Step 2: Run the rewritten tests to verify they fail**

Run: `py -m pytest tests/test_apply_lessons_delta.py -q`
Expected: FAIL — the new tests reference delete behavior the engine doesn't have yet (e.g. `book.dormant` still exists, `retire` still parks, tick still demotes).

- [ ] **Step 3: Drop `dormant` from `Playbook` and simplify `find`**

In `scripts/apply_lessons_delta.py`, replace the `Playbook` dataclass:

```python
@dataclass
class Playbook:
    run_tick: int
    cap: int
    dormancy_runs: int
    preamble: str
    active: list[Lesson]

    def find(self, lesson_id: str) -> Lesson | None:
        for lesson in self.active:
            if lesson.lesson_id == lesson_id:
                return lesson
        return None
```

- [ ] **Step 4: Make `load_playbook` tolerate-and-discard a legacy Dormant section**

Replace the body of `load_playbook` from the `active_idx = ...` line through the `return Playbook(...)`:

```python
    active_idx = text.find("\n## Active")
    if active_idx == -1:
        raise LessonsDeltaError(f"playbook missing '## Active' section: {path}")
    dormant_idx = text.find("\n## Dormant")

    preamble = text[:active_idx].rstrip("\n")
    if dormant_idx != -1 and dormant_idx > active_idx:
        # Legacy file: parse the Active slice up to the graveyard, discard the
        # graveyard entirely (it is GC'd on the next render).
        active_block = text[active_idx + len("\n## Active") : dormant_idx]
    else:
        active_block = text[active_idx + len("\n## Active") :]

    return Playbook(
        run_tick=run_tick,
        cap=cap,
        dormancy_runs=dormancy,
        preamble=preamble,
        active=parse_lessons(active_block),
    )
```

Also change the missing-file seed line in `load_playbook` (top of the function):

```python
    if not path.exists():
        text = _default_preamble() + "\n## Active\n"
```

- [ ] **Step 5: Drop the Dormant section from `render_playbook`**

Replace the body of `render_playbook` after the `preamble = STATE_RE.sub(...)` block:

```python
    parts = [preamble, "", "## Active", ""]
    for lesson in book.active:
        parts.append(lesson.render())
        parts.append("")
    return "\n".join(parts).rstrip("\n") + "\n"
```

- [ ] **Step 6: Rework `apply_delta` — retire deletes, confirm has no revive, tick deletes (pins constellation)**

In `apply_delta`, replace the per-op `found`/`section` handling. Change the lookup and `add` block:

```python
    for op in ordered:
        kind, lesson_id = op["op"], op["id"]
        lesson = book.find(lesson_id)

        if kind == "add":
            if lesson:
                raise LessonsDeltaError(f"add {lesson_id}: id already exists")
            if len(book.active) >= book.cap:
                raise LessonsDeltaError(
                    f"add {lesson_id}: active cap {book.cap} reached — retire before adding"
                )
            book.active.append(
                Lesson(
                    lesson_id=lesson_id,
                    scope=op["scope"],
                    task_class=str(op["task_class"]).strip(),
                    statement=str(op["statement"]).strip(),
                    grounding=str(op["grounding"]).strip(),
                    added=stamp,
                )
            )
            log.append(f"added lesson:{lesson_id}")
            continue

        if not lesson:
            raise LessonsDeltaError(f"{kind} {lesson_id}: no such lesson")
```

Replace the `confirm` block (drop the dormant-revive branch entirely):

```python
        if kind == "confirm":
            lesson.mentions += 1
            lesson.last_confirmed = stamp
            lesson.runs_since_confirmed = 0
            if lesson.scope == "constellation":
                lesson.recurrences += 1
                lesson.status = "recurrence-debt"
                lesson.history.append(
                    f"recurred {stamp} (constellation debt, not trust) — {op['grounding']}"
                )
                log.append(
                    f"recurrence-debt lesson:{lesson_id} (now {lesson.recurrences} unfixed "
                    "recurrence(s)) — export to CONSTELLATION_FEEDBACK and fix upstream; "
                    "confirming a constellation defect logs debt, not trust"
                )
            else:
                lesson.confirmed += 1
                lesson.history.append(f"confirmed {stamp} — {op['grounding']}")
                if lesson.status == "charter-review" and lesson.confirmed > lesson.disconfirmed:
                    lesson.status = "active"
                log.append(f"confirmed lesson:{lesson_id} (now {lesson.confirmed})")
```

Replace the `retire` block (was the `elif kind == "retire":` branch):

```python
        elif kind == "retire":
            book.active.remove(lesson)
            log.append(f"deleted lesson:{lesson_id} — {op['reason']}")
```

(The `disconfirm` and `mention` branches are unchanged — they already operate on `lesson` directly.)

Replace the tick block at the end of `apply_delta`:

```python
    if tick:
        book.run_tick += 1
        expired: list[Lesson] = []
        for lesson in book.active:
            lesson.runs_since_confirmed += 1
            # Constellation lessons are pinned: shared-machinery debt persists until
            # fixed upstream and retired by hand — never silently auto-deleted.
            if lesson.scope == "constellation":
                continue
            if lesson.runs_since_confirmed > book.dormancy_runs:
                expired.append(lesson)
        for lesson in expired:
            book.active.remove(lesson)
            log.append(
                f"auto-deleted lesson:{lesson.lesson_id} "
                f"(unconfirmed for {book.dormancy_runs} runs)"
            )
        log.append(f"tick -> run {book.run_tick}")

    return log
```

- [ ] **Step 7: Fix the `main` summary line (no dormant count)**

In `main`, replace the playbook summary print:

```python
    print(
        f"playbook: {len(book.active)} active (cap {book.cap}, run {book.run_tick})"
    )
```

- [ ] **Step 8: Run the full engine test file to verify it passes**

Run: `py -m pytest tests/test_apply_lessons_delta.py -q`
Expected: PASS (all tests, including the round-trip and constellation-debt tests that were already present).

- [ ] **Step 9: Commit**

```bash
git add scripts/apply_lessons_delta.py tests/test_apply_lessons_delta.py
git commit -m "Lessons engine: retire deletes, drop the Dormant graveyard

retire now removes a lesson outright; the unread, drift-causing Dormant
section is gone. Tick auto-aging deletes unconfirmed lessons but pins
constellation debt. load_playbook discards a legacy Dormant section so old
playbooks GC it on first write.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Collector — parse the legacy prose export format

**Files:**
- Modify: `scripts/collect_feedback.py` (add `PROSE_HEADING_RE`, `INLINE_FIELD_RE`, `_extract_inline_fields`, `_map_prose_label`, `parse_prose_findings`; extend `iter_findings`)
- Test: `tests/test_feedback_tooling.py` (add to `CollectFeedbackTests`)

**Interfaces:**
- Consumes: `parse_entries`, `_is_finding`, `fingerprint` (unchanged).
- Produces:
  - `parse_prose_findings(text) -> list[dict]` — entries in the same dict shape as `parse_entries` (`heading`, `candidate`, optional `lesson`/`observed`/`proposal`/`cost`/`grounding`/`confidence`).
  - `iter_findings(text)` returns field-format findings followed by prose-format findings.
- Note: prose parsing buys VISIBILITY, not cross-repo grouping. Two repos that named the same defect differently (no shared `Lesson:` id) stay two findings — that's the human-naming gap the field-format `Lesson:` id closes going forward, not something the parser can infer.

- [ ] **Step 1: Write the failing prose-parsing tests**

Add these tests to `class CollectFeedbackTests` in `tests/test_feedback_tooling.py`:

```python
    def test_prose_finding_surfaced_network_elo_shape(self):
        # `### Lesson: <slug>  (confidence: x)` heading + standalone **Field:** lines
        root = Path(self.tmp.name) / "elo"
        (root / ".agent-work").mkdir(parents=True)
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
            "# Constellation Feedback\n\n"
            "## 2026-06-20 — from `wc2026-pipeline`\n\n"
            "### Lesson: worktree-isolation-not-real-on-windows  (confidence: high)\n"
            "**Observed:** isolation worktree did not create per-agent dirs on Windows.\n"
            "**Recommended platform guidance:** verify isolation before parallel dispatch.\n",
            encoding="utf-8",
        )
        new, open_unresolved = self.m.collect([root])
        self.assertEqual(len(new), 1)
        first = next(iter(new.values()))[0][1]
        self.assertEqual(first["candidate"], "worktree-isolation-not-real-on-windows  (confidence: high)")
        self.assertIn("did not create per-agent dirs", first["observed"])
        self.assertIn("verify isolation", first["proposal"])

    def test_prose_finding_fingerprints_on_inline_lesson_id(self):
        # story_time shape: `### <slug> (scope)` + inline **Lesson:** id + **Upstream fix:**
        root = Path(self.tmp.name) / "story"
        (root / ".agent-work").mkdir(parents=True)
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
            "# Constellation Feedback\n\n"
            "## epic-1 (story_time, 2026-06-22)\n\n"
            "### worktree-isolation-not-guaranteed (constellation)\n"
            "Agent-tool isolation did not create separate dirs and subagents collided. "
            "**Upstream fix:** make Agent worktree isolation real. "
            "**Lesson:** worktree-isolation-not-guaranteed.\n",
            encoding="utf-8",
        )
        new, _ = self.m.collect([root])
        self.assertEqual(len(new), 1)
        fp = next(iter(new))
        self.assertEqual(fp, self.m._hash12("lesson:worktree-isolation-not-guaranteed"))
        first = next(iter(new.values()))[0][1]
        self.assertIn("subagents collided", first["observed"])
        self.assertIn("make Agent worktree isolation real", first["proposal"])

    def test_prose_contentless_subblock_not_a_finding(self):
        root = Path(self.tmp.name) / "empty"
        (root / ".agent-work").mkdir(parents=True)
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
            "# Constellation Feedback\n\n"
            "## Template-delta recommendations\n\n"
            "### just a heading with no fields and no prose body\n",
            encoding="utf-8",
        )
        self.assertEqual(self.m.collect([root]), ({}, {}))

    def test_field_and_prose_not_double_counted(self):
        # A file mixing a field-format block and a prose block yields exactly 2.
        root = Path(self.tmp.name) / "mixed"
        (root / ".agent-work").mkdir(parents=True)
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
            FEEDBACK_ENTRY.format(project="mixed")
            + "\n## epic-2 (mixed, 2026-06-23)\n\n"
            "### powershell-heredoc-use-here-string (constellation)\n"
            "PR bodies fail with heredoc. **Upstream fix:** prescribe gh pr create -F file. "
            "**Lesson:** powershell-heredoc-use-here-string.\n",
            encoding="utf-8",
        )
        new, _ = self.m.collect([root])
        self.assertEqual(len(new), 2)
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `py -m pytest tests/test_feedback_tooling.py -q -k "prose or double_counted"`
Expected: FAIL — `collect` drops the prose blocks (returns 0 findings), so the count assertions fail.

- [ ] **Step 3: Add the prose parser and wire it into `iter_findings`**

In `scripts/collect_feedback.py`, add near the other regexes (after `FIELD_RE`):

```python
PROSE_HEADING_RE = re.compile(r"^### (.+)$", re.MULTILINE)
# Inline bold field label, e.g. **Observed:** / **Upstream fix:** — value runs to
# the next such label or end of the sub-block.
INLINE_FIELD_RE = re.compile(r"\*\*([A-Z][A-Za-z /]+?):\*\*\s*")

# Map a prose field label (lowercased) to the canonical finding key.
_PROSE_LABELS = {
    "observed": "observed",
    "upstream fix": "proposal",
    "proposal": "proposal",
    "lesson": "lesson",
    "impact": "cost",
    "cost": "cost",
    "grounding": "grounding",
    "confidence": "confidence",
}


def _map_prose_label(label: str) -> str | None:
    if label.startswith("recommended"):
        return "proposal"
    return _PROSE_LABELS.get(label)


def _extract_inline_fields(body: str) -> tuple[dict[str, str], str]:
    """Pull `**Label:** value` spans out of a prose sub-block.

    Returns (fields, leading_prose) where leading_prose is the text before the
    first label (used as `observed` when no explicit **Observed:** is present).
    """
    matches = list(INLINE_FIELD_RE.finditer(body))
    if not matches:
        return {}, body.strip()
    fields: dict[str, str] = {}
    for i, m in enumerate(matches):
        label = m.group(1).strip().lower()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        value = body[m.end() : end].strip().strip(".").strip()
        if label not in fields:
            fields[label] = value
    return fields, body[: matches[0].start()].strip()
```

Add the finding parser:

```python
def parse_prose_findings(text: str) -> list[dict[str, str]]:
    """Parse the legacy prose export shape into finding dicts.

    A finding is a `### <label>` sub-heading under a `## <epic>` block. The label
    (minus a leading `Lesson:` prefix) is the candidate slug; inline `**Field:**`
    spans and the leading paragraph supply observed/proposal/lesson/etc. The
    field-format parser (`parse_entries`) ignores these blocks (they carry no
    `- **Field:**` list lines), so the two parsers never double-count.
    """
    findings: list[dict[str, str]] = []
    blocks = list(ENTRY_HEADING_RE.finditer(text))
    for i, block_match in enumerate(blocks):
        block_end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        block = text[block_match.start() : block_end]
        subs = list(PROSE_HEADING_RE.finditer(block))
        for j, sub in enumerate(subs):
            sub_end = subs[j + 1].start() if j + 1 < len(subs) else len(block)
            body = block[sub.end() : sub_end]
            heading = sub.group(1).strip()
            candidate = re.sub(r"^Lesson:\s*", "", heading)
            fields, lead = _extract_inline_fields(body)
            entry: dict[str, str] = {"heading": heading, "candidate": candidate}
            for label, value in fields.items():
                key = _map_prose_label(label)
                if key and value and key not in entry:
                    entry[key] = value
            if "observed" not in entry and lead:
                entry["observed"] = lead
            findings.append(entry)
    return findings
```

Replace `iter_findings`:

```python
def iter_findings(text: str) -> list[dict[str, str]]:
    """Findings in either export shape (content-less blocks dropped)."""
    field = [e for e in parse_entries(text) if _is_finding(e)]
    prose = [e for e in parse_prose_findings(text) if _is_finding(e)]
    return field + prose
```

- [ ] **Step 4: Run the collector tests to verify they pass**

Run: `py -m pytest tests/test_feedback_tooling.py -q`
Expected: PASS (new prose tests plus all existing CollectFeedback/Inbox tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/collect_feedback.py tests/test_feedback_tooling.py
git commit -m "Collector: parse the legacy prose feedback format

iter_findings now also reads ### sub-heading findings with inline **Field:**
spans, so prose-format exports (story_time, network_elo, st-cleanroom) are no
longer silently dropped. Visibility only — cross-repo grouping still needs a
shared Lesson: id.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Collector — drop the `resolved` sidecar + issue auto-close

**Files:**
- Modify: `scripts/collect_feedback.py` (`load_sidecar`, `collect`, remove `mark_resolved`/`resolved_across`/`gh_close_issue`, rework `sync_issues`/`file_issues`/`_file_issues_cli`/`main`)
- Test: `tests/test_feedback_tooling.py` (remove resolved/close tests; fix `sync_issues` call sites)

**Interfaces:**
- Produces:
  - `load_sidecar(root) -> {"collected": {...}}` (no `resolved` key).
  - `collect(roots)` no longer skips a `resolved` finding (there is no resolved state).
  - `sync_issues(merged, *, inbox_path, filer=..., commenter=..., include_singles=False, confirm=False, labels=(), repo=None)` — NO `resolved` positional, NO `closer`; returns dict with `would_file/would_update/filed/updated` only (no `would_close`/`closed`).
  - `file_issues(merged, *, inbox_path, filer=..., include_singles=False, confirm=False, labels=(), repo=None)`.
  - No `--resolve`/`--note` CLI flags.

- [ ] **Step 1: Remove the resolved/close tests and fix call sites**

In `tests/test_feedback_tooling.py`:

Delete these test methods entirely:
- `CollectFeedbackTests.test_resolved_entries_disappear`
- `CollectFeedbackTests.test_legacy_resolved_fingerprint_still_resolves`
- `InboxLifecycleTests.test_resolved_finding_is_auto_closed`
- `InboxLifecycleTests.test_closed_issue_stays_closed_even_if_it_recurs`
- `InboxLifecycleTests.test_resolved_across_unions_project_notes`

In the two surviving `InboxLifecycleTests` methods, drop the now-removed `resolved` positional arg from every `sync_issues(...)` call. Replace `test_recurrence_growth_comments_and_watermarks`:

```python
    def test_recurrence_growth_comments_and_watermarks(self):
        filer, commenter = self._filer(), self._recorder()
        self._file_once(filer)  # filed at 2x / 2 projects
        self._project("gamma", FEEDBACK_ENTRY.format(project="gamma"))  # now 3x / 3 projects
        res = self.m.sync_issues(
            self._merged(), inbox_path=self.inbox, filer=filer, commenter=commenter, confirm=True
        )
        self.assertEqual(res["filed"], [])
        self.assertEqual(len(res["updated"]), 1)
        self.assertEqual(len(commenter.calls), 1)
        self.assertEqual(len(filer.calls), 1)
        ledger = json.loads(self.inbox.read_text(encoding="utf-8"))
        (_, rec), = ledger["filed"].items()
        self.assertEqual(rec["occurrences"], 3)
        self.assertEqual(rec["projects"], ["alpha", "beta", "gamma"])
        res2 = self.m.sync_issues(
            self._merged(), inbox_path=self.inbox, filer=filer, commenter=commenter, confirm=True
        )
        self.assertEqual(res2["updated"], [])
        self.assertEqual(len(commenter.calls), 1)
```

Replace `test_dry_run_reports_actions_without_calling_gh`:

```python
    def test_dry_run_reports_actions_without_calling_gh(self):
        filer, commenter = self._filer(), self._recorder()
        self._file_once(filer)
        self._project("gamma", FEEDBACK_ENTRY.format(project="gamma"))
        res = self.m.sync_issues(
            self._merged(), inbox_path=self.inbox,
            filer=filer, commenter=commenter, confirm=False,
        )
        self.assertEqual(len(res["would_update"]), 1)
        self.assertEqual(commenter.calls, [])
        self.assertEqual(len(filer.calls), 1)
```

Update `_file_once` in `InboxLifecycleTests` to the new signature:

```python
    def _file_once(self, filer):
        return self.m.sync_issues(self._merged(), inbox_path=self.inbox, filer=filer, confirm=True)
```

- [ ] **Step 2: Run the test file to verify the expected failures**

Run: `py -m pytest tests/test_feedback_tooling.py -q`
Expected: FAIL/ERROR — the surviving tests call `sync_issues` without the `resolved` positional, but the current signature still requires it (TypeError), proving the call sites now demand the new shape.

- [ ] **Step 3: Simplify `load_sidecar` and `collect`**

In `scripts/collect_feedback.py`, replace `load_sidecar`:

```python
def load_sidecar(root: Path) -> dict:
    path = _sidecar_path(root)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"collected": {}}
```

In `collect`, remove the resolved-skip line so the loop body reads:

```python
        for entry in iter_findings(feedback.read_text(encoding="utf-8")):
            fp = fingerprint(entry)
            bucket = open_unresolved if _in_sidecar(entry, state["collected"]) else new
            bucket.setdefault(fp, []).append((root.name, entry))
```

- [ ] **Step 4: Delete `mark_resolved`, `resolved_across`, and `gh_close_issue`**

Remove these three functions entirely from `scripts/collect_feedback.py`.

- [ ] **Step 5: Rework `sync_issues` to file + comment only**

Replace `sync_issues` with:

```python
def sync_issues(
    merged: Hits,
    *,
    inbox_path: Path,
    filer=gh_file_issue,
    commenter=gh_comment_issue,
    include_singles: bool = False,
    confirm: bool = False,
    labels=(),
    repo: str | None = None,
) -> dict:
    """File new eligible findings and comment on filed issues whose recurrence has
    grown since the ledger watermark. Dry run unless `confirm`. The ledger is saved
    after each successful action so a mid-run gh failure leaves prior actions durably
    recorded. Issues are closed the normal way (a fixing PR references them) — there
    is no auto-close.
    """
    inbox = load_inbox(inbox_path)
    ledger = inbox.setdefault("filed", {})

    to_file = [
        issue_spec(fp, hits, labels=labels)
        for fp, hits in eligible_for_filing(merged, inbox, include_singles=include_singles)
    ]

    to_update = []
    for fp, hits in merged.items():
        entry = ledger.get(fp)
        if not entry or not _is_open(entry):
            continue
        occ, projects = len(hits), sorted({p for p, _ in hits})
        grew = occ > entry.get("occurrences", 0) or bool(
            set(projects) - set(entry.get("projects", []))
        )
        if grew:
            to_update.append((fp, entry, occ, projects, hits))

    if not confirm:
        return {
            "would_file": to_file,
            "would_update": [
                {"fingerprint": fp, "ref": _issue_ref(e),
                 "from": f"{e.get('occurrences', 0)}x/{len(e.get('projects', []))}p",
                 "to": f"{occ}x/{len(projs)}p"}
                for fp, e, occ, projs, _ in to_update
            ],
            "filed": [], "updated": [],
        }

    filed, updated = [], []
    for spec in to_file:
        ref = filer(spec, repo=repo)
        ledger[spec["fingerprint"]] = {
            "issue": ref.get("number", ""),
            "url": ref.get("url", ""),
            "title": spec["title"],
            "candidate": spec["candidate"],
            "projects": spec["projects"],
            "occurrences": spec["occurrences"],
            "status": "open",
            "date": date.today().isoformat(),
        }
        save_inbox(inbox_path, inbox)
        filed.append({**spec, **ref})

    for fp, entry, occ, projects, hits in to_update:
        commenter(_issue_ref(entry), _recurrence_comment(entry, occ, projects, hits), repo=repo)
        entry["occurrences"], entry["projects"] = occ, projects
        entry["last_updated"] = date.today().isoformat()
        save_inbox(inbox_path, inbox)
        updated.append({"fingerprint": fp, "ref": _issue_ref(entry), "occurrences": occ})

    return {"would_file": [], "would_update": [], "filed": filed, "updated": updated}
```

Replace `file_issues` (drop the empty resolved dict it passed):

```python
def file_issues(
    merged: Hits,
    *,
    inbox_path: Path,
    filer=gh_file_issue,
    include_singles: bool = False,
    confirm: bool = False,
    labels=(),
    repo: str | None = None,
) -> dict:
    """Thin wrapper over `sync_issues` for callers/tests that only file."""
    return sync_issues(
        merged, inbox_path=inbox_path, filer=filer,
        include_singles=include_singles, confirm=confirm, labels=labels, repo=repo,
    )
```

- [ ] **Step 6: Update `_file_issues_cli` and `main` (remove close + `--resolve`)**

In `_file_issues_cli`, drop the `resolved` plumbing and the close reporting. Replace the function body through the dry-run/confirm reporting:

```python
def _file_issues_cli(roots, new, open_unresolved, args, filer, commenter) -> int:
    """Handle the --file-issues mode (file/comment); returns an exit code."""
    inbox_path = args.inbox or (Path.cwd() / ".agent-work" / INBOX_NAME)
    merged = merge_hits(new, open_unresolved)
    try:
        result = sync_issues(
            merged,
            inbox_path=inbox_path,
            filer=filer,
            commenter=commenter,
            include_singles=args.include_singles,
            confirm=args.confirm,
            labels=args.label,
            repo=args.repo,
        )
    except FileNotFoundError:
        print("error: `gh` not found on PATH; cannot manage issues", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"error: gh failed: {exc.stderr or exc}", file=sys.stderr)
        print(f"(actions completed before the failure are recorded in {inbox_path})", file=sys.stderr)
        return 1

    if not args.confirm:
        wf, wu = result["would_file"], result["would_update"]
        if not (wf or wu):
            print(
                "Inbox up to date: nothing to file or update "
                "(recurring findings only; --include-singles to widen)."
            )
            return 0
        print(f"DRY RUN — {len(wf)} file, {len(wu)} update; re-run with --confirm:\n")
        for spec in wf:
            print(f"  [file]   {spec['title']}")
            print(f"           fingerprint {spec['fingerprint']}, projects: {', '.join(spec['projects'])}")
        for u in wu:
            print(f"  [update] {u['ref']}  {u['from']} -> {u['to']}  ({u['fingerprint']})")
        return 0

    filed, updated = result["filed"], result["updated"]
    if not (filed or updated):
        print("Inbox already up to date (nothing to file or update).")
        return 0
    for entry in filed:
        ref = f"#{entry['number']}" if entry.get("number") else entry.get("url", "")
        print(f"filed  {ref}: {entry['title']}")
    for u in updated:
        print(f"update {u['ref']}: now {u['occurrences']}x ({u['fingerprint']})")
    print(f"\nfiled {len(filed)}, updated {len(updated)}; ledger: {inbox_path}")
    return 0
```

In `main`, change the signature to drop `closer`, remove the `--resolve`/`--note` arguments and the resolve branch, and update the `_file_issues_cli` call. Replace the `def main(...)` signature and the resolve/file-issues region:

```python
def main(
    argv: list[str] | None = None,
    *,
    filer=gh_file_issue,
    commenter=gh_comment_issue,
) -> int:
```

Delete the two `parser.add_argument("--resolve", ...)` / `--note` blocks. Delete the entire `if args.resolve:` block. Change the `--file-issues` dispatch to:

```python
    if args.file_issues:
        new, open_unresolved = collect(roots)
        return _file_issues_cli(roots, new, open_unresolved, args, filer, commenter)
```

- [ ] **Step 7: Run the full collector test file to verify it passes**

Run: `py -m pytest tests/test_feedback_tooling.py -q`
Expected: PASS.

- [ ] **Step 8: Run the whole suite to catch cross-references**

Run: `py -m pytest -q`
Expected: PASS (no other test references the removed `--resolve`/`mark_resolved`/`gh_close_issue`).

- [ ] **Step 9: Commit**

```bash
git add scripts/collect_feedback.py tests/test_feedback_tooling.py
git commit -m "Collector: drop the unused resolved-sidecar and issue auto-close

Under delete-not-mark a consuming repo deletes a handled finding rather than
marking it resolved, so the auto-close trigger can never fire. Remove the
resolved sidecar state, --resolve CLI, and gh issue auto-close; keep inbox
filing + comment-on-recurrence (the human-read front end). Issues close the
normal way via a fixing PR.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Templates + skills — teach "delete handled lessons"

**Files:**
- Modify: `skills/workbench/templates/LESSONS.template.md`
- Modify: `skills/lessons-auditor/templates/LESSON_CANDIDATES.template.md`
- Modify: `skills/lessons-auditor/templates/LESSONS_AUDIT.template.json`

**Interfaces:** none (documentation/templates). The `retire` op remains valid everywhere it's named in commander/admiral spines — only its meaning changed, which is documented in LESSONS.template.md.

- [ ] **Step 1: Rewrite the LESSONS template preamble + drop the Dormant section**

In `skills/workbench/templates/LESSONS.template.md`, replace the dormancy bullet (the line beginning "- Active lessons unconfirmed for `dormancy-runs`"):

```markdown
- `retire` **deletes** a lesson outright — there is no graveyard. Delete a lesson
  once you believe it's handled (internalized into the workflow, or a
  constellation defect fixed upstream); worst case it re-surfaces in a later run
  and you learn it again. Active lessons unconfirmed for `dormancy-runs` ticks are
  auto-deleted, except `constellation`-scoped debt, which is pinned until you
  retire it by hand.
```

Then delete the trailing `## Dormant` section heading (the last line of the file) so the file ends with the `## Active` section.

- [ ] **Step 2: Update the auditor reconciliation template**

In `skills/lessons-auditor/templates/LESSON_CANDIDATES.template.md`, replace the line:

```markdown
- `<or none — checked Active and Dormant against this run's evidence>`
```

with:

```markdown
- `<or none — checked Active lessons against this run's evidence>`
```

- [ ] **Step 3: Update the auditor checklist imperative**

In `skills/lessons-auditor/templates/LESSONS_AUDIT.template.json`, in the `playbook` task's `imperative`, change `Read .agent-work/LESSONS.md (Active and Dormant).` to `Read .agent-work/LESSONS.md (Active).`

- [ ] **Step 4: Verify no Dormant references remain in the lessons surfaces, and freshness still passes**

Run: `py -m pytest tests/test_feedback_tooling.py -q -k Freshness`
Expected: PASS (freshness installs the templates fresh and compares; content changes are fine).

Run (Grep, not bash): search `skills/workbench/templates` and `skills/lessons-auditor` for `Dormant` / `dormant`.
Expected: no matches.

- [ ] **Step 5: Commit**

```bash
git add skills/workbench/templates/LESSONS.template.md skills/lessons-auditor/templates/LESSON_CANDIDATES.template.md skills/lessons-auditor/templates/LESSONS_AUDIT.template.json
git commit -m "Templates: retire deletes, drop Dormant from lessons surfaces

LESSONS template preamble now describes deletion (with constellation pinning)
instead of demote/revive; the Dormant section is gone. Auditor templates read
Active only.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Rollout (post-merge, operational) — seed field-format template tracking into the prose repos

> Run this AFTER Tasks 1-4 merge to `main`, so the seeded templates carry the final delete-semantics wording. This modifies three EXTERNAL repos (story_time, network_elo, st-cleanroom-e3); any commit happens in those repos, not in constellation-skills. Not a code change — no unit tests.

**Files:** none in this repo. Seeds `.agent-work/templates/**` in each external repo.

- [ ] **Step 1: Dry-run the propagation against one repo**

From `C:\Programs\constellation-skills`:

Run: `py scripts/install_constellation.py --agent claude --scope project --project /c/Programs/story_time --skills workbench lessons-auditor --baseline-only`
Expected: prints "Template baseline seeded: N template(s)" and "Template working copies seeded: N editable copy(ies)".

- [ ] **Step 2: Verify the field-format feedback template landed**

Run (Grep, not bash): search `C:/Programs/story_time/.agent-work/templates/CONSTELLATION_FEEDBACK.template.md` for `Candidate:`.
Expected: match present (field format), and the file exists.

Run (Grep): search `C:/Programs/story_time/.agent-work/templates/LESSONS.template.md` for `Dormant`.
Expected: no match (the new delete-semantics template).

- [ ] **Step 3: Repeat for the other two repos**

Run: `py scripts/install_constellation.py --agent claude --scope project --project /c/Programs/network_elo --skills workbench lessons-auditor --baseline-only`
Run: `py scripts/install_constellation.py --agent claude --scope project --project /c/Programs/st-cleanroom-e3 --skills workbench lessons-auditor --baseline-only`
Expected: same seeded output for each.

- [ ] **Step 4: Hand back to the user**

Report the seeded paths and note that each external repo now has uncommitted `.agent-work/templates/**` to review and commit in that repo. Future feedback entries there will follow the field format with a stable `Lesson:` id; the prose entries already written are collectable via the Task 2 parser.

---

## Self-Review

**Spec coverage:**
- Piece 1 (engine delete + Dormant removal + constellation pin) → Task 1. ✓
- Piece 2 (prose parser) → Task 2. ✓
- Piece 3 (repos onto template) → Task 5 (operational). ✓
- Piece 4 (drop resolved/auto-close, keep inbox) → Task 3. ✓
- Piece 5 (skills/templates delete semantics) → Task 4. ✓
- Tests called out in the spec → covered in Tasks 1-3 steps. ✓

**Placeholder scan:** No TBD/TODO; every code step shows the actual code; commands have expected output. ✓

**Type/name consistency:**
- `Playbook.find` returns `Lesson | None` in Task 1; Task 1 Step 6 uses `lesson = book.find(...)` consistently (no `(lesson, section)` tuple anywhere). ✓
- `sync_issues` new signature (no `resolved`, no `closer`) in Task 3 Step 5 matches all call sites updated in Task 3 Step 1 and `_file_issues_cli` in Step 6. ✓
- `parse_prose_findings` / `iter_findings` names in Task 2 match their uses. ✓
- `load_sidecar` returns `{"collected": {}}`; `collect` no longer reads `state["resolved"]`. ✓

**Scope check:** One cohesive change to the lessons machinery, sequenced so each task ends green. Task 5 is operational and explicitly post-merge. ✓
