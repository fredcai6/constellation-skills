# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` — episode record grammar and store doctrine (issue #301, epic-298)

## Result
`BLOCK`

VERDICT: BLOCK

Driven survey: `.agent-work/301/g1-review/review.json` (session `reviewer-g1-301`, claimed/released),
Fowler pass record: `.agent-work/301/g1-review/fowler-pass.json` (`verify_fowler_pass.py` exit 0).

## Handoff compliance
The deliverable matches the g1-handoff task statement: `docs/EPISODE_STORE.md` (503 lines, 10
sections) and `episodes/README.md` exist, both new. C2, C4, C5, C6, C7, C8, C9 are each
substantively satisfied, not just grep-matchable — verified by reading the actual sections, not
taking the implementer's spot-check greps at face value. C3 is where this review found a genuine
defect (below).

## Scope drift
None. `git status --short --untracked-files=all` shows exactly the two allowed files. Specific
exclusions honored: `LESSONS.md`/`apply_lessons_delta.py` untouched, #300's manifest not designed
(only an obligation stated on it), no capture/consolidation code, no executable code or tests.

## Evidence verdict
Both claimed side-effects independently reproduced, not just re-read from the report:
- `git check-ignore episodes/ ; echo $?` → **exit=1** (not ignored) — matches implementer's and
  Commander's claim exactly.
- `python -m pytest tests/ -q` → **1157 passed, 2 skipped, 260 subtests** — exact match to the
  claimed baseline (used `python`, not `py`, per the handoff's Windows note).

All three load-bearing evidence items (Stratum A + addressability worked example, tracked-path
proof, retirement-layout-open quote) are present. The retirement-layout quote is present verbatim,
but its surrounding text has the consistency defect described below, which weakens how genuinely
open it reads in practice.

## Code/doc quality
Fowler pass (r6-fowler): 12/12 baseline smells visited, rail exits 0. 10 absent, 1 overridden
(`primitive-obsession`, subordinate to `constraint:markdown-in-git` — flat string fields are the
medium's sanctioned shape, not an oversight), 1 **flagged**: `shotgun-surgery` — binding the
retirement layout at g4 will require scattered edits (§2, §7, §8) rather than one localized
change, the same root cause as the top finding below.

## Map impact verdict
- **Evidence supports claimed change:** yes, verified independently (see Evidence verdict).
- **Constraints not violated:** yes — markdown-in-git, stochastic-boundary-B0.1, and
  retired-is-excluded-not-deleted are all honored in the text.
- **Notes match the diff:** yes, files/sections claimed match what was actually written.
- **Decision candidates surfaced:** partially. `decision:store-lives-at-a-tracked-path` correctly
  marked resolved; `decision:episode-store-shape` correctly marked NOT resolved. But the Map
  Impact's "Trust limitations / drift found: none found" does not surface the effect-level
  pre-emption risk this review found — a minor completeness gap, not independently costly since
  Commander's own handoff shows they had already caught the same concern before dispatch.
- **Durable context routed:** yes, no orphaned decisions.

Not blocking on its own (folded into the finding below, same root cause).

## Reconciliation check
No `docs/architecture/` packet exists in this worktree (confirmed: `ls docs/architecture` → no
such file), consistent with the implementer's "skill-source repo, no packet map" framing. No
architecture divergence beyond what is captured in the findings below.

## Findings, most serious first

### 1. [BLOCKER — High] SS7's worked retirement example asserts Option B's behavior as
unconditional fact, contradicting the "HELD OPEN" declaration two paragraphs later
**File:** `docs/EPISODE_STORE.md`, §7.

**This directly answers the "HUNT THIS SPECIFICALLY" ask: Commander's reading is correct, and
independent testing found a sharper, more literal instance than the one originally flagged.**

Quote, immediately after the retirement worked-example diff:

> Nothing else in the file changes... **The file is never deleted, moved, or truncated** —
> "retained in history" is one field flip on the same file at the same path, not a second data
> store to keep in sync.

Two paragraphs later, the very next subsection:

> **Layout — HELD OPEN, not chosen here.** Whether retiring an episode: **(Option A) moves the
> file** between `episodes/active/<id>.md` and `episodes/retired/<id>.md`... **or** (Option B)
> changes a `status` field in place...

"The file is never... moved" and "at the same path" are true **only under Option B**. Stated as
unconditional fact in the worked example, this contradicts Option A's own definition in the
following paragraph. This is not an inference risk or a matter of careful reading between the
lines — it is a direct textual self-contradiction inside the same section that then claims to
hold the choice open. A reader who takes the worked example at face value (which is what worked
examples are for) walks away believing the file-never-moves behavior is settled, when it is not.

**Fix:** qualify the "never moved" sentence — e.g. "the episode's *content* is never deleted or
truncated; whether the file's *path* also stays fixed is exactly the layout question below" —
rather than asserting path stability as a blanket property of retirement.

### 2. [BLOCKER — High] SS8's "additive, not a rewrite" claim does not hold for g3's
implementation, only for the primitive's name — no membership-predicate seam is named
**File:** `docs/EPISODE_STORE.md`, §7 (closing paragraph) and §8.

§7 claims: "binding the layout later is additive, not a rewrite of g2 or g3's own contracts...
the retrieval primitives operate on 'does this episode carry a non-retired status,' never on
'does this path live under `active/`.'" §8 then specifies the mechanism concretely: "every
retrieval primitive... is a direct path read or **a line-anchored grep**" — and §7's own
single-line-enforcement paragraph confirms the "enumerate non-retired" primitive's actual shape
is "a negative 'not retired' filter over `## Retirement`'s `status` field" — i.e., content
parsing. No seam abstracts this the way §1 names "one named seam" for `durable_root()`.

Tested against reality: if g3 is built literally to this text (content-based/grep), then
ratifying Option A later requires **rewriting g3's ordinary-search implementation** from
content-parsing to directory-globbing to realize any of Option A's structural-immunity benefit.
Without that rewrite, Option A becomes a cosmetic directory split that retrieval never actually
trusts — exactly "true in letter and hollow in effect," Commander's own phrase for the failure
mode. So §7's "additive, not a rewrite" claim is true only for the **caller-facing primitive
name**, not for the **implementation**, and the document does not draw that distinction — a
builder reading it at face value would not know to preserve rewrite-freedom.

**Answering Commander's Q3 directly: yes**, the right fix is to route the membership predicate
through one named adapter seam — e.g. `is_episode_active(episode_id)` — with an Option-B adapter
(grep the `status` field) and, if/when Option A is bound, an Option-A adapter (check which
directory the id resolves under). g3's enumerate/select primitives call the seam, never the
mechanism directly. This uses the doc's own vocabulary (`references/global-everyone.md`
"Deep-module vocabulary": Seam = where an interface lives, Adapter = a thing satisfying an
interface at a seam) and mirrors §1's existing "one named seam" treatment of `durable_root()`.
That makes g4's binding genuinely additive — swap the adapter, not the primitive — instead of a
retrieval rewrite disguised as "additive."

### 3. [Minor — Low] SS2's "the filename is the id" claim quietly assumes Option B's flat path
**File:** `docs/EPISODE_STORE.md`, §2.

"The filename **is** the id: `episodes/<id>.md`" is stated unconditionally. Under Option A the
full relative path becomes `episodes/active/<id>.md` or `episodes/retired/<id>.md` — the
*basename* is still the id, but the claimed path form is not. Same root cause as findings 1–2
(prose defaults to Option B without flagging the conditionality), smaller blast radius. Fold into
the same fix pass.

### 4. [Observation — carries to g3, not blocking] Fowler shotgun-surgery flag
Binding the retirement layout at g4 currently requires scattered edits across §2, §7, §8 rather
than one localized change — the Fowler-pass record for this same root cause. Resolves
automatically once findings 1–3 are fixed with a named seam.

### 5. [Observation — carries to Cartographer/Commander closeout, not blocking] Map Impact
completeness gap
The implementer's "Trust limitations / drift found: none found" did not surface this pre-emption
risk. Not independently costly here since Commander caught the same concern before dispatch, but
worth naming so a future doc-gate's self-review looks harder at claims like "additive, not a
rewrite" before asserting them.

## What I verified as fine (independently, not taken on the report's word)
- `git check-ignore episodes/` exits 1 — reproduced myself.
- `python -m pytest tests/ -q` — reproduced myself, 1157 passed / 2 skipped / 260 subtests,
  exact match.
- `git status --short --untracked-files=all` — confirmed only the two allowed files touched.
- C2 (§4 literal `## Mechanical` / `## Agent-supplied` / `## Diagnosis (optional)` headings,
  always written), C4/C5 (§5/§6 worked dispute walkthrough + Stratum A table, checked against
  the same worked episode, lifecycle-standing shown as a genuinely separate dimension), C6 (§1,
  one named seam, no `durable_root()` call), C7 (§8 explicit no-ranking/no-similarity/no-embedding,
  #300 obligation correctly stated as an obligation not a spec), C8 (§2, panel-unanimity
  retraction named explicitly, reasoning stands independent of it), C9 (§9, epic-lease exception
  and read-only fence both explicitly addressed) — read in full, not spot-checked.
- No `docs/architecture/` packet exists in this worktree — confirmed directly.
- Fowler pass rail (`verify_fowler_pass.py`) exits 0 against a full 12-smell record.

## What I could not check, and why
- Whether g2/g3's eventual implementers would in fact misread SS7/SS8 as Commander and I did —
  this is a prediction about future work, not something directly testable at this gate. My
  confidence rests on the text being ambiguous/self-contradictory on its face, independent of who
  reads it next.
- No code exists yet, so I could not test retrieval behavior directly — this gate is
  inspection-only by design and I did not ask for tests, per the handoff's explicit exclusion.

## Blockers
- Findings 1 and 2 above. Both are prose-only fixes confined to `docs/EPISODE_STORE.md` §2, §7,
  §8 — no design re-litigation, no re-opening of the retirement-layout decision itself. Recommend:
  (a) qualify §7's "never moved / same path" sentence so it does not assert Option B's behavior
  as settled, and (b) name one membership-predicate seam in §7/§8 (mirroring §1's `durable_root()`
  treatment) so "additive, not a rewrite" becomes true of the implementation, not just the
  primitive's name. Both are small, targeted edits — this should not meaningfully delay g2/g3.

## Out-of-scope observations
- Findings 3–5 above — carry finding 3 into the same fix pass as 1–2 (cheap, same file); findings
  4–5 are informational, no action required beyond awareness at g3/closeout.

## Workflow Feedback
- **Handoff gaps:** None material. The handoff's "HUNT THIS SPECIFICALLY" section was unusually
  well-targeted — it named the exact section, quoted the exact claim, and asked three specific
  testable questions, which made independent verification fast and concrete rather than a vague
  "does this seem OK" ask. Worth naming as a pattern other reviewer handoffs with a candidate
  defect should copy.
- **Context rediscovered:** None — the handoff, g1-handoff.md, and g1-result.md together carried
  everything needed; I did not need to dig outside them except to independently read the doc
  itself and reproduce the two evidence commands.
- **Instructions improvised around:** The reviewer skill's `r6-fowler` check assumes code exists
  to smell-test. This diff is prose-only. Rather than invoking the skill's docs-only-diff
  co-sign/override escape hatch (awkward here since I am the sole independent reviewer for this
  gate — there is no second reviewer to co-sign my own override), I instead ran the pass in full
  and marked each baseline smell `absent`/`overridden`/`flagged` against the *document's
  structure* (treating sections/claims as the analog of methods/classes where a smell concept
  transfers, e.g. shotgun-surgery over scattered layout-assumption edits) rather than skipping the
  item. This produced a genuinely useful flag (shotgun-surgery, reinforcing finding 1–2) rather
  than a ceremonial pass-through, so I'd suggest the skill text acknowledge this as a sanctioned
  reading of "run the pass" for a docs-only diff, not just "skip with co-sign."
- **What would have made this easier:** Nothing structural. One small note: the checklist
  engine's `append` put `r7-hunt-preemption` after `r6-fowler` in execution order even though I
  appended it right after `r1-handoff` — cosmetic only, did not affect the review, but a
  Commander reading the journal in id order rather than execution order should know appended
  items go to the end of the queue, not next-in-line.

## Return status
`complete`
