# scripts.code_map.cli
scripts/code_map/cli.py, 121 lines, 8 holes

The code_map command line: one entrypoint in front of the whole pipeline.

python -m scripts.code_map build          extract -> supplement -> render
    python -m scripts.code_map discover       print the mappable corpus
    python -m scripts.code_map extract        the statement store only
    python -m scripts.code_map supplement     the supplement only
    python -m scripts.code_map render         the page tree only
    python -m scripts.code_map check          the print-only diagnostics

Every subcommand takes `--root`, so nothing here is pinned to one checkout; the
prototype this was ported from hardcoded an absolute path to another repository.

Stage modules are imported inside their handler rather than at module scope.
Parsing arguments must not pay for the extractor, and `discover` must run before
a later gate has finished moving the stages around.

imports stdlib: argparse, pathlib.Path
imports internal: scripts.code_map.checks:, scripts.code_map.discovery:, scripts.code_map.extract:, scripts.code_map.render:, scripts.code_map.supplement:
imported by: scripts.code_map.__main__, tests.test_code_map

```python
REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIRNAME = '.code-map'
MAP_DIRNAME = 'map'
STAGES = (('discover', 'print the mappable corpus and stop'), ('extract', 'walk the corpus and w...
_WANTS_ARTIFACTS = {'extract', 'supplement', 'render', 'build', 'check'}
_WANTS_OUT = {'render', 'build', 'check'}
HANDLERS = {'discover': _discover, 'extract': _extract, 'supplement': _supplement, 'render': _rend...
```

- [_Parser](_Parser.md) class: Resolves the artifact and map directories against `--root` at parse time,
  - [_Parser.parse_args](_Parser.parse_args.md) method: HOLE: no docstring
- [build_parser](build_parser.md) function: The argument parser for every stage. One `--root` per subcommand rather
- [_discover](_discover.md) function: HOLE: no docstring
- [_extract](_extract.md) function: HOLE: no docstring
- [_supplement](_supplement.md) function: HOLE: no docstring
- [_render](_render.md) function: HOLE: no docstring
- [_build](_build.md) function: HOLE: no docstring
- [_check](_check.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
