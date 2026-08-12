# Implementer Handoff

## Gate
`g3` — layout-independent retrieval + the cross-session / cross-worktree acceptance exercise
(issue #301, epic-298)

## Task

Build **`scripts/query_episodes.py`** — deterministic retrieval over the episode store — and
**the acceptance exercise for the whole issue**, added to `tests/test_episode_store.py`.

This gate carries issue #301's headline acceptance criterion: *"a seeded episode is retrievable
across sessions."* A pre-ruling requires that criterion to be **exercised, not asserted**.

Read **`docs/EPISODE_STORE.md`** first (the frozen contract) and
**`scripts/apply_episode_delta.py`** (gate g2's writer, which you seed through and whose seams
you reuse).

## Protected Intent

1. **The acceptance criterion must be genuinely exercised.** A test that calls a function twice
   in one process has not crossed a session boundary.
2. **Retrieval must never silently omit** a record it should return. Silent omission is the
   failure mode this store's whole design fears — no error, no crash, just a candidate set one
   record short with no signal that it is short.
3. **The retirement layout stays unbound.** Retirement-dependent retrieval is gate g4's, not
   yours. See the scope fence.

## Test Mode

**TDD strongly preferred.** Per `lesson:round-trip-tests-prove-artifacts-not-parsers`, a
round-trip test over well-formed input proves the input was clean, not that your retrieval is
correct. **Pair every enumeration test with an adversarial fixture** authored to make a naive
implementation return a WRONG answer — especially a silent omission.

## Close Criteria

- **C2 — cross-session retrieval, exercised.** Seed an episode in one process; retrieve it in a
  **separately launched** process that shares only the working tree. The test must boot a
  genuinely fresh interpreter via `subprocess` + `sys.executable`. No in-process double-call, no
  shared module state, no warm cache.
- **C3 — cross-worktree sharing, exercised through git.** Seed **and commit** an episode in one
  linked worktree, then prove it is retrievable from a **second** worktree of the same repo
  after the ordinary git path. Use a real `git worktree add` against a temporary repo — do not
  simulate a worktree with a directory name. This is the mechanism that actually provides
  cross-worktree sharing now that the store is a tracked path.
- **C4 — non-foreclosure, exercised (the priority-1 obligation).** Seed an episode, apply a
  `dispute` op to **one** agent-supplied field, and prove by retrieval that: (a) the disputed
  field's standing changed; (b) a sibling agent-supplied field's standing is unchanged; and
  (c) the sibling's stored line is **byte-identical** before and after — so the record was
  **not** rewritten to accommodate the dispute.
- **C5 — retrieval is exact-match and set-membership only.** No ranking, no scoring, no
  similarity, no embedding. The candidate set handed to a downstream sensor is complete and
  unordered.

## Retrieval primitives to build

Per `docs/EPISODE_STORE.md` §8, and **routed through the named seams** — never inlining their
mechanics:

- **fetch by id** — via `resolve_episode_path()`.
- **enumerate all episodes** — via `iter_episode_ids()`.
- **select by exact field value / set membership** — enumerate, then match exactly. Line-anchor
  every match; a bare substring match is a defect.
- **enumerate neighbours** — for episode E, every *other* episode sharing at least one exact
  join key with E (e.g. a shared `artifact-ref`, or the same `role`+`spine-step` pair). The
  union is the candidate set a downstream sensor consumes: complete by construction, unranked.

**Do NOT build the retirement-dependent variants** (ordinary-search exclusion, history-inclusive
enumeration, the silent-omission-on-retirement fixture). Those are g4, after the layout is
ratified. Where a primitive would need `is_episode_in_ordinary_search()`, call the seam and let
its current placeholder adapter answer — do not inline a status check or a directory check.

## Fix-now, carried from the g2 review

The g2 reviewer demonstrated one further instance of g2's root-cause class, judged non-blocking
there and routed here: **`artifact-ref` entries are never `.strip()`ed before storage, while
`parse_episode()` strips the whole line before matching.** So an `artifact-ref` with trailing
whitespace validates, writes, and then silently loses that whitespace on the next parse —
`render(parse(text)) != text`. One-line fix in `scripts/apply_episode_delta.py`; add a
round-trip test that would have caught it. You are authorized to make exactly this fix.

## Allowed Scope

- `scripts/query_episodes.py` (new)
- `tests/test_episode_store.py` (extend — do **not** restructure the existing 24 tests)
- `tests/fixtures/episodes/*.json` (new fixtures as needed; **do not rename or alter the three
  existing ones** — the g2 closeout invokes them by exact path)
- `scripts/apply_episode_delta.py` — **only** the one-line `artifact-ref` strip fix above
- `docs/EPISODE_STORE.md` — only if you find a genuine contract conflict; flag it loudly

## Specific Exclusions

- **Do NOT bind the retirement layout** (gate g4, after human ratification).
- **Do NOT build retirement-dependent retrieval** (gate g4).
- **Do NOT modify `scripts/apply_lessons_delta.py` or `.agent-work/LESSONS.md`** (issue #308
  owns any cutover).
- **Do NOT build capture wiring** (issue #305) or consolidation / rhyme-search (issue #308).
- **Do NOT design issue #300's manifest** — `context-manifest-ref` stays an opaque
  `<ref>@<revision>` string.
- **Do NOT call `durable_root()`** — use the g1 store-root seam.

## Constraints

- **Markdown in git only.** No database, no index, no query engine.
- **The store never guesses.** Retrieval is mechanical; rhyme detection is a downstream sensor
  job owned at #308.
- Tests write to a **temp store root** (`tmp_path`), never the real `episodes/` directory. The
  repo must stay clean and the suite order-independent.
- **Windows + Git Bash.** `\r\n` translation is a live hazard for byte-identical assertions
  (C4c). Be deliberate about `encoding="utf-8"` and newline handling, and say what you chose.
- The C3 worktree test will create temp git repos: set `user.email`/`user.name` locally in the
  temp repo so `git commit` cannot fail on an unconfigured identity, and make cleanup robust on
  Windows (read-only `.git` files resist `shutil.rmtree`; an `onerror` handler that chmods and
  retries is the usual fix).
- If any test drives concurrent file I/O, `lesson:test-harness-concurrency-failsafe` applies:
  `try/except` with a guaranteed stop-signal in `finally`, `daemon=True` helper threads.

## Map Anchors (inbound)

- **Structural:** `scripts/apply_episode_delta.py` (g2's writer — the seeding path and the seam
  definitions); `docs/EPISODE_STORE.md` §§7–8 (the frozen retrieval contract); new:
  `scripts/query_episodes.py`.
- **Capability:** episode retrieval — the mechanical surface a downstream stochastic sensor
  works on top of.
- **Constraints:** `constraint:stochastic-boundary-B0.1`; `constraint:markdown-in-git`;
  `constraint:cross-worktree-durability`.
- **Decision anchors:**
  - `decision:episode-store-shape` — record shape and retirement mechanism.
    `@grade: settled/human · leans g3,g4 · settle: held for Tommy; NOT yours to choose`
  - `decision:store-lives-at-a-tracked-path` — closed at g1.
    `@grade: settled/measured · leans g1,g2,g3 · settle: git ls-files episodes returns non-empty`
- **Evidence expectations:** `claim:seeded-episode-survives-a-session-boundary`;
  `claim:seeded-episode-survives-a-worktree-boundary`;
  `claim:an-agent-supplied-claim-can-be-disputed-individually`;
  `claim:retrieval-does-not-silently-omit`.
- **Map confidence flags:** issue #300's manifest is live and unverified in a concurrent
  worktree — treat its reference as opaque.

## Deliverable Path Check

- **Committed** — `scripts/query_episodes.py`, the `tests/` additions. `git check-ignore` exits
  **1** for `scripts/` and `tests/` (verified before dispatch; neither is ignored).
- `scripts/query_episodes.py` is **new**: untracked until staged, so it appears in
  `git status`, not `git diff`.

## Required Evidence

**Load-bearing — prove rigorously, with pasted output:**

1. **C2** — the cross-session test, showing it really boots a separate interpreter (paste the
   subprocess invocation and the assertion).
2. **C3** — the cross-worktree test, showing a real `git worktree add` and retrieval from the
   second worktree.
3. **C4** — the non-foreclosure round trip, especially the **byte-identical sibling line**
   assertion.
4. **At least one adversarial fixture that catches a silent omission** — an input where a naive
   enumeration returns fewer records than it should. Show what the naive version would return
   and what yours returns.

**Confirmatory — spot-check:** C5, the `artifact-ref` fix.

## Verification Commands

```bash
python -m pytest tests/test_episode_store.py -q
python -m pytest tests/ -q      # baseline 1181 passed, 2 skipped — plus your new tests
git status --short              # only your new/edited files; episodes/ must stay clean
```

Use `python`, **not** `py` — `py` has no pytest here and reports "No module named pytest".

## Suggested Model Tier

`stronger` — the acceptance exercise involves real subprocesses and real git worktrees, which
is where subtle test-harness bugs live, and a wrong test here would falsely certify the issue's
headline criterion.

## Authority

**Already decided:** Markdown in git; the tracked `episodes/` path; the record grammar and
seams (frozen at g1); the validated-delta write path (g2); retrieval is mechanical.

**You must NOT decide alone — stop and return:** the retirement layout; any record-grammar
change; anything touching `LESSONS.md`, `apply_lessons_delta.py`, or issue #300.

**You may decide** (log it): `query_episodes.py`'s CLI surface and internal structure; which
exact join keys define "neighbour" (state your choice and why); test and fixture layout.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be touched;
required evidence cannot be produced; a decision outside the given authority is needed; or
**you find that a close criterion cannot be honestly demonstrated** — in particular, if the
cross-worktree exercise (C3) cannot be made real, **report that as a finding rather than
weakening the test to fit.** That instruction is explicit and comes from the Admiral: a store
that passes a same-directory test while siloing per worktree is exactly the silently-wrong-but-
green shape this run is guarding against.

## Return Format

Return **IMPLEMENTER_RESULT** at `.agent-work/301/crew-handoffs/g3-result.md` with a literal
`VERDICT: COMPLETE` (or `VERDICT: BLOCKED` + reason) line, and: completed slice, files changed,
test mode satisfied, evidence with pasted output, assumptions used, stop conditions hit,
out-of-scope observations, and a **non-empty Workflow Feedback** section.

Do not commit; I integrate and commit.
