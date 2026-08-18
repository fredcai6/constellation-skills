# Reviewer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g4-review` — Dispose #596 and #526: review.

## Task statement

Two co-travelers of #559, each owed a **disposition backed by a grep, not an opinion** — and an
evidenced *"no longer reproduces"* is a complete, successful disposition, to be judged with the same
rigor as a fix.

The implementer returned:

| | Verdict it claims |
|---|---|
| **#596** — `CONSTELLATION_FEEDBACK.md` still mandated after the switch to the episode ledger | **reproduces, in a narrower and sharper form than the issue frames it** — repaired |
| **#526 defect 1** — close criteria name `python scripts/code_map/build.py` | **does not reproduce**, *"and never did, in the skill corpus"* |
| **#526 defect 1, widened** — close-criteria phrasing that assumes a layout | **reproduces once**, with a different script name — fixed |
| **#526 defect 2** — no survey-reuse convention across review rounds | **reproduces** — fixed |

Dispositions: `.agent-work/567-d1/dispositions/596.md`, `.agent-work/567-d1/dispositions/526.md`.
Full result: `.agent-work/567-d1/crew-handoffs/g4-implementer-result.md`.

## How to inspect

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
git status --porcelain
git diff HEAD -- skills/ .agent-work/templates/ tests/
```

Expect: `skills/admiral/SKILL.md`, `skills/admiral/references/fleet-doctrine.md`,
`skills/commander-delegated/SKILL.md`, `skills/reviewer/SKILL.md`,
`skills/reviewer/templates/REVIEW_SURVEY.template.json`, that template's two
`.agent-work/templates/` copies, and `tests/data/store_mentions.approved.txt`.

## Close criteria

1. Both disposition files exist and are non-empty.
2. Each **quotes the grep output that establishes it**, including a negative one.
3. `python3 -m pytest tests/test_cli_retirement_guard.py -q` reports no violation outside
   `skills/workbench/`.
4. `python3 -m pytest tests/test_mcp_adoption.py -q` stays green.
5. Any edited `.json` still parses.

The Commander has re-run 3–5 and the gate check independently (exit 0; adoption 172 passed, 2
skipped; all JSON parses; the edited `REVIEW_SURVEY.template.json` is byte-identical across all three
copies). Re-run them anyway; do not spend your budget there.

## The review's real work

### 1. Is each disposition's evidence sufficient for its verdict? — the whole gate

A disposition is a **claim about the world**, and the standard here is asymmetric:

- **For a "reproduces" verdict**, check the fix actually addresses what was found, and that what was
  found is what the issue meant.
- **For "does not reproduce"**, the bar is higher, not lower. A negative established by a grep is
  only as good as the grep's reach. **Re-run each negative search yourself, and widen it**: different
  script names, different phrasings, the overlay copies, the `.baseline/` mirrors. The implementer
  strengthens its own claim to *"and never did, in the skill corpus"* — that is a stronger statement
  than "not there now" and needs stronger evidence. Check it against git history if it is to stand.

The launch order pre-ruled #526 as a `guess`: *"the Admiral grepped `skills/commander/` and found no
match, so the issue may already be stale."* An honest null here is a complete deliverable — but an
**unchecked** null is not, and the difference is entirely in the search's reach.

### 2. #596 — verify the crux, because the whole disposition turns on it

The issue's sharpest claim is that `skills/commander-delegated/SKILL.md`'s clause — *"A `FENCE.md`
citation without the staged export still fails the gate"* — is **false as written**, because the
`feedback` gate's only postcondition asks for an **episode**, not an export.

**Read that gate's actual postconditions in `skills/commander/templates/COMMANDER_SPINE.template.json`
yourself** and say whether the clause was false, and whether the repair makes it true. A clause that
teaches a false model of what a gate enforces is the specific harm the issue names — the issue
records that agents propagate that model into launch orders, and that on 2026-08-15 both a lane and
the Admiral did exactly the right thing by a stale doctrine and produced work that had to be
reverted.

The governing doctrine is `docs/agents/ORCHESTRATOR_CONTEXT.md` §"The Retired Learning Playbook"
(#447). It is **read-only** — the authority, not the target. Check the repair against it, in
particular its hard bound: *"There is to be no successor playbook and no read-and-apply loop."* A
repair that reinvents a distilled-advice file under a new name is that retirement undone.

Also confirm: does the repair leave the **fence case** with an answer? A fenced Commander forbidden
from writing the main checkout still needs its learning to reach the Admiral. And is the archive
gate's `c4` deny-glob on `.agent-work/CONSTELLATION_FEEDBACK.md` still consistent with the new text?

### 3. #526 defect 2 — judge the convention against what this run actually did

The convention was undocumented, and **this run is the evidence**: gates `g1b` and `g3` were each
reviewed **twice** (BLOCK → rework → APPROVE). Round 1's survey was preserved and round 2 used a new
file, on Commander instruction rather than doctrine — which is the gap.

Read `.agent-work/567-d1/g1b-review/{review.json,review-2.json}` and
`.agent-work/567-d1/g3-review/{review.json,review-2.json}`, then ask: **does the convention the
implementer wrote describe what actually worked here?** The issue names two shapes — append a recheck
item as a sibling and re-consolidate with `--override-reason`, or a new round file. If the written
convention picks one, it should be the one the evidence supports, and it should say why.

**You are about to be the next instance of this.** If the convention is wrong or incomplete, you will
find out by following it.

### 4. Scope and the three-copy rule

`skills/reviewer/templates/REVIEW_SURVEY.template.json` is mirrored in `.agent-work/templates/` and
again under `.baseline/constellation-reviewer/`. All three must stay identical — a swept source beside
an unswept overlay is the drift this epic exists to remove. The Commander measured them identical;
confirm.

`tests/data/store_mentions.approved.txt` changed. Confirm the delta corresponds to the new store
mentions the edits introduce, and nothing else was silently dropped.

## Constraints on you

1. Re-run every verification command yourself and read the exit code.
2. Do not edit anything.
3. **File no issues.** If you find out-of-scope work, it is a triage candidate under
   `.agent-work/567-d1/triage-candidates/` — the human's ruling, *"we've been ballooning out
   tracking."*
4. Do not propose promoting anything into `docs/agents/*` — the human's call.
5. Fenced: `skills/workbench/**`, `docs/agents/**`, `scripts/mcp_spine_server.py`, `episodes/**`,
   `scripts/run_crew.py`, `scripts/checklist_engine.py`, `map/INDEX.md`,
   `tests/test_cli_retirement_guard.py`.
6. **POSIX shell only** — the engine runs `command` checks through `/bin/sh` (`dash` here);
   `set -o pipefail` is rejected with exit 2.
7. **Do not run the whole suite while driving your own survey through the engine** —
   `tests/test_gauge_chain_writer_to_trip.py:604` snapshots every file under the repo's
   `.agent-work/` and asserts nothing moved, so your own records produce a failure that is yours. A
   sibling reviewer in this lane hit exactly that and nearly reported it as someone else's defect.
   `g5-final` owns the whole-suite run, in a clean detached worktree.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
grep -rn 'CONSTELLATION_FEEDBACK' skills/ docs/ scripts/ | grep -v '^skills/workbench/'
grep -rn 'code_map/build.py\|code_map/check.py\|scripts/code_map' skills/ docs/ specs/ .agent-work/templates/
python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g4r.log 2>&1
grep -oE '^E +(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g4r.log | sed 's/^E *//' \
  | grep -v '^skills/workbench/' | sort -u        # expect nothing
python3 -m pytest tests/test_mcp_adoption.py -q
python3 -c "import json,glob; [json.load(open(p)) for p in glob.glob('skills/**/*.json',recursive=True)+glob.glob('.agent-work/templates/**/*.json',recursive=True)]; print('json ok')"
```

## Map anchors (inbound)

- `docs/agents/ORCHESTRATOR_CONTEXT.md` §"The Retired Learning Playbook" — the governing doctrine for
  #596. **Read-only.**
- `skills/commander/templates/COMMANDER_SPINE.template.json` — the `feedback` gate's real
  postconditions (#596's crux) and `archive`'s `c4` deny-globs.
- `skills/reviewer/SKILL.md:30` — what #526 defect 2 already had (`--override-reason` and its
  BLOCK/APPROVE asymmetry) and what it lacked.
- `.agent-work/567-d1/g1b-review/`, `.agent-work/567-d1/g3-review/` — this run's own two-round
  reviews, live evidence for #526 defect 2.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop conditions

Stop and return if: a "does not reproduce" verdict does not survive a widened search; a repair
reinvents a successor playbook; or reviewing would require editing a fenced file.

## Return format

Write the full `REVIEW_RESULT` to
`.agent-work/567-d1/crew-handoffs/g4-reviewer-result.md` **before ending your turn** — that write is
the delivery. Include a `Verdict` field whose value is exactly `APPROVE` or `BLOCK` (uppercase).
Include a `Workflow Feedback` section: what helped, what got in the way, and your own mistakes.

Survey state location: `.agent-work/567-d1/g4-review/review.json`. Fowler record:
`.agent-work/567-d1/g4-review/FOWLER_PASS.json`.
