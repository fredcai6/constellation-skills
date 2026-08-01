# episodes/

This directory is the **durable episode store** — a durable, deterministically-findable
record of structured observations captured across Constellation runs. Full grammar,
partition, retirement policy, and Stratum A mapping: **`docs/EPISODE_STORE.md`**.

## Why this directory exists, and why it is here

The store must **outlive** the run that captures it, and its whole purpose is to stay
findable across sessions and worktrees so a later rhyme-detection pass (issue #308) can
find neighbours of a new episode months later. That only works if the store is **tracked
in git**: `.agent-work/` is gitignored (see `.gitignore` line 1) and nothing under it
survives a `git worktree remove` or a fresh clone. `episodes/` is a plain repo-root
directory, tracked like any other, so a commit here is visible in every worktree, every
clone, and every later checkout — no special durability plumbing required. See
`docs/EPISODE_STORE.md` § "Why a tracked path" for the full argument.

## What lives here

One Markdown file per episode, named `<episode-id>.md` (see `docs/EPISODE_STORE.md` for
the id grammar and the full record shape). This file (`README.md`) is the one tracked
file that makes the directory itself survive in git even before the first episode is
captured — git does not track empty directories.

## What does NOT live here yet

- **No writer script ships in this gate.** Mutation of episode files goes through a
  future validated, all-or-nothing delta script (`scripts/apply_episode_delta.py`,
  gate g2) that mirrors `scripts/apply_lessons_delta.py`'s contract. Nothing in this
  directory should be hand-edited once that script exists.
- **No retrieval script ships in this gate** (gate g3).
- **No automated capture wiring** (issue #305) and **no consolidation / rhyme-search**
  (issue #308) — both are downstream of this store, not part of it.

## Not to be confused with

`.agent-work/LESSONS.md` — a live, curated, human-facing playbook of open problems,
deliberately transitory ("where lessons pass through, not where they live"). This store
is the opposite: a raw, append-mostly, machine-consumed capture that is meant to outlive
its own consolidation. The two systems are siblings, not the same thing, and this run
does not touch `LESSONS.md` or its writer.
