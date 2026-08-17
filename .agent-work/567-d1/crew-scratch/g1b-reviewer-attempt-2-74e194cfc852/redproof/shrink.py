"""The case the control count exists for: BOTH sides shrink together, so the tie
stays green and only the pin catches it."""
import sys, pathlib, re
sys.path.insert(0, str(pathlib.Path(".").resolve() / "tests"))
import test_cli_retirement_guard as G, test_mcp_adoption as A
real = A._engine_verbs
T = G.TestTheVerbSetIsTheEnginesOwn()

def run(label, fn):
    try: fn()
    except AssertionError as e:
        print(f"  {label}: RED   -> {str(e).splitlines()[0][:95]}"); return True
    print(f"  {label}: GREEN"); return False

for shrunk, why in [(frozenset({"claim", "release"}), "derivation reads the wrong thing, returns 2"),
                    (frozenset(), "derivation returns the EMPTY set (the docstring's own example)")]:
    print(f"=== both sides derived from a broken oracle: {why}")
    G._engine_verbs = lambda s=shrunk: s; A._engine_verbs = G._engine_verbs
    sv, ss, sp = G._ENGINE_VERBS, G.ENGINE_VERBS, G.ENGINE_STANDIN_COMMAND_RE
    G._ENGINE_VERBS = "|".join(re.escape(v) for v in sorted(shrunk))
    G.ENGINE_VERBS = frozenset(re.sub(r"\\(.)", r"\1", t) for t in G._ENGINE_VERBS.split("|"))
    run("tie (expected GREEN: they agree)", T.test_the_verb_set_is_the_engines_own_registry)
    run("control count (must be RED)     ", T.test_the_engine_has_all_eighteen_verbs_todays_pin_expects)
    G._ENGINE_VERBS, G.ENGINE_VERBS, G.ENGINE_STANDIN_COMMAND_RE = sv, ss, sp
    G._engine_verbs = real; A._engine_verbs = real
    print()

print("=== does the guard survive `flag-candidate`'s hyphen? (re.escape claim)")
print("  alternation contains 'flag\\-candidate':", "flag\\-candidate" in G._ENGINE_VERBS)
print("  '<engine> flag-candidate --from g1' caught:",
      bool(G.ENGINE_STANDIN_COMMAND_RE.search("<engine> flag-candidate --from g1")))
print("  round-trip unescape recovers it:", "flag-candidate" in G.ENGINE_VERBS)
