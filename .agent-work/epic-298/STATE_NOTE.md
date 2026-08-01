# Crash-resume state note — epic-298

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

> **Authoring rule, learned twice in this file (2026-08-01):** this note is rewritten only at
> detach boundaries while the ADMIRAL_LOG is written as rulings happen, so the artifact read in a
> disaster goes stale fastest. **Carry pointers, never copies**, for anything another agent keeps
> writing to.

- **step:** execute · wave 0 · **#303 and #301 both MERGED, closed, harvested, swept.** #300 is the last wave-0 issue in flight. #304 held; #299 baselines not started.
- **slug:** epic-298, main checkout `C:/Programs/constellation-skills`; **one** live worktree `../constellation-skills-wt/298-300` on branch `epic-298/300`
- **next command:** `py scripts/checklist_engine.py --file .agent-work/epic-298/spine.json current`
- **pid:** none — foreground. Live: `commander-300` only (lease `commander-300`, 2 commits, g1 and g3 reviews both APPROVE, no PR yet). All other dispatches shut down or complete.
- **expected artifact:** #300's PR, then merge gated on the CI exit code. **HARVEST BEFORE SWEEP** — read `../constellation-skills-wt/298-300/.agent-work/` directly, do not trust counts from here; its `staged-feedback/300/FENCE.md` carries a cap-drop ordering. Already harvested: `harvest/303/`, `harvest/301/`, `harvest/301-full/` (83 files). Recon: `prep-{299,302}-report.md`.

**HARVEST ORDERING RULE, learned from #301 and non-obvious:** harvest → wait for the commander's lease **release** → **re-read its verdict's status line** → then sweep. A harvested verdict is *guaranteed* stale by the closing sequence, because the last state change happens after the release; the status line is the only field that moves in that window.

**Tommy's rulings, now pre-rulings in the renewed contract:** manifest lives in `.agent-work/`, **no** committed per-role artifact; retirement **moves** the file; corpus is **f1Brainz** with task set **#710, #715, #698 + #704 as a deliberate negative control**; **no third bin** — Assumption 6 stands, B0.3 unchanged.

**OWED, do not let the epic close without it:** un-gitignore `.agent-work/` in this repo (keeping `__pycache__` excluded) — agreed with Tommy, deliberately **deferred until wave-0 PRs land** so a `git add -A` in a live worktree cannot pollute a production PR. #300's PR is the last one.

**Also owed at closeout:** the epic retrospective in `.agent-work/AGENT_FEEDBACK.md` (`verify_agent_feedback.py epic-298 --phase feedback` currently reports the epic-298 entry missing); pay the **2 constellation recurrence debts** upstream; the lessons playbook is at **20/20 cap**, so #300's delta needs graduate-or-retire, not adding.

**Invariants that paid this wave:** gate merges on the CI exit code verified at source, never a reported local green (`python` here is 3.14.3, CI pins 3.12); compare cross-worktree state by **id + count + content hash**; **filesystem mtime, not engine heartbeat, is the liveness test** for a working commander; file cross-issue obligations onto the **issue**.

_Updated: 2026-08-01T16:52:00Z_
