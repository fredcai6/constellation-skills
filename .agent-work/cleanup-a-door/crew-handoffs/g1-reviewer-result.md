# Review Result

## Assigned Gate
`g1` — issue #604, telemetry-never-fatal.

## Result
`APPROVE`

Survey: `.agent-work/cleanup-a-door/g1-review/review.json` — 7/7 items visited, all `pass`,
consolidated `APPROVE`, no override needed. Fowler record:
`.agent-work/cleanup-a-door/FOWLER_PASS.json` (rail exits 0).

**Read this first: the handoff names commit `8b1d3208`; HEAD is `0060dc08`.** The commit was
amended after the handoff was written. `git diff 8b1d3208 0060dc08` is
`scripts/mcp_spine_server.py` **byte-identical** and `tests/test_mcp_door_telemetry.py` +15
lines — one added test, `test_an_unwritable_call_log_does_not_suppress_the_start_marker`,
which pins the separate guards. The amendment strictly strengthens the change, so it does
not bar the gate. I reviewed HEAD. Every line number below is at `0060dc08`.

## Handoff compliance

All seven close criteria met. Each was reproduced, not read.

**1. The crash reproduces pre-fix and not post-fix, with real subprocess exit codes.**

| tree | probe result | exit |
|---|---|---|
| `a69bbac4` (pre-fix) | `(the server never answered the call)` | `EXIT 1` |
| `0060dc08` (HEAD) | `{"content":[…"FileNotFoundError…"],"isError":true}` | `EXIT 0` |

Same probe, same target (`.agent-work/epic-418-followon/spine.json`, whose directory does
not exist). Post-fix the door answers and both drops are named on `stderr`.

**2. The guard catches `OSError`, not bare `Exception`** — `:213` and `:218`. The width is
right in the other direction too: `json.dumps` at `:209` sits *outside* both guards, so a
programming error still propagates instead of hiding behind a telemetry message.

**3. The loss is reported on `stderr`** — both drops, each carrying the lost record, observed
in the probe above.

**4. No telemetry write remains unguarded — my own count is FOUR filesystem writes**, which
confirms the two prior passes. Enumerated mechanically (an `ast.walk` over the module for
every write-capable call site), not by eye: 12 sites, classifying as 4 filesystem writes and
8 non-filesystem.

| # | site | kind | guarded? |
|---|---|---|---|
| a | `:211-212` `CALLLOG` append | telemetry | yes — `except OSError` `:213` |
| b | `:217` `START_MARKER.write_text` | telemetry | yes — `except OSError` `:218` |
| c | `:527-528` `REJECTIONLOG` append | telemetry | yes — `except OSError` `:529` (pre-existing, #541) |
| d | `:570` `_write_amend_delta` | **functional, not telemetry** | at its call site, `:1324-1330` |

The 8 non-filesystem: `:187`/`:530` `sys.stderr`; `:1402`/`:1410` `sys.stdout` (the protocol
channel); `:485`/`:493` `err.write` into an `io.StringIO` buffer (`:479` — in-memory, cannot
raise `OSError`); and `:212`/`:528`, the `fh.write` halves of (a) and (c).

So **three of three telemetry writes are guarded.** The fourth is deliberately *not*
telemetry and correctly not best-effort — it materialises the delta the engine must then
read, so it must fail the call. I did not take that on reading:

- `spine_amend` against the missing directory → `isError: true`,
  `"spine_amend: could not write delta file: [Errno 2]…"`, **`EXIT 0`**.
- an unknown tool (the only path reaching `_log_rejection`) → `isError: true`,
  `REJECTION CAPTURE FAILED` on `stderr`, **`EXIT 0`**.

Worth naming: the implementer's tests exercise only (a) and (b). Paths (c) and (d) rest on
my probes.

**5. `stdout` stays pure JSON-RPC while telemetry is failing** — and this is not a check that
cannot fail. Mutating `_report_dropped_telemetry` to write to `stdout` turns
`test_stdout_stays_pure_json_rpc_when_telemetry_fails` red.

**6. The test genuinely fails pre-fix — 5 failed, 2 passed.** Matches the commit message.

**7. `SPINE_CALLLOG` / `SPINE_START_MARKER` / `SPINE_REJECTION_LOG` still work.** The three
module-level `os.environ.get` lines (`:162`, `:167`, `:177`) are outside the diff hunk, and
all three overrides are exercised green by `test_mcp_lifecycle.py:102-103`,
`test_mcp_friction_capture.py:99` and `test_mcp_door_telemetry.py:118-120`.

**Stop conditions:** none triggered.

## Scope drift

None. `git show 0060dc08 --stat` is exactly the two files the handoff names, and the server
diff is a **single hunk** (`@@ -177,11 +177,46 @@`), so nothing outside `_log` and the new
helper moved. Every fenced item verified untouched: `_identity_violation`,
`checklist_engine.py`, `scripts/hooks/**`, `run_crew.py`, `gauge_reader.py`, `.mcp.json`,
`examples/mcp-interactive-demo/**`. Both reviewed files are clean in the working tree; the
only modified or untracked paths are under `.agent-work/`.

## Evidence verdict

Sufficient, and it discriminates. Three mutations settle what reading could not:

| mutation | expected | observed |
|---|---|---|
| collapse the two guards into one `try` | separate-guard tests die | **2 failed**, 5 passed |
| reroute the drop report to `stdout` | purity test dies | **2 failed**, 5 passed |
| `_log` returns immediately (writes nothing) | positive control dies | **4 failed**, 3 passed |

Each mutation asserted that it actually applied before running, per the repo's own rule that
a `sed` matching nothing leaves a green suite reading exactly like a passing guard.

The first of those confirms the implementer's separate-guards choice is **pinned, not
decorative** — the claim in the commit message is true.

**The handoff's question — is the second pre-fix pass equally benign, or a check that cannot
fail? Both are benign, and the disclosure was complete.**

- `test_stdout_stays_pure_json_rpc_when_telemetry_fails` passes pre-fix because a dead door's
  `stdout` holds only the `initialize` reply, which is valid JSON-RPC. Disclosed by the
  implementer, and shown above to have a reachable failing state.
- `test_healthy_run_writes_both_telemetry_files` is the **declared positive control**. It is
  *supposed* to pass on both trees — that is precisely how it stops a "fix" that simply
  stopped writing telemetry — and it is documented as such in its own docstring and the
  module docstring. It is not a check that cannot fail: the no-write mutant kills it.

Suite on HEAD: **96 passed, 10 subtests passed** (implementer reported 95 at `8b1d3208`;
the amendment adds one test).

**A departure from the handoff's recipe, deliberately.** Criterion 6 prescribes
`git checkout a69bbac4 -- scripts/mcp_spine_server.py` in place. I did not do that: lanes B
and C are running concurrently in this worktree, and briefly reverting a shared file could
corrupt them. Instead I built an isolated tree with `git archive a69bbac4 scripts`, confirmed
it was genuinely pre-fix (`_report_dropped_telemetry` absent, `_log` unguarded at `:181`/`:184`),
and confirmed `checklist_engine.py` is byte-identical between `a69bbac4` and HEAD so the
engine was not a hidden variable. Same measurement, no shared-tree mutation.

`__pycache__` was cleared before every measurement, in the worktree and both temp trees.
All validation ran against subprocesses I launched, never this session's own door. The suite
ran with `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`.

Evidence artifacts exist and are fresh from this run: `evidence/pre-fix-probes.txt` (05:44),
`post-fix-probes.txt` (05:59), `red-test.txt` (06:04).

## Code/doc quality

Minimal and well-placed. The fix is inside `_log`, so `run_engine`'s call-site contract never
had to move — that it did not is the evidence the change was made at the right level. The
refactoring pass visited all 12 Fowler baseline smells: ten absent, one flagged
(duplicated-code, below), one overridden.

The override is **comments-as-deodorant**. The ratio reads as the smell — `_log`'s docstring
is 15 lines against 11 of code. It is subordinated by `global-crew.md`'s "match the
surrounding code's in-file documentation conventions": this module's convention is uniform
why-first docstrings (`_log_rejection`, `_write_amend_delta`, `_git_rev_parse`,
`_resolve_confined`, `_utf8_stdio`, plus a 60-line module docstring). The reason the standard
wins is that the prose is rationale, not restatement — why `OSError` and not bare `Exception`,
why two separate guards, why `stderr` and never `stdout`, and the #604 history. None of that
is recoverable from the code, which is the line between deodorant and rationale.

## Map impact verdict

- **Evidence supports claimed change:** Yes. `claim:604-kills-the-server` reproduced in both
  directions with real exit codes, by me.
- **Constraints not violated:** `constraint:stdout-is-the-protocol-channel` is honoured and
  now *pinned*, not merely observed — I proved the guarding test goes red when the report is
  rerouted to `stdout`. `constraint:env-overrides-for-log-paths-must-survive` is honoured;
  all three overrides green.
- **Notes match the diff:** Yes. `:180-219` matches the file at HEAD exactly, and the claim
  that `run_engine`'s call site is unchanged holds — the single hunk never reaches it.
- **Decision candidates surfaced:** Yes. `decision:telemetry-never-fatal`
  (`@grade: settled/measured`) implemented as given; the one in-authority choice (separate
  guards) was disclosed and is test-pinned.
- **Durable context routed:** Yes — three triage candidates recorded on the survey, none
  filed as issues.

No architecture-significant graph change: a module-private helper, no interface widened.
Nothing here needs a Cartographer pass.

## Reconciliation check

No divergence for the Commander to reconcile.

Confirmed independently: `map/ids.jsonl` is tracked and **0 bytes**, so no map anchor
resolves anywhere in this repo and every anchor in both handoffs was necessarily verified
against source. This is the handoff's own `tc1` — restated, not re-filed.

## Blockers

- none.

## Out-of-scope observations

Three, all non-blocking, recorded as triage candidates on the survey (`tc1`–`tc3` are the
survey's own numbering, which does **not** line up with the handoff's `tc1`):

1. **`tc1` — CRLF discipline.** `docs/agents/CREW_CONTEXT.md` requires
   `encoding='utf-8', newline='\n'` on **every** write. `_log_rejection` (`:527`) passes
   `newline='\n'`; `_log`'s two writes (`:211`, `:217`) pass encoding only, so on Windows the
   call log and start marker get CRLF while the rejection log gets LF. **Pre-existing** — the
   diff wrapped those calls in guards without altering their arguments and introduced no new
   file write — so not a regression and not a bar to g1.
2. **`tc2` — the empty map.** `map/ids.jsonl` is 0 bytes (confirms the handoff's `tc1`).
3. **`tc3` — duplicated drop report.** `_report_dropped_telemetry` (`:187-191`) and
   `_log_rejection`'s inline `stderr` block (`:530-534`) are the same five lines apart from
   one label (`TELEMETRY WRITE FAILED` vs `REJECTION CAPTURE FAILED`). The implementer
   described the helper as reusing `_log_rejection`'s shape, and it reused that shape by
   copying rather than extracting. One `_report_lost_record(kind, target, exc, lost)` would
   carry both and keep the two diagnostics guaranteed to match. Out of g1's scope: the fix
   would edit `_log_rejection`.

Minor, not filed: the new `_log` docstring cites `run_engine`'s call site as `:461` without
naming a revision. True pre-fix; at HEAD that call is at `:496`, since the change inserted 35
lines above it. The inherited "pin a claim to the revision you read it at" rule applies to
history notes in docstrings too.

## What I did NOT check — scoped nulls

- **Fail-closed refusal wording** for a missing or unbound spine. Fenced to g3 (#603). The
  post-fix probe answering `isError: true` with a raw `FileNotFoundError` is the correct
  outcome *for this gate*, per the handoff, and I did not judge it.
- **Anything under the fenced files** — `_identity_violation`, `checklist_engine.py`,
  `scripts/hooks/**`, `run_crew.py`, `gauge_reader.py`, `.mcp.json`,
  `examples/mcp-interactive-demo/**`. I confirmed they were untouched; I did not review them.
- **Windows behaviour.** Every measurement here is Linux, Python 3.12.3. The
  `IsADirectoryError`-vs-`PermissionError` shade the test docstring names is unverified on
  Windows, and so is `tc1`'s CRLF claim, which is reasoning from the documented rule rather
  than an observation.
- **Whether this local green matches CI's pin.** Local pytest is 9.1.1; per
  `CREW_CONTEXT.md`, a local green is evidence, never the gate.
- **Concurrency.** Two `_log` calls racing on the same append are not exercised by any test
  here, and I did not test them. Out of scope for #604 — but the door is a single-threaded
  stdio loop, so this is a note about coverage, not a suspected defect.

## Workflow Feedback

- **Handoff gaps:** The **`## What was implemented` section named a commit that was no longer
  HEAD** (`8b1d3208` vs `0060dc08`), along with a stale line count (247 vs 262) and a stale
  pre-fix tally (`4 failed, 2 passed` vs the actual `5 failed, 2 passed`). Everything I was
  told to inspect via `git show 8b1d3208` was therefore one revision behind the tree I was
  told to test. It was benign here, but a reviewer who trusted the pinned commit and skipped
  `git log` would have reviewed a superseded artifact and never known. If a handoff pins a
  commit, something should re-read it at dispatch time — or it should pin the *branch* and
  state the commit as "at time of writing."
- **Context rediscovered:** Criterion 4's cited line numbers (`:181`, `:184`, `:492`, `:535`)
  are **pre-fix** coordinates presented without saying so; at HEAD the same four writes are at
  `:211`, `:217`, `:527`, `:570`. I had to work out which revision they belonged to before I
  could tell whether I was confirming or refuting the count. Also: criterion 4 says "no
  *telemetry* write remains unguarded" but the count of four includes `_write_amend_delta`,
  which is not telemetry and must *not* be best-effort. The criterion and its count are
  measuring two different sets, and reconciling that was most of the work on that item.
- **Instructions improvised around:** Two. (1) The reviewer skill says a dispatched crew's
  bound spine is its checklist and not to author a survey — but `SPINE_FILE` here is the
  **Commander's gated `execute` spine**, under the Commander's own active lease, whose active
  gate is `execute`. `spine_survey_result` is survey-only and driving that spine's gates would
  have meant advancing my parent's work. I called `spine_status` first as instructed, read
  that it was not a review survey, and built my own at the workbench path
  `.agent-work/cleanup-a-door/g1-review/review.json`. The skill has no branch for "a spine is
  bound, but it is not yours." (2) Criterion 6's in-place `git checkout` recipe conflicts with
  the handoff's own statement that lanes B and C run concurrently in this worktree; I used an
  isolated `git archive` tree instead, as recorded above.
- **What would have made this easier:** One concrete engine bug worth fixing: driving my
  survey at `.agent-work/cleanup-a-door/g1-review/review.json` made `checklist_engine.py`
  create a **nested** work root at `.agent-work/cleanup-a-door/cleanup-a-door/`, containing
  `context/r0-context.json` and `mechanical/r0-context.json`. The per-gate packets the
  Commander wrote sit at `.agent-work/cleanup-a-door/context/`, one level up. The work-root
  resolution is doubling the work-id when the checklist lives in a subdirectory of its own
  work area, and it leaves untracked scratch that closeout will read as an orphan.

## Return status
`complete`
