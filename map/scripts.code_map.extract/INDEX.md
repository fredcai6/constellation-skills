# scripts.code_map.extract
scripts/code_map/extract.py, 786 lines, 32 holes

Pure-AST statement extractor with its own cross-file name resolution.

Python stdlib only (ast, os, json, hashlib). No SCIP, no type inference beyond
the two cheap rules stated in RESOLUTION RULES below.

Two passes:
  pass 1  index every corpus module's *module-level* binding table
          (defs, classes, assignments, imports and what each import binds)
  pass 2  walk the same files, tracking scopes, and emit one statement per
          fact with the resolved symbol -- or an explicit unresolved marker.

Both passes read the mappable corpus from `discovery.discover_corpus`. The
prototype this was ported from indexed three hardcoded directories of one
external checkout and took its pass-2 file list from a handwritten manifest.

RESOLUTION RULES (the honest cheap version)
  R1 scope chain      a name bound in an enclosing function scope is `local`
  R2 module table     else a module-level def/class/assign -> mod:name
  R3 imports          from m import n [as a] -> a binds (m, n)
                      import m.n [as a]      -> a binds module m.n
                      relative imports resolved from the file's package path
  R4 re-export chase  if m's own table says n is itself an import, follow it
                      (max 5 hops) to the defining module
  R5 attribute base   module alias  -> mod:attr (then R4)
                      class name    -> mod:Class.attr (walk same-module bases)
                      self in C     -> mod:C.attr (walk same-module bases)
                      local var whose ONLY assignment is `v = Known(...)`
                                    -> mod:Known.attr        [inference rule 1]
                      param annotated `p: Known`
                                    -> mod:Known.attr        [inference rule 2]
                      anything else -> UNRESOLVED/dispatch-unknown-base
  R6 star import      from m import * : if m is internal and has the name,
                      resolve; else UNRESOLVED/star-import
  R7 builtins         -> external
  R8 dynamic          getattr/setattr/importlib -> UNRESOLVED/dynamic

Statement line shape:
  {"s","p","o","q":{"file","line","col"},"ref":"ast","hash"}
plus two measurement-only fields:
  "res"  internal|external|local|unresolved|literal
  "why"  failure class, present only when res == unresolved

imports stdlib: ast, builtins, hashlib, json, os, sys
imports internal: scripts.code_map.discovery:discover_corpus
imported by: scripts.code_map.checks, scripts.code_map.cli, scripts.code_map.render

```python
ROOT = None
BUILTINS = set(dir(builtins))
STATEMENTS_NAME = 'statements.jsonl'
REPORT_NAME = 'extract_report.json'
TABLES = {}
UNRES = 'UNRESOLVED'
```

- [mod_of](mod_of.md) function: HOLE: no docstring
- [pkg_of](pkg_of.md) function: HOLE: no docstring
- [resolve_rel](resolve_rel.md) function: HOLE: no docstring
- [ModuleTable](ModuleTable.md) class: Module-level bindings for one file.
  - [ModuleTable.__init__](ModuleTable.__init__.md) method: HOLE: no docstring
- [build_table](build_table.md) function: HOLE: no docstring
- [_table_stmt](_table_stmt.md) function: HOLE: no docstring
- [_dotted](_dotted.md) function: HOLE: no docstring
- [pass1](pass1.md) function: Index the module-level binding table of every file in the corpus.
- [chase](chase.md) function: Follow a (module, name) through re-exports to its defining module.
- [Scope](Scope.md) class: HOLE: no docstring
  - [Scope.__init__](Scope.__init__.md) method: HOLE: no docstring
  - [Scope.bind](Scope.bind.md) method: HOLE: no docstring
  - [Scope.lookup](Scope.lookup.md) method: HOLE: no docstring
- [Extractor](Extractor.md) class: HOLE: no docstring
  - [Extractor.__init__](Extractor.__init__.md) method: HOLE: no docstring
  - [Extractor.emit](Extractor.emit.md) method: HOLE: no docstring
  - [Extractor.here](Extractor.here.md) method: HOLE: no docstring
  - [Extractor.resolve_name](Extractor.resolve_name.md) method: ast.Name -> (symbol, res, why)
  - [Extractor.from_binding](Extractor.from_binding.md) method: Resolve an import binding tuple -> (symbol, res, why).
  - [Extractor.class_member](Extractor.class_member.md) method: Look attr up on class cls, walking same-module bases. -> symbol|None
  - [Extractor.attr_via_import](Extractor.attr_via_import.md) method: `head` is bound by an import; resolve `head....attr` through it.
  - [Extractor.resolve_attr](Extractor.resolve_attr.md) method: ast.Attribute -> (symbol, res, why)
  - [Extractor.resolve_expr](Extractor.resolve_expr.md) method: HOLE: no docstring
  - [Extractor.pos_of](Extractor.pos_of.md) method: Position of the *identifier* SCIP would mark (0-based line/col).
  - [Extractor.infer_type](Extractor.infer_type.md) method: `v = Known(...)` / annotation -> (module, class) or None.
  - [Extractor.infer_annotation](Extractor.infer_annotation.md) method: HOLE: no docstring
  - [Extractor.run](Extractor.run.md) method: HOLE: no docstring
  - [Extractor.visit_ClassDef](Extractor.visit_ClassDef.md) method: HOLE: no docstring
  - [Extractor._func](Extractor._func.md) method: HOLE: no docstring
  - [Extractor._prebind](Extractor._prebind.md) method: HOLE: no docstring
  - [Extractor.visit_Assign](Extractor.visit_Assign.md) method: HOLE: no docstring
  - [Extractor.visit_AnnAssign](Extractor.visit_AnnAssign.md) method: HOLE: no docstring
  - [Extractor.visit_AugAssign](Extractor.visit_AugAssign.md) method: HOLE: no docstring
  - [Extractor._store](Extractor._store.md) method: HOLE: no docstring
  - [Extractor._ref](Extractor._ref.md) method: HOLE: no docstring
  - [Extractor.visit_Name](Extractor.visit_Name.md) method: HOLE: no docstring
  - [Extractor.visit_Attribute](Extractor.visit_Attribute.md) method: HOLE: no docstring
  - [Extractor.visit_Call](Extractor.visit_Call.md) method: HOLE: no docstring
  - [Extractor.visit_Import](Extractor.visit_Import.md) method: HOLE: no docstring
  - [Extractor.visit_ImportFrom](Extractor.visit_ImportFrom.md) method: HOLE: no docstring
- [_target_names](_target_names.md) function: HOLE: no docstring
- [run](run.md) function: Extract the statement store for `root` into `artifacts`. Returns an exit code.
