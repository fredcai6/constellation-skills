# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g0-fix321-review` (issue-309, worktree C:/Programs/constellation-skills-wt/e298-309, branch epic-298/309)

## Result
`APPROVE`

## Handoff compliance
Satisfied. `resolve_episode_path()` in `scripts/apply_episode_delta.py` now runs
`if not ID_RE.fullmatch(episode_id): return None` as its literal first statement,
before `_require_store_layout()` or any other filesystem access — independently
verified by calling `resolve_episode_path()` with a traversal-shaped id against a
root path that does not exist on disk at all: it returns `None` cleanly instead of
raising from `_require_store_layout`, proving no filesystem access precedes the
guard. One new adversarial test class, `PathTraversalGuardTests`, was added to
`tests/test_episode_store.py`, matching the task statement.

## Scope drift
None. `git diff --stat` shows exactly the two allowed files
(`scripts/apply_episode_delta.py`, `tests/test_episode_store.py`); no others
touched. All four specific exclusions (`query_episodes.py`, `episode_id_for()`,
`iter_episode_ids()`, `docs/EPISODE_STORE.md`) are untouched, confirmed against the
diff. `grep -n "^ID_RE" scripts/apply_episode_delta.py` confirms the pattern itself
(`r"[a-z0-9][a-z0-9-]*-[0-9]{3,}"`) is unmodified. `grep -rn
"resolve_episode_path(" scripts/*.py` shows only the one definition-site change
plus the same two pre-existing call sites — the fix was not duplicated at any
caller.

## Evidence verdict
All required evidence independently reproduced from scratch (not accepted from
`IMPLEMENTER_RESULT.md`'s pasted transcripts), per the handoff's explicit
instruction:

1. **Traversal target exists.** Confirmed via a fresh Python check:
   `Path('SKILL_INDEX.md').exists()` → `True` at repo root.
2. **The exposure (pre-fix-style join).** Confirmed via a fresh script: the raw
   inline join `root / "active" / f"{episode_id}.md"` with `episode_id =
   "../../../SKILL_INDEX"` and no format check resolves to (and `.exists()` is
   `True` for) the same real `SKILL_INDEX.md`.
3. **The fix (guard fires).** Confirmed by importing the module fresh and calling
   `resolve_episode_path()` directly: the traversal id returns `None`. Also
   confirmed the guard runs *before* any filesystem access — calling
   `resolve_episode_path()` with a nonexistent root path returns `None` cleanly
   rather than raising from `_require_store_layout()`, which would fire if the
   guard ran second.
4. **RED reproduced independently.** `git stash push -- scripts/apply_episode_delta.py`
   to revert to the pre-fix state, re-ran `PathTraversalGuardTests` alone: it
   failed with the exact same `EpisodeDeltaError` (half-retired-guard branch) the
   report claims — byte-for-byte the same failure mode, not a different one.
   Restored via `git stash pop` and confirmed the working tree matched the
   pre-stash diff exactly afterward.
5. **GREEN reproduced independently.** Ran `python -m pytest
   tests/test_episode_store.py -q` myself against the restored (fixed) tree:
   `106 passed, 1 skipped, 16 subtests passed` — matches the claimed net
   +1 test / 0 regressions over the 105/1-skipped baseline.

Judgment on the substitute RED proof (guard fires via the half-retired branch
rather than a wrong-`Path` return, as flagged in the handoff): **sound**. Step 1
(the raw join lands on a real file) is proven independently of what the live
function does pre-fix, and the live function's actual pre-fix behavior — raising
rather than returning `None` — is itself proof no validation existed. Both close-
criterion halves (exposure + fix) hold regardless of which exact pre-fix failure
shape occurs. The test is not "a check that cannot fail": I directly reproduced it
failing against the reverted, unguarded function.

## Code/doc quality
Minimal and maintainable. The constraint "no new exception type; `None` is the
established not-found contract" is honored (`return None`, no raise). The
constraint "fix at the one seam, not duplicated at each caller" is honored
(verified above). Diff is small (13 lines in the source file, mostly an
explanatory docstring addition) and matches the file's existing
docstring-heavy, rationale-documented convention. The new test class follows the
file's existing `unittest.TestCase` naming and structuring style.

**Fowler code-smell pass** (recorded to
`.agent-work/issue-309/g0-fix321-review/FOWLER_PASS.json`,
`verify_fowler_pass.py` exits 0): all 12 baseline smells given a verdict.
- **Flagged (non-blocking observation):** `duplicated-code` —
  `PathTraversalGuardTests.setUp`/`tearDown` near-duplicates ~5-6 lines of
  `EpisodeStoreTestCase.setUp`/`tearDown` (the `load()`, `TemporaryDirectory`,
  `ensure_store_layout`, `tmp.cleanup()` pattern) rather than subclassing and
  overriding just the tempdir anchor. It's a single instance (rule of two, not
  three) isolated to one adversarial test class, and the implementer's own notes
  explain why it isn't a subclass (needs `dir=str(ROOT)` for deterministic `..`
  depth, plus an extra `self.q`). Minor; not a blocker.
- **Overridden:** `comments-as-deodorant` — the added docstring text is voluminous
  but explains genuine design rationale for code that is itself trivially simple
  (a 2-line guard clause); it follows this file's own pre-existing house style of
  documenting the "why" behind every seam (`global-crew.md`: match surrounding
  documentation conventions), not compensating for confusing code. Logged
  standard + reason in the Fowler record.
- All other 10 baseline smells: absent.

## Map impact verdict
- **Evidence supports claimed change:** yes — see Evidence verdict above; every
  claim independently reproduced.
- **Constraints not violated:** yes — #321's constraint ("the store validates ids
  it lists but not ids it is handed") is now closed at the fetch/handed-id path
  without touching the already-validated writer/listing paths.
- **Notes match the diff:** yes — the implementer's Map Impact notes (structural:
  one guard clause in `resolve_episode_path()`; capability: fetch/retrieval path
  now validates handed ids; constraints: #321 resolved,
  `decision:fix-321-at-the-seam` executed as ruled) match the diff exactly, no
  overstatement.
- **Decision candidates surfaced:** none needed — this was bounded, in-latitude
  work per the launch order, no new authority-requiring decision arose.
- **Durable context routed:** one triage candidate flagged (below) rather than
  dropped.

## Reconciliation check
No architecture-breaking divergence. The fix lands exactly at the seam
`docs/EPISODE_STORE.md` §7 already names as authoritative for path resolution
("The fetch-by-id path-resolution seam"); neither the writer's validated-
transaction discipline nor the store's directory layout changed.

One documentation-gap observation: `docs/EPISODE_STORE.md` §7 documents
`resolve_episode_path()`'s half-retired-refusal and existence-check behavior but
does not mention the new id-format (`ID_RE.fullmatch`) guard. The doc was
correctly excluded from this bounded fix's scope (the handoff named it as a
specific exclusion), but since EPISODE_STORE.md is elsewhere described as frozen
store doctrine, a follow-up should add one sentence there so the doc stays a
complete description of the seam's contract. Flagged as triage candidate `tc1` in
the survey (`.agent-work/issue-309/g0-fix321-review/review.json`).

## Blockers
- none

## Out-of-scope observations
- `docs/EPISODE_STORE.md` §7 doc gap (triage candidate `tc1`, detailed above) —
  add one sentence documenting the id-format guard once a follow-up doc pass is
  scheduled.
- Minor `duplicated-code` Fowler observation (detailed above under Code/doc
  quality) — not worth a rework cycle on its own; note for a future test-fixture
  cleanup pass if `PathTraversalGuardTests` ever grows a sibling test.
- `notes-309.md` and `.agent-work/issue-309/` are untracked in the worktree but
  belong to the parent Commander's own working notes (per its header, "Sole
  writer per LAUNCH_ORDER-309.md File Ownership") — unrelated to this bounded
  gate, not a defect in the reviewed diff, noted only for completeness.

## Workflow Feedback
- **Handoff gaps:** none — the handoff was unusually precise (exact grep
  commands, exact expected counts, an explicit instruction to independently
  reproduce rather than trust the pasted transcript). This made verification
  fast and unambiguous.
- **Context rediscovered:** the handoff's "Note on this RED shape" pointer was
  accurate and sufficient — no extra digging needed beyond what it named. I did
  additionally read `docs/EPISODE_STORE.md` §7 (not named in the handoff's Map
  Anchors beyond a general pointer) to check the reconciliation item; that's
  where the doc-gap observation came from.
- **Instructions improvised around:** `config_ref` in the survey template points
  at `docs/agents/engine-config.json`, which does not exist in this worktree
  (same gap the implementer already noted for its own plan). Set to `null` in the
  instantiated `review.json`, matching the implementer's precedent — the engine
  ran fine without it.
- **What would have made this easier:** none — this handoff and the underlying
  fix were both tight and bounded enough that the review had no friction worth
  reporting beyond the two items above.

## Return status
`complete`
