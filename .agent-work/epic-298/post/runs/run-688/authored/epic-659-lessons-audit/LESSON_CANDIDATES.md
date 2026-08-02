# Lesson Candidates: `epic-659-lessons-audit`

Nominations only — nothing here is applied until the Admiral (dispatcher) routes it.
Every candidate cites a grounding artifact line; two dangling ops that cited
non-existent lesson ids were caught and re-routed rather than silently applied.

Source artifacts read in full: `.agent-work/epic-659/ADMIRAL_LOG.md` (300 lines,
Waves 0–6, #660–671); all 11 staged `lessons-delta.json` +
`AGENT_FEEDBACK.md`/`CONSTELLATION_FEEDBACK.md` trios
(`epic659-661`, `epic-659/663`, `epic-659/665`, `662-segment-map`,
`664-reference-laps`, `666-driver-fingerprint`, `667-join`,
`668-instrument-panel`, `669-pilot`, `670-season-run`, `671-reconcile`);
`.agent-work/LESSONS.md` Active (364 lines, 18 lessons, tick=33); spot-checked
crew `Workflow Feedback` sections under `.agent-work/archive/2026-07-2{6,7}-{664,666,667,668,669,670}-*/`.

## Dedup groups (task-brief-named patterns resolved)

- **"Windows liveness-detection false positive"** — NOT a new lesson. It is the
  existing `lesson:crew-idle-strands-deliverable` (status: exported), which
  already carries the "verify via PowerShell `Get-Process`, not git-bash `ps`"
  clause from the epic-601 audit. This epic reconfirms it three times: impl-660's
  idle-strand (`ADMIRAL_LOG:36`, explicitly logged as a recurrence), 662's g3
  rework strand-on-result-write (662's own confirm op), and 670's git-bash
  `tasklist` false-negative vs PowerShell `Get-Process` (670's own confirm op,
  textually matches the lesson's existing clause). Routed as 3 confirms of the
  ONE existing id, not a new slug.
- **"harvest-before-sweep + worktree-lease-redirect"** — the harvest ordering
  (`lesson:harvest-collected-not-verified-merged`) held cleanly for all 11 fenced
  trios this epic (every `MERGE` log entry cites the staged-feedback path copied
  to main BEFORE the worktree sweep) — routed as a confirm, not a new add. The
  worktree-lease-redirect sub-mechanism (`durable_root()` resolving to the
  worktree because a concurrent Admiral epic-lease exists in main) recurred
  verbatim in 671's own confirm of `lesson:shared-files-not-on-mission-branch`
  — folded into that lesson's existing history, not a new slug.
- **"verify claims independently, green-check is blind"** — this is a real,
  recurring, epic-dominant theme but it is NOT one existing lesson id; it
  resolves the two DANGLING confirms below (`verify-claimed-side-effects`,
  cited against a lesson id that does not exist) plus two more sightings
  (663's cartographer self-report inaccuracy; 671's cartographer content-verify
  catching two symbol errors past a green `check_arch_map`). Routed as ONE new
  candidate, `verify-subagent-self-report-not-just-green-check` (see below) —
  do not apply the dangling op as originally written.

## Broken ops caught before application (would have raised in `apply_lessons_delta.py`)

- **`668-instrument-panel/lessons-delta.json` op 6**: `{"op":"confirm","id":"verify-claimed-side-effects", ...}`
  — this id exists NOWHERE in `.agent-work/LESSONS.md` (current or historical/retired). `confirm` requires
  an existing lesson (`apply_lessons_delta.py:454-455`, "no such lesson") — this op will raise, not silently
  no-op. **Recommend: strip this op from 668's staged delta before applying it**; its content is folded into
  the new `verify-subagent-self-report-not-just-green-check` add below instead.
- **`669-pilot/lessons-delta.json` op 4**: `{"op":"confirm","id":"worktree-untracked-data", ...}` — same
  defect, this id also does not exist anywhere in the corpus. **Recommend: strip this op from 669's staged
  delta before applying.** Its content (reading gitignored input stores from absolute main-checkout paths;
  scratch-copying a tracked DB) is already covered by the established `#632` own-DB-guard convention cited
  repeatedly elsewhere this epic — not banked as new.

## Candidates

### `commander-dispatch-proof-of-life-gate-near-compaction`
- **Scope:** commander
- **Task-class:** general-workflow
- **Observed:** cmdr-667 was dispatched pre-compaction and produced ZERO activity for 15+ minutes (no spine claim, no notes, no commit) despite a confirmed-correct spawn briefing — a silent non-continuation, not a crash, query, or float.
- **Cost:** 15+ minutes of wall-clock uncertainty, a TaskStop + cold re-dispatch, and (per Fred's own report) matches a cross-session pattern of agents "not continuing today" near compaction boundaries.
- **Proposal:** Make the FIRST action of every delegated Commander dispatch a hard gate: echo `ISOLATION_OK` + `SendMessage` proof-of-life + claim the spine, BEFORE any other work. This is a required template slot (an omitted element), not a reminder — bake it into the dispatch prompt / `COMMANDER_SPINE.template.json` init step.
- **Grounding:** `ADMIRAL_LOG.md` `## INCIDENT + RECOVERY — cmdr-667 non-continuation (2026-07-26)` (lines 162–167), explicit standing-lesson-candidate text already in the log.
- **Corroboration:** VALIDATED IN-EPIC — the re-dispatched cmdr-667, briefed with a hard FIRST-ACTIONS gate, echoed proof-of-life within seconds. Not assertion-only; a same-epic before/after pair.
- **Confidence:** high
- **Routing:** graduate-and-retire → `constellation-commander-delegated` dispatch protocol (SKILL.md or `COMMANDER_SPINE.template.json` init step). Doctrine target → needs `authority=human` + a reproduction drill before apply per skill doctrine; **surfaced for acceptance, not self-applied.**

### `consumed-frozen-module-run-guard-tests`
- **Scope:** commander
- **Task-class:** general-workflow
- **Observed:** cmdr-668's PR broke 2 pre-existing #660 frozen-constant guard tests (`test_exactly_seven_ratified_constants` + the replication-deferred stub) while adding new constants to the SAME module those tests guard. cmdr-668 verified its own new module + its own new tests but never re-ran the CONSUMED module's existing guard-test file.
- **Cost:** A real regression shipped to the PR; the Admiral had to catch it independently at the merge gate and fix it directly (updating the ratified count 7→12, inverting the deferral stub) rather than sending it back — the commander was unresponsive to the fix directive at the time.
- **Proposal:** When a gate's plan ADDS to a previously-ratified/frozen/consumed module, its acceptance criteria MUST explicitly include re-running that module's OWN pre-existing test file(s), not just the newly authored tests — a required checklist item in gate planning (structural, not a reminder).
- **Grounding:** `ADMIRAL_LOG.md` `## MERGE — #668 instrument panel` (lines 220–230), specifically the "REGRESSION CAUGHT + FIXED at the gate" entry and the "NEW LESSON candidate" line the commander itself flagged in prose — **but this was never actually staged as an `add` op in `668-instrument-panel/lessons-delta.json`** (that file only adds `load-bearing-correction-needs-negative-control-falsifier`). This audit drafts it fresh from the log so it isn't lost.
- **Corroboration:** Rework-adjacent (Admiral direct-fix, not a reviewer BLOCK) + task brief named this exact pattern as item (c) — independently expected before this audit started.
- **Confidence:** high
- **Routing:** lesson-inbox add (bank, re-observe once more before graduating to a hard checklist item — n=1 for this exact phrasing, though the underlying "verify the consumed contract wasn't silently broken" theme recurs epic-wide).

### `cartographer-subagent-wrong-checkout-root` (AMEND before applying — do not apply 663's original wording as-is)
- **Scope:** constellation
- **Task-class:** general-workflow
- **Observed:** A dispatched Cartographer subagent, given the worktree's absolute path, wrote all its arch-doc edits to the MAIN checkout instead. Recovery reapplied the content to the worktree filesystem — but that reapplication was itself never COMMITTED, so post-merge the map delta was silently absent (caught only by an unrelated post-merge grep, not by `check_arch_map`, which stays green either way).
- **Cost:** A near-silent loss of the #663 map reconcile (content was preserved off to the side in the main epic work area, so nothing was truly lost — but only by luck of a secondary check, not by design).
- **Proposal:** 663's own staged add already proposes "an independent git-status in both worktree AND main checkout after any cartographer subagent" — **amend its statement to also require confirming the reapplied content is COMMITTED on the branch (not just present on the worktree filesystem)** before trusting the recovery. This closes the SECOND half of the same incident chain, which the original add's wording doesn't quite cover.
- **Grounding:** `ADMIRAL_LOG.md` lines 59, 63, 66 (fence-timing incident → wrong-checkout-root discovery → uncommitted-reapply catch, one continuous incident chain for cmdr-663).
- **Corroboration:** VALIDATED IN-EPIC — 671 (the very next cartographer dispatch) carried the carry-forward mandate and had ZERO recurrence of either half of the chain; independent world-verify at 671's merge confirmed clean `docs/architecture` diff.
- **Confidence:** high
- **Routing:** lesson-inbox add (amended statement below), scope constellation, bank/needs-one-more-reobservation — one clean validating instance (671) is encouraging but not yet proof against a Cartographer dispatched under different conditions.

### `mandatory-full-chain-smoke-before-unattended-run`
- **Scope:** commander
- **Task-class:** general-workflow
- **Observed:** 669's cold-critic-mandated pre-unattended full-chain smoke (not just unit tests) caught a FastF1-fallthrough detector that false-matched a benign string and silently parked a genuinely-fresh E run as fallen-back — all 29 unit tests passed; only the real end-to-end GB smoke exposed it.
- **Cost:** Would have silently corrupted provenance labeling in the unattended #670 season run had it not been caught in the pilot first.
- **Proposal:** For any AFK/unattended multi-stage-pipeline run, gate the build on a mandatory end-to-end smoke against one real data slice BEFORE the unattended run — integration-only silent-correctness bugs pass unit tests and surface only against the whole chain.
- **Grounding:** `.agent-work/staged-feedback/669-pilot/AGENT_FEEDBACK.md` 2026-07-27 (op already staged as an `add` in `669-pilot/lessons-delta.json`).
- **Corroboration:** Assertion-plus-artifact (the false-fallback was a real, demonstrated bug, not a hypothetical).
- **Confidence:** medium
- **Routing:** lesson-inbox add — apply 669's staged op as-is (well-formed, bank_reason already states the re-observe condition).

### `season-batch-runner-per-round-fault-isolation`
- **Scope:** project
- **Task-class:** batch-compute
- **Observed:** #670's first detached season-compute launch died ~2 min in on round 1 (Bahrain) — E's car-ceiling build needs strictly-prior rounds, so round 1 (and often round 2) legitimately has no prior data and crashed the whole batch instead of parking just that item.
- **Cost:** A full batch death requiring a relaunch; caught fast by the auto-park watcher (not silent), but would have been worse undetected.
- **Proposal:** Any real-data multi-round/multi-item batch runner over this pipeline MUST isolate per-item failures (try/except-per-item → PARK with diagnosis + continue); smoke an EARLY/edge item (expected-to-park) before a long detached run, not just a mid-season happy path — synthetic-runner unit tests don't exercise this real-data property.
- **Grounding:** `ADMIRAL_LOG.md` `## INCIDENT (handled in-latitude) — #670 season runner early-round crash + fix` (lines 277–281); staged as an `add` in `670-season-run/lessons-delta.json`.
- **Corroboration:** Direct incident + fix + clean rerun (20/22 covered, 2 honestly parked) — strong within-run proof the fix works.
- **Confidence:** high
- **Routing:** lesson-inbox add, project scope — apply 670's staged op as-is (item (d) from the task brief).

### `verify-subagent-self-report-not-just-green-check`
- **Scope:** constellation
- **Task-class:** general-workflow
- **Observed:** Three independent sightings this epic that a subagent's OWN claim of having done/verified something is not reliable ground truth: (1) cmdr-663's cartographer self-reported "reapplied + verified" after its wrong-checkout recovery, but the reapply was never actually committed — inaccurate self-report, caught only by an unrelated grep; (2) cmdr-668 explicitly logged (confirm op against a since-nonexistent id) that independently re-verifying every crew claim before integrating — re-running `simplification_limits` on the pinned interpreter, byte-checking signed constants, ground-truthing the DB clean — caught a radon/interpreter-env split that would have false-failed a re-check; (3) 671's independent cartographer CONTENT-verify (a reverse-import-scan against real source, not just `check_arch_map`'s exit code) caught two real symbol-attribution errors a green `check_arch_map` could not see.
- **Cost:** (1) was a near-silent loss; (2) and (3) are the Admiral's own standing independent-world-verify discipline paying off — corroborating that a green mechanical check or a subagent's self-report is not sufficient proof.
- **Proposal:** When a subagent (crew, cartographer, or Commander) reports a claim ("done", "reapplied", "verified", "clean"), and a cheap independent re-derivation is available (re-run the check yourself, grep the real content, diff the actual artifact), do it before trusting the claim — especially for architecture-map/content-drift checks, where a green mechanical gate is provably blind to content correctness by construction.
- **Grounding:** `ADMIRAL_LOG.md` lines 63 (cmdr-663 self-report inaccuracy), `668-instrument-panel/lessons-delta.json` op 6 (dangling confirm, redirected here), `671-reconcile/lessons-delta.json` mention op (cartographer content-verify vs green `check_arch_map`).
- **Corroboration:** 3 independent within-epic sightings, one with a concrete catch each time (not assertion-only). Overlaps in spirit with the user's own project memory `cartographer-audit-gaps.md` ("green check_arch_map.py is BLIND to content drift") — this epic reconfirms that principle generalizes beyond cartography to crew claims generally.
- **Confidence:** medium-high — a real, recurring, well-evidenced theme, but genuinely close to 3 EXISTING narrower lessons (`idle-artifact-completeness-distinguisher`, `harvest-collected-not-verified-merged`, `stale-map-reconcile-verify-against-final-commit`). Flagging the overlap transparently rather than forcing a merge judgment call that isn't mine to make.
- **Routing:** lesson-inbox add (constellation scope) — bank_reason: re-observe whether this keeps recurring as ITS OWN pattern or should consolidate with the three narrower siblings above at the next audit.

### `constellation-slash-workid-parsing-gaps`
- **Scope:** constellation
- **Task-class:** general-workflow
- **Observed:** Two constellation-commander scripts assume a `work_id` has no internal `/`, breaking this repo's own nested Commander-under-Admiral convention (`epic-659/665`): `run_crew.py --verify-result`'s `load_registry_for_resume` does `session.split('/')[1]`, dropping everything after the first slash; `verify_agent_feedback.py`'s `_current_run_archive_dirs` string-matches `path.name == work_id`, which is UNSATISFIABLE by construction when `work_id` itself contains `/`.
- **Cost:** cmdr-665 hit BOTH bugs independently within one run — one crew-verification workaround (bypass the CLI parser) + one FORCED self-waive on `archive.c1` (with `--force` + `authority=commander-self`).
- **Proposal:** A single shared work_id-safe parsing/matching helper both scripts import, rather than two independent ad hoc string-splits — mechanical, code-fixable (rung 1 per Form Selection: a script could refuse/handle this instead of a sentence warning about it).
- **Grounding:** `.agent-work/staged-feedback/epic-659/665/AGENT_FEEDBACK.md` 2026-07-25 (originally staged as an `add` in `epic-659/665/lessons-delta.json`).
- **Corroboration:** TELEMETRY-STRENGTHENED by this audit: this is not a one-off — it is the SAME root cause the ADMIRAL_LOG explicitly ties to a SECOND forced-waive event within the run ("2nd instance this run, same root as `run_crew.py --verify-result`"). Two independent forced-waive/workaround events in one run, across two different scripts, sharing one root defect.
- **Confidence:** high
- **Routing:** **add + export** (constellation scope, unshipped shared-machinery bug) so it stays visible to the next upstream constellation sweep — **AND flag as a NEW CODE-FIX ISSUE** the Admiral should file (or route to wherever `constellation-commander`'s scripts are maintained): a `work_id`-safe helper for both `run_crew.py::load_registry_for_resume` and `verify_agent_feedback.py::_current_run_archive_dirs`.

## Existing-Lesson Reconciliation

- `confirm lesson:engine-artifact-attest` — reconfirmed in 10/11 staged deltas this epic (all clean, standing constellation debt, already `status: exported`). Routine tick only — do not re-export; nothing new to add to the upstream queue this cycle.
- `retire lesson:run-crew-cli-launcher-misfit` — reconfirmed clean in 9/11 staged deltas (`--backend external` used with zero dispatch-mechanism friction across all 11 waves). **Note: `apply_lessons_delta.py` already auto-skips `confirm` on a `fixed-upstream` constellation lesson (anti-churn contract) — those 9 confirm ops are silent no-ops as staged.** The lesson has served its purpose; retire explicitly to reclaim the cap slot rather than let it sit inert.
- `confirm lesson:shared-files-not-on-mission-branch` — reconfirmed in 9/11 staged deltas, including the worktree-lease-redirect sub-mechanism recurring verbatim in 671 (`durable_root()` resolving to the worktree under a concurrent Admiral epic-lease) — already folds into this lesson's existing history line from 630-phase6-bt-injection.
- `graduate + retire lesson:from-child-refuses-on-gated-checklist` — reconfirmed CLEAN in 7/7 opportunities this epic (every commander correctly avoided `--from-child` on the gated `execute.json` child and used a plain `attest execute --cond c1` instead). Status was already `exported` targeting `COMMANDER_SPINE.template.json`/engine message; 100% correct navigation across an entire epic is strong evidence the doctrine is understood and ready to graduate into the template as a documented required behavior rather than keep re-confirming a still-unfixed engine surprise that no one is actually surprised by anymore. Surfaced for human acceptance (doctrine target, needs drill).
- `confirm lesson:loo-residual-diagnostic-over-self-weighted-predictor` — 664 confirmed the g4 GATING jackknife is genuinely out-of-sample (delete-d/driver-block), not self-weighted.
- `confirm + amend lesson:admiral-owns-long-batch-compute` — confirmed 3x (664, 667, 669: all correctly declined/scoped multi-hour compute away from the delegated commander); #670 itself is a textbook POSITIVE instance (OS-detached `Start-Process -WindowStyle Hidden`, PID-tracked, durable PowerShell monitor, per-round fault isolation making it resumable). **Amend** to fold in the fixer-667 false-alarm refinement: a stall-watchdog armed against a file's mtime must snapshot that mtime AT ARM TIME, not trust a pre-existing file's already-stale absolute age as the baseline (`ADMIRAL_LOG.md` line 184 — the fixer-667 non-continuation "FALSE ALARM" entry).
- `graduate + retire lesson:self-authored-reasoning-gate-checks-need-review-scrutiny` — reconfirmed 4 MORE times this epic alone (663's `simplification_limits` flag typo, 667's malformed command postcondition caught by its own reviewer, 671's false-green grep-invariant, 668's g1-diagnose self-review) on top of its original 624-phase0 grounding — 5 independent instances across 2 epics is graduation-strength. Surfaced for human acceptance → `constellation-commander` `references/commander-core.md` "Crew gate vs reasoning gate" section (already its recorded target).
- `confirm lesson:scope-self-authored-regression-to-import-graph` — 664's `admiral-owns-long-batch-compute` confirm op explicitly states the regression was "scoped to the import graph rather than the full physics suite" — direct corroboration of this sibling lesson too, not previously cross-cited by 664's own delta.
- `confirm lesson:idle-artifact-completeness-distinguisher` — cmdr-663's ambiguous watchdog INCIDENT (`ADMIRAL_LOG:56-57`: files built, no commit/PR/verdict, no idle signal) was correctly resolved by checking artifact completeness (cartographer reconcile completed + `execute.json` touched = actively finishing), exactly the lesson's prescribed diagnostic.
- `confirm + amend lesson:delegated-commander-foreground-poll-over-watcher-yield` — confirmed 6x (662, 664, 666, 667, 669) at genuine multi-crew scale (up to 12 crew dispatches in one run) with zero Admiral nudges. **Amend** to fold in 668's refinement: distinguish a FINITE compute job (foreground-poll) from a human-gated sign-off (yield-with-an-explicit-message is correct there, not a contradiction) — `668-instrument-panel/lessons-delta.json`'s own confirm op already states this refinement precisely.
- `mention lesson:stale-map-reconcile-verify-against-final-commit` — 671's independent cartographer content-verify catching two real symbol-attribution errors past a green `check_arch_map` reconfirms the underlying "a green mechanical check is blind to content drift" principle this lesson's own reconcile-staleness case exemplifies (already staged as a `mention` op in `671-reconcile/lessons-delta.json`).
- `amend lesson:admiral-message-queue-latency-coordination-hazard` — fold in the Wave-0 near-collision: cmdr-661 and cmdr-663 both nearly/actually edited the shared `docs/architecture/packets/physics.md` in parallel because the Admiral's fence (sent as a follow-up message) queued behind each commander's already-in-flight cartographer step (`ADMIRAL_LOG.md` lines 46, 59 — "the fence should have been in the launch order pre-dispatch, not mid-run — same lesson as the #665-block coordination gap", explicitly self-identified as the same mechanism in the log). Extends the lesson's mitigation list: a fence on a SHARED resource for a PARALLEL wave must be baked into every launch order pre-dispatch, never sent as a mid-flight message.
- `confirm lesson:harvest-collected-not-verified-merged` — the epic-601 gap this lesson describes did NOT recur: all 11 fenced-commander trios this epic were independently verified copied to `.agent-work/staged-feedback/` (or the durable archive) BEFORE their worktree was swept, cited explicitly at every `MERGE` log entry. Confirming the discipline held under a full 12-issue/7-wave epic, though the lesson's own bank_reason (whether the fix needs to be mechanical) isn't yet resolved by one clean epic — keep banked.
- `graduate + retire lesson:admiral-close-after-merge-verified` — the prior audit (epic-601) explicitly flagged this as a "graduation CANDIDATE for the next audit" pending a committed doc home. This epic's 12 merges (#674 through #711) show the SAME verify-checks→merge→verify-HEAD→close sequence held with zero violations, including explicitly reading the pyright check row rather than trusting `gh pr checks --watch`'s exit code (e.g. the #674/#702 entries). Two clean epics in a row + an already-flagged graduation intent = ready now. Surfaced for human acceptance → new home: `constellation-admiral` SKILL.md Merge/Closeout section (no prior committed doc states this sequence verbatim).

## Playbook Delta (ready to apply)

Distinct from — and to be applied ALONGSIDE — the 11 already-staged per-wave deltas
(apply those as-is, EXCEPT strip the two dangling ops named above from 668's and
669's files before applying). This is this audit's own consolidated delta:

```json
{
  "work_id": "epic-659-lessons-audit-closeout",
  "tick": true,
  "ops": [
    {
      "op": "retire",
      "id": "run-crew-cli-launcher-misfit",
      "reason": "Fixed upstream (constellation-commander's first-class --backend external path); reconfirmed clean across all 11 epic-659 waves with zero dispatch-mechanism friction. Confirms against a fixed-upstream constellation lesson are already auto-skipped by apply_lessons_delta.py's anti-churn contract, so the lesson was serving no further purpose sitting in Active. Retiring to reclaim the cap slot."
    },
    {
      "op": "retire",
      "id": "from-child-refuses-on-gated-checklist",
      "reason": "100% correct navigation (7/7) across epic-659 — every commander closed the gated execute.json child with a plain attest, never --from-child. Graduating to COMMANDER_SPINE.template.json's execute-step imperative as a documented required behavior (surfaced for human acceptance + reproduction drill, not self-applied doctrine edit)."
    },
    {
      "op": "retire",
      "id": "self-authored-reasoning-gate-checks-need-review-scrutiny",
      "reason": "5 independent confirmations across 2 epics (624-phase0 original; epic-659's 663/667/671/668) is graduation-strength. Graduating to constellation-commander references/commander-core.md 'Crew gate vs reasoning gate' section (its already-recorded target), surfaced for human acceptance + reproduction drill."
    },
    {
      "op": "retire",
      "id": "admiral-close-after-merge-verified",
      "reason": "The prior audit (epic-601-closeout-audit) explicitly flagged this as a graduation candidate for the next audit. Epic-659's 12 merges reconfirm the verify-checks-then-merge-then-verify-HEAD-then-close sequence with zero violations (2 clean epics in a row). Graduating to constellation-admiral SKILL.md's Merge/Closeout section, surfaced for human acceptance + reproduction drill."
    },
    {
      "op": "add",
      "id": "cartographer-subagent-wrong-checkout-root",
      "scope": "constellation",
      "task_class": "general-workflow",
      "statement": "A Cartographer subagent dispatched at the reconcile step, given the worktree's absolute path in its dispatch prompt, wrote all its architecture-doc edits (docs/architecture/packets/*.md, index.md, overlays/*.yml, a new decisions/*.md file) to the MAIN CHECKOUT instead of the assigned worktree -- a git-invisible failure caught only because the dispatching commander independently ran git status in BOTH locations. Recovery: capture each file's diff/content before touching anything, revert the main checkout to clean, re-apply the identical changes to the worktree, THEN VERIFY THE REAPPLIED CONTENT IS ACTUALLY COMMITTED ON THE BRANCH (not just present on the worktree filesystem) -- a second, distinct failure mode chained onto the same incident: cmdr-663's own 'reapplied + verified' self-report was inaccurate because the reapply was never committed, and check_arch_map stays green with or without the map node so it can't catch the gap. Re-verify both ends plus the worktree's own architecture-map checker AND confirm the branch diff includes the map files before trusting the recovery.",
      "grounding": "ADMIRAL_LOG.md 2026-07-25 lines 59/63/66 (cmdr-663 fence-timing -> wrong-checkout-root discovery -> uncommitted-reapply catch, one continuous incident chain); AGENT_FEEDBACK.md 2026-07-25 663-grip-g INCIDENT+RECOVERY entry (full diff/status evidence both locations).",
      "bank_reason": "One validating same-epic instance (671, the next cartographer dispatch, carried the carry-forward mandate and had zero recurrence of either half of the chain) is encouraging but not yet proof against a Cartographer dispatched under different conditions (different skill version, different worktree layout) -- re-observe on the next epic that dispatches a Cartographer subagent before deciding whether the fix should be a stronger prompt pattern or a self-verify-write-location step built into the Cartographer skill's own doctrine.",
      "target": "constellation-cartographer skill dispatch doctrine + commander cartographer-dispatch carry-forward note"
    },
    {
      "op": "add",
      "id": "consumed-frozen-module-run-guard-tests",
      "scope": "commander",
      "task_class": "general-workflow",
      "statement": "When a gate's plan ADDS to a previously-ratified/frozen/consumed module, its acceptance criteria MUST explicitly include re-running that module's OWN pre-existing test file(s), not just the newly authored tests for the new content. Verifying only your own new tests can pass while silently breaking the guard tests of the module you are extending.",
      "grounding": "ADMIRAL_LOG.md 2026-07-27 'MERGE -- #668 instrument panel' entry, 'REGRESSION CAUGHT + FIXED at the gate (cmdr-668 miss)': the PR broke 2 pre-existing #660 frozen-constant guard tests (test_exactly_seven_ratified_constants + the replication-deferred stub); cmdr-668 verified its own module + its own new tests but not the CONSUMED frozen_constants guard tests; the Admiral caught it and fixed it directly at the merge gate. The commander's own log named this a 'NEW LESSON candidate (for closeout audit)' but it was never actually staged as an add op in 668-instrument-panel/lessons-delta.json -- drafted fresh here so it is not lost.",
      "bank_reason": "First occurrence of this exact phrasing (n=1) though the underlying 'verify the consumed contract wasn't silently broken' theme recurs epic-wide (byte-identical invariants, leakage guards, positive controls) -- re-observe on the next gate that extends a previously-ratified/frozen module before graduating this into a hard checklist item in gate-planning doctrine.",
      "target": "constellation-commander references/commander-core.md gate-planning / acceptance-criteria section"
    },
    {
      "op": "add",
      "id": "mandatory-full-chain-smoke-before-unattended-run",
      "scope": "commander",
      "task_class": "general-workflow",
      "statement": "For an unattended/AFK run that builds a multi-stage pipeline, gate the build on a MANDATORY end-to-end smoke on one real slice BEFORE the unattended run (not just unit tests) -- integration-only silent-correctness bugs (e.g. a provenance/branch inversion) pass every unit test and surface only when the whole chain runs against real data.",
      "grounding": ".agent-work/staged-feedback/669-pilot/AGENT_FEEDBACK.md 2026-07-27 669-pilot: the cold-critic's mandatory 'first full-chain run must NOT be the unattended g3 run' (fix #1) caught a FastF1-fallthrough detector that false-matched a benign 'fastf1' mention and parked a genuinely-fresh E run as fell-back -- every one of the 29 unit tests passed; only the GB full-chain smoke exposed it.",
      "bank_reason": "Re-observe across future pipeline-wiring runs whether a mandatory pre-unattended end-to-end smoke repeatedly catches integration-only silent bugs the unit suite misses -- if it recurs it earns a standing gate; if not, it was one-off.",
      "target": null
    },
    {
      "op": "add",
      "id": "season-batch-runner-per-round-fault-isolation",
      "scope": "project",
      "task_class": "batch-compute",
      "statement": "A real-data multi-round/multi-item batch runner over the epic-659 pipeline MUST isolate per-item failures (try/except-per-item -> PARK with a diagnosis + continue), never let one item's exception kill the whole batch. The pipeline is strictly-pre: E's car ceiling needs sessions with round_idx < R, so early rounds with no strictly-prior data (round 1, sometimes 2) legitimately produce no severity classes and crash inside run_circuit -- expect them to PARK, and smoke an EARLY/edge round (expected to park), not just a mid-season happy path, before launching a long detached batch. Synthetic-runner unit tests do NOT exercise this real-data early-round property.",
      "grounding": ".agent-work/staged-feedback/670-season-run/AGENT_FEEDBACK.md 2026-07-27 670: first detached launch crashed on round 1 (no strictly-prior data); g1 reopened to add per-round fault isolation; rounds 1-2 then parked cleanly and the season completed over 20 covered rounds.",
      "bank_reason": "Re-observe on the next real-data batch runner (backfill, multi-season, other pipelines) to confirm the per-item-isolation + strictly-pre-early-park pattern generalizes beyond the 2023 season run.",
      "target": null
    },
    {
      "op": "add",
      "id": "verify-subagent-self-report-not-just-green-check",
      "scope": "constellation",
      "task_class": "general-workflow",
      "statement": "A subagent's (crew, cartographer, or Commander's) own claim of having done/verified/reapplied something is not reliable ground truth on its own, and a green mechanical check (e.g. check_arch_map) can be structurally blind to content drift by construction. When a cheap independent re-derivation is available -- re-run the check yourself on the pinned interpreter, grep/diff the actual artifact, reverse-scan real source against a claimed map -- do it before trusting the claim, especially for architecture-map/content-correctness claims.",
      "grounding": "ADMIRAL_LOG.md line 63 (cmdr-663's cartographer self-report 'reapplied + verified' was inaccurate -- the reapply was never committed, caught only by an unrelated grep); 668-instrument-panel/lessons-delta.json op 6 (a dangling confirm against a non-existent lesson id, redirected here -- its actual content: every crew claim independently re-verified before integrating, catching a radon/interpreter-env split); 671-reconcile/lessons-delta.json mention op (an independent cartographer content-verify, a reverse-import-scan against real source, caught two real symbol-attribution errors a green check_arch_map could not see).",
      "bank_reason": "3 independent within-epic sightings with a concrete catch each time is real signal, but this sits close to 3 existing narrower lessons (idle-artifact-completeness-distinguisher, harvest-collected-not-verified-merged, stale-map-reconcile-verify-against-final-commit) and to the user's own project memory cartographer-audit-gaps.md. Banking as its own candidate rather than forcing a merge call that belongs to the next audit or the human -- re-observe whether it keeps recurring as ITS OWN pattern (crew-claim verification generally) or should consolidate with the narrower siblings.",
      "target": null
    },
    {
      "op": "add",
      "id": "constellation-slash-workid-parsing-gaps",
      "scope": "constellation",
      "task_class": "general-workflow",
      "statement": "Multiple constellation-commander scripts assume a work_id has no internal '/', breaking under this repo's own nested Commander-under-Admiral convention (epic-<N>/<issue>, e.g. epic-659/665). CONFIRMED TWICE, independently, in the SAME run: (1) run_crew.py --verify-result <session>: load_registry_for_resume parses work_id as session.split('/')[1] (one segment), dropping everything after the first '/'. (2) verify_agent_feedback.py --phase archive: _current_run_archive_dirs string-matches path.name == work_id or path.name.endswith(f'-{work_id}') -- both unsatisfiable when work_id contains '/'. Workarounds used: (1) call run_crew's registry functions directly, bypassing the CLI parser; (2) a FORCED self-waive on archive.c1 with --force + authority=commander-self, citing this exact defect.",
      "grounding": ".agent-work/staged-feedback/epic-659/665/AGENT_FEEDBACK.md 2026-07-25 epic-659/665 entry: reproduced on all 4 crew-verification calls (root cause read directly from run_crew.py's load_registry_for_resume) and once at archive closeout (root cause read directly from verify_agent_feedback.py's _current_run_archive_dirs). ADMIRAL_LOG.md 2026-07-25 line 51 explicitly ties the archive.c1 forced-waive to being the '2nd instance this run, same root as run_crew.py --verify-result'.",
      "bank_reason": "Two independent forced-waive/workaround events in one run, across two different scripts, sharing one root defect -- banked (and exported) so it stays visible to the next upstream constellation sweep rather than getting lost as a per-project one-off.",
      "target": "constellation-commander scripts/run_crew.py load_registry_for_resume + scripts/verify_agent_feedback.py _current_run_archive_dirs"
    },
    {
      "op": "export",
      "id": "constellation-slash-workid-parsing-gaps",
      "grounding": "Two independent forced-waive/workaround events in one epic (epic-659/665) sharing one root cause across run_crew.py and verify_agent_feedback.py -- queuing for the next constellation upstream sweep. RECOMMEND the Admiral additionally file a standalone code-fix issue for a shared work_id-safe parsing/matching helper both scripts import."
    },
    {
      "op": "amend",
      "id": "admiral-owns-long-batch-compute",
      "statement": "Multi-hour batch compute must be Admiral-owned and OS-detached (e.g. PowerShell Start-Process -WindowStyle Hidden, which survives all three fleet-doctrine kill vectors). A commander's harness-tracked background workers die when the subagent idles -- guaranteed strand. Pattern: Admiral launches detached workers, records PIDs + state note, uses a durable watcher (Wait-Process) rather than a harness-tracked background; CLIs must be idempotent/resumable so partial runs continue. A commander may discover or diagnose batch scope, but must not be the one running multi-hour compute. When a Commander's OWN plan (not launch-order-mandated) folds a full-repo/full-suite regression check into a gate's closing postcondition, size it BEFORE freezing: grep the real import graph of changed files and scope to actual importers. Factor any standing thread-cap guard into runtime estimates. When launching a detached process with a multi-word argument, prefer the script's own in-code default/tuple over PowerShell's Start-Process -ArgumentList where possible. WHEN ARMING A STALL-WATCHDOG AGAINST A FILE'S MTIME, SNAPSHOT THAT MTIME AT ARM TIME -- do not key liveness off a pre-existing file's already-stale absolute age, or a healthy in-flight process will read as a false 'SILENT' alarm.",
      "grounding": "ADMIRAL_LOG.md 2026-07-27 '#667 fixer-667 non-continuation FALSE ALARM' entry: a watchdog fired 'SILENT' but was a baseline bug (keyed on join.py's pre-existing 16:50 mtime, already >10min stale before fixer started); pinged for liveness, fixer was actually driving and landed the commit. #670 season compute itself corroborates the rest of the lesson cleanly (OS-detached Start-Process hidden, PID-tracked durable PowerShell monitor, per-round fault isolation making the run resumable).",
      "task_class": "general-workflow"
    },
    {
      "op": "amend",
      "id": "delegated-commander-foreground-poll-over-watcher-yield",
      "statement": "In a headless/delegated run, arming a fire-and-forget BACKGROUND watcher and ending the turn to 'wait' reads to the Admiral as IDLE and stalls the run between steps. For a medium wait (a crew rework, a re-review, a slow-but-finite check) prefer a BOUNDED FOREGROUND in-turn poll (a foreground bash until-loop with a deadline that returns the moment the signal fires) so the turn stays alive; reserve OS-level detach + a single completion-notify only for genuinely-long (>~10min) jobs, and even then verify-alive rather than trusting the notify. REFINEMENT (668): this is a foreground-poll-vs-background-yield distinction for a FINITE compute job, not a rule against ever yielding -- when the wait is on a HUMAN-GATED decision (a sign-off, a routed float) with nothing to poll, making the block visible (SendMessage + a state note) and yielding the turn as a governed reach-up is the correct shape, not a violation; the Admiral resumes with a query round-trip, context intact.",
      "grounding": "668-instrument-panel/lessons-delta.json confirm op: 'All F12-independent work (4 instruments) was completed first... At the HARD GATE, with nothing to poll (the sign-off is a human-routed decision, not a finite compute job), I made the block visible... and yielded the turn as a governed reach-up... So: foreground-poll a finite compute job; yield-with-a-clear-message a human-gated sign-off -- the two are different shapes, not a contradiction.' Confirmed 6x this epic (662, 664, 666, 667, 669) with zero Admiral nudges at up to 12-crew scale.",
      "task_class": "general-workflow"
    },
    {
      "op": "amend",
      "id": "admiral-message-queue-latency-coordination-hazard",
      "statement": "A SendMessage to a delegated commander/implementer queues until that agent's own turn boundary -- it is not delivered instantly. This creates concrete Admiral-side hazards: (a) steering/adjudicating a commander's IMPLEMENTER directly (bypassing the commander layer) leaves the commander itself unaware; (b) a commander that appears to silently diverge from an explicit ruling may simply not have received it yet; (c) A FENCE ON A SHARED RESOURCE FOR A PARALLEL WAVE (e.g. 'only one commander may edit docs/architecture/packets/*.md this wave') sent as a follow-up message after dispatch queues behind each commander's already-in-flight action -- a cartographer step already running when the fence arrives will still touch the shared file before it's ever seen. Shared-resource fences for parallel waves MUST be baked into every launch order BEFORE dispatch, never sent as a mid-flight message.",
      "grounding": "ADMIRAL_LOG.md 2026-07-25 lines 46 and 59 (epic-659 Wave 0): cmdr-665's reconcile edited the shared docs/architecture/packets/physics.md before the Admiral's one-writer fence could reach cmdr-661/cmdr-663 (message-queue latency); cmdr-663's cartographer independently hit the SAME fence-timing gap minutes later ('its cartographer was already running when my fence arrived... the fence should have been in the launch order pre-dispatch, not mid-run -- same lesson as the #665-block coordination gap', explicitly self-identified as the same mechanism in the log).",
      "task_class": "general-workflow"
    },
    {
      "op": "confirm",
      "id": "crew-idle-strands-deliverable",
      "grounding": "epic-659, 3 sightings: impl-660's idle-strand (ADMIRAL_LOG line 36, explicit 'Recurrence of active lesson crew-idle-strands-deliverable'); 662's g3 rework strand-on-result-write (662-segment-map/lessons-delta.json confirm op); 670's git-bash tasklist PID-liveness false-negative vs PowerShell Get-Process confirming a live detached process (670-season-run/lessons-delta.json confirm op) -- the exact 'Windows liveness-detection false positive' pattern the task brief named is this existing lesson's own PowerShell-Get-Process clause, reconfirmed, not a new slug."
    },
    {
      "op": "confirm",
      "id": "shared-files-not-on-mission-branch",
      "grounding": "epic-659: reconfirmed in 9/11 staged deltas (epic659-661, epic-659/663, 662, 664, 666, 667, 668, 671, plus 665's own confirm) -- every mission-branch diff verified code+tests+docs only, zero .agent-work leaks; the worktree-lease-redirect sub-mechanism (durable_root() resolving to the worktree under a concurrent Admiral epic-lease) recurred verbatim in 671 (671-reconcile/lessons-delta.json confirm op)."
    },
    {
      "op": "confirm",
      "id": "loo-residual-diagnostic-over-self-weighted-predictor",
      "grounding": "664-reference-laps/lessons-delta.json confirm op: the g4 GATING jackknife is out-of-sample delete-d/driver-block (27-45 laps dropped per replicate), NOT self-weighted; the cold plan critic forced the leveraged design before any code, reviewer confirmed non-self-weighted."
    },
    {
      "op": "confirm",
      "id": "scope-self-authored-regression-to-import-graph",
      "grounding": "664-reference-laps/lessons-delta.json admiral-owns-long-batch-compute confirm op states the g4 real-data validation kept the regression 'scoped to the import graph rather than the full physics suite' -- direct corroboration of this sibling lesson, not previously cross-cited by 664's own delta."
    },
    {
      "op": "confirm",
      "id": "idle-artifact-completeness-distinguisher",
      "grounding": "ADMIRAL_LOG.md 2026-07-25 lines 56-57 (cmdr-663 watchdog INCIDENT): files built >40min old, no commit/PR/verdict, no idle signal, PowerShell Get-Process confirmed no python process running -- ambiguous state resolved by checking artifact completeness (cartographer reconcile completed + execute.json touched 11:13 = actively finishing a long thorough run), exactly the lesson's prescribed diagnostic; resolved ALIVE-not-stalled, no recovery needed."
    },
    {
      "op": "confirm",
      "id": "harvest-collected-not-verified-merged",
      "grounding": "epic-659: all 11 fenced-commander trios independently verified copied to .agent-work/staged-feedback/ (or the durable archive) BEFORE their worktree was swept, cited explicitly at every MERGE log entry (#674/#676/#677/#681/#683/#689/#697/#699/#702/#705/#709/#711) -- zero repeats of the epic-601 harvest-ordering gap across a full 12-issue/7-wave epic."
    },
    {
      "op": "mention",
      "id": "stale-map-reconcile-verify-against-final-commit",
      "grounding": "671-reconcile/lessons-delta.json mention op: an independent cartographer content-verify (reverse-import-scan against actual source) caught two real symbol-attribution errors (run_panel misattributed as a component instrument; the D->E grip consumer misattributed) that a green check_arch_map could not see -- corroborates the general 'green mechanical check is blind to content drift' principle this lesson's own staleness case exemplifies."
    }
  ]
}
```

## Queued for Human Review

- **`admiral-latitude-interrogator-inline-method`** — the Admiral used the
  constellation-interrogator's METHOD (one-at-a-time, facts-vs-decisions,
  recommend-an-answer) for its own interactive latitude settlement instead of
  standing up a redundant parallel survey lease (`ADMIRAL_LOG.md` line 23,
  self-flagged "Flagged as a lessons-audit candidate at closeout"). Low
  confidence — this was a judgment call the Admiral is pleased with, not
  friction the run worked around; not banked. If the Admiral/human wants this
  sanctioned explicitly, it belongs in `constellation-admiral` SKILL.md's
  latitude step as a one-line carve-out, not a re-observed lesson.
- **`stale-pessimism-verify-data-absence-against-current-store`** — the #668
  premise correction (`ADMIRAL_LOG.md` line 204: the "3-circuit regen needed"
  premise carried forward from #667 was false — `fp_slice_2023Q.db` already
  held all 4 circuits, and the log itself names this "the exact
  optimistic-data-chasing trap"). This is a fresh, well-grounded, repo-Admiral-
  specific corroboration of the user's OWN standing cross-project directive
  (project memory `feedback-optimistic-data-chasing.md`: "chase data avenues
  aggressively... verify stale pessimistic memory against current stores
  before repeating it"). Not banked as a new `LESSONS.md` lesson — it is
  already tracked at the correct altitude (personal memory, cross-project);
  recommend only a cross-reference note, not a repo-specific bank entry.
- **`dont-relabel-preexisting-threshold-as-validated`** — Fred's direct
  correction on the #660 corner-gate constant wording (`ADMIRAL_LOG.md` line
  32: don't call an inherited/pre-existing threshold "validated" absent a
  proving test). High-value signal (a direct owner correction) but
  self-corrected within the SAME log entry with zero recurrence across the
  rest of the epic (11 more waves, several with their own frozen-constant
  work — #666/#668's F12 sets never repeated the mislabeling). Recommend
  **drop** — appears to be a one-off wording slip already fixed in the
  moment, not a repeating pattern; re-raise only if it recurs.
- **`cite-external-precedent-once-thread-verbatim`** (epic-659/665's own
  n=1 add) — single instance, narrow (one commander's handoff-authoring
  hygiene across two gates for one code region), and the general principle
  (author shared context once, thread it verbatim) is already implicit in
  existing mission-frame doctrine. Recommend **drop** — re-flag only if it
  recurs on a future run, not worth a standing bank entry now.
- **`adopt-commander-delegated-skill-variant-for-frozen-launch-order`**
  (`ADMIRAL_LOG.md` line 53) — a Wave-0 launch-order typo (named
  `constellation-commander` instead of `constellation-commander-delegated`)
  that cmdr-665 self-corrected immediately, with zero recurrence across the
  remaining 10 dispatches this epic (all correctly named the delegated
  variant per the log's own `WAVE ... LAUNCH` entries). Recommend **drop** —
  already fixed in practice.
- **`sandbox-py-shim-shadows-real-launcher`** (epic659-661's own n=1-in-trio
  add, corroborated by 4+ flags within Wave 0) — a real but narrow
  environment quirk (this sandbox's bare `py` resolves to a codex-runtime
  Python 3.12 lacking project deps, not the project's pinned 3.14). The
  GENERAL mitigation (always use the pinned 3.14 interpreter explicitly,
  never trust bare `py`) is already such deeply embedded standard practice in
  every staged delta this epic that a new standing `LESSONS.md` lesson would
  be redundant bookkeeping. Recommend **graduate directly to
  `CLAUDE.md`'s existing "Python Invocation" section** (add one line naming
  the WindowsApps path) rather than banking — skip the Active-lesson cycle
  entirely for this one.

## Workflow Feedback
- **Brief gaps:** none — the team-lead's dispatch message supplied epic
  intent, issue range, wave structure, model tiers, and exact artifact paths
  in enough detail to skip a separate `RUN_BRIEF.template.md` document; no
  `TEMPLATES_MANIFEST` diff was supplied, but the per-wave `LAUNCH_ORDER-*.md`
  files on disk document every project-specific customization directly
  (map-fence, staged-feedback FENCE, cartographer-wrong-checkout carry-forward,
  F12 pre-registration protocol), which was sufficient to distinguish
  "template was wrong" from "project customized this."
- **Artifact gaps:** two staged `lessons-delta.json` files (668, 669) each
  contain one `confirm` op citing a lesson id that does not exist anywhere in
  `.agent-work/LESSONS.md` (current or historical) — `verify-claimed-side-effects`
  and `worktree-untracked-data` respectively. Neither is explained in the
  corresponding `CONSTELLATION_FEEDBACK.md`/`AGENT_FEEDBACK.md` (668's
  `CONSTELLATION_FEEDBACK.md` documents `engine-artifact-attest` and an
  interpreter-env observation, but never `verify-claimed-side-effects` by
  name) — these read as the authoring commander believing a lesson existed
  (or inventing a plausible id) without checking `LESSONS.md` first. Both
  would raise `LessonsDeltaError: no such lesson` in `apply_lessons_delta.py`
  had this audit not caught them; re-routed above rather than silently applied
  or silently dropped.
- **What would have made this audit easier:** a single per-epic manifest file
  listing exactly which `staged-feedback/<id>/` directories exist and which
  work_id each corresponds to (this epic used 4 different naming conventions
  across its 11 trios — `epic659-661`, `epic-659/663`, `epic-659/665`, and
  plain `662-segment-map` etc. — discovering all of them required listing
  three different parent directories by hand).
