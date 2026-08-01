# Fence citation -- 301

This delegated run is fenced off the main checkout's durable `.agent-work/` per its Admiral launch order:

- **Launch order:** `C:/Programs/constellation-skills/.agent-work/epic-298/launch-orders/LAUNCH_ORDER-301.md`
- **Fence (File Ownership):** notes-301.md in this worktree; sole writer of the episode-record/store code and tests
- **Return Shape:** verdict at .agent-work/verdict-301.md; PR #320 MERGED 195e893b8; harvested by admiral-298

Per the delegated-commander "Fenced feedback/archive closeout -- stage, do not waive" doctrine, the durable-root write is impossible from this worktree, so the feedback trio is staged here instead of waived:

- `AGENT_FEEDBACK.md` -- this run's retrospective entry
- `lessons-delta.json` -- tick + lesson ops
- `CONSTELLATION_FEEDBACK.md` -- constellation export (or confirmed-empty)

The Admiral harvests this trio into the shared durable `.agent-work/` root before sweeping this worktree.

## Cap-drop ordering (restored after a re-stage wiped it — see the note at the end)

**HARVESTED AND APPLIED 2026-08-01.** The Admiral followed this ordering exactly as authored;
2 confirms and the top 4 adds landed, leaving the playbook at 20 active against a cap of 20 —
the number the dry-run predicted. Kept for the record, not for action.

Playbook was at **16 active** against a cap of **20**, so **4 of my 10 adds** could land.

**KEEP, in priority order:**

1. **`a-panel-inherits-what-it-was-not-told-to-vary`** — a **dependency, not a preference**.
   #300's `panel-convergence-can-be-inheritance-not-evidence` lands as a *confirm against this
   id*; dropping it orphans another agent's confirm and forks the identity the sibling-fork
   ruling exists to preserve.
2. **`guard-must-be-defined-by-the-consumer-not-a-character-list`** — the only add arriving with a
   counter of **2 from independent instances in one run** (the newline guard at g2, the classifier
   at g4), both of which shipped real silent-wrong-answer defects.
3. **`a-check-that-cannot-fail-is-indistinguishable-from-one-that-passed`** — constellation-scoped,
   **three instances across three agents**; its bank-reason names the graduation path
   (mutation-verification in the crew handoff templates).
4. **`stale-description-has-two-shapes-and-only-one-yields-to-verification`** — constellation-scoped
   and novel; shape 2 is a property of the worktree/harvest topology and it produced a protocol.

**DROP in this order:** 5 `cold-critic-catches-manufactured-consensus-in-design-it-twice` ·
6 `inherited-lesson-text-does-not-transfer-without-a-cold-reader` ·
7 `local-green-is-not-ci-green-when-the-interpreter-differs` (constellation debt already filed at
**#313** — banking it risks confirming a shared-machinery defect into a permanent workaround) ·
8 `a-traceback-under-reports-the-blast-radius` · 9 `fixing-a-defect-relocates-its-class-rather-than-removing-it`
(five instances but all one subsystem, one commander — #305/#308 are the test) ·
10 `seam-per-held-decision-keeps-a-human-choice-genuinely-deferrable` — **last to drop and the
closest call**; it has a measured payoff and the epic has more surfaced-always convergences
coming. **If a slot frees, restore this one first.**

---

**Tool note, found by causing it.** `stage_feedback.py --force` **regenerates `FENCE.md` from its
arguments and silently discards anything hand-appended to it.** I re-staged to correct a
`task-class` → `task_class` key form in the delta, and that correct fix destroyed this ordering —
a real fix breaking a real artifact, with no warning and no diff to notice it by. Anyone appending
judgment to `FENCE.md` (which is exactly what the cap-ordering convention asks for) must re-append
after any later `--force`, or keep that content somewhere the tool does not own.
