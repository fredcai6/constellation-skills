# Launch Order: `commander-142 — issue #142 (clamp restoration + enforcement prose)`

## Mission
Implement https://github.com/fredcai6/constellation-skills/issues/142 — restore the measured four-clause completion doctrine across the stripped skills and upgrade the shared prose home. This is the getting-IN moment of the #138 counter-doctrine: no runtime channel reaches an agent before its first engine call, so skill text is the only defense there. Deliverable: a green, reviewed PR on branch `issue-142`.

## Prior-Wave Verdicts (pasted)
From the #101 SIMPLIFICATION_REVIEW (2026-07-11): at base, NINE skills carried an in-context "Mandatory, no exceptions: drive [workflow] to completion through the engine" clamp; on current main that text survives only in `_shared/global-everyone.md`, reachable via the bare pointer "Compliance/engine-drive rule: inherited — see references/global-everyone.md". The pointer wording is character-identical across the nine skills — a clean mechanical restore target. The clamp's first clause names a load-time trigger that pointer-delivery defeats by construction. Ranked exposure: (1) crew implementer + reviewer (guards skip/theater/fabrication one tier below Commander — HIGHEST), (2) commander-core.md (both modes inherit), (3) admiral entry clamp, (4) interrogator "drive the survey to completion".

From the #129 measurement arc: four flat-imperative clauses — engine-first entry; solution-is-the-MIDDLE; release-after-final-advance; wait-loop — took the delegated commander from ~1/3 to 3/3 strict terminal completion on sonnet. The eval-proven wording lives in the repo's delegated-commander skill text on current main (find it there; it is your transcription source — transcription-grade means THAT wording, not a paraphrase).

From the CONFIRMED #138 spec (§D1): the target denominator is the SIMPLIFICATION_REVIEW's stripped-skill enumeration, defined by reference (the "nine" was a stale count — enumerate file-by-file in your PR body). High-exposure targets (crew implementer, crew reviewer, commander-core, admiral, interrogator) get the four clauses transcription-grade. The remaining pointer-only skills get this sentence VERBATIM:

> Drive every step through the checklist engine and finish its sequence — final `advance`, then `release`, as journaled actions. Work the engine never saw did not happen. Full completion doctrine: `_shared/global-everyone.md`.

Plus (§D4 enforcement half): upgrade the scoped-nulls section of `skills/_shared/global-everyone.md` as the prose elaboration home, citing the engine rail string table (being built in #140, same wave) as the canonical enforcement source — on conflict the rail table wins.

## Pre-Rulings
- Text is spec-frozen: four clauses transcribed from the in-repo eval-proven source; pointer sentence verbatim from above. A deviation you believe necessary STOPS and floats.
- NO new files. NO all-caps/exclamatory styling. The #101 judged-correct removals (banners) stay removed.
- Adapt only the clause's role-noun where grammatically required (e.g. "this run"/"the survey") — flag every such adaptation in the PR body.
- Add a presence test (script or test asserting the wording exists in each target) so the clamps cannot silently re-strip.
- You cannot see #140's final rail code (parallel wave) — cite the rail table as "the engine rail string table (`checklist_engine.py`, #140)" in prose; do not block on it.

## Honest-Null Clause
A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win.

## Inherited Latitude
You may: decide exact clamp placement within each SKILL.md (load-time-early per the review's finding); minor grammatical adaptation (flagged). You must float: wording changes, denominator disputes (if the review's enumeration conflicts with current main, report what you found), anything touching eval task.md. Merges are the human's — open the PR, never merge.

## File Ownership
Sole writer of: `skills/**/SKILL.md` doctrine text, `skills/_shared/global-everyone.md`, `skills/**/commander-core.md`, your presence test, and `.agent-work/epic-138/verdicts/commander-142.md` (MAIN checkout, absolute path below). Do not touch `scripts/`.

## Workspace
`C:/Programs/constellation-wt-142` — branch `issue-142`, base commit 93f38505 (main), created via `git worktree add ../constellation-wt-142 -b issue-142 main`.
First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-142` — must exit 0; paste output into your report.
NOTE: PR integration defaults to **server-side merge**.

## Inherited Context
- Windows/py launcher conventions; UTF-8 writes; `gh pr create -F <tempfile>` for PR bodies.
- Superpowers is a competitor — never cite or import its doctrine.
- Source repo is authority: edit `skills/` in-repo; NEVER touch installed copies at `~/.claude/skills`.

## Pre-empted Steps
Context and plan pre-empted: design confirmed through a full explorer pass. Your understand step is the SIMPLIFICATION_REVIEW + the in-repo skill files + this order.

## Data Locations
- #101 stripped-skill enumeration (untracked, main checkout): `C:/Programs/constellation-skills/.agent-work/dispatch-126-127/SIMPLIFICATION_REVIEW.md`
- Confirmed spec: `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/DESIGN_SPEC.md`

## Budget
- **Model tier (required):** sonnet (bounded, spec-frozen wording work; least-powerful that works).
- **Compute/time, session-window:** target ≤ 45 min.

## Stop Conditions
Stop and return when: the enumeration is ambiguous against current main, a wording deviation seems needed, budget crossed, or context missing — return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape
Verdict + evidence to `C:/Programs/constellation-skills/.agent-work/epic-138/verdicts/commander-142.md`: PR URL, the file-by-file denominator list, presence-test results (exit codes), isolation-check output, flagged adaptations, triage candidates, workflow feedback. Deliver artifacts **before** going idle.
