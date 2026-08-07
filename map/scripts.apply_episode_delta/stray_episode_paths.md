# scripts.apply_episode_delta:stray_episode_paths
function, scripts/apply_episode_delta.py:553, 33 lines

```python
def stray_episode_paths(root: Path) -> list[Path]
```

Every Markdown file sitting at the store's FLAT root — i.e. in neither active/

nor retired/ — that is not one of the store's known non-episode files.

Trap 3 (see the seam-block header). Under the bound layout an episode is a member of
exactly one of two directories; a file at `episodes/<id>.md` is a member of neither,
so BOTH the ordinary and the history-inclusive enumerations would return an answer
that silently excludes it. That is the same silent-omission class the flat layout
had, wearing a migration's clothes: a pre-layout episode left behind by a partial
migration reads, to every query, as though it does not exist.

So it is surfaced rather than skipped — and the exclusion of the store's own
documentation is a NAMED allowlist (NON_EPISODE_FILENAMES), never a glob shape that
happens not to match it. The allowlist lives HERE and only here: inside the layout
directories the id grammar answers the same question without anyone maintaining a
list (episode_id_for).

Recursive, and the allowlist applies at the flat root ONLY (trap 6). A Markdown file
at `episodes/archive/<id>.md` is exactly as invisible to every one-level-deep scan as
one at the flat path, and "a directory nobody declared" is not a safer place to hide
a record than "the level above". Files inside active/ and retired/ are excluded here
because _layout_episode_ids() scans those two with its own, stricter rule.

calls stdlib: builtins.any, builtins.sorted
reads internal: ACTIVE_DIR, NON_EPISODE_FILENAMES, RETIRED_DIR
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
