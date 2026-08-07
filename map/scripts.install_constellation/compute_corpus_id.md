# scripts.install_constellation:compute_corpus_id
function, scripts/install_constellation.py:995, 40 lines

```python
def compute_corpus_id(skills_dir, names: Iterable[str] | None = None) -> str
```

Content id of an installed skill tree: ``"sha256:" + sha256`` over the

sorted ``(rel_posix_path, _hash_file(p))`` pairs of every file. PURE.

``names`` restricts the hash to those top-level subdirectories (the skills a
given install actually wrote), so foreign siblings already present in a shared
skills root — a user's own skills under ``~/.claude/skills`` — never perturb
the constellation corpus id. ``None`` hashes the whole tree, which is what the
eval harness wants for its clean temp_install. The marker file itself is always
excluded so writing it cannot change the id it records.

calls internal: _hash_file
calls stdlib: builtins.sorted x2, hashlib.sha256, pathlib.Path
reads internal: CORPUS_MARKER
reads stdlib: builtins.str x2, builtins.list, builtins.tuple, hashlib (module)
writes internal: compute_corpus_id.skills_dir
unresolved: 13 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
