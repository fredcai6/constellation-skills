# Implementer Handoff

## Gate
`g3-drop-cap-implement` (issue #308, epic-298)

## Task
Remove the 20-entry hard cap from `scripts/apply_lessons_delta.py`. The cap is deleted outright — **not renamed, not softened, not made configurable**. The episode store now owns accumulation; the Curator's regular cleanup pass replaces the cap as the retention story.

## Protected Intent
The lessons **writer keeps working**. This is a cutover, not a demolition: `apply_lessons_delta.py` must still add, retire, confirm, export and rewrite the file exactly as it does today, minus the cap refusal. A run that produces a finding must be able to bank it — today it cannot, because the bank sits at 20/20 and `add` exits 1.

## Test Mode
Test-after allowed, but the cap-refusal test at `tests/test_apply_lessons_delta.py:120` (`test_cap_enforced_and_retire_before_add`) **must be rewritten, not deleted**. Its scenario is exactly what this change now forbids. Delete-the-test would make the suite green by removing the only thing that could have failed — the failure mode this epic keeps rediscovering. Replace it with a test that adds past 20 and asserts the add **succeeds**, so the removal has an assertion standing behind it.

## Close Criteria
- `python .agent-work/issue-308/checks/cap_is_gone.py` exits 0. It drives the REAL writer against a frozen 20-entry fixture (`.agent-work/issue-308/fixtures/LESSONS-at-cap.md`) and refuses to report a pass when the add is rejected for a non-cap reason. **It is red at HEAD — run it before you change anything and paste the red transcript.**
- `! grep -nE 'DEFAULT_CAP|active cap' scripts/apply_lessons_delta.py` — the removal is not a rename.
- No residual `cap=<N>` claim survives anywhere that reads as enforced. Specifically:
  - `DEFAULT_CAP` (`:37`) gone.
  - The refusal branch (`:435-437`, `if len(book.active) >= book.cap: raise ... active cap {book.cap} reached`) gone.
  - The `cap` field on the `Book` dataclass (`:122`) and the `cap=` group in the `playbook-state` header regex (`:48`) and its rewrite (`:272`) — **remove the field from the grammar**, and make the parser TOLERANT of a legacy header that still carries `cap=N` (every existing file in the repo has one, including `.agent-work/LESSONS.md` and the test fixtures) by accepting and discarding it. A parsed-but-unenforced `cap=20` left in the header is a stale claim that enforces nothing — the exact defect class this epic has been fixing all week.
  - The `## Active` preamble prose the writer emits (`:145`, "Reaching the cap is a failure mode...") and the seeded header (`:140`) — replace the cap sentence with the replacement retention story: **the Curator's regular cleanup pass**, not a number.
  - The summary line at `:685` (`"playbook: N active (cap {book.cap}, run {book.run_tick})"`).
- Full suite green: `python -m pytest -q`.

## Allowed Scope
- `scripts/apply_lessons_delta.py`
- `tests/test_apply_lessons_delta.py` — pre-authorized, including its header fixtures at `:57`, `:306`, `:557`, `:575`, `:630`, `:778`, all of which embed `cap=20`.
- `.agent-work/LESSONS.md`'s **header prose only**, and only if you write it through `apply_lessons_delta.py` itself. **Never hand-edit that file.**
- Any other test or doc the suite proves is pinned to cap behaviour — find them by running the suite, not by guessing.

## Specific Exclusions
- `scripts/apply_episode_delta.py`, `episodes/`, `skills/lessons-auditor/` — untouched. The auditor and the episode store are other gates' territory (#308 g4, g5).
- Do **not** empty, delete, or migrate any lesson content. The migration is gate g4 and it is mine, not yours.
- Do not add a replacement cap, warning threshold, `--max-active` flag, config key, or environment override. `decision:no-cap-replacement-by-hygiene`.

## Constraints
- `decision:no-cap-replacement-by-hygiene`: no replacement numeric limit of any kind, in any form.
- Prove the behaviour changed by **running the writer**, never by reading the diff.
- Legacy headers carrying `cap=N` must keep parsing. A hard failure on existing files is a regression, not a cleanup.
- Interpreter is `python` (3.14, has pytest). **`py` has no pytest and reports a silently green suite** — do not use it for tests.
- Single-quote any grep pattern in a shell string: backticks inside double quotes are executed by this shell and produce a refusal for the wrong reason.
- Do not `git checkout <file>` to undo a probe mutation — it reverts your real edit too. Snapshot to a scratch copy instead.

## Deliverable Path Check
- **Committed** — `scripts/apply_lessons_delta.py`, `tests/test_apply_lessons_delta.py`. `git check-ignore` on both exits 1 (not ignored).
- **Committed** — `.agent-work/LESSONS.md`. `.agent-work/` is **tracked** in this repo as of `b69e6c8` (#326); `git check-ignore .agent-work/` exits 1 and `git ls-files .agent-work/` returns 1958 files. Any doc claiming `.agent-work/` is gitignored is stale.

## Required Evidence
**Load-bearing — prove rigorously:**
1. `cap_is_gone.py` RED at HEAD before your change (paste it), GREEN after (paste it). Both transcripts, both exit codes.
2. The rewritten `test_cap_enforced_and_retire_before_add` replacement: show it FAILS against pre-change `apply_lessons_delta.py` if the assertion is meaningful, or state plainly why it cannot be red-proved.
3. Full suite: `python -m pytest -q`, final counts pasted.

**Confirmatory — a spot-check suffices:**
4. `! grep -nE 'DEFAULT_CAP|active cap' scripts/apply_lessons_delta.py`.
5. A legacy header carrying `cap=20` still parses (drive the writer against `.agent-work/issue-308/fixtures/LESSONS-at-cap.md`, which has one).

If the suite goes red anywhere outside `test_apply_lessons_delta.py`, derive the distribution mechanically — `python -m pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c` — and report that command's output, never a glance at the tail.

## Verification Commands
```bash
python .agent-work/issue-308/checks/cap_is_gone.py
! grep -nE 'DEFAULT_CAP|active cap' scripts/apply_lessons_delta.py
python -m pytest -q
```

## Suggested Model Tier
`stronger` — the grammar change (removing `cap=` from the header while keeping legacy files parsing) is where this can quietly break every existing lessons file.

## Authority
Decided already, not yours to revisit: the cap is removed with no numeric replacement (Tommy, 2026-08-01: *"the hard cap was intended to not let things hang out, but it just leads to forgetting when it's not cleaned up"*); the writer survives; the Curator's regular cleanup is the replacement retention story. **You decide** the mechanics of the grammar removal and legacy tolerance.

## Stop Conditions
Stop and return if: the cap cannot be removed without breaking existing lessons files; a test outside the allowed scope pins cap behaviour in a way that needs a design call; removing the header field turns out to require touching the episode store or the auditor; or the red-before-green proof cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (with the four transcripts), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write your result to `.agent-work/issue-308/crew-handoffs/g3-implement-result.md`.
