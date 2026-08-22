"""Presence test for issue #142 clamp restoration.

Asserts the transcription-grade four-clause completion doctrine, or the
verbatim pointer-with-force sentence, is present in each target skill file so
the #101 stripping defect (bare pointer with no load-time force) cannot
silently recur. Substring checks only -- this does not judge quality, only
that the required wording exists.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

FOUR_CLAUSE_KEYPHRASES = [
    "Start here — drive the engine before you touch",
    "This is your **first command**",
    "is the MIDDLE of",
    "not the end",
    "Do not end your turn while any",
    "is never a reason to end your turn",
    "Work the engine never saw did not happen.",
]

FULL_CLAUSE_TARGETS = [
    "skills/implementer/SKILL.md",
    "skills/reviewer/SKILL.md",
    "skills/commander/references/commander-core.md",
    "skills/admiral/SKILL.md",
    "skills/interrogator/SKILL.md",
]

POINTER_SENTENCE = (
    "Drive every step through the checklist engine and finish its sequence "
    "— final `advance`, then `release`, as journaled actions. "
    "Work the engine never saw did not happen. "
    "Full completion doctrine: `_shared/global-everyone.md`."
)

POINTER_ONLY_TARGETS = [
    "skills/cartographer/SKILL.md",
    "skills/charter/SKILL.md",
    "skills/curator/SKILL.md",
    "skills/lessons-auditor/SKILL.md",
    "skills/scout/SKILL.md",
]

RAIL_CITATION_MARKER = "canonical enforcement source"


def check_full_clause(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [kp for kp in FOUR_CLAUSE_KEYPHRASES if kp not in text]


def check_pointer_only(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return POINTER_SENTENCE in text


def main() -> int:
    failures = []

    for rel in FULL_CLAUSE_TARGETS:
        path = REPO / rel
        if not path.exists():
            failures.append(f"{rel}: FILE NOT FOUND")
            continue
        missing = check_full_clause(path)
        if missing:
            failures.append(f"{rel}: missing key phrases: {missing}")

    for rel in POINTER_ONLY_TARGETS:
        path = REPO / rel
        if not path.exists():
            failures.append(f"{rel}: FILE NOT FOUND")
            continue
        if not check_pointer_only(path):
            failures.append(f"{rel}: verbatim pointer-with-force sentence not found")

    global_everyone = REPO / "skills/_shared/global-everyone.md"
    if not global_everyone.exists():
        failures.append("skills/_shared/global-everyone.md: FILE NOT FOUND")
    else:
        text = global_everyone.read_text(encoding="utf-8")
        if RAIL_CITATION_MARKER not in text:
            failures.append(
                "skills/_shared/global-everyone.md: missing rail-canonicality citation"
            )

    if failures:
        print("PRESENCE TEST: FAIL")
        for f in failures:
            print(f" - {f}")
        return 1

    print("PRESENCE TEST: PASS")
    print(f" - {len(FULL_CLAUSE_TARGETS)} full-clause targets OK")
    print(f" - {len(POINTER_ONLY_TARGETS)} pointer-only targets OK")
    print(" - global-everyone.md rail-canonicality citation OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
