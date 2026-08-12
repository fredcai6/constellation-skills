# Implementation Result — Rework 1

## Assigned gate
`g3-implement` (issue #300, epic-298), rework round 1 against `.agent-work/300/g3-review/REVIEW_RESULT.md` (verdict BLOCK, 2 blockers).

## Completed slice
Fixed both blockers named in `.agent-work/300/g3-implement/REWORK-1.md`. Nothing else was touched — the
original handoff's scope-clean deliverables (protected prose, shape test, obligations statement) are
unmodified.

### Fix 1 — B1: the lint's stated direction was inverted, in four places

The predicate (`every declared path must appear inside its task's imperative`) actually catches only
**declaration ⊄ prose** (a declared path the prose never mentions). It **cannot** catch **prose ⊄
declaration** ("narrowing" — a path quietly dropped from the declaration while the prose still names
it). The shipped docstring, doc section, and fixture readme all described the guarantee as running the
other way. Corrected all four places the review named:

1. `scripts/verify_context_declaration.py` module docstring — replaced the "catches narrowing away"
   claim with the real one ("catches the declaration naming a path its own prose never mentions... CANNOT
   catch the reverse — a path quietly dropped from `context_refs` while the prose still names it").
   Also added one clarifying sentence noting "verbatim" means a whole path token, not a substring of a
   longer path (ties into fix 2).
2. `docs/CHECKLIST_ENGINE_DESIGN.md`'s `#300` narrative section — replaced the same inverted sentence,
   and removed the false "stated honestly ... rather than oversold" endorsement (the doc no longer
   vouches for the docstring's honesty as a separate claim; it just states the same, now-correct, limit
   in the same terms).
3. `tests/fixtures/context_declaration_lint.json`'s `_readme` — corrected the `divergent` fixture's
   description (it is "a declaration pointing somewhere its own prose never covers," not "narrowing")
   and reattributed the "narrowing" language to the `prose_names_more_than_declared` fixture, where it
   actually belongs.
4. Added `test_narrowed_declaration_is_deliberately_not_caught` to
   `tests/test_context_declaration_lint.py` (`CliTests`) — a characterization test asserting `main()`
   exits **0** on the `prose_names_more_than_declared` fixture (a path dropped from the declaration while
   the prose still names it), with a comment stating this is the lint's known, documented blind spot. This
   pins the boundary mechanically instead of leaving it restated only in prose that can drift again.

### Fix 2 — B2: substring containment replaced with path-boundary matching

`verify_context_declaration.py` used `if path not in prose`, so a declared `agents/GLOSSARY.md` passed
clean against prose naming only the longer, different path `docs/agents/GLOSSARY.md`. Fixed with a
leading-path-boundary check:

```python
_PATH_CHAR = re.compile(r"[A-Za-z0-9_./\\-]")

def _appears_at_path_boundary(path: str, prose: str) -> bool:
    start = 0
    while True:
        idx = prose.find(path, start)
        if idx == -1:
            return False
        if idx == 0 or not _PATH_CHAR.match(prose[idx - 1]):
            return True
        start = idx + 1
```

`offenders_in_task` now calls `_appears_at_path_boundary(path, prose)` instead of `path not in prose`. A
match counts only when the character immediately preceding the occurrence is not itself a path
character — so a match is rejected when it is merely a suffix of a longer, different path, and accepted
at start-of-string or after whitespace, a backtick, `(`, or a quote (the shapes the real shipped prose
actually uses).

Added two fixtures to `tests/fixtures/context_declaration_lint.json` plus two tests in
`tests/test_context_declaration_lint.py`:

- `boundary_suffix_rejected` / `test_suffix_of_a_longer_path_is_rejected` — declared `agents/GLOSSARY.md`
  vs. prose naming only `docs/agents/GLOSSARY.md`; must FAIL, and does.
- `boundary_legitimate_occurrences_accepted` / `test_legitimate_boundary_occurrences_are_accepted` — five
  declared paths, each occurring at a different legitimate boundary (start-of-string, whitespace,
  backtick, `(`, quote); all must PASS, and do.

**Mandatory regression check** — `skills/commander/templates/COMMANDER_SPINE.template.json` (untouched,
its prose wraps declared paths in backticks and parens) still lints clean after the boundary change:
`python scripts/verify_context_declaration.py skills/commander/templates/COMMANDER_SPINE.template.json`
→ `context declaration lint ok: 1 checklist(s) checked, 0 offenders`, exit 0.

## Scope
**Files changed:**
- `scripts/verify_context_declaration.py` (new file, edited further this round — docstring + `_appears_at_path_boundary` + `offenders_in_task`)
- `tests/test_context_declaration_lint.py` (new file, edited further this round — 3 new tests)
- `tests/fixtures/context_declaration_lint.json` (new file, edited further this round — `_readme` fixed, 2 new fixtures added)
- `docs/CHECKLIST_ENGINE_DESIGN.md` (edited — corrected the `#300` section's direction claim)

**Untouched, confirmed byte-identical to before rework** (per REWORK-1.md's "leave alone" list):
`skills/commander/templates/COMMANDER_SPINE.template.json`, `scripts/context_manifest.py`,
`scripts/checklist_engine.py`, `scripts/verify_skip_guard.py`, `docs/CHECKLIST_SCHEMA.md`,
`tests/test_context_manifest.py`, `.agent-work/300/OBLIGATIONS-301.md`.

**Specific exclusions touched:** no.

## Behavior changed
Yes: `scripts/verify_context_declaration.py` now rejects a declared path that only matches as a suffix
of a longer, different prose path (previously a silent pass). The lint's stated guarantee (docstring +
design doc + fixture readme) now matches what the code actually does; no behavior change from the
narrative correction itself.

## Test mode
**Required:** test-first (characterization/regression tests for both blockers).
**Satisfied:** yes — both fixes are pinned by tests that fail without the fix and pass with it (verified
by the before/after transcript below for B2; B1's characterization test is new so there is no
pre-existing failing state to show, but it directly encodes the corrected direction and would fail if the
lint's actual behavior regressed to catching the wrong direction).

## Evidence — B2 before/after transcript (required by REWORK-1.md)

**BEFORE** (pre-fix code, bare `if path not in prose`), against a scratch fixture with declared
`agents/GLOSSARY.md` and prose naming only `docs/agents/GLOSSARY.md`:

```
$ python scripts/verify_context_declaration.py .agent-work/300/g3-implement/scratch/suffix_before.json
context declaration lint ok: 1 checklist(s) checked, 0 offenders
exit=0
```

**AFTER** (post-fix code, `_appears_at_path_boundary`), same fixture, unchanged:

```
$ python scripts/verify_context_declaration.py .agent-work/300/g3-implement/scratch/suffix_before.json
context_refs declaration diverges from imperative prose:
  - .agent-work\300\g3-implement\scratch\suffix_before.json: task 'context' declares context_refs path 'agents/GLOSSARY.md' that does not appear verbatim in its own imperative prose
exit=1
```

Confirms the fixture flips 0 → 1 across the change, for the actual offending path. (Scratch file was a
throwaway probe outside allowed scope and was deleted after use; the same case is now permanently pinned
as `boundary_suffix_rejected` / `test_suffix_of_a_longer_path_is_rejected` in the committed fixture/test
files.)

## Evidence — full invariant chain (REWORK-1.md, run in order, this session)

```bash
$ python -m pytest tests/test_context_declaration_lint.py -q
............                                                             [100%]
12 passed in 0.16s
exit=0

$ python -m pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected -q
.                                                                        [100%]
1 passed in 0.14s
exit=0

$ python scripts/verify_context_declaration.py skills/commander/templates/COMMANDER_SPINE.template.json
context declaration lint ok: 1 checklist(s) checked, 0 offenders
exit=0

$ python -m pytest tests/ -q --junitxml=junit-report.xml
1224 passed, 2 skipped, 329 subtests passed in 33.79s
exit=0

$ python scripts/verify_skip_guard.py junit-report.xml
skip guard ok: 2 skip(s) in report, all match documented allow-tuples
exit=0

$ rm -f junit-report.xml
exit=0
```

(Full-suite count is 1224 passed vs. the review's previously-recorded 1221 — the +3 delta is exactly the
three new tests added this round: the B1 characterization test and the two B2 boundary tests. Skip count
unchanged at 2, still matching the documented allow-tuples — no new `skipTest` introduced.)

## Docs/contracts touched
- `docs/CHECKLIST_ENGINE_DESIGN.md` — corrected the `#300` section's direction claim (see Fix 1, item 2).

## Assumptions
- The characterization test required by B1 ("a narrowed declaration is deliberately not caught") is
  satisfied by reusing the existing `prose_names_more_than_declared` fixture at the CLI (`main()`) level,
  rather than authoring a new fixture — that fixture already encodes exactly this scenario (a path in the
  declaration is missing while the prose still names it); only its framing was wrong, not its shape. The
  existing unittest-level test on the same fixture (`test_prose_naming_more_than_declared_is_not_flagged`)
  was left in place since it independently exercises `check_checklist` directly.
- B2's fix is a leading-boundary check only (not preceded by a path character), matching REWORK-1.md's
  fix description exactly. The review's "prefix direction" example (declared `references/global-everyone.md`
  passing against prose naming only `references/global-everyone.md.bak`) is a *trailing*-boundary gap that
  REWORK-1.md's fix instructions do not ask to close (its required fixture list names only the suffix case,
  start-of-string, whitespace/backtick, and paren/quote — no trailing-overrun fixture). Not fixed this
  round since it is outside what REWORK-1.md specified; flagged below as a triage candidate rather than
  silently left unaddressed.

## Stop conditions hit
None.

## Out-of-scope observations
- **Trailing-boundary gap, not closed this round.** A declared path that is a strict *prefix* of a longer
  prose path (e.g. declared `references/global-everyone.md` vs. prose `references/global-everyone.md.bak`)
  still passes, because the fix implemented is a leading-boundary check only, per REWORK-1.md's explicit
  fix description and fixture list. Closing it would need a trailing check (character immediately after
  the match must also not be a path character) plus one more fixture/test. Cheap, same shape as this
  round's fix — worth a follow-up if this matters in practice.
- Everything the prior `REVIEW_RESULT.md` marked as observations (1–5) and triage candidates (CI wiring)
  is unchanged and out of this rework's scope per REWORK-1.md ("Do not re-litigate what passed").

## Workflow Feedback
- **Handoff gaps:** none this round — REWORK-1.md was precise: predicate stated in set terms
  ("declaration ⊄ prose is caught; prose ⊄ declaration is invisible"), fix described down to the regex
  character class, and the exact fixture list to add. No ambiguity encountered.
- **Context rediscovered:** none — REVIEW_RESULT.md's reproduction commands and REWORK-1.md's fix
  description were sufficient without re-deriving anything from `scripts/context_manifest.py` or the
  spine template.
- **Instructions improvised around:** the B1 "characterization test" instruction didn't specify whether to
  add a wholly new fixture or reuse an existing one; I reused `prose_names_more_than_declared` at the CLI
  level (see Assumptions) since it already had the right shape and adding a near-duplicate fixture would
  have been pure duplication.
- **What would have made this easier:** none — this rework note was unusually precise (it named exact
  line ranges, exact fixture requirements, and the exact predicate in set-notation). Nothing to improve.

## Return status
`complete`

---

## Addendum — trailing boundary (commander-300, post-verification)

Commander-300 independently verified both fixes above, then reproduced the trailing half of the same
defect class live (declared `docs/agents/GLOSSARY.md`, prose only naming `docs/agents/GLOSSARY.md.bak`
→ exit 0) and asked for `_appears_at_path_boundary()` to be made symmetric — bounded at both ends, not
leading-only — closing the gap flagged as an out-of-scope observation above. Scope: that one change,
plus fixtures/tests and re-verification; nothing else revisited.

### Fix — symmetric (trailing) path-boundary matching

Added `_bounded_after(prose, end)` to `scripts/verify_context_declaration.py` and made
`_appears_at_path_boundary` require both `leading_ok` and `trailing_ok` before accepting a match:

```python
_TRAILING_CONTINUATION_CHAR = re.compile(r"[A-Za-z0-9_/\\-]")

def _bounded_after(prose: str, end: int) -> bool:
    if end >= len(prose):
        return True
    ch = prose[end]
    if ch == ".":
        nxt = prose[end + 1] if end + 1 < len(prose) else ""
        return not nxt.isalnum()
    return not _TRAILING_CONTINUATION_CHAR.match(ch)
```

`.` is deliberately excluded from the ordinary trailing-continuation class and handled separately,
because it is genuinely ambiguous on its own: `GLOSSARY.md` followed by `.` could be an extension
continuing the path (`GLOSSARY.md` + `.bak`) or a sentence-ending period (`GLOSSARY.md` + `. Attest
c1.`). The rule looks one character further: `.` followed by an alphanumeric character is treated as an
extension glued onto the match (reject); `.` followed by anything else, or nothing, is ordinary
punctuation (accept). This is exactly what let the shipped spine template's own paths — several of which
end a sentence at a `.` — keep passing while `GLOSSARY.md.bak` correctly fails.

Added two fixtures to `tests/fixtures/context_declaration_lint.json` plus two tests in
`tests/test_context_declaration_lint.py`:

- `boundary_trailing_rejected` / `test_trailing_extension_glued_to_a_shorter_path_is_rejected` — declared
  `docs/agents/GLOSSARY.md` vs. prose naming only `docs/agents/GLOSSARY.md.bak`; must FAIL, and does.
- `boundary_trailing_legitimate_accepted` / `test_legitimate_trailing_occurrences_are_accepted` — five
  declared paths, each immediately followed by a different legitimate trailing boundary (sentence-ending
  period, comma, closing backtick, closing paren, end-of-string); all must PASS, and do.

### Evidence — trailing before/after transcript

**BEFORE** (leading-boundary-only code from the main rework), against a scratch fixture with declared
`docs/agents/GLOSSARY.md` and prose naming only `docs/agents/GLOSSARY.md.bak`:

```
$ python scripts/verify_context_declaration.py .agent-work/300/g3-implement/scratch/trailing_before.json
context declaration lint ok: 1 checklist(s) checked, 0 offenders
exit=0
```

**AFTER** (symmetric boundary fix), same fixture, unchanged:

```
$ python scripts/verify_context_declaration.py .agent-work/300/g3-implement/scratch/trailing_before.json
context_refs declaration diverges from imperative prose:
  - .agent-work\300\g3-implement\scratch\trailing_before.json: task 'context' declares context_refs path 'docs/agents/GLOSSARY.md' that does not appear verbatim in its own imperative prose
exit=1
```

Confirms the trailing fixture flips 0 → 1 across the change, for the actual offending path. The scratch
fixture was a throwaway probe outside allowed scope and was deleted after use; the same case is now
permanently pinned as `boundary_trailing_rejected` / `test_trailing_extension_glued_to_a_shorter_path_is_rejected`
in the committed fixture/test files.

### Evidence — re-run checks (this addendum)

```bash
$ python -m pytest tests/test_context_declaration_lint.py -q
..............                                                          [100%]
14 passed in 0.17s
exit=0

$ python scripts/verify_context_declaration.py skills/commander/templates/COMMANDER_SPINE.template.json
context declaration lint ok: 1 checklist(s) checked, 0 offenders
exit=0

$ python -m pytest tests/ -q --junitxml=junit-report.xml
1226 passed, 2 skipped, 329 subtests passed in 39.03s
exit=0

$ python scripts/verify_skip_guard.py junit-report.xml
skip guard ok: 2 skip(s) in report, all match documented allow-tuples
exit=0

$ rm -f junit-report.xml
exit=0
```

(1226 passed vs. this file's earlier 1224 — the +2 delta is exactly the two new trailing-boundary tests.
Skip count unchanged at 2, still matching the documented allow-tuples — no new `skipTest` introduced.)

### Scope for this addendum

**Files touched, same set as the main rework** (no new files added): `scripts/verify_context_declaration.py`,
`tests/test_context_declaration_lint.py`, `tests/fixtures/context_declaration_lint.json`. Nothing else
revisited — the B1 direction fix, the obligations statement, the shape test, and the protected prose are
unchanged since the main rework's `IMPLEMENTER_RESULT-rework1.md` content above.

### Out-of-scope observations — resolved

The "Trailing-boundary gap, not closed this round" observation above is now closed by this addendum.

### Return status (addendum)
`complete`

---

## ADDENDUM (Commander-300, closing reviewer finding F1)

**This document above describes a superseded, leading-only predicate. Read this section as the
authoritative account of what actually shipped.** The staleness is my doing, not the implementer's:
after the crew correctly delivered exactly the leading-boundary fix REWORK-1.md specified — and
correctly flagged the trailing half as still open rather than gold-plating — I judged that stopping
at one end was arbitrary and resumed it to extend the scope. The plan addendum recorded the work;
this narrative did not.

**What shipped, superseding three statements above:**

1. `_appears_at_path_boundary` is **symmetric**, not leading-only. It has a trailing companion, so a
   declared path that is a strict *prefix* of a longer path in the prose is also rejected.
2. The *Assumptions* line "B2's fix is a leading-boundary check only" is **false** against the
   shipped file.
3. The *Out-of-scope observations* entry describing the trailing gap as still open and "worth a
   follow-up if this matters in practice" is **false and must not be cut into an issue** — that work
   is done. This is precisely the harvest hazard the reviewer flagged: an Admiral reading the stale
   text would have filed a follow-up for completed work and understated what landed.
4. The full-suite figure **1224 is stale**. The correct figure is **1226 passed, 2 allowlisted
   skips**, `verify_skip_guard.py` exit 0 — independently measured by the Commander and matched by
   the reviewer.

**Verified in the Commander's own hands after the extension:** the trailing fixture
(declared `docs/agents/GLOSSARY.md`, prose naming only `docs/agents/GLOSSARY.md.bak`) exits **1**
where it exited 0 before; the leading suffix fixture exits **1**; the narrowing case exits **0** as
deliberately-uncaught and is pinned by a characterization test; and the shipped
`COMMANDER_SPINE.template.json` still lints clean with 0 offenders — the regression check that
constrained the rule's design, since several of its declared paths end a sentence.

**Still genuinely open, carried to the triage step (not defects that should hold #300):** tighten the
trailing rule from a path-character deny-list to a punctuation allow-list; document the unchecked
`root` token as a second blind spot in the lint docstring; and wire the lint into CI, which nothing
currently does.
