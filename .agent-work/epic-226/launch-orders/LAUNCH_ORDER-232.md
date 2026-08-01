# Launch Order: `commander-232 — issue #232 (epic-226 item F, wave 1)`

Commanders start cold. Everything you need is pasted below — do not assume you can
open anything referenced by id alone. **This is WAVE 1: prior-wave verdicts exist
and are pasted in full below** — unlike wave 0, weak pointers ("see commander-227's
verdict") are not acceptable; the load-bearing content is inline.

## Mission

**Issue #232 — hardening: `_glob_to_regex` property tests, #205 atomic eval meta,
doc-drift sweep.**

Deliverable: a merged-ready PR against `fredcai6/constellation-skills` implementing
all three build items below, with the acceptance evidence pasted into your verdict.

How it serves the epic intent: epic-226 batches six independently-merited issues;
F is the hardening pass over machinery wave 0 already shipped. It closes two
already-filed, already-triaged follow-ups (#205, #198) by absorption, and adds test
coverage to a function (`_glob_to_regex`) that has none today. It carries **no
cross-issue coupling** beyond the one encoded edge: C (#229, merged) supplies the
command set F's acceptance is measured against.

**Full issue body, verbatim:**

> Spec S10 (corrected by the testability critic: `_collect_changed_files` is
> ALREADY tested via `GitChangePolicyCollectorIntegration` — do not rebuild it; its
> real defect is the silent `skipTest` without git, closed by issue C's
> skip-guard).
>
> Build:
> (a) Property tests for `_glob_to_regex` (zero direct tests today). Optionally an
> additive reopen-cascade property test (well-covered already — polish, not gap).
> (b) #205: atomic `_write_meta` (temp file + `os.replace`) + corrupt-meta
> resilience in `run_skill_eval.py` (`_adopt_existing_runs` treats corrupt meta as
> orphan), with the regression test the issue names. Closes #205.
> (c) Doc-drift sweep: `run_skill_eval.py`'s three stale 'inert stubs / wired at
> g3' sites (module docstring, ~:555, ~:1288) — the launch seam is live; plus
> `install_constellation.py:430-431`'s stale eval-fingerprint comment (closes
> #198; small scope addition flagged at review).
>
> Acceptance: new tests green in CI (issue C) with zero unexpected skips; grep for
> the stale phrases returns nothing. Out of scope: any behavior change to the eval
> runner beyond #205's write path.
>
> type: AFK

## Prior-Wave Verdicts (pasted)

Wave 0 (issues #227–#231) is fully merged into `main` — your fork point (`3283158`)
already contains all of it. Two verdicts matter to you; both pasted in full below.

### #229 (CI) — no verdict was written; the Admiral's own re-verification below is
the substitute. `commander-229` dropped its verdict, so this is reconstructed from
`.agent-work/epic-226/evidence/findings-229.md` (its findings file) plus the
Admiral's own read of the merged `.github/workflows/ci.yml` (PR #237, merged into
`main` at `cd6e75e`/`048febb`, confirmed present at your fork point).

**The exact command set — this is the literal contract your acceptance reads
against (PR-2b cascade):**

```
python -m pip install --upgrade pip
python -m pip install pytest coverage

python -m pytest tests/ -q --junitxml=junit-report.xml

python scripts/verify_skip_guard.py junit-report.xml

python -m coverage run --include="*/checklist_engine.py" -m pytest tests/test_checklist_engine.py -q && python -m coverage report
python -m coverage report --fail-under=90
```
Environment: `PYTHONIOENCODING: utf-8`, `shell: bash`, Python 3.12,
`runs-on: windows-latest`. Verified byte-for-byte against the merged workflow file.

**Skip-guard design (from findings-229.md, cold-critic-hardened):** the allowlist is
keyed on **(classname, test name, message) together, not message alone** — the cold
critic flagged message-only as spoofable (a future test could reuse an allowed
message string to sneak past the guard) and this was fixed before merge. Two
pre-existing, environment-conditional skips are allow-listed as expected:
`test_verify_spec_confirmed.py` (untracked `DESIGN_SPEC.md` absent from fresh
worktrees) and `test_verify_worktree_isolation.py` (symlink-creation permission).
Anything else that skips — in particular the git-integration skip in
`GitChangePolicyCollectorIntegration.setUp` (`tests/test_checklist_engine.py:1003`,
`if shutil.which("git") is None: self.skipTest(...)`) — must **fail** the guard, not
pass silently.

**Coverage floor:** measured **91%** on `scripts/checklist_engine.py` restricted to
`tests/test_checklist_engine.py` at wave-0's fork point; floor pinned at
current-minus-1 = **90%**, verified to fire non-zero in both directions
(`--fail-under=92` → exit 2). **This number is now stale for you** — #227 rewrote
`checklist_engine.py` entirely and #232(a) adds new tests to the same file.
**Measure your own floor-relevant coverage after your changes; do not cite 91%/90%
as your own evidence.**

**`windows-latest`/git-bash assumption:** documented, not measured — GitHub's
`actions/runner-images` spec documents Git for Windows (incl. `git-bash.exe`) as a
stable inclusion in the `windows-2022` image. No Actions run was triggered to prove
it. State this the same way if you cite it: a documented assumption, not an
observation.

**Local environment note carried forward:** in that Commander's session, `py`
resolved to a sandboxed runtime with neither `pytest` nor `coverage` preinstalled;
`python` did not have this problem. Consistent with #227's independent finding
below — **use `python`, not `py`, throughout your run.**

### #227 (engine rewrite) — verdict excerpts relevant to you (full file:
`.agent-work/epic-226/verdicts/commander-227.md`)

`scripts/checklist_engine.py` was rewritten and merged (`386bf3e`/PR #241, and its
four child commits `56453e7`/`3907e46`/`9e1b911`/`1beb90c`/`c75fcc4`). Confirmed
symbols on current `main` (independently re-grepped for this order, not just cited):
`recovery_for(exc, cl)` at `scripts/checklist_engine.py:301`, `state(cl)` at
`:1328`, `render_human(view)` at `:1367`. **Your `_glob_to_regex` property tests
target this post-#227 file** — `_glob_to_regex` itself is unchanged by #227 (still
at `:449`, called at `:496`), but the surrounding module you're adding tests to is
the new one. Confirmed via grep: **zero** existing references to `_glob_to_regex`
anywhere under `tests/` — the issue's "zero direct tests today" claim holds exactly
as stated.

**Output-ordering fact, both sides — verify which holds, don't assume:** #227 item
4 moved the RAIL banner to the front of the stream specifically so the operative
result/refusal line is now **last**. The verdict's own field evidence
(`commander-227.md` §"Item 4") shows `tail -1` on both a refusal and a success
stream now returning the operative line, not the RAIL banner — this is a fix, not
a design note; before it, `tail -1` returned the banner on both streams. **Before
you rely on this for your own engine-output parsing (if any), reproduce the check
yourself on the merged engine** — the `tail -1` fix is real per this evidence, but
the historically-safe form (`grep -v '^RAIL'`) still works too and is a fallback if
your own reproduction disagrees.

**Rework-cost lesson from #227, directly relevant to your own test design:** four
defects in that run shared one shape — "the test fixtures could not express the
failing state" (single-dimension fixtures hid a bug that only appeared on a second,
uncovered dimension). Your `_glob_to_regex` property tests are exactly the kind of
surface this bites: parameterize over every dimension the function's behavior
depends on (glob special chars, empty pattern, path-separator handling, anchoring),
not just the happy-path cases.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when
overriding.

- **PR-2b (Actions unavailable) — ABSOLUTE, this is the load-bearing ruling for
  your acceptance.** No Commander may trigger, wait on, poll for, or claim a GitHub
  Actions run. #232's "green in CI" acceptance reads as **"green under #229's
  workflow command set (pasted above), run locally."** A verdict asserting "CI
  green" without a local command transcript is invalid evidence. **Acceptance also
  requires ZERO UNEXPECTED SKIPS** — run the skip-guard yourself and paste its exit
  code, don't infer it from the suite's own summary line.
- **Baseline — measure your own, do not inherit a number.** A fresh-worktree
  baseline at `3283158` from another environment was **approximately 1037 passed, 2
  skipped** (informational, from a `--collect-only` scan during this order's
  drafting: 1039 collected) — **this is not your baseline.** Run the suite yourself
  in `C:/Programs/constellation-wt-232` before making any change and state the
  number you measured, with the command that produced it. A test count from another
  environment is not a baseline.
- **PORTABILITY HAZARD — git-less proof, read before you attempt it.** Reproducing
  the "git-less" skip-guard proof locally is error-prone on a dev box. Stripping
  `/mingw64/bin` from `PATH` leaves a **second `git` shim at `/cmd/git`** still
  reachable, so the run is not git-less at all and the guard trivially appears to
  work — this produced a false pass once already, on #229's own clean-room review.
  **You must assert `which git` exits non-zero** before trusting any git-less
  result — never infer git-lessness from having stripped one directory. The real
  Actions runner has no MSYS shim, so this is a **local-reproduction hazard only**,
  but it is exactly the kind that yields a confident wrong answer.
- **PR-5 (file already shared with #227, but not concurrently).** #227 merged
  before you dispatch — there is no concurrent-edit collision. Your `_glob_to_regex`
  property tests (item a) must be written against the **post-#227 engine surface**
  named above (`state()`, `render_human()`, `recovery_for()`, RAIL-banner-first
  ordering) — not the pre-#227 file. You are not modifying `_glob_to_regex`'s
  behavior, only adding tests to it, per the issue's own scope line ("no behavior
  change to the eval runner beyond #205's write path" — note this line is scoped to
  the *eval runner*; it does not license an engine behavior change either, since
  item (a) is explicitly "property tests," not a fix).
- **PR-6 (canonical doctrine source).** Doctrine edits, if any arise, go to
  `skills/_shared/global-*.md`, never `skills/<role>/references/global-*.md`
  (install-time copies `install_constellation.py` regenerates and silently
  overwrites). **Not expected to fire this issue** — #232's three build items are
  code/test/comment edits, not doctrine — but binding if you find yourself touching
  a `global-*.md` file for any reason.
- **PR-7 (verify before plan) — re-verified independently for this order; four data
  points now, the most-confirmed lesson in the inbox.** Findings below, from
  grepping current `main` at `3283158` **before** this order was written — you must
  still re-verify them yourself before you plan, per the lesson's letter, but they
  are accurate as of this writing and should save you the rediscovery:
  - **(a) `_glob_to_regex` — confirmed live gap.** `scripts/checklist_engine.py:449`
    (def), `:496` (call site). `grep -rn "_glob_to_regex" tests/` returns nothing.
    Real work, not a null.
  - **(b) #205 — confirmed live gap, and issue #205 is CLOSED as absorbed, not
    fixed.** `gh issue view 205` shows `stateReason: COMPLETED` with a comment:
    *"Absorbed into #232 (epic #226) item (b)."* The code itself confirms the gap:
    `_write_meta` (`scripts/run_skill_eval.py:938`) does a direct
    `.write_text(...)` — no temp file, no `os.replace`. `_adopt_existing_runs`
    (`:1080`) catches `(OSError, ValueError)` on a corrupt `meta.json` and
    **`break`s the scan loop** — this stops counting further runs and treats the
    corrupt slot as the next free index to relaunch into, which is **not** the same
    as routing it through `_adjudicate_orphan` (the path the sibling `"launched"`
    branch two lines up already uses, at `:1098`). That gap between "doesn't crash"
    and "adjudicated as an orphan" is the live defect the issue names — confirm
    this yourself before assuming the `try/except` already satisfies "corrupt-meta
    resilience."
    - The regression test target: issue #205's own body says *"Add a regression
      test simulating a corrupt/truncated meta."* Per
      `lesson:verify-harness-field-and-drive-real-writer` (pasted below), that test
      must corrupt a `meta.json` produced by the **real** `_write_meta`/run path,
      not a hand-authored fixture dict serialized directly to disk — a hand-set
      fixture can pass green even if the real writer never produces that shape.
  - **(c) doc-drift, `run_skill_eval.py` — all three sites confirmed live and
    stale.** `launch_agent` (`:675`) and `temp_install` (`:766`) are **fully
    implemented, real functions** (real `subprocess.Popen`, real
    `install_constellation.discover_skills`/`install_skills` calls) — not stubs.
    Yet three comments still call them stubs: module docstring `:12-13` ("`launch_agent`
    and `temp_install` are inert stubs here (raising `NotImplementedError`...)"),
    section-header comment `:555` ("the ONE real seam (inert until g3)"), and
    `:1288` ("the real `launch_agent` + `temp_install` are inert stubs until g3").
    Confirms the issue's claim exactly.
  - **(c) doc-drift, `install_constellation.py` — confirmed live, but the LINE
    NUMBER IN THE ISSUE HAS DRIFTED.** Issue #232 (filed pre-epic, as #198) names
    `install_constellation.py:430-431`. On current `main` (post-#228, which
    inserted content earlier in the file) the actual comment is now at
    **`:531-533`**: *"The eval harness imports these same primitives so an eval run
    and a real install fingerprint a corpus identically."* Issue #198 (also CLOSED
    as absorbed — same comment-pattern as #205) explains why this is stale: after
    #153 made `stable_corpus_id()` path-normalize the eval id specifically, an eval
    run's fingerprint and a real install's fingerprint are **deliberately no
    longer identical** (real installs bake in absolute paths; eval ids are
    normalized). The comment still asserts they match. **Do not search for line
    430-431 and conclude the target is gone — it moved.** Grep for `fingerprint` in
    `scripts/install_constellation.py` to relocate it yourself.
- **PR-8 (stay in lane).** Adjacent #219/#220 work is not yours — file or comment,
  don't absorb. Same for #239's remaining open items (1, 2, 4, 5) and for
  #242/#243/#244 (which #227's and #229's runs filed against this same epic's own
  friction — #242 items 2 and 3 below are literally about your own launch order,
  read them, don't re-file them as new).

**Known live drift already filed — do not re-discover, just honor it:** `#242`
tracks three items from wave 0's friction, all relevant to you and already
accounted for above: item 2 (`py` resolves to a pytest-less runtime on this box —
**use `python`**, applied throughout this order); item 3 (the launch-order
template's claim that `.agent-work/archive/` holds usable transcripts is **false**
— none exist; see Data Locations below, do not go looking there and do not cite it
as a source); item 1 (`waive()`'s raise sites unwired into `recovery_for()` —
**not your item**, leave it filed).

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable.
Report it with the same rigor as a win. Per the PR-7 findings above, all three of
#232's build items independently re-verified as **live, ungrafted work** at the
time this order was written — no honest null is expected here, but you still owe
the independent re-verification, and if your own re-check disagrees with this
order's findings, that disagreement is itself the honest-null report: state what
you tested and what you found.

## Inherited Latitude

You may decide, without floating to the Admiral:

- Test organization, naming, and file layout for the new `_glob_to_regex` property
  tests (a dedicated test class/module vs. extending
  `tests/test_checklist_engine.py`).
- The exact property-test strategy (hypothesis-style generators vs. a hand-authored
  parameterized matrix) for item (a), provided it covers the dimensions named in
  the #227 rework-cost lesson above.
- Implementation shape of the atomic write in `_write_meta` (temp-file naming,
  same-directory vs. dedicated tmp) and of the corrupt-meta-as-orphan routing in
  `_adopt_existing_runs`, provided both preserve every existing call site's
  contract.
- Exact wording of the corrected comments for item (c) — the issue only requires
  the stale phrases to disappear and the true state to be documented, not specific
  prose.
- Narrowing scope where a build item proves already-shipped (honest null, evidence
  pasted) — not expected here per PR-7 findings, but always available if your own
  re-verification disagrees with this order's.
- Bounded fix-now triage: a small defect you trip over and fix in-lane.

You must **float to the Admiral** (stop and return, do not guess):

- Any behavior change to the eval runner **beyond** #205's write path — the issue
  says this explicitly is out of scope.
- Any change to `_glob_to_regex`'s own behavior (you are adding tests, not fixing
  a defect the tests might surface — if a property test finds a real bug, that is
  a float, not a silent fix, since the issue scopes you to tests only for item a).
- Any change to the five frozen rail strings, or to engine behavior beyond what's
  needed to make `_write_meta`/`_adopt_existing_runs` atomic/resilient.
- Any doctrine edit (not expected; PR-6 governs if it arises).
- Adding scope, or dropping a build item for a reason other than a measured null.
- Anything that would require touching `.github/workflows/**` or
  `scripts/verify_skip_guard.py` (owned by #229, merged — you consume its command
  set, you do not edit it).

Asking up is always sanctioned. If you need epic-level context this order does not
carry, **return-and-query the Admiral** — it answers and continues you. That is a
first-class move, not a failure.

## File Ownership

**Sole writer this wave** of:
- `tests/test_checklist_engine.py` (or a new test module, your choice) — item (a)'s
  property tests, additive only, no engine-behavior edits.
- `scripts/run_skill_eval.py` — item (b)'s atomic `_write_meta` +
  `_adopt_existing_runs` corrupt-meta routing, and item (c)'s three stale-comment
  fixes.
- `tests/test_run_skill_eval.py` (or wherever that suite's tests live — confirm the
  actual filename in your worktree) — item (b)'s regression test.
- `scripts/install_constellation.py` — **comment-only** edit for item (c)'s stale
  fingerprint comment (now at `:531-533`, see PR-7 above). Do not touch any code in
  this file.
- `.agent-work/epic-226/evidence/findings-232.md` (your working notes; sole
  writer).

**Fenced — do not write:** `.github/workflows/**` and `scripts/verify_skip_guard.py`
(#229 owns them, merged); `scripts/checklist_engine.py`'s behavior (#227 owns it,
merged — you may add tests that import from it, you may not edit its logic);
`scripts/install_constellation.py` beyond the one named comment; anything under
`skills/prototyper/**`, `skills/commander/**` (#231); planning templates /
`scripts/grade_lint.py` (#230); anything belonging to #219/#220/#239/#242/#243/#244
(PR-8 — file or comment, don't absorb).

Your findings file: `.agent-work/epic-226/evidence/findings-232.md`. **Known harness
guard:** the `Write` tool refuses paths whose basename contains "findings" — create
this file via a `Bash` heredoc, not `Write`.

## Workspace

Absolute worktree path: `C:/Programs/constellation-wt-232`
Branch: `issue-232` · Base: `main` at `3283158`
Already provisioned by the Admiral (confirmed via `git worktree list` at order-write
time: `C:/Programs/constellation-wt-232  3283158 [issue-232]`) with:
```
git worktree add C:/Programs/constellation-wt-232 -b issue-232 main
```
`3283158` already contains all six... **five** wave-0 merges relevant to your fork
(#227/#228/#229/#230/#231 — PR-5's premise holds: you are strictly post-#227).

**First step, before any git operation:** run
`python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-232`
— it must exit 0, proving you are in your own worktree and not the shared checkout.
Paste its output into your return report. **Use `python`, not `py`, for this and
every other invocation** — `py` resolves to a pytest-less sandboxed runtime on this
box (independently confirmed by both #227's and #229's Commanders).

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR
itself, not a local merge that would diverge your worktree from main).

## Inherited Context

**This repo VENDORS its own scripts.** Drive everything from the repo copy under
`scripts/`, not from any globally-installed `C:/Users/fredc/.claude/skills/...`
copy — the two can diverge. Same for templates: prefer `skills/<role>/templates/`.

**Active lessons from `.agent-work/LESSONS.md` bearing on your mission:**

- `lesson:test-harness-concurrency-failsafe` (project / testing, 2 confirmed data
  points): test harnesses driving real concurrent file I/O need try/except with a
  guaranteed stop-signal in `finally`, plus `daemon=True` helper threads. If your
  item (b) atomic-write regression test drives any real concurrent writer/reader
  pair (not required by the issue, but possible if you test interruption mid-write),
  apply this pattern or a hang will eat your session.
- `lesson:verify-launch-order-claims-against-code` (project / delegated-planning,
  now effectively 4 data points counting this order's own PR-7 findings above):
  verify every named symbol/line against current code before planning — a headline
  mechanism already shipped is an honest null, a wrong line number is a drift to
  relocate, not a reason to conclude the target is gone.
- `lesson:verify-harness-field-and-drive-real-writer` (project / testing): a
  regression test for a harness-supplied field/shape must drive the REAL writer
  path, not a hand-injected fixture. **Directly binds item (b)'s regression test**
  — corrupt a `meta.json` that the real `_write_meta` actually wrote, don't
  fabricate one.
- `lesson:observe-midprocess-state-not-via-end-output` (handoff / test-authoring):
  to observe a MID-process state the observation channel must survive the
  kill/hang being tested. Relevant only if your atomic-write test simulates a
  mid-write process death (optional, not required by the issue's stated scope).

**Platform invariants (Windows):**

- **Command-checks run under a POSIX shell (bash).** Author `grep`/`&&`/pipe checks
  in POSIX form. On a box with no bash the engine stamps `shell: cmd-fallback` and
  the check fails visibly.
- **`gh pr create` body:** write the body to a temp file and use
  `gh pr create -F <file>`. Never a heredoc, never a PowerShell `@'...'@`
  here-string for `--body` (here-strings work for `git commit -m` only).
- Set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you
  capture — cp1252 pipes corrupt captured output silently. (Already set at the CI
  workflow level; set it yourself for local runs too.)
- The Agent-tool `isolation:"worktree"` flag is a **silent no-op** on Windows. Your
  worktree is real because the Admiral provisioned it with `git worktree add` —
  verify with `--here`.
- **Engine output ordering — verify which holds for you, per the #227 excerpt
  above:** pipe through `grep -v '^RAIL'` is the historically-safe form; `tail -1`
  is claimed fixed by #227's field evidence. Reproduce the check yourself before
  depending on either in your own test/verification commands.

**Charter-lite carrier:** this repo has no `docs/agents/` overlay, so this block is
your doctrine carrier. Beyond it, your inherited globals are
`references/global-orchestrator.md` + `references/global-everyone.md` bundled with
your skill.

**Doctrine you must not re-derive** (inherited, not restated per-handoff):
correctness over velocity for promoted behavior; behavior changes are test-led
where a test surface exists; fail visibly rather than emit plausible wrong output;
one canonical path, no speculative abstraction.

## Pre-empted Steps

- **Latitude / authorization:** settled by the Admiral's confirmed, re-armed
  latitude contract (`.agent-work/epic-226/LATITUDE_CONTRACT.md`, confirmed
  2026-07-24, re-armed at the wave-0/1 checkpoint — all `PR-1..PR-8` pre-rulings
  stand). Cite it for `user-decision` checkpoints on your spine.
- **Design-it-twice:** not applicable — none of #232's three build items invent a
  new load-bearing interface; they add tests, harden an existing write path, and
  fix comments.
- **Issue triage / scoping:** the issue body is frozen as written. Do not re-scope
  it. #205 and #198 are already closed as absorbed — do not re-open or re-file
  them; your PR closing #232 closes their intent by reference.
- **Worktree provisioning:** done for you (verify with `--here`, do not create your
  own).
- **PR-7's re-verification of the three build items' targets:** substantially done
  for you above (exact symbols, line numbers, and the one line-number drift) — but
  you still owe your own independent re-check per the lesson's letter before you
  freeze a plan. This order's findings are a head start, not a substitute.

## Data Locations

Untracked inputs absent from your worktree, in the main checkout at
`C:/Programs/constellation-skills`:

- `.agent-work/` (the whole tree — lessons inbox, prior epic archives, the
  Admiral's live spine). **Read-only for you.**
- **`.agent-work/archive/` does NOT hold usable transcripts — this is a confirmed
  false claim (per #242 item 3, restated here so you don't rediscover it the hard
  way as #227's run did).** Do not look there for corpus/baseline material.
- Prior-wave verdicts and findings you may want to re-read in full:
  `.agent-work/epic-226/verdicts/commander-227.md`,
  `.agent-work/epic-226/evidence/findings-229.md` — both already excerpted above,
  but the full files exist if you need more.

## Budget

- **Model tier (required):** **sonnet** (per the latitude contract's Budget
  section — F is not one of the two design-heavy issues). Crew (implementer/
  reviewer) also **sonnet**. **No Fable at any tier.**
- **Compute/time, session-window:** you are the sole wave-1 dispatch (wave 1 has
  no concurrent siblings drawing the same pool this run). If you hit a session
  limit mid-flight, write your state to your spine and return — do not silently
  die.

## Stop Conditions

Stop and return when:

- A decision listed as **float to the Admiral** above is needed.
- Your scope would exceed the issue's declared boundary (any eval-runner behavior
  change beyond #205's write path; any `_glob_to_regex` behavior change).
- The suite goes red in a way you cannot attribute to your own change within a
  bounded effort — return with the failure attributed by a `uniq -c`-style command
  over the failure list, never from the pytest tail alone.
- The skip-guard reports an unexpected skip you did not introduce and cannot
  attribute.
- The git-less proof (if you attempt one for your own verification, though this
  issue doesn't require re-proving #229's CI) trips the portability hazard above —
  resolve it with `which git`, don't report a result you haven't confirmed
  git-less.
- Budget crossed, or evidence for an acceptance item proves impossible to produce.
- You need **context this order does not cover and cannot safely proceed
  without** — return-and-query the Admiral (it answers and continues you). Asking
  up is always sanctioned.

## Return Shape

Write `.agent-work/epic-226/verdicts/commander-232.md` **in the main checkout's
shared `.agent-work/`** (git-common-dir resolution points the durable trio at one
shared root) containing:

1. **Verdict** — per build item (a/b/c): SHIPPED / HONEST-NULL (already existed,
   with code evidence) / BLOCKED (with the reason).
2. **Evidence** —
   - `python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-232`
     output (the matched worktree path).
   - Your **own measured baseline** (`python -m pytest tests/ -q`, run before any
     change) and the post-change run — both with exit codes and tails.
   - `python scripts/verify_skip_guard.py junit-report.xml` output, with its exit
     code, run on your own branch's `junit-report.xml`.
   - The coverage floor commands (pasted above) run on your branch, with the
     measured percentage and the two-directions proof (`--fail-under=90` passes,
     a higher threshold fails non-zero) if you re-derive it.
   - `which git` output if you attempt any git-less reproduction, proving the
     portability hazard was avoided (or a note that you did not attempt one, if
     out of scope for this issue).
   - The new `_glob_to_regex` property tests, named, with pass output.
   - The item (b) atomic-write regression test, named, with pass output, and a
     one-line note confirming it corrupts a real `_write_meta`-produced file (per
     `lesson:verify-harness-field-and-drive-real-writer`).
   - `grep` output proving the three `run_skill_eval.py` stale phrases and the
     `install_constellation.py` stale comment are gone (the literal acceptance
     text: "grep for the stale phrases returns nothing").
   - The PR number and URL.
3. **Map impact** — what capabilities/seams changed, for the Cartographer's
   reconcile (likely minimal: `_write_meta`'s write semantics, if you consider that
   a capability boundary).
4. **Triage candidates** — out-of-scope discoveries, each as a one-line statement
   (in particular: anything in #219/#220/#239/#242/#243/#244's remaining open
   items you notice but do not absorb, per PR-8).
5. **Workflow feedback** — friction in this launch order, the spine, or the
   tooling. Be blunt; this is the lessons audit's input.

**Deliver before going idle.** Write your result artifact and send your verdict
**before** you go idle: an idle notification with no artifact reads as stalled,
not done. The Admiral judges completion from what you produced, not from a message
that arrives after you have gone quiet.

When you open the PR on Windows, write the body to a temp file and use
`gh pr create -F <file>`.
