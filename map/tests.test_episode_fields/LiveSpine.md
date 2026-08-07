# tests.test_episode_fields:LiveSpine
class, tests/test_episode_fields.py:268, 62 lines

```python
class LiveSpine
```

A real spine on disk, driven through the engine's own CLI.

These fields are read out of state the engine WROTE — a journal line, an evidence
item, a manifest's bytes — so exercising them through the Python API would prove
the wrong thing. Every mutation below goes through `checklist_engine.py` as a
subprocess, exactly as an agent drives it.

```python
SESSION = 'sess-live'
```

- [__init__](LiveSpine.__init__.md) method: HOLE: no docstring
- [run](LiveSpine.run.md) method: HOLE: no docstring
- [verb](LiveSpine.verb.md) method: HOLE: no docstring
- [complete](LiveSpine.complete.md) method: HOLE: no docstring
- [load](LiveSpine.load.md) method: HOLE: no docstring
- [fields](LiveSpine.fields.md) method: HOLE: no docstring

reads stdlib: pathlib.Path
writes internal: LiveSpine.SESSION

referenced by: 9 sites, this module only
