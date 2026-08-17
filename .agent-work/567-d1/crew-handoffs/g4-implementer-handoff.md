# Implementer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g4-implement` — Dispose issues **#596** and **#526**.

## Task

Two co-travelers of #559: the same kind of work, in the same files. Each gets a **disposition backed
by a grep, not by an opinion** — and **an evidenced "no longer reproduces" is a complete, successful
disposition**, reported with the same rigor as a fix.

Write one file per issue:
- `.agent-work/567-d1/dispositions/596.md`
- `.agent-work/567-d1/dispositions/526.md`

Each states the disposition and **quotes the grep output that establishes it, including a negative
one**.

---

## #596 — `CONSTELLATION_FEEDBACK.md` is still mandated after the switch to the episode ledger

**The issue's own framing**, which you should verify rather than assume: the Commander spine's
`feedback` step now has exactly one postcondition — *"this run captured at least one episode: an
episode in the store records this work id"* — so **the check is the episode ledger**. But several
live doctrine sites still mandate the older `CONSTELLATION_FEEDBACK.md` export, and one of them
asserts something the postcondition contradicts.

**The four sites the issue names.** All four are in this lane's files. Verify each still says what
the issue claims, at its current line:

| Site | What the issue quotes |
|---|---|
| `skills/admiral/SKILL.md` (~:96) | *"**Harvest before sweep (mandated substep, ordered before `git worktree remove`)**… What does **not** survive is a commander's worktree-local `CONSTELLATION_FEEDBACK.md` export, so collect that from each commander worktree **before** it is swept."* |
| `skills/admiral/references/fleet-doctrine.md` (~:160-167) | *"**Harvest before you sweep — a required precondition of removal**… removal is not permitted until it is collected"* |
| `skills/commander-delegated/SKILL.md` (~:17, now ~:22) | *"stage that export plus a `FENCE.md`… **A `FENCE.md` citation without the staged export still fails the gate**"* |
| `skills/commander/templates/COMMANDER_SPINE.template.json` (`feedback` imperative) | *"Include the crew Workflow Feedback harvested at each gN-integrate"* |

**The issue's sharpest claim, and the one to check first: the third is false as written.** A missing
feedback export *cannot* fail the `feedback` gate, because the postcondition asks only for an
episode. **Read the `feedback` gate's actual postconditions in
`skills/commander/templates/COMMANDER_SPINE.template.json` and confirm or refute that**, because the
whole disposition turns on it: a clause that teaches a false model of what a gate enforces is worse
than a redundant one, and the issue says agents propagate that model into launch orders.

**What it actually cost, from the issue** — evidence you do not need to re-derive: on 2026-08-15 a
lane wrote its episodes correctly *and also* produced a `CONSTELLATION_FEEDBACK.md` export plus a
`FENCE.md`, reasonably, because the delegated-commander clause says omitting it fails the gate. The
Admiral then harvested it into the durable file, because two other sites make harvesting a
precondition of sweeping a worktree. **Neither did anything wrong by the doctrine in front of them;
the doctrine is stale.** The harvest was reverted and the content refiled as #594.

**The governing doctrine is `docs/agents/ORCHESTRATOR_CONTEXT.md` §"The Retired Learning Playbook"**
(#447). Read it. It is explicit that `episodes/` replaces the old inboxes, that its only write path
is `scripts/apply_episode_delta.py`, and — the part that bounds your fix — **"There is to be no
successor playbook and no read-and-apply loop."** You may **not** edit that file; it is the
authority, not the target.

**What to decide and do.** Reconcile every live mandate in files this lane owns with the episode
ledger. Two things the issue flags as needing an answer rather than a deletion:

1. **Say what happens to the fence case that motivated staging.** A fenced Commander forbidden from
   writing the main checkout still needs its learning to reach the Admiral. Episodes are tracked
   inside the worktree and a commit carries them out — so does the staging step still have a job? If
   it does not, say so plainly; if it does, say what it stages and what checks it.
2. **The archive gate's `c4` git-change-policy deny-globs `.agent-work/CONSTELLATION_FEEDBACK.md`**
   (see `COMMANDER_SPINE.template.json`, `archive` `c4`). Note whether your change leaves that
   consistent.

Also present, and yours to judge: `scripts/collect_feedback.py` and `scripts/agent_work_root.py`
both still read/describe `CONSTELLATION_FEEDBACK.md`, and both are in this lane's sole-writer list.
**A script that still supports the file is not the same as doctrine that mandates it** — the issue is
about the mandate. Decide deliberately whether either is in scope, and say why either way. Do not
delete a working script's capability to make a grep come out clean.

---

## #526 — stock close criteria cite a nonexistent build script; no survey-reuse convention

**The launch order pre-ruled this one `guess`:** *"the Admiral grepped `skills/commander/` for the
nonexistent build script #526 names and found **no match**, so the issue may already be stale or may
describe different wording. Verify it reproduces before fixing it."*

**Two separate defects. Treat them separately — the Commander's own preliminary greps say they
disposed differently, and you should confirm or refute both independently.**

**Defect 1 — the build command.** The issue says the Commander's stock close-criteria phrasing told
three consecutive reviewers to run:

```
python scripts/code_map/build.py
python scripts/code_map/check.py
```

There are no such standalone scripts; the real entry point is the package CLI
(`python -m scripts.code_map build --root .`). The issue's own diagnosis of the cost is worth
carrying: each of the three reviewers rediscovered the real path independently and **none reported
it**, because from inside a single gate it reads as the Commander knowing something they do not.

**Commander's preliminary measurement, to be confirmed or refuted by you:** grepping
`skills/ docs/ specs/` for `code_map/build.py`, `code_map/check.py` and `scripts/code_map` returns
only three hits, all in `docs/CONSTELLATION_OVERVIEW.md`, and all of them name the package
correctly. **That looks like "no longer reproduces."** Widen the search before you conclude it —
the issue says *"the phrasing should resolve the entry point from the repo rather than assume a
layout"*, so also check whether any close-criteria phrasing anywhere assumes a layout, even with
different script names. An evidenced negative is a complete disposition; an unchecked one is not.

**Defect 2 — the survey-reuse convention.** On a re-review the survey already exists in a
consolidated state, and the convention — append a recheck item as a sibling, record it, re-consolidate
with `--override-reason` — is *"written down nowhere."*

**Commander's preliminary measurement:** `skills/reviewer/SKILL.md:30` documents `--override-reason`
and its BLOCK/APPROVE asymmetry well. It does **not** document reusing a survey across rounds. So
defect 2 looks like it **still reproduces**, in the narrower form of the two halves the issue names.

**And this lane has live evidence for it, which you should use.** This run reviewed gate `g1b`
**twice** — round 1 returned BLOCK, the implementer reworked, round 2 returned APPROVE. Read what the
reviewers actually did:

- `.agent-work/567-d1/g1b-review/review.json` — round 1's consolidated survey, preserved.
- `.agent-work/567-d1/g1b-review/review-2.json` — round 2's, a **new file**, because the Commander
  told it to preserve round 1 as the audit record.
- `.agent-work/567-d1/crew-handoffs/g1b-reviewer-result.md` §Workflow Feedback, and the round-1
  result preserved in git at `4df66479`.

That is the convention gap in action, one run old: the second reviewer needed a rule for what to do
with an existing consolidated survey, and got one from a handoff rather than from doctrine. If you
write the convention, write the one the evidence supports, and say which of the two shapes
(append-and-re-consolidate, or a new round file) this run actually used and why.

`skills/reviewer/SKILL.md` is this lane's file.

---

## Close criteria

1. `.agent-work/567-d1/dispositions/596.md` and `.agent-work/567-d1/dispositions/526.md` both exist
   and are non-empty.
2. Each states its disposition and **quotes the grep output that establishes it**, including a
   negative one where the answer is "no longer reproduces".
3. Every edit you make to `skills/**` keeps the guard green:
   `python3 -m pytest tests/test_cli_retirement_guard.py -q` reports no violation outside
   `skills/workbench/` (lane D2's fenced files — expected, not yours).
4. `python3 -m pytest tests/test_mcp_adoption.py -q` stays green.
5. Any edited `.json` still parses.

## Allowed scope

- `skills/**` **except** `skills/workbench/**`
- `scripts/collect_feedback.py`, `scripts/agent_work_root.py` — **only if** you decide they are in
  scope and say why
- `.agent-work/567-d1/dispositions/**`, `.agent-work/567-d1/triage-candidates/**`
- If you edit a `skills/` template that is mirrored in `.agent-work/templates/` and its `.baseline/`
  copy, **update all three** — gate `g2` swept all three and they must not drift apart again.

## Fenced — do not edit

`docs/agents/ORCHESTRATOR_CONTEXT.md` (the governing authority, and `docs/agents/*` promotion is the
human's call); `skills/workbench/**`, `docs/agents/CREW_CONTEXT.md` (lane D2);
`scripts/mcp_spine_server.py`, `episodes/**` (lane E); `scripts/run_crew.py` (lane F);
`scripts/checklist_engine.py` (lane H); `map/INDEX.md` (Admiral);
`tests/test_cli_retirement_guard.py` (the guard).

## Constraints

1. **File NO issues.** Stage candidates under `.agent-work/567-d1/triage-candidates/`. The human's
   reason, verbatim: *"we've been ballooning out tracking."*
2. **Do not promote any observation into `docs/agents/*`** — the human's call.
3. `episodes/` has exactly one write path, `scripts/apply_episode_delta.py --store-root episodes`.
   You should not need it. Never hand-edit under `episodes/`.
4. **Any edit you make to `skills/**` must keep the guard green.**
5. Edit shipped compact-format JSON templates as **raw text**; never round-trip through
   `json.load`/`json.dump`. Re-validate with `json.load` after.
6. **An evidenced "no longer reproduces" is a complete disposition.** Do not manufacture a fix to
   have something to show. There is no rule that a gate must end with a change —
   `decision:no-net-deletion-rule` was withdrawn by the human on 2026-08-17.

## Map anchors (inbound)

No architecture map exists in this repo (`map_orient` → `DEGRADED-UNPARSEABLE`). Entry points:

- `docs/agents/ORCHESTRATOR_CONTEXT.md` §"The Retired Learning Playbook" — **the governing doctrine
  for #596.** Read-only.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — the `feedback` gate's real
  postconditions (the crux of #596) and the `archive` gate's `c4` deny-globs.
- `skills/admiral/SKILL.md`, `skills/admiral/references/fleet-doctrine.md`,
  `skills/commander-delegated/SKILL.md` — the other three mandate sites.
- `skills/reviewer/SKILL.md:30` — what #526's defect 2 already has, and what it does not.
- `.agent-work/567-d1/g1b-review/{review.json,review-2.json}` — this run's own two-round review,
  live evidence for #526 defect 2.

## Deliverable path check

`git check-ignore .agent-work/567-d1/dispositions/596.md` → exit 1 (not ignored). Verified —
`.agent-work/` is tracked deliberately in this repo (11,188 files), so your dispositions are
committed on the branch and reach `main` at merge.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
grep -rn 'CONSTELLATION_FEEDBACK' skills/ docs/ scripts/ | grep -v '^skills/workbench/'
grep -rn 'code_map/build.py\|code_map/check.py\|scripts/code_map' skills/ docs/ specs/
python3 -m pytest tests/test_cli_retirement_guard.py -q
python3 -m pytest tests/test_mcp_adoption.py -q
git status --porcelain
```

The gate's own closing check, which the Commander re-runs independently. **POSIX form** — the engine
runs `command` checks through `/bin/sh`, which is `dash` here, and `set -o pipefail` is rejected with
exit 2:

```sh
test -s .agent-work/567-d1/dispositions/596.md \
  && test -s .agent-work/567-d1/dispositions/526.md \
  && { python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g4-guard.log 2>&1 || true; } \
  && ! grep -oE '(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g4-guard.log | grep -qv '^skills/workbench/'
```

**Do not run the whole suite while driving your own plan through the engine** —
`tests/test_gauge_chain_writer_to_trip.py:604` snapshots every file under the repo's `.agent-work/`
and asserts nothing moved, so your own engine records produce a failure that is yours.

## Test mode

**Doc/doctrine change.** No runtime behaviour changes, so no new runtime test is owed; the guard and
the adoption suite are the checks. If you change a script's behaviour, that needs a test and you
should say so.

## Required evidence

- For each issue: the grep output that establishes the disposition, quoted, including negatives.
- For #596: the `feedback` gate's actual postconditions, quoted, and whether the
  `commander-delegated` clause is false as written.
- For #526: separate verdicts on defect 1 and defect 2, each evidenced.
- The before/after text of every clause you reworded.

## Suggested model tier

**Opus.** Both issues are judgement about doctrine wording under a governing rule that forbids the
obvious fix (a successor playbook), and one of them may correctly end in a measured negative.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop conditions

Stop and return if: reconciling a mandate would require editing `docs/agents/*` or a fenced file;
the `feedback` gate's real postconditions contradict the issue in a way that changes the whole
disposition; or a fix would need a successor playbook, which the governing doctrine forbids outright.

## Return format

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/567-d1/crew-handoffs/g4-implementer-result.md` **before ending your turn** — that write
is the delivery. Include a `Return status` field whose value is exactly `complete` (lowercase) when
the close criteria are met. Include a `Workflow Feedback` section: what helped, what got in the way,
and your own mistakes.
