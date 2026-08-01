# Design-it-twice comparison and recommendation — issue #301

**Status: this is a FLOAT.** Per `decision:convergence-is-human`, I generated and compared;
the convergence choice belongs to the Admiral to surface to Tommy. Below is a defended
recommendation, not a menu — but it is not a decision I have taken.

Panel: **N=4**, one named distinct constraint each, run in parallel with no visibility of
each other. Rationale for panel-over-single: one of the epic's two load-bearing interfaces,
the first accumulating store the design builds, and a spec-mandated design-it-twice.

| | Constraint | File |
|---|---|---|
| A | minimal-record | `candidate-A-minimal-record.md` |
| B | assertion-native | `candidate-B-assertion-native.md` |
| C | append-only-history | `candidate-C-append-only.md` |
| D | retrieval-first | `candidate-D-retrieval-first.md` |

---

## 0. CORRECTION NOTICE — this document was revised after a cold critic

A cold critic (no authoring context) attacked the first version of this comparison and found
that **I manufactured consensus on two of my six "unanimity" claims and overstated a third.**
I verified every one of its claims mechanically before accepting them. The corrections are
folded into §1, §6, and §7 below. Recording it here rather than quietly editing, because the
Admiral had already received the first version and the errors were material.

What was wrong, and the command that proved it:

- `for f in candidate-*.md; do grep -ic "durable_root\|durable root" "$f"; done` → A:1, B:5,
  **C:0, D:0**. My claim that all four reused `durable_root()` was false, and the candidate I
  recommended is one of the two silent on it.
- Episode-id scheme: only A (`<run-id>-e<seq>`) and D (`<run>-<seq>`) derive an id from
  run+sequence. **B** specifies `ep-[a-z0-9][a-z0-9-]*`, a kebab-case slug; **C**'s worked
  example is the narrative slug `governor-hard-band-none-vs-low`. 2 of 4, not unanimous.
- `grep -n "^### mechanical\|^## entry" candidate-C-append-only.md` → C's partition headings
  are `### mechanical` / `### agent-supplied` nested under `## entry:0001`. A `grep '^## '`
  does **not** match a `###` line, so my claim that this grep enumerates the partition on any
  candidate's file is false for C.

## 1. What the panel actually settled — corrected

Four agents, four constraints, no contact. **Four** things genuinely landed unanimously;
two I previously listed did not, and are demoted to majority positions.

**Unanimous (verified against all four candidate files):**

1. **One file per episode.** Not one growing `EPISODES.md`. Every candidate derived this
   independently: a shared mutable file is a merge-conflict generator across concurrent
   worktrees, and this epic is running three commanders at once. (C partly undoes this in
   spirit by adding a shared `INDEX.md` — see §4.)
2. **Retirement never deletes and never truncates.** Four different mechanisms, same rule.
3. **The LLM never writes the store directly** — mutation goes through a validated script.
   A keeps the principle while dropping the batch-delta object; the principle still holds 4/4.
4. **Suspected-cause and proposed-remedy are separately attachable and genuinely optional** —
   an episode with no diagnosis is complete and valid in all four.

**Majority, NOT unanimous — real open decisions, not settled findings:**

5. **Episode id from run+sequence** (A, D) **vs a descriptive kebab slug** (B, C). This is a
   live decision. Run+seq is mechanically derivable at capture time with zero agent effort,
   which is why I still prefer it — but it is my preference, not the panel's verdict.
6. **`durable_root()` reuse for cross-worktree durability** (A, B explicitly; C and D silent).
   **This is the most consequential correction.** No candidate's cross-session exercise tests
   a cross-*worktree* boundary — every one tests "a new process, same working directory."
   Given that episodes will be captured by concurrent commanders in separate worktrees, a
   store that resolves `.agent-work/` worktree-locally produces N siloed stores rather than
   one findable one. **This must become an explicit requirement of whatever design is chosen,
   and the acceptance exercise must cross a worktree boundary, not just a process boundary.**

## 2. The panel-level honest-null worth reporting

**Every candidate independently declined to import the lessons-playbook machinery.** No
counters, no cap, no dormancy/auto-expiry, in any of the four — each argued, separately,
that an episode is a *raw atomic capture that is written once and then stands or is retired*,
whereas a lesson is a *curated evolving claim that gets reconfirmed*. The adjudication
machinery that is right for the latter is over-engineering for the former.

So: **the store issue #301 needs is meaningfully smaller than the issue's framing implies.**
Per the Honest-Null Clause this is a result, not a shortfall. What that conclusion rests on:
four independent design passes reasoning from the record's usage, plus a read of the prior
art. What it does **not** rest on: any measurement of a populated store, which does not exist
yet. If #308's consolidation loop turns out to need per-episode adjudication counters after
all, this conclusion is the thing to revisit first.

## 3. The real axis of disagreement

Once the unanimous six are set aside, the candidates differ on exactly one question:

> **How is "what is true now" represented — stored, or derived?**

- **A, B, D: stored.** Current state is a field you read directly. Mutation edits that field
  (and appends history lines alongside it).
- **C: derived.** The file is an append-only log; current state is a pure fold over it, with
  a hash-verified `INDEX.md` cache regenerated on every write to keep things greppable.

A secondary axis: **how much assertion structure to commit to up front** — B maximal
(everything is an assertion block, including `reopen_count=0`), A minimal (assertion slots
exist but are usually empty), C and D in between.

## 4. Axis-by-axis

**Testability — D wins, and not narrowly.** Every retrieval path in D is a literal shell
command that can be falsified on its own. D's adversarial fixture is the single best artifact
the panel produced: an episode with `status: disputed` — legitimately *not retired* — which a
naive positive-allowlist implementation of "enumerate non-retired episodes"
(`rg -l '^- status: active'`) silently drops, with no error and no crash, returning a
candidate set one file short and no signal that it is short. That is precisely the failure
class our inherited `lesson:round-trip-tests-prove-artifacts-not-parsers` warns about, and it
forces the allowlist-vs-denylist choice to be made deliberately rather than by accident. A's
two fixtures are good; C's fold-staleness fixture is necessary only because C introduced the
INDEX that creates the staleness.

**Locality — A and D strong; C fails here.** This is C's decisive problem and its own
self-scoring does not catch it. C regenerates `INDEX.md` from scratch **on every write**.
That makes every episode capture touch a shared file — reintroducing exactly the
cross-worktree merge contention that all four candidates independently designed
one-file-per-episode to avoid. C flags the *growth* cost of full regeneration honestly; it
does not flag the *concurrency* cost, which bites immediately at this epic's own three
concurrent commanders, not eventually.

**Depth — D.** Six enumerated retrieval questions collapse to two primitives: a direct path
read, and a grep with an optional retired filter. A caller and the downstream #308 sensor
need to learn two things, not a storage schema. C's depth is undercut by the INDEX being a
second moving part with its own honesty protocol.

**Seam placement — D, with A dissenting interestingly.** D inherits
`apply_lessons_delta.py`'s validated all-or-nothing delta seam rather than inventing one —
the right amount of novelty for a first accumulating store. A deliberately *drops* it,
arguing there is no cross-referencing state to protect since each mutation touches exactly
one file. A's argument is genuinely good and I nearly took it. What it loses is a single
gatekeeper that can enforce the mechanical/agent partition at the only write path — see
graft 1.

**Non-foreclosure — B is best by construction, at a price I do not think is worth paying.**
B satisfies Stratum A expressibility by identity: there is no mapping because there is
nothing to map. But B renders `reopen_count=0` as a five-line assertion block carrying
`strength` and `standing`, and assigns mechanical facts `strength=strong / standing=active`
**by class default**. That is not merely verbose — it manufactures a stored belief assessment
about a fact nobody has asserted, which sits awkwardly against the truth model's own
requirement that strength "creates no inertia against decisive new evidence." D reaches
adequate non-foreclosure with a real, concrete mapping at a fraction of the cost.

## 5. D's distinctive insight, which no other candidate got as cleanly

D separates two things the other three partly conflate:

- **`lifecycle-standing`** is per-**assertion**: "is this specific claim still believed?"
- **`status`** is per-**episode**: "is this episode in the ordinary rhyme-search universe?"

These are genuinely different questions. An episode can be `retired` — consolidated away, out
of ordinary search — while its individual assertions remain `active` and true. Retirement is
a **search-visibility switch, not a verdict on the claims.** That is the literal mechanical
enactment of the truth model's "belief strength and lifecycle standing remain separate
dimensions," and it is the property that makes the #308 companion exercise work: the
neighbour relationship (shared `artifact-ref`) is timeless, and only whether it surfaces *by
default* changes.

## 6. Recommendation

**Take D as the spine, with three named grafts.** Not a menu, not a hybrid-by-averaging —
D's structure, plus three specific things the other candidates did better.

**Graft 1 — from C: make the partition mechanically unforgeable.** C's writer hard-splits the
create payload into required `mechanical` and `agent_supplied` sub-objects with a field-name
allowlist per group, and **rejects** a delta where a mechanical field appears under
`agent_supplied` or vice versa. D states the delta contract but leaves the partition
conventional. The spec requires the partition be *explicit*; enforcement at the single write
path is what makes it explicit rather than merely documented. Cheap, and it is the difference
between a rule and a habit.

**Graft 2 — from A: always write the fixed section headings, even when empty.** A's
observation is right — headings are cheap and mechanically written, so *the partition itself
stays visible even in a minimal episode*. Under D as written, a minimal episode (no
diagnosis) and a schema-drifted episode are indistinguishable to a naive check. With A's
convention, `grep '^## '` enumerates the full schema on every file.

**Graft 3 — from A and the prior art: `retire` requires a non-empty reason, validated.** D
has a `retired-reason` field but does not make it mandatory. `apply_lessons_delta.py` already
enforces exactly this rule for its own `retire` op; inherit it rather than re-deciding it.

**Graft 4 — from A, ADDED AFTER THE COLD CRITIC: single-line enforcement on agent-supplied
free-text fields, validated at write time.** This closes a silent-omission hole that inverts
D's own testability argument. D's ordinary-search filter is *negative* — find files WITHOUT a
`- status: retired` line. D never specifies single-line enforcement, so if an agent's
`observed-behavior` value spans physical lines and any continuation line reads
`- status: retired` (easy: quoting a transcript that discusses a retired episode), that line
matches the anchor and the episode is **silently excluded from ordinary search while being
fully active** — no error, no crash. A negative filter is *more* exposed to this than a
positive one: under an allowlist the injected text must spell "active" to do harm; under D's
denylist any text spelling "retired" does harm. A already designed this defense and shipped a
fixture for it; D did not import it. Also line-anchor the filter with `-x`, matching what D
already does for its other queries, which closes a forward-compatibility hole where a future
status value merely *starting with* "retired" would be silently swept up.

**Graft 5 — from B, ADDED AFTER THE COLD CRITIC: per-field assertion addressability for the
agent-supplied bin only.** This closes a real hit against `decision:no-foreclosure-is-testable`,
which says a design that can only satisfy expressibility by rewriting the record later has
**not** satisfied it. D bundles all five agent-supplied fields into one `core-assertion`
whose statement is "this episode occurred as described above." So if a reviewer later disputes
only the `impact-cost` claim while accepting `observed-behavior`, D has nowhere to put that:
it must either mutate the bundled statement or bolt on a duplicate assertion block — which is
exactly the later-rewrite pattern the pre-ruling calls a FAIL. B's worked example demonstrates
the target behaviour concretely: `a3` (observed-behavior) stays `active` while `a4`
(impact-cost) independently goes `disputed`, same episode, no rewrite.

The synthesis this produces is, I think, the panel's most valuable output and something my
first pass missed: **the partition itself tells you which bin needs assertion machinery.**
Agent-supplied claims are the ones that get disputed, so they need individually addressable
standing. Mechanical facts are not disputed, so they stay flat `- key: value` lines and pay
none of B's ceremony. That resolves the ceremony-versus-non-foreclosure tension the panel
exposed, rather than trading one off against the other.

**Recommended against, explicitly:**

- **C's `INDEX.md` projection.** It reintroduces shared-file contention (§4), and adds a
  staleness class we would then have to build fixtures for. D's sizing analysis — episodes
  captured at spine-step granularity, plausibly 1–5 per dispatch, so hundreds-to-low-thousands
  of files after years — shows a full-directory grep is sub-second for far longer than this
  design horizon. An index is unearned. This is the same posture as the Markdown-over-Neo4j
  ruling: no machinery until observed pressure earns it.
- **B's blanket assertion-shaping of mechanical facts**, for the ceremony and default-strength
  reasons in §4. B's *idea* survives where it matters — D's `## core-assertion`,
  `## suspected-cause`, `## proposed-remedy` blocks each carry the full Stratum A field set.
- **A's dropping of the validated delta writer**, because graft 1 depends on having one.

## 7. The sharpest sub-question inside this float

The panel genuinely split on one thing I do **not** think I should settle, and it is the part
of this float most worth Tommy's attention:

> **When an episode retires, does the file move, or does a field change?**

- **A moves it** (`active/` → `retired/`). "Ordinary search" then means globbing `active/`,
  which is very hard to get wrong — the default is correct by construction.
- **D changes a field** and filters negatively. The file path stays stable forever.

**My lean has FLIPPED to A after the cold critic, and I want to be explicit that it flipped.**

I originally leaned D on the grounds that a stable path means a reference to an episode never
breaks when it retires, which #308's companion exercise depends on. **That reason was wrong.**
No candidate — D included — cross-references episodes by path. All four reference by *id*
(`superseded-by`, `corroborated-by`, `consolidated-into`), resolved to a path at read time.
A's own design already specifies the resolution: check `active/<id>.md`, fall back to
`retired/<id>.md`. That is a two-glob lookup, not a broken reference. I weighed a cost of A
that largely does not exist.

Meanwhile A's advantage is stronger than I credited. "Which set is this episode in" is a
**filesystem fact** under A, and a **content-parsing fact** under D. Every silent-failure mode
in graft 4 — injected text, malformed file, case drift, enum-prefix collision — is a
content-parsing failure, and A is structurally immune to all of them rather than defended
against them by validation. When the failure mode is *silent* (an active episode vanishing
from the candidate set with no error), structural immunity beats a validated defense, because
a validated defense fails open the moment someone hand-edits a file or a future writer path
skips the validator.

So: **A's retirement mechanism, on D's record shape.** I am stating this as a flipped
recommendation rather than a settled call — per `decision:convergence-is-human` the choice is
Tommy's, and he should know it moved under scrutiny and why.

## 8. Untaken roads (loud, per the brief)

- **A fifth constraint, `human-narrative-first`** — design the store to be read top-to-bottom
  by a human like `LESSONS.md` is. Not run. Reason: the spec assigns rhyme-detection to a
  downstream LLM sensor and keeps `LESSONS.md` alive for the human-playbook job, so
  optimizing episodes for linear human reading would trade away the store's actual purpose.
  Named here because **both A and D independently flagged loss of human narrative readability
  as their own worst cost** — so the road is untaken, not unnoticed, and if Tommy weights
  human readability higher than I have, this is the constraint that would have argued for him.
- **A `git`-history-as-the-log candidate** — use git itself as the append-only mechanism
  rather than file content. Not run. Reason: git history is not deterministically queryable
  at the granularity the store needs, which would put it in tension with the B0.1 ruling that
  every transformation between canon and an agent's surface be deterministic and attributable.
  C's brief pre-empted this explicitly.

## 9. Panel-vs-single record

**Panel (N=4), and it paid for itself.** The unanimous six in §1 are only knowable *because*
four independent constraints converged on them — a single pass would have produced the same
six as unargued assumptions rather than as findings. The scaling choice is surfaced here for
the Admiral and Tommy to overturn if they disagree.

## 10. Manifest obligation — resolved, no float needed

My `context` field places one obligation on #300's projection manifest: for a given run, an
enumerable set of `(loaded-artifact-id, canonical-revision)` pairs, addressable as
`<ref>@<revision>`. **A and D both independently concluded this requires no shape change to
#300** — any content-addressable artifact under git satisfies it by pinning to its own blob
hash at capture time. I am therefore *not* floating a manifest change.

The one conditional: if #300 lands as something that is not revision-pinnable (a
live-mutating index with no historical snapshot), that becomes a real conflict and a float at
that point. I will re-check against #300's merged shape before closing this issue.
