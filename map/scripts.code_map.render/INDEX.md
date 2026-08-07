# scripts.code_map.render
scripts/code_map/render.py, 439 lines, 10 holes

Full-repo derived map -- one page per entity, agent-lean.

The module list is DERIVED from the extraction, not hardcoded. The entity tree
is driven by the supplement's structurally-correct keys, joined to the store's
symbols on (file, line); see D2 below. The top INDEX groups modules by
top-level package so it stays a routing surface as the module count grows.

Importing this module has no side effects: the prototype loaded both stores at
import time, which made the module unimportable without a built store and
impossible to run twice against different roots. `load_stores()` now owns that.

Defects carried, each owned by a later gate:
  D1 the store's q.line is 0-based and the schema does not say so, so every
     line read out of a statement gets +1. Gate g3.
  D2 the store's `contains` symbol truncates the enclosing chain for entities
     nested inside a function -- a class defined in a function is named as if
     module-level, and a function defined in a method is named against the
     class, dropping the method. Pages are therefore keyed by the supplement's
     qualified name, and the store's symbol is looked up through a (file, line)
     join. Gate g2.

Output layout:
  map/INDEX.md                       top index, grouped by package
  map/<dotted.module>/INDEX.md       module doc, deps, constants, contents
  map/<dotted.module>/<Entity>.md    one page per class/function/method
  map/ids.jsonl                      id -> symbol-path lookup

imports stdlib: collections, json, os, pathlib, shutil, subprocess, sys
imports internal: scripts.code_map.extract:STATEMENTS_NAME, scripts.code_map.supplement:SUPPLEMENT_NAME
imported by: scripts.code_map.cli

```python
STDLIB = set(sys.stdlib_module_names)
REPORT_NAME = 'render_report.json'
HOLE = 'HOLE: no docstring'
ent_supp = {}
mod_supp = {}
docs = {}
params = collections.defaultdict(list)
inherits = collections.defaultdict(list)
edges = collections.defaultdict(list)
inbound = collections.defaultdict(collections.Counter)
imports_out = collections.defaultdict(list)
imported_by = collections.defaultdict(set)
cont_at = {}
alias = {}
alias_missing = 0
children = collections.defaultdict(list)
members_of = collections.defaultdict(list)
MODULES = []
BY_PKG = collections.defaultdict(list)
intern = sys.intern
```

- [modof](modof.md) function: HOLE: no docstring
- [load_stores](load_stores.md) function: Read the statement store and the supplement, and build every index the
- [ext_label](ext_label.md) function: stdlib vs third-party -- classified renderer-side; the store does not say.
- [tally](tally.md) function: HOLE: no docstring
- [summary_of](summary_of.md) function: Store first (that is the map's source of truth); supplement fills gaps.
- [mod_summary_of](mod_summary_of.md) function: HOLE: no docstring
- [loc](loc.md) function: file:line, N lines. Supplement lines are 1-based already (D1 applied at load).
- [doc_block](doc_block.md) function: HOLE: no docstring
- [attr_lines](attr_lines.md) function: Constants / fields as code-shaped lines: NAME: annotation = value
- [uses_lines](uses_lines.md) function: HOLE: no docstring
- [refs_line](refs_line.md) function: HOLE: no docstring
- [entity_page](entity_page.md) function: HOLE: no docstring
- [module_index](module_index.md) function: HOLE: no docstring
  - [module_index.walk](module_index.walk.md) method: HOLE: no docstring
- [repo_name](repo_name.md) function: Name the map after the repository, not the directory it was built in: a
- [top_index](top_index.md) function: HOLE: no docstring
- [run](run.md) function: Render the page tree for `root` from `artifacts` into `out`. Returns an
