# PROBLEM STATEMENT — issue #698 (cmdr-698)

**Status:** confirmed at `understand`. Engagement is **planning only** — mission frame + `execute.json`, stopping before `execute`.
**Counterpart:** no human reachable; the engagement dispatch is the standing authority for every decision checkpoint.
**Interrogation:** `.agent-work/cmdr-698/INTERROGATION_RECORD.json` — 13 questions (9 fact / 4 decision), rail exit 0.

---

## The ask, restated

Three low-priority hardening items carried out of #666 (DriverFingerprint, epic #659 stage G), all
recommend-and-defer, none of which blocked that merge. No capability changes. The issue fences behaviour
itself: *"Out of scope: any behavior change to the fit/coverage."*

## What the interrogation actually found

**Two of the issue's three premises are wrong, and correcting them changes the work.**

### H1 — store-API primitive obsession

- **The stated acceptance is unachievable as written.** `CellAddress` carries six fields including
  `class_id` (`address.py:81-86`). Every store entry point is *class-agnostic* and takes the same five —
  `write_fingerprint` (`store.py:193-203`), `get_fingerprint` (`:255-257`), `row_count` (`:298-300`) — with the
  class dimension supplied by `vocabulary.class_ids`. The k-cells-always-populated invariant *depends* on each
  method spanning all k classes. Typing them on `CellAddress` would force a meaningless `class_id` argument.
- **But the defect underneath is real, and it is on the read side.** Write validates: it builds a
  `CellAddress` per class inside its row loop (`store.py:233-236`), so a malformed component raises from
  `__post_init__` (`address.py:88-104`). Read validates *nothing*: `get_fingerprint` and `row_count` bind
  primitives straight into the SELECT. `driver=""` or `driver="VER|X"` returns exactly k synthesized
  `"unresolved"` cells (`store.py:277-285`) — indistinguishable from a legitimately not-yet-fitted driver.
  That is the *silent wrong answer* shape `ORCHESTRATOR_CONTEXT.md:22` lists as failure mode #1.
- **Ruling (q3, q6):** satisfy the *effect*, not the letter. Add a five-field frozen `SlotAddress`
  (driver, era, vocabulary_version, channel, what_measure); re-express `CellAddress` as slot + `class_id` so
  there is **one** address ontology and **one** copy of the validation; type all three store methods on
  `SlotAddress`. **Hard cutover, no compatibility overload** — the project rule is one clear execution path,
  and an overload would preserve exactly the unvalidated path H1 exists to close.
- **Blast radius (q5):** 4 production/script call sites + ~44 test call sites, **all positional**, so a
  missed one is a `TypeError` at collect time, not a silent behaviour change.
  Production: `fit.py:356`, `pilot/pipeline.py:257`, `pilot/pipeline.py:325`.
  Scripts: `fingerprint_bounded_validation.py:124`, `join_bounded_validation_667.py:173`.

### H2 — missing worktree-first `sys.path` guard

- **Real, and the prescribed fix genuinely works** — verified from source, not assumed. The editable install
  is the *finder-hook* flavour (`__editable___f1brainz_0_2_0_finder.py`, `MAPPING={'src': 'C:/Programs/f1Brainz/src'}`
  — the MAIN checkout, confirming the trap), but its `install()` **appends** to `sys.meta_path`, so it sits
  behind CPython's default `PathFinder` and `sys.path.insert(0, repo_root)` wins. Had it inserted at position 0
  the prescribed fix would have been inert; that was the load-bearing unknown.
- **Scope corrected (q10).** My first ruling widened H2 to a sibling script on a premise I self-caught as
  false — `join_bounded_validation_667.py` *has* the guard (`:41-43`). A real sweep shows **51** `scripts/*.py`
  import `src.*` with no `sys.path` line at all. That is a repo-wide convention gap wanting a lint/CI check,
  not #666 follow-on work. **Hold the literal scope: fix the one named script; triage the other 50.**

### H3 — gitignore

- **The premise is false.** `.agent-work/` is **tracked**. `.gitignore` covers four named legacy subpaths plus
  `*.pkl` / `*.npz` / `*.db` / `scratch/` / `ckpt/` / `backtests/` under it (`:241-254`, `:283-288`) — nothing
  covers `*.json`. Both named JSONs are **committed** under the archive path, as are siblings from
  664/667/669/670, deliberately: *"Commit Commander work logs only after the work package is finished and
  archived under `.agent-work/archive`."* tc2's blanket `.agent-work/**/*.json` rule would silently un-track
  the repo's evidence trail.
- **The genuine stray risk is concrete, not hypothetical.** `fingerprint_class_coverage_675.py` writes to a
  bare **relative** `Path(".agent-work/666-driver-fingerprint/artifacts/coverage_675_verdict.json")` (`:123`)
  and `mkdir -p`s it (`:477`). That work area was archived to `.agent-work/archive/2026-07-26-666-driver-fingerprint/`,
  so any rerun today **resurrects a stale pre-archive directory** — untracked, un-ignored, inside a tracked
  tree — at whatever cwd the script ran from.
- **Ruling (q9):** reject the blanket rule. Anchor the script's output at `_REPO_ROOT` (the same constant the
  H2 guard introduces) with an `--out` override, **and** add a narrow ignore for the live pre-archive path.

---

## Protected intent — must be observably unchanged

The store's four documented invariants (`store.py:10-32`, guard-tested in `test_store.py`'s five classes):
non-NULL `cell_key`; k-cells-always-populated; loud refusal in all four arms (era/vocabulary argument
mismatch, vocabulary drift, non-PASS vocabulary, reserved `what_measure` on write); no fit-on-read.
Plus `constraint:physics_region_no_evo_import` and the three fingerprint decision anchors.

**Note on the era-mismatch guard:** the convenience constructor `SlotAddress.for_vocabulary(...)` derives
`era` from `vocabulary.rules_era` and so cannot produce a mismatch — but the explicit constructor must remain,
and `_check_era_vocabulary_argument_consistency` must stay live and guard-tested. Dissolving the failure class
for well-behaved callers is a gain; deleting the refusal is not permitted.

## Out of scope (ruled, routed to triage)

1. **Reserved-`what_measure` read asymmetry** (q13) — write refuses a Build-2 dormant slot, read does not.
   Closing it is a store behaviour change; the issue fences behaviour. (The address object still tightens an
   *unknown* `what_measure` on read, via `_KNOWN_WHAT_MEASURES`.)
2. **Repo-wide missing `sys.path` guard** — 51 scripts; wants a lint/CI check.
3. **cmdr-666 tc4** — vocabulary-drift migrate/purge API gap, same surface, still open.
4. Anything touching fit numerics, coverage method, or the store's on-disk schema.

## Map note for reconcile

`docs/architecture/packets/physics.md` says `instrument_panel` "reads un-aggregated
`fingerprint.store.get_fingerprint` cells directly". No store import exists under
`src/physics/instrument_panel/`; the call actually lives in `src/physics/pilot/pipeline.py:325`. The edge is
real, the attribution is imprecise — record at reconcile.
