# Ideas Board — `explore-post-phase1`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history; a mid-exploration shelve files *this file* as the shaped-design issue, loudly marked unconfirmed. Keep it current — it is what survives a reopen cascade.

## The point

Phase 1 of a substantial overhaul is done (epic #298 closed 2026-07-31, follow-on issues #299–#310 landed through 2026-08-03). The backlog now holds many issues and episodes of unclear standing — some block the target architecture, many are in-the-weeds artifacts of the old shape. The point of this exploration: (1) **consolidate the open work** down to the actual needed fixes, and (2) **take the next deliberate step toward the target architecture** articulated in the last explorer run (explore-grander-scale). Done feels like: a short, honest backlog where every survivor is tied to the target architecture or a real defect, plus a confirmed next-step design. Kill condition: if review shows the open work is already coherent and the next step is already cut, this exploration is pointless — route to an Admiral instead.

Top concerns (from Tommy, 2026-08-03): too many in-the-weeds issues; getting to target architecture.

**Tommy's seven drivers (verbatim-condensed, 2026-08-03, after cycle-1 consolidation):**
1. There is a bigger vision for this project.
2. Too many issues; suspects lots are or will be moot.
3. Last epic got super in the weeds — made things very specific or durable while just taking a first step; notably an obsession with undefined performance metrics. Some (token load) were on the right track but undisciplined.
4. Near-term ideas not getting settled: (a) get the context governor actually working so agents don't get overloaded; (b) move step-specific skills/instructions into the spine to reduce overhead on general agent instructions.
5. Prefer mechanization over prose instructions. The power of the project is the framework. Prose stays light except (a) ensuring spine use and (b) focusing on the project itself.
6. Jargon is causing issues. Make discourse simple and direct: demand reports in American simplified technical English; build a local glossary.
7. Many moving parts — find the through-lines to stay organized and bite off manageable chunks.

## Current candidates

All from cycle-1 consolidation. None culled; none converged. These are directions, not a menu ranked by me — except where an excursion's own evidence ranks them, cited inline.

- **C1 — Backlog consolidation sweep.** Execute exc-4's disposition list (close 4 done-but-open, dup/merge 3, rescope 3, rewrite-or-close 2 empty stubs) and re-file the 13 clusters as cluster-level items instead of 127 singles. Cheap, mechanical, directly answers the "too many in-the-weeds issues" itch. Evidence: `evidence/exc-4-issues-RESULT.md` §5–6.
- **C2 — Corpus reachability first (K13).** Before any further doctrine or measurement work: does the corpus reach a run at all? #331 measured zero skill invocations in 5/5 runs; 12/19 skills fail the registration verifier; this repo has no map (#156) so B3's own contract runs degraded here. Upstream of every other candidate's payoff. Evidence: exc-4 §5-K13, exc-2 Part C6.
- **C3 — Close the B1 loop: run the first real consolidation (K10).** The store went 7→32 episodes (the stated blocker was "not enough recurrence"); #392 is a cold-sensor-validated cluster sitting ready; consolidating it is simultaneously the outstanding clause of phase 1's own "done" and a live test of the whole B1 mechanism. Evidence: exc-2 Part C2/E, exc-3 §2c, exc-4 §5-K10.
- **C4 — Idea-substrate exploration (the vision step).** Federation's stated precondition ("local map use is proven") was met by #307's PASS — the only gate in the record that flipped — and the spec routes the revisit to a new exploration, never a cut. Tommy's own #297 notes (graph over markdown, genericise beyond coding, journal ∩ philosophy) point the same way and partly contradict the shipped spec, so they need deliberate reading against it. This exploration could take that as its refine direction. Evidence: exc-2 Parts C1/C7/E.
- **C5 — Cheap unblocking measurements, no new architecture.** Three, in ascending cost (exc-2 Part E): re-query the existing #307 transcripts for B4's second trigger conjunct; the first consolidation (= C3); #414's ablation arm (parked, correctly, by its own author).
- **C6 — Pay the unowned closeout debts.** File the audit's #1 finding (resolved load manifest + the unit question — named precondition of any kernel/fragment split, currently owned by nobody, recorded nowhere but a closeout artifact); bookkeeping closures (epic #298 issue, #322); settings.json wiring note points at a closed issue. Evidence: exc-1 §5.1/5.2/5.5.

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Phase 1 delivered: 12/12 dispositioned, 10 as intended; #306 dissolved as an honest null; #308 substituted migration for the required consolidation — the spec's "done" clause is unmet and untracked | Tested: all closeout artifacts, tracker state, net diff. NOT: full ADMIRAL_LOG, #303's evidence, per-issue authorship of ≥313 | exc-1 |
| Target architecture = confirmed Stratum A (uncuttable direction) + Stratum B (B1/B3 done, B2 not-yet-earned, B4 half-triggered); federation's precondition is now MET and the spec's own routing for it is a new exploration | Tested: full DESIGN_SPEC + ideas board + cut-issue verdicts. NOT: pre-archive excursion reports, cycle files | exc-2 |
| Episode store: 23/32 episodes carry live unpaid signal; only 7 harvested; the closeout read 1/32, so the store has never actually been harvested | Tested: all 32 read, remedies grepped against shipped corpus, mechanisms confirmed to exist. NOT: whether any is worth fixing (Tommy's reserved call), dogfood repos | exc-3 |
| Backlog: 127 open issues = ~10 immediate dispositions + 13 consolidation clusters; majority is correct-findings-at-wrong-granularity, not junk; only 4 genuinely obsolete/superseded | Tested: 127/127 classified, 24 tree-verified. NOT: 103 rest on filer evidence quoted, not re-derived | exc-4 |
| The single upstream question under all of it: #331 — the corpus was offered and declined in 5/5 measured runs; nothing phase 1 shipped reaches a run that doesn't invoke it | Tested: exc-2 and exc-4 independently converged on it. NOT: whether invocation rate differs in real (non-measured) use — no instrument exists (#136) | exc-2 + exc-4 |

- **C7 — Plain-language discourse standard + local glossary.** (Added from driver 6.) Reports written in simplified technical English; a maintained project glossary; possibly a mechanical jargon-density check on human-facing surfaces (an idea already parked in 2026-07-10 feedback). Fits driver 5: the check is a mechanism, the standard is one prose line. Note `docs/agents/GLOSSARY.md` referenced by doctrine does not exist today (verified cycle 1).
- **C8 — Spine-carries-the-instructions.** (Added from driver 4b.) Move step-specific skill prose into the spine templates the engine pushes per gate, shrinking always-loaded role instructions. Evidence already in hand: #310's refusal note observed the corpus is "already kernel-shaped" and #307 showed per-task delivery through the spine template moved behavior that always-loaded prose could not. This attacks B2's goal by the deletion/relocation route the spec explicitly blesses ("if deletion alone suffices, the break is not taken — that outcome is success") — no gate evidence or metrics needed.

## Open threads

Seeds for cycle 2:

- **Proposed through-lines (agent recommendation, awaiting Tommy):** Arc 1 "make the frame hold" = governor-fires (K2) + spine-carries-instructions (C8) + mechanize-over-prose (K1 wiring + #328/#329); Arc 2 "clean the decks" = backlog sweep (C1) + closeout debts (C6) + plain-language/glossary (C7); Arc 3 "the vision step" = idea-substrate exploration (C4, reading #297 against the spec). Metrics work (K4/K5) stays parked per driver 3. Token load is the one metric with a live consumer — the governor's gauge — so it survives inside Arc 1, disciplined by having exactly one customer.

- **Which candidate (C1–C6) leads, and what mix?** C1+C6 are near-mechanical and could ride alongside any deeper direction. Convergence is Tommy's.
- **#297 vs. the confirmed spec.** Tommy's "markdown is kind of a shitty graph structure" contradicts the spec's git-native-authored-truth commitment. Needs a deliberate read, likely inside C4 — is that a revision of Stratum A or a new layer under it?
- **The B1 consolidation trigger is unowned.** "Wait for recurrence" has no threshold, owner, or trigger. If C3 runs, that gap closes by doing; if not, it needs an owner.
- **Two observation banks are live again** (4 lessons banked post-cut, #404 confirmed live) — any consolidation design has to say which bank is canonical.
- **The `strength`-field migration** (#399): 173 values Tommy ruled out sit in 32/32 episodes; any consolidation must decide their fate first.
- **11 unmerged branches**, incl. #264's three commits with no PR — orphan-risk under #412; disposition needed before any branch cleanup.
- **Scoped-null carryovers:** #303's evidence never located (exc-1); dogfood-repo inbound-signal question (zero findings from three projects — export path never exercised, or nothing hit?) still has no instrument.

## Excursion briefs (cycle 1)

## Cycle 2 framing (Tommy, 2026-08-03)

- The three arcs are "generally true, and can probably be subdivided further" (lines unknown — a cycle-2 consolidation question).
- Vision (Arc 3) goes on the back burner — **but thresholds must be set well: "we do not know what the finished project looks like, this is early."** Standing constraint: any threshold or durable decision made now must be cheap to revise; grade decisions guess/placeholder unless measured.
- Mechanisms + cleanup lead (Arc 1 + Arc 2).
- He does not trust most of the open issues: **one agent per issue** (sonnet) to judge whether it is real given the work already landed and where the project is going → `exc-5-issue-reality`.
- Governor fix is suspected pernicious, not easy: **prototype it**, and the proof includes the prototype successfully creating its own subagents that are separately tracked → `exc-6-governor-prototype`.
- Jargon is confusing him and likely confusing between agents: research **simplified technical English** for reports + glossary → `exc-7-simple-english`.

## Open threads after cycle 2

- **Adjudicate the 12 issue-verdict disagreements** (list in exc-5 artifact) before closing anything; both passes agree on everything else.
- **Check the PostToolUse hook payload for subagent calls** — the one untested question that decides whether the governor fix is ~one line or needs the prototype's fallback matcher.
- **Write `docs/agents/GLOSSARY.md`** — Charter skill already owns the imperative; exc-7 provides the seed terms (21 measured) and format.
- **Arc subdivision:** cycle-2 evidence suggests Arc 1 splits naturally into governor-fix (proven seed) / spine-carries-instructions (unprototyped — candidate for the same treatment) / wiring-checks; Tommy suspected subdivision, lines now visible.
- **Spine-carries-instructions has no prototype yet** — the one Arc-1 leg still resting on inference (#310's observation) rather than a live demonstration.
- **Stale-binding sweep** (47 live bindings, 36 under one session key) — cheap after re-keying; part of the governor cut.

## Cycle 3 framing (Tommy, 2026-08-03)

"let's definitely do the spine instructions prototype. we can do a quick overview of the 12 disagreements as well." → exc-8 prototype dispatched; the 12-disagreement overview is done inline by the orchestrator from the exc-4/exc-5 artifacts (no new dispatch) and delivered for adjudication.

## Excursion briefs (cycle 3)

### EXCURSION_BRIEF exc-8-spine-instructions: spine carries the step instructions

- **The one named question:** Can step-specific instructions move out of a role's always-loaded skill prose into the spine template the engine pushes per gate — demonstrated live on one real role step — without losing the behavior, and what does the seam look like?
- **Type:** prototype — dispatches constellation-prototyper. **Why:** the belief rests on one inference (#310's "already kernel-shaped" + #307's spine-delivery effect); a live tracer is the honest test, exactly as the governor got.
- **Branch:** logic. **Location:** worktree (agent-driven, throwaway).
- **What "answered" looks like:** (1) a live tracer — one relocated instruction delivered through the engine's `current` at its gate, acted on correctly by a cold sonnet subagent that never saw the skill prose; (2) a paragraph-level relocation census of one role (step-specific vs always-needed vs reference-on-demand, with counts and shares); (3) the seam description for a general relocation. Lands at `evidence/exc-8-spine-instructions-RESULT.md`.
- **Budget / stop conditions:** ~3 delivery-seam variants; nothing on main; no corpus rewrite (tracer + census only); no settings.json/hook changes; scoped nulls.

## Spec-phase excursion (Tommy, 2026-08-03)

During section-by-section spec review (Intent and Section A approved), Tommy stepped back before the spine sections: "we may be working too hard for the checklist engine. this seems like exactly what MCP is for, and models are trained on MCP." He chose the live test over belief.

### EXCURSION_BRIEF exc-9-mcp-front-door: an MCP server as the engine's front door

- **The one named question:** Does putting an MCP front door on the existing checklist engine let a cold agent drive a spine correctly with less teaching and fewer fumbles than the CLI door — and what does the production seam look like?
- **Type:** prototype — dispatches constellation-prototyper. **Why:** the belief rests on training-data intuition (models are trained on MCP tool calling, not on our CLI) plus four live CLI fumbles in this session; a two-arm tracer is the honest test, same treatment the governor and spine-instructions got.
- **Branch:** logic. **Location:** worktree (agent-driven, throwaway).
- **What "answered" looks like:** (1) a live two-arm tracer — a minimal stdio MCP server wrapping the existing engine module, ~6 coarse tools, registered only inside the worktree; one cold sonnet agent drives a toy spine to done through the MCP tools with no CLI teaching in its prompt, a control agent drives the same spine through the CLI with an equivalent minimal prompt; count invalid calls, engine refusals, retries, and prompt words per arm. (2) The seam description: one core, two doors (CLI stays for hooks and non-MCP harnesses); tool count and schema shape; how the gate imperative rides tool results; what breaks (headless runs, subagent tool inheritance, lease/session identity). (3) The governor note, scoped: could the server push gauge readings in its responses — identity question flagged, not solved. Lands at `evidence/exc-9-mcp-front-door-RESULT.md`.
- **Budget / stop conditions:** ~3 variants on the tool shape if the first fails; nothing on main; no settings.json or global config changes; `.mcp.json` and any SDK install live only in the throwaway worktree/venv; scoped nulls — state what was and was NOT tested.

**Tommy's exc-9 rulings (2026-08-03):** per-agent server instances ("gotta keep those work chains separate"); the ~1k schema token trade accepted ("small steps are good"); bare-descriptions control arm SKIPPED — rich tool descriptions accepted as just-in-time teaching ("almost exactly what I'm getting at with just in time subskill loading"), trimming descriptions is a later item. Workstream F added to the spec with these as design constraints.

### exc-9 verdicts (spec-phase, added to the running verdict table)

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| MCP door works live and halves the cost of driving a spine: cold sonnet agents reached done in 14 engine calls with zero fumbles through 7 MCP tools, vs 24–27 calls with 2 refusals and 4–7 `--help` reads through the CLI — same engine, same spine, hooks suppressed in both arms. CAVEAT: 2 of 4 fumble classes were prevented by tool-description prose the author wrote, not by MCP structure; the named next variant (bare descriptions, ~$0.30) separates the two | Tested: live MCP round trip in cold headless sessions, 2 replicates/arm, subagent tool inheritance confirmed, gauge advisory riding a tool result demonstrated. NOT: interactive-session .mcp.json pickup without restart, real role spine, concurrency, bare-description control, long-run schema token cost | exc-9 prototype |
| Serious regression risk found: subagents inherit the parent's server process, so parent and child present as ONE session id — the actor-authority lease could not tell a Commander from its implementer, and a subagent polling status would get the PARENT's context reading as its own (a plausible wrong number). Production door must carry caller identity; ties directly to Section A's identity module | Same scope as above; demonstrated by direct subagent tool call | exc-9 prototype |
| Premise correction: always-loaded SKILL.md files carry only 1–2 lines of engine-calling teaching each — the real invocation-string weight is in the on-demand engine reference (~4,500 tokens) and inside 7 of 21 spine-template imperatives (10,298 chars). The MCP trade is ~1,000 always-loaded schema tokens for stripping those, a real but narrower win | Measured over the installed corpus by the excursion | exc-9 prototype |
| Two engine defects surfaced: command checks run with no cwd (checklist_engine.py:731 — independently reproduces #315), and the `refusals` counter silently records 0 for a run whose refusals predate the lease claim (observed live: 2 real refusals, recorded 0) | Reproduced directly; counter arming is documented, the zero-on-real-run failure mode may not be | exc-9 prototype |

## Excursion briefs (cycle 2)

### EXCURSION_BRIEF exc-5-issue-reality: per-issue reality check

- **The one named question:** For each of the 127 open issues, is it real *today* — given the tree at HEAD, the work phase 1 already landed, and the project's stated direction (mechanization over prose, spine-carried instructions, governor working, vision later)?
- **Type:** research — one cold sonnet agent per issue (Tommy's explicit instruction), fan-out via workflow; each agent reads the issue and checks its claims against the tree by command where cheap.
- **What "answered" looks like:** per-issue verdict (real-now / real-later / superseded / obsolete / unclear) + one-line evidence + recommended disposition, aggregated to `evidence/exc-5-issue-reality-RESULT.md`. Agents are NOT shown exc-4's classifications (cold, unbiased second read).
- **Budget / stop conditions:** read-only against tracker and tree; no issue edits/comments; an agent that cannot decide returns unclear with what it checked. Scoped nulls apply.

### EXCURSION_BRIEF exc-6-governor-prototype: separately-tracked subagents

- **The one named question:** Can the context governor track a dispatched subagent's engine work under the subagent's own identity — the prototype agent creates its own subagents whose activity is gauged separately (not accumulated onto the parent's binding), with terminal work releasing its binding — or is the fix pernicious as suspected?
- **Type:** prototype — dispatches constellation-prototyper. **Why this type:** the failure (#383: subagents share the parent session id; 30 stale bindings; zero readings over a multi-day run) is a runtime-identity problem you can only feel out in code.
- **Question:** (same as above — one question, one prototype)
- **Branch:** logic. **Why this branch:** pure mechanism behavior, no UI, no measurement apparatus.
- **Host-project conventions:** Python 3.12; run tests as `python -m pytest` (NOT `py -m pytest` — #313); engine and governor code under `scripts/`.
- **Location:** worktree. **Driver:** agent-driven → throwaway worktree.
- **Stop conditions:** answered = a spawned subagent's engine activity demonstrably lands under its own binding while the parent's stays clean, shown live, or a scoped statement of exactly where separation breaks. Budget: ~3 mechanism variants, then report even if inconclusive. Exclusions: do NOT modify `~/.claude/settings.json` (Tommy's file), do NOT wire hooks globally, do NOT land changes on main — throwaway worktree only.
- **Return format:** `PROTOTYPE_RESULT` → `evidence/exc-6-governor-prototype-RESULT.md`.

### EXCURSION_BRIEF exc-7-simple-english: simplified technical English standard

- **The one named question:** What should a simplified-technical-English standard for this project's reports look like — drawing on ASD-STE100 and similar controlled languages — including a local-glossary mechanism, so that agent-to-human and agent-to-agent writing becomes simple, direct, and (where possible) mechanically checkable?
- **Type:** research — primary sources on controlled/simplified English (ASD-STE100 rules, plain-language standards), plus a sample audit of this repo's own artifacts for jargon shapes that caused confusion.
- **What "answered" looks like:** cited findings + a concrete draft: ~10 writing rules fit for agent reports, the approved-vocabulary/glossary structure, and 2–3 candidate mechanical checks (lintable rules). Lands at `evidence/exc-7-simple-english-RESULT.md`.
- **Budget / stop conditions:** research + drafting only; no doctrine edits; the standard itself is a cycle-2 consolidation item for Tommy, not something this excursion ships. Scoped nulls apply.

## Excursion briefs (cycle 1)

### EXCURSION_BRIEF exc-1-epic298: phase-1 delivery audit

- **The one named question:** What did phase 1 (epic #298 and its follow-on issues #299–#310) actually deliver against its stated intent, and what did its closeout flag (lessons, backlog routing, architecture reconcile, deferred work) that bears on backlog consolidation or the next step?
- **Type:** research — facts from run artifacts and git/forge history, not opinion.
- **What "answered" looks like:** a cited findings file: delivered-vs-intended table, every closeout flag with source path, and an explicit list of items epic #298 deferred or routed to the backlog. Lands at `evidence/exc-1-epic298-RESULT.md`.
- **Budget / stop conditions:** read-only; sources are `.agent-work/epic-298/`, `.agent-work/archive/2026-08-03-epic-298/`, GitHub issues/PRs #298–#310 area, git log. Do not modify anything outside the result file. Report even if inconclusive. Scoped nulls apply.
- **Sources:** the two work areas above (ADMIRAL_LOG, EPIC_SUMMARY, LESSONS_AUDIT, BACKLOG_ROUTING, ARCHITECTURE_RECONCILE first), `gh issue view`/`gh pr view` for #298–#310, `git log`.
- **Findings format:** every claim cites file path or issue/PR number; contradictions surfaced, not smoothed.

### EXCURSION_BRIEF exc-2-explorer: target architecture + vision from explore-grander-scale

- **The one named question:** What target architecture and longer-term vision did the explore-grander-scale run (closed 2026-07-31) confirm or discuss-but-not-cut, and what does its own record imply the natural next step is?
- **Type:** research — the record exists; this is extraction, not invention.
- **What "answered" looks like:** a cited findings file: the confirmed spec's shape (what B0/B1/B2/B3 etc. were, what was cut vs conditional vs doctrine-only), the vision threads discussed beyond the cut scope (with quotes/paths), and the record's own statements about what comes next. Lands at `evidence/exc-2-explorer-RESULT.md`.
- **Budget / stop conditions:** read-only; primary source `.agent-work/archive/2026-07-31-explore-grander-scale/` (ideas board + DESIGN_SPEC first); secondary: issues cut from it (#299, #307, #331 and siblings). Do not modify anything outside the result file. Scoped nulls apply.
- **Sources:** archive work area above; `gh issue view` for the cut issues; docs/ROADMAP.md if present.
- **Findings format:** distinguish CONFIRMED-spec content from discussed-but-unconfirmed vision, with citations; contradictions surfaced.

### EXCURSION_BRIEF exc-3-episodes: episode store triage

- **The one named question:** Which open/stored episodes still carry live signal for the post-overhaul corpus, and which are artifacts of the pre-phase-1 shape (superseded, already-harvested, or moot)?
- **Type:** research — classification against the delivered phase-1 reality.
- **What "answered" looks like:** a per-episode table (id, one-line content, verdict: live-signal / superseded-by-<what> / already-harvested / moot, evidence) plus counts derived by command, not memory. Lands at `evidence/exc-3-episodes-RESULT.md`.
- **Budget / stop conditions:** read-only; start from `docs/EPISODE_STORE.md` to locate the store and its schema, then enumerate ALL episodes by command and state the count looped over. Do not modify or delete episodes. Scoped nulls apply.
- **Sources:** `docs/EPISODE_STORE.md`, the episode store it names, `.agent-work/` feedback/inbox artifacts where episodes reference them.
- **Findings format:** table + counts; every verdict cites the episode content and what supersedes it.

### EXCURSION_BRIEF exc-4-issues: open-issue census and consolidation map

- **The one named question:** Of all open GitHub issues, which block the target architecture, which are real standalone defects, and which are in-the-weeds (superseded by phase 1, obsolete, or consolidatable into a larger cut) — and what consolidation clusters fall out?
- **Type:** research — full census with per-issue evidence.
- **What "answered" looks like:** a complete table of ALL open issues (number, title, age, verdict: arch-blocking / real-defect / superseded / obsolete / consolidate-into-<cluster>, one-line evidence), the total count derived from `gh issue list` (state the command and count), and proposed consolidation clusters. Recommendations only — closing/relabeling is the human's call. Lands at `evidence/exc-4-issues-RESULT.md`.
- **Budget / stop conditions:** read-only against the tracker (no issue edits, no comments); enumerate every open issue — an under-inclusive census is a failed check. Scoped nulls apply.
- **Sources:** `gh issue list --state open --limit 200 --json ...`, individual `gh issue view` where the title is not decisive, phase-1 artifacts for supersession evidence.
- **Findings format:** table + cluster proposals; every verdict carries evidence, uncertainty marked UNCLEAR rather than guessed.

## Rejected ideas (with reasons)

_None yet._

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | shotgun (human-directed: divergence sourced from review corpus, not invented one-liners) | four research excursions: epic #298 closeout, explore-grander-scale record, episode store, open issues — all 4 answered, artifacts under evidence/ | Six candidate directions C1–C6 on the board; ~10 immediate tracker dispositions identified; #331 named the upstream question; convergence/flavor for cycle 2 awaiting Tommy |
| 2 | refine (mechanisms + cleanup per Tommy) | exc-5 per-issue fleet (127 cold sonnet agents), exc-6 governor prototype, exc-7 simplified-English research — all 3 answered | Governor fix proven feasible (re-key on per-subagent identity; not pernicious; check hook payload first). Jargon = vocabulary problem; glossary slot empty; glossary-first plan. Backlog: 112/124 two-pass agreement, 15 close candidates, 17 parkable, 12 disagreements to adjudicate. Shape of a mechanisms+cleanup epic is forming; convergence is Tommy's call |
| 3 | refine (continuing) | exc-8 spine-instructions prototype + inline 12-disagreement adjudication overview | Relocation PROVEN live: 54.2% of Commander's always-loaded words are step-specific; SKILL.md already pure kernel; 84% of relocatable words land on execute+plan. Constraints: bootstrap kernel must stay; fix the engine RAIL 2x echo first; relocate selectively. New defect found: gate anchors/constraints are invisible through `current` (5/5 cold agents hit it). Adjudication recs: close 10, rescope #208, dup #278→#409. Both Arc-1 legs now prototype-proven |

## Cycle-3 verdicts (added to the running verdict table)

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Spine-carried instructions work: a relocated instruction delivered only through the engine's per-gate output was acted on correctly by a cold agent (round 2 discriminated: no-instruction arm skipped the behavior, spine arm performed it and rebuilt the missing artifact section) | Tested: one real instruction, one gate, real engine, 5 cold sonnet agents in 2 rounds, 229 guard tests green. NOT: bulk relocation (dose-response = named next variant), other roles, shared-across-roles doctrine text, n=1 per arm | exc-8 prototype |
| Relocation design constraints: leave a bootstrap kernel (SKILL.md is already exactly that — 6/6 units always-needed); fix the RAIL imperative echo (exact 2x cost measured) before any bulk move; keep reference-on-demand text behind pointers; multi-step rules stay in prose | Same scope as above; census is hand-classified judgment over 97 units, reproducible by census.py | exc-8 prototype |
| Defect discovered: gates carry `anchors`/`constraints` blocks the engine never renders into `current`, so agents driving from the canonical channel cannot see them — 5/5 cold agents independently hit and flagged it | Tested: read of checklist_engine.py state projection + empirical (constraints written, never rendered). NOT: whether any live run has been harmed by it (bears on #393) | exc-8 prototype |
| Disagreement adjudication (recommendation, Tommy disposes): close 10 (#239 #244 #296 #336 #337 #338 #347 #349 #364 #374), rescope #208 to its unbuilt mechanized-check half, close #278 as dup of #409. Where the two passes conflicted on a tree fact, the cold per-issue read was right in the one case hand-verified (#239: @grade lines exist, landed by 7c8ff1b) | Tested: cold-read evidence cross-checked, one contested claim re-verified by hand. NOT: the other 11 tree claims not independently re-run by the orchestrator | q1 inline |

## Cycle-2 verdicts (added to the running verdict table)

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| The governor fix is feasible and NOT pernicious: harness ≥2.1.220 gives every subagent its own transcript + agentId; keying bindings on session_id#agentId separates tracking, keeps the parent clean, and lets terminal work release — #383's two symptoms are one bug | Tested: live in a throwaway worktree with real spawned sonnet subagents, 3 variants (env-only failed; naive text match failed instructively; structured match works). NOT: the real PostToolUse hook payload (decides fix size — check first), identical-command race, real engine integration, migrating the 47 live stale bindings | exc-6 prototype |
| The jargon problem is undefined vocabulary, not sentence length: medians 12–15 words (inside STE caps) but ~1 word in 40 is an undefined coined term; the doctrine-referenced glossary file does not exist | Tested: 5 artifacts measured by script, 36-term census over 3 artifacts, repo-wide glossary-heading grep (zero hits). NOT: official STE Issue 9 text (numbers are from secondary sources); whether jargon actually degrades agent-to-agent comprehension (no evidence either way — cheap test named) | exc-7 research |
| Backlog reality: 93 real-now, 17 real-later, 15 superseded, 2 unclear out of 127 — and two independent passes (cluster-level exc-4 vs cold per-issue exc-5) agree on 112 of 124 comparable | Tested: every issue read cold by its own agent with tree checks. NOT: 12 disagreements unadjudicated (both directions); cluster fits not re-derived | exc-5 fleet |
