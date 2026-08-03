# Episode Store

Status of this document: **record grammar and store doctrine.** Frozen at gate g1 of
issue #301 as the contract gates g2 (the validated writer) and g3 (retrieval) built
against; **updated at gate g4**, which bound the one question g1 deliberately left open —
the retirement layout (§7) — and shipped the retirement-dependent retrieval §§8/10 had
described in advance. Everything described here now exists.

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
this store, for a reason verifiable by command — **re-measured at issue #308, because the
transcript this section originally carried went stale.**

```
$ git check-ignore .agent-work/ ; echo $?              # 1  -> NOT ignored
$ git ls-files .agent-work/ | wc -l                    # 1958
$ git check-ignore episodes/ ; echo $?                 # 1  -> NOT ignored, trackable
```

**What changed, and why the ruling survives it.** When this section was frozen at issue #301
gate g1, `.agent-work/` was gitignored and held nothing in git, and §1 used that as its
illustrative contrast. Commit `b69e6c8` (issue #326, *"chore: track `.agent-work/` — run
history is project history"*) reversed that for an unrelated reason, and nobody revisited
this paragraph. Issue **#348** tracks it; the numbers above are pinned to `4cec87a`.

The correction does **not** disturb the location decision, and the distinction is the point:
the argument for `episodes/` never rested on `.agent-work/` being *ignored*. It rests on the
store needing to be **tracked in git** so it survives worktree teardown and a fresh clone —
which `episodes/` is, unchanged. What went stale was the contrast, not the ruling. A reader
who found the old transcript and concluded the storage decision was unfounded would have been
misled by a true-when-written claim, which is exactly the failure this store exists to make
findable.

`LESSONS.md` lives under `.agent-work/` because it is a deliberately **transitory inbox**:
"where lessons pass through, not where they live." A lesson that graduates is applied and
deleted from the playbook; the playbook's job is to carry *open* problems, not a permanent
record. As of issue #308 that inbox is retired as a live-agent input entirely — see
`docs/CONSTELLATION_OVERVIEW.md` § "Truth layers".

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

Because git does not track empty directories, the store ships tracked placeholders so the
layout is present the moment the change is committed, before any episode exists:
`episodes/README.md` at the flat root, and `episodes/active/.gitkeep` /
`episodes/retired/.gitkeep` in the two scanned directories.

**The two scanned directories deliberately hold `.gitkeep` and not `README.md`, and that is
not a style preference.** Membership is decided by `episode_id_for()` (§7), which applies the
store's own id grammar to every `*.md` it lists. A `README.md` inside `active/` or `retired/`
is therefore a `*.md` whose stem is not a well-formed id — the classifier refuses it, as it
should. `.gitkeep` sits outside the store's file grammar entirely, so it is never a candidate
in the first place.

The first attempt at this gate got exactly this wrong: it shipped `README.md` in all three
directories and excluded them with a hand-maintained filename allowlist consulted only at the
flat root. The result was that the store as shipped **could not be read by its own tooling** —
the stem `README` became a phantom episode id in both scanned directories at once. See §7's
trap 4. `NON_EPISODE_FILENAMES` survives for the flat root only, where there is no grammar to
lean on.

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
number is still taken) — the union of `episodes/active/<run>-*.md` and
`episodes/retired/<run>-*.md`, which the writer obtains from the base-enumeration seam
(`iter_episode_ids(include_retired=True)`, §7) rather than globbing itself.

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
  enumerates one run's episodes with a bare glob — no index, no parsing (the pattern
  applies under each of `episodes/active/` and `episodes/retired/`, per §7's seam; which
  of the two to scan is exactly the ordinary-vs-history choice §7 makes deliberate). A
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
sequence of at least 3 digits. The **basename** is the id: `<id>.md`. Which directory
holds it is its retirement status (§7) — `episodes/active/<id>.md` while it is in the
ordinary rhyme-search set, `episodes/retired/<id>.md` once retired. A file at the flat
`episodes/<id>.md` belongs to neither set and is **malformed**; §7 explains why that is
refused rather than skipped.

## 3. Record grammar — a real worked episode, as it appears on disk

`episodes/active/governor-268-003.md` — an episode in the ordinary rhyme-search set;
retiring it moves the same file to `episodes/retired/governor-268-003.md` (§7):

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
   claim that gets reconfirmed over time, so it carries mentions/confirmed/disconfirmed
   counters. It also carried a 20-entry cap for the same reason — until #308 removed it,
   having measured that a cap does not bound a bank so much as silently drop from it, and
   at 20/20 refuses new entries outright. Bounding is now the Curator's regular cleanup
   pass, in both stores. This contrast therefore holds on the counters and no longer on
   the cap. An episode is a *raw,
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
truncated by retirement. The field diff above is the whole content effect; it is
accompanied by a file **move** from `episodes/active/<id>.md` to
`episodes/retired/<id>.md`, per the ratified layout below.

**Layout — RATIFIED (2026-08-01), bound at gate g4.** Held open through gates g1–g3 for
human ratification; ruled by Tommy, verbatim:

> *"move the file, prefer to keep files clean of history unless they're historical.
> archives are available strats."*

**Option A binds: retiring an episode MOVES its file** between `episodes/active/<id>.md`
and `episodes/retired/<id>.md`. "Ordinary search" means scanning `active/`, so the
default is correct by construction, and "which set is this episode in" is a filesystem
fact — structurally immune to a malformed, hand-edited, or forged `status` line, because
nothing parses one to decide.

**The archive principle** — the ruling's second half, which is a design rule and not
decoration. *Files stay clean of history unless they are themselves historical, and an
archive is a legitimate separate strategy.* So `episodes/retired/` is a **genuine
archive, not a second live search space that every query has to remember to exclude**.
Ordinary retrieval scans `active/` and never looks at `retired/`; history-inclusive
retrieval is a deliberate, separate act. Mechanically (§8): every scanning primitive
takes `include_retired`, defaulting to **False**. An opt-*out* default would turn every
future caller's forgotten filter into a silent correctness bug — which is the failure
class this whole store is written against.

**Option B, and why it is recorded rather than deleted.** The rejected alternative
changed a `status` field in place (the diff above) and had ordinary search filter it out
negatively — files *without* `status: retired`. Its real advantage: the file path never
changes, so an id-based cross-reference (`consolidated-into:`, `superseded-by:`) never
needs re-resolving after a retirement. Its real cost, and the reason the seams below
exist: ordinary search becomes a content-parsing operation rather than a filesystem one,
which is exposed to a silent-omission failure if a free-text agent-supplied field ever
embeds a line that looks like a status marker (see the single-line-enforcement note
below). Both were live, real trade-offs, argued at length in
`.agent-work/301/design-it-twice/COMPARISON.md` §7, where the Commander's own lean
flipped once under a cold critic. **The reasoning is kept because it is why the seams
exist** — a reader who finds four adapter functions and no record of the second candidate
would reasonably conclude the indirection was unearned. Option A's cross-reference cost
turned out to be small in practice: fetch-by-id resolves through `resolve_episode_path()`
and reaches the archive, so a cross-reference to a retired episode never dangles.

**What binding Option A did NOT do: it relocated the silent-omission class rather than
removing it.** Option B's trap was a positive allowlist over a parsed field — enumerating
`status: active` silently dropped a legitimately-not-retired `disputed` episode. That
specific trap is now structurally impossible. Three others took its place, and each has
an adversarial fixture in `tests/test_episode_store.py`:

1. **a glob that misses a subdirectory** — `episodes/*.md`, correct before the layout
   gained `active/`/`retired/`, now silently returns nothing (indistinguishable from an
   empty store) or only strays;
2. **a history-inclusive enumeration that forgets to union both directories** — the
   caller explicitly asked for history and silently gets half of it, in a non-empty
   answer that looks plausible;
3. **a stray file at the old flat path** (`episodes/<id>.md`) — it belongs to *neither*
   set, so ordinary *and* history-inclusive retrieval both omit it while the file sits
   there looking like a stored episode. This is the live migration hazard, and note that
   `episodes/README.md` already lives at that flat root: the exclusion of the store's own
   documentation is therefore a **named allowlist** (`NON_EPISODE_FILENAMES`), never a
   glob shape that happens not to match it. A stray is **surfaced as malformed**, not
   skipped — by the enumeration seam, so the writer's own id-assignment scan inherits the
   refusal too and cannot mint an id a stray already holds;
4. **a non-episode file INSIDE a layout directory** — the mirror image of (3), and the
   one that actually shipped at the gate's first attempt. Membership moved from file
   *content* to file *location*, so a directory listing became the candidate set and
   anything sitting in the directory was minted into an id no record backs. The gate's
   own tracked placeholders, `active/README.md` and `retired/README.md`, produced the
   phantom id `README` in **both** sets and made the whole store unreadable by every
   primitive it ships;
5. **a store root or layout directory that is not there at all** — `Path.glob` over a
   missing directory returns empty, so a typo'd `--store-root`, or a layout that was
   never committed (git does not track empty directories, and this layout is two of
   them), answers `count: 0, exit 0`. That is (1)'s own failure description reached by a
   different route;
6. **a Markdown file one level deeper** (`episodes/archive/<id>.md`,
   `episodes/active/old/<id>.md`) — invisible to every one-level scan while looking, to a
   human reading the tree, exactly like a stored record.

**The classifier is derived, not enumerated — this is the rule that keeps (3)–(6)
closed.** "Is this file an episode?" is answered by the store's OWN id grammar (§2), in
one named function, applied uniformly in all three directories:
**`episode_id_for(path)`** returns the episode id for `<well-formed-id>.md` and `None` for
everything else. A hand-maintained list of filenames cannot do this job: the first attempt
used one, consulted at the flat root only, and it failed in the way such lists always fail
— the layout gained two directories, membership moved with it, and the classifier stayed
behind. An id grammar cannot drift from itself, needs no edit when someone adds a
`.gitkeep` or a `CODEOWNERS`, and would have refused a bad placeholder **at authoring
time** rather than at first read. `NON_EPISODE_FILENAMES` survives for the one place a
grammar cannot help — the store's own README at the flat root — and is scoped to that
directory and nowhere else.

Consequently the tracked layout directories are kept alive by a **`.gitkeep`**, not a
`README.md`: git needs a tracked file in each or the layout vanishes at commit, and inside
`active/`/`retired/` a `.md` file that is not a well-formed episode is **refused as
malformed**. What the two directories are for is documented in `episodes/README.md`, at
the level where a non-episode file is legitimate.

**The retirement write-side seam.** The worked diff above (`status`/`retired-reason`/
`retired-at`/`consolidated-into`) is the entire **content** effect of a retire operation.
The **layout effect** — the file's move into the archive — is a separate concern, and the
two are deliberately kept apart: `scripts/apply_episode_delta.py` routes the content half
through **`apply_retirement(episode, reason)`** and the layout half through
**`destination_for(episode, root, current_path)`**. The latter owns the test on the
episode's own status too, so no call site reads that field to pick a path — a caller that
branched on `status` itself and then chose a directory would be an inlined layout check
wearing a delegation's clothes. No call site inlines either a field-only write or a file
move.

**Half-retirement is ruled out by construction, not by care.** A retirement whose field
update landed and whose move did not (or the reverse) is a corrupt store: it reads as
retired while still sitting in the ordinary-search set, and nothing about it is loud. The
writer makes that state unrepresentable rather than merely unlikely — the updated content
is only ever rendered to the **new** path, so one write-plan entry carries both halves and
there is no plan in which they can disagree. Placement then compensates: the transaction
snapshots the prior bytes of every path it is about to disturb and, on any failure,
restores them and deletes what it newly created, so an interrupted retirement ends
*wholly un-retired* rather than half-applied. The honest residual — a hard process kill or
power loss between two filesystem calls runs no compensation at all, and markdown-in-git
offers no journal to close it — is made **loud** instead of denied, at every seam that can
meet it rather than only at the ones that happen to scan:

| caller | where the refusal comes from |
|---|---|
| `enumerate` / `select` / `neighbours`, both directions | the enumeration seam (`iter_episode_ids`) |
| `fetch` by id | `resolve_episode_path()` — it checks both directories and refuses two, instead of preferring `active/` |
| every writer op, including a `retire` of an unrelated episode | `apply_delta()`'s pre-flight scan, run before any op is applied |

The `fetch` and writer halves were **missing** in the gate's first attempt (g4 review, F2):
a lookup by id silently returned the `active/` copy with `status: active`, and a retire
committed against a store already known to be corrupt. Loud in one hand and silent in the
other is worse than either, because the silent hand is the one #308's consolidation pass
walks back through when it follows a `consolidated-into:` reference by id. One narrow
limit is deliberate and stated rather than papered over: `fetch` refuses for the **affected
id**, and does not scan the whole store on every addressed lookup — turning an O(1) lookup
into an O(n) scan is a cost the store declines to pay for a residue that scanning readers
and every write already refuse.

**The membership-predicate seam.** **`is_episode_in_ordinary_search(episode_id)`** is the
single place any retrieval primitive asks "is this episode currently in the ordinary
rhyme-search candidate set." Bound to a **directory check**: does `episode_id`'s file
resolve under `episodes/active/`?

Every retrieval primitive that respects retirement calls it, and none inlines a directory
check or a status grep at the call site. That containment mattered before the ruling
because inlining would have turned "bind the layout at g4" into a retrieval rewrite; it
still matters now, for a different reason — it is what keeps the bound layout in one place
instead of scattered across call sites, so the archive discipline above is enforced by
four adapters rather than by every future caller remembering it.
`tests/test_episode_store.py` asserts the containment mechanically.

**The base-enumeration seam.** **`iter_episode_ids(include_retired)`** answers the prior
question — "what candidate ids exist to ask about in the first place." Bound to a
**directory union**: it lists `episodes/active/*.md`, and when `include_retired` is true
additionally unions in `episodes/retired/*.md` (exactly the union §2 specifies for the
id-sequence scan, which always calls this seam with `include_retired=true`, since a
retired episode's sequence number is still taken).

Four malformed-store conditions are refused here rather than answered around — every one
of them would otherwise yield a silently wrong candidate set, and putting them in the seam
every reader *and* the writer already goes through means no caller has to remember them:
an **absent store or layout directory** (trap 5), a **stray anywhere outside the two
layout directories** (traps 3 and 6), a **`.md` file inside a layout directory that is not
a well-formed episode, or is buried one level deeper** (traps 4 and 6), and an **id present
in both directories** (an interrupted retirement). Both directory listings go through
`episode_id_for()`, so a file never becomes a candidate id merely by being in the
directory. The archive is listed even for an ordinary scan solely to check the last
condition; that listing can only ever produce a refusal and never contributes a candidate,
so the archive remains an archive rather than a second search space.

**Composition rule.** "Enumerate the ordinary-search set" (§8) is
`iter_episode_ids(include_retired=False)` followed by confirming each returned id through
`is_episode_in_ordinary_search()` — scan, then filter, always both steps, never one folded
into the other. Under the bound layout the second step cannot subtract anything from the
first, so it is kept for a *different* reason than the one that introduced it: the scan
and the membership predicate are two **independent** seams, and a change that updated only
one of them is caught here. Their disagreement is therefore **raised**, never silently
dropped — dropping is how a candidate set gets quietly shorter. §2's id-sequence scan, by
contrast, calls `iter_episode_ids(include_retired=True)` alone with no membership filter,
because every episode's sequence number counts regardless of retirement.

**The fetch-by-id path-resolution seam.** **`resolve_episode_path(episode_id)`** returns
the one on-disk path to read. Bound to: check `episodes/active/<id>.md` and
`episodes/retired/<id>.md`, and return the one that exists. At most one *should* exist for
any valid id — but "should" is the point, since the half-retired residue above is admitted
to be possible, so this seam **checks** rather than preferring `active/`, and refuses when
both are there. It refuses an absent store for the same reason (trap 5): "there is no
store" and "there is no such episode" are different facts.

Fetch-by-id calls it and reads whatever path it returns; it never constructs a path
itself. It answers "where is it," a distinct question from "is it in the ordinary-search
set" — and note that **fetch-by-id deliberately reaches into the archive**. An addressed
lookup by name is not a search, and retirement excludes an episode from *search*, never
from retrieval by name; without this, every `consolidated-into:` / `superseded-by:`
cross-reference would dangle the moment its target was retired.

**Single-line enforcement, retained as an obligation on the writer.** The rejected
Option B needed this as a *defense*: a negative "not retired" filter over `##
Retirement`'s `status` field is exposed to a silent-omission bug if an agent-supplied
free-text field (e.g. `observed-behavior`) spans physical lines and a continuation line
happens to read `- status: retired` — easy, if an agent pastes a transcript that itself
discusses a retired episode. A naive line-oriented parser would match that line and
silently exclude a fully active episode from ordinary search, with no error and no crash.

Under the bound layout that exposure is **gone rather than mitigated** — a directory
check never parses free text, so there is no status parse to fool. The obligation is kept
anyway, for its own independent reason: a multi-line value silently truncates on the next
`parse_episode()`, corrupting the record regardless of retirement. The writer enforces
**single-line values on every agent-supplied free-text field**, rejecting a delta whose
value contains any line boundary the parser's own `str.splitlines()` recognizes.
`tests/test_episode_store.py` asserts that a forged `- status: retired` in free text
cannot move an episode between sets — "structurally impossible" is a claim about an
implementation, and implementations change.

**The full seam set, gathered in one place.** Seven things in this store route through
exactly one named mechanism each, and every caller must use the name — never inlining the
path, glob, grep, or move it stands for:

| Concern | Named seam | Bound implementation (g4) |
|---|---|---|
| Store root | the literal path `episodes/` (§1) | layout-invariant; unaffected by the ruling |
| Is this file an episode? | `episode_id_for(path)` (above) | the store's own id grammar (§2), uniform in all three directories |
| Layout creation | `ensure_store_layout(root)` | the WRITER's bootstrap only; every read seam refuses an absent layout |
| Retirement write | `apply_retirement()` + `destination_for()` (above) | field diff, plus a move into `retired/` |
| Per-id membership | `is_episode_in_ordinary_search(episode_id)` (above) | directory check: does it resolve under `active/`? |
| Base enumeration | `iter_episode_ids(include_retired)` (above) | `active/`, unioned with `retired/` when asked |
| Fetch-by-id path resolution | `resolve_episode_path(episode_id)` (above) | `active/` or `retired/`, refusing both-at-once |

Binding the layout at g4 cost close to what the seams promised: four adapter bodies plus
the removal of the rejected option's, and **no change to any primitive's shape**. What it
did cost, and what the seam set did NOT protect against, is worth recording: moving
membership from file content to file location silently invalidated the *classifier* —
"which files are episodes" was answered somewhere else, by a hand-maintained list, and did
not move with it. The seams keep a bound decision in one place; they do not tell you which
other decision the binding just made stale. That question — what did membership stop being
a property of? — is the one to ask at the next such binding.

The seam set is not scaffolding to be dismantled
now that the decision is made — it is what keeps the layout in one place, which is what
the archive discipline above needs in order to be a property of the store rather than a
convention every caller has to remember. `tests/test_episode_store.py` asserts that no
retrieval primitive names either directory as a literal.

## 8. Mechanical only — no ranking, no similarity, no embedding

This store never guesses. It exposes stable ids, enumerable fields, and exact-match /
set-membership retrieval — nothing more. All of it ships in `scripts/query_episodes.py`,
built entirely from the named seams in §7, never from an inlined path, glob, or grep at
the call site:

- **Fetch by id** (`fetch_episode`) resolves the on-disk path through
  `resolve_episode_path()` (§7) and reads it directly — no scan, no membership check. It
  finds retired episodes too, deliberately: a lookup by name is not a search.
- **Enumerate the ordinary-search set** (`enumerate_episode_ids` /`enumerate_episodes`)
  obtains its candidate id set from `iter_episode_ids(include_retired=False)` (§7), then
  confirms each id through `is_episode_in_ordinary_search()` (§7) before including it —
  the scan-then-filter composition §7 specifies, never a filter that also does its own
  scanning.
- **Select by exact field value** (`select_episodes`) and **enumerate the neighbours of
  an episode by shared exact join key** (`neighbours`) both scan the same candidate set
  before applying their own field/key match — identical composition to enumeration, just
  with an extra predicate layered on top.

**Retirement-dependent retrieval, and where the default sits.** Every *scanning*
primitive above takes `include_retired`, defaulting to **False**; the CLI spells it
`--include-retired` on `enumerate`, `select`, and `neighbours`, and the JSON envelope
reports which universe it answered from, so a caller cannot mistake an archive-excluding
answer for a complete one. `fetch` carries no such flag — it has nothing to hide, and
offering one would wrongly imply its default did. This is §7's archive principle made
mechanical rather than advisory: history is reached by asking, and never by accident.

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
does. (This section's argument is about git's own commit/merge/fetch mechanics, not about
which subdirectory a file lives under, so it held unchanged while the layout was open and
holds unchanged now that it is bound.) The steps:

1. A commander in worktree W writes `episodes/active/<id>.md` (via the validated writer)
   and commits it on its own branch, inside its own worktree — every commander only ever
   writes files inside the worktree it owns.
2. That commit merges to `main` (ordinary PR/merge flow, the same path any other change in
   this repo takes).
3. From that point on, the episode is visible in **every** worktree that has that commit —
   a `git pull`/`git fetch` + checkout in any other linked worktree, and any fresh
   `git clone` of the repo, resolves **the same content at the same blob OID**, because
   that is the definition of a tracked path in a shared git history.

**Working-tree bytes are NOT the cross-worktree identity, and the distinction is
load-bearing.** The claim above is exact at the *content* and *blob* level and would be
wrong at the byte level. This repo's `.gitattributes` sets `* text=auto`, so checkout
normalizes line endings per platform: the writer always emits LF-only bytes, and a
worktree materialized on a machine with `core.autocrlf=true` (the Git-for-Windows
default) gets CRLF. The record is identical, the blob OID is identical — git hashes the
normalized index content — but `read_bytes()` in two worktrees can legitimately differ.

This does not weaken cross-worktree durability: retrieval crosses the boundary intact
either way, because the record is what the store promises. It does mean anything
downstream wanting a stable content address for an episode must use git's blob hash and
not a hash of the file in its own worktree — exactly what §8's `<ref>@<revision>` pinning
already prescribes. A future consolidation/dedup pass (#308) that compared episodes by
hashing working-tree bytes would be silently wrong on Windows, which is why
`test_working_tree_bytes_are_not_the_cross_worktree_identity` pins it as a test rather
than leaving it as prose. Context: issue **#319**.

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

## 10. What is built, and what is deliberately not

**Built** (issue #301, gates g1–g4):

- **`scripts/apply_episode_delta.py`** — the validated, all-or-nothing delta writer
  (mirroring `apply_lessons_delta.py`'s contract) that is the **only** write path; the LLM
  never writes an episode file directly. It enforces the partition allowlist (§4), the
  mandatory non-empty retire reason (§7), and single-line enforcement on agent-supplied
  free-text fields (§7). Its retire op routes its content half through
  `apply_retirement()` and its layout half through `destination_for()` (§7) —
  never an inlined file move at a call site.
- **`scripts/query_episodes.py`** — deterministic retrieval: fetch by id, enumerate,
  exact/set-membership select, neighbour enumeration, each in an ordinary-search and a
  history-inclusive form (§8). Every primitive is built from the seams named in §7
  (`resolve_episode_path`, `iter_episode_ids`, `is_episode_in_ordinary_search`,
  `episode_id_for`) — never from an inlined path, glob, or grep. A store that is absent,
  malformed, or half-retired is REFUSED by every one of them rather than answered as empty.
- **`episodes/`** — the tracked store: a `README.md` at the flat root (documentation, and
  the one entry in `NON_EPISODE_FILENAMES`), plus `active/` and `retired/` each kept alive
  by a tracked `.gitkeep`. Git does not track empty directories, so without a tracked file
  in each the layout would vanish at commit — and the placeholder is deliberately NOT a
  `.md` file, because inside those two directories every Markdown file is an episode and a
  `README.md` there is refused as malformed (§7).
- **`tests/test_episode_store.py`** — including the cross-session and cross-worktree
  acceptance exercise (write from one process, read from a genuinely separate one across
  a real `git worktree` boundary, per §9), the adversarial silent-omission fixtures (§7),
  and the half-retirement fault injections (§7).

**Deliberately not built here**, so it is not rediscovered from scratch:

- **#305** wires automated capture of the **mechanical half only**, and that split is
  not a shortfall — it is what §4's partition means in practice. The `## Mechanical`
  group falls out of the engine with **zero agent effort**:
  `scripts/episode_capture.py`'s composer reads every field of it out of engine state
  and emits it as a snapshot beside each step's manifest, whether or not any agent
  records anything. The `## Agent-supplied` half stays **agent-initiated**, because it
  is irreducibly judgment: `_validate_create` requires all five assertion kinds with
  non-empty statements, so a complete episode **cannot** exist without an agent
  asserting what was intended, what was expected, what was observed, what it cost and
  what was done about it. So nothing auto-*creates* an episode, and nothing should — an
  auto-created one could only carry fabricated assertions. What #305 removes is the
  mechanical bookkeeping an agent would otherwise have to remember; what it leaves is
  the part only an agent can supply. A field that is not honestly readable from engine
  state is **refused** rather than defaulted, so an absent mechanical line means "this
  could not be read", never "this was zero".
- **#308** builds the rhyme-detection sensor and the consolidation/adjudication loop on
  top of what this store exposes (§8). The store makes consolidation *possible* — a
  retired cluster member stays reachable by id, by history-inclusive scan, and from a
  surviving member's neighbourhood — and implements none of it.
- **#300**'s projection manifest. `context-manifest-ref` stays an opaque
  `<ref>@<revision>` (§8).
