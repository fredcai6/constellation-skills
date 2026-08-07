import subprocess, sys

E = r"C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/checklist_engine.py"
F = ".agent-work/epic418-h-447/g5-review/review.json"
SID = "g5-reviewer-447"


def run(*a):
    p = subprocess.run([sys.executable, E, "--file", F, *a, "--session-id", SID],
                       capture_output=True, text=True, encoding="utf-8")
    print(f"  exit={p.returncode} {(p.stdout or '').strip()[:130]}{(p.stderr or '').strip()[:200]}")


CANDIDATES = [
("c6-census",
 "README.md's skill table lists 18 skills while README.md:31 in the same file says the corpus is 19, because constellation-how-to-talk was never added to the table. PRE-EXISTING at 77e428d and NOT caused by g5: at HEAD the table also had a phantom constellation-lessons-auditor row (the skill directory was deleted at g4), so 19 rows accidentally matched the count for the wrong reason. g5 correctly removed the phantom, which makes the real omission visible. Note g5 left SKILL_INDEX.md exactly correct (19 entries, all matching a directory on disk). Fix: add a constellation-how-to-talk row to README's table."),

("c6-census",
 "tests/data/store_mentions.approved.txt still carries repeated reason text: 52 entries share only 29 distinct reasons across 7 groups (x9 verify_episode_captured.py, x5 install_constellation.py, x5 docs/CONSTELLATION_OVERVIEW.md, x3 TRIPWIRES.md, x3 episode_capture.py, x3 the two spine templates, x2 install_constellation.py). This is the same STRUCTURAL shape as the defect g5 was sent to fix, but it is NOT that defect here: I read every group and none covers a line that instructs an agent to read the store and condition behaviour on it. Every g5-touched entry carries a bespoke reason (verified mechanically: zero g5-added entries sit under a repeated reason), and all 7 groups live in files g5 never touched, so they were out of this gate's scope. The retired-name census sets the better standard at 53 entries / 53 distinct reasons. Recommend a follow-up giving each store-mention entry its own reason."),

("c10-prescriptive",
 "The redefined `harvest` in docs/agents/GLOSSARY.md under-covers a live second sense. The new definition is 'Gathering what a run's own artifacts recorded and writing it into the episode store as episodes', but the Admiral's harvest-before-sweep (skills/admiral/SKILL.md step 3, references/fleet-doctrine.md, skills/commander-delegated/SKILL.md, skills/_shared/global-orchestrator.md, scripts/stage_feedback.py) harvests a worktree-local CONSTELLATION_FEEDBACK.md export into the durable root - not into the episode store as episodes. NOT A BLOCKER and not a regression: no live use reads the episode store back, which is the property that matters, and the OLD definition ('Reading stored episodes back to act on them') covered ZERO live uses, so this is a strict improvement. But one term now names two things, against the repo's one-name-per-thing standard. Options: widen the definition to cover collecting a run's durable artifacts generally, or give the sweep sense its own term."),

("c2-survivors",
 "scripts/agent_work_root.py's edited docstring has a ragged line wrap: 'The durable run-record artifacts (CONSTELLATION_FEEDBACK.md, plus its sidecar / ledger) must be shared by / every linked worktree of a repo' leaves 'ledger) must be shared by' on a short line where the surrounding text wraps near column 72. Cosmetic only, content is correct. Worth a one-line reflow whenever the file is next touched."),

("r6-fowler",
 "Fowler data-clump (from the recorded pass, non-blocking): the approval key (entry.path, entry.mention) is assembled at two sites in scripts/verify_retirement.py, once per census leg. A one-line `key` property on ApprovedEntry would name the concept once and make both legs read identically."),

("c6-census",
 "SECONDING the implementer's own open note, which the census header records rather than silently approving: scripts/stage_feedback.py still writes an AGENT_FEEDBACK.md and a lessons-delta.json into its staging dir and names verify_agent_feedback.py, a verifier deleted at g4. I independently confirmed it is orphaned - git grep finds no shipped surface referencing stage_feedback.py outside its own file, its tests, verify_retirement.py's explanatory comment, and the historical design record. It accounts for 8 of the 53 census approvals. Out of g5's scope by explicit ruling; worth an issue to either retire the script or update it to the episode store."),
]

for frm, statement in CANDIDATES:
    print(f"flag <- {frm}")
    run("flag-candidate", "--from", frm, "--statement", statement)
