# `src.utils.console`

> Console encoding helpers for CLI script entrypoints.
>
> On Windows a redirected stdout/stderr defaults to the cp1252 code page, so a plain
> ``print("→")`` raises ``UnicodeEncodeError`` and crashes the run. Scripts that emit
> non-ASCII status output call :func:`force_utf8_console` at the top of ``main`` so
> their output is safe regardless of the active code page (see issue #358).

*(everything after the first line above is [s].)*

`src/utils/console.py` · 33 lines [s] · 2 top-level, 2 entities total · 2 documented, 0 **holes**

## Dependencies

**Imports (stdlib)**: `__future__.annotations`, `sys`, `typing.TextIO`

**Imported by**: no importer inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted, so this is *not* evidence the module is unused).

## Contents

- [`force_stream_utf8`](#force-stream-utf8) — *function* — Reconfigure *stream* to UTF-8 when it supports it; otherwise do nothing.
- [`force_utf8_console`](#force-utf8-console) — *function* — Make stdout and stderr UTF-8 so unicode prints don't crash under cp1252.

---

## `force_stream_utf8`
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


## `force_utf8_console`
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

**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; `[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. No sentence on this page was written by a model.

Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based lines for all 87 entities and the schema does not say so (defect D1).
