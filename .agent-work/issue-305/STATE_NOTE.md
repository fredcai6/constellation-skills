# Crash-resume state note — issue-305

- **step:** execute · **`g1` CLOSED** · **`g2-review` CLOSED (BLOCK)** · **`g2-implement` REOPENED
  (rework 1/3)** — rework implementer dispatched
- **slug:** issue-305 · branch `epic-298/305` (**PUSHED**) · worktree
  `C:/Programs/constellation-skills-wt/e298-305` · base `967493c`
- **next command:** `cd "C:/Programs/constellation-skills-wt/e298-305" && python scripts/checklist_engine.py --file .agent-work/issue-305/execute.json current`
- **pid:** run_crew.py external/record-only — `constellation/issue-305/g2-implement/implementer/attempt-2`
- **expected artifact:** `.agent-work/issue-305/crew/g2-implement-rework-result.md`

**Everything is committed AND pushed.** Nothing depends on this machine.

## Leases and engine

Lease **`commander-305-e298`** (reused across both resumes — job-file-not-agent-file keeps journal
provenance continuous). Spine `.agent-work/issue-305/spine.json`, gate plan
`.agent-work/issue-305/execute.json`. **Drive the WORKTREE `scripts/checklist_engine.py`.**

**#357: the child `execute.json` carries `engine_session: null`, so the lease does NOT protect the
gates.** You are alone; do not rely on the lease to keep you that way.

## Done

- **g1 COMPLETE** — seam at `start()`/`reopen()`, write-if-absent; transitive closure ships to all
  ten engine-carrying skills; AST detector sees plain sibling imports. **#362 verified in the world.**
- **g2-implement attempt 1 COMPLETE** — composer, refusals counter, `docs/CHECKLIST_SCHEMA.md`,
  `docs/EPISODE_STORE.md:781`. Suite **1470 passed / 2 skipped / 472 subtests**.
- **Return item 4 proven** — #300's AC1 can now fail.
- **HUNT 1 PROVEN IN THE WORLD** (`308e9fe`): `.agent-work/issue-305/evidence/hunt1_reopens_overcount.py`
  — one command, exits **1** on the defect, **0** once fixed. A run with exactly ONE reopen emits
  `"reopens": 2`. Mechanism: `reopen()`'s escalation branch (`checklist_engine.py:1870-1879`)
  returns a normal string **without** incrementing `rework_count`, does not raise, so `main()`
  takes the success path (`:2634`) and `reopen` is in `MUTATING_VERBS` — journalled anyway.
- **g2-review CLOSED, verdict BLOCK, 3 blockers, all accepted in full** (`fa0d8b6`). Result:
  `.agent-work/issue-305/crew/g2-review-result.md` (351 lines).
- **g2-implement REOPENED**; rework handoff at
  `.agent-work/issue-305/crew/g2-implement-rework-handoff.md`.

## The reviewer's two findings I could NOT have made myself

1. **Mutation M5 SURVIVED** — replacing the whole two-witness `max` with `_rework_total` alone
   leaves all 63 episode tests green. **The reconciliation has NO discriminating test.** Whichever
   fix lands, it lands on unconstrained code. This is the epic's fourth vacuous-check entry (#337).
2. **The over-count is `E` at a `start` seam but `E−1` at a `reopen` seam** — the in-flight verb's
   own journal line is not yet written, so a single escalation is exactly cancelled there. **A test
   exercising only the `reopen` seam PASSES on the broken code.** Same shape as the `project`
   defect that shipped because it was only tested in a plain checkout.

## Rulings I made this session — cite these, do not re-litigate

- **Fix shape B**: `reopens` uses `_rework_total()` alone; journal witness + `find_spine_path`
  deleted (~60 lines). Rejected "subtract escalations" — arithmetically sound (premise verified:
  escalation blockers are durable, `resume` refuses before its blockers filter) but it string-matches
  engine-authored human-readable text from `episode_capture.py`, so it regresses silently on a
  reword. **B removes the class.** Honest cost: loses amend-drops-a-gate recovery, so it can now
  *under*-count on a narrow path — the direction doctrine concedes. Rejected "refuse" as too
  aggressive (witnesses legitimately disagree in the amend case).
- **`refusals` scope = DOCUMENTATION fix, not a semantics change.** Filed the attribution question
  as **#367**. Ruled in-latitude because the field is new in this PR and has no production behavior
  yet to change. **Floated to the Admiral as the one ruling I'd most want reversed if wrong.**
- **The gate imperative's "reopens from the journal's reopen entries" is SUPERSEDED** by fix B. The
  engine text will not update; the rework handoff says so explicitly.

## HUNT 3 — CLOSED, all three source claims confirmed by the reviewer

`write_manifest` returns `Path(path)` so the collapsed return is value-identical ·
`emit_mechanical_snapshot` swallows every `Exception` (not `BaseException` — reviewer's precision
correction) so it cannot poison the manifest stub path · the write-if-absent/overwrite asymmetry is
documented and deliberate. **The start/reopen snapshot collision is right by DESIGN** — no reader of
`mechanical/` exists in `scripts/`, and `context-manifest-ref` pins the manifest, not the snapshot.

**Wiring proven NOT ceremonial**: 6 of 7 independent call-site mutations caught, including deletion
of the `emit_mechanical_snapshot` call site.

## Still open

- g2 rework → g2 re-review → g2-integrate, then g3, g4, then reconcile → triage → review → feedback
  → archive.
- **No CI check has ever been run on this branch. Claim nothing about one.** When you do: gate on
  the status text reading `pass`, not a zero exit — `gh pr checks` has exited 0 on a *pending* check.

## Lessons harvested (for the feedback step — do not lose these)

- **A vacuous check plus an honest crew reads exactly like a passing check plus a compliant crew.**
- **A revert-based red proves the assertion matches the tree; only a NOVEL module proves the
  detector parses.** Belongs in the handoff template.
- **`constellation-implementer` has no sanctioned resume or no-plan path** — every rework dispatch
  costs the implementer a judgment call against the skill's opening imperative.
- **Handoffs should carry the gate's `anchors` block verbatim.** Done twice this session.
- **When a handoff freezes an adjudicated table, say who to tell and whether to proceed if a row
  proves unimplementable.** Done twice this session; the reviewer confirmed it worked.
- `--session-id` is **required** by `consolidate`, and must follow the verb, not precede it.
- **An adjudicator's stated invariant deserves the same falsification as a crew's test.** The
  `max()` reconciliation was accepted on a one-sentence invariant nobody tried to break. ~15 minutes
  to break, once someone tried.
- **"No output produced" and "output produced somewhere you did not look" are indistinguishable
  without checking the path derivation.** `manifest_root()` is the checklist dir's PARENT and
  `manifest_path` re-appends the work-id, so my first repro emitted outside the fixture and looked
  like no emit at all. Live face of **#360**.
- **Telling a reviewer which claims you MEASURED versus ASSERTED changes what it does.** The
  reviewer said naming HUNT 1 as already-proven and asking for three specific things instead is what
  made it build a *boundary* repro rather than re-run mine — which is how the seam-masking surfaced.
- **REVIEWER-REPORTED GAP:** a handoff that names hunts should also name the survey **shape**. The
  reviewer had to extend the template with nine hunt-specific items; without that, three hunts would
  have been crammed into two generic slots and the engine would have recorded far less.
- **REVIEWER-REPORTED:** `docs/agents/engine-config.json` does not exist in this worktree, yet the
  survey template and the g1 survey both reference it as `config_ref`. Harmless (engine falls back
  to defaults) but two reviewers have now inherited the dangling reference.

## Issues filed

**#362** packaging — FIXED, close with the PR · **#359** surveys bypass the seam — **must travel in
the PR body**, per the Admiral · **#360** doubled work-id manifest path, confirmed live twice ·
**#361** unguarded `work_id` + duplicated place-and-write · **#367** `refusals` checklist-scoped not
run-scoped (filed this session) · **#368** shotgun surgery on the eleven-field group (filed this
session, against unfreezing).

**Branch: PENDING** — pushed, no PR yet.

_Updated: 2026-08-02T05:40:00Z_
