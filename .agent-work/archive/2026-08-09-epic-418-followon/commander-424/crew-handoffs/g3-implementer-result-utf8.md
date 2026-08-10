# Implementation Result

## Assigned gate
`g3fix2` (post-archive fix, issue #424, workstream F, epic #418) — Windows CI mojibake in the MCP door's stdio.

## Completed slice
Pinned `scripts/mcp_spine_server.py`'s protocol encoding to UTF-8 explicitly (stdin, stdout, and stderr), instead of
inheriting the platform default (cp1252 on Windows) — conformance with the MCP stdio transport spec, not a
workaround. Made `tests/test_mcp_identity.py` and `tests/test_mcp_spine_server.py` decode the door's child pipes as
explicit UTF-8 everywhere they open one, so a future regression in the server surfaces as a decode mismatch rather
than being masked by a matching platform default on Linux. Added a new, platform-independent, byte-level regression
test that reproduces the Windows hazard on Linux and proves the fix red-then-green.

## Scope
**Files changed:**
- `scripts/mcp_spine_server.py` — the real fix: `_utf8_stdio()`, called at the top of `main()`.
- `tests/test_mcp_identity.py` — `ServerInstance.__init__`'s `Popen` now passes `encoding="utf-8"`.
- `tests/test_mcp_spine_server.py` — `encoding="utf-8"` added to all 4 remaining `Popen`/`subprocess.run`
  `text=True` call sites (`McpRpcClient.__init__`, `ToolsWrapEngineTests._cli_current`, the CLI-refusal
  `subprocess.run` in `RefusalSurfacesAsIsErrorTests`, and `McpJsonVarExpansionLaunchTests`'s launch `Popen`), plus a
  new `Utf8StdioConformanceTests` class (byte-level round-trip regression coverage).
- `map/INDEX.md` — rebuilt (`python -m scripts.code_map build --root .`) after the new function/class landed;
  per-symbol sub-pages under `map/<module>/` are gitignored (`map/*`), only `map/INDEX.md` is tracked.
- `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-plans/g3fix2-implementer-plan-utf8.json`
  (+ its `.journal`) and the `g3fix2-utf8-mcp-door/{context,mechanical}/*.json` context-manifest sidecars — the
  engine-driven plan for this run and its auto-emitted sidecars.

**Specific exclusions touched:** no. `scripts/checklist_engine.py` was read (to mirror its existing `_utf8_stdio()`
precedent for stdout/stderr) but not edited. No `.template.json`, no imperative/rail/doctrine text, no
`settings.json` at any scope, no checklist JSON, nothing under `episodes/`.

## Behavior changed
Yes. The MCP door's `sys.stdin`/`sys.stdout`/`sys.stderr` are now explicitly UTF-8 on every platform, regardless of
the ambient locale/codepage default. On Linux this is a no-op (the platform default is already UTF-8, which is
exactly why this class of bug ships unnoticed from a Linux dev box — see the Local-vs-Windows split below). On
Windows, this closes the path by which a non-ASCII request argument sent as raw (non-ASCII-escaped) UTF-8 bytes —
the shape a real, non-Python MCP client sends — would previously be decoded with the ANSI codepage (cp1252) before
`json.loads()` ever saw it, corrupting the value permanently at the point of entry.

## Map Impact
- **Structural anchors touched:** `scripts.mcp_spine_server` (7→8 entities: new `_utf8_stdio()`),
  `tests.test_mcp_spine_server` (44→50 entities: new `Utf8StdioConformanceTests` class + its 4 methods), both
  module-level — map rebuilt, `tests/test_code_map.py` reconfirmed fresh (148 passed, 63 subtests).
- **Capabilities added/changed/affected:** the MCP door (`scripts/mcp_spine_server.py`) now conforms to the MCP
  stdio transport's UTF-8 requirement on every platform, not only where the OS default happens to already be UTF-8.
- **Constraints/assumptions touched:** DC4's byte-identity property (`tests/test_mcp_imperative_equivalence.py`) was
  read but not edited or weakened — still compares rendered `ACTIVE <id> [<status>] — <imperative>` substrings
  verbatim, not normalised/ASCII-folded. `run_engine()`'s `io.StringIO()` capture of the in-process engine call was
  independently verified (not assumed) to need no encoding treatment — see Assumptions.
- **Trust limitations / drift found:** `tests/test_mcp_imperative_equivalence.py:182`'s `cli_current_text()` has
  the identical missing-encoding defect and was very likely the literal origin of the handoff's pasted CI failure
  trace, but that file is outside this handoff's stated scope. Filed as triage candidate `tc1` on this plan (see
  Out-of-scope observations).
- **Claims/evidence produced:** byte-level red→green round trip for the server's own stdin decode (below); full
  suite baseline reproduced exactly plus the one new test.

## Test mode
**Required:** test-led (behavior change with a real test surface — `global-crew.md`).
**Satisfied:** yes — genuine TDD red→green, reproduced locally without Windows (see below), not merely asserted.

## Evidence

### 1. RED — the new conformance test fails against the unfixed server

Before touching `scripts/mcp_spine_server.py`, added `Utf8StdioConformanceTests` to
`tests/test_mcp_spine_server.py` and ran it against the still-unfixed server:

```bash
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py -k utf8 -v
```

**Result:** 1 failed, exit code 1, in 0.07s (no hang):

```
E           AssertionError: b'tester\xe2\x80\x94caf\xc3\xa9' != b'tester\xc3\xa2\xe2\x82\xac\xe2\x80\x9dcaf\xc3\x83\xc2\xa9' : non-ASCII claimed_by did not round-trip byte-for-byte through the server's own stdin decode: sent b'tester\xe2\x80\x94caf\xc3\xa9', got back b'tester\xc3\xa2\xe2\x82\xac\xe2\x80\x9dcaf\xc3\x83\xc2\xa9' (decoded: 'testerâ€”café')
```

The decoded mismatch (`testerâ€”café`) is the *exact* mojibake signature the handoff describes (`â€”` for the
em dash), reproduced deterministically on Linux by forcing `PYTHONIOENCODING=cp1252` in the **server's own**
environment — the standard, documented, cross-platform way to force CPython's stdio streams to a non-UTF-8
default, i.e. exactly what an unconfigured `sys.stdin` defaults to on a Windows box, without needing Windows
itself. The test builds its request with `json.dumps(..., ensure_ascii=False)` (genuine multi-byte UTF-8 bytes on
the wire — the shape a real, non-Python MCP client sends; this repo's own `McpRpcClient`/`ServerInstance` always
use the bare `json.dumps()` default `ensure_ascii=True`, which ASCII-escapes every non-ASCII character before it
ever reaches a pipe, and so could never exercise this path — exactly the kind of Linux-only accidental green this
whole gate exists to catch).

**Debugging note, reported honestly:** an early draft of this test used a naked blocking `proc.stdout.readline()`
and an eager f-string in the assertion message calling `proc.stderr.read()` unconditionally — the exact
deadlock-prone anti-pattern this same file's own `McpJsonVarExpansionLaunchTests` docstring already warns about
(`proc.stderr.read()` blocks until EOF, and the child, still alive with stdin open, never closes it on the success
path). It hit that deadlock in practice. Fixed by (a) reading via a daemon reader thread + `queue.Queue` with a
bounded `timeout=`, mirroring `test_mcp_identity.py`'s own `ServerInstance` house pattern, and (b) deferring
`proc.stderr.read()` to the failure branch only (`self.fail(...)` inside an `if ... is None:` check), never inside
an eagerly-evaluated assert-message argument.

### 2. GREEN — the fix, and the same test passing

Added `_utf8_stdio()` to `scripts/mcp_spine_server.py`, called at the top of `main()`:

```python
def _utf8_stdio() -> None:
    """Pin the protocol encoding to UTF-8 explicitly rather than inheriting
    the platform default. On Windows, Python's stdio falls back to the ANSI
    code page (cp1252), not UTF-8, unless a stream is reconfigured -- the
    same trap scripts/checklist_engine.py's own `_utf8_stdio()` already
    names for the CLI's stdout/stderr (that CLI never reads stdin, so it
    never had to cover this door's own extra surface: `sys.stdin`, read
    every request off, here). The MCP stdio transport IS UTF-8 by spec, so
    this is conformance, not a workaround -- do not "simplify" it back to
    the platform default."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


def main() -> None:
    _utf8_stdio()
    for line in sys.stdin:
        ...
```

```bash
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py -k utf8 -v
```

**Result:** `1 passed, 21 deselected in 0.05s`. Exit code 0. Same `PYTHONIOENCODING=cp1252` forcing, same raw
`ensure_ascii=False` request bytes — the fix, not the environment, made the difference.

### 3. Harness fixes: both named files, plus the DC4 population test, green together

```bash
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_identity.py tests/test_mcp_imperative_equivalence.py
```

**Result:** `39 passed in 3.80s`. Exit code 0. (`test_mcp_identity.py` alone: `12 passed in 0.65s`, same count as the
pre-existing baseline — DC2/DC3 unweakened. `test_mcp_imperative_equivalence.py`'s DC4 population test —
`test_every_gate_imperative_is_byte_identical_between_cli_and_mcp`, exercising all ~61 gates — passed unmodified;
that file imports and reuses `ServerInstance` from `test_mcp_identity.py`, already fixed, and its own
`assertEqual`/`ACTIVE_LINE_RE` comparisons were not touched.)

### 4. `io.StringIO` capture verification (task item 3 — verified, not assumed)

```bash
python3 -c "
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    print('em dash test: —')
val = buf.getvalue()
print(repr(val)); print('is str:', isinstance(val, str))
"
```

**Result:** `'em dash test: —\n'`, `is str: True`. `io.StringIO` is a built-in C class operating purely on Python
`str` objects — `contextlib.redirect_stdout(io.StringIO())` swaps `sys.stdout` for the duration of the `with`
block, and `.write()`/`.getvalue()` never invoke any encode/decode step. `run_engine()`'s capture of
`checklist_engine.main()`'s output needs no encoding treatment on any platform — confirmed, not assumed.

### 5. Map rebuild + freshness

```bash
cd /home/tommy/projects/constellation-skills-wt/f-424 && python -m scripts.code_map build --root .
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_code_map.py
```

**Result:** map build exit 0; `148 passed, 63 subtests passed in 11.62s`.

### 6. Full suite baseline

```bash
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

**Result:** `2178 passed, 1 skipped, 1061 subtests passed in 98.89s (0:01:38)`. Exit code 0. That is the stated
baseline (`2177 passed, 1 skipped, 1061 subtests, 0 failed`) plus the one new conformance test, 0 failed — same
bar.

## TDD evidence, if required
- Failing test observed: §1 above (`1 failed` in `0.07s`, decoded mismatch `testerâ€”café`).
- Passing test observed: §2 above (`1 passed` in `0.05s`).
- Refactor while green: no refactor step was needed beyond the fix itself; the bounded-reader-thread rewrite of
  the test's own I/O (described in §1's debugging note) happened *before* the RED run was accepted as evidence,
  not after.

## Local-vs-Windows split (stated plainly, per the handoff's requirement)

**Verified locally (Linux, this exact tree):**
- The mojibake failure mode is real and reproducible: forcing `PYTHONIOENCODING=cp1252` on the server's own
  process, then sending genuine raw (non-ASCII-escaped) UTF-8 bytes over its stdin, produces exactly the
  `testerâ€”café`-shaped corruption the handoff describes, byte-for-byte (§1).
- The fix (`_utf8_stdio()`, explicit `.reconfigure(encoding="utf-8")`) eliminates that corruption under the
  identical forced-cp1252 environment (§2) — this is not "passes because the platform default already agrees";
  the ambient default was deliberately forced *wrong* and the explicit reconfigure overrode it anyway.
- All three named files' tests, DC2/DC3, DC4's whole population, and the full suite are green (§3, §6).
- `io.StringIO`'s unicode-native behavior (§4).

**Reasoned about Windows, not independently verified there (cannot run Windows in this environment):**
- That Windows' actual unconfigured `sys.stdin`/`sys.stdout` default is cp1252 (or another non-UTF-8 ANSI
  codepage) — this is well-documented CPython behavior and the same claim `scripts/checklist_engine.py`'s own
  pre-existing `_utf8_stdio()` already rests on for its stdout/stderr half, but I did not measure it on an actual
  Windows box.
- That a real (non-Python) MCP client genuinely sends raw, non-ASCII-escaped UTF-8 bytes over stdin rather than
  ASCII-escaped JSON — inferred from how `JSON.stringify` behaves in JS/TS hosts by default, not measured against
  an actual MCP client implementation.
- That this exact fix, applied on an actual Windows CI runner, turns the originally-reported red into green. The
  `PYTHONIOENCODING=cp1252` simulation is the closest platform-independent stand-in available, and the reasoning
  chain from "forced cp1252 default corrupts, explicit reconfigure fixes it" to "Windows' own unconfigured default
  corrupts the same way, the same reconfigure fixes it the same way" is direct, but it is reasoning by mechanism,
  not a Windows CI run.
- Whether `tests/test_mcp_imperative_equivalence.py`'s unfixed `cli_current_text()` (triage candidate `tc1`,
  below) is *actually* the literal file/line behind the handoff's pasted CI trace — this is a strong inference
  (matching mechanism, matching mojibake shape, matching assertion-failure text) but not confirmed against the
  original Windows CI log.

## Docs/contracts touched
- none — no `.template.json`, no imperative/rail text, no `scripts/checklist_engine.py` edits.

## Assumptions
- None beyond what's stated in the Local-vs-Windows split above.

## Stop conditions hit
- None that blocked the work. One genuine scope gap was found and routed via `flag-candidate` rather than
  silently fixed or silently dropped — see Out-of-scope observations.

## Out-of-scope observations
- **`tests/test_mcp_imperative_equivalence.py:182`, `cli_current_text()`** — `subprocess.run([sys.executable,
  ENGINE, ..., "current"], capture_output=True, text=True)` with no explicit `encoding=`. This is the identical
  missing-encoding defect this gate fixed elsewhere, but this file was **not** in the handoff's stated scope
  (`scripts/mcp_spine_server.py`, `tests/test_mcp_identity.py`, `tests/test_mcp_spine_server.py` only), so it was
  read but not edited. `checklist_engine.py`'s own `_utf8_stdio()` already pins the CLI child's stdout to UTF-8 on
  write, so that CLI subprocess emits genuine raw multi-byte UTF-8 bytes for its rendered `ACTIVE <id> [<status>]
  — <imperative>` line (unlike the MCP door's JSON-RPC responses, which stay ASCII-safe by construction via
  `json.dumps`'s default `ensure_ascii=True`); on Windows this parent-side read would decode those raw bytes with
  the platform cp1252 default and mojibake, breaking the `ACTIVE_LINE_RE` match `extract_imperative()` requires —
  this is very likely the literal origin of the handoff's pasted failure trace. Filed as flag-candidate `tc1` on
  this plan (`g3fix2-implementer-plan-utf8.json`) for Commander to route: either amend this gate's scope by one
  file and one `encoding="utf-8"` kwarg, or open it as an immediate follow-up. **Until it lands, the DC4
  population test may still fail with mojibake on actual Windows CI even after this fix merges** — this fix alone
  is not sufficient to guarantee the originally-reported CI run goes fully green.

## Workflow Feedback

- **Handoff gaps:** the handoff's stated scope (3 files) does not include the file most likely responsible for the
  exact failure trace it pasted (`tests/test_mcp_imperative_equivalence.py:215`/`216`, `extract_imperative()`/
  `cli_current_text()`). This isn't a defect in the handoff's reasoning about the *product* bug (the server-side
  fix is correct and necessary regardless), but the stated scope may not be sufficient, on its own, to turn the
  originally-observed Windows CI failure fully green. Worth a scope-completeness pass before pasting a CI trace
  into a handoff: name the exact file/line the trace's assertion originates from, and check it against the scope
  list.
- **Context rediscovered:** `json.dumps()`'s default `ensure_ascii=True` ASCII-escapes the entire MCP JSON-RPC
  wire protocol in both directions for every call site in this repo's own Python test clients, which makes the
  *outbound* half of the door's own protocol accidentally immune to a stdout codec mismatch as currently written
  (only `sys.stdin`, decoding a genuinely raw non-ASCII request from a non-Python client, is reachably exploitable
  through the JSON-RPC layer today). This took real digging to establish and isn't stated anywhere in the handoff
  or in `scripts/mcp_spine_server.py`'s own docstring; pinning stdout/stderr regardless is still correct
  (conformance + defense against a future `ensure_ascii=False` change), but the *reachability* argument for why
  the fix matters would have been faster to build with this fact already in hand.
- **Instructions improvised around:** the engine template's TDD guidance ("encode the RED step as a check:null
  postcondition... keep the GREEN step as the command check") assumes a red state is naturally available. Here
  the platform-specific bug isn't naturally red on Linux; I had to *construct* a platform-independent red state
  (the `PYTHONIOENCODING=cp1252` simulation) as its own first-class deliverable rather than a red state that
  already existed to be observed. Worked within the template as given (m1's postcondition is `check: null`,
  manually attested with the captured failure output), but a plan template built to fix a platform-conditional bug
  from a platform that can't reproduce it might want to say this explicitly rather than leave it to be inferred.
- **What would have made this easier:** a plan template variant (or a documented convention) for "construct a
  platform-independent red state" as a distinct step shape from "TDD red already exists, observe it" — the two
  require materially different guidance (the former needs to justify *why* the simulation is faithful to the real
  platform hazard, not just that a test fails).

## Return status
`complete`
