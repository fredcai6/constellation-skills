# scripts.run_crew:CrewBackend
class, scripts/run_crew.py:443, 51 lines

```python
class CrewBackend
```

A pluggable crew-launch backend (Decision 1). Exactly two concrete

implementations exist — `CliBackend` and `ExternalBackend` — behind ONE
result contract (Decision 2): every backend records a durable entry
*before/at* dispatch, honors the duplicate-guard, and verifies results
exists-AND-fresh against the entry's `started_at` (the single `result_fresh`,
never forked). A backend may *dispatch* differently but may never weaken this
contract.

```python
name: str = ''
```

- [dispatch](CrewBackend.dispatch.md) method: Record the durable entry (running) BEFORE work. cli: spawn the
- [resume](CrewBackend.resume.md) method: cli: relaunch the subprocess with the stored session/handoff and
- [verify](CrewBackend.verify.md) method: Uniform across backends: exists-AND-fresh against the entry's

reads internal: CrewSpec
reads stdlib: builtins.dict x6, builtins.list x3, builtins.str x3, builtins.tuple x3, pathlib.Path x3, builtins.int x2, builtins.bool
writes internal: CrewBackend.name

referenced by: 2 sites, this module only
