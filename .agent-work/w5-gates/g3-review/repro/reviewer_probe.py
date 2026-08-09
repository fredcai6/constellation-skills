"""REVIEWER's OWN probe for archive.c2b (g3-review).

Deliberately shares NO code with tests/test_iterative_planning_doctrine.py:
its own gh stub, its own git stub, its own resolver substitution, its own
shell invocation. If this agrees with the implementer's harness, the agreement
is independent.

Usage: python reviewer_probe.py
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(r"C:/Programs/constellation-skills-wt/epic418-w5-gates")
TEMPLATE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"

# --- my own gh stub: a plain dispatch table, nothing derived from theirs ------
GH = r'''
import json, os, re, sys
a = sys.argv[1:]
assert a[0:2] == ["pr", "list"], "reviewer-stub: not a pr list: %r" % (a,)
o = {}
i = 2
while i < len(a):
    o[a[i]] = a[i + 1]
    i += 2
fixture = json.loads(os.environ["RPRS"])
rows = [{"state": s} for s in fixture.get(o["--head"], [])]
st = o["--state"]
if st == "open":
    rows = [r for r in rows if r["state"] == "OPEN"]
elif st == "merged":
    rows = [r for r in rows if r["state"] == "MERGED"]
elif st == "closed":
    rows = [r for r in rows if r["state"] in ("CLOSED", "MERGED")]
elif st != "all":
    sys.stderr.write("reviewer-stub: unknown --state %s\n" % st); sys.exit(9)
jq = o.get("--jq")
if jq is None:
    print(json.dumps(rows)); sys.exit(0)
m = re.match(r'^\[\.\[\] \| select\((.*)\)\] \| length$', jq)
if m:
    wanted = re.findall(r'\.state == "([A-Z]+)"', m.group(1))
    if not wanted:
        sys.stderr.write("reviewer-stub: cannot read selector %s\n" % jq); sys.exit(9)
    print(sum(1 for r in rows if r["state"] in wanted)); sys.exit(0)
if jq.strip() == "length":
    print(len(rows)); sys.exit(0)
m = re.match(r'^length > (\d+)$', jq.strip())
if m:
    print("true" if len(rows) > int(m.group(1)) else "false"); sys.exit(0)
sys.stderr.write("reviewer-stub: unknown --jq %s\n" % jq); sys.exit(9)
'''

GIT = r'''
import os, sys
a = sys.argv[1:]
if a[0:1] == ["-C"] and a[2:] == ["rev-parse", "--abbrev-ref", "HEAD"]:
    print(os.environ["RPBRANCH"]); sys.exit(0)
sys.stderr.write("reviewer-git-stub: unmodelled %r\n" % (a,)); sys.exit(9)
'''

BRANCH = "epic-418/w5-bookend-gates"


def shipped_command():
    doc = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    for c in doc["tasks"]["archive"]["postconditions"]:
        if c["id"] == "c2b":
            # my own <repo-root> substitution, not the repo resolver
            return c["check"]["command"].replace("<repo-root>", ROOT.as_posix())
    raise SystemExit("no c2b")


def make_bin(tmp):
    binp = pathlib.Path(tmp) / "bin"
    binp.mkdir()
    for name, src in (("gh", GH), ("git", GIT)):
        py = pathlib.Path(tmp) / (name + "_rp.py")
        py.write_text(src, encoding="utf-8", newline="\n")
        sh = binp / name
        sh.write_text(
            '#!/bin/sh\nexec "%s" "%s" "$@"\n'
            % (pathlib.Path(sys.executable).as_posix(), py.as_posix()),
            encoding="utf-8", newline="\n",
        )
        os.chmod(sh, 0o755)
    return binp


def bash():
    for cand in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files\Git\usr\bin\bash.exe"):
        if os.path.exists(cand):
            return cand
    found = shutil.which("bash")
    if not found:
        raise SystemExit("no bash — refusing to report results")
    return found


def run(cmd, fixture, binp, branch=BRANCH, use_stub_git=True):
    env = dict(os.environ)
    env["PATH"] = str(binp) + os.pathsep + env.get("PATH", "")
    env["RPRS"] = json.dumps(fixture)
    env["RPBRANCH"] = branch
    return subprocess.run([bash(), "-c", cmd], capture_output=True, text=True, env=env)


FOUR = (("no-PR", {}), ("OPEN", {BRANCH: ["OPEN"]}),
        ("MERGED", {BRANCH: ["MERGED"]}), ("CLOSED-unmerged", {BRANCH: ["CLOSED"]}))


def main():
    cmd = shipped_command()
    old = ("gh pr list --head <branch> --state open --json number "
           "--jq 'length > 0'")
    with tempfile.TemporaryDirectory() as tmp:
        binp = make_bin(tmp)

        print("=== SHIPPED text, four states (exit code is the verdict) ===")
        for label, fx in FOUR:
            p = run(cmd, fx, binp)
            print("  %-16s exit=%-3s stdout=%r stderr=%r"
                  % (label, p.returncode, p.stdout, p.stderr.strip()[:70]))

        print("\n=== OLD shipped text (claim b), four states ===")
        for label, fx in FOUR:
            p = run(old, fx, binp)
            print("  %-16s exit=%-3s stdout=%r stderr=%r"
                  % (label, p.returncode, p.stdout, p.stderr.strip()[:70]))

        print("\n=== #484's suggested replacement (claim a) ===")
        s484 = ('gh pr list --head "$(git -C %s rev-parse --abbrev-ref HEAD)" '
                "--state all --json state --jq 'length > 0'" % ROOT.as_posix())
        for label, fx in FOUR:
            p = run(s484, fx, binp)
            print("  %-16s exit=%-3s stdout=%r" % (label, p.returncode, p.stdout.strip()))

        print("\n=== MY mutations of the SHIPPED text ===")
        deriv = '"$(git -C %s rev-parse --abbrev-ref HEAD)"' % ROOT.as_posix()
        muts = [
            ("M1 literal <branch> back", cmd.replace(deriv, "<branch>"), FOUR[1]),
            ("M1b quoted \"<branch>\"", cmd.replace(deriv, '"<branch>"'), FOUR[1]),
            ("M2 --state all -> open  [MERGED fixture]",
             cmd.replace("--state all", "--state open"), FOUR[2]),
            ("M2n --state open on OPEN fixture (expected NO-OP)",
             cmd.replace("--state all", "--state open"), FOUR[1]),
            ("M4 drop MERGED arm      [MERGED fixture]",
             cmd.replace(' or .state == "MERGED"', ""), FOUR[2]),
            ("M5 widen to CLOSED      [CLOSED fixture]",
             cmd.replace('.state == "MERGED"',
                         '.state == "MERGED" or .state == "CLOSED"'), FOUR[3]),
        ]
        for label, mutant, (fxlabel, fx) in muts:
            c = run(cmd, fx, binp)
            m = run(mutant, fx, binp)
            verdict = "DISCRIMINATES" if (c.returncode == 0) != (m.returncode == 0) else "*** NO-OP ***"
            print("  %-50s fixture=%-16s control=%-3s mutant=%-3s %s"
                  % (label, fxlabel, c.returncode, m.returncode, verdict))

        print("\n=== gh failure / empty output (fail-closed check) ===")
        broken = cmd.replace("gh pr list", "gh-does-not-exist pr list")
        p = run(broken, {BRANCH: ["OPEN"]}, binp)
        print("  gh missing        exit=%s stdout=%r" % (p.returncode, p.stdout))

        print("\n=== can the SHIPPED test's stub be silently fooled? ===")
        print("  (probing unknown-flag handling with the reviewer stub too)")
        for extra in ("--limit 100", "--repo someone/else", "--draft x"):
            probe = cmd.replace("--state all", extra + " --state all")
            p = run(probe, {BRANCH: []}, binp)
            print("  extra %-22s exit=%-3s stderr=%r" % (extra, p.returncode, p.stderr.strip()[:60]))


if __name__ == "__main__":
    main()
