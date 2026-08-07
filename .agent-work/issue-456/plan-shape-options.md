# Two plan shapes — for the approval checkpoint

The cold critic's structural findings (F1, F3, F9, F10, F14) do not fit inside
the current gate list. They are presented here as two concrete shapes rather
than as advice, so the choice is a pick and not a redesign.

**Both shapes cover all nine issue gates.** Neither drops scope. The difference
is where the work sits.

---

## Shape A — as currently ruled: ten gates, the issue's own order

    g0  package + CLI + discovery (port)
    g1  a check stage that can fail          <- commits ALL thresholds
    g2  D2 symbol identity
    g3  referenced-by trust fix
    g4  statement-schema merge + line base
    g5  top index second tier
    g6  production vs test caller split
    g7  stale-tag detector
    g8  comment-extraction pass
    g9  BOM + D3 + practice + churn re-measure

**What it costs.** g1 commits hole counts, ASCII provenance, edge-recall floors
and the churn ratio — every one measured against rendered output. g4 then
deletes a pipeline stage, g5 restructures the index, and g6 changes every page's
referenced-by line. So g1's baselines are invalidated three times *after* being
committed, and each time the cheapest in-gate fix is to edit the baseline. A
threshold that gets edited whenever the next gate turns it red is the print-only
diagnostic this issue exists to replace.

Two further gaps stay open in this shape: no gate owns the four `skills/` files,
and no gate owns the committed `map/` tree.

**Honest reading:** this is the shape that matches the ruling most literally. It
also carries a rework loop nobody has costed, and it would ship the
one-gate-per-file rule while breaking it.

---

## Shape B — the critic's restructure: same scope, ten gates, different seams

    g0  package + CLI + discovery (port)
    g1  invariants that CANNOT move          <- nonzero exit, byte-identical
                                                rebuild, mutation-provable
                                                structural assertions only
    g2  D2 symbol identity + referenced-by trust fix   (one line of code, one gate)
    g3  statement-schema merge + line base
    g4  top index second tier
    g5  production vs test caller split
    gB  BASELINE GATE                        <- every corpus-count and
                                                render-shape threshold, measured
                                                ONCE the render has stopped
                                                moving: holes, ASCII provenance,
                                                edge recall, churn ratio
    g6  stale-tag detector
    g7  comment-extraction pass
    g8  BOM + D3
    gS  skills integration                   <- the cherry-pick, with a command

That is eleven rows for ten gates' worth of work: g2 absorbs the old g3 (the
issue itself says "ships with #2 — same line"), and the old g9's grab-bag splits
into a code gate (BOM + D3) and non-gate closeout lessons.

**What it buys.** Thresholds are committed once, after the last gate that moves
them, so no baseline is ever edited to make a later gate green. The skills files
get an owner. Each gate's close criterion is a property rather than a
conjunction across a fix, a fixture, a prose artifact and a measurement.

**What it costs.** It reorders the issue's ranked queue, which was itself
critic-ordered during the exploration. The "checks first, nothing downstream is
trustworthy until a regression can go red" principle is *weakened but not
abandoned*: g1 still lands first and still can go red — it just carries only the
assertions that survive a render change.

---

## The one question underneath both

**Does this run generate and commit a `map/` tree for constellation-skills
itself?**

- **Yes** → ~3,411 entity pages into a repo tracking ~3,441 files, roughly
  doubling it, and the tree churns wholesale at every render-changing gate. Some
  gate must own "the committed tree matches a fresh build."
- **No** → the tool ships without its own output, and the skills changes riding
  this branch instruct every crew in this repo to start from a "map entry point"
  that does not exist. That dangle needs to be stated knowingly rather than
  discovered.

This is independent of A-vs-B and is the larger call.

---

## Recommendation

**Shape B**, on one axis: it is the only shape in which g1's checks stay
falsifiable through to the end of the run. Everything else about B is
bookkeeping; that one property is the issue's stated reason for existing.

On the map tree: **generate it, and let one gate own freshness** — because the
skills integration shipping on this branch already promises it to every crew
that reads a handoff. Shipping the promise without the artifact is the worse of
the two dangles.
