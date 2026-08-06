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

## 2026-08-01 — 299 (epic-298 baseline capture)

**Lesson:** a-check-that-cannot-fail-is-indistinguishable-from-one-that-passed

**Recurrence (4th in this epic), NEW SHAPE: the mutation test was itself the check that could
not fail.**

The standing lesson's own prescribed repair is "mutation-testing a guard — break the thing,
watch it go red, restore." This run applied that repair and it silently did not work. The
mutation was applied with a `sed` whose pattern did not match; the file was unchanged; the
suite stayed green; and "mutant killed" was the natural reading. It was caught only by
separately asserting that the mutation had actually landed (`assert mut != src`).

So the repair for a vacuous check has a vacuous mode of its own, and the standing lesson does
not warn about it. **A mutation test that does not verify the mutant was applied is exactly the
defect it exists to detect.**

Second shape, same run, same class: the guard's fixtures were all synthesized by the author,
so they encoded the author's *guess* at the input format. `input.command` was the only field
ever exercised, while real `stream-json` transcripts carry `file_path` (Read) and `pattern`
(Glob). Every check passed against a format that does not occur. The fix was to check in a real
transcript excerpt as a fixture — after which restricting extraction to `command` drives 9
checks red.

**Suggested upstream shape:** extend the lesson's repair clause from "mutate the guard and
watch it go red" to "mutate the guard, **assert the mutation applied**, and watch it go red" —
and add that a guard over an external format needs at least one fixture captured from that
format rather than synthesized.

**Grounding:** `.agent-work/epic-298/baselines/extract_ordering.py` (33-check `--self-test`,
`fixtures/real-stream-excerpt.ndjson`); `.agent-work/299/PLAN_CRITIC_DISPOSITION.md` findings
B4 and B6; `.agent-work/AGENT_FEEDBACK.md` 2026-08-01 entry for 299.

## 2026-08-01 — issue-309 (adversarial coherence sweep, #321 fix)

**Lesson:** a-check-that-cannot-fail-is-indistinguishable-from-one-that-passed

**Fifth+ recurrence in this epic, same mechanism class, caught pre-dispatch this time.**
A solo cold plan critic (mandatory per the sibling lesson
`cold-critic-mandatory-for-measurement-dependent-plans`, itself confirmed again this run)
found TWO independent vacuous-pass checks in this run's own gate plan before any crew was
dispatched or any real recall/noise number was produced:

1. **`g1-seed`'s original postcondition** asserted "corpus-slice/ populated with 4 seeded
   copies, none under git tracking" via
   `git status --porcelain .agent-work/ | wc -l -eq 0 || git check-ignore -q
   .agent-work/issue-309/corpus-slice/`. `git status --porcelain` silently OMITS an
   ignored directory rather than reporting it — it does not distinguish "ignored and
   populated" from "ignored and never created" from "not ignored at all." The check
   passed unconditionally the moment `.agent-work/` was confirmed generally ignorable,
   regardless of whether the 4 files existed.
2. **`g0`'s adversarial test spec** for issue #321's fix asked for a traversal-shaped id
   handed to `resolve_episode_path()`, asserted to return `None`. A well-formed-but-absent
   id already returns `None` with or without the new `ID_RE` guard — so a test that only
   checks "returns `None`" cannot distinguish "the guard fired" from "the id was simply
   not found," and would pass whether or not the fix existed.

Both fixed before dispatch (see `.agent-work/issue-309/plan/PLAN_CRITIC_DISPOSITION.md`,
findings 1 and 2, for the corrected checks). Distinct from all four prior recurrences in
mechanism (a `git status`/existence-check confusing "silently absent from a filtered
listing" with "confirmed present," and a not-found-id test standing in for a
guard-fired test) but the same root shape: **a check whose failure path is never actually
exercised is indistinguishable, from the outside, from one that passed for real.**

**Suggested upstream shape, additive to the existing repair clause:** for any postcondition
or test asserting a directory/file is BOTH ignored/excluded AND populated/correct, require
BOTH halves to be independently, positively checked (existence of the specific expected
artifacts, not merely a filtered listing's silence about them) — a single command that can
pass on either half alone is the same vacuous-pass shape as an untriggered guard.

**Grounding:** `.agent-work/issue-309/plan/PLAN_CRITIC_DISPOSITION.md` findings 1 and 2;
`.agent-work/issue-309/execute.json` g1-seed.c1 and g0-fix321-implement's corrected
imperative; `.agent-work/AGENT_FEEDBACK.md` 2026-08-01 entry for issue-309.

---

## 2026-08-05 — issue-419-governor-identity — recurrence of the vacuous-check family, in a NEW place: the plan's own command postconditions

**Lesson:** `lesson:falsify-a-check-against-a-decoy-before-trusting-it`

**What recurred.** Every `command`-kind postcondition in this run's frozen gate plan was **already
green at HEAD, with zero code written**. Three checks, all of the shape
`python -m pytest tests/test_<module>.py -q` — a re-run of the green baseline, dressed as verification
of a change. None asserted that a new test existed, that a new function was exercised, or that any
count had moved. The discriminating content lived entirely in the statement prose the engine never
evaluates.

**Why this recurrence matters more than another instance.** The banked lesson's own bank-reason named
the exact discriminator: *"If a second commander writes a grep-theatre check from the same template, it
is the template."* This is that second commander, working from the same
`EXECUTE_PLAN.template.json`, and the failure took a **different surface form** — not a keyword grep
this time, but a whole-file test invocation. So the pattern is not "authors reach for greps"; it is
**authors reach for the cheapest command that is true when the work is done, without asking whether it
is false when the work is not.** That generalises past greps and past this run.

**The near-miss is the point.** A cold critic caught it by simply *running the plan's own checks against
the unmodified tree* — 140 passed, 1621 passed, exit 0 — before a line was written. Nothing in the
engine, the template, or the spine would have caught it, and all three checks would have gone green at
their gates while proving nothing.

**Suggested upstream shape.** The existing repair clause asks the author to falsify a check against a
decoy. Make the decoy concrete and unavoidable for the commonest case, because the decoy for a test
command already exists and costs nothing: **run every `command` postcondition against the tree as it
stands at plan-freeze time, and refuse to freeze any that exits 0.** A postcondition that passes before
the work starts is not a postcondition. That is one command per check at the plan step, it needs no new
engine primitive, and it would have caught all three of this run's — and, by the same test, both of
issue-310's.

Two secondary shapes worth carrying in the same clause, both measured here:

- A **whole-file test invocation** is the vacuous form for test-led gates the way a keyword grep is for
  doc gates. The repair is naming the new tests by node id (`-k`, or `file::Class`), so the command
  fails on a tree where they were never written.
- A **count assertion needs a direction, not a number.** This run's closeout check originally pinned
  "1621 passed" as the baseline, which was guaranteed not to match once gates added tests. The working
  form asserts the count is strictly **greater** than the pinned baseline, with the delta stated.

**Grounding:** `.agent-work/issue-419-governor-identity/CRITIC_TRIAGE.md` finding 2 (and its
disposition row);
`.agent-work/issue-419-governor-identity/execute.json` `g1-integrate.c1`, `g2-integrate.c1`,
`g6-closeout.c1` as finally authored, each of which now names its new tests and, at closeout, its
required delta; `.agent-work/AGENT_FEEDBACK.md` 2026-08-05 entry for issue-419-governor-identity.
