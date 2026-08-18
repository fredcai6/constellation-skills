# Fleet Doctrine — surviving long, detached compute on this harness

Platform/harness-scoped doctrine for running a fleet: how Admiral and Commander
sessions die, how to make every death cheap, and how to recover. This is **not**
project doctrine — it is true for every project running Constellation on an
agent harness, which is why it lives in the skill (shipped to every install)
rather than in any one project's run records. A project's episode store records
what happened on that project; it is never the home for a fleet rule, and it is
never read back as one. A fleet rule lives here.

Distilled from field fleets (f1brainz epics #372/#378/#453); the incident count
there was dominated by *tracking* long detached jobs, not by the work itself.

## Contents
- [The three kill vectors](#the-three-kill-vectors)
- [State-note-before-detach (makes every recovery trivial)](#state-note-before-detach-makes-every-recovery-trivial)
- [Watcher-sleep is the dominant Commander kill](#watcher-sleep-is-the-dominant-commander-kill)
- [The sleeper hazard ("completed" is ambiguous)](#the-sleeper-hazard-completed-is-ambiguous)
- [Recovery drill](#recovery-drill)
- [Worktree isolation is a harness no-op on Windows — provision it yourself](#worktree-isolation-is-a-harness-no-op-on-windows--provision-it-yourself)
- [Windows shell hazards (command-checks)](#windows-shell-hazards-command-checks)
- [Adjudication invariants (Admiral errors that bit)](#adjudication-invariants-admiral-errors-that-bit)
- [Engine/platform quirks](#engineplatform-quirks)

## The three kill vectors

A multi-hour ship dies to all three; budget for them:

1. **Plan session limits** kill whole waves mid-run — a Commander "completes"
   with the limit message as its only result; Sonnet crews are separate sessions
   drawing on the same budget, so a wave of ships + crews hits the wall together.
2. **Host-process exit** (the harness restarts, the box reboots) kills every
   in-process agent; the notification arrives as `status=failed`/"previous
   process exited".
3. **Background-task termination** — harness-tracked background shells and
   Agent-tool background subagents are killed by both of the above.

**Only an OS-detached process survives all three.** On Windows, launch long
compute with PowerShell `Start-Process -WindowStyle Hidden` (detached); a
harness-tracked background shell does **not** survive. This is the single
highest-leverage habit for multi-hour gold/training runs.

## State-note-before-detach (makes every recovery trivial)

Before launching any detached multi-hour process, write the crash-resume state
note FIRST: **step · slug · next command · process PID · expected output
artifact**. When honored, every recovery was a clean resume from the note; the
one time it was skipped, ~3h vanished to forensics.

This is **mechanical, not advisory**: the spine `execute` step carries a
`command` precondition (`scripts/verify_state_note.py <work-id>`) that refuses to
enter the detach-heavy phase until `.agent-work/<work-id>/STATE_NOTE.md` is filled
(step, slug, next command, pid, expected artifact — `pid: none — foreground` is a
valid value). The engine guarantees the *first* note exists; re-writing it before
each subsequent detach (the PID changes) stays your discipline. Seed the note from
`.agent-work/templates/STATE_NOTE.template.md`.

## Watcher-sleep is the dominant Commander kill

The most common way a Commander dies is *arming a watcher and ending its turn
waiting on it*. Two failure shapes:

- A per-progress-line monitor resurrects the session on every event — dozens of
  near-empty cold wakes, heavy token burn (users notice).
- The session simply dies asleep on the watcher and never resurrects.

**The watcher itself is the failure mode, not the underlying job.** Safe pattern:
detach the job (above), write the state note, then either **one**
completion-notification (fires on output-exists OR process-death) or **bounded
foreground polls** (≤10 min each) — never a per-progress-line monitor. Short
steps run foreground; never background-and-wait a >10-min step.

**Idle sessions do not receive notifications.** Field-measured (four incidents,
2026-07-11): a correctly-armed completion notification can fire on time and be
DELIVERED hours late, because the platform suspends an idle session and holds
its notifications until something external wakes it. A watcher that "worked"
still stalls the fleet. Two proven counters, use at least one on every dispatch:
(1) **stay active** — bounded in-turn poll loops instead of idling on the
signal; (2) **self-scheduled wake-up** keyed to the work's own deadline (an
external wake by construction) — on firing, adjudicate from artifacts, never
from the missing signal. The deadline, not the notification, is the backstop.

## The sleeper hazard ("completed" is ambiguous)

An agent that ended its turn waiting on a watched event reports
`status=completed` but **may resurrect when the event fires**. You cannot tell
done / sleeping / dead apart from the status alone — inspect the worktree + PID.
Hard rule: **never launch a continuation into a "completed" Commander's worktree
without first confirming the original is dead** (TaskStop it, or verify no live
PID). Two agents in one worktree corrupts engine state and duplicates compute.

## Recovery drill

For a stalled-but-**alive** agent, resume it directly: `SendMessage` to the
agent's id/name continues it with full context (see `windows.md` hazard #2 —
there is no `--resume` CLI flag, but the `SendMessage` resume primitive does
exist). Use worktree recovery only for a **confirmed-dead** Commander (host-
process exit, box reboot, no live PID) — there is no id left to message: a
**fresh agent pointed into the dead Commander's worktree**, which survives the
process (worktrees + workbench artifacts are on disk). Resume from the
engine's on-disk spine/execute state — do **not** restart from zero. On
session resume, sweep task notifications, inspect each affected worktree
(commits, workbench state, orphan processes), and relaunch continuations with
verified inheritance.

**Symmetric with intentional refresh (#179/#183).** A live agent's `current` already carries the run's
`DIGEST:` (running understanding) and, when applicable, `REFRESH REQUESTED:` (`global-everyone.md`
§reach-up). Resuming a confirmed-dead Commander from its on-disk spine above, and relaunching a live one
that filed a refresh-request, read the **identical** `current` — a crash is just a refresh-request that
never got filed. This does not replace the state note below: its PID and expected-artifact fields track
OS-process survival that the engine JSON knows nothing about, and it remains mandatory before any detach.
But for "what step was I on and what do I already understand," `current`'s `DIGEST:` is now the canonical
answer at every tier including this one — read it before reasoning from the state note's `step`/`slug`
fields alone.

## Worktree isolation is a harness no-op on Windows — provision it yourself

See `windows.md` (hazard #3) for the base fact, its grounding, and why a
git-level probe alone returns a false green. **Admiral-specific process** —
do not trust the flag; provision the worktree yourself before a parallel wave:

1. Stand up each Commander's worktree and work area — provision the worktree,
   scaffold `.agent-work`, instantiate its `spine.json`, and hand it the spine path
   in the LAUNCH_ORDER `## Workspace` field — per the shared recipe in
   `stand-up-work-area.md`. That doc is the single source for this step; do not
   restate it here.
2. Gate the wave: `python <admiral-skill-dir>/scripts/verify_worktree_isolation.py <path1> <path2> ...`
   must exit 0 (every path a real, registered worktree, distinct from each other
   and from the main checkout) before you launch. A non-zero exit means isolation
   is not real — fix it; do not launch.

The gate above is the **mechanical guarantee** for the wave. The Commander no
longer runs an arrival check of its own or reports one back — it never scaffolds
its own worktree, so there is nothing left for a self-check to catch (the
`verify_worktree_isolation.py --here` script itself is untouched and still
available; it is simply no longer part of the Commander's own first step).

**Sweep on the right boundary.** Remove a worktree (`git worktree remove <path>`
then `git worktree prune`) only after its Commander's PR is **merged**, or the
Commander is **confirmed dead with no continuation pending** — never while a live
or recovering Commander still holds it. This is the same "confirm dead before you
touch its worktree" rule the recovery drill already applies.

**This isolation is git-topology only — it does not fence hook code.**
`verify_worktree_isolation.py` proves the worktree is real, registered, and
distinct; it says nothing about which project's *hook scripts* the dispatched
Commander actually runs. `CLAUDE_PROJECT_DIR` is fixed once at session launch and
inherited unchanged by every Agent-tool subagent, so a Commander correctly
isolated at the git level still executes the **main checkout's**
`scripts/hooks/*.py` against the **main checkout's** `.agent-work/` state —
silently: the gate passes, git is fenced, and the code under test is still not
the code running (issue #269). A Commander whose mission touches hook behavior
cannot validate that change from inside the worktree containing it, because doing
so runs the same unchanged main-checkout code the harness would run anyway.
Validate with a **fresh process** whose `CLAUDE_PROJECT_DIR` genuinely resolves to
the worktree — a headless `claude -p` launch pointed at it, or a plain subprocess
with the env var set for the non-agent (pure-function) paths — never a fixture
that hand-injects the value under test.

**Collect before you sweep, where there is anything to collect.** A worktree can
carry durable learning the shared root does not yet hold: a
`CONSTELLATION_FEEDBACK.md` export, the cross-project channel
`scripts/collect_feedback.py` sweeps. No Commander gate writes one — the
`feedback` gate's single postcondition is the episode capture — so most worktrees
carry no export, and an absent one is the ordinary case rather than a lost
record. Where one does exist, collect it into the shared durable `.agent-work/`
at the main checkout **before** `git worktree remove`, and look in both places:
the worktree's own `.agent-work/` root, and
`.agent-work/staged-feedback/<work-id>/`, where a **fenced** Commander stages it
with a `FENCE.md` launch-order citation. Just as you confirm a Commander dead
before touching its worktree, you look before you sweep, because a swept
worktree's learning is unrecoverable. The run's **episodes** are the
exception and need no harvesting: `episodes/` is a tracked repo-root path, so a
committed episode already survives the sweep and lands in a fresh clone.
Git-common-dir resolution points the durable root at one shared root, so the
collection is **mostly automatic**; the manual step above remains the fallback for
consuming projects on older scripts, or any hand reconciliation.

## Windows shell hazards (command-checks)

See `windows.md` (hazard #1) for the canonical `gh ... --body` recipe and its
grounding — do not restate it here.

**Command-checks run under bash.** The checklist engine runs `command`-kind checks
(postconditions/preconditions) under a POSIX shell, so an authored test/verify
command may freely use `grep`, `&&`, and pipes and will behave the same on Windows as
on Mac/Linux. On a box with no bash on `PATH` (git installed without Git for Windows)
the engine falls back to cmd.exe and stamps `shell: cmd-fallback` into the check's
evidence — a check that needs bash then visibly fails rather than silently
false-FAILing, so read a `cmd-fallback` marker as "install Git Bash, then re-run".

## Adjudication invariants (Admiral errors that bit)

- **Issue-close gates on verified MERGED, not on green checks.** Sequence:
  verify checks green → merge → verify main HEAD advanced → close. Never batch
  the close with gate verification or chain it onto an unverified merge.
- **Gate merges on the check exit code; never chain** a merge after a watch
  command (`... --watch; merge` runs the merge even when checks go red).
- **Cross-session findings land on the issue at discovery time.** A defect found
  in one session that lives only in scratch is rediscovered from zero by the next
  fleet. Post it as an issue comment when you find it; archiving a session must
  check for findings that belong on open issues.
- **Re-validate after any promotion.** A change that only breaks a committed
  pointer *after* promotion is invisible to reviewers who validated
  pre-promotion; re-run validation post-promotion before declaring done.
- **Verify an idle commander from artifacts; never block on a dropped verdict.** The general rule — idle
  plus complete artifacts reads as *done*, judged from the artifact set, and still confirm-dead before reuse —
  is shared orchestrator doctrine in `global-orchestrator.md` (§idle-subagent-adjudication). The Admiral bite
  it names: when a dispatched commander returns idle with no verdict, verify from the artifact set (branch /
  commit / PR / changed files) **and a clean-room reviewer subagent** pointed at them, and accept on that
  basis rather than hanging on a message it can silently drop.
- **Advancing local `main` mid-run without a normal checkout leaves the working tree stale.** A bare
  `git update-ref refs/heads/main <sha>` (used to fast-forward local main without disturbing an in-flight
  working tree) moves the ref but NOT the working tree — so a file that changed between old and new HEAD shows
  as a false local modification/**deletion**, risking an accidental revert of merged work at the next
  commit/merge. Sync the working tree too (`git status`, then `git restore`/checkout the affected paths — or
  `git merge --ff-only origin/main` which moves ref and tree together), not just the ref. Tag a genuine
  self-inflicted near-miss as an **`ADMIRAL ERROR`** entry even when caught and fixed inline — the dedicated
  tag is what makes it greppable when closeout writes the run's episodes; folding it into a `MERGE` entry's
  prose hides it.

## Engine/platform quirks

- The Commander spine has no dedicated `compact` step: `/compact` is user-level and
  most harnesses don't expose it to agents, so context headroom and the
  **mandatory** commander skill reload open `execute`'s imperative directly —
  compaction is best-effort (run it if the harness exposes it, else rely on
  auto-compaction), the reload is not. A spine instantiated with its own `compact`
  step still runs it to completion.
- The engine owns utf-8 stdio internally, but still set `PYTHONIOENCODING=utf-8`
  in the child env of any *other* subprocess whose output you capture — cp1252
  pipes corrupt captured output silently.
- The spine lease goes stale after `lease_stale_seconds` (default 1800s) of no
  heartbeat, but staleness gates **non-owners only**: as the lease owner you are
  never refused for your own staleness — every mutating verb refreshes the lease,
  so a long crew/compute step or idle gap self-heals on your next verb. A re-claim
  is only needed to take over a *different* session's lease.
- **Self-hosting an engine edit mid-run** (an epic that rewrites `checklist_engine.py` — the very engine
  driving your own spine): pre-rule the hazard in the latitude contract before wave 1. Implement/review the
  change in an isolated worktree. **Before merging**, verify the new engine still drives your **live** spine:
  a read-only `current` on the live spine (exit 0), and a mutating verb (`advance`) run against a **copy** of
  the spine (never the live file) to confirm it refuses/succeeds sanely rather than crashing. Only then merge,
  sync your local checkout to the new engine, and continue driving remaining advances on it — that is how the
  feature gets proven in production, not just in its own test suite (the governor epic #178 dogfed its own
  `--why` capture onto this Admiral's closing advances this way, zero incident).
