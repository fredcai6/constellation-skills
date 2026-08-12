# Agent Feedback Log (staged copy — fenced closeout)

**Staged, not durable.** This Commander is running under `LAUNCH_ORDER-261` (Admiral epic #267),
fenced off the main checkout's `.agent-work/` per that order's Data Locations section ("Read these;
do not write to any of them. Your writes stay inside your worktree."). This is the worktree-local
staged copy of the entry that belongs in the shared `.agent-work/AGENT_FEEDBACK.md` — the Admiral
harvests it into that durable file at epic closeout. See `FENCE.md` in this same directory.

---

## `2026-07-27` — `governor-261`

**Run shape:** `commander (delegated, under LAUNCH_ORDER-261)` · `10/10 spine steps closed; execute.json 2 gates, g1 reworked twice (3 implementer attempts total)` · `sonnet throughout (implementer/reviewer crews and this Commander)`

**Instruction adherence:** `minor deviations`
- Followed the spine/gate/reopen/attest/attach/advance verb discipline exactly throughout, including two full reopen-and-rework cycles on g1 when new evidence contradicted an already-approved design. Deviated once: my very first `claim` call used a relative `--file` path inside a compound `cd && ...` Bash command, which resolved against the wrong base (session-fixed `cwd`, not my actual shell cwd) and wrote a wrong binding entry plus a stray `gauge.json` into the main checkout — an avoidable self-inflicted error, caught and mostly cleaned up (one stray file could not be removed from outside my worktree; the sandbox correctly refused the `rm -rf`, and that refusal was correct, not a bug).

**Friction / unclear:**
- The launch order's "one concrete constraint" section (`_scan_active_spine` returns a dict, not a path) was accurate, but the launch order's implicit framing of `cwd`/worktree as a reliable per-agent signal was NOT — this is the single biggest finding of the run and cost real time to establish empirically (multiple isolated `claim` calls, direct transcript reads) before I could trust a design built on top of it. A one-line pointer in delegated-mode doctrine — "verify any harness-payload field's *scope* (session-lifetime-fixed vs. per-call-live), not just its presence" — would generalize `lesson:verify-harness-field-and-drive-real-writer` usefully; presence and liveness are different questions and this run needed both answered.
- Crew plan files that happen to live directly in the same directory as the Commander's own `spine.json` (rather than a subdirectory, e.g. `<gate>-review/`) share that directory's `gauge.json` with the Commander's own spine — this caused two consecutive freshly-dispatched implementers to hit an immediate Context Governor HARD trip, from a reading that was never their own (traced to the epic's own Admiral, sharing this Commander's session_id and physical transcript). Worked around by having crew plan files use a subdirectory, mirroring the reviewer role's own already-established convention — worth promoting from an implementer-role convention to a Commander-dispatch default, since the collision is structural (directory-sharing), not implementer-specific.
- `checklist_engine.py`'s `advance` sometimes requires a preceding `attest --cond p1 --which preconditions` even when the imperative text doesn't obviously call it out as a separate step from `start` — I hit this refusal pattern repeatedly (every gate) and it became mechanical, but a first-time reader would likely be surprised by it needing to be explicit every single gate rather than being implied by `start`.

**Crew-reported friction:**
- g1's first implementer: hand-rolled `-k` substring filters for its own plan's postconditions swept in tests belonging to a later gate, forcing that gate's code to land earlier than the vertical-slice ordering intended, and `amend` refused to rescope an already-`in-progress` gate. Recommends authoring `-k` filters as exact test-name unions from the start.
- g1's second-rework reviewer: found the standard "temporarily edit the file under review, run, revert" old-vs-new repro technique blocked by the permission classifier (reviewers editing the file under review, correctly). Improvised a reviewer-side standalone script that loads the real module by path and defines the OLD handler inline instead, without ever mutating the artifact under review — recommends promoting this as the documented default technique.
- g2's reviewer: had to grep a crew's own why-records to find where a decision reconfirmation was actually reasoned through, since the handoff pointed at the decision anchor but not the specific why-record id backing it. Recommends handoffs cite the exact why-record id when a crew's own plan file holds the load-bearing reasoning.
- Several reviewers independently proposed/used a Fowler-pass duplicated-code / shotgun-surgery finding — "no shared accessor for a session's bound entries" — as an explanation for why a consumer got missed during the #202 re-key. Filed as issue #272 rather than fixed in-run (would have widened scope).

**What worked:**
- The cold-critic-then-freeze plan step caught a genuine, source-verified arithmetic bug (a `.parent.parent` off-by-one) in the plan's own headline mechanism before any code was written — exactly the value this gate is supposed to provide, and it also surfaced a same-worktree-different-spine collision the original design had silently assumed away.
- The reopen/cascade mechanism handled two consecutive corrective reworks on an already-"complete" gate cleanly — no hand-editing, full evidence trail preserved (superseded, not deleted), and re-driving the downstream cascade-reset gates was mechanical once the underlying code was right.
- Treating a peer agent's (the Admiral's) live evidence with full skepticism — verifying every claim read-only before acting on it — caught nothing wrong in this case, but the discipline meant the eventual design pivot rested on independently-reproduced facts, not borrowed authority.

**Improvement signals:**
- The `cwd`-is-session-fixed finding generalizes past this one run → disposition: confirmed against the existing lesson `verify-harness-field-and-drive-real-writer` this run (see staged `lessons-delta.json`), not a new lesson — it's the same lesson, new grounding.
- Crew plan files sharing a gauge.json directory with the parent spine, and defaulting to a subdirectory to avoid it → disposition: distilled to a new lesson candidate this run (`crew-plan-file-shares-parent-gauge-directory`); needs a second independent recurrence before promoting to a template default (see staged delta).
- Reviewer-side old-vs-new repro without mutating the file under review → disposition: distilled to a new lesson candidate (`reviewer-old-vs-new-repro-without-mutating-file-under-review`); recommend promoting to documented technique in the reviewer skill after one more confirming instance.

---
