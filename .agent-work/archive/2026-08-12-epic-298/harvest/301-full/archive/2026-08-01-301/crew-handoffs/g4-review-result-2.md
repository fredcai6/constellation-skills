# Review Result — gate g4 RE-REVIEW (issue #301)

VERDICT: APPROVE

Survey driven end to end through the engine at `.agent-work/301/g4-review-2/review.json`
(work_id `301-g4-review-2`, session `g4-review-2-cold-panel`, 15 items, consolidated with
findings). Fowler pass record in the session scratchpad, `verify_fowler_pass.py` exit 0.

Approved **with findings**, one of which is a demonstrated defect. It does not meet the
BLOCK bar — every close criterion is met and independently verified, and the defect
requires an input no shipped caller produces — but it **must not merge unrouted**. See
"Merge conditions" below; they are cheap and neither needs another review cycle.

## Assigned Gate

`g4` — bind the ratified retirement layout (Option A, file move) + retirement-dependent
retrieval. Full cold-panel class, last gate before merge. Re-review after a BLOCK with
seven findings.

## Result

`APPROVE` — the BLOCK is genuinely closed. All seven prior findings verified fixed by
execution, not by reading. Four new findings, ranked below: one demonstrated defect
(F1), one doc defect that contradicts the gate's own document (F2), and two minor
observations.

---

## Merge conditions (both cheap; neither needs a re-review)

1. **F1 needs a filed issue number before merge.** There is no gate after this one, so a
   routed finding with no home is a dropped finding. #308 is the first consumer that
   would meet it, but F1 is not #308's work — it wants its own issue.
2. **F2 should be fixed in the merge commit.** It is a five-line correction to a paragraph
   this gate already rewrote around, and leaving it means the shipped document instructs
   the next reader to recreate the exact defect that was blocked.

If Commander cannot file (1), treat F1 as a blocker instead — that is the honest
consequence of the "every routed finding needs a named home" rule, not a change of my
severity judgment.

---

## Findings (ranked)

### F1 — MAJOR, demonstrated. THE FIFTH TRAP. The grammar classifies names the store **lists**; nothing classifies an id the store is **handed**.

This is the class relocating a third time, and the relocation is a direct consequence of
the fix. Asked what a grammar-based classifier gets wrong that a filename list did not,
the answer is structural: **a list could only ever have classified files the store
enumerated — it had nothing to say about an id arriving from outside, and nobody expected
it to. A grammar is a decidable predicate the store now owns, and owning it creates an
obligation to apply it wherever an id ENTERS the system.** That obligation was discharged
for the three directories and nowhere else.

`episode_id_for()` is applied to `rglob` results. It is applied to nothing else.
`resolve_episode_path()` and `is_episode_in_ordinary_search()` interpolate their `str`
argument straight into `root / sub / f"{episode_id}.md"` and ask the filesystem.

Three demonstrations, all against a **store I first proved healthy**
(`iter_episode_ids(include_retired=True)` → exactly `['governor-268-001',
'governor-268-002']`):

**(a) The membership seam returns a silent wrong answer.**

```
is_episode_in_ordinary_search('../../elsewhere', root)  ->  True
```

`§7` names this seam as "the single place any retrieval primitive asks 'is this episode
currently in the ordinary rhyme-search candidate set'". It answers **True** for a file
that is not an episode, is not in `active/`, and is not under the store root at all. Its
own docstring argues that "a predicate that collapses [two facts] hands its caller a False
that means nothing" — a True that means nothing is the same defect with the sign flipped,
and unlike the False it is not loud anywhere.

**(b) A healthy store reports itself corrupt, with a destructive remediation instruction.**

```
$ python scripts/query_episodes.py --store-root <healthy store> fetch "../../elsewhere"
error: half-retired store: ../../elsewhere exists in BOTH active/ and retired/ — a
retirement was interrupted between placing the archived copy and removing the source.
The retired/ copy is the newer one; remove the active/ copy to complete the retirement,
or the reverse to abandon it.
exit=1
```

Identical for `neighbours`, and for an **absolute** path argument. The cause is arithmetic:
both `root/active/../../elsewhere.md` and `root/retired/../../elsewhere.md` normalise to
the same file, both `.exists()`, so `len(found) > 1` fires the half-retirement guard. The
guard is new in this rework (it is F2's fix), so this misfire is rework-introduced. An
operator or agent following that message deletes a file from a store that was never
corrupt.

**(c) An addressed lookup returns a record the enumeration refuses.**

```
$ ... enumerate            -> error: malformed store: active/old/probe-run-001.md is not a
                              well-formed episode file at this level ...        exit=1
$ ... fetch "old/probe-run-001"  -> exit 0, returns the record
```

**Where this actually reaches production, not just my probes.** `_validate_retire()` and
`_validate_amend_assertion()` both `ID_RE.fullmatch` their `id`, so the **write** path is
grammar-checked and the store cannot be steered into corruption — that is why this is not
a blocker. But the same validator treats `consolidated-into` and `superseded-by` as
`_require_str` + `_reject_newline` only, **not** as ids. The store will therefore persist a
cross-reference of any shape, and §7's own argument for why `fetch` reaches the archive is
precisely that #308 "walks back through [it] when it follows a `consolidated-into:`
reference by id". That is an unvalidated value flowing into an unvalidated lookup, in the
one consumer the design names.

**Fix direction** (offered, not required — this is the shape, the ruling is Commander's):
one named `episode_path(episode_id, root, sub)` that refuses an id `episode_id_for()`'s own
grammar would not accept. It removes the four-times-repeated address expression
(`duplicated-code`, flagged), gives the classifier the one place it is currently absent,
and makes `fetch <not-an-id>` say "that is not an episode id" instead of accusing the store.

**Why I did not block on it.** C2–C6 are all met and verified. No shipped caller passes a
path-shaped id today; the write path is protected; nothing corrupts. It is a hardening gap
against inputs that do not exist yet — but #308 is where they start existing, which is why
condition (1) is not optional.

### F2 — MAJOR (doc). §1 still documents the placeholders that caused the BLOCK, and contradicts §7 and §10 of its own document.

`docs/EPISODE_STORE.md` lines 59–64, untouched by the rework:

> Because git does not track empty directories, the store ships with a tracked `README.md`
> in `episodes/`, `episodes/active/`, and `episodes/retired/` … These are the store's only
> non-episode files and are excluded from enumeration by a **named allowlist**
> (`NON_EPISODE_FILENAMES`) … see §7's trap 3 for why that distinction is load-bearing.

Three claims, all false of what shipped: there is no `README.md` in either layout
directory (`.gitkeep`); the allowlist is explicitly **not** consulted inside them, and a
`README.md` there is now **refused as malformed**; and the governing trap is 4, not 3.

Severity is not pedantry about a stale sentence. §1 is the section that tells a reader
**how the layout is kept trackable**, and this gate's whole failure mode was a reader-facing
instruction that bricked the store. A future implementer who follows §1 places
`README.md` in `active/` and hard-errors every primitive — while §7, forty lines further
down, explains at length why that is refused. The rest of the doc set is clean: §7 is
accurate and thorough (traps 1–6, the derived classifier, the `.gitkeep` decision with its
reason, the per-caller half-retirement table — all three rows probe-confirmed true — the
seven-row seam table, and the honest "what the seam set did NOT protect against"
paragraph), §10 is correct, and `episodes/README.md` and both `.gitkeep` bodies are
accurate and genuinely useful. §1 is the single stale spot.

### F3 — MINOR. Two unnamed membership decisions still run **ahead** of the classifier in both scans.

`_layout_episode_ids()` and `stray_episode_paths()` both open with
`if not path.is_file(): continue` — a **silent skip**, in the two functions whose stated
contract is "refused rather than skipped: skipping is how a filename becomes a phantom id,
and how a real record becomes invisible". Demonstrated: a directory named
`active/probe-run-009.md` is dropped without a word, `enumerate` exits 0 with a
plausible-looking set. The case that matters more is a **broken symlink** at
`active/<id>.md`, which takes the same branch; the original handoff listed symlinks as a
hunt target and I could not create one (Windows `WinError 1314`, no privilege), so I flag
the code path and cannot demonstrate that instance.

The second is the `*.md` glob itself, which is half the membership rule and is not part of
`episode_id_for()`'s reach. Its case-sensitivity is platform-dependent: I observed
`active/probe-run-004.MD` **refused as malformed on Windows** (the glob matched it, the
grammar rejected the uppercase stem); on POSIX `rglob("*.md")` will not match it at all
(`fnmatchcase('x-001.MD','*.md')` → `False`), so the same file is **silently invisible**.
One file, two verdicts, decided by the OS. Combined with the known case-insensitive
`.exists()` lookup divergence the previous review recorded and this rework correctly
reports as unchanged, this is the second reason a **Linux confirmation run before merge**
is worth its cost.

### F4 — MINOR. A well-formed filename with non-episode content still mints a phantom id at the id level.

```
active/probe-run-001.md containing "just some notes, not an episode":
  enumerate_episode_ids(root)           -> ['governor-268-002', 'probe-run-001']   # phantom
  enumerate_episodes(root)              -> EpisodeDeltaError: corrupt episode: missing
                                           episode-state header
```

The grammar classifies the **name**; nothing classifies the **content**. This is the same
sentence the previous review wrote about `README` — "a phantom id enters the candidate set
from nothing but a filename" — surviving for names the grammar happens to accept. It is
much less severe than F1 was: it needs a hand-placed file, the record level is loud, and
`enumerate_episodes()`'s new raise (the implementer's own sweep find, mutation M14, which I
verified red) closes the path that mattered. Recording it because the id-level surface is
public and #305/#308 consume it. A ruling that "an id is a filename fact and content is
checked on read" is a perfectly good answer — it just is not written down anywhere.

---

## Handoff compliance

Every one of the seven prior findings verified closed, by execution:

| prior finding | verified |
|---|---|
| F1 store unreadable | **CLOSED** — every primitive runs against the real `episodes/`, exit 0 |
| F2 half-retirement silent at `fetch`/writer | **CLOSED** — all three caller classes refuse; probe-confirmed |
| F3 absent layout reads as empty | **CLOSED** — two distinct refusals; readers never create |
| F4 allowlist is the wrong mechanism | **APPLIED as ruled** — grammar uniform in the layout dirs, allowlist only at the flat root |
| F5 false-invariant docstrings | **CLOSED** — all three now state what the code does |
| F6 nested strays | **CLOSED** — both scans recursive, depth is part of the name test |
| F7 duplicated error string | **CLOSED** — one `_selectable_field_reader()`, message written once |

The original handoff's item 2 still holds (`include_retired` defaults False on every
scanning primitive, correctly absent from `fetch`). The three self-swept finds beyond the
brief are real and correctly fixed. The `.gitkeep` reshape is forced by the ruled fix and
explicitly granted by the handoff.

**Close criteria.** C2 met (containment reproduced: zero directory literals, globs or
status branches in `query_episodes.py`; all writer uses inside lines 470–804; Option-B
scaffolding still 0). C3 met, demonstrated both directions live. C4 met — six adversarial
traps, every fixture mutation-verified with teeth by my own source patches. C5 met,
demonstrated both directions. C6 met — verified at all three caller classes. One caveat
against C4's *spirit*: the criterion is worded about **omission**, and F1 is silent
**admission**, which it does not reach.

## Scope drift

None. `git status --short` is byte-identical to the implementer's reported state.
`tests/fixtures/episodes/` untouched, all three still exit 1 at their exact paths.
`.agent-work/LESSONS.md`, `scripts/apply_lessons_delta.py` and #300's manifest untouched.
No capture wiring, no consolidation. Record grammar and writer validation not relitigated.
`destination_for()` still owns the sole `status`→directory branch (one caller); the two
other `status` references are the record renderer, not path decisions.

## Evidence verdict

Every claimed command independently reproduced, with matching numbers. `enumerate` against
the real store exit 0. Create into a fresh `--store-root` bootstraps the layout and reads
back. `tests/test_episode_store.py`: **105 passed, 1 skipped, 16 subtests**. `tests/`:
**1262 passed, 3 skipped, 276 subtests** (third skip is the floor-interpreter guard, as
briefed). Three fixtures exit 1.

**The mutation claim, verified independently and in full.** I copied `scripts/`, `tests/`,
`docs/`, `episodes/` and `.github/` to an out-of-repo sandbox, patched each mutation into
the **real source**, and re-ran the suite in a fresh interpreter — the method the
implementer names, not the in-process monkeypatch the previous review showed cannot work.
Sandbox baseline reproduced exactly (105/1/16). **All 17 are red, and every single failure
count matches the reported table**: M1=67, M2=9, M3=2, M4=3, M5=6, M6=1, M6b=1, M7=1,
M7b=1, M8=11, M9=1, M10=1, M11=2, M12=6, M13=2, M14=1, M15=3.

**The self-reported M6 hole is true, and I confirmed it by experiment rather than taking
it.** Weakening the test assertion back to the substring `"missing store"` and re-applying
M6 gives **105 passed, 1 skipped — fully green with the guard deleted.** With the shipped
`"is not a directory"` assertion it goes red. The claim that the stronger method caught
what the weaker one hid is exactly, demonstrably correct.

Test mode `test-first` is satisfied and **honestly reported**, including the F2 slice where
red was obtained by temporarily reverting real source rather than being claimed as clean
TDD. That disclosure is the right call and worth saying so.

## Code/doc quality

`docs/EPISODE_STORE.md` §7 describes what shipped, in detail and without over-claim; the
correction of the "cost exactly what the seams promised" paragraph into a statement of what
the seams did **not** protect against is the most valuable paragraph in the diff, and its
transferable question — *what did membership stop being a property of?* — is the right
lesson stated at the right altitude. Option B survives as rejected-with-reason (lines
413–427) with its trade-offs intact. §10, `episodes/README.md` and both `.gitkeep` bodies
are accurate. §1 is stale (F2).

**Fowler pass** (12 baseline smells visited, verifier exit 0). Flagged: `large-class` +
`divergent-change` (the writer is now 1298 lines with five reasons to change — TC1,
correctly deferred by the handoff but a larger deferral than last time), `duplicated-code`
(the `root / sub / f"{id}.md"` address expression written four times — precisely where the
classifier is absent, so it is F1's mechanical shape), `primitive-obsession` (bare-`str`
ids — flagged as F1's root cause by the previous review, still unaddressed, and the direct
cause of this review's F1), `comments-as-deodorant` (downgraded, not cleared: the
false-invariant docstrings are genuinely repaired). Overridden with logged standards:
`long-method`, `feature-envy`, `data-clumps`, `speculative-generality` — the last on the
strength of M11/M15/M6/M6b all going red, since a guard that fails when deleted is not
speculative.

## Map impact verdict

- **Evidence supports claimed change:** yes, including `claim:retrieval-does-not-silently-omit`,
  which the previous review could not support. Six traps, each with a fixture I verified has
  teeth.
- **Constraints not violated:** `constraint:markdown-in-git` and
  `constraint:stochastic-boundary-B0.1` intact — no ranking, scoring, similarity or
  embedding, confirmed by reading every primitive.
- **Notes match the diff:** yes. The correction owed on
  `constraint:retired-is-excluded-not-deleted` is genuinely discharged — structural for
  `fetch` and the writer too, probe-confirmed, not just asserted.
- **Decision candidates surfaced:** yes; all three graded `settled/measured` and I
  reproduced each measurement.
- **Durable context routed:** yes, with the gap named in merge condition (1).

## Reconciliation check

No structural baseline divergence. F2 is the one doc/code mismatch and it is inside this
gate's own document.

## Blockers

None. F1 is routed rather than blocking, on the conditions above.

## Out-of-scope observations

- **TC1 stands and has grown**: split `scripts/apply_episode_delta.py` (1298 lines, five
  independent reasons to change). Named follow-up after #301 merges.
- **A Linux confirmation run before merge**, now with two motivations rather than one: the
  case-insensitive `.exists()` lookup divergence the previous review found, and F3's
  platform-dependent glob classification.
- The implementer's own triage list (3-vs-2 skip count → #313; `HalfRetiredStore`
  reachability; `apply_lessons_delta.py` still flat → #308) I checked and agree with.

## What I could not check

- **Broken symlinks under `active/`.** The `is_file()` branch that would silently drop one
  is demonstrated via a directory; the symlink instance itself I could not create
  (`WinError 1314`, no privilege on this host).
- **POSIX behaviour**, for both halves of F3 and for the previously-recorded
  case-insensitivity divergence. Ran on Windows/NTFS throughout. The POSIX half of F3 is
  derived from documented `pathlib`/`fnmatch` semantics, not observed.
- **Real hard-kill / power-loss behaviour.** Only the injected-fault path is testable; the
  residue is uncoverable by design and I did not kill a process mid-`commit()`.
- **Concurrent retirement of the same episode in two worktrees** (a rename/delete conflict
  shape). Not in this gate's criteria; noted only, unchanged from the previous review.

## Cleanup

Nothing stray. `git status --short` is byte-identical to the handoff's; `episodes/` contains
exactly `README.md`, `active/.gitkeep`, `retired/.gitkeep`. Every probe, the mutation
sandbox, and the Fowler record ran under the session scratchpad, outside the repo. No repo
file edited. The only thing I wrote inside the worktree is this result and the survey under
`.agent-work/301/g4-review-2/`.

## Workflow Feedback

- **Handoff gaps:** the re-review brief's probe list was excellent and is why F1 landed —
  but the item that actually found it was *not* on the list. The list named six file-shaped
  probes (stem-vs-content, flat-root, case, nested, long id, extensions); every one of those
  came back clean or minor. F1 came from turning the list's own question around: the brief
  asked "what does a grammar get wrong that a list did not" and answered it *about files*,
  when the structural answer is *about the direction data flows* — a grammar can classify an
  id you were handed, and a list never could, so the grammar creates an obligation at the
  input boundary that no one has ever had before. A probe list phrased as "**where does an id
  enter this system, and is it classified at each entrance?**" would have gone straight there.
  Worth carrying into the next re-review brief: when a classifier changes shape, enumerate
  its *call sites*, not its *inputs*.
- **Context rediscovered:** that `consolidated-into` / `superseded-by` are validated as
  strings and never as ids. That fact lives in `_validate_retire()`, three hundred lines from
  the seam block, and it is what turns F1 from a probe curiosity into something #308 will
  meet. Neither handoff mentions it, and the g2 exclusion ("do not relitigate the writer's
  validation design") actively discourages looking there — I nearly did not.
- **Instructions improvised around:** same two the previous reviewer reported, both still
  unfixed in the skill text. (1) SKILL.md says "`advance` that check" and "run the engine's
  final `advance`/`consolidate`", but `advance` is refused on a `survey` — `record` is the
  verb. (2) `flag-candidate`'s required `--from` / `--statement` are still undocumented in
  SKILL.md. Neither cost me a failed call only because the previous result recorded them,
  which is a nice demonstration of the feedback loop working and a poor substitute for
  fixing the text.
- **What would have made this easier:** the previous review asked for "one line in the
  handoff running the primitives against the **real** store", and the rework's evidence
  block now leads with exactly that — it is the first thing in the result and it is why
  F1-the-original was checkable in one command. That request was answered well and the
  practice is worth making standard for any gate that ships a data store: **the first
  evidence line should be the shipped artifact answering its own tooling.**

## Return status

`complete`
