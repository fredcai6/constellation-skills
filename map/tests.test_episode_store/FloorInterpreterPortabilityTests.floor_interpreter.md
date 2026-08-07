# tests.test_episode_store:FloorInterpreterPortabilityTests.floor_interpreter
method, tests/test_episode_store.py:2821, 40 lines

```python
def floor_interpreter(self)
```

A launcher that really is the declared floor version, or None.

Every candidate is ACCEPTED ONLY IF it reports the floor version when asked, so
bare launcher names are safe to probe — the version check, not the name, is what
makes the answer trustworthy. That matters here: on this host `py` is not the
Windows launcher but a shim pointing straight at a 3.12 runtime, and it rejects
the `-3.12` selector outright. A candidate list that assumed the selector worked
found nothing and skipped, which is the failure mode this whole class exists to
prevent — a guard that silently never runs is worse than no guard, because it
reads as coverage.

calls internal: load
calls stdlib: os.environ.get, subprocess.run
reads stdlib: subprocess (module) x2, builtins.OSError, os (module), os.environ, subprocess.SubprocessError
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
