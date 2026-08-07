# UI branch

**Question this branch answers:** *"what should this look like?"* — layout, visual hierarchy, which arrangement reads best.

## Shape

**3–5 structurally different variants on one route.** Not five shades of the same layout — genuinely different structures: sidebar vs. top-nav, table vs. cards, single-column vs. split. If two variants differ only in spacing or color, they are one variant; cut one and add a real alternative. The point is to make the structural choice visible, and near-identical variants hide it.

- **`?variant=` switcher.** One route, the variant chosen by a query param (`?variant=2`). No rebuild to compare.
- **Floating cycle bar.** A small fixed control that cycles through the variants, so the human flips between them in place and feels the difference.
- **Hidden in production.** The route is gated off from real users — a prototype, not a feature.

## Mount inside a real page

**Strongly prefer mounting the variants inside a real, existing, populated page** rather than a fresh empty route. An empty route hides the design problems a populated one exposes: real content lengths, real edge cases, the row that wraps to three lines, the empty state, the too-long title. A variant that looks clean on lorem ipsum and falls apart on real data has failed to answer the question — and you only learn that on a real page.

## Rules

- **One command to run**, stated in the result. The human opens it and cycles.
- **No tests, no persistence, no polish** beyond what makes the structural difference legible.
- The verdict is the human's eye, not a metric — if the question is really "is this measurably faster to scan," that is a **measurement** prototype, not this one.

## Closeout

**Fold the winner, delete the losers.** The winning variant's structure is the answer; it gets absorbed into the real page (record the commit ref). The losing variants are deleted — they were scoped negative results, and their reasons belong in the result, not in the codebase.

## Scoped verdict

Name what the comparison covered. A layout that won on the populated desktop page has been tested *there*; call mobile widths, empty states, or accessibility **NOT tested** if you didn't put them under the variants. The default next move after an inconclusive round is another structural variant, not "none of these work."
