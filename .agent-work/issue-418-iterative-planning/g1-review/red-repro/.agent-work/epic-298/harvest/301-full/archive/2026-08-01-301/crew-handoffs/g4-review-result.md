# Review Result — gate g4 (issue #301)

VERDICT: BLOCK

Survey driven end to end through the engine at `.agent-work/301/g4-review/review.json`
(work_id `301-g4-review`, session `g4-review-cold-panel`, 12 items, consolidated
`verdict=BLOCK findings=7`). Fowler pass record at the session scratchpad,
`verify_fowler_pass.py` exit 0.

## Assigned Gate

`g4` — bind the ratified retirement layout (Option A, file move) + retirement-dependent
retrieval. Full cold-panel class, last gate before merge.

## Result

`BLOCK` — one demonstrated defect that ships live in the deliverable (F1), plus two
correctness findings and four refinements.

---

## Blockers

### F1 — BLOCKER. The fourth relocated silent-omission trap ships live: the store the gate delivers cannot be read or written at all.

`NON_EPISODE_FILENAMES` is consulted in exactly **one** place — `stray_episode_paths()`,
which globs `root/*.md`, the **flat root only** (`scripts/apply_episode_delta.py:478-498`).
It is never applied inside `active/` or `retired/`. But `iter_episode_ids()` globs both of
those directories unconditionally and promotes **every** `*.md` stem to an episode id:

```python
live = {p.stem for p in (root / ACTIVE_DIR).glob("*.md")}
archived = {p.stem for p in (root / RETIRED_DIR).glob("*.md")}
```

Membership moved from file *content* to file *location*. The non-episode classifier did
not move with it. That is precisely the question the handoff told me to keep asking, and
this is its answer.

The gate's own shipped placeholders — `episodes/active/README.md` and
`episodes/retired/README.md`, documented as design in §10 — therefore contribute the stem
`README` to **both** sets, and `_reject_half_retired()` fires on the real tracked store:

```
$ cd C:/Programs/constellation-skills-wt/298-301
$ python scripts/query_episodes.py enumerate
error: corrupt store: half-retired store: README exists in BOTH active/ and retired/ —
a retirement was interrupted between placing the archived copy and removing the source. …
exit=1
```

Reproduced identically for `select`, `neighbours`, `enumerate --include-retired`, and for
the **writer's** `create` op (its id-assignment scan goes through the same seam). The
default `store_root()` store is unusable by every primitive the gate ships. #305's capture
wiring cannot write a single episode into it.

Remove one placeholder and it degrades differently, into the *silent* form of the class:

```
only episodes/active/README.md present:
  enumerate_episode_ids(root)  -> ['README', 'governor-268-001']   # a PHANTOM id
  enumerate_episodes(root)     -> EpisodeDeltaError: corrupt episode: missing episode-state header
  select / neighbours          -> same hard failure
```

A phantom id enters the candidate set from nothing but a filename, and every primitive
built on top of the candidate set dies on it.

**Why the suite missed it.** No test ever constructs a store containing the shipped
placeholders. Both test helpers that enumerate the store filter README out by an inline
glob shape — `p.name != "README.md"` at `tests/test_episode_store.py:72` and `:1755` —
which is the exact "exclusion by accident of a glob's shape" pattern §7 rejects, sitting
in the tests that are supposed to police it. The trap-3 fixture proves the allowlist works
at the flat root and stops there.

**Close criteria affected.** C4 is unmet: the claim is
`claim:retrieval-does-not-silently-omit`, and retrieval both omits (phantom/absent) and
hard-refuses on the store as delivered. C6's own guard produces a false positive on a store
that was never retired at all.

**Fix direction** (see F4 for the ruling behind it): classify by the id grammar the store
already owns, uniformly in all three directories, rather than by a filename allowlist
applied in one of them.

---

## Findings (ranked, F1 above is #1)

### F2 — MAJOR. Half-retirement is loud for scanning readers only; `fetch` and the writer's `retire` silently proceed.

The handoff asked me to test this specifically: *"create an episode in both directories and
confirm readers AND the writer refuse rather than silently picking one."* Result, with
`governor-268-002` placed in both directories:

| caller | behaviour |
|---|---|
| `enumerate` / `select` / `neighbours` (both directions) | REFUSE — correct |
| writer `create` | REFUSE — correct |
| **`fetch_episode` / `resolve_episode_path`** | **PROCEED — silently returns the `active/` copy, `status: active`** |
| **writer `retire` (of any episode)** | **PROCEED — the delta commits against a store known to be corrupt** |

`resolve_episode_path()`'s docstring asserts *"Exactly one of the two exists for any valid
id — an episode is never in both places at once"* — false in exactly the residual state the
design admits exists. §7 and `g4-result.md` both claim the state is *"refused by the
enumeration seam, by readers and by the writer alike."* Two of the four callers do not.

Consequence for #308: a consolidation pass that walks back from an archived member by id
gets the pre-retirement copy with `status: active`, with nothing signalling it — while
every scan around it refuses. The store is loud in one hand and silent in the other.

Layers (a) unrepresentable-by-construction and (b) compensating rollback I verified sound
and well-tested; this is layer (c) only.

### F3 — MAJOR. A missing layout directory reads as an empty store, with no refusal.

```
store with 2 episodes, then active/ removed:
  enumerate_episode_ids(root)                        -> []   (exit 0)
  enumerate_episode_ids(root, include_retired=True)  -> []   (exit 0)
store root that does not exist at all:               -> []   (exit 0)
```

`Path.glob` on a missing directory returns empty; `stray_episode_paths` returns `[]` when
`root` is not a directory. This is verbatim trap 1's own failure description — *"an empty
candidate set is indistinguishable from 'the store is empty'"* — for the case the gate
did not enumerate. It matters more after this gate than before it: the layout now *requires*
two subdirectories, git does not track empty directories, and a typo'd `--store-root`
silently answers `count: 0, exit 0` rather than failing. Violates `global-crew.md`
*"No hidden fallback; fail visibly."*

### F4 — MAJOR (ruling requested). `NON_EPISODE_FILENAMES` is the right principle in the wrong mechanism, and it does reintroduce the character-list drift shape.

**The principle is right and load-bearing.** I mutation-verified it: emptying the allowlist
in the real source turns four tests red. The exclusion genuinely comes from the named
allowlist and not from a glob shape, exactly as claimed.

**The mechanism reintroduces the same drift shape, in two ways.**

1. **Scope drift, already realised.** The allowlist is consulted at one of the three
   directories that now hold files. Membership moved from content to location; the
   classifier stayed at the old location. That asymmetry *is* F1 — this is not a
   hypothetical drift risk, it is a drift that already happened, inside the same gate that
   introduced the allowlist.
2. **A hand-maintained enumeration standing in for a computable property.** This is the
   same shape as the character-list guard this run already had to replace once. The store
   already owns an id grammar: `<kebab-case-run>-NNN`, enforced at create (the run must be
   kebab-case) and relied on by `_next_episode_id`'s `suffix.isdigit()`. "Is this filename
   an episode?" is *derivable*. A `frozenset` of filenames must instead be edited whenever
   anyone adds a `.gitkeep`, a `CODEOWNERS`, an `index.md`, or a second README variant —
   and forgetting is silent in one direction (a real stray accepted) and store-bricking in
   the other (F1).

**Recommendation:** make the id grammar the classifier, applied uniformly in all three
directories. A `*.md` file whose stem is not a well-formed episode id is not an episode:
in `active/` or `retired/` refuse it as misfiled; at the flat root ignore it only if it is
in a small named allowlist. That is drift-free by construction and would have refused the
shipped placeholders at authoring time rather than at first use.

### F5 — MINOR. Three docstrings and one doc paragraph assert invariants the code does not hold.

`resolve_episode_path()` ("an episode is never in both places at once"),
`apply_retirement()` ("the store cannot end up half-retired"), and §7's "refused … by
readers and by the writer alike" — all contradicted by F2. This is the one
comments-as-deodorant flag I did not override: the in-file rationale density is repo
convention and genuinely load-bearing, but a comment that asserts a false invariant is what
the next implementer will trust instead of testing.

### F6 — MINOR. Nested-subdirectory strays are silently omitted.

`episodes/archive/x.md` and `episodes/active/old/x.md` are invisible to every enumeration
and trigger no refusal (`stray_episode_paths` is flat-root-only and non-recursive; the
layout globs are non-recursive). Lower severity than F1 because nothing produces such a
file today, but it is the same class and one `rglob` away from covered.

### F7 — MINOR / observation. Duplicated selectable-field error string.

The `"is not a selectable field"` message is written twice verbatim, in
`query_episodes.field_values()` (`:247`) and `select_episodes()` (`:285`).

---

## Handoff compliance

Met: Option A bound; `_LAYOUT_ADAPTER` / `_LAYOUT_OPTION_*` gone (grep returns 0 across all
of `scripts/`); `include_retired` defaults False on every scanning primitive and is
correctly absent from `fetch`; doc corrections landed; Option B retained as
rejected-with-reason.

Unmet: the handoff's central obligation — that the relocated silent-omission class be
*closed*, not merely named. A fourth member of it ships in the deliverable.

**On the `fetch` asymmetry (handoff item 2).** The reasoning is sound and I could not break
it: a lookup by name is not a search, and without it every `consolidated-into:` /
`superseded-by:` cross-reference dangles the moment its target is retired. The one caller
surprise I can construct — treating `fetch(id) is not None` as "this episode is live" — is
already answered by `is_episode_in_ordinary_search()` existing as a separate named seam and
by the envelope reporting `include_retired`. Keep it as is.

## Scope drift

None. `tests/fixtures/episodes/` untouched and all three fixtures still exit 1.
`LESSONS.md`, `apply_lessons_delta.py`, #300's manifest untouched. Record grammar and
writer validation not relitigated.

**The one change beyond a pure adapter swap** — moving the `ep.status` routing branch out of
`_Transaction.write_plan()` into `destination_for()` — is behaviour-preserving (a
non-retired episode gets `current_path` back, identical to the old no-op branch) and was
genuinely necessary for C2: left in `write_plan()`, a call site outside the seam block reads
`status` to pick a directory. Justified, not opportunistic.

## Evidence verdict

Every claimed command independently reproduced. `tests/test_episode_store.py`: 94 passed,
1 skipped (the implementer's result says 93; the review handoff's 94 is correct).
`tests/`: 1251 passed, 3 skipped — third skip is the floor-interpreter guard, as briefed.
C2 containment reproduced exactly: zero directory literals, globs, or status branches in
`query_episodes.py`; all writer uses inside lines 422-643. C5's 19 tests pass.

**The mutation claim I verified independently and more strongly than reported.** The
implementer's `red_probe.py` monkeypatched an in-process module object; that harness cannot
work here, because `tests/test_episode_store.py` reloads the writer per test via `load()`
(I confirmed: six in-process mutations produced 0 red / 95 run). I therefore patched seven
mutations into the **real source** in a sandbox copy of `scripts/`+`tests/`+`docs/` outside
the repo:

| mutation | result |
|---|---|
| M1 flat glob (trap 1) | 56 red |
| M2 forgets the union (trap 2) | 8 red |
| M3 strays silently skipped (trap 3) | 2 red |
| M4 `resolve_episode_path` never reaches the archive | 9 red |
| M5 membership predicate always True | 2 red |
| M6 `NON_EPISODE_FILENAMES` emptied | 4 red |
| M7 half-retired guard removed | 1 red |

All three claimed traps have real teeth, and so do four seams the implementer did not claim.
That part of the work is better than reported.

## Code/doc quality

`docs/EPISODE_STORE.md` §7 describes what shipped; §§8/10 match reality (I checked every
primitive and CLI flag §8 names); §9's byte-level claim is correctly replaced by *"the same
content at the same blob OID"* with `.gitattributes * text=auto`, the platform conversion,
the pinning test, and issue **#319** named — doc and test now agree. §§1/2/3 swept of stale
Option-B disclaimers. Two doc defects: §7's writer-refusal over-claim (F2/F5) and §10
documenting the placeholders that cause F1.

**Fowler pass** (all 12 baseline smells visited, verifier exit 0):
flagged `duplicated-code` (F7 + the test helpers' inline README exclusion),
`primitive-obsession` (bare-`str` ids with no grammar check — the root cause of F1),
`divergent-change` (1115-line writer with five reasons to change), `comments-as-deodorant`
(F5). Overridden with logged standards: `long-method` (commit()'s phases share one rollback
contract — locality), `feature-envy` (§7's seam set *is* the contract), `data-clumps`
(`(root, include_retired)` — no speculative abstraction), `speculative-generality`
(`HalfRetiredStore` — §7's composition rule, mutation-verified load-bearing).

## Map impact verdict

- **Evidence supports claimed change:** yes for C2/C3/C5; no for
  `claim:retrieval-does-not-silently-omit` (F1).
- **Constraints not violated:** `constraint:markdown-in-git` and
  `constraint:stochastic-boundary-B0.1` intact — no ranking, scoring, similarity or
  embedding added, confirmed by reading every primitive.
- **Notes match the diff:** yes, with one correction owed —
  `constraint:retired-is-excluded-not-deleted` is described as *"now structural, not
  procedural"*; true for scanning readers, not for `fetch` or for the writer's `retire`
  (F2).
- **Decision candidates surfaced:** yes. `decision:layout-routing-lives-in-destination_for`
  is graded `settled/measured` and I reproduced the measurement (containment 1 → 0).
- **Durable context routed:** yes; one additional triage candidate flagged in the survey.

## Reconciliation check

No structural baseline divergence beyond the map correction above.

## Out-of-scope observations

- **TC1 (flagged in the survey):** split `scripts/apply_episode_delta.py` — 1115 lines with
  five independent reasons to change (record grammar, layout seams, delta validation,
  staging transaction, CLI). Needs a named follow-up issue **after #301 merges**; the g4
  handoff forbids restructuring and §7 requires the seams to live with the writer.
- The implementer's own triage list (3-vs-2 skip count → #313; `HalfRetiredStore`
  reachability; `apply_lessons_delta.py` still flat → #308) I checked and agree with.

## Routing for the findings, if Commander disagrees on severity

F1 must land in **this** gate — it is the deliverable's own store. F2, F3, F5 belong with
it (same rework pass, same seam block, and F5 is the documentation of F2). F4 is the design
ruling behind F1's fix. F6 and F7 are legitimately deferrable, but need a named home: fold
them into the F1 rework, or file them against **#308** (which is the first consumer that
would meet either).

## What I could not check

- **Behaviour on a case-sensitive filesystem.** I ran on Windows/NTFS. `resolve_episode_path`
  and `is_episode_in_ordinary_search` both answered True for `GOVERNOR-268-001` when only
  `governor-268-001.md` exists — that is case-insensitivity, and the same calls would return
  None/False on Linux/CI. Not a silent omission (ids are minted kebab-case; a case-variant
  run is refused at validate: `'Governor-268' must be kebab-case`), but the platform
  divergence is real and unasserted. Worth a Linux confirmation before merge.
- **Real hard-kill / power-loss behaviour.** Only the injected-fault path is testable; the
  residual is by design uncoverable, and I did not attempt to kill a process mid-`commit()`.
- **Git rename/merge behaviour when the same episode is retired in two worktrees**
  concurrently. §9 covers ordinary sharing; the move introduces a rename/delete conflict
  shape that no test exercises. Not in this gate's criteria — noted only.

## Cleanup

Nothing stray left. `git status --short` is byte-identical to the handoff's; `episodes/`
contains exactly `README.md`, `active/README.md`, `retired/README.md`. All probes and the
mutation sandbox ran outside the repo, under the session scratchpad. No repo file edited.

## Workflow Feedback

- **Handoff gaps:** the "HUNT THESE SPECIFICALLY" candidate list (case-insensitive
  filesystems, missing directory, both directories, symlinks, id colliding with a
  non-episode filename) was excellent and is why I probed the right space — but it listed
  the collision as *"an episode id that collides with a non-episode filename"*, framing it
  as an adversarial input. The realised defect is the mirror image: a **non-episode
  filename that the store mints an episode id from**, and it was already sitting in the
  deliverable. Naming the direction "a non-episode file inside the layout directories"
  would have pointed straight at it.
- **Context rediscovered:** that `tests/test_episode_store.py` reloads the writer per test
  via `load()`, which invalidates any in-process monkeypatch mutation harness. The
  implementer reported `ALL FIXTURES HAVE TEETH` from a harness of exactly that shape; I had
  to build a source-level sandbox to check the claim honestly. A handoff that cites a
  mutation-verification artifact should say **how** the substitution reaches the code under
  test, because "monkeypatched the seam" and "patched the source" are not interchangeable
  here and only one of them works.
- **Instructions improvised around:** the engine's `advance` verb refuses on a `survey`
  (`REFUSED: advance is for gated checklists; use record`), but the reviewer SKILL.md says
  *"integrate it, `advance` that check"* and *"Run the engine's final `advance`/`consolidate`
  first"*. I used `record` throughout and `consolidate` at the end. Also
  `flag-candidate`'s required `--from` / `--statement` are not mentioned in SKILL.md and
  cost a failed call. Both worth correcting in the skill text.
- **What would have made this easier:** one line in the handoff's evidence block running the
  primitives against the **real** `episodes/` root rather than only temp stores. Every
  reproduction command in the handoff used a throwaway store, and the defect is visible in
  a single command against the shipped one. A "does the thing you are shipping work" check
  is cheap and would have caught F1 three roles earlier.

## Return status

`complete`
