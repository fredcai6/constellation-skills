# Reviewer Handoff

## Gate
`g3` — layout-independent retrieval + the cross-session / cross-worktree acceptance exercise
(issue #301, epic-298)

**This gate certifies issue #301's headline acceptance criterion.** A wrong test here would
falsely certify the whole issue. Judge the *tests* at least as hard as the code.

## What was implemented

- `scripts/query_episodes.py` (new) — four retrieval primitives (fetch by id, enumerate, select
  by exact field / set membership, enumerate neighbours), all routed through the seams named in
  `docs/EPISODE_STORE.md` §7, plus a CLI emitting a deterministic JSON envelope.
- `tests/test_episode_store.py` — extended from 24 to 65 tests.
- `scripts/apply_episode_delta.py` — one authorized fix-now: `artifact-ref` values are now
  stripped before storage, closing a round-trip defect the g2 review found.

## How to inspect

```bash
cd C:/Programs/constellation-skills-wt/298-301
git status --short            # 2 modified, 1 new (query_episodes.py is new: git status, not git diff)
git diff scripts/apply_episode_delta.py tests/test_episode_store.py
cat scripts/query_episodes.py
cat docs/EPISODE_STORE.md     # the frozen contract, sections 7-8
```

Implementer's result: `.agent-work/301/crew-handoffs/g3-result.md`. Its handoff:
`.agent-work/301/crew-handoffs/g3-handoff.md`.

## Close criteria

- **C2** cross-session retrieval **exercised**: seeded in one process, retrieved in a
  separately launched one sharing only the working tree.
- **C3** cross-worktree sharing **exercised through git**: seeded and committed in one linked
  worktree, retrieved from a second.
- **C4** non-foreclosure **exercised**: dispute one agent-supplied field; the disputed field's
  standing changes, a sibling's does not, and the sibling's stored line is **byte-identical**.
- **C5** retrieval is exact-match and set-membership only — no ranking, scoring, similarity, or
  embedding.

## HUNT THESE SPECIFICALLY

**1. Are C2 and C3 REAL boundaries, or elaborate simulations?** This is the whole gate. The
implementer claims:
- C2 uses `subprocess.Popen` + `sys.executable`, observes three distinct OS pids (parent,
  writer, query), and has the query child report its own `os.getpid()` inside its JSON answer
  so the answer is tied to that process rather than assumed. It also ships a vacuity test
  pointing an identical session 2 at an empty store root, asserting failure.
- C3 uses real `git init` + two real `git worktree add`s, asserts each linked worktree's `.git`
  is a **file** containing a `gitdir:` pointer, and observes the transition absent → still
  absent after a local commit → present only after merge.

**Verify these claims by reading the tests and running them — do not take the summary's word.**
Then attack: can either test pass while the property it claims to prove is false? Specifically —
does session 2 genuinely receive only a store root and an id, with no smuggled state (env vars,
inherited file handles, a pickled object, a path that leaks content)? Could the worktree test
pass if the two worktrees *did* share a directory?

**2. Is the vacuity/falsification coverage real?** A test that cannot fail is worse than no
test. For each of the four acceptance properties, ask: if I broke the underlying behavior,
would this test actually go red? Try it — break something and see. That is the most convincing
evidence you can produce.

**3. The silent-omission fixture.** The implementer claims a naive dict-collapse implementation
returns 1 of 3 matching episodes while theirs returns 3 of 3, asserted as
`set(naive) < set(ours)`. Verify the naive version is a *realistic* naive implementation and not
a strawman built to lose. Then hunt for a silent omission the fixture does **not** cover — a
record that should be returned and is not. This is the failure class the store's design most
fears.

**4. Seam discipline.** Retrieval must call `resolve_episode_path()`, `iter_episode_ids()`, and
`is_episode_in_ordinary_search()`, never inline a glob, a path check, or a status grep. Verify
by reading `query_episodes.py`. Any inlining means binding the held retirement layout at g4
becomes a rewrite instead of an adapter swap — the exact failure two g1 review rounds fixed.

**5. Scope discipline.** The retirement layout must still be **unbound**, and
retirement-dependent retrieval (ordinary-search exclusion, history-inclusive enumeration) must
**not** be built — that is g4. The implementer flagged a genuine tension in its handoff: it
built an unfiltered enumeration with no `include_retired` parameter exposed. Judge whether that
was the right call.

## Two findings the implementer already routed — confirm, don't rediscover

1. **Windows `core.autocrlf`** means an episode's working-tree bytes differ across worktrees
   (blob hash and parsed record are identical). Harmless for #301, a real hazard for #308 if
   its consolidation compares working-tree bytes. Already filed as **issue #319** and pinned as
   a named test. Confirm the test genuinely pins it.
2. `is_episode_in_ordinary_search()` cannot distinguish "no such episode" from "retired" —
   harmless now, relevant when g4 wires it in.

## Allowed scope

Review only. **Do not edit any repo file.** Probe scripts go outside the repo or under
`.agent-work/`. Leave nothing stray in `scripts/`, `tests/`, or `episodes/`, and leave no
episodes in the real `episodes/` directory.

## Specific exclusions

- Do not ask for the retirement layout to be chosen, or for retirement-dependent retrieval —
  both are g4.
- Do not re-litigate the record grammar (frozen at g1, reviewed three times) or the writer's
  validation design (approved at g2).
- Do not propose changes to `LESSONS.md`, `apply_lessons_delta.py`, or issue #300's manifest.

## Evidence produced (reproduce it)

I independently ran all of these:

```bash
python -m pytest tests/test_episode_store.py -q     # 65 passed, 16 subtests
python -m pytest tests/ -q                           # 1222 passed, 2 skipped (baseline 1181)
python -m pytest tests/test_episode_store.py -v -k "CrossSessionRetrievalTests or CrossWorktreeSharingTests or NonForeclosureTests or SilentOmissionTests"
                                                     # all 12 PASSED
git status --short                                   # 2 modified, 1 new; episodes/ clean
```

Use `python`, **not** `py` — `py` has no pytest here and reports "No module named pytest".

## Return format

Return **REVIEW_RESULT** with a literal `VERDICT: APPROVE` or `VERDICT: BLOCK` line, findings
ranked most-serious-first with severities, what you verified as fine, what you could not check
and why, and a Workflow Feedback section.

Reserve `BLOCK` for an unmet close criterion or a defect you actually **demonstrate** —
especially a test that certifies a property it does not really prove. `APPROVE`-with-findings
is right if the criteria are met and the rest are refinements; say which gate carries each.
