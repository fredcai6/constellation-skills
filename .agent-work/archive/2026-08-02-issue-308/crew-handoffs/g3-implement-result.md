# IMPLEMENTER_RESULT — g3-drop-cap-implement (issue #308, epic-298)

**Status:** COMPLETE. Plan `.agent-work/issue-308/g3-implement-plan.json` driven to `DONE: no open items`
through the engine (lease `g3-impl-308b`, claimed before any solution work, released as the last action).

## Completed slice

The 20-entry hard cap is deleted from `scripts/apply_lessons_delta.py` — removed outright, not renamed,
softened, or made configurable. No replacement numeric limit of any kind exists
(`decision:no-cap-replacement-by-hygiene` honored). The writer still adds, retires, confirms, exports and
rewrites exactly as before; the only behavior removed is the refusal.

Legacy playbooks carrying `cap=N` keep parsing: the grammar accepts the field as a **tolerated,
non-capturing** group and discards it, so it is never stored, never read, and never round-tripped back out.

## Files changed

| file | change |
|---|---|
| `scripts/apply_lessons_delta.py` | cap removed at 8 sites (below) |
| `tests/test_apply_lessons_delta.py` | cap test **rewritten**, legacy-tolerance test added, 6 header fixtures migrated |
| `skills/workbench/templates/LESSONS.template.md` | seeded-header twin: literal `cap=20` + "Hard cap … (default 20)" rule replaced with the Curator's-cleanup retention story |

`git diff --stat`: 3 files, 92 insertions, 41 deletions.
`git check-ignore` exits 1 (not ignored) on all three — all committed paths.

The 8 removal sites in the writer, each verified by running the writer, never by reading the diff:
`DEFAULT_CAP` const · `STATE_RE` capture group · `Playbook.cap` field · `load_playbook` unpack ·
`Playbook(...)` construction · `render_playbook` header rewrite · the add-refusal branch ·
the seeded preamble (header + prose) · the summary line.

**Enumeration, derived by command not by reading.** `git grep -nI 'Playbook('` over `scripts/ tests/`
returns **1** — the writer constructs it in exactly one place. `git grep -nIE '\.cap\b'` over the same
returns **4**, all inside the writer. So removing the field breaks no caller. That is the whole call-site
population, not a sample.

## Test mode satisfied

Test-after with a mandatory rewrite. `test_cap_enforced_and_retire_before_add` was **rewritten, never
deleted**, as `test_add_past_twenty_succeeds_and_retire_still_deletes`. It performs the exact op the cap
refused (an add at 20/20), asserts it succeeds, then continues to 26 entries so a wall that merely moved
one entry out would still fail it, asserts `hasattr(book, "cap")` is False and that no `cap=` survives in
the rendered file, and keeps the retire-and-delete coverage that outlived its cap rationale. Added
`test_legacy_cap_header_parses_and_is_dropped_on_render`.

## Evidence

### 1. `cap_is_gone.py` — RED at HEAD, GREEN after

RED, at unmodified HEAD `752a62f`, **before any edit**:

```
$ python .agent-work/issue-308/checks/cap_is_gone.py
FAIL: the cap still refuses the add at 20 entries:
error: add cap-removal-behavioural-check: active cap 20 reached — retire before adding
EXIT=1
```

GREEN, after:

```
$ python .agent-work/issue-308/checks/cap_is_gone.py
PASS: add accepted at 20 active entries — the cap is gone
EXIT=0
```

The check reaches the cap branch in the red arm, so its green arm is meaningful — it is not a check that
cannot fail.

### 2. The replacement test, red-proved

Red-proved by swapping the **HEAD writer snapshot** back in from scratch (`cmp`-verified restore
afterward; `git checkout` was NOT used, per the handoff). The mutation was asserted applied
(`grep -c 'DEFAULT_CAP = 20'` → 1) before the run.

```
$ python -m pytest tests/test_apply_lessons_delta.py -q      # NEW tests vs PRE-CHANGE writer
11 failed, 59 passed in 1.41s
PYTEST_EXIT=1

FAILED …::test_add_past_twenty_succeeds_and_retire_still_deletes
E   AssertionError: 1 != 0
error: add lesson-20: active cap 20 reached — retire before adding

FAILED …::test_legacy_cap_header_parses_and_is_dropped_on_render
>       self.assertFalse(hasattr(book, "cap"))
E       AssertionError: True is not false
```

The headline test fails on the **exact old refusal**, not on incidental breakage. The other 9 failures are
the migrated header fixtures rejected by the old cap-requiring regex — which independently confirms the
fixtures really moved to the new grammar rather than being left dual-compatible.

Restore verified byte-identical (`cmp -s` → YES), then GREEN:

```
$ python -m pytest tests/test_apply_lessons_delta.py -q
70 passed in 1.22s
```

### 3. Full suite

```
$ python -m pytest -q
1621 passed, 2 skipped, 543 subtests passed in 417.61s (0:06:57)
PYTEST_EXIT=0
```

Run twice — before and after the template change — with **identical counts**, so the template edit broke
nothing. Nothing outside `test_apply_lessons_delta.py` was pinned to cap behaviour; the suite proved that,
it was not guessed. No `FAILED` distribution to report because there were no failures.

### 4. The removal is not a rename

```
$ ! grep -nE 'DEFAULT_CAP|active cap' scripts/apply_lessons_delta.py
EXIT=0
```

The only `cap` tokens left in the writer are the tolerance comment, the tolerated non-capturing regex
group, and the prose sentence that explicitly says there is no cap.

### 5. Legacy header tolerance, driven through the real writer

```
IN  (legacy): <!-- playbook-state: run-tick=40 cap=20 dormancy-runs=10 apply-recurrences=1 … -->
added lesson:rt-probe
playbook: 21 active (run 40)
EXIT=0
OUT: <!-- playbook-state: run-tick=40 dormancy-runs=10 apply-recurrences=1 … -->     # cap= dropped

# re-apply to the now-migrated header
added lesson:rt-probe-2
playbook: 22 active (run 40)
EXIT=0
```

Legacy accepted → discarded on write → the migrated header re-parses. Bank went to 21 then 22, both past
the old wall. Every other header field (`run-tick`, `dormancy-runs`, `apply-*`, the 20-entry
`ticked-work-ids` ring) survived intact.

### 6. Residual-claim sweep, derived by command

Live `cap=[0-9]` in tracked `scripts/ tests/ skills/ docs/`: **13 → 8**. The 8 survivors, all accounted for:

- **4** — `tests/test_checklist_engine.py`, the engine's unrelated **rework cap** (`gated(cap=3)`). Different concept.
- **3** — quoted headers inside `docs/superpowers/plans/2026-06-2{4,7}-*.md`, dated historical design records. Rewriting them would falsify the archive.
- **1** — `tests/test_apply_lessons_delta.py:169`, the deliberate legacy-tolerance fixture.

**Zero** surviving claim reads as an enforced lessons-playbook limit.

## Decisions the handoff did not settle

**(a) `skills/workbench/templates/LESSONS.template.md` — fixed, though the suite did not prove it pinned.**
The handoff's Allowed Scope admits other docs only when "the suite proves [them] pinned"; the suite proved
nothing else pinned. But the Close Criteria independently forbid any residual `cap=<N>` claim that reads as
enforced and explicitly name "the seeded header". This template *is* the seeded header in template form —
the twin of `_default_preamble()` — and it carried a literal `cap=20` plus the rule "Hard cap on Active
lessons (default 20); beyond it, retire before adding" attributed to the apply script. Leaving it would
hand the **next** project a stale enforced claim on day one, which is the exact defect class this gate
exists to remove. I judged the Close Criterion the controlling one. Full suite re-run after the change,
counts identical.

**(b) `.agent-work/LESSONS.md` — deliberately NOT mutated.** Permitted by the handoff, not required, and I
declined for three grounded reasons, all measured on a scratch copy rather than asserted:

1. Every write path mutates state that is g4's. There is no no-op write: the writer demands ops or `tick`.
   A bare `tick` on the copy moved `run-tick` 40→41, appended to the dedup ring, and incremented
   `runs-since-confirmed` on all 20 lessons — aging the entire bank one step toward auto-deletion
   immediately before g4's migration reads it. "Do not empty, delete, or migrate any lesson content" is a
   g3 exclusion.
2. The stale header fixes itself. Writing the copy through the real writer dropped `cap=20` from the state
   marker mechanically. g4's own migration write will do the same.
3. The more visible claim is unreachable anyway. `.agent-work/LESSONS.md:8` says the script "enforces cap,
   grounding, and counter rules" — that sentence lives in `book.preamble`, which the writer preserves
   **verbatim** (only `STATE_RE.sub` touches it); `_default_preamble()` seeds new files only. So no delta
   can rewrite it and hand-editing is forbidden. Writing the file would have aged the store while leaving
   the worse claim standing — strictly worse than not writing it. Filed as tc3.

## Triage candidates (in the plan's `triage_candidates`)

- **tc1** — `skills/lessons-auditor/SKILL.md:10` still reads "Reaching the cap is a failure signal". Stale, but the auditor is **explicitly excluded** from g3 (g4/g5 territory). Left untouched on purpose; g4 should sweep it.
- **tc2** — `docs/EPISODE_STORE.md:246-248` asserts `LESSONS.md` "needs … counters and a cap to keep the bank from growing unbounded". Now false. It is a live contract doc, but carries no literal `cap=N` and the suite does not pin it, so it sat outside g3's doc scope.
- **tc3** — `.agent-work/LESSONS.md:8` preamble prose is unreachable through the only sanctioned write path (see (b)3). Needs a g4 ruling or a writer capability, not a hand-edit.

## Out-of-scope observations

- `docs/CONSTELLATION_OVERVIEW.md:104` **already** tells the removal story in the past tense with the #308
  measurement. An earlier gate got there first; no change needed, and it confirms the intended retention
  story is "regular curator cleanup", which is the wording I used in the writer and the template.
- `docs/RECURSIVE_IMPROVEMENT_DESIGN.md:414` says "hard cap (start 15–20, enforced by the apply script)".
  Left alone: its own header reads "Status: draft for discussion · 2026-06-10" — a dated proposal record,
  same archive class as `docs/superpowers/plans/`. Editing it would falsify history rather than fix a claim.

## Stop conditions hit

None. The cap came out without breaking any existing lessons file, nothing outside the allowed scope was
pinned in a way needing a design call, the header field came out without touching the episode store or the
auditor, and the red-before-green proof was produced for both the acceptance check and the replacement test.

## Workflow feedback

1. **The Allowed Scope and the Close Criteria disagreed, and nothing said which wins.** Allowed Scope gated
   other docs on "the suite proves it pinned"; the Close Criteria said no enforced-reading `cap=<N>` may
   survive "anywhere". For `LESSONS.template.md` those point opposite ways — the suite does not pin it, yet
   it carries the literal claim. I ruled for the Close Criterion and said so. A handoff that names a
   criterion broader than its own scope list should say which is controlling.
2. **"Write `.agent-work/LESSONS.md`'s header prose through the writer" is not a thing the writer can do.**
   The permission assumes a capability that does not exist: the writer substitutes only the state marker and
   preserves preamble prose verbatim. It also assumes a write can be side-effect-free, when the cheapest
   available write ages the whole dormancy clock. Worth correcting before another gate inherits the same
   instruction.
3. **The `Test Mode` field asked for a rewrite whose red-proof needs a writer swap, and the constraints
   separately banned `git checkout`** — those belong together. The workable recipe (snapshot to scratch →
   swap → assert the mutation applied → run → restore → `cmp`-verify) had to be assembled from two
   distant sections. Naming it once in the handoff would remove the guesswork.
4. Everything else — the frozen fixture, the non-grep acceptance check, the `python`-not-`py` warning, the
   single-quote-your-grep note — was accurate and load-bearing. The acceptance check in particular was well
   built: it refuses to report a pass when the add is rejected for a non-cap reason, which is what let me
   trust the green arm.

## Map impact

Low. No structural or seam change: one module's interface lost a field and a refusal, with no caller
outside itself (1 construction site, 4 attribute reads, all internal). The durable change is a **constraint
removal** — "the lessons bank enforces a 20-entry ceiling" is no longer true of `apply_lessons_delta.py` —
and a **decision**: retention moved from a writer-enforced number to the Curator's periodic cleanup pass
(`decision:no-cap-replacement-by-hygiene`). Any map text asserting a bounded/capped playbook is now stale.
