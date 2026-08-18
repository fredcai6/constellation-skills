# Reviewer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g2-review` — Sweep the corpus and the tracked overlay, and invert the mandate: review.

**This is the epic's headline diff.** 23 files, doctrine that ships to every agent in the corpus.

## Task statement

Issue #559: *"the door is the interface, not a second path — remove the CLI fallback for agents."*
The human's ruling, verbatim:

> **"the agents should not know about the CLI. period."**

The implementer did three things in one gate:

- **(a) The sweep** — 13 `CLI fallback` clauses and 10 `<engine>` occurrences out of `skills/`
  (excluding lane D2's `skills/workbench/`), plus the drive-path cell at
  `skills/write-a-skill/SKILL.md:20`, then propagated to the tracked `.agent-work/templates/`
  overlay and its `.baseline/` mirrors (16 `<engine>`, 18 clause occurrences, 10 files).
- **(b) The mandate inversion** — the assertions in `tests/test_mcp_adoption.py` that *required* the
  text, inverted to absence assertions or deleted, plus `tests/data/store_mentions.approved.txt`
  regenerated.
- **(c) The specificity proof** — a clause reintroduced at a reworded site, guard RED; reverted,
  guard GREEN on the reworded text.

**Why (b) matters more than it looks.** That test suite is *why this text grew back twice*. A lane
deleted the clauses, the suite went red on a test whose own message said *"the CLI door must stay,
never be removed or discouraged"*, and the lane put the text back. The regrowth had a mechanism and
it was a test. **Inverting it is the real work of this gate**, and it is where a mistake would be
hardest to see.

## How to inspect

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
git status --porcelain
git diff HEAD -- skills/ .agent-work/templates/ tests/
```

The full `IMPLEMENTER_RESULT` is at `.agent-work/567-d1/crew-handoffs/g2-implementer-result.md`. It
reports a **tenth** mandating assertion the handoff's table of nine missed — find it in the ledger
and judge whether the handling was right.

## Close criteria

1. `grep -rn -i 'CLI fallback' skills/ --exclude-dir=workbench` → nothing.
2. `grep -rn '<engine>' skills/ --exclude-dir=workbench` → nothing.
3. Same two greps over `.agent-work/templates/` → nothing (mirrors included).
4. `python3 -m pytest tests/test_mcp_adoption.py -q` → green.
5. The guard reports **no** violation outside `skills/workbench/`.
6. All five overlay files and their `.baseline/` mirrors match their `skills/` sources
   (`git hash-object`).
7. `scripts/init_work_area.py:24` and
   `docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` are **untouched**.
8. Every edited `.json` parses.

The Commander has already re-run 1–5, 7 and 8 independently: gate check exit 0, non-workbench site
list empty, 41 JSON files parse, both survivors untouched by `git diff`. **Re-run them anyway** — a
pasted summary is a pointer to evidence, never the evidence — but do not spend your budget there.

## The review's real work

### 1. Judge the replacement wording — this is the biggest thing

Every clause was replaced, not just deleted. Read each replacement **as an agent would**, in place,
and ask three questions:

- **Is it true?** It must not promise a door path the measurement shows does not exist.
- **Does it leave anyone stranded?** `global-everyone.md`: *"Fail visibly rather than emit plausible
  wrong output; no hidden fallback."* Deleting an agent's only path and saying nothing trades a
  documentation problem for a hidden-fallback problem.
- **Does the two-path idea survive in the grammar?** The implementer claims it removed *"by default
  … otherwise"* framings too, on the grounds that leaving them keeps the two-path idea alive after
  the second path is gone. Check that claim against the diff.

**The three second-checklist sites are the hard ones** — `skills/interrogator/SKILL.md`,
`skills/write-a-skill/templates/{gated-engine,survey}-SKILL.template.md`. There the door **provably
cannot** reach the path: it refuses to rebind while the process holds its own lease
(*"one door drives one spine at a time"*), and releasing the lease to escape fails the archive
provenance check. Those three keep a real path and lose the "fallback" framing, per the Admiral's
F-1 ruling and the framing it endorsed: *"'CLI fallback' is the wrong word, because a fallback
implies a working primary."* **Judge whether the new wording states the measured truth or merely
avoids the banned phrase.**

### 2. Audit the mandate inversion, assertion by assertion — the load-bearing check

For **each** of the assertions at the old lines 737, 784, 834, 950, 954, 1132, 1149, 1324, 1345 —
plus the tenth the implementer found — establish:

- **inverted or deleted?**
- **if deleted, was that right?** The rule given was: delete where the target is a **lane-D2 file**
  (`skills/workbench/**`, rows 950/954/1324 and the `skills/workbench/SKILL.md` entry in
  `TIER2_SKILL_FILES`), because those files still carry the text, lane D2 has not merged, and an
  inverted assertion would go red on a fenced file — coverage is not lost because
  `tests/test_cli_retirement_guard.py` asserts absence over the whole corpus. **Verify that
  reasoning holds for every deletion**, and flag any deletion that is *not* covered by it.
- **was any door-tool-affirmative half weakened?** `test_field_names_door_tool_as_default`,
  `test_paragraph_names_door_tool`, `test_names_door_tools_as_default`,
  `test_no_door_tool_name_introduced` and their siblings were to stay **exactly as strict**.

**The count fell from 183 passed to 172.** Account for the difference: 11 fewer passing tests should
correspond exactly to assertions inverted or deleted, with none silently lost. If it does not
reconcile, that is the finding of this gate.

**And check the two rules that suite holds about itself**, stated in its own header: the corpus is
**walked, never listed**; and **no assertion may be satisfied by the negation of what it pins**. An
inversion that quietly turns a walked check into a listed one is the defect this whole epic is about,
reappearing in the fix.

### 3. Verify the specificity proof is discriminating, not vacuous

The implementer reintroduced a clause at `skills/interrogator/SKILL.md:28`, **one line below** the
reworded text at `:27` that describes the same mechanism in the same words. RED named `:28`; `:27`
was flagged by nothing, in either direction.

**Re-run this proof yourself.** Make the scratch edit, run the guard, revert, run again, and confirm
the tree is clean afterwards (`git status --porcelain`). This is the item that closes #559 and it is
the one thing in this run that a pasted transcript should not be trusted for. If the reworded text
and the reintroduction are not genuinely adjacent and near-identical, the proof is weaker than
claimed.

### 4. `store_mentions.approved.txt`

It was regenerated *"through the guard's own code path"*. Confirm that is a real regeneration and not
a hand-edit dressed as one, and that the file's remaining content is still true of the tree.

## Constraints on you

1. **Re-run every verification command yourself and read the exit code.**
2. **Do not edit anything.** Report findings.
3. **Do not edit `tests/test_cli_retirement_guard.py`** and do not propose widening it to cover
   something the sweep should have fixed.
4. The guard failing on `skills/workbench/**` is **known and expected** — lane D2 owns and deletes
   those files, this lane merges last, `g5-final` re-runs the guard after the rebase. Not a defect.
5. **Author any shell in POSIX form.** The engine runs `command` checks through `/bin/sh`, which is
   `dash` here; `set -o pipefail` is rejected outright with exit 2. This lane has paid for that once.
6. **Do not run the whole suite while driving your own survey through the engine.**
   `tests/test_gauge_chain_writer_to_trip.py:604` snapshots size and mtime of every file under the
   repo's `.agent-work/` and asserts nothing moved — your own records break it and the failure looks
   like someone else's. A sibling reviewer in this lane hit exactly that. `g5-final` owns the
   whole-suite run, in a clean detached worktree.
7. Write your Fowler record to `.agent-work/567-d1/g2-review/FOWLER_PASS.json`, not the template's
   work-id-root default — that path already holds another gate's record.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
grep -rn -i 'CLI fallback' skills/ --exclude-dir=workbench          # expect nothing
grep -rn '<engine>' skills/ --exclude-dir=workbench                 # expect nothing
grep -rn -i 'CLI fallback' .agent-work/templates/                   # expect nothing
grep -rn '<engine>' .agent-work/templates/                          # expect nothing
python3 -m pytest tests/test_mcp_adoption.py -q                     # expect green (172 passed, 2 skipped)
python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g2r.log 2>&1
grep -oE '^E +(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g2r.log | sed 's/^E *//' \
  | grep -v '^skills/workbench/' | sort -u                          # expect nothing
git diff --quiet HEAD -- scripts/init_work_area.py docs/superpowers/ && echo survivors untouched
python3 -c "import json,glob; [json.load(open(p)) for p in glob.glob('skills/**/*.json',recursive=True)+glob.glob('.agent-work/templates/**/*.json',recursive=True)]; print('json ok')"
```

## Map anchors (inbound)

No architecture map exists (`map_orient` → `DEGRADED-UNPARSEABLE`). Entry points:

- `tests/test_mcp_adoption.py:838` — `TestTier2SpineAlreadyBoundForDispatchedCrews`, the in-tree
  precedent the inversion generalizes. It already asserted absence for two files and already pinned
  the human ruling verbatim. **Read it first**: the inversion should read as that precedent widened,
  not as a reversal.
- `tests/test_mcp_adoption.py:1268` — `TestCLIStaysAvailableNotDeprecated`, whose whole premise this
  gate inverts. Its docstring is also the repo's measured argument about over-eager predicates.
- `tests/test_mcp_adoption.py` header — the two rules the suite holds about itself.
- `tests/test_cli_retirement_guard.py` — the guard, the specification this sweep was written against.
- `.agent-work/567-d1/notes-1.md` §M1 — the fresh-process probe behind the three reworded sites.
- `.agent-work/567-d1/LAUNCH_ORDER.md` — the Admiral's F-1 ruling on those three sites.

## Evidence produced by the implementer

Every figure is its own; re-derive rather than accept.

- 23 files changed: 11 under `skills/`, 10 under `.agent-work/templates/`, 2 under `tests/`.
- Every JSON template edited as **raw text** with `assert raw.count(old) == 1` per edit, re-validated
  with `json.load`; no `json.dump` round-trip.
- Adoption suite green; the guard's non-workbench site list empty.
- Specificity proof pasted verbatim, both directions.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop conditions

Stop and return if: a replacement leaves an agent with no path; an inversion weakens a
door-affirmative half; a deletion is not covered by the lane-D2 rule; the 183→172 count does not
reconcile; or the specificity proof does not reproduce in your hands.

## Return format

Write the full `REVIEW_RESULT` to
`.agent-work/567-d1/crew-handoffs/g2-reviewer-result.md` **before ending your turn** — that write is
the delivery. Include a `Verdict` field whose value is exactly `APPROVE` or `BLOCK` (uppercase).
Include a `Workflow Feedback` section: what helped, what got in the way, and your own mistakes.

Survey state location: `.agent-work/567-d1/g2-review/review.json`.
