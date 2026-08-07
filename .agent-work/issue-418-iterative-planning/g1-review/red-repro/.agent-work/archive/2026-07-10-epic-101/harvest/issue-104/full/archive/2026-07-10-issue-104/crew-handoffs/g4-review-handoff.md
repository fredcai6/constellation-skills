# Reviewer Handoff

Concise. Paste, don't point.

## Gate
`g4-review` (issue #104, constellation-curator)

## What was implemented
Curator install wiring: `SKILL_SCRIPT_BUNDLES["curator"]` + `SKILL_REFERENCE_BUNDLES["curator"]`
in `scripts/install_constellation.py`, a `SKILL_INDEX.md` entry, and 3 per-skill install tests.
Implementer report: `.agent-work/issue-104/crew-handoffs/g4-implement-result.md`.

## How to inspect
Worktree `C:\Programs\constellation-wt-104`. `git diff scripts/install_constellation.py
SKILL_INDEX.md tests/test_install_constellation.py`. Reproduce the runs.

## Close criteria to verify (yes/no + evidence)
1. `SKILL_SCRIPT_BUNDLES["curator"] == ("curate_corpus.py",)`.
2. `SKILL_REFERENCE_BUNDLES["curator"] == _GLOBAL_EVERYONE` — reuses the EXISTING constant
   (no new `global-*.md` filename, no new bucket constant). Confirm the diff adds only the
   two dict lines + index + tests, and changed NO other skill's bundle entry.
3. `SKILL_INDEX.md` has one curator entry in the file's format.
4. The 3 install tests assert: script bundles into `constellation-curator/scripts/`; the
   everyone bucket (`global-everyone.md` + `windows.md`) lands in
   `constellation-curator/references/`; curator installs/discovers as a skill. Confirm each
   would RED if its backing dict line were removed — reproduce ONE falsification yourself
   (delete a dict line in a throwaway git-stash-safe way OR monkeypatch, observe red, then
   restore). Leave the tree clean.
5. `test_bundled_scripts_carry_their_sibling_imports` still passes (curate_corpus.py is
   stdlib-only → no sibling-import obligation).
6. `py -m pytest tests/ -q` green (should be 467 passed, 152 subtests) and
   `py -m pytest tests/test_install_constellation.py -v -k curator` shows 3 curator tests pass.
7. Scope: only the three named files changed; `git status --short` shows exactly them.

## Verification commands
```bash
cd C:/Programs/constellation-wt-104
git diff --stat
git diff scripts/install_constellation.py SKILL_INDEX.md
py -m pytest tests/test_install_constellation.py -v -k curator
py -m pytest tests/ -q
```

## Suggested Model Tier
`simple bounded — reproduce + one falsification`

## Stop Conditions
Return BLOCK with the specific failing criterion + reproduction if any fails (a new
global-*.md filename, another skill's entry changed, or a test that still passes with its
dict line removed = BLOCK).

## Return Format
Return REVIEW_RESULT with an explicit `verdict: APPROVE` or `verdict: BLOCK` token,
per-criterion findings with reproduced evidence (incl. your falsification + restore),
out-of-scope observations, workflow feedback. Keep it focused. WRITE the full REVIEW_RESULT
as your final message AND to the given result path before going idle.
