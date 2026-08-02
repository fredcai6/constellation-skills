# Review Result

## Assigned Gate
G3 — FIA sector-line derivation + nesting (issue #662, epic #659) — RE-REVIEW after prior BLOCK, rework
attempt 2.

## Result
`APPROVE`

## Handoff compliance
Focused re-review per `.agent-work/662-segment-map/g3-rereview-handoff.md`, verifying the fix to the sole
prior blocker. Read `_merge_slivers` in
`src/physics/segment_map/derivation/sector_nesting.py`: the `left_removable` (backward-merge) branch now
reads

```python
if left_removable:
    del boundaries[i]
    del types[i]
```

— symmetric with the forward (`right_removable`) branch, which also does `del types[i]`. In both
directions the entry deleted from `types` is always the SLIVER's own (index `i`), never the real
neighbor's; the neighbor's type shifts into the merged slot in both cases. Confirmed this is the exact,
correctly-scoped fix for the previously-BLOCKed defect (old code did `del types[i - 1]` in the backward
branch, deleting the real left neighbor's type and leaving the sliver's own noise type in place).

**The catching test genuinely catches it (independently reproduced, not trusted from the report):**
`test_backward_merge_keeps_the_real_neighbors_type_not_the_slivers` builds a cut-blocked backward-merge
sliver (`segment0=CORNER [0,297.5)`, `segment1=STRAIGHT [297.5,400)` split by sector line `300.0`, forcing
the STRAIGHT sliver `[297.5,300)` to merge backward into the differently-typed CORNER neighbor) and asserts
the merged segment carries CORNER, not STRAIGHT. I did not just re-read this or trust the impl-result's own
revert-test claim — I mechanically reverted the fix myself: loaded the real module source, replaced the
fixed backward-merge block with the exact old buggy form (`del types[i - 1]`) via a text substitution assert
(so I know I reverted the actual shipped code, not a stand-in), `exec`'d it as an isolated module, and ran
the new test's exact fixture logic against it. Result: old code produces
`types after nesting = [0, 0, 0, 0, 2]` (STRAIGHT at the position that must be CORNER) —
`t2[idx_300 - 1] == STRAIGHT(0)`, not `CORNER(2)` — so the test would genuinely `assert 0 == 2` and FAIL
against the pre-fix code. Confirmed non-vacuous by execution, not inference.

## Scope drift
Clean. `git status --porcelain` reproduced: only `src/physics/segment_map/derivation/sector_nesting.py` and
`tests/unit/physics/segment_map/derivation/test_sector_nesting.py` are the production/test diff for this
gate; the rework is confined to the one-line fix + comment + one new test, matching the handoff's stated
scope exactly. `data/f1_data_2023.db` still shows `M` in git status — this is the SAME pre-existing hygiene
item the prior (BLOCK) review already flagged and traced to a pre-session artifact, not reproduced by
re-running the reviewed code; unchanged by this rework, not a new scope violation. An untracked
`.agent-work/663-grip-g/` directory belongs to a sibling epic-659 gate and is out of this review's scope.

## Evidence verdict
Both required commands re-run independently and reproduced exactly:

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_sector_nesting.py -q
# -> 18 passed in 1.21s   (was 17 before this rework's new test)

C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/sector_nesting.py
# -> PASS (1 files checked)
```

Also re-confirmed the two invariants unaffected by this rework: `grep -nE "\b5\.0\b"` → zero matches (exit
1, `MIN_SEGMENT_LENGTH_M` still the only source of the threshold); `grep -inE "^\s*(import fastf1|from
fastf1)"` → zero matches (exit 1, DB/store-only unchanged).

Went beyond the handoff's two commands with a third, self-devised evidence step: the in-memory revert-and-
rerun described above under Handoff compliance, executed at
`C:/Users/fredc/AppData/Local/Temp/claude/C--Programs-f1Brainz/75f751ad-3984-44e8-a745-c0c90f57a861/scratchpad/revert_check.py`,
output:
```
boundaries after nesting: [0.0, 300.0, 400.0, 600.0, 700.0, 1000.0]
types after nesting:      [0, 0, 0, 0, 2]
t2[idx_300 - 1] = 0 (CORNER=2, STRAIGHT=0)
CONFIRMED: old buggy code produces the WRONG type (0, expected 2) -- the new regression test is non-vacuous,
it would FAIL against the pre-fix code.
```
This matches the implementer's own claimed revert-test result in `g3-impl-result.md` (`Rework (attempt 2)`
section) byte-for-byte in substance — but was independently derived, not copied from it.

All 18/18 tests genuinely demonstrate their claimed rule classes; the previously-uncovered sliver-merge
type-inheritance gap is now covered and passing for real (verified by controlled failure against the old
code, not just green-against-new-code).

## Code/doc quality
CREW_CONTEXT project rules re-checked in light of the rework: no hardcoded literal threshold (grep-confirmed
above), DB-only/no-FastF1 unaffected, `MIN_SEGMENT_LENGTH_M` import unchanged. The fix itself is minimal — a
one-token index change plus an updated comment — no scope creep, no speculative refactor smuggled in with
the bugfix. The rewritten comment on the backward branch now accurately states the symmetric behavior the
code actually has (previously it implicitly described behavior the old code did not have).

**Fowler pass** (`.agent-work/662-segment-map/g3-review/fowler_pass_rework2.json`, rail-verified —
`verify_fowler_pass.py` exit 0, `smells=12, flagged=[duplicated-code], overridden=[data-clumps,
primitive-obsession, divergent-change]`):
- 8/12 absent, incl. `comments-as-deodorant` explicitly checked absent (comment now matches code).
- 1 flagged (minor, non-blocking, a repeat of the prior review's own observation, not new): the forward and
  backward merge blocks in `_merge_slivers` remain near-mirror-image ~5-line blocks after this fix — the fix
  corrected the asymmetry rather than removing the duplication. A shared helper
  (e.g. `_do_merge(boundaries, types, remove_boundary_idx, remove_type_idx)`) would make the two directions
  structurally incapable of diverging again; worth doing on the next touch of this file, not blocking here.
- 3 overridden with logged repo-standard reasons carried forward unchanged from the prior review (this
  rework does not touch `derive_sector_lines`, the sole site those three overrides concern): data-clumps
  against `session_fit.load_quali_session`'s own signature; primitive-obsession against `runtime.py`'s
  documented int-coded convention; divergent-change against G1's one-file-per-derivation-gate precedent.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the fix and its evidence fully back the "backward-merge now
  keeps the neighbor's type" claim; independently reproduced, not just inferred.
- **Constraints not violated:** Unaffected by this narrow fix; `constraint:db-only-analysis` and
  `decision:sector-split-not-snap` remain honored (re-confirmed via grep, unchanged from prior approval).
- **Notes match the diff:** `g3-impl-result.md`'s "Rework (attempt 2)" section accurately describes the fix,
  the new test, and the revert-verification it ran — matches the actual diff and my independent
  reproduction.
- **Decision candidates surfaced:** The impl-result's "Decision candidate superseded" note (the earlier
  forward-first-preference framing replaced by "type-inheritance must be symmetric regardless of direction")
  is an accurate, appropriately-scoped refinement — properly surfaced for Commander to carry into the g4/g5
  decision-candidate record, not silently resolved.
- **Durable context routed:** Yes.

## Reconciliation check
No docs/architecture divergence. This is a correctness-only fix inside the already-approved shape of
`nest_sectors`/`_merge_slivers` — no new file, capability, or map anchor. No reconciliation gap for Commander
beyond carrying forward the superseded decision-candidate note above.

## Blockers
- None.

## Out-of-scope observations
- `data/f1_data_2023.db` still shows as git-modified — same pre-existing, pre-session artifact the prior
  BLOCK review already traced and flagged as a pre-merge hygiene item (revert before merge), not a code
  defect; unchanged by this rework.
- Fowler: the near-duplicate forward/backward merge blocks in `_merge_slivers` (flagged, non-blocking) are
  still present after the fix — the fix corrected the asymmetry rather than the duplication itself. Worth
  extracting a shared helper when this file is next touched, both for clarity and to make the two
  directions' behavior structurally impossible to diverge again (the exact class of bug that was just
  fixed).

## Workflow Feedback

- **Handoff gaps:** None — the re-review handoff's three numbered focus items (fix correctness, non-vacuous
  test, no regression) mapped directly onto the survey's evidence/handoff-compliance checks; no ambiguity
  encountered.
- **Context rediscovered:** None beyond what the handoff pointed at directly (the prior `g3-review-result.md`
  BLOCK writeup and the rework section of `g3-impl-result.md` were both exactly where I needed to look).
- **Instructions improvised around:** None. The handoff's two verification commands were sufficient to
  reproduce the claimed green state; I added a third, self-devised evidence step (in-memory revert-and-rerun)
  on my own initiative to satisfy the inherited "verify claimed side-effects against the world" doctrine at a
  stronger standard than a manual trace alone — this was an addition, not a workaround for a gap.
- **What would have made this easier:** Nothing missing from the handoff. One small process note: the
  g3-review directory already held a consolidated (DONE) `review.json` from the first pass — I created a
  fresh sibling survey file (`review-rework2.json`) rather than reopening the closed one, since the engine's
  `reopen` verb is for `gated` rework-cascades, not a natural fit for re-running a fully-consolidated survey.
  Worth a documented convention (`review-rework<N>.json` naming, as used here) so future re-reviews don't
  have to make this call fresh each time.

## Return status
`complete`
