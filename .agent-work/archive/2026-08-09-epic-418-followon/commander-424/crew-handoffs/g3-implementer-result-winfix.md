# Implementation Result

## Assigned gate
`g3fix` — post-archive fix, `epic-418-followon/commander-424`, crew id
`constellation/archive/2026-08-09-epic-418-followon/commander-424/g3fix/implementer/attempt-1`

## Completed slice
Replaced `select.select` on the subprocess stdout pipe in
`tests/test_mcp_identity.py::ServerInstance.recv()` with a portable
daemon-reader-thread + `queue.Queue` bound. `select.select` on Windows accepts
sockets only, so every test in the file errored at setup on Windows CI
(`OSError: [WinError 10038]`); `queue.Queue.get(timeout=...)` is portable
stdlib synchronization, not an OS-level `select()` on a file descriptor.
The `None`-on-any-failure contract (dead process, never-started process,
broken pipe, no reply in time) is preserved exactly — same call signature,
same behavior on every path — and made *stronger* in one respect: after the
child dies, every subsequent `recv()` call returns `None` promptly (a sticky
EOF sentinel put back on the queue) rather than waiting out the full timeout
again.

## Scope
**Files changed:**
- `tests/test_mcp_identity.py` — the only file the handoff put in scope.
- `map/INDEX.md` and `map/tests.test_mcp_identity/**` — regenerated, not
  hand-edited (see "Out-of-scope observations" below for why this was
  necessary).
- `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-plans/g3fix-implementer-plan-winfix.json`
  (+ `.journal`) — my own engine-driven plan.
- `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/g3fix-winfix-recv-portability/**`
  — engine episode-capture bookkeeping (mechanical + context snapshots per
  gate), the same artifact shape the prior `g3-implement-mcp-identity-424`
  gate left and committed.
- `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-runs.json`
  — auto-updated by the harness with this run's registry row.

**Specific exclusions touched:** no. Did not touch
`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `.mcp.json`,
any other test file, or anything under `episodes/`. Did not hand-edit any
checklist JSON — every plan-state change went through the engine's `attest`/
`advance` verbs.

## Behavior changed
Yes, but only the *mechanism* of one private helper, not any observable test
behavior: `ServerInstance.recv()`'s external contract (signature, return
type, `None`-on-failure semantics, the fact that it still bounds rather than
blocking indefinitely) is identical before and after. What changed is *how*
the bound is implemented — thread + queue instead of `select.select` — so it
no longer breaks on Windows.

## Map Impact
- **Structural anchors touched:** `struct:tests.test_mcp_identity.ServerInstance.recv` —
  reimplemented on top of a new private helper, same public contract.
  `struct:tests.test_mcp_identity.ServerInstance.__init__` — now starts a
  daemon reader thread. `struct:tests.test_mcp_identity.ServerInstance.close` —
  now joins that thread (bounded, `timeout=5`) for hygiene. New symbol added:
  `struct:tests.test_mcp_identity.ServerInstance._read_loop`.
- **Capabilities added/changed/affected:** none — `recv()`'s observable
  capability (bounded read of one JSON-RPC reply line) is unchanged; only its
  internal mechanism moved off a POSIX-only primitive.
- **Constraints/assumptions touched:** the original implementer's own named
  assumption — *"`select.select`-based bounded reads are POSIX-only ... not
  tested on Windows"* — is retired by this change; the new mechanism has no
  POSIX-only primitive to retest.
- **Trust limitations / drift found:** the code map's entity count is
  sensitive to adding a private helper method to an already-mapped test
  file. `map/INDEX.md`'s freshness check
  (`tests/test_code_map.py::MapTreeFreshnessTests`) is not itself DC2/DC3
  test coverage but is a real regression gate this change tripped and fixed
  (below) — worth Cartographer/Charter knowing this is a live tripwire on
  *any* future edit to a mapped test file, not just source files.
- **Triage candidates:** `tests/test_mcp_spine_server.py::McpRpcClient.rpc()`
  still does a genuinely unbounded `self.proc.stdout.readline()` with no
  timeout at all (line ~153) — the exact footgun class this file's own
  history warns about (g1's deadlock). It happens not to hang today only
  because that file's own scenarios never construct a dead/never-started
  process the way `test_mcp_identity.py` deliberately does. It was **not**
  in scope here (constraint: "any other test file" is fenced), but it is a
  live latent risk the same shape as the bug this gate just fixed, and I
  flag it for Triage rather than touch it.

## Test mode
**Required:** evidence-only / test-after — no TDD red state exists on this
Linux host for a POSIX-only bug (`select.select` already works correctly on
POSIX pipes, which is exactly why the break was invisible locally in the
first place; see "Local vs. reasoned" below).
**Satisfied:** yes — every claim below is backed by a real command with real
output.

## Local vs. reasoned-about-Windows (explicit split)

**Verified locally (Linux, this run, this host):**
- Pre-fix: `tests/test_mcp_identity.py` was green — 12 passed — confirming
  the bug is invisible on POSIX, exactly as the handoff describes.
- Post-fix: the identity file passes **three consecutive times**, 12/12 each
  run (below) — no reader-thread race observed across repetitions.
- `-k DC2` (5 tests) and `-k DC3` (7 tests) subsets pass explicitly.
- `git diff` of the change touches only `ServerInstance` plumbing (imports,
  `__init__`, new `_read_loop`, `recv`, `close`) — zero lines changed in any
  DC2/DC3 test method body, in `assert_door_is_up_and_serving`, in the DC2
  collision-control test, or in the DC3 ambient-leak counterfactual.
- The timeout bound is demonstrated, not asserted: a never-started process
  returns `None` in 0.006s (EOF path); a genuinely alive but non-replying
  process returns `None` at elapsed 2.000s (the configured bound), and is
  then independently proven still alive via a follow-up `status_text()` call
  that returns the correct marker.
- Full suite matches the stated baseline exactly: 2177 passed, 1 skipped,
  1061 subtests, 0 failed (after the map rebuild described below).

**Reasoned about Windows (NOT run — I have no Windows host available):**
- `queue.Queue.get(timeout=...)` is documented CPython stdlib
  synchronization (a `threading.Condition`/lock under the hood), not an
  OS-level `select()` call on a file descriptor — this is why it is expected
  to be portable where `select.select([pipe], ...)` was not. I am reasoning
  from CPython's documented implementation, not from having executed this
  file on a Windows machine.
- `subprocess.Popen(..., stdin=PIPE, stdout=PIPE, text=True)` plus
  `.readline()`/EOF-on-process-exit semantics are expected to behave the same
  on Windows as on POSIX — this is inferred from Python's own
  platform-independent file-object contract for pipes, and is indirectly
  corroborated by the fact that the handoff's own bug report says only the
  `select.select(...)` line raised `WinError 10038` on Windows CI — every
  other line in this file, including the plain blocking reads that
  `_read_loop` itself now performs, was not reported as failing there.
- Because `select` is no longer imported and `select.select` is no longer
  called anywhere in this file, the specific `WinError 10038` failure mode
  cannot recur — this is a "removed the only call site" argument, not a
  Windows-side observation.
- I cannot verify actual Windows CI behavior for this change; that
  verification happens the next time this branch's PR runs on the real
  Windows CI runner, not in this run.

## Evidence

Baseline, before any change (matches the handoff's stated baseline for the
file):
```bash
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
............                                                             [100%]
12 passed in 0.65s
```

Identity-file run 1/3 (immediately after the `recv()` rewrite):
```bash
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
............                                                             [100%]
12 passed in 0.66s
```
exit 0.

Identity-file run 2/3 (no code changes):
```bash
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
............                                                             [100%]
12 passed in 0.65s
```
exit 0.

Identity-file run 3/3 (no code changes):
```bash
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
............                                                             [100%]
12 passed in 0.64s
```
exit 0.

DC3 subset:
```bash
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py -k DC3 -v
collected 12 items / 5 deselected / 7 selected
tests/test_mcp_identity.py .......                                       [100%]
7 passed, 5 deselected in 0.28s
```
exit 0.

DC2 subset:
```bash
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py -k DC2 -v
collected 12 items / 7 deselected / 5 selected
tests/test_mcp_identity.py .....                                         [100%]
5 passed, 7 deselected in 0.42s
```
exit 0.

Timeout-bound demonstration (scratch script, not committed — imports the
real `ServerInstance`/`write_marked_spine` from the test file, run from
repo root):
```bash
$ python /tmp/.../scratchpad/timeout_demo.py
[never-started]  recv(timeout=2.0) -> None  elapsed=0.006s
[non-replying]   recv(timeout=2.0) -> None  elapsed=2.000s
[non-replying]   server was genuinely alive throughout: status_text() now -> 'RAIL: ... ACTIVE g1 [pending] — MARKER::NON-REPLYING\n...'
OK: bound demonstrated for both scenarios; non-replying server was independently proven alive afterward
```
exit 0. The never-started case hits the EOF/sticky-sentinel path almost
instantly (0.006s), *not* the 2s timeout path — that is expected and
correct: a process that never started exits immediately with an error, so
`recv()` sees EOF, not silence. The non-replying case (a real, live server
that is simply never sent a request) is the one that genuinely exercises the
`queue.get(timeout=2.0)` bound, landing at exactly 2.000s, and the follow-up
`status_text()` call proves that server was never dead — the bound fired
because nothing was sent, not because the process died.

Full suite, immediately before the map rebuild (regression found):
```bash
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
1 failed, 2176 passed, 1 skipped, 1061 subtests passed in 98.27s (0:01:38)
```
exit 1. Confirmed via `git stash` that this failure is **absent** on the
clean tree and **present only** with this diff applied — adding
`ServerInstance._read_loop` shifted the code map's entity count by exactly
1 (3557 → 3558), and `map/INDEX.md` is a generated artifact that must track
the source.

Map rebuild:
```bash
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && python -m scripts.code_map build --root .
```
exit 0. `git status --short -- map/` shows `M map/INDEX.md` (plus the
per-symbol pages under `map/tests.test_mcp_identity/`).

Full suite, after the map rebuild:
```bash
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2177 passed, 1 skipped, 1061 subtests passed in 98.59s (0:01:38)
```
exit 0. **Result: pass — exactly matches the stated baseline** (2177
passed, 1 skipped, 1061 subtests, 0 failed), with the same 12 tests in
`tests/test_mcp_identity.py` passing.

## TDD evidence, if required
Not applicable — evidence-only/test-after mode (see "Test mode" above): no
TDD red state exists on this Linux host for a POSIX-only bug. Refactor while
green: yes — the entire change is a mechanism swap behind an unchanged
public contract, verified green at every one of the three repeated identity-
file runs plus the DC2/DC3 subsets plus the full suite.

## Docs/contracts touched
- `map/INDEX.md` and `map/tests.test_mcp_identity/**` — regenerated
  (generated artifact, not hand-authored prose), required to keep the
  full-suite bar at 0 failed after adding a method to a mapped test file.

## Assumptions
- The three identity-file reruns plus the DC2/DC3 subset reruns plus one
  full-suite run add up to more than three total executions of the file
  under this fix; I did not find any flake across any of them, which is the
  strongest stability signal available on this host.
- `queue.Queue`'s portability is treated as settled CPython stdlib fact, not
  reverified from source in this run.

## Stop conditions hit
- None. No DC2/DC3 guarantee was found weakened; no scope violation; no
  ambiguity requiring escalation.

## Out-of-scope observations
- The map-freshness regression (`tests/test_code_map.py`) was fixed inline
  as a direct, mechanical, one-command consequence of the in-scope change
  (adding a method to a mapped file), matching the "generated artifact →
  regenerate/check evidence" rule in `global-crew.md`. I judged this as
  covered by the handoff's "same bar: 0 failed" requirement rather than a
  scope expansion requiring escalation — flagging it here for visibility
  since the handoff's fenced-file list did not name `map/`.
- `tests/test_mcp_spine_server.py::McpRpcClient.rpc()`'s unbounded
  `readline()` — see "Triage candidates" above. Left untouched (fenced:
  "any other test file"), flagged for Triage.

## Workflow Feedback

- **Handoff gaps:** none material. The handoff was unusually precise about
  what NOT to do (don't remove the timeout, don't weaken DC2/DC3, don't
  touch the fenced files) and about what to prove (three runs, elapsed-time
  demonstration, local-vs-reasoned split) — all four of those were checkable
  against my own output as I went, which is a well-shaped handoff. One small
  gap: the fenced-file list ("do not touch ... or any other test file")
  didn't anticipate that a change confined to the named file could still
  force a `map/` regeneration to hold the "same bar: 0 failed" requirement.
  Not a contradiction — the bar-must-hold instruction and the fenced-file
  list are both satisfiable together, and I judged the map/ rebuild as
  covered by the former rather than blocked by the latter — but a one-line
  "generated artifacts like map/INDEX.md may need a matching rebuild; that's
  in scope" would have removed a moment of genuine hesitation before I
  decided to proceed rather than block.

- **Context rediscovered:** the "house pattern worth matching" pointer in
  the handoff (`tests/test_mcp_spine_server.py` "uses no `select` at all")
  turned out to be true but misleading if followed literally: that file's
  `McpRpcClient.rpc()` has **no bound at all** — a plain unbounded
  `readline()` — which is the exact footgun this whole gate exists to avoid,
  not a portable-and-bounded pattern to copy. It only gets away with that
  because its own test scenarios never construct a dead/never-started
  process. I had to read that file myself to discover this rather than being
  able to trust the pointer at face value; recorded above as a Triage
  candidate so it doesn't quietly become the "house pattern" a future crew
  copies verbatim.

- **Instructions improvised around:** the plan template's TDD-red
  postcondition shape (`c1`: manual attest of "new test written and observed
  failing") doesn't fit a POSIX-only bug with no Linux-observable red state.
  I used the template's own documented escape hatch — "for a test-after/
  inspection run, collapse to the single green/observable postcondition
  (c2)" — and stated why in each item's imperative rather than silently
  omitting `c1`.

- **What would have made this easier:** a standing note (in
  `global-crew.md` or the checklist-engine reference) that a `command`
  postcondition should account for known generated-artifact side effects
  (map/INDEX.md, similar build outputs) when scoping "which files may this
  gate legitimately touch" — right now that judgment call is left entirely
  to the implementer's own reading of `global-crew.md`'s "generated
  artifact → regenerate/check evidence" rule, with no explicit tie-in to the
  fenced-file list a handoff hands down.

## Return status
`complete`
