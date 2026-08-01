# Crash-resume state note — 301

A fresh Commander resumes from exactly these five lines. No forensics needed.

- **step:** spine `execute` · `execute.json` gates **g1, g2, g3 all CLOSED and committed**. Active gate is **`g4-implement`, which is BLOCKED BY DESIGN** on Tommy's retirement-layout ratification. Its precondition p1 requires a ratification record; **do not start it without one — stop and return instead.** After g4 the spine still owes: reconcile → triage → review → feedback → archive.
- **slug:** work-id `301`, branch `epic-298/301`, worktree `C:/Programs/constellation-skills-wt/298-301`, **PR #320** (open, not merged)
- **next command:** `py scripts/checklist_engine.py --file .agent-work/301/execute.json current` — if ratification has arrived, `attest g4-implement --cond p1 --which preconditions` citing it, then dispatch via `python scripts/run_crew.py` (run `python scripts/recover_crews.py 301` first).
- **pid:** none — foreground
- **expected artifact:** `.agent-work/verdict-301.md` (written, current). Shipped: `docs/EPISODE_STORE.md`, `episodes/`, `scripts/apply_episode_delta.py`, `scripts/query_episodes.py`, `tests/test_episode_store.py`.

## The one thing g4 must do

Bind the ratified retirement layout at **four adapter seams** — `apply_retirement`,
`iter_episode_ids`, `is_episode_in_ordinary_search`, `resolve_episode_path` — plus the module
constant `_LAYOUT_ADAPTER` in `scripts/apply_episode_delta.py`, which currently defaults to
Option B as an **explicitly-marked placeholder, not a ratified choice** (a reviewer independently
confirmed that reading). Then add retirement-dependent retrieval (ordinary-search exclusion,
history-inclusive enumeration) and its silent-omission fixtures.

**Doc corrections g4 owes** (`docs/EPISODE_STORE.md`), both known and neither shipping before
then, since PR #320 cannot merge until g4 completes:

1. **§§8/10 describe retirement-dependent retrieval as if it exists.** It does not — it was
   deliberately deferred to g4. Correct them to match what actually shipped. (Found by the g3
   review.)
2. **§9 says a second worktree "sees the identical file content."** True at the blob/content
   level, **misleading at the byte level** — the repo's `.gitattributes` sets `* text=auto`, so
   checkout converts line endings and the working-tree bytes differ. My own test
   `test_working_tree_bytes_are_not_the_cross_worktree_identity` pins exactly that, so the doc
   and the test currently disagree in tone. Say "the same content, and the same blob OID —
   working-tree bytes may differ by platform." Context on issue **#319**.

The options: **A** moves the file between `episodes/active/` and `episodes/retired/`; **B** flips
a `status` field filtered negatively. My floated recommendation is **A** — see `verdict-301.md` §8.

## Traps a successor must not fall into

1. **Silence is not consent.** The convergence is surfaced-always under the epic-298 contract.
   The Admiral corrected me on this twice. Do not read an unanswered float as approval.
2. **`durable_root()` is wrong for this store.** Verified at HEAD (`agent_work_root.py:136-141`):
   under an active Admiral epic lease it returns the *worktree* root. The store is a **tracked**
   path (`episodes/`), and git itself provides cross-worktree sharing.
3. **pytest runs under `python`, not `py`.** `py -m pytest` reports "No module named pytest",
   which reads like a broken suite. Final suite: **1223 passed, 2 skipped**.
4. **Never hand-edit `execute.json`** — use the engine's `amend` verb, as both restructures did.

## Lease

Session lease `commander-301-s1` is **held** deliberately (mid-mission, not archived; doctrine
releases only as the last action at `archive`). Take it over with:

`py scripts/checklist_engine.py --file .agent-work/301/spine.json claim --session-id <new> --claimed-by <you> --worktree . --force --reason "resuming this run"`

## Harvest before sweeping

`.agent-work/` is gitignored. `verdict-301.md`, `design-it-twice/`, and `staged-feedback/301/`
exist **only here** and die with the worktree. Code and docs are safe on PR #320.

_Updated: 2026-08-01T09:30:00Z_
