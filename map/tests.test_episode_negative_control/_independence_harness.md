# tests.test_episode_negative_control:_independence_harness
function, tests/test_episode_negative_control.py:219, 67 lines

```python
@contextlib.contextmanager
def _independence_harness()
```

Make every producer under test UNCALLABLE, and the emitted snapshot UNREADABLE.

Independence proven by execution rather than by declaration. Inside this block the
oracle either builds its expectation from its own tallies and the manifest file, or
it raises — there is no third outcome, and no description string is consulted to
decide which happened.

File reads are guarded rather than the whole filesystem blocked, because the oracle
legitimately reads ONE file: the context manifest whose own bytes it pins. What it
may not read is anything under a `mechanical/` directory — that is the seam's
emitted snapshot, which is the reading under test wearing a different hat.

- [patch](_independence_harness.patch.md) method: HOLE: no docstring
- [raiser](_independence_harness.raiser.md) method: HOLE: no docstring
- [guard](_independence_harness.guard.md) method: HOLE: no docstring
- [guarded_open](_independence_harness.guarded_open.md) method: HOLE: no docstring
- [guarded_read_text](_independence_harness.guarded_read_text.md) method: HOLE: no docstring
- [guarded_read_bytes](_independence_harness.guarded_read_bytes.md) method: HOLE: no docstring

calls stdlib: builtins.reversed
reads internal: _ControlRun x2, FORBIDDEN_PRODUCERS
reads stdlib: builtins.object x4, pathlib.Path x4, builtins.str x3, builtins (module) x2, builtins.list, builtins.open, builtins.tuple, io (module), pathlib.Path.read_bytes, pathlib.Path.read_text
unresolved: 1 calls (dynamic), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
