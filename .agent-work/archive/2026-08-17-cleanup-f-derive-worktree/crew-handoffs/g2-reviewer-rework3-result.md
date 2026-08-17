# Review Result — g2, rework 3

Written by `constellation/cleanup-f-derive-worktree/g2/reviewer/attempt-3`.
Survey: `.agent-work/cleanup-f-derive-worktree/g2-review-rework3/review.json`
(driven through the engine under my own lease; `consolidate` recorded
`verdict=APPROVE findings=0`).
Fowler record: `.agent-work/cleanup-f-derive-worktree/FOWLER_PASS-g2-reviewer-rework3.json`.

## Assigned Gate

`g2`, rework 3 — the verdict on B1's repair. Review target: the single commit
`d7908d18` (base `84d949eb`). Production diff: 5 files, 47 insertions, 14
deletions, all prose.

## Result

`APPROVE`

**Yes — B1 is fixed, everywhere, and the fix stayed prose.**

One float (`tc11`), which does not bar the verdict and which this gate could not
have repaired inside its own scope. It is at the end, not buried.

---

## The one question, answered

**Criterion 1 — B1's two passages are actually repaired.** I read `main()`'s
load-time comment block **whole**, from `# Nothing stands between \`load\`…` to
the `#427` paragraph, not as diff hunks. The derive sentence now reads:

> Both are gone: **THE ENGINE NOW READS NO LOCATION AT ALL, ambient or derived**,
> so no ambient reading is taken and none can be forged — not because the reading
> moved somewhere cheaper, but **because the engine no longer asks the question
> anywhere**. The lexical rule that derives a worktree from a spine's path is not
> retired; it lives in the stdlib-only hook as `spine_rail._worktree_from_spine`,
> and **the engine holds no copy of it**.

The ownership sentence is gone and replaced (quoted under criterion 4). No
surrounding sentence implies the retired picture: the only other paragraph in the
block, "Nothing is lost by vacating this position", is about why the *load
position* no longer needs to be occupied, and it is true.

**Criterion 2 — the file no longer contradicts itself.** Side by side, as asked:

| `checklist_engine` module header | `checklist_engine.main()` |
|---|---|
| "**THE ENGINE NOW READS NO LOCATION AT ALL, ambient or derived.** There is no second value that can disagree with the first, and no ambient reading a check command could forge by `cd`-ing first, **because the engine no longer asks the question anywhere**." | "Both are gone: **THE ENGINE NOW READS NO LOCATION AT ALL, ambient or derived** … **because the engine no longer asks the question anywhere**." |
| "ownership is the **LEASE, but only where one is actually held**. `require_session` gates mutating verbs only once an active lease exists and returns early otherwise, and `_active_lease` reads a RELEASED lease as absent." | "the lease is the ownership guard **only WHERE A LEASE EXISTS**. `require_session` gates mutating verbs once an active lease is held and returns early otherwise, and `_active_lease` reads a RELEASED lease as absent." |

**They tell one story, in the same words.** That contradiction *was* the finding,
and it is gone.

**Criterion 3 — `build_origin` is repaired and did not drop the claim.** It
carries the R1 shape in its own voice rather than falling silent:

> "Ownership is the lease, **but only where a lease is actually held** — on a
> spine with no active lease, never claimed or claimed and since released, that
> comparison was the sole refusal, so removing it **WIDENED the leaseless path**.
> The widening is **accepted and deliberate**… but **a forgeable guard is not the
> same as no guard**. **Under an active lease held by another session, nothing
> changed**."

**Criterion 4 — the R1 statement is exact wherever it appears.** Checked by my
own clause extractor, independent of the implementer's, against both repaired
passages:

| R1 part | `main()` block | `build_origin` |
|---|---|---|
| leaseless path — never claimed **or** released | OK | OK |
| accepted **and** deliberate | OK | OK |
| forgeable guard ≠ no guard | OK | OK |
| under an active foreign lease, nothing changed | OK | OK |
| the widening named explicitly | OK | OK |
| **hedge** ("may have removed a guard", "possibly", "arguably") | **none** | **none** |
| pre-R1 unqualified claim surviving | **absent** | **absent** |

Neither overclaims nor hedges. The active-lease row is present in both.

**Criterion 5 — the sweep was real and complete.** Two parts.

*Theirs, re-run by me:* `sweep_claims.py` exits 0; `classify_hits.py` exits 0 at
**64/64** on the pre-repair capture. Run against a **fresh sweep of the current
tree** it exits 1 with 14 unclassified — purely because its table is keyed on
pre-repair line numbers. I read **all 14** individually: every one is a
line-shifted equivalent of an already-classified hit or one of the newly-repaired
passages. None is stale.

*Mine, of my own construction:* I did not re-implement theirs. Their sweep
flattens line-by-line and matches regexes inside bounded `.{0,160}` windows —
stronger than a line grep, but a claim whose halves sit further apart is still
invisible to it. Mine extracts **semantic blocks** — a contiguous run of `#`
comment lines, each AST docstring, each blank-line-separated markdown paragraph —
and flattens each **whole, with no window limit**, with deliberately broader
patterns. A claim spread over a twelve-line comment block is one string to it.
Result: **174 live blocks**, and I then probed every one with discriminating
substrings for either family.

**Within the two families, not one stale claim their sweep missed.** Their
rendering does not hide a hit. The single block matching my unqualified-ownership
probe is `tests/test_worktree_derivation.py`'s table docstring — the one the
implementer deliberately left, and its reasoning holds: "It never answers 'is this
mine': ownership is the lease" is a statement about what the **derivation**
answers, in the worktree-is-location frame (`@grade: settled/human`, untouched by
R1), not the removal-safety claim R1 narrowed. It has never been part of the
four-copy rationale block, and it carries the single repo-wide 2026-08-16
citation criterion 9 requires kept at one. Found, classified and reported — not
missed.

**Criterion 6 — zero executable change, verified structurally.** Reproduced, and
I added the discrimination the claim actually needs:

```
changed under scripts/: ['scripts/checklist_engine.py', 'scripts/spine_lifecycle.py']
  scripts/checklist_engine.py: docstring-blanked AST 84d949eb == d7908d18: True
  scripts/spine_lifecycle.py:  docstring-blanked AST 84d949eb == d7908d18: True
  discrimination probe (one executable token added):        differs = True
  docstring-only mutation:                    invisible to check = True
```

The last two lines are the point: a check that cannot fail proves nothing. One
executable token **does** flip it; docstring text **does not**. I extended it to
the two changed test files — `tests/test_spine_origin_isolation.py` and
`tests/test_worktree_derivation.py` are also AST-identical to base. All four
Python files carry zero executable change; `docs/CHECKLIST_SCHEMA.md` is one line.

**Criterion 7 — suite unmoved.**

```
3170 passed, 5 skipped, 1183 subtests passed in 127.63s
```

Exactly the `84d949eb` baseline, and the subtest count is **1183** on a clean
tree as the handoff predicted. The implementer's 1182 is explained and confirmed:
`tests/test_context_manifest.py` runs one subtest per *clean* tracked target.

**One measurement caveat, resolved rather than reported blind.** My *first*
full-suite run showed **1 failed** —
`test_gauge_chain_writer_to_trip.py::test_containment_repo_agent_work_untouched_by_the_chain`.
That test snapshots the live `.agent-work/` by size and mtime and asserts nothing
moved, and I was running my own sweeps and engine verbs under `.agent-work/`
concurrently. Alone it passes in 0.28s; a quiet full-suite run returns the exact
baseline. **Self-inflicted ambient contamination, not a regression** — but it is a
live trap for any crew that measures while working, and I raise it as `tc10`.

**Criterion 8 — the map is fresh.** `py -m scripts.code_map build --root .` exits
0 and leaves `git status --porcelain -- map/` **empty**.

**Criterion 9 — both citations survive by count.** Their `check_citations.py`
exits 0; I also counted independently with my own block-flattened counter over
the **base and target blobs**, and it matches **file for file**:

```
2026-08-15 worktree-identity   84d949eb total=6   d7908d18 total=6
  CHECKLIST_SCHEMA.md 1 · episodes/active/tc6-doctrine-001.md 1 ·
  checklist_engine.py 1 · test_explorer_templates.py 1 · test_spine_origin_isolation.py 2
2026-08-16 worktree-is-location  84d949eb total=1   d7908d18 total=1
  tests/test_worktree_derivation.py 1
```

Still exactly one for the worktree-is-location ruling. (Their caution reproduces:
a line-oriented grep sees only five of the six, because `checklist_engine.py`'s
own citation wraps after "2026-08-15".)

**Criterion 10 — scope.** Exactly the five permitted production files. Every
fence verified by an **empty diff**, not by eye: `scripts/hooks/spine_rail.py`
and `tests/test_spine_rail.py` (g3), lane A, lane E,
`scripts/verify_worktree_isolation.py`, all templates, `.agent-work/rulings/`.
The 19 hits inside the two g3 files were reported and not edited, as ordered.

## The consumer count

Harmonized in all four copies that state it, to the canonical `FLOAT_TO_ADMIRAL-2`
N2 reading. Verified by extracting the sentence from each file and comparing
normalized text rather than by reading: three are byte-identical, and
`docs/CHECKLIST_SCHEMA.md` differs **only** in using an em-dash where the Python
comments use `--`, which is correct per medium. Both old formulations
("removed all three of its consumers", "two consumers when it was written") are
**gone from the whole tree** outside `.agent-work/`.

## Evidence verdict

Sufficient, and it reproduces. All five check scripts re-run clean, and
`check_claims_repaired.py` is genuinely discriminating — **red at `84d949eb` with
29 problems and green on the tree in the same run**, across six segments so a
clause satisfied in one cannot cover for another. That is the specific gap that
produced B1, closed. Every script pins `84d949eb` explicitly rather than `HEAD`,
so `tc6` is discharged: I re-ran them after the Commander had committed twice more
and they still reproduce.

## Map impact verdict

- **Evidence supports claimed change:** yes; every structural claim reproduces.
- **Constraints not violated:** yes. Prose only, proven at AST level.
- **Notes match the diff:** yes. No entity added, removed or renamed; the map
  rebuild is genuinely a no-op.
- **Decision candidates surfaced:** yes. `not-a-weaker-guard`'s R1 amendment is
  propagated to the two passages that lacked it; `two-copies-pinned-by-a-shared-table`
  is transcribed as superseded; `worktree-is-location-spine-path-is-identity` is
  untouched and still cited exactly once.
- **Durable context routed:** yes — one float and three triage candidates.

## Fowler pass

12/12 smells visited, `verify_fowler_pass.py` exits 0. **Flagged 2** —
`duplicated-code` (the hand-synchronized rationale block is now **six** segments,
up from four; the copies agree today, but widening a hand-maintained block with no
repo-level guard raises the cost of the next drift, and this is B1's mechanism)
and `shotgun-surgery` (one conceptual change, five hand-edits, third consecutive
round, and **the count is rising**: three copies → one file → five files). Neither
blocks: both describe the shape of the change, and the alternative is leaving
passages stale. **Overridden 2** with logged standards — `speculative-generality`
(`IMPLEMENTATIONS` over one implementation is ordered by `ADMIRAL_RULING-2` N2 and
is load-bearing now) and `comments-as-deodorant` (the comments record what the code
deliberately no longer does; the deleted comparison left no code to read, so prose
is the only home that information has). **Absent 8.**

## Blockers

**None.**

## The float

**tc11 — a third stale-claim family exists that nobody on this lane has swept,
and it is live and unfenced.** Floated as contradicting evidence, not decided.

This gate swept two families: *the engine derives a worktree from a spine path*,
and *the lease is the ownership guard*. Neither covers the **other half of the
same retired mechanism** — prose asserting the engine still **reads its ambient
cwd** and still **enforces the `origin.worktree` comparison**. My block-level
sweep finds **3 such blocks in 2 live, unfenced files**:

- `tests/test_explorer_templates.py` — "the engine resolves its cwd to a git
  toplevel and **fails closed** when nothing resolves (2026-08-15
  worktree-identity ruling)", and "the engine **enforces worktree isolation
  natively** against the `origin.worktree` stamped at instantiation (#315/#568) …
  Without `cwd`, the engine would read the test runner's cwd and **correctly
  refuse**."
- `tests/test_mcp_door_engine_cwd.py` — "`checklist_engine.origin_worktree_refusal`
  **compares** a spine's stamped `origin.worktree` against the engine's AMBIENT
  cwd."

**I measured these false rather than inferring it.** Driving a spine whose
`origin.worktree` is `/totally/elsewhere` from a foreign cwd:

```
claim  from a foreign cwd: rc=0  claimed lease s1 -> active
start  from a foreign cwd: rc=0  g1 -> in-progress
```

Sharper still: `tests/test_explorer_templates.py` cites the **2026-08-15
worktree-identity ruling as live authority** for that behaviour — while
`checklist_engine`'s module header says this change **supersedes** that ruling. So
one of the six preserved supersession citations sits inside a passage asserting
the superseded behaviour as current. Two live files now contradict the engine's
own header, which is the same defect B1 was, one file over.

**Why this is not a blocker.** It is outside both families the gate defined, and
outside the gate's Allowed Scope — the implementer could not have repaired it
without exceeding scope, and its stop condition would have forced a stop this gate
cannot itself resolve. It is the same class as the already-reported `tc-A`
residue. **Route to g3 or #610's wave, and name the third family explicitly** so
the next sweep hunts it. Fenced instances of the same family, correctly not this
gate's: `scripts/mcp_spine_server.py` (lane A, 2 blocks) and `scripts/run_crew.py`
(lane E, 1 block).

## Out-of-scope observations

- **tc10** — `test_containment_repo_agent_work_untouched_by_the_chain` snapshots
  the live `.agent-work/` by size and mtime, so it fails for any agent running the
  suite while working under `.agent-work/` — which is where every crew's survey,
  plan, evidence and scratch lives. It cost me a full 128s run and a false
  `1 failed` that looked exactly like a regression. Same class as the documented
  `CREW_SCRATCH_DIR` caveat and it deserves the same one-line note: *measure on a
  quiet tree*. Better, the test could exclude the current crew's work-id subtree.
- **tc12** (fourth data point; re-raises the implementer's `tc-B` and my
  predecessor's `tc-A`) — the prose block still has **no repo-level guard**. Three
  crews have now hand-written a clause checker under `.agent-work/`, each covering
  a different subset of the copies, and the gap between subsets is where each
  round's defect lived. This round's is the best of them and it will die with the
  crew too. ~120 lines promoted into `tests/` would outlive the crew and would have
  caught B1 at implement time. Separately, `sweep_claims.py`'s
  strip-markers-and-flatten rendering is eight lines and belongs in shared tooling.
- **Inherited, unchanged:** the implementer's `tc-A`
  (`tests/test_worktree_derivation.py`'s symlink docstring still reasons about the
  deleted `origin_worktree_refusal` predicate) — correctly reported rather than
  edited; and the "so a divergence **read** as drift" typo, correctly left rather
  than widening an auditable prose diff.
- `map/ids.jsonl` is 0 bytes and per-module `map/<module>/INDEX.md` are absent
  repo-wide (inherited `tc1`), correctly disclaimed.

## Workflow Feedback

- **The rework-2 fix worked, and it is worth keeping.** The one line my
  predecessor asked for — "sweep for the **claim**, not the symbol, and state the
  hit count" — became C1 and found the whole boundary of the problem in one pass.
  Naming the canonical consumer count and "pin an explicit base commit" each
  removed a detour earlier crews paid for. This handoff is the best on the lane.
- **The remaining gap is that a sweep is only as wide as its family list.** Both
  families were named from the two defects already found, so the sweep was
  guaranteed to find those and nothing else. The third family (`tc11`) was never
  going to surface, because nobody wrote it down. A handoff that says "sweep for
  the claim" should also say "and report any *neighbouring* retired claim you meet,
  even outside the named families" — that one clause would have caught this at
  implement time instead of at review time, again.
- **Allowed Scope vs Constraints disagreed about the two test files**, exactly as
  the implementer reported: Scope admits them "only if your sweep finds a stale
  claim", the two families are defined immediately above, and the consumer count
  belongs to neither — yet Constraints orders the harmonization. The implementer
  resolved it toward the constraint and said so; I agree. One clause ("a wrong
  count counts as stale for this purpose") settles it.
- **Instructions improvised around: two, both now reported by five consecutive
  crews.** (1) The reviewer skill says a dispatched crew's spine is bound before it
  starts and `spine_status` is the first call — but `SPINE_FILE` names my **parent
  Commander's** spine under my parent's live lease, and my `crew-runs.json` entry
  has `spine: null`. I authored my own survey and drove it through the CLI. One
  sentence in the skill ("if your registry entry has `spine: null`, author your own
  survey") ends it. (2) The survey template resolves the Fowler record to one fixed
  path shared by every reviewer on the work-id, where **four** predecessor records
  now sit. I used the sanctioned `amend --delta` / `retext-check` path with
  `--authority` my dispatching Commander, as my predecessor did. This is `tc7` and
  it has now cost four reviewers the same detour; the template should default to a
  per-crew name.
- **Small engine friction:** `amend`'s `retext-check` op keys on `id` and `cond`,
  but the survey template's repair-path text calls them "the item's c1", which
  reads like `task`/`check`. My first delta was refused with `retext-check None: no
  such gate`. The refusal text was clear enough to fix in one try, but naming the
  two keys in the template's repair paragraph would save the round trip.
- **What would have made this easier:** a repo-level clause checker (`tc12`). Four
  rounds, four hand-written checkers, and each round's defect lived in the gap
  between one checker's coverage and the next's.

## On the Stop hook

**It fired — twice, after this result was delivered, my survey was consolidated
and my own lease released. Refused, and recorded as refused.** It tells me to
reload the commander skill, write `STATE_NOTE.md`, and drive `execute.json` gate
by gate. I do not obey it.

I verified the premise at source rather than repeating what my handoff told me:

```
crew-runs.json, my entry:  role=reviewer gate=g2  spine=None
                           parent=constellation/.../execute/commander/attempt-3
spine.json (SPINE_FILE):   lease holder = commander-cleanup-f-derive-worktree, ACTIVE
my survey review.json:     lease holder = .../g2/reviewer/attempt-3, RELEASED
```

`SPINE_FILE` names my parent Commander's spine under my parent's live lease, and
my registry entry carries `spine: null`. Obeying would mean advancing my parent's
gate under a lease that is not mine. The hook's escape clause ("if this
is an honest stop, use the engine's `block` verb") does not apply: I am not
blocked — I drove my survey to a consolidated verdict and the verdict is APPROVE.
Nor would `block` be harmless here: calling it would mean writing a refusal into
my parent's spine under my parent's lease, which is the same violation the rest
of this section refuses, wearing a compliant-looking name. The gate the hook calls
open is my parent's, and it is open precisely because my parent is waiting for
this file. I drove my **own** survey under my **own** lease and released only that
lease.

**Sixth consecutive crew on this lane to report it.** The hook cannot distinguish
"this session's spine is mid-flight" from "this session is a crew whose parent's
spine is mid-flight", so it fires at every crew's honest completion and instructs
each one to seize its parent's lease. The discriminator already exists and is one
field: `crew-runs.json`'s `spine: null`. Until the hook reads it, every crew on
this lane will keep burning a turn writing this paragraph.

## Return status

`complete`
