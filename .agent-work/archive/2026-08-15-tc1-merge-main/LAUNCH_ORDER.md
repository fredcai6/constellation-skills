# Launch Order: `tc1-merge-main` — resolve one generated-file conflict so #588 can run CI

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

Small and precisely scoped. PR #588's content is finished and correct. This is the last thing blocking it.

## Mission

PR #588 (`tc1/worktree-identity`) is **CONFLICTING** with `main`, so GitHub cannot compute a merge commit
and therefore **never runs `pull_request` CI**. That is why the last four pushes produced no checks.

There is exactly **one** conflicted file, confirmed with `git merge-tree` before this order was written:

```
$ git merge-tree --write-tree --name-only origin/main 5992b936
map/INDEX.md
CONFLICT (content): Merge conflict in map/INDEX.md
```

**Merge `origin/main` into `tc1/worktree-identity` and resolve it.**

## Why the conflict exists — my error, not yours

`map/INDEX.md` is a **generated** code map. PR #587 merged into `main` as `6947b15e` and regenerated it;
this branch regenerated it too. Two independent regenerations of the same generated file conflict on
content.

It is conflicted only because I explicitly instructed the previous lane **not** to merge main — I was
protecting a clean Windows-CI failure-set comparison, and did not account for #587 having already landed.
That instruction is hereby withdrawn. **Merge main.**

## How to resolve it — do not hand-merge

`map/INDEX.md` is generated output. **Do not pick hunks, do not hand-edit, do not take one side wholesale
and hope.** Resolve it by **regenerating from the merged tree**:

```
git merge origin/main            # expect the conflict in map/INDEX.md only
python -m scripts.code_map build --root .
git add map/INDEX.md
git commit
```

`tests/test_code_map.py` fails the suite when the map is stale, so a correct regeneration is verifiable
rather than a matter of judgment — and that test passing is your proof the resolution is right.

**If any file other than `map/INDEX.md` conflicts, stop and report.** This order is written on the
measured claim that only that one does; a second conflict means the situation changed under me and you
should not improvise through it.

## What #588 contains, so you can confirm nothing is lost

After the merge, the branch's own changes against `main` should still be:

- `scripts/checklist_engine.py` — the worktree-identity ruling: equality not containment, git toplevel
  resolved at the single call site, fail-closed.
- `tests/test_spine_origin_isolation.py` — the ruling's tests, including the posix-form Windows assertion.
- `tests/test_explorer_templates.py` — a `git init` so its fixture is a real repo under fail-closed.
- `episodes/active/tc1-*.md` — run records, including two reworded to read as observations.
- `map/INDEX.md` — regenerated.

Plus everything #587 brought in. **If the merge appears to drop any of the above, stop and report.**

## Pre-Rulings — settled

1. **`decision:merge-main-now` — settled.** The earlier "do not merge main" instruction is withdrawn.
2. **`decision:regenerate-dont-handmerge` — settled.** The map is generated; regenerate it.
3. **`decision:content-is-final` — settled.** #588's substantive work is done and reviewed. **Do not
   revisit the predicate, the call site, the assertions, or the episodes.**

## File Ownership

**Yours:** `map/INDEX.md` (by regeneration), the merge commit, your work area.

**NOT yours — do not edit while resolving:** `scripts/checklist_engine.py`,
`tests/test_spine_origin_isolation.py`, `tests/test_explorer_templates.py`, any `episodes/` file,
`scripts/hooks/spine_rail.py` (#589 is open on it), `scripts/run_crew.py`, `.mcp.json`. Taking main's side
for files only main touched is a normal merge outcome and is not "editing" them — but you must not make
your own changes to any of them.

## Do not park

When your turn ends, your process exits. There is no scheduler and no notification will reach you. The
full suite takes ~2 minutes and **the harness auto-backgrounds a command that runs that long** — if that
happens, **poll its output file until complete.** Do not end your turn waiting. Four Commanders have lost
a dispatch to this today. Do not dispatch a crew either; everything here is yours to do in this turn.

## Evidence required

- `git merge origin/main` completed, with **only** `map/INDEX.md` conflicted.
- Map regenerated with `python -m scripts.code_map build --root .`, not hand-edited.
- Full Linux suite, cache-clean, clean env. Clear first:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  then:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q`
  Your own spine lease exports those three vars and `tests/test_mcp_identity.py:600` asserts they are
  absent; without stripping them you will see a false failure. **Expect 0 failed.** The passed count will
  now exceed the old 3010 because #587 brought its own tests in — that rise is expected. **0 failed and
  `tests/test_code_map.py` green are the bar.**
- Push to `tc1/worktree-identity`, then confirm `gh pr view 588 --json mergeable` no longer reports
  `CONFLICTING`.

## Budget

One merge. If it turns into a content dispute, stop and report.

## Stop Conditions

- Any file other than `map/INDEX.md` conflicts.
- The merge appears to drop any of #588's listed changes.
- The suite shows any failure in a clean env.
- You find yourself hand-editing `map/INDEX.md`, or about to dispatch, or about to end your turn waiting.

## Return Shape

What `spine_status` resolved to, named explicitly; the merge result and which files conflicted; how you
resolved the map; clean-env suite counts; the commit SHA; and #588's `mergeable` status after pushing.

**You are fenced from merging the PR.** The Admiral merges.
