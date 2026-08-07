"""Reviewer's OWN independent probe of scripts/verify_episode_captured.py.

Builds throwaway stores through the sanctioned writer, then runs the gate as a
SUBPROCESS (real exit codes, no in-process trust) for each close criterion.
Nothing here touches the repo's real episodes/ store.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
WRITER = ROOT / "scripts" / "apply_episode_delta.py"
GATE = ROOT / "scripts" / "verify_episode_captured.py"
SENT = "REVIEWER-SENTINEL-LEAK-CANARY-7c31"


def create_op(run):
    return {
        "op": "create",
        "mechanical": {
            "run": run,
            "project": "constellation-skills",
            "role": "commander",
            "spine-step": "feedback",
            "context-manifest-ref": "none",
            "refusals": 0,
            "reopens": 0,
            "rework-count": 0,
            "failed-commands": 0,
        },
        "agent_supplied": {
            k: {"strength": "strong", "statement": SENT}
            for k in (
                "task-intent",
                "expected-behavior",
                "observed-behavior",
                "impact-cost",
                "workaround",
            )
        },
    }


def seed(base, store, run, count=1):
    delta = {"work_id": run, "ops": [create_op(run) for _ in range(count)]}
    p = base / f"delta-{run}.json"
    with p.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(delta, fh)
    r = subprocess.run(
        [sys.executable, str(WRITER), "--delta", str(p), "--store-root", str(store)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"seed failed: {r.stdout}\n{r.stderr}"


def gate(argv, cwd=None):
    r = subprocess.run(
        [sys.executable, str(GATE), *argv], capture_output=True, text=True,
        cwd=str(cwd) if cwd else None,
    )
    return r.returncode, r.stdout, r.stderr


results = []


def check(label, expect, rc, out, err, leak_check=True):
    ok = rc == expect
    leak = SENT in out or SENT in err
    if leak_check and leak:
        ok = False
    results.append((label, expect, rc, ok, leak))
    print(f"[{'OK ' if ok else 'BAD'}] {label}: expected exit {expect}, got {rc}, "
          f"sentinel-in-output={leak}")
    for line in (out or "").splitlines()[:2] + (err or "").splitlines()[:2]:
        print(f"      | {line}")


with tempfile.TemporaryDirectory() as td:
    base = Path(td)

    # --- CC1a: seeded store with the asked-for run -> 0
    s1 = base / "s1" / "episodes"
    seed(base, s1, "issue-447", count=2)
    check("CC1a seeded store", 0, *gate(["issue-447", "--store-root", str(s1)]))

    # --- CC1b: store that exists and is EMPTY -> 1
    s2 = base / "s2" / "episodes"
    (s2 / "active").mkdir(parents=True)
    (s2 / "retired").mkdir(parents=True)
    check("CC1b empty store", 1, *gate(["issue-447", "--store-root", str(s2)]))

    # --- CC1c: store holding ONLY another run's episodes -> 1
    s3 = base / "s3" / "episodes"
    seed(base, s3, "issue-999", count=3)
    check("CC1c other-runs-only store", 1, *gate(["issue-447", "--store-root", str(s3)]))

    # --- CC3a: missing store root entirely -> 2
    check("CC3a missing store root", 2,
          *gate(["issue-447", "--store-root", str(base / "does-not-exist")]))

    # --- CC3b: root exists, active/ missing -> 2 (NOT answered as zero)
    s4 = base / "s4" / "episodes"
    (s4 / "retired").mkdir(parents=True)
    check("CC3b missing active/ dir", 2, *gate(["issue-447", "--store-root", str(s4)]))

    # --- CC3c: malformed record (no `- run:` line) -> 2, not silently skipped
    s5 = base / "s5" / "episodes"
    seed(base, s5, "issue-447")
    stray = s5 / "active" / "issue-447-999.md"
    with stray.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("<!-- episode-state: schema=1 id=issue-447-999 status=active -->\n")
    check("CC3c malformed record", 2, *gate(["issue-447", "--store-root", str(s5)]))

    # --- CC2: --phase archive on an episode present but NOT git-added -> 1
    g = base / "repo"
    g.mkdir()
    subprocess.run(["git", "init", "-q", str(g)], check=True, capture_output=True)
    s6 = g / "episodes"
    seed(base, s6, "issue-447")
    check("CC2 archive, episode uncommitted", 1,
          *gate(["issue-447", "--store-root", str(s6), "--phase", "archive"]))
    # feedback phase on the SAME store must be green -> the archive failure is the
    # git question and nothing else
    check("CC2b feedback phase, same untracked store", 0,
          *gate(["issue-447", "--store-root", str(s6)]))
    # now git add it -> archive goes green
    subprocess.run(["git", "add", "episodes"], cwd=str(g), check=True, capture_output=True)
    check("CC2c archive after git add", 0,
          *gate(["issue-447", "--store-root", str(s6), "--phase", "archive"]))
    # and with a RELATIVE --store-root from inside the repo (the mid-run defect)
    check("CC2d archive, RELATIVE --store-root", 0,
          *gate(["issue-447", "--store-root", "episodes", "--phase", "archive"], cwd=g))

bad = [r for r in results if not r[3]]
print()
print(f"{len(results)} probes, {len(bad)} failed")
sys.exit(1 if bad else 0)
