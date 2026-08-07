# tests.test_episode_store:SeparateProcessMixin
class, tests/test_episode_store.py:1169, 49 lines

```python
class SeparateProcessMixin
```

Launch a real, separately-booted Python interpreter and observe its OS pid.

subprocess + sys.executable is the whole point: issue #301's acceptance criterion is
that a seeded episode is retrievable ACROSS SESSIONS, and a test that calls a
function twice in one interpreter has not crossed a session boundary — it has
proved that a warm module still holds the value it was just handed. Every child
below is started with Popen so the PARENT observes each child's pid directly, and
the query child reports its own os.getpid() back inside its JSON answer, so the
answer can be tied to the process that produced it rather than assumed.

```python
CHILD_TIMEOUT = 120
```

- [run_in_separate_process](SeparateProcessMixin.run_in_separate_process.md) method: HOLE: no docstring
- [seed_in_separate_process](SeparateProcessMixin.seed_in_separate_process.md) method: HOLE: no docstring

writes internal: SeparateProcessMixin.CHILD_TIMEOUT

referenced by: none found
