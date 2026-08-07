# Implementation Result — g5-implement (issue #102, Moves 6 & 7)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g5-implement` — two orchestrator-tier doctrines reconcile-then-cut into `skills/_shared/global-orchestrator.md`, each its own canonical subsection with role-specific tails left at the carriers.

## Completed slice
Both moves complete. Two new canonical subsections in `global-orchestrator.md`; commander + admiral SKILL.md reduced to slug-cited pointer + genuine role tail for BOTH moves; fleet-doctrine reduced to its epic-specific bite + pointer for Move 7. Suite green.

## Per-move disposition

### Move 6 — unchanged-tree shortcut
- **Canonical** added to `global-orchestrator.md` as `## Unchanged-tree shortcut` (the shared evidence contract: HEAD-hash match AND clean `git status --porcelain` AND pasted prior green output; any tree change voids it; doctrine/evidence-shape only, no engine change).
- **commander/SKILL.md** reduced to pointer (`§unchanged-tree-shortcut`) + its genuine tail: "does not change what an engine `command` postcondition executes on `advance`… governs only the manual Commander-facing re-verification."
- **admiral/SKILL.md** reduced to pointer (`§unchanged-tree-shortcut`) + its genuine wave-batching tail: "batch the merges and re-verify once, on the final merged main, in a fresh worktree, rather than per-PR."
- Bold headings on the carriers were renamed off the signature phrase ("Re-verification, unchanged tree." / "Batched re-verification.") so the moved phrase no longer appears as a heading in the carrier — the g4 slug-not-title lesson.

### Move 7 — crew-idle / idle-subagent adjudication
- **Canonical** added to `global-orchestrator.md` as `## Idle subagent adjudication` (idle+COMPLETE artifacts = *done*; judge from the artifact set, never the idle signal; complete → integrate as if verdict arrived, silence+incomplete → stalled; judges the verdict not liveness — confirm dead before reuse/sweep/continuation).
- **commander/SKILL.md** reduced to pointer (`§idle-subagent-adjudication`) + Implementer/Reviewer-at-`gN-integrate` framing.
- **admiral/SKILL.md** reduced to pointer (`§idle-subagent-adjudication`) + Commander-at-recovery framing and the **clean-room reviewer subagent** verification method; still points to fleet-doctrine for the epic delta.
- **admiral/references/fleet-doctrine.md** "Adjudication invariants" bullet reduced to ONLY its epic-specific bite (Admiral-error bite-list framing: "when a dispatched commander returns idle with no verdict, verify from the artifact set + clean-room reviewer subagent, accept on that basis rather than hanging") + a pointer to `global-orchestrator.md (§idle-subagent-adjudication)`. The full shared rule is no longer restated there.

## Scope
**Files changed:**
- `skills/_shared/global-orchestrator.md` (append two canonical subsections)
- `skills/commander/SKILL.md` (two carrier passages → pointer + tail)
- `skills/admiral/SKILL.md` (two carrier passages → pointer + tail)
- `skills/admiral/references/fleet-doctrine.md` (one bullet → epic delta + pointer)

**Specific exclusions touched:** no — only the unchanged-tree and crew-idle passages were edited; move-4/5/8 passages and other gates' doctrine (delegate-not-replacement, world-verification, sibling-ids, design-it-twice) untouched.

## Behavior changed
No — doctrine-text relocation only. No engine, script, or test behavior changed.

## Map Impact
- **Structural anchors touched:** `global-orchestrator.md` (+2 canonical subsections), `commander/SKILL.md`, `admiral/SKILL.md`, `admiral/references/fleet-doctrine.md` — all reduced at the moved passages.
- **Constraints/assumptions touched:** relies on the install-time bundling constraint that `global-orchestrator.md` reaches only the orchestrator tier (commander, admiral, charter) — verified against `tests/test_install_constellation.py::test_global_doctrine_buckets_bundled_per_audience`. Both carriers are orchestrator-tier, so both still load the moved rules via their bundled `references/global-orchestrator.md`.
- **Decision candidates / resolved decisions:** destination ruled (global-orchestrator) by handoff; canonical wording/tails/pointer phrasing authored here.
- **Claims/evidence produced:** carrier-count for both moved phrases now 0 in the carriers; canonical present in global-orchestrator; suite green (see Evidence).

## Two before/after grep pairs

### Move 6 (unchanged-tree)
BEFORE (carriers):
```
$ grep -rn "Unchanged-tree shortcut" skills/commander/SKILL.md skills/admiral/SKILL.md
skills/commander/SKILL.md:54:**Unchanged-tree shortcut.** When the manual re-verification suite this bullet calls for ...
skills/admiral/SKILL.md:61:**Unchanged-tree shortcut.** Re-running the full suite once per merged PR is often redundant ...
```
AFTER:
```
$ grep -rn "Unchanged-tree shortcut" skills/commander/SKILL.md skills/admiral/SKILL.md
        (no matches — carrier count 0)
$ grep -rn "Unchanged-tree shortcut" skills/_shared/global-orchestrator.md
skills/_shared/global-orchestrator.md:89:## Unchanged-tree shortcut
```

### Move 7 (crew-idle)
BEFORE (carriers):
```
$ grep -rn "idle_notification\|Crew idle" skills/commander/SKILL.md skills/admiral/SKILL.md skills/admiral/references/fleet-doctrine.md
skills/commander/SKILL.md:56:**Crew idle, no verdict.** ... (`idle_notification`, `idleReason: available`) ...
skills/admiral/SKILL.md:44:- A Commander that dies or stalls: ... An **idle** commander (`idle_notification`, `idleReason: available`) ...
skills/admiral/references/fleet-doctrine.md:156:- **Verify an idle commander from artifacts...** ... only an `idle_notification` (`idleReason: available`) ...
```
AFTER:
```
$ grep -rn "idle_notification\|Crew idle" skills/commander/SKILL.md skills/admiral/SKILL.md skills/admiral/references/fleet-doctrine.md
        (no matches — carrier count 0)
$ grep -rn "idle_notification\|idle subagent" skills/_shared/global-orchestrator.md
skills/_shared/global-orchestrator.md:100:An idle subagent (`idle_notification`, `idleReason: available`) that has produced COMPLETE artifacts is
```

## Canonical + pointer quotes

### Move 6
- Canonical (`global-orchestrator.md` §Unchanged-tree shortcut): "A redundant manual re-verification may be skipped ONLY when the working tree is provably identical to the last green run: `git rev-parse HEAD` matches the hash recorded with that green run, AND `git status --porcelain` is empty, AND the prior green output is pasted alongside the matched hash. Any tree change … voids the shortcut and forces a fresh run. This is doctrine and evidence shape only; no engine or script change."
- commander pointer+tail: "**Re-verification, unchanged tree.** The manual re-verification this bullet calls for may be skipped when the tree is provably unchanged since the last green run — the shared evidence contract in `references/global-orchestrator.md` (§unchanged-tree-shortcut). This does not change what an engine `command` postcondition executes on `advance`… never the engine's own check execution."
- admiral pointer+tail: "**Batched re-verification.** Re-running the full suite once per merged PR is often redundant … batch the merges and re-verify once, on the final merged main, in a fresh worktree, rather than per-PR. The skip is governed by the shared unchanged-tree evidence contract in `references/global-orchestrator.md` (§unchanged-tree-shortcut)."

### Move 7
- Canonical (`global-orchestrator.md` §Idle subagent adjudication): "An idle subagent (`idle_notification`, `idleReason: available`) that has produced COMPLETE artifacts is *done*, not stalled. Judge it from the **artifact set** … never from the idle signal alone … This judges the **verdict**, not liveness … confirm it dead before you reuse, sweep, or launch a continuation into its worktree."
- commander pointer+tail: "**Idle crew at `gN-integrate`.** … Adjudicate it per the shared rule in `references/global-orchestrator.md` (§idle-subagent-adjudication): judge the crew from its **artifacts** … The same recipe runs one tier up at the Admiral."
- admiral pointer+tail: "An **idle** commander … *done*, not stalled — adjudicate it per the shared rule in `references/global-orchestrator.md` (§idle-subagent-adjudication): verify from the artifact set … plus a **clean-room reviewer subagent** … Epic-specific adjudication deltas: `references/fleet-doctrine.md`, \"Adjudication invariants\"."
- fleet-doctrine epic delta+pointer: "**Verify an idle commander from artifacts; never block on a dropped verdict.** The general rule … is shared orchestrator doctrine in `global-orchestrator.md` (§idle-subagent-adjudication). The Admiral bite it names: when a dispatched commander returns idle with no verdict, verify from the artifact set … **and a clean-room reviewer subagent** … accept on that basis rather than hanging."

## Test mode
**Required:** evidence-only (inspection-only; keep suite green)
**Satisfied:** yes — full suite green after both moves.

## Evidence
```bash
py -m pytest tests/ -q
```
**Result:** pass — `442 passed, 2 skipped, 26 subtests passed in 11.74s`

Verification-command results:
- `grep -rn "Unchanged-tree shortcut" skills/commander/SKILL.md skills/admiral/SKILL.md` → 0 matches (moved).
- `grep -rn "idle_notification\|Crew idle" skills/commander/SKILL.md skills/admiral/SKILL.md skills/admiral/references/fleet-doctrine.md` → 0 matches (moved).
- `grep -c "Unchanged-tree\|idle_notification\|idle subagent" skills/_shared/global-orchestrator.md` → 2.
- `ls skills/_shared/global-*.md` → global-crew.md, global-everyone.md, global-orchestrator.md (no new global-*.md filename).

## TDD evidence, if required
n/a — inspection-only test mode.

## Docs/contracts touched
- The four listed skill/doctrine files. No template or engine-config changes.

## Assumptions
- Pointer path from the carriers is `references/global-orchestrator.md` (commander/admiral) and, from within `admiral/references/fleet-doctrine.md`, the sibling `global-orchestrator.md` — both resolve because install bundles `global-orchestrator.md` into every orchestrator-tier `references/` dir (test_install_constellation.py). The `_shared/` source dir is never a runtime lookup path.
- Slug citations use the `§<kebab-heading>` form; no existing repo convention forced a different slug spelling, so I matched the kebab-case of the destination headings (`§unchanged-tree-shortcut`, `§idle-subagent-adjudication`).
- Carrier bold-heading rename (off the signature phrase) is the intended reading of the g4 "cite by slug, not section-title" lesson: keep the moved phrase out of the carrier entirely, heading included, so the before/after carrier-count grep goes cleanly to 0.

## Stop conditions hit
- none — neither rule entangled with another gate's doctrine, and fleet-doctrine's epic delta (the Admiral-error bite-list bite) separated cleanly from the shared rule. The admiral "dies or stalls / inspect worktree" recovery doctrine sits in the same bullet as the idle-adjudication passage; I edited only the idle sentences and left the recovery doctrine intact (in-scope: it is part of the crew-idle passage's host bullet, not a separate gate).

## Out-of-scope observations
- The admiral idle-commander pointer and the fleet-doctrine bite now BOTH name the "clean-room reviewer subagent" method. That is intentional (admiral SKILL is the operating surface; fleet-doctrine is the epic bite-list) but is a mild redundancy a future consolidation pass could collapse if the bite-list is ever folded into SKILL.md. Flag for Cartographer/triage only if the duplication grows.
- `docs/agents/engine-config.json` (the `config_ref` in the plan template and the g4 plan) does not exist in this skill-source repo; the engine tolerates its absence for a `gated` plan. Noted for workflow feedback below, not a blocker.

## Workflow Feedback
- **Handoff gaps:** none blocking — the handoff was complete and unusually precise (per-move carriers with line numbers, explicit tail assignments, the g4 slug lesson called out). The one micro-ambiguity: the handoff says "cite pointers by slug, not section-title, when the moved phrase equals the heading" but does not state the slug *spelling convention* (`§kebab` vs `"Section Title"` vs anchor link). I chose `§kebab-heading`; if the repo has a house style a future handoff could name it.
- **Context rediscovered:** the pointer-path resolution (that carriers reference `references/global-orchestrator.md` and fleet-doctrine references sibling `global-orchestrator.md`, both populated at install) had to be reconstructed from `test_install_constellation.py`. A one-line Map Anchor stating "orchestrator-tier references/ is install-populated from _shared/; cite the sibling path, not `_shared/`" would have saved that dig.
- **Instructions improvised around:** the IMPLEMENTER_PLAN template's `config_ref` points at `docs/agents/engine-config.json`, which is absent in this repo. I kept the template's value (matching the g4 sibling plan); the engine ran the `command` postconditions fine without it. No action needed, but the template default assumes a consuming repo, not the skill-source repo.
- **What would have made this easier:** add the install-time pointer-path convention (sibling `global-orchestrator.md`, not `_shared/…`) to the inbound Map Anchors for any "move doctrine into a global-* bucket" gate — it is the one non-obvious fact every such move needs.

## Return status
`complete`
