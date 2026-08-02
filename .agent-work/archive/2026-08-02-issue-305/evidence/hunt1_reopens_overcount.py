"""HUNT 1 world-proof: `reopens` over-counts after an escalated reopen.

Run from the worktree root:  python .agent-work/issue-305/evidence/hunt1_reopens_overcount.py

Builds a throwaway gated checklist with `rework_cap: 1`, drives it through the REAL
CLI (so the journal sidecar is written by `main()` exactly as in production), lets the
second `reopen` hit the cap and ESCALATE, then reads the mechanical snapshot the seam
emitted on the NEXT gate.

Ground truth: exactly ONE reopen happened. The engine's own message for the second is
"ESCALATED a: rework cap 1 reached; blocked and bubbled to parent (NOT REOPENED)".

Shipped behaviour: `mechanical/b.json` carries `"reopens": 2`.

Why: `reopen()`'s escalation branch (checklist_engine.py:1870-1879) returns a normal
string WITHOUT incrementing `rework_count`. It does not raise, so `main()` takes the
success path (:2634) and `reopen` is in MUTATING_VERBS (:70-75) -- so it is journalled
as a `reopen` anyway. `journal_reopens()` counts it; `_rework_total()` does not; and
`reopen_total()` takes `max(...)`, so the OVER-counting witness wins.

That falsifies the invariant `reopen_total`'s docstring rests on
("Both can only ever UNDER-count ... Neither can over-count.") and fabricates a
mechanical fact -- the exact thing refuse-never-fabricate forbids.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ENGINE = REPO / "scripts" / "checklist_engine.py"


def task(iid: str) -> dict:
    return {
        "id": iid, "title": iid.upper(), "imperative": "do it",
        "preconditions": [],
        "postconditions": [{"id": "c1", "statement": "done", "check": None,
                            "satisfied": False}],
        "constraints": [], "directives": None, "child_checklist": None,
        "status": "pending", "status_detail": {}, "result": None,
        "finding": None, "evidence": [], "rework_count": 0,
    }


def main() -> int:
    # A temp dir OUTSIDE any repo: `project` must REFUSE rather than guess, which this
    # incidentally also demonstrates.
    root = Path(tempfile.mkdtemp(prefix="hunt1-"))
    try:
        # Mirror a real work area: <agent-work-root>/<work-id>/spine.json. That layout
        # matters -- `manifest_root()` is the checklist directory's PARENT and
        # `manifest_path` re-appends the work-id, so the emit lands in
        # <parent>/<work-id>/, which is this directory only because it is named for
        # the work-id. (See triage #360 on that doubled path.)
        workdir = root / "hunt1"
        workdir.mkdir()
        spine = workdir / "hunt1.json"
        spine.write_text(json.dumps({
            "work_id": "hunt1", "type": "gated", "config": {"rework_cap": 1},
            "items": ["a", "b"],
            "tasks": {"a": task("a"), "b": task("b")},
        }, indent=1), encoding="utf-8", newline="\n")

        def run(*argv: str) -> str:
            out = subprocess.run(
                [sys.executable, str(ENGINE), "--file", str(spine), *argv],
                # cwd = the REPO, as a real run has. The checklist still lives in a
                # temp dir, so `project` refuses (no git there) -- which is the
                # refuse-never-fabricate path working, and is incidental here.
                capture_output=True, text=True, cwd=str(REPO),
            )
            line = (out.stdout or out.stderr).strip().splitlines()[-1]
            print(f"  $ {' '.join(argv[:3])} -> {line}")
            return line

        sid = ["--session-id", "hunt1"]
        print("Driving the fixture through the real CLI:")
        run("claim", "--session-id", "hunt1", "--claimed-by", "test")
        run("start", "a", *sid)
        run("attest", "a", "--cond", "c1", "--which", "postconditions",
            "--note", "ok", *sid)
        run("advance", "a", "--mechanical", *sid)
        reopen1 = run("reopen", "a", "--reason", "first", *sid)
        run("attest", "a", "--cond", "c1", "--which", "postconditions",
            "--note", "ok", *sid)
        run("advance", "a", "--mechanical", *sid)
        reopen2 = run("reopen", "a", "--reason", "second", *sid)
        # Resolve the escalation the way a parent would, so the run can continue and
        # the seam fires again. `resume` REFUSES a rework-cap escalation by design
        # (:1811-1817), so `skip` is the reachable route.
        run("skip", "a", "--reason", "escalation resolved by parent: OBE", *sid)
        run("start", "b", *sid)

        assert reopen1.startswith("a reopened"), reopen1
        assert reopen2.startswith("ESCALATED"), reopen2

        snapshot = json.loads((workdir / "mechanical" / "b.json")
                              .read_text(encoding="utf-8"))
        reported = snapshot["mechanical"]["reopens"]

        journal = [json.loads(ln) for ln in
                   (workdir / "hunt1.json.journal").read_text(encoding="utf-8")
                   .splitlines() if ln.strip()]
        journal_reopens = sum(1 for e in journal if e.get("verb") == "reopen")
        checklist = json.loads(spine.read_text(encoding="utf-8"))
        rework_total = sum(t.get("rework_count", 0)
                           for t in checklist["tasks"].values())

        print()
        print(f"  journal `reopen` lines      : {journal_reopens}")
        print(f"  total rework_count          : {rework_total}")
        print(f"  TRUE reopens (ground truth) : 1   <- the 2nd ESCALATED, 'not reopened'")
        print(f"  SHIPPED `reopens` in b.json : {reported}")
        print()
        if reported == 1:
            print("PASS - `reopens` matches ground truth. The defect is FIXED.")
            return 0
        print(f"FAIL - `reopens` reports {reported} where the true count is 1.")
        print("       max() took the OVER-counting journal witness. Fabricated fact.")
        return 1
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
