#!/usr/bin/env python
"""Before/after repro for engine-native worktree isolation (epic 568, commander-315-native).

Builds a throwaway main checkout + a real registered git worktree in a temp dir,
instantiates a Commander spine INTO the worktree with this tree's own
`init_work_area.py`, and then drives `checklist_engine.py claim` against that
spine from two different places:

    A. cwd = the WORKTREE     -- the agent is where it belongs. Must PASS.
    B. cwd = the MAIN CHECKOUT -- the agent is in the wrong tree. Must REFUSE
                                  once the native comparison exists.

Case B is the whole point. Before the change the engine has no idea it is in the
wrong tree and claims the lease happily; after the change it refuses, because it
compares its OWN `Path.cwd()` against the `origin.worktree` the spine carries.

It also drives a third case:

    C. an origin-LESS spine, cwd = the MAIN CHECKOUT. Must PASS in BOTH worlds --
       that is the stated fallback, and a change that refuses here would silently
       break every spine created before the stamp existed.

Nothing here touches the real repo: everything is built inside
`tempfile.TemporaryDirectory()` and removed on exit. Run it from anywhere.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "scripts" / "checklist_engine.py"
INIT_WORK_AREA = ROOT / "scripts" / "init_work_area.py"
TEMPLATE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"


def git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


def claim_from(spine: Path, cwd: Path, session: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(ENGINE), "--file", str(spine), "claim",
         "--session-id", session, "--claimed-by", "commander", "--worktree", "."],
        cwd=str(cwd), capture_output=True, text=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def verdict(code: int) -> str:
    return "PASS   " if code == 0 else "REFUSED"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        main_checkout = base / "main"
        worktree = base / "wt"

        main_checkout.mkdir()
        git("init", "-q", cwd=main_checkout)
        git("-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "--allow-empty", "-m", "init", cwd=main_checkout)
        git("worktree", "add", "-q", str(worktree), "-b", "wtbranch", cwd=main_checkout)

        # A SEPARATE, UNCLAIMED spine per case. Sharing one spine across cases
        # made case B refuse with "already owned by active session" -- a refusal,
        # but not the one under test. A repro whose failing case can fail for the
        # wrong reason proves nothing, so each case gets its own work area and
        # every verdict is matched against the refusal REASON, not just an exit
        # code.
        def make_spine(work_id: str) -> Path:
            subprocess.run(
                [sys.executable, str(INIT_WORK_AREA), work_id,
                 "--root", str(worktree), "--spine", str(TEMPLATE)],
                check=True, capture_output=True, text=True,
            )
            return worktree / ".agent-work" / work_id / "spine.json"

        spine_a = make_spine("wa")
        spine_b = make_spine("wb")
        spine_c = make_spine("wc")
        spine_d = make_spine("wd")

        stamped = json.loads(spine_a.read_text(encoding="utf-8")).get("origin")

        # Case C's spine is the origin-LESS shape: every spine created before the
        # stamp existed looks like this, and must keep working.
        data = json.loads(spine_c.read_text(encoding="utf-8"))
        data.pop("origin", None)
        spine_c.write_text(json.dumps(data, indent=2), encoding="utf-8")

        print("main checkout          :", main_checkout)
        print("worktree               :", worktree)
        print("origin stamped in spine:", json.dumps(stamped) if stamped else "(none -- stamp not landed yet)")
        print()

        # D drives from a SUBDIRECTORY of the worktree. The check being
        # superseded compares `git rev-parse --show-toplevel`, which succeeds
        # from anywhere inside the tree, so a guard that demands cwd EQUAL the
        # root would be a regression. Only cases A and B would never notice.
        subdir = worktree / ".agent-work" / "wd"

        code_a, out_a = claim_from(spine_a, worktree, "s-a")
        code_b, out_b = claim_from(spine_b, main_checkout, "s-b")
        code_c, out_c = claim_from(spine_c, main_checkout, "s-c")
        code_d, out_d = claim_from(spine_d, subdir, "s-d")

        print(f"A  origin spine, cwd = WORKTREE ROOT -> {verdict(code_a)}  (want PASS)")
        print(f"B  origin spine, cwd = MAIN CHECKOUT -> {verdict(code_b)}  (want REFUSED after the change)")
        print(f"C  no-origin,    cwd = MAIN CHECKOUT -> {verdict(code_c)}  (want PASS in both worlds -- the fallback)")
        print(f"D  origin spine, cwd = WT SUBDIR     -> {verdict(code_d)}  (want PASS -- containment, not equality)")
        print()
        print("--- B's engine output (the case that must change) ---")
        print(out_b)
        print()
        print("--- C's engine output (the fallback, must be unchanged) ---")
        print(out_c.splitlines()[-1] if out_c else "(no output)")

        # B's verdict is decided on a STATE FACT, never on a substring of the
        # refusal prose. An earlier version of this file matched
        # `"worktree" in out and "lease" not in out`, which is the corollary
        # defect this repo names -- "assert against the behaviour, never against
        # text describing the behaviour". It was brittle both ways: a correct
        # refusal worded differently would have reported the gate broken, and a
        # wrong refusal that happened to say "worktree" (which `claim` takes as
        # a literal argument) would have reported it armed.
        #
        # The behavioural fact is available and unambiguous: a refused `claim`
        # writes no lease. So B is a true isolation refusal exactly when the
        # spine on disk still carries no engine_session.
        b_lease = json.loads(spine_b.read_text(encoding="utf-8")).get("engine_session")
        b_took_no_lease = not (isinstance(b_lease, dict) and b_lease.get("status") == "active")
        b_refused = code_b != 0 and b_took_no_lease

        gate_armed = code_a == 0 and b_refused and code_c == 0 and code_d == 0
        print()
        print("B refused AND took no lease (state fact):", b_refused)
        print("GATE ARMED:", gate_armed)
        return 0 if gate_armed else 1


if __name__ == "__main__":
    raise SystemExit(main())
