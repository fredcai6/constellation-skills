"""r7: is the verb set the ENGINE's own? Oracle read independently of _engine_verbs()."""
import re, subprocess, sys, pathlib
ROOT = pathlib.Path(".").resolve()
sys.path.insert(0, str(ROOT / "tests"))

# --- Oracle A: the engine's --help text, parsed here. Independent of the repo's helper.
help_txt = subprocess.run([sys.executable, "scripts/checklist_engine.py", "--help"],
                          capture_output=True, text=True).stdout
m = re.search(r"\{([a-z,\-\s]+)\}", help_txt)
from_help = frozenset(v.strip() for v in m.group(1).replace("\n", "").split(",") if v.strip())
print(f"A. from `checklist_engine.py --help`      : {len(from_help)} {sorted(from_help)}")

# --- Oracle B: argparse choices, read straight off the parser object.
sys.path.insert(0, str(ROOT / "scripts"))
import checklist_engine
import argparse
seen = set()
_real_add = argparse._SubParsersAction.add_parser
parser_choices = None
try:
    checklist_engine.parse_args(["--file", "/dev/null", "__bogus__"])
except SystemExit:
    pass
# recover choices by re-invoking with a bogus verb and reading stderr
p = subprocess.run([sys.executable, "scripts/checklist_engine.py", "--file", "/dev/null", "__bogus__"],
                   capture_output=True, text=True)
m2 = re.search(r"\(choose from ([^)]+)\)", p.stderr)
from_argparse = frozenset(x.strip().strip("'\"") for x in m2.group(1).split(",")) if m2 else frozenset()
print(f"B. from argparse's own error            : {len(from_argparse)} {sorted(from_argparse)}")

# --- What the guard actually applies
import test_cli_retirement_guard as G
from test_mcp_adoption import _engine_verbs
print(f"C. guard's ENGINE_VERBS (from alternation): {len(G.ENGINE_VERBS)} {sorted(G.ENGINE_VERBS)}")
print(f"D. repo helper _engine_verbs()           : {len(_engine_verbs())} {sorted(_engine_verbs())}")
print()
print("A == C :", from_help == G.ENGINE_VERBS, "| missing from guard:", sorted(from_help - G.ENGINE_VERBS),
      "| extra in guard:", sorted(G.ENGINE_VERBS - from_help))
print("B == C :", from_argparse == G.ENGINE_VERBS)
print("D == C :", _engine_verbs() == G.ENGINE_VERBS)
print("'resume' in guard verb set:", "resume" in G.ENGINE_VERBS)
print()
print("compiled alternation, verbatim:", G._ENGINE_VERBS)
print("blocker line vs stand-in pattern:", bool(G.ENGINE_STANDIN_COMMAND_RE.search(
      "Second path: <cli> resume g1 --reason 'unblocked'.")))
