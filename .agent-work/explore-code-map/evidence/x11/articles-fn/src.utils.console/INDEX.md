[map index](../INDEX.md)

# `src.utils.console`

> Console encoding helpers for CLI script entrypoints.
>
> On Windows a redirected stdout/stderr defaults to the cp1252 code page, so a plain
> ``print("→")`` raises ``UnicodeEncodeError`` and crashes the run. Scripts that emit
> non-ASCII status output call :func:`force_utf8_console` at the top of ``main`` so
> their output is safe regardless of the active code page (see issue #358).

*(everything after the first line above is [s].)*

`src/utils/console.py` · 33 lines [s] · 2 entities · 2 documented, 0 **holes**

## Dependencies

**Imports (stdlib)**: `__future__.annotations`, `sys`, `typing.TextIO`

**Imported by**: no importer inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted, so this is *not* evidence the module is unused).

## Contents

- [`force_stream_utf8`](force_stream_utf8.md) — *function* [s] — Reconfigure *stream* to UTF-8 when it supports it; otherwise do nothing.
- [`force_utf8_console`](force_utf8_console.md) — *function* [s] — Make stdout and stderr UTF-8 so unicode prints don't crash under cp1252.
---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
