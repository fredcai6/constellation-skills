"""Probe: package-nesting depth per top-level dir, from git ls-files. Evidence
for gate g4's tier design — no source mutated, read-only analysis script."""
import collections
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/files.txt"
with open(path, encoding="utf-8") as f:
    files = [l.strip() for l in f if l.strip().endswith(".py")]

by_top = collections.defaultdict(list)
for rel in files:
    parts = rel.split("/")
    by_top[parts[0]].append(parts)

for top in sorted(by_top):
    parts_list = by_top[top]
    depths = collections.Counter(len(p) for p in parts_list)
    seconds = collections.Counter(
        p[1] for p in parts_list if len(p) > 2)
    print(f"{top}: {len(parts_list)} files, depth histogram {dict(sorted(depths.items()))}")
    if seconds:
        print(f"  subdirs: {dict(seconds.most_common(10))}")
