# Candidate B — assertion-native episode record

Constraint: **assertion-native**. Panel context: issue #301, episode record + durable
store, one of four candidates under the shared brief at
`.agent-work/301/design-it-twice/BRIEF.md`.

## 1. The constraint, restated, and what it drove

Every other candidate in this panel can design a convenient bespoke record — flat fields,
free prose, whatever reads best for a human — and then, separately, write a mapping
function from that record onto Stratum A assertions. That mapping is future work, and
future work on a truth-model boundary is exactly the kind of "we'll adapt it later" that
non-foreclosure exists to rule out.

Under **assertion-native**, that move is not available to me. The record does not get
mapped onto assertions; it **is** assertions, from the first line of the first file. An
episode is not "a document that can be read as a list of assertions" — it is literally a
list of assertion blocks, each independently identified, sourced, evidenced, and given a
lifecycle standing. There is no translation step because there is nothing on either side
of a translation: the on-disk shape and the Stratum A shape are the same shape.

This drove four concrete decisions, in order:

1. **The atomic unit of the store is the assertion, not the episode.** An episode file is
   a container of assertions sharing one narrative, not a record with fields.
2. **The mechanical/agent-supplied partition is a property of assertions**
   (`origin: mechanical` vs `origin: agent`), rendered as two visibly separate sections —
   *and* it must survive at reduced ceremony for the mechanical bin, or the constraint
   would make trivial facts expensive for no epistemic reason (see §3, §5, §10).
3. **Suspected-cause and proposed-remedy are a third bin**, not fields hung off either
   group, because the brief requires them separate and optional, and because diagnosis is
   exactly the class of claim most likely to be revised, disputed, or superseded —
   assertion machinery is not overhead there, it is the point.
4. **Retirement and lifecycle standing had to be kept mechanically distinct**, because an
   assertion-native record is precisely the design most tempted to conflate them (both are
   "assertion-flavored" moves) — see §7.

## 2. The record shape — a real worked episode, as it appears on disk

Path: `durable_root() / ".agent-work" / "episodes" / "ep-governor-265-nonreading-visible.md"`
(`durable_root()` from `scripts/agent_work_root.py`, the same helper
`apply_lessons_delta.py` already uses to resolve `.agent-work/LESSONS.md` — this store
lives beside it, under the same durability rule, in a sibling directory).

```markdown
<!-- episode-state: status=active m-next=9 a-next=6 d-next=3 -->

# episode: ep-governor-265-nonreading-visible

## Mechanical

### assertion:ep-governor-265-nonreading-visible.m1
- kind: run-project
- origin: mechanical
- source: spine.json (governor-265, engine_session)
- statement: run=governor-265, project=constellation-skills, work-id=governor-265

### assertion:ep-governor-265-nonreading-visible.m2
- kind: role-step
- origin: mechanical
- source: spine.json:active-step
- statement: role=commander-delegated, spine-step=g1-implement

### assertion:ep-governor-265-nonreading-visible.m3
- kind: context
- origin: mechanical
- source: projection-manifest (#300) resolution for this run
- statement: manifest-ref=ctx-governor-265-g1, resolved-at-revision=a3f9c1e

### assertion:ep-governor-265-nonreading-visible.m4
- kind: rework-count
- origin: mechanical
- source: checklist_engine.py gauge (governor-265/gauge.json)
- statement: rework_count=2

### assertion:ep-governor-265-nonreading-visible.m5
- kind: failed-command
- origin: mechanical
- source: crew-handoffs/265-attempt1.log
- statement: pytest tests/test_context_governor.py::test_zero_reading_distinct -> exit 1

### assertion:ep-governor-265-nonreading-visible.m6
- kind: artifact
- origin: mechanical
- source: git diff, PR #283
- statement: skills/governor/engine/reading.py; crew-handoffs/265-result.md

### assertion:ep-governor-265-nonreading-visible.m7
- kind: refusal
- origin: mechanical
- source: spine.json:refusals
- statement: none

### assertion:ep-governor-265-nonreading-visible.m8
- kind: reopen
- origin: mechanical
- source: spine.json:reopen-count
- statement: reopen_count=0

## Agent-supplied

### assertion:ep-governor-265-nonreading-visible.a1
- kind: task-intent
- origin: agent
- source: commander-265, g1-implement notes
- strength: strong
- standing: active
- statement: Make an unarmed (no probe yet) governor gauge visibly distinct from a real
  low reading, so a HARD-band false positive cannot fire before the governor has data.

### assertion:ep-governor-265-nonreading-visible.a2
- kind: expected-behavior
- origin: agent
- source: commander-265, g1-implement notes
- strength: medium
- standing: active
- statement: A session with zero probes renders a neutral "unarmed" gauge state, never a
  numeric low reading.

### assertion:ep-governor-265-nonreading-visible.a3
- kind: observed-behavior
- origin: agent
- source: crew-handoffs/265-result.md:34-41
- strength: strong
- standing: active
- supporting: crew-handoffs/265-result.md:34-41 (pasted gauge render, HARD banner text
  identical for unarmed vs. a genuine reading of 0)
- supporting: REVIEW_RESULT-265.md:12 (reviewer's independent re-render, same collision,
  different transcript)
- statement: Before the fix, an unarmed gauge rendered the same HARD/red banner as a real
  reading of 0 — an agent reading it could not tell "no data yet" from "genuinely bad".

### assertion:ep-governor-265-nonreading-visible.a4
- kind: impact-cost
- origin: agent
- source: commander-265 closeout notes
- strength: strong
- standing: disputed
- supporting: crew-handoffs/265-attempt1.log (first HARD-band stop, no probes yet)
- supporting: crew-handoffs/265-attempt2.log (second HARD-band stop, same signature)
- challenging: REVIEW_RESULT-265.md:29 — reviewer attributes attempt 2's stop partly to
  flaky test infra (a stale gauge.json from a prior run), not purely the unarmed/zero
  collision; disputes full attribution of both reworks to this one cause.
- statement: Two implement/rework cycles (m4) were spent chasing a phantom HARD band
  before the unarmed/real-zero collision was identified as (at least the primary) cause.

### assertion:ep-governor-265-nonreading-visible.a5
- kind: workaround
- origin: agent
- source: commander-265 closeout notes
- strength: strong
- standing: active
- statement: none applied — fixed at the source (see remedy d2) rather than worked around.

## Diagnosis (optional)

### assertion:ep-governor-265-nonreading-visible.d1
- kind: suspected-cause
- origin: agent
- source: commander-265, first-pass reading before code inspection
- strength: weak
- standing: superseded
- statement: Suspected the gauge renderer used a hardcoded red-band threshold that
  happened to equal the unarmed default value.
- history: superseded 2026-07-28 (governor-265) by d2, after direct code inspection —
  crew-handoffs/265-result.md:52-58 (the actual branch condition, pasted).

### assertion:ep-governor-265-nonreading-visible.d2
- kind: suspected-cause
- origin: agent
- source: crew-handoffs/265-result.md:52-58
- strength: strong
- standing: active
- supersedes: ep-governor-265-nonreading-visible.d1
- supporting: crew-handoffs/265-result.md:52-58 (pasted source: `if value <= threshold`
  with no `armed` check, so an unset/None-coerced-to-0 reading matches the same branch as
  a real reading of 0)
- statement: reading.py's render path branched on `value <= threshold` without checking
  an `armed` flag, so an unarmed (never-probed) reading and a genuine 0 took the same
  code path.

### assertion:ep-governor-265-nonreading-visible.d3
- kind: proposed-remedy
- origin: agent
- source: commander-265, g1-implement notes
- strength: strong
- standing: active
- statement: Add an explicit `armed: bool` field to the reading record; render "unarmed"
  as its own distinct state; gate HARD-band logic on `armed=true`. (Shipped: PR #283.)
```

**Parsing rule this shape commits to** (load-bearing for §9): every `- field: value` line
is a **single physical line**. A value that must quote multi-line source text does **not**
continue as bare `- `-prefixed lines (those are field lines by definition and would be
silently mis-parsed as new fields); it continues as `>`-prefixed blockquote lines, which
the field regex does not match and the parser explicitly skips over as continuation of the
previous field's value. `m3`'s statement shows the ordinary case; nothing in this episode
needed a blockquote continuation, but the grammar reserves it for exactly that case.

## 3. The mechanical / agent-supplied partition, and how it survives assertion-shaping

The brief requires the partition to be **visible in the record itself**, not implied by
field naming. This candidate satisfies that twice over, redundantly, on purpose:

- **Structurally**: two H2 sections, `## Mechanical` and `## Agent-supplied`, plus a third,
  `## Diagnosis (optional)`, that is absent entirely when there is no diagnosis (not an
  empty section — its absence is itself the signal that the episode is complete without
  one, per the hard constraint).
- **In the id itself**: every assertion id carries a bin letter — `.m*` mechanical, `.a*`
  agent-supplied, `.d*` diagnosis — so a query never needs to resolve which section an id
  belongs to; the id is self-describing. This redundancy is what makes the adversarial
  fixture in §9 possible to write cheaply: a validator can check that section membership
  and id-prefix membership agree, and a fixture that makes them disagree is a real defect
  to catch.

The harder question the constraint forces is not *where* the line is drawn but *what it
costs* to draw it in assertion vocabulary. A mechanical fact like `rework_count=2` has no
epistemic status to argue about — nobody will ever supply challenging evidence against a
counter the engine incremented. Two escape hatches were considered and rejected:

- **Skip assertion-shaping for the mechanical bin entirely** (flat `- key: value` list,
  like the agent-supplied bin has full fields). Rejected: this reintroduces exactly the
  "bespoke record with an assertion-shaped-only agent half" that the constraint forbids —
  the mechanical bin would need mapping onto Stratum A *later*, the same foreclosure the
  brief rules out, just for one bin instead of the whole record.
- **Give the mechanical bin the full apparatus** (`strength:`, `standing:`, `supporting:`,
  `challenging:` on every line, matching the agent-supplied bin exactly). Rejected as pure
  ceremony: see §5 and §10 for the honest cost accounting.

The shape actually used is the middle path: mechanical assertions **are** Stratum A
assertions — `strength: strong` and `standing: active` by **class default**, not by a
written field. The default is a property of `origin: mechanical`, not a per-instance
choice, so it costs nothing to render and nothing to parse in the common case. It is only
written explicitly when reality diverges from the default — see the next paragraph. This
is a distinguished rendering, not a distinguished truth model: a mechanical assertion is
never "less of an assertion," it just starts from a fixed, well-justified point on the
strength/standing axes instead of an agent having to assert the obvious.

**If a mechanical fact is ever actually disputed** (e.g., a later audit finds the rework
counter double-counted a retried command), that dispute is never edited into the
mechanical block. A new **agent-supplied** assertion is added (`kind: observed-behavior`
or a new `kind: mechanical-dispute`) that challenges `m4` by id, and *that* act is what
flips `m4`'s rendering from implicit-default to an explicit `- standing: disputed` line.
The mechanical bin's ceremony-reduction is a one-way default with an explicit escape, never
a claim that mechanical facts are immune to being wrong.

## 4. Suspected-cause and proposed-remedy as separate optional assertions

`## Diagnosis (optional)` is a third bin, structurally and by id prefix (`.d*`), never
folded into either the mechanical or agent-supplied section. Two properties fall out of
giving diagnosis its own bin rather than treating it as extra fields:

- **It can be absent without leaving a hole.** An episode with no `## Diagnosis` heading
  at all is syntactically identical to one where diagnosis was considered and yielded
  nothing — both are complete, valid episodes. (Contrast: if suspected-cause were an
  optional *field* on the observed-behavior assertion, its absence would be ambiguous
  between "not yet diagnosed" and "field omitted by mistake.")
- **It gets full assertion apparatus, unconditionally**, unlike the mechanical bin. `d1`
  and `d2` in the worked example show why: a suspected cause is exactly the kind of claim
  that gets **superseded** as investigation proceeds (`d1` was a guess before code
  inspection; `d2` supersedes it once the actual branch condition was read). A proposed
  remedy (`d3`) is a claim about what *should* fix it, distinct from a claim about what
  the fix actually shipped as — a remedy assertion does not silently become true because a
  PR merged; it stays `standing: active` as *what was proposed*, and the shipped-PR
  citation is additional supporting context, not a status change. (A separate, later
  concern — did the shipped fix work? — is itself a new observed-behavior assertion in a
  *subsequent* episode, not a mutation of `d3`.)

## 5. The Stratum A mapping — trivial for us; the converse is the real content

**The mapping**, shown because the hard constraint requires it even though it is close to
an identity function here:

| Stratum A element | This record |
|---|---|
| identified assertion | `### assertion:<episode-id>.<bin><n>` heading |
| source | `- source:` line |
| supporting evidence | `- supporting:` lines (0+, repeatable) |
| challenging evidence | `- challenging:` lines (0+, repeatable) |
| qualitative strength | `- strength: weak\|medium\|strong` |
| lifecycle standing | `- standing: active\|disputed\|superseded\|rejected`, a field
  entirely separate from `strength` — see `a4` (strength: strong, standing: disputed) for
  a worked example of the two dimensions moving independently |

There is no second column of transformation work because there is no second shape. That is
the entire point of the constraint, and it would be dishonest to spend more of this section
restating it.

**The converse — what this candidate costs, and what a later assertion-model
implementation still has to add**, is the real content the brief is asking for here:

1. **Ceremony on the mechanical bin.** Every mechanically-captured atomic fact costs a
   heading plus 3-4 lines (`kind`, `origin`, `source`, `statement`) instead of the one
   `- key: value` line a flat-field design would use for the same fact. `m1`-`m8` above are
   eight facts that, in `LESSONS.md`'s field-list style, would be eight lines under one
   heading. Here they are eight headings. This is real overhead, paid on every episode, for
   facts nobody will ever dispute. §10 scores this honestly as a place the constraint hurt.
2. **A global assertion namespace and index**, which this candidate does *not* need for its
   own retrieval (episode-local ids plus a filename-is-the-id lookup suffice at
   Markdown-in-git scale, §6) but which a later cross-episode assertion graph (owned at
   #308's consolidation/rhyme-search loop) would need to add: a registry mapping
   `assertion-id -> episode file path` for O(1) resolution once `supersedes:` and
   cross-episode challenge pointers make directory-scan resolution too slow to be pleasant.
   Nothing here blocks building that registry later — every id is already globally unique
   (episode-id-qualified) — but it is genuinely unbuilt.
3. **Transitive supersession resolution.** `d1 -> d2` is a one-hop pointer. A real
   consolidation pass will eventually need to walk chains (`X superseded by Y superseded by
   Z`) and resolve cross-*episode* supersession (a consolidated pattern-episode superseding
   assertions that live in several neighbor episode files). This candidate's `supersedes:`
   field is deliberately just a string id — flat, unresolved, exactly the raw material a
   graph walk needs and nothing more. The walk itself is unbuilt, and is explicitly #308's
   job, not mine.
4. **Cross-assertion strength aggregation.** Nothing here combines "three episodes each
   weakly assert X" into "X is now medium-strength across the corpus." That aggregation is
   the rhyme-search sensor's stochastic job (B0.1) — this store supplies the exact,
   individually-graded raw assertions it needs to work on, and stops there on purpose.
5. **Query tooling**, not schema translation. `grep`-based retrieval (§6) works today, but a
   convenience layer (`--kind`, `--standing`, `--origin` filters as a thin script wrapping
   the same regexes) is unbuilt. This is retrieval ergonomics, not a shape gap — no field
   needs to change to build it.

So: the cost of assertion-native is **not** "we'll need to translate this later" — that
cost is genuinely zero, which is the constraint doing its job. The cost is ceremony paid
today on facts that will never need it, plus infrastructure (index, graph walk,
aggregation) that a bespoke-record candidate would *also* eventually need to build once it
did its own later mapping — the difference is that candidate pays translation cost AND
infrastructure cost later; this one pays ceremony cost now and infrastructure cost later.

## 6. File layout and deterministic retrieval

```
<durable_root>/.agent-work/episodes/
  ep-governor-265-nonreading-visible.md
  ep-<other-episode-slug>.md
  ...
```

One file per episode. `durable_root()` (already shipped, `scripts/agent_work_root.py`)
resolves the same durable location `apply_lessons_delta.py` uses for `LESSONS.md`, so a
linked-worktree run reads and writes the main checkout's episode store, not a disposable
worktree-local copy — no new durability mechanism, reuse of the existing one.

**Episode id grammar**: `ep-[a-z0-9][a-z0-9-]*` (kebab-case, same convention
`LESSON_HEADING_RE` already enforces for lesson ids). The filename **is** the id
(`<episode-id>.md`) — no separate index file maps ids to paths, because the filesystem
already is that index.

**Assertion id grammar**: `<episode-id>.<bin><n>`, `bin ∈ {m, a, d}`, `n` a 1-based counter
that only increases, tracked per-bin in the header (`m-next=9 a-next=6 d-next=3` in the
worked example — the *next* id the delta script will assign in each bin, so assignment is
O(1) and never requires rescanning the file to find the highest existing number). Ids are
never reused, even across retirement — deleting or superseding an assertion never frees its
number.

**Retrieval, all deterministic, no ranking, no embedding, no guessing:**

- **By episode id** (exact match): open `<episode-id>.md` directly. No scan.
- **By assertion id** (exact match): split on the last `.`, get the episode id, open that
  one file, find the `### assertion:<id>` heading, read to the next heading or section
  boundary.
- **By kind / origin / standing / strength (set-membership)**: `grep` the field-line regex
  (`^- (kind|origin|standing|strength): `) across `.agent-work/episodes/*.md`, filtered to
  the value(s) wanted. E.g. "all disputed assertions": `grep -B4 '^- standing: disputed'
  .agent-work/episodes/*.md` to also see the enclosing heading.
- **By artifact / content substring (set-membership)**: plain `grep -l <string>
  .agent-work/episodes/*.md` — e.g. `grep -l skills/governor/engine/reading.py
  .agent-work/episodes/*.md` finds every episode touching that file, using the mechanical
  `artifact` assertions as the substrate. This is the deterministic *candidate set* a
  stochastic rhyme-sensor is handed to work on top of (B0.1) — the store never itself
  judges that two episodes rhyme, it only ever answers exact and set-membership questions.
- **Active vs. retired (structural filter)**: read line 1 of each file (the
  `<!-- episode-state: ... -->` header) with one regex; no full parse needed to know
  whether a file is in scope for ordinary search. Two-step retrieval: (1) filter the file
  list by header `status`, (2) grep content within that filtered set. "Ordinary rhyme
  search" always does step 1 with `status=active`; an explicit history query does step 1
  with `status=retired` or skips the filter for "all".

**Honest sizing on this section**: I tested this reasoning against a directory holding
dozens to a few hundred files (the scale this repo's issue/epic cadence would plausibly
produce over many months) — `grep` across a few hundred small Markdown files is instant and
needs no index. I did **not** test or design for thousands of files; at that scale the
registry named in §5 point 2 stops being optional. That threshold crossing is future
pressure, not a gap in this design — Tommy's own ruling ("Markdown is sufficient until
observed pressure earns a backend") applies exactly here, and nothing in this shape blocks
adding an index file later without touching any existing episode.

**Mutation discipline (rhyming with the prior art, not designed for implementation here)**:
mutation goes through a validated, all-or-nothing JSON delta script,
`apply_episode_delta.py`, mirroring `apply_lessons_delta.py`'s contract exactly — the LLM
never writes an episode file directly. Its op set: `new-episode`, `add-assertion` (bin,
kind, origin, source, statement, optional strength/standing/supporting/challenging/
supersedes), `amend-assertion` (requires grounding, like the lessons `amend` op),
`retire-episode` (requires a reason, like the lessons `retire` op — see §7). Each op is
validated field-by-field before any write; any invalid op in a delta rejects the whole
delta, same as today. This script is a design *obligation*, not a deliverable of this
candidate (the brief scopes implementation out); I am specifying its contract precisely
enough that §8's exercise is mechanically runnable once built, not hand-waved.

## 7. Retirement policy — mechanical, and strictly separate from belief strength

Retirement is a **per-episode, per-file** structural flag. Lifecycle standing
(`disputed`/`superseded`/`rejected`) is a **per-assertion**, epistemic dimension. The two
are never allowed to move together in one operation, on purpose, because an assertion-native
design is exactly the design most tempted to blur "this claim's standing changed" with
"this record is no longer surfaced" — they read as similar moves in this vocabulary, and
keeping them separate is the whole reason retirement gets its own op with its own mechanics
rather than being folded into a standing transition.

**The `retire-episode` op** (delta example, mirroring `apply_lessons_delta.py`'s mandatory
`reason` on `retire`):

```json
{"work_id": "consolidate-308-run1",
 "episode": "ep-governor-265-nonreading-visible",
 "op": "retire-episode",
 "reason": "folded into pattern episode ep-pattern-unarmed-vs-zero-collision (2026-08-03)"}
```

Mechanical effect, and nothing else:

1. Header flips `status=active` -> `status=retired`.
2. A `## Retirement` section is appended to the file: `- retired: 2026-08-03
   (consolidate-308-run1) — folded into pattern episode
   ep-pattern-unarmed-vs-zero-collision (2026-08-03)`.
3. **No assertion body is touched.** Every `standing:` field in the file is exactly what
   it was before the op. The op is rejected by the validator if it carries any assertion-
   level field at all — retirement cannot also mutate standing in the same call, structurally,
   not just by convention.
4. The file is never deleted, never moved, never truncated. It remains fully readable, at
   its same path, forever (retention is git's job — nothing here prunes history).

**What "retired" changes and doesn't change:**

- Retired **excludes the episode from step 1 of ordinary retrieval** (§6) — it will not
  surface in a default rhyme-search candidate set.
- Retired **does not** mean any assertion in it was wrong. An episode's assertions can all
  still read `standing: active` after the episode itself is retired — the claims are still
  true, they are just no longer surfaced as a distinct hit because a consolidation pass
  decided the pattern lives more usefully as a synthesized neighbor episode.
- Conversely, an assertion's `standing` can flip to `superseded` or `rejected` while its
  episode stays `status: active` — disputing or superseding one claim inside an otherwise
  live episode does not retire the whole episode. That is a separate, ordinary
  `amend-assertion` op, cited with its own grounding.
- If a consolidation pass *also* wants to mark specific assertions as superseded by the new
  pattern episode (typically it will), that is two separate, separately-grounded ops:
  `retire-episode` on the old file, and one `amend-assertion` per superseded claim (which
  can point cross-file: `supersedes: ep-pattern-unarmed-vs-zero-collision.a1`). Neither op
  implies the other; the validator enforces neither op accepting the other's payload.

## 8. The cross-session retrieval exercise

**Honest session boundary, as the brief demands**: a genuinely new OS process — a fresh
`python` invocation (or a fresh terminal) — that shares nothing with the writer except the
git working tree on disk. Not a continued conversation, not a shared Python interpreter, no
in-memory cache.

1. **Session 1 (process P1)**: runs `python scripts/apply_episode_delta.py delta.json`
   where `delta.json` is the `new-episode` + `add-assertion` ops that produced the worked
   example in §2. The script writes
   `.agent-work/episodes/ep-governor-265-nonreading-visible.md` to disk and exits. (It does
   not commit to git — that stays a separate, human/CI-owned step, matching how
   `apply_lessons_delta.py` behaves today: it writes the file; nothing in this candidate
   changes who commits.)
2. **P1 exits.** Process boundary is real: no shared memory, no shared file handle, nothing
   held open.
3. **Session 2 (process P2)**, started independently, later, possibly on a different
   invocation of the shell entirely: runs `grep -l "kind: observed-behavior"
   .agent-work/episodes/*.md`, finds `ep-governor-265-nonreading-visible.md`, opens it, and
   reads `a3` verbatim — byte-identical to what P1 wrote, including its `supporting:`
   citations and `standing: active`.
4. Acceptance is met when P2's read of `a3` matches what P1 wrote, character for character,
   using nothing but the filesystem and `grep` — no cache, no index, no shared process
   state, no re-derivation.

**The harder downstream companion (owned at #308, not designed here — checking this
candidate does not preclude it)**: seed several episodes across several runs (several
`new-episode` deltas from several process invocations), consolidate one cluster
(`retire-episode` on the consolidated originals, per §7), and confirm rhymes involving the
*neighbors* of the consolidated cluster are still findable. This candidate does not
preclude that exercise: neighbor episodes are untouched files (retirement only ever touches
the file(s) named in its own op), so a directory-scan-plus-grep query after consolidation
returns exactly the same neighbor hits it would have before, modulo the consolidated
files themselves dropping out of the `status=active` filter. Cross-file `supersedes:`
pointers from the new pattern episode into neighbor assertions are plain id strings; they
do not require editing the neighbor files at all, so neighbors are never at risk of being
silently mutated by a consolidation pass.

**What I tested vs. what I did not**: this candidate is design-only — no code was written,
no delta script exists yet, and I did not execute the exercise above. What I did do is
specify the exercise precisely enough (concrete commands, concrete file, concrete
byte-identity check) that it is directly runnable once `apply_episode_delta.py` is built,
with no ambiguity about what "session boundary" or "found" means. That is a deliberate,
disclosed gap, not a hidden one.

## 9. One adversarial fixture

**Target defect class**: a naive line-oriented parser using the field regex (`^- ([a-z-]+):
(.*)$`, the same shape `apply_lessons_delta.py`'s `FIELD_RE` already uses) with no
awareness of statement-value continuation. If a `- statement:` value is allowed to embed
raw multi-line pasted text — e.g. an agent quoting a transcript that itself contains lines
shaped like `- kind: proposed-remedy` or `- standing: rejected` — a parser that doesn't
respect the blockquote-continuation rule from §2 will treat those embedded lines as **new
field assignments on the current assertion**, silently overwriting its real `kind` and
`standing`.

**The fixture** (a single assertion block, deliberately malformed against the §2 grammar):

```markdown
### assertion:ep-fixture-adversarial.a1
- kind: observed-behavior
- origin: agent
- source: crew note, pasted verbatim
- strength: medium
- standing: active
- statement: The failing log read literally:
- kind: proposed-remedy
- standing: rejected
(pasted from a different report, quoted for context)
```

**Wrong answers this catches**:

- **False FAIL on a valid record**: a query for `standing: active` assertions will
  silently miss `a1` — a naive parser overwrites `standing` to `rejected` from the embedded
  line, even though the real assertion (an observed-behavior claim, genuinely active) is
  perfectly valid. The assertion is wrongly excluded from every "what's currently live"
  query.
- **Silent PASS on an invalid one**: a query for rejected assertions will wrongly include
  `a1` — it looks, to the naive parser, like a rejected proposed-remedy, when it is neither
  rejected nor a remedy. Worse, `kind` was also overwritten, so a `--kind observed-behavior`
  filter silently drops a genuine observed-behavior assertion, and a `--kind
  proposed-remedy` filter silently gains a phantom one that was never authored as a remedy
  at all.

**What a correct parser must do, forced by this fixture**: respect the §2 rule that
multi-line quoted text is only ever valid inside a `>`-prefixed blockquote continuation,
never as bare `- `-prefixed lines. The fixture above is *itself invalid* under that
grammar (its continuation lines are bare `- ` lines, not `> ` blockquote lines) — a correct
implementation must **reject the whole delta that tried to write this**, at write time
(the validated-delta-script discipline in §6), rather than silently accept a malformed
statement value and let a downstream reader guess what it meant. The adversarial fixture
therefore doubles as the acceptance test for the write-time validator, not just the
read-time parser: a delta containing this block must fail validation, loudly, before it
ever reaches disk.

This directly rhymes with the already-banked lesson
`round-trip-tests-prove-artifacts-not-parsers` in the live `LESSONS.md` — a round-trip test
over the well-formed episode in §2 would pass a naive parser cleanly and prove nothing
about this failure mode; only a fixture deliberately shaped to violate the continuation
rule exercises it.

## 10. Honest self-scoring

**Depth** — medium-high. The store hides consolidation/rhyme complexity well: a rhyme
sensor built on top only ever needs to scan uniform `kind`/`origin`/`standing`/`strength`
fields, with zero impedance between "what's on disk" and "what Stratum A wants" (§5). It is
dinged because the constraint *leaks* representational complexity in the other direction:
the mechanical bin's ceremony (§3, §10 below) is visible to anyone reading a raw episode
file, even though nothing about a rework counter needed that shape. Depth was won on the
downstream side and partly spent on the upstream (authoring) side.

**Locality** — high. The change is fully contained to one new directory
(`.agent-work/episodes/`), reuses the existing `durable_root()` helper unmodified, and adds
one new delta script alongside (not instead of) `apply_lessons_delta.py`. Nothing about
`LESSONS.md` changes. The one locality cost worth naming honestly: assertion-shaping makes
each episode file systematically larger (more headings, more lines) than a flat-field
equivalent for the same underlying facts — a diff-size cost, not an architectural fan-out
cost.

**Seam placement** — good, with one named mismatch. The retrieval seam (exact id lookup,
set-membership grep, no ranking) sits exactly where a deterministic caller and a stochastic
sensor both want it (B0.1). The named mismatch: the mechanical bin's real caller is the
*harness/engine* (issue #305, out of scope but not precluded here), and a harness emitting
a rework counter does not actually want assertion ceremony — it wants to log a fact. Routing
it through the same `add-assertion` op as an agent's hard-won observed-behavior claim gives
the harness integration a heavier interface than a flat key-value logger would need. This
candidate accepts that mismatch deliberately (§3) to avoid a two-tier record that would
itself need later reconciliation, but it is a real seam cost, not a free win.

**Testability** — high, and this is where the constraint earns its keep most cleanly. One
uniform assertion-block grammar covers the *entire* file — mechanical, agent-supplied, and
diagnosis all parse through the same rule — so one parser, one validator, and one
adversarial fixture class (§9) exercise 100% of the record shape. A heterogeneous design
(flat fields for one bin, assertion blocks for another) would need two parsers and two
fixture classes to get the same coverage.

**Where the constraint HURT the design, stated plainly**: §3 and §5 already carry the
detail, but naming it once, together, here: (1) mechanical ceremony — every atomic
engine-emitted fact costs a heading plus 3-4 lines instead of one `key: value` line, paid
on every single episode, for facts nobody will ever dispute; (2) semantic awkwardness —
writing (even implicitly) `strength` and `standing` on a rework counter is a category
mismatch between a vocabulary built for contested claims and a fact that is definitionally
uncontested; (3) a real internal complexity tax — the `m`/`a`/`d` id-prefix redundancy
exists *only* to make partition-verification cheap without full parsing, which is scaffolding
the constraint itself required, not scaffolding the underlying problem required. A
non-assertion-native candidate does not pay any of these three costs — it pays a translation
cost instead, later. This candidate's honest claim is that translation-cost-never beats
ceremony-cost-always, not that ceremony-cost-always is free.
