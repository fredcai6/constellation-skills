VERDICT: COMPLETE

# Implementation Result — gate g4 REWORK (issue #301)

Rework of the g4 BLOCK (`g4-review-result.md`, 7 findings). The original g4 handoff still
governs; nothing it ratified was revisited.

Engine: `.agent-work/301/crew-handoffs/g4-rework-plan.json`, work_id `301-g4-rework`,
session `g4-rework-implementer`, 7 items, driven to done.

## Assigned gate

`g4` — bind the ratified retirement layout (Option A, file move) + retirement-dependent
retrieval. Rework after a full cold-panel BLOCK.

## Completed slice

The store the gate ships is readable and writable by the tooling it ships. Membership is
still a directory fact; what changed is that **the classifier moved with it** — "is this
file an episode?" is now derived from the store's own id grammar and applied uniformly in
all three directories, instead of being answered by a hand-maintained list of filenames
consulted in one of them.

## Scope

**Files changed:**
- `scripts/apply_episode_delta.py` — the seam block (classifier, layout scans, absent-store
  refusal, layout bootstrap, loud path resolution, writer pre-flight) + three docstrings
- `scripts/query_episodes.py` — store-refusal contract, one silent-omission fix, F7
- `tests/test_episode_store.py` — helpers rerouted through the real classifier; 11 new tests
- `docs/EPISODE_STORE.md` — §7 (traps 4–6, the derived classifier, the per-caller
  half-retirement table, the seam table), §10 (placeholders)
- `episodes/README.md` — absorbed the two subdirectory READMEs; documents the classifier
- `episodes/active/README.md`, `episodes/retired/README.md` — **deleted**
- `episodes/active/.gitkeep`, `episodes/retired/.gitkeep` — **added** (the tracked
  placeholders, in a form the store's own grammar cannot mistake for a record)

**Specific exclusions touched:** no. `scripts/apply_lessons_delta.py` and
`.agent-work/LESSONS.md` untouched; no capture wiring (#305); no consolidation (#308); the
three fixtures under `tests/fixtures/episodes/` keep their exact paths and still exit 1; no
`Path.read_text(newline=)`/`write_text(newline=)`; every test writes to `tmp_path` (the one
new test that touches the real `episodes/` is strictly read-only). The ratified layout was
not revisited.

**Kept intact, as instructed:** C2 seam containment (zero directory literals in
`query_episodes.py`; every writer use inside the seam block, lines 470–804), C3 both
directions, C5, the `destination_for()` move, and §9's blob-OID correction.

## Per-finding account

### F1 — BLOCKER. The shipped store could not be read by its own tooling. **CLOSED.**

Root cause exactly as diagnosed: membership moved from file *content* to file *location*,
and the non-episode classifier stayed at the old location. `iter_episode_ids()` promoted
every `*.md` stem in `active/`/`retired/` to an episode id, so the gate's own
`active/README.md` and `retired/README.md` became the phantom id `README` in both sets.

Fix, per F4's ruling: **the store's existing id grammar is the classifier.** One named
function, `episode_id_for(path)`, returns the episode id for `<well-formed-id>.md` and
`None` for everything else, and it is applied in all three directories:

- `active/` and `retired/` — `_layout_episode_ids()` turns a listing into ids through the
  classifier, and **refuses** a `*.md` whose stem is not a well-formed id (a misfiled
  record, or a placeholder that should not carry a `.md` name);
- the flat root — `stray_episode_paths()` keeps the small named allowlist, which now
  survives *only* there, for the one file a grammar cannot help with (the store's README).

Because the classifier would refuse them, the layout placeholders had to change shape:
`active/.gitkeep` and `retired/.gitkeep` (not `*.md`, so outside the store's file grammar
entirely), with their documentation folded into `episodes/README.md`. That is the
authoring-time refusal the reviewer asked for, made structural rather than remembered.

```
$ python scripts/query_episodes.py enumerate
{
  "query": "enumerate",
  "store_root": "C:\\Programs\\constellation-skills-wt\\298-301\\episodes",
  "pid": 55396,
  "include_retired": false,
  "count": 0,
  "ids": [],
  "results": []
}
exit=0
```

### F2 — MAJOR. Half-retirement loud for scanning readers only. **CLOSED.**

Two seams, covering the two callers that used to proceed:

- `resolve_episode_path()` now checks **both** directories and refuses when both hold the
  id, instead of preferring `active/`. `fetch_episode()` and `_Transaction.load()` are both
  built on it, so both inherit the refusal.
- `apply_delta()` runs the enumeration seam as a **pre-flight before any op is applied**.
  Previously only `create` scanned (for id assignment), so a `retire` of an unrelated
  episode committed against a store already known to be corrupt. Now every op refuses.

One limit is deliberate and stated rather than papered over (§7): `fetch` refuses for the
**affected id** and does not scan the whole store on every addressed lookup — turning an
O(1) lookup into an O(n) scan is a cost declined for a residue that every scan and every
write already refuse.

### F3 — MAJOR. An absent `active/` enumerated to `[]` with exit 0. **CLOSED.**

Split the create/read asymmetry explicitly, because it is a real asymmetry:

- `ensure_store_layout(root)` — the **writer's** bootstrap, and the only thing that ever
  creates the layout. `apply_delta()` calls it, so a create into a store root that does not
  exist yet still works (that is how a store comes into being).
- `_require_store_layout(root)` — every **read** seam's first act (`iter_episode_ids`,
  `resolve_episode_path`, `is_episode_in_ordinary_search`). A missing root and a missing
  layout directory are two distinct refusals with distinct wording.

A reader never creates the store it could not find — asserted directly.

### F4 — MAJOR (ruling requested). Right principle, wrong mechanism. **ACCEPTED AND APPLIED.**

The recommendation was implemented as given: id grammar as classifier, uniform in all three
directories, allowlist retained only at the flat root. The reasoning is recorded in the
code (`episode_id_for`'s docstring) and in §7 so the next person does not have to
re-derive it: *a hand-maintained enumeration standing in for a computable property is the
same drift shape this run already had to replace once*, when the newline guard's hand-listed
character set drifted from what `str.splitlines()` actually treats as a boundary. Same
lesson, second costume. §7 now also records the general form, since that is the transferable
part: **binding a decision can silently invalidate a different decision elsewhere** — the
seam set keeps a bound decision in one place, but it does not tell you which other decision
the binding just made stale. The question to ask at the next such binding is *what did
membership stop being a property of?*

### F5 — MINOR. Docstrings and a doc paragraph asserting false invariants. **CLOSED.**

- `resolve_episode_path()` — "an episode is never in both places at once" replaced by a
  statement of what the code now does, with the reason the old comment was worse than
  nothing (the next reader trusts it instead of testing).
- `apply_retirement()` — the claim is narrowed to what it actually covers: no *plan* this
  writer builds can disagree with itself. It no longer implies the store can never be
  half-retired.
- `commit()` and §7 — the residue is loud at every seam that can meet it, stated as a
  per-caller table (scanning readers / `fetch` / every writer op) rather than the blanket
  "refused by readers and by the writer alike" that was two-thirds true.

### F6 — MINOR. Nested-subdirectory strays silently omitted. **CLOSED** (folded into the F1 rework, as F4's routing suggested).

Both scans are now recursive, and depth is part of the name test:
`episodes/archive/<id>.md` is refused by the stray scan, `episodes/active/old/<id>.md` by
the layout scan (a well-formed episode filename at the wrong depth). The flat-root
allowlist does not apply one level down.

### F7 — MINOR. Duplicated selectable-field error string. **CLOSED.**

Collapsed into `_selectable_field_reader()`; `grep -c 'is not a selectable field'` returns
1. Both callers now share one wording, which matters because the message is contract: "your
field name is wrong" must read identically from the CLI and from the API.

## Sweep beyond the named findings

Swept the diff for the same class rather than only the named instances. Three finds, all fixed:

1. **`enumerate_episodes()` silently dropped a scanned id it could not resolve** — it built
   its list with a trailing `if ep is not None`. That is a candidate set getting quietly
   shorter between two lines of one function, in the module whose entire premise is that it
   never does that. Now raises, naming the id. (New test; mutation M14.)
2. **The query CLI prefixed every store refusal with `corrupt store:`** — which was simply
   wrong for the new "the store is not there" case. Each message now names its own
   condition and the blanket prefix is gone.
3. **`--dry-run` had no store pre-flight** — it inherited one only when the delta happened
   to contain a `create`. It now runs the same check (and, being a dry run, still creates
   nothing, including a directory).

## Re-verification method (named explicitly, per the brief)

**Source patch in an out-of-repo sandbox.** `scripts/`, `tests/`, `docs/`, `episodes/` and
`.github/` were copied to a sandbox outside the repository; each mutation was written into
the **real source** of that copy and the whole episode-store suite re-run in a fresh
interpreter, then the source restored. Harness: `<session scratchpad>/mutate.py`, sandbox
`<session scratchpad>/mutation-sandbox/`.

This is **not** the in-process monkeypatch method the review found broken: the suite
re-executes the writer per test via `load()`, which discards any in-process substitution —
which is why the previous run's `ALL FIXTURES HAVE TEETH` did not mean what it said.

Baseline, unmutated sandbox: `105 passed, 1 skipped, 16 subtests passed`.

| mutation | result |
|---|---|
| M1 enumeration goes flat again (trap 1) | 67 failed |
| M2 history-inclusive forgets the union (trap 2) | 9 failed |
| M3 strays silently skipped (trap 3) | 2 failed |
| M4 layout listing promoted straight to ids — **the shipped defect** (trap 4) | 3 failed |
| M5 classifier accepts every filename | 6 failed |
| M6 absent store ROOT no longer refused (trap 5) | 1 failed |
| M6b absent LAYOUT DIRECTORY no longer refused (trap 5) | 1 failed |
| M7 layout scan back to one level deep (trap 6) | 1 failed |
| M7b stray scan back to one level deep (trap 6) | 1 failed |
| M8 `resolve_episode_path` never reaches the archive | 11 failed |
| M9 fetch prefers `active/` instead of refusing (F2) | 1 failed |
| M10 writer's pre-flight store check removed (F2) | 1 failed |
| M11 membership predicate always True | 2 failed |
| M12 `NON_EPISODE_FILENAMES` emptied | 6 failed |
| M13 half-retired guard removed | 2 failed |
| M14 unresolvable scanned id silently dropped (sweep find) | 1 failed |
| M15 writer's layout bootstrap removed | 3 failed |

**17/17 red — and the method earned its keep on M6.** M6 initially **survived**: the
absent-layout message contains the substring `missing store`, so my new test could not tell
the two guards apart and one of them was effectively dead. The assertion was tightened to
the distinct wording (`is not a directory`) and M6 goes red. An in-process harness would
have reported this suite as fully armed; a source patch found the hole.

## Test mode

**Required:** `test-first`
**Satisfied:** yes — red observed before green on every behavioural slice.

- **F1 red:** `ShippedStoreTests` → 2 failed;
  `test_the_real_tracked_store_is_readable_by_the_tooling_that_ships_with_it` failed with
  `AssertionError: 1 != 0 : the shipped store cannot be read by its own tooling: error:
  corrupt store: half-retired store: README exists in BOTH active/ and retired/`, and
  `test_the_shipped_stores_own_placeholders_read_end_to_end` with
  `AttributeError: module 'apply_episode_delta' has no attribute 'episode_id_for'`.
- **F3 red:** 4 `AbsentStoreTests` failed, twice with `AssertionError: EpisodeDeltaError not
  raised` — the absent store enumerated to `[]` without complaint.
- **F2 red:** the fix had already landed while wiring F3's writer pre-flight, so red was
  demonstrated by **temporarily reverting the two F2 changes in real source**
  (`resolve_episode_path`'s `len(found) > 1` refusal and `apply_delta`'s `tx.known_ids()`),
  running the new test — `AssertionError: EpisodeDeltaError not raised` at the
  `resolve_episode_path` assertion — and restoring from a scratchpad copy. Reported this
  way rather than claimed as clean TDD.
- **F6 red:** `test_trap6...` failed with `AssertionError: EpisodeDeltaError not raised`.

## Evidence

```bash
$ python scripts/query_episodes.py enumerate
{ "query": "enumerate", "store_root": ".../episodes", "pid": 55396,
  "include_retired": false, "count": 0, "ids": [], "results": [] }
exit=0
```
**Result:** pass — the store this gate ships now reads cleanly.

```bash
$ python scripts/apply_episode_delta.py --delta <valid create> --store-root <tmp>/episodes
created episode:governor-268-001
exit=0
$ python scripts/query_episodes.py --store-root <tmp>/episodes enumerate
  ... "count": 1, "ids": [ "governor-268-001" ] ...
$ ls -aR <tmp>/episodes
episodes: active retired
episodes/active: governor-268-001.md
episodes/retired:
```
**Result:** pass — the writer bootstraps a brand-new store root and the record reads back.

```bash
$ python -m pytest tests/test_episode_store.py -q
105 passed, 1 skipped, 16 subtests passed in 3.83s
```
**Result:** pass (was 94 passed / 1 skipped at review time; +11 tests).

```bash
$ python -m pytest tests/ -q
1262 passed, 3 skipped, 276 subtests passed in 35.74s
```
**Result:** pass (was 1251 passed / 3 skipped; the third skip is still the
floor-interpreter guard).

```bash
$ ! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/misfiled-field-delta.json
error: create: misfiled field 'lifecycle-standing' under mechanical — not a recognized mechanical field (...)
exit=1
$ ! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/missing-retire-reason-delta.json
error: retire: reason is required
exit=1
$ ! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/newline-injection-delta.json
error: create.agent_supplied.observed-behavior.statement: value must be a single line (no embedded or trailing line boundary) — a multi-line value could forge a store field once rendered
exit=1
```
**Result:** pass — all three still refuse, at their exact paths.

```bash
$ git status --short
 M docs/EPISODE_STORE.md
 M episodes/README.md
 M scripts/apply_episode_delta.py
 M scripts/query_episodes.py
 M tests/test_episode_store.py
?? episodes/active/
?? episodes/retired/

$ git add -An episodes
add 'episodes/README.md'
add 'episodes/active/.gitkeep'
add 'episodes/retired/.gitkeep'
```
**Result:** pass — same shape as the handoff's; the layout is really trackable, now via
`.gitkeep` rather than `README.md`. Nothing committed, nothing staged.

```bash
$ grep -n "'active'|\"active\"|'retired'|\"retired\"" scripts/query_episodes.py   # (no matches)
$ grep -n "ACTIVE_DIR|RETIRED_DIR" scripts/apply_episode_delta.py | first/last   # 470 .. 804
$ grep -rn "_LAYOUT_ADAPTER|_LAYOUT_OPTION_" scripts/                            # (no matches)
```
**Result:** pass — C2 containment preserved; the Option-B scaffolding is still gone.

## Docs/contracts touched

- `docs/EPISODE_STORE.md` §7 — traps 4/5/6 added to the relocated-class list; the derived
  classifier documented as the rule that keeps 3–6 closed; the `.gitkeep` placeholder
  decision recorded with its reason; the half-retirement claim replaced by a per-caller
  table naming what was missing and why it mattered; the enumeration and fetch seam
  paragraphs corrected; the seam table grown to seven rows (`episode_id_for`,
  `ensure_store_layout`); the "cost exactly what the seams promised" paragraph corrected to
  record what the seams did **not** protect against.
- `docs/EPISODE_STORE.md` §10 — placeholders described as they now ship.
- `episodes/README.md` — absorbed both subdirectory READMEs, plus a new section on what
  counts as an episode and why the placeholders are not `.md`.
- `scripts/query_episodes.py` module header — the store-level refusal contract stated.

## Assumptions

- **`.gitkeep`, not a renamed Markdown file, for the layout placeholders.** The handoff
  grants this choice explicitly ("whether the placeholders are `README.md` or `.gitkeep`").
  A non-`.md` placeholder is outside the store's file grammar entirely, so the classifier
  cannot be tempted by it and no allowlist is needed inside the layout directories. Nothing
  was lost: both READMEs' content is now in `episodes/README.md`, plus a pointer in each
  `.gitkeep`.
- **Refusing a non-episode `*.md` inside a layout directory, rather than ignoring it.**
  This is the reviewer's own recommendation and it is the stricter reading. It means adding
  an `index.md` under `active/` is a hard error rather than a silent no-op — deliberate.
- **`fetch` refuses for the affected id only**, and does not scan on every addressed
  lookup. Stated in §7 rather than left as an unremarked hole.
- **Temp stores in the suite now start with the layout** (`ensure_store_layout` in
  `setUp`), matching the shipped store. Two existing tests relied on reading a directory
  that had no layout at all; both were re-pointed at a real-but-empty store, which
  preserves their falsification intent exactly (`CrossSessionRetrievalTests`' vacuousness
  guard, and `CrossWorktreeSharingTests`' origin seed — the latter now seeds from the
  **real** store's scaffolding rather than a hand-written stand-in).

## Stop conditions hit

None. No decision outside the granted authority was needed; no g3 retrieval primitive had
to change shape.

## Out-of-scope observations

- **TC1 stands**: `scripts/apply_episode_delta.py` is now ~1160 lines with five independent
  reasons to change. This rework added to the seam block rather than restructuring, as the
  handoff requires. It needs a named follow-up after #301 merges.
- **Case-sensitivity, unchanged and still unasserted.** The reviewer's find holds: on
  Windows/NTFS `resolve_episode_path` and `is_episode_in_ordinary_search` answer for
  `GOVERNOR-268-001` when only `governor-268-001.md` exists; on Linux they would not. The
  new classifier makes this *tighter* in one direction (`Governor-268-001.md` is now
  refused as malformed by the layout scan, on every platform, because `ID_RE` requires
  kebab-case) but the case-insensitive *lookup* is unchanged. Still worth a Linux
  confirmation before merge.
- **A `.md` file is now refused anywhere under `episodes/` outside the two layout
  directories**, including `episodes/anything/README.md`. If a future need arises for
  documentation in a nested directory under the store, that is the rule to revisit.
- The previous result's triage list (3-vs-2 skip count → #313; `HalfRetiredStore`
  reachability; `apply_lessons_delta.py` still flat → #308) is unchanged and still stands.

## Map Impact

- **Structural anchors touched:** `scripts/apply_episode_delta.py` (seam block: one new
  classifier seam, one new layout-bootstrap seam, two scans made recursive and
  grammar-checked), `scripts/query_episodes.py` (refusal contract; one silent-omission fix),
  `docs/EPISODE_STORE.md` §7/§10, `episodes/` (placeholder shape changed).
- **Capabilities affected:** episode retirement and history-inclusive retrieval — now
  actually exercisable against the shipped store.
- **Constraints touched:** `constraint:retired-is-excluded-not-deleted` — the review's owed
  correction is discharged: it is structural for `fetch` and for the writer too, not only
  for scanning readers. `constraint:markdown-in-git` and
  `constraint:stochastic-boundary-B0.1` intact — no ranking, scoring, similarity or
  embedding added.
- **Decision candidates / resolved:**
  - `decision:episode-ness-is-derived-from-the-id-grammar` — the classifier is a computable property of the store's own id grammar, applied uniformly in all three directories; a named allowlist survives only at the flat root.
    `@grade: settled/measured · leans g4 · settle: 17/17 source-patch mutations red, M4/M5/M12 specifically`
  - `decision:layout-placeholders-are-gitkeep-not-readme` — the tracked placeholders are not `.md`, so the store's grammar cannot mistake them for records.
    `@grade: settled/measured · leans g4 · settle: the shipped store enumerates exit 0; a README.md in active/ is refused`
  - `decision:writer-creates-the-layout-readers-refuse-it` — the create/read asymmetry is explicit and named at both ends.
    `@grade: settled/measured · leans g4 · settle: M6/M6b/M15 all red`
- **Claims/evidence produced:** `claim:retrieval-does-not-silently-omit` — now supported:
  the class has six named members, each with an adversarial fixture, and the classifier that
  keeps them closed is derived rather than maintained.
- **Trust limitations:** case-sensitivity divergence unasserted (above); the half-retirement
  residue remains uncoverable by design (only the injected-fault path is testable).
- **Triage candidates:** TC1 (split the writer), a Linux confirmation run.

## Workflow Feedback

- **Handoff gaps:** the rework brief was unusually complete — it named the defect, the
  ruling, and the fix direction, and I did not have to infer any of them. The one thing it
  did not settle, and that I had to decide inside the work, is that the reviewer's fix
  *forces* the placeholder shape to change: "refuse a non-episode `.md` inside a layout
  directory" and "keep `README.md` placeholders" cannot both hold. The brief says the fix
  "would have refused your placeholders at authoring time" — true, and it means the
  placeholders must move. Naming that consequence explicitly ("expect to re-shape the
  placeholders") would have saved a decision round.
- **Context rediscovered:** that `QueryTestCase.seed()` enumerates the store *before* it
  writes, so any refusal added to the read path lands on every test's first line. That is
  the mechanical reason F3 could not be added without also deciding what a temp store looks
  like at `setUp` — a bigger consequence than "add a guard", and it is not visible from the
  finding itself.
- **Instructions improvised around:** two engine friction points. (1) `--session-id` is a
  **sub-verb** argument, not a top-level one, so
  `checklist_engine.py --file X --session-id S attest ...` fails with
  `invalid choice: '<session>'`; the skill text and the refusal message both say "pass
  `--session-id`" without saying where, and it cost three failed calls. (2) `advance`
  requires `--why` on a non-exempt gate, which is good, but nothing before the first
  `advance` says so — it is discoverable only by being refused.
- **What would have made this easier:** a postcondition check I wrote for m1 — "no test
  helper filters a non-episode file by an inline name comparison" — tripped on my own
  *prose*, because the docstring explaining why that pattern is wrong contains the pattern.
  Worth knowing when authoring grep-shaped gates: a check that greps for an anti-pattern
  will fire on the comment documenting it, and the fix is to reword the comment, which is
  faintly absurd. A note in the plan template about grep checks needing to be
  comment-insensitive would have saved a cycle.

## Return status

`complete`
