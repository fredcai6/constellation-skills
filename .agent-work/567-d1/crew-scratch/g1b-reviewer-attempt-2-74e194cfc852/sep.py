"""Price the separator gap: the docstring says HORIZONTAL WHITESPACE, the code says [ \t]."""
import sys, pathlib, re, unicodedata
sys.path.insert(0, str(pathlib.Path(".").resolve() / "tests"))
import test_cli_retirement_guard as G

def addrs(pat):
    out = set()
    for path, where, text, whole in G.GUARD_TEXTS:
        for m in pat.finditer(text):
            out.add(f"{where}:{text.count(chr(10),0,m.start())+1}" if whole else where)
    return out

shipped = G.ENGINE_STANDIN_COMMAND_RE
variants = {
    "[ \\t]        (SHIPPED)":  r"[ \t]+",
    "[^\\S\\r\\n]   (horizontal ws incl. unicode)": r"[^\S\r\n]+",
    "\\s           (the priced loosening)": r"\s+",
}
base = None
for label, sep in variants.items():
    pat = re.compile(G._ENGINE_STANDIN + sep + r"(?:" + G._ENGINE_VERBS + r")\b")
    a = addrs(pat)
    if base is None: base = a
    extra = sorted(a - base)
    print(f"{label:46} addresses={len(a):3}  extra vs shipped={len(extra)}")
    for e in extra[:4]:
        print(f"      {e}")
print()
print("=== does the corpus contain ANY non-ASCII horizontal whitespace at all?")
odd = {}
for path, where, text, whole in G.GUARD_TEXTS:
    for ch in set(text):
        if ch.isspace() and ch not in " \t\r\n":
            odd.setdefault(f"U+{ord(ch):04X} {unicodedata.name(ch,'?')}", set()).add(path)
for k, v in sorted(odd.items()):
    print(f"  {k}: {len(v)} file(s)  e.g. {sorted(v)[:2]}")
print("  (none listed = corpus is pure ASCII whitespace)" if not odd else "")
print()
print("=== the three honest-prose probes of MINE that fire, against the shipped pattern")
for s in ["after a crash the <run> resume picks up where it stopped",
          "see <skill-dir> release notes for the change",
          "the <id> current state is read from the journal",
          "the `<work-id>` resume is written by the engine"]:
    print(f"  {'FIRES ' if shipped.search(s) else 'clean '} {s!r}")
print()
print("=== how many of the 18 verbs are ordinary English words that could follow a placeholder?")
common = {"record","block","append","start","current","release","skip","claim","attach","resume","amend","advance"}
print(f"  {len(common & G.ENGINE_VERBS)} of {len(G.ENGINE_VERBS)}: {sorted(common & G.ENGINE_VERBS)}")
print(f"  docstring names 9 of them; NOT named: {sorted(common - {'record','block','append','start','current','release','skip','claim','attach'})}")
