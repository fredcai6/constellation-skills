# scripts.checklist_engine:repo_revision
function, scripts/checklist_engine.py:591, 49 lines

```python
def repo_revision(base_dir: Path | None = None) -> dict
```

The repo's HEAD commit and whether its working tree is dirty relative to it

-- Tommy's doctrine-version traceability stamp (#300 g5): "practically, it's
just the repo rev number ... it could just be the current repo version in
totality for ease."

A bare commit SHA lies about a dirty tree -- that is precisely why
`context_manifest.rev()` never uses one for a per-file row. An earlier
version of this docstring argued `dirty` keeps that coarser, repo-wide SHA
honest by shipping *inside the same content field* as `commit` -- a review
disproved that (#300 g5 rework 1): two checkouts at the same commit,
delivering byte-identical declared canon, disagreed on content solely
because `git status --porcelain` is repo-wide and picked up dirt on a file
no declaration named. What to do about that was `context_manifest`'s call,
not this function's: `commit` is canon-determined (identical for any
checkout of that commit) so it is safe as manifest *content*, and `dirty`
first moved to the manifest's excluded `run` subtree and was then dropped
altogether (#327, #305 g4) -- it is repo-wide, so it reports dirt on files no
declaration names, and once a real caller made that observable the field
turned out to be neither dependably constant nor informatively varying.
Neither move reopens the honesty gap a bare SHA has -- the per-file blob OID
already answers "which bytes did this agent actually get" for a dirty,
untracked or out-of-repo file, which is the question `dirty` was protecting;
`commit` only ever had to be the coarse, human-facing traceability stamp.
This function is unaffected and still returns both fields together: it is a
general repo-facts primitive, not pre-shaped to one caller's appetite, and
its one manifest consumer simply now uses `commit` only.

Uses `_git()`, the same subprocess helper `_collect_changed_files` already
relies on for git-change-policy -- so this stays the one place in the module
that shells out for repo-level git facts, not a second ad-hoc caller.
`context_manifest.py` imports this function by name rather than reimplementing
it, which keeps that module's own "shells out to nothing" invariant
(`ProducerGuards.test_producer_shells_out_to_nothing`) literally true: no
`subprocess` identifier ever appears in its source.

Absence -- no git on PATH, `base_dir` not inside a repository, or any other
git failure -- yields `{"commit": None, "dirty": None}` rather than raising.
A revision stamp is best-effort provenance, not a precondition the caller
must satisfy first; this mirrors `read_bytes()`/`rev()`'s "absence is normal,
never raise" rule for a manifest row.

calls internal: _git x2
calls stdlib: builtins.bool
unresolved: 2 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
