# Implementer Handoff

## Gate
`g0-fix321-implement` (issue-309, worktree C:/Programs/constellation-skills-wt/e298-309, branch epic-298/309)

## Task
Fix issue #321: `resolve_episode_path(episode_id, root)` in `scripts/apply_episode_delta.py`
(currently starting at line 704) builds `root / sub / f"{episode_id}.md"` from a
caller-handed `episode_id` string with **zero format validation**, then only checks
`.exists()`. Contrast: the id-LISTING path (`iter_episode_ids` -> `_layout_episode_ids`)
validates every filename through `episode_id_for()` (the grammar classifier) before it
becomes a candidate id. Ids the store is **handed** (via `query_episodes.py`'s `fetch`/
`neighbours` CLI/API, which call `fetch_episode()` -> `resolve_episode_path()` directly)
are not validated at all. This allows a crafted id containing `..` path-traversal segments
to resolve outside `episodes/` entirely and read an arbitrary `.md` file that happens to
exist at the traversed location.

Add `ID_RE.fullmatch(episode_id)` as the **first** check inside `resolve_episode_path()`
(the module already defines `ID_RE = re.compile(r"[a-z0-9][a-z0-9-]*-[0-9]{3,}")` at line
113) — if it does not match, return `None` immediately, before `_require_store_layout()`
or any filesystem check. This mirrors the function's existing "not found" contract (a
malformed id can never legitimately exist, so `None` is the correct, contract-preserving
answer, not a new exception type) and fixes the exposure at the ONE seam every id-taking
reader (`fetch_episode`, `neighbours`'s anchor fetch, and the writer's own
`Transaction.load()`) already routes through — no other call site needs to change.

## Protected Intent
The store's own seam discipline (`docs/EPISODE_STORE.md` section 7): "never inlining the
path... at the call site." The fix must land in the ONE named seam, not be duplicated at
each caller. Do not weaken or change `ID_RE`'s own grammar (`docs/EPISODE_STORE.md`
section 2) — reuse it exactly as already defined.

## Test Mode
TDD preferred but test-after is acceptable — this is a narrowly bounded defensive-check
addition to an existing, already-tested module (`tests/test_episode_store.py` already
exists and is extensive).

## Close Criteria
- `resolve_episode_path()` returns `None` for any `episode_id` that does not fully match
  `ID_RE`, without touching the filesystem for that id.
- All existing behavior for well-formed ids (found in `active/`, found in `retired/`,
  found in both -> half-retired refusal, not found at all -> `None`) is unchanged.
- One new adversarial test in `tests/test_episode_store.py` that **proves the guard
  actually fires**, not merely that a lookup returns `None` (a not-found well-formed id
  already returns `None` with or without this fix — that would be a check that cannot
  fail). Concretely, the test must:
  1. Construct a traversal-shaped id string (e.g. `"../../SKILL_INDEX"`) such that, when
     joined the way the OLD (pre-fix) code did — `root / sub / f"{episode_id}.md"` — it
     resolves to a REAL FILE THAT ACTUALLY EXISTS on disk (`SKILL_INDEX.md` at the repo
     root is confirmed present at HEAD — verify this yourself with a `Path.exists()` check
     inside the test, and fail loudly/skip with a clear message if that assumption ever
     stops holding, rather than passing vacuously).
  2. Assert that WITHOUT the guard (e.g. by directly constructing that same raw path
     inline in the test, not by disabling the real fix) the path would have resolved to
     that real file — demonstrating the exposure existed.
  3. Assert that WITH the guard in place, `resolve_episode_path(episode_id, root)` (and/or
     `fetch_episode`) returns `None` for that same id.
  A test that only asserts step 3 in isolation is not sufficient to close this criterion.

## Allowed Scope
- `scripts/apply_episode_delta.py`: `resolve_episode_path()` only (one function).
- `tests/test_episode_store.py`: add the one new adversarial test function. You may add a
  small helper if needed, but do not restructure the existing test file.

## Specific Exclusions
- Do not touch `query_episodes.py`, `episode_id_for()`, `iter_episode_ids()`, or any other
  seam — the fix belongs at `resolve_episode_path()` alone (Protected Intent).
- Do not change `ID_RE`'s pattern.
- Do not touch `docs/EPISODE_STORE.md` (doctrine text is out of scope for this gate — code
  only).

## Constraints
- Match this module's existing style: no new exception type, `None` is the established
  "not found" contract.
- Windows: any file write must use `encoding='utf-8', newline='\n'` explicitly (project
  convention; this repo has previously lost content to `UnicodeDecodeError` on ANSI
  default encoding).

## Map Anchors (inbound)
- **Structural:** `apply_episode_delta.py:704 resolve_episode_path()`
- **Capability:** episode store fetch/retrieval path
- **Constraints/assumptions:** #321 — the store validates ids it lists but not ids it is handed
- **Decision anchors:** `decision:fix-321-at-the-seam — bounded, single-function fix at resolve_episode_path() rather than duplicating checks at every caller`
  `@grade: settled/measured · leans g0-fix321-implement · settle: already measured by direct code read`
- **Evidence expectations:** adversarial test in `tests/test_episode_store.py` proving the guard fires (not just "returns None")

## Deliverable Path Check
- **Committed** — `scripts/apply_episode_delta.py`; verified via `git check-ignore scripts/apply_episode_delta.py` exiting 1 (not ignored) before dispatch.
- **Committed** — `tests/test_episode_store.py`; same, not ignored.

## Required Evidence
- The exact diff to `resolve_episode_path()`.
- The new test function's full source.
- `python -m pytest tests/test_episode_store.py -q` output, pasted verbatim, showing the
  new test passing and the full suite green (state the pre-change pass count and the
  post-change pass count so a net "+1 test, 0 regressions" claim is checkable, not
  asserted).
- Confirm your traversal target (`SKILL_INDEX.md` or whatever you chose) really exists at
  repo root — paste the `Path.exists()` result.

## Verification Commands
```bash
python -m pytest tests/test_episode_store.py -q
```

## Suggested Model Tier
Simple bounded — one function, well-specified guard, existing test harness to extend.

## Authority
The bounded-fix-vs-workaround choice for #321 was already made by the Commander
(`decision:fix-321-at-the-seam`, above) — you do not need to re-litigate whether to fix it,
only how, within Allowed Scope.

## Stop Conditions
Stop and return if: `ID_RE` doesn't behave as documented when you test it directly, the
close-criteria test construction turns out to be impossible (e.g. no real file exists at
any traversal-reachable path from the store root — in which case say so and propose an
alternative real-file target), or you find the exposure also reachable through a path this
handoff didn't anticipate.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback.
