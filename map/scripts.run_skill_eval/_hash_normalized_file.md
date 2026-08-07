# scripts.run_skill_eval:_hash_normalized_file
function, scripts/run_skill_eval.py:480, 11 lines

```python
def _hash_normalized_file(path: Path, needle: str) -> str
```

sha256 hexdigest of a file's TEXT with `needle` (the install root's posix

string) replaced by a fixed sentinel, so the baked absolute install path does not
perturb the digest. Undecodable/binary files (which carry no baked text path) fall
back to the raw-bytes `_hash_file`, keeping them stable and format-identical.

calls internal: _hash_file
calls stdlib: hashlib.sha256
reads internal: CORPUS_ROOT_SENTINEL
reads stdlib: builtins.OSError, builtins.UnicodeDecodeError, hashlib (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
