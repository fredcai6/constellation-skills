# Launch Order: `commander-230 — issue #230 (epic-226 item D)`

Commanders start cold. Everything you need is pasted below — do not assume you can
open anything referenced by id alone.

## Mission

**Issue #230 — planning: `@grade` fixedness schema + `grade_lint.py` (the guess ledger
IS the pre-flight).**

Deliverable: a merged-ready PR against `fredcai6/constellation-skills` implementing the
five build items below, with the acceptance evidence pasted into your verdict.

How it serves the epic intent: epic-226 is "spend agent effort on the actual problem
instead of the scaffolding." Your issue attacks a different scaffolding tax than #227's:
today, a plan's decisions are either silently treated as fixed (no way to say "this is a
guess, revisit freely") or, if guess-marking existed at all, it would live in a second
hand-maintained ledger that drifts from the plan. Your deliverable makes fixedness an
inline, greppable property of the decision itself, so no second artifact ever needs
reading or maintaining.

**Full issue body, verbatim:**

> Spec S6 (S8 folded in). Design ratified via 3-agent design-it-twice panel (archived:
> dit-I2-*-RESULT.md). Register note from the human: this is a traceability aid, not high
> ceremony.
>
> Build:
> 1. Markup: one inline `@grade:` tag on the decision's own line in existing decision
>    blocks (Pre-Rulings, Decision Anchors, anchors.decision[], spec sections). Grammar:
>    `@grade: <tier>[ /provenance][ · leans <ids>][ · settle: <experiment>]`, tier ∈
>    settled|guess|placeholder. Floor: tier always; `settle:` required on guess;
>    provenance (/human|/measured|/inherited) required on settled. `leans` optional
>    sharpening.
> 2. Executor doctrine (planning + executing skills): tier is an index into an action at
>    a reality-contradiction — guess→revise in place freely, run the settle experiment,
>    regrade settled/measured, no reopen/float; settled/human + settled/inherited→stop
>    and float to the owning tier; settled/measured→re-measure, contradicting measurement
>    licenses revisit with new provenance; placeholder→hard-stop only if the current
>    slice leans on it.
> 3. THE FORK, ratified: lint loud, execute safe — pre-flight lint FAILs on ungraded
>    decisions in recognized blocks (new plans can't ship ungraded); at execution time
>    ungraded reads as settled (legacy plans behave like today; the tag only buys
>    freedom).
> 4. `scripts/grade_lint.py`: generates the guess-ledger view on demand (load-bearing
>    guesses, guesses missing settle, ungraded decisions, settled inventory), scans
>    contradictions/TBD sections, surfaces ALL objections as ONE batched question at the
>    existing plan-approval checkpoint (no new checkpoint). This IS the batched
>    plan-conflict pre-flight (#219's dormant thread ships here).
> 5. Template updates: the decision-block templates in planning skills gain the tag
>    convention + one example line each.
>
> Burden checkpoint (spec-mandated): after the first epic that runs fully graded, review
> actual authoring burden vs value and keep/trim.
> Thread-C coupling (explicit): `expires` and cross-artifact `leans` are deferred PENDING
> Thread C (issue H), not dead.
>
> Acceptance: grade_lint unit tests (fixture plans with seeded violations: ungraded
> load-bearing FAIL, guess-without-settle FAIL, dangling leans FAIL, clean plan PASS);
> template round-trips. Executor rules are doctrine-observed-at-first-use (eval-on-change
> trigger when a planning skill next changes — #136 seam). Out of scope: numeric
> confidence, depends-on edges, stored ledger table, per-decision revisit override (all
> recorded untaken roads).

## Ratified design (dit-I2-caller, pasted in full — this is the frozen schema, not a
starting point)

Design-it-twice already ran and picked **common-caller-first** (`dit-I2-caller-RESULT.md`,
archived at `.agent-work/archive/2026-07-24-explore-design-thrust/`). Do not re-derive the
schema — implement this one. Pasted verbatim because it is the single most load-bearing
spec content in this issue and you cannot open the archive from inside your worktree
(untracked; see Data Locations):

**Grammar** — one inline tag, welded to the decision it grades. The "guess ledger" is not
an artifact; it is a grep over these tags.

```
decision:dedup-wal — dedup writes reuse the existing WAL, not a new journal.
  @grade: guess · leans g1-implement · settle: 20-line spike appends 2 records, assert ordering survives a crash
```
```
decision:error-envelope — public error shape is {code,msg,retriable}.
  @grade: settled/human · leans g1-implement,g1-review
```

Markdown form (Pre-Rulings, Decision Anchors, latitude Pre-Rulings): a child line under
the decision bullet, backtick-fenced. JSON form (`EXECUTE_PLAN` `anchors.decision[]`):
appended to the decision string itself, so grade and decision cannot separate:
```json
"decision": ["decision:dedup-wal — reuse WAL not new journal @grade: guess · leans g1-implement · settle: 20-line spike, assert ordering"]
```
`@grade:` is the sole greppable anchor. `·` separates fields; only `@grade: <tier>` is
hard-required — every other field's absence degrades gracefully, never errors.

**Fields** — tier (`settled|guess|placeholder`, always required); provenance
(`/human|/measured|/inherited`, required when tier is settled, else WARN); `leans`
(gate/item ids in *this* plan, optional, dangling id → FAIL); `settle:` (one line, the
cheapest experiment, required on `guess` else FAIL).

**Invariants (7, verbatim from the ratified candidate):**
1. One grade per decision, in a recognized block (`## Pre-Rulings`, `Decision Anchors`,
   `anchors.decision[]`). Absent → readers treat it as `placeholder`; linter FAILs.
2. tier is exactly one of `{settled, guess, placeholder}`.
3. settled ⇒ provenance present; absent → WARN, not FAIL.
4. guess ⇒ `settle:` present and non-empty; else FAIL.
5. `leans` ids resolve to real gate/item ids in this plan; dangling → FAIL. Empty `leans`
   is legal (future/unattached decision).
6. placeholder ⇒ no provenance, no settle (either would mean it is mis-tagged).
7. **Locality is enforced, not hoped.** No separate ledger file ever. `grade_lint.py` is a
   view generated from the inline tags every time it is asked for — never a maintained
   second place.

**Executor decision rules per tier at a reality-contradiction** (this is item 2's
doctrine content, already fully specified by the panel — you are transcribing it into
doctrine prose, not inventing it):
- `settled/human` → STOP, float to the Admiral/human; only the ruling tier unsettles it.
- `settled/measured` → may re-measure; a contradicting new measurement is evidence —
  revisit, log the new measurement as new provenance.
- `settled/inherited` → constraint from outside this run; cannot unsettle locally, float
  to the tier that owns it.
- `guess` → revisit FREELY; run `settle:` (or cheaper) if the slice leans on it; log the
  ruling; regrades to `settled/measured`. No reopen, no float.
- `placeholder` → if the slice leans on it: decide within latitude → log → regrade
  `settled`, or float if beyond latitude. If not leaned on: leave it for a later slice.

**Named untaken forks / weaknesses already recorded by the panel** (do not re-litigate
these — they are settled, not omissions you found):
- Cross-artifact `leans` (a latitude Pre-Ruling a later commander gate leans on) is
  explicitly unresolved — deferred to Thread C (issue H, #234), not yours to solve.
- Minimum viable subset, if you need to phase: `@grade: <tier>` + `settle:` on guess is
  the irreducible floor; `leans` and `provenance` are fast-follow sharpening, not
  required for the floor to be useful. The issue's acceptance criteria do not require
  phasing — build the floor and both sharpening fields together unless you hit a genuine
  blocker, in which case narrowing to the floor with a stated reason is a delegated
  scope-narrowing (see Inherited Latitude), not a float.

## Prior-Wave Verdicts (pasted)

None — you are **wave 0**. No prior-wave verdict exists for this epic. (Design-it-twice
for your headline schema is nonetheless pre-satisfied — see Pre-Rulings below and the
pasted design above.)

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- **PR-7 — VERIFY THE ISSUE'S CLAIMS AGAINST THE CODE BEFORE PLANNING.** Active repo
  lesson `verify-launch-order-claims-against-code` (two prior data points). Before you
  freeze a plan: `grep -r "@grade\|grade_lint\|guess.ledger" skills/ scripts/ tests/` in
  your worktree. As of this launch order's authoring, that search turns up **nothing in
  shipped code** — only design-archive material (`.agent-work/archive/...`, untracked,
  outside your worktree) and this epic's own contract/launch-order files. Unlike #227,
  this issue is a genuine **build-from-zero**, not a rediscovery of already-shipped
  mechanism — the honest-null path is unlikely to apply to the whole issue, but still run
  the grep yourself and report what you found; a partial null on one sub-item is still
  possible and still a success if it occurs.
- **PR-6 — CANONICAL DOCTRINE SOURCE.** Any doctrine prose you add (item 2's executor
  rules, item 3's fork rule) goes to `skills/_shared/global-*.md` **only if** it is
  cross-role doctrine; role-specific doctrine (e.g. the Decision Anchors convention in
  `skills/commander/references/commander-core.md`) goes to that role's canonical
  `references/` or `templates/` source directly — **never** to
  `skills/<role>/references/global-*.md`, which is an install-time copy
  `install_constellation.py` regenerates and silently overwrites. If you touch any
  `global-*.md` doctrine, regenerate the role copies the sanctioned way (via the
  installer), not by hand.
- **PROJECT-SPECIFIC EXTENSION OF PR-5's SPIRIT — `checklist_engine.py` IS NOT YOURS.**
  Item 2's "executor doctrine" and item 3's "THE FORK" describe *decision rules an
  executor follows*, but the issue's own acceptance line says: *"Executor rules are
  doctrine-observed-at-first-use (eval-on-change trigger when a planning skill next
  changes — #136 seam)."* Read that literally: **you write doctrine prose describing the
  rules, you do not implement runtime tier-checking logic inside
  `scripts/checklist_engine.py`.** That file is #227's sole writer this wave (its own
  launch order fences it explicitly) and is being rewritten concurrently. Do not open it
  for writing. If you find yourself reaching for engine-code changes to make item 2/3
  "real," that is a scope signal to float, not a reason to touch that file.
- **FILE-OWNERSHIP TENSION WITH #231 — SURFACE, DO NOT RESOLVE UNILATERALLY.**
  `LAUNCH_ORDER-227.md`'s fence list assigns all of `skills/commander/**` to #231. Your
  own issue's item 5 requires editing at least
  `skills/commander/templates/MISSION_FRAME.template.md` and the Decision Anchors section
  of `skills/commander/references/commander-core.md` — both inside that fenced tree. This
  launch order grants you narrow, named ownership of exactly those two files' decision-tag
  content (see File Ownership below); #231's declared scope is a *different* paragraph
  ("commander understand doctrine" / the prototyper seam), so the overlap is believed
  non-colliding by content, not by directory. If you find #231's Commander has an open PR
  touching either file when you go to edit it, **stop and return-and-query the Admiral**
  rather than guessing at a merge order.
- **PR-8 — #219/#220 STAY IN LANE, EXCEPT THE ONE NAMED ABSORPTION.** Your issue
  explicitly absorbs #219's dormant "batched plan-conflict pre-flight" thread into item 4
  (`grade_lint.py`'s batched-objections behavior) — that absorption is in scope, declared
  by the issue itself. Anything else you find adjacent in #219 or #220 gets filed or
  commented, not absorbed.
- **Design-it-twice is PRE-SATISFIED for the headline schema and the executor decision
  rules** — both are pasted verbatim above from the ratified `dit-I2-caller-RESULT.md`.
  You do not re-run design-it-twice on the schema shape. You DO run it (or record an
  untaken road) for any load-bearing interface you invent that the panel did not settle —
  most likely `grade_lint.py`'s exact CLI surface and output format, and the precise
  regex/parse strategy for locating "recognized decision blocks" in Markdown.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report
it with the same rigor as a win. Concretely here: if PR-7's grep turns up a fragment of
this mechanism already partially built (unlikely per the search above, but verify — do
not trust the launch order's own claim uncritically), report which sub-item and what you
verified, then build only what remains.

## Inherited Latitude

You may decide, without floating to the Admiral:

- `grade_lint.py`'s exact CLI surface, output format, and internal parse strategy for
  locating "recognized decision blocks" (this is the load-bearing interface the panel
  left to you — see Pre-Rulings above).
- Test organization and fixture-plan design for the seeded-violation acceptance tests.
- Which exact files count as "decision-block templates in planning skills" beyond the two
  named above — verify each candidate holds a genuine Pre-Rulings/Decision Anchors block
  before editing it (grep found `skills/admiral/templates/LATITUDE_CONTRACT.template.md`,
  `skills/admiral/templates/LAUNCH_ORDER.template.md`,
  `skills/commander/templates/MISSION_FRAME.template.md`,
  `skills/commander/references/commander-core.md`, plus two weaker matches —
  `skills/commander-delegated/SKILL.md` and `skills/cartographer/references/map-model.md`
  — that may be false positives from a different sense of "anchors"; confirm before
  touching).
- Narrowing scope where a sub-item proves already-shipped (honest null, evidence pasted),
  or phasing to the floor subset the panel named, with the reason stated.
- Bounded fix-now triage: a small defect you trip over and fix in-lane.
- Per the latitude contract's decision-class table: **"Doctrine / shipped-template
  edit"** is `[REC] delegated` for exactly the edit this issue already specifies (D's
  planning-template tag convention, item 5) — that is you, for that edit. It becomes
  `[REC] surfaced` the moment you want to reshape doctrine **beyond** what item 5 and
  item 2's transcription of the panel's rules already name (e.g. inventing new decision
  rules the panel didn't rule on, or editing doctrine unrelated to grading).

You must **float to the Admiral** (stop and return, do not guess):

- Any edit to `scripts/checklist_engine.py` (see Pre-Rulings — not yours this wave).
- A live collision with #231 over `skills/commander/templates/MISSION_FRAME.template.md`
  or `skills/commander/references/commander-core.md`.
- Adding scope (numeric confidence, depends-on edges, a stored ledger table, per-decision
  revisit override) — all four are explicitly named untaken roads in the issue; building
  any of them is a scope addition, not a narrowing.
- Cross-artifact `leans` or an `expires` field — explicitly deferred to Thread C (#234) by
  the issue itself; implementing either here is scope creep into a different thread.
- Any doctrine edit that reshapes rules the design panel didn't already rule on.
- Anything that would require touching another wave-0 issue's fenced files
  (`.github/workflows/**` #229, `scripts/install_constellation.py` #228,
  `skills/prototyper/**` #231).

Asking up is always sanctioned. If you need epic-level context this order does not carry,
**return-and-query the Admiral** — it answers and continues you. That is a first-class
move, not a failure.

## File Ownership

**Sole writer this wave** of:
- `scripts/grade_lint.py` (new)
- `tests/test_grade_lint.py` and any seeded-violation fixture plans it needs (new)
- `skills/admiral/templates/LATITUDE_CONTRACT.template.md` and
  `skills/admiral/templates/LAUNCH_ORDER.template.md` (tag convention + example line)
- `skills/commander/templates/MISSION_FRAME.template.md` and the Decision Anchors section
  of `skills/commander/references/commander-core.md` (tag convention + example line;
  narrow, named ownership — see the file-ownership-tension Pre-Ruling above)
- Your findings file: `.agent-work/epic-226/evidence/findings-230.md`

**Fenced — do not write:** `scripts/checklist_engine.py` (#227 owns it this wave, and its
executor-behavior surface is explicitly not yours per the Pre-Rulings above),
`.github/workflows/**` (#229), `scripts/install_constellation.py` (#228),
`skills/prototyper/**` and any part of `skills/commander/**` beyond the two named files
(#231).

## Workspace

Absolute worktree path: `C:/Programs/constellation-wt-230`
Branch: `issue-230` · Base: current `main`
Provisioned by the Admiral with:
```
git worktree add C:/Programs/constellation-wt-230 -b issue-230 main
```

**First step, before any git operation:** run
`py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-230`
— it must exit 0, proving you are in your own worktree and not the shared checkout. Paste
its output into your return report.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself,
not a local merge that would diverge your worktree from main).

## Inherited Context

**This repo VENDORS its own scripts.** `scripts/` in the repo root is the real one — work
from the repo copy, not from any globally-installed `C:/Users/fredc/.claude/skills/...`
copy. The two **can diverge**. Same for templates: prefer `skills/<role>/templates/`.

**Active lessons from `.agent-work/LESSONS.md` that bear on your mission:**

- `lesson:verify-launch-order-claims-against-code` (project / delegated-planning, 2 data
  points): verify this launch order's named claims against current code before planning —
  see PR-7 above; this is why PR-7 exists, honor it literally.
- `lesson:verify-harness-field-and-drive-real-writer` (project / testing): when a test
  depends on a harness-supplied field or format, verify it against the real contract and
  drive the REAL producing path, not a hand-injected fixture. **Directly relevant to your
  seeded-violation fixture plans:** build them as real Markdown/JSON decision blocks a
  planning skill would actually emit (per the pasted grammar above), not a
  hand-simplified stand-in shape that would pass even if your parser mis-reads the real
  format.
- `lesson:test-harness-concurrency-failsafe` and
  `lesson:observe-midprocess-state-not-via-end-output`: unlikely to apply — `grade_lint.py`
  is a single-pass static scanner, not a concurrent or long-running process. Note only if
  you find otherwise.

**Platform invariants (Windows):**

- **Command-checks run under a POSIX shell (bash).** Author `grep`/`&&`/pipe checks in
  POSIX form.
- **`gh pr create` body:** write the body to a temp file and use `gh pr create -F <file>`.
  Never a heredoc, never a PowerShell `@'...'@` here-string for `--body`.
- Set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you
  capture — cp1252 pipes corrupt captured output silently.
- The Agent-tool `isolation:"worktree"` flag is a **silent no-op** on Windows. Your
  worktree is real because the Admiral provisioned it with `git worktree add` — verify
  with `--here`.

**Charter-lite carrier:** this repo has no `docs/agents/` overlay, so this block is your
doctrine carrier. Beyond it, your inherited globals are
`references/global-orchestrator.md` + `references/global-everyone.md` bundled with your
skill.

**Doctrine you must not re-derive** (it is inherited, not restated per-handoff):
correctness over velocity for promoted behavior; behavior changes are test-led where a
test surface exists; fail visibly rather than emit plausible wrong output; one canonical
path, no speculative abstraction.

## Pre-empted Steps

- **Latitude / authorization:** settled by the Admiral's confirmed latitude contract. This
  launch order IS the ratified intent — satisfy `user-decision` checkpoints on your spine
  by citing it.
- **Design-it-twice on the schema and executor decision rules:** pre-satisfied by the
  archived 3-agent panel (`dit-I2-caller-RESULT.md`), pasted in full above. Record it as
  pre-empted; run it only for the load-bearing interfaces the panel left open (see
  Pre-Rulings).
- **Issue triage / scoping:** the issue body is frozen as written. Do not re-scope it.
- **Worktree provisioning:** done for you (verify with `--here`, do not create your own).

## Data Locations

Untracked inputs absent from your worktree, in the main checkout at
`C:/Programs/constellation-skills`:

- `.agent-work/` (the whole tree — lessons inbox, prior epic archives, the Admiral's live
  spine). **Read-only for you.**
- `.agent-work/archive/2026-07-24-explore-design-thrust/` holds the full design-it-twice
  record. The essential content is already pasted above; open `dit-I2-caller-RESULT.md`
  directly only if you need a self-score or an untaken-fork detail this order didn't
  transcribe. If you cannot locate it, that is a **context query for the Admiral**, not a
  reason to redesign.
- `dit-I2-guess-grading-BRIEF.md` and `dit-I2-flex-RESULT.md` / `dit-I2-min-RESULT.md` in
  the same directory are the losing/alternate candidates from the panel — reference only
  if you need to understand why caller-first won; do not resurrect their shapes.

## Budget

- **Model tier (required):** **opus** — one of the two design-heavy wave-0 issues per the
  latitude contract's Budget row (a grammar plus a linter plus doctrine, even with the
  schema pre-ratified, needs real judgment on parse-strategy edge cases and doctrine
  phrasing). Crew (implementer/reviewer) run at **sonnet**. **No Fable at any tier.**
- **Compute/time, session-window:** you are one of five concurrent wave-0 Commanders
  drawing on a shared usage pool. Keep crew dispatches tight; do not spawn speculative
  parallel crews. If you hit a session limit mid-flight, write your state to your spine
  and return — do not silently die.

## Stop Conditions

Stop and return when:

- A decision listed as **float to the Admiral** above is needed.
- You discover #231 mid-edit on `MISSION_FRAME.template.md` or `commander-core.md`.
- Your scope would exceed the issue's declared boundaries (numeric confidence,
  depends-on edges, a stored ledger table, per-decision revisit override, cross-artifact
  `leans`, `expires`).
- The suite goes red in a way you cannot attribute to your own change within a bounded
  effort — return with the failure attributed by a `uniq -c`-style command over the
  failure list, never from the pytest tail alone.
- Budget crossed, or evidence for an acceptance item proves impossible to produce.
- You need **context this order does not cover and cannot safely proceed without** —
  return-and-query the Admiral (it answers and continues you). Asking up is always
  sanctioned.

## Return Shape

Write **two** artifacts in the main checkout's shared `.agent-work/` (git-common-dir
resolution points the durable trio at one shared root):

1. `.agent-work/epic-226/evidence/findings-230.md` — your working findings (PR-7 grep
   results, template-candidate verification, parse-strategy notes). You are the sole
   writer of this file.
2. `.agent-work/epic-226/verdicts/commander-230.md` — the verdict, containing:
   - **Verdict** — per build item (1–5): SHIPPED / HONEST-NULL (already existed, with the
     code evidence) / BLOCKED (with the reason).
   - **Evidence** —
     - `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-230`
       output.
     - `py -m pytest tests/ -q` exit code + tail, run on your branch.
     - The seeded-violation fixture tests, named, with pass output for each of: ungraded
       load-bearing FAIL, guess-without-settle FAIL, dangling-leans FAIL, clean-plan PASS.
     - The template round-trip evidence (a real decision block, tagged, parsed by
       `grade_lint.py`, correctly classified).
     - The PR number and URL.
   - **Map impact** — what capabilities/seams changed, for the Cartographer's reconcile.
   - **Triage candidates** — out-of-scope discoveries, each as a one-line statement.
   - **Workflow feedback** — friction in this launch order, the spine, or the tooling. Be
     blunt; this is the lessons audit's input.

**Deliver before going idle.** Write both artifacts and send your verdict **before** you
go idle: an idle notification with no artifact reads as stalled, not done. The Admiral
judges completion from what you produced, not from a message that arrives after you have
gone quiet.

When you open the PR on Windows, write the body to a temp file and use
`gh pr create -F <file>`.
