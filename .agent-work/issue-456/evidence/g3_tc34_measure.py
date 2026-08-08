"""tc34, measured on the CURRENT corpus.

Re-runs the deleted stage's own recursion -- `node.body` only, copied verbatim
from the removed `supplement.walk` -- against today's source, and diffs it
against today's statement store. Every symbol in the difference is a definition
the map had NO page for while that stage drove the entity tree.
"""
import ast
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.code_map.discovery import discover_corpus  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[3]


def mod_of(rel):
    parts = rel.split("/")
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


old = set()
for rel in discover_corpus(ROOT):
    rel = rel.replace("\\", "/")
    try:
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        continue
    modname = mod_of(rel)

    def walk(node, prefix):
        for child in node.body:                       # the removed stage's rule
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                qual = f"{prefix}.{child.name}" if prefix else child.name
                old.add(f"{modname}:{qual}")
                walk(child, qual)

    walk(tree, "")

new = set()
with open(ROOT / ".code-map-g3" / "statements.jsonl", encoding="utf-8") as f:
    for line in f:
        st = json.loads(line)
        if st["p"] == "contains":
            new.add(st["o"])

gained = sorted(new - old)
print("body-only descent:", len(old), "definitions")
print("one-schema store :", len(new), "definitions")
print("definitions the removed stage could not see:", len(gained))
for symbol in gained:
    print("  +", symbol)
print("definitions the store misses that the old rule found:", sorted(old - new))
