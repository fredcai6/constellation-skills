"""Surgical raw-text edit of ADMIRAL_SPINE.template.json (#447 g3).

Same discipline as the commander edit: raw text only, newline="" so the file's 66
CRLF endings survive, every span located by START/END markers and sliced rather than
retyped.

THE ONE THING THIS EDIT MUST NOT DO: repoint the lessons-auditor dispatch at
`episodes/`. An "episode auditor" that reads the store and routes dispositions IS the
playbook, rebuilt under a new directory name. The dispatch and its whole
disposition-routing paragraph are DELETED.
"""
from pathlib import Path

SPINE = Path("skills/admiral/templates/ADMIRAL_SPINE.template.json")

text = SPINE.read_text(encoding="utf-8", newline="")
crlf_before = text.count("\r\n")
lines_before = len(text.split("\r\n"))

RECORD_NOT_A_RULE = (
    "An episode is a record, not a rule: write what you observed, and do NOT write a "
    "rule for a future agent to follow — a rule to follow belongs in docs/agents/* "
    "and is a human's call."
)


def cut(start: str, end: str, replacement: str) -> None:
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


# --- closeout.imperative, steps 1 and 2 -----------------------------------------------
# Step 1 (run brief + lessons-auditor subagent + the graduate-and-retire / template-delta /
# Charter-nomination / export / inbox-delta / drop-with-reason routing + apply_lessons_delta
# + authority=human + bank_reason) is deleted outright. Step 2 becomes the epic's episode
# capture. The surgical-raw-text-JSON warning is kept -- it is generally true of every
# shipped compact template and still applies.
excised = text[
    text.index("The run cannot close with unrouted observations."):
    text.index(" 3) Hand the epic's net change to a constellation-cartographer subagent")
]
for vocabulary in ("lessons-auditor", "bank_reason", "apply_lessons_delta", "graduate",
                   "AGENT_FEEDBACK.md", "LESSONS.md", "authority=human"):
    if vocabulary not in excised:
        raise SystemExit(f"excised span does not contain {vocabulary!r} -- wrong span")
if "episodes" in excised:
    raise SystemExit("excised span already names the store -- re-read before cutting")

cut(
    "The run cannot close with unrouted observations.",
    " 3) Hand the epic's net change to a constellation-cartographer subagent",
    "The run cannot close without a record of what happened. 1) Write the epic "
    "retrospective as EPISODES: one episode per distinct thing that happened across the "
    "epic — not one per wave, and not a summary — each stating its task-intent, "
    "expected-behavior, observed-behavior, impact-cost and workaround, and each harvesting "
    "what the ADMIRAL_LOG, the crew Workflow Feedback and the Commander returns actually "
    "recorded. " + RECORD_NOT_A_RULE + " Write the delta to "
    ".agent-work/<work-id>/episode-delta.json and apply it deterministically: python "
    "<admiral-skill-dir>/scripts/apply_episode_delta.py --delta "
    ".agent-work/<work-id>/episode-delta.json --store-root episodes. Pass --store-root on "
    "every invocation: the writer's default resolves relative to the installed skill "
    "directory, so an installed copy would silently build a store at "
    "~/.claude/skills/constellation-admiral/episodes — outside the repo — while every gate "
    "reported green. Never hand-edit a file under episodes/: that writer is the only write "
    "path into it. 2) When any part of this closeout edits a shipped compact-format JSON "
    "template, edit the raw text surgically (never round-trip it through "
    "json.load/json.dump, which reflows the file and destroys blame) and re-validate with "
    "json.load afterward.",
)

# --- closeout postconditions ----------------------------------------------------------
# c1: statement rewritten, check stays null. c2: RETARGETED onto the capture gate.
# c6 (verify_lessons_applied.py) is DELETED -- terminal, so removing it renumbers nothing.
# c3, c4, c5 are untouched.
cut(
    '{"id": "c1", "statement": "lessons audit ran with fresh context',
    '\r\n        {"id": "c3", "statement": "architecture reconciled',
    '{"id": "c1", "statement": "the epic\'s observations recorded as episodes — what was '
    'observed, with no rule written for a future agent to follow", "check": null, '
    '"satisfied": false},\r\n        {"id": "c2", "statement": "at least one episode in the '
    'store records this epic\'s work id", "check": {"kind": "command", "command": "python '
    '<admiral-skill-dir>/scripts/verify_episode_captured.py <work-id> --store-root episodes '
    '--phase feedback"}, "satisfied": false},',
)
# c6's closing `],` is NOT a unique end marker -- every task's postconditions array ends
# the same way -- so this span is taken from the start marker to the FIRST following
# array close and then asserted, rather than trusting a marker that matches four times.
C6_START = ',\r\n        {"id": "c6", "statement": "no threshold-ripe lesson left unpaid'
if text.count(C6_START) != 1:
    raise SystemExit("c6 start marker not unique")
i = text.index(C6_START)
j = text.index('\r\n      ],', i)
span = text[i:j]
if "verify_lessons_applied.py" not in span or span.count('{"id":') != 1:
    raise SystemExit(f"c6 span is not exactly the one terminal condition: {span[:200]!r}")
text = text[:i] + text[j:]

SPINE.write_text(text, encoding="utf-8", newline="")
after = SPINE.read_text(encoding="utf-8", newline="")
CRLF = "\r\n"
print(f"CRLF before={crlf_before} after={after.count(CRLF)}")
print(f"lines before={lines_before} after={len(after.split(CRLF))}")
print(f"bare LF (must be 0): {after.count(chr(10)) - after.count(CRLF)}")
