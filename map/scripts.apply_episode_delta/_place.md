# scripts.apply_episode_delta:_place
function, scripts/apply_episode_delta.py:988, 9 lines

```python
def _place(tmp_path: Path, final_path: Path) -> None
```

Move one staged temp file onto its final path. A single os.replace() is atomic on

both POSIX and Windows, and the temp file is created in the SAME directory as its
destination, so this is always a same-filesystem rename rather than a copy.

A named function rather than an inlined call so a test can inject a failure at
exactly this step — the same discipline the write step's write_text_exact() seam
already made possible.

calls stdlib: os.replace
reads stdlib: os (module)

referenced by: 1 sites, this module only
