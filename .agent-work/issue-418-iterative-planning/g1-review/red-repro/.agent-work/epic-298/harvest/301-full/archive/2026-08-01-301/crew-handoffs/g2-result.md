# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

VERDICT: COMPLETE

## Assigned gate
`g2` — the validated episode writer (issue #301, epic-298) — **REWORK** of a BLOCKed
review (`.agent-work/301/crew-handoffs/g2-review-result.md`), addressing the two
demonstrated defects the Commander reproduced.

## Completed slice
Fixed both BLOCK defects in `scripts/apply_episode_delta.py`, added tests proving
each fix, swept the module for the same defect class, and reverified the full gate
contract (three negation fixtures, full suite, clean `git status`).

## Scope
**Files changed:**
- `scripts/apply_episode_delta.py` — `_reject_newline()` predicate redefinition;
  `_Transaction.commit()` stage-then-move rewrite; `main()`'s error-message split.
- `tests/test_episode_store.py` — new `LineBoundaryGuardTests` and
  `WritePhaseAtomicityTests` classes (existing 18 tests untouched, not restructured).

**Specific exclusions touched:** no. The retirement layout placeholder
(`_LAYOUT_ADAPTER = _LAYOUT_OPTION_B`) is byte-for-byte unchanged; `durable_root()`
is still never called; `apply_lessons_delta.py` and `.agent-work/LESSONS.md` were not
touched; the three fixtures remain at their exact existing paths, untouched.

## Behavior changed
Yes:
1. A free-text agent-supplied value containing `\v`, `\f`, `\x1c`-`\x1e`, `\x85`
   (NEL), U+2028, or U+2029 — anywhere in the string, including a trailing position
   — is now rejected at validation time instead of silently corrupting the episode
   on its next parse.
2. A real OS-level failure on the write phase (2nd+ of N touched files) now leaves
   the store byte-for-byte unchanged instead of leaving earlier writes landed on
   disk. The CLI's error message for this case is now honest (`"write failed, store
   left unchanged"`) instead of the previous misleading `"cannot read delta"`.

## Defect 1 — silent data corruption (newline guard vs. `splitlines()`)

**Root cause confirmed exactly as reviewer-reported:** `parse_episode()` sections
the file with `str.splitlines()`, which treats a wider character set as line
boundaries than the old guard's literal `"\n" in value or "\r" in value` check.

**Fix (`scripts/apply_episode_delta.py`, `_reject_newline`):**

```python
if value != "" and value.splitlines() != [value]:
    raise EpisodeDeltaError(...)
```

**Exact predicate and why:** `value.splitlines() != [value]`, guarded by an
explicit `value != ""` carve-out. Chosen over the handoff's suggested
`len(value.splitlines()) > 1` because that form alone misses the trailing-separator
case: `"text ".splitlines()` is `["text"]` — length 1, so a length check alone
would wrongly accept it, even though the trailing separator is silently dropped on
the next parse exactly like an embedded one. Comparing the whole list
(`!= [value]`) catches both the multi-segment case AND the trailing case in one
predicate, because *any* character `splitlines()` treats specially — embedded or
trailing — makes the round-trip `splitlines() -> [value]` fail to reproduce the
original string. The one correction needed on top of that: `"".splitlines()` is
`[]`, not `[""]`, so the bare predicate would wrongly reject the empty string
(several optional fields legitimately pass `""`) — hence the explicit `value != ""`
short-circuit, which is the only special case, not a parallel character list.

This ties the guard's own boundary definition to the **same function** the parser
uses (`str.splitlines()`), so the two literally cannot drift apart again — closing
the class, not one more character at a time. That reasoning is now in the code as
an in-line comment on `_reject_newline`, and the function's docstring is updated to
match (both explain WHY the predicate is defined via the parser's own behavior
rather than an enumerated character list).

**Tests added** (`LineBoundaryGuardTests` in `tests/test_episode_store.py`):
- `test_reject_newline_unit_rejects_every_splitlines_boundary_character` — one
  subtest per non-`\n`/`\r` boundary character (`\v`, `\f`, `\x1c`, `\x1d`, `\x1e`,
  `\x85`, U+2028, U+2029), embedded mid-string.
- `test_reject_newline_unit_rejects_trailing_separator` — same 8 characters, this
  time as the LAST character of the value (the case a naive length-based fix would
  miss).
- `test_reject_newline_unit_still_accepts_a_genuinely_single_line_value` —
  no-regression check on the happy path.
- `test_u2028_forged_status_line_end_to_end_create_rejected` — **end-to-end**: a
  `create` op's `observed-behavior` statement embeds a literal `"- status:
  retired"` line using U+2028 as the separator (the reviewer's exact
  reproduction). Asserts the whole CLI call exits 1 AND that no file is written
  (the attack never lands on disk even transiently).
- `test_u2028_forged_status_line_end_to_end_amend_history_rejected` — same attack
  shape via `amend-assertion`'s `history` field.

**TDD red, proved honestly:** ran the new tests against the OLD `\n`/`\r`-only
guard first — 18 failures (16 subtests across the two character-sweep tests, plus
both end-to-end tests), including the end-to-end create test failing with
`AssertionError: 0 != 1` — i.e. the delta was silently ACCEPTED and the file WAS
written, reproducing the reviewer's exact finding. Then implemented the fix; full
`LineBoundaryGuardTests` class now green.

## Defect 2 — write-phase atomicity gap

**Root cause confirmed exactly as reviewer-reported:** `_Transaction.commit()`
called `path.write_text()` directly on each final path, in sequence, with no
staging. A failure on the 2nd of 2 writes left the 1st file's write landed on disk.

**Fix (`scripts/apply_episode_delta.py`, `_Transaction.commit()`):** stage every
touched file to a temp path in the **same directory** as its final destination
(same store root, same filesystem) via `Path.write_text`; only once **every**
staged write has succeeded does it move each staged file into place via
`os.replace()` (atomic for a single file, on both POSIX and Windows). Any staging
failure removes every temp file already written and re-raises without ever
touching a final path.

**Honesty note (in-code comment, not overclaimed):** the move loop across N staged
files is **not** atomic as a whole — only each individual `os.replace()` call is.
A crash between the 1st and 2nd move can still leave a partial result on disk.
There is no journal/WAL available under `EPISODE_STORE.md`'s markdown-in-git
constraint to close that residual gap, so this is the best available guarantee for
the write step, stated as such rather than claimed as full multi-file atomicity.

**Side fix, same investigation:** `main()`'s single `except (OSError,
json.JSONDecodeError)` block wrapped both delta-file reading AND `apply_delta()`
(the write phase), so a write-phase `OSError` printed the misleading `"error:
cannot read delta"` — the delta had, in fact, been read fine. Split into two `try`
blocks so a write-phase failure now reports `"error: write failed, store left
unchanged"`. This surfaced directly from the TDD-red run below (see captured
stderr) and is in scope of defect 2's own code path — not a separate expansion.

**Test added** (`WritePhaseAtomicityTests` in `tests/test_episode_store.py`):
`test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged`
— seeds one pre-existing episode, snapshots every file under the store root
(path -> bytes), then runs a delta with two individually-valid ops touching two
different files (an amend on the pre-existing episode, a create of a new one).
Monkeypatches `Path.write_text` to raise on exactly the 2nd call made after the
delta file itself is written (so the delta-file write is never counted), forcing a
failure regardless of whether the implementation writes directly to the final path
or via a staged temp path. Asserts the CLI still exits 1 and that the full
before/after directory snapshot (content **and** the exact set of files present) is
identical.

**TDD red, proved honestly:**

```
AssertionError: {Wind[1331 chars]ing: active\n...'} != {Wind[1331 chars]ing: disputed\n...'}
...
Captured stderr call
error: cannot read delta: simulated write failure (e.g. disk full) on the second touched file
```

— against the OLD sequential `commit()`, the pre-existing episode's file WAS
mutated on disk (the diff shows `lifecycle-standing: active` vs `disputed`) even
though the whole delta was rejected, reproducing the reviewer's exact finding —
plus the misleading stderr message. Then implemented the fix; the test is now
green with the store snapshot identical before/after.

## Sweep for the same defect class

Both defects share one root cause: an invariant enforced in one place using a
DIFFERENT definition than the place that depends on it. Swept every
`re.compile`/`.strip()`/`write_text`/`read_text` site in
`scripts/apply_episode_delta.py`:

- **All free-text values that reach a rendered store line** (mechanical scalars,
  `artifact-ref` entries, assertion `statement`/`history`, retire
  `reason`/`retired-at`/`consolidated-into`/`superseded-by`) were traced call-site
  by call-site — every one routes through `_reject_newline` before it is ever
  written. No gap found.
- **`ID_RE`/`RUN_RE`** (validate op-supplied ids) vs. `_next_episode_id()`'s actual
  construction (`run + "-" + zero-padded sequence`): the regexes are stricter-or-
  equal to what the writer ever constructs, and `run` is independently
  double-guarded — both `RUN_RE.fullmatch()` AND `_reject_newline()` run against it
  (via the mechanical-fields validation loop). No gap; also confirmed `ID_RE`'s
  charset excludes path-traversal characters (`/`, `..`), so an attacker-supplied
  `amend`/`retire` id cannot escape the store directory.
- **`FIELD_RE`/`ASSERTION_HEADING_RE`/`HEADER_RE`** (parse-side) vs.
  `render_episode()`'s actual output: every rendered `"- key: value"` line's value
  is guard-clean (single-line) by construction after the defect-1 fix, so
  `FIELD_RE`'s per-line assumption always holds; the assertion heading's
  `<id>.<aid>` tokens are writer-controlled, never free text.
- **`str.strip()` vs. the newline guard**: Python classifies several
  `splitlines()`-boundary characters (`\x1c`-`\x1e`, `\x85`, U+2028, U+2029) as
  whitespace, so a value that is *only* a boundary character is caught earlier by
  `_require_str`'s `not value.strip()` empty-check (different message, still a
  correct rejection); a value with real content plus a boundary character reaches
  `_reject_newline` and is caught there. Verified both paths reject — no silent-
  accept gap either way.
- **Noted, not fixed** (pre-existing, unchanged by this rework, low risk): in the
  new `commit()`, `final_path.parent.mkdir(parents=True, exist_ok=True)` runs
  before that file's staged write, so a staging failure on write N can leave an
  empty directory created for write N's parent. This is only reachable under the
  not-yet-ratified Option-A layout (which creates `active/`/`retired/`
  subdirectories) — an empty, untracked directory, not corrupted data. This exact
  `mkdir` call existed in the OLD sequential `commit()` too (same line, same
  ordering relative to the write it guards), so it is not a regression introduced
  by this rework. Flagged as a cheap future tidy (e.g. only `mkdir` once a write is
  about to move into place), not a live risk.

No other instances of the class were found. No additional code changes were made
beyond the two defects already fixed above.

## Test mode
**Required:** test-first (TDD) — inherited from the g2 handoff, unchanged by this
rework.
**Satisfied:** yes. Both new test classes were run against the OLD, unfixed code
first and observed failing for the exact reason the reviewer described (pasted
above), then the fix was implemented and the tests turned green.

## Evidence

```bash
$ python -m pytest tests/test_episode_store.py -q
........................                                 [100%]
24 passed, 16 subtests passed in 0.30s
```

```bash
$ python -m pytest tests/ -q
........................................................................ [ 57%]
........................................................................ [ 63%]
............................................................ [ 68%]
................................................................ [ 74%]
........................................................................ [ 80%]
........................................................................ [ 86%]
........................................................................ [ 92%]
..........................................................s........s.... [ 98%]
...................                                                      [100%]
1181 passed, 2 skipped, 276 subtests passed in 31.61s
```
(Baseline named in the handoff: 1157 passed + 2 skipped; this run adds 24 new test
methods in `tests/test_episode_store.py` — up from the pre-rework 18 — accounting
for the 1181 total, plus 276 subtests from the two new parametrized test methods.)

```bash
$ python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/misfiled-field-delta.json
error: create: misfiled field 'lifecycle-standing' under mechanical — not a recognized mechanical field (allowed: run, project, role, spine-step, context-manifest-ref, refusals, reopens, rework-count, failed-commands, artifact-ref). Agent-supplied fields belong under agent_supplied/diagnosis, never mechanical.
exit=1

$ python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/missing-retire-reason-delta.json
error: retire: reason is required
exit=1

$ python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/newline-injection-delta.json
error: create.agent_supplied.observed-behavior.statement: value must be a single line (no embedded or trailing line boundary) — a multi-line value could forge a store field once rendered
exit=1
```

```bash
$ git status --short
?? scripts/apply_episode_delta.py
?? tests/fixtures/episodes/
?? tests/test_episode_store.py

$ ls episodes/
README.md
```
Only the three documented paths appear; `episodes/` itself holds only its
pre-existing `README.md` — clean, exactly as before.

## TDD evidence, if required

- Failing test observed (defect 1, against old guard): 18 failed (16 subtests + 2
  end-to-end), including `AssertionError: 0 != 1` on
  `test_u2028_forged_status_line_end_to_end_create_rejected` — the delta was
  accepted and the file written.
- Failing test observed (defect 2, against old `commit()`):
  `AssertionError: {Wind[1331 chars]...active...} != {Wind[1331 chars]...disputed...}`
  — the pre-existing file's `lifecycle-standing` line had already flipped on disk
  before the 2nd write's forced failure, plus stderr showed the misleading
  `"cannot read delta"` message.
- Passing test observed: both classes green after the fixes (`24 passed, 16
  subtests passed` for the whole file).
- Refactor while green: no separate refactor pass; the fixes themselves were the
  minimal change (predicate redefinition; stage-then-move rewrite).

## Docs/contracts touched
- None. `docs/EPISODE_STORE.md` was not touched — no contract conflict was found;
  both fixes are internal-implementation corrections against the existing contract
  (C3b's injection defense, C4's all-or-nothing guarantee), not new obligations.

## Assumptions
- The handoff's `os.replace()` suggestion for the move step was taken literally
  (atomic-for-a-single-file, correct on both POSIX and Windows) rather than
  `Path.rename()`, which is NOT atomic-overwrite on Windows when the destination
  already exists — `os.replace()` is the right primitive per the Python docs and
  per the handoff's own wording.
- Temp files are named `.{final_name}.tmp-{uuid4().hex}` and placed in the same
  parent directory as the final path (not a separate scratch dir), satisfying
  "same filesystem" without introducing a new store-relative path convention that
  would need its own seam.

## Stop conditions hit
- None. Both defects were mechanical, scoped fixes to the already-existing module,
  as the reviewer predicted; no decision outside implementer latitude was required,
  no exclusion needed touching, no evidence was unproducible.

## Out-of-scope observations
- Carried forward, unchanged, from the BLOCKed review's own "Out-of-scope
  observations" (not re-verified in this rework, since scope was the two
  Blockers only): the 6th unnamed layout seam (`_new_episode_path()`) triage
  candidate, top-level unrecognized op keys being silently accepted, and
  duplicate-op last-write-wins semantics. No new out-of-scope findings surfaced
  during this rework beyond the sweep note above (the pre-existing eager-`mkdir`
  cosmetic point), which is reported inline in the sweep section rather than
  repeated here since it is not a future-work item so much as a "checked, judged
  safe" note.

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed
after review: <what you checked>`; a bare `none` is treated as an unfilled field. This
is workflow signal, not project signal: you are the only one who saw this friction — if
you do not report it here, it is lost.

- **Handoff gaps:** None load-bearing. The rework instructions (this dispatch's own
  brief, quoting the reviewer's BLOCK verbatim) named the exact file, exact line
  range, exact reproduction, and the exact suggested fix shape for both defects —
  the only real decision left to me was the precise predicate for defect 1
  (`!= [value]` plus the `value != ""` carve-out vs. the brief's own suggested
  `len(...) > 1`), which the brief explicitly invited ("choose the exact predicate
  deliberately and say why").
- **Context rediscovered:** The empty-string edge case in the `splitlines()`
  predicate (`"".splitlines() == []`, not `[""]`) was not called out anywhere in
  the rework brief or the original review — I found it by testing the brief's own
  suggested `len(value.splitlines()) > 1` predicate against `""` before adopting a
  variant, and it would have broken every currently-passing test that submits an
  empty optional field (`retired-at`, `consolidated-into`, `superseded-by`). Worth
  naming explicitly in a future newline-guard rework brief, since it is the kind of
  edge case that is easy to introduce silently while "fixing" exactly this class of
  bug.
- **Instructions improvised around:** The g2-implementer-plan.json job file
  (`.agent-work/301/crew-handoffs/g2-implementer-plan.json`) was already `complete`
  and lease-released from the original g2 run. Rather than starting a fresh plan
  file (which would have orphaned the original run's `why_trail` and evidence from
  the same job), I re-claimed the existing lease and used the engine's `amend`
  verb (`add` ops) to append four new pending gates (m8-m11) for the rework,
  matching the "job-file-not-agent-file" doctrine in `references/global-everyone.md`
  (the file belongs to the job, not the agent process). This isn't named
  explicitly anywhere for the REWORK case specifically (only for the reach-up/
  refresh-request case) — worth confirming this is the intended pattern for a
  bounded rework dispatch, or naming it explicitly in the implementer skill.
- **What would have made this easier:** Nothing significant — the rework dispatch
  quoting the reviewer's BLOCK verbatim, with exact line numbers, exact
  reproduction steps, and an explicit sweep instruction, made both fixes and the
  sweep straightforward to execute without needing to re-derive anything from the
  original handoff or review result.

## Return status
`complete`
