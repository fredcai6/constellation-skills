"""r7 red-proof: make the guard's verb set and the engine's disagree, three ways,
and confirm the tie assertions go RED and NAME the difference."""
import sys, pathlib, re
ROOT = pathlib.Path(".").resolve()
sys.path.insert(0, str(ROOT / "tests"))
import test_cli_retirement_guard as G
import test_mcp_adoption as A

def run(label, fn):
    try:
        fn()
    except AssertionError as e:
        print(f"  {label}: RED   -> {str(e).splitlines()[0][:100]}")
        for ln in str(e).splitlines()[1:4]:
            if ln.strip(): print(f"           | {ln.strip()[:110]}")
        return True
    print(f"  {label}: GREEN (no assertion) <-- would be a hole")
    return False

T = G.TestTheVerbSetIsTheEnginesOwn()
print("=== control: unmutated, all four tie assertions must be GREEN")
for name in ["test_every_verb_the_engine_has_is_caught_as_a_stood_in_for_command",
             "test_the_verb_set_is_the_engines_own_registry",
             "test_the_engine_has_all_eighteen_verbs_todays_pin_expects",
             "test_a_word_the_engine_does_not_have_is_not_a_command"]:
    run(name.replace("test_", "")[:52], getattr(T, name))

print()
print("=== (a) THE ENGINE GAINS A VERB the guard's set lacks (real drift direction)")
real = A._engine_verbs
G._engine_verbs = lambda: frozenset(real()) | {"frobnicate"}
A._engine_verbs = G._engine_verbs
red_a1 = run("tie names the difference", T.test_the_verb_set_is_the_engines_own_registry)
red_a2 = run("behavioural catches it   ", T.test_every_verb_the_engine_has_is_caught_as_a_stood_in_for_command)
red_a3 = run("control count            ", T.test_the_engine_has_all_eighteen_verbs_todays_pin_expects)
G._engine_verbs = real; A._engine_verbs = real

print()
print("=== (b) THE GUARD LOSES `resume` (the exact historical drift), engine unchanged")
saved_verbs, saved_set, saved_pat = G._ENGINE_VERBS, G.ENGINE_VERBS, G.ENGINE_STANDIN_COMMAND_RE
G._ENGINE_VERBS = "|".join(re.escape(v) for v in sorted(set(real()) - {"resume"}))
G.ENGINE_VERBS = frozenset(re.sub(r"\\(.)", r"\1", t) for t in G._ENGINE_VERBS.split("|"))
G.ENGINE_STANDIN_COMMAND_RE = re.compile(G._ENGINE_STANDIN + r"[ \t]+(?:" + G._ENGINE_VERBS + r")\b")
red_b1 = run("tie names `resume`       ", T.test_the_verb_set_is_the_engines_own_registry)
red_b2 = run("behavioural on `resume`  ", T.test_every_verb_the_engine_has_is_caught_as_a_stood_in_for_command)
red_b3 = run("control count 17!=18     ", T.test_the_engine_has_all_eighteen_verbs_todays_pin_expects)
S = G.TestTheStandInCommandPredicateItself()
red_b4 = run("pinned blocker fixture   ", S.test_catches_every_stand_in_command_shape)
print(f"  blocker line under the 17-verb counterfactual: "
      f"{'MISS (evasion route open)' if not G.ENGINE_STANDIN_COMMAND_RE.search(chr(34)+'Second path: <cli> resume g1.'+chr(34)) else 'match'}")
G._ENGINE_VERBS, G.ENGINE_VERBS, G.ENGINE_STANDIN_COMMAND_RE = saved_verbs, saved_set, saved_pat

print()
print("=== (c) THE DERIVATION IS REPLACED BY A LITERAL that agrees today, then the engine moves")
print("    (this is the durability property the implementer claims recovery-from-alternation buys)")
G._ENGINE_VERBS = "|".join(re.escape(v) for v in sorted(real()))   # a literal, agrees today
G.ENGINE_VERBS = frozenset(re.sub(r"\\(.)", r"\1", t) for t in G._ENGINE_VERBS.split("|"))
G._engine_verbs = lambda: frozenset(real()) | {"newverb"}          # engine moves
A._engine_verbs = G._engine_verbs
red_c1 = run("tie still fires on literal", T.test_the_verb_set_is_the_engines_own_registry)
red_c2 = run("behavioural still fires   ", T.test_every_verb_the_engine_has_is_caught_as_a_stood_in_for_command)
G._engine_verbs = real; A._engine_verbs = real
G._ENGINE_VERBS, G.ENGINE_VERBS = saved_verbs, saved_set

print()
print("=== (d) THE PATTERN DEGENERATES into 'any word after a stand-in'")
G.ENGINE_STANDIN_COMMAND_RE = re.compile(G._ENGINE_STANDIN + r"[ \t]+\w+\b")
red_d = run("negative-control fires    ", T.test_a_word_the_engine_does_not_have_is_not_a_command)
G.ENGINE_STANDIN_COMMAND_RE = saved_pat

print()
print("VERDICT: every mutation reached a failing state:",
      all([red_a1, red_a2, red_a3, red_b1, red_b2, red_b3, red_b4, red_c1, red_c2, red_d]))
