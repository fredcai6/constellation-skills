# tests.test_install_constellation:HookWiringOptInTests.test_the_wired_command_string_actually_executes
method, tests/test_install_constellation.py:2252, 21 lines

```python
def test_the_wired_command_string_actually_executes(self)
```

Run the generated command EXACTLY as Claude Code would -- same string,

stdin JSON -- and require it not to refuse.

String-matching the rendered command is not evidence that it works, and
this whole issue exists because a shipped-but-inert Context Governor is
indistinguishable from a working one from the outside. A quoting slip,
a bad interpreter, or a path that does not resolve would be invisible to
every other assertion in this class.

calls internal: HookWiringOptInTests._entries, HookWiringOptInTests._wire, HookWiringOptInTests.assertEqual
calls stdlib: subprocess.run, tempfile.TemporaryDirectory
reads stdlib: os (module), os.environ, subprocess (module), tempfile (module)
unresolved: 3 reads (dispatch-unknown-base)

referenced by: none found
