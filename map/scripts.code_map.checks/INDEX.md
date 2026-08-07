# scripts.code_map.checks
scripts/code_map/checks.py, 211 lines, 1 holes

Print-only diagnostics over the built map: non-ASCII provenance, entity

reconciliation, store-only definition sites, and the function-local-import
measurement.

These PRINT. They assert nothing and they never set an exit code, so a broken
map does not fail a run today. Gate g1 rewrites them into real checks; this
port exists only to keep the `check` subcommand wired and the numbers readable
in the meantime.

The prototype's fourth section is DROPPED. It spot-checked one hardcoded file
of another repository (`scripts/validate_segment_map_662.py`) and printed one
named page from it, so there is nothing here for it to look at. What it
demonstrated -- that every top-level def in a source file gets a page -- is a
real check, and it belongs in g1's rewrite as a rule over the whole corpus
rather than as one file's spot check.

Both prototype halves (`checks.py` and `checks2.py`) are folded into this one
module; they read the same two stores and split only because they were written
on different days.

imports stdlib: ast, collections, json, os, pathlib
imports internal: scripts.code_map.discovery:discover_corpus, scripts.code_map.extract:STATEMENTS_NAME, scripts.code_map.supplement:SUPPLEMENT_NAME
imported by: scripts.code_map.cli

- [_statements](_statements.md) function: HOLE: no docstring
- [non_ascii_provenance](non_ascii_provenance.md) function: (b) every non-ASCII line in the page tree should trace to a docstring or
- [reconciliation](reconciliation.md) function: (c) statements `contains` vs the supplement's AST walk.
- [store_only_sites](store_only_sites.md) function: What the store sees that the supplement's body-walk does not.
- [function_local_imports](function_local_imports.md) function: Defect D4: names bound by a function-scoped import, and how many
- [run](run.md) function: Print every diagnostic. Always returns 0 -- these do not gate anything
