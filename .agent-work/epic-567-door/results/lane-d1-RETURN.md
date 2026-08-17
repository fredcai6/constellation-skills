# Lane D1 return — the complete doctrine sweep and the regrowth guard (#559, with #596 and #526)

Epic **#567**, wave 2, lane **D1**. Branch `feat/567-d1-doctrine-sweep-guard`, rebased on
`origin/main` at `5099eea1`. Verified head: **`1037ab86`** (the suite run below); current head
carries only the return artifact and closeout on top.

---

## 1. Verdict

**Delivered.** #559 is closed by a guard, not by a deletion. Every `CLI fallback` clause and every
agent-facing `<engine>` token is gone from this lane's files *and* from the tracked overlay an agent
in this repo actually instantiates; the test that mandated the text is inverted; and the guard is
red-proofed at the hardest place available — a reintroduction one line below the reworded text that
says the same thing in the same words.

**The launch order's own acceptance test passes.** The order said the sweep is not done if a token
still reaches a Commander from a freshly instantiated spine, *"whatever a grep over the templates
says."* I instantiated one with `init_work_area.py` in a clean detached worktree and read the `init`,
`plan` and `archive` imperatives a Commander is handed:

```
init    <engine>: False | CLI fallback: False | checklist_engine.py: False
plan    <engine>: False | CLI fallback: False | checklist_engine.py: False
archive <engine>: False | CLI fallback: False | checklist_engine.py: False
```

**One thing is not finished and it is not mine to finish:** lane **D2 has not merged**. The guard is
green everywhere except `skills/workbench/SKILL.md` and
`skills/workbench/references/checklist-engine.md` — 10 addresses, 2 files, both D2's, which D2
deletes. I proved rather than promised that this residual is the whole of it: **with
`skills/workbench/` removed in a scratch copy, the guard is fully green, 19 passed.** See §6.

---

## 2. The sweep table

### `CLI fallback` clauses — 13 in this lane's files, all gone

| # | Site | Disposition |
|---|---|---|
| 1 | `skills/admiral/templates/ADMIRAL_SPINE.template.json` `.tasks.init.imperative` | swept — door named as the path |
| 2 | `ADMIRAL_SPINE` `.tasks.closeout.imperative` | swept |
| 3 | `skills/charter/SKILL.md:12` | swept |
| 4 | `skills/commander/references/commander-core.md:127` | swept |
| 5 | `COMMANDER_SPINE.template.json` `.tasks.init.imperative` | swept |
| 6 | `COMMANDER_SPINE` `.tasks.plan.imperative` | swept |
| 7 | `COMMANDER_SPINE` `.tasks.archive.imperative` | swept |
| 8 | `skills/explorer/SKILL.md:31` | swept |
| 9 | `EXPLORER_SPINE.template.json` `.tasks.init.imperative` | swept |
| 10 | `EXPLORER_SPINE` `.tasks.route.imperative` | swept |
| 11 | `skills/interrogator/SKILL.md` | **reworded** — second-checklist site |
| 12 | `skills/write-a-skill/templates/gated-engine-SKILL.template.md` | **reworded** |
| 13 | `skills/write-a-skill/templates/survey-SKILL.template.md` | **reworded** |
| — | `skills/workbench/SKILL.md:37`, `…/checklist-engine.md:5`, `:45` | **lane D2's** — not swept, deliberately |

For the 10 bound-spine sites the replacement names the path that works. For the 3 second-checklist
sites the clause is reworded to the measured truth, per the Admiral's F-1 ruling and the framing it
endorsed: *"'CLI fallback' is the wrong word, because a fallback implies a working primary."*

The sweep also removed the *"by default … otherwise"* framings around the deleted clauses. Leaving
them keeps the two-path idea alive in the grammar after the second path is gone.

### All 11 `<engine>` sites classified, including the two that survive

| # | Site | Class | Disposition |
|---|---|---|---|
| 1 | `docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` | historical plan record | **survives** — pre-ruled, and **out of the guard's walk by the walk rule alone**, named nowhere |
| 2 | `scripts/init_work_area.py:24` | comment documenting the never-resolved-placeholder convention | **survives** — same, structurally out |
| 3–4 | `ADMIRAL_SPINE` init, closeout | agent-facing | swept |
| 5 | `commander-core.md:127` | agent-facing | swept |
| 6 | `crew-dispatch.md:35` | agent-facing (arrived in wave 1 via lane C) | swept |
| 7–9 | `COMMANDER_SPINE` init, plan, archive | agent-facing | swept |
| 10–11 | `EXPLORER_SPINE` init, route | agent-facing | swept |

**Two census refinements the crews reported rather than smoothed**, both of which changed the work:

- `<engine>` is **10 occurrences on 9 lines**. `COMMANDER_SPINE` `.tasks.archive.imperative` carries
  **two** on one line. A one-edit-per-line sweep would have left one behind.
- `CLI fallback` matched **16**, not 15: the pattern's loosened separator also catches `CLI-fallback`
  at `skills/workbench/references/checklist-engine.md:45`, prose that *forbids* the thing while
  quoting it. Accepted as a declared false-alarm class rather than narrowing the pattern to duck it —
  a hyphen respelling is the cheapest way to defeat a space-only pattern.

### A surface the order did not know about, and without it #559 is not closed

`.agent-work/templates/` is a **tracked overlay** of the skills templates that workbench doctrine
tells agents to **prefer** when instantiating. It carried the same doctrine, byte-identical, and
**mirrored again** under `.baseline/<skill>/`. Nothing in the repo read it.

Measured: **16 `<engine>` occurrences and 18 clause matches across 10 files.** All swept, all three
copies of each template verified byte-identical afterwards.

I floated the ownership gap; **the Admiral independently granted it at `5099eea1`** and named the
root cause better than I did: *"Nobody owned it because I built the ownership table from the lanes'
missions rather than from the guard's reach."* Its landmine warning — that the obvious repair would
write this host's absolute paths into up to 56 tracked files — did not bite: this lane never ran the
installer, it propagated content directly.

---

## 3. The guard, red-proofed — the item that closes #559

`tests/test_cli_retirement_guard.py`, 718 lines. **It is a generalization of an in-tree precedent**
(`test_mcp_adoption.py:838`, which already asserted absence for 2 files and already pinned the human
ruling verbatim), widened from 2 files to **216 files / 3098 texts**.

**Scope has an exception list of length zero.** It reuses the repo's own `INSTRUCTION_FILES` walk —
imported, not re-derived, so the repo holds one definition of "agent-facing text" — extended to
`specs/**/*.toml` and `.agent-work/templates/**`. Both pre-ruled survivors are out **because of what
they are**, named nowhere. The overlay walk is rooted *at* the overlay, so this run's own artifacts
are never reachable rather than reached-and-filtered — which is why no exception is needed.

**Four patterns, because the behaviour has four shapes**, not one spelling. Every failure message
carries the scan census and quotes the ruling verbatim — this lane may not write `docs/agents/*` and
files no issue, so a pointer would dangle; carrying the ruling inline means deleting the guard
deletes its reason.

### The red-proof

The specificity proof is at the hardest available place: a genuine clause reintroduced at
`skills/interrogator/SKILL.md:28`, **one line below** the reworded text at `:27` that describes the
same mechanism in the same words.

```
$ python3 -m pytest tests/test_cli_retirement_guard.py -q ; echo "exit: $?"
exit: 1
E             skills/interrogator/SKILL.md:28
E                 ...checklist engine, and by nothing else. CLI fallback, always available: the absolute path to...
FAILED …::test_no_cli_fallback_clause_reaches_an_agent
FAILED …::test_no_engine_invocation_reaches_an_agent

$ # scratch edit reverted, tree clean
$ python3 -m pytest tests/test_cli_retirement_guard.py -q
### site addresses, non-workbench only:
### (empty)
```

`:27` is flagged by nothing in either direction. **The guard separates the two sentences, not the two
files.** A pattern that merely banned the phrase would fail this.

### It was reviewed BLOCK twice, and both were right

- **`g1b` round 1** — the verb list enumerated **17** of the engine's **18** verbs; `resume` was
  missing, so `<cli> resume g1 --reason '…'` passed all four patterns. Fixed **at the class**: the
  verb set is now derived from `test_mcp_adoption._engine_verbs()`, which reads the engine's own
  argparse, and the tie is pinned by recovering the set from the **compiled alternation** — so it
  holds even if a later author swaps the derivation for a literal that agrees today. The re-reviewer
  red-proofed that four ways by mutation, each red and each naming the difference.
- **`g3` round 1** — see §4.

---

## 4. `specs/*.spine.toml`

**Before:** both files carried **zero** door mentions, and these two are the only role specs that
exist. **After:** +41 and +44 lines. Schema question settled as **prose, no new keys**, reasoned from
`generate_spine.py`'s `_compile_gate` rather than from taste.

The vocabulary states both halves: the door is the interface for the spine you were launched against,
and *"what you may not do is drive a second checklist from this process"* — with the reason, so a
future author cannot "fix" the rule.

**This gate produced the run's most useful correction, and it is a correction to me.** Round 1 was
BLOCKed because the prose justified the rule with *"the **archive gate** requires the lease to cover
every journaled action."* Measured: `archive gate` appears **nowhere** in `skills/`; the Commander
archive gate's only lease postcondition is `c3` "engine session lease released" with `check: null`;
`spine_lifecycle.py` refuses in the **opposite** direction; and **neither crew plan template has a
closeout gate at all**.

The repair is better than the correction I asked for — it scopes the claim to its reader:

> *"Dispatched without a spine of your own you arrive holding no lease — nothing to release, and the
> escape never arises."*

---

## 5. #596 and #526

**#596 — reproduces, in a narrower and sharper form than the issue frames it. Repaired.** The issue's
crux held: the `feedback` gate's only postcondition asks for an **episode**, so
`commander-delegated/SKILL.md`'s *"a `FENCE.md` citation without the staged export still fails the
gate"* was **false as written** — a clause teaching a false model of what a gate enforces, which the
issue records agents propagating into launch orders. Four mandate sites reconciled against
`ORCHESTRATOR_CONTEXT.md`'s Retired Learning Playbook, which was read-only throughout.

**#526 — splits three ways, and the honest null is the interesting part.**

| | Verdict |
|---|---|
| Defect 1, as literally written (`python scripts/code_map/build.py`) | **does not reproduce** — and, per the crew's widened search, never did in the skill corpus |
| Defect 1, widened to the property the issue cared about — close-criteria phrasing that *assumes* a layout rather than resolving it | **reproduces once**, under a different script name — **fixed** |
| Defect 2 — no survey-reuse convention across review rounds | **reproduces** — **fixed** |

The widening is why this is a disposition and not a shrug: stopping at the convenient null would have
closed the issue while leaving what it was actually about. **And this run was its own evidence** —
gates `g1b` and `g3` were each reviewed twice, and round 2 used a new round file on *my instruction*
rather than on doctrine, which is precisely the gap.

---

## 6. Suite result

Full suite on **Linux**, in a **clean detached worktree** of the branch (`git worktree add --detach
/tmp/d1-verify 1037ab86`), never the working copy, with `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`/
`CREW_SCRATCH_DIR` unset (per the Admiral's warning about the `CREW_SCRATCH_DIR` leak).

**Commit verified: `1037ab867dbc197fc2629602a18ccdc53cb1d735`.**

```
3 failed, 3371 passed, 6 skipped, 1219 subtests passed in 140.23s
```

`grep '^FAILED'` returns exactly three lines:

```
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_cli_fallback_clause_reaches_an_agent
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_engine_invocation_reaches_an_agent
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
```

- `MapTreeFreshnessTests` — **permitted**, Admiral-owned and stale by construction on every parallel
  branch (#544).
- The two guard failures — **entirely lane D2's**, and proven so:

```
$ # residual, addressed:
6  skills/workbench/references/checklist-engine.md
4  skills/workbench/SKILL.md
$ # non-workbench addresses: NONE
$ # with skills/workbench/ removed in a scratch copy:
19 passed          exit 0
```

`test_no_engine_placeholder_token_reaches_an_agent` **passes**, so every `<engine>` token is gone
corpus-wide *including* workbench.

**`g5-final`'s postcondition was rewritten to measure this rather than assert it** — two falsifiable
conjuncts, verified in both directions, and it becomes the original whole-corpus check automatically
once D2 lands.

---

## 7. Touched paths

`tests/test_cli_retirement_guard.py` (new, 718) · `tests/test_mcp_adoption.py` ·
`tests/data/store_mentions.approved.txt` · `skills/{admiral/SKILL.md, admiral/references/fleet-doctrine.md,
admiral/templates/ADMIRAL_SPINE.template.json, charter/SKILL.md, commander-delegated/SKILL.md,
commander/references/commander-core.md, commander/references/crew-dispatch.md,
commander/templates/COMMANDER_SPINE.template.json, explorer/SKILL.md,
explorer/templates/EXPLORER_SPINE.template.json, interrogator/SKILL.md, reviewer/SKILL.md,
reviewer/templates/REVIEW_SURVEY.template.json, write-a-skill/SKILL.md,
write-a-skill/templates/{gated-engine,survey}-SKILL.template.md}` · `specs/{implementer,reviewer}.spine.toml` ·
`.agent-work/templates/` — 6 templates × (overlay + `.baseline/` mirror) · `.agent-work/567-d1/**`.

**Wanted but did not touch, because another lane owns it:**
`skills/workbench/SKILL.md` and `skills/workbench/references/checklist-engine.md` (D2 — the 2
surviving clauses); `docs/agents/CREW_CONTEXT.md` (D2 — a stale measurement, staged);
`scripts/mcp_spine_server.py` (E — a `CLI-fallback` sentence no walk reads);
`scripts/checklist_engine.py` (H); `scripts/run_crew.py` (F); `map/INDEX.md` (Admiral).

**Deliberately not fixed:** `.agent-work/templates/TEMPLATES_MANIFEST.json`'s five now-stale hashes.
It is an **install lockfile** carrying `generated: 2026-08-10` and a `source_commit`; hand-editing
hashes into it would make it claim bytes were installed at a commit where they were not — the
falsification `decision:records-are-not-instruction` forbids. A stale lockfile is honest.

---

## 8. Map impact

**Yes, this touches indexed source** — `tests/`, `skills/`, `specs/`. **Not acted on.** `map/INDEX.md`
is Admiral-owned (#544) and `MapTreeFreshnessTests` is accepted red. `map_orient` returns
`DEGRADED-UNPARSEABLE` for this repo (no `docs/architecture` packet, empty `map/ids.jsonl`); the
mission frame was authored against five hash-pinned substitutes and that gap is staged.

New structure worth recording: `.agent-work/templates/**` is now agent-facing instruction text with a
machine check on it, where before it was read by no walk in the repo.

---

## 9. Triage candidates — 19 files under `.agent-work/567-d1/triage-candidates/`, none filed as issues

Per `decision:no-issue-filing-mid-run`. **One should be paired with priority:**

- **`dispatched-crew-spine-is-not-bound.md`** — a live **impersonation hazard**, reproduced **six
  times** across three gates and both roles. The crew skills say a dispatched crew's spine is bound
  before it starts; for a handoff-driven `run_crew.py` dispatch it is not. Worse, the g1b re-reviewer
  finished its work and was then **refused permission to end its turn by the Stop hook**, which
  resolved a spine from disk and handed it **this Commander's** spine — whose in-progress step was the
  crew's own dispatch. It refused: *"That's impersonation, not delegation."* It was right. The hook's
  sanctioned escapes (`block`, `waive`) both **write to the parent's spine**, so the prescribed honest
  stop is itself the destructive act. Cheap fix: skip the hook when `SPINE_FILE` is unset and
  `SPINE_PARENT` is set. Durable fix: have `run_crew.py` bind the crew's own plan.

Others: `pipefail-in-command-checks-cannot-pass` · `whole-suite-evidence-is-unsafe-during-engine-drive`
· `corpus-never-names-the-doors-binding-call` · `overlay-baseline-mirror-doubles-every-target` ·
`templates-manifest-is-a-fourth-copy` · `doctrine-asserts-spine-postconditions-with-no-tie` ·
`crew-launcher-scratch-dir-test-fails-inside-a-crew` · `fowler-record-path-collides-across-gates` ·
`crew-context-python-invocation-stale` · `mcp-spine-server-cli-fallback-sentence` ·
`glossary-has-no-door-entry` · plus 7 inherited from the plan step.

---

## 10. Workflow feedback, including my own mistakes

**What worked.** Authoring the guard **before** the sweep, which the cold plan critic argued for and
which was the single best decision in the plan: the red-proof came from the real corpus instead of
from a scratch string its own author chose. And handing crews the **bar** rather than the answer —
pointing the g1b implementer at `TestCLIStaysAvailableNotDeprecated:1268` with a line number turned
"how wide should this pattern be?" from taste into a measurement it ran four candidates through.

**My own mistakes, and they cluster into one shape.**

1. **Three of my own checks were defective, in the same way each time: authored from what the output
   *should* say rather than run against what it *does* say.** (a) Every command postcondition in this
   plan opened with `set -o pipefail`, which dash rejects with exit 2 — **five checks that could not
   pass**, and the provenance is the sharp part: the cold critic correctly killed `| tail -5` as *a
   check that cannot fail* and offered `set -o pipefail` as the repair. **The repair for a check that
   cannot fail produced five that cannot pass**, and neither the plan author, the critic, nor I
   noticed — a crew that tried to run one found it. (b) My rescoped `g3`/`g4` checks matched the
   guard's own **census line** as a violation, so they would have failed on a correctly-swept tree.
   (c) `g3`/`g4` originally required a whole-corpus green that lane D2's un-merged files made
   unobtainable.
2. **I stated the second-checklist boundary wrong in two handoffs**, repeating the Admiral's F-1
   phrasing that *"every child plan in this system is driven off-door."* A dispatched crew's door is
   **unbound**, so it can drive its own plan. The g3 implementer refused my premise and measured it;
   the g3 reviewer reproduced the correction and was itself the live case. I have corrected
   `notes-1.md` and `REPLAN_INPUT.json` rather than leaving my version standing.
3. **I dispatched the g1b re-reviewer with a `--result` path the handoff document did not name**, so
   it followed the document and overwrote round 1's BLOCK result. Recoverable only because I had
   committed it at `4df66479` — which the reviewer itself checked and noted.

**What the crews did better than they were asked.** Two BLOCKs, both correct, both on things I had
approved. The g1b reviewer refused to verify a derivation by calling the same helper the guard calls
— *"that would be a tautology"* — and read the engine two other ways. The g2 reviewer checked its
absence-greps for **non-vacuity** before believing them. The g1b re-reviewer traced a 7-vs-6 suite
discrepancy to **its own** side effect rather than reporting it as someone else's defect, and wrote
the lesson down: *"when your measurement disagrees with a claim, suspect your measurement's side
effects before you suspect the claim."*

**A float, non-blocking.** `docs/agents/GLOSSARY.md` still has **no entry for "door"** — the term this
epic makes load-bearing. Staged, not taken: `docs/agents/*` is the human's call.

---

## 11. PR

**Not yet opened at the time of writing** — see the handoff note below. Branch
`feat/567-d1-doctrine-sweep-guard`, rebased on `origin/main` `5099eea1`, verified head `1037ab86`.

**Merge sequencing, which is the Admiral's call and the one thing this lane cannot do for itself:**
this lane merges **last**, and **lane D2 must merge first**. Until it does, the guard is red on
exactly D2's two files. The moment D2 lands, `g5-final`'s check becomes the unfiltered whole-corpus
check with no edit required.

---

## Handoff — what remains

The `execute` step is complete: `execute.json` is driven to `g5-final`, its lease released, and
`verify_iterative_role_artifacts.py commander --work-id 567-d1` returns ok. The remaining spine steps
are **reconcile → triage → review → feedback → archive**, plus opening the PR. A fresh Commander picks
these up from this artifact and from `.agent-work/567-d1/{notes-1.md, STATE_NOTE.md, REPLAN_INPUT.json}`.
