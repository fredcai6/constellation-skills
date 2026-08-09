"""Reviewer's template-level mutation runner (g3-review).

Mutates the SHIPPED template on disk, runs the gate's own -k selectors, and
asserts they go RED. Restores the file byte-identically (verified by sha256)
in a finally block, so an interrupted run cannot leave production code edited.
"""
import hashlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(r"C:/Programs/constellation-skills-wt/epic418-w5-gates")
TPL = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"

SHIPPED = (
    'test \\"$(gh pr list --head \\"$(git -C <repo-root> rev-parse --abbrev-ref HEAD)\\" '
    '--state all --json state --jq \'[.[] | select(.state == \\"OPEN\\" or '
    '.state == \\"MERGED\\")] | length\')\\" -gt 0'
)

# (label, replacement command text as it appears INSIDE the JSON string)
MUTATIONS = [
    # Required confirmation 1
    ("M1: literal <branch> token reintroduced",
     SHIPPED.replace(
         '\\"$(git -C <repo-root> rev-parse --abbrev-ref HEAD)\\"', "<branch>")),
    # Required confirmation 2 (discriminates only on a MERGED fixture)
    ("M2: --state all narrowed back to --state open",
     SHIPPED.replace("--state all", "--state open")),
    # Required confirmation 3: a form under which a branch with NO PR PASSES.
    # This is #484's suggested replacement -- the check that cannot fail.
    ("M3: verdict on stdout (#484 form) -- no-PR would PASS",
     'gh pr list --head \\"$(git -C <repo-root> rev-parse --abbrev-ref HEAD)\\" '
     "--state all --json state --jq 'length > 0'"),
    # Extra: does the suite notice the MERGED arm going away?
    ("M4: MERGED arm dropped from the selector",
     SHIPPED.replace(' or .state == \\"MERGED\\"', "")),
    # Extra: does the suite notice CLOSED being accepted?
    ("M5: CLOSED widened into the selector",
     SHIPPED.replace('.state == \\"MERGED\\"',
                     '.state == \\"MERGED\\" or .state == \\"CLOSED\\"')),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_selectors():
    p = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_iterative_planning_doctrine.py",
         "-q", "-k", "archive_c2b or archive_mutation"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    tail = [l for l in p.stdout.splitlines() if l.strip()][-1:]
    return p.returncode, (tail[0] if tail else "")


def main():
    original_bytes = TPL.read_bytes()
    original_sha = sha(TPL)
    original_text = original_bytes.decode("utf-8")
    if SHIPPED not in original_text:
        raise SystemExit("REFUSING: my SHIPPED literal does not match the file — "
                         "the mutations would be vacuous.")
    print("baseline sha256:", original_sha)
    code, line = run_selectors()
    print("UNMUTATED           exit=%-3s %s" % (code, line))
    if code != 0:
        raise SystemExit("REFUSING: baseline is not green; mutations prove nothing.")
    try:
        for label, replacement in MUTATIONS:
            if replacement == SHIPPED:
                print("%-52s *** MUTATION DID NOT APPLY -- VACUOUS ***" % label)
                continue
            TPL.write_bytes(original_text.replace(SHIPPED, replacement).encode("utf-8"))
            assert sha(TPL) != original_sha, "file unchanged"
            code, line = run_selectors()
            print("%-52s exit=%-3s %s  -> %s"
                  % (label, code, line, "RED (caught)" if code != 0 else "*** GREEN -- NOT CAUGHT ***"))
            TPL.write_bytes(original_bytes)
            assert sha(TPL) == original_sha, "restore failed!"
    finally:
        TPL.write_bytes(original_bytes)
        print("restored sha256:", sha(TPL), "IDENTICAL" if sha(TPL) == original_sha else "*** MISMATCH ***")


if __name__ == "__main__":
    main()
