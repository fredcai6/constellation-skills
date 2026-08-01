# Result: #180 — Gauge writer (Claude Code PostToolUse hook + golden fixture)

## Verdict: DELIVERED, built to the HITL seam. No blockers, no floats.

The X2 strategic-compact technique is no longer just "confirmed buildable but
never run against the real harness" (the launch order's stated uncertainty).
During implementation it was hand-verified against **this machine's own
live, in-progress Claude Code session transcript** (not just the fixture) —
the real schema matched exactly what the writer depends on, and the sum
technique produced a sane, plausible fill number against a real ~150k-token
session. That's a positive, measured result, not a fake one — full detail in
`docs/GAUGE_WRITER_HOOK.md`'s "Validated against a real transcript" section.

## `--here` isolation output

```
worktree OK: in C:/Programs/constellation-wt-180
```

## Test command + full output

```
$ py -u -m pytest tests/test_gauge_writer.py -q
............                                                             [100%]
12 passed in 1.77s
```

Re-ran 3x back-to-back (no `--timeout` plugin installed, so no artificial
per-test timeout) to rule out flakiness in the concurrency (TF9) test: 12
passed each time, 1.75s / 2.07s / 2.16s.

Sibling module sanity check (spine_rail.py is imported/reused, not
modified — confirmed still green):

```
$ py -m pytest tests/test_spine_rail.py -q
.................................                                        [100%]
33 passed in 2.23s
```

## Files changed + diffstat

New files only (file fence honored — `checklist_engine.py`, `gauge_reader.py`,
and `spine_rail.py` all untouched; `scripts/gauge_reader.py` does not even
exist in this worktree, confirmed by directory listing):

```
 docs/GAUGE_WRITER_HOOK.md              | (new)
 scripts/hooks/gauge_writer_hook.py     | (new)
 tests/fixtures/golden_transcript.jsonl | (new)
 tests/test_gauge_writer.py             | (new)
 4 files changed, 748 insertions(+)
```

Commit `c33050f` on branch `epic178-180-gauge-writer` (base `54f5965`).

## PR

https://github.com/fredcai6/constellation-skills/pull/186

(Note: `gh pr create` was transiently denied by the auto-mode permission
classifier on the first attempt with "Blocked by classifier" — no code or
policy issue, a retry of the identical command succeeded immediately. Same
transient denial hit a plain read-only `git log`/`git diff --stat` afterward;
noting it here only because it's a session-classifier quirk worth knowing
about, not a repo or implementation problem.)

## What was built

- **`scripts/hooks/gauge_writer_hook.py`** — the `PostToolUse` hook.
  Resolves `.agent-work/<work_id>/gauge.json` by reusing
  `spine_rail.py`'s existing session→spine binding (loaded by file path,
  not re-derived); parses the transcript's tail (bounded 2MB reverse scan,
  not a full-file parse) for the latest non-sidechain assistant `usage`
  record; sums `input_tokens + cache_creation_input_tokens +
  cache_read_input_tokens`; normalizes by a per-model context-window table
  (`MODEL_WINDOWS`, all current models at 200k, calibration-TBD comment);
  atomically writes the frozen 4-field record via tmp+`os.replace`.
  Skip-on-uncertainty at every failure point — never fabricates.
- **`tests/fixtures/golden_transcript.jsonl`** — a 5-line hand-built
  transcript modeled directly on the real schema validated live (see
  below), including a deliberate sidechain (subagent) usage record that is
  chronologically later and numerically bigger than the real answer, to
  positively test that sidechain filtering works and isn't accidental.
- **`tests/test_gauge_writer.py`** — 12 tests: well-formed write from the
  golden fixture; sidechain-is-ignored (with hand-computed expected
  fill_fraction); parse-failure-leaves-prior-file-untouched (two variants:
  corrupt JSON, and well-formed-but-no-usable-usage); missing
  transcript_path / nonexistent transcript file / no binding all skip
  cleanly; unknown model falls back to the default window; atomic
  tmp+rename write primitive; and the TF9 concurrency test (real threads,
  not just code inspection — see "one real bug found and fixed" below).
- **`docs/GAUGE_WRITER_HOOK.md`** — wiring, the HITL human-action section,
  the real-transcript validation writeup, the exact format-drift table
  (every field/path this parser depends on), the skip-on-uncertainty
  enumeration, and the bounded-tail-scan rationale.

## One real bug found and fixed during self-testing (worth flagging)

The first version of the TF9 concurrency test hung the whole pytest process
indefinitely. Root cause: if a writer's `os.replace` call hit a transient
Windows sharing violation, the writer thread died without ever calling
`stop.set()`; the reader thread's tight polling loop then spun forever, and
because both threads were non-daemon, the Python process could never exit
even after the test itself would otherwise have finished. Fixed by wrapping
the writer's per-iteration work in `try/except OSError` with `stop.set()` in
a `finally`, and marking both threads `daemon=True` as a safety net. Not a
bug in the hook itself (the hook always catches its own I/O errors) — a bug
in my own first test harness, caught by actually running it rather than
trusting the design. Left in the artifact trail in case it's a useful lesson
candidate (test-harness threads doing real concurrent file I/O need the same
fail-safe discipline as the production code they're testing).

## Human action — HITL seam (build ends here)

Everything up to this point is built, tested, and does not need you. Three
things do:

### (a) The exact `settings.json` snippet

Add this as an **additional** `PostToolUse` entry (alongside the existing
`spine_rail.py` one — don't replace it) to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {"matcher": "Bash", "hooks": [{"type": "command", "command": "py \"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\" PostToolUse", "timeout": 10}]},
      {"matcher": "*", "hooks": [{"type": "command", "command": "py \"${CLAUDE_PROJECT_DIR}/scripts/hooks/gauge_writer_hook.py\"", "timeout": 10}]}
    ]
  }
}
```

Matcher is `"*"` (every tool call), unlike `spine_rail.py`'s `"Bash"`-only
matcher, because fill has to be tracked continuously regardless of which
tool ran.

### (b) One real tool call to confirm it

1. Make sure a spine is claimed in your session (any normal Constellation
   run already does this).
2. Run any tool call.
3. Check `.agent-work/<work-id>/gauge.json` (sibling to that run's
   `spine.json`) — should now exist:
   `{"schema_version": 1, "fill_fraction": 0.34, "model": "claude-opus-4-8", "observed_at": "..."}`.
4. Run a few more tool calls and re-check — `observed_at` should advance,
   `fill_fraction` should trend upward.

### (c) What "looks right" means

Four fields, no extras; `fill_fraction` in `[0,1]` trending up within one
continuous stretch of work (small jitter fine); `model` matches what you
were talking to; `observed_at` close to "now," not stale. Full detail —
including what a *broken* reading looks like (flat/stuck, or wildly
discontinuous) — is in `docs/GAUGE_WRITER_HOOK.md`.

No real `settings.json` (global or this repo's project-local one) was
touched by this implementation — that edit is entirely yours to make.

## Floats / map-impact / triage

None. The session→spine binding existed and was reused as instructed (no
invented fallback mechanism needed). No change to the frozen record format.
No spec contradiction encountered. Nothing to triage as a separate follow-up
beyond what's already named in the format-drift note (the "silence is the
detection signal" risk for future transcript-format drift, which the epic
already scopes as accepted/out-of-scope for v1 automated alarming).

## Rework 1 (reviewer finding, closed)

Independent review of PR #186 = APPROVE, with one non-blocking test-coverage
nit: `test_golden_fixture_picks_latest_main_chain_usage_not_sidechain`
claimed to test that a sidechain (subagent) usage record is correctly
skipped, but in the original fixture the sidechain line (line 4, 11:59:00)
came *before* the true main-chain answer (line 5, 12:00:00) in file order.
Since `_iter_tail_lines_reverse` scans from the end of the file, it matched
line 5 immediately and never reached line 4 at all — so the
`isSidechain`-skip branch in `find_latest_usage` (gauge_writer_hook.py:143)
was never actually executed by the test, despite the docstring's claim.

**Fix:** reordered `tests/fixtures/golden_transcript.jsonl` so the true
answer (now line 4) is followed by two trailing sidechain turns (lines
5-6 — later in file order AND in time, with bigger usage totals) that the
reverse scan must skip past to reach the answer. This also more accurately
models the real Claude Code transcript shape: a subagent's sidechain
entries append at the point of the `Agent`/`Task` tool call, and
`PostToolUse` can fire while those trailing sidechain lines are the most
recent thing in the file, before the main chain has spoken again — exactly
the case that needs the skip to work correctly. Added a second assertion
comparing against the sidechain's own (larger) fill value, so a future
regression that silently stops skipping produces a value clearly above the
expected one, not just a wrong-but-plausible number.

**Verified the fix actually tests what it claims**, not just that it
passes: temporarily disabled the `isSidechain` check in
`gauge_writer_hook.py`, re-ran `py -m pytest tests/test_gauge_writer.py -q
-k sidechain`, confirmed it now fails (`assert 'claude-sonnet-5' ==
'claude-opus-4-8'`), then restored the real implementation via `git
checkout -- scripts/hooks/gauge_writer_hook.py` (confirmed zero diff
against the last commit) and reran the full suite green.

```
$ py -u -m pytest tests/test_gauge_writer.py -q
............                                                             [100%]
12 passed in 1.51s
$ py -u -m pytest tests/test_spine_rail.py -q
.................................                                        [100%]
33 passed in 1.05s
$ git status --porcelain
 M tests/fixtures/golden_transcript.jsonl
 M tests/test_gauge_writer.py
```

Commit `d15ee77` on `epic178-180-gauge-writer`, pushed
(`c33050f..d15ee77`). File fence held — only the fixture and test file
touched, exactly as the rework request scoped it. PR #186 updated; no new
floats.
