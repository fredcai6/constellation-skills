"""Guard: g4 migrated EVERY active lesson into the episode store, losing none.

Supersedes `dispositions_done.py` (git mv'd to this name). That script encoded the
WITHDRAWN scope: it required exactly ONE surviving active lesson -- the cluster-A
carve-out held back for the withdrawn `g6` consolidation -- and FAILED on zero.
Tommy re-scoped #308 to "just go to episodes. no doctrine updates": there is no g6,
no bin ruling, no graduation, no deletion. Under that scope **zero active lessons is
the correct end state**, because every lesson becomes an episode. The old script
asserted the opposite of the requirement; the fix is to correct the check, not to
waive it, so that the acceptance test and the requirement are the same object.

Exit 0 requires BOTH halves -- retirement alone is not migration:

  1. `.agent-work/LESSONS.md`'s Active section holds ZERO entries.
  2. Every id in `fixtures/migrated-lesson-ids.txt` (snapshotted BY COMMAND from
     LESSONS.md before the migration, asserted to be non-empty here) is reachable
     in the episode store, as a `- artifact-ref: lesson:<id>` provenance line on
     some episode under episodes/active/ or episodes/retired/.

Half 2 is what makes half 1 safe. A check that only counted active lessons down to
zero would be satisfied by deleting the file -- the exact "a check that cannot fail
is indistinguishable from one that passed" shape this corpus keeps rediscovering.

The enumeration is ASSERTED, never assumed: an empty fixture, an empty store scan,
or a fixture/marker count mismatch is a FAIL with the numbers printed, because an
under-inclusive enumeration presented as complete is itself one of the observations
being migrated here.

Run from the repo root.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
LESSONS = ROOT / ".agent-work/LESSONS.md"
FIXTURE = pathlib.Path(__file__).resolve().parents[1] / "fixtures/migrated-lesson-ids.txt"
EPISODE_DIRS = (ROOT / "episodes/active", ROOT / "episodes/retired")

MARKER_RE = re.compile(r"^- artifact-ref: lesson:(\S+)\s*$", re.M)


def main() -> int:
    failures = []

    # --- half 1: nothing is left live in the playbook -----------------------------
    if not LESSONS.exists():
        print(f"FAIL: {LESSONS} missing -- the playbook is retired by emptying its Active "
              f"section, not by deleting the file (the writer survives; see #308 scope)")
        return 1
    text = LESSONS.read_text(encoding="utf-8")
    if "## Active" not in text:
        print("FAIL: no '## Active' section -- the file's shape changed; this check cannot speak to it")
        return 1
    active_ids = re.findall(r"^### lesson:(\S+)", text.split("## Active", 1)[1], re.M)
    print(f"active lessons remaining: {len(active_ids)} -> {active_ids}")
    if active_ids:
        failures.append(f"{len(active_ids)} lesson(s) still active: {active_ids}")

    # --- the enumeration this check loops over, asserted --------------------------
    if not FIXTURE.exists():
        print(f"FAIL: {FIXTURE} missing -- the pre-migration id snapshot is what makes "
              f"'every lesson migrated' checkable at all")
        return 1
    expected = [line.strip() for line in FIXTURE.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"lesson ids to account for: {len(expected)}")
    if not expected:
        print("FAIL: the id snapshot is EMPTY, so every membership test below would pass "
              "vacuously -- refusing to report a green on an empty enumeration")
        return 1

    # --- half 2: every one of them is reachable in the store ----------------------
    episode_files = sorted(p for d in EPISODE_DIRS if d.is_dir() for p in d.glob("*.md"))
    print(f"episode files scanned: {len(episode_files)} across "
          f"{[str(d.relative_to(ROOT)) for d in EPISODE_DIRS if d.is_dir()]}")
    if not episode_files:
        print("FAIL: scanned ZERO episode files -- the destination store is empty or the "
              "scan paths are wrong; either way nothing below could have failed")
        return 1

    seen: dict[str, list[str]] = {}
    for path in episode_files:
        for lesson_id in MARKER_RE.findall(path.read_text(encoding="utf-8")):
            seen.setdefault(lesson_id, []).append(path.name)

    print(f"distinct lesson provenance markers found in the store: {len(seen)}")
    missing = [i for i in expected if i not in seen]
    if missing:
        failures.append(f"{len(missing)} of {len(expected)} lesson(s) have NO episode carrying "
                        f"'- artifact-ref: lesson:<id>': {missing}")
    unexpected = sorted(set(seen) - set(expected))
    if unexpected:
        failures.append(f"{len(unexpected)} provenance marker(s) name ids that were not in the "
                        f"pre-migration snapshot: {unexpected}")

    if failures:
        for line in failures:
            print(f"FAIL: {line}")
        return 1

    print(f"PASS: 0 active lessons; all {len(expected)} migrated lesson ids are reachable "
          f"in the episode store across {len(episode_files)} episode files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
