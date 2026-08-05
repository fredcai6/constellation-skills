"""Independent docstring/comment census over f1Brainz source, via Python's ast.

Method
------
Parse every .py file under the pyright `include` roots that scip-python
indexed (src/ + scripts/ + run_*.py, i.e. the 443 documents). For each
module, class, function and async function:
  - docstring: ast.get_docstring(node) is non-empty
  - leading comment: the physical line immediately above the def/class
    (skipping decorators and blank lines) starts with '#'
  - either: docstring or leading comment
Also count module-level assignments (containers) and whether they have a
trailing/leading comment, since those never carry docstrings at all.

Read-only. Prints JSON.
"""

import ast, io, json, os, sys
from collections import Counter

ROOT = r"C:\Programs\f1Brainz"
DOC_DIRS = ["src", "scripts"]

c = Counter()
no_doc_examples = {"function": [], "class": []}


def leading_comment(lines, node):
    ln = node.lineno - 1
    if getattr(node, "decorator_list", None):
        ln = min(d.lineno for d in node.decorator_list) - 1
    i = ln - 1
    while i >= 0 and not lines[i].strip():
        i -= 1
    return i >= 0 and lines[i].lstrip().startswith("#")


files = [os.path.join(ROOT, l.strip()) for l in io.open(r"indexed_files.txt", encoding="utf-8") if l.strip()]
_skip = []
for d in []:
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, d)):
        dirnames[:] = [x for x in dirnames
                       if x not in (".venv", "venv", "__pycache__", "node_modules")]
        for fn in filenames:
            if fn.endswith(".py"):
                files.append(os.path.join(dirpath, fn))
for fn in []:
    if fn.endswith(".py"):
        files.append(os.path.join(ROOT, fn))

for f in files:
    try:
        src = io.open(f, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except SyntaxError:
        c["parse_failed"] += 1
        continue
    lines = src.splitlines()
    c["files"] += 1
    c["module"] += 1
    if ast.get_docstring(tree):
        c["module_doc"] += 1

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            c["function"] += 1
            d = bool(ast.get_docstring(node))
            lc = leading_comment(lines, node)
            if d:
                c["function_doc"] += 1
            if lc:
                c["function_leading_comment"] += 1
            if d or lc:
                c["function_doc_or_comment"] += 1
            elif len(no_doc_examples["function"]) < 5:
                no_doc_examples["function"].append(
                    os.path.relpath(f, ROOT) + ":" + str(node.lineno) + " " + node.name)
            if node.name.startswith("_"):
                c["function_private"] += 1
                if d:
                    c["function_private_doc"] += 1
            else:
                c["function_public"] += 1
                if d:
                    c["function_public_doc"] += 1
        elif isinstance(node, ast.ClassDef):
            c["class"] += 1
            d = bool(ast.get_docstring(node))
            lc = leading_comment(lines, node)
            if d:
                c["class_doc"] += 1
            if lc:
                c["class_leading_comment"] += 1
            if d or lc:
                c["class_doc_or_comment"] += 1
            elif len(no_doc_examples["class"]) < 5:
                no_doc_examples["class"].append(
                    os.path.relpath(f, ROOT) + ":" + str(node.lineno) + " " + node.name)

    # module-level containers (assignments at module scope)
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            c["module_level_assignment"] += 1
            if leading_comment(lines, node):
                c["module_level_assignment_comment"] += 1

    # class-level fields (dataclass attrs etc.)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for st in node.body:
                if isinstance(st, (ast.Assign, ast.AnnAssign)):
                    c["class_field"] += 1
                    if leading_comment(lines, st):
                        c["class_field_comment"] += 1


def pct(a, b):
    return round(100.0 * c[a] / c[b], 1) if c[b] else None


res = {
    "counts": dict(c),
    "coverage_pct": {
        "module_docstring": pct("module_doc", "module"),
        "class_docstring": pct("class_doc", "class"),
        "class_doc_or_comment": pct("class_doc_or_comment", "class"),
        "function_docstring": pct("function_doc", "function"),
        "function_doc_or_comment": pct("function_doc_or_comment", "function"),
        "public_function_docstring": pct("function_public_doc", "function_public"),
        "private_function_docstring": pct("function_private_doc", "function_private"),
        "module_level_assignment_comment": pct("module_level_assignment_comment",
                                               "module_level_assignment"),
        "class_field_comment": pct("class_field_comment", "class_field"),
    },
    "undocumented_examples": no_doc_examples,
}
outdir = os.path.dirname(os.path.abspath(__file__))
json.dump(res, open(os.path.join(outdir, "docstring_census_indexed.json"), "w",
                    encoding="utf-8"), indent=2)
print(json.dumps(res, indent=2))
