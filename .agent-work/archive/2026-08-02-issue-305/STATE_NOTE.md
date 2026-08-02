# Crash-resume state note — issue-305

- **step:** execute · **`g1` CLOSED · `g2` CLOSED (implement + review + integrate)** · gate
  **`g3-implement`** is next, `pending`
- **slug:** issue-305 · branch `epic-298/305` (**PUSHED** through `85ce553`) · worktree
  `C:/Programs/constellation-skills-wt/e298-305` · base `967493c`
- **next command:** `cd "C:/Programs/constellation-skills-wt/e298-305" && python scripts/checklist_engine.py --file .agent-work/issue-305/execute.json current`
- **holder:** `commander-305d` — **fourth** holder of lease `commander-305-e298`
- **pid:** none — foreground
- **expected artifact:** `.agent-work/issue-305/crew/g3-implement-result.md`

**Everything is committed AND pushed. Tree clean.** Nothing depends on this machine.

## READ THIS BEFORE RESUMING — confirm-dead is a TWO-READING measurement

A double-dispatch happened at this boundary: the Admiral sent `commander-305c` a new ruling
*after* it had handed off (which re-opened it), then dispatched `commander-305d` against the
same ruling. Both agents were correct; the dispatcher collided with itself.

`305d` caught it and refused to claim. **Every static signal said "dead" and every one was
wrong:** clean tree, crew registry all `completed`, a committed handoff note, a held lease,
last journal write preceding the handoff commit. The occupant was committing and pushing.

**What discriminated — and it is the only thing that did:**

> **Observe twice, separated in time, and require both readings to agree.**
> A single observation of a changing system tells you nothing about whether it is changing.
> **The second reading is the measurement; the first is only a value.**

Snapshot HEAD + SHA-256 of `STATE_NOTE.md`/`execute.json` + journal line count + newest
worktree mtime; wait; take them again. Live looked like: HEAD `3f787a3`→`85ce553` and the note's
hash `420D79B0…`→`5156A7ED…` inside 64s. Dead looked like: three readings over 50s **byte-identical**,
newest write 5.5min stale, plus a stated stand-down. **A first mtime bump alone proves nothing** —
content can be byte-identical to HEAD at that instant and read as a no-op rewrite.

## `py` IS BROKEN UNDER THE POWERSHELL TOOL — a green is indistinguishable from a no-op

`py` is a shim at `C:\Users\fredc\.local\bin\py`. Under the **PowerShell** tool it produces
**no output and no exit code at all** — `$LASTEXITCODE` comes back *empty*, not non-zero.
**Run `py` through the Bash tool.** This matters most for the very first command every launch
order mandates: `py scripts/verify_worktree_isolation.py --here …`. Through PowerShell that
isolation check — the one guarding against cross-worktree data loss — **silently proves nothing**.
Through Bash it correctly returns `worktree OK: in C:/Programs/constellation-skills-wt/e298-305`,
exit 0. Reported to the Admiral, who is filing it. `python` works fine in both.

## Leases and engine

Lease **`commander-305-e298`** — **reuse it, do not mint a new one.** Job-file-not-agent-file
keeps journal provenance continuous across resumes; this is the third holder.
`claim --force --reason "..."` on `.agent-work/issue-305/spine.json`.

Spine `.agent-work/issue-305/spine.json`, gate plan `.agent-work/issue-305/execute.json`.
**Drive the WORKTREE `scripts/checklist_engine.py`**, not the installed copy.

**#357: the child `execute.json` carries `engine_session: null`, so the lease does NOT protect
the gates.** You are alone; do not rely on the lease to keep you that way.

## Gate status

```
e0-context   complete    g2-implement complete    g3-implement PENDING  <- you are here
g1-implement complete    g2-review    complete    g3-review    pending
g1-review    complete    g2-integrate complete    g3-integrate pending
g1-integrate complete                             g4-*         pending
```

After g4: **reconcile → triage → review → feedback → archive** on the parent spine.

## Suite

**1472 passed / 2 skipped / 472 subtests** (`python -m pytest -q`, ~90s). Baseline was 1470/2/472;
**+2 is exactly the two new tests**, nothing else moved.

## What closed this session (g2)

**The named hunt was real and is now fixed.** `reopens` over-counted after an escalated reopen:
`reopen()`'s rework-cap branch (`checklist_engine.py:1870-1879`) returns an ordinary string
**without** incrementing `rework_count` and does **not** raise, so `main()` takes the success path
(`:2634`) and `reopen` is in `MUTATING_VERBS` — journalled as a reopen its own message says did not
happen. `max(journal, rework)` then preferred the inflated reading.

**Proven in the world before acting** — `.agent-work/issue-305/evidence/hunt1_reopens_overcount.py`,
one command, exit **1** on the defect and **0** when fixed. It now exits 0.

**Fix shape B shipped:** `reopen_total()` sums per-task `rework_count` alone; `journal_reopens()`,
`find_spine_path()` and the `spine_path` plumbing are deleted (~84 lines). Entirely in
`episode_capture.py`; the engine is untouched.

**The real deliverable was the test, not the arithmetic.** Reviewer mutation M5 had shown the old
two-witness `max` was pinned by **no test at all**. `EscalatedReopenIsNotAReopenTests` is proven
red on the old expression (`2 != 1` start seam, `4 != 3` reopen seam) and green on the fix, and
covers **both seams** — the inflation is `E` at a `start` seam but `E−1` at a `reopen` seam, so the
reopen-seam case needs **two** escalations or it passes on broken code.

## Three independent mutations, all recorded — do not repeat them

1. **Implementer's:** restored the old `max` expression. RED as predicted.
2. **Commander's (mine):** re-inflated from the `blockers` escalation tally without restoring the
   deleted journal reader. Both new tests RED (`5 != 3`). Restored; blob OID verified against HEAD.
3. **Re-reviewer's M-A:** filtered `skipped` gates out of the checklist handed to `reopen_total`.
   Caught **by the new tests alone** while the pre-existing `ReopensFieldTests` stayed green — the
   proof the new tests add a discriminating axis rather than restating old coverage.
   Its **M-B** (count reworked *tasks*, not reopens) **survives the new tests** and is caught only
   by an older one: new tests pin *which* gates count, old ones pin *how much* each counts.
   Complementary; neither alone suffices.

## Rulings in force from this session — cite, do not re-litigate

- **Fix shape B** over "subtract escalations". A's premise checked out (escalation blockers are
  durable — `resume` refuses before reaching its blockers filter) but it string-matches
  engine-authored human-readable text from `episode_capture.py`, so it regresses silently on a
  reword. **B removes the class.** Accepted cost: can now *under*-count on the amend-drop path.
- **`refusals` scope = DOCUMENTATION fix, not a semantics change.** Filed as **#367**. Ruled
  in-latitude because the field is new in this PR with no production behavior yet to change.
  **Floated to the Admiral as the ruling most worth reversing if wrong** — no answer received.
- **`g2-integrate.c2` waived `--force`.** It required a literal `verdict == "APPROVE"`; the
  reviewer returned the sanctioned **`APPROVE-WITH-FOLLOWUPS`**, no blockers. I refused to attach a
  second evidence item reading `APPROVE` — that fabricates a verdict the reviewer did not give,
  the exact sin the gate spent two rounds hunting. Real verdict is on the record. Filed as **#371**.

## Still open — and the traps waiting in them

- **g3** is the **negative control**: drive a real spine where the agent records nothing, then
  assert the full mechanical group is present **and correct** against an independently-tallied
  ground truth. Per the launch order this is **the** test of the issue's premise, and the Honest-Null
  Clause applies: **if it fails, that is the issue's most valuable output** — report it, do not
  engineer around it. Also **confirm the control can FAIL** before trusting it (run it against a
  deliberately incomplete capture).
- **g4** dogfoods the gates in this repo, full suite.
- **`run.dirty` removal (#327) and the #300 successor line are still UNDONE — BOTH BELONG TO g4.**
  **Ownership ruled by the Admiral** (it wrote the order), after I flagged them as unowned: #327 was
  scoped to g4 by the first commander and never contradicted; the #300 successor line is a one-line
  note on #300's shipped design doc saying the producer had no caller until #305 wired it, and sits
  naturally alongside it. **Do not let g4 close without both** — they are launch-order return items
  5 and the design-doc note, and an unowned return item is the same shape as a design pass that
  exists only as a sentence in a PR body.
- **No CI check has ever run on this branch. Claim nothing about one.** When you open the PR: gate
  on the status text reading **`pass`**, not a zero exit — `gh pr checks` has exited 0 on a *pending*
  check.
- **#359 (surveys bypass the seam — Reviewer, Cartographer, Scout, Curator uncovered) MUST travel in
  the PR body** alongside the capability, per the Admiral. The re-reviewer checked and found no
  evidence the scope is wider than those four.
- **#362 closes with the PR.**

## PR-BODY CONTRACT — Admiral-directed. Do not paraphrase these away.

The PR does not exist yet. When you open it, the body **must** carry all four:

1. **The `reopens` cost, in these words:** *it can now under-count on a narrow path, which is the
   direction doctrine already concedes.* The Admiral's reasoning: **a known-direction inaccuracy
   that is documented is a different object from one that is discovered.**
2. **#359** — surveys bypass the seam (Reviewer, Cartographer, Scout, Curator uncovered). **Must
   travel alongside the capability.** Do not let a reader infer coverage the code does not have.
   (The g2 re-reviewer checked and found no evidence the scope is wider than those four.)
3. **#362** closes with the PR.
4. **The store is complete for engine-driven runs and empty for everything else** — an agent that
   never drives the engine leaves no engine state. Launch order: say so plainly rather than letting
   a reader assume the store sees all work.

## Admiral rulings received AFTER g2 closed — all verified ALREADY satisfied, no rework needed

- **BINDING: the `refusals` doc must say what it IS, not hedge toward what it was meant to be.**
  Verified against what shipped: `docs/CHECKLIST_SCHEMA.md:59` reads *"Scoped to the FILE, not to
  the leaseholder — and say it that way"* and *"the honest reading is 'refusals taken against this
  checklist', not 'refusals this agent took'"*; `scripts/episode_capture.py:391-399` matches. **No
  hedging** — no "approximately run-scoped", no "run-scoped in the common case". Satisfied.
- **File the run-scoped question as its own issue before closing the gate** — done, **#367**, filed
  before `g2-integrate` closed. The reasoning is worth carrying: *a design pass that exists only as
  a sentence in a PR body evaporates; give it a number so the deferral is a decision rather than a
  disappearance.*
- **The discriminating test must be in the SUITE, not in `evidence/`** — satisfied:
  `tests/test_episode_fields.py::EscalatedReopenIsNotAReopenTests`. The `evidence/` script is a
  separate one-command repro, not the test.
- **The discriminating test must hit the `start` seam** — satisfied:
  `test_an_escalation_does_not_inflate_reopens_at_a_start_seam:526`, alongside the reopen-seam case
  at `:545`. The class docstring writes the `E` vs `E−1` trap down so it cannot be lost.

## Lessons harvested (for the feedback step — do not lose these)

- **A vacuous check plus an honest crew reads exactly like a passing check plus a compliant crew.**
- **A revert-based red proves the assertion matches the tree; only a NOVEL module proves the detector
  parses.**
- **`constellation-implementer` has no sanctioned rework/resume path** — it opens by demanding a
  fresh plan, which is exactly wrong for an attempt-2. **Three reworks in this epic have now hit the
  same gap**; each dispatch had to override the skill in prose.
- **Handoffs should carry the gate's `anchors` block verbatim.** Done three times this session.
- **When a handoff freezes an adjudicated table, say who to tell and whether to proceed if a row
  proves unimplementable.** Done; the reviewer confirmed it worked.
- **An adjudicator's stated invariant deserves the same falsification as a crew's test.** The `max()`
  reconciliation was accepted on a one-sentence invariant nobody tried to break. ~15 minutes to
  break, once someone tried.
- **"No output produced" and "output produced somewhere you did not look" are indistinguishable
  without checking the path derivation.** `manifest_root()` is the checklist dir's PARENT and
  `manifest_path` re-appends the work-id; my first repro emitted outside the fixture and read as no
  emit at all. Live face of **#360**.
- **Telling a crew which of your claims you MEASURED versus ASSERTED changes what it does.** The
  reviewer said this is why it built a *boundary* repro instead of re-running mine — which is how the
  reopen-seam cancellation surfaced. **Declaring already-spent mutations** did the same for the
  re-reviewer.
- **A handoff that names hunts should also name the survey SHAPE.** The reviewer had to extend the
  template with nine hunt-specific items; without that, three hunts would have been crammed into two
  generic slots and the engine would have recorded far less.
- **`docs/agents/engine-config.json` does not exist** in this worktree, yet the survey template and
  the g1 survey both reference it as `config_ref`. Harmless (engine falls back to defaults) but three
  reviewers have now inherited the dangling reference.
- **A gate acceptance criterion that cannot accept a sanctioned verdict pushes the agent toward
  fabricating one.** #371. The wedge is not ergonomic, it is doctrinal.

## Issues

**#362** packaging — FIXED, close with the PR · **#359** surveys bypass the seam — **must travel in
the PR body** · **#360** doubled work-id manifest path, confirmed live twice · **#361** unguarded
`work_id` + duplicated place-and-write · **#367** `refusals` checklist-scoped not run-scoped ·
**#368** shotgun surgery on the eleven-field group (against unfreezing) · **#371** integrate gate
wedges on `APPROVE-WITH-FOLLOWUPS` · **#372** the conceded amend-drop under-count is pinned by no test.

(#367, #368, #371, #372 filed this session.)

**Branch: PENDING** — pushed through `c48b48a`, **no PR yet**.

_Updated: 2026-08-02T06:30:00Z_
