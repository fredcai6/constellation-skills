# tests.test_episode_store:FloorInterpreterPortabilityTests
class, tests/test_episode_store.py:2790, 126 lines

```python
class FloorInterpreterPortabilityTests(TestCase)
```

The store must run on the OLDEST interpreter it claims to support, not merely on

whatever the author happened to launch.

Why this class exists. PR #320 went green locally on Python 3.14 and RED in CI on
3.12: 39 failures from one root cause, `Path.read_text(newline="")`, a kwarg pathlib
only gained in 3.13. The local suite could not have caught it, because the local
interpreter was two minor versions AHEAD of CI — so "green here" was never evidence
for "green there", and nothing said so out loud.

The sting is that the skew came from following advice. Issue #313 documents that
`py -m pytest` false-reds on this host (no pytest installed for it), which routes
agents onto `python`. Here `python` is 3.14 and `py` is 3.12 — the CI version. The
documented false-red and this false-green are the same underlying problem, two
interpreters that are not the same environment, and the guidance is wrong in both
directions.

A CI matrix entry would not have helped: CI already ran the floor and already caught
it. What was missing was a LOCAL check, so this drives the store on the floor
interpreter in a real subprocess. It SKIPS rather than fails when no floor
interpreter is discoverable, so it is a safety net and not a new environment
requirement.

Stated honestly, because a guard whose reach is overclaimed is worse than none. On CI
the running interpreter IS the floor, so the round trip below genuinely exercises it
(and `["python"]` resolves on the first try). On a developer host it runs only if a
launcher name resolves to the floor or `EPISODE_STORE_FLOOR_PYTHON` points at one;
otherwise it skips and the drift test below is the only protection left. So this
class does not make local green equal CI green — it narrows the gap and names it.

- [floor_interpreter](FloorInterpreterPortabilityTests.floor_interpreter.md) method: A launcher that really is the declared floor version, or None.
- [test_the_declared_floor_matches_the_version_ci_actually_pins](FloorInterpreterPortabilityTests.test_the_declared_floor_matches_the_version_ci_actually_pins.md) method: HOLE: no docstring
- [test_the_store_actually_runs_on_the_floor_interpreter](FloorInterpreterPortabilityTests.test_the_store_actually_runs_on_the_floor_interpreter.md) method: HOLE: no docstring

referenced by: none found
