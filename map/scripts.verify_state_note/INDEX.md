# scripts.verify_state_note
scripts/verify_state_note.py, 104 lines, 3 holes

Verify a crash-resume state note exists and is filled, before detached work.

Wired as a `command` precondition on the spine `execute` step: an agent cannot
enter the detach-heavy execute phase without a well-formed
`.agent-work/<work-id>/STATE_NOTE.md`. The note is the one artifact that turns a
dead detached session into a clean resume instead of hours of forensics — see
`skills/admiral/references/fleet-doctrine.md`, "State-note-before-detach".

It checks the five resume fields are present and actually filled (not left as
`<placeholder>` text and not empty). It does NOT judge whether the values are
correct — that is the agent's job; the engine only guarantees the note exists
and is filled in before the first detach.

imports stdlib: __future__.annotations, argparse, pathlib.Path, re, sys
imported by: none found

```python
REQUIRED_FIELDS = ('step', 'slug', 'next command', 'pid', 'expected artifact')
FIELD_RE = re.compile('^- \\*\\*(.+?):\\*\\*\\s*(.*?)\\s*$')
```

- [_utf8_stdio](_utf8_stdio.md) function: HOLE: no docstring
- [parse_fields](parse_fields.md) function: Pull `- **key:** value` lines into a lowercased key -> value map.
- [_is_placeholder](_is_placeholder.md) function: True for an empty value or an unfilled `<...>` template placeholder.
- [validate](validate.md) function: Return a list of problems; empty means the note is well-formed.
- [note_path](note_path.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
