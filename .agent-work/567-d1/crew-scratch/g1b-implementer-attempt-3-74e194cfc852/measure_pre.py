import sys, re
sys.path.insert(0, "tests")
import test_cli_retirement_guard as g

LINE = "Second path: <cli> resume g1 --reason 'unblocked'."
pats = {
    "placeholder": g.ENGINE_PLACEHOLDER_RE,
    "fallback": g.CLI_FALLBACK_RE,
    "invocation": g.ENGINE_INVOCATION_RE,
    "stand-in": g.ENGINE_STANDIN_COMMAND_RE,
}
print("PRE-CHANGE, the blocker line against all four patterns:")
for name, p in pats.items():
    print(f"  {name:12s} -> {'MATCH' if p.search(LINE) else 'MISS'}")

print("\nhand-typed verb list, as a set:")
hand = set(g._ENGINE_VERBS.split("|"))
print(f"  {len(hand)} verbs: {sorted(hand)}")

sys.path.insert(0, "tests")
from test_mcp_adoption import _engine_verbs
eng = _engine_verbs()
print(f"engine argparse verbs: {len(eng)}: {sorted(eng)}")
print(f"in engine, missing from the hand list: {sorted(eng - hand)}")
print(f"in hand list, not in engine:           {sorted(hand - eng)}")

def addresses(pattern):
    out = set()
    for path, where, text, whole in g.GUARD_TEXTS:
        for m in pattern.finditer(text):
            out.add(f"{where}:{text.count(chr(10),0,m.start())+1}" if whole else where)
    return out

print(f"\nwalk: {len(g.GUARD_TEXTS)} texts, {len(g.GUARDED_FILES)} files")
base = {}
for name in ("invocation", "stand-in"):
    a = addresses(pats[name])
    base[name] = a
    print(f"  PRE {name:10s}: {len(a)} addresses")
union_pre = addresses(pats["placeholder"]) | addresses(pats["fallback"]) | base["invocation"] | base["stand-in"]
print(f"  PRE union over all four: {len(union_pre)} addresses")

# what deriving all 18 would do: rebuild both patterns with the engine's set
verbs = "|".join(re.escape(v) for v in sorted(eng))
inv2 = re.compile(
    r"""(?:(?:python3?|py)\s+(?:[^\s`'"]+\s+)?|[^\s`'"]*/)checklist_engine\.py"""
    r"""|checklist_engine\.py(?=[`'"\s]*(?:--[A-Za-z]|(?:""" + verbs + r""")\b))"""
)
standin2 = re.compile(g._ENGINE_STANDIN + r"[ \t]+(?:" + verbs + r")\b")
for name, p, pre in (("invocation", inv2, base["invocation"]), ("stand-in", standin2, base["stand-in"])):
    a = addresses(p)
    print(f"  POST(derived) {name:10s}: {len(a)} addresses | ADDED: {sorted(a - pre)} | REMOVED: {sorted(pre - a)}")
union_post = addresses(pats["placeholder"]) | addresses(pats["fallback"]) | addresses(inv2) | addresses(standin2)
print(f"  POST union over all four: {len(union_post)} addresses (delta {len(union_post)-len(union_pre)})")
print(f"  blocker line under derived stand-in pattern: {'MATCH' if standin2.search(LINE) else 'MISS'}")
