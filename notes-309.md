# notes-309.md — working notes, commander-309 (issue #309)

Sole writer per LAUNCH_ORDER-309.md File Ownership. Never `findings-309.md` (Write tool
refuses any path with "findings" in the basename).

## Problem statement (understand step)

Issue #309, spec B1 (Testing pathways: coherence sweep). Build and RUN an adversarial
coherence sweep:

1. Seed known incoherences into a **bounded, named, copied** corpus slice (never the live
   corpus) — pre-cleared corpus surgery, but copy-not-live is a settled/human pre-ruling.
2. Dispatch opinionated viewpoint subagents against the seeded slice, each handed its
   doctrine inline (no reliance on it invoking a skill — #299's zero-Skill-invocation
   finding).
3. Measure seeded-defect **recall** and **noise ratio** from what the viewpoints report.
4. Before trusting either number: **prove the instrument can miss** (a defect it should not
   find, and it must report the miss, not score green) and **prove it can raise a false
   positive it is then correctly rejected** (settled/human, decision:prove-the-miss).
5. All findings land as **predictive episodes** in `episodes/active/` (#301's store, MERGED
   at 195e893) — never LESSONS.md, never direct doctrine mutation.
6. Confirm seeded material is gone from the live corpus (it was never live) or reverted,
   compared by **normalized content or blob OID, never raw bytes** (#319).
7. Disposition #321 (episode store validates listed ids, not handed ids) — fix or work
   around deliberately.

## Baseline verified against code before planning (lesson:verify-launch-order-claims-against-code)

**#301 store — verified MERGED and matches the launch order's description.**
`episodes/README.md`, `episodes/active/.gitkeep`, `episodes/retired/.gitkeep` all present
at HEAD (8de2faa). `docs/EPISODE_STORE.md` is frozen store doctrine, updated at g4
(retirement layout ratified). `scripts/apply_episode_delta.py` (1298 lines) is the only
write path (create/amend-assertion/retire ops, all-or-nothing transaction). Confirmed.

**#321 — CONFIRMED, and narrower than the one-line summary makes it sound.**
Read `scripts/apply_episode_delta.py` in full for the id-validation surface:

- `_validate_amend_assertion` (line 947) and `_validate_retire` (line 960) both call
  `ID_RE.fullmatch(episode_id)` on the caller-handed `id` field BEFORE `apply_delta()`
  ever calls `tx.load()` → `resolve_episode_path()`. **The writer's own amend/retire ops
  are already validated on the handed path.** `_validate_create` (line 854) forbids a
  caller supplying `id` at all — the writer always assigns it via `_next_episode_id()`,
  well-formed by construction. So the **writer/delta path is not the exposed one**.
- The exposed one is `resolve_episode_path(episode_id, root)` (line 704) itself — the
  seam `fetch_episode()` in `scripts/query_episodes.py` (line 154) calls directly, with
  **zero format validation**: `root / sub / f"{episode_id}.md"`, existence-checked, full
  stop. No `ID_RE.fullmatch` anywhere on this path. `query_episodes.py fetch` (CLI) and
  `neighbours` (which calls `fetch_episode` for its anchor, query_episodes.py:382) both
  hand an arbitrary caller string straight into this seam.
- Contrast with the LISTING path: `iter_episode_ids()` → `_layout_episode_ids()` passes
  every directory-listed filename through `episode_id_for()` (the grammar classifier,
  line 481) before it becomes a candidate id — ids the store **lists** are validated.
  Ids the store is **handed** for a direct fetch/neighbours lookup are not. This is
  exactly the launch order's characterization and exactly the shape
  `lesson:guard-must-be-defined-by-the-consumer-not-a-character-list` names: a hand-listed
  character/format check exists in one place (the classifier) and a sibling entry point
  (`resolve_episode_path`) was never wired to it.
- Concrete exposure: `episode_id = "../../SKILL_INDEX"` (no `ID_RE` anchoring requires the
  whole string be a well-formed run-seq id) resolves to
  `root/active/../../SKILL_INDEX.md`, escaping the store root entirely. If that path
  exists, `fetch_episode` reads and attempts to `parse_episode()` arbitrary `.md` content
  from anywhere reachable by relative traversal — a store-scoping bypass, not merely a
  wasted lookup. This is squarely the sweep's own hazard: I hand the store a **programmatic
  batch of seeded-finding ids** for confirm/select/neighbours lookups, which is exactly the
  unvalidated path.

**Disposition: FIX, bounded, at the seam.** Add `ID_RE.fullmatch(episode_id)` as the first
check in `resolve_episode_path()` itself (apply_episode_delta.py:704), refusing (return
None — "no such episode", the existing not-found contract, since a malformed id can never
legitimately exist) rather than doing any filesystem check on a malformed id. One-seam fix:
every caller (`fetch_episode`, `neighbours`'s anchor fetch, and the writer's own
`Transaction.load()`, which already gets pre-validated ids from amend/retire but gains
defense-in-depth for free) inherits it, matching EPISODE_STORE.md's own seam discipline
("never inlining the path... at the call site") and the guard-at-the-consumer lesson. Scope
is one function, ~3 lines, covered by the existing `tests/test_episode_store.py` harness
plus one new adversarial case. This is within Inherited Latitude ("Fixing it inside this
issue is within your latitude if it is bounded; say which you chose and why" — chosen:
fix, because the bound is a single seam already named as the fix point in the store's own
documentation, not a redesign).

**#319 — CONFIRMED, already documented, already tested.** `docs/EPISODE_STORE.md` §9
states the byte-vs-blob-OID distinction verbatim, cites issue #319 by number, and
`tests/test_episode_store.py` already has
`test_working_tree_bytes_are_not_the_cross_worktree_identity`. No code gap — this is a
verification-methodology instruction for MY OWN "seeded material confirmed removed"
check, not a defect to fix. I will compare via `git hash-object` (blob OID) or normalized
(`\n`-joined) content, never `Path.read_bytes()` equality, for that acceptance condition.

## Scope — bounded slice, named before seeding (decision:sweep-scope-is-bounded)

Corpus slice for this sweep: **copies of 4 files**, chosen because they are self-contained
enough to carry a legible seeded contradiction and small enough to keep the slice bounded:
- `skills/constellation-triage/SKILL.md`
- `skills/constellation-curator/SKILL.md`
- `docs/EPISODE_STORE.md` (a section-scale excerpt, not the whole 788-line file)
- `docs/DEBT_SWEEP_CADENCE.md`

Copies live under `.agent-work/issue-309/corpus-slice/` (gitignored — inside `.agent-work/`,
never committed, never touches the live corpus at all: satisfies "reverting live canon is
the fallback, not the plan" by not needing the fallback). If the slice needs to grow beyond
these 4 files during the run, that is a scope change — STOP and surface, per Stop
Conditions, not absorbed silently.

## user-decision evidence

Reconciled against LAUNCH_ORDER-309.md Mission/Pre-Rulings/Inherited Latitude (delegated
mode, no reachable human) rather than interrogating a human. Attaching per-gate
`user-decision` evidence citing the launch order at each engine checkpoint that calls for
one.
