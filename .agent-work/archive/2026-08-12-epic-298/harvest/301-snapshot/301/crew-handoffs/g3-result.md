# Implementation Result

VERDICT: COMPLETE

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3` — layout-independent retrieval + the cross-session / cross-worktree acceptance exercise (issue #301, epic-298)

## Completed slice

Built `scripts/query_episodes.py` (deterministic retrieval: fetch by id, enumerate,
select by exact field value / set membership, enumerate neighbours) and the acceptance
exercise for the whole issue in `tests/test_episode_store.py`. Applied the one authorized
carried fix from the g2 review. **41 new tests**; the retirement layout is untouched.

Driven through the engine end to end: `.agent-work/301/crew-handoffs/g3-implementer-plan.json`,
10 items, session `impl-301-g3`.

## Scope

**Files changed:**
- `scripts/query_episodes.py` — **new** (untracked; appears in `git status`, not `git diff`)
- `tests/test_episode_store.py` — extended (+1055/-8); the existing 24 tests are unrestructured
- `scripts/apply_episode_delta.py` — **one line**, the authorized fix-now

No new fixture files were needed: every adversarial case is built by seeding through the
real writer, so no hand-authored file can drift from what the writer actually produces.
The three existing fixtures are untouched.

**Specific exclusions touched:** no. Retirement layout unbound; no retirement-dependent
retrieval; `apply_lessons_delta.py` / `LESSONS.md` untouched; no capture wiring; no
consolidation/rhyme-search; `context-manifest-ref` stays an opaque string; `durable_root()`
never called.

## Behavior changed

Yes — new retrieval surface (module + CLI), plus one writer bug fix: `artifact-ref`
entries are now `.strip()`ed before storage, so `render(parse(text)) == text` holds for
an `artifact-ref` carrying whitespace.

## Test mode
**Required:** `test-first (TDD strongly preferred)`
**Satisfied:** `yes, with two honestly-declared exceptions.` m1/m2/m3/m4 were genuine
red→green (failing output observed and attested each time). m5 (C2) and m7 (C4) had **no
honest RED available** — the code they exercise was already green from earlier slices, so
a failing-first version would have had to be manufactured. Rather than fake a red, I
falsified each exercise and **baked the falsification in as a permanent test** (see
Evidence 1b and 3). m6 produced a real, unplanned RED that turned out to be a finding.

## Evidence

### 1. C2 — cross-session retrieval across a REAL process boundary

`tests/test_episode_store.py::CrossSessionRetrievalTests`. Session 1 launches
`apply_episode_delta.py`; session 2 launches `query_episodes.py`. Both via
`subprocess.Popen` + `sys.executable`, so the parent observes each child's OS pid
directly; the query child additionally reports its **own** `os.getpid()` inside its JSON
answer, so the answer is tied to the process that produced it rather than assumed.

```
pytest/parent process pid : 24092
session 1 (writer) argv   : ...\python.exe ...\scripts\apply_episode_delta.py ...
session 1 (writer) pid    : 23680 -> exited rc 0 | stdout: created episode:governor-268-001
session 2 (query)  argv   : ...\python.exe ...\scripts\query_episodes.py --store-root ...\episodes fetch governor-268-001
session 2 (query)  pid    : 3164 -> exited rc 0
pid REPORTED BY the query child inside its own JSON answer: 3164
  == the pid the parent observed for that child? True
  all three distinct? True
retrieved ids: ['governor-268-001']
retrieved observed-behavior: ['The Admiral spine carries the identical missing-fallback defect, unnamed by the launch order.']
sys.executable used to boot each session: C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

The assertions that make this a boundary rather than a claim:

```python
self.assertNotEqual(seed["pid"], query["pid"])
self.assertNotIn(os.getpid(), (seed["pid"], query["pid"]))
self.assertEqual(payload["pid"], query["pid"])   # the answer came from THAT process
```

Session 2 is handed nothing but the store root and the id — no content, no handle, and
session 1 has already exited. `test_a_third_session_enumerates_what_the_first_two_never_told_it_about`
asserts `len({pid1, pid2, pid3, os.getpid()}) == 4` and passes **no id at all** to the
enumerating session: the store on disk is the only channel.

**1b. Falsification (baked in):** `test_the_cross_session_exercise_is_not_vacuous` points
an identical session 2 at a different, empty store root and asserts `rc == 2` /
`"no such episode"`. So the exercise genuinely depends on store contents, not on anything
ambient in the interpreter.

### 2. C3 — cross-worktree sharing through GIT

`tests/test_episode_store.py::CrossWorktreeSharingTests`. Real `git init` + two real
`git worktree add`s against a temp repo; `user.email`/`user.name`/`commit.gpgsign=false`
set **locally** so commit cannot fail on identity or signing.

```
$ git worktree list
C:/.../episode-store-worktrees-e1qlt1jw/origin    516258a [main]
C:/.../episode-store-worktrees-e1qlt1jw/wt-reader 516258a [reader-branch]
C:/.../episode-store-worktrees-e1qlt1jw/wt-writer 516258a [writer-branch]

wt-reader/.git is a file (linked worktree marker), not a dir: True
  contents: gitdir: C:/.../origin/.git/worktrees/wt-reader

BEFORE any commit -> query in wt-reader:
   []
seeded governor-268-001 in wt-writer (pid 6048), NOT yet committed
  query in wt-reader: [] <- still invisible
committed in wt-writer; query in wt-reader: [] <- STILL invisible (commit hasn't reached it)

after the ordinary git path (merge to main, merge main into wt-reader):
  query in wt-reader, fresh interpreter pid 21524 -> ['governor-268-001']
  store root the reader queried: C:\...\wt-reader\episodes
  observed-behavior: The Admiral spine carries the identical missing-fallback defect, unnamed by the launch order.
  blob hash in wt-writer: 50c5c8b2e91595ae2bfb7526f3e6de8a66310a52
  blob hash in wt-reader: 50c5c8b2e91595ae2bfb7526f3e6de8a66310a52
  raw working-tree bytes identical? False | CRLF in reader copy? True
```

**Why this is a real worktree boundary, not a directory-name simulation.** Three
independent proofs, all asserted in the test:

1. A linked worktree's `.git` is a **file** containing `gitdir: .../.git/worktrees/<name>`,
   not a directory. Asserted for both worktrees — a simulated directory cannot pass it.
2. The **absent → still-absent-after-local-commit → present-only-after-merge** transition
   is observed. If the two worktrees shared a filesystem, the episode would have appeared
   at step 1. It appears only after `git merge` onto main and into the reader.
3. `test_the_two_worktrees_do_not_share_a_directory` is a dedicated falsification: an
   **uncommitted** episode written in worktree A is invisible in worktree B. What crosses
   is the commit, not the filesystem.

### 3. C4 — non-foreclosure, byte-identical sibling

`tests/test_episode_store.py::NonForeclosureTests`. Disputed exactly `a4` (impact-cost).
The file is read with `read_bytes()` — no decoding, no newline translation anywhere in
the comparison path, since Python's universal-newline handling would happily make a CRLF
and an LF file compare equal and hand back a false pass.

```
DISPUTED field a4 (impact-cost) — read back by retrieval:
   standing: disputed | history entries: 1
SIBLING field a3 (observed-behavior) — read back by retrieval:
   standing: active | history entries: 0

a4 raw bytes BEFORE: b'### assertion:governor-268-001.a4\n- kind: impact-cost\n- strength: medium\n- lifecycle-standing: active\n- statement: One e' ...
a4 raw bytes AFTER : b'### assertion:governor-268-001.a4\n- kind: impact-cost\n- strength: medium\n- lifecycle-standing: disputed\n- statement: One' ...
a4 changed? True

a3 raw bytes BEFORE: b'### assertion:governor-268-001.a3\n- kind: observed-behavior\n- strength: strong\n- lifecycle-standing: active\n- statement: The Admiral spine carries the identical missing-fallback defect, unnamed by the launch order.'
a3 raw bytes AFTER : b'### assertion:governor-268-001.a3\n- kind: observed-behavior\n- strength: strong\n- lifecycle-standing: active\n- statement: The Admiral spine carries the identical missing-fallback defect, unnamed by the launch order.'
a3 BYTE-IDENTICAL before and after? True
whole file changed? True | file bytes with a4-before->a4-after substituted == after? True
```

That last line is the strongest form of the claim and is asserted in the test: substituting
a4's before-block with a4's after-block reproduces the **entire** new file byte for byte,
so a4 is the *only* delta anywhere in it. Two sibling tests add that the `## Mechanical`
block and the `## Retirement` block are byte-unchanged, and that a disputed episode is
still retrievable and still in the candidate set.

### 4. Silent omission — the adversarial fixture

`tests/test_episode_store.py::SilentOmissionTests`. Three episodes **all** genuinely carry
the target `artifact-ref`, positioned first, middle, and last in their respective lists.
`naive_select_dict_collapse` folds the `## Mechanical` block into a dict — the way a
reasonable person writes it — which keeps only the **last** `artifact-ref` line.

```
  governor-268-001: artifact-refs = ['docs/EPISODE_STORE.md', 'scripts/a.py', 'scripts/b.py']
  governor-268-002: artifact-refs = ['scripts/c.py', 'docs/EPISODE_STORE.md', 'scripts/d.py']
  governor-268-003: artifact-refs = ['scripts/e.py', 'scripts/f.py', 'docs/EPISODE_STORE.md']

query: which episodes carry artifact-ref == docs/EPISODE_STORE.md
  NAIVE (mechanical block folded into a dict): 1 of 3 -> ['governor-268-003']
  OURS  (field_values is list-valued):         3 of 3 -> ['governor-268-001', 'governor-268-002', 'governor-268-003']
  omitted by the naive version, with no error: ['governor-268-001', 'governor-268-002']
```

No exception, no warning, no partial-result flag — just a candidate set two records short.
The test asserts the property, not only the counts: `set(naive) < set(ours)`.

**The fix is structural, not a patch:** `field_values()` returns a **list for every
field**, including scalars. There is no scalar path a caller could take, so the collapse
has no way in.

Three further omission/exactness fixtures, each running naive-vs-ours over the same store:

- `test_naive_first_key_wins_silently_omits_the_other_join_key` — a neighbour enumeration
  that returns on the first matching join key omits the neighbour joined on the second.
  Naive `[by_ref]`, ours `[by_pair, by_ref]`.
- `test_enumeration_returns_every_episode_including_ones_a_run_glob_would_miss` — enumerating
  by run-prefix glob (tempting, since §2 makes the filename a free run-lookup key) silently
  drops every other run's episodes.
- `test_select_matches_whole_values_not_prefixes` — the other direction: a substring search
  **over**-returns (`g1` dragging in `g1-implement`). Exact match does neither.

Plus the non-silent guard: an unrecognized field name **raises** (`rc 1`, naming the
selectable fields) rather than returning an empty set, so a typo can never masquerade as
a genuine no-match.

### 5. C5 — exact-match / set-membership only (confirmatory)

`MechanicalOnlyRetrievalTests`: candidate set independent of write order; no
`score`/`rank`/`similarity`/`distance`/`relevance`/`embedding`/`confidence` key anywhere in
the output; no ranking/embedding imports; and neighbours are **not** ordered by how many
join keys they share (counting shared keys would be scoring wearing a sort's clothes).
Results are id-sorted purely for determinism.

### 6. Layout independence (confirmatory, and stronger than a source grep)

`LayoutIndependenceTests::test_retrieval_survives_flipping_the_layout_adapter` runs **every**
primitive under **both** candidate adapters. Option A really does write to `store-A/active/`
(asserted) and Option B stays flat (asserted) — and all four primitives return identical
answers, because they ask the seams rather than the filesystem. A source guard additionally
rejects an inlined status/directory check; it is demonstrably not vacuous, having caught two
real occurrences before I narrowed it to *branches* on status rather than the word.

`test_the_membership_seam_is_left_for_g4_and_still_answers` confirms
`is_episode_in_ordinary_search()` works, so g4's scan-then-filter composition has both
halves present — while **no** primitive here calls it, because no retirement-dependent
retrieval was built.

### 7. The authorized fix-now (confirmatory)

TDD red, verbatim, before the fix:
```
E       AssertionError: '- artifact-ref: docs/EPISODE_STORE.md\n' not found in '...
        - artifact-ref: docs/EPISODE_STORE.md   \n- artifact-ref:   scripts/apply_episode_delta.py  \n...'
```
Fix — one line in `_apply_create`, matching every sibling mechanical field:
```python
-        artifact_refs=list(mech.get("artifact-ref", [])),
+        artifact_refs=[ref.strip() for ref in mech.get("artifact-ref", [])],
```
Regression test `test_artifact_ref_with_trailing_whitespace_round_trips` asserts
`render(parse(text)) == text` over **dirty** input — a round trip over clean input could
never have caught this.

### 8. Verification commands (run foreground to completion)

```bash
$ python -m pytest tests/test_episode_store.py -q
65 passed, 16 subtests passed in 2.58s          # was 24; +41 new

$ python -m pytest tests/ -q
1222 passed, 2 skipped, 276 subtests passed in 36.30s   # baseline 1181 passed, 2 skipped -> +41, no regression

$ git status --short
 M scripts/apply_episode_delta.py
 M tests/test_episode_store.py
?? scripts/query_episodes.py

$ git status --short -- episodes/ | wc -l
0                                # the real store stayed clean
$ ls episodes/
README.md
```

Zero temp git repos leaked after the full suite (`ls -d .../episode-store-worktrees-* | wc -l` → `0`),
so the Windows read-only `onerror` handler works.

**Result:** `pass`

## TDD evidence

- Failing test observed: m1 (`- artifact-ref: ...   ` trailing spaces, quoted above); m2 (8 failed, module absent); m3 (9 failed); m4 (6 failed); m6 (real byte-identity failure — see Finding 1).
- Passing test observed: every slice green before its engine `advance`; full suite 1222 passed.
- Refactor while green: yes — the layout source-guard was narrowed twice (after it fired on serialization rather than on a branch) with the suite green throughout.

## Docs/contracts touched
- None. No contract conflict found; `docs/EPISODE_STORE.md` is unmodified.

## Decisions logged (within granted authority)

- **Neighbour join keys** — (1) any shared `artifact-ref` value; (2) the `(role, spine-step)`
  **pair**. Rationale in the module: §6's Stratum A mapping calls `artifact-ref` lines an
  assertion's *supporting evidence*, so a shared artifact is a shared piece of evidence —
  the strongest mechanical "about the same thing" signal available. The pair is a pair on
  purpose: `role` alone would make every implementer episode a neighbour of every other,
  producing a candidate set so large it stops being one. Explicitly **not** join keys:
  `run` (already a free lookup key via the filename), `project`, and every counter field.
- **Enumeration is unfiltered** — `iter_episode_ids(include_retired=True)`, no membership
  filter. Under the currently-bound placeholder adapter `include_retired` is a no-op, so
  this is the layout-independent "enumerate all". The ordinary-search-restricted and
  history-inclusive variants are g4's and are deliberately absent.
- **CLI shape** — `fetch` / `enumerate` / `select --field --value[ --value ...]` /
  `neighbours`, all emitting one JSON envelope. Exit codes: `0` answered, `1` invalid query
  (never an empty result standing in for a rejected one), `2` no such episode.
- **`pid` in the envelope** — provenance: it names the OS process that produced the answer,
  and is what lets the cross-session exercise tie an answer to a process rather than assume it.
- **Newline handling** — reads use `encoding="utf-8", newline=""` (matching the writer);
  every byte-identity assertion uses `read_bytes()`, never decoded text.

## Map Impact

- **Structural anchors touched:** new `struct:scripts/query_episodes.py` (module, ~330 lines)
  — the read side of the store, built entirely on g2's seams; `scripts/apply_episode_delta.py`
  (one-line fix in `_apply_create`); `tests/test_episode_store.py` (+41 tests).
- **Capabilities added:** `capability:episode-retrieval` — fetch/enumerate/select/neighbours,
  deterministic and mechanical; the surface a downstream stochastic sensor (#308) sits on top of.
- **Constraints touched:** `constraint:stochastic-boundary-B0.1` honored (nothing ranks, scores,
  or infers); `constraint:markdown-in-git` honored (no index, no DB); `constraint:cross-worktree-durability`
  **now measured, not assumed** — see Finding 1 for the one place it is narrower than it reads.
- **Decisions:** `decision:episode-store-shape` untouched (`settled/human`, not mine — the
  retirement layout is left unbound and is proven unbound behaviorally).
  `decision:store-lives-at-a-tracked-path` (`settled/measured`) — **re-measured and upheld**
  by the C3 exercise: the tracked path really does deliver across a worktree boundary via git.
- **Claims produced:** `claim:seeded-episode-survives-a-session-boundary` (Evidence 1);
  `claim:seeded-episode-survives-a-worktree-boundary` (Evidence 2);
  `claim:an-agent-supplied-claim-can-be-disputed-individually` (Evidence 3);
  `claim:retrieval-does-not-silently-omit` (Evidence 4).
- **Trust limitations:** a new one, Finding 1 below — an episode's *working-tree bytes* are
  not worktree-stable on Windows. Its git blob hash is.
- **Triage candidates:** Findings 1 and 2 below.

## Assumptions

- "Enumerate all episodes" is the layout-independent primitive for this gate; the
  retirement-restricted variants are g4's. Stated because the handoff excludes both
  "ordinary-search exclusion" **and** "history-inclusive enumeration", and under the
  current placeholder adapter those are the same call — I built the unfiltered scan and
  documented the g4 obligation rather than exposing an `include_retired` parameter.
- Adversarial fixtures are seeded through the real writer rather than hand-authored, so no
  fixture can encode a file shape the writer could not produce.

## Stop conditions hit
- None. C3 **was** made real, so the Admiral's "report it rather than weaken it"
  instruction did not need to be exercised — though it did surface Finding 1 en route.

## Out-of-scope observations

**Finding 1 (real, worth routing — surfaced by a genuine test failure).** An episode's
**working-tree bytes are not stable across worktrees on Windows.** `core.autocrlf` is
`true` at system level on this machine, so git converts line endings on checkout: the
writer emits LF-only, and a second worktree materializing the same commit gets CRLF. My
first C3 run failed on exactly this (`b'...\n' != b'...\r\n'`).

This does **not** break the store — the record and the git blob hash are identical across
worktrees, and §8's `<ref>@<revision>` blob-hash pinning is exactly the right mechanism, so
the contract is intact. But **#308's consolidation/dedup, or any future content-addressing
that hashes the file it finds in its own worktree, would be silently wrong on Windows.** I
pinned this as a named test (`test_working_tree_bytes_are_not_the_cross_worktree_identity`)
rather than leaving it as prose. Candidate remedy, **not applied** (outside allowed scope,
and it is a store-shape decision): a `.gitattributes` entry pinning `episodes/*.md` to
`text eol=lf`. The repo's `.gitattributes` currently says only `* text=auto`. Recommend
routing to g4 or #308.

**Finding 2 (minor).** `is_episode_in_ordinary_search()` returns `False` for a nonexistent
id — indistinguishable from "exists but retired". Harmless today (nothing calls it), but
g4 wires it into the scan-then-filter composition, where a caller may want those two cases
apart. Flagging so g4 decides deliberately rather than inheriting it.

## Workflow Feedback

- **Handoff gaps:** one real tension. **"Retrieval primitives to build"** says *enumerate all
  episodes*, while **"Do NOT build the retirement-dependent variants"** excludes both
  *ordinary-search exclusion* **and** *history-inclusive enumeration* — and under the
  currently-bound placeholder adapter those two exclusions between them describe the only
  two ways to call `iter_episode_ids()`. Read literally, no enumeration was buildable. I
  resolved it as "build the unfiltered scan, document the g4 obligation, expose no
  `include_retired` parameter" and logged it under Assumptions, but a future handoff should
  say which `include_retired` value the gate is expected to pass.
- **Context rediscovered:** (a) the `.gitattributes` / `core.autocrlf` interaction — the
  handoff warned about `\r\n` for the C4 byte assertion (within one worktree, where it turned
  out to be a non-issue) but the place it actually bit was C3 *across* worktrees, which the
  warning did not anticipate; (b) that the seams take `root` as an explicit parameter
  (`iter_episode_ids(root, include_retired)`), which the seam table in `EPISODE_STORE.md`
  writes without it — a one-line signature note in the anchors would have saved a read.
- **Instructions improvised around:** the plan template mandates a TDD-red postcondition per
  item, but two slices (C2, C4) exercise code that earlier slices had already turned green,
  so no honest red existed. Rather than manufacture one or waive the condition, I attested
  it with the truth and substituted a *falsification* — proving each exercise fails when its
  premise is removed — then baked that falsification in as a permanent test. I'd suggest the
  template name this explicitly: for an acceptance-exercise item over already-green code,
  "falsify the exercise" is the right red-equivalent, and it is strictly more valuable than
  a staged failure.
- **What would have made this easier:** the handoff's constraints say tests write to
  `tmp_path`, which is pytest-fixture vocabulary — but `tests/test_episode_store.py` is
  `unittest`-based and uses `tempfile.TemporaryDirectory`. I followed the existing file's
  convention (crew doctrine: match the surrounding code). Naming the temp-root *requirement*
  rather than a specific fixture API would remove the ambiguity.

## Return status
`complete`
