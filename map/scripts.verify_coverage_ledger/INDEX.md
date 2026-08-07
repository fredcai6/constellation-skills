# scripts.verify_coverage_ledger
scripts/verify_coverage_ledger.py, 133 lines, 2 holes

Verify the removability coverage ledger against the installed-externals manifest.

This is the mechanical rail behind epic-164's done-condition (#11): "superpowers +
Pocock are removable" must be *checkable*, not asserted. Before the human uninstalls
the external skills, this script proves the coverage ledger
(``docs/removability_ledger.json``) actually accounts for every installed external
(``docs/installed_externals_manifest.json``) and makes no false coverage claim.

It REFUSES (non-zero exit) when any of:
  (a) a ``new`` row (new/changed work THIS epic, the "*" rows) — or any covered row —
      names a constellation ``home_skill`` that does not exist in the corpus (a home
      that isn't really shipped is a false coverage claim);
  (b) an external in the captured installed-inventory manifest is ABSENT from the
      ledger (an unmapped external = an uncovered capability the ledger silently missed);
  (c) a ``declined`` row carries no reason (a declination with no rationale is not a
      recorded decision).

It also rejects a structurally malformed ledger (unknown status, declined row that
still names a home, non-declined row with no home). Quality of the mapping is the
independent reviewer's judgment; this rail only proves the ledger is grounded,
complete, and internally honest.

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, sys
imported by: none found

```python
_VALID_STATUS = {'new', 'covered', 'declined'}
```

- [CoverageLedgerError](CoverageLedgerError.md) class: Raised when the coverage ledger fails a mechanical rail check.
- [manifest_externals](manifest_externals.md) function: Flatten every installed external skill name across all sources.
- [skill_exists](skill_exists.md) function: A home is real iff a skill directory of that name exists in the corpus.
- [verify_coverage_ledger](verify_coverage_ledger.md) function: Raise CoverageLedgerError on the first rail violation; return None if clean.
- [_load_json](_load_json.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
