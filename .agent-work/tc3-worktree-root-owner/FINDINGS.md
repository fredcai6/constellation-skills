# FINDINGS: stray `.worktrees/` work areas and the sibling-`-wt` origin question

Scope: investigation only, per m9 of `IMPLEMENTER_PLAN.json`. Nothing under
`.worktrees/` was deleted, moved, or otherwise modified while gathering this
evidence. All paths below are on the PRIMARY checkout
(`/home/tommy/projects/constellation-skills/.worktrees/...`), not this
worktree's own nested tree.

## 1. `.worktrees/s` and `.worktrees/t`

Both directories carry the same shape: `context/*.json` + `mechanical/*.json`
step-manifest files (contract 1, shape matching `context_manifest.py`'s
output). Inspecting `.worktrees/s/context/v1.json` and `.worktrees/t/context/g1.json`
(and the other files alongside them) directly:

```json
"run": {
  "work_id": "s",
  "generated_at": "2026-08-14T16:55:31Z",
  "roots": {
    "skill": "/home/tommy/projects/constellation-skills/.worktrees/epic-568-510",
    "repo": "/home/tommy/projects/constellation-skills/.worktrees/epic-568-510",
    "durable": "/home/tommy/projects/constellation-skills/.worktrees/epic-568-510"
  },
  "host": {
    "platform": "linux",
    "python": "3.12.3",
    "cwd": "/home/tommy/projects/constellation-skills/.worktrees/epic-568-510"
  }
}
```

`work_id` is the literal single letter `"s"` (and `"t"` in the sibling
directory) -- not a fragment or a slice of a longer identifier. `roots.skill`,
`roots.repo`, `roots.durable`, and `host.cwd` all point at
`/home/tommy/projects/constellation-skills/.worktrees/epic-568-510`, a worktree
that is real: `git log --oneline -- '*epic-568-510*'` shows commits such as
`fix(568): stop branding an agent for the start the HARD advisory instructs
(#510) (#581)` and `chore(568): sweep the epic's archived work areas onto main
(#583)`, and that worktree's own run history is now archived at
`.agent-work/archive/2026-08-15-epic-568-510/` (issue #510 of epic 568).

**This refutes the literal "character-by-character consumption of a longer
work id" hypothesis as stated.** There is no longer identifier anywhere in
the data for a char-split to have consumed -- `"s"` and `"t"` are short,
literal placeholder `work_id` values used directly as-is. The more consistent
read of the evidence: some manifest-generation tooling (shape matches
`context_manifest.py`'s output contract) was invoked with a placeholder
`work_id` (`s`, then `t`) from *within* the (now-archived) `epic-568-510`
worktree -- `roots`/`cwd` all agree on that origin -- but its OUTPUT landed
under the *current* top-level `.worktrees/` root (i.e.
`/home/tommy/projects/constellation-skills/.worktrees/s`,
`/home/tommy/projects/constellation-skills/.worktrees/t`) rather than nested
under `epic-568-510`'s own directory tree. That is orphaned smoke-test /
verification output from a worktree that no longer exists as a live checkout,
not automatic character-splitting of a real work id.

## 2. A third, previously unnamed stray area: `.worktrees/probe`

Discovered during this sweep, not named in the original handoff's two known
leads (`s` and `t`). Same shape (`context/`+`mechanical/`, contract 1), same
root family:

```json
"run": {
  "work_id": "probe",
  "generated_at": "2026-08-15T00:30:32Z",
  "roots": {
    "skill": ".../.worktrees/epic-568-510",
    "repo": ".../.worktrees/epic-568-510",
    "durable": ".../.worktrees/epic-568-510"
  },
  "host": { "cwd": ".../.worktrees/epic-568-510", ... }
}
```

`work_id` is the literal string `"probe"` -- clearly a deliberate placeholder,
not a fragment of anything. `roots`/`cwd` point at the same now-archived
`epic-568-510` worktree as `s` and `t`. Its `generated_at`
(2026-08-15T00:30:32Z, mtime 2026-08-14 17:30 local) is later than `s`/`t`'s
(2026-08-14T16:55:31Z / 09:55 local mtime) -- so `probe` was produced by a
later invocation of whatever tooling generated all three, not the same run.

This is recorded as a new lead in the **same root-cause family** as `s`/`t`:
orphaned output from manifest-generation tooling run inside the
`epic-568-510` worktree, landing in the current top-level `.worktrees/`
instead of nested under that worktree's own directory. Who ran it, and
exactly when relative to `epic-568-510`'s own working lifetime (versus after
it was archived), remains unestablished from the evidence gathered here.
Left untouched, as instructed.

## 3. Was the sibling `-wt` layout chosen because of the Windows path limit, or arbitrarily?

The repo's own `.gitignore` (comments around the `constellation-eval-*` and
`.agent-work/**/.agent-work/` rules) document a REAL, specific prior Windows
failure:

> Captured eval workspaces embed a full copy of another checkout's skills
> tree... their nesting exceeds the Windows path limit -- `git worktree add`
> fails with 'Filename too long'... a RED-reproduction capture under a work
> area slipped past it and landed at 216 characters -- past the Windows
> limit, so every test running `git worktree add` died with exit 128
> ('Filename too long').

That incident is real and well-documented, but it is about a captured/nested
checkout landing *inside* `.agent-work/` (a second, deeply-nested copy of a
skills tree), not about the top-level choice of where the worktree ROOT
itself lives relative to the primary checkout. It explains a **different,
related defect class** -- deep nesting inside `.agent-work/` captures -- and
does not, by itself, establish that the original sibling-`-wt` convention
(worktrees living as `<repo>-wt/<work-id>`, beside rather than under the
primary checkout) was chosen *because of* the Windows path limit.

**This remains open / unresolved from written evidence.** No comment, commit
message, or design doc found during this sweep states a rationale for the
sibling-vs-nested choice itself. (Separately, m1 of this same plan computed
that switching to the new nested `.worktrees/` layout costs only +8 characters
worst-case against a 260-character MAX_PATH budget -- 132 characters of margin
-- so whatever the original reason was, it was not a hard requirement that the
nested layout as landed here would have violated.)
