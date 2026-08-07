"""x7b: pure-AST statement extractor with its own cross-file name resolution.

Python stdlib only (ast, os, json, hashlib). No SCIP, no type inference beyond
the two cheap rules stated in RESOLUTION RULES below.

Two passes:
  pass 1  index every src/**.py module's *module-level* binding table
          (defs, classes, assignments, imports and what each import binds)
  pass 2  walk the slice files, tracking scopes, and emit one statement per
          fact with the resolved symbol -- or an explicit unresolved marker.

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

Statement line shape (per the x7a brief):
  {"s","p","o","q":{"file","line","col"},"ref":"ast","hash"}
plus two measurement-only fields:
  "res"  internal|external|local|unresolved|literal
  "why"  failure class, present only when res == unresolved
"""
import ast
import builtins
import hashlib
import json
import os
import sys

ROOT = r"C:\Programs\f1Brainz"
# x13 change: pass 1 indexes src/ AND scripts/ AND tests/, so that names defined
# in scripts and tests resolve as internal (x7b indexed src/ only).
INDEX_DIRS = [os.path.join(ROOT, d) for d in ("src", "scripts", "tests")]
SRC = INDEX_DIRS[0]
BUILTINS = set(dir(builtins))

# ------------------------------------------------------------------ pass 1


def mod_of(path):
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    parts = rel.split("/")
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def pkg_of(path):
    m = mod_of(path)
    if path.endswith("__init__.py"):
        return m
    return m.rsplit(".", 1)[0] if "." in m else ""


def resolve_rel(pkg, level, name):
    parts = pkg.split(".") if pkg else []
    drop = level - 1
    base = parts[: len(parts) - drop] if drop else parts
    if name:
        base = base + name.split(".")
    return ".".join(base)


class ModuleTable:
    """Module-level bindings for one file."""

    def __init__(self, mod, path):
        self.mod = mod
        self.path = path
        self.defs = {}        # name -> 'func'|'class'|'var'
        self.imports = {}     # local name -> ('from', srcmod, origname) | ('mod', modname)
        self.stars = []       # modules star-imported
        self.bases = {}       # class name -> [base name strings]
        self.classes = {}     # class name -> set(member names)
        self.all = None       # __all__ contents if literal


def build_table(path):
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except Exception:
        return None, None
    mod, pkg = mod_of(path), pkg_of(path)
    t = ModuleTable(mod, path)
    for n in tree.body:
        _table_stmt(n, t, pkg)
    return t, tree


def _table_stmt(n, t, pkg):
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        t.defs[n.name] = "func"
    elif isinstance(n, ast.ClassDef):
        t.defs[n.name] = "class"
        t.bases[n.name] = [_dotted(b) for b in n.bases if _dotted(b)]
        members = set()
        for c in n.body:
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                members.add(c.name)
            elif isinstance(c, ast.Assign):
                for tg in c.targets:
                    if isinstance(tg, ast.Name):
                        members.add(tg.id)
            elif isinstance(c, ast.AnnAssign) and isinstance(c.target, ast.Name):
                members.add(c.target.id)
            elif isinstance(c, ast.ClassDef):
                members.add(c.name)
        t.classes[n.name] = members
    elif isinstance(n, ast.Assign):
        for tg in n.targets:
            if isinstance(tg, ast.Name):
                t.defs[tg.id] = "var"
                if tg.id == "__all__":
                    try:
                        t.all = [e.value for e in n.value.elts
                                 if isinstance(e, ast.Constant)]
                    except Exception:
                        pass
    elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
        t.defs[n.target.id] = "var"
    elif isinstance(n, ast.Import):
        for a in n.names:
            if a.asname:
                t.imports[a.asname] = ("mod", a.name)
            else:
                t.imports[a.name.split(".")[0]] = ("mod", a.name.split(".")[0])
    elif isinstance(n, ast.ImportFrom):
        srcmod = resolve_rel(pkg, n.level, n.module or "") if n.level else (n.module or "")
        for a in n.names:
            if a.name == "*":
                t.stars.append(srcmod)
            else:
                t.imports[a.asname or a.name] = ("from", srcmod, a.name)
    elif isinstance(n, (ast.If, ast.Try, ast.With)):
        for c in ast.iter_child_nodes(n):
            if isinstance(c, ast.stmt):
                _table_stmt(c, t, pkg)


def _dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


TABLES = {}      # module name -> ModuleTable


def pass1():
    for root in INDEX_DIRS:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
            for fn in sorted(filenames):
                if fn.endswith(".py"):
                    p = os.path.join(dirpath, fn)
                    t, _ = build_table(p)
                    if t:
                        TABLES[t.mod] = t


# ------------------------------------------------------------------ resolver

UNRES = "UNRESOLVED"


def chase(mod, name, hops=0):
    """Follow a (module, name) through re-exports to its defining module.
    Returns (symbol, res, why)."""
    if hops > 5:
        return UNRES, "unresolved", "reexport-depth"
    t = TABLES.get(mod)
    if t is None:
        # not an internal src/ module -> external (stdlib / third-party)
        return "%s:%s" % (mod, name), "external", None
    if name in t.defs:
        return "%s:%s" % (mod, name), "internal", None
    if name in t.imports:
        b = t.imports[name]
        if b[0] == "from":
            return chase(b[1], b[2], hops + 1)
        return b[1] + ":", ("internal" if b[1] in TABLES else "external"), None
    # submodule of a package?  `from src.utils import config`
    sub = mod + "." + name
    if sub in TABLES:
        return sub + ":", "internal", None
    for st in t.stars:
        st_t = TABLES.get(st)
        if st_t and (name in st_t.defs or name in st_t.imports):
            return chase(st, name, hops + 1)
    if t.stars:
        return UNRES, "unresolved", "star-import"
    return UNRES, "unresolved", "missing-in-module"


class Scope:
    def __init__(self, kind, parent=None, cls=None):
        self.kind = kind            # 'module'|'func'|'class'|'comp'
        self.parent = parent
        self.cls = cls              # enclosing class name, if any
        self.func_sym = None        # owning transformer symbol, for params
        self.names = {}             # local name -> 'param'|'assign'|'import'|'def'
        self.imports = {}           # local name -> same binding shape as ModuleTable.imports
        self.types = {}             # local name -> inferred class name (same module)
        self.multi = set()          # names assigned more than once (kills inference)
        self.globals = set()

    def bind(self, name, how, typ=None):
        if name in self.names and typ != self.types.get(name):
            self.multi.add(name)
        # a parameter reassigned in its own body is still that parameter
        if not (self.names.get(name) == "param" and how == "assign"):
            self.names[name] = how
        if typ and name not in self.multi:
            self.types[name] = typ

    def lookup(self, name):
        s = self
        while s is not None:
            if s.kind == "class" and s is not self:
                s = s.parent
                continue
            if name in s.names:
                return s
            s = s.parent
        return None


class Extractor(ast.NodeVisitor):
    def __init__(self, path, tree, core):
        self.path = path
        self.rel = os.path.relpath(path, ROOT)
        self.mod = mod_of(path)
        self.table = TABLES[self.mod]
        self.tree = tree
        self.core = core          # True if this file is in src/utils
        self.out = []
        self.scope = Scope("module")
        self.encl = [self.mod + ":"]     # enclosing transformer stack
        self.clsstack = []
        for k, v in self.table.defs.items():
            self.scope.bind(k, "def")
        for k in self.table.imports:
            self.scope.bind(k, "import")

    # -------------------------------------------------------- emit helpers
    def emit(self, s, p, o, line, col, res, why=None, extra=None):
        h = hashlib.sha1(("%s|%s|%s|%s|%s|%s" % (s, p, o, self.rel, line, col))
                         .encode("utf-8")).hexdigest()[:16]
        row = {"s": s, "p": p, "o": o,
               "q": {"file": self.rel.replace("\\", "/"), "line": line, "col": col},
               "ref": "ast", "hash": h, "res": res}
        if why:
            row["why"] = why
        if extra:
            row["q"].update(extra)
        self.out.append(row)

    def here(self):
        return self.encl[-1]

    # -------------------------------------------------------- name resolution
    def resolve_name(self, node):
        """ast.Name -> (symbol, res, why)"""
        name = node.id
        sc = self.scope.lookup(name)
        if sc is not None and sc.kind in ("func", "comp"):
            # R1a: a parameter is a *named* symbol owned by its function,
            # not an anonymous local -- same model SCIP uses.
            if sc.names.get(name) == "param" and sc.func_sym:
                return "%s.%s" % (sc.func_sym, name), "internal", None
            if name in sc.imports:                      # D4: function-scoped import
                return self.from_binding(sc.imports[name])
            return "local:%s" % name, "local", None
        # R2a: directly inside a class body, the class namespace wins over the
        # module namespace. Inside a *method* it does not -- Python skips the
        # class scope there -- so this is gated on the innermost scope.
        if (self.scope.kind == "class" and self.clsstack
                and name in self.table.classes.get(self.clsstack[-1], ())):
            return "%s:%s.%s" % (self.mod, self.clsstack[-1], name), "internal", None
        if name in self.table.defs:
            return "%s:%s" % (self.mod, name), "internal", None
        if name in self.table.imports:
            b = self.table.imports[name]
            if b[0] == "from":
                return chase(b[1], b[2])
            return b[1] + ":", ("internal" if b[1] in TABLES else "external"), None
        if name in BUILTINS:
            return "builtins:%s" % name, "external", None
        if self.table.stars:
            for st in self.table.stars:
                t = TABLES.get(st)
                if t and (name in t.defs or name in t.imports):
                    return chase(st, name)
            return UNRES, "unresolved", "star-import"
        return UNRES, "unresolved", "unbound-name"

    def from_binding(self, b):
        """Resolve an import binding tuple -> (symbol, res, why)."""
        if b[0] == "from":
            return chase(b[1], b[2])
        return b[1] + ":", ("internal" if b[1] in TABLES else "external"), None

    def class_member(self, cls, attr, mod=None):
        """Look attr up on class cls, walking same-module bases. -> symbol|None"""
        mod = mod or self.mod
        t = TABLES.get(mod)
        if t is None:
            return None
        seen, stack = set(), [cls]
        while stack:
            c = stack.pop(0)
            if c in seen:
                continue
            seen.add(c)
            if c in t.classes and attr in t.classes[c]:
                return "%s:%s.%s" % (mod, c, attr)
            for b in t.bases.get(c, []):
                if "." in b:
                    continue
                if b in t.classes:
                    stack.append(b)
                elif b in t.imports and t.imports[b][0] == "from":
                    _m, _n = t.imports[b][1], t.imports[b][2]
                    r = self.class_member(_n, attr, _m)
                    if r:
                        return r
        return None

    def attr_via_import(self, b, dotted, head, attr, depth):
        """`head` is bound by an import; resolve `head....attr` through it."""
        if b[0] == "mod":
            full = b[1] + dotted[len(head):]
            return chase(full, attr)
        # from-import: base is a class/func/module in another module
        sym, res, why = chase(b[1], b[2])
        if res == "internal" and sym.endswith(":"):
            mid = dotted.split(".")[1:]
            return chase(".".join([sym[:-1]] + mid), attr)
        if depth > 1:
            return UNRES, "unresolved", "chained-attribute"
        if res == "internal":
            m, mem = sym.split(":", 1)
            if "." not in mem:
                r = self.class_member(mem, attr, m)
                if r:
                    return r, "internal", None
            return "%s.%s" % (sym, attr), "internal", None
        if res == "external":
            return "%s.%s" % (sym, attr), "external", None
        return UNRES, "unresolved", why or "dispatch-unknown-base"

    def resolve_attr(self, node):
        """ast.Attribute -> (symbol, res, why)"""
        attr = node.attr
        base = node.value
        # self.x inside a method
        if isinstance(base, ast.Name) and base.id == "self" and self.clsstack:
            r = self.class_member(self.clsstack[-1], attr)
            if r:
                return r, "internal", None
            return "%s:%s.%s" % (self.mod, self.clsstack[-1], attr), "internal", None
        if isinstance(base, ast.Name) and base.id == "cls" and self.clsstack:
            r = self.class_member(self.clsstack[-1], attr)
            if r:
                return r, "internal", None
            return "%s:%s.%s" % (self.mod, self.clsstack[-1], attr), "internal", None
        dotted = _dotted(base)
        if dotted:
            head = dotted.split(".")[0]
            # depth > 1 means the base is itself an attribute chain (a.b.c).
            # We know the type of `a` at best; the type of the FIELD `a.b` needs
            # real inference. Guessing would silently attribute `c` to a's class,
            # so for non-module heads we stop and say so.
            depth = len(dotted.split("."))
            sc = self.scope.lookup(head)
            islocal = sc is not None and sc.kind in ("func", "comp")
            # D4: a function-scoped import is a real binding, not an opaque local
            if islocal and head in sc.imports:
                return self.attr_via_import(sc.imports[head], dotted, head, attr, depth)
            # inferred local type (single-assignment or annotation)
            if islocal:
                typ = None
                s = self.scope
                while s is not None:
                    if head in s.types and head not in s.multi:
                        typ = s.types[head]
                        break
                    s = s.parent
                if typ and depth == 1:
                    tm, tc = typ
                    r = self.class_member(tc, attr, tm)
                    if r:
                        return r, "internal", None
                    return "%s:%s.%s" % (tm, tc, attr), "internal", None
                if typ:
                    return UNRES, "unresolved", "chained-attribute"
                return UNRES, "unresolved", "dispatch-unknown-base"
            # module alias or dotted module path
            if head in self.table.imports:
                return self.attr_via_import(self.table.imports[head],
                                            dotted, head, attr, depth)
            # class defined in this module
            if head in self.table.classes:
                if depth > 1:
                    return UNRES, "unresolved", "chained-attribute"
                r = self.class_member(head, attr)
                if r:
                    return r, "internal", None
                return "%s:%s.%s" % (self.mod, head, attr), "internal", None
            if head in self.table.defs:
                return UNRES, "unresolved", "dispatch-unknown-base"
            if head in BUILTINS:
                return "builtins:%s.%s" % (head, attr), "external", None
        return UNRES, "unresolved", "dispatch-unknown-base"

    def resolve_expr(self, node):
        if isinstance(node, ast.Name):
            return self.resolve_name(node)
        if isinstance(node, ast.Attribute):
            return self.resolve_attr(node)
        return UNRES, "unresolved", "non-name-expr"

    def pos_of(self, node):
        """Position of the *identifier* SCIP would mark (0-based line/col)."""
        if isinstance(node, ast.Attribute):
            return node.end_lineno - 1, node.end_col_offset - len(node.attr)
        return node.lineno - 1, node.col_offset

    # -------------------------------------------------------- type inference
    def infer_type(self, value):
        """`v = Known(...)` / annotation -> (module, class) or None."""
        if isinstance(value, ast.Call):
            sym, res, _ = self.resolve_expr(value.func)
            if res == "internal" and ":" in sym:
                m, mem = sym.split(":", 1)
                t = TABLES.get(m)
                if t and mem in t.classes:
                    return (m, mem)
        return None

    def infer_annotation(self, ann):
        if ann is None:
            return None
        d = _dotted(ann)
        if not d:
            return None
        head = d.split(".")[-1]
        if head in self.table.classes:
            return (self.mod, head)
        first = d.split(".")[0]
        if first in self.table.imports:
            b = self.table.imports[first]
            if b[0] == "from":
                sym, res, _ = chase(b[1], b[2])
                if res == "internal" and ":" in sym:
                    m, mem = sym.split(":", 1)
                    t = TABLES.get(m)
                    if t and mem in t.classes:
                        return (m, mem)
        return None

    # -------------------------------------------------------- visitors
    def run(self):
        for n in self.tree.body:
            self.visit(n)
        doc = ast.get_docstring(self.tree)
        if doc:
            self.emit(self.mod + ":", "documents", doc.strip().splitlines()[0][:160],
                      0, 0, "literal")
        return self.out

    def visit_ClassDef(self, node):
        sym = "%s:%s" % (self.mod, node.name) if not self.clsstack else \
              "%s:%s.%s" % (self.mod, self.clsstack[-1], node.name)
        self.emit(self.here(), "contains", sym, node.lineno - 1, node.col_offset, "internal")
        doc = ast.get_docstring(node)
        if doc:
            self.emit(sym, "documents", doc.strip().splitlines()[0][:160],
                      node.lineno - 1, node.col_offset, "literal")
        for b in node.bases:
            s2, r2, w2 = self.resolve_expr(b)
            ln, cl = self.pos_of(b)
            self.emit(sym, "inherits", s2, ln, cl, r2, w2)
        for d in node.decorator_list:
            self.visit(d)
        self.clsstack.append(node.name)
        prev = self.scope
        self.scope = Scope("class", prev, node.name)
        self.encl.append(sym)
        for c in node.body:
            self.visit(c)
        self.encl.pop()
        self.scope = prev
        self.clsstack.pop()

    def _func(self, node):
        if self.clsstack:
            sym = "%s:%s.%s" % (self.mod, self.clsstack[-1], node.name)
        elif len(self.encl) > 1:
            sym = self.here() + "." + node.name
        else:
            sym = "%s:%s" % (self.mod, node.name)
        self.emit(self.here(), "contains", sym, node.lineno - 1, node.col_offset, "internal")
        doc = ast.get_docstring(node)
        if doc:
            self.emit(sym, "documents", doc.strip().splitlines()[0][:160],
                      node.lineno - 1, node.col_offset, "literal")
        for d in node.decorator_list:
            self.visit(d)
        prev = self.scope
        self.scope = Scope("func", prev, self.clsstack[-1] if self.clsstack else None)
        self.scope.func_sym = sym
        args = node.args
        allargs = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
        if args.vararg:
            allargs.append(args.vararg)
        if args.kwarg:
            allargs.append(args.kwarg)
        for a in allargs:
            self.emit("%s.%s" % (sym, a.arg), "param-of", sym,
                      a.lineno - 1, a.col_offset, "internal")
            self.scope.bind(a.arg, "param", self.infer_annotation(a.annotation))
            if a.annotation is not None:
                self.visit(a.annotation)
        for d in list(args.defaults) + [d for d in args.kw_defaults if d]:
            self.visit(d)
        if node.returns is not None:
            self.visit(node.returns)
        self.encl.append(sym)
        # pre-bind local assignment targets so forward references read as local
        self._prebind(node)
        for c in node.body:
            self.visit(c)
        self.encl.pop()
        self.scope = prev

    visit_FunctionDef = _func
    visit_AsyncFunctionDef = _func

    def _prebind(self, fnode):
        for n in ast.walk(fnode):
            if n is fnode:
                continue
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.scope.bind(n.name, "def")
            elif isinstance(n, ast.Assign):
                typ = self.infer_type(n.value)
                for t in n.targets:
                    for nm in _target_names(t):
                        self.scope.bind(nm, "assign", typ if len(n.targets) == 1 else None)
            elif isinstance(n, ast.AnnAssign):
                for nm in _target_names(n.target):
                    self.scope.bind(nm, "assign", self.infer_annotation(n.annotation))
            elif isinstance(n, (ast.For, ast.AsyncFor)):
                for nm in _target_names(n.target):
                    self.scope.bind(nm, "assign")
            elif isinstance(n, (ast.With, ast.AsyncWith)):
                for it in n.items:
                    if it.optional_vars is not None:
                        for nm in _target_names(it.optional_vars):
                            self.scope.bind(nm, "assign")
            elif isinstance(n, ast.ExceptHandler) and n.name:
                self.scope.bind(n.name, "assign")
            elif isinstance(n, ast.comprehension):
                for nm in _target_names(n.target):
                    self.scope.bind(nm, "assign")
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                # x13 change (defect D4): record WHAT a function-scoped import
                # binds, not just that the name is taken. x7b bound the name and
                # dropped the target, so every call through a function-local
                # import resolved to `local:` and vanished from both the callee's
                # `referenced by` and the caller's `calls`.
                pkg = pkg_of(self.path)
                if isinstance(n, ast.ImportFrom):
                    srcmod = resolve_rel(pkg, n.level, n.module or "") if n.level \
                        else (n.module or "")
                for a in n.names:
                    if a.name == "*":
                        continue
                    local = a.asname or a.name.split(".")[0]
                    self.scope.bind(local, "import")
                    if isinstance(n, ast.ImportFrom):
                        self.scope.imports[local] = ("from", srcmod, a.name)
                    else:
                        self.scope.imports[local] = (
                            "mod", a.name if a.asname else a.name.split(".")[0])
            elif isinstance(n, ast.Global):
                self.scope.globals.update(n.names)
            elif isinstance(n, ast.NamedExpr):
                for nm in _target_names(n.target):
                    self.scope.bind(nm, "assign")

    def visit_Assign(self, node):
        typ = self.infer_type(node.value)
        self.visit(node.value)
        for t in node.targets:
            self._store(t, typ)

    def visit_AnnAssign(self, node):
        if node.value is not None:
            self.visit(node.value)
        self.visit(node.annotation)
        self._store(node.target, self.infer_annotation(node.annotation))

    def visit_AugAssign(self, node):
        self.visit(node.value)
        self._store(node.target, None)
        self._ref(node.target, "reads")

    def _store(self, t, typ=None):
        if isinstance(t, (ast.Tuple, ast.List)):
            for e in t.elts:
                self._store(e, None)
            return
        if isinstance(t, ast.Starred):
            return self._store(t.value, None)
        if isinstance(t, ast.Subscript):
            self.visit(t.value)
            self.visit(t.slice)
            s, r, w = self.resolve_expr(t.value)
            ln, cl = self.pos_of(t.value)
            self.emit(self.here(), "writes", s + "[]", ln, cl, r, w)
            return
        if isinstance(t, ast.Name):
            if self.scope.kind == "module" or self.scope.kind == "class":
                pass
            else:
                self.scope.bind(t.id, "assign", typ)
        if isinstance(t, (ast.Name, ast.Attribute)):
            if isinstance(t, ast.Attribute):
                self.visit(t.value)
            self._ref(t, "writes")

    def _ref(self, node, pred):
        s, r, w = self.resolve_expr(node)
        ln, cl = self.pos_of(node)
        self.emit(self.here(), pred, s, ln, cl, r, w)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self._store(node)
            return
        if isinstance(node.ctx, ast.Del):
            self._ref(node, "writes")
            return
        self._ref(node, "reads")

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Store):
            self.visit(node.value)
            self._ref(node, "writes")
            return
        self.visit(node.value)
        self._ref(node, "reads")

    def visit_Call(self, node):
        f = node.func
        if isinstance(f, (ast.Name, ast.Attribute)):
            if isinstance(f, ast.Name) and f.id in ("getattr", "setattr",
                                                    "__import__", "eval", "exec"):
                ln, cl = self.pos_of(f)
                self.emit(self.here(), "calls", UNRES, ln, cl, "unresolved", "dynamic")
            else:
                s, r, w = self.resolve_expr(f)
                ln, cl = self.pos_of(f)
                self.emit(self.here(), "calls", s, ln, cl, r, w)
            if isinstance(f, ast.Attribute):
                self.visit(f.value)
        else:
            self.visit(f)
        for a in node.args:
            self.visit(a)
        for k in node.keywords:
            self.visit(k.value)

    def visit_Import(self, node):
        for a in node.names:
            self.emit(self.mod + ":", "imports", a.name + ":",
                      node.lineno - 1, node.col_offset,
                      "internal" if a.name in TABLES else "external")

    def visit_ImportFrom(self, node):
        pkg = pkg_of(self.path)
        srcmod = resolve_rel(pkg, node.level, node.module or "") if node.level \
            else (node.module or "")
        for a in node.names:
            if a.name == "*":
                self.emit(self.mod + ":", "imports", srcmod + ":*",
                          node.lineno - 1, node.col_offset,
                          "unresolved", "star-import")
            else:
                s, r, w = chase(srcmod, a.name)
                self.emit(self.mod + ":", "imports", s,
                          node.lineno - 1, node.col_offset, r, w)


def _target_names(t):
    if isinstance(t, ast.Name):
        return [t.id]
    if isinstance(t, (ast.Tuple, ast.List)):
        out = []
        for e in t.elts:
            out += _target_names(e)
        return out
    if isinstance(t, ast.Starred):
        return _target_names(t.value)
    return []


# ------------------------------------------------------------------ main

def main():
    import time
    sys.setrecursionlimit(20000)
    here = os.path.dirname(os.path.abspath(__file__))
    manifest = json.load(open(os.path.join(here, "slice_manifest.json"), encoding="utf-8"))
    # x13 change: every manifest file is core.
    files = sorted(set(manifest["core"]) | set(manifest["importers"]))
    t0 = time.time()
    pass1()
    t1 = time.time()
    print("pass1: %d modules indexed (%.1fs)" % (len(TABLES), t1 - t0))
    failed = []
    nrows = 0
    outp = os.path.join(here, "statements.jsonl")
    with open(outp, "w", encoding="utf-8", newline="\n") as f:
        for rel in files:
            p = os.path.join(ROOT, rel)
            try:
                tree = ast.parse(open(p, encoding="utf-8").read())
            except Exception as e:
                failed.append((rel, "parse: " + str(e)))
                continue
            if mod_of(p) not in TABLES:
                failed.append((rel, "no module table"))
                continue
            ex = Extractor(p, tree, True)
            try:
                rows = ex.run()
            except RecursionError:
                failed.append((rel, "recursion"))
                continue
            for r in rows:
                f.write(json.dumps(r) + "\n")
            nrows += len(rows)
    t2 = time.time()
    print("statements: %d over %d files (%d failures) (%.1fs)"
          % (nrows, len(files), len(failed), t2 - t1))
    for r in failed:
        print("  FAILED:", r)
    json.dump({"files": len(files), "statements": nrows,
               "modules_indexed": len(TABLES),
               "failures": [list(x) for x in failed],
               "pass1_sec": round(t1 - t0, 1), "pass2_sec": round(t2 - t1, 1)},
              open(os.path.join(here, "extract_report.json"), "w", encoding="utf-8"),
              indent=1)


if __name__ == "__main__":
    main()
