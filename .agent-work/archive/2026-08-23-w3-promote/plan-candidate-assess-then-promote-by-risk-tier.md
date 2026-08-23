# Candidate: assess-then-promote-by-risk-tier

**Constraint (assigned):** decouple measurement from mutation. Assess and record the bucket
(1/2/3) for every `check: null` condition across all 8 templates in ONE consolidated pass —
comparing each template's split against the predicted 9/19 (~47%) ratio and flagging material
divergence — before any template file is edited. Then partition the bucket-2 promotion set by
**risk tier**, not by template, and gate promotion + red-proofs by tier.

Cites, not re-derives: the launch order's three-bucket partition and its N=3 provenance
(`LAUNCH_ORDER-w3-promote.md`), `decision:record-the-partition-per-condition`,
`decision:blocking-where-adjudicated`, `decision:no-new-check-kinds`, and w2-basis's own
per-condition table for `COMMANDER_SPINE.template.json`
(`.agent-work/archive/2026-08-22-w2-basis/plan-candidate-artifact-conversion.md` — 5 clean:
`plan.c1`, `plan.c4`, `plan.c5`, `reconcile.c1`, `archive.c2`).

## 0. Measured inputs this plan is grounded in

Fresh count, this run, per template (`tasks[*].preconditions|postconditions[*] where check is
null`):

| template | null conditions | predicted bucket-2 (×0.474) | live check kinds already in the template |
|---|---|---|---|
| `COMMANDER_SPINE.template.json` | 19 | 9 | `command`(7), `artifact`(5), `git-change-policy`(1) |
| `ADMIRAL_SPINE.template.json` | 10 | 5 | `command`(4), `artifact`(2) |
| `CARTOGRAPHER.template.json` | 5 | 2 | **none — zero live checks of any kind** |
| `CHARTER.template.json` | 10 | 5 | `artifact`(6) |
| `EXECUTE_PLAN.template.json` | 4 | 2 | `artifact`(3), `command`(1) |
| `EXPLORER_SPINE.template.json` | 10 | 5 | `command`(5), `artifact`(3) |
| `IMPLEMENTER_PLAN.template.json` | 3 | 1 | `command`(1) |
| `SCOUT.template.json` | 4 | 2 | **none — zero live checks of any kind** |

`python3 scripts/validate_spine.py <each>` faults, measured fresh: COMMANDER_SPINE 2,
ADMIRAL_SPINE 0, CARTOGRAPHER 4, CHARTER 6, EXECUTE_PLAN 2 (incl. one
`falsifiable-unresolved-placeholder` on `g1-integrate.c1`'s `<exact test command>`),
EXPLORER_SPINE 2, IMPLEMENTER_PLAN 2 (incl. one placeholder fault on `m1.c2`), SCOUT 3 —
**21 faults total across the corpus, 0 files clean except `ADMIRAL_SPINE`.**

`CARTOGRAPHER` and `SCOUT` carry a structural fact the risk-tiering in this plan depends on:
they have **no live check kind at all** — every existing postcondition is `check: null`. Any
bucket-2 promotion in either file is, by definition, a first use of whatever kind it picks,
regardless of how clean the locator is.

## 1. Gate sequence (Commander `execute.json` shape)

```
g1-consolidated-assessment
  imperative: |
    Before touching any template file, walk all 65 check:null conditions across the 8 templates
    (COMMANDER_SPINE, ADMIRAL_SPINE, CARTOGRAPHER, CHARTER, EXECUTE_PLAN, EXPLORER_SPINE,
    IMPLEMENTER_PLAN, SCOUT — MISSION_FRAME.md's Structural Anchors) and assign each one bucket
    (1 = no locator; 2 = locator expressible, no new mechanism; 3 = artifact exists but the claim
    is a judgement, basis territory, out of scope per decision:no-basis-backfill). Reuse
    w2-basis's measured 19-condition table for COMMANDER_SPINE as a cited starting point, but
    re-verify each verdict fresh at this run's HEAD and record where this run's own authority
    (decision:blocking-where-adjudicated, which w2-basis lacked) agrees or diverges — e.g.
    w2-basis's "converts (borderline)" archive.c3 call on a weak citation-only locator gets an
    explicit bucket-2-or-3 answer here. The other 46 conditions (7 templates) are first-pass, not
    re-verification. Produce ONE table, not eight, in .agent-work/w3-promote/notes-1.md: template,
    condition id, statement (abridged), bucket, locator, reuses-existing-kind (yes/no/n-a), note.
    Compute each template's actual bucket-2 fraction against the 9/19 (~47%) predicted ratio.
  close criteria:
    - all 65 conditions carry a recorded bucket with a one-line reason
    - every bucket-2 row carries a real, named locator (file path or re-runnable command); a
      bucket-2 row with no locator is a contradiction and must be re-decided
    - per-template actual-vs-predicted bucket-2 fraction stated explicitly
    - CARTOGRAPHER/SCOUT's zero-live-check-kind fact carried as a table column, feeding g3
  required evidence: file-diff (notes-1.md consolidated table), command-output (fresh
    validate_spine.py run against all 8 templates, per decision:validate-spine-wiring-is-
    in-scope's "count faults across all shipped templates first")
  constraints: no template file under skills/*/templates/*.json is edited in this gate — read-only
    measurement, full stop; any promotion urge is g4/g5's job, not g1's
```

```
g2-divergence-check
  imperative: |
    Compare g1's per-template actual bucket-2 fraction against the 9/19 (~47%) prediction.
    decision:record-the-partition-per-condition makes a materially different partition a stop-
    and-float, not a silently absorbed variance. Apply a stated threshold (e.g. outside
    [30%, 65%] — wide enough to tolerate ordinary variance, narrow enough to catch a
    structurally different template; CARTOGRAPHER's 5 mostly-"is the map compliant" conditions
    with no live-check precedent are the first candidate to check). Any template that trips the
    threshold gets its float-up note written now, before g3 partitions anything.
  close criteria: every template's divergence status (within-band / material-exception) recorded;
    any material exception has a float-up note, not a silent fold into g3
  required evidence: file-diff (notes-1.md divergence table), user-decision (only if a material
    exception needs an Admiral answer before continuing)
  constraints: arithmetic/judgement on g1's table only, no new template inspection; resolve
    routing here, do not re-open g1
```

```
g3-risk-tier-partition
  imperative: |
    Split g1's bucket-2 set (post g2) into two tiers, not by template: LOW-RISK = the chosen check
    kind is already live elsewhere in that SAME template's non-null conditions (e.g. COMMANDER_
    SPINE's plan.c1/plan.c4/plan.c5/reconcile.c1/archive.c2 all promote to "artifact", already
    live there on understand.c1, plan.c3, triage.c2, review.c1, archive.c5). HIGH-RISK = either
    (a) first use of that kind anywhere in the template (true by construction for every bucket-2
    candidate in CARTOGRAPHER.template.json and SCOUT.template.json — g1 recorded zero live kinds
    in either file), or (b) the locator is ambiguous (multiple candidates could satisfy the match,
    or "close enough" requires judgement — e.g. a free-form doc section vs a fixed path or a
    stable-exit-code command). Record tier + specific reason per bucket-2 condition in notes-1.md.
  close criteria: every bucket-2 condition carries exactly one tier and a named reason; the two
    tier lists are disjoint and union to g1's full bucket-2 set
  required evidence: file-diff (notes-1.md tier table)
  constraints: tiering evaluates each condition against ITS OWN template's live-kind set, never
    the corpus-wide set — artifact being live in COMMANDER_SPINE doesn't make a CARTOGRAPHER
    artifact promotion low-risk, since CARTOGRAPHER has never run that kind
```

```
g4-promote-low-risk-blocking
  imperative: |
    For every low-risk-tier condition, hand-edit its template surgically (compact-format JSON,
    raw text, never json.load/json.dump — re-validate with json.load after) to replace
    `"check": null` with the real check object, using the tier's already-live kind and g1's
    locator. Ship BLOCKING per decision:blocking-where-adjudicated: reusing a kind the template
    already runs live is not a new refusal surface — the same argument w2-basis made for
    COMMANDER_SPINE's 5 (attest's artifact branch, unchanged code, already blocking on 5 siblings
    in the same file) — and this wave has the authority to ratify it that w2-basis lacked. Sync
    the .agent-work/templates/ overlay + .baseline copies for every file touched.
  close criteria: every low-risk condition's check.kind populated with evidence_type/match (or
    command/match); no high-risk or bucket-1/3 condition touched; all files remain valid JSON;
    overlays in sync
  required evidence: file-diff (each edited template + overlay), command-output (JSON
    parse-validate on every touched file)
  constraints: hand-edit only; touch nothing outside g3's low-risk list; commit granularity is
    author's latitude, but the diff must be checkable line-by-line against g3's tier table
```

```
g5-promote-high-risk-report-only
  imperative: |
    Promote every high-risk-tier condition from g3 too — do not leave it null just because it is
    riskier, that would shrink the honest-null population into a different shape than g1 measured.
    Ship REPORT-ONLY per decision:blocking-where-adjudicated, naming the promotion trigger in the
    SAME commit/PR: e.g. a CARTOGRAPHER first-use-of-artifact promotion's trigger is "N clean
    report-only runs through this gate with zero false-refusals, reviewed at the next
    Cartographer-owning wave." A report-only condition with no named trigger is the launch order's
    own named defect (an unmeasured signal shipped silently) — do not ship one without it.
  close criteria: every high-risk condition promoted with a report-only flag/marker per the
    schema's existing mechanism (command/git-change-policy kinds only — if a high-risk condition's
    kind is artifact and no report-only shape exists for it, per w2-basis §5, it is DEMOTED back
    to check: null with the reason recorded, not force-shipped blocking); every shipped condition
    names its trigger in the commit message and notes-1.md
  required evidence: file-diff (edited templates + overlays), user-decision (the trigger is a
    decision surfaced, not unilaterally set)
  constraints: no engine change to add a report-only artifact mechanism — a blocked artifact-kind
    condition demotes to null-and-documented, not an excuse to invent engine code
```

```
g6-red-proof-by-tier
  imperative: |
    Red-proof every g4/g5 promotion against the shipped revision per decision:red-proof-each-
    promotion, using an attacker-chosen mutation, not a self-designed falsifier — pin the
    template's git blob OID so the test cannot silently pass against a future edit. Run low-risk
    and high-risk proofs as two labeled groups (same or sibling pytest module) so a reviewer sees
    tier-by-tier which promotions are proven, matching g3's partition rather than a
    template-by-template listing.
  close criteria: every g4/g5 condition has a red-proof test that (a) fails pre-promotion, (b)
    passes post-promotion, (c) fails again under an independently-chosen mutation (missing
    evidence, wrong type, non-matching payload); full tests/test_checklist_engine.py green
  required evidence: command-output (pytest, full file, green)
  constraints: no engine code change — a red-proof needing one means the promotion's premise is
    wrong; revert to check: null with the reason recorded, don't patch around it
```

```
g7-validate-spine-wiring-decision
  imperative: |
    With g1's full-corpus fault count in hand (21, section 0 above, now reduced by whichever
    falsifiable-all-null faults g4/g5 resolved — a gate whose only null condition got promoted no
    longer trips it; a gate with several nulls where only one promoted still trips), decide with
    the Admiral whether wiring validate_spine.py at the shipped templates lands blocking this
    wave, per decision:validate-spine-wiring-is-in-scope. If wiring still reds the suite on faults
    this wave didn't fix (e.g. the two falsifiable-unresolved-placeholder faults on
    EXECUTE_PLAN's g1-integrate.c1 and IMPLEMENTER_PLAN's m1.c2 — template-authoring bugs, a
    different defect class than check:null), float that split rather than suppress or silently
    expand scope.
  close criteria: explicit decision recorded — wire blocking now / wire report-only / defer with a
    named owner — plus, if deferred, a triage entry for the placeholder faults specifically
  required evidence: user-decision, command-output (validate_spine.py re-run against all 8
    templates post-g4/g5, faults recounted)
```

```
g8-reconcile-docs-and-map
  imperative: |
    Update docs/CHECK_SCRIPT_CENSUS.md's grep-derived counts (and any cited in
    docs/CHECKLIST_SCHEMA.md) to the post-g4/g5 figures, dated to this run. Update
    GoldenOutputBriefing fixtures in tests/test_checklist_engine.py for every changed render line
    (null -> kind name) across all touched templates, not just COMMANDER_SPINE. State whether the
    map/INDEX.md pre-commit hook fired (map is already DEGRADED-UNPARSEABLE repo-wide per
    MISSION_FRAME.md — this gate reports, does not repair).
  close criteria: doc counts match a fresh re-run grep/count; GoldenOutputBriefing green with
    fixtures updated for every changed line; map hook status stated
  required evidence: command-output (fresh grep/counts, full pytest suite)
```

```
g9-integrate
  imperative: |
    Commit (split by tier or template at the author's latitude, but the PR description must
    reproduce g1's consolidated table and g3's tier split), run the full suite, open the PR
    server-side-merge per launch order defaults. Do not merge.
  close criteria: PR open, full python3 -m pytest -q green, RESULT.md written per the launch
    order's Return Shape including per-template assessed-vs-promoted counts (Honest-Null Clause:
    report promoted alongside assessed)
  required evidence: command-output (full suite, post-commit), file-diff (PR link)
```

## 2. Tradeoffs

- **Depth:** measurement is uniformly deep (all 65 conditions, one table, nothing sampled) before
  any promotion — depth front-loaded into g1, not re-earned per template. Promotion depth then
  varies deliberately by tier: low-risk gets full blocking depth (g4), high-risk gets shallower
  report-only depth with an explicit deepening trigger (g5) — depth allocated by measured risk,
  not by editing order.
- **Locality:** the worst axis relative to a per-template plan. g4 and g5 each touch conditions
  scattered across up to 8 files in one gate, since the partition key is risk tier, not file. A
  reviewer checking "did CARTOGRAPHER's promotions land correctly" must filter g4/g5's diff by
  file rather than read one gate as one file — the direct, non-free cost of the assigned
  constraint.
- **Seam placement:** the seam is the risk boundary itself (kind-already-live-in-this-template vs
  kind-first-use-in-this-template) — a genuinely new seam this candidate adds; neither the launch
  order's bucket partition nor w2-basis's table names it. It is grounded in a measured fact
  (CARTOGRAPHER and SCOUT have zero live check kinds today; COMMANDER_SPINE has three), not
  invented, but it sits on top of the inherited partition and the Admiral should know that before
  ratifying it.
- **Testability:** strong and tier-labeled (g6 groups red-proofs by tier), but it exposes a real
  gap for CARTOGRAPHER/SCOUT: every bucket-2 condition there is high-risk by construction, so this
  plan may ship ZERO blocking promotions in either file this wave — report-only-strength proofs
  only, materially weaker than COMMANDER_SPINE's outcome, and that gap should be named in
  RESULT.md rather than averaged into one corpus-wide count.

## 3. Verdict

This constraint does exactly what it was assigned to do: it stops the corpus-wide extrapolation
(9/19 ≈ 47%) from being spent silently, since g1 forces every template's actual ratio onto one
table before a single file changes, and g2 makes divergence a stop condition rather than a
rounding error. A "one gate per template, sequential" alternative would instead discover
CARTOGRAPHER's zero-live-check-kind fact only at CARTOGRAPHER's turn, several gates in, with
COMMANDER_SPINE's promotions already merged and the risk framing anchored to the corpus's easiest
case. This candidate is worse at locality and at giving a reviewer one clean per-template diff —
the sequential alternative reads more naturally gate-equals-file, and a reviewer trusting one
template's promotions cannot partially trust g4/g5 without reading the tier table first. Pick this
constraint when the live worry is "did we quietly assume 47% generalizes"
(decision:record-the-partition-per-condition's point); pick sequential when the worry is "can a
reviewer approve template-by-template without holding the whole corpus in their head."
