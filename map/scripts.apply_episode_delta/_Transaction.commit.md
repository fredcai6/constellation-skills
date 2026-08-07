# scripts.apply_episode_delta:_Transaction.commit
method, scripts/apply_episode_delta.py:1063, 75 lines

```python
def commit(self) -> None
```

REWORK (g2 review BLOCK, defect 2): stage every touched file to a temp

path FIRST, and only move a temp file into its final place once every
staged write has succeeded. The old version called path.write_text()
directly on each final path in sequence — a real OS-level failure (disk
full, permission denied, a locked file) on, say, the 2nd of 2 touched files
left the 1st file's write landed on disk while the delta as a whole still
failed, contradicting this module's own all-or-nothing claim. Staging
closes that gap for the WRITE step: if any staged write raises, every temp
file already written is removed and no final path is ever touched.

The temp file lives NEXT TO its final path (same directory, so same store
root, same filesystem) so the move below is a same-filesystem rename, never
a cross-filesystem copy.

g4 (C6, half-retirement). Binding Option A gave the placement phase a SECOND
step — a retirement both writes `retired/<id>.md` and removes `active/<id>.md` —
and a failure between those two steps would leave the id present in BOTH
directories: retired by content, still in the ordinary-search set by directory.
That is precisely the half-retired store the gate must rule out, and the old
placement loop had no answer for it (it removed sources in an unguarded loop
after an unguarded replace loop).

So the placement phase now snapshots the prior bytes of every path it is about
to overwrite or remove, and on ANY failure restores all of them and deletes the
paths it newly created. A failed retirement therefore ends with the episode
wholly un-retired — active/<id>.md back with its original bytes, no
retired/<id>.md — rather than half of each. The compensating restore is
deliberately not silent: if it fails too, that exception propagates.

Honest limit, unchanged in kind: this is compensation, not atomicity. A hard
process kill or power loss BETWEEN two of these calls runs no compensation at
all, and nothing in EPISODE_STORE.md's markdown-in-git constraint provides a
journal/WAL to close that. What is closed is every failure the process itself
survives to observe — an OSError from a locked file, a permission denial, a full
disk — which is the class this store can actually defend against. The residue
that remains is made LOUD at every seam that could meet it: the enumeration seam
for scanning readers, resolve_episode_path() for fetch-by-id, and apply_delta()'s
own pre-flight scan for every write op — not only the ops that scan anyway.

calls internal: _Transaction.write_plan, _place, _remove_superseded, write_text_exact
calls stdlib: builtins.list, builtins.sorted, uuid.uuid4
reads stdlib: pathlib.Path x3, builtins.Exception x2, builtins.bytes, builtins.dict, builtins.list, builtins.tuple, uuid (module)
unresolved: 11 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
