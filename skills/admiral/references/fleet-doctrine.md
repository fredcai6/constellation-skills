# Fleet Doctrine — surviving long, detached compute on this harness

Platform/harness-scoped doctrine for running a fleet: how Admiral and Commander
sessions die, how to make every death cheap, and how to recover. This is **not**
project doctrine — it is true for every project running Constellation on an
agent harness, which is why it lives in the skill (shipped to every install)
rather than in any one project's `.agent-work/LESSONS.md`. A project's own
playbook carries only its genuinely project-specific fleet rules.

Distilled from field fleets (f1brainz epics #372/#378/#453); the incident count
there was dominated by *tracking* long detached jobs, not by the work itself.

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

This is now **mechanical, not advisory**: the spine `execute` step carries a
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

## Worktree isolation is a harness no-op on Windows — provision it yourself

See `windows.md` (hazard #3) for the base fact, its grounding, and why a
git-level probe alone returns a false green. **Admiral-specific process** —
do not trust the flag; provision the worktree yourself before a parallel wave:

1. For each Commander, run `git worktree add <path> -b <branch> <base>` from the
   main checkout, and **log that command and its outcome in the ADMIRAL_LOG** — a
   provisioned worktree is a material fleet action.
2. Hand each Commander its **absolute** worktree path in the LAUNCH_ORDER
   `## Workspace` field, with the instruction to run
   `py scripts/verify_worktree_isolation.py --here <path>` as its first step and
   paste the result into its return report.
3. Gate the wave: `py scripts/verify_worktree_isolation.py <path1> <path2> ...`
   must exit 0 (every path a real, registered worktree, distinct from each other
   and from the main checkout) before you launch. A non-zero exit means isolation
   is not real — fix it; do not launch.

The gate is the **mechanical guarantee**; `--here` is the Commander's own
risk-reduction, surfaced as evidence in its report rather than a hard refusal
(Agent-tool dispatch has no engine chokepoint to refuse at).

**Sweep on the right boundary.** Remove a worktree (`git worktree remove <path>`
then `git worktree prune`) only after its Commander's PR is **merged**, or the
Commander is **confirmed dead with no continuation pending** — never while a live
or recovering Commander still holds it. This is the same "confirm dead before you
touch its worktree" rule the recovery drill already applies.

**Harvest before you sweep — a required precondition of removal.** A worktree
carries durable learning the shared root does not yet hold: its lessons-delta,
its `AGENT_FEEDBACK.md` entry, and its `CONSTELLATION_FEEDBACK.md` exports. Just
as you confirm a Commander dead before touching its worktree, you harvest that
trio into the shared durable `.agent-work/` at the main checkout **before**
`git worktree remove` — removal is not permitted until it is collected, because a
swept worktree's learning is unrecoverable. Live grounding: this epic
(`20260706-dogfood-audit`) kept its learning only because the Admiral
hand-harvested every worktree — 12+ manual reconciliations across the run — and
issue-54 had to improvise a snapshot-then-delta dance (copy the canonical
`LESSONS.md` into its worktree before applying a delta, so the apply would not run
against a vacuous empty playbook) for exactly the reason g1's git-common-dir
resolution now removes: it points the durable trio at one shared root, so the
harvest is **mostly automatic** and the improvisation is unnecessary. The manual
harvest above remains the fallback for consuming projects on older scripts, or any
hand reconciliation.

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
- **Verify an idle commander from artifacts; never block on a dropped verdict.** An Agent-tool commander sometimes ends with only an `idle_notification` (`idleReason: available`) and never emits its verdict text, even with the work complete. Artifacts are ground truth; the verdict message is a convenience it can silently drop. When a dispatched commander returns idle with no verdict, **verify from the artifact set** (branch / commit / PR / changed files) and a **clean-room reviewer subagent** pointed at them, and accept the work on that basis — do not hang waiting for a message. This judges the **verdict**, not liveness: it does **not** weaken the sleeper-hazard rule — an idle/"completed" commander may still resurrect, so **confirm it dead before you reuse, sweep, or launch a continuation into its worktree**. "The verdict is in the artifacts" is not "the process is gone."

## Engine/platform quirks

- The Commander spine has no dedicated `compact` step (removed — it was permanent
  skip-with-reason ceremony, since `/compact` is user-level and most harnesses
  don't expose it to agents). Context headroom and the **mandatory** commander
  skill reload now open `execute`'s imperative directly: compaction is best-effort
  (run it if the harness exposes it, else rely on auto-compaction), the reload is
  not. Spines instantiated before this change keep their own `compact` step in
  their instantiated JSON and still run it to completion; only new instantiations
  from the template drop it.
- The engine owns utf-8 stdio internally, but still set `PYTHONIOENCODING=utf-8`
  in the child env of any *other* subprocess whose output you capture — cp1252
  pipes corrupt captured output silently.
- The spine lease goes stale after `lease_stale_seconds` (default 1800s) of no
  heartbeat, but staleness gates **non-owners only**: as the lease owner you are
  never refused for your own staleness — every mutating verb refreshes the lease,
  so a long crew/compute step or idle gap self-heals on your next verb. A re-claim
  is only needed to take over a *different* session's lease.
