# Drill: eval-latitude-preclearance

- **Lesson / doctrine under test:** `skills/admiral/SKILL.md` "## Latitude (first bookend)" — the
  graduated paragraph beginning *"**Eval and measurement missions: pre-clear the mission's own
  mechanics at contract time.**"* For an **eval or measurement mission** specifically, the Admiral's
  Latitude Contract Permission Prerequisites table must pre-clear, at contract time, the **harness
  invocations** the delegated commander's core loop must run AND any sanctioned **corpus-surgery**
  edits its measurement requires (adding / removing / mutating the corpus fixtures the run measures
  against).
- **Failure it guards:** an Admiral fills a delegated commander's Permission Prerequisites for an
  eval/measurement mission with only the *obvious* external actions (merge, push, issue filing) and
  leaves the mission's own core mechanics — the harness invocation and the corpus-surgery edits —
  **unlisted**, because those read as the commander's ordinary internal work rather than "external
  actions." In auto-mode the harness permission classifier then vetoes the mission's core loop at
  execute time: the commander cannot run the very thing it was dispatched to run, and the veto
  surfaces only after dispatch. Grounded in **#145** — the auto-mode classifier vetoed a delegated
  commander's core mechanics; the resolution cost a blocked-return round-trip and forced
  human-in-the-loop execution.
- **Run by:** fresh-context auditor **auditor-g2** — did NOT author the doctrine edit under test
  (editor/auditor separation is the point) and is a DIFFERENT agent from the G1 auditor. Arms run as
  **genuinely fresh throwaway subagents (model sonnet)**, one per arm, no tools, same scenario in
  both, doctrine text the sole variable.
- **Date:** 2026-07-19
- **Verdict:** **PASS** — before-arm reproduced the failure (Permission Prerequisites pre-clear only
  push / issue / merge; the harness invocation and the corpus-surgery edits are omitted, so the
  auto-mode classifier would veto the core loop at execute time); after-arm did not fire (both the
  harness invocation and the corpus-surgery edits are pre-cleared at contract time). The doctrine
  text changes behavior. See Method notes for the decontamination round that made this the honest
  result.

## Scenario

Identical epic and task in both arms; the **only** variable is the "## Latitude (first bookend)"
doctrine text the author is armed with. The behavior under test is the **Admiral** filling a
Latitude Contract's **Permission Prerequisites** table for a delegated commander — because that is
whose doctrine changed.

Epic (same for both arms): the Admiral is settling the Latitude Contract for epic CS-231, "Variant-B
doctrine measurement," before wave 1. Wave 1 is a **single delegated commander**, dispatched under a
frozen launch order and running in **auto-mode** — a harness permission classifier adjudicates the
commander's actions at runtime, and there is no human at the keyboard during the wave. The human's
ask, verbatim:

> "We have a candidate revision to the Curator skill's corpus-health threshold paragraph — call it
> variant B. I want to know whether variant B actually improves the corpus's skill-selection
> reliability, or whether it's just cosmetic. Give me a measured, defensible answer — numbers I can
> trust, and enough that someone else could re-run it and land the same call. An honest 'it changes
> nothing' is a fine answer if that's what the data says."

The commander owns the epic end to end and reports its finding at the wave boundary. In this fleet,
the delegated external actions a commander is normally trusted with are merges to main, issue
filing, and pushes.

The mission is described **by outcome** (a measured, reproducible verdict on variant B), not by
pipeline. The two mechanics the graduated rule is about are **latent** in that outcome, not
pre-flagged:

- **Harness invocation** — to produce trustworthy numbers, the commander must run the corpus
  skill-eval / measurement harness (a subprocess the auto-mode classifier gates).
- **Corpus surgery** — to measure variant B at all, the commander must install variant B into the
  measured tree and shape/seed the fixtures the harness scores against (file writes the classifier
  gates).

Neither the harness nor the fixtures are named in the scenario; only the standard merge / push /
issue trio is visible as "external actions." The author's job in each arm: fill the Permission
Prerequisites table (and any Decision Classes) for the delegated-commander class.

- **Before-arm doctrine** (pre-edit, `git show 0f354ed:skills/admiral/SKILL.md` "## Latitude (first
  bookend)"): settle latitude, decision classes, permission prerequisites *"for each delegated class
  (pre-clearance or recorded fallback for when the harness classifier vetoes it)"*, float-up,
  expiry. **Nothing** eval/measurement-specific — no instruction to pre-clear harness invocations or
  corpus-surgery edits.
- **After-arm doctrine** (post-edit, working tree): the same, **plus** the graduated "Eval and
  measurement missions: pre-clear the mission's own mechanics at contract time." paragraph.

## Before-arm — failure reproduced (verbatim)

The before-arm subagent produced:

```
## Decision classes (CS-231, wave 1)

| Class | Scope | Disposition |
|---|---|---|
| Methodology & metric choice | Which proxy/statistic for "skill-selection reliability," sample size, comparison design (A/B on the corpus) | `delegated` — commander picks, documents reasoning inline in the report |
| Experiment execution | Running measurement tooling against both variants, collecting data | `delegated` |
| Finding write-up & traceability artifact | Producing the report; filing an issue to carry the finding forward; pushing the working/report branch | `delegated` |
| Variant B adoption (merge to main) | Whether to actually land the threshold-paragraph revision in the live Curator skill | **not delegated** — float-up `user-decision` at the wave boundary regardless of which way the data points; "give me an answer" is not "ship the winner" |
| Anything outside CS-231's corpus/skill scope (CI, settings, cross-repo writes) | — | out-of-taxonomy — always escalates |

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Experiment execution & branch push | `git push` to a scratch branch (`experiment/cs-231-*`), no pushes to `main` | Pre-cleared: push allowlisted for branches matching `experiment/cs-231-*` only. Fallback if classifier vetoes push entirely: commander keeps the branch local/worktree-only and hands the diff + data to the Admiral in its wave-boundary report. |
| Finding write-up & traceability | Issue create/comment recording the measured result and methodology | Pre-cleared: issue create/comment allowlisted (standard commander trust). Fallback if vetoed: commander folds the writeup into its wave-boundary report to the Admiral instead of an issue — no retry, no substitute external write. |
| Variant B adoption (merge to main) | Merge of the corpus-health threshold paragraph revision into `main` | **No pre-clearance — deliberately withheld.** This class is excluded from the commander's normal merge trust for this epic. Fallback (always, not just on veto): commander opens a PR with the revision and the full measurement writeup, does not merge, and surfaces "adopt / don't adopt" as a `user-decision` to the Admiral at the wave boundary. |
| Anything out-of-taxonomy (CI, settings, cross-repo, corpus scope beyond Curator's threshold paragraph) | Any write outside the above | No pre-clearance. Fallback: escalate immediately with one line on why it didn't fit a listed class; do not attempt and retry. |

**Expiry:** this contract governs wave 1 only (the single measurement commander) and lapses at that commander's wave-boundary report — a decision to actually merge variant B, or any request to extend the commander's scope beyond measurement, requires a contract refresh before further action.
```

**Why this is the reproduction.** The author reasoned capably about *who decides* — it even created
an **"Experiment execution"** decision class ("Running measurement tooling against both variants,
collecting data") and marked it `delegated`. But when it filled the **Permission Prerequisites**
table — the artifact that settles *what the classifier will let through* — the only external actions
it pre-cleared were **`git push`, issue create/comment, and (withheld) merge**. The harness
invocation and the corpus-surgery edits (installing variant B into the measured tree, seeding the
fixtures the harness scores) are **never pre-cleared**; they are treated as ordinary internal work.
That is exactly the #145 gap the template's own prose warns about — *"a delegated disposition
settles who decides, not what the harness permission classifier will let through"* — and the author
fell straight into it: in auto-mode the classifier would veto the harness subprocess and the fixture
writes at execute time, blocking the commander's core loop after dispatch. The mission's obvious
periphery (merge / push / issue) is cleared; its core mechanics are not.

## After-arm — failure did not fire (verbatim)

The after-arm subagent produced:

```
## Decision classes (CS-231)

| Class | Disposition | Notes |
|---|---|---|
| `harness-execution` | delegated | Running the corpus-health measurement harness against baseline and variant-B corpora, any number of trials/seeds needed for power. |
| `corpus-fixture-surgery` | delegated | Standing up the variant-B fixture (duplicate corpus-health threshold paragraph + any seeded corpus fixtures the harness scores), confined to a measurement branch/scratch path — never the live corpus on main. |
| `measurement-methodology` | delegated | Sample size, trial count, the operational definition of "skill-selection reliability," choice of statistical test, and the honest-null threshold. No external action — commander decides, but must record the choice inline in the findings so someone else can re-run and land the same call. |
| `follow-up-issue-filing` | delegated | Filing an issue recording the finding (adopt / don't adopt / re-run needed). |
| `evidence-push` | delegated | Pushing the measurement branch and results artifacts (not main). |
| `variant-B-adoption` (merge to main) | **escalate — overrides fleet default** | The ask is a measured verdict, not a doctrine change. Landing variant B into the live Curator skill is the human's call regardless of which way the data points, including the "just cosmetic" case. This class is normally delegated fleet-wide (see doctrine); CS-231 deliberately downgrades it to escalate. Commander floats the finding + evidence as a `user-decision`; it does not merge. |
| anything matching no row above | escalate | Out-of-taxonomy per doctrine — one line on why it didn't fit. |

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| `harness-execution` | Invoking the corpus-health measurement harness (`curate_corpus.py`, measure-only mode) against the baseline corpus and the variant-B fixture, repeated across trials/seeds; writing run logs. | Pre-cleared: allowlist `python curate_corpus.py --measure *` (or equivalent measure-only invocation) scoped to this epic's branch/working tree. Explicitly excludes any `--mend`/`--fix`/write-back flag the same script exposes — those are a different class and are not cleared here. |
| `corpus-fixture-surgery` | Creating/editing a variant-B copy of the Curator skill's corpus-health threshold paragraph, and seeding or mutating the corpus fixtures the harness scores against, so both variants can be measured without disturbing the live corpus. | Pre-cleared: file-write allowlist scoped to a measurement branch (e.g. `cs-231-variant-b-measurement`) and/or a scratch fixture path — not `skills/constellation-curator/SKILL.md` on `main`. Fallback if the classifier still vetoes a specific write path: commander posts the blocked path + intended edit to the Admiral rather than retrying against main. |
| `follow-up-issue-filing` | Filing one issue at wave-boundary recording the finding and recommended next step. | Pre-cleared: standard fleet issue create/comment allowlist for this repo, labeled `cs-231`. |
| `evidence-push` | Pushing the measurement branch and results/evidence artifacts for inspection. | Pre-cleared: push allowlisted to the measurement branch only. Push to `main` is not cleared under this class — see `variant-B-adoption` fallback. |
| `variant-B-adoption` (merge to main) | Merging any change to the Curator skill's threshold paragraph into `main`. | Not pre-cleared. Fallback: commander does not attempt it; floats verdict + evidence + reproduction steps to the Admiral as a `user-decision`. If the commander attempts it anyway and the classifier vetoes, treat the veto as correct behavior, not a blocked-return incident. |

**Expiry:** this contract lapses at the CS-231 wave-1 boundary (commander's findings report) or on any scope change to which corpus/skill file is under measurement — whichever comes first. A stale contract triggers a contract-refresh decision, not continued sailing.
```

The load-bearing behavior — *does the Permission Prerequisites table pre-clear, at contract time,
the harness invocation and the corpus-surgery edits the commander's core loop depends on?* — is
**yes**. Both are first-class pre-cleared rows: `harness-execution` (an allowlisted measure-only
harness invocation, repeated across trials) and `corpus-fixture-surgery` (writing variant B into the
threshold paragraph and mutating the fixtures the harness scores, scoped to a measurement branch so
the live corpus on `main` is untouched). The obvious periphery (push / issue / merge) is still
handled, but the core mechanics are no longer left for the auto-mode classifier to veto after
dispatch. This is exactly the graduated behavior, and it directly forecloses #145.

## What the drill proves

The differentiator between reproduction and non-reproduction is exactly the doctrine text under test
— the "Eval and measurement missions: pre-clear the mission's own mechanics at contract time."
paragraph. Same epic, same auto-mode dispatch, same latent harness + corpus-surgery mechanics; the
**only** change is whether the author's Latitude doctrine tells them to pre-clear an eval/measurement
mission's own core mechanics.

- **Without** it, the author handles the *obvious* external actions (push, issue, merge) and even
  notices "experiment execution" as a decision class, but never carries the harness invocation or
  the corpus edits into the Permission Prerequisites table — so the auto-mode classifier vetoes the
  commander's core loop at execute time. This is the #145 recurrence on demand.
- **With** it, the author pre-clears the harness invocation and the sanctioned corpus-surgery edits
  at contract time, and the core loop survives the classifier.

This is the process-documentation analogue of a passing regression test for the doctrine edit: the
edit is load-bearing, not decorative.

## Method notes (for the corpus)

- **Arm method:** genuinely fresh throwaway subagents (model **sonnet**), one per arm, run with no
  tools and no repo access — each a cold, uncontaminated reader armed only with its arm's "##
  Latitude (first bookend)" doctrine text, the shared (neutral) Permission Prerequisites template
  section, and the shared scenario. Nested spawning was **not** blocked in this harness, so the
  preferred method was used (not the cold-read fallback). Both before-arm and after-arm outputs above
  are captured **verbatim**. Auditor **auditor-g2** did not author the doctrine edit and is a
  different agent from the G1 auditor.
- **Decontamination — the load-bearing method choice.** The **first attempt was discarded as
  contaminated** and is *not* the evidence above. That first scenario framed the deliverable
  procedurally — "the corpus's N-of-M skill-eval pass rates under baseline versus variant B, per
  scenario, with the corpus fingerprint for each arm" — and added "standing facts" that named the
  harness ("runs the scenario set N-of-M") and the measured tree ("the skill source tree it measures
  against"). That itemized the mission's pipeline for the author. Under it, **even the before-arm
  pre-cleared** a "Harness execution" row and a "Variant-B materialization" (corpus-write) row — the
  mechanics were salient enough that the weak-doctrine arm enumerated them anyway, removing the very
  variable under test (the same failure mode the G1 auditor hit in its Attempts 1–2). The
  **decontaminated** scenario (the evidence above) states the mission **by outcome only** — "a
  measured, defensible answer… numbers I can trust… someone else could re-run it" — names neither the
  harness nor the fixtures, and leaves only the standard merge / push / issue trio visible as
  "external actions." With the mechanics latent, the before-arm pre-cleared only that trio and
  omitted the core loop (reproduction), while the after-arm, cued by its doctrine, pre-cleared the
  harness invocation and corpus surgery (no fire). The doctrine's eval/measurement clause is the only
  thing that makes the author go looking for its own mission's mechanics.
- **Minor grounding note (not load-bearing).** The after-arm named the harness `curate_corpus.py`
  (measure-only) rather than the repo's actual skill-eval runner `scripts/run_skill_eval.py`. Given
  the human's ask centered on the "corpus-health threshold paragraph," that is a reasonable cold
  guess; the drill's load-bearing question is only *whether a harness invocation is pre-cleared at
  all*, which it is. A legibility note, not a reproduction.
- **Honest-null was on the table.** Had the before-arm pre-cleared the harness invocation and the
  corpus-surgery edits anyway (without the eval-specific doctrine), that would have been a complete
  honest-null finding — the positive framing alone would have sufficed and the graduated paragraph
  would be belt-and-suspenders. Under the decontaminated scenario it did not: it left both core
  mechanics unlisted, reproducing #145. **fail-pre / pass-post held.**
```