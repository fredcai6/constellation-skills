# tests.test_episode_negative_control:test_every_field_has_a_named_independent_source
function, tests/test_episode_negative_control.py:784, 49 lines

```python
def test_every_field_has_a_named_independent_source(control)
```

C3: the control must be able to say, per field, what the independent source was —

and the saying must be BACKED, in three layers of decreasing strength.

The previous version had only the third layer: a substring scan over `exp.source`,
which is a human-readable DESCRIPTION. That checks what the harness says about
itself, never what it does, so mutation M5 — rewiring the oracle to read its tallies
back out of `mechanical_fields` while leaving the description untouched — passed
cleanly. It was also a substring scan over prose, which is the "assert against the
FIELD, never a substring of the serialized record" trap one level up.

**(a) Behavioural, and the one that actually carries the claim.** The expectation is
rebuilt with every producer under test patched to raise and the seam's emitted
snapshot made unreadable. If the oracle touches any of them it raises, and the test
fails naming what it touched. This proves independence by execution.

**(b) Static over CODE, not prose.** (a) is defeated by exactly one thing: a name
bound at import time (`from episode_capture import reopen_total`), which no attribute
patch can reach. So the expectation-building code is parsed and every identifier it
mentions is checked against `FORBIDDEN_IDENTIFIERS`. Over the AST rather than the
text, so a docstring saying "never `context_manifest.rev()`" — which the oracle's own
sources do say — is not mistaken for a call to it.

**(c) The prose check, kept.** It is cheap, it documents intent, and it catches a
description that has drifted from its value. It is no longer the only thing standing.

calls internal: _independence_harness
calls stdlib: builtins.sorted x3, builtins.isinstance x2, ast.parse, ast.walk, builtins.set, inspect.getsource, textwrap.dedent
reads internal: FORBIDDEN_IDENTIFIERS x2, MECHANICAL_GROUP, _ControlRun, _ControlRun.expectations, _git, blob_oid
reads stdlib: ast (module) x4, ast.Attribute, ast.Name, builtins.set, builtins.str, inspect (module), textwrap (module)
unresolved: 5 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
