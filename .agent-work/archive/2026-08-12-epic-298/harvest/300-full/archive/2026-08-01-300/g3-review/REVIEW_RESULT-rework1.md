# Review Result — gate `g3-review`, issue #300 (epic-298) — Rework 1 re-review

## Verdict

**APPROVE**

Both round-1 blockers are **cleared**, verified in my own hands rather than taken on your report.
1 open finding remains (a stale gate artifact, not the change), consolidated with a logged override.
1 triage candidate filed.

Survey continued in the same engine file `.agent-work/300/g3-review/review.json` — three checks
appended for this round (`r13-b1-refix`, `r14-b2-refix`, `r15-artifact-trail`), consolidated
`verdict=APPROVE findings=3`, session `g3rev2-1785600325`. (`reopen` is gated-only, so a survey
records a rework round by appending; the round-1 `fail` records stay in the file as history.)

---

## Your two questions, answered

### 1. Does the corrected direction claim state the lint's real guarantee, without overselling?

**Yes.** The docstring now says the lint catches *"the declaration naming a path its own prose never
mentions"* and *"CANNOT catch the reverse — a path quietly dropped from `context_refs` while the
prose still names it."* That is exactly what the code does. Two details make it better than a
minimal correction:

- The phrase *"narrowing away"* has been **reattached to the uncaught direction**, where it belongs.
  Round 1's defect was that the phrase was doing duty for both directions at once; moving it is what
  makes the sentence unambiguous rather than merely differently worded.
- The fixture `_readme` was **reattributed**, not just reworded: "narrowing" now labels
  `prose_names_more_than_declared`, which really is the narrowing shape, and `divergent` is described
  as "a declaration pointing somewhere its own prose never covers." The two fixtures now teach the
  distinction instead of blurring it.
- `docs/CHECKLIST_ENGINE_DESIGN.md` carries the same corrected sentence, and the false
  *"stated honestly … rather than oversold"* endorsement is gone (0 grep hits). Removing it was
  right: a doc vouching for another file's honesty is a claim that has to be maintained, and it was
  false.

The characterization test is the part I'd single out. `test_narrowed_declaration_is_deliberately_not_caught`
asserts `main()` exits **0** on the narrowing fixture, so the blind spot is now *watched* rather than
described. I reproduced it independently — my own round-1 `h2_dropped.json` (prose names three files,
declaration retains one) still exits 0, which is now the documented, tested behaviour instead of a
contradiction. That converts B1 from "the prose was wrong" to "the boundary is pinned," which is a
better outcome than what I asked for.

**One residual imprecision — observation-tier, not a block.** The closing sentence
*"it only guarantees that no declared path points somewhere its own prose is silent about"* is still
slightly wider than the code, because **the `root` token is never compared**. Reproduced:

```
# prose: "...your inherited global doctrine (this skill's references/global-everyone.md)"
# context_refs: [{"root": "durable", "path": "references/global-everyone.md", ...}]
$ python scripts/verify_context_declaration.py <scratch>/root_drift.json
context declaration lint ok: 1 checklist(s) checked, 0 offenders     exit=0
```

`root` selects which base the path resolves under, so `skill` → `durable` on the same relative path
names a **different file** — somewhere the prose is silent about — and the lint is clean. This is not
a missing guard so much as a second blind spot of the same kind as narrowing: the root lives in the
prose as English (*"this skill's …"*), which is exactly as unparseable as the reverse direction. The
fix is one clause in the docstring naming it alongside the narrowing limit — and tightening
"no declared **path**" to "no declared **path string**". Filed as a triage candidate, not a
condition of approval.

### 2. Is there a third hole in the symmetric boundary rule?

**Yes, but strictly smaller than B2 and not worth a third block.** 34 independent probes against
`_appears_at_path_boundary`.

**First, the over-rejection worry you specifically raised: unfounded.** All 15 legitimate prose
shapes are accepted — start-of-string, whitespace, backtick, paren, single quote, double quote,
**sentence-final period**, comma, semicolon, colon, question mark, newline, end-of-string, a
possessive `'s`, and a bounded second occurrence following an unbounded first. The `.`-disambiguation
in `_bounded_after` is what earns that, and the comment explaining it is accurate. Three edge
over-rejections exist, all **conservative and loud** (they flag, never silently pass), none present
in this corpus:

| prose shape | declared | result |
|---|---|---|
| `Read ./refs/a.md now.` | `refs/a.md` | flagged — the `./` form names the *same* file |
| `the refs/a.md-derived list` | `refs/a.md` | flagged — hyphenated English after a bare path |
| `Read refs/a.md.then stop` | `refs/a.md` | flagged — a typo shape, not real prose |

The first is the only one I'd even mention to an author, and backticking the path (what the shipped
spine already does) makes it moot.

**The hole.** The trailing rule is a **deny-list** (`[A-Za-z0-9_/\-]` plus the `.`-rule), so any
character that in fact continues a filename but isn't on that list reads as a boundary. Each of these
is accepted although the prose names a different file:

```
declared docs/x.md   vs prose  docs/x.md._old      -> accepted (`.` then non-alnum)
declared docs/x.md   vs prose  docs/x.md.~1~       -> accepted (emacs/rsync backup)
declared docs/x.md   vs prose  docs/x.md..bak      -> accepted
declared docs/x.md   vs prose  docs/x.md(2)        -> accepted (`(` glued)
declared docs/x.md   vs prose  docs/x.md:stream    -> accepted (NTFS ADS)
declared docs/x.md   vs prose  docs/x.mdé          -> accepted (any non-ASCII glue)
```

Everything realistic is closed: `.bak`, `-old`, `_v2`, `.5`, and `/child` are all correctly rejected,
as is the leading-side suffix case. The residue needs a backup-file naming convention this corpus
does not use, in prose, adjacent to a declared path. The principled tightening is to **invert the
trailing rule to a punctuation allow-list** (accept only whitespace, end-of-string, `,;:!?)"'` and
a backtick, or a `.` not followed by alnum) — same shape as today's rule, one line, and it closes the
whole family instead of enumerating it. Filed as triage candidate `tc1`, not a blocker: the `:` case
is additionally unreachable from the declaration side, since `context_manifest.resolve()` rejects a
declared path containing `:` outright.

**On the scope addition itself — you asked me to review it as critically as the rest.** It was the
right call and I'd have said so unprompted. Stopping at the leading boundary would have shipped a
rule whose two halves disagreed about what a path boundary is, and `GLOSSARY.md` vs `GLOSSARY.md.bak`
is a more plausible drift than the suffix case that motivated B2 in the first place. The
implementation is also better than the minimum: `_bounded_after` isolates the one genuinely ambiguous
character instead of hand-waving it, and the comment states the ambiguity and its resolution in the
same breath. The fixture set covers the five legitimate trailing shapes rather than asserting the
happy path once.

---

## Open finding

### F1 — The rework's return artifact describes code that was superseded (not blocking the diff)

`IMPLEMENTER_RESULT-rework1.md` documents the **leading-only** predicate. It quotes a
`_appears_at_path_boundary` body with no `_bounded_after`, states under *Assumptions* that
*"B2's fix is a leading-boundary check only,"* and lists the trailing gap under *Out-of-scope
observations* as still open — *"still passes … worth a follow-up if this matters in practice."*
All three statements are false against the shipped file. Its full-suite figure (1224) is stale too;
I measured **1226 passed, 2 allowlisted skips**, matching your number.

The scope extension is recorded only in `IMPLEMENTER_PLAN-rework1-addendum.json` (both tasks
`complete`, `consolidation: null`), with no result document. As it stands, the artifact an Admiral
harvests would invite a follow-up issue for work that is already done, and would understate what
shipped.

This is a **closeout condition for you, not a reason to withhold approval** — the code is correct and
independently verified, and the artifact is a gitignored process record. I recorded `r15` as a genuine
`fail` and consolidated APPROVE over it via the engine's `--override-reason` rather than softening the
record, so the finding stays visible in the survey. An addendum paragraph on
`IMPLEMENTER_RESULT-rework1.md` naming the extension, the symmetric predicate, and the 1226 figure
closes it.

## Triage candidate (`tc1`, flagged in the survey)

Tighten the trailing-boundary rule from a path-char deny-list to a punctuation allow-list, and name
the unchecked `root` token as a second documented blind spot in the lint docstring. Both are the same
one-file, few-line shape as this round's fix; neither is a defect that should hold #300.

Round 1's triage candidate (wiring the lint into `.github/workflows/ci.yml`) still stands and is
untouched by this round.

---

## Verified independently this round

- **Round-1 blockers, re-run against the fixed lint.** My own `h1_substring.json` (declared
  `agents/GLOSSARY.md`, prose `docs/agents/GLOSSARY.md`) now exits **1** and names the offending
  path; my own `h2_dropped.json` exits **0**, which is the documented and now-tested blind spot.
- **No regression on the real corpus.** `skills/commander/templates/COMMANDER_SPINE.template.json`
  lints clean (0 offenders); default discovery over the whole corpus reports **13 checklists checked,
  0 offenders**. The boundary change did not break prose that wraps paths in backticks and parens.
- **Scope.** `COMMANDER_SPINE.template.json`, `scripts/context_manifest.py`,
  `scripts/checklist_engine.py`, `scripts/verify_skip_guard.py` all byte-unchanged vs HEAD;
  `.github/` untouched; no committed projection artifact. Round-1-approved work unchanged:
  `docs/CHECKLIST_SCHEMA.md` still exactly 1 insertion, `tests/test_context_manifest.py` still
  exactly 54 — so the shape test and the schema row I approved are the ones still in the tree.
  `.agent-work/300/OBLIGATIONS-301.md` untouched.
- **CI constraints.** Full suite `1226 passed, 2 skipped, 329 subtests`, exit 0;
  `verify_skip_guard.py` exit 0 ("2 skips, all match documented allow-tuples") — no new `skipTest`.
  The added `re` import is stdlib and 3.12-safe; no 3.13+ API anywhere in the change.
  `tests/test_context_declaration_lint.py` now 14 passed, and the bare node-id
  `::test_divergent_declaration_is_rejected` still resolves.

## Workflow Feedback

- **The rework note was better than the handoff it corrected.** Stating the predicate in set terms
  (`declaration ⊄ prose` is caught; `prose ⊄ declaration` is invisible) is what stopped the inversion
  from propagating a second time — the implementer's own feedback says the same, from the other side.
  That set-notation habit is worth carrying into future handoffs that pin a mechanical rule; it is
  the specific thing that would have prevented round 1's blocker at authoring time.
- **A scope extension mid-round outran its record.** The addendum plan was driven properly, but the
  return artifact was never updated to match, which is F1. Where a Commander extends scope after the
  crew has written its result, the cheapest fix is to require an addendum section on the *existing*
  result document rather than a second plan file — one artifact the Admiral reads, not two that
  disagree.
- **`reopen` is gated-only, so a survey cannot re-run a failed check.** I appended three new checks
  instead, which preserves the round-1 `fail` records as history and is arguably the better audit
  trail — but it means a re-review's structure is improvised each time. Worth a line in the reviewer
  skill: *on a rework re-review, append `rN-<blocker>-refix` checks; do not attempt `reopen`.*
- **`--override-reason` on `consolidate` was the right tool** for a real fail that should not block a
  correct diff, and I would not have found it without reading `--help`. Worth naming in the skill,
  since the alternative is a reviewer quietly downgrading a fail to a pass to make the verdict come
  out — which is exactly the softening the doctrine forbids.
