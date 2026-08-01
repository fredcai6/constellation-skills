# Implementer Handoff

## Gate
g5 — Deep-module vocabulary + Commander intake line + installer + install tests (issue-58; FINAL gate — this one takes the suite fully green and ends the waiver window)

## Task
Wire the two new skills into the shared doctrine, the Commander seam, and the installer. Design contract: `.agent-work/issue-58/DESIGN_SPEC.md` (CONFIRMED, read-only) — governing sections "Chosen design 3", "4. Install and test integration", and the "Commander seam (one line, in scope)" paragraph under Chosen design 1.

1. **`skills/_shared/global-everyone.md`** — append a concise **"Deep-module vocabulary"** section, dense and departures-only, matching the file's existing register. Terms (spec-fixed): **module** (interface + implementation, scale-agnostic); **interface** (*everything* a caller must know — invariants, ordering, error modes, config, performance — not just the type surface); **seam** (where an interface lives; its placement is its own decision); **adapter** (a thing satisfying an interface at a seam; **one adapter = hypothetical seam, two = real**); **depth/leverage** (behavior per unit of interface a caller must learn); **locality** (change and verification concentrate in one place). Plus the two working rules: **the interface is the test surface** (wanting to test past it means the module is the wrong shape) and **the deletion test** (delete the module in imagination: complexity vanishes = pass-through; reappears across N callers = earning its keep). The integrate gate greps for `deep-module` (case-insensitive) in this file.
2. **`skills/commander/SKILL.md`** — add the shaped-design intake line to the understand-step guidance (ONE line-scale addition, not a section): an ask citing a shaped-design spec/issue is verified confirmed (`verify_spec_confirmed.py` passes / CONFIRMED marker visible) before work is cut; an `UNCONFIRMED — DO NOT CUT` shaped-design issue is never cut into work. **Marker discipline: the marker mention must be INLINE in prose, never a standalone line** (verified classes of this in g2/g4 — check against `verify_spec_confirmed.py`'s `_unconfirmed_marker_hit` if in doubt). The integrate gate greps for `shaped-design` (case-insensitive) in this file.
3. **`scripts/install_constellation.py`** — `SKILL_SCRIPT_BUNDLES["explorer"] = ("checklist_engine.py", "init_work_area.py", "run_crew.py", "recover_crews.py", "verify_cycles.py", "verify_spec_confirmed.py")`; `SKILL_REFERENCE_BUNDLES["explorer"] = _GLOBAL_ORCHESTRATOR`, `SKILL_REFERENCE_BUNDLES["prototyper"] = _GLOBAL_CREW`. Prototyper needs no scripts. Match the exact key convention the dicts use (directory name vs installed name — read the dict and its consumers first).
4. **`tests/test_install_constellation.py`** — add `constellation-explorer` and `constellation-prototyper` to the expected-skills list (this clears the last 2 waived failures); assert the explorer script bundle (all six scripts land in the installed skill); assert the installed explorer's `global-everyone.md` copy carries the Deep-module vocabulary section (this is spec Testing pathway 3's "vocabulary ships to every skill via the existing reference-bundle mechanism").
5. Run `python scripts/install_constellation.py --dry-run` (check its actual flag name via --help) to confirm discovery of both new skills with correct installed names; paste the output.

## Protected Intent
This gate ends the epic's transient window: after it, `python -m pytest tests/ -q` must be FULLY green — no waiver, no exception. The vocabulary lands in the single-source shared file so every installed skill inherits it without installer changes; the Commander line is the downstream half of the hard gate (explorer refuses to emit unconfirmed specs; Commander refuses to consume them).

## Test Mode
Test-after allowed; item 4's assertions are gate deliverables. The suite itself is the red→green proof: the 2 expected-skills failures exist NOW and must pass AFTER — confirm you see them red before your change (they are the pre-existing waived failures) and green after.

## Close Criteria
- All four file changes per items 1–4; dry-run discovery output per item 5.
- `python -m pytest tests/test_install_constellation.py -q` fully green.
- **`python -m pytest tests/ -q` FULLY green** — zero failures of any kind. This is the epic's exit criterion; there is no waiver at this gate.
- Integrate-gate greps pass: `grep -qi 'deep-module' skills/_shared/global-everyone.md`, `grep -qi 'shaped-design' skills/commander/SKILL.md`.
- No standalone `UNCONFIRMED — DO NOT CUT` line introduced anywhere (inline prose only).
- Commander SKILL.md change is one-line-scale in the understand guidance; no other Commander doctrine touched.
- Commit on `constellation/issue-58`.

## Allowed Scope
- EDIT: `skills/_shared/global-everyone.md` (append vocabulary section), `skills/commander/SKILL.md` (understand-step intake line only), `scripts/install_constellation.py` (the two bundle dicts only), `tests/test_install_constellation.py` (additive: expected list + new assertions).

## Specific Exclusions
- Do NOT touch: `skills/explorer/**`, `skills/prototyper/**` (g2–g4, frozen), `scripts/verify_*.py`, `scripts/checklist_engine.py`, `scripts/init_work_area.py`, `scripts/run_crew.py`, `scripts/recover_crews.py`, other tests/ files, `.agent-work/issue-58/DESIGN_SPEC.md`. If a frozen file turns out to be wrong (e.g. a bundle script name mismatch), STOP and surface it — do not patch frozen files.

## Constraints
- Vocabulary section: dense, departures-only, matching global-everyone.md's register — not an essay; the spec text above is the content contract.
- Installer edits limited to the two dict entries; no refactors, no new mechanisms.
- Contractual strings: the six vocabulary terms, the two working rules, `shaped-design`, the marker (inline only), bundle script names exactly as listed.
- Python 3 stdlib only.

## Map Anchors (inbound)
- **Structural:** skills/_shared/global-everyone.md (append), skills/commander/SKILL.md (one line), scripts/install_constellation.py::SKILL_SCRIPT_BUNDLES/SKILL_REFERENCE_BUNDLES, tests/test_install_constellation.py (additive)
- **Capability:** vocabulary shipped to every skill via existing reference-bundle mechanism; Commander downstream refusal seam; both skills installable with correct bundles
- **Constraints/assumptions:** suite fully green = epic exit criterion (waiver window ends here); marker inline-only discipline; frozen g2–g4 files
- **Decision anchors:** DESIGN_SPEC "Chosen design 3" + "Install and test integration" + Commander-seam paragraph — surface conflicts, don't improvise
- **Evidence expectations:** red→green on the 2 expected-skills tests; full suite zero failures (feeds g5-integrate.c1, which has NO override policy)

## Deliverable Path Check
- **Committed** — all four paths; verify none gitignored.

## Required Evidence
- Pasted BEFORE state: the 2 expected-skills failures red (pre-change full-suite or targeted run).
- Pasted AFTER: `python -m pytest tests/test_install_constellation.py -q` green AND `python -m pytest tests/ -q` fully green.
- Pasted dry-run discovery output showing both skills with installed names `constellation-explorer` / `constellation-prototyper`.
- Pasted grep outputs for `deep-module` and `shaped-design`.

## Verification Commands

```bash
python -m pytest tests/test_install_constellation.py -q
grep -qi 'deep-module' skills/_shared/global-everyone.md && grep -qi 'shaped-design' skills/commander/SKILL.md && echo GREPS-OK
python -m pytest tests/ -q
```

## Suggested Model Tier
simple bounded — four tightly-scoped edits with an unambiguous mechanical exit criterion.

## Authority
Design fixed by DESIGN_SPEC.md. You may choose the vocabulary section's exact prose (within the term/rule contract) and the intake line's wording. You may NOT add scripts to prototyper's bundle, expand the Commander edit beyond the intake line, restructure the installer, or touch frozen files. Surface conflicts instead.

## Stop Conditions
Stop and return if: the full suite cannot reach fully green without touching a frozen/excluded file; the installer's dict conventions don't match what the spec assumes (surface the mismatch); or a decision outside authority is needed.

## Return Format
Return IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g5-implement/IMPLEMENTER_RESULT.md`: completed slice, files changed, evidence produced (pasted red→green, dry-run, greps), assumptions, stop conditions hit, out-of-scope observations, workflow feedback (run-specific; bare `none` = unfilled).
