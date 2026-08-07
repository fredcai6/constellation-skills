[map index](../INDEX.md) / [`src.utils.console`](INDEX.md)

# `force_stream_utf8`
*function* [s] · [`src/utils/console.py:15`](C:/Programs/f1Brainz/src/utils/console.py#L15) · 13 lines [s]

**Signature** [s]

```python
def force_stream_utf8(stream: TextIO | None) -> None
```

> Reconfigure *stream* to UTF-8 when it supports it; otherwise do nothing.
>
> No-op when *stream* is ``None`` or has no ``reconfigure`` (e.g. it has already
> been replaced by a capture buffer), and when reconfiguration is rejected.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `stream` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | stdlib | `builtins.OSError`, `builtins.ValueError` |

*Not shown: 1 local-variable calls, 1 local-variable reads, 1 local-variable writes; 1 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dynamic)

**Referenced by**: 2 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
