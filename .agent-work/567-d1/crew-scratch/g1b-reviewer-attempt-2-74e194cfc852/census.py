"""r5: verify the census g2 depends on, in the unit the docstring now states."""
import sys, pathlib, re
sys.path.insert(0, str(pathlib.Path(".").resolve() / "tests"))
import test_cli_retirement_guard as G

def census(pat, subset=None):
    occ, files = 0, set()
    for path, where, text, whole in G.GUARD_TEXTS:
        if subset and not subset(path): continue
        n = len(pat.findall(text))
        if n: occ += n; files.add(path)
    return occ, len(files)

overlay = lambda p: p.startswith(".agent-work/templates/")
skills  = lambda p: p.startswith("skills/")
specs   = lambda p: p.startswith("specs/")
print(f"{'target':<28}{'corpus':>16}{'overlay':>16}{'skills/':>16}{'specs/':>14}")
for lbl, pat in [("<engine>", G.ENGINE_PLACEHOLDER_RE), ("CLI fallback", G.CLI_FALLBACK_RE),
                 ("stood-in-for command", G.ENGINE_STANDIN_COMMAND_RE),
                 ("engine invocation", G.ENGINE_INVOCATION_RE)]:
    c, o, s, sp = census(pat), census(pat, overlay), census(pat, skills), census(pat, specs)
    f = lambda t: f"{t[0]} occ/{t[1]} f"
    print(f"{lbl:<28}{f(c):>16}{f(o):>16}{f(s):>16}{f(sp):>14}")

print("\n=== the docstring's own claims, checked one by one")
eng_c, eng_f = census(G.ENGINE_PLACEHOLDER_RE); eng_oc, eng_of = census(G.ENGINE_PLACEHOLDER_RE, overlay)
fb_c, fb_f = census(G.CLI_FALLBACK_RE); fb_oc, fb_of = census(G.CLI_FALLBACK_RE, overlay)
for claim, got, want in [("overlay carries 16 of the corpus's 26 <engine> occurrences", (eng_oc, eng_c), (16, 26)),
                         ("across 6 of the 11 files containing one", (eng_of, eng_f), (6, 11)),
                         ("18 of its 34 CLI fallback occurrences", (fb_oc, fb_c), (18, 34)),
                         ("across 10 of the 21 files containing one", (fb_of, fb_f), (10, 21))]:
    print(f"  {'OK ' if got == want else 'NO '} {claim:<58} measured {got} vs stated {want}")

print("\n=== which overlay files g2 must sweep for <engine> (occurrences per file)")
for path, where, text, whole in G.GUARD_TEXTS:
    n = len(G.ENGINE_PLACEHOLDER_RE.findall(text))
    if n and overlay(path): print(f"  {n}  {path}  [{where if not whole else 'whole-file'}]")

print("\n=== the 40/27/31 code-span figures")
STAND = re.compile(G._ENGINE_STANDIN + r"[ \t]+[A-Za-z]+\b")
tot = 0; json_leaf = 0; spanned = 0; files = set(); excerpts = set()
for path, where, text, whole in G.GUARD_TEXTS:
    for m in STAND.finditer(text):
        word = text[m.start():m.end()].split()[-1]
        if word in G.ENGINE_VERBS: continue
        tot += 1; files.add(path); excerpts.add(" ".join(text[m.start():m.end()].split()))
        if path.endswith(".json"): json_leaf += 1
        line_start = text.rfind("\n", 0, m.start()) + 1
        if text.count("`", line_start, m.start()) % 2 == 1 and "`" in text[m.end():m.end()+40]:
            spanned += 1
print(f"  measured: {tot} occurrences across {len(files)} files containing one, "
      f"{len(excerpts)} distinct excerpts; {json_leaf} in JSON leaves; {spanned} code-spanned "
      f"({tot-spanned} bare)")
print(f"  docstring states: 40 across 25 files, 13 distinct, 27 JSON, 31 bare")
