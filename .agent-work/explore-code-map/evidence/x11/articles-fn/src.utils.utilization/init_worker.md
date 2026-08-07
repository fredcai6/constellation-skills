# src.utils.utilization:init_worker
function, src/utils/utilization.py:203, 21 lines

```python
def init_worker(threads_per_worker: int, priority: str) -> None
```

Configure the *current* process for a single worker slot.

Module-level and side-effect-only so it is usable as a ``ProcessPoolExecutor``
initializer (which must be importable/picklable). Sets the BLAS/OMP thread-cap
environment variables, then — if torch is importable — caps torch's thread pool,
then applies a best-effort OS priority. The torch import is guarded so the module
and this function work even when torch is absent.

calls internal: _set_os_priority
calls stdlib: builtins.str
reads internal: logger
reads stdlib: builtins.Exception, os (module), os.environ
writes stdlib: os.environ[]
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
