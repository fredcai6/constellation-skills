"""Baseline for THIS repo, excluding .agent-work -- the corpus gate 1's
committed thresholds will actually run against.

The prototype's numbers came from a 1,224-file repo. Committing those as
thresholds here would make the first CI run the experiment.
"""
import ast
import os
import subprocess
import sys
from collections import Counter

root = sys.argv[1]
out = subprocess.run(["git", "ls-files", "*.py"], cwd=root,
                     capture_output=True, text=True, check=True)
allfiles = [f for f in out.stdout.splitlines() if f.strip()]
files = [f for f in allfiles if not f.startswith(".agent-work/")]

entities = 0
by_dir = Counter()
kinds = Counter()
stmt_lines = 0
docstrings = 0
decorated = 0
nested = 0          # gate 2: nested defs are the collision source
flat_names = Counter()

for rel in files:
    p = os.path.join(root, rel)
    raw = open(p, "rb").read()
    tree = ast.parse(raw.decode("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"))
    stmt_lines += len(raw.decode("utf-8", "replace").splitlines())
    mod = rel[:-3].replace("/", ".").replace("\\", ".")
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        entities += 1
        kinds[type(node).__name__] += 1
        by_dir[rel.split("/")[0]] += 1
        if ast.get_docstring(node):
            docstrings += 1
        if getattr(node, "decorator_list", None):
            decorated += 1
        # a def whose parent chain contains another def/class is "nested"
        flat_names["%s.%s" % (mod, node.name)] += 1
    # count nesting properly: walk with parent tracking
    for parent in ast.walk(tree):
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for child in ast.iter_child_nodes(parent):
                for sub in ast.walk(child):
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        nested += 1
                        break

collisions = {k: v for k, v in flat_names.items() if v > 1}

print("files tracked (all)   :", len(allfiles))
print("files in corpus       :", len(files), "  (.agent-work excluded)")
print("source lines          :", stmt_lines)
print("entities              :", entities)
print("  kinds               :", dict(kinds))
print("  with docstring      :", docstrings)
print("  decorated           :", decorated)
print("nested def/class      :", nested)
print()
print("WITHDRAWN -- DO NOT USE THE NEXT NUMBER AS A D2 MEASUREMENT.")
print("  flat-name groups (module.name model) :", len(collisions))
print("  This models the symbol as `module.name`. That is NOT what the")
print("  extractor emits: astx.py:_func uses `mod:{clsstack[-1]}.{name}`")
print("  whenever ANY class is on the stack, so methods are ALREADY")
print("  qualified by their class and cannot collide this way. Every group")
print("  listed below is an artefact of the wrong model -- setUp/tearDown")
print("  across sibling test classes, which the real rule keeps distinct.")
print("  THE REAL D2 MEASUREMENT IS 4 COLLISIONS. Authority:")
print("    probe_d2.py -> d2_collisions.txt   (simulates the ACTUAL rule)")
print("    probe_arms.py -> d2_arms.txt       (D2's second arm: 0 here)")
for k, v in sorted(collisions.items(), key=lambda x: -x[1])[:6]:
    print("   x%d  %s   [artefact]" % (v, k))
print("top dirs:")
for d, n in by_dir.most_common(8):
    print("   %-14s %5d" % (d, n))
