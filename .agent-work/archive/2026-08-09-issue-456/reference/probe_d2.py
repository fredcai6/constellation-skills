"""Count REAL D2 collisions by simulating the store's actual symbol rule.

Two earlier probes modelled the symbol as `module.name`, which is not what
astx.py emits. The real rule, from astx.py:_func and :visit_ClassDef --

  ClassDef : mod:Name                       when clsstack is empty
             mod:{clsstack[-1]}.Name        otherwise   (INNERMOST class only)
  Function : mod:{clsstack[-1]}.name        when clsstack is non-empty
             here() + "." + name            when nested in a function
             mod:name                       otherwise

The bug (D2, documented in x13/render_map.py): when clsstack is non-empty the
method branch wins REGARDLESS of how deep inside a method the definition sits,
so a closure inside `Class.test_x` is named `mod:Class.<closure>` -- dropping
the method. And a class defined inside a function is named as if module-level.
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

DEF = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
sites = defaultdict(list)          # emitted symbol -> [(truth, rel, line)]


def walk(node, mod, clsstack, encl, truthstack):
    for ch in ast.iter_child_nodes(node):
        if isinstance(ch, ast.ClassDef):
            sym = ("%s:%s" % (mod, ch.name) if not clsstack
                   else "%s:%s.%s" % (mod, clsstack[-1], ch.name))
            truth = "%s:%s" % (mod, ".".join(truthstack + [ch.name]))
            sites[sym].append((truth, ch.lineno))
            walk(ch, mod, clsstack + [ch.name], encl + [sym], truthstack + [ch.name])
        elif isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if clsstack:
                sym = "%s:%s.%s" % (mod, clsstack[-1], ch.name)
            elif len(encl) > 1:
                sym = encl[-1] + "." + ch.name
            else:
                sym = "%s:%s" % (mod, ch.name)
            truth = "%s:%s" % (mod, ".".join(truthstack + [ch.name]))
            sites[sym].append((truth, ch.lineno))
            walk(ch, mod, clsstack, encl + [sym], truthstack + [ch.name])
        else:
            walk(ch, mod, clsstack, encl, truthstack)


for rel in files:
    raw = open(os.path.join(root, rel), "rb").read()
    tree = ast.parse(raw.decode("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"))
    mod = rel[:-3].replace("/", ".").replace("\\", ".")
    walk(tree, mod, [], [mod + ":"], [])

# A REAL collision: one emitted symbol, more than one distinct true entity.
collisions = {s: v for s, v in sites.items() if len({t for t, _ in v}) > 1}

kinds = Counter()
for s, v in collisions.items():
    depths = {t.split(":", 1)[1].count(".") for t, _ in v}
    kinds["mixed-depth (closure folded onto its class)" if len(depths) > 1
          else "same-depth siblings"] += 1

print("entities emitted     :", sum(len(v) for v in sites.values()))
print("distinct symbols     :", len(sites))
print("REAL D2 collisions   :", len(collisions), " (one symbol, >1 true entity)")
for k, n in kinds.most_common():
    print("   %-46s %d" % (k, n))
print()
print("examples (symbol -> the distinct true entities it merges):")
for s, v in sorted(collisions.items())[:10]:
    print("  %s" % s)
    for t in sorted({t for t, _ in v}):
        print("       <- %s" % t)
