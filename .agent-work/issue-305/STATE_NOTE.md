# Crash-resume state note — issue-305

- **step:** execute · **`g1` CLOSED · `g2-implement` CLOSED** · gate **`g2-review`** — p1 attested,
  reviewer DISPATCHED
- **slug:** issue-305 · branch `epic-298/305` (**PUSHED**) · worktree
  `C:/Programs/constellation-skills-wt/e298-305` · base `967493c`
- **next command:** `cd "C:/Programs/constellation-skills-wt/e298-305" && python scripts/checklist_engine.py --file .agent-work/issue-305/execute.json current`
- **pid:** run_crew.py foreground/blocking — `constellation/issue-305/g2-review/reviewer/attempt-1`
- **expected artifact:** `.agent-work/issue-305/crew/g2-review-result.md`

**Everything is committed AND pushed.** Nothing depends on this machine.

## Leases and engine

Lease **`commander-305-e298`** (reused across the resume — job-file-not-agent-file keeps journal
provenance continuous). Spine `.agent-work/issue-305/spine.json`, gate plan
`.agent-work/issue-305/execute.json`. **Drive the WORKTREE `scripts/checklist_engine.py`** — the
Admiral approved this explicitly over the installed copy.

**#357: the child `execute.json` carries `engine_session: null`, so the lease does NOT protect the
gates.** You are alone; do not rely on the lease to keep you that way.

## Done

- **g1 COMPLETE** — seam emits at `start()`/`reopen()`, write-if-absent; transitive closure ships
  to all ten engine-carrying skills; AST detector sees plain `sys.path` + sibling imports.
  **#362 verified fixed in the world.**
- **g2-implement COMPLETE** — mechanical composer, refusals counter, `docs/CHECKLIST_SCHEMA.md`,
  `docs/EPISODE_STORE.md:781`. Suite **1470 passed / 2 skipped / 472 subtests**.
- **Return item 4 proven** — #300's AC1 can now fail (pre-seam `manifests=[]`, post-seam `['g1.json']`).
- **HUNT 1 PROVEN IN THE WORLD (this session, commit `308e9fe`).** No longer a suspicion.
  `.agent-work/issue-305/evidence/hunt1_reopens_overcount.py` — one command, exits **1** on the
  defect and **0** once fixed. A run with exactly ONE reopen emits `"reopens": 2` into a real
  `mechanical/b.json`. Mechanism: `reopen()`'s escalation branch (`checklist_engine.py:1870-1879`)
  returns a normal string **without** incrementing `rework_count`, does **not** raise, so `main()`
  takes the success path (`:2634`) and `reopen` is in `MUTATING_VERBS` (`:70-75`) — journalled
  anyway. `max()` then takes the over-counting witness. The shipped docstring's invariant
  (`episode_capture.py:365-369`, *"Neither can over-count"*) is **false**.
- **HUNT 3 verified at source** (confirm-or-overturn handed to the reviewer): `write_manifest`
  returns `Path(path)` so the collapsed return is value-identical; `emit_mechanical_snapshot`
  swallows every exception so it cannot poison the manifest stub path; the
  write-if-absent/overwrite asymmetry IS documented and justified at `episode_capture.py:514-521`.
- **`g2-review` p1 attested**; handoff written at `.agent-work/issue-305/crew/g2-review-handoff.md`
  **carrying the gate `anchors` block verbatim** (the g2 crew's #1 asked-for fix) and an explicit
  unimplementable-row protocol (tell the Commander, proceed with the rest).

## Incidental finding this session — worth a triage line

`manifest_root()` is the checklist directory's **PARENT** and `manifest_path` re-appends the
work-id, so the emit lands in `<parent>/<work-id>/`. My first repro silently emitted **outside**
the fixture directory and looked like "no emit at all". This is the live face of **#360** (doubled
work-id manifest path) — it makes an emit land somewhere a reader would not look. Already filed.

## Still open after g2-review returns

- **Rule the `reopens` fix shape** (A subtract-escalations / B rework_total-only / C refuse), then
  apply it at `g2-integrate` or a reopened `g2-implement`. **The fix must live in
  `episode_capture.py`** — the engine diff is ruled zero-logic.
- Then: g2-integrate, g3, g4, then reconcile → triage → review → feedback → archive.

## Lessons harvested (for the feedback step — do not lose these)

- **A vacuous check plus an honest crew reads exactly like a passing check plus a compliant crew.**
  m3's "import plus two call sites and nothing else" was checked by `git diff --stat`, which exits 0
  regardless. Authored **by a Commander into a crew's job file** — the grader, not the graded.
- **A revert-based red proves the assertion matches the tree; only a NOVEL module proves the detector
  parses.** Belongs in the handoff template.
- **`constellation-implementer` has no sanctioned resume or no-plan path** — every rework dispatch
  costs the implementer a judgment call against the skill's opening imperative.
- **Handoffs should carry the gate's `anchors` block verbatim.** Done this session; make it template.
- **When a handoff freezes an adjudicated table, say who to tell and whether to proceed if a row
  proves unimplementable.** Done this session; make it template.
- Fix in my own handoffs: `--session-id` is **required** by `consolidate`, not rejected; and it must
  follow the verb, not precede it.
- **NEW: an adjudicator's stated invariant deserves the same falsification as a crew's test.** The
  `max()` reconciliation was accepted on a one-sentence invariant nobody tried to break. It took
  ~15 minutes to break once someone tried.
- **NEW: "no output produced" and "output produced somewhere you did not look" are indistinguishable
  without checking the path derivation.** Cost a debug cycle this session.

## Issues filed

**#362** packaging — FIXED this run, close with the PR · **#359** surveys bypass the seam — **must
travel in the PR body alongside the capability**, per the Admiral · **#360** doubled work-id manifest
path, confirmed live again this session · **#361** unguarded `work_id` + duplicated place-and-write.

**Branch: PENDING** — pushed, no PR yet. Remaining: g2-review, g2-integrate, g3, g4, then
reconcile → triage → review → feedback → archive.

_Updated: 2026-08-02T05:05:00Z_
