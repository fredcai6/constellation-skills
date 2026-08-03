# Problem statement — issue #308

Reconciled against `LAUNCH_ORDER-308.md` (delegated mode; no reachable human). Base
revision `4cec87a`.

## Protected intent

Two halves, coupled through one artifact family (`docs/agents/`).

**Half 1 — exercise collation end to end.** Rhyme-search the accumulated episode store,
select ONE cluster, route it through the two-bin rule, land ONE consolidation. **The
routing decision is the reviewable evidence, more than the change itself.** Source episodes
marked consolidated per retirement policy.

**Half 2 — retire the playbook.** `.agent-work/LESSONS.md` is a dead end between an
episodic accumulator and actual doctrine updates. Consolidation lands in `docs/agents/`;
the 20-entry cap goes; every active lesson gets a terminal disposition; live agents stop
reading lessons; #322 folds in.

## Rhyme-search result — NOT a null

Candidate set obtained mechanically from the store's own seam, never by recollection:

```
$ python scripts/query_episodes.py enumerate
"count": 7, ids: issue-304-g3-001..005, issue-309-001, issue-309-002    (exit 0)
```

An **independent cold sensor** (fresh context, opus, given the 7 files and NO hypothesis,
and explicitly authorised to return "no cluster") was run before I recorded my own read, so
convergence here is not inheritance — cf. `lesson:a-panel-inherits-what-it-was-not-told-to-vary`,
which is precisely the trap of reading agreement as evidence when it is transmission.

It returned two STRONG groups and one WEAK.

### Cluster A (SELECTED) — 3 members, 2 runs, 2 roles

**Shared failure mode:** a written, secondhand claim about current repo state was taken as a
premise, was wrong, and only re-deriving it by command caught it.

| member | run | role | the quote that puts it in the group |
|---|---|---|---|
| `issue-304-g3-001` | issue-304-g3 | implementer | d2: *"grep the deleted phrases corpus-wide … instead of trusting a handoff's suite list"* |
| `issue-304-g3-003` | issue-304-g3 | implementer | a5: *"Answer 'was this already done?' with a command over git history rather than a reading of the current file"* |
| `issue-309-002` | issue-309 | commander | a3: *"EPISODE_STORE.md section 1's own claim … is now stale, and the plan's first draft inherited the same false premise"* |

Sensor's own honest caveat, retained rather than smoothed over: 001 is *under-inclusive
enumeration* while 003 and 309-002 are *stale specific claims*. Grouped because one
instruction covers all three, not because the mechanisms are identical.

### Cluster B (NOT selected this run) — 2 members, 2 runs

**Shared failure mode:** a check reports without being able to register the outcome it is
credited with detecting; in both cases operated by the party whose work it measured.
Members `issue-304-g3-005` (*"can verify that orientation HAPPENED but can never verify
that it happened FIRST"*) and `issue-309-001` (*"a null is not a demonstration"*).

I did not identify this cluster; the cold sensor did. Recording that, because it is
evidence about the pathway: a solo read missed a STRONG cluster that a second independent
read found.

### Why A and not B

`decision:one-consolidation-not-many` — exactly one. A wins on: 3 members vs 2; two roles
vs one; and decisively, **A's consolidation and Half 2's disposition of the bank's
most-confirmed lesson are the same act.** `lesson:verify-launch-order-claims-against-code`
(mentions 9, confirmed 6, last-confirmed 1 run ago — the strongest entry in the bank)
states cluster A's pattern for one role. Consolidating A *is* graduating that lesson. Half 1
and Half 2 become one motion, which is exactly what "the playbook is a dead end between an
accumulator and actual doctrine updates" predicts should happen.

### The finding the epic should hear

**Both STRONG clusters independently rediscovered patterns the lessons bank already holds**
— A ↔ `verify-launch-order-claims-against-code`, B ↔
`a-check-that-cannot-fail-is-indistinguishable-from-one-that-passed`. The store's
rhyme-search, running on 7 episodes from 2 runs with no access to `LESSONS.md`, found what
the playbook found by a different route. That is convergent validity for the collation
mechanism and it is the strongest single piece of evidence this issue produces that the
store can carry what the playbook was carrying.

Scoped honestly: this is 2 clusters from 7 episodes in one store at one moment. It says the
pathway *works here*; it does not establish a rate.

## Singletons (real findings, no partner in this set)

- `issue-304-g3-004` — guard a deletion in both directions; put the invariant in the editing
  tool as a refusal, not only in the test. Clear singleton.
- `issue-304-g3-002` — near-singleton; its outcome is a clean null.

## The routing question — Tommy's, not mine

Cluster A routes to one of two bins under `#302` (*"Machinize the mechanizable. We don't
need stochastic reasoning for predictable logic… these are aspirations"*). Both are live;
neither is recommended into inevitability. Argued in full in `ROUTING_QUESTION.md`.

## Open scope question floated to the Admiral

Mission item 2 keeps `apply_lessons_delta.py` (drop its cap) while item 4 cuts live-agent
reads. That leaves the writer alive and every reader gone. Whether the Commander `feedback`
step should keep *writing* lessons is not settled by the order. Proceeding on the reading
that this is a **cutover, not a demolition**: the writer survives, uncapped, as staging the
curator drains; ripping out the writer is out of scope. Named, not assumed silently.
