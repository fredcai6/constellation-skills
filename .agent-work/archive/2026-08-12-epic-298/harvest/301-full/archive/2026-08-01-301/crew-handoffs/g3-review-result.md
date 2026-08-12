# REVIEW_RESULT — gate g3, issue #301 (epic-298)

VERDICT: APPROVE

Approve with findings. All four close criteria (C2, C3, C4, C5) are met, and I did not take
that on the implementer's word: I built a pristine out-of-repo mirror of `scripts/` +
`tests/`, confirmed it green, and then **broke the underlying behavior eight different ways
and confirmed each acceptance test actually goes red**. The two boundaries the gate rests on
are genuinely real — C2 crosses a real OS process boundary, C3 crosses a real git worktree
boundary — and I attacked both rather than reading their comments.

The findings below are refinements, not unmet criteria. Finding 1 is a demonstrated defect and
I recommend Commander authorize it as a one-line fix-now inside this gate (the same route g2's
`artifact-ref` defect took into g3); it does not falsify any close criterion and the shipped
CLI cannot reach it.

Survey (engine-driven, all 8 checks recorded): `.agent-work/301/g3-review/review.json`
Fowler pass (12/12 smells, `verify_fowler_pass.py` exit 0): `.agent-work/301/g3-review/fowler-pass.json`
Probe script (outside the repo): `…/scratchpad/probe_omission.py`; mutation mirror: `…/scratchpad/mirror/`

---

## Are C2 and C3 real boundaries, or elaborate simulations?

**Both are real. Verified by reading, running, and attacking — not by trusting the summary.**

### C2 — cross-session: REAL

`SeparateProcessMixin` uses `subprocess.Popen` + `sys.executable`. Three distinct OS pids are
observed (parent, writer child, query child), and `test_a_third_session_enumerates_…` asserts
`len({first, second, listing, os.getpid()}) == 4`. The query child reports its own
`os.getpid()` inside its JSON envelope, and the parent asserts it equals the pid it observed
at launch — so the answer is *tied* to that process, not assumed.

**Smuggled-state attack — nothing is smuggled.** Session 2 receives exactly two things:
`--store-root <temp path>` and an episode id.

- No env var: neither `query_episodes.py` nor `apply_episode_delta.py` reads any environment
  variable; `store_root()` is derived from `__file__`, and the CLI's explicit `--store-root`
  overrides it. The child inherits the parent's env, but nothing in the code path consults it.
- No inherited handle, no pickle, no shared module object: session 1 has already **exited**
  (`proc.communicate()` returns only after the child terminates) before session 2 launches.
- **No content leaking through the id.** This was the sharpest thing to check. The id is
  `<run>-<seq>` (`governor-268-001`) and carries only the run slug. The assertion that proves
  the crossing is on `observed-behavior.statement` — a sentence that appears nowhere in the id,
  nowhere in the argv, and only inside the file on disk.
- The store root is a fresh `tempfile.TemporaryDirectory`, so no ambient repo state can answer.

**Vacuity guard is real and live**: `test_the_cross_session_exercise_is_not_vacuous` points an
identical session 2 at a *different, empty* root and requires rc 2 + "no such episode".

**Proved it can fail** (mutations in the mirror):

| # | Mutation | Result |
|---|---|---|
| M1 | `_envelope` reports a constant pid (`424242`) instead of `os.getpid()` | **RED** — `AssertionError: 424242 != 5728` on `payload["pid"] == query["pid"]`. The process-tying assertion is live. |
| M2 | A not-found fetch silently returns rc 0 with an empty envelope (a hidden fallback) | **RED** on the vacuity test *and* on the C3 pre-merge check |
| M3 | `assertion.statement` truncated to 5 chars in transit | **RED** — `- Writt` vs the full sentence. The content-integrity half is live. |

### C3 — cross-worktree: REAL

Real `git init -b main`, real `git worktree add` twice, a real commit in the writer worktree,
a real `merge` to `main`, a real `merge` into the reader worktree. The test asserts each linked
worktree's `.git` is a **file** whose contents start with `gitdir:` and point under
`.git/worktrees/` — an assertion a directory-name simulation structurally cannot pass. The
reader worktree is created **before** the episode exists and queried **before** the merge, so
the transition absent → still-absent-after-local-commit → present-only-after-merge is
*observed*, including a filesystem-level
`assertFalse((reader_wt/"episodes"/f"{id}.md").exists())`.

**Could it pass if the two worktrees did share a directory? No — and I proved it twice.**

| # | Attack | Result |
|---|---|---|
| M7 | `reader_wt` set to the same path as `writer_wt` | **RED** at `assertIn("wt-reader", listing)` |
| M7b | Both worktrees genuinely created, then `reader_wt` **aliased** to `writer_wt` **and** the `assertNotEqual(resolve(), resolve())` guard deliberately neutered | **STILL RED** — `['governor-268-001'] != []` at the *still-absent-after-local-commit* assertion |

M7b is the important one: even with the explicit anti-aliasing guard removed, the transition
observation itself catches the simulation. That is defense in depth, not a single tripwire.

`test_the_two_worktrees_do_not_share_a_directory` adds the converse: an **uncommitted** episode
in worktree A is invisible in worktree B. What crosses is the commit, not the filesystem.

**The `core.autocrlf` finding is genuinely pinned**, not left as prose: writer bytes asserted
LF-only, cross-worktree bytes differ by line endings at most, `git ls-files --eol` asserted
`i/lf`, and — when CRLF is actually live — raw bytes asserted **unequal** while the parsed
records are asserted **equal**. That is a real pin. Issue #319 carries it for #308.

### C4 and C5

- **C4** — proved live by **M6** (make `_apply_amend_assertion` re-stamp every sibling's
  standing): **RED** on both the sibling-standing assertion and the byte-identical assertion.
  The byte check is done on `read_bytes()` with no decoding anywhere in the comparison path,
  and it goes further than the criterion requires — it asserts that substituting only a4's
  block into the *before* bytes reproduces the *after* bytes exactly.
- **C5** — verified independently: no ranking/similarity/embedding import, no score-like key in
  the envelope, id-sort only, and a neighbour sharing *two* join keys does not sort above one
  sharing *one* (counting shared keys would be scoring in a sort's clothes).

### Seam discipline — enforced, not merely intended

`query_episodes.py` calls `resolve_episode_path()`, `iter_episode_ids()`, `parse_episode()` and
`store_root()` through the writer, and inlines no glob, no path construction, and no status
branch. **M8** (inline `root.glob("*.md")` plus a `.status != "retired"` check into
`enumerate_episode_ids`) turned **three** tests red, including
`test_query_module_inlines_no_status_check_and_no_directory_check`. The g4 adapter swap is
protected by a live test, not by convention.

**Retirement layout is still unbound**: `_LAYOUT_ADAPTER` is untouched by this diff, both
adapters remain implemented, `test_retrieval_survives_flipping_the_layout_adapter` runs every
primitive under both and asserts identical answers (while asserting Option A really did create
`active/`), and `is_episode_in_ordinary_search()` is deliberately named-but-unused.
Retirement-dependent retrieval was **not** built. I judge that the right call.

---

## Findings, most serious first

### 1 — MEDIUM (demonstrated defect; recommend an authorized one-line fix-now, this gate)
**`select_episodes()` silently returns the WRONG episode when `values` is a bare string.**
`scripts/query_episodes.py:213` — `wanted = set(values)`. A string is iterable, so
`set("implementer")` becomes a set of *characters*.

Demonstrated against the repo's real scripts (`probe_omission.py`), two episodes seeded,
`role="implementer"` and `role="i"`:

```
select_episode_ids(root, "role", ["implementer"])  -> ['governor-268-001']   correct
select_episode_ids(root, "role",  "implementer")   -> ['governor-268-002']   WRONG record,
                                                       matched on the letter 'i'
```

No exception, no signal — a wrong answer, not merely an empty one. This is exactly the
silent-omission class the module's own docstring says it is written against ("An unrecognized
field name RAISES. It never returns an empty candidate set, which is what makes a typo'd field
name a visible failure"), and `select_episode_ids(root, "role", "implementer")` is the *natural*
way a caller writes it. The CLI cannot reach it (`argparse action="append"` always yields a
list), which is why no test caught it — and why the first real callers (#305, #308, agent-written)
are the ones who will hit it.

Fix is one line beside the existing guard:
```python
if isinstance(values, str):
    raise QueryError("select values must be a sequence of values, not a single string")
```
Plus one test. **Why not a BLOCK:** no close criterion is unmet, the CLI path is unreachable,
there are no callers yet, and this is the same shape and severity as the `artifact-ref` defect
g2's review routed as an authorized fix-now rather than a gate failure. Consistency with that
precedent, not leniency.

### 2 — MEDIUM (documentation reconciliation; carry to g4)
**`EPISODE_STORE.md` §8 and §10 now describe primitives that do not exist as described.**
§8 states that "enumerate non-retired" scans `iter_episode_ids(include_retired=False)` then
confirms each id through `is_episode_in_ordinary_search()`, and that select and neighbours
"both scan the same `iter_episode_ids(include_retired=False)` candidate set". §10 lists
"enumerate non-retired" as a **g3** deliverable. The shipped code calls
`iter_episode_ids(root, include_retired=True)` with no membership filter anywhere, and builds
no non-retired variant.

Behavior is identical **today** (under the bound Option-B placeholder, `include_retired` is a
no-op), but the observable consequence exists now and I demonstrated it: a retired episode is
returned by `enumerate`, `select` and `neighbours` while `is_episode_in_ordinary_search()`
correctly answers `False` — contradicting §7's *settled* "retirement means excluded from
ordinary rhyme-search". `apply_retirement` already works (g2), so the store can reach that
state today.

I judge the implementer's deferral **correct** — wiring the membership seam is
retirement-dependent retrieval, which this handoff explicitly excludes and §10 assigns to g4.
So the fix is a doc move, not code: at g4, §8's composition sentences and §10's g3 bullet must
move to g4. Flagging it loudly because anyone reading the frozen contract as the spec is
currently misled about what g3 shipped.

### 3 — LOW (observation; g4 or #308)
**`enumerate_episodes()` drops an unresolvable id with zero signal.**
`scripts/query_episodes.py:155` ends with `if ep is not None`. Demonstrated by stubbing
`resolve_episode_path` to return `None` for one id: `enumerate_episode_ids` listed 2,
`enumerate_episodes` returned 1, and `select` returned nothing — a candidate set silently one
record short, which is the store's named worst case. Unreachable under either bound adapter
today (scan and resolve agree), but this store's entire premise is content arriving **via git**,
so a merge or checkout landing between the scan and the read is a live race. Inherited doctrine
is explicit: no hidden fallback, fail visibly. An id that enumerates but does not resolve is a
corrupt store and should raise.

### 4 — LOW (Fowler: speculative generality / drift hazard)
**`JOIN_KEYS` is dead and can silently drift from the code it documents.**
`scripts/query_episodes.py:258` defines `JOIN_KEYS = ("artifact-ref", "role+spine-step")`;
nothing reads it. `_join_key_values()` hardcodes both keys independently, and `JOIN_KEYS`
survives only inside `neighbours()`'s docstring, which asserts the answer is "a union over all
of `JOIN_KEYS`". So the module's completeness claim is stated against a constant with no
mechanical relationship to the code implementing it. Add a third join key to one and forget the
other and nothing notices. Either iterate it in `_join_key_values()` or delete it. Real hazard
when #308 wants to extend the join set.

### 5 — LOW (Fowler: duplicated code)
The unknown-field rejection is written twice with a byte-identical message, at
`query_episodes.py:194-196` and `:216-219`. Extract `_require_selectable_field(field)`.

### 6 — LOW (Fowler: comments-as-deodorant — two already-drifted comments)
- `select_episodes()`'s docstring says the field name is "validated once, up front, against the
  FIRST episode scanned — and, when the store is empty, still validated below." The code
  validates against `_FIELD_READERS` before the loop, unconditionally. The code is *better* than
  the comment; the comment should say so.
- `naive_select_dict_collapse`'s docstring says it reads "each episode's `## Mechanical` block
  into a dict"; the code folds every `- key: value` line in the whole file. Outcome for
  `artifact-ref` is identical, so the demonstration is unaffected — but fix the comment.

### 7 — LOW (Fowler: primitive obsession)
`_join_key_values()` builds the composite key as `f"{episode.role}\x00{episode.spine_step}"`
inside a tuple that is already a tuple. A nested tuple needs no sentinel, reads directly in a
failure message, and cannot be defeated by a value containing the separator. Cosmetic today
(the writer rejects control characters).

---

## Silent-omission hunt — is the fixture honest, and what does it miss?

**The naive implementations are realistic, not strawmen built to lose.**
`naive_select_dict_collapse` folds `- key: value` lines into a dict — the single most common way
anyone writes a Markdown field reader — and it loses on the store's *own* genuinely repeated
field (`artifact-ref`), not on a contrivance. `naive_select_substring` fails in the **opposite**
direction (over-returns on the real `g1` / `g1-implement` prefix collision), so "exact" is pinned
from both sides. `naive_neighbours_first_key_wins` reads as an entirely sensible "find shared
artifacts, else fall back to same role+step". The fixtures are not rigged either:
`seed_ref_position_fixture` places the target ref **first, middle and last**, so the collapse
loses 2 of 3 rather than on one hand-placed record, and the property is asserted as
`set(naive) < set(ours)` rather than as a magic number. All three demonstrations proved live:
**M4** (first-key-wins) and **M5** (collapse `artifact-ref` to its last value) turned the
corresponding tests red.

**Omissions the fixture does NOT cover** — the fixture covers three shapes (repeated-field
collapse, run-prefix glob, first-key-wins neighbours). It does not cover:

1. **the `values`-shape degradation** — finding 1, a *wrong record returned* rather than a
   record omitted, and the only one of the three that lives in the shipped code;
2. **the enumerate/resolve drop** — finding 3, an omission with no signal at all;
3. **the inverse omission** — finding 2, a record that should *not* be in the ordinary-search
   set and is.

---

## What I verified as fine

- Every claimed command reproduced exactly: `pytest tests/test_episode_store.py -q` →
  **65 passed, 16 subtests**; `pytest tests/ -q` → **1222 passed, 2 skipped** (baseline 1181);
  `git status --short` → 2 modified + 1 new. No claim rests unreproduced.
- The authorized writer fix (`artifact-ref` `.strip()` on create) is in scope, is one line, and
  carries a proper adversarial regression test that asserts the real invariant
  `render_episode(parse_episode(text)) == text` over **dirty** input — not a clean round-trip,
  which could never have caught it.
- Fail-visibly at the CLI boundary: three distinct exit codes (0 answered / 1 invalid query /
  2 no such episode), so an unanswerable query never masquerades as an empty result.
- Scope respected: no `LESSONS.md`, no `apply_lessons_delta.py`, no #300 manifest changes; the
  record grammar and the writer's validation design were not re-litigated.
- **Repo left clean by me**: `git status --short` shows exactly the implementer's 2 modified +
  1 new file and nothing of mine; `episodes/` contains only `README.md`. Every mutation was made
  in an out-of-repo mirror and every probe wrote to `tempfile` directories.

## What I could not check

- **Non-Windows behavior.** Every run was on Windows 11 with `core.autocrlf` live. The CRLF
  branch of `test_working_tree_bytes_are_not_the_cross_worktree_identity` is conditional, so on
  a Linux CI runner that branch does not execute — the test still passes, but it certifies less
  there. Not a defect; a scope note for whoever wires CI.
- **Behavior under a bound Option A.** I exercised the flip in-process
  (`test_retrieval_survives_flipping_the_layout_adapter` genuinely creates `active/` and I
  confirmed the assertion is live), but no cross-session or cross-worktree exercise runs under
  Option A. That is correctly g4's.
- **Concurrency.** Finding 3's race is reasoned from the code, not raced in a test. I did not
  attempt to demonstrate a real merge landing mid-scan.
- I did not re-verify issue #319's contents on GitHub (no network calls made); I verified only
  that the test pinning it does what the handoff claims.

---

## Workflow Feedback

1. **The handoff was the best I have worked from at this tier**, and the reason is specific: its
   "HUNT THESE SPECIFICALLY" section named the *attacks*, not the areas — "can either test pass
   while the property it claims to prove is false", "break something and see". That turned the
   review from reading-with-an-opinion into an experiment with a red/green outcome. The eight
   mutations are the whole value of this review and I would not have run them off a generic
   "verify the tests are adequate". Worth making a standing pattern for any gate that certifies
   a headline acceptance criterion.
2. **The handoff's scope rule ("do not edit any repo file") and the review's strongest technique
   (break it and watch it go red) are in direct tension, and nothing named the resolution.** I
   improvised an out-of-repo mirror of `scripts/` + `tests/` (the test file resolves `ROOT` from
   `parents[1]`, so a scratch dir with those two subdirectories runs unmodified). This worked
   perfectly and left `git status` provably untouched, but I had to derive it. Naming
   "mutation-test in a copy outside the repo" in the reviewer skill or in handoffs that ask for
   demonstrated failure would save every future reviewer the same derivation — and would stop a
   less careful one from mutating in place and hoping to restore.
3. **Engine friction, minor and worth reporting:** (a) `start`/`record` require `--session-id`
   once a lease is claimed, but `current` **refuses** it — an asymmetry that costs one failed
   call to discover; (b) `reopen` is refused on a `survey` ("applies to gated checklists") even
   though `record` happily overwrites a previous result, so re-adjudicating a check is possible
   but only by a route the refusal message does not mention.
4. **A shell hazard specific to this handoff's shape:** finding text passed to
   `--finding` on the Bash tool gets backtick-substituted, silently deleting the identifier
   inside any `` `code` `` span. One of my recorded findings lost two identifiers that way. The
   survey text is agent-facing so the substance survived, but reviewers writing dense findings
   through the engine CLI should be warned to avoid backticks entirely.
5. The handoff's "two findings already routed — confirm, don't rediscover" section was
   genuinely efficient and I would keep it. Both confirmed.
