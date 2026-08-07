[map index](../INDEX.md) / [`src.utils.constants`](INDEX.md)

# `validate_session_type`
*function* [s] · [`src/utils/constants.py:354`](C:/Programs/f1Brainz/src/utils/constants.py#L354) · 11 lines [s]

**Signature** [s]

```python
def validate_session_type(session_type: str) -> bool
```

> Validate if session type is recognized.
>
> Args:
>     session_type: Session type string
>
> Returns:
>     True if valid, False otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `session_type` — session_type: Session type string [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `SESSION_TYPES` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
