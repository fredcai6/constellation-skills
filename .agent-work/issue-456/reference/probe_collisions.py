"""Classify the 75 flat-name collisions. The Commander claimed they were
nested-vs-top-level (the D2 mechanism); the cold critic says they are
overwhelmingly method-vs-method. Settle it by classification, not assertion.
"""
import ast
import os
import subprocess
import sys
from collections import Counter, defaultdict

root = sys.argv[1]
out = subprocess.run(["git", "ls-files", "*.py"], cwd=root,
                     capture_output=True, text=True, check=True)
files = [f for f in out.stdout.splitlines()
         if f.strip() and not f.startswith(".agent-work/")]

# name -> list of (kind_of_parent_chain)
sites = defaultdict(list)

DEF = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def walk(node, mod, chain):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, DEF):
            # what encloses it?
            if not chain:
                ctx = "top-level"
            elif all(isinstance(c, ast.ClassDef) for c in chain):
                ctx = "method"
            else:
                ctx = "closure"          # at least one function in the chain
            sites["%s.%s" % (mod, child.name)].append(ctx)
            walk(child, mod, chain + [child])
        else:
            walk(child, mod, chain)


for rel in files:
    raw = open(os.path.join(root, rel), "rb").read()
    tree = ast.parse(raw.decode("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"))
    mod = rel[:-3].replace("/", ".").replace("\\", ".")
    walk(tree, mod, [])

collisions = {k: v for k, v in sites.items() if len(v) > 1}
pairs = Counter()
for k, ctxs in collisions.items():
    pairs["+".join(sorted(set(ctxs))) if len(set(ctxs)) > 1
          else "%s-vs-%s" % (sorted(ctxs)[0], sorted(ctxs)[0])] += 1

ctx_total = Counter(c for v in sites.values() for c in v)

print("entities            :", sum(len(v) for v in sites.values()))
print("by enclosing context:", dict(ctx_total))
print("colliding names     :", len(collisions))
print("collision kinds:")
for k, n in pairs.most_common():
    print("   %-32s %d" % (k, n))
print()
print("closure-involving collisions (the D2 prose case):")
shown = 0
for k, v in collisions.items():
    if "closure" in v:
        print("   %-60s %s" % (k, v))
        shown += 1
        if shown >= 12:
            break
if not shown:
    print("   NONE")
