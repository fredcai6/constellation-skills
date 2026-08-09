# Implementation Result

## Assigned gate
`gs` — land the skills cherry-pick with a real check

## Completed slice
Two things, as scoped: (1) cherry-picked exactly the four `skills/` paths from
`d102c05` (never the whole commit); (2) tracked the measured-stable 2-file map
landing zone (`map/INDEX.md` + `map/ids.jsonl`) and wrote `map_tree_freshness`,
a permanent regression test proving the committed entry point matches a fresh
build.

## Scope
**Files changed:**
- `skills/commander/references/commander-core.md` (cherry-picked from `d102c05`)
- `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md` (cherry-picked from `d102c05`)
- `skills/implementer/SKILL.md` (cherry-picked from `d102c05`)
- `skills/scout/SKILL.md` (cherry-picked from `d102c05`)
- `.gitignore` (new `map/*` rule + two negations; corrected an adjacent comment
  that had gone stale — see Workflow Feedback)
- `map/INDEX.md`, `map/ids.jsonl` (newly tracked; the 2-file landing zone)
- `tests/test_code_map.py` (`MapTreeFreshnessTests`, 2 tests)
- `.agent-work/issue-456/gs-implement/` (my own plan + engine journal)
- `.agent-work/issue-456/crew-handoffs/gs-implement-RESULT.md` (this file)

**Specific exclusions touched:** no — `scripts/code_map/*.py` untouched (one
transient, reverted-and-verified mutation to `scripts/agent_work_root.py` for
the mutation-kill proof, see Evidence; that file is not on the exclusion
list and carries zero net diff).

## Behavior changed
Yes. `map/INDEX.md` now resolves as a real, committed starting page (crews no
longer hit an untracked dangling path); `map/ids.jsonl` is tracked too (empty,
correctly — no anchor id has ever been authored in this repo). A stale commit
of either file is now caught by `pytest -k map_tree_freshness`.

## Map Impact
- **Structural anchors touched:** `map/INDEX.md`, `map/ids.jsonl` — now real,
  git-tracked files, not just a build target. `skills/commander/references/commander-core.md`,
  `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`,
  `skills/implementer/SKILL.md`, `skills/scout/SKILL.md` — carry the 9-line
  `d102c05` diff, now with an owning gate (this one) closing the file-ownership
  gap critic F3 found.
- **Capabilities added/changed/affected:** a crew that reads the cherry-picked
  skill text now finds a resolvable map entry point at `map/INDEX.md`, not a
  dangling instruction.
- **Constraints/assumptions touched:** honored "one gate per file and
  decision-class in scope" — the same rule `d102c05` adds — by giving these
  four files an owning gate instead of shipping the rule while violating it.
- **Decision candidates / resolved decisions:** the landing-zone decision
  (`.agent-work/issue-456/landing-zone-measurement.md`) is now executed, not
  just measured: 2 files tracked, ~4,010 remain untracked and gitignored.
- **Claims/evidence produced:** determinism — `map_tree_freshness` asserts the
  committed entry point matches a fresh `build` from this repo's own tracked
  source; proven able to fail (see Evidence).
- **Triage candidates:** none surfaced beyond what's already tracked in
  Workflow Feedback below.

## Test mode
**Required:** `test-first` (TDD) for the freshness test
**Satisfied:** yes — red observed against a deliberately staled committed
index, then green; a separate mutation-kill proof (source edit, not index
edit) also shown RED then reverted byte-clean.

## Evidence

### 1. Skills cherry-pick — scoped diff empty
```
$ git diff d102c05 -- skills/commander/references/commander-core.md skills/commander/templates/IMPLEMENTER_HANDOFF.template.md skills/implementer/SKILL.md skills/scout/SKILL.md
(no output, exit 0)
$ git diff --quiet -- .agent-work/explore-code-map/cycle-3.json
(exit 0 — untouched)
```
Note: `git diff d102c05 -- skills/` (the whole tree, as the handoff's close
criterion literally reads) is **not** empty — see Workflow Feedback for why
that's expected and not a defect in this change.

### 2. `git ls-files map/` — exactly two paths
```
map/INDEX.md
map/ids.jsonl
```

### 3. Build + check — 7/7, exit 0
```
$ python -m scripts.code_map build --root .
pass1: 114 modules indexed
statements: 98539 over 114 files (0 failures)
{"modules": 114, "entities": 3897, "pages": 4012, "entity_pages": 3897, "holes": 2602, "ids": 0, ...}
$ python -m scripts.code_map check --root .
ok   no-empty-pages
ok   page-accounting
ok   refs-line-self-consistent
ok   entity-symbol-join
ok   page-location-matches-content
ok   inbound-attribution
ok   deterministic-rebuild
passed 7 checks
```

### 4. `map_tree_freshness` — TDD red, then green
Staled the committed `map/INDEX.md` (appended a marker line to a backup-restored copy), ran:
```
$ python -m pytest tests/test_code_map.py -k map_tree_freshness -v --color=no
tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_ids_jsonl_matches_a_fresh_build PASSED
tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build FAILED
AssertionError: "# co[123 chars], 2928 entities\n..." != "# co[123 chars], 2924 entities\n..."
1 failed, 1 passed, 146 deselected in 17.48s
```
Restored `map/INDEX.md` byte-for-byte; re-ran and both tests passed. (This
red-proof run also surfaced a real fact, not a manufactured one: my own edits
to `tests/test_code_map.py` — adding this very test class — moved the corpus's
entity count, so `map/` genuinely needed a rebuild before I could finalize;
I ran `build --root .` again, re-staged, and reconfirmed 7/7 + green before
reporting done.)

### 5. `map_tree_freshness` — mutation-kill proof (RED under a real source edit)
Added a top-level function `_map_tree_freshness_probe` to
`scripts/agent_work_root.py` (a mapped module outside `scripts/code_map/`),
did **not** rebuild `map/`, ran the selector:
```
$ python -m pytest tests/test_code_map.py -k map_tree_freshness -v --color=no
tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_ids_jsonl_matches_a_fresh_build PASSED
tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build FAILED
AssertionError: "# co[89 chars]s, 916 entities\ntests: 52 modules, 2928 entit[19856 chars]m.\n" != "# co[89 chars]s, 915 entities\ntests: 52 modules, 2928 entit[19856 chars]m.\n"
1 failed, 1 passed, 146 deselected in 16.57s
```
916 (fresh, mutated source) vs. 915 (committed, stale) entities — exactly the
root-index movement `landing-zone-measurement.md`'s Arm B predicted for a
shape edit. Reverted the function:
```
$ git diff --quiet -- scripts/agent_work_root.py
(exit 0 — byte-clean; NOT git status --porcelain, which false-negatives here
under core.autocrlf=true per the handoff's own warning)
```
Re-ran the selector: both tests PASSED.

### 6. Full suite
```
$ python -m pytest tests/ -q --color=no
1840 passed, 2 skipped, 701 subtests passed in 512.12s (0:08:32)
```
Baseline was 1838 passed / 2 skipped / 701 subtests / 0 failed; +2 is exactly
the two new `map_tree_freshness` tests. 0 failed.

**Result:** pass

## TDD evidence, if required
- Failing test observed: see Evidence §4 above (`1 failed, 1 passed`)
- Passing test observed: see Evidence §4 above, post-restore (`2 passed`)
- Refactor while green: no refactor needed; the test is small and single-purpose

## Docs/contracts touched
- `.gitignore` — added the `map/*` / `!map/INDEX.md` / `!map/ids.jsonl` rule
  and corrected an adjacent comment that had gone stale (see Workflow
  Feedback).

## Assumptions
- The RED-proof mutation belongs in a mapped module *outside*
  `scripts/code_map/` (I used `scripts/agent_work_root.py`), reading the
  handoff's "do not touch `scripts/code_map/*.py`" exclusion as governing
  shipped diffs, not a transient, git-diff-verified-clean proof step — the
  same document explicitly asks for exactly that proof. Net diff on that file
  is zero; flagging the reading here rather than assuming it's uncontested.
- Comparison in `map_tree_freshness` is over `str.read_text(encoding="utf-8")`
  (universal-newline-normalized), not raw bytes — required by
  `CREW_CONTEXT.md`'s Windows guidance and confirmed necessary in practice:
  `git add map/INDEX.md` itself warned "LF will be replaced by CRLF the next
  time Git touches it." A raw-byte comparison would read that checkout
  behavior as staleness.

## Stop conditions hit
None.

## Out-of-scope observations
None beyond what's captured in Workflow Feedback.

## Workflow Feedback

- **Handoff gaps:** the close criterion "`git diff d102c05 -- skills/` being
  empty afterwards" reads as the whole `skills/` tree, but the branch has
  legitimately diverged from `d102c05` elsewhere in `skills/` via unrelated
  later gates (g5–g8 touched `skills/cartographer/references/map-model.md`,
  `skills/commander/templates/COMMANDER_SPINE.template.json`,
  `skills/interrogator/templates/INTERROGATION.template.json`,
  `skills/reviewer/templates/REVIEW_SURVEY.template.json`) — none of which are
  mine to touch or revert. Scoping the diff to exactly the four cherry-picked
  paths is empty (evidence §1); the whole-tree form is not and never will be
  again once any other gate lands. I corrected my own plan's check text
  in-engine via `amend --delta` (authority "agent", logged) rather than
  silently reinterpreting the criterion.
- **Context rediscovered:** none — `landing-zone-measurement.md` and the
  handoff together carried everything needed; no extra digging required.
- **Instructions improvised around:** the handoff's freshness-test recipe says
  "mutate something that should move the root index (add a top-level function
  to any mapped module)" while a separate exclusion says "do not touch
  `scripts/code_map/*.py`." I read the exclusion as governing the shipped
  diff, chose a mapped module outside `scripts/code_map/` for the proof
  (`scripts/agent_work_root.py`), and reverted it byte-clean before
  finalizing — see Assumptions.
- **What would have made this easier:** scope the `git diff d102c05 -- skills/`
  close criterion to the four paths explicitly in the handoff text, so a
  gate landing after other unrelated `skills/` changes doesn't have to
  re-derive that the whole-tree form was never literally intended.

## Which gate owns freshness
No dedicated gate owns it going forward — the mechanism is the
`map_tree_freshness` test itself, permanently embedded in
`tests/test_code_map.py`. Any future change runs the full suite as its own
close criterion, and the full suite now includes this test; a stale
`map/INDEX.md` or `map/ids.jsonl` fails that run the same way any other
regression would, with no separate freshness gate to remember to invoke.

## Return status
`complete`
