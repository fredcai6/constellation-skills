# scripts.check_skill_freshness:_normalized_hash
function, scripts/check_skill_freshness.py:54, 25 lines

```python
def _normalized_hash(path: Path, skill: str, skills_root: Path) -> str
```

Content hash after resolving <skill-dir> / <name-skill-dir> tokens to the

installed skill dir, so the three sides compare on equal footing.

A template lives in three forms: the installed skill copy has absolute paths
(rewritten at install), while the baseline and the project working copy keep
the portable token form — and a *promoted* baseline (check_skill_freshness
--update-baseline copies the installed upstream) becomes absolute too.
Comparing raw hashes would flag a token-form working copy against an
absolute-form baseline as a phantom edit forever. Normalizing every side to
the resolved (absolute) form neutralizes the token-vs-absolute difference
while leaving genuine edits visible. Tokenless templates hash unchanged.

The installer also rewrites the `python <` interpreter prefix to the platform
interpreter (`py`/`python3`); the token-form baseline/working-copy keep `python
<`. Apply the same interpreter rewrite here FIRST (before the `<…-skill-dir>`
token consumes the trailing `<`) so that rewrite, too, reads as no edit.

calls internal: _platform_interpreter
calls stdlib: hashlib.sha256
reads stdlib: hashlib (module)
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
