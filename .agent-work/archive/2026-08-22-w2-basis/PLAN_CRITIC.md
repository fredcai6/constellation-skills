# Plan Critic — w2-basis (converged hybrid, PLAN_ALTERNATIVES.md)

Cold read against MISSION_FRAME.md, PLAN_ALTERNATIVES.md, the three source candidates,
`scripts/checklist_engine.py`, and `skills/commander/templates/COMMANDER_SPINE.template.json`
(all read live at this run's HEAD; specific line numbers below are re-confirmed against the
files, not assumed from the plan's own citations).

Every finding below was checked against the real files, not just the plan's prose. Findings are
ordered roughly by severity.

---

## 1. `init.c1`'s promotion misattributes its own cited source and is not actually "zero new engine code" — fix-before-execute

PLAN_ALTERNATIVES.md line 40: `init.c1` → `command` (reads `engine_session.status` live — **"the
honest kind per `structured-field`'s own table"**, corrected from `artifact-conversion`'s "wrong
kind" finding).

This citation is backwards. `plan-candidate-structured-field.md:135` says, verbatim: `init.c1 |
engine session lease claimed | state_field engine_session.status == active | genuine`. Structured-
field's own table recommends `state_field`, not `command`. `artifact-conversion`'s table (line 81)
is the one that says `command`. The hybrid credits the wrong candidate for the choice it made.

This isn't just a citation nit — it exposes that **whichever kind is actually chosen, `init.c1`
does not fit band 1's blanket claim of "zero new engine code, reuses the engine's existing
refusal verbatim."**
- `state_field` is not an existing engine check kind. `_check_condition()`
  (`scripts/checklist_engine.py:1048-1133`) only recognizes `command`, `artifact`, and
  `git-change-policy`, raising `EngineError(f"unknown check kind {kind!r}")` for anything else.
  Shipping `state_field` as a `check.kind` requires genuinely new engine code — the opposite of
  what band 1 claims for all four of its members.
- `command` avoids that, but requires a brand-new, unnamed, unwritten script that must
  independently re-open and re-parse `spine.json` from disk to read `engine_session.status` —
  nontrivial new engineering that the plan does not name (contrast with `plan.c1`/`reconcile.c1`/
  `archive.c2`, each of which gets a concrete `evidence_type`/command named in the same paragraph).

`init.c1` is `bookend: true` and is the **first postcondition of the first gate of every single
Commander run in the corpus** (confirmed in `skills/commander/templates/COMMANDER_SPINE.template.json:7-17`).
Shipping an unwritten, unreviewed script as "live, blocking, on merge" against that specific gate,
with no report-only trial, is a much higher blast-radius bet than the other three promotions in
the same batch.

**Fix**: either name the actual command string/script and give it its own fresh-process red-proof
before merge, or fold `init.c1` into the same report-only-with-promotion-trigger treatment the
basis-field half already gets, rather than bundling it into "ships live, blocking" by citing a
source that recommended something else.

## 2. "Not a new refusal surface" conflates mechanism-reuse with behavior-preservation — fix-before-execute

The plan's justification for shipping the whole check-kind-promotion batch (`plan.c1`,
`reconcile.c1`, `archive.c2`, `init.c1`) live and blocking, bypassing `ruling-widening-live-
refusal-report-only`, is: "this is not a new refusal surface (5 other conditions in this same
file already block on the identical code path today)."

That's true of the *mechanism* (confirmed: the shipped template already has 7 `command`-kind and
5 `artifact`-kind checks that block live today) but not of the *behavior*, per condition. Today,
an agent satisfies `plan.c1`/`reconcile.c1`/`archive.c2`/`init.c1` with a bare `attest` — no
evidence required. After promotion, each of those four specific conditions refuses a bare attest
and demands a real artifact/command pass. No agent has ever been refused on these four gates
before; that a *different* condition elsewhere in the same file already enforces a check does not
make refusing on *these* four not-new. The ruling is about whether behavior changes for the gate
in question, not about whether the engine supports the check-kind machinery somewhere in the file.

Given `init.c1` gates the very first step of every run (see finding 1), this reasoning deserves
more scrutiny before "ships live, blocking, on merge" — at minimum an explicit acknowledgment that
this is a real behavior change being accepted deliberately, rather than argued away as not-new.

**Fix**: either get the Admiral's adjudication in hand explicitly for this widening (which
`ruling-widening-live-refusal-report-only` allows as an exemption), or give the check-kind
promotions the same report-only trial the basis-field half gets.

## 3. `reconcile.c1`'s conversion is decorative as specified — reproduces the exact failure the epic exists to kill — fix-before-execute (blocks this specific sub-decision)

PLAN_ALTERNATIVES.md line 40 gives `reconcile.c1` → `artifact` (`evidence_type: file-diff`) with
no match constraint at all. Even the fuller version in the source candidate
(`plan-candidate-artifact-conversion.md:88`, `match: {"nonempty": true}`) doesn't fix the
underlying problem: `_artifact_match_satisfied()` (`checklist_engine.py:1036-1045`) only compares
agent-*supplied* payload fields against wanted values — `payload.get(k) == v`. It never
independently re-runs `git show`/`git diff` to verify the claim. An agent can attach a
`file-diff` evidence item against **any** path, with `nonempty: true` self-declared in the
payload, and the check passes.

`structured-field`'s own table (`plan-candidate-structured-field.md:146`) independently flagged
this exact condition: `reconcile.c1 | map reflects implemented changes | *target doc not fixed
at template-authoring time* | **degenerate**`. The hybrid's resolution doesn't fix that
degeneracy — it just requires *some* artifact of the right *type* to exist, unconstrained in
content or path. This is precisely the "self-graded blob wearing an artifact costume" failure the
plan itself invokes to justify *not* converting `execute.c1`/`triage.c1` — the identical defect,
just not applied to `reconcile.c1`. Mission frame's own hard constraint
(`ruling-decorative-basis-is-a-failure`) exists specifically to prevent this class of "looks
enforced, checks nothing" mechanism.

**Fix**: either drop `reconcile.c1` from the promoted batch (fold it into the honest-null band,
which is what the candidates' own analysis suggests it deserves), or add a real, independently-
computed match — e.g. a `command`-kind check that itself runs `git diff <base>...HEAD -- <path>`
and asserts non-empty output, rather than trusting an agent-typed payload field.

## 4. The convergence table's own count is incomplete: `plan.c2` is a real condition that appears in none of the four bands — fix-before-execute

Directly counted against the live template
(`skills/commander/templates/COMMANDER_SPINE.template.json`): 8 null preconditions + 11 null
postconditions = 19, matching the plan's own headline number. But walking PLAN_ALTERNATIVES.md's
"Independent convergence" table: band 1 names 4 conditions (`plan.c1`, `reconcile.c1`,
`archive.c2`, `init.c1` — not the stated "~5"), band 2 names 2 (`plan.c4`, `plan.c5`), band 3
names all 8 preconditions, band 4 names 4 postconditions (`context.c1`-half, `execute.c1`,
`triage.c1`, `archive.c3`). That's 4+2+8+4 = **18, not 19**.

The missing condition is `plan.c2` ("execute.json authored from the converged candidate plan...
every file and decision-class in scope has its own gate" — confirmed at
`COMMANDER_SPINE.template.json:55`). It is not decorative or trivial: `structured-field`'s own
table calls it "genuine" (locator: `file`, `.agent-work/<work-id>/execute.json`), and
`artifact-conversion`'s own analysis (`plan-candidate-artifact-conversion.md:84`) calls it
"resists (partial)" with the **same judgment-vs-existence split** the plan uses to justify
authoring the new `basis` field on `plan.c4`/`plan.c5`: "the substantive claims — anchors
genuinely *cut from* the frame (fidelity), full ownership-scope coverage — are judgment calls no
`match` dict can verify... Full conversion here is the exact failure mode named in the launch
order."

Nowhere does the hybrid explain why `plan.c2` isn't a third `basis`-field candidate alongside
`c4`/`c5`, nor does it appear in the "leave everything else `check: null`" closing statement
(item 3) — it simply isn't mentioned. This is a completeness gap in the plan's own accounting,
not a missing citation.

**Fix**: explicitly place `plan.c2` in a band with a stated reason (most likely band 2, given its
own judgment-vs-existence shape mirrors `c4`/`c5` closely) before treating the 19-condition tally
as settled.

## 5. The basis-field promotion trigger is not mechanically measurable as designed — fix-before-execute

The promotion trigger for `plan.c4`/`plan.c5`'s new attest guard is "after 10 real Commander runs
have exercised [it] with zero false-refusals, OR the Admiral rules blocking explicitly." Grepped
`scripts/checklist_engine.py` and `docs/CHECKLIST_SCHEMA.md` for `report_only`/`report-only`:
zero hits in either. The one existing "`--report-only`" precedent in the corpus
(`plan.c6`'s `map_check_note`, `COMMANDER_SPINE.template.json:51`) is a flag on an *external
script's own exit-code behavior* ("Gate-vs-report is a flag flip: appending --report-only turns
this gate into a non-blocking report without rewiring the step"), not a generic engine feature —
it establishes no pattern `attest()` can reuse.

The plan's new attest guard "resolves the locator and, on failure, reports rather than blocks,"
but never says where that report is durably recorded — no evidence item, no log, no spine.json
field is named. Without persistence, "10 real runs with zero false-refusals" has nothing to count
against: nobody can query how many runs hit this locator, or how many times it failed. This is
exactly the report-only failure mode this review was asked to check for — a promotion trigger
that reads as accountable but is not actually checkable by anyone, ever.

**Fix**: either persist a report-only failure as a real, queryable record (an evidence item, a
log line, a counter on the checklist) the trigger can be measured against, or replace the
numeric trigger with something an Admiral can actually audit at a named future wave boundary.

## 6. Band 2's own chosen locator kinds don't actually reach the "judgment" claim they're justified by — fix-before-execute

The stated reason the hybrid needs a brand-new `basis` field at all (rather than just promoting
check kind, which is free) is that `plan.c4`/`plan.c5`'s real claim is *judgment* — "converged to
one recommendation" / "triaged by human" — which "no mechanical check can make." But the two
locator kinds actually kept (`file`, `evidence_ref`) only verify that named files *exist*
(`plan-candidate-*.md` glob + `PLAN_ALTERNATIVES.md`; `PLAN_CRITIC.md`). They do not verify
convergence or triage any more than `artifact-conversion`'s own already-proposed conversion for
these same two conditions would (`match: {"converged": true}` / `match: {"triaged": true}`,
`plan-candidate-artifact-conversion.md:85-86`) — which is exactly as self-asserted, and which the
hybrid explicitly declines in favor of the new field.

If the shipped locator can only confirm existence either way, the new field's marginal value over
simply promoting `plan.c4`/`plan.c5` to `artifact` (zero new schema, per `ruling-engine-first-
backfill-where-it-earns-it`'s "earns it" bar) is unclear on the plan's own terms. This directly
undercuts the plan's own load-bearing sentence: "this is the only band where a brand-new field
earns anything a promoted check kind can't already give it" — as authored, it doesn't yet.

**Fix**: either strengthen the two `basis` locators to actually test something an `artifact` match
dict cannot (e.g. require the referenced file's content to name a specific recommendation string,
or require a distinct evidence type not already available to `artifact`), or have the Admiral
confirm explicitly that the new field is worth its engine-risk for what is, as specified, the same
existence-only guarantee `artifact` already provides.

## 7. `.agent-work/templates/` overlay/baseline sync is dropped between the mission frame and the plan — note-only, should be an explicit execute.json step

The mission frame's own Structural Anchors name `.agent-work/templates/` explicitly: "overlay
mirror with `.baseline` copies; changing the shipped template means syncing both (Inherited
Context)." PLAN_ALTERNATIVES.md never mentions `.agent-work/templates/`, overlay, or baseline —
zero occurrences. Verified directly: `.agent-work/templates/COMMANDER_SPINE.template.json` and
`.agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json` are
currently byte-identical to the shipped `skills/commander/templates/COMMANDER_SPINE.template.json`
(diffed all three; no output). Nothing in the plan schedules updating either copy once this wave
edits the shipped template, so the overlay/baseline will silently drift the moment this merges.

**Fix**: this is likely a one-line addition once execute.json is authored (sync or explicitly
justify not syncing), but it should be a named step, not an implicit assumption the plan carries
forward unaddressed.

## 8. No red-proof / test plan named anywhere in the document — note-only at this stage

PLAN_ALTERNATIVES.md contains zero occurrences of the word "test." Given the mission frame's own
dogfooding constraint (new engine code changing `checklist_engine.py` must be validated via
fresh-process CLI runs or pytest, never by re-querying this run's own live door) and
`ruling-red-proof-pinned-to-shipped-revision`, the plan should at least gesture at what a
red-proof for the new attest guard / new `command`-kind check / new render line looks like before
`execute.json` is authored. Not fatal at the plan-alternatives stage — this is normally an
`execute.json`-level concern — but worth flagging given the epic's own history with unwired/
unexercised checks (the `map_check_note` defect cited in the mission frame's own Examples/Events).

## Where the plan is solid (checked, not just asserted)

- **`plan.c1` → `artifact` (mission-frame)** and **`archive.c2` → `artifact` (command-output,
  exit 0)** are well-founded: `plan.c1`'s target file is a real, fixed path already
  independently re-verified by `plan.c6`'s own live `command` check
  (`map_orient.py verify-frame`), and `archive.c2`'s conversion reuses an existing evidence type
  against a genuinely re-runnable `git` command. No issue found with either.
- **INV-2 purity is correctly not violated by a `command`-kind check reading live state at
  `start`/`advance`.** Checked precisely: INV-2 (`checklist_engine.py:2363-2368`) scopes only
  `state()`/`_condition_view`/`_blocking_conditions` — it explicitly says "only `start()`/
  `advance()` actually run a check." Existing shipped `command`-kind checks already run
  subprocesses that read live state today (e.g. `verify_state_note.py`,
  `COMMANDER_SPINE.template.json:70`). A new `command`-kind check for `init.c1` reading state
  live at `start`/`advance` would not, on its own, violate INV-2 — the plan's misattribution
  (finding 1) is a citation/kind problem, not an INV-2 violation.
- **The 8-precondition "structurally guaranteed" band and the 19-condition total are accurate.**
  Independently recomputed by walking the live JSON: 8 null preconditions
  (`understand.p1, plan.p1, execute.p1, reconcile.p1, triage.p1, review.p1, feedback.p1,
  archive.p1`), 11 null postconditions — exact match to the plan's claimed ids and counts (minus
  the `plan.c2` gap in finding 4).
- **The panel-of-3 / single-critic staging choice is reasonable and defensible as written** — no
  issue found with that meta-decision.
