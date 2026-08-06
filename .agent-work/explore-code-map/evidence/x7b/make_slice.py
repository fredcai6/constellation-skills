"""Define the x7b slice: src/utils/*.py plus every src/ file that imports it.

Emits slice_files.txt (repo-relative, backslash form, matching SCIP relpaths)
and slice_manifest.json splitting core (src/utils) from importers.
"""
import ast
import json
import os
import sys

ROOT = r"C:\Programs\f1Brainz"
SRC = os.path.join(ROOT, "src")


def modname(path):
    rel = os.path.relpath(path, ROOT)
    parts = rel.replace("\\", "/").split("/")
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def resolve_relative(mod, level, name):
    parts = mod.split(".")
    # for a package __init__, mod already IS the package
    base = parts[: len(parts) - level + 1] if level >= 1 else parts
    if name:
        base = base + name.split(".")
    return ".".join(base)


def imports_utils(path):
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except Exception:
        return False
    mod = modname(path)
    is_pkg = path.endswith("__init__.py")
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            if n.level:
                lvl = n.level - 1 if is_pkg else n.level
                target = resolve_relative(mod, lvl + 1, n.module or "")
            else:
                target = n.module or ""
            if target == "src.utils" or target.startswith("src.utils."):
                return True
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "src.utils" or a.name.startswith("src.utils."):
                    return True
    return False


def main():
    core, importers = [], []
    for dirpath, dirnames, filenames in os.walk(SRC):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, ROOT)
            if rel.replace("\\", "/").startswith("src/utils/"):
                core.append(rel)
            elif imports_utils(p):
                importers.append(rel)
    core.sort()
    importers.sort()
    out = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(out, "slice_files.txt"), "w", encoding="utf-8") as f:
        for r in core + importers:
            f.write(r + "\n")
    with open(os.path.join(out, "slice_manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"core": core, "importers": importers,
                   "n_core": len(core), "n_importers": len(importers)}, f, indent=2)
    print("core: %d  importers: %d  total: %d" % (len(core), len(importers),
                                                  len(core) + len(importers)))


if __name__ == "__main__":
    main()
