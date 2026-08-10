# Implementer handoff — post-archive fix: the MCP door mangles non-ASCII on Windows

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g3fix2` (post-archive fix)
**Worktree (work only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door` · **PR #533**
**Authority:** Commander for issue #424, under `LAUNCH_ORDER-424-continuation.md`, whose definition of
done requires the **PR green**. It is not.

## This is a PRODUCT defect, not a test artifact. Read that first.

Windows CI is red with mojibake. An em-dash written `—` (U+2014, UTF-8 `E2 80 94`) arrives as `â€”` —
the classic signature of UTF-8 bytes decoded as cp1252:

```
E  AssertionError: projection for 'g1-implement' has an ACTIVE line that does not match the
   expected 'ACTIVE <id> [<status>] — <imperative>' shape:
   "ACTIVE g1-implement [pending] â€” Fill templates/IMPLEMENTER_HANDOFF.template.md ..."
   tests\test_mcp_imperative_equivalence.py:215
```

and `tests/test_mcp_spine_server.py` reds separately with `isError: True` where a call should have
succeeded (lines ~274, ~289, ~309).

**Do not reach for the test file first.** On Windows, Python's stdio defaults to the ANSI code page
(cp1252), not UTF-8. `scripts/mcp_spine_server.py` speaks JSON-RPC over `sys.stdin` / `sys.stdout`
(see its read loop around line 530 and its writes around 563-572) and never pins an encoding. The
engine's own rails, imperatives and refusal text are full of em-dashes and other non-ASCII. So **the
shipped door corrupts its own protocol on Windows for the ordinary case** — every gate whose
imperative contains an em-dash, which is most of them. The CLI door is unaffected, so this is
precisely the kind of CLI/MCP divergence DC4 exists to catch, and it caught it.

The test harnesses have the mirror-image bug: `tests/test_mcp_identity.py` (around line 118) and
`tests/test_mcp_spine_server.py` both `subprocess.Popen(..., text=True)` with no `encoding=`, so they
decode the child's pipes with the platform default too.

## Task

Make the door's stdio UTF-8 on every platform, and make the tests decode it as UTF-8.

1. **`scripts/mcp_spine_server.py` — the real fix.** Pin the protocol encoding to UTF-8 explicitly
   rather than inheriting the platform default. Say in a comment *why*, naming Windows/cp1252, so
   nobody "simplifies" it back later. The MCP stdio transport is UTF-8; this is conformance, not a
   workaround.
2. **`tests/test_mcp_identity.py` and `tests/test_mcp_spine_server.py`** — pass an explicit UTF-8
   encoding when opening the child's pipes, so a future regression in (1) surfaces as a decode
   mismatch rather than being silently papered over by a matching default on Linux.
3. **Consider whether the engine's own captured output needs the same treatment.** The server runs
   `checklist_engine.main(argv)` in-process under `redirect_stdout`/`redirect_stderr` into
   `StringIO`, which is unicode and therefore fine — verify that rather than assume it, and say which
   you did.

## Constraints

- Work only in the worktree above. In scope: `scripts/mcp_spine_server.py`,
  `tests/test_mcp_identity.py`, `tests/test_mcp_spine_server.py`.
- **Do not change any imperative text, template, or engine file to dodge the encoding problem.**
  Replacing em-dashes with hyphens would turn a real product defect into a hidden one, and would
  quietly rewrite doctrine text this workstream does not own. If you find yourself editing a
  `.template.json` or `scripts/checklist_engine.py`, stop.
- **Do not weaken any DC2/DC3/DC4 guarantee.** DC4's byte-identity property is the check that caught
  this; it must still compare rendered output byte-for-byte, not normalised or ASCII-folded text.
- Do not touch `settings.json` at any scope, any checklist JSON, or anything under `episodes/`.
- Adding or changing module-level entities makes `map/INDEX.md` stale and reds
  `tests/test_code_map.py`. Stage first, then `python -m scripts.code_map build --root .`, and commit.

## Verification

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_identity.py tests/test_mcp_imperative_equivalence.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Baseline: **2177 passed, 1 skipped, 1061 subtests, 0 failed** on Linux. Same bar.

**The target is Windows CI, which you cannot run.** So build one piece of evidence that does not
depend on the platform: demonstrate that the door round-trips a non-ASCII imperative through a real
server subprocess **byte-for-byte**, and show the bytes (e.g. the UTF-8 encoding of the round-tripped
string) rather than only that a string comparison passed. A test that passes on Linux by accident of
a matching default is exactly what shipped this bug.

State plainly which claims you verified locally and which are reasoning about Windows. Do not present
the second as the first.

## Reporting

Write your `IMPLEMENTER_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-handoffs/g3-implementer-result-utf8.md
```

**Write that file before ending your turn — the write is the delivery.** Include exact commands with
real output and exit codes, the byte-level round-trip evidence, the local-vs-reasoned split, and a
blunt `## Workflow Feedback` section. Commit to `epic-418/f-424-mcp-door`.
