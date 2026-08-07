# x10 result — storage design-it-twice: synthesis and recommendation

Three independent designs, same brief, one distinct constraint each. Full designs: `x10-candidate-1.md` (diff-ergonomics-first), `x10-candidate-2.md` (rename-survival-first), `x10-candidate-3.md` (minimal-machinery-first). Orchestrator synthesis below; **the pick is the human's.**

## Where the candidates agree (unanimous, therefore probably right)

All three, independently:
- **Dropped positions from the committed store.** Line/col is the churn that poisons every diff (C1 measured it: a 3-line edit rewrites ~450 position-bearing lines; 87% of a file's statements sit below a typical edit point). Positions live in a gitignored, seconds-to-rebuild cache. The x11 line-base defect (0- vs 1-based, undeclared) lands on the cache schema, not the store.
- **Stored facts, not occurrences** — with C2 and C3 keeping the count (`n`) so x4's validated call-frequency signal survives in git; C1 dropped counts entirely (its one clear mistake — it moves a *validated measurement* onto the disposable side).
- **Mirrored something stable in the path** and made a pure file-move cost ~zero content diff (C1/C3 via module-relative ids inside source-mirrored trees + git rename detection; C2 via serial-addressed bundles).
- **Did not store the tag→edge vocabulary** (x9's kind-lookup holds in all three).

## The real fork: what deserves identity machinery

- **C2's answer: everything.** Birth-name hash serials, a sharded ledger with relative names, a 5-rung matching cascade, gray-band human rulings, alias tables. The payoff is real: file move + method rename = a **2-line identity diff, zero statement churn, zero re-mints**, and docent permalinks that survive every refactor. The bill is real too, and C2 itemized it honestly: **the store is unreadable without the ledger** (its loss is catastrophic, not degrading); a PR reviewer **cannot audit the diff independently** (`{"p":"calls","o":"n930d775b0b"}`); a rung-4 false positive **silently fuses two entities' histories**; and identity survival degrades silently if the crawl cadence slips.
- **C3's answer: only what someone authored.** Structural ids are symbol paths — disposable by design, because the structural layer regenerates in 2.3s and *the interpreter already forced the developer to propagate the rename through the code*, so store churn is bounded by churn the PR already contains. The only content worth protecting — authored concept prose — already carries its own identity via x9's `[stable-id]`, which C3 correctly names "a free, author-supplied allocator." The residue (external references into the store) is a one-line human ruling appended to a redirect table at the supersession report, measured volume ~1 batch per rename PR.
- **C1's answer: the same as C3, but it spends the substrate's JSON-lines verdict** to buy grouped plain-text files a reviewer can skim, and pays a custom merge driver and format converters for it.

## Scenario scorecard

| | C1 diff-ergo | C2 rename-surv | C3 minimal |
|---|---|---|---|
| 3-line edit → store diff | 12 lines, legible | 9 lines + new bundles, **objects unreadable without ledger** | **6 lines, legible** |
| File move alone | git renames, 0 content diff | 2 ledger lines | git renames, **0 content diff** |
| Move + method rename | 2 in-file lines + **up to 262 inbound lines/46 files** (worst case measured) | **2 identity lines, 0 statements** | 22 adjacent lines + 7 one-line importer diffs + 1 ruling line |
| Reformat/reorder source | reorder = full-file diff (declaration-order sort) | 0 | **0** (sorted lines) |
| Tag reworded | re-mints visibly, adjacent diff; `[stable-id]` immune | serial survives (ordinal preimage) | `[stable-id]` immune; slug re-mint visible + report nags to add id |
| Deleted anchor (tombstone) | not addressed | absent-state serials keep it resolvable | **orphan gate at supersession report = exactly the ruled tombstone design** |
| Store survives its own index dying | yes (no index) | **no — ledger loss = total loss** | yes (redirect table is convenience, not load-bearing) |
| Audit independence in a PR | **best** | worst | good |
| Verdict compliance | breaks JSON-lines | breaks readable-store; honors opaque-identity | honors JSON-lines; narrows opaque-identity to the authored layer |
| Machinery to build & own | format converters, merge driver | cascade, ledger, shards, aliases, PENDING flow | supersession report + pairing heuristic + one flat rulings file |

## Recommendation (agent's, for the human to accept, adapt, or reject)

**C3 as the base, with three grafts, none from C2's core:**

1. **C3 wholesale**: source-mirrored `derived/` tree, two files per source file (`.py.jsonl` facts with counts, `.py.md` prose with the `##`/`### Tag [id]` heading grammar), symbol-path ids relative within their file, no allocator, `rulings.jsonl` as the only hand-authored file, supersession report with the cheap fact-multiset pairing heuristic, orphan gate for tombstones.
2. **Graft (C2): commit the run report.** C2's `RUN.md` — the name-resolved, human-readable summary of what a crawl changed (minted/renamed/pending + fact deltas) — is the best artifact any candidate produced for the *reviewer*; C3 only prints it. Commit it per run.
3. **Graft (C3's own named guards, built first):** the empty-diff determinism assertion (rebuild with no source change → `git diff --exit-code`), the mis-pairing guard on auto-supersession, and fixing the C++ colon collision in the relative-id rule *now* (cheap now, expensive after adoption).
4. **Untaken roads, named:** C2's full identity machinery (revive if external citation of structural ids ever becomes load-bearing — e.g., cross-project federation or long-lived agent caches; its §8 is the honest catalog of what it costs); C1's grouped plain-text format (revive if JSONL proves unskimmable in real review — it spends a substrate verdict to buy readability, which is the human's call, not ours).

**Why this way:** the fork's deep question is *what deserves identity machinery*, and the whole run's evidence points one way — derivation is cheap (2.3s), the authored layer already self-identifies through the grammar, rename churn is bounded by the source churn the PR already contains, and every piece of C2's machinery exists to protect content that costs nothing to regenerate, at the price of a store that can die of ledger loss and diffs no reviewer can independently audit. C3 also lands the tombstone ruling and the x9 confidence rule *for free* — its orphan gate and `~`-slug marker are the ruled designs, already in the layout.

**What this does NOT settle:** the statement-vocabulary extensions x11 measured (values, kinds, signatures, docstring bodies, spans, decorators, extraction-window) — those are additive line-schema work on top of whichever layout wins; and scale beyond ~10× (C3's own named ceiling, with a graceful degradation named).
