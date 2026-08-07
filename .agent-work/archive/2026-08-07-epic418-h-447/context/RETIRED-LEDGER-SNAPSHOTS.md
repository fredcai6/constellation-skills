# The two ledger snapshots this run read from, and why they are not here

This run staged read-only copies of `.agent-work/LESSONS.md` (140 lines, 8 active lessons) and
`.agent-work/AGENT_FEEDBACK.md` (2119 lines) as they stood on `main` at **`861ecbe`**, because
this worktree is based on `cbd9aee` and its copies were stale by two lessons. The crews at g4 read
those snapshots, not the worktree copies.

They are **deliberately not committed.** #447 retires both files; committing verbatim copies into the
archive would re-introduce the retired content under a path the deny-globs do not literally match,
which is a weaker version of the thing being retired. The content is not lost:

- **Both files at their final revision:** `git show 861ecbe:.agent-work/LESSONS.md` and
  `git show 861ecbe:.agent-work/AGENT_FEEDBACK.md`.
- **The eight live lessons, carried:** `episodes/active/issue-447-001.md` .. `008.md`, each
  carrying `- artifact-ref: lesson:<slug>` back to the lesson it came from.
- **AGENT_FEEDBACK.md was dropped with reason,** not migrated: synthesising typed assertions from
  unstructured prose retrospectives is the fabrication the store's own doctrine forbids.
