# Findings — `epic-568-530` archive resume

Dispatch: `LAUNCH_ORDER-wave2-archive-530.md` · session
`constellation/epic-568-530/archive/commander/attempt-1`

## F1 — the MCP door was bound correctly this time (carried finding, now closed)

`FINDINGS-wave2-repair.md` F1 recorded that the predecessor's door resolved to a foreign scratch
spine (`scratch-mcp-424`) and could not be redirected. This dispatch launched through the `cli`
backend with `--spine`, and `spine_status` resolved to **`epic-568-530`**: the lease it reported was
`constellation/epic-568-530`, and its digest named episode `epic-568-530-001`. No foreign-spine
mutation risk in this session. The `--spine` binding is the fix that worked; record it as the
launch shape for resumed spines.

## F2 — this run's work-area records cannot reach history, and that is not fixable from here (FLOAT)

`.agent-work/` is tracked in this repo on purpose — `.gitignore` opens by saying so, and 8345 files
under `.agent-work/` are tracked, including prior archived work areas such as
`.agent-work/archive/2026-07-08-issue-58/`. This run's work area was never tracked: it has been
untracked (`?? .agent-work/epic-568-530/`) at every point, including through publication.

It cannot be corrected in this lane:

- PR #580 was **squash**-merged, so nothing committed to `epic-568/530-binding` now can reach `main`
  through it.
- Pre-ruling 1 (`decision:publication-is-done`) forbids pushing, opening, or modifying a PR, so a
  second publication path is not mine to open.
- Committing the archive locally would also make postcondition `c2` ("branch committed and pushed")
  false, forcing either a forbidden push or a false attestation.

So the archived work area at `.agent-work/archive/2026-08-14-epic-568-530/` stays local to this
worktree and dies with it. **The durable record survives regardless**: episode
`epic-568-530-001` is tracked and present on `origin/main` (verified with `git cat-file -e
origin/main:episodes/active/epic-568-530-001.md`), which is exactly the property the archive
imperative calls load-bearing.

**Floated to the Admiral**, who holds the publication class: if this run's work-area records are
wanted in history, they must be committed on a follow-up branch by someone who may publish. I have
not done it and have not worked around it.

## F3 — the work-area move must follow the release, not precede it

The archive imperative orders the move of `.agent-work/<slug>/` before closeout, but `SPINE_FILE` is
an absolute path into that directory. Moving it while the spine is live breaks the MCP door mid-gate,
leaving no way to `advance` or `release`. Postcondition `c1` does not depend on the work-area path —
its command only verifies episode capture under `episodes/` — so the move is safe to perform after
the release, and only then. A filesystem move is not a journaled action, so doing it last does not
disturb the release-is-last provenance rule. Worth folding into the archive imperative's wording.
