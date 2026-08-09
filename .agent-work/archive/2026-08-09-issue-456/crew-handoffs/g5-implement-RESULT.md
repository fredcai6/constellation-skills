# Implementation Result

## Assigned gate
`g5`: unused and untested must stop looking identical

## Completed slice
Split the page's `referenced by:` line into two independently-attributed
lines — `referenced by (production): ...` and `referenced by (tests): ...`
— so a reader can tell unused / test-only / production-used apart on the
page itself. Added `is_test_module(mod)`, derived from pytest's documented
default discovery convention (`test_*.py` / `*_test.py` naming, or a `tests`
package anywhere on the module's dotted path), independently duplicated by
hand in `checks.py` (never imported from `render.py`). A test-defined
entity's own page additionally carries `TEST_NOTE`, so its near-universal
`none found` / `none found` reads as the expected state rather than a
dead-code alarm. `SPLIT_LEGEND` states the classification basis on every
page that carries a split. Also closed `tc32`: a new falsifier proves caller
ordering is stable under a permuted statement-visit order, shown red (via a
deleted `sorted(...)`) before green.

## Scope
**Files changed:**
- `scripts/code_map/render.py` — `is_test_module`, `_bucket_line`, rewritten
  `refs_line`, new constants `REFS_PROD_PREFIX`/`REFS_TEST_PREFIX`/
  `TEST_NOTE`/`SPLIT_LEGEND`/`REFS_NONE`.
- `scripts/code_map/checks.py` — independent second copies of the same
  constants and `is_test_module`; rewritten `refs_line_self_consistent` and
  `inbound_attribution` for the two-bucket grammar; `refs_prefix_of` helper.
- `tests/test_code_map.py` — new `ProductionTestCallerSplitTests` (6 tests),
  new `CallerOrderStableUnderPermutedVisitTests` (2 tests, tc32), plus
  fixtures `_make_prod_test_split_repo` and `_make_multi_caller_repo`;
  retargeted 3 pre-existing mutation anchors (`OWN_MODULE_NAMED_MUTATION`,
  `LEGEND_DROPPED_MUTATION`; `OWN_SITES_UNACCOUNTED_MUTATION` needed no
  change) and 3 assertion sites that hardcoded the old single-line grammar.
- `.agent-work/issue-456/evidence/measure_split.py` — the three-way split
  evidence script (new).

**Specific exclusions touched:** yes, by necessity, all confirmed still
green — `_make_collision_repo`'s cross-platform `INDEX` collision still
collides (`CaseOnlyPageIdentityTests`); `OWN_MODULE_NAMED_MUTATION`'s anchor
was retargeted to the new source (`ext = sorted(m for m in counter if m !=
mod)`) and still kills the mutant; `test_refs_lines_are_self_consistent_on_
an_intact_map`'s input precondition still holds; `entity_symbol_join`'s two
independent derivations are untouched; page headers still carry `path, N
lines` with no `:<line>`; `page_location_matches_content` still ok on both
corpora. Verified together in one selector run (32 passed) plus the full
suite and both `check` runs below.

## Behavior changed
Yes. Every entity page's inbound section is now two labeled lines instead
of one, plus a `SPLIT_LEGEND` line always and a `TEST_NOTE` line on
test-defined entities. `checks.py`'s `refs_line_self_consistent` and
`inbound_attribution` are correspondingly stronger (2-line shape, bucket
arithmetic, note consistency).

## Map Impact
- **Structural anchors touched:** `scripts/code_map/render.py` (`refs_line`,
  new `is_test_module`/`_bucket_line`), `scripts/code_map/checks.py`
  (`refs_line_self_consistent`, `inbound_attribution`, new `is_test_module`).
- **Capabilities added/changed/affected:** entity pages now distinguish
  "unused" / "test-only" / "production-used" without a second page open —
  this gate's whole point.
- **Constraints/assumptions touched:** the classification predicate is a
  NEW assumption — pytest's default `python_files` glob plus a `tests`
  package layout — stated on the page (`SPLIT_LEGEND`) and known to degrade
  (classify as production) on a corpus following neither convention.
  Confirmed concretely on f1Brainz: its `run_tests.py` module correctly
  falls to production because it matches neither rule.
- **Decision candidates / resolved decisions:** the split is by CALLER
  MODULE classification only, never by an absolute count threshold (critic
  F4, honored).
- **Claims/evidence produced:** three-way split measured on two corpora of
  different shape (below); tc32 falsifier proven red-before-green.
- **Trust limitations / drift found:** none found beyond the stated
  predicate blind spot.
- **Triage candidates:** none surfaced beyond what the handoff already
  named.

## Test mode
**Required:** port-defective-then-fix / red-before-green
**Satisfied:** yes. `ProductionTestCallerSplitTests` (6 tests) observed
failing against the pre-change grammar, then passing after the render.py +
checks.py rewrite. `CallerOrderStableUnderPermutedVisitTests`'s falsifier
graded **A** (reproduces on real input): the mutant (deleted `sorted(...)`)
survives on a fixture with only 1 external caller module and is KILLED once
the fixture is widened to 2 — recorded in the test's own docstring/comments
so the cardinality requirement is not lost; the committed test uses the
2-caller fixture, i.e. the falsifier that actually bites.

## Evidence

```bash
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k 'refs or caller' -q --color=no
```
RED (before): 6 new `ProductionTestCallerSplitTests` failures against the
old single-line grammar; 11 pre-existing passed. GREEN (after all changes):
**19 passed**.

```bash
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/ -q --color=no
```
**Result:** 1780 passed, 2 skipped, 672 subtests passed, exit 0 (entering
this gate: 1772 passed, 2 skipped, 672 subtests — the +8 delta is exactly
the new `ProductionTestCallerSplitTests` (6) + `CallerOrderStableUnder
PermutedVisitTests` (2)).

```bash
python -m scripts.code_map build && python -m scripts.code_map check
```
**Result:** build and check both exit 0. `check`: **7/7 checks pass**
(`no-empty-pages`, `page-accounting`, `refs-line-self-consistent`,
`entity-symbol-join`, `page-location-matches-content`, `inbound-attribution`,
`deterministic-rebuild`, all `ok`). Report: modules=111, entities=3752,
pages=3864 (grown from the entering baseline 3728/3840 because the new test
code I added is itself part of the mapped corpus).

**Three-way split, THIS REPO** (`measure_split.py --out map`, of 3752
entity pages — the baseline's 3728 plus the 24 new test entities my own
change added):
- unused: **2428 (64.7%)**
- test-only: **451 (12.0%)**
- production: **873 (23.3%)**

**Three-way split, f1Brainz** (`C:/Programs/f1Brainz`, READ-ONLY, built into
scratch — `python -m scripts.code_map build/check --root C:/Programs/
f1Brainz --artifacts <scratch>/.code-map --out <scratch>/map`, never
touching the f1Brainz working tree). Shape: 1227 modules / 15037 entities,
a top-level `tests` package of 548 `.py` files AND a separate top-level
`run_tests.py` module — genuinely different from this repo's shape.
`check`: **7/7 exit 0**, including `inbound-attribution` and
`refs-line-self-consistent` on the real 15037-entity tree. Split (of
15037):
- unused: **8485 (56.4%)**
- test-only: **1498 (10.0%)**
- production: **5054 (33.6%)**

`run_tests.py` classifies **production** (last dotted segment `run_tests`
matches neither `test_*` nor `*_test`, and its top-level package segment is
not `tests`) — the concrete case the predicate is expected to degrade
honestly on, confirmed rather than assumed.

**Predicate basis, stated:** pytest's documented default `python_files`
glob (`test_*.py`, `*_test.py`) plus the `tests` package layout pytest's own
docs recommend — never this repo's own directory conventions. **What
defeats it:** a corpus whose tests follow neither naming nor a `tests`
package (e.g. a bare `spec/` directory, or files named without the `test`
token) — every such caller classifies as production, which under-counts the
test-only bucket and over-counts production. That degradation is stated on
every page via `SPLIT_LEGEND`, not hidden.

**tc32, red before green** (`CallerOrderStableUnderPermutedVisitTests`):
```bash
unset FORCE_COLOR PYTHONIOENCODING && python -m pytest tests/test_code_map.py -k CallerOrderStableUnderPermutedVisitTests -q --color=no
```
2 passed: `test_caller_lists_are_byte_identical_under_a_permuted_visit_order`
(canonical vs a reversed-file-block-order render — byte-identical page
trees) and `test_falsifier_bites_when_the_caller_order_sort_is_deleted`
(same two builds through a mutated `render.py` with the ordering
`sorted(...)` deleted — non-empty `tree_diff`, confirming the falsifier
actually distinguishes visit-order-dependent rendering). During
development the mutant initially SURVIVED against `_make_cross_module_repo`
(only 1 external caller module — a one-element list orders the same with
or without a sort); the committed test uses a wider `_make_multi_caller_
repo` fixture (2 external callers) precisely so the falsifier bites — this
is recorded in-file, not just here.

## Docs/contracts touched
- none — the change is confined to the map's own generated-page grammar and
  its checks; no external doc references the old single-line format.

## Assumptions
- The production/test predicate treats a `tests` package anywhere on a
  module's dotted path (not only top-level) as a test layout — a slightly
  more permissive reading of "the conventional tests package" than
  top-level-only, to also cover a nested `pkg/tests/` subpackage. Not
  exercised by either corpus's actual shape (both are top-level), so it is
  a design choice, not something the evidence here validates either way.

## Stop conditions hit
- One HARD context trip (governed reach-up, not a stall) at the very start
  of the run, before any code was written — filed a `refresh-request` and
  used the one unblocked `advance` to capture the full design in the
  engine's `why_trail`, then reported to Commander and went idle per
  `global-everyone.md`'s reach-up doctrine. Commander resumed the SAME
  session in place rather than relaunching a fresh agent; the digest turned
  out to have been enough to resume directly from `m1` without re-reading
  the source tree. A second, much longer gap occurred around the full-suite
  re-run at `m4` (~6 minutes per run, run twice — once for the gate
  selector's own record, once again as `advance`'s own command check) plus
  the f1Brainz build/check (1227 modules); both were genuinely running, not
  stalled, but the file-based polling I used to watch them landed on empty
  buffered output repeatedly and cost real wall-clock time before I let the
  background-task completion notification (rather than manual file
  polling) do its job.

## Out-of-scope observations
- none found — everything encountered was within this gate's scope.

## Workflow Feedback

- **Handoff gaps:** none — the handoff's grammar section (checks.py
  independence, exact anchors to update) matched the actual source closely
  enough that no field was missing or wrong.
- **Context rediscovered:** the refresh-request `why_ref` identity rule
  (`has_pending_refresh_request` keys on the CURRENT latest why-record,
  and **every** `advance` — mechanical or not — mints a new why-record,
  moving that target) is not stated plainly anywhere I read before hitting
  it live. I initially attached a refresh-request with a stale `why_ref`
  four times in a row before realizing each prior `advance` had already
  moved the latest why-record past the id I was citing. The correct
  sequence — read the current latest `why_trail` id, THEN attach the
  refresh-request citing exactly that id, THEN advance — should be spelled
  out in `checklist-engine.md`'s refresh section rather than left to be
  reverse-engineered from refusal messages.
- **Instructions improvised around:** the plan's `command` postconditions
  for `m2`/`m3` ran the full gate selector via the engine's own POSIX-shell
  command execution, which is fine, but the SAME `advance` for `m4`
  re-ran the FULL suite (`pytest tests/`, ~6 minutes) as its command check,
  on top of having already run it manually moments before to gather the
  numbers for the `--why` text. I did not find a way to satisfy a command
  postcondition by reference to evidence already gathered (the way
  `attest --evidence` works for artifact postconditions) — a `command`
  postcondition always re-runs. Not wrong, just doubled a genuinely slow
  command; noting it in case a future gate wants to budget for that.
- **What would have made this easier:** a one-line note in
  `checklist-engine.md`'s refresh section: "re-read `why_trail`'s last id
  immediately before attaching a refresh-request; a prior `advance` —
  including a `--mechanical` one — always moves it."

## Return status
`complete`
