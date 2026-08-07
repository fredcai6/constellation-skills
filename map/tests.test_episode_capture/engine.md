# tests.test_episode_capture:engine
function, tests/test_episode_capture.py:110, 6 lines

```python
def engine(spine, *argv)
```

Run the real engine CLI the way an agent does, and return the CompletedProcess.

calls stdlib: builtins.str x2, subprocess.run
reads internal: ENGINE
reads stdlib: subprocess (module), sys (module), sys.executable

referenced by: 10 sites, this module only
