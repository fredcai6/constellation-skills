BLOCK

blocking_findings: 1

# Review Result — g3-review, issue #467 (epic #418)

## Assigned Gate

`g3` — DC4: per-gate context-headroom override, tighten-only, exercised exactly once.
Diff under review: **`f9925be6`** (inspected with `git show f9925be6 -- scripts tests skills`,
never `git diff main...HEAD`).

Survey driven at `.agent-work/issue-467-trip-semantics/g3-review/review.json`
(session `g3-review-rev-01`, 18 items, consolidated `BLOCK`).
Fowler record at `.agent-work/issue-467-trip-semantics/g3-review/fowler-pass.json` (rail exit 0).

## Result

`BLOCK` — **one** blocking finding.

The mechanism itself is correct, tightly scoped, and unusually well defended. Eight of the nine
close criteria pass, and I verified the load-bearing ones by attack rather than by reading. The
single blocking finding is not a behavioural defect in shipped code: it is a **falsified evidence
claim** — the mutation log's M15 `EQUIVALENT` declaration — which leaves a genuinely unkilled
branch on a line this gate itself added. Rework is one test plus a corrected log entry, with **no
source change**.

---

## Blocking finding

### B-1 — M15 is not an equivalent mutant; the branch is genuinely unkilled

**Where:** `scripts/checklist_engine.py:2857-2858` (added by `f9925be6`), and
`.agent-work/issue-467-trip-semantics/g3-mutation-log.md` §M15. Also asserted in `f9925be6`'s
commit message: *"1 declared EQUIVALENT rather than faked (M15: `args.id == active_id` in every
reachable state)"*.

**The claim:** *"`advance` refuses any gate that is not `in-progress`, and `start` refuses to open a
gate that is not the active one, so in every reachable state the gate being advanced IS the active
gate and `args.id == active_id(cl)`."*

**Why it is false:** the reasoning enumerates `start` and `advance` but not **`block`**. `block()`
(`checklist_engine.py:2116`) carries **no status guard** — it will block an already-`complete` gate
— and `blocked` is not in `TERMINAL` (`{"complete", "skipped"}`, `:63`). So `active_id()` moves
*backwards*, behind a later gate that is already `in-progress`.

**Reproduction — public verbs only, at the CLI, against the shipped engine.** Two gates, `g2`
carries `context_headroom_tokens: 50000`; gauge on `claude-opus-5` (1M/80K/150K), so `g2`'s hard
line is 10% while the default is 15%. Context fills from 2% to 12% while `g2` is under way — the
ordinary case.

```
$ python scripts/checklist_engine.py --file m15.json start g1
g1 -> in-progress
$ python scripts/checklist_engine.py --file m15.json advance g1
g1 -> complete
$ python scripts/checklist_engine.py --file m15.json start g2
g2 -> in-progress
# ... gauge.json fill_fraction 0.02 -> 0.12 while working g2 ...
$ python scripts/checklist_engine.py --file m15.json block g1 \
      --blocker "upstream authority" --authority human --next "wait"
g1 -> blocked (bubbled to parent)

statuses: {'g1': 'blocked', 'g2': 'in-progress'}
$ python scripts/checklist_engine.py --file m15.json current
ACTIVE g1 [blocked] — do g1                     # active_id is g1; the gate being closed is g2
```

Shipped code, closing `g2` with no `--why`:

```
$ python scripts/checklist_engine.py --file m15.json advance g2
REFUSED: g2: context is at/over the hard limit, so this gate cannot be closed silently — a
mechanical or why-less close records no understanding, and the next agent would cold-start from a
digest written before your work. Closing the gate is NOT refused; only the silence is.
Run: advance g2 --why "<understanding>"
```

The M15 mutant (`require_why=_trip_hard_band_reading(cl, base_dir)`), same file, same state, same
fill:

```
$ python <mutated-engine> --file m15.json advance g2
g2 -> complete
```

**Consequence.** The `getattr(args, "id", None)` argument that `f9925be6` added at `:2857` has zero
test coverage, and removing it **silently disables the no-silent-close rule for the gate being
closed** in a state the engine sanctions. That rule is one of this issue's own shipped guarantees;
this is the g3 line that carries it to the overridden gate, so the gap is in scope for g3 (it is
*not* a claim that anything g2 shipped is wrong).

**What honest looks like here.** The declaration was transparent, not a fabrication — the log states
"NAMED test red: none, TOTAL: 0 failed" and gives falsifiable reasoning, which is exactly what let
me falsify it. But close criterion 8 asks whether it is honest *or* covering a genuinely unkilled
branch, and the answer is that the branch is genuinely unkilled.

**Rework (small, no source change):** (1) add one test that reaches the state above through public
verbs and asserts `advance g2` is refused without `--why`; confirm it goes red under the M15
mutation. (2) Replace the M15 log entry's `EQUIVALENT` declaration with the kill, and note the
correction against the commit message's claim. Optionally (3) file a separate observation that
`block()` accepts a `complete` gate — pre-existing, not this gate's to fix.

---

## Per-criterion findings

| # | Criterion | Verdict |
|---|---|---|
| 1 | Tighten-only unreachable to violate | **pass** |
| 2 | Malformed/negative test carries a positive control | **pass** |
| 3 | Neighbour isolation asserted both sides by name | **pass** |
| 4 | `_PROFILES` untouched | **pass** |
| 5 | No checklist-config tier | **pass** |
| 6 | Advisory and guard read the same resolved number | **pass** (+ NB-1) |
| 7 | Exactly one shipped gate carries an override | **pass** |
| 8 | Every logged mutation kills its named test; judge M15 | **FAIL — B-1** |
| 9 | Suite green, deltas explained | **pass** |

### 1 — Tighten-only (non-blocking: NB-2) — PASS

Attacked, not read. I swept 26 JSON-authorable values through the **real resolver** into the **real
`thresholds_for`** on `claude-opus-5`: `-10**400, -1e308, -sys.float_info.max, -sys.maxsize, -1,
-1.5, -0.0, 0, 1, 1.5, 30000, 10**400, True, False, None, nan, inf, -inf, "30000", "-30000", "1e9",
"0x10", " 30000 ", [], {}, [30000], {"v":30000}`. **Zero loosened, zero raised.**

Both layers attacked independently, which is what the criterion asks:

- Delete the resolver's negative check (M6) and `thresholds_for`'s own clamp still refuses to loosen.
- Delete `thresholds_for`'s clamp (M1) and 18 subtests go red (re-run below).

One detail worth recording as a strength: `max(0, headroom_tokens)` is in the **safe argument
order**. `max(0, nan)` returns `0`; `max(nan, 0)` would return `nan` and produce a `nan` threshold
that no fill can ever exceed. The shipped order is the correct one.

### 2 — Anti-vacuity, the central risk of this gate — PASS

I did not take M5 on report. Four-way experiment on the frozen selector
`-k malformed_or_negative`, source restored and byte-verified after each step:

```
A. shipped code, shipped test            : 1 passed, 382 deselected, 12 subtests passed
B. M5 dead-coded, shipped test           : 1 failed,  382 deselected, 12 subtests passed
C. M5 dead-coded, positive control REMOVED: 1 passed, 382 deselected, 12 subtests passed
D. shipped code,  positive control REMOVED: 1 passed, 382 deselected, 12 subtests passed
```

`C == D`. Without the positive control the test is exactly vacuous — all twelve negative assertions
stay green with the mechanism entirely dead-coded — and the control is the only thing that
discriminates (B). The implementer's M5 claim is confirmed by my own hands.

I applied the same question to criteria 1 and 3: under M5 (mechanism deleted) **all four**
neighbour/advisory/guard tests and the shipped-template test go red, so none of them is a
negative-only assertion.

### 3 — Neighbour isolation — PASS

Asserted on both sides **by name**, in the same test, at one fill (`0.12`) on one model
(`claude-opus-5`), four independent ways: the unit guard (`execute` raises, `reconcile` returns
`None`); the band decision itself; the CLI boundary through `dispatch` (`start execute` refuses and
leaves it `pending`, `start reconcile` → `in-progress`); and the strongest form — the neighbour's
advisory asserted **byte-identical** to the no-override text while the overridden gate's is asserted
*not* equal. M9 (scoping removed) kills exactly the neighbour tests.

### 4 — `_PROFILES` untouched — PASS

`_PROFILES` … `_DEFAULT_PROFILE` region extracted from `f9925be6^` and `f9925be6`: both 2231 chars,
`sha256[:16] = fefce258ae14362b`, string equality `True`. The only diff lines naming them are new
docstring prose.

### 5 — No config tier — PASS

I placed `50000` at six locations and resolved through the real resolver: checklist root → 0,
`cl["config"]` → 0, the gate's `directives` → 0, its `status_detail` → 0, its `constraints` list →
0, a sibling gate → 0. Only `tasks.<gate>.context_headroom_tokens` resolves.

### 6 — Shown vs judged (non-blocking: NB-1) — PASS with a caveat

Demonstrated, not asserted: the shipped sweep runs 5 reserves × 13 fills = 65 samples asserting
`advisory-says-hard == guard-refuses` on every one, **and** asserts the sweep crossed the line in
both directions so the equality is not vacuous. M11 and M12 kill it from opposite sides, which is
what makes it evidence.

**NB-1, non-blocking.** On the `reopen` path the two *can* differ. `_trip_advisory` always reports
the **active** gate; `_trip_hard_gate` is passed the gate being **begun**, and a `reopen` target is
by definition never the active gate. Reproduced: `execute` complete carrying reserve 50000,
`reconcile` active, fill `0.12` —

```
 active gate         : reconcile
 advisory says HARD? : False   | says SOFT? : True
 reopen-execute guard: REFUSES -> execute: context at 12% is at/over the hard limit, so this is
                                  not the moment to BEGIN work
```

The direction is fail-safe (tighter, never looser) and the refusal explains itself, so this is a
docstring overclaim plus a test gap, not a defect. `_trip_hard_band_reading`'s docstring says shown
and judged "cannot diverge"; that is true for the gate the advisory is about, not universally.

### 7 — Exactly one override, and the guess is honestly recorded — PASS

Verified repo-wide, not on the commander spine alone: parsing every `*.json` under `skills/` yields
exactly one carrier — `COMMANDER_SPINE.template.json`, gate `execute`, `30000`. Resolving all ten
spine gates through the real resolver: `init 0, context 0, understand 0, plan 0, execute 30000,
reconcile 0, triage 0, review 0, feedback 0, archive 0`. M16 kills the delete; the same test pins
the "and no other gate" half.

On `decision:execute-gate-reserve-value` (in scope: honesty and revisability only — per the handoff
I did **not** re-derive the settle experiment's un-runnability and do **not** block on the grade):
the adjacent `context_headroom_note` says *"WHY 30000, and it is a GUESS, revisable in place"*,
states the single observation it rests on **and** why that observation cannot separate the resume
baseline from the gate's marginal cost, gives the resulting band shift (15% → 12% begin-work, 8% →
5% advisory on `claude-opus-5`), and says a later run may revise the number "here, in this one
place". The shipped test asserts the string `GUESS` is present, so the label cannot be quietly
dropped. This is the honest presentation the criterion asks for.

### 8 — Mutations — FAIL (B-1)

Four re-run by me in a clean `git archive` sandbox at `f9925be6`. Sandbox baseline is
`2 failed, 431 passed, 155 subtests` — the two failures are `RepoRevision::…_git_rev_parse_head_oracle`
and `…_git_status_porcelain…`, constant artifacts of running outside a git checkout, present
identically in every run below. Subtract them and the totals match the log exactly.

```
M1  reserve = max(0, headroom_tokens) -> reserve = headroom_tokens
    18 failed, 50 passed, 30 subtests passed        (tests/test_gauge_reader.py alone)
    all 18 SUBFAILED on
      ThresholdsHeadroomOverrideTests::test_headroom_override_can_only_tighten_never_loosen
    e.g. SUBFAILED(model='claude-opus-5', reserve=-1000000000000)
    log says 18 — MATCHES

M5  `return raw` -> `return 0`   (the whole mechanism dead-coded)
    11 failed, 422 passed, 155 subtests  ->  9 real + 2 git
    RED: GateHeadroomOverrideResolverTests::test_malformed_or_negative_headroom_override_…
         GateHeadroomOverrideResolverTests::test_wellformed_headroom_override_is_read_from_its_own_gate_only
         GateHeadroomOverrideTripTests::test_headroom_override_also_governs_the_no_silent_close_rule
         GateHeadroomOverrideTripTests::test_headroom_override_changes_the_advisory_for_its_gate_only
         GateHeadroomOverrideTripTests::test_headroom_override_defaults_to_the_active_gates_reserve
         GateHeadroomOverrideTripTests::test_headroom_override_neighbour_advisory_is_byte_identical_to_no_override
         GateHeadroomOverrideTripTests::test_headroom_override_neighbour_is_unaffected_through_the_cli_boundary
         GateHeadroomOverrideTripTests::test_headroom_override_trips_its_own_gate_and_not_its_neighbour
         GateHeadroomOverrideTripTests::test_shipped_spine_template_carries_exactly_one_headroom_override
    log says 9 — MATCHES

M9  per-gate scoping removed (first task carrying the key wins)
    9 failed, 424 passed, 155 subtests  ->  7 real + 2 git
    every one a NEIGHBOUR test (the per-gate resolver test, the four
    advisory/guard/close neighbour tests, and the shipped-template test)
    log says 7 — MATCHES

M15 require_why drops the gate being CLOSED
    2 failed, 431 passed, 155 subtests  ->  0 real failures
    log says 0 — MATCHES, and the mutant survives. See B-1: it is NOT equivalent.
```

### 9 — Suite and deltas — PASS, and tc3 sharpened

Live worktree, full suite: **1832 passed, 2 skipped, 808 subtests passed** in 382.72s.
Focused selector: **20 passed, 413 deselected, 125 subtests passed** — exact match to the reported
figure.

The `+17` is attributed two independent ways.

1. **From the diff.** The test diff is purely additive: 2 hunks, **zero** deleted or modified lines,
   **17** new `def test_` methods (5 in `test_gauge_reader.py`, 12 in `test_checklist_engine.py`).
   No existing test was touched, so the passed-count delta cannot be anything but 17.
2. **From a controlled run.** I extracted the **true parent `5a69a30b`** and `f9925be6` with
   `git archive` into two clean sibling trees and ran the full suite in each under identical
   conditions:

```
parent 5a69a30b : 16 failed, 1795 passed, 10 skipped, 665 subtests passed
post   f9925be6 : 16 failed, 1812 passed, 10 skipped, 790 subtests passed
                  -> +17 passed, +125 subtests, same 16 git-oracle failures both sides
```

`+125` is exactly what the focused headroom selector reports. **This resolves tc3 rather than
tolerating it:** the diff-attributable subtest delta is a clean `+125`, so the ±1 lives in the
handoff's *stated* 683 baseline, not in the diff. Note the handoff's stated baseline commit
`d376b786` is **not** the diff's parent — it predates g1 and g2 (`d376b786..f9925be6` spans 15
commits) — which is the likeliest source of the confusion. Separately I measured **808** subtests
where the implementer measured **806** at the same commit, confirming the whole-suite subtest count
varies with tree state.

---

## Handoff compliance

All four parts of the frozen imperative shipped, and the Map Impact notes match the diff
line-by-line. (a) both caps reduced before the division, two non-negative clamps; (b) one resolver,
one source key, no config tier; (c) that resolver feeds both `:1485` and `:1542`; (d) one gate
carries an override, repo-wide. Stop conditions: none hit — the diff was accessible, evidence was
reproducible, and no policy decision was required.

## Scope drift

None. `f9925be6`'s source diff touches exactly `scripts/gauge_reader.py`,
`scripts/checklist_engine.py`, `skills/commander/templates/COMMANDER_SPINE.template.json`,
`tests/test_gauge_reader.py`, `tests/test_checklist_engine.py` — all on the allowed list. The two
pre-authorized reconciliation test files were untouched. No specific exclusion was touched:
`_PROFILES`/`_DEFAULT_PROFILE` byte-identical, no config tier, one override gate, no threshold
arithmetic in the engine (`grep` confirms `thresholds_for` has exactly two call sites, both fed by
the resolver, and no cap/window arithmetic appears in `checklist_engine.py`), and nothing g2 shipped
was reopened.

## Evidence verdict

TDD was required and the evidence shows real red→green→refactor with mutation on every guard. Three
of four mutations I re-ran reproduce exactly; the fourth (M15) is where the one blocking finding
lives. The reported command outputs reproduce in my own shell, with the subtest-count caveat above
explained rather than waved through.

## Code/doc quality

Minimal and well-shaped: 3 executable lines changed in `gauge_reader.py`, one 8-line resolver plus
two threaded arguments in `checklist_engine.py`, and a 2-line data edit in one template. Fowler pass
run over the full diff (`verify_fowler_pass.py` exit 0, `smells=12,
flagged=['duplicated-code'], overridden=['data-clumps','primitive-obsession',
'comments-as-deodorant']`). The one flagged smell is NB-4 below. Project deltas honoured: `python`
not `py`; no working-tree byte comparison.

## Map impact verdict

- **Evidence supports claimed change:** yes. Every claimed property is backed by a named test that a
  named mutation turns red, except M15's — which is B-1.
- **Constraints not violated:** yes, all three. `constraint:no-threshold-values` (two call sites,
  no arithmetic in the engine), `constraint:tighten-only` (26-value sweep, no loosening),
  `constraint:global-default-untouched` (byte-identical).
- **Notes match the diff:** yes. I checked every line number and every claim in the `Map Impact`
  section against `f9925be6`; none is missing or overstated.
- **Decision candidates surfaced:** yes. The three `settled/measured` decisions were implemented as
  given and none is contradicted. `decision:execute-gate-reserve-value` is correctly left at
  `@grade: guess`, recorded where a later run can revise it, with the replacement experiment routed
  up rather than invented locally. The implementer explicitly states it used the retracted
  role-blindness reading for nothing, and I found no trace of it in the diff or the reasoning.
- **Durable context routed:** yes — the schema-doc gap and the settle-experiment gap were both
  surfaced as observations rather than fixed silently or dropped.

## Reconciliation check

One divergence for the Commander to reconcile: `docs/CHECKLIST_SCHEMA.md` documents the Task
object's optional keys and now under-describes the schema by one key (`context_headroom_tokens`,
plus the inert `context_headroom_note`). The implementer flagged this itself and correctly declined
to edit it as out of its allowed scope. Natural home is this run's `reconcile` gate.

## Blockers

- **B-1** — the mutation log's M15 `EQUIVALENT` declaration is falsified; a genuinely unkilled
  branch remains on `checklist_engine.py:2857`. Full reproduction above.

## Out-of-scope observations

- **NB-1** — advisory/guard divergence on the `reopen` path. Fail-safe direction. Narrow
  `_trip_hard_band_reading`'s "cannot diverge" claim and add a reopen-with-a-reserve case to the
  sweep. (`tc2`)
- **NB-2** — `thresholds_for`'s docstring claims "for every input the returned pair is `<=` the
  un-overridden pair". False for non-real-number arguments: `Decimal('NaN')` raises
  `decimal.InvalidOperation`, and an object with a custom `__gt__`/`__rsub__` defeats both clamps —
  I produced `(1000.08, 1000.15)`, roughly 6600× looser than shipped. **Unreachable from any shipped
  path** (the resolver admits only non-negative plain `int`s and is the sole feeder of both call
  sites). Reword to "for every real-number input". (`tc3`)
- **NB-3** — the spine's `execute` reserve does not propagate into the child `execute.json`
  checklist, so a Commander already *inside* `execute` driving crew gates is governed by the
  default. This matches the authored intent ("may not be BEGUN with less than this much room") and
  is not a leak; recorded so a reader of the note does not assume run-wide effect.
- **NB-4** (Fowler, `duplicated-code`) — `thresholds_for(model, _gate_headroom_tokens(cl, gate))` is
  written out at `:1485` and `:1542`. One private `_thresholds_for_gate(cl, model, gate)` would make
  "shown == judged" structural rather than conventional, and would delete M11/M12's failure mode
  entirely. (`tc4`)
- **NB-5** — `block()` accepts an already-`complete` gate with no status guard, which is what makes
  B-1's state reachable. Pre-existing, not introduced by this diff, and not g3's to fix.
- **NB-6** — my reviewer skill's bundled engine is **not** byte-identical to the repo engine
  (`sha256[:16]`: bundled `e997cd2a3e6e766a`, repo HEAD `23aa9c552ae2a3d0`, pre-g3
  `4b9e6c82723f1431`), contrary to the handoff's note. It does support `amend`. I drove my survey
  with the bundled copy and verified all g3 behaviour against the **repo** copy, so nothing in this
  review rests on the bundled one.
- **tc5** — the tc3 subtest item, updated with the `+125` measurement above. Suite-hygiene, not a
  gate blocker.

## Workflow Feedback

- **Handoff gaps:** criterion 9 names the pre-change baseline as `d376b786`, but that commit is
  **not** the diff's parent — `d376b786..f9925be6` spans 15 commits including all of g1 and g2. Any
  reviewer comparing against it gets `+39 passed`, not `+17`, and would either chase a phantom or
  accept a number it could not reproduce. The true parent is `5a69a30b`. This is very likely also
  the whole origin of the "±1 subtest" mystery that has now cost two agents time: against the true
  parent the delta is a clean `+125`. **Name the parent commit, not a run-start commit, whenever a
  criterion asks for a suite delta.**
- **Context rediscovered:** the survey template's `r6-fowler` postcondition placeholder. The handoff
  warns about a previous reviewer force-waiving it, which was useful — but the fix is one sentence
  the *template* already contains and the handoff paraphrases at length: resolve
  `<fowler-pass-record-path>` at instantiation time, exactly like `<work-id>`. Doing that meant no
  `amend` and no waiver were needed at all. A handoff line reading "substitute the Fowler path when
  you instantiate, before you claim" would be shorter and would remove the failure mode entirely.
- **Instructions improvised around:** two. (1) "Do not modify anything under `scripts/` or `tests/`"
  is in direct tension with "re-run at least two of the mutations yourself" — mutation testing *is*
  modifying `scripts/`. I resolved it by extracting `git archive` snapshots of `5a69a30b` and
  `f9925be6` into temp trees and mutating only those, which left the worktree untouched and gave me
  a controlled parent baseline for free. Worth making the sanctioned method explicit in the handoff
  rather than leaving each reviewer to invent it. (2) Those extracted trees have no `.git`, so 16
  tests that shell out to git fail identically on both sides; I report totals net of that constant
  rather than pretending to a clean run.
- **What would have made this easier:** one concrete change — have the implementer record the parent
  commit and the *paired* baseline/post numbers measured in the same conditions, rather than a
  baseline number inherited from an earlier handoff. Every reproduction problem in this gate traces
  back to that one field.

## Return status

`blocked`
