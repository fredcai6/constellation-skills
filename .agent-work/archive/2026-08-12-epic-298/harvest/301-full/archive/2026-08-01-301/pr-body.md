Implements the episode record and its durable, queryable store for issue #301 (epic #298, element C).

**All four gates are complete, green, and independently reviewed.** The retirement layout was held open across g1-g3 for a human decision and has now been ruled: *"move the file, prefer to keep files clean of history unless they're historical. archives are available strats."* Gate g4 binds it.

## What ships

| Gate | Deliverable |
|---|---|
| g1 | `docs/EPISODE_STORE.md` + the store at git-tracked `episodes/` |
| g2 | `scripts/apply_episode_delta.py` — the only write path, all-or-nothing |
| g3 | `scripts/query_episodes.py` + the acceptance exercise |
| g4 | binds the ratified file-move retirement layout + retirement-dependent retrieval |

Suite on CI: **1308 passed, 2 skipped** (baseline at `b69e6c8` was 1157). Verified on Python 3.12, the version CI pins, not only on the local 3.14.

## Acceptance criteria

- **Store exists** — `episodes/`, git-tracked.
- **Partition documented** — mechanical vs agent-supplied as literal section headings, enforced at the single write path by a per-bin allowlist, not merely described.
- **Retirement policy stated** — retired means excluded from ordinary rhyme-search and **retained in history**; never deletion or truncation; a non-empty reason is required and validated.
- **A seeded episode is retrievable across sessions** — exercised, not asserted (below).

## The load-bearing correction: the store had to move

All four design candidates placed the store under `.agent-work/episodes/`. That directory is gitignored at `.gitignore:1` and has **zero** tracked files — `git ls-files .agent-work/` returns nothing, and `LESSONS.md` itself is not in git. A store there would not be "Markdown in git" and would be destroyed with the worktree, violating the one settled storage ruling.

The candidates inherited the location from `LESSONS.md`, which is a deliberately **transitory inbox** — its own preamble calls it "where lessons pass through, not where they live." The episode store is the opposite: the spec's whole point is that the structured episode **outlives its consolidation**.

Moving to a tracked path also makes cross-worktree sharing git's own job. It needs no `durable_root()` — which, verified at HEAD (`agent_work_root.py:136-141`), returns the *worktree* root whenever an active Admiral epic lease exists, i.e. produces the very N-siloed-stores condition it would have been used to prevent.

## The acceptance criterion is exercised, not asserted

- **Session boundary:** `subprocess` + `sys.executable`, three distinct OS pids, and the child reports its own `getpid()` inside its answer so the result is tied to that process rather than assumed.
- **Worktree boundary:** real `git worktree add`, an assertion that each linked `.git` is a *file* carrying a `gitdir:` pointer, and the observed transition **absent → still absent after a local commit → present only after merge**. A shared filesystem would have leaked at step one.
- Both carry vacuity falsifications, and the reviewer independently proved the suite can fail by running **eight mutations** in an out-of-repo mirror — including neutering the anti-aliasing guard to test whether the worktree test could pass with two worktrees sharing a directory. It still went red.

## Non-foreclosure is shown, not promised

Each of the five agent-supplied fields is individually addressable with its own lifecycle standing, so one claim can be **disputed while a sibling stays active with no rewrite** — proven by a round-trip asserting the sibling's stored line is byte-identical before and after. Mechanical facts stay flat `key: value` lines carrying no strength and no standing, because the partition itself tells you which bin needs assertion machinery: agent-supplied claims get disputed, mechanical facts do not.

## The held decision, and what deferring it bought

Whether retiring **moves the file** or **flips a status field** was the human's. Keeping it genuinely open took two reworks across three g1 review rounds — each found another place describing a mechanism concretely while silently assuming one layout. Every such mechanism was routed through a named seam with one adapter per option and none bound.

**The deferral paid off exactly as designed: binding the ruling at g4 did not require changing a single g3 retrieval primitive.** The stop condition written for that possibility never fired.

Binding it also **relocated the silent-omission class twice**, and full cold-panel review caught both. First, the non-episode classifier did not move when membership moved from file *content* to file *location*, so the gate's own `README` placeholders became a phantom episode id in both scanned directories — the store as shipped could not be read by its own tooling. Fixed by making the store's existing id grammar the classifier, a computable property replacing a hand-maintained list; the placeholders then had to become `.gitkeep`, outside the file grammar entirely. Second, found on re-review and **filed as #321** rather than fixed here: the grammar classifies names the store *lists*, but nothing classifies an id the store is *handed*.

## Two silent-wrong-answer defects caught by review

Both were the same root cause — *an invariant enforced with a different definition than the code depending on it*:

1. The line-boundary guard rejected only `\n`/`\r`, but `parse_episode()` uses `str.splitlines()`, which breaks on more. `'safe - status: retired'` passed validation, **forged the exact status line the guard exists to prevent**, and silently truncated the record on the next touch. The guard is now `value != "" and value.splitlines() != [value]` — defined in terms of the parser's own behaviour, so the two cannot drift apart again.
2. `select_episodes()` did `set(values)`, so a bare string degraded to **character** membership: `select_episodes(root, "role", "implementer")` silently matched single-character roles and missed the value named. A bare string is now refused rather than wrapped.

## Out of scope, per the issue

Automated capture wiring (#305), consolidation and rhyme-search (#308), and #300's projection manifest. The existing `LESSONS.md` machinery is untouched; cutover is ruled at #308.

## Filed while building this

- **#313** — 24 repo docs prescribe `py -m pytest`, which false-reds as a broken suite where pytest is installed only for `python`.
- **#314** — `commander-core.md` tells delegated Commanders to have subagents reply via `SendMessage`, which their tier cannot do.
- **#319** — episode working-tree bytes differ across worktrees under `core.autocrlf`; harmless here, a real hazard for #308 if consolidation compares bytes rather than blob hashes.

## Known deferral

The promised re-check of the `context-manifest-ref` obligation against **#300's merged shape** ran and returned a **deferral**: #300 is still open and has not merged. Nothing here depends on its implementation (the reference is stored opaquely as `<ref>@<revision>`), so a later mismatch is a documentation fix rather than a rewrite — but whoever closes #300 or runs #305 must re-verify.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_0144fxRT9HovYs1rcStyJ8E6
