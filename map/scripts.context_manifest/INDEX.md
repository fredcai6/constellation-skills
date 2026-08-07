# scripts.context_manifest
scripts/context_manifest.py, 462 lines

Deterministic projection substrate: what was made available to an agent, and at

which revision.

The manifest this module produces is a record of **delivery, not use**. It says
"these files, in this order, at these revisions, were made available to the agent
running this step." It is deliberately *not* an access trace, not transcript
analysis, and not an archive of file contents — a design that widens toward
proving *use* is a different artifact, not a better version of this one.

Three properties carry the whole design:

1. **Revision identity is the git blob OID of the LF-normalised bytes**, computed
   in-process (`rev`). No `git` subprocess, and deliberately **no commit SHA**: a
   commit SHA lies about a dirty tree and says nothing at all about untracked or
   gitignored files. One function covers tracked, dirty, untracked, gitignored and
   out-of-repo files with no case analysis, and it structurally eliminates CRLF —
   this corpus's largest named irreproducibility source — rather than excluding it.
   Beside every per-file row sits one repo-level, coarser fact in content,
   `repo_rev: {commit}` — *which commit is canon versioned at* (Tommy's
   doctrine-version stamp, #300 g5). `commit` alone is safe as content because it
   is **canon-determined**: identical in any checkout of that commit, anywhere, so
   two environments delivering the same declared bytes always agree on it.
   The `repo_state` edge also returns `dirty` — *is that commit's tree honest
   right now* — and this module **drops it on the floor**. It is not merely
   excluded from content; no manifest carries it at all any more (#327, #305 g4).
   It reached the manifest first as content and then, when `git status
   --porcelain`'s repo-wide reach was shown to make two environments delivering
   byte-identical canon disagree, in the excluded `run` subtree (#300 g5 rework
   1). Removal is what a real producing caller finally made visible: `dirty` is
   repo-wide, so it reports dirt on files no declaration names — dominated, once
   the manifest itself is written under a tracked `.agent-work/`, by the run's own
   bookkeeping — and it is computed BEFORE the manifest is written, so it never
   reads its own side effect but its predecessor's. Measured **on the tree
   this removal was made on**, across the 49 manifests this producer had
   actually written here: 47 `true`, 1 `false`, 1 field-absent — and the lone
   `false` was written 2m16s after a commit cleaned the tree, so it is the
   read-your-predecessor mechanism in miniature rather than an exception to it.
   **Both sides are given in full because the count is pinned to that moment
   deliberately and keeps growing as this producer runs**: 49 / 47 / 1 / 1
   immediately before the removal, 56 / 51 / 1 / 4 at the removal commit
   itself — measured at `35d2686^` and `35d2686` on `epic-298/305`, landed as
   #389. The squash-merge carries neither SHA into `main`, so the SHAs settle
   this on the branch and `#389` settles it afterwards. So a reader can neither
   rely on a constant nor extract a signal from a varying one — both readings
   are unavailable, which is why the field
   went rather than being re-placed a third time. Content loses nothing: it
   already carries the per-file blob OID as the precise "which bytes did this
   agent actually get" answer for a dirty, untracked or out-of-repo file, and
   per-declared-file dirtiness stays derivable from content alone by comparing
   each row's `rev` against `git rev-parse <commit>:<path>` — scoped to the
   declared set, which is strictly better than a repo-wide flag. `repo_rev.commit`
   only has to be the coarse, human-facing traceability stamp. Computed by
   `checklist_engine.repo_revision()` — a real `git` subprocess, deliberately
   kept **out of this module's own source** so the guarantee above (no `git`
   subprocess **in this file**) stays literally true.
2. **Declaration order is content.** There are no globs, no directory patterns and
   no directory enumeration anywhere in this module, and paths are never sorted.
   A glob would import filesystem ordering — the second named irreproducibility
   source — into the record for no benefit. Doctrine has reading precedence
   (inherited global doctrine, *then* project deltas), so the declared order is
   part of what is being recorded.
3. **`/run` is the entire exclusion set.** Every legitimately-varying fact —
   timestamps, run ids, absolute roots, host facts — lives in the `run` subtree and
   nowhere else. Determinism is therefore checked by comparing everything outside
   one JSON pointer.

   The mechanism that keeps that claim true is that `content()` **admits** the keys
   in `CONTENT_KEYS` rather than **denying** `run`. Denial was the obvious spelling
   and it is the wrong one: it makes every future key content by default, so a new
   varying field becomes "accidentally content" merely by being added, silently.
   Admission inverts the default — a new key is excluded until someone edits
   `CONTENT_KEYS`, and that edit fails
   `ManifestEnvelope::test_the_envelope_is_exactly_the_content_allowlist_plus_run`
   until the envelope and the allow-list are made to agree deliberately.

There are now two injected impure edges, mirroring each other: `reader` for file
bytes, and `repo_state` for the repo-level `repo_rev` fact. Each is what lets a
test point the whole producer at a fixture tree (or a fixed `{commit, dirty}`)
without touching the real filesystem or a real git process.

There is intentionally **no CLI verb** here: the manifest is a JSON file, and a
verb would touch the engine's persistence control flow for a convenience print.

imports stdlib: __future__.annotations, datetime.datetime, datetime.timezone, hashlib, json, os, pathlib.Path, pathlib.PurePosixPath, platform, sys, typing.Any, typing.Callable, typing.Mapping, typing.Sequence
imports third-party: checklist_engine.active_id, checklist_engine.repo_revision
imported by: none found

```python
_MANIFEST_CONTRACT_VERSION = 1
DECLARATION_KEY = 'context_refs'
ROOT_TOKENS = ('skill', 'repo', 'durable')
CONTENT_KEYS = ('contract', 'step', 'files', 'repo_rev')
```

- [rev](rev.md) function: Git blob OID of `data` after LF normalisation.
- [DeclarationError](DeclarationError.md) class: A `context_refs` entry is malformed, names an unknown root, or escapes it.
- [read_bytes](read_bytes.md) function: Read `abs_path`, or return None if it does not exist.
- [resolve](resolve.md) function: Absolute filesystem path for one declaration entry.
- [declaration_of](declaration_of.md) function: The task's ordered `context_refs`, or an empty tuple.
- [rows](rows.md) function: One `{root, path, rev}` row per declared entry, in declaration order.
- [default_repo_state](default_repo_state.md) function: The real, git-backed implementation of the `repo_state` impure edge.
- [run_facts](run_facts.md) function: The `/run` subtree: every legitimately-varying fact, and nothing else.
- [build_manifest](build_manifest.md) function: The one envelope, for the checklist's active step.
- [content](content.md) function: The part of the manifest that must be identical across environments.
- [encode](encode.md) function: The one canonical encoder. No second encoder, no stored digest to disagree
- [manifest_path](manifest_path.md) function: `<agent_work_root>/<work-id>/context/<step>.json` — named for this
- [write_manifest](write_manifest.md) function: Write the manifest with LF line endings, always.
- [produce](produce.md) function: Build the active step's manifest and write it. Returns `(path, manifest)`.
