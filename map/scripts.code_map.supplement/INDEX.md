# scripts.code_map.supplement
scripts/code_map/supplement.py, 206 lines, 4 holes

Supplementary AST pass over the mappable corpus (READ-ONLY over source).

Every fact fetched here is a MEASURED GAP in the statement vocabulary: the
statement store should have carried it and did not. The gap ids below are the
measurement, and gate g3 removes this stage by merging what it fetches into the
statement schema itself. Until then this is ported, not improved.

The prototype took its file list from a handwritten manifest and hardcoded one
external checkout as its root; both are now `discover_corpus` and `run(root)`.

Output: <artifacts>/supplement.json

imports stdlib: ast, json, os, sys
imports internal: scripts.code_map.discovery:discover_corpus
imported by: scripts.code_map.checks, scripts.code_map.cli, scripts.code_map.render

```python
SUPPLEMENT_NAME = 'supplement.json'
REPORT_NAME = 'supplement_report.json'
GAPS = {'G1-kind': 'entity kind (class / function / method / async / property)', 'G2-signature...
```

- [mod_of](mod_of.md) function: HOLE: no docstring
- [attrs_of](attrs_of.md) function: Annotated / assigned attributes directly in a class or module body.
- [sym](sym.md) function: The extractor's symbol scheme: 'scripts.code_map.cli:build_parser'.
- [sig_of](sig_of.md) function: HOLE: no docstring
  - [sig_of.one](sig_of.one.md) method: HOLE: no docstring
- [doc_split](doc_split.md) function: HOLE: no docstring
- [run](run.md) function: Write the supplement for `root` into `artifacts`. Returns an exit code.
