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

## Recovery drill (no agent-resume on this harness)

There is no SendMessage/agent-resume primitive: recovery for a stalled or dead
Commander is a **fresh agent pointed into the dead Commander's worktree**, which
survives the process (worktrees + workbench artifacts are on disk). Resume from
the engine's on-disk spine/execute state — do **not** restart from zero. On
session resume, sweep task notifications, inspect each affected worktree
(commits, workbench state, orphan processes), and relaunch continuations with
verified inheritance.

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

## Engine/platform quirks

- The spine `compact` step invokes a user-level CLI the agent cannot run — skip
  with reason; harness auto-compaction covers it.
- The engine owns utf-8 stdio internally, but still set `PYTHONIOENCODING=utf-8`
  in the child env of any *other* subprocess whose output you capture — cp1252
  pipes corrupt captured output silently.
- The spine lease goes stale after `lease_stale_seconds` (default 1800s) of no
  heartbeat; a long crew/compute step lapses it and the next mutating verb is
  refused. Re-claim with the same session id (idempotent) on resume — treat it
  as expected, not an error.
