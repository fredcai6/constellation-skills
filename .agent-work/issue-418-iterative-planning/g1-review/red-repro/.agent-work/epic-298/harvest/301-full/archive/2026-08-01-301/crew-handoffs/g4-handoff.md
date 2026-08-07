# Implementer Handoff

## Gate
`g4` — bind the ratified retirement layout + retirement-dependent retrieval (issue #301)

## The ruling that unblocks this gate

The retirement layout was held for human ratification through gates g1–g3. **It has now been
ruled.** Tommy's answer, verbatim:

> *"move the file, prefer to keep files clean of history unless they're historical. archives are
> available strats."*

So: **retirement MOVES the file** — `episodes/active/<id>.md` → `episodes/retired/<id>.md`.
That is **Option A** in `docs/EPISODE_STORE.md` §7. Option B (a `status` field filtered
negatively) is **not** chosen and its adapters come out.

**The second half of the ruling is a design principle, not decoration.** *Files stay clean of
history unless they are themselves historical, and archives are a legitimate separate strategy.*
Read that as licence for `retired/` to be a **genuine archive** — not a second live search space
that every query has to remember to exclude. Ordinary retrieval globs `active/` and simply never
looks at `retired/`; history-inclusive retrieval is a deliberate, separate act.

## Task

Four things, in this order:

1. **Bind Option A at the four named seams**, and only there.
2. **Remove the Option-B adapters** now that the choice is made — they were scaffolding for a
   held decision, and the decision is no longer held.
3. **Add retirement-dependent retrieval** to `scripts/query_episodes.py`, plus its adversarial
   fixtures.
4. **Clear the two doc corrections** `docs/EPISODE_STORE.md` owes (below).

## Protected Intent

1. **Retired means excluded from ordinary rhyme-search and RETAINED in history.** Never
   deletion, never truncation. Under Option A that is now structural: the file moves, it does
   not vanish.
2. **Retrieval must never silently omit** a record it should return.
3. **The move must be atomic-ish and reversible in principle** — a retirement that half-happens
   (fields updated, file not moved, or vice versa) is a corrupt store.

## Close Criteria

- **C2 — Option A is bound at the single seam set and nowhere else.** The diff touches exactly
  the adapter implementations; no call site inlines a directory check. Prove it: no primitive
  outside the seams references `active/` or `retired/` as a literal path.
- **C3 — a retired episode is ABSENT from ordinary retrieval AND PRESENT in history-inclusive
  retrieval.** Both directions proven. This is the acceptance criterion for "excluded from
  ordinary rhyme-search, retained in history."
- **C4 — an adversarial fixture proves retrieval does not silently omit.** Keep and adapt the
  fixture that started this whole thread: an episode in a lifecycle state that is **neither
  active nor retired** (e.g. a `disputed` core assertion on a non-retired episode) must still
  appear in ordinary search. Under Option A the trap changes shape rather than disappearing —
  see "the trap under Option A" below. Also prove a free-text field containing a forged
  `- status: retired` line does **not** change which set the episode falls in (under Option A it
  structurally cannot, which is the point — assert it).
- **C5 — the #308 companion is not precluded:** with one episode of a cluster retired, its
  still-active neighbours remain findable by ordinary retrieval and the retired one stays
  reachable history-inclusively.
- **C6 — the retirement move is safe.** Prove the store is never left half-retired: if the field
  update succeeds and the move fails (or vice versa), the store must end in a consistent state.
  Use the same staging discipline `commit()` already uses.

## The trap under Option A — do not let it vanish quietly

Under Option B the silent-omission trap was a *positive allowlist*: enumerating
`status: active` silently dropped a legitimately-not-retired `disputed` episode. Option A makes
that specific trap structurally impossible, because membership is a directory fact.

**It does not remove the class, it relocates it.** Under Option A the equivalent traps are:
- a **glob that misses a subdirectory** — e.g. `episodes/*.md` after the layout gains
  `active/`/`retired/`, silently returning nothing or only strays;
- **history-inclusive enumeration that forgets to union both directories**, silently returning
  only the active half;
- **a stray file at the old flat path** (`episodes/<id>.md`, neither `active/` nor `retired/`)
  being silently ignored by both — it belongs to neither set and should be surfaced as
  malformed, not skipped.

Write a fixture for each. The third is the one most likely to be missed and is a real migration
hazard: `episodes/README.md` already lives at the flat root and must be excluded *deliberately*
rather than by accident.

## The two doc corrections this gate owes

Both were deliberately deferred to g4. From `.agent-work/301/STATE_NOTE.md`:

1. **§§8/10 describe retirement-dependent retrieval as if it already exists.** It did not — it is
   what you are building now. Correct them to match what actually ships.
2. **§9 says a second worktree "sees the identical file content."** True at the blob level,
   **misleading at the byte level** — the repo's `.gitattributes` sets `* text=auto`, so checkout
   converts line endings and working-tree bytes differ by platform. My own test
   `test_working_tree_bytes_are_not_the_cross_worktree_identity` pins exactly that, so the doc
   and the test currently disagree in tone. Say: *the same content and the same blob OID —
   working-tree bytes may differ by platform.* Context on issue **#319**.

Also update §7 itself: the layout is **no longer an open seam**. Record that Option A was
ratified, quote the ruling, keep the Option-B description as *rejected-with-reason* rather than
deleting it (the reasoning is why the seams exist), and state the archive principle.

## Allowed Scope

- `scripts/apply_episode_delta.py` — the four seams and the retire op
- `scripts/query_episodes.py` — retirement-dependent retrieval
- `tests/test_episode_store.py` — extend; do **not** restructure the existing 68 tests
- `tests/fixtures/episodes/*.json` — new fixtures as needed; **do not rename or alter the three
  existing ones**, the g2 closeout invokes them by exact path
- `docs/EPISODE_STORE.md` — the corrections above
- `episodes/` — the `active/`/`retired/` layout plus tracked placeholders so git keeps them

## Specific Exclusions

- **Do NOT modify `scripts/apply_lessons_delta.py` or `.agent-work/LESSONS.md`** (issue #308 owns
  any cutover).
- **Do NOT build capture wiring** (#305) or the consolidation / rhyme-search loop (#308). You may
  make consolidation *possible*; you may not implement it.
- **Do NOT design #300's manifest** — `context-manifest-ref` stays an opaque `<ref>@<revision>`.
- **Do NOT call `durable_root()`** — the store root seam resolves to tracked `episodes/`.
- Do not use `Path.read_text(newline=)` / `write_text(newline=)` — Python 3.13+, CI pins 3.12.
  Use the existing `read_text_exact` / `write_text_exact` helpers.

## Constraints

- **Markdown in git only.** No database, no index.
- **The store never guesses** — exact match and set membership only.
- Tests write to a **temp store root** (`tmp_path`), never the real `episodes/`.
- Use `git mv` semantics where the file is tracked, but the writer must also work on an untracked
  temp store (the tests' case) — plain filesystem move is acceptable; say what you chose and why.
- `python`, **not** `py`, for pytest.

## Map Anchors (inbound)

- **Structural:** `scripts/apply_episode_delta.py` (the seams), `scripts/query_episodes.py`,
  `docs/EPISODE_STORE.md` §7 (the contract), `tests/test_episode_store.py`.
- **Capability:** episode retirement and history-inclusive retrieval — completed by this gate.
- **Constraints:** `constraint:retired-is-excluded-not-deleted`;
  `constraint:stochastic-boundary-B0.1`; `constraint:markdown-in-git`.
- **Decision anchors:**
  - `decision:episode-store-shape` — **now RATIFIED**: D's record shape + A's file-move
    retirement + five grafts.
    `@grade: settled/human · leans g4 · settle: ruled by Tommy 2026-08-01, quoted above`
  - `decision:retired-is-an-archive-not-a-second-search-space` — from the ruling's second half.
    `@grade: settled/human · leans g4 · settle: ordinary retrieval never globs retired/`
- **Evidence expectations:** `claim:retired-episodes-leave-ordinary-search-and-stay-in-history`;
  `claim:retrieval-does-not-silently-omit`.

## Deliverable Path Check

- **Committed** — all of the above; `git check-ignore` exits **1** for `scripts/`, `tests/`,
  `docs/`, `episodes/` (verified; none ignored).
- `episodes/active/` and `episodes/retired/` are **new directories**: git does not track empty
  directories, so each needs a tracked placeholder or the layout vanishes at commit. g1 hit this
  exact hazard.

## Required Evidence

**Load-bearing — prove rigorously, with pasted output:**

1. **C3 both directions** — the retired episode absent from ordinary retrieval, present in
   history-inclusive. Paste both assertions.
2. **The three relocated silent-omission fixtures** (missed subdirectory, forgotten union, stray
   flat-path file). Show what a naive implementation returns versus yours.
3. **C6 half-retirement safety** — force a failure between the field update and the move, and
   show the store is consistent afterward.
4. **C2 seam containment** — show no primitive outside the seams references `active/`/`retired/`
   as a literal.

**Confirmatory — spot-check:** the doc corrections, C5.

## Verification Commands

```bash
python -m pytest tests/test_episode_store.py -q
python -m pytest tests/ -q                    # baseline 1223 passed, 2 skipped, plus yours
! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/misfiled-field-delta.json
! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/missing-retire-reason-delta.json
! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/newline-injection-delta.json
git ls-files episodes | grep -q .             # the layout is really tracked
git status --short
```

## Suggested Model Tier

`stronger` — this binds a ratified human decision, removes scaffolding, and relocates a
silent-failure class rather than eliminating it. Getting the relocation wrong would ship the
exact defect the whole gate sequence was built to prevent.

## Authority

**Already decided — do not re-litigate:** the file-move layout (Tommy, quoted above); D's record
shape and the five grafts; the tracked `episodes/` location; retirement policy; the store is
mechanical.

**You must NOT decide alone — stop and return:** anything that would change the record grammar;
anything touching `LESSONS.md`, `apply_lessons_delta.py`, or #300; any scope expansion into #305
or #308.

**You may decide** (log it): how the move is implemented and staged; whether the placeholders are
`README.md` or `.gitkeep`; the exact CLI surface for history-inclusive retrieval; fixture layout.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; required evidence cannot be produced; a
decision outside the given authority is needed; or **you find that binding Option A requires
changing a g3 retrieval primitive rather than only an adapter body** — the seams were designed
so it would not, and if that proves false it is a finding I need, not something to work around.

## Return Format

Return **IMPLEMENTER_RESULT** at `.agent-work/301/crew-handoffs/g4-result.md` with a literal
`VERDICT: COMPLETE` (or `VERDICT: BLOCKED` + reason), completed slice, files changed, evidence
with pasted output, assumptions, stop conditions hit, out-of-scope observations, and a
**non-empty Workflow Feedback** section.

Do not commit; I integrate and commit.
