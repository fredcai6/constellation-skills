# Review Result

## Assigned Gate
`g5-review` (issue #102, Moves 6 & 7 — two orchestrator-tier doctrines into `skills/_shared/global-orchestrator.md`)

## Result
`APPROVE`

## Handoff compliance
Both moves landed exactly as the handoff specified. Two new canonical subsections were appended to `global-orchestrator.md` (`## Unchanged-tree shortcut`, `## Idle subagent adjudication`); commander + admiral SKILL.md carriers were reduced to slug-cited pointer + genuine role tail for both moves; `admiral/references/fleet-doctrine.md` was reduced to its epic bite + pointer for Move 7. Suite green. Nothing outside the assigned scope changed.

## Scope drift
None. `git status --porcelain` shows exactly the 4 expected files:
- `skills/_shared/global-orchestrator.md` (append-only: +18 lines, two subsections; nothing above line 85 touched)
- `skills/commander/SKILL.md` (2 insertions / 2 deletions — the two carrier paragraphs only)
- `skills/admiral/SKILL.md` (2 insertions / 2 deletions — the idle sentences in the dies-or-stalls bullet + the batched-re-verify paragraph)
- `skills/admiral/references/fleet-doctrine.md` (one bullet → epic bite + pointer)

The `--stat` on commander and admiral is `2 insertions(+), 2 deletions(-)` each, mechanically confirming only the two passages changed and every other passage is byte-identical. Excluded doctrine (delegate-not-replacement, world-verification, sibling-ids, design-it-twice, move-4/5/8 passages) untouched.

## Evidence verdict
Reproduced independently, not accepted from the report:
- `py -m pytest tests/ -q` → **442 passed, 2 skipped, 26 subtests passed** (matches the claimed tail).
- `grep -rn "Unchanged-tree shortcut" skills/commander/SKILL.md skills/admiral/SKILL.md` → 0 matches (carrier count 0).
- `grep -rn "idle_notification\|Crew idle" skills/{commander,admiral}/SKILL.md admiral/references/fleet-doctrine.md` → 0 matches.
- `grep -c "## Unchanged-tree shortcut\|## Idle subagent adjudication" skills/_shared/global-orchestrator.md` → 2 (each canonical reads once).
- `ls skills/_shared/global-*.md` → `global-crew.md, global-everyone.md, global-orchestrator.md` — no new `global-*.md`.
- All three carriers (`commander/SKILL.md`, `admiral/SKILL.md`, `fleet-doctrine.md`) cite `§idle-subagent-adjudication`; both unchanged-tree carriers cite `§unchanged-tree-shortcut`. Slugs are the kebab-case of the canonical headings and resolve consistently.

## Code/doc quality
- **Move 6 meaning preserved.** The canonical carries the full evidence contract: HEAD-hash match AND empty `git status --porcelain` AND pasted prior green output, any tree change voids it, doctrine/evidence-shape only. Commander keeps its genuine tail (the engine `command`-postcondition boundary — postcondition still runs every `advance`; shortcut governs only manual re-verification). Admiral keeps its genuine wave-batching tail (batch merges, re-verify once on final merged main in a fresh worktree). Both are pointers, not restatements.
- **Move 7 meaning preserved.** The canonical carries idle+COMPLETE = *done*; judge from the artifact set never the idle signal; complete → integrate as if the verdict arrived, silence+incomplete → stalled; judges the verdict not liveness; confirm dead before reuse/sweep/continuation. Commander keeps the Implementer/Reviewer-at-`gN-integrate` framing; admiral keeps the Commander-at-recovery framing plus the clean-room reviewer subagent method. Fleet-doctrine keeps ONLY its epic bite (dispatched-commander-returns-idle + clean-room reviewer subagent, accept-not-hang) and explicitly defers the general rule to `global-orchestrator.md (§idle-subagent-adjudication)` — it does not restate the full shared rule.
- **Admiral recovery doctrine intact.** The "A Commander that dies or stalls: inspect its worktree … relaunch a continuation into the same worktree … Log every incident and recovery" doctrine is fully present at admiral/SKILL.md:44; only the idle-adjudication sentences within that bullet were rewritten to a pointer+tail.

## Map impact verdict
- **Evidence supports claimed change:** yes — greps + suite reproduce the carrier-count-0 / canonical-present / green claims.
- **Constraints not violated:** yes — relies on install-time bundling of `global-orchestrator.md` into every orchestrator-tier `references/` dir; both carriers are orchestrator-tier, and `tests/test_install_constellation.py` remains green.
- **Notes match the diff:** yes — the Map Impact notes list exactly the four touched anchors and correctly describe append-only vs reduction edits.
- **Decision candidates surfaced:** n/a — destination was handoff-ruled; wording authored in-gate, no authority beyond the implementer required.
- **Durable context routed:** yes — the one mild-redundancy observation (clean-room reviewer method named in both admiral SKILL and fleet-doctrine) is flagged for triage/Cartographer, not dropped.

## Reconciliation check
Doctrine-text relocation only; no structural, contract, engine, or test-behavior drift. The `_shared → orchestrator-tier references/` consolidation model is preserved. Nothing here forces a Commander reconcile beyond the routine architecture note that global-orchestrator gained two subsections.

## Blockers
- none

## Out-of-scope observations
- The admiral idle pointer and the fleet-doctrine bite both name the "clean-room reviewer subagent" method. Intentional (admiral SKILL is the operating surface; fleet-doctrine is the epic bite-list), but a mild redundancy a future consolidation pass could collapse if the bite-list ever folds into SKILL.md. Triage candidate only — do not act on it now.

## Workflow Feedback
- **Handoff gaps:** none blocking. The handoff was unusually precise — per-move carriers, explicit tail assignments, the recovery-doctrine caveat spelled out, and the exact grep/suite evidence to reproduce. The one micro-gap (also flagged by the implementer): the slug *spelling* convention (`§kebab` vs quoted section-title vs anchor link) was not stated; the implementer chose `§kebab-heading` and it is internally consistent, so no friction in review.
- **Context rediscovered:** none — the implementer result pre-listed every reproduction command, so verification was a straight replay. The pointer-path resolution (carriers cite sibling `references/global-orchestrator.md`, not `_shared/…`, populated at install) was already documented in the implementer's Assumptions; a Map Anchor stating that would spare the next such gate the dig.
- **Instructions improvised around:** the survey `config_ref` points at `docs/agents/engine-config.json`, absent in this skill-source repo; the engine tolerated its absence for a survey plan, so no action needed. Same non-issue the implementer noted.
- **What would have made this easier:** add the install-time pointer-path convention (cite sibling `global-orchestrator.md`, never `_shared/…`) to inbound Map Anchors for any "move doctrine into a global-* bucket" gate — the single non-obvious fact every such move needs.

## Return status
`complete`
