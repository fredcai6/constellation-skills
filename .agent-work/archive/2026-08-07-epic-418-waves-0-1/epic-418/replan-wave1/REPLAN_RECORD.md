## Wave decision
**replan** (applicable: false)

## Criteria assessment
- Wave exit: Wave 1 has not reached its exit. Both launched issues are open and mid-run: #440 is at its second gate with a live two-arm harness executing, #447 is at its second gate with the g1 guard shipped and independently falsified. Neither exit criterion is met or refuted yet, so this pass revises unlaunched truth only and leaves the wave running.
- Epic done: The epic is not complete, and one of its five done-conditions is not merely unmet but falsified by the epic's own execution. Three mechanism conditions are on track: the governor trips live (#419) though not yet in the right tree (#440), the engine channel is fixed and its render targets proved real (#420), and the named invariants refuse instead of hoping (#422). The MCP-door condition is untouched and deferred. The backlog condition has moved backwards.
- Good enough: The mandatory quality boundary held and did real work this wave. #419's cold critic measured that every machine-checkable postcondition was already green at HEAD before any code was written, and #440's harness carries an explicit positive-control requirement precisely because a quiet control would be indistinguishable from a reproduced bug. Scope discipline was applied as breadth-narrowing without weakening evidence.

## Discrepancy dispositions
- D1: **repair_current_wave** — Already the current wave's repair: #440 is launched, open, and mid-gate. No new work is created; the wave continues as launched.
- D2: **revise_plan** — The fourth done-condition is falsified by measurement, not merely behind: 117 open at the epic's start, 138 now, roughly twenty findings filed against four closed. Because definition_of_done is a fixed boundary, this pass proposes rather than applies the revision, and escalates to Tommy. The proposed re-cut converts an absolute count target into a directional one plus a separate consolidation epic.
- D3: **revise_plan** — C #421's forecast entry described corpus shrinkage; C is now the mechanism that carries per-step spine instructions and the route for #432's fix. The forecast entry is rewritten to say what C is actually for, so a future wave does not launch it against a stale rationale. #421 already exists; nothing new is filed.
- D4: **revise_plan** — The multi-spine attribution failure is a distinct defect from #440's single-spine worktree case and is covered by no launched issue, so the governor's done-condition is not reachable by #440 alone. Recorded in the revised uncertainty register with a named probe. A tracker issue should be filed for it; this offline pass creates none.
- D5: **record_evidence_only** — The disposition it would have driven was already taken: #285 is held open and routed to #447. Recording the disproof is the entire action, and it matters because the false rationale nearly closed a live issue.
- D6: **amend_forecast_or_parked** — The archive-gate defect bites at closeout, not at the wave-1 boundary, so it is added to the forecast as an entry condition on this epic's own closing rather than pulled into the current wave. #439 and #446 already carry it.

## Unlaunched dispositions
- 421: **keep** — Deferred by ruling, not cancelled, and its rationale is corrected in the revised forecast rather than in the issue identity. Still blocked on the governor landing in the right tree.
- 423: **rewrite** — E's scope has materially shrunk since it was cut. Its batch-confirm half is executed (#131, #289, #298, #322 closed with evidence; #285 held and routed to #447) and its labelling half is largely done — 13 theme labels exist and cover about 98 of 138 open issues, against a state note that recorded none existing at all. What remains is a 40-issue sweep, not a taxonomy build.
- 424: **keep** — Deferred by ruling; still needs A, B and C. Its entry condition is unchanged and its forecast entry is retained verbatim.
- 427: **keep** — Engine refusals counter records zero when a refusal precedes the lease claim — a real instrumentation gap, unclaimed and correctly outside this wave.
- 428: **keep** — verify_spec_confirmed --phase review refuses every template-conformant draft by construction: a check that cannot pass, the mirror of a check that cannot fail.
- 429: **keep** — Needs re-verification, not just keeping: file_issue_set.py was substantially rewritten by the iterative-planning change that merged today, so the WinError 206 over-32K --body path may already be gone or may have moved. Re-run the reproduction before scheduling work.
- 430: **keep** — spine_rail binding accepts an unexpanded shell-variable junk key and a stale lease can shadow the live one. Sits inside #440's file fence; check for overlap when #440 returns rather than launching it separately.
- 431: **keep** — A HARD trip blocks advance, which freezes the DIGEST the trip's own forced handoff depends on — a deadlock in the mechanism #419 and #440 are building. Should be considered for the wave that closes the governor.
- 432: **keep** — A dispatched role can skip the engine entirely and its return still reads as a clean success. Routed into F #424 by ruling, with C #421 as the mechanism; kept as the tracking identity for that route.
- 433: **keep** — Render directives in current — the same unrendered-defect class #420 fixed for anchors and constraints. Cheap, and its sibling is already proved real.
- 436: **keep** — Confirm the worktree-precondition enumeration check catches a real second worktree-entering template — the falsification pass #422's wiring did not get.
- 437: **keep** — Stale comment in _next_verbs, outdated post-#328. Mechanical, no decision needed.
- 439: **keep** — COMMANDER_SPINE archive.c2b's <branch> placeholder is never resolved, so the check always fails. Paired with #446 in the revised forecast.
- 441: **keep** — Binding store durability: no lock, no reaper, unvalidated paths, divergent agent_id rules. The substrate under #440; likely to grow once #440's evidence lands.
- 442: **keep** — The engine's rail and HARD refusal read badly to the agent they are aimed at — a message-quality defect in the exact channel #420 just fixed structurally.
- 443: **keep** — docs/agents/engine-config.json does not exist but every config_ref points at it: a dangling reference asserted repeatedly, the same shape as the seven-site claim #419 hit.
- 444: **keep** — Nothing links the gauge record's field count across its seven assertion sites — the mechanical link that would have closed #419's blast-radius problem.
- 446: **keep** — The archive gate accepts only an OPEN PR, so a well-run epic forces --force on its success path. Promoted into the revised forecast because this epic will hit it at closeout.
- 448: **keep** — Closeout debt: the resolved-load-manifest finding is unowned and recorded only in a closed run's artifacts. Filed by E; ownership still open.
- 449: **keep** — Closeout debt: #298's item J was never done — #308 substituted a migration for it. Filed by E.
- 450: **keep** — Closeout debt: the B1 first consolidation was never run and is now homeless across two epics. Filed by E; a natural member of the proposed consolidation epic.
- 451: **keep** — Closeout debt: 23 of 32 episodes carry unpaid signal and 7 were ever harvested — the store has no scheduled consumer. Directly relevant to #447, which is retiring the two ledgers into that store; #447 should be told this consumer gap exists.
- F-relocate: **rewrite** — The entry described C as corpus shrinkage. C is now the delivery mechanism for per-step spine instructions and the route for #432's fix, and its entry conditions need the governor landing in the right tree plus an actual token measurement rather than an assumed shrinkage.
- F-mcp-door: **keep** — Unchanged: still gated on per-step spine instructions existing, still deferred by ruling.
- U-backlog-converges: **rewrite** — The unknown is no longer whether consolidation converges but whether it can converge inside an epic that is simultaneously generating findings — and it now has a measured answer pointing at no, which is what forces the escalation.
- U-multi-spine-attribution: **keep** — The unknown as stated is exactly right and its evidence has strengthened rather than changed shape: the Admiral has now gone a full run with no reading. Kept verbatim; the probe stands.
- P-vision: **keep** — Ruled out of this design by Tommy; parked, not dropped.
- P-metrics: **keep** — Ruled out of this design by Tommy; parked, not dropped.
- P-simplified-english: **keep** — Tommy's to run elsewhere; parked, not dropped.

## Wave review — epic #418, wave 0 closed, wave 1 in flight

**Wave 0 landed four of four.** #419 governor per-agent identity (a HARD trip fired live on a dispatched subagent and the engine refused its advance), #420 engine output channel (and `anchors`/`constraints` proved not vestigial against 20-plus archived gates, so C's relocation targets demonstrably exist), #422 wired invariants (deliberate-breakage test passes), #425 defect filing (nine tracker references, no code change — correctly a null).

**Wave 1 is running and this pass does not touch it.** #440 and #447 are both mid-gate and are preserved exactly as launched.

**Exit chosen: `replan`.** Not `advance`, because wave 1 has not reached its exit. Not `repair`, because nothing blocks wave 1's exit that is not already inside it. Not `stop`. The revision is entirely to unlaunched truth.

**One escalation, and it is the headline.** The epic's fourth done-condition — that the backlog ends short enough for one issue-list sweep — is not behind schedule, it is falsified by the epic's own execution. The epic opened against 117 open issues; there are 138 now, 40 of them unlabelled. Roughly twenty findings were filed by this epic against four issues closed under E's batch confirm. Doing the mechanisms work correctly *generates* findings, so the count moves the wrong way precisely when the epic is going well. `definition_of_done` is a fixed boundary, so this pass proposes and does not apply: the recommendation is to narrow the condition to classification progress (which is real — 13 theme labels now cover about 98 of 138 issues) and cut consolidation-to-a-count as its own epic.

**Three corrections to the record.** The state note says no theme labels exist; 13 do, applied to most open issues. #285's proposed close rationale — that #308 deleted the playbook wholesale — is false, measured at `cbd9aee`. And the Context Governor has no `PostToolUse` entry in the user-scope `settings.json` at all, so every governor observation outside a purpose-built harness is currently vacuous.

**One new defect class, uncovered by no launched issue.** A session bound to several candidate spines gets no reading at all — the writer hook refuses to guess and writes nothing. This epic's own Admiral has run for over a day with the gauge silent. #440's scope is the single-spine worktree case and will not reach it, so the governor's done-condition is not reachable by #440 alone.

## Current planning truth — epic #418

### What is done
Wave 0, four of four, all merged and green: per-agent governor identity with a live HARD trip (#419), the engine output channel with `anchors` and `constraints` rendering (#420), the wired worktree-isolation and `record()` invariants (#422), and the explorer run's defects filed (#425).

### What is running
Wave 1, launched and preserved exactly: #440 (a worktree-dispatched agent's reading must land in the tree it is working in) and #447 (episodes replace both shared ledgers, behind a guard proven to fail on purpose). Neither has reached its exit.

### What is deferred, and why
#421 stays deferred but its rationale has changed: it is no longer corpus shrinkage, it is the mechanism that carries per-step spine instructions and the route for #432's fix. #424 stays deferred and still needs A, B and C. #423 shrinks to a 40-issue label sweep, because the taxonomy it was going to build already exists and already covers about 98 of 138 open issues.

### Nonbinding forecast
Relocate gate instructions into the spine as an instruction-delivery mechanism, entered on the governor landing in the right tree plus a real token measurement. Then the MCP door. Separately: repair the archive gate before this epic's own closeout hits it, and cut backlog consolidation as its own epic.

### Open uncertainty
Whether consolidation can converge inside an epic that generates findings — measured today at 138 open against 117 at the start, which is what forces the escalation below. Whether a reading can be attributed when a session is bound to several candidate spines; #440 will not reach this case. Whether the governor is wired at all outside a purpose-built harness — today the installer reports no `PostToolUse` entry in the user-scope settings.

### Awaiting a human decision
The fourth done-condition is falsified by the epic's own correct execution. Narrowing it, and moving the count target to a dedicated consolidation epic, is proposed but not applied. Tommy decides.

