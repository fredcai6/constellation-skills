# Launch Order: `commander-228 — issue #228 (epic-226 item B)`

Commanders start cold. Everything you need is pasted below — do not assume you can
open anything referenced by id alone.

## Mission

**Issue #228 — install: resolve the Python launcher at install time — stop
hardcoding `py` in skill bodies.**

Deliverable: a merged-ready PR against `fredcai6/constellation-skills` implementing
the build item below, with the acceptance evidence pasted into your verdict.

How it serves the epic intent: epic-226 is "spend agent effort on the actual problem
instead of the scaffolding." This issue is the direct portability half of that —
the design excursion that named it (`x4-testability`, cited below) found the failure
mode is real and recurring: an agent on a fresh non-Windows box burns tokens
discovering `python3` the hard way because installed skill bodies hardcode `py`. The
fix is cheap and portability-defining: resolve the interpreter once, on the real
install host, and stamp it into what ships — never re-discovered per invocation.

**Full issue body, verbatim:**

> Spec S4 (design settled by excursion x4's explicit three-option comparison —
> env-var and wrapper-script options assessed and rejected; per-install rewrite
> recommended).
>
> Build: install_constellation.py probes the target host once (`py` → `python3` →
> `python`, first that answers `--version`) and stamps the resolved interpreter into
> the installed SKILL.md copies + a small sidecar consumed by engine-invoking
> command strings. Repo source keeps `py` as the Windows-dev default; the installed
> copies name an interpreter that exists on that host.
>
> Acceptance: installer test asserting the stamped interpreter resolves on the
> install host; a simulated `py`-less install names a working interpreter; existing
> install/fingerprint tests green (mind #197's path-invariant corpus_id behavior).
> Out of scope: containerized runtimes; cross-harness (Codex) work (#219 thread 3).

## Prior-Wave Verdicts (pasted)

None — you are wave 0. No prior-wave verdict exists for this epic.

Relevant settled history you would otherwise have to rediscover:

- **The design record**, `excursions/x4-testability-RESULT.md` (archived; see Data
  Locations), assessed three options and its own words are the spec: *"(a) env-var
  config (`CONSTELLATION_PY`): pushes setup onto every user/host; brittle... Reject.
  (b) probe-once wrapper script: good for repo-level scripts, but the brittle callers
  are agent-read SKILL.md prose... insufficient for skill bodies. (c) per-install
  rewrite — recommended... probe the target host once (`py` → `python3` → `python`,
  first that answers `--version`) and stamp the resolved interpreter into the
  installed SKILL.md copies (and a tiny sidecar the engine-invoking commands read).
  The probe runs once, on the real machine, so every skill body then names an
  interpreter that exists — zero per-invocation token burn, and the repo source can
  keep `py` as the Windows-dev default."* Do not re-litigate (a) or (b); they are
  closed roads.
- **A partial mechanism already exists — read it before you plan (this is PR-7 in
  practice, already run once by the Admiral; re-verify it yourself, do not trust this
  paraphrase blind).** `scripts/install_constellation.py:235-241` has
  `_platform_interpreter()`:
  ```python
  def _platform_interpreter() -> str:
      """Interpreter for installed command strings: the `py` launcher on Windows,
      `python3` elsewhere. ..."""
      return "py" if os.name == "nt" else "python3"
  ```
  and it is already wired into `rewrite_installed_skill_paths` (same file, ~line 244),
  which rewrites the literal token `"python <"` → `f"{_platform_interpreter()} <"` in
  every installed `.json`/`.md`/`.txt` file. **This is a real but partial answer** —
  it picks an interpreter name, and it does get baked into installed bodies. What it
  does **not** do, on the Admiral's read: (1) **no host probe** — it never actually
  runs `py --version` / `python3 --version` / `python --version`; it branches purely
  on `os.name == "nt"`, so a Windows host without a working `py` launcher (a real,
  if uncommon, configuration — e.g. a python.org install with the launcher
  unchecked) would still be stamped `"py"` and the acceptance criterion "a simulated
  `py`-less install names a working interpreter" would fail; (2) **no three-way
  fallback chain** — `python3`/`python` are never tried in sequence, non-Windows
  always gets `python3` unconditionally; (3) **no sidecar file** — only in-body text
  rewriting exists, nothing "a small sidecar consumed by engine-invoking command
  strings" as the issue names. Treat items (1)–(3) as the live, unshipped work. If
  your own grep finds this differently — e.g. a sidecar already exists elsewhere, or
  the probe logic has moved since this was written — report the honest null for
  whichever sub-item is actually already done, and spend effort on what remains.
- **#197's path-invariant `corpus_id` behavior (named directly in the issue's
  acceptance line) is a real interaction to check, not just a caution to note.**
  `scripts/run_skill_eval.py:492` (`stable_corpus_id`) normalizes the **install-root
  path** baked into installed files before hashing, so two installs of the same
  corpus at different temp paths hash identically
  (`tests/test_run_skill_eval.py:601`, `test_corpus_id_install_path_invariant`). It
  does **not** normalize interpreter tokens. `_platform_interpreter()` already varies
  installed bytes by `os.name` today, so some host-conditioned variance in
  `corpus_id` already exists pre-#228 — your job is to confirm your change does not
  **newly** break `test_corpus_id_install_path_invariant` or the raw
  `compute_corpus_id`/fingerprint tests in `tests/test_install_constellation.py`, not
  to redesign #197's normalization. If your probe-based resolution makes the same
  host resolve differently across two installer runs (flaky probe), that **would**
  be a new #197-shaped regression — worth explicit attention in your test design.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when
overriding.

- **PR-7 — VERIFY THE ISSUE'S CLAIMS AGAINST THE CODE BEFORE PLANNING.** Active repo
  lesson with two prior data points: a launch order's named defect is sometimes
  already fixed, and the real live defect is an unnamed sibling. The Admiral's own
  first pass above found `_platform_interpreter()` partially shipped — before you
  freeze a plan, re-run that grep yourself (`_platform_interpreter`,
  `rewrite_installed_skill_paths`, any existing `sidecar`/`CONSTELLATION_PY`-shaped
  name) against current `scripts/install_constellation.py` and its tests, and record
  what you find independently. Do not simply cite the Admiral's paraphrase as your
  own verification.
- **Design-it-twice is PRE-SATISFIED for the headline design.** The issue records the
  design as settled by excursion x4's explicit three-option comparison (pasted
  above). You do **not** re-run design-it-twice on the overall shape (probe-then-
  stamp, per-install rewrite). You DO run it, or record an untaken road, for any
  load-bearing interface you invent that x4 did not settle — most likely the
  sidecar's exact file format/name and where it lives in the installed tree, since
  future consumers (engine-invoking command strings, per the issue) bind to that
  shape.
- **PR-6 — CANONICAL DOCTRINE SOURCE.** This issue names no doctrine riders. If, in
  the course of the work, you find a genuine need to edit shared doctrine (e.g. to
  document the sidecar contract for future skill authors), that edit targets
  `skills/_shared/global-*.md` — **never** `skills/<role>/references/global-*.md`
  (install-time copies `install_constellation.py` regenerates; an edit there is
  silently overwritten). Per the Decision Classes table, adding a doctrine edit not
  already named by the issue is **surfaced**, not delegated — float it rather than
  writing it unilaterally.
- **PR-2 — NO CI EXISTS YET.** `.github/workflows/` does not exist in this repo;
  issue #229 is building it in parallel with you. Your PR therefore has **no status
  checks**. Your acceptance evidence is the **locally-run** `py -m pytest tests/ -q`
  exit code and tail, pasted into your verdict. Do not wait for, or claim, a green
  CI run.
- **Installer self-test caution (bespoke to this issue, same spirit as A's PR-1).**
  You are changing what `install_constellation.py` writes into skill bodies. Never
  run an install (real or test) that targets the **live, shared skills roots** other
  agents in this epic are currently running from — not the repo's own installed
  copies under any project's `.claude/skills`, not any user-level
  `~/.claude/skills`. Every install you exercise, real or simulated, writes to a
  `tmp_path`/temp directory, exactly as the existing `test_install_constellation.py`
  fixtures already do. This is a straightforward extension of that file's existing
  pattern, not a new discipline to invent.
- **PR-5 — sole file ownership this wave.** No other wave-0 issue touches
  `scripts/install_constellation.py`. You have sole ownership of it this wave; see
  File Ownership below for the fence around adjacent files you do **not** own.
- **PR-8 — STAY IN YOUR LANE ON #219/#220.** The issue's own out-of-scope line names
  "cross-harness (Codex) work (#219 thread 3)" explicitly — do not touch it. If you
  find other adjacent ergonomics defects belonging to #219's live threads or #220's
  surviving items, **file or comment — do not absorb.**

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable.
Report it with the same rigor as a win. Concretely here: if your PR-7 re-verification
confirms part of the mechanism already exists (e.g. the interpreter-name selection),
"this sub-item already shipped — here is the code proving it, here is what I verified
and what I did NOT verify" is a **success** for that sub-item, not a shortfall — spend
the saved effort on the genuinely missing probe/fallback/sidecar work. Per repo
doctrine, every null states what was tested **and what was not**; a null with an
empty scope is an unfinished result.

## Inherited Latitude

You may decide, without floating to the Admiral:

- Implementation shape: how the host probe is structured (subprocess calls, timeout
  handling, error paths), file layout inside `scripts/`, test organization, naming.
- The sidecar's exact file name, format, and location within the installed tree (it
  is an internal contract this issue is minting; no external consumer is named yet
  beyond "engine-invoking command strings").
- Narrowing scope where a sub-item proves already-shipped (honest null, evidence
  pasted) — e.g. if the interpreter-name selection is judged sufficient and only the
  probe/fallback/sidecar are genuinely new work.
- Bounded fix-now triage: a small defect you trip over and fix in-lane.
- Whether the probe result is cached anywhere beyond the sidecar, and how the
  `py`-less simulation is constructed for the test (e.g. a `PATH`-shadowing fixture).

You must **float to the Admiral** (stop and return, do not guess):

- Any doctrine edit beyond what the issue already specifies (none is named — so any
  doctrine edit at all is a float, per PR-6 above).
- Adding scope, or dropping the build item for a reason other than a measured null.
- Containerized-runtime support or cross-harness (Codex) work — both are explicit
  out-of-scope lines in the issue; treat a temptation to fold either in as a scope
  addition, which floats.
- Any change to `#197`'s `stable_corpus_id` normalization logic itself (as opposed to
  verifying your change doesn't break it) — that is a settled fix from a prior issue,
  not yours to reopen.
- Any change to user-visible engine behavior beyond what the issue specifies (e.g.
  changing what an installed skill body's commands *do*, not just which interpreter
  name they're prefixed with).
- Anything that would require touching another wave-0 issue's files
  (`scripts/checklist_engine.py`, `.github/workflows/**`, `scripts/grade_lint.py` and
  planning templates, `skills/prototyper/**`, `skills/commander/**`).

Asking up is always sanctioned. If you need epic-level context this order does not
carry, **return-and-query the Admiral** — it answers and continues you. That is a
first-class move, not a failure.

## File Ownership

**Sole writer this wave** of:
- `scripts/install_constellation.py`
- `tests/test_install_constellation.py` and any new test module you add for the
  probe/fallback/sidecar tests
- The sidecar file's format definition (wherever you site it — likely inline in
  `install_constellation.py` plus a fixture/doc comment, not a shared doctrine file
  per PR-6)

**Fenced — do not write:** `scripts/checklist_engine.py` (issue #227 owns it this
wave), `.github/workflows/**` (issue #229 owns it), `scripts/grade_lint.py` and
planning templates (#230), `skills/prototyper/**` and `skills/commander/**` (#231).
**Read-only, verify-don't-edit:** `scripts/run_skill_eval.py` (owns `stable_corpus_id`
from #197) — run its existing tests to confirm you haven't broken the invariant; do
not modify its normalization logic.

Your findings file: `.agent-work/epic-226/evidence/findings-228.md`.

## Workspace

Absolute worktree path: `C:/Programs/constellation-wt-228`
Branch: `issue-228` · Base: current `main`
Provisioned by the Admiral with:
```
git worktree add C:/Programs/constellation-wt-228 -b issue-228 main
```

**First step, before any git operation:** run
`py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-228`
— it must exit 0, proving you are in your own worktree and not the shared checkout.
Paste its output into your return report.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR
itself, not a local merge that would diverge your worktree from main).

## Inherited Context

**This repo VENDORS its own scripts.** `scripts/install_constellation.py` in the
repo root is the real one — drive the installer from the repo copy, not from any
globally-installed `C:/Users/fredc/.claude/skills/...` copy. The two **can diverge**.
Same for templates: prefer `skills/<role>/templates/`.

**Active lessons from `.agent-work/LESSONS.md` that bear on your mission:**

- `lesson:verify-launch-order-claims-against-code` (project / delegated-planning, 2
  data points): verify a launch order's named defect against the current code before
  planning — a headline mechanism already shipped becomes an honest null, and the
  real live recurrence may be a different, unnamed sibling. **This is why PR-7 exists
  and why the Admiral's own partial-mechanism finding above is offered as a starting
  point to re-verify, not a conclusion to inherit.**
- `lesson:verify-harness-field-and-drive-real-writer` (project / testing): when a
  decision depends on a harness-supplied payload/condition, verify it against the
  real contract AND make the regression test drive the REAL path, not a hand-injected
  fixture. **Directly relevant to the "simulated `py`-less install names a working
  interpreter" acceptance criterion:** the test must actually make `py` unresolvable
  to the real probe (e.g. shadow `PATH`, or monkeypatch the subprocess call at the
  boundary the probe genuinely calls) and observe the probe fall through to
  `python3`/`python` — asserting a hand-set "resolved interpreter" fixture value
  would be exactly the self-confirming test this lesson warns against.

**Platform invariants (Windows):**

- **Command-checks run under a POSIX shell (bash).** Author `grep`/`&&`/pipe checks
  in POSIX form. On a box with no bash the engine stamps `shell: cmd-fallback` and
  the check fails visibly.
- **`gh pr create` body:** write the body to a temp file and use `gh pr create -F
  <file>`. Never a heredoc, never a PowerShell `@'...'@` here-string for `--body`
  (here-strings work for `git commit -m` only).
- Set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you
  capture — cp1252 pipes corrupt captured output silently.
- The Agent-tool `isolation:"worktree"` flag is a **silent no-op** on Windows. Your
  worktree is real because the Admiral provisioned it with `git worktree add` —
  verify with `--here`.

**Charter-lite carrier:** this repo has no `docs/agents/` overlay, so this block is
your doctrine carrier. Beyond it, your inherited globals are
`references/global-orchestrator.md` + `references/global-everyone.md` bundled with
your skill.

**Doctrine you must not re-derive** (it is inherited, not restated per-handoff):
correctness over velocity for promoted behavior; behavior changes are test-led where
a test surface exists; fail visibly rather than emit plausible wrong output; one
canonical path, no speculative abstraction.

## Pre-empted Steps

- **Latitude / authorization:** settled by the Admiral's confirmed latitude contract.
  This launch order IS the ratified intent — satisfy `user-decision` checkpoints on
  your spine by citing it.
- **Design-it-twice on the headline design:** pre-satisfied by excursion x4's
  three-option comparison (pasted above). Record it as pre-empted; run it only for a
  new load-bearing interface x4 did not settle (see Pre-Rulings) — most likely the
  sidecar's shape.
- **Issue triage / scoping:** the issue body is frozen as written. Do not re-scope
  it.
- **Worktree provisioning:** done for you (verify with `--here`, do not create your
  own).

## Data Locations

Untracked inputs absent from your worktree, in the main checkout at
`C:/Programs/constellation-skills`:

- `.agent-work/` (the whole tree — lessons inbox, prior epic archives, the Admiral's
  live spine). **Read-only for you.**
- The design record: `.agent-work/archive/2026-07-24-explore-design-thrust/excursions/x4-testability-RESULT.md`
  (pasted in relevant part above). If you need more of it than what's pasted, that is
  a context query for the Admiral, not a reason to redesign.

## Budget

- **Model tier (required):** **sonnet** — per the latitude contract's tier table,
  #228 is not one of the two design-heavy issues (A #227, D #230) that draw opus.
  Crew (implementer/reviewer) also run at **sonnet**. **No Fable at any tier.**
- **Compute/time, session-window:** you are one of five concurrent wave-0 Commanders
  drawing on a shared usage pool. Keep crew dispatches tight; do not spawn
  speculative parallel crews. If you hit a session limit mid-flight, write your state
  to your spine and return — do not silently die.

## Stop Conditions

Stop and return when:

- A decision listed as **float to the Admiral** above is needed.
- Your scope would exceed the issue's declared boundaries (containerized runtimes,
  cross-harness/Codex work).
- The suite goes red in a way you cannot attribute to your own change within a
  bounded effort — return with the failure attributed by a `uniq -c`-style command
  over the failure list, never from the pytest tail alone.
- `test_corpus_id_install_path_invariant` or another #197-adjacent fingerprint test
  breaks in a way your own change plausibly caused and you cannot resolve without
  touching `run_skill_eval.py`'s normalization logic — that edit is out of your file
  ownership and floats.
- Budget crossed, or evidence for an acceptance item proves impossible to produce.
- You need **context this order does not cover and cannot safely proceed without** —
  return-and-query the Admiral (it answers and continues you). Asking up is always
  sanctioned.

## Return Shape

Write `.agent-work/epic-226/verdicts/commander-228.md` **in the main checkout's
shared `.agent-work/`** (git-common-dir resolution points the durable trio at one
shared root) containing:

1. **Verdict** — per sub-item (host probe, three-way fallback chain, sidecar,
   SKILL.md stamping): SHIPPED / HONEST-NULL (already existed, with the code
   evidence) / BLOCKED (with the reason).
2. **Evidence** —
   - `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-228`
     output (the matched worktree path), proving you worked in isolation.
   - `py -m pytest tests/ -q` exit code + tail, run on your branch.
   - The new installer test asserting the stamped interpreter resolves on the
     install host, and the simulated `py`-less install test — named, with their pass
     output, and a note on how the `py`-less condition was genuinely induced (per the
     verify-harness-field lesson above, not a hand-set fixture).
   - `tests/test_install_constellation.py` full run, and
     `test_corpus_id_install_path_invariant` specifically, both green.
   - The PR number and URL.
3. **Map impact** — what capabilities/seams changed (the sidecar contract, in
   particular, since future skill/engine consumers bind to it), for the
   Cartographer's reconcile.
4. **Triage candidates** — out-of-scope discoveries (especially anything belonging
   to #219's live threads or #220's surviving items), each as a one-line statement.
5. **Workflow feedback** — friction in this launch order, the spine, or the tooling.
   Be blunt; this is the lessons audit's input.

**Deliver before going idle.** Write your result artifact and send your verdict
**before** you go idle: an idle notification with no artifact reads as stalled, not
done. The Admiral judges completion from what you produced, not from a message that
arrives after you have gone quiet.

When you open the PR on Windows, write the body to a temp file and use `gh pr create
-F <file>`.
