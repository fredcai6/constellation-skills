import sys, re, collections
sys.path.insert(0, "tests")
import test_cli_retirement_guard as g
FOLLOW = re.compile(g._ENGINE_STANDIN + r"[ \t]+([A-Za-z][A-Za-z'-]*)")
files, kinds, spans, sentences = set(), collections.Counter(), collections.Counter(), set()
for path, where, text, whole in g.GUARD_TEXTS:
    for m in FOLLOW.finditer(text):
        if m.group(1) in g.ENGINE_VERBS:
            continue
        files.add(path)
        kinds["JSON string leaf" if not whole else "Markdown/TOML whole file"] += 1
        ls = text.rfind("\n", 0, m.start()) + 1
        le = text.find("\n", m.end()); le = le if le != -1 else len(text)
        line = text[ls:le]
        before, after = line[:m.start()-ls], line[m.end()-ls:]
        spans["code-spanned" if (before.count("`") % 2 == 1 and "`" in after) else "bare"] += 1
        sentences.add(" ".join(text[max(0,m.start()-45):m.end()+25].split()))
total = sum(kinds.values())
print(f"{total} occurrences across {len(files)} files containing one; "
      f"{len(sentences)} distinct excerpts (the corpus mirrors each into skills/, the overlay and .baseline/)")
print(f"  by container: {dict(kinds)}")
print(f"  by span:      {dict(spans)}")
