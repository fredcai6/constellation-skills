# Mission frame — issue #308

**Map status: DEGRADED-NO-MAP, discharged.** This repo has no `docs/architecture/` packet
map, no `map.json`, no decision-anchor overlay — permanently, not transiently: it is a
skill-source repo. Receipt: `.agent-work/issue-308/map-orientation.json`. Every anchor cited
below is one of the substitutes hash-pinned into that receipt at the context step, declared
before any source read.

## Intent

Prove the collation loop end to end by landing exactly **one** consolidation out of the
accumulated episode store, and retire `.agent-work/LESSONS.md` as a live-agent input — the
dead middle between an episodic accumulator (`episodes/`) and actual doctrine updates
(`docs/agents/`).

## Structural anchors (all hash-pinned substitutes)

| anchor | role in this run |
|---|---|
| `docs/EPISODE_STORE.md` | the store's contract. **Also an edit target** — §1 carries the stale transcript (#348), which is itself a live instance of the cluster being consolidated. |
| `episodes/README.md` | the `active/` vs `retired/` layout; retirement moves the file. |
| `docs/agents/ORCHESTRATOR_CONTEXT.md` | the repo's ONLY `docs/agents/` file; the consolidation destination's existing half. |
| `docs/CONSTELLATION_OVERVIEW.md` | truth-layer taxonomy — the #322 edit target. |
| `.agent-work/LESSONS.md` | the artifact being retired; 20 active entries at cap 20. |

## Affected capabilities

- the episode store's retirement write path (`apply_episode_delta.py` retire op)
- the lessons writer's cap enforcement (`apply_lessons_delta.py`)
- live-agent context intake (Commander spine, launch-order template, Admiral doctrine,
  Charter agent guide)
- the corpus's own truth-layer description

## Governing constraints and decisions

**These are LAUNCH-ORDER PRE-RULINGS, not map decision anchors.** Stated that way
deliberately: this repo has no map, so it has no decision-anchor inventory, and citing
these in map-anchor syntax would claim a provenance they do not have. Their authority is
the frozen launch order (and behind it, Tommy), not a map packet. Named by their
launch-order slug, with the `decision:` prefix omitted for exactly that reason.

| launch-order pre-ruling | grade | effect on this plan |
|---|---|---|
| destination-is-docs-agents | settled/human | consolidation lands in `docs/agents/`, never `LESSONS.md` |
| retirement-moves-the-file | settled/human | retiring an episode MOVES it; no in-place annotation |
| no-cap-replacement-by-hygiene | settled/human | cap goes; curator hygiene replaces it; **no substitute numeric cap** |
| tier-must-be-justified | settled/human | every graduation names its tier; broader-than-audience is a defect |
| one-consolidation-not-many | settled/inherited | exactly ONE consolidation this run |
| #302 two-bin ruling | settled/human | no third bin; routing is Tommy's |

## Decision pressure

**The two-bin routing on cluster A is unresolved and is Tommy's** (`ROUTING_QUESTION.md`,
both bins argued). Gate g6 is authored but **blocked** on that ruling. Everything else in
this plan is independent of it and proceeds now — that independence is deliberate, so a
ruling that arrives late costs nothing and a ruling that never arrives still leaves Half 2
complete.

## Claims / evidence surfaces

- **Measured, reproduced:** cap binds at 20/20 (`add` exits 1); 10/20 never confirmed;
  12/20 stale ≥4 runs. Live file sha256-identical before/after the probe.
- **Verified against the tree:** `.agent-work/` is NOT gitignored (exit 1, 1958 tracked) —
  so `EPISODE_STORE.md` §1 is false at HEAD.
- **To be verified by reading back, not by having written:** episodes actually moved to
  `retired/`; lessons actually gone from Active. Compared by **blob OID or normalized
  content**, never raw working-tree bytes (#319: `* text=auto` makes CRLF legitimate).

## Map confidence / staleness / disputes

No map exists, so there is nothing to be stale — but the **substitutes are demonstrably
stale**, which is the sharper risk and the reason this frame names it: `EPISODE_STORE.md` §1
is provably wrong at HEAD (#348), and `CONSTELLATION_OVERVIEW.md`'s taxonomy is incomplete
(#322). Two of my five anchors are known-defective, and **both are in-scope edit targets
rather than trusted context.** No gate in this plan assumes either is accurate.

## Out of scope

- changing the episode store's schema or standings (#301/#342 territory)
- ripping out `apply_lessons_delta.py` (cutover, not demolition — floated, proceeding)
- consolidating cluster B (filed as **#392**)
- the not-chosen bin (to be filed once Tommy rules)
