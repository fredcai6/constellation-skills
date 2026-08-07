# src.utils.utilization:_detect_physical_cores
function, src/utils/utilization.py:72, 3 lines

```python
def _detect_physical_cores() -> int
```

Best available physical-core count, never below 1.

calls stdlib: os.cpu_count
calls third-party: psutil.cpu_count
reads stdlib: os (module)
reads third-party: psutil (module)

referenced by: 1 sites, this module only
