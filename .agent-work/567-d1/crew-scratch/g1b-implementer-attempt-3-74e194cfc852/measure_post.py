import sys, re
sys.path.insert(0, "tests")
import test_cli_retirement_guard as g
from test_mcp_adoption import _engine_verbs

def addresses(pattern):
    out = set()
    for path, where, text, whole in g.GUARD_TEXTS:
        for m in pattern.finditer(text):
            out.add(f"{where}:{text.count(chr(10),0,m.start())+1}" if whole else where)
    return out

# the file as it now stands: 18 verbs, derived
post_inv, post_si = addresses(g.ENGINE_INVOCATION_RE), addresses(g.ENGINE_STANDIN_COMMAND_RE)

# the same file with resume removed -- the counterfactual, i.e. yesterday's hand list
verbs17 = "|".join(re.escape(v) for v in sorted(_engine_verbs() - {"resume"}))
inv17 = re.compile(
    r"""(?:(?:python3?|py)\s+(?:[^\s`'"]+\s+)?|[^\s`'"]*/)checklist_engine\.py"""
    r"""|checklist_engine\.py(?=[`'"\s]*(?:--[A-Za-z]|(?:""" + verbs17 + r""")\b))"""
)
si17 = re.compile(g._ENGINE_STANDIN + r"[ \t]+(?:" + verbs17 + r")\b")
pre_inv, pre_si = addresses(inv17), addresses(si17)

print(f"walk: {len(g.GUARD_TEXTS)} texts across {len(g.GUARDED_FILES)} files "
      f"({len(g.INSTRUCTION_FILES)} skills/, {len(g.SPEC_FILES)} specs/, {len(g.OVERLAY_FILES)} overlay)")
print(f"verb set: {len(g.ENGINE_VERBS)} verbs, derived; == engine argparse: {g.ENGINE_VERBS == _engine_verbs()}")
for name, pre, post in (("ENGINE_INVOCATION_RE", pre_inv, post_inv),
                        ("ENGINE_STANDIN_COMMAND_RE", pre_si, post_si)):
    print(f"\n{name}: 17 verbs -> {len(pre)} addresses | 18 verbs -> {len(post)} addresses "
          f"| DELTA {len(post)-len(pre)}")
    print(f"  added by `resume`: {sorted(post - pre) or 'NONE'}")
    print(f"  lost:              {sorted(pre - post) or 'NONE'}")

union_pre = addresses(g.ENGINE_PLACEHOLDER_RE) | addresses(g.CLI_FALLBACK_RE) | pre_inv | pre_si
union_post = addresses(g.ENGINE_PLACEHOLDER_RE) | addresses(g.CLI_FALLBACK_RE) | post_inv | post_si
print(f"\nunion over all four patterns: 17 verbs -> {len(union_pre)} | 18 verbs -> {len(union_post)}")

BLOCKER = "Second path: <cli> resume g1 --reason 'unblocked'."
print(f"\nblocker line, per pattern (now): " + ", ".join(
    f"{n}={'MATCH' if p.search(BLOCKER) else 'MISS'}" for n, p in
    (("placeholder", g.ENGINE_PLACEHOLDER_RE), ("fallback", g.CLI_FALLBACK_RE),
     ("invocation", g.ENGINE_INVOCATION_RE), ("stand-in", g.ENGINE_STANDIN_COMMAND_RE))))
print(f"blocker line under the 17-verb counterfactual: "
      f"stand-in={'MATCH' if si17.search(BLOCKER) else 'MISS'}")

print("\n-- floors / scope, unchanged? --")
print(f"  INSTRUCTION_FILES={len(g.INSTRUCTION_FILES)} (floor 60) "
      f"SPEC_FILES={len(g.SPEC_FILES)} (floor 1) OVERLAY_FILES={len(g.OVERLAY_FILES)} (floor 60) "
      f"GUARD_TEXTS={len(g.GUARD_TEXTS)} (floor 1800)")
strays = [p for p in g.GUARDED_FILES if p.startswith(".agent-work/") and not p.startswith(g.OVERLAY_DIR + "/")]
print(f"  strays under .agent-work/ outside the overlay: {len(strays)}")
for s in ("docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md", "scripts/init_work_area.py"):
    print(f"  pre-ruled survivor IN WALK? {s}: {s in g.GUARDED_FILES}")
src = open("tests/test_cli_retirement_guard.py", encoding="utf-8").read()
print(f"  either survivor named anywhere in the guard source: "
      f"{'superpowers' in src or 'init_work_area' in src and 'init_work_area.py`' in src}")
print(f"  occurrences of 'init_work_area' in guard source: {src.count('init_work_area')} (prose only)")
