# Constellation Feedback Export

Lessons scoped `constellation` — about the skills, templates, or engine themselves,
not this project. Appended by the feedback/closeout steps; swept by the skills
repo's `collect_feedback.py`, which treats scope tags as claims to verify
(cross-project recurrence is the validator). Per-entry collection/resolution
state lives in the sidecar `CONSTELLATION_FEEDBACK.collected.json` (script-owned;
collected means ingested by a sweep, resolved means acted on upstream — a
candidate stays visible in sweep reports until resolved). Just append entries;
never edit the sidecar by hand. Never archived with a run.

Recurrence is the validator, so a finding's **identity must be stable across
runs**. When this export derives from a `constellation`-scoped lesson, carry that
lesson's id in the **Lesson** field — the sweep fingerprints on it, so the same
finding groups even as its prose/slug drift. Reword a recurring finding by
`amend`-ing the lesson (its id is preserved), not by inventing a new slug. Only
when there is no originating lesson does the sweep fall back to the candidate
slug.

## Cleared 2026-07-27 by the constellation-curator weekly sweep

Supersedes the 2026-07-17 and 2026-07-24 clear notes (collapsed here to keep this file bounded;
full sweep records live in the constellation-skills repo).

**CORRECTION carried forward — read this before trusting a past "resolved upstream" ruling.**
The 2026-07-17 sweep cleared `engine-artifact-attest` / "`attest` precondition/postcondition
fallback" as resolved. **It was not.** Verified 2026-07-27 against repo HEAD *and* the global
install (byte-identical): `checklist_engine.py:2001` still refuses `attest` on an artifact-kind
postcondition — `attach` first is still required. A narrower improvement had shipped
(`attest --evidence <id>` satisfies an identical sibling postcondition *by reference*) and the
sweep over-generalized it. Cost: 4 f1Brainz sub-runs re-hit the pattern against a finding the
fleet had been told was closed; 18 recurrences accrued. Now tracked live in **#220**.

**Dispositions this sweep:**
- **Mended (PR #258):** `init_work_area.py --root` silently scaffolding `.agent-work/.agent-work/`
  — now refuses and names the intended root; 3 tests, suite 1074 green.
- **Resolved upstream (cleared):** REVIEWER_HANDOFF missing a `Survey State Location` field
  (present in repo *and* install); `from-child-refuses-on-gated-checklist` (already a tracked
  item in #220); #208 TR-1 harvest doctrine (shipped 7c8ff1b).
- **Out of scope for constellation (cleared):** `simplification_limits` standing postcondition and
  the `--paths` flag slip — both about a consuming project's own CLI, not shared machinery.
- **Routed:** engine/CLI ergonomics + the attest correction + `run_crew.py` harness detection →
  **#220**; launch-order Data Locations provenance + canonical-routing stop conditions → **#221**;
  reviewer perturb-restore data-loss hazard + `--override-reason` sanctioning → **#259**;
  resumed-subagent cwd leak + Agent-tool self-send + fast-integrate-gate fork → **#260**;
  harvest-completeness enforcement → **#208**; corpus-health null result → **#117**.
- **Corpus health:** 73 findings / 52 flagged — identical to last week, zero drift. No install lag.

See `constellation-skills/.agent-work/CURATOR_REPORT.md` for the full sweep.
Append new entries below this line.
### commander-core.md instructs delegated Commanders to use a channel their tier cannot open

- **Where:** `skills/commander/references/commander-core.md`, Mission frame section — "Any background subagent you dispatch ... must be told **in its spawn prompt** to deliver its result via `SendMessage`".
- **Defect:** a delegated Commander runs as a *teammate*, and the harness refuses a teammate spawning a *named* subagent ("Teammates cannot spawn other teammates — the team roster is flat"). Unnamed subagents have no `SendMessage` address, so the instruction is unfollowable at exactly the tier the doctrine targets. All four design-panel dispatches from commander-301 failed on first attempt.
- **Also misleading, not just impossible:** the stated rationale (teammates "end on a bare idle notification with the report undelivered") does not apply to an unnamed subagent, whose final message the parent reads directly.
- **Suggested:** split the guidance by tier — keep the SendMessage line for agents that can spawn named teammates; for a delegated Commander, specify "dispatch without `name`; deliverable to a path, summary as the final message." Check whether `skills/admiral/` carries the same instruction downward.
- **Filed:** fredcai6/constellation-skills#314
# CONSTELLATION_FEEDBACK exports — staged from issue-300 (epic-298)

Constellation-scoped findings from this run. Per the counter semantics, a constellation-scoped
lesson accrues *debt*, not trust — these are exported for upstream fixing rather than confirmed into
permanent workarounds. Both are already filed to the tracker.

## 1. Delegated Commander (teammate) cannot spawn named or background subagents

**Target:** `constellation-commander` skill's `references/commander-core.md` (§Mission frame,
the "must be told in its spawn prompt to deliver via SendMessage" clause) and
`constellation-commander-delegated/SKILL.md` (§5, "wait actively, inside your turn: poll the crew's
result artifact ... in a loop").

**Defect:** a delegated Commander dispatched by an Admiral runs as a harness teammate. Teammates
cannot spawn *named* subagents ("the team roster is flat") and cannot spawn *background* subagents
at all. So an unnamed subagent has no address and cannot `SendMessage` a teammate parent, and a
synchronous dispatch cannot be polled because it blocks. Both instructions are unfollowable at the
exact tier that is told to follow them.

**Not a blocker:** multiple synchronous `Agent` calls issued in ONE message do run concurrently, and
the result-artifact file is a fine delivery channel. But each restriction costs a failed-dispatch
discovery round-trip, and a Commander that trusts the doctrine will burn both.

**Suggested edit:** qualify both clauses with the teammate case — "when you are yourself a teammate,
dispatch synchronous subagents in parallel in a single message and take delivery from the result
artifact rather than SendMessage."

**Filed:** issue #316.

## 2. Engine command postconditions inherit the launcher's cwd

**Target:** `scripts/checklist_engine.py`, `_run_check_command`.

**Defect:** it calls `subprocess.run([shell, "-c", command])` with no `cwd=`, while `_git()` in the
same file passes `cwd=base_dir`. Every relative path in a gate's `command` postcondition therefore
resolves against wherever the engine process was launched rather than the checklist's own base dir.
Fails closed for most check shapes, but a negated or short-circuiting form can return 0.

**Filed:** issue #315.

## Also filed, project-scoped rather than constellation-scoped

Issue #317 — every spine template carries `config_ref: docs/agents/engine-config.json`, a path that
is absent-by-design in skill-source repos, together with several hundred words of imperative prose
explaining that it is dead. A corpus-wide cleanup, deliberately not fixed inside #300 because a
single divergent plan is a worse local state than the redundancy.

## 3. Survey checklists: `record` is the re-record verb, and nothing says so

**Target:** `constellation-reviewer` skill's checklist doctrine, and the engine's REFUSED text.

**Defect:** on a `survey`-type checklist, `advance` and `reopen` both refuse as gated-only. The way to
re-record a check after a rework round is to call `record` again on a terminal item. That works, but
it is documented nowhere and the refusal message names neither the rule nor the alternative — the
same shape as the already-exported
`lesson:checklist-engine-from-child-relative-path-and-gated-vs-survey`.

**Grounding:** the g1/g3/g5 reviewer hit it across **five** review rounds in this one issue and
reported it each time, having found it by being refused rather than by reading anything. Its words:
*"Fifth round, one-line fix in the reviewer SKILL."*

**Suggested fix:** one line in the reviewer skill's checklist section, and add the alternative to the
engine's gated-only refusal message so it is discoverable from the error.

## 4. Engine `--finding` text is shell-mangled when it contains backticks

**Target:** `scripts/checklist_engine.py` journal writes, or the doctrine that tells agents how to
pass finding text.

**Defect:** a `--finding` string containing backticks was mangled by the shell and **silently dropped
two words** from the journal. The engine accepted the truncated text without complaint, so the
provenance record is quietly wrong rather than loudly rejected.

**Grounding:** reported by the g5 reviewer at the end of its BLOCK round. Same class as this run's
other silent-degradation findings: the failure produces a plausible-looking artifact.

**Suggested fix:** either strip/escape control characters on the engine side, or state the
single-quoting requirement where agents are told to pass finding text. Given how much of this system's
value is in journal provenance, silent truncation of a finding is worse than a refusal.
