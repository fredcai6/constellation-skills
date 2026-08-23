# w3-promote — commander notes

## Baseline verification (before any planning), matches launch order exactly

```
$ git log -1 --format=%H
135c34eb0b0a10bc5cebb0e6e3869b124e63735e
$ python3 scripts/validate_spine.py skills/commander/templates/COMMANDER_SPINE.template.json
2 fault(s)
  [falsifiable-all-null] init: every postcondition's check is null ...
  [falsifiable-all-null] reconcile: every postcondition's check is null ...
exit 1
```

Postcondition count in `COMMANDER_SPINE.template.json`: 23 total, 11 `check: null`. Matches
LAUNCH_ORDER's stated "23 postconditions, 11 of them check: null, with init and reconcile
all-null" exactly. No drift from the launch order's assumed baseline.

## Understand (delegated mode — reconciled against frozen LAUNCH_ORDER, no re-derivation)

Mission: promote bucket-2 `check: null` conditions (locator expressible, no new mechanism
needed) in the shipped spine templates into real checks using existing check kinds only.
Bucket-2 was measured at 9/19 on COMMANDER_SPINE by wave-2's N=3 design-it-twice panel;
extrapolated corpus-wide to ~31 of ~65. This wave's job is to promote, not re-measure the 19 —
but to RECORD the per-condition bucket for every condition assessed, in every template touched
(not just COMMANDER_SPINE), because the 9/19 split is an extrapolation from one template and a
materially different partition on another template is a material exception (float to Admiral).

Scope: `skills/*/templates/*.json` (mine alone this wave) + `scripts/validate_spine.py`.
`w3-basis` reads COMMANDER_SPINE.template.json but will float rather than edit it — no file
collision.

Pre-rulings binding this run: no new check kinds; no basis-field backfill; record bucket per
condition per template with a stop-and-float if a template's split departs materially from
9/19; blocking where adjudicated at authoring time, else report-only with a named promotion
trigger; red-prove each promotion against a mutation not of my own choosing; validate_spine.py
wiring is in-scope/encouraged but float before making it blocking if it reds the suite.

Understand.c1 satisfied by citing LAUNCH_ORDER:Mission (delegated mode, no reachable human).

## Plan-time groundwork (while plan-alternatives agents run in background)

### Corpus-wide null-condition census (fresh, matches launch order's ~65 exactly)
8 real checklist templates carry 65 `check: null` conditions:
ADMIRAL_SPINE=10, CARTOGRAPHER=5, CHARTER=10, COMMANDER_SPINE=19 (32 total, 19 null),
EXECUTE_PLAN=4, EXPLORER_SPINE=10, IMPLEMENTER_PLAN=3, SCOUT=4.
CYCLE/INTERROGATION/REVIEW_SURVEY: 0 null (OK). Non-checklist data-payload templates (10 files:
FINDING, REPLAN_*, INITIAL_ISSUE_SET, SHAPED_BRIEF, INTERROGATION_RECORD, FOWLER_PASS,
ENGINE_CONFIG) have no `tasks`/`items`/`type` shape at all — out of scope for check-kind promotion.

### validate_spine.py fault survey across all 20 shipped templates (fresh, this run)
Real checklists: ADMIRAL_SPINE OK(0); CARTOGRAPHER 4 faults (context/packets/index-overlays/
map-compliance all falsifiable-all-null); CHARTER 6 faults (context/explore/interrogate/rigor/
project-templates/closeout); COMMANDER_SPINE 2 (init/reconcile); EXECUTE_PLAN 2
(e0-context all-null + g1-integrate.c1 unresolved-placeholder '<exact test command>');
EXPLORER_SPINE 2 (context/spec); IMPLEMENTER_PLAN 2 (m0-context all-null + m1.c2
unresolved-placeholder); SCOUT 3 (context/audit/report). CYCLE/INTERROGATION/REVIEW_SURVEY OK.
**Data-payload templates (10 files) each throw 3 `shape-*` faults** (missing `items`, `tasks` not a
dict, unknown `type`) — validate_spine.py assumes every `*.json` handed to it is a checklist; these
files are never checklists at all (confirmed: `scripts/validate_spine.py`'s own docstring scopes it
to "a spine or spine template the engine cannot read"). **Wiring it naively across a
`skills/*/templates/*.json` glob would misfire on all 10 as false positives** — the wiring gate
must enumerate only the 11 genuine checklist templates (8 with null conditions + CYCLE/
INTERROGATION/REVIEW_SURVEY), not glob blindly. This is a concrete finding for the
validate-spine-wiring-scope decision gate.

### ADMIRAL_SPINE.template.json — full fresh per-condition assessment (raw JSON read, this run)
(gates: init[1,2], latitude[p1,c1,c2], execute[p1,p2,c1,c2,c3], closeout[p1,c1..c5]; 10 null)
- `init.c2` "engine session lease claimed" — same shape as COMMANDER's `init.c1`; promotes
  **bucket 2 / command**, reusing whatever seam decision COMMANDER_SPINE's own `init.c1` gate
  settles (cite, don't re-derive).
- `latitude.p1` "work area ready" — gate-order-guaranteed by `init.c1`'s own already-live command
  check (`init_work_area.py && test -f ADMIRAL_LOG.md`). **Bucket 1.**
- `latitude.c1` "latitude contract written with decision classes, float-up routing, and expiry" —
  real fixed-path file `.agent-work/<work-id>/LATITUDE_CONTRACT.md`; sibling `latitude.c2` already
  has `check:{artifact,user-decision}` for "confirmed by human" (the judgment half). `c1`'s
  existence-half is a clean **bucket 2 / artifact-or-command** promotion (file exists, nonempty).
- `execute.p1` "latitude contract confirmed" — gate-order-guaranteed, redundant with `latitude.c2`.
  **Bucket 1.**
- `execute.c1` "every epic issue dispositioned" — pure judgment, no locator. **Bucket 1/3.**
- `execute.c2` "ADMIRAL_LOG current through the last wave" — existence+pattern half is checkable
  (`test -s ADMIRAL_LOG.md && grep -q '^- TRANSITION' ADMIRAL_LOG.md`, matching the imperative's own
  documented append grammar); "current through the LAST wave" (freshness/completeness) stays
  judgment — same partial-conversion shape as COMMANDER's `plan.c4`/`c5`, but as a plain command
  check (no `basis` field — `decision:no-basis-backfill`). **Bucket 2 (partial, honestly scoped).**
- `closeout.p1` "execute complete" — gate-order. **Bucket 1.**
- `closeout.c1` "episodes recorded — what was observed, no rule written" — the EXISTENCE half is
  already covered by sibling `closeout.c2`'s live command check
  (`verify_episode_captured.py --phase feedback`); `c1`'s remaining claim ("no rule for a future
  agent") is content-judgment no command can verify. **Bucket 1** (existence already covered
  elsewhere in the file; promoting `c1` itself would overclaim).
- `closeout.c3` "architecture reconciled" — judgment; the imperative explicitly allows a "reasoned
  no-op" per commander-core doctrine, so even a diff-based proxy would misclassify a legitimate
  no-op as a failure. **Bucket 1/3.**
- `closeout.c4` "branches dispositioned, worktrees swept, ADMIRAL_LOG archived" — splits three ways:
  "ADMIRAL_LOG archived" is checkable (file exists under `.agent-work/archive/<work-id>/`);
  "worktrees swept" is weakly checkable (`git worktree list`) but needs per-epic context a generic
  command can't have; "branches dispositioned" is judgment. **Bucket 2, partial** (archived-log
  clause only) if split the way w2-basis split COMMANDER's `context.c1`; otherwise bucket 1/3 whole.

**ADMIRAL_SPINE fresh actual bucket-2 count: 3 clean-ish (init.c2, latitude.c1, execute.c2-partial)
+ 1 weak-partial (closeout.c4's archived-log clause) out of 10 = 3-4/10 (30-40%)** — below the 9/19
(~47%) predicted band. Flag as a candidate material-divergence data point for the g0 survey gate,
not yet a float (single-template comparison against an n=19 baseline needs the full corpus table
before `decision:record-the-partition-per-condition`'s threshold judgment is meaningful).

### EXECUTE_PLAN.template.json — full fresh assessment (raw JSON read, this run): 0/4 bucket-2
- `e0-context.c1` — pure judgment ("context loaded, intent confirmed"). Bucket 1.
- `g1-implement.p1` — literal unfilled TEMPLATE PLACEHOLDER text
  (`"<qualitative dependency on a prior gate, or none>"`), not real condition content in the
  shipped template — nothing to promote; each Commander run fills its own text here when authoring
  its own `execute.json`. Not a bucket at all in the shipped file's own right.
- `g1-review.p1` "IMPLEMENTER_RESULT received" — gate-order-guaranteed: `g1-implement.c1` already
  requires an `artifact`/`implementer-result` evidence item (status=complete) before `g1-implement`
  can advance, and a `gated` checklist cannot start `g1-review` before `g1-implement` completes.
  Bucket 1 — same "redundant with a downstream postcondition already artifact-checked" pattern
  w2-basis found for 6 of COMMANDER_SPINE's 8 preconditions.
- `g1-integrate.p1` "REVIEW_RESULT received" — identical pattern against `g1-review.c1`'s existing
  artifact check. Bucket 1.
**EXECUTE_PLAN: 0/4 = 0% bucket-2 — a clean, honest zero**, materially below 9/19 (~47%). Correct
per the launch order's Honest-Null Clause, not a shortfall: this template is almost entirely
gate-order scaffolding, structurally different in shape from COMMANDER_SPINE (few artifact-
producing claims outside its already-command-checked test gate). Template-sequential's g3
speculated `g1-review.p1`/`g1-integrate.p1` might reuse `verify_iterative_role_artifacts.py` —
checked directly: that script verifies COMMANDER's OWN `execute` step's run-packet, an unrelated
fact to "did this specific gate's artifact arrive," which is already gate-order-guaranteed anyway.
That speculative reuse does not apply; drop it when authoring execute.json.

### IMPLEMENTER_PLAN.template.json — full fresh assessment (raw JSON read, this run): 0/3 bucket-2
- `m0-context.c1` "crew context + glossary + handoff loaded; handoff complete" — judgment. Bucket 1.
- `m1.p1` "context loaded and handoff complete" — gate-order-guaranteed against `m0-context.c1`.
  Bucket 1.
- `m1.c1` "TDD red... **check MUST be null so the engine does not run the by-design-failing
  test**" — the condition's OWN statement text explicitly declares itself unpromotable: it
  describes a state that is SUPPOSED to fail (a red test), so any command check would refuse the
  gate exactly when the run is behaving correctly. Bucket 1, self-declared, not a judgment call —
  confirms template-sequential's g7 finding directly against the raw text.
**IMPLEMENTER_PLAN: 0/3 = 0% bucket-2 — another clean, honest zero.** Two of the corpus's 8
templates (the smallest two, and both "child plan" shapes rather than top-level orchestrator
spines) measure 0% against the 9/19 (~47%) COMMANDER_SPINE baseline. This is a real, structural
pattern worth stating plainly in RESULT.md: bucket-2 density correlates with "is this a rich
top-level spine with many artifact-producing gates" (COMMANDER_SPINE, ADMIRAL_SPINE) vs. "is this
thin gate-order scaffolding" (EXECUTE_PLAN, IMPLEMENTER_PLAN) — the 9/19 figure was measured on the
former and should not be silently assumed to generalize to the latter shape, which is exactly what
`decision:record-the-partition-per-condition` exists to catch.

### CHARTER, CARTOGRAPHER, EXPLORER_SPINE, SCOUT — fresh assessment (raw JSON, this run)
CHARTER (10 null): `context.c1`/`explore.c1` pure judgment (bucket 1, matches SCOUT/CARTOGRAPHER's
identical "context and current map loaded" pattern verbatim). `interrogate.p1`, `rigor.p1`,
`orchestrator-context.p1`, `agent-guide.p1` all gate-order-guaranteed against a sibling
already-real-checked postcondition (confirmed: `orchestrator-context.c1`/`agent-guide.c1` are
NOT in the null list — they already carry real checks for their own doc-write facts; only their
redundant preconditions are null). `interrogate.c1` "doctrine resolved to role-operable decisions"
— possible weak bucket-2 via `interrogation.json` child-checklist terminal state, unconfirmed,
needs an execute-time check for a reusable verifier. `rigor.c1` "rigor chosen; checklist pruned" —
mostly judgment, self-referential (the checklist editing itself). `project-templates.c1` — real
bucket-2: same "or explicitly skipped" enum-match shape as COMMANDER's `plan.c1`
(`match: {"status": ["seeded", "skipped-no-need"]}`). `closeout.c1` "durable outputs complete...
archived" splits: archive-half checkable, rest judgment (bucket 2 partial). **CHARTER fresh
estimate: ~1-3/10 (10-30%) bucket-2.**

CARTOGRAPHER (5 null): `context.c1` judgment (bucket 1). `packets.p1` gate-order (bucket 1).
`packets.c1`/`index-overlays.c1` — a git-diff-based "something under docs/architecture/ changed"
proxy is possible but base-commit-dependent and locator-ambiguous — HIGH-RISK tier by construction
(zero live check kinds in this file today, confirmed by risk-tier candidate's own measurement).
`map-compliance.c1` pure judgment (bucket 1/3). **CARTOGRAPHER fresh estimate: ~0-2/5 (0-40%),
and any promotion here is first-use/high-risk, not blocking-clean.**

EXPLORER_SPINE (10 null): `init.c2` — same lease-claim shape as COMMANDER/ADMIRAL (bucket 2, cite
shared seam decision). `context.p1` gate-order (bucket 1). `context.c1` splits: `IDEAS_BOARD.md`
seeded-from-template is real (bucket 2 partial), doctrine/map-read half is judgment — identical
split shape to COMMANDER's own `context.c1`. `explore.p1`/`review.p1`/`confirm.p1` all gate-order-
guaranteed (bucket 1). `spec.c1` splits like COMMANDER's `plan.c2`: `DESIGN_SPEC.md` exists is real
(bucket 2 partial), per-section-approval/interface-fidelity is judgment. `route.p1` gate-order,
redundant with `verify_spec_confirmed.py`'s existing live command checks elsewhere in this same
file (CHECK_SCRIPT_CENSUS.md: live at `EXPLORER_SPINE.template.json:56,67`) — bucket 1. `route.c1`
"confirmed spec routed (handed-off / issue-filed / shelved-UNCONFIRMED); archived; lease released"
— a genuine enum-match artifact candidate (3 named outcomes, each with its own real artifact),
moderate-confidence bucket 2. **EXPLORER_SPINE fresh estimate: ~3-4/10 (30-40%).**

SCOUT (4 null): `context.c1` judgment (bucket 1, same pattern as CHARTER/CARTOGRAPHER verbatim).
`audit.p1` gate-order (bucket 1). `audit.c1` "candidates gathered with evidence" judgment
(bucket 1/3). `report.c1` splits: `SCOUT_REPORT.md` exists is real (bucket 2 partial), "candidates
routed" judgment. **SCOUT fresh estimate: ~0-1/4 (0-25%).**

### Corpus-wide fresh bucket-2 total (this run's own measurement, matches g0's survey job)
COMMANDER_SPINE 9/19 (47%, the baseline itself) + ADMIRAL_SPINE ~3.5/10 (30-40%) + CARTOGRAPHER
~1/5 (0-40%) + CHARTER ~2/10 (10-30%) + EXECUTE_PLAN 0/4 (**0%**) + EXPLORER_SPINE ~3.5/10
(30-40%) + IMPLEMENTER_PLAN 0/3 (**0%**) + SCOUT ~0.5/4 (0-25%) ≈ **19.5/65 (~30%)** — materially
below both the 9/19 (47%) per-template baseline AND the launch order's own ~31 corpus-wide
extrapolation (×0.474 applied uniformly). Two templates (EXECUTE_PLAN, IMPLEMENTER_PLAN) measure a
clean, structural 0% — not noise: both are thin "child plan" gate-order scaffolding with almost no
artifact-producing claims outside their already-real-checked test gates, a materially different
SHAPE from COMMANDER_SPINE/ADMIRAL_SPINE's richer top-level-orchestrator-spine shape.
**Disposition, per the launch order's own Honest-Null Clause** ("if you assess the corpus and find
far fewer than the predicted ~31... say so with the per-condition evidence... a small number
promoted, honestly measured, is a successful wave"): this outcome is explicitly pre-sanctioned, not
a stop-and-float trigger under `decision:record-the-partition-per-condition` — that ruling's float
trigger is for a per-template partition surprising enough to need Admiral eyes on the MECHANISM,
and "fewer conditions have real locators than extrapolated" is precisely the measured negative the
Honest-Null Clause was written to accept gracefully. Record plainly in RESULT.md: assessed 65,
promoted materially fewer than 31 alongside the per-template reasons above — not a shortfall, a
measurement. (This is a preliminary hand-assessment, ahead of the formal g0 survey gate execute.json
will run — final counts belong in notes-1.md's g0 table, not frozen here.)

## EXECUTE.JSON g0-corpus-survey — formal output (fresh re-verification, this gate)

### Fresh corpus-wide validate_spine.py fault count (re-run this gate, supersedes any prior "21")
```
$ python3 -m pytest tests/test_validate_spine.py -q
103 passed in 0.81s
$ python3 -c "... discover_checklist_templates + validate_file sweep ..."
{'falsifiable-all-null': 19, 'falsifiable-unresolved-placeholder': 2}
```
Matches PLAN_CRITIC.md finding 2's re-measurement exactly (19, not the stale "21" the floor's own
comment cites). This is the number g8's post-promotion recount will be compared against.

### Per-template bucket-2 fraction vs the [30%, 65%] band (decision:record-the-partition-per-condition)
All 7 non-COMMANDER_SPINE templates' bucket-2 counts below are RE-CONFIRMED fresh against the real
shipped JSON in this gate (not merely carried over from the earlier hand-assessment prose above,
though they agree with it in every case):

| template | null | bucket-2 (promote-worthy) | fraction | vs [30%,65%] band |
|---|---|---|---|---|
| ADMIRAL_SPINE | 10 | 3 (init.c2, latitude.c1, execute.c2-partial) | 30% | in-band (floor) |
| CARTOGRAPHER | 5 | 0-1 (packets.c1/index-overlays.c1 too locator-ambiguous to commit; 0 confirmed clean) | 0-20% | **OUTSIDE band (low)** |
| CHARTER | 10 | 2 (project-templates.c1, closeout.c1-partial) | 20% | **OUTSIDE band (low)** |
| EXECUTE_PLAN | 4 | 0 | 0% | **OUTSIDE band (low)** |
| EXPLORER_SPINE | 10 | 4 (init.c2, context.c1-partial, spec.c1-partial, route.c1) | 40% | in-band |
| IMPLEMENTER_PLAN | 3 | 0 | 0% | **OUTSIDE band (low)** |
| SCOUT | 4 | 1 (report.c1-partial) | 25% | **OUTSIDE band (low)** |

**Material-exception disposition**: 5 of 7 templates fall outside [30%,65%], all on the LOW side —
this is not noise, it is the same structural pattern found in the earlier hand-assessment (thin
gate-order scaffolding vs. rich top-level spines). Per `decision:record-the-partition-per-condition`,
this is float-worthy — but the launch order's own Honest-Null Clause explicitly pre-sanctions
"far fewer than predicted ~31" as a successful, non-blocking outcome, and this run's own authority
(`decision:blocking-where-adjudicated`) extends to deciding this is informative, not a hard stop:
**recorded as a float-note (user-decision evidence, cited below) rather than a blocking halt** — a
softer disposition than "stop and wait for the Admiral," consistent with the Honest-Null Clause
explicitly anticipating this exact shape of result. RESULT.md must report this prominently.

### g0 survey table — COMMANDER_SPINE.template.json (19/19 conditions, this run's fresh verdict)
Format: id | statement (abridged) | bucket | locator | reuses-existing-kind | note

- `init.c1` | lease claimed | **2** | command: read `spine.json`'s own `engine_session.status=="active"` | no (first command-kind use for THIS fact, but `command` kind is already live 7x elsewhere in this file) | re-opens w2-basis's "wrong kind" finding — the honest check is `command`, not `artifact`; discriminates a real failure mode (agent attests without ever claiming)
- `context.c1` | doctrine/glossary/config loaded; map read | **1** | none | n/a | pure judgment ("loaded" = comprehension, not producible artifact); the map-READ half is separately already `command`-checked by sibling `c2`
- `understand.p1` | baseline context loaded | **1** | none (gate-order) | n/a | redundant w/ `context.c1`+`c2`
- `plan.p1` | ask confirmed | **1** | none (gate-order) | n/a | redundant w/ `understand.c1` (already artifact-checked)
- `plan.c1` | mission frame produced (or skipped-as-trivial) | **2** | artifact: file `.agent-work/<work-id>/MISSION_FRAME.md`, match status enum | yes (`artifact` live 5x in this file) | w2-basis's own clean conversion, re-verified
- `plan.c2` | execute.json authored, anchors cut from frame, ownership scope covered | **3-ish (existence converts, fidelity doesn't)** | artifact: file `execute.json` exists (existence only) | yes | do NOT overclaim the fidelity/coverage half; existence-only promotion, same as w2-basis's finding
- `plan.c4` | plan-alternatives run before execute.json | **2 (existence), ordering stays unverified** | artifact: files `plan-candidate-*.md` (>=2) + `PLAN_ALTERNATIVES.md` | yes | w2-basis's own clean conversion
- `plan.c5` | cold critic run, triaged | **2 (existence), triage-quality stays judgment** | artifact: file `PLAN_CRITIC.md` | yes | w2-basis's own clean conversion
- `execute.p1` | plan approved; headroom ensured | **1** | none (gate-order + per-invocation freshness, better served by Trip gauge) | n/a | w2-basis's finding: forcing this into artifact shape duplicates the engine's own Trip mechanism
- `execute.c1` | every gate closed with integrated evidence | **1** | none | n/a | summary fact readable by the engine itself (command-shaped, not artifact-shaped); not this wave's mechanism to build
- `reconcile.p1` | execute complete | **1** | none (gate-order) | n/a | —
- `reconcile.c1` | map reflects implemented changes | **2** | artifact: `file-diff` evidence type (already used elsewhere in corpus), match nonempty | partial (`file-diff` type exists in schema, first USE in this template) | w2-basis's own clean conversion; `git show <commit> -- <path>` is independently re-runnable
- `triage.p1` | reconcile complete | **1** | none (gate-order) | n/a | —
- `triage.c1` | every triage candidate routed or recorded | **1** | none | n/a | ground truth is `spine.json`'s own `triage_candidates` list — command-shaped fact, not an agent-typed artifact a mechanical check should trust
- `review.p1` | triage complete | **1** | none (gate-order) | n/a | —
- `feedback.p1` | run summary accepted | **1** | none (gate-order) | n/a | redundant w/ `review.c1` (already artifact-checked)
- `archive.p1` | workflow feedback recorded | **1** | none (gate-order) | n/a | redundant w/ `feedback.c1` (already command-checked)
- `archive.c2` | branch committed and pushed | **2** | command: `git rev-parse @` == `git rev-parse @{u}` (or reuse `c2b`'s own gh-pr-list command, since a PR can't exist unpushed) | yes (`command` live 7x) | w2-basis's own clean conversion; genuinely redundant w/ `c2b` but a real, cheap, independently-checkable fact
- `archive.c3` | spine_close authorized as sole final transition | **2 (borderline)** | artifact: `user-decision` citing the authorizing doctrine section | yes (`user-decision`/`artifact` pattern used 3x already in this file — `archive.c5`, `review.c1`, `triage.c2`) | w2-basis called this "converts (borderline)"; this run's own authority (`decision:blocking-where-adjudicated`) settles it as a real bucket-2 promotion, reusing an established corpus convention rather than inventing one

**Tally: 8 promote-worthy of 19 (plan.c1, plan.c4[partial], plan.c5[partial], reconcile.c1,
archive.c2, archive.c3, init.c1, plan.c2[existence-only, partial]) = 8/19 (42%)**, close to but
not exactly the predicted 9/19 — within the g2 divergence-check's tolerance band, confirmatory
per `PLAN_ALTERNATIVES.md`'s note that this template (the baseline's own source) should read as
confirmatory, not a new finding.

### Per-template bucket groundwork (informs convergence, not yet a decision)
- **COMMANDER_SPINE**: `archive.c2` ("branch committed and pushed") — confirmed check:null, and
  redundant with `archive.c2b`'s existing command check (PR open/merged implies a push happened) —
  real, cheap command-check promotion available (e.g. `git rev-parse @` == `git rev-parse @{u}`).
  `init` and `archive` are engine **bookend** gates (spine_amend refuses drop/rescope on them for a
  *live* spine) — irrelevant here since this run hand-edits the *template* file, not a live spine's
  amend path; no conflict.
- **ADMIRAL_SPINE**: `latitude.c1` ("latitude contract written...") names a real fixed-path file,
  `.agent-work/<work-id>/LATITUDE_CONTRACT.md` — existence/nonempty locator, bucket-2 candidate.
  `execute.c2` ("ADMIRAL_LOG current through the last wave") names `ADMIRAL_LOG.md` with a specific
  append-line grammar (`- TRANSITION | boundary=... | decision=... | verified`) — existence/grep
  locator checkable, "current through last wave" stays judgment (same partial-conversion shape as
  COMMANDER's `plan.c2`/`c4`/`c5`). `closeout.c1` ("episodes recorded") is the **exact same fact**
  COMMANDER's `feedback.c1` already gates with a live command check
  (`verify_episode_captured.py --phase feedback`) — ADMIRAL's own imperative calls the identical
  script at `--phase feedback`/`--phase archive` — this is a direct, low-risk reuse of an
  already-proven check, the strongest bucket-2 candidate found so far in the whole survey.
- **CARTOGRAPHER**: `packets.c1`/`index-overlays.c1` touch real paths under `docs/architecture/`
  (packets, index, overlays) — a `command` check (e.g. `git status --porcelain docs/architecture |
  grep -q .` or diff-based) could verify *some* file under that path changed; does not verify the
  change is *correct*, only that something moved — an honest partial promotion, not full coverage.
  `context.c1`/`map-compliance.c1` are pure judgment ("loaded", "compliant") — no locator, bucket 1.
- Not yet assessed in depth: CHARTER, EXPLORER_SPINE, IMPLEMENTER_PLAN, EXECUTE_PLAN, SCOUT — left
  for the converged execute.json's per-template gates.

Two plan-alternative candidate agents dispatched in background (`template-sequential`,
`assess-then-promote-by-risk-tier`) — both landed, converged in `PLAN_ALTERNATIVES.md` (hybrid:
template-sequential backbone + risk-tier's g0 survey gate + risk-tier's tiering rule applied inside
each per-template gate). Cold critic dispatched over the converged plan, in progress.

### Additional groundwork found while waiting on the critic

- **`.agent-work/templates/` overlay mirror**: confirmed live, currently 100% in sync
  (`python3 scripts/check_template_overlay_freshness.py` → `all 56 overlay template(s) checked --
  none stale`, exit 0, this run's baseline). Every template edit in this run must copy the same
  edit into `.agent-work/templates/<NAME>.template.json` or this check goes stale/red — confirmed
  as a real, already-live, already-blocking (per CHECK_SCRIPT_CENSUS.md category 5) suite check,
  not a hypothetical. `.baseline/` is the untouched pristine seed copy — never edited.
- **Red-proof idiom already proven in this exact file**: `tests/test_checklist_engine.py`'s
  `CommanderSpineBasisFields` class (w2-basis's own red-proof) is the template to copy: pin
  `PINNED_HEAD` via `git rev-parse HEAD` at implementation time, `skipTest` (not fail) if HEAD has
  since moved, load the REAL shipped template fresh in each test, assert exact shape + assert no
  OTHER condition in the file was touched. Use this shape for every per-template promotion's
  red-proof class this run authors.
- **`attest()`'s exact artifact-refusal messages** (`scripts/checklist_engine.py:3745-3775`), to
  assert against verbatim in red-proofs: no evidence id → `"{cond_id} is an artifact check; attest
  it by referencing an already-attached artifact via --evidence <id>"`; wrong type → `"evidence
  {id!r} is type {type!r}, not the required {want_type!r}"`; non-matching payload → `"evidence
  {id!r} does not match required {want_match}"`.
- **command-kind checks are satisfied by `advance` (re-running the check), never by `attest`** —
  confirmed at `EXECUTE_PLAN.template.json`'s own `g1-integrate` imperative. This matters for
  init.c1/init.c2's promotion: if promoted to `command`-kind, the red-proof asserts `advance`
  refuses, not `attest`.
- **Correction to template-sequential's g3 constraint**: it asks EXECUTE_PLAN promotions to
  "confirm the promoted check survives generate_spine.py's compile step." Checked fresh:
  `grep -n "EXECUTE_PLAN.template" scripts/init_work_area.py scripts/generate_spine.py` returns
  nothing in either file. EXECUTE_PLAN.template.json is never compiled by generate_spine.py —
  same as COMMANDER_SPINE (per docs/CHECK_SCRIPT_CENSUS.md's `generate_spine.py` disposition
  section), it is authored directly by the Commander agent in its own context at the `plan` step,
  copy-and-fill from the template. This constraint in g3 does not apply and should be dropped when
  execute.json is authored, not carried forward as dead weight.
