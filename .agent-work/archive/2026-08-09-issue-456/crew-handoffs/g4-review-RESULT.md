# Review Result

## Assigned Gate
`g4` — the top index must ROUTE, not list. Issue #456.

## Result
`APPROVE-WITH-FINDINGS`

(Engine-recorded survey verdict is `APPROVE` — the workbench consolidation guard is binary
pass/APPROVE unless a check fails; the finding below is real but non-blocking, so
`APPROVE-WITH-FINDINGS` is the accurate label for the Commander-facing three-way verdict this
gate's handoff asks for.)

## Corpus-shape finding — lead item

The Commander's mandate: only `f1Brainz` genuinely exercised critic F9's trap (~75% of a real
repo's entities are test code); `superCoolSpaceSim` was an admitted null test (0 `.py` files).
My job was to find or synthesize a third, genuinely different shape and run the tier against it.

**The third shape was already in hand, unexamined.** This repo's own real, freshly built
`map/INDEX.md` shows the `tests` package — 50 modules / 2769 entities, **74.3%** of the
corpus's 3728 entities, the *same proportion F9 named* — is completely **flat** (every module
is `tests.test_foo`, two dotted segments). The tier predicate `len(m.split("."))>=3` never
fires for a single one of its 50 modules, so `## tests` renders as 50 undifferentiated bullets
with **zero** subheadings (`map/INDEX.md` lines 89–140) — exactly the flat-list problem this
gate exists to fix, unaddressed, in the single largest bucket. The crew's own
`g4_tier_shape.md` measured tier-1 sizes for this repo but never looked at tier-2 behavior on
it — this is why it went unseen.

I also built two **synthetic** shapes to isolate the mechanism
(`.agent-work/issue-456/evidence/g4_reviewer_synth_corpora.{py,txt}`, scratch temp dirs only):

- **Shape A — flat single package** (30 modules, zero nesting; this is what `tests/` above
  *is*, isolated). Tier 2 provides zero benefit — 31 loose bullets, 0 `###` headings.
- **Shape B — loose top-level modules, no packages at all** (named explicitly in the handoff).
  **Tier 1 itself degenerates**: `BY_PKG` keys on `m.split(".")[0]`, so every module becomes
  its own "package" — a 30-line, one-package-per-module list. This falsifies `top_index`'s own
  docstring claim that tier 1 is "bounded by how many top-level packages the corpus has, never
  by how many modules." The crew's evidence doc claims "none is 'N buckets of one'" but only
  checked the 0-module null case; Shape B is the actual N-buckets-of-one case and the claim
  does not hold for it.

**Verdict on the shapes: both real, not pathological** — Shape A is the default pytest layout
(and this repo's own `tests/`); Shape B is any small script-bag repo with no package structure.

**Does this route or degenerate?** Both — routes genuinely for corpora/packages with real
nesting (this repo's `evals`, partially `scripts`; f1Brainz's `src/`), degenerates to a no-op
for a flat/loose shape. Not a blocker: the tier stays derived, not tuned (honest "nothing to
group" report, not fabricated structure), and no close criterion promises uniform routing.
Filed as a triage candidate (tc1) — the docstring's tier-1 bound claim should be corrected, and
a later gate should consider a secondary grouping signal for flat dominant packages.

## Handoff compliance
All "Also verify" items independently attacked, not taken on trust:

- **tc31 attacked with relocations the implementer never chose**
  (`g4_reviewer_tc31_attack.{py,txt}`): (1) a **module** page moved cross-module
  (`scripts.code_map.discovery/INDEX.md` → `scripts.code_map.cli/`), (2) an **entity** page
  moved into a **subdirectory of its own correct module**. Both isolate
  `page-location-matches-content` as the sole failing check, both name the exact offending
  page, all other 6 checks stay green. tc31 is genuinely closed, not vacuous.
- **Threshold re-grep**: confirmed independently from the diff's own added lines — exactly one
  new numeric comparison in the whole diff, `len(m.split("."))>=3`. No slice/sort-truncate/count
  threshold anywhere else in the tier path.
- **Non-falsifier label**: `test_top_index_lists_a_loose_module_directly_with_no_subheading` —
  confirmed trivially true pre-gate (old `top_index` never emitted `###` at all) and confirmed,
  by tracing `module_group_key`/`subpkgs` by hand against the fixture, that it *would* catch a
  real regression (grouping widened to swallow loose modules). Correctly labeled a regression
  guard, not a falsifier, and not a check-that-cannot-fail.

## Scope drift
None. `git diff --name-only 0e63f208..HEAD` (my own run): exactly `scripts/code_map/checks.py`,
`scripts/code_map/render.py`, `tests/test_code_map.py`, plus workbench artifacts under
`.agent-work/`. `checks.py` is a narrow, handoff-predicted exception (tc31 ownership), same
class as g3's. All named exclusions re-verified directly: `_make_collision_repo`'s INDEX
collision still fires (non-vacuous test body confirmed); `OWN_MODULE_NAMED_MUTATION` /
`test_refs_lines_are_self_consistent_on_an_intact_map` green; `entity_symbol_join`'s two
derivations untouched by this diff; zero `:<line>` across all 3840 built pages.

## Evidence verdict
Every claimed number independently reproduced: full suite **1772 passed, 2 skipped, 672
subtests, 0 failed** (310.98s, my own backgrounded run — exact match); gate selector **5
passed, 75 deselected** (exact match); fresh build **111 modules / 3728 entities / 3840 pages**
(exact match); fresh `check` **7/7** including `page-location-matches-content`. New evidence
this review contributes beyond the RESULT doc: the tc31 attack and the corpus-shape synthesis
above.

## Code/doc quality
Fowler pass: 12/12 baseline smells rendered, all **absent** for this diff (rail exit 0,
`.agent-work/issue-456/g4-review/fowler-pass.json`) — `_module_line` extraction actually
*removes* a would-be duplication; every new function takes one parameter; `top_index`'s 57
lines (incl. docstring) match this file's own `module_index` baseline (58 lines), not an
outlier.

## Map impact verdict
- **Evidence supports claimed change:** yes, for the corpora/sections it was measured on.
- **Constraints not violated:** yes — stdlib only (zero new imports in the diff), no timings in
  reports, page register pure ASCII with no `:<line>`.
- **Notes match the diff:** mostly — the "two-tier routing surface" capability claim overstates
  generality; see the corpus-shape finding. Filed as tc1, not a blocker.
- **Decision candidates surfaced:** yes — tier granularity and tc31's closure route are both
  argued with a rejected alternative on record.
- **Durable context routed:** yes — tc1 filed via `flag-candidate --from r5-reconciliation`.

## Reconciliation check
No `docs/architecture/` exists in this repo to reconcile against — the map itself is the
architecture record this issue is building. No unreconciled divergence.

## Blockers
- none

## Out-of-scope observations
- tc1 (this review): the routing/two-tier claim does not hold uniformly across corpus shapes —
  correct `top_index`'s docstring tier-1 bound claim (false for a loose-top-level corpus) and
  consider a secondary grouping signal for flat dominant packages in a later gate.
- Carried forward from the implementer, not re-litigated: filename-within-directory not checked
  by tc31's check; `tests.unit` still 92% of its package after tier-2 grouping on f1Brainz;
  `gate-spec.json` vs. the handoff reconciliation.

## Workflow Feedback

- **Handoff gaps:** none material. The handoff's framing ("if you find one, say whether
  real-world or pathological — that distinction is the finding, not a technicality") correctly
  anticipated exactly this outcome and told me how to report it rather than forcing a
  block/no-block binary I'd have had to invent.
- **Context rediscovered:** the crew's own real-corpus evidence (`g4_tier_shape.md`) reported
  tier-1 sizes for constellation-skills but never rendered tier-2 for it — the gap that let the
  `tests/` degeneracy go unnoticed was an omission in what was *measured*, not a hidden fact;
  the built `map/INDEX.md` was sitting right there. Worth a standing reviewer habit: when a
  crew's own dogfood corpus is available, read the ACTUAL generated artifact before reaching for
  a new one.
- **Instructions improvised around:** none — pre-filled the Fowler-pass postcondition's real
  record path directly into the survey JSON at creation time (rather than instantiating the raw
  template with its `<fowler-pass-record-path>` placeholder), which avoided the amend/attest
  dead-end g0–g3's reviewers each hit and reported. Worth promoting into the template itself: the
  placeholder should be filled by the survey's own creation step, not left for `record` to trip
  over.
- **What would have made this easier:** nothing further.

## Return status
`complete`
