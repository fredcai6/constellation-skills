# scripts.checklist_engine:amend._floor
method, scripts/checklist_engine.py:2079, 8 lines

```python
def _floor() -> int
```

1 + index of the last non-pending (frozen) gate; 0 if none. A new gate

may not be inserted at an index below this.

calls stdlib: builtins.enumerate

referenced by: none found
