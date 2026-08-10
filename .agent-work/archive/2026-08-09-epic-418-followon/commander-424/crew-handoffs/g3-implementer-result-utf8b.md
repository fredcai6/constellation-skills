# Implementation Result

## Assigned gate
`g3fix3` (post-archive fix on issue #424, workstream F, epic #418) — pin
`tests/test_mcp_imperative_equivalence.py`'s `cli_current_text()` decode to
explicit UTF-8, the last unpinned decoder in the DC4 property test.

## Completed slice
Added `encoding="utf-8"` to `cli_current_text()`'s one `subprocess.run(...,
text=True)` call (line ~180-188, now line ~185-188), mirroring the exact
comment/shape already landed in `tests/test_mcp_spine_server.py`'s own
`_cli_current()`. Swept the whole file for other unpinned `text=True` call
sites — there was only ever this one.

## Scope
**Files changed:**
- `tests/test_mcp_imperative_equivalence.py` — the one in-scope production
  file; added `encoding="utf-8"` plus a short comment, no other change.
- `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-plans/g3fix3-implementer-plan-utf8b.json`
  (+ `.journal`) — the gated plan driven for this gate.
- `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-plans/g3fix3-utf8b-demo.py`
  — the one-off red/green demonstration script (see below; not a repo test).
- `.agent-work/.../evidence/g3fix3-utf8b-demo-{BEFORE,AFTER}-fix.txt` —
  captured demonstration output.
- `.agent-work/.../g3fix3-utf8b-cli-decode/{context,mechanical}/*.json` —
  engine-generated why-capture, one pair per plan item (same pattern g3fix2
  left in its own commit `eeec4f5d`).
- `.agent-work/.../commander-424/crew-runs.json` — engine-updated run
  bookkeeping (pre-existing tracked file, touched by the lease claim/release).
- `.agent-work/.../crew-handoffs/g3-implementer-handoff-utf8b.md` — the
  inbound handoff itself (was untracked; added so the record is complete).

**Specific exclusions touched:** no. No imperative text, template, or engine
file was touched; DC4's comparison assertions are byte-for-byte identical to
before this change; `settings.json`, checklist JSON, and `episodes/` were not
touched; the population walk and non-zero gate-count assertion are unchanged.

## Behavior changed
Yes, narrowly: `cli_current_text()` now always decodes the CLI child's
stdout as UTF-8 explicitly instead of falling back to
`locale.getencoding()` (the platform default) when no `encoding=` is given.
On this Linux box the platform default already resolves to UTF-8, so no
locally-observable test outcome changes (all 2178 tests that passed before
still pass). On an unconfigured Windows box, where that default resolves to
cp1252, this removes a real mangling of the CLI arm's rendered
`ACTIVE <id> [<status>] — <imperative>` line — reasoned, not locally
verified (see Local vs Reasoned below).

## Map Impact
No structural anchors, capabilities, events, or decisions were added or
changed — `python -m scripts.code_map build --root .` was re-run after the
edit and produced **zero diff** to `map/INDEX.md` (confirmed via
`git status --porcelain map/`), consistent with the change being a keyword
argument added inside an existing function body, not a new top-level entity.
- **Trust limitations / drift found:** none newly introduced.
- **Triage candidates:** none. This item is itself the resolution of the one
  triage candidate (`tc1`) g3fix2 filed for this exact gap.

## Test mode
**Required:** `test-after` for the production fix (a decode-default pin,
proven by demonstration rather than a driven-in-repo TDD red/green, since the
bug only manifests under a platform default this box cannot literally
reproduce) plus an explicit **evidence-only** red-then-green demonstration
required by the handoff.
**Satisfied:** yes — see Evidence and the demonstration section below.

## Evidence

```bash
cd /home/tommy/projects/constellation-skills-wt/f-424 && bash -c 'offending=$(grep -n "text=True" tests/test_mcp_imperative_equivalence.py | grep -v "encoding="); if [ -n "$offending" ]; then echo "$offending"; exit 1; fi' && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_imperative_equivalence.py
```
```
.....                                                                    [100%]
5 passed in 2.53s
```
**Result:** pass, exit 0. Sweep is clean and the file's 5 tests match the
handoff's stated baseline of 5 tests in this file.

```bash
grep -n "text=True" tests/test_mcp_imperative_equivalence.py
```
```
187:        capture_output=True, text=True, encoding="utf-8", timeout=30,
```
**Result:** the only remaining `text=True` line in the file carries
`encoding=` on the same line — the sweep the handoff asked for.

```bash
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
```
2178 passed, 1 skipped, 1061 subtests passed in 97.91s (0:01:37)
```
**Result:** pass, exit 0. Exact match to the stated baseline (2178 passed, 1
skipped, 1061 subtests, 0 failed).

```bash
python -m scripts.code_map build --root . && git status --porcelain map/
```
**Result:** exit 0; `git status --porcelain map/` printed nothing — no map
drift from this change.

## Red-then-green demonstration

**Kept as a one-off, NOT added as a permanent test.** The script is
`.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-plans/g3fix3-utf8b-demo.py`
— committed for the record (this repo tracks `.agent-work/` as durable run
history, same as prior crews' `crew-plans/scratch-*` files), but it is not
imported by, referenced from, or collected by any pytest run; the target
file's test count is unchanged at 5, matching the handoff's pinned baseline.

**Why a direct-decode demonstration instead of the handoff's suggested
`PYTHONIOENCODING=cp1252`-in-the-child's-env recipe (correction, stated
explicitly):** the handoff's example doesn't reach the actual bug site for
*this* fix, and I verified this locally before building the demonstration
differently. Two things are true simultaneously:

1. `checklist_engine.py`'s own `_utf8_stdio()` (line 43-55, called
   unconditionally at module import, line 55) already reconfigures the CLI
   child's own `sys.stdin/stdout/stderr` to UTF-8 the moment the CLI process
   starts — before anything in that child's environment (`PYTHONIOENCODING`
   included) could matter. So the CLI child **always** emits genuine UTF-8
   bytes on the wire, on every platform, regardless of `PYTHONIOENCODING` set
   in its own env. (This is the mechanism g3fix2 fixed for the MCP door's
   side; the CLI door had it fixed even earlier, hence no bug on the encode
   side here.)
2. The actual bug in `cli_current_text()` is on the **decode (parent) side**:
   `subprocess.run(..., text=True)` with no `encoding=` picks
   `locale.getencoding()` as its default. I confirmed empirically (below)
   that `PYTHONIOENCODING` set in the **calling** process's own environment
   has **no effect** on that default either — it only governs a *new*
   interpreter's own stdio streams at its own startup, not
   `subprocess.py`'s internal pipe-decode default in the process that is
   already running and calling `subprocess.run`.

Verified locally:
```bash
$ python3 -c "import locale; print(locale.getencoding())"
UTF-8
$ PYTHONIOENCODING=cp1252 python3 -c "import locale; print(locale.getencoding())"
UTF-8
$ LC_ALL=C python3 -c "import locale; print(locale.getencoding())"
ANSI_X3.4-1968
```
`PYTHONIOENCODING` does nothing to `locale.getencoding()`; only the locale
(`LC_ALL`/`LANG`) does. This box's available locales (`locale -a`) are only
`C`, `C.utf8`, `POSIX`, and a set of `en_*.utf8` variants — no `cp1252` (a
Windows codepage) is installable as a POSIX locale here, so I could not force
the exact Windows-default decode via environment/locale manipulation alone.

**What I did instead — the honest, directly-controlled proxy:** the
demonstration script spawns the real, unmodified `checklist_engine.py` CLI
subprocess exactly as `cli_current_text()` does, captures its **raw stdout
bytes** (no `text=True`, so nothing decodes them yet), gets the MCP arm's
already-correct reference text via `ServerInstance` (untouched, fixed by
g3fix2), then decodes those *same real production bytes* two ways:

- **BEFORE** — `raw.decode("cp1252")`: the literal decode an unconfigured
  Windows box's `subprocess.run(text=True)` would apply to these exact
  bytes (Windows' `locale.getencoding()` resolving to the ANSI codepage is
  documented CPython/Windows behavior — reasoned, not locally verified,
  since this run is on Linux).
- **AFTER** — `raw.decode("utf-8")`: what the fix now pins explicitly.

Run before the fix landed (`tests/test_mcp_imperative_equivalence.py` still
unmodified at that point — confirmed via `grep -n "encoding=" ...` showing no
hits, and via `sed -n '176,189p'` showing the bare `text=True` call):

```bash
$ python3 .agent-work/.../crew-plans/g3fix3-utf8b-demo.py
Demonstration gate: skills/admiral/templates/ADMIRAL_SPINE.template.json::closeout
CLI raw stdout: 2688 bytes, contains non-ASCII bytes: True
MCP  ACTIVE line (reference, correct): "ACTIVE closeout [pending] — The run cannot close ..."
CLI  ACTIVE line BEFORE (cp1252 decode -- simulated unfixed default): "ACTIVE closeout [pending] â€” The run cannot close ..."
CLI  ACTIVE line AFTER  (utf-8 decode -- what the fix pins): "ACTIVE closeout [pending] — The run cannot close ..."

BEFORE matches MCP: False
AFTER  matches MCP: True
```
Exit code 0 (the script's own success criterion: BEFORE must mismatch and
AFTER must match — both held). Full captured output in
`evidence/g3fix3-utf8b-demo-BEFORE-fix.txt`.

**RED**, byte for byte the same shape as the handoff's pasted CI trace: the
source em-dash (U+2014, UTF-8 bytes `E2 80 94`) decoded as cp1252 renders as
the three-character mojibake `â€”` — exactly what the CI trace showed.

Run again after the fix landed (independent confirmation the fix doesn't
change what BEFORE/AFTER *would* look like — the demo decodes the real bytes
directly, so this run is not gated on the file's own edit, but re-running it
is cheap corroboration that nothing else shifted):

```bash
$ python3 .agent-work/.../crew-plans/g3fix3-utf8b-demo.py
...
BEFORE matches MCP: False
AFTER  matches MCP: True
```
Same result — **GREEN** for AFTER, confirmed both before and after the fix
(as expected, since the demonstration controls the decode directly rather
than depending on the file's own default). Full output in
`evidence/g3fix3-utf8b-demo-AFTER-fix.txt`.

**The actual repo-level green** — proof that the *fixed* `cli_current_text()`
function itself, exercised through the real test suite, is unaffected and
still passes on this platform where the platform default was already
UTF-8 — is the `pytest -q tests/test_mcp_imperative_equivalence.py` run
above (5 passed) and the full-suite run (2178 passed).

## Local vs. reasoned-about-Windows split

**Verified locally (this Linux box, this run):**
- `_utf8_stdio()` in `checklist_engine.py` is called unconditionally at
  module import (line 55), so the CLI child's own stdout is always UTF-8 on
  the encode side, on every platform — read the source, not assumed.
- `PYTHONIOENCODING` has zero effect on `locale.getencoding()` (the value
  `subprocess.run(text=True)` uses when no `encoding=` is given) — confirmed
  by direct `python3 -c` invocations, shown above.
- Decoding the real CLI subprocess's actual production wire bytes (for a
  real gate's real imperative text, containing a real em-dash) with cp1252
  produces the exact `â€”` mojibake pasted in the handoff's CI trace, byte
  for byte — confirmed by running the demonstration script and capturing its
  output.
- Decoding those same bytes with `encoding="utf-8"` (what the fix now does)
  matches the MCP arm's reference text exactly.
- The fixed file's own test suite (5 tests) and the full repo suite (2178
  tests) both pass, exit 0, matching the stated baseline exactly.
- `map/INDEX.md` has zero drift from this change (rebuilt and diffed).

**Reasoned, not locally verified (cannot run Windows):**
- That an *actually unconfigured* Windows Python process's
  `locale.getencoding()` resolves to `cp1252` specifically (rather than some
  other non-UTF-8 default) — this is documented CPython/Windows behavior
  (the ANSI code page via `GetACP()`, pre-UTF-8-mode), consistent with what
  g3fix2's own handoff and result already stated and this handoff repeats,
  but not independently re-verified on real Windows in this run.
- That this specific fix, once merged, actually turns the CI trace pasted in
  the handoff from red to green on the real Windows CI runner — inferred
  from the mechanism match (this is the CLI arm of the exact comparison the
  trace's assertion line names, and the demonstration reproduces the trace's
  symptom exactly on real production bytes), not observed on that runner.

## Docs/contracts touched
- none.

## Assumptions
- None beyond the reasoned-about-Windows items above.

## Stop conditions hit
- none.

## Out-of-scope observations
- none. This gate was itself the out-of-scope item a prior crew (g3fix2)
  flagged as triage candidate `tc1`; that candidate is now resolved by this
  change and needs no further routing.

## Workflow Feedback

- **Handoff gaps:** the handoff's suggested demonstration recipe ("Force the
  CLI subprocess to a non-UTF-8 default (e.g. `PYTHONIOENCODING=cp1252` in
  its environment)") does not actually reach the bug site for *this specific
  fix*. `PYTHONIOENCODING` set in a child's env governs that child's *own*
  stdio at its *own* interpreter startup (which is why it worked for
  g3fix2's server-side fix, and why `checklist_engine.py`'s CLI child is
  already immune to it via `_utf8_stdio()`); it does **not** govern
  `subprocess.run(text=True)`'s decode default in the *calling* process,
  which is `locale.getencoding()` and is controlled by locale
  (`LC_ALL`/`LANG`), not `PYTHONIOENCODING`. I verified this empirically
  before building the demonstration differently (see above) rather than
  following the literal recipe into a demonstration that would have silently
  proven nothing (both arms would have matched, since the parent's own
  decode default never changes when only the child's env changes). Worth
  correcting in the doctrine/precedent this "e.g." was drawn from, since the
  next handoff that reuses this phrasing for a decode-side (not encode-side)
  gap will hit the same dead end.
- **Context rediscovered:** the encode-vs-decode distinction above (which
  side of a subprocess boundary an env var or reconfigure call actually
  governs) wasn't explicit anywhere in the handoff or in g3fix2's result —
  I had to re-derive it by reading `subprocess.py`'s own source
  (`_text_encoding()` → `locale.getencoding()`) and testing directly. Since
  this exact class of bug (unpinned `text=True` decode) is likely to recur
  in future gates, it may be worth a durable note (`docs/agents/` or a
  code comment) naming this distinction once, rather than each crew
  re-deriving it.
- **Instructions improvised around:** the plan template's `m1` red-step
  guidance assumes TDD red/green against a test *in the scope file*; since
  the actual required evidence here was an out-of-file demonstration (per
  the handoff's own instruction to demonstrate via a forced-default
  approach, and the constraint that adding a permanent test would change the
  file's pinned 5-test baseline), I treated the demonstration script as the
  red/green evidence and kept the scope file's own change as a single
  test-after step. Both are explicitly sanctioned by the handoff ("If you
  add that as a permanent test, say so; if you run it only as a one-off
  demonstration, say that instead — both are acceptable").
- **What would have made this easier:** naming the encode/decode-side
  distinction explicitly in the handoff (or fixing the `PYTHONIOENCODING`
  example to name which side it applies to) would have saved the
  re-derivation. Otherwise this handoff was tight and correct — small
  single-line fix, clear scope, clear stop conditions.

## Return status
`complete`
