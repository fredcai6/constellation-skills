# src.utils.console
src/utils/console.py, 33 lines

Console encoding helpers for CLI script entrypoints.

On Windows a redirected stdout/stderr defaults to the cp1252 code page, so a plain
``print("→")`` raises ``UnicodeEncodeError`` and crashes the run. Scripts that emit
non-ASCII status output call :func:`force_utf8_console` at the top of ``main`` so
their output is safe regardless of the active code page (see issue #358).

imports stdlib: __future__.annotations, sys, typing.TextIO
imported by: none found (scripts/ and tests/ not indexed)

- [force_stream_utf8](force_stream_utf8.md) function: Reconfigure *stream* to UTF-8 when it supports it; otherwise do nothing.
- [force_utf8_console](force_utf8_console.md) function: Make stdout and stderr UTF-8 so unicode prints don't crash under cp1252.
