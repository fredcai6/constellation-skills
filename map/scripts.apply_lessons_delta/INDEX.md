# scripts.apply_lessons_delta
scripts/apply_lessons_delta.py, 699 lines, 13 holes

Deterministically apply structured lesson delta operations to a LESSONS.md playbook.

The LLM proposes operations (add/amend/confirm/disconfirm/mention/retire/defer/apply/
export/resolve) in a JSON delta file; this script validates and applies them mechanically.
The LLM never writes the playbook directly. All-or-nothing: any invalid op rejects the
whole delta.

imports stdlib: __future__.annotations, argparse, dataclasses.dataclass, dataclasses.field, datetime.date, json, pathlib.Path, re, sys
imports third-party: agent_work_root.durable_root
imported by: none found

```python
SCOPES = ('handoff', 'commander', 'admiral', 'project', 'constellation')
DEFAULT_DORMANCY_RUNS = 10
DEFAULT_APPLY_RECURRENCES = 1
DEFAULT_APPLY_CONFIRMED = 3
TICKED_WORK_ID_RETENTION = 50
STATE_RE = re.compile('<!--\\s*playbook-state:\\s*run-tick=(\\d+)(?:\\s+cap=\\d+)?\\s+dormancy-run...
LESSON_HEADING_RE = re.compile('^### lesson:([a-z0-9][a-z0-9-]*)$')
FIELD_RE = re.compile('^- ([a-z-]+): (.*)$')
```

- [_utf8_stdio](_utf8_stdio.md) function: Per field feedback: don't make every call site set PYTHONIOENCODING.
- [LessonsDeltaError](LessonsDeltaError.md) class: Raised when a delta cannot be applied; nothing is written.
- [Lesson](Lesson.md) class: HOLE: no docstring
  - [Lesson.render](Lesson.render.md) method: HOLE: no docstring
- [Playbook](Playbook.md) class: HOLE: no docstring
  - [Playbook.find](Playbook.find.md) method: HOLE: no docstring
- [_default_preamble](_default_preamble.md) function: HOLE: no docstring
- [parse_lessons](parse_lessons.md) function: HOLE: no docstring
  - [parse_lessons.flush](parse_lessons.flush.md) method: HOLE: no docstring
- [load_playbook](load_playbook.md) function: HOLE: no docstring
- [render_playbook](render_playbook.md) function: HOLE: no docstring
- [ripe_lessons](ripe_lessons.md) function: Threshold-ripe lessons still awaiting an apply/export/defer disposition.
- [_apply_threshold_ripe](_apply_threshold_ripe.md) function: Is this non-constellation lesson ripe for apply?
- [_is_doctrine_target](_is_doctrine_target.md) function: A path is a doctrine artifact (an agent reads it; no unit test grades it) when it
- [_stamp](_stamp.md) function: HOLE: no docstring
- [_stamp_date](_stamp_date.md) function: Extract the ISO date from a "YYYY-MM-DD (work-id)" stamp for same-epoch
- [validate_delta](validate_delta.md) function: HOLE: no docstring
- [apply_delta](apply_delta.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
