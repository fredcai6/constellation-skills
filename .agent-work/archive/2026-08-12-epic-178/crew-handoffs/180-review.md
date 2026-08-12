# Review: #180 — gauge writer PostToolUse hook (epic-178, Module 2 write side)

**VERDICT: APPROVE**

Reviewer: independent clean-room review, dispatched by the Admiral (constellation-reviewer role). No code written by this reviewer.

## Isolation

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-180-rev
worktree OK: in C:/Programs/constellation-wt-180-rev
```

Worktree at PR tip `c33050f` (detached), parent `54f5965` as expected.

## Diff scope

```
$ git diff 54f5965...HEAD --stat
docs/GAUGE_WRITER_HOOK.md              | 209 ++++++++++++++++++++++
scripts/hooks/gauge_writer_hook.py     | 258 ++++++++++++++++++++++++
tests/fixtures/golden_transcript.jsonl |   5 +
tests/test_gauge_writer.py             | 276 ++++++++++++++++++++++++++++
4 files changed, 748 insertions(+)
```

Exactly the 4 new files claimed, nothing else touched. Confirmed `spine_rail.py`, `gauge_reader.py`, `checklist_engine.py` all have empty diffs against the parent. Confirmed no `*settings.json*` path appears in the diff at all (empty stat) — the HITL wiring genuinely was not applied anywhere in-repo, only documented. This is correct behavior per the launch order, not a defect.

## Per-criterion

**1. Well-formed record from the golden transcript — PASS.**
`test_golden_fixture_produces_well_formed_record` asserts `set(record.keys()) == {"schema_version","fill_fraction","model","observed_at"}` (exactly 4, no extras) and `0.0 <= fill_fraction <= 1.0`. The fixture's matching line (`tests/fixtures/golden_transcript.jsonl:5`) itself carries extra keys under `message` (`server_tool_use`, `service_tier`) that are correctly *not* leaked into the record — good evidence the hook only ever emits its 4 frozen fields regardless of what's in the source line.

**2. Parse failure leaves prior gauge file untouched — PASS.**
`test_parse_failure_leaves_prior_gauge_file_untouched` and `test_transcript_with_no_usable_usage_leaves_prior_file_untouched` both seed a real prior `gauge.json`, feed a bad/empty transcript, and assert the file is byte-equal (via re-parsed JSON) to the seeded prior. Also covered: missing `transcript_path` key, nonexistent file path, and no session→spine binding — each asserts no file is written at all (not even a first write). Traced the code (`gauge_writer_hook.py:209-226`): every one of these returns `{}` before reaching `_atomic_write_json`. No placeholder/zero path exists in `compute_record` — it returns `None` on any uncertainty, which short-circuits the write.

**3. Atomic write / no torn reads (TF9) — PASS, this is the strong part.**
`test_concurrent_reads_never_observe_a_torn_record` (`tests/test_gauge_writer.py:196-252`) spins a real writer thread doing 200 rapid `_atomic_write_json` calls alternating between two distinct records, and a real reader thread hammering `read_text` + `json.loads` + key-set check concurrently, for up to 30s each. This is genuine concurrent thread scheduling, not a code-inspection stand-in — confirmed by reading it line by line. Re-ran the full suite 4 times and the concurrency test in isolation 3 additional times (7 total passes, 0 flakes, ~1.7-2.0s each):
```
== run 1 ==  ............  12 passed in 1.79s
== run 2 ==  ............  12 passed in 1.77s
== run 3 ==  ............  12 passed in 1.68s
(isolated -k concurrent, x3): 1 passed in 1.66s / 1.47s / 1.70s
```
The write primitive itself (`_atomic_write_json`, `gauge_writer_hook.py:199-204`) is genuinely tmp+`os.replace` — never an in-place open-write-truncate on the target path. `os.replace` is atomic on both POSIX and Windows (`MoveFileExW` + `MOVEFILE_REPLACE_EXISTING` under the hood), so the guarantee holds on this platform.

**4. Wiring documented, not applied — PASS.**
`docs/GAUGE_WRITER_HOOK.md` §"The human action (HITL seam)" gives the exact `settings.json` snippet (new `PostToolUse` matcher `"*"` entry, added alongside the existing `spine_rail.py` `"Bash"`-matcher entry, not replacing it) plus a 3-step manual verification procedure. No real `settings.json` anywhere was touched (confirmed above via diff). Correctly scoped as HITL and correctly *not* claimed as done.

## Specific probes

**Fail-open / never blocks:** every public entry point (`handle_post_tool_use`, `main`) wraps its body in `try/except Exception: return {}` / `return 0`. `main()` also wraps `json.loads(stdin_text)` separately and falls back to `{}` on bad stdin — verified by `test_main_malformed_stdin_fails_open`, which feeds literally `"{ not json"` and asserts `rc == 0` and no stdout. Could not find a path that raises out of the hook or blocks the tool call.

**Frozen record fidelity:** `compute_record` (`gauge_writer_hook.py:175-194`) constructs the dict as a literal with exactly the 4 keys — no code path appends a 5th field or omits one. Confirmed by the exact-keyset assertions in both golden-fixture tests.

**fill_fraction bounds:** `fill = max(0.0, min(1.0, total_tokens / window))`. Traced NaN/Infinity edge cases by hand (Python's permissive `json.loads` accepts `NaN`/`Infinity` literals): because Python's two-arg `min`/`max` are asymmetric and only compare via `<`, `min(1.0, nan)` evaluates to `1.0` (since `nan < 1.0` is `False`, the first operand is kept) and the subsequent `max(0.0, ...)` behaves correctly too — so even a NaN/Inf token count clamps to a value in `[0,1]` rather than propagating NaN into the record. `window` is guarded (`if not window or window <= 0: return None`) so there's no division-by-zero path, and `MODEL_WINDOWS`/`DEFAULT_WINDOW` are always positive constants. Unknown model correctly falls back to `DEFAULT_WINDOW` (200_000) rather than guessing 0 — verified by `test_unknown_model_uses_default_window`. This is a genuinely defensive normalization; no bounds violation found.

**File fence:** confirmed via `git diff` above — the three named files are untouched.

## One non-blocking finding

**LOW — test docstring overclaims what it verifies (test-coverage gap, not a functional bug).**
`test_golden_fixture_picks_latest_main_chain_usage_not_sidechain` (`tests/test_gauge_writer.py:75-91`) says the sidechain line "has a bigger and chronologically-later usage total than the real latest main-chain line — if the writer picked it up by mistake, model/fill would differ." Tracing the actual fixture: the sidechain line is `golden_transcript.jsonl:4` (`timestamp: 11:59:00`), and the correct main-chain answer is `golden_transcript.jsonl:5` (`timestamp: 12:00:00`) — which is both **later in the file and later in time** than the sidechain line. Because `_iter_tail_lines_reverse` yields lines in reverse file order, the correct answer (line 5) is the *first* candidate the reverse scan encounters and it matches immediately — `find_latest_usage` returns before the scan ever reaches line 4, so the `d.get("isSidechain")` → `continue` branch (`gauge_writer_hook.py:143`) is never actually exercised by this test.

Read the code path by hand to confirm correctness anyway: on a genuine hit (`type == "assistant"` and `isSidechain` falsy) it returns immediately; on a sidechain hit it falls through to `continue` and keeps scanning further back — so if a *more recent* sidechain line existed after the true answer, the loop would correctly skip past it. The logic itself is right; only the claimed test coverage for that specific branch is missing.

**Suggested fix (non-blocking):** reorder the fixture so the sidechain assistant line is the *last* line in the file (after the true main-chain answer), which would force the reverse scan to actually visit and skip it before finding the correct one. This doesn't affect this review's verdict — it's a test-quality nit for a future pass, not a defect in the shipped hook.

## Independent test run (full suite)

```
$ py -u -m pytest tests/test_gauge_writer.py -q
............                                                             [100%]
12 passed in 2.03s
```
Repeated 3 more times (see above), all green, no flakiness observed.

## Summary

All four acceptance criteria hold under independent, adversarial re-verification — including re-running the concurrency test multiple times specifically to rule out flakiness, and hand-tracing the fail-open and bounds-clamping paths rather than trusting the docstrings. The one finding is a test-coverage nit (a docstring's claim doesn't match what its fixture actually exercises), not a functional defect, and does not block. The HITL settings.json wiring is correctly left undone and correctly documented — not treated as a defect, per the review scope.
