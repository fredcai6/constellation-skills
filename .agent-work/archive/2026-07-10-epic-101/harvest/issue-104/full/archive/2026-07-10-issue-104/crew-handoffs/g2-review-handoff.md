# Reviewer Handoff

Concise. Paste, don't point.

## Gate
`g2-review` (issue #104, constellation-curator)

## What was implemented
`skills/curator/SKILL.md` (new, untracked) + one line added to `SKILL_NAMES` in
`tests/test_install_constellation.py` (green-at-boundary fixture edit). Implementer
report: `.agent-work/issue-104/crew-handoffs/g2-implement-result.md`.

## How to inspect
Worktree `C:\Programs\constellation-wt-104`. Read `skills/curator/SKILL.md` and
`git diff tests/test_install_constellation.py`. Read `scripts/curate_corpus.py` to
confirm the SKILL.md describes the tool's ACTUAL behavior.

## Close criteria to verify (yes/no + evidence)
1. **Frontmatter:** `name: constellation-curator`; `description:` is THIRD-PERSON (no
   I/you/we), has a "Use when" clause, and carries an exclusion clause naming BOTH
   scout and write-a-skill; `invoker: human` key present.
2. **Dogfood:** `py scripts/curate_corpus.py --root skills | grep -i "^curator"` shows
   curator with invoker=ok, when-to-use present (no flag), exclusion present (info),
   size within budget. Reproduce it.
3. **Body covers, correctly and without contradicting curate_corpus.py:** trigger
   (human-only, never scheduled/agent-dispatched/code-change-reaction), invariant #1
   measure-before-mend (starts with curate_corpus.py; T7 mechanical-vs-semantic split),
   invariant #2 flags-never-gates (exit 0, rows not failures), mend (in-place mechanical,
   git-diff review gate, fixed linear pass / no engine checklist), route (design
   decisions -> triage), outputs (CURATOR_REPORT.md + --json, inline, no template),
   portfolio duty OPTIONAL+dormant until #106 with no dependency, error modes
   (unparseable dir = row; first run flags all invoker tags = expected).
4. **Green-at-boundary:** SKILL_NAMES gained exactly `"constellation-curator"` and
   NOTHING else changed in that file; `py -m pytest tests/ -q` is green.
5. **Scope:** only `skills/curator/SKILL.md` (SKILL.md only — no references/templates)
   and the one SKILL_NAMES line. No install_constellation.py edit, no bundle entries, no
   new curator install tests, no other skill touched, no report template shipped.

## Verification commands
```bash
cd C:/Programs/constellation-wt-104
py scripts/curate_corpus.py --root skills | grep -i "^curator"
git diff tests/test_install_constellation.py
git status --short
py -m pytest tests/ -q
ls skills/curator/   # expect: SKILL.md only
```

## Suggested Model Tier
`simple bounded`

## Stop Conditions
Return BLOCK with the specific failing criterion + reproduction if any fails.

## Return Format
Return REVIEW_RESULT with an explicit `verdict: APPROVE` or `verdict: BLOCK` token,
per-criterion findings with reproduced evidence, out-of-scope observations, workflow
feedback. Keep it focused. WRITE the full REVIEW_RESULT as your final message AND to the
given result path before going idle.
