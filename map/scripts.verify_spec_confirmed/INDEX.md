# scripts.verify_spec_confirmed
scripts/verify_spec_confirmed.py, 207 lines, 5 holes

Verify a shaped-design spec's Confirmation block and findings table.

Wired as the explorer spine's `review`/`confirm` step command checks and as
the Commander understand-step intake check: "no work is cut from an
unconfirmed design" must be mechanically enforceable, not prose. See
DESIGN_SPEC.md, headline doctrine 3.

Phases:
  review  -- PASS iff a findings table exists and no Disposition cell is
             empty. Status may still be DRAFT.
  confirm -- (default) PASS iff Status is CONFIRMED, Confirmed-by and Date
             are non-empty, AND no Disposition cell is empty.

Any phase: a loud `UNCONFIRMED -- DO NOT CUT` marker line (em-dash or hyphen)
FAILs with a named refusal. A spec with no findings table FAILs both phases
-- a critical review is mandatory; absence must not pass silently.

imports stdlib: __future__.annotations, argparse, pathlib.Path, re, sys
imported by: none found

```python
_CONFIRMATION_HEADING_RE = re.compile('^##\\s+Confirmation\\s*$', re.MULTILINE)
_ANY_H2_RE = re.compile('^##\\s+\\S', re.MULTILINE)
_STATUS_RE = re.compile('^-\\s*\\*\\*Status:[ \\t]*(.*?)\\*\\*\\s*$', re.MULTILINE)
_CONFIRMED_BY_RE = re.compile('^-[ \\t]*Confirmed by:[ \\t]*(.*)$', re.MULTILINE)
_DATE_RE = re.compile('^-[ \\t]*Date:[ \\t]*(.*)$', re.MULTILINE)
_UNCONFIRMED_MARKER_RE = re.compile('UNCONFIRMED\\s+[—-]\\s+DO NOT CUT')
```

- [SpecVerificationError](SpecVerificationError.md) class: Raised when the design-spec confirmation invariant is broken.
- [_confirmation_section](_confirmation_section.md) function: Return the ``## Confirmation`` section body, or None if absent.
- [parse_confirmation](parse_confirmation.md) function: Pull Status / Confirmed-by / Date out of the Confirmation section.
  - [parse_confirmation._find](parse_confirmation._find.md) method: HOLE: no docstring
- [_split_row](_split_row.md) function: HOLE: no docstring
- [_is_separator_row](_is_separator_row.md) function: HOLE: no docstring
- [find_findings_table](find_findings_table.md) function: Return the list of Disposition cell values (one per data row), or None
- [_unconfirmed_marker_hit](_unconfirmed_marker_hit.md) function: Return the offending line if the marker appears as a status/header
- [verify_spec_confirmed](verify_spec_confirmed.md) function: HOLE: no docstring
- [resolve_target](resolve_target.md) function: Resolve the CLI target: a path if it exists, else a work-id form.
- [main](main.md) function: HOLE: no docstring
