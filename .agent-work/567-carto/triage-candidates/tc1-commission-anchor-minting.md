# Triage candidate — commission anchor minting so `map/ids.jsonl` stops being permanently empty

**Found at:** epic #567 architecture-reconcile closeout, cartographer crew, commit `148ae62e`.

**What was found.** `map/ids.jsonl` is 0 bytes and stays 0 bytes on every rebuild — confirmed
mechanically: 0 of 167,950 statements in `.code-map/statements.jsonl` carry the `anchored`
predicate `render.py`/`extract.py` require to populate it. No one has ever written a `[slug]`
anchor comment anywhere in this codebase. `docs/architecture/` is likewise empty (untracked,
zero packets/overlays/decisions). Consequence, reported independently by two lanes this wave and
confirmed by the Admiral: every run in this repo orients `DEGRADED`, permanently, and
`verify-frame` passes only frames that cite nothing. Full evidence:
`.agent-work/567-carto/RECONCILE.md` §1, §3.

**Size, measured this commit.** Anchors are minted on demand, one `[slug]` comment per chosen
definition, Python-AST-only. The candidate population (everything the scanner can already see)
is 6,522 definitions (3,688 methods, 2,044 functions, 717 classes, 33 class methods, 26 static
methods, 14 properties) across 599 tracked `.py` files. The real task is a curation judgment
pass over that population — deciding which definitions earn a durable id, starting at
module/component level per the map-model's stated minimum — not writing all 6,522 comments.
Building the packet map itself (`docs/architecture/packets|overlays|decisions`) is a further,
larger, separate effort on top of anchor minting.

**Why it is a candidate and not a fix.** Both minting anchors and building the packet map are
explicitly out of scope for this reconcile (hard constraint in the closeout handoff) — sizing
the work is this crew's job; commissioning it is the human's call.

**Disposition:** `recommend-and-defer`. Pair onto an open issue or record as an episode at
closeout, per the epic's standing ruling against minting new tracking mid-run. Not filed as an
issue here.
