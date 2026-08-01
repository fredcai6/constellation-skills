# Mission Frame — issue #309

**Shrunk per template guidance**: this repo has no `docs/architecture/` packet map (no
`capability:`/`struct:`/`decision:`-node graph exists at all — grep for `docs/architecture`
returns nothing at HEAD). Substituting the closest project doctrine
(`docs/EPISODE_STORE.md`, frozen at #301 g1/updated g4) as the structural anchor for the
one system this run writes into (the episode store) and the launch order itself as the
anchor for the sweep's own design. Node-id vocabulary below is therefore doctrine
section/seam names, not graph ids.

## Intent
Build and RUN a bounded adversarial coherence sweep once: seed known incoherences into a
**copied** slice of 4 named files, dispatch opinionated viewpoint subagents against the
slice (doctrine handed inline), measure recall/noise against a ground-truth manifest,
demonstrate the instrument can both MISS a seeded defect and RAISE-then-REJECT a false
positive before either number is reported, write findings as predictive episodes, confirm
the slice never touched the live corpus (or is provably reverted), and disposition #321.

## Affected Capabilities (doctrine sections in lieu of capability: nodes)
- **Episode store write path** (`docs/EPISODE_STORE.md` §4/§7, `apply_episode_delta.py`) —
  this run's findings write `create` ops here. Read-only otherwise; no schema change.
- **Episode store fetch/retrieval path** (`docs/EPISODE_STORE.md` §8,
  `query_episodes.py`) — this run's #321 fix touches `resolve_episode_path()`
  (`apply_episode_delta.py:704`), the one seam `fetch_episode`/`neighbours` both route
  through.

## Structural Anchors
- `apply_episode_delta.py:704 resolve_episode_path()` — the #321 fix point (single seam,
  all id-taking readers route through it).
- `apply_episode_delta.py:481 episode_id_for()` — the grammar classifier already used on
  the LIST path; the fix reuses `ID_RE` from the same module, not a new pattern.
- `episodes/active/` — where this run's predictive episodes land (never `episodes/retired/`
  — nothing seeded here is ever retired, it is either accepted as a real finding-episode or
  never written).
- `.agent-work/issue-309/corpus-slice/` (new, this run) — the copied-and-seeded slice.
  **CORRECTED mid-plan (see notes-309.md)**: `.agent-work/` is **no longer gitignored**
  as of commit b69e6c8 (#326, "track .agent-work/ — run history is project history");
  `docs/EPISODE_STORE.md` §1's own "`.agent-work/episodes/` is ignored" claim is now
  **stale** (predates #326). The slice is instead kept out of git via a worktree-local
  `.agent-work/issue-309/.gitignore` (`corpus-slice/`), verified with
  `git check-ignore -v` (exit 0). "Seed a copy, not the live corpus" is now true by this
  explicit mechanism plus never staging the directory, not by an assumption about
  `.agent-work/`'s ignore status that turned out to be false.

## Governing Constraints / Assumptions
- **decision:copied-slice-not-live-corpus** (LAUNCH_ORDER Pre-Rulings) — seeding never
  touches a tracked file. Satisfied structurally: the slice lives under `.agent-work/`,
  which is gitignored (`.gitignore` line 1), so it cannot become canon by any git operation
  this run performs.
  `@grade: settled/human · leans g1-seed`
- **decision:proposals-to-episode-store** — all findings are `create` ops against
  `episodes/active/`, never a `LESSONS.md` edit, never a direct doctrine-file edit.
  `@grade: settled/inherited · leans g4-episodes`
- **decision:prove-the-miss** — recall/noise numbers are not reportable until both a
  demonstrated miss and a demonstrated-then-rejected false positive exist.
  `@grade: settled/human · leans g3-score`
- **decision:viewpoints-are-handed-their-context** — each viewpoint dispatch's prompt
  pastes its lens + the seeded-slice location inline; no viewpoint is told to invoke a
  skill or fetch doctrine itself.
  `@grade: guess · leans g2-dispatch · settle: if a viewpoint demonstrably fetches context
  unprompted anyway, relax this for future runs`
- **decision:sweep-scope-is-bounded** — exactly the 4 named files (§ notes-309.md Scope).
  Growth beyond them mid-run is a stop condition, not an absorbed change.
  `@grade: settled/human · leans g1-seed`
- **#321 exposure** — `resolve_episode_path()` has no `ID_RE` check; this run hands the
  store ids programmatically at g3/g4 (score + episode writes), which is exactly the
  unvalidated path. Fix chosen: bounded, at the seam (notes-309.md).
  `@grade: settled/measured · leans g0-fix321 · settle: already measured by direct code read, see notes-309.md`
- **#319 exposure** — working-tree bytes differ under `core.autocrlf`; already documented
  (`EPISODE_STORE.md` §9) and tested. This run's own "seeded material confirmed removed"
  check (g5) must use blob-OID/normalized-content comparison, never raw bytes.
  `@grade: settled/inherited · leans g5-confirm-gone`

## Decision Anchors & Decision Pressure
- decision pressure: **viewpoint count/panel weight** — bounded-issue measurement, not
  architecture-touching, so lightweight (2 viewpoints) per
  `lesson:lightweight-critic-catches-real-findings-on-bounded-issues` rather than a full
  3-lens panel. Surfaced at plan approval below, not chosen silently.
- decision pressure: **cold plan critic mandatory** — this plan's acceptance depends on a
  before/after recall/noise measurement, which is exactly
  `lesson:cold-critic-mandatory-for-measurement-dependent-plans`'s trigger. Treated as
  MANDATORY, not bias-to-yes, for this plan.

## Claims / Evidence Surfaces
- claim: "the sweep can miss" — verified by g0.5 (a seeded defect the viewpoints are
  never shown a hint for, scored MISS not green).
- claim: "the sweep can raise and reject noise" — verified by g0.5 (a decoy trap flagged
  by a viewpoint, then correctly rejected at scoring against the ground-truth manifest).
- claim: "seeded material never touched the live corpus" — verified by g5, blob-OID/content
  comparison of the 4 live source files against their pre-run state, never raw bytes.
- claim: "#321 fixed" — verified by an adversarial test (malformed/traversal id handed to
  `fetch_episode`/`resolve_episode_path`, asserted refused) added to
  `tests/test_episode_store.py`.

## Map Confidence / Staleness / Disputes
- No packet map exists for this repo at all (not stale — absent by design, a
  skill-source repo). Substituted doctrine is current (EPISODE_STORE.md updated at g4,
  2026-08-01, same day as this run).

## Out of Scope
- #308's rhyme-detection/consolidation sensor (downstream, not this issue).
- #305's automated capture wiring (episodes are written by hand-composed `create` deltas
  here, not by an automated capture hook).
- Any change to `docs/EPISODE_STORE.md`'s doctrine text itself (read-only reference this
  run; #321's fix is code, not doctrine).
- Growing the corpus slice beyond the 4 named files.
