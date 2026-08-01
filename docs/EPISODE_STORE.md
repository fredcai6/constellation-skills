# Episode Store

Status of this document: **record grammar and store doctrine, frozen at gate g1 of issue
#301.** It is the contract gates g2 (the validated writer) and g3 (retrieval) build
against. This gate ships **no executable code and no tests** — everything here is prose
plus the directory layout it describes.

Ownership boundary, stated once up front because it recurs throughout: the episode store
is the **mechanical** half of an episode memory. It captures, partitions, and makes
findable. It never judges, ranks, or decides that two episodes *rhyme* — that is a
downstream stochastic-sensor job, owned at issue #308 (§8). Automated capture wiring is
issue #305. Neither is designed here.

## 1. Why a tracked path

The store lives at repo-root **`episodes/`**, a plain git-tracked directory — **not**
under `.agent-work/episodes/`, and **not** resolved through `durable_root()`
(`scripts/agent_work_root.py`).

This is a deliberate departure from all four design-it-twice candidates
(`.agent-work/301/design-it-twice/`), which placed the store at `.agent-work/episodes/`
by inheriting the location from `.agent-work/LESSONS.md`. That inheritance was wrong for
this store, for a reason verifiable at HEAD:

```
$ git check-ignore .agent-work/episodes/ ; echo $?     # 0  -> IGNORED
$ git ls-files .agent-work/ | wc -l                    # 0  -> nothing under it is in git
$ git check-ignore episodes/ ; echo $?                 # 1  -> NOT ignored, trackable
```

`.gitignore` line 1 is `.agent-work/`. Nothing under it is in git — not even
`LESSONS.md` itself. `LESSONS.md` gets away with living there because it is a
deliberately **transitory inbox**: "where lessons pass through, not where they live." A
lesson that graduates is applied and deleted from the playbook; the playbook's job is to
carry *open* problems, not a permanent record.

The episode store is the **opposite**. Its entire purpose (§2 of the launch order's
protected intent) is **durability past consolidation**: an episode must outlive its own
consolidation so rhymes stay findable across runs, months later, from a worktree that no
longer exists. A store at `.agent-work/episodes/` would be destroyed the moment the
worktree that wrote it is swept — the opposite of durable. This is `decision:
markdown-in-git`'s storage ruling applied honestly to what "storage" has to mean for a
record that must survive worktree teardown: **Markdown, in git**, not Markdown in a
gitignored scratch directory that happens to be Markdown-shaped.

**One named seam.** The store root resolves through exactly one seam: the literal
relative path `episodes/` from the repository root. It does **not** call
`durable_root()`. `durable_root()` solves a different problem — redirecting a *linked
worktree's* `.agent-work/` reads/writes to the *main checkout's* `.agent-work/`, because
that directory is gitignored and worktree-local by construction. A tracked path needs no
such redirect: `episodes/` is the same logical directory in every worktree of the same
repo the moment a commit touches it, because that is what "tracked in git" means. Calling
`durable_root()` here would be solving an already-solved problem with the wrong tool, and
it would silently reintroduce a worktree-relative resolution path into code whose whole
point is that no such resolution is needed. See §9 for the full cross-worktree argument.

Because git does not track empty directories, this directory ships with one tracked
file, `episodes/README.md`, so the directory itself is present the moment this gate's
change is committed, before any episode exists.

## 2. Episode-id scheme

**Decided fresh, on its own merits — not cited as a panel finding.** (`COMPARISON.md`
§0 already retracted an earlier claim that all four design-it-twice candidates agreed on
an id scheme; the honest count is 2 of 4 — candidates A and D derived the id from
run+sequence, B and C used a descriptive kebab slug. That is a real, live split, not a
settled panel verdict, and this document does not lean on it as one.)

**Chosen here: `<run>-<seq>`**, e.g. `governor-268-003` — the same run-id
vocabulary the lessons machinery already uses (`governor-268`, `epic-226-lessons-audit`,
…), plus a zero-padded per-run sequence number. The sequence is derived by scanning
existing `<run>-*.md` basenames for the current maximum and incrementing; no counter file,
no UUID, nothing that can drift from the directory's own contents. **The scan must cover
every episode for that run regardless of retirement status** (a retired episode's sequence
number is still taken) — under Option B that is one glob over `episodes/`; under Option A
it is the union of `episodes/active/<run>-*.md` and `episodes/retired/<run>-*.md`. Either
way this is a mechanical detail of g2's writer, not a design choice this document is
making — see §7 for the layout question itself.

The reasoning, independent of the panel split:

- **Zero agent effort to derive.** The launch order's protected intent ranks "the
  agent-supplied half stays deliberately small" as a load-bearing priority — agent effort
  is a real cost. A run+sequence id is assignable by the harness/writer alone, from
  mechanical state (the current run id, a directory scan) with no judgment call. A
  descriptive slug requires an agent (or a human) to compose a name, which is exactly the
  kind of small-but-nonzero authoring cost the intent asks the design to avoid wherever a
  mechanical alternative exists.
- **Collision-safe by construction.** Incrementing off the existing files in the
  directory cannot collide with itself. A descriptive slug needs an explicit uniqueness
  check against existing filenames, which is machinery a run+sequence id does not need.
- **The filename doubles as a query primitive for free.** `governor-268-*.md`
  enumerates one run's episodes with a bare glob — no index, no parsing (under Option B
  that glob is `episodes/governor-268-*.md`; under Option A it is the same pattern applied
  under each of `episodes/active/` and `episodes/retired/`, per §7's seam — the property
  "the id is a free run-lookup key" holds under either, only the glob's root changes). A
  slug-only scheme loses this without also carrying the run id as a separate mechanical
  field (which it would, in `## Mechanical`, making the id itself redundant as a run-lookup
  key).
- **The honest cost, named rather than hidden**: a run+sequence id is not
  human-memorable and carries no hint of *what* the episode is about — a reader (or a log
  line) sees `governor-268-003`, not "the nonreading-vs-zero collision episode." The
  agent-supplied `task-intent` field (§4) is exactly where that description lives instead;
  the id's job is stable, mechanical addressability, not narration.

**Grammar**: `[a-z0-9][a-z0-9-]*-[0-9]{3,}` — a run-id (kebab-case, matching the
work-id vocabulary already in use across the fleet) followed by a hyphen and a zero-padded
sequence of at least 3 digits. The **basename** is the id, under either retirement-layout
option (§7): `<id>.md`. The full path that basename lives at is layout-dependent and not
settled here — under Option B (status field, in place) it is `episodes/<id>.md`; under
Option A (file moves on retirement) it is `episodes/active/<id>.md` or
`episodes/retired/<id>.md` depending on current status. Every example in this document
that writes the flat form `episodes/<id>.md` is illustrating the id, not asserting a
settled path — see §7 for the layout question itself.

## 3. Record grammar — a real worked episode, as it appears on disk

`episodes/governor-268-003.md` — Option B's path, shown for concreteness; per §2's
disclaimer, only the basename `governor-268-003.md` is settled, not this full path:

```markdown
<!-- episode-state: schema=1 id=governor-268-003 status=active -->

# episode: governor-268-003

## Mechanical
- run: governor-268
- project: constellation-skills
- role: implementer
- spine-step: g1-implement
- context-manifest-ref: ctx-governor-268-g1@a1b2c3d
- refusals: 0
- reopens: 1
- rework-count: 1
- failed-commands: 2
- artifact-ref: skills/admiral/references/fleet-doctrine.md
- artifact-ref: docs/superpowers/drills/dogfood-context-paths-absent.md

## Agent-supplied

### assertion:governor-268-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Fix the STATE_NOTE-fallback wording gap named in the launch order for the
  Commander spine.

### assertion:governor-268-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The named launch-order defect (Commander spine, PR #75/#86 pattern) is the
  only place carrying the missing-fallback wording.

### assertion:governor-268-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The Admiral spine (fleet-doctrine.md:57) carries the identical
  missing-fallback defect, unnamed by the launch order and undetected by the existing
  drill.

### assertion:governor-268-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One extra sweep pass needed to find the sibling; the drill kept reporting
  PASS on the checked-in fix while the sibling defect persisted.

### assertion:governor-268-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none.

## Diagnosis (optional)

### assertion:governor-268-003.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A drill written to prove a doctrine-text fix is load-bearing, when the
  doctrine pattern recurs across sibling role-templates, gives false confidence if it
  names only ONE sibling — re-running it only re-checks the named template.

### assertion:governor-268-003.d2
- kind: proposed-remedy
- strength: weak
- lifecycle-standing: active
- statement: When authoring or updating a drill for a doctrine pattern that recurs across
  sibling templates, the drill's "doctrine under test" line should enumerate every sibling
  template carrying the pattern, or explicitly note which ones it does NOT cover.

## Retirement
- status: active
- retired-reason:
- retired-at:
- consolidated-into:
- superseded-by:
```

A **minimal valid episode** carries only `## Mechanical`, `## Agent-supplied` (all five
fields), and an empty-valued `## Retirement` block. `## Diagnosis (optional)` is present
only when a suspected cause and/or proposed remedy exist — its **absence** (not an empty
heading) is itself the signal that diagnosis was not attempted; an episode with no
diagnosis is complete and valid.

**Rhyme / depart from `apply_lessons_delta.py`, stated explicitly.** This grammar rhymes
with the prior art deliberately: one Markdown record per unit, `- field: value` lines, an
HTML-comment state header carrying machine state, all mutation through a validated
all-or-nothing delta script so the LLM never writes a record directly (§6). It departs in
three places, and here is why:

1. **One file per episode, not one growing file.** `LESSONS.md` is a single running
   playbook because it is read top-to-bottom by a human. Episodes are captured by several
   concurrent Commanders in separate worktrees; a shared mutable file is a merge-conflict
   generator under that concurrency, and nothing about the episode store's job needs
   linear human readability the way the playbook does.
2. **No counters, no cap, no dormancy/auto-expiry.** `LESSONS.md` curates an *evolving*
   claim that gets reconfirmed over time, so it needs mentions/confirmed/disconfirmed
   counters and a cap to keep the bank from growing unbounded. An episode is a *raw,
   atomic capture*, written once and then either stands or is retired (§7) — the
   adjudication machinery that is right for a curated playbook is over-engineering for a
   write-once record.
3. **The agent-supplied bin is individually addressable per field; the mechanical bin is
   not.** See §5 — this is new structure `apply_lessons_delta.py` has no analogue for,
   because a lesson's `statement` is a single evolving claim, not five independently
   assertable facts about one occurrence.

## 4. The partition — literal section headings, not implied by field naming

The record carries two bins, visibly separated by an `## `-level heading, always written
even when a bin's optional contents are empty (so `grep '^## '` enumerates the schema on
every file, not just a populated one):

- **`## Mechanical`** — zero agent effort, captured by the harness/engine at write time:
  `run`, `project`, `role`, `spine-step`, `context-manifest-ref`, `refusals`, `reopens`,
  `rework-count`, `failed-commands`, `artifact-ref` (repeated, one per line). Flat
  `- key: value` lines. **No `strength` and no `lifecycle-standing` on these lines** —
  see §5 for why, and for how a mechanical fact is disputed if it ever needs to be.
- **`## Agent-supplied`** — deliberately small: exactly the five fields the launch order
  names, no more. `task-intent`, `expected-behavior`, `observed-behavior`, `impact-cost`,
  `workaround`. Each is its own `### assertion:<id>.a<n>` block with its own
  `lifecycle-standing` (§5).
- **`## Diagnosis (optional)`** — `suspected-cause` and `proposed-remedy` are **separate,
  optional assertions**, not ordinary fields of either bin above. Zero, one, or many of
  each may be present; an episode with none is complete and valid. Each is independently
  addressable, exactly like the agent-supplied bin.

**Partition enforcement is a g2 obligation, stated here, not built here.** This gate ships
no code. The obligation this document places on gate g2's writer
(`scripts/apply_episode_delta.py`): the create/amend payload must hard-split into the
three bins with a field-name allowlist per bin, and **reject** a delta where a field
appears under the wrong bin. That is what makes the partition *enforced*, not merely
documented — a rule, not a habit. Stating the obligation here satisfies "the partition is
explicit" for this gate; the validator that makes a misfiled field a hard write-time error
is g2's deliverable.

## 5. Per-field assertion addressability — agent-supplied bin only

Every `### assertion:<episode-id>.a<n>` block in `## Agent-supplied`, and every
`### assertion:<episode-id>.d<n>` block in `## Diagnosis`, carries its own
`lifecycle-standing` (`active` / `disputed` / `superseded` / `rejected`) and `strength`
(`weak` / `medium` / `strong`). Mechanical facts in `## Mechanical` do **not** — they stay
flat `- key: value` lines with no strength and no standing field at all.

This asymmetry is deliberate, not an oversight:

- **Mechanical facts have no epistemic status to argue about.** Nobody will supply
  challenging evidence against a `rework-count` the engine itself incremented. Giving
  every mechanical fact a `strength`/`standing` pair would manufacture a stored belief
  assessment about a claim nobody asserted — which is a real cost the assertion-native
  design-it-twice candidate (`candidate-B-assertion-native.md`) named honestly and this
  document deliberately avoids paying for facts that will never be disputed.
- **If a mechanical fact ever IS disputed** (e.g. a later audit finds `rework-count`
  double-counted a retried command), that dispute is never edited into the `## Mechanical`
  block. A new **agent-supplied** assertion is added instead — `kind:
  mechanical-dispute`, statement citing the specific mechanical field and the correction —
  and that new assertion carries its own `lifecycle-standing`. The mechanical line itself
  is never mutated; the record grows, it does not get rewritten. This is what
  non-foreclosure costs zero to satisfy here: the escape hatch already exists in the
  agent-supplied bin's ordinary shape, so disputing a mechanical fact needs no new
  mechanism.
- **Agent-supplied claims are exactly the ones that get disputed** — a reviewer's later
  read of `observed-behavior`, a corrected `impact-cost` estimate — so they need
  individually addressable standing from the start.

**Worked walk-through: disputing one field while a sibling stays active, no rewrite.**
Take the worked episode in §3. Suppose a later reviewer, re-reading `governor-268-003`,
concludes the `impact-cost` assertion (`a4`) over-counted — only one sweep pass was
actually needed, not two — while `observed-behavior` (`a3`) is independently confirmed
correct. The write path is one `amend-assertion` op (g2's writer, out of scope here) that
changes exactly `a4`:

```diff
 ### assertion:governor-268-003.a4
 - kind: impact-cost
 - strength: medium
-- lifecycle-standing: active
+- lifecycle-standing: disputed
 - statement: One extra sweep pass needed to find the sibling; the drill kept reporting
   PASS on the checked-in fix while the sibling defect persisted.
+- history: disputed 2026-08-05 (reviewer-audit-268) — re-read of the sweep transcript
+  found only one pass was actually needed; the "extra" pass was the ordinary re-run, not
+  a second discovery.
```

**What changes:** `a4`'s `lifecycle-standing` line, plus an appended `history` entry
recording who disputed it and why (append-only, same convention `apply_lessons_delta.py`
already uses for its own `- history:` lines).

**What does not change:** `a1`, `a2`, `a3`, `a5`, every `## Mechanical` line, both
`## Diagnosis` assertions, the episode's own `## Retirement` block (§7), and the episode's
filename/id. `a3` (`observed-behavior`) stays exactly `lifecycle-standing: active` — a
reviewer disputing one claim in an episode never forces a rewrite of, or even a touch to,
any sibling claim. That is the concrete demonstration this document owes: an episode
*never needs rewriting later* to become expressible under Stratum A, because it already
*is* Stratum A assertions from the moment it is written (§6), and disputing one of them is
a one-field, append-history mutation, not a record-shape change.

## 6. The Stratum A mapping — concrete, against the worked example

| Stratum A dimension | Episode field | Value in the worked example (`a3`) |
|---|---|---|
| Identified assertion (the claim) | `### assertion:<id>.a<n>` block's `- statement:` | "The Admiral spine (fleet-doctrine.md:57) carries the identical missing-fallback defect, unnamed by the launch order and undetected by the existing drill." |
| Stable assertion identity | the heading itself | `assertion:governor-268-003.a3` |
| Source | implicit: the episode's own `## Mechanical` `run`/`role`/`spine-step` fields, read alongside the assertion — an agent-supplied assertion's source is always "the agent named by the episode's own mechanical `run`/`role`", so it is not a separately repeated field | run=governor-268, role=implementer |
| Supporting evidence | `## Mechanical` `- artifact-ref:` lines the episode already carries, cross-referenced by the reader | `artifact-ref: skills/admiral/references/fleet-doctrine.md` |
| Challenging evidence | a later, separate assertion (this episode's or another episode's) that names this one, per the amend walk-through in §5 | none recorded for `a3` in this worked example — see `a4`'s dispute above for a populated instance |
| Qualitative strength | `- strength: weak\|medium\|strong` | `strong` |
| Lifecycle standing (**separate dimension**) | `- lifecycle-standing: active\|disputed\|superseded\|rejected` | `active` |

**Two dimensions live at two different scopes, and this design keeps them mechanically
distinct, never conflated:**

- **`lifecycle-standing`** is per-*assertion* (§5) — "is this specific claim still
  believed?" One episode can carry a superseded diagnosis assertion side by side with an
  active agent-supplied one (§7's worked retirement example makes the same point at the
  episode level).
- **`status`** (`## Retirement`, §7) is per-*episode* — "is this episode in the ordinary
  rhyme-search candidate universe?" These are genuinely different questions: an episode
  can be `retired` (excluded from ordinary search) while every one of its assertions
  stays `lifecycle-standing: active` — retirement is a **search-visibility switch**, not a
  verdict on the claims it contains.

**Why this is non-foreclosure "shown, not promised."** There is no second shape to
translate into later. The on-disk record's own headings and fields *are* the Stratum A
vocabulary — `statement`, `strength`, `lifecycle-standing` are literal field names on
literal blocks, not values a future migration would derive by parsing prose. A design
that satisfied Stratum A expressibility only by promising a future mapping function would
fail the launch order's non-foreclosure obligation by definition; this table exists
because the mapping is already true of the file on disk today, demonstrated against a
concrete example rather than asserted in the abstract.

## 7. Retirement

**Policy (settled — stated here):**

- Retirement means **excluded from ordinary rhyme-search, RETAINED in history.** Never
  deletion, never truncation.
- Retiring an episode requires a **non-empty reason**, validated at write time by g2's
  writer (mirroring `apply_lessons_delta.py`'s own mandatory `retire` reason — inherited,
  not re-decided).
- Retiring an episode never touches any assertion inside it. `lifecycle-standing` on an
  agent-supplied or diagnosis assertion, and `status` on the episode itself, are separate
  operations (§6) — a consolidation pass that wants both must issue two separately-grounded
  writes, never one op that does both.

Worked example, continuing `governor-268-003` from §3 — the episode is later folded into a
consolidated pattern episode:

```diff
 ## Retirement
-- status: active
-- retired-reason:
-- retired-at:
-- consolidated-into:
+- status: retired
+- retired-reason: consolidated into cluster governor-drill-sibling-coverage-1
+- retired-at: 2026-08-12 (audit-308-run-4)
+- consolidated-into: governor-drill-sibling-coverage-1
 - superseded-by:
```

Nothing else in the file changes. `a1`–`a5` and `d1`–`d2` keep whatever
`lifecycle-standing` they already had. The episode's **content** is never deleted or
truncated by retirement — that much holds under either layout option below. Shown here
**under Option B** (defined next): "retained in history" is one field flip on the same
file at the same path, not a second data store to keep in sync — the file itself never
moves. Under **Option A**, the identical field update happens (the same `status` /
`retired-reason` / `retired-at` / `consolidated-into` diff shown above), but it is
accompanied by a file **move** between `episodes/active/<id>.md` and
`episodes/retired/<id>.md`. Content-preservation is settled; whether the file's *path*
also stays fixed is exactly the layout question below, not a blanket property of
retirement asserted here.

**Layout — HELD OPEN, not chosen here.** Whether retiring an episode:

- **(Option A) moves the file** between `episodes/active/<id>.md` and
  `episodes/retired/<id>.md`, so "ordinary search" means globbing `active/` — the default
  is correct by construction, and "which set is this episode in" is a filesystem fact,
  structurally immune to a malformed or hand-edited `status` line; **or**
- **(Option B) changes a `status` field** in place (as shown in the diff above) and
  ordinary search filters it out negatively (files *without* `status: retired`) — the file
  path never changes, so an id-based cross-reference (`consolidated-into:`,
  `superseded-by:`) never needs re-resolving after a retirement, at the cost of ordinary
  search being a content-parsing operation rather than a filesystem one, which is more
  exposed to a silent-omission failure if a free-text agent-supplied field ever embeds a
  line that looks like a status marker (see the single-line-enforcement note below).

is a **named open seam**, deliberately **not resolved by this document**. Both options are
live, real trade-offs (locality/testability favor A's structural immunity to
content-parsing failure modes; a stable file path favors B's simpler cross-reference
story) argued at length in `.agent-work/301/design-it-twice/COMPARISON.md` §7, where the
Commander's own lean flipped once under a cold critic — itself evidence this is a genuine,
live judgment call and not a foregone one. It is **held for human ratification** and will
be **bound at gate g4**.

**The retirement write-side seam — how g2's writer stays layout-agnostic too, not only
g3's reads.** The worked diff above (`status`/`retired-reason`/`retired-at`/
`consolidated-into`) is the entire **content** effect of a retire operation, and it is
identical under either layout option — nothing about it depends on which one binds. What
is *not* identical is the **layout effect**: whether that write is also accompanied by a
file move. g2's writer (`scripts/apply_episode_delta.py`, §10) must route every retire op
through exactly one seam, **`apply_retirement(episode_id, reason)`**, so that effect —
like the read-side effects below — is bound at g4 by an adapter swap, never by a rewrite
of the writer itself:

- **Option-A adapter** — performs the field diff above, then moves the file from
  `episodes/active/<id>.md` to `episodes/retired/<id>.md`.
- **Option-B adapter** — performs the field diff above only; the file's path never
  changes.

g2's writer calls `apply_retirement()` for every retire op and must not inline a file-move
or an in-place-only write at the call site. Both adapters share the identical content
update; only the layout effect differs, and only that half is what g4 binds.

**The membership-predicate seam — how g1–g3 stay layout-agnostic in practice, not just in
name.** Nothing in gates g1–g3 may assume either answer, and that has to be true of the
*implementation* g3 writes, not merely of a primitive's caller-facing name. This document
therefore names one seam, exactly parallel to §1's treatment of `durable_root()`:
**`is_episode_in_ordinary_search(episode_id)`** — the single place any retrieval primitive
asks "is this episode currently in the ordinary rhyme-search candidate set." Two adapters
can satisfy that seam, one per layout option; g4 binds exactly one, and only one may exist
at a time:

- **Option-A adapter** — a directory check: does `episode_id`'s file resolve under
  `episodes/active/` (as opposed to `episodes/retired/`)?
- **Option-B adapter** — a status check: does the episode's `## Retirement` `status` field
  read anything other than `retired` (line-anchored — see the single-line-enforcement
  obligation below)?

Every g3 retrieval primitive that needs to respect retirement (enumerate non-retired
episodes, any select/neighbour-enumeration restricted to the ordinary-search set) **calls
`is_episode_in_ordinary_search()`**; it must **not** inline a directory check or a status
grep at the call site — that inlining is exactly what would turn "bind the layout at g4"
into a retrieval rewrite instead of an adapter swap. Fetch-by-id (§8) needs no membership
check at all — but it does need its own path-resolution seam, since which directory (if
any) holds the file is exactly the layout question; see `resolve_episode_path()` below,
which is a distinct concern from this seam, not a substitute for it. With the seam named
this way, binding the layout at g4 means writing the chosen adapter (on the order of a
handful of lines) and wiring it in at the seam — g3's primitives, and this document's §§6,
8 description of them, do not change. **That is what makes "additive, not a rewrite" true
of g3's actual retrieval code, not only of the primitive's name** — the distinction the
seam exists to close.

**The base-enumeration seam — the other half of "enumerate," not yet named above.** The
membership seam above answers "is this one id in the ordinary-search set"; every g3
primitive that scans the store also needs an answer to a prior question — "what candidate
ids exist to ask that about in the first place" — and that half was, until now, only
worked out for one caller (§2's id-sequence scan) and left unspecified for retrieval. This
document names that second seam too, **`iter_episode_ids(include_retired)`**, parallel in
kind to the membership seam and to §2's own already-worked treatment of its sibling case:

- **Option-A adapter** — lists `episodes/active/*.md`; when `include_retired` is true,
  additionally unions in `episodes/retired/*.md` (exactly the union §2 already specifies
  for the id-sequence scan, which always calls this seam with `include_retired=true`,
  since a retired episode's sequence number is still taken).
- **Option-B adapter** — lists `episodes/*.md` unconditionally; `include_retired` is a
  no-op for this adapter's own filtering, because status is not encoded in the path — the
  retired/active split is left entirely to the per-id membership seam above.

**Composition rule, so correctness never depends on which adapter is bound.** "Enumerate
non-retired episodes" (§8) is `iter_episode_ids(include_retired=False)` followed by
confirming each returned id through `is_episode_in_ordinary_search()` before including it
— scan, then filter, always both steps, never one folded into the other. This is
deliberate, not redundant-and-removable: under Option A the base scan already excludes
`episodes/retired/` on its own, so the per-id confirmation is a no-op in practice — but
g3's code does not special-case that; it always performs both steps, so the same code path
stays correct regardless of which adapter g4 eventually binds. §2's id-sequence scan, by
contrast, calls `iter_episode_ids(include_retired=True)` alone, with no membership filter
afterward, because every episode's sequence number counts regardless of retirement — that
existing treatment is now this seam's other caller, not a bespoke one-off.

**The fetch-by-id path-resolution seam.** A "direct path read" (§8) is only actually
direct once the reader knows which path to read, and that is exactly the layout question
for an id whose retirement status is unknown to the caller. This document names a third
seam, **`resolve_episode_path(episode_id)`**, returning the one on-disk path to read:

- **Option-A adapter** — checks `episodes/active/<id>.md`; if absent, checks
  `episodes/retired/<id>.md`. (Exactly one of the two exists for any valid id — an episode
  is never in both places at once.)
- **Option-B adapter** — always `episodes/<id>.md`; no check needed.

Fetch-by-id calls `resolve_episode_path()` and reads whatever path it returns; it never
constructs a path itself. This answers "where is it," a distinct question from "is it in
the ordinary-search set" above — fetch-by-id, needing no membership check, needs exactly
this seam and nothing else.

**Single-line enforcement, named as an obligation on g2's writer and on the Option-B
adapter specifically, regardless of whether Option B is the one eventually bound.** A
negative "not retired" filter over `## Retirement`'s `status` field — the check the
Option-B adapter above performs — is more exposed to a silent-omission bug than a positive
allowlist would be: if an agent-supplied free-text field (e.g. `observed-behavior`) spans
physical lines and a continuation line happens to read `- status: retired` — easy, if an
agent pastes a transcript that itself discusses a retired episode — a naive line-oriented
parser would match that line and silently exclude a fully active episode from ordinary
search, with no error and no crash. (The Option-A adapter has no analogous exposure: a
directory check never parses free text.) g2's writer must therefore enforce **single-line
values on every agent-supplied free-text field** (reject a delta whose value spans
physical lines outside a documented continuation convention), and the Option-B adapter,
if bound, must **line-anchor** its filter (`-x` / `^...$`, not a bare substring match) —
both stated here as obligations this record shape places on the gates that build on it,
not implemented in this gate.

**The full seam set, gathered in one place.** Five things in this store route through
exactly one named mechanism each, and gates g1–g3 must call each by name — never inline
the path, glob, grep, or move it stands for:

| Concern | Named seam | Adapters (bound at g4) |
|---|---|---|
| Store root | the literal path `episodes/` (§1) | none — layout-invariant, same under either option |
| Retirement write | `apply_retirement(episode_id, reason)` (above) | Option A: field diff + file move · Option B: field diff only |
| Per-id membership | `is_episode_in_ordinary_search(episode_id)` (above) | Option A: directory check · Option B: status check |
| Base enumeration | `iter_episode_ids(include_retired)` (above) | Option A: directory union · Option B: flat glob |
| Fetch-by-id path resolution | `resolve_episode_path(episode_id)` (above) | Option A: try `active/`, then `retired/` · Option B: fixed path |

The store root needs no adapter at all — it is unaffected by which option binds. The
other four each carry exactly two adapters; binding the retirement layout at g4 means
writing the four chosen adapters (one per layout-affected row, on the order of a handful
of lines each) and wiring each in at its named seam. No primitive's shape, and no
primitive's description anywhere in this document, changes when that binding happens —
that is what "additive, not a rewrite" means for the whole store, not only for one seam
in isolation.

## 8. Mechanical only — no ranking, no similarity, no embedding

This store never guesses. It exposes stable ids, enumerable fields, and exact-match /
set-membership retrieval — nothing more. Concretely, every retrieval primitive this record
shape supports is built entirely from the named seams in §7, never from an inlined path,
glob, or grep at the call site:

- **Fetch by id** resolves the on-disk path through `resolve_episode_path()` (§7) and
  reads it directly — no scan, no membership check.
- **Enumerate non-retired episodes** obtains its candidate id set from
  `iter_episode_ids(include_retired=False)` (§7), then confirms each id through
  `is_episode_in_ordinary_search()` (§7) before including it — the scan-then-filter
  composition §7 specifies, never a filter that also does its own scanning.
- **Select by exact field value restricted to the ordinary-search set**, and **enumerate
  the neighbours of an episode by shared exact join key**, both scan the same
  `iter_episode_ids(include_retired=False)` candidate set before applying their own
  field/key match — identical composition to enumeration, just with an extra predicate
  layered on top.

None ranks, scores, embeds, or infers similarity. Finding that two
episodes **rhyme** — the actually useful, actually hard question — is explicitly a
downstream LLM sensor's job, owned at issue #308, and is out of scope for this store by
design (governing principle B0.1, the stochastic boundary: stochastic work happens
upstream of canon, and between canonical truth and an agent's active surface every
transformation the store itself performs is deterministic and attributable). The store's
job is to hand that sensor a **clean, complete, enumerable candidate set**; the sensor's
stochastic judgment happens entirely on top of what this document specifies, never inside
it.

**The obligation this store's `context-manifest-ref` field places on issue #300's
projection manifest** (running concurrently in another worktree; not designed here): for a
given run, the manifest must expose an enumerable set of `(loaded-artifact-id,
canonical-revision)` pairs. This record stores that as an opaque-to-the-store reference
plus the revision it resolved at (`<manifest-ref>@<revision>`, as in the worked example's
`context-manifest-ref: ctx-governor-268-g1@a1b2c3d`). Any content-addressable artifact
under git satisfies this trivially by pinning to its own blob hash at capture time; no
shape change to #300 is being requested here. If #300 lands as something that is *not*
revision-pinnable (a live-mutating index with no historical snapshot), that is a real
conflict and a float to the Admiral at that point — not something resolved in this
document.

## 9. Cross-worktree sharing — through git itself

The store needs no daemon, no shared filesystem mount, and no `durable_root()` redirect,
because sharing across worktrees is exactly what committing a tracked file to git already
does. (As throughout this document, `episodes/<id>.md` below is the id's basename, not a
settled path — see §2's disclaimer. This section's argument is about git's own
commit/merge/fetch mechanics, not about which subdirectory a file lives under, so it holds
unchanged under either retirement-layout option.) The steps:

1. A commander in worktree W writes `episodes/<id>.md` (via g2's future writer) and
   commits it on its own branch, inside its own worktree — every commander only ever
   writes files inside the worktree it owns.
2. That commit merges to `main` (ordinary PR/merge flow, the same path any other change in
   this repo takes).
3. From that point on, `episodes/<id>.md` is visible in **every** worktree that has that
   commit — a `git pull`/`git fetch` + checkout in any other linked worktree, and any
   fresh `git clone` of the repo, sees the identical file content, because that is the
   definition of a tracked path in a shared git history.

**This needs no `durable_root()`.** `durable_root()` exists to solve a narrower problem —
redirecting *reads and writes of a gitignored, worktree-local directory* to one canonical
location (the main checkout) so N linked worktrees do not each accumulate their own siloed
copy of something that was never going to be committed. A tracked path has no such
siloing problem in the first place: there is exactly one canonical copy the moment a
commit lands, and git's own object model is the synchronization mechanism. Calling
`durable_root()` on a tracked path would be redundant at best and actively wrong at worst
(it would make episode resolution depend on worktree topology for a file whose whole
point is to be independent of it).

**This is unaffected by the epic-lease exception.** `durable_root()`'s one exception
(honor the worktree instead of redirecting to the main checkout, when the main checkout
holds an active Admiral epic lease) exists specifically because that redirect target can
be fenced read-only. The episode store never redirects anywhere — its target is always
"the caller's own worktree's `episodes/` directory, followed by an ordinary commit" — so
there is no redirect target to fence, and no exception logic that could apply to it.

**This is unaffected by the read-only fence on the main checkout.** The fence exists to
stop a linked worktree from writing into the main checkout's working tree while an Admiral
epic is live there. It never applies to a commander's own writes inside its own worktree,
which is the only place this store's writer ever writes. Cross-worktree visibility for
this store is achieved entirely downstream of that local write, through the ordinary
commit-and-merge path in point 2 above — never through any process reaching into another
worktree's files directly.

## 10. What this gate did not build

No executable code, no tests. The obligations this document places on later gates, named
so they are not rediscovered from scratch:

- **g2** builds `scripts/apply_episode_delta.py`: the validated, all-or-nothing delta
  writer (mirroring `apply_lessons_delta.py`'s contract) that is the **only** write path —
  the LLM never writes an episode file directly. It enforces the partition allowlist
  (§4), the mandatory non-empty retire reason (§7), and single-line enforcement on
  agent-supplied free-text fields (§7). Its retire op routes through the
  `apply_retirement()` seam (§7) — never an inlined file-move or in-place-only write.
- **g3** builds deterministic retrieval (fetch by id, enumerate non-retired, exact/
  set-membership select, neighbour enumeration) and the cross-session / cross-worktree
  acceptance exercise: write from one process, read from a genuinely separate one sharing
  nothing but the git working tree — extended to a real worktree boundary, not just a
  process boundary, per this document's §9. Every primitive is built from the read-side
  seams named in §7 (`resolve_episode_path`, `iter_episode_ids`,
  `is_episode_in_ordinary_search`) — never from an inlined path, glob, or grep.
- **g4** binds the retirement layout (§7) — file-move vs status-field — once Tommy
  ratifies it, and updates this document's §7 to record the bound choice.
- **#305** wires automated capture. **#308** builds the rhyme-detection sensor and the
  consolidation/adjudication loop on top of what this store exposes (§8). Neither is
  designed here.
