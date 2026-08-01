# Implementation Result — g6-implement (issue #102, Moves 9 & 10)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g6-implement` — two single-home relocations (Move 9 sibling-ids, Move 10 design-it-twice), inspection-only, keep suite green.

## Per-move disposition
- **Move 9 (dedup-sibling-ids): CUT.** admiral's harvest substep 4 was a full inline restatement of the rule; trimmed to operative reminder + pointer. lessons-auditor home left untouched (already the single home).
- **Move 10 (design-it-twice): SUBSUMED by #99.** Both carriers (commander:97, explorer:63) are already pointers to the canonical home; explorer:62 is its own excursion-type mechanic (kept per handoff). No genuine doctrine restatement remained to cut. No edit made.

## Files changed
- `skills/admiral/SKILL.md` (harvest substep 4 only) — the sole edited file.
- (unchanged, verified: `skills/lessons-auditor/SKILL.md`, `skills/commander/SKILL.md`, `skills/explorer/SKILL.md`, `skills/_shared/design-it-twice-brief.md`, `skills/_shared/global-orchestrator.md`.)

**Specific exclusions touched:** no. Canonical design-it-twice text untouched; explorer excursion mechanic preserved; no other gate's doctrine edited; no new global-*.md.

## Behavior changed
No (agent-facing doctrine text only; suite unaffected).

## Move 9 — before/after grep pair
Command: `grep -n "sibling lesson ids\|forks its identity" skills/admiral/SKILL.md`

**BEFORE (admiral:56 tail):**
> When applying the harvested deltas, sibling lesson ids raised from **different worktrees for the same defect** are `confirm`s of the existing lesson (or an `amend` to reword it), **not** new `add`s — a new slug for the same defect forks its identity and breaks recurrence counting.

**AFTER (admiral:56 tail — trimmed reminder + pointer):**
> When applying the harvested deltas, sibling lesson ids raised from **different worktrees for the same defect** are `confirm`s of the existing lesson (or an `amend` to reword it), **not** new `add`s (a new slug for the same defect forks its identity) — the full rationale (recurrence counting, the export fingerprint) lives in the `constellation-lessons-auditor` home, which owns this rule; apply it here, don't restate it.

The operative sentence (sibling ids for same defect = confirm/amend, not new add) is retained inline so the harvest step is not stranded; the recurrence-counting / export-fingerprint rationale is delegated by slug to the `constellation-lessons-auditor` home. Not a bare pointer, not a full restatement.

**Home intact (lessons-auditor:22) — reads the full rule once:**
> **Dedup sibling ids to a confirm, not a new add**: when the *same defect* surfaces under sibling lesson ids across multiple worktrees in one epic, that is a `confirm` of the existing lesson (or an `amend` to reword it) — **never a new slug that forks its identity**. A fresh `add` for a recurring defect splits its history: recurrence counting undercounts, and the constellation-export fingerprint (which keys off the stable lesson id) stops tracking it as one debt. Authoring the delta as a confirm/amend against the existing id keeps that identity — and its debt-not-trust counter — stable.

## Move 10 — subsumption grep (proof both carriers already point)
Command: `grep -n "design-it-twice" skills/commander/SKILL.md skills/explorer/SKILL.md`

- **commander:97** — POINTER (unchanged): "...**plan-alternatives** — parallel gate-plan candidates under distinct constraints converging to one recommendation, **per the shared design-it-twice standard in `references/global-orchestrator.md` and the `references/design-it-twice-brief.md` contract**; ... Both point at doctrine — **the rules live there, not here.**" This is commander's own plan-alternatives gate-mechanic naming, already deferring to canonical for the rules — no constraint-menu / comparison-axes doctrine block to cut.
- **explorer:62** — EXCURSION-TYPE MECHANIC (kept, per handoff): "**Three types**: research ... prototype ... **design-it-twice** (3+ parallel agents design the same module's interface under distinct constraints, compared on depth/locality/seam/testability; opinionated recommendation or hybrid)." Explorer-specific operational description, not a doctrine restatement.
- **explorer:63** — POINTER (unchanged): "Design-it-twice is now a tier-wide standard ... **see `references/global-orchestrator.md` "Design-it-twice (standard, not optional)" and the shared `references/design-it-twice-brief.md` contract** — this excursion type is its design-phase form."
- **explorer:38, :76** — table cell / run-instruction referencing the move by name (kept; not doctrine restatements).

A mechanic-vocab sweep (`grep -ni "constraint menu\|comparison ax\|untaken road\|distinct constraint\|parallel agents design"`) surfaced no duplicated doctrine block beyond the pointers above. Move 10 is substantially subsumed by #99.

## Canonical-untouched confirmation
Command: `git status --porcelain skills/_shared/design-it-twice-brief.md skills/_shared/global-orchestrator.md` → **(empty — clean).**
Full-tree: `git status --porcelain skills/` → `M skills/admiral/SKILL.md` (only).

## Test mode
**Required:** evidence-only (inspection-only; keep suite green).
**Satisfied:** yes.

## Evidence (suite tail)
```bash
py -m pytest tests/ -q
```
**Result:** pass — `442 passed, 2 skipped, 26 subtests passed in 11.51s`.

## Map Impact
- **Structural anchors touched:** `skills/admiral/SKILL.md` (harvest substep 4) — inline sibling-ids rule reduced to reminder + pointer; `skills/lessons-auditor/SKILL.md` confirmed sole home.
- **Constraints/assumptions touched:** single-home invariant for the sibling-ids rule now holds (full rationale reads once, in lessons-auditor); design-it-twice canonical single-home in `_shared/` confirmed intact.
- **Decision candidates / resolved decisions:** Move 10 resolved as subsumed-by-#99 (no action), with grep proof — recorded so reconcile need not re-litigate.
- **Claims/evidence produced:** suite green post-change; canonical `_shared/` diff empty.

## Assumptions
- Read the handoff's "cite by slug/home-name, not by a signature-reintroducing title" (g4 lesson) as satisfied by pointing to `constellation-lessons-auditor` (the slug/home) rather than quoting its rule's bolded title; the AFTER text names the home, not the rule heading.
- Treated the parenthetical "(a new slug for the same defect forks its identity)" as part of the operative reminder (not a rationale restatement), keeping recurrence-counting + export-fingerprint as the delegated rationale — the minimal split that leaves the harvest step self-sufficient without duplicating the full three-nub rationale.

## Stop conditions hit
- None. No cut would have deleted canonical text or explorer's excursion mechanic; no carrier entangled another gate's doctrine (commander:97 co-locates plan-alternatives + cold-critic, but each already points at its own standard — untouched).

## Out-of-scope observations
- None new. (manifest / ROADMAP / repo-root stray tracked as #105 per handoff; not touched.)

## Workflow Feedback
- **Handoff gaps:** none material. The Move 9 spec was precise; the only latent tension was between "point to lessons-auditor for the full rationale (forks-identity / recurrence-counting / export-fingerprint)" and single-home discipline — listing all three nubs in admiral would re-duplicate the home. Resolved by keeping only "forks its identity" as an operative gloss and delegating the other two. A one-line note in the handoff on which rationale nubs (if any) may stay inline vs. must delegate would remove that judgment call.
- **Context rediscovered:** `config_ref` in the plan template points at `docs/agents/engine-config.json`, which does not exist in this worktree (prior g4/g5 plans carried the same dangling ref and still ran). The engine tolerates it, so no blocker — but the dangling default ref is a minor papercut for anyone validating the plan by hand.
- **Instructions improvised around:** engine `attest` requires `--cond` (and `--which preconditions` for preconditions); the plan template's imperative says "attest c1" without the flag form. Minor; discovered on first call and corrected.
- **What would have made this easier:** none beyond the two notes above.

## Return status
`complete`
