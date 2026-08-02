# CONSTELLATION_FEEDBACK (staged) — 664-reference-laps (2026-07-26)

Staged per the launch-order fence; the Admiral harvests into the shared
`.agent-work/CONSTELLATION_FEEDBACK.md` at central epic closeout. Each entry carries its
originating Lesson id so the upstream sweep groups recurrences on stable identity.

---
## 2026-07-26 — f1Brainz — cmdr-664 (664-reference-laps)
**Lesson: engine-artifact-attest** (constellation, already `status: exported`).
Recurred again this run: `attest` still refuses artifact-kind postconditions; the working
pattern remains attach-the-artifact + reference-by-`--evidence` at the sibling gate, `attest
--which` for null conditions, `advance` for command conditions. No behavior change observed.
Upstream-fix proposal (unchanged): either make `attest` accept an artifact postcondition when
a matching artifact is already attached, or have the refusal message state the attach-then-
reference recipe inline. NOT a trust issue — pure ergonomic debt across every commander run.

**Lesson: from-child-refuses-on-gated-checklist** (constellation, `status: exported`).
Recurred on the Commander spine's OWN standard shape: the `execute` step names `execute.json`
(a gated child); `--from-child` does not apply (that verb reads a survey `consolidation`).
Recipe that works: drive the gated child to done, release its lease, then plain
`attest <spine-execute-step> --cond c1`. Upstream-fix proposal (unchanged): the
COMMANDER_SPINE template's `execute` imperative should say "do not use --from-child for the
gated execute.json child", or the engine's from-child refusal should hint at the survey-only
restriction.

**Lesson: delegated-commander-foreground-poll-over-watcher-yield** (commander).
Corroborated by a NEW harness fact worth folding upstream: an in-process teammate CANNOT spawn
a background subagent ("In-process teammates cannot spawn background agents") NOR a named one
("Teammates cannot spawn other teammates — the team roster is flat"). So in this harness the
"foreground bounded poll vs detach+notify" boundary collapses — crews MUST be dispatched
synchronous+unnamed (`Agent(run_in_background=false)`), which returns the result inline and
makes the recommended foreground pattern the ONLY pattern. Suggestion: the crew-dispatch
reference could note that in an in-process-teammate harness, synchronous foreground dispatch is
mandatory (background/named spawn is refused), so the "poll the result artifact in a loop"
guidance is a no-op there.

---
Ripe-lesson settlement (export/apply/resolve/defer against the shared `.agent-work/LESSONS.md`)
and application of `lessons-delta.json` are DEFERRED to the Admiral's central harvest per the
fence — this worktree does not write the shared durable playbook.
