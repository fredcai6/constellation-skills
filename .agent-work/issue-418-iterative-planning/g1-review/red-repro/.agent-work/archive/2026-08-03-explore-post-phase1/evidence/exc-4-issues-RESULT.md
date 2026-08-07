# exc-4-issues — open-issue census and consolidation map

**Excursion:** `exc-4-issues` (cycle 1, `explore-post-phase1`)
**Date:** 2026-08-03 · **Repo:** `C:/Programs/constellation-skills` · **HEAD:** `79db918`
**Posture:** STRICTLY READ-ONLY against the tracker. No issue was closed, edited, labelled, or commented on. Everything below is a recommendation; the human disposes.

---

## 1. The census — command and counts

```
gh issue list --state open --limit 200 --json number,title,createdAt,labels
```

| | count |
|---|---|
| **Open issues returned by the command** | **127** |
| **Rows in the classification table (§4)** | **127** |
| Match? | **YES — 127 = 127** |

The two counts are stated as the brief requires and they agree. No open issue was dropped, and no row is invented. Ages are computed against 2026-08-03.

Supporting commands used for evidence (all read-only):

```
gh issue list --state open --limit 200 --json number,title,body        # full bodies for every row
gh issue list --state closed --limit 60 --json number,title,closedAt   # supersession evidence
git log --oneline --all --grep="(#N)"                                  # merged-work-per-issue sweep
git branch -a --no-merged main                                         # abandoned-work sweep
```

---

## 2. Headline findings (read this if you read nothing else)

1. **Three issues are already DONE on `main` and were never closed** — #131, #208, #322. Each is verified against the shipped tree, not against a claim. This is issue #354 (*"issues stay open after their PR merges"*) firing three more times, undetected, which upgrades #354 from a tidiness complaint to a measured tracker-integrity defect. It also means the raw backlog count overstates real work.

2. **The single biggest arch-blocker is #156 — this repo has no map.** `ls docs/architecture` → *No such file or directory* at `79db918`. Phase 1's entire B3 deliverable is a *map-first* contract, and the repo that ships it cannot orient against its own architecture (#394 confirms it runs `DEGRADED-NO-MAP`). Every downstream map-first measurement in this repo is measured in degraded mode by construction.

3. **The second biggest is #331 — measured runs invoked ZERO skills.** If an ordinary brief causes an agent to decline the corpus, then every doctrine change phase 1 landed reaches nobody. #136 (one invocation-in-anger eval per skill) is the instrument that would detect this; #290, #346, and #356 are three separate defects in the corpus's *trigger surface*. These five are one cluster and it is upstream of everything else.

4. **The "in-the-weeds" mass is real but it is not junk — it is one recurring shape.** 34 of the 127 are follow-ups filed by epic-298's own gates (#357–#415). They are individually correct, individually small, and collectively unreadable. They consolidate into six clusters, not sixty issues.

5. **Only 4 issues are genuinely obsolete or superseded.** The backlog is not full of stale garbage; it is full of *correct findings filed at the wrong granularity*. Consolidation, not closure, is the lever. The exception is the epic-298 measurement-methodology set, which should be folded into one standing document rather than carried as issues.

6. **Abandoned work exists on an unmerged branch.** `governor/264-e2e-assertion` carries three real commits of #264 work (`fd5e1be`, `b8f4f26`, `3e0193d`) with no PR and no merge. Given #412 (deleting a squash-merged branch orphans its commits), this is at risk. Flagged, not touched.

---

## 3. Verdict vocabulary and clusters

**Verdicts**

| verdict | meaning |
|---|---|
| `ARCH-BLOCKING` | must be resolved for the target architecture (grander-scale Stratum B: B0–B4) to work or to progress |
| `REAL-DEFECT` | a genuine standalone defect worth fixing on its own terms, independent of the arch direction |
| `SUPERSEDED` | the work is done, or its premise was overtaken by phase 1 — recommend close |
| `OBSOLETE` | the premise no longer holds — recommend close without work |
| `CONSOLIDATE→Kn` | real, but should be absorbed into the named larger cut rather than carried alone |
| `UNCLEAR` | could not be determined from the available evidence; what was checked is stated |

**Clusters** (full proposals in §5)

| id | cluster |
|---|---|
| K1 | Built-but-not-delivered — capability ships, the wiring that makes it run does not |
| K2 | Context Governor: make it fire (epic #267 remainder) |
| K3 | Episode store hardening (B1 substrate correctness) |
| K4 | Measurement methodology for measured arms |
| K5 | B2 kernel-break evidence |
| K6 | Harness capability limits (what the agent harness will and will not do) |
| K7 | Engine, lease, and gate mechanics |
| K8 | Artifact and tracker hygiene |
| K9 | Curator-routed doctrine bundles |
| K10 | A check that cannot register its own failure |
| K11 | Code-shape cleanups (Fowler-class) |
| K12 | Unconfirmed design threads (explorer intake, not dispatchable) |
| K13 | Corpus reachability — is the corpus invoked at all |

---

## 4. Full census — all 127 open issues

| # | age | verdict | cluster | one-line evidence |
|---|---|---|---|---|
| 117 | 24d | CONSOLIDATE→K9 | K9 | The v2 tooling half merged (`8ba1293`, PR #212) and the "first real run" premise is overtaken — curator sweeps ran 2026-07-24 and 2026-07-27 and produced #220–#223, #259, #260; the remaining consolidation targets need re-measurement, not this stale list. |
| 131 | 23d | **SUPERSEDED** | — | **DONE, never closed.** `51d14ef feat(engine): append-only journal sidecar + eval cross-verification (#131)` is on `main` via PR #133, and `checklist_engine.py:2512` carries the shipped implementation citing #131 by number. |
| 136 | 22d | **ARCH-BLOCKING** | K13 | #331 measured zero `Skill` calls across five Opus runs with the full corpus installed; a per-skill invocation-in-anger eval is the only instrument that would have caught that, and today only `commander-delegated` has one. |
| 139 | 22d | CONSOLIDATE→K12 | K12 | Body opens `UNCONFIRMED — DO NOT CUT` and states it needs its own explorer run; #297 (Tommy, 2026-07-30) restates the same idea — *"agent on harness is clearly needed vice harness in agent"* — so the two are one thread. |
| 156 | 22d | **ARCH-BLOCKING** | K13 | `ls docs/architecture` returns *No such file or directory* at `79db918`; #394 independently confirms this repo orients `DEGRADED-NO-MAP`. B3 shipped a map-first contract into a repo with no map. |
| 208 | 15d | **SUPERSEDED** | — | **DONE, never closed.** `skills/admiral/SKILL.md:70` now reads *"Sweep both locations — under an epic the trio does NOT land at the main checkout"* and describes harvesting the worktree-root trio; merged as `7c8ff1b` (PR #251). |
| 214 | 14d | CONSOLIDATE→K2 | K2 | Token-use and cost capture is the same instrument family as the gauge; the governor already reads token usage from the transcript (`find_latest_usage`), so this is an extension of K2, not a separate build. |
| 215 | 14d | CONSOLIDATE→K9 | K9 | A one-line Admiral latitude doctrine ask ("lean forward on triage") with no evidence attached — belongs in the next Admiral doctrine batch, not as a standing issue. |
| 219 | 10d | CONSOLIDATE→K12 | K12 | `docs/ROADMAP.md` is confirmed absent (retired at `83a31b1`); this issue is now the *only* record of the salvaged forward threads, so it is a design-intake document, not work. |
| 220 | 10d | CONSOLIDATE→K7 | K7 | A curator-routed bundle of engine/CLI paper-cuts, already partly absorbed by #227 (struck in-body); the live remainder is engine-owner design calls that belong with the other engine mechanics work. |
| 221 | 10d | CONSOLIDATE→K9 | K9 | Curator-routed launch-order provenance cluster; every member is an Admiral/Commander doctrine or template edit, which is exactly what K9 exists to batch. |
| 222 | 10d | CONSOLIDATE→K6 | K6 | The subagent detached-work stall is a *harness* behaviour (a subagent's turn-end kills its child process), the same root as #294, #314, #413, #248 — it cannot be fixed by doctrine alone, which the body itself concedes ("prose reminders have been proven fragile repeatedly"). |
| 223 | 10d | CONSOLIDATE→K9 | K9 | Two reviewer-handoff template graduations, both vindicated by cold critics; pure doctrine/template edits. |
| 233 | 10d | CONSOLIDATE→K12 | K12 | Body opens `UNCONFIRMED — DO NOT CUT` and states *"NOT dispatchable work"*; it absorbs #216 and #225 (both closed) and carries #171's thread. |
| 234 | 10d | CONSOLIDATE→K12 | K12 | Same `UNCONFIRMED — DO NOT CUT` marker and same explicit not-dispatchable framing; the `@grade` half was separately shipped at `2334181`, the planning half was not. |
| 235 | 10d | REAL-DEFECT | K2 | Two shipped rails give contradictory instructions at the same moment: the engine says *"hand off now; do not keep working"* while `spine_rail.py` blocks the Stop event with *"SPINE MID-FLIGHT"*. Reproduced live during epic #226. |
| 239 | 9d | REAL-DEFECT (partial) | K9 | **Half done.** Item 2 is fixed — `commander-core.md:118` now points at the fixedness doctrine. Item 1 is not — `IMPLEMENTER_HANDOFF.template.md:47` and `REVIEWER_HANDOFF.template.md:49` still carry bare `**Decision anchors:**` lines with no `@grade` child line. Recommend rescoping to the surviving half. |
| 242 | 9d | CONSOLIDATE→K7 | K7 | Three `#227` engine/doc follow-ups; item 2 (`py` resolves to a pytest-less runtime) is the same root cause as #313 and #373 and should move there. |
| 243 | 9d | REAL-DEFECT | K1 | `probe_host_interpreter()` is untested against a `py.exe` install-manager stub with no registered runtime; the motivating incident wrote ~136MB of partial state into the working directory. Interpreter-resolution class, same family as #313/#373. |
| 244 | 9d | **ARCH-BLOCKING** | K8 | Human instruction recorded verbatim (Fred, 2026-07-25) and now recurring — worktree-local findings are destroyed by `git worktree remove`, so every run's learning depends on a manual harvest. B1's whole premise is that observations are durable; this is the hole under it. |
| 248 | 9d | CONSOLIDATE→K6 | K6 | Direct human ask ("make sure anything we're asking an agent harness to do is possible"); `select_backend()` auto-detects a spawn path that the harness then refuses. Same root as #222/#294/#314/#413. |
| 249 | 9d | REAL-DEFECT | — | A deliberately-filed off-ramp with a stated trigger ("needs one epic planned fully under it"). Epic-298 ran fully under `@grade`, so the checkpoint is now answerable — it was not when filed. Standalone decision, no cluster. |
| 257 | 9d | **ARCH-BLOCKING** | K1 | *"This repo tests a source tree and ships an installed tree"* — the gap that hid an entirely inert Context Governor. #344 and #406 (closed) are both later instances. This is the umbrella test-surface gap under K1. |
| 259 | 7d | REAL-DEFECT | K9 | Item 1 is a data-loss hazard that fired for real (a `git checkout`-based perturb-restore wiped an uncommitted working tree); severity puts it above the rest of the curator bundle. |
| 260 | 7d | CONSOLIDATE→K6 | K6 | Items 1–2 are harness-behaviour gaps (resumed-subagent cwd leak, Agent-tool self-send no-op); item 3 is a gate-planning design fork that belongs in K7. |
| 264 | 7d | REAL-DEFECT | K2 | **Work exists and was never merged.** Three commits on unmerged branch `governor/264-e2e-assertion` (`fd5e1be`, `b8f4f26`, `3e0193d`), no PR, not on `main`. At risk under #412's orphaning hazard. |
| 266 | 7d | CONSOLIDATE→K2 | K2 | *"The only real-world firing of the Governor's enforcement path to date was a false positive caused by a bug"* — the Trip/handoff path is untested in anger. Same epic #267, same evidence base as #264. |
| 267 | 7d | **ARCH-BLOCKING** | K2 | The epic itself: *"The math is correct. The plumbing is dead."* It is the K2 umbrella and it is still open with ~14 open children. Every B0 "collate before reacting" claim depends on runs surviving long enough to collate. |
| 270 | 7d | REAL-DEFECT | K2 | The Stop rail fires on every turn boundary of a normal healthy wave because it has no concept of *"an Admiral in `execute`, waiting on a dispatched Commander, where waiting IS the work."* Labelled `bug`. |
| 271 | 7d | CONSOLIDATE→K2 | K2 | An orchestrator holding multiple bindings is ungauged for the whole wave — a known, accepted cost of #202's fix, not a regression. Superseded in mechanism by #383, which measures the same shape at scale (30 bindings). |
| 272 | 7d | CONSOLIDATE→K11 | K11 | Verified live: `grep -n "def entries_for" scripts/hooks/spine_rail.py` returns nothing, so the shared accessor still does not exist. Quality cleanup, explicitly below the blocking bar in its own body. |
| 274 | 7d | **ARCH-BLOCKING** | K2 | Direct human requirement (Fred, 2026-07-28): *"I want you to be able to maintain commanders and commanders to maintain their crew levels by just stopping over loaded sessions and kicking off new ones."* This is the capability the whole governor points at; its trigger half is blocked on #284/#383. |
| 275 | 6d | REAL-DEFECT | K2 | Measured live in `governor-269`: hook *state* cross-writes to `C:/Programs/constellation-skills/.agent-work/.spine-rail-binding.json` even from a worktree that passed `verify_worktree_isolation.py --here`. Labelled `bug`. |
| 277 | 6d | REAL-DEFECT | K3 | Hit live: the bank renders ids as `lesson:foo` and `apply_lessons_delta.py:365` rejects the colon with a message reading `(kebab-case)` — which misdirects, since the id *is* kebab-case. |
| 278 | 6d | **SUPERSEDED by #409** | K8 | #409 supersedes it: same defect, larger and better evidenced (six files, ~79KB, enumerated with sizes and landing commits, vs. #278's two). Recommend closing #278 as a duplicate of #409, not doing the work twice. |
| 280 | 6d | REAL-DEFECT | K1 | `fleet-doctrine.md:57` seeds the state note from `.agent-work/templates/STATE_NOTE.template.md`, a path confirmed absent in a default install; the identical defect was already fixed once at #268 (`d6d25a6`), so the fix wording exists verbatim. |
| 281 | 6d | REAL-DEFECT | K1 | Verified live: `ls scripts/gauge_doctor.py` → *No such file or directory*. The "hook not wired at all" cause is unlocatable from inside the hook process by construction, so only an external doctor can cover it. |
| 282 | 6d | CONSOLIDATE→K11 | K11 | Three near-identical guard/age-format skeletons in `checklist_engine.py`; flagged non-blocking by the #265 reviewer's Fowler pass. |
| 284 | 6d | **ARCH-BLOCKING** | K2 | Measured, not asserted: four Commanders, four for four past the HARD band, one at 354,437 tokens (2.4x). Subagents run unmeasured *in principle*. This is #274's blocked precondition. |
| 285 | 6d | **SUPERSEDED (verify)** | K3 | The lesson is no longer in the Active bank — `grep` puts `lesson:verify-harness-field-and-drive-real-writer` only in `episodes/active/issue-308-004.md`, i.e. #308 migrated it into the episode store. The graduation this issue asks for was overtaken by the migration; recommend confirming the episode carries the operative content, then closing. |
| 286 | 6d | REAL-DEFECT | K2 | The 30-minute freshness window swallows the skip sidecar, so `current` prints a frozen number as a live measurement — and #271's original 26-minute freeze sits *inside* that window, meaning the fix silently un-fixes its own motivating incident. |
| 287 | 6d | REAL-DEFECT | K2 | Observed live 2026-07-28: the ambiguous-binding fan-out materialized `.agent-work/governor-262/` and siblings in the **main checkout**, containing only `gauge-skip.json`. |
| 288 | 6d | **ARCH-BLOCKING** | K1 | Tommy's ruling (*"an agent's own branch cannot edit the code that judges it"*) is implemented for the hook **code** and not for the **registration** — an agent can leave the judge untouchable and delete its own `PostToolUse` entry. This is a governance-integrity hole, not hardening. |
| 289 | 6d | UNCLEAR | K2 | **Body is literally `@-`** — the issue has no content beyond its title. The title states a real and important shape (*an inert governor is silence WITHOUT a sidecar*), and #383 measured exactly that, but the issue itself cannot be actioned as written. Recommend rewriting from #383's evidence or closing as a title-only stub. |
| 290 | 6d | **REAL-DEFECT (reproduced)** | K13 | Reproduced live at HEAD: `verify_skill_registered.py --skill workbench` → `REFUSED: ... invoker: missing invoker tag`. An independent sweep of `skills/*/SKILL.md` confirms **12 of 19** still lack `invoker:` (admiral, cartographer, charter, commander, commander-delegated, docent, explorer, lessons-auditor, prototyper, scout, triage, workbench). |
| 291 | 6d | CONSOLIDATE→K1 | K1 | Three reproduced fidelity gaps in the wiring detector, including "an interpreter change is invisible to `stale`" — same family as #281/#288, all about whether wiring is honestly reported. |
| 292 | 6d | CONSOLIDATE→K10 | K10 | *"The reviewer confirmed argparse satisfies the same assertion pre-change"* — a refusal test that passes with the guard deleted is precisely the "check that cannot register its own failure" shape #392 names. |
| 294 | 6d | **REAL-DEFECT** | K6 | Five independent rediscoveries in one wave, zero filings, each costing a step. Superseded in scope by #413 (4/4 dispatch failures, results relayed through the Admiral) but #294 carries the original evidence; merge the two. |
| 295 | 6d | UNCLEAR | K2 | **Body is literally `@-`** — title-only stub, same as #289. The title names two distinct claims (inert binding entries; `candidate_count` under-reporting), and #383 supplies evidence for the first, but nothing here is actionable as filed. |
| 296 | 6d | CONSOLIDATE→K12 | K12 | Two YouTube links and a one-line note from Tommy; genuine direction-setting input, not work. Pairs naturally with #297 and #139. |
| 297 | 4d | CONSOLIDATE→K12 | K12 | Tommy's own four bullets, and they contradict shipped decisions rather than extend them — *"markdown is kind of a shitty graph structure"* runs against the spec's "Git-native authored truth", and *"genericise constellation skills"* is a Stratum A move. Needs an explorer pass, not a cut. |
| 298 | 2d | **SUPERSEDED (bookkeeping)** | K8 | The epic is closed in the run record — memory and `git log` both show *"close(epic-298): spine terminal, lease released — epic complete"* at `79db918` — but the issue is still open and labelled `epic`. Another #354 instance. Verify against the closeout, then close. |
| 311 | 2d | REAL-DEFECT | K7 | The `!` negation-wrapper works and is confirmed by two independent data points, but lives only in a banked lesson, not in `IMPLEMENTER_PLAN.template.json` — the file a plan author actually copies from. Small, closed-form. |
| 313 | 2d | **REAL-DEFECT** | K1 | Reproduced in-body: `py -m pytest` → *No module named pytest* while `python -m pytest` → 1157 passed. 24 places in the repo prescribe the failing form. Same root as #373 and #242 item 2. |
| 314 | 2d | CONSOLIDATE→K6 | K6 | `commander-core.md` instructs delegated Commanders to do something the harness refuses: *"Teammates cannot spawn other teammates — the team roster is flat."* Doctrine contradicting harness reality. |
| 315 | 2d | **REAL-DEFECT** | K7 | `_run_check_command` invokes the shell with no `cwd=` while `_git()` a hundred lines above passes `cwd=base_dir`; five shipped relative checks resolve against wherever the engine was launched. Labelled `bug`. Found by a cold plan critic and reproduced directly. |
| 318 | 2d | **ARCH-BLOCKING** | K3 | `durable_root()` silos per worktree *under an epic* — the exact condition it exists to centralize — verified empirically during epic-298 (`durable_root('.')` returns the worktree). B1 requires episodes to accumulate in one place; this guarantees they do not, and an abandoned lease pins it forever. |
| 319 | 2d | CONSOLIDATE→K3 | K3 | Real and measured (working-tree bytes differ across worktrees under `core.autocrlf`), but explicitly scoped as *"a hazard for #308's consolidation if it compares bytes"* — #308 has since landed, so this needs re-checking against what it actually does. |
| 322 | 2d | **SUPERSEDED** | — | **DONE, never closed.** `docs/CONSTELLATION_OVERVIEW.md:72` now lists `episodes/active/ + episodes/retired/: raw observed history` as a truth layer, plus a whole new section *"The episode store, and what replaces the playbook"*. Fixed at `1dd83a1`. |
| 323 | 2d | CONSOLIDATE→K3 | K3 | Its own body states *"None of these is a live wrong answer today"* — guard gaps that only bite as the corpus grows. Correct to keep, wrong to carry as a standalone issue. |
| 328 | 2d | **ARCH-BLOCKING** | K1 | Two invariants documented as mechanically enforced are wired as `record()` surveys, which *"stores whatever the agent types and invokes nothing"*. Made actionable by Tommy's `machinize the mechanizable` ruling on #302. Direct B0.3 two-bin-rule violation. |
| 329 | 2d | **ARCH-BLOCKING** | K1 | Verified live: `grep -rln "verify_worktree_isolation" skills/*/templates/*.json` returns **zero**. The corpus's own words call the failure *"data loss, not friction"*, a working exit-code script exists, and it is invoked by prose only. Highest-consequence prose-only invariant. |
| 330 | 2d | REAL-DEFECT | K1 | No confirm-dead check exists before a worktree is reused; the body is honest that this is *"a real systems problem"* (the harness reports "completed" for processes still holding the worktree), which is why it is lower priority than #329. |
| 331 | 2d | **ARCH-BLOCKING** | K13 | **All five measured runs invoked ZERO skills** with the full corpus installed and enumerated in `init.skills`. Not instrument failure — the treatment was offered and declined. This threatens the delivery premise of every doctrine change phase 1 landed. |
| 336 | 2d | REAL-DEFECT | K1 | A live contradiction between two current roles: Charter ships a task to write `docs/agents/engine-config.json` while `COMMANDER_SPINE.template.json` states the path is dead and must not be created. Not staleness — both are current. |
| 337 | 2d | CONSOLIDATE→K10 | K10 | *"Two nothings compared equal and the check reported success."* The body itself tabulates the same shape appearing **four times in one epic in four costumes** — it is the K10 cluster's founding evidence. |
| 338 | 2d | CONSOLIDATE→K7 | K7 | A real loss under epic-298: a held PR was merged past, and the commander's later push never reached `main`. Two contributing causes, both gate/handoff protocol. |
| 339 | 2d | **REAL-DEFECT (reproduced)** | K8 | Verified present at HEAD (`.agent-work/CONSTELLATION_INBOX.json` exists) and the body's measurement is unambiguous: **5 of 5** tracked issues report `open` while all are closed. A ledger that stores a copy of status manufactures phantom debt forever. |
| 342 | 2d | **ARCH-BLOCKING** | K3 | `LIFECYCLE_STANDINGS = ("active", "disputed", "superseded", "rejected")` — no `confirmed`, so a prediction that was checked and held is indistinguishable from one never checked. Labelled `bug`. B1's rhyme-detection cannot reason over a store where "held" and "never looked at" share a value. |
| 343 | 2d | CONSOLIDATE→K3 | K3 | Pathless *"the current map"* phrasing in four role surfaces (cartographer, scout, explorer, commander-core); the body is careful that it is *"possibly not the same defect"*, so it needs a scoping pass, not a fan-out. |
| 344 | 2d | REAL-DEFECT (reduced) | K1 | **Materially improved since filing.** `~/.claude/skills/CORPUS.json` now records `source_commit: 466eafa` and `git rev-list --count 466eafa..HEAD` = **2**, not the 18 the body measured. The defect class (no mechanism keeps the installed corpus current) survives; the acute instance does not. |
| 345 | 2d | **ARCH-BLOCKING** | K1 | The K1 umbrella, and item 1 is reproduced live: `grep -rn "context_manifest" skills/` returns **nothing** — the projection manifest producer still has no caller. Six instances in one epic. This is the pattern statement the whole cluster hangs from. |
| 346 | 2d | **REAL-DEFECT (reproduced first-hand)** | K13 | Confirmed from *this* session's own skill roster, which lists `constellation-diagnose: Constellation Diagnose` — a degenerate description — while every other skill shows its full one. Both `skills/diagnose/SKILL.md` and the installed `~/.claude/skills/constellation-diagnose/SKILL.md` carry a correct description, so the fault is in registration, not the file. That narrows the root cause the issue says was unestablished. |
| 347 | 2d | CONSOLIDATE→K4 | K4 | *"Unachievable by construction for any Commander-loaded arm"* — the Commander spine's `plan` step **is** authoring a file, so "zero Write calls" cannot be an evidence standard. Methodology, and it recurs on every arm. |
| 349 | 2d | CONSOLIDATE→K4 | K4 | A measurement-design lesson that could not be banked (bank at cap) and was filed to the tracker as a fallback — by its own account it is a lesson, not an issue. |
| 351 | 2d | CONSOLIDATE→K4 | K4 | Structural, not a packet-assembly slip: a Commander externalises reasoning into `.agent-work/`, so a blind grader sees a thin artifact. Recurs on every future skill-driven measured arm. |
| 352 | 2d | CONSOLIDATE→K4 | K4 | Measured: run-698 tool call 147 of 148 wrote to the f1Brainz auto-memory store, outside its worktree. A denylist cannot enumerate every such path; an allowlist can. |
| 354 | 2d | **REAL-DEFECT (recurring)** | K8 | The body counts two instances in one epic; **this census independently found three more** — #131, #208, #322 are all done on `main` and still open. That is 5 known instances, and the failure is silent in both directions. |
| 356 | 2d | **REAL-DEFECT** | K13 | Direct evidence against a shipped doctrine claim: `constellation-commander`'s description says it is *"not for a delegated/launch-order dispatch"*, and PRE-B ran 5/5 headless subjects through its spine with no stalls. A wrong description is a wrong trigger surface. |
| 357 | 2d | **ARCH-BLOCKING** | K7 | Observed, not theorised: `spine.json` carries the lease, `execute.json` carries `engine_session: null`, and **all the gates live in the child** — so a force-claim buys no exclusivity. The child journal recorded four mutating verbs from a session-less caller two minutes after a force-claim. |
| 358 | 2d | REAL-DEFECT | K7 | A complete consolidated `APPROVE` can exist in `review.json` with nothing at all in `crew-handoffs/`, because the artifact the consuming gate reads is written after the journalled step, by convention. Observed in epic-298. |
| 359 | 2d | **ARCH-BLOCKING** | K3 | `record()` has no `in-progress` guard, so **surveys never emit a context manifest** — and Reviewer, Cartographer, Scout and Curator all drive surveys. An entire class of runs produces no manifest, silently. B2/B3's observability rests on the manifest existing. |
| 360 | 2d | REAL-DEFECT | K3 | Reproduced twice by the run's own crews: `manifest_root()` is correct only when `dirname(checklist) == work_id`, so crew plans and review surveys write manifests into phantom sibling directories. |
| 361 | 2d | CONSOLIDATE→K3 | K3 | Two smaller `episode_capture.py` findings, one an unguarded `work_id` path interpolation (reproduced: `work_id: "../../ESCAPED"` writes outside the work area) — same class as the already-fixed #321. |
| 363 | 2d | REAL-DEFECT | K1 | `skills/reviewer/SKILL.md:44` directs the Fowler record into the **installed template**, mutating the shared skill install for every future run on the machine. The g2 reviewer on #304 refused to follow it and improvised. |
| 364 | 2d | CONSOLIDATE→K10 | K10 | The "grep for the caller" rule was written down, applied, and *still* missed dead code — because `map_orient.py` ships its self-test as a production subcommand, so reachability analysis lies. Confirmed three ways. |
| 366 | 2d | **CONSOLIDATE→K9 (high value)** | K9 | Three rules written as content rules that were all actually **ordering** rules, and every one recurred *after* being documented. This is a doctrine-authoring insight, not a defect — and it is the kind of thing B1 consolidation is supposed to produce. |
| 367 | 2d | REAL-DEFECT | K3 | Measured with a four-line reproduction: a foreign session's lease-conflict refusal increments the owning run's tally. The counter is checklist-scoped while both the schema doc and the composer comment call it run-scoped. |
| 368 | 2d | CONSOLIDATE→K3 | K3 | The eleven-field mechanical group is spelled out in five places with no consistency check; explicitly filed *"against the moment the group is unfrozen"*, so it is a tripwire, not current work. |
| 369 | 2d | **ARCH-BLOCKING** | K7 | *"Every recovery and continuation drill in this corpus is written from the dispatcher's side."* Epic-298 hit both halves; a resuming agent handed `claim --force` has no instruction to check whether anyone else is live. Pairs with #357 — together they are why two agents ended up in one worktree. |
| 370 | 2d | REAL-DEFECT | K6 | A g4 reviewer's APPROVE with 13 items was delivered to a commander that had handed off hours earlier and *"survived only because the recipient chose to forward it"*. Nothing in the protocol required that. |
| 371 | 2d | **REAL-DEFECT** | K7 | Hit live in #305: `REFUSED: evidence 'e-g2-review-2' does not match required {'verdict': 'APPROVE'}` against a sanctioned `APPROVE-WITH-FOLLOWUPS`. The wedge pushes a Commander toward fabricating a verdict — the exact violation the rest of the corpus exists to prevent. |
| 372 | 2d | CONSOLIDATE→K10 | K10 | A documented cost (`reopen_total` can under-count) that is reachable by an ordinary three-step route, measured by the g2 reviewer, and pinned by no test. Documented-but-unverified is the K10 shape. |
| 373 | 2d | **REAL-DEFECT** | K1 | *"It affects the first command every launch order in this epic instructs a commander to run."* Under the PowerShell tool, `py` produces no output and no exit code, so a green result is indistinguishable from the command never running — guarding the invariant the corpus calls data loss. |
| 374 | 2d | REAL-DEFECT | K7 | *"append `--report-only` to the command below"* is unreachable through `current`, which never renders command text — and reading `spine.json` directly is itself a doctrine violation. A general shape, worth a lint as well as a fix. |
| 375 | 2d | CONSOLIDATE→K7 | K7 | Improvised three times on one issue (`g1/g2/g4-review-result-2.md`), and flagged by the reviewer itself the third time. A missing engine shape, not a discipline failure. |
| 376 | 2d | CONSOLIDATE→K7 | K7 | Stale by construction: a gate that *adds* a test file cannot be certified by a fixed required-evidence list authored before it. Raised independently by both the implementer and the reviewer. |
| 377 | 2d | CONSOLIDATE→K11 | K11 | Self-described *"Quality only — no defect, nothing red."* Verified still growing: `wc -l scripts/map_orient.py` = **1732** at HEAD, up from the 1689 the body recorded. Its `self_test` bloat is also the cause of #364's lying reachability analysis. |
| 379 | 2d | CONSOLIDATE→K3 | K3 | The #305 negative control did its job and named exactly which fields are not mechanically capturable — `role` and `refusals` refuse at every child-gate seam, because the child gate plan is never claimed (#357). Downstream of #357. |
| 381 | 2d | CONSOLIDATE→K10 | K10 | The red-proofs ran against `49059be`/`fb9dfc2`; the shipped file is `667b5e4`. *"The shipped artifact had never itself been red-proofed."* Textbook K10. |
| 382 | 2d | CONSOLIDATE→K10 | K10 | Two measured holes in the **negative control** — *"the artifact whose entire purpose is to have no holes of this kind"* — including a guard whose own docstring claims coverage it does not have. |
| 383 | 2d | **ARCH-BLOCKING** | K2 | *"Zero readings across a multi-day run"*, with the engine saying so in plain text (`bound to 9 candidate spines at once`) and 30 bindings accumulated from never-released terminal leases. This is the measured, root-caused version of #271/#289/#295. |
| 384 | 2d | CONSOLIDATE→K10 | K10 | A **surviving mutant, measured**: deleting `"dirty": None` leaves 1487 tests green, while the module docstring explicitly justifies keeping it as a settled design decision. Nothing tests the decision. |
| 385 | 2d | CONSOLIDATE→K11 | K11 | Two prose copies of one measurement with no single source, which *"diverged during the very gate that created them"* and took three rounds to settle. Root cause of that gate's only BLOCK. |
| 386 | 2d | CONSOLIDATE→K11 | K11 | Two test-hygiene items, with an explicit warning not to "fix" the first by narrowing the token — mutation M3 proved the value-matching layer is the only one catching value-shaped reintroduction. |
| 387 | 2d | CONSOLIDATE→K11 | K11 | Speculative generality stated as settled: `repo_revision()` returns both halves justified by a *hypothesised* second caller, written in shipped prose in the register of a closed question. |
| 388 | 2d | CONSOLIDATE→K9 | K9 | Two crew-doctrine corrections from #305 g3/g4 — the spent-mutation rule should read *"not a repeat under the same conditions"*, and an exception-failing battery is broken, not a result. Doctrine edits. |
| 390 | 2d | **ARCH-BLOCKING** | K7 | A gate's `imperative` is frozen and re-emitted verbatim forever, with no op to mark a clause superseded — so a claim **measured false during the very gate it justifies** keeps being pushed to every agent that touches the gate. Directly contradicts B0.1's "everything between canon and active context is deterministic *and correct*". |
| 392 | 2d | **CONSOLIDATE→K10 (cluster seed)** | K10 | Found by the first live collation pass (#308) and *"deliberately left unconsolidated"* because that run was bound to land exactly one consolidation. It names the K10 cluster and rates it STRONG. This is the highest-confidence consolidation target in the backlog — a rhyme already found by the mechanism built to find rhymes. |
| 394 | 2d | **ARCH-BLOCKING** | K13 | Hit live running #307 *in this repo*, which has no `docs/architecture/`: `verify-frame` → `FRAME-REFUSED`, one problem per typed anchor, while `MISSION_FRAME.template.md` mandates those anchors. Two shipped surfaces contradict each other in the degraded mode that is this repo's normal state. Downstream of #156. |
| 395 | 2d | REAL-DEFECT | K4 | Measured: `constellation-commander/SKILL.md` has **0** 'map' hits while `COMMANDER_SPINE.template.json` has **4** `map_orient` hits — the shallow digest cannot see `templates/` or `scripts/`, where the map-first contract actually lives. Any corpus comparison on it is wrong in both directions. |
| 396 | 2d | CONSOLIDATE→K4 | K4 | Cost a full five-run capture set (~20 min, ~$50). A backgrounded process survived a compound command that reported failure, and two drivers raced into the same directories. The void set is preserved with evidence. |
| 397 | 2d | REAL-DEFECT | K4 | Adjudicated: **all five** reported forbidden operations were false positives — `git merge-base` matching `\bgit\s+merge\b`, and `Write` file *content* being pattern-matched as if executed. An instrument that cries wolf on read-only queries. |
| 399 | 2d | **ARCH-BLOCKING** | K3 | *"The code is not wrong. It is faithful to a model that has been superseded."* Tommy has ruled an episode is an **observation, not a diagnosis**, and the shipped record does the opposite in three places. The 'strength' half is RULED OUT by Tommy; the rest is open. B1's foundation. |
| 400 | 2d | **REAL-DEFECT (half stale)** | K3 | Verified at HEAD: the preamble still says *"Read the Active section at the Commander context step"* and *"enforces cap"*, and `grep DEFAULT_CAP scripts/apply_lessons_delta.py` returns nothing — so the cap claim is confirmed false. **But the second half of the title is now wrong:** the bank is *not* empty — four lessons are active (`falsify-a-check-against-a-decoy-before-trusting-it`, `a-verdict-must-not-select-on-the-gap-it-escalates`, `grading-a-contested-claim-settled-launders-it`, `reasoning-gate-crew-waiver-can-be-wrong-for-synthesis`). Rescope before working. |
| 401 | 2d | CONSOLIDATE→K4 | K4 | 15,456 files of host debris archived per run, and a filesystem witness that could not fail — *"no check would have caught either"*, found only because Tommy asked. Both defects reduce to one missing sentence: nobody declared which files belong to the run. |
| 402 | 2d | **ARCH-BLOCKING** | K5 | #307 proved the map-first effect **exists**; the magnitude is unattributable because the corpus moved 8 days and +31 files, not #304 alone. Everything needed for the clean arm is already on `main`. Without this, B3's headline result stays directional. |
| 403 | 2d | **ARCH-BLOCKING** | K1 | The acceptance guard for #308's read-path cut *"lives under a work-id directory and is archived with the run"* — nothing in `tests/` asserts it, and the guard had three demonstrated blind spots. Verified: the corpus still instructs the read (see #400). Textbook built-but-not-delivered. |
| 404 | 2d | **ARCH-BLOCKING** | K3 | The write path outlived the read path: #308 cut agents off from reading lessons, but the Commander spine's `feedback` step still tells agents to bank *"a lesson … you are carrying forward"* for re-observation, and nothing re-observes. **Confirmed live** — four lessons were banked into the Active section *after* #308 landed. The B1 loop is open at one end. |
| 405 | 2d | REAL-DEFECT | K3 | Verified corpus-wide by the filer: `git grep '"root": "durable"' -- skills/` returns **zero**. The token is retained with two silent traps on its resolution path and no shipped data exercising them. Filed as a decision, not a defect — treat it as one. |
| 408 | 0d | **ARCH-BLOCKING** | K6 | *"Contract pre-clearance and harness permission are two different systems, and only one of them can actually stop a command."* A verbatim-confirmed latitude contract did not bind the harness classifier, at the Admiral's own merge step. #145 recurring. This is the autonomy envelope failing at its boundary. |
| 409 | 0d | **REAL-DEFECT (reproduced)** | K8 | Verified at HEAD: `ls notes-*.md` returns **six** files — `notes-261, 269, 301, 304, 308, 309`. The doctrine names the file and never names a home, and nothing removes it. Supersedes #278. |
| 411 | 0d | REAL-DEFECT | K8 | `TREND_SNAPSHOT.md` §2 counts `_shared` as a 20th role while `install_constellation.py:245` and `README.md` both say it is not a skill — and the artifact *declares its own successor* and instructs it to re-run §1–§3 verbatim, so the error is built to propagate. |
| 412 | 0d | **REAL-DEFECT (high)** | K8 | Measured: `git for-each-ref --contains fc1685a` → empty, while #310's trend instrument uses that revision as a blocking baseline check. Garbage-collectible commits under a "pin numbers to a revision" rule. **This census found live exposure:** `governor/264-e2e-assertion` holds three unmerged commits with no PR. |
| 413 | 0d | **REAL-DEFECT** | K6 | 4/4 dispatches failed, reported in the agents' own words, every result relayed through the Admiral. Supersedes #294's evidence with a cleaner denominator; merge the two rather than working both. |
| 414 | 0d | **ARCH-BLOCKING** | K5 | B2 gate (b) is at **n = 0 — no evidence, not weak evidence** — and #310 established that this epic's relaunches cannot serve as evidence because every relaunched agent held the full monolith. The kernel-break decision cannot be made without this. |
| 415 | 0d | **CONSOLIDATE→K5 (do not re-derive)** | K5 | Tommy cut it 2026-08-03 as premature *in kind*: *"we're just reworking the substrate, we're not aiming to idealize any particular metric."* Nothing was deleted; the oracle-validated instrument is preserved on `epic-298/310` with `README-SALVAGE.md`. Keep as an inheritance record, not work. |

**Row count: 127.** Matches the census count of 127.

---

## 5. Proposed consolidation clusters

Ordered by what I would put in front of Tommy first. Each names its members, the one question it answers, and why the members belong together.

### K13 — Corpus reachability: is the corpus invoked at all? *(5 issues — #331, #136, #290, #346, #356; #156 and #394 feed it)*

**The question:** does any of this reach a working agent?

This is upstream of every other cluster. #331 measured **zero skill invocations across five runs** with the corpus installed and enumerated. #136 is the missing instrument that would have caught it. #290, #346, and #356 are three independent defects in the *trigger surface* — 12 of 19 skills fail the registration verifier, one skill's description never registers (reproduced first-hand in this session), and one skill's description states a limitation that measurement disproved. #156 (no `docs/architecture/`) and #394 (`verify-frame` refuses every anchor in degraded mode) are the same failure at the artifact level: the map-first contract shipped into a repo with no map.

**Why one cut:** fixing any one of these alone changes nothing measurable. Together they answer whether phase 1's deliverables are reachable at all — which is the precondition for reading any later measurement as meaningful.

### K1 — Built-but-not-delivered *(13 issues — #345 umbrella, #257, #328, #329, #330, #280, #281, #288, #291, #313, #363, #373, #403; #243 and #344 adjacent)*

**The question:** what else ships correct, tested, merged, and never runs?

#345 states the pattern with six instances in one epic, and item 1 is reproduced live in this census: `grep -rn "context_manifest" skills/` returns nothing. #329 is the sharpest instance — a working exit-code script guarding an invariant the corpus itself calls *"data loss, not friction"*, invoked by prose only, wired into zero spine templates (verified). #257 is the umbrella test-surface gap that let an entire inert Context Governor pass review. #288 is the governance version: the judge's code is protected, its registration is not.

**Why one cut:** these are not thirteen bugs, they are one missing acceptance question — *"what causes this to run, and what test fails if that wiring disappears?"* — asked thirteen times. A single mechanism (a wiring/reachability check that runs against the **installed** tree) closes most of the cluster.

### K2 — Context Governor: make it fire *(15 issues — #267 epic, #235, #264, #266, #270, #271, #274, #275, #281, #282, #284, #286, #287, #289, #295, #383, #214)*

**The question:** can a run of any length survive?

#383 is the measured root cause and it supersedes the older members: subagents share the parent `session_id`, so every crew claim adds a binding, terminal spines never release, 30 bindings accumulated, and the writer declined to guess — **zero readings across a multi-day run**. #284's table (four Commanders, four past HARD, one at 2.4x) is the cost. #274 is Tommy's stated requirement that this all points at.

**Why one cut:** #271, #289, and #295 are three partial views of what #383 measured whole — and #289 and #295 have **empty bodies (`@-`)**, so they cannot be worked as filed. Rebuilding this cluster from #383's evidence would shrink it substantially. This is also where the reworked backlog would most visibly get shorter.

### K3 — Episode store hardening *(14 issues — #399, #342, #318, #359, #404, #277, #319, #323, #343, #360, #361, #367, #368, #379, #400, #405; #285 resolves here)*

**The question:** is B1's substrate correct enough to accumulate on?

#399 is the head: *"The code is not wrong. It is faithful to a model that has been superseded"* — Tommy has ruled an episode is an observation, not a diagnosis, and the shipped record solicits diagnosis in three places. #342 (no `confirmed` lifecycle standing) makes a held prediction indistinguishable from an unchecked one. #318 means episodes silo per worktree under exactly the condition they were centralized for. #359 means an entire class of runs (every survey — Reviewer, Cartographer, Scout, Curator) emits no manifest. #404 is confirmed live in this census: **four lessons were banked after #308 cut the read path**, so the write path outlived its observer.

**Why one cut:** phase 1 built this store two weeks ago and it already has fourteen open corrections against it. Working them individually re-opens the same files fourteen times. One hardening pass against the ruled-but-not-implemented model (#399) would subsume most of them.

### K10 — A check that cannot register its own failure *(8 issues — #392 seed, #337, #292, #364, #372, #381, #382, #384)*

**The question:** how many of our guards would notice if the thing they guard disappeared?

**This cluster is not my invention** — #392 is a rhyme found by the first live collation pass (#308), rated STRONG, and deliberately left unconsolidated only because that run was bound to land exactly one consolidation. #337 independently tabulates the same shape appearing four times in one epic in four costumes. #384 is a measured surviving mutant (deleting a line leaves 1487 tests green). #381 is a red-proof certifying a file that never shipped.

**Why one cut, and why it is the best one:** it is the highest-confidence target in the backlog because the mechanism built to find rhymes already found it, wrote it down, and said so. Consolidating it is also a live test of B1 — if the episode store's first identified cluster cannot be consolidated, that is evidence about B1, not just about these eight issues.

### K7 — Engine, lease, and gate mechanics *(13 issues — #357, #369, #390, #315, #371, #374, #338, #358, #375, #376, #311, #220, #242)*

**The question:** does the engine's own state machine hold under the load epic-298 put on it?

#357 and #369 are the pair that let two agents into one worktree: the lease is on the parent while all the gates live in the unclaimed child, and no drill places any obligation on the *resuming* side. #390 is the sharpest doctrine defect in the backlog — an imperative's claim was **measured false during the gate it justifies** and there is no op to supersede it, so a disproven claim is pushed to every agent forever. #371 wedges a Commander toward fabricating a verdict.

**Why one cut:** #357, #369, #379, and the child-claim question are one design change (claim the child gate plan), not four fixes.

### K4 — Measurement methodology *(9 issues — #347, #349, #351, #352, #395, #396, #397, #401, #402-adjacent)*

**The question:** how do we run a measured arm without re-deriving its design every time?

Every member says, in its own words, that it *"will recur on every future arm"*. These are not defects in the tracker sense; they are a **methodology document that does not exist yet**.

**Recommendation:** this is the cluster where I would convert issues into a single artifact (a measured-arm playbook covering evidence standards, write boundaries, corpus identity, capture-rig scope, and false-positive adjudication) and close the issues against it — rather than carrying nine standing items.

### K5 — B2 kernel-break evidence *(3 issues — #414, #415, #402)*

**The question:** can the kernel-plus-fragments decision be made, and at what cost?

#414 establishes gate (b) is at **n = 0** and carries the design of the cheapest honest arm. #415 preserves gate (a)'s instrument after Tommy cut it as premature *in kind*. #402 would convert B3's magnitude from directional to attributable. All three are inheritance records so the next run does not re-derive.

**Recommendation:** keep all three, work none of them yet. They are correctly parked, and #415 records Tommy's reasoning for why.

### K6 — Harness capability limits *(7 issues — #408, #413, #294, #314, #222, #248, #260, #370)*

**The question:** which of our doctrine instructs agents to do things the harness refuses?

#408 is the most consequential: a latitude contract Tommy confirmed verbatim did not bind the harness permission classifier at the Admiral's own merge step. #413 and #294 are the same routing defect measured twice (4/4 and 5 rediscoveries) — **merge them**. #314 and #222 are doctrine instructing the impossible. #248 is Tommy's own ask for exactly this probe.

### K8 — Artifact and tracker hygiene *(8 issues — #354, #409, #412, #339, #411, #278, #298, #244)*

**The question:** does the tracker and the repo tell the truth about their own state?

#354 is now measured at **five instances** (its own two, plus #131/#208/#322 found here). #339 is 5-of-5 wrong by its own measurement, verified still present. #409 is six files (~79KB) on `main`, verified. #412 orphans commits under a rule that points straight at them, with live exposure found in this census. #244 is the human-instruction version and is arch-blocking because B1's durability premise rests on it.

**Why one cut:** it is cheap, it is entirely mechanical, and it is the cluster that most directly answers Tommy's stated concern about too many in-the-weeds issues — because several of these issues *are* the reason the backlog looks worse than it is.

### K9 — Curator-routed doctrine bundles *(8 issues — #117, #215, #221, #223, #259, #366, #388, #239)*

**The question:** which doctrine edits are queued and never batched?

#366 is the highest-value member and does not read like the others: three rules independently discovered to be **ordering** rules rather than content rules, each of which recurred after being written down. #259 item 1 is a data-loss hazard that fired for real and should be lifted out of the batch. #239 is half-done (verified) and should be rescoped to its surviving half.

### K11 — Code-shape cleanups *(6 issues — #272, #282, #377, #385, #386, #387)*

**The question:** none — these are quality items with no live wrong answer.

Every one is self-described as non-blocking. #377 is verified still growing (`map_orient.py` 1689 → **1732** lines) and has a second payoff: shrinking its `self_test` is what stops reachability analysis lying (#364).

**Recommendation:** one `/simplify`-class pass, or explicit deferral. Not individual issues.

### K12 — Unconfirmed design threads *(5 issues — #139, #233, #234, #219, #296, #297)*

**The question:** none yet — these are explorer intake.

#139, #233, and #234 all carry the literal marker `UNCONFIRMED — DO NOT CUT`. #219 is the salvage record for a retired ROADMAP (confirmed deleted). #296 and #297 are Tommy's own direction-setting notes, and #297 **contradicts shipped decisions** rather than extending them (*"markdown is kind of a shitty graph structure"* against the spec's Git-native-authored-truth commitment).

**Recommendation:** these should not be in the issue tracker's working set at all. They are ideas-board material, and #297 in particular deserves a deliberate reading against the confirmed spec before anything else is cut.

---

## 6. Recommended dispositions (recommendations only — the human disposes)

**Close as already done** (verified against the shipped tree, not against a claim):
- **#131** — journal sidecar + eval cross-verification merged at `51d14ef` via PR #133
- **#208** — worktree-root trio harvest is in `skills/admiral/SKILL.md:70`, merged at `7c8ff1b`
- **#322** — episode store is in the truth-layer taxonomy at `docs/CONSTELLATION_OVERVIEW.md:72`, fixed at `1dd83a1`
- **#298** — the epic is closed in the run record; the issue was not

**Close as duplicate / superseded:**
- **#278** → superseded by **#409** (same defect, six files vs two, fully enumerated)
- **#294** → merge into **#413** (same routing defect, cleaner denominator)
- **#285** → overtaken by #308's migration; confirm the episode carries the content, then close

**Rewrite or close as unactionable:**
- **#289** and **#295** — both have literally empty bodies (`@-`). Their titles name real shapes, and #383 supplies the evidence, but neither can be worked as filed.

**Rescope before working** (the issue is now partly false):
- **#400** — the "empty bank" half is wrong; four lessons are active. The "enforces cap" half is confirmed false.
- **#344** — the acute measurement (18 commits stale) is now 2; the defect class survives.
- **#239** — item 2 is done; only the two template `@grade` lines remain.

**Do not work yet, keep as inheritance:** #414, #415, #402 (K5) — correctly parked, with Tommy's reasoning recorded on #415.

---

## 7. Scoped nulls and what I could not determine

- **#289, #295 — UNCLEAR.** Both bodies are the single string `@-`. I checked the issue body via `gh issue list --json body`, and cross-read #383 (which measures an overlapping shape). I did not guess at intent; the titles are suggestive but an issue's title is not its scope.
- **Verdicts are one-per-issue by construction, and several issues legitimately sit in two clusters.** Where that happened I assigned the cluster that would *do the work* and named the other in the evidence line (e.g. #403 is both K1 and K3; #242 item 2 belongs with #313/#373).
- **"Arch-blocking" is judged against the confirmed grander-scale spec** (`.agent-work/archive/2026-07-31-explore-grander-scale/DESIGN_SPEC.md`, Stratum B B0–B4), not against a private notion of the target. Where an issue blocks a *conditional* element (B2), I said so rather than calling it a hard blocker.
- **I did not verify every issue against the tree** — that would be 127 reproductions. I reproduced or tree-verified 24 of them (#131, #156, #208, #239, #257-adjacent, #272, #281, #285, #290, #313, #322, #329, #339, #344, #345, #346, #354, #373-adjacent, #377, #400, #403, #404, #409, #412). The rest carry their filer's own measured evidence, which I quoted rather than re-derived; where a body asserted without measuring, the verdict says so.
- **I did not read closed issues #299–#310 in full**, only their titles and closure dates, since exc-1-epic298 owns the phase-1 delivery audit. Supersession claims here rest on tree state and merged commits, not on those issues' bodies.
- **Side-finding, outside the brief but material:** `git branch -a --no-merged main` shows **eleven** unmerged branches, one of which (`governor/264-e2e-assertion`) carries three real commits of #264 work with no PR. Under #412's orphaning hazard this is live exposure. Reported, not touched.
