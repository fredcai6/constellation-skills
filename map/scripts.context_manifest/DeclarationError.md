# scripts.context_manifest:DeclarationError
class, scripts/context_manifest.py:171, 6 lines

```python
class DeclarationError(ValueError)
```

A `context_refs` entry is malformed, names an unknown root, or escapes it.

Raised rather than skipped: a declaration the producer cannot honour must fail
visibly, never degrade into a plausible-looking manifest that is missing a row.

referenced by: 12 sites, this module only
