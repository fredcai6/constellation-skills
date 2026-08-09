"""D2 has TWO arms. Count the occurrences of each shape on this corpus.

astx.py:visit_ClassDef has NO enclosing-chain branch:
    sym = mod:Name            if not clsstack
          mod:{clsstack[-1]}.Name  otherwise
so a class defined inside a FUNCTION (clsstack empty) is emitted as if
module-level. astx.py:_func does have such a branch (elif len(encl) > 1).
"""
import ast
import os
import subprocess
import sys
from collections import Counter

root = sys.argv[1]
out = subprocess.run(["git", "ls-files", "*.py"], cwd=root,
                     capture_output=True, text=True, check=True)
files = [f for f in out.stdout.splitlines()
         if f.strip() and not f.startswith(".agent-work/")]

shapes = Counter()
FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)


def walk(node, clsstack, funcdepth):
    for ch in ast.iter_child_nodes(node):
        if isinstance(ch, ast.ClassDef):
            if funcdepth and not clsstack:
                shapes["class inside a function (clsstack EMPTY)"] += 1
            elif funcdepth and clsstack:
                shapes["class inside a method"] += 1
            else:
                shapes["class at module/class level"] += 1
            walk(ch, clsstack + [ch.name], funcdepth)
        elif isinstance(ch, FUNC):
            if clsstack and funcdepth:
                shapes["closure inside a method"] += 1
            elif clsstack:
                shapes["method in a class"] += 1
            elif funcdepth:
                shapes["closure inside a module-level function"] += 1
            else:
                shapes["module-level function"] += 1
            walk(ch, clsstack, funcdepth + 1)
        else:
            walk(ch, clsstack, funcdepth)


for rel in files:
    raw = open(os.path.join(root, rel), "rb").read()
    tree = ast.parse(raw.decode("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"))
    walk(tree, [], 0)

for k, n in shapes.most_common():
    print("%-46s %5d" % (k, n))
print()
print("D2 arm 1 (closure-in-method, symbol drops the method) : %d occurrences"
      % shapes["closure inside a method"])
print("D2 arm 2 (class-in-function, named as module-level)   : %d occurrences  <- fixture-only if 0"
      % shapes["class inside a function (clsstack EMPTY)"])
