# src.utils.utilization:_detect_available_mem_gb
function, src/utils/utilization.py:77, 3 lines

```python
def _detect_available_mem_gb() -> float
```

Currently-available system memory in GiB.

calls third-party: psutil.virtual_memory
reads third-party: psutil (module)
unresolved: 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
