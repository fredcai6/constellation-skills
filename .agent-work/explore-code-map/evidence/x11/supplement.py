"""Supplementary AST pass over f1Brainz/src/utils (READ-ONLY).

Every fact fetched here is a MEASURED GAP in the statement vocabulary: the
statement store should have carried it and did not. Each is tagged with a gap
id so x11-result.md can enumerate them.

Output: evidence/x11/supplement.json
"""
import ast
import json
import pathlib
import sys

SRC = pathlib.Path(r"C:\Programs\f1Brainz\src\utils")
OUT = pathlib.Path(__file__).parent / "supplement.json"

# gap-id -> (what we had to fetch, why the store could not answer)
GAPS = {
    "G1-kind": "entity kind (class / function / method / async / property)",
    "G2-signature": "rendered signature: annotations, defaults, *args/**kwargs, return type",
    "G3-decorators": "decorator list (@classmethod, @staticmethod, @dataclass, ...)",
    "G4-docbody": "docstring body past the summary line (Args/Returns/Raises/Examples)",
    "G5-span": "entity end line / line count",
    "G6-dunder": "module __all__ / re-export surface",
    "G7-value": "the VALUE and annotation of a module-level constant (store records only the name, via `writes`)",
    "G8-annassign": "annotation-only attributes (dataclass fields, ClassVar decls) -- the store has NO statement of any kind for these",
}


def attrs_of(node):
    """Annotated / assigned attributes directly in a class or module body."""
    out = []
    for n in node.body:
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            out.append({
                "name": n.target.id,
                "line": n.lineno,
                "annotation": ast.unparse(n.annotation),
                "value": ast.unparse(n.value) if n.value is not None else None,
                "form": "annotation-only" if n.value is None else "annotated-assign",
            })
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    out.append({
                        "name": t.id,
                        "line": n.lineno,
                        "annotation": None,
                        "value": ast.unparse(n.value),
                        "form": "assign",
                    })
    return out


def sym(module: str, qual: str) -> str:
    """x7b symbol scheme: 'src.utils.config:Config.load_config'."""
    return f"{module}:{qual}" if qual else f"{module}:"


def sig_of(node) -> str:
    a = node.args
    parts = []
    posonly = getattr(a, "posonlyargs", [])

    def one(arg, default=None):
        s = arg.arg
        if arg.annotation is not None:
            s += ": " + ast.unparse(arg.annotation)
        if default is not None:
            s += ("=" if arg.annotation is None else " = ") + ast.unparse(default)
        return s

    defaults = list(a.defaults)
    positional = posonly + a.args
    pad = [None] * (len(positional) - len(defaults)) + defaults
    for arg, d in zip(posonly, pad[: len(posonly)]):
        parts.append(one(arg, d))
    if posonly:
        parts.append("/")
    for arg, d in zip(a.args, pad[len(posonly):]):
        parts.append(one(arg, d))
    if a.vararg is not None:
        parts.append("*" + one(a.vararg))
    elif a.kwonlyargs:
        parts.append("*")
    for arg, d in zip(a.kwonlyargs, a.kw_defaults):
        parts.append(one(arg, d))
    if a.kwarg is not None:
        parts.append("**" + one(a.kwarg))
    ret = ""
    if node.returns is not None:
        ret = " -> " + ast.unparse(node.returns)
    return f"({', '.join(parts)}){ret}"


def doc_split(node):
    d = ast.get_docstring(node, clean=True)
    if not d:
        return None, None
    lines = d.strip().split("\n")
    summary = lines[0].strip()
    body = "\n".join(lines[1:]).strip()
    return summary, (body or None)


def main():
    out = {"gaps": GAPS, "entities": {}, "modules": {}}
    for path in sorted(SRC.glob("*.py")):
        modname = "src.utils" if path.name == "__init__.py" else f"src.utils.{path.stem}"
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        summary, body = doc_split(tree)
        srclines = path.read_text(encoding="utf-8").splitlines()
        dunder_all = None
        for n in tree.body:
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name) and t.id == "__all__":
                        try:
                            dunder_all = ast.literal_eval(n.value)
                        except Exception:
                            dunder_all = None
        out["modules"][modname] = {
            "file": f"src/utils/{path.name}",
            "loc": len(srclines),
            "doc_summary": summary,       # G4 (store has this)
            "doc_body": body,             # G4-docbody GAP
            "all": dunder_all,            # G6-dunder GAP
            "attrs": attrs_of(tree),      # G7-value / G8-annassign GAP
        }

        def walk(node, prefix):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    qual = f"{prefix}.{child.name}" if prefix else child.name
                    key = sym(modname, qual)
                    s, b = doc_split(child)
                    decos = [ast.unparse(d) for d in child.decorator_list]
                    if isinstance(child, ast.ClassDef):
                        kind = "class"
                        signature = None
                        bases = [ast.unparse(x) for x in child.bases]
                    else:
                        kind = "method" if prefix else "function"
                        if isinstance(child, ast.AsyncFunctionDef):
                            kind = "async " + kind
                        if "property" in decos:
                            kind = "property"
                        elif "staticmethod" in decos:
                            kind = "static method"
                        elif "classmethod" in decos:
                            kind = "class method"
                        signature = sig_of(child)
                        bases = None
                    out["entities"][key] = {
                        "kind": kind,              # G1
                        "signature": signature,    # G2
                        "decorators": decos,       # G3
                        "doc_summary": s,
                        "doc_body": b,             # G4
                        "line": child.lineno,      # store has this
                        "end_line": getattr(child, "end_lineno", None),  # G5
                        "bases": bases,
                        "attrs": attrs_of(child) if isinstance(child, ast.ClassDef) else None,
                    }
                    walk(child, qual)

        walk(tree, "")
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("entities:", len(out["entities"]), "modules:", len(out["modules"]))
    print("wrote", OUT)


if __name__ == "__main__":
    sys.exit(main())
