# Implementation Result — g2, rework 3 (reviewer BLOCK B1)

Written by `constellation/cleanup-f-derive-worktree/g2/implementer/attempt-4`.
Plan driven through the engine at
`.agent-work/cleanup-f-derive-worktree/g2-implement-rework3/plan.json` under my
own lease (`spine: null` in my registry entry — see "On the Stop hook").

Everything below I ran in this session. Nothing is reconstructed.

## Assigned gate

`g2`, rework 3. Repair the two stale claim families the rework-2 review found,
after a sweep for the **claim** rather than for the symbol. Base `84d949eb`.

## Completed slice

Four stale claims repaired in two files, the consumer count harmonized in the
four copies that state it, and a claim-level sweep run over the whole repo and
reported with its counts. No behaviour change: the diff under `scripts/` is
comment and docstring text only, proven at AST level.

## Files changed

**Committed (the Commander commits; `git check-ignore` exits 1 on each):**

| file | change |
|---|---|
| `scripts/checklist_engine.py` | `main()`'s load-time comment block: both stale sentences replaced. Module header: consumer-count sentence harmonized. |
| `scripts/spine_lifecycle.py` | `build_origin` docstring: the parenthesis that held one stale claim of each family. |
| `docs/CHECKLIST_SCHEMA.md` | consumer-count sentence harmonized. |
| `tests/test_spine_origin_isolation.py` | consumer-count sentence harmonized (module docstring). |
| `tests/test_worktree_derivation.py` | consumer-count sentence harmonized (module docstring). |
| `map/INDEX.md` | **not changed** — rebuilt, and the rebuild is a no-op (C7). |

```
docs/CHECKLIST_SCHEMA.md             |  2 +-
scripts/checklist_engine.py          | 30 ++++++++++++++++++++++++------
scripts/spine_lifecycle.py           | 14 ++++++++++++--
tests/test_spine_origin_isolation.py |  7 +++++--
tests/test_worktree_derivation.py    |  8 +++++---
5 files changed, 47 insertions(+), 14 deletions(-)
```

**Committed, new (for the Commander — I did not commit them):**

- this result;
- `.agent-work/cleanup-f-derive-worktree/g2-implement-rework3/**` — plan, four
  check scripts, and evidence;
- `.agent-work/cleanup-f-derive-worktree/cleanup-f-derive-worktree-g2-implement-rework3/**`
  — the engine's own per-item `context/` and `mechanical/` records for my plan,
  written by the engine, not by me.

**Specific exclusions: none touched.** `scripts/hooks/spine_rail.py`,
`tests/test_spine_rail.py`, lane A, lane E,
`scripts/verify_worktree_isolation.py`, every template and
`.agent-work/rulings/` are all absent from the diff.

## C1 — the claim-level sweep, run and reported

Full report: `g2-implement-rework3/m1-sweep.md`. Raw: `m1-sweep-raw.txt`
(pre-repair), `m2-sweep-after.txt` (post-repair), `m1-classification.txt`.

```bash
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/sweep_claims.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/classify_hits.py
```

`sweep_claims.py` never names `worktree_from_spine_path`. It matches the two
claims over **10224** git-tracked text files, on a rendering with comment
markers (`#`, `//`, `*`, `>`) stripped and whitespace collapsed, so a claim
that **wraps across two comment or docstring lines is one sentence** to the
patterns. That wrap is why B1 survived three passes: `main()`'s stale sentence
breaks after "derived". Patterns, per family:

| family | patterns |
|---|---|
| derive | `deriv\w*.{0,160}?worktree` · `worktree.{0,160}?\bderiv\w*` · `worktree … (computed\|resolved\|inferred\|read) … from … (spine\|checklist) … path` · `from … spine's own path` |
| ownership | `ownership guard` · `ownership is the lease` · `lease … (is\|was\|remains) … ownership` · `ownership … is … the lease` · `as it always was` |

**Hit count: 1589** — derive 1503, ownership 86.

| zone | derive | ownership | total |
|---|---|---|---|
| **live** | 52 | 12 | **64** |
| record: `.agent-work/` | 1448 | 74 | 1522 |
| record: `episodes/` | 2 | 0 | 2 |
| record: `map/` | 1 | 0 | 1 |

The **record zone is counted, not repaired**: launch orders, floats, rulings,
predecessor results, archived epics, harvested episodes and a generated map are
dated records of what was said at the time. Editing them falsifies the record
rather than repairing a claim; `.agent-work/rulings/` is fenced outright and
`map/` is regenerated, never hand-edited.

**Every one of the 64 live hits is classified**, and `classify_hits.py` exits 1
on any live hit it has no class for — so `64/64` is mechanical, not a claim:

| class | hits |
|---|---|
| stale → **repaired** | 6 |
| correct claim, **consumer count harmonized** | 4 |
| already correct → left as-is | 6 |
| **fenced** (g3 / lane A) → reported, not edited | 19 |
| unrelated to either family | 29 |

**The 6 stale hit-lines are 4 claims in 2 files — exactly the three passages the
reviewer named. The sweep found no fourth stale claim in either family.**

- `scripts/checklist_engine.py:3498/:3499` — derive, in `main()`
- `scripts/checklist_engine.py:3507/:3508` — ownership, in `main()`
- `scripts/spine_lifecycle.py:92` — derive, in `build_origin`
- `scripts/spine_lifecycle.py:94` — ownership, same parenthesis

**Fenced, reported, not edited (19):** `scripts/hooks/spine_rail.py:721`,
`:1171`, and 17 hits in `tests/test_spine_rail.py` (`:874 :885 :903 :904 :909
:911 :925 :930 :944 :945 :946 :947 :950 :1917 :1918 :2654 :2656`), two of them
(`:903`, `:904`) the known stale references to the deleted engine twin. All
g3's.

**Left as-is, deliberately:** `tests/test_worktree_derivation.py:8` — "It never
answers 'is this mine': ownership is the lease, and among spines sharing one
tree the discriminator is binding-key provenance (2026-08-16
worktree-is-location ruling)". This is not the guard-removal claim R1 narrowed;
it says what the **derivation** answers, in the worktree-is-location frame,
which `ADMIRAL_RULING-1` did not touch and which is `@grade: settled/human`. It
is also the single repo-wide citation C8 requires kept at exactly one.
`scripts/hooks/spine_rail.py:721` carries the same frame and is fenced anyway.

## C2 / C4 — what the repaired passages now say

`main()` now states the same thing as the module header 3400 lines above it,
and states R1 in full rather than in outline:

> What dispatch() still enforces is the LEASE -- and the lease is the ownership
> guard only WHERE A LEASE EXISTS. `require_session` gates mutating verbs once
> an active lease is held and returns early otherwise, and `_active_lease` reads
> a RELEASED lease as absent. So on a spine with NO ACTIVE LEASE -- never
> claimed, or claimed and since released -- the retired comparison was the sole
> refusal, and removing it WIDENED that path. That widening is ACCEPTED and
> deliberate: a `cd <worktree> &&` prefix defeated the comparison, so it was
> never a boundary -- but a forgeable guard is not the same as no guard. Under
> an active lease held by another session, nothing changed (`ADMIRAL_RULING-1`
> R1; the module header above carries the same statement in full).

`spine_lifecycle.build_origin` carries the same four elements in its own voice.
Neither hedges: both say the widening happened, that it is accepted, that it is
the leaseless path only, and that an active foreign lease is unchanged.

**The consumer count, told one way in all four copies that state it** (the
canonical reading from `FLOAT_TO_ADMIRAL-2` N2, as the handoff's constraint
requires) — one identical sentence, mechanically compared for equality across
the four:

> it had TWO consumers -- the shape question inside `origin_worktree_refusal`,
> deleted by that same gate, and #315's `cwd` thread, re-homed to #610 by
> `ADMIRAL_RULING-1` R3 -- and a third that `ADMIRAL_RULING-1` R2 withdrew
> before it ever existed. Three sound decisions in a row, and a definition
> nothing calls is not shipped.

### The checker, and that it can fail

```bash
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/check_claims_repaired.py
```

It extracts **six** prose segments by their own anchors — the engine module
header, `main()`'s block, `build_origin`'s docstring, `docs/CHECKLIST_SCHEMA.md`'s
`origin` section, and the two test module docstrings — so a clause satisfied in
one segment cannot cover for another. That is precisely the failure that
produced B1. It runs the same clause set twice, against the working tree and
against the **blobs at `84d949eb`** (never `HEAD`, per tc-C):

```
== working tree: PASS (0 problem(s))

== base 84d949eb (must FAIL, or this check cannot discriminate): FAIL as expected (29 problem(s))
   base 84d949eb: engine-header: STALE claim present: 'removed all three of its consumers'
   base 84d949eb: engine-main: STALE claim present: "the worktree is derived from the spine's own path"
   base 84d949eb: engine-main: STALE claim present: 'which is the actual ownership guard'
   base 84d949eb: engine-main: STALE claim present: 'as it always was'
   ... (25 more: missing R1 clauses in engine-main and build_origin, the stale
       count in docs/CHECKLIST_SCHEMA.md and tests/test_spine_origin_isolation.py,
       and the "two consumers when it was written" phrasing in the table docstring)

RESULT: OK -- red at 84d949eb, green on the working tree, 6 segments x 77 clause assertions.
```

## C3 — the module header and `main()` tell one story

Both passages are quoted **in full, side by side**, together with the two
sentences they replaced, in `g2-implement-rework3/m2-one-story.md`. The
quotations there are extracted from the file and from the base blob by script,
not retyped. In summary, each of these is now asserted present in **both**
passages: the engine reads no location at all, ambient or derived; because it no
longer asks the question anywhere; the lexical rule itself is not retired and
lives in the stdlib-only hook; the lease guards ownership only where a lease
exists; the leaseless path was the sole refusal and was widened; the widening is
accepted and deliberate; a forgeable guard is not the same as no guard; under an
active foreign lease nothing changed.

## C5 — zero executable change, pinned to `84d949eb`

```bash
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/check_no_exec_change.py
```

The handoff's pipeline, run verbatim, and its output verbatim
(`m3-no-exec-change.txt`):

```
$ git diff 84d949eb -- scripts/ | grep '^+' | grep -v '^+++' | sed 's/^+//' | grep -vE '^\s*#' | grep -vE '^\s*$'
    and that comparison is retired (#609 g2). The engine now reads no location
    at all, ambient or derived: the lexical rule that derives a worktree from a
    spine's path lives only in the stdlib-only hook, as
    `spine_rail._worktree_from_spine`. Ownership is the lease, but only where a
    lease is actually held -- on a spine with no active lease, never claimed or
    claimed and since released, that comparison was the sole refusal, so
    removing it WIDENED the leaseless path. The widening is accepted and
    deliberate: a `cd <worktree> &&` prefix defeated the comparison, so it was
    never a boundary, but a forgeable guard is not the same as no guard. Under
    an active lease held by another session, nothing changed
    (`ADMIRAL_RULING-1` R1; `checklist_engine`'s module header carries the full
    statement). Keep writing it accurately anyway,
```

**Not empty, and every line is docstring text** — the repaired
`build_origin` docstring. A docstring line is not a `#` line, so the pipeline
prints it by construction; the handoff's stop condition is a printed line that
is *not* docstring text, and there is none. Asserted mechanically rather than
by eye: each printed line must occur inside a docstring of a changed file.

The stronger property the pipeline only samples:

```
changed files under scripts/: ['scripts/checklist_engine.py', 'scripts/spine_lifecycle.py']
lines printed by the pipeline: 12 -- all docstring text: True
  scripts/checklist_engine.py: AST with docstrings blanked, 84d949eb == working tree: True
  scripts/spine_lifecycle.py: AST with docstrings blanked, 84d949eb == working tree: True
```

Comments never enter an AST, so with docstrings blanked what remains is exactly
the executable content — identical to base in both files. No statement,
argument or constant moved.

## C6 — the suite has not moved

```bash
find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q
```

```
3170 passed, 5 skipped, 1182 subtests passed in 127.23s (0:02:07)
```

**3170 passed / 5 skipped / 0 failed** — the baseline exactly, unmoved
(`m4-full-suite.txt`). The subtest figure reads 1182 rather than 1183 for the
reason the rework-2 result recorded and the reviewer confirmed:
`tests/test_context_manifest.py` runs one subtest per **clean** tracked target
and `scripts/checklist_engine.py` is dirty in my tree. It returns to 1183 once
the Commander commits. Not a movement in passed, skipped or failed.

I rebuilt the map **before** this run rather than after, so the freshness test
could not fire on a stale index mid-measurement; the rebuild turned out to be a
no-op (C7).

## C7 — the map is fresh

`py -m scripts.code_map build --root .` leaves `git status --porcelain -- map/`
**empty** (`m5-map-build.txt`). Rebuilt rather than assumed, as the handoff
asked; a change confined to comment and docstring prose moved no map entity.
`map/INDEX.md` is unchanged and was never hand-edited.

## C8 — both citations survive, by count

```bash
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/check_citations.py
```

```
2026-08-15 worktree-identity supersession citation (outside ('.agent-work/', 'map/')):
  docs/CHECKLIST_SCHEMA.md: 84d949eb=1 tree=1  ok
  episodes/active/tc6-doctrine-001.md: 84d949eb=1 tree=1  ok
  scripts/checklist_engine.py: 84d949eb=1 tree=1  ok
  tests/test_explorer_templates.py: 84d949eb=1 tree=1  ok
  tests/test_spine_origin_isolation.py: 84d949eb=2 tree=2  ok
  totals: 84d949eb=6 tree=6

2026-08-16 worktree-is-location citation (outside ('.agent-work/', 'map/')):
  tests/test_worktree_derivation.py: 84d949eb=1 tree=1
  totals: 84d949eb=1 tree=1
```

Counted against the base blobs, file for file. **One caution for whoever
re-verifies this:** the count is taken with comment markers stripped first.
A line-oriented grep sees **five**, not six — `scripts/checklist_engine.py`'s
own citation wraps after "2026-08-15", so the naive grep cannot see it. Same
wrap that hid B1.

## Test mode

**Required:** inspection-only for the edit, full suite green as the regression
floor. **Satisfied:** yes. There is nothing to test-drive in a prose change, so
the discrimination evidence is at the check level instead: the claim checker is
**red at `84d949eb` and green on the tree**, in the same run, which is what
makes it a check rather than an assertion. The suite is the floor and it has not
moved.

## Evidence

```bash
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/sweep_claims.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/classify_hits.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/check_claims_repaired.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/check_no_exec_change.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/check_citations.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q

py -m scripts.code_map build --root . && git status --porcelain -- map/
```

All five checks exit 0. Every evidence script pins `84d949eb` explicitly; none
reads `HEAD`, so they keep reproducing after the Commander commits (tc-C).
Artifacts: `m1-sweep.md`, `m1-sweep-raw.txt`, `m1-classification.txt`,
`m2-sweep-after.txt`, `m2-one-story.md`, `m3-no-exec-change.txt`,
`m4-full-suite.txt`, `m5-map-build.txt`, `m6-citations.txt`.

The post-repair sweep differs from the pre-repair one in exactly one place:
`scripts/spine_lifecycle.py`'s derive-family hits go 3 → 4, because the repaired
docstring now states the **correct** derive claim where it used to state the
stale one. No live hit disappeared unaccounted for.

## Map Impact

- **Structural anchors touched:** `checklist_engine` module header and `main()`'s
  load-time comment block; `spine_lifecycle.build_origin` docstring;
  `docs/CHECKLIST_SCHEMA.md`'s `origin` section; the module docstrings of
  `tests/test_spine_origin_isolation.py` and `tests/test_worktree_derivation.py`.
  No entity added, removed or renamed — the map rebuild is a no-op.
- **Capabilities affected:** none. Prose only.
- **Constraints/assumptions touched:** the claim that the engine derives a
  worktree from a spine path is now absent from every live passage outside the
  two g3-fenced files; R1's narrowing is stated in **six** segments rather than
  four; the consumer count is a single shared sentence.
- **Decisions:** `not-a-weaker-guard` — R1's amendment propagated to the two
  passages that had not received it. Not re-decided.
  `two-copies-pinned-by-a-shared-table` — superseded by `ADMIRAL_RULING-2` N2,
  transcribed. `worktree-is-location-spine-path-is-identity` — unchanged,
  deliberately untouched, still cited exactly once.
- **Trust limitations:** `map/ids.jsonl` is 0 bytes and per-module
  `map/<module>/INDEX.md` files are absent repo-wide (inherited tc1, not mine).

## Assumptions

- **The record zone is not prose to repair.** `.agent-work/`, `episodes/` and
  `map/` hold 1525 of the 1589 hits. I read them as dated records rather than
  standing claims and left them alone. If the Commander wants any of them
  amended, that is a separate call — `.agent-work/rulings/` is fenced regardless.
- **A wrong consumer count is a "stale claim" for the purpose of the test-file
  scope.** Allowed Scope admits the two test files "only if your sweep finds a
  stale claim in them", and the count is not a member of either named family;
  the Constraints section orders the harmonization independently. I took the
  constraint as the governing text, since leaving two of four copies on the old
  count would reproduce the exact failure mode this gate exists to end.
- **The `worktree-is-location` sentence is a different claim** and is left
  untouched (reasoning above). If the Commander reads R1 as reaching that
  sentence too, this is the one line to reopen.

## Stop conditions hit

**None.** No stale claim fell outside the allowed scope; C5 shows no executable
change; the suite did not move off 3170; no repair required re-deciding a
ruling. Nothing here is a float — I transcribed R1 and N2 rather than reasoning
about them.

## Out-of-scope observations

- **tc-A — `tests/test_worktree_derivation.py`'s symlink docstring still reasons
  about a deleted predicate.** "A `realpath` here would also make
  `origin_worktree_refusal` impure while its purity test … stayed green." That
  predicate was deleted in g2. It is a stale reference to a deleted symbol,
  which is **not** a member of either claim family I was sent to hunt, and is
  the same class of residue the handoff fences to g3 in the two `spine_rail`
  files. Reported rather than edited, for consistency with that fence. Route to
  g3 or #610's wave.
- **tc-B — the prose block still has no repo-level guard (fourth data point).**
  Rework 1 raised it, rework 2 re-raised it, the reviewer re-raised it as tc-A,
  and this rework is the third time drift shipped in it. My
  `check_claims_repaired.py` covers six segments and can discriminate, but it
  lives under `.agent-work/` and dies with this crew, exactly like the two
  checkers before it. A repo-level test — the segment extractor plus the clause
  table, roughly 120 lines — would make the guard outlive the crew. Each crew
  rewriting it from scratch is how a fifth copy of the claim gets missed.
- **tc-C — a claim that wraps across two comment lines is invisible to every
  line-oriented grep in this lane's doctrine.** It hid B1 from three passes and
  it hides one of the six C8 citations from the obvious verification command. It
  is not a one-off: any handoff that says "grep for this sentence" is wrong by
  default in a repo whose prose lives in wrapped comments. The
  strip-markers-and-flatten rendering in `sweep_claims.py` is eight lines and
  belongs in shared tooling rather than in each crew's scratch directory.
- Minor, unchanged: the reviewer's note that
  `tests/test_worktree_derivation.py`'s retired drift-test comment reads "so a
  divergence **read** as drift" where it should read "reads". It is a typo, not
  a claim; I left it rather than widen a prose-repair diff the gate wants
  auditable.

## Workflow Feedback

- **Handoff gaps: very few, and the fix from last round worked.** The one line
  the rework-2 reviewer asked for — "sweep for the **claim**, not the symbol,
  and state the hit count" — is in this handoff as C1, and it is what found the
  boundary of the problem in one pass. The canonical consumer-count reading and
  the "pin an explicit base commit" instruction each removed a detour my
  predecessors paid for. The remaining seam is small: **Allowed Scope and
  Constraints disagree about the two test files.** Scope admits them "only if
  your sweep finds a stale claim", the two claim families are defined
  immediately above it, and the consumer count belongs to neither — but the
  count harmonization is ordered in Constraints. I resolved it toward the
  constraint and said so; one clause ("a wrong count counts as stale for this
  purpose") would settle it.
- **Context rediscovered:** none of substance. The handoff carried the three
  named passages, the canonical count, and the fenced list, so the only work
  left was the sweep itself. This is the first crew on this gate that had to
  rediscover nothing.
- **Instructions improvised around:** the same one every crew on this lane has
  reported, now the fifth time. The implementer skill says a dispatched crew's
  spine is bound before it starts and `spine_status` is the first call. My
  `SPINE_FILE` is my **parent Commander's** spine under my parent's live lease,
  and my `crew-runs.json` entry carries `spine: null`. I authored my own plan
  and drove it through the CLI, which is what the workbench reference prescribes
  for this case — but the crew has to know to read a registry field to tell
  which of the two texts applies, and the skill gives no hint that the field
  exists. One sentence in the skill ("if your registry entry has `spine: null`,
  author your own plan") ends it.
- **Also worth one line:** every mutating engine verb needs `--session-id`
  passed explicitly even though the lease was claimed under that same id
  moments earlier in the same shell. Harmless, but the first three verbs of
  every crew run are refusals nobody learns anything from.
- **What would have made this easier:** a repo-level version of the clause
  checker (tc-B). Three crews have now hand-written one, each covering a
  different subset of the copies, and the gap between subsets is where each
  round's defect lived.

## On the Stop hook

**Refused, and recorded as refused.** It fired — twice, after this result was
already delivered, my plan reported `DONE: no open items` and my own lease was
released. It tells me to reload the commander skill and drive `execute.json`.
I do not obey it.
`SPINE_FILE` names my parent Commander's spine
(`.../cleanup-f-derive-worktree/spine.json`), whose lease is held by
`commander-cleanup-f-derive-worktree`; my registry entry carries `spine: null`
with `parent: .../execute/commander/attempt-3`. Obeying would mean advancing my
parent's gate under a lease that is not mine. The hook's escape clause ("if this
is an honest stop, use the engine's `block` verb") does not apply: I am not
blocked — my own plan reports every item complete, and the gate the hook calls
open is my parent's, open precisely because my parent is waiting for this file.
I drove my own plan under my own lease and release only that lease. Every crew
before me on this lane has written this up; it is still firing.

**Return status**: complete
