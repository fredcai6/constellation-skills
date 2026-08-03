# Implementer Handoff

## Gate
`g5-cut-intake-implement` (issue #308, epic-298)

## Task
**Live agents stop reading the lessons bank.** Remove every instruction that tells a running agent to READ `.agent-work/LESSONS.md`'s Active section, and remove the context-manifest declaration that mechanically loads it. Agents work from local (`docs/agents/`) and global doctrine only.

**This is a cutover of the READ path, not a demolition of the writer.** Everything that WRITES lessons survives untouched.

## Protected Intent
Two things must still be true when you are done:
1. The lessons **writer** works exactly as it does now. `apply_lessons_delta.py`, the Commander spine's `feedback` step, `verify_lessons_applied.py`, and the `lessons-auditor` skill are all untouched. The Curator drains a bank someone still fills.
2. A launch order still carries **platform invariants** and its charter-lite doctrine-carrier role. You remove the *lessons half* of that block, not the block.

## The intake set — 6 sites across 5 files, and I derived this by command, not by memory
Reproduce it yourself before editing: `python .agent-work/issue-308/checks/lesson_intake_is_cut.py` (currently RED, and it prints every site it matched).

| # | file | what to remove |
|---|---|---|
| 1 | `skills/admiral/SKILL.md:61` | "The project's lessons inbox (`.agent-work/LESSONS.md` Active section) and platform invariants ride in every launch order's inherited-context block." — drop the lessons half, keep platform invariants. |
| 2 | `skills/admiral/templates/ADMIRAL_SPINE.template.json:22` | In the **`latitude`** task (NOT `context` — this is the site an earlier enumeration missed): "…then docs/agents/ORCHESTRATOR_CONTEXT.md and the Active section of .agent-work/LESSONS.md if present." |
| 3 | `skills/admiral/templates/LAUNCH_ORDER.template.md:57` | The inherited-context placeholder `<Active lessons from .agent-work/LESSONS.md relevant to this mission; platform/technical invariants …>` — remove the lessons clause, keep the invariants clause. |
| 4 | `skills/charter/templates/AGENT_GUIDE.template.md:75` | "…read the Active section before planning; update it only through `apply_lessons_delta.py`…" — the READ instruction goes; the write-path sentence may stay. |
| 5 | `skills/commander/templates/COMMANDER_SPINE.template.json:22` | The `context` imperative's "Read the Active section of .agent-work/LESSONS.md if it exists: these are distilled workflow lessons from prior runs — condition planning and handoff authoring on them, and note any lesson this run's evidence contradicts (it becomes a disconfirm op at the feedback step)." |
| 6 | `skills/commander/templates/COMMANDER_SPINE.template.json:34` | The `context_refs` declaration entry `{"root": "durable", "path": ".agent-work/LESSONS.md", "required": false}`. |

**Do NOT touch** the other `LESSONS.md` mentions in `COMMANDER_SPINE.template.json` — there are **5 occurrences in that file** and only the two above are the read path. The other three are the writer: the `feedback` imperative (`:109`), `verify_lessons_applied.py --file` (`:112`), and the `git-change-policy` `deny_globs` entry (`:125`). A grep-and-delete over that filename in this file destroys the writer. (The gate's own c2 check originally *was* that grep; I corrected it through the engine before dispatching you, because it was unsatisfiable.)

**Also leave alone:** `skills/lessons-auditor/**` (the auditor), `scripts/apply_lessons_delta.py` (the writer), `skills/commander/references/commander-core.md:60` (write path), `skills/admiral/SKILL.md:60` and `:67` (staging/audit, i.e. writing), `skills/admiral/templates/ADMIRAL_SPINE.template.json:49` and `:57` (the closeout audit — writing), `skills/admiral/references/fleet-doctrine.md:7` (tells the Admiral *not* to relearn platform doctrine there — not a read instruction), `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md:22` (records an originating lesson id).

## Blast radius on the tests — larger than the gate plan said, measured by me
The frozen plan named only `tests/test_context_manifest.py`. **That is under-inclusive.** Removing site 6 deletes *the only shipped `durable` declaration in the corpus*, and at least two test modules use it as their fixture:

- `tests/test_context_manifest.py:550` — the `EXPECTED` literal pins `("durable", ".agent-work/LESSONS.md", False)` as an exact tuple. Its own docstring says this literal is deliberately the only place a dropped entry is visible: **a deliberate change here is a two-line diff, an accidental one is a failure.** This is a deliberate change. Drop the row.
- `tests/test_episode_capture.py:146-200` — three tests (`test_roots_durable_is_the_checkout_root_not_the_agent_work_directory`, `test_roots_durable_resolves_the_one_shipped_declaration_without_double_nesting`, `test_roots_durable_is_resolved_from_the_repo_root_not_the_checklist_directory`) resolve "the one shipped `durable` declaration" and assert it is `.agent-work/LESSONS.md`. **Their subject is the resolution mechanics — the double-nesting trap and the repo-root-vs-checklist-dir trap — not this particular path.** Rework them to construct a synthetic `{"root": "durable", "path": ...}` entry so they keep testing the trap. **Do not delete them**: they guard a real silent defect, and after this change there is no shipped declaration to rediscover it with.

**Both test files are pre-authorized.** So is any other test the suite proves is pinned — find them by running the suite, and derive the failure distribution mechanically: `python -m pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`. Report that command's output, never a glance at the tail.

`scripts/episode_capture.py:66-68` and `:162-163` carry *comments* naming `.agent-work/LESSONS.md` as the single shipped declaration. Update the comments to match reality — a comment describing a declaration that no longer exists is the stale-claim defect this issue keeps recording. Do not change that file's behaviour.

## Close Criteria
- `python .agent-work/issue-308/checks/lesson_intake_is_cut.py` exits 0. **Run it before you edit and paste the red transcript** — it names every site, and its own history is a warning: an earlier version of this guard used a character class excluding the dot and so went green against three live intake sites. Read *which sites it names*, do not trust its exit code alone.
- The corrected c2: `python -c "import json,sys; d=json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json',encoding='utf-8')); refs=d['tasks']['context']['context_refs']; sys.exit(2) if not refs else None; bad=[e['path'] for e in refs if 'LESSONS.md' in e['path']]; print('context_refs entries:',len(refs),'| naming LESSONS.md:',bad); sys.exit(1 if bad else 0)"` exits 0 (it is red now, printing 6 entries and the offender).
- Every edited JSON template still parses: `python -c "import json,glob; [json.load(open(p,encoding='utf-8')) for p in glob.glob('skills/*/templates/*.json')]"`.
- Full suite green: `python -m pytest -q`.

## Constraints
- **Edit shipped compact-format JSON templates SURGICALLY as raw text.** Never round-trip through `json.load`/`json.dump` — it reflows the whole file and destroys blame. Re-validate with `json.load` afterwards. This is standing doctrine in this corpus, not my preference.
- Interpreter is `python`. **`py` has no pytest and reports a silently green suite.**
- Single-quote grep patterns in shell strings: backticks inside double quotes are executed by this shell and produce a refusal for the wrong reason.
- Never `git checkout <file>` to undo a probe mutation — it reverts your real edit too. Snapshot to a scratch copy.
- Worktree is `C:/Programs/constellation-skills-wt/e298-308`. **Never touch `C:/Programs/constellation-skills`.**

## Deliverable Path Check
All edited paths are **committed** (`git check-ignore` exits 1 on each): `skills/**`, `tests/**`, `scripts/episode_capture.py`.

## Required Evidence
**Load-bearing — prove rigorously:**
1. `lesson_intake_is_cut.py` red before (with the site list it printed) and green after, both exit codes.
2. The corrected c2 command, red before and green after.
3. Full suite counts, and if anything reds, the mechanically-derived distribution.
4. For each of the 6 sites: the before and after text of the line you changed, so the reviewer can confirm the *lessons half* went and the *invariants half* stayed.

**Confirmatory — spot-check:**
5. JSON templates all parse.
6. `git diff --stat` — assert the file count and state it.

## Suggested Model Tier
`stronger` — the risk is not the edit but the over-reach: five of the LESSONS.md mentions in the Commander spine must survive and two must go, and the test rework has to preserve what those tests actually guard.

## Authority
Already decided, not yours to revisit: the read path is cut, the writer survives, and the `durable` declaration goes even though it is the corpus's only one. **You decide** how the reworked `test_episode_capture.py` tests construct their synthetic declaration, and the exact replacement wording at each of the 6 sites.

## Stop Conditions
Stop and return if: cutting a site would require touching the writer, the auditor, or `apply_lessons_delta.py`; removing the `durable` declaration breaks something you cannot rework without a design call; the guard cannot be made to go green without weakening it; or the suite reds outside the two named test files for a reason you cannot attribute.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/issue-308/crew-handoffs/g5-implement-result.md`: completed slice, files changed with an asserted count, test mode satisfied, all four load-bearing evidence items, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback. Do not commit.
