# x2 — Corpus Survey: where the constellation skills corpus is heavy, layered, duplicated, or mis-tailored

Scope: `C:\Programs\constellation-skills\skills\` — 14 skills + `_shared`. Read-only measurement. No redesigns proposed.

## Summary

- The corpus is **bimodal**: three heavy SKILL.md files (commander 113 lines / 2580 words, explorer 99 / 1695, docent 152 / 1110) carry most of the prose; the other 11 are 24–72 lines. Weight concentrates in orchestrator-tier skills that run in the human's/Admiral's context.
- **`_shared/` is real but under-used.** Global doctrine (`global-everyone/orchestrator/crew`, `design-it-twice-brief`, `windows`) is factored out, yet several doctrines that *should* live there are still copy-pasted into individual SKILL.md files.
- The single biggest duplication is the **"Mandatory, no exceptions … reporting misfit is compliance, not deviation"** boilerplate — near-identical in **10** SKILL.md files, with only a per-role tail ("at closeout" / "in your workflow feedback" / "at the feedback step").
- **`FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY`** appears in 6 files; **engine-invocation boilerplate** ("drive … through the absolute path to this installed skill's bundled `scripts/checklist_engine.py`, workbench `references/checklist-engine.md`") is restated in ~10 files with wording drift.
- **Commander and Admiral show the clearest lesson-patch layering**: bolted-on edge-case paragraphs (Unchanged-tree shortcut, Crew idle/no-verdict, Crew backend CLI-vs-Agent-tool) that read as incident write-ups, several cross-referencing each other ("mirrors the admiral's … one tier down"). 96 commits touched a `SKILL.md` in 60 days.
- **Scripts are not in the source skill dirs** — they live once in top-level `scripts/` and are bundled per-skill at install. So "scripts n/size" is 0 everywhere in source; heaviness there is an install-time concern, not a source one.
- **Mis-tailoring flags:** `interrogator` prose reads human-facing ("Interview the user relentlessly") but it is mostly loaded as a subskill by orchestrators; `manifest.json` lists only 11 of 14 skills (explorer, prototyper, docent missing).

## Per-skill table

Scripts column omitted from per-skill measurement: **no skill has a `skills/*/scripts/` dir in source** — all 18 scripts live in top-level `scripts/` and are bundled at install. templates/references counts are source-tree file counts (`du -sk`).

| skill | SKILL.md lines/words | templates n/size | references n/size | invoker class | notes |
|---|---|---|---|---|---|
| admiral | 63 / 1495 | 4 / 24K | 1 / 12K (fleet-doctrine 1679w) | **human** (hands an epic) | Heavy inline "Operating doctrine" bullet list; 2 bolted edge-case paras (idle-commander, Unchanged-tree shortcut). |
| cartographer | 27 / 365 | 5 / 24K (map-model.md 2388w = largest ref in corpus) | 1 / 20K | **both** — human curation OR Commander `reconcile` subagent | Lean SKILL; nearly all detail pushed to `references/map-model.md`. Good factoring. |
| charter | 33 / 354 | 10 / 47K | 4 / 36K (scenario-bank 1248w, rubric 728w, interrogation-protocol 667w) | **human** (repo setup) | Heaviest template+reference payload of any skill (10 templates). "FOLLOW THIS SKILL STRICTLY" appears twice (lines 8-area mandatory + line 31). Typo "managemetn"→ actually that's workbench. |
| commander | **113 / 2580** (largest SKILL.md) | 6 / 60K (IMPLEMENTER_HANDOFF 634w, REVIEWER_HANDOFF 632w) | 0 | **both** — human OR Admiral `LAUNCH_ORDER` (explicit delegated mode) | The layering epicenter — see Layering findings. No references/ dir despite being the densest doctrine; everything inline. |
| docent | **152 / 1110** (most lines) | 0 | 0 | **human** (on-demand explainer generation) | All detail inline because it is "a method, not a program"; coherent, not patchy, but long. Self-contained-HTML constraints repeat frontend guidance that could be shared. |
| explorer | 99 / 1695 | 7 / 40K (EXCURSION_BRIEF 572w, DESIGN_SPEC 505w) | 0 | **human ONLY** (explicit: "requires a reachable human by construction … no delegated mode") | Cleanest heavy skill: "Headline doctrine" section is deliberate, not accreted. Scoped-nulls + design-it-twice doctrine duplicated with prototyper / global-orchestrator. |
| implementer | 24 / 322 | 2 / 12K (IMPLEMENTER_RESULT 426w) | 0 | **agent** (dispatched from `IMPLEMENTER_HANDOFF`) | Lean. Carries mandatory-boilerplate + "FOLLOW THIS SKILL STRICTLY" + full engine-invocation string. |
| interrogator | 28 / 490 | 1 / 4K | 0 | **both / mis-tailored** — loaded by Commander/Admiral as subskill; prose reads human-facing | See mis-tailoring flag. Delegated-context paragraph bolted on to reconcile the two audiences. |
| lessons-auditor | 72 / 979 | 3 / 20K (LESSONS 664w in workbench, not here) | 0 | **agent** (subagent at Admiral closeout / Commander feedback) | Dense but purposeful (rules of evidence, form-selection ladder, reproduction drills). "Dedup sibling ids" doctrine duplicated with admiral closeout step 4. |
| prototyper | 64 / 893 | 2 / 8K | 3 / 12K (logic/ui/measurement) | **both** — explorer excursion / Commander / standalone human | Scoped-nulls doctrine (whole section) near-duplicates explorer headline #2. |
| reviewer | 26 / 446 | 2 / 12K (REVIEW_RESULT 387w) | 0 | **agent** (dispatched from `REVIEWER_HANDOFF`) | "Verify every claimed side-effect against the world" para closely parallels commander gN-integrate verification prose. |
| scout | 36 / 384 | 2 / 12K | 1 / 4K (scout-heuristics 520w) | **both** — human/Commander cadence | Lean; audit-for lists could arguably live in scout-heuristics.md. |
| triage | 43 / 526 | 1 / 4K | 0 | **both** — Commander `triage` step OR user | "No checklist" outlier. Fix-Now ladder is self-contained doctrine. |
| workbench | 45 / 335 | 6 / 32K | 2 / 24K (checklist-engine 1915w — the shared engine ref) | **infra / agent** (substrate loaded by every role) | Owns the shared engine reference every other skill points at. Typo "managemetn" (line 8). |
| _shared (no SKILL.md) | — | — | 5 files: global-orchestrator 883w, global-everyone 781w, design-it-twice-brief 691w, windows 458w, global-crew 342w | bundled into every skill at install | The intended home for cross-skill doctrine; several doctrines that belong here are still inlined in skills. |

## Layering findings (cited)

Ordered by strength of "accreted lesson-patch" signal.

1. **commander/SKILL.md:56 — "Unchanged-tree shortcut."** A dense edge-case paragraph about when a manual re-verification re-run may be skipped (HEAD hash + `git status --porcelain` empty + pasted prior output). Reads as an incident-hardening patch bolted onto "Executing a gate." Near-identical twin at **admiral/SKILL.md:61** ("Unchanged-tree shortcut") one tier up — same evidence contract restated for the epic level. Strong duplication + layering.

2. **commander/SKILL.md:58 — "Crew idle, no verdict."** A paragraph teaching that an `idle_notification`/`idleReason: available` subagent with complete artifacts is *done*. It explicitly says it "mirrors the admiral's commander-idle adjudication in `skills/admiral/SKILL.md` and `skills/admiral/references/fleet-doctrine.md`'s 'Adjudication invariants' section — the same recipe, one tier down." Self-admitted duplication across three locations (commander SKILL, admiral SKILL:44, fleet-doctrine).

3. **commander/SKILL.md:68 — "Crew backend (CLI vs Agent-tool harness)."** The single longest paragraph in the corpus (~250 words): a highly specific operational patch about `--dispatch external`/`--backend external`/`--verify-result`, `SendMessage` resume, `recover_crews.py` state vocabulary. Points at an external spec doc and `windows.md §2`. Classic accreted-mechanism layering — reads as harness-specific lore that outgrew the SKILL.

4. **admiral/SKILL.md:36–47 — "Operating doctrine, learned from field fleets."** A 12-bullet list, several bullets self-labeled as imported lessons ("Surviving long detached compute is platform doctrine, not project lore", "State-note-first is now engine-enforced"). The section header itself ("learned from field fleets") announces accretion. Some bullets point to `references/fleet-doctrine.md` (good), others restate it inline.

5. **commander/SKILL.md:105 — gate-sequencing "plan smell" paragraph** and **:99 design-it-twice/cold-critic paragraph**: both are doctrine restatements that also live in `_shared/global-orchestrator.md` and `_shared/design-it-twice-brief.md`; the SKILL even says "Both point at doctrine — the rules live there, not here," yet still restates a paragraph of them. Git log confirms these arrived as discrete lesson PRs (`2c84955 docs(commander): gate-sequencing keeps suite green`; `467542b docs(doctrine): critical spec review as a shared orchestrator standard`).

6. **interrogator/SKILL.md:16 — "Delegated context (no reachable human)."** A bolted-on reconciliation paragraph explaining that the human-facing prose above it ("Interview the user relentlessly", "wait for the answer") should be re-read for the delegated case. The need for this patch is itself the mis-tailoring signal (see below).

7. **charter/SKILL.md** — "FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY" appears **twice** (once as the mandatory block at line 10, again standalone at line 31), a redundant emphatic warning bracketing the "Compile" section.

8. **cartographer/SKILL.md:14** and **:22-25** — the docent-staleness soft-pointer and the Scout-disposition handling read as later inserts into an otherwise tight ownership statement, but they are cleanly scoped; lower-confidence layering call.

## Duplication findings (cited)

1. **Mandatory-compliance boilerplate — 10 files.** `grep "reporting misfit is compliance, not deviation"` hits: admiral, cartographer, charter, commander, implementer, interrogator, lessons-auditor, reviewer, scout, workbench SKILL.md. The stem ("Mandatory, no exceptions … within a step judgment is yours … do the closest compliant thing and report the misfit … reporting misfit is compliance, not deviation") is identical; only the tail location varies ("at closeout" / "in your workflow feedback" / "at the feedback step" / bare). Prime candidate to live once in `_shared/global-everyone.md` with a one-token per-role slot. Not currently in `_shared`.

2. **Engine-invocation string — ~10 files.** The phrase "drive … as a `gated`/`survey` … through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`)" recurs with wording drift across charter:12, implementer:14, interrogator:14, reviewer:12, scout:8, cartographer:8, lessons-auditor:14, commander:113, workbench:39. Reviewer:12 even spells it out longhand ("the constellation-workbench skill's bundled `references/checklist-engine.md` under the installed workbench skill directory"). The canonical statement already exists in `workbench/references/checklist-engine.md`; the per-skill restatements are copies.

3. **`FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY` — 6 files** (charter, commander, explorer, implementer, interrogator, reviewer), verbatim, unattached to any skill-specific content.

4. **Scoped-nulls doctrine — 2 near-identical copies.** explorer/SKILL.md:22 (Headline doctrine #2) and prototyper/SKILL.md:25-30 (whole "Scoped nulls" section) teach the same rule ("kills that specific test … never the idea class", "what was NOT tested is mandatory"). The user's own memory (`scoped-nulls-optimistic-persistence.md`) treats this as one doctrine. Not factored into `_shared`.

5. **Design-it-twice doctrine — restated in commander:99 and explorer:64-65** on top of the canonical `_shared/global-orchestrator.md` + `_shared/design-it-twice-brief.md`. Both skills say the rules live in the shared docs, then restate a paragraph anyway. (This is a *deliberate* partial dedup per PR #99/#100 — the shared brief exists — but the SKILL-level paragraphs remain.)

6. **"Delegate is not a replacement / I need my human" — commander:85 and admiral:45.** Same doctrine (asking-up is sanctioned, chain terminates at the human) written twice, once per tier, with parallel phrasing. Matches the user memory `delegate-not-replacement.md`.

7. **Dedup-sibling-ids doctrine — lessons-auditor:22 and admiral:56.** The "same defect under sibling ids across worktrees is a `confirm`/`amend`, never a new `add`" rule is spelled out fully in both places.

8. **World-verification of claimed side-effects — reviewer:18 and commander:54.** "Verify every claimed side-effect against the world, not the report … re-run the command, stat the artifact, check it is fresh" appears in both, tier-appropriate but textually parallel.

9. **Inherited-global-doctrine pointer — charter:29, commander:73, scout:18** each restate "the approach baseline is inherited global doctrine (`references/global-orchestrator.md` + `references/global-everyone.md`); project deltas come from ORCHESTRATOR_CONTEXT." Minor, but three copies of the same pointer sentence.

## Uncertain / not measured

- **Invoker class for `workbench` and `interrogator`** are the least clear. Workbench is really a substrate/library loaded by other roles (I classed it infra/agent); interrogator is dispatched-as-subskill in practice but written human-first (I flagged it mis-tailored/both). Treat both as judgment calls.
- **Whether the duplications are intentional per-context repetition vs. accidental drift.** Some (mandatory boilerplate, engine string) look like they *should* be shared; others (delegate-not-replacement, world-verification) are arguably deliberate tier-local restatements the authors chose for standalone readability. I measured presence, not intent.
- **Template/reference internal duplication not inspected.** I measured template/reference file counts and sizes and grepped signature phrases, but did not diff template *bodies* against each other (e.g. IMPLEMENTER_HANDOFF vs REVIEWER_HANDOFF at 634/632 words are suspiciously equal in size — possible shared boilerplate — not confirmed).
- **`manifest.json` staleness** (lists 11 of 14 skills; explorer/prototyper/docent absent) — flagged as a mis-tailoring/consistency smell; I did not check whether the installer reads manifest.json or the `skills/` dir listing, so impact is unverified.
- **docent's self-contained-HTML constraint block** (SKILL.md:73-87) overlaps conceptually with the platform's frontend/artifact guidance; I did not verify whether a shared reference exists to point at instead.
- **Scripts heaviness** deliberately not measured per-skill (they are not in source skill dirs); if the question cares about *installed* skill size, that requires running the installer, which I did not do (read-only).
