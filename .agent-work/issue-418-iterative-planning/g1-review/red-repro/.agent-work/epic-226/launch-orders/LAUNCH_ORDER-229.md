# Launch Order: `commander-229 — issue #229 (epic-226 item C)`

Commanders start cold. Everything you need is pasted below — do not assume you can
open anything referenced by id alone.

## Mission

**Issue #229 — CI: gate merges on the existing 906-test suite + engine coverage floor + skip-guard.**

Deliverable: a merged-ready PR against `fredcai6/constellation-skills` that **authors** a
real, valid, reviewable `.github/workflows/*.yml`, proven correct entirely by **local**
command runs (see Pre-Ruling PR-2b below — this is not optional, it is the whole shape
of this issue).

How it serves the epic intent: the issue's own body names this "the single biggest
evidence gap (x4)" — the suite is green and fast but currently gates nothing. Beyond
that: **#229 is the epic's one encoded structural edge — it blocks #232 (wave 1)**.
F #232's acceptance reads (per PR-2b's cascade) as "green under **C's workflow command
set**, run locally" — meaning the exact command set you write down in your workflow
YAML becomes the literal contract wave 1 is measured against. You must state that
command set **explicitly and unambiguously** in your verdict, not just embed it in YAML
prose, so the next Commander can copy it verbatim without re-deriving it.

**Full issue body, verbatim:**

> Spec S5. The suite is green and fast (~30s) but gates nothing — the single biggest evidence gap (x4).
>
> Build: GitHub Actions workflow on a Windows runner running `pytest tests/`; engine coverage floor pinned at current-minus-1 (measure in-run: `python -m coverage run --include="*/checklist_engine.py" -m pytest tests/test_checklist_engine.py -q && python -m coverage report`); skip-guard: fail the build on unexpected skipped tests (the git-integration tests skipTest silently without git — a runner without git must go RED, not green). Pre-check before building: verify windows-latest provisions git-bash (spec names this assumed-unverified).
>
> Acceptance: a PR with a failing test is blocked; a run where git-integration tests skip is red; floor documented with its measurement command. Out of scope: Linux matrix leg (natural follow-on after B ships), other CI providers, eval runs in CI (governance: evals are a curator instrument, not a merge gate).

**Read this acceptance paragraph through PR-2b before you plan against it.** As written
it reads like a live-PR/live-CI observation ("a PR with a failing test is blocked").
PR-2b supersedes that reading: you demonstrate the same three guard behaviors by
running the workflow's own command set **locally**, not by triggering an Actions run.
That is not a downgrade of the acceptance bar — it is the only form of evidence this
launch order will accept.

## Prior-Wave Verdicts (pasted)

**None — you are wave 0.** No prior-wave verdict exists for this epic; nothing to paste.

Relevant settled history you would otherwise have to rediscover:

- `.github/workflows/` **does not exist in this repo** (confirmed by directory listing at
  launch-order authoring time — `.github` itself is absent). This is a from-scratch build,
  not a fix. There is no pre-existing partial workflow to reconcile against.
- The named skip-guard target is real: `tests/test_checklist_engine.py:1006` —
  `GitChangePolicyCollectorIntegration.setUp` calls `self.skipTest("git not available")`
  when `shutil.which("git") is None`. This is the exact test class your skip-guard must
  catch turning into a silent-green skip on a git-less runner.
- **Do not confuse** `scripts/verify_coverage_ledger.py` / `tests/test_verify_coverage_ledger.py`
  with this issue's "engine coverage floor." That existing script verifies the **skills
  corpus** coverage ledger (external-mechanism-to-home-skill mapping) — an unrelated concept
  that happens to share the word "coverage." Your coverage floor is `python -m coverage`
  (the code-coverage tool) measuring `checklist_engine.py` line coverage under
  `tests/test_checklist_engine.py`. Naming collision only — no code relationship.
- **A #227 is concurrently rewriting `scripts/checklist_engine.py` this same wave.** Your
  coverage floor targets that file's *test suite*, not its internals — you do not need A's
  output to build your workflow, but the coverage percentage you measure will reflect
  whatever `checklist_engine.py` looks like on **your own branch** (based on pre-A `main`),
  not A's post-merge version. State this explicitly as a documented limitation: your
  floor number is a baseline off current `main`, and it is expected to be re-measured
  after wave-0 merges settle (PR-3's batched re-verification), not treated as eternally
  fixed the moment you compute it.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- **PR-2b — ACTIONS UNAVAILABLE, HUMAN AMENDMENT (2026-07-24, quoted verbatim from the
  latitude contract). This is the governing ruling for your entire mission:**

  > Fred: *"my github actions are used up, so let's make the ci but only expect it to run
  > locally."* Therefore:
  > - C #229 **authors** the workflow file correctly (a real, valid, reviewable
  >   `.github/workflows/*.yml` a future runner would execute), but its **acceptance
  >   evidence is local**: run the exact command set the workflow invokes and demonstrate
  >   each guard fires — seeded failing test ⇒ non-zero exit; git-less environment ⇒
  >   skip-guard non-zero, not a silent green; coverage floor measured and documented with
  >   its command.
  > - **No Commander waits on, polls for, or claims a GitHub Actions run.** A verdict
  >   asserting "CI green" without a local command transcript is invalid evidence.
  > - **Cascade:** PR-2's local-gating rule extends to **wave 1** as well. F #232's "green
  >   in CI" acceptance reads as "green under C's workflow command set, run locally."
  > - The pre-check #229 names ("verify windows-latest provisions git-bash") cannot be
  >   settled empirically without a run — it is answered from GitHub's documented runner
  >   image spec and recorded as a **documented assumption**, not a measurement. Say which
  >   it is.
  > - Standing note: this repo is **public**, and public repos normally get unlimited free
  >   Actions minutes, so the cap is more likely a spending-limit/account setting than a
  >   true cap. Flagged to Fred; his constraint governs regardless. If Actions later becomes
  >   available, the workflow is already correct and needs only to be run.

  Concretely, your three pieces of local evidence:
  1. **Seed a failing test** (a throwaway assertion-false test, removed or reverted before
     PR, or a documented seed-then-revert transcript) and show `pytest tests/` (or whatever
     exact invocation your workflow uses) exits non-zero.
  2. **Simulate a git-less run** — e.g. by making `git` unresolvable on `PATH` for a child
     process, or by directly asserting `GitChangePolicyCollectorIntegration` skips and
     showing your skip-guard step (e.g. `pytest --strict-markers` won't do this alone; you
     likely need `-rs` output parsing or `pytest-json-report`/exit-code logic that fails
     the build on any unexpected skip) turns that skip into a non-zero exit. Prove the
     *guard*, not just that the test skips.
  3. **Run the coverage command from the issue body** (`python -m coverage run
     --include="*/checklist_engine.py" -m pytest tests/test_checklist_engine.py -q &&
     python -m coverage report`) and record the resulting percentage as your
     "current-minus-1" floor, with the exact command in your verdict.

  For the windows-latest/git-bash pre-check: cite GitHub's documented `windows-latest`
  runner image spec (the `actions/runner-images` repo's software manifest for the current
  Windows image) showing Git for Windows (which bundles git-bash) is preinstalled. Label
  this explicitly as a **documented assumption**, not a measurement, in your verdict —
  do not phrase it as if you observed it running.

- **PR-7 — VERIFY THE ISSUE'S CLAIMS AGAINST THE CODE BEFORE PLANNING.** Active repo lesson
  `lesson:verify-launch-order-claims-against-code` (2 prior data points, `.agent-work/LESSONS.md`):
  a named defect is sometimes already fixed, and the real live defect is an unnamed sibling.
  This launch order already ran that grep for you at authoring time (see "Relevant settled
  history" above: no `.github/`, the skip-guard target is real at line 1006, no engine
  coverage-floor tooling exists). **You must still independently re-confirm these three
  facts yourself before freezing your plan** — the launch order's characterization is a
  starting point, not a substitute for your own verification, exactly as the lesson requires.
  If your own grep disagrees with what is stated here, the disagreement itself is worth a
  line in your verdict.
- **PR-6 — CANONICAL DOCTRINE SOURCE.** Issue #229 does **not** name any doctrine rider —
  unlike A #227 (two `global-everyone.md` riders) or D #230 (planning-template tag
  convention), C carries no pre-authorized doctrine edit. **Do not edit
  `skills/_shared/global-*.md` or any `skills/<role>/references/global-*.md`** as part of
  this issue. If you find a genuine doctrine gap while building the workflow (e.g. "CI
  expectations" belongs somewhere agents read), that is new scope — float it, do not add it.
- **PR-4 — WORKTREE IS PRE-PROVISIONED.** Do not create or move worktrees; yours already
  exists (see Workspace below). Verify with `--here`, do not `git worktree add` again.
- **PR-8 — STAY IN YOUR LANE ON #219/#220.** If building CI surfaces adjacent friction that
  belongs to #220's surviving items or #219's live threads, **file or comment — do not
  absorb.** Nothing in #229 is a declared #220 absorption (only A #227's three items are).
- **No CI exists yet to gate on for your own PR.** Your own PR to add the workflow has, by
  definition, no pre-existing status check to pass — you are the one creating the first
  check. Do not treat "no CI ran on my PR" as a defect; it is expected for this issue.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report
it with the same rigor as a win. Concretely here: this issue is a from-scratch build (no
`.github/workflows/` exists), so a full honest-null across the whole issue is unlikely —
but if any **sub-piece** turns out to already exist (e.g. a coverage-floor helper script
elsewhere in `scripts/`, or an existing skip-guard convention in another test file), name
it, cite the code, and narrow your build to what is genuinely missing. Per repo doctrine,
every null states what was tested **and what was not**.

## Inherited Latitude

From the latitude contract's Decision Classes table, applied to your mission:

**You may decide, without floating to the Admiral (delegated):**
- Implementation shape of the workflow YAML: job/step naming, file layout under
  `.github/workflows/`, whether the coverage-floor check is inline shell or a small
  helper script — engineering detail the issue leaves open.
- Scope narrowing on an honest-null sub-piece (log it as a RULING in your verdict per the
  contract's "scope change: narrowing" row).
- Bounded fix-now triage: a small in-lane defect you trip over and fix immediately (log as
  a RULING).
- Issue filing/closing for your own issue and for out-of-scope discovery (Triage drains
  those later).
- Merge to main, once your local evidence is green and a reviewer APPROVEs (the contract's
  "Merge to main" row is delegated on exactly those two conditions — no GitHub status
  check exists to also require, per PR-2b).

**You must float to the Admiral (surfaced) — stop and return, do not guess:**
- Any architecture/structural change beyond what the issue already specifies (contract:
  "Architecture / structural change" → surfaced).
- Adding scope, or dropping the issue outright for a reason other than a measured null
  (contract: "Scope change: adding scope, or dropping an issue outright" → surfaced).
- Any production-default or user-visible behavior change beyond the workflow itself
  (contract: "Production defaults / user-visible behavior" → surfaced).
- Any doctrine or shipped-template edit **not** already named by this issue — see PR-6
  above; C names none, so **any** doctrine edit here is surfaced, full stop.
- Anything that doesn't fit a named class at all — always escalates, with one line on why.
- **Hard constraint, not a class but absolute:** triggering, waiting on, polling for, or
  claiming a GitHub Actions run. There is no delegated path to this — it is simply not
  available to you under PR-2b. If you find yourself wanting to "just check it actually
  runs," that impulse itself is the signal to stop and float, not to proceed quietly.

## File Ownership

**Sole writer this wave** of:
- `.github/workflows/**` (new — the workflow YAML and any helper script it invokes, if you
  choose to factor the coverage-floor logic out of inline shell).
- `.agent-work/epic-226/evidence/findings-229.md` — your working findings file (PR-7 grep
  results, running notes, the three local-proof transcripts as you produce them). **One
  writer per document** — you are the sole writer here; no other Commander touches it.
- `.agent-work/epic-226/verdicts/commander-229.md` — your final compiled verdict.

**Fenced — do not write:** `scripts/checklist_engine.py` (issue #227 owns it this wave),
`scripts/install_constellation.py` (#228 owns it), `scripts/grade_lint.py` and planning
templates (#230), `skills/prototyper/**` and `skills/commander/**` (#231),
`skills/_shared/global-*.md` (no rider is named for C — see PR-6).

## Workspace

Absolute worktree path: `C:/Programs/constellation-wt-229`
Branch: `issue-229` · Base: current `main` (confirmed at commit `83a31b1` at launch-order
authoring time)
Provisioned by the Admiral with:
```
git worktree add C:/Programs/constellation-wt-229 -b issue-229 main
```
(Already exists — confirmed present via `git worktree list` at authoring time. Do not
re-create it.)

**First step, before any git operation:** run
`py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-229`
— it must exit 0, proving you are in your own worktree and not the shared checkout. Paste
its output into your return report.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself,
not a local merge that would diverge your worktree from main).

## Inherited Context

**This repo VENDORS its own scripts.** `scripts/checklist_engine.py` and friends in the
repo root are the real ones — drive tooling from the repo copy, not from any
globally-installed `C:/Users/fredc/.claude/skills/...` copy. The two **can diverge**. Same
for templates: prefer `skills/<role>/templates/`.

**Active lessons from `.agent-work/LESSONS.md` that bear on your mission:**

- `lesson:verify-launch-order-claims-against-code` (project / delegated-planning, 2 data
  points) — **directly governs this mission via PR-7 above.** Honor it literally: re-grep
  before you freeze a plan, even though this order already did the first pass for you.
- `lesson:verify-harness-field-and-drive-real-writer` (project / testing) — **directly
  relevant to your skip-guard proof.** Do not fake the git-less scenario with a
  hand-injected fixture that asserts "skip-guard would fail here" in the abstract; drive
  the REAL path — an actual `pytest` invocation in an environment where `git` genuinely
  resolves to nothing (or the real test genuinely skips), then show your guard step's real
  exit code on that real output. A hand-set fixture that never touches the actual
  `skipTest` call would be exactly the self-confirming shortcut this lesson warns about.
- `lesson:test-harness-concurrency-failsafe` (project / testing) — likely not directly
  triggered (you are not writing new concurrent-file-I/O tests), but if your skip-guard
  proof ends up spawning a subprocess pytest run you monitor, apply the same fail-safe
  discipline (timeout, no silent hang) rather than assuming a clean exit.
- `lesson:observe-midprocess-state-not-via-end-output` (handoff / test-authoring) — not
  directly applicable (you are not observing a mid-process hang/kill state); noted for
  completeness since it is in the Active section.

**Platform invariants (Windows):**

- **Command-checks run under a POSIX shell (bash).** Author `grep`/`&&`/pipe checks in
  POSIX form. On a box with no bash the engine stamps `shell: cmd-fallback` and the check
  fails visibly. Your workflow YAML's `runs-on: windows-latest` job should use `shell: bash`
  steps to match this repo's existing POSIX-shell convention, unless you have a specific
  reason to use PowerShell for a given step (say so if you deviate).
- **`gh pr create` body:** write the body to a temp file and use `gh pr create -F <file>`.
  Never a heredoc, never a PowerShell `@'...'@` here-string for `--body` (here-strings work
  for `git commit -m` only).
- Set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you capture
  — cp1252 pipes corrupt captured output silently. This applies to your own local proof
  transcripts (the seeded-failure run, the git-less run, the coverage run) as much as to
  the workflow YAML's `env:` block.
- The Agent-tool `isolation:"worktree"` flag is a **silent no-op** on Windows. Your
  worktree is real because the Admiral provisioned it with `git worktree add` — verify
  with `--here`.

**Charter-lite carrier:** this repo has no `docs/agents/` overlay, so this block is your
doctrine carrier. Beyond it, your inherited globals are `references/global-orchestrator.md`
+ `references/global-everyone.md` bundled with your skill.

**Doctrine you must not re-derive** (it is inherited, not restated per-handoff):
correctness over velocity for promoted behavior; behavior changes are test-led where a
test surface exists; fail visibly rather than emit plausible wrong output; one canonical
path, no speculative abstraction.

## Pre-empted Steps

- **Latitude / authorization:** settled by the Admiral's confirmed latitude contract,
  including the PR-2b human amendment. This launch order IS the ratified intent — satisfy
  `user-decision` checkpoints on your spine by citing it.
- **Issue triage / scoping:** the issue body is frozen as written, its acceptance section
  reinterpreted through PR-2b as described above — do not re-scope it further.
- **Worktree provisioning:** done for you (verify with `--here`, do not create your own).
- **The windows-latest/git-bash pre-check's evidentiary form:** already settled by PR-2b as
  "documented assumption, not measurement." Do not attempt to upgrade it to a measurement
  by triggering a run — that would violate the hard constraint above.

## Data Locations

Untracked inputs absent from your worktree, in the main checkout at
`C:/Programs/constellation-skills`:

- `.agent-work/` (the whole tree — lessons inbox, prior epic archives, the Admiral's live
  spine). **Read-only for you**, except your two owned files under
  `.agent-work/epic-226/evidence/` and `.agent-work/epic-226/verdicts/` (git-common-dir
  resolution points the durable trio at one shared root, same as #227's pattern).
- GitHub's `windows-latest` runner image software manifest is an **external** reference
  (the `actions/runner-images` repository's documented image spec), not a repo path — cite
  the specific manifest/version you read when you record the documented assumption.

## Budget

- **Model tier (required):** **sonnet** — per the latitude contract's explicit assignment
  (B #228, C #229, E #231, F #232 all run Sonnet; only A #227 and D #230 are Opus). Crew
  (implementer/reviewer) also run at **sonnet**. **No Fable at any tier.**
- **Compute/time, session-window:** you are one of up to five concurrent wave-0 Commanders
  drawing on a shared usage pool (the contract's fallback, if the pool shows strain, is a
  3-then-2 split with **A, C, D dispatched first** — you are explicitly in the first batch
  because you unblock wave 1). Keep crew dispatches tight; do not spawn speculative
  parallel crews. If you hit a session limit mid-flight, write your state to your spine and
  return — do not silently die.

## Stop Conditions

Stop and return when:

- A decision listed as **float to the Admiral** above is needed — including, explicitly,
  any impulse to trigger/poll/wait on a real GitHub Actions run to "just double-check."
  That is never a resolution path here; float instead.
- Your scope would exceed the issue's declared boundaries (Linux matrix leg, other CI
  providers, eval-runs-in-CI — all explicitly out of scope in the issue body).
- The 906-test suite (or whatever count your own collection run shows — re-verify the
  number, don't just cite "906" from the issue title) goes red in a way you cannot
  attribute to your own change within a bounded effort — return with the failure
  attributed by a `uniq -c`-style command over the failure list, never from the pytest
  tail alone.
- You cannot produce local evidence for one of the three guards (seeded-failure, git-less
  skip-guard, coverage floor) within a bounded effort — that is a BLOCKED verdict for that
  item, escalate rather than shipping unproven YAML.
- Budget crossed, or evidence for an acceptance item proves impossible to produce.
- You need **context this order does not cover and cannot safely proceed without** —
  return-and-query the Admiral (it answers and continues you). Asking up is always
  sanctioned.

## Return Shape

Write `.agent-work/epic-226/evidence/findings-229.md` as your working findings file, and
`.agent-work/epic-226/verdicts/commander-229.md` (**in the main checkout's shared
`.agent-work/`** — git-common-dir resolution points the durable trio at one shared root)
as your final compiled verdict, containing:

1. **Verdict** — per guard (workflow authorship / seeded-failure guard / skip-guard /
   coverage floor): SHIPPED / HONEST-NULL (already existed, with code evidence) / BLOCKED
   (with the reason). State plainly whether the windows-latest/git-bash pre-check is a
   documented assumption or a measurement (it must be the former).
2. **The exact command set your workflow invokes, written out verbatim and unambiguously**
   — this is not optional flourish, it is the literal artifact #232's wave-1 Commander will
   copy to prove "green under C's workflow command set, run locally." If it is buried only
   inside YAML syntax, restate it as a plain shell transcript in the verdict body.
3. **Evidence** —
   - `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-229`
     output (the matched worktree path), proving you worked in isolation.
   - The seeded-failing-test transcript: command + non-zero exit code, with the seed
     reverted/removed before your PR (state how you reverted it).
   - The git-less-run transcript: how you simulated no-git, the command, and the non-zero
     exit code your skip-guard step produced.
   - The coverage-floor transcript: the exact `python -m coverage run ...` command from the
     issue body, its output, and the resulting floor number you are pinning as
     "current-minus-1."
   - The documented-assumption citation for windows-latest/git-bash (which GitHub manifest,
     what it says).
   - The PR number and URL.
4. **Map impact** — what capabilities/seams changed, for the Cartographer's reconcile
   (a new CI surface is itself a map-relevant addition).
5. **Triage candidates** — out-of-scope discoveries (especially anything belonging to
   #220's surviving items or #219's live threads), each as a one-line statement.
6. **Workflow feedback** — friction in this launch order, the spine, or the tooling. Be
   blunt; this is the lessons audit's input.

**Deliver before going idle.** Write your result artifacts and send your verdict **before**
you go idle: an idle notification with no artifact reads as stalled, not done. The Admiral
judges completion from what you produced, not from a message that arrives after you have
gone quiet.

When you open the PR on Windows, write the body to a temp file and use
`gh pr create -F <file>`.
