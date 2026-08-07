# scripts.code_map.cli:_Parser
class, scripts/code_map/cli.py:42, 12 lines

```python
class _Parser(ArgumentParser)
```

Resolves the artifact and map directories against `--root` at parse time,

so a caller reading the parsed arguments never has to redo that join and the
two cannot drift apart.

- [parse_args](_Parser.parse_args.md) method: HOLE: no docstring

referenced by: 1 sites, this module only
