# Problem statement — issue #301, episode record and durable store

Reconciled against the frozen `LAUNCH_ORDER-301.md` (delegated mode; no reachable human).
Source of truth for every settled question below is that order, not a re-derivation.

## The ask, in one line

Build the **mechanical half** of an episode memory: a durable, deterministically-findable
store of structured observation records that outlives consolidation, partitioned into
mechanically-captured and agent-supplied fields, retired by explicit policy, and shaped so
the Stratum A assertion model can later be built *over* it rather than *alongside* it.

## What is settled (cite, do not re-litigate)

| Question | Ruling | Source |
|---|---|---|
| Storage medium | Markdown in git. No DB, no query language, no backend. | Pre-Rulings, `decision:markdown-in-git` |
| What "queryable" means | Findable by deterministic means over Markdown in git | same |
| Design-it-twice | REQUIRED, 3+ parallel candidates, one named constraint each | `decision:design-it-twice-required` |
| Who converges | Not me. Float comparison + recommendation to the Admiral | `decision:convergence-is-human` |
| Existing LESSONS.md | Stays live. No migration, no disable, no rewrite. Cutover ruled at #308 | `decision:lessons-inbox-keeps-running` |
| Review class | Full cold panel, no light single-reviewer pass | `decision:full-cold-panel` |
| Non-foreclosure | An acceptance obligation, shown concretely, not a hope | `decision:no-foreclosure-is-testable` |
| Cross-session retrieval | Exercised across a real session boundary, not asserted | `decision:cross-session-retrieval-is-the-acceptance-test` |

## Scope fence

**In:** the episode record schema; the durable Markdown-in-git store; deterministic
retrieval; the mechanical/agent-supplied partition; the retirement policy; the Stratum A
expressibility mapping; tests including adversarial fixtures.

**Out:** automated capture wiring (issue #305); consolidation and the rhyme-search loop
(issue #308); the projection manifest (issue #300 — I consume its obligation, I do not
design it); any edit to the live `.agent-work/LESSONS.md` machinery.

## The obligation I place on #300's manifest

My episode record carries a **context** field. Per the pasted B1 spec it must record
*what was loaded, at which revision*. I do not design the manifest. I define the obligation:
the manifest must expose, for a given run, an enumerable set of `(loaded-artifact-id,
canonical-revision)` pairs. My record stores that as an opaque-to-me reference plus the
revision it was resolved at. If #300's shape cannot satisfy that, it is a **float**, not a
cross-edit.

## Baseline verified against code (lesson:verify-launch-order-claims-against-code)

- `grep -ril "episode"` across `*.py`/`*.md`/`*.json` — **zero hits**. Nothing shipped.
- `grep -ril "stratum\|rhyme"` — **zero hits**. The truth model exists only as spec text.
- `scripts/apply_lessons_delta.py` (699 lines) is the direct neighbour and **stays untouched**.
  Its shape is the prior art to rhyme with: `### lesson:<slug>` headings, `- field: value`
  lines, append-only `- history:` entries, all mutation through a validated all-or-nothing
  JSON delta so the LLM never writes the store directly.

**Conclusion: the mission premise holds.** This is a genuine build, not an honest-null.

## The one genuinely-new tension I must design against

The store must be **deterministically findable** (B0.1: between canonical truth and an
agent's active surface every transformation is deterministic and attributable) while the
thing that makes episodes *useful* — noticing that two episodes rhyme — is explicitly a
stochastic sensor job owned downstream. So the store must expose enough **mechanical**
surface (stable ids, enumerable fields, exact-match and set-membership retrieval) that a
sensor can do its stochastic work *on top* without the store itself ever guessing.

## Protected intent

The episode record is one of the epic's two load-bearing interfaces. What must survive
contact with implementation, in priority order:

1. **Non-foreclosure.** An episode must be expressible as assertions under Stratum A
   *without rewriting the record later*.
2. **Durability past consolidation.** Retired never means deleted; rhymes stay findable.
3. **The partition is explicit and documented**, not implicit in field names.
4. **The agent-supplied half stays deliberately small** — effort is a real cost.
