# Triage — lane D1 (#559), 19 candidates, **zero issues filed**

**Disposition for every candidate: `recommend-and-defer`.** No `filed`, and no `fix-now` remaining —
the three fix-now items this run took (the `.:` typo in three copies, the re-review convention
tightening, and the five POSIX check repairs) were taken inside their own gates and are already in
the diff.

**Filing is ruled, not chosen.** `decision:no-issue-filing-mid-run`, `@grade: settled/human`, with
the human's reason verbatim: *"we've been ballooning out tracking."* Each candidate is staged as a
file under `.agent-work/567-d1/triage-candidates/`, tracked and committed on this branch, so it
reaches `main` at merge. At epic closeout each is paired onto an **open** issue as a comment, or
recorded as an episode. A lane that wants to file is not floating a decision — the answer is already
ruled.

## Ranked for the Admiral

**Priority 1 — a live hazard, not a documentation nit**

1. `dispatched-crew-spine-is-not-bound.md` — the crew skills state that a dispatched crew's spine is
   bound before it starts; for a handoff-driven `run_crew.py` dispatch it is not. **Six independent
   reproductions, three gates, both roles.** The sharp end: the g1b re-reviewer finished its work and
   was refused permission to end its turn by the Stop hook, which resolved a spine from disk and
   handed it **this Commander's** spine, whose in-progress step was the crew's own dispatch. It
   refused — *"That's impersonation, not delegation."* The hook's sanctioned escapes (`block`,
   `waive`) both write to the parent's spine, so the prescribed honest stop is itself the destructive
   act. Cheap fix: skip the hook when `SPINE_FILE` is unset and `SPINE_PARENT` is set. Durable fix:
   have `run_crew.py` bind the crew's own plan.

**Priority 2 — checks that cannot do their job**

2. `pipefail-in-command-checks-cannot-pass.md` — `set -o pipefail` in an engine `command` check is
   rejected by dash with exit 2 before the check runs. Five of this run's own checks shipped with it.
3. `whole-suite-evidence-is-unsafe-during-engine-drive.md` — the standard whole-suite evidence
   command fails for any crew that records through the engine while it runs. Deterministic, and it
   fires on exactly the recipe the role skills prescribe.
4. `doctrine-asserts-spine-postconditions-with-no-tie.md` — three doctrine files assert facts owned by
   `COMMANDER_SPINE.template.json` with nothing connecting them. This is the coupling that **caused
   #596**, uncorrected.

**Priority 3 — structure this run exposed**

5. `corpus-never-names-the-doors-binding-call.md` — after lane D2 merges, no corpus file will tell an
   in-session crew member how to drive its own plan. Nobody is stranded (the door's refusal carries
   its remedy), but this needs a deliberate epic-level answer.
6. `overlay-baseline-mirror-doubles-every-target.md` and 7. `templates-manifest-is-a-fourth-copy.md` —
   the same doctrine now lives in four tracked copies with no automatic reconciler.

**Priority 4 — smaller, each with a named owner elsewhere**

8. `fowler-record-path-collides-across-gates.md` · 9. `crew-launcher-scratch-dir-test-fails-inside-a-crew.md`
· 10. `crew-context-python-invocation-stale.md` · 11. `mcp-spine-server-cli-fallback-sentence.md` ·
12. `glossary-has-no-door-entry.md` (no entry for **"door"**, the term this epic makes load-bearing) ·
13. `feedback-export-template-claims-a-writer-that-is-gone.md` ·
14. `prose-names-vendored-script-paths-corpus-wide.md`

**Inherited from the plan step, unchanged:** `engine-config-json-absent.md` ·
`execute-json-anchors-duplicated-per-task.md` · `map-ids-jsonl-empty.md` ·
`verify-frame-refuses-graded-decisions.md` · `headless-dispatch-inherits-parent-spine.md`
