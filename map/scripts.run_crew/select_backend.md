# scripts.run_crew:select_backend
function, scripts/run_crew.py:625, 26 lines

```python
def select_backend(explicit: str | None, *, launcher: str = DEFAULT_LAUNCHER, which=shutil.which) -> CrewBackend
```

Choose the crew-launch backend (Decision 4). PURE (given an injectable

`which`): explicit override always wins; otherwise auto-detect from whether the
headless `claude` CLI is on PATH.

  * `explicit in {"cli","external"}` -> that backend (explicit override wins);
  * `explicit in {None, "auto"}`     -> auto-detect: `which(launcher)` truthy
    (the CLI is on PATH) -> `CliBackend`; else `ExternalBackend`.

`which` is injectable so tests control PATH presence without touching the real
PATH. Fails visibly on an unknown token (no hidden fallback).

calls internal: CliBackend x2, ExternalBackend x2, CrewLaunchError, select_backend.which
reads internal: BACKEND_AUTO x2, BACKEND_CLI x2, BACKEND_EXTERNAL x2

referenced by: 1 sites, this module only
