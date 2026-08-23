# Cold Critic — PLAN_ALTERNATIVES.md's converged recommendation (w3-promote)

Target: the "Output — recommendation (hybrid, not a menu)" section of
`.agent-work/w3-promote/PLAN_ALTERNATIVES.md` (the g0..g10 sequence). Candidates are background,
not re-litigated here except where the hybrid's grafting of one onto the other creates a defect
neither candidate has alone. All numbers below are freshly measured against this worktree's HEAD,
not recalled from any candidate file.

## 1. `g9`'s late placement will very likely leave the full suite RED for several gates before it
   runs — contradicting the plan's own stated reason for choosing template-sequential

**What's wrong.** Fresh measurement, this run:

```
$ python3 -c "... vs.discover_checklist_templates / vs.validate_file over all 11 shipped templates ..."
{'falsifiable-all-null': 19, 'falsifiable-unresolved-placeholder': 2}
```

`tests/test_validate_spine.py::TestCorpusSweepFindings::test_measured_finding_totals` asserts
`by_code.get("falsifiable-all-null", 0) >= 15`. Current margin to the floor is **4 gates' worth of
clearing**, not the ~6 a naive read of the pinned "measured 21" comment implies (see finding 2).
`falsifiable-all-null` fires per-*gate* (per `tasks[*]`), not per-condition, and is cleared the
moment *any one* postcondition in that gate stops being `check: null`
(`tests/test_validate_spine.py:267-273`, `test_one_real_check_among_nulls_is_innocent`).

Walking the converged sequence against what each gate's own imperative already commits to
promoting:

- `g1-commander-spine`: `init` and `reconcile` are each single-postcondition, all-null gates
  (`init.c1`, `reconcile.c1` — verified: each gate has exactly one postcondition, `check: null`)
  and are the launch order's own named "first targets." Clearing both: 19 → **17**.
- `g5-explorer-spine`: `context` and `spec` are likewise single-postcondition all-null gates
  (`context.c1`, `spec.c1` — verified fresh). g5's own imperative explicitly proposes promoting
  the locator-backed half of *both* ("`context.c1`'s 'IDEAS_BOARD.md seeded from template' half has
  a real file locator", "`spec.c1`... the file-exists half converts"). Clearing both: 17 → **15**
  — exactly at the floor.
- `g3-execute-plan`'s `e0-context` is a third single-postcondition all-null gate under active
  assessment in that gate's own imperative. If it clears too (plausible; g3 runs *before* g5): 15
  → **14**, already below the floor.
- `g6-charter` alone carries **6** all-null gates (`context`, `explore`, `interrogate`, `rigor`,
  `project-templates`, `closeout` — verified fresh), and g6's own imperative names two of them
  (`project-templates.c1`, `closeout.c1`) as promotable. Any single one of these promoting pushes
  well past the breach already established by g5.

So by the plan's *own* stated intentions for g1, g3, g5, and g6 — not a hypothetical worst case —
the corpus's `falsifiable-all-null` count drops below 15 at or before `g5`/`g6`, several gates
before `g9-validate-spine-wiring` (deliberately placed last, specifically because "it needs the
post-promotion fault count"). Between that breach and `g9`, `python3 -m pytest -q` — "the local
run is the gate" per the launch order's own platform invariant — is RED.

**Why it matters.** This directly undercuts the *stated reason* the hybrid picked
template-sequential as the backbone: "template-sequential's core property, that every gate boundary
ships a complete, independently-mergeable, revertible story for one file... the Admiral can accept
g1-gN and defer the rest." A gate boundary that leaves the full suite red is not a complete,
independently-mergeable story — accepting g1-g5 mid-wave means accepting a state where
`test_validate_spine.py` is failing for a reason none of g1-g5's own close criteria (each scoped to
`tests/test_checklist_engine.py`, per-template) ever look at. It also breaks the launch order's
Return Shape #3 discipline ("Suite result... run after your final commit") if read as applying at
each meaningful commit, not just the very last one — and this epic has already burned a wave on
"six e2e tests only pass while the work is uncommitted" (this repo's own recent history), i.e. the
project has a demonstrated blind spot exactly here.

**Disposition: fix the plan.** Do not defer the floor update wholesale to `g9`. Either (a) make
"update `test_validate_spine.py`'s pinned floor to the freshly-measured count" a close criterion of
*every* gate that clears an all-null fault (cheap: one line diff each time), so the full suite never
goes red between gates, or (b) explicitly acknowledge in `g0` or `g1` that the full suite will run
red between some gate and `g9`, and scope `g9` earlier in the sequence (e.g., immediately after
`g1`/`g2`, then again as a final re-check) rather than pinned last. Silently leaving it as currently
written ships a wave whose own mid-sequence commits fail its own stated gate.

## 2. The plan's spot-check of `test_validate_spine.py` repeats an already-stale pinned number
   without re-verifying it — understating how tight the margin already is

**What's wrong.** PLAN_ALTERNATIVES.md's "Independent convergence" section (lines ~59-64) correctly
identifies the floor's shape (`>= 15`, not `== 0`) and correctly warns that promotions will make it
go red — that part is accurate. But it then cites the floor's own comment verbatim — `"measured 21
at authoring time"` — as if that were still true, without re-running the sweep to check. It is not
still true: `git blame` pins that comment to `303b7f19e` (2026-08-11); a fresh sweep today measures
**19**, not 21 (`falsifiable-all-null` specifically; the risk-tier candidate's "21 faults total"
figure sums *both* fault codes — `19 + 2 (falsifiable-unresolved-placeholder)` — which is a
different number than the one the floor's comment is actually about, and the two get conflated).
The corpus has already drifted 2 gates closer to the floor since the pin was written, by work
outside this wave, and nobody updated the comment.

**Why it matters.** The plan's own risk framing ("my own promotions will make this exact test go
RED") is right in direction but wrong in magnitude — the real margin (4 gates from breach, not ~6)
makes finding 1's breach-before-g9 outcome more certain, not less, and a reviewer trusting the
quoted "21" would underestimate how early in the sequence this fires.

**Disposition: fix the plan.** `g0` (or wherever `g9`'s corpus-wide fault count first gets
mentioned) should state the freshly-measured 19/2 split, not repeat the stale 21, and should flag
that the pin was already stale before this wave touched anything — that's a preexisting defect this
wave's own doctrine (`decision:validate-spine-wiring-is-in-scope`) says to name, not silently
inherit.

## 3. Risk-tier's tiering discipline is asserted as "adopted inside each gate" but the actual
   inherited gate bodies neither carry the "own template's live-kind set" restriction nor the
   report-only-naming/demotion rules — and template-sequential's own design actively encourages the
   cross-template shortcut the restriction was written to forbid

**What's wrong.** The Output section says risk-tier's tiering language — "a check kind already live
in that SAME template = ship blocking; first use of that kind in that template... = ship report-only
... or demote" — is adopted "as the blocking-vs-report-only decision rule inside each gate." But the
actual quoted per-template gate bodies (kept "largely as designed" from template-sequential) do not
contain this rule anywhere in their `imperative` or `close criteria` text, and in at least one place
directly conflict with it:

- `g4-admiral-spine`'s constraint: "if `init.c2`'s promotion literally duplicates `g1`'s `init.c1`
  check shape, cite `g1` rather than re-justifying from scratch (locality payoff of doing
  COMMANDER_SPINE first)." Risk-tier's own `g3-risk-tier-partition` constraint says the opposite in
  spirit: "tiering evaluates each condition against ITS OWN template's live-kind set, never the
  corpus-wide set — artifact being live in COMMANDER_SPINE doesn't make a CARTOGRAPHER artifact
  promotion low-risk, since CARTOGRAPHER has never run that kind." In this one case the two happen
  to agree by coincidence (ADMIRAL_SPINE already has `command`(4) live per risk-tier's own measured
  table, so `init.c2`→command is independently low-risk on its own template's merits) — but nothing
  in the converged text *checks* that coincidence before permitting the citation-shortcut; it is
  written as a general locality-payoff move, not gated on "and also verify command is live in
  ADMIRAL_SPINE."
- `g8-cartographer-and-scout` is the case where the coincidence does **not** hold: risk-tier's own
  measured table records CARTOGRAPHER and SCOUT as having **zero live check kinds of any kind**
  today — verified fresh, both files' existing postconditions are 100% `check: null` outside the
  ones this wave would promote. Under risk-tier's own rule, *any* bucket-2 promotion in either file
  is HIGH-RISK by construction (first use). But `g8`'s own imperative (inherited unchanged) invites
  exactly the cross-template reuse the rule forbids: "check whether either script's command-kind
  pattern extends to `route.c1`" cites a pattern wired live at **EXPLORER_SPINE**, a different
  template, as justification. If an executor reads "reuse a live pattern elsewhere" as license to
  ship CARTOGRAPHER's first-ever check blocking, that is precisely the failure mode
  `decision:record-the-partition-per-condition`'s per-template-authority framing and risk-tier's own
  restriction exist to catch.

**Why it matters.** This is the exact question the task brief flags: does grafting the tiering rule
INSIDE each gate actually preserve the guarantee, or quietly drop it? Here it is dropped at the
level of the actual gate text a reviewer or executor would read — the guarantee exists only in
`PLAN_ALTERNATIVES.md`'s prose describing the hybrid, not in the gate bodies it says will carry it.
`execute.json` is authored from those gate bodies "largely as designed," so whatever isn't
explicitly rewritten into them does not survive.

**Disposition: fix the plan.** When authoring `execute.json`, every per-template gate must carry an
explicit constraint line: "check-kind live-ness is evaluated against THIS template's own existing
checks only; a pattern cited from another template is context, not eligibility." `g8` specifically
needs its blocking/report-only call pinned to the fact that CARTOGRAPHER/SCOUT start at zero live
checks — i.e. this wave's promotions there should default to report-only-with-named-trigger (or
demotion, if the chosen kind is `artifact` and has no report-only shape) unless a specific, stated
reason overrides that default.

## 4. `g0`'s material-exception threshold is unstated

**What's wrong.** Risk-tier's own `g2-divergence-check` proposed a concrete numeric band ("outside
[30%, 65%]... wide enough to tolerate ordinary variance, narrow enough to catch a structurally
different template") as the operational test for
`decision:record-the-partition-per-condition`'s "materially different partition." The hybrid's `g0`
description drops this entirely: "compare each template's bucket-2 fraction to 9/19 (~47%), float
any material exception" — with no stated band. "Material" is left to the executor's unaided
judgment at exactly the point this ruling calls a stop-and-float, non-silent-absorption event.

**Why it matters.** Without a stated threshold, `g0`'s close criterion ("material exceptions
flagged") is not actually checkable by anyone other than the person who wrote it — a materially
different second reviewer could reasonably disagree on whether e.g. CARTOGRAPHER's known
zero-live-check-kind structural difference, or SCOUT's population of only 4, counts as "material,"
with no shared bar to appeal to.

**Disposition: fix the plan.** Carry risk-tier's stated band (or an equivalent, explicitly reasoned
one) into `g0`'s close criteria verbatim when authoring `execute.json`, rather than leaving
"material" undefined.

## 5. `g0` and the per-template gates both claim the same notes-1.md bucket table for the same
   conditions, with no reconciliation rule if they disagree

**What's wrong.** `g0` records "the bucket for all 65 conditions across all 8 templates in one
pass" into `notes-1.md`. `g1-commander-spine` (inherited unchanged from template-sequential) has as
its own close criterion "all 19 conditions have a recorded bucket in
`.agent-work/w3-promote/notes-1.md`" and its imperative explicitly instructs *re-opening* specific
calls (`init.c1`, `archive.c3`) that `g0` will already have recorded. The Output section's only
guidance is "re-verify each against g0's survey rather than re-deriving bucket assignments from
scratch" — a narrative instruction, not a rewritten close criterion. Nothing says which record wins
if `g1`'s fresh look at `init.c1` lands on a different bucket than `g0`'s first pass did (plausible
precisely for `init.c1`, which template-sequential's own text flags as a live seam disagreement with
w2-basis).

**Why it matters.** At minimum this is duplicated work (the same 19 conditions bucketed twice, once
read-only, once "for real"); at worst it is a silent-divergence risk on exactly the artifact
(`decision:record-the-partition-per-condition`'s per-condition record) this wave's central ruling
depends on being a single source of truth.

**Disposition: fix the plan.** Either narrow `g0`'s scope in `execute.json` to the 7 templates `g1`
does not already own (COMMANDER_SPINE's own re-verification stays entirely inside `g1`, as
template-sequential designed it), or make `g1`'s close criterion explicitly "extend/amend g0's
existing rows for these 19 conditions, do not re-produce them" and say a later gate's judgment
supersedes `g0`'s on conflict, recorded as a diff not a silent overwrite.

## 6. Corpus-wide docs reconciliation (`docs/CHECK_SCRIPT_CENSUS.md`) has no owning gate

**What's wrong.** Risk-tier's `g8-reconcile-docs-and-map` explicitly owned updating
`docs/CHECK_SCRIPT_CENSUS.md`'s corpus-wide classification counts. The hybrid's Output section only
grafts risk-tier's `g1`+`g2` (the survey) onto template-sequential's backbone — it does not adopt
risk-tier's `g8`. Template-sequential's own per-gate doc-sync language is template-scoped ("update
any doc that cites stale counts for that template"), which does not naturally cover a corpus-wide
tally line. Concretely: `docs/CHECK_SCRIPT_CENSUS.md:90-93` currently pins "17 live... 8 unwired, 1
dead" across 26 rows, and `g8-cartographer-and-scout`'s own imperative proposes wiring
`check_role_spine_bookends.py` or `check_skill_freshness.py` (both currently `unwired`, verified
fresh at `docs/CHECK_SCRIPT_CENSUS.md:84-85`) live via a new command-kind check — which would move
that count from 17/8 to 18/7. No gate in the converged sequence is named as responsible for editing
that census line if `g8` does this.

**Why it matters.** This is exactly the kind of stale-count defect the epic's own thesis is about
(a claim nobody re-checks), reproduced in this wave's own output if left as-is — and it is
concretely the kind of thing `docs/CHECK_SCRIPT_CENSUS.md`'s own doc contract cares about, since the
census is cited as a load-bearing input by other gates in this same plan (`g5`, `g8` both cite it as
a "before inventing a new locator" check).

**Disposition: fix the plan.** Add a docs-reconciliation close criterion to `g9` or `g10` (or a
dedicated gate) that explicitly covers `docs/CHECK_SCRIPT_CENSUS.md`'s corpus-wide tallies, not just
template-scoped doc citations — conditioned on whether `g8` (or any other gate) actually flips a
script from unwired to live.

## 7. "Attacker-chosen mutation, not self-designed" is asserted per gate, never given a mechanism

**What's wrong.** Every gate's constraints repeat `decision:red-proof-each-promotion`'s language
("mutation not self-designed") but none names *who* chooses the mutation or how a close criterion
could verify it wasn't self-designed. This is a single Commander lane with no built-in second author
during the promotion gates themselves (the reviewer only enters after a PR is opened, per the
launch order's Return Shape #7).

**Why it matters.** As written this constraint is unfalsifiable at gate-close time — an executor
could design a mutation, convince themselves it's "what an attacker would do," and the close
criterion ("fails again under an independently-chosen mutation") has no independent party to check
independence against until the post-hoc PR review, by which point all 8 templates' worth of
red-proofs already exist.

**Disposition: accept as a named risk, with one cheap mitigation.** Full independence isn't
achievable solo mid-wave without adding process this launch order doesn't grant latitude for. But
the plan should at minimum require each red-proof's mutation to be logged with a one-line rationale
distinct from the promotion's own justification (e.g., "attacks the boundary the check's `match`
does NOT cover" rather than "restates what `match` requires") so the eventual reviewer has something
concrete to evaluate independence against, rather than trusting a bare "red-proofed" label.

## 8. Minor: `g10-integrate`'s close criteria are compressed to the point of dropping the
   Honest-Null Clause's explicit reporting requirement

**What's wrong.** Risk-tier's own `g9-integrate` explicitly required "RESULT.md written... including
per-template assessed-vs-promoted counts (Honest-Null Clause: report promoted alongside assessed)."
The hybrid's `g10-integrate` is one line: "commit, full suite, PR, RESULT.md." This is plausibly just
brevity in the summary (full detail deferred to `execute.json`), but as written it is the one place
in the converged plan where the Honest-Null Clause's specific reporting shape isn't restated.

**Disposition: not a real issue if `execute.json` restates it (likely, given the launch order names
this explicitly as a Return Shape requirement independent of this plan) — but flag it so it isn't
silently lost in the compression from candidate to hybrid summary to `execute.json`.**

## Commander triage (delegated mode, citing LAUNCH_ORDER:Inherited Latitude — plan-invalidating
## discoveries are mine to resolve within latitude; none of the 8 below exceed it)

All 8 findings are accepted as real; none rejected. Dispositions ratified, folded into
`execute.json` at authoring time (next step):

1. **Accepted — fix.** `execute.json` makes "update `test_validate_spine.py`'s pinned
   `falsifiable-all-null`/`falsifiable-unresolved-placeholder` floor to the freshly-measured count"
   a close criterion of every gate that clears an all-null fault (option (a) from the critic's own
   disposition) — the suite stays green at every gate boundary, not just at `g9`, matching the
   plan step's own "verification green at every gate boundary" requirement.
2. **Accepted — fix.** Every reference to "21" is replaced with the freshly re-measured **19**
   (`falsifiable-all-null`) **+ 2** (`falsifiable-unresolved-placeholder`) split, and `g0`/`g1`
   states plainly that the floor's own pin comment was already stale before this wave touched
   anything (a preexisting defect this wave names, per `decision:validate-spine-wiring-is-in-scope`).
3. **Accepted — fix.** Every per-template gate gains an explicit constraint: "check-kind live-ness
   is evaluated against THIS template's own existing checks only; a pattern cited from another
   template is context, not eligibility." `g8` (CARTOGRAPHER + SCOUT) is pinned to ship its
   promotions report-only-with-named-trigger (or demoted to `check: null` if the kind has no
   report-only shape) by default, since both templates measure zero live check kinds today —
   overridable only with a stated per-condition reason.
4. **Accepted — fix.** `g0` adopts risk-tier's own numeric band verbatim: a template's bucket-2
   fraction outside **[30%, 65%]** is a material exception, float it; inside the band is ordinary
   variance, record and proceed.
5. **Accepted — fix.** `g0`'s consolidated survey is narrowed to the **7 non-COMMANDER_SPINE
   templates**. COMMANDER_SPINE's own 19-condition re-verification stays entirely inside `g1`, as
   template-sequential originally designed — no duplicate table, no ownership conflict. (This
   run's own notes-1.md already produced COMMANDER_SPINE's 19-row table under `g1`'s ownership,
   confirming this is the natural seam, not a retrofit.)
6. **Accepted — fix.** A docs-reconciliation close criterion is added to `g9` (folded into the
   validate-spine-wiring gate, since both are corpus-wide, post-promotion measurements) covering
   `docs/CHECK_SCRIPT_CENSUS.md`'s corpus-wide live/unwired/dead tallies specifically, conditioned
   on whether any gate actually flips a script's wiring status.
7. **Accepted — named risk, with the proposed mitigation.** Every red-proof's mutation is logged
   with a one-line rationale distinct from the promotion's own `match`/check text (e.g., "attacks
   the boundary the check's `match` does NOT cover"), giving the eventual PR reviewer something
   concrete to evaluate independence against. Full solo-lane independence is not achievable within
   this run's granted latitude — named, not silently accepted.
8. **Accepted — restated, not a plan defect.** The final integrate gate explicitly requires
   `RESULT.md` to report promoted-alongside-assessed counts per template, per the launch order's
   own Return Shape and Honest-Null Clause — restated in full in `execute.json`, not compressed.

## Not-a-finding, for the record

- `TestShapeAcceptsEveryShippedTemplate::test_no_shape_faults` really is blocking, zero-tolerance,
  corpus-wide on shape faults, parametrized over `discover_checklist_templates(ROOT)` — verified by
  reading `tests/test_validate_spine.py:233-249`. PLAN_ALTERNATIVES.md's characterization of this
  half of the claim is accurate.
- The 65-null / 8-template / 9-19-baseline arithmetic in `MISSION_FRAME.md` and both candidates is
  exactly reproduced by an independent fresh count of every `skills/*/templates/*.json` with
  `type in ("gated","survey")` (verified this run): ADMIRAL 10, CARTOGRAPHER 5, CHARTER 10,
  COMMANDER_SPINE 19, EXECUTE_PLAN 4, EXPLORER_SPINE 10, IMPLEMENTER_PLAN 3, SCOUT 4 = 65; CYCLE,
  INTERROGATION, REVIEW_SURVEY independently confirmed at 0 null each. No defect here.
- `decision:no-new-check-kinds` and `decision:no-basis-backfill` are both explicitly represented
  somewhere in the converged sequence (`g5`'s constraints name the `basis` temptation and refuse it
  directly). No gap found.
