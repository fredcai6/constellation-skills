# scripts.verify_fowler_pass
scripts/verify_fowler_pass.py, 205 lines, 3 holes

Refuse a skipped smell or a silent override — the reviewer Fowler-pass RAIL.

This is the mechanically-enforced rail for the `constellation-reviewer`
sharpening (DESIGN_SPEC Section D3). The reviewer drives a survey whose
`r6-fowler` item runs a refactoring / code-smell pass in the sense of Martin
Fowler's *Refactoring*. This script is the gate the Fowler-pass RECORD must clear
before that item may record pass. It enforces the two locked behaviors in code,
so neither can rest on the reviewer's self-assertion:

  * VISIT-EVERY-SMELL. The pass must render a verdict on every smell in Fowler's
    baseline catalog (`REQUIRED_SMELLS`). A record that omits a baseline smell is
    REFUSED — the pass cannot be silently narrowed so a present smell is never
    looked at. Each smell carries exactly one verdict:
      - `flagged`    — smell present and worth raising; needs a non-empty finding.
      - `overridden` — smell present but a DOCUMENTED REPO STANDARD makes it
                       acceptable, so it is NOT flagged. This is the bounded
                       override: it MUST carry a logged reason — a non-empty
                       `override.repo_standard` (the standard that wins) AND a
                       non-empty `override.reason` (why it subordinates the smell).
                       "Repo standard wins" is never a silent, unexplained
                       dismissal (the OVERRIDE-LOG rail).
      - `absent`     — smell not present in the diff; no further obligation.

  * The Fowler smells are JUDGMENT CALLS, always subordinate to the repo's
    documented standards — never hard violations. The rail does NOT decide whether
    a smell is really present or whether an override is wise; it only refuses a
    SKIPPED smell and a silent (unlogged) override. Which smells to flag, and
    whether the pass genuinely sharpened the review, is the INDEPENDENT reviewer's
    judgment (DESIGN_SPEC TF8), deliberately NOT gated here.

A defended exception — skipping the whole pass (e.g. a docs-only diff with no code
to smell-test) — requires a `rail_exception` carrying a non-empty `reviewer_cosign`
(the INDEPENDENT reviewer, never the author) AND a non-empty `log`. Self-assertion
never passes. The exception covers the whole-pass skip ONLY; it never excuses a
single unlogged override once the pass is run. Standard library only.

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, sys
imported by: none found

```python
REQUIRED_SMELLS = ('long-method', 'large-class', 'duplicated-code', 'feature-envy', 'data-clumps', 'primi...
VALID_VERDICTS = ('flagged', 'overridden', 'absent')
```

- [FowlerPassError](FowlerPassError.md) class: Raised when a Fowler-pass record fails the rail — the refusal.
- [_require](_require.md) function: HOLE: no docstring
- [_nonempty](_nonempty.md) function: HOLE: no docstring
- [_exception_cosigned](_exception_cosigned.md) function: True only when an INDEPENDENT reviewer co-signed a whole-pass skip AND a log
- [verify_structure](verify_structure.md) function: The record's basic shape: a diff reference and a smell list with unique,
- [verify_visit_every_smell](verify_visit_every_smell.md) function: Visit-every-item: every baseline smell has a verdict — unless a reviewer-
- [verify_overrides_logged](verify_overrides_logged.md) function: The bounded override rail: an `overridden` verdict (smell present but a
- [verify_fowler_pass](verify_fowler_pass.md) function: Raise FowlerPassError on any failed rule; return None if the record clears
- [main](main.md) function: HOLE: no docstring
