# scripts.verify_issue_set
scripts/verify_issue_set.py, 167 lines, 2 holes

Refuse a malformed cut-work issue set — the constellation-to-issues RAIL.

This is the single mechanically-enforced rail for the `constellation-to-issues`
skill (DESIGN_SPEC Section A). The skill emits ONE tracker-agnostic manifest
(the issue-set artifact); this script is the gate that manifest must clear
before the skill may emit or file it. `file_issue_set.py` runs this first and
refuses to file anything if it fails, so a malformed set can never reach a
tracker.

It exits NON-ZERO (and raises `IssueSetError`) on any of the four locked
refusals, plus the structural basics a well-formed manifest needs:

  1. UNCONFIRMED SPEC — re-runs the existing verify_spec_confirmed.py confirm
     gate against the spec the manifest was cut from. "No work is cut from an
     unconfirmed design" is enforced here, not merely asserted in prose.
  2. NO DEPENDENCY EDGE — an issue set with zero `blocks` edges across every
     issue is refused (a wave-ordered epic needs at least one edge to order).
     A `blocks` target that names no known issue id is also refused (a dangling
     edge would break the downstream topological sort).
  3. UNTYPED ISSUE — every issue must be typed HITL or AFK; an untyped issue,
     or one carrying any other type value, is refused.
  4. HITL WITHOUT REASON — a HITL issue must carry a non-empty `hitl_reason`.

Everything else about the cut (coverage vs spec, invented scope, whether a
risky AFK should be HITL) is the INDEPENDENT reviewer's judgment — deliberately
NOT gated here (DESIGN_SPEC Section A: the manifest is evidence, never a review
gate; well-formed != well-cut). Standard library only.

imports stdlib: __future__.annotations, argparse, json, os, pathlib.Path, sys
imports third-party: verify_spec_confirmed.SpecVerificationError, verify_spec_confirmed.verify_spec_confirmed
imported by: none found

```python
VALID_TYPES = ('HITL', 'AFK')
```

- [IssueSetError](IssueSetError.md) class: Raised when the issue-set manifest is malformed — the rail's refusal.
- [_require](_require.md) function: HOLE: no docstring
- [verify_manifest_shape](verify_manifest_shape.md) function: Structural basics of the one manifest: an epic with a title and a
- [verify_edges](verify_edges.md) function: Rule 2: at least one dependency edge across the set, and every edge
- [verify_types](verify_types.md) function: Rules 3 and 4: every issue typed HITL/AFK; HITL requires a hitl_reason.
- [verify_issue_set](verify_issue_set.md) function: Raise IssueSetError on any malformed condition; return None if the set is
- [main](main.md) function: HOLE: no docstring
