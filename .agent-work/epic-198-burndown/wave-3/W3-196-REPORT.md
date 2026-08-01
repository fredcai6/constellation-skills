# W3-196 Commander Report — gauge absolute-token caps + CHECKLIST_SCHEMA verb-doc

**Commander:** commander-gauge (delegated) · **Branch:** `feat/gauge-abs-caps-196` (base `main` @ `0f354ed`) · **Worktree:** `C:/Programs/cs-wt-gauge` · **PR:** https://github.com/fredcai6/constellation-skills/pull/206 (open — Admiral merges) · **Commit:** `f27dc7b`

## Verdict — both deliverables COMPLETE, independently reviewed APPROVE

### Deliverable 1 — #196 absolute-token-cap thresholds: DONE
Refactored `gauge_reader` threshold storage from per-model `(soft,hard)` **fractions** (`_THRESHOLDS`) to intent-first **absolute-token caps** (`_PROFILES` keyed `model -> (window, soft_cap, hard_cap)` + `_DEFAULT_PROFILE`). `thresholds_for(model)` converts to the same `(soft,hard)` fractions by dividing caps by the model's window — its signature and fraction return are unchanged, so `checklist_engine.py` Trip (`_trip_advisory`/`_trip_hard_gate`) is **untouched**. Numerically **EXACT**, not a recalibration.

**Representation choice (justified — this is the pre-ruling FALLBACK, chosen within latitude, no float).** The pre-ruling's *preferred* "writer emits `used_tokens`+`window`; reader/Trip computes `min(fraction_cap, absolute_cap/window)`" shape is out of bounds: the Trip computation lives in `checklist_engine.py`, explicitly **outside this wave's file ownership**, and `gauge_reader` is deliberately writer-agnostic with a frozen 4-field record. Threading a per-record window into `thresholds_for(model)` cannot be done without editing that forbidden file. The pre-ruling pre-authorized the reader-side fallback ("store absolute caps + convert in the reader … justify your choice"), so the reader keeps its own window column and the caller contract stays byte-identical.

### Deliverable 2 — resume/amend-retext verb-doc: DONE
Documented in `docs/CHECKLIST_SCHEMA.md`, matching shipped engine behavior (`checklist_engine.py` `resume()` ~L1157, `amend` `retext-check` ~L1412): `resume` verb (restores pre-block pending/in-progress from `status_detail.prior_status`; refuses cap-escalations/legacy/empty-reason; does NOT overclaim "clears blocked markers"; added to both mutating-verb enumerations, the Engine-verbs table, and the Status ASCII diagram); `amend` `retext-check` op (4th op-table row; pending-or-in-progress; same-kind; deep-copy all-or-nothing; resets-not-satisfies; fixed the now-false "PENDING gates only / Three op kinds" framing in both places).

## Evidence
- **Equivalence (proves same trip points):** all six cap/window divisions are exact — opus/sonnet/fable `80K/1M=0.08`, `150K/1M=0.15`; haiku `90K/200K=0.45`, `140K/200K=0.70`; default `80K/200K=0.40`, `130K/200K=0.65`. New tests `test_equivalence_to_prior_fraction_literals` and `test_trip_points_unchanged_at_boundary` assert against **independent hardcoded literals** (not read back off the new table). `test_calibrated_shipped_thresholds` + `test_unknown_model_falls_back_to_default` pass **unchanged** (`DEFAULT_THRESHOLDS` kept = `(0.40,0.65)`).
- **Verb-doc matches shipped behavior:** independently confirmed by the reviewer against `checklist_engine.py`.
- **Full suite green:** `py -m pytest tests/ -q` → **890 passed, 2 skipped** (baseline 888/2; +2 new). Engine re-ran it as the g1-integrate postcondition and again at the spine execute boundary.
- **Diff scope:** exactly 3 files (`scripts/gauge_reader.py`, `tests/test_gauge_reader.py`, `docs/CHECKLIST_SCHEMA.md`); `checklist_engine.py` and `scripts/hooks/gauge_writer_hook.py` untouched; reader does not import the writer hook.
- **Independent fresh-context reviewer:** APPROVE (recomputed all six divisions by hand, reproduced the suite, verified doc fidelity incl. no resume overclaim). Cold plan critic caught 2 pre-dispatch BLOCKERs (folded in) → zero reopens/blocks/waivers.

## Isolation output
`py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-gauge` → `worktree OK: in C:/Programs/cs-wt-gauge` (exit 0).

## Map impact
No `docs/architecture` packet map in this skill-source repo. Direct reconcile: `gauge_reader` is an internal representation refactor (no boundary/capability change), self-documented in its updated module docstring; the verb-doc landed directly in `CHECKLIST_SCHEMA.md` (the schema structural record). No separate reconcile edit owed.

## Triage candidates (recommend-and-defer — no filing authority this run; for Admiral)
- **tc1** `gauge_reader.py`: extract a shared `_fractions(profile)` helper to remove a tiny idiom repeat (default-fraction computation vs the division in `thresholds_for`). Pure tidy-up.
- **tc2** `checklist_engine.py` `resume()` docstring (~L1161) says resume "Clears the blocked markers" — imprecise (only `prior_status` is popped; `blocker`/`authority_needed`/`next_action` remain as history). Out of #196 ownership; the shipped schema doc is already precise.

## Workflow feedback
Fenced staged-feedback trio at `.agent-work/staged-feedback/epic-198-w3-196-gauge/` (worktree) — path: `C:/Programs/cs-wt-gauge/.agent-work/staged-feedback/epic-198-w3-196-gauge/` (AGENT_FEEDBACK.md, lessons-delta.json [tick-only], CONSTELLATION_FEEDBACK.md [no-export], FENCE.md). Passes `verify_agent_feedback.py --phase feedback/archive`. Harvest into the shared durable root at epic closeout. Named path for the trio is above. One handoff-authoring nugget: verb-doc handoffs should state the verb's `applies` (gated/survey/both) explicitly — the sole gap the implementer had to resolve from engine source.

## Do NOT merge — Admiral merges. Ready.
