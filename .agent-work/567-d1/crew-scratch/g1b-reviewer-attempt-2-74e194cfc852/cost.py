"""r8: what did deriving the verb set COST over the whole walk? Priced against the
right counterfactual -- the alternation rebuilt from the engine MINUS resume."""
import sys, pathlib, re
sys.path.insert(0, str(pathlib.Path(".").resolve() / "tests"))
import test_cli_retirement_guard as G
from test_mcp_adoption import _engine_verbs

def addresses(pat):
    out = set()
    for path, where, text, whole in G.GUARD_TEXTS:
        for m in pat.finditer(text):
            out.add(f"{where}:{text.count(chr(10),0,m.start())+1}" if whole else where)
    return out
def matches(pat):
    return sum(len(pat.findall(t)) for _, _, t, _ in G.GUARD_TEXTS)

print(G._census())
print(f"verb set: {len(G.ENGINE_VERBS)} verbs, derived; == engine argparse: {G.ENGINE_VERBS == _engine_verbs()}")
print()
def build(verbs):
    alt = "|".join(re.escape(v) for v in sorted(verbs))
    inv = re.compile(r"""(?:(?:python3?|py)\s+(?:[^\s`'"]+\s+)?|[^\s`'"]*/)checklist_engine\.py"""
                     r"""|checklist_engine\.py(?=[`'"\s]*(?:--[A-Za-z]|(?:""" + alt + r""")\b))""")
    sti = re.compile(G._ENGINE_STANDIN + r"[ \t]+(?:" + alt + r")\b")
    return inv, sti

full = set(_engine_verbs())
inv17, sti17 = build(full - {"resume"})
inv18, sti18 = build(full)
for name, p17, p18 in [("ENGINE_INVOCATION_RE", inv17, inv18), ("ENGINE_STANDIN_COMMAND_RE", sti17, sti18)]:
    a17, a18 = addresses(p17), addresses(p18)
    print(f"{name:26} 17 verbs -> {len(a17)} addr / {matches(p17)} occ | "
          f"18 verbs -> {len(a18)} addr / {matches(p18)} occ | DELTA {len(a18)-len(a17)}")
    print(f"{'':26}   added by `resume`: {sorted(a18-a17) or 'NONE'}   lost: {sorted(a17-a18) or 'NONE'}")

ship = [G.ENGINE_PLACEHOLDER_RE, G.CLI_FALLBACK_RE, G.ENGINE_INVOCATION_RE, G.ENGINE_STANDIN_COMMAND_RE]
u17 = addresses(inv17) | addresses(sti17) | addresses(G.ENGINE_PLACEHOLDER_RE) | addresses(G.CLI_FALLBACK_RE)
u18 = set().union(*(addresses(p) for p in ship))
print(f"\nunion over all four patterns: 17 verbs -> {len(u17)} | 18 verbs -> {len(u18)}")
print(f"per-pattern shipped occurrences: placeholder={matches(G.ENGINE_PLACEHOLDER_RE)} "
      f"fallback={matches(G.CLI_FALLBACK_RE)} invocation={matches(G.ENGINE_INVOCATION_RE)} "
      f"standin={matches(G.ENGINE_STANDIN_COMMAND_RE)}")
print(f"g1's three patterns' addresses: {len(addresses(G.ENGINE_PLACEHOLDER_RE)|addresses(G.CLI_FALLBACK_RE)|addresses(G.ENGINE_INVOCATION_RE))}")
print(f"standin addresses NOT reported by the other three: "
      f"{sorted(addresses(G.ENGINE_STANDIN_COMMAND_RE) - (addresses(G.ENGINE_PLACEHOLDER_RE)|addresses(G.CLI_FALLBACK_RE)|addresses(G.ENGINE_INVOCATION_RE)))}")
print("\nfalse alarms: any standin address that is NOT also an <engine> address?",
      sorted(addresses(G.ENGINE_STANDIN_COMMAND_RE) - addresses(G.ENGINE_PLACEHOLDER_RE)) or "NONE")
