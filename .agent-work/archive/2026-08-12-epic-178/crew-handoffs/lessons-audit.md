# Lesson Candidates: `epic-178` (Context Governor v1)

Nominations only — nothing here is applied until the dispatcher/Admiral routes it. Every
candidate cites a grounding artifact line; the audit was driven through
`checklist_engine.py` as a survey (`.agent-work/epic-178/lessons-audit.json`, work_id
`epic-178-lessons-audit`).

Of the 7 candidate signals in `LESSONS_RUN_BRIEF.md`, **3 confirm existing permanent
doctrine already outside the LESSONS.md inbox** (not new adds), **1 needed a correction to
its own attribution**, and 4 are genuinely new. One additional candidate (#8, dispatch-shape
validation) and one meta-observation (log-tagging discipline) were found beyond the brief's
list.

## Candidates

### `classifier-transient-denial-retry`
- **Scope:** `project`
- **Task-class:** `general-workflow`
- **Observed:** `gh pr create` (180-result.md:61-66) was transiently denied with "Blocked
  by classifier"; an identical retry succeeded immediately. A second, distinct instance hit
  the **Admiral's own** `git reset --hard` (vetoed; fell back to `git restore` per
  ADMIRAL_LOG.md:44) — **not** impl-182 as the run brief's candidate list asserted. impl-182's
  result/review artifacts contain no mention of "classifier" at all (grepped, zero hits) —
  the brief's attribution is ungrounded and should be corrected.
- **Cost:** Low this run (both resolved by immediate retry/fallback with no lost work), but
  the pattern is undocumented outside one narrow "worked example" in
  `LATITUDE_CONTRACT.template.md` (scoped to merge-class actions only). Read/create actions
  (`gh pr create`, `git log`, `git diff --stat`) aren't merge-class, so a future crew member
  hitting this outside a merge context has no doctrine pointer telling them "retry once
  before treating it as a real block."
- **Proposal:** Add a short note to `skills/_shared/windows.md` (harness quirks, alongside
  the existing worktree-isolation-no-op precedent): "the permission classifier can transiently
  deny a `gh`/`git` command with 'Blocked by classifier'; an identical retry typically
  succeeds. Retry once before escalating or treating it as a real policy block. For
  **delegated-class** actions (merge, issue-close), the fallback is still the contract's
  human-approval-then-batch rule — this note is for the more common case of an ordinary
  read/create hitting the same transient flakiness."
- **Grounding:** `180-result.md:61-66`; `ADMIRAL_LOG.md:44`
- **Corroboration:** Assertion-level (2 grounded instances, this run only) but consistent
  with the pre-existing `LATITUDE_CONTRACT.template.md:39` worked-example precedent for the
  same harness behavior in a different class of action.
- **Confidence:** `medium`
- **Routing:** `graduate-and-retire` → `skills/_shared/windows.md`. **Targets a `.md` doctrine
  file → needs `authority=human`.** Per the ladder, this is a positive-recipe form (state
  the retry-once behavior directly). No drill run yet — the failure mode is a simple
  fact-lookup/retry habit, not a discipline-under-pressure scenario, so a full before/after
  drill has low marginal value; recommend the human accept on grounding alone or commission a
  drill if they want a demonstrated repro.

### `test-harness-concurrency-failsafe`
- **Scope:** `project`
- **Task-class:** `testing`
- **Observed:** The first version of #180's TF9 concurrency test hung pytest indefinitely: a
  writer thread died on a transient Windows `os.replace` sharing violation before setting its
  stop flag; the non-daemon reader thread then spun forever (180-result.md:98-112).
- **Cost:** Would have hung any subsequent full-suite run touching this test file until
  manually killed — a silent CI-style stall, not a loud failure.
- **Proposal:** Fixed **this run** (try/except + `stop.set()` in `finally`, both threads
  `daemon=True`) — verified by 7 total green re-runs (implementer 3x + reviewer 4x), 0 flakes.
  The generalizable lesson — "test-harness threads doing real concurrent file I/O need the
  same fail-safe discipline (try/except, daemon threads) as the production code under test" —
  has no existing home; this repo has no dedicated testing-conventions doc to graduate it
  into (checked: no `*testing*` doctrine file exists).
- **Grounding:** `180-result.md:98-112`
- **Corroboration:** Strong — the fix itself is the corroboration (before: hangs; after: 7/7
  green, reviewer independently re-verified).
- **Confidence:** `medium`
- **Routing:** `lesson-inbox delta (add)` — single instance so far; bank rather than graduate
  because there is no natural doctrine home yet and one more occurrence would justify minting
  one (e.g., a `testing-conventions.md` reference). See `lessons-delta.json` block below.

### `launch-order-doctrine-home-path`
- **Scope:** `admiral`
- **Task-class:** `general-workflow`
- **Observed:** The #183 launch order cited global doctrine's editable home as
  `skills/<role>/references/global-*.md`; the canonical **source** is
  `skills/_shared/global-*.md`, copied into each skill's `references/` at install time by
  `install_constellation.py` (confirmed: `install_constellation.py:93-101` names
  `SHARED_REFERENCE_ROOT = SOURCE_ROOT / "_shared"` as the single source). The implementer
  caught this and edited the correct source (183-result.md Float 3; ADMIRAL_LOG.md's
  scope/triage RULING notes it "for future orders"). Checked `LAUNCH_ORDER.template.md` —
  it has no slot at all instructing where to cite a doctrine-edit target, so this was an ad
  hoc Admiral citation, not a template following a wrong precedent.
- **Cost:** Zero this run (implementer's own diligence caught it before any wrong edit
  happened), but the next launch order dispatching a doctrine edit has nothing preventing a
  repeat, and a less careful implementer could edit the installed copy instead of the source
  (a wasted edit, invisible until the next `install_constellation.py` run overwrites it).
- **Proposal:** Add one clarifying line to `skills/admiral/SKILL.md` near the launch-order
  bullet (line 50) or to `LAUNCH_ORDER.template.md` itself: "When a launch order asks a crew
  member to **edit** global doctrine, cite the canonical source `skills/_shared/global-*.md`
  — not `skills/<role>/references/global-*.md`, which is an install-time copy regenerated by
  `install_constellation.py`."
- **Grounding:** `183-result.md` Float 3; `ADMIRAL_LOG.md:42` (RULING, Scope/triage)
- **Corroboration:** Single instance, assertion-level; caught before causing harm.
- **Confidence:** `medium`
- **Routing:** `template delta` → `skills/admiral/SKILL.md` (or `LAUNCH_ORDER.template.md`).
  **Targets doctrine → `authority=human`.** No drill run — this is a wrong-shaped-output
  fix (rung 3, state the canonical path), not a discipline/pressure scenario; low value from
  a full drill given the simplicity, but flagging per doctrine that one would be the rigorous
  route if the human wants it demonstrated first.

### `engine-self-edit-hazard-pattern`
- **Scope:** `admiral`
- **Task-class:** `general-workflow`
- **Observed:** #179 rewrote `scripts/checklist_engine.py` — the very engine driving this
  epic's own spine. The Admiral pre-ruled the hazard **before** wave 1
  (`LATITUDE_CONTRACT.md` Pre-Rulings: "Engine-edit hazard (#179)") and executed it exactly as
  pre-ruled: implement/review in an isolated worktree → before merge, run the new engine
  read-only (`current` on the live spine, exit 0) and mutating (`advance` on a **copy**, clean
  `REFUSED: postconditions unmet`, no crash) → only then merge → sync the local checkout to
  the new engine → continue driving remaining spine advances on it with real `--why` entries
  (ADMIRAL_LOG.md:21, :44). This is a clean, fully-worked, zero-incident execution of a
  hazard class that has no existing name or recipe in doctrine (checked `fleet-doctrine.md`'s
  "Engine/platform quirks" section — covers compact/utf-8/lease-staleness, not self-editing).
- **Cost:** N/A this run (executed successfully) — the value is in naming the pattern before
  the next epic that edits the engine mid-flight has to re-derive it from scratch.
- **Proposal:** Add a positive-recipe bullet to `fleet-doctrine.md`'s "Engine/platform quirks"
  section (or a new subsection): "**Self-hosting an engine edit mid-run:** pre-rule it in the
  latitude contract before wave 1. Implement/review in an isolated worktree. Before merging,
  verify the new engine still drives your **live** spine: a read-only `current` (exit 0) and
  a mutating verb run against a **copy** of the spine (never the live file) to confirm it
  refuses/succeeds sanely, not crashes. Only then merge, sync your local checkout to the new
  engine, and continue driving remaining advances on it — this is how the feature gets
  proven in production, not just in its own test suite."
- **Grounding:** `LATITUDE_CONTRACT.md` Pre-Rulings section; `ADMIRAL_LOG.md:21,44`
- **Corroboration:** Single instance, but primary-source (the Admiral's own log, not a
  secondhand claim) and the outcome (166→181 tests green throughout, no incident) is strong
  positive evidence.
- **Confidence:** `high`
- **Routing:** `graduate-and-retire` → `skills/admiral/references/fleet-doctrine.md`
  ("Engine/platform quirks" or a new subsection). **Targets doctrine → `authority=human`.**
  No drill run yet (recommend one before/if the human wants it demonstrated — the scenario
  is reproducible: arm a throwaway subagent with a fake "engine rewrite mid-spine" fixture,
  once without this doctrine and once with it, and see whether the pre-merge live-spine
  check gets skipped).

### `git-update-ref-working-tree-skew`
- **Scope:** `admiral`
- **Task-class:** `general-workflow`
- **Observed:** The Admiral advanced local `main` via a bare `git update-ref` (to fast-forward
  without disrupting the mid-run working tree) partway through the run. This left the working
  tree stale relative to the new ref: `gauge_reader.py` (a file that existed at the new HEAD
  but whose content differed from what was checked out) showed as a **staged deletion** —
  a state that "could have silently reverted a merged PR at closeout commit" (per the run
  brief's own framing, corroborated by ADMIRAL_LOG.md:44). Caught and fixed via `git restore`
  (the classifier vetoed the more obvious `git reset --hard`, matching the documented
  permission-fallback pattern).
- **Cost:** Near-miss on silently reverting merged work at closeout — a real, if
  self-caught, hazard. By the log's own entry-grammar (ADMIRAL_LOG.md:9-17, which defines
  `ADMIRAL ERROR` as "a mistake you own... a closeout asset, not a liability"), this
  qualifies as an `ADMIRAL ERROR` entry, but it was folded into a `MERGE` entry's prose
  instead — a minor process-discipline slip in the log's own tagging on top of the underlying
  git hazard.
- **Proposal:** Add to `fleet-doctrine.md`'s "Adjudication invariants (Admiral errors that
  bit)" section (the section is literally titled for this): "**Advancing local `main`
  mid-run without a normal checkout (e.g. a bare `git update-ref` to fast-forward without
  disturbing an in-flight working tree) leaves the working tree stale relative to the new
  ref** — a file that changed between old and new HEAD can appear as a false local
  modification/deletion, risking an accidental revert at the next commit/merge. Sync the
  working tree too (`git status` + `git restore`/checkout), not just the ref, whenever you
  advance main this way." Also worth a one-line addendum to the entry-grammar section: tag a
  genuine self-inflicted near-miss as `ADMIRAL ERROR` even when it's caught and fixed inline,
  rather than folding it into a `MERGE` entry's prose — the dedicated tag is what makes it
  greppable at the next lessons audit.
- **Grounding:** `ADMIRAL_LOG.md:44`; `LESSONS_RUN_BRIEF.md` candidate 7
- **Corroboration:** Single instance, primary-source, self-caught before any real damage.
- **Confidence:** `high`
- **Routing:** `graduate-and-retire` → `skills/admiral/references/fleet-doctrine.md`
  ("Adjudication invariants (Admiral errors that bit)"). **Targets doctrine →
  `authority=human`.** No drill run — recommend one if the human wants it demonstrated
  (scenario: a throwaway subagent given a spine mid-advance via bare `git update-ref`,
  once without the doctrine line and once with it, checked for whether it notices the
  working-tree skew before the next commit).

## Existing-Lesson Reconciliation

`.agent-work/LESSONS.md` Active section is confirmed **empty** (verified directly, matches
the run brief). There is nothing to `confirm`/`disconfirm` **as a playbook op** — but three
of the brief's candidate signals independently re-validate **permanent doctrine that already
lives outside the inbox**. Recorded here for the audit trail, not as inbox ops (no lesson id
exists to attach a `confirm` to):

- **Delayed subagent notifications (~40 min late)** — re-validates
  `fleet-doctrine.md:74-82` ("Idle sessions do not receive notifications," field-measured
  2026-07-11, four prior incidents) almost verbatim. The Admiral's active in-turn polling
  (per that doctrine's own prescribed counter) is exactly why this cost nothing. **Not a new
  lesson.** Note: the "~40 min" figure itself has no independent ADMIRAL_LOG timestamp
  grounding it — it's the run brief's own assertion (`LESSONS_RUN_BRIEF.md:17`), corroborated
  only by the pre-existing doctrine's general shape, not by a fresh measurement this run.
- **Cross-issue integration awareness (impl-182 checking #180's actual merged writer path)**
  — re-validates `global-everyone.md:86-93` ("Verify claimed side-effects against the
  world") almost exactly: impl-182 paired reader↔writer against the real merged code rather
  than a claim. **Not a new lesson**, a clean positive instance of existing doctrine.
- **Dispatch-shape ruling (implementer-with-plan + reviewer, not full Commander spines)** —
  re-validates `skills/admiral/SKILL.md:51` ("Right-size the dispatch: for small, bounded
  autonomous work, dispatch an implementer-with-plan directly rather than standing up a full
  Commander") verbatim. This run is a clean validating instance: all 5 issues merged green,
  0-2 rework each, no Commander spine needed because the DESIGN_SPEC had already frozen
  design-it-twice work. **Not a new lesson**, but worth citing as a strong precedent if this
  doctrine line is ever questioned.

## Playbook Delta (ready to apply)

Only one candidate (`test-harness-concurrency-failsafe`) is bank-worthy; the rest are either
confirms-of-permanent-doctrine (no lesson id, nothing to apply here) or doctrine graduations
that need human authority (not appliable via this script, which only writes the LESSONS.md
inbox).

```json
{
  "work_id": "epic-178",
  "tick": true,
  "ops": [
    {
      "op": "add",
      "id": "test-harness-concurrency-failsafe",
      "scope": "project",
      "task_class": "testing",
      "statement": "Test harnesses that drive real concurrent file I/O (threads doing actual reads/writes, not mocks) need the same fail-safe discipline as the production code under test: wrap per-iteration work in try/except with a guaranteed stop-signal in `finally`, and mark helper threads daemon=True as a backstop. A writer thread that dies on a transient OS error without signaling stop leaves a non-daemon reader spinning forever and hangs the whole pytest process.",
      "grounding": "crew-handoffs/180-result.md:98-112 (TF9 concurrency test hung pytest indefinitely on a transient Windows os.replace sharing violation; fixed by try/except + daemon threads; 7 total green re-runs after)",
      "bank_reason": "single instance so far in this repo; no dedicated testing-conventions doc exists to graduate this into yet. A second concurrent-file-I/O test hang would confirm this as a repo-wide pattern worth minting a reference doc for, rather than a one-off fixed in place."
    }
  ]
}
```

## Queued for Human Review
- All four `graduate-and-retire` candidates above (`classifier-transient-denial-retry`,
  `launch-order-doctrine-home-path`, `engine-self-edit-hazard-pattern`,
  `git-update-ref-working-tree-skew`) — every one targets a project doctrine `.md` file, so
  per this skill's doctrine, applying them is a human call (`authority=human`), not a
  self-apply. None has a reproduction drill run yet; each candidate above says what a drill
  would look like if the human wants one before accepting.
- **Low-confidence, not routed:** a nuance surfaced in `drill-fresh-result.md` §4 — the fresh
  drill agent needed `scripts/checklist_engine.py --help`/source to learn CLI *mechanics*
  (not doctrine's fault; it correctly distinguished "tooling knowledge" from "task briefing"
  and the human already signed off "yeah good enough" on the substance). Flagging only in
  case a future symmetric-recovery doctrine pass wants to make that scope boundary explicit
  ("`current` promises task/decision content, not CLI literacy"). Confidence too low and
  stakes too low to propose a concrete edit.

## Workflow Feedback
- **Brief gaps:** None blocking. The brief's "candidate signals" section usefully seeded the
  audit but one attribution (candidate 2, classifier denial → "#180, #182") was wrong for
  #182 (no grounding found in `182-result.md`/`182-review.md`; the real second instance is
  the Admiral's own `git reset --hard` veto). Future run briefs should derive per-candidate
  attribution from a grep of the actual artifacts rather than from memory of the run, per
  the standing practice of deriving distribution claims from a command, not recollection.
- **Artifact gaps:** None. All 5 result + 5 review docs, the drill result, ADMIRAL_LOG,
  LATITUDE_CONTRACT, and the run brief were complete, internally consistent, and
  non-performative (friction was reported candidly, including the implementer's own
  self-caught bugs, e.g. 180's concurrency-test hang and the TF9 fix write-up).
- **What would have made this audit easier:** A single consolidated "floats/triage" index
  across all 5 issues (there wasn't one — each result file's floats had to be individually
  read and cross-checked against the others, e.g. to confirm candidate 2's #182 attribution
  was wrong). Not a defect in this run, just a mechanical time cost for the audit.
