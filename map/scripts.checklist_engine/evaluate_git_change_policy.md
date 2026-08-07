# scripts.checklist_engine:evaluate_git_change_policy
function, scripts/checklist_engine.py:540, 42 lines

```python
def evaluate_git_change_policy(files: list[dict], policy: dict) -> list[str]
```

PURE policy evaluation. Returns a list of human-readable violations

(empty == satisfied). `files` is a list of dicts:
`{"path": str, "size": int, "binary": bool}`. No git, no filesystem — this
is the fully unit-testable core.

A file VIOLATES if:
  - it matches any `deny_globs` entry (an explicit deny ALWAYS denies — it
    beats an allow); OR
  - its size exceeds `max_file_bytes`; OR
  - it is binary and `require_human_waiver_for_binary` is true,
UNLESS the path matches an `allow_globs` entry, which exempts it from the
SIZE and BINARY checks only (deny still denies). Empty/missing policy lists
mean "no constraint of that kind"; a clean (empty) file list yields zero
violations.

calls internal: _glob_match x2
calls stdlib: builtins.bool x2, builtins.int x2, builtins.isinstance x2, builtins.any, builtins.next
reads stdlib: builtins.float x2, builtins.int x2, builtins.list, builtins.str
writes internal: evaluate_git_change_policy.policy
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
