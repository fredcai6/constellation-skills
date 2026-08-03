# Reviewer Handoff

## Gate
`g5-review` (issue #308, epic-298) — independent review of the lessons read-path cutover.

## Worktree
`C:/Programs/constellation-skills-wt/e298-308`. **Never touch the main checkout `C:/Programs/constellation-skills`.** Interpreter is `python` — **`py` has no pytest and reports a silently green suite.**

## The change under review
The single commit `feat(#308): cut live agents off from the lessons bank (g5 implement)` — `git show HEAD --stat`, and `git show HEAD -- skills/ tests/ scripts/episode_capture.py` for the substance. Ignore the `.agent-work/**` files in that commit; they are workflow artifacts.

The implementer's account is at `.agent-work/issue-308/crew-handoffs/g5-implement-result.md`, and its handoff at `.agent-work/issue-308/crew-handoffs/g5-implement-handoff.md`. **Read both as claims, not as evidence.**

## What this gate was required to do
Live agents stop READING `.agent-work/LESSONS.md`'s Active section. Six sites across five files, plus the `context_refs` declaration that mechanically loaded it. **The writer survives untouched** — `apply_lessons_delta.py`, the Commander spine's `feedback` step, `verify_lessons_applied.py`, the `lessons-auditor` skill. **Launch orders still carry platform invariants** and the charter-lite doctrine-carrier role; only the lessons half of that block goes.

## Hunt these three specifically
Named by the gate plan before any of this was written, so they are the load-bearing part of your review:

1. **An intake site the enumeration missed.** The acceptance guard `.agent-work/issue-308/checks/lesson_intake_is_cut.py` is now green — **assume it is under-inclusive until you prove otherwise.** Its own history is the reason: an earlier revision used a character class excluding the dot, so it could not match any phrase containing `.agent-work/` and went green against three live intake sites. Build your own enumeration by a different route (different patterns, wider scope than `skills/`, or a semantic read of every file that mentions the bank) and compare. **Assert the count you looped over.**

2. **A template left syntactically valid but semantically broken.** Every JSON template still parses — that is necessary and nowhere near sufficient. An imperative can parse fine and instruct nonsense: a dangling "then", a sentence whose object was excised, a postcondition that now refers to a read that no longer happens, a `context` step whose `c1` statement still promises something the imperative no longer does. Read the edited imperatives end to end as prose.

3. **Platform-invariant guidance destroyed as collateral.** Sites 1 and 3 were compound sentences carrying both the lessons half and the invariants half. Confirm the invariants half survived intact and still reads as an instruction, and that `LAUNCH_ORDER.template.md`'s charter-lite carrier sentence is untouched.

## Two specific things to satisfy yourself about, by running code
- **The writer is intact.** `skills/commander/templates/COMMANDER_SPINE.template.json` held five `.agent-work/LESSONS.md` occurrences; two were removed and three must remain — the `feedback` imperative's `apply_lessons_delta.py` instructions, `verify_lessons_applied.py --file`, and the `git-change-policy` `deny_globs` entry. Verify by content, not by count. Then verify the writer still *works*: drive `apply_lessons_delta.py` against a scratch copy.
- **The reworked tests still test what they guarded.** `tests/test_episode_capture.py`'s `durable`-root tests protected a real silent trap (`durable_agent_work()` double-nesting `.agent-work/.agent-work/…`, and resolution from the checklist directory rather than the repo root). Their fixture — the one shipped `durable` declaration — no longer exists. Determine **by construction** whether the reworked versions can still fail: break the production code they cover and confirm they go red. A test reworked onto a synthetic fixture is exactly where a guard quietly stops guarding.

## Independent reproduction
- `python .agent-work/issue-308/checks/lesson_intake_is_cut.py` (green now).
- The corrected c2: `python -c "import json,sys; d=json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json',encoding='utf-8')); refs=d['tasks']['context']['context_refs']; sys.exit(2) if not refs else None; bad=[e['path'] for e in refs if 'LESSONS.md' in e['path']]; print('context_refs entries:',len(refs),'| naming LESSONS.md:',bad); sys.exit(1 if bad else 0)"`.
- `python -m pytest -q` — report the counts you observed, not the ones you were told.
- To see anything red, load the pre-change file from `git show HEAD~1:<path>` into a scratch location. **Do not `git checkout` a file under review** — it reverts real edits.

## Out of scope — do not report as defects
- `.agent-work/LESSONS.md`'s Active section is empty (g4 migrated all 20 lessons into `episodes/`) and its **preamble still says "Read the Active section at the Commander context step"**. That is known, unreachable through the sanctioned write path, and filed as **#400**. Do not report it again; do tell me if you find a *reachable* instance I could have fixed.
- Downstream repos' already-compiled `docs/agents/AGENT_GUIDE.md` still carry the old read instruction. The guard only scans `skills/`. Known, raised by the implementer.
- The episode store's schema constraints — filed as **#399**.

## Deliverable
Write `REVIEW_RESULT` to `.agent-work/issue-308/crew-handoffs/g5-review-result.md` with an explicit **ACCEPT** or **REWORK**. For each finding: severity, the exact command that demonstrates it, and its output. State which of the three hunted classes you found and which you searched for and did **not** find — **a null you actually looked for is a result; silence is not.** Include a workflow-feedback section.

Do not commit; do not edit production code.
