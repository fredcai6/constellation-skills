# exc-1-epic298 — Phase-1 delivery audit

**Excursion:** `EXCURSION_BRIEF exc-1-epic298` (`.agent-work/explore-post-phase1/IDEAS_BOARD.md:29-36`)
**Question:** What did phase 1 (epic #298 + follow-ons #299–#310) actually deliver against its stated intent, and what did its closeout flag that bears on backlog consolidation or the next step?
**Type:** read-only research. Every claim below cites a file path, an issue/PR number, or a command run at `main` = `79db918` on 2026-08-03.

---

## VERDICT

**All 12 issues (#299–#310) were dispositioned and merged, and the two headline deliverables (B3 map-first, B1 lessons rework) landed with measured results. But three things the spec named as "done" were not delivered — one deliverable dissolved (#306), one was rescoped out at the human's instruction (#308's consolidation exercise), and the audit's own top-priority finding was never applied or filed. And the epic issue #298 itself is still OPEN on the tracker.**

The single most consolidation-relevant number: **74 of the 127 currently-open issues (58%) are numbered ≥313**, i.e. filed during this epic's window. The epic's own routing file already ruled that none of them blocks anything (`BACKLOG_ROUTING.md:96`).

---

## 0. SCOPE — what was and was NOT examined (scoped nulls)

**Examined in full:** `.agent-work/epic-298/EPIC_SUMMARY.md`, `ARCHITECTURE_RECONCILE.md`, `BACKLOG_ROUTING.md`, `LESSONS_AUDIT.md`, `STATE_NOTE.md`, `LATITUDE_CONTRACT.md`, `epic-298-body.md`; the archive at `.agent-work/archive/2026-08-03-epic-298/`; tracker state for all 270 issues; closing comments on #299, #302, #304, #305, #309; bodies of #306, #308, #414, #415; git tags, branches, and the epic's net diff.

**NOT examined:** the 453 KB `ADMIRAL_LOG.md` in full — I read the archived tail (final 25 entries) and ran ~8 targeted greps. Where I report "no instance found", that is not evidence of absence. I did not read `LESSONS_RUN_BRIEF.md`, `INTERROGATION_RECORD.json`, `prep-299-report.md`, `prep-302-report.md`, the 11 launch orders, or the `baselines/`, `preb/`, `post/`, `harvest/`, `context/`, `mechanical/` subdirectories. I did not read the 32 episode files' contents (only counted and grepped them). I did not verify per-issue authorship of the 85 issues numbered ≥313 — I inherit the routing file's caveat (`BACKLOG_ROUTING.md:12`) that this is an upper bound on the epic's output.

---

## 1. STATED INTENT

From `LATITUDE_CONTRACT.md:7-14` and the epic body (`epic-298-body.md:1`):

> One closed vertical slice proving Constellation skills can natively enter, consume, and improve a shared, observable knowledge substrate. Deliverables: the reworked one-framework lessons system (**B1**) and the Commander map-first tracer (**B3**), under the B0 principles. The **B2 kernel-plus-fragments break is CONDITIONAL** — decided at issue L (#310) on evidence gates, never assumed. B4 is not in this cut.

**Success Shape** (`LATITUDE_CONTRACT.md:17-23`): *"All 12 issues (#299–#310) dispositioned. Each testing pathway exercised at least once with its evidence paired for Tommy's verdict. Honest nulls are complete deliverables."*

The spec's own narrower "done" (`epic-298-body.md:28`) adds a requirement the Success Shape does not restate: a reworked lessons framework *"in which observation is collated before reaction — **exercised by at least one consolidation acting on a collated cluster, not just a full store**"*.

---

## 2. DELIVERED VS INTENDED — all 12 issues

Wave-letter → issue mapping derived from `epic-298-body.md:168-188` (waves A–L) against issue titles; confirmed for H by the constellation-key in #306's body (`issue:c312386d4b62:H`) and for J by `ADMIRAL_LOG.md:283,417`.

| Wave | # | State | Intended | Delivered | Verdict |
|---|---|---|---|---|---|
| A | 299 | CLOSED 08-01 | Choose dogfood corpus + task set; capture baseline runs | PR #334 merged `8de2faa`. 5 transcripts, rubric frozen at `a226642b` before any run. **Every run read source before the map; every run did read the map**; 3/5 reached it after 20+ tool calls | **DELIVERED + overdelivered** — produced the finding the issue was not cut for: **zero skill invocations across all 5 runs**, so an identically-instrumented POST arm would null by construction (#331) |
| B | 300 | CLOSED 08-01 | Projection generator + manifest, design-it-twice | 3-candidate panel, hybrid converged; revision identity = git blob OID of LF-normalised bytes | **DELIVERED** |
| C | 301 | CLOSED 08-01 | Episode record + durable store, design-it-twice | Store shipped; PR #320 portability fix, CI green on Python 3.12 | **DELIVERED** |
| D | 302 | CLOSED 08-01 | Invariant inventory under the two-bin rule (HITL, Tommy owner) | 16 catastrophic-class invariants at `prep-302-report.md`; **8 mechanism-owned / 8 prose-only**. Tommy ruled **no third bin; Assumption 6 stands, B0.3 unchanged** | **DELIVERED**, assumption 6 closed |
| E | 303 | CLOSED 08-01 | Exercise confirm-gate refusal | Closed with **zero comments** on the issue — evidence is elsewhere (not located in my scope) | **DELIVERED (unverified here)** — see §6 null |
| F | 304 | CLOSED 08-02 | Commander map-input contract: entrypoint, degraded mode, tripwired prose deletion | Contract landed in `COMMANDER_SPINE.template.json`; `scripts/map_orient.py orient` canonical (`CONSTELLATION_OVERVIEW.md:118`). Cold panel caught 15 findings; finding 6 would have deleted degraded-mode intake | **DELIVERED**, with the caveat that `skills/commander/SKILL.md` has **zero** occurrences of "map" (#393) |
| G | 305 | CLOSED 08-02 | Mechanical episode capture, with negative control | PR #389 merged `4cec87a`; PR #391 recovered 2 stranded commits. **Negative control earned its keep: severing the seam turns it RED 8/13** while #300's own tests stay green (reached-count 0). Eight successive commanders, 3 waivers | **DELIVERED** |
| H | 306 | CLOSED 08-01 | Mechanize the drift check: committed projection vs regenerated canon | **NOT BUILT.** Closed as an honest null: under `decision:manifest-lives-in-agent-work` the manifest is a per-run *output record*, not an input, so the staleness failure mode cannot occur; a check on it would fire on every legitimate doctrine edit (`ADMIRAL_LOG.md:299`) | **DISSOLVED** — legitimate under "honest nulls are complete deliverables", but a spec-named mechanism does not exist |
| I | 307 | CLOSED 08-02 | Map-first measurement, paired evidence (HITL) | PR #398 merged `19667a3d`. **`map_before_src` PRE 0/4 → POST 4/4.** `read_at_bootstrap` **0/4 in BOTH arms**. Tommy ruled **PASS** (`cfa2c40`) | **DELIVERED + measured**; limitation stated first — manipulation was 8 days and +31 files, not #304 alone |
| J | 308 | CLOSED 08-03 | *"First collated consolidation: rhyme-search, cluster, two-bin route, one change"* | **RESCOPED at Tommy's instruction** (`ADMIRAL_LOG.md:417`, *"rescope 308"*) to *"Migrate the lessons playbook into the episode store, and retire it."* Issue body now reads **"Explicitly out of scope: No consolidation. No graduations. No deletions."** PR #407 merged `a4934cb` | **SUBSTITUTED** — migration delivered; **the consolidation exercise the spec's own "done" required was not performed** |
| K | 309 | CLOSED 08-01 | Coherence sweep with seeded defects | PR #350 merged `967493c`. **Recall 4/4 (100%), noise 0/7 (0%)**; proved the instrument could miss; caught a *live* defect (#348) it was not seeded with | **DELIVERED** — the strongest measured result in the epic |
| L | 310 | CLOSED 08-03 | B2 gate evaluation: trends, role-competence test, kernel-break decision (HITL) | PR #410 merged `390ee90`, 64 files **all under `.agent-work/`, zero source changes**. **Verdict: `not-yet-earned`**, re-founded on gate (b) alone — n=0, gates conjunctive, so a conjunction with an unrun conjunct cannot close | **DELIVERED as a blessed "no"** — one of the two outcomes the spec explicitly blesses; **no break decided, the call is still Tommy's** |

**Score: 12/12 dispositioned and merged. 10 delivered as intended, 1 dissolved (#306), 1 substituted (#308).**

---

## 3. THE SPEC'S TESTING PATHWAYS — exercised vs not

`LATITUDE_CONTRACT.md:18` requires *"each testing pathway exercised at least once."* The spec names eight (`epic-298-body.md:143-150`):

| Pathway | Exercised? | Evidence |
|---|---|---|
| Map-first behavior (B3) | **YES** | #299 PRE arm + #307 POST arm; Tommy ruled PASS |
| Degraded mode and drift (B3/B2) | **HALF** | Degraded mode delivered in #304 (hash-pinned substitutes, `ADMIRAL_LOG.md:381`). **Drift check never built** — #306 dissolved |
| Tripwired deletion (B1) | **PARTIAL** | #304 carried "tripwired prose deletion" in its title and shipped; the *aggregate* corpus-size trend measure was cut as premature (#415) |
| Projection determinism (B2) | **PARTIAL** | #300 tests determinism. The spec's **second-environment clean-checkout rebuild** was #306's half and died with it |
| Episode capture (B1) with negative control | **YES** | #305; negative control RED 8/13 |
| Coherence sweep (B1) | **YES** | #309; recall 4/4, noise 0/7 |
| Two-bin routing + invariant inventory (B0) | **HALF** | Inventory done (#302, no third bin). **"Each consolidated cluster states its bin"** was never exercised — no consolidation happened |
| Confirm-gate refusal | **CLAIMED** | #303 closed; I could not locate the evidence within my scope |

**Three pathways are incompletely exercised, and all three trace to the same two events: #306 dissolving and #308 being rescoped.**

---

## 4. CLOSEOUT FLAGS — complete list, each with its source

### 4a. From `EPIC_SUMMARY.md` — "Open for you" (l.107-116)

1. **The kernel break** — undecided; *both* threshold and unit handed up. (`EPIC_SUMMARY.md:109`)
2. **The ablation arm (#414)** — declined with a cost estimate so the decline is attributable. A disposable single-role arm would make gate (b) genuinely runnable. **#414 OPEN.**
3. **`wip/clean-codebase`** — parked at `f704273`, verified present (`git rev-parse wip/clean-codebase` → `f704273006caf...`, dated 2026-08-02). *"It is a rebase, not a rescue"*: the skill itself does not conflict; two wiring files do, at +2 and +28 lines against `main`'s +469 of drift.
4. **`settings.json` unwired** — the Context Governor never fires; the gauge was silent for the entire multi-day run (#383). **Verified: `grep -c PostToolUse ~/.claude/settings.json` → 0.**

### 4b. The two findings the summary says constrain what gets built next (`EPIC_SUMMARY.md:37-56`)

- **You cannot decompose a role whose load surface you cannot compute.** Named reference tokens do not resolve inside their own role's directory — **10 of 21** as the commander measured it at `9a90298`; **29 of 46** when the auditor re-derived it independently at `cad1ec3`. Same finding, different denominator, because they tokenized differently.
- **There is no unit, not just no threshold.** `docent` ranks 1st by lines and 5th by bytes — the order fully reverses. `scripts/curate_corpus.py:49-50` carries `SKILL_WORD_TARGET = 400` beside `SKILL_LINE_HARD_FLAG = 500` with no stated relationship.

### 4c. From `LESSONS_AUDIT.md` — six promoted findings

| # | Finding | Named home | Applied? |
|---|---|---|---|
| 1 | `a-check-that-cannot-fail` graduated at crew tier, never at orchestrator tier | `skills/_shared/global-orchestrator.md` | **YES** (`466eafa`) |
| 2 | **You cannot decompose a role whose load surface you cannot compute** | `scripts/install_constellation.py` + `scripts/curate_corpus.py` | **NO — see §5.1** |
| 3 | Built-but-not-wired: green tests are not evidence a deliverable landed — a call site is | `IMPLEMENTER_HANDOFF.template.md` | **YES** — required "Wiring Grep" slot |
| 4 | Enumerate the blast radius of your own change | `skills/_shared/global-everyone.md` | **YES** |
| 5 | A terminal spine is not reachable work (3/3 commanders left work unreachable) | `COMMANDER_SPINE.template.json` `archive` step | **YES** — postcondition `c2b` asserting an open PR |
| 6 | Pin to a revision — and a squash-merge dissolves the pin | `skills/_shared/global-everyone.md` | **YES** |

The audit **dropped 39 issue numbers in seven named groups**, sums checked by `comm` rather than by eye (`LESSONS_AUDIT.md:226-292`). Largest group: **10 instrumentation findings** for a measurement apparatus that may never run again.

**Two things the audit recorded rather than routed, because they need no fix** (`LESSONS_AUDIT.md:303-308`): **every cold plan critic caught a blocking defect — ten for ten, no exceptions**, now the most convergent process evidence in the repo; and **pre-registration saved #310's verdict** — it committed to what *insufficient evidence* would look like before knowing whether evidence would exist.

**Deliberately not routed, as a null that does not discriminate** (`LESSONS_AUDIT.md:298-301`): ~75 issues generated in this repo, **zero inbound findings from three dogfood projects in the same window**. Either they hit nothing or the export path is never exercised — the sweep cannot distinguish these. *"It is a question, not a finding, and it needs an instrument nobody has built."*

### 4d. From `ARCHITECTURE_RECONCILE.md`

- **Verdict: no drift.** The recorded architecture describes the system as it stands. Done as a **direct Admiral check rather than a cartographer dispatch**, recorded as a reasoned scope decision on Tommy's steer *"I've got the distinct feeling we've over complicated a lot"* (l.3).
- **One thing surfaced and NOT reconciled:** six `notes-*.md` files at the repo root, half of everything tracked there, spanning two epics. Filed as **#409**. *"This is not an architecture drift — it is the absence of a declared home, which is why the reconcile finds it and cannot fix it"* (l.36).
- **Caveat carried forward, not resolved:** #393 established the map contract lives **only** in `COMMANDER_SPINE.template.json`; `skills/commander/SKILL.md` contains zero occurrences of "map" (l.26).

### 4e. From `BACKLOG_ROUTING.md` — the routing recommendation

Three-line recommendation (l.98-102):
1. **Pull forward exactly one: #395** (corpus fingerprint is blind to `templates/` and `scripts/` drift). **#395 OPEN.** The audit then *declined* to promote it, leaving it in the drop pile with a marker: *"if an arm is ever run again, fix #395 first"* (`LESSONS_AUDIT.md:245-251`).
2. **Route group C through the closeout lessons audit** — done; the audit ruled.
3. **Everything else is ordinary backlog and should be triaged against the Stratum A vision, not against its own severity.**

The file's own closing judgement (l.104) is the sharpest thing in it for consolidation:

> *"This epic's real output is the doctrine in C and the two measured results. The other ~65 issues are the sediment of producing those. **Triaging them by asking 'is this worth fixing?' one at a time will keep all of them.** Ask instead: which of these does the next arc actually walk through?"*

**The routing file also retracts two of its own claims in place** (l.3, l.18-33, l.56-58): "delivery is broken" (false by the time it was read — Tommy caught it) and "doctrine that earned its place" (the routing file does not get to pre-empt the audit). *"Pin a routing claim to the revision you measured it at, or it outlives its subject."*

### 4f. Self-reported defects (`EPIC_SUMMARY.md:79-104`)

*"I was the epic's largest source of defects. Roughly twenty of my claims failed against the tree, and every one was caught by the commander or panel I handed it to — never by me."* Three that cost directly: destroying the run log by fast-forwarding `main` (292 of 458 entries recovered); re-conflicting its own PR; **orphaning cited revisions twice, the second time within an hour of filing the issue about it** (#412).

---

## 5. CONTRADICTIONS AND GAPS FOUND — surfaced, not smoothed

### 5.1 The audit's #1 priority was never applied and has no issue — the biggest carry-forward

`LESSONS_AUDIT.md:320` calls finding 2 *"the one item here I would fix before anything else"* and *"a precondition on the work you are about to do."* Its named homes are `scripts/install_constellation.py` (emit a per-role **resolved load manifest**) and `scripts/curate_corpus.py` (name one unit or delete the constants).

- `ADMIRAL_LOG` (archived tail) records: *"All six audit graduations target DOCTRINE (`global-orchestrator.md`, `global-everyone.md`, `IMPLEMENTER_HANDOFF.template.md`, and `COMMANDER_SPINE.template.json`'s archive step)."* **Neither script is in that list.**
- The commit is titled **`doctrine(epic-298): graduate five audit findings`** (`466eafa`) — five findings, six clauses. The log's "six graduations" counts clauses, and that count masks that **finding 2 has no disposition at all**.
- **No tracker issue exists for it.** `gh issue list --search "load surface role-locally resolve"` returns only #298 itself; `--search "resolved load manifest installer"` returns only #101 (CLOSED, unrelated).

**This is the item the audit says blocks the B2 substrate rework, and it is currently owned by nobody and recorded nowhere except a closeout artifact.**

### 5.2 The epic issue #298 is still OPEN

`gh issue view 298` → `state=OPEN closedAt=null`. Meanwhile `git log` says *"close(epic-298): spine terminal, lease released — epic complete"* (`79db918`), `EPIC_SUMMARY.md:3` says *"12 of 12 issues closed"*, and the archived log's final entry says *"EPIC-298 COMPLETE."* All 12 child issues are genuinely CLOSED; **the epic issue itself was never closed.**

### 5.3 `ARCHITECTURE_RECONCILE.md` claims "This closes #322" — #322 is still OPEN

`ARCHITECTURE_RECONCILE.md:18`: *"**This closes #322**, which was the standing complaint that the taxonomy omitted it."* The **fix genuinely landed** — `docs/CONSTELLATION_OVERVIEW.md:72` carries `episodes/active/` + `episodes/retired/` and l.82 has the section. But `gh issue view 322` → **OPEN, with zero comments**. Nobody closed it or recorded the fix on it.

### 5.4 `EPIC_SUMMARY.md` is stale on the deployed corpus

The summary's headline (l.3) says *"Corpus deployed at `5c6d977` (`sha256:e8bac5a3`)."* `5c6d977` is **three commits behind `main`** and predates the doctrine graduations. The **actually installed corpus** is:

```
C:/Users/fredc/.claude/skills/CORPUS.json
  corpus_id     = sha256:3fb431a47d3c05c0bd2459b1e7340faf7ec4e01cfec318cf1ea74167d6db9aee
  source_commit = 466eafa589436f73bc1c09e27087fcca4531cd0e
```

The graduations **are** deployed — verified by grep in the installed tree (`"A check that cannot fail"` present in `constellation-admiral/references/global-orchestrator.md`; `"Pin a claim to the revision"` present across role `global-everyone.md` copies). The summary Tommy reads simply names the wrong revision, because it was written at 20:38 and the graduations landed at 20:51.

### 5.5 `EPIC_SUMMARY.md` routes the settings.json item to a CLOSED issue

l.115: *"`settings.json` remains unwired (#180)."* **#180 is CLOSED** (2026-07-19T01:15:22Z), well before this epic. The condition is real — `grep -c PostToolUse ~/.claude/settings.json` → **0** — but **the work has no open tracker item**, so the only place it is recorded is a closeout artifact.

### 5.6 Episode count discrepancy: summary says 23, the store holds 25 under that prefix

`EPIC_SUMMARY.md:21-23` claims *"23 episodes migrated — 20 lessons one-for-one, plus 3 of the run's own observations"* and *"Store now holds 32 active."*

Counted at `main` = `79db918`:
```
ls episodes/active/ | wc -l                          -> 32   (matches)
ls episodes/active/ | sed 's/-[0-9]*\.md$//' | uniq -c
    5 issue-304-g3   25 issue-308   2 issue-309
grep -ril "unknown" episodes/active/ | wc -l         -> 11   (matches the "11 unknowns")
```
**25 files carry the `issue-308` prefix, not 23.** `issue-308-024` and `-025` both landed in the same merge `a4934cb` and carry mechanical capture fields (`refusals: 4`), so they are plausibly two further run-observations — but the summary's stated arithmetic (20 + 3) does not reach 25. The "11 unknowns" figure checks out exactly; **its denominator does not.**

### 5.7 The cited-revision rescue worked — verified live

`LESSONS_AUDIT.md:220` flagged as urgent: *"tag `9a90298` before `epic-298/310` is deleted"*, because it is the revision #310's verdict pins its structural finding to.

**Verified done and pushed:**
```
git rev-parse verdict/310-endpoint^{commit}  -> 9a90298f165bf41d7d88aef50ea430de262ed5bb
git merge-base --is-ancestor 9a90298 origin/main -> exit 1   (still NOT on main)
git ls-remote --tags origin | grep verdict    -> both verdict/* tags present on origin
```
The revision remains off `main` and is held alive **only** by the pushed annotated tag `verdict/310-endpoint`. The evidence survives; it survives by one thread.

### 5.8 Retirement lifecycle exists but has never been exercised

`episodes/retired/` exists and contains **0 files**. Spec B1 (`epic-298-body.md:74`) requires *"consolidated, superseded, and stale episodes are retired by the same explicit policy discipline the corpus itself lives under."* Consistent with #308's rescope: no consolidation ran, so nothing has ever been retired.

### 5.9 The `strength` / `Diagnosis` migration Tommy ruled out is still outstanding

`LESSONS_AUDIT.md:267-270` notes *"applying the `strength` ruling is a data migration, not a schema edit."* Re-verified at `79db918`:
```
grep -rl "strength" episodes/active/ | wc -l      -> 32   (32/32)
grep -rl "## Diagnosis" episodes/active/ | wc -l  ->  7
```
Both fields solicit judgement by name — exactly what Tommy ruled out (*"the thing that is finding the episodes cannot make a call on the importance"*, #308 body). Carried by **#399, OPEN**.

---

## 6. DEFERRED AND ROUTED WORK — the complete list

### 6a. Explicitly deferred with a preserved artifact (filed at closeout)

| # | State | What was deferred, and why it is attributable |
|---|---|---|
| **414** | OPEN | **The ablation arm for B2 gate (b).** Declined with a full design + cost so the decline is attributable, not asserted-impossible. Carries two corrections #310 had to make first: this epic's relaunches are **not** gate-(b) evidence (every relaunched agent held the full monolith — the treatment was never varied), and *"you cannot test the break without building the break"* is **FALSE** (an ablation needs zero authoring of a decomposition). Spec: Commander, mid-spine step, ≥4 runs per arm, reuse `preb/discriminate.py` + existing `RUBRIC.md`, pre-register before any number exists |
| **415** | OPEN | **The corpus surface census.** Cut by Tommy mid-run as premature *in kind* — *"we're just reworking the substrate, we're not aiming to idealize any particular metric."* **Nothing deleted:** `measure_surface.py` (60 KB), `trends.json` (586 KB, 187 rows), `panel.json`, `test_measure_surface.py` preserved on branch `epic-298/310` with `README-SALVAGE.md`. **Passed its blocking external oracle** — reproduced `TREND_SNAPSHOT` §1 exactly on all four figures. **Treat `trends.json` as UNREVIEWED** — the second oracle (independent hand-recompute) never ran |

### 6b. Routed to the human, undecided

- **The kernel break itself** — `not-yet-earned` is a verdict on the *evidence*, not a decision on the break. Two questions handed up: threshold **and** unit.
- **`wip/clean-codebase`** at `f704273` — land as a PR or leave parked.
- **`settings.json` / Context Governor wiring** — Tommy's file by standing ruling (`STATE_NOTE.md:47`: *"Install ONLY — never `--wire-hooks`; `settings.json` is his"*). No open issue (§5.5).

### 6c. Routed to the backlog — the 39 dropped in seven groups (`LESSONS_AUDIT.md:245-288`)

State re-verified at 2026-08-03. All OPEN unless marked.

- **Group i — instrumentation for an apparatus that may not run again (10):** #331, #393 *(CLOSED)*, #402, #401, #347, #351, #356, #395, #397, #349. *Only bind if another measurement arm is run.* Marker: **fix #395 first if an arm is ever run again.**
- **Group ii — engine/concurrency defects carried by their own issues (8):** #357, #383, #315, #358, #330, #318, #359, #390. *Real bugs, all filed, none blocking.* The routing file names **#357 most consequential** (the lease does not protect the gates — four mutating verbs accepted from a session-less caller; it is why three agents ended up in one worktree) and **#383 most consequential to the Admiral role** (the gauge goes silent on exactly the runs that need it — anti-proportional to risk).
- **Group iii — stale doctrine / corpus contradictions; a Curator pass (4):** #336, #343, #313, #322 *(fix landed, issue still open — §5.3)*.
- **Group iv — local defects in this epic's own new code (7):** #360, #361, #342, #363, #403, #392, #399.
- **Group v — ordinary wiring debt (3):** #328, #329, #346. *Instances of finding 3's class; they get fixed by finding 3's mechanism landing, not one at a time.*
- **Group vi — closed or not findings (4):** #317, #327, #362 all CLOSED; #326 is a change, not a finding.
- **Group vii — small, unowned, cheap (3):** #314, #323, #409. **#409 is named the cheapest fix in the entire pile** — name a directory in one doctrine line — *"but it is housekeeping, not a lesson, and I am not going to dress it up as one."*
- **Folded into promoted rows, not dropped (2):** #339 rides with finding 6; #352 rides with finding 1.

### 6d. Filed by the epic but outside the audit's 39

#404, #405, #406 *(CLOSED)*, #408, #411, #412, #413. Of these, **#412** (deleting a squash-merged branch orphans every commit on it) is the one the Admiral committed twice within an hour of filing it, and **#408** (latitude pre-clearance does not bind the harness permission classifier) is the one that forced Tommy to run the merge himself.

---

## 7. WHAT THIS MEANS FOR BACKLOG CONSOLIDATION AND THE NEXT STEP

**1. The backlog is majority epic-298 sediment.** Counted by command at 2026-08-03:
```
gh issue list --state all --limit 400 --json number,state  ->  270 issues, 127 OPEN
  numbered >=313:  85 total, 74 OPEN
```
**74 of 127 open issues (58%) come from this epic's filing window.** The routing file's own conclusion (`BACKLOG_ROUTING.md:96`) is that **there is no group that blocks the others** — *"67 open issues from one epic, none of them blocking, is a debt pile."* That was 67 on 2026-08-02; it is 74 now. It grew by 7 during closeout.

**2. Both routing artifacts under-enumerate, in opposite directions** (`LESSONS_AUDIT.md:236-238, 331-333`). The audit unioned them rather than trusting either — 51 distinct numbers across both, 47 in the routing file alone. **Any consolidation pass that reads one artifact will be under-inclusive.** The audit's own first draft made the same error (29 items against a stated 41), which is why "enumerate the blast radius of your own change" became finding 4.

**3. The stated triage question is already written down, and it is not "is this worth fixing?"** — it is *"which of these does the next arc actually walk through?"* (`BACKLOG_ROUTING.md:104`). Applied mechanically that would drop groups i, ii, iv, v and most of vii unless the next arc is another measurement run.

**4. The one item that genuinely gates the next architectural step has no owner.** Audit finding 2 — the resolved load manifest and the unit question — is the named precondition on any kernel/fragment split, was ranked first by the auditor, was not graduated, and has no issue (§5.1). **If the next step is the substrate rework, this is the first thing to file.**

**5. Three closeout bookkeeping gaps are cheap and would otherwise mislead the next reader:** epic #298 not closed (§5.2), #322 open with its fix already landed (§5.3), and the settings.json item pointing at a closed issue (§5.5).

**6. Nothing in the epic foreclosed Stratum A.** #310 returned `not-yet-earned` rather than taking the break; the episode store is in the overview taxonomy as a truth layer; the reconcile found no drift. The idea-substrate half remains unbuilt and unblocked, as the spec required (`epic-298-body.md:28`).

---

## 8. NULLS — what I could not establish

- **#303's evidence.** The issue is CLOSED with zero comments and I did not locate its verification artifact. I did not search `.agent-work/epic-298/evidence/` or the launch orders. *This is a scoped null: not examined, not absent.*
- **Whether all 85 issues ≥313 were filed by this epic.** Not verified per-issue; 85 is an upper bound, inherited from `BACKLOG_ROUTING.md:12`.
- **Whether the two extra `issue-308` episodes (§5.6) are legitimate run-observations or a miscount.** I read their headers, not their bodies.
- **The full `ADMIRAL_LOG`.** 453 KB, ~449–458 entries. I read the archived tail and ran targeted greps. Patterns I did not find may still be there.
- **Whether the epic's inbound-findings asymmetry** (~75 issues here, zero from three dogfood projects) reflects the export path never being exercised. The audit explicitly declined to route this as a finding because the sweep cannot discriminate the two causes — and neither can I.
