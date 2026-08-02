# Crash-resume state note — issue-305

- **step:** execute · **`g1` CLOSED · `g2-implement` CLOSED** · gate **`g2-review`** is next
- **slug:** issue-305 · branch `epic-298/305` (**PUSHED**) · worktree `C:/Programs/constellation-skills-wt/e298-305` · base `967493c`
- **next command:** `cd "C:/Programs/constellation-skills-wt/e298-305" && python scripts/checklist_engine.py --file .agent-work/issue-305/execute.json current`
- **pid:** none — foreground
- **expected artifact:** `.agent-work/issue-305/crew/g2-review-result.md`

**Everything is committed AND pushed.** Nothing depends on this machine.

## Leases and engine

Lease **`commander-305-e298`**. Spine `.agent-work/issue-305/spine.json`, gate plan
`.agent-work/issue-305/execute.json`. **Drive the WORKTREE `scripts/checklist_engine.py`** — the
Admiral approved this explicitly over the installed copy. If the emit path ever wedges a verb, that
is a **finding to report**, not a reason to switch engines and hide it.

## Done

- **g1 COMPLETE** — seam emits at `start()`/`reopen()`, write-if-absent; the transitive closure
  (`episode_capture.py`, `agent_work_root.py`, `context_manifest.py`) ships to all ten
  engine-carrying skills; a new AST-based detector sees plain `sys.path` + sibling imports.
  **#362 verified fixed in the world** — a real install of `implementer` (bundle = engine alone) run
  in a fresh process **outside the repo** bound `emit_step_manifest.__module__ == 'episode_capture'`.
- **g2-implement COMPLETE** — mechanical composer, refusals counter, `docs/CHECKLIST_SCHEMA.md`,
  `docs/EPISODE_STORE.md:781`. Suite **1470 passed / 2 skipped / 472 subtests**.
- **Return item 4 proven** — #300's AC1 can now fail (pre-seam `manifests=[]`, post-seam `['g1.json']`).

## g2-review is next — TWO NAMED HUNTS, do not let a reviewer improvise past them

**HUNT 1 — the `reopens` over-count. I verified this at source; it is not speculative.**
The crew deviated from the adjudicated table with good reason: the literal "journal sidecar" row is
**unimplementable at the seam**, because `append_journal_entry` runs *after* the verb returns (so the
in-flight verb has no journal line) and a run's first mutating verb has no journal file at all.
`claim` is not in `MUTATING_VERBS`. **I accepted the deviation** — and the handoff's justification for
that row was mine and was wrong, describing `failed-commands` rather than `reopens`.

As shipped, `reopens` = **max(journal reopen lines, total `rework_count`)**, justified by "both
witnesses can only under-count; neither can over-count."

**That invariant is FALSE, and the crew's own triage item 3 says so.** The escalation path in
`reopen()` (`rework_count + 1 > cap`) returns `ESCALATED` **without incrementing `rework_count`**, yet
it is a successful verb and still gets a journal `reopen` line. So on any run where a reopen escalated,
the journal over-counts and the `max` takes the **wrong, higher** reading — fabricating a mechanical
fact in exactly the case `refuse-never-fabricate` forbids. Narrow, but real. **The reviewer must
construct an escalated reopen and check what `reopens` reports.**

**HUNT 2 — the constant-composer class**, plus the case a one-sided test misses: **induce a
SUCCESSFUL verb and assert the refusals counter did NOT move.** And the reviewer **must devise a
mutation outside the implementer's shipped set** — the implementer cannot audit its own falsifiability.

Also verify: `project` refuses (not guesses) with no git; the `#344` latency claim; that
`docs/CHECKLIST_SCHEMA.md` matches the implementation exactly.

## Open item the crew raised and I did NOT rule on

It added one call inside `emit_step_manifest`'s `try` (semantics identical — `cm.write_manifest`
returns the same `destination` the early branch returned). It asked whether "do not touch the seam
logic" forbade that and proceeded when no answer came. **Confirm the semantics really are unchanged**;
it is trivially movable to the two engine call sites if the stricter reading is wanted.

## Lessons harvested (for the feedback step — do not lose these)

- **A vacuous check plus an honest crew reads exactly like a passing check plus a compliant crew.**
  m3's "import plus two call sites and nothing else" was checked by `git diff --stat`, which exits 0
  regardless. Authored **by a Commander into a crew's job file** — the grader, not the graded.
- **A revert-based red proves the assertion matches the tree; only a NOVEL module proves the detector
  parses.** Belongs in the handoff template.
- **`constellation-implementer` has no sanctioned resume or no-plan path** — every rework dispatch
  costs the implementer a judgment call against the skill's opening imperative.
- **Handoffs should carry the gate's `anchors` block verbatim.** The g2 crew had to open the
  Commander's `execute.json` to find where the composer belonged, which doctrine calls a violation.
- **When a handoff freezes an adjudicated table, say who to tell and whether to proceed if a row
  proves unimplementable.** The g2 crew had to invent that protocol mid-run.
- Fix in my own handoffs: `--session-id` is **required** by `consolidate`, not rejected; and it must
  follow the verb, not precede it.

## Issues filed

**#362** packaging — FIXED this run, close with the PR · **#359** surveys bypass the seam — **must
travel in the PR body alongside the capability**, per the Admiral · **#360** doubled work-id manifest
path, confirmed live · **#361** unguarded `work_id` + duplicated place-and-write.

**Branch: PENDING** — pushed, no PR yet. Remaining: g2-review, g2-integrate, g3, g4, then
reconcile → triage → review → feedback → archive.

_Updated: 2026-08-02T04:40:00Z_
