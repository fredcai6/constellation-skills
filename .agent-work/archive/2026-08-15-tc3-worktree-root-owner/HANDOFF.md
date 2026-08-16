# Implementer Handoff: one owner for the default worktree root

**Issued:** 2026-08-15 · **Requested by:** the human, directly · **Not** under epic 568's latitude
contract, which expired at that epic's closeout. This handoff is the whole scope.

## Task

Give the repo **one** owner for the question *"where do worktrees live"*, and change the answer to
`<repo-root>/.worktrees`.

Today there are two answers and they are copies of each other:

1. `scripts/spine_lifecycle.py:154-158` — `_default_wt_root(root)` returns `str(root.parent / f"{root.name}-wt")`.
2. `scripts/mcp_spine_server.py:664` — computes `root.parent / f"{root.name}-wt"` **inline**, rather
   than calling the helper that exists for exactly this.

Both must end up returning `<root>/.worktrees`, and site 2 must **call** site 1 rather than restate it.

## Why now

The worktrees on disk were relocated to `.worktrees/` during epic 568, but **no code knows that
happened** — `grep -rn "\.worktrees" scripts/ skills/ docs/ tests/` returns zero hits. The MCP door
still creates worktrees at the sibling `-wt` path while every live worktree sits under `.worktrees/`.
Both layouts were registered in `git worktree list` at the same time. This closes that split.

## Scope — what is IN

- `_default_wt_root` returns `<root>/.worktrees`.
- `mcp_spine_server.py:664` calls `_default_wt_root` instead of duplicating its rule.
- Docstrings that assert the sibling convention as fact, at minimum
  `spine_lifecycle.py:154-157` and `mcp_spine_server.py:572-577`. The stale `_default_wt_root`
  docstring is republished verbatim into the generated map, so leaving it stale propagates.
- `.gitignore`: `.worktrees/` is currently **neither tracked nor ignored**, so every live worktree
  shows as untracked content inside the primary checkout. Once this is the default, ignore it.
- Regenerate `map/INDEX.md` with `python -m scripts.code_map build --root .` and commit it;
  `tests/test_code_map.py` fails the suite if it is stale.

## Scope — what is OUT, and must not be touched

- **The lexical-vs-git disagreement.** `spine_rail._worktree_from_spine` derives the owning worktree
  *lexically* from the spine path; `mcp_spine_server._worktree_root_for_lifecycle` asks
  `git rev-parse --show-toplevel`. Both have docstrings arguing their case, and they agree only while
  spines live at `<worktree>/.agent-work/<id>/`. Deciding which is authoritative is a design question
  and is **not** in this handoff. Leave both alone.
- **`origin_worktree_refusal`'s containment predicate** (`checklist_engine.py:155`). It admits a
  nested cwd, which is a real defect — separately recorded — but changing a live engine gate is not
  this change.
- **Existing `origin.worktree` values.** They are immutable engine identity and already name the old
  sibling location on archived spines. **No rewriting, no backfill, no migration.**
- **`.worktrees/epic-568-441`** — a retained worktree holding a live lease and a blocked `execute`.
  Do not touch, move, or clean it.
- Every `git rev-parse --show-toplevel` call in `map_orient.py`, `episode_capture.py`,
  `checklist_engine.py`, `verify_worktree_isolation.py`. These answer *"what is the repo root"*, a
  different question. They are not duplicates of this one.

## The risk that most likely breaks this — check it explicitly

**Windows path limits.** This repo has been bitten twice: nested checkouts pushed paths past the
Windows limit and `git worktree add` died with `exit 128 ('Filename too long')`, which is why two
rules exist in `.gitignore` (see its comments around `constellation-eval-*` and
`.agent-work/**/.agent-work/`). One capture landed at 216 characters.

Nesting worktrees under `<root>/.worktrees` makes every worktree path **~8 characters longer** than
the sibling `-wt` layout, and **CI is a single `windows-latest` job**.

Required: work out whether any test that runs `git worktree add` can now exceed the limit on the
Windows runner, and say so with numbers — the deepest path the new layout produces, against the
limit. If it cannot be made safe, **stop and report**; do not ship a change that reds Windows CI.

## Evidence required

- **Red before, green after**, over behavior: a test asserting `_default_wt_root` resolves to
  `<root>/.worktrees`, failing before your change.
- A test that `mcp_spine_server`'s open path and `_default_wt_root` agree — i.e. that the duplicate is
  genuinely gone rather than merely edited to match.
- **`tests/test_spine_lifecycle.py:136-160` is expected to change behavior and this is the interesting
  part.** It currently `pytest.skip`s whenever the checkout is not directly inside `<primary>-wt/`,
  which is always, so the default-layout convention has **no live coverage today**. Under the new
  default a worktree at `.worktrees/<slug>` *is* directly inside the default root, so that test should
  actually run. Confirm whether it does, from this worktree. If it still skips, say why — that is a
  finding, not a failure.
- Full Linux suite, cache-clean. Clear caches first:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  A stale `.pyc` carrying a dead path fabricated a convincing phantom failure during epic 568 and cost
  four falsifications to attribute. Baseline on `main` at `09747fc6` is **2997 passed, 0 failed**.

## Anything interesting you find

The human explicitly asked to "learn whatever is interesting." Record findings you are **not** fixing
in `.agent-work/tc3-worktree-root-owner/FINDINGS.md` rather than widening the diff. Two known leads,
neither yours to fix:

- Two stray work areas sit at `constellation-skills-wt/s` and `constellation-skills-wt/t`, dated
  2026-08-09, each containing exactly `context/` and `mechanical/`, neither a registered git worktree.
  The hypothesis — **unverified** — is that a work id was consumed character-by-character to build a
  path. If your work happens to confirm or refute that cheaply, say which. Do not delete them; they
  are deliberately preserved evidence.
- Whether the sibling `-wt` layout existed *because* of the Windows limit, or arbitrarily. The
  `.gitignore` comments are the only written trace found so far.

## Workspace

Worktree `.worktrees/tc3-worktree-root-owner`, branch `tc3/worktree-root-owner`, based on `main` at
`09747fc6`. Yours alone. Work area `.agent-work/tc3-worktree-root-owner/`.

No spine, no engine gates — this is a plain bounded implementation, not a gated run.

## Stop conditions

Stop and report rather than pressing on if:

- Windows path budget cannot be shown safe.
- Green would require touching anything in the OUT list.
- The change turns out to need the lexical-vs-git question answered.
- Any existing test's *intent* must change to pass, as opposed to its expected path value.

## Return shape

Report: what you changed; the red/green proof; cache-clean suite counts before and after; the Windows
path-budget numbers; whether the skipping test now runs; and anything recorded in `FINDINGS.md`.

**You are fenced from push, PR, and merge.** Leave the branch committed locally and say so.
