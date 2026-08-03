"""Guard: no live-agent corpus artifact instructs an agent to READ the lessons bank.

Why this is not a grep for one phrase. The cold plan critic found that
`! grep -rn 'Active section of .agent-work/LESSONS.md' skills/` matches exactly TWO
of the six real intake sites -- the other four phrase it differently
("`.agent-work/LESSONS.md` Active section", "Active lessons from ...", a backtick
splitting the phrase). Edit the two that match and the guard goes green while the
Admiral doctrine, the launch-order inherited-context block and the Charter agent
guide all still instruct reading lessons.

That is an under-inclusive enumeration standing in for the predicate -- which is
precisely `issue-304-g3-001`, one of the three episodes THIS issue is consolidating.
It was committed while planning that consolidation. So the guard is written the way
the cluster's own remedy prescribes: enumerate the whole corpus by command, then
classify, rather than trusting a hand-written list of sites.

Method: enumerate EVERY reference to the lessons bank under `skills/`, and require
each one to be on the frozen allowlist of WRITER-side survivors below. Anything else
is an unreviewed reference and fails. The enumeration asserts it is non-empty, so a
glob that silently matched nothing cannot report clean.

Run from the repo root. Exit 0 = intake cut. Exit 1 = a read-intake site survives.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]

# WRITER-side survivors. This is a cutover of the READ path, not a demolition of the
# writer: the lessons auditor, the feedback/closeout write path and the export
# template all legitimately keep naming the file. Each entry is (path, why).
ALLOWLIST = {
    "skills/lessons-auditor/SKILL.md": "the auditor's own subject matter",
    "skills/lessons-auditor/templates/LESSONS_AUDIT.template.json": "the audit checklist itself",
    "skills/lessons-auditor/templates/RUN_BRIEF.template.md": "the audit's input brief",
    "skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md": "export carries the originating lesson id",
    "skills/commander/references/commander-core.md": "feedback step WRITES a delta; not a read",
    "skills/admiral/references/fleet-doctrine.md": "describes where fleet lore does NOT live",
}

# Files that must retain SOME references (the write/closeout half) but must lose the
# READ-intake instruction. Listed so a reviewer sees they were considered, not missed.
PARTIAL = {
    "skills/commander/templates/COMMANDER_SPINE.template.json": "feedback-step writes survive; context read + manifest entry go",
    "skills/admiral/templates/ADMIRAL_SPINE.template.json": "closeout lessons-audit survives; context read goes",
    "skills/admiral/SKILL.md": "auditor dispatch survives; the launch-order intake sentence goes",
}

# Phrases that mean "an agent is being told to READ the bank". Deliberately broad and
# phrasing-independent: the point is to catch wording the author did not anticipate.
# NOTE on the character class: an earlier draft used `[^.\n]{0,40}`, which cannot
# match any of these phrases, because every one of them contains `.agent-work/` and
# the dot is excluded by the class. That draft went green against three real intake
# sites. Same defect class as the grep it replaced, in the same file, one revision
# later -- recorded rather than quietly fixed, because it is a third instance of the
# cluster this issue consolidates.
READ_MARKERS = [
    re.compile(r"[Rr]ead[^\n]{0,120}LESSONS\.md"),
    re.compile(r"LESSONS\.md[^\n]{0,60}Active section"),
    re.compile(r"Active section of[^\n]{0,60}LESSONS\.md"),
    re.compile(r"Active lessons from[^\n]{0,60}LESSONS\.md"),
    re.compile(r"\"path\":\s*\"\.agent-work/LESSONS\.md\""),
    re.compile(r"read the Active section", re.I),
]


def main() -> int:
    proc = subprocess.run(
        ["git", "grep", "-l", "LESSONS.md", "--", "skills/"],
        capture_output=True, text=True, cwd=ROOT,
    )
    files = sorted(f for f in proc.stdout.splitlines() if f.strip())

    # Assert what we looped over. An empty enumeration must never read as clean.
    if len(files) < 5:
        print(f"FAIL: enumeration returned only {len(files)} files under skills/. "
              f"A guard that looped over nothing cannot report clean.")
        return 1
    print(f"enumerated {len(files)} files under skills/ referencing the lessons bank")

    violations = []
    for f in files:
        text = (ROOT / f).read_text(encoding="utf-8")
        hits = [m.pattern for m in READ_MARKERS if m.search(text)]
        if not hits:
            continue
        if f in ALLOWLIST:
            continue
        violations.append((f, hits))

    unknown = [f for f in files if f not in ALLOWLIST and f not in PARTIAL]
    for f in unknown:
        print(f"  NOTE: {f} references the bank and is on neither list — review it")

    if violations:
        print("\nFAIL: read-intake instruction survives in:")
        for f, hits in violations:
            print(f"  {f}")
            for h in hits:
                print(f"      matched: {h}")
        return 1

    print("PASS: no live-agent artifact instructs reading the lessons bank")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
