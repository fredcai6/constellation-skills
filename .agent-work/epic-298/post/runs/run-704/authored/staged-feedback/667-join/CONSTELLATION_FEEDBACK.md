# CONSTELLATION_FEEDBACK (staged) — 667-join (2026-07-26)

Staged per the launch-order fence; the Admiral harvests into the shared
`.agent-work/CONSTELLATION_FEEDBACK.md` at central epic closeout. Each entry carries its
originating Lesson id so the upstream sweep groups recurrences on stable identity.

---
## 2026-07-26 — f1Brainz — cmdr-667 (667-join)
**Lesson: engine-artifact-attest** (constellation, already `status: exported`).
Recurred again this run: `attest` still refuses artifact-kind postconditions; the working
pattern remains attach-the-artifact + `attest --which` for null conditions + `advance` for
command conditions. No behavior change observed. Upstream-fix proposal (unchanged): make
`attest` accept an artifact postcondition when a matching artifact is already attached, or have
the refusal message state the attach recipe inline. Pure ergonomic debt across every commander run.

**Lesson: from-child-refuses-on-gated-checklist** (constellation, `status: exported`).
Recurred on the Commander spine's OWN standard shape: the `execute` step names `execute.json`
(a gated child); `--from-child` does not apply. Recipe that works: drive the gated child to
done, then plain `attest execute --cond c1`. Upstream-fix proposal (unchanged): the
COMMANDER_SPINE template's `execute` imperative should say "do not use --from-child for the
gated execute.json child", or the engine's from-child refusal should hint at the survey-only
restriction.

**Lesson: self-authored-reasoning-gate-checks-need-review-scrutiny** (commander).
NEW mechanism worth folding upstream: when a self-authored COMMAND postcondition is found
malformed at integrate (here g1-integrate c3's `simplification_limits` used bare positionals
instead of `--paths`, and the `-m` module form hits the editable-.pth worktree trap), the CLEAN
fix on a still-pending/in-progress gate is the engine `amend --retext-check` op (corrects only
the check's command text, invalidates any prior verdict, forces re-evaluation) — NOT a hand-edit
of execute.json and NOT a `waive` (a waiver accepts risk; this is a typo correction, the work
passes under the corrected command). Suggestion: commander-core's "Crew gate vs reasoning gate"
/ "Doc-only gates: pre-author the invariant chain" guidance could name `amend --retext-check` as
the sanctioned remedy for a malformed self-authored command postcondition, so a commander does
not reach for `waive` (wrong tool) or a hand-edit (forbidden).

---
Ripe-lesson settlement (export/apply/resolve/defer against the shared `.agent-work/LESSONS.md`)
and application of `lessons-delta.json` are DEFERRED to the Admiral's central harvest per the
fence — this worktree does not write the shared durable playbook.
