[map index](../INDEX.md) / [`src.utils.console`](INDEX.md)

# `force_utf8_console`
*function* [s] · [`src/utils/console.py:30`](C:/Programs/f1Brainz/src/utils/console.py#L30) · 4 lines [s]

**Signature** [s]

```python
def force_utf8_console() -> None
```

> Make stdout and stderr UTF-8 so unicode prints don't crash under cp1252.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `force_stream_utf8` x2 |
| reads | stdlib | `sys (module)` x2, `sys.stderr`, `sys.stdout` |

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
