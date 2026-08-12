# Candidate D — retrieval-first

## 1. Constraint restated, and the retrieval questions that drove the design

**Constraint:** design the record backwards from the retrieval question. "Queryable" means
findable by deterministic means over Markdown in git. The store's only job is to hand a
downstream stochastic rhyme sensor (#308) a clean, complete, enumerable candidate set — it
never ranks, embeds, or guesses.

Every design choice below is justified by one of these enumerated queries. If a field or a
file doesn't serve one of them, it isn't in this design.

- **Q1 — fetch one episode by stable id.** Given `<id>`, return its full content in one
  operation, no scan.
- **Q2 — enumerate all non-retired episodes.** The default candidate universe for rhyme
  search.
- **Q3 — select episodes by an exact field value or set membership.** e.g. "all episodes
  touching `skills/admiral/references/fleet-doctrine.md`", "all episodes with
  `role: implementer`".
- **Q4 — enumerate the neighbours of a given episode.** The actual input the #308 sensor
  consumes: for episode E, every OTHER episode sharing at least one exact join key with E.
- **Q5 (derived, not extra machinery) — retrieve an episode's full assertion set.** Given an
  id, hand the sensor everything it needs to judge a rhyme: the core claim plus every
  suspected-cause / proposed-remedy assertion attached to it. This is just Q1 read in full;
  it's called out because it's literally "the sensor's input" the brief asks me to be
  concrete about.
- **Q6 (history-inclusive variant of Q2–Q4) — same three queries, retired included.** Needed
  for the #308 companion exercise: neighbours of a consolidated episode must still resolve.

## 2. Record shape — a real worked episode on disk

One file per episode. Filename **is** the stable id: `episodes/<id>.md`. This is the load-
bearing choice under this constraint — Q1 becomes a direct path read, not a parse-and-scan.

`id` = `<run>-<seq>`, using the same work-id vocabulary the lessons machinery already relies
on (`governor-268`, `epic-226-lessons-audit`, …) plus a zero-padded per-run sequence. The
sequence is assigned by scanning existing `episodes/<run>-*.md` for the current max and
incrementing — no separate counter file, no UUID; deterministic from the directory listing
itself.

```
episodes/governor-268-003.md
```

```markdown
<!-- episode-state: schema=1 id=governor-268-003 status=active -->

# episode: governor-268-003

## mechanical
- run: governor-268
- project: constellation-skills
- role: implementer
- spine-step: m3-implement
- context-manifest-ref: .agent-work/governor-268/context-manifest.json@a1b2c3d
- refusals: 0
- reopens: 1
- rework-count: 1
- failed-commands: 2
- artifact-ref: skills/admiral/references/fleet-doctrine.md
- artifact-ref: docs/superpowers/drills/dogfood-context-paths-absent.md

## agent-supplied
- task-intent: Fix the STATE_NOTE-fallback wording gap named in the launch order for the Commander spine.
- expected-behavior: The named launch-order defect (Commander spine, PR #75/#86 pattern) is the only place carrying the missing-fallback wording.
- observed-behavior: The Admiral spine (fleet-doctrine.md:57) carries the identical missing-fallback defect, unnamed by the launch order and undetected by the existing drill.
- impact-cost: One extra sweep pass needed to find the sibling; the drill kept reporting PASS on the checked-in fix while the sibling defect persisted.
- workaround: none

## core-assertion
- assertion-id: governor-268-003-core
- statement: This episode occurred as described above — the sibling-template gap was found by the governor-268 launch-order-mandated class sweep, not by the pre-existing drill.
- source: mechanical (harness-captured fields above) + agent report (implementer, governor-268)
- supporting-evidence: artifact-ref fleet-doctrine.md:57 confirmed present in this run's diff; failed-commands=2 corroborates the drill re-run that still reported PASS before the sweep caught it
- challenging-evidence: none recorded
- strength: weak
- lifecycle-standing: active

## suspected-cause
- assertion-id: governor-268-003-cause-1
- statement: A drill written to prove a doctrine-text fix is load-bearing, when the doctrine pattern recurs across sibling role-templates, gives false confidence if it names only ONE sibling — re-running it only re-checks the named template.
- source: agent (implementer, governor-268), citing AGENT_FEEDBACK.md 'Friction / unclear' section
- supporting-evidence: LAUNCH_ORDER-268.md part 2 class sweep found fleet-doctrine.md:57 carrying the identical defect, undetected until the sweep
- challenging-evidence: none recorded
- strength: medium
- lifecycle-standing: active

## proposed-remedy
- assertion-id: governor-268-003-remedy-1
- statement: When authoring or updating a drill for a doctrine pattern that recurs across sibling templates, the drill's 'doctrine under test' line should enumerate every sibling template carrying the pattern, or explicitly note which ones it does NOT cover.
- source: agent (implementer, governor-268)
- supporting-evidence: none beyond this single episode
- challenging-evidence: none recorded
- strength: weak
- lifecycle-standing: active

## retirement
- status: active
- retired-reason:
- retired-at:
- consolidated-into:
- superseded-by:
```

A **minimal valid episode** carries only `## mechanical`, `## agent-supplied`,
`## core-assertion`, and an empty `## retirement` block — no `suspected-cause`, no
`proposed-remedy`. It is complete and valid, satisfying constraint 2 directly: nothing about
Q1–Q6 requires a diagnosis to be present, because none of the retrieval mechanisms in
section 6 dereference those sections.

## 3. Mechanical / agent-supplied partition

Visibly separated by heading, not by naming convention, exactly as constraint 2 requires:

- `## mechanical` — zero agent effort, written by the harness/engine at capture time: run,
  project, role, spine-step, context-manifest-ref, refusals, reopens, rework-count,
  failed-commands, artifact-ref (repeated, one per line — see §6 for why not comma-joined).
- `## agent-supplied` — deliberately small, exactly the five fields the brief names: task-
  intent, expected-behavior, observed-behavior, impact-cost, workaround. I did not add a
  sixth (e.g. a `task-class` field, which the neighbour LESSONS.md schema carries) — that
  would be scope creep past what constraint 2 actually authorizes, even though it would have
  made Q3/Q4 slightly richer. Named explicitly in §10 as a place the constraint held me back.

## 4. Suspected-cause / proposed-remedy as separate, optional, pluralizable assertions

Each is its own `##`-level block with its own `assertion-id`, entirely independent of the
mechanical/agent-supplied sections and of each other. Two consequences of taking "separate
assertions" literally rather than as a single mutable field:

- **Optional in aggregate.** Zero, one, or many `## suspected-cause` blocks may be present.
  An episode is complete with none.
- **Additive under new evidence, not overwritten.** A revised diagnosis appends a second
  `## suspected-cause` block (`governor-268-003-cause-2`) rather than replacing the first.
  The first assertion's own `lifecycle-standing` can then be moved to `superseded` (with a
  `superseded-by: governor-268-003-cause-2` field added to it) while its `strength` and
  history stay on the record. This is what "creates no inertia against decisive new
  evidence" cashes out to mechanically: superseding costs one field mutation, not a rewrite.

## 5. Stratum A field-by-field mapping (concrete, not promised)

| Stratum A dimension | Episode field | Value in the worked example |
|---|---|---|
| Identified assertion (the claim) | `## core-assertion` / `## suspected-cause` / `## proposed-remedy` block's `statement` | "A drill written to prove a doctrine-text fix is load-bearing... gives false confidence if it names only ONE sibling..." |
| Stable assertion identity | `assertion-id` | `governor-268-003-cause-1` |
| Source | `source` | "agent (implementer, governor-268), citing AGENT_FEEDBACK.md" |
| Supporting evidence | `supporting-evidence` | "LAUNCH_ORDER-268.md part 2 class sweep found fleet-doctrine.md:57..." |
| Challenging evidence | `challenging-evidence` | "none recorded" (present as an empty-but-real field, not absent — a later disconfirming episode fills this in without touching `statement`) |
| Qualitative strength | `strength` (enum: weak / medium / strong) | `medium` |
| Lifecycle standing (separate dimension) | `lifecycle-standing` (enum: active / disputed / superseded / rejected), on the **assertion** | `active` |

Two dimensions live at two different scopes and I keep them mechanically distinct:

- **`lifecycle-standing`** is per-*assertion* — it answers "is this specific claim still
  believed." A single episode can carry one superseded cause-assertion and one active one
  side by side.
- **`status`** (`active` / `retired`) is per-*episode*, in the `## retirement` block — it
  answers "is this episode in the ordinary rhyme-search candidate universe" (constraint 4).

These are genuinely different questions: an episode can be fully `active` for search
purposes while one of its cause-assertions has been `superseded` by a later one, or an
episode can be `retired` (consolidated away) while its assertions are still individually
`active`/true — retirement is a search-visibility switch, not a verdict on the claims.

## 6. File layout and the exact mechanism for each retrieval question

```
.agent-work/episodes/
  <run>-<seq>.md      # one file per episode, filename = id
```

No index file, no manifest, no per-artifact reverse-lookup directory. See §11 for why.

Multi-valued mechanical fields (`artifact-ref`) are written **one per line**, not comma-
joined, specifically so exact-match grep is line-anchored and cannot false-positive on a
substring (`fleet-doctrine.md` inside `fleet-doctrine.md.bak`) or false-negative on
whitespace-after-comma variance. This rhymes with the house pattern's own repeated
`- history: ...` convention in `apply_lessons_delta.py` (`current["history"] = list[...]`,
one accumulated line per entry) — same trick, applied to a field that needs exact-match
retrieval instead of just append-only narration.

- **Q1 (fetch by id).** `Read(".agent-work/episodes/<id>.md")` — direct path, O(1), no
  scan, no parse of anything except the one file requested.
- **Q2 (enumerate non-retired).**
  `rg -L -- '^- status: retired' .agent-work/episodes/*.md`
  (files *without* a retired status line). Deliberately a **negative** filter, not a
  positive `rg -l '^- status: active'` allowlist — see §9, this exact distinction is the
  adversarial fixture.
- **Q3 (exact field / set membership).**
  Scalar field: `rg -l -- '^- role: implementer' .agent-work/episodes/*.md`
  Multi-valued field: `rg -l -x -- '- artifact-ref: skills/admiral/references/fleet-doctrine.md' .agent-work/episodes/*.md`
  (`-x` line-anchors the whole line — no substring ambiguity, per the layout note above.)
- **Q4 (neighbours of episode E).** Mechanical procedure, not a search:
  1. Read E (`Q1`).
  2. For each of E's `artifact-ref` values, run `Q3` for that exact value.
  3. Run `Q3` for E's exact `(role, spine-step)` pair.
  4. Union the file sets from steps 2–3, minus E itself, minus (by default) any file that
     also matches the Q2 retired-filter.
  The union **is** the candidate set handed to the #308 sensor — complete (every episode
  sharing an exact join key is in it, by construction of the union) and unranked (the store
  does no ordering or scoring across the union; that's the sensor's job entirely).
- **Q5 (assertion set for the sensor).** Identical to Q1 — the file *is* the full assertion
  set. The sensor's actual input for a candidate pair (E, N) is: "read both files whole,
  compare their `## core-assertion` / `## suspected-cause` / `## proposed-remedy` blocks."
  Nothing more structured than that is owed to it; it receives complete text, not a summary.
- **Q6 (history-inclusive Q2–Q4).** Drop the retired-filter step: run the same `rg`
  invocations without the `-L '^- status: retired'` exclusion. Because retirement never
  deletes the file (§7), this is the *same file set plus retired files*, not a different
  data source — no separate archive to query.

## 7. Retirement policy

Retirement is a field mutation on the episode file, never a deletion or a move:

```
## retirement
- status: retired
- retired-reason: consolidated into cluster governor-drill-sibling-coverage-1
- retired-at: 2026-08-02 (audit-308-run-4)
- consolidated-into: governor-drill-sibling-coverage-1
- superseded-by:
```

All mutation goes through a validated, all-or-nothing delta script mirroring
`apply_lessons_delta.py`'s contract exactly: `apply_episode_delta.py <delta.json>` takes ops
(`add`, `add-cause`, `add-remedy`, `retire`, `supersede-assertion`), validates every op before
writing anything, and rejects the whole delta on any single invalid op. The LLM proposes the
delta; it never writes an episode file directly. (Full implementation is out of scope here —
this is the record-shape candidate — but the write path is part of "how a record is written
and read," so I'm stating its contract, not leaving it implicit.)

Ordinary rhyme-search (Q2–Q4 as given in §6) excludes `status: retired` by construction of
the negative filter. History (Q6) includes it, because the file was never removed — it is
still sitting in `.agent-work/episodes/`, still matching every `artifact-ref` and
`role`/`spine-step` grep it always matched. "Retired means excluded from ordinary search,
retained in history" is not two code paths over two data stores; it's one predicate
(`-L`/no `-L`) over one directory.

## 8. Cross-session retrieval exercise

Honest session boundary: a **new process** invoked with nothing shared but the git working
tree on disk — no shared env vars, no in-memory cache, no shared Python interpreter state.

1. **Process A** (session 1): run `apply_episode_delta.py delta_A.json` where
   `delta_A.json` has one `add` op creating `governor-268-003` as shown in §2. Process A
   exits.
2. **Process B** (session 2, freshly launched, different PID, no imported state from A):
   run `rg -l -x -- '- artifact-ref: skills/admiral/references/fleet-doctrine.md' .agent-work/episodes/*.md`.
3. **Assert:** B's output includes `governor-268-003.md`, and `Read(".agent-work/episodes/governor-268-003.md")`
   in process B returns byte-identical content to what A wrote.

This exercises Q1 and Q3 across the process boundary using only the filesystem as the shared
channel — no daemon, no cache to warm, nothing that could silently make session 1 "still
running" underneath. For durability across machines/clones (not just across processes on one
machine), the delta script's write should be followed by a normal `git add && git commit` —
that's a harness-level concern (#305's capture wiring), not a change to the retrieval
mechanism: a committed file and an uncommitted-but-present file answer Q1–Q6 identically as
long as they're in the working tree.

## 9. The harder downstream companion (neighbours of a consolidated episode)

Not designing #308's consolidation record — only confirming the episode fields give it
enough to build on, and that consolidation does not break neighbour-findability:

1. Seed three episodes across three separate runs that all carry
   `- artifact-ref: skills/admiral/references/fleet-doctrine.md`: `governor-268-003`,
   `epic-someid-011`, `epic-otherid-004`.
2. Consolidate: `governor-268-003` gets `status: retired`,
   `consolidated-into: cluster-drill-sibling-1`, `retired-reason: consolidated`.
3. Run Q4 for `epic-someid-011` with the **default** (non-retired) filter: the union from
   §6 step 2 still includes `epic-otherid-004` (still active) but drops `governor-268-003`
   (now retired) from the default candidate set — correct, that's what "excluded from
   ordinary rhyme-search" means.
4. Run Q6 (history-inclusive) for the same episode: the union now **also** includes
   `governor-268-003.md` — its file never moved, its `artifact-ref` line never changed, only
   its `status` line did. The neighbour relationship (shared artifact-ref) is timeless; only
   whether it surfaces by default changed.

This is what "must not preclude" cashes out to concretely: #308 needs no new relationship
data from me to answer "what were this consolidated episode's neighbours" — it's the same Q4
mechanism with one flag flipped.

## 10. Manifest obligation (issue #300, not designed here)

`context-manifest-ref` places exactly one obligation on #300's manifest: for a given run, an
enumerable set of `(loaded-artifact-id, canonical-revision)` pairs, addressable by a path
plus the revision it resolved at (`<path>@<revision>`, e.g. a git blob/commit hash). I am not
asking for a shape change — any content-addressable artifact under git already satisfies
this trivially by pinning to its own blob hash at capture time. If #300 lands as something
that is *not* revision-pinnable (e.g. a live-mutating index with no historical snapshot),
that's a real conflict and a float to the Admiral — but nothing in this candidate requires it
be anything other than "a file, at a revision."

## 11. Honest self-scoring

- **Depth — strong.** The four/six retrieval questions collapse to two mechanisms: a direct
  path read (Q1/Q5) and a grep with an optional retired-filter (Q2/Q3/Q4/Q6). A caller or the
  #308 sensor needs to know exactly two primitives, not a schema of storage internals. That's
  real complexity hidden behind a small seam.
- **Locality — strong.** Two artifacts total: the validated writer script
  (`apply_episode_delta.py`, mirroring the existing `apply_lessons_delta.py` contract) and a
  handful of `rg` invocations that could live in a thin `read_episodes.py` helper if callers
  want a Python API instead of shelling out. No third system, no index to keep in sync, no
  fan-out into other files when an episode is added or retired — exactly one file changes per
  operation.
- **Seam placement — strong, because it's a copy, not an invention.** "LLM proposes a JSON
  delta, a validated script applies it all-or-nothing" is the exact seam
  `apply_lessons_delta.py` already proves out in this repo. I inherited it rather than
  re-litigating it, which is the correct amount of novelty for a first accumulating store.
- **Testability — strong.** Every one of Q1–Q6 is a literal shell command; each can be
  falsified independently with a fixture that should or shouldn't appear in its output. §9's
  adversarial fixture below is the sharpest instance of this.
- **Where the constraint hurt.** Two honest costs:
  1. **Fragmentation over narrative readability.** LESSONS.md's single running file lets a
     human read "what happened this run" top-to-bottom in git diff/blame. One-file-per-
     episode optimizes machine query (Q1 especially) at the cost of that linear read — a
     human wanting "everything from governor-268" gets a directory listing, not a scroll.
     I judged this acceptable because episodes are a *machine-consumed* accumulating log
     feeding a sensor, not a human playbook (LESSONS.md keeps that job), but it is a real
     trade I made *because* of retrieval-first, not a free win.
  2. **Temptation to over-fit the field list.** Because I was designing backward from
     queries, I kept wanting one more field to make Q3/Q4 richer (a `task-class` field,
     borrowed from the LESSONS.md schema, would sharpen set-membership queries). I did not
     add it — constraint 2's agent-supplied list is exactly five fields and no more, and
     "agent effort is a real cost" argues against it even if retrieval would benefit. Named
     here because a future reviewer should know it was considered and deliberately cut, not
     overlooked.

## 12. Honest sizing

Episodes are captured at run/spine-step granularity (per constraint 2's mechanical list),
not per tool call — plausibly 1–5 per bounded Commander dispatch. Even at an aggressive
sustained rate (500 dispatches/year × 3 episodes ≈ 1,500/year), the store sits in the
hundreds-to-low-thousands of files for years of continuous use. At that size:

- A full-directory `rg` scan (Q2–Q4, Q6) over a few thousand small (~1–2 KB) Markdown files
  is sub-second even accounting for Windows NTFS's higher per-file-open overhead relative to
  Linux. **No index, manifest, or reverse-lookup structure is justified at this size**, and I
  did not build one — the brief explicitly warns that retrieval-first risks premature
  denormalization, and a write-time index (or a `by-artifact/<slug>/` symlink tree) is
  exactly that: a second surface that must be kept in sync with every add/retire, for a
  performance problem that does not exist yet.
- Where I'd revisit: past roughly 10,000–50,000 files, a full-directory grep's per-file-open
  floor cost starts to matter and a write-time reverse index (artifact-ref → episode-ids)
  would earn its keep. That's two-plus orders of magnitude past anything this design horizon
  produces. Tested/reasoned here: file count growth rate and grep-at-scale characteristics.
  Not tested: actual NTFS timing at 10k+ files (a measurement, not a design decision — I'm
  flagging the threshold, not claiming to have benchmarked it).
- What I *did* add that costs nothing extra but isn't free: one-per-line `artifact-ref`
  fields instead of comma-joined. This is not premature — it's the same grep, same file, same
  write cost, just line-anchored instead of substring-matched — so I count it as correctness,
  not denormalization.

## Adversarial fixture (see also §6, §9)

**Fixture:** an episode `episodes/fixture-disputed-001.md` whose `## retirement` block reads
`- status: disputed` — not `active`, not `retired`. (`disputed` is a legitimate value in this
design: an episode whose core-assertion has been challenged by later evidence but has not
been consolidated or rejected — still squarely "not retired.")

**What it catches:** a naive implementation of Q2 written as a *positive* allowlist —
`rg -l -- '^- status: active' episodes/*.md` — silently **omits** `fixture-disputed-001.md`
from "enumerate all non-retired episodes," even though it is unambiguously not retired and
constraint 4 requires it stay in ordinary search. This is exactly the failure mode the brief
calls out: a retrieval that silently drops a record it should have returned, with no error,
no crash — just a candidate set one file short and no signal that it's short.

The correct implementation (§6's actual mechanism) is a *negative* denylist —
`rg -L -- '^- status: retired' episodes/*.md` — which includes `fixture-disputed-001.md`
because it has no `status: retired` line to match. The fixture is the test that forces the
allowlist-vs-denylist choice to be made correctly rather than by accident: any future
addition of a new lifecycle value (`superseded`, or something not yet invented) is safe by
construction under the denylist and silently broken under the allowlist.

A second, cheaper variant worth keeping alongside it: a file at
`episodes/drafts/stray-001.md` (same valid schema, wrong directory) — the non-recursive glob
`episodes/*.md` correctly excludes it from every query. This isn't a bug to catch so much as
a pin on the glob's exact scope: if a future change swaps in a recursive glob
(`episodes/**/*.md`) without deliberate intent, this fixture would start silently returning a
file that was never meant to be in the store, which is the mirror-image failure (silent
inclusion instead of silent omission) and just as worth pinning down.
