"""Reviewer-built refusal probe: force the refusal, then check the stated count
against the roots actually listed. An under-inclusive enumeration presented as
complete is the defect class this wave is about."""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

SRC = Path(r"C:/Programs/constellation-skills-wt/epic418-w5-gates/scripts/verify_iterative_role_artifacts.py")
fails = []
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    # script lives in a NON-bundle directory (no SKILL.md at its parent[1])
    detached = tmp / "wt" / "some-worktree" / "scripts"
    detached.mkdir(parents=True)
    shutil.copy2(SRC, detached / SRC.name)
    assert not (detached.parent / "SKILL.md").exists()

    # cwd: a project with NO .claude/skills, but WITH the artifact so the read passes
    proj = tmp / "proj"
    wa = proj / ".agent-work" / "probe-run"
    wa.mkdir(parents=True)
    (wa / "REPLAN_INPUT.json").write_text("{}", encoding="utf-8", newline="\n")
    assert not (proj / ".claude" / "skills").exists()

    # HOME: bare, no .claude/skills  (without this the developer's real ~/.claude/skills
    # leaks in and the refusal is unreachable -- a check that cannot fail)
    home = tmp / "bare"; home.mkdir()
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), HOMEDRIVE="", HOMEPATH="")

    run = subprocess.run(
        [sys.executable, str(detached / SRC.name), "commander", "--work-id", "probe-run"],
        cwd=proj, env=env, capture_output=True, text=True,
    )
    print("EXIT:", run.returncode)
    print("STDOUT:", repr(run.stdout))
    print("STDERR:", run.stderr.strip())
    print()

    if run.returncode != 1: fails.append(f"expected exit 1, got {run.returncode}")
    err = run.stderr

    # (i) names the REAL problem, not either old wrong one
    if "cannot locate an installed constellation skills root" not in err:
        fails.append("refusal does not name the real problem")
    for stale in ("role verifier must run from an installed constellation-* skill",
                  "installed public verifier is missing"):
        if stale in err: fails.append(f"stale/wrong message still present: {stale}")

    # (ii) stated count vs roots ACTUALLY listed
    mm = re.search(r"Roots tried \((\d+)\):\s*(.+)$", err.strip(), re.S)
    if not mm:
        fails.append("no 'Roots tried (N): ...' enumeration found")
    else:
        stated = int(mm.group(1))
        listed = [s.strip() for s in mm.group(2).split(";") if s.strip()]
        print(f"stated count = {stated}")
        print(f"listed roots = {len(listed)}")
        for r in listed: print("   -", r)
        if stated != len(listed):
            fails.append(f"UNDER/OVER-INCLUSIVE: stated {stated} but listed {len(listed)}")

        # (iii) are the listed roots the ones the code ACTUALLY consulted?
        expected = [str(detached.parent.parent),            # bundle.parent
                    str(proj / ".claude" / "skills"),        # project scope
                    str(home / ".claude" / "skills")]        # user scope
        print()
        print("expected consulted roots:")
        for r in expected: print("   -", r)
        if [Path(x) for x in listed] != [Path(x) for x in expected]:
            fails.append("listed roots are not exactly the roots consulted, in order")

print()
print("FAILURES:", fails if fails else "none")
sys.exit(1 if fails else 0)
