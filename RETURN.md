# RETURN — `cmdr-447-episodes-retirement` · issue #447 · epic-418 workstream H

> This file replaces workstream A's inherited `RETURN.md`, which was tracked at `cbd9aee` and
> appears in every worktree off it. Its content is preserved in git history at `77e428d^`.

Branch `epic-418/h-447-episodes-retirement` · base `cbd9aee` · **ten commits** · **not pushed, no PR,
not merged** — those are the Admiral's per this launch order. Spine terminal, lease released.

---

## 1. Verdict

**This is a win, not a measured negative.**

I was asked to finish #308's retirement: `.agent-work/LESSONS.md` and `.agent-work/AGENT_FEEDBACK.md`
genuinely retired, replaced by the episode store, with a shipped guard that keeps it true, live
content carried across, and nothing reading episodes as prescriptions.

All of that is now true. Both files are off the index with no shipped writer, no shipped reader, and
no skill or template pointing at them. The eight live lessons are in `episodes/` as records of what
happened rather than rules to follow. `AGENT_FEEDBACK.md`'s prose is dropped with a stated reason and
retained in git history. The playbook's machinery — three scripts, a whole skill, two templates — is
deleted, and the closeout obligation on both the Commander and Admiral spines now runs through a
capture gate that can emit ids and counts but structurally cannot emit an episode's content.
`scripts/verify_retirement.py` exits 0 across four legs, having been observed **failing** on the
untouched tree before it was ever observed passing. The suite is 1622 passed, 0 failed, 0 xfailed.

The one thing this run did **not** do is fix the store's existing records: roughly 24 of the 32
episodes that predate this run carry `workaround` assertions written as instructions. That is
`constraint:episodes-are-not-prescriptions` failing inside the store rather than around it. It is
filed (**#460**) and floated, not fixed — `decision:store-hardening-out-of-scope` makes it a
different job, and this run introduced none of it.

---

## 2. Evidence — commands with real exit codes

All suite runs prefixed `FORCE_COLOR=0 NO_COLOR=1`; see §7 for why that matters.

| command | exit | result |
|---|---|---|
| `python scripts/verify_retirement.py` | **0** | **zero bytes printed** — all four legs green |
| `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` | **0** | 1622 passed, 2 skipped, 0 failed, 0 xfailed |
| `python -m pytest tests/test_retirement_guard.py -q` | **0** | 16 passed, no xfail marker remains |
| `python scripts/verify_episode_captured.py issue-447 --store-root episodes` | **0** | 8 episodes |
| `... --phase archive` | **0** | all 8 tracked by git |
| `git ls-files --error-unmatch .agent-work/LESSONS.md` | **1** | off the index |
| `git ls-files --error-unmatch .agent-work/AGENT_FEEDBACK.md` | **1** | off the index |
| `test -f` on both retired paths | **0** | still on disk — see §3 |
| installed `verify_agent_feedback.py epic418-h-447 --phase feedback` | **1** | **unchanged** before and after |
| `git diff --stat 77e428d..HEAD -- docs/RECURSIVE_IMPROVEMENT_DESIGN.md` | — | 16 insertions, **0 deletions** |
| `git grep -c 'LESSONS.md' -- docs/RECURSIVE_IMPROVEMENT_DESIGN.md` | — | **12**, same as at `77e428d` |
| `recover_crews.py epic418-h-447` | — | 8 crews, **0 unresolved** |

**Commits.** `bf8819a` guard · `dbf9a23` capture gate · `100a33c` rewire · `77e428d`
carry+untrack+delete · `fd7ef60` prose+census · `f2dd40a` verify · `613ac88` this run's own
sixteen episodes and the `RETURN.md` classification · `97905e7` terminal spine · `79df575`
orphan-stamp fold.

**Final state on the committed tree:** `python scripts/verify_retirement.py` exit **0**, zero bytes.
`FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` exit **0**, **1622 passed, 2 skipped, 0 failed, 0
xfailed**. `git status --porcelain` shows only `.agent-work/AGENT_FEEDBACK.md` and
`.agent-work/LESSONS.md` as untracked — which is the retirement, not dirt.

**Suite delta, reconciled by name** (`.agent-work/epic418-h-447/evidence/g6-count-delta.md`):
1688 baseline + 12 guard + 15 capture gate + 1 general install assertion − 85 deleted
(`test_apply_lessons_delta` 70, `test_verify_agent_feedback` 11, `test_verify_lessons_applied` 4)
− 13 pruned + 3/−2 census + 2 HEAD-pinning tests restored by g5's commit + 1 marker removal = **1622**.
The claim is **"0 failed"**, never "strictly greater" — a retirement that deletes 85 tests cannot
honestly assert a higher count.

**Every gate carried an independent review.** Six gates, each with an implementer, an independent
reviewer that re-ran the evidence rather than reading the transcript, and my own re-derivation.
All four reviews returned **APPROVE with 0 blockers**. One implementer raised a blocker (g4) and it
was dispositioned, not absorbed.

**PR state:** none. Not pushed, no PR opened, nothing merged. `gh pr view --json state` has nothing
to report because this launch order reserves those for you.

---

## 3. The three things you said you would check first

### (1) The guard — what ships, and the evidence it failed on purpose

`scripts/verify_retirement.py`, authored at `bf8819a` **before any retirement work**, so it was
falsified against the real disease rather than a decoy. On the untouched tree it exited **1 across
three legs**; transcript at `.agent-work/epic418-h-447/evidence/g1-guard-red.txt`.

Four **named** legs, so each is falsifiable alone rather than a single boolean:

| leg | what it catches |
|---|---|
| `retired-path-still-tracked` | either retired path back in the **index** — path-based, unparaphraseable |
| `retired-name-on-shipped-surface` | a retired name on any surface an agent is instructed by — path half **and** content half |
| `unapproved-store-mention` | a new shipped site naming the store without an approved reason |
| `replacement-absent` | the replacement missing from either spine's **imperatives** or either bundle |

Surfaces are enumerated from `git ls-files`, not `rglob`, so a path deleted from the working tree but
still in the index is seen — which is exactly the state §3(2) leaves behind.

Two reason-carrying censuses back it, both naming **exact sites, never patterns**:
`tests/data/store_mentions.approved.txt` and the new `tests/data/retired_names.approved.txt`. The
g5 reviewer measured the second **exactly-covering in both directions** — 53 approvals against 53
residual sites, zero dead approvals, zero uncovered lines — and ran a six-property decoy suite
proving a reworded near-miss suppresses nothing, the same text under a different path still fires,
and the path half fires despite an approval written for it.

`test_canon_is_clean` carried `xfail(strict=True)` from g1 through g5. **Strict means an XPASS
fails**, so the moment the tree really went clean the scaffolding broke the build and forced its own
removal at `f2dd40a`. It did not need remembering.

**The guard caught me, twice.** At g1 review it fired on **itself** once tracked — 12 self-hits,
because its own constants name the retired files — and the fix was the principle that a guard cannot
be inside the set it guards. And at g5 integrate, my own one-column edit to
`docs/CONSTELLATION_OVERVIEW.md` took it from exit 0 to exit 1 within the minute, because the census
records approved lines **verbatim** and is exactly-covering, so editing an approved line orphans its
approval.

### (2) How I avoided stranding my own closeout

**Both** of the sequencing options you named, deliberately.

`scripts/agent_work_root.py:136-140` redirects `durable_root()` to the **worktree** whenever an
active Admiral epic lease exists — and epic #418 holds one. So this run's own `feedback`/`archive`
gate reads *this worktree's* `.agent-work/AGENT_FEEDBACK.md`. Therefore:

- **`git rm --cached`, never `git rm`** (`decision:untrack-do-not-delete`). Untracking removes the
  path from the **index**, which is what "shipped" means and what the guard's path leg checks. The
  on-disk copies survive this run and die with the worktree. Deleting them would have stranded the
  closeout, whose only two exits are recreating a retired file — literally #308's failure shape — or
  a human override in a run with no reachable human. The measurement is now recorded in a docstring
  **at the leg that enforces it**, so the next reader finds the why where the rule lives.
- **Dropping `verify_agent_feedback.py` from `SKILL_SCRIPT_BUNDLES` does not delete the installed
  copy** — no install runs mid-gate. I verified this rather than assuming it: the installed gate
  exits **1 before and 1 after**, byte-identical message. Unchanged, not merely non-fatal.

My outer spine was instantiated before g3's rewiring, so its `feedback`/`archive` conditions still
call the installed `verify_agent_feedback.py`. That path is confirmed open. A Commander launched
**after** this merges gets the rewired spine and the capture gate instead.

### (3) What happened to the live content

**`LESSONS.md` — carried, all of it, and there was more of it than the plan knew.**

Your resume brief said not to assume those files were frozen at what my worktree sees. They were not.
`main` advanced to `861ecbe` and `LESSONS.md` was union-merged there: its Active section holds
**eight** lessons, not the six my frozen plan named. The two extra came from the governor-262 side —
`name-scoped-test-filter-gates-are-strong-but-structurally-blind` and
`crew-blocked-on-a-commander-blocked-on-that-crew-has-no-exit` — and both satisfy the plan's own
CARRY RULE, each `grounding` naming a concrete observed event.

Carrying six would have silently dropped two live lessons at merge, which is the loss "Done looks
like" item 3 forbids. So I **amended the spine through the engine** — `rescope` on `g4-implement` and
`g4-integrate`, count 6→8, authority cited as `admiral:launch-order/H-447 (resume brief)` — rather
than attesting a statement I knew to be false. Both audit entries are in the journal. I did **not**
rebase or merge: episodes land in `episodes/`, my own tracked path.

The **inversion** is the substance. A lesson's `statement` is prescriptive; an episode holds no
rules. So each statement became the episode's `workaround` assertion **rewritten as an observation of
what that run did**. All eight read as reports. One is worth your eye: `issue-447-001`'s source rule
demanded a check be run against a decoy, and that run caught its checks by cold reading and never ran
one — so the episode reports the cold reading. Claiming the decoy would have been the fabricated
`observed-behavior` the store's doctrine forbids.

**`AGENT_FEEDBACK.md` — dropped with reason, not migrated.** 2119 lines (its state on main at
`861ecbe`). Synthesising typed assertions from unstructured prose retrospectives is that same
fabrication. Git history retains the file at its final revision, and a snapshot sits at
`.agent-work/epic418-h-447/context/AGENT_FEEDBACK-main-861ecbe.md`.

**Where the replaced content now lives:** `episodes/active/issue-447-001.md` … `008.md`, each
carrying `- artifact-ref: lesson:<slug>` for identity continuity with the retired playbook.

---

## 4. Isolation proof

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/epic418-h-447
worktree OK: in C:/Programs/constellation-skills-wt/epic418-h-447
EXIT=0
```

That is the tool's entire output — one line. Run at closeout; transcript at
`.agent-work/epic418-h-447/evidence/isolation-proof.txt`. **Fence honoured:** `scripts/hooks/*`,
`scripts/gauge_reader.py` and `docs/GAUGE_WRITER_HOOK.md` have an **empty diff** across
`cbd9aee..HEAD`, index and worktree. **No commander-to-commander contact with `cmdr-440`.**

---

## 5. Scope-discipline report — corner cases deliberately not chased

Each has a comment at the code site naming it.

| # | corner case | comment site |
|---|---|---|
| 1 | the `--store-root` default carries the installed-copy hazard (resolves to the skill install dir); mitigated by printing the resolved root on every outcome | `scripts/verify_episode_captured.py:196-201` |
| 2 | "untracked" is not distinguished from "not a git repository" — both mean not durable, git's own message is carried through | `scripts/verify_episode_captured.py:151-161` |
| 3 | `retired/` is not searched, so an episode retired mid-run reads as uncaptured; chasing it means teaching the capture gate to reach into the archive | `scripts/verify_episode_captured.py:125-130` |
| 4 | `store_root()`'s semantics and its `durable_root()` ruling left untouched; only the hazard is named | `scripts/apply_episode_delta.py:511-522` |
| 5 | `query_episodes.py` unbundled is a **default, not a boundary** — four measured routes around it named, because an overclaim here is worse than no claim | `scripts/install_constellation.py:141-159` |
| 6 | the `retired-name` leg's **path half is deliberately unapprovable** | at the leg in `scripts/verify_retirement.py` |
| 7 | untrack-not-delete, and why the leg asks the index rather than the filesystem | docstring at the leg in `scripts/verify_retirement.py` |
| 8 | the `Lesson:` field **name** kept while its accepted value became an episode id — `collect_feedback.py` fingerprints recurrence on the literal name | in `CONSTELLATION_FEEDBACK.template.md`; filed as **#464** |
| 9 | g1's unchased guard limits: a successor playbook that never names episodes, prescriptions inside workaround statements, lowercase variants, prescriptions split across two lines | at the code site in `scripts/verify_retirement.py` |

Limit 9's first item is why the **tombstone** exists: no mechanical leg can catch a successor
playbook that never names episodes, so `docs/agents/ORCHESTRATOR_CONTEXT.md` names the *shape* of the
retirement as doctrine. That is where a good-faith agent acting from a stale instruction lands.

---

## 6. Map impact

**No packet map exists** — `docs/architecture/` is absent — so the spine's own fallback applied and I
reconciled the structural record directly, inside g5 rather than as a separate pass. Nine documents
carry it: `docs/CONSTELLATION_OVERVIEW.md` (taxonomy row), `docs/agents/ORCHESTRATOR_CONTEXT.md`
(tombstone), `docs/agents/CREW_CONTEXT.md`, `docs/agents/GLOSSARY.md`, `docs/EPISODE_STORE.md`,
`episodes/README.md`, `README.md`, `SKILL_INDEX.md`, `docs/POSITIONING.md`.

Net structural change an architecture reconcile needs to know:

- **`capability:run-closeout-learning` changes owner** — from the lessons playbook to the episode
  store. Both spines' closeout conditions now run `verify_episode_captured.py`.
- **New:** `scripts/verify_episode_captured.py` (the store's first write-side gate, at two strengths:
  captured, and captured **and** tracked), `scripts/verify_retirement.py`,
  `tests/data/retired_names.approved.txt`.
- **Gone:** `scripts/apply_lessons_delta.py`, `scripts/verify_lessons_applied.py`,
  `scripts/verify_agent_feedback.py`, `skills/lessons-auditor/` (whole tree),
  `skills/workbench/templates/{LESSONS,AGENT_FEEDBACK}.template.md`.
- **Deliberately not reconciled:** `docs/RECURSIVE_IMPROVEMENT_DESIGN.md`. It is a design **record**
  of the loop as built in June 2026 and gains only a superseding header. Reconciling a map means
  making it match reality; doing that to a record would falsify history.

---

## 7. Triage — 8 filed, 4 folded, 2 fixed now

**Filed** (filing is delegated; every number below is new):

| # | what |
|---|---|
| **459** | `test_mutation_floor.py`'s kill detector cannot match coloured pytest output — see §7 note |
| **460** | ~24 of 32 canon episodes carry **imperative** workarounds. **Read this one first.** |
| **461** | the episode-store negative control reds every run that legitimately captures, between `git add` and commit |
| **462** | `docs/agents/engine-config.json` does not exist, yet every checklist names it; the engine accepts the dangling ref **silently**, so every run is on defaults nobody chose |
| **463** | `stage_feedback.py` is orphaned after this run and still writes retired-named files |
| **464** | `CONSTELLATION_FEEDBACK`'s `Lesson:` field takes an episode id under its old name; rename it **with** `collect_feedback.py` |
| **465** | reviewer `r6-fowler` ships a placeholder no engine verb can fill, and filling it in text mode rewrites every CRLF in the state file |
| **466** | README's skill table reads 18 against its own "19 skills" sentence (pre-existing) |

**Folded, not re-filed** per `decision:fold-dont-refile` — commented on **#400, #403, #404, #277**.
**No issue closed. Every close is floated to you.** #277 is moot (its validator no longer ships);
I flagged rather than assumed that its underlying interest — id grammar and validators agreeing —
may still be live for `episodes/` and is uncovered by anything I filed.

**Fixed now**, both recorded with their commit rather than left unrecorded: the `copytree` line-number
citation invalidated by its own insertion, replaced with the symbol name (`100a33c`); and
`curator rhyme-search` removed from the overview's audience column, a consumer with no implementation
anywhere in `skills/curator/` (`fd7ef60`).

### The measurement worth your attention

**The "10 pre-existing `test_mutation_floor` failures" that my crew and the pre-crash g1 session both
reasoned about are neither pre-existing nor a regression.** `FORCE_COLOR=3` in the session
environment puts an ANSI reset between `FAILED` and the node id, defeating the harness regex at
`tests/test_mutation_floor.py:255`. With colour off the file is 14 passed, exit 0. It is fail-loud,
not fail-green, so nothing shipped wrong — but while red it **masks any real regression in that
file**, and it means every suite number in this run had to be taken with colour disabled.

---

## 8. Workflow feedback — where things fought us

- **My own g4 handoff asked for the wrong proof.** I told the reviewer to verify writer-provenance by
  comparing blob OIDs against `HEAD`. That cannot work for **new** files — they have no `HEAD` blob —
  so the check is vacuous exactly where it is needed. The reviewer replaced it with a **delta replay**
  into a scratch store, getting the eight staged blobs back byte-identically. OID-vs-HEAD proves the
  *existing* records were untouched; a replay proves the *new* ones came from the writer. Two
  questions, two commands. The replay recipe belongs in the reviewer template.
- **My line-ending guidance nearly caused a false BLOCK.** I warned that `grep -c $'\r$'` is
  unreliable here (it is). But the obvious Python alternative — worktree bytes vs
  `git show <rev>:<file>` — is *also* wrong and fails alarmingly: `.gitattributes` sets `* text=auto`,
  so blobs are LF by design and all 23 changed files report as corrupted. The correct baseline is
  unmodified **worktree** files.
- **The g4 prune widened from two test files to four**, found by command rather than by eye — which is
  the exact shape of the lesson being carried in `issue-447-006` ("enumerate the sites by command
  before editing a claim"), arriving inside the handoff that carries it. Tests couple to scripts by
  file path through per-file `importlib` loaders, so any deletion is shotgun-surgery by construction.
- **A survey has no verdict for "confirmed a real defect that is out of this gate's scope."** The g4
  reviewer had to record #460 as `pass` with the finding intact, because recording it as `fail` would
  have forced a BLOCK on something the gate neither introduced nor was allowed to fix.
- **Two crews reported the same proof-of-life problem:** the team roster listed the crew's own name as
  the Commander's, so there was no distinct parent to message without guessing. Both skipped it rather
  than message an unrelated agent. Worth fixing in the dispatch harness.
- **The launch order's "Expected and NOT defects" section earned its place.** The g3 reviewer said so
  explicitly: being told the red guard was expected let it spend its effort on the intent question
  instead of re-litigating a known red. I put one in every reviewer handoff after that.

---

## 9. Provenance

Spine `.agent-work/epic418-h-447/spine.json` (lease `cmdr-447-episodes-retirement`), execute plan
`.agent-work/epic418-h-447/execute.json` (lease `exec-447`, released after its terminal advance).
Two engine amendments, both with authority and reason: the lesson count 6→8, and the
`retired-name` approval census added to g5 without which the guard could never have gone green and
the xfail scaffolding would have outlived the work.

Evidence transcripts: `.agent-work/epic418-h-447/evidence/`. Crew handoffs and results:
`.agent-work/epic418-h-447/crew-handoffs/` and `results/`. Episode candidates harvested from every
gate: `.agent-work/epic418-h-447/episode-candidates.md`.

**Merge note.** This branch is based on `cbd9aee`; `main` is at `861ecbe`. Per your instruction I did
not rebase or merge mid-gate. Expect a conflict in `.agent-work/LESSONS.md` and
`.agent-work/AGENT_FEEDBACK.md` — **both are deletions on my side**, and all eight of main's lessons
are already carried into `episodes/`, so taking my side loses nothing. `main`'s new `replan` and
`to-initial-issues` skills were checked and mention neither retired file, so the guard's censuses do
not need to account for them. `skills/to-issues/` was renamed on main and my `SKILL_SCRIPT_BUNDLES`
edit touches the old name — that hunk needs the rename applied.

---

## 10. Three closeout calls you should see

**`RETURN.md` is now classified, not approved.** Writing this report took the guard from exit 0 to
exit 1 with 25 findings, because `RETURN.md` is tracked and a retirement report necessarily names
what it retired. The convenient fix was 25 census approvals. The honest one is that a Commander's
return report is a **record of a finished run addressed to an Admiral** — the same class as the
root-level `notes-*.md` files already in `RUN_NOTES` — so it joins them by name with its own
written-out reason, and its two existing census entries were **removed** rather than left to orphan.
The guard caught that too: `test_every_exclusion_is_bounded_and_reasoned` pins `len(RUN_NOTES)`
precisely so adding the eighth is a decision somebody takes. It failed, the decision was taken, and
the episode is recorded in that test's own docstring.

**The two ledger snapshots are not committed.** g4's crews read 261KB and 14KB verbatim copies of
the retired files as they stood on `main` at `861ecbe`. Committing them into the archive would
re-introduce the retired content under a path the deny-globs do not literally match — a weaker
version of the thing being retired. They are replaced by a pointer at
`context/RETIRED-LEDGER-SNAPSHOTS.md` naming `git show 861ecbe:…`, the eight carried episodes and
their `artifact-ref`s. **The guard stayed green either way**, which is exactly why this was a
judgement call and not a check.

**The closeout leaves two orphan engine stamps, and I folded them.** The `archive` step moves the
work area and then keeps driving the engine from the moved spine, but the engine derives its
stamp paths from the **work id**, not from the spine file it was handed — so `archive`'s own
`context/archive.json` and `mechanical/archive.json` landed in `.agent-work/archive/epic418-h-447/`,
a sibling of the real package matching nothing. Both moved into the dated package, orphan directory
removed, mechanism recorded at `ORPHAN-NOTE.md`. Not filed: cosmetic, exactly two files, visible as
untracked scratch the moment it happens.
