import sys, re
sys.path.insert(0, "tests")
import test_cli_retirement_guard as g
FOLLOW = re.compile(g._ENGINE_STANDIN + r"[ \t]+([A-Za-z][A-Za-z'-]*)")
n = 0
for path, where, text, whole in g.GUARD_TEXTS:
    for m in FOLLOW.finditer(text):
        if m.group(1) in g.ENGINE_VERBS:
            continue
        n += 1
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        line = text[line_start: line_end if line_end != -1 else len(text)]
        before = line[:m.start()-line_start]; after = line[m.end()-line_start:]
        span = "CODESPAN" if (before.count("`") % 2 == 1 and "`" in after) else "bare    "
        kind = "JSON" if not whole else "MD  "
        ex = " ".join(text[max(0,m.start()-45):m.end()+25].split())
        print(f"{n:2d} {kind} {span} {path.split('/')[-1][:34]:34s} ...{ex}...")
