# scripts.run_skill_eval:stable_corpus_id
function, scripts/run_skill_eval.py:493, 40 lines

```python
def stable_corpus_id(skills_dir, install_root, names=None) -> str
```

Install-path-invariant corpus id. Mirrors `_install.compute_corpus_id`'s file

selection (sorted `rglob`, skip `CORPUS_MARKER` / `.pyc` / `__pycache__`) and its
`"sha256:" + sha256` over sorted `(rel_posix, file_hash)` pairs EXACTLY — only the
per-file bytes are normalized, so the id FORMAT is unchanged.

`skills_dir` is the tree to hash; `install_root` is the ORIGINAL install root whose
posix string was baked into the files (the ANCHOR). The two DIFFER at the assert
site, where the tree is a COPY of an `install_root`-rooted corpus — see the ANCHOR
RULE above. The needle is built from `install_root.as_posix()` (forward slashes,
matching how the installer baked it via `target.as_posix()`); `str(install_root)`
would use backslashes on Windows and silently no-op.

calls internal: _hash_normalized_file
calls stdlib: builtins.sorted x2, pathlib.Path x2, hashlib.sha256
reads internal: CORPUS_MARKER
reads stdlib: builtins.str x2, builtins.list, builtins.tuple, hashlib (module)
writes internal: stable_corpus_id.skills_dir
unresolved: 14 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only
