# Triage candidate: `_atomic_write_json`'s fixed temp name corrupts under two writers

- **Disposition:** `recommend-and-defer`. Not filed (`decision:no-issue-filing`). **Not
  fixed: `scripts/hooks/*` is out of scope for epic #567 lane A**, and hooks execute
  from the main checkout for every live session, so editing one mid-wave can break
  other running agents.
- **Raised by:** `cmdr-567-a` at `600de020`. Found by this lane's cold plan critic while
  reviewing a handoff that had mandated this pattern for reuse.
- **Severity:** high where two writers are possible, and it is presented as the repo's
  canonical atomic write, so it invites exactly that reuse.

## The defect

`scripts/hooks/gauge_writer_hook.py:513`:

```python
def _atomic_write_json(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")      # <-- FIXED name, one per target
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(record, f)
    os.replace(tmp, path)  # atomic on POSIX and Windows alike
```

The temp name is a pure function of the target path, so **two concurrent writers of one
target share one temp file.** The sequence that corrupts:

1. Writer A and writer B both open the same `<target>.tmp`.
2. A finishes and calls `os.replace`, installing that inode as the live target.
3. B's file handle **still points at that inode** — which is now the live file. B's
   buffered flush writes straight into the live target, *after* the rename, bypassing
   atomicity entirely.
4. B's own `os.replace` then raises `FileNotFoundError`, because the temp path it
   expects was renamed away.

Measured by running the pattern with two writers on one path:

```
installed: b'{"a": "S"}LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"}'
parses: NO -> JSONDecodeError Extra data: line 1 column 11 (char 10)
errors: ["FileNotFoundError: [Errno 2] No such file or directory: 'probe2.json.tmp' -> 'probe2.json'"]
```

## Why this is worse than no atomic write at all

A bare `write_bytes` tear is **transient** — the next successful write heals it. An
**installed** unparseable document is **permanent**, and it is installed by the
mechanism whose whole purpose is to prevent that.

So in the two-writer case this function is a regression against the naive
implementation it replaced, while reading as the safe choice.

## Two further gaps in the same function

- **No `fsync` before the rename.** `os.replace` can be durable before the data is, so
  the crash-safety half of "atomic write" is not actually delivered. A crash can leave
  a rename pointing at unwritten or partially written blocks.
- **File mode is lost.** A fresh temp gets default permissions and the rename carries
  them onto the target, so an existing file's mode is silently replaced.

## Recommended fix

```python
fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
try:
    if path.exists():
        os.fchmod(fd, path.stat().st_mode & 0o7777)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(record, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
finally:
    if os.path.exists(tmp):
        os.unlink(tmp)
```

`mkstemp` gives a **unique** name per writer, so no two writers ever share a temp
inode. Everything else is unchanged in shape.

## Why it matters beyond this one hook

`grep -rn` for atomicity claims across `scripts/ tests/ docs/` returns 13 files, and
this function is the one a reader naturally treats as the house pattern — it is the
cleanest instance, it carries the confident comment "atomic on POSIX and Windows
alike", and it is the one lane A's own handoff told an implementer to mirror by name.
**A defective canonical pattern propagates by being canonical.** Lane A caught it only
because a cold critic actually ran the pattern instead of reading it.

Worth checking the same property in the neighbours before closing this out:

- `scripts/hooks/spine_rail.py:369` `_replace_binding_atomically` — described as using
  a **unique**-temp atomic replace, so it is probably already correct; confirm.
- `scripts/apply_episode_delta.py:1201` — "A single `os.replace()` is atomic on ...";
  check whether its temp name is unique per writer.
- `scripts/run_skill_eval.py:970` — writes a temp in the same directory as `meta.json`;
  same question.

## Related

Lane A's own `checklist_engine.save()` fix (#613's atomicity half) deliberately does
**not** copy this pattern, for exactly this reason. Its implementation is the
recommended fix above and can be lifted directly if this candidate is taken up.
