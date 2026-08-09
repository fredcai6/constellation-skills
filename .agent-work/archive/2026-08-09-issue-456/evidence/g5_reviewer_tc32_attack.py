"""g5 REVIEWER independent attack on tc32 (CallerOrderStableUnderPermutedVisitTests).

The implementer's own falsifier deletes the ONE `sorted(...)` call and proves the
mutant survives at 1 external caller, is killed at 2. That proves ONE specific
mutation (insertion order, no sort at all) is caught. Per the g5-review handoff:
"attack it with a mutation the implementer did not choose... Try ordering by
insertion, by reverse-sort, by call-count -- and confirm the test still bites."

This script builds the SAME statement store twice (canonical file order,
reversed file order -- exactly `_permuted_statements`'s technique) through THREE
different mutated copies of `_bucket_line`'s sort line, and diffs each pair of
trees. Two of the three are still legitimately visit-order-INDEPENDENT
canonicalizations (so the diff SHOULD be empty -- that is not a bug, it is the
mutation failing to be a mutation); the third has a real tie-break gap.

Mutations tried:
  reverse-sort   ext = sorted((m for m in counter if m != mod), reverse=True)
                 Still a pure function of the SET, not of visit order --
                 expected: diff EMPTY (correctly not flagged; alphabetical-
                 descending is just as canonical as ascending).
  call-count     ext = sorted((m for m in counter if m != mod), key=lambda m: -counter[m])
                 pkg.alpha and pkg.beta each call target() exactly once (see
                 _MULTI_CALLER_ALPHA/BETA_SOURCE) -- a tied count. Python's
                 sort is stable, so ties break by the CURRENT iteration order
                 of `counter`, a Counter that fills in visit order --
                 expected: diff NON-EMPTY (a real visit-order leak on ties).
  reversed-insertion  ext = list(reversed([m for m in counter if m != mod]))
                 No sort at all, order is (reversed) Counter insertion order --
                 expected: diff NON-EMPTY (directly visit-order dependent,
                 same defect class as the implementer's own mutation, different
                 shape).

Usage: python .agent-work/issue-456/evidence/g5_reviewer_tc32_attack.py
"""
import pathlib
import sys
import tempfile
import contextlib
import io

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from scripts.code_map import checks, cli, extract  # noqa: E402
import test_code_map as T  # noqa: E402

ANCHOR = "    ext = sorted(m for m in counter if m != mod)\n"

MUTATIONS = {
    "reverse-sort": (
        ((ANCHOR, "    ext = sorted((m for m in counter if m != mod), reverse=True)\n"),),
        "empty",
    ),
    "call-count-tiebreak": (
        ((ANCHOR, "    ext = sorted((m for m in counter if m != mod), key=lambda m: -counter[m])\n"),),
        "nonempty",
    ),
    "reversed-insertion": (
        ((ANCHOR, "    ext = list(reversed([m for m in counter if m != mod]))\n"),),
        "nonempty",
    ),
}


def main():
    tmp = tempfile.TemporaryDirectory()
    repo = pathlib.Path(tmp.name) / "repo"
    repo.mkdir()
    T._make_multi_caller_repo(repo)

    artifacts = repo / ".code-map"
    with contextlib.redirect_stdout(io.StringIO()):
        rc = cli.main(["extract", "--root", str(repo), "--artifacts", str(artifacts)])
    assert rc == 0, "extract failed"
    text = (artifacts / extract.STATEMENTS_NAME).read_text(encoding="utf-8")
    groups = T._group_statement_lines_by_file(text)
    assert len(groups) > 1, "need >1 file to permute"
    permuted_text = T._permuted_statements(text)

    results = {}
    for name, (subs, expect) in MUTATIONS.items():
        work = pathlib.Path(tmp.name) / name
        work.mkdir()
        host = T.mutated_package(str(work), "render.py", subs)

        canon_art = work / "art-canon"
        canon_art.mkdir()
        (canon_art / extract.STATEMENTS_NAME).write_text(text, encoding="utf-8", newline="\n")
        canon_out = work / "map-canon"
        p1 = T.run_code_map(host, "render", "--root", str(repo),
                             "--artifacts", str(canon_art), "--out", str(canon_out))
        assert p1.returncode == 0, p1.stdout + p1.stderr

        perm_art = work / "art-perm"
        perm_art.mkdir()
        (perm_art / extract.STATEMENTS_NAME).write_text(permuted_text, encoding="utf-8", newline="\n")
        perm_out = work / "map-perm"
        p2 = T.run_code_map(host, "render", "--root", str(repo),
                             "--artifacts", str(perm_art), "--out", str(perm_out))
        assert p2.returncode == 0, p2.stdout + p2.stderr

        diff = checks.tree_diff(canon_out, perm_out)
        got = "empty" if diff == [] else "nonempty"
        results[name] = (expect, got, diff)

    print(f"{'mutation':<22} {'expected':<10} {'observed':<10} {'match':<6}")
    all_match = True
    for name, (expect, got, diff) in results.items():
        match = expect == got
        all_match = all_match and match
        print(f"{name:<22} {expect:<10} {got:<10} {'OK' if match else 'MISMATCH'}")
        if diff:
            print(f"    diff: {diff}")
    print()
    print("ALL EXPECTATIONS MET" if all_match else "MISMATCH FOUND")
    tmp.cleanup()
    return 0 if all_match else 1


if __name__ == "__main__":
    sys.exit(main())
