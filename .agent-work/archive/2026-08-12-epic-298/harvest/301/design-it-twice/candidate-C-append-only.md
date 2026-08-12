# Candidate C — append-only-history

## 1. The constraint, restated, and what it drove

**Named constraint: append-only-history.** Nothing in an episode's on-disk record is ever
mutated in place. An episode is the *fold* of a strictly ordered, append-only sequence of
stamped entries. "Add a diagnosis" appends an entry. "Retire" appends an entry. "Supersede"
appends an entry. There is no line in any file that a later operation edits, reorders, or
deletes. Current state — "is this episode still live," "what's the strongest suspected
cause right now" — is never stored as the truth; it is *computed* from the log, every time,
by a pure function (a fold) that the store ships alongside the log.

What this drove, directly, not as afterthought:

- **One file per episode**, not one shared growing file. Append-only at the *line* level
  (like `apply_lessons_delta.py`'s `- history: ...` lines) still lets you overwrite the
  `- status: active` line next to it. To make "nothing is edited" literal, the *whole
  record* for one episode has to be the append log — every field, not just history —
  so the file itself can be opened in append mode and nothing already on disk is ever
  rewritten.
- **Retirement falls out for free.** "Retired means excluded from ordinary search, retained
  in history" is not a flag I had to invent a rule for — it is what "append a `retire`
  entry to an immutable log" *means*. The entry that marks an episode retired sits in the
  same file, in the same append stream, as every entry that came before it. You cannot
  retire an episode without keeping its whole history, because there is no other place to
  put the history — the log *is* the episode.
- **Suspected-cause / proposed-remedy as separate optional assertions falls out too**: they
  are just entry *kinds* that may or may not appear in a given episode's stream. An episode
  with zero `diagnose` entries is a complete, valid fold (open, undiagnosed) — nothing is
  missing, because nothing was ever a required field to begin with.
- **The real cost, confronted, not hidden**: reading "what is true now" requires a fold, not
  a grep. Files grow monotonically — there is no delete, and (honestly) no compaction,
  because compaction would be a rewrite and the whole point is that nothing rewrites. I
  address the "not directly greppable" problem with a derived, disposable projection
  (§6) that is *never* the source of truth and is explicitly allowed to be wrong until
  reconciled — see §6 for exactly how that's kept honest, and §9 for the fixture that
  catches it when it silently isn't.

## 2. The record shape — a real worked example, including an append that changes standing

Layout: one append-only file per episode at
`.agent-work/episodes/log/<episode-id>.md`. Nothing above the last line is ever touched by
any later operation; every mutation is `open(path, "a").write(new_entry)`.

Here is `.agent-work/episodes/log/governor-hard-band-none-vs-low.md` as it exists on disk,
shown at four points in its life — but on disk it is **one file**, and everything below is
literally present in it, top to bottom, in this order, forever.

```markdown
# episode:governor-hard-band-none-vs-low

## entry:0001 — 2026-07-27T09:12:04Z (work-id: governor-265) — op: create
### mechanical (engine/harness-captured)
- run: governor-265
- role: implementer
- spine-step: m2-implement
- context-manifest: manifest-ref:governor-265/run-manifest.json@sha256:7f3c1a…
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: (none)
- artifact-refs: crew-handoffs/265-result.md#L18-L40
### agent-supplied
- task-intent: keep the Context Governor's HARD band readable as "a speed bump, not a
  wall" per the push-not-pull ruling
- expected-behavior: an absent gauge reading renders as visibly distinct from a real
  low reading, so a silent gap in instrumentation is never confused with "things are fine"
- observed-behavior: `_gauge_reading()` returns `None` on a missing gauge.json, and the
  HARD-band comparator sorts `None` below LOW, so an absent reading silently passes as
  "ok" instead of surfacing as a gap
- impact-cost: ~40min rework loop; caught by manual re-test, not by the original suite
- workaround: none applied yet

## entry:0002 — 2026-07-27T10:03:41Z (work-id: governor-265) — op: diagnose
- assertion-id: 0002
- suspected-cause: the HARD-band comparator treats a missing reading (None) as strictly
  less than LOW because it does `if reading and reading >= HARD_THRESHOLD`, so `None`
  falls through every branch and lands in the same "fine" path as a genuinely low number
- source: crew-handoffs/265-result.md#L52 (traced comparator with pdb against a
  gauge.json-less worktree)
- strength: medium

## entry:0003 — 2026-07-27T10:20:15Z (work-id: governor-265) — op: corroborate
- assertion-ref: 0002
- source: crew-handoffs/265-result.md#L58 (independent repro: fresh worktree, gauge.json
  deleted, comparator returns band=ok with no reading present)
- note: reproduced on a second, independently-created worktree — not the same repro as
  entry 0002's original trace

## entry:0004 — 2026-07-27T10:41:02Z (work-id: governor-265) — op: remedy
- assertion-id: 0004
- proposed-remedy: give an absent reading its own band value (NONE) distinct from LOW,
  rendered as a visible gauge gap rather than folded into the "fine" path
- source: crew-handoffs/265-result.md#L66 (patch sketch, not yet applied this episode)
- strength: medium

## entry:0005 — 2026-07-28T08:55:30Z (work-id: governor-268) — op: restrength
- assertion-ref: 0004
- strength: strong
- grounding: PR #283 shipped exactly this remedy (NONE band, distinct from LOW) and the
  fix held under governor-268's independent re-check — proposed remedy is now the shipped
  fix, not a hypothesis

## entry:0006 — 2026-07-28T09:02:11Z (work-id: governor-268) — op: retire
- reason: consolidated and shipped — PR #283 "make a non-reading visible, distinct from a
  low reading (#265)"; the remedy in entry 0004 is now the fix. Full history above is
  retained; this episode is excluded from ordinary rhyme-search from this entry forward.
```

That sixth entry is the append that changes standing — from `open` to `retired` — without
touching a single byte written before it. The file is longer after retirement, never
shorter, never edited.

## 3. The explicit mechanical / agent-supplied partition

Visible in the record itself, not implied by naming: the `create` entry (the only entry
kind that carries both) is split into two literal subheadings, `### mechanical
(engine/harness-captured)` and `### agent-supplied`, shown above. The partition is not a
convention agents are trusted to honor — `apply_episode_delta.py` (§6) hard-splits the
`create` op's payload into two required sub-objects, `mechanical` and `agent_supplied`, and
rejects a delta where a mechanical field appears under `agent_supplied` or vice versa
(field-name allowlist per group, same shape as `SCOPES`/required-field validation in
`apply_lessons_delta.py`'s `validate_delta`). Mechanical fields are populated by the caller
from harness state the agent never touches (run id, role, active spine step, the context
manifest reference, refusal/reopen/rework counters, failed-command log, artifact refs) —
the agent process supplies zero of them. Agent-supplied fields are deliberately the small
list the brief names: task-intent, expected-behavior, observed-behavior, impact-cost,
workaround. Nothing else is agent-writable at `create` time.

## 4. Suspected-cause and proposed-remedy as separate, optional, later appends

They are not fields of `create` — they are their own entry *kinds* (`diagnose`, `remedy`),
each optional, each addable independently, at any later time, by any later work-id. Entry
0001 in §2 has neither. Entries 0002 and 0004 add them, two work-ids and roughly ninety
minutes apart in the worked example — a diagnosis and a remedy do not have to arrive
together, or from the same run, or ever arrive at all. An episode with only a `create`
entry is complete and valid: `open`, no diagnosis, no remedy, fully retrievable. This is the
direct payoff of §1's "entry kind, not required field" move.

## 5. Stratum A mapping — field by field, from the real entries above

Non-foreclosure requires this to work without a later rewrite. Here it is, against the
concrete assertion in entry 0002 (not a promise — these are the actual lines from §2):

| Stratum A dimension | Where it lives in the record | Concrete value from §2 |
|---|---|---|
| Identified assertion | `(episode-id, assertion-id)` pair, plus the assertion's own text field | `(governor-hard-band-none-vs-low, 0002)` → *"the HARD-band comparator treats a missing reading (None) as strictly less than LOW…"* |
| Source | the assertion entry's `source:` field | `crew-handoffs/265-result.md#L52 (traced comparator with pdb…)` |
| Supporting evidence | every later `corroborate` entry whose `assertion-ref:` matches the assertion-id, folded into a list | entry 0003: independent repro on a second worktree |
| Challenging evidence | every later `challenge` entry whose `assertion-ref:` matches (none in this episode) | *(none present — an empty list is a valid fold result, not a missing field)* |
| Qualitative strength | the assertion entry's `strength:` field, **overridden by the latest `restrength` entry referencing it, in file order** | entry 0002 set `medium`; the *remedy* assertion (0004) was later restrengthed to `strong` by entry 0005 — strength is per-assertion and independently revisable |
| Lifecycle standing (separate dimension) | derived by folding only the entries that reference a given assertion-id (`challenge`→disputed, `reject`→rejected, otherwise→asserted); **independent of the episode's own standing** | assertion 0002: `asserted` (never challenged or rejected) — true even though the *episode* itself is `retired` as of entry 0006 |

The last row is the point non-foreclosure is actually testing: an assertion's belief
strength and standing, and the *episode's* standing, are three independently-derived values
from three independent folds over the same log, and none of them required editing anything
to change. Episode standing is itself computed the same way, one level up: fold the
episode-level entries (`create`→open, `supersede`→superseded, `retire`→retired) in file
order; entry 0006 is the last episode-level entry, so standing is `retired`.

## 6. File layout and deterministic retrieval over a log

```
.agent-work/episodes/
  log/
    <episode-id>.md          # one append-only file per episode — SOURCE OF TRUTH
  INDEX.md                   # derived projection — regenerated wholesale, never edited
```

**Writing.** `scripts/apply_episode_delta.py` (mirrors `apply_lessons_delta.py`'s
contract): takes a JSON delta (`work_id`, `episode_id`, `op`, op-specific fields), validates
it (unknown op, missing required field, bad assertion-ref, mechanical/agent-supplied
cross-contamination → the whole delta rejects, nothing is written), then does exactly two
things: (a) appends the rendered entry to `log/<episode-id>.md` (assigning the entry number
as `count(existing "## entry:" headings) + 1` — assigned by the script, never by the agent,
so entry order and file order are the same thing by construction — no clock trust required);
(b) regenerates `INDEX.md` from scratch by folding every log file. Same script, same
invocation, one atomic write to each of the two files, mirroring the prior art's "the LLM
never writes the store directly."

**INDEX.md** is a plain enumerable table, one row per episode, current-fold-only:

```markdown
<!-- episodes-index: generated-at=2026-07-28T09:02:12Z entries-folded=6 -->
| episode-id | run | role | standing | has-diagnosis | has-remedy | log-entries | fold-hash |
|---|---|---|---|---|---|---|---|
| governor-hard-band-none-vs-low | governor-265 | implementer | retired | yes | yes | 6 | a91f7c… |
```

`fold-hash` is a SHA-256 over the exact bytes of `log/<episode-id>.md` at the moment INDEX
was generated. It is the honesty check: **`INDEX.md` is not trusted on its own.** A reader
that wants a fast answer reads `INDEX.md`; a reader that wants a *safe* answer (or the
`apply_episode_delta.py` regeneration step itself) recomputes each row's hash against the
live log file and treats a mismatch as "this INDEX row is stale — refuse or rebuild," never
as "trust the row." Disagreement is resolved with one rule, always: **the log wins,
unconditionally; `INDEX.md` is discarded and regenerated from the logs, in full, never
patched.** `INDEX.md` carries no information the logs don't already carry — it is a cache,
not a second copy of truth, and the cache is verifiable cheaply (one hash per episode)
without doing the full fold.

**Reading (mechanical, deterministic, no ranking, no embeddings):**

- *Ordinary rhyme-search* (what a Stratum B sensor works on top of, per constraint 5):
  `episode_query.py --standing open --field run=governor-265` — filters `INDEX.md` rows by
  exact/set-membership match, `standing != retired and standing != superseded` implicit
  in "ordinary." Purely mechanical: string/enum equality over enumerable fields, nothing
  fuzzy.
- *Full current view of one episode* (the fold, exposed as a callable, not hand-rolled by
  every caller): `episode_query.py --fold governor-hard-band-none-vs-low` — reads the one
  log file, folds it top to bottom, prints the current view (episode standing, latest
  strength per assertion, latest standing per assertion, all mechanical/agent-supplied
  fields from `create`). This is the pure function §1 promised; it never consults
  `INDEX.md`.
- *Full history, including retired* (what the harder downstream companion needs, §8):
  `episode_query.py --history governor-hard-band-none-vs-low` — prints every raw entry, in
  file order, unfiltered. Retired episodes are never excluded from this path; only from the
  `--standing open`-style ordinary search.

**The cost, stated plainly.** Folding one episode is O(entries in that one file) — cheap,
because the store is one-file-per-episode, not one growing shared file (the direct benefit
of the §1 decision to depart from the prior art's single-shared-playbook layout). Folding
*all* episodes (what `INDEX.md` regeneration does) is O(total entries across every episode)
and happens on every write — that is a real, monotonically growing cost as the store
accumulates episodes, and I am not hiding it: at scale this is the first place the "add an
incremental per-episode INDEX update instead of a full rebuild" optimization would need to
land, and I have deliberately not designed that optimization here because a full rebuild is
trivially correct and an incremental one is not (see §9) — "full rebuild for correctness
now, optimize later under observed pressure" is the same posture the brief's Markdown-over-
Neo4j ruling already takes.

## 7. Retirement policy

`retire` and `supersede` are the two terminal-standing episode-level ops:

- `retire`: requires a `reason` (validated non-empty, same discipline as
  `apply_lessons_delta.py`'s `retire`/`defer`). Sets episode standing to `retired` from that
  entry forward. Does not require naming a successor — "no longer relevant" is a valid
  reason on its own (e.g., "the underlying code path was deleted").
- `supersede`: requires a `successor-episode-id` that must already exist as a log file (or
  be created in the same delta — the delta script accepts a batch so `create` for the
  successor and `supersede` for the predecessor can land atomically). Sets episode standing
  to `superseded`, distinct from `retired`, so a rhyme-search sensor that follows
  `superseded-by` pointers forward can do so mechanically (an exact-match traversal, not a
  guess).

Both are appends. Neither deletes the file, truncates it, or removes it from `log/`.
**Retired/superseded means excluded from `--standing open` ordinary search and retained
under `--history`.** There is no separate "graveyard" section or file to move things into
(unlike the prior art's now-removed Dormant section) — the log a retired episode lives in
*is* its permanent record; retirement is one more line in it, not a relocation.

There is deliberately **no dormancy auto-delete** here, and no cap. That is the constraint
biting: `apply_lessons_delta.py`'s dormancy GC *deletes* a lesson (removes its block
entirely) when it goes stale. Under append-only-history that operation doesn't exist —
there is nothing to delete without violating the constraint, and the brief is explicit that
durability past consolidation is a hard requirement, not a nice-to-have. The honest
consequence: this store has no self-cleaning mechanism and will need one designed
separately (an archival/cold-storage move, never a delete) if episode count becomes a real
operational problem — I am flagging that now rather than pretending append-only gets GC for
free.

## 8. The cross-session retrieval exercise

"A seeded episode is retrievable across sessions," made concrete against this design:

1. **Process A** (a Bash/PowerShell tool call, PID N): run
   `python scripts/apply_episode_delta.py delta-create.json` with a `create` op. This writes
   `log/governor-hard-band-none-vs-low.md` (entry 0001) and regenerates `INDEX.md`. Process
   A then exits — no daemon, no server, nothing held in memory past the process boundary.
2. **Honest session boundary**: a genuinely new process, invoked in a *separate* tool call
   (a fresh `python` interpreter, new PID, no imported module state, no shared variables) —
   the only thing it shares with Process A is the git working tree on disk. This is real in
   this repo's own tooling model: every Bash/PowerShell tool call in this harness already is
   a fresh process with a reset working directory (stated in this session's own tool
   contract), so the exercise doesn't need to be staged specially — it's the default way
   every subsequent tool call already runs.
3. **Process B**: `python scripts/episode_query.py --standing open --field
   run=governor-265` — must list `governor-hard-band-none-vs-low`. Confirms `INDEX.md`
   survived the process boundary and reflects the write.
4. **Process C**: `python scripts/episode_query.py --fold governor-hard-band-none-vs-low` —
   must reproduce the exact `task-intent`/`expected-behavior`/`observed-behavior` text from
   `delta-create.json`, read fresh off disk, folded from zero, with no cache from Process A
   or B available to it. This is the real test of the constraint: Process C has never seen
   the in-memory `Playbook`/entry objects Process A built — it re-derives the identical
   current view purely from the bytes in `log/governor-hard-band-none-vs-low.md`.

## 9. Adversarial fixture — catching a fold that returns stale or wrong current state

The brief's own callout is exactly the failure mode I'm most exposed to (§1, §6): a fold
that silently returns wrong current state. Two fixtures, the first primary:

**Fixture A — stale `INDEX.md`, primary.** Hand-construct a log file
`log/fixture-stale.md` with a `create` entry followed by a `retire` entry (standing should
fold to `retired`), then hand-construct an `INDEX.md` whose row for `fixture-stale` still
says `standing: open` and `log-entries: 1` (simulating a regeneration that ran before the
`retire` entry was appended — e.g., someone appended directly to the log file, bypassing
`apply_episode_delta.py`, which is a realistic failure mode since the log is a plain text
file nothing prevents `>>` against). Feed this pair to `episode_query.py --standing open`.
A **correct** implementation recomputes `fixture-stale`'s hash against the live 2-entry log,
sees it doesn't match `INDEX.md`'s recorded hash for a 1-entry log, and either (a) excludes
the row and reports it stale, or (b) transparently re-folds that one episode instead of
trusting the cached row — either way it must **not** report `fixture-stale` as `open`. A
**naive** implementation that reads `INDEX.md` at face value without the hash check reports
`fixture-stale` as `open` — a silently wrong current-state answer, exactly the failure class
named in the brief. This is the test I'd write first, before anything else, because it's
the one place this design's whole safety argument (§6: "the log wins, INDEX is a checked
cache") either holds or doesn't.

**Fixture B — trusting embedded timestamp over append order.** Hand-construct a log where
entry 0002 (`diagnose`, physically first) carries a *later* wall-clock timestamp string than
entry 0003 (`retire`, physically second and correctly final) — plausible in practice from
clock skew between two machines racing to append near-simultaneously, or a work-id backfilling
a diagnosis it had actually formed earlier. A **naive** fold that sorts entries by the
embedded `timestamp` string before folding (a superficially reasonable "chronological order"
optimization) processes `retire` *before* `diagnose` and reports standing as `open` — wrong,
and silently so. A **correct** fold trusts entry-number / physical file order only — which is
authoritative by construction, because `apply_episode_delta.py` assigns entry numbers itself
from the existing count in the file, never from agent-supplied timestamps — and reports
`retired`, matching entry 0003 being the last entry physically present. The embedded
timestamp field is for humans reading the file; it is never a sort key in the store's own
mechanics.

Both fixtures are exactly the shape the brief warns is easy to get wrong (false PASS on
stale/invalid, not false FAIL on valid) — a round-trip test over a real, freshly-generated
episode would never exercise either, because a real run never produces a stale INDEX or an
out-of-order timestamp on its own.

## 10. Honest self-scoring

- **Depth — good, with one leak.** The fold is genuinely hidden behind
  `episode_query.py --fold`: a caller never re-implements "what does retired mean" or
  "which strength wins." The leak: a caller who reads `INDEX.md` directly (rather than
  through the query tool) can see a stale row if they skip the hash check themselves —
  the safety property lives in the *tool*, not in the file format, so a shortcut around the
  tool is a real way to leak the complexity back upward. I'd flag this as the one place a
  reviewer should insist the tool is the only sanctioned reader.
- **Locality — good for writes, honestly mixed for reads.** Every episode's own history is
  fully local to one file — appending a diagnosis to episode X touches zero bytes belonging
  to any other episode, a real and valuable property the single-shared-playbook prior art
  doesn't have (an edit to one lesson's block sits inside the same file every other lesson's
  block sits inside). But every *write* also touches the shared `INDEX.md`, and the cost of
  keeping that shared file honest (§6's O(all entries) rebuild) is a fan-out this design
  does not avoid, only makes cheap-to-verify. That is the constraint's real locality tax:
  perfect write-locality at the log layer, paid for with a shared, growing regeneration
  cost at the projection layer.
- **Seam placement — good.** The three retrieval shapes callers actually want —
  "is X still live," "give me X's current view," "give me X's whole history" — map onto
  three distinct, independently testable operations (`INDEX.md` filter,
  `--fold`, `--history`) rather than one API that quietly does different things depending on
  a flag. #308's consolidation/rhyme-search sensor sits cleanly on top of the first two
  without needing to know the log format at all.
- **Testability — the constraint's best result.** Every pathway is a pure function over
  bytes on disk: append validation, single-episode fold, INDEX regeneration, and
  hash-freshness are each independently fixturable with hand-authored `.md` files, no
  mocking, no timing. §9's two fixtures are exactly the adversarial shape the brief asked
  for and neither is reachable from a "seed a real episode and round-trip it" test — a
  reviewer has to author them by hand, which is itself evidence the store needed them.
- **Where the constraint hurt.** No GC, ever (§7) — this design is honestly larger over time
  than a mutate-in-place design, and I'm not claiming otherwise. Trivial corrections (a typo
  in `task-intent`) cost a full appended correction entry rather than a one-line edit — real
  ergonomic friction for a case that doesn't deserve ceremony. And the two-file layout
  (log + INDEX) is strictly more moving parts than a single file would be — append-only
  bought retirement-for-free and per-episode write-locality, but it did **not** buy cheap
  "what's true now right now" for free; I had to build and separately justify a cache for
  that, and that cache is the single largest source of remaining risk in this design (§9,
  Fixture A). A candidate under a different named constraint that allows in-place field
  updates would not need an INDEX at all — it would just grep the one file. That's the
  honest price of this constraint, paid in full, not hidden.
