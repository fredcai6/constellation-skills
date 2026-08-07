# scripts.run_skill_eval:_write_meta
function, scripts/run_skill_eval.py:939, 22 lines

```python
def _write_meta(run_dir: Path, payload: dict) -> None
```

Write `<run-dir>/meta.json`. Called twice per run (a launch record at spawn,

the final classification at end) so a run that is tree-killed mid-flight still
leaves a diagnosable meta.json instead of nothing.

Written ATOMICALLY (#205): a direct write_text can be killed mid-write/flush
and leave a truncated/corrupt meta.json behind. Instead, write to a temp file
in the SAME directory as meta.json (so os.replace is an atomic same-filesystem
rename on both POSIX and Windows), then replace the real path in one step. On
any write failure, clean up the temp file so a failed attempt leaves no stray
`.tmp` file behind.

calls stdlib: json.dumps, os.fdopen, os.replace, pathlib.Path, tempfile.mkstemp
reads stdlib: os (module) x2, builtins.BaseException, json (module), tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only
