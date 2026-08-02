# Reviewer Handoff — g2-review

## Gate
`g2-review` (issue #305, epic #298 — the **mechanical field composer**, the second gate).

You are reviewing the g2 implementer's work. g1 (the capture seam itself) is **closed and
approved** — do not re-review it except where g2 touched it (see HUNT 3).

## Survey State Location
Create your review survey checklist at `.agent-work/issue-305/g2-review/review.json`.
**Never at the worktree root.**

Drive it with the **worktree's** `scripts/checklist_engine.py`, not the installed copy — this
change modifies the engine, so mixing binaries is the hazard. On a **survey**, `record` is the
re-record verb; `advance`/`reopen` refuse as gated-only. `--session-id` is **required** by
`consolidate` and must follow the verb, not precede it.

## What Was Implemented

`scripts/episode_capture.py` gained `mechanical_fields()` — the composer that assembles the
mechanical half of an episode record (`run`, `project`, `role`, `spine-step`, `refusals`,
`reopens`, `rework-count`, `failed-commands`, `context-manifest-ref`, `artifact-ref`) **from
engine state, with zero agent effort**, plus `emit_mechanical_snapshot()` which writes it beside
the manifest on the same g1 seam.

The engine gained a `refusals` counter in `main()`'s refusal path (`checklist_engine.py:2617-2619`)
— additive, armed-only. Docs: `docs/CHECKLIST_SCHEMA.md` (new) and `docs/EPISODE_STORE.md:781`
(rewritten).

Suite as handed to you: **1470 passed / 2 skipped / 472 subtests.**

## How to Inspect the Diff

Everything is **committed** on branch `epic-298/305` in worktree
`C:/Programs/constellation-skills-wt/e298-305`. Base is `967493c`.

```
cd C:/Programs/constellation-skills-wt/e298-305
git diff baf9f16~1..baf9f16 -- scripts/ tests/ docs/     # the g2 implementer's commit
git diff 967493c..HEAD -- scripts/ tests/ docs/          # everything since base (g1 + g2)
```

Do **not** use `git diff main...HEAD` — it shows unrelated merged-PR divergence. Also run
`git status --porcelain` to confirm nothing is stranded untracked.

Read `.agent-work/issue-305/crew/g2-implement-result.md` for the implementer's own evidence and
its **triage items — item 3 is load-bearing here** (see HUNT 1).

## Gate Anchors (verbatim from the plan — `g2-review` inherits `g2-implement`'s)

```
structural:
  struct:episode_capture.mechanical_fields — the composer
  struct:apply_episode_delta._validate_create — :866, the frozen allowlist this feeds
  struct:query_episodes._FIELD_READERS — :240, the eleven fields, frozen
capability:
  capability:mechanical-capture — the deliverable
constraint:
  constraint:frozen-field-group — the group is not mine to redesign
decision:
  decision:zero-agent-effort-is-literal — a field an agent can omit by forgetting is not
    mechanically captured  @grade: settled/human
  decision:episode-store-is-301s — write into episodes/active/ as shipped; no second store
    @grade: settled/inherited
  decision pressure: whether refusals gets an engine counter — RULED IN SCOPE by the Admiral
    (see Rulings below); the plan-time "NOT decided here" is now settled
evidence:
  claim:refusals-has-no-engine-source — main() persists on the refusal path but records
    nothing that a refusal occurred; the journal is success-only
```

---

# THE HUNTS

## HUNT 1 — the `reopens` over-count. **I HAVE ALREADY PROVEN THIS. Do not spend runway re-proving it.**

This is a **confirmed, reproducible defect**, verified by me at source and in the world:

```
python .agent-work/issue-305/evidence/hunt1_reopens_overcount.py
```

Exits **1** today, printing `reopens: 2` for a run in which **exactly one** reopen happened.
Exits **0** once the defect is fixed. (Exit-code verdict, deliberately — per #315 a command
postcondition's stdout is captured and discarded, so the exit code is the only signal that
reaches a spine.)

**The mechanism, verified at source:**
- `reopen()`'s escalation branch (`checklist_engine.py:1870-1879`) sets `blocked`, appends a
  blocker, and **returns a normal string WITHOUT incrementing `rework_count`**.
- It does **not** raise, so `main()` takes the **success** path (`:2634`), and `reopen` is in
  `MUTATING_VERBS` (`:70-75`) — so `append_journal_entry` writes a `reopen` line **anyway**.
- `journal_reopens()` counts that line; `_rework_total()` does not; `reopen_total()` takes
  `max(...)` — so the **over-counting** witness wins.

This falsifies the invariant the shipped docstring rests on
(`episode_capture.py:365-369`: *"Both can only ever UNDER-count ... Neither can over-count."*).
**The implementer's own triage item 3 states the contradiction it did not notice writing.**

**What I need from you on HUNT 1 — three things, in order:**

1. **Audit my proof, not the claim.** I cannot audit my own falsifiability. Is the repro sound,
   or does it prove something narrower than I think? Specifically: is `skip`-after-escalation
   the *reachable* continuation, or did I pick an unrealistic route to get a second emit?
   `resume` refuses a rework-cap escalation by design (`:1811-1817`) — confirm that, because if
   there is **no** reachable continuation after an escalation, the defect is latent rather than
   live and that materially changes its severity. **Say which it is.**
2. **Hunt the same CLASS elsewhere.** The bug is not "reopens is wrong" — it is *a witness was
   assumed monotone without checking every branch of the verb that writes it.* Apply that to
   **`failed-commands`, `rework-count`, and `refusals`**: for each, enumerate **every** branch
   of the code that writes it and confirm none can move it in the unexpected direction. This is
   the highest-value thing you will do in this gate.
3. **Rule on the fix shape.** Do not implement it — the fix lands at `g2-integrate` or a
   reopened `g2-implement`, my call after your verdict. Candidates I have already scoped:
   - **(A) Subtract observable escalations** from the journal witness. Each escalation appends a
     distinctive entry to `cl["blockers"]` and `resume` **cannot** clear it (it refuses on a
     rework-cap escalation), so escalations *are* countable. Verify that claim — it is mine and
     it is the load-bearing premise of option A.
   - **(B) Drop the journal witness; use `_rework_total()` alone.** It can never over-count and
     is always readable in-memory. Cost: loses the amend-drops-a-gate recovery the `max` existed
     for. **Note the docstring's stated reason for the journal — "at the first mutating verb of
     a run there is no journal file yet" — is an argument against a journal-ONLY source, not an
     argument for `max`. Check whether it survives as a reason to keep the journal at all.**
   - **(C) Refuse the field** when the witnesses disagree. Probably too aggressive: they
     legitimately disagree in the amend case.

   **Constraint on any fix: it must live in `episode_capture.py`.** The engine diff is ruled
   **zero logic** (import shim, two call lines, `base_dir` threading) and changing how
   `reopen()`/`main()` journal would breach that ruling.

## HUNT 2 — the gate's own defect class (the original imperative, unchanged)

**A composer that returns plausible constants and reads no engine state at all would pass a
presence-based check.** Verify each field is **DERIVED** — trace it to the state it came from,
and construct a run where the true value is **non-default** (a real reopen, a real failed
command) and confirm the composer tracks it rather than returning a constant that happened to
match. **Do not accept `validate_delta()` as evidence of anything but shape** — it is
isinstance-and-non-empty only.

Plus, by amendment:

- **(a) The `refusals` counter.** Confirm it is genuinely **additive** — construct a checklist
  saved BEFORE the counter existed and confirm every reader still works. Confirm
  `docs/CHECKLIST_SCHEMA.md` documents the field and **matches the implementation exactly**; a
  stale schema doc is a shipped defect here, not a nit. Confirm the increment is on the refusal
  path and not somewhere a success also reaches — **induce a SUCCESSFUL verb and assert the
  counter did NOT move**, which is the case a one-sided test misses.
- **(b) YOU MUST DEVISE A MUTATION THE IMPLEMENTER DID NOT SHIP.** The implementer cannot audit
  its own falsifiability; your independent mutation is the only thing that establishes it. Break
  the derivation in a way its own red-proof does not cover and confirm the suite catches it.
  **To test whether wiring is real, break the CALL SITE, not the callee** — ceremonial wiring
  stays green otherwise. This has found real holes three times this epic.
- **(c)** Confirm the `docs/EPISODE_STORE.md:781` rewrite is **TRUE as written** against the
  shipped code — specifically that it no longer promises automated episode creation that
  `_validate_create` forbids.
- **(d) MAKE THE PREDICATE THE WHOLE CONDITION.** Any predicate with a boundary needs cases on
  **both sides**; any predicate quantifying over a collection needs a **multi-element** case; and
  a test environment that cannot reach the failing condition is as vacuous as a predicate that
  cannot discriminate. Check the counter's and the tallies' tests against that bar.

Also verify: **`project` REFUSES (does not guess) with no git**, and the **`#344` latency claim**
stated in the implementer result.

## HUNT 3 — the asymmetry the g2 refactor introduced. **I verified this; CONFIRM or OVERTURN me.**

g2 collapsed `emit_step_manifest`'s early return, so `emit_mechanical_snapshot()` now runs on
**both** paths — including when the manifest **already exists**, where the old early return had
returned first (`episode_capture.py:598-612`).

What I checked at source, and want you to confirm independently:
- `context_manifest.write_manifest` returns `Path(path)` (`context_manifest.py:420-431`), so the
  collapsed `return destination` is **value-identical** to the old `return cm.write_manifest(...)`.
- `emit_mechanical_snapshot` **swallows every exception** (`episode_capture.py:563-564`), so a
  broken snapshot cannot be misreported as a failed **manifest** via the stub path.
- The asymmetry — manifest is **write-if-absent**, snapshot **overwrites** — is explicitly
  documented and justified (`episode_capture.py:514-521`): the manifest is a frozen delivery
  record pinned by revision, the snapshot is a live tally.

**The open question I did NOT rule on, and which is now yours:** `snapshot_path` **collides across
a start/reopen pair** — one file per step, overwritten. That is intentional per the docstring, but
it means a `reopen` **destroys the original activation reading**. Confirm nothing depends on the
original, and that this is right by **design** rather than right by **accident**.

---

## Rulings in Force — do NOT reopen these

- **Seam at `start()` + `reopen()`, write-if-absent.** Engine diff is an import shim, two call
  lines, and `base_dir` threading — **zero logic**.
- **`refusals` IS in scope**, with four conditions: additive only · `docs/CHECKLIST_SCHEMA.md` in
  the same PR · **prove the counter can be wrong AND prove that test can fail** · state the #344
  latency.
- **Mechanical snapshot, NOT auto-created episodes.** `_validate_create` requires all five
  agent-supplied assertion kinds; auto-creation would fabricate judgment.
- **Refuse, never fabricate.** A field that cannot be honestly sourced **refuses** rather than
  emitting a silent `0`. This is the doctrine HUNT 1 is a breach of.
- **#327 (`run.dirty` removal) stays in scope** — `@grade: settled/human`.
- **#362 packaging fix is done and verified in the world** — installed skill, fresh process, cwd
  outside the repo, `emit_step_manifest.__module__ == 'episode_capture'`.
- **#359 — surveys bypass the seam** (Reviewer, Cartographer, Scout, Curator all uncovered). Known
  and travelling in the PR body. **Not a finding for you to re-raise**; do flag it if you find the
  scope is *wider* than those four.

## Protocol — read this before you deviate

**If any hunt above proves unimplementable or wrong as written: tell ME (the Commander), and
PROCEED with the rest of the review.** Do not stop the gate on it, and do not silently
re-scope it. Put the deviation and its reasoning in your result under a clearly-marked heading.
The frozen items are frozen against *casual* change, not against evidence — **if the code
contradicts this handoff, the code wins, and say so.**

Two handoffs earlier in this run carried errors that cost a crew a cycle each; both were things
the Commander **asserted rather than measured**. Treat my claims above as claims. HUNT 1 is the
one I *did* measure — the rest of my source-reading in HUNT 3 is exactly the kind of assertion
that has been wrong before.

## Standing Constraints

- **`python -m pytest`, not `py`.** `py` is 3.12.13 (CI's pin) but has **no pytest**; `python` is
  3.14.3 with pytest 9.0.2. **Neither reproduces CI** — a local green is never the gate.
  `Path.read_text(newline=...)` is 3.13+; it passed locally and failed CI on PR #320.
- **Windows:** explicit `encoding='utf-8', newline='\n'` on every write. Compare **normalized
  content or blob OIDs, never raw working-tree bytes** (#319 — `core.autocrlf` differs across
  worktrees).
- **Do not touch `C:/Programs/constellation-skills`** (the main checkout) or any sibling worktree.
- Edit canonical `skills/_shared/global-*.md`, **never** the `skills/<role>/references/` copies
  that `install_constellation.py` regenerates.
- `--finding` text with backticks is shell-mangled and silently drops words.

## Return Shape

Write your result to **`.agent-work/issue-305/crew/g2-review-result.md`**. Verdict must be one of
**APPROVE / APPROVE-WITH-FOLLOWUPS / BLOCK**, and must cover:

1. **HUNT 1**: is my proof sound? Is the defect **live or latent** (the reachable-continuation
   question)? Your ruling on fix shape A/B/C with reasoning.
2. **HUNT 1 class sweep**: for `failed-commands`, `rework-count`, `refusals` — every writing
   branch enumerated, and whether any can move the value unexpectedly.
3. **HUNT 2**: per-field derivation trace; the `refusals` additivity, schema-match, and
   did-NOT-move proofs; **your independent mutation and what it caught**; the EPISODE_STORE.md:781
   check; the both-sides/multi-element audit.
4. **HUNT 3**: confirm or overturn my three source claims, plus your ruling on the start/reopen
   snapshot collision.
5. Anything you had to deviate on, and why.
6. Suite result, run with `python -m pytest`.
