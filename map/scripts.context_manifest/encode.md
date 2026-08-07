# scripts.context_manifest:encode
function, scripts/context_manifest.py:425, 4 lines

```python
def encode(obj: Any) -> str
```

The one canonical encoder. No second encoder, no stored digest to disagree

with its own bytes.

calls stdlib: json.dumps
reads stdlib: json (module)

referenced by: 1 sites, this module only
