# Review Result — #447 gate g1 (the retirement guard)

**Verdict: BLOCK**

**Reviewed:** `scripts/verify_retirement.py`, `tests/test_retirement_guard.py`,
`tests/data/store_mentions.approved.txt` (three new files, nothing else touched).
**Worktree:** `C:/Programs/constellation-skills-wt/epic418-h-447` · branch `epic-418/h-447-episodes-retirement`
**Survey:** `.agent-work/epic418-h-447/g1-review/review.json` · **Fowler record:** `.agent-work/epic418-h-447/g1-review/fowler-pass.json`

All evidence below was re-run by me. I did not read the implementer's transcript for any of it.

---

## What is genuinely good, and measured

The central worry going in was a check that cannot fail. **It is not that.** I built my own
baseline repository — not the shipped `healthy_repo` fixture — and planted one violation per leg
using *different* plants than the shipped decoys use. Every leg fired, alone, with the right path:

```
BASELINE (expect clean)                        distinct legs: []
leg retired-path-still-tracked                 ['retired-path-still-tracked']  -> scripts/verify_agent_feedback.py
leg unapproved-store-mention                   ['unapproved-store-mention']    -> docs/ops.md
leg replacement-absent (bundle half only)      ['replacement-absent']          -> scripts/install_constellation.py
leg retired-name-on-shipped-surface            ['retired-name-on-shipped-surface'] -> docs/ops.md
```

The shipped decoys are testing what they claim. The `falsify-against-a-decoy` lesson is satisfied.

Required evidence reproduced:

```
$ python scripts/verify_retirement.py > guard-out.txt; echo EXIT=$?
EXIT=1
$ cut -f1 guard-out.txt | sort | uniq -c
      5 replacement-absent
    121 retired-name-on-shipped-surface
      5 retired-path-still-tracked
$ python -m pytest tests/test_retirement_guard.py -q
8 passed, 1 xfailed in 1.58s
$ python -m pytest -q
1696 passed, 2 skipped, 1 xfailed, 550 subtests passed in 434.19s
```

Baseline was 1688 passed, 2 skipped → **+8 passed, +1 xfailed, no new failures.**

**Criterion 4 (strict xfail) passes.** I forced the clean-tree condition with a pytest plugin that
replaces `vr.scan` with `lambda root: []`:

```
$ PYTHONPATH=... python -m pytest tests/test_retirement_guard.py -q -k canon -p xpass_plugin
FAILED tests/test_retirement_guard.py::test_canon_is_clean - [XPASS(strict)] ...
1 failed, 8 deselected
```

The scaffolding really does break the build when the tree goes clean. The mechanism is correct.
Finding 1 is that the condition can never be reached.

**Criterion 5 (approval census) passes.** 18 entries, every one verbatim at its stated path, every
one carrying a reason, no duplicates, zero entries under `skills/`. No stale entry widens the guard.

**Criterion 6 (scope) passes.** `git status --porcelain` shows exactly the three allowed files plus
the `.agent-work/` workbench. No skill, spine, doc or existing script was edited.

---

## Findings

### 1. BLOCKING — the guard fires on its own source once committed, so the tree can never go clean

The guard's own definition literals live in `scripts/verify_retirement.py`, which is **on the shipped
surface**. Right now the file is untracked, so `git ls-files` never shows it to `scan()`. The moment
Commander commits — the entire point of this gate — the guard starts reporting itself.

Measured with the three deliverables staged into a throwaway index (the real index untouched):

```
$ git add scripts/verify_retirement.py tests/test_retirement_guard.py tests/data/store_mentions.approved.txt
$ python scripts/verify_retirement.py > guard-tracked.txt; echo EXIT=$?
EXIT=1
$ cut -f1 guard-tracked.txt | sort | uniq -c
      5 replacement-absent
    133 retired-name-on-shipped-surface     <- was 121
      5 retired-path-still-tracked
      6 unapproved-store-mention            <- was 0

$ grep verify_retirement.py guard-tracked.txt | cut -f1,2,3
retired-name-on-shipped-surface  scripts/verify_retirement.py  92,97,98,99,100,101,108,109,110,111,112,113
unapproved-store-mention         scripts/verify_retirement.py  126,194,292,298,299,311
```

Those are exactly `RETIRED_PATHS` (:96-102), `RETIRED_NAMES` (:107-114), `STORE_MENTION_PATTERNS`
(:292) and `STORE_OWN_FILES` (:297-301) — the constants that *define* the guard.

Three documented properties are false in the committed state:

| claimed | committed reality |
|---|---|
| `unapproved-store-mention` is "GREEN by construction" (result design table; census header) | fires 6 times |
| "3 distinct legs" on the untouched tree | 4 legs |
| `test_canon_is_clean` goes clean at g6 and strict XPASS forces the marker off | can never go clean; the marker outlives the work |

The consequence is the one #403 exists to prevent. At g6 the retirement will be complete and the guard
will still report 18 self-violations, so the acceptance surface never turns over. The pressure at that
point will be to approve the guard's own lines into the census or add a broad exclusion — which is the
silent widening this design is built to stop.

The module *states* the correct principle and applies it to the wrong directory. The test docstring
(`tests/test_retirement_guard.py:10-16`) says "a guard cannot be inside the set it guards without
either weakening itself or making its own test unwritable" — and draws the boundary at `tests/`. But
the guard's definition is in `scripts/`, inside the guarded set. The handoff's phrase "the guard file
itself must contain the forbidden strings" was about the test module; it was inherited without
checking whether the scanner had the same problem.

**The fix is one entry, and I verified it resolves the defect exactly:**

```
$ # add scripts/verify_retirement.py to SCOPE_EXCLUSIONS with a reason
AS BUILT (committed):        {'retired-name': 133, 'retired-path': 5, 'replacement-absent': 5, 'unapproved-store-mention': 6}
WITH the guard self-excluded: {'retired-name': 121, 'retired-path': 5, 'replacement-absent': 5}
```

That restores 131 violations across the 3 intended legs and the store-mention leg green by
construction — the state the gate's evidence describes. Re-capture `g1-guard-red.txt` **with the three
files staged**, since the current transcript is pinned to a state the repo leaves at integrate.

### 2. ADVISORY (with teeth) — the `notes-*.md` exclusion reaches more than twice as far as its own reason says

This is the judgement call I was asked to rule on. **The exclusion is defensible in kind; its stated
reach is wrong, and its form is unbounded.**

Defensible: root-level run notes genuinely are the same class as `docs/superpowers/` — records of what
a past issue found, not instructions. The implementer put it in a separate `SCOPE_EXCLUSIONS` constant
so the handoff's four roots stay recognisable, gave it a reason string, commented it at the code site,
and reported it up for a Commander ruling. That is the scope-discipline ruling followed correctly, and
it is not a silent widening. The 37 → 18 arithmetic is honest — I reproduced both numbers.

Wrong: the comment at `scripts/verify_retirement.py:141-143` and the result both name **three** files
(`notes-304/308/309.md`). Measured by command, the glob removes **seven** tracked files:

```
$ python -c "...fnmatch over git ls-files..."
tracked root notes-*.md: ['notes-261.md','notes-269.md','notes-301.md','notes-304.md','notes-308.md','notes-309.md','notes-b420.md']
store-mention lines inside notes-*.md: 19
census size with notes ON surface: 37   with notes excluded: 18
```

— plus every future root-level `notes-*.md`, unbounded. `global-everyone.md` requires enumerating the
blast radius **by command** and stating the count; the count stated is 3, the real count is 7 and
growing. And a glob that auto-absorbs future files is the wrong shape here specifically, because the
retired playbook occupied exactly that class of surface (see finding 3, case C).

**Ruling: keep the exclusion, narrow it to an explicit enumeration of the seven tracked files (or move
run notes under a directory), and correct the comment's count.** Not blocking on its own.

### 3. ADVISORY — five realistic edits reintroduce the retired behaviour and the guard misses them

Each planted in an independent baseline repo, with a working control:

```
MISSED  | A: skills/lessons-auditor/SKILL.md re-added, content never self-names
MISSED  | B: docs/guide.md says 'read .agent-work/lessons.md' (lowercase)
MISSED  | C: notes-999.md at root prescribes reading LESSONS.md and episodes/
MISSED  | D: docs/guide.md holds the retired name in latin-1 bytes
MISSED  | E: prescription split so no ONE line spells the retired name
CAUGHT  | F: CONTROL docs/guide.md single line naming LESSONS.md
```

**A is the serious one, because the code claims otherwise.** The comment at
`scripts/verify_retirement.py:106-107` says the bare substrings catch a mention "whether it arrives as
a path, a prose reference, a bundle entry or **a skill directory**." `_leg_retired_name` (:262) only
ever reads line *content* — it never tests the path string. `lessons-auditor` is in `RETIRED_NAMES`
specifically for the skill-directory case, and the skill directory is the one thing it cannot see. A
commander re-adding the retired auditor skill walks straight through. Fix is one line: also test
`path` against `RETIRED_NAMES`.

**C** is finding 2 made concrete — the glob is a live door, not a theoretical one.

**D is a doctrine breach, not just a gap.** `_read_lines` (:212) returns `None` on
`UnicodeDecodeError`/`OSError` and both content legs `continue` silently. An undecodable shipped file
is an unscanned shipped file and the guard says nothing — against `global-everyone.md` §Universal
posture, "fail visibly rather than emit plausible wrong output; no hidden fallback." The same file in
UTF-8 is caught. Emit a violation or a distinct diagnostic instead of skipping.

**B** (case sensitivity) and **E** (line splitting) are cheaper to accept; B is worth a
`.lower()` comparison, E is not worth chasing.

The two limits the dispatch already knew about — a successor playbook that never names episodes, and
prescriptions inside `workaround` statements — I confirm are real and out of reach of this design.

### 4. ADVISORY — Fowler pass: three flagged smells

Full record at `.agent-work/epic418-h-447/g1-review/fowler-pass.json`; `verify_fowler_pass.py` exits 0.
All 12 baseline smells ruled; `long-method`, `speculative-generality` and `comments-as-deodorant`
overridden with logged standards (the mandated verbatim discriminator text, the `--root` test seam, and
the epic-418 requirement that un-chased corner cases carry a comment at the code site).

- **duplicated-code** — `RETIRED_PATHS` (:96) and `RETIRED_NAMES` (:107) restate the same retirement
  facts; 3 of 5 paths have their basename repeated, the other 2 are basenames. A future retirement that
  adds a path and forgets the name loses the content leg for it, and nothing tests the overlap.
- **primitive-obsession** — `is_shipped` (:168) infers the matching algorithm from the *shape* of a
  dict key (trailing `/` → prefix, otherwise a root-only fnmatch glob). That convention is invisible at
  the declaration and is the direct cause of finding 2.
- **data-clumps** — `store_mention_sites` (:323) returns a bare `(path, line, mention)` triple where the
  module models its other tuples as NamedTuples.

---

## Triage candidates

1. Narrow `SCOPE_EXCLUSIONS['notes-*.md']` to an enumeration, or give run notes a directory.
2. Make an unreadable/undecodable shipped file a visible diagnostic rather than a silent skip.

---

## Verdict

**BLOCK** on finding 1 alone. Everything else in this gate is well built — the legs are genuinely
falsifiable, the decoys test what they claim, the census is clean, the scope is exact, and the strict
xfail mechanism works. But the deliverable as it stands cannot ever certify the retirement it exists to
certify, and it only looks green because it has not been committed yet. One `SCOPE_EXCLUSIONS` entry
plus a re-captured red transcript clears it.

---

## Workflow Feedback

- **The handoff's "~18 lines" figure is the root of finding 2, and the implementer flagged it too.**
  A prose measurement with no command behind it forced the implementer to reverse-engineer the surface
  definition, and the mechanism they invented to hit the number is broader than the number needed. This
  repo already carries the lesson `derive-distribution-claims-from-a-command`. It applies to handoffs
  that *quote* a measurement, not only to results that report one — pin the command beside the number.
- **The handoff created finding 1 by talking about "the guard file" ambiguously.** Its §2 says "`tests/`
  is deliberately outside the shipped surface — the guard file itself must contain the forbidden
  strings." There are two guard files. The sentence resolves to the test module, and the scanner —
  which has the identical problem and is *not* in an excluded root — is never mentioned. The handoff
  should have required the exclusion set to be closed under "files this guard's own definition lives in."
- **No close criterion covered the committed state.** All five close criteria and all three required
  evidence commands are satisfiable — and were satisfied — with the deliverable untracked. A gate whose
  artifact changes the very surface it measures needs an explicit "re-run with the deliverable staged"
  step. Without it the centerpiece transcript is pinned to a state that ends at integrate. I would add
  that as a standing rule for any self-referential check.
- **Review criteria were unusually good.** Being told to measure rather than reason, to plant my own
  decoys rather than trust the shipped ones, and to actively hunt for bypasses is what produced findings
  1 and 3; a criteria list that only said "verify the evidence" would have passed this gate, because the
  evidence is all accurate for the state it was measured in.
- **Engine friction (minor):** `advance` is refused on a `survey` ("advance is for gated checklists; use
  record"), but the reviewer SKILL.md instructs "record it, then `advance` that check" and "run the
  engine's final `advance`/`consolidate`." The doctrine text and the survey controller disagree; I used
  `record` + `consolidate`. Worth reconciling in SKILL.md.
