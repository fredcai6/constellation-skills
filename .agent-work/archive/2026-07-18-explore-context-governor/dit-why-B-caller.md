# Why-capture — design B (constraint: COMMON-CALLER-FIRST)

Panel: design-it-twice, "why-capture" extension to the checklist engine (context-governor
module 1). Constraint assigned to this design: shape the interface around how `advance`/`attach`
are ACTUALLY called today; the 90% flow must be effortless; the rare case may be more verbose.

## Grounding — how callers actually invoke advance/attach today

From `scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, and every role skill
(`implementer/SKILL.md`, `_shared/global-everyone.md`, `workbench/references/checklist-engine.md`):

- `advance <id>` fires **once per gate** — the terminal, status-flipping call. It already has a
  refusal idiom every agent has learned: `REFUSED: {id}: postconditions unmet [...]`, fix the
  named gap, retry. Agents are drilled ("Ask the engine `current`... `advance` only once its
  postconditions pass") to treat a refusal as the next instruction, not friction to route around.
- `attach <id> --type <t> --field K=V` fires **multiple times per gate** — evidence bookkeeping
  (a `review-result`, a `user-decision`, a `file-diff`). `global-everyone.md` explicitly teaches
  *attach once, reference by `attest --evidence` elsewhere* — i.e. the doctrine already treats
  attach as a comparatively cheap, repeatable, low-ceremony call, unlike advance.
  Most evidence on a task is in fact never a CLI `attach` at all — `_check_condition`
  auto-records `command`/`git-change-policy` evidence directly, bypassing the `attach()` API
  entirely. So the population of *agent-issued* `attach` calls is smaller and lower-stakes than
  it first looks.
- The fixed design spec's own **Error modes** line names only `advance`: "a non-exempt advance
  with no why-answer is refused." `attach` appears in the *interface* sentence but not in the
  *enforcement* sentence. I read that gap as intentional room, and this design uses it: the
  mandatory prompt concentrates at the one **already-refusing, once-per-gate** call (`advance`);
  `attach` gets an *optional*, never-refusing why so evidence bookkeeping never slows down.

## Fields added

**Checklist-level** (new top-level array, same shape family as `blockers` / `triage_candidates`):

```json
"why_trail": [
  {
    "seq": 1,
    "ts": "<iso8601>",
    "task": "g1",
    "verb": "advance",
    "why_done": "mechanical",
    "now_understand": "the retry storm was a missing backoff, not a network flake",
    "next": "mechanical",
    "mechanical": false
  }
]
```

`mechanical` is a derived convenience flag (true iff all three text fields equal the literal
sentinel `"mechanical"`) — not authoritative, just cheap filtering for anyone skimming the trail.

**Task-level:** one new optional field, `"why_exempt": bool`, set only by a template author
authoring the gate (never by a verb — no CLI toggle exists for it, matching the fixed-context
requirement that it is a template-authoring-time decision).

No new config field. See *Invariants* for why a global on/off switch is deliberately omitted.

## The common path — advance

```
advance g1                                   # unchanged call, no why flags
advance g1 --why mechanical                  # the ENTIRE mandatory prompt, in one token
advance g1 --now-understand "TTL off-by-one, not a cache stampede"
```

- `--why mechanical` is a one-token literal shorthand: fills `why_done = now_understand = next
  = "mechanical"`. This is the frequent-case answer the fixed context calls first-class.
- `--why-done TEXT`, `--now-understand TEXT`, `--next TEXT` are independent, optional flags.
  **Any one of them, given alone, satisfies the whole prompt** — the other two silently default
  to `"mechanical"`. An agent that only has something real to say about *one* of the three parts
  (usually `now_understand`, since that's the live digest) never has to hand-fill the other two.
  This is the load-bearing common-caller-first move: the realistic frequent case is "I have one
  sentence of real understanding to leave behind," not "I have three."
- `--why mechanical` composes with a granular override: `--why mechanical --next "run the
  integration suite next"` sets `why_done = now_understand = "mechanical"`, `next = "..."`. An
  agent spends words only where it has something non-trivial to say.
- `--why` accepts **only** the literal `mechanical`; any other value is a usage error
  (`EngineError: --why accepts only 'mechanical'; use --why-done/--now-understand/--next for free
  text`) — keeps the one-token shortcut unambiguous instead of a second free-text channel that
  competes with the granular flags.

**Enforcement, precisely:** inside `advance()`, postconditions are checked exactly as today
(unchanged code path, unchanged refusal message) *first*. Only once postconditions pass does the
engine ask: is this task `why_exempt`? If not, and none of `--why-done` / `--now-understand` /
`--next` / `--why mechanical` were supplied, refuse:

```
REFUSED: g1: advance requires a why-answer (--why-done/--now-understand/--next, or --why mechanical); this gate is not why_exempt
```

then flip status to `complete` and append the `why_trail` record last. Checking postconditions
before the why-requirement means the *new* friction never compounds with the *old* friction — an
agent mid-flight on unmet postconditions never sees a why-refusal it can't yet act on; the new
refusal appears exactly once, at the true end of the gate, reusing the exact refusal idiom
(`REFUSED: ...`, fix the named thing, retry) agents already drill on.

## The common path — attach

```
attach g1 --type review-result --field verdict=APPROVE            # unchanged, exactly as today
attach g1 --type review-result --field verdict=APPROVE --now-understand "reviewer flagged the retry storm"
```

`attach` gains the same three optional flags plus `--why mechanical`, with the same
any-one-fills-the-rest defaulting. **Unlike `advance`, attach never refuses.** If none of the why
flags are given, nothing changes: no record is appended, no prompt, zero new cost on the call
agents make several times per gate. If any are given, one `why_trail` entry is appended with
`"verb": "attach"`. This is the asymmetry the constraint buys: the once-per-gate checkpoint
carries the mandatory prompt; the many-times-per-gate bookkeeping call stays exactly as fast as
it is today, with an *opt-in* channel for an agent that wants to leave reasoning where it
happened rather than saving it all for the final advance.

## `why_exempt` — keeping exempt gates silent

- Read from the **active task**, not global config. Absence of the `why_exempt` key on a task
  defaults it to **exempt** (`true`) — the same backward-compat posture the engine already uses
  for `engine_session` ("a checklist with no lease behaves exactly as before"). A template that
  has never heard of this feature has not set the field; treating that silence as exemption means
  **every existing template keeps behaving exactly as it does today**, with zero migration and
  zero new refusals, until a human deliberately opts specific gates in by authoring
  `"why_exempt": false` on them.
- On an exempt task: `advance` never checks for a why-answer (no refusal, ever, regardless of
  flags). `attach`'s optional why-flags, if supplied anyway, are silently **ignored, not
  recorded** — an exempt gate's why_trail stays empty even if an agent passes the flags out of
  habit, so exempt gates genuinely never prompt *and* never accumulate trail noise.
- `amend`: `why_exempt` becomes one more field the `add` op can set on a new pending gate, and one
  more overwritable field for `rescope`. This is a small, necessary companion touch (one line
  each in `_build_amend_task` and the `rescope` field allowlist), not a new module.

## Digest retrieval

No new verb. `current` — the call every agent already makes between every step — gains one more
optional line, appended the same way the lease line already is:

```
LEASE active: commander/issue-420/attempt-2 (by commander, heartbeat ...)
ACTIVE g2 [in-progress] — wire the retry backoff
DIGEST: TTL off-by-one, not a cache stampede
```

`DIGEST` is the `now_understand` field of the **last** `why_trail` entry (checklist-wide, not
per-task — the whole point of a top-level, flat, seq-ordered trail is that "the latest" is a
single O(1) read with no per-task hunting). Absent when `why_trail` is empty (nothing to digest
yet) — no line printed, matching how the lease line is already conditionally omitted.

Programmatic/handoff consumers (the Refresh module) read `cl["why_trail"]` directly from the
persisted JSON, the same way they already read `blockers`/`triage_candidates` directly rather
than through a dedicated query verb — no new read-surface to design.

## Invariants

1. Absence of `why_exempt` on a task ⇒ exempt (opt-in enforcement; see above).
2. `why_trail` entries carry a monotonic `seq` (`len(why_trail) + 1`), independent of the
   evidence-id and journal sequence spaces.
3. `why_trail` is **never** touched by `reopen`'s reset/cascade — postconditions and evidence
   reset on rework, but recorded understanding is not erased by a gate being redone. This matches
   the fixed-context invariant: "the sequence is the append-only history."
4. Postconditions are checked before the why-requirement inside `advance` (see *Enforcement*).
5. A refused `advance` (either failure mode) appends no `why_trail` entry — the check reads args
   and existing state only; it performs no mutation before raising, so a why-refusal leaves
   `why_trail` exactly as it was, and `main()`'s existing persist-on-refusal path (which already
   saves any postcondition-check evidence) is unaffected by this addition.

## Error modes

| call | outcome |
|---|---|
| `advance g1` (non-exempt, postconditions unmet) | unchanged: `REFUSED: g1: postconditions unmet [...]` |
| `advance g1` (non-exempt, postconditions met, no why flags) | `REFUSED: g1: advance requires a why-answer (...); this gate is not why_exempt` |
| `advance g1 --why mechanical` | succeeds; `why_trail` gets one entry, all three fields `"mechanical"` |
| `advance g1 --now-understand "..."` | succeeds; `why_done`/`next` backfilled to `"mechanical"` |
| `advance g1 --why banana` | `EngineError: --why accepts only 'mechanical'; use --why-done/--now-understand/--next for free text` |
| `advance g1` (why_exempt: true, no flags) | succeeds silently; no `why_trail` entry, no prompt |
| `attach g1 --type ...` (no why flags) | unchanged: exactly today's behavior, no `why_trail` entry |
| `attach g1 --type ... --now-understand "..."` | succeeds; one `why_trail` entry, verb `"attach"` |
| `attach g1 ... --why mechanical` (why_exempt: true) | succeeds; flags silently ignored, no entry recorded |

## Config

None added. `why_exempt` is a per-task, author-declared field — no global toggle. Deliberate:
one fewer knob to learn, and the backward-compat default (absence ⇒ exempt) already gives a
whole-template escape hatch without needing a project-level switch.

## Journal interaction (deliberately deferred, not silently skipped)

The append-only hash-chained journal (`append_journal_entry`) is unchanged: it keeps recording
`verb`/`task`/`evidence_ids` only, nothing from `why_trail`. A forger wanting to fabricate a
convincing why-trail would still have to produce consistent monotonic `seq` values within
`why_trail` itself, which is some resistance, but it is *not* woven into the journal's hash chain
the way evidence ids are. Folding `why_trail` entries into the journal payload (e.g. a hash of the
latest why record) is a natural follow-up hardening step but is out of scope here — flagged, not
silently assumed solved.

## Self-assessment

**DEPTH.** One token (`--why mechanical`) discharges the entire mandatory-prompt obligation on
the one call that enforces it. Behind that token the interface hides: three-field defaulting,
seq-ordering, the exemption default, and digest surfacing through the verb agents already call
between every step. A caller who wants to say something real reaches for up to three flags and
never needs to know `why_trail`'s shape, the seq scheme, or how exemption defaults. High
depth on the enforcing path.

**LOCALITY.** Enforcement is entirely inside `advance()` (~10 lines: an exemption check, a
"none of the four flags" check, the defaulting logic, one append). `attach()` gets a symmetric
but non-refusing ~6-line addition. `current()` gets one conditional line. No caller-side
machinery, no new module, no new files. The one thing that could look like a locality gap —
enforcement lives only in `advance`, not `attach` — is not a gap: every legal path off
`in-progress` for a gated task passes through `advance` (that's the only status-flipping verb),
so there is no route that closes a gate while skipping the enforcing call.

**SEAM PLACEMENT.** The why-prompt rides the two verbs that already carry the doctrine rail
(`RAIL_VERBS` includes `advance`/`attach`) and the two verbs `dispatch()` already treats as
mutating/railed chokepoints — no new seam is invented, an existing one is reused. `why_exempt`'s
seam is the task JSON itself, the same place `postconditions`/`preconditions` already live as
author-declared per-task data, not a new config layer parallel to the existing one.

**TESTABILITY.** Every behavior above is a pure function of `(task, args)` — no filesystem, no
git, matching the existing `test_checklist_engine.py` style. Concretely testable: non-exempt
advance with no why flags refuses; why_exempt advance with no flags succeeds and appends nothing;
`--why mechanical` fills all three; a lone `--now-understand` backfills the other two; `--why
banana` is a usage error; `why_trail` survives `reopen` untouched; `current` shows `DIGEST:` after
an entry exists and omits it when `why_trail` is empty; `attach` with no why flags never appends.

## What this constraint costs

- **The recorded triple is often 2/3 filler.** Optimizing for "fill the one field you actually
  have something to say about" means `why_done`/`next` will frequently just read `"mechanical"`
  even in gates where the agent *did* have real things to say elsewhere. Nothing stops an agent
  from filling all three when it matters (final gates, near-terminal steps) — but nothing nudges
  it either. A quality-first design might have wanted a richer per-field prompt; this one trades
  that for a single-sentence common case.
- **Attach's optionality is a real enforcement gap, accepted deliberately.** An agent could
  front-load all its genuine reasoning into `attach` calls and hand `advance` nothing but `--why
  mechanical`, technically compliant while defeating the spirit of the capture. This mirrors how
  the engine already treats qualitative postconditions (`attest` can assert falsely; the engine
  checks mechanism, not honesty) — consistent with existing philosophy, but worth naming as a cost
  a quality-first design (the sibling panel constraint) would likely refuse to accept.
- **Backward-compat-by-default under-rolls the feature at ship time.** Because absence of
  `why_exempt` means exempt, no existing template gains why-capture until a human explicitly edits
  templates to set `why_exempt: false` on chosen gates. That is slower than a global switch that
  turns it on everywhere at once — the tradeoff is zero migration breakage in exchange for a
  rollout that needs a deliberate second step (template authoring) before it does anything.
