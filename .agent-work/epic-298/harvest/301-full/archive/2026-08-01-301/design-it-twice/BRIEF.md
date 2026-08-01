# Design-it-twice Brief: `episode record + durable store (issue #301)`

Run N=4 agents in parallel, each producing ONE candidate under **one named distinct
constraint**, then converge to a single recommendation. Convergence is NOT yours — the
Commander composes the comparison and floats it to the Admiral, who surfaces it to Tommy.

## The one thing being designed twice

**The episode record interface and its on-disk store shape**: what fields an episode
carries, how they are partitioned, how a record is written and read, how it is retired,
and how it is found — as Markdown in git.

This is ONE decision. Retrieval, retirement, and partition are facets of the record's
interface, not separate briefs: a candidate that changes the record shape changes all
three, which is exactly why they are compared together.

## Count and panel

**N=4, panel.** Rationale: this is one of epic #298's two load-bearing interfaces, the
first accumulating store the design builds, and a spec-mandated design-it-twice. "When in
doubt, panel." Four constraints give real contrast across the axis that actually matters
here — how much structure the record commits to up front.

## Hard constraints — true for EVERY candidate, not negotiable

These are ruled by the confirmed spec and the Admiral's launch order. A candidate that
violates one is void, not interesting.

1. **Markdown in git.** No database, no query language, no backend, no index server.
   "Queryable" means *findable by deterministic means over Markdown in git*. Tommy's
   explicit direction, superseding an earlier exploration finding that favoured Neo4j:
   *"Markdown is sufficient until observed pressure earns a backend."*
2. **The partition is explicit.** Two field groups, visibly separated in the record itself
   — not merely implied by field naming:
   - **Mechanically captured** (from engine/harness state, zero agent effort): run/project,
     role and active spine step, context manifest (what was loaded, at which revision),
     refusals, reopens, rework counts, failed commands, artifact references.
   - **Agent-supplied** (kept deliberately *small* — agent effort is a real cost): task
     intent, expected behavior, observed behavior, impact/cost, workaround.
   - **Suspected cause** and **proposed remedy** are SEPARATE, OPTIONAL assertions — not
     ordinary fields of either group. An episode with no diagnosis is complete and valid.
3. **Non-foreclosure under Stratum A.** The record must remain expressible as assertions
   under this truth model, WITHOUT a later rewrite:
   > All truth claims use the same mechanics: an identified assertion with source,
   > supporting and challenging evidence, and a qualitative weak/medium/strong assessment
   > that allocates trust-but-verify attention and creates no inertia against decisive new
   > evidence. Belief strength and lifecycle standing (disputed, superseded, rejected)
   > remain separate dimensions.
   Your candidate MUST include a concrete field-by-field mapping showing how an episode
   becomes (identified assertion, source, supporting/challenging evidence, qualitative
   strength) with lifecycle standing as a *separate* dimension. "It could be mapped later"
   is a FAIL. Show the mapping.
4. **Durability past consolidation.** The current lessons inbox evaporates a lesson when it
   graduates. The episode must OUTLIVE its consolidation so rhymes stay findable across
   runs. **Retired means excluded from ordinary rhyme-search, RETAINED in history.**
   Retirement is never deletion.
5. **Deterministic mechanics only.** Governing principle B0.1, the stochastic boundary:
   stochastic work happens *upstream of canon*; between canonical truth and an agent's
   active surface every transformation is **deterministic and attributable**. Finding that
   two episodes *rhyme* is a sensor (LLM) job, owned downstream. **The store that makes
   rhymes findable is mechanical.** Your store never guesses, never ranks by similarity,
   never embeds. It exposes stable ids, enumerable fields, and exact/set-membership
   retrieval that a stochastic sensor can work *on top of*.
6. **Do not touch the live lessons machinery.** `.agent-work/LESSONS.md` and
   `scripts/apply_lessons_delta.py` stay operative and unmodified. You are building a NEW
   store alongside them. Cutover is ruled downstream at issue #308, not by you.
7. **Out of scope, hard:** automated capture wiring (issue #305), consolidation and the
   rhyme-search loop (issue #308), and the projection manifest (issue #300, running
   concurrently in another worktree — you may DEPEND on it, you may not DESIGN it).

## Prior art you must read before designing

`C:/Programs/constellation-skills-wt/298-301/scripts/apply_lessons_delta.py` (699 lines) and
the live playbook at `C:/Programs/constellation-skills/.agent-work/LESSONS.md` (read-only).

This is the direct neighbour and the house pattern:
- Markdown records under `### lesson:<slug>` headings, `- field: value` lines, append-only
  `- history: ...` entries.
- A `<!-- playbook-state: ... -->` HTML-comment header carrying machine state.
- **All mutation goes through a validated, all-or-nothing JSON delta script. The LLM never
  writes the store directly.** Any invalid op rejects the whole delta.
- Counters, caps, dormancy, and an explicit `retire` op that requires a reason.

Rhyme with this where it earns its keep; depart from it where your named constraint
demands, and **say so explicitly** when you depart.

## The manifest obligation (issue #300, do not design)

Your record's **context** field consumes #300's projection manifest. Do not design the
manifest. State the obligation your field places on it: for a given run, an enumerable set
of `(loaded-artifact-id, canonical-revision)` pairs. Store it as a reference plus the
revision it resolved at. If you believe the manifest must change SHAPE to serve you, say so
loudly — that is a float to the Admiral, not something you resolve.

## Compared on (score your own candidate honestly on each)

- **Depth** — does it hide the right complexity behind the seam, or leak it upward?
- **Locality** — is the change contained, or does it fan out?
- **Seam placement** — is the boundary where the caller and the tests actually want it?
- **Testability** — can each pathway be exercised and falsified on its own? Specifically:
  can you write an **adversarial fixture** that makes a naive implementation return a WRONG
  answer (false FAIL on a valid record, silent PASS on an invalid one)?

## Also required of every candidate

- **The acceptance exercise**: "a seeded episode is retrievable across sessions" must be
  exercisable against your design. Say concretely how, including what constitutes an honest
  session boundary (a NEW process that shares nothing but the git working tree).
- **The harder downstream companion** (owned at #308, but your design must not preclude it):
  seed episodes across several runs, consolidate one cluster, and confirm that rhymes
  involving the *neighbours* of consolidated episodes are still findable.
- **Honest sizing.** If your constraint drives you to a store far smaller than the issue
  implies, SAY SO PLAINLY. A measured "this needs less than you think" is a complete,
  successful result, not a shortfall. State what you tested and what you did not.

## Output — a candidate, not a menu

Write ONE candidate. Be opinionated inside your constraint. Do not hedge across
alternatives; that is what the other three agents are for.
