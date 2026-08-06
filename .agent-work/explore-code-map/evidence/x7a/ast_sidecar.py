"""x7a step 2 — AST sidecar: recover Store/Load contexts SCIP does not emit.

For every file in the slice (src/utils) and every inbound file that references
a src.utils symbol, walk the AST and record each *identifier token* with its
context. Positions are emitted twice — UTF-8 byte column (what CPython's
col_offset actually is) and character column — so the join can report which
one SCIP's ranges agree with.

Output: ast_ctx.jsonl
  {file, line(1-based), bcol, ccol, name, ctx: store|load|del|augstore|param|
   def, node: Name|Attribute|arg|FunctionDef|ClassDef, ...}
"""
import ast, os, json, sys

OUT = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\Programs\f1Brainz"


def char_col(line_bytes, bcol):
    """UTF-8 byte column -> character column on that line."""
    try:
        return len(line_bytes[:bcol].decode("utf-8"))
    except UnicodeDecodeError:
        return bcol


class Walker(ast.NodeVisitor):
    def __init__(self, relpath, lines_b):
        self.rel = relpath
        self.lines_b = lines_b
        self.rows = []
        self.stack = []          # enclosing def/class symbol-ish path

    def emit(self, line, bcol, name, ctx, node_kind, extra=None):
        lb = self.lines_b[line - 1] if 0 < line <= len(self.lines_b) else b""
        row = {"file": self.rel, "line": line, "bcol": bcol,
               "ccol": char_col(lb, bcol), "name": name, "ctx": ctx,
               "node": node_kind, "scope": "/".join(self.stack)}
        if extra:
            row.update(extra)
        self.rows.append(row)

    # ---- identifier-bearing expression nodes
    def visit_Name(self, node):
        ctx = type(node.ctx).__name__.lower()   # load | store | del
        self.emit(node.lineno, node.col_offset, node.id, ctx, "Name")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        # node.col_offset points at the *value* expression; the attribute
        # identifier ends the node, so back off from the end.
        ctx = type(node.ctx).__name__.lower()
        bcol = node.end_col_offset - len(node.attr.encode("utf-8"))
        base = None
        if isinstance(node.value, ast.Name):
            base = node.value.id
        self.emit(node.end_lineno, bcol, node.attr, ctx, "Attribute",
                  {"base": base})
        self.generic_visit(node)

    def visit_Subscript(self, node):
        # container mutation: d[k] = v  -> a write to whatever d resolves to
        if isinstance(node.ctx, ast.Store) and isinstance(node.value, ast.Name):
            self.emit(node.value.lineno, node.value.col_offset,
                      node.value.id, "store", "Subscript",
                      {"via": "subscript"})
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        # x += 1 : AST marks the target Store, but it is read-then-write.
        t = node.target
        if isinstance(t, ast.Name):
            self.emit(t.lineno, t.col_offset, t.id, "augstore", "AugAssign")
        elif isinstance(t, ast.Attribute):
            bcol = t.end_col_offset - len(t.attr.encode("utf-8"))
            self.emit(t.end_lineno, bcol, t.attr, "augstore", "AugAssign")
        self.generic_visit(node)

    # ---- definitions and parameters
    def _fn(self, node, kind):
        # the name token sits after the keyword; find it on the def line
        kw = b"class " if kind == "ClassDef" else (
            b"async def " if isinstance(node, ast.AsyncFunctionDef) else b"def ")
        lb = self.lines_b[node.lineno - 1]
        idx = lb.find(kw)
        bcol = (idx + len(kw)) if idx >= 0 else node.col_offset
        self.emit(node.lineno, bcol, node.name, "def", kind,
                  {"doc": ast.get_docstring(node) or None,
                   "end_line": node.end_lineno})
        self.stack.append(node.name)
        if kind != "ClassDef":
            a = node.args
            for grp, is_kwonly in ((a.posonlyargs, False), (a.args, False),
                                   (a.kwonlyargs, True)):
                for arg in grp:
                    self.emit(arg.lineno, arg.col_offset, arg.arg, "param",
                              "arg", {"kwonly": is_kwonly})
            for arg in (a.vararg, a.kwarg):
                if arg is not None:
                    self.emit(arg.lineno, arg.col_offset, arg.arg, "param",
                              "arg", {"star": True})
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node):
        self._fn(node, "FunctionDef")

    def visit_AsyncFunctionDef(self, node):
        self._fn(node, "FunctionDef")

    def visit_ClassDef(self, node):
        self._fn(node, "ClassDef")

    # ---- nodes SCIP indexes but that carry no ast.Name (glue round 2)
    def _dotted(self, line, bcol, dotted, module):
        """Emit one row per segment of a dotted name starting at bcol."""
        off = bcol
        for seg in dotted.split("."):
            self.emit(line, off, seg, "import", "alias",
                      {"module": module, "dotted": dotted})
            off += len(seg.encode("utf-8")) + 1        # segment + '.'

    def _alias(self, node, module):
        for a in node.names:
            self._dotted(a.lineno, a.col_offset, a.name, module)

    def visit_Import(self, node):
        self._alias(node, None)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            # `from <module> import ...` — no node covers <module>; it starts
            # right after the keyword, 5 bytes in ("from ").
            self._dotted(node.lineno, node.col_offset + 5, node.module,
                         node.module)
        self._alias(node, node.module)
        self.generic_visit(node)

    def visit_Call(self, node):
        # f(name=...) : SCIP emits an occurrence of the *parameter* symbol at
        # the keyword token, where there is no Name node.
        for kw in node.keywords:
            if kw.arg is not None:
                self.emit(kw.lineno, kw.col_offset, kw.arg, "kwarg", "keyword")
        # mark the callee token so the join can label `calls` from AST too
        f = node.func
        if isinstance(f, ast.Name):
            self.emit(f.lineno, f.col_offset, f.id, "callee", "Call")
        elif isinstance(f, ast.Attribute):
            bcol = f.end_col_offset - len(f.attr.encode("utf-8"))
            self.emit(f.end_lineno, bcol, f.attr, "callee", "Call")
        self.generic_visit(node)


def run(relpaths):
    rows, mods = [], []
    for rel in relpaths:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            print("MISSING %s" % rel, file=sys.stderr)
            continue
        raw = open(p, "rb").read()
        try:
            tree = ast.parse(raw.decode("utf-8"), filename=rel)
        except (SyntaxError, UnicodeDecodeError) as e:
            print("PARSE FAIL %s: %s" % (rel, e), file=sys.stderr)
            continue
        lines_b = raw.split(b"\n")
        w = Walker(rel, lines_b)
        w.visit(tree)
        rows.extend(w.rows)
        mods.append({"file": rel, "doc": ast.get_docstring(tree) or None,
                     "nonascii": any(b > 127 for b in raw)})
    return rows, mods


if __name__ == "__main__":
    slice_files = [os.path.join("src", "utils", f)
                   for f in sorted(os.listdir(os.path.join(REPO, "src", "utils")))
                   if f.endswith(".py")]
    inbound = json.load(open(os.path.join(OUT, "scip_slice.json")))["inbound_files"]
    targets = slice_files + [f for f in inbound if f not in slice_files]
    rows, mods = run(targets)
    with open(os.path.join(OUT, "ast_ctx.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(OUT, "ast_modules.json"), "w", encoding="utf-8") as f:
        json.dump(mods, f, indent=2)
    from collections import Counter
    c = Counter(r["ctx"] for r in rows)
    print("files: %d  rows: %d" % (len(mods), len(rows)))
    print(json.dumps(dict(c.most_common()), indent=2))
    print("files with non-ascii: %d" % sum(1 for m in mods if m["nonascii"]))
