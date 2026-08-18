# Architecture reconcile — epic #567, "the door is the interface" (closeout)

**Verdict: evidenced honest null.** There is no `docs/architecture` packet map in this repo, no
curated overlay, and no minted anchor anywhere in the source tree. The epic's net change —
one agent-facing path to the engine (the MCP door) where there were two — has nothing to
reconcile *against* at the packet/overlay/decision level, because that level does not exist yet.
This is a complete, evidenced result, not a skipped step.

All measurements below are pinned to `origin/main` at `148ae62e` (the commit named in the
handoff, confirmed as current `HEAD` for this run).

## 1. What map truth currently exists

**`docs/architecture/` — untracked, empty.**

```
$ git status --porcelain docs/architecture
?? docs/architecture/

$ find docs/architecture -maxdepth 3
docs/architecture
docs/architecture/generated
docs/architecture/generated/map.json

$ cat docs/architecture/generated/map.json
{"findings": [], "nodes": [], "relationships": [], "version": 1}
```

No `packets/`, `overlays/`, `decisions/`, or `index.md` exist under `docs/architecture` — not
stale, not partially built, simply never created. There is no touched node packet to reconcile
for any of the epic's nine lanes, because no packet has ever existed for any node in this repo.

**`map/INDEX.md` — generated, scan-only, Admiral-owned, and currently fresh.**

```
$ wc -c map/INDEX.md
31150 map/INDEX.md
$ find map -maxdepth 1 -mindepth 1 -type d | wc -l
167
```

This is a source-scan render (`scripts/code_map/render.py`), not a curated packet set — it
reflects current structure by construction whenever it is regenerated, and the Admiral already
regenerated it on merged `main` per #544. There is nothing for a packet-reconcile step to do to
a generated artifact; the map-model's packet doctrine governs *curated* `docs/architecture/`
content, which this repo does not have. Per the brief's hard constraint, it is not touched here.

**`map/ids.jsonl` — 0 bytes, and independently confirmed why.**

The brief states rebuilding does not change this. I verified the mechanism directly rather than
taking the claim on trust: `render.py:728` writes `ids.jsonl` from the `ids` dict, which is
populated *only* by `extract.py`'s `anchor()` method (line ~873) emitting an `"anchored"`
statement — and an anchor is minted only when a human or agent writes a `[slug]` comment
directly above a definition (`anchors_in()`, `extract.py:138`, "ids are minted ON DEMAND").

```
$ python3 -c "
import json
total = anchored = 0
with open('.code-map/statements.jsonl') as f:
    for line in f:
        total += 1
        if json.loads(line).get('p') == 'anchored':
            anchored += 1
print(total, anchored)
"
167950 0
```

Zero of 167,950 extracted statements carry the `anchored` predicate. This is not a rendering
bug and not drift — it is the direct, correct consequence of no one having ever authored a
`[slug]` anchor comment anywhere in this codebase. `map/ids.jsonl` being empty is map truth, not
a defect in the map.

## 2. What "reconcile" can mean here, stated plainly

A packet reconcile compares curated map content against current code and updates status,
confidence, dependencies, or rationale where they've drifted. That requires a packet to compare
against. With zero packets, zero overlays, and zero anchors, there is no comparison to run —
not "the comparison came back clean," but "the comparison has no second operand." Declaring the
epic's net change reconciled against a map that has never had any curated content would be
ceremony: it would assert a check ran that structurally could not discriminate a healthy state
from a broken one, because both states look identical (empty) either way.

This matches the pattern independently reached at lane scope, twice, earlier in this same epic:
`.agent-work/567-d1/RECONCILE.md` (`map_orient` → `DEGRADED-UNPARSEABLE`, folded the lane's
change into `specs/*.spine.toml` and `tests/test_mcp_adoption.py` instead — the nearest thing
this repo has to a structural record) and
`.agent-work/archive/2026-08-16-epic-567-door-cmdr-b/RECONCILE.md` (same finding, reasoned
no-op). Both lane-scoped reconciles already folded their own changes into the structural records
that actually exist and that they owned; nothing found here reopens or contradicts either. At
epic scope there is no additional structural record — beyond what those two lanes already
covered — for the closeout reconcile to fold into.

**The honest conclusion: nothing to reconcile against exists, evidenced above, and that is a
complete answer** — per the brief, preferred to inventing ceremony to fill the gate.

## 3. Anchor-minting recommendation — size and shape (not a plan, not the work)

This is a recommendation for the human to commission, not work performed here.

**What it would take mechanically:** an anchor is a `[slug]` comment line written directly
above a definition, one at a time, by whoever decides that definition is worth a durable,
citable id. Nothing auto-generates it — the "on demand" design in `extract.py` is deliberate
("most definitions never get one, and that is the point"). So minting anchors is a **curation
pass**, not a mechanical script run: for each definition, a person or agent judges whether it
is worth citing durably, and only then writes the slug.

**Size of the candidate population, measured directly from the code-map statement store, this
commit:**

```
$ python3 -c "
import json
from collections import Counter
kinds = Counter()
with open('.code-map/statements.jsonl') as f:
    for line in f:
        st = json.loads(line)
        if st.get('p') == 'contains':
            kinds[st['d'].get('kind')] += 1
for k, c in kinds.most_common():
    print(k, c)
print('total', sum(kinds.values()))
"
method        3688
function      2044
class          717
class method    33
static method   26
property        14
total          6522
```

Across 599 tracked `.py` files (`git ls-files '*.py' | wc -l`), the code-map scanner already
identifies 6,522 addressable definitions. The scanner is Python-AST-only (`ast`-based
extraction) — anchors are a Python-source mechanism in this repo, not a corpus-wide one.

**Shape:** 6,522 is the *ceiling* of the candidate population, not the size of the task — the
doctrine is explicit that most definitions should stay unanchored. The actual task is a judgment
pass across up to ~600 files deciding *which* definitions in that population earn a durable id
(module/file and component-level nodes first, per the map-model's stated minimum level, before
descending to function-or-method), which is a different — and much smaller — shape than "write
6,522 comments." Building the packet map itself (packets, overlays, decision anchors per
`references/map-model.md`) is a further, larger, separate effort layered on top of anchor
minting, and is explicitly out of scope for this reconcile and for the recommendation itself.

## 4. Triage candidates staged

One candidate staged, not filed as an issue:
`.agent-work/567-carto/triage-candidates/tc1-commission-anchor-minting.md` — carries this
sizing forward so it is not lost, per the epic's standing ruling that new work gets paired onto
an open issue or recorded as an episode at closeout, not freshly minted.

## Spine

Driven through `mcp__spine__spine_*` (MCP door) per the handoff — no CLI fallback used or
needed at any gate.
