# scripts.run_skill_eval:_print_verdict
function, scripts/run_skill_eval.py:1277, 21 lines

```python
def _print_verdict(v: Verdict, *, as_json: bool) -> None
```

HOLE: no docstring

calls stdlib: builtins.print x6, json.dumps
reads internal: Verdict.completed_count x2, Verdict.corpus_id x2, Verdict.exit_code x2, Verdict.fenced_count x2, Verdict.passed_count x2, Verdict.source_commit x2, Verdict.status x2
reads stdlib: json (module)

referenced by: 1 sites, this module only
