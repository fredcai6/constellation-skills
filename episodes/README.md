# episodes/

This directory is the **durable episode store** — a durable, deterministically-findable
record of structured observations captured across Constellation runs. Full grammar,
partition, retirement policy, and Stratum A mapping: **`docs/EPISODE_STORE.md`**.

## Why this directory exists, and why it is here

The store must **outlive** the run that captures it, and its whole purpose is to stay
findable across sessions and worktrees so a later rhyme-detection pass (issue #308) can
find neighbours of a new episode months later. That only works if the store is **tracked
in git** at a path with no durability plumbing of its own: `episodes/` is a plain repo-root
directory, tracked like any other, so the moment a commit lands the store is visible in
every worktree, every clone, and every later checkout, with nothing to configure and
nothing to resolve at runtime. A store whose location has to be computed — from a lease, a
work-id, or which worktree happens to be current — is a store that can be written to the
wrong place while every gate still reports green. See `docs/EPISODE_STORE.md` § "Why a
tracked path" for the full argument.

## What lives here

**Two subdirectories, and no episode files at this level.** Every episode is one Markdown
file named `<episode-id>.md` (see `docs/EPISODE_STORE.md` for the id grammar and the full
record shape), and it lives in exactly one of:

- **`active/`** — the ordinary rhyme-search set. New episodes are written here.
- **`retired/`** — the archive. Retiring an episode **moves its file** here; the content
  is retained in full, never deleted or truncated.

Which directory a file is in *is* its membership — a filesystem fact rather than a parsed
field, so no `status` line can be malformed, hand-edited, or forged into changing it. The
layout was ratified on 2026-08-01 (`docs/EPISODE_STORE.md` §7):

> "move the file, prefer to keep files clean of history unless they're historical.
> archives are available strats."

**`retired/` is an archive, not a second live search space.** Ordinary retrieval globs
`active/` and never looks at `retired/`; reaching into the archive is a separate,
deliberate act (`--include-retired`, or a `fetch` by id — an addressed lookup by name is
not a search, so a `consolidated-into:` / `superseded-by:` cross-reference never dangles
when its target is retired).

## What counts as an episode, and what does not

**Inside `active/` and `retired/`, every Markdown file IS an episode.** Membership is the
directory, so a directory listing there is a list of records — and the store decides
whether a file is a record from its **own id grammar** (`<kebab-case-run>-NNN.md`,
`episode_id_for()` in `scripts/apply_episode_delta.py`), never from a list of filenames
somebody maintains by hand. A `.md` name the grammar does not recognize is **refused as
malformed**, not skipped: skipping is how a filename becomes a phantom episode id, and
how a real record becomes invisible.

That is why the two subdirectories are kept alive by a **`.gitkeep`** rather than a
`README.md`. Git does not track empty directories, so each needs a tracked file or the
layout vanishes at commit — but a `README.md` inside `active/` is not a well-formed
episode filename, and the first attempt at this layout shipped exactly that and minted
the phantom id `README` in both directories, making the whole store unreadable by its own
tooling. A placeholder that is not a `.md` file cannot be mistaken for a record.

**A file at THIS level, alongside this README, is malformed** — it belongs to neither set,
so every enumeration would silently omit it. `scripts/apply_episode_delta.py` refuses
rather than skipping it. This `README.md` is the one exception, excluded by name through
that script's `NON_EPISODE_FILENAMES` allowlist — never by a glob that happens not to
match it. The allowlist is scoped to this flat root and nowhere else.

**A missing directory is refused, not answered.** `active/` or `retired/` absent (a
typo'd `--store-root`, a layout that never got committed) fails visibly rather than
enumerating to zero episodes with exit 0, which would read exactly like an empty store.

## What does NOT live here

- **Nothing hand-edited.** `scripts/apply_episode_delta.py` is the only write path — a
  validated, all-or-nothing delta writer: it checks the whole delta before it touches the
  store, and either every operation lands or none does.
- **No consolidation / rhyme-search** (issue #308) — downstream of this store, not part of
  it.
- **No rules.** An episode records what was observed, and nothing here is read back as an
  instruction. A rule for a future agent to follow belongs in `docs/agents/*` and is a
  human's call — see `docs/agents/ORCHESTRATOR_CONTEXT.md` § "The Retired Learning
  Playbook".
