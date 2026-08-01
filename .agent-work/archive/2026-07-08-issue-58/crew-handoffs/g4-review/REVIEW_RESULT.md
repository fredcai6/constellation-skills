# Review Result — g4 (constellation-explorer SKILL.md + templates + CYCLE tc2 fix)

## Verdict: APPROVE

Commit `9b89e530e4164e75542f13b2a1f560f3fe68d3e3` on `constellation/issue-58`. Working tree clean; diff touches exactly the 7 allowed files. Every Close Criterion reproduced independently — doctrine coverage by side-by-side paragraph read, marker discipline and tc2 by scratch/script reproduction (not eyeballing), both pytest runs re-run here.

## Per-check findings

**1. Doctrine coverage vs "Chosen design 1", paragraph by paragraph — PASS.**
I read DESIGN_SPEC.md §"Chosen design 1" against SKILL.md paragraph by paragraph. Every load-bearing paragraph is carried without dilution:
- Role/tier: orchestrator-tier, upstream-only, requires-reachable-human, **no delegated/autonomous mode**, `explore-<topic>`. Faithful (adds the honest "no `user-decision` you may satisfy by citation").
- Headline doctrine 1-2-3 **in order**: premature-convergence-is-THE-failure-mode + agent-never-initiates + ripeness-only-as-standalone-message-containing-nothing-else; scoped-nulls with was-and-was-NOT-tested + impossibility-requires-class-spanning-evidence + default-next-move-another-variant; hard gate with verifier + marker + honest trust-model statement (engine records `user-decision`, does not cryptographically prove; no sanctioned fabrication path; verifier + downstream refusal are the backstops).
- Spine 7-step table matches the spec's step semantics including the `explore` dual close (user-decision AND verify_cycles.py) and review/confirm command checks.
- Flavors: Shotgun (~20 human-set, wild sanctioned, culls-stay-on-board-as-scoped-verdict), Compare (2-5 recommendation-led, hybrids), Refine (spec-shaped), the natural arc, AND the dead-refine fallback framed verbatim as "the loop working, not failing."
- Excursion ramps complete: brief-before-dispatch, background, on-ramp-before-consolidation, either-side-initiates, run_crew + recover_crews **before each dispatch and before consolidation**, slow-excursion-never-silently-dropped, one-brief-no-double-entry, scoped-nulls.
- Ideas board as source of truth (resume-from-board, mid-exploration-shelve-files-the-board). Spec phase (per-section, delta after first pass, design-it-twice skip-with-stated-reason). Critical review (cold/no-record/nothing-sacred/human-filters-noise, panel-scaled-by-weight, when-in-doubt-panel, EDIT/RE-EXPLORE/REJECT human-only, confirm-on-full-Disposition-column, reopen cascade cost documented + cap 99). Route (three routes, explorer NEVER cuts, archive + release). Interrogator seam.

**2. Marker discipline vs the script — PASS.** Ran `verify_spec_confirmed._unconfirmed_marker_hit` over all five authored files: SKILL.md and all four new templates report clean (every mention inline in prose). The sole standalone-marker hit in `skills/explorer/` is `templates/DESIGN_SPEC.template.md` — the frozen g2 refused-DRAFT, out of scope and correct by design. The shelve route (`SKILL.md:92`) correctly instructs placing the marker as a standalone header line on the shelved issue, where enforcement is intended.

**3. Six-heading byte-match — PASS.** `diff` of the EXCURSION_BRIEF prototype-section top-level headings against the real `PROTOTYPE_HANDOFF.template.md` = IDENTICAL (Question / Branch / Host-project conventions / Location / Stop conditions / Return format). Sub-bullets adapted appropriately (Return format points at the board, not PROTOTYPE_RESULT.template.md) per the g3 "top-level headings only" note. All three excursion types present with the four named constraint lenses and the depth/locality/seam/testability axes; research section carries primary-sources/cited-findings.

**4. CRITIC_HANDOFF — PASS.** Cold-read contract explicit (spec only, no exploration record, nothing sacred, may attack deliberate decisions). Return format = `| ID | Lens | Severity | Finding | Disposition | Reason |` exactly. Disposition/Reason documented as left EMPTY for human triage; "The critic never self-triages"; EDIT/RE-EXPLORE/REJECT named as human-only.

**5. tc2 fix — PASS.** `CYCLE.template.json` no longer references `docs/agents/engine-config.json` (key dropped). Verified against engine source: `load_config` returns `{}` when `config_ref` is absent/missing (no crash), and `reopen` raises `EngineError` for non-gated checklists — a cycle is `type: "survey"`, so `rework_cap` is never consulted. The implementer's "degrades to `{}`, survey never consults rework_cap" rationale is accurate; the "dangling reference, not a crash" framing is the honest defect statement. Reproduced the new `CycleSurveyConfiglessRuntime` test: the engine claims/starts/records/skips/consolidates a cycle survey in a directory with no engine-config file — green.

**6. Frontmatter — PASS.** `name: constellation-explorer`; imperative "Use…" description consistent with commander/prototyper siblings.

**7. Suite inflection, reproduced — PASS.** Targeted `tests/test_explorer_templates.py` → 24 passed. Full `tests/` → **2 failed, 420 passed, 1 skipped, 20 subtests**; both failures are `test_install_constellation.py` expected-skills-list assertions (installer now discovers `constellation-explorer` + `constellation-prototyper`, not yet in the expected list — g5's). `test_feedback_tooling.py` fully green. No failure outside the expected-skills class.

## Blockers
None.

## Out-of-scope observations
- Compare-flavor prose drops two purely illustrative parentheticals present in the spec (excursion-type examples and the "Home of the superpowers 2-3-approaches pattern" provenance aside). The load-bearing clause "excursions per candidate where earned" is retained; not a dilution finding, noted only for completeness.
- For g5: `DESIGN_SPEC.template.md` legitimately carries the one enforceable standalone marker; invariant tests should expect exactly one standalone marker there and none across the five authored files.
- `test_install_constellation.py` expected-skills list and explorer script-bundle assertions remain g5's, as scoped.

## Workflow feedback (run-specific)
The handoff's instruction to reproduce the marker check "against the script's actual `_unconfirmed_marker_hit`, scratch fixtures not eyeballing" was the right call and paid off: `grep UNCONFIRMED` surfaces the standalone marker in the frozen DESIGN_SPEC.template.md too, which would read as a violation to a reviewer working by eye — running the actual function makes the inline-vs-standalone distinction mechanical and unambiguous, and it confirmed the one standalone hit is the intended frozen-template one. Similarly, the tc2 criterion's demand to read `load_config`/`reopen` rather than trust the "hard-fail" framing was well-placed: the engine degrades gracefully, so the real defect was a dangling reference, and the implementer's result correctly restated it — the criterion's independent-read requirement is what let me confirm the rationale rather than the outputs alone. Both are the same independent-reproduction discipline that caught earlier gates' silent-pass and mis-attribution bugs; it held here and found nothing to hold against.
