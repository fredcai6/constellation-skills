Closes #33.

## The finding

The Agent-tool `isolation:"worktree"` parameter is a **harness primitive that is silently a no-op on Windows**: subagents launched with it run in the shared checkout instead of their own worktree. An Admiral dispatching a parallel wave in that belief gets a collision in the single checkout. It was the #2 finding of the dogfooding harvest, hitting two **independent** projects: network_elo (two Commanders racing a push) and story_time (three crews colliding on `git checkout -b`, a commit landing on a sibling's branch). This is data loss, not friction.

## The strategy — fix it, don't enshrine the workaround

The issue's first idea was "detect-and-serialize": verify isolation after launch, and if absent fall back to sequential dispatch. That **permanently surrenders parallel throughput** on the main dev platform — the exact "confirmed into a permanent workaround instead of fixed" pattern the fold-back arc exists to stop. And it can't even be preflight-verified: a git-level probe (`git worktree add` in a temp dir) tests *git's* worktree support, which is fine on Windows — it's the Agent *tool* that skips provisioning — so a probe returns a false green.

So we **stop trusting the flag and provision worktrees explicitly.** `git worktree add` works fine on Windows. The Admiral runs it itself before a parallel wave and hands each Commander its absolute workspace path. Isolation becomes real; parallelism is preserved.

## The change

**A new helper — `scripts/verify_worktree_isolation.py`** (styled after `verify_state_note.py`), with two modes:

- `verify_worktree_isolation.py PATH [PATH ...]` — the Admiral's **pre-wave gate**: every path must exist, be a registered git worktree, and be distinct from every other path and from the primary checkout. Exit 0/1.
- `verify_worktree_isolation.py --here EXPECTED` — a Commander's **first-step self-check**: is my `git rev-parse --show-toplevel` my assigned worktree, or did I land in the shared checkout?

The decision logic is split into pure, unit-tested helpers — `normalize_path` (`os.path.normcase(os.path.realpath(...))`, folding Windows case/separators/junctions), `parse_worktree_list`, `check_distinct_real`, `check_here` — with a thin git-shelling CLI and one guarded integration test over a real `git worktree add`. The primary checkout is found via the parent of `git rev-parse --git-common-dir` (ordering-independent, not "the first `git worktree list` entry").

**Doctrine — three files.** A new `fleet-doctrine.md` section ("Worktree isolation is a harness no-op on Windows — provision it yourself") states the provision → gate → sweep lifecycle: `git worktree add` logged in the ADMIRAL_LOG, the wave gated on `verify_worktree_isolation.py`, and worktrees swept only after the Commander's PR is **merged** or it is **confirmed dead with no continuation pending**. The `LAUNCH_ORDER` `## Workspace` field now carries the provisioned absolute path + the `git worktree add` command + a first-step `--here` instruction; `## Return Shape` requires the Commander to paste its `--here` confirmation. The `admiral/SKILL.md` dispatch bullet and closeout item are updated to match.

## Enforcement, honestly

The gate is the **mechanical guarantee** (run before launch; the Admiral doesn't launch on a non-zero exit). `--here`, run by the Commander, is **risk-reduction surfaced as evidence in the return report** — Agent-tool dispatch has no engine chokepoint to hard-refuse at, and the doctrine says so plainly rather than implying a guarantee it can't make.

## Testing

- TDD: pure-helper unit tests (registered/primary/duplicate/mismatch/missing-path/git-failure/usage-error branches) plus a git integration test; the symlink-resolution test skips gracefully where links are unprivileged.
- Full suite: **219 passed, 1 skipped** on this branch (was 205; +14 new methods, no regressions).

Built subagent-driven (per-task TDD + spec/quality review + opus whole-branch review: *Ready to merge = Yes*, no blockers — the reviewer ran the real script and confirmed it rejects a path that is really the shared checkout while passing N distinct worktrees).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
