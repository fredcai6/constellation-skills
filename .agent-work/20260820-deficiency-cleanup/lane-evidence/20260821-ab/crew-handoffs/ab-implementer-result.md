# Implementation Result

## Assigned gate
Wave 3 batch A+B implementer dispatch — eight bounded changes across
`scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`, `scripts/run_crew.py`.

## Completed slice
All eight items (A1–A6, B1–B2) implemented, tested, and committed in two
logical units. Plan `.agent-work/20260821-ab/IMPLEMENTER_PLAN.json` driven
to `DONE` through the bundled checklist engine (no spine bound in this
process's environment; per the implementer skill's fallback path, and per
the handoff's explicit "do not call any `mcp__spine__*` tool" instruction).

## Scope
**Files changed:**
- `scripts/checklist_engine.py`
- `scripts/hooks/spine_rail.py`
- `scripts/run_crew.py`
- `tests/test_checklist_engine.py`
- `tests/test_spine_rail.py`
- `tests/test_mcp_door_unbound.py`, `tests/test_mcp_identity.py`,
  `tests/test_mcp_spine_bind.py`, `tests/test_mcp_spine_server.py`
- `tests/test_crew_launcher.py`, `tests/test_crew_delivery_addressing.py`,
  `tests/test_crew_worktree_cwd.py`, `tests/test_work_id_nesting.py`

**Specific exclusions touched:** no. `skills/charter/*`,
`skills/_shared/global-everyone.md`, `tests/data/store_mentions.approved.txt`,
`map/`, `docs/architecture` all untouched (verified: `git status --short`
shows no matches).

## Behavior changed
Yes — per item below.

### A1 — remove `"current"` from `RAIL_VERBS`
`scripts/checklist_engine.py:468`. `RAIL_VERBS` shrank from six to five
verbs: `{"claim", "start", "advance", "attest", "attach"}`. `_RAIL_STRINGS`
is byte-identical to base (verified: only the *set membership* changed, no
string edited). `current`'s CLI output no longer carries a `RAIL: ...` block
at all. Updated the pinned `test_rail_verbs_set_is_exact` and rewrote
`RailPositionOrdering.test_current_rail_banner_is_first_suffix_ordering_after_body_unchanged`
(renamed `test_current_carries_no_rail_banner`, now asserts the ABSENCE of
the banner rather than its position).

### A2 — archive banner and rail suppression
New `_is_archived_path(base_dir)` helper (a lexical fact about the caller's
`--file` path — two consecutive `.agent-work`/`archive` path components,
no `resolve()`, no cwd read) and `_ARCHIVED_BANNER` constant. Wired into
`dispatch()`'s existing rail chokepoint: when the path is archived, the
rail is suppressed for **every** railed verb (not just `current`) and the
banner is prepended for every verb dispatched against that plan. 5 new
tests in `ArchivedPathBannerAndRailSuppression`.

### A3 — `HELD`, not `active`; render age, never a verdict
`_lease_line` rewritten: renders `LEASE HELD: <id> (by <who>, last
heartbeat <age> ago)` instead of `LEASE active: <id> (by <who>, heartbeat
<raw-ISO-timestamp>)`. Age computed via the pre-existing `_format_age`
helper (no new formatting logic). No verdict word (STALE/LIVE) appears
anywhere — an absent/unparseable heartbeat renders `unknown`, never a
guessed age. The stored `engine_session.status` field is never rewritten,
only the render. 8 test call sites across `test_checklist_engine.py` and
the four MCP door integration test files updated to the new string shape
(none asserted the exact literal text before, except one, which I fixed).

### A4 — `next (for the holder):`
`state()` gained a `lease_held` boolean field (`_active_lease(cl) is not
None`); `render_human()` relabels `next:` to `next (for the holder):`
whenever a lease is held — true for the owner and a non-owner alike, since
`current` takes no caller identity to compare against, so no new argument
was needed. 3 new tests in `NextForTheHolder`.

### A5 — staleness in `_scan_active_spine`
`scripts/hooks/spine_rail.py`. New `_lease_is_stale(lease, now_text=None)`
(mirrors `checklist_engine._is_stale`'s threshold and fail-toward-stale
rule locally — this hook is stdlib-only by contract and cannot import the
engine) and `_LEASE_STALE_SECONDS = 1800`. `_scan_active_spine`'s match
loop now skips stale leases. The owned-binding resume path (a session
resuming its OWN prior claim) is deliberately left ungated — an owner is
never blocked by its own staleness, the same rule `require_session` uses
on the write path. Fixed `make_spine`'s test fixture: its default
`last_heartbeat` was a fixed constant ~40 days in the past (accidentally
stale relative to real time), which would have broken every
staleness-blind existing test once the gate went live; changed the default
to a fresh per-call timestamp with an optional override, and fixed one
test (`test_a_parents_restart_does_not_take_the_crews_gate_away_from_the_crew`)
that asserts byte-identical output across two calls of the same helper —
it now passes one fixed heartbeat explicitly to both. 6 new focused tests.

### A6 — rewrite `require_session`'s refusal text
The active-non-stale-session refusal (`:1148-1152` in the handoff's line
numbering) no longer hands out either filed-defect remedy unconditionally.
Both remedies (`--session-id <holder's>`, `claim --force --reason`) are
kept — passing the holder's own id back IS the correct, required move for
a relaunched run resuming itself — but each is now stated WITH the
condition that makes it correct (only if you truly are that run; only if
you know it is gone), plus the honest third option: leave the plan alone.
No test asserted the old exact text, so nothing broke; 1 new focused test
added.

### B1 — exempt `waive` from the session gate
`require_session`'s early return became `if verb not in MUTATING_VERBS or
verb == "waive": return`. `waive` stays in `MUTATING_VERBS`, so `main()`'s
journaling branch (which reads that same set) still fires. Proved: (1) a
cross-session waive succeeds while a different session holds the lease,
(2) the waiver is journaled with the correct verb/session/task, (3)
`"waive" in E.MUTATING_VERBS` still holds, (4) every OTHER mutating verb is
still session-gated. Ran the 4 existing `PreToolUse` self-waive denial
tests in `test_crew_launcher.py` **unmodified** — all 4 pass, confirming
the actual self-waive guard (a different mechanism, one layer up, in the
harness hook `run_crew.py` installs) is untouched.

### B2 — make `--parent` required
`CrewSpec.__post_init__` now refuses a blank/missing `parent` with a
message naming what to pass, at the same choke point that already enforces
the handoff/spine and result/spine requirements. `--parent`'s CLI help
text updated; it stays optional at the *argparse* level (required only at
construction) because `--resume`/`--abandon`-only/`--verify-result` build
no fresh `CrewSpec` and must not be forced to pass an unused flag.
`UNKNOWN_PARENT` retained for **display** of pre-existing registry entries
recorded before this requirement shipped.

## Map Impact
- **Structural anchors touched:** `struct:checklist_engine.require_session`,
  `struct:checklist_engine._lease_line`, `struct:checklist_engine.render_human`,
  `struct:checklist_engine.dispatch` — display/message and gate-condition
  changes only, no new verb, no new schema field, no new file.
  `struct:spine_rail._scan_active_spine` gained a staleness precondition.
  `struct:run_crew.CrewSpec` gained a required-field validation.
- **Capabilities added/changed/affected:** `current`'s render (banner,
  HELD/age, next-label) changed for every reader; `require_session`'s
  refusal texts changed; `waive` no longer session-gated; crew dispatch now
  refuses with no `--parent`.
- **Constraints/assumptions touched:** `_RAIL_STRINGS` frozen-verbatim
  constraint (#145) honored — verified byte-identical, only set membership
  changed. "No liveness verdict from the display" constraint honored
  throughout A2–A4 (path facts and ages only, never STALE/LIVE).
- **Trust limitations / drift found:** `scripts/hooks/spine_rail.py`'s
  OTHER lease-line renderer (`reconstruct_current`, used by the Stop hook)
  still prints the old `LEASE active: ...` shape — deliberately untouched,
  see "Out-of-scope observations" below. `map/INDEX.md` is now stale
  relative to this diff (new functions added two entities); `map/` is
  explicitly excluded from this batch's scope, so it was not regenerated.
- **Triage candidates:** split `reconstruct_current`'s duplicate lease-line
  render to match A3's HELD/age shape (see below); `map/INDEX.md`
  regeneration is owed to whoever next touches map/ in this epic.

## Test mode
**Required:** test-after / evidence-only (bounded handoff, focused
regression per item, full suite at the end).
**Satisfied:** yes.

## Evidence

```bash
python -m pytest -q tests/test_checklist_engine.py -k DoctrineRail   # A1: 21 passed
python -m pytest -q tests/test_checklist_engine.py -k Archive        # A2: 5 passed
python -m pytest -q tests/test_checklist_engine.py                   # A3/A4/A6/B1: 485 passed, 143 subtests
python -m pytest -q tests/test_spine_rail.py                         # A5: 180 passed, 1 skipped, 35 subtests
python -m pytest -q tests/test_crew_launcher.py -k WaiveHookTests    # B1 self-waive proof: 4 passed
python -m pytest -q tests/test_crew_launcher.py tests/test_crew_delivery_addressing.py \
  tests/test_work_id_nesting.py tests/test_crew_worktree_cwd.py      # B2: 288 passed, 18 subtests
python -m pytest -q                                                  # full ordinary suite
```

**Result:** all green except the full-suite run's one known failure (see
below). Baseline at `efe92791`: 3447 passed, 6 skipped, 1222 subtests.
This run: **3465 passed, 1 failed, 6 skipped, 1222 subtests** — subtest
count matches baseline exactly; 18 net new passing tests from this batch's
own focused coverage.

**The one failure:** `tests/test_code_map.py::MapTreeFreshnessTests::
test_map_tree_freshness_root_index_matches_a_fresh_build`. `map/` is
explicitly excluded from this batch's scope fence. This batch's source
changes add two new module-level functions (`_is_archived_path`,
`_lease_is_stale`), which shifts `map/INDEX.md`'s pinned entity count
(1274 → 1276) — the map is a generated artifact that needs regenerating,
and regenerating it is exactly the excluded action. This is disclosed as a
known, structural consequence of the scope fence intersecting with a
real source change, not a functional regression. `git diff --check`
against `efe92791` is clean (exit 0).

## Before/after renders (A2, A3, A4)

Scratch copy of the real archived plan cited in the handoff/ADMIRAL_LOG
(`.agent-work/archive/2026-08-12-20260728-charter-refresh/charter.json`,
owner last heartbeat 2026-07-29, ~23 days dead at measurement time), copied
to `.agent-work/20260821-ab/scratch/demo/.agent-work/archive/charter-copy/
charter.json` — a path that preserves the `.agent-work/archive/` segment
so A2's path predicate is genuinely exercised. **The real archived file was
never touched** (`current` is read-only by construction, and the copy's
bytes were diffed identical to the original after every render below).

**BEFORE** (pristine `efe92791` engine, run via
`.agent-work/20260821-ab/scratch/checklist_engine_BASELINE.py`):
```
RAIL: A working solution is the MIDDLE of this run — you are 7 steps from done. Next: the ACTIVE line above. Run it.

LEASE active: charter-refresh-20260728 (by charter, heartbeat 2026-07-29T17:52:38.525498+00:00)
ACTIVE orchestrator-context [in-progress] — Write docs/agents/ORCHESTRATOR_CONTEXT.md as project DELTAS over the inherited global doctrine — do not restate references/global-orchestrator.md or references/global-everyone.md; capture only project facts (purpose, authority), non-default rigor, and where this project departs. Confirm it with the user.
postconditions:
  c1 [unmet] artifact — ORCHESTRATOR_CONTEXT written and confirmed
1/2 met
next: attest orchestrator-context --cond c1 --which postconditions --evidence <evidence-id>
DIGEST: The project needs durable rigor while remaining lightweight in its real-work feedback loop. Standard checkpoints preserve human authority without adding additional confirmation gates.
```

**AFTER** (this batch's engine, all of A1–A6 applied):
```
ARCHIVED -- this file is under .agent-work/archive/. It records a finished run.

LEASE HELD: charter-refresh-20260728 (by charter, last heartbeat 550h01m ago)
ACTIVE orchestrator-context [in-progress] — Write docs/agents/ORCHESTRATOR_CONTEXT.md as project DELTAS over the inherited global doctrine — do not restate references/global-orchestrator.md or references/global-everyone.md; capture only project facts (purpose, authority), non-default rigor, and where this project departs. Confirm it with the user.
postconditions:
  c1 [unmet] artifact — ORCHESTRATOR_CONTEXT written and confirmed
1/2 met
next (for the holder): attest orchestrator-context --cond c1 --which postconditions --evidence <evidence-id>
DIGEST: The project needs durable rigor while remaining lightweight in its real-work feedback loop. Standard checkpoints preserve human authority without adding additional confirmation gates.
```

The imperative ("Run it.") is gone. The lease claims `HELD` and an age, not
`active` and a raw timestamp a reader must do arithmetic on. The next-step
hint is explicitly labelled for the holder, not the reader. 550h01m ≈ 22.9
days — matches the dossier's "22 days dead" measurement.

## Docs/contracts touched
- None.

## Assumptions
- The two-part interpretation of A4 ("next (for the holder):" whenever a
  lease is held, regardless of caller identity) rather than threading a new
  `--session-id`-comparison through `current` — see Workflow Feedback.
- B2's enforcement point (`CrewSpec.__post_init__`, not argparse
  `required=True`) — see Workflow Feedback.

## Stop conditions hit
- None outright refused the batch. Every gated plan item's `start` verb
  hit the Trip HARD context-band advisory at least once (this run's own
  context usage climbing through the batch); each time I followed the
  engine's own documented recovery (`attach ... --type refresh-request`,
  then retry `start`), never waived or bypassed the gate. Recorded here
  because it happened on every item from A1 onward, not because it
  blocked anything.

## Out-of-scope observations
- **`spine_rail.reconstruct_current`** (the Stop hook's own lease-line
  renderer, stdlib-only duplicate of `_lease_line`) still prints `LEASE
  active: <id> (by <who>, heartbeat <raw-ts>)` — A3's fix was scoped to
  `checklist_engine.py` only (the handoff names A3 without a file, A5 is
  the only item that names `spine_rail.py` explicitly, and touching a
  second renderer wasn't asked). This means `current` and the Stop hook
  now show two different shapes for the same fact. Float-up: give
  `reconstruct_current` the same HELD/age treatment in a follow-on.
- **`map/INDEX.md` is now stale** relative to this diff (entity count
  1274 → 1276). Explicitly out of scope (`map/` excluded); flagged above
  and in the evidence section rather than silently worked around.
- **The refusal text A6 rewrote is a message, not a schema** — per Lane
  D's own §5 cost note, messages rot with nothing testing them unless a
  test asserts a substring, which I added (`test_active_non_stale_refusal_
  teaches_the_qualified_remedy`), but it is one test against prose that can
  still drift silently if someone edits the string later without reading
  the docstring.
- **`--session-id` was not added to `current`** (Lane D's D6). A4 chose
  the simpler "relabel whenever any lease is held" shape instead of
  identity-aware relabeling, per the standing "added machinery is a cost"
  criterion. If a future item wants the owner's OWN render to say plain
  `next:` (never "for the holder") while a stranger's says the relabeled
  form, that needs the `--session-id` plumbing this batch deliberately did
  not add.

## Workflow Feedback

- **Handoff gaps:** none material. The eight items each named an exact
  site and reason; the three named traps (A1 frozen strings, A3 no
  verdict, B1 journaling) were exactly the three places I would have
  gotten it wrong without the warning.
- **Context rediscovered:** the actual test-suite blast radius of B2
  (making `--parent` required) was not named in the handoff beyond "check
  the test suite... before you decide the shape" — I had to discover it was
  ~75 initial test failures across 4 files, requiring a scripted AST-based
  patch pass (three small Python scripts under `.agent-work/20260821-ab/
  scratch/`) plus 4 hand-rewrites of tests whose entire premise was the old
  "no parent still works" behavior. The handoff's warning was accurate and
  sufficient, but a rough failure-count estimate would have let me size
  the item before starting.
- **Instructions improvised around:** A4's exact mechanism ("relabel
  whenever a lease is held" vs. "relabel only when the CALLER is not the
  holder") was left as latitude by the handoff's wording ("When the plan
  is held by a session that is not the caller..."). I chose the simpler,
  identity-blind shape because `current` takes no caller argument today and
  adding one is exactly the kind of machinery the standing criterion warns
  against paying for without a measured need — the owner's render gains one
  harmless extra clause ("(for the holder)") rather than the system
  growing a new parameter. Documented above under Assumptions.
- **What would have made this easier:** a rough failure-count estimate
  attached to B2 in the handoff ("expect on the order of N existing call
  sites without --parent") would have let me plan the AST-scripting
  approach up front instead of discovering the scale mid-item.

## Return status
`complete`

---

# Addendum — coordinator-adjudicated repair (R1, R2)

The coordinator relayed the Admiral's adjudication of both residuals
disclosed above and asked for a bounded fix-now, on this same branch, no
new scope beyond the two named items. Both are done, as two further
commits (four total on the branch). Plan
`.agent-work/20260821-ab/IMPLEMENTER_PLAN.json` was amended (authority
`admiral`) to add `r1-stop-hook-render` and `r2-map-regen`, driven to
`DONE` through the same engine, same as A1–B2.

## R1 — `reconstruct_current` now renders the A3 shape

`scripts/hooks/spine_rail.py:654`'s `reconstruct_current` (the Stop hook's
own lease-line renderer) rewritten from:

```
LEASE active: {sid} (by {by}, heartbeat {hb})
```

to:

```
LEASE HELD: {sid} (by {by}, last heartbeat {age} ago)
```

— the identical shape A3 established for `checklist_engine._lease_line`:
`HELD` never `active`, an age never a raw timestamp, no STALE/LIVE verdict
word anywhere.

**Is the helper shared? No — deliberately, and it says so explicitly, per
the instruction.** `scripts/hooks/spine_rail.py` is stdlib-only *by design*
and documented to "gain none" — this is not a constraint I invented for
this fix; it is the file's own established law, stated verbatim already
(for a different function, `_worktree_from_spine`, deleted from the engine
under `ADMIRAL_RULING-2` N2 and re-landed here "as a COPY, not an import").
`_format_age` is therefore a local copy in `spine_rail.py`, same
unit-conversion arithmetic, same no-threshold-judgment rule as
`checklist_engine._format_age`. Kept in sync **by inspection**, not by
sharing code — and I did not leave that as an unenforced promise: a new
regression, `ReconstructCurrentLeaseShapeMatchesA3.
test_stop_hook_render_shares_the_same_shape_as_checklist_engine`, loads
both modules, runs the identical fixture (a 22-day-stale lease) through
`checklist_engine._lease_line` and `spine_rail.reconstruct_current`, and
asserts both produce the same `LEASE HELD: ... last heartbeat ...`
substring shape and neither contains the word `active`. If the two ever
drift, this test — not a human noticing in the field — is what catches it.

6 new tests total in `tests/test_spine_rail.py`
(`ReconstructCurrentLeaseShapeMatchesA3` class, plus fixes to the two
pre-existing `reconstruct_current` tests that asserted the old string).

**Stop-hook render, before and after, against a stale lease** (22 days 19
hours dead, matching the dossier's own measurement):

```
=== BEFORE (Stop hook, efe92791) ===
LEASE active: charter-refresh-20260728 (by charter, heartbeat 2026-07-29T21:05:17.862438+00:00)
ACTIVE g1 [in-progress] -- keep going

=== AFTER (Stop hook, R1 fix) ===
LEASE HELD: charter-refresh-20260728 (by charter, last heartbeat 547h00m ago)
ACTIVE g1 [in-progress] -- keep going
```

Evidence: `python -m pytest -q tests/test_spine_rail.py tests/test_checklist_engine.py`
→ 668 passed, 1 skipped, 180 subtests. `git diff --check` clean.

Committed alone: `a5b01dca` — `fix(spine_rail): Stop hook's lease render
matches A3's HELD+age shape`.

## R2 — `map/INDEX.md` regenerated

Ran `python -m scripts.code_map build --root .` on this branch. `git
status --short map/` showed only `map/INDEX.md` modified; `map/ids.jsonl`
regenerated byte-identical; the per-module subdirectories remain
untracked, as designed.

**Map diff shape** (sanity-checked before committing, per the
instruction): entity-count and module-listing changes only, no structural
content —

```
scripts:               1274 -> 1277 entities
tests:                  5291 -> 5319 entities
scripts.hooks:            87 ->   89 entities
scripts.checklist_engine: 112 ->  113 entities
scripts.hooks.spine_rail:  65 ->   67 entities
tests.test_checklist_engine: 653 -> 670 entities (500 -> 513 holes)
tests.test_spine_rail:      220 -> 231 entities (94 -> 104 holes)
```

Every delta is attributable to this batch's own new functions
(`_is_archived_path`, `_lease_is_stale`, R1's `_format_age`) and new test
methods/classes across the four commits. Nothing appeared that wasn't
already accounted for by the diff this batch produced — no unrelated
module gained or lost entities, no broken cross-reference, no unexpected
file. Nothing to stop and report.

Committed alone, separate from R1: `99a46a08` — `chore(map): regenerate
map/INDEX.md for the deficiency-cleanup A+B batch`.

## Final suite counts (all four commits applied)

```
python -m pytest -q
3469 passed, 6 skipped, 1224 subtests passed in 141.50s
```

**Zero failures** — the one previously-disclosed failure
(`MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`)
now passes. `git diff --check` against `efe92791` exits 0.

Comparison to the original batch's own count (3465 passed / 1 failed / 6
skipped / 1222 subtests): +4 passed = 3 genuinely new test functions
(`ReconstructCurrentLeaseShapeMatchesA3`'s three methods; R1's other two
edits were the two pre-existing `reconstruct_current` tests fixed in
place, not new functions) plus the 1 previously-failing map test now
passing. +2 subtests (R1's
subtests).

## Branch state

```
99a46a08 chore(map): regenerate map/INDEX.md for the deficiency-cleanup A+B batch
a5b01dca fix(spine_rail): Stop hook's lease render matches A3's HELD+age shape
1fd593ac fix(engine,run_crew): exempt waive from the session gate; require --parent
a790ab7c fix(engine): stop the read/rail surface from instructing an agent to resume a dead plan
```

Four commits total on `afk/20260821-ab`, base `efe92791`. No push, no PR,
no `mcp__spine__*` call at any point in this addendum either. No file
under `skills/charter/*`, `skills/_shared/global-everyone.md`, or
`tests/data/store_mentions.approved.txt` touched (verified again via `git
status --short` across the whole addendum).

## Addendum return status
`complete`

---

# Addendum 2 — independent review findings F1, F2 (Admiral-adjudicated)

The independent review returned APPROVE on `efe92791..99a46a08` and raised
two non-blocking findings; the Admiral ruled both fix-now on this branch.
Plan amended again (authority `admiral`) to add `f2-parent-optional-
regression` and `f1-parent-doctrine`, driven through the same engine.

## F2 — restored the coverage the AST patches removed

New class `ParentOptionalForRecoveryVerbsTests` in `tests/test_crew_launcher.py`
(3 tests), mirroring the file's own pre-existing pattern for the identical
class of concern (`MandatoryModelTests.test_resume_needs_no_model_at_all`
/ `test_bare_abandon_needs_no_model_at_all`):

- `test_resume_succeeds_with_no_parent` — a synthetic `running` registry
  entry with no `parent` key, `--resume` with no `--parent`, asserts
  `completed`.
- `test_bare_abandon_succeeds_with_no_parent` — same shape, bare
  `--abandon` (no `--relaunch`), asserts `abandoned`.
- `test_verify_result_succeeds_with_no_parent` — a synthetic `external`
  entry with no `parent` key and no spine, `--verify-result` with no
  `--parent` but with the `#432` `--accept-mtime-only-risk` escape hatch
  (so no dispatch of any kind — which WOULD need `--parent` — is needed to
  build the fixture), asserts `completed`.

None of the three constructs a `CrewSpec` (`CliBackend.resume`/
`abandon_crew`/`ExternalBackend.verify` all read the stored entry
directly), which is the exact reason B2 put the requirement at
`CrewSpec.__post_init__` rather than argparse `required=True` — this is
the regression that proves that design choice still holds and that would
catch someone later "tidying" it into a blanket flag requirement.

Evidence: `python -m pytest -q tests/test_crew_launcher.py` → 248 passed.
Committed alone: `4e13b789`.

## F1 — documented `--parent` in the dispatch doctrine

Added a new section to `skills/commander/references/crew-dispatch.md`
(scope fence extended by the coordinator for this one file, this item
only), in the identical shape of the file's existing "Name a tier"
section — refusal site, what to pass, where the value comes from, and the
`--resume`/bare-`--abandon` exemption:

> ## Name your dispatcher: --parent is required, and it is your own SPINE_SESSION
>
> `run_crew.py` refuses a fresh or relaunched dispatch that names no
> `--parent` at all (`CrewSpec.__post_init__`) — `crew-runs.json:parent`
> is what `verify_declared_dispatch.py` checks a crew's dispatch against,
> and an absent value cannot be checked. Pass your own `SPINE_SESSION`
> (the identity you were bound with, read from your own environment) as
> `--parent`: `run_crew.py --parent "$SPINE_SESSION" ...`. `--resume` and
> a bare `--abandon` construct no `CrewSpec` and so need no `--parent` at
> all — the refusal, like the model requirement above, applies only to a
> fresh or relaunched dispatch.

**Where "pass your own `SPINE_SESSION`" came from**: no prior doctrine
established this anywhere in the corpus (confirmed by a dedicated research
pass across `commander-core.md`, `COMMANDER_SPINE.template.json`,
`run_crew.py`'s own docstrings, and `skills/workbench/references/`).
`run_crew.py`'s `--parent` help text only names the category ("e.g. a
Commander/Admiral session name"), never a concrete value or lookup path.
`SPINE_SESSION` is the literal, available identity — already treated as
ambient in this same doctrine file (the full-suite polling snippet earlier
in the file unsets `SPINE_SESSION` before running tests, which only makes
sense if the Commander's process already carries a real one). This is
named as new doctrine, not cited as a pre-existing convention.

Committed alone, separate from F2: `ee59a7b9`.

## Map impact — a new, disclosed residual, NOT regenerated this round

**F1 contributes zero delta to `map/`.** It is a markdown file;
`scripts.code_map` indexes Python modules only. Confirmed directly: after
staging only the F1 commit's file, `git status --short map/` reported
nothing.

**F2 does shift `map/`**, the same way every test-coverage addition in
this batch has: 3 new test methods (`tests` entity count 5319 → 5323).
`python -m pytest -q` therefore fails
`MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
again, for the same structural reason as the original batch's own
disclosed residual (resolved last round by R2, an explicitly authorized
map regen).

**This round's instruction was explicit the other way — "do not touch
map/... if it does, stop and tell me" — so `map/` was NOT regenerated.**
This is disclosed here rather than silently worked around or silently
regenerated without authorization. The evidence below isolates the rest
of the suite by deselecting the one known-stale test, exactly as the
prior round's own m9-suite/r1/r2 checkpoints did.

## Evidence

```bash
python -m pytest -q tests/test_crew_launcher.py                      # F2: 248 passed
python -m pytest -q --deselect tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
# 3471 passed, 6 skipped, 1 deselected, 1224 subtests passed
```

Full, undeselected `python -m pytest -q`: **3471 passed, 1 failed, 6
skipped, 1224 subtests** — the 1 failure is the disclosed map staleness
above, not a functional regression. `git diff --check` against `efe92791`
exits 0.

## Branch state (final)

```
ee59a7b9 docs(commander): document the now-required --parent flag (F1)
4e13b789 test(run_crew): restore coverage the B2 AST patches removed (F2)
99a46a08 chore(map): regenerate map/INDEX.md for the deficiency-cleanup A+B batch
a5b01dca fix(spine_rail): Stop hook's lease render matches A3's HELD+age shape
1fd593ac fix(engine,run_crew): exempt waive from the session gate; require --parent
a790ab7c fix(engine): stop the read/rail surface from instructing an agent to resume a dead plan
```

Six commits total on `afk/20260821-ab`, base `efe92791`. No push, no PR,
no `mcp__spine__*` call. `map/` untouched this round (verified: `git
status --short map/` is empty at HEAD). No file under `skills/charter/*`,
`skills/_shared/global-everyone.md`, or
`tests/data/store_mentions.approved.txt` touched.

Coordinator note acknowledged: `main` has moved (three commits: a docs
restructure, three episodes, the epic work area) since this branch's base.
This branch was not rebased or merged against it; base remains `efe92791`
throughout, unchanged by this addendum.

## Addendum 2 return status
`complete`

---

# Addendum 3 — final map regeneration (coordinator-authorized)

Both F1 and F2 verified by the coordinator ("F1 and F2 touch exactly
`skills/commander/references/crew-dispatch.md` and
`tests/test_crew_launcher.py` and nothing else, and `map/` is untouched
at HEAD"). The coordinator then authorized the map regen this round, same
terms as R2: `map/INDEX.md`/`map/ids.jsonl` only, commit `map/` alone,
sanity-check the diff shape first.

## Exact map diff shape

Ran `python -m scripts.code_map build --root .`. `git status --short map/`
showed only `map/INDEX.md` modified (`ids.jsonl` regenerated identical;
per-module subdirs untracked by design).

```diff
 evals: 12 modules, 54 entities
 examples: 1 modules, 4 entities
 scripts: 60 modules, 1277 entities
 skills: 1 modules, 18 entities
-tests: 95 modules, 5319 entities
+tests: 95 modules, 5323 entities

-## tests (95 modules, 5319 entities)
+## tests (95 modules, 5323 entities)

-- [tests.test_crew_launcher](...) (338 entities, 259 holes): HOLE: no docstring
+- [tests.test_crew_launcher](...) (342 entities, 262 holes): HOLE: no docstring
```

Three lines total (`git diff --stat`: 1 file changed, 3 insertions, 3
deletions) — exactly the predicted narrow shape: `tests` entities
5319→5323 (the corpus summary line and the `tests` section header, same
number stated twice) and `tests.test_crew_launcher` 338→342 entities
(259→262 holes). **No module added or removed, no link retargeted, no
docstring line rewritten** — sanity-checked before committing, per the
instruction. F1's doctrine edit contributes nothing to this diff, confirmed
directly: the only entity-count line that moved names `test_crew_launcher`
specifically, matching F2's three new test methods plus their containing
class (`ParentOptionalForRecoveryVerbsTests`) exactly, and no
`crew-dispatch`-named entry appears anywhere in the diff (it is a markdown
file, never indexed by `scripts.code_map`).

**Extra check run before committing**, beyond what was asked: since
`tests.test_crew_dispatch_doctrine` exists and asserts specific content
inside `crew-dispatch.md` (pins the "Suggested Model Tier" doctrine wording
from an earlier issue, #611), I ran it explicitly to confirm F1's addition
did not disturb what it already pins:
`python -m pytest -q tests/test_crew_dispatch_doctrine.py` → 2 passed.

Committed alone: `8957d925`.

## Final suite counts

```
python -m pytest -q
3472 passed, 6 skipped, 1224 subtests passed in 143.28s (0:02:23)
```

**Zero failures.** `git diff --check` against `efe92791` exits 0.

## Branch state (final)

```
8957d925 chore(map): regenerate map/INDEX.md for F1/F2 (--parent doctrine + regression)
ee59a7b9 docs(commander): document the now-required --parent flag (F1)
4e13b789 test(run_crew): restore coverage the B2 AST patches removed (F2)
99a46a08 chore(map): regenerate map/INDEX.md for the deficiency-cleanup A+B batch
a5b01dca fix(spine_rail): Stop hook's lease render matches A3's HELD+age shape
1fd593ac fix(engine,run_crew): exempt waive from the session gate; require --parent
a790ab7c fix(engine): stop the read/rail surface from instructing an agent to resume a dead plan
```

Seven commits total on `afk/20260821-ab`. Base confirmed unmoved:
`git merge-base afk/20260821-ab efe92791` == `efe92791`. No push, no PR,
no `mcp__spine__*` call. `main`'s three new commits (docs restructure,
episodes, epic work area) were not pulled or rebased into this branch.

## Addendum 3 return status
`complete`

This closes the implementer's lane on this branch.
