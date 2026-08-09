"""Does the SHIPPED gh stub refuse everything it does not model, or can a
drifted check text slip past it silently? (g3-review, claim (c).)

Loads GH_STUB_SOURCE straight out of the test module and drives it directly.
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
    "doctrine_probe", ROOT / "tests" / "test_iterative_planning_doctrine.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["doctrine_probe"] = mod
spec.loader.exec_module(mod)

BRANCH = "epic-418/reachability-probe"

BASE = ["pr", "list", "--head", BRANCH, "--state", "all", "--json", "state",
        "--jq", '[.[] | select(.state == "OPEN" or .state == "MERGED")] | length']

CASES = [
    ("MODELLED baseline (OPEN present)", BASE, {BRANCH: ["OPEN"]}),
    ("unknown flag --limit 100", BASE + ["--limit", "100"], {BRANCH: ["OPEN"]}),
    ("unknown flag --repo someone/else", BASE + ["--repo", "someone/else"], {BRANCH: ["OPEN"]}),
    ("unknown flag --author @me", BASE + ["--author", "@me"], {BRANCH: ["OPEN"]}),
    ("boolean-style flag --draft (eats next token)",
     ["pr", "list", "--draft", "--head", BRANCH, "--state", "all", "--json", "state",
      "--jq", '[.[] | select(.state == "OPEN" or .state == "MERGED")] | length'],
     {BRANCH: ["OPEN"]}),
    ("--search qualifier instead of --head",
     ["pr", "list", "--head", BRANCH, "--search", "is:merged", "--state", "all",
      "--json", "state",
      "--jq", '[.[] | select(.state == "OPEN" or .state == "MERGED")] | length'],
     {BRANCH: ["OPEN"]}),
    ("jq with != operator", BASE[:-1] + ['[.[] | select(.state != "CLOSED")] | length'],
     {BRANCH: ["OPEN"]}),
    ("--json number,state (implementer's own case)",
     ["pr", "list", "--head", BRANCH, "--state", "all", "--json", "number,state",
      "--jq", '[.[] | select(.state == "OPEN")] | length'], {BRANCH: ["OPEN"]}),
    ("--state draft (implementer's own case)",
     ["pr", "list", "--head", BRANCH, "--state", "draft", "--json", "state",
      "--jq", '[.[] | select(.state == "OPEN")] | length'], {BRANCH: ["OPEN"]}),
]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        stub = pathlib.Path(tmp) / "gh_stub.py"
        stub.write_text(mod.GH_STUB_SOURCE, encoding="utf-8", newline="\n")
        print("%-48s %-6s %-8s %s" % ("case", "exit", "stdout", "stderr"))
        print("-" * 100)
        for label, argv, fixture in CASES:
            env = dict(os.environ)
            env["GH_STUB_PRS"] = json.dumps(fixture)
            p = subprocess.run([sys.executable, str(stub)] + argv,
                               capture_output=True, text=True, env=env)
            verdict = "REFUSED" if p.returncode != 0 else "ANSWERED"
            print("%-48s %-6s %-8s %-9s %s"
                  % (label[:48], p.returncode, repr(p.stdout.strip()), verdict,
                     p.stderr.strip()[:40]))


if __name__ == "__main__":
    main()
