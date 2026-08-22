# Plan Critic — w2-reindex pre-commit hook (index-snapshot mechanism)

Cold read of `MISSION_FRAME.md` and `PLAN_ALTERNATIVES.md` only. Several findings below were
spot-checked against the live repo state (this checkout is itself one of the objects under
scrutiny — it is a linked worktree of a shared `.git`), and those checks are cited inline.

---

## 1. Shared hooks directory gives one lane's install a blast radius over every sibling lane

**Defect.** `git worktree list` in this exact checkout right now shows nine linked worktrees
sharing one common `.git`:

```
constellation-skills  [main]
569-w1-verdict         [epic-569/w1-verdict]
569-w1-wiring          [epic-569/w1-wiring]
569-w2-basis           [epic-569/w2-basis]
569-w2-ledger          [epic-569/w2-ledger]
569-w2-reindex         [epic-569/w2-reindex]   <- this mission
fix/win-hook-command-word
fix/win-path-semantics
fix/532-resolved-interpreter-fallback
fix/539-hook-interpreter-portable
```

`git rev-parse --path-format=absolute --git-path hooks` resolves to the identical
`/home/tommy/projects/constellation-skills/.git/hooks` from every one of these checkouts
(`extensions.worktreeConfig` is unset, confirmed via `git config --get extensions.worktreeConfig`
returning empty — there is no per-worktree hooks override available here). The plan already knows
the hooks dir is shared (that is exactly why it insists on `--git-path hooks` over a hardcoded
join), but it treats "shared" only as an installer-correctness fact ("write to the right place"),
never as a **blast-radius** fact: installing the hook once, from *this* lane's self-install run,
silently starts intercepting every commit made in the other eight worktrees too — including two
sibling wave-2 lanes (`569-w2-basis`, `569-w2-ledger`) that are active concurrently right now, and
four `win-fix-*` lanes on unrelated branches that never ran this mission's installer and have no
reason to expect a new git hook governing their commits.

**Why it matters.** A Commander crew in `569-w2-basis` making a routine commit could have its
staged content silently rewritten (a `map/INDEX.md`/`ids.jsonl` add on top of whatever it staged)
by a hook that a *different* lane's crew installed, with no notice, no opt-out per-worktree, and no
test anywhere in the gate plan that checks "an unrelated sibling worktree, on a branch that never
asked for this hook, still gets it and that's either fine or explicitly handled." Gate 3's
"second-worktree-also-fires-correctly" case treats this as a feature to demonstrate, not a
cross-lane coordination risk to gate.

**Severity: blocking.**

---

## 2. Concurrent commits from sibling worktrees race on the index-snapshot machinery

**Defect.** Given finding 1, two sibling worktrees can commit at literally the same moment (this is
the epic's own operating model — parallel wave lanes). Each concurrent commit runs
`git write-tree` → `git commit-tree` → `git worktree add --detach <path> <commit>` against the
*same shared* `.git`. The plan never states: (a) how the ephemeral worktree's path is chosen (fixed
name vs. per-invocation-unique, e.g. a PID/mktemp-derived path), (b) what happens if two concurrent
invocations pick a colliding path or colliding worktree-admin name, (c) whether `git worktree add`
under concurrent load from two processes against one shared `.git/worktrees/` admin area is
exercised anywhere. `git worktree add` does take internal locks, but the plan's own gates never
name a "two commits, two sibling worktrees, same instant" test case — only a sequential
"second-worktree-also-fires-correctly" case.

**Why it matters.** A collision or lock contention here either (a) corrupts one of the two
concurrent builds (wrong tree gets checked out/read), or (b) makes one hook invocation error out —
which fail-open is supposed to swallow, but see finding 3 for why fail-open doesn't fully cover
this class of failure. This is not a hypothetical edge case for this repo; it is the literal shape
of concurrent wave-2 lane execution happening in this worktree layout today.

**Severity: blocking.**

---

## 3. No timeout anywhere — fail-open covers crashes, not hangs

**Defect.** The mission frame's hard constraint is "the hook must never fail/block the commit."
The plan's mechanism is a "fail-open shim... mirroring `gauge_writer_hook.py`'s documented
always-exit-0 contract" — but always-exit-0 only protects against the hook *raising*. It does
nothing if the hook *hangs*: `git worktree add` can block on a lock file
(`.git/worktrees/<name>/locked`) held by a concurrent invocation (finding 2), and
`python -m scripts.code_map build` walking a corpus on a slow or network-mounted filesystem, or
stalled behind an interactive prompt some git subprocess unexpectedly opens, can hang indefinitely.
No gate, no candidate description, and no framing-block line mentions a timeout or a watchdog
anywhere in either document.

**Why it matters.** A hung pre-commit hook blocks the commit exactly as hard as a crashing one that
isn't caught — worse, because a crash is visible and a hang looks like "git is just slow," and the
developer's only recourse is Ctrl-C, which can leave a half-created worktree/lock behind (compounds
finding 2 and finding 8). This directly violates the plan's own stated "never fail/block the
commit" contract in a mode the fail-open try/except cannot catch.

**Severity: blocking** (this is explicitly the sharpest of the named hazards the task called out,
and the plan is silent on it).

---

## 4. The copy-back path from the ephemeral snapshot worktree to the real index is never specified

**Defect.** The mechanism as described: build a synthetic tree via `write-tree`/`commit-tree`,
materialize it into a detached worktree via `git worktree add`, and presumably run
`code_map build` there. But Gate 1's description ("a staleness-compare + exact-two-path stage
function") and the candidate comparison never say **how the built bytes get from that ephemeral,
separately-rooted worktree back into the real commit's index/working tree.** `git add --
map/INDEX.md map/ids.jsonl` (the exact-two-path staging mechanism both candidates converge on) has
to run somewhere that can see both the newly-built content and the real repo's working
directory/index — but the build itself, by construction, ran in a *different* directory tree (the
ephemeral worktree), not the real one. Options exist (copy the two files' bytes across; or
`git read-tree`/`git checkout-index` the two blobs directly from the synthetic tree into the real
index) but the plan names none of them, and this is exactly the kind of mechanical step where a
naive implementation (e.g. a recursive copy of the built `--out`/`--artifacts` directories) could
reintroduce the very "stage more than two paths" leak the plan is otherwise careful to guard
against with an explicit two-path `git add`.

**Why it matters.** This is the single most load-bearing mechanical step in the "most-testable"
design — it is the actual bridge between "we built the right content" and "we staged the right
content" — and it is asserted, not designed. A hostile reviewer implementing Gate 1 from this
document alone would have to invent this step from scratch with no guidance on which approach
preserves the "exactly two paths" and "byte-identical modulo real changes" guarantees the rest of
the plan depends on.

**Severity: blocking.**

---

## 5. Index-snapshot truth source diverges from `MapTreeFreshnessTests`' truth source on partial-hunk commits

**Defect.** Read directly: `scripts/code_map/discovery.py`'s `tracked_python_files()` calls
`git ls-files` to get the *list* of tracked paths, but `scripts/code_map/extract.py`'s
`build_table(path)` does `open(path, encoding="utf-8").read()` — it reads **live working-tree file
bytes off disk**, not git blob/tree content. `tests/test_code_map.py::MapTreeFreshnessTests`
inherits this: its `_fresh_build()` calls `code_map build --root <ROOT>` where `ROOT` is the actual
checkout directory, so the freshness test's notion of "fresh" is **whatever is currently sitting on
disk for tracked files** — staged or not, dirty or not.

The plan's index-snapshot mechanism is explicitly designed to do the opposite: build from
`git write-tree`'s snapshot of **only the index** (what's about to be committed), specifically so a
partial-hunk commit (`git commit -p`) with unstaged remainder left in the working tree doesn't leak
into the build. That is the correct behavior *for the hook's own job*. But it means: immediately
after such a partial-hunk commit, the hook's freshly-staged `map/INDEX.md`/`ids.jsonl` reflect the
**staged-only** tree, while a subsequent run of `MapTreeFreshnessTests` (in the same working
directory, with the unstaged remainder of that same file still on disk) will rebuild from the
**working-tree-including-unstaged-remainder** content and can legitimately disagree with what the
hook just committed — not because the hook did anything wrong, but because the hook and the
freshness test are answering two different questions ("what matches the tree just committed" vs.
"what matches the file bytes on disk right now") that happen to coincide in every case except
partial-hunk commits with a residual unstaged diff on the *same* file.

**Why it matters.** Gate 3's own required evidence includes "both partial-commit shapes for real"
*and* "a final regression check that... the full local suite is still green." Those two evidence
items can genuinely conflict in exactly the scenario both candidates claim to have "reproduced and
verified" — and neither document's description of that reproduction says whether they ran
`MapTreeFreshnessTests` itself immediately afterward with the unstaged remainder still present. If
they didn't, the plan's central claim to have solved the partial-commit hazard is unverified against
the one test the mission requires to stay green.

**Severity: blocking.**

---

## 6. Full build-and-materialize cost is paid unconditionally on every single commit, and is never measured

**Defect.** The mission frame re-confirms only that `python -m scripts.code_map build --root .`
itself takes "2.9 seconds and is deterministic." Nothing in either document measures the *added*
cost of `git write-tree` + `git commit-tree` + `git worktree add --detach` (which materializes a
full checkout of the snapshot tree to disk) that the chosen mechanism pays before it can even ask
"is anything stale." The mission frame's own "decision pressure" list explicitly names "how to
detect staleness cheaply... full rebuild vs. incremental hash-compare" as a question this run must
decide — but the converged plan's Gate 1 description ("builds from an index snapshot... so the
build input is provably the tree about to be committed") implies the full worktree-materialize-plus-
build path runs unconditionally on *every* commit, with no cheap pre-check to skip it when nothing
under the mappable corpus changed. That decision-pressure item is never explicitly answered on the
record in `PLAN_ALTERNATIVES.md` — the plan just enacts one branch of it without naming the choice.

**Why it matters.** This hook runs on *every commit, in every one of the nine currently-live
worktrees, forever* (per finding 1). A cost that's fine once is a real tax paid on every commit —
including commits that touch nothing under the mappable corpus (a one-line doc fix, a `.md` note) —
and it is entirely unmeasured. If the added machinery costs even a few seconds per commit, that is
a materially different UX than the "2.9s and deterministic" number the plan leans on, and nobody
has checked.

**Severity: should-fix.**

---

## 7. Worktree-awareness is proven only for *install-time* directory resolution, not *run-time* code resolution across differently-versioned sibling worktrees

**Defect.** Both candidates verify `git rev-parse --path-format=absolute --git-path hooks` for
**where the installer writes the hook**. Neither document says how the installed hook resolves
**which copy of `scripts/hooks/*.py` / `scripts/code_map/` to execute** at commit time. Given
finding 1 (one shared hook governs nine worktrees on different branches/commits — some of which, by
definition, predate this mission and may not even have `scripts/code_map/` in the shape this hook
expects), the run-time resolution question is at least as load-bearing as the install-time one: does
the shim resolve the code relative to the *invoking* worktree (`git rev-parse --show-toplevel` at
hook run time, which correctly varies per worktree) or via a path baked in at install time (which
silently binds every worktree's commits to whichever single worktree happened to run the installer,
and breaks for all of them if that worktree is later deleted or moved, e.g. after this epic's
branch merges and its worktree is cleaned up)? The plan is silent on this distinction entirely.

**Why it matters.** This repo's own recent commit history (`f315d7bf fix(mcp): make the door's
interpreter portable by measurement (#553, #575)`, plus three more live sibling branches —
`fix/win-hook-command-word`, `fix/532-resolved-interpreter-fallback`,
`fix/539-hook-interpreter-portable` — all currently checked out as worktrees in this exact
environment) shows this repo has *just* spent multiple branches fixing exactly this class of
problem for a different hook family (Claude Code's PostToolUse hooks / the MCP door). The plan
shows no evidence of consulting or even being aware of that prior art before proposing a new hook
mechanism with the same shared-hooks-directory, multi-worktree shape.

**Severity: should-fix.**

---

## 8. No cleanup story for ephemeral worktrees / dangling commit objects, especially on the fail-open path

**Defect.** `git worktree add --detach` materializes a full checkout on disk and registers
`.git/worktrees/<name>/` admin state; `git commit-tree` creates a real (if unreferenced) commit
object. Neither document mentions removing the worktree (`git worktree remove` + prune) or garbage
collecting the synthetic commit after use — and critically, doesn't say this cleanup happens even
on the **fail-open / exception / hang-then-killed** path, which is exactly when cleanup is easiest
to skip (the code path that's supposed to "swallow everything and exit 0" is the one place a
"remove what I just created" step is most likely to get dropped or itself throw).

**Why it matters.** A worktree or dangling-commit leak on every failure accumulates disk usage and
`.git/worktrees/` admin clutter over the lifetime of a repo that (per finding 1) commits across nine
concurrently-active worktrees; left long enough, colliding or stale worktree-admin entries can start
producing *new* failures for `git worktree add` itself (e.g. "already exists" for a fixed name, or
`git worktree list` noise), which is a second-order way the mechanism could degrade the very
commits it's meant to protect.

**Severity: should-fix.**

---

## 9. Fail-open has zero observability — a silently-dead hook regresses to exactly the pre-mission failure mode, undetected

**Defect.** The chosen fail-open contract ("mirroring `gauge_writer_hook.py`'s... always-exit-0...
Silence is an acceptable outcome") is copied wholesale from a best-effort telemetry writer where
silent skip is genuinely fine. This mission's entire premise is different: the motivating failure
(`244665ee`, a commit whose message claimed "map/INDEX.md rebuilt" while it was actually stale by a
whole module) is precisely a silent failure of the *human* process this hook replaces. If the hook
itself dies silently for any environment reason — no python on the invoking PATH inside a GUI git
client's stripped environment, the interpreter-resolution class of bug named in finding 7,
permission issues, etc. — nothing in the plan surfaces that to a human. Even a single non-blocking
`stderr` line on the fail-open path (git shows hook stderr during a normal commit without failing
it) is not mentioned anywhere.

**Why it matters.** The plan's own backstop for this — `MapTreeFreshnessTests` — is the same
backstop that existed at the time of the motivating failure and evidently didn't prevent it (or
wasn't run before merge). Leaning on "the pre-existing backstop will eventually catch a dead hook"
is circular: that backstop already failed once to prevent exactly this class of problem, and the
plan proposes no new signal for "the new mechanism itself silently stopped working," only a
regression check that the backstop's *text* is unchanged.

**Severity: should-fix.**

---

## 10. Gate 3's "a real scratch clone/worktree of this actual repo" phrasing conflates two setups that are not equivalent for the one risk that matters most here

**Defect.** Gate 3 says "end-to-end red/green proof against a real scratch clone/worktree of this
actual repo at the shipped SHA." A `git clone` produces an independent `.git` with its own,
unshared `hooks/` directory — it cannot reproduce finding 1's shared-hooks-directory hazard at all.
Only a `git worktree add` against a shared common `.git` reproduces it. The "clone/worktree"
phrasing treats these as interchangeable options for satisfying the same evidence bullet, which
means a crew executing Gate 3 could legitimately pick "clone" (simpler to set up, no shared-state
cleanup) and satisfy every named evidence bullet in the letter — including "a second-worktree-also-
fires-correctly case," which could itself be built as two worktrees of one scratch clone rather than
two worktrees of the *same shared* `.git` this repo actually has — while never once exercising the
actual cross-lane blast-radius shape this repo lives in today.

**Why it matters.** This is exactly the kind of gate-boundary gap the task asked to hunt for: a
place where the plan's own verification can go green without the real hazard ever being exercised,
because the required-evidence wording doesn't force the one topology that matters.

**Severity: should-fix.**

---

## 11. Two of the mission frame's named "decision pressure" questions are never explicitly, traceably answered

**Defect.** `MISSION_FRAME.md`'s "Decision Anchors & Decision Pressure" section names two specific
questions this run "forces... decided without floating, recorded here rather than silently": (1)
full-rebuild vs. incremental hash-compare for staleness detection, and (2) whether the hook script
is a standalone file invoked via a thin shim or is itself the installed `.git/hooks/pre-commit`
file. `PLAN_ALTERNATIVES.md` never states either answer as an explicit decision — the shape of the
chosen mechanism *implies* answers (full-rebuild-then-compare, per finding 6; a shim in
`scripts/hooks/` invoked by something installed at the resolved hooks path, per the convergence
paragraph) but the mission frame's own instruction was to record these on the record, not leave them
inferable from mechanism description.

**Why it matters.** Minor as a standalone item, but it compounds findings 4 and 6: the plan glosses
exactly the two implementation-shape questions the mission frame flagged as consequential enough to
require an explicit, on-the-record answer, and both turn out to be the ones this critique had to
reverse-engineer rather than read.

**Severity: minor.**

---

## 12. Rebase/cherry-pick/`commit --amend` replay multiplies the hook's cost per replayed commit; no named gate pathway covers it

**Defect.** `pre-commit` fires on every commit-creating operation, not just a single interactive
`git commit` — an interactive rebase or cherry-pick sequence replays it once per commit, and
`commit --amend` fires it again on top of whatever already ran. None of the five named pathways in
either document (fresh / stale / pathspec-partial / hunk-partial / unrelated-dirty / forced-failure)
covers "N commits replayed in one rebase," and given finding 6's unmeasured per-commit cost, this is
the scenario where that cost is most likely to become visible and painful (a 20-commit rebase paying
worktree-materialization overhead 20 times).

**Why it matters.** Not a correctness bug, but a real UX/perf gap the plan's gate list doesn't
surface evidence for either way.

**Severity: minor.**

---

## 13. No test for the target paths becoming git-ignored or otherwise refused by `git add`

**Defect.** `git add -- map/INDEX.md map/ids.jsonl` will refuse (with only a warning, not an error,
by default) to add a path that matches a `.gitignore` rule, unless `-f` is passed. Neither document
mentions this case, and combined with the fail-open/silent-on-purpose staging step, a future
accidental `.gitignore` rule matching `map/*.md` or similar would make the "stage silently" step a
permanent, undetected no-op for exactly the two files this whole mission exists to keep fresh.

**Why it matters.** Low-probability, but it's a single-line accidental regression (a `.gitignore`
edit in an unrelated PR) that this plan's design has no defense against and no gate that would catch
it before merge.

**Severity: worth-noting.**

---

## 14. `git commit-tree`'s identity requirement — checked, and found not to be a live risk under normal `git commit`, but still an unexercised assumption for non-standard invocation paths

**Defect (downgraded after empirical check).** `git commit-tree` requires committer/author identity
(confirmed empirically: `git commit-tree <tree> -m msg` fails with "empty ident name" when no
identity is configured). This looked like a candidate for "fail-open silently defeats the mechanism
in any environment lacking git identity" — but a direct empirical check in this environment shows
`git commit` itself refuses to run at all (and never invokes `pre-commit`) when identity is
unconfigured, so by the time the hook's own `commit-tree` call runs, identity is guaranteed to
already be resolvable via the same config/env git already validated for the outer commit. This
specific failure mode is very likely a non-issue for a plain `git commit`. It remains untested for
non-standard invocation shapes (e.g. `-c user.name=... -c user.email=...` passed only to the outer
`git commit` process) that rely on `GIT_CONFIG_PARAMETERS` propagation to a `git commit-tree`
subprocess launched by the hook — plausible that this works via git's own env propagation, but
nothing in either document names it as checked.

**Severity: worth-noting.**

---

## Summary by severity

- **Blocking (5):** shared-hooks-directory blast radius (1); concurrent sibling-worktree race on
  the snapshot machinery (2); no timeout / fail-open doesn't cover hangs (3); unspecified copy-back
  from ephemeral worktree to real index (4); index-snapshot vs. on-disk-read truth-source divergence
  against `MapTreeFreshnessTests` on partial-hunk commits (5).
- **Should-fix (5):** unmeasured full-materialize-per-commit cost (6); run-time worktree-code
  resolution unaddressed despite this repo's own recent interpreter-portability history (7); no
  ephemeral-worktree/dangling-commit cleanup story, especially on the fail-open path (8); zero
  observability on fail-open (9); Gate 3's clone/worktree phrasing lets verification go green
  without exercising the real shared-hooks topology (10).
- **Minor (2):** two mission-frame-named decision-pressure questions not explicitly recorded (11);
  rebase/cherry-pick/amend cost multiplication untested (12).
- **Worth-noting (2):** `.gitignore`-refusal silent no-op risk (13); `commit-tree` identity
  requirement, checked and downgraded (14).

---

## Commander disposition (delegated-mode triage, per design-it-twice-brief.md: critic never
self-triages; the Commander stands in for human triage under `LAUNCH_ORDER-w2-reindex.md`)

Every finding is fixable within the chosen mechanism by pinning down a concrete implementation
detail the plan left open — none forces abandoning the index-snapshot approach for
smallest-diff's skip-on-dirty rule, which would reintroduce the "usually correct, not correct by
construction" gap the convergence already rejected. All five "blocking" findings are re-graded
**fix-now, folded into `execute.json`'s gate imperatives as pinned specifications** (so a crew
implements the resolved design, not an invented one) rather than left as open questions:

1. **Shared-hooks blast radius** — real, but this is inherent to how git hooks work (repo-wide,
   not worktree-scoped) and the human already ruled for a git hook knowing 2.9s/commit is
   repo-wide cost. Re-graded **should-fix / must-test-explicitly, not blocking**: Gate 3 gets an
   explicit required-evidence item proving (not merely asserting) that a commit from a *second*
   worktree sharing this repo's `.git` — on a branch that never ran the installer — is governed by
   the hook too, and RESULT.md's triage-candidates section names worktree-scoped hooks
   (`core.hooksPath` + `extensions.worktreeConfig`) as a real, out-of-mission-scope future option
   for the Admiral, not silently absorbed.
2. **Concurrent sibling-worktree race on `git worktree add`** — real gap, concrete fix: the
   ephemeral worktree path MUST be created via `tempfile.mkdtemp()` (a kernel-guaranteed-unique
   path, hence a unique worktree admin name), never a fixed name. Two concurrent invocations using
   distinct unique paths do not collide at the git level (this is the same pattern CI systems use
   for concurrent `git worktree add` against one shared clone). Pinned into Gate 1's spec; Gate 1
   gets an explicit concurrent-invocation test (two threads/processes calling the mechanism
   against the same repo simultaneously, asserting both succeed and neither's temp worktree
   collides).
3. **No timeout — fail-open doesn't cover hangs** — real, most serious gap, concrete fix: every
   subprocess call in the mechanism (`git write-tree`, `git commit-tree`, `git worktree add`,
   `code_map build`, `git worktree remove`) gets an explicit `timeout=` on its `subprocess.run`
   call; a `TimeoutExpired` is caught by the same fail-open boundary as any other exception. Pinned
   into Gate 1's spec with a concrete timeout value (10s per subprocess call — 3x the measured
   2.9s build cost) and a test that simulates a hanging subprocess (e.g. a fake `runner` that
   sleeps past the timeout) and asserts the shim still exits 0 within a bounded wall-clock window.
4. **Unspecified copy-back mechanism** — real specification gap, concrete fix pinned into Gate 1:
   the build runs inside the ephemeral worktree (because `discovery.py` needs a real `.git`-backed
   directory to run `git ls-files`), but the copy-back is **plain file I/O, not git plumbing** —
   read the bytes of the two built files from the ephemeral worktree, write those same bytes to
   the same two paths in the real working tree (overwrite), then `git add -- map/INDEX.md
   map/ids.jsonl` in the real repo. No `git read-tree`/`checkout-index` needed; this keeps "exactly
   two paths ever touched in the real tree" true by construction, since the mechanism never touches
   any other path in the real tree at any step.
5. **Index-snapshot vs. on-disk truth-source divergence on partial-hunk commits** — confirmed real
   but re-graded: not a design flaw, an inherent, pre-existing property of `MapTreeFreshnessTests`
   itself (it compares disk-including-any-unstaged-diff against committed content, for ANY reason a
   tracked mappable file has an unstaged diff, hook or no hook) — the hook's index-snapshot build is
   the technically correct answer to "what does this commit contain," and the freshness test
   answers a different question ("does disk match HEAD's committed map right now"), which
   legitimately diverge only when a mappable file still carries an unstaged remainder. Disposition:
   **should-fix at the gate-instruction level, not the mechanism level** — Gate 3's required
   evidence is amended so the "full suite green" check runs against a freshly-clean scratch
   checkout (`git status --porcelain` empty) separate from the checkout used to demonstrate the
   partial-hunk-commit case, so the pre-existing, hook-independent freshness-test behavior is never
   mistaken for a hook defect during execution.
6. **Unmeasured per-commit materialize cost** — should-fix, folded into Gate 3's required evidence:
   time the real end-to-end hook invocation (including worktree materialization) and report the
   number alongside the 2.9s build-only figure already on record.
7. **Run-time code resolution across differently-versioned sibling worktrees** — should-fix,
   folded into Gate 1: the shim resolves `repo_root` via `git rev-parse --show-toplevel` from `cwd`
   at hook run time (dynamic per invoking worktree, never a path baked in at install time — this was
   already both candidates' design, now stated explicitly as a pinned requirement) and imports the
   invoking worktree's OWN copy of `scripts.code_map.precommit`. Gate 1 gets an explicit test:
   invoking the hook from a worktree whose checkout predates this feature (no
   `scripts/code_map/precommit.py` at that commit) still exits 0 (fail-open covers the
   `ImportError`/`ModuleNotFoundError`).
8. **No cleanup story, especially on fail-open** — should-fix, folded into Gate 1: worktree removal
   (`git worktree remove --force <path>`) runs in a `finally` block inside the same outer
   `try/except` (a cleanup failure is itself swallowed and logged, never allowed to block the
   commit); the shim also opportunistically runs `git worktree prune` at the start of each
   invocation to self-heal any admin residue left by a prior crashed/killed run. Gate 1 gets an
   explicit test asserting zero `git worktree list` residue after both the success and the
   forced-failure paths.
9. **Zero observability on fail-open** — should-fix, folded into Gate 1: every fail-open exit
   prints one diagnostic line to stderr (git shows hook stderr on a normal commit without failing
   it — no UX cost, no violation of "never block/fail"), naming what was swallowed. Not wired to
   any blocking check (this mission adds no new blocking check beyond the two named), purely a
   printed signal a human glancing at commit output can see instead of silent regression to the
   pre-mission failure mode.
10. **Gate 3's clone/worktree phrasing lets verification go green without the real topology** —
    should-fix, resolved by dropping "clone" from Gate 3's required evidence entirely: every Gate 3
    scratch setup MUST be a `git worktree add` against one shared scratch `.git` (never a `git
    clone`), so the shared-hooks-directory topology this repo actually has is what gets exercised,
    not a topology that cannot reproduce it.
11. **Two decision-pressure questions not explicitly recorded** — accepted, answered explicitly
    right here rather than left inferable: (a) staleness detection is full-rebuild-then-compare, not
    incremental hash-compare — chosen because the mission's own measured baseline (2.9s,
    deterministic) makes the cheaper path unnecessary complexity, and every fresh-vs-stale test
    needs a real build's output to compare against regardless; (b) the hook is a standalone
    `scripts/hooks/code_map_precommit.py` module invoked by a thin installed shim, not the shim
    itself, so the substantive logic is importable and unit-testable without a real installed hook
    (the most-testable constraint's own point).
12. **Rebase/cherry-pick/amend cost multiplication** — accepted as a real, untested UX gap; not
    fixed in this mission (no evidence it is unacceptable, and the mission's file-ownership fence
    does not cover adding rebase-specific short-circuiting). Logged as a triage candidate for
    RESULT.md rather than gated here.
13. **`.gitignore`-refusal silent no-op risk** — accepted, worth-noting severity confirmed. Logged
    as a triage candidate (a `git check-ignore` assertion could be added as a cheap defensive test)
    rather than gated — the current tracked `.gitignore` does not exhibit this today (confirmed:
    `map/INDEX.md` and `map/ids.jsonl` are explicitly negated), so there is no live defect, only a
    future-regression risk.
14. **`commit-tree` identity requirement** — accepted as already downgraded by the critic's own
    empirical check; no further action.

Untaken alternative reconsidered and rejected again: reverting to smallest-diff's skip-on-dirty
rule would sidestep findings 2/3/4/6/8/9/10 for free (no worktree materialization at all), but
reintroduces the exact "silently does nothing whenever anything else is dirty" gap the original
convergence rejected as failing to meet "correct by construction." Every blocking finding above has
a concrete, boundable fix that does not require that retreat, so the index-snapshot mechanism
stands as the recommendation, now with those fixes pinned into `execute.json` rather than left for
an implementing crew to invent.
