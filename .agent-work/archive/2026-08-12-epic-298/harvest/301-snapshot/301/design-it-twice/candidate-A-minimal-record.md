# Candidate A — minimal-record

Constraint: **minimal-record**. Design the smallest episode record and store that can
honestly satisfy every hard constraint in the brief. Aggressive subtraction: every field
must survive "what breaks if this is absent?" — pushed hardest against the agent-supplied
half, since agent effort is the cost the spec explicitly wants minimized.

## 1. The constraint, restated, and what it cut

I read "minimal-record" as two separate cuts, not one:

- **Cut the record's per-episode field count** to what actually earns its keep against the
  seven hard constraints — not what the brief's illustrative field lists happen to name.
- **Cut the store's machinery**, not just the schema. The prior art (`apply_lessons_delta.py`)
  carries counters, a cap, dormancy, and an all-or-nothing JSON-delta validator because it
  manages a small *curated, evolving* set of lessons (mentions, confirmed, disconfirmed,
  status transitions). An episode is a different kind of object: a **raw, single, atomic
  capture** of one observation. It is written once and then either stands or is retired — it
  is never "confirmed again." Importing the lesson-playbook's counter/cap/dormancy machinery
  onto episodes would be building unearned structure to look consistent with the neighbour,
  not because episodes need it. I cut all of it.

What that cut, concretely:

- **No shared growing file.** One Markdown file per episode, not one big `EPISODES.md`.
  This isn't a stylistic choice — a single shared file mutated by every concurrent Commander
  across every worktree is a merge-conflict generator and forces exactly the
  read-whole-file/rewrite-whole-file discipline `apply_lessons_delta.py` needs for a *cap and
  counters* I don't have. One file per episode means every capture is a **new file**, which
  git can never conflict on.
- **No confirm/disconfirm/mentions counters on the episode itself.** Adjudicating whether a
  claim holds across repeated observation is exactly the "does this rhyme, is it still true"
  judgment the brief assigns to the downstream stochastic sensor (#308's consolidation loop),
  not to the store. I give the store two thin, citation-required *link* fields
  (`corroborated-by` / `disputed-by`) so that downstream judgment has somewhere deterministic
  to land — but the store itself never counts, weighs, or ages anything.
- **No JSON-delta batch-validator.** That machine exists to protect a single shared file with
  cross-referencing state (a cap, a run-tick, per-lesson counters) from a half-applied
  mutation. A one-file-per-episode store has no cross-referencing state to corrupt — each
  mutation touches exactly one file. I still keep the "the LLM never writes the store
  directly" principle (three small, single-purpose scripts: capture / retire / validate), but
  I do not need the heavyweight all-or-nothing delta object to get it.
- **In the agent-supplied half, only `intent` is mandatory.** `expected`, `observed`,
  `impact`, `workaround` are each independently optional. See §3 for why, and §10 for the
  honest cost of that choice.

## 2. The record shape — a real worked example

One episode = one file. Two examples: a typical capture, and the same story consolidated
later (to show the lifecycle fields in use without inventing a second scenario).

**`.agent-work/episodes/active/governor-268-e2.md`** (as captured, mid-run):

```markdown
<!-- episode: v1 id=governor-268-e2 -->
# episode:governor-268-e2

## mechanical
- run: governor-268
- role: commander
- step: m3-execute
- captured: 2026-07-27 (governor-268)
- context: manifest:governor-268-run1@a1b2c3d
- reopens: 1
- artifact: staged-feedback/governor-268/AGENT_FEEDBACK.md#L14-22

## agent
- intent: verify the STATE_NOTE fallback path exists before editing commander-core.md
- observed: skills/workbench/templates/STATE_NOTE.template.md exists but .agent-work/templates/ is absent in this fresh worktree, contradicting the launch order's assumed fallback location

## diagnosis

## lifecycle
- status: active
```

Notes on what's *not* there: `refusals`, `rework`, `failed-command` are omitted — this
episode had none, and a mechanical field with nothing to report costs nothing to omit (same
convention `apply_lessons_delta.py` already uses for `bank-reason`/`recurrences`: rendered
only when set, defaulted on parse). `expected`, `impact`, `workaround` are omitted — the
agent judged `observed` self-explanatory against `intent` and didn't spend effort restating
an expectation that's obvious from the intent line. The `## diagnosis` heading is present
with nothing under it — headings are cheap and mechanical (written by the capture script
regardless), so the *partition itself* is always visible even when a section is empty.

**Same episode, one Admiral run later, after a governor-268-class doctrine sweep
independently reproduces it and a reviewer assigns strength, then a later consolidation
subsumes it** — moved to `.agent-work/episodes/retired/governor-268-e2.md`:

```markdown
<!-- episode: v1 id=governor-268-e2 -->
# episode:governor-268-e2

## mechanical
- run: governor-268
- role: commander
- step: m3-execute
- captured: 2026-07-27 (governor-268)
- context: manifest:governor-268-run1@a1b2c3d
- reopens: 1
- artifact: staged-feedback/governor-268/AGENT_FEEDBACK.md#L14-22

## agent
- intent: verify the STATE_NOTE fallback path exists before editing commander-core.md
- observed: skills/workbench/templates/STATE_NOTE.template.md exists but .agent-work/templates/ is absent in this fresh worktree, contradicting the launch order's assumed fallback location

## diagnosis
- suspected-cause: fallback-path doctrine names one sibling template but not this one — cause-source: reviewer:g1, governor-268 AGENT_FEEDBACK.md 'Friction/unclear' section
- proposed-remedy: enumerate every sibling template in the drill scope, not just the first one fixed — remedy-source: reviewer:g1, same citation

## evidence
- corroborated-by: fleet-doctrine-sweep-269-e1 — same missing-fallback shape, independently found in skills/admiral/references/fleet-doctrine.md:57
- strength: medium — reviewer:g1, 1 corroborating episode vs 0 disputing, see governor-268 AGENT_FEEDBACK.md

## lifecycle
- status: retired
- retired: 2026-07-28 (epic-298-consolidation) — subsumed into drill-scope-should-name-every-sibling-template
- superseded-by: consolidation:drill-scope-should-name-every-sibling-template
```

Nothing was deleted or rewritten in place to get from the first version to the second — every
line in v1 is still present in v2; only lines were **appended**, plus one file **move**
(`active/` → `retired/`, done by the retire script, not by hand-editing content).

## 3. The mechanical / agent-supplied partition, visible in the file

The partition is not implied by field-name prefixing — it is a literal `## ` heading, so a
naive `grep '^## '` on any episode file enumerates the partition without needing to know a
single field name:

- `## mechanical` — written by the capture tooling from harness/engine state only. Zero
  agent effort by construction: nothing under this heading is ever agent-authored text.
- `## agent` — the deliberately small agent-supplied half. Only `intent` is required; the
  rest exist as optional slots the agent fills only when they add signal the mechanical
  block doesn't already carry.
- `## diagnosis` — always present as a heading, always legal to leave empty. See §4.
- `## evidence` — cross-episode corroboration/dispute links plus an optional `strength`
  assessment. Never written by the capture script; only ever appended by a downstream act
  (reviewer, consolidation sensor) with a citation. See §5.
- `## lifecycle` — `status`, and (only once retired) `retired` + `superseded-by`. See §7.

A reader — human or script — never has to infer "is this field mechanical or agent-supplied"
from naming convention; the answer is which heading it sits under.

## 4. Suspected-cause and proposed-remedy as separate optional assertions

`## diagnosis` is a section of its own, not a field of `## mechanical` or `## agent`. Two
independent, both-optional lines:

- `- suspected-cause: <text> — cause-source: <who/what asserted it + citation>`
- `- proposed-remedy: <text> — remedy-source: <who/what asserted it + citation>`

Either, both, or neither may be present — an episode with an empty `## diagnosis` section is
a complete, valid episode (the worked v1 example above has exactly this). They are not
required to co-occur: a cause can be suspected with no remedy proposed yet, and — less
common but legal — a remedy can be proposed as a experiment ("try X and see") without a firm
suspected cause behind it. Each carries its own `-source` citation because a diagnosis is
itself an assertion (see §5) and needs the same source-attribution any Stratum A claim needs;
it is never mechanically inferred.

## 5. Field-by-field Stratum A mapping — a real mapping, not a promise

| Stratum A dimension | Episode field(s) | How it is populated |
|---|---|---|
| **Identified assertion** | `## agent → observed`, or — if `observed` is absent — the raw mechanical anomaly itself (`refusals`, `reopens`, `rework`, `failed-command` lines) | The claim being made: "X was observed," or, with no narrative at all, "command Y failed N times." The validator (§9) requires at least one of {`observed`, a non-zero mechanical anomaly field} — an episode can never assert nothing. |
| **Source** | `## mechanical → run, role, step, captured` | Always present, always mechanical: who/where/when the claim originated. Zero agent effort. |
| **Supporting evidence (intra-episode)** | `## mechanical → artifact` (repeatable), `failed-command` (repeatable), `context` | Concrete citations backing the claim, captured by the harness at the time of the episode. |
| **Supporting evidence (cross-episode)** | `## evidence → corroborated-by` (repeatable) | Appended later, by a downstream act (reviewer or #308's consolidation sensor), citing another episode id plus a reason. The slot exists in the schema from the first commit of this design — nothing about adding a corroboration later requires a shape change. |
| **Challenging evidence** | `## evidence → disputed-by` (repeatable) | Identical shape to `corroborated-by`, opposite direction. Also never populated by the capture script — only by a downstream act with a citation. |
| **Qualitative strength (weak/medium/strong)** | `## evidence → strength` | **Never auto-computed and never store-guessed** — assigning strength by weighing evidence is a judgment call, the same category of stochastic work the brief assigns to the downstream sensor (constraint 5: "finding that two episodes rhyme is a sensor job... the store never guesses"). The field exists and is legal to set, but only by an explicit downstream act carrying a citation (mirrors the prior art's grounding-required convention for `confirm`/`disconfirm`). Left absent, an episode is simply *unassessed*, which is a valid, complete state — not a missing field. |
| **Lifecycle standing** | `## lifecycle → status, retired, superseded-by` | Fully separate from `strength`. An episode can be `status: retired` (superseded by a consolidation) while its `strength` field, if ever set, still reads `medium` unchanged — retirement moves the file and appends a reason; it never touches `strength`. This is the literal, mechanical enactment of "belief strength and lifecycle standing remain separate dimensions." |

The one interpretive call I'm making explicit: strength is a *field that exists but is
usually empty*, populated only by a deterministic, attributable, citation-carrying act (never
by the store computing it from counts). I considered instead deriving it automatically from
`len(corroborated-by) - len(disputed-by)`, which would keep the store "fully mechanical" in
letter, but a bare arithmetic derivation over-claims precision an evidence *count* doesn't
actually support (two weak corroborations aren't obviously "stronger" than one strong one) —
so I chose to expose the countable inputs and require the judgment be made and cited
explicitly downstream, rather than have the store quietly compute a number that looks
authoritative but isn't. This is a place where I'd want the panel/Admiral to weigh in if they
disagree.

**The manifest obligation (#300, not designed here):** `context` stores a reference plus the
revision it resolved at (`manifest:<manifest-id>@<revision>`), per the brief's literal
phrasing of the obligation. My requirement on #300 is exactly what the brief already states —
an enumerable set of `(loaded-artifact-id, canonical-revision)` pairs reachable from that
reference — and I don't see a reason #300 needs to change shape to serve this; no float.

## 6. File layout and deterministic retrieval

```
.agent-work/
  episodes/
    active/
      governor-268-e1.md
      governor-268-e2.md
      fleet-doctrine-sweep-269-e1.md
    retired/
      epic-198-burndown-e3.md
```

Rooted via the same `agent_work_root.durable_root()` helper `apply_lessons_delta.py` already
uses (unmodified, imported, not touched) — so episodes captured in any linked worktree land
in the **main checkout's** `.agent-work/episodes/`, visible to every other worktree and every
later session, exactly like the lessons playbook already is. This is not a new convention; it
is reuse of one that ships today.

**Episode id**: `<run-id>-e<seq>`, e.g. `governor-268-e2`. `run-id` is the harness's own
work-id (mechanical, already known at capture time); `seq` is a per-run monotonic counter the
capture script owns (scan `active/` + `retired/` for the highest existing `<run-id>-e*` and
increment — no shared counter file to get out of sync, since it's derived from the
filesystem itself each time). Collision-free across concurrent runs by construction (distinct
run-ids); collision-free within a run because the capture script is the only writer of that
run's sequence.

**Retrieval — all of it is `ls`/`grep` over the two directories, no parser required for the
common cases:**

- Enumerate all active episodes: `ls .agent-work/episodes/active/*.md`
- Enumerate everything ever captured (active + retired, for history/consolidation-neighbour
  work): `ls .agent-work/episodes/*/*.md`
- Exact-match by run: `grep -l '^- run: governor-268$' .agent-work/episodes/active/*.md`
- Exact-match by role+step: `grep -l '^- role: commander$' ... | xargs grep -l '^- step: m3-execute$'`
- Set-membership by touched artifact: `grep -l '^- artifact: .*STATE_NOTE' .agent-work/episodes/active/*.md`
- By id directly: `.agent-work/episodes/active/<id>.md`, falling back to
  `.agent-work/episodes/retired/<id>.md` if not found active — a two-glob check, still
  deterministic, no ambiguity (an id lives in exactly one of the two directories at a time).

For structured field extraction (not just membership), a ~15-line parser reusing the prior
art's own regex convention (`^- ([a-z-]+): (.*)$` for fields, `^## (\w+)$` for section
headers) is sufficient — genuinely small because there is no cap/counter/dormancy state to
reconstruct, only one episode's flat field set. This is the store's entire query surface: no
similarity, no ranking, no embedding — exact string match and set membership, exactly as
constraint 5 requires, and it composes with any Unix-toolable `grep`/`ls`, which is what
"deterministic means over Markdown in git" cashes out to concretely.

## 7. Retirement policy, mechanically stated

Retirement is exactly two mechanical actions, done together by one small script
(`retire_episode.py <id> --reason "..." [--superseded-by <ref>]`), never by hand-edit:

1. **Append**, inside the file, under `## lifecycle`: `- status: retired`, replacing
   `- status: active`, plus `- retired: <date> (<work-id>) — <reason>` (reason is
   **required**, mirroring the prior art's retire-requires-reason rule), plus, if given,
   `- superseded-by: <ref>`.
2. **Move** the file: `git mv .agent-work/episodes/active/<id>.md .agent-work/episodes/retired/<id>.md`.

The move is what makes "retired = excluded from ordinary rhyme-search" mechanical: ordinary
retrieval (§6) globs `active/` only. The append-not-delete is what makes "retained in
history" mechanical: `retired/` is a permanent, fully readable, fully grep-able directory —
nothing is ever truncated, and git's own history additionally preserves every prior state of
the file regardless. Retirement never means the content disappears; it means it moved out of
the *default* search path while staying byte-for-byte intact and independently findable by
the same `ls`/`grep` primitives, just pointed at the other directory.

I did not build a dormancy/auto-expiry mechanism (the prior art's `tick` + `dormancy-runs`).
That machinery exists to auto-GC lessons that stop being reconfirmed. Episodes are not
reconfirmed in place (§1) — an episode is retired by an explicit act (a human, a reviewer, or
#308's consolidation loop), never by silently aging out. Under minimal-record, inventing an
aging mechanism nothing here requires would be adding state to guess "is this still
relevant" — exactly the kind of judgment the brief reserves for the downstream sensor.

## 8. The cross-session retrieval exercise

**Acceptance exercise ("a seeded episode is retrievable across sessions")**, concretely:

1. **Session 1** (a fresh process — e.g. one `python`/PowerShell invocation, or one Claude
   Code session): run `capture_episode.py --run test-run-1 --role commander --step m1
   --context manifest:test@abc123 --intent "verify X"`. It scans `active/` +`retired/` for
   the next seq, writes `.agent-work/episodes/active/test-run-1-e1.md`, prints the id, and
   exits. Nothing is held anywhere but the file on disk — no server, no cache, no open
   connection.
2. **The session boundary**: a genuinely new process, sharing nothing with session 1 but the
   git working tree — no imported Python objects, no inherited environment variables scoped
   to session 1, no warm cache of any kind. This is trivially an honest boundary here *because
   the read path is `open(path).read()` from disk, full stop* — there is no daemon or
   in-memory index that could accidentally leak session-1 state into session 2 even by
   accident.
3. **Session 2** (a different fresh process, possibly a different tool entirely — e.g. a bare
   `grep` at a terminal, no Python at all): `grep -l '^- run: test-run-1$'
   .agent-work/episodes/active/*.md` finds the file; reading it recovers exactly the fields
   session 1 wrote, byte-identical.

Because retrieval has no state beyond the filesystem, this exercise is satisfied by
construction rather than by careful session-boundary engineering — which I read as a genuine
strength of the minimal-record shape, not just a checkbox pass.

**The harder downstream companion (owned at #308, must not be precluded):** seed four
episodes describing the same recurring defect across four different runs
(`run-a-e1`..`run-d-e1`). At consolidation time, the sensor adds `corroborated-by` links
between all four (mutual citations), then retires two of them (`run-a-e1`, `run-b-e1`) with
`superseded-by: consolidation:<slug>`, appending the reason and moving the files — leaving
`run-c-e1` and `run-d-e1` active and untouched. Confirm two things mechanically: (a) ordinary
rhyme-search (`grep` over `active/`) still finds `run-c-e1` and `run-d-e1` — they were never
touched by the consolidation, so nothing about retiring their neighbours removed them; (b)
the retired pair remain fully readable under `retired/`, and their `corroborated-by` lines
still point at `run-c-e1`/`run-d-e1` by id, so the audit trail is walkable in both directions
— from a still-active neighbour, one can find which retired episodes it corroborated, and
from a retired episode, which still-active ones back it. Nothing in this design requires a
schema or store-shape change to make that walk work; the links and the two-directory split
already carry it.

**What I tested (by construction/reasoning) vs. what I did not**: I worked through the
retrieval commands and file transitions above by hand against the worked examples in §2, and
they check out. I did **not** run actual scripts (none were written — this is a design
candidate, no implementation, per the brief) and I did not measure real concurrent-write
behavior under git; the "one file per episode never conflicts" claim is a structural argument
(two new files never collide), not an empirically observed merge.

## 9. One adversarial fixture to catch a wrong answer

Two, because the failure modes are different in kind and the brief asks for one that could
produce either a false FAIL on valid input or a silent PASS on invalid input:

**(a) False FAIL / conflation — decoy field line inside free text.** Because retrieval is
line-based grep on `^- field: value$`, a naive parser that doesn't restrict where field lines
can appear is vulnerable to a multi-line agent value that happens to *contain* a line shaped
like a field. Fixture: an episode whose `observed` line reads (as a single logical value, but
if a naive implementation allowed embedded newlines, spanning two physical lines):

```
- observed: the agent's own note says "- run: decoy-999" was the one that actually failed, but that's prose inside this field, not a new field
```

A correct implementation must never treat that decoy text as a real `run:` field of some
other episode. My design's actual defense: agent-supplied free-text fields are **single-line
by convention and by capture-script validation** — `capture_episode.py` rejects any
`--intent`/`--observed`/`--expected`/`--impact`/`--workaround` argument containing a newline
outright, so the ambiguous case can't be written in the first place. The fixture is exactly
the regression test that catches an implementation that skipped that rejection: hand-craft
the file directly (bypassing the script, as a corrupt/hand-edited input would), run the
retrieval/parser against it, and assert it does **not** produce a phantom `decoy-999` episode
or corrupt the real `run: test-run-1` value it should read for that file.

**(b) Silent PASS on invalid — missing mandatory field.** Hand-craft an episode file with a
complete `## mechanical` block but an **empty** `## agent` section (no `intent` line at all,
not even blank) and `## diagnosis`/`## evidence` also empty. A naive validator that only
checks "the file exists under `active/` and has a `run:` line" would silently accept this as
a legal episode. My design's `validate_episode.py` (small, mirrors the prior art's
`flush()`-time required-field check: `required = ("run","role","step","captured","context",
"intent","status"); missing = [...]`) must **reject** this file. The fixture additionally
covers the boundary a naive "is the key present" check would miss: `- intent: ` (key present,
value empty string) must fail the same way as the key being wholly absent — presence of the
line is not presence of content.

## 10. Honest self-scoring

- **Depth — good, with a caveat.** The store hides retrieval mechanics (which directory, what
  grep pattern) behind three small named scripts a caller never has to look inside. The
  caveat: some of that "depth" is really "there is less complexity to hide" rather than
  complexity genuinely hidden — I removed the delta-validator layer instead of concealing it,
  which is honest but means less is centrally guarded against a hand-edited file than the
  lessons playbook's single gatekeeper provides. I accept that trade under this constraint
  but flag it plainly rather than claim it away.
- **Locality — strong.** One capture touches exactly one new file; one retirement touches
  exactly one existing file (content append + move). No shared growing document, no
  cross-worktree contention, no fan-out. This is where the constraint paid off most cleanly.
- **Seam placement — good.** The mechanical/stochastic seam sits exactly where constraint 5
  wants it: the store exposes stable ids, enumerable fields, and link slots; all
  rhyme-judgment and strength-judgment happen downstream, on top, never inside. The
  seam toward #305 (capture wiring) is thinner than I'd like — I sketched a CLI shape for
  `capture_episode.py` because #305 needs *something* to build against, but I did not design
  its triggers, which is correctly out of scope, not a flaw of this design, but it does mean
  that seam is less proven than the retrieval seam.
- **Testability — strong.** Every pathway (capture, id-lookup, run/role/step grep,
  set-membership grep, retire, corroborate/dispute, cross-session boundary) is exercisable
  independently against plain hand-crafted Markdown fixtures, with no shared state to fake.
  Both adversarial fixtures in §9 are cheap to write and target real, specific
  implementation choices (single-line enforcement; mandatory-field enforcement) rather than
  generic parser fuzz.
- **Where the constraint hurt.** Minimizing the agent-supplied half means a lean episode
  (§2's v1 example) can be *thin enough that a downstream reader has to do real work to
  understand why it matters* — the cost of low authoring effort is partly a transferred cost
  onto whoever consolidates or judges rhymes later, who may need to cross-reference the
  mechanical block and artifact refs to reconstruct context a fuller `expected`/`impact`
  narrative would have handed them directly. Relatedly, dropping confirm/disconfirm counters
  means a *single* episode, read alone, carries less inherent trust signal than a
  `LESSONS.md` entry with `confirmed: 5` — that's a deliberate trade (adjudication lives at
  #308, not per-capture) but it is a real one, not a free lunch. And the single-line
  discipline on agent fields (chosen for parse-safety, §9) means a genuinely gnarly narrative
  either gets compressed awkwardly or pushed out to an `artifact` reference — usable, but a
  real friction point a less minimal design wouldn't have.

## Honest sizing

If the issue's own framing implies episodes need something close to the lesson-playbook's
weight (counters, cap, dormancy, batch-validated deltas), I don't think that's true, and I
think that's a legitimate, useful finding under this constraint rather than a shortfall: an
episode is a cheap, atomic, single-write observation, not a curated evolving claim, and the
adjudication machinery that makes sense for the latter is over-engineering for the former.
What I did **not** test: actual concurrent-worktree write behavior under real git, and
real script implementations (none were written, per scope). What I did work through
concretely: every retrieval path, the full retirement transition, the Stratum A mapping
field-by-field, and both adversarial fixtures, all against real worked examples rather than
abstract field lists.
