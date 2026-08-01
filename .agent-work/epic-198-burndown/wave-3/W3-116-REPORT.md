# W3-116 Report — commander-tests

**Issue:** #116 — test-hardening: SKILL_INDEX pin + `_shared` sync-integrity + discovery-derived `SKILL_NAMES`
**Launch order:** `.agent-work/epic-198-burndown/launch-orders/W3-116-tests.md`
**Worktree:** `C:/Programs/cs-wt-tests` (branch `test/hardening-116`, base `main` @ `c0f18ce`)
**PR:** https://github.com/fredcai6/constellation-skills/pull/209 (NOT merged — Admiral's call) — now **genuinely green** (see Amendment below)
**Model tier:** sonnet (Commander + implementer + reviewer subagents, all sonnet)

## AMENDMENT (post-archive, per Admiral ruling)

Team-lead ruled fix-now: amended this PR's file-ownership fence to greenlight adding the 3 missing
`SKILL_INDEX.md` entries in this same PR (constellation-diagnose, constellation-to-issues,
constellation-write-a-skill), constrained to exactly those 3 entries with accurate frontmatter-
sourced descriptions, independent-reviewer-verified, pin test required to be genuinely green after.

Reopened the spine (`reopen execute`, cascade-reset reconcile/triage/review/feedback/archive as
designed), added gate `g2` (implement/review/integrate) to `execute.json`, drove it through the
engine exactly like `g1`:
- Implementer added the 3 entries, modeled on existing format, sourced from each skill's real
  `SKILL.md` frontmatter `description:` field.
- Independent fresh-context reviewer read all 3 frontmatter files directly (not trusting the
  implementer's quotes) and confirmed each entry faithful; confirmed exactly 3 additions, 0
  removals/reorders; confirmed suite genuinely green. Verdict: **APPROVE**.
- Full suite re-verified independently by the Commander: **50 passed, 226 subtests passed, 0
  failed** (up from 49 passed / 1 known-red).
- Triage candidate tc1 updated from "floated, out of scope" to "resolved in this PR."
- Second commit `f87aaa1` pushed to `test/hardening-116`; PR #209 body updated to describe the
  now-fully-green state.

This is the "genuinely-green PR" outcome the original report flagged as the alternative to holding
or shipping a known-red test — the Admiral chose it, and it closed cleanly.

## Isolation check (first action)

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-tests
worktree OK: in C:/Programs/cs-wt-tests
```

## Verdict per fix

1. **SKILL_INDEX pin — IMPLEMENTED, correctly RED against real drift (floated, not fixed).**
   New test `test_every_discovered_skill_is_pinned_in_skill_index` enumerates
   `installer.discover_skills()` and asserts every discovered skill's `skills/<name>/SKILL.md`
   path appears in `SKILL_INDEX.md`. It is a genuine hard assertion — no allowlist, no skip. It
   currently fails because `SKILL_INDEX.md` really is missing 3 of 19 discovered skills:
   `constellation-diagnose`, `constellation-to-issues`, `constellation-write-a-skill` (confirmed
   independently before writing any code, and reproduced twice more afterward, plus by an
   independent reviewer). Per file ownership, `SKILL_INDEX.md` was **not** edited to force this
   green — floated as a triage candidate below instead. This is exactly the "docent/explorer/
   prototyper"-class silent gap the issue describes, recurring with three different skills.

2. **`_shared` sync-integrity — IMPLEMENTED, green.**
   New test `test_shared_sync_integrity_installed_references_match_source_bytes`: for every skill
   with a non-empty `SKILL_REFERENCE_BUNDLES` entry, installs to a temp dir and asserts each
   installed `references/<f>` is byte-identical to source `skills/_shared/<f>`. Passes cleanly
   (226 subtests across the file's `subTest` blocks, this test contributing its share).

3. **Discovery-derived `SKILL_NAMES` — IMPLEMENTED, green.**
   `SKILL_NAMES` is now `sorted(skill.install_name for skill in load_installer().discover_skills())`
   — no hand-maintained roster remains. Every pre-existing test consuming `SKILL_NAMES` stays green.

## Evidence

Full suite (`py -m pytest tests/test_install_constellation.py -v`), reproduced independently by the
Commander (twice) and by a fresh-context independent reviewer:

```
1 failed, 49 passed, 226 subtests passed
FAILED tests/test_install_constellation.py::InstallConstellationTests::test_every_discovered_skill_is_pinned_in_skill_index
```

Isolated pin-test failure detail:
```
AssertionError: Lists differ: [] != ['constellation-diagnose', 'constellation-to-issues', 'constellation-write-a-skill']
```
— exactly the 3 known-missing names, no others, no false negatives.

`git diff main -- scripts/install_constellation.py SKILL_INDEX.md skills/_shared/ "skills/**/SKILL.md"`
→ empty. No production or content file touched. Only `tests/test_install_constellation.py` changed
(1 file, 64 insertions, 21 deletions).

Independent reviewer (fresh context, dispatched via `run_crew.py --backend external` + Agent tool,
own engine-driven survey including a Fowler pass) verdict: **APPROVE**. Re-ran every command
independently rather than trusting the implementer's claims.

## Map impact

None. This repo carries no `docs/architecture/` map (confirmed at the context step — it's a
skill-source repo). Reconcile step recorded a reasoned no-op per the commander skill's
skill-source-repo fallback.

## Triage candidates

1. **`SKILL_INDEX.md` is missing entries for `constellation-diagnose`, `constellation-to-issues`,
   `constellation-write-a-skill`.** RESOLVED in this PR via the amendment above (Admiral ruling,
   gate g2). No follow-up issue needed — the drift was fixed directly, verified by the pin test
   flipping from red to green and an independent reviewer confirming each entry's accuracy against
   the real skill frontmatter.

## Workflow feedback (durable root)

Under this epic your durable root resolves worktree-local (active `admiral-burndown-198` lease
fences the main checkout) — per the launch order's Return Shape, I wrote the trio directly at
`C:/Programs/cs-wt-tests/.agent-work/AGENT_FEEDBACK.md` and
`C:/Programs/cs-wt-tests/.agent-work/LESSONS.md` (now moved with the archived work area to
`C:/Programs/cs-wt-tests/.agent-work/archive/2026-07-19-116-tests/`, with `AGENT_FEEDBACK.md` and
`LESSONS.md` left at the worktree's `.agent-work/` root, gitignored, uncommitted, per the archive
step's imperative for a gitignored `.agent-work/`). No staging under `.agent-work/staged-feedback/`
was needed since the durable root correctly resolved worktree-local — no fence blocked it.

**One real finding surfaced mid-feedback-step, worth flagging to you directly:** the installed
`~/.claude/skills/constellation-commander/scripts/agent_work_root.py` (the copy every commander in
this session invokes via absolute installed path, per doctrine) is **stale relative to this repo's
own `main`** — it is missing the #118 epic-lease-fencing logic entirely (confirmed by diff: 12+
lines of missing logic; `verify_agent_feedback.py` itself was byte-identical between installed and
repo copies). Because `verify_agent_feedback.py` imports `agent_work_root` as a sibling module,
invoking it via the installed absolute path pulls in the STALE sibling, so `durable_root()` silently
resolved to the MAIN checkout instead of worktree-local — the opposite of what the active epic
lease should produce. I worked around it per-call with the script's own documented `--root .`
override (never by editing the installed corpus or hand-editing spine.json), and force-waived the
two affected spine postconditions (`feedback.c1`, `archive.c1`) with a documented reason each,
independently re-verifying the actual invariant held true both times. **This will very likely bite
every other commander in this wave the same way** if they invoke `verify_agent_feedback.py` at
`feedback`/`archive` without `--root .` — worth a heads-up to the other wave-3 commanders, and
worth considering whether a corpus refresh (`check_corpus_freshness.py`) is warranted before further
dispatches on this epic, or whether commander-core doctrine should just always pass `--root .`
explicitly on these two calls regardless of durable-root logic version skew. Banked as lesson
`stale-installed-corpus-sibling-import-drift` (constellation scope, not yet ripe — single instance
so far) in the worktree-local `LESSONS.md`.

Crew-reported friction (implementer + reviewer, both integrated into the archived
`AGENT_FEEDBACK.md`): a verification-command example implicitly constrained a test name substring
(should be stated explicitly in handoffs); the reviewer noted this worktree fixture has no
`docs/agents/` overlay at all, which the reviewer skill's context step expects at least partially.

## Full suite / instruction adherence

Fully followed the launch order, Pre-Rulings, and File Ownership. Spine driven init → context →
understand → plan → execute (1 gate: implement/review/integrate) → reconcile (no-op, no map) →
triage (1 candidate routed as a floated recommendation) → review → feedback → archive, all through
the engine, lease claimed at init and released as the final action after archive's closing advance.

## Isolation output (repeated per Return Shape)

```
worktree OK: in C:/Programs/cs-wt-tests
```
