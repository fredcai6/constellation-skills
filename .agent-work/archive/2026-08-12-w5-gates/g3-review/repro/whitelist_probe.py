"""Re-verification probe (g3-review, commit 84d1e998).

Is the stub's flag whitelist actually CLOSED? Probes flag SHAPES, not just flag
names -- combined --flag=value tokens, short flags, repeats, missing values,
abbreviations, separators, empty values -- looking for anything still ANSWERED.

Only an ANSWERED (exit 0) row on an unmodelled shape is a finding. A refusal is
the safe direction, even a refusal for the "wrong" stated reason.
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(r"C:/Programs/constellation-skills-wt/epic418-w5-gates")
spec = importlib.util.spec_from_file_location(
    "doctrine_reverify", ROOT / "tests" / "test_iterative_planning_doctrine.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["doctrine_reverify"] = mod
spec.loader.exec_module(mod)

B = "epic-418/reachability-probe"
JQ = '[.[] | select(.state == "OPEN" or .state == "MERGED")] | length'
BASE = ["pr", "list", "--head", B, "--state", "all", "--json", "state", "--jq", JQ]


def ins(*extra):
    """BASE with extra argv tokens spliced in after `pr list`."""
    return BASE[:2] + list(extra) + BASE[2:]


CASES = [
    ("CONTROL modelled baseline", BASE, True),
    # --- flag NAMES the commander already proved (regression) ---
    ("--repo someone/else", ins("--repo", "someone/else"), False),
    ("--limit 100", ins("--limit", "100"), False),
    ("--author @me", ins("--author", "@me"), False),
    ("--search is:merged", ins("--search", "is:merged"), False),
    # --- flag SHAPES the commander did NOT try ---
    ("combined --repo=someone/else (one token)", ins("--repo=someone/else"), False),
    ("combined --limit=100 (one token)", ins("--limit=100"), False),
    ("MODELLED flag in combined form --json=state",
     ["pr", "list", "--head", B, "--state", "all", "--json=state", "--jq", JQ], False),
    ("MODELLED flag combined --head=BRANCH",
     ["pr", "list", "--head=" + B, "--state", "all", "--json", "state", "--jq", JQ], False),
    ("short flag -R someone/else", ins("-R", "someone/else"), False),
    ("short flag -L 100", ins("-L", "100"), False),
    ("short flag -s all", ins("-s", "all"), False),
    ("bare -- separator", ins("--"), False),
    ("unknown flag with NO value at end of argv", BASE + ["--web"], False),
    ("modelled flag with NO value at end of argv", BASE + ["--jq"], False),
    ("unknown flag whose value looks like a flag", ins("--repo", "--limit"), False),
    ("empty-string flag value", ins("--repo", ""), False),
    ("uppercase --HEAD", ins("--HEAD", B), False),
    ("trailing-space flag '--repo '", ins("--repo ", "x"), False),
    ("unicode-lookalike --repo (en dash)", ins("\u2013-repo", "x"), False),
    ("positional argument after list", ins("someone/else"), False),
    # --- repeats / ordering (modelled names, odd shapes) ---
    ("repeated --head, second wins",
     ["pr", "list", "--head", "other/branch", "--head", B, "--state", "all",
      "--json", "state", "--jq", JQ], None),
    ("repeated --state open then all",
     ["pr", "list", "--head", B, "--state", "open", "--state", "all",
      "--json", "state", "--jq", JQ], None),
    # --- the OPTIONAL --jq else-branch the commander asked about ---
    ("--jq dropped entirely (raw JSON path)",
     ["pr", "list", "--head", B, "--state", "all", "--json", "state"], None),
    # --- branches DELETED in 84d1e998: must now refuse ---
    ("DELETED --state closed",
     ["pr", "list", "--head", B, "--state", "closed", "--json", "state", "--jq", JQ], False),
    ("DELETED --state merged",
     ["pr", "list", "--head", B, "--state", "merged", "--json", "state", "--jq", JQ], False),
    ("DELETED bare `length` jq",
     ["pr", "list", "--head", B, "--state", "all", "--json", "state", "--jq", "length"], False),
    # --- still-modelled jq forms that MUST keep working (leg 6) ---
    ("KEEP `length > 0` jq (leg 6 needs it)",
     ["pr", "list", "--head", B, "--state", "all", "--json", "state",
      "--jq", "length > 0"], True),
]


def main():
    findings = []
    with tempfile.TemporaryDirectory() as tmp:
        stub = pathlib.Path(tmp) / "gh_stub.py"
        stub.write_text(mod.GH_STUB_SOURCE, encoding="utf-8", newline="\n")
        assert "MODELLED_FLAGS" in mod.GH_STUB_SOURCE, "whitelist not present — probe is vacuous"
        print("%-46s %-5s %-9s %-9s %s" % ("shape", "exit", "stdout", "behaviour", "expected"))
        print("-" * 108)
        for label, argv, expect_answer in CASES:
            env = dict(os.environ)
            env["GH_STUB_PRS"] = json.dumps({B: ["OPEN"]})
            p = subprocess.run([sys.executable, str(stub)] + argv,
                               capture_output=True, text=True, env=env)
            answered = p.returncode == 0
            behaviour = "ANSWERED" if answered else "REFUSED"
            if expect_answer is None:
                expected = "(informational)"
            elif answered == expect_answer:
                expected = "as expected"
            else:
                expected = "*** UNEXPECTED ***"
                findings.append((label, p.returncode, p.stdout.strip()))
            print("%-46s %-5s %-9s %-9s %s"
                  % (label[:46], p.returncode, repr(p.stdout.strip())[:9], behaviour, expected))
    print()
    if findings:
        print("FINDINGS — unmodelled shapes still answered, or modelled shapes broken:")
        for f in findings:
            print("  ", f)
    else:
        print("NO FINDINGS: every unmodelled shape probed refuses; both kept forms still answer.")


if __name__ == "__main__":
    main()
