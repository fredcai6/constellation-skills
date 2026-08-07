"""Surgical raw-text edit of COMMANDER_SPINE.template.json (#447 g3).

Raw text, never json.load/json.dump: a round-trip reflows every line of a compact
spine and destroys blame. Read and write with newline="" so the file's 135 CRLF
endings survive byte-for-byte -- flipping every line ending is the same defect as a
reflow. Every span is located by START and END markers and sliced out rather than
hand-retyped, so a drifted anchor raises instead of silently editing nothing, and a
transcription slip in a 3000-character imperative cannot pass as a match.
"""
from pathlib import Path

SPINE = Path("skills/commander/templates/COMMANDER_SPINE.template.json")

text = SPINE.read_text(encoding="utf-8", newline="")
crlf_before = text.count("\r\n")
lines_before = len(text.split("\r\n"))

RECORD_NOT_A_RULE = (
    "An episode is a record, not a rule: write what you observed, and do NOT write a "
    "rule for a future agent to follow — a rule to follow belongs in docs/agents/* "
    "and is a human's call."
)


def cut(start: str, end: str, replacement: str) -> None:
    """Replace text[start_marker : end_marker) exactly once, asserting both markers
    are unique so a moved anchor fails loudly."""
    global text
    if text.count(start) != 1:
        raise SystemExit(f"start marker not unique ({text.count(start)}): {start[:90]!r}")
    i = text.index(start)
    if text.count(end) != 1:
        raise SystemExit(f"end marker not unique ({text.count(end)}): {end[:90]!r}")
    j = text.index(end, i)
    if j <= i:
        raise SystemExit(f"end marker precedes start: {start[:60]!r}")
    text = text[:i] + replacement + text[j:]


# --- feedback.imperative -------------------------------------------------------------
# Keep the honest-reflection opening and the crew Workflow Feedback harvest. Everything
# from the AGENT_FEEDBACK append onward is apply-or-defer / ripeness / bank_reason /
# dormancy / export-resolve-defer machinery, and it retires WITH the playbook rather than
# being translated into episode vocabulary.
excised = text[
    text.index("Append one dated entry for this work-id"):
    text.index('",\r\n      "preconditions": [{"id": "p1", "statement": "run summary accepted"')
]
for vocabulary in ("bank_reason", "apply_lessons_delta", "threshold-ripe", "LESSONS.md",
                   "AGENT_FEEDBACK.md", "verify_agent_feedback"):
    if vocabulary not in excised:
        raise SystemExit(f"excised span does not contain {vocabulary!r} -- wrong span")

cut(
    "Append one dated entry for this work-id",
    '",\r\n      "preconditions": [{"id": "p1", "statement": "run summary accepted"',
    "Then record what happened as EPISODES: one episode per distinct thing that happened "
    "— not one per run, and not a summary — each stating its task-intent, "
    "expected-behavior, observed-behavior, impact-cost and workaround. "
    + RECORD_NOT_A_RULE +
    " Write the delta to .agent-work/<work-id>/episode-delta.json and apply it "
    "deterministically: python <commander-skill-dir>/scripts/apply_episode_delta.py --delta "
    ".agent-work/<work-id>/episode-delta.json --store-root episodes. Pass --store-root on "
    "every invocation: the writer's default resolves relative to the installed skill "
    "directory, so an installed copy would silently build a store at "
    "~/.claude/skills/constellation-commander/episodes — outside the repo — while "
    "every gate reported green. Never hand-edit a file under episodes/: that writer is the "
    "only write path into it. Then run the capture gate before advancing: python "
    "<commander-skill-dir>/scripts/verify_episode_captured.py <work-id> --store-root episodes "
    "--phase feedback.",
)

# The bare-'none' rule survives; the invariant check it named does not.
cut(
    "bare 'none' entries fail the invariant check.",
    " Then record what happened as EPISODES",
    "a bare 'none' does not close this step.",
)

# --- feedback postconditions ----------------------------------------------------------
# c1 is RETARGETED IN PLACE, never deleted: `c1` is the bare-form `attest` default in
# checklist_engine.py. c2 (verify_lessons_applied.py, "no threshold-ripe lesson left
# unpaid") is DELETED outright -- it is the terminal condition, so removing it renumbers
# nothing, and its obligation moves nowhere because ripeness and apply-or-defer no longer
# exist.
cut(
    '"postconditions": [{"id": "c1", "statement": "durable feedback log exists',
    '"constraints": [], "directives": null, "child_checklist": null,\r\n      "status": '
    '"pending", "status_detail": {}, "result": null, "finding": null, "evidence": [], '
    '"rework_count": 0\r\n    },\r\n    "archive": {',
    '"postconditions": [{"id": "c1", "statement": "this run captured at least one episode: '
    'an episode in the store records this work id", "check": {"kind": "command", "command": '
    '"python <commander-skill-dir>/scripts/verify_episode_captured.py <work-id> --store-root '
    'episodes --phase feedback"}, "satisfied": false}],\r\n      ',
)

# --- archive.imperative ---------------------------------------------------------------
cut(
    "Commit all remaining work, including the appended",
    " Push the branch to remote.",
    "Commit all remaining work, including this run's episodes under episodes/. That is a "
    "tracked repo-root path, so the committed episode IS the durable record: it survives "
    "`git worktree remove` and lands in a fresh clone. None of the old "
    "is-.agent-work-gitignored reasoning applies to it.",
)
cut(
    "Run the archive-phase feedback invariant check",
    " Confirm the branch is clean",
    "Run the archive-phase capture gate before marking archive complete — it "
    "additionally requires git to TRACK the episode, which is what proves the record "
    "outlived this worktree: python <commander-skill-dir>/scripts/verify_episode_captured.py "
    "<work-id> --store-root episodes --phase archive.",
)

# --- archive.c1: RETARGET IN PLACE ----------------------------------------------------
cut(
    '{"id": "c1", "statement": "work area archived and durable feedback log',
    '\r\n        {"id": "c2", "statement": "branch committed and pushed"',
    '{"id": "c1", "statement": "work area archived and this run\'s episode captured AND '
    'tracked by git, so the record survives this worktree", "check": {"kind": "command", '
    '"command": "python <commander-skill-dir>/scripts/verify_episode_captured.py <work-id> '
    '--store-root episodes --phase archive"}, "satisfied": false},',
)

# archive.c4's deny_globs is deliberately UNTOUCHED. After g4 untracks them,
# `.agent-work/LESSONS.md` and `.agent-work/AGENT_FEEDBACK.md` stop meaning "do not commit
# this record dump" and start meaning "do not re-stage the retired files" -- a stronger
# reason to keep them than the one they were added for. `episodes/` is deliberately NOT
# added there: episodes are MEANT to be committed.

SPINE.write_text(text, encoding="utf-8", newline="")
after = SPINE.read_text(encoding="utf-8", newline="")
CRLF = "\r\n"
print(f"CRLF before={crlf_before} after={after.count(CRLF)}")
print(f"lines before={lines_before} after={len(after.split(CRLF))}")
print(f"bare LF (must be 0): {after.count(chr(10)) - after.count(CRLF)}")
