# Verdict: commander-232 (issue #232, epic-226 item F, wave 1)

PR: **#246** — https://github.com/fredcai6/constellation-skills/pull/246
Branch: `issue-232` · Commits: `b95b936` (item a), `710d369` (item b, closes
#205), `89ca36d` (item c, closes #198) · Fork point: `3283158`
Worktree: `C:/Programs/constellation-wt-232` (verified isolated —
`python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-232`
→ `worktree OK: in C:/Programs/constellation-wt-232`)

## 1. Verdict — per build item

- **(a) `_glob_to_regex` property tests — SHIPPED.** Zero direct tests
  existed before (`grep -rn "_glob_to_regex" tests/` returned nothing,
  independently re-confirmed at `understand`). 9 new tests
  (`TestGlobToRegex` in `tests/test_checklist_engine.py`) cover every
  dimension named in the #227 rework-cost lesson: literal-char escaping,
  single `*` (segment-only), `**` (mid-pattern / leading `**/` / trailing
  `/**`), `?`, empty pattern, anchoring, path-separator handling.
  `scripts/checklist_engine.py` diff is empty — `_glob_to_regex`'s own
  behavior is unchanged (PR-5 honored).
- **(b) #205: atomic `_write_meta` + corrupt-meta resilience — SHIPPED,
  closes #205.** `_write_meta` (`scripts/run_skill_eval.py:938`) now
  writes via `tempfile.mkstemp(dir=run_dir)` + `os.replace` (same-directory,
  atomic on POSIX and Windows), with cleanup on failure; signature and
  both existing call sites unchanged. `_adopt_existing_runs`'s corrupt-meta
  branch now routes through `_adjudicate_orphan` (the same path the
  sibling `"launched"` branch already used) and continues the scan,
  instead of `break`-ing and silently losing every run-dir after the
  corrupt one. Regression test drives the REAL post-fix `_write_meta` to
  produce an actual `meta.json`, then truncates those real bytes — not a
  hand-authored fixture — per `lesson:verify-harness-field-and-drive-real-writer`.
  TDD RED (against pre-fix `break`) then GREEN shown; the reviewer
  independently reproduced RED in an isolated scratch tree by reverting
  only the fix.
- **(c) doc-drift sweep — SHIPPED, closes #198.** All four stale sites
  fixed: `run_skill_eval.py` module docstring (`:12-13`), `:556` (was
  `:555`, shifted by the docstring edit), `:1315` (was `:1288`) — all
  called `launch_agent`/`temp_install` "inert stubs"/"inert until g3"
  though both have been real, live implementations since g3 shipped
  (confirmed: `launch_agent` at `:675` really spawns `subprocess.Popen`,
  `temp_install` at `:766` really calls
  `install_constellation.install_skills`). `install_constellation.py:531-533`
  (drifted from the issue's cited `:430-431`, confirmed via grep before
  editing) claimed an eval run and a real install fingerprint a corpus
  identically — false since #153's `stable_corpus_id()` path-normalizes
  the eval id specifically; corrected to state the two are deliberately
  non-identical when install paths differ.

No honest null on any of the three items — all confirmed live, ungrafted
work exactly as `LAUNCH_ORDER-232.md`'s PR-7 findings stated, independently
re-verified against current code before planning (not inherited un-checked).

## 2. Evidence

**Worktree isolation:**
```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-232
worktree OK: in C:/Programs/constellation-wt-232
```

**Own measured baseline** (`python -m pytest tests/ -q`, run in
`C:/Programs/constellation-wt-232` before any change — NOT inherited from
the launch order's cross-environment figure):
```
1037 passed, 2 skipped, 250 subtests passed in 46.09s
```
(skip-guard on this baseline: exit 0, both skips allow-listed — same two
as post-change below.)

**Post-change run** (same command, all 3 items shipped, run just before
writing this verdict):
```
$ python -m pytest tests/ -q --junitxml=junit-report.xml
1047 passed, 2 skipped, 250 subtests passed in 45.71s
exit: 0
```
(+10 net: +9 tests from item a, +1 regression test from item b; zero
regressions, zero unrelated changes.)

**Full local CI command set** (PR-2b — no GitHub Actions run triggered,
waited on, or claimed; every guard proven locally):
```
$ python -m pip install --upgrade pip
$ python -m pip install pytest coverage
$ python -m pytest tests/ -q --junitxml=junit-report.xml
1047 passed, 2 skipped, 250 subtests passed in 45.71s
exit: 0

$ python scripts/verify_skip_guard.py junit-report.xml
skip guard ok: 2 skip(s) in report, all match documented allow-tuples
exit: 0

$ python -m coverage run --include="*/checklist_engine.py" -m pytest tests/test_checklist_engine.py -q && python -m coverage report
290 passed, 24 subtests passed in 7.11s
Name                          Stmts   Miss  Cover
-------------------------------------------------
scripts\checklist_engine.py    1189     72    94%
-------------------------------------------------
TOTAL                          1189     72    94%
exit: 0

$ python -m coverage report --fail-under=90
... 94% ...
exit: 0

$ python -m coverage report --fail-under=95   # two-directions proof
... 94% ...
Coverage failure: total of 94 is less than fail-under=95
exit: 2
```
(Own-environment coverage baseline, measured before any change, restricted
to `tests/test_checklist_engine.py`: **93%**. Wave-0's 91%/90% figures are
stale for this run per the launch order's own note — not cited as this
run's evidence.)

**`which git`:**
```
$ which git
/mingw64/bin/git
exit: 0
```
No git-less reproduction was attempted this run — out of scope for #232
(the git-less skip-guard proof belongs to #229, merged; this issue only
consumes its command set).

**Environment note:** `python --version` → `3.14.3`
(`C:/Users/fredc/AppData/Local/Microsoft/WindowsApps/python`), not the CI
workflow's pinned 3.12 — this is the local dev-box interpreter used for
the local-proof requirement (PR-2b), not a CI run; `python`, never `py`,
used throughout per the confirmed `py`-resolves-to-a-pytest-less-runtime
hazard (#242 item 2).

**New `_glob_to_regex` property tests, named, with pass output:**
```
$ python -m pytest tests/test_checklist_engine.py -q -k glob_to_regex
9 passed, 281 deselected in 0.20s
```
`TestGlobToRegex` (`tests/test_checklist_engine.py`): `test_glob_to_regex_literal_chars_are_escaped`,
`test_glob_to_regex_single_star_matches_within_segment_only`,
`test_glob_to_regex_double_star_crosses_segments`,
`test_glob_to_regex_leading_double_star_slash_matches_zero_or_more_leading_segments`,
`test_glob_to_regex_trailing_slash_double_star_also_matches_directory_itself`,
`test_glob_to_regex_question_mark_matches_exactly_one_non_separator_char`,
`test_glob_to_regex_empty_pattern_matches_only_empty_string`,
`test_glob_to_regex_anchoring_requires_full_string_match`,
`test_glob_to_regex_path_separator_is_literal`.

**Item (b) regression test, named, with pass output, real-writer note:**
```
$ python -m pytest tests/test_run_skill_eval.py -q -k corrupt_meta
1 passed, 89 deselected in 0.27s
```
`test_adopt_existing_runs_routes_corrupt_meta_through_adjudicate_orphan_and_continues`
(`tests/test_run_skill_eval.py`) — calls the real (post-fix) `_write_meta`
to produce an actual `meta.json` on disk, reads back the real bytes, then
truncates them (`real_bytes[: len(real_bytes) // 2]`) to simulate a kill
mid-write, before driving `_adopt_existing_runs`. Confirms a corrupt slot
is adjudicated (not silently lost) AND that the scan continues past it
(a second, later run-dir is still adopted/counted). Independently
re-verified by the gate's reviewer, who additionally reverted the fix in
an isolated scratch tree and reproduced the identical pre-fix RED failure.

**`grep` proof — all four stale phrases gone:**
```
$ grep -n 'inert stub' scripts/run_skill_eval.py; echo "exit:$?"
exit:1
$ grep -n 'inert until g3' scripts/run_skill_eval.py; echo "exit:$?"
exit:1
$ grep -n 'fingerprint a corpus identically' scripts/install_constellation.py; echo "exit:$?"
exit:1
```
(exit 1 = grep found nothing = phrase gone, in all three checks — the
literal acceptance text "grep for the stale phrases returns nothing" is
met.)

## 3. Map impact

Minimal, per the reconcile step (no `docs/architecture/` map exists in
this repo — confirmed absent, reconciled directly rather than via
Cartographer dispatch, per the reconcile step's own absent-map guidance):

- `_write_meta`'s write semantics changed (direct `write_text` → atomic
  temp-file + `os.replace`) — a capability-boundary-adjacent change, but
  its signature and both call sites' contracts are unchanged, so no
  caller-visible interface shift.
- `_adopt_existing_runs`'s corrupt-meta handling changed (silently
  stop-scan → adjudicate-and-continue) — an internal robustness
  improvement to the resume/adoption capability (issue #130's original
  scope), no interface change.
- `_glob_to_regex` and the four doc-drift sites: no behavior change at
  all (tests + comments only).
- No design/schema doc anywhere in `docs/` references any of `meta.json`,
  `_write_meta`, or `_glob_to_regex` (confirmed via grep) — the only
  durable description of the touched write/routing contracts is each
  function's own docstring, which items (b) and (c) already updated
  in-place as part of their own diffs.

## 4. Triage candidates

- (from g2's review, non-blocking Fowler observation) `_adopt_existing_runs`'s
  new corrupt-meta branch duplicates 4 lines of tail logic (append /
  count-if-terminal / `idx+=1` / `continue`) already present below it in
  the launched/terminal branch. A `try/except/else` restructure would
  unify them. Functionally correct and fully test-covered either way —
  routed **recommend-and-defer** (too trivial for a standalone GH issue;
  noted here for awareness, not fixed now since it would reopen an
  already-closed, reviewed, committed gate for a cosmetic DRY nit).
- PR-8 lane check: nothing touching #219, #220, #239's remaining open
  items (1, 2, 4, 5), #242, #243, or #244 was discovered during this run
  — confirmed nothing to file or comment on.

## 5. Workflow feedback

Full retrospective staged at
`C:/Programs/constellation-wt-232/.agent-work/staged-feedback/232/AGENT_FEEDBACK.md`
(see below for why staged, not applied, to the shared log). Highlights:

- **Fencing discovered mid-run, handled per this skill's own documented
  carve-out, not floated.** The main checkout carries an ACTIVE Admiral
  epic-226 lease (`admiral-epic-226-b`, confirmed at the `context` step by
  direct read of `.agent-work/epic-226/spine.json`). Per
  `agent_work_root.py`'s documented exception, this fences the main
  checkout's durable `.agent-work/` read-only for a delegated Commander,
  so `durable_root()` resolves to this worktree instead. Per
  `constellation-commander-delegated`'s fenced-feedback-closeout
  instructions, staged the `AGENT_FEEDBACK.md`/`lessons-delta.json`/
  `CONSTELLATION_FEEDBACK.md` trio plus a `FENCE.md` citation under
  `.agent-work/staged-feedback/232/` in the worktree, rather than writing
  (or attempting to write) the shared durable log directly. `lessons-delta.json`
  was validated via `--dry-run` against a read-only scratch copy of the
  real `LESSONS.md` (not applied for real — that's the Admiral's harvest
  step). **The Admiral should harvest this trio into the shared root at
  epic closeout, then run the real threshold-ripe sweep
  (`apply_lessons_delta.py --ripe`) against the shared playbook** — this
  run's own `verify_lessons_applied.py` check degraded gracefully to
  "no playbook — clear" against the fenced-empty worktree-local path,
  which is a sanctioned but real gap this run could not close itself.
- `checklist_engine.py attach --payload-file` requires JSON; the crew's
  own `IMPLEMENTER_RESULT`/`REVIEW_RESULT` artifacts are Markdown by the
  templates' own convention. First attempt at `attach ... --payload-file
  g1-implementer-result.md` failed with a `JSONDecodeError`; worked around
  with `--field`-based pointer attachments instead (arguably the more
  correct "return thin, write fat" shape anyway, but the JSON-only
  constraint isn't documented anywhere a Commander would see it before
  hitting the traceback).
- `checklist_engine.py <verb> --why "...`code`..."` (backtick-wrapped code
  identifiers inside a Bash-tool double-quoted `--why`/`--note` string)
  triggers Git-Bash command substitution — the word inside backticks
  silently vanishes from the recorded digest even though the engine call
  itself still succeeds. Hit once (harvested from a crew's own workflow
  feedback), avoided afterward.
- Both crew-verification loops (implementer claims a number, reviewer
  independently reproduces it, Commander re-verifies before advancing)
  caught two real accuracy nits before they reached the shipped diff: an
  off-by-one baseline figure in my own g2-reviewer-handoff.md prose (not
  code), and a stale map-anchor line number after g2's own edit shifted
  the file. Neither was a defect in the shipped change — both were
  Commander-authored planning-artifact drift, caught by the review layer
  exactly as designed.
- design-it-twice and the cold plan critic were both skipped at `plan`,
  each recorded as a named untaken road citing `LAUNCH_ORDER-232.md`'s
  own Pre-empted Steps section (no load-bearing interface introduced by
  any of the three build items) — worked cleanly, no friction.
- Treating item (c) as a reasoning gate (no crew, three pre-authored
  grep-absence command postconditions) instead of a full crew cycle was
  proportionate for a comment-only, mechanically-verifiable change —
  same rigor, a fraction of the wall-clock cost.
