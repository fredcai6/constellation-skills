# Implementer handoff — post-archive fix: `tests/test_mcp_identity.py` is POSIX-only and reds Windows CI

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g3` (post-archive fix)
**Worktree (work only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door` · **PR #533**
**Authority:** Commander for issue #424, under `LAUNCH_ORDER-424-continuation.md`. That order's
definition of done requires the **PR green**. It is not.

## The break

`tests/test_mcp_identity.py` line 37 imports `select` and line 148 does:

```python
ready, _, _ = select.select([self.proc.stdout], [], [], timeout)
```

`select.select` on Windows accepts **sockets only**, never pipes or file objects. CI runs the suite on
Windows, and every test in that file errors at setup:

```
E  OSError: [WinError 10038] An operation was attempted on something that is not a socket
   tests\test_mcp_identity.py:148: OSError
```

Locally on Linux the whole suite is green (`2177 passed, 1 skipped, 1061 subtests`), so this is
platform-specific and invisible here. The original implementer named the risk honestly in its own
Assumptions — *"`select.select`-based bounded reads are POSIX-only, matching the handoff's 'Host is
Linux' framing; not tested on Windows"* — and the handoff it was working from is what said Linux.
This is my omission, not that crew's.

## Task

Make `ServerInstance.recv()` bounded **portably**, so the file passes on Windows and Linux alike.

## Do not lose the property the `select` call exists to protect

The bound is not decoration. A previous gate on this branch **deadlocked** on an unbounded blocking
pipe read (`assertTrue(line, f"...{proc.stderr.read()}")` evaluates its f-string message
unconditionally, so the blocking read runs even on the success path). This file deliberately
constructs several "the process is dead / never started / serving the wrong thing" scenarios, and an
unbounded `readline()` in any of them is one edge case from repeating that hang.

So the replacement must still return `None` — never block indefinitely — on: a dead process, a
process that never started, a broken pipe, and a process that simply does not reply within the
timeout. **Do not "fix" this by removing the timeout.**

## Suggested approach (a hypothesis, not a spec)

A daemon reader thread per instance feeding a `queue.Queue`, with `queue.get(timeout=...)` as the
bound, is portable and keeps the same call signature. `tests/test_mcp_spine_server.py` uses no
`select` at all and may already show a house pattern worth matching. Choose whatever you can defend —
the requirement is portability plus a real bound, not a particular mechanism.

## Constraints

- Work only in the worktree above; only `tests/test_mcp_identity.py` is in scope.
- **Do not weaken any DC2 or DC3 guarantee.** The DC3 positive control must stay in the assertion
  path and stay able to go red; the DC2 collision control must still reproduce a real lease leak; the
  ambient-leak counterfactual must still prove the no-leak assertion is not vacuous. If your change
  makes any control weaker, stop and say so rather than shipping it.
- Do not touch `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `.mcp.json`, or any other
  test file. Do not touch `settings.json` at any scope.
- Do not hand-edit any checklist JSON or anything under `episodes/`.
- Host is Linux; **the target is Windows CI**, which you cannot run. Say plainly which of your claims
  are verified locally and which are reasoned about Windows behaviour — do not present the second as
  the first.

## Verification

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py -k DC3 -v
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Baseline: **2177 passed, 1 skipped, 1061 subtests, 0 failed.** Your bar is the same, with the same 12
tests in `test_mcp_identity.py` still passing. Run the identity file **three times** — a threaded
reader can pass once and race the next time, and a flaky bound is worse than a POSIX-only one because
it fails somewhere other than where it was introduced.

**Also prove the bound still bounds.** Show `recv()` returning `None` rather than hanging for a
process that never started and for one that does not reply, with the elapsed time, so the timeout is
demonstrated rather than asserted.

## Reporting

Write your `IMPLEMENTER_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-handoffs/g3-implementer-result-winfix.md
```

**Write that file before ending your turn — the write is the delivery.** Include exact commands with
real output and exit codes, the three identity-file runs, the timeout demonstration with elapsed
times, an explicit local-vs-reasoned split for the Windows claims, and a blunt `## Workflow Feedback`
section. Commit to `epic-418/f-424-mcp-door`.
