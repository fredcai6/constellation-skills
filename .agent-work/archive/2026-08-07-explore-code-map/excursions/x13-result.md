# Implementation Result — x13 map dogfood trial (f1Brainz #708)

## Assigned gate
x13 (explore-code-map cycle 4 dogfood trial)

## Completed slice
`split_half_boundary_drift` now takes a required keyword-only `store` argument, plumbed to all three
places it reaches telemetry, with one named resolution site that fails with the attempted path.

- **Worktree:** `C:/Programs/f1Brainz/.claude/worktrees/map-trial-708`
- **Branch:** `map-trial-708` (from `main` @ `3cf79f78`)
- **Commit:** `337f661f` — not pushed.

The bug turned out to be slightly larger than "the default doesn't resolve". `run_stage_c` in
`src/physics/pilot/pipeline.py` already carried a `telemetry_store` parameter and forwarded it to
`derive_segment_map`, then **dropped it** for the drift call — so the gate could be measuring drift on
telemetry other than the map it had just derived. The unresolvable-store error was the visible
symptom of that dropped argument.

## Scope
**Files changed:**
- `C:/Programs/f1Brainz/.claude/worktrees/map-trial-708/scripts/validate_segment_map_662.py`
- `C:/Programs/f1Brainz/.claude/worktrees/map-trial-708/src/physics/pilot/pipeline.py`
- `C:/Programs/f1Brainz/.claude/worktrees/map-trial-708/tests/unit/physics/segment_map/derivation/test_segment_map_gating.py`

**Specific exclusions touched:** no. The drift numerics are untouched; nothing in #722 or #710's
territory was edited; f1Brainz `main` and its working copy were never modified.

## Behavior changed
Yes, narrowly. Where the canonical store resolves, the resolved path is now passed explicitly and the
computation is identical — same store, same laps, same numbers. Where it does not resolve, the check
now raises `ValueError` naming the attempted path instead of falling through to
`load_quali_session`'s silent FastF1-cache fallback and failing later as a `min_laps` error. Giving up
that fallback **for this one function** is a deliberate trade recorded as a `Rejected:` comment: the
split-half check compares two halves of the same field, so both halves must come from the same durable
source, and a worktree has neither store nor cache.

Signature now:

```python
def split_half_boundary_drift(
    gp_name: str, year: int = GRIP_FIT_YEAR, session_type: str = "Q", *, store: str | None
) -> BoundaryDriftResult
```

`store` is keyword-only and has **no default**, so every caller states its choice; `None` remains a
legal, explicit way to say "the canonical store", which is what `run_stage_c`'s own `str | None`
parameter needs.

---

# Evidence

## 1. Use-trace (the trial's measurement)

Honest accounting. Five map pages loaded, two of them clear wins, one worthless, two roughly at parity
with a single file read.

**`evidence/x13/map/scripts.validate_segment_map_662/split_half_boundary_drift.md`** (entry point)
Question: what does this function touch, and who calls it? The `calls cross-module` line answered the
one thing that shaped the whole fix — the function reaches telemetry through **two different**
functions (`reference_lap_from_store` x2 **and** `load_quali_session`), so a store argument has three
forwarding points, not one. I knew the full plumbing surface before opening the file. A grep for the
symbol would not have given that; reading the 28-line body would have, at about the same cost, but the
`x2` multiplicity is exactly the kind of thing a quick read glosses over. **Mild win.**

**`evidence/x13/map/INDEX.md`** (top level)
Question: is there naming drift on the entry-point path? Read 60 lines of a 235-module alphabetical
listing and learned nothing. To use it for its stated purpose I would have had to grep it, and `ls` on
the map directory answered "does the page exist" in one call. **The map added nothing here** — a
flat directory listing at this size is not a navigation aid.

**`evidence/x13/map/scripts.validate_segment_map_662/INDEX.md`** (module page)
Question: what else lives in this module and who imports it? Useful: the entity list with one-line
summaries plus the constants block, and the `imported by` line. It also surfaced that `main` lives in
this same module — which matters, because `main` is one of the three callers and the symbol page's
own module list omitted it (see evidence 2). Cost-equivalent alternative: reading the file's first 100
lines. **Roughly parity, with one thing the symbol page got wrong.**

**`evidence/x13/map/src.physics.segment_map.derivation.reference_lap/reference_lap_from_store.md`**
Question: does this function already accept a store, and what does `None` mean? Gave the complete
signature — including `*, store: str | None = None` — and the parameter's documented semantics,
without opening an 88-line function in a large module. Grep would have found the `def` line but the
signature spans multiple lines, so I would have needed an offset read to get the same answer.
**Clear win, the cheapest answer available.**

**`evidence/x13/map/src.physics.session_fit/load_quali_session.md`**
Question: same, for the other store path. Gave the signature and the decisive design fact — "the
durable telemetry SQLite store first, the FastF1 cache as fallback... A missing store **transparently**
falls back to the cache." That silent fallback is why the original failure was confusing, and it is
what my change gives up on purpose. **Win for locating and framing it.** I then read the source
anyway (`session_fit.py:168-211`) to confirm the fallback is a bare `except Exception`, because that
detail decides whether raising early is safe. The page framed the question; the source settled it.

**Where I skipped the map:**

- **Finding the canonical store constant.** Went straight to grep. The map indexes symbols per module,
  so to use it I would have had to already know which module held the constant. Grep answered in one
  call and returned the genuinely surprising literal: `src/data/telemetry_store.py:64`
  `DEFAULT_STORE_PATH = "C:/Programs/f1Brainz/data/telemetry_store.db"` — an **absolute path to one
  machine's main checkout**, not a repo-relative path. That changed my model of the bug (the default
  usually *does* resolve from a worktree; the real defect is the dropped argument). Worth noting
  fairly: the map *could* have answered this — module pages do print a constants block with values, so
  `src.data.telemetry_store`'s page would have shown it. I could not get there because **the map is
  navigable by symbol name, not by value or by question.**
- **Reading `run_stage_c`.** Source, necessarily. I needed the body — does it already hold a store, does
  it forward it elsewhere. A map page gives calls and callers, never the assignment structure that
  shows an argument being carried and then dropped.
- **Reading the gating test file.** Source, whole file. The load-bearing content is the skip guards and
  fixtures (`_MAIN_CHECKOUT_TELEMETRY_STORE`), which is where the worktree mismatch actually lives. A
  map page for a test module lists entities, not guard constants.
- **Confirming no other callers.** Repo-wide grep. The map covers `src`/`scripts`/`tests`; I wanted
  certainty that nothing under docs, notebooks, or `.agent-work` called the symbol.

**Summary judgment:** the map paid for itself on **cross-module signature lookups** — "what does this
function I am about to call accept, and what do its defaults mean" — twice, cheaply. It was neutral on
the module I was editing (source reads are as cheap and more trustworthy), and it could not help at
all with the two questions that actually drove the design: *where does this default value come from*
and *what does this caller do with the argument it holds*.

## 2. Caller count — map vs grep

**Map** (`split_half_boundary_drift.md`, last line):
`referenced by: 3 sites in 3 modules (src.physics.pilot.pipeline, tests.unit.physics.segment_map.derivation.test_segment_map_gating)`

**Grep** (`grep -rn "split_half_boundary_drift" --include=*.py .../src .../scripts .../tests`) — 7 raw
lines, which resolve to:

| kind | location |
|---|---|
| call | `src/physics/pilot/pipeline.py:683` |
| call | `scripts/validate_segment_map_662.py:297` (inside `main`) |
| call | `tests/unit/physics/segment_map/derivation/test_segment_map_gating.py:92` |
| import | `src/physics/pilot/pipeline.py:672` |
| definition | `scripts/validate_segment_map_662.py:160` |
| docstring mention | `scripts/validate_segment_map_662.py:12` |
| docstring mention | `test_segment_map_gating.py:89` |

**They agree on the number and disagree on the names.** Both say **3 call sites**, and I updated
exactly 3. But the map's parenthetical names only **2** of the 3 modules while its own count says 3 —
the missing one is the defining module itself (`scripts.validate_segment_map_662`, whose `main`
calls the function). **Had I trusted the name list instead of the count, I would have shipped a broken
`main`.** The count was the honest part; the list was not. This is a prep-fullmap defect worth fixing:
either name the defining module in the list or state the self-reference separately.

Second, smaller observation: the map's `3` is more useful than grep's `7` **once you know what it
counts** — it has already discarded the definition, the import, and two docstring mentions. Nothing on
the page says that, so a reader who greps first and sees 7 has no way to reconcile without doing the
classification by hand, which is what I did here.

## 3. Gating test output (load-bearing)

```bash
cd C:/Programs/f1Brainz/.claude/worktrees/map-trial-708 && py -m pytest tests/unit/physics/segment_map/derivation/test_segment_map_gating.py -q
```

```
collected 7 items
tests\unit\physics\segment_map\derivation\test_segment_map_gating.py .......  [100%]
7 passed in 8.31s
```

**Result: pass.** 5 pre-existing tests plus the 2 I added. No skips — the real telemetry store was
reachable, so the two split-half drift tests genuinely computed drift against 2023 Bahrain and Austria
data and passed the `MAP_STABILITY_DRIFT_M` gate. Full suite not run (known stalls, per the handoff).

One interim failure, fixed and re-run: my first error message interpolated the path with `!r`, which
doubles every backslash on Windows and made the path unreadable — the exact defect the issue was
about, reintroduced in the fix. The message is now unquoted:

```
telemetry store not found at data/telemetry_store.db -- the split-half stability check reads
real telemetry and cannot run without it; pass store=<path to a populated telemetry_store.db>
```

**Test invocation note:** `py -m pytest` fails in this environment — the first `py` on PATH is
`C:/Users/fredc/.local/bin/py`, a codex runtime shim with no pytest. The working interpreter is
`C:/Users/fredc/AppData/Local/Microsoft/WindowsApps/py` (Python 3.14.3, pytest 9.0.2), which is what
produced the output above.

## 4. Diff and tagged comments

Diff: `git -C C:/Programs/f1Brainz/.claude/worktrees/map-trial-708 show 337f661f` — 3 files, +77/-7.

Six tagged comments written, each where a future reader would otherwise have to re-derive the choice:

| tag | location | records |
|---|---|---|
| `Constraint:` | `validate_segment_map_662.py`, `resolve_telemetry_store` | both halves must come from one durable source, so the cache fallback is given up here |
| `Rejected:` | same block | letting the fallback stand — it produced the pathless `min_laps` error |
| `Constraint:` | same, error branch | the path is interpolated unquoted; `!r` doubles Windows backslashes |
| `Rationale:` | `validate_segment_map_662.py`, `main` | the CLI owns the "use the canonical store" decision, stated once |
| `Constraint:` | `pipeline.py`, `run_stage_c` | the gate must read the same telemetry the map was derived from |
| `Constraint:` | `test_segment_map_gating.py` | pass the store the test's own skip guard checked for |

No bracketed anchor ids minted — nothing external needs to point at a specific line here, which is
what the handoff predicted.

---

## Map Impact
- **Structural anchors touched:** `scripts/validate_segment_map_662.py:160` — `split_half_boundary_drift`
  gained a required keyword-only `store`; new sibling function `resolve_telemetry_store` at the same
  level. `src/physics/pilot/pipeline.py:683` and the gating test's call site now pass it.
- **Constraints/assumptions touched:** "worktrees have no default telemetry store" is now **enforced**
  rather than assumed — the check states it and fails on it. The map's `calls cross-module` edges for
  `split_half_boundary_drift` are unchanged in target, changed in arguments.
- **Trust limitations / drift found:** the symbol page's `referenced by` module list is under-inclusive
  (evidence 2). The map's referenced-by page for this symbol will need regenerating after this commit.
- **Triage candidates:** see out-of-scope observations.

## Test mode
**Required:** test-after. **Satisfied:** yes — gating file green at 7/7, with 2 new tests covering the
explicit-arg path (absent store names the attempted path; omitting `store` raises `TypeError`).

## Docs/contracts touched
None beyond docstrings in the changed functions.

## Assumptions
- Raising rather than falling back to the FastF1 cache is the intended reading of "make the no-store
  failure mode a clear error". `ValueError` was chosen deliberately over a new exception type so the
  existing `except (SectorLineUnavailableError, ValueError)` handlers in `main` and the test keep
  working — the failure surfaces as a clean `UNAVAILABLE` print and a clean skip, preserving the
  module's stated no-frame-kill contract without editing any handler.

## Stop conditions hit
None. Scope stayed inside the three named files; the gating test ran; the map pages for the entry
point were present and legible.

## Out-of-scope observations
1. **Running the gating tests dirties the working tree.** `data/f1_data_2023.db` is a tracked binary
   that the test run modifies (SQLite side effect of opening it). It shows as modified after any test
   run. I left it unstaged and uncommitted. Worth an issue — every test run makes `git status` lie.
2. **`DEFAULT_STORE_PATH` hardcodes one machine's absolute path**
   (`src/data/telemetry_store.py:64` = `"C:/Programs/f1Brainz/data/telemetry_store.db"`). Everything
   store-related inherits it, so the whole repo's store resolution is machine-specific. Adjacent to
   #708 and strictly larger; untouched.
3. **The gating test's skip guard hardcodes the same absolute main-checkout paths**
   (`test_segment_map_gating.py:43-44`). It is why the test can pass in a worktree at all, and it is
   fragile for the same reason as (2).

## Workflow Feedback
- **Handoff gaps:** the **Verification Commands** field's `py -m pytest` does not work here — the first
  `py` on PATH is a codex runtime shim without pytest. The handoff anticipated `py` trouble but pointed
  at the wrong fallback (Makefile/TESTING.md, which also just say `py`). The fix is an absolute
  interpreter path; that belongs in the handoff field.
- **Context rediscovered:** two things the **Map Anchors** field should have carried. First, that
  `run_stage_c` already has a `telemetry_store` parameter and drops it — that is the actual defect
  shape and I found it only by reading the caller. Second, that `DEFAULT_STORE_PATH` is absolute, which
  determines whether "the default resolves" is even true in a worktree; I found it by grep.
- **Instructions improvised around:** the comment-grammar constraint gives no guidance on where a tag
  goes when the rationale covers a whole function rather than a line. I put the block above the first
  statement inside `resolve_telemetry_store`, under its docstring. A convention would help.
- **What would have made this easier:** one line in the Map Anchors saying **which caller holds the
  value being plumbed**. "Callers per the map" sent me to the map, and the map's caller list is a list
  of names — it cannot say "this one already has the thing you are about to add".

## Return status
`complete`
