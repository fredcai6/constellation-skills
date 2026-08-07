# scripts.code_map.extract:Extractor
class, scripts/code_map/extract.py:255, 467 lines

```python
class Extractor(NodeVisitor)
```

HOLE: no docstring

```python
visit_FunctionDef = _func
visit_AsyncFunctionDef = _func
```

- [__init__](Extractor.__init__.md) method: HOLE: no docstring
- [emit](Extractor.emit.md) method: HOLE: no docstring
- [here](Extractor.here.md) method: HOLE: no docstring
- [resolve_name](Extractor.resolve_name.md) method: ast.Name -> (symbol, res, why)
- [from_binding](Extractor.from_binding.md) method: Resolve an import binding tuple -> (symbol, res, why).
- [class_member](Extractor.class_member.md) method: Look attr up on class cls, walking same-module bases. -> symbol|None
- [attr_via_import](Extractor.attr_via_import.md) method: `head` is bound by an import; resolve `head....attr` through it.
- [resolve_attr](Extractor.resolve_attr.md) method: ast.Attribute -> (symbol, res, why)
- [resolve_expr](Extractor.resolve_expr.md) method: HOLE: no docstring
- [pos_of](Extractor.pos_of.md) method: Position of the *identifier* SCIP would mark (0-based line/col).
- [infer_type](Extractor.infer_type.md) method: `v = Known(...)` / annotation -> (module, class) or None.
- [infer_annotation](Extractor.infer_annotation.md) method: HOLE: no docstring
- [run](Extractor.run.md) method: HOLE: no docstring
- [visit_ClassDef](Extractor.visit_ClassDef.md) method: HOLE: no docstring
- [_func](Extractor._func.md) method: HOLE: no docstring
- [_prebind](Extractor._prebind.md) method: HOLE: no docstring
- [visit_Assign](Extractor.visit_Assign.md) method: HOLE: no docstring
- [visit_AnnAssign](Extractor.visit_AnnAssign.md) method: HOLE: no docstring
- [visit_AugAssign](Extractor.visit_AugAssign.md) method: HOLE: no docstring
- [_store](Extractor._store.md) method: HOLE: no docstring
- [_ref](Extractor._ref.md) method: HOLE: no docstring
- [visit_Name](Extractor.visit_Name.md) method: HOLE: no docstring
- [visit_Attribute](Extractor.visit_Attribute.md) method: HOLE: no docstring
- [visit_Call](Extractor.visit_Call.md) method: HOLE: no docstring
- [visit_Import](Extractor.visit_Import.md) method: HOLE: no docstring
- [visit_ImportFrom](Extractor.visit_ImportFrom.md) method: HOLE: no docstring

reads internal: Extractor._func x2
writes internal: Extractor.visit_AsyncFunctionDef, Extractor.visit_FunctionDef

referenced by: 1 sites, this module only
