# scripts.checklist_engine:EngineError
class, scripts/checklist_engine.py:103, 32 lines

```python
class EngineError(Exception)
```

A refusal: the requested transition is not allowed. No exit-0.

Optional structured attributes (#227 gate g3) let the CLI boundary
(`main()`, via `recovery_for()`) compose a recovery line WITHOUT
re-parsing the message string -- the verb functions that raise stay pure
(their message text is unchanged); they just also hand the boundary the
facts it needs:
  - `task_id` / `verb`: which task, and which attempted verb, refused.
  - `status`: the task's ACTUAL status at refusal time (a status-caused
    refusal -- start/advance/resume/reopen each require one).
  - `unmet`: the REAL unmet condition ids from a live check inside the
    verb (`start`'s preconditions, `advance`'s postconditions), each as
    {"id", "which", "kind"}. A command/git-change-policy kind's pass/fail
    is only known HERE, at the moment the check ran -- `state()` must
    never re-derive it (INV-2 purity), so this is genuinely a fact only
    the exception carries.
  - `valid_ids`: every real p*/c* id on the task, for an unknown-cond-id
    refusal on `attest` (a malformed-argument refusal, a 4th axis
    outside the (status, verb) grid -- see `recovery_for`).
None of these are read anywhere except `recovery_for` at the CLI
boundary; a caller that never inspects them (most of the existing test
suite, which raises/asserts EngineError by message text) is unaffected.

- [__init__](EngineError.__init__.md) method: HOLE: no docstring

referenced by: 80 sites, this module only
