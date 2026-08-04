# exc-3-episodes — episode store triage

**The one named question:** which stored episodes still carry live signal for the post-overhaul
corpus, and which are artifacts of the pre-phase-1 shape (superseded, already-harvested, or moot)?

**Answered:** 32 episodes enumerated, 32 verdicts. **23 carry live signal, 7 are already
harvested into shipped doctrine, 1 is superseded by a later measurement, 1 is moot-conditional.**
Read-only; no episode was edited, moved, or deleted.

Every number below is pinned to the working tree at `79db918` (`main`, clean at excursion start)
unless another revision is named.

---

## 0. What I looped over, and how I know it is complete

Three independent enumerations, all agreeing on **32**:

```
$ find episodes -type f | wc -l
35                                    # 32 episodes + README.md + 2 x .gitkeep

$ find episodes -type f -name '*.md' | wc -l
33                                    # 32 episodes + episodes/README.md (flat root, NON_EPISODE_FILENAMES)

$ python scripts/query_episodes.py enumerate | jq '.count'
32                                    # the store's own ordinary-search enumeration

$ python scripts/query_episodes.py enumerate --include-retired | jq '.count'
32                                    # history-inclusive: same set, so nothing is archived
```

`find` at **any depth** was used deliberately, not `episodes/*.md` — `docs/EPISODE_STORE.md` §7
names "a Markdown file one level deeper" and "a glob that misses a subdirectory" as two of its six
silent-omission traps. The three counts agreeing means neither trap fired here.

**The store's own tooling refuses a malformed store rather than answering it as empty**
(`docs/EPISODE_STORE.md` §7, `iter_episode_ids`). `query_episodes.py enumerate` exited 0 with a
populated `ids` array, so the store is well-formed as well as non-empty. That is a stronger
statement than "the glob returned 32 files."

**Composition of the 32**, by id prefix:

| prefix | n | what it is |
|---|---|---|
| `issue-304-g3-*` | 5 | native captures from #304 gate g3 (tripwired prose deletion) |
| `issue-308-001..020` | 20 | the **migrated** `LESSONS.md` playbook, one episode per lesson |
| `issue-308-021..025` | 5 | native captures from #308's own run |
| `issue-309-*` | 2 | native captures from #309 (coherence-sweep measurement) |

**Retired set: 0.**

```
$ find episodes/retired -name '*.md' | wc -l
0
$ ls -A episodes/retired/
.gitkeep
```

---

## 1. The framing that decides most of these verdicts

Two facts about how the store got its contents drive the triage, and neither is obvious from
reading an episode.

### 1a. The 20 migrated episodes were deliberately NOT dispositioned

`notes-308.md:248-263` — **"CORRECTION — #308 WAS RE-SCOPED. THE TABLE ABOVE IS OBSOLETE."**
The original g4 plan routed the 20 active lessons to GRADUATE (11), DELETE (4), and RETIRE-as-
already-graduated (3). Tommy withdrew it mid-run:

> **"Graduation and deletion are both withdrawn.** The correct disposition for every one of the
> 20 is now the same: *Migrate it into an episode. Record what is known; mark what is not as
> unknown.*" — `notes-308.md:256-260`

and `notes-308.md:345`: *"Every row is `MIGRATED`. There is no disposition column, because under
this scope there is no disposition to make."*

**So "was this lesson harvested?" cannot be answered from the migration — the migration
deliberately declined to answer it.** I answered it per-episode by grepping the shipped corpus
for the lesson's own remedy. That is why the evidence column below cites `skills/` and
`docs/agents/` paths rather than the migration table.

The withdrawal was on a stated principle, and it is load-bearing for this exploration:

> *"fundamentally the thing that is finding the episodes cannot make a call on the importance,
> that requires a more global view. it is not smart to ask our lower level agents to diagnose."*
> — Tommy, quoted in issue **#399**

**The importance call on these 23 live items is explicitly Tommy's, not an agent's.** I have
graded them by *unpaid-ness* (is the remedy in the corpus? does the mechanism still exist?) and
by measured recurrence where the record carries one — never by inventing a severity ranking.

### 1b. The epic-298 lessons audit enumerated the store but read one episode

`.agent-work/epic-298/LESSONS_AUDIT.md:23-24`, the auditor's own stated limitation:

> *"I enumerated the episode store (32 files: 5 × `issue-304-g3-*`, 25 × `issue-308-*`, 2 ×
> `issue-309-*`) and read one in full (`issue-308-021`). I did not read the other 31."*

**The store has never been harvested.** The one episode read (`issue-308-021`) became the evidence
for audit finding 4, which graduated. The other 31 were not assessed by the closeout that was
supposed to assess them. This excursion is the first read of the store as a whole, and that fact
is itself a finding: the closeout's coverage of the store was 1/32 by its own admission.

### 1c. The five graduations that DID land, verified present

Commit `466eafa` ("doctrine(epic-298): graduate five audit findings, authority=human"). I verified
each landed in the tree rather than trusting the commit message:

| finding | landed at | verified |
|---|---|---|
| a check that cannot fail — orchestrator tier | `skills/_shared/global-orchestrator.md:94` `## A check that cannot fail` | ✅ incl. mechanical detector at `:102` |
| liveness clause | `skills/_shared/global-orchestrator.md` `## Idle subagent adjudication` | ✅ |
| enumerate the blast radius of your own change | `skills/_shared/global-everyone.md:136` | ✅ |
| pin a claim to the revision; squash-merge dissolves the pin | `skills/_shared/global-everyone.md:149-163` | ✅ |
| Wiring Grep slot | `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md:66` | ✅ |
| archive `c2b` — an open PR must exist | `skills/commander/templates/COMMANDER_SPINE.template.json:123` | ✅ |

Plus three that graduated earlier, at **#308 gate g1**, into `docs/agents/CREW_CONTEXT.md:78-97`
(crew tier): *a check that cannot fail*, *define a guard by its consumer's behaviour*, and
*a round-trip test proves the artifacts, not the tool*.

Those nine landings are the entire "already-harvested" evidence base. Everything else in the store
is unpaid.

---

## 2. Per-episode verdicts

Verdict vocabulary: **live-signal** (remedy absent from the corpus AND the mechanism still exists,
both checked by command) · **already-harvested** (content is in shipped doctrine, path cited) ·
**superseded-by-X** · **moot** (conditional or otherwise).

### 2a. `issue-304-g3-*` — native captures, #304 gate g3 (5)

| id | one-liner | verdict | evidence |
|---|---|---|---|
| `issue-304-g3-001` | A handoff enumerated *the suites* that pin a file; it enumerated suites, not assertions — two out-of-scope test files broke on the deletion. | **already-harvested** | Its `d2` (grep the deleted phrases corpus-wide, treat every hit as a pin) is the authoring-side blast-radius rule graduated at `global-everyone.md:136`: *"before you call a change done, enumerate by command — never by memory — every artifact that asserts something about what you changed."* Residue: it is also a **cluster-A member** (see `issue-308-022`), and that cluster never consolidated. |
| `issue-304-g3-002` | 172 words of dead-path prose deleted from two shipped templates; an execute plan instantiated from the edited template advanced `e0-context` first try, `exit 0`, with the narrated `config_ref` absent from disk. | **live-signal** — *design input, not an unpaid defect* | #304 is CLOSED and this was its acceptance evidence, so nothing here is owed. But it is the cleanest empirical datum in the store for the substrate rework: prose narrating a mechanism the code already implements is **load-free by construction** (`d1`), measured on a real driven engine rather than argued. `grep -rn 'narrates a mechanism\|dead-path' skills/_shared/ docs/agents/` returns nothing — the generalization has no doctrine home. |
| `issue-304-g3-003` | The handoff said gate g2 had already retargeted a phrase; git history over all 8 commits touching the file showed it byte-identical throughout. **Reading the current file would have CONFIRMED the false claim.** | **live-signal** | `global-everyone.md`'s verify-claims clause says *"confirm it at its source — read the file"*, which is precisely the move that fails here: the question is about **history**, and the current file agrees with the lie. `d2`'s remedy (`git log --format=%h -- <file>`, then `git show <sha>:<file>` per commit, printing the phrase under test) is in no shipped artifact. Cluster-A member. |
| `issue-304-g3-004` | Dead prose and a live rule shared a distinctive phrase, so a naive string delete would have removed both — the deletion script refused rather than leaving the invariant to the test suite. | **live-signal** — narrow | `d2`: *"pin a deletion in BOTH directions — dead text absent AND the survivor present, because an absence-only assertion passes just as happily on an emptied field"*, plus *"put the invariant in the editing tool as a refusal, not only in the test that runs afterwards."* `CREW_CONTEXT.md:78-97` covers vacuity and adversarial fixtures but carries neither the bidirectional-deletion pin nor refuse-in-the-tool. |
| `issue-304-g3-005` | Whether re-anchoring the context imperative moved orientation ordering was **NOT DETERMINABLE** at that gate — a receipt check can prove orientation *happened*, never that it happened *first*. | **superseded-by #307** | #307 CLOSED, verdict PASS (Tommy, 2026-08-02): `map_before_src` **0/4 → 4/4** on content-identical briefs with byte-identical scorers, measured from run transcripts under both anchors — exactly the forward requirement `a5` stated and exactly `d2`'s first option (*"measure ordering where it is observable — a run transcript"*). The insufficient-vs-irrelevant question this episode raised is answered. Residue: it is a **cluster-B member** (`issue-308-023`) for the self-measurement shape, which #392 still carries. |

### 2b. `issue-308-001..020` — the migrated `LESSONS.md` playbook (20)

Provenance per row is `notes-308.md:348-372`. Every "live-signal" verdict below was reached by
grepping the shipped corpus for the lesson's own remedy and finding nothing, and by confirming the
mechanism still exists in current code.

| id | origin | one-liner | verdict | evidence |
|---|---|---|---|---|
| `issue-308-001` | epic-178 | A concurrency test hung the whole pytest process: a writer thread died on a Windows `os.replace` sharing violation without signalling stop, leaving a non-daemon reader spinning. | **live-signal** — narrow, reference-grade | Workaround (`try/except` with a guaranteed stop-signal in `finally`, `daemon=True` as backstop) is applied in the one test and written down nowhere. `grep -rn 'daemon=True\|sharing violation' docs/agents/*.md skills/_shared/*.md` → no hits. A durable platform fact with no home. |
| `issue-308-002` | epic-198-burndown | The launch order's named defect/edit-target did not exist as described — **six confirmations across three epics in five distinct failure modes**, never disconfirmed. | **live-signal — the strongest unpaid item in the store** | *"the most-confirmed entry in the bank and never disconfirmed"* (mentions 9 / confirmed 6, last confirmed 2026-08-01). `grep -rn 'named defect\|premise\|already shipped' skills/commander-delegated/` → **no hits**; nothing in `skills/` carries it. It is unpaid for a traceable reason: the g4 table held this exact row back for a `g6` consolidation, and `notes-308.md:267-269` records *"There is no `g6` now — the consolidation is withdrawn."* **It fell through the cutover.** |
| `issue-308-003` | epic-198-burndown | A discovery channel printed from a `finally` block could not survive the kill-or-hang it existed to observe — a hard Windows tree-kill skips `finally`. | **live-signal** — narrow | Remedy (a child-scoped `TMP`/`TEMP` written *before and independently of* the death) is in no doctrine file. `impact-cost` is UNKNOWN — the record says an **unknown** recurrence count, not an absent one (`notes-308.md:303-307`). |
| `issue-308-004` | epic-198-burndown | Injected-`cwd` fixtures pass green even if production never delivers the field; a later confirm found **presence and liveness are different questions** — `cwd` was present but session-fixed, not per-call-live. | **live-signal** | Five confirmations, last 2026-07-27. `grep -rn 'real writer path\|hand-injected\|drive the REAL' skills/ docs/agents/` → no hits. Rhymes with the graduated orchestrator liveness clause but is a different subject (harness field liveness, not subagent idleness), so the graduation does not cover it. |
| `issue-308-005` | epic-226-lessons-audit | 18 green tests over the real shipped artifacts while a greedy regex silently PASSED an ungraded decision — round-trips prove the artifacts, not the tool. | **already-harvested** | `docs/agents/CREW_CONTEXT.md`: *"A round-trip test over the real shipped artifacts proves the artifacts are clean — it does not prove the tool is correct. Pair it with adversarial fixtures authored to make the tool return a wrong answer."* Verbatim match to `a5`. Graduated at #308 g1; the g4 table's row 5 already called it *"already graduated at g1."* |
| `issue-308-006` | epic-226-lessons-audit | `checklist_engine advance --from-child` refuses a relative path (unlike every other verb) and only works against a SURVEY child; neither rule is in `--help`, the doctrine, or the refusal message. | **live-signal** — mechanical debt, unpaid upstream fix | Verified still true: `scripts/checklist_engine.py:1684` raises `child {from_child} has no consolidation yet` — **naming neither rule** — and `:2331`'s `--help` string says only *"child checklist file; attach its consolidation as review-result first."* Two independent worktrees hit it in one wave; status `exported` 2026-07-24, fix unpaid. |
| `issue-308-007` | epic-226-lessons-audit | Nothing mechanically checks the harvest before a worktree sweep; a staged trio that passes its own feedback gate looks identical to one merged into the durable log. | **live-signal — high, with a real near-loss** | f1Brainz epic-601: **6 of 6 staged trios were the sole surviving copy** of their worktrees' learning, caught by a human. Verified the named upstream fix is still unbuilt: `grep -n 'harvest' scripts/verify_agent_feedback.py` → **zero matches**. Only the prose workaround (write HARVEST EXECUTED/MANIFEST before any sweep) stands between this and a repeat. |
| `issue-308-008` | epic-226-lessons-audit | **Every run that ran the cold plan critic found a plan-invalidating defect before any crew was dispatched** — wt-227, wt-230, 300, 299, issue-309, and #308 itself. | **live-signal — high** | Remedy is *"run the cold plan critic as MANDATORY rather than bias-to-yes for any gate plan whose acceptance depends on a before/after measurement or a required round-trip or parser test."* Verified **not applied**: `skills/commander/references/commander-core.md:126` still describes both rigor mechanisms as **"bias-to-yes with any skip surfaced as a named untaken road."** Independently corroborated by the closeout: *"every cold plan critic caught a blocking defect — ten for ten, no exceptions, which is now the most convergent process evidence in this repo"* (`LESSONS_AUDIT.md:303-306`) — which the auditor **recorded rather than routed**, so nothing changed. |
| `issue-308-009` | epic-226-lessons-audit | On Windows, `subprocess.run(env={'PATH': ...})` does not control executable resolution — `CreateProcess` resolves against the *calling* process's environment, so the test passes silently even when the probe is broken. | **live-signal** — narrow reference fact | Established empirically with two pasted transcripts. `grep -rn 'CreateProcess\|os.environ' docs/agents/*.md skills/_shared/*.md` → no hits. A platform invariant that will stay true; homeless. |
| `issue-308-010` | epic-226-lessons-audit | A gate postcondition that must prove a command *correctly fails* has no direct expression in the engine's exit-0-is-pass semantics, so it degrades to a self-reported attest. | **live-signal** — narrow | Workaround (`! <command>` bash-negation as the postcondition `command`) confirmed once in #303 with verbatim exit codes. `grep -rn 'negation\|! <command>' skills/ docs/agents/` → no hits. Note the corpus now *uses* an equivalent trick unwritten: `COMMANDER_SPINE.template.json:123`'s new `c2b` uses `--jq 'length > 0'` truthiness rather than negation, so two idioms for "prove a condition" now coexist undocumented. |
| `issue-308-011` | epic-226-lessons-audit | A launch order fenced a contended file; resolving the canonical target first made the contended edit unnecessary — the collision dissolved rather than being resolved. | **live-signal** — narrow, single occurrence | Remedy (resolve canonical routing first; qualify stop-conditions with *"if the edit is still required after canonical routing"*) is in no launch-order template. Unknown recurrence count, 8 runs since. |
| `issue-308-012` | governor-261 | `_gauge_path` keys purely off the checklist file's containing directory, so a dispatched crew's plan file resolved to the **Commander's own gauge** — two dispatch attempts lost to a HARD Governor trip before any work. | **live-signal** — mechanical defect, still present | Verified: `scripts/checklist_engine.py:1173` is still `def _gauge_path(base_dir: Path | None)`, keyed on the directory. Posted to **#266**. The workaround (put crew plan files in their own subdirectory, mirroring `<gate>-review/`) is convention, not enforcement. |
| `issue-308-013` | governor-261 | A reviewer could not do the standard OLD-vs-NEW repro — the permission classifier correctly blocked it editing the artifact under review. | **live-signal** | The reviewer improvised a genuinely better technique (load the real module by file path with `importlib`, define the OLD handler inline as a local function, reuse the same real helpers) and **explicitly recommended promoting it as the documented default**. Verified not promoted: `grep -rn 'importlib' skills/reviewer/ docs/agents/` → **zero hits**. Cheap, concrete, and the recommendation is a year of reviewer friction away from being paid. |
| `issue-308-014` | governor-268 | A regression drill reported PASS for a doctrine pattern while a sibling template carried the identical unfixed defect, because the drill names only one sibling. | **live-signal** | The instance was fixed (`skills/admiral/references/fleet-doctrine.md:57` now points at `STATE_NOTE.template.md`), but the **method** was not: `docs/superpowers/drills/dogfood-context-paths-absent.md:3` still reads *"Lesson / doctrine under test: `skills/commander/templates/COMMANDER_SPINE.template.json`"* — one template, no sibling enumeration, no note of what it does **not** cover. This is `#319`'s *fix-the-instance-not-the-method* in miniature, still open. |
| `issue-308-015` | governor-265 | A lightweight design-it-twice pass (2 candidates) plus one solo cold critic caught a blocking design gap before the implement gate, on a run that had judged a full panel unnecessary. | **live-signal — but a consolidation candidate, not a standalone** | Its own g4 row proposed DELETE with the reason *"subsumed by #8; keeping both graduates one rule twice"* (`notes-308.md:223`). Under the re-scope it survived as a separate episode anyway. **Merge into `issue-308-008` rather than route separately** — they are one rule about critic floors at two weights. |
| `issue-308-016` | governor-265 | The reviewer's `r6-fowler` step says *record the pass to `templates/FOWLER_PASS.template.json`* — read literally, that means overwriting the shared skill template rather than filling a per-run working copy. | **live-signal — cheapest fix in the store, and its own routing claim is wrong** | Verified the ambiguous wording survives verbatim in **two** places: `skills/reviewer/SKILL.md:44` and `skills/reviewer/templates/REVIEW_SURVEY.template.json:52`. **The episode misroutes its own fix**: it says *"the named target is upstream of this repo — the installed constellation-reviewer skill's r6-fowler wording, not a file this repo owns."* That was a delegated-mode reading of the *installed* copy; the **source** is `skills/reviewer/` in this repo. The fix is local, one-line, and has been sitting behind a false "not ours" label. |
| `issue-308-017` | 301 | A hand-maintained character list stood in for a predicate the parser already computes: a `U+2028` value passed validation and forged the exact status line the guard existed to prevent. | **already-harvested** | `docs/agents/CREW_CONTEXT.md`: *"Define a guard by its consumer's behaviour, not by a hand-maintained list. A list of characters, filenames or call sites drifts from the predicate the code actually applies, and the gap is silent."* Direct match. Graduated at #308 g1. |
| `issue-308-018` | 301 | A design panel varies what it is told to vary and **inherits everything it is not** — all four #301 candidates inherited a false `.agent-work/`-is-gitignored claim from prior art; #300's audit retracted a "convergence" that was the brief handed back. | **live-signal — and it binds a standard this corpus ships** | Remedy: *"run a shared-assumption audit over the panel's convergences, by an auditor who did NOT author the brief, and treat unanimity across deliberately-differing constraints as evidence about the varied axis only."* Verified absent: `grep -rn 'shared-assumption\|inherits what it was not told' skills/` → **zero hits**, and `skills/_shared/design-it-twice-brief.md` has no such step. The corpus ships design-it-twice as a tier-wide standard and its convergence-reading has a known, measured failure mode that the standard does not mention. |
| `issue-308-019` | 301 | Five-plus instances in one epic of checks whose output is identical in the healthy and the defective world. | **already-harvested — both tiers** | Crew tier: `docs/agents/CREW_CONTEXT.md:78-97` (#308 g1). Orchestrator tier: `skills/_shared/global-orchestrator.md:94` `## A check that cannot fail`, incl. `:102` *"any guard that loops must assert what it looped over"* (`466eafa`). **Named residue:** the graduated corollary is *"a check that runs against your own working copy is not a check on the world"* — the **self-measurement** shape (instrument operated by the party whose work it measures) is a different shape and is carried by neither text. That residue is `issue-308-023` / **#392**, still open. |
| `issue-308-020` | 301 | A description accurate when taken and wrong when used comes in **two shapes with different fixes**: shape 1 yields to verification, shape 2 (two agents sharing a fact neither can see the other write) does not. | **live-signal on shape 2 — and the warned-against failure has now occurred** | Shape 1 is now covered by `global-everyone.md`'s *"Verify claimed side-effects"* plus the new *"Pin a claim to the revision you read it at"* (`466eafa`). Shape 2 — the epic-298 Admiral's fork resolution naming a slug *after* it had been renamed, caught only by comparing the live staged file — is uncovered. **The episode's author explicitly warns against graduating shape 1 alone and considering the class closed**, which is precisely the state the corpus is now in. Remedy (a quote-id-and-count protocol; compare the live staged file before harvest) is unwritten. |

### 2c. `issue-308-021..025` — native #308 captures (5)

| id | one-liner | verdict | evidence |
|---|---|---|---|
| `issue-308-021` | While planning the consolidation of *under-inclusive enumeration taken as complete*, the commander committed that exact failure twice in ~1 hour: enumerated 5 intake sites where a command finds 6, then wrote a guard whose character class excluded `.` so it went green against three live sites. | **already-harvested** | The **only episode the epic-298 auditor read in full** (`LESSONS_AUDIT.md:24`) and the named evidence for audit finding 4 (`LESSONS_AUDIT.md:145-149`). Graduated twice: `global-everyone.md:136` (blast radius, authoring side) and `global-orchestrator.md:102` (assert what you looped over). |
| `issue-308-022` | **Cluster A**, found by an independent cold rhyme-search sensor: *a written secondhand claim about current repo state was taken as a premise, was wrong, and only re-deriving it by command caught it.* Members: `issue-304-g3-001`, `issue-304-g3-003`, `issue-309-002`. | **live-signal — as an unconsolidated cluster record** | No consolidation landed: *"Tommy withdrew the bin ruling, and deciding which observation deserves a doctrine line is the importance judgement he ruled requires a global view."* Carries a **measured fact this exploration can use**: a mechanical doc-transcript checker would have caught **1 of 3** members; a prose instruction addresses **3 of 3**, and each member's own remedy independently converged on a variant of that sentence. The cluster rediscovered `lesson:verify-launch-order-claims-against-code` (= `issue-308-002`) by a different route with no access to `LESSONS.md` — **two independent paths to the same unpaid rule.** |
| `issue-308-023` | **Cluster B**, found by the same cold sensor and **missed by the commander's solo read**: *a check reports without being able to register the outcome it is credited with detecting, and the instrument was operated by the party whose work it measured.* Members: `issue-304-g3-005`, `issue-309-001`. | **live-signal — filed and open** | **#392 OPEN** (*"consolidation candidate: 'a check that cannot register its own failure', found and deliberately deferred by #308"*). Adds a shape the graduated `## A check that cannot fail` text does not carry: **self-measurement**. Also carries a fact about the rhyme-search pathway itself — *one read is not enough to trust a null on any individual cluster*; the solo read had filed `issue-304-g3-005` as a singleton. |
| `issue-308-024` | A frozen `execute.json` survived a mid-run re-scope with **two checks wrong in opposite directions**, neither of which would have announced why; both were corrected through `amend` rather than waived, and both replacements verified RED first. | **live-signal** | `skills/commander/references/commander-core.md:46` carries *amend-not-hand-edit* and names `add`/`drop`/`rescope` — but **not `retext-check`**, and says nothing about **correct-vs-waive** or **verify the replacement RED before doing the work that turns it green**. The episode's own framing: *"a waived check stays in the tree asserting the old rule; a corrected one becomes the acceptance test the gate actually needs."* Adjacent to **#390** (dropped in the audit's group ii as a one-line `imperative`-assignment gap in the same verb). |
| `issue-308-025` | A handoff stated 5 occurrences where the file holds 6 — **the third under-inclusive enumeration inside issue #308 alone, by two different agents**. Cost was zero because the handoff also said *verify by content, not by count*. | **already-harvested, with a named residue** | Covered by the same two graduations as `issue-308-021`. **Residue:** the graduated text addresses the **author** (*enumerate what you touched*); this episode's actual save came from an instruction aimed at the **downstream reader** (*verify BY CONTENT, naming each item that must survive, so a wrong total cannot become a wrong action*). *"The count was wrong and the work was still correct, because nothing depended on the count alone."* That reader-side half is not in the graduated clause. |

### 2d. `issue-309-*` — native captures, #309 (2)

| id | one-liner | verdict | evidence |
|---|---|---|---|
| `issue-309-001` | Coherence-sweep instrument validation: recall 4/4 (100%), real-viewpoint noise 0/7 (0%), with both the miss control and a raise-then-reject demonstrated — but *"a null is not a demonstration"*, and the 0% noise measures **lens discipline**, not an absence of noise risk. | **moot — conditional on another measurement arm** | Its `d2` (seed a decoy the target lens's own guardrail does not already name as an exclusion) binds only if another coherence sweep is designed. `LESSONS_AUDIT.md:245-251` group i drops exactly this class — *"instrumentation for a measurement apparatus that may not run again… the rework is the live work"* — with a stop-condition: **if an arm is ever run again, fix #395 first.** Consistent with Tommy's cut of the trend census as premature during substrate rework. Residue: it is a **cluster-B member** (#392), and that membership is live independently of any future arm. |
| `issue-309-002` | `docs/EPISODE_STORE.md` §1's worked `git check-ignore` transcript claimed `.agent-work/` was ignored — true when written at #301, invalidated by #326 — and the plan's first draft inherited the false premise. | **already-harvested** | Remedy applied and the issue closed: **#348 CLOSED**, and `docs/EPISODE_STORE.md:33-45` now carries an explicit correction — *"What changed, and why the ruling survives it… nobody revisited this paragraph. Issue #348 tracks it; the numbers above are pinned to `4cec87a`."* Residue: **cluster-A member**, and it is the only one of the three whose defect a mechanical doc-transcript checker could have caught. |

---

## 3. Counts, derived from the table above

| verdict | n | ids |
|---|---|---|
| **live-signal** | **23** | `304-g3-002`, `304-g3-003`, `304-g3-004`, `308-001`, `308-002`, `308-003`, `308-004`, `308-006`, `308-007`, `308-008`, `308-009`, `308-010`, `308-011`, `308-012`, `308-013`, `308-014`, `308-015`, `308-016`, `308-018`, `308-020`, `308-022`, `308-023`, `308-024` |
| **already-harvested** | **7** | `304-g3-001`, `308-005`, `308-017`, `308-019`, `308-021`, `308-025`, `309-002` |
| **superseded** | **1** | `304-g3-005` (by #307's POST arm) |
| **moot (conditional)** | **1** | `309-001` (unless another measurement arm runs) |
| | **32** | matches the enumeration in §0 |

**The headline for the exploration: 23 of 32 are unpaid, and only 3 of the 7 harvested ones were
harvested by phase 1's own closeout.** The other four (`308-005`, `308-017`, `308-019` at crew
tier, plus `309-002`'s doc fix) graduated *during* #308 and #348, before the store existed as a
thing anyone read.

**Almost nothing here is an artifact of the pre-phase-1 shape in the sense the brief anticipated.**
The store was built in phase 1 (#301), so no episode predates it. What the 20 migrated episodes
carry is *content* from pre-phase-1 runs (epic-178, epic-198-burndown, epic-226, governor-261/265/268,
301) — and that content is overwhelmingly still true, because it describes mechanisms that still
exist. I verified the mechanism was still present for every live-signal verdict rather than
inferring it from the record's age.

**Within live-signal, four items are separable by measured recurrence** (their own records, not my
ranking): `308-002` (6 confirmations, never disconfirmed, and independently rediscovered by the
cold sensor as cluster A), `308-008` (every run that ran it found a blocking defect; the closeout
independently measured 10/10), `308-007` (one near-loss of 6/6 worktrees' learning), and `308-018`
(binds a standard the corpus ships). The remaining 19 are single-occurrence or unknown-recurrence
records — which under the re-scope means **the count is empty, not that the record is invalid**
(`notes-308.md:303-307`).

---

## 4. Four store-wide findings that no single row carries

### 4.1 Every episode carries a field Tommy has ruled out (#399, OPEN)

```
$ grep -c '^- strength:' episodes/active/*.md | awk -F: '{s+=$2} END {print s}'
173
$ grep -l '^- strength:' episodes/active/*.md | wc -l
32
$ grep -l '^## Diagnosis' episodes/active/*.md | wc -l
7
```

**173 `strength` values across 32/32 episodes**, and **7 `## Diagnosis (optional)` sections** — and
those 7 are exactly the 7 natively-captured pre-#308 episodes (`issue-304-g3-001..005`,
`issue-309-001`, `issue-309-002`). #308 wrote **zero** diagnosis bins on all 23 it created, on the
stated reason that `suspected-cause`/`proposed-remedy` *"name the subject and thereby solicit a
confident one-run guess, which is the exact shape Tommy ruled out"* (`notes-308.md:407-409`).

#399 carries the measurement that makes this concrete:

| authoring population | strong | medium | weak |
|---|---|---|---|
| #308's 25 episodes (125 assertions) | 109 (87%) | 1 (1%) | 15 (12%) |
| the 7 pre-#308 episodes (48 assertions) | 32 (67%) | 15 (31%) | 1 (2%) |

*"The same required field produced opposite degenerate distributions from two authoring
populations. A field whose distribution is set by who is filling it rather than by the episodes is
not measuring a property of the episodes."*

The closeout audit reached the same place from the other side (`LESSONS_AUDIT.md:266-270`, group
iv): **"applying the `strength` ruling is a data migration, not a schema edit."** Any consolidation
of this store has to decide what happens to 173 values and 7 sections first.

### 4.2 The store's archive half has never been exercised

**0 retired episodes.** `docs/EPISODE_STORE.md` §7 specifies a ratified file-move retirement layout,
four named seams (`apply_retirement`, `destination_for`, `resolve_episode_path`,
`is_episode_in_ordinary_search`), half-retirement fault injection, and six named silent-omission
traps. All of it is tested (`tests/test_episode_store.py`) and **none of it has ever run against a
real episode**, because retirement was #308's g7 and g7 was withdrawn with the consolidation. The
first real retirement will be the first live exercise of that machinery.

### 4.3 There are two live observation banks again, and the newer four are in the retired one

`.agent-work/LESSONS.md` is not empty. It holds **4 lessons**:

```
$ grep -c '^### lesson:' .agent-work/LESSONS.md
4
  lesson:falsify-a-check-against-a-decoy-before-trusting-it
  lesson:a-verdict-must-not-select-on-the-gap-it-escalates
  lesson:grading-a-contested-claim-settled-launders-it
  lesson:reasoning-gate-crew-waiver-can-be-wrong-for-synthesis
```

They were added at `390ee90` (#310's B2 gate evaluation), which is **after** `a4934cb` (#308's
migration and intake cut), and **none of the four exists in the episode store** (grepped each slug
against `episodes/` — zero hits). So phase 1 emptied the playbook into the store, cut live-agent
intake, and then banked four fresh lessons back into the emptied file.

The write-and-audit half of the lessons machinery is still wired: `ADMIRAL_SPINE.template.json:57`
(`c6`) and `COMMANDER_SPINE.template.json:111` (`c2`) both still run
`verify_lessons_applied.py --file .agent-work/LESSONS.md`, and `skills/lessons-auditor/` still
reads it. That is exactly the state **#400** (the preamble instructs agents to read an empty bank,
and is unreachable through its own writer) and **#404** (*"the lessons feedback loop lost its
observer: the Commander spine still tells agents to bank for re-observation, but nothing
re-observes"*) describe — both **OPEN**. **These four lessons are the live evidence that #404 is not
theoretical.** They are outside this excursion's scope (not episodes), flagged because a triage of
"what carries live signal" that ignored them would be under-inclusive about the corpus's
observation banks.

### 4.4 A query by origin run finds nothing (#399, OPEN)

All 20 migrated episodes read `run: issue-308`, `role: commander`, `spine-step: execute`. Their
origin rides in `artifact-ref` as `lesson:<id>` / `origin-run:<run>`. The choice was deliberate and
its cost stated rather than hidden (`notes-308.md:404-405`): writing the origin run's four required
counters would have meant asserting four unknown numbers *in the bin that is trusted precisely
because it is machine-derived*. **The consequence: `query_episodes.py select --field run --value
epic-226-lessons-audit` returns nothing**, and *"that is the kind of thing discovered six months
later by someone who assumes the store is uniform."* The store is not uniform, and nothing in it
says so.

---

## 5. Scoped nulls — what I did NOT test

- **I did not assess whether any live-signal item is *worth* fixing.** That is the importance
  judgement Tommy explicitly reserved (#399, `notes-308.md:281-284`). Every verdict here answers
  *is the remedy in the corpus, and does the mechanism still exist* — both by command.
- **I did not check the f1Brainz or other dogfood repos** for whether these mechanisms recur
  outside this corpus. `issue-308-007`'s second occurrence (f1Brainz epic-601) is taken from the
  episode's own record, not re-verified. The closeout notes the same blind spot as a null that does
  not discriminate: ~75 issues generated here, zero inbound findings from three dogfood projects in
  the same window (`LESSONS_AUDIT.md:298-301`).
- **I did not read `tests/test_episode_store.py`** to confirm the retirement machinery works — §4.2
  claims only that it has never *run on a real episode*, which follows from the retired count of 0.
- **I did not re-run the #307 or #309 measurements.** `issue-304-g3-005`'s supersession rests on
  #307's posted verdict and Tommy's PASS, not on my own re-measurement.
- **`issue-308-002`'s six confirmations, `issue-308-004`'s five, and `issue-308-008`'s four are
  taken from the migrated records' own counters.** I verified the *remedy is absent* by command; I
  did not re-verify each historical confirmation.
- **No `gh` write of any kind, and no episode file was opened for writing.** The only file this
  excursion created is this one.
