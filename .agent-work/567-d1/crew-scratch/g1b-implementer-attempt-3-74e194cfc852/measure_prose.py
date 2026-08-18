import sys, re, collections
sys.path.insert(0, "tests")
import test_cli_retirement_guard as g

# 1. Stand-in followed by whitespace and an ordinary English word (not an engine verb).
FOLLOW = re.compile(g._ENGINE_STANDIN + r"[ \t]+([A-Za-z][A-Za-z'-]*)")
sites, in_json, codespanned, words = [], 0, 0, collections.Counter()
for path, where, text, whole in g.GUARD_TEXTS:
    for m in FOLLOW.finditer(text):
        word = m.group(1)
        if word in g.ENGINE_VERBS:
            continue
        addr = f"{where}:{text.count(chr(10),0,m.start())+1}" if whole else where
        sites.append(addr)
        words[word] += 1
        if not whole:               # a JSON string leaf
            in_json += 1
        # code-spanned: a backtick opens before the stand-in on this line and closes after the word
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        line = text[line_start: line_end if line_end != -1 else len(text)]
        before, after = line[:m.start()-line_start], line[m.end()-line_start:]
        if before.count("`") % 2 == 1 and "`" in after:
            codespanned += 1
print(f"stand-in + whitespace + ordinary English word: {len(sites)} occurrences "
      f"across {len(set(s.split(':')[0] for s in sites))} files")
print(f"  of those, in JSON template string leaves: {in_json}")
print(f"  of those, inside a Markdown code span:    {codespanned}")
print(f"  distinct following words: {len(words)}")
print(f"  most common: {words.most_common(12)}")
print(f"  any following word that IS an engine verb was excluded above; "
      f"engine verbs that are common English: "
      f"{sorted(v for v in g.ENGINE_VERBS if v in {'record','block','append','start','current','release','skip','claim','attach'})}")

# 2. Census of <engine> by occurrence and by file, per surface.
def census(pattern, files_pred):
    occ = 0; files = set()
    for path, where, text, whole in g.GUARD_TEXTS:
        if not files_pred(path):
            continue
        n = len(pattern.findall(text))
        if n:
            occ += n; files.add(path)
    return occ, len(files)

overlay = lambda p: p.startswith(g.OVERLAY_DIR + "/")
skills = lambda p: p.startswith("skills/")
specs = lambda p: p.startswith("specs/")
allp = lambda p: True
for name, pat in (("<engine>", g.ENGINE_PLACEHOLDER_RE), ("CLI fallback", g.CLI_FALLBACK_RE),
                  ("stand-in command", g.ENGINE_STANDIN_COMMAND_RE),
                  ("engine invocation", g.ENGINE_INVOCATION_RE)):
    o_all = census(pat, allp); o_ov = census(pat, overlay); o_sk = census(pat, skills); o_sp = census(pat, specs)
    print(f"\n{name}: {o_all[0]} occurrences across {o_all[1]} files containing it")
    print(f"    overlay {o_ov[0]} occ / {o_ov[1]} files | skills/ {o_sk[0]} occ / {o_sk[1]} files | specs/ {o_sp[0]} occ / {o_sp[1]} files")
